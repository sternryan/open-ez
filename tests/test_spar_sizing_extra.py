"""Additional unit tests for core.spar_sizing covering untested functions, branches, boundaries and invariants."""

import math
from itertools import pairwise

import numpy as np
import pytest

from config import config
from core import spar_sizing as ss

G = config.geometry

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


def test_module_constants_and_assumptions_defaults_and_override():
    assert ss.CAP_MATERIAL == "cap_allowables"
    assert ss._MAT_KEYS == (
        "E1",
        "E2",
        "G12",
        "nu12",
        "F1t",
        "F1c",
        "F2t",
        "F2c",
        "F6",
    )
    assert ss.MATERIALS_YAML.name == "materials.yaml"
    assert ss.MATERIALS_YAML.is_file()

    asm = ss.Assumptions()
    assert asm.density_lb_in3 == 0.072
    assert asm.f12_star == -0.5
    assert asm.required_margin == 0.0
    assert asm.load_scale == 1.0
    base_rows = {r.name: r for r in asm.rows()}
    assert list(base_rows) == ["density", "f12_star", "required_margin"]
    assert base_rows["density"].status == ss.ASSUMPTION
    assert base_rows["f12_star"].status == ss.SOURCED
    assert base_rows["required_margin"].status == ss.SOURCED

    asm_scaled = ss.Assumptions(load_scale=1.25)
    scaled_rows = {r.name: r for r in asm_scaled.rows()}
    assert list(scaled_rows) == ["density", "f12_star", "required_margin", "load_scale"]
    assert scaled_rows["load_scale"].value == 1.25
    assert scaled_rows["load_scale"].unit == "1"
    assert scaled_rows["load_scale"].status == ss.UNSOURCED
    assert scaled_rows["load_scale"].source is None

    r_base = ss.size_spar_caps(stations=[106.25, 157.0])
    r_scaled = ss.size_spar_caps(stations=[106.25, 157.0], assumptions=asm_scaled)
    assert "load_scale" not in r_base.unsourced
    assert "load_scale" in r_scaled.unsourced
    assert r_scaled.stations[0].moment_ultimate == pytest.approx(
        1.25 * r_base.stations[0].moment_ultimate, rel=1e-12
    )
    assert r_scaled.stations[0].moment_ultimate_neg == pytest.approx(
        1.25 * r_base.stations[0].moment_ultimate_neg, rel=1e-12
    )


def test_geometry_input_sourced_unsourced_and_note_precedence():
    inp_default = ss.geometry_input("wing_book_thickness_pct", "% chord")
    assert inp_default.name == "wing_book_thickness_pct"
    assert inp_default.value == (16.2, 15.7, 15.0)
    assert inp_default.unit == "% chord"
    assert inp_default.status == ss.SOURCED
    assert inp_default.source.startswith("plans-1980:p126")
    assert (
        inp_default.note == "the 16.2 trailing glyph is smeared; the others are clear"
    )

    inp_override = ss.geometry_input(
        "wing_book_thickness_pct", "% chord", note="explicit note wins"
    )
    assert inp_override.note == "explicit note wins"

    with pytest.raises(ValueError, match="no provenance entry"):
        ss.geometry_input("nonexistent_geometry_field", "in")

    with pytest.raises(ValueError, match="not sourced"):
        ss.geometry_input("wing_washout", "deg", require_sourced=True)

    inp_unsourced = ss.geometry_input(
        "wing_washout", "deg", require_sourced=False, note="allowed for test"
    )
    assert inp_unsourced.name == "wing_washout"
    assert inp_unsourced.value == 1.0
    assert inp_unsourced.unit == "deg"
    assert inp_unsourced.status == ss.UNSOURCED
    assert inp_unsourced.source is None
    assert inp_unsourced.note == "provenance unsourced; allowed for test"


def test_cap_section_sign_conventions_symmetry_and_exact_depth_boundary():
    # Top-heavy section: depth=4.0, width=2.0, t=0.25, n_top=3 (tt=0.75), n_bot=1 (tb=0.25)
    # z_top_c = 2.0 - 0.375 = +1.625, z_bot_c = -2.0 + 0.125 = -1.875
    # a_t = 1.5, a_b = 0.5 -> z_na = (1.5*1.625 + 0.5*-1.875) / 2.0 = +0.75
    # I_na = (2*0.75^3/12 + 1.5*0.875^2) + (2*0.25^3/12 + 0.5*(-2.625)^2) = 14/3 = 4.666666666666667
    sec_top = ss.cap_section(4.0, 2.0, 0.25, 3, 1)
    assert sec_top.z_top_c == pytest.approx(1.625, rel=1e-12)
    assert sec_top.z_bot_c == pytest.approx(-1.875, rel=1e-12)
    assert sec_top.z_na == pytest.approx(0.75, rel=1e-12)
    assert sec_top.z_top_c > sec_top.z_na > 0.0 > sec_top.z_bot_c
    assert sec_top.separation_in == pytest.approx(3.5, rel=1e-12)
    assert sec_top.I_in4 == pytest.approx(14.0 / 3.0, rel=1e-12)

    # Bottom-heavy section (also checking np.integer acceptance): z_na flips sign to -0.75
    sec_bot = ss.cap_section(4.0, 2.0, 0.25, np.int64(1), np.int64(3))
    assert type(sec_bot.n_top) is int and type(sec_bot.n_bot) is int
    assert sec_bot.z_top_c == pytest.approx(1.875, rel=1e-12)
    assert sec_bot.z_bot_c == pytest.approx(-1.625, rel=1e-12)
    assert sec_bot.z_na == pytest.approx(-0.75, rel=1e-12)
    assert sec_bot.z_top_c > 0.0 > sec_bot.z_na > sec_bot.z_bot_c
    assert sec_bot.separation_in == pytest.approx(3.5, rel=1e-12)
    assert sec_bot.I_in4 == pytest.approx(14.0 / 3.0, rel=1e-12)

    # Exact-fit boundary on tt + tb >= depth_in: 0.5 + 0.5 == 1.0 is rejected, 0.5 + 0.25 == 0.75 < 1.0 passes
    with pytest.raises(ValueError, match="fill the depth"):
        ss.cap_section(1.0, 2.0, 0.25, 2, 2)
    with pytest.raises(ValueError, match="fill the depth"):
        ss.cap_section(1.0, 2.0, 0.25, 3, 2)
    sec_fit = ss.cap_section(1.0, 2.0, 0.25, 2, 1)
    assert sec_fit.separation_in == pytest.approx(0.625, rel=1e-12)

    # _check_count rejects booleans, floats, and strings with TypeError
    for bad_count in (True, False, 2.0, "2"):
        with pytest.raises(TypeError, match="must be an integer"):
            ss.cap_section(4.0, 2.0, 0.25, bad_count, 1)
        with pytest.raises(TypeError, match="must be an integer"):
            ss.cap_section(4.0, 2.0, 0.25, 1, bad_count)


def test_section_response_branches_and_moment_sign_asymmetry():
    # Section with n_top=3, n_bot=1 (depth=4, width=2, t=0.25): z_na = +0.75, I = 14/3
    # Outer fiber distances: c_top = 2.0 - 0.75 = 1.25 in, c_bot = 2.0 + 0.75 = 2.75 in
    # At M = +14000 in-lbf, M / I = 3000 psi/in -> st = 3750 psi (compression), sb = 8250 psi (tension)
    sec_top_heavy = ss.cap_section(4.0, 2.0, 0.25, 3, 1)
    sigma_pos, r_pos = ss.section_response(sec_top_heavy, 14000.0, MAT)
    # Bottom cap wins max(st, sb) = 8250 psi and min(rt, rb) = min(100000/3750, 150000/8250) = 200/11
    assert sigma_pos == pytest.approx(8250.0, rel=1e-6)
    assert r_pos == pytest.approx(200.0 / 11.0, rel=1e-6)

    # Flipping the sign of M to -14000 in-lbf puts the higher-stressed bottom cap in compression (F1c=100000)
    # and the top cap in tension (F1t=150000): R drops from 200/11 (18.181818) to 100000/8250 = 400/33 (12.121212)
    sigma_neg, r_neg = ss.section_response(sec_top_heavy, -14000.0, MAT)
    assert sigma_neg == pytest.approx(8250.0, rel=1e-6)
    assert r_neg == pytest.approx(400.0 / 33.0, rel=1e-6)
    assert r_neg < r_pos

    # Section with n_top=1, n_bot=3: z_na = -0.75, c_top = 2.75 in, c_bot = 1.25 in
    # Under M = +14000 in-lbf, top cap wins both max(st, sb) = 8250 psi and min(rt, rb) = 100000/8250 = 400/33
    sec_bot_heavy = ss.cap_section(4.0, 2.0, 0.25, 1, 3)
    sigma_bh, r_bh = ss.section_response(sec_bot_heavy, 14000.0, MAT)
    assert sigma_bh == pytest.approx(8250.0, rel=1e-6)
    assert r_bh == pytest.approx(400.0 / 33.0, rel=1e-6)

    # Zero moment gives zero stress and infinite strength ratio
    sigma_zero, r_zero = ss.section_response(sec_top_heavy, 0.0, MAT)
    assert sigma_zero == 0.0
    assert math.isinf(r_zero) and r_zero > 0


def test_max_plies_exact_boundaries_and_shallow_depth():
    # Exact multiple: depth / (2*t) = 1.0 / (2*0.125) = 4.0 -> 2*4*0.125 == 1.0 fills depth, so max_plies is 3
    assert ss.max_plies(1.0, 0.125) == 3
    ss.cap_section(1.0, 2.0, 0.125, 3, 3)
    with pytest.raises(ValueError, match="fill the depth"):
        ss.cap_section(1.0, 2.0, 0.125, 4, 4)

    # Strictly above the multiple: 1.0625 / 0.25 = 4.25 -> floor is 4 and 2*4*0.125 = 1.0 < 1.0625
    assert ss.max_plies(1.0625, 0.125) == 4
    ss.cap_section(1.0625, 2.0, 0.125, 4, 4)

    # Depth too shallow for even 1 ply per cap (2 * 1 * 0.125 >= depth)
    assert ss.max_plies(0.25, 0.125) == 0
    assert ss.max_plies(0.2, 0.125) == 0


def test_governing_response_and_solve_plies_exact_boundary_and_branches():
    sec_asym = ss.cap_section(4.0, 2.0, 0.25, 3, 1)

    with pytest.raises(ValueError, match="no moment given"):
        ss.governing_response(sec_asym, [], MAT)
    with pytest.raises(ValueError, match="no moment given"):
        ss.solve_plies([], 4.0, 2.0, 0.25, MAT)

    # Scalar moment vs sequence where index 0 wins vs index 1 wins vs tie (index 0 kept)
    sg0, r0, idx0 = ss.governing_response(sec_asym, 14000.0, MAT)
    assert idx0 == 0
    assert sg0 == pytest.approx(8250.0, rel=1e-6)
    assert r0 == pytest.approx(200.0 / 11.0, rel=1e-6)

    _, r_win0, idx_win0 = ss.governing_response(sec_asym, (28000.0, -14000.0), MAT)
    assert idx_win0 == 0
    assert r_win0 == pytest.approx(100.0 / 11.0, rel=1e-6)

    _, r_win1, idx_win1 = ss.governing_response(sec_asym, (14000.0, -14000.0), MAT)
    assert idx_win1 == 1
    assert r_win1 == pytest.approx(400.0 / 33.0, rel=1e-6)

    _, _, idx_tie = ss.governing_response(sec_asym, (14000.0, 14000.0), MAT)
    assert idx_tie == 0

    # Exact binary floating-point boundary for margin(n) >= required_margin in solve_plies:
    # depth=4.0, width=3.0, t=0.5, n=1 -> z_t=1.75, a_t=1.5, I = 2*(3*0.125/12 + 1.5*1.75^2) = 9.25 exact
    # M = 4625.0 -> M/I = 500.0 -> outer fiber c=2.0 has sigma = 1000.0 psi exact
    # With F1t=F1c=2000.0 and nu12=0.0, R = 2000.0 / 1000.0 = 2.0 exact -> margin = 1.0 exact
    mat_exact = ss.CapMaterial(
        E1=4.0e6,
        E2=1.0e6,
        G12=0.5e6,
        nu12=0.0,
        F1t=2000.0,
        F1c=2000.0,
        F2t=1000.0,
        F2c=1000.0,
        F6=1000.0,
        f12_star=-0.5,
    )
    sec_1 = ss.cap_section(4.0, 3.0, 0.5, 1, 1)
    assert sec_1.I_in4 == 9.25
    sigma_1, r_1 = ss.section_response(sec_1, 4625.0, mat_exact)
    assert sigma_1 == 1000.0
    assert r_1 == 2.0
    assert ss.margin_from_ratio(r_1) == 1.0
    assert ss.solve_plies(4625.0, 4.0, 3.0, 0.5, mat_exact, required_margin=1.0) == 1
    assert (
        ss.solve_plies(4625.0, 4.0, 3.0, 0.5, mat_exact, required_margin=1.000001) == 2
    )

    # Valid negative required_margin (-1.0 < m < 0.0): at M=18500.0, sigma=4000.0, R=0.5, margin=-0.5 exact
    assert ss._check_required_margin(-0.9999) is None
    assert ss.solve_plies(18500.0, 4.0, 3.0, 0.5, mat_exact, required_margin=-0.5) == 1
    assert (
        ss.solve_plies(18500.0, 4.0, 3.0, 0.5, mat_exact, required_margin=-0.4999) == 2
    )

    # _check_required_margin boundary: m == -1.0, m = -1.0001, nan, and +/-inf all raise ValueError
    for bad_m in (-1.0, -1.0001, math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError, match="not an R - 1 margin"):
            ss._check_required_margin(bad_m)
        with pytest.raises(ValueError, match="not an R - 1 margin"):
            ss.solve_plies(18500.0, 4.0, 3.0, 0.5, mat_exact, required_margin=bad_m)

    # Infeasible when hi < 1 (depth too shallow to fit 1 ply per cap)
    with pytest.raises(ss.InfeasibleError):
        ss.solve_plies(10.0, 0.25, 3.0, 0.125, mat_exact, required_margin=0.0)


def test_elliptic_moment_validation_boundaries_and_sign():
    for bad_s in (0.0, -50.0):
        with pytest.raises(ValueError, match="semispan must be positive"):
            ss.elliptic_moment(0.0, 100.0, bad_s)
    for bad_y in (-0.001, 100.001):
        with pytest.raises(ValueError, match="outside 0..100.0"):
            ss.elliptic_moment(bad_y, 100.0, 100.0)

    # Exact closed-form at a = 0.5 (y=50, L=300, s=100):
    # bracket = (3/4)^1.5 / 3 - 0.5*(pi/4 - (0.5*sqrt(3)/2 + pi/6)/2) = 3*sqrt(3)/16 - pi/12
    expected_m = (4.0 * 300.0 * 100.0 / math.pi) * (
        3.0 * math.sqrt(3.0) / 16.0 - math.pi / 12.0
    )
    m_pos = ss.elliptic_moment(50.0, 300.0, 100.0)
    m_neg = ss.elliptic_moment(50.0, -300.0, 100.0)
    assert m_pos == pytest.approx(expected_m, rel=1e-12)
    assert m_neg == pytest.approx(-expected_m, rel=1e-12)
    assert m_pos > 0.0 > m_neg


def test_load_cap_material_and_design_cap_material_by_hand():
    mat_kaw, rows_kaw = ss.load_cap_material("glass_epoxy_ud_kaw", f12_star=-0.25)
    assert mat_kaw.E1 == pytest.approx(5598456.7, rel=1e-9)
    assert mat_kaw.E2 == pytest.approx(1199462.1, rel=1e-9)
    assert mat_kaw.G12 == pytest.approx(600456.2, rel=1e-9)
    assert mat_kaw.nu12 == pytest.approx(0.26, rel=1e-9)
    assert mat_kaw.F1t == pytest.approx(154030.1, rel=1e-9)
    assert mat_kaw.F1c == pytest.approx(88473.0, rel=1e-9)
    assert mat_kaw.F2t == pytest.approx(4496.2, rel=1e-9)
    assert mat_kaw.F2c == pytest.approx(17114.5, rel=1e-9)
    assert mat_kaw.F6 == pytest.approx(10442.7, rel=1e-9)
    assert mat_kaw.f12_star == -0.25
    assert [r.name for r in rows_kaw] == [f"cap_{k}" for k in ss._MAT_KEYS]
    assert all(r.status == ss.SOURCED for r in rows_kaw)

    mat_leg, rows_leg = ss.load_cap_material("legacy_uni_glass")
    assert mat_leg.E1 == 5.5e6
    assert mat_leg.F1t == 150000.0
    assert mat_leg.F1c == 100000.0
    assert mat_leg.f12_star == -0.5
    assert all(r.status == ss.UNSOURCED and r.source is None for r in rows_leg)
    assert all("data/materials.yaml legacy_uni_glass:" in r.note for r in rows_leg)

    with pytest.raises(ValueError, match="unknown material"):
        ss.load_cap_material("no_such_material")
    with pytest.raises(ValueError, match="bgf7781_mgs418_wet.E1 has no value"):
        ss.load_cap_material("bgf7781_mgs418_wet")

    # First-principles check of design_cap_material allowables from Kaw base + AGATE 114 / NCAMP knockdowns at 140 F:
    z_ratio = 2.3263478740408408 / 1.2815515655446004
    a_rtd_c = 51.77 - z_ratio * (51.77 - 45.11)
    a_etd_c = 31.45 - z_ratio * (31.45 - 27.41)
    a_etw_c = 29.10 - z_ratio * (29.10 - 25.35)
    rtw_c = a_rtd_c - (a_etd_c - a_etw_c)
    a_mol_c = rtw_c - (rtw_c - a_etw_c) * (70.0 - 140.0) / (70.0 - 180.0)
    expected_f1c = 88473.0 * ((51.77 / 68.96) * (a_mol_c / 51.77))

    a_rtd_t = 48.99 - z_ratio * (48.99 - 41.85)
    a_etd_t = 42.21 - z_ratio * (42.21 - 36.06)
    a_etw_t = 36.34 - z_ratio * (36.34 - 31.05)
    rtw_t = a_rtd_t - (a_etd_t - a_etw_t)
    a_mol_t = rtw_t - (rtw_t - a_etw_t) * (70.0 - 140.0) / (70.0 - 180.0)
    expected_f1t = 154030.1 * ((48.99 / 61.58) * (a_mol_t / 48.99))

    mat_des, rows_des = ss.design_cap_material(f12_star=-0.4)
    assert mat_des.f12_star == -0.4
    assert mat_des.E1 == pytest.approx(5598456.7, rel=1e-9)
    assert mat_des.F1c == pytest.approx(expected_f1c, rel=1e-12)
    assert mat_des.F1t == pytest.approx(expected_f1t, rel=1e-12)
    des_by_name = {r.name: r for r in rows_des}
    assert des_by_name["cap_E1"].status == ss.SOURCED
    assert des_by_name["cap_E1"].also == ()
    assert des_by_name["cap_F1c"].status == ss.DERIVED
    assert len(des_by_name["cap_F1c"].also) == 7


def test_default_stations_and_book_plies_schedule_by_hand():
    stns = ss.default_stations()
    assert len(stns) == 17
    # Bay 1 (23.0 to 55.5, span 32.5): ceil(32.5/8.5) = 4 steps of 8.125 in
    assert stns[:5] == [23.0, 31.125, 39.25, 47.375, 55.5]
    # Bay 2 (55.5 to 106.25, span 50.75) and Bay 3 (106.25 to 157.0, span 50.75): 6 steps each of 8.458333 in
    assert stns[10] == 106.25
    assert stns[-1] == 157.0
    assert all(0.0 < b - a <= 8.5 for a, b in pairwise(stns))

    # Chapter 19 ply spans along the 18.42 deg web line (cos 18.42 deg = 0.9487644):
    # BL 23.0 (root): only zero-offset plies cover the root -> 2 top, 1 bottom
    assert ss.book_plies(23.0) == (2, 1)
    # BL 30.0: top ply 3 starts at 28.693, bottom ply 2 starts at 27.744 -> 3 top, 2 bottom
    assert ss.book_plies(30.0) == (3, 2)
    # BL 55.0: all 7 top plies (ply 7 covers 51.463..70.438) and all 5 bottom plies (47.668..66.169) active
    assert ss.book_plies(55.0) == (7, 5)
    # Bottom ply 2 (off=5, ln=135) ends at 23 + 140*cos(18.42) = 155.827 in
    assert ss.book_plies(155.0) == (2, 2)
    assert ss.book_plies(156.0) == (2, 1)
    assert ss.book_plies(157.0) == (2, 1)
    # Outside the wing panel (BL 23..157): 0 plies
    assert ss.book_plies(22.0) == (0, 0)
    assert ss.book_plies(158.0) == (0, 0)


def test_station_result_and_spar_sizing_result_serialization_and_gates(result):
    base_kw = {
        "y_in": np.float64(157.0),
        "chord_in": 20.0,
        "cap_depth_in": 3.0,
        "cap_width_in": 3.0,
        "moment_limit": 0.0,
        "moment_ultimate": 0.0,
        "moment_ultimate_neg": 0.0,
        "governing_case": "positive",
        "I_in4": 1.0,
        "sigma_psi": 0.0,
        "R": math.inf,
        "margin": math.inf,
        "margin_limit": math.inf,
        "plies_solved": 1,
        "plies_book_top": 7,
        "plies_book_bottom": 5,
        "R_book": math.inf,
        "margin_book": math.inf,
        "tributary_bl_in": 4.0,
        "mass_lb": 0.05,
        "mass_book_lb": 0.3,
    }
    st_inf = ss.StationResult(**base_kw)
    assert st_inf.plies_book == (7, 5)
    row = st_inf.as_row()
    assert type(row["y_in"]) is float and row["y_in"] == 157.0
    assert row["R"] == "inf"
    assert row["margin"] == "inf"
    assert row["margin_limit"] == "inf"
    assert row["R_book"] == "inf"
    assert row["margin_book"] == "inf"
    assert row["plies_book"] == [7, 5]

    with pytest.raises(ValueError, match="plies_solved must be >= 1"):
        ss.StationResult(**{**base_kw, "plies_solved": 0})
    with pytest.raises(ValueError, match="not R - 1"):
        ss.StationResult(**{**base_kw, "margin": 100.0})
    with pytest.raises(ValueError, match="not R - 1"):
        ss.StationResult(**{**base_kw, "margin": -math.inf})

    d = result.as_dict()
    assert d["margin_convention"] == "R - 1 (Tsai-Wu strength ratio minus one)"
    assert d["required_margin_ultimate"] == result.required_margin
    assert d["book_schedule_sourced"] is True
    assert d["totals_lb_per_wing"] == {
        "cap_mass_solved": result.total_mass_solved_lb,
        "cap_mass_book": result.total_mass_book_lb,
        "extra_ply_mass_over_book": result.extra_ply_mass_lb,
    }
    assert len(d["notes"]) == 11
    assert d["stations"][-1]["R"] == "inf"


def test_size_spar_caps_single_station_unsorted_and_zero_extra_mass_clamp():
    with pytest.raises(ValueError, match="no stations"):
        ss.size_spar_caps(stations=[])

    for bad_m in (-1.0, -1.0001, math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError, match="not an R - 1 margin"):
            ss.size_spar_caps(
                stations=[55.5], assumptions=ss.Assumptions(required_margin=bad_m)
            )

    for bad_asm in (
        ss.Assumptions(load_scale=0.0),
        ss.Assumptions(load_scale=-1.0),
        ss.Assumptions(load_scale=math.nan),
        ss.Assumptions(density_lb_in3=0.0),
        ss.Assumptions(density_lb_in3=-0.072),
        ss.Assumptions(density_lb_in3=math.inf),
    ):
        with pytest.raises(ValueError, match="must be positive"):
            ss.size_spar_caps(stations=[55.5], assumptions=bad_asm)

    # Single station: _tributary returns [0.0], so all station and total masses are 0.0
    r_one = ss.size_spar_caps(stations=[55.5])
    assert len(r_one.stations) == 1
    assert r_one.stations[0].tributary_bl_in == 0.0
    assert r_one.stations[0].mass_lb == 0.0
    assert r_one.stations[0].mass_book_lb == 0.0
    assert r_one.total_mass_solved_lb == 0.0
    assert r_one.total_mass_book_lb == 0.0
    assert r_one.extra_ply_mass_lb == 0.0

    # Unsorted stations are sorted and produce the exact midpoint-rule tributary lengths:
    # [23.0, 55.5, 157.0] -> [0.5*(55.5-23.0), 0.5*(157.0-23.0), 0.5*(157.0-55.5)] = [16.25, 67.0, 50.75]
    r_unsorted = ss.size_spar_caps(stations=[157.0, 23.0, 55.5])
    assert [s.y_in for s in r_unsorted.stations] == [23.0, 55.5, 157.0]
    assert [s.tributary_bl_in for s in r_unsorted.stations] == pytest.approx(
        [16.25, 67.0, 50.75], rel=1e-12
    )

    # Outboard stations [140.0, 157.0] where solved plies (1) <= book plies (3 or 2 top, 2 or 1 bottom):
    # max(0, plies_solved - plies_book_*) clamps negative differences to 0, so extra_ply_mass_lb == 0.0
    r_outboard = ss.size_spar_caps(stations=[140.0, 157.0])
    assert all(s.plies_solved <= s.plies_book_top for s in r_outboard.stations)
    assert all(s.plies_solved <= s.plies_book_bottom for s in r_outboard.stations)
    assert r_outboard.total_mass_solved_lb < r_outboard.total_mass_book_lb
    assert r_outboard.extra_ply_mass_lb == 0.0


def test_station_limit_margin_and_tip_boundary_invariants(result):
    fos = result.load_case["factor_of_safety"]
    assert fos == 1.5

    for st in result.stations[:-1]:
        assert st.moment_ultimate > 0.0
        assert st.moment_ultimate_neg < 0.0
        assert st.moment_limit == pytest.approx(st.moment_ultimate / fos, rel=1e-12)
        assert st.margin_limit == pytest.approx(st.R * fos - 1.0, rel=1e-12)
        assert st.margin_limit > st.margin

    tip = result.stations[-1]
    assert tip.y_in == 157.0
    assert tip.moment_limit == 0.0
    assert tip.moment_ultimate == 0.0
    assert tip.moment_ultimate_neg == 0.0
    assert tip.sigma_psi == 0.0
    assert math.isinf(tip.R) and math.isinf(tip.margin) and math.isinf(tip.margin_limit)
    assert math.isinf(tip.R_book) and math.isinf(tip.margin_book)
    assert tip.plies_solved == 1

    # Tributary lengths over the full panel sum to tip - root = 134.0 in
    assert sum(s.tributary_bl_in for s in result.stations) == pytest.approx(
        134.0, rel=1e-12
    )
    assert result.total_mass_book_lb == pytest.approx(
        sum(s.mass_book_lb for s in result.stations), rel=1e-12
    )
