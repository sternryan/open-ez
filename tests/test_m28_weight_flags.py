# tests/test_m28_weight_flags.py
"""M2.8 Task 0: the analysis weight and engine fields carry provenance flags, values unchanged, and the folded planform values."""

import dataclasses

import pytest

from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    PROVENANCE_STATUSES,
    WEIGHT_PROVENANCE,
    PropulsionConfig,
    StrakeConfig,
    StructuralWeightParams,
    config,
)

G = config.geometry


def _field_value(name):
    for cls in (PropulsionConfig, StructuralWeightParams, StrakeConfig):
        if name in {f.name for f in dataclasses.fields(cls)}:
            return getattr(cls(), name)
    raise AssertionError(name)


def test_flagged_fields_exist_and_hold_the_values_ledger_row_68_recorded():
    # Task 3 moved the folded fields to the closure rows (row 68); the values below are the new ones.
    values = {
        "wing_weight_lb": 132.4,
        "wing_arm_in": 127.5,
        "canard_weight_lb": 18.5,
        "elevator_weight_lb": 6.5,
        "engine_cg_arm_in": 16.05,
        "engine_mass_kg": 243.0 / 2.20462,
        "engine_dry_weight_lb": 243.0,
        "engine_displacement_ci": 233.3,
        "battery_weight_lb": 19.0,
        "battery_arm_in": 11.0,
        "starter_weight_lb": 0.0,
        "starter_arm_in": 150.0,
        "instruments_weight_lb": 15.0,
        "instruments_arm_in": 40.0,
        "interior_weight_lb": 20.0,
        "interior_arm_in": 81.0,
        "tank_volume_gal": 26.0,
        "elevator_arm_in": G.fs_canard_le + 0.85 * G.canard_chord,
    }
    assert set(values) == set(WEIGHT_PROVENANCE)
    for name, v in values.items():
        assert _field_value(name) == pytest.approx(v), name


def test_entries_are_well_formed_and_only_closure_rows_are_sourced():
    for name, e in WEIGHT_PROVENANCE.items():
        assert set(e) == {"status", "source", "confidence", "note"}, name
        assert e["status"] in PROVENANCE_STATUSES, name
        # folded fields are `derived` (closure rows) or `book` (displacement); only tank_volume_gal is still a flag
        assert e["status"] in {"derived", "book", "conflict", "unsourced"}, name
        if e["status"] == "derived":
            assert "closure row" in e["note"] or "closure" in e["source"], name


def test_wing_weight_names_the_closure_derivation():
    n = WEIGHT_PROVENANCE["wing_weight_lb"]["note"]
    assert "132.4" in n and "64" in n and "85.0" in n and "wings" in n


def test_engine_notes_say_what_changed():
    assert "AFT of the firewall" in WEIGHT_PROVENANCE["engine_cg_arm_in"]["note"]
    assert "249.1" in WEIGHT_PROVENANCE["engine_mass_kg"]["note"]
    assert "243" in WEIGHT_PROVENANCE["engine_dry_weight_lb"]["note"]
    assert "233.3" in WEIGHT_PROVENANCE["engine_displacement_ci"]["note"]
    assert "starter" in WEIGHT_PROVENANCE["starter_weight_lb"]["note"]
    assert 113.0 * 2.20462 == pytest.approx(249.1, abs=0.05)


def test_folded_analysis_values_are_the_book_values():
    assert (G.wing_span, G.wing_root_bl) == (314.0, 23.0)
    assert (G.winglet_height, G.winglet_root_chord, G.winglet_tip_chord) == (
        47.0,
        27.1,
        11.4,
    )
    assert G.wing_span == 2 * 157.0  # plans-1980:p126 tip rib BL 157
    for k in (
        "wing_span",
        "wing_root_bl",
        "winglet_height",
        "winglet_root_chord",
        "winglet_tip_chord",
    ):
        assert "M2.8" in GEOMETRY_PROVENANCE[k]["note"], k
    assert GEOMETRY_PROVENANCE["winglet_tip_chord"]["status"] == "derived-unsourced"
    assert "313.2" in GEOMETRY_PROVENANCE["wing_span"]["note"]


def test_om_sample_empty_is_the_closure_target_not_the_loaded_band():
    from core.ledger import load_ledger

    led = load_ledger()
    assert (led["empty"]["weight_lb"], led["empty"]["arm_in"]) == (730, 111.7)
    env = led["envelope"]
    assert (
        led["empty"]["arm_in"] > env["aft_fs"]
    )  # the empty CG is aft of the loaded limit
    # the loaded samples are what the 97 to 103 band grades (om-1980:p26)
    assert env["fwd_fs"] <= led["samples"]["heavy_pilot"]["book_cg_in"] <= env["aft_fs"]
    # the light pilot sample is OUTSIDE the aft limit, as the OM itself says (om-1980:p25)
    assert led["samples"]["light_pilot"]["book_cg_in"] > env["aft_fs"]
