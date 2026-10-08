"""Block 3 M3.3: Report 45 wing screen on the book wing inputs.

A flagged input blocks the screen and is listed; V_D,max is computed only when every input is
sourced. Usage: python scripts/flutter_screen.py [out.json]
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.kernels.flutter_r45 import (
    twist_per_unit_torque,
    vd_max_cleared_mph,
    wing_flexibility_factor,
)


def missing_inputs(inputs: dict) -> list[str]:
    """Sorted names of every flagged or null input, strip GJ and aileron chord."""
    names = [
        k
        for k, v in inputs["inputs"].items()
        if v.get("flag") or v.get("value") is None
    ]
    for s in inputs["strips"]:
        if s["GJ_lbin2"].get("flag") or s["GJ_lbin2"].get("value") is None:
            names.append(f"{s['id']}.GJ_lbin2")
        if s["aileron"] and (
            s["chord_in"] is None
            or s["chord_in"].get("flag")
            or s["chord_in"].get("value") is None
        ):
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

    edges = [(s["bl_from"], s["bl_to"]) for s in inputs["strips"]]
    if (
        edges[0][0] != 0.0
        or any(a >= b for a, b in edges)
        or any(edges[i][1] != edges[i + 1][0] for i in range(len(edges) - 1))
    ):
        raise ValueError(
            "strips must run contiguously outward from the centreline (BL 0)"
        )
    gj = np.array([s["GJ_lbin2"]["value"] for s in inputs["strips"]]) / 144.0
    ds = np.array([(s["bl_to"] - s["bl_from"]) for s in inputs["strips"]]) / 12.0
    theta = twist_per_unit_torque(gj, ds)

    mask = np.array([s["aileron"] for s in inputs["strips"]])
    chord = (
        np.array(
            [s["chord_in"]["value"] if s["chord_in"] else 0.0 for s in inputs["strips"]]
        )
        / 12.0
    )

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
        yaml.safe_load((ROOT / "data/criteria/report45.yaml").read_text())["wing"][
            "limit_numerator"
        ]["value"]
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
