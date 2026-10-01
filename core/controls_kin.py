"""Pitch and roll control kinematics; arm and lever defaults are fitted, representational values."""

from __future__ import annotations

import math

from config import config

G = config.geometry


def travel_limits_deg() -> tuple[float, float]:
    """Return the up target and down travel range in degrees."""
    return (G.elevator_travel_up_target_deg, G.elevator_travel_down_deg)


def clamp_deflection_deg(d: float) -> float:
    """Clip deflection to [-down, +up] limits."""
    up = G.elevator_travel_up_target_deg
    down = G.elevator_travel_down_deg
    return max(-down, min(up, d))


def pushrod_stroke_in(deflection_deg: float, arm_in: float) -> float:
    """Calculate pushrod stroke in inches for a given deflection."""
    return arm_in * math.sin(math.radians(deflection_deg))


def stick_angle_deg(
    deflection_deg: float,
    arm_in: float = G.ctl_elevator_arm_fit_in,
    lever_in: float = G.ctl_stick_lever_fit_in,
    neutral_cant_deg: float = G.ctl_stick_cant_forward_deg,
) -> float:
    """Calculate stick angle from vertical in degrees."""
    stroke = pushrod_stroke_in(deflection_deg, arm_in)
    s = math.sin(math.radians(neutral_cant_deg)) - (stroke / lever_in)
    if abs(s) > 1:
        raise ValueError("Stroke exceeds lever capacity.")
    return math.degrees(math.asin(s))


def deflection_from_stick_deg(
    angle_deg: float,
    arm_in: float = G.ctl_elevator_arm_fit_in,
    lever_in: float = G.ctl_stick_lever_fit_in,
    neutral_cant_deg: float = G.ctl_stick_cant_forward_deg,
) -> float:
    """Calculate deflection from stick angle in degrees."""
    stroke = lever_in * (
        math.sin(math.radians(neutral_cant_deg)) - math.sin(math.radians(angle_deg))
    )
    ratio = stroke / arm_in
    if abs(ratio) > 1:
        # Clamp ratio to [-1, 1] to allow stick angles outside physical limits to return clamped deflection
        ratio = max(-1.0, min(1.0, ratio))
    deflection = math.degrees(math.asin(ratio))
    return clamp_deflection_deg(deflection)


def stick_range_deg(
    arm_in: float = G.ctl_elevator_arm_fit_in,
    lever_in: float = G.ctl_stick_lever_fit_in,
    neutral_cant_deg: float = G.ctl_stick_cant_forward_deg,
) -> tuple[float, float]:
    """Return the (aft, forward) stick angle range in degrees."""
    up_limit = G.elevator_travel_up_target_deg
    down_limit = G.elevator_travel_down_deg
    aft = stick_angle_deg(up_limit, arm_in, lever_in, neutral_cant_deg)
    fwd = stick_angle_deg(-down_limit, arm_in, lever_in, neutral_cant_deg)
    return (aft, fwd)


def torque_tube_roll_deg(stick_roll_deg: float) -> float:
    """Clip stick roll to torque tube limits."""
    limit = G.ctl_roll_travel_deg
    return max(-limit, min(limit, stick_roll_deg))


def roll_travel_limits_deg() -> tuple[float, float]:
    """Return the roll travel limits in degrees."""
    limit = G.ctl_roll_travel_deg
    return (-limit, limit)
