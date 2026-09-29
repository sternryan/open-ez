import json
import pytest
from guide.build_site import build
from guide.schema import SchemaError
from tests.guide.test_schema import gdir  # noqa: F401

def test_build_writes_site(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base="/private/scan-1980/pages/", docs=None)
    g = json.loads((out / "graph.json").read_text())
    assert g["order"][0] == "c03.layup-skills"
    assert {o["id"] for o in g["ops"]} == {"c03.layup-skills", "c10.cores", "c10.twist-check"}
    assert g["ops"][1]["id"] == "c10.cores" and g["ops"][1]["changes"][0]["class"] == "MEO"
    assert json.loads((out / "config.json").read_text())["scanBase"] == "/private/scan-1980/pages/"
    assert (out / "index.html").exists() and not (out / "tests").exists()

def test_build_refuses_invalid_graph(gdir, tmp_path):
    p = gdir / "ch10.yaml"; p.write_text(p.read_text().replace("requires: [c10.cores]", "requires: [nope]"))
    with pytest.raises(SchemaError):
        build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)


from tests.guide.render_fixture import ROOT, make_export, make_renders

REPO_GRAPH = ROOT / "guide" / "graph"


def test_no_renders_means_m1_output(tmp_path):  # CRITICAL regression: M1 builds unchanged
    e = make_export(tmp_path / "e")
    build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["cutaway"] is None and not (tmp_path / "site" / "renders").exists()
    assert [p["order"] for p in g["plies"]["canard.skin_top"]] == [1, 2, 3, 4]


def test_no_models_no_plies(gdir, tmp_path):
    build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["plies"] == {} and g["cutaway"] is None


def test_renders_wired(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    c = g["cutaway"]
    assert c["ops"]["r30.bottom-skin"]["src"] == "renders/op-r30-bottom-skin.png"
    assert [h["bl"] for h in c["heroes"]] == [5.0, 40.0]
    assert c["heroes"][0]["alt"].startswith("Section at BL 5: bottom skin 3 plies")
    assert "shear web 6 at BL 5, 2 at BL 40" in c["count_note"]
    assert (tmp_path / "site" / "renders" / "hero-bl40.png").exists()


@pytest.mark.parametrize("kw,needle", [({"drop": "hero-bl40"}, "hero-bl40"),
                                       ({"bad_png": "op-r30-top-skin"}, "op-r30-top-skin")])
def test_renders_strict(tmp_path, kw, needle):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e, **kw)
    with pytest.raises(SchemaError, match=needle):
        build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)


def test_renders_stale_layup(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    (e / "layup.json").write_text((e / "layup.json").read_text().replace('"semi_span": 63.0', '"semi_span": 70'))
    with pytest.raises(SchemaError, match="layup.json"):
        build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)


def test_renders_need_models(tmp_path):
    with pytest.raises(SchemaError, match="--renders needs --models"):
        build(REPO_GRAPH, tmp_path / "site", models=None, scan_base=None, docs=None, renders=tmp_path)


def test_legend_states_planform_source():  # planform correction: the chord has no plans source
    from guide.build_site import LEGEND
    assert any(e["text"] == "Canard planform from the plans; chord unsourced" for e in LEGEND)
