"""Shear centre of a closed multi-cell thin-wall section (Block 3, M3.2).

Walls are straight (x0, z0) -> (x1, z1) with z up, axial stiffness Et and shear stiffness Gt per unit
width. A vertical shear Sz = 1 is applied; the shear flow along each wall is its unknown start value plus
the open-section increment -(Et/EI) * integral of (z - zc) ds. Node equilibrium and zero twist in every
cell fix the unknowns; the shear centre is the moment of the resulting flow about the origin over its
vertical resultant.
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
    L = np.array([np.hypot(w.x1 - w.x0, w.z1 - w.z0) for w in walls])
    Et = np.array([w.Et for w in walls], dtype=float)
    z0 = np.array([w.z0 for w in walls], dtype=float)
    dz = np.array([w.z1 - w.z0 for w in walls], dtype=float)
    zc = float(np.sum(Et * L * (z0 + dz / 2)) / np.sum(Et * L))
    EI = float(np.sum(Et * L * ((z0 + dz / 2 - zc) ** 2 + dz**2 / 12)))
    d_end = -(Et / EI) * ((z0 - zc) * L + dz * L / 2)
    d_int = -(Et / EI) * ((z0 - zc) * L**2 / 2 + dz * L**2 / 6)

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
    tx = np.array([(w.x1 - w.x0) for w in walls]) / L
    tz = dz / L
    x0 = np.array([w.x0 for w in walls], dtype=float)
    moment = float(np.sum(Q * (x0 * tz - z0 * tx)))
    return moment / float(np.sum(Q * tz))
