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
