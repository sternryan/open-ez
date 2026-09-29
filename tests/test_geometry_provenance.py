# tests/test_geometry_provenance.py
"""Every planform/station geometry value is sourced from the book or visibly flagged."""
import dataclasses
import math
import re

import pytest

from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    PROVENANCE_STATUSES,
    GeometricParams,
    StrakeConfig,
    StructuralWeightParams,
    config,
)

PATTERN = re.compile(r"^(fs_|canard_|wing_(span|root_chord|tip_chord|sweep_le|dihedral|root_bl|le_anchor)|datum_offset_in$)")


def geometry_fields() -> set[str]:
    return {f.name for f in dataclasses.fields(GeometricParams) if PATTERN.match(f.name)}


def test_every_geometry_field_has_provenance():
    missing = sorted(geometry_fields() - set(GEOMETRY_PROVENANCE))
    assert missing == [], f"add GEOMETRY_PROVENANCE entries for: {missing}"


def test_provenance_entries_are_well_formed():
    for field, e in GEOMETRY_PROVENANCE.items():
        assert set(e) == {"status", "source", "confidence", "note"}, field
        assert e["status"] in PROVENANCE_STATUSES, (field, e["status"])
        assert e["confidence"] in {"high", "medium", "low", "n/a"}, (field, e["confidence"])
        if e["status"] in {"book", "cp-corrected"}:
            assert e["source"].strip(), f"{field}: a {e['status']} value needs a source"


def test_no_stale_provenance_entries():
    stale = sorted(set(GEOMETRY_PROVENANCE) - geometry_fields())
    assert stale == [], f"provenance for fields that no longer exist: {stale}"


OLD = {"fs_pilot_seat": 80.0, "fs_rear_seat": 115.0, "fs_firewall": 180.0, "fs_tail": 214.0, "fs_nose": 0.0}
SHIFT = 45.5


def test_canard_is_a_book_rectangle():
    g = config.geometry
    assert g.canard_sweep_le == 0.0
    assert g.canard_root_chord == g.canard_tip_chord == g.canard_chord
    assert g.canard_span == 126.0
    assert GEOMETRY_PROVENANCE["canard_sweep_le"]["status"] == "book"
    assert "p.71" in GEOMETRY_PROVENANCE["canard_sweep_le"]["source"]


def test_chord_aliases_are_read_only():  # Review Focus 2
    with pytest.raises(AttributeError):
        config.geometry.canard_root_chord = 17.0
    with pytest.raises(AttributeError):
        config.geometry.canard_tip_chord = 13.5


def test_frame_is_published():
    assert config.geometry.datum_offset_in == 0.0
    assert config.geometry.to_published_datum(100.0) == 100.0


def test_book_stations():
    g = config.geometry
    assert g.fs_canard_le == 18.7
    fs, bl = g.wing_le_anchor
    assert (fs, bl) == (113.9, 58.0)
    expect = 113.9 - (58.0 - g.wing_root_bl) * math.tan(math.radians(g.wing_sweep_le))
    assert g.fs_wing_le == pytest.approx(expect)
    assert g.fs_wing_le == pytest.approx(97.72, abs=0.01)  # 25 deg sweep, root BL 23.3
    assert GEOMETRY_PROVENANCE["wing_le_anchor"]["status"] == "cp-corrected"
    assert "CP25" in GEOMETRY_PROVENANCE["wing_le_anchor"]["source"]


def test_other_stations_shift_uniformly():  # Review Focus 3
    g = config.geometry
    for name, old in OLD.items():
        assert getattr(g, name) == pytest.approx(old - SHIFT), name
        assert GEOMETRY_PROVENANCE[name]["status"] == "converted-unsourced", name
    s = StrakeConfig()
    assert (s.fs_leading_edge, s.fs_trailing_edge) == (110.0 - SHIFT, 145.0 - SHIFT)
    assert g.fuselage_length == 214.0 == g.fs_tail - g.fs_nose


def test_weight_arms_shift_uniformly():
    old = {
        "wing_arm_in": 140.0, "canard_arm_in": 45.0, "fuselage_arm_in": 100.0,
        "landing_gear_arm_in": 130.0, "electrical_arm_in": 165.0,
        "instruments_arm_in": 75.0, "interior_arm_in": 95.0, "fuel_arm_in": 127.5,
    }
    w = StructuralWeightParams()
    for name, o in old.items():
        assert getattr(w, name) == pytest.approx(o - SHIFT), name
