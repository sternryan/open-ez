import json
from pathlib import Path

from scripts.generate_accuracy_report import stability_at_aft_limit, two_method_np


def test_stable_at_aft_limit():
    r = stability_at_aft_limit(np_fs=106.0, aft_fs=103.0, mac_in=40.0)
    assert r["pass"] and r["static_margin_pct"] == 7.5


def test_unstable_at_aft_limit_fails():  # gate fails on a broken input
    assert not stability_at_aft_limit(np_fs=102.0, aft_fs=103.0, mac_in=40.0)["pass"]


def test_two_method_not_run_is_not_a_pass():  # Review Focus 5
    assert two_method_np(110.0, None, 1.0)["status"] == "not run"


def test_two_method_disagreement_fails():
    assert two_method_np(110.0, 113.0, 1.0)["status"] == "fail"
    assert two_method_np(110.0, 110.4, 1.0)["status"] == "pass"


REPORT = Path(__file__).resolve().parents[1] / "data" / "validation" / "accuracy_report.json"


def test_report_carries_both_checks():  # Review Focus 5, at report level
    report = json.loads(REPORT.read_text())
    checks = report["metadata"]["checks"]
    st = checks["stability"]
    assert st["aft_limit_fs"] == 103.0
    assert isinstance(st["pass"], bool)
    tm = checks["two_method_np"]
    assert tm["status"] in {"pass", "fail", "not run"}
    if tm["status"] == "not run":
        assert tm.get("reason", "").strip()
        # a not-run check must not be counted in the summary's pass total
        metric_passes = sum(1 for m in report["metrics"] if m["grade"].lower() == "pass")
        assert report["summary"]["pass"] == metric_passes
        assert "two_method_np" not in {m["metric_id"] for m in report["metrics"]}
