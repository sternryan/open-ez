import numpy as np
from dataclasses import dataclass
from core.kernels.thinwall_sc import shear_centre_x

@dataclass(frozen=True)
class Wall:
    x0: float
    z0: float
    x1: float
    z1: float
    t: float
    Gt: float
    Et: float
    rho: float
    length: float | None = None

@dataclass(frozen=True)
class Cell:
    wall_ids: tuple[int, ...]
    area: float

def multicell_torsion(walls: list[Wall], cells: list[Cell]) -> tuple[float, np.ndarray]:
    """Calculate GJ and shear flows per unit torque for a multicell thin-wall section."""
    n = len(cells)
    K = np.zeros((n + 1, n + 1))
    r = np.zeros(n + 1)

    wall_to_cells = [[] for _ in range(len(walls))]
    for i, cell in enumerate(cells):
        for w_id in cell.wall_ids:
            wall_to_cells[w_id].append(i)

    for i, cell in enumerate(cells):
        for w_id in cell.wall_ids:
            w = walls[w_id]
            L = w.length if w.length is not None else np.sqrt((w.x1 - w.x0)**2 + (w.z1 - w.z0)**2)
            delta_w = L / w.Gt
            K[i, i] += delta_w / (2 * cell.area)
            for j in wall_to_cells[w_id]:
                if i != j:
                    K[i, j] -= delta_w / (2 * cell.area)
        K[i, n] = -1
        r[i] = 0

    for i, cell in enumerate(cells):
        K[n, i] = 2 * cell.area
    r[n] = 1

    x = np.linalg.solve(K, r)
    GJ = 1 / x[n]

    flows = []
    for w_id in range(len(walls)):
        ids = wall_to_cells[w_id]
        if len(ids) == 1:
            flows.append(x[ids[0]])
        elif len(ids) == 2:
            i, j = ids
            flows.append(x[i] - x[j] if i < j else x[j] - x[i])
        elif len(ids) == 0:
            flows.append(0.0)
        else:
            raise ValueError("Wall belongs to three or more cells")

    return float(GJ), np.array(flows)

def section_ei(walls: list[Wall], caps: list[tuple[float, float, float]]) -> float:
    """Calculate the bending stiffness EI about the horizontal axis."""
    sum_EA_z = 0.0
    sum_EA = 0.0
    for w in walls:
        L = w.length if w.length is not None else np.sqrt((w.x1 - w.x0)**2 + (w.z1 - w.z0)**2)
        EA = w.Et * L
        zmid = (w.z0 + w.z1) / 2
        sum_EA_z += EA * zmid
        sum_EA += EA
    for x, z, EA in caps:
        sum_EA_z += EA * z
        sum_EA += EA

    zc = sum_EA_z / sum_EA
    EI = 0.0
    for w in walls:
        L = w.length if w.length is not None else np.sqrt((w.x1 - w.x0)**2 + (w.z1 - w.z0)**2)
        zmid = (w.z0 + w.z1) / 2
        EI += w.Et * L * ((zmid - zc)**2 + (w.z1 - w.z0)**2 / 12)
    for x, z, EA in caps:
        EI += EA * (z - zc)**2

    return float(EI)

def mass_props(walls: list[Wall], extras: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    """Calculate mass, centroid, and polar inertia for the section."""
    m_total = 0.0
    xc_sum = 0.0
    zc_sum = 0.0
    wall_data = []

    for w in walls:
        L = w.length if w.length is not None else np.sqrt((w.x1 - w.x0)**2 + (w.z1 - w.z0)**2)
        mw = w.rho * L
        xmid = (w.x0 + w.x1) / 2
        zmid = (w.z0 + w.z1) / 2
        m_total += mw
        xc_sum += mw * xmid
        zc_sum += mw * zmid
        wall_data.append((mw, xmid, zmid, L))

    for x, z, m in extras:
        m_total += m
        xc_sum += m * x
        zc_sum += m * z

    xc = xc_sum / m_total
    zc = zc_sum / m_total

    inertia = 0.0
    for mw, xmid, zmid, L in wall_data:
        inertia += mw * ((xmid - xc)**2 + (zmid - zc)**2 + L**2 / 12)
    for x, z, m in extras:
        inertia += m * ((x - xc)**2 + (z - zc)**2)

    return float(m_total), float(xc), float(inertia)

__all__ = ("Wall", "Cell", "multicell_torsion", "section_ei", "mass_props", "shear_centre_x")
