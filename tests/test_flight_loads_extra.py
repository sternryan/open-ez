"""Additional unit tests for core.flight_loads: parameter validation, invariants, V_D, cases, and provenance rows."""

import json
import math
from dataclasses import replace
from itertools import pairwise

import pytest

from config import config
from core import flight_loads as fl
from core.analysis import LiftSurfaceTerms, PhysicsEngine
from core.spar_sizing import elliptic_moment


@pytest.fixture(scope="module")
def eng():
    return PhysicsEngine()


@pytest.fixture(scope="module")
def lc(eng):
    return fl.wing_load_case(engine=eng)


def test_gust_load_factor_validates_every_parameter_and_non_positive_values():
    valid = (14.0, 161.0, 50.0, 4.5, 3.0, fl.RHO_SL_SLUG_FT3)
    labels = ("W/S", "V", "U_de", "lift slope", "chord", "density")
    for idx, label in enumerate(labels):
        for bad in (0.0, -1.0, math.nan, math.inf, -math.inf):
            args = list(valid)
            args[idx] = bad
            with pytest.raises(ValueError, match=f"{label} must be positive"):
                fl.gust_load_factor(*args)


def test_gust_load_factor_scaling_and_monotonicity_invariants():
    dn_base, kg_base = fl.gust_load_factor(14.0, 161.0, 50.0, 4.5, 3.0)
    assert 0.0 < kg_base < 0.88

    # K_g is independent of V and U_de; delta_n is strictly linear in both
    dn_2v, kg_2v = fl.gust_load_factor(14.0, 322.0, 50.0, 4.5, 3.0)
    dn_2u, kg_2u = fl.gust_load_factor(14.0, 161.0, 100.0, 4.5, 3.0)
    assert kg_2v == pytest.approx(kg_base, rel=1e-12)
    assert kg_2u == pytest.approx(kg_base, rel=1e-12)
    assert dn_2v == pytest.approx(2.0 * dn_base, rel=1e-12)
    assert dn_2u == pytest.approx(2.0 * dn_base, rel=1e-12)

    # Higher W/S raises mass ratio mu and K_g, while lowering delta_n
    dn_light, kg_light = fl.gust_load_factor(10.0, 161.0, 50.0, 4.5, 3.0)
    dn_heavy, kg_heavy = fl.gust_load_factor(20.0, 161.0, 50.0, 4.5, 3.0)
    assert kg_light < kg_base < kg_heavy < 0.88
    assert dn_light > dn_base > dn_heavy > 0.0

    # Smaller chord or lower air density increases mu, K_g, and delta_n
    dn_small_c, kg_small_c = fl.gust_load_factor(14.0, 161.0, 50.0, 4.5, 2.0)
    dn_large_c, kg_large_c = fl.gust_load_factor(14.0, 161.0, 50.0, 4.5, 4.0)
    assert kg_small_c > kg_base > kg_large_c
    assert dn_small_c > dn_base > dn_large_c

    dn_low_rho, kg_low_rho = fl.gust_load_factor(
        14.0, 161.0, 50.0, 4.5, 3.0, rho=0.5 * fl.RHO_SL_SLUG_FT3
    )
    assert kg_low_rho > kg_base
    assert dn_low_rho > dn_base


def test_schrenk_moment_rejects_invalid_chords_and_stations():
    for bad_c in (0.0, -5.0, math.nan):
        with pytest.raises(ValueError, match="chords must be positive"):
            fl.schrenk_moment(10.0, 1000.0, 157.0, bad_c, 20.0)
        with pytest.raises(ValueError, match="chords must be positive"):
            fl.schrenk_moment(10.0, 1000.0, 157.0, 55.0, bad_c)

    for bad_s in (0.0, -157.0):
        with pytest.raises(ValueError, match="semispan must be positive"):
            fl.schrenk_moment(0.0, 1000.0, bad_s, 55.0, 20.0)

    for bad_y in (-0.01, 157.01):
        with pytest.raises(ValueError, match="outside 0.."):
            fl.schrenk_moment(bad_y, 1000.0, 157.0, 55.0, 20.0)


def test_schrenk_moment_rectangular_planform_and_chord_scale_invariance():
    L, s, c = 1200.0, 157.0, 40.0
    for y in (0.0, 23.0, 55.5, 106.25, 157.0):
        m_uniform = L * (s - y) ** 2 / (2.0 * s)
        expected = 0.5 * (elliptic_moment(y, L, s) + m_uniform)
        assert fl.schrenk_moment(y, L, s, c, c) == pytest.approx(expected, rel=1e-12)

    # Multiplying both chords by a positive factor preserves taper ratio and bending moment
    c0 = config.geometry.wing_centerline_chord
    ct = config.geometry.wing_tip_chord
    for y in (0.0, 23.0, 75.0, 130.0):
        m_base = fl.schrenk_moment(y, L, s, c0, ct)
        for scale in (0.25, 2.0, 10.0):
            assert fl.schrenk_moment(y, L, s, scale * c0, scale * ct) == pytest.approx(
                m_base, rel=1e-12
            )


def test_schrenk_moment_linearity_in_lift_and_spanwise_monotonicity():
    s = config.geometry.wing_span / 2
    c0 = config.geometry.wing_centerline_chord
    ct = config.geometry.wing_tip_chord
    L = 1500.0

    stations = [0.0, 23.0, 55.5, 106.25, 140.0, s]
    moments = [fl.schrenk_moment(y, L, s, c0, ct) for y in stations]
    assert all(b < a for a, b in pairwise(moments))
    assert moments[-1] == pytest.approx(0.0, abs=1e-12)

    for y, m_pos in zip(stations[:-1], moments[:-1]):
        assert fl.schrenk_moment(y, 0.0, s, c0, ct) == pytest.approx(0.0, abs=1e-12)
        assert fl.schrenk_moment(y, -L, s, c0, ct) == pytest.approx(-m_pos, rel=1e-12)
        assert fl.schrenk_moment(y, 2.5 * L, s, c0, ct) == pytest.approx(
            2.5 * m_pos, rel=1e-12
        )

    # Taper (ct < c0) shifts the chordwise load centroid inboard relative to a rectangle
    assert fl.schrenk_moment(0.0, L, s, c0, ct) < fl.schrenk_moment(0.0, L, s, c0, c0)


def test_gate_wing_ac_not_aft_of_canard_ac_is_rejected(eng):
    base_terms = eng.lift_surface_terms()

    class _StubEngine:
        def __init__(self, terms):
            self._terms = terms

        def lift_surface_terms(self):
            return self._terms

    for bad_ac_wing in (base_terms.ac_canard_fs, base_terms.ac_canard_fs - 10.0):
        bad_terms = replace(base_terms, ac_wing_fs=bad_ac_wing)
        with pytest.raises(
            ValueError, match="wing aerodynamic centre must be aft of the canard's"
        ):
            fl.wing_load_case(engine=_StubEngine(bad_terms), vspaero_np_fs=100.0)


def test_gate_cg_at_or_forward_of_canard_ac_or_at_np_is_rejected(monkeypatch, eng, lc):
    t = eng.lift_surface_terms()
    x_np = t.ac_canard_fs + lc.share_np * (t.ac_wing_fs - t.ac_canard_fs)

    # CG at or forward of canard AC gives wing trim share <= 0
    for bad_fwd_cg in (t.ac_canard_fs, t.ac_canard_fs - 5.0):
        monkeypatch.setattr(fl, "CG_LIMITS_FS", (bad_fwd_cg, 103.0))
        with pytest.raises(ValueError, match="no stable trim"):
            fl.wing_load_case(engine=eng)

    # CG directly at the neutral point gives s == share_np, failing strict stability s < share_np
    monkeypatch.setattr(fl, "CG_LIMITS_FS", (97.0, x_np))
    with pytest.raises(ValueError, match="no stable trim"):
        fl.wing_load_case(engine=eng)


def test_vd_and_gust_load_factors_at_vc_and_vd(monkeypatch, eng, lc):
    t = eng.lift_surface_terms()
    s_tot = t.s_wing_sqft + t.s_canard_sqft
    w_s = lc.gross_lb / s_tot
    vc_min = 33.0 * math.sqrt(w_s)
    expected_vd = max(1.25 * fl.VC_KEAS, 1.5 * vc_min, fl.V_REDLINE_KIAS / 0.9)
    assert lc.v_d_keas == pytest.approx(expected_vd, rel=1e-12)
    assert lc.v_d_keas == pytest.approx(fl.V_REDLINE_KIAS / 0.9, rel=1e-12)

    g = config.geometry
    a_air = (t.wing_term + t.canard_term) / s_tot
    mgc_w = t.s_wing_sqft * 144.0 / g.wing_span / 12.0
    mgc_c = t.s_canard_sqft * 144.0 / g.canard_span / 12.0
    mgc = (t.s_wing_sqft * mgc_w + t.s_canard_sqft * mgc_c) / s_tot
    dn_vc_expected, _ = fl.gust_load_factor(w_s, fl.VC_KEAS, fl.U_DE_VC_FPS, a_air, mgc)
    dn_vd_expected, _ = fl.gust_load_factor(
        w_s, expected_vd, fl.U_DE_VD_FPS, a_air, mgc
    )
    assert lc.n_gust_vc == pytest.approx(1.0 + dn_vc_expected, rel=1e-12)
    assert lc.n_gust_vd == pytest.approx(1.0 + dn_vd_expected, rel=1e-12)

    # Identical W/S, chord, slope, and density at V_C and V_D -> delta_n ratio equals (U_de * V) ratio
    dn_vc = lc.n_gust_vc - 1.0
    dn_vd = lc.n_gust_vd - 1.0
    assert dn_vc > dn_vd > 0.0
    assert (dn_vd / dn_vc) == pytest.approx(
        (fl.U_DE_VD_FPS * lc.v_d_keas) / (fl.U_DE_VC_FPS * fl.VC_KEAS), rel=1e-12
    )

    # Raising V_C so 1.25 * V_C exceeds V_redline / 0.9 switches the governing V_D branch
    monkeypatch.setattr(fl, "VC_KEAS", 180.0)
    lc_high_vc = fl.wing_load_case(engine=eng)
    assert lc_high_vc.v_d_keas == pytest.approx(1.25 * 180.0, rel=1e-12)


def test_all_eight_load_cases_and_cg_directional_effects(lc):
    assert len(lc.cases) == 8
    dn_vc = lc.n_gust_vc - 1.0
    assert dn_vc > lc.n_gust_vd - 1.0
    w_min = fl.W_SAMPLE_EMPTY_LB + fl.W_SAMPLE_MIN_PILOT_LB

    for x, s in lc.share_cg.items():
        assert lc.cases[f"manoeuvre +{fl.N_UTILITY} g, CG {x:g}"] == pytest.approx(
            fl.N_UTILITY * s, rel=1e-12
        )
        assert lc.cases[
            f"manoeuvre -{fl.NEG_FACTOR * fl.N_UTILITY:g} g, CG {x:g}"
        ] == pytest.approx(-fl.NEG_FACTOR * fl.N_UTILITY * s, rel=1e-12)
        assert lc.cases[f"gust +, gross, CG {x:g}"] == pytest.approx(
            s + dn_vc * lc.share_np, rel=1e-12
        )
        assert lc.cases[
            f"gust -, light 1 g with gross gust, CG {x:g}"
        ] == pytest.approx(
            (w_min * s - lc.gross_lb * dn_vc * lc.share_np) / lc.gross_lb, rel=1e-12
        )

    # Aft CG (103) loads the wing more in positive cases; forward CG (97) has less 1 g relief in negative gust
    assert lc.cases["manoeuvre +4.4 g, CG 103"] > lc.cases["manoeuvre +4.4 g, CG 97"]
    assert lc.cases["gust +, gross, CG 103"] > lc.cases["gust +, gross, CG 97"]
    assert (
        lc.cases["gust -, light 1 g with gross gust, CG 97"]
        < lc.cases["gust -, light 1 g with gross gust, CG 103"]
    )
    assert lc.governing_pos == "gust +, gross, CG 103"
    assert lc.governing_neg == "gust -, light 1 g with gross gust, CG 97"
    assert lc.k_pos == pytest.approx(lc.cases[lc.governing_pos], rel=1e-12)
    assert lc.k_neg == pytest.approx(lc.cases[lc.governing_neg], rel=1e-12)
    assert lc.neg_over_pos == pytest.approx(lc.k_neg / lc.k_pos, rel=1e-12)
    assert -1.0 < lc.neg_over_pos < 0.0


def test_vd_gust_governs_when_dn_d_exceeds_dn_c_by_hand(monkeypatch):
    # Hard-coded scenario where V_D = 360 / 0.9 = 400 kt EAS and V_C = 140 kt EAS,
    # so U_de,d * V_D = 25 * 400 = 10000 > U_de,c * V_C = 50 * 140 = 7000 and dn_d > dn_c.
    terms = LiftSurfaceTerms(
        s_wing_sqft=80.0,
        s_canard_sqft=20.0,
        ac_wing_fs=125.0,
        ac_canard_fs=25.0,
        a_wing_per_rad=5.0,
        a_canard_per_rad=4.0,
        d_eps_dalpha=0.2,
        mac_wing_in=36.0,
    )

    class _StubEngine:
        def lift_surface_terms(self):
            return terms

    custom_cfg = replace(
        config,
        geometry=replace(config.geometry, wing_span=240.0, canard_span=120.0),
        flight_condition=replace(config.flight_condition, gross_weight_lb=1600.0),
    )
    monkeypatch.setattr(fl, "VC_KEAS", 140.0)
    monkeypatch.setattr(fl, "V_REDLINE_KIAS", 360.0)

    res = fl.wing_load_case(cfg=custom_cfg, engine=_StubEngine(), vspaero_np_fs=110.0)

    # Hand calculation:
    # S_tot = 100 sq ft, W/S = 16 psf, a_air = (320 + 80) / 100 = 4.0 /rad
    # mgc_w = 80 / 20 = 4.0 ft, mgc_c = 20 / 10 = 2.0 ft -> area-weighted mgc = 3.6 ft
    # mu = 32 / (0.0023769 * 3.6 * 4.0 * 32.174) = 29.058388205543652
    # K_g = 0.88 * mu / (5.3 + mu) = 0.7442543866134937
    # dn_c = K_g * 50 * 140 * 4.0 / (498 * 16) = 2.61535176018798
    # dn_d = K_g * 25 * 400 * 4.0 / (498 * 16) = 3.7362168002685426
    # share_np = (110 - 25) / 100 = 0.85; share_cg = {97: 0.72, 103: 0.78}
    dn_c_hand = 2.61535176018798
    dn_d_hand = 3.7362168002685426
    assert res.v_d_keas == pytest.approx(400.0, rel=1e-6)
    assert res.n_gust_vc == pytest.approx(1.0 + dn_c_hand, rel=1e-6)
    assert res.n_gust_vd == pytest.approx(1.0 + dn_d_hand, rel=1e-6)
    assert res.n_gust_vd > res.n_gust_vc

    # Governing gust cases must use dn_d (3.7362168002685426), not dn_c (2.61535176018798)
    k_pos_hand = 0.78 + dn_d_hand * 0.85  # 3.9557842802282613
    k_neg_hand = (
        865.0 * 0.72 - 1600.0 * dn_d_hand * 0.85
    ) / 1600.0  # -2.7865342802282613
    assert res.cases["gust +, gross, CG 103"] == pytest.approx(
        3.9557842802282613, rel=1e-6
    )
    assert res.cases["gust +, gross, CG 97"] == pytest.approx(
        3.8957842802282613, rel=1e-6
    )
    assert res.cases["gust -, light 1 g with gross gust, CG 97"] == pytest.approx(
        -2.7865342802282613, rel=1e-6
    )
    assert res.cases["gust -, light 1 g with gross gust, CG 103"] == pytest.approx(
        -2.7540967802282613, rel=1e-6
    )
    assert res.k_pos == pytest.approx(k_pos_hand, rel=1e-6)
    assert res.k_neg == pytest.approx(k_neg_hand, rel=1e-6)


def test_area_weighted_mgc_with_unequal_surface_areas_by_hand():
    # 9:1 area split: wing 90 sq ft over 15 ft span (mgc_w = 6.0 ft),
    # canard 10 sq ft over 5 ft span (mgc_c = 2.0 ft).
    # Area-weighted mgc = (90 * 6 + 10 * 2) / 100 = 5.6 ft (plain mean would be 4.0 ft).
    terms = LiftSurfaceTerms(
        s_wing_sqft=90.0,
        s_canard_sqft=10.0,
        ac_wing_fs=125.0,
        ac_canard_fs=25.0,
        a_wing_per_rad=5.0,
        a_canard_per_rad=4.0,
        d_eps_dalpha=0.2,
        mac_wing_in=72.0,
    )

    class _StubEngine:
        def lift_surface_terms(self):
            return terms

    custom_cfg = replace(
        config,
        geometry=replace(config.geometry, wing_span=180.0, canard_span=60.0),
        flight_condition=replace(config.flight_condition, gross_weight_lb=1600.0),
    )
    res = fl.wing_load_case(cfg=custom_cfg, engine=_StubEngine(), vspaero_np_fs=115.0)

    # Hand calculation for mgc = 5.6 ft, W/S = 16 psf, a_air = 4.0 /rad, V_C = 161 kt:
    # mu = 32 / (0.0023769 * 5.6 * 4.0 * 32.174) = 18.68039241784949
    # K_g = 0.88 * mu / (5.3 + mu) = 0.685507770317865
    # dn_c = K_g * 50 * 161 * 4.0 / (498 * 16) = 2.770249774627918
    # Plain mean mgc = 4.0 ft would instead give n_gust_vc = 3.956962666927966.
    by_name = {r.name: r for r in res.rows}
    assert "c 5.600 ft" in by_name["n_gust_vc"].note
    assert "K_g 0.6855" in by_name["n_gust_vc"].note
    assert "c 4.000 ft" not in by_name["n_gust_vc"].note
    assert res.n_gust_vc == pytest.approx(3.770249774627918, rel=1e-6)
    assert res.cases["gust +, gross, CG 103"] == pytest.approx(
        0.78 + 0.90 * 2.770249774627918, rel=1e-6
    )


def test_vspaero_np_override_monotonicity_and_json_consistency(eng):
    raw = json.loads(fl.VSPAERO_NP_JSON.read_text())
    assert fl._vspaero_np() == pytest.approx(float(raw["np_fs"]), rel=1e-6)

    np_analytic = eng.calculate_neutral_point()
    t = eng.lift_surface_terms()
    lc_analytic = fl.wing_load_case(engine=eng, vspaero_np_fs=np_analytic - 5.0)
    lc_aft = fl.wing_load_case(engine=eng, vspaero_np_fs=np_analytic + 5.0)

    assert lc_aft.share_np == pytest.approx(
        (np_analytic + 5.0 - t.ac_canard_fs) / (t.ac_wing_fs - t.ac_canard_fs),
        rel=1e-6,
    )
    assert lc_aft.share_np > lc_analytic.share_np
    assert lc_aft.share_cg == lc_analytic.share_cg
    assert lc_aft.k_pos > lc_analytic.k_pos
    assert lc_aft.k_neg < lc_analytic.k_neg


def test_wing_load_case_config_propagation_and_planform_fields(eng, lc):
    assert lc.gross_lb == pytest.approx(
        config.flight_condition.gross_weight_lb, rel=1e-6
    )
    assert lc.factor_of_safety == pytest.approx(fl.FACTOR_OF_SAFETY, rel=1e-6)
    assert lc.c_root_in == pytest.approx(
        config.geometry.wing_centerline_chord, rel=1e-6
    )
    assert lc.c_tip_in == pytest.approx(config.geometry.wing_tip_chord, rel=1e-6)

    heavier_cfg = replace(
        config,
        flight_condition=replace(config.flight_condition, gross_weight_lb=1400.0),
    )
    lc_heavy = fl.wing_load_case(cfg=heavier_cfg, engine=eng)
    assert lc_heavy.gross_lb == pytest.approx(1400.0, rel=1e-6)
    assert lc_heavy.n_gust_vc < lc.n_gust_vc
    assert lc_heavy.k_pos < lc.k_pos


def test_wing_load_case_rows_match_dataclass_fields_and_serialize(lc):
    names = [r.name for r in lc.rows]
    assert len(names) == 18
    assert len(set(names)) == len(names)

    by_name = {r.name: r for r in lc.rows}
    assert by_name["design_category"].value == "utility"
    assert by_name["n_limit_manoeuvre"].value == pytest.approx(fl.N_UTILITY, rel=1e-6)
    assert by_name["n_limit_negative_factor"].value == pytest.approx(
        fl.NEG_FACTOR, rel=1e-6
    )
    assert by_name["factor_of_safety"].value == pytest.approx(
        lc.factor_of_safety, rel=1e-6
    )
    assert by_name["u_de_vc"].value == pytest.approx(fl.U_DE_VC_FPS, rel=1e-6)
    assert by_name["u_de_vd"].value == pytest.approx(fl.U_DE_VD_FPS, rel=1e-6)
    assert by_name["v_c"].value == pytest.approx(fl.VC_KEAS, rel=1e-6)
    assert by_name["v_d"].value == pytest.approx(lc.v_d_keas, rel=1e-6)
    assert by_name["gross_weight_lb"].value == pytest.approx(lc.gross_lb, rel=1e-6)
    assert by_name["light_flight_weight_lb"].value == pytest.approx(
        fl.W_SAMPLE_EMPTY_LB + fl.W_SAMPLE_MIN_PILOT_LB, rel=1e-6
    )
    assert by_name["cg_limits_fs"].value == fl.CG_LIMITS_FS
    assert by_name["wing_share_trim"].value == {
        str(k): v for k, v in lc.share_cg.items()
    }
    assert by_name["wing_share_increment"].value == pytest.approx(lc.share_np, rel=1e-6)
    assert by_name["n_gust_vc"].value == pytest.approx(lc.n_gust_vc, rel=1e-6)
    assert by_name["wing_lift_factor_pos"].value == pytest.approx(lc.k_pos, rel=1e-6)
    assert by_name["wing_lift_factor_neg"].value == pytest.approx(lc.k_neg, rel=1e-6)
    assert lc.governing_pos in by_name["wing_lift_factor_pos"].note
    assert lc.governing_neg in by_name["wing_lift_factor_neg"].note

    for r in lc.rows:
        serialized = r.as_row()
        assert set(serialized.keys()) == {
            "name",
            "value",
            "unit",
            "status",
            "source",
            "also",
            "note",
        }
    assert by_name["cg_limits_fs"].as_row()["value"] == list(fl.CG_LIMITS_FS)
