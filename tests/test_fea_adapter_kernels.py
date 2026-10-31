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


def test_unknown_material_message_names_material_and_valid_names():
    ply = CompositePly("no_such_cloth", 0.01, 0.0)
    with pytest.raises(KeyError, match="no_such_cloth") as exc:
        _ = ply.properties
    msg = str(exc.value)
    valid = ", ".join(sorted(fea_adapter.MATERIAL_PROPERTIES))
    assert f"valid names: {valid}" in msg


def test_abd_is_the_kernel_abd(monkeypatch):
    """An inlined ABD sum never calls the kernel, so it cannot return this sentinel."""
    sentinel = (
        np.full((3, 3), 11.0),
        np.full((3, 3), 22.0),
        np.full((3, 3), 33.0),
    )

    def fake_abd(_plies):
        return sentinel

    monkeypatch.setattr(laminate, "abd", fake_abd)
    A, B, D = _section().abd_matrices()
    assert A is sentinel[0] and B is sentinel[1] and D is sentinel[2]


def test_tsai_wu_margin_is_strength_ratio_minus_one():
    sec = CompositeSection(plies=[CompositePly("uni", 0.009, 0.0)], width_in=1.0)
    sigma = np.array([60000.0, 1000.0, 2000.0])
    p = fea_adapter.UNI_GLASS_PROPERTIES
    R = tsai_wu_strength_ratio(
        sigma, p["F1t"], p["F1c"], p["F2t"], p["F2c"], p["F6"], -0.5
    )
    assert sec.tsai_wu_strength_ratio(sigma) == pytest.approx(R, rel=1e-12)
    assert sec.tsai_wu_margin(sigma) == pytest.approx(R - 1.0, rel=1e-12)
    assert sec.tsai_wu_strength_ratio(np.zeros(3)) == float("inf")
    assert sec.tsai_wu_margin(np.zeros(3)) == float("inf")


def test_dbox_tsai_wu_margins_are_strength_ratio_minus_one(monkeypatch):
    """D-box Tsai-Wu keys are kernel R - 1. The old 1 - F path never calls the kernel."""
    ratios = []
    real = fea_adapter.tsai_wu_strength_ratio

    def spy(sigma, *args, **kwargs):
        R = real(sigma, *args, **kwargs)
        ratios.append(R)
        return R

    monkeypatch.setattr(fea_adapter, "tsai_wu_strength_ratio", spy)
    out = fea_adapter.dbox_failure_checks(100.0, 450.0)
    assert ratios, "dbox Tsai-Wu margins must come from tsai_wu_strength_ratio"
    assert len(ratios) == 2
    assert math.isfinite(ratios[0]) and math.isfinite(ratios[1])
    assert out["dbox_spar_cap_tsai_wu_margin"] == pytest.approx(ratios[0] - 1.0)
    assert out["dbox_skin_tsai_wu_margin"] == pytest.approx(ratios[1] - 1.0)


def test_dbox_tsai_wu_margin_zero_stress_is_inf(monkeypatch):
    """Zero stress: kernel R is inf, and both D-box margins stay float('inf'), not 1."""
    seen = []
    real = fea_adapter.tsai_wu_strength_ratio

    def spy(sigma, *args, **kwargs):
        R = real(sigma, *args, **kwargs)
        seen.append((np.asarray(sigma, dtype=float).copy(), R))
        return R

    monkeypatch.setattr(fea_adapter, "tsai_wu_strength_ratio", spy)
    out = fea_adapter.dbox_failure_checks(100.0, 0.0)
    assert out["dbox_spar_cap_tsai_wu_margin"] == float("inf")
    assert out["dbox_skin_tsai_wu_margin"] == float("inf")
    assert len(seen) == 2
    for sigma, R in seen:
        assert np.all(sigma == 0.0)
        assert R == float("inf")


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
