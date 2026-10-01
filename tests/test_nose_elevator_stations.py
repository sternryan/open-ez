# tests/test_nose_elevator_stations.py
"""Chapters 11-13 values (nose box, nose gear, Roncz elevators): provenance, conflicts, ledger references."""
import dataclasses

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, PROVENANCE_STATUSES, GeometricParams, config
from core.ledger import fuselage_ledger, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

VALUES = {
    "ng6_width_in": 2.75, "ng6_bore_height_in": 1.25, "ng7_length_in": 2.75,
    "ng30_thickness_in": 0.2, "ng30_gap_in": 3.0, "ng3_to_ng7_in": 6.71,
    "nose_strut_pivot_to_pivot_in": 25.5,
    "floor_block_length_in": 20.9, "floor_block_width_in": 8.2, "floor_block_thickness_in": 1.6,
    "side_block_length_in": 21.9, "side_block_height_f22_in": 15.6,
    "side_block_height_ng31_above_in": 5.5, "side_block_height_ng31_below_in": 2.8,
    "top_block_length_in": 19.3, "top_block_width_aft_in": 19.6, "top_block_width_fwd_in": 7.0,
    "pedal_block_from_ng30_in": 6.1, "wl_static_port": 13.0,
    "fs_nose_wheel": 17.0, "fs_nose_wheel_manual": 20.0, "fs_nose": -6.8,
    "elevator_length_right_in": 55.7, "elevator_length_left_in": 72.7,
    "elevator_travel_up_target_deg": 15.0, "elevator_travel_up_floor_deg": 12.5,
    "elevator_travel_down_deg": 30.0,
    "elevator_hinge_bl_in": (9.2, 34.1, 59.0),
    "elevator_slot_gap_in": 0.2, "elevator_hinge_offset_in": 0.55, "elevator_tube_od_in": 1.0,
    "elevator_pin_right_in": 36.0, "elevator_pin_left_in": 61.0,
    "cs11_lead_dims": (2.0, 0.6, 0.8), "cs10_inboard_from_end_in": 7.5,
    "balance_pocket_clearance_in": 0.06, "elevator_fuselage_gap_in": 0.0625,
    "elevator_weight_ceiling_left_lb": 3.9, "elevator_weight_ceiling_right_lb": 3.6,
}
DERIVED = ("fs_static_port", "fs_ng31_min", "fs_ng31_max")
NEW = tuple(k for k in VALUES if k not in ("fs_nose", "fs_nose_wheel")) + DERIVED
SOURCED = {"book", "derived", "cp-corrected"}
ELEVATOR = [n for n in NEW if n.startswith(("elevator_travel", "elevator_hinge"))]


def test_every_new_field_exists_with_its_value():
    for n, v in VALUES.items():
        assert getattr(G, n) == pytest.approx(v), n


def test_every_new_field_has_provenance_and_citation():
    fields = {f.name for f in dataclasses.fields(GeometricParams)}
    for n in NEW:
        assert n in fields or hasattr(GeometricParams, n), n
        e = P[n]
        assert e["status"] in PROVENANCE_STATUSES, n
        if e["status"] in SOURCED | {"conflict", "positioned-from-text"}:
            check_citation(e["source"])
        assert e["source"].startswith(("plans-1980:p", "om-1980:p", "cobelu:p", "cp-text:p", "plans-1980:p")), n


def test_chapter_13_plans_pages():
    pages = {"ng6_width_in": 73, "ng7_length_in": 73, "ng30_gap_in": 77, "ng3_to_ng7_in": 78,
             "nose_strut_pivot_to_pivot_in": 81, "floor_block_length_in": 79,
             "side_block_length_in": 79, "pedal_block_from_ng30_in": 79,
             "top_block_length_in": 82, "wl_static_port": 82, "fs_static_port": 82}
    for n, pg in pages.items():
        assert P[n]["source"].startswith(f"plans-1980:p{pg}"), n
    assert "0.05" in P["ng3_to_ng7_in"]["note"]
    assert P["nose_strut_pivot_to_pivot_in"]["confidence"] == "medium"
    for n in ("floor_block_length_in", "side_block_length_in", "top_block_length_in"):
        assert P[n]["confidence"] == "medium", n


def test_nose_tip_is_still_minus_6_8_book_with_lowered_confidence():
    assert G.fs_nose == -6.8
    e = P["fs_nose"]
    assert e["status"] == "book" and e["confidence"] == "medium"
    assert "500 dpi" in e["note"] and "not crisp" in e["note"]
    assert "fs_nose_tip" not in {f.name for f in dataclasses.fields(GeometricParams)}


def test_nose_wheel_is_a_conflict_pair():  # Review Focus 1
    assert (G.fs_nose_wheel, G.fs_nose_wheel_manual) == (17.0, 20.0)
    assert P["fs_nose_wheel"]["status"] == "conflict"
    m = P["fs_nose_wheel_manual"]
    assert m["status"] == "conflict" and m["source"].startswith("om-1980:p35")
    assert "19.6" in m["note"]


def test_no_unprinted_gear_dimension_exists():  # Review Focus 1
    banned = ("rake", "fork", "trail", "ng6_position", "axle_offset")
    names = [f.name for f in dataclasses.fields(GeometricParams)] + list(P)
    for n in names:
        assert not any(b in n for b in banned), n


def test_ng31_station_is_a_range_not_a_value():
    assert G.fs_ng31_min == pytest.approx(0.1)
    assert G.fs_ng31_max == pytest.approx(1.1)
    assert G.fs_ng31_min < G.fs_ng31_max
    assert not hasattr(G, "fs_ng31")
    for n in ("fs_ng31_min", "fs_ng31_max"):
        assert P[n]["status"] == "derived" and P[n]["confidence"] == "medium"
        assert "range" in P[n]["note"]
    g = dataclasses.replace(G, fs_f22=30.0)
    assert g.fs_ng31_min == pytest.approx(30.0 - 21.9)


def test_static_port_follows_the_panel():
    assert G.fs_static_port == pytest.approx(G.fs_panel - 8.0)
    assert dataclasses.replace(G, fs_panel=50.0).fs_static_port == pytest.approx(42.0)
    assert P["fs_static_port"]["status"] == "derived"
    assert "left" in P["wl_static_port"]["note"].lower()


def test_elevator_travel_is_roncz_not_gu_or_manual():  # Review Focus 4
    assert (G.elevator_travel_up_target_deg, G.elevator_travel_up_floor_deg,
            G.elevator_travel_down_deg) == (15.0, 12.5, 30.0)
    for n in ("elevator_travel_up_target_deg", "elevator_travel_up_floor_deg", "elevator_travel_down_deg"):
        src = P[n]["source"]
        assert src.startswith("cobelu:p"), n
        assert "plans-1980:p72" not in src and "om-1980:p29" not in src, n
        assert "different" in P[n]["note"]
    for n in ELEVATOR + ["elevator_length_right_in", "elevator_length_left_in"]:
        assert "plans-1980:p72" not in P[n]["source"] and "om-1980:p29" not in P[n]["source"], n
    for v in (20.0, 22.0):
        assert v not in (G.elevator_travel_up_target_deg, G.elevator_travel_down_deg)


def test_elevator_lengths_agree_with_stock_tubes():
    assert 57.0 - G.elevator_length_right_in == pytest.approx(1.3)
    assert 74.0 - G.elevator_length_left_in == pytest.approx(1.3)


def test_hinge_bls_are_flagged_positioned_from_text_low():  # Review Focus 3
    e = P["elevator_hinge_bl_in"]
    assert e["status"] == "positioned-from-text" and e["confidence"] == "low"
    assert "57.0" in e["note"] and "7.8" in e["note"]
    assert G.elevator_hinge_bl_right_first_drawn_in == 7.8


def test_elevator_weight_is_a_check_bound_not_a_mass():  # Review Focus 5
    for n in ("elevator_weight_ceiling_left_lb", "elevator_weight_ceiling_right_lb"):
        assert P[n]["source"].startswith("om-1980:p30")
        assert "check bound" in P[n]["note"]


def test_prototype_weights_are_cited_reference_data():  # Review Focus 5
    pw = load_ledger()["prototype_weights"]
    rows = pw["rows"]
    assert {k: rows[k]["weight_lb"] for k in ("f22", "f28", "panel")} == {"f22": 1.44, "f28": 0.19, "panel": 2.13}
    for k in ("f22", "f28", "panel"):
        check_citation(rows[k]["cite"])
        assert rows[k]["cite"].startswith("cp-text:p26")
        assert "prototype" in rows[k]["note"] and "uncured" in rows[k]["note"]
    assert pw["complete_fuselage_lb"]["weight_lb"] == 183.0
    check_citation(pw["complete_fuselage_lb"]["cite"])
    assert "reference only" in pw["complete_fuselage_lb"]["note"]
    assert "cs11_lead" not in rows and "elevator" not in " ".join(rows)


def test_prototype_weights_are_not_in_any_sum():
    led = load_ledger()
    assert "prototype_weights" not in led["gear"]
    names = {r["part"] for r in fuselage_ledger()}
    assert {"f22", "f28", "panel"} <= names  # computed rows stay; no second copy is added


def test_computed_core_is_below_the_prototype_finished_part():
    rows = {r["part"]: r for r in fuselage_ledger()}
    ref = load_ledger()["prototype_weights"]["rows"]
    for k in ("f22", "f28", "panel"):
        assert 0 < rows[k]["core_mass_lb"] < ref[k]["weight_lb"], k


def test_nose_strut_stays_2_8_with_cp23_note():
    r = {x["name"]: x for x in load_ledger()["gear"]["rows"]}["nose_strut"]
    assert r["weight_lb"] == 2.8 and r["arm_in"] == 17.0
    assert "2.6" in r["note"] and "CP23" in r["note"]
