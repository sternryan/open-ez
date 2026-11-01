"""Geometry-derived cloth quantities (P2-B, contract 18).

The functions raise NotImplementedError until the bodies land. Expectations
are the contract: band area within 1%, no solid means omitted, catalog yards
from roll width, and a missing thickness or width leaves the authored estimate.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from core.structures import CanardGenerator
from guide import layup, quantities
from guide.catalog import DATA, load_catalog
from guide.layup_geometry import PLY_T, WEB_XC, Planform
from guide.schema import Buy, Graph, Operation, load_graph

ROOT = Path(__file__).resolve().parents[2]
G = load_graph(ROOT / "guide" / "graph")
CATALOG = load_catalog(DATA / "catalog" / "prices.yaml")


def _op(op_id: str, materials: tuple[dict, ...] = ()) -> Operation:
    return Operation(id=op_id, chapter=30, title=op_id, materials=materials)


def one_ply_graph() -> Graph:
    """Shear web reduced to the single BL-10 BID ply. Skins have no cloth.

    Spar-cap ops still emit their one UND ply (layup.plies always does).
    """
    ops = {}
    for op_id in layup.INCLUDED_OPS:
        mats: tuple[dict, ...] = ()
        if op_id == "r30.shear-web":
            mats = (
                {"cloth": "BID", "plies": 1, "where": "45 degrees, inboard of BL 10"},
            )
        ops[op_id] = _op(op_id, mats)
    return Graph(ops=ops)


def _web_sheet_m2(bl_max: float) -> float:
    """Area of one order-1 web sheet, right-hand half, from the planform.

    The solid is a ruled loft of the end rectangles, so the sheet area is the
    trapezoid of the end heights. Independent of CadQuery volume.
    """
    pf = Planform.from_generator(CanardGenerator())

    def height(bl: float) -> float:
        x0 = pf.le_x(bl) + WEB_XC * pf.chord(bl) - PLY_T
        top = pf.surface(bl, "top")
        bot = pf.surface(bl, "bottom")
        zt = float(np.interp(x0, top[:, 0], top[:, 1]))
        zb = float(np.interp(x0, bot[:, 0], bot[:, 1]))
        return zt - zb

    area_in2 = (height(0.0) + height(bl_max)) / 2.0 * bl_max
    return area_in2 * quantities.M_PER_IN**2


def test_one_ply_area():
    # The ply runs BL -10..10: the solid is the right half, the op cloths both.
    expected = 2 * _web_sheet_m2(10.0)
    got = quantities.cloth_m2_by_op(one_ply_graph())["r30.shear-web"]["BID"]
    assert got == pytest.approx(expected, rel=0.01)


def test_no_solid_omitted():
    areas = quantities.cloth_m2_by_op(G)
    solid_ops = {p.op for p in layup.plies(G)}
    assert "r30.align-canard" not in solid_ops
    assert "r30.align-canard" not in areas
    assert "r30.elev-skin-bottom" not in areas
    assert "r30.shear-web" in areas
    assert "r30.bottom-skin" in areas
    assert set(areas) <= solid_ops


def test_catalog_unit_conversion():
    item = CATALOG["bid-7725"]
    assert item.unit == "yd"
    width_in = quantities.ROLL_WIDTH_IN["bid-7725"].value
    assert width_in == 38.0
    area_m2 = 1.0
    yards = area_m2 / (width_in * quantities.M_PER_IN * quantities.M_PER_YD)
    got = quantities.m2_to_catalog_qty(area_m2, width_in, item.unit)
    assert got == pytest.approx(yards)
    assert got != pytest.approx(area_m2)


def test_missing_conversion_keeps_flag():
    bid = Buy("bid-7725", 1.48, "estimate")
    assert quantities.PLY_THICKNESS_IN["BID"].flag == "unsourced"
    assert quantities.PLY_THICKNESS_IN["UND"].flag == "unsourced"
    kept = quantities.derived_cloth_buy(bid, 1.5)
    assert kept.qty == bid.qty
    assert kept.flag == bid.flag

    peel = Buy("peel-ply-582c", 0.026, "estimate")
    assert "peel-ply-582c" not in quantities.ROLL_WIDTH_IN
    kept = quantities.derived_cloth_buy(peel, 1.5)
    assert kept.qty == peel.qty
    assert kept.flag == peel.flag


def test_resin_mass_from_ratio_has_no_scrap():
    cloth_kg = 4.0
    assert quantities.RESIN_TO_CLOTH_BY_WEIGHT == 1.0
    mass = quantities.resin_mass_kg(cloth_kg)
    assert mass == pytest.approx(cloth_kg * quantities.RESIN_TO_CLOTH_BY_WEIGHT)
    assert mass != pytest.approx(cloth_kg * 1.25)


def _sourced(monkeypatch):
    """Pretend both cloth thicknesses are sourced so a derived buy is possible."""
    for cloth in ("BID", "UND"):
        m = quantities.PLY_THICKNESS_IN[cloth]
        monkeypatch.setitem(
            quantities.PLY_THICKNESS_IN,
            cloth,
            quantities.Measure(m.value, "page", "test"),
        )


def _plan_buys(o):
    return (o["plan"] or {}).get("buy", [])


def _buys(ops_json, op_id):
    return {b["item"]: b for o in ops_json if o["id"] == op_id for b in _plan_buys(o)}


def test_site_derived_buy(monkeypatch, tmp_path):
    from guide import build_site

    ops_json = [build_site._op_json(G.ops[i]) for i in G.ops]
    before = {o["id"]: _plan_buys(o) for o in ops_json}

    # Unsourced thickness: every shipped buy keeps its authored qty and flag.
    kept = build_site.derive_cloth_buys(G, ops_json)
    assert {o["id"]: _plan_buys(o) for o in kept} == before

    _sourced(monkeypatch)
    areas = quantities.cloth_m2_by_op(G)
    got = build_site.derive_cloth_buys(G, ops_json, areas)
    # Authored "derived" flags exist on other items; count only changed buys.
    derived = {o["id"] for o in got if _plan_buys(o) != before[o["id"]]}
    assert derived == {"r30.bottom-skin", "r30.top-skin"}
    for op_id in derived:
        new, old = _buys(got, op_id), _buys(ops_json, op_id)
        for item, b in new.items():
            cloth = quantities.CLOTH_OF_ITEM.get(item)
            if cloth is None:
                assert b == old[item]  # resin, peel ply: untouched
                continue
            width = quantities.ROLL_WIDTH_IN[item].value
            yd = quantities.m2_to_catalog_qty(areas[op_id][cloth], width, "yd")
            assert b["qty"] == pytest.approx(yd)
            assert b["qty"] != pytest.approx(areas[op_id][cloth])  # never m2
    # Ops with a cloth buy but no layup solid keep the authored estimate.
    assert _buys(got, "f04.front-seat-bkhd-back")["bid-7725"]["flag"] == "estimate"
    assert _buys(got, "f04.front-seat-bkhd-back") == _buys(
        ops_json, "f04.front-seat-bkhd-back"
    )
    assert ops_json == [build_site._op_json(G.ops[i]) for i in G.ops]  # input unmutated

    # A cloth with no roll width keeps the authored buy even when sourced.
    monkeypatch.delitem(quantities.ROLL_WIDTH_IN, "bid-7725")
    got = build_site.derive_cloth_buys(G, ops_json, areas)
    assert (
        _buys(got, "r30.top-skin")["bid-7725"]
        == _buys(ops_json, "r30.top-skin")["bid-7725"]
    )
    assert _buys(got, "r30.top-skin")["und-7715"]["flag"] == "derived"

    # build() ships the derived buys in graph.json.
    monkeypatch.setitem(
        quantities.ROLL_WIDTH_IN, "bid-7725", quantities.Measure(38.0, "page", "test")
    )
    out = tmp_path / "site"
    build_site.build(
        ROOT / "guide" / "graph",
        out,
        models=None,
        scan_base=None,
        docs=None,
        public=True,
    )
    shipped = json.loads((out / "graph.json").read_text())["ops"]
    assert _buys(shipped, "r30.top-skin")["bid-7725"]["flag"] == "derived"
    assert _buys(shipped, "r30.top-skin")["mgs-lr285-gal"]["flag"] == "estimate"


def _measure(value, flag: str) -> quantities.Measure:
    return quantities.Measure(value, flag, "test")


def test_null_estimate_thickness_and_unsourced_width_stay_authored(monkeypatch):
    """Grader case: null estimated thickness and unsourced width must not derive."""
    monkeypatch.setitem(quantities.PLY_THICKNESS_IN, "BID", _measure(None, "estimate"))
    monkeypatch.setitem(
        quantities.ROLL_WIDTH_IN, "bid-7725", _measure(38.0, "unsourced")
    )
    authored = Buy("bid-7725", 1.48, "estimate")
    got = quantities.derived_cloth_buy(authored, 1.5)
    assert got == authored
    assert got.flag != "derived"


@pytest.mark.parametrize(
    ("thickness", "width"),
    [
        (_measure(None, "page"), _measure(38.0, "page")),
        (_measure(0.0, "page"), _measure(38.0, "page")),
        (_measure(-0.1, "page"), _measure(38.0, "page")),
        (_measure(float("inf"), "page"), _measure(38.0, "page")),
        (_measure(float("nan"), "page"), _measure(38.0, "page")),
        (_measure(0.10, "estimate"), _measure(38.0, "page")),
        (_measure(0.10, "unsourced"), _measure(38.0, "page")),
        (_measure(0.10, "page"), _measure(None, "page")),
        (_measure(0.10, "page"), _measure(0.0, "page")),
        (_measure(0.10, "page"), _measure(-38.0, "page")),
        (_measure(0.10, "page"), _measure(float("inf"), "page")),
        (_measure(0.10, "page"), _measure(float("nan"), "page")),
        (_measure(0.10, "page"), _measure(38.0, "unsourced")),
        (_measure(0.10, "page"), _measure(38.0, "estimate")),
        (_measure(None, "estimate"), _measure(38.0, "unsourced")),
    ],
)
def test_unsupported_conversion_input_keeps_authored_buy(monkeypatch, thickness, width):
    monkeypatch.setitem(quantities.PLY_THICKNESS_IN, "BID", thickness)
    monkeypatch.setitem(quantities.ROLL_WIDTH_IN, "bid-7725", width)
    authored = Buy("bid-7725", 1.48, "estimate")
    assert quantities.can_derive(authored.item) is False
    assert quantities.derived_cloth_buy(authored, 1.5) == authored
