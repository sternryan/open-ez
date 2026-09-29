# tests/test_geometry_provenance.py
"""Every planform/station geometry value is sourced from the book or visibly flagged."""
import dataclasses
import re

from config.aircraft_config import GEOMETRY_PROVENANCE, PROVENANCE_STATUSES, GeometricParams

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
