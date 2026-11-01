"""Insert or replace ``group:`` on chapter ops from the assignment table.

The table is ``scripts/group_assignments.yaml`` (op id -> group id). Every other
byte of each ``guide/graph/ch*.yaml`` file is left unchanged. A missing ``group``
is inserted on the line after ``chapter:``. An existing ``group`` line is updated
in place.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "guide" / "graph"
ASSIGNMENTS = Path(__file__).resolve().parent / "group_assignments.yaml"

OP_START = re.compile(r"(?m)^- id: (\S+)\s*$")
CHAPTER = re.compile(r"(?m)^  chapter: \d+\s*$")
GROUP = re.compile(r"(?m)^  group: \S+\s*$")
VARIANTS = re.compile(r"(?m)^  variants: \[([^\[\]]*)\]\s*$")
STUB = re.compile(r"(?m)^  stub: true\s*$")


def _variants(op_id: str, block: str) -> tuple[str, ...]:
    found = VARIANTS.findall(block)
    if not found:
        return ("both",)
    if len(found) != 1:
        raise SystemExit(f"{op_id}: more than one variants line")
    parts = tuple(part.strip() for part in found[0].split(",") if part.strip())
    return parts or ("both",)


def _needs_group(op_id: str, block: str) -> bool:
    return STUB.search(block) is None and _variants(op_id, block) != ("gu",)


def _apply_block(block: str, op_id: str, group_id: str) -> str:
    groups = list(GROUP.finditer(block))
    if len(groups) > 1:
        raise SystemExit(f"{op_id}: more than one group line")
    line = f"  group: {group_id}"
    if groups:
        current = groups[0]
        if block[current.start() : current.end()] == line:
            return block
        return block[: current.start()] + line + block[current.end() :]
    chapter = CHAPTER.search(block)
    if chapter is None:
        raise SystemExit(f"{op_id}: no chapter line to insert group after")
    at = chapter.end()
    if at < len(block) and block[at] == "\n":
        at += 1
    return block[:at] + line + "\n" + block[at:]


def _blocks(text: str, name: str) -> list[tuple[str, str]]:
    starts = list(OP_START.finditer(text))
    if not starts:
        raise SystemExit(f"{name}: no ops")
    parts: list[tuple[str, str]] = [("", text[: starts[0].start()])]
    for idx, match in enumerate(starts):
        end = starts[idx + 1].start() if idx + 1 < len(starts) else len(text)
        parts.append((match.group(1), text[match.start() : end]))
    return parts


def apply_text(
    text: str, name: str, assignments: dict[str, str]
) -> tuple[str, set[str]]:
    seen: set[str] = set()
    out: list[str] = []
    for op_id, block in _blocks(text, name):
        if not op_id:
            out.append(block)
            continue
        if op_id in seen:
            raise SystemExit(f"{name}: duplicate op id {op_id}")
        seen.add(op_id)
        if op_id not in assignments:
            if _needs_group(op_id, block):
                raise SystemExit(
                    f"{op_id}: needs a group but is not in the assignment table"
                )
            out.append(block)
            continue
        out.append(_apply_block(block, op_id, assignments[op_id]))
    return "".join(out), seen


def _load_assignments() -> dict[str, str]:
    raw = yaml.safe_load(ASSIGNMENTS.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise SystemExit("group_assignments.yaml must be an op-id to group-id mapping")
    assignments: dict[str, str] = {}
    for op_id, group_id in raw.items():
        if not isinstance(op_id, str) or not isinstance(group_id, str) or not group_id:
            raise SystemExit(f"bad assignment {op_id!r}: {group_id!r}")
        assignments[op_id] = group_id
    return assignments


def main() -> int:
    assignments = _load_assignments()
    groups_doc = yaml.safe_load((GRAPH / "groups.yaml").read_text(encoding="utf-8"))
    valid = {row["id"] for row in groups_doc["groups"]}
    unknown = sorted({gid for gid in assignments.values() if gid not in valid})
    if unknown:
        raise SystemExit(
            "assignment group ids not in groups.yaml: " + ", ".join(unknown)
        )

    files = sorted(GRAPH.glob("ch*.yaml"))
    required = set(groups_doc["required_files"])
    names = {path.name for path in files}
    if required != names:
        missing = ", ".join(sorted(names - required))
        extra = ", ".join(sorted(required - names))
        raise SystemExit(
            f"groups.yaml required_files must list every chapter file"
            f" (missing: {missing or 'none'}; extra: {extra or 'none'})"
        )

    seen_all: set[str] = set()
    revised_files: list[tuple[Path, str]] = []
    changed = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        revised, seen = apply_text(original, path.name, assignments)
        overlap = seen_all & seen
        if overlap:
            raise SystemExit(
                "op id repeated across files: " + ", ".join(sorted(overlap))
            )
        seen_all |= seen
        revised_files.append((path, revised))
        if revised != original:
            changed += 1
    missing_ids = sorted(set(assignments) - seen_all)
    if missing_ids:
        raise SystemExit(
            "assignment ids not in any chapter file: " + ", ".join(missing_ids)
        )
    for path, revised in revised_files:
        current = path.read_text(encoding="utf-8")
        if revised != current:
            path.write_text(revised, encoding="utf-8")
    print(f"wrote group fields in {changed} chapter files ({len(assignments)} ops)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
