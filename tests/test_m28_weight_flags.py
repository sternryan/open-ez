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


def test_flagged_fields_exist_and_keep_their_values():
    values = {
        "wing_weight_lb": 85.0,
        "engine_cg_arm_in": 8.0,
        "engine_mass_kg": 113.0,
        "engine_dry_weight_lb": 243.0,
        "electrical_weight_lb": 25.0,
        "electrical_arm_in": 119.5,
        "tank_volume_gal": 26.0,
    }
    assert set(values) == set(WEIGHT_PROVENANCE)
    for name, v in values.items():
        assert _field_value(name) == v, name


def test_entries_are_well_formed_and_never_book():
    for name, e in WEIGHT_PROVENANCE.items():
        assert set(e) == {"status", "source", "confidence", "note"}, name
        assert e["status"] in PROVENANCE_STATUSES, name
        assert e["status"] in {"conflict", "unsourced"}, name  # flags, not sources


def test_wing_weight_names_both_values():
    n = WEIGHT_PROVENANCE["wing_weight_lb"]["note"]
    assert "85.0" in n and "64 lb" in n and "128" in n and "CP26" in n


def test_engine_flags_say_what_contradicts():
    assert "aft of the firewall" in WEIGHT_PROVENANCE["engine_cg_arm_in"]["note"]
    assert "249.1" in WEIGHT_PROVENANCE["engine_mass_kg"]["note"]
    assert "243" in WEIGHT_PROVENANCE["engine_dry_weight_lb"]["note"]
    assert "station 150+" in WEIGHT_PROVENANCE["electrical_weight_lb"]["note"]
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
