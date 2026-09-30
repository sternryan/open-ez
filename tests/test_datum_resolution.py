"""
Datum Resolution Tests: FS Coordinate Translation & Reference Data Integrity
=============================================================================

Verifies:
1. GeometricParams.datum_offset_in correctly maps internal FS to published FS
2. reference_data.json has required schema with full provenance
3. StabilityMetrics.summary() shows dual FS display
4. Published NP in reference data matches translated internal NP
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from unittest.mock import MagicMock  # noqa: E402

sys.modules.setdefault("cadquery", MagicMock())
sys.modules.setdefault("OCP", MagicMock())

from config import config  # noqa: E402


# ---------------------------------------------------------------------------
# Datum offset field and method tests
# ---------------------------------------------------------------------------


class TestDatumOffset:
    """Verify the datum offset field and to_published_datum() method."""

    def test_datum_offset_field_exists(self):
        """config.geometry.datum_offset_in must be a float equal to 0.0 (code uses the published datum)."""
        offset = config.geometry.datum_offset_in
        assert isinstance(offset, float), (
            f"datum_offset_in should be float, got {type(offset)}"
        )
        assert offset == 0.0, f"datum_offset_in should be 0.0, got {offset}"

    def test_to_published_datum_method_exists(self):
        """to_published_datum() must be callable on GeometricParams."""
        assert callable(config.geometry.to_published_datum), (
            "config.geometry.to_published_datum() is not callable"
        )

    def test_to_published_datum_is_identity(self):
        """With datum_offset_in = 0, to_published_datum(x) == x."""
        for x in (0.0, 36.0, 99.0, 108.0, 153.5):
            assert config.geometry.to_published_datum(x) == x

    def test_round_trip_consistency(self):
        """internal = published + datum_offset_in identity must hold."""
        offset = config.geometry.datum_offset_in
        test_internal = 153.5
        published = config.geometry.to_published_datum(test_internal)
        recovered = published + offset
        assert abs(recovered - test_internal) < 1e-9, (
            f"Round-trip failed: internal={test_internal}, published={published:.4f}, "
            f"recovered={recovered:.4f}, offset={offset}"
        )

    def test_offset_is_zero(self):
        """datum_offset_in == 0: internal FS values are the published FS values."""
        assert config.geometry.datum_offset_in == 0.0, (
            f"datum_offset_in should be 0.0, got {config.geometry.datum_offset_in}"
        )


# ---------------------------------------------------------------------------
# reference_data.json schema integrity tests
# ---------------------------------------------------------------------------

REF_DATA_PATH = REPO_ROOT / "data" / "validation" / "reference_data.json"


def _load_ref_data():
    """Load reference_data.json from the repository root."""
    with open(REF_DATA_PATH) as f:
        return json.load(f)


class TestReferenceDataSchema:
    """Verify reference_data.json has required structure and provenance fields."""

    def test_reference_data_file_exists(self):
        """data/validation/reference_data.json must exist."""
        assert REF_DATA_PATH.exists(), (
            f"reference_data.json not found at {REF_DATA_PATH}"
        )

    def test_top_level_structure(self):
        """Top-level keys: metadata, sources, aircraft_specs, airfoil_data (community_builds removed 2026-09-29)."""
        data = _load_ref_data()
        required_keys = {"metadata", "sources", "aircraft_specs", "airfoil_data"}
        missing = required_keys - set(data.keys())
        assert not missing, (
            f"reference_data.json missing top-level keys: {missing}"
        )

    def test_sources_have_required_fields(self):
        """Each source entry must have title and type fields."""
        data = _load_ref_data()
        sources = data["sources"]
        for source_id, source in sources.items():
            assert "title" in source, (
                f"Source '{source_id}' missing 'title' field"
            )
            assert "type" in source, (
                f"Source '{source_id}' missing 'type' field"
            )

    def test_aircraft_specs_have_provenance(self):
        """Each aircraft_specs entry has an audit status and its matching provenance field."""
        data = _load_ref_data()
        specs = data["aircraft_specs"]
        assert len(specs) > 0, "aircraft_specs is empty"
        for spec_name, spec in specs.items():
            assert "source_id" not in spec, f"Spec '{spec_name}' still carries retired 'source_id'"
            status = spec.get("status")
            assert status in {"confirmed", "derived", "unverified"}, (
                f"Spec '{spec_name}' has no valid 'status'"
            )
            field = {"confirmed": "cite", "derived": "formula", "unverified": "was_cited"}[status]
            assert spec.get(field), f"Spec '{spec_name}' ({status}) missing '{field}' field"

    def test_airfoil_data_has_both_profiles(self):
        """airfoil_data must contain roncz_r1145ms and eppler_1230 entries."""
        data = _load_ref_data()
        airfoil_data = data["airfoil_data"]
        assert "roncz_r1145ms" in airfoil_data, (
            "airfoil_data missing 'roncz_r1145ms' entry (safety critical canard airfoil)"
        )
        assert "eppler_1230" in airfoil_data, (
            "airfoil_data missing 'eppler_1230' entry (main wing airfoil)"
        )

    def test_community_builds_removed(self):
        """community_builds was unsourced and is removed (Block 1 reference audit)."""
        data = _load_ref_data()
        assert "community_builds" not in data


# ---------------------------------------------------------------------------
# Cross-validation: reference_data.json vs. computed internal NP
# ---------------------------------------------------------------------------


class TestDatumReferenceDataConsistency:
    """Verify consistency between reference_data.json and computed physics values."""

    def test_published_np_is_unverified_not_truth(self):
        """The neutral point reference (108.0) is unverified: kept for history, never graded against.

        The model's NP is not compared to it. The accuracy report emits the NP metric as
        NOT GRADED, and truth_specs() excludes the entry.
        """
        from core.reference import truth_specs

        data = _load_ref_data()
        entry = data["aircraft_specs"]["neutral_point_fs"]
        assert entry["status"] == "unverified"
        assert "neutral_point_fs" not in truth_specs(data)

    def test_summary_shows_dual_display(self):
        """StabilityMetrics.summary() must contain '(internal)' and '(published)' labels."""
        from core.analysis import PhysicsEngine

        engine = PhysicsEngine()
        metrics = engine.calculate_cg_envelope()
        s = metrics.summary()

        assert "(internal)" in s, (
            "StabilityMetrics.summary() missing '(internal)' label. "
            "Dual FS display not implemented."
        )
        assert "(published)" in s, (
            "StabilityMetrics.summary() missing '(published)' label. "
            "Dual FS display not implemented."
        )

    def test_published_cg_range_is_reasonable(self):
        """Translated CG range limits must be within ±10 inches of reference data CG range.

        Verifies the datum translation produces CG limits consistent with
        the manual CG envelope (om-1980:p28, F.S. 97 to 103).
        """
        from core.analysis import PhysicsEngine

        data = _load_ref_data()
        ref_fwd = data["aircraft_specs"]["cg_range_fwd_fs"]["value"]
        ref_aft = data["aircraft_specs"]["cg_range_aft_fs"]["value"]

        engine = PhysicsEngine()
        metrics = engine.calculate_cg_envelope()

        computed_fwd_published = config.geometry.to_published_datum(metrics.cg_range_fwd)
        computed_aft_published = config.geometry.to_published_datum(metrics.cg_range_aft)

        fwd_delta = abs(computed_fwd_published - ref_fwd)
        aft_delta = abs(computed_aft_published - ref_aft)

        assert fwd_delta <= 10.0, (
            f"Computed forward CG limit (published: {computed_fwd_published:.2f} in) "
            f"differs from reference ({ref_fwd} in) by {fwd_delta:.2f} in, exceeding 10 in tolerance."
        )
        assert aft_delta <= 10.0, (
            f"Computed aft CG limit (published: {computed_aft_published:.2f} in) "
            f"differs from reference ({ref_aft} in) by {aft_delta:.2f} in, exceeding 10 in tolerance."
        )
