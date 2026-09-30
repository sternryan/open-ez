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


def test_static_margin_metric_is_the_check_number():  # one static margin
    report = json.loads(REPORT.read_text())
    st = report["metadata"]["checks"]["stability"]
    assert st["aft_limit_fs"] == 103.0
    metric = next(m for m in report["metrics"] if m["metric_id"] == "static_margin_pct")
    assert abs(metric["computed"] - st["static_margin_pct"]) < 1e-6
    assert metric["grade"] == "NOT GRADED"


def test_vlm_marker_requires_root_bl_and_panel_span(tmp_path):
    from scripts.generate_accuracy_report import current_vlm_np

    good = {"wing_span_in": 300.0, "canard_span_in": 140.0, "wing_root_bl": 23.3, "wing_panel_span_in": 126.7}
    (tmp_path / "vspaero_native_polars.json").write_text(json.dumps({"neutral_point_fs": 110.0, "geometry": good}))
    args = (300.0, 140.0, 23.3, 126.7)
    _, reason = current_vlm_np(tmp_path, *args)
    assert "predates" not in reason
    for key in ("wing_root_bl", "wing_panel_span_in"):
        stale = {k: v for k, v in good.items() if k != key}
        (tmp_path / "vspaero_native_polars.json").write_text(json.dumps({"neutral_point_fs": 110.0, "geometry": stale}))
        val, reason = current_vlm_np(tmp_path, *args)
        assert val is None and "predates" in reason
