"""Decision axes: a decision picks one option per declared axis (Hangar H1/H2 amendment)."""

from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest
import yaml

from hangar.records import validate
from tests.hangar.test_records import GRAPH, base, errs, fact, make


def two_axes() -> dict:
    d = copy.deepcopy(base())
    d["options"] += [
        {"id": "f1", "label": "F1", "kind": "candidate", "facts": [fact()], "why": "x",
         "implies": {"tank_resin": "the book resin is fine", "flag": "unknown"}},
        {"id": "f2", "label": "F2", "kind": "candidate", "facts": [fact()], "why": "x",
         "implies": {"tank_resin": "needs a fuel-resistant resin", "cite": "om-1980:p4"}},
        {"id": "old", "label": "Old", "kind": "dropped", "facts": [fact()], "why": "x"},
    ]
    d["axes"] = [{"id": "engine", "options": ["book", "alt", "old"]}, {"id": "fuel_path", "options": ["f1", "f2"]}]
    return d


def decided_two(picks=None, history_picks=None) -> dict:
    d = two_axes()
    picks = picks or {"engine": "alt", "fuel_path": "f2"}
    d["status"] = "decided"
    d["decision"] = {"picks": picks, "date": "2026-10-20", "reason": "r"}
    d["history"] = [{"date": "2026-10-20", "from": "open", "to": "decided", "reason": "r",
                     "picks": history_picks or picks}]
    return d


def test_two_axis_decided_record_is_valid(tmp_path):
    assert errs(tmp_path, two_axes()) == []
    assert errs(tmp_path, decided_two()) == []


def test_axes_are_required(tmp_path):
    d = base()
    d.pop("axes")
    with pytest.raises(ValueError):
        make(tmp_path, d)
    d["axes"] = []
    assert any("axes" in e for e in errs(tmp_path, d))


def test_axis_options_must_exist_and_ids_be_unique(tmp_path):
    d = two_axes()
    d["axes"][1]["options"] = ["f1", "ghost"]
    assert any("ghost" in e for e in errs(tmp_path, d))
    d = two_axes()
    d["axes"][1]["id"] = "engine"
    assert any("engine" in e and "duplicate" in e.lower() for e in errs(tmp_path, d))


def test_every_axis_must_be_picked(tmp_path):
    out = errs(tmp_path, decided_two(picks={"engine": "alt"}))
    assert any("fuel_path" in e for e in out)


def test_pick_must_be_in_the_axis_options(tmp_path):
    out = errs(tmp_path, decided_two(picks={"engine": "f1", "fuel_path": "f2"}))
    assert any("engine" in e and "f1" in e for e in out)


def test_unknown_axis_in_picks_fails(tmp_path):
    out = errs(tmp_path, decided_two(picks={"engine": "alt", "fuel_path": "f2", "colour": "red"}))
    assert any("colour" in e for e in out)


def test_dropped_or_unavailable_pick_fails(tmp_path):
    out = errs(tmp_path, decided_two(picks={"engine": "old", "fuel_path": "f2"}))
    assert any("dropped" in e for e in out)


def test_picks_must_match_history(tmp_path):
    out = errs(tmp_path, decided_two(history_picks={"engine": "book", "fuel_path": "f2"}))
    assert any("pick" in e for e in out)
    d = decided_two()
    d["history"][0].pop("picks")
    assert errs(tmp_path, d)


def test_picks_must_be_a_mapping(tmp_path):
    d = decided_two()
    d["decision"]["picks"] = ["alt", "f2"]
    assert errs(tmp_path, d)
    d["decision"].pop("picks")
    assert errs(tmp_path, d)


def test_implies_shape(tmp_path):
    d = two_axes()
    d["options"][2]["implies"] = {"tank_resin": "x"}  # neither cite nor flag
    assert errs(tmp_path, d)
    d = two_axes()
    d["options"][2]["implies"] = {"flag": "unknown"}  # no tank_resin text
    assert errs(tmp_path, d)
    d = two_axes()
    d["options"][2]["implies"] = {"tank_resin": "x", "cite": "nosuch:p1"}
    assert any("unknown source id" in e for e in errs(tmp_path, d))


def test_position_picks(tmp_path):
    base_pos = {"role": "propulsion", "confidence": "low", "reasoning": "r", "citations": [], "judgment": True}
    d = two_axes()
    d["positions"] = [dict(base_pos, picks={"engine": "alt", "fuel_path": "f1"}), dict(base_pos, picks={"fuel_path": "f2"})]
    assert errs(tmp_path, d) == []
    for bad in ({"colour": "alt"}, {"engine": "f1"}, ["alt"], {}):
        d["positions"] = [dict(base_pos, picks=bad)]
        assert errs(tmp_path, d), bad


def test_decision_picks_with_two_axes_through_the_server_shape(tmp_path):
    # validate() directly: a reopened record may keep its picks, which must still be valid
    d = decided_two()
    d["status"] = "reopened"
    d["history"].append({"date": "2026-10-21", "from": "decided", "to": "reopened", "reason": "new data"})
    assert errs(tmp_path, d) == []
    d["decision"]["picks"]["fuel_path"] = "ghost"
    assert errs(tmp_path, d)
