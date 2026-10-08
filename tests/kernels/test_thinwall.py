"""M3.2 thin-wall section kernel against Stere's Megson three-cell example and hand cases.

Vectors: vectors/thinwall_textbook.yaml. Bounds: the ledger's M3.2 validation-bounds freeze row,
written before the kernel body exists (plan T6/T7).

Kernel contract (plan T6 signatures, plus the two names the tests need):
  Wall(x0, z0, x1, z1, t, Gt, Et, rho, length=None): a straight wall; Gt is shear stiffness per unit
      width (G x t), Et axial stiffness per unit width, rho mass per unit area. `length`, when given,
      overrides the endpoint distance (a curved wall whose arc length is printed).
  Cell(wall_ids, area): a closed cell, the indices of its walls in `walls` and its enclosed area.
  multicell_torsion(walls, cells) -> (GJ, shear_flow_per_wall): shear flows per unit torque, one per
      wall; a wall in one cell carries that cell's flow, a wall shared by two cells the difference.
  section_ei(walls, caps) -> EI about the horizontal axis through the modulus-weighted centroid;
      caps are (x, z, EA) tuples.
  shear_centre_x(walls, cells) -> x of the shear centre.
  mass_props(walls, extras) -> (mass_per_length, centroid_x, torsional_inertia); extras are
      (x, z, m) point masses per unit length; inertia is polar, about the mass centroid.
"""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.thinwall",
    reason="M3.2 kernel body pending (plan T7, after the remote-runner gate)",
)

from core.kernels.thinwall import (
    Cell,
    Wall,
    mass_props,
    multicell_torsion,
    section_ei,
    shear_centre_x,
)

from core.sources import check_citation
from tests.kernels._vectors import load

V = load("thinwall_textbook.yaml")
S = V["stere_megson_three_cell"]
R = V["single_cell_rectangle"]
W2 = V["two_cell_rectangle"]


# ---- Stere / Megson three-cell case ----------------------------------------------------------


def stere_section(walls=None, cells=None):
    walls = dict(S["walls"]) if walls is None else walls
    cells = S["cells"] if cells is None else cells
    names = list(walls)
    wall_objs = [
        Wall(0.0, 0.0, 0.0, 0.0, t, S["G"] * t, 0.0, 0.0, length=L)
        for L, t in (walls[n] for n in names)
    ]
    cell_objs = [
        Cell(tuple(names.index(w) for w in c["walls"]), c["area"]) for c in cells
    ]
    return names, wall_objs, cell_objs


def stere_matches(names, GJ, q_unit) -> bool:
    """True when the result meets the frozen bound against every printed value."""
    p, b = S["printed"], S["bound"]
    T = S["torque"]
    q = {n: abs(v) * T for n, v in zip(names, q_unit)}
    rel = b["cell_flow_and_J_rel"]
    J = GJ / S["G"]
    if abs(J - p["J"]) > rel * p["J"]:
        return False
    for n, printed in p["wall_shear_flow_abs"].items():
        if n not in q:
            return False
        tol = (
            b["web_flow_abs"]
            if n.startswith("web_") and n not in ("web_56",)
            else rel * printed
        )
        if abs(q[n] - printed) > tol:
            return False
    return True


def test_vector_cites_are_registered():
    check_citation(S["cite"])


def test_stere_three_cell_matches_printed():
    names, walls, cells = stere_section()
    GJ, q = multicell_torsion(walls, cells)
    assert stere_matches(names, GJ, q)


def test_stere_cell_flows_balance_the_torque():
    names, walls, cells = stere_section()
    _, q = multicell_torsion(walls, cells)
    cell_q = [q[names.index(c["walls"][0])] for c in S["cells"]]
    torque = sum(2 * c["area"] * qi for c, qi in zip(S["cells"], cell_q))
    assert torque == pytest.approx(1.0, rel=1e-9)


def test_broken_nose_thickness_fails():
    walls = dict(S["walls"])
    L, t = walls["nose_12o"]
    walls["nose_12o"] = [L, 2 * t]
    names, w, c = stere_section(walls=walls)
    assert not stere_matches(names, *multicell_torsion(w, c))


def test_broken_swapped_cell_areas_fails():
    cells = [dict(c) for c in S["cells"]]
    cells[0]["area"], cells[2]["area"] = cells[2]["area"], cells[0]["area"]
    names, w, c = stere_section(cells=cells)
    assert not stere_matches(names, *multicell_torsion(w, c))


def test_broken_dropped_web_fails():
    cells = [dict(c) for c in S["cells"]]
    cells[1]["walls"] = [n for n in cells[1]["walls"] if n != "web_34"]
    names, w, c = stere_section(cells=cells)
    assert not stere_matches(names, *multicell_torsion(w, c))


# ---- hand cases ------------------------------------------------------------------------------


def rect_walls(width, height, web_x=None, Gt=None, Et=None, rho=None):
    Gt = R["G"] * R["t"] if Gt is None else Gt
    Et = R["Et"] if Et is None else Et
    rho = R["rho"] if rho is None else rho
    h2 = height / 2

    def w(x0, z0, x1, z1):
        return Wall(x0, z0, x1, z1, R["t"], Gt, Et, rho)

    if web_x is None:
        walls = [
            w(0, h2, width, h2),
            w(width, h2, width, -h2),
            w(width, -h2, 0, -h2),
            w(0, -h2, 0, h2),
        ]
        return walls, [Cell((0, 1, 2, 3), width * height)]
    walls = [
        w(0, h2, web_x, h2),  # 0 top, cell 1
        w(web_x, -h2, 0, -h2),  # 1 bottom, cell 1
        w(0, -h2, 0, h2),  # 2 left
        w(web_x, h2, web_x, -h2),  # 3 web, shared
        w(web_x, h2, width, h2),  # 4 top, cell 2
        w(width, h2, width, -h2),  # 5 right
        w(width, -h2, web_x, -h2),  # 6 bottom, cell 2
    ]
    cells = [
        Cell((0, 1, 2, 3), web_x * height),
        Cell((3, 4, 5, 6), (width - web_x) * height),
    ]
    return walls, cells


def test_single_cell_gj_matches_hand_case():
    walls, cells = rect_walls(R["width"], R["height"])
    GJ, q = multicell_torsion(walls, cells)
    assert GJ == pytest.approx(R["GJ"], rel=R["rel_tol"])
    assert np.allclose(q, 1 / (2 * R["width"] * R["height"]), rtol=1e-9)


def test_symmetric_web_carries_no_torsion_flow():
    walls, cells = rect_walls(R["width"], R["height"], web_x=W2["web_x_symmetric"])
    GJ, q = multicell_torsion(walls, cells)
    assert GJ == pytest.approx(W2["GJ_symmetric_web"], rel=W2["rel_tol"])
    assert abs(q[3]) < 1e-12


def test_offset_web_changes_gj_and_matches_hand_case():
    walls, cells = rect_walls(R["width"], R["height"], web_x=W2["web_x_offset"])
    GJ, q = multicell_torsion(walls, cells)
    assert GJ == pytest.approx(W2["GJ_offset_web"], rel=W2["rel_tol"])
    assert (
        GJ > R["GJ"] * 1.01
    )  # same outline without the web is stiffer by 2.65 percent, not equal
    assert abs(q[0]) == pytest.approx(W2["cell_flows_offset_per_unit_T"][0], rel=1e-9)
    assert abs(q[4]) == pytest.approx(W2["cell_flows_offset_per_unit_T"][1], rel=1e-9)
    assert abs(q[3]) == pytest.approx(W2["web_flow_offset_abs_per_unit_T"], rel=1e-9)


def test_broken_web_dropped_from_cell_changes_gj():
    walls, cells = rect_walls(R["width"], R["height"], web_x=W2["web_x_offset"])
    broken = [cells[0], Cell((4, 5, 6), cells[1].area)]
    GJ, _ = multicell_torsion(walls, broken)
    assert GJ != pytest.approx(W2["GJ_offset_web"], rel=1e-3)


def test_section_ei_walls_only():
    walls, _ = rect_walls(R["width"], R["height"])
    assert section_ei(walls, []) == pytest.approx(R["EI_walls"], rel=1e-9)


def test_section_ei_with_caps():
    walls, _ = rect_walls(R["width"], R["height"])
    cp = R["caps_pair"]
    caps = [(R["width"] / 2, z, cp["EA"]) for z in cp["z"]]
    assert section_ei(walls, caps) == pytest.approx(R["EI_with_caps_pair"], rel=1e-9)


def test_section_ei_moves_the_neutral_axis():
    walls, _ = rect_walls(R["width"], R["height"])
    c = R["cap_top_only"]
    ei = section_ei(walls, [(c["x"], c["z"], c["EA"])])
    assert ei == pytest.approx(R["EI_with_top_cap"], rel=1e-9)


def test_broken_ei_dropped_cap_fails():
    walls, _ = rect_walls(R["width"], R["height"])
    cp = R["caps_pair"]
    ei = section_ei(walls, [(R["width"] / 2, cp["z"][0], cp["EA"])])
    assert ei != pytest.approx(R["EI_with_caps_pair"], rel=1e-3)


def test_shear_centre_of_symmetric_box_is_its_centre():
    walls, cells = rect_walls(R["width"], R["height"])
    assert shear_centre_x(walls, cells) == pytest.approx(R["shear_centre_x"], abs=1e-9)


def test_shear_centre_follows_a_rigid_shift():
    walls, cells = rect_walls(R["width"], R["height"], web_x=W2["web_x_offset"])
    x0 = shear_centre_x(walls, cells)
    moved = [
        Wall(w.x0 + 3.0, w.z0, w.x1 + 3.0, w.z1, w.t, w.Gt, w.Et, w.rho) for w in walls
    ]
    assert shear_centre_x(moved, cells) == pytest.approx(x0 + 3.0, abs=1e-9)


def test_mass_props_of_the_box():
    walls, _ = rect_walls(R["width"], R["height"])
    m, xc, ip = mass_props(walls, [])
    assert (m, xc, ip) == pytest.approx(
        (R["mass_per_length"], R["centroid_x"], R["torsional_inertia"]), rel=1e-9
    )


def test_mass_props_with_a_point_mass():
    walls, _ = rect_walls(R["width"], R["height"])
    e, want = R["extra_point"], R["with_extra"]
    m, xc, ip = mass_props(walls, [(e["x"], e["z"], e["m"])])
    assert (m, xc, ip) == pytest.approx(
        (want["mass_per_length"], want["centroid_x"], want["torsional_inertia"]),
        rel=1e-9,
    )


def test_broken_mass_props_dropped_wall_fails():
    walls, _ = rect_walls(R["width"], R["height"])
    m, xc, ip = mass_props(walls[:-1], [])
    assert (m, xc, ip) != pytest.approx(
        (R["mass_per_length"], R["centroid_x"], R["torsional_inertia"]), rel=1e-3
    )
