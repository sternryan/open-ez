import functools, http.server, json, shutil, threading
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from guide.build_site import build
from tests.guide.test_schema import gdir  # noqa: F401

@pytest.fixture
def site(tmp_path, gdir):
    import cadquery as cq
    from guide.export_glb import export_components
    glb = export_components({"canard.core": cq.Workplane().box(10, 2, 1)}, tmp_path / "m.glb")
    out = tmp_path / "site"
    build(gdir, out, models=glb, scan_base=None, docs=None)
    return out

def serve(root: Path):
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"

def open_page(p, url, width=1280, init=None):
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": width, "height": 900})
    if init:
        pg.add_init_script(init)
    pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
    return b, pg

def test_variant_and_bidirectional_selection(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "gu")
        ids = pg.eval_on_selector_all("#ops li[data-op]", "els => els.map(e => e.dataset.op)")
        assert "c10.cores" in ids
        pg.click('#ops li[data-op="c10.cores"]')
        assert pg.get_attribute('#parts .chip[data-cid="canard.core"]', "data-badge") == "unvalidated"
        pg.evaluate("window.__guide.selectComponent('canard.core')")
        assert pg.eval_on_selector_all("#ops li.selected", "els => els.map(e => e.dataset.op)") == ["c10.cores"]
        b.close()
    s.shutdown()

def test_no_private_assets_shows_none_not_broken(site):  # Review Focus 1
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.cores"]')
        assert pg.locator("#source .none").count() == 1 and pg.locator("#source img").count() == 0
        b.close()
    s.shutdown()

def test_localstorage_throwing_checklist_still_works(site):  # Review Focus 2
    s, url = serve(site)
    init = "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})"
    with sync_playwright() as p:
        b, pg = open_page(p, url, init=init)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.cores"]')
        pg.check("#checklist input[type=checkbox] >> nth=0")
        assert pg.is_checked("#checklist input[type=checkbox] >> nth=0")
        b.close()
    s.shutdown()

def test_missing_model_degrades(site):  # Review Focus 3
    (site / "models" / "longez.glb").unlink()
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.wait_for_function("document.querySelector('#model-status').textContent.includes('3D unavailable')")
        pg.select_option("#variant", "gu")
        assert pg.locator("#ops li[data-op]").count() >= 2
        b.close()
    s.shutdown()

def test_phone_width_no_horizontal_scroll(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=390)
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390
        b.close()
    s.shutdown()

def test_glb_loads_and_maps_dotted_component_and_canvas_click_selects(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
        pg.wait_for_function("window.__guide.meshComponents().includes('canard.core')", timeout=10000)
        pg.select_option("#variant", "gu")
        pg.wait_for_timeout(500)  # let a frame render
        box = pg.locator("#c").bounding_box()
        pg.click("#c", position={"x": box["width"] / 2, "y": box["height"] / 2})
        assert "c10.cores" in pg.eval_on_selector_all("#ops li.selected", "els => els.map(e => e.dataset.op)")
        b.close()
    s.shutdown()

def test_variant_change_clears_detail_of_invisible_op(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.cores"]')
        assert pg.inner_text("#op-title")
        pg.select_option("#variant", "roncz")
        assert pg.inner_text("#op-title") == "" and pg.locator("#parts .chip").count() == 0
        b.close()
    s.shutdown()

def test_gu_lists_no_geometry_chip_and_hides_unused_meshes(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
        pg.wait_for_function("window.__guide.meshComponents().includes('canard.core')", timeout=10000)
        # default variant roncz: no visible op uses canard.core
        assert "canard.core" in pg.evaluate("window.__guide.meshComponents()")
        assert "canard.core" not in pg.evaluate("window.__guide.visibleMeshComponents()")
        pg.select_option("#variant", "gu")
        assert "canard.core" in pg.evaluate("window.__guide.visibleMeshComponents()")
        pg.click('#ops li[data-op="c10.twist-check"]')
        assert pg.get_attribute('#parts .chip[data-badge="no-geometry"]', "data-cid") == "canard.spar_cap_bottom"
        pg.select_option("#variant", "roncz")
        assert "canard.core" not in pg.evaluate("window.__guide.visibleMeshComponents()")
        b.close()
    s.shutdown()


# ---- M2 Task 9: cutaway toggle, glance view, states
from tests.guide.render_fixture import ROOT, make_export, make_renders  # noqa: E402


@pytest.fixture
def csite(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    out = tmp_path / "site"
    build(ROOT / "guide" / "graph", out, models=e / "longez.glb", scan_base=None, docs=None, renders=r)
    return out


def test_cutaway_toggle_memory_and_hidden_on_non_layup(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=1180)
        pg.select_option("#variant", "roncz")
        pg.click('#ops li[data-op="r30.bottom-skin"]')
        assert pg.is_visible("#viewtoggle")
        pg.click('#viewtoggle [data-view="cutaway"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        assert pg.get_attribute("#cutimg", "src") == "renders/op-r30-bottom-skin.png"
        assert pg.get_attribute("#cutimg", "alt").startswith("After ")
        assert not pg.is_visible("#c") and not pg.is_visible("#parts") and pg.is_visible("#cutpane")
        assert pg.get_attribute('#viewtoggle [data-view="cutaway"]', "aria-checked") == "true"
        assert pg.get_attribute('#viewtoggle [data-view="3d"]', "aria-checked") == "false"
        assert "not to scale" in pg.text_content("#cutcap").lower()
        pg.click('#viewtoggle [data-view="3d"]')
        assert pg.is_visible("#c") and not pg.is_visible("#cutpane")
        assert pg.get_attribute('#viewtoggle [data-view="3d"]', "aria-checked") == "true"
        pg.click('#viewtoggle [data-view="cutaway"]')
        pg.click('#ops li[data-op="r30.jig-assemble"]')
        assert pg.is_visible("#c") and not pg.is_visible("#cutpane")
        assert not pg.is_visible("#viewtoggle") and pg.evaluate("window.__guide.paneMode()") == "3d"
        pg.click('#ops li[data-op="r30.top-skin"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"  # remembered
        b.close()
    s.shutdown()


def test_glance_view(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        for width in (1180, 820):
            b, pg = open_page(p, url, width=width)
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.click('#ops li[data-op="__glance"]')
            assert pg.locator("#glance img").count() == 2 and pg.is_visible("#legend")
            assert "shear web 6 at BL 5" in pg.text_content("#op-summary")
            assert pg.evaluate("window.__guide.paneMode()") == "glance"
            assert not pg.is_visible("#c") and not pg.is_visible("#parts")
            assert "not to scale" in pg.text_content("#legend").lower()
            # heroes are wide frames: nothing wider than its container, viewport contains the stack
            assert pg.evaluate("""() => [...document.querySelectorAll('#glance img')].every(i => {
                const f = i.closest('figure').getBoundingClientRect();
                return i.getBoundingClientRect().width <= f.width + 1; })""")
            for w in (820, 390):
                pg.set_viewport_size({"width": w, "height": 900}); pg.wait_for_timeout(100)
                assert pg.evaluate("""() => { const v = document.querySelector('#viewport').getBoundingClientRect(),
                    g = document.querySelector('#glance').getBoundingClientRect();
                    return v.bottom >= g.bottom - 1 && v.top <= g.top + 1; }""")
                assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            pg.set_viewport_size({"width": width, "height": 900})
            # glance is not an op: variant change, resize, canvas click, then a real op must not throw
            pg.select_option("#variant", "gu")
            assert pg.evaluate("window.__guide.paneMode()") == "glance"
            pg.set_viewport_size({"width": width, "height": 700})
            pg.select_option("#variant", "roncz")
            pg.click('#ops li[data-op="__glance"]')
            pg.click('#ops li[data-op="r30.bottom-skin"]')
            assert pg.evaluate("window.__guide.paneMode()") == "3d"
            pg.click("#c", position={"x": 20, "y": 20}, force=True)
            pg.click('#ops li[data-op="__glance"]')
            pg.click('#ops li[data-op="r30.jig-assemble"]')
            assert errors == []
            b.close()
    s.shutdown()


def test_missing_cutaway_png_shows_retry(csite):  # Review Focus 4
    png = csite / "renders" / "op-r30-bottom-skin.png"
    png_bak = csite / "bak.png"; shutil.copy(png, png_bak); png.unlink()
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
        pg.click('#viewtoggle [data-view="cutaway"]')
        pg.wait_for_selector("#cuterr:not([hidden])")
        assert pg.is_visible("text=Cutaway picture didn't load")
        assert not pg.is_visible("#cutzoom") and not pg.is_visible("#cutimg")
        assert pg.get_attribute("#cutzoom", "hidden") is not None
        shutil.copy(png_bak, png)
        pg.click("#cutretry")
        pg.wait_for_selector("#cutimg", state="visible")
        assert "?r=" in pg.get_attribute("#cutimg", "src") and pg.is_visible("#cutzoom")
        assert not pg.is_visible("#cuterr")
        pg.click('#viewtoggle [data-view="3d"]')
        assert pg.evaluate("window.__guide.paneMode()") == "3d"
        assert pg.is_visible("#c")
        b.close()
    s.shutdown()


def test_toggle_works_when_localstorage_throws(csite):
    s, url = serve(csite)
    init = "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})"
    with sync_playwright() as p:
        b, pg = open_page(p, url, init=init)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
        pg.click('#viewtoggle [data-view="cutaway"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        b.close()
    s.shutdown()


def test_site_without_renders_has_no_toggle_or_glance(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        assert pg.locator('#ops li[data-op="__glance"]').count() == 0
        assert not pg.is_visible("#viewtoggle")
        b.close()
    s.shutdown()


def test_toggle_keyboard_and_zoom_escape(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
        pg.focus('#viewtoggle [data-view="3d"]')
        assert pg.get_attribute('#viewtoggle [data-view="3d"]', "tabindex") == "0"
        assert pg.get_attribute('#viewtoggle [data-view="cutaway"]', "tabindex") == "-1"
        pg.keyboard.press("ArrowRight")
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        assert pg.get_attribute('#viewtoggle [data-view="cutaway"]', "aria-checked") == "true"
        assert pg.get_attribute('#viewtoggle [data-view="cutaway"]', "tabindex") == "0"
        pg.keyboard.press("ArrowDown")
        assert pg.evaluate("window.__guide.paneMode()") == "3d"
        pg.keyboard.press("ArrowUp")
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        pg.click("#cutzoom")
        assert pg.evaluate("document.querySelector('#zoom').open")
        pg.keyboard.press("Escape")
        assert not pg.evaluate("document.querySelector('#zoom').open")
        b.close()
    s.shutdown()


def test_phone_cutaway_pane_inside_viewport_and_clear_of_toggle(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        for w in (820, 390):
            b, pg = open_page(p, url, width=w)
            pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
            pg.click('#viewtoggle [data-view="cutaway"]')
            pg.wait_for_timeout(200)
            r = pg.evaluate("""() => { const q = s => document.querySelector(s).getBoundingClientRect();
                return {v: q('#viewport'), p: q('#cutpane'), t: q('#viewtoggle'), i: q('#cutimg'), a: q('aside')}; }""")
            assert r["v"]["bottom"] >= r["p"]["bottom"] - 1
            assert r["i"]["top"] >= r["t"]["bottom"] - 1
            assert r["a"]["top"] >= r["v"]["bottom"] - 1
            assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            b.close()
    s.shutdown()


# ---- M2 Task 11: ply list with isolate + empty Checklist heading
GL = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"]
P3 = "canard.shear_web.p3"


def _open_gl(p, url, width):
    b = p.chromium.launch(args=GL)
    pg = b.new_page(viewport={"width": width, "height": 900})
    pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
    pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.shear-web"]')
    pg.wait_for_function("window.__guide.meshPlies().length > 0", timeout=10000)
    return b, pg


def _inside(pg, sel):
    return pg.evaluate("""(s) => { const v = document.querySelector('#viewport').getBoundingClientRect(),
        r = document.querySelector(s).getBoundingClientRect();
        return r.width > 0 && r.height > 0 && r.left >= v.left - 1 && r.right <= v.right + 1 && r.top >= v.top - 1 && r.bottom <= v.bottom + 1; }""", sel)


def _all_opaque(pg):
    return all(m["opacity"] == 1 for m in pg.evaluate("window.__guide.meshOpacities()"))


@pytest.mark.parametrize("width", [1180, 820])
def test_ply_list_isolates_inner_web_ply(csite, width):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, width)
        assert not pg.is_visible("#plydock")
        # chip without plies must not open the dock (spec 6.2 empty state)
        pg.click('#parts .chip[data-cid="canard.core"]')
        assert not pg.is_visible("#plydock")
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        assert pg.is_visible("#plydock") and pg.locator("#plydock button").count() == 6
        assert _inside(pg, "#plydock")
        for sel in ('#parts .chip', '#plydock button'):
            for h in pg.eval_on_selector_all(sel, "els => els.map(e => e.getBoundingClientRect().height)"):
                assert h >= 44, (sel, h)
        pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.evaluate("window.__guide.isolated()") == P3
        ops = pg.evaluate("window.__guide.meshOpacities()")
        assert any(m["node"] == P3 and m["opacity"] == 1 for m in ops)
        assert all(m["opacity"] == 1 for m in ops if m["node"] == P3)
        assert all(m["opacity"] < 1 for m in ops if m["node"] != P3) and len(ops) > 1
        assert pg.is_visible("#isobar") and _inside(pg, "#isobar") and pg.is_visible("#plydock")
        assert pg.text_content("#isotext") == "Showing Shear web ply 3"
        assert pg.get_attribute(f'#plydock button[data-node="{P3}"]', "aria-pressed") == "true"
        assert pg.get_attribute("#plydock", "role") == "group" and "plies" in pg.get_attribute("#plydock", "aria-label")
        assert pg.get_attribute("#isotext", "aria-live") == "polite"
        chip = pg.locator('#parts .chip[data-cid="canard.shear_web"]')
        assert chip.get_attribute("aria-expanded") == "true" and chip.get_attribute("aria-controls") == "plydock"
        assert pg.eval_on_selector("#viewport", "e => e.classList.contains('isolating')")
        pg.keyboard.press("Escape")
        assert pg.evaluate("window.__guide.isolated()") is None and not pg.is_visible("#isobar")
        assert _all_opaque(pg) and not pg.eval_on_selector("#viewport", "e => e.classList.contains('isolating')")
        # same ply twice toggles back
        pg.click(f'#plydock button[data-node="{P3}"]'); assert pg.evaluate("window.__guide.isolated()") == P3
        pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.evaluate("window.__guide.isolated()") is None and _all_opaque(pg)
        # Show all button
        pg.click(f'#plydock button[data-node="{P3}"]'); pg.click("#showall")
        assert pg.evaluate("window.__guide.isolated()") is None and not pg.is_visible("#isobar") and _all_opaque(pg)
        # changing op resets and hides dock
        pg.click(f'#plydock button[data-node="{P3}"]')
        pg.click('#ops li[data-op="r30.bottom-skin"]')
        assert pg.evaluate("window.__guide.isolated()") is None and not pg.is_visible("#plydock")
        assert not pg.is_visible("#isobar") and _all_opaque(pg)
        b.close()
    s.shutdown()


def test_ply_list_keyboard(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, 1180)
        pg.focus('#parts .chip[data-cid="canard.shear_web"]')
        assert pg.evaluate("document.activeElement.tagName") == "BUTTON"
        pg.keyboard.press("Enter")
        assert pg.is_visible("#plydock")
        assert pg.evaluate("document.activeElement.closest('#plydock') !== null")  # focus lands on first row
        pg.keyboard.press("Tab")
        assert pg.evaluate("document.activeElement.closest('#plydock') !== null")
        node = pg.evaluate("document.activeElement.dataset.node")
        assert node.endswith(".p2")
        pg.keyboard.press("Enter")
        assert pg.evaluate("window.__guide.isolated()") == node
        pg.keyboard.press("Escape")
        assert pg.evaluate("window.__guide.isolated()") is None
        pg.keyboard.press("Tab"); pg.keyboard.press("Space")  # next row via Space
        assert pg.evaluate("window.__guide.isolated()") is not None
        pg.keyboard.press("Escape")
        assert pg.evaluate("window.__guide.isolated()") is None and _all_opaque(pg)
        b.close()
    s.shutdown()


def test_empty_checklist_heading_hidden(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=1180)
        pg.select_option("#variant", "roncz")
        pg.click('#ops li[data-op="__glance"]')
        assert not pg.is_visible("#checklist-h")
        pg.click('#ops li[data-op="r30.shear-web"]')
        assert pg.is_visible("#checklist-h") and pg.locator("#checklist li").count() > 0
        pg.click('#ops li[data-op="r30.elevators"]')
        assert pg.locator("#checklist li").count() == 0 and not pg.is_visible("#checklist-h")
        pg.click('#ops li[data-op="r30.shear-web"]')
        pg.select_option("#variant", "gu")  # r30 op no longer visible -> clearDetail
        assert not pg.is_visible("#checklist-h")
        b.close()
    s.shutdown()


def _rect(pg, sel):
    return pg.evaluate("s => { const r = document.querySelector(s).getBoundingClientRect(); return {l: r.left, r: r.right, t: r.top, b: r.bottom}; }", sel)


@pytest.mark.parametrize("width", [1180, 820])
def test_cutaway_toggle_clears_isolation_and_dock(csite, width):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, width)
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.evaluate("window.__guide.isolated()") == P3
        pg.click('#viewtoggle [data-view="cutaway"]')
        assert not pg.is_visible("#plydock") and not pg.is_visible("#isobar")
        assert pg.evaluate("window.__guide.isolated()") is None
        pg.click('#viewtoggle [data-view="3d"]')
        assert _all_opaque(pg) and not pg.is_visible("#plydock") and not pg.is_visible("#isobar")
        b.close()
    s.shutdown()


@pytest.mark.parametrize("width", [1180, 820])
def test_dock_never_covers_chips_and_chip_closes_it(csite, width):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, width)
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        assert pg.is_visible("#plydock")
        d = _rect(pg, "#plydock")
        for r in pg.eval_on_selector_all("#parts .chip", "els => els.map(e => { const r = e.getBoundingClientRect(); return {l: r.left, r: r.right, t: r.top, b: r.bottom}; })"):
            assert not (d["l"] < r["r"] and r["l"] < d["r"] and d["t"] < r["b"] and r["t"] < d["b"]), (d, r)
        assert _inside(pg, "#plydock")
        if width == 1180:  # guard: chips must really wrap, or the overlap check above is vacuous
            tops = pg.eval_on_selector_all("#parts .chip", "els => els.map(e => Math.round(e.getBoundingClientRect().top))")
            assert len(set(tops)) >= 2, tops
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        assert not pg.is_visible("#plydock")
        b.close()
    s.shutdown()


def test_phone_isobar_clear_of_toggle_and_toggle_clickable(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, 390)
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.evaluate("window.__guide.isolated()") == P3
        t, i = _rect(pg, "#viewtoggle"), _rect(pg, "#isobar")
        assert not (t["l"] < i["r"] and i["l"] < t["r"] and t["t"] < i["b"] and i["t"] < t["b"]), (t, i)
        assert pg.eval_on_selector("#showall", "e => e.getBoundingClientRect().height") >= 44
        d = _rect(pg, "#plydock")
        assert d["t"] >= i["b"] - 1, (d, i)
        assert pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        pg.click('#viewtoggle [data-view="cutaway"]', timeout=3000)
        assert pg.evaluate("window.__guide.isolated()") is None and not pg.is_visible("#isobar")
        b.close()
    s.shutdown()


def test_parts_empty_area_passes_clicks_to_canvas(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, 1180)
        pt = pg.evaluate("""() => { const pr = document.querySelector('#parts').getBoundingClientRect();
            const chips = [...document.querySelectorAll('#parts .chip')].map(c => c.getBoundingClientRect());
            for (let y = pr.top + 2; y < pr.bottom; y += 4) for (let x = pr.left + 2; x < pr.right; x += 4)
                if (!chips.some(r => x >= r.left - 1 && x <= r.right + 1 && y >= r.top - 1 && y <= r.bottom + 1)) return [x, y];
            return null; }""")
        assert pt, "no empty point inside #parts box"
        assert pg.evaluate("([x, y]) => document.elementFromPoint(x, y).id", pt) == "c"
        assert pg.evaluate("() => { const r = document.querySelector('#parts .chip').getBoundingClientRect(); return !!document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2).closest('.chip'); }")
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        assert pg.evaluate("() => { const r = document.querySelector('#plydock button').getBoundingClientRect(); return !!document.elementFromPoint(r.left + 5, r.top + 5).closest('#plydock'); }")
        b.close()
    s.shutdown()


def test_isolate_before_glb_loads_labels_and_ghosts_late_meshes(csite):
    held = []
    s, url = serve(csite)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GL)
        pg = b.new_page(viewport={"width": 1180, "height": 900})
        pg.route("**/models/longez.glb", lambda route: held.append(route))  # park the request
        pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.shear-web"]')
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.text_content("#isotext") == "Showing Shear web ply 3"
        assert held
        held[0].continue_()
        pg.wait_for_function("window.__guide.meshPlies().length > 0", timeout=10000)
        ops = pg.evaluate("window.__guide.meshOpacities()")
        assert any(m["node"] == P3 and m["opacity"] == 1 for m in ops)
        assert all(m["opacity"] < 1 for m in ops if m["node"] != P3)
        b.close()
    s.shutdown()


def test_showall_button_dark_mode_styled(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b = p.chromium.launch(args=GL)
        pg = b.new_page(viewport={"width": 1180, "height": 900}, color_scheme="dark")
        pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.shear-web"]')
        pg.wait_for_function("window.__guide.meshPlies().length > 0", timeout=10000)
        pg.click('#parts .chip[data-cid="canard.shear_web"]'); pg.click(f'#plydock button[data-node="{P3}"]')
        assert pg.eval_on_selector("#showall", "e => getComputedStyle(e).backgroundColor") == "rgba(0, 0, 0, 0)"
        assert pg.eval_on_selector("#showall", "e => e.getBoundingClientRect().height") >= 44
        b.close()
    s.shutdown()


def _dark_pixels(pg, clip):
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("L")
    return sum(1 for v in im.getdata() if v < 200)


@pytest.mark.parametrize("width", [1180])  # 820 measured 3907 -> 2538 (layout leaves too little model in the clip): not a stable >50% drop
def test_isolate_visibly_ghosts_other_plies_on_screen(csite, width):
    """Pixel-level: material.transparent flips need needsUpdate or nothing ghosts after the first frame."""
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, width)
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        pg.wait_for_timeout(500)
        c = pg.eval_on_selector("#c", "e => { const r = e.getBoundingClientRect(); return {x: r.left, y: r.top, w: r.width, h: r.height}; }")
        c0 = c["y"]
        # isolate first so the isobar is laid out, then use the region below it, right half of the canvas
        pg.click(f'#plydock button[data-node="{P3}"]'); pg.wait_for_timeout(300)
        ib = _rect(pg, "#isobar")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
        top = max(c0, ib["b"] + 4)  # page coords: right half of #c, below the isobar
        clip = {"x": c["x"] + c["w"] / 2, "y": top, "width": c["w"] / 2, "height": c0 + c["h"] - top}
        before = _dark_pixels(pg, clip)
        pg.click(f'#plydock button[data-node="{P3}"]'); pg.wait_for_timeout(500)
        iso = _dark_pixels(pg, clip)
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
        after = _dark_pixels(pg, clip)
        print("DARK", width, before, iso, after)
        assert before > 500, before
        assert iso < before * 0.5, (before, iso)
        assert abs(after - before) <= before * 0.2, (before, after)
        b.close()
    s.shutdown()


def test_gu_shear_web_offers_no_plies(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = _open_gl(p, url, 1180)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.shear-web"]')
        chip = pg.locator('#parts .chip[data-cid="canard.shear_web"]')
        assert chip.count() == 1 and "plies" not in chip.text_content()
        chip.click()
        assert not pg.is_visible("#plydock")
        b.close()
    s.shutdown()
