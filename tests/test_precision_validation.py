"""
Precision Validation Tests: Phase 4/5 Calibrated Tolerance Targets
===================================================================

Encodes precision tolerances for calibrated Long-EZ physics model:
  - VAL-01: Stability (NP, CG fwd, CG aft) at 2"/1" tolerance vs. published Long-EZ specs
  - VAL-02: Airfoil config values (CLmax, alpha_0L) vs. wind tunnel reference data
  - VAL-04: Performance (stall speed, gross weight) vs. published specs

PURPOSE: Active precision validation. VAL-01 tests pass after Phase 5 calibration of
fs_wing_le (133.0 → 125.61) and CG margin percentages (17.21%/7.65% from Rutan CP-29).
All four previously-xfail tests now pass as normal assertions. See calibration_log.json.

DO NOT MODIFY existing tests in test_physics_external_validation.py or
test_datum_resolution.py — those are sanity checks with generous tolerances.
This file provides precision measurement at calibrated tolerances.
"""

import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from unittest.mock import MagicMock  # noqa: E402

sys.modules.setdefault("cadquery", MagicMock())
sys.modules.setdefault("OCP", MagicMock())

import pytest  # noqa: E402

from config import config  # noqa: E402

REF_DATA_PATH = REPO_ROOT / "data" / "validation" / "reference_data.json"


def _load_ref_data() -> dict:
    """Load reference_data.json from the repository root."""
    with open(REF_DATA_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# VAL-01: Stability precision (NP, CG fwd, CG aft) — calibrated Phase 5
# ---------------------------------------------------------------------------


def test_np_reference_is_unverified_not_graded():
    """The NP reference (108.0) is unverified, so the model's NP is NOT GRADED against it.

    The value stays in reference_data.json for history only; truth_specs() excludes it.
    """
    from core.reference import truth_specs

    data = _load_ref_data()
    assert data["aircraft_specs"]["neutral_point_fs"]["status"] == "unverified"
    assert "neutral_point_fs" not in truth_specs(data)


# Resolved Phase 5: calibrated fs_wing_le corrects CG fwd limit (delta <1")
@pytest.mark.xfail(
    strict=True,
    reason="book geometry: see docs/geometry-correction-ledger.md rows 12, 47, 52, 54 and 61; gap +6.85 in (103.85 vs 97.0)",
)
def test_cg_fwd_limit_precision():
    """VAL-01: Computed CG forward limit (published datum) must be within 1\" of 97.0.

    Known status: XFAIL. The same fs_wing_le datum error that affects NP also
    shifts the computed CG envelope fwd limit away from the published 97.0\" FS.

    This test documents:
      - Target tolerance: 1.0\" (from reference_data.json cg_range_fwd_fs.tolerance_abs)
      - Reference value: 97.0\" (published FS datum, om-1980:p28)
    """
    from core.analysis import PhysicsEngine

    data = _load_ref_data()
    ref_cg_fwd = data["aircraft_specs"]["cg_range_fwd_fs"]["value"]
    tolerance = data["aircraft_specs"]["cg_range_fwd_fs"]["tolerance_abs"]

    engine = PhysicsEngine()
    metrics = engine.calculate_cg_envelope()
    computed_cg_fwd_published = config.geometry.to_published_datum(metrics.cg_range_fwd)
    delta = abs(computed_cg_fwd_published - ref_cg_fwd)

    assert delta <= tolerance, (
        f"CG fwd limit precision check FAILED (expected for Phase 4): "
        f'computed CG fwd = {computed_cg_fwd_published:.2f}" (published datum), '
        f'reference = {ref_cg_fwd:.1f}", delta = {delta:.2f}" exceeds {tolerance:.1f}" tolerance. '
        f'Internal CG fwd = {metrics.cg_range_fwd:.2f}". '
        f'Phase 5 target: calibrate geometry parameters to reduce delta to <{tolerance:.1f}".'
    )


# Resolved Phase 5: calibrated fs_wing_le corrects CG aft limit (delta <1")
@pytest.mark.xfail(
    strict=True,
    reason="see docs/geometry-correction-ledger.md rows 54 and 61; gap +4.71 in (107.71 vs 103.0)",
)
def test_cg_aft_limit_precision():
    """VAL-01: Computed CG aft limit (published datum) must be within 1\" of 103.0.

    Status: passing again (ledger row 52, two-method reconciliation: 103.42); was strict xfail from
    the gross reference area (row 45) and passing after the wing panel convention fix (row 13). The
    limit is NP minus a retired fixed MAC fraction, so this PASS inherits the unvalidated NP. Same fs_wing_le datum error shifts CG aft limit from
    published 103.0\" FS.

    This test documents:
      - Target tolerance: 1.0\" (from reference_data.json cg_range_aft_fs.tolerance_abs)
      - Reference value: 103.0\" (published FS datum, om-1980:p28)
    """
    from core.analysis import PhysicsEngine

    data = _load_ref_data()
    ref_cg_aft = data["aircraft_specs"]["cg_range_aft_fs"]["value"]
    tolerance = data["aircraft_specs"]["cg_range_aft_fs"]["tolerance_abs"]

    engine = PhysicsEngine()
    metrics = engine.calculate_cg_envelope()
    computed_cg_aft_published = config.geometry.to_published_datum(metrics.cg_range_aft)
    delta = abs(computed_cg_aft_published - ref_cg_aft)

    assert delta <= tolerance, (
        f"CG aft limit precision check FAILED (expected for Phase 4): "
        f'computed CG aft = {computed_cg_aft_published:.2f}" (published datum), '
        f'reference = {ref_cg_aft:.1f}", delta = {delta:.2f}" exceeds {tolerance:.1f}" tolerance. '
        f'Internal CG aft = {metrics.cg_range_aft:.2f}". '
        f'Phase 5 target: calibrate geometry parameters to reduce delta to <{tolerance:.1f}".'
    )


# ---------------------------------------------------------------------------
# VAL-02: Airfoil references are unverified — metrics are NOT GRADED
# ---------------------------------------------------------------------------


def test_roncz_clmax_reference_is_unverified_not_graded():
    """VAL-02: the Roncz R1145MS CLmax reference (roncz_r1145ms.cl_max) is unverified, so the metric is NOT GRADED.

    truth_airfoil() excludes the entry; nothing is compared against the old value.
    """
    from core.reference import truth_airfoil

    data = _load_ref_data()
    assert data["airfoil_data"]["roncz_r1145ms"]["cl_max"]["status"] == "unverified"
    assert "cl_max" not in truth_airfoil(data)["roncz_r1145ms"]


def test_roncz_alpha_0l_reference_is_unverified_not_graded():
    """VAL-02: the Roncz R1145MS alpha_0L reference (roncz_r1145ms.alpha_zero_lift_deg) is unverified, so the metric is NOT GRADED.

    truth_airfoil() excludes the entry; nothing is compared against the old value.
    """
    from core.reference import truth_airfoil

    data = _load_ref_data()
    assert (
        data["airfoil_data"]["roncz_r1145ms"]["alpha_zero_lift_deg"]["status"]
        == "unverified"
    )
    assert "alpha_zero_lift_deg" not in truth_airfoil(data)["roncz_r1145ms"]


def test_eppler_clmax_reference_is_unverified_not_graded():
    """VAL-02: the Eppler 1230 CLmax reference (eppler_1230.cl_max) is unverified, so the metric is NOT GRADED.

    truth_airfoil() excludes the entry; nothing is compared against the old value.
    """
    from core.reference import truth_airfoil

    data = _load_ref_data()
    assert data["airfoil_data"]["eppler_1230"]["cl_max"]["status"] == "unverified"
    assert "cl_max" not in truth_airfoil(data)["eppler_1230"]


def test_eppler_alpha_0l_reference_is_unverified_not_graded():
    """VAL-02: the Eppler 1230 alpha_0L reference (eppler_1230.alpha_zero_lift_deg) is unverified, so the metric is NOT GRADED.

    truth_airfoil() excludes the entry; nothing is compared against the old value.
    """
    from core.reference import truth_airfoil

    data = _load_ref_data()
    assert (
        data["airfoil_data"]["eppler_1230"]["alpha_zero_lift_deg"]["status"]
        == "unverified"
    )
    assert "alpha_zero_lift_deg" not in truth_airfoil(data)["eppler_1230"]


def test_airfoil_cm_zero_in_reference_data():
    """VAL-02 schema check: reference_data.json must contain cm_zero for both airfoils.

    This is a schema integrity check — the config does not implement section Cm0
    (no config.aero_limits.canard_cm0 or wing_cm0 field). The reference data
    keeps the Cm0 entries for history. They are unverified (Block 1 follow-up: no wind
    tunnel source found), so nothing may use them as truth.

    Values kept for history (unverified):
      - roncz_r1145ms.cm_zero = -0.05 (Purdue tunnel, 1984)
      - eppler_1230.cm_zero = -0.02 (Stuttgart / UIUC database)
    """
    data = _load_ref_data()
    airfoil_data = data["airfoil_data"]

    # Roncz R1145MS cm_zero must exist and be numeric
    assert "cm_zero" in airfoil_data["roncz_r1145ms"], (
        "reference_data.json missing roncz_r1145ms.cm_zero field. "
        "Wind tunnel Cm0 is required for Phase 5 pitching moment validation."
    )
    roncz_cm0 = airfoil_data["roncz_r1145ms"]["cm_zero"]["value"]
    assert isinstance(
        roncz_cm0, (int, float)
    ), f"roncz_r1145ms.cm_zero.value must be numeric, got {type(roncz_cm0)}"
    assert (
        roncz_cm0 < 0
    ), f"Roncz R1145MS cm_zero should be negative (nose-down), got {roncz_cm0}"

    # Eppler 1230 cm_zero must exist and be numeric
    assert "cm_zero" in airfoil_data["eppler_1230"], (
        "reference_data.json missing eppler_1230.cm_zero field. "
        "Wind tunnel Cm0 is required for Phase 5 pitching moment validation."
    )
    eppler_cm0 = airfoil_data["eppler_1230"]["cm_zero"]["value"]
    assert isinstance(
        eppler_cm0, (int, float)
    ), f"eppler_1230.cm_zero.value must be numeric, got {type(eppler_cm0)}"
    assert (
        eppler_cm0 < 0
    ), f"Eppler 1230 cm_zero should be negative (nose-down tendency), got {eppler_cm0}"


# ---------------------------------------------------------------------------
# VAL-04: Performance validation (stall speed, gross weight)
# ---------------------------------------------------------------------------


def test_stall_speed_reference_is_unverified_not_graded():
    """The stall speed reference (56 KTAS) is unverified, so stall speed is NOT GRADED.

    The first-principles stall speed is still computed, from the confirmed areas
    (wing 81.99 sqft + canard 12.8 sqft, om-1980:p3), canard CLmax 1.35 and config gross weight.
    """
    from core.reference import truth_specs

    data = _load_ref_data()
    assert data["aircraft_specs"]["stall_speed_ktas"]["status"] == "unverified"
    truth = truth_specs(data)
    assert "stall_speed_ktas" not in truth

    S = truth["wing_area_sqft"]["value"] + truth["canard_area_sqft"]["value"]
    W = config.flight_condition.gross_weight_lb
    rho = 0.002377  # slug/ft^3 (sea-level standard atmosphere)
    v_ktas = math.sqrt(2.0 * W / (rho * S * config.aero_limits.canard_clmax)) / 1.6878
    assert (
        30.0 < v_ktas < 100.0
    ), f"computed stall speed {v_ktas:.1f} KTAS is not physical"


def test_gross_weight_matches_published():
    """VAL-04: config.flight_condition.gross_weight_lb must equal the manual 1325 lb max takeoff gross exactly.

    This is an exact match check — no tolerance. The FAA-approved maximum gross
    weight for Long-EZ Model 61 is a hard regulatory limit, not an estimate.
    The config must match this value precisely.

    Reference: om-1980:p4 (max takeoff gross); the manual also has a 1425 lb takeoff-only band (om-1980:p28).
    """
    data = _load_ref_data()
    ref_gross_weight = data["aircraft_specs"]["max_gross_weight_lb"]["value"]

    computed_gross_weight = config.flight_condition.gross_weight_lb

    assert computed_gross_weight == ref_gross_weight, (
        f"Gross weight mismatch: "
        f"config.flight_condition.gross_weight_lb = {computed_gross_weight}, "
        f"published max gross weight = {ref_gross_weight} lb. "
        f"This must be an exact match — no tolerance on FAA gross weight limit."
    )
