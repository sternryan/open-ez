# tests/test_gear_stations.py
"""Chapters 7-9 book geometry (skins, roll-over, belts, step, main gear): provenance and cross-checks."""

import dataclasses

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, GeometricParams, config
from core.sources import check_citation

NEW_FIELDS = (
    "fs_spar_aft_face",
    "bl_gear_datum",
    "main_axle_fwd_of_spar",
    "fs_main_axle",
    "wl_main_axle",
    "fs_nose_wheel",
    "wl_nose_wheel",
    "gear_tip_back_deg",
    "gear_toe_in_b_minus_a",
    "gear_toe_in_square_in",
    "skin_third_ply_fs_range",
    "skin_strip_width",
    "skin_strip_lengths",
    "skin_firewall_lap",
    "skin_bottom_overlap",
    "skin_ply_angle_deg",
    "belt_insert_fs_range",
    "rollover_width",
    "rollover_base_height",
    "rollover_shoulder",
    "rollover_peak_base",
    "rollover_peak_height",
    "rollover_notch",
    "rollover_side_length",
    "rollover_side_ends",
    "rollover_back_triangle",
    "rollover_shoulder_top",
    "rollover_foam_thickness",
    "rollover_insert",
    "rollover_harness_insert_spacing",
    "rollover_harness_insert_from_end",
    "rollover_canopy_insert_from_peak",
    "rollover_map_slot",
    "rollover_baggage_hole_dia",
    "belt_front_fwd_of_front_seat_bkhd",
    "belt_rear_fwd_of_rear_seat_bkhd",
    "step_size",
    "step_thickness",
    "step_min_bend_radius",
    "gear_jig_block",
    "gear_tube",
    "gear_tube_showing",
    "gear_tab_pads",
    "gear_extrusion",
)
G = config.geometry
P = GEOMETRY_PROVENANCE
SOURCED = {"book", "derived", "cp-corrected"}


def test_every_new_field_has_provenance():
    names = {f.name for f in dataclasses.fields(GeometricParams)} | {"fs_main_axle"}
    for n in NEW_FIELDS:
        assert n in names or hasattr(GeometricParams, n), n
        assert n in P, n


def test_sourced_new_fields_cite_the_registry():
    for n in NEW_FIELDS:
        e = P[n]
        if e["status"] in SOURCED:
            check_citation(e["source"])
            assert e["source"].startswith(("plans-1980:p", "cp-text:p")), n


def test_main_axle_is_the_printed_station():  # Review Focus 2
    assert G.fs_spar_aft_face == 125.5
    assert G.main_axle_fwd_of_spar == 15.0
    assert G.fs_main_axle == G.fs_spar_aft_face - 15 == 110.5
    assert P["fs_main_axle"]["status"] == "derived"
    assert P["fs_spar_aft_face"]["status"] == "book"
    assert G.bl_gear_datum == 26.75
    assert G.wl_main_axle == -22.0
    assert P["wl_main_axle"]["status"] == "book"
    assert G.gear_tip_back_deg == 12.0
    assert (G.gear_toe_in_b_minus_a, G.gear_toe_in_square_in) == ((0.2, 0.45), 24.0)


def test_axle_follows_the_spar_not_a_copy():
    g = dataclasses.replace(G, fs_spar_aft_face=130.0)
    assert g.fs_main_axle == 115.0


def test_spar_face_vs_firewall_is_recorded():
    assert G.fs_spar_aft_face - G.fs_firewall == 0.5
    assert "firewall" in P["fs_spar_aft_face"]["note"]


def test_nose_wheel_conflict_is_kept():  # Review Focus 8
    assert G.fs_nose_wheel == 17.0
    e = P["fs_nose_wheel"]
    assert e["status"] == "conflict"
    assert "20" in e["note"]
    assert G.wl_nose_wheel == -22.0
    assert P["wl_nose_wheel"]["status"] == "cp-corrected"
    assert "LPC 24" in P["wl_nose_wheel"]["source"]


def test_no_track_or_tread_anywhere():  # Review Focus 2
    for n in [f.name for f in dataclasses.fields(GeometricParams)] + list(P):
        assert "track" not in n and "tread" not in n, n


def test_skin_schedule():  # Review Focus 6
    assert G.skin_third_ply_fs_range == (60.0, 110.0)
    assert G.skin_third_ply_fs_range == (G.fs_firewall - 15 - 50, G.fs_firewall - 15)
    assert G.skin_strip_lengths == (52.0, 50.0, 48.0)
    assert G.skin_strip_width == 3.0
    assert G.skin_ply_angle_deg == 30.0
    assert P["skin_third_ply_fs_range"]["status"] == "derived"
    assert G.belt_insert_fs_range == (49.7, 54.7)
    assert P["belt_insert_fs_range"]["confidence"] == "medium"
    assert G.belt_insert_fs_range[0] == pytest.approx(G.fs_f22 + 27.7)


def test_rollover_box_adds_up():
    assert 2 * G.rollover_shoulder + G.rollover_peak_base == pytest.approx(
        G.rollover_width
    )
    assert G.rollover_width == G.front_seat_bkhd_width == 23.0
    assert G.rollover_side_length == 13.0
    assert P["rollover_side_length"]["status"] == "cp-corrected"
    assert "LPC 37" in P["rollover_side_length"]["source"]


def test_harness_spacing_is_the_cp_value():
    assert G.rollover_harness_insert_spacing == 4.0
    e = P["rollover_harness_insert_spacing"]
    assert e["status"] == "cp-corrected" and "LPC 52" in e["source"]


def test_baggage_hole_reads_three_and_three_quarters():
    assert G.rollover_baggage_hole_dia == 3.75


def test_gear_hardware():
    assert G.gear_extrusion == (0.25, 2.0, 2.0)
    assert G.gear_tube == (0.625, 0.049, 6.75)
    assert G.gear_tab_pads == ((2.5, 12.0), (2.5, 3.5), (2.5, 2.5))
