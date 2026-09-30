"""Lab engine skeleton: the page at /lab/ loads the canard and renders something other than a flat colour."""
import functools
import http.server
import io
import threading

import pytest
from playwright.sync_api import sync_playwright

from guide.build_site import build
from tests.guide.render_fixture import ROOT

GL = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]


@pytest.fixture(scope="module")
def rsite(tmp_path_factory):
    from guide.export_glb import main as export_main
    tmp = tmp_path_factory.mktemp("lab_site")
    export_main(["--out", str(tmp / "e" / "longez.glb")])
    out = tmp / "site"
    build(ROOT / "guide" / "graph", out, models=tmp / "e" / "longez.glb", scan_base=None, docs=None)
    return out


def serve(root):
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"


def test_lab_renders_the_canard_and_old_viewer_still_loads(rsite):
    from PIL import Image, ImageStat
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 960, "height": 600})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "lab/?test=1&q=low")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            names = pg.evaluate("window.__lab.meshNames()")
            assert "canard.core" in names
            assert any(n.startswith("canard.skin_top.p") for n in names), names[:10]
            pg.evaluate("window.__lab.advance(0.1)")
            img = Image.open(io.BytesIO(pg.locator("#gl").screenshot())).convert("L")
            var = ImageStat.Stat(img).var[0]
            assert var > 50, f"canvas looks flat (variance {var:.1f})"
            assert not errors, errors
            pg.goto(url)
            pg.wait_for_selector("#ops li[data-op]")
            b.close()
    finally:
        s.shutdown()
