# tests/guide/test_loadpaths.py
"""Load paths: schema, geometry (real solids from layup_geometry), and the graph.json payload. Review Focus 4."""

import json
import textwrap
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

from guide import loadpaths
from guide.build_site import build
from guide.layup_geometry import build_layup
from guide.schema import load_graph, validate

ROOT = Path(__file__).resolve().parents[2]
GRAPH_DIR = ROOT / "guide" / "graph"
G = load_graph(GRAPH_DIR)
TOL = 0.5  # in


@pytest.fixture(scope="module")
def built():
    return build_layup(G)


@pytest.fixture(scope="module")
def paths(built):
    return loadpaths.polylines(G, built)


def _parts_shape(built, parts):
    solids = []
    for cid in parts:
        v = built[cid]
        solids += list(v.values()) if isinstance(v, dict) else [v]
    return cq.Compound.makeCompound(solids).wrapped


def dist_to(shape, pt) -> float:
    d = BRepExtrema_DistShapeShape(cq.Vertex.makeVertex(*pt).wrapped, shape)
    assert d.IsDone()
    return d.Value()


def off_part(built, path, tol=TOL) -> list:
    """Every point and every segment midpoint farther than `tol` from all of the path's parts."""
    shape = _parts_shape(built, path["parts"])
    bad = []
    for seg in path["segments"]:
        pts = [tuple(p) for p in seg]
        pts += [tuple((a + b) / 2 for a, b in zip(p, q)) for p, q in zip(seg, seg[1:])]
        bad += [p for p in pts if dist_to(shape, p) > tol]
    return bad


# ---- schema
def _graph_with(tmp_path, body):
    (tmp_path / "components.yaml").write_text(
        "- {id: canard.core, label: Core, fidelity: unvalidated}\n"
    )
    (tmp_path / "loadpaths.yaml").write_text(textwrap.dedent(body))
    return load_graph(tmp_path)


def test_repo_loadpaths_are_valid():
    assert validate(G) == []
    assert [lp.id for lp in G.loadpaths] == [
        "lift-into-caps",
        "cap-bending",
        "web-shear",
    ]


def test_schema_rejects_unknown_part(tmp_path):
    g = _graph_with(
        tmp_path,
        """
        paths:
          - {id: a, label: A, kind: shear, parts: [canard.nope]}
    """,
    )
    assert any("unknown component canard.nope" in e for e in validate(g))


def test_schema_rejects_unknown_kind(tmp_path):
    g = _graph_with(
        tmp_path,
        """
        paths:
          - {id: a, label: A, kind: torsion, parts: [canard.core]}
    """,
    )
    assert any("bad kind torsion" in e for e in validate(g))


def test_schema_rejects_duplicate_id_empty_label_no_parts(tmp_path):
    g = _graph_with(
        tmp_path,
        """
        paths:
          - {id: a, label: A, kind: shear, parts: [canard.core]}
          - {id: a, label: " ", kind: shear, parts: []}
    """,
    )
    errs = validate(g)
    assert (
        any("duplicate id" in e for e in errs)
        and any("label required" in e for e in errs)
        and any("one part" in e for e in errs)
    )


def test_schema_rejects_unknown_key(tmp_path):
    from guide.schema import SchemaError

    with pytest.raises(SchemaError, match="unknown key"):
        _graph_with(
            tmp_path,
            """
            paths:
              - {id: a, label: A, kind: shear, parts: [canard.core], magnitude: 3}
        """,
        )


# ---- geometry
def test_paths_shape(paths):
    assert set(paths) == {"lift-into-caps", "cap-bending", "web-shear"}
    for pid, p in paths.items():
        assert set(p) == {"label", "kind", "parts", "segments"}, pid
        assert p["segments"] and all(
            len(s) >= 2 and all(len(pt) == 3 for pt in s) for s in p["segments"]
        ), pid
    assert len(paths["cap-bending"]["segments"]) == 2 and all(
        len(s) == 9 for s in paths["cap-bending"]["segments"]
    )
    assert len(paths["lift-into-caps"]["segments"]) == 8 and all(
        len(s) == 2 for s in paths["lift-into-caps"]["segments"]
    )


@pytest.mark.parametrize("pid", ["lift-into-caps", "cap-bending", "web-shear"])
def test_every_point_and_midpoint_touches_its_parts(
    built, paths, pid
):  # Review Focus 4
    assert off_part(built, paths[pid]) == []


def test_bending_runs_root_to_cap_end_and_web_along_the_span(paths, built):
    for seg in paths["cap-bending"]["segments"]:
        ys = [p[1] for p in seg]
        assert ys[0] == 0 and abs(ys[-1] - 54.0) < 1e-6 and ys == sorted(ys)
    ws = paths["web-shear"]["segments"][0]
    assert ws[0][1] == 0 and abs(ws[-1][1] - 54.0) < 1e-6


def test_checker_flags_a_deliberately_offset_polyline(built, paths):
    p = json.loads(json.dumps(paths["web-shear"]))
    assert off_part(built, p) == []
    p["segments"][0][3][0] += 2.0  # shift one point 2 in chordwise, into air
    assert off_part(
        built, p
    ), "the distance gate must fail on a polyline 2 in off its part"


def test_checker_flags_a_segment_whose_midpoint_is_in_air(built):
    # The wing is ~1 in thick, so no chord between two skin points is >0.5 in from both skins (best pair found: 0.41 in). To isolate the
    # midpoint pass at real geometry we tighten the tolerance to 0.25 in: both endpoints (top and bottom skin, same station) are ~0.02 in
    # from a skin, the midpoint in the foam gap is ~0.38 in from either.
    skins = ["canard.skin_top", "canard.skin_bottom"]
    both = _parts_shape(built, skins)
    top = loadpaths._centre(loadpaths._solids(built, skins[0]), 5.0, x=3.2)
    bot = loadpaths._centre(loadpaths._solids(built, skins[1]), 5.0, x=3.2)
    mid = [(a + b) / 2 for a, b in zip(top, bot)]
    tight = 0.25
    assert (
        dist_to(both, top) < tight and dist_to(both, bot) < tight
    )  # each endpoint passes on its own
    assert dist_to(both, mid) > tight  # the midpoint alone fails
    assert off_part(built, {"parts": skins, "segments": [[top, bot]]}, tol=tight) == [
        tuple(mid)
    ]


# ---- payload
def test_graph_json_carries_loadpaths(tmp_path):
    from tests.guide.render_fixture import make_export

    e = make_export(tmp_path / "e")
    build(
        GRAPH_DIR, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None
    )
    lp = json.loads((tmp_path / "site" / "graph.json").read_text())["loadpaths"]
    assert [p["id"] for p in lp] == ["lift-into-caps", "cap-bending", "web-shear"]
    assert (
        lp[1]["kind"] == "bending"
        and lp[1]["parts"] == ["canard.spar_cap_top", "canard.spar_cap_bottom"]
        and len(lp[1]["segments"]) == 2
    )


def test_graph_json_without_a_model_ships_paths_without_segments(tmp_path):
    build(GRAPH_DIR, tmp_path / "site", models=None, scan_base=None, docs=None)
    lp = json.loads((tmp_path / "site" / "graph.json").read_text())["loadpaths"]
    assert len(lp) == 3 and all(p["segments"] == [] for p in lp)


def test_graph_json_loadpaths_empty_when_graph_has_none(tmp_path):
    from tests.guide.test_schema import gdir  # noqa: F401

    (tmp_path / "components.yaml").write_text(
        "- {id: canard.core, label: Core, fidelity: unvalidated}\n"
    )
    build(tmp_path, tmp_path / "site", models=None, scan_base=None, docs=None)
    assert json.loads((tmp_path / "site" / "graph.json").read_text())["loadpaths"] == []
