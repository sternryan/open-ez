from dataclasses import dataclass
from pathlib import Path
from typing import Any
import dataclasses
import yaml
import os
from hangar.records import dump_record
from core.ledger import load_ledger, in_envelope

_DATA = Path(__file__).resolve().parents[1] / "data" / "hangar" / "mod-ez"

@dataclass(frozen=True)
class Value:
    v: float | None
    flag: str  # "sourced"|"derived"|"unknown"
    note: str = ""

@dataclass(frozen=True)
class MissionScore:
    option: str
    empty_lb: Value
    empty_cg: Value
    fuel_needed_lb: Value
    takeoff_lb: Value
    takeoff_cg: Value
    landing_cg: Value
    range_full_fuel_nm: Value
    block_time_h: Value
    in_envelope: bool | None
    assumptions: list[str]
    worst_flag: str

@dataclass(frozen=True)
class LoadingScore:
    option: str
    loading: str
    takeoff_lb: Value
    takeoff_cg: Value
    landing_lb: Value
    landing_cg: Value
    fwd_margin_in: Value
    in_envelope: bool | None
    assumptions: list[str]
    worst_flag: str

BOOK_WEIGHT_LB = 243
BOOK_ARM_IN = 141.05

FLAG_ORDER = {"unknown": 3, "derived": 2, "sourced": 1}

def _get_worst_flag(flags: list[str]) -> str:
    if not flags:
        return "sourced"
    return max(flags, key=lambda f: FLAG_ORDER.get(f, 0))

def _to_value(data: Any) -> Value:
    if isinstance(data, dict):
        v = data.get("v")
        flag = data.get("flag", "sourced")
        note = data.get("note", "")
        if v is None:
            return Value(None, "unknown", note)
        return Value(v, flag, note)
    # For private overrides: bare numbers become "derived"
    return Value(data, "derived", "")

def load_mission(private_dir: Path | None = None) -> dict:
    path = _DATA / "mission.yaml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if private_dir and (private_dir / "mission.yaml").exists():
        with open(private_dir / "mission.yaml", "r") as f:
            extra = yaml.safe_load(f)
        if isinstance(extra, dict):
            data.update(extra)
    return data

def score(option_id: str, mission: dict = None, plants: dict = None) -> MissionScore:
    if mission is None:
        priv = os.environ.get("HANGAR_PRIVATE_DIR")
        mission = load_mission(Path(priv) if priv else None)
    if plants is None:
        with open(_DATA / "powerplants.yaml", "r") as f:
            plants = yaml.safe_load(f)

    # Convert all Value-shaped dicts to Value objects
    m = {}
    for k, val in mission.items():
        m[k] = _to_value(val) if isinstance(val, dict) else _to_value(val) if k in ["cruise_ktas", "fuel_capacity_gal", "fuel_density_lb_per_gal"] else val
    
    # Re-handle mission keys that are plain numbers but should be treated as Values for logic
    # Actually, the task says: "A bare number in the private override for a Value-shaped key becomes Value(..., 'derived', 'private override')"
    # and "plain keys (leg_nm, occupants_lb...) are used as given".
    # Let's refine the conversion:
    m = {}
    value_keys = {"cruise_ktas", "fuel_capacity_gal", "fuel_density_lb_per_gal"}
    for k, val in mission.items():
        if k in value_keys:
            m[k] = _to_value(val)
        else:
            m[k] = val

    p_raw = plants[option_id]
    p = {}
    for k, val in p_raw.items():
        p[k] = _to_value(val) if isinstance(val, dict) else _to_value(val)

    ledger = load_ledger()
    env = ledger["envelope"]
    loads = ledger["loads"]

    # Constants/Inputs
    # ledger values
    BASE_EMPTY_LB = float(ledger["empty"]["weight_lb"])
    BASE_EMPTY_ARM = float(ledger["empty"]["arm_in"])
    OIL_LB = ledger["samples"]["light_pilot"]["items"]["oil"]
    OIL_ARM = ledger["loads"]["oil"]["arm_in"]

    # 1. empty_lb
    inst_lb = p["installed_lb"]
    empty_lb_val = BASE_EMPTY_LB - BOOK_WEIGHT_LB + inst_lb.v if inst_lb.v is not None else None
    empty_lb = Value(empty_lb_val, inst_lb.flag)

    # 2. empty_cg
    cg_arm_in = p["cg_arm_in"]
    if inst_lb.v is not None and cg_arm_in.v is not None:
        empty_cg_v = (BASE_EMPTY_LB * BASE_EMPTY_ARM - BOOK_WEIGHT_LB * BOOK_ARM_IN + inst_lb.v * cg_arm_in.v) / empty_lb_val
        empty_cg = Value(empty_cg_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag]), cg_arm_in.note)
    elif inst_lb.flag == "unknown" or cg_arm_in.flag == "unknown":
        empty_cg = Value(None, "unknown")
    else:
        empty_cg = Value(None, "unknown")

    # 3. block_time_h
    if m["leg_nm"] is not None and m["reserve_min"] is not None and m["cruise_ktas"].v is not None:
        block_time_v = m["leg_nm"] / m["cruise_ktas"].v + m["reserve_min"] / 60
        block_time = Value(block_time_v, _get_worst_flag([m["cruise_ktas"].flag]))
    else:
        block_time = Value(None, "unknown")

    # 4. fuel_needed_lb
    if p["cruise_ff_gph"].v is not None and block_time.v is not None and m["fuel_density_lb_per_gal"].v is not None:
        fuel_needed_v = p["cruise_ff_gph"].v * block_time.v * m["fuel_density_lb_per_gal"].v
        fuel_needed = Value(fuel_needed_v, _get_worst_flag([p["cruise_ff_gph"].flag, m["cruise_ktas"].flag, m["fuel_density_lb_per_gal"].flag]))
    else:
        fuel_needed = Value(None, "unknown")

    # 5. takeoff_lb and takeoff_cg
    # mission may override oil_lb
    oil_lb_val = m.get("oil_lb", OIL_LB)
    if isinstance(oil_lb_val, dict):
        oil_lb_val = _to_value(oil_lb_val).v
    
    if empty_lb_val is not None and fuel_needed.v is not None and m["cruise_ktas"].v is not None and m["fuel_density_lb_per_gal"].v is not None:
        takeoff_lb_v = empty_lb_val + sum(m["occupants_lb"]) + m["bags_lb"] + fuel_needed.v + oil_lb_val
        takeoff_lb = Value(takeoff_lb_v, _get_worst_flag([inst_lb.flag, fuel_needed.flag]))
        if cg_arm_in.v is not None:
            base_moment = BASE_EMPTY_LB * BASE_EMPTY_ARM - BOOK_WEIGHT_LB * BOOK_ARM_IN
            moments = base_moment + (inst_lb.v * cg_arm_in.v)
            moments += m["occupants_lb"][0] * loads["pilot"]["arm_in"]
            moments += m["occupants_lb"][1] * loads["passenger"]["arm_in"]
            moments += m["bags_lb"] * loads["baggage"]["arm_in"]
            moments += fuel_needed.v * loads["fuel"]["arm_in"]
            moments += oil_lb_val * OIL_ARM
            takeoff_cg = Value(moments / takeoff_lb_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag, fuel_needed.flag]))
        else:
            takeoff_cg = Value(None, "unknown")
    else:
        takeoff_lb = Value(None, "unknown")
        takeoff_cg = Value(None, "unknown")

    # 6. landing_cg
    if takeoff_lb.v is not None and fuel_needed.v is not None and takeoff_cg.v is not None:
        leg_fuel_v = p["cruise_ff_gph"].v * (m["leg_nm"] / m["cruise_ktas"].v) * m["fuel_density_lb_per_gal"].v
        landing_lb_v = takeoff_lb.v - leg_fuel_v
        # Recalculate moments for landing (subtract fuel used)
        # Note: we must also subtract the oil if it was part of the takeoff weight but not the fuel? 
        # No, oil is always there. We only subtract the fuel used during the leg.
        moments_landing = (takeoff_lb.v * takeoff_cg.v) - (leg_fuel_v * loads["fuel"]["arm_in"])
        landing_cg_v = moments_landing / landing_lb_v
        landing_cg = Value(landing_cg_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag, fuel_needed.flag]))
        landing_lb_v = landing_lb_v
    else:
        landing_cg = Value(None, "unknown")
        landing_lb_v = None

    # 7. range_full_fuel_nm
    if m["fuel_capacity_gal"].v is not None and p["cruise_ff_gph"].v is not None and m["cruise_ktas"].v is not None and m["reserve_min"] is not None:
        range_v = (m["fuel_capacity_gal"].v / p["cruise_ff_gph"].v - m["reserve_min"] / 60) * m["cruise_ktas"].v
        range_full_fuel_nm = Value(range_v, _get_worst_flag([m["fuel_capacity_gal"].flag, p["cruise_ff_gph"].flag, m["cruise_ktas"].flag]))
    else:
        range_full_fuel_nm = Value(None, "unknown")

    # 8. in_envelope
    in_env = None
    if takeoff_lb.v is not None and takeoff_cg.v is not None and landing_lb_v is not None and landing_cg.v is not None:
        in_env = in_envelope(takeoff_lb.v, takeoff_cg.v, env) and in_envelope(landing_lb_v, landing_cg.v, env)

    # 9. assumptions
    assumptions = []
    # "include the non-empty note of every input Value used (installed_lb, cg_arm_in, cruise_ff_gph, and the mission's cruise, capacity, density) 
    # when its flag is not 'sourced' OR its note is non-empty; no duplicates, keep order."
    inputs_to_check = [
        inst_lb, cg_arm_in, p["cruise_ff_gph"], 
        m["cruise_ktas"], m["fuel_capacity_gal"], m["fuel_density_lb_per_gal"]
    ]
    for val in inputs_to_check:
        if val.flag != "sourced" or val.note:
            if val.note and val.note not in assumptions:
                assumptions.append(val.note)

    # 10. worst_flag
    all_flags = [empty_lb.flag, empty_cg.flag, fuel_needed.flag, takeoff_lb.flag, takeoff_cg.flag, landing_cg.flag, range_full_fuel_nm.flag, block_time.flag]
    worst_flag = _get_worst_flag(all_flags)

    return MissionScore(
        option=option_id,
        empty_lb=empty_lb,
        empty_cg=empty_cg,
        fuel_needed_lb=fuel_needed,
        takeoff_lb=takeoff_lb,
        takeoff_cg=takeoff_cg,
        landing_cg=landing_cg,
        range_full_fuel_nm=range_full_fuel_nm,
        block_time_h=block_time,
        in_envelope=in_env,
        assumptions=assumptions,
        worst_flag=worst_flag
    )

def load_loadings() -> dict:
    """Compose loadings from ledger sample rows. Dropping a row flags the result derived."""
    with open(_DATA / "loadings.yaml", "r") as f:
        raw = yaml.safe_load(f)
    samples = load_ledger()["samples"]
    out = {}
    for name, entry in raw.items():
        dropped = entry.get("drop") or []
        items = {
            key: weight
            for key, weight in samples[entry["from"]]["items"].items()
            if key not in dropped
        }
        out[name] = {
            "items": items,
            "label": entry["label"],
            "flag": "derived" if dropped else "sourced",
        }
    return out

def _mission_and_plants(mission: dict | None, plants: dict | None) -> tuple[dict, dict]:
    """Same defaults as score(): private mission override, public powerplants file."""
    if mission is None:
        priv = os.environ.get("HANGAR_PRIVATE_DIR")
        mission = load_mission(Path(priv) if priv else None)
    if plants is None:
        with open(_DATA / "powerplants.yaml", "r") as f:
            plants = yaml.safe_load(f)
    return mission, plants

def score_loading(
    option_id: str,
    loading_id: str,
    mission: dict | None = None,
    plants: dict | None = None,
    extras: list[dict] | None = None,
) -> LoadingScore:
    mission, plants = _mission_and_plants(mission, plants)
    plant_raw = plants[option_id]
    loading = load_loadings()[loading_id] if isinstance(loading_id, str) else loading_id
    loading_id = loading_id if isinstance(loading_id, str) else loading.get("id", "custom")

    value_keys = {"cruise_ktas", "fuel_capacity_gal", "fuel_density_lb_per_gal"}
    m = {}
    for key, val in mission.items():
        m[key] = _to_value(val) if key in value_keys else val
    plant = {key: _to_value(val) for key, val in plant_raw.items()}

    ledger = load_ledger()
    env = ledger["envelope"]
    arms = ledger["loads"]
    base_lb = float(ledger["empty"]["weight_lb"])
    base_arm = float(ledger["empty"]["arm_in"])
    items = loading["items"]
    extras = list(extras or [])
    ex_known = all(e.get("weight_lb") is not None and e.get("arm_in") is not None for e in extras)
    ex_w = sum(e["weight_lb"] for e in extras) if ex_known else 0.0
    ex_m = sum(e["weight_lb"] * e["arm_in"] for e in extras) if ex_known else 0.0
    loading_flag = _get_worst_flag([loading["flag"], *[e.get("flag", "derived") for e in extras]])

    inst = plant["installed_lb"]
    cg_arm = plant["cg_arm_in"]
    flow = plant["cruise_ff_gph"]
    density = m["fuel_density_lb_per_gal"]
    reserve_min = m["reserve_min"]

    def flagged(unknown: bool, *flags: str) -> str:
        # A None value is unknown. A derived loading is at least derived; unknown still wins.
        if unknown:
            return "unknown"
        return _get_worst_flag([*flags, loading_flag])

    weights_known = inst.v is not None and ex_known
    cg_known = weights_known and cg_arm.v is not None
    burn_known = flow.v is not None and density.v is not None and reserve_min is not None

    if weights_known:
        empty_lb = base_lb - BOOK_WEIGHT_LB + inst.v
        takeoff_w = empty_lb + sum(items.values()) + ex_w
        takeoff_lb = Value(takeoff_w, flagged(False, inst.flag))
    else:
        takeoff_w = None
        takeoff_lb = Value(None, "unknown")

    if cg_known:
        empty_m = base_lb * base_arm - BOOK_WEIGHT_LB * BOOK_ARM_IN + inst.v * cg_arm.v
        takeoff_m = empty_m + sum(items[key] * arms[key]["arm_in"] for key in items) + ex_m
        takeoff_cg = Value(takeoff_m / takeoff_w, flagged(False, inst.flag, cg_arm.flag))
    else:
        takeoff_m = None
        takeoff_cg = Value(None, "unknown")

    # Unknown fuel flow, density, or reserve blanks landing, the forward margin, and the envelope.
    if weights_known and burn_known:
        reserve_lb = flow.v * (reserve_min / 60) * density.v
        burned = items["fuel"] - reserve_lb
        landing_w = takeoff_w - burned
        landing_lb = Value(landing_w, flagged(False, inst.flag, flow.flag, density.flag))
        if cg_known:
            landing_m = takeoff_m - burned * arms["fuel"]["arm_in"]
            landing_cg = Value(
                landing_m / landing_w,
                flagged(False, inst.flag, cg_arm.flag, flow.flag, density.flag),
            )
        else:
            landing_cg = Value(None, "unknown")
    else:
        landing_lb = Value(None, "unknown")
        landing_cg = Value(None, "unknown")

    if takeoff_cg.v is not None and landing_cg.v is not None:
        margin = min(takeoff_cg.v, landing_cg.v) - env["fwd_fs"]
        fwd_margin = Value(
            margin, flagged(False, inst.flag, cg_arm.flag, flow.flag, density.flag)
        )
    else:
        fwd_margin = Value(None, "unknown")

    if None not in (takeoff_lb.v, takeoff_cg.v, landing_lb.v, landing_cg.v):
        inside = in_envelope(takeoff_lb.v, takeoff_cg.v, env) and in_envelope(
            landing_lb.v, landing_cg.v, env
        )
    else:
        inside = None

    assumptions: list[str] = []
    for val in (inst, cg_arm, flow, density):
        if val.flag != "sourced" or val.note:
            if val.note and val.note not in assumptions:
                assumptions.append(val.note)
    if loading["label"] not in assumptions:
        assumptions.append(loading["label"])
    for e in extras:
        assumptions.append(f"{e.get('name', 'extra weight')}: {e.get('weight_lb')} lb at {e.get('arm_in')} in")

    outputs = (takeoff_lb, takeoff_cg, landing_lb, landing_cg, fwd_margin)
    return LoadingScore(
        option=option_id,
        loading=loading_id,
        takeoff_lb=takeoff_lb,
        takeoff_cg=takeoff_cg,
        landing_lb=landing_lb,
        landing_cg=landing_cg,
        fwd_margin_in=fwd_margin,
        in_envelope=inside,
        assumptions=assumptions,
        worst_flag=_get_worst_flag([item.flag for item in outputs]),
    )

def _pilot_loading(option_id, pilot_lb, passenger_lb, mission, plants):
    """A solo or two-up loading: oil from the book rows, the mission's fuel and baggage, the pilot in front, an optional rear seat."""
    fuel = score(option_id, mission, plants).fuel_needed_lb
    if fuel.v is None:
        return None
    bags = mission.get("bags_lb", 0) or 0
    items = {"oil": float(load_ledger()["samples"]["light_pilot"]["items"]["oil"]), "fuel": fuel.v, "pilot": float(pilot_lb)}
    if passenger_lb:
        items["passenger"] = float(passenger_lb)
    if bags:
        items["baggage"] = float(bags)
    seat = "two up" if passenger_lb else "solo, rear seat empty"
    return {
        "id": f"pilot-{pilot_lb:g}" + (f"+{passenger_lb:g}" if passenger_lb else ""),
        "items": items,
        "label": f"{seat}: pilot {pilot_lb:g} lb, mission fuel at takeoff and the reserve only at landing, mission baggage",
        "flag": "derived" if fuel.flag != "sourced" else "sourced",
    }


def score_pilot(
    option_id: str,
    pilot_lb: float,
    passenger_lb: float = 0.0,
    mission: dict | None = None,
    plants: dict | None = None,
    extras: list[dict] | None = None,
) -> LoadingScore:
    """Score one pilot weight (front seat), alone or with a rear passenger, at takeoff and at landing with the reserve only."""
    mission, plants = _mission_and_plants(mission, plants)
    loading = _pilot_loading(option_id, pilot_lb, passenger_lb, mission, plants)
    if loading is None:
        unknown = Value(None, "unknown")
        return LoadingScore(option_id, f"pilot-{pilot_lb:g}", unknown, unknown, unknown, unknown, unknown, None,
                            ["fuel flow or density unknown"], "unknown")
    return score_loading(option_id, loading, mission, plants, extras=extras)


def _public(mission: dict | None) -> dict:
    return load_mission(None) if mission is None else mission


def solo_crossing_weight(
    option_id: str,
    extras: list[dict] | None = None,
    mission: dict | None = None,
    plants: dict | None = None,
    lo: float = 50.0,
    hi: float = 400.0,
) -> Value:
    """Solo pilot weight (lb) at which the forward margin reaches zero. Public mission by default, never the private one.

    v is None with a note when the margin never reaches zero in [lo, hi] or the inputs are unknown."""
    mission = _public(mission)

    def margin(w: float):
        return score_pilot(option_id, w, mission=mission, plants=plants, extras=extras).fwd_margin_in.v

    mlo, mhi = margin(lo), margin(hi)
    if mlo is None or mhi is None:
        return Value(None, "unknown", "inputs unknown")
    if mlo < 0:
        return Value(None, "derived", f"already forward of the limit at {lo:g} lb")
    if mhi >= 0:
        return Value(None, "derived", f"no crossing up to {hi:g} lb")
    a, b = lo, hi
    for _ in range(60):
        mid = (a + b) / 2
        a, b = (mid, b) if margin(mid) >= 0 else (a, mid)
    return Value((a + b) / 2, "derived", "solved on the solo loading score, mission fuel and baggage")


def solo_table(
    option_id: str,
    extras: list[dict] | None = None,
    mission: dict | None = None,
    plants: dict | None = None,
) -> list[dict]:
    """The public range: pilot 120 to 220 lb in 10 lb steps plus the book's light (135) and heavy (210) pilot samples."""
    mission = _public(mission)
    samples = load_ledger()["samples"]
    lbs = sorted({*range(120, 221, 10), samples["light_pilot"]["items"]["pilot"], samples["heavy_pilot"]["items"]["pilot"]})
    rows = []
    for lb in lbs:
        s = score_pilot(option_id, lb, mission=mission, plants=plants, extras=extras)
        rows.append({"pilot_lb": lb, "takeoff_cg": s.takeoff_cg.v, "landing_cg": s.landing_cg.v,
                     "fwd_margin_in": s.fwd_margin_in.v, "in_envelope": s.in_envelope})
    return rows


def _row(s: LoadingScore) -> dict:
    return {"takeoff_cg": s.takeoff_cg.v, "landing_cg": s.landing_cg.v, "fwd_margin_in": s.fwd_margin_in.v,
            "in_envelope": s.in_envelope, "flag": s.worst_flag}


def score_pilots(
    option_id: str,
    extras: list[dict] | None = None,
    plants: dict | None = None,
    private_dir: Path | None = None,
) -> list[dict]:
    """Private check: each `pilots: [{label, lb}]` entry of $HANGAR_PRIVATE_DIR/mission.yaml, alone and two up with the next listed pilot.

    Returns [] when the private file lists no pilots. Never read by anything that writes tracked files."""
    priv = private_dir if private_dir is not None else os.environ.get("HANGAR_PRIVATE_DIR")
    if not priv:
        return []
    try:
        mission = load_mission(Path(priv))
    except Exception:  # an unreadable private file means no pilots; its text (owner weights) is never echoed
        return []
    pilots = []
    seen: dict[str, int] = {}
    for i, p in enumerate(mission.get("pilots") or []):
        lb = p.get("lb") if isinstance(p, dict) else None
        if isinstance(lb, bool) or not isinstance(lb, (int, float)) or not (30.0 <= float(lb) <= 500.0):
            continue  # also rejects NaN and inf, which fail the range test
        label = str(p.get("label", f"pilot {i + 1}"))
        seen[label] = seen.get(label, 0) + 1
        pilots.append({"label": label if seen[label] == 1 else f"{label} ({seen[label]})", "lb": float(lb)})
    out = []
    for i, p in enumerate(pilots):
        solo = score_pilot(option_id, p["lb"], mission=mission, plants=plants, extras=extras)
        other = pilots[(i + 1) % len(pilots)] if len(pilots) > 1 else None
        two = score_pilot(option_id, p["lb"], other["lb"], mission=mission, plants=plants, extras=extras) if other else None
        out.append({"label": str(p.get("label", f"pilot {i + 1}")), "solo": _row(solo),
                    "two_up_with": str(other.get("label")) if other else None, "two_up": _row(two) if two else None})
    return out


def apply_effect(effect: dict | None, plants: dict | None = None) -> tuple[str, list[dict], dict]:
    """A record option's machine-readable `effect` -> (engine option id, extras, plants).

    effect keys: engine (default the 912 iS), extras (weights added or moved), engine_arm_shift_in (engine CG arm moved aft)."""
    effect = effect or {}
    engine = effect.get("engine", "rotax-912is")
    if plants is None:
        with open(_DATA / "powerplants.yaml", "r") as f:
            plants = yaml.safe_load(f)
    shift = effect.get("engine_arm_shift_in")
    if shift:
        import copy

        plants = copy.deepcopy(plants)
        arm = plants[engine]["cg_arm_in"]
        plants[engine]["cg_arm_in"] = {"v": arm["v"] + shift, "flag": "derived", "note": f"engine installed CG moved {shift:.2f} in aft"}
    return engine, list(effect.get("extras") or []), plants


def solo_range_text(effect: dict | None) -> str:
    """The sentence the record states for a fix: crossing weight at the forward limit and landing margins across the public range."""
    engine, extras, plants = apply_effect(effect)
    fwd = load_ledger()["envelope"]["fwd_fs"]
    c = solo_crossing_weight(engine, extras=extras, plants=plants)
    rows = {r["pilot_lb"]: r for r in solo_table(engine, extras=extras, plants=plants)}
    pts = ", ".join(
        f"{lb} lb {rows[lb]['fwd_margin_in']:+.1f} in" if rows[lb]["fwd_margin_in"] is not None else f"{lb} lb unknown"
        for lb in (120, 160, 200, 220)
    )
    if c.v is not None:
        head = f"solo pilot weight at the {fwd} in forward limit: {c.v:.0f} lb"
    elif "no crossing" in c.note:
        head = f"solo pilot weight at the {fwd} in forward limit: none in the 120 to 220 lb range (no crossing up to 400 lb)"
    else:
        head = f"solo pilot weight at the {fwd} in forward limit: unknown ({c.note})"
    return (f"Solo, rear seat empty, mission fuel and baggage, reserve only at landing; {head}. "
            f"Landing margin at {pts}. Public weight range, no owner weights")


def ballast_for_margin(
    option_id: str,
    loading_id: str,
    arm_in: float,
    margin_in: float,
    mission: dict | None = None,
    plants: dict | None = None,
) -> Value:
    """Ballast (lb) at `arm_in` that brings the forward margin of a loading up to `margin_in`; 0 when it already holds.

    Solved numerically on score_loading (the margin rises monotonically with aft ballast). Unknown inputs give an
    unknown Value; the flag is derived because the ballast arm is a choice, not a measurement."""
    base = score_loading(option_id, loading_id, mission, plants)
    if base.fwd_margin_in.v is None:
        return Value(None, "unknown", "inputs unknown")
    if base.fwd_margin_in.v >= margin_in:
        return Value(0.0, "derived", "margin already holds")

    def margin(b: float) -> float:
        ex = [{"name": "ballast", "weight_lb": b, "arm_in": arm_in, "flag": "derived"}]
        return score_loading(option_id, loading_id, mission, plants, extras=ex).fwd_margin_in.v

    lo, hi = 0.0, 1.0
    while margin(hi) < margin_in:
        hi *= 2
        if hi > 2000:
            return Value(None, "unknown", "no ballast at this arm reaches the margin")
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if margin(mid) < margin_in else (lo, mid)
    return Value(hi, "derived", f"solved on the loading score, ballast arm {arm_in} in")


def write_scores(root: Path) -> int:
    with open(_DATA / "powerplants.yaml", "r") as f:
        plants = yaml.safe_load(f)
    n = 0
    for path in sorted(Path(root).glob("*/decisions/*.yaml")):
        rec = yaml.safe_load(path.read_text())
        if "mission_score" not in rec:
            continue
        for opt in rec.get("options") or []:
            if isinstance(opt, dict) and isinstance(opt.get("effect"), dict):
                for fact in opt.get("facts") or []:
                    if isinstance(fact, dict) and fact.get("computed") == "solo-range":
                        fact["text"] = solo_range_text(opt["effect"])
        scoring = rec.get("scoring")
        if isinstance(scoring, dict) and scoring.get("kind") == "loadings":
            rec["mission_score"] = {
                eng: {
                    ld: dataclasses.asdict(score_loading(eng, ld, load_mission(None), plants))
                    for ld in load_loadings()
                }
                for eng in scoring.get("engines", [])
            }
            path.write_text(dump_record(rec))
            n += 1
            continue
        ids = {o["id"] for o in rec.get("options", []) if isinstance(o, dict)}
        if not (ids & set(plants)):
            continue  # no engine options to score (for example the propeller record)
        # write_scores must NOT use private dir: pass mission=load_mission(None)
        rec["mission_score"] = {
            opt: dataclasses.asdict(score(opt, load_mission(None), plants)) for opt in plants if opt in ids
        }
        path.write_text(dump_record(rec))
        n += 1
    return n

def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m hangar.mission")
    ap.add_argument("--write-scores", action="store_true", help="recompute mission_score in the decision records")
    ap.add_argument("--root", type=Path, default=_DATA.parent, help="records root (default data/hangar)")
    args = ap.parse_args(argv)
    if not args.write_scores:
        ap.error("nothing to do; pass --write-scores")
    print(f"scores written for {write_scores(args.root)} record(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
