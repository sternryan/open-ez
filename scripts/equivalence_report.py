"""Block 3 M3.4: canard equivalence report (book glass canard against the carbon proposal).

Every number comes from deterministic code. Gates have four states: pass, fail, blocked, open.
Neither blocked nor open can ever read as pass: any flagged input or any reason blocks, and
requires_original_test alone reads open. The report is canonical JSON and regenerates byte for byte.

Usage: python scripts/equivalence_report.py [out.json]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.equivalence_inputs import (
    BOOK_MATERIALS,
    CARBON_MATERIALS,
    STIFFNESS_FLAG_FRACTION,
    inputs_sha256,
)
from core.materials import load_materials

OUT = ROOT / "data/validation/equivalence_canard.json"
BOOK_SCHEDULE = "data/laminates/canard_book.yaml"
CARBON_SCHEDULE = "data/laminates/canard_carbon.yaml"
LEDGER = "data/mass_ledger.yaml"

REASONS = {
    "inputs_unsourced",
    "glass_unvalidated",
    "criterion_unavailable",
    "not_applicable",
    "requires_original_test",
}
STATES = ("pass", "fail", "blocked", "open")
LOAD_CASES = ("+M", "-M", "+T", "-T")

# M3.1 glass status, plan T5; see the geometry-correction ledger
GLASS_VALIDATED = True

# Sizing-rule stations (docs/harness/block3-sizing-rule.md): the BL 0 centre, just inboard and
# outboard of BL 10, 20 and 30, and BL 54 (end of the shear web and the cap troughs).
STATIONS = (
    {"bl": 0.0, "side": "centre"},
    {"bl": 10.0, "side": "inboard"},
    {"bl": 10.0, "side": "outboard"},
    {"bl": 20.0, "side": "inboard"},
    {"bl": 20.0, "side": "outboard"},
    {"bl": 30.0, "side": "inboard"},
    {"bl": 30.0, "side": "outboard"},
    {"bl": 54.0, "side": "end"},
)

# Report 45 elevator criteria need fuselage frequencies, which are not available.
# The citation that a mass centroid aft of the elastic axis is destabilising is not registered.
CG_CITE_INPUT = "basis.cg_aft_destabilising_cite"


# ---- gates ------------------------------------------------------------------------------------


def gate(passed, flagged=(), reasons=(), test_required=None) -> dict:
    """One gate result. `passed` is True, False or None (result not computable)."""
    reasons = set(reasons)
    unknown = reasons - REASONS
    if unknown:
        raise ValueError(f"unknown gate reasons: {sorted(unknown)}")
    if "requires_original_test" in reasons:
        raise ValueError(
            "requires_original_test must come from test_required, with its inputs and coupons"
        )
    flagged = sorted(set(flagged))
    test_required = dict(test_required or {})
    if flagged:
        reasons.add("inputs_unsourced")
    if test_required:
        reasons.add("requires_original_test")
    reasons_sorted = sorted(reasons)
    if reasons_sorted == ["requires_original_test"]:
        state = "open"
        label = "open: requires_original_test"
    elif reasons_sorted or passed is None:
        state = "blocked"
        label = "blocked: " + (
            ", ".join(reasons_sorted) if reasons_sorted else "result_unavailable"
        )
    elif passed:
        state, label = "pass", "pass"
    else:
        state, label = "fail", "fail"
    return {
        "state": state,
        "reasons": reasons_sorted,
        "flagged_inputs": flagged,
        "test_required_inputs": sorted(test_required),
        "closing_coupons": sorted(set(test_required.values())),
        "label": label,
    }


def strength_ratio_min(carbon: dict, book: dict) -> float:
    """Minimum carbon/book capacity over every (load case, f12) key."""
    for name, caps in (("carbon", carbon), ("book", book)):
        f12s = {f for (_, f) in caps}
        if len(f12s) < 2:
            raise ValueError(
                f"{name}: needs two or more f12 values, got {sorted(f12s)}"
            )
        for f in f12s:
            missing = [lc for lc in LOAD_CASES if (lc, f) not in caps]
            if missing:
                raise ValueError(f"{name}: f12={f} missing load cases {missing}")
    if set(carbon) != set(book):
        raise ValueError("carbon and book must hold the same (load case, f12) keys")
    for name, caps in (("carbon", carbon), ("book", book)):
        bad = [k for k, v in caps.items() if not (math.isfinite(v) and v > 0)]
        if bad:
            raise ValueError(
                f"{name}: capacities must be finite and positive, not at {bad}"
            )
    return min(carbon[k] / book[k] for k in carbon)


def strength_gate(carbon, book, flagged=(), reasons=(), test_required=None) -> dict:
    return gate(
        strength_ratio_min(carbon, book) >= 1.0, flagged, reasons, test_required
    )


def mass_placement_gate(offset_carbon, offset_book, flagged=(), reasons=()) -> dict:
    """Pass iff the carbon mass centroid is no further aft of the shear centre than the book's."""
    passed = None
    if offset_carbon is not None and offset_book is not None:
        passed = offset_carbon <= offset_book
    return gate(passed, flagged, reasons)


def f_consistency(F_carbon, F_book, flagged=(), reasons=()) -> dict:
    """Consistency check on flexibility F: smaller is stiffer; pass iff carbon <= book."""
    passed = None
    if F_carbon is not None and F_book is not None:
        passed = F_carbon <= F_book
    g = gate(passed, flagged, reasons)
    g["kind"] = "consistency_check"
    return g


def stiffness_deltas(book: dict, carbon: dict, threshold: float) -> dict:
    out = {}
    for name, b in book.items():
        delta = (carbon[name] - b) / b
        out[name] = {
            "book": b,
            "carbon": carbon[name],
            "delta_fraction": delta,
            "flag": delta > threshold,
        }
    return out


# ---- flagged-input collection -----------------------------------------------------------------


def flagged_inputs(schedule: dict, materials: dict, material_ids) -> list[str]:
    """`<material>.<property>` for each flagged property, `<ply id>.count` for each flagged ply and
    `<ply id>.extent` for each structural ply whose extent is unsourced or a conflict. Any flag but
    requires_original_test counts (conflict included); those are listed by test_required_inputs."""
    out = set()
    for mid in material_ids:
        for prop, p in materials[mid]["properties"].items():
            if p.get("flag") and p.get("flag") != "requires_original_test":
                out.add(f"{mid}.{prop}")
    for ply in schedule.get("plies", []):
        if ply.get("flag"):
            out.add(f"{ply['id']}.count")
        if ply.get("region") in SECTION_REGIONS and ply.get("extent_status") in (
            "unsourced",
            "conflict",
        ):
            out.add(f"{ply['id']}.extent")
    return sorted(out)


def test_required_inputs(materials: dict, material_ids) -> dict[str, str]:
    out = {}
    for mid in material_ids:
        for prop, p in materials[mid]["properties"].items():
            if p.get("flag") == "requires_original_test":
                out[f"{mid}.{prop}"] = p["closing_test"]["coupon"]
    return dict(sorted(out.items()))


def geometry_flagged_inputs(geometry: dict) -> list[str]:
    """`cell.<name>` for each cell geometry entry that is flagged (unsourced or conflict)."""
    return sorted(f"cell.{k}" for k, v in geometry.items() if v.get("flag"))


# ---- station capacities (kernel-based) --------------------------------------------------------

# Regions the idealised section reads; pads, elevator skins and other plies are not in it.
SECTION_REGIONS = (
    "skin_top",
    "skin_bottom",
    "spar_cap_top",
    "spar_cap_bottom",
    "shear_web",
)
# An angle pair on a woven fabric is one fabric ply per count, at the first (warp) angle; on a
# unidirectional material it is one ply at each angle in turn (schedule `frame` lines in
# data/laminates/canard_book.yaml and canard_carbon.yaml).
FABRIC_MATERIALS = frozenset(
    {"bid_7725_wet", "bgf7781_mgs418_wet", "carbon3k_mgs418_wet"}
)

_LAMINA = ("E1", "E2", "G12", "nu12", "t_ply", "F1t", "F1c", "F2t", "F2c", "F6")


def _expand(rows, bl: float) -> list[tuple[str, float]]:
    """Active ply rows at `bl`, in stack order (row order where none is given), one entry per ply."""
    plies = []
    order = sorted(
        enumerate(rows), key=lambda ir: (ir[1].get("stack_order", ir[0]), ir[0])
    )
    for _, row in order:
        lo, hi = row.get("bl_from"), row.get("bl_to")
        if lo is None or hi is None or not (lo <= bl <= hi):
            continue
        n = row["count"]
        if n is None:
            raise ValueError(f"ply row {row['id']}: count is null")
        angle = row["angle_deg"]
        if angle is None:
            raise ValueError(f"ply row {row['id']}: angle is null")
        for i in range(int(n)):
            if isinstance(angle, (list, tuple)):
                a = (
                    angle[0]
                    if row["material"] in FABRIC_MATERIALS
                    else angle[i % len(angle)]
                )
            else:
                a = angle
            plies.append((row["material"], float(a)))
    return plies


def station_capacities(schedule, materials, section, bl, f12_star) -> dict:
    """First-ply-failure capacity under a unit moment and a unit torque, both signs, at span
    station `bl`: the minimum Tsai-Wu strength ratio over walls, wall ends, plies and faces.

    Section model: idealised rectangular two-cell section, captain choice, unsourced.
    `section` = {width, height, web_x, cap_width} in inches, x chordwise from 0, z up, surfaces at
    z = +-height/2. Top and bottom surfaces each split at web_x +- cap_width/2 into front, cap and
    rear walls; the cap wall is carried as two halves meeting the web, so each cell closes on
    wall ends. A vertical web at web_x and closing walls at x = 0 and x = width.
    """
    import numpy as np

    from core.kernels.lamina import Ply
    from core.kernels.laminate import abd, ply_stresses
    from core.kernels.thinwall import Cell, Wall, multicell_torsion, section_ei
    from core.kernels.tsai_wu import tsai_wu_strength_ratio

    w, h = float(section["width"]), float(section["height"])
    wx, cw = float(section["web_x"]), float(section["cap_width"])
    if not (0.0 < wx - cw / 2.0 and wx + cw / 2.0 < w):
        raise ValueError(
            "cap must lie inside the section: 0 < web_x -/+ cap_width/2 < width"
        )

    by_region: dict[str, list] = {}
    for row in schedule["plies"]:
        by_region.setdefault(row["region"], []).append(row)

    def lamina(mid):
        props = materials[mid]["properties"]
        vals = {}
        for k in _LAMINA:
            v = props[k]["value"]
            if v is None:
                raise ValueError(f"{mid}.{k} is null: no capacity can be computed")
            vals[k] = float(v)
        return vals

    def laminate(regions):
        spec = []
        for region in regions:
            spec += _expand(by_region.get(region, []), bl)
        if not spec:
            raise ValueError(f"no active plies at BL {bl} for {regions}")
        plies, strengths = [], []
        for mid, ang in spec:
            v = lamina(mid)
            plies.append(Ply(v["E1"], v["E2"], v["G12"], v["nu12"], v["t_ply"], ang))
            strengths.append((v["F1t"], v["F1c"], v["F2t"], v["F2c"], v["F6"]))
        A, _, _ = abd(plies)
        a = np.linalg.inv(np.asarray(A, dtype=float))
        t = sum(p.t for p in plies)
        return {
            "plies": plies,
            "strengths": strengths,
            "Et": 1.0 / a[0, 0],
            "Gt": 1.0 / a[2, 2],
            "t": t,
        }

    skin_t, skin_b = ["skin_top"], ["skin_bottom"]
    lam = {
        "top": laminate(skin_t),
        "top_cap": laminate(["skin_top", "spar_cap_top"]),
        "bot": laminate(skin_b),
        "bot_cap": laminate(["skin_bottom", "spar_cap_bottom"]),
        "web": laminate(["shear_web"]),
        "close": laminate(skin_t),
    }
    zt, zb = h / 2.0, -h / 2.0
    x1, x2 = wx - cw / 2.0, wx + cw / 2.0
    # (name, x0, z0, x1, z1, laminate)
    geo = [
        ("top_front", 0.0, zt, x1, zt, "top"),
        ("top_cap_front", x1, zt, wx, zt, "top_cap"),
        ("top_cap_rear", wx, zt, x2, zt, "top_cap"),
        ("top_rear", x2, zt, w, zt, "top"),
        ("bot_front", 0.0, zb, x1, zb, "bot"),
        ("bot_cap_front", x1, zb, wx, zb, "bot_cap"),
        ("bot_cap_rear", wx, zb, x2, zb, "bot_cap"),
        ("bot_rear", x2, zb, w, zb, "bot"),
        ("web", wx, zb, wx, zt, "web"),
        ("close_front", 0.0, zb, 0.0, zt, "close"),
        ("close_rear", w, zb, w, zt, "close"),
    ]
    names = [g[0] for g in geo]
    walls = [
        Wall(
            g[1],
            g[2],
            g[3],
            g[4],
            lam[g[5]]["t"],
            lam[g[5]]["Gt"],
            lam[g[5]]["Et"],
            0.0,
        )
        for g in geo
    ]
    idx = names.index
    cells = [
        Cell(
            tuple(
                idx(n)
                for n in (
                    "top_front",
                    "top_cap_front",
                    "bot_front",
                    "bot_cap_front",
                    "close_front",
                    "web",
                )
            ),
            wx * h,
        ),
        Cell(
            tuple(
                idx(n)
                for n in (
                    "top_cap_rear",
                    "top_rear",
                    "bot_cap_rear",
                    "bot_rear",
                    "close_rear",
                    "web",
                )
            ),
            (w - wx) * h,
        ),
    ]

    def wall_ratio(lm, N, f12):
        stresses = ply_stresses(lm["plies"], np.asarray(N, float), np.zeros(3))
        best = math.inf
        for (top, bottom), st in zip(stresses, lm["strengths"]):
            for sigma in (top, bottom):
                r = tsai_wu_strength_ratio(np.asarray(sigma, float), *st, f12)
                best = min(best, float(r))
        return best

    # unit moment
    EI = float(section_ei(walls, []))
    num = den = 0.0
    for wl in walls:
        L = math.hypot(wl.x1 - wl.x0, wl.z1 - wl.z0)
        num += wl.Et * L * (wl.z0 + wl.z1) / 2.0
        den += wl.Et * L
    zc = num / den
    out = {}
    for lc, sign in (("+M", 1.0), ("-M", -1.0)):
        best = math.inf
        for g, wl in zip(geo, walls):
            for z in (wl.z0, wl.z1):
                eps = sign * (z - zc) / EI
                best = min(
                    best, wall_ratio(lam[g[5]], [wl.Et * eps, 0.0, 0.0], f12_star)
                )
        out[lc] = best
    # unit torque
    _, q = multicell_torsion(walls, cells)
    for lc, sign in (("+T", 1.0), ("-T", -1.0)):
        best = math.inf
        for g, qi in zip(geo, q):
            best = min(
                best, wall_ratio(lam[g[5]], [0.0, 0.0, sign * float(qi)], f12_star)
            )
        out[lc] = best
    return out


# ---- the report -------------------------------------------------------------------------------


def _load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text())


def build_report() -> dict:
    mats = load_materials()
    book = _load(BOOK_SCHEDULE)
    carbon = _load(CARBON_SCHEDULE)
    ledger = _load(LEDGER)

    # strength: capacities cannot be computed (counts null, chord conflict, web position unsourced)
    cell_flags = geometry_flagged_inputs(book["geometry"])
    flagged_strength = sorted(
        set(flagged_inputs(book, mats, BOOK_MATERIALS))
        | set(flagged_inputs(carbon, mats, CARBON_MATERIALS))
        | set(cell_flags)
    )
    strength_reasons = [] if GLASS_VALIDATED else ["glass_unvalidated"]
    strength = gate(
        None,
        flagged=flagged_strength,
        reasons=strength_reasons,
        test_required=test_required_inputs(mats, CARBON_MATERIALS),
    )

    mass_flags = sorted(set(flagged_strength) | set(cell_flags) | {CG_CITE_INPUT})
    mass = gate(None, flagged=mass_flags)

    elevator = gate(None, reasons=["criterion_unavailable"])
    elevator["by_analogy"] = True

    f_rel = f_consistency(None, None, flagged=mass_flags)
    f_rel["F_book"] = None
    f_rel["F_carbon"] = None

    deltas = {}
    for name in ("EI", "GJ", "torsional_inertia", "mass_per_length"):
        deltas[name] = {
            "book": None,
            "carbon": None,
            "delta_fraction": None,
            "flag": None,
            "state": "blocked",
            "reasons": ["inputs_unsourced"],
        }

    canard_row = next(r for r in ledger["closure"]["rows"] if r["name"] == "canard")
    mass_vs_closure = {
        "book_mass_lb": None,
        "closure_mass_lb": canard_row["weight_lb"],
        "closure_band_lb": canard_row["weight_band_lb"],
        "delta_fraction": None,
        "reported_only": True,
        "state": "blocked",
        "reasons": ["inputs_unsourced"],
    }

    notes = [
        "strength: blocked; book and carbon inputs are unsourced. Glass moduli are validated on one NCAMP 7781 prepreg laminate only (row 80); glass strength is not.",
        "strength: carbon warp values need an original coupon test (requires_original_test).",
        "mass_placement: blocked; cell geometry, lamina values and the destabilising-centroid citation are unsourced.",
        "elevator_balance: blocked by analogy; Report 45 elevator criteria need fuselage frequencies.",
        "reported items are blocked with the gates; none is a gate.",
    ]
    return {
        "part": "canard",
        "gates": {
            "strength": strength,
            "mass_placement": mass,
            "elevator_balance": elevator,
        },
        "reported": {
            "f_relative": f_rel,
            "stiffness_and_mass_deltas": deltas,
            "book_canard_mass_vs_closure": mass_vs_closure,
            "stiffness_flag_fraction": STIFFNESS_FLAG_FRACTION,
        },
        "stations": [dict(s) for s in STATIONS],
        "inputs_sha256": inputs_sha256(),
        "notes": notes,
    }


def render(report: dict) -> str:
    return json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"


def main(out: Path = OUT) -> None:
    Path(out).write_text(render(build_report()))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
