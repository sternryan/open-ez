# tests/test_spar_stations.py
"""Chapters 14-17 values (centre-section spar, firewall, controls, trim): provenance, sums, conflicts, ledger."""

import dataclasses
import math

import pytest

from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    PROVENANCE_STATUSES,
    GeometricParams,
    config,
)
from core.ledger import fuselage_cg, fuselage_ledger, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

VALUES = {
    "spar_fwd_face_fs": 118.5,
    "spar_aft_face_fs_centre": 125.0,
    "spar_kink_bl": 23.0,
    "spar_outboard_sweep_deg": 8.57,
    "spar_half_span_bl": 56.46,
    "spar_chord_centreline_in": 6.50,
    "spar_face_length_fwd_outboard_in": 33.834,
    "spar_face_length_aft_outboard_in": 32.865,
    "spar_hard_point_spacing_aft_in": 28.82,
    "spar_depth_in": 8.50,
    "spar_top_wl": 22.0,
    "spar_bottom_wl": 13.5,
    "spar_bottom_flat_to_bl": 9.0,
    "spar_bottom_wl_outboard": 15.15,
    "spar_top_flat_to_bl": 25.0,
    "spar_top_wl_outboard": 21.7,
    "spar_hp_inboard_bl_in": 25.0,
    "spar_hp_inboard_wl_in": 20.25,
    "spar_hp_outboard_bl_in": 53.5,
    "spar_hp_outboard_wl_in": (20.5, 16.3),
    "spar_end_bulkhead_width_in": 6.30,
    "spar_end_bulkhead_height_in": 6.83,
    "spar_foam_height_centre_in": 8.41,
    "spar_foam_height_kink_in": 7.94,
    "spar_foam_height_end_in": 6.83,
    "spar_cap_tape_width_in": 3.0,
    "spar_ply_thickness_laid_in": 0.0375,
    "spar_ply_thickness_stock_in": 0.035,
    "spar_full_ply_end_bl": 55.5,
    "spar_spruce_block_in": (1.0, 1.0, 3.0),
    "spar_spruce_block_bl": 7.5,
    "spar_em12_length_in": 8.0,
    "spar_em12_count": 4,
    "spar_lwa1_outboard_setback_in": 0.75,
    "spar_baggage_hole_in": (14.0, 5.0),
    "spar_nut_access_hole_dia_in": 2.25,
    "ctl_torque_tube_hole_dia_in": 1.0,
    "ctl_torque_tube_hole_bl_in": 6.2,
    "ctl_torque_tube_hole_wl_in": 12.3,
    "ctl_rudder_conduit_wl_in": 8.0,
    "ctl_rudder_conduit_length_in": 82.0,
    "ctl_stick_pivot_fs_front": 45.5,
    "ctl_stick_pivot_fs_rear": 89.7,
    "ctl_stick_cant_inboard_deg": 5.0,
    "ctl_stick_cant_forward_deg": 5.0,
    "ctl_roll_travel_deg": 20.0,
    "ctl_cs103_length_in": 6.1,
    "ctl_cs110_length_in": 39.2,
    "ctl_cs105_length_in": 42.9,
    "ctl_cs106_length_in": 3.8,
    "ctl_cs115_length_in": 4.2,
    "ctl_cs116_length_in": 4.4,
    "ctl_cs121_length_in": 29.5,
    "ctl_cs119_length_in": 4.1,
    "ctl_elevator_arm_gu_in": 1.9,
    "trim_panel_face_fs_in": 40.0,
    "trim_pth_dim_from_panel_in": 9.5,
    "trim_pth_leftmost_fs_label": 49.8,
    "trim_handle_pivot_wl_in": 8.6,
    "trim_friction_bolt_wl_in": 7.1,
    "trim_swage_from_sleeve_in": (5.6, 6.2),
    "trim_sleeve_bl_in": 9.5,
    "trim_sleeve_wl_in": (9.6, 8.3),
    "trim_spring_pts_in": (6.0, 9.0),
    "trim_spring_rts_in": (2.0, 3.0),
    "trim_spring_cs_in": (0.5, 0.25),
    "trim_nc5a_belcrank_bl_left_in": 9.2,
    "trim_cs202_extra_spacer_in": 0.4,
}
DERIVED = (
    "spar_chord_square_outboard_in",
    "spar_fwd_face_fs_tip",
    "spar_aft_face_fs_bl_55_5",
    "trim_pth_leftmost_fs",
)
TUPLES = (
    "spar_top_cap_strips_in",
    "spar_bottom_cap_strips_in",
    "spar_top_cap_partial_end_bl",
    "spar_bottom_cap_partial_end_bl",
    "spar_lwa_sizes",
)
NEW = tuple(VALUES) + DERIVED + TUPLES
CP_CORRECTED = {
    "ctl_cs119_length_in": "cp-text:p26",
    "spar_lwa1_outboard_setback_in": "cp-text:p25",
    "spar_lwa_sizes": "cp-text:p43",
    "trim_sleeve_bl_in": "cp-text:p25",
    "trim_sleeve_wl_in": "cp-text:p25",
}


def test_every_new_field_exists_with_its_value():
    for n, v in VALUES.items():
        assert getattr(G, n) == pytest.approx(v), n


def test_every_new_field_has_provenance_and_citation():
    fields = {f.name for f in dataclasses.fields(GeometricParams)}
    for n in NEW:
        assert n in fields or hasattr(GeometricParams, n), n
        e = P[n]
        assert e["status"] in PROVENANCE_STATUSES, n
        check_citation(e["source"])
        assert e["source"].startswith(("plans-1980:p", "cp-text:p", "cobelu:p")), n


def test_spar_planform_and_ply_pages_and_statuses():
    for n in (
        "spar_fwd_face_fs",
        "spar_kink_bl",
        "spar_half_span_bl",
        "spar_hp_outboard_wl_in",
    ):
        assert (
            P[n]["source"].startswith("plans-1980:p88") and P[n]["status"] == "book"
        ), n
    for n in (
        "spar_top_cap_strips_in",
        "spar_bottom_cap_strips_in",
        "spar_full_ply_end_bl",
    ):
        assert P[n]["source"].startswith("plans-1980:p86"), n
    for n in ("spar_end_bulkhead_width_in", "spar_foam_height_centre_in"):
        assert P[n]["source"].startswith("plans-1980:p90"), n
    for n in (
        "spar_top_wl_outboard",
        "spar_bottom_flat_to_bl",
        "spar_baggage_hole_in",
        "ctl_stick_pivot_fs_front",
        "ctl_stick_pivot_fs_rear",
    ):
        assert P[n]["confidence"] == "medium", n
    for n in DERIVED[:3]:
        assert P[n]["status"] == "derived", n


def test_cp_corrected_values_cite_their_issue():
    for n, src in CP_CORRECTED.items():
        assert P[n]["status"] == "cp-corrected" and P[n]["source"].startswith(src), n
    assert (
        "printed 3.1" in P["ctl_cs119_length_in"]["note"]
        or "3.1" in P["ctl_cs119_length_in"]["note"]
    )
    assert "1.0" in P["spar_lwa1_outboard_setback_in"]["note"]


def test_the_seven_inch_spar_note_is_gone():
    n = P["fs_spar_aft_face"]["note"]
    assert "7 in spar" not in n and "implies" not in n
    assert "6.50" in n and "125.57" in n and "firewall" in n
    assert G.fs_spar_aft_face == 125.5 and G.bl_gear_datum == 26.75
    assert G.spar_aft_face_fs_centre == G.fs_firewall


def test_swept_aft_face_matches_125_5_at_the_gear_datum():
    t = math.tan(math.radians(G.spar_outboard_sweep_deg))
    assert G.spar_aft_face_fs_centre + (
        G.bl_gear_datum - G.spar_kink_bl
    ) * t == pytest.approx(G.fs_spar_aft_face, abs=0.1)


def test_no_attach_bolt_station_and_no_pitch_stop_exist():
    names = [f.name for f in dataclasses.fields(GeometricParams)] + list(P)
    for n in names:
        assert (
            "attach" not in n and "pitch_stop" not in n and "stop" not in n.split("_")
        ), n
    assert "not printed" in P["spar_hp_inboard_bl_in"]["note"]
    assert "representational" in P["ctl_stick_cant_forward_deg"]["note"]


def test_ply_schedule_sums_and_counts():
    top, bot = G.spar_top_cap_strips_in, G.spar_bottom_cap_strips_in
    assert (len(top), len(bot)) == (12, 9)
    assert (sum(top), sum(bot), sum(top) + sum(bot)) == (972, 705, 1677)
    assert (
        top.count(113) == 4 and bot.count(113) == 3
    )  # cobelu's four bottom full strips is rejected
    for strips, ends in (
        (top, G.spar_top_cap_partial_end_bl),
        (bot, G.spar_bottom_cap_partial_end_bl),
    ):
        partials = sorted(s for s in strips if s != 113)
        assert [2 * e for e in ends] == partials
    assert "three" in P["spar_bottom_cap_strips_in"]["note"]


def test_derived_chord_and_aft_station_agree_with_the_sweep():
    assert G.spar_chord_square_outboard_in == pytest.approx(6.43, abs=0.02)
    assert G.spar_aft_face_fs_bl_55_5 == pytest.approx(129.9, abs=0.02)
    assert G.spar_fwd_face_fs_tip == pytest.approx(123.54, abs=0.02)
    assert dataclasses.replace(
        G, spar_outboard_sweep_deg=0.0
    ).spar_aft_face_fs_bl_55_5 == pytest.approx(125.0)
    s = G.spar_outboard_sweep_deg
    assert (G.spar_half_span_bl - G.spar_kink_bl) / math.cos(
        math.radians(s)
    ) == pytest.approx(G.spar_face_length_fwd_outboard_in, abs=0.01)
    assert (55.5 - G.spar_kink_bl) / math.cos(math.radians(s)) == pytest.approx(
        G.spar_face_length_aft_outboard_in, abs=0.01
    )


def test_lwa_sizes_carry_the_cp43_heights():
    lwa = {r[0]: r for r in G.spar_lwa_sizes}
    assert (lwa["LWA4"][1], lwa["LWA5"][1]) == (1.75, 2.25)
    assert [(lwa[k][1], lwa[k][2], lwa[k][4]) for k in ("LWA1", "LWA2", "LWA3")] == [
        (1.5, 0.125, 6),
        (2.5, 0.125, 4),
        (6.4, 0.125, 4),
    ]
    assert all(r[3] == 2.0 for r in lwa.values())
    n = P["spar_lwa_sizes"]["note"]
    assert "1.5x1/4" in n and "2x1/4" in n


def test_pth_end_is_a_conflict_pair_and_nothing_moves():
    assert G.trim_pth_leftmost_fs == pytest.approx(49.5)
    assert G.trim_pth_leftmost_fs_label == 49.8
    assert abs(G.trim_pth_leftmost_fs_label - G.trim_pth_leftmost_fs) == pytest.approx(
        0.3
    )
    for n in ("trim_pth_leftmost_fs", "trim_pth_leftmost_fs_label"):
        assert P[n]["status"] == "conflict", n
    assert G.fs_panel == 39.75


def test_nc5a_belcrank_is_bl_9_2_left_positioned_from_text():
    e = P["trim_nc5a_belcrank_bl_left_in"]
    assert e["status"] == "positioned-from-text" and e["confidence"] in (
        "low",
        "medium",
    )
    assert G.trim_nc5a_belcrank_bl_left_in == 9.2 and "BL 0" in e["note"]
    assert e["source"].startswith("cobelu:p")


def test_roncz_travel_untouched_and_no_gu_travel():
    assert (
        G.elevator_travel_up_target_deg,
        G.elevator_travel_up_floor_deg,
        G.elevator_travel_down_deg,
    ) == (15.0, 12.5, 30.0)
    assert 20.0 not in (G.elevator_travel_up_target_deg, G.elevator_travel_down_deg)
    assert not any(
        "elevator" in n and "travel" in n and n.startswith(("ctl_", "trim_")) for n in P
    )
    assert "are not carried" in P["ctl_elevator_arm_gu_in"]["note"]


def test_spar_mass_row_is_sourced_reference_not_in_any_sum():
    row = load_ledger()["prototype_weights"]["rows"]["spar"]
    assert row["weight_lb"] == 29.3
    check_citation(row["cite"])
    assert row["cite"].startswith("cp-text:p26") and "29 lb 5 oz" in row["cite"]
    assert (
        "25.8" in row["note"]
        and "3.5 lb" in row["note"]
        and "CP25 LPC 26" in row["note"]
    )
    assert "spar" not in {r["part"] for r in fuselage_ledger()}
    w, arm, inc, exc = fuselage_cg(lower_bound=True)
    assert "spar" not in inc and "spar" not in exc
    assert "cg" not in row and "arm_in" not in row
