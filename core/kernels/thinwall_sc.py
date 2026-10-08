"""Shear centre of a closed multi-cell thin-wall section (Block 3, M3.2).

Walls are straight (x0, z0) -> (x1, z1) with z up, axial stiffness Et and shear stiffness Gt per unit
width. A vertical shear Sz = 1 (no horizontal shear) is applied. With X = x - xc and Z = z - zc about the
modulus-weighted centroid, the unsymmetric-bending flow gradient is dq/ds = -Et (kz Z + kx X), where
[[Izz, Ixz], [Ixz, Ixx]] [kz, kx] = [1, 0]; so the flow has no horizontal resultant and its moment does
not depend on the reference point. The flow along each wall is its unknown start value plus that
increment; node equilibrium and zero twist in every cell fix the unknowns. The shear centre is the
moment of the flow about the origin over its vertical resultant.
"""

import numpy as np


def _node(x: float, z: float) -> tuple[float, float]:
    return (round(x, 9), round(z, 9))


def _cell_signs(walls, ids) -> dict[int, int]:
    """Orient a cell's walls around its loop: +1 traversed start to end, -1 the other way."""
    ids = list(ids)
    first = ids[0]
    signs = {first: 1}
    here = _node(walls[first].x1, walls[first].z1)
    rest = ids[1:]
    while rest:
        for j in rest:
            w = walls[j]
            if _node(w.x0, w.z0) == here:
                signs[j], here = 1, _node(w.x1, w.z1)
                break
            if _node(w.x1, w.z1) == here:
                signs[j], here = -1, _node(w.x0, w.z0)
                break
        else:
            raise ValueError("cell walls do not form a closed loop")
        rest.remove(j)
    if here != _node(walls[first].x0, walls[first].z0):
        raise ValueError("cell walls do not form a closed loop")
    return signs


def shear_centre_x(walls, cells) -> float:
    """x of the shear centre of a closed section of straight walls, for a vertical shear."""
    n = len(walls)
    for w in walls:
        if w.Gt <= 0:
            raise ValueError("every wall needs a positive shear stiffness Gt")
    x0 = np.array([w.x0 for w in walls], dtype=float)
    z0 = np.array([w.z0 for w in walls], dtype=float)
    dx = np.array([w.x1 - w.x0 for w in walls], dtype=float)
    dz = np.array([w.z1 - w.z0 for w in walls], dtype=float)
    L = np.hypot(dx, dz)
    if np.any(L <= 0):
        raise ValueError("zero-length wall")
    for w, chord in zip(walls, L):
        length = getattr(w, "length", None)
        if length is not None and abs(length - chord) > 1e-9 * chord:
            raise ValueError(
                "shear centre needs wall geometry: length must match the endpoints"
            )
    Et = np.array([w.Et for w in walls], dtype=float)
    ea = float(np.sum(Et * L))
    if ea <= 0:
        raise ValueError("no axial stiffness in the section")
    xc = float(np.sum(Et * L * (x0 + dx / 2)) / ea)
    zc = float(np.sum(Et * L * (z0 + dz / 2)) / ea)
    X0, Z0 = x0 - xc, z0 - zc
    izz = float(np.sum(Et * L * ((Z0 + dz / 2) ** 2 + dz**2 / 12)))
    ixx = float(np.sum(Et * L * ((X0 + dx / 2) ** 2 + dx**2 / 12)))
    ixz = float(np.sum(Et * L * ((X0 + dx / 2) * (Z0 + dz / 2) + dx * dz / 12)))
    kz, kx = np.linalg.solve(np.array([[izz, ixz], [ixz, ixx]]), np.array([1.0, 0.0]))
    # integral of (kz Z + kx X) from 0 to s along a wall, at s = L, and its integral over [0, L]
    lin0 = kz * Z0 + kx * X0
    slope = (kz * dz + kx * dx) / L
    d_end = -Et * (lin0 * L + slope * L**2 / 2)
    d_int = -Et * (lin0 * L**2 / 2 + slope * L**3 / 6)

    rows, rhs = [], []
    nodes: dict[tuple[float, float], list[tuple[int, bool]]] = {}
    for i, w in enumerate(walls):
        nodes.setdefault(_node(w.x0, w.z0), []).append((i, False))
        nodes.setdefault(_node(w.x1, w.z1), []).append((i, True))
    for members in nodes.values():
        row, const = np.zeros(n), 0.0
        for i, ends_here in members:
            if ends_here:
                row[i] += 1.0
                const += d_end[i]
            else:
                row[i] -= 1.0
        rows.append(row)
        rhs.append(-const)
    for cell in cells:
        row, const = np.zeros(n), 0.0
        for j, sign in _cell_signs(walls, cell.wall_ids).items():
            row[j] += sign * L[j] / walls[j].Gt
            const += sign * d_int[j] / walls[j].Gt
        rows.append(row)
        rhs.append(-const)
    q0 = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)[0]

    Q = q0 * L + d_int
    tx, tz = dx / L, dz / L
    moment = float(np.sum(Q * (x0 * tz - z0 * tx)))
    return moment / float(np.sum(Q * tz))
