import json
from pathlib import Path

import pytest

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


REPORT = (
    Path(__file__).resolve().parents[1] / "data" / "validation" / "accuracy_report.json"
)


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
        metric_passes = sum(
            1 for m in report["metrics"] if m["grade"].lower() == "pass"
        )
        assert report["summary"]["pass"] == metric_passes
        assert "two_method_np" not in {m["metric_id"] for m in report["metrics"]}


def test_static_margin_metric_is_the_check_number():  # one static margin
    report = json.loads(REPORT.read_text())
    st = report["metadata"]["checks"]["stability"]
    assert st["aft_limit_fs"] == 103.0
    metric = next(m for m in report["metrics"] if m["metric_id"] == "static_margin_pct")
    assert abs(metric["computed"] - st["static_margin_pct"]) < 1e-6
    assert metric["grade"] == "NOT GRADED"


def _vlm_fixture(tmp_path, np_fs, geometry):
    (tmp_path / "vspaero_np.json").write_text(
        json.dumps({"np_fs": np_fs, "geometry": geometry, "timestamp": "t0"})
    )


def test_vlm_marker_requires_root_bl_and_panel_span(tmp_path):
    from config.aircraft_config import config
    from scripts.generate_accuracy_report import current_vlm_np
    from scripts.vspaero_np import geometry_marker

    good = geometry_marker(config.geometry)
    _vlm_fixture(tmp_path, 110.0, good)
    val, reason = current_vlm_np(tmp_path, good)
    assert val == 110.0 and reason == ""
    # the last two keys: a run of the exposed panels only (pre ledger C2) is stale
    for key in (
        "wing_root_bl",
        "wing_panel_span_in",
        "wing_centerline_chord_in",
        "vlm_wing_inboard_bl",
    ):
        _vlm_fixture(tmp_path, 110.0, {k: v for k, v in good.items() if k != key})
        val, reason = current_vlm_np(tmp_path, good)
        assert val is None and "predates" in reason


def test_two_method_reads_vspaero_np_json_stale_geometry_is_not_run(tmp_path):
    from config.aircraft_config import config
    from scripts.generate_accuracy_report import two_method_check
    from scripts.vspaero_np import geometry_marker

    stale = {**geometry_marker(config.geometry)}
    stale["wing_span_in"] += 3.6  # the retired 316.8 span
    _vlm_fixture(tmp_path, 108.0, stale)
    r = two_method_check(tmp_path, config.geometry, 108.0)
    assert r["status"] == "not run" and r["vlm"] is None
    assert "predates" in r["reason"] and "wing_span_in" in r["reason"]


def test_two_method_missing_vlm_file_is_not_run(tmp_path):
    from config.aircraft_config import config
    from scripts.generate_accuracy_report import two_method_check

    r = two_method_check(tmp_path, config.geometry, 108.0)
    assert r["status"] == "not run" and "vspaero_np.json" in r["reason"]


def test_two_method_current_vlm_file_grades_by_the_1in_bound(tmp_path):
    from config.aircraft_config import config
    from scripts.generate_accuracy_report import two_method_check
    from scripts.vspaero_np import geometry_marker

    current = geometry_marker(config.geometry)
    _vlm_fixture(tmp_path, 108.5, current)
    r = two_method_check(tmp_path, config.geometry, 108.0)
    assert r["status"] == "pass" and r["vlm"] == 108.5
    _vlm_fixture(tmp_path, 110.0, current)
    r = two_method_check(tmp_path, config.geometry, 108.0)
    assert r["status"] == "fail" and abs(r["delta"] - 2.0) < 1e-9


@pytest.mark.xfail(
    strict=True,
    reason="see docs/geometry-correction-ledger.md rows 53 and 54; analytic 110.68 vs VLM 112.36, delta +1.68 in against the 1.0 in bound (C4 partial-span downwash)",
)
def test_committed_report_two_method_np_agrees():
    """External check: the committed report's analytic and VLM NPs agree within the 1.0 in bound."""
    tm = json.loads(REPORT.read_text())["metadata"]["checks"]["two_method_np"]
    assert (
        tm["status"] == "pass"
    ), f"two-method NP {tm['status']}: delta {tm.get('delta')} in"
