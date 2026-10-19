"""Flag a decided record when its loading matrix moved after a sourced value.

The decision itself is left as the owner wrote it. Reopening is a separate step.
"""

from __future__ import annotations

import copy
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

import yaml

from hangar.matrix_extra import matrix_digest
from hangar.records import dump_record, load_record, validate

_REASON = "the loading matrix changed after a sourced value"
_GRAPH = None

# Records skipped on the last flag_reopen call (read or score failures). The CLI prints
# these and the briefing server logs them. Not part of the returned id list.
last_errors: list[str] = []


def decision_digests(rec_dict: dict) -> dict[str, str]:
    """Current digest of every option that carries an effect."""
    found: dict[str, str] = {}
    for opt in rec_dict.get("options") or []:
        if not isinstance(opt, dict) or not isinstance(opt.get("effect"), dict):
            continue
        opt_id = opt.get("id")
        if not isinstance(opt_id, str):
            continue
        found[opt_id] = matrix_digest(opt["effect"])
    return found


def _differ(stored: dict, current: dict) -> bool:
    if set(stored) != set(current):
        return True
    return any(stored[key] != current[key] for key in stored)


def _sourced_from(rec: dict, decision: dict) -> list[str]:
    named = decision.get("over_unknowns") or []
    if not isinstance(named, list):
        return []
    by_id = {}
    for row in rec.get("unknowns") or []:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            by_id[row["id"]] = row
    return [
        item
        for item in named
        if isinstance(item, str) and isinstance(by_id.get(item), dict) and by_id[item].get("state") == "sourced"
    ]


def _iso(value: object) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def _same_flag(existing: object, stored: dict, current: dict, unknowns: list[str]) -> bool:
    """True when the flag already records this digest pair, so its date must stay."""
    if not isinstance(existing, dict):
        return False
    return (
        _iso(existing.get("date")) is not None
        and existing.get("reason") == _REASON
        and existing.get("unknowns") == unknowns
        and existing.get("digest_then") == stored
        and existing.get("digest_now") == current
    )


def _graph():
    global _GRAPH
    if _GRAPH is None:
        import guide.schema

        _GRAPH = guide.schema.load_graph(Path(__file__).resolve().parents[1] / "guide" / "graph")
    return _GRAPH


def _record_ids(root: Path) -> set[str]:
    found: set[str] = set()
    for path in Path(root).glob("*/decisions/*.yaml"):
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            continue
        if isinstance(loaded, dict) and isinstance(loaded.get("id"), str):
            found.add(loaded["id"])
    return found


def _schema_errors(rec: dict, root: Path) -> list[str] | None:
    """Validator errors, or None when the mapping is not a full record."""
    fd, name = tempfile.mkstemp(prefix=".reopen-", suffix=".yaml")
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(dump_record(rec))
        try:
            loaded = load_record(tmp)
        except ValueError:
            return None
        return list(validate(loaded, _graph(), _record_ids(root) | {loaded.id}))
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _replace(path: Path, text: str) -> None:
    fd, name = tempfile.mkstemp(prefix=".reopen-", suffix=".tmp", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def _validate_and_write(path: Path, root: Path, rec: dict) -> None:
    text = dump_record(rec)
    if path.read_text(encoding="utf-8") == text:
        return
    errors = _schema_errors(rec, root)
    if errors:
        raise ValueError("record rejected")
    _replace(path, text)


def _flag_one(path: Path, root: Path, flagged: list[str]) -> None:
    rec = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(rec, dict) or rec.get("status") != "decided":
        return
    decision = rec.get("decision")
    if not isinstance(decision, dict) or not isinstance(decision.get("matrix_digest"), dict):
        return
    stored = decision["matrix_digest"]
    current = decision_digests(rec)
    if _differ(stored, current):
        unknowns = _sourced_from(rec, decision)
        if _same_flag(rec.get("reopen_flag"), stored, current, unknowns):
            return
        rec["reopen_flag"] = {
            "date": date.today().isoformat(),
            "reason": _REASON,
            "unknowns": unknowns,
            "digest_then": copy.deepcopy(stored),
            "digest_now": current,
        }
        _validate_and_write(path, root, rec)
        if isinstance(rec.get("id"), str):
            flagged.append(rec["id"])
        return
    if "reopen_flag" in rec:
        rec.pop("reopen_flag", None)
        _validate_and_write(path, root, rec)


def flag_reopen(records_root: Path) -> list[str]:
    """Set or clear ``reopen_flag`` from the stored matrix digest.

    Returns ids whose flag was newly set, or whose flag content changed, in this call.
    A repeat call with the same digests returns nothing and keeps the flag's date.
    Clearing a stale flag is not reported. One bad record is skipped; the rest still
    run. Skipped names are listed in ``last_errors`` for the caller to print.
    A write is atomic and happens only when the text would change, after validation
    when the file is a full record.
    """
    global last_errors
    last_errors = []
    flagged: list[str] = []
    root = Path(records_root)
    for path in sorted(root.glob("*/decisions/*.yaml")):
        try:
            _flag_one(path, root, flagged)
        except Exception:
            last_errors.append(f"skipped {path.stem}")
    return flagged
