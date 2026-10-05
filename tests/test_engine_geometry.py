"""M2.8 engine geometry (chapter 23): the striped engine block, the bracket, the cowl outline, the wing-root rib; every part is representational."""

import math
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from core import engine_book as ng
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl
from core.sources import check_citation

REPO = Path(__file__).resolve().parents[1]
G_FLANGE = (
    155.8  # eng_o235_flange_fs, asserted against the config in test_engine_o235_fields
)
EXPECTED_COMPONENTS = {
    "engine.block",
    "engine.bracket",
    "engine.cowl",
    "engine.rib",
    # ledger row 71: the O-235 accessories, one alias group each
    "engine.starter",
    "engine.alternator",
    "engine.magnetos",
    "engine.carburettor",
    "engine.fuel_pump",
    "engine.mount_pads",
}


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


def bb(wp):
    return comp(wp).BoundingBox()


def overlap(sa, sb_) -> float:
    a, b = comp(sa), comp(sb_)
    ba, bbx = a.BoundingBox(), b.BoundingBox()
    if (
        ba.xmax < bbx.xmin
        or bbx.xmax < ba.xmin
        or ba.ymax < bbx.ymin
        or bbx.ymax < ba.ymin
        or ba.zmax < bbx.zmin
        or bbx.zmax < ba.zmin
    ):
        return 0.0
    return volume(a.intersect(b))


@pytest.fixture(scope="module")
def parts():
    return ng.build_engine()


def test_every_component_has_parts_valid_positive_solids_and_is_representational(parts):
    assert set(ng.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    assert {n for ns in ng.COMPONENT_PARTS.values() for n in ns} == set(parts)
    for n, p in parts.items():
        assert p.fidelity == "representational" and p.fidelity in FIDELITIES, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert comp(p.solid).Volume() > 0, n
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert {"engine.block", "engine.bracket", "engine.cowl", "engine.rib"} <= set(
        g.components
    )


def test_block_is_the_o235_compound_placed_from_the_flange_on_bl_0(parts):
    # ledger row 71: was a 30 by 32 by 18 box from FS 127; now the component compound from the flange datum
    import core.engine_o235_book as o

    b = bb(parts["block"].solid)
    assert b.xmin > 125.28  # aft of the stainless-faced firewall
    half = o.FITTED_CASE_WIDTH / 2 + o.FITTED_BARREL_LEN + o.FITTED_HEAD_LEN
    assert (b.ymin, b.ymax) == (
        pytest.approx(-half),
        pytest.approx(half),
    )  # centred on BL 0
    expected = sum(
        comp(f()).Volume()
        for f in (o.crankcase, o.cylinders, o.sump, o.accessory_housing, o.crank_flange)
    )
    assert comp(parts["block"].solid).Volume() == pytest.approx(expected)
    assert b.xmax < G_FLANGE + 1.0  # only the stub and disc pass the flange
    assert (
        "Section II, not held" in parts["block"].note
        and "fitted shape" in parts["block"].note
    )


def test_block_oil_and_starter_stations_fall_inside_it(parts):
    b = bb(parts["block"].solid)
    assert b.xmin < 140.0 < b.xmax  # oil FS 140 (om-1980:p25)
    assert (
        b.xmin < 150.0 < b.xmax
    )  # the case and stub reach station 150+; the starter (a separate part) sits at the prop end (cp-text:p27)
    assert bb(parts["starter"].solid).xmax > 150.0


def test_down_thrust_pitches_the_crank_with_the_prop_flange_end_up(parts):
    ang = ng.DOWN_THRUST_DEG
    assert ang == 2.0
    front = ng.block_bottom_z(127.0)
    aft = ng.block_bottom_z(157.0)
    assert (
        aft > front
    )  # the aft (prop flange) end is higher than the front (magneto end)
    assert math.degrees(math.atan((aft - front) / 30.0)) == pytest.approx(2.0, abs=1e-6)
    # the solid agrees with the transform: its lowest point is the aft-most sump bottom corner, its highest the case front top corner
    import core.engine_o235_book as o

    b = bb(parts["block"].solid)
    low = o.to_fuselage(
        o.FITTED_SUMP_U_START + o.FITTED_SUMP_LEN, 0.0, -o.FITTED_SUMP_DEPTH_BELOW_CL
    )[2]
    high = o.to_fuselage(o.FITTED_CASE_U_START, 0.0, o.FITTED_CASE_HEIGHT / 2)[2]
    assert b.zmin == pytest.approx(low, abs=1e-6)
    assert b.zmax == pytest.approx(high, abs=1e-6)


def test_bracket_is_the_figure_23_1_plate_under_the_block(parts):
    p = bb(parts["bracket"].solid)
    assert p.xmax - p.xmin == pytest.approx(6.5)  # plate length
    assert p.ymax - p.ymin == pytest.approx(2.5)  # plate width
    assert p.zmax < ng.block_bottom_z(p.xmin) and p.zmax < ng.block_bottom_z(p.xmax)
    assert overlap(parts["bracket"].solid, parts["block"].solid) < 1e-6
    # two holes in the 0.063 plate: the plate volume is the box less the holes
    box = 6.5 * 2.5 * 0.063
    holes = math.pi * (0.9**2 + 1.0**2) * 0.063
    plate_and_angle = comp(parts["bracket"].solid).Volume()
    angle = 2 * 0.063 * 2.0 * 2.5 - 0.063 * 0.063 * 2.5
    assert plate_and_angle == pytest.approx(box - holes + angle, rel=1e-3)


def test_cowl_runs_from_the_firewall_to_the_wing_te_and_to_bl_23(parts):
    c = bb(parts["cowl"].solid)
    assert c.xmin == pytest.approx(125.4)
    assert c.xmax == pytest.approx(148.4)  # the wing TE at BL 23, p126
    assert (c.ymin, c.ymax) == (
        pytest.approx(-23.0),
        pytest.approx(23.0),
    )  # meets the wing at BL 23, p171
    assert c.zmax == pytest.approx(z_of_wl(32.8))  # p171, medium
    assert "shape" in parts["cowl"].note and "not drawn" in parts["cowl"].note
    # the block fits inside it
    b = bb(parts["block"].solid)
    assert c.zmin + 0.12 < b.zmin and b.zmax < c.zmax - 0.12


def test_rib_is_020_thick_on_the_inboard_face_of_the_wing_root(parts):
    r = bb(parts["rib_right"].solid)
    assert r.ymax - r.ymin == pytest.approx(0.020)
    assert r.ymax < 23.0  # inboard of the wing root face
    assert r.xmin == pytest.approx(
        125.05
    )  # at the spar face (centre-section spar aft face FS 125.0)
    assert r.xmax == pytest.approx(148.4)  # the trailing edge at the root
    assert "0.20" in parts["rib_right"].note and "typo" in parts["rib_right"].note
    left = bb(parts["rib_left"].solid)
    assert (left.ymin, left.ymax) == (pytest.approx(-r.ymax), pytest.approx(-r.ymin))
    # two cut-outs: the plate is lighter than its outline
    from core import wing_book as wb

    area = 0.5 * (r.zmax - r.zmin) * (r.xmax - r.xmin)
    assert (
        comp(parts["rib_right"].solid).Volume()
        < (r.zmax - r.zmin) * (r.xmax - r.xmin) * 0.020
    )
    assert area > 0 and wb.te_fs(23.0) == pytest.approx(148.4)


_PART_NAMES = list(ng.build_engine())
_SEATED = frozenset(
    ("block", "mount_pads")
)  # intentional: the pads are seated on the case (contract test below)
_XFAIL_PAIRS = {
    frozenset(
        ("block", "starter")
    ): "ledger row 71: the starter box clips the crank stub (0.45 cubic in); frozen layout, not re-tuned",
    frozenset(
        ("carburettor", "cowl")
    ): "ledger row 71: the carburettor pokes through the cowl bottom (2.30 cubic in); frozen layout, not re-tuned",
}
_PAIRS = [
    pytest.param(
        a,
        b,
        id=f"{a}-{b}",
        marks=[pytest.mark.xfail(strict=True, reason=_XFAIL_PAIRS[frozenset((a, b))])]
        if frozenset((a, b)) in _XFAIL_PAIRS
        else [],
    )
    for i, a in enumerate(_PART_NAMES)
    for b in _PART_NAMES[i + 1 :]
    if frozenset((a, b)) != _SEATED
]


@pytest.mark.parametrize("a,b", _PAIRS)
def test_engine_parts_are_clear_of_each_other(parts, a, b):
    assert overlap(parts[a].solid, parts[b].solid) < 1e-6, (a, b)


def test_mount_pads_are_seated_on_the_block(parts):
    # intentional contact (row 71): the four pads sit on the case rear face, half in the case and half in the housing
    blk, pads = comp(parts["block"].solid), comp(parts["mount_pads"].solid)
    assert overlap(parts["block"].solid, parts["mount_pads"].solid) > 1.0
    bb_ = blk.BoundingBox()
    for s in pads.Solids():
        c = s.Center()
        assert (
            bb_.xmin <= c.x <= bb_.xmax
            and bb_.ymin <= c.y <= bb_.ymax
            and bb_.zmin <= c.z <= bb_.zmax
        )


def _airframe():
    from core import strake_book as sb
    from core import wing_book as wb
    from core import winglet_book as wl
    from core.canopy_book import build_canopy
    from core.firewall_book import build_firewall
    from core.spar_book import build_spar

    out = {}
    for pref, d in (
        ("fus", build_fuselage()),
        ("spar", build_spar()),
        ("fw", build_firewall()),
        ("can", build_canopy()),
        ("wingR", wb.build_wing("right")),
        ("wingL", wb.build_wing("left")),
        ("wlR", wl.build_winglet("right")),
        ("strakeR", sb.build_strake("right")),
    ):
        for n, p in d.items():
            if p.void or n in {"jigs", "jig", "jig_lines", "blocks"}:
                continue
            out[(pref, n)] = p.solid
    return out


@pytest.mark.parametrize("name", _PART_NAMES)
def test_engine_parts_are_clear_of_the_airframe(parts, name):
    for (pref, k), s in _airframe().items():
        assert overlap(parts[name].solid, s) < 1e-3, (name, pref, k)


@pytest.mark.xfail(
    strict=True,
    reason="ledger row 71: the bracket (WL 8.04 to 10.11) hangs fully below the cowl inner bottom (WL 11.12); it was positioned from the retired box and is not moved",
)
def test_bracket_is_inside_the_cowl(parts):
    assert (
        bb(parts["bracket"].solid).zmin
        >= bb(parts["cowl"].solid).zmin + ng.FITTED_COWL_T
    )


def test_no_engine_station_is_a_page_value():
    import ast

    tree = ast.parse((REPO / "core" / "engine_book.py").read_text())
    nums = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, float)
    }
    assert not (nums & {246.0, 286.0, 140.0, 127.0, 150.0, 148.4, 23.0, 125.0})


@pytest.mark.xfail(
    strict=True,
    reason="ledger row 71: the carburettor bottom (WL about 10.25) is below the fitted cowl bottom (WL 11.0); the frozen layout is not re-tuned; the sump clears, only the carburettor pokes through",
)
def test_the_carburettor_and_sump_clear_the_cowl_bottom(parts):
    cb = bb(parts["cowl"].solid)
    for n in ("block", "carburettor"):
        assert bb(parts[n].solid).zmin >= cb.zmin + ng.FITTED_COWL_T, n
