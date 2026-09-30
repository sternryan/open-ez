"""
Generate Accuracy Report: Per-Metric Grading Against External Reference Data
=============================================================================

This script grades every validated Long-EZ metric (NP, CG fwd/aft, static margin,
stall speed, CLmax, alpha_0L, weights, wing area) against curated values from
reference_data.json and vspaero_native_polars.json. No self-referential sources
(physics_baseline.json) are permitted.

Output: data/validation/accuracy_report.json

Purpose: Provide the machine-readable accuracy report Phase 6 uses to lock
regression tests. Traceability enforcement breaks the self-referential
validation loop established by physics_baseline.json.

Usage:
    cd /path/to/open-ez
    python3 scripts/generate_accuracy_report.py
    python3 main.py --accuracy-report   (identical output)
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

# --- CadQuery/OCP mock MUST be set before any core/ imports -----------------
# Analysis modules import CadQuery lazily. Without this mock, importing
# core.analysis raises ImportError in environments without CadQuery installed.
sys.modules.setdefault("cadquery", MagicMock())
sys.modules.setdefault("OCP", MagicMock())

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from core.reference import truth_airfoil, truth_specs  # noqa: E402
from core.sources import check_citation  # noqa: E402

NOT_GRADED = "NOT GRADED"
_USE_ENTRY = object()


# ---------------------------------------------------------------------------
# Core grading logic
# ---------------------------------------------------------------------------


def grade_metric(
    computed: float,
    reference: float,
    tolerance_abs: float | None = None,
    tolerance_pct: float | None = None,
) -> tuple[str, float, float]:
    """
    Grade a computed metric against a reference value.

    Grading bands:
        PASS:      error <= tolerance
        MARGINAL:  tolerance < error <= 2 * tolerance
        FAIL:      error > 2 * tolerance
        UNGRADED:  no tolerance specified

    Args:
        computed: Computed value from the physics model.
        reference: Reference (published / wind-tunnel) value.
        tolerance_abs: Absolute tolerance (same units as values).
        tolerance_pct: Percentage tolerance (0-100 scale, e.g. 5.0 = 5%).
            Only used if tolerance_abs is None.

    Returns:
        Tuple of (grade_str, error_abs, error_pct) where:
            - grade_str: one of "PASS", "MARGINAL", "FAIL", "UNGRADED"
            - error_abs: absolute error |computed - reference|
            - error_pct: percentage error (relative to |reference|), 0.0 if reference==0
    """
    error_abs = abs(computed - reference)
    if reference != 0.0:
        error_pct = error_abs / abs(reference) * 100.0
    else:
        error_pct = 0.0

    # Determine which tolerance band to use
    if tolerance_abs is not None:
        tol = tolerance_abs
        error_for_grading = error_abs
    elif tolerance_pct is not None:
        tol = tolerance_pct
        error_for_grading = error_pct
    else:
        return ("UNGRADED", round(error_abs, 6), round(error_pct, 6))

    if error_for_grading <= tol:
        grade = "PASS"
    elif error_for_grading <= 2.0 * tol:
        grade = "MARGINAL"
    else:
        grade = "FAIL"

    return (grade, round(error_abs, 6), round(error_pct, 6))


def spec_fields(
    truth: dict,
    key: str,
    computed: float,
    *,
    tolerance_abs: object = _USE_ENTRY,
) -> dict:
    """
    Grade ``computed`` against ``truth[key]`` (a confirmed or derived entry).

    A key absent from ``truth`` (its reference is unverified) is never skipped: the
    metric keeps its computed value and is emitted with grade "NOT GRADED".
    """
    entry = truth.get(key)
    if entry is None:
        return {
            "computed": round(computed, 4),
            "reference": None,
            "tolerance_abs": None,
            "tolerance_pct": None,
            "error_abs": None,
            "error_pct": None,
            "grade": NOT_GRADED,
            "reason": "reference unverified",
        }
    tol_abs = entry.get("tolerance_abs") if tolerance_abs is _USE_ENTRY else tolerance_abs
    tol_pct = entry.get("tolerance_pct") if tolerance_abs is _USE_ENTRY else None
    grade, err_abs, err_pct = grade_metric(
        computed, entry["value"], tolerance_abs=tol_abs, tolerance_pct=tol_pct
    )
    return {
        "computed": round(computed, 4),
        "reference": entry["value"],
        "tolerance_abs": tol_abs,
        "tolerance_pct": tol_pct,
        "error_abs": err_abs,
        "error_pct": err_pct,
        "grade": grade,
    }


def validate_sources(report: dict, ref_data: dict) -> None:
    """
    Validate that all metric sources in the report are traceable and not self-referential.

    Raises:
        ValueError: If any metric source:
            - Contains "physics_baseline.json" (self-referential, forbidden)
            - Is not a recognized reference_data.json key or "vspaero_native"

    Args:
        report: The accuracy report dict (must have "metrics" list).
        ref_data: The loaded reference_data.json dict.
    """
    # Build valid source set from reference_data.json keys
    valid_sources: set[str] = {"vspaero_native"}
    # aircraft_specs: only confirmed/derived entries are truth; confirmed ones must
    # carry a registry citation (the new `cite` form replaces source_id).
    for top_key, entry in truth_specs(ref_data).items():
        if entry["status"] == "confirmed":
            check_citation(entry["cite"])
        valid_sources.add(f"reference_data.json:aircraft_specs.{top_key}")
    # Unverified specs are still legitimate to name as a source of a NOT GRADED metric.
    for top_key, entry in ref_data.get("aircraft_specs", {}).items():
        if entry.get("status") == "unverified":
            valid_sources.add(f"reference_data.json:aircraft_specs.{top_key}")
    # airfoil_data: confirmed entries must carry a registry citation; unverified entries
    # need no source id and are still legitimate sources of NOT GRADED metrics.
    for name, entries in truth_airfoil(ref_data).items():
        for key, entry in entries.items():
            if entry["status"] == "confirmed":
                check_citation(entry["cite"])
    for name, af in ref_data.get("airfoil_data", {}).items():
        valid_sources.add(f"reference_data.json:airfoil_data.{name}")
        for key, e in af.items():
            if isinstance(e, dict):
                valid_sources.add(f"reference_data.json:airfoil_data.{name}.{key}")

    for metric in report.get("metrics", []):
        source = metric.get("source", "")
        if "physics_baseline.json" in source:
            raise ValueError(
                f"Metric '{metric.get('metric_id')}' source '{source}' references "
                f"physics_baseline.json — self-referential sources are forbidden. "
                f"All sources must trace to reference_data.json or vspaero_native."
            )
        if source not in valid_sources:
            raise ValueError(
                f"Metric '{metric.get('metric_id')}' source '{source}' "
                f"not in valid source set. Expected one of: {sorted(valid_sources)[:5]}..."
            )


def load_vspaero_provenance(data_dir: Path) -> dict:
    """
    Load VSPAERO provenance metadata from vspaero_native_polars.json.

    Returns a dict with vsp_version, run_timestamp, solver_settings.
    Falls back to a placeholder dict if the file is missing.

    Args:
        data_dir: Directory containing vspaero_native_polars.json.

    Returns:
        Dict with provenance metadata.
    """
    polars_path = data_dir / "vspaero_native_polars.json"
    if not polars_path.exists():
        return {
            "vsp_version": "not_available",
            "run_timestamp": "not_available",
            "solver_settings": {},
            "note": "vspaero_native_polars.json not found — no native VSPAERO data",
        }

    with open(polars_path, encoding="utf-8") as f:
        polars = json.load(f)

    return {
        "vsp_version": polars.get("vsp_version", "unknown"),
        "run_timestamp": polars.get("timestamp", "unknown"),
        "solver_settings": polars.get("solver_settings", {}),
    }


# ---------------------------------------------------------------------------
# Physics checks (Block 1 Task 8): stability at the aft limit, two-method NP
# ---------------------------------------------------------------------------

TWO_METHOD_NP_BOUND_IN = 1.0
# A VSPAERO run is "current" only if it records an NP and the geometry it ran on matches config.


def stability_at_aft_limit(np_fs: float, aft_fs: float, mac_in: float) -> dict:
    """NP must lie aft of the manual's aft CG limit (positive static margin there)."""
    margin = round((np_fs - aft_fs) / mac_in * 100.0, 6)
    return {
        "np_fs": np_fs,
        "aft_limit_fs": aft_fs,
        "static_margin_pct": round(margin, 4),
        "pass": bool(np_fs > aft_fs),
    }


def two_method_np(analytic: float, vlm: float | None, bound_in: float) -> dict:
    """Analytic vs vortex-lattice NP. None (no VLM run) is 'not run', never a pass."""
    if vlm is None:
        return {"status": "not run", "analytic": analytic, "vlm": None,
                "delta": None, "bound_in": bound_in}
    delta = abs(analytic - vlm)
    return {"status": "pass" if delta <= bound_in else "fail", "analytic": analytic,
            "vlm": vlm, "delta": delta, "bound_in": bound_in}


VLM_NP_FILE = "vspaero_np.json"  # written by `python3.13 scripts/vspaero_np.py`


def current_vlm_np(data_dir: Path, marker: dict[str, float]) -> tuple[float | None, str]:
    """Return (VLM NP in published FS, reason). None means no CURRENT run.

    Conservative: vspaero_np.json must carry an explicit ``np_fs`` AND a ``geometry`` block in
    which every key of ``marker`` (scripts.vspaero_np.geometry_marker of the live config: spans,
    wing root BL, panel span, chords, sweeps, incidences, stations) matches to 0.05.
    """
    path = data_dir / VLM_NP_FILE
    try:
        run = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, f"{VLM_NP_FILE} missing or unreadable (run: python3.13 scripts/vspaero_np.py)"
    np_val = run.get("np_fs")
    geom = run.get("geometry") or {}
    stale = sorted(
        k for k, v in marker.items()
        if not isinstance(geom.get(k), (int, float)) or abs(float(geom[k]) - v) >= 0.05
    )
    why = []
    if not isinstance(np_val, (int, float)):
        why.append(f"{VLM_NP_FILE} holds no neutral point")
    if stale:
        why.append(
            f"{VLM_NP_FILE} ({run.get('timestamp', 'no timestamp')}) geometry does not match the "
            f"current config ({', '.join(stale)}), so it predates the current geometry"
        )
    if why:
        return None, "; ".join(why)
    return float(np_val), ""


def two_method_check(data_dir: Path, geo: object, analytic: float) -> dict:
    """two_method_np() fed by vspaero_np.json when its geometry block is current."""
    from scripts.vspaero_np import geometry_marker

    vlm, reason = current_vlm_np(data_dir, geometry_marker(geo))
    two = two_method_np(analytic, vlm, TWO_METHOD_NP_BOUND_IN)
    if two["status"] == "not run":
        two["reason"] = reason or "no current VLM run"
    else:
        run = json.loads((data_dir / VLM_NP_FILE).read_text(encoding="utf-8"))
        two["vlm_source"] = {
            "file": f"data/validation/{VLM_NP_FILE}",
            "vsp_version": run.get("vsp_version"),
            "timestamp": run.get("timestamp"),
            "method": run.get("method"),
        }
    return two


def compute_checks(engine: object, config_module: object, data_dir: Path) -> dict:
    """Assemble metadata.checks."""
    from core.ledger import load_ledger  # noqa: E402

    geo = config_module.geometry  # type: ignore[attr-defined]
    np_fs = geo.to_published_datum(engine.calculate_cg_envelope().neutral_point)  # type: ignore[attr-defined]
    # MAC: PhysicsEngine.calculate_mac() in core/analysis.py (the MAC used for static margin).
    mac_in, _ = engine.calculate_mac()  # type: ignore[attr-defined]
    aft_fs = float(load_ledger()["envelope"]["aft_fs"])
    return {
        "stability": {**stability_at_aft_limit(np_fs, aft_fs, mac_in), "mac_in": mac_in},
        "two_method_np": two_method_check(data_dir, geo, np_fs),
    }


def collect_metrics(
    ref_data: dict,
    config_module: object,
    engine: object,
) -> list[dict]:
    """
    Compute all validated metrics and assemble metric dicts.

    Each metric dict contains:
        metric_id, description, computed, reference, tolerance_abs, tolerance_pct,
        error_abs, error_pct, grade, source, units

    Args:
        ref_data: Loaded reference_data.json.
        config_module: The config module (config object with .geometry, .aero_limits, etc.).
        engine: PhysicsEngine instance with .calculate_cg_envelope() method.

    Returns:
        List of metric dicts.
    """
    metrics: list[dict] = []
    specs = truth_specs(ref_data)
    airfoils = truth_airfoil(ref_data)
    geo = config_module.geometry  # type: ignore[attr-defined]

    # -------------------------------------------------------------------------
    # Stability metrics (from PhysicsEngine)
    # -------------------------------------------------------------------------
    stability = engine.calculate_cg_envelope()  # type: ignore[union-attr]

    # --- Neutral Point ---
    computed_np_pub = geo.to_published_datum(stability.neutral_point)
    metrics.append(
        {
            "metric_id": "neutral_point_fs",
            "description": "Longitudinal Neutral Point (published datum)",
            **spec_fields(specs, "neutral_point_fs", computed_np_pub),
            "source": "reference_data.json:aircraft_specs.neutral_point_fs",
            "units": "inches (published FS datum)",
        }
    )

    # --- CG Forward Limit ---
    computed_cg_fwd_pub = geo.to_published_datum(stability.cg_range_fwd)
    metrics.append(
        {
            "metric_id": "cg_range_fwd_fs",
            "description": "Forward CG limit (published datum)",
            **spec_fields(specs, "cg_range_fwd_fs", computed_cg_fwd_pub),
            "source": "reference_data.json:aircraft_specs.cg_range_fwd_fs",
            "units": "inches (published FS datum)",
        }
    )

    # --- CG Aft Limit ---
    computed_cg_aft_pub = geo.to_published_datum(stability.cg_range_aft)
    metrics.append(
        {
            "metric_id": "cg_range_aft_fs",
            "description": "Aft CG limit (published datum)",
            **spec_fields(specs, "cg_range_aft_fs", computed_cg_aft_pub),
            "source": "reference_data.json:aircraft_specs.cg_range_aft_fs",
            "units": "inches (published FS datum)",
        }
    )

    # --- Static Margin ---
    # ONE number: the same stability_at_aft_limit() that feeds metadata.checks.stability.
    # (NP - manual aft CG limit FS 103) / MAC. Deliberately NOT the model's own CG-aft
    # (StabilityMetrics.static_margin), which is a different quantity.
    from core.ledger import load_ledger  # noqa: E402

    mac_in, _ = engine.calculate_mac()  # type: ignore[union-attr]
    sm_check = stability_at_aft_limit(
        computed_np_pub, float(load_ledger()["envelope"]["aft_fs"]), mac_in
    )
    metrics.append(
        {
            "metric_id": "static_margin_pct",
            "description": "Static margin at the manual's aft CG limit FS 103 (om-1980:p28), % MAC",
            **spec_fields(specs, "static_margin_pct", sm_check["static_margin_pct"]),
            "source": "reference_data.json:aircraft_specs.static_margin_pct",
            "notes": "Static margin at the manual's aft CG limit FS 103 (om-1980:p28): (NP - 103.0) / MAC x 100, from stability_at_aft_limit(); identical to metadata.checks.stability.static_margin_pct. Reference (12.0) unverified, not graded.",
            "units": "percent MAC",
        }
    )

    # -------------------------------------------------------------------------
    # Performance metrics
    # -------------------------------------------------------------------------

    # --- Stall Speed (first-principles, confirmed reference areas) ---
    wing_area_sqft = specs["wing_area_sqft"]["value"]  # confirmed (om-1980:p3)
    canard_area_sqft = specs["canard_area_sqft"]["value"]  # confirmed (om-1980:p3)
    total_area_sqft = wing_area_sqft + canard_area_sqft
    W = config_module.flight_condition.gross_weight_lb  # type: ignore[attr-defined]
    rho = 0.002377  # slug/ft^3 sea-level standard atmosphere
    cl_max = config_module.aero_limits.canard_clmax  # type: ignore[attr-defined]  # canard stalls first
    v_fps = math.sqrt(2.0 * W / (rho * total_area_sqft * cl_max))
    computed_stall_ktas = v_fps / 1.6878  # 1 knot = 1.6878 ft/s

    metrics.append(
        {
            "metric_id": "stall_speed_ktas",
            "description": "Canard stall speed at gross weight (first-principles, manual reference areas)",
            **spec_fields(specs, "stall_speed_ktas", computed_stall_ktas),
            "source": "reference_data.json:aircraft_specs.stall_speed_ktas",
            "notes": "Its CLmax input (canard CLmax 1.35, airfoil_data.roncz_r1145ms.cl_max) is unverified (not found in the CP text, cobelu, plans OCR, or the public web); the computed value is kept and the drift lock stays.",
            "units": "knots TAS",
            "convention_note": (
                f"Uses manual reference areas: "
                f"wing={wing_area_sqft} sqft + canard={canard_area_sqft} sqft = "
                f"{total_area_sqft} sqft. CLmax={cl_max} (canard stalls first)."
            ),
        }
    )

    # --- Max Gross Weight (exact match; no tolerance in reference_data) ---
    computed_mgw = config_module.flight_condition.gross_weight_lb  # type: ignore[attr-defined]
    metrics.append(
        {
            "metric_id": "max_gross_weight_lb",
            "description": "Maximum gross weight (hard limit)",
            **spec_fields(specs, "max_gross_weight_lb", computed_mgw, tolerance_abs=0.0),
            "source": "reference_data.json:aircraft_specs.max_gross_weight_lb",
            "units": "pounds",
        }
    )

    # --- Empty Weight ---
    sw = config_module.structural_weights  # type: ignore[attr-defined]
    # Sum all structural component weights from config
    computed_empty_weight = (
        sw.wing_weight_lb
        + sw.canard_weight_lb
        + sw.fuselage_weight_lb
        + sw.landing_gear_weight_lb
        + sw.electrical_weight_lb
        + sw.instruments_weight_lb
        + sw.interior_weight_lb
        # Engine/propulsion: O-235 standard weights
        + 250.0  # Engine (O-235)
        + 25.0   # Prop & Spinner
        + 30.0   # Engine Accessories
    )
    metrics.append(
        {
            "metric_id": "empty_weight_lb",
            "description": "Estimated empty weight (structural + propulsion components)",
            **spec_fields(specs, "empty_weight_lb", computed_empty_weight),
            "source": "reference_data.json:aircraft_specs.empty_weight_lb",
            "units": "pounds",
            "convention_note": (
                "Config structural weights are a partial model (wing, canard, fuselage, "
                "landing gear, electrical, instruments, interior + propulsion estimates). "
                "Missing: avionics, fairings, paint, wiring harness, miscellaneous hardware."
            ),
        }
    )

    # -------------------------------------------------------------------------
    # Airfoil metrics (from config.aero_limits, against wind tunnel reference)
    # -------------------------------------------------------------------------

    def _airfoil(mid, desc, af, key, computed, tol, src, units):
        metrics.append(
            {
                "metric_id": mid,
                "description": desc,
                **spec_fields(airfoils[af], key, computed, tolerance_abs=tol),
                "source": f"reference_data.json:airfoil_data.{af}.{key}",
                "units": units,
            }
        )

    al = config_module.aero_limits  # type: ignore[attr-defined]
    _airfoil("canard_clmax", "Canard (Roncz R1145MS) maximum lift coefficient",
             "roncz_r1145ms", "cl_max", al.canard_clmax, 0.05, None, "dimensionless")
    _airfoil("wing_clmax", "Main wing (Eppler 1230) maximum lift coefficient",
             "eppler_1230", "cl_max", al.wing_clmax, 0.05, None, "dimensionless")
    _airfoil("canard_alpha_0l_deg", "Canard (Roncz R1145MS) zero-lift angle of attack",
             "roncz_r1145ms", "alpha_zero_lift_deg", al.canard_alpha_0L, 0.5, None, "degrees")
    _airfoil("wing_alpha_0l_deg", "Main wing (Eppler 1230) zero-lift angle of attack",
             "eppler_1230", "alpha_zero_lift_deg", al.wing_alpha_0L, 0.5, None, "degrees")

    # -------------------------------------------------------------------------
    # Geometry metrics
    # -------------------------------------------------------------------------

    # --- Wing Area ---
    # Reference area: gross trapezoid, LE/TE extended to the centreline (BL 0 to tip, both sides).
    computed_wing_area_sqft = geo.wing_area_sqft
    metrics.append(
        {
            "metric_id": "wing_area_sqft",
            "description": "Main wing planform area",
            **spec_fields(specs, "wing_area_sqft", computed_wing_area_sqft),
            "source": "reference_data.json:aircraft_specs.wing_area_sqft",
            "units": "square feet",
            "convention_note": (
                "Reference is the manual's wing area, which excludes the canard "
                "(om-1980:p3; total 94.8 sq ft). Model area is the gross reference trapezoid: "
                "the straight panel taper (plans-1980:p126) extended to BL 0, both sides, tip to "
                f"tip. Exposed panels alone (wing_root_bl to tip): {geo.wing_exposed_area_sqft:.2f} sq ft."
            ),
        }
    )

    return metrics


def build_report(metrics: list[dict], vspaero_provenance: dict, checks: dict | None = None) -> dict:
    """
    Build the full accuracy report dict from graded metrics and provenance.

    Args:
        metrics: List of graded metric dicts from collect_metrics().
        vspaero_provenance: VSPAERO provenance dict from load_vspaero_provenance().

    Returns:
        Complete accuracy report dict ready for JSON serialization.
    """
    # Count grades
    grade_counts: dict[str, int] = {"pass": 0, "marginal": 0, "fail": 0, "ungraded": 0, "not graded": 0}
    for m in metrics:
        g = m["grade"].lower()
        if g in grade_counts:
            grade_counts[g] += 1

    return {
        "metadata": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "vspaero_provenance": vspaero_provenance,
            "checks": checks or {},
            "geometry_basis": "book (planform correction 2026-09-29); NP is a check, not a fit; see docs/geometry-correction-ledger.md",
            "traceability": (
                "All metric sources trace to reference_data.json (external published/measured) "
                "or vspaero_native. No sources from physics_baseline.json (self-referential). "
                "Verified by validate_sources() at generation time."
            ),
        },
        "summary": {
            "total": len(metrics),
            "pass": grade_counts["pass"],
            "marginal": grade_counts["marginal"],
            "fail": grade_counts["fail"],
            "ungraded": grade_counts["ungraded"],
            "not_graded": grade_counts["not graded"],
        },
        "metrics": metrics,
    }


def generate_accuracy_report(output_path: Path | None = None) -> Path:
    """
    Main entry point: generate accuracy_report.json.

    Loads reference data, runs the physics engine, grades all validated metrics,
    enforces source traceability, and writes the report.

    Args:
        output_path: Optional output path override. Defaults to
            <repo_root>/data/validation/accuracy_report.json.

    Returns:
        Path where the report was written.

    Raises:
        ValueError: If any metric source resolves to physics_baseline.json.
    """
    from config import config  # noqa: E402 — deferred import for CadQuery mock safety
    from core.analysis import PhysicsEngine  # noqa: E402

    data_dir = REPO_ROOT / "data" / "validation"
    data_dir.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output_path = data_dir / "accuracy_report.json"

    # Load reference data
    ref_data_path = data_dir / "reference_data.json"
    with open(ref_data_path, encoding="utf-8") as f:
        ref_data = json.load(f)

    # Load VSPAERO provenance
    vspaero_provenance = load_vspaero_provenance(data_dir)

    # Instantiate physics engine and collect metrics
    engine = PhysicsEngine()
    metrics = collect_metrics(ref_data, config, engine)

    # Build report structure
    checks = compute_checks(engine, config, data_dir)
    report = build_report(metrics, vspaero_provenance, checks)

    # Enforce traceability — raises ValueError on violations
    validate_sources(report, ref_data)

    # Write JSON output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return output_path


def main() -> None:
    """CLI entry point: generate accuracy report and print summary to stdout."""
    report_path = generate_accuracy_report()

    # Load and print summary
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    summary = report["summary"]
    print(f"\nAccuracy Report: {report_path}")
    print(f"Generated: {report['metadata']['generated']}")
    print(f"\nSummary ({summary['total']} metrics):")
    print(f"  PASS:     {summary['pass']}")
    print(f"  MARGINAL: {summary['marginal']}")
    print(f"  FAIL:     {summary['fail']}")
    print(f"  UNGRADED: {summary['ungraded']}")
    print(f"  NOT GRADED (unverified reference): {summary['not_graded']}")
    print()
    st = report["metadata"]["checks"]["stability"]
    print(f"CHECK stability at aft limit FS {st['aft_limit_fs']}: "
          f"{'PASS' if st['pass'] else 'FAIL'} (NP FS {st['np_fs']:.2f}, margin {st['static_margin_pct']:.2f}% MAC)")
    tm = report["metadata"]["checks"]["two_method_np"]
    if tm["status"] == "not run":
        print(f"CHECK two-method NP: NOT RUN ({tm['reason']})")
    else:
        print(f"CHECK two-method NP: {tm['status'].upper()} (analytic FS {tm['analytic']:.2f}, VLM FS {tm['vlm']:.2f}, "
              f"delta {tm['delta']:.3f} in, bound {tm['bound_in']} in)")
    print()

    # Print metric table
    print(f"{'Metric ID':<35} {'Grade':<10} {'Computed':>12} {'Reference':>12} {'Error Abs':>12}")
    print("-" * 90)
    for m in report["metrics"]:
        print(
            f"{m['metric_id']:<35} "
            f"{m['grade']:<10} "
            f"{m['computed']:>12.4f} "
            f"{'-' if m['reference'] is None else format(m['reference'], '.4f'):>12} "
            f"{'-' if m['error_abs'] is None else format(m['error_abs'], '.4f'):>12}"
        )


if __name__ == "__main__":
    main()
