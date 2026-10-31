"""Main-wing spar cap sizing (core.spar_sizing): hand checks, monotonicity, gates, weight, old adapter."""

import itertools
import math

import pytest

from config import config
from core import spar_sizing as ss
from core.simulation.fea_adapter import CompositeFEAAdapter

G = config.geometry
# literal hand-check material (the legacy uni-glass numbers, written out so the test owns them)
MAT = ss.CapMaterial(
    E1=5.5e6,
    E2=1.2e6,
    G12=0.6e6,
    nu12=0.28,
    F1t=150000.0,
    F1c=100000.0,
    F2t=5000.0,
    F2c=20000.0,
    F6=10000.0,
    f12_star=-0.5,
)


@pytest.fixture(scope="module")
def result():
    return ss.size_spar_caps()


# ---- 1. hand-calculation reference cases ---------------------------------------------------------------


def test_symmetric_two_cap_section_matches_closed_form():
    # depth 6.0, width 3.0, ply 0.0375, 4 plies each cap: cap 0.15 thick, centroids 2.925 off the axis
    sec = ss.cap_section(6.0, 3.0, 0.0375, 4, 4)
    i_own = 3.0 * 0.15**3 / 12  # 0.00084375
    area = 3.0 * 0.15  # 0.45
    d = (6.0 - 0.15) / 2  # 2.925
    I_hand = 2 * (i_own + area * d**2)  # 2 * (0.00084375 + 3.85003125) = 7.7017500
    assert I_hand == pytest.approx(7.70175, rel=1e-12)
    assert sec.I_in4 == pytest.approx(I_hand, rel=1e-12)
    assert sec.z_na == pytest.approx(0.0, abs=1e-12)
    assert sec.separation_in == pytest.approx(5.85, rel=1e-12)


def test_symmetric_stress_and_strength_ratio_match_closed_form():
    sec = ss.cap_section(6.0, 3.0, 0.0375, 4, 4)
    M = 100000.0
    sigma_hand = M * 3.0 / 7.70175  # M c / I, c = 3.0 = outer face = 38951.5 psi
    sigma, R = ss.section_response(sec, M, MAT)
    assert sigma == pytest.approx(sigma_hand, rel=1e-9)
    # top outer face in compression, sigma_1 = -38951.5, sigma_2 = tau = 0 (free edges, all 0 deg)
    f1 = 1 / 150000 - 1 / 100000
    f11 = 1 / (150000 * 100000)
    a = f11 * sigma_hand**2
    b = f1 * (-sigma_hand)
    R_c = (-b + math.sqrt(b * b + 4 * a)) / (
        2 * a
    )  # compression root, = 100000 / 38951.5
    b_t = f1 * sigma_hand
    R_t = (-b_t + math.sqrt(b_t * b_t + 4 * a)) / (2 * a)  # bottom outer face, tension
    assert R_c == pytest.approx(100000 / sigma_hand, rel=1e-9)
    assert R_t == pytest.approx(150000 / sigma_hand, rel=1e-9)
    assert R == pytest.approx(min(R_c, R_t), rel=1e-9)
    assert ss.margin_from_ratio(R) == pytest.approx(100000 / sigma_hand - 1, rel=1e-9)


def test_asymmetric_section_neutral_axis_by_hand():
    # depth 5, width 3, ply 0.05: top 2 plies (0.1), bottom 1 ply (0.05)
    sec = ss.cap_section(5.0, 3.0, 0.05, 2, 1)
    z_t, z_b = 2.5 - 0.05, -2.5 + 0.025  # 2.45, -2.475
    a_t, a_b = 0.3, 0.15
    z_na = (0.3 * 2.45 + 0.15 * -2.475) / 0.45  # 0.8083333
    I = (3 * 0.1**3 / 12 + a_t * (z_t - z_na) ** 2) + (
        3 * 0.05**3 / 12 + a_b * (z_b - z_na) ** 2
    )
    assert sec.z_na == pytest.approx(z_na, rel=1e-12)
    assert sec.I_in4 == pytest.approx(I, rel=1e-12)
    M = 20000.0
    sigma, _ = ss.section_response(sec, M, MAT)
    # the bottom face is furthest from the neutral axis: c = 2.5 + z_na
    assert sigma == pytest.approx(M * (2.5 + z_na) / I, rel=1e-9)


def test_elliptic_moment_closed_form():
    # root of an elliptic load: resultant L at 4 s / (3 pi)
    assert ss.elliptic_moment(0.0, 1000.0, 157.0) == pytest.approx(
        1000.0 * 4 * 157.0 / (3 * math.pi), rel=1e-12
    )
    assert ss.elliptic_moment(157.0, 1000.0, 157.0) == 0.0
    # numeric integral at a = 0.5 against the closed form
    s, L, y = 100.0, 1.0, 50.0
    n = 200000
    h = (s - y) / n
    num = sum(
        4
        * L
        / (math.pi * s)
        * math.sqrt(1 - ((y + (i + 0.5) * h) / s) ** 2)
        * (i + 0.5)
        * h
        * h
        for i in range(n)
    )
    assert ss.elliptic_moment(y, L, s) == pytest.approx(num, rel=1e-6)


# ---- 2. monotonicity ------------------------------------------------------------------------------------


@pytest.mark.parametrize("y", [23.0, 55.5, 106.25])
def test_more_plies_strictly_raise_the_margin(result, y):
    st = next(s for s in result.stations if s.y_in == y)
    t = G.spar_ply_thickness_laid_in
    margins = [
        ss.margin_from_ratio(
            ss.section_response(
                ss.cap_section(st.cap_depth_in, st.cap_width_in, t, n, n),
                st.moment_ultimate,
                ss.load_cap_material()[0],
            )[1]
        )
        for n in range(1, 13)
    ]
    assert all(b > a for a, b in itertools.pairwise(margins))


def test_solved_plies_meet_the_margin_and_one_fewer_does_not(result):
    mat = ss.load_cap_material()[0]
    t = G.spar_ply_thickness_laid_in
    for st in result.stations:
        assert st.margin >= result.required_margin
        if st.plies_solved > 1:
            sec = ss.cap_section(
                st.cap_depth_in,
                st.cap_width_in,
                t,
                st.plies_solved - 1,
                st.plies_solved - 1,
            )
            assert (
                ss.margin_from_ratio(
                    ss.section_response(sec, st.moment_ultimate, mat)[1]
                )
                < result.required_margin
            )


def test_solved_plies_do_not_increase_toward_the_tip(result):
    # asserted for the default stations, where the moment falls outboard faster than the depth
    ms = [s.moment_ultimate for s in result.stations]
    assert all(b < a for a, b in itertools.pairwise(ms))
    ns = [s.plies_solved for s in result.stations]
    assert all(b <= a for a, b in itertools.pairwise(ns))


# ---- 3. gates: each feeds a broken input and asserts rejection ------------------------------------------


def test_gate_unknown_citation_is_rejected():
    with pytest.raises(ValueError, match="unknown source id"):
        ss.Input("cap_width", 3.0, "in", ss.SOURCED, "nosuch-doc:p1")


def test_gate_missing_provenance_is_rejected():
    prov = dict(ss.GEOMETRY_PROVENANCE)
    del prov["wing_book_spar_cap_width_in"]
    with pytest.raises(ValueError, match="no provenance entry"):
        ss.size_spar_caps(provenance=prov)


def test_gate_unsourced_field_treated_as_sourced_is_rejected():
    prov = dict(ss.GEOMETRY_PROVENANCE)
    prov["wing_book_spar_cap_width_in"] = {
        "status": "unsourced",
        "source": "",
        "confidence": "n/a",
        "note": "",
    }
    with pytest.raises(ValueError, match="not sourced"):
        ss.size_spar_caps(provenance=prov)


@pytest.mark.parametrize(
    "args",
    [(6.0, -3.0, 0.0375, 2, 2), (6.0, 3.0, 0.0, 2, 2), (-6.0, 3.0, 0.0375, 2, 2)],
    ids=["width", "ply_thickness", "depth"],
)
def test_gate_non_positive_dimension_is_rejected(args):
    with pytest.raises(ValueError, match="must be positive"):
        ss.cap_section(*args)


@pytest.mark.parametrize("counts", [(0, 4), (4, 0), (-1, 4)])
def test_gate_ply_count_below_one_is_rejected(counts):
    with pytest.raises(ValueError, match=">= 1"):
        ss.cap_section(6.0, 3.0, 0.0375, *counts)


@pytest.mark.parametrize("y", [10.0, 157.5])
def test_gate_station_out_of_range_is_rejected(y):
    with pytest.raises(ValueError, match="outside the wing panel"):
        ss.size_spar_caps(stations=[23.0, y])


def test_gate_infeasible_requirement_is_rejected():
    with pytest.raises(ss.InfeasibleError):
        ss.solve_plies(5.0e7, 6.0, 3.0, 0.0375, MAT, 0.0)
    with pytest.raises(ss.InfeasibleError):
        ss.size_spar_caps(stations=[23.0], assumptions=ss.Assumptions(n_limit=400.0))


def _station(**kw):
    base = {
        "y_in": 50.0,
        "chord_in": 40.0,
        "cap_depth_in": 6.0,
        "cap_width_in": 3.0,
        "moment_limit": 1.0,
        "moment_ultimate": 1.5,
        "I_in4": 5.0,
        "sigma_psi": 1.0,
        "R": 2.0,
        "margin": 1.0,
        "margin_limit": 2.0,
        "plies_solved": 2,
        "plies_book_top": 7,
        "plies_book_bottom": 5,
        "R_book": 3.0,
        "margin_book": 2.0,
        "tributary_bl_in": 8.0,
        "mass_lb": 0.1,
        "mass_book_lb": 0.3,
    }
    base.update(kw)
    return ss.StationResult(**base)


def test_gate_wrong_margin_convention_is_rejected():
    _station()  # R - 1 everywhere: accepted
    # 1 - F style "margin" for R = 2 (F = 0.5) would be 0.5, not R - 1 = 1.0
    with pytest.raises(ValueError, match="not R - 1"):
        _station(margin=0.5)
    with pytest.raises(ValueError, match="not R - 1"):
        _station(margin_book=1.0 - 1.0 / 3.0)


@pytest.mark.parametrize("m", [-1.0, -2.0, math.inf, math.nan])
def test_gate_required_margin_outside_r_minus_one_range_is_rejected(m):
    with pytest.raises(ValueError, match="not an R - 1 margin"):
        ss.solve_plies(1.0e5, 6.0, 3.0, 0.0375, MAT, m)


# ---- 4. weight ------------------------------------------------------------------------------------------


def test_cap_mass_small_case_by_hand():
    # 4 strips (2 per cap) x 0.0375 thick x 3 wide x 0.072 lb/in3 x 10 in long = 0.324 lb
    assert ss.cap_mass_lb(4, 0.0375, 3.0, 0.072, 10.0) == pytest.approx(
        0.324, rel=1e-12
    )


def test_station_masses_use_the_station_increment_not_the_full_span():
    r = ss.size_spar_caps(stations=[23.0, 90.0, 157.0])
    trib = [s.tributary_bl_in for s in r.stations]
    assert trib == pytest.approx([33.5, 67.0, 33.5])  # sums to the 134 in panel, once
    cos_w = math.cos(math.radians(G.wing_book_shear_web_sweep_deg))
    t, w, rho = G.spar_ply_thickness_laid_in, G.wing_book_spar_cap_width_in, 0.072
    for s, dy in zip(r.stations, trib):
        assert s.mass_lb == pytest.approx(
            2 * s.plies_solved * t * w * rho * dy / cos_w, rel=1e-12
        )
        assert s.mass_book_lb == pytest.approx(
            (s.plies_book_top + s.plies_book_bottom) * t * w * rho * dy / cos_w,
            rel=1e-12,
        )
    extra_hand = sum(
        (
            max(0, s.plies_solved - s.plies_book_top)
            + max(0, s.plies_solved - s.plies_book_bottom)
        )
        * t
        * w
        * rho
        * dy
        / cos_w
        for s, dy in zip(r.stations, trib)
    )
    assert r.extra_ply_mass_lb == pytest.approx(extra_hand, rel=1e-12)
    assert (
        extra_hand > 0
    )  # the root station needs more than the book's 2/1 there, so this is not 0 = 0
    assert r.total_mass_solved_lb == pytest.approx(
        sum(s.mass_lb for s in r.stations), rel=1e-12
    )


# ---- 5. the old adapter no longer returns the saturated result ------------------------------------------


def test_analyze_spar_cap_is_no_longer_saturated(result):
    old = CompositeFEAAdapter().analyze_spar_cap()
    assert min(old.tsai_wu_margins) > -0.9  # was -0.995 on every inboard station
    assert 43 not in old.recommended_plies and max(old.recommended_plies) < 17
    assert old.weight_penalty_lb < 5.0  # was 121.39 lb
    assert max(old.max_stresses) < 2.0e5  # was 2.94e7 psi
    assert old.weight_penalty_lb == pytest.approx(result.extra_ply_mass_lb)
    assert old.recommended_plies == [s.plies_solved for s in result.stations]


def test_analyze_spar_cap_rejects_the_unsourced_legacy_loads():
    with pytest.raises(ValueError, match="retired"):
        CompositeFEAAdapter().analyze_spar_cap(tip_load_lbf=500.0)


# ---- inputs table ---------------------------------------------------------------------------------------


def test_every_input_row_is_cited_or_flagged(result):
    from core.sources import check_citation

    for row in (i.as_row() for i in result.inputs):
        if row["source"] == ss.UNSOURCED:
            continue
        check_citation(row["source"])
    for name in (
        "n_limit",
        "factor_of_safety",
        "wing_share",
        "density",
        "cap_F1c",
        "required_margin",
    ):
        assert name in result.unsourced
    for name in (
        "wing_book_spar_cap_width_in",
        "spar_ply_thickness_laid_in",
        "gross_weight_lb",
        "wing_cap_top_plies_in",
    ):
        assert name not in result.unsourced


def test_disclaimer_in_module_and_output(result):
    assert "NOT a certification or airworthiness substantiation" in ss.__doc__
    assert (
        "NOT a certification or airworthiness substantiation"
        in result.as_dict()["disclaimer"]
    )


def test_report_script_writes_only_where_told(tmp_path, capsys):
    import json
    import runpy

    mod = runpy.run_path(
        str(
            __import__("pathlib").Path(ss.__file__).parents[1]
            / "scripts"
            / "spar_sizing_report.py"
        )
    )
    out = tmp_path / "spar.json"
    assert mod["main"](["--out", str(out)]) == 0
    data = json.loads(out.read_text())
    assert data["margin_convention"].startswith("R - 1")
    assert len(data["stations"]) == len(ss.default_stations())
    assert "UNSOURCED" in capsys.readouterr().out
