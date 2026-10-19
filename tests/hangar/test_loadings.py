"""Loadings scored from the book's own sample rows (Hangar follow-up: cg-ballast record)."""

from __future__ import annotations

import pytest

from core.ledger import load_ledger
from hangar import mission
from hangar.mission import LoadingScore, Value, load_loadings, score_loading


def V(v, flag="sourced", note=""):
    return {"v": v, "flag": flag, "note": note}


def plant(lb=166.2, arm=141.05, ff=4.3):
    return {"x": {"installed_lb": V(lb), "cg_arm_in": V(arm, "derived", "assumed same installed CG as the book engine"),
                  "cruise_ff_gph": V(ff)}}


MISSION = {"leg_nm": 300, "reserve_min": 30, "occupants_lb": [155, 155], "bags_lb": 15,
           "cruise_ktas": V(150), "fuel_capacity_gal": V(52), "fuel_density_lb_per_gal": V(6.0)}


def test_loadings_come_from_the_ledger_samples():
    L = load_loadings()
    s = load_ledger()["samples"]
    assert set(L) >= {"light_solo", "heavy_solo", "heavy_two"}
    assert L["light_solo"]["items"] == s["light_pilot"]["items"]
    assert L["heavy_two"]["items"] == s["heavy_pilot"]["items"]
    assert L["heavy_solo"]["items"]["pilot"] == s["heavy_pilot"]["items"]["pilot"]
    assert "passenger" not in L["heavy_solo"]["items"] and "baggage" not in L["heavy_solo"]["items"]
    assert L["heavy_solo"]["flag"] == "derived" and L["light_solo"]["flag"] == "sourced"


def test_exact_arithmetic_with_injected_plant():
    s = score_loading("x", "heavy_solo", MISSION, plant())
    assert isinstance(s, LoadingScore)
    led = load_ledger()
    it = load_loadings()["heavy_solo"]["items"]
    empty_w = 730 - 243 + 166.2
    empty_m = 730 * 111.7 - 243 * 141.05 + 166.2 * 141.05
    arms = {k: led["loads"][k]["arm_in"] for k in ("oil", "fuel", "pilot")}
    tw = empty_w + sum(it.values())
    tm = empty_m + sum(it[k] * arms[k] for k in it)
    assert s.takeoff_lb.v == pytest.approx(tw)
    assert s.takeoff_cg.v == pytest.approx(tm / tw)
    reserve = 4.3 * 0.5 * 6.0  # 30 min at the option's flow and the mission's density
    lw = tw - (it["fuel"] - reserve)
    lm = tm - (it["fuel"] - reserve) * arms["fuel"]
    assert s.landing_lb.v == pytest.approx(lw)
    assert s.landing_cg.v == pytest.approx(lm / lw)
    fwd = led["envelope"]["fwd_fs"]
    assert s.fwd_margin_in.v == pytest.approx(min(tm / tw, lm / lw) - fwd)
    assert s.in_envelope is (s.fwd_margin_in.v >= 0 and max(tm / tw, lm / lw) <= led["envelope"]["aft_fs"] and lw <= led["envelope"]["max_lb"])


def test_book_engine_stays_inside_for_every_loading():
    for name in ("light_solo", "heavy_solo", "heavy_two"):
        s = score_loading("o235-book", name)
        assert s.in_envelope is not None
        assert s.fwd_margin_in.v is not None


def test_912_heavy_solo_goes_forward_of_the_limit_and_two_adults_stay_in():
    solo = score_loading("rotax-912is", "heavy_solo")
    two = score_loading("rotax-912is", "heavy_two")
    assert solo.in_envelope is False and solo.fwd_margin_in.v < 0
    assert two.in_envelope is True and 0 <= two.fwd_margin_in.v < 3
    assert solo.worst_flag in ("derived", "unknown") and any("coolant" in a.lower() for a in solo.assumptions)


def test_unknown_inputs_propagate():
    s = score_loading("x", "heavy_solo", MISSION, {"x": {**plant()["x"], "cruise_ff_gph": V(None, "unknown")}})
    assert s.landing_cg.v is None and s.landing_cg.flag == "unknown" and s.in_envelope is None
    assert s.takeoff_cg.v is not None


def test_unknown_loading_raises():
    with pytest.raises(KeyError):
        score_loading("x", "nope", MISSION, plant())


def test_write_scores_scores_loadings_when_the_record_asks(tmp_path):
    """A record with `scoring: {kind: loadings, engines: [...]}` gets loading scores, generated and idempotent."""
    import copy, dataclasses, shutil
    import yaml
    from hangar.mission import write_scores
    from hangar.records import DATA_ROOT, dump_record, load_records, validate_all

    root = tmp_path / "hangar"
    shutil.copytree(DATA_ROOT, root)
    p = root / "mod-ez" / "decisions" / "propeller.yaml"
    d = yaml.safe_load(p.read_text())
    d["scoring"] = {"kind": "loadings", "engines": ["o235-book", "rotax-912is"]}
    p.write_text(dump_record(d))
    write_scores(root)
    got = yaml.safe_load(p.read_text())["mission_score"]
    assert list(got) == ["o235-book", "rotax-912is"]
    assert set(got["rotax-912is"]) == {"light_solo", "heavy_solo", "heavy_two"}
    want = dataclasses.asdict(score_loading("rotax-912is", "heavy_solo"))
    assert got["rotax-912is"]["heavy_solo"] == yaml.safe_load(yaml.safe_dump(want))
    before = p.read_text()
    write_scores(root)
    assert p.read_text() == before
    assert validate_all(root) == []
