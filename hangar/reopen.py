"""Flag a decided record when its loading matrix moved after a sourced value.

The decision itself is left as the owner wrote it. Reopening is a separate step.
"""

from __future__ import annotations

import copy
from datetime import date
from pathlib import Path

import yaml

from hangar.matrix_extra import matrix_digest
from hangar.records import dump_record

_REASON = "the loading matrix changed after a sourced value"


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


def flag_reopen(records_root: Path) -> list[str]:
    """Set or clear reopen_flag from the stored matrix digest. Returns the ids flagged."""
    flagged: list[str] = []
    root = Path(records_root)
    for path in sorted(root.glob("*/decisions/*.yaml")):
        rec = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(rec, dict) or rec.get("status") != "decided":
            continue
        decision = rec.get("decision")
        if not isinstance(decision, dict) or not isinstance(decision.get("matrix_digest"), dict):
            continue
        stored = decision["matrix_digest"]
        current = decision_digests(rec)
        if _differ(stored, current):
            rec["reopen_flag"] = {
                "date": date.today().isoformat(),
                "reason": _REASON,
                "unknowns": _sourced_from(rec, decision),
                "digest_then": copy.deepcopy(stored),
                "digest_now": current,
            }
            path.write_text(dump_record(rec), encoding="utf-8")
            if isinstance(rec.get("id"), str):
                flagged.append(rec["id"])
            continue
        if "reopen_flag" in rec:
            rec.pop("reopen_flag", None)
            path.write_text(dump_record(rec), encoding="utf-8")
    return flagged
