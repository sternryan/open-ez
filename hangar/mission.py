from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from core.ledger import load_ledger, in_envelope

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
        if v is None and data.get("flag") == "unknown":
            return Value(None, "unknown", data.get("note", ""))
        return Value(v, data.get("flag", "sourced"), data.get("note", ""))
    return Value(data, "sourced", "")

def _combine_values(v1: Value, v2: Value) -> Value:
    if v1.flag == "unknown" or v2.flag == "unknown":
        return Value(None, "unknown", "")
    new_flag = _get_worst_flag([v1.flag, v2.flag])
    new_note = (v1.note + " " + v2.note).strip()
    return Value(v1.v if v1.v is not None else v2.v, new_flag, new_note)

def load_mission(private_dir: Path | None = None) -> dict:
    path = Path("data/hangar/mod-ez/mission.yaml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if private_dir and (private_dir / "mission.yaml").exists():
        with open(private_dir / "mission.yaml", "r") as f:
            data.update(yaml.safe_load(f))
    return data

def score(option_id: str, mission: dict = None, plants: dict = None) -> MissionScore:
    if mission is None:
        mission = load_mission()
    if plants is None:
        with open("data/hangar/mod-ez/powerplants.yaml", "r") as f:
            plants = yaml.safe_load(f)

    # Convert all Value-shaped dicts to Value objects
    m = {}
    for k, val in mission.items():
        m[k] = _to_value(val) if isinstance(val, dict) else val
    
    p_raw = plants[option_id]
    p = {}
    for k, val in p_raw.items():
        p[k] = _to_value(val) if isinstance(val, dict) else val

    ledger = load_ledger()
    env = ledger["envelope"]
    loads = ledger["loads"]

    # Constants/Inputs
    # mission: leg_nm (float), reserve_min (float), occupants_lb [f, r], bags_lb (float), 
    # cruise_ktas (Value), fuel_capacity_gal (Value), fuel_density_lb_per_gal (Value)
    # plants: installed_lb (Value), cg_arm_in (Value), cruise_ff_gph (Value)

    # 1. empty_lb
    inst_lb = p["installed_lb"]
    empty_lb_v = BOOK_WEIGHT_LB - BOOK_WEIGHT_LB + inst_lb.v if inst_lb.v is not None else None
    # Wait, the formula is: empty_lb = 730 - 243 + installed_lb
    empty_lb_val = 730 - 243 + inst_lb.v if inst_lb.v is not None else None
    empty_lb = Value(empty_lb_val, inst_lb.flag)

    # 2. empty_cg
    cg_arm_in = p["cg_arm_in"]
    if inst_lb.v is not None and cg_arm_in.v is not None:
        empty_cg_v = (730 * 111.7 - 243 * BOOK_ARM_IN + inst_lb.v * cg_arm_in.v) / empty_lb_val
        empty_cg = Value(empty_cg_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag]), cg_arm_in.note)
    elif inst_lb.flag == "unknown" or cg_arm_in.flag == "unknown":
        empty_cg = Value(None, "unknown")
    else:
        empty_cg = Value(None, "derived") # Should not happen given logic

    # 3. block_time_h
    # leg_nm (plain), reserve_min (plain), cruise_ktas (Value)
    if m["leg_nm"] is not None and m["reserve_min"] is not None and m["cruise_ktas"].v is not None:
        block_time_v = m["leg_nm"] / m["cruise_ktas"].v + m["reserve_min"] / 60
        block_time = Value(block_time_v, _get_worst_flag([m["cruise_ktas"].flag]))
    else:
        block_time = Value(None, "unknown")

    # 4. fuel_needed_lb
    # cruise_ff_gph (Value), block_time_h (Value), density (Value)
    if p["cruise_ff_gph"].v is not None and block_time.v is not None and m["fuel_density_lb_per_gal"].v is not None:
        fuel_needed_v = p["cruise_ff_gph"].v * block_time.v * m["fuel_density_lb_per_gal"].v
        fuel_needed = Value(fuel_needed_v, _get_worst_flag([p["cruise_ff_gph"].flag, m["cruise_ktas"].flag, m["fuel_density_lb_per_gal"].flag]))
    else:
        fuel_needed = Value(None, "unknown")

    # 5. takeoff_lb and takeoff_cg
    # occupants: [front, rear], bags: bags_lb, fuel: fuel_needed
    # arms: pilot=loads.pilot, rear=loads.passenger, bags=loads.baggage, fuel=loads.fuel
    if empty_lb_val is not None and fuel_needed.v is not None and m["cruise_ktas"].v is not None and m["fuel_density_lb_per_gal"].v is not None:
        takeoff_lb_v = empty_lb_val + sum(m["occupants_lb"]) + m["bags_lb"] + fuel_needed.v
        
        # Moments
        moments = (empty_lb_val * 111.7) # base empty moment
        # Note: the formula for empty_cg uses 730*111.7 - 243*141.05 + inst_lb*cg_arm. 
        # This implies the "730" part is the base moment of the plane without the engine.
        # Let's re-calculate moments from scratch based on the provided formula logic.
        # Base moment (plane - book engine) = 730 * 111.7 - 243 * 141.05
        base_moment = 730 * 111.7 - 243 * BOOK_ARM_IN
        
        moments = base_moment + (inst_lb.v * cg_arm_in.v)
        moments += m["occupants_lb"][0] * loads["pilot"]["arm_in"]
        moments += m["occupants_lb"][1] * loads["passenger"]["arm_in"]
        moments += m["bags_lb"] * loads["baggage"]["arm_in"]
        moments += fuel_needed.v * loads["fuel"]["arm_in"]
        
        takeoff_cg_v = moments / takeoff_lb_v
        takeoff_lb = Value(takeoff_lb_v, _get_worst_flag([inst_lb.flag, m["occupants_lb"][0] != None, m["bags_lb"] != None, fuel_needed.flag])) # simplified
        # Actually, the test expects takeoff_lb to be derived from inputs.
        # The flag of takeoff_lb depends on the flags of its components.
        takeoff_lb = Value(takeoff_lb_v, _get_worst_flag([inst_lb.flag, fuel_needed.flag]))
        takeoff_cg = Value(takeoff_cg_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag, fuel_needed.flag]))
    else:
        takeoff_lb = Value(None, "unknown")
        takeoff_cg = Value(None, "unknown")

    # 6. landing_cg
    if takeoff_lb.v is not None and fuel_needed.v is not None:
        leg_fuel_v = p["cruise_ff_gph"].v * (m["leg_nm"] / m["cruise_ktas"].v) * m["fuel_density_lb_per_gal"].v
        landing_lb_v = takeoff_lb.v - leg_fuel_v
        # landing_cg: same as takeoff but with fuel_needed - leg_fuel
        moments_landing = (moments - leg_fuel_v * loads["fuel"]["arm_in"])
        landing_cg_v = moments_landing / landing_lb_v
        landing_cg = Value(landing_cg_v, _get_worst_flag([inst_lb.flag, cg_arm_in.flag, fuel_needed.flag]))
        landing_lb_v = landing_lb_v # for envelope
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
    if cg_arm_in.flag == "derived" and cg_arm_in.note:
        assumptions.append(cg_arm_in.note)
    # Add other notes if they are derived/unknown
    for val in [m["fuel_density_lb_per_gal"], m["cruise_ktas"], m["fuel_capacity_gal"], p["cruise_ff_gph"]]:
        if isinstance(val, Value) and val.flag != "sourced" and val.note:
            if val.note not in assumptions:
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
