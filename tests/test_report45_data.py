"""Structure and citation checks for data/criteria/report45.yaml."""

import itertools
from pathlib import Path

import yaml

from core.sources import check_citation

DATA = Path(__file__).resolve().parents[1] / "data" / "criteria" / "report45.yaml"
TOP_META = {"source_sha256", "source_id", "transcribed_by", "reread"}


def _load():
    return yaml.safe_load(DATA.read_text())


def _walk(node, path=""):
    """Yield (path, dict) for every mapping in the tree."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from _walk(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def _is_point(d):
    return "x" in d and "y" in d


def _is_leaf(d):
    return "value" in d or _is_point(d)


def validate(doc):
    """Return a list of problems in a criteria document."""
    errs = []
    for path, d in _walk(doc):
        if not _is_leaf(d):
            continue
        cite = d.get("cite")
        if not cite:
            errs.append(f"{path}: missing cite")
        else:
            try:
                check_citation(cite)
            except ValueError as e:
                errs.append(f"{path}: {e}")
        if _is_point(d):
            if "fig" not in d:
                errs.append(f"{path}: chart point lacks fig")
            if d.get("chart-read") is not True:
                errs.append(f"{path}: chart point not chart-read true")
            if "y_uncertainty" not in d:
                errs.append(f"{path}: chart point lacks uncertainty")
    return errs


def test_header():
    doc = _load()
    assert len(doc["source_sha256"]) == 64
    assert doc["transcribed_by"] == "crew"
    rr = doc["reread"]
    assert rr == "pending" or rr["status"] in {"partial", "done"}


def test_every_leaf_cited_and_chart_points_tagged():
    assert validate(_load()) == []


def test_has_leaves_and_points():
    doc = _load()
    nodes = [d for _, d in _walk(doc) if _is_leaf(d)]
    assert sum(1 for d in nodes if _is_point(d)) >= 40
    assert sum(1 for d in nodes if not _is_point(d)) >= 40


def test_wing_constants():
    w = _load()["wing"]
    assert w["limit_numerator"]["value"] == 200
    assert w["Vd_basis"]["value"] == "IAS"
    assert w["Vd_unit"]["inference"] is True


def test_fig2_monotonic_non_increasing():
    pts = _load()["aileron"]["fig2_points"]
    pts = sorted(pts, key=lambda p: p["x"])
    assert [p["x"] for p in pts][:1] == [0]
    ys = [p["y"] for p in pts]
    assert all(b <= a for a, b in itertools.pairwise(ys))
    assert all(p["fig"] == 2 for p in pts)


def test_fig3_fig4_curves_decreasing():
    doc = _load()
    for curve in (
        doc["fig3"]["elevator_curve"],
        doc["fig3"]["rudder_curve"],
        doc["fig4"]["curve"],
    ):
        pts = sorted(curve["points"], key=lambda p: p["x"])
        ys = [p["y"] for p in pts]
        assert all(b <= a for a, b in itertools.pairwise(ys)), curve["label"]


def test_missing_cite_fixture_fails():
    bad = {"wing": {"limit_numerator": {"value": 200}}}
    assert any("missing cite" in e for e in validate(bad))


def test_unknown_source_fixture_fails():
    bad = {"a": {"value": 1, "cite": "no-such-source:p1"}}
    assert validate(bad)


def test_chart_point_without_tags_fixture_fails():
    bad = {"a": {"points": [{"x": 1, "y": 2, "cite": "faa-report-45:p10"}]}}
    errs = validate(bad)
    assert any("fig" in e for e in errs) and any("uncertainty" in e for e in errs)
