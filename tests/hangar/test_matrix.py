"""Loading matrix: every mass/CG option scored over a fixed public matrix, both CG limits plus gross."""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from hangar import matrix as mx
from hangar import mission
from hangar.mission import apply_effect, score_pilot

E = "rotax-912is"


def V(v, flag="sourced", note=""):
    return {"v": v, "flag": flag, "note": note}


MISSION = {"leg_nm": 300, "reserve_min": 30, "occupants_lb": [155, 155], "bags_lb": 15,
           "cruise_ktas": V(150), "fuel_capacity_gal": V(52), "fuel_density_lb_per_gal": V(5.87)}
PLANT = {"x": {"installed_lb": V(166.2), "cg_arm_in": V(141.05, "derived", "assumed same installed CG"),
               "cruise_ff_gph": V(4.3)}}


def option_effects():
    rec = yaml.safe_load(open("data/hangar/mod-ez/decisions/cg-ballast.yaml"))
    return {o["id"]: o["effect"] for o in rec["options"] if isinstance(o.get("effect"), dict)}


def public(effect):
    return mx.matrix_for_effect(effect)


def cell(m, occ, bag, fuel, state):
    found = [c for c in m["cells"] if c["id"] == f"{occ}|{bag}|{fuel}|{state}"]
    assert len(found) == 1, f"cell {occ}|{bag}|{fuel}|{state}"
    return found[0]


def test_public_matrix_shape_and_ids():
    m = mx.matrix(E)
    # 11 solo pilots (120-220 by 10) + 9 two-up pairs (front, rear in 120/170/220), x 2 bags x 3 fuels x 2 states
    assert m["cell_count"] == len(m["cells"]) == (11 + 9) * 2 * 3 * 2
    ids = {c["id"] for c in m["cells"]}
    assert len(ids) == m["cell_count"]
    assert "solo-120|none|full|takeoff" in ids and "solo-220|light|reserve|landing" in ids
    assert "two-120-220|light|mission|landing" in ids  # front 120, rear 220
    assert m["unknown_cells"] == 0
    for key in ("id", "occupancy", "occupancy_label", "bag", "fuel", "state", "gross_lb", "cg_in", "fwd_margin_in",
                "aft_margin_in", "gross_margin_lb", "ok", "flag", "loading", "bag_label"):
        assert key in m["cells"][0]
    assert set(m["worst"]) == {"fwd", "aft", "gross"} and set(m["crossings"]) == {"fwd", "aft", "gross"}


def test_cell_arithmetic_matches_the_pilot_score():
    # Solo 160 lb, the mission bag (light bag = 15 lb = mission bags_lb), mission fuel: the existing solo score is the oracle.
    m = mx.matrix("x", plants=PLANT, mission=MISSION)
    s = score_pilot("x", 160.0, mission=MISSION, plants=PLANT)
    t = cell(m, "solo-160", "light", "mission", "takeoff")
    l = cell(m, "solo-160", "light", "mission", "landing")
    assert t["cg_in"] == pytest.approx(s.takeoff_cg.v, abs=1e-6)
    assert t["gross_lb"] == pytest.approx(s.takeoff_lb.v, abs=1e-6)
    assert l["cg_in"] == pytest.approx(s.landing_cg.v, abs=1e-6)
    assert l["gross_lb"] == pytest.approx(s.landing_lb.v, abs=1e-6)
    assert t["fwd_margin_in"] == pytest.approx(t["cg_in"] - 97.0)
    assert t["aft_margin_in"] == pytest.approx(103.0 - t["cg_in"])
    assert t["gross_margin_lb"] == pytest.approx(1325 - t["gross_lb"])
    assert t["ok"] is True and t["flag"] in ("derived", "sourced")


def test_fuel_states_and_landing_floor():
    m = mx.matrix("x", plants=PLANT, mission=MISSION)
    leg = 4.3 * (300 / 150) * 5.87
    res = 4.3 * 0.5 * 5.87
    full = 52 * 5.87
    base = cell(m, "solo-160", "none", "reserve", "takeoff")["gross_lb"]
    assert cell(m, "solo-160", "none", "full", "takeoff")["gross_lb"] - base == pytest.approx(full - res)
    assert cell(m, "solo-160", "none", "mission", "takeoff")["gross_lb"] - base == pytest.approx(leg)
    # landing = takeoff minus the leg fuel, floored at the reserve
    assert cell(m, "solo-160", "none", "full", "landing")["gross_lb"] - base == pytest.approx(full - leg - res)
    assert cell(m, "solo-160", "none", "mission", "landing")["gross_lb"] == pytest.approx(base)
    assert cell(m, "solo-160", "none", "reserve", "landing")["gross_lb"] == pytest.approx(base)


# Worst cell per limit per option on the public range, from an independent hand-rolled oracle (margins in inches / lb).
ORACLE = {
    "book-engine-cg": {"fwd": (2.77, "solo-220", "light", "mission", "landing"), "aft": (-1.59, "solo-120", "none", "mission", "landing"),
                       "gross": (-173.24, "two-220-220", "light", "full", "takeoff")},
    "loading-limit": {"fwd": (-0.75, "solo-220", "light", "mission", "landing"), "aft": (0.84, "two-120-220", "none", "full", "takeoff"),
                      "gross": (-96.44, "two-220-220", "light", "full", "takeoff")},
    "fixed-aft-ballast": {"fwd": (-0.04, "solo-220", "light", "mission", "landing"), "aft": (0.41, "two-120-220", "none", "full", "takeoff"),
                          "gross": (-111.03, "two-220-220", "light", "full", "takeoff")},
    "battery-aft": {"fwd": (1.97, "solo-220", "light", "mission", "landing"), "aft": (-1.26, "solo-120", "none", "full", "takeoff"),
                    "gross": (-96.44, "two-220-220", "light", "full", "takeoff")},
    "engine-arm-aft": {"fwd": (-0.05, "solo-220", "light", "mission", "landing"), "aft": (0.35, "two-120-220", "none", "full", "takeoff"),
                       "gross": (-96.44, "two-220-220", "light", "full", "takeoff")},
}
FIELD = {"fwd": "fwd_margin_in", "aft": "aft_margin_in", "gross": "gross_margin_lb"}


@pytest.mark.parametrize("opt", sorted(ORACLE))
@pytest.mark.parametrize("limit", ["fwd", "aft", "gross"])
def test_worst_cell_per_limit(opt, limit):
    m = public(option_effects()[opt])
    w = m["worst"][limit]
    margin, occ, bag, fuel, state = ORACLE[opt][limit]
    assert w[FIELD[limit]] == pytest.approx(margin, abs=0.01)
    assert w["id"] == f"{occ}|{bag}|{fuel}|{state}"
    assert w[FIELD[limit]] == min(c[FIELD[limit]] for c in m["cells"])  # it really is the minimum
    assert isinstance(w["loading"], str) and "lb" in w["loading"]


# Solo pilot weight where each limit starts to bind (worst over bag, fuel and takeoff/landing), oracle scan to 0.1 lb.
CROSS = {
    "book-engine-cg": {"fwd": ("above", 292.1), "aft": ("below", 161.5), "gross": ("above", 266.8)},
    "loading-limit": {"fwd": ("above", 202.2), "aft": ("below", 95.1), "gross": ("above", 343.6)},
    "fixed-aft-ballast": {"fwd": ("above", 219.1), "aft": ("below", 107.7), "gross": ("above", 329.0)},
    "battery-aft": {"fwd": ("above", 267.2), "aft": ("below", 151.3), "gross": ("above", 343.6)},
    "engine-arm-aft": {"fwd": ("above", 218.9), "aft": ("below", 109.5), "gross": ("above", 343.6)},
}


@pytest.mark.parametrize("opt", sorted(CROSS))
def test_crossing_weights(opt):
    m = public(option_effects()[opt])
    for limit, (side, lb) in CROSS[opt].items():
        c = m["crossings"][limit]
        assert set(c) >= {"fails_above_lb", "fails_below_lb", "note"}
        mine, other = (c["fails_above_lb"], c["fails_below_lb"]) if side == "above" else (c["fails_below_lb"], c["fails_above_lb"])
        assert mine == pytest.approx(lb, abs=0.2)
        assert other is None


def test_battery_aft_breaks_the_aft_limit_for_light_pilots():
    """The council's claim: moving the battery aft pushes a light pilot past the 103.0 in aft limit."""
    m = public(option_effects()["battery-aft"])
    assert m["worst"]["aft"]["aft_margin_in"] < 0 and m["worst"]["aft"]["ok"] is False
    assert m["worst"]["aft"]["cg_in"] > 103.0
    assert 120 < m["crossings"]["aft"]["fails_below_lb"] < 160  # a 120 lb pilot breaks it, a 160 lb pilot does not
    # The fixed ballast option and the engine move stay inside the aft limit across the public range.
    for opt in ("fixed-aft-ballast", "engine-arm-aft", "loading-limit"):
        assert public(option_effects()[opt])["worst"]["aft"]["aft_margin_in"] > 0


def test_whole_range_binding_is_reported_not_dropped():
    # book engine: the aft limit already binds for every pilot below 161.5 lb, including at the 50 lb scan floor
    c = public(option_effects()["book-engine-cg"])["crossings"]["aft"]
    assert c["fails_below_lb"] == pytest.approx(161.5, abs=0.2) and isinstance(c["note"], str) and c["note"]


def test_unknown_inputs_make_unknown_cells_and_no_worst():
    plant = copy.deepcopy(PLANT)
    plant["x"]["cg_arm_in"] = V(None, "unknown", "not weighed")
    m = mx.matrix("x", plants=plant, mission=MISSION)
    assert m["unknown_cells"] == m["cell_count"] > 0
    assert all(c["flag"] == "unknown" and c["ok"] is None and c["cg_in"] is None for c in m["cells"])
    assert m["flag"] == "unknown"
    assert all(m["worst"][k] is None for k in ("fwd", "aft", "gross"))
    # an unknown weight leaves the cell unknown too, and an unknown fuel flow blanks every landing and takeoff
    plant2 = copy.deepcopy(PLANT)
    plant2["x"]["cruise_ff_gph"] = V(None, "unknown", "no published flow")
    assert mx.matrix("x", plants=plant2, mission=MISSION)["unknown_cells"] == m["cell_count"]


def test_unknown_extra_weight_is_unknown():
    m = mx.matrix("x", extras=[{"name": "thing", "weight_lb": None, "arm_in": 100.0, "flag": "unknown"}], plants=PLANT, mission=MISSION)
    assert m["unknown_cells"] == m["cell_count"]


def test_flag_is_derived_floor_and_follows_inputs():
    m = mx.matrix("x", plants=PLANT, mission=MISSION)
    assert m["flag"] == "derived"
    assert all(c["flag"] == "derived" for c in m["cells"])


def test_public_matrix_ignores_the_private_directory(tmp_path, monkeypatch):
    base = json.dumps(mx.matrix(E), sort_keys=True)
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"pilots": [{"label": "Pat", "lb": 133}], "bags_lb": 31, "leg_nm": 100}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(tmp_path))
    assert json.dumps(mx.matrix(E), sort_keys=True) == base
