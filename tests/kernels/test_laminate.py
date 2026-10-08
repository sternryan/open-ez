"""M3.1 laminate kernel against Kaw's printed [30/-45/-60] example (vectors/clt_textbook.yaml)."""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.laminate",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.lamina import Ply
from core.kernels.laminate import abd, midplane_response, strain_at

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
