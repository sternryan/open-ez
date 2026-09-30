# tests/test_fuselage_stations.py
"""Fuselage book geometry (chapters 4-6): provenance, stations, side table, cross-checks."""
import dataclasses
import math
from itertools import pairwise

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, GeometricParams, config
from core.sources import check_citation

NEW_FIELDS = (
    "fs_f22", "fs_f28", "fs_panel",
    "fs_front_seat_bkhd_bottom", "fs_front_seat_bkhd_top",
    "fs_rear_seat_bkhd_bottom", "fs_rear_seat_bkhd_top",
    "side_panel_length", "side_panel_top_wl", "side_panel_thickness", "side_panel_heights",
    "side_spar_cutout", "side_sight_gauge", "side_dish",
    "front_seat_bkhd_length", "front_seat_bkhd_width", "front_seat_bkhd_thickness",
    "front_seat_bkhd_taper", "front_seat_bkhd_notch_top", "front_seat_bkhd_notch_bottom",
    "rear_seat_bkhd_bottom_width", "rear_seat_bkhd_top_width", "rear_seat_bkhd_length",
    "rear_seat_bkhd_thickness", "rear_seat_bkhd_side_taper", "rear_seat_bkhd_bevel_top_deg",
    "rear_seat_bkhd_bevel_bottom_deg", "rear_seat_bkhd_notch", "rear_seat_bkhd_access_dia",
    "rear_seat_bkhd_foam_circle_dia",
    "fuselage_inner_width_stations", "fuselage_inner_width_fwd",
    "bottom_foam_thickness", "bottom_trim_outboard", "bottom_aft_trim",
)
G = config.geometry
P = GEOMETRY_PROVENANCE


def side_depth(x, table=None):
    t = table or G.side_panel_heights
    for (x0, h0), (x1, h1) in pairwise(t):
        if x0 <= x <= x1:
            return h0 + (h1 - h0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def test_every_new_field_exists_and_has_provenance():
    names = {f.name for f in dataclasses.fields(GeometricParams)}
    for n in NEW_FIELDS:
        assert n in names, n
        assert n in P, n


def test_sourced_new_fields_cite_plans_pages():
    for n in NEW_FIELDS:
        e = P[n]
        if e["status"] in {"book", "derived"}:
            check_citation(e["source"])
            assert e["source"].startswith("plans-1980:p"), n
    assert P["fuselage_inner_width_fwd"]["status"] == "unsourced"
    assert P["side_dish"]["status"] == "conflict"


def test_fs_panel_conflict_note_names_the_manual():
    e = P["fs_panel"]
    assert e["status"] == "derived"
    assert "conflict: om-1980:p34" in e["note"] and "40" in e["note"]


def test_seat_bulkheads_sit_at_derived_stations():  # Review Focus 2
    assert G.fs_f22 == 22.0
    assert G.fs_f22 + G.side_panel_length == G.fs_firewall
    for name, x in (
        ("fs_f28", 5.65), ("fs_panel", 17.75),
        ("fs_front_seat_bkhd_bottom", 41.55), ("fs_front_seat_bkhd_top", 59.75),
        ("fs_rear_seat_bkhd_bottom", 85.0), ("fs_rear_seat_bkhd_top", 96.5),
    ):
        assert getattr(G, name) == pytest.approx(22.0 + x), name
    assert G.fs_rear_seat_bkhd_bottom == pytest.approx(G.fs_f22 + G.side_panel_length - 18.0)
    assert G.fs_rear_seat_bkhd_top == pytest.approx(G.fs_front_seat_bkhd_top + 36.75)
    # occupant CG arms are unchanged and are not bulkhead stations
    assert G.fs_pilot_seat == 59.0 and G.fs_rear_seat == 103.0
    stations = [getattr(G, n) for n in NEW_FIELDS if n.startswith("fs_")]
    assert G.fs_pilot_seat not in stations and G.fs_rear_seat not in stations


def test_side_height_table_is_the_printed_one():
    assert G.side_panel_heights == (
        (0, 19.8), (10, 20.3), (20, 20.5), (30, 20.5), (40, 20.5), (50, 20.5),
        (60, 20.5), (70, 20.4), (80, 19.8), (90, 18.4), (100, 16.6), (103, 16.0),
    )
    xs = [x for x, _ in G.side_panel_heights]
    assert len(xs) == 12 and all(a < b for a, b in pairwise(xs))
    assert xs[-1] == G.side_panel_length
    assert [b - a for a, b in pairwise(xs)] == [10] * 10 + [3]


def test_rear_bulkhead_slant_matches_printed_length():
    d85 = side_depth(85.0)
    slant = math.hypot(96.5 - 85.0, d85 - G.side_spar_cutout[1])
    assert slant == pytest.approx(G.rear_seat_bkhd_length, abs=0.6)


def test_front_bulkhead_slant_matches_printed_length():
    d = side_depth(41.55)
    slant = math.hypot(59.75 - 41.55, d - 0.0)
    assert slant == pytest.approx(G.front_seat_bkhd_length, abs=1.2)


def test_cross_checks_fail_on_a_broken_value():
    # rear check: push the aft depths (x 80 and 90) deeper by 6 in
    rear = tuple((x, h + 6.0 if x in (80, 90) else h) for x, h in G.side_panel_heights)
    assert abs(math.hypot(11.5, side_depth(85.0, rear) - 8.5) - 16.1) > 0.6
    # front check: a wrong 25 in depth at x 40 breaks the 1.2 tolerance
    front = tuple((x, 25.0 if x == 40 else h) for x, h in G.side_panel_heights)
    assert abs(math.hypot(18.2, side_depth(41.55, front)) - 28.3) > 1.2
    # the side table itself: one monkeypatched height no longer equals the printed value
    assert rear != G.side_panel_heights
    # station check: a wrong seat-bulkhead station breaks the derived-station rule
    assert 22.0 + 41.0 != G.fs_front_seat_bkhd_bottom
