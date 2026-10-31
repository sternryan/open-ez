"""
compliance_audit script: is a non-compliant tracker a failure?
==============================================================

scripts/compliance_audit.py prints IN-PROGRESS below 51% and still exits 0.
It is also not run by CI. A gate must reject a non-compliant tracker; the script now
exits 1 below 51% and this test holds it to that.
"""

import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import core.compliance as compliance  # noqa: E402

SCRIPT = REPO_ROOT / "scripts" / "compliance_audit.py"


def test_audit_exits_nonzero_when_below_51_percent(tmp_path, monkeypatch):
    fresh = compliance.ComplianceTracker()
    monkeypatch.setattr(compliance, "compliance_tracker", fresh)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert not fresh.is_compliant
    assert exc.value.code not in (0, None)
