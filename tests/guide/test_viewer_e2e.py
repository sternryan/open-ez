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
