"""Fuel-wetted steps keep MGS and carry an unknown UL94 compatibility flag."""

import importlib.util
from pathlib import Path

import pytest
import yaml

from guide.check import main
from guide.schema import load_graph
from tests.guide.test_plan_fields import with_plan
from tests.guide.test_schema import gdir as _schema_gdir

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "guide" / "graph"
RESINS = ROOT / "data" / "resins"
FUEL_OPS = (
    "f07.skin-right",
    "f07.skin-left",
    "f21.inside-layups",
    "f21.close-tank",
)
WHY = "no published UL94 immersion test of this resin; Block 5 coupon test pending"
FUEL = {
    "wetted": True,
    "fuel": "UL94",
    "resin_compat": "unknown",
    "why": WHY,
    "source": None,
}

gdir = pytest.fixture(_schema_gdir.__wrapped__)


def _script():
    path = ROOT / "scripts" / "apply_plan_values.py"
    spec = importlib.util.spec_from_file_location("apply_plan_values", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_no_placeholder_and_four_ops_flag_unknown():
    hits = []
    for path in sorted(GRAPH.glob("ch*.yaml")):
        if "fuel-resistant-tbd" in path.read_text():
            hits.append(path.name)
    for path in sorted(RESINS.glob("*.yaml")):
        if "fuel-resistant-tbd" in path.read_text():
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []
    graph = load_graph(GRAPH)
    for op_id in FUEL_OPS:
        plan = graph.ops[op_id].plan
        assert plan is not None and plan.resin == "mgs-285-287"
        fuel = plan.fuel
        assert fuel is not None
        assert fuel.wetted is True
        assert fuel.fuel == "UL94"
        assert fuel.resin_compat == "unknown"
        assert fuel.why == WHY
        assert fuel.source is None


def test_fuel_wall_script_sets_unknown_flag():
    mod = _script()
    assert not hasattr(mod, "FUEL_RESIN")
    assert not hasattr(mod, "PLACEHOLDER_RESIN")
    assert mod.FUEL_WALL_OPS == frozenset(FUEL_OPS)
    prepared = mod._prepare(
        "f07.skin-right",
        {"people": 1, "cure": "part", "resin": "mgs-285-287"},
    )
    assert prepared["resin"] == "mgs-285-287"
    assert prepared["fuel"] == FUEL
    rendered = mod.render_plan(prepared)
    assert "fuel-resistant-tbd" not in rendered
    parsed = yaml.safe_load(rendered)
    assert parsed["plan"]["resin"] == "mgs-285-287"
    assert parsed["plan"]["fuel"]["resin_compat"] == "unknown"
    assert parsed["plan"]["fuel"]["source"] is None
    plain = mod._prepare("f06.tape", {"people": 1, "cure": "none"})
    assert "fuel" not in plain


@pytest.mark.parametrize(
    ("plan", "needle"),
    [
        (
            (
                "plan:\n  fuel: {wetted: true, fuel: UL94, resin_compat: sourced, "
                "why: pending, source: null}\n"
            ),
            "sourced needs a source",
        ),
        (
            (
                "plan:\n  fuel: {wetted: true, fuel: UL94, resin_compat: unknown, "
                'why: pending, source: "om-1980:p25"}\n'
            ),
            "unknown carries no source",
        ),
        (
            (
                "plan:\n  fuel: {wetted: true, fuel: UL94, resin_compat: unknown, "
                "why: pending, source: null, note: x}\n"
            ),
            "['note']",
        ),
        (
            (
                "plan:\n  fuel: {wetted: true, fuel: UL94, resin_compat: maybe, "
                "why: pending, source: null}\n"
            ),
            "bad resin_compat",
        ),
    ],
)
def test_fuel_compat_rejected_by_guide_check(gdir, capsys, plan, needle):
    with_plan(gdir, plan)
    assert main(["--schema-only", "--graph", str(gdir)]) == 1
    assert needle in capsys.readouterr().out
