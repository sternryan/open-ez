"""Lab engine: the page at /lab/ loads the canard, fills the viewport, and its op bar drives the step card and the camera."""
import functools
import json
import http.server
import io
import threading
import time

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


def _open(p, url, w, h, init=None, query="", q="low"):
    b = p.chromium.launch(args=GL)
    ctx = b.new_context(viewport={"width": w, "height": h})
    if init:
        ctx.add_init_script(init)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url + "lab/?test=1" + (f"&q={q}" if q else "") + query)
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
                gap = pg.evaluate("document.getElementById('dock').getBoundingClientRect().top - document.getElementById('controls').getBoundingClientRect().bottom")
                assert gap >= 300, gap  # the dock is the readout line over the step card
                assert pg.evaluate("document.getElementById('readout').getBoundingClientRect().height") <= 44  # one compact line
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


def _expected_state(g, variant, cur, lay, ghost):
    """Independent restatement of the build rule, from graph.json alone: earlier ops built, the current op's laid plies (and its
    whole-part meshes) current, everything later hidden, or ghost when the toggle is on."""
    byid = {o["id"]: o for o in g["ops"]}
    order = [i for i in g["order"] if variant in byid[i]["variants"] or "both" in byid[i]["variants"]]
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
            out[r["node"]] = "hidden" if i is None else "built" if i < idx[cur] else ("current" if r["order"] <= lay else later) if i == idx[cur] else later
    for c in g["components"]:
        if c in g["plies"]:
            continue
        i = idx.get(first.get(c))
        out[c] = "hidden" if i is None else "built" if i < idx[cur] else "current" if i == idx[cur] else later
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
                    assert set(state) <= set(want) and {k: want[k] for k in state} == state, (ghost, lay)  # every mesh, and only meshes that exist
                    if lay == 1:
                        for k in (2, 3, 4):
                            assert state[f"canard.skin_top.p{k}"] == ("ghost" if ghost else "hidden")
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
            assert pg.evaluate(f"window.__lab.phase('{cap}')") == {"state": "built", "unroll": 1, "front": 1, "cure": 1}
            assert pg.evaluate(f"window.__lab.material('{cap}').wet") == 0
            assert pg.evaluate("window.__lab.state()")["canard.skin_bottom.p1"] == "hidden"
            pg.evaluate("window.__lab.setLay(1)")  # the first skin ply unrolls, dry; the cap next to it stays cured
            pg.evaluate("window.__lab.advance(0.6)")
            ph = pg.evaluate("window.__lab.phase('canard.skin_bottom.p1')")
            assert ph["state"] == "current" and abs(ph["unroll"] - 0.5) < 1e-9 and ph["front"] == 0
            assert pg.evaluate(f"window.__lab.material('{cap}').wet") == 0
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_play_lays_every_ply_then_cures_and_stops_and_time_only_moves_with_advance(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 960, 600)
            pg.evaluate("window.__lab.freeze(true)")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert pg.evaluate("window.__lab.play()") is True
            assert pg.evaluate("window.__lab.lay()") == 1
            assert pg.evaluate("document.querySelector('#play').getAttribute('aria-pressed')") == "true"
            time.sleep(0.3)
            assert pg.evaluate("window.__lab.phase('canard.skin_top.p1').unroll") == 0  # frozen: wall-clock time does not move it
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
                assert pg.evaluate(f"window.__lab.phase('canard.skin_top.p{k}').cure") == 1
                assert pg.evaluate(f"window.__lab.material('canard.skin_top.p{k}').wet") == 0
            assert pg.evaluate("document.querySelector('#play').getAttribute('aria-pressed')") == "false"
            assert pg.evaluate("window.__lab.play()") is True  # Play again starts over from ply 1
            assert pg.evaluate("window.__lab.lay()") == 1
            assert pg.evaluate("window.__lab.play()") is False  # a second press while playing stops it
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
    rows = sorted((n for k, n in g["layup"]["nodes"].items() if (n["bl_max"] is None or bl <= n["bl_max"]) and (alive is None or k in alive)),
                  key=lambda n: (n["op_index"], n["order"]))
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
        out.append(f'{_lab_of(g, cid)}: ' + ", ".join(f"{v} {k}" for k, v in cl.items()))
    return " · ".join(out)


def test_section_readout_lists_the_layers_cut_there(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            assert pg.get_attribute("#section-bl", "max") == str(g["layup"]["semi_span"]) and pg.get_attribute("#section-bl", "min") == "0"
            assert pg.get_attribute("#section-bl", "step") == "0.5" and pg.is_visible("#section")
            assert pg.inner_text("#ro-station") == "Section off"
            pg.click("#section-on")  # the real controls, once
            pg.eval_on_selector("#section-bl", "(e) => { e.value = 40; e.dispatchEvent(new Event('input', {bubbles: true})); }")
            assert pg.inner_text("#ro-station") == "B.L. 40" and pg.inner_text("#section-station") == "B.L. 40"
            txt = pg.inner_text("#ro-layers")
            assert _want_layers(g, 40) in txt and _lab_of(g, "canard.core") in txt, (txt, _want_layers(g, 40))
            assert pg.get_attribute("#ro-layers", "title") == pg.evaluate("document.getElementById('ro-layers').textContent")  # phone: the full text lives in the title
            assert pg.get_attribute("#readout", "aria-live") == "polite"
            pg.evaluate("window.__lab.setSection(true, 12.5)")  # the slider steps 0.5; fmtBl rounding is unit-tested
            assert pg.inner_text("#ro-station") == "B.L. 12.5"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_section_readout_lists_only_built_layers(rsite):
    """The plane cuts every visible layer and only those: at the shear-web op the skins and spar caps are not built yet."""
    g = _graph(rsite)
    later = ["canard.skin_top", "canard.skin_bottom", "canard.spar_cap_top", "canard.spar_cap_bottom"]
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            pg.evaluate("window.__lab.setSection(true, 20)")
            txt = pg.inner_text("#ro-layers")
            assert _lab_of(g, "canard.shear_web") in txt and _lab_of(g, "canard.core") in txt, txt
            assert not [c for c in later if _lab_of(g, c) in txt], txt
            pg.evaluate("window.__lab.ghost(true)")  # future work drawn see-through is still not built: not a layer of the cut
            assert not [c for c in later if _lab_of(g, c) in pg.inner_text("#ro-layers")]
            pg.evaluate("window.__lab.ghost(false)")
            pg.evaluate("window.__lab.setLay(1)")  # one ply into the web op: only ply 1 is built, so only ply 1 is listed
            web = [n for n in g["layup"]["nodes"].values() if n["component"] == "canard.shear_web" and n["order"] <= 1 and (n["bl_max"] is None or 20 <= n["bl_max"])]
            assert len(web) == 1
            assert f'{_lab_of(g, "canard.shear_web")}: 1 {web[0]["cloth"]}' in pg.inner_text("#ro-layers")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            txt = pg.inner_text("#ro-layers")
            assert all(_lab_of(g, c) in txt for c in later + ["canard.shear_web", "canard.core"]), txt
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
            want = {n for n, v in g["layup"]["nodes"].items() if (v["bl_max"] is None or bl <= v["bl_max"]) and n in have}
            c = pg.evaluate("window.__lab.cut()")
            capped = set(c["cappedNodes"])
            assert capped - {"canard.core"} == want, (bl, capped ^ want)
            assert "canard.core" in capped
            assert set(c["capNodesVisible"]) == capped and c["capsVisible"] == len(capped)  # every cap the shader will draw is a capped solid
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
            bad = [n for n in c["capNodesVisible"] if n.startswith(("canard.skin_", "canard.spar_cap_"))]
            assert not bad and "canard.shear_web.p1" in c["capNodesVisible"], c["capNodesVisible"]
            pg.evaluate("window.__lab.ghost(true)")  # ghosted future work does not cap either
            assert not [n for n in pg.evaluate("window.__lab.cut().capNodesVisible") if n.startswith(("canard.skin_", "canard.spar_cap_"))]
            pg.evaluate("window.__lab.ghost(false)")
            pg.evaluate("window.__lab.setSection(false, 20)")
            assert pg.evaluate("window.__lab.cut().capsVisible") == 0
            pg.evaluate("window.__lab.setSection(true, 20)")
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert any(n.startswith("canard.skin_top") for n in pg.evaluate("window.__lab.cut().capNodesVisible"))
            pg.evaluate("window.__lab.select('r30.templates-cores')")  # back to a core-only build: nothing else may keep a cap
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
            assert box["min"][2] == pytest.approx(-30, abs=0.01) and box["max"][2] == pytest.approx(0, abs=0.01)  # B.L. runs along -Z, inches
            pg.evaluate("window.__lab.setSection(true, 25)")
            c = pg.evaluate("window.__lab.cut()")
            assert c["planeConstant"] == pytest.approx(-25, abs=0.01) and c["bl"] == 25
            assert c["keepsOutboard"] and c["removesInboard"]
            assert "canard.shear_web.p3" in c["cappedNodes"]
            pg.evaluate("window.__lab.setSection(true, 35)")
            c = pg.evaluate("window.__lab.cut()")
            assert c["planeConstant"] == pytest.approx(-35, abs=0.01) and "canard.shear_web.p3" not in c["cappedNodes"]
            assert "canard.shear_web.p1" in c["cappedNodes"]  # bl_max 54
            pg.evaluate("window.__lab.select('r30.bottom-skin')")  # the jig pose is inverted: the plane turns with the canard
            pg.evaluate("window.__lab.advance(3)")
            assert pg.evaluate("window.__lab.pose()") == "inverted"
            c = pg.evaluate("window.__lab.cut()")
            assert c["keepsOutboard"] and c["removesInboard"] and c["planeConstant"] == pytest.approx(-35, abs=0.01)
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
            assert "canard.core" in c["cappedNodes"] and not [x for x in c["cappedNodes"] if x.startswith("canard.skin_")]  # skins are later ops: hidden
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert [x for x in pg.evaluate("window.__lab.cut().cappedNodes") if x.startswith("canard.skin_top")]
            pg.evaluate("window.__lab.select('r30.shear-web')")
            assert not [x for x in pg.evaluate("window.__lab.cut().cappedNodes") if x.startswith("canard.skin_")]
            pg.evaluate("window.__lab.setSection(false, 40)")
            off = pg.evaluate("window.__lab.cut()")
            assert not off["enabled"] and off["clipped"] == 0 and off["cappedNodes"] == [] and off["capsVisible"] == 0
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
            assert pg.evaluate("window.__lab.cutGlow()") == pytest.approx(1)  # frozen: wall-clock time does not settle it
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
            assert _want_layers(g, 20, alive) in txt and _lab_of(g, "canard.core") in txt, (txt, _want_layers(g, 20, alive))
            cnt = {}
            for n in g["layup"]["nodes"]:
                if n in alive:
                    cl = g["layup"]["nodes"][n]["cloth"]
                    cnt[cl] = cnt.get(cl, 0) + 1
            assert pg.inner_text("#ro-cloth") == " · ".join(f"{k} {cnt[k]}" for k in ("UND", "BID") if k in cnt)
            assert pg.inner_text("#ro-mass") == "not yet computed"  # the ledger does not source it yet: no invented number
            pg.evaluate("window.__lab.select('r30.lift-tabs')")  # an op without plies: no plies tile
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
            assert set(labs) == {"canard.core", "canard.shear_web", "canard.spar_cap_top", "canard.spar_cap_bottom", "canard.skin_top", "canard.skin_bottom"}  # lift tabs have no geometry
            assert all(labs[k]["text"] == _lab_of(g, k) for k in labs)
            assert labs["canard.skin_top"]["opacity"] > 0.9  # built and facing the camera
            assert labs["canard.skin_bottom"]["opacity"] < 0.05  # built, but its surface faces away from the top-skin shot
            pg.evaluate("window.__lab.select('r30.templates-cores')")
            pg.evaluate("window.__lab.advance(3)")
            labs = {x["id"]: x for x in pg.evaluate("window.__lab.labels()")}
            assert all(labs[k]["opacity"] < 0.05 for k in labs if k != "canard.core"), labs  # nothing else is built yet
            pg.evaluate("window.__lab.select('r30.top-skin')")
            pg.evaluate("window.__lab.advance(3)")
            assert pg.is_checked("#labels-on")
            _display(pg)
            pg.click("#labels-on")
            pg.evaluate("window.__lab.advance(3)")
            assert all(x["opacity"] < 0.05 for x in pg.evaluate("window.__lab.labels()"))
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


def test_load_paths_follow_the_build_and_the_toggle_is_remembered_even_without_storage(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.shear-web")
            assert [x["id"] for x in pg.evaluate("window.__lab.paths()")] == ["lift-into-caps", "cap-bending", "web-shear"]
            assert _drawn(pg) == ["web-shear"]
            for op, want in [("r30.bottom-spar-cap", ["web-shear"]),  # only the bottom cap exists: neither cap path has both caps
                             ("r30.top-spar-cap", ["cap-bending", "web-shear"]),  # both caps, no skins yet: no lift
                             ("r30.bottom-skin", ["web-shear"]),  # the jig pose is inverted; the bottom skin alone is not enough
                             ("r30.templates-cores", [])]:
                pg.evaluate(f"window.__lab.select('{op}')")
                assert _drawn(pg) == want, op
            pg.evaluate("window.__lab.select('r30.top-skin')")
            pg.evaluate("window.__lab.setLay(0)")
            assert _drawn(pg) == ["cap-bending", "web-shear"]  # skins exist once the first ply of the top skin is laid
            pg.evaluate("window.__lab.setLay(1)")
            assert _drawn(pg) == ["cap-bending", "lift-into-caps", "web-shear"]
            pg.evaluate("window.__lab.select('r30.shear-web')")  # stepping back hides what no longer exists
            assert _drawn(pg) == ["web-shear"]
            # the toggle: off draws nothing but the build state is unchanged; remembered across a reload, and on again
            pg.evaluate("window.__lab.select('r30.top-skin')")
            assert pg.is_checked("#paths-on") and len(_drawn(pg)) == 3
            _display(pg)
            pg.uncheck("#paths-on")
            assert _drawn(pg) == [] and _seen(pg) == ["cap-bending", "lift-into-caps", "web-shear"]
            pg.evaluate("window.__lab.select('r30.shear-web')"); pg.evaluate("window.__lab.select('r30.top-skin')")
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
            ctx.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
            pg2 = ctx.new_page()
            errs2 = []
            pg2.on("pageerror", lambda e: errs2.append(str(e)))
            pg2.goto(url + "lab/?test=1&q=low&op=r30.top-skin")
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
            for op, pose in (("r30.top-skin", "upright"), ("r30.bottom-skin", "inverted")):
                b, pg, errors = _lab_at(p, url, op)
                pg.evaluate("window.__lab.advance(3)")
                assert pg.evaluate("window.__lab.pose()") == pose
                paths = pg.evaluate("window.__lab.paths()")
                checked = 0
                for lp in g["loadpaths"]:
                    boxes = [pg.evaluate(corners, c) for c in lp["parts"] if pg.evaluate("(c) => !!window.__lab.plyBox(c)", c)]
                    pts = next(x for x in paths if x["id"] == lp["id"])["worldPoints"]
                    assert len(pts) == sum(len(sg) for sg in lp["segments"])
                    for pt in pts:  # within 0.5 in (0.0127 m) of one of its parts' boxes
                        assert any(all(bx[i][0] - 0.0127 <= pt[i] <= bx[i][1] + 0.0127 for i in range(3)) for bx in boxes), (op, lp["id"], pt, boxes)
                        checked += 1
                assert checked >= 40
                web = next(x for x in paths if x["id"] == "web-shear")["worldPoints"]
                assert abs(web[0][2] - web[-1][2]) == pytest.approx(54 * 0.0254, abs=1e-3)  # spans the 54 in of B.L., along Z
                assert not errors, errors
                b.close()
    finally:
        s.shutdown()


def _hue(rgb):
    import colorsys
    return colorsys.rgb_to_hsv(*[c / 255 for c in rgb])[0] * 360


def _strongest(im, xy, r=7):
    """The most saturated pixel (HSV) within r px of xy, as (saturation, rgb). """
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


def test_the_section_cut_clips_load_paths_and_the_flows_are_drawn_in_their_own_colours(rsite):
    from PIL import Image
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _lab_at(p, url, "r30.top-skin")
            pg.add_style_tag(content="#controls,#dock,#labels,#opbar{visibility:hidden}")
            pg.evaluate("window.__lab.advance(3)")
            paths = {x["id"]: x for x in pg.evaluate("window.__lab.paths()")}
            assert not any(x["clipped"] for x in paths.values())  # section off: unclipped
            kinds = {x["kind"]: x["color"] for x in paths.values()}
            assert len(kinds) == 3 and len({tuple(c) for c in kinds.values()}) == 3

            def snap():
                pg.evaluate("window.__lab.advance(0)")
                return Image.open(io.BytesIO(pg.screenshot())).convert("RGB")

            def mid(x, i=None):  # the middle of a polyline's first segment (points are in order, two segments' worth for bending)
                pts = x["worldPoints"]
                n = len(pts) if i is None else i
                return [(pts[n // 2 - 1][k] + pts[n // 2][k]) / 2 for k in range(3)]

            web, cap, lift = paths["web-shear"], paths["cap-bending"], paths["lift-into-caps"]
            pg.evaluate("document.getElementById('paths-on').click()")
            bare = snap()  # the same frame without the flows: the laminate is cream
            pg.evaluate("document.getElementById('paths-on').click()")
            im = snap()
            for x in (web, cap, lift):
                xy = pg.evaluate("(p) => window.__lab.project(p)", mid(x, 6 if x is lift else 9 if x is cap else None))
                sat, rgb = _strongest(im, xy)
                if x["kind"] == "bending":  # amber is close to the cream laminate's hue: it must also be clearly more saturated than the bare frame
                    assert sat > _strongest(bare, xy)[0] + 0.15, (x["id"], sat, rgb)
                assert _own_kind(kinds, rgb) == x["kind"], (x["id"], rgb)
            # the plane is the structure's: at B.L. 30 the web at B.L. 22 is clipped away, at B.L. 45 it is not
            pg.evaluate("window.__lab.setSection(true, 30)")
            paths = {x["id"]: x for x in pg.evaluate("window.__lab.paths()")}
            assert all(x["clipped"] for x in paths.values())  # every path reaches inboard of B.L. 30 (lift starts at 6.75)
            im = snap()
            wp = paths["web-shear"]["worldPoints"]
            at = lambda bl: [wp[0][0], wp[0][1], wp[0][2] + (wp[-1][2] - wp[0][2]) * bl / 54]  # noqa: E731
            xk, xg = (pg.evaluate("(p) => window.__lab.project(p)", at(bl)) for bl in (45, 22))
            assert all(0 <= q[0] < 960 and 0 <= q[1] < 600 for q in (xk, xg)), (xk, xg)  # both stations are on screen at this shot
            sk, kept = _strongest(im, xk)
            sg, gone = _strongest(im, xg)
            assert _own_kind(kinds, kept) == "shear" and sk > 0.4, (kept, sk)
            assert _own_kind(kinds, gone) != "shear" or sg < 0.4, (gone, sg)  # clipped with the structure
            pg.evaluate("window.__lab.setSection(true, 5)")  # the lift paths lie outboard of B.L. 5; the spar caps and the web reach the root
            clipped = {x["id"]: x["clipped"] for x in pg.evaluate("window.__lab.paths()")}
            assert clipped == {"lift-into-caps": False, "cap-bending": True, "web-shear": True}
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
    return [i for i in g["order"] if variant in byid[i]["variants"] + (["roncz", "gu"] if "both" in byid[i]["variants"] else [])
            and byid[i]["chapter"] == 30 and not byid[i]["stub"]]


def _open_rec(p, url, w=960, h=600, query=""):
    b = p.chromium.launch(args=GL)
    pg = b.new_page(viewport={"width": w, "height": h})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url + "lab/?rec=1&q=low&test=1" + query)
    pg.wait_for_function("window.__rec && window.__lab && window.__lab.ready", timeout=90000)
    return b, pg, errors


def test_rec_film_visits_every_op_in_order_and_ends(rsite):
    g = _graph(rsite)
    want = _tour_ops(g)
    layup = g["layup"]["nodes"]
    span = {}
    for n in layup.values():
        span[n["op"]] = max(span.get(n["op"], 0), n["bl_max"] if n["bl_max"] is not None else g["layup"]["semi_span"])
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url, query="&clean=1")
            assert pg.evaluate("document.body.classList.contains('rec')") and pg.evaluate("document.body.classList.contains('clean')")
            assert not pg.is_visible("#controls") and not pg.is_visible("#opbar")  # ?clean=1: the canvas and the cards only
            dur = pg.evaluate("window.__rec.start('canard')")
            assert 55 <= dur <= 95, dur  # the film is about a minute and a half
            assert pg.evaluate("__lab.touring()") is True
            seen, idx, plays, cuts, active, frames = [], [], set(), [], True, 0
            while active and frames < 60 * 100 * 2:
                r = pg.evaluate("window.__rec.frame(1 / 60, false)")
                active = r["active"]
                frames += 1
                sel, i = pg.evaluate("[__lab.selected(), __lab.tourIndex()]")
                if sel and (not seen or seen[-1] != sel):
                    seen.append(sel)
                if not idx or idx[-1] != i:
                    idx.append(i)
                if pg.evaluate("__lab.playing()"):
                    plays.add(sel)
                c = pg.evaluate("__lab.cut()")
                if c["enabled"] and sel in span and (not cuts or cuts[-1][:2] != [sel, c["bl"]]):
                    cuts.append([sel, c["bl"]])
            assert not active and pg.evaluate("__lab.touring()") is False
            assert abs(frames / 60 - dur) < 1.0, (frames, dur)
            assert seen == want, seen
            assert idx == list(range(len(want))), idx  # the segment index only moves forward, one op at a time
            with_plies = {o for o in want if o in span}
            assert plays == with_plies, plays  # Play is pressed for exactly the ops that have plies
            assert {c[0] for c in cuts} == with_plies  # ... and each of them is cut open once, inside its own layup
            assert all(0 <= bl <= span[op] for op, bl in cuts), cuts
            assert pg.evaluate("__lab.selected()") is None  # the film ends on the finished canard
            assert pg.evaluate("__lab.cut().enabled") is False  # ... and the person's own section setting is back
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
        if pg.evaluate("__lab.selected()") == "r30.shear-web" and pg.evaluate("__lab.playing()"):
            return
    raise AssertionError("the tour never pressed Play on the shear web")


def test_tour_button_runs_the_tour_and_every_user_action_stops_it(rsite):
    g = _graph(rsite)
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open_rec(p, url)
            assert pg.get_attribute("#tour", "aria-pressed") == "false" and pg.text_content("#tour") == "Tour"
            _tour_to_first_ply_op(pg, g)
            assert pg.get_attribute("#tour", "aria-pressed") == "true" and pg.text_content("#tour") == "Stop tour"
            assert pg.evaluate("__lab.tourIndex()") == _tour_ops(g).index("r30.shear-web")  # the segment follows the op it is showing
            assert pg.evaluate("__lab.lay()") >= 1

            def stops(label, act, keeps_op=True):
                _tour_to_first_ply_op(pg, g) if not pg.evaluate("__lab.touring()") else None
                sel, lay, ci = pg.evaluate("[__lab.selected(), __lab.lay(), __lab.tourIndex()]")
                act()
                assert pg.evaluate("__lab.touring()") is False, label
                assert pg.get_attribute("#tour", "aria-pressed") == "false" and pg.text_content("#tour") == "Tour", label
                _adv(pg, 0.3)
                if keeps_op:
                    assert pg.evaluate("__lab.selected()") == sel, label  # it stays where it was
                return sel

            stops("escape", lambda: pg.keyboard.press("Escape"))
            stops("second press", lambda: pg.click("#tour"))
            other = "r30.top-skin"
            stops("op chip", lambda: pg.click(f'#chips button[data-op="{other}"]'), keeps_op=False)
            assert pg.evaluate("__lab.selected()") == other  # the click still did its job
            stops("variant", lambda: pg.click('#variant button[data-variant="gu"]'), keeps_op=False)
            pg.click('#variant button[data-variant="roncz"]')
            stops("scrubber", lambda: pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = '1'; s.dispatchEvent(new Event('input', { bubbles: true })) })()"), keeps_op=False)
            assert pg.evaluate("__lab.lay()") == 1
            stops("play", lambda: pg.click("#play"), keeps_op=False)
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
                assert pg.evaluate("__lab.cut().enabled") is True  # the tour opened the section
                pg.click("#tour")  # stop with the cut open: the state stays where it was
                assert pg.evaluate("__lab.touring()") is False and pg.evaluate("__lab.cut().enabled") is False  # the cut goes back to what the person had
                assert pg.evaluate("document.getElementById('cursor').style.opacity") == "0"
                pg.click("#section-on")  # the person's own control still works after the tour
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
            pg.goto(url)  # same origin: seed the person's stored settings, then count every setItem from the lab's first line
            pg.evaluate("() => { localStorage.setItem('longez.paths', '0'); localStorage.setItem('longez.labels', '0') }")
            pg.add_init_script("window.__setItems = 0; const o = Storage.prototype.setItem; Storage.prototype.setItem = function () { window.__setItems++; return o.apply(this, arguments) }")
            pg.goto(url + "lab/?rec=1&q=low&test=1")
            pg.wait_for_function("window.__rec && window.__lab && window.__lab.ready", timeout=90000)
            assert not pg.is_checked("#paths-on") and not pg.is_checked("#labels-on")
            pg.click("#tour")
            shown = False
            for _ in range(400):
                _adv(pg, 0.25)
                if pg.evaluate("__lab.paths().some(p => p.drawn)") and pg.evaluate("__lab.labels().some(l => l.opacity > 0)"):
                    shown = True
                    break
            assert shown, "the tour should show paths and part names while it runs"
            pg.keyboard.press("Escape")
            _adv(pg, 2.0)  # the part names fade out in sim time
            assert pg.evaluate("__lab.touring()") is False
            assert not pg.is_checked("#paths-on") and not pg.is_checked("#labels-on")
            assert pg.evaluate("[localStorage.getItem('longez.paths'), localStorage.getItem('longez.labels')]") == ["0", "0"]
            assert pg.evaluate("__lab.paths().every(p => !p.drawn)") and pg.evaluate("__lab.labels().every(l => l.opacity === 0)")
            assert pg.evaluate("window.__setItems") == 0  # the tour never wrote storage
            assert pg.evaluate("__lab.cut().enabled") is False
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


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
        ia, ic = Image.open(io.BytesIO(a)).convert("RGB"), Image.open(io.BytesIO(c)).convert("RGB")
        diff = ImageChops.difference(ia, ic).convert("L").point(lambda v: 255 if v > 0 else 0)
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


def test_frame_time_median_while_dragging_the_section_on_the_low_tier(rsite):
    # Ported from the 2.1 viewer's budget test. Headless swiftshader (software GL) is a PROXY for the iPad, not a measurement of it:
    # the iPad judgement is the owner's walk-through. The budget is a median rAF delta <= 33 ms over a continuous 2 s drag of the
    # section slider from B.L. 0 to max, top-skin op, all plies, load paths on, section on, at 1180x820, on ?q=low. It is never raised.
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            # real frames: not frozen, and ?realframes=1 lets the low tier's adaptive resolution see them (tests otherwise feed their own)
            b, pg, errors = _open(p, url, 1180, 820, init=FRAMES_JS, q="low", query="&realframes=1")
            assert pg.evaluate("window.__lab.tier()") == "low" and pg.evaluate("window.__lab.auto()") is False
            pg.evaluate("window.__lab.select('r30.top-skin')")  # a step opens fully built: all its plies
            assert pg.is_checked("#paths-on") and len([x for x in pg.evaluate("window.__lab.paths()") if x["visible"]]) == 3
            pg.click("#section-on")
            pg.eval_on_selector("#section-bl", "(e) => { e.value = 0; e.dispatchEvent(new Event('input', {bubbles: true})); }")
            pg.wait_for_timeout(500)
            max_bl = pg.evaluate(EFFECTIVE_MAX_JS)
            # The low tier trims its resolution while frames run long (quality.ts). Give it a warm-up drag of the same cut, then wait for the
            # resolution to stop moving, so the measured drag runs at the resolution the tier settled on (printed below).
            pg.evaluate(DRAG_JS, 2000)
            pg.eval_on_selector("#section-bl", "(e) => { e.value = 0; e.dispatchEvent(new Event('input', {bubbles: true})); }")
            still, last = 0, None
            for _ in range(60):
                pg.wait_for_timeout(1000)
                cur = pg.evaluate("window.__lab.resScale()")
                still = still + 1 if cur == last else 0
                last = cur
                if still >= 3:
                    break
            assert still >= 3, f"resolution never settled (scale {last})"
            print("settled resolution scale", last, "pixels", pg.evaluate("window.__lab.stats()")["pixels"])
            before = pg.evaluate("window.__lab.cut()")
            assert before["enabled"] and before["bl"] == pytest.approx(0, abs=1e-6), before
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
            assert after["enabled"] and after["bl"] == pytest.approx(max_bl), (before["bl"], after["bl"], max_bl)
            assert seen[0] <= max_bl * 0.05 and seen[-1] == max_bl, (seen[:3], seen[-3:], max_bl)
            assert all(a <= c for a, c in zip(seen, seen[1:])), "slider values must be monotonic non-decreasing"
            assert len(set(seen)) >= 100, len(set(seen))
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
            pg.goto(url + "lab/?rec=1&test=1")
            pg.wait_for_function("window.__rec && window.__lab && window.__lab.ready", timeout=90000)
            assert pg.evaluate("window.__lab.tier()") == "high" and pg.evaluate("window.__lab.auto()") is False
            b.close()
    finally:
        s.shutdown()


def test_auto_step_down_drops_high_to_mid_to_low_and_the_scene_keeps_its_state(rsite):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b, pg, errors = _open(p, url, 500, 360, q=None, query="&op=r30.top-skin")  # no ?q=: auto is on, and a desktop starts on high
            assert pg.evaluate("window.__lab.auto()") is True and pg.evaluate("window.__lab.tier()") == "high"
            pg.evaluate("window.__lab.setLay(3)")
            names = pg.evaluate("window.__lab.meshNames()")
            sel, lay = pg.evaluate("window.__lab.selected()"), pg.evaluate("window.__lab.lay()")
            assert sel == "r30.top-skin" and lay == 3 and pg.inner_text("#quality-label") == "Quality: High (auto)"
            # fast frames change nothing
            assert pg.evaluate(FEED_JS, [16.7, 200]) == "high"
            seen = ["high"]
            for _ in range(2):  # slow frames until the tier drops (the frames right after a drop are ignored while it settles)
                seen.append(pg.evaluate(FEED_JS, [60, 60]))
            assert seen == ["high", "mid", "low"], seen
            assert pg.evaluate(FEED_JS, [400, 200]) == "low"  # never below low
            assert pg.evaluate(FEED_JS, [5, 200]) == "low"  # and no step back up
            # nothing about the build was lost, and it still draws
            assert pg.evaluate("window.__lab.meshNames()") == names
            assert pg.evaluate("window.__lab.selected()") == sel and pg.evaluate("window.__lab.lay()") == lay
            # It still draws. One full-file run read 0 draw calls here: three.js skips a frame while the GL context is lost, and swiftshader
            # seems to drop it when the tier and the resolution are rebuilt back to back (not confirmed). So redraw until a frame lands.
            pg.wait_for_function("(window.__lab.advance(0.05), window.__lab.stats().calls > 20)", timeout=10000, polling=200)
            assert pg.inner_text("#quality-label") == "Quality: Low (auto)"
            assert pg.get_attribute('#quality-seg button[data-q="auto"]', "aria-pressed") == "true"
            # the segmented control overrides: a tier turns auto off, Auto turns it back on
            _display(pg)
            pg.click('#quality-seg button[data-q="high"]')
            assert pg.evaluate("window.__lab.tier()") == "high" and pg.evaluate("window.__lab.auto()") is False
            assert pg.inner_text("#quality-label") == "Quality: High"
            assert pg.get_attribute('#quality-seg button[data-q="high"]', "aria-pressed") == "true"
            pg.evaluate("window.__lab.advance(0.05)")
            assert pg.evaluate("window.__lab.meshNames()") == names and pg.evaluate("window.__lab.lay()") == lay
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
    return pg.evaluate(f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom] }})()")


@pytest.mark.parametrize("w,h", [(1400, 860), (1180, 820), (390, 844)])
def test_the_cards_leave_the_canard_clear_and_touch_targets_are_40px(rsite, w, h):
    s, url = serve(rsite)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=GL)
            ctx = b.new_context(viewport={"width": w, "height": h}, has_touch=w < 1400)  # the iPad and the phone have coarse pointers
            pg = ctx.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            for op in (None, "r30.top-skin"):
                pg.goto(url + "lab/?test=1&q=low" + (f"&op={op}" if op else ""))
                pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
                if op:
                    pg.evaluate("window.__lab.setLay(Number(document.getElementById('scrub').max))")
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
                assert area > 0.05 * w * h, (op, box)  # the canard is on screen, not a speck
                for sel in _CARDS:
                    c = _rect(pg, sel)
                    ov = max(0, min(box[2], c[2]) - max(box[0], c[0])) * max(0, min(box[3], c[3]) - max(box[1], c[1]))
                    assert ov < 0.10 * area, (w, op, sel, round(ov / area, 3), box, c)
            if w < 1400:
                # every control in the cards is a 40 px target on a touch screen, the popover's too
                pg.click("#more")
                small = pg.evaluate("""() => [...document.querySelectorAll(['#controls button', '#controls input[type=range]', '#controls label.check',
                    '#viewpop button', '#viewpop label.check', '#opbar button', '#step-head'].join(','))].filter((e) => e.offsetParent)
                    .map((e) => [e.id || e.textContent.trim().slice(0, 24), e.getBoundingClientRect().height]).filter((x) => x[1] < 39.5)""")
                assert small == [], small
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
