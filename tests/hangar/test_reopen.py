"""Reopen flags: a decided loading matrix that moved, and the scores CLI that notices."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

from hangar.matrix_extra import matrix_digest, matrix_text
from hangar.matrix import matrix_for_effect
from hangar.mission import main, write_scores
from hangar.records import dump_record
from hangar.reopen import decision_digests, flag_reopen

EFFECT = {"engine": "rotax-912is"}
REASON = "the loading matrix changed after a sourced value"


def _tree(tmp_path: Path, rec: dict) -> tuple[Path, Path]:
    root = tmp_path / "hangar"
    folder = root / "mod-ez" / "decisions"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "demo.yaml"
    path.write_text(dump_record(rec))
    return root, path


def _rec(effect: dict, digest: dict, **kw) -> dict:
    rec = {
        "id": "demo",
        "status": "decided",
        "mission_score": None,
        "history": [{"date": "2026-10-01", "from": "open", "to": "decided", "reason": "kept"}],
        "unknowns": [],
        "options": [{"id": "alt", "effect": copy.deepcopy(effect), "facts": []}],
        "decision": {
            "picks": {"cg_fix": "alt"},
            "date": "2026-10-01",
            "reason": "kept",
            "matrix_digest": dict(digest),
            "over_unknowns": [],
        },
    }
    rec.update(kw)
    return rec


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_decision_digests_cover_options_with_an_effect():
    rec = _rec(EFFECT, {})
    rec["options"].append({"id": "plain", "facts": []})
    got = decision_digests(rec)
    assert list(got) == ["alt"]
    assert got["alt"] == matrix_digest(EFFECT)


def test_equal_digests_do_not_flag_and_a_stale_flag_is_removed(tmp_path):
    """Deleting the digest comparison (always flag, or never look) fails this."""
    digest = {"alt": matrix_digest(EFFECT)}
    rec = _rec(EFFECT, digest)
    root, path = _tree(tmp_path, rec)
    before = path.read_bytes()
    assert flag_reopen(root) == []
    assert path.read_bytes() == before
    assert "reopen_flag" not in _load(path)

    rec = _load(path)
    rec["reopen_flag"] = {"date": "2026-10-01", "reason": "old", "unknowns": ["coolant-weight"]}
    path.write_text(dump_record(rec))
    decision = copy.deepcopy(rec["decision"])
    history = copy.deepcopy(rec["history"])
    assert flag_reopen(root) == []
    got = _load(path)
    assert "reopen_flag" not in got
    assert got["decision"] == decision and got["history"] == history and got["status"] == "decided"


def test_a_moved_matrix_flags_without_editing_the_decision(tmp_path):
    """Deleting the digest comparison so nothing is flagged fails this."""
    digest = {"alt": matrix_digest(EFFECT)}
    rec = _rec(EFFECT, digest)
    rec["unknowns"] = [
        {"id": "coolant-weight", "state": "sourced"},
        {"id": "still-open", "state": "open"},
        {"id": "not-listed", "state": "sourced"},
    ]
    rec["decision"]["over_unknowns"] = ["coolant-weight", "still-open"]
    rec["options"][0]["effect"] = {
        "engine": "rotax-912is",
        "extras": [{"name": "ballast", "weight_lb": 10, "arm_in": 141.05, "flag": "derived"}],
    }
    root, path = _tree(tmp_path, rec)
    decision = copy.deepcopy(rec["decision"])
    history = copy.deepcopy(rec["history"])
    assert flag_reopen(root) == ["demo"]
    got = _load(path)
    assert got["decision"] == decision
    assert got["history"] == history and got["status"] == "decided"
    flag = got["reopen_flag"]
    assert flag["reason"] == REASON
    assert flag["date"]
    assert flag["unknowns"] == ["coolant-weight"]
    assert flag["digest_then"] == decision["matrix_digest"]
    assert flag["digest_now"]["alt"] == matrix_digest(got["options"][0]["effect"])
    assert flag["digest_now"] != flag["digest_then"]
    assert flag_reopen(root) == ["demo"]  # idempotent
    assert _load(path)["decision"] == decision


def test_a_new_or_missing_digest_key_flags(tmp_path):
    digest = {"alt": matrix_digest(EFFECT), "gone": "abc"}
    root, path = _tree(tmp_path, _rec(EFFECT, digest))
    assert flag_reopen(root) == ["demo"]
    assert "gone" in _load(path)["reopen_flag"]["digest_then"]
    assert "gone" not in _load(path)["reopen_flag"]["digest_now"]

    fresh = matrix_digest(EFFECT)
    rec = _rec(EFFECT, {"alt": fresh})
    rec["options"].append({"id": "extra", "effect": {"engine": "o235-book"}})
    root, path = _tree(tmp_path, rec)
    assert flag_reopen(root) == ["demo"]
    assert "extra" in _load(path)["reopen_flag"]["digest_now"]


def test_open_records_and_records_without_a_stored_digest_are_left_alone(tmp_path):
    rec = _rec(EFFECT, {"alt": "0" * 16})
    rec["status"] = "open"
    root, path = _tree(tmp_path, rec)
    before = path.read_bytes()
    assert flag_reopen(root) == []
    assert path.read_bytes() == before

    rec = _rec(EFFECT, {"alt": "0" * 16})
    del rec["decision"]["matrix_digest"]
    root, path = _tree(tmp_path, rec)
    before = path.read_bytes()
    assert flag_reopen(root) == []
    assert path.read_bytes() == before


def test_write_scores_refreshes_matrix_facts(tmp_path):
    """A matrix fact is regenerated. Leaving the typed sentence in place fails this."""
    root = tmp_path / "hangar"
    folder = root / "mod-ez" / "decisions"
    folder.mkdir(parents=True, exist_ok=True)
    effect = {"engine": "rotax-912is"}
    rec = {
        "mission_score": None,
        "scoring": {"kind": "loadings", "engines": ["rotax-912is"]},
        "options": [{
            "id": "alt",
            "effect": effect,
            "facts": [{"text": "typed by hand", "flag": "derived", "computed": "matrix"}],
        }],
    }
    path = folder / "demo.yaml"
    path.write_text(dump_record(rec))
    write_scores(root)
    got = _load(path)
    fact = next(f for f in got["options"][0]["facts"] if f.get("computed") == "matrix")
    assert fact["text"] == matrix_text(matrix_for_effect(effect))
    assert fact["text"] != "typed by hand"


def test_write_scores_cli_runs_flag_reopen_and_prints_ids(tmp_path, capsys):
    digest = {"alt": "deadbeef"}
    rec = _rec(EFFECT, digest)
    rec["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
    root, path = _tree(tmp_path, rec)
    assert main(["--write-scores", "--root", str(root)]) == 0
    out = capsys.readouterr().out
    assert "demo" in out
    got = _load(path)
    assert got["status"] == "decided"
    assert got["decision"]["matrix_digest"] == digest
    assert got["reopen_flag"]["reason"] == REASON
    assert got["reopen_flag"]["unknowns"] == []
