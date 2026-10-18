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
        dict(pos(), picks={"engine": ["x"]}), dict(pos(), reasoning=None), dict(pos(role="historian")),
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


def test_picks_are_validated_per_axis(tmp_path):
    from tests.hangar.test_axes import two_axes

    r = make(tmp_path, two_axes())
    ps = [
        dict(pos(role="propulsion"), picks={"engine": "alt", "fuel_path": "f2", "colour": "red"}),  # bad axis dropped
        dict(pos(role="structures"), picks={"engine": "f1"}),  # wrong option for the axis: nothing valid left, position dropped
        dict(pos(role="historian"), picks={"fuel_path": "f1"}),  # partial picks are fine
        dict(pos(role="aero-flight-test"), picks="alt"),  # not a mapping
        dict(pos(role="fuel-systems"), picks={"engine": "old"}),  # a dropped option may be argued but not as a pick
    ]
    out = ask(r, "go", [], post=fake(reply_of(ps)))
    got = {p["role"]: p["picks"] for p in out.positions}
    assert got == {"propulsion": {"engine": "alt", "fuel_path": "f2"}, "historian": {"fuel_path": "f1"}}


def test_prompt_and_backbone_carry_axes(tmp_path):
    from tests.hangar.test_axes import two_axes

    r = make(tmp_path, two_axes())
    assert backbone(r)["axes"][1]["id"] == "fuel_path"
    post = fake(reply_of([pos()]))
    ask(r, "go", [], post=post)
    system = post.seen[0]["messages"][0]["content"].lower()
    assert "picks" in system and "axes" in system
