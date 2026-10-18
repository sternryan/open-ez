"""Council engine: prompt pack, model call, deterministic post-validation (Hangar H2)."""

from __future__ import annotations

import json

import pytest

from hangar.council import CouncilReply, CouncilUnavailable, ask, backbone
from hangar.records import ROLES
from tests.hangar.test_records import base, make


def rec(tmp_path):
    return make(tmp_path, base())


def pos(role="propulsion", option="alt", conf="medium", cites=("om-1980:p4",), judgment=False):
    return {
        "role": role,
        "option": option,
        "confidence": conf,
        "reasoning": "because",
        "citations": list(cites),
        "judgment": judgment,
    }


def reply_of(positions, text="hello", unknowns=()):
    body = {"positions": positions, "reply_text": text, "unknowns": list(unknowns)}
    return {"choices": [{"message": {"content": json.dumps(body)}}]}


def fake(resp):
    seen = []

    def post(payload):
        seen.append(payload)
        return resp

    post.seen = seen
    return post


def test_valid_reply_passes_through(tmp_path):
    r = rec(tmp_path)
    out = ask(r, "go", [], post=fake(reply_of([pos(role=x) for x in ROLES], text="hi")))
    assert isinstance(out, CouncilReply)
    assert out.error is None
    assert [p["role"] for p in out.positions] == list(ROLES)
    assert all(p["judgment"] is False for p in out.positions)
    assert out.reply_text == "hi"


def test_fenced_json_is_accepted(tmp_path):
    body = json.loads(reply_of([pos()])["choices"][0]["message"]["content"])
    fenced = "```json\n" + json.dumps(body) + "\n```"
    out = ask(rec(tmp_path), "go", [], post=fake({"choices": [{"message": {"content": fenced}}]}))
    assert out.error is None and len(out.positions) == 1


def test_uncited_claim_becomes_judgment(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(cites=("madeup:p3",))])))
    p = out.positions[0]
    assert p["citations"] == []
    assert p["judgment"] is True
    assert p["reasoning"].endswith("(uncited)")


def test_registered_but_not_in_backbone_is_removed(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(cites=("plans-1980:p21",))])))
    assert out.positions[0]["citations"] == []
    assert out.positions[0]["judgment"] is True


def test_good_cite_kept_bad_cite_dropped(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(cites=("om-1980:p4", "madeup:p3"))])))
    p = out.positions[0]
    assert p["citations"] == ["om-1980:p4"]
    assert p["judgment"] is True and p["reasoning"].endswith("(uncited)")


def test_bad_role_and_option_dropped(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(role="chef"), pos(option="ghost"), pos()])))
    assert len(out.positions) == 1
    assert out.positions[0]["role"] == "propulsion" and out.positions[0]["option"] == "alt"


def test_bad_confidence_becomes_low(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake(reply_of([pos(conf="certain")])))
    assert out.positions[0]["confidence"] == "low"


def test_non_json_reply(tmp_path):
    out = ask(rec(tmp_path), "go", [], post=fake({"choices": [{"message": {"content": "sure!"}}]}))
    assert out.error
    assert out.positions == []


def test_timeout(tmp_path):
    def boom(payload):
        raise TimeoutError("slow")

    out = ask(rec(tmp_path), "go", [], post=boom)
    assert out.error
    assert out.positions == []


def test_missing_env_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("HANGAR_COUNCIL_URL", raising=False)
    monkeypatch.delenv("HANGAR_COUNCIL_MODEL", raising=False)
    with pytest.raises(CouncilUnavailable):
        ask(rec(tmp_path), "go", [])


def test_prompt_carries_message_history_and_backbone(tmp_path):
    post = fake(reply_of([pos()]))
    ask(rec(tmp_path), "MSG-123", [{"role": "user", "content": "EARLIER-456"}], post=post)
    blob = json.dumps(post.seen[0])
    assert "MSG-123" in blob and "EARLIER-456" in blob and "om-1980:p4" in blob


def test_backbone_shape(tmp_path):
    b = backbone(rec(tmp_path))
    assert "om-1980:p4" in b["cites"]
    assert b["book_choice"]["text"] == "the book engine"
    assert "om-1980" in b["sources"]


def test_backbone_has_no_private_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", "/secret/dir")
    s = json.dumps(backbone(rec(tmp_path)))
    assert "private/" not in s and "/secret/dir" not in s
