"""The live briefing room end to end: real companion service, built public site, Chromium.

Covers the loading matrix and unknowns panels, the acknowledgement gate, the research -> accept chain and the reopen flag.
Research lane and spot-check are stubs (no network); everything else is the real code on real records."""

from __future__ import annotations

import json
import shutil
import time
import threading
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import sync_playwright

from guide.build_site import build
from hangar.briefing_server import make_server

ROOT = Path(__file__).resolve().parents[2]
GL = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
PILOTS = {"pilots": [{"label": "Pat", "lb": 133.37}, {"label": "Sam", "lb": 187.91}]}


def wait_until(cond, timeout=20.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return
        time.sleep(0.25)
    raise AssertionError("condition not met in time")


def lane(brief):
    assert "Pat" not in brief and "133.37" not in brief and "187.91" not in brief  # the lane only sees public text
    return {"claim": "installed CG arm 139.2 in", "value": 139.2, "unit": "in", "url": "https://example.org/engine-data.html",
            "title": "Example engine data", "quote": "installed CG arm 139.2 in",
            "patch": {"file": "powerplants.yaml", "path": ["rotax-912is", "cg_arm_in"], "value": 139.2, "note": "from the maker data"}}


def check(proposal):
    return {"method": "http fetch + text search (stub)", "fetched": True, "matched": True, "quote_found": True,
            "value_found": True, "detail": "stub"}


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("live_site") / "site"
    build(ROOT / "guide" / "graph", out, models=None, scan_base=None, docs=None, public=True)
    return out


@pytest.fixture()
def live(tmp_path, site, monkeypatch):
    records = tmp_path / "records"
    shutil.copytree(ROOT / "data" / "hangar", records)
    registry = tmp_path / "registry.yaml"
    shutil.copy(ROOT / "data" / "sources" / "registry.yaml", registry)
    priv = tmp_path / "private"
    priv.mkdir()
    (priv / "mission.yaml").write_text(yaml.safe_dump(PILOTS))
    import core.sources as core_sources

    monkeypatch.setattr(core_sources, "REGISTRY", registry)   # citations are validated against the registry the test writes to
    core_sources.load_registry.cache_clear()
    srv = make_server(site, 0, priv, records_root=records, council=lambda *a, **k: None, research_lane=lane,
                      spotcheck=check, registry_path=registry)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"

    def get(path):
        return json.loads(urllib.request.urlopen(base + path).read())

    try:
        yield {"base": base, "get": get, "records": records, "registry": registry, "priv": priv}
    finally:
        srv.shutdown()
        core_sources.load_registry.cache_clear()


def test_matrix_unknowns_research_and_reopen_flag(live):
    get, base = live["get"], live["base"]
    with sync_playwright() as p:
        b = p.chromium.launch(args=GL)
        pg = b.new_page(viewport={"width": 1100, "height": 900})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(base + "briefing.html#cg-ballast")
        # visible without opening any collapsed panel
        pg.wait_for_selector('[data-test="matrix"]', state="visible", timeout=20000)
        pg.wait_for_selector('[data-test="unknowns"]', state="visible", timeout=20000)
        text = pg.inner_text('[data-test="matrix"]')
        assert all(s in text.lower() for s in ("forward limit", "aft limit", "gross"))  # inner_text applies CSS case transforms
        assert "your loadings" in text.lower() and "Pat" in text   # private overlay, labels only
        assert "133.37" not in text and "187.91" not in text
        assert "not scored yet" in text.lower()                           # radiator-aft has no loading effect
        assert pg.locator('[data-test="matrix"] .out').count() > 0   # something is outside a limit and marked so
        assert pg.locator('[data-test="unknowns"] [data-action="research"]').count() >= 3

        # deciding without acknowledging the open unknowns is refused and writes nothing
        pg.select_option('select[name="pick-cg_fix"]', "loading-limit")
        pg.fill('textarea[name="reason"]', "smoke reason")
        assert pg.locator('input[name="ack-unknowns"]').count() == 1
        pg.click('form[data-test="decide"] button[type="submit"]')
        pg.wait_for_timeout(1500)
        assert get("api/records")["cg-ballast"]["status"] != "decided"

        # research -> proposed with a matched spot-check; accept stays disabled until then
        pg.click('[data-action="research"][data-unknown="installed-cg-arm"]')
        pg.wait_for_selector('[data-action="resolve"][data-outcome="accept"]', state="visible", timeout=20000)
        assert pg.locator('[data-action="resolve"][data-outcome="accept"]').is_enabled()

        # decide with the box ticked (unknowns still open): the decision records what it was taken over
        pg.select_option('select[name="pick-cg_fix"]', "loading-limit")
        pg.fill('textarea[name="reason"]', "smoke reason")
        pg.check('input[name="ack-unknowns"]')
        pg.click('form[data-test="decide"] button[type="submit"]')
        wait_until(lambda: get("api/records")["cg-ballast"]["status"] == "decided")
        rec = get("api/records")["cg-ballast"]
        assert rec["decision"]["picks"] == {"cg_fix": "loading-limit"}
        assert "installed-cg-arm" in rec["decision"]["over_unknowns"]
        assert set(rec["decision"]["matrix_digest"]) >= {"loading-limit", "battery-aft"}

        # accept the research: source registered, value patched, unknown sourced, decision flagged for reopen, never edited
        pg.reload()
        pg.wait_for_selector('[data-action="resolve"][data-outcome="accept"]', state="visible", timeout=20000)
        pg.click('[data-action="resolve"][data-outcome="accept"]')
        wait_until(lambda: any(u.get("id") == "installed-cg-arm" and u.get("state") == "sourced"
                               for u in get("api/records")["cg-ballast"]["unknowns"]))
        rec = get("api/records")["cg-ballast"]
        assert rec["status"] == "decided" and rec["decision"]["picks"] == {"cg_fix": "loading-limit"}
        assert rec["reopen_flag"] and "installed-cg-arm" in rec["reopen_flag"]["unknowns"]
        cg = yaml.safe_load((live["records"] / "mod-ez" / "powerplants.yaml").read_text())["rotax-912is"]["cg_arm_in"]
        assert cg["v"] == 139.2 and cg["flag"] == "sourced" and cg["cite"].endswith(":p1")
        assert "example-engine-data" in live["registry"].read_text()
        pg.reload()
        pg.wait_for_selector('[data-test="reopen-flag"]', state="visible", timeout=20000)
        assert not errors, errors
        b.close()
    for f in live["records"].rglob("*.yaml"):                        # no owner weight reached a record
        t = f.read_text()
        assert "133.37" not in t and "187.91" not in t
    assert all("133.37" not in j.read_text() for j in (live["priv"] / "research").glob("*.json"))
