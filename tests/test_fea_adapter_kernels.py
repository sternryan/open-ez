"""fea_adapter's laminate and torsion classes delegate to core.kernels (Block 3 plan T8).

The legacy adapter carried its own Q-bar, ABD, Tsai-Wu and Bredt-Batho arithmetic, graded a
"margin" of 1 - F and fell back to UNI glass for an unknown material (Block 3 spec section 3).
These tests pin the adapter to the validated kernels instead.
"""

import math

import numpy as np
import pytest

from core.kernels import lamina, laminate, thinwall
from core.kernels.tsai_wu import tsai_wu_strength_ratio
from core.simulation import fea_adapter
from core.simulation.fea_adapter import (
    CompositeFEAAdapter,
    CompositePly,
    CompositeSection,
    TorsionSection,
)

# An unsymmetric mixed layup: B is non-zero and Poisson coupling is strong.
MIXED = [
    ("uni", 0.009, 0.0),
    ("bid", 0.013, 45.0),
    ("bid", 0.013, -45.0),
    ("uni", 0.009, 90.0),
]


def _section():
    return CompositeSection(
        plies=[CompositePly(m, t, a) for m, t, a in MIXED], width_in=2.0
    )


def _kernel_plies():
    out = []
    for m, t, a in MIXED:
        p = fea_adapter.MATERIAL_PROPERTIES[m]
        out.append(lamina.Ply(p["E1"], p["E2"], p["G12"], p["nu12"], t, a))
    return out


def test_unknown_material_raises():
    ply = CompositePly("no_such_cloth", 0.01, 0.0)
    with pytest.raises(KeyError, match="no_such_cloth"):
        _ = ply.properties


def test_abd_is_the_kernel_abd():
    A, B, D = _section().abd_matrices()
    kA, kB, kD = laminate.abd(_kernel_plies())
    np.testing.assert_allclose(A, kA, rtol=1e-12)
    np.testing.assert_allclose(B, kB, rtol=1e-12, atol=1e-9)
    np.testing.assert_allclose(D, kD, rtol=1e-12)


def test_tsai_wu_margin_is_strength_ratio_minus_one():
    sec = CompositeSection(plies=[CompositePly("uni", 0.009, 0.0)], width_in=1.0)
    sigma = np.array([60000.0, 1000.0, 2000.0])
    p = fea_adapter.UNI_GLASS_PROPERTIES
    R = tsai_wu_strength_ratio(
        sigma, p["F1t"], p["F1c"], p["F2t"], p["F2c"], p["F6"], -0.5
    )
    assert sec.tsai_wu_strength_ratio(sigma) == pytest.approx(R, rel=1e-12)
    assert sec.tsai_wu_margin(sigma) == pytest.approx(R - 1.0, rel=1e-12)


def test_ply_by_ply_uses_full_abd_response():
    moment = 500.0
    sec = _section()
    rows = CompositeFEAAdapter().analyze_ply_by_ply(moment, section=sec)
    plies = _kernel_plies()
    eps0, kappa = laminate.midplane_response(
        plies, np.zeros(3), np.array([moment / sec.width_in, 0.0, 0.0])
    )
    assert len(rows) == len(plies)
    for row, p in zip(rows, plies):
        Qb = lamina.transformed_stiffness(
            lamina.reduced_stiffness(p.E1, p.E2, p.G12, p.nu12), p.theta_deg
        )
        s = lamina.stress_to_material(
            Qb @ laminate.strain_at(eps0, kappa, row["z_position"]), p.theta_deg
        )
        np.testing.assert_allclose(
            [row["sigma_1"], row["sigma_2"], row["tau_12"]], s, rtol=1e-9, atol=1e-6
        )
        props = fea_adapter.MATERIAL_PROPERTIES[MIXED[row["ply_index"]][0]]
        R = tsai_wu_strength_ratio(
            s, props["F1t"], props["F1c"], props["F2t"], props["F2c"], props["F6"], -0.5
        )
        assert row["tsai_wu_strength_ratio"] == pytest.approx(R, rel=1e-9)
        assert row["tsai_wu_margin"] == pytest.approx(R - 1.0, rel=1e-9)


def test_torsion_gj_goes_through_the_multicell_kernel(monkeypatch):
    calls = []

    def spy(walls, cells):
        calls.append((walls, cells))
        return thinwall.multicell_torsion(walls, cells)

    monkeypatch.setattr(fea_adapter, "multicell_torsion", spy, raising=True)
    sec = TorsionSection(
        enclosed_area_sq_in=50.0,
        perimeter_segments=[(10.0, 0.05), (5.0, 0.05), (10.0, 0.05), (5.0, 0.05)],
        shear_modulus_psi=1.0e6,
    )
    assert sec.gj == pytest.approx(4 * 50**2 * 1e6 / 600, rel=1e-12)
    assert len(calls) == 1
    walls, cells = calls[0]
    assert len(walls) == 4 and len(cells) == 1
    assert math.isclose(cells[0].area, 50.0)
