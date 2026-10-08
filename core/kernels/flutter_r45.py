import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import numpy as np


KT_TO_MPH = 1852 / 1609.344


@dataclass(frozen=True)
class Speed:
    """Speed representation with unit and basis validation."""

    value: float
    unit: str
    basis: str

    def __post_init__(self) -> None:
        if self.unit not in ("mph", "kt"):
            raise ValueError(f"Invalid unit: {self.unit}")
        if self.basis not in ("IAS", "CAS", "EAS", "TAS"):
            raise ValueError(f"Invalid basis: {self.basis}")


def to_mph(speed: Speed) -> Speed:
    """Convert Speed to mph while preserving the basis."""
    if speed.unit == "mph":
        return speed
    return Speed(speed.value * KT_TO_MPH, "mph", speed.basis)


def speeds_le(a: Speed, b: Speed) -> bool:
    """Compare two speeds after converting to mph; error if bases differ."""
    if a.basis != b.basis:
        raise ValueError("Bases must match for comparison.")
    return to_mph(a).value <= to_mph(b).value


def _mph(v: Speed) -> float:
    """Private helper to extract mph value; raises ValueError if not mph."""
    if v.unit != "mph":
        raise ValueError(f"Expected unit 'mph', got '{v.unit}'")
    return v.value


def twist_per_unit_torque(GJ: np.ndarray, ds: np.ndarray) -> np.ndarray:
    """Calculate cumulative twist at each strip midpoint."""
    if np.any(GJ <= 0) or np.any(ds <= 0):
        raise ValueError("GJ and ds must be positive.")
    f = ds / GJ
    theta = np.cumsum(f) - f / 2
    return theta


def wing_flexibility_factor(theta: np.ndarray, chord: np.ndarray, ds: Union[float, np.ndarray]) -> float:
    """Calculate wing flexibility factor sum(theta * chord^2 * ds)."""
    return float(np.sum(theta * (chord**2) * ds))


def wing_limit(v_d_mph: float, limit_const: float) -> float:
    """Calculate the wing limit for a given dive speed."""
    if v_d_mph <= 0:
        raise ValueError("v_d_mph must be positive.")
    return limit_const / (v_d_mph**2)


def vd_max_cleared_mph(F: float, limit_const: float) -> float:
    """Calculate the maximum cleared dive speed."""
    if F <= 0:
        raise ValueError("F must be positive.")
    return math.sqrt(limit_const / F)


def wing_criterion(F: float, v_d: Speed, limit_const: float) -> Dict[str, float]:
    """Evaluate the wing criterion for a given dive speed."""
    if v_d.unit != "mph":
        raise ValueError("v_d must be in mph.")
    lim = wing_limit(_mph(v_d), limit_const)
    return {
        "passed": bool(F <= lim),
        "F": float(F),
        "limit": lim,
        "margin": lim / F,
    }


def curve_limit(x: float, points: List[Tuple[float, float]]) -> float:
    """Linear interpolation over a set of points."""
    pts = sorted(points, key=lambda p: p[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    if x < xs[0] or x > xs[-1]:
        raise ValueError(f"x={x} is outside range [{xs[0]}, {xs[-1]}]")
    return float(np.interp(x, xs, ys))


def aileron_ki_limit(v_d: Speed, points: List[Tuple[float, float]]) -> float:
    """Calculate aileron limit using curve interpolation."""
    if v_d.unit != "mph":
        raise ValueError("v_d must be in mph.")
    return curve_limit(_mph(v_d), points)


def balance_ratio(K: float, I: float) -> float:
    """Calculate the balance ratio K/I."""
    return float(K / I)


def elevator_gamma(b: float, S_beta: float, I: float) -> float:
    """Calculate elevator gamma b*S_beta/I."""
    return float(b * S_beta / I)


def elevator_lambda(b: float, K: float, S: float, I: float) -> float:
    """Calculate elevator lambda b*K/(S*I)."""
    return float(b * K / (S * I))


def flutter_speed_parameter(v_d: Speed, b: float, f_cpm: float) -> float:
    """Calculate the flutter speed parameter v_d / (b * f_cpm)."""
    if v_d.unit != "mph":
        raise ValueError("v_d must be in mph.")
    return float(_mph(v_d) / (b * f_cpm))
