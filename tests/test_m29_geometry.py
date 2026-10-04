"""M2.9 geometry (chapters 24 and 26): covers, consoles, thigh support, canard cover, gap seal, cushions, headrests, suitcases; the finish layer's tags.

Only LC1 is ``book`` (its stations are printed); every other solid is ``representational``. The finish is data, never a solid.
"""

import ast
import math
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from config.aircraft_config import config
from core import covers_book as cv
from core import upholstery_book as up
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl
from core.sources import check_citation

G = config.geometry
REPO = Path(__file__).resolve().parents[1]
COVER_COMPONENTS = {
    "cover.aft",
    "cover.console_lc1",
    "cover.consoles",
    "cover.thigh",
    "cover.valve",
    "cover.canard",
    "cover.seal",
}
UPH_COMPONENTS = {"upholstery.cushions", "upholstery.headrests", "upholstery.suitcases"}


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
def covers():
    return cv.build_covers()


@pytest.fixture(scope="module")
def uph():
    return up.build_upholstery()


@pytest.fixture(scope="module")
def parts(covers, uph):
    return {**covers, **uph}


def test_every_component_has_parts_valid_positive_solids_and_a_cited_note(covers, uph):
    assert set(cv.COMPONENT_PARTS) == COVER_COMPONENTS
    assert set(up.COMPONENT_PARTS) == UPH_COMPONENTS
    assert {n for ns in cv.COMPONENT_PARTS.values() for n in ns} == set(covers)
    assert {n for ns in up.COMPONENT_PARTS.values() for n in ns} == set(uph)
    for n, p in {**covers, **uph}.items():
        assert p.fidelity in FIDELITIES, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert comp(p.solid).Volume() > 0, n
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert COVER_COMPONENTS | UPH_COMPONENTS <= set(g.components)


def test_only_lc1_is_book_and_every_other_part_is_a_fitted_shape(covers, uph):
    assert {n for n, p in covers.items() if p.fidelity == "book"} == {"lc1"}
    assert {p.fidelity for n, p in covers.items() if n != "lc1"} == {"representational"}
    assert {p.fidelity for p in uph.values()} == {"representational"}
    assert cv.FIDELITIES_USED == {"book", "representational"}


def test_lc1_stations_offset_and_top_are_the_printed_values(covers):
    b = bb(covers["lc1"].solid)
    assert (b.xmin, b.xmax) == (pytest.approx(52.0), pytest.approx(60.0))
    assert b.ymin == pytest.approx(
        -11.5 + 2.0 - 0.0, abs=0.05
    ) or b.ymin == pytest.approx(-9.5, abs=0.05)
    assert b.ymax - b.ymin == pytest.approx(0.35)
    assert b.zmax == pytest.approx(z_of_wl(11.6))  # WL 11.6 (printed label)
    # 9.1 printed from the floor line; the foot is trimmed to the cockpit floor (fitted)
    assert b.zmax - b.zmin == pytest.approx(9.1, abs=0.2)
    assert "FS 52 to FS 60" in covers["lc1"].note and "trimmed" in covers["lc1"].note


def test_console_pieces_have_the_printed_sizes(covers):
    lc2 = bb(covers["lc2"].solid)
    assert lc2.xmax - lc2.xmin == pytest.approx(30.6)
    assert lc2.ymax - lc2.ymin == pytest.approx(2.35)
    assert lc2.zmax - lc2.zmin == pytest.approx(0.35)
    assert "30.8" in covers["lc2"].note and "unresolved" in covers["lc2"].note
    # the throttle cutout makes it lighter than its box
    assert comp(covers["lc2"].solid).Volume() < 30.6 * 2.35 * 0.35
    lc3 = bb(covers["lc3"].solid)
    assert lc3.xmax - lc3.xmin == pytest.approx(10.6)
    assert comp(covers["lc3"].solid).Volume() < 10.6 * (lc3.zmax - lc3.zmin) * 0.35
    lc4 = bb(covers["lc4"].solid)
    assert lc4.xmax - lc4.xmin == pytest.approx(11.7)
    box = 11.7 * (lc4.zmax - lc4.zmin) * 0.35
    assert comp(covers["lc4"].solid).Volume() == pytest.approx(
        box - math.pi * 0.5**2 * 0.35, rel=1e-3
    )  # one 1 in hole (CP24, not the plans)
    assert "CP24" in covers["lc4"].note
    lc5 = bb(covers["lc5"].solid)
    assert lc5.xmax - lc5.xmin == pytest.approx(18.2)
    assert lc5.ymax - lc5.ymin == pytest.approx(1.9)
    lc6 = bb(covers["lc6"].solid)
    assert lc6.zmax - lc6.zmin == pytest.approx(8.0)
    base = 8.0 / math.tan(math.radians(50)) + 8.0 / math.tan(math.radians(45))
    assert lc6.xmax - lc6.xmin == pytest.approx(base)
    assert base < 18.2  # the triangle sits inside LC5's length
    # LC2 ends at the front seat bulkhead and starts aft of the panel
    assert lc2.xmin > G.fs_panel and lc2.xmax < 71.63
    # LC5 starts behind the bulkhead, so the rear console is aft of the front one
    assert lc5.xmin > lc2.xmax


def test_aft_cover_is_the_printed_block_dished_and_slotted_round_the_strut(covers):
    b = bb(covers["aft_cover"].solid)
    assert b.ymax - b.ymin == pytest.approx(20.0)
    assert b.zmax - b.zmin == pytest.approx(2.0)
    assert b.xmin == pytest.approx(cv.FITTED_AFT_COVER_FWD) and b.xmax <= 125.0 + 1e-6
    full = (b.xmax - b.xmin) * 20.0 * 2.0
    assert comp(covers["aft_cover"].solid).Volume() < full  # dished and slotted
    # the slot is the strut's x extent plus 1/8 in each side: clear of the strut, and nothing of the cover inside the slot
    from core import landing_gear_book as lg

    strut = lg.build_gear()["strut"].solid
    sb = bb(strut)
    assert overlap(covers["aft_cover"].solid, strut) < 1e-6
    probe = cq.Workplane("XY").add(
        cq.Solid.makeBox(
            (sb.xmax - sb.xmin) + 2 * 0.125 - 0.01,
            5.0,
            1.0,
            cq.Vector(sb.xmin - 0.125 + 0.005, -2.5, b.zmin + 0.5),
        )
    )
    assert overlap(covers["aft_cover"].solid, probe) < 1e-6
    assert (
        "conflict" in covers["aft_cover"].note and "LPC 54" in covers["aft_cover"].note
    )


def test_thigh_support_sizes_slope_and_the_valve_cover(covers):
    f = bb(covers["thigh_floor"].solid)
    assert f.ymax - f.ymin == pytest.approx(17.0)
    assert f.xmax - f.xmin == pytest.approx(12.3)
    assert f.xmin > G.fs_panel
    # the floor slopes from the rib height at the front down to the cockpit floor at the aft edge
    assert f.zmax - f.zmin == pytest.approx(3.65 + 0.35, abs=0.05)
    notch = 5.6 * 4.5
    slab_area_plan = 17.0 * 12.3 - notch
    assert comp(covers["thigh_floor"].solid).Volume() == pytest.approx(
        slab_area_plan * 0.35, rel=0.01
    )
    ra, rb = bb(covers["thigh_rib_a"].solid), bb(covers["thigh_rib_b"].solid)
    for r in (ra, rb):
        assert r.xmax - r.xmin == pytest.approx(10.8)
        assert r.zmax - r.zmin == pytest.approx(3.65, abs=0.05)  # at the front
    assert (rb.ymin + rb.ymax) / 2 - (ra.ymin + ra.ymax) / 2 == pytest.approx(5.6)
    # one rib is notched for the fuel lines
    assert (
        comp(covers["thigh_rib_a"].solid).Volume()
        < comp(covers["thigh_rib_b"].solid).Volume()
    )
    v = bb(covers["valve_cover"].solid)
    assert v.ymax - v.ymin == pytest.approx(6.6)
    assert comp(covers["valve_cover"].solid).Volume() == pytest.approx(
        6.6 * 5.0 * 0.025, rel=0.02
    )
    assert "0.025" in covers["valve_cover"].note
    # ribs and floor are bonded: they touch, never overlap; the cover rests on the floor
    assert overlap(covers["thigh_floor"].solid, covers["thigh_rib_a"].solid) < 1e-6
    assert overlap(covers["valve_cover"].solid, covers["thigh_floor"].solid) < 1e-6


def test_canard_cover_is_the_2_in_block_that_stops_short_of_f28(covers):
    b = bb(covers["canard_cover"].solid)
    assert b.zmax - b.zmin == pytest.approx(2.0)
    assert b.xmax < G.fs_f28 and b.xmin > G.fs_f22 + 0.2
    assert (
        "fitted" in covers["canard_cover"].note and "F28" in covers["canard_cover"].note
    )
    # it stands on the canard's top: above the core at the root (canard frame: chord x, span y, thickness z)
    from guide import export_glb as eg

    core = eg.canard_components()["canard.core"]
    core_top = G.canard_le_wl + core.BoundingBox().zmax
    assert b.zmin > core_top


def test_gap_seal_is_half_an_inch_at_the_back_and_a_sixteenth_at_the_front(covers):
    r = covers["seal_right"].solid
    b = bb(r)
    gap, front = 0.5, 0.0625
    ln = b.xmax - b.xmin
    h = b.zmax - b.zmin
    assert b.ymax - b.ymin == pytest.approx(gap)
    assert comp(r).Volume() == pytest.approx((gap + front) / 2 * ln * h, rel=1e-3)
    left = bb(covers["seal_left"].solid)
    assert (left.ymin, left.ymax) == (pytest.approx(-b.ymax), pytest.approx(-b.ymin))
    assert "3/4" in covers["seal_right"].note


def test_cushions_headrests_and_suitcases_have_the_printed_sizes(uph):
    fc, rc = bb(uph["front_cushion"].solid), bb(uph["rear_cushion"].solid)
    assert fc.ymax - fc.ymin == pytest.approx(16.5)
    assert rc.ymax - rc.ymin == pytest.approx(16.0)
    # 2 in of foam: the slabs are bent, so check the volume against width x path x thickness
    assert comp(uph["front_cushion"].solid).Volume() == pytest.approx(
        16.5 * 2.0 * up.front_cushion_path_in(), rel=0.25
    )
    assert up.front_cushion_path_in() < 46.0  # the model's floor and bulkhead end first
    assert (
        "46" in uph["front_cushion"].note and "not placed" in uph["front_cushion"].note
    )
    hf, hr = bb(uph["front_headrest"].solid), bb(uph["rear_headrest"].solid)
    for h, t in ((hf, 2.0), (hr, 1.5)):
        assert (h.ymax - h.ymin, h.zmax - h.zmin) == (
            pytest.approx(4.5),
            pytest.approx(4.5),
        )
        assert h.xmax - h.xmin == pytest.approx(t)
    sr = bb(uph["suitcase_right"].solid)
    assert sr.xmax - sr.xmin == pytest.approx(30.0)
    assert sr.ymax - sr.ymin == pytest.approx(5.0)
    assert sr.zmax - sr.zmin == pytest.approx(18.0)
    sl = bb(uph["suitcase_left"].solid)
    assert sl.xmax - sl.xmin == pytest.approx(
        30.0 - up.FITTED_LEFT_SHORTEN_IN
    )  # shortened, length fitted
    assert (sl.ymin, sl.ymax) == (pytest.approx(-sr.ymax), pytest.approx(-sr.ymin))
    assert (
        "no length" in uph["suitcase_left"].note
        or "fitted" in uph["suitcase_left"].note
    )


def test_suitcase_front_edge_slopes_as_the_front_seat_bulkhead_does():
    # printed 18 high with a 14 in top edge on a 30 in base: the front edge rises 16 in over 18 in
    slope = (30.0 - 14.0) / 18.0
    assert slope == pytest.approx(up._faces()["front"]["slope"], abs=0.01)


def test_the_finish_is_a_layer_of_tags_never_a_solid_and_white_only_on_the_upper_wing_and_canard():
    rows = cv.finish_rows()
    assert rows and not hasattr(cv, "finish_solid")
    white = {r["surface"] for r in rows if r["final_colour"] == "white"}
    assert white == {"wing_upper", "canard_upper"} == set(G.fin_book_white_surfaces)
    assert {r["final_colour"] for r in rows if r["surface"] not in white} == {
        "primer-grey"
    }
    for r in rows:
        fill, primer, paint = r["stages"]
        assert (fill["stage"], primer["stage"], paint["stage"]) == (
            "fill",
            "primer",
            "paint",
        )
        assert fill["thickness_in"] == [0.02, 0.03] and primer["thickness_in"] == [
            0.004,
            0.008,
        ]
        assert paint["thickness_in"] is None  # none printed
        assert [fill["from"], primer["from"], paint["from"]] == [
            "f25.feather-fill",
            "f25.primer",
            "f25.paint-seals",
        ]
        assert not any("weight" in k or "lb" in k for k in r)
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert {r["component"] for r in rows} <= set(g.components)
    assert {r["component"] for r in rows if r["final_colour"] == "white"} == {
        "wing.skins",
        "canard.skin_top",
        "cover.canard",
    }
    # the wing's white is the TOP skin only
    assert [r["match"] for r in rows if r["component"] == "wing.skins"] == [
        "skin_top",
        "skin_bottom",
    ]


def test_no_printed_value_is_typed_in_the_geometry_modules():
    printed = {
        52.0,
        60.0,
        30.6,
        30.8,
        10.6,
        11.7,
        18.2,
        10.8,
        3.65,
        12.3,
        6.6,
        0.0625,
        0.025,
        2.35,
        11.6,
        16.5,
        46.0,
    }
    for mod in ("covers_book", "upholstery_book"):
        tree = ast.parse((REPO / "core" / f"{mod}.py").read_text())
        nums = {
            n.value
            for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, float)
        }
        assert not (nums & printed), (mod, nums & printed)


def test_clear_of_the_airframe_and_of_each_other(parts):
    from core import (
        controls_book,
        electrical_book,
        engine_book,
        firewall_book,
        landing_gear_book,
        nose_book,
        spar_book,
    )
    from core import strake_book as sb
    from core import wing_book as wb
    from core import winglet_book as wl
    from core.canopy_book import build_canopy

    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert overlap(parts[a].solid, parts[b].solid) < 1e-6, (a, b)
    airframe = {}
    for pref, d in (
        ("fus", build_fuselage()),
        ("spar", spar_book.build_spar()),
        ("fw", firewall_book.build_firewall()),
        ("can", build_canopy()),
        ("wingR", wb.build_wing("right")),
        ("wingL", wb.build_wing("left")),
        ("wlR", wl.build_winglet("right")),
        ("strR", sb.build_strake("right")),
        ("strL", sb.build_strake("left")),
        ("gear", landing_gear_book.build_gear()),
        ("nose", nose_book.build_nose()),
        ("ctl", controls_book.build_controls()),
        ("elec", electrical_book.build_electrical()),
        ("eng", engine_book.build_engine()),
    ):
        for n, p in d.items():
            if p.void or n in {
                "jigs",
                "jig",
                "jig_lines",
                "blocks",
                "jig_blocks",
                "datum_board",
                "tank",
            }:
                continue
            airframe[(pref, n)] = p.solid
    for n, p in parts.items():
        for (pref, k), s in airframe.items():
            assert overlap(p.solid, s) < 1e-3, (n, pref, k)
