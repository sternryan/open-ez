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
    b, pg, errors = _open(p, url, w, h)
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
