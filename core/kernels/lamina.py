import dataclasses
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Ply:
    E1: float
    E2: float
    G12: float
    nu12: float
    t: float
    theta_deg: float


def reduced_stiffness(E1: float, E2: float, G12: float, nu12: float) -> np.ndarray:
    """Calculate the reduced stiffness matrix Q for an orthotropic ply."""
    nu21 = nu12 * E2 / E1
    d = 1 - nu12 * nu21
    Q11 = E1 / d
    Q12 = nu12 * E2 / d
    Q22 = E2 / d
    Q66 = G12
    return np.array([[Q11, Q12, 0.0], [Q12, Q22, 0.0], [0.0, 0.0, Q66]])


def transformed_stiffness(Q: np.ndarray, theta_deg: float) -> np.ndarray:
    """Calculate the transformed reduced stiffness matrix Q-bar."""
    theta = np.radians(theta_deg)
    c = np.cos(theta)
    s = np.sin(theta)
    Q11, Q12, Q22, Q66 = Q[0, 0], Q[0, 1], Q[1, 1], Q[2, 2]

    Qb11 = Q11 * c**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * s**4
    Qb12 = (Q11 + Q22 - 4 * Q66) * s**2 * c**2 + Q12 * (s**4 + c**4)
    Qb22 = Q11 * s**4 + 2 * (Q12 + 2 * Q66) * s**2 * c**2 + Q22 * c**4
    Qb16 = (Q11 - Q12 - 2 * Q66) * c**3 * s - (Q22 - Q12 - 2 * Q66) * s**3 * c
    Qb26 = (Q11 - Q12 - 2 * Q66) * c * s**3 - (Q22 - Q12 - 2 * Q66) * c**3 * s
    Qb66 = (Q11 + Q22 - 2 * Q12 - 2 * Q66) * s**2 * c**2 + Q66 * (s**4 + c**4)

    return np.array(
        [[Qb11, Qb12, Qb16], [Qb12, Qb22, Qb26], [Qb16, Qb26, Qb66]]
    )


def stress_to_material(sigma_xy: np.ndarray, theta_deg: float) -> np.ndarray:
    """Transform global stress to material coordinate system stress."""
    theta = np.radians(theta_deg)
    c = np.cos(theta)
    s = np.sin(theta)
    T = np.array(
        [[c**2, s**2, 2 * s * c], [s**2, c**2, -2 * s * c], [-s * c, s * c, c**2 - s**2]]
    )
    return T @ np.asarray(sigma_xy, dtype=float)
