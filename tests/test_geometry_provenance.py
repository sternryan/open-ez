# tests/test_geometry_provenance.py
"""Every planform/station geometry value is sourced from the book or visibly flagged."""
import dataclasses
import math
import re

import pytest

from core.sources import check_citation
from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    PROVENANCE_STATUSES,
    GeometricParams,
    StrakeConfig,
    StructuralWeightParams,
    config,
)

PATTERN = re.compile(r"^(fs_|canard_|wing_(span|root_chord|tip_chord|sweep_le|dihedral|root_bl|le_anchor)|datum_offset_in$|fuselage_length$)")


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
        if e["status"] in {"book", "cp-corrected", "derived"}:
            assert e["source"].strip(), f"{field}: a {e['status']} value needs a source"


def test_no_stale_provenance_entries():
    stale = sorted(set(GEOMETRY_PROVENANCE) - geometry_fields())
    assert stale == [], f"provenance for fields that no longer exist: {stale}"


OLD = {"fs_tail": 214.0}
SHIFT = 45.5


def test_canard_is_a_book_rectangle():
    g = config.geometry
    assert g.canard_sweep_le == 0.0
    assert g.canard_root_chord == g.canard_tip_chord == g.canard_chord
    assert g.canard_span == 141.6
    assert GEOMETRY_PROVENANCE["canard_sweep_le"]["status"] == "book"
    assert GEOMETRY_PROVENANCE["canard_sweep_le"]["source"].startswith("plans-1980:p71")


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
    assert g.fs_wing_le == pytest.approx(99.19, abs=0.01)  # 22.98 deg sweep, root BL 23.3
    assert GEOMETRY_PROVENANCE["wing_le_anchor"]["status"] == "cp-corrected"
    assert GEOMETRY_PROVENANCE["wing_le_anchor"]["source"].startswith("cp-text:p25")


def test_other_stations_shift_uniformly():  # Review Focus 3
    g = config.geometry
    for name, old in OLD.items():
        assert getattr(g, name) == pytest.approx(old - SHIFT), name
        assert GEOMETRY_PROVENANCE[name]["status"] == "converted-unsourced", name
    assert StrakeConfig().fs_trailing_edge == 145.0 - SHIFT
    # tail unsourced, so the length is left alone and flagged, not recomputed from the book nose
    assert g.fuselage_length == 214.0
    assert GEOMETRY_PROVENANCE["fuselage_length"]["status"] == "conflict"


def test_book_stations_block1():
    g = config.geometry
    assert g.fs_nose == pytest.approx(-6.8)
    assert g.fs_firewall == pytest.approx(125.0)
    assert g.fs_pilot_seat == pytest.approx(59.0)
    assert g.fs_rear_seat == pytest.approx(103.0)
    for name in ("fs_nose", "fs_firewall", "fs_pilot_seat", "fs_rear_seat"):
        assert GEOMETRY_PROVENANCE[name]["status"] == "book", name
    assert GEOMETRY_PROVENANCE["fs_nose"]["source"].startswith("plans-1980:p171")
    assert StrakeConfig().fs_leading_edge == pytest.approx(50.0)
    w = StructuralWeightParams()
    assert w.canard_arm_in == pytest.approx(g.fs_canard_le + 0.25 * g.canard_chord)
    assert w.fuel_arm_in == pytest.approx(104.5)
    assert g.fuselage_length == 214.0
    assert GEOMETRY_PROVENANCE["fuselage_length"]["status"] == "conflict"


def test_weight_arms_shift_uniformly():
    old = {
        "wing_arm_in": 140.0, "fuselage_arm_in": 100.0,
        "landing_gear_arm_in": 130.0, "electrical_arm_in": 165.0,
        "instruments_arm_in": 75.0, "interior_arm_in": 95.0,
    }
    w = StructuralWeightParams()
    for name, o in old.items():
        assert getattr(w, name) == pytest.approx(o - SHIFT), name


def test_sourced_entries_cite_the_registry():  # Review Focus 1
    for field, e in GEOMETRY_PROVENANCE.items():
        if e["status"] in {"book", "cp-corrected", "derived"}:
            check_citation(e["source"])  # raises on unknown id or bad form


def test_wing_planform_is_the_book():  # Task 7
    g = config.geometry
    P = GEOMETRY_PROVENANCE
    assert g.wing_span == 313.2
    assert g.wing_sweep_le == 22.98
    assert g.wing_tip_chord == 20.0
    assert g.wing_dihedral == 0.0
    assert g.wing_root_bl == 23.3
    assert (P["wing_span"]["status"], P["wing_span"]["source"]) == ("book", "om-1980:p3 wing span 26.1 ft")
    assert (P["wing_sweep_le"]["status"], P["wing_sweep_le"]["source"]) == ("book", "plans-1980:p126 22.98 deg LE sweep")
    assert (P["wing_tip_chord"]["status"], P["wing_tip_chord"]["source"]) == ("book", "plans-1980:p126 chord 20.0 at B.L. 157")
    assert (P["wing_dihedral"]["status"], P["wing_dihedral"]["source"]) == (
        "book", "plans-1980:p134 wing flat at 17.4 waterline plane")
    assert P["wing_root_bl"]["status"] == "unsourced"


def test_wing_root_chord_is_derived_from_the_printed_chords():
    inputs = (42.7, 55.5, 20.0, 157.0, 23.3)  # chord at 55.5, BL, tip chord, tip BL, root BL
    c1, bl1, c2, bl2, bl0 = inputs
    root = c1 + (bl1 - bl0) * (c1 - c2) / (bl2 - bl1)
    assert config.geometry.wing_root_chord == pytest.approx(round(root, 2), abs=1e-9)
    assert config.geometry.wing_root_chord == 49.90
    e = GEOMETRY_PROVENANCE["wing_root_chord"]
    assert e["status"] == "derived"
    assert e["source"] == "plans-1980:p126 chords 42.7 at BL 55.5, 20.0 at BL 157"
    assert "42.7 + (55.5-23.3)*(42.7-20.0)/(157-55.5)" in e["note"]
    # the printed mid chord (31.35 at BL 106.25) lies on the same straight taper
    assert c1 + (106.25 - bl1) * (c2 - c1) / (bl2 - bl1) == pytest.approx(31.35, abs=0.01)


def test_canard_planform_is_the_gu_planform_flagged_conflict():
    g = config.geometry
    P = GEOMETRY_PROVENANCE
    import config.aircraft_config as ac
    assert (ac.CHORD, ac.CHORD_STATUS, ac.CHORD_SOURCE) == (13.02, "conflict", "om-1980:p3 GU canard 11.8 ft, 12.8 sq ft")
    assert g.canard_chord == 13.02
    assert g.canard_span == 141.6
    assert P["canard_chord"]["status"] == "conflict"
    assert P["canard_chord"]["source"] == "om-1980:p3 GU canard 11.8 ft, 12.8 sq ft"
    assert P["canard_chord"]["note"] == "GU planform (om-1980 p3); Roncz planform unconfirmed; chord = 12.8*144/141.6"
    assert P["canard_span"]["status"] == "conflict"
    assert P["canard_span"]["source"] == "om-1980:p3 canard span 11.8 ft"
    assert 12.8 * 144 / 141.6 == pytest.approx(13.02, abs=0.005)
    assert P["canard_incidence"]["status"] == "unsourced"
    assert "CP 47" in P["canard_incidence"]["note"]


def test_canard_height_above_the_wing_plane():
    g = config.geometry
    P = GEOMETRY_PROVENANCE
    assert g.wing_le_wl == 0.0
    assert g.canard_le_wl == 1.5
    assert g.canard_vertical_offset_in == 1.5
    for k in ("canard_le_wl", "canard_vertical_offset_in"):
        assert P[k]["status"] == "conflict", k
        assert P[k]["source"] == "plans-1980:p171 W.L. 18.9 at canard", k
    assert 18.9 - 17.4 == pytest.approx(1.5)


def test_canard_arm_follows_the_chord():
    w = StructuralWeightParams()
    assert w.canard_arm_in == pytest.approx(18.7 + 0.25 * 13.02)


def test_canard_area_matches_chord_times_span_and_the_manual():
    g = config.geometry
    area = g.canard_area
    assert area == pytest.approx(g.canard_chord * g.canard_span / 144, abs=0.01)
    assert area == pytest.approx(12.8, abs=0.01)  # om-1980:p3 GU canard area


def test_derived_status_is_recognised():
    assert "derived" in PROVENANCE_STATUSES
