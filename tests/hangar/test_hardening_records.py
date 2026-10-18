"""Gaps the first-round reviews found: hostile input, bindings, and what must never leak (Hangar H1/H2)."""

from __future__ import annotations

import copy
import dataclasses
import io
import json
import os
import shutil
from pathlib import Path

import pytest
import yaml

from hangar import council, mission
from hangar.council import CouncilReply, CouncilUnavailable, ask, backbone
from hangar.records import DATA_ROOT, load_record, validate, validate_all
from tests.hangar.test_council import fake, pos, reply_of
from tests.hangar.test_records import GRAPH, base, decided, errs, fact, make

# ---------------------------------------------------------------- records


def write(root: Path, name: str, text: str, spot="mod-ez"):
    d = root / spot / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text)


def test_malformed_files_become_errors(tmp_path):
    write(tmp_path, "empty.yaml", "")
    write(tmp_path, "list.yaml", "- a\n- b\n")
    write(tmp_path, "partial.yaml", "id: partial\nspot: mod-ez\n")
    out = validate_all(tmp_path)
    assert len(out) >= 3
    for stem in ("empty", "list", "partial"):
        assert any(stem in e for e in out), (stem, out)


def test_duplicate_ids_are_an_error(tmp_path):
    write(tmp_path, "a.yaml", yaml.safe_dump(base()))
    write(tmp_path, "b.yaml", yaml.safe_dump(base()))
    assert any("duplicate" in e.lower() for e in validate_all(tmp_path))


def test_spot_must_match_directory(tmp_path):
    d = base()
    d["spot"] = "rv-12"
    write(tmp_path, "demo.yaml", yaml.safe_dump(d))
    assert any("spot" in e for e in validate_all(tmp_path))


def test_validate_all_is_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert validate_all() == []


HOSTILE = [
    ("coupled_with", None), ("options", None), ("book_choice", None), ("positions", None),
    ("evidence", None), ("replaces", None), ("unknowns", None), ("history", None),
    ("options", ["just a string"]), ("options", [{"id": "book", "kind": "book", "facts": ["str"], "why": "x"}]),
    ("options", [{"id": "book", "kind": "book", "facts": [{"text": "t", "cite": None}], "why": "x"}]),
    ("options", [{"id": "book", "kind": "book", "facts": [{"text": "t", "cite": 5}], "why": "x"}]),
    ("positions", ["str"]), ("positions", [{"role": "propulsion", "option": ["x"], "citations": None}]),
    ("decision", "a string"), ("history", ["str"]), ("history", [{"from": "open"}]),
]


@pytest.mark.parametrize("field,value", HOSTILE)
def test_hostile_values_never_crash_validate(tmp_path, field, value):
    d = base()
    d[field] = value
    out = errs(tmp_path, d)  # must return, not raise
    assert isinstance(out, list)
    assert out, f"{field}={value!r} should be reported"


def test_bogus_flag_fails(tmp_path):
    d = base()
    d["options"][1]["facts"] = [{"text": "x", "flag": "bogus"}]
    assert errs(tmp_path, d)


def test_option_without_id_fails(tmp_path):
    d = base()
    d["options"].append({"label": "no id", "kind": "candidate", "facts": [fact()], "why": "x"})
    assert errs(tmp_path, d)


def test_open_record_with_history_fails(tmp_path):
    d = base()
    d["history"] = [{"date": "2026-10-20", "from": "open", "to": "decided", "reason": "x", "option": "alt"}]
    assert errs(tmp_path, d)  # status open but history ends decided


def test_reopened_needs_history(tmp_path):
    d = decided()
    d["status"] = "reopened"
    d["history"] = []
    assert errs(tmp_path, d)


def test_reopened_decision_option_must_exist(tmp_path):
    d = decided()
    d["history"].append({"date": "2026-10-21", "from": "decided", "to": "reopened", "reason": "new data"})
    d["status"] = "reopened"
    d["decision"] = {"option": "ghost", "date": "2026-10-20", "reason": "x"}
    assert any("ghost" in e for e in errs(tmp_path, d))
    d["decision"]["option"] = "alt"
    assert errs(tmp_path, d) == []


def test_decision_option_is_bound_to_history(tmp_path):
    """Review focus 3: editing decision.option alone (history untouched) must fail."""
    d = decided()
    d["decision"]["option"] = "book"  # history still says the owner picked "alt"
    out = errs(tmp_path, d)
    assert out and any("option" in e for e in out)


def test_decided_history_entry_needs_option(tmp_path):
    d = decided()
    d["history"][0].pop("option")
    assert errs(tmp_path, d)




def test_unquoted_yaml_dates_load_as_strings_and_json_dump(tmp_path):
    """An unquoted `date: 2026-10-20` becomes datetime.date in YAML; records must hold strings so hangar.json can be built."""
    d = decided()
    text = yaml.safe_dump(d).replace("'2026-10-20'", "2026-10-20")
    assert "date: 2026-10-20" in text
    p = tmp_path / "demo.yaml"
    p.write_text(text)
    r = load_record(p)
    assert isinstance(r.decision["date"], str) and isinstance(r.history[0]["date"], str)
    json.dumps(dataclasses.asdict(r))
    assert validate(r, GRAPH, {"demo"}) == []
