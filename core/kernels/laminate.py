import numpy as np

from core.kernels.lamina import (
    Ply,
    reduced_stiffness,
    stress_to_material,
    transformed_stiffness,
)


def abd(plies: list[Ply]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate the ABD matrix of a laminate."""
    if not plies:
        raise ValueError("Ply list is empty.")

    h = sum(p.t for p in plies)
    z_k = np.zeros(len(plies) + 1)
    z_k[0] = -h / 2
    for i, p in enumerate(plies):
        z_k[i + 1] = z_k[i] + p.t

    A = np.zeros((3, 3))
    B = np.zeros((3, 3))
    D = np.zeros((3, 3))

    for i, p in enumerate(plies):
        Q_bar = transformed_stiffness(
            reduced_stiffness(p.E1, p.E2, p.G12, p.nu12), p.theta_deg
        )
        z_prev, z_curr = z_k[i], z_k[i + 1]
        A += Q_bar * (z_curr - z_prev)
        B += 0.5 * Q_bar * (z_curr**2 - z_prev**2)
        D += (1 / 3) * Q_bar * (z_curr**3 - z_prev**3)

    return A, B, D


def laminate_constants(A: np.ndarray, h: float) -> dict:
    """Calculate in-plane engineering constants from the A matrix."""
    a = np.linalg.inv(A)
    Ex = 1 / (h * a[0, 0])
    Ey = 1 / (h * a[1, 1])
    Gxy = 1 / (h * a[2, 2])
    nuxy = -a[0, 1] / a[0, 0]
    return {"Ex": float(Ex), "Ey": float(Ey), "Gxy": float(Gxy), "nuxy": float(nuxy)}


def midplane_response(
    plies: list[Ply], N: np.ndarray, M: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Solve for midplane strain and curvature."""
    A, B, D = abd(plies)
    ABD = np.block([[A, B], [B, D]])
    load = np.concatenate([N, M])
    res = np.linalg.solve(ABD, load)
    return res[:3], res[3:]


def strain_at(eps0: np.ndarray, kappa: np.ndarray, z: float) -> np.ndarray:
    """Calculate total strain at a specific z coordinate."""
    return eps0 + z * kappa


def ply_stresses(
    plies: list[Ply], N: np.ndarray, M: np.ndarray
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Calculate material-axis stresses at the top and bottom of each ply."""
    eps0, kappa = midplane_response(plies, N, M)
    h = sum(p.t for p in plies)
    z_k = np.zeros(len(plies) + 1)
    z_k[0] = -h / 2
    for i, p in enumerate(plies):
        z_k[i + 1] = z_k[i] + p.t

    results = []
    for i, p in enumerate(plies):
        Q_bar = transformed_stiffness(
            reduced_stiffness(p.E1, p.E2, p.G12, p.nu12), p.theta_deg
        )
        top_stress = stress_to_material(
            Q_bar @ strain_at(eps0, kappa, z_k[i]), p.theta_deg
        )
        bottom_stress = stress_to_material(
            Q_bar @ strain_at(eps0, kappa, z_k[i + 1]), p.theta_deg
        )
        results.append((top_stress, bottom_stress))
    return results
