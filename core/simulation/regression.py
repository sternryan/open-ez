"""Physics regression against the externally-validated accuracy report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from config import config
from .openvsp_adapter import OpenVSPAdapter

# Phase 6: Default baseline is now the accuracy report (externally-validated)
# Every metric in this file traces to reference_data.json (published Long-EZ specs,
# wind tunnel data) — not to physics_baseline.json (self-referential).
DEFAULT_ACCURACY_REPORT = (
    Path(__file__).resolve().parents[2] / "data" / "validation" / "accuracy_report.json"
)


class RegressionRunner:
    """Run deterministic physics regressions for CI validation."""

    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance
        self.aero = OpenVSPAdapter()

    def compare_to_accuracy_report(
        self,
        accuracy_report_path: Path,
        report_dir: Path,
    ) -> Tuple[bool, Dict[str, float], List[str]]:
        """Compare current physics outputs against accuracy_report.json baselines.

        Unlike the old compare_to_baseline() (which compared against self-referential
        physics_baseline.json), this method compares against externally-validated
        values from the Phase 5 accuracy report. Each metric traces to
        reference_data.json (published Long-EZ specs, wind tunnel data).

        The comparison strategy:
        - Load PASS metrics from accuracy_report.json (FAIL metrics are known gaps,
          not regression targets)
        - Re-run collect_metrics() to get current computed values
        - Compare each current computed value against the accuracy report's stored
          computed value (the calibrated baseline) using each metric's tolerance_abs
        - Return (all_passed, current_values_dict, failure_messages)

        Args:
            accuracy_report_path: Path to accuracy_report.json.
            report_dir: Directory to write the regression report JSON.

        Returns:
            Tuple of (passed, current_values, failures) where:
                - passed: True if all PASS metrics are within tolerance
                - current_values: Dict of metric_id -> current computed value
                - failures: List of failure message strings
        """
        from unittest.mock import MagicMock
        import sys

        # CadQuery/OCP mock must be set before importing core analysis modules
        # (same pattern used in generate_accuracy_report.py)
        sys.modules.setdefault("cadquery", MagicMock())
        sys.modules.setdefault("OCP", MagicMock())

        from scripts.generate_accuracy_report import collect_metrics
        from core.analysis import PhysicsEngine

        report_dir.mkdir(parents=True, exist_ok=True)

        # Load accuracy_report.json (the externally-validated baseline)
        with open(accuracy_report_path, "r", encoding="utf-8") as f:
            accuracy_report = json.load(f)

        # Load reference_data.json (needed to re-run collect_metrics)
        ref_data_path = accuracy_report_path.parent / "reference_data.json"
        with open(ref_data_path, "r", encoding="utf-8") as f:
            ref_data = json.load(f)

        # Filter to PASS metrics only — FAIL metrics are known gaps, not regressions
        baseline_metrics = {
            m["metric_id"]: m
            for m in accuracy_report["metrics"]
            if m["grade"] == "PASS"
        }

        # Re-run physics engine to get current values
        engine = PhysicsEngine()
        current_metric_list = collect_metrics(ref_data, config, engine)
        current_values: Dict[str, float] = {
            m["metric_id"]: m["computed"] for m in current_metric_list
        }

        # Compare current values against calibrated baselines
        failures: List[str] = []
        for metric_id, baseline_m in baseline_metrics.items():
            if metric_id not in current_values:
                failures.append(f"Metric '{metric_id}' missing from current run")
                continue

            current_val = current_values[metric_id]
            baseline_val = baseline_m["computed"]  # calibrated baseline (Phase 5 run)
            tolerance_abs = baseline_m.get("tolerance_abs")

            if tolerance_abs is None:
                # Fall back to relative tolerance if no abs tolerance defined
                if baseline_val == 0:
                    deviation = abs(current_val - baseline_val)
                else:
                    deviation = abs(current_val - baseline_val) / abs(baseline_val)
                if deviation > self.tolerance:
                    failures.append(
                        f"{metric_id}: deviated by {deviation:.2%} "
                        f"(current {current_val:.4f} vs baseline {baseline_val:.4f})"
                    )
            else:
                error_abs = abs(current_val - baseline_val)
                if error_abs > tolerance_abs:
                    failures.append(
                        f"{metric_id}: abs error {error_abs:.6f} exceeds tolerance "
                        f"{tolerance_abs:.6f} "
                        f"(current {current_val:.4f} vs baseline {baseline_val:.4f})"
                    )

        # Write regression report
        regression_report = {
            "baseline_source": str(accuracy_report_path),
            "baseline_pass_metrics": list(baseline_metrics.keys()),
            "current_values": current_values,
            "tolerance": self.tolerance,
            "failures": failures,
            "status": "fail" if failures else "pass",
        }
        json_report = report_dir / "physics_accuracy_regression_report.json"
        with open(json_report, "w", encoding="utf-8") as f:
            json.dump(regression_report, f, indent=2)

        return (len(failures) == 0, current_values, failures)
