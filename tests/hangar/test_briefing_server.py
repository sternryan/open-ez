"""Briefing companion service (Hangar H2)."""

from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

from hangar import briefing_server
from hangar.briefing_server import make_server
from hangar.council import CouncilReply, CouncilUnavailable
from hangar.records import load_records, validate_all
from tests.hangar.test_records import base

REPO = Path(__file__).resolve().parents[2]


class Env:
    def __init__(self, tmp_path, council):
        self.root = tmp_path / "records"
        d = self.root / "mod-ez" / "decisions"
        d.mkdir(parents=True)
        self.file = d / "demo.yaml"
        self.file.write_text(yaml.safe_dump(base()))
        self.site = tmp_path / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("<h1>site</h1>")
        self.private = tmp_path / "private"
        self.council = council
        self.server = make_server(self.site, 0, self.private, self.root, council=council)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, method=method,
            headers={"content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(r, timeout=10) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw[:1] in (b"{", b"[") else raw.decode())
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, raw.decode()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def good_council(rec, message, history, **kw):
    return CouncilReply(
        positions=[{"role": "propulsion", "picks": {"engine": "alt"}, "confidence": "medium",
                    "reasoning": "lighter", "citations": ["om-1980:p4"], "judgment": False}],
        reply_text="here is my view", unknowns=["ethanol limit"],
    )


def error_council(rec, message, history, **kw):
    return CouncilReply(positions=[], reply_text="", unknowns=[], error="council reply was not valid JSON")


@pytest.fixture
def env(tmp_path):
    e = Env(tmp_path, good_council)
    yield e
    e.close()


def test_health_and_records(env):
    assert env.req("GET", "/api/health") == (200, {"ok": True})
    status, recs = env.req("GET", "/api/records")
    assert status == 200 and list(recs) == ["demo"] and recs["demo"]["status"] == "open"
    status, html = env.req("GET", "/")
    assert status == 200 and "<h1>site</h1>" in html


def test_binds_loopback_only(env):
    assert env.server.server_address[0] == "127.0.0.1"


def test_brief_writes_transcript_outside_repo_and_positions(env):
    status, out = env.req("POST", "/api/brief", {"record_id": "demo", "message": "talk me through it"})
    assert status == 200 and out["reply_text"] == "here is my view" and out["error"] is None
    t = env.private / "transcripts" / "demo.jsonl"
    lines = t.read_text().splitlines()
    assert len(lines) == 1 and "talk me through it" in lines[0]
    assert not (REPO / "transcripts").exists() and not list((REPO / "data").rglob("*.jsonl"))
    rec = yaml.safe_load(env.file.read_text())
    assert [p["role"] for p in rec["positions"]] == ["propulsion"]
    assert validate_all(env.root, REPO / "guide/graph") == []
    status, turns = env.req("GET", "/api/transcript/demo")
    assert status == 200 and len(turns) == 1


def test_council_error_no_record_change(env):
    env.server.council = error_council  # type: ignore[attr-defined]
    before = env.file.read_bytes()
    status, out = env.req("POST", "/api/brief", {"record_id": "demo", "message": "hi"})
    assert status == 200 and out["error"]
    assert env.file.read_bytes() == before
    assert len((env.private / "transcripts" / "demo.jsonl").read_text().splitlines()) == 1


def test_council_unavailable_is_503_no_change(tmp_path):
    def unavailable(rec, message, history, **kw):
        raise CouncilUnavailable("no env")

    e = Env(tmp_path, unavailable)
    try:
        before = e.file.read_bytes()
        status, out = e.req("POST", "/api/brief", {"record_id": "demo", "message": "hi"})
        assert status == 503 and out["error"]
        assert e.file.read_bytes() == before
    finally:
        e.close()


def test_brief_bad_input(env):
    assert env.req("POST", "/api/brief", {"record_id": "demo", "message": ""})[0] == 400
    assert env.req("POST", "/api/brief", {"record_id": "ghost", "message": "x"})[0] == 404


def test_decide_happy_path(env):
    status, out = env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "lighter"})
    assert status == 200
    rec = yaml.safe_load(env.file.read_text())
    assert rec["status"] == "decided"
    assert rec["decision"]["picks"]["engine"] == "alt" and rec["decision"]["reason"] == "lighter" and rec["decision"]["date"]
    assert [(h["from"], h["to"]) for h in rec["history"]] == [("open", "decided")]
    assert validate_all(env.root, REPO / "guide/graph") == []


def test_decide_unknown_option_400_file_unchanged(env):
    before = env.file.read_bytes()
    status, _ = env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "ghost"}, "reason": "x"})
    assert status == 400
    assert env.file.read_bytes() == before


def test_decide_empty_reason_400(env):
    before = env.file.read_bytes()
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": " "})[0] == 400
    assert env.file.read_bytes() == before


def test_decide_twice_400(env):
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "r"})[0] == 200
    before = env.file.read_bytes()
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "book"}, "reason": "r2"})[0] == 400
    assert env.file.read_bytes() == before


def test_reopen_then_decide(env):
    assert env.req("POST", "/api/reopen", {"record_id": "demo", "reason": "x"})[0] == 400  # still open
    env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "first"})
    assert env.req("POST", "/api/reopen", {"record_id": "demo", "reason": ""})[0] == 400
    assert env.req("POST", "/api/reopen", {"record_id": "demo", "reason": "new data"})[0] == 200
    assert yaml.safe_load(env.file.read_text())["status"] == "reopened"
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "book"}, "reason": "settled"})[0] == 200
    rec = yaml.safe_load(env.file.read_text())
    assert [(h["from"], h["to"]) for h in rec["history"]] == [
        ("open", "decided"), ("decided", "reopened"), ("reopened", "decided")]
    assert rec["decision"]["picks"]["engine"] == "book"
    assert validate_all(env.root, REPO / "guide/graph") == []


def test_invalid_record_after_change_is_409(env):
    d = base()
    d["replaces"] = ["f99.nope"]  # fails the graph gate already on disk
    env.file.write_text(yaml.safe_dump(d))
    before = env.file.read_bytes()
    status, _ = env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "r"})
    assert status == 409
    assert env.file.read_bytes() == before


def test_atomic_write(env, monkeypatch):
    before = env.file.read_bytes()
    names = sorted(os.listdir(env.file.parent))

    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    status, _ = env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "r"})
    assert status >= 500
    assert env.file.read_bytes() == before
    assert sorted(os.listdir(env.file.parent)) == names


def test_refuses_private_dir_in_repo(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    with pytest.raises(SystemExit) as ei:
        make_server(site, 0, REPO / "some-private-dir")
    assert ei.value.code == 2


def test_main_refuses_unset_private_env(tmp_path, monkeypatch):
    monkeypatch.delenv("HANGAR_PRIVATE_DIR", raising=False)
    with pytest.raises(SystemExit) as ei:
        briefing_server.main(["--site", str(tmp_path), "--port", "0"])
    assert ei.value.code == 2


def raw(env, method, path, body=b"", headers=None):
    import http.client

    c = http.client.HTTPConnection("127.0.0.1", env.port, timeout=10)
    c.request(method, path, body=body, headers=headers or {})
    r = c.getresponse()
    out = (r.status, r.read())
    c.close()
    return out


def test_post_requires_json_content_type(env):
    body = json.dumps({"record_id": "demo", "picks": {"engine": "alt"}, "reason": "r"}).encode()
    assert raw(env, "POST", "/api/decide", body, {"Content-Type": "text/plain"})[0] == 415
    assert yaml.safe_load(env.file.read_text())["status"] == "open"


def test_foreign_host_or_origin_is_refused(env):
    h = {"Content-Type": "application/json"}
    assert raw(env, "GET", "/api/records", headers={"Host": "evil.example"})[0] == 403
    assert raw(env, "POST", "/api/decide", b"{}", dict(h, Origin="http://evil.example"))[0] == 403
    assert raw(env, "GET", "/api/records", headers={"Host": f"localhost:{env.port}"})[0] == 200


def test_oversized_body_is_413(env):
    big = b"x" * 200_000
    assert raw(env, "POST", "/api/brief", big, {"Content-Type": "application/json"})[0] == 413


def test_unhashable_option_is_400_not_500(env):
    before = env.file.read_bytes()
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": []}, "reason": "r"})[0] == 400
    assert env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": {"a": 1}}, "reason": "r"})[0] == 400
    assert env.file.read_bytes() == before


def test_brief_does_not_touch_a_decided_record(env):
    env.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt"}, "reason": "r"})
    before = env.file.read_bytes()
    status, out = env.req("POST", "/api/brief", {"record_id": "demo", "message": "again"})
    assert status == 200 and env.file.read_bytes() == before


def test_directory_listing_is_404(env):
    (env.site / "sub").mkdir()
    assert raw(env, "GET", "/sub/")[0] == 404


def test_private_dir_inside_site_is_refused(tmp_path):
    site = tmp_path / "site"
    (site / "private").mkdir(parents=True)
    with pytest.raises(SystemExit) as ei:
        make_server(site, 0, site / "private")
    assert ei.value.code == 2


def test_decide_with_two_axes(tmp_path):
    from tests.hangar.test_axes import two_axes

    e = Env(tmp_path, good_council)
    try:
        e.file.write_text(yaml.safe_dump(two_axes()))
        before = e.file.read_bytes()
        for picks in ({"engine": "alt"}, {"engine": "alt", "fuel_path": "ghost"}, {"engine": "old", "fuel_path": "f1"},
                      {"engine": "alt", "fuel_path": "f1", "colour": "x"}, "alt", None):
            status, _ = e.req("POST", "/api/decide", {"record_id": "demo", "picks": picks, "reason": "r"})
            assert status == 400, picks
            assert e.file.read_bytes() == before
        assert e.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt", "fuel_path": "f2"}, "reason": " "})[0] == 400
        assert e.req("POST", "/api/decide", {"record_id": "demo", "option": "alt", "reason": "r"})[0] == 400  # old shape
        assert e.file.read_bytes() == before
        status, _ = e.req("POST", "/api/decide", {"record_id": "demo", "picks": {"engine": "alt", "fuel_path": "f2"}, "reason": "r"})
        assert status == 200
        rec = yaml.safe_load(e.file.read_text())
        assert rec["decision"]["picks"] == {"engine": "alt", "fuel_path": "f2"}
        assert rec["history"][-1]["picks"] == {"engine": "alt", "fuel_path": "f2"}
    finally:
        e.close()
