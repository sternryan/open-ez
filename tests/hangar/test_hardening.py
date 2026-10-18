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


# ---------------------------------------------------------------- mission


def V(v, flag="sourced", note=""):
    return {"v": v, "flag": flag, "note": note}


MISSION = {
    "leg_nm": 300, "reserve_min": 30, "occupants_lb": [155, 155], "bags_lb": 15,
    "cruise_ktas": V(150), "fuel_capacity_gal": V(52), "fuel_density_lb_per_gal": V(6.0),
}


def plant(arm=V(141.05, "derived", "assumed same installed CG as the book engine"), ff=V(4.3), lb=V(173.0)):
    return {"x": {"installed_lb": lb, "cg_arm_in": arm, "cruise_ff_gph": ff}}


def test_unknown_cg_arm_does_not_crash():
    s = mission.score("x", MISSION, plant(arm=V(None, "unknown")))
    assert s.takeoff_cg.v is None and s.landing_cg.v is None and s.empty_cg.v is None
    assert s.in_envelope is None and s.worst_flag == "unknown"
    assert s.empty_lb.v is not None  # the weight does not need the arm


def test_null_value_is_unknown_whatever_the_flag():
    s = mission.score("x", MISSION, plant(ff=V(None, "derived")))
    assert s.fuel_needed_lb.v is None and s.fuel_needed_lb.flag == "unknown"
    assert s.worst_flag == "unknown"


def test_oil_is_in_the_takeoff_loading():
    s = mission.score("x", MISSION, plant())
    fuel = 4.3 * 2.5 * 6.0
    assert s.takeoff_lb.v == pytest.approx(s.empty_lb.v + 310 + 15 + 8 + fuel)


def test_private_override_reaches_score_and_is_derived(tmp_path, monkeypatch):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"cruise_ktas": 160}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(tmp_path))
    s = mission.score("o235-book")
    assert s.block_time_h.v == pytest.approx(300 / 160 + 0.5)
    assert s.block_time_h.flag == "derived"  # a bare private number is never "sourced"


def test_write_scores_ignores_the_private_dir(tmp_path, monkeypatch):
    root = tmp_path / "hangar"
    shutil.copytree(DATA_ROOT, root)
    mission.write_scores(root)
    before = (root / "mod-ez/decisions/powerplant-fuel-resin.yaml").read_text()
    priv = tmp_path / "priv"
    priv.mkdir()
    (priv / "mission.yaml").write_text(yaml.safe_dump({"occupants_lb": [250, 250], "cruise_ktas": 120}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(priv))
    mission.write_scores(root)
    assert (root / "mod-ez/decisions/powerplant-fuel-resin.yaml").read_text() == before


def test_assumptions_surface_caveat_notes():
    a = " ".join(mission.score("rotax-912is").assumptions).lower()
    assert "coolant" in a  # the installed-weight caveat
    assert "assumed same installed cg" in a


# ---------------------------------------------------------------- council


def rec(tmp_path, d=None):
    return make(tmp_path, d or base())


def test_empty_citations_means_judgment(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(cites=())])))
    p = out.positions[0]
    assert p["judgment"] is True and p["reasoning"].endswith("(uncited)")


def test_judgment_is_coerced_to_bool(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([dict(pos(), judgment="false")])))
    assert out.positions[0]["judgment"] in (True, False) and isinstance(out.positions[0]["judgment"], bool)


def test_book_choice_cite_is_citable(tmp_path):
    d = base()
    d["book_choice"] = {"text": "x", "cite": "plans-1980:p21"}
    r = rec(tmp_path, d)
    assert "plans-1980:p21" in backbone(r)["cites"]
    out = ask(r, "go", [], post=fake(reply_of([pos(cites=("plans-1980:p21",))])))
    assert out.positions[0]["citations"] == ["plans-1980:p21"] and out.positions[0]["judgment"] is False


def test_backbone_carries_couplings_and_unknowns(tmp_path):
    d = base()
    d["coupled_with"] = ["other"]
    d["unknowns"] = [{"text": "ethanol limit", "how": "ask"}]
    b = backbone(rec(tmp_path, d))
    assert b["coupled_with"] == ["other"] and b["unknowns"][0]["text"] == "ethanol limit"


def test_citation_with_trailing_text_is_normalized(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(cites=("om-1980:p4 sample empty",))])))
    assert out.positions[0]["citations"] == ["om-1980:p4"] and out.positions[0]["judgment"] is False


@pytest.mark.parametrize("content", [
    "```json\n{BODY}\n```\n", "```JSON\n{BODY}\n```", "  ```\n{BODY}\n```  ",
    "Here is my answer:\n```json\n{BODY}\n```\nHope that helps.", "Sure. {BODY} done",
])
def test_fence_and_prose_variants(tmp_path, content):
    body = reply_of([pos()])["choices"][0]["message"]["content"]
    out = ask(rec(tmp_path), "go", [], post=fake({"choices": [{"message": {"content": content.replace("{BODY}", body)}}]}))
    assert out.error is None and len(out.positions) == 1


def test_one_bad_position_does_not_kill_the_reply(tmp_path):
    bad = [
        "str", None, 5, dict(pos(), citations=None), dict(pos(), citations=[5, None, ["x"]]),
        dict(pos(), option=["x"]), dict(pos(), reasoning=None), dict(pos(role="historian")),
    ]
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of(bad)))
    assert out.error is None
    assert any(p["role"] == "historian" for p in out.positions)
    assert all(isinstance(p["reasoning"], str) and isinstance(p["citations"], list) for p in out.positions)


@pytest.mark.parametrize("body", ['["a"]', '{"positions": null}', '{"positions": {"a": 1}}', '{"reply_text": 5}', "null"])
def test_odd_top_level_shapes_do_not_crash(tmp_path, body):
    out = ask(rec(tmp_path), "go", [], post=fake({"choices": [{"message": {"content": body}}]}))
    assert isinstance(out, CouncilReply)
    assert isinstance(out.reply_text, str) and isinstance(out.unknowns, list) and isinstance(out.positions, list)


def test_missing_choices_is_an_error_reply(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake({"oops": 1}))
    assert out.error and out.positions == []


def test_backbone_failure_stays_inside_the_contract(tmp_path):
    d = base()
    d["options"][1]["facts"] = [{"text": "t", "cite": 5}]
    r = rec(tmp_path, d)
    out = ask(r, "go", [], post=fake(reply_of([pos()])))  # must not raise
    assert isinstance(out, CouncilReply)


def test_history_roles_are_whitelisted(tmp_path):
    post = fake(reply_of([pos()]))
    hist = [{"role": "system", "content": "EVIL-SYSTEM"}, {"role": "user", "content": "ok-user"}, {"role": "assistant", "content": 5}]
    ask(rec(tmp_path), "go", hist, post=post)
    blob = json.dumps(post.seen[0])
    assert "EVIL-SYSTEM" not in blob and "ok-user" in blob


def test_prompt_carries_the_schema_and_behaviors(tmp_path):
    post = fake(reply_of([pos()]))
    ask(rec(tmp_path), "go", [], post=post)
    system = post.seen[0]["messages"][0]["content"].lower()
    for word in ("positions", "reply_text", "unknowns", "citations", "judgment", "confidence", "reasoning",
                 "propulsion", "structures", "fuel-systems", "aero-flight-test", "historian",
                 "unknown", "disagree", "coupl", "mission", "trust standard"):
        assert word in system, word
    user = post.seen[0]["messages"][-1]["content"]
    assert '"alt"' in user or "alt" in user  # option ids are in the pack the model sees


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_default_post_uses_env_model_url_and_key(tmp_path, monkeypatch):
    seen = {}

    def fake_urlopen(req, timeout=None):
        seen["url"], seen["data"], seen["headers"], seen["timeout"] = req.full_url, req.data, dict(req.header_items()), timeout
        return FakeResp(json.dumps(reply_of([pos()])).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setenv("HANGAR_COUNCIL_URL", "http://example.invalid/v1/")
    monkeypatch.setenv("HANGAR_COUNCIL_MODEL", "model-xyz")
    monkeypatch.delenv("HANGAR_COUNCIL_KEY", raising=False)
    out = ask(rec(tmp_path), "go", [], timeout_s=7)
    assert out.error is None and len(out.positions) == 1
    assert seen["url"] == "http://example.invalid/v1/chat/completions" and seen["timeout"] == 7
    assert json.loads(seen["data"])["model"] == "model-xyz"
    assert not any(k.lower() == "authorization" for k in seen["headers"])
    monkeypatch.setenv("HANGAR_COUNCIL_KEY", "k123")
    ask(rec(tmp_path), "go", [])
    assert any(k.lower() == "authorization" and v == "Bearer k123" for k, v in seen["headers"].items())


def test_error_text_does_not_echo_the_url(tmp_path):
    def boom(payload):
        raise OSError("connect to http://10.1.2.3:9/secret failed")

    out = ask(rec(tmp_path), "go", [], post=boom)
    assert out.error and "10.1.2.3" not in out.error and "secret" not in out.error
