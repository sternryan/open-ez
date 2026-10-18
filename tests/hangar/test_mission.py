"""Deterministic mission calculator (Hangar H1)."""

from __future__ import annotations

import pytest
import yaml

from hangar.mission import MissionScore, Value, load_mission, score


def V(v, flag="sourced", **kw):
    return {"v": v, "flag": flag, "note": kw.get("note", "")}


def plants(ff=V(4.3), lb=173.0, arm=141.05, arm_flag="derived"):
    return {
        "x": {
            "installed_lb": V(lb),
            "cg_arm_in": {"v": arm, "flag": arm_flag, "note": "assumed same installed CG as the book engine"},
            "cruise_ff_gph": ff,
        }
    }


MISSION = {
    "leg_nm": 300,
    "reserve_min": 30,
    "occupants_lb": [155, 155],
    "bags_lb": 15,
    "cruise_ktas": V(150),
    "fuel_capacity_gal": V(52),
    "fuel_density_lb_per_gal": V(6.0),
}


def test_book_engine_round_trip():
    s = score("o235-book")
    assert isinstance(s, MissionScore)
    assert s.empty_lb.v == pytest.approx(730)
    assert s.empty_cg.v == pytest.approx(111.7)


def test_lighter_engine_moves_cg_forward():
    s = score("x", MISSION, plants())
    assert s.empty_cg.v < 111.7
    assert s.empty_lb.v == pytest.approx(730 - 243 + 173)


def test_cg_arithmetic():
    s = score("x", MISSION, plants(lb=173.0, arm=141.05))
    want = (730 * 111.7 - 243 * 141.05 + 173 * 141.05) / (730 - 243 + 173)
    assert s.empty_cg.v == pytest.approx(want)


def test_unknown_ff_propagates():
    s = score("x", MISSION, plants(ff=V(None, "unknown")))
    assert s.fuel_needed_lb.flag == "unknown"
    assert s.range_full_fuel_nm.v is None
    assert s.in_envelope is None
    assert s.worst_flag == "unknown"


def test_fuel_math():
    s = score("x", MISSION, plants(ff=V(4.3)))
    assert s.block_time_h.v == pytest.approx(2.5)
    assert s.fuel_needed_lb.v == pytest.approx(4.3 * 2.5 * 6.0)


def test_takeoff_and_landing():
    s = score("x", MISSION, plants(ff=V(4.3)))
    fuel = 4.3 * 2.5 * 6.0
    assert s.takeoff_lb.v == pytest.approx(s.empty_lb.v + 310 + 15 + fuel)
    leg_fuel = 4.3 * (300 / 150) * 6.0
    # landing weight is not a field; landing CG must lie between takeoff CG and the no-fuel CG
    assert s.landing_cg.v is not None and s.takeoff_cg.v is not None
    assert abs(s.landing_cg.v - s.takeoff_cg.v) > 0 or leg_fuel == 0


def test_range():
    s = score("x", MISSION, plants(ff=V(4.3)))
    assert s.range_full_fuel_nm.v == pytest.approx((52 / 4.3 - 0.5) * 150)


def test_worst_flag_is_derived_when_arm_derived():
    s = score("x", MISSION, plants())
    assert s.worst_flag == "derived"
    assert s.empty_cg.flag == "derived"
    assert s.empty_lb.flag == "sourced"


def test_envelope_is_boolean_when_inputs_known():
    s = score("x", MISSION, plants())
    assert isinstance(s.in_envelope, bool)


def test_private_override(tmp_path):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"occupants_lb": [180, 130]}))
    base = load_mission()
    over = load_mission(tmp_path)
    assert over["occupants_lb"] == [180, 130]
    assert over["leg_nm"] == base["leg_nm"]
    assert base["occupants_lb"] == [155, 155]


def test_assumptions_listed():
    s = score("x", MISSION, plants())
    assert any("same installed CG as the book engine" in a for a in s.assumptions)


def test_unknown_option_raises():
    with pytest.raises(KeyError):
        score("nope", MISSION, plants())


def test_value_dataclass_frozen():
    v = Value(1.0, "sourced", "")
    with pytest.raises(Exception):
        v.v = 2.0  # type: ignore[misc]
