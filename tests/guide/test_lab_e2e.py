"""Lab engine: the page at / loads the canard, fills the viewport, and its op bar drives the step card and the camera."""

import contextlib
import functools
import json
import sys
import http.server
import io
import threading
import time
import types

import pytest
from playwright.sync_api import sync_playwright as _real_sync_playwright

from guide.build_site import build
from tests.guide.render_fixture import ROOT
from tests.guide.test_schema import gdir as _schema_gdir

_graph_dir = pytest.fixture(name="gdir")(_schema_gdir.__wrapped__)

GL = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]

# One chromium for the whole module (launching one per test was most of the suite's wall time). Each test still gets its own
# context and page: `sync_playwright()` below hands a test a per-test view of the shared browser, and closing that view closes
# only the contexts the test opened. All tests (including those that set device_scale_factor or init scripts) use the shim, so all run on both engines.
_SHARED = {}


class _View:
    def __init__(self, browser):
        self._b, self._ctxs = browser, []

    def new_context(self, **kw):
        c = self._b.new_context(**kw)
        self._ctxs.append(c)
        return c

    def new_page(self, **kw):
        return self.new_context(**kw).new_page()

    @property
    def contexts(self):
        return list(self._ctxs)

    def close(self):
        for c in self._ctxs:
            c.close()
        self._ctxs.clear()


# Every test in this module runs on both engines: the owner's iPad Chrome is WebKit underneath. Chromium keeps its software-GL
# args; WebKit takes no GL args (it uses the platform's GL) and only runs on macOS. Tests launch through the shim below, which
# ignores their `args` and hands back the engine under test, so no test needs to know which engine it is on.
@pytest.fixture(scope="module", autouse=True, params=["chromium", "webkit"])
def _one_browser(request):
    engine = request.param
    if engine == "webkit" and sys.platform != "darwin":
        pytest.skip(
            "webkit runs on macOS only (the iPad engine; Linux WebKit is not the shipping build)"
        )
    pw = _real_sync_playwright().start()
    try:
        if engine == "webkit":
            import os

            if not os.path.exists(pw.webkit.executable_path):
                pytest.skip(
                    "webkit executable missing (run: python -m playwright install webkit)"
                )
            _SHARED["b"] = pw.webkit.launch()
        else:
            _SHARED["b"] = pw.chromium.launch(args=GL)
        _SHARED["engine"] = engine
        yield engine
    finally:
        b = _SHARED.pop("b", None)
        if b:
            b.close()
        pw.stop()


@contextlib.contextmanager
def sync_playwright():
    """Stands in for playwright's: `p.chromium.launch(args=GL)` returns a view of the module's one browser."""
    yield types.SimpleNamespace(
        chromium=types.SimpleNamespace(
            launch=lambda args=None, **kw: _View(_SHARED["b"])
        )
    )


@pytest.fixture(scope="module")
def rsite(tmp_path_factory):
    from guide.export_glb import main as export_main

    tmp = tmp_path_factory.mktemp("lab_site")
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
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"


def test_lab_renders_the_canard_and_the_classic_viewer_still_loads(rsite):
    from PIL import Image, ImageStat

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 960, "height": 600})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            names = pg.evaluate("window.__lab.meshNames()")
            assert "canard.core" in names
            assert any(n.startswith("canard.skin_top.p") for n in names), names[:10]
            pg.evaluate("window.__lab.advance(0.1)")
            img = Image.open(io.BytesIO(pg.locator("#gl").screenshot())).convert("L")
            var = ImageStat.Stat(img).var[0]
            assert var > 50, f"canvas looks flat (variance {var:.1f})"
            assert not errors, errors
            pg.goto(url + "classic/")
            pg.wait_for_selector("#ops li[data-op]")
            b.close()
    finally:
        s.shutdown()


def _open(p, url, w, h, init=None, query="", q="low"):
    b = p.chromium.launch(args=GL)
    ctx = b.new_context(viewport={"width": w, "height": h})
    if init:
        ctx.add_init_script(init)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url + "?test=1" + (f"&q={q}" if q else "") + query)
    pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
    return b, pg, errors


def _graph(rsite):
    return json.loads((rsite / "graph.json").read_text())


def _display(pg):
    """Open the display popover (part names, load paths, future work, quality) if it is closed."""
    if pg.get_attribute("#more", "aria-expanded") != "true":
        pg.click("#more")
    assert pg.is_visible("#viewpop")


def _unfold_checklist(pg):
    """Wide screens fold the checklist behind its heading when the step card would cover too much of the frame."""
    if pg.get_attribute("#step", "data-open") != "true":
        pg.click("#step-head")
    if pg.get_attribute("#step", "data-list") == "closed":
        pg.click("#checklist-h")


def _bar_ops(g, variant):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if variant
        in byid[i]["variants"]
        + (["roncz", "gu"] if "both" in byid[i]["variants"] else [])
        and byid[i]["chapter"]
        not in (0, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18)
        and not byid[i]["stub"]
    ]


@pytest.mark.parametrize("w,h", [(1400, 860), (390, 844)])
def test_canvas_is_full_bleed_and_page_does_not_scroll(rsite, w, h):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, w, h)
            r = pg.evaluate(
                "(() => { const r = document.getElementById('gl').getBoundingClientRect(); return [r.left, r.top, r.width, r.height] })()"
            )
            assert r == [0, 0, w, h], r
            assert pg.evaluate("document.documentElement.scrollWidth") <= w
            assert pg.evaluate("document.documentElement.scrollHeight") <= h
            if (
                w == 390
            ):  # the cards must leave the model room: a collapsed step card and >= 300 px between the top and bottom cards
                assert pg.get_attribute("#step", "data-open") == "false"
                gap = pg.evaluate(
                    "document.getElementById('dock').getBoundingClientRect().top - document.getElementById('controls').getBoundingClientRect().bottom"
                )
                assert (
                    gap >= 300
                ), gap  # the dock is the readout line over the step card
                assert (
                    pg.evaluate(
                        "document.getElementById('readout').getBoundingClientRect().height"
                    )
                    <= 44
                )  # one compact line
                assert (
                    pg.evaluate(
                        "document.getElementById('opbar').getBoundingClientRect().bottom"
                    )
                    <= h
                )
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
            for op in (
                "r30.top-skin",
                "r30.bottom-skin",
                "r30.lift-tabs",
            ):  # a top shot, an under-jig shot, and an op with no authored tour (goes home)
                pg.click(f'#opbar button[data-op="{op}"]')
                assert pg.text_content("#step-title") == titles[op]
                assert pg.evaluate("window.__lab.selected()") == op
                assert pg.evaluate("window.__lab.flying()") is True
                pg.evaluate("window.__lab.advance(3)")
                assert pg.evaluate("window.__lab.flying()") is False
                cam = pg.evaluate("window.__lab.camera()")
                shot = pg.evaluate(
                    f"window.__lab.shot('{op}') || window.__lab.shot('home')"
                )
                for k in ("pos", "target"):
                    assert max(abs(a - c) for a, c in zip(cam[k], shot[k])) < 1e-3, (
                        op,
                        k,
                        cam[k],
                        shot[k],
                    )
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

            def bar():
                return pg.eval_on_selector_all(
                    "#opbar button[data-op]", "els => els.map(e => e.dataset.op)"
                )

            assert bar() == _bar_ops(g, "roncz") and bar()
            pg.click('#variant button[data-variant="gu"]')
            assert bar() == _bar_ops(g, "gu") and bar()
            assert all(i.startswith("c1") for i in bar()), bar()
            assert (
                pg.get_attribute('#variant button[data-variant="gu"]', "aria-pressed")
                == "true"
            )
            assert (
                pg.evaluate("window.__lab.selected()") == bar()[0]
            )  # the old selection left the variant: first op of the new bar
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
            _unfold_checklist(pg)
            pg.check(box)
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.is_checked(box)
            b.close()
            throwing = "Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } })"
            b, pg, errors = _open(p, url, 1400, 860, init=throwing)
            _unfold_checklist(pg)
            pg.check(box)  # falls back to memory
            assert pg.is_checked(box)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_canard_is_inverted_in_the_jig_until_the_turnover_and_every_tour_op_has_a_lab_shot(
    rsite,
):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860)
            top = pg.evaluate("window.__lab.tableTopY()")
            shots = pg.evaluate("window.__lab.labShots()")
            assert set(shots) == set(g["tours"]), set(shots) ^ set(g["tours"])
            for op, t in g["tours"].items():
                assert (
                    shots[op]["target"] == t["target"]
                ), op  # the authored focus is kept; only the eye is re-authored
            pg.click('#opbar button[data-op="r30.bottom-skin"]')
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.flipping()") is False
            assert pg.evaluate("window.__lab.pose()") == "inverted"
            assert (
                pg.evaluate("window.__lab.camera().pos[1]") > top
            )  # the eye is above the table, looking down at the bottom surface
            pg.click('#opbar button[data-op="r30.top-skin"]')
            assert (
                pg.evaluate("window.__lab.flipping()") is True
            )  # the turnover is animated, and only step() drives it
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.flipping()") is False
            assert pg.evaluate("window.__lab.pose()") == "upright"
            assert pg.evaluate("window.__lab.camera().pos[1]") > top
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_every_ply_mesh_has_the_material_its_cloth_dictates_and_wet_is_a_uniform_change(
    rsite,
):
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


def _expected_state(g, variant, cur, lay, ghost):
    """Independent restatement of the build rule, from graph.json alone: earlier ops built, the current op's laid plies (and its
    whole-part meshes) current, everything later hidden, or ghost when the toggle is on."""
    byid = {o["id"]: o for o in g["ops"]}
    order = [
        i
        for i in g["order"]
        if variant in byid[i]["variants"] or "both" in byid[i]["variants"]
    ]
    idx = {o: i for i, o in enumerate(order)}
    first = {}
    for o in order:
        for c in byid[o]["components"]:
            first.setdefault(c, o)
    later = "ghost" if ghost else "hidden"
    out = {}
    for comp, plies in g["plies"].items():
        for r in plies:
            i = idx.get(r["op"])
            out[r["node"]] = (
                "hidden"
                if i is None
                else "built"
                if i < idx[cur]
                else ("current" if r["order"] <= lay else later)
                if i == idx[cur]
                else later
            )
    for c in g["components"]:
        if c in g["plies"]:
            continue
        i = idx.get(first.get(c))
        out[c] = (
            "hidden"
            if i is None
            else "built"
            if i < idx[cur]
            else "current"
            if i == idx[cur]
            else later
        )
    return out, idx


def test_build_state_follows_op_and_lay_and_stepping_back_hides_later_work(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 960, 600)
            pg.evaluate("window.__lab.freeze(true)")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert pg.evaluate("window.__lab.lay()") == 4  # a step opens fully built
            for ghost in (False, True):
                pg.evaluate(f"window.__lab.ghost({str(ghost).lower()})")
                for lay in (4, 1):  # forward, then back
                    pg.evaluate(f"window.__lab.setLay({lay})")
                    state = pg.evaluate("window.__lab.state()")
                    want, idx = _expected_state(g, "roncz", "r30.top-skin", lay, ghost)
                    assert (
                        set(state) <= set(want) and {k: want[k] for k in state} == state
                    ), (ghost, lay)  # every mesh, and only meshes that exist
                    if lay == 1:
                        for k in (2, 3, 4):
                            assert state[f"canard.skin_top.p{k}"] == (
                                "ghost" if ghost else "hidden"
                            )
            assert pg.evaluate("window.localStorage.getItem('longez.ghost')") == "1"
            pg.evaluate("window.__lab.advance(0.1)")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_earlier_op_plies_are_built_and_cured_at_lay_zero_of_the_next_op(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 960, 600)
            pg.evaluate("window.__lab.freeze(true)")
            pg.evaluate("window.__lab.select('r30.bottom-skin')")
            pg.evaluate("window.__lab.setLay(0)")
            pg.evaluate("window.__lab.advance(2.0)")
            cap = "canard.spar_cap_bottom.p1"
            assert pg.evaluate("window.__lab.state()")[cap] == "built"
            assert pg.evaluate(f"window.__lab.phase('{cap}')") == {
                "state": "built",
                "unroll": 1,
                "front": 1,
                "cure": 1,
            }
            assert pg.evaluate(f"window.__lab.material('{cap}').wet") == 0
            assert (
                pg.evaluate("window.__lab.state()")["canard.skin_bottom.p1"] == "hidden"
            )
            pg.evaluate(
                "window.__lab.setLay(1)"
            )  # the first skin ply unrolls, dry; the cap next to it stays cured
            pg.evaluate("window.__lab.advance(0.6)")
            ph = pg.evaluate("window.__lab.phase('canard.skin_bottom.p1')")
            assert (
                ph["state"] == "current"
                and abs(ph["unroll"] - 0.5) < 1e-9
                and ph["front"] == 0
            )
            assert pg.evaluate(f"window.__lab.material('{cap}').wet") == 0
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_play_lays_every_ply_then_cures_and_stops_and_time_only_moves_with_advance(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 960, 600)
            pg.evaluate("window.__lab.freeze(true)")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert pg.evaluate("window.__lab.play()") is True
            assert pg.evaluate("window.__lab.lay()") == 1
            assert (
                pg.evaluate(
                    "document.querySelector('#play').getAttribute('aria-pressed')"
                )
                == "true"
            )
            time.sleep(0.3)
            assert (
                pg.evaluate("window.__lab.phase('canard.skin_top.p1').unroll") == 0
            )  # frozen: wall-clock time does not move it
            seen = {1}
            for _ in range(60):
                if not pg.evaluate("window.__lab.playing()"):
                    break
                pg.evaluate("window.__lab.advance(0.25)")
                seen.add(pg.evaluate("window.__lab.lay()"))
            assert seen == {1, 2, 3, 4}
            assert pg.evaluate("window.__lab.playing()") is False
            assert pg.evaluate("window.__lab.lay()") == 4
            for k in range(1, 5):
                assert (
                    pg.evaluate(f"window.__lab.phase('canard.skin_top.p{k}').cure") == 1
                )
                assert (
                    pg.evaluate(f"window.__lab.material('canard.skin_top.p{k}').wet")
                    == 0
                )
            assert (
                pg.evaluate(
                    "document.querySelector('#play').getAttribute('aria-pressed')"
                )
                == "false"
            )
            assert (
                pg.evaluate("window.__lab.play()") is True
            )  # Play again starts over from ply 1
            assert pg.evaluate("window.__lab.lay()") == 1
            assert (
                pg.evaluate("window.__lab.play()") is False
            )  # a second press while playing stops it
            assert pg.evaluate("window.__lab.playing()") is False
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---- section cut, labels and readout (Task 4) ----
EPS = 1e-3


def _lab_at(p, url, op, w=960, h=600):
    # frozen from boot, so the sim clock (and the flow pulses' phase) is the same on every run, whatever the machine load
    b, pg, errors = _open(p, url, w, h, query="&freeze=1")
    pg.evaluate("window.__lab.freeze(true)")
    pg.evaluate(f"window.__lab.select('{op}')")  # a step opens fully built
    return b, pg, errors


def _lab_of(g, cid):
    return g["components"][cid]["label"]


def _want_layers(g, bl, alive=None):
    """The 2.1 summary text for the layup nodes cut at `bl`, from graph.json alone (independent of the TypeScript)."""
    rows = sorted(
        (
            n
            for k, n in g["layup"]["nodes"].items()
            if (n["bl_max"] is None or bl <= n["bl_max"])
            and (alive is None or k in alive)
        ),
        key=lambda n: (n["op_index"], n["order"]),
    )
    seen = []
    for n in rows:
        if n["component"] not in seen:
            seen.append(n["component"])
    out = []
    for cid in seen:
        cl = {}
        for n in rows:
            if n["component"] == cid:
                cl[n["cloth"]] = cl.get(n["cloth"], 0) + 1
        out.append(
            f"{_lab_of(g, cid)}: " + ", ".join(f"{v} {k}" for k, v in cl.items())
        )
    return " · ".join(out)


def test_section_readout_lists_the_layers_cut_there(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            assert (
                pg.get_attribute("#section-bl", "max") == str(g["layup"]["semi_span"])
                and pg.get_attribute("#section-bl", "min") == "0"
            )
            assert pg.get_attribute("#section-bl", "step") == "0.5" and pg.is_visible(
                "#section"
            )
            assert pg.inner_text("#ro-station") == "Section off"
            pg.click("#section-on")  # the real controls, once
            pg.eval_on_selector(
                "#section-bl",
                "(e) => { e.value = 40; e.dispatchEvent(new Event('input', {bubbles: true})); }",
            )
            assert (
                pg.inner_text("#ro-station") == "B.L. 40"
                and pg.inner_text("#section-station") == "B.L. 40"
            )
            txt = pg.inner_text("#ro-layers")
            assert _want_layers(g, 40) in txt and _lab_of(g, "canard.core") in txt, (
                txt,
                _want_layers(g, 40),
            )
            assert pg.get_attribute("#ro-layers", "title") == pg.evaluate(
                "document.getElementById('ro-layers').textContent"
            )  # phone: the full text lives in the title
            assert pg.get_attribute("#readout", "aria-live") == "polite"
            pg.evaluate(
                "window.__lab.setSection(true, 12.5)"
            )  # the slider steps 0.5; fmtBl rounding is unit-tested
            assert pg.inner_text("#ro-station") == "B.L. 12.5"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_section_readout_lists_only_built_layers(rsite):
    """The plane cuts every visible layer and only those: at the shear-web op the skins and spar caps are not built yet."""
    g = _graph(rsite)
    later = [
        "canard.skin_top",
        "canard.skin_bottom",
        "canard.spar_cap_top",
        "canard.spar_cap_bottom",
    ]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            pg.evaluate("window.__lab.setSection(true, 20)")
            txt = pg.inner_text("#ro-layers")
            assert (
                _lab_of(g, "canard.shear_web") in txt
                and _lab_of(g, "canard.core") in txt
            ), txt
            assert not [c for c in later if _lab_of(g, c) in txt], txt
            pg.evaluate(
                "window.__lab.ghost(true)"
            )  # future work drawn see-through is still not built: not a layer of the cut
            assert not [
                c for c in later if _lab_of(g, c) in pg.inner_text("#ro-layers")
            ]
            pg.evaluate("window.__lab.ghost(false)")
            pg.evaluate(
                "window.__lab.setLay(1)"
            )  # one ply into the web op: only ply 1 is built, so only ply 1 is listed
            web = [
                n
                for n in g["layup"]["nodes"].values()
                if n["component"] == "canard.shear_web"
                and n["order"] <= 1
                and (n["bl_max"] is None or 20 <= n["bl_max"])
            ]
            assert len(web) == 1
            assert (
                f'{_lab_of(g, "canard.shear_web")}: 1 {web[0]["cloth"]}'
                in pg.inner_text("#ro-layers")
            )
            pg.evaluate("window.__lab.select('r30.top-skin')")
            txt = pg.inner_text("#ro-layers")
            assert all(
                _lab_of(g, c) in txt
                for c in later + ["canard.shear_web", "canard.core"]
            ), txt
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("bl", [5, 20, 30, 40, 54, 60])
def test_cut_geometry_matches_layer_data(rsite, bl):
    """The capped solids are exactly the plies layersAt lists (bl <= bl_max, inclusive like counts_at), plus the foam core."""
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")  # every ply built
            pg.evaluate(f"window.__lab.setSection(true, {bl})")
            have = set(pg.evaluate("window.__lab.meshNames()"))
            want = {
                n
                for n, v in g["layup"]["nodes"].items()
                if (v["bl_max"] is None or bl <= v["bl_max"]) and n in have
            }
            c = pg.evaluate("window.__lab.cut()")
            capped = set(c["cappedNodes"])
            assert capped - {"canard.core"} == want, (bl, capped ^ want)
            assert "canard.core" in capped
            assert set(c["capNodesVisible"]) == capped and c["capsVisible"] == len(
                capped
            )  # every cap the shader will draw is a capped solid
            assert c["planeConstant"] == pytest.approx(-bl + EPS, abs=1e-6)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_no_caps_for_hidden_ghost_or_disabled_solids(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            assert pg.evaluate("window.__lab.cut().capsVisible") == 0  # section off
            pg.evaluate("window.__lab.setSection(true, 20)")
            c = pg.evaluate("window.__lab.cut()")
            assert c["capsVisible"] > 0
            bad = [
                n
                for n in c["capNodesVisible"]
                if n.startswith(("canard.skin_", "canard.spar_cap_"))
            ]
            assert not bad and "canard.shear_web.p1" in c["capNodesVisible"], c[
                "capNodesVisible"
            ]
            pg.evaluate(
                "window.__lab.ghost(true)"
            )  # ghosted future work does not cap either
            assert not [
                n
                for n in pg.evaluate("window.__lab.cut().capNodesVisible")
                if n.startswith(("canard.skin_", "canard.spar_cap_"))
            ]
            pg.evaluate("window.__lab.ghost(false)")
            pg.evaluate("window.__lab.setSection(false, 20)")
            assert pg.evaluate("window.__lab.cut().capsVisible") == 0
            pg.evaluate("window.__lab.setSection(true, 20)")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert any(
                n.startswith("canard.skin_top")
                for n in pg.evaluate("window.__lab.cut().capNodesVisible")
            )
            pg.evaluate(
                "window.__lab.select('r30.templates-cores')"
            )  # back to a core-only build: nothing else may keep a cap
            assert pg.evaluate("window.__lab.cut().capNodesVisible") == ["canard.core"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_station_maps_to_model_bl_not_mirrored_and_the_plane_follows_the_flip(rsite):
    """A bl_max-30 ply is cut at B.L. 25 and not at B.L. 35, and the plane keeps the outboard side in either pose."""
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            box = pg.evaluate("window.__lab.plyBox('canard.shear_web.p3')")
            assert box["min"][2] == pytest.approx(-30, abs=0.01) and box["max"][
                2
            ] == pytest.approx(0, abs=0.01)  # B.L. runs along -Z, inches
            pg.evaluate("window.__lab.setSection(true, 25)")
            c = pg.evaluate("window.__lab.cut()")
            assert c["planeConstant"] == pytest.approx(-25, abs=0.01) and c["bl"] == 25
            assert c["keepsOutboard"] and c["removesInboard"]
            assert "canard.shear_web.p3" in c["cappedNodes"]
            pg.evaluate("window.__lab.setSection(true, 35)")
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["planeConstant"] == pytest.approx(-35, abs=0.01)
                and "canard.shear_web.p3" not in c["cappedNodes"]
            )
            assert "canard.shear_web.p1" in c["cappedNodes"]  # bl_max 54
            pg.evaluate(
                "window.__lab.select('r30.bottom-skin')"
            )  # the jig pose is inverted: the plane turns with the canard
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.pose()") == "inverted"
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["keepsOutboard"]
                and c["removesInboard"]
                and c["planeConstant"] == pytest.approx(-35, abs=0.01)
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_caps_follow_the_build_state_and_section_off_restores_the_view(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            assert pg.evaluate("window.__lab.cut().clipped") == 0
            pg.evaluate("window.__lab.setSection(true, 40)")
            c = pg.evaluate("window.__lab.cut()")
            assert c["enabled"] and c["clipped"] > 0
            assert "canard.core" in c["cappedNodes"] and not [
                x for x in c["cappedNodes"] if x.startswith("canard.skin_")
            ]  # skins are later ops: hidden
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert [
                x
                for x in pg.evaluate("window.__lab.cut().cappedNodes")
                if x.startswith("canard.skin_top")
            ]
            pg.evaluate("window.__lab.select('r30.shear-web')")
            assert not [
                x
                for x in pg.evaluate("window.__lab.cut().cappedNodes")
                if x.startswith("canard.skin_")
            ]
            pg.evaluate("window.__lab.setSection(false, 40)")
            off = pg.evaluate("window.__lab.cut()")
            assert (
                not off["enabled"]
                and off["clipped"] == 0
                and off["cappedNodes"] == []
                and off["capsVisible"] == 0
            )
            assert pg.inner_text("#ro-station") == "Section off"
            assert pg.evaluate("window.__lab.state()['canard.core']") == "built"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_cut_edge_glow_rides_the_slider_and_settles_in_sim_time(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            pg.evaluate("window.__lab.setSection(true, 30)")
            assert pg.evaluate("window.__lab.cutGlow()") == pytest.approx(1)
            time.sleep(0.3)
            assert pg.evaluate("window.__lab.cutGlow()") == pytest.approx(
                1
            )  # frozen: wall-clock time does not settle it
            pg.evaluate("window.__lab.advance(0.5)")
            mid = pg.evaluate("window.__lab.cutGlow()")
            assert 0 < mid < 1
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.cutGlow()") == 0
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_readout_tiles_at_top_skin_lay_2_with_the_section_at_bl_20(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            pg.evaluate("window.__lab.setSection(true, 20)")
            pg.evaluate("window.__lab.setLay(2)")
            want, _ = _expected_state(g, "roncz", "r30.top-skin", 2, False)
            alive = {n for n, st in want.items() if st in ("built", "current")}
            assert pg.inner_text("#ro-station") == "B.L. 20"
            assert pg.inner_text("#ro-plies") == "2 / 4"
            txt = pg.inner_text("#ro-layers")
            assert (
                _want_layers(g, 20, alive) in txt and _lab_of(g, "canard.core") in txt
            ), (txt, _want_layers(g, 20, alive))
            cnt = {}
            for n in g["layup"]["nodes"]:
                if n in alive:
                    cl = g["layup"]["nodes"][n]["cloth"]
                    cnt[cl] = cnt.get(cl, 0) + 1
            assert pg.inner_text("#ro-cloth") == " · ".join(
                f"{k} {cnt[k]}" for k in ("UND", "BID") if k in cnt
            )
            assert (
                pg.inner_text("#ro-mass") == "not yet computed"
            )  # the ledger does not source it yet: no invented number
            pg.evaluate(
                "window.__lab.select('r30.lift-tabs')"
            )  # an op without plies: no plies tile
            assert pg.is_hidden("#t-plies")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_part_labels_follow_the_build_the_camera_and_the_toggle(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert set(labs) == {
                "canard.core",
                "canard.shear_web",
                "canard.spar_cap_top",
                "canard.spar_cap_bottom",
                "canard.skin_top",
                "canard.skin_bottom",
            }  # lift tabs have no geometry
            assert all(labs[k]["text"] == _lab_of(g, k) for k in labs)
            assert (
                labs["canard.skin_top"]["opacity"] > 0.9
            )  # built and facing the camera
            assert (
                labs["canard.skin_bottom"]["opacity"] < 0.05
            )  # built, but its surface faces away from the top-skin shot
            pg.evaluate("window.__lab.select('r30.templates-cores')")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert all(
                labs[k]["opacity"] < 0.05 for k in labs if k != "canard.core"
            ), labs  # nothing else is built yet
            pg.evaluate("window.__lab.select('r30.top-skin')")
            pg.evaluate("window.__lab.advance(3)")
            assert pg.is_checked("#labels-on")
            _display(pg)
            pg.click("#labels-on")
            pg.evaluate("window.__lab.advance(3)")
            assert all(
                x["opacity"] < 0.05 for x in pg.evaluate("window.__lab.labels()")
            )
            assert pg.evaluate("window.localStorage.getItem('longez.labels')") == "0"
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert not pg.is_checked("#labels-on")  # remembered
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---- load paths as flows (Task 5)
def _drawn(pg):
    return sorted(x["id"] for x in pg.evaluate("window.__lab.paths()") if x["drawn"])


def _seen(pg):
    return sorted(x["id"] for x in pg.evaluate("window.__lab.paths()") if x["visible"])


def test_load_paths_follow_the_build_and_the_toggle_is_remembered_even_without_storage(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            assert [x["id"] for x in pg.evaluate("window.__lab.paths()")] == [
                "lift-into-caps",
                "cap-bending",
                "web-shear",
            ]
            assert _drawn(pg) == ["web-shear"]
            for op, want in [
                (
                    "r30.bottom-spar-cap",
                    ["web-shear"],
                ),  # only the bottom cap exists: neither cap path has both caps
                (
                    "r30.top-spar-cap",
                    ["cap-bending", "web-shear"],
                ),  # both caps, no skins yet: no lift
                (
                    "r30.bottom-skin",
                    ["web-shear"],
                ),  # the jig pose is inverted; the bottom skin alone is not enough
                ("r30.templates-cores", []),
            ]:
                pg.evaluate(f"window.__lab.select('{op}')")
                assert _drawn(pg) == want, op
            pg.evaluate("window.__lab.select('r30.top-skin')")
            pg.evaluate("window.__lab.setLay(0)")
            assert _drawn(pg) == [
                "cap-bending",
                "web-shear",
            ]  # skins exist once the first ply of the top skin is laid
            pg.evaluate("window.__lab.setLay(1)")
            assert _drawn(pg) == ["cap-bending", "lift-into-caps", "web-shear"]
            pg.evaluate(
                "window.__lab.select('r30.shear-web')"
            )  # stepping back hides what no longer exists
            assert _drawn(pg) == ["web-shear"]
            # the toggle: off draws nothing but the build state is unchanged; remembered across a reload, and on again
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert pg.is_checked("#paths-on") and len(_drawn(pg)) == 3
            _display(pg)
            pg.uncheck("#paths-on")
            assert _drawn(pg) == [] and _seen(pg) == [
                "cap-bending",
                "lift-into-caps",
                "web-shear",
            ]
            pg.evaluate("window.__lab.select('r30.shear-web')")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert _drawn(pg) == []  # stays off across steps
            assert pg.evaluate("window.localStorage.getItem('longez.paths')") == "0"
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert not pg.is_checked("#paths-on") and _drawn(pg) == []  # remembered
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert _drawn(pg) == []
            _display(pg)
            pg.check("#paths-on")
            assert len(_drawn(pg)) == 3
            assert not errors, errors
            # localStorage throws: on by default, and the toggle still works
            ctx = b.new_context(viewport={"width": 960, "height": 600})
            ctx.add_init_script(
                "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})"
            )
            pg2 = ctx.new_page()
            errs2 = []
            pg2.on("pageerror", lambda e: errs2.append(str(e)))
            pg2.goto(url + "?test=1&q=low&op=r30.top-skin")
            pg2.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg2.is_checked("#paths-on") and len(_drawn(pg2)) == 3
            _display(pg2)
            pg2.uncheck("#paths-on")
            assert _drawn(pg2) == []
            assert not errs2, errs2
            b.close()
    finally:
        s.shutdown()


def test_load_path_points_lie_on_their_parts_in_world_space_upright_and_inverted(rsite):
    g = _graph(rsite)
    corners = """(cid) => { const L = window.__lab, b = L.plyBox(cid), pts = [];
        for (const x of [b.min[0], b.max[0]]) for (const y of [b.min[1], b.max[1]]) for (const z of [b.min[2], b.max[2]]) pts.push(L.toWorld([x, y, z]));
        return [0, 1, 2].map((i) => [Math.min(...pts.map((q) => q[i])), Math.max(...pts.map((q) => q[i]))]) }"""  # a half turn about Z keeps the box axis aligned
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            for op, pose in (
                ("r30.top-skin", "upright"),
                ("r30.bottom-skin", "inverted"),
            ):
                b, pg, errors = _lab_at(p, url, op)
                pg.evaluate("window.__lab.advance(3)")
                assert pg.evaluate("window.__lab.pose()") == pose
                paths = pg.evaluate("window.__lab.paths()")
                checked = 0
                for lp in g["loadpaths"]:
                    boxes = [
                        pg.evaluate(corners, c)
                        for c in lp["parts"]
                        if pg.evaluate("(c) => !!window.__lab.plyBox(c)", c)
                    ]
                    pts = next(x for x in paths if x["id"] == lp["id"])["worldPoints"]
                    assert len(pts) == sum(len(sg) for sg in lp["segments"])
                    for (
                        pt
                    ) in pts:  # within 0.5 in (0.0127 m) of one of its parts' boxes
                        assert any(
                            all(
                                bx[i][0] - 0.0127 <= pt[i] <= bx[i][1] + 0.0127
                                for i in range(3)
                            )
                            for bx in boxes
                        ), (op, lp["id"], pt, boxes)
                        checked += 1
                assert checked >= 40
                web = next(x for x in paths if x["id"] == "web-shear")["worldPoints"]
                assert abs(web[0][2] - web[-1][2]) == pytest.approx(
                    54 * 0.0254, abs=1e-3
                )  # spans the 54 in of B.L., along Z
                assert not errors, errors
                b.close()
    finally:
        s.shutdown()


def _hue(rgb):
    import colorsys

    return colorsys.rgb_to_hsv(*[c / 255 for c in rgb])[0] * 360


def _strongest(im, xy, r=7):
    """The most saturated pixel (HSV) within r px of xy, as (saturation, rgb)."""
    import colorsys

    best = (-1.0, (0, 0, 0))
    for x in range(max(0, int(xy[0]) - r), min(im.width, int(xy[0]) + r + 1)):
        for y in range(max(0, int(xy[1]) - r), min(im.height, int(xy[1]) + r + 1)):
            px = im.getpixel((x, y))[:3]
            sat = colorsys.rgb_to_hsv(*[c / 255 for c in px])[1]
            if sat > best[0]:
                best = (sat, px)
    return best


def _own_kind(kinds, rgb):
    def d(k):
        a = abs(_hue(rgb) - _hue([c * 255 for c in kinds[k]]))
        return min(a, 360 - a)

    return min(kinds, key=d)


def test_the_section_cut_clips_load_paths_and_the_flows_are_drawn_in_their_own_colours(
    rsite,
):
    from PIL import Image

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            pg.add_style_tag(
                content="#controls,#dock,#labels,#opbar{visibility:hidden}"
            )
            pg.evaluate("window.__lab.advance(3)")
            paths = {x["id"]: x for x in pg.evaluate("window.__lab.paths()")}
            assert not any(
                x["clipped"] for x in paths.values()
            )  # section off: unclipped
            kinds = {x["kind"]: x["color"] for x in paths.values()}
            assert len(kinds) == 3 and len({tuple(c) for c in kinds.values()}) == 3

            def snap():
                pg.evaluate("window.__lab.advance(0)")
                return Image.open(io.BytesIO(pg.screenshot())).convert("RGB")

            def mid(
                x, i=None
            ):  # the middle of a polyline's first segment (points are in order, two segments' worth for bending)
                pts = x["worldPoints"]
                n = len(pts) if i is None else i
                return [(pts[n // 2 - 1][k] + pts[n // 2][k]) / 2 for k in range(3)]

            web, cap, lift = (
                paths["web-shear"],
                paths["cap-bending"],
                paths["lift-into-caps"],
            )
            pg.evaluate("document.getElementById('paths-on').click()")
            bare = snap()  # the same frame without the flows: the laminate is cream
            pg.evaluate("document.getElementById('paths-on').click()")
            im = snap()
            for x in (web, cap, lift):
                xy = pg.evaluate(
                    "(p) => window.__lab.project(p)",
                    mid(x, 6 if x is lift else 9 if x is cap else None),
                )
                sat, rgb = _strongest(im, xy)
                if (
                    x["kind"] == "bending"
                ):  # amber is close to the cream laminate's hue: it must also be clearly more saturated than the bare frame
                    assert sat > _strongest(bare, xy)[0] + 0.15, (x["id"], sat, rgb)
                assert _own_kind(kinds, rgb) == x["kind"], (x["id"], rgb)
            # the plane is the structure's: at B.L. 30 the web at B.L. 22 is clipped away, at B.L. 45 it is not
            pg.evaluate("window.__lab.setSection(true, 30)")
            paths = {x["id"]: x for x in pg.evaluate("window.__lab.paths()")}
            assert all(
                x["clipped"] for x in paths.values()
            )  # every path reaches inboard of B.L. 30 (lift starts at 6.75)
            im = snap()
            wp = paths["web-shear"]["worldPoints"]

            def at(bl):
                return [
                    wp[0][0],
                    wp[0][1],
                    wp[0][2] + (wp[-1][2] - wp[0][2]) * bl / 54,
                ]

            xk, xg = (
                pg.evaluate("(p) => window.__lab.project(p)", at(bl)) for bl in (45, 22)
            )
            assert all(0 <= q[0] < 960 and 0 <= q[1] < 600 for q in (xk, xg)), (
                xk,
                xg,
            )  # both stations are on screen at this shot
            sk, kept = _strongest(im, xk)
            sg, gone = _strongest(im, xg)
            assert _own_kind(kinds, kept) == "shear" and sk > 0.4, (kept, sk)
            assert _own_kind(kinds, gone) != "shear" or sg < 0.4, (
                gone,
                sg,
            )  # clipped with the structure
            pg.evaluate(
                "window.__lab.setSection(true, 5)"
            )  # the lift paths lie outboard of B.L. 5; the spar caps and the web reach the root
            clipped = {
                x["id"]: x["clipped"] for x in pg.evaluate("window.__lab.paths()")
            }
            assert clipped == {
                "lift-into-caps": False,
                "cap-bending": True,
                "web-shear": True,
            }
            pg.evaluate("window.__lab.setSection(false, 5)")
            assert not any(x["clipped"] for x in pg.evaluate("window.__lab.paths()"))
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---------------------------------------------------------------- the tour and the film (Task 6)


def _tour_ops(g, variant="roncz"):
    """The ops the tour visits: chapter 30, non-stub, in graph order (the same rule as guide/viewer/js/tour.js)."""
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if variant
        in byid[i]["variants"]
        + (["roncz", "gu"] if "both" in byid[i]["variants"] else [])
        and byid[i]["chapter"] == 30
        and not byid[i]["stub"]
    ]


def _open_rec(p, url, w=960, h=600, query=""):
    b = p.chromium.launch(args=GL)
    pg = b.new_page(viewport={"width": w, "height": h})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url + "?rec=1&q=low&test=1" + query)
    pg.wait_for_function(
        "window.__rec && window.__lab && window.__lab.ready", timeout=90000
    )
    return b, pg, errors


def test_rec_film_visits_every_op_in_order_and_ends(rsite):
    g = _graph(rsite)
    want = _tour_ops(g)
    layup = g["layup"]["nodes"]
    span = {}
    for n in layup.values():
        span[n["op"]] = max(
            span.get(n["op"], 0),
            n["bl_max"] if n["bl_max"] is not None else g["layup"]["semi_span"],
        )
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url, query="&clean=1")
            assert pg.evaluate(
                "document.body.classList.contains('rec')"
            ) and pg.evaluate("document.body.classList.contains('clean')")
            assert not pg.is_visible("#controls") and not pg.is_visible(
                "#opbar"
            )  # ?clean=1: the canvas and the cards only
            dur = pg.evaluate("window.__rec.start('canard')")
            assert 55 <= dur <= 95, dur  # the film is about a minute and a half
            assert pg.evaluate("__lab.touring()") is True
            seen, idx, plays, cuts, active, frames = [], [], set(), [], True, 0
            shots = {
                op: pg.evaluate(f"__lab.shot('{op}') || __lab.shot('home')")
                for op in want
            }
            dist = lambda a, c: sum((x - y) ** 2 for x, y in zip(a, c)) ** 0.5  # noqa: E731
            best = {
                op: [9e9, 9e9] for op in want
            }  # the closest the camera's target / distance came to the op's shot while it was selected
            top_lay, scrub_max = {}, {}
            snap_js = """(() => { const L = __lab, c = L.cut(); return [L.selected(), L.tourIndex(), L.playing(), c.enabled, c.bl, L.lay(),
                +document.getElementById('scrub').max, L.camera()] })()"""
            while active and frames < 60 * 100 * 2:
                r = pg.evaluate("window.__rec.frame(1 / 60, false)")
                active = r["active"]
                frames += 1
                sel, i, playing, cut_on, cut_bl, lay, smax, cam = pg.evaluate(snap_js)
                if sel and (not seen or seen[-1] != sel):
                    seen.append(sel)
                if not idx or idx[-1] != i:
                    idx.append(i)
                if playing:
                    plays.add(sel)
                if (
                    cut_on
                    and sel in span
                    and (not cuts or cuts[-1][:2] != [sel, cut_bl])
                ):
                    cuts.append([sel, cut_bl])
                if sel in best:
                    sh = shots[sel]
                    best[sel][0] = min(best[sel][0], dist(cam["target"], sh["target"]))
                    best[sel][1] = min(
                        best[sel][1],
                        abs(
                            dist(cam["pos"], cam["target"])
                            - dist(sh["pos"], sh["target"])
                        ),
                    )
                    top_lay[sel] = max(top_lay.get(sel, 0), lay)
                    scrub_max[sel] = smax
            assert not active and pg.evaluate("__lab.touring()") is False
            assert abs(frames / 60 - dur) < 1.0, (frames, dur)
            assert seen == want, seen
            assert idx == list(
                range(len(want))
            ), idx  # the segment index only moves forward, one op at a time
            with_plies = {o for o in want if o in span}
            assert (
                plays == with_plies
            ), plays  # Play is pressed for exactly the ops that have plies
            assert (
                {c[0] for c in cuts} == with_plies
            )  # ... and each of them is cut open once, inside its own layup
            assert all(0 <= bl <= span[op] for op, bl in cuts), cuts
            assert (
                pg.evaluate("__lab.selected()") is None
            )  # the film ends on the finished canard
            assert (
                pg.evaluate("__lab.cut().enabled") is False
            )  # ... and the person's own section setting is back
            # 2.1 parity: the camera eases to each op's shot within its step (the 2.1 bar was the authored target within 0.05 in; the
            # lab's units are metres, so 0.01 m = 0.4 in is the tighter bar), and the scrubber reaches the top ply before the tour advances
            assert all(b[0] < 0.01 and b[1] < 0.01 for b in best.values()), best
            nply = {}
            for n in layup.values():
                nply[n["op"]] = nply.get(n["op"], 0) + 1
            for op in with_plies:
                assert scrub_max[op] == nply[op] and top_lay[op] == nply[op], (
                    op,
                    top_lay[op],
                    scrub_max[op],
                    nply[op],
                )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _adv(pg, seconds, dt=0.05):
    """advance the sim clock without drawing (recorder mode owns the clock: nothing moves between calls)"""
    for _ in range(round(seconds / dt)):
        pg.evaluate(f"window.__rec.frame({dt}, false)")


def _tour_to_first_ply_op(pg, g):
    pg.click("#tour")
    assert pg.evaluate("__lab.touring()") is True
    assert pg.evaluate("__lab.tourIndex()") == 0
    for _ in range(400):
        _adv(pg, 0.25)
        if pg.evaluate("__lab.selected()") == "r30.shear-web" and pg.evaluate(
            "__lab.playing()"
        ):
            return
    raise AssertionError("the tour never pressed Play on the shear web")


def test_tour_button_runs_the_tour_and_every_user_action_stops_it(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            assert (
                pg.get_attribute("#tour", "aria-pressed") == "false"
                and pg.text_content("#tour") == "Tour"
            )
            _tour_to_first_ply_op(pg, g)
            assert (
                pg.get_attribute("#tour", "aria-pressed") == "true"
                and pg.text_content("#tour") == "Stop tour"
            )
            assert pg.evaluate("__lab.tourIndex()") == _tour_ops(g).index(
                "r30.shear-web"
            )  # the segment follows the op it is showing
            assert pg.evaluate("__lab.lay()") >= 1

            def stops(label, act, keeps_op=True):
                _tour_to_first_ply_op(pg, g) if not pg.evaluate(
                    "__lab.touring()"
                ) else None
                sel, lay, ci = pg.evaluate(
                    "[__lab.selected(), __lab.lay(), __lab.tourIndex()]"
                )
                act()
                assert pg.evaluate("__lab.touring()") is False, label
                assert (
                    pg.get_attribute("#tour", "aria-pressed") == "false"
                    and pg.text_content("#tour") == "Tour"
                ), label
                _adv(pg, 0.3)
                if keeps_op:
                    assert (
                        pg.evaluate("__lab.selected()") == sel
                    ), label  # it stays where it was
                return sel

            stops("escape", lambda: pg.keyboard.press("Escape"))
            stops("second press", lambda: pg.click("#tour"))
            other = "r30.top-skin"
            stops(
                "op chip",
                lambda: pg.click(f'#chips button[data-op="{other}"]'),
                keeps_op=False,
            )
            assert (
                pg.evaluate("__lab.selected()") == other
            )  # the click still did its job
            stops(
                "variant",
                lambda: pg.click('#variant button[data-variant="gu"]'),
                keeps_op=False,
            )
            pg.click('#variant button[data-variant="roncz"]')
            stops(
                "scrubber",
                lambda: pg.evaluate(
                    "(() => { const s = document.getElementById('scrub'); s.value = '1'; s.dispatchEvent(new Event('input', { bubbles: true })) })()"
                ),
                keeps_op=False,
            )
            assert pg.evaluate("__lab.lay()") == 1
            stops("play", lambda: pg.click("#play"), keeps_op=False)
            assert (
                pg.get_attribute("#play", "aria-pressed") == "true"
            )  # Play itself runs, unfought: it restarted from ply 1 under the person's press
            assert (
                pg.evaluate("__lab.playing()") is True
                and pg.evaluate("__lab.lay()") == 1
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_tour_can_be_run_twice_and_leaves_no_cut_or_cursor_behind(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            for _ in range(2):
                pg.click("#tour")
                for _ in range(400):
                    _adv(pg, 0.25)
                    if pg.evaluate("__lab.cut().enabled"):
                        break
                assert (
                    pg.evaluate("__lab.cut().enabled") is True
                )  # the tour opened the section
                pg.click(
                    "#tour"
                )  # stop with the cut open: the state stays where it was
                assert (
                    pg.evaluate("__lab.touring()") is False
                    and pg.evaluate("__lab.cut().enabled") is False
                )  # the cut goes back to what the person had
                assert (
                    pg.evaluate("document.getElementById('cursor').style.opacity")
                    == "0"
                )
                pg.click(
                    "#section-on"
                )  # the person's own control still works after the tour
                assert pg.evaluate("__lab.cut().enabled") is True
                pg.click("#section-on")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_tour_leaves_paths_labels_and_storage_as_the_person_set_them(rsite):
    """2.1's rule: a tour may change what is shown while it runs, but it never writes storage, and when it stops the toggles are as they were."""
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 960, "height": 600})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(
                url + "config.json"
            )  # same origin: seed the person's stored settings, then count every setItem from the lab's first line
            pg.evaluate(
                "() => { localStorage.setItem('longez.paths', '0'); localStorage.setItem('longez.labels', '0') }"
            )
            pg.add_init_script(
                "window.__setItems = 0; const o = Storage.prototype.setItem; Storage.prototype.setItem = function () { window.__setItems++; return o.apply(this, arguments) }"
            )
            pg.goto(url + "?rec=1&q=low&test=1")
            pg.wait_for_function(
                "window.__rec && window.__lab && window.__lab.ready", timeout=90000
            )
            assert not pg.is_checked("#paths-on") and not pg.is_checked("#labels-on")
            pg.click("#tour")
            shown = False
            for _ in range(400):
                _adv(pg, 0.25)
                if pg.evaluate("__lab.paths().some(p => p.drawn)") and pg.evaluate(
                    "__lab.labels().some(l => l.opacity > 0)"
                ):
                    shown = True
                    break
            assert shown, "the tour should show paths and part names while it runs"
            pg.keyboard.press("Escape")
            _adv(pg, 2.0)  # the part names fade out in sim time
            assert pg.evaluate("__lab.touring()") is False
            assert not pg.is_checked("#paths-on") and not pg.is_checked("#labels-on")
            assert pg.evaluate(
                "[localStorage.getItem('longez.paths'), localStorage.getItem('longez.labels')]"
            ) == ["0", "0"]
            assert pg.evaluate("__lab.paths().every(p => !p.drawn)") and pg.evaluate(
                "__lab.labels().every(l => l.opacity === 0)"
            )
            assert pg.evaluate("window.__setItems") == 0  # the tour never wrote storage
            assert pg.evaluate("__lab.cut().enabled") is False
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.local_render
def test_recorder_frames_are_reproducible(rsite):
    """Two independent pages render frames 0, 120 and 240 of the film. The frame is a function of the sim clock only (grain, flows, glow,
    cursor and cards all take sim time; nothing reads the wall clock or Math.random), so the PNGs must match. On the software renderer
    used here they are compared byte for byte; if a GPU or driver ever makes that impossible the fallback bar is a 1% pixel difference."""
    from PIL import Image, ImageChops

    s, url = serve(rsite)
    runs = []
    try:
        with sync_playwright() as p:
            for _ in range(2):
                b, pg, errors = _open_rec(p, url)
                pg.evaluate("window.__rec.start('canard')")
                shots = {}
                for i in range(241):
                    if i in (0, 120, 240):
                        pg.evaluate("window.__rec.frame(1 / 60, true)")
                        shots[i] = pg.screenshot()
                    else:
                        pg.evaluate("window.__rec.frame(1 / 60, false)")
                assert not errors, errors
                runs.append(shots)
                b.close()
    finally:
        s.shutdown()
    for i in (0, 120, 240):
        a, c = runs[0][i], runs[1][i]
        if a == c:
            continue
        ia, ic = (
            Image.open(io.BytesIO(a)).convert("RGB"),
            Image.open(io.BytesIO(c)).convert("RGB"),
        )
        diff = (
            ImageChops.difference(ia, ic)
            .convert("L")
            .point(lambda v: 255 if v > 0 else 0)
        )
        frac = sum(diff.histogram()[255:]) / (ia.width * ia.height)
        assert frac <= 0.01, f"frame {i} differs in {frac:.2%} of pixels"
    # and the frames are not the same picture: the clock really moves the film
    assert runs[0][0] != runs[0][240]


# ---- quality tiers and the frame budget (Task 7) ----
FRAME_BUDGET_MS = 33  # the budget; never raised. Default rAF quantises at 16.7 ms, so a median of 33.3 ms FAILS it.
FRAMES_JS = """(() => { const d = []; let run = false, last = 0;
    const tick = t => { if (run && last) d.push(t - last); last = t; requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
    window.__frames = { start() { d.length = 0; run = true; last = 0; }, stop() { run = false; return d.slice(); } }; })()"""
# Drags #section-bl from 0 to max over `ms`, one input event per animation frame; returns the slider value seen at each frame.
DRAG_JS = """(ms) => new Promise(res => { const el = document.querySelector('#section-bl'), max = +el.max, step = +el.step || 1, t0 = performance.now(), seen = [];
    const tick = t => { const k = Math.min(1, (t - t0) / ms); el.value = k < 1 ? Math.round(max * k / step) * step : el.max; seen.push(+el.value);
        el.dispatchEvent(new Event('input', {bubbles: true})); if (k < 1) requestAnimationFrame(tick); else res(seen); };
    requestAnimationFrame(tick); })"""
# Feeds frame times until the tier changes (or `max` frames); one evaluate, because a page rendering the high tier in software GL answers slowly.
FEED_JS = """([ms, max]) => { const t0 = window.__lab.tier(); for (let i = 0; i < max; i++) { window.__lab.feedFrame(ms); if (window.__lab.tier() !== t0) break; } return window.__lab.tier(); }"""
EFFECTIVE_MAX_JS = """(() => { const e = document.querySelector('#section-bl'), v = e.value; e.value = e.max; const m = +e.value; e.value = v; return m; })()"""  # max after step snapping


@pytest.mark.local_render
def test_frame_time_median_while_dragging_the_section_on_the_low_tier(rsite):
    # Ported from the 2.1 viewer's budget test. Headless swiftshader (software GL) is a PROXY for the iPad, not a measurement of it:
    # the iPad judgement is the owner's walk-through. The budget is a median rAF delta <= 33 ms over a continuous 2 s drag of the
    # section slider from B.L. 0 to max, top-skin op, all plies, load paths on, section on, at 1180x820, on ?q=low. It is never raised.
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            # real frames: not frozen, and ?realframes=1 lets the low tier's adaptive resolution see them (tests otherwise feed their own)
            b, pg, errors = _open(
                p, url, 1180, 820, init=FRAMES_JS, q="low", query="&realframes=1"
            )
            assert (
                pg.evaluate("window.__lab.tier()") == "low"
                and pg.evaluate("window.__lab.auto()") is False
            )
            pg.evaluate(
                "window.__lab.select('r30.top-skin')"
            )  # a step opens fully built: all its plies
            assert (
                pg.is_checked("#paths-on")
                and len(
                    [x for x in pg.evaluate("window.__lab.paths()") if x["visible"]]
                )
                == 3
            )
            pg.click("#section-on")
            pg.eval_on_selector(
                "#section-bl",
                "(e) => { e.value = 0; e.dispatchEvent(new Event('input', {bubbles: true})); }",
            )
            pg.wait_for_timeout(500)
            max_bl = pg.evaluate(EFFECTIVE_MAX_JS)
            # The low tier trims its resolution while frames run long (quality.ts). Give it a warm-up drag of the same cut, then wait for the
            # resolution to stop moving, so the measured drag runs at the resolution the tier settled on (printed below).
            pg.evaluate(DRAG_JS, 2000)
            pg.eval_on_selector(
                "#section-bl",
                "(e) => { e.value = 0; e.dispatchEvent(new Event('input', {bubbles: true})); }",
            )
            still, last = 0, None
            for _ in range(60):
                pg.wait_for_timeout(1000)
                cur = pg.evaluate("window.__lab.resScale()")
                still = still + 1 if cur == last else 0
                last = cur
                if still >= 3:
                    break
            assert still >= 3, f"resolution never settled (scale {last})"
            print(
                "settled resolution scale",
                last,
                "pixels",
                pg.evaluate("window.__lab.stats()")["pixels"],
            )
            before = pg.evaluate("window.__lab.cut()")
            assert before["enabled"] and before["bl"] == pytest.approx(
                0, abs=1e-6
            ), before
            pg.evaluate("window.__frames.start()")
            seen = pg.evaluate(DRAG_JS, 2000)
            d = pg.evaluate("window.__frames.stop()")
            pg.wait_for_timeout(150)
            after = pg.evaluate("window.__lab.cut()")
            st = pg.evaluate("window.__lab.stats()")
            d = sorted(d)
            med = d[len(d) // 2]
            print("frame stats", st, "n", len(d), "distinct bl", len(set(seen)))
            print("median frame ms", med)
            # the cut really moved during the drag (not a frozen view being timed)
            assert after["enabled"] and after["bl"] == pytest.approx(max_bl), (
                before["bl"],
                after["bl"],
                max_bl,
            )
            assert seen[0] <= max_bl * 0.05 and seen[-1] == max_bl, (
                seen[:3],
                seen[-3:],
                max_bl,
            )
            assert all(
                a <= c for a, c in zip(seen, seen[1:])
            ), "slider values must be monotonic non-decreasing"
            # "The plane really moved" is about distinct positions per drawn frame, not a frame count: 2.1 asked for >= 100 distinct stations,
            # which only a 60 fps run can reach in 2 s (a 92-frame run on the Mac test node read 91 and failed with a 16.7 ms median). So: a new
            # station on (nearly) every tick of the drag, and no tick jumps more than a tenth of the span (no chunk of the drag went unseen).
            assert len(set(seen)) >= 0.9 * len(seen), (len(set(seen)), len(seen))
            assert max(b_ - a for a, b_ in zip(seen, seen[1:])) <= 0.1 * max_bl, max(
                b_ - a for a, b_ in zip(seen, seen[1:])
            )
            assert st["calls"] > 20, st  # the last frame drew a real scene
            assert len(d) >= 10, len(d)
            assert pg.evaluate("window.__lab.tier()") == "low"
            assert med <= FRAME_BUDGET_MS, (med, len(d), st)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_forced_tier_freeze_and_rec_turn_automatic_step_down_off(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            for q, query, want_auto in [("mid", "", False), (None, "&freeze=1", False)]:
                b, pg, errors = _open(p, url, 500, 360, q=q, query=query)
                assert pg.evaluate("window.__lab.auto()") is want_auto
                start = pg.evaluate("window.__lab.tier()")
                assert pg.evaluate(FEED_JS, [80, 400]) == start
                assert not errors, errors
                b.close()
            # ?rec=1 is a forced high tier, and off
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 500, "height": 360})
            pg.goto(url + "?rec=1&test=1")
            pg.wait_for_function(
                "window.__rec && window.__lab && window.__lab.ready", timeout=90000
            )
            assert (
                pg.evaluate("window.__lab.tier()") == "high"
                and pg.evaluate("window.__lab.auto()") is False
            )
            b.close()
    finally:
        s.shutdown()


def test_auto_step_down_drops_high_to_mid_to_low_and_the_scene_keeps_its_state(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 500, 360, q=None, query="&op=r30.top-skin"
            )  # no ?q=: auto is on, and a desktop starts on high
            assert (
                pg.evaluate("window.__lab.auto()") is True
                and pg.evaluate("window.__lab.tier()") == "high"
            )
            pg.evaluate("window.__lab.setLay(3)")
            names = pg.evaluate("window.__lab.meshNames()")
            sel, lay = (
                pg.evaluate("window.__lab.selected()"),
                pg.evaluate("window.__lab.lay()"),
            )
            assert (
                sel == "r30.top-skin"
                and lay == 3
                and pg.inner_text("#quality-label") == "Quality: High (auto)"
            )
            # fast frames change nothing
            assert pg.evaluate(FEED_JS, [16.7, 200]) == "high"
            seen = ["high"]
            for _ in range(
                2
            ):  # slow frames until the tier drops (the frames right after a drop are ignored while it settles)
                seen.append(pg.evaluate(FEED_JS, [60, 60]))
            assert seen == ["high", "mid", "low"], seen
            assert pg.evaluate(FEED_JS, [400, 200]) == "low"  # never below low
            assert pg.evaluate(FEED_JS, [5, 200]) == "low"  # and no step back up
            # nothing about the build was lost, and it still draws
            assert pg.evaluate("window.__lab.meshNames()") == names
            assert (
                pg.evaluate("window.__lab.selected()") == sel
                and pg.evaluate("window.__lab.lay()") == lay
            )
            # It still draws. One full-file run read 0 draw calls here: three.js skips a frame while the GL context is lost, and swiftshader
            # seems to drop it when the tier and the resolution are rebuilt back to back (not confirmed). So redraw until a frame lands.
            pg.wait_for_function(
                "(window.__lab.advance(0.05), window.__lab.stats().calls > 20)",
                timeout=10000,
                polling=200,
            )
            assert pg.inner_text("#quality-label") == "Quality: Low (auto)"
            assert (
                pg.get_attribute('#quality-seg button[data-q="auto"]', "aria-pressed")
                == "true"
            )
            # the segmented control overrides: a tier turns auto off, Auto turns it back on
            _display(pg)
            pg.click('#quality-seg button[data-q="high"]')
            assert (
                pg.evaluate("window.__lab.tier()") == "high"
                and pg.evaluate("window.__lab.auto()") is False
            )
            assert pg.inner_text("#quality-label") == "Quality: High"
            assert (
                pg.get_attribute('#quality-seg button[data-q="high"]', "aria-pressed")
                == "true"
            )
            pg.evaluate("window.__lab.advance(0.05)")
            assert (
                pg.evaluate("window.__lab.meshNames()") == names
                and pg.evaluate("window.__lab.lay()") == lay
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---- layout: the canard owns the frame (Task 8) ----
_CANARD_BOX_JS = """() => {
  const L = window.__lab, W = innerWidth, H = innerHeight, st = L.state()
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9
  for (const n of Object.keys(st)) {
    if (st[n] === 'hidden') continue
    const b = L.meshBox(n)
    if (!b) continue
    for (const x of [b[0][0], b[1][0]]) for (const y of [b[0][1], b[1][1]]) for (const z of [b[0][2], b[1][2]]) {
      const p = L.project([x, y, z]); x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); x1 = Math.max(x1, p[0]); y1 = Math.max(y1, p[1])
    }
  }
  return [Math.max(0, x0), Math.max(0, y0), Math.min(W, x1), Math.min(H, y1)]
}"""
_CARDS = ("#controls", "#dock", "#opbar")


def _rect(pg, sel):
    return pg.evaluate(
        f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom] }})()"
    )


@pytest.mark.parametrize("w,h", [(1400, 860), (1180, 820), (390, 844)])
def test_the_cards_leave_the_canard_clear_and_touch_targets_are_44px(rsite, w, h):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(
                viewport={"width": w, "height": h}, has_touch=w < 1400
            )  # the iPad and the phone have coarse pointers
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            for op in (None, "r30.top-skin"):
                pg.goto(url + "?test=1&q=low" + (f"&op={op}" if op else ""))
                pg.wait_for_function(
                    "window.__lab && window.__lab.ready", timeout=60000
                )
                if op:
                    pg.evaluate(
                        "window.__lab.setLay(Number(document.getElementById('scrub').max))"
                    )
                    pg.evaluate("window.__lab.setSection(true, 20)")
                pg.evaluate("window.__lab.advance(4)")
                assert not pg.evaluate("window.__lab.flying()")
                assert pg.is_hidden("#viewpop")  # the display popover starts closed
                if w == 390:
                    # a phone cannot keep the canard clear of every card, but the band between the top and bottom cards is >= 300 px
                    top = _rect(pg, "#controls")[3]
                    bottom = min(_rect(pg, "#dock")[1], _rect(pg, "#opbar")[1])
                    assert bottom - top >= 300, (op, top, bottom)
                    continue
                box = pg.evaluate(_CANARD_BOX_JS)
                area = (box[2] - box[0]) * (box[3] - box[1])
                assert area > 0.05 * w * h, (
                    op,
                    box,
                )  # the canard is on screen, not a speck
                for sel in _CARDS:
                    c = _rect(pg, sel)
                    ov = max(0, min(box[2], c[2]) - max(box[0], c[0])) * max(
                        0, min(box[3], c[3]) - max(box[1], c[1])
                    )
                    assert ov < 0.10 * area, (w, op, sel, round(ov / area, 3), box, c)
            if w < 1400:
                # every control in the cards is a 44 px target on a touch screen, the popover's too (the 2.1 bar)
                pg.click("#more")
                small = pg.evaluate("""() => [...document.querySelectorAll(['#controls button', '#controls input[type=range]', '#controls label.check',
                    '#viewpop button', '#viewpop label.check', '#opbar button', '#step-head'].join(','))].filter((e) => e.offsetParent)
                    .map((e) => [e.id || e.textContent.trim().slice(0, 24), e.getBoundingClientRect().height]).filter((x) => x[1] < 43.5)""")
                assert small == [], small
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Parity with the milestone 2.1 behaviour tests (they lived in test_viewer_e2e.py and now run against the lab at /).
# The mapping from each 2.1 test to its lab counterpart is in the Task 8 report; the names below say what they port.
# ======================================================================================================================
def _scrub(pg, v):
    pg.eval_on_selector(
        "#scrub",
        "(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }",
        str(v),
    )


def _web(pg):
    return {
        k: v
        for k, v in pg.evaluate("window.__lab.state()").items()
        if k.startswith("canard.shear_web.")
    }


def _ply_names(state):
    import re

    return {n for n in state if re.search(r"\.p\d+$", n)}


def test_scrubber_selects_web_plies_and_core_built(
    rsite,
):  # 2.1: test_scrubber_selects_web_plies_and_core_built
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            pg.click('#opbar button[data-op="r30.shear-web"]')
            assert (
                pg.is_visible("#scrub")
                and pg.get_attribute("#scrub", "max") == "6"
                and pg.input_value("#scrub") == "6"
            )
            assert pg.evaluate("window.__lab.state()['canard.core']") == "built"
            web = _web(pg)
            assert len(web) == 6 and set(web.values()) == {"current"}
            _scrub(pg, 1)
            web = _web(pg)
            assert (
                list(web.values()).count("current") == 1
                and list(web.values()).count("hidden") == 5
            )
            assert (
                pg.evaluate("window.__lab.lay()") == 1
                and pg.inner_text("#scrublabel") == "Ply 1 of 6"
            )
            st = pg.evaluate("window.__lab.state()")
            assert st["canard.core"] == "built"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_earlier_op_leaves_no_later_ply_visible(
    rsite,
):  # 2.1: test_earlier_op_leaves_no_later_ply_visible (Review Focus 1)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            pg.click('#opbar button[data-op="r30.bottom-skin"]')
            assert any(
                k.startswith("canard.skin_bottom") and v in ("built", "current")
                for k, v in pg.evaluate("window.__lab.state()").items()
            )
            for early in ("r30.shear-web", "r30.templates-cores"):
                pg.click('#opbar button[data-op="r30.bottom-skin"]')
                pg.click(f'#opbar button[data-op="{early}"]')
                assert {
                    v
                    for k, v in pg.evaluate("window.__lab.state()").items()
                    if k.startswith("canard.skin_bottom")
                } == {"hidden"}, early
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ghost_toggle_through_the_popover_and_memory(
    rsite,
):  # 2.1: test_ghost_toggle_and_memory (the control, not the hook)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            pg.click('#opbar button[data-op="r30.shear-web"]')
            _scrub(pg, 2)
            assert list(_web(pg).values()).count("hidden") == 4
            _display(pg)
            assert not pg.is_checked("#ghost")
            st = pg.evaluate("window.__lab.state()")
            future = {n for n, v in st.items() if v == "hidden" and n in _ply_names(st)}
            solid = {
                n
                for n, v in st.items()
                if n in _ply_names(st) and v in ("built", "current")
            }
            assert (
                len(future) >= 4
                and len([n for n in future if n.startswith("canard.shear_web.")]) == 4
            )
            pg.check("#ghost")
            st = pg.evaluate("window.__lab.state()")
            ghosts = {n for n, v in st.items() if v == "ghost"}
            assert ghosts == future  # exactly the future plies show, faintly
            assert {
                n
                for n, v in st.items()
                if n in _ply_names(st) and v in ("built", "current")
            } == solid  # the built/current ones are untouched
            assert len([n for n in ghosts if n.startswith("canard.shear_web.")]) == 4
            assert (
                pg.evaluate("window.__lab.state()['canard.core']") == "built"
            )  # a built mesh is never ghosted
            pg.uncheck("#ghost")
            st = pg.evaluate("window.__lab.state()")
            assert (
                not [n for n, v in st.items() if v == "ghost"]
                and {n for n, v in st.items() if v == "hidden" and n in _ply_names(st)}
                == future
            )
            pg.check("#ghost")
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            _display(pg)
            assert pg.is_checked("#ghost")
            assert {
                n
                for n, v in pg.evaluate("window.__lab.state()").items()
                if v == "ghost"
            }  # and it is in force, not just ticked
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_play_button_steps_the_scrubber_in_real_time_and_a_second_press_stops(
    rsite,
):  # 2.1: test_play_steps_scrubber_and_second_press_stops
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820)
            pg.click('#opbar button[data-op="r30.shear-web"]')
            pg.click("#play")
            assert (
                pg.input_value("#scrub") == "1"
                and pg.get_attribute("#play", "aria-pressed") == "true"
            )
            pg.wait_for_function(
                "document.querySelector('#scrub').value === '2'", timeout=15000
            )  # it steps by itself, in real time
            pg.click("#play")
            assert pg.get_attribute("#play", "aria-pressed") == "false"
            pg.wait_for_timeout(1500)
            assert (
                pg.input_value("#scrub") == "2"
                and pg.evaluate("window.__lab.playing()") is False
            )  # a second press holds it
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_scrubber_hidden_without_plies_and_hooks_need_the_test_flag(
    rsite,
):  # 2.1: test_scrubber_hidden_without_plies_and_hooks_need_test_flag
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820)
            pg.click('#opbar button[data-op="r30.templates-cores"]')
            assert (
                pg.is_hidden("#scrubwrap")
                and pg.is_hidden("#scrub")
                and pg.is_hidden("#play")
            )
            pg.goto(url)  # no ?test=1
            pg.wait_for_selector("#opbar button[data-op]")
            assert (
                pg.evaluate("typeof window.__lab") == "undefined"
                and pg.evaluate("typeof window.__rec") == "undefined"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _overlap(a, c):
    return not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])


@pytest.mark.parametrize("w,h", [(1180, 820), (390, 844)])
def test_build_controls_clear_of_other_controls(
    rsite, w, h
):  # 2.1: test_build_controls_clear_of_other_controls
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=True)
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&op=r30.shear-web")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.click(
                "#more"
            )  # the popover open: the build row must still be clear of it, and of the cards below
            bar = _rect(pg, "#scrubwrap")
            assert (
                pg.is_visible("#scrub")
                and bar[0] >= 0
                and bar[2] <= w
                and bar[1] >= 0
                and bar[3] <= h
            ), bar
            for other in (
                "#viewpop",
                "#dock",
                "#opbar",
                "#variant",
                "#home",
                "#tour",
                "#more",
            ):
                if pg.is_visible(other):
                    assert not _overlap(bar, _rect(pg, other)), (
                        other,
                        bar,
                        _rect(pg, other),
                    )
            ctl = _rect(pg, "#controls")
            assert (
                ctl[0] <= bar[0]
                and bar[2] <= ctl[2]
                and ctl[1] <= bar[1]
                and bar[3] <= ctl[3]
            )  # it lives inside the control card
            assert (
                pg.evaluate(
                    "document.querySelector('#play').getBoundingClientRect().height"
                )
                >= 44
            )  # the 2.1 touch target
            assert pg.evaluate("document.documentElement.scrollWidth") <= w
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_variant_change_keeps_the_build_state_rules(
    rsite,
):  # 2.1: test_variant_change_keeps_isolate_rule, the part that exists in the lab (no isolate)
    """Every ply op is roncz-only in the real graph, so widen r30.shear-web to both variants to reach the still-visible path."""
    widened = {}

    def widen(route):
        g = route.fetch().json()
        for o in g["ops"]:
            if o["id"] == "r30.shear-web":
                o["variants"] = ["both"]
        widened.update(g)
        route.fulfill(json=g)

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 1180, "height": 820})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.route("**/graph.json", widen)
            pg.goto(url + "?test=1&q=low&freeze=1")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.click('#opbar button[data-op="r30.shear-web"]')
            _scrub(pg, 2)
            before = pg.evaluate("window.__lab.state()")
            hidden = {n for n, v in before.items() if v == "hidden"}
            assert "canard.shear_web.p3" in hidden and hidden
            pg.click('#variant button[data-variant="gu"]')
            assert (
                pg.evaluate("window.__lab.selected()") == "r30.shear-web"
            )  # still in the bar: the selection stays
            st = pg.evaluate("window.__lab.state()")
            want, _ = _expected_state(
                widened, "gu", "r30.shear-web", pg.evaluate("window.__lab.lay()"), False
            )
            assert {
                k: want[k] for k in st
            } == st  # the same rules, recomputed for the new variant
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("w,h", [(390, 844)])
def test_phone_model_stays_visible_and_scrubber_reachable(
    rsite, w, h
):  # 2.1: test_phone_model_stays_visible_and_scrubber_reachable
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=True)
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&op=r30.shear-web")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.is_visible("#scrubwrap") and pg.is_visible("#dock")
            assert pg.evaluate("document.documentElement.scrollWidth") <= w
            top, bottom = (
                _rect(pg, "#controls")[3],
                min(_rect(pg, "#dock")[1], _rect(pg, "#opbar")[1]),
            )
            assert bottom - top >= 300, (
                top,
                bottom,
            )  # >= 300 px of the canvas is free between the cards
            r = _rect(pg, "#scrub")
            assert r[0] >= 0 and r[2] <= w and r[1] >= 0 and r[3] <= h, r
            hit = pg.evaluate(
                "(() => { const r = document.querySelector('#scrub').getBoundingClientRect(); return document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2).id })()"
            )
            assert hit == "scrub"
            pg.click("#scrub")
            assert pg.evaluate("document.documentElement.scrollWidth") <= w
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _box_js(bl):
    """The cut face at B.L. `bl` in viewport CSS px: the core's model-frame box at Z = -bl, through toWorld and project."""
    return f"""(() => {{
        const L = window.__lab, bx = L.plyBox('canard.core'), z = -{bl}
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9
        for (const x of [bx.min[0], bx.max[0]]) for (const y of [bx.min[1], bx.max[1]]) {{
            const q = L.project(L.toWorld([x, y, z])); x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1])
        }}
        return {{ x0, y0, x1, y1 }}
    }})()"""


def _changed(a, c, tol=24):
    """Pixels that differ by more than `tol` (summed RGB) between two same-size crops."""
    pa, pc = list(a.getdata()), list(c.getdata())
    return sum(
        1 for u, v in zip(pa, pc) if sum(abs(i - j) for i, j in zip(u[:3], v[:3])) > tol
    )


def _cap_pixels_case(pg, w, dpr):
    from PIL import Image

    pg.evaluate("window.__lab.freeze(true)")
    pg.evaluate("window.__lab.select('r30.top-skin')")
    pg.evaluate("window.__lab.advance(3)")
    assert pg.evaluate("window.devicePixelRatio") == dpr
    pg.evaluate("window.__lab.setSection(true, 40)")
    pg.evaluate("window.__lab.advance(3)")  # the cut-edge glow has settled
    r = pg.evaluate(_box_js(40))
    c = pg.eval_on_selector(
        "#gl",
        "e => { const r = e.getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height} }",
    )
    assert (
        r["x1"] - r["x0"] > (20 if w < 500 else 100) and r["y1"] - r["y0"] > 4
    ), r  # the projected cut face has area
    assert (
        -1 <= r["x0"]
        and r["x1"] <= c["w"] + 1
        and -1 <= r["y0"]
        and r["y1"] <= c["h"] + 1
    ), (r, c)
    clip = {
        "x": c["x"] + max(0, r["x0"]),
        "y": c["y"] + max(0, r["y0"]),
        "width": min(c["w"], r["x1"]) - max(0, r["x0"]),
        "height": min(c["h"], r["y1"]) - max(0, r["y0"]),
    }
    import io

    on = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")
    assert on.width >= dpr * clip["width"] - 2, (
        on.size,
        clip,
    )  # screenshot pixels are dpr x CSS pixels
    pg.evaluate("window.__lab.setSection(false, 40)")
    pg.evaluate("window.__lab.advance(3)")
    off = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")
    n, total = _changed(on, off), on.width * on.height
    print("cap pixels changed", n, "of", total, "clip", clip)
    # with the cut on, the cut face shows the layers (foam, plies) in place of the skin the camera otherwise sees there
    assert n > 0.15 * total, (n, total)
    # and the face is not one flat colour: a foam core and several plies show as distinct tones
    colours = {(px[0] // 16, px[1] // 16, px[2] // 16) for px in on.getdata()}
    assert len(colours) >= 6, len(colours)


def test_section_cap_pixels_at_the_cut_face(
    rsite,
):  # 2.1: test_section_cap_pixels_at_the_cut_face
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _cap_pixels_case(pg, 1180, 1)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_section_at_dpr2_projection_and_cap_pixels(
    rsite,
):  # 2.1: test_section_at_dpr2_projection_and_cap_pixels
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(
                viewport={"width": 390, "height": 844}, device_scale_factor=2
            )
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&freeze=1")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            _cap_pixels_case(pg, 390, 2)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_section_control_hidden_without_layup(
    tmp_path, gdir
):  # 2.1: test_section_control_hidden_without_layup
    import cadquery as cq
    from guide.export_glb import export_components

    glb = export_components(
        {"canard.core": cq.Workplane().box(10, 2, 1)}, tmp_path / "m.glb"
    )  # a model with no layup.json beside it
    out = tmp_path / "site"
    build(gdir, out, models=glb, scan_base=None, docs=None)
    s, url = serve(out)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, q="low")
            assert pg.is_hidden("#section") and pg.is_hidden("#scrubwrap")
            assert pg.evaluate("window.__lab.cut().enabled") is False
            b.close()
    finally:
        s.shutdown()


def test_phone_section_readout_one_line_and_controls_reachable(
    rsite,
):  # 2.1: test_phone_section_readout_one_line_and_controls_reachable
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&freeze=1&op=r30.top-skin")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.evaluate(
                "window.__lab.setLay(Number(document.getElementById('scrub').max))"
            )  # all plies
            pg.evaluate(
                "window.__lab.setSection(true, 5)"
            )  # a station every layer reaches: the longest readout this op can produce
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390
            m = pg.evaluate("""(() => { const e = document.querySelector('#ro-layers'), cs = getComputedStyle(e);
                return {scrollWidth: e.scrollWidth, clientWidth: e.clientWidth, textOverflow: cs.textOverflow, whiteSpace: cs.whiteSpace,
                        height: e.getBoundingClientRect().height, lineHeight: parseFloat(cs.lineHeight), title: e.title, text: e.textContent} })()""")
            assert (
                m["scrollWidth"] > m["clientWidth"]
            ), m  # truly truncated, not merely short
            assert m["textOverflow"] == "ellipsis" and m["whiteSpace"] == "nowrap", m
            assert m["height"] <= m["lineHeight"] * 1.3, m  # one line
            assert (
                m["title"] == m["text"] and pg.inner_text("#ro-station") == "B.L. 5"
            ), m  # the full text stays reachable
            pg.evaluate("window.__lab.setSection(true, 40)")
            for sel in ("#scrub", "#section-bl", "#tour"):
                r = _rect(pg, sel)
                assert r[0] >= 0 and r[2] <= 390 and r[1] >= 0 and r[3] <= 844, (sel, r)
                hit = pg.evaluate(
                    """(s) => { const r = document.querySelector(s).getBoundingClientRect();
                    const e = document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2); return !!e && (e.id === s.slice(1) || !!e.closest(s)) }""",
                    sel,
                )
                assert hit, sel
            pg.click("#tour")
            assert pg.get_attribute("#tour", "aria-pressed") == "true"
            pg.click("#tour")
            assert pg.get_attribute("#tour", "aria-pressed") == "false"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_frame_time_at_dpr2_is_reported_not_asserted(
    rsite,
):  # 2.1: test_frame_time_at_dpr2_is_reported_not_asserted
    # INFORMATION ONLY for the owner's iPad walk-through note: the same drag at device_scale_factor=2. The one budget is the 33 ms
    # test above; this run only has to complete and move the cut.
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(
                viewport={"width": 1180, "height": 820}, device_scale_factor=2
            )
            ctx.add_init_script(FRAMES_JS)
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&realframes=1&op=r30.top-skin")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.click("#section-on")
            pg.eval_on_selector(
                "#section-bl",
                "(e) => { e.value = 0; e.dispatchEvent(new Event('input', {bubbles: true})); }",
            )
            pg.wait_for_timeout(500)
            pg.evaluate("window.__frames.start()")
            seen = pg.evaluate(DRAG_JS, 2000)
            d = sorted(pg.evaluate("window.__frames.stop()"))
            print("DPR2 median frame ms", d[len(d) // 2], "n", len(d))
            assert len(d) >= 3 and seen[-1] == pg.evaluate(EFFECTIVE_MAX_JS)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("w,h", [(1180, 820), (390, 844)])
def test_tour_button_is_touch_sized_and_clear_of_other_controls(
    rsite, w, h
):  # 2.1: test_tour_button_is_touch_sized_and_clear_of_other_controls
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=True)
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?test=1&q=low&op=r30.top-skin")
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            t = _rect(pg, "#tour")
            assert pg.is_visible("#tour") and t[3] - t[1] >= 44  # the 2.1 touch target
            assert t[0] >= 0 and t[2] <= w and t[1] >= 0 and t[3] <= h
            assert pg.evaluate("document.documentElement.scrollWidth <= innerWidth")
            pg.click("#more")
            for other in (
                "#variant",
                "#home",
                "#more",
                "#scrubwrap",
                "#section",
                "#viewpop",
                "#dock",
                "#opbar",
            ):
                if pg.is_visible(other):
                    assert not _overlap(t, _rect(pg, other)), (
                        other,
                        t,
                        _rect(pg, other),
                    )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _tour_adv(pg, seconds, dt=0.05):
    for _ in range(round(seconds / dt)):
        pg.evaluate(f"window.__rec.frame({dt}, false)")


@pytest.mark.parametrize("how", ["escape", "second_press"])
def test_stopping_the_tour_leaves_no_animation(
    rsite, how
):  # 2.1: test_stopping_the_tour_leaves_no_animation
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.click("#tour")
            for _ in range(400):
                _tour_adv(pg, 0.25)
                if (
                    pg.evaluate("__lab.selected()") == "r30.shear-web"
                    and pg.evaluate("__lab.playing()")
                    and pg.evaluate("__lab.lay()") >= 2
                ):
                    break
            assert pg.evaluate("__lab.selected()") == "r30.shear-web" and pg.evaluate(
                "__lab.playing()"
            )
            _tour_adv(pg, 0.3)  # mid-flight, mid-lay
            if how == "escape":
                pg.keyboard.press("Escape")
            else:
                pg.click("#tour")
            assert pg.evaluate("__lab.touring()") is False
            snap_js = """(() => { const c = __lab.camera(), r = (x) => Math.round(x * 1e6) / 1e6
                return [c.pos.map(r), c.target.map(r), __lab.lay(), __lab.selected(), __lab.playing(), __lab.cut().bl, __lab.cut().enabled] })()"""
            snap = pg.evaluate(snap_js)
            assert snap[4] is False  # the Play the film pressed stops with it
            _tour_adv(pg, 4.0)
            assert (
                pg.evaluate(snap_js) == snap
            ), how  # nothing keeps moving: camera, plies, selection, cut
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_tour_leaves_the_section_cut_as_the_user_set_it(
    rsite,
):  # 2.1: test_tour_leaves_the_section_cut_and_paths_as_the_user_set_them (the cut half; paths are covered above)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.click('#opbar button[data-op="r30.templates-cores"]')
            pg.click("#section-on")
            pg.eval_on_selector(
                "#section-bl",
                "(e) => { e.value = 40; e.dispatchEvent(new Event('input', {bubbles: true})); }",
            )
            assert pg.evaluate("__lab.cut()").get("bl") == 40
            pg.click("#tour")
            moved = False
            for _ in range(400):  # the tour cuts at its own stations
                _tour_adv(pg, 0.25)
                c = pg.evaluate("__lab.cut()")
                if c["enabled"] and c["bl"] != 40:
                    moved = True
                    break
            assert moved, "the tour never moved the cut"
            pg.keyboard.press("Escape")
            c = pg.evaluate("__lab.cut()")
            assert (
                c["enabled"] is True and c["bl"] == 40
            )  # the person's own cut is back
            assert (
                pg.is_checked("#section-on") and pg.input_value("#section-bl") == "40"
            )
            assert "B.L. 40" in pg.inner_text("#ro-station")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _tour_seen(pg, n_ops):
    """Advance the film and collect the ops it selects, in order, until it has shown n_ops of them (or ends)."""
    seen = []
    for _ in range(4000):
        _tour_adv(pg, 0.25)
        sel = pg.evaluate("__lab.selected()")
        if sel and (not seen or seen[-1] != sel):
            seen.append(sel)
        if len(seen) >= n_ops or not pg.evaluate("__lab.touring()"):
            break
    return seen


def _chapter_ops(g, variant, chapter):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if variant
        in byid[i]["variants"]
        + (["roncz", "gu"] if "both" in byid[i]["variants"] else [])
        and byid[i]["chapter"] == chapter
        and not byid[i]["stub"]
    ]


def test_tour_with_nothing_selected_tours_the_variants_first_chapter(
    rsite,
):  # 2.1: test_tour_with_nothing_selected_tours_the_variants_first_chapter
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.evaluate("__lab.select(null)")
            assert pg.is_visible("#tour") and pg.evaluate("__lab.selected()") is None
            pg.click("#tour")
            assert (
                _tour_seen(pg, 1)[0]
                == "r30.templates-cores"
                == _chapter_ops(g, "roncz", 30)[0]
            )
            pg.click("#tour")
            assert pg.evaluate("__lab.touring()") is False
            pg.click('#variant button[data-variant="gu"]')
            pg.evaluate("__lab.select(null)")
            pg.click("#tour")
            seen = _tour_seen(pg, 2)
            assert (
                seen[0] == "c10.templates-cores" and "c12.align-canard" not in seen
            )  # the first chapter only, not the next one
            pg.click("#tour")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_tour_follows_the_selected_ops_chapter(
    rsite,
):  # 2.1: test_tour_follows_the_selected_ops_chapter
    g = _graph(rsite)
    want = _chapter_ops(g, "gu", 12)
    assert want == ["c12.alignment-pins", "c12.align-canard"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.click('#variant button[data-variant="gu"]')
            pg.click(
                '#subject button[data-subject="fuselage"]'
            )  # chapter 12 (the canard installed) is the fuselage subject's since M2.4; its tour is the same film
            pg.click('#opbar button[data-op="c12.align-canard"]')
            pg.click("#tour")
            assert (
                pg.evaluate("__lab.touring()") is True
                and pg.evaluate("__lab.tourIndex()") == 0
            )
            assert _tour_seen(pg, len(want)) == want  # chapter 12's own ops, in order
            pg.click("#tour")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_tour_from_a_stub_only_chapter_falls_back_to_the_first_real_chapter(
    rsite,
):  # 2.1: test_tour_from_a_stub_only_chapter_falls_back_to_the_first_real_chapter
    g = _graph(rsite)
    want = _chapter_ops(g, "roncz", 30)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.evaluate("__lab.select('c03.layup-skills')")
            assert pg.evaluate("__lab.selected()") == "c03.layup-skills"
            pg.click("#tour")
            assert pg.evaluate("__lab.touring()") is True
            assert _tour_seen(pg, 1)[0] == want[0]  # the first real chapter's film
            pg.click("#tour")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _lose(pg):
    """Force a context loss through WEBGL_lose_context; skip (with the reason) on a build that does not expose it."""
    if not pg.evaluate("window.__lab.loseContext()"):
        pytest.skip(
            f"{_SHARED.get('engine')}: this headless build does not expose WEBGL_lose_context, so a loss cannot be forced (not faked)"
        )
    pg.wait_for_function("window.__lab.contextLost()", timeout=10000)


def test_context_loss_shows_an_overlay_and_a_restore_brings_the_frame_back(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820)
            assert pg.evaluate("window.__lab.contextLost()") is False
            assert pg.locator("#gl-lost").is_hidden()
            _lose(pg)
            assert pg.locator("#gl-lost").is_visible()
            assert pg.locator("#gl-lost-reload").is_visible()
            # the UI cards stay usable while the 3D is paused
            ids = pg.evaluate(
                "[...document.querySelectorAll('#chips button')].map((x, i) => i)"
            )
            assert len(ids) >= 2
            before = pg.evaluate("window.__lab.selected()")
            pg.locator("#chips button").nth(1).click()
            assert pg.evaluate("window.__lab.selected()") != before
            assert pg.evaluate("window.__lab.restoreContext()") is True
            pg.wait_for_function("!window.__lab.contextLost()", timeout=10000)
            deadline = time.time() + 10
            calls = 0
            while time.time() < deadline:
                pg.evaluate("window.__lab.advance(0.05)")
                calls = pg.evaluate("window.__lab.stats().calls")
                if calls > 20 and pg.locator("#gl-lost").is_hidden():
                    break
                time.sleep(0.2)
            assert pg.locator(
                "#gl-lost"
            ).is_hidden(), "the overlay stayed after the restore"
            assert pg.evaluate("window.__lab.contextLost()") is False
            assert calls > 20, f"no frame drawn after the restore (calls={calls})"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_context_loss_reload_button_returns_to_the_same_op(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, _ = _open(p, url, 1180, 820)
            ops = pg.evaluate("[...document.querySelectorAll('#chips button')].length")
            assert ops >= 2
            pg.locator("#chips button").nth(1).click()
            op = pg.evaluate("window.__lab.selected()")
            assert op
            _lose(pg)
            pg.locator("#gl-lost-reload").click()
            pg.wait_for_url(f"**op={op}*", timeout=30000)
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.evaluate("window.__lab.selected()") == op
            assert pg.evaluate("window.__lab.contextLost()") is False
            b.close()
    finally:
        s.shutdown()


def test_context_restore_drops_one_tier_when_auto_is_on_and_remembers_it(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, _ = _open(
                p, url, 1180, 820, q=""
            )  # no ?q=: automatic quality, starts on high on a desktop
            assert pg.evaluate("window.__lab.auto()") is True
            assert pg.evaluate("window.__lab.tier()") == "high"
            _lose(pg)
            assert (
                pg.evaluate("window.__lab.tier()") == "high"
            ), "the tier must not move while the context is lost"
            pg.evaluate("window.__lab.restoreContext()")
            pg.wait_for_function("!window.__lab.contextLost()", timeout=10000)
            assert pg.evaluate("window.__lab.tier()") == "mid"
            assert pg.evaluate("window.__lab.auto()") is True
            for _ in range(20):
                pg.evaluate("window.__lab.advance(0.05)")
                if pg.locator("#gl-lost").is_hidden():
                    break
                time.sleep(0.2)
            assert pg.locator("#gl-lost").is_hidden()
            pg.reload()  # the session remembers: the reload starts a tier down
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.evaluate("window.__lab.tier()") == "mid"
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# The fuselage box (Block 2 M2.2 Task 5): a second subject, chapters 4-6, in its own corner of the shop. The canard stays the default.
# ======================================================================================================================
_BOOK_BOND_ORDER = (
    "front_seat_bkhd",
    "panel",
    "f22",
    "rear_seat_bkhd",
    "firewall",
)  # plans-1980:p40, then F28 (p41)


def _fuse_ops(g, chapters=(4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18)):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if byid[i]["chapter"] in chapters
        and not byid[i]["stub"]
        and ("both" in byid[i]["variants"] or "roncz" in byid[i]["variants"])
    ]


# the all-chapters tour (nothing selected) covers chapters 4-13; chapters 14-17 have their own tour (the ch14-17 tour)
_TOUR_CH = (4, 5, 6, 7, 8, 9, 12, 13)


def _by_chapter(g, ops):
    """The all-chapters tour walks chapter by chapter; the bar is in graph order, which since 2.5 puts f06.bond-firewall after chapter 7."""
    ch = {o["id"]: o["chapter"] for o in g["ops"]}
    return sorted(ops, key=lambda i: ch[i])


def _chips(pg):
    return pg.eval_on_selector_all(
        "#opbar button[data-op]", "els => els.map(e => e.dataset.op)"
    )


def test_fuselage_subject_bar_bond_order_fidelity_labels_cg_and_back_to_the_canard(
    rsite,
):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            assert pg.evaluate("window.__lab.subject()") == "canard"  # the default
            canard_bar = _chips(pg)
            assert canard_bar == _bar_ops(g, "roncz")
            pg.click('#subject button[data-subject="fuselage"]')
            assert pg.evaluate("window.__lab.subject()") == "fuselage"
            assert (
                _chips(pg) == _fuse_ops(g) and len(_chips(pg)) >= 31
            )  # exactly chapters 4-6, graph order, no stubs
            assert pg.is_hidden("#variant")  # the variant only changes the canard
            assert set(pg.evaluate("Object.keys(window.__lab.state())")) == {
                n for p in fz["parts"].values() for n in [p["node"]]
            } | set(fz["nodes"])
            shots = pg.evaluate("window.__lab.fuseShots()")
            assert set(_fuse_ops(g)) <= set(shots) and all(
                shots[o] for o in _fuse_ops(g)
            )  # every op has its own lab shot
            # the ch6 bond ops put their bulkhead in the jig one at a time, in the book's order
            bonds = [o for o in _fuse_ops(g) if o.startswith("f06.bond-")]
            for i, op in enumerate(bonds):
                pg.click(f'#opbar button[data-op="{op}"]')
                pl = pg.evaluate("window.__lab.placement()")
                assert [k for k in _BOOK_BOND_ORDER if pl[k] == "jig"] == list(
                    _BOOK_BOND_ORDER[: i + 1]
                ), (op, pl)
                # the firewall bond moved after the spar fit (2.5, CP25 hint), long after the bottom went on; the bottom is only checked unbonded before it
                assert pl["side_left"] == pl["side_right"] == "jig" and (
                    (pl["bottom"] != "none")
                    if op == "f06.bond-firewall"
                    else (pl["bottom"] == "none")
                )
            pg.click('#opbar button[data-op="f06.bond-panel"]')
            pl = pg.evaluate("window.__lab.placement()")
            assert (
                pl["front_seat_bkhd"] == pl["panel"] == "jig" and pl["f22"] == "table"
            ), pl
            assert (
                pg.evaluate("window.__lab.jigPose()") == "inverted"
            )  # the book builds the box upside down
            # chapter 5: the sides lie flat on the table; chapter 4: the bulkheads are made flat on the table
            pg.click('#opbar button[data-op="f05.inside-layup"]')
            pl = pg.evaluate("window.__lab.placement()")
            assert (
                pl["side_left"] == pl["side_right"] == "table"
                and pl["front_seat_bkhd"] == "table"
            ), pl
            # a fitted (representational) part and every ply on it carry the hatch; a book part never does; the labels say so
            pg.evaluate(
                "window.__lab.select(null)"
            )  # the finished box: every part exists
            pg.evaluate("window.__lab.advance(3)")
            for part, row in fz["parts"].items():
                m = pg.evaluate(f"window.__lab.material('{row['node']}')")
                assert (
                    m["hatch"] == (row["fidelity"] == "representational")
                    and m["fidelity"] == row["fidelity"]
                ), (part, m)
            for node, n in fz["nodes"].items():
                assert pg.evaluate(f"window.__lab.material('{node}').hatch") == (
                    n["fidelity"] == "representational"
                ), node
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            for part, row in fz["parts"].items():
                assert ("fitted shape" in labs[row["node"]]["text"]) == (
                    row["fidelity"] == "representational"
                ), labs[row["node"]]
            assert any(
                labs[r["node"]]["opacity"] > 0.5
                for r in fz["parts"].values()
                if r["fidelity"] == "representational"
            )
            assert pg.is_visible("#t-legend") and "fitted shape" in pg.inner_text(
                "#t-legend"
            )
            # the CG row: the strict ledger has no weight yet, so it says so; the lower bound is never presented as the CG
            assert pg.inner_text("#ro-cg") == "not yet computed"
            sub = pg.inner_text("#ro-cg-sub")
            assert "lower bound" in sub and "not yet computed" not in sub.split("·")[-1]
            # back to the canard: its bar exactly, its meshes, no fuselage rows in the readout
            pg.click('#subject button[data-subject="canard"]')
            assert _chips(pg) == canard_bar
            assert pg.evaluate("window.__lab.subject()") == "canard" and pg.is_visible(
                "#variant"
            )
            assert all(
                k.startswith("canard.")
                for k in pg.evaluate("Object.keys(window.__lab.state())")
            )
            assert pg.is_hidden("#t-cg") and pg.is_hidden("#t-legend")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_subject_choice_survives_a_reload_and_storage_that_throws(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820)
            pg.click('#subject button[data-subject="fuselage"]')
            assert (
                pg.evaluate("window.localStorage.getItem('longez.subject')")
                == "fuselage"
            )
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.evaluate("window.__lab.subject()") == "fuselage" and _chips(
                pg
            ) == _fuse_ops(g)
            assert (
                pg.get_attribute(
                    '#subject button[data-subject="fuselage"]', "aria-pressed"
                )
                == "true"
            )
            assert not errors, errors
            b.close()
            throwing = "Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } })"
            b, pg, errors = _open(p, url, 1180, 820, init=throwing)
            assert (
                pg.evaluate("window.__lab.subject()") == "canard"
            )  # nothing to remember: the default
            pg.click('#subject button[data-subject="fuselage"]')
            assert pg.evaluate("window.__lab.subject()") == "fuselage" and _chips(
                pg
            ) == _fuse_ops(g)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_fuselage_station_cut_opens_the_front_seat_bulkhead_and_lists_its_layers(rsite):
    from PIL import Image

    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    fs = 72.0  # through the front seat bulkhead (it slopes from FS 63.55 at the floor to 81.75 at the top)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f06.bottom-tape"
            )
            assert (
                pg.evaluate("window.__lab.subject()") == "fuselage"
            )  # a chapter 4-6 op in the address opens the fuselage
            pg.evaluate("window.__lab.advance(3)")
            bx = pg.evaluate("window.__lab.plyBox('fuselage.front_seat_bkhd')")
            assert bx["min"][0] < fs < bx["max"][0]
            # look at the station from forward of it (the side the cut removes)
            ctr = [fs, (bx["min"][1] + bx["max"][1]) / 2, 0]
            pos = pg.evaluate(
                f"window.__lab.fuseToWorld([{fs - 70}, {bx['max'][1] + 30}, 30])"
            )
            tgt = pg.evaluate(f"window.__lab.fuseToWorld({ctr})")
            pg.evaluate(f"window.__lab.setCamera({pos}, {tgt})")
            pg.evaluate("window.__lab.advance(0.2)")
            corners = [
                [fs, y, z]
                for y in (bx["min"][1], bx["max"][1])
                for z in (bx["min"][2], bx["max"][2])
            ]
            pts = [
                pg.evaluate(f"window.__lab.project(window.__lab.fuseToWorld({c}))")
                for c in corners
            ]
            x0, x1 = max(0, min(q[0] for q in pts)), min(1180, max(q[0] for q in pts))
            y0, y1 = max(0, min(q[1] for q in pts)), min(820, max(q[1] for q in pts))
            assert x1 - x0 > 60 and y1 - y0 > 30, pts
            clip = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
            off = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")
            pg.evaluate(f"window.__lab.setSection(true, {fs})")
            pg.evaluate("window.__lab.advance(3)")  # the cut-edge glow has settled
            on = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")
            n, total = _changed(on, off), on.width * on.height
            assert n > 0.10 * total, (n, total)
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["enabled"]
                and c["fs"] == fs
                and c["planeConstant"] == pytest.approx(-fs, abs=1e-6)
            )
            assert c["keepsAft"] and c["removesForward"]
            assert "fuselage.front_seat_bkhd" in c["capNodesVisible"] and c[
                "capsVisible"
            ] == len(c["cappedNodes"])
            # the readout lists the layers there, from layup.json alone: the front seat bulkhead's plies that span the station, by cloth
            want = {}
            for n_ in fz["nodes"].values():
                if (
                    n_["part"] == "front_seat_bkhd"
                    and n_["fs_min"] - 1e-3 <= fs <= n_["fs_max"] + 1e-3
                ):
                    want[n_["cloth"]] = want.get(n_["cloth"], 0) + 1
            txt = pg.inner_text("#ro-layers")
            assert (
                "Front seat bulkhead: " + ", ".join(f"{v} {k}" for k, v in want.items())
                in txt
            ), (txt, want)
            assert pg.inner_text("#ro-station") == "FS 72"
            assert (
                fz["parts"]["bottom"]["label"] in txt
            )  # a fitted part is named with its fidelity in the layers too
            pg.evaluate(f"window.__lab.setSection(false, {fs})")
            assert (
                pg.evaluate("window.__lab.cut().capsVisible") == 0
                and pg.inner_text("#ro-station") == "Section off"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_fuselage_tour_button_follows_the_selected_chapter_and_the_ch6_film_ends_on_the_station_cut(
    rsite,
):
    g = _graph(rsite)
    ch = lambda n: [o for o in _fuse_ops(g) if o.startswith(f"f0{n}.")]  # noqa: E731
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.click('#subject button[data-subject="fuselage"]')
            pg.evaluate("__lab.select('%s')" % ch(5)[2])
            pg.click("#tour")  # a chapter 5 op selected: the chapter 5 tour
            assert _tour_seen(pg, len(ch(5))) == ch(5)
            pg.click("#tour")
            pg.evaluate("__lab.select(null)")
            pg.click("#tour")  # nothing selected: all of chapters 4-6
            assert (
                _tour_seen(pg, len(_fuse_ops(g, _TOUR_CH)))
                == _by_chapter(g, _fuse_ops(g, _TOUR_CH))
                and len(_fuse_ops(g, _TOUR_CH)) >= 31
            )
            pg.click("#tour")
            b.close()
            # the recorder's chapter 6 film: the ch6 ops in order, then the cut on inside the front seat bulkhead (FS 63.55-81.75)
            b, pg, errors = _open_rec(p, url, query="&clean=1")
            dur = pg.evaluate("window.__rec.start('fuselage6')")
            assert pg.evaluate("__lab.subject()") == "fuselage" and dur > 30
            seen, active = [], True
            while active:
                active = pg.evaluate("window.__rec.frame(1 / 30, false)")["active"]
                sel = pg.evaluate("__lab.selected()")
                if sel and (not seen or seen[-1] != sel):
                    seen.append(sel)
                if active:
                    c = pg.evaluate(
                        "__lab.cut()"
                    )  # the cut as of the last frame the film was running (the end of the tour puts the person's own cut back)
            assert seen == ch(6)
            assert c["enabled"] is True and 63.55 <= c["bl"] <= 81.75, c
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_chapter_6_and_8_films_close_in_the_state_at_the_end_of_their_chapter_not_the_finished_airplane(
    rsite,
):
    """M2.3 Task 6 fix: with the station cut on, the film shows the box as its chapter leaves it (last op selected, the jig pose),
    never the finished airplane on its gear (no wheel, strut or axle label, no floor pose)."""
    g = _graph(rsite)
    last = {
        6: [o for o in _fuse_ops(g) if o.startswith("f06.")][-1],
        8: [o for o in _fuse_ops(g) if o.startswith("f08.")][-1],
    }
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            for ch, film in ((6, "fuselage6"), (8, "fuselage8")):
                b, pg, errors = _open_rec(p, url, query="&clean=1")
                assert pg.evaluate(f"window.__rec.start('{film}')") > 30
                active, cut_frames = True, 0
                while active:
                    active = pg.evaluate("window.__rec.frame(1 / 15, false)")["active"]
                    if active and pg.evaluate("__lab.cut().enabled"):
                        cut_frames += 1
                        assert pg.evaluate("__lab.selected()") == last[ch]
                        assert pg.evaluate("__lab.jigPose()") != "on-gear"
                        # the fitted gear extrusions are part of the box in both chapters; the wheels, strut, axles and tubes are chapter 9's
                        shown = [
                            x["id"]
                            for x in pg.evaluate("__lab.labels()")
                            if x["id"].startswith("gear.") and x["opacity"] > 0.05
                        ]
                        assert not [i for i in shown if i != "gear.extrusions"], shown
                assert cut_frames > 20 and not errors, (cut_frames, errors)
                b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.2 Task 7 polish: the dock's CG and legend rows fold away, the box turns over in sim time, the cut hides the labels it removes.
# ======================================================================================================================
def test_fuselage_dock_folds_the_cg_and_legend_rows_clear_of_the_box_and_remembers_it(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f06.bottom-tape"
            )
            pg.evaluate("window.__lab.select(null)")
            pg.evaluate("window.__lab.advance(3)")
            # closed by default: one line, the legend still says what the stripes mean, the CG's reasons fold away
            assert pg.get_attribute("#fuse-more", "aria-expanded") == "false"
            assert (
                pg.is_visible("#t-cg")
                and pg.is_visible("#t-legend")
                and pg.is_hidden("#ro-cg-sub")
            )
            assert "fitted shape" in pg.inner_text("#t-legend")
            # the box's forward end (FS 22) is not under the dock at the home view
            dock = _rect(pg, "#dock")
            bx = pg.evaluate("window.__lab.plyBox('fuselage.side_left')")
            for y in (bx["min"][1], bx["max"][1]):
                for z in (-12, 12):
                    x, yy = pg.evaluate(
                        f"window.__lab.project(window.__lab.fuseToWorld([22, {y}, {z}]))"
                    )
                    assert not (dock[0] <= x <= dock[2] and dock[1] <= yy <= dock[3]), (
                        x,
                        yy,
                        dock,
                    )
            pg.click("#fuse-more")
            assert pg.get_attribute(
                "#fuse-more", "aria-expanded"
            ) == "true" and pg.is_visible("#ro-cg-sub")
            assert "lower bound" in pg.inner_text("#ro-cg-sub")
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            assert pg.get_attribute(
                "#fuse-more", "aria-expanded"
            ) == "true" and pg.is_visible("#ro-cg-sub")  # remembered
            assert not errors, errors
            b.close()
            # a phone: the rows are there (closed), one tap opens them; storage that throws only means it is not remembered
            throwing = "Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked') } })"
            b, pg, errors = _open(
                p, url, 390, 844, init=throwing, query="&freeze=1&op=f06.bottom-tape"
            )
            assert (
                pg.is_visible("#t-cg")
                and pg.is_visible("#fuse-more")
                and pg.is_hidden("#ro-cg-sub")
            )
            r = _rect(pg, "#fuse-more")
            assert r[0] >= 0 and r[2] <= 390 and r[3] <= 844
            pg.click("#fuse-more")
            assert pg.is_visible("#ro-cg-sub") and pg.is_visible("#t-legend")
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_fuselage_box_turns_over_in_sim_time_at_the_bottom_bond_and_back(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f06.bottom-glass"
            )
            pg.evaluate("window.__lab.advance(3)")
            q = [70, 5, 9]  # a point of the box, off its turning axis
            inv, up = (
                pg.evaluate(f"window.__lab.fuseRestToWorld({q}, '{k}')")
                for k in ("inverted", "upright")
            )
            assert pg.evaluate(f"window.__lab.fuseToWorld({q})") == pytest.approx(
                inv, abs=1e-6
            )
            pg.evaluate("window.__lab.select('f06.bottom-bond')")
            assert pg.evaluate("window.__lab.jigPose()") == "upright" and pg.evaluate(
                "window.__lab.fuseTurning()"
            )
            pg.evaluate(
                "window.__lab.advance(1.1)"
            )  # partway round: only step() moves it
            mid = pg.evaluate(f"window.__lab.fuseToWorld({q})")

            def far(a, c):
                return max(abs(u - v) for u, v in zip(a, c)) > 0.02  # metres

            assert far(mid, inv) and far(mid, up), (mid, inv, up)
            pg.evaluate("window.__lab.advance(2)")
            assert not pg.evaluate("window.__lab.fuseTurning()")
            assert pg.evaluate(f"window.__lab.fuseToWorld({q})") == pytest.approx(
                up, abs=1e-6
            )  # settles exactly upright
            pg.evaluate(
                "window.__lab.select('f06.bottom-glass')"
            )  # stepping back turns it back over
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "inverted"
            assert pg.evaluate(f"window.__lab.fuseToWorld({q})") == pytest.approx(
                inv, abs=1e-6
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_station_cut_hides_the_labels_of_parts_it_removes_and_labels_the_face_it_opens(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f06.rear-seat-tape"
            )  # every bulkhead is in by now
            pg.evaluate(
                "(() => { const s = window.__lab.fuseShots().fhome; window.__lab.setCamera(s.pos, s.target) })()"
            )
            pg.evaluate("window.__lab.advance(3)")
            ahead = (
                "fuselage.f22",
                "fuselage.f28",
                "fuselage.panel",
            )  # wholly forward of FS 72

            def shown(lab):
                return lab["opacity"] > 0.5 and not lab.get("hidden")

            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert all(labs[k]["opacity"] > 0.5 for k in ahead), [
                labs[k] for k in ahead
            ]  # fitted shapes: labelled whatever the op
            pg.evaluate("window.__lab.setSection(true, 72)")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert all(labs[k]["opacity"] < 0.05 for k in ahead), [
                labs[k] for k in ahead
            ]
            fs = labs["fuselage.front_seat_bkhd"]
            assert (
                shown(fs)
                and not fs["collapsed"]
                and fs["text"] == "Front seat bulkhead"
            ), fs
            pg.evaluate("window.__lab.setSection(false, 72)")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert all(labs[k]["opacity"] > 0.5 for k in ahead), [
                labs[k] for k in ahead
            ]
            for k in (
                ahead
            ):  # a fitted part's label keeps its words whenever it is shown in full
                assert "fitted shape" in labs[k]["text"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("film", ["canard", "fuselage6"])
def test_recorder_url_exposes_rec_and_both_films_start(rsite, film):
    """The recorder opens the page with a bare ?rec=1 (no test hooks, the high tier, no frame loop) and waits for window.__rec.
    It must appear within a bound; each film must report a positive length and step a frame."""
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 960, "height": 540})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?rec=1")
            pg.wait_for_function(
                "typeof window.__rec === 'object'", timeout=30000, polling=250
            )
            dur = pg.evaluate(f"window.__rec.start('{film}')")
            assert isinstance(dur, (int, float)) and dur > 0
            r = pg.evaluate("window.__rec.frame(1 / 60, true)")
            assert r["active"] is True
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_recorder_chapter_9_film_starts_and_steps_a_frame(rsite):
    """The recorder's fuselage9 film (M2.3 Task 6): a bare ?rec=1 page reports a positive length, then steps an active frame."""
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            pg = b.new_page(viewport={"width": 960, "height": 540})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "?rec=1")
            pg.wait_for_function(
                "typeof window.__rec === 'object'", timeout=30000, polling=250
            )
            dur = pg.evaluate("window.__rec.start('fuselage9')")
            assert isinstance(dur, (int, float)) and dur > 0
            r = pg.evaluate("window.__rec.frame(1 / 60, true)")
            assert r["active"] is True
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.3 Task 5: chapters 7-9 in the lab. The 45 degree rolls, the gear table, the gear and fitted-shape stripes, the CG and
# ground rows, and the station cut through the skins and the roll-over.
# ======================================================================================================================
def _up(pg, q, n):
    """World 'up' component of the box-frame direction n at box-frame point q (unit-free): where the box is now."""
    a = pg.evaluate(f"window.__lab.fuseToWorld({q})")
    b = pg.evaluate(f"window.__lab.fuseToWorld({[q[i] + n[i] for i in range(3)]})")
    d = [b[i] - a[i] for i in range(3)]
    return d[1] / max(1e-9, sum(x * x for x in d) ** 0.5)


def test_ch7_skin_right_rolls_the_box_right_side_up_in_sim_time_then_through_to_the_left_and_back(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f07.belt-insert"
            )
            assert (
                pg.evaluate("window.__lab.subject()") == "fuselage"
            )  # a chapter 7 op in the address opens the fuselage
            pg.evaluate("window.__lab.advance(3)")
            q_right, q_left = (
                [70, -5, -12.3],
                [70, -5, 12.3],
            )  # on the right (B.L. > 0 is the box frame's z < 0) and left sides
            assert pg.evaluate("window.__lab.jigPose()") == "upright"
            up0 = pg.evaluate(f"window.__lab.fuseToWorld({q_right})")
            pg.evaluate("window.__lab.select('f07.skin-right')")
            assert pg.evaluate(
                "window.__lab.jigPose()"
            ) == "bank-left-45" and pg.evaluate("window.__lab.fuseTurning()")
            assert pg.evaluate(f"window.__lab.fuseToWorld({q_right})") == pytest.approx(
                up0, abs=1e-6
            )  # only step() moves it
            pg.evaluate(
                "window.__lab.advance(0.9)"
            )  # a quarter of the way round (0.6 s delay, then 135 degrees over 1 s)
            mid = _up(pg, q_right, [0, 0, -1])
            pg.evaluate("window.__lab.advance(2)")
            assert not pg.evaluate("window.__lab.fuseTurning()")
            # the box is rolled 135 degrees (captain's reading of p46's "45 degrees of left bank"): the right side's AND the bottom's
            # outward normals point up 45 degrees, the left side's down; the right side is higher
            assert _up(pg, q_right, [0, 0, -1]) == pytest.approx(0.7071, abs=0.01)
            assert _up(pg, q_right, [0, -1, 0]) == pytest.approx(0.7071, abs=0.01)
            assert _up(pg, q_left, [0, 0, 1]) == pytest.approx(-0.7071, abs=0.01)
            assert 0.05 < mid < 0.7, mid  # partway round when it was sampled
            yr, yl = (
                pg.evaluate(f"window.__lab.fuseToWorld({q})")[1]
                for q in (q_right, q_left)
            )
            assert yr > yl + 0.3, (yr, yl)  # metres
            assert pg.evaluate(f"window.__lab.fuseToWorld({q_right})") == pytest.approx(
                pg.evaluate(f"window.__lab.fuseRestToWorld({q_right}, 'bank-left-45')"),
                abs=1e-6,
            )
            # the right skin's plies lie on the right side and the bottom only
            fz = _graph(rsite)["layup"]["fuselage"]
            parts = {
                n["part"] for n in fz["nodes"].values() if n["op"] == "f07.skin-right"
            }
            assert parts == {"side_right", "bottom"}, parts
            # through to 45 degrees of right bank for the left skin
            pg.evaluate("window.__lab.select('f07.skin-left')")
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "bank-right-45"
            assert _up(pg, q_left, [0, 0, 1]) == pytest.approx(0.7071, abs=0.01)
            assert _up(pg, q_left, [0, -1, 0]) == pytest.approx(0.7071, abs=0.01)
            # stepping back puts it right side up again, exactly
            pg.evaluate("window.__lab.select('f07.belt-insert')")
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "upright"
            assert pg.evaluate(f"window.__lab.fuseToWorld({q_right})") == pytest.approx(
                up0, abs=1e-6
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ch9_position_gear_inverts_the_box_with_the_datum_boards_and_marks_the_axle_at_fs_110_5(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f09.jig-blocks"
            )
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "upright"
            pl = pg.evaluate("window.__lab.placement()")
            assert (
                pl["strut"] == "table"
                and pl["jig_blocks"] == "jig"
                and pl["datum_board"] == "none"
            ), pl  # the strut waits on the table
            assert not pg.evaluate("window.__lab.gearMarks()")["shown"]
            top, bottom = (
                [80, 5.6, 0],
                [80, -14.9, 0],
            )  # the longeron tops (W.L. 23) and the box's floor at FS 80
            pg.evaluate("window.__lab.select('f09.position-gear')")
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "gear-table"
            yt, yb = (
                pg.evaluate(f"window.__lab.fuseToWorld({q})")[1] for q in (top, bottom)
            )
            assert yt < yb - 0.3, (
                yt,
                yb,
            )  # upside down: the longeron tops below the floor
            assert _up(pg, [80, 0, 0], [0, 1, 0]) == pytest.approx(
                -1, abs=1e-6
            )  # level on the longerons, not rolled
            pl = pg.evaluate("window.__lab.placement()")
            assert pl["datum_board"] == pl["strut"] == pl["jig_blocks"] == "jig", pl
            gm = pg.evaluate("window.__lab.gearMarks()")
            assert gm["shown"] and gm["axleFs"] == 110.5 and gm["boardFs"] == 125.5
            assert (
                gm["dimText"] == "15 in"
                and gm["axleText"] == "Axle C.L. F.S. 110.5 (book)"
            )
            assert gm["axleModel"][0] == pytest.approx(110.5) and gm["dimModel"][
                0
            ] == pytest.approx((110.5 + 125.5) / 2)
            # the mark is where the axle goes (it is fitted at axles-brakes): inside the axles' box in the box's frame, on the right
            ab = pg.evaluate("window.__lab.plyBox('gear.axles')")
            assert all(
                ab["min"][i] - 0.5 <= gm["axleModel"][i] <= ab["max"][i] + 0.5
                for i in range(3)
            ), (ab, gm["axleModel"])
            assert (
                gm["axleModel"][2] < -26.75
            )  # outboard of the right datum board (B.L. 26.75; the box frame's z is -B.L.)
            # and it turned over with the box: the axle line is above the box's floor now
            assert (
                gm["axleWorld"][1]
                > pg.evaluate(f"window.__lab.fuseToWorld({bottom})")[1] + 0.3
            )
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert (
                labs["mark.dim"]["text"] == "15 in"
                and labs["mark.dim"]["opacity"] > 0.5
            )
            assert (
                labs["mark.axle"]["text"] == "Axle C.L. F.S. 110.5 (book)"
                and labs["mark.axle"]["opacity"] > 0.5
            )
            # it stays upside down to the end of the chapter, then (the finished box) right side up on its gear with the boards and marks gone
            for op in ("f09.tab-layup", "f09.axles-brakes", "f09.brake-lines"):
                pg.evaluate(f"window.__lab.select('{op}')")
                assert pg.evaluate("window.__lab.jigPose()") == "gear-table", op
            pg.evaluate("window.__lab.select(null)")
            pg.evaluate("window.__lab.advance(3)")
            assert (
                pg.evaluate("window.__lab.jigPose()") == "on-gear"
            )  # on its own feet (the next test checks where)
            assert (
                pg.evaluate("window.__lab.placement()")["datum_board"] == "none"
                and not pg.evaluate("window.__lab.gearMarks()")["shown"]
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_gear_and_the_ch7_9_fitted_shapes_are_striped_and_book_or_derived_parts_never_are(
    rsite,
):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f09.axles-brakes"
            )
            pg.evaluate("window.__lab.advance(3)")
            fitted = (
                "strut",
                "extrusions",
                "gear_tubes",
                "axles",
                "jig_blocks",
                "carved_corners",
                "canard_cutout",
            )
            for part in fitted:
                m = pg.evaluate(f"window.__lab.material('{fz['parts'][part]['node']}')")
                assert m["hatch"] and m["fidelity"] == "representational", (part, m)
            for part in (
                "rollover",
                "rollover_inserts",
                "step",
                "belt_attach",
                "belt_insert",
                "datum_board",
                "side_left",
                "side_right",
                "front_seat_bkhd",
            ):
                m = pg.evaluate(f"window.__lab.material('{fz['parts'][part]['node']}')")
                assert not m["hatch"] and m["fidelity"] in ("book", "derived"), (
                    part,
                    m,
                )
            for node, n in fz[
                "nodes"
            ].items():  # the skins and the roll-over glass are on book or derived parts: never striped
                if n["op"].startswith(("f07.", "f08.")):
                    assert pg.evaluate(f"window.__lab.material('{node}').hatch") == (
                        n["fidelity"] == "representational"
                    ), node
            # what is on screen says so in its label: the gear's fitted parts read "(fitted shape)", the datum boards do not
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            for part in ("strut", "extrusions", "gear_tubes", "axles"):
                lab = labs[fz["parts"][part]["node"]]
                assert lab["text"].endswith("(fitted shape)"), lab
            assert any(
                labs[fz["parts"][x]["node"]]["opacity"] > 0.5
                for x in ("strut", "axles")
            )
            assert "fitted shape" not in labs["gear.datum_board"]["text"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_readout_lists_the_gear_rows_and_the_ground_note_with_no_tip_back_or_tip_over_number(
    rsite,
):
    import re

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f09.position-gear"
            )
            assert pg.is_hidden(
                "#t-ground"
            )  # closed by default: the dock stays one line
            pg.click("#fuse-more")
            assert pg.is_visible("#t-ground") and pg.is_visible("#ro-cg-sub")
            sub = pg.inner_text("#ro-cg-sub")
            assert pg.inner_text("#ro-cg") == "not yet computed"
            last = sub.split("·")[-1]
            assert (
                "lower bound" in last
                and "24.8 lb of gear (main and nose struts)" in last
            ), sub
            assert (
                "Wheels and brakes: excluded, no source" in sub and "20.2" not in sub
            ), sub
            assert pg.inner_text("#ro-ground") == "Main axle F.S. 110.5 (book)"
            gsub = pg.inner_text("#ro-ground-sub")
            assert "12° tip-back line" in gsub, gsub
            segs = {x.strip().split(":")[0]: x.strip() for x in gsub.split("·")}
            assert segs["tip-back check"].startswith(
                "tip-back check: not yet computed"
            ) and not re.search(r"\d", segs["tip-back check"]), gsub
            assert segs["tip-over check"].startswith(
                "tip-over check: not yet computed"
            ) and not re.search(r"\d", segs["tip-over check"]), gsub
            assert (
                pg.evaluate("window.__lab.ground()")["value"]
                == "Main axle F.S. 110.5 (book)"
            )
            # the track has no source: no number next to it anywhere on the page
            assert not re.search(r"track\D{0,20}\d", pg.inner_text("body"), re.I)
            pg.click(
                '#subject button[data-subject="canard"]'
            )  # the canard has no ground note
            assert pg.is_hidden("#t-ground")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_station_cut_opens_the_roll_over_at_fs_80_the_skins_at_fs_72_and_the_gear(
    rsite,
):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1&op=f08.step")
            pg.evaluate("window.__lab.advance(3)")
            pg.evaluate("window.__lab.setSection(true, 80)")
            pg.evaluate("window.__lab.advance(3)")
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["enabled"] and c["fs"] == 80 and c["keepsAft"] and c["removesForward"]
            )
            assert "fuselage.rollover" in c["capNodesVisible"], c["capNodesVisible"]
            ro_plies = sorted(
                k
                for k, n in fz["nodes"].items()
                if n["part"] == "rollover"
                and n["fs_min"] - 1e-3 <= 80 <= n["fs_max"] + 1e-3
            )
            assert ro_plies and set(ro_plies) <= set(c["capNodesVisible"]), (
                ro_plies,
                c["capNodesVisible"],
            )
            assert c["capsVisible"] == len(c["cappedNodes"])
            assert f"Roll-over box: {len(ro_plies)} BID" in pg.inner_text("#ro-layers")
            # FS 72: the skins are thin caps over the sides (every chapter 7 ply on a side spanning 72 is cut there)
            pg.evaluate("window.__lab.setSection(true, 72)")
            pg.evaluate("window.__lab.advance(3)")
            c = pg.evaluate("window.__lab.cut()")
            skins = [
                k
                for k, n in fz["nodes"].items()
                if n["op"].startswith("f07.skin")
                and n["part"].startswith("side_")
                and n["fs_min"] - 1e-3 <= 72 <= n["fs_max"] + 1e-3
            ]
            assert len(skins) >= 4 and set(skins) <= set(c["capNodesVisible"]), (
                skins,
                c["capNodesVisible"],
            )
            assert "Right side: " in pg.inner_text("#ro-layers")
            # the gear is cut too: through the strut's flat and the extrusions at FS 117
            pg.evaluate("window.__lab.select('f09.axles-brakes')")
            pg.evaluate("window.__lab.setSection(true, 117)")
            pg.evaluate("window.__lab.advance(3)")
            c = pg.evaluate("window.__lab.cut()")
            assert {"gear.strut", "gear.extrusions"} <= set(c["capNodesVisible"]), c[
                "capNodesVisible"
            ]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _boxes_overlap(a, b):
    return all(a[0][i] < b[1][i] and b[0][i] < a[1][i] for i in range(3))


def test_the_finished_box_stands_on_its_gear_on_the_floor_clear_of_the_bench(rsite):
    import re

    inch = 0.0254
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f09.brake-lines"
            )
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.jigPose()") == "gear-table"
            pg.evaluate(
                "window.__lab.select(null)"
            )  # the finished box: after chapter 9 the book sets it on its own feet
            pg.evaluate("window.__lab.advance(4)")
            assert pg.evaluate("window.__lab.jigPose()") == "on-gear"
            f = pg.evaluate("window.__lab.fuseFloor()")
            gear, bench = f["gear"], f["bench"]
            fz = _graph(rsite)["layup"]["fuselage"]["parts"]
            assert {
                fz[k]["node"] for k in ("strut", "axles", "extrusions", "gear_tubes")
            } | {"gear.wheels"} <= set(gear), sorted(gear)
            # no gear part's world box meets the jig bench's (top, legs and blocks)
            for name, bx in gear.items():
                assert not _boxes_overlap(bx, bench), (name, bx, bench)
            # it stands on the floor plane (y = 0), on its wheels
            low = min(bx[0][1] for bx in gear.values())
            assert abs(low) <= 0.5 * inch, low
            assert gear["gear.wheels"][0][1] == pytest.approx(low, abs=1e-9)
            assert all(
                bx[0][1] > low + 2 * inch
                for k, bx in gear.items()
                if k != "gear.wheels"
            )  # the axles and legs are up off it
            # and the whole box with it: nothing of the box under the floor or in the bench
            for node in (
                "fuselage.side_left",
                "fuselage.side_right",
                "fuselage.bottom",
                "fuselage.rollover",
                "fuselage.firewall",
            ):
                mn, mx = pg.evaluate(f"window.__lab.meshBox('{node}')")
                assert mn[1] > 0 and not _boxes_overlap([mn, mx], bench), (node, mn, mx)
            assert f["noseStand"]  # its forward end on a stand: no nose gear yet
            # the wheels are fitted: striped and labelled so; the home shot frames them, and no track number is printed anywhere
            m = pg.evaluate("window.__lab.material('gear.wheels')")
            assert m["hatch"] and m["fidelity"] == "representational", m
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert (
                labs["gear.wheels"]["text"] == "Main gear and wheels (fitted shape)"
                and labs["gear.wheels"]["opacity"] > 0.5
            ), labs["gear.wheels"]
            for c in [gear["gear.wheels"][0], gear["gear.wheels"][1]]:
                x, y = pg.evaluate(f"window.__lab.project({c})")
                assert 0 <= x <= 1180 and 0 <= y <= 820, (c, x, y)
            assert not re.search(r"track\D{0,20}\d", pg.inner_text("body"), re.I)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_home_view_names_the_finished_box_by_family_in_ten_labels_or_fewer(rsite):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1180, 820, query="&freeze=1&op=f09.brake-lines"
            )
            pg.evaluate("window.__lab.select(null)")
            pg.evaluate("window.__lab.advance(4)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            on = [k for k, x in labs.items() if x["opacity"] > 0.5]
            assert len(on) <= 10, on
            assert (
                fz["parts"]["rollover"]["node"] in on
                and fz["parts"]["rollover_inserts"]["node"] not in on
            )  # one roll-over label
            gear = [
                k
                for k in on
                if k.startswith("gear.")
                or k in {fz["parts"][x]["node"] for x in ("extrusions", "gear_tubes")}
            ]
            assert gear == ["gear.wheels"], gear  # one gear label
            # a fitted part whose label waits for its op is still drawn striped
            for part in (
                "strut",
                "axles",
                "extrusions",
                "gear_tubes",
                "carved_corners",
            ):
                node = fz["parts"][part]["node"]
                assert (
                    node not in on
                    and pg.evaluate(f"window.__lab.material('{node}')")["hatch"]
                ), part
                assert (
                    pg.evaluate(f"window.__lab.meshBox('{node}')") is not None
                ), part  # drawn
            # with an op selected the parts keep their own labels (the axles at the axles op)
            pg.evaluate("window.__lab.select('f09.axles-brakes')")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert (
                labs["gear.axles"]["opacity"] > 0.5
                and labs["gear.wheels"]["opacity"] < 0.05
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.4 Task 5: chapters 11-13 in the lab. The elevators (canard subject, chapter 11), the canard and elevators installed on the
# airplane (fuselage subject, chapters 12-13), the nose and the nose gear (chapter 13).
# ======================================================================================================================
def _run(pg, seconds, dt=0.1):
    pg.evaluate(
        f"(() => {{ for (let i = 0; i < {int(round(seconds / dt))}; i++) window.__lab.advance({dt}) }})()"
    )


def _roncz_order(g):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if "roncz" in byid[i]["variants"] or "both" in byid[i]["variants"]
    ], byid


def _first_ops(g):
    order, byid = _roncz_order(g)
    first = {}
    for o in order:
        for c in byid[o]["components"]:
            first.setdefault(c, o)
    return order, byid, first


def _elev_component(name):
    import re

    name = name.replace("~core", "")
    return (
        name
        if name in ("elevator.right", "elevator.left")
        else re.sub(r"\.(left|right)$", "", name)
    )


def _to_fuselage(pg):
    pg.click('#subject button[data-subject="fuselage"]')
    assert pg.evaluate("window.__lab.subject()") == "fuselage"


def test_ch11_elevators_appear_on_their_ops_are_fitted_shapes_and_never_show_on_a_chapter_30_op(
    rsite,
):
    g = _graph(rsite)
    order, byid, first = _first_ops(g)
    ex = g["layup"]["fuselage"]["extras"]["elevators"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860, query="&freeze=1")
            ch11 = [
                o for o in order if byid[o]["chapter"] == 11 and not byid[o]["stub"]
            ]
            assert len(ch11) >= 15
            for op in ch11:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.2)
                st = pg.evaluate("window.__lab.stateAll()")
                names = [n for n in st if n.startswith("elevator.")]
                assert names and not any(
                    ".left" in n for n in names
                ), names  # the canard subject is the right half
                for n in names:
                    i = order.index(first[_elev_component(n)])
                    want = (
                        "hidden"
                        if i > order.index(op)
                        else "current"
                        if i == order.index(op)
                        else "built"
                    )
                    assert st[n] == want, (op, n, st[n], want)
            # the chapter 30 ops keep the canard alone, as before: the ones that follow chapter 11 in the book too
            for op in ("r30.top-skin", "r30.install-pins", "r30.align-canard", None):
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.2)
                st = pg.evaluate("window.__lab.stateAll()")
                assert {st[n] for n in st if n.startswith("elevator.")} == {
                    "hidden"
                }, op
                assert pg.evaluate("window.__lab.elevators()")["boxes"] == {}, op
            # every elevator part is a fitted shape: striped, said so in its label
            pg.evaluate("window.__lab.select('r30.elev-mass-balance')")
            _run(pg, 4)
            st = pg.evaluate("window.__lab.stateAll()")
            for n in [n for n in st if n.startswith("elevator.")]:
                m = pg.evaluate(f"window.__lab.material('{n}')")
                assert m["hatch"] and m["fidelity"] == "representational", (n, m)
            labs = {
                x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")
            }  # labels() keeps the canard's own set
            for cid, row in ex["parts"].items():
                if cid in ("elevator.left",):
                    continue
                assert (
                    labs[cid]["text"] == row["label"] and "fitted" in labs[cid]["text"]
                ), (
                    cid,
                    labs[cid],
                )  # (the hinges and the tube say it in their own one parenthetical)
            assert any(
                labs[c]["opacity"] > 0.5
                for c in ("elevator.right", "elevator.tube", "elevator.balance_weight")
            )
            # bond cores: the tube held clear of the bench on its two jigs, the cores bare (no skin yet); the skin op skins them
            pg.evaluate("window.__lab.select('r30.elev-bond-cores')")
            _run(pg, 4)
            e = pg.evaluate("window.__lab.elevators()")
            assert (
                e["mode"] == "apart" and e["jigs"] and e["slide"] == pytest.approx(10.0)
            )
            assert (
                "elevator.tube.right" in e["boxes"]
                and "elevator.right~core" in e["boxes"]
                and "elevator.right" not in e["boxes"]
            )
            assert "elevator.hinges.right" not in e["boxes"]
            assert pg.evaluate("window.__lab.material('elevator.right~core')")["hatch"]
            pg.evaluate("window.__lab.select('r30.elev-skin-bottom')")
            _run(pg, 0.5)
            e = pg.evaluate("window.__lab.elevators()")
            assert (
                "elevator.right" in e["boxes"]
                and "elevator.right~core" not in e["boxes"]
            )
            # the hinges join the tube and the elevators come home onto the canard
            pg.evaluate("window.__lab.select('r30.elev-hinges')")
            _run(pg, 6)
            e = pg.evaluate("window.__lab.elevators()")
            assert (
                e["mode"] == "none"
                and e["slide"] == 0
                and not e["jigs"]
                and "elevator.hinges.right" in e["boxes"]
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ch11_travel_checks_run_30_down_then_15_up_with_the_live_readout(rsite):
    from core import elevators_kin as ek

    hinge = _graph(rsite)["layup"]["fuselage"]["extras"]["elevators"]["hinge_xz"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860, query="&freeze=1")
            pg.evaluate(
                "window.__lab.select('r30.top-skin')"
            )  # an upright canard: the travel op does not turn it over, so its boxes read steady
            _run(pg, 3)
            for op in ("r30.elev-travel-check", "r30.elev-uptravel-test"):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 1.0)
                box0 = pg.evaluate("window.__lab.meshBox('elevator.tube.right')")
                assert (
                    pg.evaluate("window.__lab.kin()")["value"] == "Neutral"
                    and pg.evaluate("window.__lab.elevators()")["mode"] == "travel"
                )
                degs, texts, boxes = [], [], {}
                for _ in range(80):
                    _run(pg, 0.1)
                    e = pg.evaluate("window.__lab.elevators()")
                    degs.append(e["degDown"])
                    texts.append(pg.evaluate("window.__lab.kin()")["value"])
                    if abs(e["degDown"] - 30) < 1e-6:
                        boxes[30.0] = pg.evaluate(
                            "window.__lab.meshBox('elevator.tube.right')"
                        )
                    if abs(e["degDown"] + 15) < 1e-6:
                        boxes[-15.0] = pg.evaluate(
                            "window.__lab.meshBox('elevator.tube.right')"
                        )
                assert max(degs) == pytest.approx(30.0) and min(degs) == pytest.approx(
                    -15.0
                )
                assert degs.index(max(degs)) < degs.index(
                    min(degs)
                )  # 30 down first, then 15 up
                assert "Down 30.0 deg  (limit 30)" in texts
                assert texts[-1] == "Up 15.0 deg  (target 15, floor 12.5)"
                assert pg.text_content("#ro-kin") == texts[-1] and pg.is_visible(
                    "#t-kin"
                )  # the live row on the page, in the plan's words
                assert pg.inner_text("#ro-kin-label") == "Elevator travel"
                assert (
                    ek.classify_up_travel(15.0) == "target"
                    and ek.classify_up_travel(12.5) == "floor only"
                )
                # the part really turns about the hinge line, by the kernel's rotation: the torque tube's centre (a cylinder along the span
                # turns into itself, so its box centre is a point of the elevator) moves where core.elevators_kin.rotate_about_hinge puts it
                inch = 0.0254
                tb = pg.evaluate(
                    "window.__lab.plyBox('elevator.tube.right')"
                )  # the tube's own frame (inches: x chord, y up)
                c0 = (
                    (tb["min"][0] + tb["max"][0]) / 2,
                    (tb["min"][1] + tb["max"][1]) / 2,
                )
                for deg, bx in boxes.items():
                    ex_, ez_ = ek.rotate_about_hinge(c0, tuple(hinge), deg)
                    got = (
                        (bx[0][0] + bx[1][0]) / 2 - (box0[0][0] + box0[1][0]) / 2,
                        (bx[0][1] + bx[1][1]) / 2 - (box0[0][1] + box0[1][1]) / 2,
                    )
                    assert got[0] == pytest.approx(
                        (ex_ - c0[0]) * inch, abs=2e-6
                    ) and got[1] == pytest.approx((ez_ - c0[1]) * inch, abs=2e-6), (
                        deg,
                        got,
                        ex_ - c0[0],
                        ez_ - c0[1],
                    )
                assert set(boxes) == {30.0, -15.0}
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ch11_balance_check_hangs_each_elevator_nose_down_with_the_cg_labelled_illustrative(
    rsite,
):
    from core import elevators_kin as ek

    g = _graph(rsite)
    ex = g["layup"]["fuselage"]["extras"]["elevators"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860, query="&freeze=1")
            pg.evaluate("window.__lab.select('r30.elev-balance-check')")
            _run(pg, 0.5)
            assert pg.evaluate("window.__lab.elevators()")["degDown"] == 0
            _run(pg, 15)
            e = pg.evaluate("window.__lab.elevators()")
            want = ek.hang_pitch_deg(
                ex["hang_cg"]["dx"], ex["hang_cg"]["dz"]
            )  # the kernel's pitch for the fitted CG
            assert e["mode"] == "hang" and e["noseDown"] and 0 < e["hangPitch"] < 180
            assert e["hangPitch"] == pytest.approx(want, abs=1e-9) and e[
                "degDown"
            ] == pytest.approx(-want, abs=0.01)
            assert e["jigs"] and e["slide"] == pytest.approx(
                10.0
            )  # hung clear of the canard on its hinge line
            k = pg.evaluate("window.__lab.kin()")
            assert (
                k["label"] == "Elevator hang"
                and k["value"] == f"Hangs nose down, about {round(want)} deg"
                and "illustrative CG: masses not sourced" in k["sub"]
            ), k  # M2.4 review 9: rounded; the note is the sub-line
            # nose down in the world: the leading-edge weights hang below the hinge line, the trailing edge goes up
            hx, hz = ex["hinge_xz"]
            hinge_y = pg.evaluate(f"window.__lab.toWorld([{hx}, {hz}, -30])")[1]
            w = pg.evaluate("window.__lab.meshBox('elevator.balance_weight.right')")
            body = pg.evaluate("window.__lab.meshBox('elevator.right')")
            assert (w[0][1] + w[1][1]) / 2 < hinge_y - 0.5 * 0.0254, (w, hinge_y)
            assert (
                body[1][1] > hinge_y + 1.0 * 0.0254
            )  # the trailing edge swung up over the hinge line
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---- M2.4 fix 1: the elevators are SEEN. The canard's core and skins used to fill the space the elevators sit in, so the hinge, travel and
# pocket ops showed a canard with labels pointing at nothing. These tests judge the on-screen pixels, not transforms and states.
def _bare_view(pg):
    """Only the 3D view: the cards, the bar, the labels and the load-path glow are off, so the pixels in a crop are the model's."""
    _display(pg)
    pg.uncheck("#paths-on")
    pg.click("#more")
    pg.add_style_tag(
        content="#controls,#dock,#opbar,#labels,#status,#viewpop{visibility:hidden !important}"
    )


def _screen_clip(pg, boxes, w, h, pad=4):
    """The crop (screen pixels) that holds every world box in `boxes` (metres), clamped to the viewport."""
    pts = [
        pg.evaluate("(p) => window.__lab.project(p)", [x, y, z])
        for bx in boxes
        for x in (bx[0][0], bx[1][0])
        for y in (bx[0][1], bx[1][1])
        for z in (bx[0][2], bx[1][2])
    ]
    x0, x1 = max(0, min(q[0] for q in pts) - pad), min(w, max(q[0] for q in pts) + pad)
    y0, y1 = max(0, min(q[1] for q in pts) - pad), min(h, max(q[1] for q in pts) + pad)
    assert x1 - x0 > 40 and y1 - y0 > 20, pts
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def _look_at(pg, box, dist, d=(0.55, 0.62, 0.55)):
    """Aim the camera at the middle of a world box from `dist` metres along direction `d` (x aft, y up, z toward the root side)."""
    n = sum(v * v for v in d) ** 0.5
    c = [(box[0][i] + box[1][i]) / 2 for i in range(3)]
    pos = [c[i] + dist * d[i] / n for i in range(3)]
    pg.evaluate(f"window.__lab.setCamera({pos}, {c})")


def _shot_clip(pg, clip):
    from PIL import Image

    return Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")


def _pair(p, url, hide, query="", w=1180, h=820):
    """Two pages on the same site: the lab as it is, and the lab with the elevators left out of the scene (?hide=, a debugging aid that keeps the
    cove as it is). What differs between their frames is the elevator's own pixels: no colour guessing, no stripe classifier."""
    b1, pg, e1 = _open(p, url, w, h, query="&freeze=1" + query)
    b2, pgh, e2 = _open(p, url, w, h, query=f"&freeze=1&hide={hide}" + query)
    for g in (pg, pgh):
        _bare_view(g)
    return (b1, b2), pg, pgh, e1 + e2


def _elevator_pixels(pg, pgh, clip, tol=45):
    """The mask (list of 0/1 per pixel of `clip`) of where the elevator is on screen: pixels that differ between the two pages' frames."""
    on, off = _shot_clip(pg, clip), _shot_clip(pgh, clip)
    return [
        1 if sum(abs(i - j) for i, j in zip(u, v)) > tol else 0
        for u, v in zip(on.getdata(), off.getdata())
    ]


def _orange(img_pixels, mask):
    """How many of the masked pixels read amber (the fitted-shape stripe, mixed into the part's colour): red over green over blue, clearly warm."""
    return sum(
        1 for (r, g, b), m in zip(img_pixels, mask) if m and r > g > b and r - b >= 45
    )


def test_ch11_travel_check_changes_the_pixels_of_the_elevator_on_screen_between_30_down_and_15_up(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            bs, pg, pgh, errors = _pair(p, url, "elevator.")
            masks = {}
            for g in (pg, pgh):
                g.evaluate(
                    "window.__lab.select('r30.top-skin')"
                )  # an upright canard: the travel op does not turn it over
                _run(g, 3)
                g.evaluate("window.__lab.select('r30.elev-travel-check')")
                for _ in range(
                    40
                ):  # the op's own camera flight (1.8 s) ends before the elevator reaches 30 down (2.4 s): then take the camera
                    _run(g, 0.1)
                    if not g.evaluate("window.__lab.flying()"):
                        break
            assert pg.evaluate("window.__lab.elevators()")["degDown"] < 29
            box = pg.evaluate("window.__lab.elevators()")["boxes"]["elevator.right"]
            for g in (pg, pgh):
                _look_at(g, box, 1.7)
            boxes, got = [], set()
            for _ in range(80):
                _run(pg, 0.1)
                _run(pgh, 0.1)
                e = pg.evaluate("window.__lab.elevators()")
                for deg in (30.0, -15.0):
                    if abs(e["degDown"] - deg) < 1e-6 and deg not in got:
                        got.add(deg)
                        boxes.append((deg, e["boxes"]["elevator.right"]))
                        masks[deg] = (_shot_clip(pg, None), _shot_clip(pgh, None))
            assert got == {30.0, -15.0}, sorted(got)
            clip = _screen_clip(pg, [b for _, b in boxes], 1180, 820)

            def crop(im):
                return im.crop(
                    (
                        int(clip["x"]),
                        int(clip["y"]),
                        int(clip["x"] + clip["width"]),
                        int(clip["y"] + clip["height"]),
                    )
                )

            m = {}
            for deg, (on, off) in masks.items():
                on, off = crop(on), crop(off)
                m[deg] = [
                    1 if sum(abs(i - j) for i, j in zip(u, v)) > 45 else 0
                    for u, v in zip(on.getdata(), off.getdata())
                ]
            n30, n15 = sum(m[30.0]), sum(m[-15.0])
            moved = sum(1 for a, c in zip(m[30.0], m[-15.0]) if a != c)
            print(
                f"elevator box {clip['width']:.0f}x{clip['height']:.0f}: the elevator covers {n30} px at 30 down and {n15} at 15 up; {moved} px belong to one pose only"
            )
            # an elevator buried in the canard shows a sliver (6k and 14k px here); out in its cove it is most of the box (86k and 57k)
            assert (
                n30 > 30000 and n15 > 30000
            ), f"the elevator is not on screen: it covers {n30} px at 30 down and {n15} px at 15 up"
            assert (
                moved > 10000
            ), f"the elevator does not move on screen: only {moved} px of its footprint differ between 30 down and 15 up"
            assert not errors, errors
            for b in bs:
                b.close()
    finally:
        s.shutdown()


def test_ch11_hinge_slots_show_the_striped_elevator_in_an_open_cove_of_the_canard(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            bs, pg, pgh, errors = _pair(p, url, "elevator.")
            for op in ("r30.elev-hinge-slots", "r30.elev-mass-balance"):
                for g in (pg, pgh):
                    g.evaluate("window.__lab.select('r30.top-skin')")
                    _run(g, 3)
                    g.evaluate(f"window.__lab.select('{op}')")
                    _run(g, 6)
                e = pg.evaluate("window.__lab.elevators()")
                assert e["mode"] == "none" and "elevator.right" in e["boxes"], (
                    op,
                    e["mode"],
                )
                for g in (pg, pgh):
                    _look_at(g, e["boxes"]["elevator.right"], 1.7)
                    _run(g, 0.2)
                clip = _screen_clip(pg, [e["boxes"]["elevator.right"]], 1180, 820)
                mask = _elevator_pixels(pg, pgh, clip)
                n, warm = sum(mask), _orange(list(_shot_clip(pg, clip).getdata()), mask)
                print(
                    f"{op}: the elevator covers {n} px of its {clip['width']:.0f}x{clip['height']:.0f} box, {warm} of them amber"
                )
                assert (
                    n > 30000 and warm > 0.5 * n
                ), f"{op}: the striped elevator is not on screen ({n} px, {warm} amber)"
                cv = pg.evaluate("window.__lab.cove()")
                assert cv["open"] and cv["xCut"] == pytest.approx(
                    _graph(rsite)["layup"]["fuselage"]["extras"]["elevators"]["cove"][
                        "x_cut"
                    ]
                ), cv
            assert not errors, errors
            for b in bs:
                b.close()
    finally:
        s.shutdown()


def test_ch12_installed_elevators_read_on_screen_with_a_fitted_shape_label(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op in ("r30.f22-drill-tabs", "r30.elev-fuselage-clearance"):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 5)
                labs = {x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")}
                lab = labs["elevator.installed"]
                assert (
                    lab["text"]
                    == "Elevators (fitted shape; span vs fuselage sides unresolved)"
                    and lab["opacity"] > 0.5
                    and not lab.get("hidden")
                    and not lab.get("collapsed")
                ), (op, lab)
            assert pg.evaluate("window.__lab.cove()")["installed"]
            b.close()
            bs, pg, pgh, errors = _pair(
                p, url, "installed:elevator.", query="&op=r30.f22-drill-tabs"
            )
            for g in (pg, pgh):
                assert (
                    g.evaluate("window.__lab.subject()") == "fuselage"
                )  # the op in the address opens the airplane
                g.evaluate("window.__lab.select('r30.f22-drill-tabs')")
                _run(g, 5)
            bx = pg.evaluate("window.__lab.installedCanard()")["boxes"][
                "installed:elevator.right"
            ]
            for g in (pg, pgh):
                _look_at(g, bx, 1.4, d=(0.7, 0.55, 0.45))
                _run(g, 0.2)
            clip = _screen_clip(pg, [bx], 1180, 820)
            mask = _elevator_pixels(pg, pgh, clip)
            n = sum(mask)
            print(
                f"installed right elevator: {n} px on screen ({clip['width']:.0f}x{clip['height']:.0f} box)"
            )
            assert n > 20000, f"the installed elevator is not on screen ({n} px)"
            assert not errors, errors
            for b in bs:
                b.close()
    finally:
        s.shutdown()


def test_the_canards_cove_is_open_exactly_while_an_elevator_part_shows_and_always_on_the_installed_canard(
    rsite,
):
    g = _graph(rsite)
    order, byid, first = _first_ops(g)
    ex = g["layup"]["fuselage"]["extras"]["elevators"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            ch11 = [
                o for o in order if byid[o]["chapter"] == 11 and not byid[o]["stub"]
            ]
            for op in ch11 + [
                "r30.top-skin",
                "r30.install-pins",
                "r30.align-canard",
                None,
            ]:
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.3)
                shown = any(
                    v != "hidden"
                    for k, v in pg.evaluate("window.__lab.stateAll()").items()
                    if k.startswith("elevator.")
                )
                cv = pg.evaluate("window.__lab.cove()")
                assert cv["open"] == shown, (
                    op,
                    cv,
                    shown,
                )  # the canard keeps its full chord wherever no elevator is on screen (chapter 30's frames)
                assert (
                    cv["xCut"]
                    == pytest.approx(ex["tube_le_x"] - ex["cove"]["slot_gap"], abs=1e-6)
                    and cv["blEnd"] == ex["cove"]["bl_end"]
                )
                assert (
                    cv["blIn"] == ex["cove"]["bl_start"] == pytest.approx(9.3)
                )  # M2.4 fix 3: the cove is the FOAM span, not the whole half span
            _to_fuselage(pg)
            for op in (
                "r30.f22-drill-tabs",
                "r30.elev-fuselage-clearance",
                "f13.nose-door",
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                assert pg.evaluate("window.__lab.cove()")["installed"], op
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_canard_and_elevators_stand_installed_on_a_chapter_12_or_13_op_and_not_on_a_chapter_4_9_op(
    rsite,
):
    g = _graph(rsite)
    ci = g["layup"]["fuselage"]["extras"]["canard_install"]
    inch = 0.0254
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op in (
                "r30.f22-drill-tabs",
                "r30.elev-fuselage-clearance",
                "r30.lift-tab-bushings",
                "r30.f28-pins-permanent",
                "f13.strut-reinforce",
                "f13.nose-door",
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 4)
                ic = pg.evaluate("window.__lab.installedCanard()")
                assert ic["shown"] and ic["nodes"] >= 20, (op, ic["nodes"])
                assert {
                    "installed:canard.core",
                    "installed:canard.core:left",
                    "installed:elevator.right",
                    "installed:elevator.left",
                } <= set(ic["boxes"]), op
            # the airplane stays as it was for chapters 4-9, and for the finished chapter 4-9 box
            for op in (
                "f04.front-seat-bkhd-front",
                "f06.trial-fit",
                "f07.canard-cutout",
                "f07.skin-right",
                "f08.step",
                "f09.brake-lines",
                None,
            ):
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 1)
                assert not pg.evaluate("window.__lab.installedCanard()")["shown"], op
            # where it stands: leading edge at F.S. 18.7 and the canard's height, zero incidence (no rotation), the left half the right mirrored
            pg.evaluate("window.__lab.select('f13.nose-door')")
            _run(pg, 4)
            ic = pg.evaluate("window.__lab.installedCanard()")
            assert (
                ic["at"][:2] == [ci["fs_le"], ci["z_le"]] and ci["incidence_deg"] == 0.0
            )
            pb = pg.evaluate(
                "window.__lab.plyBox('canard.core')"
            )  # the canard's own frame (inches)
            r, left = (
                ic["boxes"]["installed:canard.core"],
                ic["boxes"]["installed:canard.core:left"],
            )
            lo = pg.evaluate(
                f"window.__lab.fuseToWorld([{ci['fs_le'] + pb['min'][0]}, {ci['z_le'] + pb['min'][1]}, 0])"
            )
            assert r[0][0] == pytest.approx(lo[0], abs=1e-6) and r[0][
                1
            ] == pytest.approx(lo[1], abs=1e-6)
            assert (r[1][1] - r[0][1]) == pytest.approx(
                (pb["max"][1] - pb["min"][1]) * inch, abs=1e-6
            )  # no tilt: the height is the section's own
            assert (r[1][0] - r[0][0]) == pytest.approx(
                (pb["max"][0] - pb["min"][0]) * inch, abs=1e-6
            )
            zc = pg.evaluate("window.__lab.fuseToWorld([0, 0, 0])")[2]
            assert left[0][2] == pytest.approx(2 * zc - r[1][2], abs=1e-6) and left[1][
                2
            ] == pytest.approx(2 * zc - r[0][2], abs=1e-6)
            assert (r[1][2] - r[0][2]) == pytest.approx(
                70.8 * inch, abs=1e-3
            )  # a whole canard: both halves of the 141.6 in span
            re_, le_ = (
                ic["boxes"]["installed:elevator.right"],
                ic["boxes"]["installed:elevator.left"],
            )
            # the right elevator is on the right of the centre line, the left one reaches out on the left; the FOAMS mirror and neither crosses the
            # centre line (M2.4 fix 3: cobelu figure C-1's 72.7 in is the left TUBE, which crosses; the foam is 55.7 in on both sides)
            assert (
                re_[0][2] > zc - 70 * inch
                and re_[1][2] < zc
                and le_[1][2] > zc + 60 * inch
                and le_[1][2] < zc + 70 * inch
            )
            assert (
                le_[0][2] > zc and re_[1][2] < zc
            )  # the left foam stays on its side of the centre line
            assert (le_[1][2] - le_[0][2]) == pytest.approx(
                55.7 * inch, abs=0.002
            ) and (re_[1][2] - re_[0][2]) == pytest.approx(55.7 * inch, abs=0.002)
            # no gross interpenetration with the box: the canard stays inside the airplane's width and off the bench
            bench = pg.evaluate("window.__lab.fuseFloor()")["bench"]
            for bx in (r, left, re_, le_):
                assert not _boxes_overlap(bx, bench)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _legible(x):
    """A label counts as on screen only if it has its words: visible, not collapsed to its dot, not hidden by the declutter rule."""
    return x["opacity"] > 0.5 and not x.get("collapsed") and not x.get("hidden")


_NG_BENCH = ("gear.nose_strut", "nose.ng30_plates", "nose.ng_hardware")


def test_nose_parts_appear_on_the_op_that_lists_them_and_never_before_chapter_13(rsite):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    rows = fz["extras"]["nose_parts"]
    order, byid, first = _first_ops(g)
    ch13 = [o for o in order if byid[o]["chapter"] == 13 and not byid[o]["stub"]]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            assert set(_chips(pg)) >= set(ch13) and "r30.f22-drill-tabs" in _chips(pg)
            for op in ch13:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.2)
                pl = pg.evaluate("window.__lab.placement()")
                for name, row in rows.items():
                    due = order.index(first[row["component"]]) <= order.index(op)
                    if (
                        name == "gear_nose_strut"
                    ):  # drawn from the op that lowers it into the box (before that, only on the bench: below)
                        due = due and order.index(op) >= order.index("f13.lower-gear")
                    # M2.4 fix 2: the NG box (strut group, plates, NG6) is built on the jig bench ('table') from the op that makes each, until f13.ng31-f6 mounts it
                    on_bench = row["component"] in _NG_BENCH and order.index(
                        first[row["component"]]
                    ) <= order.index(op) < order.index("f13.ng31-f6")
                    want = "table" if on_bench else "jig" if due else "none"
                    assert pl[name] == want, (op, name, pl[name])
                    assert (
                        pg.evaluate(f"window.__lab.meshBox('{row['node']}')")
                        is not None
                    ) == (due or on_bench), (op, name)
            # the first op of each nose component is a real chapter 13 op (not a stub, not a later chapter)
            assert all(
                byid[first[r["component"]]]["chapter"] == 13 for r in rows.values()
            )
            # nothing of the nose before chapter 13, nor on the finished chapter 4-9 box
            for op in (
                "f09.brake-lines",
                "r30.f22-drill-tabs",
                "r30.f28-pins-permanent",
                None,
            ):
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.5)
                pl = pg.evaluate("window.__lab.placement()")
                assert all(pl[n] == "none" for n in rows), (
                    op,
                    {n: pl[n] for n in rows if pl[n] != "none"},
                )
            # a fitted shape, every one: striped and labelled so; the nose runs to the tip
            pg.evaluate("window.__lab.select('f13.nose-door')")
            _run(pg, 4)
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            for name, row in rows.items():
                m = pg.evaluate(f"window.__lab.material('{row['node']}')")
                assert m["hatch"] and m["fidelity"] == "representational", (name, m)
                assert labs[row["node"]]["text"] == row["label"] and labs[row["node"]][
                    "text"
                ].endswith("(fitted shape)"), name
            assert _legible(labs["nose.door"]), labs[
                "nose.door"
            ]  # on screen with its words: not a collapsed dot, not hidden
            assert min(r["fs_min"] for r in rows.values()) == pytest.approx(
                -6.8, abs=0.01
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_chapter_12_and_13_ops_show_at_most_ten_labels_and_keep_the_conflict_and_the_new_parts(
    rsite,
):
    g = _graph(rsite)
    order, byid, first = _first_ops(g)
    ops = [o for o in order if byid[o]["chapter"] in (12, 13) and not byid[o]["stub"]]
    assert (
        "f13.rig-nose-gear" in ops
        and "r30.f28-pins-permanent" in ops
        and len(ops) == 24
    ), ops
    g["layup"]["fuselage"]["extras"]["nose_parts"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op in ops:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 3)
                allp = pg.evaluate("window.__lab.labelsAll()")
                on = [x["id"] for x in allp if x["opacity"] > 0.5]
                assert len(on) <= 10, (
                    op,
                    on,
                )  # dots count: nothing beyond ten is on screen, readable or collapsed
                ng = pg.evaluate("window.__lab.noseGear()")
                if (
                    ng["shown"] and ng["t"] < 1
                ):  # the nose wheel is down and in view: its two candidates (conflict) always stay, readable (M2.4 fix: not hidden, not a dot)
                    legible = {x["id"] for x in allp if _legible(x)}
                    assert {"mark.nose-plans", "mark.nose-manual"} <= legible, (
                        op,
                        [x for x in allp if x["id"].startswith("mark.nose")],
                    )
            # the parts new on an op keep their fitted-shape label, whatever else is dropped for the budget
            for op, node in (
                ("f13.nose-door", "nose.door"),
                ("f13.carve-glass-nose", "nose.skin"),
                ("f13.pitot-static", "nose.pitot"),
                ("f13.top-foam", "nose.top_block"),
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 3)
                on = {
                    x["id"]: x
                    for x in pg.evaluate("window.__lab.labelsAll()")
                    if _legible(x)
                }  # M2.4 fix: a collapsed or hidden label is not "on"
                assert node in on and "fitted shape" in on[node]["text"], (op, list(on))
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_nose_gear_is_down_until_the_rig_op_cranks_it_up_in_six_seconds_and_it_ends_in_the_nb_box(
    rsite,
):
    g = _graph(rsite)
    fz = g["layup"]["fuselage"]
    ng = fz["extras"]["nose_gear"]
    panel = fz["parts"]["panel"]["fs_min"]
    nb = fz["extras"]["nose_parts"]["nose_nb_box"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            # before the gear is lowered into the box it is not drawn and the nose stands on its stand; from lower-gear it is down on the floor
            pg.evaluate("window.__lab.select('f13.ng-box-assemble')")
            _run(pg, 0.3)
            n = pg.evaluate("window.__lab.noseGear()")
            assert (
                not n["shown"] and n["stand"] and not pg.evaluate("window.__lab.kin()")
            )
            pg.evaluate("window.__lab.select('f13.lower-gear')")
            _run(pg, 0.3)
            n = pg.evaluate("window.__lab.noseGear()")
            assert (
                n["shown"]
                and n["t"] == 0
                and not n["stand"]
                and n["crank"] == "Crank 0.0 of 10.8 turns (gear down)"
            )
            assert (
                n["wheel"]["plans"][0] == pytest.approx(17.0)
                and n["wheel"]["manual"][0] == pytest.approx(20.0)
                and n["ghostShown"]
            )
            # the rig op: the crank turns in sim time (frozen: wall time moves nothing), six seconds inside the book's five to seven
            pg.evaluate("window.__lab.select('f13.rig-nose-gear')")
            _run(pg, 0.3)
            time.sleep(0.3)
            assert (
                pg.evaluate("window.__lab.noseGear()")["t"] == 0
                and pg.text_content("#ro-kin") == "Crank 0.0 of 10.8 turns (gear down)"
            )
            started = ended = None
            xs = []
            for i in range(1, 120):
                _run(pg, 0.1)
                n = pg.evaluate("window.__lab.noseGear()")
                xs.append(n["wheel"]["plans"][0])
                if started is None and n["t"] > 0:
                    started = i
                if ended is None and n["t"] >= 1:
                    ended = i
                    break
            secs = (ended - started + 1) * 0.1
            assert (
                ng["book_seconds"][0] <= secs <= ng["book_seconds"][1]
                and abs(secs - ng["retract_seconds"]) < 0.25
            ), secs
            assert (
                max(xs) - xs[0] > 15 and max(xs) - xs[-1] < 1.0
            )  # the wheel swings aft (to the strut's horizontal, F.S. 34, and a little past it)
            assert all(
                a <= b_ + 1e-9
                for a, b_ in zip(xs[: xs.index(max(xs))], xs[1 : xs.index(max(xs)) + 1])
            )
            _run(pg, 1)
            n = pg.evaluate("window.__lab.noseGear()")
            assert (
                n["t"] == 1
                and n["crank"] == "Crank 10.8 of 10.8 turns (retracted)"
                and pg.text_content("#ro-kin") == n["crank"]
            )
            # the wheel ends inside the NB box, forward of the panel; the other candidate's ghost ends there too
            for c in ("plans", "manual"):
                assert nb["fs_min"] < n["wheel"][c][0] < panel, (
                    c,
                    n["wheel"][c],
                    nb["fs_min"],
                    panel,
                )
            assert (
                n["wheel"]["plans"][1] > -17.4 - 22 + 4.5
            )  # up off the floor: the wheel centre is well above its gear-down height
            # the ops after it keep it retracted; the nose stands on its stand again
            pg.evaluate("window.__lab.select('f13.pitot-static')")
            _run(pg, 0.3)
            n = pg.evaluate("window.__lab.noseGear()")
            assert (
                n["t"] == 1
                and n["stand"]
                and pg.evaluate("window.__lab.kin()")["value"]
                == "Crank 10.8 of 10.8 turns (retracted)"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_both_nose_wheel_axle_candidates_show_with_the_word_conflict_and_the_station_is_never_a_bare_fact(
    rsite,
):
    import re

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(
                p, url, 1400, 900, query="&freeze=1&op=f13.rig-nose-gear"
            )
            _run(pg, 4)
            pg.click("#fuse-more")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert (
                "conflict" in labs["mark.nose-plans"]["text"]
                and "17" in labs["mark.nose-plans"]["text"]
                and "plans" in labs["mark.nose-plans"]["text"]
            )
            assert (
                "conflict" in labs["mark.nose-manual"]["text"]
                and "20" in labs["mark.nose-manual"]["text"]
                and "manual" in labs["mark.nose-manual"]["text"]
            )
            n = pg.evaluate("window.__lab.noseGear()")
            assert (
                n["ghostShown"] and 0 < n["t"] < 1
            ), n  # 4 s into the rig op the crank is turning
            sub = pg.inner_text("#ro-cg-sub")
            assert (
                "Nose wheel arm: F.S. 17 (plans) / about 20 (manual): conflict" in sub
            ), sub
            assert (
                sub.split("·")[-1].strip().startswith("≥")
                and "lower bound" in sub.split("·")[-1]
            )  # the lower bound keeps its sourced rows, last
            assert (
                pg.inner_text("#ro-cg") == "not yet computed"
            )  # the CG stays not computed while a row is unsourced
            g = pg.inner_text("#ro-ground-sub")
            assert "nose wheel W.L. -22 (CP25 LPC 24)" in g, g
            assert (
                not re.search(r"tip-over[^·]*\d", g, re.I)
                and "tip-over check: not yet computed" in g
            )
            assert "conflict" in pg.inner_text("#ro-kin-sub")
            # no label or readout states the nose wheel's F.S. as a bare fact
            texts = [x["text"] for x in pg.evaluate("window.__lab.labels()")]
            texts += [
                pg.inner_text(i)
                for i in (
                    "#ro-cg",
                    "#ro-cg-sub",
                    "#ro-ground",
                    "#ro-ground-sub",
                    "#ro-kin",
                    "#ro-kin-sub",
                )
            ]
            seen = 0
            for t in texts:
                for seg in re.split(r"·", t):
                    if re.search(
                        r"(nose wheel|nose gear|ghost|axle station)[^·]{0,90}(F\.S\. ?\d|about \d)",
                        seg,
                        re.I,
                    ):
                        seen += 1
                        assert "conflict" in seg.lower(), seg
            assert seen >= 3
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_station_cut_works_through_the_nose_and_the_elevators_and_keeps_the_old_range_for_chapters_4_9(
    rsite,
):
    _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f09.brake-lines')")
            assert (
                pg.get_attribute("#section-bl", "min") == "22"
                and pg.get_attribute("#section-bl", "max") == "125.5"
            )
            pg.evaluate(
                "window.__lab.setSection(true, 5)"
            )  # the old range clamps: nothing forward of F22 on a chapter 9 op
            assert pg.evaluate("window.__lab.cut()")["fs"] == 22
            pg.evaluate("window.__lab.setSection(false, 22)")
            pg.evaluate("window.__lab.select('f13.nose-door')")
            _run(pg, 3)
            assert pg.get_attribute("#section-bl", "min") == "-6.8"
            pg.evaluate("window.__lab.setSection(true, -3)")
            _run(pg, 3)
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["enabled"] and c["fs"] == -3 and c["keepsAft"] and c["removesForward"]
            ), c
            assert {"nose.skin", "nose.pitot"} <= set(c["capNodesVisible"]) and c[
                "capsVisible"
            ] == len(c["cappedNodes"]), c["capNodesVisible"]
            assert (
                "Nose skin" in pg.inner_text("#ro-layers")
                and pg.inner_text("#ro-station") == "FS -3"
            )
            pg.evaluate("window.__lab.setSection(true, 12)")
            _run(pg, 3)
            c = pg.evaluate("window.__lab.cut()")
            assert {
                "nose.skin",
                "nose.floor_blocks",
                "nose.ng30_plates",
                "nose.side_blocks",
            } <= set(c["capNodesVisible"]), c["capNodesVisible"]
            pg.evaluate("window.__lab.setSection(true, -6.8)")  # the nose tip itself
            assert pg.evaluate("window.__lab.cut()")["fs"] == -6.8
            assert (
                "nose.skin" in pg.evaluate("window.__lab.cut()")["capNodesVisible"]
            )  # the tip cut still has the skin's cap
            # leaving the nose: the slider is the box's again, and the cut stays where it fits
            pg.evaluate("window.__lab.select('r30.f28-pins-permanent')")
            assert (
                pg.get_attribute("#section-bl", "min") == "22"
                and pg.evaluate("window.__lab.cut()")["fs"] == 22
            )
            # the elevators, at a buttock-line cut on the canard (the right half): the body and the tube are capped inside their span, not outboard of it
            pg.click('#subject button[data-subject="canard"]')
            pg.evaluate("window.__lab.select('r30.elev-travel-check')")
            _run(pg, 8)
            pg.evaluate("window.__lab.setSection(true, 30)")
            _run(pg, 2)
            c = pg.evaluate("window.__lab.cut()")
            assert (
                c["enabled"]
                and c["keepsOutboard"]
                and c["removesInboard"]
                and c["capsVisible"] == len(c["cappedNodes"])
            )
            assert {"elevator.right", "elevator.tube.right"} <= set(
                c["capNodesVisible"]
            ), c["capNodesVisible"]
            pg.evaluate(
                "window.__lab.setSection(true, 67)"
            )  # past the elevators' outboard end (B.L. 65)
            _run(pg, 2)
            assert not {
                n
                for n in pg.evaluate("window.__lab.cut()")["cappedNodes"]
                if n.startswith("elevator.")
            }
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_canard_bar_follows_chapter_11_and_the_fuselage_bar_takes_chapters_12_and_13_and_the_canard_frame_is_its_own(
    rsite,
):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1400, 860, query="&freeze=1")
            canard_bar = _chips(pg)
            assert canard_bar == _bar_ops(g, "roncz")
            assert (
                "r30.elev-bond-cores" in canard_bar
                and "r30.canard-tips" in canard_bar
                and "r30.install-pins" in canard_bar
                and "r30.align-canard" in canard_bar
            )
            assert (
                not [o for o in canard_bar if o.startswith("f13.")]
                and "r30.f22-drill-tabs" not in canard_bar
                and "r30.lift-tab-bushings" not in canard_bar
            )
            assert (
                canard_bar.index("r30.top-skin")
                < canard_bar.index("r30.elev-bond-cores")
                < canard_bar.index("r30.install-pins")
            )  # the chapter 11 ops follow the ones they follow in the book
            # the canard's home frame is the canard's box alone: the elevators, hung beside it for some ops, never move it
            pg.evaluate("window.__lab.select(null)")
            _run(pg, 4)
            boxes = [
                pg.evaluate(f"window.__lab.meshBox('{n}')")
                for n in pg.evaluate("window.__lab.meshNames()")
                if n.startswith("canard.")
                and not n.endswith(tuple(f".p{i}" for i in range(1, 9)))
            ]
            lo = [min(bx[0][i] for bx in boxes) for i in range(3)]
            hi = [max(bx[1][i] for bx in boxes) for i in range(3)]
            cam = pg.evaluate("window.__lab.camera()")
            ctr = [(lo[i] + hi[i]) / 2 for i in range(3)]
            assert cam["target"][0] == pytest.approx(ctr[0], abs=0.02) and cam[
                "target"
            ][2] == pytest.approx(ctr[2], abs=0.02)
            pg.click('#subject button[data-subject="fuselage"]')
            chips = _chips(pg)
            assert (
                chips == _fuse_ops(g)
                and "r30.f22-drill-tabs" in chips
                and "f13.nose-door" in chips
                and "r30.elev-bond-cores" not in chips
            )
            assert (
                chips.index("f09.brake-lines")
                < chips.index("r30.f22-drill-tabs")
                < chips.index("f13.strut-reinforce")
            )
            shots = pg.evaluate("window.__lab.fuseShots()")
            assert all(
                shots[o] for o in chips
            )  # every chapter 12 and 13 op has its own lab shot
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.4 Task 6: the chapter 11, 12 and 13 tours and the canard12 film (the canard lowering onto F22).
# ======================================================================================================================
def _tour_probe(pg, ops, probes, after):
    """Run the tour (dt 0.1) until it selects `after` (or ends); return the ops it selected in order and, for each op in `probes`, the probe's
    value on the last frame the op was selected, i.e. at the moment the tour leaves it."""
    seen, last = [], {}
    for _ in range(6000):
        _tour_adv(pg, 0.1, dt=0.1)
        sel = pg.evaluate("__lab.selected()")
        if sel and (not seen or seen[-1] != sel):
            seen.append(sel)
        if sel in probes:
            last[sel] = pg.evaluate(probes[sel])
        if sel == after or not pg.evaluate("__lab.touring()"):
            break
    return seen, last


def test_chapter_11_tour_visits_every_elevator_op_and_holds_on_the_travel_and_hang_poses(
    rsite,
):
    g = _graph(rsite)
    want = _chapter_ops(g, "roncz", 11)
    assert len(want) >= 10 and want[0] == "r30.elev-nc2-inserts"
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            pg.evaluate(f"__lab.select('{want[0]}')")
            pg.click("#tour")
            assert (
                pg.evaluate("__lab.touring()") is True
                and pg.evaluate("__lab.tourIndex()") == 0
            )
            probes = {
                "r30.elev-travel-check": "[__lab.elevators().degDown, __lab.kin().value]",
                "r30.elev-balance-check": "[__lab.elevators().noseDown, __lab.elevators().hangPitch, __lab.elevators().degDown, __lab.kin().value]",
            }
            seen, last = _tour_probe(pg, want, probes, after=want[-1])
            assert seen == want, seen  # every chapter 11 op, in order
            deg, text = last["r30.elev-travel-check"]
            assert (
                deg == pytest.approx(-15.0)
                and text == "Up 15.0 deg  (target 15, floor 12.5)"
            ), last  # the travel reached 15 up before the tour left
            nose_down, pitch, deg, text = last["r30.elev-balance-check"]
            assert (
                nose_down is True
                and pitch > 0
                and deg == pytest.approx(-pitch, abs=0.01)
                and "Hangs nose down" in text
            ), last  # the hang settled
            pg.click("#tour")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_chapter_12_and_13_tours_visit_every_op_hold_the_crank_and_end_on_their_own_last_op(
    rsite,
):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            # chapter 11 (the canard subject): the film's last frame is the elevators as the chapter leaves them, not the bare canard
            b, pg, errors = _open_rec(p, url)
            ch11 = _chapter_ops(g, "roncz", 11)
            pg.evaluate(f"__lab.select('{ch11[0]}')")
            pg.click("#tour")
            seen, _ = _tour_probe(pg, ch11, {}, after="never")
            assert seen == ch11 and pg.evaluate("__lab.touring()") is False
            assert pg.evaluate("__lab.selected()") == ch11[-1]
            assert pg.evaluate("__lab.stateAll()")["elevator.right"] != "hidden"
            b.close()
            for ch, last_probe in ((12, None), (13, "crank")):
                want = _chapter_ops(g, "roncz", ch)
                b, pg, errors = _open_rec(p, url)
                _to_fuselage(pg)
                pg.evaluate(f"__lab.select('{want[0]}')")
                pg.click("#tour")
                assert pg.evaluate("__lab.touring()") is True
                probes = (
                    {"f13.rig-nose-gear": "__lab.noseGear().crank"} if ch == 13 else {}
                )
                seen, last = _tour_probe(pg, want, probes, after="never")
                assert seen == want, (ch, seen)
                if (
                    ch == 13
                ):  # the tour waited out the crank: 10.8 turns, retracted, when it left the rig op
                    assert (
                        last["f13.rig-nose-gear"]
                        == "Crank 10.8 of 10.8 turns (retracted)"
                    ), last
                # the closing frame is the chapter's own last op with the canard installed, never another chapter's closing state
                assert (
                    pg.evaluate("__lab.touring()") is False
                    and pg.evaluate("__lab.selected()") == want[-1]
                )
                assert pg.evaluate("__lab.installedCanard()")["shown"] is True
                assert pg.evaluate("__lab.subject()") == "fuselage"
                assert not errors, (ch, errors)
                b.close()
    finally:
        s.shutdown()


def test_canard12_film_starts_on_the_card_lowers_the_canard_onto_f22_and_ends_on_a_chapter_12_op(
    rsite,
):
    g = _graph(rsite)
    want = _chapter_ops(g, "roncz", 12)
    ci = g["layup"]["fuselage"]["extras"]["canard_install"]
    inch = 0.0254
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url, query="&clean=1")
            dur = pg.evaluate("window.__rec.start('canard12')")
            assert 35 <= dur <= 60, dur
            assert pg.evaluate("__lab.subject()") == "fuselage"
            # the first frame is the chapter card, over an airplane with no canard on it
            pg.evaluate("window.__rec.frame(0.5, false)")
            assert (
                pg.evaluate(
                    "getComputedStyle(document.getElementById('endcard')).display"
                )
                != "none"
            )
            assert pg.inner_text("#endcard .ec-t") == "Chapter 12 — Canard installation"
            assert pg.evaluate("__lab.installedCanard().shown") is False
            samples, seen, active, t, nxt = [], [], True, 0.5, 0.5
            while active:
                r = pg.evaluate("window.__rec.frame(1 / 15, false)")
                active, t = r["active"], t + 1 / 15
                sel = pg.evaluate("__lab.selected()")
                if sel and (not seen or seen[-1] != sel):
                    seen.append(sel)
                if t >= nxt:
                    ic = pg.evaluate("__lab.installedCanard()")
                    samples.append(
                        (
                            t,
                            ic["shown"],
                            ic["at"][1],
                            ic["boxes"].get("installed:canard.core"),
                        )
                    )
                    nxt += 0.5
            shown = [x for x in samples if x[1]]
            assert shown and not samples[0][1], samples[:3]
            ys = [
                x[2] for x in shown
            ]  # the group's height in the box frame (inches): 24 in over, then down, then exactly installed
            assert ys[0] == pytest.approx(ci["z_le"] + 24.0, abs=1e-6)
            assert all(
                a >= b2 - 1e-9 for a, b2 in zip(ys, ys[1:])
            ), ys  # only ever coming down
            assert (
                ys[-1] == ci["z_le"] and ys.count(ci["z_le"]) >= 20
            )  # then held exactly at the installed pose (Task 5's)
            falling = [x for x in shown if x[2] > ci["z_le"]]
            assert (
                len({round(x[2], 3) for x in falling}) >= 8
            )  # a real descent: many distinct heights, not a jump
            # clear on the way down: the canard's lowest point stays at least `lift` above where it ends up (it only translates vertically)
            final_min = shown[-1][3][0][1]
            for _, _, y, bx in falling:
                assert bx[0][1] - final_min == pytest.approx(
                    (y - ci["z_le"]) * inch, abs=1e-6
                )
            # the film ends on a chapter 12 op, the last one, with the cut off and the canard installed
            assert (
                not pg.evaluate("__lab.touring()")
                and pg.evaluate("__lab.selected()") == want[-1]
            )
            assert [o for o in seen if o in want] == want  # the chapter 12 ops in order
            assert pg.evaluate("__lab.cut().enabled") is False
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ---- M2.4 fix round 2 (visual review findings 2, 3, 4, 5, 9): the chapter 13 frames show their subject, the stowed wheel carries no stale
# station, the phone readout does not overlap. These judge what is on screen (boxes in screen pixels, label state), not transforms alone.
def _screen_box(pg, bx):
    pts = [
        pg.evaluate("(p) => window.__lab.project(p)", [x, y, z])
        for x in (bx[0][0], bx[1][0])
        for y in (bx[0][1], bx[1][1])
        for z in (bx[0][2], bx[1][2])
    ]
    return [
        min(q[0] for q in pts),
        min(q[1] for q in pts),
        max(q[0] for q in pts),
        max(q[1] for q in pts),
    ]


def _ch13_ops(g):
    order, byid, first = _first_ops(g)
    return [o for o in order if byid[o]["chapter"] == 13 and not byid[o]["stub"]], byid


def test_every_chapter_13_op_shows_its_own_parts_with_their_words_not_a_collapsed_dot(
    rsite,
):
    g = _graph(rsite)
    rows = g["layup"]["fuselage"]["extras"]["nose_parts"]
    ops, byid = _ch13_ops(g)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op in ops:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 4)
                labs = {x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")}
                own = [
                    r["node"]
                    for r in rows.values()
                    if r["component"] in byid[op]["components"]
                ]
                for node in own:
                    assert node in labs and _legible(labs[node]), (
                        op,
                        node,
                        labs.get(node),
                    )  # the op's own part: on screen, collapsed false, hidden false
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_nose_gear_box_is_built_on_the_bench_then_mounted_and_every_nose_frame_shows_its_subject_clear_of_the_cards(
    rsite,
):
    g = _graph(rsite)
    rows = g["layup"]["fuselage"]["extras"]["nose_parts"]
    ops, byid = _ch13_ops(g)
    node_of = {r["component"]: r["node"] for r in rows.values()}
    bench_ops = [
        "f13.strut-reinforce",
        "f13.worm-drive-bench",
        "f13.ng30-plates",
        "f13.ng-box-assemble",
        "f13.ng3-ng4",
    ]
    inch = 0.0254
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            floor = pg.evaluate("window.__lab.fuseFloor()")[
                "bench"
            ]  # the bench's box: its top is the blocks' top less their 3 in
            top = floor[1][1] - 3 * inch

            def own_nodes(op):
                got = [node_of[c] for c in byid[op]["components"] if c in node_of]
                if not got:  # the worm drive has no model: the frame shows what is on the bench by then
                    got = [
                        n
                        for c, n in node_of.items()
                        if c in _NG_BENCH
                        and pg.evaluate(f"window.__lab.meshBox('{n}')")
                    ]
                return got

            def clear_of_cards(op, nodes):
                for n in nodes:
                    sb = _screen_box(pg, pg.evaluate(f"window.__lab.meshBox('{n}')"))
                    assert (
                        0 <= sb[0] and sb[2] <= 1180 and 0 <= sb[1] and sb[3] <= 820
                    ), (op, n, sb)  # on screen
                    for sel in _CARDS:
                        c = _rect(pg, sel)
                        assert not (
                            sb[0] < c[2]
                            and c[0] < sb[2]
                            and sb[1] < c[3]
                            and c[1] < sb[3]
                        ), (op, n, sel, sb, c)  # and not under a card

            for op in bench_ops + ["f13.ng31-f6", "f13.nose-door"]:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 5)
                nodes = own_nodes(op)
                assert nodes, op
                clear_of_cards(op, nodes)
                if op in bench_ops:
                    for c in _NG_BENCH:  # whatever of the NG box exists by this op lies on the bench: above its top, inside its footprint
                        n = node_of[c]
                        bx = pg.evaluate(f"window.__lab.meshBox('{n}')")
                        if bx is None:
                            continue
                        assert bx[0][1] >= top - 1e-3 and bx[1][1] < top + 0.6, (
                            op,
                            n,
                            bx,
                            top,
                        )
                        assert (
                            bx[0][0] >= floor[0][0]
                            and bx[1][0] <= floor[1][0]
                            and bx[0][2] >= floor[0][2]
                            and bx[1][2] <= floor[1][2]
                        ), (op, n, bx, floor)
            # the strut is on the bench for the first op, and the plates arrive with theirs
            pg.evaluate("window.__lab.select('f13.strut-reinforce')")
            _run(pg, 1)
            pl = pg.evaluate("window.__lab.placement()")
            assert (
                pl["gear_nose_strut"] == "table"
                and pl["nose_ng30_plates"] == "none"
                and pl["nose_ng_hardware"] == "none"
            ), pl
            # mounted: from f13.ng31-f6 the plates stand at F22, where every later op has them (same box), far from the bench
            pg.evaluate("window.__lab.select('f13.ng3-ng4')")
            _run(pg, 1)
            on_bench = pg.evaluate(
                f"window.__lab.meshBox('{node_of['nose.ng30_plates']}')"
            )
            pg.evaluate("window.__lab.select('f13.ng31-f6')")
            _run(pg, 1)
            mounted = pg.evaluate(
                f"window.__lab.meshBox('{node_of['nose.ng30_plates']}')"
            )
            assert pg.evaluate("window.__lab.placement()")["nose_ng30_plates"] == "jig"
            pg.evaluate("window.__lab.select('f13.floor-blocks')")
            _run(pg, 1)
            later = pg.evaluate(
                f"window.__lab.meshBox('{node_of['nose.ng30_plates']}')"
            )
            assert all(
                abs(u - v) < 1e-6 for r, q in zip(mounted, later) for u, v in zip(r, q)
            ), (mounted, later)
            cm = [(mounted[0][i] + mounted[1][i]) / 2 for i in range(3)]
            cb = [(on_bench[0][i] + on_bench[1][i]) / 2 for i in range(3)]
            assert sum((a - c) ** 2 for a, c in zip(cm, cb)) ** 0.5 > 1.0, (
                cm,
                cb,
            )  # moved off the bench, not nudged
            # and the strut is out of the frame between the mount and the lowering of the gear (it goes into the box at f13.lower-gear)
            assert pg.evaluate("window.__lab.placement()")["gear_nose_strut"] == "none"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("w,h", [(390, 844), (1180, 820)])
def test_the_motion_row_is_not_clipped_and_does_not_overlap_its_neighbours(rsite, w, h):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            for op, subj, secs in (
                ("r30.elev-balance-check", "canard", 16),
                ("f13.lower-gear", "fuselage", 1),
                ("f13.rig-nose-gear", "fuselage", 3),
            ):
                b = p.chromium.launch(args=GL)
                ctx = b.new_context(
                    viewport={"width": w, "height": h}, has_touch=w < 700
                )
                pg = ctx.new_page()
                errors = []
                pg.on("pageerror", lambda e: errors.append(str(e)))
                pg.goto(url + f"?test=1&q=low&freeze=1&op={op}")
                pg.wait_for_function(
                    "window.__lab && window.__lab.ready", timeout=60000
                )
                assert pg.evaluate("window.__lab.subject()") == subj
                _run(pg, secs)
                assert pg.is_visible("#t-kin")
                m = pg.evaluate("""() => {
                    const r = (e) => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom] }
                    const kin = document.getElementById('t-kin'), val = document.getElementById('ro-kin'), sub = document.getElementById('ro-kin-sub')
                    const others = [...document.querySelectorAll('#readout .tile, #readout .layers, #fuse-rows .tile')]
                        .filter((e) => e !== kin && !kin.contains(e) && e.offsetParent && e.getBoundingClientRect().width > 0)
                        .map((e) => [e.id || e.dataset.k, r(e)])
                    const fits = (e) => e.scrollWidth <= e.clientWidth + 1
                    return { kin: r(kin), val: r(val), valText: val.textContent, valFits: fits(val), subFits: fits(sub), others, kinFits: fits(kin) }
                }""")
                assert m["valFits"] and m["subFits"] and m["kinFits"], (
                    op,
                    m,
                )  # nothing clipped sideways: "Hangs nose down ... (illustrative CG:" was
                k = m["kin"]
                assert m["val"][2] <= k[2] + 1 and m["val"][0] >= k[0] - 1, (
                    op,
                    m,
                )  # the value sits inside its own tile
                for name, o in m["others"]:
                    inter = max(0, min(k[2], o[2]) - max(k[0], o[0])) * max(
                        0, min(k[3], o[3]) - max(k[1], o[1])
                    )
                    assert inter <= 1, (
                        op,
                        w,
                        name,
                        o,
                        k,
                    )  # no neighbouring tile's box meets the motion row's
                if w <= 640:
                    assert k[2] - k[0] >= w - 40, (
                        op,
                        k,
                    )  # the motion row has its own full-width line on a phone
                    assert all(
                        o[3] <= k[1] + 1
                        for _, o in m["others"]
                        if o[0] < k[2] and o[2] > k[0] and o[1] < k[1]
                    ), (op, m["others"], k)  # the others sit above it
                if op == "r30.elev-balance-check":
                    assert (
                        m["valText"].startswith("Hangs nose down, about ")
                        and m["valText"].endswith(" deg")
                        and "." not in m["valText"]
                    ), m["valText"]
                    assert "illustrative CG: masses not sourced" in pg.inner_text(
                        "#ro-kin-sub"
                    )
                assert not errors, errors
                b.close()
    finally:
        s.shutdown()


def test_the_stowed_nose_wheel_carries_no_f_s_17_or_20_mark_and_the_marks_stay_while_it_is_down(
    rsite,
):
    g = _graph(rsite)
    ops, byid = _ch13_ops(g)
    after = ops[ops.index("f13.rig-nose-gear") :]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)

            def stale():
                return [
                    (x["id"], x["text"])
                    for x in pg.evaluate("window.__lab.labelsAll()")
                    if ("F.S. 17" in x["text"] or "F.S. 20" in x["text"])
                    and x["opacity"] > 0.004
                    and not x.get("hidden")
                ]

            # gear down (and while it turns): the marks are there, in words
            for op, secs in (
                ("f13.lower-gear", 4),
                ("f13.rig-nose-gear", 4),
            ):  # (the camera is still flying in for the first ~2.5 s of an op)
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, secs)
                n = pg.evaluate("window.__lab.noseGear()")
                assert n["shown"] and n["t"] < 1, (op, n)
                legible = {
                    x["id"]
                    for x in pg.evaluate("window.__lab.labelsAll()")
                    if _legible(x)
                }
                assert {"mark.nose-plans", "mark.nose-manual"} <= legible, (op, legible)
            # stowed (t == 1): the end of the rig op and every later op: neither station is on a label, the motion and CG rows keep the conflict
            pg.evaluate("window.__lab.select('f13.rig-nose-gear')")
            _run(pg, 9)
            assert pg.evaluate("window.__lab.noseGear()")["t"] == 1
            for op in after:
                if op != "f13.rig-nose-gear":
                    pg.evaluate(f"window.__lab.select('{op}')")
                    _run(pg, 4)
                assert pg.evaluate("window.__lab.noseGear()")["t"] == 1, op
                assert stale() == [], (op, stale())
                assert "conflict" in pg.inner_text("#ro-kin-sub"), op
            pg.click("#fuse-more")
            assert "conflict" in pg.inner_text("#ro-cg-sub")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_the_root_notch_is_gone_the_cove_is_the_foam_span_only(rsite):
    """M2.4 fix 3: with the elevators left out of the scene, the canard subject shows canard material (not the table behind) inboard of
    |B.L.| 9.3, and an empty cove outboard of it; the installed canard carries the same cove."""
    ex = _graph(rsite)["layup"]["fuselage"]["extras"]["elevators"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pgh, errors = _open(p, url, 1180, 820, query="&freeze=1&hide=elevator.")
            _bare_view(pgh)
            pgh.evaluate("window.__lab.select('r30.top-skin')")
            _run(pgh, 3)
            pgh.evaluate("window.__lab.select('r30.elev-hinge-slots')")
            _run(pgh, 6)
            cv = pgh.evaluate("window.__lab.cove()")
            assert (
                cv["open"]
                and cv["blIn"] == pytest.approx(ex["cove"]["bl_start"])
                and cv["blIn"] > 9.0
            )
            xc = ex["cove"]["x_cut"]
            xa = xc + 1.5  # in the cove's depth, aft of the cut

            def w(x, bl):
                return pgh.evaluate(f"window.__lab.toWorld([{x}, 0.2, {-bl}])")

            c = w(xa, 5)
            pgh.evaluate(
                f"window.__lab.setCamera({[c[0], c[1] + 2.2, c[2] + 0.0001]}, {c})"
            )
            _run(pgh, 0.3)

            def px(bl, x=xa):
                sx, sy = pgh.evaluate(f"window.__lab.project({w(x, bl)})")[:2]
                im = _shot_clip(
                    pgh,
                    {"x": max(0, sx - 2), "y": max(0, sy - 2), "width": 4, "height": 4},
                )
                d = list(im.getdata())
                return tuple(sum(c[i] for c in d) / len(d) for i in range(3))

            def dist(a, b):
                return sum(abs(i - j) for i, j in zip(a, b))

            empty = px(
                30.0
            )  # inside the foam span: the cove is open, nothing behind the cut
            inner = [
                px(bl) for bl in (1.0, 3.0, 6.0, 8.5)
            ]  # (the canard subject shows the right half only) inboard of the foam end: canard material
            fwd = px(3.0, x=xc - 1.5)
            print(f"empty cove {empty}, forward of the cut {fwd}, root samples {inner}")
            assert (
                dist(fwd, empty) > 60
            ), "the view does not tell canard from empty cove"
            for q in inner:
                assert dist(q, empty) > 40 and dist(q, fwd) < 0.6 * dist(fwd, empty), (
                    q,
                    empty,
                    fwd,
                )
            # |B.L.| just inside 9.3 is still material, just outside is the cove
            assert dist(px(9.0), empty) > 40
            assert dist(px(10.2), empty) < 40
            assert not errors, errors
            b.close()
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('r30.elev-fuselage-clearance')")
            _run(pg, 4)
            cv = pg.evaluate("window.__lab.cove()")
            assert cv["installed"] and cv["blIn"] == pytest.approx(
                ex["cove"]["bl_start"]
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.5: chapters 14-17 in the lab. The spar built on the layup table in its jig and slid into the box from the side, the firewall's
# stainless face, the controls (the stick drives the Roncz elevators), the trim. Every part is a fitted shape (striped, labelled).
# ======================================================================================================================
_M25_SPAR = {
    "spar.box",
    "spar.cap_top",
    "spar.cap_bottom",
    "spar.bulkheads",
    "spar.lwa",
    "spar.spruce_blocks",
    "spar.jig",
}


def _m25_ops(g):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i
        for i in g["order"]
        if byid[i]["chapter"] in (14, 15, 16, 17, 18) and not byid[i]["stub"]
    ], byid


def _m25_rows(g):
    return g["layup"]["fuselage"]["extras"]["m25"]["parts"]


def _m25_expect(g, row, op):
    """'table' | 'jig' | 'none': where a chapter 14-17 part is on `op` (a chapter 14-17 op): on or after its component's first op and
    inside its own show window; the spar's parts are on the table through the last bench op."""
    order, byid, first = _first_ops(g)
    i = order.index(op)
    if i < order.index(first[row["component"]]):
        return "none"
    w = row.get("show") or {}
    if (w.get("from") and i < order.index(w["from"])) or (
        w.get("until") and i >= order.index(w["until"])
    ):
        return "none"
    if row["component"] in _M25_SPAR and i <= order.index("f14.nut-access-hole"):
        return "table"
    return "jig"


def test_m25_every_chapter_14_to_17_op_shows_its_parts_in_build_order_striped_and_labelled_and_the_jig_only_on_the_bench(
    rsite,
):
    g = _graph(rsite)
    ops, byid = _m25_ops(g)
    rows = _m25_rows(g)
    order = g["order"]
    assert len(ops) >= 30 and len(rows) >= 28
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            assert set(ops) <= set(_chips(pg))  # the bar carries every chapter 14-17 op
            for op in ops:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                pl = pg.evaluate("window.__lab.placement()")
                for name, row in rows.items():
                    want = _m25_expect(g, row, op)
                    assert pl[name] == want, (op, name, pl[name], want)
            # the jig is on the bench ops only: from its first op until the box is lifted out (f14.cap-troughs), never in the airplane
            for op in ops:
                on = (
                    order.index("f14.jig")
                    <= order.index(op)
                    < order.index("f14.cap-troughs")
                )
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.2)
                assert (
                    pg.evaluate("window.__lab.placement()")["spar_jig"] == "table"
                ) == on, op
            # nothing of it before chapter 14's ops, nor on the finished box
            for op in ("f09.brake-lines", "r30.f22-drill-tabs", "f13.nose-door", None):
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.4)
                pl = pg.evaluate("window.__lab.placement()")
                assert all(pl[n] == "none" for n in rows), (
                    op,
                    {n: pl[n] for n in rows if pl[n] != "none"},
                )
            # every part is a fitted shape: striped, representational, and says so on screen
            pg.evaluate("window.__lab.select('f16.pitch-pushrod')")
            _run(pg, 1)
            for name, row in rows.items():
                assert (
                    row["fidelity"] == "representational"
                    and row["label"].endswith("(fitted shape)")
                    or "(fitted shape;" in row["label"]
                ), name
                node = row["node"]
                m = pg.evaluate(
                    f"window.__lab.material('{node}') || window.__lab.material('{node}.p1')"
                )
                assert m and m["hatch"] and m["fidelity"] == "representational", (
                    name,
                    m,
                )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _pixels_of(pg, hide, w=1180, h=820):
    """How many pixels of the 3D view change when meshes starting with `hide` are left out of the scene: the cards, bar, labels and glow are off."""
    from PIL import Image, ImageChops

    pg.evaluate("window.__lab.hide([]); window.__lab.advance(0.02)")
    on = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
    pg.evaluate(f"window.__lab.hide({json.dumps(hide)}); window.__lab.advance(0.02)")
    off = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
    pg.evaluate("window.__lab.hide([]); window.__lab.advance(0.02)")
    d = (
        ImageChops.difference(on, off)
        .convert("L")
        .point(lambda v: 255 if v > 30 else 0)
    )
    return sum(d.histogram()[255:])


def _bare(pg):
    pg.add_style_tag(
        content="#controls,#dock,#opbar,#labels,#status,#viewpop{visibility:hidden !important}"
    )


def test_m25_every_op_with_parts_puts_them_on_screen_not_hidden_inside_another_solid(
    rsite,
):
    """M2.4's review shipped parts drawn inside other solids: positions passed, pixels did not. Here the pixels decide: the frame with the op's
    parts and the same frame without them must differ, on every chapter 14-17 op that lists a component."""
    g = _graph(rsite)
    ops, byid = _m25_ops(g)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            _bare(pg)
            seen = {}
            for op in ops:
                comps = byid[op]["components"]
                if not comps:
                    continue
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 6)
                seen[op] = _pixels_of(pg, comps)
            weak = {o: n for o, n in seen.items() if n < 150}
            print({o: n for o, n in seen.items()})
            assert not weak, f"the op's own parts are not visible on screen: {weak}"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("op", ["f14.fit-fuselage", "f16.pitch-pushrod"])
def test_m25_phone_width_keeps_the_subject_on_screen_and_the_page_unscrolled(rsite, op):
    g = _graph(rsite)
    comps = {o["id"]: o for o in g["ops"]}[op]["components"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 390, 844, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate(f"window.__lab.select('{op}')")
            _run(pg, 6)
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390
            assert pg.evaluate("document.documentElement.scrollHeight") <= 844
            if (
                op == "f16.pitch-pushrod"
            ):  # the stick control is reachable and inside the viewport
                r = pg.evaluate(
                    "(() => { const r = document.getElementById('stick-defl').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom] })()"
                )
                assert (
                    r[0] >= 0 and r[2] <= 390 and r[3] <= 844 and r[2] - r[0] > 100
                ), r
            labs = pg.evaluate("window.__lab.labelsAll()")
            assert sum(1 for x in labs if _legible(x)) <= 10
            _bare(pg)
            # the pitch pushrod op's subject on a phone is the stick's elevators (the rod itself is a few pixels at that width)
            hide = ["installed:elevator."] if op == "f16.pitch-pushrod" else comps
            assert _pixels_of(pg, hide, 390, 844) >= 150
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_spar_slides_in_from_the_side_in_sim_time_and_ends_installed(rsite):
    g = _graph(rsite)
    order = g["order"]
    assert order.index("f14.fit-fuselage") < order.index("f06.bond-firewall")
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f14.nut-access-hole')")
            _run(pg, 0.3)
            assert pg.evaluate("window.__lab.placement()")["spar_box"] == "table"
            pg.evaluate("window.__lab.select('f14.fit-fuselage')")
            sl = pg.evaluate("window.__lab.sparSlide()")
            assert sl["distance"] > 56.46 and sl["inches"] == pytest.approx(
                sl["distance"]
            ), sl
            assert pg.evaluate("window.__lab.placement()")["spar_box"] == "jig"
            zs, last = [], None
            for _ in range(70):
                _run(pg, 0.1)
                box = pg.evaluate("window.__lab.meshBox('spar.box')")
                zs.append((box[0][2] + box[1][2]) / 2)
                cur = pg.evaluate("window.__lab.sparSlide()")["inches"]
                assert last is None or cur <= last + 1e-9, (last, cur)
                last = cur
            assert pg.evaluate("window.__lab.sparSlide()")["inches"] == 0
            # it entered along the span (world Z), from the room side, and ended centred on the box
            assert zs[0] > zs[-1] + 1.0 and max(zs) - min(zs) > 1.0, (zs[0], zs[-1])
            assert pg.evaluate("window.__lab.kin()")["value"] == "In the box"
            pg.evaluate("window.__lab.select('f14.bond-spar')")
            _run(pg, 0.3)
            assert pg.evaluate("window.__lab.sparSlide()")["inches"] == 0
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_the_stick_drives_the_roncz_elevators_through_30_down_and_15_up_and_never_shows_20_or_22(
    rsite,
):
    import re

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f16.pitch-pushrod')")
            assert pg.evaluate("window.__lab.stick()")["shown"] is True
            texts, box = set(), {}
            for _ in range(120):  # the op's own sweep: 30 down, then 15 up
                _run(pg, 0.1)
                st = pg.evaluate("window.__lab.stick()")
                texts.add(pg.evaluate("window.__lab.kin().value"))
                for d in (-30.0, 15.0):
                    if st["deflUp"] == pytest.approx(d, abs=1e-6) and d not in box:
                        box[d] = (
                            pg.evaluate("window.__lab.installedCanard()")["boxes"][
                                "installed:elevator.right"
                            ],
                            pg.evaluate(
                                "window.__lab.meshBox('controls.pitch_pushrod')"
                            ),
                            pg.evaluate(
                                "window.__lab.meshBox('controls.sticks.front_stick')"
                            ),
                        )
            assert set(box) == {-30.0, 15.0}, box.keys()
            assert "Down 30.0 deg  (limit 30)" in texts
            assert "Up 15.0 deg  (target 15, floor 12.5)" in texts
            # the limits the readout states are the Roncz row alone (a live angle passing through 20 or 22 on its way is not a limit)
            nums = {
                n
                for t in texts
                for grp in re.findall(r"\(([^)]*)\)", t)
                for n in re.findall(r"[\d.]+", grp)
            }
            assert nums == {"30", "15", "12.5"}, nums
            sub = pg.evaluate("document.getElementById('ro-kin-sub').textContent")
            assert "30 down, 15 up" in sub and not re.search(r"\b(20|22)\b", sub), sub
            # the elevator, the pushrod and the stick all moved between the two limits
            for i in range(3):
                assert box[-30.0][i] != box[15.0][i], i
            # a person's slider takes over, is clamped to the Roncz travel, and says so
            pg.evaluate("window.__lab.setStick(40)")
            assert pg.evaluate("window.__lab.stick()")["deflUp"] == 15
            pg.evaluate("window.__lab.setStick(-60)")
            st = pg.evaluate("window.__lab.stick()")
            assert st["deflUp"] == -30 and st["manual"] is True
            pg.evaluate("window.__lab.select('f16.torque-tubes')")
            assert pg.evaluate("window.__lab.stick()")["shown"] is False
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_pitch_stops_are_striped_labelled_as_unprinted_and_only_from_the_pushrod_op(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f16.sticks-pushrods')")
            _run(pg, 1)
            assert "controls.pitch_stops" not in {
                x["id"] for x in pg.evaluate("window.__lab.labelsAll()") if _legible(x)
            }
            pg.evaluate("window.__lab.select('f16.pitch-pushrod')")
            _run(pg, 4)
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")}
            assert labs["controls.pitch_stops"]["text"] == (
                "Pitch stops (not printed; fitted shape)"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_stainless_face_follows_the_plywood_and_the_firewall_bond_comes_after_the_spar_fit(
    rsite,
):
    g = _graph(rsite)
    order, byid, first = _first_ops(g)
    assert order.index("f14.fit-fuselage") < order.index("f06.bond-firewall")
    assert order.index("f06.bond-firewall") < order.index("f14.bond-spar")
    assert order.index("f15.stainless-firewall") > order.index("f14.bond-spar")
    assert first["fuselage.firewall_stainless"] == "f15.stainless-firewall"
    rows = _m25_rows(g)
    assert rows["fuselage_firewall_stainless"]["fs_min"] >= 125.0


def test_m25_tour_visits_every_chapter_14_to_17_op_in_order_holds_the_slide_and_the_stick_and_ends_on_the_last(
    rsite,
):
    g = _graph(rsite)
    want = [o for ch in (14, 15, 16, 17) for o in _chapter_ops(g, "roncz", ch)]
    assert len(want) >= 30
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            _to_fuselage(pg)
            pg.evaluate(f"__lab.select('{want[0]}')")
            pg.click("#tour")
            assert pg.evaluate("__lab.touring()") is True
            probes = {
                "f14.fit-fuselage": "__lab.sparSlide().inches",
                "f16.pitch-pushrod": "__lab.kin().value",
            }
            seen, last = _tour_probe(pg, want, probes, after="never")
            assert seen == want, seen
            assert (
                last["f14.fit-fuselage"] == 0
            ), last  # the spar had gone in before the tour left the op
            assert (
                last["f16.pitch-pushrod"] == "Up 15.0 deg  (target 15, floor 12.5)"
            ), last
            assert pg.evaluate("__lab.touring()") is False
            assert pg.evaluate("__lab.selected()") == want[-1]
            assert pg.evaluate("__lab.subject()") == "fuselage"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_cap_plies_lay_down_in_build_order_top_12_then_bottom_9(rsite):
    g = _graph(rsite)
    nodes = g["layup"]["fuselage"]["extras"]["m25"]["nodes"]
    top = sorted(
        (k for k in nodes if k.startswith("spar.cap_top.")),
        key=lambda k: nodes[k]["op_order"],
    )
    bot = sorted(
        (k for k in nodes if k.startswith("spar.cap_bottom.")),
        key=lambda k: nodes[k]["op_order"],
    )
    assert (len(top), len(bot)) == (12, 9)
    assert all(
        nodes[k]["op"] == "f14.spar-caps" and nodes[k]["cloth"] == "UND"
        for k in top + bot
    )
    assert sorted(n["op_order"] for n in nodes.values()) == list(range(1, 22))
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f14.spar-caps')")
            _run(pg, 0.3)
            assert pg.evaluate("window.__lab.lay()") == 21
            pg.evaluate("window.__lab.setLay(5)")
            _run(pg, 4)
            st = pg.evaluate("window.__lab.stateAll()")
            built = [k for k in top if st[k] in ("built", "current")]
            assert (
                built == top[:5]
            ), built  # the first five plies of the op, in lay order
            assert all(st[k] == "hidden" for k in top[5:] + bot)
            pg.evaluate("window.__lab.setLay(21)")
            _run(pg, 4)
            st = pg.evaluate("window.__lab.stateAll()")
            assert all(st[k] in ("built", "current") for k in top + bot)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_the_station_cut_passes_through_the_installed_spar_and_the_slider_reaches_its_swept_aft_face(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f14.sh1-tabs')")
            _run(pg, 0.5)
            assert float(pg.get_attribute("#section-bl", "max")) >= 129.9
            pg.evaluate("window.__lab.setSection(true, 121.7)")
            _run(pg, 1)
            c = pg.evaluate("window.__lab.cut()")
            assert c["enabled"] and c["keepsAft"] and c["removesForward"], c
            assert "spar.box" in c["cappedNodes"], c["cappedNodes"]
            # a bench op has the spar on the table: the cut (the box's) does not open it
            pg.evaluate("window.__lab.select('f14.close-box')")
            _run(pg, 0.5)
            assert "spar.box" not in pg.evaluate("window.__lab.cut()")["cappedNodes"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_pitch_pushrod_shot_shows_the_stick_and_the_elevators_and_the_elevators_move_on_screen_with_the_stick(
    rsite,
):
    """Round 2 F1: the op's own camera shows the stick and the Roncz elevators together; between 30 down and 15 up the pixels over the
    elevators differ."""
    from PIL import Image, ImageChops

    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            _bare(pg)
            pg.evaluate("window.__lab.select('f16.pitch-pushrod')")
            _run(pg, 6)
            frames, boxes = {}, []
            for d in (-30, 15):
                pg.evaluate(f"window.__lab.setStick({d}); window.__lab.advance(0.05)")
                frames[d] = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
                ib = pg.evaluate("window.__lab.installedCanard()")["boxes"]
                boxes += [ib["installed:elevator.right"], ib["installed:elevator.left"]]
            clip = _screen_clip(pg, boxes, 1180, 820, pad=6)
            box = (
                int(clip["x"]),
                int(clip["y"]),
                int(clip["x"] + clip["width"]),
                int(clip["y"] + clip["height"]),
            )
            d = (
                ImageChops.difference(frames[-30].crop(box), frames[15].crop(box))
                .convert("L")
                .point(lambda v: 255 if v > 30 else 0)
            )
            moved = d.histogram()[255]
            assert moved > 400, f"the elevators do not move on screen: {moved} px"
            # the stick and the elevators are in this one frame (the stick's own pixels differ with it hidden)
            pg.evaluate("window.__lab.setStick(0); window.__lab.advance(0.05)")
            assert _pixels_of(pg, ["controls.sticks"]) >= 100
            assert pg.evaluate("window.__lab.installedCanard()")["shown"] is True
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m25_spar_reference_row_from_the_bond_on_and_never_in_the_cg(rsite):
    import json as _j

    led = _j.loads((rsite / "ledger.json").read_text())
    assert led["prototype_weights"]["rows"]["spar"]["weight_lb"] == 29.3
    assert "spar" not in led["cg"]["included"] + led["cg_lower_bound"]["included"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op, want in (
                ("f14.fit-fuselage", None),
                (
                    "f14.bond-spar",
                    "Spar (CP26 builder weight, N26MS): 29.3 lb, reference, not in CG",
                ),
                (
                    "f16.pitch-pushrod",
                    "Spar (CP26 builder weight, N26MS): 29.3 lb, reference, not in CG",
                ),
                ("f13.nose-door", None),
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                r = pg.evaluate("window.__lab.ref()")
                assert (r["value"] if r else None) == want, (op, r)
                shown = pg.evaluate(
                    "!document.getElementById('t-ref').hidden && document.getElementById('ro-ref').textContent"
                )
                assert (shown or None) == want, (op, shown)
                assert pg.evaluate("window.__lab.cg()")["value"] == "not yet computed"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# ======================================================================================================================
# Block 2 M2.6: chapter 18, the canopy (trimmed on the bench, built in place, cut free and turned over on the bench, hinged on the right).
# ======================================================================================================================
_M26_LIFT = {
    "canopy.plexi",
    "canopy.frame",
    "canopy.pads",
    "canopy.vent",
    "canopy.brace_tubes",
}


def _flat(bx):
    return [x for row in bx for x in row]


def _m26_ops(g):
    byid = {o["id"]: o for o in g["ops"]}
    return [
        i for i in g["order"] if byid[i]["chapter"] == 18 and not byid[i]["stub"]
    ], byid


def _m26(g):
    return g["layup"]["fuselage"]["extras"]["m26"]


def _m26_expect(g, row, op):
    """'table' | 'jig' | 'none': where a chapter 18 part is on `op`. On or after its component's first op and inside its own show window; the
    parts that come off with the canopy are on the bench upright while the bubble is trimmed and upside down from the cut to the vent op."""
    order, byid, first = _first_ops(g)
    i = order.index(op)
    if i < order.index(first[row["component"]]):
        return "none"
    if row["node"] == "canopy.frame_glass" and i < order.index("f18.glass-outside"):
        return "none"  # the plies are laid by that op
    w = row.get("show") or {}
    if (w.get("from") and i < order.index(w["from"])) or (
        w.get("until") and i >= order.index(w["until"])
    ):
        return "none"
    if row["component"] in _M26_LIFT:
        if order.index("f18.trim-plexi") <= i < order.index("f18.locate-blocks"):
            return "table"
        if order.index("f18.cut-remove") <= i <= order.index("f18.vent-brace"):
            return "table"
    return "jig"


def test_m26_every_chapter_18_op_shows_its_parts_in_build_order_striped_and_labelled_and_the_blocks_only_in_their_ops(
    rsite,
):
    g = _graph(rsite)
    ops, byid = _m26_ops(g)
    rows = _m26(g)["parts"]
    order = g["order"]
    assert len(ops) == 16 and len(rows) == 19
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            assert set(ops) <= set(_chips(pg))  # the bar carries every chapter 18 op
            for op in ops:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                pl = pg.evaluate("window.__lab.placement()")
                for name, row in rows.items():
                    want = _m26_expect(g, row, op)
                    assert pl[name] == want, (op, name, pl[name], want)
            # the temporary blocks exist on the ops where the canopy rests on them (until the inside is carved), never elsewhere
            for op in ops + ["f17.fixed-trim-tab", "f09.brake-lines", None]:
                on = (
                    op is not None
                    and op in order
                    and order.index("f18.locate-blocks")
                    <= order.index(op)
                    < order.index("f18.carve-inside")
                )
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.2)
                assert (
                    pg.evaluate("window.__lab.placement()")["canopy_blocks"] == "jig"
                ) == on, op
            # nothing of the canopy before chapter 18's ops, nor on the finished box
            for op in ("f17.fixed-trim-tab", "f14.fit-fuselage", "f13.nose-door", None):
                pg.evaluate(f"window.__lab.select({json.dumps(op)})")
                _run(pg, 0.4)
                pl = pg.evaluate("window.__lab.placement()")
                assert all(pl[n] == "none" for n in rows), (
                    op,
                    {n: pl[n] for n in rows if pl[n] != "none"},
                )
            # the chapter 14-17 parts stay on through chapter 18 (the spar, the controls)
            pg.evaluate("window.__lab.select('f18.hinges')")
            _run(pg, 0.3)
            pl = pg.evaluate("window.__lab.placement()")
            assert (
                pl["spar_box"] == "jig" and pl["controls_sticks_front_stick"] == "jig"
            )
            # every part is a fitted shape: striped, representational, and says so on screen
            pg.evaluate("window.__lab.select('f18.safety-catch')")
            _run(pg, 1)
            for name, row in rows.items():
                assert (
                    row["fidelity"] == "representational"
                    and "(fitted shape" in row["label"]
                ), name
                node = (
                    "canopy.frame.p1"
                    if row["node"] == "canopy.frame_glass"
                    else row["node"]
                )
                m = pg.evaluate(f"window.__lab.material('{node}')")
                assert m and m["hatch"] and m["fidelity"] == "representational", (
                    name,
                    m,
                )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


# what each op that adds something shows, as the part-name prefixes to leave out of the frame: the pixels that differ are that part on screen
_M26_SUBJECT = {
    "f18.trim-plexi": ["canopy.plexi"],
    "f18.locate-blocks": ["canopy.blocks"],
    "f18.check-ab": ["canopy.plexi"],
    "f18.foam-core": ["canopy.frame_foam"],
    "f18.carve-outside": ["canopy.frame_carved"],
    "f18.glass-outside": ["canopy.frame.p"],
    "f18.cut-remove": ["canopy.plexi", "canopy.frame"],
    "f18.carve-inside": ["canopy.pads"],
    "f18.pads-inside-glass": ["canopy.pads"],
    "f18.rear-cover-inside": ["fuselage.rear_cover"],
    "f18.vent-brace": ["canopy.vent", "canopy.brace_tubes"],
    "f18.hinges": ["canopy.hinges", "canopy.plexi"],
    "f18.door": ["fuselage.door"],
    "f18.latches": ["canopy.latches"],
    "f18.front-cover": ["fuselage.front_cover"],
    "f18.safety-catch": ["canopy.safety_catch"],
}


def test_m26_every_chapter_18_op_puts_its_subject_on_screen_not_hidden_inside_another_solid(
    rsite,
):
    """Pixels decide: the frame with the op's subject and the same frame without it must differ, for the op's own parts and for the one thing
    each op adds (the blocks, the foam, the plies, the pads, the leaves, the latches, the door, the catch)."""
    g = _graph(rsite)
    ops, byid = _m26_ops(g)
    assert set(_M26_SUBJECT) == set(ops)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            _bare(pg)
            seen_all, seen_one = {}, {}
            for op in ops:
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 6)
                seen_all[op] = _pixels_of(pg, byid[op]["components"])
                seen_one[op] = _pixels_of(pg, _M26_SUBJECT[op])
            print(seen_all, seen_one)
            weak = {o: n for o, n in seen_all.items() if n < 150}
            assert not weak, f"the op's own parts are not visible on screen: {weak}"
            weak = {o: n for o, n in seen_one.items() if n < 120}
            assert not weak, f"what the op adds is not visible on screen: {weak}"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


@pytest.mark.parametrize("op", ["f18.hinges", "f18.cut-remove"])
def test_m26_phone_width_keeps_the_subject_on_screen_and_the_page_unscrolled(rsite, op):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 390, 844, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate(f"window.__lab.select('{op}')")
            _run(pg, 7)
            assert pg.evaluate("document.documentElement.scrollWidth") <= 390
            assert pg.evaluate("document.documentElement.scrollHeight") <= 844
            if (
                op == "f18.hinges"
            ):  # the opening control is reachable and inside the viewport
                r = pg.evaluate(
                    "(() => { const r = document.getElementById('canopy-open').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom] })()"
                )
                assert (
                    r[0] >= 0 and r[2] <= 390 and r[3] <= 844 and r[2] - r[0] > 100
                ), r
            labs = pg.evaluate("window.__lab.labelsAll()")
            assert sum(1 for x in labs if _legible(x)) <= 10
            _bare(pg)
            assert _pixels_of(pg, _M26_SUBJECT[op], 390, 844) >= 150
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_plexiglass_reads_as_glass_not_invisible_and_not_opaque(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f18.locate-blocks')")
            _run(pg, 6)
            m = pg.evaluate("window.__lab.material('canopy.plexi')")
            assert m["transparent"] is True and 0.2 <= m["opacity"] <= 0.6, m
            _bare(pg)
            # on screen (it differs from the frame without it) yet see-through: the blocks it sits over still show with it in place
            assert _pixels_of(pg, ["canopy.plexi"]) >= 1500
            both = _pixels_of(pg, ["canopy.blocks"])
            assert both >= 120, both  # the blocks are visible through the glass
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_canopy_opens_on_its_right_hinges_up_to_15_past_vertical_and_the_readout_says_so(
    rsite,
):
    from PIL import Image, ImageChops

    g = _graph(rsite)
    h = _m26(g)["canopy"]["hinge"]
    assert h["max_open_deg"] == 105 and h["past_vertical_deg"] == 15
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f18.hinges')")
            c = pg.evaluate("window.__lab.canopy()")
            assert c["shown"] is True and c["openDeg"] == 0 and c["manual"] is False, c
            assert pg.evaluate("window.__lab.kin().value") == "Closed"
            _run(pg, 0.1)
            cz = lambda bx: (bx[0][2] + bx[1][2]) / 2  # noqa: E731
            closed = pg.evaluate("window.__lab.meshBox('canopy.plexi')")
            hinge0 = pg.evaluate("window.__lab.meshBox('canopy.hinges.hinge_fuselage')")
            leaf0 = pg.evaluate("window.__lab.meshBox('canopy.hinges.hinge_canopy')")
            last, texts = 0.0, set()
            for _ in range(80):  # the op's own sweep, in sim time: monotone to 105
                _run(pg, 0.1)
                d = pg.evaluate("window.__lab.canopy()")["openDeg"]
                assert d >= last - 1e-9, (last, d)
                last = d
                texts.add(pg.evaluate("window.__lab.kin().value"))
            assert last == 105
            assert "105 deg open: 15 deg past vertical, representational" in texts
            assert any(
                t.endswith("deg open") for t in texts
            )  # on its way, it reads as an angle
            opened = pg.evaluate("window.__lab.meshBox('canopy.plexi')")
            # it swung to the right (B.L. grows toward the window wall, model Z falls) and up and out; the fuselage leaves of the hinges stay, the canopy leaves go
            assert cz(opened) < cz(closed) - 0.3, (cz(closed), cz(opened))
            assert _flat(
                pg.evaluate("window.__lab.meshBox('canopy.hinges.hinge_fuselage')")
            ) == pytest.approx(_flat(hinge0))
            assert _flat(
                pg.evaluate("window.__lab.meshBox('canopy.hinges.hinge_canopy')")
            ) != pytest.approx(_flat(leaf0), abs=1e-3)
            # the pixels over the canopy differ between closed and open
            _bare(pg)
            frames = {}
            for d in (0, 105):
                pg.evaluate(
                    f"window.__lab.setCanopyOpen({d}); window.__lab.advance(0.05)"
                )
                frames[d] = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            diff = (
                ImageChops.difference(frames[0], frames[105])
                .convert("L")
                .point(lambda v: 255 if v > 30 else 0)
            )
            assert diff.histogram()[255] > 4000, diff.histogram()[255]
            # a person's slider takes over, is clamped to the range, and reads as an angle
            pg.evaluate("window.__lab.setCanopyOpen(45)")
            c = pg.evaluate("window.__lab.canopy()")
            assert (
                c["openDeg"] == 45
                and c["manual"] is True
                and c["text"] == "45 deg open"
            )
            pg.evaluate("window.__lab.setCanopyOpen(300)")
            assert pg.evaluate("window.__lab.canopy()")["openDeg"] == 105
            pg.evaluate("window.__lab.setCanopyOpen(-5)")
            assert pg.evaluate("window.__lab.canopy()")["openDeg"] == 0
            # on the other ops it is closed and the control is not offered
            pg.evaluate("window.__lab.select('f18.door')")
            _run(pg, 0.3)
            c = pg.evaluate("window.__lab.canopy()")
            assert c["openDeg"] == 0 and c["shown"] is False
            assert _flat(
                pg.evaluate("window.__lab.meshBox('canopy.plexi')")
            ) == pytest.approx(_flat(closed))
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_cut_leaves_the_covers_and_the_canopy_lifts_off_and_turns_upside_down_on_the_bench(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            box = lambda n: pg.evaluate(f"window.__lab.meshBox('{n}')")  # noqa: E731
            mid = lambda bx: [(bx[0][i] + bx[1][i]) / 2 for i in range(3)]  # noqa: E731
            # trimmed on the bench, upright: the dome above its rim; then in place on the airplane
            pg.evaluate("window.__lab.select('f18.trim-plexi')")
            _run(pg, 0.5)
            pl = pg.evaluate("window.__lab.placement()")
            assert pl["canopy_plexi"] == "table" and pl["canopy_blocks"] == "none"
            on_bench_up = mid(box("canopy.plexi"))
            pg.evaluate("window.__lab.select('f18.glass-outside')")
            _run(pg, 7)
            in_place = mid(box("canopy.plexi"))
            assert (
                in_place[2] > on_bench_up[2] + 2.0
            ), "on the airplane (room side), the bench is toward the wall"
            front = box("fuselage.front_cover")
            # the cut: the canopy starts on the airplane, goes up and over and ends upside down on the table; the covers and the blocks stay
            pg.evaluate("window.__lab.select('f18.cut-remove')")
            assert pg.evaluate("window.__lab.canopy()")["liftK"] == 0
            _run(pg, 0.3)
            start = mid(box("canopy.plexi"))
            assert all(abs(a - b_) < 0.05 for a, b_ in zip(start, in_place)), (
                start,
                in_place,
            )
            ys, zs, lifts = [], [], []
            for _ in range(80):
                _run(pg, 0.1)
                m = mid(box("canopy.plexi"))
                ys.append(m[1])
                zs.append(m[2])
                lifts.append(pg.evaluate("window.__lab.canopy()")["liftK"])
                pl = pg.evaluate("window.__lab.placement()")
                assert (
                    pl["fuselage_front_cover"] == "jig"
                    and pl["fuselage_rear_cover"] == "jig"
                ), "the covers stay on the fuselage"
                assert (
                    pl["canopy_blocks"] == "jig"
                ), "the blocks are left on the longerons"
            assert lifts == sorted(lifts) and lifts[-1] == 1
            assert zs[0] > zs[-1] + 2.0 and all(
                zs[i] >= zs[i + 1] - 1e-9 for i in range(len(zs) - 1)
            ), "it travels toward the bench"
            assert (
                max(ys) > ys[0] + 0.25 and max(ys) > ys[-1] + 0.25
            ), "it goes up and over, not straight across"
            on_bench_down = mid(box("canopy.plexi"))
            assert on_bench_up[0] == pytest.approx(
                on_bench_down[0], abs=0.02
            ) and on_bench_up[2] == pytest.approx(
                on_bench_down[2], abs=0.02
            ), "the same place on the table"
            assert _flat(box("fuselage.front_cover")) == pytest.approx(
                _flat(front)
            )  # nothing of the cover moved
            # upside down: the sill (the pads on it) is above the dome; in place it was below
            pg.evaluate("window.__lab.select('f18.carve-inside')")
            _run(pg, 0.5)
            assert (
                pg.evaluate("window.__lab.placement()")["canopy_blocks"] == "none"
            ), "discarded once the inside is carved"
            pads = mid(box("canopy.pads.pads_hinge"))
            dome = mid(box("canopy.plexi"))
            assert pads[1] > dome[1] + 0.05, "turned over: the sill is up"
            pg.evaluate("window.__lab.select('f18.hinges')")
            _run(pg, 0.3)
            assert (
                mid(box("canopy.pads.pads_hinge"))[1]
                < mid(box("canopy.plexi"))[1] - 0.02
            ), "back on the airplane, right side up"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _cyan_pixels(png):
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(int)
    r, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
    # the dimension lines are drawn flat in a cyan nothing else in the scene is (the picture goes through grading, so match the hue, not the exact value)
    return int(((b_ > 180) & (r < 110) & (g_ > 140) & (b_ - r > 110)).sum())


def test_m26_checks_a_and_b_are_dimension_lines_above_wl_23_on_their_op_only(rsite):
    g = _graph(rsite)
    checks = _m26(g)["canopy"]["checks"]
    assert [(c["id"], c["height_in"], c["wl0"]) for c in checks] == [
        ("A", 13.5, 23.0),
        ("B", 12.3, 23.0),
    ]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            _bare(pg)
            pg.evaluate("window.__lab.select('f18.check-ab')")
            _run(pg, 6)
            assert pg.evaluate("window.__lab.canopy()")["checks"] is True
            on = _cyan_pixels(pg.screenshot())
            assert on > 300, on
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")}
            assert (
                labs["canopy.check.A"]["text"]
                == "Check A: at least 13.5 in above WL 23"
            )
            assert labs["canopy.check.B"]["text"] == "Check B: 12.3 in above WL 23"
            assert _legible(labs["canopy.check.A"]) and _legible(labs["canopy.check.B"])
            assert (
                pg.evaluate("window.__lab.kin().value")
                == "A at least 13.5 in, B 12.3 in, above WL 23"
            )
            for op in ("f18.locate-blocks", "f18.foam-core"):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 4)
                assert pg.evaluate("window.__lab.canopy()")["checks"] is False
                assert _cyan_pixels(pg.screenshot()) < 40, op
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_frame_is_foam_blocks_then_carved_then_five_plies_laid_groove_ply_first(
    rsite,
):
    g = _graph(rsite)
    nodes = _m26(g)["nodes"]
    order = sorted(nodes, key=lambda k: nodes[k]["op_order"])
    assert order == [f"canopy.frame.p{i}" for i in range(1, 6)]
    assert [nodes[k]["cloth"] for k in order] == ["BID", "BID", "UND", "BID", "UND"]
    assert "groove" in nodes[order[0]]["where"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            _run(pg, 0.1)
            for op, shown in (
                ("f18.foam-core", "canopy.frame_foam"),
                ("f18.carve-outside", "canopy.frame_carved"),
                ("f18.glass-outside", "canopy.frame_carved"),
                ("f18.carve-inside", "canopy.frame"),
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                pl = pg.evaluate("window.__lab.placement()")
                on = {
                    k
                    for k in (
                        "canopy_frame_foam",
                        "canopy_frame_carved",
                        "canopy_frame",
                    )
                    if pl[k] != "none"
                }
                assert on == {shown.replace(".", "_")}, (op, on)
            pg.evaluate("window.__lab.select('f18.glass-outside')")
            _run(pg, 0.3)
            assert pg.evaluate("window.__lab.lay()") == 5
            for n in (1, 3):
                pg.evaluate(f"window.__lab.setLay({n})")
                _run(pg, 4)
                st = pg.evaluate("window.__lab.stateAll()")
                laid = [k for k in order if st[k] in ("built", "current")]
                assert laid == order[:n], (
                    n,
                    laid,
                )  # in lay order; the groove ply first
                assert all(st[k] == "hidden" for k in order[n:])
            pg.evaluate("window.__lab.select('f18.carve-inside')")
            _run(pg, 0.3)
            st = pg.evaluate("window.__lab.stateAll()")
            assert all(st[k] == "built" for k in order)
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_eight_pads_are_coloured_by_role_and_named_hinge_latch_and_catch(rsite):
    g = _graph(rsite)
    rows = _m26(g)["parts"]
    roles = {r["role"]: r for r in rows.values() if r.get("role")}
    assert set(roles) == {"hinge", "latch", "catch"}
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f18.carve-inside')")
            _run(pg, 6)
            colours = {
                r: pg.evaluate(f"window.__lab.material('{roles[r]['node']}')")["color"]
                for r in roles
            }
            assert len(set(colours.values())) == 3, colours
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labelsAll()")}
            assert (
                labs[roles["hinge"]["node"]]["text"]
                == "Hinge pads, right, 4 (fitted shape)"
            )
            assert (
                labs[roles["latch"]["node"]]["text"]
                == "Latch pads, left, 3 (fitted shape)"
            )
            assert (
                labs[roles["catch"]["node"]]["text"]
                == "Safety-catch pad, left (fitted shape)"
            )
            assert all(_legible(labs[roles[r]["node"]]) for r in roles)
            sub = pg.evaluate("document.getElementById('ro-kin-sub').textContent")
            assert (
                "Hinge pads blue" in sub
                and "latch pads green" in sub
                and "catch pad red" in sub
            ), sub
            assert "20, 25.5, 48, 53.5" in pg.evaluate("window.__lab.kin().value")
            assert "11, 41, 59 (safety catch), 71" in sub
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_the_latch_conflict_and_the_front_cut_datum_are_text_in_the_readout_on_their_ops_never_a_bare_number(
    rsite,
):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            pg.evaluate("window.__lab.select('f18.latches')")
            _run(pg, 0.3)
            k = pg.evaluate("window.__lab.kin()")
            assert k["value"] == "Pad centres FS 104.75, 74.75, 44.75 (derived)"
            assert (
                "printed labels read 104, 74, 44" in k["sub"]
                and "0.75 in apart, unresolved" in k["sub"]
            )
            assert pg.evaluate("document.getElementById('t-kin').hidden") is False
            assert "unresolved" in pg.evaluate(
                "document.getElementById('ro-kin-sub').textContent"
            )
            for op in ("f18.cut-remove", "f18.front-cover"):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                v = pg.evaluate("document.getElementById('ro-kin').textContent")
                assert (
                    v == "Front cut about FS 41.65, datum not named (representational)"
                ), (op, v)
            # neither is stated on the other ops
            pg.evaluate("window.__lab.select('f18.hinges')")
            assert "41.65" not in pg.evaluate(
                "document.getElementById('ro-kin').textContent"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_canopy_reference_row_from_the_last_op_and_never_in_the_cg(rsite):
    import json as _j

    led = _j.loads((rsite / "ledger.json").read_text())
    assert led["prototype_weights"]["rows"]["canopy"]["weight_lb"] == 16.0
    assert "canopy" not in led["cg"]["included"] + led["cg_lower_bound"]["included"]
    want = "Canopy (CP26 builder weight, N26MS): 16.0 lb, reference, not in CG"
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 1180, 820, query="&freeze=1")
            _to_fuselage(pg)
            for op, w in (
                ("f18.trim-plexi", None),
                ("f18.hinges", None),
                ("f18.front-cover", None),
                ("f18.safety-catch", want),
                (
                    "f17.fixed-trim-tab",
                    "Spar (CP26 builder weight, N26MS): 29.3 lb, reference, not in CG",
                ),
            ):
                pg.evaluate(f"window.__lab.select('{op}')")
                _run(pg, 0.3)
                r = pg.evaluate("window.__lab.ref()")
                assert (r["value"] if r else None) == w, (op, r)
                shown = pg.evaluate(
                    "!document.getElementById('t-ref').hidden && document.getElementById('ro-ref').textContent"
                )
                assert (shown or None) == w, (op, shown)
                assert pg.evaluate("window.__lab.cg()")["value"] == "not yet computed"
            # the whole sentence is on screen (it wraps rather than clipping)
            pg.evaluate("window.__lab.select('f18.safety-catch')")
            _run(pg, 0.3)
            clip = pg.evaluate(
                "(() => { const e = document.getElementById('ro-ref'); return e.scrollWidth <= e.clientWidth + 1 })()"
            )
            assert clip is True
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_m26_tour_visits_every_chapter_18_op_in_order_holds_the_lift_and_the_opening_and_ends_on_the_last(
    rsite,
):
    g = _graph(rsite)
    want = _chapter_ops(g, "roncz", 18)
    assert len(want) == 16
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            _to_fuselage(pg)
            pg.evaluate(f"__lab.select('{want[0]}')")
            pg.click("#tour")
            assert pg.evaluate("__lab.touring()") is True
            probes = {
                "f18.cut-remove": "__lab.canopy().liftK",
                "f18.hinges": "__lab.canopy().openDeg",
            }
            seen, last = _tour_probe(pg, want, probes, after="never")
            assert seen == want, seen
            assert (
                last["f18.cut-remove"] == 1
            ), last  # the canopy was on the bench before the tour left the cut
            assert (
                last["f18.hinges"] == 105
            ), last  # and open to 15 past vertical before it left the hinges
            assert pg.evaluate("__lab.touring()") is False
            assert pg.evaluate("__lab.selected()") == want[-1]
            assert pg.evaluate("__lab.subject()") == "fuselage"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
