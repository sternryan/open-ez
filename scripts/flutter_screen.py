import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import yaml

from core.kernels.flutter_r45 import (
    twist_per_unit_torque,
    wing_flexibility_factor,
    vd_max_cleared_mph,
)

ROOT = Path(__file__).resolve().parents[1]


def missing_inputs(inputs: dict) -> list[str]:
    """Return sorted names of every entry under inputs["inputs"] carrying a flag, plus "<strip id>.<field>" for every strip GJ_lbin2 carrying a flag and every aileron strip whose chord_in is null or flagged."""
    names = [k for k, v in inputs["inputs"].items() if v.get("flag")]
    for s in inputs["strips"]:
        if s["GJ_lbin2"].get("flag"):
            names.append(f"{s['id']}.GJ_lbin2")
        if s["aileron"] and (s["chord_in"] is None or s["chord_in"].get("flag") or s["chord_in"].get("value") is None):
            names.append(f"{s['id']}.chord_in")
    return sorted(names)


def screen(inputs: dict, limit_const: float) -> dict:
    """Evaluate the Report 45 wing screen based on provided inputs and limit."""
    APPLICABILITY = {"d1": "unconfirmed", "d2": "unconfirmed", "d3": "unconfirmed"}
    miss = missing_inputs(inputs)
    if miss:
        return {
            "state": "blocked",
            "reasons": ["inputs_unsourced"],
            "missing_inputs": miss,
            "F": None,
            "vd_max": None,
            "vd_max_kt": None,
            "vd_max_eas": None,
            "applicability": dict(APPLICABILITY),
        }

    gj = np.array([s["GJ_lbin2"]["value"] for s in inputs["strips"]]) / 144.0
    ds = np.array([(s["bl_to"] - s["bl_from"]) for s in inputs["strips"]]) / 12.0
    theta = twist_per_unit_torque(gj, ds)

    mask = np.array([s["aileron"] for s in inputs["strips"]])
    chord = np.array([s["chord_in"]["value"] if s["chord_in"] else 0.0 for s in inputs["strips"]]) / 12.0

    F = wing_flexibility_factor(theta[mask], chord[mask], ds[mask])
    v = vd_max_cleared_mph(F, limit_const)

    return {
        "state": "computed",
        "reasons": [],
        "missing_inputs": [],
        "F": float(F),
        "vd_max": {"value": v, "unit": "mph", "basis": "IAS"},
        "vd_max_kt": {"value": v * 1609.344 / 1852.0, "unit": "kt", "basis": "IAS"},
        "vd_max_eas": {
            "value": None,
            "unit": "kt",
            "basis": "EAS",
            "reason": "IAS to CAS position error unsourced",
        },
        "applicability": dict(APPLICABILITY),
    }


def build_report() -> dict:
    """Build the full Report 45 wing screen report from the book inputs."""
    raw = (ROOT / "data/validation/flutter_inputs_book.yaml").read_bytes()
    d = yaml.safe_load(raw)
    limit = float(
        yaml.safe_load((ROOT / "data/criteria/report45.yaml").read_text())["wing"]["limit_numerator"]["value"]
    )
    r = screen(d, limit)
    r["inputs_sha256"] = hashlib.sha256(raw).hexdigest()
    r["limit_numerator"] = limit
    r["criterion"] = "faa-report-45:p4 wing, F <= 200 / Vd^2"
    return r


def main(argv: list[str] | None = None) -> int:
    """Main entry point to write the report to a JSON file."""
    out = Path(argv[0]) if argv else ROOT / "data/validation/flutter_screen.json"
    r = build_report()
    out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
