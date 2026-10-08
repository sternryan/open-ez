"""M3.3 Report 45 criterion kernel (plan T10; vectors in vectors/flutter_r45.yaml, bounds in ledger row 79).

Kernel contract (core/kernels/flutter_r45.py, pure):
  Speed(value, unit, basis): frozen; unit "mph" or "kt", basis "IAS", "CAS", "EAS" or "TAS"; else ValueError.
  to_mph(speed) -> Speed in mph, same basis (1 kt = 1852/1609.344 mph).
  speeds_le(a, b) -> a <= b after unit conversion; ValueError when the bases differ.
  twist_per_unit_torque(GJ, ds) -> theta at each strip midpoint, cumulative from the centreline:
      sum of ds/GJ over the inboard strips plus half the strip's own (Report 45 p4: cumulative twist).
  wing_flexibility_factor(theta, chord, ds) -> sum theta c^2 ds (ds scalar or per strip).
  wing_limit(v_d_mph, limit_const) -> limit_const / v_d_mph^2.
  vd_max_cleared_mph(F, limit_const) -> sqrt(limit_const / F).
  wing_criterion(F, v_d, limit_const) -> {"passed", "F", "limit", "margin"} (margin = limit / F);
      v_d is a Speed and must be in mph (the criterion's unit), else ValueError.
  curve_limit(x, points) -> linear interpolation over (x, y) points; ValueError outside their range.
  aileron_ki_limit(v_d, points) -> curve_limit at v_d (a Speed in mph, else ValueError).
  balance_ratio(K, I) -> K / I.
  elevator_gamma(b, S_beta, I) -> b S_beta / I;  elevator_lambda(b, K, S, I) -> b K / (S I);
  flutter_speed_parameter(v_d, b, f_cpm) -> v_d / (b f_cpm), v_d a Speed in mph.
"""

from pathlib import Path

import numpy as np
import pytest
import yaml

pytest.importorskip(
    "core.kernels.flutter_r45", reason="M3.3 kernel body pending (plan T10)"
)

from core.kernels import flutter_r45 as r45
from core.sources import check_citation
from tests.kernels._vectors import load

V = load("flutter_r45.yaml")
W, A, H = V["ia100_wing"], V["ia100_aileron"], V["hand_uniform_wing"]
CRIT = yaml.safe_load(
    (Path(__file__).resolve().parents[2] / "data/criteria/report45.yaml").read_text()
)
LIMIT_CONST = CRIT["wing"]["limit_numerator"]["value"]  # 200, faa-report-45:p4
FIG2 = [(p["x"], p["y"]) for p in CRIT["aileron"]["fig2_points"]]
MPH_IAS = "IAS"


def mph(v, basis=MPH_IAS):
    return r45.Speed(v, "mph", basis)


def test_vector_cites_are_registered():
    for case in (W, A, H):
        if case["kind"] == "published":
            check_citation(case["cite"])


# ---- IA-100 published case ----------------------------------------------------------------


def ia100_F(theta=None):
    theta = W["theta"] if theta is None else theta
    return r45.wing_flexibility_factor(
        np.array(theta), np.array(W["chord_ft"]), W["ds_ft"]
    )


def test_ia100_strip_contributions_match_printed():
    for th, c, printed in zip(W["theta"], W["chord_ft"], W["dF_printed"]):
        d = r45.wing_flexibility_factor(np.array([th]), np.array([c]), W["ds_ft"])
        assert d == pytest.approx(printed, rel=W["bound"]["F_rel"])


def test_ia100_F_matches_printed():
    assert ia100_F() == pytest.approx(W["F_printed"], rel=W["bound"]["F_rel"])


def test_ia100_limit_matches_printed():
    lim = r45.wing_limit(W["v_d_mph"], LIMIT_CONST)
    assert abs(lim - W["limit_printed"]) <= W["bound"]["limit_half_unit"]


def test_ia100_passes_and_gj_over_four_fails_the_fixed_limit():
    ok = r45.wing_criterion(ia100_F(), mph(W["v_d_mph"]), LIMIT_CONST)
    assert ok["passed"] is True and ok["margin"] == pytest.approx(3.29, abs=0.01)
    k = V["ia100_wing"]["broken"]["gj_divisor"]
    broken = r45.wing_criterion(
        ia100_F([t * k for t in W["theta"]]), mph(W["v_d_mph"]), LIMIT_CONST
    )
    assert broken["passed"] is False


def test_ia100_vd_max():
    v = r45.vd_max_cleared_mph(W["F_printed"], LIMIT_CONST)
    assert v == pytest.approx((LIMIT_CONST / W["F_printed"]) ** 0.5, rel=1e-12)
    assert v > W["v_d_mph"]


def test_ia100_speed_conversion_matches_the_printed_pair():
    s = r45.to_mph(r45.Speed(W["v_d_kt"], "kt", "EAS"))
    assert s.unit == "mph" and s.basis == "EAS"
    assert round(s.value) in (W["v_d_mph"], W["v_d_mph"] + 1)  # 287.69, printed 287
    assert s.value == pytest.approx(W["v_d_kt"] * 1852 / 1609.344, rel=1e-12)


def test_ia100_aileron_balance_ratio_and_fig2_consistency():
    assert r45.balance_ratio(A["K_lbft2"], A["I_lbft2"]) == pytest.approx(
        A["KI_printed"], abs=0.05
    )
    lim = r45.aileron_ki_limit(mph(W["v_d_mph"]), FIG2)
    assert abs(lim - A["KI_limit_printed"]) <= A["consistency_abs"]
    assert (
        r45.balance_ratio(A["K_lbft2"], A["I_lbft2"]) > lim
    )  # unbalanced aileron fails


# ---- hand case: twist from GJ -------------------------------------------------------------


def test_twist_is_cumulative_from_the_centreline():
    th = r45.twist_per_unit_torque(np.full(5, H["GJ"]), np.array(H["ds"]))
    assert np.allclose(th, H["theta_mid"], rtol=1e-12)


def test_hand_wing_F_from_gj():
    th = r45.twist_per_unit_torque(np.full(5, H["GJ"]), np.array(H["ds"]))
    idx = H["aileron_strips"]
    F = r45.wing_flexibility_factor(
        th[idx], np.full(len(idx), H["chord"]), np.array(H["ds"])[idx]
    )
    assert F == pytest.approx(H["F"], rel=1e-12)


def test_broken_local_twist_is_not_cumulative_twist():  # the p4 trap: local twist per length
    th = r45.twist_per_unit_torque(np.full(5, H["GJ"]), np.array(H["ds"]))
    local = np.array(H["ds"]) / H["GJ"]
    assert not np.allclose(th, local)


def test_quartering_gj_quadruples_F():
    ds = np.array(H["ds"])
    f1 = r45.wing_flexibility_factor(
        r45.twist_per_unit_torque(np.full(5, H["GJ"]), ds), np.full(5, 3.0), ds
    )
    f4 = r45.wing_flexibility_factor(
        r45.twist_per_unit_torque(np.full(5, H["GJ"] / 4), ds), np.full(5, 3.0), ds
    )
    assert f4 == pytest.approx(4 * f1, rel=1e-12)


# ---- units, bases and curves --------------------------------------------------------------


def test_mixed_units_are_rejected():
    with pytest.raises(ValueError):
        r45.wing_criterion(ia100_F(), r45.Speed(250, "kt", "IAS"), LIMIT_CONST)
    with pytest.raises(ValueError):
        r45.aileron_ki_limit(r45.Speed(250, "kt", "IAS"), FIG2)
    with pytest.raises(ValueError):
        r45.flutter_speed_parameter(r45.Speed(250, "kt", "IAS"), 1.0, 1000.0)


def test_mixed_bases_are_rejected_and_units_convert():
    assert r45.speeds_le(r45.Speed(190, "kt", "IAS"), mph(220))
    assert not r45.speeds_le(r45.Speed(200, "kt", "IAS"), mph(220))
    with pytest.raises(ValueError):
        r45.speeds_le(r45.Speed(190, "kt", "IAS"), mph(220, "EAS"))


def test_bad_speed_labels_are_rejected():
    with pytest.raises(ValueError):
        r45.Speed(100, "km/h", "IAS")
    with pytest.raises(ValueError):
        r45.Speed(100, "mph", "GS")


def test_fig2_curve_reads_the_transcribed_points():
    assert r45.aileron_ki_limit(mph(150), FIG2) == pytest.approx(2.4, abs=1e-12)
    assert r45.aileron_ki_limit(mph(175), FIG2) == pytest.approx(2.0, abs=1e-12)
    with pytest.raises(ValueError):
        r45.aileron_ki_limit(mph(320), FIG2)


def test_elevator_parameters():
    assert r45.elevator_gamma(0.5, 2.0, 4.0) == pytest.approx(0.25)
    assert r45.elevator_lambda(0.5, 3.0, 6.0, 2.0) == pytest.approx(0.125)
    assert r45.flutter_speed_parameter(mph(200), 0.5, 2000.0) == pytest.approx(0.2)
