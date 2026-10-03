"""Mass/CG ledger: cited rows, the manual's CG envelope, and its sample loadings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import yaml

LEDGER = Path(__file__).resolve().parents[1] / "data/mass_ledger.yaml"


class Row(NamedTuple):
    name: str
    weight_lb: float
    arm_in: float
    cls: str  # primary-structure | secondary | non-structural | payload | empty
    process: str
    cite: str


@lru_cache(maxsize=1)
def load_ledger() -> dict:
    return yaml.safe_load(LEDGER.read_text())


def cg(rows: list[Row]) -> tuple[float, float]:
    w = sum(r.weight_lb for r in rows)
    return w, sum(r.weight_lb * r.arm_in for r in rows) / w


def in_envelope(weight: float, cg_in: float, env: dict) -> bool:
    return weight <= env["max_lb"] and env["fwd_fs"] <= cg_in <= env["aft_fs"]


# --- fuselage box (Block 2 M2.2 Task 4) -----------------------------------------------------------
# Constants come from data/mass_ledger.yaml `materials:` (each cited). A missing constant makes the
# dependent mass None with a "not yet computed: <input>" reason; nothing is guessed.
_IN2_PER_YD2 = 1296.0
_IN3_PER_FT3 = 1728.0
_OZ_PER_LB = 16.0
_NYC = "not yet computed: "


def _materials() -> dict:
    return load_ledger().get("materials", {})


def _core(part: str, mats: dict) -> tuple[str | None, float | None, str | None]:
    """(material, density lb/ft^3 or None, reason if density is missing)."""
    ent = mats.get("part_core", {}).get(part)
    if ent is None:
        from .fuselage_book import part_name  # lazy: fuselage_book pulls in CadQuery

        return None, None, _NYC + f"core material of {part_name(part)} not sourced"
    mat = ent["material"]
    dens = mats.get("foam_lb_ft3", {}).get(mat)
    if dens is None:
        return mat, None, _NYC + f"density of {mat.replace('_', ' ')} not sourced"
    return mat, float(dens["value"]), None


def _ply_mass_lb(
    cloth: str, area_in2: float, mats: dict
) -> tuple[float | None, str | None]:
    c = mats.get("cloth", {}).get(cloth)
    if c is None:
        return None, _NYC + f"areal weight of {cloth} cloth not sourced"
    r = mats.get("resin_to_cloth_weight")
    if r is None:
        return None, _NYC + "glass-to-resin weight ratio not sourced"
    cloth_lb = area_in2 * float(c["areal_oz_yd2"]) / _IN2_PER_YD2 / _OZ_PER_LB
    return cloth_lb * (1.0 + float(r["value"])), None


def fuselage_ledger() -> list[dict]:
    """One row per fuselage part. Masses are None (with a reason) unless every input is sourced.

    glass_complete is False when a chapter 4-6 material row for the part is excluded from the ply
    model or a mapped region under-counts (lower_bound); then total_mass_lb stays None and
    total_mass_lower_bound_lb (core plus the glass that is placed) is the most the ledger will say.
    """
    from .fuselage_book import build_fuselage
    from .fuselage_plies import excluded_by_part, plies

    mats = _materials()
    parts = build_fuselage()
    pl = plies()
    unplaced = excluded_by_part()
    rows = []
    for name, part in parts.items():
        if part.void:  # a cut-away volume (the canard opening), not a part: it has no mass and no row
            continue
        vol = part.solid.val().Volume()
        arm_core = part.solid.val().Center().x
        mat, dens, why = _core(name, mats)
        core = None if dens is None else vol * dens / _IN3_PER_FT3
        mine = [p for p in pl if p.part == name]
        count: dict[str, int] = {}
        area: dict[str, float] = {}
        for p in mine:
            count[p.cloth] = count.get(p.cloth, 0) + 1
            area[p.cloth] = area.get(p.cloth, 0.0) + p.area_in2
        glass: float | None = 0.0
        g_why = None
        g_moment = 0.0
        for p in mine:
            m, w = _ply_mass_lb(p.cloth, p.area_in2, mats)
            if m is None:
                glass, g_why = None, w
                break
            glass += m
            g_moment += m * p.arm_in
        if glass is None:
            g_moment = 0.0
        missing_rows = unplaced.get(name, [])
        partial = bool(missing_rows) or any(p.lower_bound for p in mine)
        complete = glass is not None and not partial
        # total mass: only when core and glass are both fully sourced and the glass is complete
        total = lower = None
        t_why = None
        arm = arm_lb = None
        if core is None:
            t_why = why
        elif glass is None:
            t_why = g_why
        elif partial:
            t_why = (
                _NYC
                + "glass rows not fully placed ("
                + (
                    f"{len(missing_rows)} excluded row(s)"
                    if missing_rows
                    else "under-counted regions"
                )
                + ")"
            )
        if core is not None and glass is not None:
            lower = core + glass
            arm_lb = (core * arm_core + g_moment) / lower
            if not partial:
                total, arm = lower, arm_lb
        rows.append(
            {
                "part": name,
                "fidelity": part.fidelity,
                "material": mat,
                "volume_in3": vol,
                "core_mass_lb": core,
                "core_mass_reason": why,
                "ply_count": count,
                "ply_area_in2": area,
                "glass_mass_lb": glass,
                "glass_mass_reason": g_why,
                "glass_complete": complete,
                "glass_unplaced_rows": list(missing_rows),
                "glass_lower_bound_regions": sorted(
                    {p.op for p in mine if p.lower_bound}
                ),
                "total_mass_lb": total,
                "total_mass_reason": t_why,
                "total_mass_lower_bound_lb": lower,
                "arm_core_in": arm_core,
                "arm_in": arm,
                "arm_lower_bound_in": arm_lb,
            }
        )
    return rows


def fuselage_cg(
    lower_bound: bool = False,
) -> tuple[float, float | None, list[str], dict[str, str]]:
    """Empty-structure CG so far: (weight_lb, arm_in, included parts, {excluded part: reason}).

    Strict (default) uses total_mass_lb, so only parts whose core and glass are fully sourced and
    fully placed. lower_bound=True uses total_mass_lower_bound_lb (core plus the placed glass), the
    most that can be said while rows remain unplaced.
    """
    key, arm_key = (
        ("total_mass_lower_bound_lb", "arm_lower_bound_in")
        if lower_bound
        else ("total_mass_lb", "arm_in")
    )
    inc: list[str] = []
    exc: dict[str, str] = {}
    w = m = 0.0
    proto = load_ledger().get("prototype_weights", {}).get("rows", {})
    for r in fuselage_ledger():
        if r[key] is None:
            exc[r["part"]] = (
                r["total_mass_reason"]
                or r["core_mass_reason"]
                or r["glass_mass_reason"]
                or _NYC + "mass"
            )
            continue
        # A lower bound may not contain a term a cited source contradicts: a part modelled heavier than its CP26 prototype
        # weight is left out (not replaced by the prototype number) until the excess is understood (ledger-closure test).
        if (
            lower_bound
            and r["part"] in proto
            and r[key] > proto[r["part"]]["weight_lb"]
        ):
            exc[r["part"]] = (
                f"modelled {r[key]:.2f} lb is above the CP26 prototype weight {proto[r['part']]['weight_lb']:.2f} lb: under review"
            )
            continue
        inc.append(r["part"])
        w += r[key]
        m += r[key] * r[arm_key]
    return w, (m / w if w else None), inc, exc


# --- landing gear (Block 2 M2.3 Task 4) ------------------------------------------------------------
# The retired 45 lb lump, decomposed in data/mass_ledger.yaml `gear:`. Rows with status "unsourced"
# stay in the physics empty weight (core/analysis.py) but never enter a lower bound.
class GearRow(NamedTuple):
    name: str
    label: str
    weight_lb: float
    arm_in: float
    status: str  # book | unsourced
    arm_status: str  # book | approximate | conflict | unsourced
    cite: tuple[str, ...]
    note: str


def gear_rows() -> list[GearRow]:
    """The decomposed gear rows with their status flags (every cite checked against the registry)."""
    from .sources import check_citation

    rows = []
    for r in load_ledger()["gear"]["rows"]:
        for c in r["cite"]:
            check_citation(c)
        if r["status"] != "unsourced" and not r["cite"]:
            raise ValueError(f"gear row {r['name']}: a sourced row needs a citation")
        rows.append(
            GearRow(
                r["name"],
                r["label"],
                float(r["weight_lb"]),
                float(r["arm_in"]),
                r["status"],
                r["arm_status"],
                tuple(r["cite"]),
                r["note"],
            )
        )
    return rows


def gear_cg(sourced_only: bool = False) -> tuple[float, float | None]:
    """(weight_lb, arm_in) of the gear rows; sourced_only drops every row whose status is unsourced."""
    rows = [r for r in gear_rows() if not sourced_only or r.status != "unsourced"]
    w = sum(r.weight_lb for r in rows)
    return w, (sum(r.weight_lb * r.arm_in for r in rows) / w if w else None)


def gear_json() -> dict:
    from .landing_gear_book import (
        ground_handling,
    )  # lazy: landing_gear_book pulls in CadQuery
    from .nose_gear_kin import AXLE_FS_CANDIDATES

    cand = load_ledger()["gear"]["nose_arm_candidates"]
    values = [float(v) for v in cand["values_in"]]
    if values != [float(v) for v in AXLE_FS_CANDIDATES]:
        raise ValueError(
            f"nose_arm_candidates {values} disagree with config {AXLE_FS_CANDIDATES}"
        )
    rows = []
    for r in gear_rows():
        d = r._asdict() | {"cite": list(r.cite)}
        if r.name == "nose_strut":
            d["nose_arm_candidates"] = values
            d["nose_arm_candidates_status"] = cand["status"]
        rows.append(d)
    return {
        "rows": rows,
        "nose_arm_candidates": values,
        "nose_arm_candidates_status": cand["status"],
        "total_lb": gear_cg()[0],
        "sourced_lb": gear_cg(sourced_only=True)[0],
        "ground_handling": ground_handling(),
    }


def _lower_bound_with_gear() -> dict:
    """cg_lower_bound: the fuselage's placed core and glass plus the sourced gear rows (never the unsourced one)."""
    w, arm, inc, exc = fuselage_cg(lower_bound=True)
    m = w * arm if arm is not None else 0.0
    for r in gear_rows():
        if r.status == "unsourced":
            exc[r.name] = _NYC + "weight and arm of " + r.label.lower() + " not sourced"
            continue
        inc.append(r.name)
        w += r.weight_lb
        m += r.weight_lb * r.arm_in
    return {
        "weight_lb": w,
        "arm_in": (m / w if w else None),
        "included": inc,
        "excluded": exc,
    }


def fuselage_ledger_json() -> dict:
    """Plain, JSON-serialisable ledger for the lab readout: per-part rows and both CG results."""

    def cg_dict(lower: bool) -> dict:
        w, arm, inc, exc = fuselage_cg(lower_bound=lower)
        return {"weight_lb": w, "arm_in": arm, "included": inc, "excluded": exc}

    return {
        "units": {
            "mass": "lb",
            "arm": "in (fuselage station)",
            "area": "in^2",
            "volume": "in^3",
        },
        "parts": fuselage_ledger(),
        "cg": cg_dict(False),
        "cg_lower_bound": _lower_bound_with_gear(),
        "gear": gear_json(),
        "notes": [
            "cg: parts whose core and glass are both fully sourced and placed (none yet).",
            "cg_lower_bound: core plus only the glass rows that are placed, plus the sourced gear rows (main and nose strut); never the unsourced wheels and brakes row. An undercount, not a weight.",
        ],
    }
