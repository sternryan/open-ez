"""The cg-ballast record's numbers are computed from the loading calculator, not typed (Hangar follow-up)."""

from __future__ import annotations

import copy

import yaml

from core.ledger import load_ledger
from hangar.mission import ballast_for_margin, score_loading
from hangar.records import load_records, validate_all

E = "rotax-912is"


def rec():
    return load_records()["cg-ballast"]


def text(opt_id: str) -> str:
    o = next(o for o in rec().options if o["id"] == opt_id)
    return " ".join(f["text"] for f in o["facts"])


def test_record_is_valid_open_and_coupled():
    r = rec()
    assert validate_all() == []
    assert r.status == "open" and r.decision is None and r.positions == []
    assert set(r.coupled_with) == {"powerplant-fuel-resin", "propeller"}
    assert {"book-engine-cg"} <= {o["id"] for o in r.options if o["kind"] == "book"}
    assert r.replaces and all(i.startswith(("f22.", "f23.")) for i in r.replaces)


def test_baseline_and_912_margins_are_the_calculator_output():
    for eng, opt in (("o235-book", "book-engine-cg"), (E, "loading-limit")):
        t = text(opt)
        for ld in ("heavy_solo", "heavy_two"):
            assert f"{score_loading(eng, ld).fwd_margin_in.v:+.1f} in" in t, (opt, ld, t)
    assert f"{score_loading(E, 'heavy_solo').landing_cg.v:.1f}" in text("loading-limit")


def test_912_heavy_solo_is_outside_and_the_record_says_so():
    s = score_loading(E, "heavy_solo")
    assert s.fwd_margin_in.v < 0
    assert "forward of the" in text("loading-limit")


def test_ballast_battery_and_engine_shift_numbers():
    b = ballast_for_margin(E, "heavy_solo", 141.05, 0.5).v
    assert f"{b:.1f} lb" in text("fixed-aft-ballast")
    batt = [{"name": "o", "weight_lb": -19.0, "arm_in": 11.0, "flag": "derived"},
            {"name": "n", "weight_lb": 19.0, "arm_in": 141.05, "flag": "derived"}]
    assert f"{score_loading(E, 'heavy_solo', extras=batt).fwd_margin_in.v:+.1f} in" in text("battery-aft")
    plants = yaml.safe_load(open("data/hangar/mod-ez/powerplants.yaml"))
    import re
    shift = float(re.search(r"CG ([0-9.]+) in aft", text("engine-arm-aft")).group(1))
    p = copy.deepcopy(plants)
    p[E]["cg_arm_in"] = {"v": 141.05 + shift, "flag": "derived", "note": "x"}
    assert abs(score_loading(E, "heavy_solo", plants=p).fwd_margin_in.v - 0.5) < 0.06  # shift is printed to 0.1 in


def test_battery_row_matches_the_ledger():
    # the record moves the ledger's own derived battery row
    rows = yaml.safe_load(open("data/mass_ledger.yaml"))
    txt = open("data/mass_ledger.yaml").read()
    assert "name: battery_25ah" in txt and "weight_lb: 19.0" in txt and "arm_fs: 11.0" in txt
    assert load_ledger()["loads"]["fuel"]["arm_in"] == 104.5


def test_unknowns_stay_unknown_and_no_private_numbers():
    r = rec()
    assert any("coolant" in u["text"].lower() for u in r.unknowns)
    # only the book's own sample weights are used as pilot weights: the record carries no occupant list
    assert "occupants" not in yaml.safe_dump(r.options) and "occupants" not in yaml.safe_dump(r.unknowns)
    for fixed in ("book-engine-cg", "loading-limit"):
        assert "book's own sample" in text(fixed) or "sample" in text(fixed)


def test_each_moved_weight_option_states_its_aft_check():
    for opt in ("fixed-aft-ballast", "battery-aft", "engine-arm-aft"):
        assert "Aft check" in text(opt) and "aft limit" in text(opt), opt
    # the battery move is the one that can leave the envelope on the light pilot case
    batt = [{"name": "o", "weight_lb": -19.0, "arm_in": 11.0, "flag": "derived"},
            {"name": "n", "weight_lb": 19.0, "arm_in": 141.05, "flag": "derived"}]
    s = score_loading(E, "light_solo", extras=batt)
    inside = s.in_envelope
    assert ("OUTSIDE" in text("battery-aft")) == (inside is False)
