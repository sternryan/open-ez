"""Weights moved or added to a loading: ballast, a moved battery, a shifted engine arm (cg-ballast record)."""

from __future__ import annotations

import pytest

from core.ledger import load_ledger
from hangar.mission import ballast_for_margin, score_loading

FWD = load_ledger()["envelope"]["fwd_fs"]


def test_extras_shift_weight_and_cg_exactly():
    base = score_loading("rotax-912is", "heavy_solo")
    s = score_loading("rotax-912is", "heavy_solo", extras=[{"name": "ballast", "weight_lb": 5.0, "arm_in": 141.05, "flag": "derived"}])
    for a, b in ((base.takeoff_lb, s.takeoff_lb), (base.landing_lb, s.landing_lb)):
        assert b.v == pytest.approx(a.v + 5.0)
    assert s.landing_cg.v == pytest.approx((base.landing_lb.v * base.landing_cg.v + 5.0 * 141.05) / (base.landing_lb.v + 5.0))
    assert s.fwd_margin_in.v > base.fwd_margin_in.v
    assert any("ballast" in a for a in s.assumptions)


def test_a_battery_moved_aft_is_a_pair_of_extras():
    base = score_loading("rotax-912is", "heavy_solo")
    moved = score_loading("rotax-912is", "heavy_solo", extras=[
        {"name": "battery out of the nose", "weight_lb": -19.0, "arm_in": 11.0, "flag": "derived"},
        {"name": "battery aft", "weight_lb": 19.0, "arm_in": 141.05, "flag": "derived"},
    ])
    assert moved.landing_lb.v == pytest.approx(base.landing_lb.v)
    assert moved.landing_cg.v == pytest.approx(base.landing_cg.v + 19.0 * (141.05 - 11.0) / base.landing_lb.v)
    assert moved.worst_flag in ("derived", "unknown")


def test_extras_flag_propagates_and_unknown_wins():
    s = score_loading("o235-book", "heavy_solo", extras=[{"name": "x", "weight_lb": 1.0, "arm_in": 100.0, "flag": "derived"}])
    assert s.worst_flag in ("derived", "unknown")
    t = score_loading("rotax-912is", "heavy_solo", extras=[{"name": "y", "weight_lb": None, "arm_in": 100.0, "flag": "unknown"}])
    assert t.landing_cg.v is None and t.in_envelope is None


def test_ballast_for_margin_hits_the_target():
    b = ballast_for_margin("rotax-912is", "heavy_solo", arm_in=141.05, margin_in=0.5)
    assert 0 < b.v < 30 and b.flag in ("derived", "unknown")
    s = score_loading("rotax-912is", "heavy_solo", extras=[{"name": "ballast", "weight_lb": b.v, "arm_in": 141.05, "flag": "derived"}])
    assert s.fwd_margin_in.v == pytest.approx(0.5, abs=0.01)
    assert s.in_envelope is True


def test_ballast_is_zero_when_the_margin_already_holds():
    assert ballast_for_margin("o235-book", "heavy_solo", arm_in=141.05, margin_in=0.5).v == 0.0


def test_ballast_unknown_when_inputs_unknown():
    plants = {"x": {"installed_lb": {"v": None, "flag": "unknown", "note": ""},
                    "cg_arm_in": {"v": 141.05, "flag": "derived", "note": ""},
                    "cruise_ff_gph": {"v": 4.3, "flag": "sourced", "note": ""}}}
    assert ballast_for_margin("x", "heavy_solo", arm_in=141.05, margin_in=0.5, plants=plants).v is None


def test_engine_arm_override_moves_the_margin_through_plants():
    from hangar.mission import load_mission
    import yaml, pathlib
    plants = yaml.safe_load((pathlib.Path("data/hangar/mod-ez/powerplants.yaml")).read_text())
    base = score_loading("rotax-912is", "heavy_solo")
    plants["rotax-912is"]["cg_arm_in"] = {"v": 142.05, "flag": "derived", "note": "engine one inch aft"}
    aft = score_loading("rotax-912is", "heavy_solo", plants=plants)
    assert aft.fwd_margin_in.v > base.fwd_margin_in.v
