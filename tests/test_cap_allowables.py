"""Cap design allowables (core.cap_allowables): hand checks, source consistency, gates."""

import math

import pytest

from core import cap_allowables as ca
from core.materials import get_material


def test_a_basis_by_hand():
    ratio = 2.3263478740408408 / 1.2815515655446004  # 1.8152...
    assert ca.a_basis_from_b(50.0, 45.0) == pytest.approx(50 - ratio * 5, rel=1e-12)


@pytest.mark.parametrize("mean,b", [(45.0, 50.0), (50.0, 0.0), (math.nan, 1.0)])
def test_gate_a_basis_rejects_bad_pairs(mean, b):
    with pytest.raises(ValueError):
        ca.a_basis_from_b(mean, b)


def test_wet_interpolation_by_hand():
    # RTW = 40 - (30 - 28) = 38; line from (70, 38) to (180, 28) at 140 F
    assert ca.mol_wet_value(40.0, 30.0, 28.0) == pytest.approx(
        38 - 10 * (70 - 140) / (70 - 180), rel=1e-12
    )
    # at the ends it returns the end values
    assert ca.mol_wet_value(40.0, 30.0, 28.0, t_mol=179.999999) == pytest.approx(
        28.0, rel=1e-6
    )


@pytest.mark.parametrize("t", [60.0, 70.0, 180.0, 200.0])
def test_gate_no_extrapolation_outside_the_tested_range(t):
    with pytest.raises(ValueError, match="extrapolation"):
        ca.mol_wet_value(40.0, 30.0, 28.0, t_mol=t)


def test_tabulated_means_match_the_cited_material_sets():
    wet = get_material("bgf7781_mgs418_wet")["properties"]
    pre = get_material("mtm45_7781")["properties"]
    assert ca.AGATE_114["tension"]["RTD"][0] * 1000 == pytest.approx(
        wet["F2t"]["value"]
    )
    assert ca.AGATE_114["compression"]["RTD"][0] * 1000 == pytest.approx(
        wet["F2c"]["value"]
    )
    assert ca.AGATE_114["shear"]["RTD"][0] * 1000 == pytest.approx(wet["F6"]["value"])
    assert ca.PREPREG_RTD_MEAN["tension"] * 1000 == pytest.approx(pre["F2t"]["value"])
    assert ca.PREPREG_RTD_MEAN["compression"] * 1000 == pytest.approx(
        pre["F2c"]["value"]
    )


def test_design_compression_by_hand():
    # 88473.0 psi x (51.77 / 68.96) x A-basis-wet-at-140 / 51.77
    r = 2.3263478740408408 / 1.2815515655446004
    a = {c: m - r * (m - b) for c, (m, b) in ca.AGATE_114["compression"].items()}
    rtw = a["RTD"] - (a["ETD"] - a["ETW"])
    a_mol = rtw - (rtw - a["ETW"]) * (70 - 140) / (70 - 180)
    hand = 88473.0 * (51.77 / 68.96) * (a_mol / 51.77)
    f1c = ca.design_allowables()["F1c"]
    assert f1c.value == pytest.approx(hand, rel=1e-12)
    assert 30000 < f1c.value < 40000


def test_strengths_are_knocked_down_and_moduli_are_not():
    al = ca.design_allowables()
    base = get_material(ca.BASE_SET)["properties"]
    for k in ca.STRENGTH_KINDS:
        assert al[k].value < base[k]["value"]
    for k in ca.MODULI:
        assert al[k].value == base[k]["value"]


def test_gate_unknown_strength_is_rejected():
    with pytest.raises(ValueError, match="not a strength"):
        ca.knockdown("E1")
