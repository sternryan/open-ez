"""
compliance_audit script: is a non-compliant tracker a failure?
==============================================================

scripts/compliance_audit.py prints IN-PROGRESS below 51% and still exits 0.
It is also not run by CI. A gate must reject a non-compliant tracker; this
test documents that and is a strict xfail until the script exits nonzero.
"""

import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import core.compliance as compliance  # noqa: E402

SCRIPT = REPO_ROOT / "scripts" / "compliance_audit.py"


@pytest.mark.xfail(
    strict=True,
    reason="scripts/compliance_audit.py exits 0 with IN-PROGRESS below 51% "
    "(compliance_audit.py:36-39) and is not run in CI",
)
def test_audit_exits_nonzero_when_below_51_percent(tmp_path, monkeypatch):
    fresh = compliance.ComplianceTracker()
    monkeypatch.setattr(compliance, "compliance_tracker", fresh)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert not fresh.is_compliant
    assert exc.value.code not in (0, None)
