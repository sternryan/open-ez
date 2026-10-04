# tests/test_wing_stations.py
"""Chapter 19 values (wing): provenance, the p126 arithmetic, the two conflict pairs, and the ledger reference rows."""

import math

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, config
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE
TAN_LE = math.tan(math.radians(G.wing_sweep_le))
TAN_TE = math.tan(math.radians(G.wing_book_te_sweep_deg))

BOOK = {
    "wing_book_rib_bl": (23.0, 55.5, 106.25, 157.0),
    "wing_book_le_fs_bl_55_5": 112.9,
    "wing_book_le_fs_tip": 156.0,
    "wing_book_te_fs": (155.6, 165.8, 176.0),
    "wing_book_te_fs_bl_23": 148.4,
    "wing_book_chord": (42.7, 31.35, 20.0),
    "wing_book_thickness_pct": (16.2, 15.7, 15.0),
    "wing_book_washout_deg": (-0.6, 0.96, 2.7),
    "wing_book_te_sweep_deg": 11.36,
    "wing_book_te_sweep_inboard_deg": 12.49,
    "wing_book_chord_line_wl": 17.4,
    "wing_book_te_wl": (16.95, 18.35),
    "wing_book_shear_web_fwd_fs": (125.6, 130.5, 147.35, 164.2),
    "wing_book_shear_web_sweep_deg": 18.42,
    "wing_book_spar_cap_width_in": 3.0,
    "wing_book_foam_blocks": (5, 2),
    "wing_book_core_angle_deg": (78.64, 77.51),
    "wing_book_fc1_le_length_in": 32.87,
    "wing_cap_bottom_plies_in": (142.0, 135.0, 84.0, 52.0, 19.5),
    "wing_cap_bottom_offsets_in": (5.0, 12.0, 19.0, 26.0),
    "wing_cap_top_plies_in": (142.0, 142.0, 119.0, 90.0, 61.0, 39.0, 20.0),
    "wing_cap_top_offsets_in": (6.0, 12.0, 18.0, 24.0),
    "wing_skin_plies": (2, 3),
    "wing_skin_le_lap_in": 2.0,
    "wing_aileron_outboard_bl": 118.1,
    "wing_aileron_skin_cut_top_in": (5.9, 4.35),
    "wing_aileron_skin_cut_bottom_in": (7.6, 5.65),
    "wing_aileron_rod_length_in": 65.0,
    "wing_aileron_torque_tube_length_in": 9.0,
    "wing_aileron_hinge_lengths_in": (8.0, 6.0, 6.0),
    "wing_aileron_max_up_deg": 20.0,
    "wing_spar_join_bolts": (2, 1),
    "wing_spar_join_bushings_per_wing": 6,
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_chord_is_te_minus_le_at_each_station():
    le = (
        G.wing_book_le_fs_bl_55_5,
        G.wing_le_fs_bl_106_25_derived,
        G.wing_book_le_fs_tip,
    )
    for c, te, l0 in zip(G.wing_book_chord, G.wing_book_te_fs, le):
        assert te - l0 == pytest.approx(c, abs=0.005)


def test_le_line_through_112_9_and_156_is_22_98_deg():
    slope = (G.wing_book_le_fs_tip - G.wing_book_le_fs_bl_55_5) / (157.0 - 55.5)
    assert math.degrees(math.atan(slope)) == pytest.approx(22.98, abs=0.05)
    assert G.wing_book_le_fs_bl_55_5 + (157.0 - 55.5) * TAN_LE == pytest.approx(
        156.0, abs=0.1
    )


def test_te_line_is_11_36_deg_and_the_inboard_kink_closes_at_bl_23():
    assert G.wing_book_te_fs[0] + (106.25 - 55.5) * TAN_TE == pytest.approx(
        165.8, abs=0.02
    )
    assert G.wing_book_te_fs[0] + (157.0 - 55.5) * TAN_TE == pytest.approx(
        176.0, abs=0.1
    )
    kink = math.tan(math.radians(G.wing_book_te_sweep_inboard_deg))
    assert G.wing_book_te_fs[0] - 32.5 * kink == pytest.approx(
        G.wing_book_te_fs_bl_23, abs=0.05
    )


def test_le_at_bl_58_agrees_with_the_cp25_anchor():
    assert G.wing_le_fs_bl_58 == pytest.approx(113.96, abs=0.01)
    assert abs(G.wing_le_fs_bl_58 - G.wing_le_anchor[0]) < 0.1
    assert G.wing_le_anchor == (113.9, 58.0)
    assert P["wing_le_fs_bl_58"]["status"] == "derived"
    assert P["wing_le_anchor"]["status"] == "cp-corrected"


def test_wing_le_125_61_is_a_different_point_from_113_9():
    note = P["wing_le_anchor"]["note"]
    assert "125.61" in note and "FC1 foam edge" in note
    assert G.wing_book_shear_web_fwd_fs[0] == 125.6  # the FC1 foam edge, not an LE
    assert G.wing_book_le_fs_bl_55_5 < G.wing_book_shear_web_fwd_fs[0]
    # the LE line reaches FS 125.6 only about 30 in inboard of BL 55.5, inside the strake
    assert 55.5 - (125.6 - 112.9) / TAN_LE == pytest.approx(25.6, abs=0.1)


def test_fc1_le_check_and_the_core_angles():
    sw = G.wing_book_shear_web_fwd_fs
    assert math.hypot(55.5 - 23.0, sw[1] - sw[0]) == pytest.approx(
        G.wing_book_fc1_le_length_in, abs=0.01
    )
    assert math.degrees(math.atan((sw[1] - sw[0]) / 32.5)) == pytest.approx(
        8.57, abs=0.01
    )
    assert 90 - G.wing_book_te_sweep_deg == pytest.approx(
        G.wing_book_core_angle_deg[0], abs=0.005
    )
    assert 90 - G.wing_book_te_sweep_inboard_deg == pytest.approx(
        G.wing_book_core_angle_deg[1], abs=0.005
    )


def test_shear_web_face_is_the_18_42_deg_line():
    sw = G.wing_book_shear_web_fwd_fs
    k = math.tan(math.radians(G.wing_book_shear_web_sweep_deg))
    assert sw[1] + (157.0 - 55.5) * k == pytest.approx(sw[3], abs=0.15)
    assert sw[1] + (106.25 - 55.5) * k == pytest.approx(sw[2], abs=0.15)


def test_bl_106_25_le_is_a_conflict_pair():
    assert G.wing_book_le_fs_bl_106_25_printed == 134.95
    assert G.wing_le_fs_bl_106_25_derived == pytest.approx(134.45)
    assert G.wing_le_fs_bl_106_25_line == pytest.approx(134.42, abs=0.01)
    for k in ("wing_book_le_fs_bl_106_25_printed", "wing_le_fs_bl_106_25_derived"):
        assert P[k]["status"] == "conflict"
    assert "134.45" in P["wing_book_le_fs_bl_106_25_printed"]["note"]


def test_aileron_inboard_end_is_a_conflict_pair():
    assert (G.wing_aileron_inboard_bl, G.wing_aileron_inboard_bl_p171) == (55.5, 54.3)
    assert P["wing_aileron_inboard_bl"]["status"] == "conflict"
    assert P["wing_aileron_inboard_bl_p171"]["status"] == "conflict"
    assert "plans-1980:p124" in P["wing_aileron_inboard_bl"]["source"]
    assert "plans-1980:p171" in P["wing_aileron_inboard_bl_p171"]["source"]


def test_attach_bolt_spacing_is_a_conflict_pair():
    assert (G.wing_spar_join_bolt_spacing_in, G.wing_spar_join_bolt_spacing_text_in) == (
        28.85,
        28.83,
    )
    assert P["wing_spar_join_bolt_spacing_in"]["status"] == "conflict"


def test_aileron_hinge_line_meets_the_wprp_and_the_tip_cut():
    h = G.wing_aileron_hinge_fs
    assert h == pytest.approx((149.7, 161.45))
    assert (
        abs(h[0] - G.winglet_book_jig_wprp[0]) < 0.2
    )  # WPRP is the inboard front corner
    slope = (h[1] - h[0]) / (106.25 - 55.5)
    te_tip = G.wing_book_te_fs[0] + (118.1 - 55.5) * TAN_TE
    assert te_tip - (h[0] + (118.1 - 55.5) * slope) == pytest.approx(3.99, abs=0.03)


def test_shear_web_outboard_zone_is_cp_corrected_to_two_plies():
    z = G.wing_shear_web_zones
    assert [n for *_, n in z] == [6, 4, 2]
    assert z[0][0] == 23.0 and z[-1][1] == 157.0 and z[0][1] == z[1][0]
    assert G.wing_shear_web_outboard_plies_printed == 3
    assert P["wing_shear_web_zones"]["status"] == "cp-corrected"
    assert P["wing_shear_web_zones"]["source"].startswith("cp-text:p26")


def test_cap_schedules_are_the_base_schedule_and_say_so():
    assert len(G.wing_cap_bottom_plies_in) == 5 and len(G.wing_cap_top_plies_in) == 7
    for k in ("wing_cap_bottom_plies_in", "wing_cap_top_plies_in"):
        assert "base schedule" in P[k]["note"]
    assert "CP28 LPC 56" in P["wing_cap_bottom_plies_in"]["note"]
    # tape length 142 against the web line from BL 23 to BL 157
    run = 134.0 / math.cos(math.atan(math.tan(math.radians(18.42))))
    assert run == pytest.approx(141.3, abs=0.2)


def test_analysis_fields_carry_the_book_value_in_a_note_and_do_not_move():
    assert (G.wing_span, G.wing_root_bl, G.wing_washout) == (313.2, 23.3, 1.0)
    assert "314" in P["wing_span"]["note"]
    assert "23.3 appears on no page" in P["wing_root_bl"]["note"]
    assert P["wing_washout"]["status"] == "unsourced"
    assert "0.96" in P["wing_washout"]["note"] and "2.7" in P["wing_washout"]["note"]


def test_wing_reference_rows_are_sourced_not_in_any_sum():
    rows = load_ledger()["prototype_weights"]["rows"]
    want = {
        "wing_ch19": 51.5,
        "wing_complete": 64.0,
        "aileron": 5.125,
        "upper_winglet": 6.0,
        "lower_winglet": 1.19,
    }
    for k, w in want.items():
        assert rows[k]["weight_lb"] == w and rows[k]["cite"] == "cp-text:p26"
        check_citation(rows[k]["cite"])
        assert "N26MS" in rows[k]["note"] and "CP26 page 3" in rows[k]["note"]
        assert "not a ledger row" in rows[k]["note"]
    parts = {r["part"] for r in fuselage_ledger()}
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    for k in want:
        assert k not in parts and k not in inc and k not in exc


def test_ledger_json_has_the_rows_and_the_cg_is_unchanged():
    j = fuselage_ledger_json()
    assert set(j["prototype_weights"]["rows"]) >= {
        "canopy",
        "wing_ch19",
        "wing_complete",
        "aileron",
        "upper_winglet",
        "lower_winglet",
    }
    assert j["cg"]["arm_in"] is None and j["cg"]["weight_lb"] == 0.0
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)
