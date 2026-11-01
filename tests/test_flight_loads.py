"""Wing load case (core.flight_loads): hand checks of the 23.341 gust formula and Schrenk, the split, gates."""

import math

import pytest

from core import flight_loads as fl
from core.analysis import PhysicsEngine


@pytest.fixture(scope="module")
def lc():
    return fl.wing_load_case()


def test_gust_formula_by_hand():
    # W/S 14 psf, V 161 kt, U 50 ft/s, a 4.5 /rad, c 3.0 ft, sea level
    mu = 2 * 14 / (0.0023769 * 3.0 * 4.5 * 32.174)  # 27.137...
    kg = 0.88 * mu / (5.3 + mu)
    dn_hand = kg * 50 * 161 * 4.5 / (498 * 14)
    dn, k = fl.gust_load_factor(14.0, 161.0, 50.0, 4.5, 3.0)
    assert k == pytest.approx(kg, rel=1e-12)
    assert dn == pytest.approx(dn_hand, rel=1e-12)
    assert 4.0 < 1 + dn < 5.0


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
def test_gate_gust_formula_rejects_non_positive_input(bad):
    with pytest.raises(ValueError, match="must be positive"):
        fl.gust_load_factor(14.0, bad, 50.0, 4.5, 3.0)


def test_schrenk_root_and_tip_by_hand():
    L, s, c0, ct = 1000.0, 157.0, 55.0, 20.0
    m_ell = 4 * L * s / (3 * math.pi)
    m_chord = (
        L * s * (c0 + 2 * ct) / (3 * (c0 + ct))
    )  # resultant at the trapezoid centroid
    assert fl.schrenk_moment(0.0, L, s, c0, ct) == pytest.approx(
        0.5 * (m_ell + m_chord), rel=1e-12
    )
    assert fl.schrenk_moment(s, L, s, c0, ct) == pytest.approx(0.0, abs=1e-9)


def test_schrenk_mid_station_by_numerical_integration():
    from core.spar_sizing import elliptic_moment

    L, s, c0, ct, y0 = 1000.0, 157.0, 55.0, 20.0, 60.0
    area = s * (c0 + ct) / 2
    n = 200_000
    h = (s - y0) / n
    m_chord = 0.0
    for i in range(n):  # midpoint rule over the chord-shaped load
        y = y0 + (i + 0.5) * h
        m_chord += L * (c0 + (ct - c0) * y / s) / area * (y - y0) * h
    num = 0.5 * (elliptic_moment(y0, L, s) + m_chord)
    assert fl.schrenk_moment(y0, L, s, c0, ct) == pytest.approx(num, rel=1e-8)


def test_increment_share_is_the_neutral_point_share():
    eng = PhysicsEngine()
    t = eng.lift_surface_terms()
    lc0 = fl.wing_load_case(engine=eng, vspaero_np_fs=0.0)  # analytic NP only
    x_np = t.ac_canard_fs + lc0.share_np * (t.ac_wing_fs - t.ac_canard_fs)
    assert x_np == pytest.approx(eng.calculate_neutral_point(), rel=1e-12)


def test_more_aft_neutral_point_is_used(lc):
    t = PhysicsEngine().lift_surface_terms()
    x_np = t.ac_canard_fs + lc.share_np * (t.ac_wing_fs - t.ac_canard_fs)
    assert x_np == pytest.approx(
        max(PhysicsEngine().calculate_neutral_point(), fl._vspaero_np()), rel=1e-12
    )


def test_governing_cases_bound_every_case(lc):
    assert lc.k_pos == max(lc.cases.values())
    assert lc.k_neg == min(lc.cases.values())
    assert lc.k_pos > 0 > lc.k_neg


def test_trim_shares_by_hand(lc):
    t = PhysicsEngine().lift_surface_terms()
    for x, s in lc.share_cg.items():
        assert s == pytest.approx(
            (x - t.ac_canard_fs) / (t.ac_wing_fs - t.ac_canard_fs), rel=1e-12
        )
    assert lc.share_cg[103.0] > lc.share_cg[97.0]  # aft CG loads the wing more


def test_sea_level_vc_case_bounds_the_8000_ft_cruise(lc):
    # the manual's 161 kt is TRUE at 8000 ft; flown there it is a lower EAS, and despite the higher
    # mass ratio the gust increment is smaller than the sea-level case the model uses
    t = PhysicsEngine().lift_surface_terms()
    s_tot = t.s_wing_sqft + t.s_canard_sqft
    a = (t.wing_term + t.canard_term) / s_tot
    w_s = lc.gross_lb / s_tot
    sigma = (1 - 6.8756e-6 * 8000) ** 4.2559
    from config import config

    g = config.geometry
    c = (
        t.s_wing_sqft * (t.s_wing_sqft * 144 / g.wing_span / 12)
        + t.s_canard_sqft * (t.s_canard_sqft * 144 / g.canard_span / 12)
    ) / s_tot
    dn_alt, _ = fl.gust_load_factor(
        w_s, 161 * math.sqrt(sigma), 50.0, a, c, rho=0.0023769 * sigma
    )
    assert 1 + dn_alt < lc.n_gust_vc


def test_gate_cg_aft_of_the_neutral_point_is_rejected(monkeypatch):
    monkeypatch.setattr(fl, "CG_LIMITS_FS", (97.0, 125.0))
    with pytest.raises(ValueError, match="no stable trim"):
        fl.wing_load_case()


def test_gate_vc_below_the_part_23_floor_is_rejected(monkeypatch):
    monkeypatch.setattr(fl, "VC_KEAS", 60.0)
    with pytest.raises(ValueError, match="floor"):
        fl.wing_load_case()


def test_every_row_cited_or_an_assumption(lc):
    from core.inputs import ASSUMPTION, CITED

    for r in lc.rows:
        assert r.status in CITED or r.status == ASSUMPTION


def test_buckling_standard_cases_use_the_sourced_wing_lift_factors(lc):
    from core.simulation.fea_adapter import BucklingAnalyzer

    res = BucklingAnalyzer(6.0, 20.0, 0.03, 2.6e6).standard_load_cases()
    names = [r["load_case"] for r in res]
    assert names == [f"positive_{lc.k_pos:.3f}", f"negative_{-lc.k_neg:.3f}"]
    assert "positive_3.8g" not in names  # the retired unsourced case
