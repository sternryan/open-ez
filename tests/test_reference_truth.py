# tests/test_reference_truth.py
import json
from pathlib import Path

import pytest

from core.reference import truth_specs
from core.sources import check_citation

REF = json.loads((Path(__file__).resolve().parents[1] / "data/validation/reference_data.json").read_text())


def test_every_spec_has_an_audit_status():
    for k, e in REF["aircraft_specs"].items():
        assert e.get("status") in {"confirmed", "derived", "unverified"}, k
        if e["status"] == "confirmed":
            check_citation(e["cite"])
        if e["status"] == "derived":
            assert e.get("formula"), k


def test_truth_excludes_unverified():  # Review Focus 2
    fake = {"aircraft_specs": {"a": {"status": "confirmed", "cite": "om-1980:p3", "value": 1},
                               "b": {"status": "unverified", "value": 2}}}
    assert set(truth_specs(fake)) == {"a"}


def test_community_builds_removed():
    assert "community_builds" not in REF


def test_no_consumer_reads_aircraft_specs_directly():  # Review Focus 2
    root = Path(__file__).resolve().parents[1]
    for rel in ("scripts/generate_accuracy_report.py", "core/simulation/regression.py"):
        src = (root / rel).read_text()
        assert '["aircraft_specs"]' not in src, rel


def test_consumers_use_truth_specs():
    root = Path(__file__).resolve().parents[1]
    assert "truth_specs" in (root / "scripts/generate_accuracy_report.py").read_text()
    # regression.py reaches specs only via collect_metrics
    assert "aircraft_specs" not in (root / "core/simulation/regression.py").read_text()
