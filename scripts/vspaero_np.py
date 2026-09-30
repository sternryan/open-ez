"""
VSPAERO neutral point: the second method for the two-method NP check.

Builds the wing panels and the canard from the CURRENT config geometry, runs a
VSPAERO vortex-lattice alpha sweep, and computes

    NP = X_ref - (dCMy/dCL) * c_ref

from a least-squares fit of CMy against CL. X_ref is the moment reference
(Xcg) handed to the solver; Sref and cref only scale the coefficients, so the
NP does not depend on them as long as the solver uses the same values for CL
and CMy (it does: RefFlag = manual, values recorded in the output).

Writes data/validation/vspaero_np.json, which generate_accuracy_report reads.
The report treats the run as current only if its ``geometry`` block matches
``geometry_marker(config.geometry)``.

Run with the interpreter that has the OpenVSP bindings (the project venv
does not):
    python3.13 scripts/vspaero_np.py

The config module is standard-library only, so it imports under that
interpreter directly; nothing else from the project is imported here.
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_PATH = REPO / "data" / "validation" / "vspaero_np.json"

ALPHA_START, ALPHA_END, ALPHA_NPTS = -2.0, 6.0, 9
X_REF_FS = 103.0  # moment reference: the manual's aft CG limit (om-1980:p28)

# Geometry the VLM run depends on. The report compares every key to the live config.
MARKER_FIELDS = {
    "wing_span_in": "wing_span",
    "canard_span_in": "canard_span",
    "wing_root_bl": "wing_root_bl",
    "wing_panel_span_in": "wing_panel_span",
    "wing_root_chord_in": "wing_root_chord",
    "wing_tip_chord_in": "wing_tip_chord",
    "wing_sweep_le_deg": "wing_sweep_le",
    "wing_washout_deg": "wing_washout",
    "wing_incidence_deg": "wing_incidence",
    "fs_wing_le": "fs_wing_le",
    "wing_le_wl": "wing_le_wl",
    "canard_chord_in": "canard_chord",
    "canard_sweep_le_deg": "canard_sweep_le",
    "canard_incidence_deg": "canard_incidence",
    "fs_canard_le": "fs_canard_le",
    "canard_le_wl": "canard_le_wl",
}


# The VLM wing's inboard end. 0.0 = the gross reference trapezoid from the centreline, the same
# planform the analytic NP uses (ledger C2). A run recorded without this key (the exposed panels
# from wing_root_bl) reads as stale.
VLM_WING_INBOARD_BL = 0.0


def geometry_marker(geo) -> dict[str, float]:
    """The geometry block a VLM run records and the report's currency check compares."""
    marker = {key: round(float(getattr(geo, attr)), 6) for key, attr in MARKER_FIELDS.items()}
    marker["wing_centerline_chord_in"] = round(float(geo.wing_centerline_chord), 6)
    marker["vlm_wing_inboard_bl"] = VLM_WING_INBOARD_BL
    return marker


def reference_values(geo) -> dict[str, float]:
    """Solver reference quantities: the gross reference trapezoid (inches)."""
    c0, ct = geo.wing_centerline_chord, geo.wing_tip_chord
    lam = ct / c0
    return {
        "Sref_sqin": geo.wing_area_sqft * 144.0,
        "bref_in": geo.wing_span,
        "cref_in": (2.0 / 3.0) * c0 * (1 + lam + lam**2) / (1 + lam),
        "Xref_fs": X_REF_FS,
    }


def neutral_point(cl: list[float], cm: list[float], x_ref: float, c_ref: float) -> tuple[float, float, float]:
    """Least-squares dCM/dCL and NP = x_ref - slope * c_ref. Returns (np, slope, r_squared)."""
    n = len(cl)
    mx, my = sum(cl) / n, sum(cm) / n
    sxx = sum((x - mx) ** 2 for x in cl)
    sxy = sum((x - mx) * (y - my) for x, y in zip(cl, cm))
    slope = sxy / sxx
    ss_res = sum((y - (my + slope * (x - mx))) ** 2 for x, y in zip(cl, cm))
    ss_tot = sum((y - my) ** 2 for y in cm)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return x_ref - slope * c_ref, slope, r2


def _parse_polar(path: Path) -> list[dict[str, float]]:
    """AoA, CLtot, CDtot, CMytot from a VSPAERO .polar file (3 header lines)."""
    lines = path.read_text().splitlines()
    cols = lines[2].split()
    idx = {k: cols.index(k) for k in ("AoA", "CLtot", "CDtot", "CMytot")}
    rows = []
    for ln in lines[3:]:
        vals = ln.split()
        if len(vals) > max(idx.values()):
            rows.append({"alpha_deg": float(vals[idx["AoA"]]), "CL": float(vals[idx["CLtot"]]),
                         "CD": float(vals[idx["CDtot"]]), "CMy": float(vals[idx["CMytot"]])})
    return rows


def run(geo, work_dir: Path, *, x_ref: float = X_REF_FS, fixed_wake: bool = False,
        wing_to_centerline: bool = VLM_WING_INBOARD_BL == 0.0, with_canard: bool = True) -> dict:
    """One sweep. The keyword options are diagnostics only; the recorded run uses the defaults.

    Default wing: the gross reference trapezoid from BL 0 (centreline chord, LE on the LE sweep
    line), the planform of wing_area_sqft and of the analytic NP (ledger C2).
    """
    import openvsp as vsp

    ref = {**reference_values(geo), "Xref_fs": x_ref}
    wing_root_bl = 0.0 if wing_to_centerline else geo.wing_root_bl
    wing_root_chord = geo.wing_centerline_chord if wing_to_centerline else geo.wing_root_chord
    vsp.ClearVSPModel()
    no_sym = 0.0  # half-span geoms; VSPAERO Symmetry=1 mirrors them (see core/vsp_integration.py)

    wing = vsp.AddGeom("WING", "")
    vsp.SetGeomName(wing, "MainWing")
    vsp.SetParmVal(wing, "Span", "XSec_1", geo.wing_tip_bl - wing_root_bl)
    vsp.SetParmVal(wing, "Root_Chord", "XSec_1", wing_root_chord)
    vsp.SetParmVal(wing, "Tip_Chord", "XSec_1", geo.wing_tip_chord)
    vsp.SetParmVal(wing, "Sweep", "XSec_1", geo.wing_sweep_le)
    vsp.SetParmVal(wing, "Sweep_Location", "XSec_1", 0.0)  # sweep is the LE sweep
    vsp.SetParmVal(wing, "Dihedral", "XSec_1", geo.wing_dihedral)
    vsp.SetParmVal(wing, "Twist", "XSec_1", -geo.wing_washout)
    wing_le = geo.fs_wing_le - (geo.wing_root_bl - wing_root_bl) * math.tan(math.radians(geo.wing_sweep_le))
    vsp.SetParmVal(wing, "X_Rel_Location", "XForm", wing_le)
    vsp.SetParmVal(wing, "Y_Rel_Location", "XForm", wing_root_bl)
    vsp.SetParmVal(wing, "Z_Rel_Location", "XForm", geo.wing_le_wl)
    vsp.SetParmVal(wing, "Y_Rel_Rotation", "XForm", geo.wing_incidence)
    vsp.SetParmVal(wing, "Sym_Planar_Flag", "Sym", no_sym)

    canard = vsp.AddGeom("WING", "") if with_canard else None
    if canard is not None:
        _canard(vsp, geo, canard, no_sym)
    vsp.Update()

    thin = vsp.SET_FIRST_USER
    vsp.SetSetName(thin, "ThinSurfaces")
    for gid in (wing, canard):
        if gid is not None:
            vsp.SetSetFlag(gid, thin, True)
    vsp.Update()
    return _solve(vsp, work_dir, thin, ref, fixed_wake, wing_to_centerline)


def _canard(vsp, geo, canard, no_sym) -> None:
    vsp.SetGeomName(canard, "Canard")
    vsp.SetParmVal(canard, "Span", "XSec_1", geo.canard_span / 2)
    vsp.SetParmVal(canard, "Root_Chord", "XSec_1", geo.canard_root_chord)
    vsp.SetParmVal(canard, "Tip_Chord", "XSec_1", geo.canard_tip_chord)
    vsp.SetParmVal(canard, "Sweep", "XSec_1", geo.canard_sweep_le)
    vsp.SetParmVal(canard, "Sweep_Location", "XSec_1", 0.0)
    vsp.SetParmVal(canard, "X_Rel_Location", "XForm", geo.fs_canard_le)
    vsp.SetParmVal(canard, "Z_Rel_Location", "XForm", geo.canard_le_wl)
    vsp.SetParmVal(canard, "Y_Rel_Rotation", "XForm", geo.canard_incidence)
    vsp.SetParmVal(canard, "Sym_Planar_Flag", "Sym", no_sym)


def _solve(vsp, work_dir: Path, thin: int, ref: dict, fixed_wake: bool,
           wing_to_centerline: bool) -> dict:
    vsp3 = str(work_dir / "long_ez_np.vsp3")
    vsp.SetVSP3FileName(vsp3)
    vsp.WriteVSPFile(vsp3)
    vsp.ExportFile(vsp3.replace(".vsp3", ".vspgeom"), vsp.SET_NONE, vsp.EXPORT_VSPGEOM, False, thin)

    a = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(a)
    vsp.SetIntAnalysisInput(a, "GeomSet", [vsp.SET_NONE])
    vsp.SetIntAnalysisInput(a, "ThinGeomSet", [thin])
    vsp.SetDoubleAnalysisInput(a, "AlphaStart", [ALPHA_START])
    vsp.SetDoubleAnalysisInput(a, "AlphaEnd", [ALPHA_END])
    vsp.SetIntAnalysisInput(a, "AlphaNpts", [ALPHA_NPTS])
    vsp.SetDoubleAnalysisInput(a, "MachStart", [0.0])
    vsp.SetIntAnalysisInput(a, "MachNpts", [1])
    vsp.SetIntAnalysisInput(a, "Symmetry", [1])
    vsp.SetIntAnalysisInput(a, "RefFlag", [0])  # manual reference values below
    vsp.SetDoubleAnalysisInput(a, "Sref", [ref["Sref_sqin"]])
    vsp.SetDoubleAnalysisInput(a, "bref", [ref["bref_in"]])
    vsp.SetDoubleAnalysisInput(a, "cref", [ref["cref_in"]])
    vsp.SetIntAnalysisInput(a, "UseCGModeFlag", [0])
    vsp.SetDoubleAnalysisInput(a, "Xcg", [ref["Xref_fs"]])
    vsp.SetDoubleAnalysisInput(a, "Ycg", [0.0])
    vsp.SetDoubleAnalysisInput(a, "Zcg", [0.0])
    vsp.SetIntAnalysisInput(a, "FixedWakeFlag", [1 if fixed_wake else 0])
    vsp.ExecAnalysis(a)

    rows = _parse_polar(Path(vsp3.replace(".vsp3", ".polar")))
    if len(rows) < 3:
        raise RuntimeError(f"VSPAERO returned {len(rows)} polar rows; expected {ALPHA_NPTS}")
    np_fs, slope, r2 = neutral_point([r["CL"] for r in rows], [r["CMy"] for r in rows],
                                     ref["Xref_fs"], ref["cref_in"])
    return {
        "method": ("VSPAERO vortex lattice (VLM), gross reference wing (BL 0 to tip) + canard, "
                   "thin surfaces, Mach 0, Y-symmetry"),
        "np_fs": round(np_fs, 4),
        "dCMy_dCL": slope,
        "fit_r_squared": r2,
        "formula": "NP = Xref - (dCMy/dCL) * cref; least-squares slope over the sweep",
        "reference": {**ref, "RefFlag": "manual",
                      "note": ("Sref = gross reference trapezoid (wing_area_sqft x 144), bref = wing_span, "
                               "cref = MAC of the gross trapezoid; Xref = Xcg (moment reference). "
                               "NP is independent of Sref/cref: CL and CMy share them.")},
        "model": (("wing = gross reference trapezoid, BL 0 (wing_centerline_chord) to tip, LE and TE "
                   "the straight panel lines extended to the centreline" if wing_to_centerline else
                   "wing panels BL wing_root_bl to tip (diagnostic)")
                  + "; no strakes, no fuselage, no winglets; canard constant chord from BL 0; "
                  "incidences as rigid Y rotations about each surface's root LE"),
        "sweep": rows,
    }


def main() -> int:
    sys.path.insert(0, str(REPO))
    from config import config  # stdlib-only module

    try:
        import openvsp as vsp
    except ImportError:
        print("openvsp is not importable under this interpreter; run with python3.13", file=sys.stderr)
        return 1
    geo = config.geometry
    with tempfile.TemporaryDirectory() as tmp:
        result = run(geo, Path(tmp))
    out = {
        "source": "vspaero_vlm_np",
        "vsp_version": str(vsp.GetVSPVersion()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alpha_range_deg": [ALPHA_START, ALPHA_END, ALPHA_NPTS],
        "geometry": geometry_marker(geo),
        **result,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"VSPAERO NP = FS {out['np_fs']:.2f} (dCMy/dCL {out['dCMy_dCL']:.5f}, r^2 {out['fit_r_squared']:.6f})")
    for r in out["sweep"]:
        print(f"  alpha {r['alpha_deg']:6.2f}  CL {r['CL']:.5f}  CMy {r['CMy']:.5f}")
    print(f"wrote {OUT_PATH.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
