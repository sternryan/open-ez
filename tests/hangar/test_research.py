"""Research jobs: owner-triggered, public text only, spot-checked, never straight into facts (hangar/research.py)."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest
import yaml

from hangar import research as rs
from hangar.records import load_record

REC = Path("data/hangar/mod-ez/decisions/cg-ballast.yaml")
PRIVATE = {"pilots": [{"label": "Pat Quillfeather", "lb": 133.37}, {"label": "Sam", "lb": 187.91}], "bags_lb": 31.43}


def rec_with_unknowns():
    rec = load_record(REC)
    unknowns = [
        {"id": "u-coolant", "text": "Coolant and radiator weight for the 912 iS installation", "how": "maker installation manual",
         "affects": ["loading-limit", "fixed-aft-ballast"], "state": "open"},
        {"id": "u-arm", "text": "The 912 iS installed CG arm", "how": "weigh the installation",
         "affects": ["engine-arm-aft"], "state": "sourced"},
    ]
    positions = [{"role": "propulsion", "picks": {}, "confidence": "low", "reasoning": "my friend Pat Quillfeather weighs 133.37 lb", "citations": []}]
    decision = {"picks": {"cg_fix": "loading-limit"}, "date": "2026-10-01", "reason": "PRIVATE-REASON-TEXT"}
    return dataclasses.replace(rec, unknowns=unknowns, positions=positions, decision=decision,
                               history=[{"date": "2026-10-01", "from": "open", "to": "decided", "reason": "PRIVATE-REASON-TEXT"}])


@pytest.fixture
def priv(tmp_path):
    d = tmp_path / "private"
    d.mkdir()
    (d / "mission.yaml").write_text(yaml.safe_dump(PRIVATE))
    return d


def proposal(**kw):
    p = {"claim": "coolant and radiator 4.1 lb", "value": 4.1, "unit": "lb", "url": "https://example.org/manual.html",
         "title": "Example maker manual", "quote": "coolant and radiator 4.1 lb"}
    p.update(kw)
    return p


def lane_returning(p):
    return lambda brief: p


def check_ok(p):
    return {"method": "http fetch + text search", "fetched": True, "matched": True, "quote_found": True, "value_found": True, "detail": "ok"}


def check_bad(p):
    return {"method": "http fetch + text search", "fetched": True, "matched": False, "quote_found": False, "value_found": None, "detail": "quote not found"}


# ---- the public brief ----

def test_public_brief_has_the_unknown_and_the_affected_option_facts_only():
    b = rs.public_brief(rec_with_unknowns(), "u-coolant")
    assert "Coolant and radiator weight" in b and "maker installation manual" in b
    assert "No change, publish a loading limit" in b and "Fixed aft ballast" in b          # affected option labels
    assert "Move the battery aft" not in b and "Move the engine installation aft" not in b  # unaffected options stay out
    for private in ("Pat Quillfeather", "133.37", "PRIVATE-REASON-TEXT", "friend"):
        assert private not in b


def test_public_brief_unknown_id_raises():
    with pytest.raises(KeyError):
        rs.public_brief(rec_with_unknowns(), "u-missing")


def test_assert_public_refuses_owner_labels_and_weights(priv):
    rs.assert_public("The engine weighs 166.2 lb", priv)  # fine
    for leak in ("ask Pat Quillfeather", "a 133.37 lb pilot", "bag of 31.43", "187.91"):
        with pytest.raises(ValueError):
            rs.assert_public(leak, priv)
    rs.assert_public("1133.375 is a different number", priv)   # whole-number match only
    rs.assert_public("anything", None)                          # no private dir, nothing to check
    rs.assert_public("anything", priv / "missing")


# ---- queue ----

def test_queue_job_writes_a_private_job_and_marks_nothing_public(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant", now="2026-10-19T10:00:00+00:00")
    assert job["state"] == "queued" and job["record_id"] == "cg-ballast" and job["unknown_id"] == "u-coolant"
    assert "Coolant and radiator weight" in job["brief"]
    path = priv / "research" / f"{job['id']}.json"
    assert path.is_file() and json.loads(path.read_text())["id"] == job["id"]
    assert rs.list_jobs(priv, "cg-ballast")[0]["id"] == job["id"]
    assert rs.list_jobs(priv, "other") == []
    assert "/" not in job["id"] and ".." not in job["id"]


def test_queue_job_refuses_unknown_ids_sourced_unknowns_and_double_queue(priv):
    rec = rec_with_unknowns()
    with pytest.raises(KeyError):
        rs.queue_job(priv, rec, "nope")
    with pytest.raises(ValueError):
        rs.queue_job(priv, rec, "u-arm")      # already sourced
    rs.queue_job(priv, rec, "u-coolant")
    with pytest.raises(ValueError, match="already"):
        rs.queue_job(priv, rec, "u-coolant")


def test_queue_job_refuses_a_brief_that_leaks(priv):
    rec = rec_with_unknowns()
    rec.unknowns[0]["text"] = "weight for Pat Quillfeather"
    with pytest.raises(ValueError):
        rs.queue_job(priv, rec, "u-coolant")
    assert rs.list_jobs(priv) == []


# ---- run ----

def test_run_job_proposes_when_the_lane_answers_and_the_spotcheck_runs(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    seen = []
    out = rs.run_job(priv, job["id"], lambda brief: (seen.append(brief), proposal())[1], check_ok)
    assert out["state"] == "proposed" and out["proposal"]["url"] == "https://example.org/manual.html"
    assert out["spotcheck"]["matched"] is True and seen == [job["brief"]]
    assert json.loads((priv / "research" / f"{job['id']}.json").read_text())["state"] == "proposed"


def test_failed_spotcheck_still_lands_as_a_proposal_with_matched_false(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    out = rs.run_job(priv, job["id"], lane_returning(proposal()), check_bad)
    assert out["state"] == "proposed" and out["spotcheck"]["matched"] is False


@pytest.mark.parametrize("bad", [None, "text", {}, proposal(url="file:///etc/passwd"), proposal(quote=""), proposal(url=7), proposal(claim=None)])
def test_run_job_fails_loudly_on_a_bad_proposal(priv, bad):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    out = rs.run_job(priv, job["id"], lane_returning(bad), check_ok)
    assert out["state"] == "failed" and out["error"] and out.get("proposal") is None


def test_run_job_records_lane_and_spotcheck_exceptions(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")

    def lane(brief):
        raise rs.ResearchUnavailable("no lane")

    out = rs.run_job(priv, job["id"], lane, check_ok)
    assert out["state"] == "failed" and "no lane" in out["error"]
    job2 = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")  # a failed job does not block a new one
    assert job2["id"] != job["id"]

    def check_boom(p):
        raise RuntimeError("check crashed")

    out2 = rs.run_job(priv, job2["id"], lane_returning(proposal()), check_boom)
    assert out2["state"] == "failed" and "check crashed" in out2["error"]


def test_run_job_only_runs_queued_jobs(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    rs.run_job(priv, job["id"], lane_returning(proposal()), check_ok)
    with pytest.raises(ValueError):
        rs.run_job(priv, job["id"], lane_returning(proposal()), check_ok)
    with pytest.raises(KeyError):
        rs.run_job(priv, "no-such-job", lane_returning(proposal()), check_ok)
    with pytest.raises(KeyError):
        rs.run_job(priv, "../../etc/passwd", lane_returning(proposal()), check_ok)


def test_finish_job_states(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    rs.run_job(priv, job["id"], lane_returning(proposal()), check_ok)
    assert rs.finish_job(priv, job["id"], "dismissed", note="not the right part")["state"] == "dismissed"
    with pytest.raises(ValueError):
        rs.finish_job(priv, job["id"], "accepted")      # no going back from a finished job
    job2 = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    with pytest.raises(ValueError):
        rs.finish_job(priv, job2["id"], "banana")


# ---- the default lane ----

def test_default_lane_needs_its_environment(monkeypatch):
    for k in ("HANGAR_RESEARCH_URL", "HANGAR_RESEARCH_MODEL", "HANGAR_RESEARCH_KEY"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(rs.ResearchUnavailable):
        rs.default_lane("brief")


def test_default_lane_sends_the_public_brief_and_parses_json(monkeypatch):
    monkeypatch.setenv("HANGAR_RESEARCH_URL", "http://lane.invalid/v1/chat/completions")
    monkeypatch.setenv("HANGAR_RESEARCH_MODEL", "some-model")
    monkeypatch.delenv("HANGAR_RESEARCH_KEY", raising=False)
    sent = []

    def post(payload, headers):
        sent.append((payload, headers))
        return {"choices": [{"message": {"content": "Here:\n```json\n" + json.dumps(proposal()) + "\n```"}}]}

    got = rs.default_lane("the brief text", post=post)
    assert got["value"] == 4.1 and got["url"].startswith("https://")
    payload, headers = sent[0]
    assert payload["model"] == "some-model" and "the brief text" in json.dumps(payload["messages"])
    assert "Authorization" not in headers
    system = payload["messages"][0]["content"]
    for word in ("url", "quote", "value", "public"):
        assert word in system
    with pytest.raises(rs.ResearchUnavailable):
        rs.default_lane("x", post=lambda p, h: {"choices": [{"message": {"content": "no json at all"}}]})
