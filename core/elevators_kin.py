from __future__ import annotations

import math

from config import config

G = config.geometry
SIDES = ("left", "right")


def _validate_side(side: str) -> None:
    if side not in SIDES:
        raise ValueError(f"Invalid side: {side}")


def elevator_span(side: str) -> tuple[float, float]:
    """Return the span of the elevator for the given side."""
    _validate_side(side)
    if side == "right":
        return (G.elevator_inboard_bl_right_in, G.elevator_outboard_end_bl_in)
    return (-G.elevator_outboard_end_bl_in, G.elevator_inboard_bl_left_in)


def hinge_stations(side: str) -> list[float]:
    """Return the list of hinge stations on the elevator for the given side."""
    _validate_side(side)
    lo, hi = elevator_span(side)
    if side == "right":
        stations = sorted(G.elevator_hinge_bl_in)
    else:
        stations = sorted([-s for s in G.elevator_hinge_bl_in])

    return [s for s in stations if lo <= s <= hi]


def unplaced_hinge_stations(side: str) -> list[float]:
    """Return the hinge stations that fall outside the elevator span."""
    _validate_side(side)
    lo, hi = elevator_span(side)
    if side == "right":
        stations = sorted(G.elevator_hinge_bl_in)
    else:
        stations = sorted([-s for s in G.elevator_hinge_bl_in])

    return [s for s in stations if not (lo <= s <= hi)]


def hinge_count_note() -> dict[str, int]:
    """Return a note about the number of slots and placed stations."""
    placed = len(hinge_stations("left")) + len(hinge_stations("right"))
    return {"slots_in_text": 7, "stations_placed": placed}


def pin_length(side: str) -> float:
    """Return the pin length for the given side."""
    _validate_side(side)
    return G.elevator_pin_right_in if side == "right" else G.elevator_pin_left_in


def travel_range_deg() -> tuple[float, float]:
    """Return the up target and down travel range in degrees."""
    return (G.elevator_travel_up_target_deg, G.elevator_travel_down_deg)


def classify_up_travel(deg: float) -> str:
    """Classify the up travel degree into categories."""
    floor = G.elevator_travel_up_floor_deg
    target = G.elevator_travel_up_target_deg
    if deg < floor:
        return "below floor"
    if deg < target:
        return "floor only"
    return "target"


def rotate_about_hinge(
    pt_xz: tuple[float, float], hinge_xz: tuple[float, float], deg_down: float
) -> tuple[float, float]:
    """Rotate a point about a hinge point by a given angle in degrees."""
    px, pz = pt_xz
    hx, hz = hinge_xz
    dx, dz = px - hx, pz - hz
    t = math.radians(deg_down)
    x = hx + dx * math.cos(t) + dz * math.sin(t)
    z = hz - dx * math.sin(t) + dz * math.cos(t)
    return (x, z)


def hang_pitch_deg(cg_dx: float, cg_dz: float) -> float:
    """Calculate the hang pitch in degrees."""
    if abs(cg_dx) < 1e-12 and abs(cg_dz) < 1e-12:
        raise ValueError("CG cannot be at the hinge.")
    phi = math.degrees(math.atan2(cg_dz, cg_dx))
    theta = -90.0 - phi
    while theta <= -180.0:
        theta += 360.0
    while theta > 180.0:
        theta -= 360.0
    return theta


def hangs_nose_down(cg_dx: float, cg_dz: float) -> bool:
    """Check if the elevator hangs nose down."""
    pitch = hang_pitch_deg(cg_dx, cg_dz)
    return 0 < pitch < 180


def cs11_volume_in3() -> float:
    """Return the volume of the CS11 lead block."""
    d = G.cs11_lead_dims
    return d[0] * d[1] * d[2]
