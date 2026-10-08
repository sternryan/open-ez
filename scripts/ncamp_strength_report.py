import json
import sys
from pathlib import Path

import numpy as np
import yaml

from core.kernels.lamina import Ply
from core.kernels.laminate import ply_stresses
from core.kernels.tsai_wu import tsai_wu_strength_ratio
from core.materials import get_material

ROOT = Path(__file__).resolve().parents[1]


def laminate_plies(stack: list[float], symmetric: bool, lamina: dict, t_ply: float) -> list[Ply]:
    """Create a list of Ply objects for a given stack."""
    angles = stack + stack[::-1] if symmetric else stack
    return [
        Ply(
            E1=lamina["E1"],
            E2=lamina["E2"],
            G12=lamina["G12"],
            nu12=lamina["nu12"],
            t=t_ply,
            theta_deg=a,
        )
        for a in angles
    ]


def case_result(
    plies: list[Ply], strengths: dict, mode: str, f12s: tuple[float, ...] = (-0.5, 0.0)
) -> dict:
    """Calculate FPF and fibre failure strength ratios for a given mode."""
    if mode == "UNT":
        N = np.array([1.0, 0.0, 0.0])
    elif mode == "UNC":
        N = np.array([-1.0, 0.0, 0.0])
    else:
        raise ValueError(f"Unknown mode: {mode}")

    M = np.zeros(3)
    h = sum(p.t for p in plies)
    stresses = ply_stresses(plies, N, M)
    faces = []
    for top, bottom in stresses:
        faces.append(top)
        faces.append(bottom)

    F1t = strengths["F1t"]
    F1c = strengths["F1c"]
    F2t = strengths["F2t"]
    F2c = strengths["F2c"]
    F6 = strengths["F6"]

    fpf_psi = {}
    for f in f12s:
        min_ratio = min(
            tsai_wu_strength_ratio(s, F1t, F1c, F2t, F2c, F6, f) for s in faces
        )
        fpf_psi[str(f)] = min_ratio / h

    fibre_ratios = []
    for s in faces:
        s1 = s[0]
        if s1 > 0:
            fibre_ratios.append(F1t / s1)
        elif s1 < 0:
            fibre_ratios.append(F1c / (-s1))

    fibre_failure_psi = min(fibre_ratios) / h if fibre_ratios else float("inf")

    return {"fpf_psi": fpf_psi, "fibre_failure_psi": fibre_failure_psi}


def build_report() -> dict:
    """Build the NCAMP strength report dictionary."""
    v_path = ROOT / "tests/kernels/vectors/ncamp_laminates.yaml"
    m_path = ROOT / "data/validation/ncamp_strengths_measured.yaml"
    V = yaml.safe_load(v_path.read_text())
    meas = yaml.safe_load(m_path.read_text())

    # We only process 'as4_8552' as per task description
    mat_key = "as4_8552"
    v_data = V[mat_key]
    mat_props = get_material(mat_key)["properties"]
    S = {k: float(mat_props[k]["value"]) for k in ["F1t", "F1c", "F2t", "F2c", "F6"]}

    cases = []
    for lam_cfg in v_data["laminates"]:
        name = lam_cfg["name"]
        stack = lam_cfg["stack"]
        symmetric = lam_cfg["symmetric"]
        t_ply = v_data["t_ply"]

        for mode in ("UNT", "UNC"):
            lamina = v_data["tension"] if mode == "UNT" else v_data["compression"]
            plies = laminate_plies(stack, symmetric, lamina, t_ply)
            r = case_result(plies, S, mode)

            m_data = meas["laminates"][name][mode]
            mean = m_data["mean"]

            cases.append(
                {
                    "laminate": name,
                    "mode": mode,
                    "measured_psi": mean,
                    "cv_pct": m_data["cv_pct"],
                    "cite": m_data["cite"],
                    "fpf_psi": r["fpf_psi"],
                    "fibre_failure_psi": r["fibre_failure_psi"],
                    "measured_over_fpf": {k: mean / v for k, v in r["fpf_psi"].items()},
                    "measured_over_fibre": mean / r["fibre_failure_psi"],
                }
            )

    return {
        "gate": "none: reported beside first-ply and fibre failure, not gated (spec section 5)",
        "material": mat_key,
        "condition": "RTD as measured",
        "f12_star": [-0.5, 0.0],
        "f12_note": "f12* = -0.5 and 0 bracket the unsourced interaction term",
        "fibre_note": "linear CLT to the first fibre-direction strength, matrix damage ignored",
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the report script."""
    if argv:
        out_path = Path(argv[0])
    else:
        out_path = ROOT / "data/validation/ncamp_strengths.json"

    report = build_report()
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
