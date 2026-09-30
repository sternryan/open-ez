# tests/guide/test_tours.py
"""Chapter tours: schema (guide/graph/tours.yaml), the graph.json payload, and tourSteps on the real graph. Review Focus 5."""
import json
import subprocess
import textwrap
from pathlib import Path

import pytest

from guide.build_site import build
from guide.schema import SchemaError, load_graph, validate
from tests.guide.test_schema import gdir  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
GRAPH_DIR = ROOT / "guide" / "graph"
TOUR_JS = (ROOT / "guide" / "viewer" / "js" / "tour.js").as_uri()


def _graph_with(tmp_path, body):
    (tmp_path / "tours.yaml").write_text(textwrap.dedent(body))
    return load_graph(tmp_path)


def test_repo_tours_are_valid():
    g = load_graph(GRAPH_DIR)
    assert validate(g) == []
    assert {"r30.bottom-spar-cap", "r30.bottom-skin", "r30.shear-web", "r30.top-spar-cap", "r30.top-skin"} <= set(g.tours)


def test_bottom_plies_are_viewed_from_below():
    g = load_graph(GRAPH_DIR)
    for op in ("r30.bottom-spar-cap", "r30.bottom-skin"):
        assert g.tours[op]["position"][1] < 0, op  # the camera sits under the airplane
    for op in ("r30.top-spar-cap", "r30.top-skin"):
        assert g.tours[op]["position"][1] > g.tours[op]["target"][1], op


def test_schema_rejects_a_shot_for_an_unknown_op(gdir):  # noqa: F811
    g = _graph_with(gdir, """
        shots:
          c10.nope: {target: [0, 0, 0], position: [1, 1, 1]}
    """)
    assert any("unknown op c10.nope" in e for e in validate(g))


def test_schema_accepts_a_shot_for_a_known_op(gdir):  # noqa: F811
    g = _graph_with(gdir, """
        shots:
          c10.cores: {target: [0, 0, -10], position: [1, 1.5, 30]}
    """)
    assert validate(g) == [] and g.tours["c10.cores"] == {"target": [0, 0, -10], "position": [1, 1.5, 30]}


@pytest.mark.parametrize("shot", [
    "{target: [0, 0], position: [1, 1, 1]}",          # too short
    "{target: [0, 0, 0, 0], position: [1, 1, 1]}",    # too long
    "{target: [0, 0, x], position: [1, 1, 1]}",       # not a number
    "{target: [0, 0, true], position: [1, 1, 1]}",    # a bool is not a number
    "{target: 5, position: [1, 1, 1]}",               # not a list
    "{target: [0, 0, 0]}",                            # position missing
])
def test_schema_rejects_a_malformed_vector(gdir, shot):  # noqa: F811
    with pytest.raises(SchemaError, match="c10.cores"):
        _graph_with(gdir, f"shots:\n  c10.cores: {shot}\n")


def test_schema_rejects_unknown_keys(gdir):  # noqa: F811
    with pytest.raises(SchemaError, match="unknown key"):
        _graph_with(gdir, "shots:\n  c10.cores: {target: [0, 0, 0], position: [1, 1, 1], fov: 30}\n")
    with pytest.raises(SchemaError, match="unknown key"):
        _graph_with(gdir, "shots: {}\nextra: 1\n")


def test_graph_json_carries_tours(tmp_path):
    build(GRAPH_DIR, tmp_path / "site", None, None, None)
    t = json.loads((tmp_path / "site" / "graph.json").read_text())["tours"]
    g = load_graph(GRAPH_DIR)
    assert t == {k: v for k, v in g.tours.items()} and "r30.bottom-skin" in t


def test_graph_json_tours_empty_when_graph_has_none(gdir, tmp_path):  # noqa: F811
    build(gdir, tmp_path / "site", None, None, None)
    assert json.loads((tmp_path / "site" / "graph.json").read_text())["tours"] == {}


JS = """
import { readFileSync } from "node:fs";
import { tourSteps } from "%(tour_js)s";
const g = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = {};
for (const [v, ch] of [["roncz", 30], ["gu", 10], ["gu", 12]]) out[`${v}:${ch}`] = tourSteps(g, v, ch);
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def real(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("tours")
    build(GRAPH_DIR, tmp / "site", None, None, None)
    js = tmp / "run.mjs"
    js.write_text(JS % {"tour_js": TOUR_JS})
    r = subprocess.run(["node", str(js), str(tmp / "site" / "graph.json")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout), json.loads((tmp / "site" / "graph.json").read_text())


@pytest.mark.parametrize("key,variant,chapter", [("roncz:30", "roncz", 30), ("gu:10", "gu", 10), ("gu:12", "gu", 12)])
def test_tour_steps_are_the_visible_non_stub_ops_of_the_chapter_in_graph_order(real, key, variant, chapter):
    steps, g = real
    by = {o["id"]: o for o in g["ops"]}
    want = [i for i in g["order"] if by[i]["chapter"] == chapter and not by[i]["stub"]
            and ("both" in by[i]["variants"] or variant in by[i]["variants"])]
    assert want and [s["op"] for s in steps[key]] == want
    for s in steps[key]:
        assert s["shot"] is None or s["shot"] == g["tours"][s["op"]]
