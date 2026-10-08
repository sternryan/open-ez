"""Report 45 wing screen on the book wing (Block 3 M3.3, plan T10; spec sections 4.3 to 4.5).

Contract for scripts/flutter_screen.py:
  missing_inputs(inputs: dict) -> list[str]
      sorted names of every entry under inputs["inputs"] carrying a flag, plus "<strip id>.<field>"
      for every strip GJ_lbin2 carrying a flag and every aileron strip whose chord_in is null or flagged.
  screen(inputs: dict, limit_const: float) -> dict
      if missing_inputs is non-empty: state "blocked", reasons ["inputs_unsourced"], F and every speed
      None. Otherwise: strips in order from the centreline, GJ lb-in2 -> lb-ft2 (/144), widths in -> ft
      (/12), chord in -> ft (/12); theta = twist_per_unit_torque(GJ, ds); F = wing_flexibility_factor
      over the aileron strips only; vd_max_mph = vd_max_cleared_mph(F, limit_const), state "computed".
      Speeds are {"value", "unit", "basis"} records: vd_max {unit "mph", basis "IAS"}, vd_max_kt
      {unit "kt", basis "IAS"} (value * 1609.344 / 1852), vd_max_eas {value None, unit "kt", basis
      "EAS", reason: the IAS-to-CAS position error is unsourced}.
      Always: missing_inputs, applicability {d1, d2, d3}, each "met" | "not met" | "unconfirmed"
      (d1 "unconfirmed" while EAS is unknown; d2 and d3 "unconfirmed", spec section 4.4).
  build_report() -> dict: screen() on data/validation/flutter_inputs_book.yaml with the wing limit
      numerator from data/criteria/report45.yaml, plus "inputs_sha256" of the inputs file bytes.
  main(argv) -> int writes canonical JSON (indent 2, sorted keys, trailing newline), default
      data/validation/flutter_screen.json.
"""

import copy
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data/validation/flutter_inputs_book.yaml"
REPORT = ROOT / "data/validation/flutter_screen.json"

fs = pytest.importorskip("scripts.flutter_screen")


def _hand_case() -> dict:
    """Ledger row 79 hand case in inches: uniform GJ 2e5 lb-ft2, five 2 ft strips, chord 3 ft,
    aileron on the outer two strips. F = 288 / 2e5 = 1.44e-3 exactly."""
    gj = 2.0e5 * 144.0
    strips = []
    for i in range(5):
        strips.append(
            {
                "id": f"s{i}",
                "bl_from": 24.0 * i,
                "bl_to": 24.0 * (i + 1),
                "aileron": i >= 3,
                "chord_in": {"value": 36.0, "cite": "faa-report-45:p4"}
                if i >= 3
                else None,
                "GJ_lbin2": {"value": gj, "cite": "faa-report-45:p4"},
            }
        )
    return {
        "inputs": {"g": {"value": 1.0, "cite": "faa-report-45:p4"}},
        "strips": strips,
    }


def test_hand_case_reproduces_cumulative_twist_F():
    r = fs.screen(_hand_case(), 200.0)
    assert r["state"] == "computed" and r["missing_inputs"] == []
    assert r["F"] == pytest.approx(1.44e-3, rel=1e-12)
    assert r["vd_max"] == {
        "value": pytest.approx((200.0 / 1.44e-3) ** 0.5, rel=1e-12),
        "unit": "mph",
        "basis": "IAS",
    }
    assert r["vd_max_kt"]["value"] == pytest.approx(
        r["vd_max"]["value"] * 1609.344 / 1852.0, rel=1e-12
    )
    assert r["vd_max_kt"]["basis"] == "IAS"
    assert r["vd_max_eas"]["value"] is None and r["vd_max_eas"]["reason"]


def test_quartered_gj_quadruples_F():
    case = _hand_case()
    for s in case["strips"]:
        s["GJ_lbin2"]["value"] /= 4.0
    assert fs.screen(case, 200.0)["F"] == pytest.approx(4 * 1.44e-3, rel=1e-12)


def test_one_flagged_input_blocks_and_hides_every_speed():
    case = _hand_case()
    case["inputs"]["g"] = {"value": None, "flag": "unsourced"}
    r = fs.screen(case, 200.0)
    assert r["state"] == "blocked" and r["reasons"] == ["inputs_unsourced"]
    assert r["missing_inputs"] == ["g"]
    assert r["F"] is None
    assert r["vd_max"] is None and r["vd_max_kt"] is None


def test_flagged_strip_gj_and_missing_aileron_chord_are_listed():
    case = copy.deepcopy(_hand_case())
    case["strips"][0]["GJ_lbin2"] = {"value": None, "flag": "unsourced"}
    case["strips"][4]["chord_in"] = None
    case["strips"][1]["chord_in"] = None  # not an aileron strip: no chord needed
    assert fs.missing_inputs(case) == ["s0.GJ_lbin2", "s4.chord_in"]
    assert fs.screen(case, 200.0)["state"] == "blocked"


def test_applicability_flags_always_present():
    for case in (_hand_case(), yaml.safe_load(INPUTS.read_text())):
        app = fs.screen(case, 200.0)["applicability"]
        assert set(app) == {"d1", "d2", "d3"}
        assert set(app.values()) <= {"met", "not met", "unconfirmed"}
        assert app["d2"] == "unconfirmed" and app["d3"] == "unconfirmed"


def test_book_wing_is_blocked_on_exactly_its_flagged_inputs():
    d = yaml.safe_load(INPUTS.read_text())
    r = fs.screen(d, 200.0)
    assert r["state"] == "blocked"
    flagged = sorted(k for k, v in d["inputs"].items() if v.get("flag"))
    flagged += [f"{s['id']}.GJ_lbin2" for s in d["strips"] if s["GJ_lbin2"].get("flag")]
    assert r["missing_inputs"] == sorted(flagged)
    assert "bid_7725_wet.G12" in r["missing_inputs"]
    assert "und_7715_wet.G12" in r["missing_inputs"]


def test_report_regenerates_byte_for_byte(tmp_path):
    out = tmp_path / "f.json"
    assert fs.main([str(out)]) == 0
    assert out.read_text() == REPORT.read_text()
    r = json.loads(REPORT.read_text())
    assert r["state"] == "blocked" and r["vd_max"] is None
    assert len(r["inputs_sha256"]) == 64
