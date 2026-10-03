"""Partial-span canard downwash on the wing (ledger C4).

Method fixed in the ledger before it was run: the canard as one horseshoe vortex (vortex span
b' = (pi/4) b_c, McCormick; Anderson sec. 5), Biot-Savart for the bound segment and the two
semi-infinite trailing legs (Katz and Plotkin), and a chord-weighted strip-theory average of
d eps/d alpha over the wing span. Every expected value below is computed by hand in the comment.
"""

import math
import numpy as np
import pytest

from core.analysis import average_horseshoe_downwash_gradient, horseshoe_wz_per_gamma


def test_near_field_point_on_the_centreline_hand_computed():
    # s = 1, point (x, y, z) = (1, 0, 0).
    # Bound segment: rho = 1; -(1/(4 pi)) [1/sqrt(2) + 1/sqrt(2)] = -sqrt(2)/(4 pi) = -0.112540.
    # Each leg: r = 1, d_y = -+1, (1/(4 pi)) * 1 * (1 + 1/sqrt(2)) downward = -0.135847;
    # both legs -0.271694. Total w_z / Gamma = -0.384234 (downwash).
    assert horseshoe_wz_per_gamma(1.0, 0.0, 0.0, 1.0) == pytest.approx(
        -0.384234, abs=1e-6
    )


def test_outboard_of_the_tip_vortex_is_upwash():
    # Far aft, z = 0, y = 2 s: the starboard leg (d_y = +1) gives +2/(4 pi) = +0.159155,
    # the port leg (d_y = 3, sign -) gives -(2/(4 pi))(1/3) = -0.053052. Net +0.106103, upwash.
    got = horseshoe_wz_per_gamma(1e9, 2.0, 0.0, 1.0)
    assert got == pytest.approx(1.0 / (2 * math.pi) - 1.0 / (6 * math.pi), rel=1e-6)
    assert got > 0


def test_far_field_centreline_matches_the_horseshoe_value():
    # Far aft on the centreline: w_z / Gamma = -1/(pi s). With Gamma/V = a_c S_c alpha / (2 b')
    # d eps/d alpha = a_c S_c / (pi b'^2). a_c = 2 pi, S_c = 10, b_c = 8/pi (b' = 2, s = 1):
    # 2 pi * 10 / (pi * 4) = 5.0.
    y = np.array([0.0])
    got = average_horseshoe_downwash_gradient(
        a_c=2 * math.pi,
        area_c=10.0,
        span_c=8 / math.pi,
        y=y,
        chord=np.array([1.0]),
        dx=np.array([1e9]),
        z=0.0,
    )
    assert got == pytest.approx(5.0, rel=1e-6)


def test_spanwise_average_over_a_wider_aft_span_hand_computed():
    # Uniform chord over [-B, B], B = 2 s, s = 1, z = 0.1, far aft (bound segment -> 0; legs
    # fully developed, factor 2). Each leg's w_z integrates in closed form:
    # integral 2 d_y / (d_y^2 + z^2) dy = ln(d_y^2 + z^2); both legs together give
    # (1/(4 pi)) * 2 * ln(((B - s)^2 + z^2) / ((B + s)^2 + z^2)) = (1/(2 pi)) ln(1.01 / 9.01)
    # = (1/(2 pi)) * (-2.188385) = -0.348292; average over 2B = 4: -0.087073.
    # d eps/d alpha_avg = a_c S_c / (2 b') * 0.087073 = (2 pi * 10 / 4) * 0.087073 = 1.367749.
    n = 400_000
    edges = np.linspace(-2.0, 2.0, n + 1)
    y = 0.5 * (edges[1:] + edges[:-1])
    got = average_horseshoe_downwash_gradient(
        a_c=2 * math.pi,
        area_c=10.0,
        span_c=8 / math.pi,
        y=y,
        chord=np.ones_like(y),
        dx=np.full_like(y, 1e9),
        z=0.1,
    )
    assert got == pytest.approx(2 * math.pi * 10 / 4 * 0.087073062, rel=1e-4)


def test_average_over_a_very_wide_span_tends_to_zero():
    # The trailing pair's downwash inside and upwash outside cancel over an unbounded span:
    # the closed form above with B -> inf gives ln(1) = 0.
    edges = np.linspace(-2000.0, 2000.0, 4_000_001)
    y = 0.5 * (edges[1:] + edges[:-1])
    got = average_horseshoe_downwash_gradient(
        a_c=2 * math.pi,
        area_c=10.0,
        span_c=8 / math.pi,
        y=y,
        chord=np.ones_like(y),
        dx=np.full_like(y, 1e9),
        z=0.1,
    )
    assert abs(got) < 1e-2


def test_wing_average_is_continuous_as_the_canard_height_goes_to_zero():
    # At z = 0 the trailing legs are singular at the wing stations y = +-s. The average is then a
    # principal-value integral (the closed form above with z = 0 is finite), the limit of z -> 0+.
    # The wing strips must straddle each vortex station symmetrically so that a strip midpoint
    # landing next to the vortex does not dominate the sum. h = 0 and h = 0.01 in must agree.
    from config import config
    from core.analysis import PhysicsEngine

    original_h = config.geometry.canard_vertical_offset_in
    try:
        config.geometry.canard_vertical_offset_in = 0.0
        np_h0 = PhysicsEngine().calculate_neutral_point()
        config.geometry.canard_vertical_offset_in = 0.01
        np_h001 = PhysicsEngine().calculate_neutral_point()
    finally:
        config.geometry.canard_vertical_offset_in = original_h
    assert np_h0 == pytest.approx(np_h001, abs=0.05)
