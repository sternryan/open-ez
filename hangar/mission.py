from dataclasses import dataclass
from pathlib import Path
from typing import Any
import dataclasses
import yaml
import os
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
            data.update(yaml.safe_load(f))
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

def write_scores(root: Path) -> int:
    with open(_DATA / "powerplants.yaml", "r") as f:
        plants = yaml.safe_load(f)
    n = 0
    for path in sorted(Path(root).glob("*/decisions/*.yaml")):
        rec = yaml.safe_load(path.read_text())
        if "mission_score" not in rec:
            continue
        ids = {o["id"] for o in rec.get("options", [])}
        # write_scores must NOT use private dir: pass mission=load_mission(None)
        rec["mission_score"] = {
            opt: dataclasses.asdict(score(opt, load_mission(None), plants)) for opt in plants if opt in ids
        }
        path.write_text(yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=120))
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
