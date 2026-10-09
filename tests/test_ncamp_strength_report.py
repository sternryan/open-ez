"""NCAMP AS4/8552 measured laminate strengths beside first-ply failure and fibre failure (plan T5).

Reported, never gated (spec section 5): first-ply failure does not predict ultimate laminate strength.

Contract for scripts/ncamp_strength_report.py:
  laminate_plies(stack, symmetric, lamina, t_ply) -> list[Ply]
      stack mirrored when symmetric; lamina is {E1, E2, G12, nu12} in psi.
  case_result(plies, strengths, mode, f12s=(-0.5, 0.0)) -> dict
      unit in-plane load N = [+1, 0, 0] lb/in for "UNT", [-1, 0, 0] for "UNC", M = 0; h = sum of ply t.
      fpf_psi: {str(f): min Tsai-Wu ratio over every ply and face / h} for each f in f12s.
      fibre_failure_psi: min over every ply and face of F1t / s1 (s1 > 0) or F1c / -s1 (s1 < 0), / h.
      Any other mode raises ValueError.
  build_report() -> dict, main(argv) -> int writing canonical JSON (indent 2, sorted keys, newline).
"""

import json
import math
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/validation/ncamp_strengths.json"
MEASURED = ROOT / "data/validation/ncamp_strengths_measured.yaml"

nsr = pytest.importorskip("scripts.ncamp_strength_report")

LAM = {"E1": 19.09e6, "E2": 1.34e6, "G12": 0.70e6, "nu12": 0.302}
STR = {"F1t": 299220.0, "F1c": 215290.0, "F2t": 9270.0, "F2c": 38850.0, "F6": 8000.0}


def test_all_zero_laminate_fails_at_the_lamina_strength():
    plies = nsr.laminate_plies([0, 0], True, LAM, 0.0074)
    t = nsr.case_result(plies, STR, "UNT")
    c = nsr.case_result(plies, STR, "UNC")
    assert t["fibre_failure_psi"] == pytest.approx(STR["F1t"], rel=1e-9)
    assert c["fibre_failure_psi"] == pytest.approx(STR["F1c"], rel=1e-9)
    for f in ("-0.5", "0.0"):  # sigma2 = tau12 = 0, so f12 drops out
        assert t["fpf_psi"][f] == pytest.approx(STR["F1t"], rel=1e-9)
        assert c["fpf_psi"][f] == pytest.approx(STR["F1c"], rel=1e-9)


def test_all_ninety_laminate_first_ply_is_the_transverse_strength():
    plies = nsr.laminate_plies([90], True, LAM, 0.0074)
    assert nsr.case_result(plies, STR, "UNT")["fpf_psi"]["0.0"] == pytest.approx(
        STR["F2t"], rel=1e-9
    )
    assert nsr.case_result(plies, STR, "UNC")["fpf_psi"]["0.0"] == pytest.approx(
        STR["F2c"], rel=1e-9
    )


def test_symmetric_mirror_and_thickness():
    plies = nsr.laminate_plies([45, 0], True, LAM, 0.01)
    assert [p.theta_deg for p in plies] == [45, 0, 0, 45]
    assert all(p.t == 0.01 for p in plies)
    assert len(nsr.laminate_plies([45, 0], False, LAM, 0.01)) == 2


def test_unknown_mode_raises():
    plies = nsr.laminate_plies([0], True, LAM, 0.0074)
    with pytest.raises(ValueError):
        nsr.case_result(plies, STR, "OHT")


def _close(a, b):
    """Equal keys and non-float fields exactly; floats to rel 1e-9 (the last digit differs across platforms)."""
    if isinstance(a, dict):
        return (
            isinstance(b, dict)
            and a.keys() == b.keys()
            and all(_close(a[k], b[k]) for k in a)
        )
    if isinstance(a, list):
        return (
            isinstance(b, list)
            and len(a) == len(b)
            and all(_close(x, y) for x, y in zip(a, b))
        )
    if isinstance(a, float):
        return isinstance(b, float) and a == pytest.approx(b, rel=1e-9)
    return type(a) is type(b) and a == b


def test_report_regenerates_to_tolerance(tmp_path):
    out = tmp_path / "r.json"
    assert nsr.main([str(out)]) == 0
    assert _close(json.loads(out.read_text()), json.loads(REPORT.read_text()))


def test_report_carries_every_measured_case_and_no_gate():
    r = json.loads(REPORT.read_text())
    meas = yaml.safe_load(MEASURED.read_text())["laminates"]
    got = {(c["laminate"], c["mode"]): c for c in r["cases"]}
    assert set(got) == {(lam, m) for lam in meas for m in ("UNT", "UNC")}
    for (lam, mode), c in got.items():
        assert c["measured_psi"] == meas[lam][mode]["mean"]
        assert c["cite"] == meas[lam][mode]["cite"]
        assert set(c["fpf_psi"]) == {"-0.5", "0.0"}
        assert math.isfinite(c["fibre_failure_psi"]) and c["fibre_failure_psi"] > 0
    assert r["gate"].startswith("none")
    text = REPORT.read_text()
    assert '"pass"' not in text and '"fail"' not in text
