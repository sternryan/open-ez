# tests/test_reference_truth.py
import json
from pathlib import Path


from core.reference import truth_airfoil, truth_specs
from core.sources import check_citation

REF = json.loads(
    (
        Path(__file__).resolve().parents[1] / "data/validation/reference_data.json"
    ).read_text()
)


def test_every_spec_has_an_audit_status():
    for k, e in REF["aircraft_specs"].items():
        assert e.get("status") in {"confirmed", "derived", "unverified"}, k
        if e["status"] == "confirmed":
            check_citation(e["cite"])
        if e["status"] == "derived":
            assert e.get("formula"), k


def test_truth_excludes_unverified():  # Review Focus 2
    fake = {
        "aircraft_specs": {
            "a": {"status": "confirmed", "cite": "om-1980:p3", "value": 1},
            "b": {"status": "unverified", "value": 2},
        }
    }
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


def test_every_airfoil_value_has_an_audit_status():
    for name, af in REF["airfoil_data"].items():
        vals = {k: e for k, e in af.items() if isinstance(e, dict) and "value" in e}
        assert vals, name
        assert "source_id" not in af and "facility" not in af, name
        for k, e in vals.items():
            assert e.get("status") in {"confirmed", "derived", "unverified"}, (name, k)
            if e["status"] == "confirmed":
                check_citation(e["cite"])
            if e["status"] == "derived":
                assert e.get("formula"), (name, k)
            if e["status"] == "unverified":
                assert e.get("was_cited") and e.get("why"), (name, k)
                assert "source_id" not in e and "confidence" not in e, (name, k)


def test_truth_airfoil_excludes_unverified():
    fake = {
        "airfoil_data": {
            "x": {
                "description": "d",
                "cl_max": {"status": "confirmed", "cite": "om-1980:p3", "value": 1},
                "cd_min": {"status": "unverified", "value": 2},
            }
        }
    }
    assert set(truth_airfoil(fake)["x"]) == {"cl_max"}
    assert all(v == {} for v in truth_airfoil(REF).values())


def test_airfoil_sources_removed():
    assert "roncz-wt" not in REF["sources"] and "eppler-report" not in REF["sources"]


def test_no_consumer_reads_airfoil_data_directly():
    root = Path(__file__).resolve().parents[1]
    for rel in ("scripts/generate_accuracy_report.py", "core/simulation/regression.py"):
        assert '["airfoil_data"]' not in (root / rel).read_text(), rel
    assert "truth_airfoil" in (root / "scripts/generate_accuracy_report.py").read_text()
