"""M2.8 strake geometry (chapter 21): planform lines, the two inside surfaces, plates, skins, tank volume, clearances, left-hand mirror.

Stations are asserted against literal book numbers (plans-1980:p141, p142, p143, p147), not against the builder's own constants.
"""

import ast
import io
import math
import tokenize
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from core import strake_book as sb
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl
from core.sources import check_citation

REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
    "strake.ribs",
    "strake.baffles",
    "strake.leading_edge",
    "strake.skins",
    "strake.sump",
    "strake.tank",
    "strake.fairing",
    "strake.fittings",
}


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


def vol_of(wp) -> float:
    return volume(comp(wp))


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
def right():
    return sb.build_strake("right")


@pytest.fixture(scope="module")
def left():
    return sb.build_strake("left")


# ---- planform lines against literal p147 numbers ----
def test_le_polyline_is_the_p147_stations():
    pts = sb._le_points()
    assert pts[0][0] == 50.0 and pts[1] == (73.3, 23.0) and pts[2] == (99.5, 45.0)
    assert pts[3] == (113.9, 58.0)  # the wing LE at BL 58 (CP25 LPC 7)
    assert sb.le_fs(34.0) == pytest.approx(73.3 + 11 * 26.2 / 22)
    assert sb.le_bl(86.4) == pytest.approx(34.0)


def test_spar_face_and_the_outboard_skin_corner():
    assert sb.spar_fs(23.0) == 118.5
    assert sb.spar_fs(45.0) == pytest.approx(121.8, abs=0.05)
    assert sb.BL_END == pytest.approx(54.6, abs=0.05)  # 23 + sqrt(32.0^2 - 4.9^2), p142
    assert sb.X_END == pytest.approx(123.3, abs=0.05)
    assert sb.SPAR_AT_SIDE == pytest.approx(
        116.6, abs=0.1
    )  # p142 derives 116.8 from a straight 11.7 side


def test_fuselage_side_is_the_box_models_outer_face():
    assert sb.side_outer(50.0) == pytest.approx(12.3)
    assert sb.side_outer(103.5) == pytest.approx(11.27, abs=0.01)  # p147 scales 11.3


def test_jig_plane_is_the_p143_heights():
    assert sb.jig_h(23.0) == 3.45 and sb.jig_h(45.0) == pytest.approx(2.65)
    assert sb.bot_outer_wl(23.0) == pytest.approx(17.4 - 3.45)
    assert sb.bot_outer_wl(45.0) == pytest.approx(17.4 - 2.65)
    assert math.degrees(math.atan(0.8 / 22)) == pytest.approx(2.08, abs=0.01)


# ---- the two inside surfaces against the printed part heights (literal numbers) ----
def test_heights_come_out_at_the_printed_baffle_heights():
    assert sb.inner_height(105.0, 23.0) == pytest.approx(7.3, abs=0.02)  # B23 7.3 high
    assert sb.inner_height(97.7, 23.2) == pytest.approx(
        7.3, abs=0.05
    )  # DB fore end 7.3
    assert sb.inner_height(103.5, sb.side_outer(103.5)) == pytest.approx(
        7.75, abs=0.05
    )  # BAB inboard 7.75
    assert sb.inner_height(97.4, 22.8) == pytest.approx(
        7.3, abs=0.05
    )  # BAB outboard 7.3


def test_db_aft_end_is_off_the_printed_6_5_by_the_nose_profile_bleed():
    h = sb.inner_height(115.0, 44.8)
    # printed 6.5; the nose profile (measured only at the fuselage side) still pulls the surfaces together 15 in aft of the LE at BL 45
    assert h == pytest.approx(6.16, abs=0.05)
    assert 6.5 - h < 0.4


def test_nose_table_is_reproduced_at_the_fuselage_side():
    for st, top, bot in (
        (65.8, 4.0, 6.55),
        (63.0, 2.9, 7.35),
        (60.0, 2.15, 7.9),
        (56.0, 1.7, 8.45),
        (52.0, 1.55, 8.8),
        (47.0, 1.45, 9.05),
        (42.0, 1.40, 9.1),
    ):
        x = sb.SPAR_AT_SIDE - st
        bl = sb.side_outer(x)
        assert 23.0 - sb.top_inner_wl(x, bl) == pytest.approx(top, abs=0.02), st
        assert 23.0 - sb.bot_inner_wl(x, bl) == pytest.approx(bot, abs=0.03), st


def test_the_nose_is_2_55_thick_where_the_strips_stand():
    h = sb.inner_height(50.8, sb.side_outer(50.8))
    assert h == pytest.approx(2.55, abs=0.05)  # BLE and TLE are 2.55 wide (p141)


def test_top_inside_plane_is_the_cutout_top_edge():
    assert sb.TOP_IN_WL == pytest.approx(21.6)
    # well aft of the nose (u past the table) the surfaces are the planes themselves
    assert sb.top_inner_wl(118.0, 25.0) == pytest.approx(21.6, abs=1e-6)
    assert sb.bot_inner_wl(118.0, 25.0) == pytest.approx(
        17.4 - (3.45 - 2 * 0.8 / 22) + 0.35, abs=1e-6
    )


# ---- the solids ----
def test_every_component_has_parts_valid_positive_solids_and_a_fidelity(right):
    assert set(sb.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    names = {n for ns in sb.COMPONENT_PARTS.values() for n in ns}
    assert names == set(right)
    for n, p in right.items():
        assert p.fidelity in FIDELITIES and p.fidelity in sb.FIDELITIES_USED, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert vol_of(p.solid) > 0, n
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert EXPECTED_COMPONENTS <= set(g.components)


def test_representational_parts_say_so_and_printed_plates_are_derived(right):
    derived = {n for n, p in right.items() if p.fidelity == "derived"}
    assert derived == {"b23", "db", "bab", "tle", "ble"}
    words = (
        "fitted",
        "representational",
        "scaled",
        "void",
        "envelope",
        "not drawn",
        "not unambiguous",
    )
    assert all(
        any(w in p.note for w in words)
        for n, p in right.items()
        if p.fidelity == "representational"
    )


def test_voids_are_the_two_fuselage_openings_and_nothing_else(right):
    assert {n for n, p in right.items() if p.void} == set(sb.STRAKE_PARTS_VOID)
    assert all("void" in right[n].note for n in sb.STRAKE_PARTS_VOID)


def test_plan_extents_are_the_p147_stations(right):
    sk = bb(right["skin_top"].solid)
    assert sk.xmin == pytest.approx(50.4, abs=0.1)  # LE at the fuselage side, F.S. 50
    assert sk.xmax == pytest.approx(
        122.9, abs=0.2
    )  # the aft corner at the spar face, 123.3
    assert sk.ymax == pytest.approx(54.6, abs=0.05)
    r45 = bb(right["rib_r45"].solid)
    assert r45.ymin == pytest.approx(45.0 - 0.175, abs=1e-3)
    assert r45.ymax == pytest.approx(45.0 + 0.175, abs=1e-3)
    assert r45.xmax < 121.8  # stops short of the spar face


def test_lengths_close_against_the_printed_part_lengths(right):
    b = bb(right["b23"].solid)
    assert b.xmax - b.xmin == pytest.approx(21.3, abs=0.1)  # B23 printed 21.3
    r23 = bb(right["rib_r23"].solid)
    assert r23.xmax - r23.xmin == pytest.approx(23.9, abs=0.1)  # the plan: 73.3 to 97.2
    tle = bb(right["tle"].solid)
    assert math.hypot(99.5 - 73.3, 45.0 - 23.0) == pytest.approx(34.2, abs=0.05)
    assert abs(34.2 - 33.5) < 1.0  # printed 33.5, ends bevelled
    assert tle.xmax - tle.xmin == pytest.approx(26.4, abs=0.4)


def test_plates_and_skins_are_0_35_foam(right):
    assert bb(right["rib_r23"].solid).ymax - bb(
        right["rib_r23"].solid
    ).ymin == pytest.approx(0.35, abs=1e-3)
    for n in ("skin_top", "skin_bottom"):
        s = right[n].solid.val()
        box = bb(right[n].solid)
        probe = (
            cq.Workplane("XY")
            .box(0.1, 0.1, 10.0)
            .translate((100.0, 35.0, (box.zmin + box.zmax) / 2))
        )
        thick = volume(s.intersect(probe.val())) / 0.01
        assert thick == pytest.approx(0.35, abs=0.01), n


def test_skin_bottom_is_the_jig_plane_and_top_is_wl_21_95(right):
    bot = bb(right["skin_bottom"].solid)
    assert bot.zmin == pytest.approx(
        z_of_wl(17.4 - sb.jig_h(sb.side_outer(80.0))), abs=0.1
    )
    top = bb(right["skin_top"].solid)
    assert top.zmax == pytest.approx(z_of_wl(21.6 + 0.35), abs=1e-3)


def test_tank_volume_is_a_separate_envelope_near_the_printed_capacity(right):
    gal = right["tank"].solid.val().Volume() / 231.0
    assert (
        22.0 < gal < 28.0
    )  # plans 25.5, manual 28, model 26: order of magnitude only, not a check against either
    assert sb.tank_volume_gal() == pytest.approx(gal)
    assert (
        right["tank"].fidelity == "representational"
        and "overlaps the baffles by design" in right["tank"].note
    )
    both = 2 * gal
    assert 44.0 < both < 56.0


def test_sump_blister_is_21_long_from_103_5_and_2_75_deep(right):
    b = bb(right["sump_blister"].solid)
    assert b.xmin == pytest.approx(103.5, abs=1e-6)
    assert b.xmax - b.xmin == pytest.approx(21.0, abs=1e-6)
    assert b.zmax - b.zmin == pytest.approx(
        2.75 + 0.0, abs=0.35
    )  # leg 2.75 at full size, the top plane steps up near the spar
    assert b.xmax == pytest.approx(
        124.5
    )  # flush with the firewall, within 0.5 (p144 derives 124.5 from FS 125)


def test_fittings_sit_where_the_page_says(right):
    cap = bb(right["fuel_cap"].solid)
    assert cap.xmax - cap.xmin == pytest.approx(2.25, abs=1e-3)  # 2 1/4 in hole saw
    drain = bb(right["drain_insert"].solid)
    assert (drain.xmax - drain.xmin, drain.ymax - drain.ymin) == (
        pytest.approx(1.0),
        pytest.approx(1.0),
    )
    vent = bb(right["vent_line"].solid)
    assert vent.zmax - vent.zmin == pytest.approx(
        0.5, abs=0.02
    )  # opens 1/2 in above the top
    tube = bb(right["outlet_tube"].solid)
    assert tube.xmin + 0.19 == pytest.approx(
        112.0, abs=0.02
    )  # 13 in forward of the firewall
    assert tube.ymax - tube.ymin == pytest.approx(0.4, abs=0.02)  # sticks out 0.4 in


def test_cutouts_are_the_p142_table_in_the_fuselage_side(right):
    cb = bb(right["cutout_baggage"].solid)
    assert cb.xmin == pytest.approx(sb.SPAR_AT_SIDE - 65.8, abs=1e-6)
    assert cb.xmax == pytest.approx(sb.SPAR_AT_SIDE - 42.0, abs=1e-6)
    assert cb.zmax == pytest.approx(
        z_of_wl(23.0 - 1.40), abs=1e-6
    )  # the 1.40 top depth at the aft end, WL 21.6
    ct = bb(right["cutout_tank"].solid)
    assert ct.xmin == pytest.approx(sb.SPAR_AT_SIDE - 30.0, abs=1e-6)
    assert ct.xmax == pytest.approx(sb.SPAR_AT_SIDE - 15.0, abs=1e-6)
    assert ct.zmin == pytest.approx(z_of_wl(23.0 - 9.15), abs=1e-6)


# ---- clearances ----
def test_no_strake_solid_overlaps_another_except_the_floxed_joints(right):
    names = [n for n, p in right.items() if not p.void and n not in sb.INSET_PARTS]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            v = overlap(right[a].solid, right[b].solid)
            if frozenset((a, b)) in sb.JOINTS:
                assert v < sb.JOINT_MAX_CU_IN, (a, b, v)
            else:
                assert v < 1e-3, (a, b, v)


def test_the_strake_is_clear_of_the_fuselage_the_spar_and_the_wing(right):
    from core.canopy_book import build_canopy
    from core.firewall_book import build_firewall
    from core.nose_book import build_nose
    from core.spar_book import build_spar
    from core import wing_book as wb

    airframe = {}
    for pref, d in (
        ("fus", build_fuselage()),
        ("spar", build_spar()),
        ("nose", build_nose()),
        ("fw", build_firewall()),
        ("can", build_canopy()),
        ("wing", wb.build_wing("right")),
    ):
        for n, p in d.items():
            if p.void or n in {"jigs", "jig", "blocks"}:
                continue
            airframe[f"{pref}.{n}"] = p.solid
    # the M2.6 canopy hinge fitting stands 0.45 in lower than the strake top skin at the fuselage side: a fitted-size overlap of the canopy chapter
    allowed = {("skin_top", "can.hinge_fuselage"): 0.35}
    for n, p in right.items():
        if p.void:
            continue
        for k, s in airframe.items():
            v = overlap(p.solid, s)
            assert v < allowed.get((n, k), 1e-3), (n, k, v)


def test_the_strake_butts_the_spar_forward_face(right):
    from core.spar_book import build_spar

    spar = build_spar()["box"].solid
    sk = bb(right["skin_top"].solid)
    sp = bb(spar)
    assert sk.xmax < sp.xmax and sk.xmax >= 118.5 and sp.xmin == pytest.approx(118.5)
    assert sk.xmax == pytest.approx(122.9, abs=0.2)


def test_left_strake_is_the_mirror_of_the_right(right, left):
    for n in right:
        a, b = bb(right[n].solid), bb(left[n].solid)
        assert (b.ymin, b.ymax) == (pytest.approx(-a.ymax), pytest.approx(-a.ymin)), n
        assert (b.xmin, b.xmax) == (pytest.approx(a.xmin), pytest.approx(a.xmax)), n
        assert vol_of(left[n].solid) == pytest.approx(
            vol_of(right[n].solid), rel=1e-9
        ), n
    assert left["tank"].void == right["tank"].void is False


def test_no_hard_coded_book_stations_in_the_builder():
    banned = {
        73.3,
        99.5,
        118.5,
        103.5,
        8.57,
        21.3,
        28.5,
        54.6,
        2.65,
        3.45,
        7.3,
        6.5,
        25.5,
        33.5,
        4.9,
    }
    tree = ast.parse((REPO / "core" / "strake_book.py").read_text())
    nums = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, float)
    }
    assert not (nums & banned), nums & banned


def test_fitted_constants_carry_the_comment_on_the_statement():
    src = (REPO / "core" / "strake_book.py").read_text()
    lines = src.splitlines()
    seen = 0
    for node in ast.parse(src).body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("FITTED_")
        ):
            seen += 1
            toks = [
                t
                for t in tokenize.generate_tokens(
                    io.StringIO(
                        "\n".join(lines[node.lineno - 1 : node.end_lineno])
                    ).readline
                )
                if t.type == tokenize.COMMENT
            ]
            assert any(
                ("fitted, not book" in t.string)
                or ("book" in t.string)
                or ("derived" in t.string)
                for t in toks
            ), node.targets[0].id
    assert seen >= 25
