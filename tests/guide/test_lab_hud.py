"""The quality readout is on screen only with ?hud=1, and the test hook carries the same numbers."""

import functools
import http.server
import threading

import pytest
from playwright.sync_api import sync_playwright

from guide.build_site import build
from guide.export_glb import main as export_main
from tests.guide.render_fixture import ROOT

GL = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]


@pytest.fixture(scope="module")
def rsite(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("hud_site")
    export_main(["--out", str(tmp / "e" / "longez.glb")])
    out = tmp / "site"
    build(
        ROOT / "guide" / "graph",
        out,
        models=tmp / "e" / "longez.glb",
        scan_base=None,
        docs=None,
    )
    return out


def serve(root):
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(root)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


def _open(browser, url, query):
    page = browser.new_page(viewport={"width": 1180, "height": 820})
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.goto(url + query)
    page.wait_for_function("window.__lab && window.__lab.ready", timeout=90000)
    return page, errors


def test_quality_readout_appears_only_with_the_hud_flag(rsite):
    server, url = serve(rsite)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=GL)
            plain, plain_err = _open(browser, url, "?test=1&player=0&q=high")
            assert plain.locator("#lab-hud").count() == 0
            # the hook is there for tests; the screen is unchanged without the flag
            hook = plain.evaluate("window.__lab.quality()")
            assert hook["tier"] == "high" and hook["auto"] is False
            assert "text" in hook and plain.locator("#lab-hud").count() == 0
            assert not plain_err, plain_err

            logs = []
            page, errors = _open(browser, url, "?test=1&player=0&hud=1")
            page.on(
                "console",
                lambda msg: logs.append(msg.text) if msg.type == "info" else None,
            )
            panel = page.locator("#lab-hud")
            assert panel.count() == 1 and panel.is_visible()
            box = panel.bounding_box()
            assert box and box["width"] > 80 and box["height"] > 40
            font = float(
                page.evaluate(
                    "() => parseFloat(getComputedStyle(document.getElementById('lab-hud')).fontSize)"
                )
            )
            assert font >= 14, font
            clicks = page.evaluate(
                "() => getComputedStyle(document.getElementById('lab-hud')).pointerEvents"
            )
            assert clicks == "none"
            data = page.evaluate("window.__lab.quality()")
            shown = page.evaluate(
                "() => document.getElementById('lab-hud').textContent"
            )
            assert data["text"] == shown
            for key in (
                "tier",
                "auto",
                "resScale",
                "pixelRatio",
                "devicePixelRatio",
                "medianMs",
                "p75Ms",
                "tierSteps",
                "resSteps",
                "step",
                "log",
            ):
                assert key in data, key
            assert data["tier"] == "high" and data["auto"] is True
            assert (
                "High" in data["text"]
                and "auto" in data["text"]
                and "dpr" in data["text"]
            )
            # a run of slow frames steps the tier down and the log line shows up on the panel and the console
            page.evaluate(
                "() => { for (let i = 0; i < 80; i++) window.__lab.feedFrame(80) }"
            )
            data = page.evaluate("window.__lab.quality()")
            assert data["tier"] == "mid", data["tier"]
            assert data["tierSteps"] >= 1
            assert any(
                row["kind"] == "tier" and row["to"] == "mid" for row in data["log"]
            )
            shown = page.evaluate(
                "() => document.getElementById('lab-hud').textContent"
            )
            assert data["text"] == shown
            assert any(
                "lab quality tier" in line and "-> mid" in line for line in logs
            ), logs
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
