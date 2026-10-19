from __future__ import annotations

from pathlib import Path

import yaml

from core.ledger import load_ledger
from hangar.mission import _to_value, apply_effect, load_mission

_PLANTS = Path(__file__).resolve().parents[1] / "data/hangar/mod-ez/powerplants.yaml"
_BOOK_LB = 243.0
_BOOK_ARM = 141.05
_FUELS = ("full", "mission", "reserve")
_STATES = ("takeoff", "landing")
_LIMITS = ("fwd", "aft", "gross")
_FIELDS = {"fwd": "fwd_margin_in", "aft": "aft_margin_in", "gross": "gross_margin_lb"}
_RANK = {"sourced": 0, "derived": 1, "unknown": 2}
_SCAN_LO = 50.0
_SCAN_HI = 400.0
_SCAN_STEP = 0.5


def _worst(flags: list[str]) -> str:
    return max(flags, key=lambda flag: _RANK.get(flag, 1))


def public_occupancies() -> list[dict]:
    rows = []
    for weight in range(120, 221, 10):
        rows.append(
            {
                "id": f"solo-{weight}",
                "words": f"solo {weight} lb",
                "front_lb": float(weight),
                "rear_lb": 0.0,
            }
        )
    for front in (120, 170, 220):
        for rear in (120, 170, 220):
            rows.append(
                {
                    "id": f"two-{front}-{rear}",
                    "words": f"two up {front} lb front, {rear} lb rear",
                    "front_lb": float(front),
                    "rear_lb": float(rear),
                }
            )
    return rows


def public_bags() -> list[dict]:
    return [
        {"id": "none", "label": "no baggage", "lb": 0.0},
        {"id": "light", "label": "light overnight bag", "lb": 15.0},
    ]


def _prepare(engine: str, extras, plants, mission) -> dict:
    extras = list(extras or [])
    if plants is None:
        plants = yaml.safe_load(_PLANTS.read_text())
    if mission is None:
        mission = load_mission(None)
    plant = plants[engine]
    inst = _to_value(plant["installed_lb"])
    cg_arm = _to_value(plant["cg_arm_in"])
    flow = _to_value(plant["cruise_ff_gph"])
    density = _to_value(mission["fuel_density_lb_per_gal"])
    cap = _to_value(mission["fuel_capacity_gal"])
    cruise = _to_value(mission["cruise_ktas"])
    missing = any(e.get("weight_lb") is None or e.get("arm_in") is None for e in extras)
    unknown = missing or any(
        value is None for value in (inst.v, cg_arm.v, flow.v, density.v, cap.v, cruise.v)
    )
    ledger = load_ledger()
    loads = ledger["loads"]
    ctx = {
        "unknown": unknown,
        "flag": "unknown",
        "fwd_fs": float(ledger["envelope"]["fwd_fs"]),
        "aft_fs": float(ledger["envelope"]["aft_fs"]),
        "max_lb": float(ledger["envelope"]["max_lb"]),
        "oil": float(ledger["samples"]["light_pilot"]["items"]["oil"]),
        "oil_arm": float(loads["oil"]["arm_in"]),
        "fuel_arm": float(loads["fuel"]["arm_in"]),
        "pilot_arm": float(loads["pilot"]["arm_in"]),
        "pax_arm": float(loads["passenger"]["arm_in"]),
        "bag_arm": float(loads["baggage"]["arm_in"]),
        "empty_w": 0.0,
        "empty_m": 0.0,
        "fuels": {},
    }
    if unknown:
        return ctx
    flags = [inst.flag, cg_arm.flag, flow.flag, density.flag, cap.flag, cruise.flag]
    flags.extend(e.get("flag", "derived") for e in extras)
    ctx["flag"] = _worst([*flags, "derived"])
    extra_w = sum(float(e["weight_lb"]) for e in extras)
    extra_m = sum(float(e["weight_lb"]) * float(e["arm_in"]) for e in extras)
    base_w = float(ledger["empty"]["weight_lb"])
    base_arm = float(ledger["empty"]["arm_in"])
    ctx["empty_w"] = base_w - _BOOK_LB + float(inst.v) + extra_w
    ctx["empty_m"] = base_w * base_arm - _BOOK_LB * _BOOK_ARM + float(inst.v) * float(cg_arm.v) + extra_m
    leg = float(flow.v) * (float(mission["leg_nm"]) / float(cruise.v)) * float(density.v)
    reserve = float(flow.v) * (float(mission["reserve_min"]) / 60.0) * float(density.v)
    takeoff = {
        "full": float(cap.v) * float(density.v),
        "mission": leg + reserve,
        "reserve": reserve,
    }
    ctx["fuels"] = {name: {"takeoff": weight, "landing": max(weight - leg, reserve)} for name, weight in takeoff.items()}
    return ctx


def _score(ctx: dict, front: float, rear: float, bag_lb: float, fuel: str, state: str):
    fuel_lb = ctx["fuels"][fuel][state]
    gross = ctx["empty_w"] + ctx["oil"] + front + rear + bag_lb + fuel_lb
    moment = (
        ctx["empty_m"]
        + ctx["oil"] * ctx["oil_arm"]
        + front * ctx["pilot_arm"]
        + rear * ctx["pax_arm"]
        + bag_lb * ctx["bag_arm"]
        + fuel_lb * ctx["fuel_arm"]
    )
    cg = moment / gross
    fwd = cg - ctx["fwd_fs"]
    aft = ctx["aft_fs"] - cg
    return fuel_lb, gross, cg, fwd, aft, ctx["max_lb"] - gross


def _cell(ctx: dict, occ: dict, bag: dict, fuel: str, state: str) -> dict:
    row = {
        "id": f"{occ['id']}|{bag['id']}|{fuel}|{state}",
        "occupancy": occ["id"],
        "occupancy_label": occ["words"],
        "bag": bag["id"],
        "bag_label": bag["label"],
        "fuel": fuel,
        "state": state,
        "fuel_lb": None,
        "gross_lb": None,
        "cg_in": None,
        "fwd_margin_in": None,
        "aft_margin_in": None,
        "gross_margin_lb": None,
        "ok": None,
        "flag": "unknown",
        "loading": f"{occ['words']}, {bag['label']}, {fuel} fuel, {state}",
    }
    if ctx["unknown"]:
        return row
    fuel_lb, gross, cg, fwd, aft, room = _score(
        ctx, float(occ["front_lb"]), float(occ["rear_lb"]), float(bag["lb"]), fuel, state
    )
    row.update(
        {
            "fuel_lb": fuel_lb,
            "gross_lb": gross,
            "cg_in": cg,
            "fwd_margin_in": fwd,
            "aft_margin_in": aft,
            "gross_margin_lb": room,
            "ok": fwd >= 0.0 and aft >= 0.0 and room >= 0.0,
            "flag": ctx["flag"],
        }
    )
    return row


def _pick(cells: list[dict], field: str):
    chosen = None
    best = None
    for cell in cells:
        value = cell[field]
        if value is None:
            continue
        if chosen is None or value < best:
            chosen = cell
            best = value
    return chosen


def _assemble(engine: str, ctx: dict, occupancies, bags) -> dict:
    cells = [_cell(ctx, occ, bag, fuel, state) for occ in occupancies for bag in bags for fuel in _FUELS for state in _STATES]
    flags = [cell["flag"] for cell in cells]
    return {
        "engine": engine,
        "cells": cells,
        "cell_count": len(cells),
        "unknown_cells": sum(cell["cg_in"] is None for cell in cells),
        "flag": _worst(flags) if flags else "sourced",
        "worst": {limit: _pick(cells, _FIELDS[limit]) for limit in _LIMITS},
    }


def build(engine, extras, plants, mission, occupancies, bags) -> dict:
    return _assemble(engine, _prepare(engine, extras, plants, mission), occupancies, bags)


def solo_limit_margin(engine, pilot_lb, limit, extras, plants, mission):
    occupancy = {
        "id": f"solo-{pilot_lb:g}",
        "words": f"solo {pilot_lb:g} lb",
        "front_lb": float(pilot_lb),
        "rear_lb": 0.0,
    }
    made = build(engine, extras, plants, mission, [occupancy], public_bags())
    if made["unknown_cells"]:
        return None
    return min(cell[_FIELDS[limit]] for cell in made["cells"])


def _mins(ctx: dict, pilot: float, bags) -> list[float]:
    totals = [None, None, None]
    for bag in bags:
        for fuel in _FUELS:
            for state in _STATES:
                scored = _score(ctx, float(pilot), 0.0, float(bag["lb"]), fuel, state)
                for index in range(3):
                    value = scored[3 + index]
                    if totals[index] is None or value < totals[index]:
                        totals[index] = value
    return totals


def _bisect(ctx, bags, index: int, lo: float, hi: float, lo_bad: bool) -> float:
    while hi - lo > 0.01:
        mid = (lo + hi) / 2.0
        bad = _mins(ctx, mid, bags)[index] < 0.0
        if bad == lo_bad:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _note(above, below, bad: bool) -> str:
    if above is None and below is None:
        kind = "binds" if bad else "holds"
        return f"{kind} for every solo pilot from 50 to 400 lb"
    parts = []
    if above is not None:
        parts.append(f"heavier solo pilots break the limit above {above:.0f} lb")
    if below is not None:
        parts.append(f"lighter solo pilots break the limit below {below:.0f} lb")
    return "; ".join(parts)


def _crossings(ctx: dict) -> dict:
    if ctx["unknown"]:
        blank = {"fails_above_lb": None, "fails_below_lb": None, "note": "inputs unknown"}
        return {limit: dict(blank) for limit in _LIMITS}
    count = int(round((_SCAN_HI - _SCAN_LO) / _SCAN_STEP))
    weights = [_SCAN_LO + index * _SCAN_STEP for index in range(count + 1)]
    bags = public_bags()
    above = [None, None, None]
    below = [None, None, None]
    prev_w = weights[0]
    prev = _mins(ctx, prev_w, bags)
    prev_bad = [value < 0.0 for value in prev]
    any_bad = list(prev_bad)
    for weight in weights[1:]:
        current = _mins(ctx, weight, bags)
        for index in range(3):
            bad = current[index] < 0.0
            any_bad[index] = any_bad[index] or bad
            if bad != prev_bad[index]:
                open_above = (not prev_bad[index]) and above[index] is None
                open_below = prev_bad[index] and below[index] is None
                if open_above or open_below:
                    root = _bisect(ctx, bags, index, prev_w, weight, prev_bad[index])
                    if prev_bad[index]:
                        below[index] = root
                    else:
                        above[index] = root
            prev_bad[index] = bad
        prev_w = weight
    return {
        limit: {
            "fails_above_lb": above[index],
            "fails_below_lb": below[index],
            "note": _note(above[index], below[index], any_bad[index]),
        }
        for index, limit in enumerate(_LIMITS)
    }


def matrix(engine, extras=None, plants=None, mission=None) -> dict:
    ctx = _prepare(engine, extras, plants, mission)
    made = _assemble(engine, ctx, public_occupancies(), public_bags())
    made["crossings"] = _crossings(ctx)
    return made


def matrix_for_effect(effect, mission=None) -> dict:
    engine, extras, plants = apply_effect(effect)
    return matrix(engine, extras, plants, mission)
