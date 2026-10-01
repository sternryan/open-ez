from __future__ import annotations

import math

from config import config

G = config.geometry

AXLE_FS_CANDIDATES = (G.fs_nose_wheel, G.fs_nose_wheel_manual)


def default_pivot_wl() -> float:
    """Return the default pivot W.L. based on skin and bore height."""
    return G.wl_fuselage_bottom_3view + G.ng6_bore_height_in


def ng6_pivot_for_axle(
    axle_fs: float, axle_wl: float, pivot_wl: float, strut_len: float
) -> tuple[float, float]:
    """Solve for the pivot (fs, wl) given axle position and strut length."""
    dz = pivot_wl - axle_wl
    if dz > strut_len:
        raise ValueError("Strut length insufficient for vertical drop.")
    run = math.sqrt(strut_len**2 - dz**2)
    return (axle_fs - run, pivot_wl)


def theta_down_deg(pivot_wl: float, axle_wl: float, strut_len: float) -> float:
    """Return the strut's lean angle in degrees from vertical."""
    dz = pivot_wl - axle_wl
    if dz > strut_len:
        raise ValueError("Strut length insufficient for vertical drop.")
    run = math.sqrt(strut_len**2 - dz**2)
    return math.degrees(math.atan2(run, dz))


def strut_lower_point(
    pivot_xz: tuple[float, float], strut_len: float, theta_deg: float
) -> tuple[float, float]:
    """Return the (x, z) coordinates of the lower end of the strut."""
    px, pz = pivot_xz
    t = math.radians(theta_deg)
    return (px + strut_len * math.sin(t), pz - strut_len * math.cos(t))


def retraction_theta_deg(t: float, theta_down: float, theta_up: float = 90.0) -> float:
    """Return the strut angle in degrees during retraction (theta_up: the retracted angle, 90 = flat along the bottom)."""
    if not 0 <= t <= 1:
        raise ValueError("Retraction parameter t must be in [0, 1].")
    return theta_down + t * (theta_up - theta_down)


def theta_up_for_clearance_deg(
    pivot_wl: float, strut_len: float, clearance_wl: float
) -> float:
    """Retracted strut angle that lifts the lower pivot to clearance_wl (> pivot_wl tilts the strut above flat, aft and up)."""
    rise = clearance_wl - pivot_wl
    if abs(rise) > strut_len:
        raise ValueError("Strut too short to reach the clearance height.")
    return 90.0 + math.degrees(math.asin(rise / strut_len))


def crank_turns(t: float) -> float:
    """Return the number of crank turns for a given retraction progress."""
    if not 0 <= t <= 1:
        raise ValueError("Retraction parameter t must be in [0, 1].")
    return t * G.nose_crank_turns


def crank_angle_deg(t: float) -> float:
    """Return the crank angle in degrees for a given retraction progress."""
    return crank_turns(t) * 360


def ng50_angle_deg(t: float) -> float:
    """Return the NG50 angle in degrees for a given retraction progress."""
    if not 0 <= t <= 1:
        raise ValueError("Retraction parameter t must be in [0, 1].")
    return t * G.ng50_travel_deg


def crank_seconds_range() -> tuple[float, float]:
    """Return the range of crank operation in seconds."""
    return (G.nose_crank_seconds_min, G.nose_crank_seconds_max)
