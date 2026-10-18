"""Decision-record schema and gates (Hangar H1)."""

from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from hangar import records
from hangar.records import ROLES, STATUSES, load_record, load_records, load_spots, validate, validate_all

GRAPH = SimpleNamespace(ops={"f23.engine-install": object(), "f21.close-tank": object()})


def fact(**kw):
    d = {"text": "a fact", "cite": "om-1980:p4"}
    d.update(kw)
    return d


def base() -> dict:
    return {
        "id": "demo",
        "spot": "mod-ez",
        "title": "Demo decision",
        "status": "open",
        "question": "Which engine?",
        "coupled_with": [],
        "replaces": ["f23.engine-install"],
        "book_choice": {"text": "the book engine", "cite": "om-1980:p4"},
        "options": [
            {"id": "book", "label": "Book", "kind": "book", "facts": [fact()], "why": "kept as baseline"},
            {"id": "alt", "label": "Alt", "kind": "candidate", "facts": [fact()], "why": "lighter"},
        ],
        "positions": [],
        "unknowns": [],
        "mission_score": None,
        "decision": None,
        "history": [],
        "changes": None,
        "evidence": {"paper": "none", "material": "none", "outside_review": "none", "flight": "none"},
    }


def make(tmp_path: Path, d: dict) -> records.Record:
    p = tmp_path / f"{d['id']}.yaml"
    p.write_text(yaml.safe_dump(d))
    return load_record(p)


def errs(tmp_path: Path, d: dict, all_ids=None) -> list[str]:
    rec = make(tmp_path, d)
    return validate(rec, GRAPH, all_ids if all_ids is not None else {d["id"]})


def mutated(**kw) -> dict:
    d = copy.deepcopy(base())
    d.update(kw)
    return d


def test_base_record_is_valid(tmp_path):
    assert errs(tmp_path, base()) == []


def test_constants():
    assert ROLES == ("propulsion", "structures", "fuel-systems", "aero-flight-test", "historian")
    assert STATUSES == ("open", "decided", "reopened")


def test_unknown_citation_fails(tmp_path):
    d = base()
    d["options"][1]["facts"] = [fact(cite="nosuch:p1")]
    out = errs(tmp_path, d)
    assert any("unknown source id" in e for e in out)


def test_empty_replaces_fails(tmp_path):
    out = errs(tmp_path, mutated(replaces=[]))
    assert any("replaces" in e for e in out)


def test_replaces_must_be_graph_ids(tmp_path):
    out = errs(tmp_path, mutated(replaces=["f99.nope"]))
    assert any("f99.nope" in e for e in out)
    assert errs(tmp_path, mutated(replaces=["f23.engine-install"])) == []


def test_book_option_required(tmp_path):
    d = base()
    d["options"] = [d["options"][1]]
    out = errs(tmp_path, d)
    assert any("book" in e for e in out)


def test_fact_needs_cite_or_flag(tmp_path):
    d = base()
    d["options"][1]["facts"] = [{"text": "no source"}]
    assert errs(tmp_path, d)
    d["options"][1]["facts"] = [{"text": "no source", "flag": "unknown"}]
    assert errs(tmp_path, d) == []


def position(role="propulsion", option="alt"):
    return {
        "role": role,
        "option": option,
        "confidence": "medium",
        "reasoning": "because",
        "citations": ["om-1980:p4"],
        "judgment": False,
    }


def test_position_role_fixed(tmp_path):
    d = base()
    d["positions"] = [position(role="chef")]
    assert any("chef" in e for e in errs(tmp_path, d))
    d["positions"] = [position(role=r) for r in ROLES]
    assert errs(tmp_path, d) == []


def test_position_option_and_confidence(tmp_path):
    d = base()
    d["positions"] = [position(option="ghost")]
    assert any("ghost" in e for e in errs(tmp_path, d))
    d["positions"] = [dict(position(), confidence="certain")]
    assert errs(tmp_path, d)


def decided(**kw):
    d = base()
    d["status"] = "decided"
    d["decision"] = {"option": "alt", "date": "2026-10-20", "reason": "lighter"}
    d["history"] = [{"date": "2026-10-20", "from": "open", "to": "decided", "reason": "lighter"}]
    d.update(kw)
    return d


def test_decided_record_is_valid(tmp_path):
    assert errs(tmp_path, decided()) == []


def test_decided_needs_decision(tmp_path):
    assert errs(tmp_path, decided(decision=None))
    d = base()
    d["decision"] = {"option": "alt", "date": "2026-10-20", "reason": "x"}
    assert errs(tmp_path, d)  # open with a decision


def test_decision_option_exists(tmp_path):
    d = decided(decision={"option": "ghost", "date": "2026-10-20", "reason": "x"})
    assert any("ghost" in e for e in errs(tmp_path, d))


def test_decision_needs_reason(tmp_path):
    d = decided(decision={"option": "alt", "date": "2026-10-20", "reason": ""})
    assert errs(tmp_path, d)


def test_redecide_requires_reopen(tmp_path):
    bad = decided()
    bad["history"].append({"date": "2026-10-21", "from": "decided", "to": "decided", "reason": "changed my mind"})
    bad["decision"] = {"option": "book", "date": "2026-10-21", "reason": "changed my mind"}
    assert errs(tmp_path, bad)
    good = decided()
    good["history"] += [
        {"date": "2026-10-21", "from": "decided", "to": "reopened", "reason": "new data"},
        {"date": "2026-10-22", "from": "reopened", "to": "decided", "reason": "settled"},
    ]
    good["decision"] = {"option": "book", "date": "2026-10-22", "reason": "settled"}
    assert errs(tmp_path, good) == []


def test_hand_edit_without_history_fails(tmp_path):
    """A decided record whose decision is not backed by a to:decided history entry fails."""
    d = decided(history=[])
    assert errs(tmp_path, d)


def test_history_entry_needs_date_and_reason(tmp_path):
    d = decided()
    d["history"][0]["reason"] = ""
    assert errs(tmp_path, d)
    d = decided()
    d["history"][0].pop("date")
    assert errs(tmp_path, d)


def test_coupled_ids_exist(tmp_path):
    assert any("ghost" in e for e in errs(tmp_path, mutated(coupled_with=["ghost"])))
    assert errs(tmp_path, mutated(coupled_with=["other"]), all_ids={"demo", "other"}) == []


def test_unknown_status_fails(tmp_path):
    assert errs(tmp_path, mutated(status="maybe"))


def test_load_records_layout(tmp_path):
    d = tmp_path / "mod-ez" / "decisions"
    d.mkdir(parents=True)
    (d / "demo.yaml").write_text(yaml.safe_dump(base()))
    got = load_records(tmp_path)
    assert list(got) == ["demo"]
    assert validate_all(tmp_path, Path("guide/graph")) == []


def test_repo_records_valid():
    assert validate_all() == []


def test_spots():
    spots = load_spots()
    assert [s["id"] for s in spots] == ["long-ez-1980", "mod-ez", "rv-12", "model-1"]
    assert [s["state"] for s in spots] == ["foundation", "active", "reserved", "reserved"]
    assert [s["label"] for s in spots] == ["1980 Rutan Long-EZ", "Mod-EZ", "Van's RV-12", "Stern Model 1"]
    assert [s["analogue"] for s in spots] == ["concours restoration", "restomod", "kit", "scratch build"]
    assert all(s["blurb"] for s in spots)
