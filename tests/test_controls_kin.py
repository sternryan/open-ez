"""Pushrod and torque-tube kinematics for the pitch and roll controls.

Sign convention: positive elevator deflection is trailing edge UP (matches elevators_kin up travel). The stick
angle is from vertical, positive forward. Elevator travel is the Roncz 15 up / 30 down only.
"""

import io
import math
import tokenize
from pathlib import Path

import pytest

from config import config
from core import controls_kin as ck

G = config.geometry
ARM, LEVER, CANT = 1.9, 5.0, 5.0


def test_travel_limits_read_the_roncz_fields():
    assert ck.travel_limits_deg() == (
        G.elevator_travel_up_target_deg,
        G.elevator_travel_down_deg,
    )
    assert ck.travel_limits_deg() == pytest.approx((15.0, 30.0))


def test_clamp_deflection():
    assert ck.clamp_deflection_deg(0.0) == 0.0
    assert ck.clamp_deflection_deg(10.0) == pytest.approx(10.0)
    assert ck.clamp_deflection_deg(-25.0) == pytest.approx(-25.0)
    assert ck.clamp_deflection_deg(40.0) == pytest.approx(15.0)
    assert ck.clamp_deflection_deg(-60.0) == pytest.approx(-30.0)


def test_twenty_and_twenty_two_are_never_a_deflection_limit():
    seen = {ck.clamp_deflection_deg(d / 4.0) for d in range(-400, 400)}
    assert max(seen) == pytest.approx(15.0)
    assert min(seen) == pytest.approx(-30.0)
    assert ck.clamp_deflection_deg(20.0) == pytest.approx(15.0)
    assert ck.clamp_deflection_deg(22.0) == pytest.approx(15.0)
    assert ck.clamp_deflection_deg(-20.0) == pytest.approx(
        -20.0
    )  # inside the 30 down range, not a limit
    assert ck.clamp_deflection_deg(-22.0) == pytest.approx(-22.0)
    assert ck.travel_limits_deg() not in ((20.0, 22.0), (22.0, 20.0))


def test_module_source_has_no_20_or_22_literal():
    src = Path(ck.__file__).read_text()
    nums = [
        t.string
        for t in tokenize.generate_tokens(io.StringIO(src).readline)
        if t.type == tokenize.NUMBER
    ]
    bad = [n for n in nums if float(n) in (20.0, 22.0)]
    assert bad == []


def test_pushrod_stroke():
    assert ck.pushrod_stroke_in(0.0, ARM) == 0.0
    assert ck.pushrod_stroke_in(15.0, ARM) == pytest.approx(
        1.9 * math.sin(math.radians(15.0))
    )
    assert ck.pushrod_stroke_in(15.0, ARM) > 0  # up elevator: rod moves aft
    assert ck.pushrod_stroke_in(-30.0, ARM) == pytest.approx(-0.95)
    assert ck.pushrod_stroke_in(15.0, ARM) == pytest.approx(0.4918, abs=1e-3)


def test_stick_angle_at_neutral_is_the_cant():
    assert ck.stick_angle_deg(0.0, ARM, LEVER, CANT) == pytest.approx(5.0, abs=1e-12)
    assert ck.stick_angle_deg(0.0, ARM, LEVER, 7.5) == pytest.approx(7.5, abs=1e-12)
    assert ck.stick_angle_deg(0.0) == pytest.approx(
        G.ctl_stick_cant_forward_deg, abs=1e-12
    )


def test_stick_angle_direction_and_pins():
    up = ck.stick_angle_deg(15.0, ARM, LEVER, CANT)
    down = ck.stick_angle_deg(-30.0, ARM, LEVER, CANT)
    assert up < 5.0 < down  # aft stick = up elevator = smaller forward angle
    assert up == pytest.approx(-0.641, abs=0.01)
    assert down == pytest.approx(16.09, abs=0.01)


def test_defaults_read_the_fitted_config_fields():
    assert G.ctl_elevator_arm_fit_in == pytest.approx(1.9)
    assert G.ctl_stick_lever_fit_in == pytest.approx(5.0)
    assert ck.stick_angle_deg(15.0) == pytest.approx(
        ck.stick_angle_deg(15.0, ARM, LEVER, CANT)
    )
    assert ck.stick_range_deg() == pytest.approx(ck.stick_range_deg(ARM, LEVER, CANT))
    assert ck.deflection_from_stick_deg(10.0) == pytest.approx(
        ck.deflection_from_stick_deg(10.0, ARM, LEVER, CANT)
    )


def test_stick_angle_rejects_a_stroke_too_large_for_the_lever():
    with pytest.raises(ValueError):
        ck.stick_angle_deg(-30.0, 20.0, 1.0, CANT)
    with pytest.raises(ValueError):
        ck.stick_angle_deg(15.0, 20.0, 1.0, CANT)


def test_round_trip():
    for d in (-30.0, -22.5, -10.0, 0.0, 3.3, 12.5, 15.0):
        a = ck.stick_angle_deg(d, ARM, LEVER, CANT)
        assert ck.deflection_from_stick_deg(a, ARM, LEVER, CANT) == pytest.approx(
            d, abs=1e-9
        )


def test_deflection_from_stick_is_clamped():
    assert ck.deflection_from_stick_deg(-5.0, ARM, LEVER, CANT) == pytest.approx(15.0)
    assert ck.deflection_from_stick_deg(40.0, ARM, LEVER, CANT) == pytest.approx(-30.0)


def test_stick_range():
    aft, fwd = ck.stick_range_deg(ARM, LEVER, CANT)
    assert aft < fwd
    assert aft == pytest.approx(-0.641, abs=0.05)
    assert fwd == pytest.approx(16.09, abs=0.05)
    assert aft == pytest.approx(ck.stick_angle_deg(15.0, ARM, LEVER, CANT))
    assert fwd == pytest.approx(ck.stick_angle_deg(-30.0, ARM, LEVER, CANT))


def test_roll():
    assert ck.roll_travel_limits_deg() == (
        -G.ctl_roll_travel_deg,
        G.ctl_roll_travel_deg,
    )
    assert ck.roll_travel_limits_deg() == pytest.approx((-20.0, 20.0))
    assert ck.torque_tube_roll_deg(0.0) == 0.0
    assert ck.torque_tube_roll_deg(12.5) == pytest.approx(12.5)
    assert ck.torque_tube_roll_deg(-19.9) == pytest.approx(-19.9)
    assert ck.torque_tube_roll_deg(35.0) == pytest.approx(20.0)
    assert ck.torque_tube_roll_deg(-35.0) == pytest.approx(-20.0)
