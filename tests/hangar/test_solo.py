"""Solo and two-up pilot-weight scoring: a public range and a private per-owner check (cg-ballast addendum)."""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest
import yaml

from core.ledger import load_ledger
from hangar import mission
from hangar.mission import score, score_pilot, solo_crossing_weight, solo_table

E = "rotax-912is"
LED = load_ledger()


def V(v, flag="sourced", note=""):
    return {"v": v, "flag": flag, "note": note}


MISSION = {"leg_nm": 300, "reserve_min": 30, "occupants_lb": [155, 155], "bags_lb": 15,
           "cruise_ktas": V(150), "fuel_capacity_gal": V(52), "fuel_density_lb_per_gal": V(6.0)}
PLANT = {"x": {"installed_lb": V(166.2), "cg_arm_in": V(141.05, "derived", "assumed same installed CG as the book engine"),
               "cruise_ff_gph": V(4.3)}}


def test_solo_arithmetic_uses_mission_fuel_bags_and_reserve():
    s = score_pilot("x", 180.0, mission=MISSION, plants=PLANT)  # front seat only, rear empty
    arms = {k: LED["loads"][k]["arm_in"] for k in ("oil", "fuel", "pilot", "baggage")}
    fuel = 4.3 * 2.5 * 6.0
    empty_w = 730 - 243 + 166.2
    empty_m = 730 * 111.7 - 243 * 141.05 + 166.2 * 141.05
    items = {"oil": 8.0, "fuel": fuel, "pilot": 180.0, "baggage": 15.0}
    tw = empty_w + sum(items.values())
    tm = empty_m + sum(items[k] * arms[k] for k in items)
    reserve = 4.3 * 0.5 * 6.0
    lw = tw - (fuel - reserve)
    lm = tm - (fuel - reserve) * arms["fuel"]
    assert s.takeoff_lb.v == pytest.approx(tw) and s.takeoff_cg.v == pytest.approx(tm / tw)
    assert s.landing_lb.v == pytest.approx(lw) and s.landing_cg.v == pytest.approx(lm / lw)
    assert s.fwd_margin_in.v == pytest.approx(min(tm / tw, lm / lw) - LED["envelope"]["fwd_fs"])
    assert s.worst_flag in ("derived", "unknown")


def test_two_up_adds_a_rear_passenger():
    solo = score_pilot("x", 180.0, mission=MISSION, plants=PLANT)
    two = score_pilot("x", 180.0, passenger_lb=150.0, mission=MISSION, plants=PLANT)
    assert two.takeoff_lb.v == pytest.approx(solo.takeoff_lb.v + 150.0)
    assert two.landing_cg.v > solo.landing_cg.v  # a rear seat moves the CG aft


def test_heavier_pilot_is_further_forward():
    w = [score_pilot(E, lb).fwd_margin_in.v for lb in (120, 150, 180, 210)]
    assert w == sorted(w, reverse=True)


def test_crossing_weight_solves_the_limit():
    c = solo_crossing_weight(E)
    assert c.v is not None and 150 < c.v < 260
    at = score_pilot(E, c.v)
    assert at.fwd_margin_in.v == pytest.approx(0.0, abs=0.01)
    assert score_pilot(E, c.v - 5).in_envelope is True and score_pilot(E, c.v + 5).in_envelope is False


def test_crossing_weight_rises_with_aft_ballast():
    ex = [{"name": "ballast", "weight_lb": 14.6, "arm_in": 141.05, "flag": "derived"}]
    assert solo_crossing_weight(E, extras=ex).v > solo_crossing_weight(E).v + 20


def test_book_engine_does_not_cross_in_the_public_range():
    c = solo_crossing_weight("o235-book")
    assert c.v is None or c.v > 220


def test_table_is_the_public_range_plus_the_book_samples():
    rows = solo_table(E)
    lbs = [r["pilot_lb"] for r in rows]
    assert lbs == sorted(set(lbs))
    assert set(range(120, 221, 10)) <= set(lbs) and {135, 210} <= set(lbs)
    assert all({"takeoff_cg", "landing_cg", "fwd_margin_in", "in_envelope"} <= set(r) for r in rows)
    assert rows[0]["fwd_margin_in"] > rows[-1]["fwd_margin_in"]


def test_unknown_inputs_make_unknown_not_a_number():
    p = {"x": {**PLANT["x"], "cruise_ff_gph": V(None, "unknown")}}
    s = score_pilot("x", 180.0, mission=MISSION, plants=p)
    assert s.landing_cg.v is None and s.in_envelope is None
    assert solo_crossing_weight("x", mission=MISSION, plants=p).v is None


def test_private_pilots_are_scored_per_label_and_never_in_git(tmp_path, monkeypatch):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"pilots": [{"label": "A", "lb": 170}, {"label": "B", "lb": 140}]}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(tmp_path))
    rows = mission.score_pilots(E)
    assert [r["label"] for r in rows] == ["A", "B"]
    a = score_pilot(E, 170.0)
    assert rows[0]["solo"]["fwd_margin_in"] == pytest.approx(a.fwd_margin_in.v)
    two = score_pilot(E, 170.0, passenger_lb=140.0)  # A in front, B behind
    assert rows[0]["two_up_with"] == "B" and rows[0]["two_up"]["fwd_margin_in"] == pytest.approx(two.fwd_margin_in.v)
    monkeypatch.delenv("HANGAR_PRIVATE_DIR")
    assert mission.score_pilots(E) == []
    # the public mission file never carries pilots
    assert "pilots" not in yaml.safe_load(open("data/hangar/mod-ez/mission.yaml"))
    # and write_scores ignores them
    assert "pilots" not in json.dumps(mission.load_mission(None))


def test_api_pilots_serves_private_margins_only_when_configured(tmp_path, monkeypatch):
    from hangar.briefing_server import make_server

    root = tmp_path / "records"
    d = root / "mod-ez" / "decisions"
    d.mkdir(parents=True)
    import shutil
    from hangar.records import DATA_ROOT
    shutil.copy(DATA_ROOT / "mod-ez" / "decisions" / "cg-ballast.yaml", d / "cg-ballast.yaml")
    shutil.copy(DATA_ROOT / "mod-ez" / "decisions" / "powerplant-fuel-resin.yaml", d / "powerplant-fuel-resin.yaml")
    shutil.copy(DATA_ROOT / "mod-ez" / "decisions" / "propeller.yaml", d / "propeller.yaml")
    site = tmp_path / "site"; site.mkdir()
    priv = tmp_path / "private"; priv.mkdir()
    (priv / "mission.yaml").write_text(yaml.safe_dump({"pilots": [{"label": "Owner one", "lb": 175}]}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(priv))
    srv = make_server(site, 0, priv, root)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    try:
        body = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/pilots/cg-ballast", timeout=20).read())
        assert body["pilots"][0]["label"] == "Owner one"
        opts = {o["option"]: o for o in body["pilots"][0]["options"]}
        assert {"book-engine-cg", "loading-limit", "fixed-aft-ballast", "battery-aft", "engine-arm-aft"} <= set(opts)
        assert opts["fixed-aft-ballast"]["solo"]["fwd_margin_in"] > opts["loading-limit"]["solo"]["fwd_margin_in"]
        recs = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/records", timeout=20).read().decode()
        assert "Owner one" not in recs and "175" not in json.dumps(json.loads(recs)["cg-ballast"]["options"])
        (priv / "mission.yaml").write_text("{}")
        body = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/pilots/cg-ballast", timeout=20).read())
        assert body["pilots"] == []
    finally:
        srv.shutdown(); srv.server_close()


def test_tracked_record_has_the_range_result_and_no_owner_weights():
    from hangar.records import load_records

    r = load_records()["cg-ballast"]
    blob = yaml.safe_dump({"o": r.options, "u": r.unknowns})
    for opt in ("loading-limit", "fixed-aft-ballast", "battery-aft", "engine-arm-aft"):
        o = next(x for x in r.options if x["id"] == opt)
        t = " ".join(f["text"] for f in o["facts"])
        assert "solo pilot weight" in t and "lb" in t, opt
        assert "effect" in o  # machine-readable effect used by /api/pilots
    t = " ".join(f["text"] for f in next(x for x in r.options if x["id"] == "loading-limit")["facts"])
    c = solo_crossing_weight(E)
    assert f"{c.v:.0f} lb" in t
    assert "Owner" not in blob
