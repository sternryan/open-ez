"""Nose-gear kinematics: the NG6 pivot solved from each candidate axle station, strut swing, crank.

The axle station is a conflict (17 printed on the back cover, about 20 in the manual). Nothing here measures the strut
rake, the NG6 position or a fork offset off an image: the pivot is solved from the printed strut length (25.5), the
printed axle height (W.L. -22) and the printed pivot height above the skin (bottom W.L. 0.9 + bore 1.25), with the
lower pivot taken at the axle (zero fork offset, an assumption of the shape, not a source).
"""

import math

import pytest

from config import config
from core import nose_gear_kin as nk

G = config.geometry
PIVOT_WL = G.wl_fuselage_bottom_3view + G.ng6_bore_height_in  # 2.15


def test_candidates_are_the_conflict_pair():
    assert nk.AXLE_FS_CANDIDATES == (17.0, 20.0)
    assert nk.AXLE_FS_CANDIDATES == (G.fs_nose_wheel, G.fs_nose_wheel_manual)


def test_default_pivot_height_is_skin_plus_bore():
    assert nk.default_pivot_wl() == pytest.approx(2.15)


@pytest.mark.parametrize("axle_fs", [17.0, 20.0])
def test_pivot_is_solved_so_the_strut_is_25_5_long(axle_fs):
    pfs, pwl = nk.ng6_pivot_for_axle(
        axle_fs, G.wl_nose_wheel, PIVOT_WL, G.nose_strut_pivot_to_pivot_in
    )
    assert pwl == pytest.approx(PIVOT_WL)
    assert (
        pfs < axle_fs
    )  # the forward pivot sits ahead of the axle: the strut leans aft going down
    assert math.dist((pfs, pwl), (axle_fs, G.wl_nose_wheel)) == pytest.approx(25.5)
    assert pfs == pytest.approx(axle_fs - math.sqrt(25.5**2 - (PIVOT_WL + 22.0) ** 2))


def test_pivot_values_for_the_two_candidates():
    a = nk.ng6_pivot_for_axle(17.0, -22.0, 2.15, 25.5)
    b = nk.ng6_pivot_for_axle(20.0, -22.0, 2.15, 25.5)
    assert a[0] == pytest.approx(8.81297, abs=1e-4)
    assert b[0] - a[0] == pytest.approx(3.0)


def test_pivot_needs_a_strut_long_enough():
    with pytest.raises(ValueError):
        nk.ng6_pivot_for_axle(
            17.0, -22.0, 2.15, 20.0
        )  # the vertical drop alone is 24.15


def test_theta_down_is_the_lean_from_vertical():
    th = nk.theta_down_deg(2.15, -22.0, 25.5)
    assert th == pytest.approx(
        math.degrees(math.atan2(math.sqrt(25.5**2 - 24.15**2), 24.15))
    )
    assert 15.0 < th < 25.0


def test_strut_lower_point_down_and_flat():
    pivot = nk.ng6_pivot_for_axle(17.0, -22.0, 2.15, 25.5)
    th = nk.theta_down_deg(2.15, -22.0, 25.5)
    x, z = nk.strut_lower_point(pivot, 25.5, th)
    assert (x, z) == pytest.approx((17.0, -22.0), abs=1e-6)
    x, z = nk.strut_lower_point(pivot, 25.5, 90.0)
    assert (x, z) == pytest.approx((pivot[0] + 25.5, pivot[1]), abs=1e-9)
    x, z = nk.strut_lower_point(pivot, 25.5, 0.0)
    assert (x, z) == pytest.approx((pivot[0], pivot[1] - 25.5))


def test_retraction_theta_runs_from_down_to_flat_monotonically():
    th0 = nk.theta_down_deg(2.15, -22.0, 25.5)
    assert nk.retraction_theta_deg(0.0, th0) == pytest.approx(th0)
    assert nk.retraction_theta_deg(1.0, th0) == pytest.approx(90.0)
    vals = [nk.retraction_theta_deg(t / 10, th0) for t in range(11)]
    assert vals == sorted(vals)
    assert nk.retraction_theta_deg(0.5, th0) == pytest.approx((th0 + 90.0) / 2)
    for bad in (-0.01, 1.01):
        with pytest.raises(ValueError):
            nk.retraction_theta_deg(bad, th0)


@pytest.mark.parametrize("axle_fs", [17.0, 20.0])
def test_retracted_strut_end_stays_forward_of_the_panel(axle_fs):
    pfs, _ = nk.ng6_pivot_for_axle(axle_fs, G.wl_nose_wheel, PIVOT_WL, 25.5)
    assert (
        pfs + 25.5 < G.fs_panel
    )  # the wheel folds into the box ahead of the panel (FS 39.75), either candidate


def test_crank_is_10_8_turns_over_the_156_degree_arm_swing():
    assert nk.crank_turns(0.0) == 0.0
    assert nk.crank_turns(1.0) == pytest.approx(10.8)
    assert nk.crank_turns(0.5) == pytest.approx(5.4)
    assert nk.crank_angle_deg(1.0) == pytest.approx(10.8 * 360.0)
    assert nk.ng50_angle_deg(1.0) == pytest.approx(156.0)
    assert nk.ng50_angle_deg(0.25) == pytest.approx(39.0)
    assert nk.crank_seconds_range() == (5.0, 7.0)
    for f in (nk.crank_turns, nk.crank_angle_deg, nk.ng50_angle_deg):
        with pytest.raises(ValueError):
            f(1.2)


def test_retraction_can_end_above_flat_for_tire_clearance():
    th0 = nk.theta_down_deg(2.15, -22.0, 25.5)
    up = nk.theta_up_for_clearance_deg(2.15, 25.5, 5.4)
    assert up == pytest.approx(90.0 + math.degrees(math.asin((5.4 - 2.15) / 25.5)))
    assert up > 90.0
    assert nk.retraction_theta_deg(1.0, th0, up) == pytest.approx(up)
    assert nk.retraction_theta_deg(0.0, th0, up) == pytest.approx(th0)
    assert nk.theta_up_for_clearance_deg(2.15, 25.5, 2.15) == pytest.approx(90.0)
    with pytest.raises(ValueError):
        nk.theta_up_for_clearance_deg(2.15, 25.5, 40.0)
