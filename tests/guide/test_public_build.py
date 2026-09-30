import json

import pytest

from guide.build_site import build, main
from guide.leakcheck import leaks
from tests.guide.render_fixture import ROOT, make_export, make_renders

REPO_GRAPH = ROOT / "guide" / "graph"


@pytest.fixture(scope="module")
def pub(tmp_path_factory):
    t = tmp_path_factory.mktemp("pub")
    e = make_export(t / "e")
    r = make_renders(t / "r", e)
    out = t / "site"
    build(REPO_GRAPH, out, models=e / "longez.glb", scan_base="/private/scan/", docs=ROOT / "docs" / "superpowers",
          renders=r, public=True)
    return out


def test_public_has_no_leaks(pub):
    assert leaks(pub) == []


def test_leakcheck_catches_planted_leaks(tmp_path):
    (tmp_path / "a.json").write_text('{"u": "x.ts.net", "p": "/Users/a", "s": "private/scan", "f": "I/images/30/30_03.png"}')
    (tmp_path / "b.html").write_text("<p>public " + "domain</p> 100.64.0.1")
    (tmp_path / "c.jpg").write_bytes(b"x")
    (tmp_path / "d.png").write_bytes(b"x")
    found = " ".join(leaks(tmp_path))
    for needle in (".ts.net", "/Users/", "private/", "images/", "public " + "domain", "100.", "c.jpg"):
        assert needle in found


def test_public_strips_plans_references(pub):
    assert json.loads((pub / "config.json").read_text())["scanBase"] is None
    g = json.loads((pub / "graph.json").read_text())
    assert g["pages"] == {} and g["annotations"] == []
    for o in g["ops"]:
        for s in o["sources"]:
            assert s["doc"] != "cobelu" and not s.get("figure") and s.get("scan_pp") is None and not s.get("heading")
    assert not (pub / "classic").exists() and not (pub / "docs").exists()


def test_public_lab_still_loads_its_data(pub):
    assert (pub / "index.html").is_file()
    assert (pub / "models" / "longez.glb").stat().st_size > 0
    g = json.loads((pub / "graph.json").read_text())
    assert g["ops"] and g["layup"] and g["cutaway"]["ops"]
    assert (pub / "renders").is_dir()


def test_private_build_unchanged(tmp_path):
    e = make_export(tmp_path / "e")
    build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base="/private/scan/", docs=None)
    s = tmp_path / "site"
    assert json.loads((s / "config.json").read_text())["scanBase"] == "/private/scan/"
    assert (s / "classic" / "index.html").is_file()
    g = json.loads((s / "graph.json").read_text())
    assert g["pages"] and g["annotations"]
    assert any(x.get("figure") for o in g["ops"] for x in o["sources"])


def test_cli_public_flag_ignores_scan_base(tmp_path):
    e = make_export(tmp_path / "e")
    assert main(["--graph", str(REPO_GRAPH), "--out", str(tmp_path / "s"), "--models", str(e / "longez.glb"),
                 "--scan-base", "/private/x/", "--docs", str(tmp_path / "nodocs"), "--public"]) == 0
    assert json.loads((tmp_path / "s" / "config.json").read_text())["scanBase"] is None
