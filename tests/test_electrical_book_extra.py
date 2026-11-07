"""Additional unit and geometry coverage for ``core.electrical_book`` (plans chapter 22)."""

from __future__ import annotations

import ast
import math
from pathlib import Path

import cadquery as cq
import pytest

from config import config
from config.aircraft_config import GEOMETRY_PROVENANCE
from core import electrical_book as eb
from core.fuselage_book import FusePart, z_of_wl

G = config.geometry
REPO = Path(__file__).resolve().parents[1]


def _comp(wp: cq.Workplane) -> cq.Compound:
    return cq.Compound.makeCompound(wp.vals())


def _bb(wp: cq.Workplane):
    return _comp(wp).BoundingBox()


@pytest.fixture(scope="module")
def parts() -> dict[str, FusePart]:
    return eb.build_electrical()


def test_module_fitted_constants_and_partition_sets_pinned():
    assert (
        eb._P149,
        eb._P150,
        eb._P151,
        eb._P152,
        eb._P153,
        eb._P154,
        eb._P155,
    ) == (
        "plans-1980:p149",
        "plans-1980:p150",
        "plans-1980:p151",
        "plans-1980:p152",
        "plans-1980:p153",
        "plans-1980:p154",
        "plans-1980:p155",
    )
    assert eb.FITTED_BATTERY_IN == (7.0, 4.2, 4.4)
    assert eb.FITTED_BATTERY_Y0 == 2.4
    assert eb.FITTED_FLOOR_TOP_WL == 2.5
    assert eb.FITTED_COVER_GAP == 0.1
    assert eb.FITTED_COVER_T == 0.11
    assert eb.FITTED_STRAP_W == 0.5
    assert eb.FITTED_STRAP_T == 0.03
    assert eb.FITTED_STRAP_X == 2.0
    assert eb.FITTED_RELAY_IN == (1.7, 1.5, 1.5)
    assert eb.FITTED_RELAY_Y == ((3.0, 4.5), (5.0, 6.5))
    assert eb.FITTED_RELAY_WL == 5.9
    assert eb.FITTED_CABLE_R == 0.15
    assert eb.FITTED_BUNDLE_R == 0.3
    assert eb.FITTED_RUN_R == 0.15
    assert eb.FITTED_BUNDLE_WL == 14.4
    assert eb.FITTED_BUNDLE_BL == 9.6
    assert eb.FITTED_BUNDLE_DOWN_WL == 4.4
    assert eb.FITTED_BUNDLE_STAND == 0.35
    assert eb.FITTED_LIGHT_IN == (2.4, 1.6, 1.0)
    assert eb.FITTED_LIGHT_GAP == 0.05
    assert eb.FITTED_LIGHT_WL == 18.0
    assert eb.FITTED_STROBE_IN == (4.0, 3.0, 2.0)
    assert eb.FITTED_STROBE_Y == -10.8
    assert eb.FITTED_STROBE_WL == 9.4
    assert eb.FITTED_STROBE_GAP == 0.3
    assert eb.FITTED_NAV_W == 0.5
    assert eb.FITTED_NAV_T == 0.02
    assert eb.FITTED_NAV_BL0 == 13.0
    assert eb.FITTED_NAV_X_FRAC == 0.4
    assert eb.FITTED_NAV_DROP == 0.25
    assert eb.FITTED_COMM_W == 0.5
    assert eb.FITTED_COMM_T == 0.02
    assert eb.FITTED_COMM_BELOW_TE == 1.0
    assert eb.FITTED_COMM_GAP == 0.125
    assert eb.FITTED_COMM_WL0 == 30.0
    assert eb.FITTED_WIRE_END_GAP == 0.2

    assert eb.POCKET_PARTS == frozenset(
        {
            "shelf",
            "battery",
            "cover",
            "strap",
            "start_relay",
            "overvoltage_unit",
            "battery_cable",
        }
    )
    assert eb.POCKET_FOAM == frozenset(
        {"side_blocks", "floor_blocks", "top_block", "skin"}
    )
    assert eb.PASS_THROUGH == {
        "firewall_cable": frozenset({"front_seat_bkhd", "rear_seat_bkhd", "panel"})
    }
    assert eb.IN_FOAM_PARTS == frozenset({"comm_strips"})
    assert eb.WORKSHOP_PARTS == frozenset()
    assert eb.FIDELITIES_USED == frozenset({"representational"})
    assert eb.POCKET_PARTS.isdisjoint(eb.IN_FOAM_PARTS)
    assert eb.POCKET_PARTS.isdisjoint(eb.PASS_THROUGH)
    assert eb.IN_FOAM_PARTS.isdisjoint(eb.PASS_THROUGH)


def test_config_elec_book_fields_and_provenance_flags():
    assert G.elec_book_battery_v == 12.0
    assert G.elec_book_battery_ah == 25.0
    assert G.elec_book_battery_fs_range == (0.0, 22.0)
    assert G.elec_book_battery_model_fs == 11.0
    assert G.elec_book_battery_added_lb == 19.0
    assert G.elec_book_shelf_in == (0.6, 0.4)
    assert G.elec_book_starter_fs_min == 150.0
    assert G.elec_book_relay_fs == 22.0
    assert G.elec_book_nav_strip_in == 22.8
    assert G.elec_book_comm_strip_in == 20.3

    expected_prov = {
        "elec_book_battery_v": ("book", "plans-1980:p150", "high"),
        "elec_book_battery_ah": ("book", "plans-1980:p150", "high"),
        "elec_book_battery_fs_range": (
            "positioned-from-text",
            "plans-1980:p155",
            "low",
        ),
        "elec_book_battery_model_fs": ("unsourced", "", "low"),
        "elec_book_battery_added_lb": ("derived", "cp-text:p27", "medium"),
        "elec_book_shelf_in": ("book", "plans-1980:p155", "medium"),
        "elec_book_starter_fs_min": ("positioned-from-text", "cp-text:p27", "low"),
        "elec_book_relay_fs": ("positioned-from-text", "plans-1980:p149", "low"),
        "elec_book_nav_strip_in": ("cp-corrected", "cp-text:p30", "high"),
        "elec_book_comm_strip_in": ("cp-corrected", "cp-text:p26", "high"),
    }
    for key, (status, source, confidence) in expected_prov.items():
        entry = GEOMETRY_PROVENANCE[key]
        assert (entry["status"], entry["source"], entry["confidence"]) == (
            status,
            source,
            confidence,
        ), key

    tree = ast.parse((REPO / "core" / "electrical_book.py").read_text())
    float_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, float)
    }
    printed_config_floats = {12.0, 25.0, 11.0, 19.0, 0.6, 150.0, 22.0, 22.8, 20.3}
    assert not (float_literals & printed_config_floats)


def test_primitive_helpers_box_solid_compound_and_tube():
    box = eb._box(-2.0, 3.0, 1.5, 5.5, -4.0, -1.0)
    b_bb = box.BoundingBox()
    assert (
        b_bb.xmin,
        b_bb.xmax,
        b_bb.ymin,
        b_bb.ymax,
        b_bb.zmin,
        b_bb.zmax,
    ) == pytest.approx((-2.0, 3.0, 1.5, 5.5, -4.0, -1.0), rel=1e-6)
    assert box.Volume() == pytest.approx(60.0, rel=1e-6)

    wp_single = eb._solid(box)
    assert isinstance(wp_single, cq.Workplane)
    assert _comp(wp_single).Volume() == pytest.approx(60.0, rel=1e-6)

    box2 = eb._box(10.0, 12.0, -3.0, -1.0, 0.0, 4.0)
    wp_comp = eb._compound([box, box2])
    solids = wp_comp.vals()[0].Solids()
    assert len(solids) == 2
    assert sum(s.Volume() for s in solids) == pytest.approx(60.0 + 16.0, rel=1e-6)

    # 2-point tube: no interior joints (points[1:-1] is empty -> 1 cylinder, 0 spheres)
    tube_2 = eb._tube([(1.0, -2.0, 3.0), (1.0, -2.0, 8.0)], 0.5)
    t2_solids = tube_2.vals()[0].Solids()
    assert len(t2_solids) == 1
    assert t2_solids[0].Volume() == pytest.approx(math.pi * 0.5**2 * 5.0, rel=1e-6)
    t2_bb = _bb(tube_2)
    assert (
        t2_bb.xmin,
        t2_bb.xmax,
        t2_bb.ymin,
        t2_bb.ymax,
        t2_bb.zmin,
        t2_bb.zmax,
    ) == pytest.approx((0.5, 1.5, -2.5, -1.5, 3.0, 8.0), rel=1e-6)

    # 3-point tube: 1 interior joint -> 2 cylinders + 1 sphere = 3 solids
    tube_3 = eb._tube([(0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (4.0, 3.0, 0.0)], 0.25)
    t3_solids = tube_3.vals()[0].Solids()
    assert len(t3_solids) == 3
    vols = sorted(s.Volume() for s in t3_solids)
    assert vols == pytest.approx(
        [
            (4.0 / 3.0) * math.pi * 0.25**3,
            math.pi * 0.25**2 * 3.0,
            math.pi * 0.25**2 * 4.0,
        ],
        rel=1e-6,
    )


def test_bar_helper_orientation_normalization_and_positive_volume():
    bar_pos = eb._bar((10.0, 2.0, -3.0), (10.0, 7.0, -3.0), (1.0, 0.0, 0.0), 0.5, 0.04)
    bar_neg = eb._bar(
        (10.0, -2.0, -3.0), (10.0, -7.0, -3.0), (1.0, 0.0, 0.0), 0.5, 0.04
    )
    assert bar_pos.isValid() and bar_neg.isValid()
    assert bar_pos.Volume() == pytest.approx(0.1, rel=1e-6)
    assert bar_neg.Volume() == pytest.approx(0.1, rel=1e-6)

    bp_bb = bar_pos.BoundingBox()
    bn_bb = bar_neg.BoundingBox()
    assert (
        bp_bb.xmin,
        bp_bb.xmax,
        bp_bb.ymin,
        bp_bb.ymax,
        bp_bb.zmin,
        bp_bb.zmax,
    ) == pytest.approx((9.75, 10.25, 2.0, 7.0, -3.02, -2.98), rel=1e-6)
    assert (
        bn_bb.xmin,
        bn_bb.xmax,
        bn_bb.ymin,
        bn_bb.ymax,
        bn_bb.zmin,
        bn_bb.zmax,
    ) == pytest.approx((9.75, 10.25, -7.0, -2.0, -3.02, -2.98), rel=1e-6)

    # Non-unit width_dir vector is normalized inside _bar
    bar_scaled = eb._bar((0.0, 0.0, 0.0), (0.0, 0.0, 10.0), (3.5, 0.0, 0.0), 0.6, 0.02)
    bs_bb = bar_scaled.BoundingBox()
    assert (
        bs_bb.xmin,
        bs_bb.xmax,
        bs_bb.ymin,
        bs_bb.ymax,
        bs_bb.zmin,
        bs_bb.zmax,
    ) == pytest.approx((-0.3, 0.3, -0.01, 0.01, 0.0, 10.0), abs=1e-5)
    assert bar_scaled.Volume() == pytest.approx(0.12, rel=1e-6)


def test_battery_box_and_shelf_exact_coordinates_and_volumes(parts):
    # x0 = 11.0 - 7.0/2 = 7.5, x1 = 14.5; y0 = 2.4, y1 = 6.6; z0 = (2.5 - 17.4) + 0.6 = -14.3, z1 = -9.9
    assert eb._battery_box() == pytest.approx(
        (7.5, 14.5, 2.4, 6.6, -14.3, -9.9), rel=1e-6
    )

    bat_bb = _bb(parts["battery"].solid)
    assert (
        bat_bb.xmin,
        bat_bb.xmax,
        bat_bb.ymin,
        bat_bb.ymax,
        bat_bb.zmin,
        bat_bb.zmax,
    ) == pytest.approx((7.5, 14.5, 2.4, 6.6, -14.3, -9.9), rel=1e-6)
    assert _comp(parts["battery"].solid).Volume() == pytest.approx(129.36, rel=1e-6)

    # shelf: 0.3 in margin around battery in X and Y, 0.6 in pad below z0
    sh_bb = _bb(parts["shelf"].solid)
    assert (
        sh_bb.xmin,
        sh_bb.xmax,
        sh_bb.ymin,
        sh_bb.ymax,
        sh_bb.zmin,
        sh_bb.zmax,
    ) == pytest.approx((7.2, 14.8, 2.1, 6.9, -14.9, -14.3), rel=1e-6)
    assert _comp(parts["shelf"].solid).Volume() == pytest.approx(21.888, rel=1e-6)


def test_cover_and_strap_shell_geometry_and_exact_volumes(parts, monkeypatch):
    x0, x1, y0, y1, z0, z1 = eb._battery_box()
    g_c, t_c = eb.FITTED_COVER_GAP, eb.FITTED_COVER_T
    g_s, t_s = eb.FITTED_COVER_GAP + eb.FITTED_COVER_T, eb.FITTED_STRAP_T
    xa = x0 + eb.FITTED_STRAP_X

    # cover: g = 0.1, t = 0.11 -> g + t = 0.21
    # outer: 7.42 * 4.62 * 4.61 = 158.032644; inner cut inside outer: 7.2 * 4.4 * 4.5 = 142.56
    cov_bb = _bb(parts["cover"].solid)
    assert (
        cov_bb.xmin,
        cov_bb.xmax,
        cov_bb.ymin,
        cov_bb.ymax,
        cov_bb.zmin,
        cov_bb.zmax,
    ) == pytest.approx(
        (
            x0 - g_c - t_c,
            x1 + g_c + t_c,
            y0 - g_c - t_c,
            y1 + g_c + t_c,
            z0,
            z1 + g_c + t_c,
        ),
        rel=1e-6,
    )
    cov_outer_vol = (
        (x1 - x0 + 2 * (g_c + t_c))
        * (y1 - y0 + 2 * (g_c + t_c))
        * (z1 - z0 + g_c + t_c)
    )
    cov_carved_vol = (x1 - x0 + 2 * g_c) * (y1 - y0 + 2 * g_c) * (z1 - z0 + g_c)
    assert _comp(parts["cover"].solid).Volume() == pytest.approx(
        cov_outer_vol - cov_carved_vol, rel=1e-6
    )

    # strap: xa = 7.5 + 2.0 = 9.5 to 10.0 (forward of battery midpoint 11.0); g = 0.21, t = 0.03
    # volume = 0.5 * (4.68 * 4.64 - 4.62 * 4.61) = 0.2085
    st_bb = _bb(parts["strap"].solid)
    assert (
        st_bb.xmin,
        st_bb.xmax,
        st_bb.ymin,
        st_bb.ymax,
        st_bb.zmin,
        st_bb.zmax,
    ) == pytest.approx(
        (
            xa,
            xa + eb.FITTED_STRAP_W,
            y0 - g_s - t_s,
            y1 + g_s + t_s,
            z0,
            z1 + g_s + t_s,
        ),
        rel=1e-6,
    )
    st_outer_vol = (
        eb.FITTED_STRAP_W * (y1 - y0 + 2 * (g_s + t_s)) * (z1 - z0 + g_s + t_s)
    )
    st_carved_vol = eb.FITTED_STRAP_W * (y1 - y0 + 2 * g_s) * (z1 - z0 + g_s)
    assert _comp(parts["strap"].solid).Volume() == pytest.approx(
        st_outer_vol - st_carved_vol, rel=1e-6
    )

    # B-Rep pocket z-levels on the cut strap solid: feet at z0, inner pocket roof at z1 + g_s, outer top at z1 + g_s + t_s
    strap_z_levels = sorted(
        {round(v.Z, 6) for v in _comp(parts["strap"].solid).Vertices()}
    )
    assert strap_z_levels == pytest.approx([z0, z1 + g_s, z1 + g_s + t_s], rel=1e-6)
    assert strap_z_levels[1] - strap_z_levels[0] == pytest.approx(
        (z1 + g_s) - z0, rel=1e-6
    )

    # Pin the inner pocket cutter boxes (z0 - 1.0 to z1 + g) constructed inside cover() and strap()
    box_calls = []
    orig_box = eb._box

    def spy_box(bx0, bx1, by0, by1, bz0, bz1):
        solid = orig_box(bx0, bx1, by0, by1, bz0, bz1)
        box_calls.append(((bx0, bx1, by0, by1, bz0, bz1), solid))
        return solid

    monkeypatch.setattr(eb, "_box", spy_box)
    eb.cover()
    eb.strap()
    assert len(box_calls) == 4
    cov_inner_args, cov_inner_solid = box_calls[1]
    st_inner_args, st_inner_solid = box_calls[3]

    assert cov_inner_args == pytest.approx(
        (x0 - g_c, x1 + g_c, y0 - g_c, y1 + g_c, z0 - 1.0, z1 + g_c), rel=1e-6
    )
    cov_inner_bb = cov_inner_solid.BoundingBox()
    assert (cov_inner_bb.zmin, cov_inner_bb.zmax) == pytest.approx(
        (z0 - 1.0, z1 + g_c), rel=1e-6
    )
    assert cov_inner_bb.zmax - cov_inner_bb.zmin == pytest.approx(
        (z1 + g_c) - (z0 - 1.0), rel=1e-6
    )

    assert st_inner_args == pytest.approx(
        (
            xa - 1.0,
            xa + eb.FITTED_STRAP_W + 1.0,
            y0 - g_s,
            y1 + g_s,
            z0 - 1.0,
            z1 + g_s,
        ),
        rel=1e-6,
    )
    st_inner_bb = st_inner_solid.BoundingBox()
    assert (st_inner_bb.zmin, st_inner_bb.zmax) == pytest.approx(
        (z0 - 1.0, z1 + g_s), rel=1e-6
    )
    assert st_inner_bb.zmax - st_inner_bb.zmin == pytest.approx(
        (z1 + g_s) - (z0 - 1.0), rel=1e-6
    )


def test_relays_and_relay_helper_exact_placement_and_volumes(parts):
    # xf = 22.0, length = 1.7 -> [20.3, 22.0]; z0 = 5.9 - 17.4 = -11.5 -> [-11.5, -10.0]
    sr_bb = _bb(parts["start_relay"].solid)
    ov_bb = _bb(parts["overvoltage_unit"].solid)
    assert (
        sr_bb.xmin,
        sr_bb.xmax,
        sr_bb.ymin,
        sr_bb.ymax,
        sr_bb.zmin,
        sr_bb.zmax,
    ) == pytest.approx((20.3, 22.0, 3.0, 4.5, -11.5, -10.0), rel=1e-6)
    assert (
        ov_bb.xmin,
        ov_bb.xmax,
        ov_bb.ymin,
        ov_bb.ymax,
        ov_bb.zmin,
        ov_bb.zmax,
    ) == pytest.approx((20.3, 22.0, 5.0, 6.5, -11.5, -10.0), rel=1e-6)
    assert ov_bb.ymin - sr_bb.ymax == pytest.approx(0.5, rel=1e-6)
    assert _comp(parts["start_relay"].solid).Volume() == pytest.approx(3.825, rel=1e-6)
    assert _comp(parts["overvoltage_unit"].solid).Volume() == pytest.approx(
        3.825, rel=1e-6
    )

    custom_relay = eb._relay(-4.0, -1.5)
    cr_bb = custom_relay.BoundingBox()
    assert (cr_bb.ymin, cr_bb.ymax) == pytest.approx((-4.0, -1.5), rel=1e-6)
    assert custom_relay.Volume() == pytest.approx(6.375, rel=1e-6)


def test_wire_runs_exact_endpoints_radii_and_volumes(parts, monkeypatch):
    _x0, x1, y0, y1, _z0, _z1 = eb._battery_box()
    yb = (y0 + y1) / 2
    yr = sum(eb.FITTED_RELAY_Y[0]) / 2
    zr = z_of_wl(eb.FITTED_RELAY_WL) + eb.FITTED_RELAY_IN[2] / 2
    xr = G.fs_f22 - eb.FITTED_RELAY_IN[0]
    x_start = x1 + eb.FITTED_COVER_GAP + eb.FITTED_COVER_T + 0.05
    x_end = xr - 0.1
    dx = x_end - x_start
    dy = yr - yb
    bc_len = math.hypot(dx, dy)

    # battery_cable: (14.76, 4.5, -10.75) to (20.2, 3.75, -10.75), r = 0.15, L = hypot(5.44, -0.75)
    bc_solids = parts["battery_cable"].solid.vals()[0].Solids()
    assert len(bc_solids) == 1
    assert bc_solids[0].Volume() == pytest.approx(
        math.pi * eb.FITTED_CABLE_R**2 * bc_len, rel=1e-6
    )
    cap_faces = sorted(bc_solids[0].Faces(), key=lambda f: f.Area())[:2]
    start_cap, end_cap = sorted(cap_faces, key=lambda f: f.Center().x)
    assert start_cap.Center().y == pytest.approx((y0 + y1) / 2, rel=1e-6)
    assert (
        start_cap.Center().x,
        start_cap.Center().y,
        start_cap.Center().z,
    ) == pytest.approx((x_start, (y0 + y1) / 2, zr), rel=1e-6)
    assert (
        end_cap.Center().x,
        end_cap.Center().y,
        end_cap.Center().z,
    ) == pytest.approx((x_end, yr, zr), rel=1e-6)

    bc_bb = _bb(parts["battery_cable"].solid)
    assert (bc_bb.zmin, bc_bb.zmax) == pytest.approx(
        (zr - eb.FITTED_CABLE_R, zr + eb.FITTED_CABLE_R), rel=1e-6
    )
    assert bc_bb.xmin == pytest.approx(
        x_start - eb.FITTED_CABLE_R * abs(dy) / bc_len, rel=1e-5
    )
    assert bc_bb.xmax == pytest.approx(
        x_end + eb.FITTED_CABLE_R * abs(dy) / bc_len, rel=1e-5
    )
    assert bc_bb.ymin == pytest.approx(
        yr - eb.FITTED_CABLE_R * abs(dx) / bc_len, rel=1e-5
    )
    assert bc_bb.ymax == pytest.approx(
        (y0 + y1) / 2 + eb.FITTED_CABLE_R * abs(dx) / bc_len, rel=1e-5
    )

    tube_calls = []
    orig_tube = eb._tube

    def spy_tube(points, r):
        tube_calls.append((list(points), r))
        return orig_tube(points, r)

    monkeypatch.setattr(eb, "_tube", spy_tube)
    eb.battery_cable()
    assert len(tube_calls) == 1
    bc_pts, bc_r = tube_calls[0]
    assert bc_r == pytest.approx(eb.FITTED_CABLE_R, rel=1e-6)
    assert bc_pts[0][1] == pytest.approx((y0 + y1) / 2, rel=1e-6)
    assert bc_pts == [
        pytest.approx((x_start, (y0 + y1) / 2, zr), rel=1e-6),
        pytest.approx((x_end, yr, zr), rel=1e-6),
    ]

    # panel_bundle: x = 39.4, (-9.6, -3.0) -> (9.6, -3.0) -> (9.6, -13.0), r = 0.3
    # Vertical leg drops on the RIGHT (+9.6), so ymin = -9.6 while ymax = 9.6 + 0.3 = 9.9
    pb_solids = parts["panel_bundle"].solid.vals()[0].Solids()
    assert len(pb_solids) == 3
    pb_bb = _bb(parts["panel_bundle"].solid)
    assert (
        pb_bb.xmin,
        pb_bb.xmax,
        pb_bb.ymin,
        pb_bb.ymax,
        pb_bb.zmin,
        pb_bb.zmax,
    ) == pytest.approx((39.1, 39.7, -9.6, 9.9, -13.0, -2.7), rel=1e-6)

    # firewall_cable: (39.4, 9.6, -13.0) to (124.8, 9.6, -13.0), r = 0.15, length = 85.4
    fw_x0 = G.fs_panel - eb.FITTED_BUNDLE_STAND
    fw_x1 = G.fs_firewall - eb.FITTED_WIRE_END_GAP
    fw_solids = parts["firewall_cable"].solid.vals()[0].Solids()
    assert len(fw_solids) == 1
    assert fw_solids[0].Volume() == pytest.approx(
        math.pi * eb.FITTED_RUN_R**2 * (fw_x1 - fw_x0), rel=1e-6
    )
    fw_bb = _bb(parts["firewall_cable"].solid)
    assert (
        fw_bb.xmin,
        fw_bb.xmax,
        fw_bb.ymin,
        fw_bb.ymax,
        fw_bb.zmin,
        fw_bb.zmax,
    ) == pytest.approx((39.4, 124.8, 9.45, 9.75, -13.15, -12.85), rel=1e-6)


def test_lights_and_strobe_supply_exact_boxes_and_mirror_symmetry(parts):
    # light_right: [156.0, 158.4] x [157.05, 158.65] x [0.6, 1.6]
    lr_bb = _bb(parts["light_right"].solid)
    ll_bb = _bb(parts["light_left"].solid)
    assert (
        lr_bb.xmin,
        lr_bb.xmax,
        lr_bb.ymin,
        lr_bb.ymax,
        lr_bb.zmin,
        lr_bb.zmax,
    ) == pytest.approx((156.0, 158.4, 157.05, 158.65, 0.6, 1.6), rel=1e-6)
    assert (
        ll_bb.xmin,
        ll_bb.xmax,
        ll_bb.ymin,
        ll_bb.ymax,
        ll_bb.zmin,
        ll_bb.zmax,
    ) == pytest.approx((156.0, 158.4, -158.65, -157.05, 0.6, 1.6), rel=1e-6)
    assert _comp(parts["light_right"].solid).Volume() == pytest.approx(3.84, rel=1e-6)
    assert _comp(parts["light_left"].solid).Volume() == pytest.approx(3.84, rel=1e-6)

    # strobe_supply: xa = 81.75 + 0.8 + 0.3 = 82.85 to 86.85; Y = [-10.8, -7.8]; Z = [-8.0, -6.0]
    st_bb = _bb(parts["strobe_supply"].solid)
    assert (
        st_bb.xmin,
        st_bb.xmax,
        st_bb.ymin,
        st_bb.ymax,
        st_bb.zmin,
        st_bb.zmax,
    ) == pytest.approx((82.85, 86.85, -10.8, -7.8, -8.0, -6.0), rel=1e-6)
    assert _comp(parts["strobe_supply"].solid).Volume() == pytest.approx(24.0, rel=1e-6)


def test_nav_strips_exact_placement_and_mirror_symmetry(parts):
    # x = 18.7 + 0.4 * 13.02 = 23.908 -> [23.658, 24.158]; z = 1.5 - 0.25 = 1.25 -> [1.24, 1.26]
    nr_bb = _bb(parts["nav_strip_right"].solid)
    nl_bb = _bb(parts["nav_strip_left"].solid)
    assert (
        nr_bb.xmin,
        nr_bb.xmax,
        nr_bb.ymin,
        nr_bb.ymax,
        nr_bb.zmin,
        nr_bb.zmax,
    ) == pytest.approx((23.658, 24.158, 13.0, 35.8, 1.24, 1.26), rel=1e-6)
    assert (
        nl_bb.xmin,
        nl_bb.xmax,
        nl_bb.ymin,
        nl_bb.ymax,
        nl_bb.zmin,
        nl_bb.zmax,
    ) == pytest.approx((23.658, 24.158, -35.8, -13.0, 1.24, 1.26), rel=1e-6)
    assert _comp(parts["nav_strip_right"].solid).Volume() == pytest.approx(
        0.228, rel=1e-6
    )
    assert _comp(parts["nav_strip_left"].solid).Volume() == pytest.approx(
        0.228, rel=1e-6
    )


def test_comm_strips_dual_foil_geometry_spacing_and_winglet_alignment(parts):
    from core import winglet_book as wl

    solids = parts["comm_strips"].solid.vals()[0].Solids()
    assert len(solids) == 2
    s_in, s_out = solids
    bb_in, bb_out = s_in.BoundingBox(), s_out.BoundingBox()

    length = G.elec_book_comm_strip_in
    wl0 = eb.FITTED_COMM_WL0
    dz = (
        length
        * (wl.TOP_WL - wl.ROOT_WL)
        / math.hypot(wl.TOP_WL - wl.ROOT_WL, wl.te_fs(wl.TOP_WL) - wl.te_fs(wl.ROOT_WL))
    )
    wl1 = wl0 + dz
    off_in = -(eb.FITTED_COMM_GAP + eb.FITTED_COMM_T) / 2
    x0 = wl.te_fs(wl0) - eb.FITTED_COMM_BELOW_TE
    x1 = wl.te_fs(wl1) - eb.FITTED_COMM_BELOW_TE
    y0_in = wl.y_centre(wl0) + off_in
    y1_in = wl.y_centre(wl1) + off_in
    z0_c = z_of_wl(wl0)
    z1_c = z_of_wl(wl1)
    dy_c = y1_in - y0_in
    dz_c = z1_c - z0_c
    hypot_yz = math.hypot(dy_c, dz_c)

    # Both strips sit inside the RIGHT winglet (+BL > 156), separated in Y by 0.125 + 0.02 = 0.145 in
    assert bb_in.ymin > 156.0 and bb_out.ymin > 156.0
    assert bb_out.ymin - bb_in.ymin == pytest.approx(
        eb.FITTED_COMM_GAP + eb.FITTED_COMM_T, rel=1e-6
    )
    assert bb_out.ymax - bb_in.ymax == pytest.approx(
        eb.FITTED_COMM_GAP + eb.FITTED_COMM_T, rel=1e-6
    )
    assert (
        bb_in.xmin,
        bb_in.xmax,
        bb_in.zmin,
        bb_in.zmax,
    ) == pytest.approx((bb_out.xmin, bb_out.xmax, bb_out.zmin, bb_out.zmax), rel=1e-6)
    assert (bb_in.xmin, bb_in.xmax) == pytest.approx(
        (x0 - eb.FITTED_COMM_W / 2, x1 + eb.FITTED_COMM_W / 2), rel=1e-6
    )
    assert (bb_in.zmin, bb_in.zmax) == pytest.approx(
        (
            z0_c - (eb.FITTED_COMM_T / 2) * (abs(dy_c) / hypot_yz),
            z1_c + (eb.FITTED_COMM_T / 2) * (abs(dy_c) / hypot_yz),
        ),
        rel=1e-6,
    )
    assert (bb_in.ymin, bb_in.ymax) == pytest.approx(
        (
            y1_in - (eb.FITTED_COMM_T / 2) * (dz_c / hypot_yz),
            y0_in + (eb.FITTED_COMM_T / 2) * (dz_c / hypot_yz),
        ),
        rel=1e-6,
    )
    assert z_of_wl(30.0) == pytest.approx(12.6, rel=1e-6)


def test_build_electrical_cache_identity_citations_and_fusepart_validation(parts):
    assert eb.build_electrical() is parts
    expected_cites = {
        "shelf": ("plans-1980:p155",),
        "battery": ("plans-1980:p150", "plans-1980:p151", "plans-1980:p155"),
        "cover": ("plans-1980:p155",),
        "strap": ("plans-1980:p155",),
        "start_relay": ("plans-1980:p149", "plans-1980:p152"),
        "overvoltage_unit": ("plans-1980:p149",),
        "battery_cable": ("plans-1980:p152",),
        "panel_bundle": ("plans-1980:p153",),
        "firewall_cable": ("plans-1980:p153",),
        "light_right": ("plans-1980:p151", "plans-1980:p155"),
        "light_left": ("plans-1980:p151", "plans-1980:p155"),
        "strobe_supply": ("plans-1980:p149", "plans-1980:p155"),
        "nav_strip_right": ("plans-1980:p152",),
        "nav_strip_left": ("plans-1980:p152",),
        "comm_strips": ("plans-1980:p152",),
    }
    assert {name: p.cite for name, p in parts.items()} == expected_cites
    assert all(p.void is False for p in parts.values())

    with pytest.raises(ValueError, match="fidelity"):
        FusePart(
            "bad_fidelity", parts["battery"].solid, "guessed", ("plans-1980:p150",)
        )
    with pytest.raises(ValueError, match="needs a citation"):
        FusePart("uncited_book", parts["battery"].solid, "book", ())
    with pytest.raises(ValueError, match="unknown source id"):
        FusePart(
            "bad_cite",
            parts["battery"].solid,
            "representational",
            ("nonexistent-doc:p1",),
        )
