"""M3.1 laminate kernel against Kaw's printed [30/-45/-60] example (vectors/clt_textbook.yaml)."""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.laminate",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.lamina import (
    Ply,
    reduced_stiffness,
    stress_to_material,
    transformed_stiffness,
)
from core.kernels.laminate import abd, midplane_response, ply_stresses, strain_at

from tests.kernels._vectors import load, printed_close

V = load("clt_textbook.yaml")
G = V["glass_epoxy_lamina"]
L = V["laminate_30_m45_m60"]


def plies(angles, E1=G["E1"], E2=G["E2"]):
    return [Ply(E1, E2, G["G12"], G["nu12"], L["t_ply"], a) for a in angles]


def test_abd_matches_printed():
    A, B, D = abd(plies(L["angles_deg"]))
    assert printed_close(A, L["A"])
    assert printed_close(B, L["B"])
    assert printed_close(D, L["D"])


def test_midplane_strains_and_curvatures_match_printed():
    eps0, kappa = midplane_response(
        plies(L["angles_deg"]), np.array(L["N"]), np.array(L["M"])
    )
    assert printed_close(eps0, L["eps0"])
    assert printed_close(kappa, L["kappa"])


def test_strain_at_top_of_ply_two_matches_printed():
    eps0, kappa = midplane_response(
        plies(L["angles_deg"]), np.array(L["N"]), np.array(L["M"])
    )
    s = L["strain_top_of_ply2"]
    assert printed_close(strain_at(eps0, kappa, s["z"]), s["eps"])


def _expected_material_stress(angle, eps):
    Q = reduced_stiffness(G["E1"], G["E2"], G["G12"], G["nu12"])
    return stress_to_material(transformed_stiffness(Q, angle) @ np.asarray(eps), angle)


def test_ply_stresses_top_of_ply_two_follow_the_printed_strain():
    # Consistency with the printed strain, not a printed stress: the strain is printed to 4 figures,
    # so the comparison allows 0.2 percent of the largest component.
    out = ply_stresses(plies(L["angles_deg"]), np.array(L["N"]), np.array(L["M"]))
    assert len(out) == 3
    top2, bottom2 = out[1]
    s = L["strain_top_of_ply2"]
    want = _expected_material_stress(L["angles_deg"][1], s["eps"])
    assert np.allclose(top2, want, rtol=0, atol=2e-3 * np.abs(want).max())
    assert not np.allclose(bottom2, top2, rtol=1e-3)  # bending: the two faces differ


def test_ply_stresses_bottom_of_ply_three_is_the_bottom_face():
    pl = plies(L["angles_deg"])
    N, M = np.array(L["N"]), np.array(L["M"])
    eps0, kappa = midplane_response(pl, N, M)
    h = L["t_ply"] * 3
    want = _expected_material_stress(L["angles_deg"][2], strain_at(eps0, kappa, h / 2))
    _, bottom3 = ply_stresses(pl, N, M)[2]
    assert np.allclose(bottom3, want, rtol=1e-9, atol=1e-9 * np.abs(want).max())


# Broken inputs: each must make the comparison FAIL (the tests pass by asserting the mismatch).
def test_broken_swapped_moduli_is_caught():
    A, _, _ = abd(plies(L["angles_deg"], E1=G["E2"], E2=G["E1"]))
    assert not printed_close(A, L["A"])


def test_broken_angle_sign_is_caught():
    A, _, _ = abd(plies([-a for a in L["angles_deg"]]))
    assert not printed_close(A, L["A"])


def test_broken_dropped_ply_is_caught():
    A, _, _ = abd(plies(L["angles_deg"][:2]))
    assert not printed_close(A, L["A"])
