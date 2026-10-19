"""Research recovery, accept rollback, and the jobs that must not stick."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from hangar import research
from hangar.briefing_server import _research_worker, make_server
from hangar.matrix_extra import matrix_text
from hangar.matrix import matrix_for_effect
from hangar.records import dump_record
from tests.hangar.test_briefing_server import good_council
from tests.hangar.test_matrix_server import PROPOSAL, Room, _unknown, _wait
from tests.hangar.test_records import base, decided

_ACCEPT_FAILED = "accept failed"


def _write_job(private: Path, job: dict) -> None:
    folder = private / "research"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{job['id']}.json").write_text(json.dumps(job))


def _job(job_id: str, state: str, unknown_id: str = "coolant-weight", patch=None, record_id: str = "demo") -> dict:
    proposal = dict(PROPOSAL)
    if patch is not None:
        proposal["patch"] = patch
    return {
        "id": job_id,
        "record_id": record_id,
        "unknown_id": unknown_id,
        "state": state,
        "created": "2026-10-19T00:00:00+00:00",
        "brief": "public text",
        "proposal": proposal,
        "spotcheck": {"matched": True, "quote_found": True, "value_found": True},
        "error": None,
        "note": None,
    }


def test_abandon_job_fails_inflight_work_and_leaves_finished_jobs(tmp_path):
    private = tmp_path / "private"
    queued = _job("demo--coolant-weight--1", "queued")
    proposed = _job("demo--coolant-weight--2", "proposed")
    _write_job(private, queued)
    _write_job(private, proposed)
    proposed_bytes = (private / "research" / "demo--coolant-weight--2.json").read_bytes()
    failed = research.abandon_job(str(private), queued["id"], "server restarted")
    assert failed["state"] == "failed" and failed["error"] == "server restarted"
    again = research.abandon_job(str(private), queued["id"], "other")
    assert again["state"] == "failed" and again["error"] == "server restarted"
    untouched = research.abandon_job(str(private), proposed["id"], "server restarted")
    assert untouched["state"] == "proposed"
    assert (private / "research" / "demo--coolant-weight--2.json").read_bytes() == proposed_bytes


def test_server_start_abandons_inflight_jobs_and_skips_a_bad_record(tmp_path, monkeypatch):
    """Queued and running jobs die at startup. One bad record does not stop the good one."""
    import hangar.briefing_server as briefing_server

    root = tmp_path / "records"
    folder = root / "mod-ez" / "decisions"
    folder.mkdir(parents=True)
    good = base()
    good["unknowns"] = [
        _unknown("queued-item", "researching"),
        _unknown("running-item", "researching"),
        _unknown("proposed-item", "researching"),
        _unknown("sourced-item", "sourced") | {"source": "om-1980"},
    ]
    good_path = folder / "demo.yaml"
    good_path.write_text(dump_record(good))
    bad = base()
    bad["id"] = "bad-rec"
    bad["status"] = "decided"
    bad["unknowns"] = [_unknown("stuck", "researching")]
    bad_path = folder / "bad.yaml"
    bad_text = dump_record(bad)
    bad_path.write_text(bad_text)
    private = tmp_path / "private"
    private.mkdir()
    _write_job(private, _job("demo--queued-item--1", "queued", "queued-item"))
    _write_job(private, _job("demo--running-item--1", "running", "running-item"))
    _write_job(private, _job("demo--proposed-item--1", "proposed", "proposed-item"))
    _write_job(private, _job("bad-rec--stuck--1", "queued", "stuck", record_id="bad-rec"))
    proposed_bytes = (private / "research" / "demo--proposed-item--1.json").read_bytes()
    writes: list[str] = []
    real_write = briefing_server._atomic_write

    def counting(path, data, graph, records_root):
        writes.append(Path(path).name)
        return real_write(path, data, graph, records_root)

    monkeypatch.setattr(briefing_server, "_atomic_write", counting)
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("ok")
    server = make_server(
        site, 0, private, root, council=good_council,
        research_lane=lambda brief: (_ for _ in ()).throw(AssertionError("lane")),
        spotcheck=lambda proposal: {"matched": False},
    )
    try:
        states = {row["id"]: row["state"] for row in yaml.safe_load(good_path.read_text())["unknowns"]}
        assert states == {
            "queued-item": "open",
            "running-item": "open",
            "proposed-item": "researching",
            "sourced-item": "sourced",
        }
        queued = json.loads((private / "research" / "demo--queued-item--1.json").read_text())
        running = json.loads((private / "research" / "demo--running-item--1.json").read_text())
        assert queued["state"] == "failed" and queued["error"] == "server restarted"
        assert running["state"] == "failed" and running["error"] == "server restarted"
        assert (private / "research" / "demo--proposed-item--1.json").read_bytes() == proposed_bytes
        assert bad_path.read_text() == bad_text
        stuck = json.loads((private / "research" / "bad-rec--stuck--1.json").read_text())
        assert stuck["state"] == "failed" and stuck["error"] == "server restarted"
        assert writes.count("demo.yaml") == 1
        assert writes.count("bad.yaml") == 1
    finally:
        server.server_close()


def test_worker_exception_abandons_the_job_and_reopens_the_unknown(tmp_path, monkeypatch):
    record = base()
    record["unknowns"] = [_unknown(state="researching")]
    room = Room(
        tmp_path, record,
        lane=lambda brief: (_ for _ in ()).throw(AssertionError("lane")),
        spot=lambda proposal: {"matched": False},
    )
    try:
        job_id = "demo--coolant-weight--1"
        _write_job(room.private, _job(job_id, "queued"))

        def boom(*_args, **_kwargs):
            raise RuntimeError("blew up")

        monkeypatch.setattr(research, "run_job", boom)
        _research_worker(room.server, room.file, "coolant-weight", job_id)
        job = research.load_job(str(room.private), job_id)
        assert job["state"] == "failed"
        assert job["error"] == "research worker failed"
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "open"
    finally:
        room.close()


def test_worker_record_write_failure_still_reopens_the_unknown(tmp_path, monkeypatch):
    import hangar.briefing_server as briefing_server

    record = base()
    record["unknowns"] = [_unknown()]
    real_write = briefing_server._atomic_write
    calls = {"n": 0}

    def flaky(path, data, graph, records_root):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("disk full")
        return real_write(path, data, graph, records_root)

    monkeypatch.setattr(briefing_server, "_atomic_write", flaky)

    def lane(_brief):
        raise RuntimeError("no public page")

    room = Room(tmp_path, record, lane=lane, spot=lambda proposal: {"matched": False})
    try:
        status, body, _ = room.req("POST", "/api/research", {
            "record_id": "demo", "unknown_id": "coolant-weight",
        })
        assert status == 202
        job_id = body["job"]["id"]

        def settled():
            job = research.load_job(str(room.private), job_id)
            state = yaml.safe_load(room.file.read_text())["unknowns"][0]["state"]
            return job["state"] == "failed" and state == "open"

        assert _wait(settled)
        assert calls["n"] >= 3
    finally:
        room.close()


def test_research_post_keeps_no_job_when_the_record_write_fails(tmp_path, monkeypatch):
    import hangar.briefing_server as briefing_server

    record = base()
    record["unknowns"] = [_unknown()]
    real_write = briefing_server._atomic_write
    calls = {"n": 0}

    def flaky(path, data, graph, records_root):
        calls["n"] += 1
        if calls["n"] == 1:
            return ["forced failure"]
        return real_write(path, data, graph, records_root)

    monkeypatch.setattr(briefing_server, "_atomic_write", flaky)
    room = Room(
        tmp_path, record,
        lane=lambda brief: dict(PROPOSAL),
        spot=lambda proposal: {"matched": True},
    )
    try:
        before = room.file.read_bytes()
        status, _body, _ = room.req("POST", "/api/research", {
            "record_id": "demo", "unknown_id": "coolant-weight",
        })
        assert status == 409
        assert list(room.private.glob("research/*.json")) == []
        assert room.file.read_bytes() == before
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "open"

        status, body, _ = room.req("POST", "/api/research", {
            "record_id": "demo", "unknown_id": "coolant-weight",
        })
        assert status == 202 and body["job"]["state"] == "queued"
        assert (room.private / "research" / f"{body['job']['id']}.json").is_file()
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "researching"
    finally:
        room.close()


def test_dismiss_and_unsourceable_are_allowed_on_a_failed_job(tmp_path):
    record = base()
    record["unknowns"] = [_unknown(state="researching")]
    room = Room(
        tmp_path, record,
        lane=lambda brief: dict(PROPOSAL),
        spot=lambda proposal: {"matched": True},
    )
    try:
        job_id = "demo--coolant-weight--1"
        _write_job(room.private, _job(job_id, "failed"))
        before = room.file.read_bytes()
        job_before = (room.private / "research" / f"{job_id}.json").read_bytes()
        status, body, _ = room.req("POST", "/api/research/resolve", {"job_id": job_id, "outcome": "accept"})
        assert status == 409
        assert room.file.read_bytes() == before
        assert (room.private / "research" / f"{job_id}.json").read_bytes() == job_before

        status, body, _ = room.req("POST", "/api/research/resolve", {"job_id": job_id, "outcome": "dismiss"})
        assert status == 200 and body["job"]["state"] == "dismissed"
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "open"

        record["unknowns"] = [_unknown(state="researching")]
        room.file.write_text(dump_record(record))
        other = "demo--coolant-weight--2"
        _write_job(room.private, _job(other, "failed"))
        status, body, _ = room.req("POST", "/api/research/resolve", {"job_id": other, "outcome": "unsourceable"})
        assert status == 200 and body["job"]["state"] == "dismissed"
        assert yaml.safe_load(room.file.read_text())["unknowns"][0]["state"] == "unsourceable"
    finally:
        room.close()


@pytest.mark.parametrize("state", ["dismissed", "accepted", "queued"])
def test_accept_of_a_job_that_is_not_proposed_changes_nothing(tmp_path, state):
    record = base()
    record["unknowns"] = [_unknown(state="researching")]
    room = Room(
        tmp_path, record,
        lane=lambda brief: dict(PROPOSAL),
        spot=lambda proposal: {"matched": True},
    )
    try:
        job_id = "demo--coolant-weight--1"
        _write_job(room.private, _job(job_id, state))
        before = room.file.read_bytes()
        job_before = (room.private / "research" / f"{job_id}.json").read_bytes()
        status, _body, _ = room.req("POST", "/api/research/resolve", {"job_id": job_id, "outcome": "accept"})
        assert status == 409
        assert room.file.read_bytes() == before
        assert (room.private / "research" / f"{job_id}.json").read_bytes() == job_before
        assert json.loads(job_before)["state"] == state
    finally:
        room.close()


def _registry(tmp_path: Path):
    import core.sources as sources

    registry = tmp_path / "registry.yaml"
    registry.write_bytes(Path(sources.REGISTRY).read_bytes())
    return sources, registry, Path(sources.REGISTRY).read_bytes(), sources.REGISTRY


def _plants(tmp_path: Path) -> Path:
    data_dir = tmp_path / "plants"
    data_dir.mkdir()
    src = Path("data/hangar/mod-ez")
    for name in ("powerplants.yaml", "mission.yaml", "loadings.yaml"):
        shutil.copy(src / name, data_dir / name)
    return data_dir


def test_accept_refreshes_the_matrix_fact_after_a_cg_patch(tmp_path, monkeypatch):
    import hangar.mission as mission_mod

    sources, registry, real_registry, original = _registry(tmp_path)
    data_dir = _plants(tmp_path)
    monkeypatch.setattr(mission_mod, "_DATA", data_dir)
    effect = {"engine": "rotax-912is"}
    before_text = matrix_text(matrix_for_effect(effect))
    record = base()
    record["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
    record["options"][1]["effect"] = effect
    record["options"][1]["facts"] = [{"text": before_text, "flag": "derived", "computed": "matrix"}]
    record["unknowns"] = [_unknown(state="researching")]
    sources.REGISTRY = registry
    sources.load_registry.cache_clear()
    try:
        room = Room(
            tmp_path, record,
            lane=lambda brief: dict(PROPOSAL),
            spot=lambda proposal: {"matched": True},
            registry=registry, data_dir=data_dir,
        )
        try:
            patch = {"file": "powerplants.yaml", "path": ["rotax-912is", "cg_arm_in"], "value": 80.0}
            job_id = "demo--coolant-weight--1"
            _write_job(room.private, _job(job_id, "proposed", patch=patch))
            status, body, _ = room.req("POST", "/api/research/resolve", {"job_id": job_id, "outcome": "accept"})
            assert status == 200 and body["ok"] is True
            got = yaml.safe_load(room.file.read_text())
            fact = next(item for item in got["options"][1]["facts"] if item.get("computed") == "matrix")
            after_text = matrix_text(matrix_for_effect(effect))
            assert fact["text"] == after_text
            assert fact["text"] != before_text
            assert got["unknowns"][0]["state"] == "sourced"
            planted = yaml.safe_load((data_dir / "powerplants.yaml").read_text())
            assert planted["rotax-912is"]["cg_arm_in"]["v"] == 80.0
        finally:
            room.close()
    finally:
        sources.REGISTRY = original
        sources.load_registry.cache_clear()
        assert Path("data/sources/registry.yaml").read_bytes() == real_registry


@pytest.mark.parametrize("step", ["register", "patch", "record", "finish", "scores", "reopen"])
def test_accept_rolls_back_when_a_step_fails(tmp_path, monkeypatch, step):
    import hangar.briefing_server as briefing_server
    import hangar.mission as mission_mod
    import hangar.reopen as reopen_mod

    sources, registry, real_registry, original = _registry(tmp_path)
    data_dir = _plants(tmp_path)
    record = base()
    record["unknowns"] = [_unknown(state="researching")]
    sources.REGISTRY = registry
    sources.load_registry.cache_clear()
    try:
        room = Room(
            tmp_path, record,
            lane=lambda brief: dict(PROPOSAL),
            spot=lambda proposal: {"matched": True},
            registry=registry, data_dir=data_dir,
        )
        try:
            stale = decided()
            stale["id"] = "stale-matrix"
            stale["scoring"] = {"kind": "loadings", "engines": ["rotax-912is"]}
            stale["options"][1]["effect"] = {"engine": "rotax-912is"}
            stale["decision"] = dict(stale["decision"], matrix_digest={"alt": "0" * 64}, over_unknowns=[])
            stale_path = room.file.parent / "stale.yaml"
            stale_path.write_text(dump_record(stale))
            patch = {"file": "powerplants.yaml", "path": ["rotax-912is", "cg_arm_in"], "value": 80.0}
            job_id = "demo--coolant-weight--1"
            _write_job(room.private, _job(job_id, "proposed", patch=patch))
            before = {
                "record": room.file.read_bytes(),
                "stale": stale_path.read_bytes(),
                "registry": registry.read_bytes(),
                "plants": (data_dir / "powerplants.yaml").read_bytes(),
                "job": (room.private / "research" / f"{job_id}.json").read_bytes(),
            }
            calls = {"register": 0}
            real_register = briefing_server.register_source
            real_patch = briefing_server.apply_patch
            real_write = briefing_server._atomic_write
            real_finish = research.finish_job
            real_scores = mission_mod.write_scores
            real_reopen = briefing_server.flag_reopen

            def register(*args, **kwargs):
                calls["register"] += 1
                result = real_register(*args, **kwargs)
                if step == "register" and calls["register"] >= 2:
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            def patch_fn(*args, **kwargs):
                result = real_patch(*args, **kwargs)
                if step == "patch":
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            def write_fn(*args, **kwargs):
                result = real_write(*args, **kwargs)
                if step == "record":
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            def finish(*args, **kwargs):
                result = real_finish(*args, **kwargs)
                if step == "finish":
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            def scores(*args, **kwargs):
                result = real_scores(*args, **kwargs)
                if step == "scores":
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            def reopen(*args, **kwargs):
                result = real_reopen(*args, **kwargs)
                if step == "reopen":
                    raise OSError("No such file or directory: '/tmp/accept-step'")
                return result

            monkeypatch.setattr(briefing_server, "register_source", register)
            monkeypatch.setattr(briefing_server, "apply_patch", patch_fn)
            monkeypatch.setattr(briefing_server, "_atomic_write", write_fn)
            monkeypatch.setattr(research, "finish_job", finish)
            monkeypatch.setattr(mission_mod, "write_scores", scores)
            monkeypatch.setattr(briefing_server, "flag_reopen", reopen)
            monkeypatch.setattr(reopen_mod, "flag_reopen", reopen)
            status, body, _ = room.req("POST", "/api/research/resolve", {"job_id": job_id, "outcome": "accept"})
            rendered = json.dumps(body)
            assert status == 409
            assert body["error"] == _ACCEPT_FAILED
            assert "/tmp" not in rendered
            assert "No such file" not in rendered
            assert room.file.read_bytes() == before["record"]
            assert stale_path.read_bytes() == before["stale"]
            assert registry.read_bytes() == before["registry"]
            assert (data_dir / "powerplants.yaml").read_bytes() == before["plants"]
            assert (room.private / "research" / f"{job_id}.json").read_bytes() == before["job"]
        finally:
            room.close()
    finally:
        sources.REGISTRY = original
        sources.load_registry.cache_clear()
        assert Path("data/sources/registry.yaml").read_bytes() == real_registry
