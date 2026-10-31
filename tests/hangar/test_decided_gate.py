"""Git-aware gate: a decided record's decision and history cannot be edited together (scripts/check_decided_records.py)."""

from __future__ import annotations

import copy
import importlib.util
import subprocess
from pathlib import Path

import yaml

_spec = importlib.util.spec_from_file_location(
    "check_decided_records", Path(__file__).resolve().parents[2] / "scripts" / "check_decided_records.py"
)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

REL = "data/hangar/mod-ez/decisions/r.yaml"
DECIDED = {
    "id": "r",
    "status": "decided",
    "decision": {"picks": {"engine": "a"}, "date": "2026-10-18", "reason": "why"},
    "history": [{"date": "2026-10-18", "from": "open", "to": "decided", "reason": "why", "picks": {"engine": "a"}}],
}


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)


def committed(tmp_path):
    git(tmp_path, "init", "-q")
    f = tmp_path / REL
    f.parent.mkdir(parents=True)
    f.write_text(yaml.safe_dump(DECIDED))
    git(tmp_path, "add", REL)
    git(tmp_path, "commit", "-qm", "decided")
    return f


def test_unchanged_record_passes(tmp_path):
    committed(tmp_path)
    assert gate.check(tmp_path, "HEAD") == []


def test_editing_decision_and_history_together_is_refused(tmp_path):
    f = committed(tmp_path)
    bad = copy.deepcopy(DECIDED)
    bad["decision"]["picks"] = {"engine": "b"}
    bad["history"][-1]["picks"] = {"engine": "b"}
    f.write_text(yaml.safe_dump(bad))
    errors = gate.check(tmp_path, "HEAD")
    assert len(errors) == 1 and "rewritten" in errors[0]


def test_editing_decision_alone_is_refused(tmp_path):
    f = committed(tmp_path)
    bad = copy.deepcopy(DECIDED)
    bad["decision"]["picks"] = {"engine": "b"}
    f.write_text(yaml.safe_dump(bad))
    assert gate.check(tmp_path, "HEAD")


def test_reopen_and_redecide_by_appending_history_passes(tmp_path):
    f = committed(tmp_path)
    ok = copy.deepcopy(DECIDED)
    ok["decision"] = {"picks": {"engine": "b"}, "date": "2026-11-01", "reason": "new"}
    ok["history"] += [
        {"date": "2026-10-30", "from": "decided", "to": "reopened", "reason": "moved"},
        {"date": "2026-11-01", "from": "reopened", "to": "decided", "reason": "new", "picks": {"engine": "b"}},
    ]
    f.write_text(yaml.safe_dump(ok))
    assert gate.check(tmp_path, "HEAD") == []
