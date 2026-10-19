"""Research jobs: owner-triggered, public text only, spot-checked, never straight into facts (hangar/research.py)."""

from __future__ import annotations

import dataclasses
import json
import threading
import time
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


# ---- review: public gate, job ids, exclusive run, failures ----

def test_broken_mission_yaml_fails_closed(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    (private / "mission.yaml").write_text("pilots: [\n  {label: Pat Quillfeather, lb: 133.37\n")
    with pytest.raises(ValueError):
        rs.assert_public("nothing private here", private)


def test_normalized_labels_weights_and_other_mission_strings(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    payload = {
        "pilots": [
            {"label": "Bo", "lb": 133.37},
            {"label": "Pat\u00a0Quillfeather", "lb": "180"},
        ],
        "bags_lb": {"nose": 31.43},
        "owner_note": "violet-hangar-token",
    }
    (private / "mission.yaml").write_text(yaml.safe_dump(payload))
    rs.assert_public("The engine weighs 166.2 lb", private)
    rs.assert_public("1133.375 is a different number", private)
    rs.assert_public("European 133,37 stays", private)
    rs.assert_public("Bobby is not the label", private)
    leaks = [
        "pilot 133.370 lb",
        "mass 1.3337e2 lb",
        "mass 1.3337E2 lb",
        "pilot 180.0 lb",
        "pilot 180.000 lb",
        "pilot 1.80e2 lb",
        "pilot 0180 lb",
        "bag 31.430 lb",
        "note violet-hangar-token end",
        "crew Bo today",
        "name Pat Quillfeather end",
        "name Pat\nQuillfeather end",
        "name Pat\u00a0Quillfeather end",
        "name Pat Quill\u200bfeather end",
    ]
    for leak in leaks:
        with pytest.raises(ValueError):
            rs.assert_public(leak, private)


def test_record_decision_history_and_position_strings_are_private(priv):
    record = rec_with_unknowns()
    rs.assert_public("The engine weighs 166.2 lb", priv, record=record)
    for leak in ("because PRIVATE-REASON-TEXT today", record.positions[0]["reasoning"]):
        with pytest.raises(ValueError):
            rs.assert_public(leak, priv, record=record)


def test_queue_refuses_a_brief_that_repeats_decision_text(priv):
    record = rec_with_unknowns()
    record.unknowns[0]["text"] = "See PRIVATE-REASON-TEXT before weighing"
    with pytest.raises(ValueError):
        rs.queue_job(priv, record, "u-coolant")
    assert rs.list_jobs(priv) == []


def test_unsafe_unknown_ids_are_rejected_and_do_not_collide(priv):
    record = rec_with_unknowns()
    for unsafe in ("u/cool", "u..cool", "u cool", "../u-cool"):
        record.unknowns[0]["id"] = unsafe
        with pytest.raises(ValueError):
            rs.queue_job(priv, record, unsafe)
    research = priv / "research"
    assert not research.exists() or list(research.glob("*.json")) == []
    record.unknowns[0]["id"] = "u-cool"
    job = rs.queue_job(priv, record, "u-cool")
    assert rs.load_job(priv, job["id"])["unknown_id"] == "u-cool"
    record.unknowns[0]["id"] = "u/cool"
    with pytest.raises(ValueError):
        rs.queue_job(priv, record, "u/cool")
    assert json.loads((priv / "research" / f"{job['id']}.json").read_text())["unknown_id"] == "u-cool"
    with pytest.raises(KeyError):
        rs.load_job(priv, "cg-ballast--u..cool--1")
    with pytest.raises(KeyError):
        rs.load_job(priv, "not a safe id")


def test_run_job_locks_the_queued_to_running_transition(priv):
    import fcntl

    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    lock_path = priv / "research" / f"{job['id']}.json.lock"
    entered = threading.Event()

    def lane(brief):
        entered.set()
        return proposal()

    with open(lock_path, "a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        errors = []

        def go():
            try:
                rs.run_job(priv, job["id"], lane, check_ok)
            except Exception as exc:
                errors.append(exc)

        thread = threading.Thread(target=go)
        thread.start()
        time.sleep(0.2)
        assert not entered.is_set()
        on_disk = json.loads((priv / "research" / f"{job['id']}.json").read_text())
        assert on_disk["state"] == "queued"
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    thread.join(timeout=5)
    assert errors == [] and entered.is_set()
    assert rs.load_job(priv, job["id"])["state"] == "proposed"


def test_overlapping_run_job_calls_the_lane_once(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    started = threading.Event()
    release = threading.Event()
    calls = []

    def lane(brief):
        calls.append(1)
        started.set()
        assert release.wait(timeout=3)
        return proposal()

    errors = []

    def go():
        try:
            rs.run_job(priv, job["id"], lane, check_ok)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=go), threading.Thread(target=go)]
    for thread in threads:
        thread.start()
    assert started.wait(timeout=3)
    for _ in range(50):
        if errors:
            break
        time.sleep(0.02)
    release.set()
    for thread in threads:
        thread.join(timeout=5)
    assert calls == [1]
    assert len(errors) == 1 and isinstance(errors[0], ValueError)


def test_keyboard_interrupt_leaves_the_job_failed(priv):
    record = rec_with_unknowns()
    job = rs.queue_job(priv, record, "u-coolant")

    def lane(brief):
        raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        rs.run_job(priv, job["id"], lane, check_ok)
    assert rs.load_job(priv, job["id"])["state"] == "failed"
    again = rs.queue_job(priv, record, "u-coolant")
    assert again["id"] != job["id"] and again["state"] == "queued"


def test_spotcheck_base_exception_leaves_the_job_failed(priv):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")

    def check(proposal_):
        raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        rs.run_job(priv, job["id"], lane_returning(proposal()), check)
    assert rs.load_job(priv, job["id"])["state"] == "failed"


def test_default_lane_passes_timeout_to_urlopen(monkeypatch):
    monkeypatch.setenv("HANGAR_RESEARCH_URL", "http://lane.invalid/v1/chat/completions")
    monkeypatch.setenv("HANGAR_RESEARCH_MODEL", "some-model")
    monkeypatch.delenv("HANGAR_RESEARCH_KEY", raising=False)
    seen = {}

    def fake_urlopen(req, timeout=None, **kwargs):
        seen["timeout"] = timeout

        class Resp:
            def read(self):
                body = {"choices": [{"message": {"content": json.dumps(proposal())}}]}
                return json.dumps(body).encode()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return Resp()

    monkeypatch.setattr(rs.urllib.request, "urlopen", fake_urlopen)
    got = rs.default_lane("brief", timeout_s=7)
    assert got["value"] == 4.1 and seen["timeout"] == 7


# ---- review round 2: number tokens, integer weights, short labels, final save ----

def test_private_numbers_glued_to_a_unit_or_letter_still_leak(priv):
    """A unit or letter beside a private number is still that number."""
    for leak in ("133.37lb", "133.37kg", "133.37LB", "x133.37", "x133.37y"):
        with pytest.raises(ValueError):
            rs.assert_public(leak, priv)
    rs.assert_public("1133.375 is a different number", priv)
    rs.assert_public("133.37.1 is a longer token", priv)
    rs.assert_public("133.37,1 is a longer token", priv)


def test_integer_weights_and_short_labels_do_not_block_ordinary_prose(tmp_path):
    """Integer weights collide with public numbers; short labels are case-sensitive."""
    private = tmp_path / "private"
    private.mkdir()
    payload = {
        "pilots": [
            {"label": "In", "lb": 160},
            {"label": "Al", "lb": 200},
            {"label": "Nimbus", "lb": 31.5},
        ],
        "spare_lb": 200.0,
    }
    (private / "mission.yaml").write_text(yaml.safe_dump(payload))
    doc = rs.assert_public.__doc__ or ""
    assert "primary guard" in doc
    assert "integer" in doc.casefold()
    rs.assert_public("Landing margin at 160 lb and also 200", private)
    rs.assert_public("in the aluminum skin", private)
    rs.assert_public("inside the cabin", private)
    rs.assert_public("IN the log and AL of it", private)
    with pytest.raises(ValueError):
        rs.assert_public("pilot In today", private)
    with pytest.raises(ValueError):
        rs.assert_public("crew Al today", private)
    with pytest.raises(ValueError):
        rs.assert_public("bag 31.5 lb", private)
    with pytest.raises(ValueError):
        rs.assert_public("ask nimbus later", private)


def test_queue_job_accepts_a_brief_that_mentions_public_integer_weights(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    (private / "mission.yaml").write_text(yaml.safe_dump({"pilots": [{"label": "In", "lb": 160}, {"label": "Al", "lb": 200}]}))
    job = rs.queue_job(str(private), rec_with_unknowns(), "u-coolant")
    assert job["state"] == "queued"
    assert "160" in job["brief"]


def test_final_save_failure_records_failed_and_reraises(priv, monkeypatch):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    real = rs._save_job

    def flaky(path, job_dict):
        if job_dict.get("state") == "proposed":
            raise OSError("disk full")
        return real(path, job_dict)

    monkeypatch.setattr(rs, "_save_job", flaky)
    with pytest.raises(OSError, match="disk full"):
        rs.run_job(priv, job["id"], lane_returning(proposal()), check_ok)
    saved = rs.load_job(priv, job["id"])
    assert saved["state"] == "failed"
    assert "disk full" in (saved.get("error") or "")


def test_failed_state_save_is_retried_without_masking(priv, monkeypatch):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    real = rs._save_job
    seen = {"failed": 0}

    def flaky(path, job_dict):
        if job_dict.get("state") == "failed":
            seen["failed"] += 1
            if seen["failed"] == 1:
                raise OSError("disk full")
            if seen["failed"] > 2:
                raise RuntimeError("retry failed")
        return real(path, job_dict)

    monkeypatch.setattr(rs, "_save_job", flaky)
    with pytest.raises(OSError, match="disk full"):
        rs.run_job(priv, job["id"], lane_returning(None), check_ok)
    saved = rs.load_job(priv, job["id"])
    assert saved["state"] == "failed"
    assert saved.get("error")
    assert seen["failed"] >= 2


def test_retry_of_a_final_save_does_not_replace_the_original_exception(priv, monkeypatch):
    job = rs.queue_job(priv, rec_with_unknowns(), "u-coolant")
    real = rs._save_job

    def flaky(path, job_dict):
        if job_dict.get("state") == "proposed":
            raise OSError("disk full")
        if job_dict.get("state") == "failed":
            raise RuntimeError("retry failed")
        return real(path, job_dict)

    monkeypatch.setattr(rs, "_save_job", flaky)
    with pytest.raises(OSError, match="disk full"):
        rs.run_job(priv, job["id"], lane_returning(proposal()), check_ok)
