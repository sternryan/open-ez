"""Additional coverage for ``core.covers_book`` (chapter 24 covers/consoles and chapter 25 finish tags).

Targets public helpers, coordinate/station functions, exact volume and centroid invariants,
caching, and finish-row structure left untested by ``tests/test_m29_geometry.py``.
"""

from __future__ import annotations

import math

import cadquery as cq
import pytest

from config import config
from core import covers_book as cv
from core import landing_gear_book as lg
from core.fuselage_book import front_bulkhead_line_fs, half_width, z_of_wl

G = config.geometry


def _comp(wp: cq.Workplane) -> cq.Compound:
    return cq.Compound.makeCompound(wp.vals())


def _bb(wp: cq.Workplane) -> cq.BoundBox:
    return _comp(wp).BoundingBox()


@pytest.fixture(scope="module")
def covers():
    return cv.build_covers()


def test_prism_xz_extrusion_bounds_and_volume():
    rect_pts = [(10.0, -5.0), (18.0, -5.0), (18.0, 2.0), (10.0, 2.0)]
    rect_wp = cv.prism_xz(rect_pts, -9.5, -9.15)
    rbb = _bb(rect_wp)
    assert (rbb.xmin, rbb.xmax) == (
        pytest.approx(10.0, abs=1e-6),
        pytest.approx(18.0, abs=1e-6),
    )
    assert (rbb.ymin, rbb.ymax) == (
        pytest.approx(-9.5, abs=1e-6),
        pytest.approx(-9.15, abs=1e-6),
    )
    assert (rbb.zmin, rbb.zmax) == (
        pytest.approx(-5.0, abs=1e-6),
        pytest.approx(2.0, abs=1e-6),
    )
    assert _comp(rect_wp).Volume() == pytest.approx(8.0 * 0.35 * 7.0, rel=1e-6)

    tri_pts = [(20.0, 0.0), (26.0, 0.0), (20.0, 4.0)]
    tri_wp = cv.prism_xz(tri_pts, -2.0, 3.0)
    tbb = _bb(tri_wp)
    assert (tbb.ymin, tbb.ymax) == (
        pytest.approx(-2.0, abs=1e-6),
        pytest.approx(3.0, abs=1e-6),
    )
    assert _comp(tri_wp).Volume() == pytest.approx(0.5 * 6.0 * 4.0 * 5.0, rel=1e-6)


def test_wall_y_default_single_station_and_interval_narrowing():
    fs_lc1_fwd = G.cov_book_lc1_fs[0]
    expected_default = -half_width(fs_lc1_fwd) + cv.FITTED_WALL_CLEAR
    assert cv.wall_y() == pytest.approx(expected_default, abs=1e-9)
    assert cv.wall_y(fs_lc1_fwd) == pytest.approx(expected_default, abs=1e-9)

    for fs in (52.0, 75.0, 95.0, 110.0):
        y = cv.wall_y(fs)
        assert y == pytest.approx(-half_width(fs) + cv.FITTED_WALL_CLEAR, abs=1e-9)
        assert y < 0.0

    # Endpoint order invariance and narrowing aft of FS 80
    assert cv.wall_y(75.0, 105.0) == pytest.approx(cv.wall_y(105.0, 75.0), abs=1e-9)
    assert half_width(105.0) < half_width(75.0)
    assert cv.wall_y(75.0, 105.0) == pytest.approx(
        -half_width(105.0) + cv.FITTED_WALL_CLEAR, abs=1e-9
    )
    assert cv.wall_y(75.0, 105.0) > cv.wall_y(75.0)


def test_floor_top_z_and_console_station_helpers():
    for fs in (G.fs_f22, G.cov_book_lc1_fs[0], G.fs_firewall):
        assert cv.floor_top_z(fs) == pytest.approx(cv.FITTED_FLOOR_Z, abs=1e-9)

    assert cv.LC1_TOP_Z == pytest.approx(z_of_wl(G.cov_book_lc1_top_wl), abs=1e-9)
    assert cv.T_CORE == pytest.approx(G.cov_book_console_core_in, abs=1e-9)

    x0, x1 = cv.lc2_span()
    bkhd_fs = front_bulkhead_line_fs(cv.LC1_TOP_Z)
    assert x1 == pytest.approx(bkhd_fs - cv.FITTED_BULKHEAD_CLEAR, abs=1e-9)
    assert x1 - x0 == pytest.approx(G.cov_book_lc2_len_in, abs=1e-9)

    x5 = cv.lc5_x0()
    assert x5 == pytest.approx(bkhd_fs + cv.FITTED_LC5_FROM_BULKHEAD, abs=1e-9)
    assert x5 - x1 == pytest.approx(
        cv.FITTED_BULKHEAD_CLEAR + cv.FITTED_LC5_FROM_BULKHEAD, abs=1e-9
    )


def test_lc1_and_front_console_sides_y_and_z_alignment(covers):
    x0_lc1, x1_lc1 = G.cov_book_lc1_fs
    y_out_lc1 = -half_width(x0_lc1) + G.cov_book_lc1_offset_in
    b1 = _bb(covers["lc1"].solid)
    assert (b1.ymin, b1.ymax) == (
        pytest.approx(y_out_lc1, abs=1e-6),
        pytest.approx(y_out_lc1 + cv.T_CORE, abs=1e-6),
    )
    assert (b1.zmin, b1.zmax) == (
        pytest.approx(cv.FITTED_FLOOR_Z, abs=1e-6),
        pytest.approx(cv.LC1_TOP_Z, abs=1e-6),
    )
    assert _comp(covers["lc1"].solid).Volume() == pytest.approx(
        (x1_lc1 - x0_lc1) * (cv.LC1_TOP_Z - cv.FITTED_FLOOR_Z) * cv.T_CORE, rel=1e-6
    )

    b2 = _bb(covers["lc2"].solid)
    b3 = _bb(covers["lc3"].solid)
    b4 = _bb(covers["lc4"].solid)
    lc2_x0, lc2_x1 = cv.lc2_span()
    assert b2.xmin == pytest.approx(lc2_x0, abs=1e-6)
    assert b2.xmax == pytest.approx(lc2_x1, abs=1e-6)
    assert b3.xmin == pytest.approx(lc2_x0, abs=1e-6)
    assert b4.xmin == pytest.approx(lc2_x0, abs=1e-6)

    # LC3 and LC4 stand on the floor up to LC1_TOP_Z; LC2 rests on top of them
    for b_side in (b3, b4):
        assert b_side.zmin == pytest.approx(cv.FITTED_FLOOR_Z, abs=1e-6)
        assert b_side.zmax == pytest.approx(cv.LC1_TOP_Z, abs=1e-6)
    assert b2.zmin == pytest.approx(cv.LC1_TOP_Z, abs=1e-6)
    assert b2.zmax == pytest.approx(cv.LC1_TOP_Z + cv.T_CORE, abs=1e-6)

    # Lateral placement: LC2 and LC3 start at wall_y(); LC4 starts at LC2's inboard edge
    y_wall = cv.wall_y()
    assert b2.ymin == pytest.approx(y_wall, abs=1e-6)
    assert b3.ymin == pytest.approx(y_wall, abs=1e-6)
    assert b3.ymax == pytest.approx(y_wall + cv.T_CORE, abs=1e-6)
    assert b4.ymin == pytest.approx(b2.ymax, abs=1e-6)
    assert b4.ymax == pytest.approx(b2.ymax + cv.T_CORE, abs=1e-6)


def test_lc2_lc3_lc5_lc6_exact_volumes_and_bounds(covers):
    cx, cy = cv.FITTED_LC2_THROTTLE_CUT
    expected_lc2_vol = (
        G.cov_book_lc2_len_in * G.cov_book_lc2_width_in - cx * cy
    ) * cv.T_CORE
    assert _comp(covers["lc2"].solid).Volume() == pytest.approx(
        expected_lc2_vol, rel=1e-6
    )

    along_lc3 = G.cov_book_lc3_in[0]
    step_lc3 = G.cov_book_lc3_step_in
    h_console = cv.LC1_TOP_Z - cv.FITTED_FLOOR_Z
    expected_lc3_vol = (
        0.5 * (along_lc3 + (along_lc3 - step_lc3)) * h_console * cv.T_CORE
    )
    assert _comp(covers["lc3"].solid).Volume() == pytest.approx(
        expected_lc3_vol, rel=1e-6
    )

    len_lc5, wid_lc5 = G.cov_book_lc5_in
    b5 = _bb(covers["lc5"].solid)
    x5 = cv.lc5_x0()
    y5 = cv.wall_y(x5, x5 + len_lc5)
    assert (b5.xmin, b5.xmax) == (
        pytest.approx(x5, abs=1e-6),
        pytest.approx(x5 + len_lc5, abs=1e-6),
    )
    assert (b5.ymin, b5.ymax) == (
        pytest.approx(y5, abs=1e-6),
        pytest.approx(y5 + wid_lc5, abs=1e-6),
    )
    assert (b5.zmin, b5.zmax) == (
        pytest.approx(cv.LC1_TOP_Z, abs=1e-6),
        pytest.approx(cv.LC1_TOP_Z + cv.T_CORE, abs=1e-6),
    )
    assert _comp(covers["lc5"].solid).Volume() == pytest.approx(
        len_lc5 * wid_lc5 * cv.T_CORE, rel=1e-6
    )

    depth_lc6 = G.cov_book_lc6_depth_in
    base_lc6 = depth_lc6 / math.tan(math.radians(50.0)) + depth_lc6 / math.tan(
        math.radians(45.0)
    )
    b6 = _bb(covers["lc6"].solid)
    y6 = cv.wall_y(x5, x5 + base_lc6)
    assert b6.xmin == pytest.approx(x5, abs=1e-6)
    assert (b6.ymin, b6.ymax) == (
        pytest.approx(y6, abs=1e-6),
        pytest.approx(y6 + cv.T_CORE, abs=1e-6),
    )
    assert (b6.zmin, b6.zmax) == (
        pytest.approx(cv.LC1_TOP_Z - depth_lc6, abs=1e-6),
        pytest.approx(cv.LC1_TOP_Z, abs=1e-6),
    )
    assert _comp(covers["lc6"].solid).Volume() == pytest.approx(
        0.5 * base_lc6 * depth_lc6 * cv.T_CORE, rel=1e-6
    )


def test_lc4_pitch_trim_hole_position_is_clear(covers):
    x0 = cv.lc2_span()[0]
    hx = x0 + cv.FITTED_LC4_HOLE_FS_FROM_FRONT
    hz = 0.5 * (cv.FITTED_FLOOR_Z + cv.LC1_TOP_Z)
    y1 = cv.wall_y() + G.cov_book_lc2_width_in
    r_probe = 0.45 * cv.FITTED_LC4_HOLE_DIA

    probe = (
        cq.Workplane("XZ")
        .center(hx, hz)
        .circle(r_probe)
        .extrude(-cv.T_CORE)
        .translate((0.0, y1, 0.0))
    )
    inter = _comp(covers["lc4"].solid).intersect(_comp(probe))
    assert not inter.Solids() or inter.Volume() < 1e-6


def test_thigh_x_and_floor_z_under_linear_slope():
    x0, x1 = cv.thigh_x()
    assert x0 == pytest.approx(G.fs_panel + 0.2 + cv.FITTED_PANEL_CLEAR, abs=1e-9)
    assert x1 - x0 == pytest.approx(G.cov_book_thigh_floor_in[1], abs=1e-9)

    rib_h = G.cov_book_thigh_rib_in[1]
    z_front = cv._floor_z_under(x0)
    z_aft = cv._floor_z_under(x1)
    assert z_front == pytest.approx(
        cv.FITTED_FLOOR_Z + rib_h + cv.FITTED_RIB_CLEAR, abs=1e-9
    )
    assert z_aft == pytest.approx(cv.FITTED_FLOOR_Z + cv.FITTED_RIB_CLEAR, abs=1e-9)
    assert z_front - z_aft == pytest.approx(rib_h, abs=1e-9)

    xm = 0.5 * (x0 + x1)
    assert cv._floor_z_under(xm) == pytest.approx(0.5 * (z_front + z_aft), abs=1e-9)
    assert z_front > cv._floor_z_under(xm) > z_aft


def test_thigh_ribs_arch_volume_and_valve_cover_lap(covers):
    ra = _bb(covers["thigh_rib_a"].solid)
    rb = _bb(covers["thigh_rib_b"].solid)
    spacing = G.cov_book_thigh_rib_spacing_in
    assert (ra.ymin, ra.ymax) == (
        pytest.approx(-spacing / 2 - cv.T_CORE / 2, abs=1e-6),
        pytest.approx(-spacing / 2 + cv.T_CORE / 2, abs=1e-6),
    )
    assert (rb.ymin, rb.ymax) == (
        pytest.approx(spacing / 2 - cv.T_CORE / 2, abs=1e-6),
        pytest.approx(spacing / 2 + cv.T_CORE / 2, abs=1e-6),
    )

    x0, _ = cv.thigh_x()
    ln, _ = G.cov_book_thigh_rib_in
    h0 = cv._floor_z_under(x0) - cv.FITTED_FLOOR_Z
    h1 = cv._floor_z_under(x0 + ln) - cv.FITTED_FLOOR_Z
    vol_b = _comp(covers["thigh_rib_b"].solid).Volume()
    vol_a = _comp(covers["thigh_rib_a"].solid).Volume()
    assert vol_b == pytest.approx(0.5 * (h0 + h1) * ln * cv.T_CORE, rel=1e-6)
    arch_half_cyl = 0.5 * math.pi * cv.FITTED_RIB_ARCH_R**2 * cv.T_CORE
    assert vol_b - vol_a == pytest.approx(arch_half_cyl, rel=1e-3)

    # Valve cover laps the floor notch equally on both sides in x and y
    cw, cl, _ct = G.cov_book_valve_cover_in
    nw, nd = G.cov_book_thigh_notch_in
    _, x_aft = cv.thigh_x()
    vb = _bb(covers["valve_cover"].solid)
    assert (vb.ymin, vb.ymax) == (
        pytest.approx(-cw / 2, abs=1e-6),
        pytest.approx(cw / 2, abs=1e-6),
    )
    lap_x = 0.5 * (cl - nd)
    assert vb.xmin == pytest.approx(x_aft - nd - lap_x, abs=1e-6)
    assert vb.xmax == pytest.approx(x_aft + lap_x, abs=1e-6)
    assert (vb.ymax - vb.ymin) - nw == pytest.approx(cw - nw, abs=1e-6)


def test_aft_cover_caching_bounds_and_exact_volume():
    assert cv.aft_cover() is cv.aft_cover()

    ac = _comp(cv.aft_cover())
    b = ac.BoundingBox()
    ln, wd, th = G.cov_book_aft_cover_block_in
    x0 = cv.FITTED_AFT_COVER_FWD
    x1 = x0 + ln - 0.4
    z1 = cv.FITTED_AFT_COVER_TOP_Z
    z0 = z1 - th
    assert (b.xmin, b.xmax) == (
        pytest.approx(x0, abs=1e-6),
        pytest.approx(x1, abs=1e-6),
    )
    assert (b.ymin, b.ymax) == (
        pytest.approx(-wd / 2, abs=1e-6),
        pytest.approx(wd / 2, abs=1e-6),
    )
    assert (b.zmin, b.zmax) == (
        pytest.approx(z0, abs=1e-6),
        pytest.approx(z1, abs=1e-6),
    )
    assert ac.Center().y == pytest.approx(0.0, abs=1e-6)

    d = G.cov_book_aft_cover_dish_in
    sb = _comp(lg.build_gear()["strut"].solid).BoundingBox()
    s0 = sb.xmin - cv.FITTED_STRUT_CLEAR
    s1 = sb.xmax + cv.FITTED_STRUT_CLEAR
    vol_block = (x1 - x0) * wd * th
    vol_dish = (x1 - x0 - 2 * d) * (wd - 2 * d) * cv.FITTED_DISH_DEPTH
    slot_x = max(0.0, min(x1, s1) - max(x0, s0))
    dish_slot_x = max(0.0, min(x1 - d, s1) - max(x0 + d, s0))
    vol_slot_net = slot_x * wd * th - dish_slot_x * (wd - 2 * d) * cv.FITTED_DISH_DEPTH
    assert ac.Volume() == pytest.approx(vol_block - vol_dish - vol_slot_net, rel=1e-5)


def test_canard_cover_exact_bounds_symmetry_and_volume(covers):
    assert cv.FITTED_CANARD_TOP_Z == pytest.approx(2.4, abs=1e-9)
    assert cv.FITTED_CANARD_BLOCK_X == (
        pytest.approx(22.3, abs=1e-9),
        pytest.approx(27.5, abs=1e-9),
    )
    assert cv.FITTED_CANARD_BLOCK_HALF_W == pytest.approx(10.0, abs=1e-9)

    cc = _comp(covers["canard_cover"].solid)
    b = cc.BoundingBox()
    x0, x1 = cv.FITTED_CANARD_BLOCK_X
    hw = cv.FITTED_CANARD_BLOCK_HALF_W
    z0 = cv.FITTED_CANARD_TOP_Z + 0.05
    th = G.cov_book_canard_cover_foam_in

    assert (b.xmin, b.xmax) == (
        pytest.approx(x0, abs=1e-6),
        pytest.approx(x1, abs=1e-6),
    )
    assert (b.ymin, b.ymax) == (
        pytest.approx(-hw, abs=1e-6),
        pytest.approx(hw, abs=1e-6),
    )
    assert b.zmin == pytest.approx(cv.FITTED_CANARD_TOP_Z, abs=0.06)
    assert (b.zmin, b.zmax) == (
        pytest.approx(z0, abs=1e-6),
        pytest.approx(z0 + th, abs=1e-6),
    )
    assert (b.zmin, b.zmax) == (
        pytest.approx(2.45, abs=1e-6),
        pytest.approx(2.45 + th, abs=1e-6),
    )
    assert cc.Center().y == pytest.approx(0.0, abs=1e-6)
    assert cc.Volume() == pytest.approx((x1 - x0) * (2.0 * hw) * th, rel=1e-6)


def test_gap_seals_placement_centroid_and_mirror_symmetry(covers):
    sr = _comp(covers["seal_right"].solid)
    sl = _comp(covers["seal_left"].solid)
    br, bl = sr.BoundingBox(), sl.BoundingBox()

    xa, xb = cv.FITTED_SEAL_X
    z0, z1 = cv.FITTED_SEAL_Z
    root_y = G.wing_root_bl + cv.FITTED_SEAL_Y_OFF
    gap = G.cov_book_seal_gap_in
    front = G.cov_book_seal_front_gap_in

    for b in (br, bl):
        assert (b.xmin, b.xmax) == (
            pytest.approx(xa, abs=1e-6),
            pytest.approx(xb, abs=1e-6),
        )
        assert (b.zmin, b.zmax) == (
            pytest.approx(z0, abs=1e-6),
            pytest.approx(z1, abs=1e-6),
        )
    assert (br.ymin, br.ymax) == (
        pytest.approx(root_y, abs=1e-6),
        pytest.approx(root_y + gap, abs=1e-6),
    )
    assert (bl.ymin, bl.ymax) == (
        pytest.approx(-(root_y + gap), abs=1e-6),
        pytest.approx(-root_y, abs=1e-6),
    )

    assert sr.Volume() == pytest.approx(sl.Volume(), rel=1e-6)
    cr, cl = sr.Center(), sl.Center()
    assert cr.x == pytest.approx(cl.x, abs=1e-6)
    assert cr.y == pytest.approx(-cl.y, abs=1e-6)
    assert cr.z == pytest.approx(cl.z, abs=1e-6)

    # Trapezoid wedge is wider at xb (aft) than at xa (front), shifting centroid aft of midpoint
    expected_cx = xa + (xb - xa) * (front + 2.0 * gap) / (3.0 * (front + gap))
    assert cr.x == pytest.approx(expected_cx, abs=1e-4)
    assert cr.x > 0.5 * (xa + xb)


def test_finish_rows_order_stage_colours_and_fresh_copies():
    expected_surfaces = (
        ("wing.skins", "skin_top", "wing_upper"),
        ("wing.skins", "skin_bottom", "wing_lower"),
        ("canard.skin_top", None, "canard_upper"),
        ("canard.skin_bottom", None, "canard_lower"),
        ("cover.canard", None, "canard_upper"),
        ("fuselage.skin_right", None, "fuselage"),
        ("fuselage.skin_left", None, "fuselage"),
        ("fuselage.bottom", None, "fuselage"),
        ("nose.skin", None, "fuselage"),
        ("strake.skins", None, "fuselage"),
        ("winglet.skins", None, "winglet"),
        ("engine.cowl", None, "cowl"),
        ("cover.aft", None, "fuselage"),
    )
    assert ("cover.canard", None, "canard_upper") in cv.FINISH_SURFACES
    assert cv.FINISH_SURFACES == expected_surfaces

    rows = cv.finish_rows()
    assert len(rows) == len(cv.FINISH_SURFACES) == 13
    assert [(r["component"], r["match"], r["surface"]) for r in rows] == list(
        expected_surfaces
    )

    by_comp_match = {(r["component"], r["match"]): r for r in rows}
    canard_cover_row = by_comp_match[("cover.canard", None)]
    assert canard_cover_row["surface"] == "canard_upper"
    assert canard_cover_row["final_colour"] == cv.WHITE
    assert canard_cover_row["stages"][-1]["colour"] == cv.WHITE

    aft_cover_row = by_comp_match[("cover.aft", None)]
    assert aft_cover_row["surface"] == "fuselage"
    assert aft_cover_row["final_colour"] == cv.PRIMER_GREY

    white_targets = {
        ("wing.skins", "skin_top"),
        ("canard.skin_top", None),
        ("cover.canard", None),
    }
    assert {
        (r["component"], r["match"]) for r in rows if r["final_colour"] == cv.WHITE
    } == white_targets
    assert {
        r["final_colour"]
        for r in rows
        if (r["component"], r["match"]) not in white_targets
    } == {cv.PRIMER_GREY}

    for r in rows:
        fill, primer, paint = r["stages"]
        assert fill["colour"] == cv.PRIMER_GREY
        assert primer["colour"] == cv.PRIMER_GREY
        assert paint["colour"] == r["final_colour"]

    # Mutating a returned row does not corrupt config or subsequent calls
    rows[0]["stages"][0]["thickness_in"].append(99.0)
    fresh = cv.finish_rows()
    assert fresh[0]["stages"][0]["thickness_in"] == list(G.fin_book_fill_in)


def test_build_covers_partition_and_metadata_invariants(covers):
    assert cv.WORKSHOP_PARTS == frozenset()
    all_grouped = [name for group in cv.COMPONENT_PARTS.values() for name in group]
    assert len(all_grouped) == len(set(all_grouped)) == len(covers) == 14
    assert set(all_grouped) == set(covers)

    for key, part in covers.items():
        assert part.name == key
        assert part.void is False
        assert isinstance(part.cite, tuple) and len(part.cite) >= 1
