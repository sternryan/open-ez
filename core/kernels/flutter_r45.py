"""FAA Report 45 simplified flutter criteria (Block 3, M3.3): pure functions, no airframe data.

The criteria take V_D in mph IAS (faa-report-45:p4 basis; the mph unit is an inference from p6 and the
Fig 2 axis, faa-report-45:p6 and p10). Any other unit or basis is rejected, never converted silently.
"""

import math
from dataclasses import dataclass

import numpy as np

KT_TO_MPH = 1852 / 1609.344
CRITERION_UNIT = "mph"
CRITERION_BASIS = "IAS"


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
        if not (math.isfinite(self.value) and self.value > 0):
            raise ValueError(f"Speed must be finite and positive: {self.value}")


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
    """The criterion speed in mph IAS; any other unit or basis raises ValueError."""
    if v.unit != CRITERION_UNIT or v.basis != CRITERION_BASIS:
        raise ValueError(f"Report 45 takes V_D in mph IAS, got {v.unit} {v.basis}")
    return v.value


def twist_per_unit_torque(GJ: np.ndarray, ds: np.ndarray) -> np.ndarray:
    """Calculate cumulative twist at each strip midpoint."""
    GJ, ds = np.asarray(GJ, dtype=float), np.asarray(ds, dtype=float)
    if GJ.shape != ds.shape or GJ.ndim != 1 or GJ.size == 0:
        raise ValueError("GJ and ds must be equal-length 1-D arrays.")
    if not (np.all(GJ > 0) and np.all(ds > 0)):
        raise ValueError("GJ and ds must be positive.")
    f = ds / GJ
    theta = np.cumsum(f) - f / 2
    return theta


def wing_flexibility_factor(
    theta: np.ndarray, chord: np.ndarray, ds: float | np.ndarray
) -> float:
    """Calculate wing flexibility factor sum(theta * chord^2 * ds)."""
    theta, chord = np.asarray(theta, dtype=float), np.asarray(chord, dtype=float)
    ds = np.broadcast_to(np.asarray(ds, dtype=float), theta.shape)
    if theta.ndim != 1 or theta.size == 0 or chord.shape != theta.shape:
        raise ValueError("theta and chord must be equal-length 1-D arrays.")
    if not (np.all(ds > 0) and np.all(chord > 0) and np.all(theta >= 0)):
        raise ValueError("ds and chord must be positive and theta non-negative.")
    return float(np.sum(theta * chord**2 * ds))


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


def wing_criterion(F: float, v_d: Speed, limit_const: float) -> dict[str, float]:
    """Evaluate the wing criterion for a given dive speed."""
    if not (math.isfinite(F) and F > 0):
        raise ValueError("F must be finite and positive.")
    lim = wing_limit(_mph(v_d), limit_const)
    return {
        "passed": bool(F <= lim),
        "F": float(F),
        "limit": lim,
        "margin": lim / F,
    }


def curve_limit(x: float, points: list[tuple[float, float]]) -> float:
    """Linear interpolation over a set of points."""
    pts = sorted(points, key=lambda p: p[0])
    if len(pts) < 2:
        raise ValueError("a curve needs at least two points")
    xs = np.array([p[0] for p in pts], dtype=float)
    ys = np.array([p[1] for p in pts], dtype=float)
    if np.any(np.diff(xs) <= 0):
        raise ValueError("curve x values must be distinct")
    if not math.isfinite(x) or x < xs[0] or x > xs[-1]:
        raise ValueError(f"x={x} is outside range [{xs[0]}, {xs[-1]}]")
    return float(np.interp(x, xs, ys))


def aileron_ki_limit(v_d: Speed, points: list[tuple[float, float]]) -> float:
    """Calculate aileron limit using curve interpolation."""
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
    return float(_mph(v_d) / (b * f_cpm))
