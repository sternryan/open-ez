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
EXPECTED_COMPONENTS = {"engine.block", "engine.bracket", "engine.cowl", "engine.rib"}


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
    assert EXPECTED_COMPONENTS <= set(g.components)


def test_block_is_an_o235_sized_box_aft_of_the_firewall_on_bl_0(parts):
    b = bb(parts["block"].solid)
    assert b.xmin > 125.28  # aft of the stainless-faced firewall
    assert (b.ymin, b.ymax) == (
        pytest.approx(-16.0),
        pytest.approx(16.0),
    )  # centred on BL 0
    assert comp(parts["block"].solid).Volume() == pytest.approx(30.0 * 32.0 * 18.0)
    assert (
        "Section II, not held" in parts["block"].note
        and "fitted shape" in parts["block"].note
    )


def test_block_oil_and_starter_stations_fall_inside_it(parts):
    b = bb(parts["block"].solid)
    assert b.xmin < 140.0 < b.xmax  # oil FS 140 (om-1980:p25)
    assert (
        b.xmin < 150.0 < b.xmax
    )  # starter and alternator at station 150+ (cp-text:p27)


def test_down_thrust_pitches_the_crank_with_the_prop_flange_end_up(parts):
    ang = ng.DOWN_THRUST_DEG
    assert ang == 2.0
    front = ng.block_bottom_z(127.0)
    aft = ng.block_bottom_z(157.0)
    assert (
        aft > front
    )  # the aft (prop flange) end is higher than the front (magneto end)
    assert math.degrees(math.atan((aft - front) / 30.0)) == pytest.approx(2.0, abs=1e-6)
    # the solid agrees with the formula: its lowest point is at the front bottom corner
    b = bb(parts["block"].solid)
    h = 18.0
    th = math.radians(ang)
    assert b.zmin == pytest.approx(
        z_of_wl(23.0) - (h / 2) * math.cos(th) - 15.0 * math.sin(th), abs=1e-6
    )
    assert b.zmax == pytest.approx(
        z_of_wl(23.0) + (h / 2) * math.cos(th) + 15.0 * math.sin(th), abs=1e-6
    )


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


def test_clear_of_the_airframe_and_of_each_other(parts):
    from core import strake_book as sb
    from core import wing_book as wb
    from core import winglet_book as wl
    from core.canopy_book import build_canopy
    from core.firewall_book import build_firewall
    from core.spar_book import build_spar

    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert overlap(parts[a].solid, parts[b].solid) < 1e-6, (a, b)
    airframe = {}
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
            airframe[(pref, n)] = p.solid
    for n, p in parts.items():
        for (pref, k), s in airframe.items():
            assert overlap(p.solid, s) < 1e-3, (n, pref, k)


def test_no_engine_station_is_a_page_value():
    import ast

    tree = ast.parse((REPO / "core" / "engine_book.py").read_text())
    nums = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, float)
    }
    assert not (nums & {246.0, 286.0, 140.0, 127.0, 150.0, 148.4, 23.0, 125.0})
