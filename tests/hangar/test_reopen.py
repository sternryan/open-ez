"""Reopen flags: a decided loading matrix that moved, and the scores CLI that notices."""

from __future__ import annotations

import copy
import time
from pathlib import Path

import yaml

from hangar import mission, reopen
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
    stamped = flag["date"]
    before = path.read_bytes()
    assert flag_reopen(root) == []  # a repeat flags nothing new and does not rewrite
    again = _load(path)
    assert again["decision"] == decision
    assert again["reopen_flag"]["date"] == stamped
    assert path.read_bytes() == before


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


def test_flag_date_stays_when_the_digests_do_not_change(tmp_path):
    """A repeat call must not stamp today's date over the flag already on the record."""
    digest = {"alt": matrix_digest(EFFECT)}
    rec = _rec(EFFECT, digest)
    rec["options"][0]["effect"] = {
        "engine": "rotax-912is",
        "extras": [{"name": "ballast", "weight_lb": 10, "arm_in": 141.05, "flag": "derived"}],
    }
    root, path = _tree(tmp_path, rec)
    assert flag_reopen(root) == ["demo"]
    loaded = _load(path)
    loaded["reopen_flag"]["date"] = "2020-01-01"
    path.write_text(dump_record(loaded))
    before = path.read_bytes()
    assert flag_reopen(root) == []
    assert path.read_bytes() == before
    got_date = _load(path)["reopen_flag"]["date"]
    text = got_date.isoformat() if hasattr(got_date, "isoformat") else got_date
    assert text == "2020-01-01"


def test_flag_reopen_skips_one_bad_record_and_flags_the_rest(tmp_path):
    """A record whose matrix cannot be scored must not stop the others."""
    digest = {"alt": matrix_digest(EFFECT)}
    good = _rec(EFFECT, digest)
    good["options"][0]["effect"] = {
        "engine": "rotax-912is",
        "extras": [{"name": "ballast", "weight_lb": 10, "arm_in": 141.05, "flag": "derived"}],
    }
    root, path = _tree(tmp_path, good)
    bad = _rec({"engine": "no-such-engine"}, {"alt": "0"})
    bad["id"] = "broken"
    bad_path = path.parent / "broken.yaml"
    bad_path.write_text(dump_record(bad))
    bad_before = bad_path.read_bytes()
    assert flag_reopen(root) == ["demo"]
    assert _load(path)["reopen_flag"]["reason"] == REASON
    assert bad_path.read_bytes() == bad_before
    assert any("broken" in item for item in reopen.last_errors)


def test_write_scores_skips_a_bad_record_and_leaves_unchanged_files(tmp_path):
    root = tmp_path / "hangar"
    folder = root / "mod-ez" / "decisions"
    folder.mkdir(parents=True)
    effect = {"engine": "rotax-912is"}
    good = {
        "id": "demo",
        "mission_score": None,
        "scoring": {"kind": "loadings", "engines": ["rotax-912is"]},
        "options": [{
            "id": "alt",
            "effect": effect,
            "facts": [{"text": "typed by hand", "flag": "derived", "computed": "matrix"}],
        }],
    }
    path = folder / "demo.yaml"
    path.write_text(dump_record(good))
    bad = {
        "id": "broken",
        "mission_score": None,
        "options": [{"id": "alt", "effect": {"engine": "no-such-engine"}, "facts": [
            {"text": "typed", "flag": "derived", "computed": "matrix"},
        ]}],
    }
    bad_path = folder / "aaa.yaml"
    bad_path.write_text(dump_record(bad))
    bad_before = bad_path.read_bytes()
    assert write_scores(root) == 1
    got = _load(path)
    fact = next(item for item in got["options"][0]["facts"] if item.get("computed") == "matrix")
    assert fact["text"] == matrix_text(matrix_for_effect(effect))
    assert bad_path.read_bytes() == bad_before
    assert any("aaa" in item for item in mission.last_errors)
    stamped = path.stat().st_mtime_ns
    time.sleep(0.05)
    assert write_scores(root) == 1
    assert path.stat().st_mtime_ns == stamped


def test_scores_cli_prints_skipped_records(tmp_path, capsys):
    root = tmp_path / "hangar"
    folder = root / "mod-ez" / "decisions"
    folder.mkdir(parents=True)
    (folder / "aaa.yaml").write_text(":\n  - [\n")
    rec = _rec(EFFECT, {"alt": "deadbeef"})
    rec["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
    rec["mission_score"] = None
    (folder / "demo.yaml").write_text(dump_record(rec))
    assert main(["--write-scores", "--root", str(root)]) == 0
    captured = capsys.readouterr()
    assert "demo" in captured.out
    assert "aaa" in captured.err


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
