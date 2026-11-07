"""Additional unit and geometry tests for ``core.controls_book``."""

from __future__ import annotations

import math

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from config import config
from core import controls_book as cb
from core.fuselage_book import WING_PLANE_WL, FusePart, z_of_wl

G = config.geometry


def wl_to_z(wl: float) -> float:
    """Independent derivation of model Z from W.L. via the wing-plane datum (W.L. 17.4)."""
    return wl - WING_PLANE_WL + G.wing_le_wl


def volume(shape: cq.Shape) -> float:
    """Compute exact B-Rep volume via OpenCASCADE global properties."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def vol_of(wp: cq.Workplane) -> float:
    """Sum volumes of all solids in a CadQuery Workplane."""
    return sum(volume(s) for s in wp.solids().vals())


def bbox_of(wp: cq.Workplane) -> cq.BoundBox:
    """Return the bounding box of all solids in a Workplane."""
    return cq.Compound.makeCompound(wp.vals()).BoundingBox(1e-5)


@pytest.fixture(scope="module")
def neutral_controls() -> dict[str, FusePart]:
    """Build the neutral controls dictionary once for the module."""
    return cb.build_controls()


def test_documented_constants_and_component_mapping_pinned() -> None:
    """Pin documented fitted and book constants and the component-parts map."""
    assert cb.FITTED_CONSOLE_LEAD == pytest.approx(1.0, rel=1e-6)
    assert cb.FITTED_CONSOLE_BELOW_TUBE == pytest.approx(1.5, rel=1e-6)
    assert cb.FITTED_GRIP_LEN == pytest.approx(3.0, rel=1e-6)
    assert cb.FITTED_GRIP_R == pytest.approx(0.4, rel=1e-6)
    assert cb.FITTED_CONDUIT_BL == pytest.approx(5.0, rel=1e-6)
    assert cb.FITTED_CONDUIT_R == pytest.approx(0.25, rel=1e-6)
    assert cb.FITTED_PTH_BL == pytest.approx(-9.5, rel=1e-6)
    assert cb.FITTED_PTH_PIN_R == pytest.approx(0.25, rel=1e-6)
    assert cb.FITTED_PTS_GAP == pytest.approx(1.0, rel=1e-6)
    assert cb.FITTED_PTS_R == pytest.approx(0.175, rel=1e-6)
    assert cb.FITTED_RT_X == (80.5, 82.0, 83.5)
    assert cb.FITTED_RT_TAB == (1.0, 2.0)
    assert cb.FITTED_RT1_H == pytest.approx(3.5, rel=1e-6)
    assert cb.FITTED_RTS_R == pytest.approx(0.15, rel=1e-6)
    assert cb.FITTED_RTS_Z == pytest.approx(3.0, rel=1e-6)

    assert cb._TUBE_BL == pytest.approx(6.2, rel=1e-6)
    assert cb._TUBE_WL == pytest.approx(12.3, rel=1e-6)
    assert cb._TUBE_OD == pytest.approx(0.75, rel=1e-6)
    assert cb._TUBE_WALL == pytest.approx(0.058, rel=1e-6)
    assert cb._STICK_R == pytest.approx(5.0 / 16.0, rel=1e-6)
    assert cb._WALL == pytest.approx(0.35, rel=1e-6)
    assert cb._PLANES == {"front": 45.5, "rear": 89.7}
    assert cb._STUB == {"front": 6.1, "rear": 4.1}

    assert G.trim_pth_leftmost_fs == pytest.approx(49.5, rel=1e-6)
    assert G.trim_spring_pts_in == (6.0, 9.0)
    assert G.trim_spring_rts_in == (2.0, 3.0)
    assert G.trim_sleeve_wl_in == (9.6, 8.3)

    assert cb.COMPONENT_PARTS == {
        "controls.consoles": ("front_console", "rear_console"),
        "controls.torque_tube": ("torque_tube",),
        "controls.sticks": ("front_stick", "rear_stick"),
        "controls.pitch_pushrod": ("pitch_pushrod",),
        "controls.rudder_conduit": ("rudder_conduit",),
        "trim.pitch_handle": ("pth", "pth_pivot", "pth_springs"),
        "trim.roll_trim": ("roll_trim", "roll_trim_springs"),
    }


def test_torque_tube_and_rudder_conduits_axes_bounds_and_volumes(
    neutral_controls: dict[str, FusePart],
) -> None:
    """Verify torque_tube_axis endpoints, hollow tube volume, and conduit stations."""
    a, b = cb.torque_tube_axis()
    expected_z = wl_to_z(12.3)  # 12.3 - 17.4 = -5.1
    assert z_of_wl(cb._TUBE_WL) == pytest.approx(expected_z, rel=1e-6)
    assert (a.x, a.y, a.z) == (
        pytest.approx(45.5, rel=1e-6),
        pytest.approx(6.2, rel=1e-6),
        pytest.approx(expected_z, rel=1e-6),
    )
    assert (b.x, b.y, b.z) == (
        pytest.approx(125.0, rel=1e-6),
        pytest.approx(6.2, rel=1e-6),
        pytest.approx(expected_z, rel=1e-6),
    )
    tube_len = 125.0 - 45.5
    assert b.x - a.x == pytest.approx(tube_len, rel=1e-6)

    tt = neutral_controls["torque_tube"].solid
    tt_bb = bbox_of(tt)
    r_out = 0.75 / 2.0
    r_in = r_out - 0.058
    assert (tt_bb.xmin, tt_bb.xmax) == (
        pytest.approx(45.5, rel=1e-6),
        pytest.approx(125.0, rel=1e-6),
    )
    assert (tt_bb.ymin, tt_bb.ymax) == (
        pytest.approx(6.2 - r_out, rel=1e-3),
        pytest.approx(6.2 + r_out, rel=1e-3),
    )
    assert (tt_bb.zmin, tt_bb.zmax) == (
        pytest.approx(expected_z - r_out, rel=1e-3),
        pytest.approx(expected_z + r_out, rel=1e-3),
    )
    expected_tt_vol = math.pi * (r_out**2 - r_in**2) * tube_len
    assert vol_of(tt) == pytest.approx(expected_tt_vol, rel=1e-4)

    conduits = cb.rudder_conduits().solids().vals()
    assert len(conduits) == 2
    by_y = sorted(conduits, key=lambda s: s.Center().y)
    left_bb, right_bb = by_y[0].BoundingBox(1e-5), by_y[1].BoundingBox(1e-5)
    conduit_z = wl_to_z(8.0)  # 8.0 - 17.4 = -9.4
    for c_bb, expected_y in ((left_bb, -5.0), (right_bb, 5.0)):
        assert (c_bb.xmin, c_bb.xmax) == (
            pytest.approx(125.0 - 82.0, rel=1e-6),
            pytest.approx(125.0, rel=1e-6),
        )
        assert (c_bb.ymin, c_bb.ymax) == (
            pytest.approx(expected_y - 0.25, rel=1e-3),
            pytest.approx(expected_y + 0.25, rel=1e-3),
        )
        assert (c_bb.zmin, c_bb.zmax) == (
            pytest.approx(conduit_z - 0.25, rel=1e-3),
            pytest.approx(conduit_z + 0.25, rel=1e-3),
        )
    expected_conduit_vol = math.pi * (0.25**2) * 82.0
    assert volume(by_y[0]) == pytest.approx(expected_conduit_vol, rel=1e-5)
    assert vol_of(neutral_controls["rudder_conduit"].solid) == pytest.approx(
        2.0 * expected_conduit_vol, rel=1e-5
    )


def test_stick_axis_input_validation_and_hand_computed_neutral_vectors() -> None:
    """Reject unknown stick names and pin code-derived neutral base and tip vectors."""
    for bad in ("", "left", "right", "center", "FRONT"):
        with pytest.raises(ValueError, match="unknown stick"):
            cb.stick_axis(bad)
        with pytest.raises(ValueError, match="unknown stick"):
            cb.stick(bad)

    a_rad = math.radians(5.0)
    b_rad = math.radians(5.0)
    ux = -math.sin(a_rad)
    uy = -math.cos(a_rad) * math.sin(b_rad)
    uz = math.cos(a_rad) * math.cos(b_rad)
    base_z = wl_to_z(12.3)

    f_len = 6.1 + 3.0
    f_base, f_tip = cb.stick_axis("front", 0.0, 0.0)
    assert (f_base.x, f_base.y, f_base.z) == (
        pytest.approx(45.5, rel=1e-6),
        pytest.approx(6.2, rel=1e-6),
        pytest.approx(base_z, rel=1e-6),
    )
    assert (f_tip.x, f_tip.y, f_tip.z) == (
        pytest.approx(45.5 + f_len * ux, rel=1e-6),
        pytest.approx(6.2 + f_len * uy, rel=1e-6),
        pytest.approx(base_z + f_len * uz, rel=1e-6),
    )
    assert (f_tip - f_base).Length == pytest.approx(f_len, rel=1e-6)

    r_len = 4.1 + 3.0
    r_base, r_tip = cb.stick_axis("rear", 0.0, 0.0)
    assert (r_base.x, r_base.y, r_base.z) == (
        pytest.approx(89.7, rel=1e-6),
        pytest.approx(6.2, rel=1e-6),
        pytest.approx(base_z, rel=1e-6),
    )
    assert (r_tip.x, r_tip.y, r_tip.z) == (
        pytest.approx(89.7 + r_len * ux, rel=1e-6),
        pytest.approx(6.2 + r_len * uy, rel=1e-6),
        pytest.approx(base_z + r_len * uz, rel=1e-6),
    )
    assert (r_tip - r_base).Length == pytest.approx(r_len, rel=1e-6)


def test_stick_axis_pitch_clamp_branches_and_sign_reversal() -> None:
    """Test lower clamp, interior, upper clamp, exact boundaries, and fore-aft sign flip."""
    f_len = 6.1 + 3.0
    # Lower clamp boundary: elevator_deflection_deg = -30.0 (nose-down limit)
    stroke_m30 = 1.9 * math.sin(math.radians(-30.0))
    sin_a_m30 = math.sin(math.radians(5.0)) - stroke_m30 / 5.0
    expected_dx_m30 = -f_len * sin_a_m30
    b_m30, t_m30 = cb.stick_axis("front", elevator_deflection_deg=-30.0, roll_deg=0.0)
    _, t_m45 = cb.stick_axis("front", elevator_deflection_deg=-45.0, roll_deg=0.0)
    _, t_m29_5 = cb.stick_axis("front", elevator_deflection_deg=-29.5, roll_deg=0.0)
    assert t_m30.x == pytest.approx(45.5 + expected_dx_m30, rel=1e-6)
    assert t_m45.x == pytest.approx(45.5 + expected_dx_m30, rel=1e-6)
    assert t_m30.x - b_m30.x == pytest.approx(expected_dx_m30, rel=1e-6)
    assert t_m30.x < b_m30.x
    assert t_m29_5.x > t_m30.x

    # Upper clamp boundary: elevator_deflection_deg = +15.0 (nose-up limit)
    stroke_p15 = 1.9 * math.sin(math.radians(15.0))
    sin_a_p15 = math.sin(math.radians(5.0)) - stroke_p15 / 5.0
    expected_dx_p15 = -f_len * sin_a_p15
    b_p15, t_p15 = cb.stick_axis("front", elevator_deflection_deg=15.0, roll_deg=0.0)
    _, t_p25 = cb.stick_axis("front", elevator_deflection_deg=25.0, roll_deg=0.0)
    _, t_p14_5 = cb.stick_axis("front", elevator_deflection_deg=14.5, roll_deg=0.0)
    assert t_p15.x == pytest.approx(45.5 + expected_dx_p15, rel=1e-6)
    assert t_p25.x == pytest.approx(45.5 + expected_dx_p15, rel=1e-6)
    assert t_p15.x - b_p15.x == pytest.approx(expected_dx_p15, rel=1e-6)
    assert t_p15.x > b_p15.x
    assert t_p14_5.x < t_p15.x

    # Strict monotonicity across the unclamped pitch range [-30, 15]
    xs = [
        cb.stick_axis("front", elevator_deflection_deg=d, roll_deg=0.0)[1].x
        for d in (-30.0, -15.0, 0.0, 10.0, 15.0)
    ]
    assert xs == sorted(xs) and len(set(xs)) == 5


def test_stick_axis_roll_clamp_branches_and_lateral_sign_reversal() -> None:
    """Test roll_deg lower clamp, interior, upper clamp, boundaries, and lateral sign flip."""
    f_len = 6.1 + 3.0
    a_rad = math.radians(5.0)
    base_z = wl_to_z(12.3)

    # At roll_deg = -5.0, b = 5.0 + (-5.0) = 0.0 deg, so the stick is vertical in YZ (tip.y == 6.2)
    b_zero, t_zero = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=-5.0)
    assert t_zero.y == pytest.approx(6.2, rel=1e-6)
    assert t_zero.z == pytest.approx(base_z + f_len * math.cos(a_rad), rel=1e-6)
    assert t_zero.x == pytest.approx(45.5 - f_len * math.sin(a_rad), rel=1e-6)

    # Lower roll clamp boundary: roll_deg = -20.0 -> b = -15.0 deg (tilts outboard: tip.y > base.y)
    expected_dy_m20 = -f_len * math.cos(a_rad) * math.sin(math.radians(-15.0))
    _, t_m20 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=-20.0)
    _, t_m35 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=-35.0)
    _, t_m19_5 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=-19.5)
    assert t_m20.y == pytest.approx(6.2 + expected_dy_m20, rel=1e-6)
    assert t_m35.y == pytest.approx(6.2 + expected_dy_m20, rel=1e-6)
    assert t_m20.y - b_zero.y == pytest.approx(expected_dy_m20, rel=1e-6)
    assert t_m20.y > b_zero.y
    assert t_m19_5.y < t_m20.y

    # Upper roll clamp boundary: roll_deg = +20.0 -> b = +25.0 deg (tilts inboard: tip.y < base.y)
    expected_dy_p20 = -f_len * math.cos(a_rad) * math.sin(math.radians(25.0))
    _, t_p20 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=20.0)
    _, t_p35 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=35.0)
    _, t_p19_5 = cb.stick_axis("front", elevator_deflection_deg=0.0, roll_deg=19.5)
    assert t_p20.y == pytest.approx(6.2 + expected_dy_p20, rel=1e-6)
    assert t_p35.y == pytest.approx(6.2 + expected_dy_p20, rel=1e-6)
    assert t_p20.y - b_zero.y == pytest.approx(expected_dy_p20, rel=1e-6)
    assert t_p20.y < b_zero.y
    assert t_p19_5.y > t_p20.y

    # Roll does not alter the stick's X station
    assert t_m20.x == pytest.approx(t_p20.x, rel=1e-6)


def test_stick_compound_solids_volumes_and_rotation_invariance() -> None:
    """Verify stub and grip cylinders in front and rear sticks and volume invariance under rotation."""
    front_solids = sorted(
        cb.stick("front", 0.0, 0.0).solids().vals(), key=lambda s: s.Center().z
    )
    rear_solids = sorted(
        cb.stick("rear", 0.0, 0.0).solids().vals(), key=lambda s: s.Center().z
    )
    assert len(front_solids) == 2 and len(rear_solids) == 2

    expected_front_stub_vol = math.pi * ((5.0 / 16.0) ** 2) * 6.1
    expected_rear_stub_vol = math.pi * ((5.0 / 16.0) ** 2) * 4.1
    expected_grip_vol = math.pi * (0.4**2) * 3.0
    expected_front_total = expected_front_stub_vol + expected_grip_vol
    expected_rear_total = expected_rear_stub_vol + expected_grip_vol

    assert volume(front_solids[0]) == pytest.approx(expected_front_stub_vol, rel=1e-6)
    assert volume(front_solids[1]) == pytest.approx(expected_grip_vol, rel=1e-6)
    assert vol_of(cb.stick("front", 0.0, 0.0)) == pytest.approx(
        expected_front_total, rel=1e-6
    )

    assert volume(rear_solids[0]) == pytest.approx(expected_rear_stub_vol, rel=1e-6)
    assert volume(rear_solids[1]) == pytest.approx(expected_grip_vol, rel=1e-6)
    assert vol_of(cb.stick("rear", 0.0, 0.0)) == pytest.approx(
        expected_rear_total, rel=1e-6
    )

    # Deflected stick preserves volume and places stub and grip centers at 3.05 and 7.6 along axis
    deflected = sorted(
        cb.stick("front", elevator_deflection_deg=15.0, roll_deg=-20.0).solids().vals(),
        key=lambda s: s.Center().z,
    )
    assert sum(volume(s) for s in deflected) == pytest.approx(
        expected_front_total, rel=1e-6
    )
    base, tip = cb.stick_axis("front", elevator_deflection_deg=15.0, roll_deg=-20.0)
    unit_d = (tip - base).normalized()
    expected_stub_c = base + unit_d * (6.1 / 2.0)
    expected_grip_c = base + unit_d * (6.1 + 3.0 / 2.0)
    stub_c, grip_c = deflected[0].Center(), deflected[1].Center()
    assert (stub_c.x, stub_c.y, stub_c.z) == (
        pytest.approx(expected_stub_c.x, rel=1e-6),
        pytest.approx(expected_stub_c.y, rel=1e-6),
        pytest.approx(expected_stub_c.z, rel=1e-6),
    )
    assert (grip_c.x, grip_c.y, grip_c.z) == (
        pytest.approx(expected_grip_c.x, rel=1e-6),
        pytest.approx(expected_grip_c.y, rel=1e-6),
        pytest.approx(expected_grip_c.z, rel=1e-6),
    )


def test_front_and_rear_consoles_trough_volumes_bounds_and_taper_direction(
    neutral_controls: dict[str, FusePart],
) -> None:
    """Verify console Y/Z bounds, U-channel volumes, and forward-to-aft downward taper on rear console."""
    fc = neutral_controls["front_console"].solid
    rc = neutral_controls["rear_console"].solid
    fc_bb, rc_bb = bbox_of(fc), bbox_of(rc)
    zb = wl_to_z(12.3) - 1.5  # -5.1 - 1.5 = -6.6

    # Front console: x in [44.5, 74.6], y in [4.45, 7.95], z in [-6.6, 2.5]
    assert (fc_bb.xmin, fc_bb.xmax) == (
        pytest.approx(45.5 - 1.0, rel=1e-6),
        pytest.approx(45.5 - 1.0 + 30.1, rel=1e-6),
    )
    assert (fc_bb.ymin, fc_bb.ymax) == (
        pytest.approx(6.2 - 3.5 / 2.0, rel=1e-6),
        pytest.approx(6.2 + 3.5 / 2.0, rel=1e-6),
    )
    assert (fc_bb.zmin, fc_bb.zmax) == (
        pytest.approx(zb, rel=1e-6),
        pytest.approx(zb + 9.1, rel=1e-6),
    )
    expected_fc_vol = 30.1 * (3.5 * 9.1 - (3.5 - 2 * 0.35) * (9.1 - 0.35))
    assert vol_of(fc) == pytest.approx(expected_fc_vol, rel=1e-5)

    # Rear console: x in [88.7, 114.5], y in [4.65, 7.75], z in [-6.6, 1.4]
    assert (rc_bb.xmin, rc_bb.xmax) == (
        pytest.approx(89.7 - 1.0, rel=1e-6),
        pytest.approx(89.7 - 1.0 + 25.8, rel=1e-6),
    )
    assert (rc_bb.ymin, rc_bb.ymax) == (
        pytest.approx(6.2 - 3.1 / 2.0, rel=1e-6),
        pytest.approx(6.2 + 3.1 / 2.0, rel=1e-6),
    )
    assert (rc_bb.zmin, rc_bb.zmax) == (
        pytest.approx(zb, rel=1e-6),
        pytest.approx(zb + 8.0, rel=1e-6),
    )
    h_avg = 0.5 * (8.0 + 3.0)
    expected_rc_vol = 25.8 * (3.1 * h_avg - (3.1 - 2 * 0.35) * (h_avg - 0.35))
    assert vol_of(rc) == pytest.approx(expected_rc_vol, rel=1e-5)

    # Pin taper direction: rear console is 8.0 tall at the front (x=88.7) and 3.0 at the back (x=114.5)
    fwd_upper_probe = (
        cq.Workplane("XY")
        .box(1.0, 4.0, 3.0, centered=False)
        .translate((88.8, 4.2, -2.0))
    )
    aft_upper_probe = (
        cq.Workplane("XY")
        .box(1.0, 4.0, 3.0, centered=False)
        .translate((113.4, 4.2, -2.0))
    )
    assert vol_of(rc.intersect(fwd_upper_probe)) == pytest.approx(
        2.0 * 1.0 * 0.35 * 3.0, rel=1e-4
    )
    assert vol_of(rc.intersect(aft_upper_probe)) == pytest.approx(0.0, abs=1e-9)


def test_console_cutout_cavity_offset_and_clearance_bounds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pin the 0.5 in fore/aft cutout overhang and 1.0 in top clearance in _console."""
    captured: list[tuple[cq.Workplane, cq.Workplane]] = []
    orig_cut = cq.Workplane.cut

    def capture_cut(
        self: cq.Workplane,
        to_cut: cq.Workplane,
        *args: object,
        **kwargs: object,
    ) -> cq.Workplane:
        captured.append((self, to_cut))
        return orig_cut(self, to_cut, *args, **kwargs)

    monkeypatch.setattr(cq.Workplane, "cut", capture_cut)
    fc_wp = cb.front_console()
    rc_wp = cb.rear_console()
    assert len(captured) == 2

    zb = wl_to_z(12.3) - 1.5
    wall = 0.35
    overhang_x = 0.5
    extra_len = 1.0
    extra_h = 1.0
    specs = (
        (fc_wp, captured[0], 45.5, 30.1, 3.5, 9.1, 9.1),
        (rc_wp, captured[1], 89.7, 25.8, 3.1, 8.0, 3.0),
    )
    for result_wp, (
        outer_wp,
        cavity_wp,
    ), pivot_fs, length, width, h_fwd, h_aft in specs:
        x0 = pivot_fs - 1.0
        y0 = 6.2 - width / 2.0
        outer_bb = bbox_of(outer_wp)
        cav_bb = bbox_of(cavity_wp)

        assert (cav_bb.xmin, cav_bb.xmax) == (
            pytest.approx(x0 - overhang_x, rel=1e-6),
            pytest.approx(x0 - overhang_x + length + extra_len, rel=1e-6),
        )
        assert (cav_bb.ymin, cav_bb.ymax) == (
            pytest.approx(y0 + wall, rel=1e-6),
            pytest.approx(y0 + width - wall, rel=1e-6),
        )
        assert (cav_bb.zmin, cav_bb.zmax) == (
            pytest.approx(zb + wall, rel=1e-6),
            pytest.approx(zb + wall + h_fwd + extra_h, rel=1e-6),
        )

        # Pin the exact 0.5 in forward and aft cutout clearances relative to the housing
        assert outer_bb.zmax == pytest.approx(zb + max(h_fwd, h_aft), rel=1e-6)
        assert outer_bb.xmin - cav_bb.xmin == pytest.approx(overhang_x, rel=1e-6)
        assert cav_bb.xmax - outer_bb.xmax == pytest.approx(
            extra_len - overhang_x, rel=1e-6
        )
        assert cav_bb.ymin - outer_bb.ymin == pytest.approx(wall, rel=1e-6)
        assert outer_bb.ymax - cav_bb.ymax == pytest.approx(wall, rel=1e-6)
        assert cav_bb.zmin - outer_bb.zmin == pytest.approx(wall, rel=1e-6)
        assert cav_bb.zmax - (zb + h_fwd) == pytest.approx(wall + extra_h, rel=1e-6)

        expected_cav_vol = (
            (length + extra_len) * (width - 2.0 * wall) * (h_fwd + extra_h)
        )
        assert vol_of(cavity_wp) == pytest.approx(expected_cav_vol, rel=1e-6)
        assert vol_of(result_wp) == pytest.approx(
            vol_of(outer_wp) - vol_of(outer_wp.intersect(cavity_wp)), rel=1e-5
        )

    # Also verify upward-sloping console where h_aft exceeds the cavity ceiling (zb + wall + h_fwd + 1)
    up_len, up_w, up_hf, up_ha = 10.0, 3.5, 2.0, 6.0
    up_wp = cb._console("front", up_len, up_w, up_hf, up_ha)
    outer_vol = up_len * up_w * 0.5 * (up_hf + up_ha)
    cav_top_above_zb = wall + up_hf + extra_h
    slope = (up_ha - up_hf) / up_len
    u_split = (cav_top_above_zb - up_hf) / slope
    cut_xz_area = u_split * 0.5 * ((up_hf - wall) + (cav_top_above_zb - wall)) + (
        up_len - u_split
    ) * (up_hf + extra_h)
    expected_up_vol = outer_vol - (up_w - 2.0 * wall) * cut_xz_area
    assert vol_of(up_wp) == pytest.approx(expected_up_vol, rel=1e-5)


def test_pitch_pushrod_dimensions_and_kinematic_translation() -> None:
    """Verify pushrod tube size, code-derived neutral and limit positions, and stick clearance."""
    pr_len = 12.7 + 8.5
    pr_r = 0.25
    stick_r = 5.0 / 16.0
    lever = 5.0
    b_rad = math.radians(5.0)
    base_z = wl_to_z(12.3)

    pr_0 = cb.pitch_pushrod(0.0)
    bb_0 = bbox_of(pr_0)
    assert bb_0.xlen == pytest.approx(pr_len, rel=1e-6)
    assert bb_0.ylen == pytest.approx(2.0 * pr_r, rel=1e-3)
    assert bb_0.zlen == pytest.approx(2.0 * pr_r, rel=1e-3)
    assert vol_of(pr_0) == pytest.approx(math.pi * (pr_r**2) * pr_len, rel=1e-5)

    a0_rad = math.radians(5.0)
    rod0_x = 45.5 - lever * math.sin(a0_rad)
    rod0_y = 6.2 - lever * math.cos(a0_rad) * math.sin(b_rad)
    rod0_z = base_z + lever * math.cos(a0_rad) * math.cos(b_rad)
    xmax_0 = rod0_x - stick_r - 0.1
    assert (bb_0.xmin, bb_0.xmax) == (
        pytest.approx(xmax_0 - pr_len, rel=1e-6),
        pytest.approx(xmax_0, rel=1e-6),
    )
    assert (bb_0.ymin + bb_0.ymax) / 2 == pytest.approx(rod0_y, rel=1e-3)
    assert (bb_0.zmin + bb_0.zmax) / 2 == pytest.approx(rod0_z, rel=1e-3)

    # At -30 deg (and clamped -45 deg)
    sin_a_m30 = (
        math.sin(math.radians(5.0)) - (1.9 * math.sin(math.radians(-30.0))) / lever
    )
    xmax_m30 = (45.5 - lever * sin_a_m30) - stick_r - 0.1
    bb_m30 = bbox_of(cb.pitch_pushrod(-30.0))
    bb_m45 = bbox_of(cb.pitch_pushrod(-45.0))
    assert (bb_m30.xmin, bb_m30.xmax) == (
        pytest.approx(xmax_m30 - pr_len, rel=1e-6),
        pytest.approx(xmax_m30, rel=1e-6),
    )
    assert (bb_m45.xmin, bb_m45.xmax) == (
        pytest.approx(bb_m30.xmin, rel=1e-6),
        pytest.approx(bb_m30.xmax, rel=1e-6),
    )

    # At +15 deg (and clamped +25 deg)
    sin_a_p15 = (
        math.sin(math.radians(5.0)) - (1.9 * math.sin(math.radians(15.0))) / lever
    )
    xmax_p15 = (45.5 - lever * sin_a_p15) - stick_r - 0.1
    bb_p15 = bbox_of(cb.pitch_pushrod(15.0))
    bb_p25 = bbox_of(cb.pitch_pushrod(25.0))
    assert (bb_p15.xmin, bb_p15.xmax) == (
        pytest.approx(xmax_p15 - pr_len, rel=1e-6),
        pytest.approx(xmax_p15, rel=1e-6),
    )
    assert (bb_p25.xmin, bb_p25.xmax) == (
        pytest.approx(bb_p15.xmin, rel=1e-6),
        pytest.approx(bb_p15.xmax, rel=1e-6),
    )
    assert bb_m30.xmin < bb_0.xmin < bb_p15.xmin


def test_pitch_trim_handle_pivot_and_springs_geometry(
    neutral_controls: dict[str, FusePart],
) -> None:
    """Verify pth_pivot_xz, pth tangent-lobe plate, pivot pin, and installed PTS springs."""
    px, pz = cb.pth_pivot_xz()
    expected_px = 49.5 - 5.2 + 1.5
    expected_pz = wl_to_z(8.6)
    assert (px, pz) == (
        pytest.approx(expected_px, rel=1e-6),
        pytest.approx(expected_pz, rel=1e-6),
    )

    pth_wp = neutral_controls["pth"].solid
    pth_bb = bbox_of(pth_wp)
    r1, r2, t_plate = 1.5, 0.375, 0.125
    assert (pth_bb.xmin, pth_bb.xmax) == (
        pytest.approx(expected_px - r1, rel=1e-3),
        pytest.approx(49.5, rel=1e-3),
    )
    assert (pth_bb.ymin, pth_bb.ymax) == (
        pytest.approx(-9.5 - t_plate / 2.0, rel=1e-6),
        pytest.approx(-9.5 + t_plate / 2.0, rel=1e-6),
    )
    assert (pth_bb.zmin, pth_bb.zmax) == (
        pytest.approx(expected_pz - r1, rel=1e-3),
        pytest.approx(expected_pz + r1, rel=1e-3),
    )
    # Exact analytical volume of two circles (r1, r2 at distance d) joined by outer tangents, extruded by t_plate
    d_lobes = (49.5 - r2) - expected_px
    theta = math.acos((r1 - r2) / d_lobes)
    expected_pth_vol = t_plate * (
        (math.pi - theta) * r1**2
        + theta * r2**2
        + (r1 + r2) * math.sqrt(d_lobes**2 - (r1 - r2) ** 2)
    )
    assert vol_of(pth_wp) == pytest.approx(expected_pth_vol, rel=1e-3)

    pin_wp = neutral_controls["pth_pivot"].solid
    pin_bb = bbox_of(pin_wp)
    pin_len = t_plate + 0.2
    pin_r = 0.25
    assert (pin_bb.xmin, pin_bb.xmax) == (
        pytest.approx(expected_px - pin_r, rel=1e-3),
        pytest.approx(expected_px + pin_r, rel=1e-3),
    )
    assert (pin_bb.ymin, pin_bb.ymax) == (
        pytest.approx(-9.5 - pin_len / 2.0, rel=1e-6),
        pytest.approx(-9.5 + pin_len / 2.0, rel=1e-6),
    )
    assert (pin_bb.zmin, pin_bb.zmax) == (
        pytest.approx(expected_pz - pin_r, rel=1e-3),
        pytest.approx(expected_pz + pin_r, rel=1e-3),
    )
    assert vol_of(pin_wp) == pytest.approx(math.pi * (pin_r**2) * pin_len, rel=1e-5)

    pts_solids = sorted(
        neutral_controls["pth_springs"].solid.solids().vals(),
        key=lambda s: s.Center().z,
    )
    assert len(pts_solids) == 2
    pts_r = 0.175
    pts_len = 9.0
    expected_pts_zs = sorted(wl_to_z(wl) for wl in (9.6, 8.3))
    for s, expected_z in zip(pts_solids, expected_pts_zs, strict=True):
        s_bb = s.BoundingBox(1e-5)
        assert (s_bb.xmin, s_bb.xmax) == (
            pytest.approx(40.0 - 1.0 - pts_len, rel=1e-6),
            pytest.approx(40.0 - 1.0, rel=1e-6),
        )
        assert (s_bb.ymin, s_bb.ymax) == (
            pytest.approx(-9.5 - pts_r, rel=1e-3),
            pytest.approx(-9.5 + pts_r, rel=1e-3),
        )
        assert (s_bb.zmin, s_bb.zmax) == (
            pytest.approx(expected_z - pts_r, rel=1e-3),
            pytest.approx(expected_z + pts_r, rel=1e-3),
        )
        assert volume(s) == pytest.approx(math.pi * (pts_r**2) * pts_len, rel=1e-5)


def test_roll_trim_and_springs_placement_and_volumes(
    neutral_controls: dict[str, FusePart],
) -> None:
    """Verify RT2 tabs, RT1 lever, and RTS springs in the inter-console gap."""
    rt_solids = sorted(
        neutral_controls["roll_trim"].solid.solids().vals(), key=lambda s: s.Center().x
    )
    assert len(rt_solids) == 3

    zc = wl_to_z(12.3)
    t_tab = 0.125
    w_tab, h_tab = 1.0, 2.0
    h_lever = 3.5
    r_tube = 0.75 / 2.0
    expected_specs = (
        (80.5, zc, zc + h_tab, t_tab * w_tab * h_tab),
        (82.0, zc + r_tube, zc + r_tube + h_lever, t_tab * w_tab * h_lever),
        (83.5, zc, zc + h_tab, t_tab * w_tab * h_tab),
    )
    for s, (xc, z0, z1, vol) in zip(rt_solids, expected_specs, strict=True):
        s_bb = s.BoundingBox(1e-5)
        assert (s_bb.xmin, s_bb.xmax) == (
            pytest.approx(xc - t_tab / 2.0, rel=1e-6),
            pytest.approx(xc + t_tab / 2.0, rel=1e-6),
        )
        assert (s_bb.ymin, s_bb.ymax) == (
            pytest.approx(6.2 - w_tab / 2.0, rel=1e-6),
            pytest.approx(6.2 + w_tab / 2.0, rel=1e-6),
        )
        assert (s_bb.zmin, s_bb.zmax) == (
            pytest.approx(z0, rel=1e-6),
            pytest.approx(z1, rel=1e-6),
        )
        assert volume(s) == pytest.approx(vol, rel=1e-6)
    assert vol_of(neutral_controls["roll_trim"].solid) == pytest.approx(
        2 * (t_tab * w_tab * h_tab) + t_tab * w_tab * h_lever, rel=1e-6
    )

    rts_solids = sorted(
        neutral_controls["roll_trim_springs"].solid.solids().vals(),
        key=lambda s: s.Center().y,
    )
    assert len(rts_solids) == 2
    rts_r = 0.15
    rts_len = 3.0
    rts_z = zc + 3.0
    y_ranges = (
        (6.2 - w_tab / 2.0 - rts_len, 6.2 - w_tab / 2.0),
        (6.2 + w_tab / 2.0, 6.2 + w_tab / 2.0 + rts_len),
    )
    for s, (y0, y1) in zip(rts_solids, y_ranges, strict=True):
        s_bb = s.BoundingBox(1e-5)
        assert (s_bb.xmin, s_bb.xmax) == (
            pytest.approx(82.0 - rts_r, rel=1e-3),
            pytest.approx(82.0 + rts_r, rel=1e-3),
        )
        assert (s_bb.ymin, s_bb.ymax) == (
            pytest.approx(y0, rel=1e-6),
            pytest.approx(y1, rel=1e-6),
        )
        assert (s_bb.zmin, s_bb.zmax) == (
            pytest.approx(rts_z - rts_r, rel=1e-3),
            pytest.approx(rts_z + rts_r, rel=1e-3),
        )
        assert volume(s) == pytest.approx(math.pi * (rts_r**2) * rts_len, rel=1e-5)


def test_build_controls_deflected_state_updates_moving_parts_only(
    neutral_controls: dict[str, FusePart],
) -> None:
    """Verify build_controls propagates pitch and roll to sticks/pushrod and preserves citations."""
    rolled = cb.build_controls(elevator_deflection_deg=0.0, roll_deg=15.0)
    # Roll moves both sticks laterally in Y but leaves pitch_pushrod unchanged
    assert (
        bbox_of(rolled["front_stick"].solid).ymin
        < bbox_of(neutral_controls["front_stick"].solid).ymin
    )
    assert (
        bbox_of(rolled["rear_stick"].solid).ymin
        < bbox_of(neutral_controls["rear_stick"].solid).ymin
    )
    assert bbox_of(rolled["pitch_pushrod"].solid).xmin == pytest.approx(
        bbox_of(neutral_controls["pitch_pushrod"].solid).xmin, rel=1e-6
    )

    pitched = cb.build_controls(elevator_deflection_deg=15.0, roll_deg=-20.0)
    sin_a_p15 = math.sin(math.radians(5.0)) - (1.9 * math.sin(math.radians(15.0))) / 5.0
    expected_xmax_p15 = (45.5 - 5.0 * sin_a_p15) - 5.0 / 16.0 - 0.1
    assert bbox_of(pitched["pitch_pushrod"].solid).xmax == pytest.approx(
        expected_xmax_p15, rel=1e-6
    )
    assert (
        bbox_of(pitched["front_stick"].solid).ymax
        > bbox_of(neutral_controls["front_stick"].solid).ymax
    )

    stationary = (
        "front_console",
        "rear_console",
        "torque_tube",
        "rudder_conduit",
        "pth",
        "pth_pivot",
        "pth_springs",
        "roll_trim",
        "roll_trim_springs",
    )
    for name in stationary:
        b_def = bbox_of(pitched[name].solid)
        b_neu = bbox_of(neutral_controls[name].solid)
        assert (
            b_def.xmin,
            b_def.xmax,
            b_def.ymin,
            b_def.ymax,
            b_def.zmin,
            b_def.zmax,
        ) == (
            pytest.approx(b_neu.xmin, rel=1e-6),
            pytest.approx(b_neu.xmax, rel=1e-6),
            pytest.approx(b_neu.ymin, rel=1e-6),
            pytest.approx(b_neu.ymax, rel=1e-6),
            pytest.approx(b_neu.zmin, rel=1e-6),
            pytest.approx(b_neu.zmax, rel=1e-6),
        )

    expected_cites = {
        "front_console": ("plans-1980:p97",),
        "rear_console": ("plans-1980:p97",),
        "torque_tube": ("plans-1980:p98", "plans-1980:p99"),
        "front_stick": ("plans-1980:p98", "plans-1980:p99"),
        "rear_stick": ("plans-1980:p98", "plans-1980:p99"),
        "pitch_pushrod": ("plans-1980:p99",),
        "rudder_conduit": ("plans-1980:p103",),
        "pth": ("plans-1980:p106", "plans-1980:p107"),
        "pth_pivot": ("plans-1980:p106",),
        "pth_springs": ("plans-1980:p105",),
        "roll_trim": ("plans-1980:p105", "plans-1980:p107"),
        "roll_trim_springs": ("plans-1980:p105",),
    }
    assert set(pitched) == set(expected_cites)
    for name, part in pitched.items():
        assert part.name == name
        assert part.fidelity == "representational"
        assert part.void is False
        assert part.cite == expected_cites[name]
