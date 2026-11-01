"""
compliance_audit script: report mode, eligibility gate, input integrity.

The audit reads real builder progress from a YAML file; nothing is simulated.
All outputs and progress files live under tmp_path.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from core.compliance import ComplianceTracker  # noqa: E402

SCRIPT = REPO_ROOT / "scripts" / "compliance_audit.py"
SHIPPED = REPO_ROOT / "data" / "compliance_progress.yaml"

_spec = importlib.util.spec_from_file_location("compliance_audit", SCRIPT)
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def _run(capsys, tmp_path, progress=None, *extra):
    argv = ["--out-dir", str(tmp_path / "out"), *extra]
    if progress is not None:
        argv += ["--progress", str(progress)]
    code, _ = audit.run(argv)
    cap = capsys.readouterr()
    return code, cap.out, cap.err


def _progress(tmp_path, entries):
    p = tmp_path / "progress.yaml"
    p.write_text(yaml.safe_dump({"completed": entries}))
    return p


def _entry(task_id, method="builder_manual", evidence="build log p1"):
    return {"task_id": task_id, "method": method, "date": "2026-01-02", "evidence": evidence}


def test_default_mode_on_shipped_empty_progress_exits_0(capsys, tmp_path):
    assert yaml.safe_load(SHIPPED.read_text())["completed"] == []
    code, out, _ = _run(capsys, tmp_path, SHIPPED)
    assert code == 0
    assert "0.0%" in out
    assert (tmp_path / "out" / "FAA_compliance_audit.md").exists()


def test_require_eligible_exits_nonzero_below_51(capsys, tmp_path):
    code, _, err = _run(capsys, tmp_path, SHIPPED, "--require-eligible")
    assert code == 1
    assert "below threshold" in err


def test_unknown_task_id_is_integrity_error(capsys, tmp_path):
    code, _, err = _run(capsys, tmp_path, _progress(tmp_path, [_entry("no_such_task")]))
    assert code == 1
    assert "unknown task_id" in err


@pytest.mark.parametrize("evidence", [None, "", "   "])
def test_missing_evidence_is_integrity_error(capsys, tmp_path, evidence):
    entry = _entry("paint", evidence=evidence)
    if evidence is None:
        del entry["evidence"]
    code, _, err = _run(capsys, tmp_path, _progress(tmp_path, [entry]))
    assert code == 1
    assert "evidence" in err


def test_unknown_method_and_duplicate_are_integrity_errors(capsys, tmp_path):
    code, _, err = _run(capsys, tmp_path, _progress(tmp_path, [_entry("paint", method="magic")]))
    assert code == 1 and "unknown method" in err
    dup = [_entry("paint"), _entry("paint")]
    code, _, err = _run(capsys, tmp_path, _progress(tmp_path, dup))
    assert code == 1 and "duplicate" in err


def test_missing_progress_file_fails(capsys, tmp_path):
    code, _, err = _run(capsys, tmp_path, tmp_path / "nope.yaml")
    assert code == 1 and "cannot read" in err


def test_all_tasks_builder_manual_is_fraction_1_and_eligible(capsys, tmp_path):
    ids = list(ComplianceTracker()._tasks)
    prog = _progress(tmp_path, [_entry(t) for t in ids])
    code, out, _ = _run(capsys, tmp_path, prog, "--require-eligible")
    assert code == 0
    assert "100.0%" in out


def test_credit_is_normalized_by_total_base_weight(capsys, tmp_path):
    fresh = ComplianceTracker()
    total = sum(t.base_credit for t in fresh._tasks.values())
    assert total != pytest.approx(1.0)  # base credits do not sum to 1
    ids = ["wing_cores_left", "wing_skins_left", "systems_integration"]
    x = sum(fresh.get_task(i).base_credit for i in ids)
    errors = audit.load_progress(fresh, _progress(tmp_path, [_entry(i) for i in ids]))
    assert errors == []
    assert fresh.raw_credit == pytest.approx(x)
    assert fresh.total_credit == pytest.approx(x / total)


def test_runs_do_not_mutate_global_singleton(capsys, tmp_path):
    import core.compliance as compliance

    prog = _progress(tmp_path, [_entry("paint")])
    _run(capsys, tmp_path, prog)
    assert not compliance.compliance_tracker.get_task("paint").completed


def test_integrity_errors_detects_bad_weights():
    t = ComplianceTracker()
    assert t.integrity_errors() == []
    t.get_task("paint").base_credit = 0.0
    t.get_task("nose_gear").base_credit = float("nan")
    errs = t.integrity_errors()
    assert len(errs) == 3
