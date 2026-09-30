"""Lab engine: the page at /lab/ loads the canard, fills the viewport, and its op bar drives the step card and the camera."""
import functools
import json
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


def _open(p, url, w, h, init=None):
    b = p.chromium.launch(args=GL)
    ctx = b.new_context(viewport={"width": w, "height": h})
    if init:
        ctx.add_init_script(init)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url + "lab/?test=1&q=low")
    pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
    return b, pg, errors


def _graph(rsite):
    return json.loads((rsite / "graph.json").read_text())


def _bar_ops(g, variant):
    byid = {o["id"]: o for o in g["ops"]}
    return [i for i in g["order"] if variant in byid[i]["variants"] + (["roncz", "gu"] if "both" in byid[i]["variants"] else [])
            and byid[i]["chapter"] not in (0, 3, 6) and not byid[i]["stub"]]


@pytest.mark.parametrize("w,h", [(1400, 860), (390, 844)])
def test_canvas_is_full_bleed_and_page_does_not_scroll(rsite, w, h):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, w, h)
            r = pg.evaluate("(() => { const r = document.getElementById('gl').getBoundingClientRect(); return [r.left, r.top, r.width, r.height] })()")
            assert r == [0, 0, w, h], r
            assert pg.evaluate("document.documentElement.scrollWidth") <= w
            assert pg.evaluate("document.documentElement.scrollHeight") <= h
            if w == 390:  # the cards must leave the model room: a collapsed step card and >= 300 px between the top and bottom cards
                assert pg.get_attribute("#step", "data-open") == "false"
                gap = pg.evaluate("document.getElementById('step').getBoundingClientRect().top - document.getElementById('controls').getBoundingClientRect().bottom")
                assert gap >= 300, gap
                assert pg.evaluate("document.getElementById('opbar').getBoundingClientRect().bottom") <= h
                pg.click("#step-head")
                assert pg.get_attribute("#step", "data-open") == "true"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_op_chip_selects_step_and_flies_camera_to_its_shot(rsite):
    g = _graph(rsite)
    titles = {o["id"]: o["title"] for o in g["ops"]}
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860)
            assert pg.evaluate("window.__lab.shot('home') !== null")
            for op in ("r30.top-skin", "r30.bottom-skin", "r30.lift-tabs"):  # a top shot, an under-jig shot, and an op with no authored tour (goes home)
                pg.click(f'#opbar button[data-op="{op}"]')
                assert pg.text_content("#step-title") == titles[op]
                assert pg.evaluate("window.__lab.selected()") == op
                assert pg.evaluate("window.__lab.flying()") is True
                pg.evaluate("window.__lab.advance(3)")
                assert pg.evaluate("window.__lab.flying()") is False
                cam = pg.evaluate("window.__lab.camera()")
                shot = pg.evaluate(f"window.__lab.shot('{op}') || window.__lab.shot('home')")
                for k in ("pos", "target"):
                    assert max(abs(a - c) for a, c in zip(cam[k], shot[k])) < 1e-3, (op, k, cam[k], shot[k])
                assert abs(cam["fov"] - shot["fov"]) < 1e-3
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_variant_switch_changes_the_bar(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860)
            bar = lambda: pg.eval_on_selector_all("#opbar button[data-op]", "els => els.map(e => e.dataset.op)")
            assert bar() == _bar_ops(g, "roncz") and bar()
            pg.click('#variant button[data-variant="gu"]')
            assert bar() == _bar_ops(g, "gu") and bar()
            assert all(i.startswith("c1") for i in bar()), bar()
            assert pg.get_attribute('#variant button[data-variant="gu"]', "aria-pressed") == "true"
            assert pg.evaluate("window.__lab.selected()") == bar()[0]  # the old selection left the variant: first op of the new bar
            assert pg.text_content("#step-title")
            pg.click('#variant button[data-variant="roncz"]')
            assert bar() == _bar_ops(g, "roncz")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_checklist_survives_reload_and_works_without_storage(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860)
            box = "#checklist input[type=checkbox] >> nth=0"
            assert pg.locator("#checklist input[type=checkbox]").count() >= 1
            pg.check(box)
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.is_checked(box)
            b.close()
            throwing = "Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } })"
            b, pg, errors = _open(p, url, 1400, 860, init=throwing)
            pg.check(box)  # falls back to memory
            assert pg.is_checked(box)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_canard_is_inverted_in_the_jig_until_the_turnover_and_every_tour_op_has_a_lab_shot(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860)
            top = pg.evaluate("window.__lab.tableTopY()")
            shots = pg.evaluate("window.__lab.labShots()")
            assert set(shots) == set(g["tours"]), (set(shots) ^ set(g["tours"]))
            for op, t in g["tours"].items():
                assert shots[op]["target"] == t["target"], op  # the authored focus is kept; only the eye is re-authored
            pg.click('#opbar button[data-op="r30.bottom-skin"]')
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.flipping()") is False
            assert pg.evaluate("window.__lab.pose()") == "inverted"
            assert pg.evaluate("window.__lab.camera().pos[1]") > top  # the eye is above the table, looking down at the bottom surface
            pg.click('#opbar button[data-op="r30.top-skin"]')
            assert pg.evaluate("window.__lab.flipping()") is True  # the turnover is animated, and only step() drives it
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.flipping()") is False
            assert pg.evaluate("window.__lab.pose()") == "upright"
            assert pg.evaluate("window.__lab.camera().pos[1]") > top
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_every_ply_mesh_has_the_material_its_cloth_dictates_and_wet_is_a_uniform_change(rsite):
    g = _graph(rsite)
    nodes = g["layup"]["nodes"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 960, 600)
            names = pg.evaluate("window.__lab.meshNames()")
            assert pg.evaluate("window.__lab.material('canard.core').kind") == "foam"
            for node, n in nodes.items():
                m = pg.evaluate(f"window.__lab.material('{node}')")
                assert m["kind"] == n["cloth"].lower(), (node, m)  # und / bid
                assert m["wet"] == 0  # every ply starts cured
            assert set(nodes) <= set(names)
            first = next(iter(nodes))
            pg.evaluate(f"window.__lab.setWet('{first}', 1)")
            assert pg.evaluate(f"window.__lab.material('{first}').wet") == 1
            pg.evaluate("window.__lab.advance(0.1)")  # renders with the new uniform
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
