"""Insert ``plan:`` blocks into chapter ops from plan-values YAML files.

Each values file maps an op id to ``{plan: ...}``. The block is written on the
line after that op's ``group:``. Every other byte of the chapter file stays as
it was. Re-running replaces an existing ``plan:`` block on those ops.

Item ids in ``ITEM_ALIASES`` are rewritten to one catalog id. ``QTY_FACTORS``
converts a quantity into that id's unit. Ops in ``FUEL_WALL_OPS`` keep the
build resin and record ``plan.fuel``: UL94 compatibility unknown, source null.
That flag does not say the resin resists fuel.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "guide" / "graph"

OP_START = re.compile(r"(?m)^- id: (\S+)\s*$")
GROUP = re.compile(r"(?m)^  group: \S+\s*$")

# Page-priced row wins when two docs name the same part.
ITEM_ALIASES = {
    "foam-pvc-0p35": "foam-pvc-0p375-32x48",
    "foam-pvc-0p35-32x48": "foam-pvc-0p375-32x48",
    "nylaflow-3-16": "brake-line-nylon-316",
    "alu-angle-2024-1x1x0125": "al-2024-angle-1x1x0125",
    "urethane-foam-2in": "urethane-foam-2x24x48",
}
# foam-pvc-0p35 was counted in square feet. The kept row is one 32 x 48 sheet.
QTY_FACTORS = {
    "foam-pvc-0p35": 144 / (32 * 48),
}
# Aft side skins (chapter 7) and the strake tank interior. No published UL94
# immersion clears or rules out the build resin; the flag stays unknown.
FUEL_WALL_OPS = frozenset(
    {
        "f07.skin-right",
        "f07.skin-left",
        "f21.inside-layups",
        "f21.close-tank",
    }
)
FUEL_WETTED = {
    "wetted": True,
    "fuel": "UL94",
    "resin_compat": "unknown",
    "why": "no published UL94 immersion test of this resin; Block 5 coupon test pending",
    "source": None,
}


def _fmt_num(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SystemExit(f"bad number {value!r}")
    if isinstance(value, int):
        return str(value)
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _rewrite_buy(item: str, qty: float) -> tuple[str, float]:
    factor = QTY_FACTORS.get(item)
    kept = ITEM_ALIASES.get(item, item)
    if factor is None:
        return kept, qty
    scaled = round(float(qty) * factor + 1e-12, 5)
    if scaled == int(scaled):
        return kept, int(scaled)
    return kept, scaled


def _prepare(op_id: str, plan: dict) -> dict:
    if op_id == "f15.stainless-firewall" and plan.get("cure") != "none":
        raise SystemExit("f15.stainless-firewall cure must stay none")
    out = dict(plan)
    if op_id in FUEL_WALL_OPS:
        out["fuel"] = dict(FUEL_WETTED)
    buys = out.get("buy")
    if buys:
        rewritten = []
        for row in buys:
            item, qty = _rewrite_buy(row["item"], row["qty"])
            rewritten.append({**row, "item": item, "qty": qty})
        out["buy"] = rewritten
    return out


def _render_fuel(fuel: dict) -> str:
    wetted = fuel.get("wetted")
    if wetted is not True:
        raise SystemExit(f"bad fuel wetted {wetted!r}")
    grade = fuel.get("fuel")
    compat = fuel.get("resin_compat")
    why = fuel.get("why")
    if not isinstance(grade, str) or not isinstance(compat, str):
        raise SystemExit(f"bad fuel {fuel!r}")
    if not isinstance(why, str):
        raise SystemExit(f"bad fuel why {why!r}")
    source = fuel.get("source")
    source_text = "null" if source is None else _quote(source)
    return (
        "    fuel: {wetted: true, fuel: "
        f"{grade}, resin_compat: {compat}, "
        f"why: {_quote(why)}, source: {source_text}}}"
    )


def render_plan(plan: dict) -> str:
    """Deterministic Contract 2 block, indented as a chapter-op field."""
    lines = ["  plan:"]
    lines.append(f"    people: {plan.get('people', 1)}")
    why = plan.get("people_why")
    if why is not None:
        lines.append(f"    people_why: {_quote(why)}")
    hours = plan.get("hours")
    if hours is not None:
        source = hours.get("source")
        source_text = "null" if source is None else _quote(source)
        lines.append(
            "    hours: {value: "
            f"{_fmt_num(hours['value'])}, flag: {hours['flag']}, "
            f"source: {source_text}}}"
        )
    lines.append(f"    cure: {plan.get('cure', 'none')}")
    resin = plan.get("resin")
    if resin is not None:
        lines.append(f"    resin: {resin}")
    fuel = plan.get("fuel")
    if fuel:
        lines.append(_render_fuel(fuel))
    tools = plan.get("tools") or []
    if tools:
        lines.append("    tools: [" + ", ".join(tools) + "]")
    buys = plan.get("buy") or []
    if buys:
        lines.append("    buy:")
        for row in buys:
            lines.append(
                "      - {item: "
                f"{row['item']}, qty: {_fmt_num(row['qty'])}, "
                f"flag: {row['flag']}}}"
            )
    return "\n".join(lines) + "\n"


def _blocks(text: str, name: str) -> list[tuple[str, str]]:
    starts = list(OP_START.finditer(text))
    if not starts:
        raise SystemExit(f"{name}: no ops")
    parts: list[tuple[str, str]] = [("", text[: starts[0].start()])]
    for idx, match in enumerate(starts):
        end = starts[idx + 1].start() if idx + 1 < len(starts) else len(text)
        parts.append((match.group(1), text[match.start() : end]))
    return parts


def _strip_plan(block: str) -> str:
    lines = block.splitlines(keepends=True)
    out: list[str] = []
    skipping = False
    for line in lines:
        if not skipping and line.startswith("  plan:"):
            skipping = True
            continue
        if skipping:
            if line.startswith("    "):
                continue
            skipping = False
        out.append(line)
    return "".join(out)


def _insert_plan(block: str, op_id: str, rendered: str) -> str:
    block = _strip_plan(block)
    groups = list(GROUP.finditer(block))
    if len(groups) != 1:
        raise SystemExit(f"{op_id}: expected one group line, found {len(groups)}")
    at = groups[0].end()
    if at < len(block) and block[at] == "\n":
        at += 1
    return block[:at] + rendered + block[at:]


def apply_text(text: str, name: str, plans: dict[str, dict]) -> tuple[str, set[str]]:
    seen: set[str] = set()
    out: list[str] = []
    for op_id, block in _blocks(text, name):
        if not op_id:
            out.append(block)
            continue
        if op_id in seen:
            raise SystemExit(f"{name}: duplicate op id {op_id}")
        seen.add(op_id)
        if op_id not in plans:
            out.append(block)
            continue
        prepared = _prepare(op_id, plans[op_id])
        rendered = render_plan(prepared)
        parsed = yaml.safe_load(rendered)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("plan"), dict):
            raise SystemExit(f"{op_id}: rendered plan did not parse")
        out.append(_insert_plan(block, op_id, rendered))
    return "".join(out), seen


def load_plans(paths: list[Path]) -> dict[str, dict]:
    plans: dict[str, dict] = {}
    for path in paths:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not raw:
            raise SystemExit(f"{path}: must be an op-id mapping")
        for op_id, body in raw.items():
            if not isinstance(op_id, str) or not isinstance(body, dict):
                raise SystemExit(f"{path}: bad entry {op_id!r}")
            if set(body) != {"plan"} or not isinstance(body["plan"], dict):
                raise SystemExit(f"{path}: {op_id} must be a single plan mapping")
            if op_id in plans:
                raise SystemExit(f"duplicate op id {op_id}")
            plans[op_id] = body["plan"]
    return plans


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("values", nargs="+", type=Path)
    parser.add_argument("--graph", type=Path, default=GRAPH)
    args = parser.parse_args(argv)
    plans = load_plans(args.values)
    files = sorted(args.graph.glob("ch*.yaml"))
    if not files:
        raise SystemExit(f"{args.graph}: no chapter files")
    seen_all: set[str] = set()
    revised_files: list[tuple[Path, str]] = []
    changed = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        revised, seen = apply_text(original, path.name, plans)
        overlap = seen_all & seen
        if overlap:
            raise SystemExit(
                "op id repeated across files: " + ", ".join(sorted(overlap))
            )
        seen_all |= seen
        revised_files.append((path, revised))
        if revised != original:
            changed += 1
    missing = sorted(set(plans) - seen_all)
    if missing:
        raise SystemExit("plan ids not in any chapter file: " + ", ".join(missing))
    for path, revised in revised_files:
        if revised != path.read_text(encoding="utf-8"):
            path.write_text(revised, encoding="utf-8")
    print(f"wrote plan blocks for {len(plans)} ops in {changed} chapter files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
