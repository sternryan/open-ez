"""Briefing-room matrix, research and the decide acknowledgement gate (wave 3)."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import http.client
import yaml

from hangar.briefing_server import make_server
from hangar.matrix import matrix_for_effect
from hangar.matrix_extra import matrix_digest
from hangar.records import dump_record, load_record
from hangar import research
from tests.hangar.test_briefing_server import good_council
from tests.hangar.test_records import base, decided

PROPOSAL = {
    "claim": "coolant and radiator 4.1 lb",
    "value": 4.1,
    "unit": "lb",
    "url": "https://example.org/open-ez-coolant-note.html",
    "title": "Example coolant sheet",
    "quote": "coolant and radiator 4.1 lb",
}


def _unknown(uid="coolant-weight", state="open", affects=None) -> dict:
    return {
        "id": uid,
        "text": "Coolant weight for the installation",
        "how": "maker manual",
        "affects": ["alt"] if affects is None else affects,
        "state": state,
    }


class Room:
    def __init__(self, tmp_path, record, lane=None, spot=None, registry=None, data_dir=None):
        self.root = tmp_path / "records"
        folder = self.root / "mod-ez" / "decisions"
        folder.mkdir(parents=True)
        self.file = folder / "demo.yaml"
        self.file.write_text(dump_record(record))
        self.site = tmp_path / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("ok")
        self.private = tmp_path / "private"
        self.private.mkdir()
        self.server = make_server(
            self.site, 0, self.private, self.root, council=good_council,
            research_lane=lane, spotcheck=spot, registry_path=registry, data_dir=data_dir,
        )
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def req(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, body=data, headers={
            "Content-Type": "application/json",
            "Host": f"127.0.0.1:{self.port}",
        })
        resp = conn.getresponse()
        raw = resp.read()
        headers = {k.lower(): v for k, v in resp.getheaders()}
        conn.close()
        if raw[:1] in (b"{", b"["):
            parsed = json.loads(raw)
        else:
            parsed = raw.decode()
        return resp.status, parsed, headers

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def _wait(pred, timeout=5.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.02)
    return False


def test_server_source_starts_research_only_from_the_post():
    text = Path("hangar/briefing_server.py").read_text()
    assert "Timer" not in text
    assert "schedule" not in text.lower()


def test_research_post_is_the_only_way_a_job_starts(tmp_path):
    """No timer and no other caller: before the POST there is no job. Deleting the POST's queue fails this."""
    calls = []

    def lane(brief):
        calls.append(brief)
        return dict(PROPOSAL)

    def spot(proposal):
        return {"matched": True, "quote_found": True, "value_found": True}

    record = base()
    record["unknowns"] = [_unknown()]
    room = Room(tmp_path, record, lane=lane, spot=spot)
    try:
        time.sleep(0.3)
        assert calls == []
        assert list(room.private.glob("research/*.json")) == []
        status, body, _ = room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "coolant-weight"})
        assert status == 202 and body["job"]["state"] == "queued"
        assert _wait(lambda: calls and research.load_job(room.private, body["job"]["id"])["state"] == "proposed")
        assert calls and "Coolant weight" in calls[0]
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "researching"
    finally:
        room.close()


def test_a_failed_job_returns_the_unknown_to_open(tmp_path):
    def lane(brief):
        raise RuntimeError("no public page")

    record = base()
    record["unknowns"] = [_unknown()]
    room = Room(tmp_path, record, lane=lane, spot=lambda p: {"matched": False})
    try:
        status, body, _ = room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "coolant-weight"})
        assert status == 202
        job_id = body["job"]["id"]

        def settled():
            job = research.load_job(room.private, job_id)
            state = yaml.safe_load(room.file.read_text())["unknowns"][0]["state"]
            return job["state"] == "failed" and state == "open"

        assert _wait(settled)
    finally:
        room.close()


def test_research_post_errors_and_already_queued_is_409(tmp_path):
    record = base()
    record["unknowns"] = [_unknown(state="sourced")]
    room = Room(tmp_path, record, lane=lambda b: dict(PROPOSAL), spot=lambda p: {"matched": True})
    try:
        before = room.file.read_bytes()
        assert room.req("POST", "/api/research", {"record_id": "missing", "unknown_id": "coolant-weight"})[0] == 404
        assert room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "no-such"})[0] == 400
        status, _, _ = room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "coolant-weight"})
        assert status == 400
        assert room.file.read_bytes() == before

        record["unknowns"] = [_unknown()]
        room.file.write_text(dump_record(record))
        research.queue_job(room.private, load_record(room.file), "coolant-weight")
        before = room.file.read_bytes()
        status, body, _ = room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "coolant-weight"})
        assert status == 409
        assert room.file.read_bytes() == before
        assert len(list(room.private.glob("research/*.json"))) == 1
        assert "already" in json.dumps(body).lower() or body.get("error")
    finally:
        room.close()


def test_research_index_is_no_store(tmp_path):
    record = base()
    record["unknowns"] = [_unknown()]
    room = Room(tmp_path, record, lane=lambda b: dict(PROPOSAL), spot=lambda p: {"matched": True})
    try:
        room.req("POST", "/api/research", {"record_id": "demo", "unknown_id": "coolant-weight"})
        status, body, headers = room.req("GET", "/api/research/demo")
        assert status == 200 and len(body["jobs"]) == 1
        assert headers.get("cache-control") == "no-store"
    finally:
        room.close()


def _plant_job(room: Room, job_id: str, matched: bool, patch=None) -> None:
    proposal = dict(PROPOSAL)
    if patch is not None:
        proposal["patch"] = patch
    job = {
        "id": job_id,
        "record_id": "demo",
        "unknown_id": "coolant-weight",
        "state": "proposed",
        "created": "2026-10-19T00:00:00+00:00",
        "brief": "public text",
        "proposal": proposal,
        "spotcheck": {"matched": matched, "quote_found": matched, "value_found": matched},
        "error": None,
        "note": None,
    }
    folder = room.private / "research"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{job_id}.json").write_text(json.dumps(job))


def test_resolve_accept_dismiss_and_unsourceable(tmp_path, monkeypatch):
    import core.sources as sources

    registry = tmp_path / "registry.yaml"
    registry.write_bytes(Path(sources.REGISTRY).read_bytes())
    real_registry = Path(sources.REGISTRY).read_bytes()
    original = sources.REGISTRY
    sources.REGISTRY = registry
    sources.load_registry.cache_clear()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "powerplants.yaml").write_text(yaml.safe_dump({
        "rotax-912is": {
            "installed_lb": {"v": 166.2, "flag": "derived", "note": "starter figure"},
            "cg_arm_in": {"v": 141.05, "flag": "derived", "note": "assumed"},
            "cruise_ff_gph": {"v": None, "flag": "unknown", "note": "cruise fuel flow"},
        }
    }))
    plants_before = (data_dir / "powerplants.yaml").read_bytes()

    record = base()
    record["unknowns"] = [_unknown(state="researching")]
    try:
        room = Room(
            tmp_path, record, lane=lambda b: dict(PROPOSAL), spot=lambda p: {"matched": True},
            registry=registry, data_dir=data_dir,
        )
        try:
            # a second decided record whose stored digest is already stale: accept must flag it
            stale = decided()
            stale["id"] = "stale-matrix"
            stale["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
            stale["options"][1]["effect"] = {"engine": "rotax-912is"}
            stale["decision"] = dict(stale["decision"], matrix_digest={"alt": "0" * 64}, over_unknowns=[])
            (room.file.parent / "stale.yaml").write_text(dump_record(stale))
            stale_decision = copy_decision(stale)

            _plant_job(room, "demo--coolant-weight--1", matched=False)
            before = room.file.read_bytes()
            reg_before = registry.read_bytes()
            status, body, _ = room.req("POST", "/api/research/resolve", {
                "job_id": "demo--coolant-weight--1", "outcome": "accept",
            })
            assert status == 409 and "match" in body["error"]
            assert room.file.read_bytes() == before
            assert registry.read_bytes() == reg_before
            assert json.loads((room.private / "research" / "demo--coolant-weight--1.json").read_text())["state"] == "proposed"

            _plant_job(room, "demo--coolant-weight--2", matched=True, patch={
                "file": "powerplants.yaml", "path": ["missing-engine", "cruise_ff_gph"], "value": 4.2,
            })
            status, body, _ = room.req("POST", "/api/research/resolve", {
                "job_id": "demo--coolant-weight--2", "outcome": "accept",
            })
            assert status == 409
            assert room.file.read_bytes() == before
            assert registry.read_bytes() == reg_before
            assert (data_dir / "powerplants.yaml").read_bytes() == plants_before
            assert json.loads((room.private / "research" / "demo--coolant-weight--2.json").read_text())["state"] == "proposed"

            _plant_job(room, "demo--coolant-weight--3", matched=True, patch={
                "file": "powerplants.yaml", "path": ["rotax-912is", "cruise_ff_gph"], "value": 4.2,
            })
            status, body, _ = room.req("POST", "/api/research/resolve", {
                "job_id": "demo--coolant-weight--3", "outcome": "accept",
            })
            assert status == 200 and body["ok"] is True
            assert body["job"]["state"] == "accepted"
            assert "stale-matrix" in body["reopened"]
            got = yaml.safe_load(room.file.read_text())
            assert got["unknowns"][0]["state"] == "sourced"
            sid = got["unknowns"][0]["source"]
            assert isinstance(sid, str) and sid
            reg = yaml.safe_load(registry.read_text())
            assert reg["sources"][sid]["obtain"] == PROPOSAL["url"]
            planted = yaml.safe_load((data_dir / "powerplants.yaml").read_text())
            assert planted["rotax-912is"]["cruise_ff_gph"]["v"] == 4.2
            assert planted["rotax-912is"]["cruise_ff_gph"]["flag"] == "sourced"
            assert planted["rotax-912is"]["cruise_ff_gph"]["cite"] == f"{sid}:p1"
            flagged = yaml.safe_load((room.file.parent / "stale.yaml").read_text())
            assert flagged["status"] == "decided"
            assert flagged["decision"]["matrix_digest"] == stale_decision["matrix_digest"]
            assert flagged["reopen_flag"]["reason"] == "the loading matrix changed after a sourced value"

            # dismiss and unsourceable on a fresh unknown, job still proposed
            record["unknowns"] = [_unknown(state="researching")]
            room.file.write_text(dump_record(record))
            _plant_job(room, "demo--coolant-weight--4", matched=True)
            status, body, _ = room.req("POST", "/api/research/resolve", {
                "job_id": "demo--coolant-weight--4", "outcome": "dismiss",
            })
            assert status == 200 and body["job"]["state"] == "dismissed" and body["reopened"] == []
            assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "open"

            record["unknowns"] = [_unknown(state="researching")]
            room.file.write_text(dump_record(record))
            _plant_job(room, "demo--coolant-weight--5", matched=True)
            status, body, _ = room.req("POST", "/api/research/resolve", {
                "job_id": "demo--coolant-weight--5", "outcome": "unsourceable",
            })
            assert status == 200 and body["job"]["state"] == "dismissed"
            assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "unsourceable"

            assert room.req("POST", "/api/research/resolve", {"job_id": "missing-job", "outcome": "dismiss"})[0] == 404
            assert room.req("POST", "/api/research/resolve", {"job_id": "demo--coolant-weight--5", "outcome": "maybe"})[0] == 400
        finally:
            room.close()
    finally:
        sources.REGISTRY = original
        sources.load_registry.cache_clear()
        assert Path("data/sources/registry.yaml").read_bytes() == real_registry


def copy_decision(rec: dict) -> dict:
    return json.loads(json.dumps(rec["decision"]))


def test_matrix_get_never_writes_private_weights(tmp_path):
    """Private labels show up in the response and never in the record file. Writing them back fails this."""
    record = base()
    record["options"][1]["effect"] = {"engine": "rotax-912is"}
    record["options"].append({
        "id": "bad",
        "label": "Bad effect",
        "kind": "candidate",
        "facts": [{"text": "a fact", "cite": "om-1980:p4"}],
        "why": "kept so a bad effect has somewhere to land",
        "effect": {"engine": "no-such-engine"},
    })
    record["unknowns"] = [_unknown()]
    room = Room(tmp_path, record, lane=lambda b: (_ for _ in ()).throw(AssertionError("lane")), spot=lambda p: None)
    try:
        (room.private / "mission.yaml").write_text(yaml.safe_dump({
            "pilots": [{"label": "Pat", "lb": 133.37}, {"label": "Sam", "lb": 187.91}],
            "bags_lb": 12,
        }))
        before = room.file.read_bytes()
        status, body, headers = room.req("GET", "/api/matrix/demo")
        assert status == 200
        assert headers.get("cache-control") == "no-store"
        assert body["record_id"] == "demo"
        by = {row["option"]: row for row in body["options"]}
        assert by["book"]["public"] is None and by["book"]["private"] is None and "error" not in by["book"]
        assert by["alt"]["public"]["unknown_cells"] == 0
        assert by["alt"]["public"]["crossings"]["fwd"]["note"]
        assert by["alt"]["private"]["crossings"] is None
        assert by["bad"]["public"] is None and by["bad"]["error"] == "bad effect"
        rendered = json.dumps(body)
        assert "Pat" in rendered and "Sam" in rendered
        assert room.file.read_bytes() == before
        text = room.file.read_text()
        for secret in ("Pat", "Sam", "133.37", "187.91"):
            assert secret not in text
        # the unknown carries no job until a POST, which this test never sends
        assert body["unknowns"][0]["id"] == "coolant-weight"
        assert body["unknowns"][0]["job"] is None
    finally:
        room.close()


def test_decide_409_when_unknown_cells_are_not_acknowledged(tmp_path):
    """ul350is cruise fuel flow is unknown, so the matrix is blank. Deleting the gate lets this decide."""
    plants = yaml.safe_load(Path("data/hangar/mod-ez/powerplants.yaml").read_text())
    assert plants["ul350is"]["cruise_ff_gph"]["flag"] == "unknown"
    assert matrix_for_effect({"engine": "ul350is"})["unknown_cells"] > 0

    record = base()
    record["scoring"] = {"kind": "loadings", "engines": ["ul350is"]}
    record["options"][1]["effect"] = {"engine": "ul350is"}
    record["unknowns"] = [
        _unknown("cruise-fuel-flow", "open"),
        _unknown("coolant-weight", "researching"),
        _unknown("arm-known", "sourced") | {"source": "om-1980"},
    ]
    # sourced unknown does not need a fresh acknowledgement
    room = Room(tmp_path, record)
    try:
        before = room.file.read_bytes()
        status, body, _ = room.req("POST", "/api/decide", {
            "record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter",
        })
        assert status == 409
        assert body["error"] == "unknown cells not acknowledged"
        assert body["unknowns"] == ["cruise-fuel-flow", "coolant-weight"]
        assert room.file.read_bytes() == before

        status, body, _ = room.req("POST", "/api/decide", {
            "record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter",
            "acknowledged_unknowns": ["cruise-fuel-flow"],
        })
        assert status == 409
        assert body["unknowns"] == ["coolant-weight"]
        assert room.file.read_bytes() == before

        status, body, _ = room.req("POST", "/api/decide", {
            "record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter",
            "acknowledged_unknowns": ["cruise-fuel-flow", "coolant-weight"],
        })
        assert status == 200
        got = yaml.safe_load(room.file.read_text())
        assert got["status"] == "decided"
        assert got["decision"]["over_unknowns"] == ["cruise-fuel-flow", "coolant-weight"]
        assert got["decision"]["matrix_digest"]["alt"] == matrix_digest({"engine": "ul350is"})
        assert "book" not in got["decision"]["matrix_digest"]
    finally:
        room.close()


def test_decide_without_unknown_cells_stores_digest_and_open_ids(tmp_path):
    record = base()
    record["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
    record["options"][1]["effect"] = {"engine": "rotax-912is"}
    record["unknowns"] = [
        _unknown("coolant-weight", "open"),
        _unknown("arm-known", "unsourceable"),
        {"text": "a legacy note", "how": "ask"},
    ]
    assert matrix_for_effect({"engine": "rotax-912is"})["unknown_cells"] == 0
    room = Room(tmp_path, record)
    try:
        status, _, _ = room.req("POST", "/api/decide", {
            "record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter",
        })
        assert status == 200
        got = yaml.safe_load(room.file.read_text())
        assert got["decision"]["over_unknowns"] == ["coolant-weight"]
        assert got["decision"]["matrix_digest"] == {"alt": matrix_digest({"engine": "rotax-912is"})}
    finally:
        room.close()


def test_decide_omits_over_unknowns_when_none_are_identified(tmp_path):
    record = base()
    record["unknowns"] = [{"text": "ethanol limit", "how": "ask"}]
    room = Room(tmp_path, record)
    try:
        assert room.req("POST", "/api/decide", {
            "record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter",
        })[0] == 200
        decision = yaml.safe_load(room.file.read_text())["decision"]
        assert "over_unknowns" not in decision and "matrix_digest" not in decision
    finally:
        room.close()


def test_reopen_clears_the_flag_and_records_api_emits_it(tmp_path):
    record = decided()
    record["reopen_flag"] = {
        "date": "2026-10-19",
        "reason": "the loading matrix changed after a sourced value",
        "unknowns": [],
        "digest_then": {"alt": "aa"},
        "digest_now": {"alt": "bb"},
    }
    room = Room(tmp_path, record)
    try:
        status, body, _ = room.req("GET", "/api/records")
        assert status == 200
        assert body["demo"]["reopen_flag"]["digest_then"] == {"alt": "aa"}
        decision = yaml.safe_load(room.file.read_text())["decision"]
        status, _, _ = room.req("POST", "/api/reopen", {"record_id": "demo", "reason": "new data"})
        assert status == 200
        got = yaml.safe_load(room.file.read_text())
        assert got["status"] == "reopened"
        assert "reopen_flag" not in got
        assert got["decision"] == decision
    finally:
        room.close()
