# tests/test_electrical_stations.py
"""Chapter 22 values (electrical): provenance, the nose battery range, the flagged electrical row, and the N26MS ladder reference rows."""

import pytest

from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    WEIGHT_PROVENANCE,
    StructuralWeightParams,
    config,
)
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

BOOK = {
    "elec_book_battery_v": 12.0,
    "elec_book_battery_ah": 25.0,
    "elec_book_shelf_in": (0.6, 0.4),
    "elec_book_nav_strip_in": 22.8,
    "elec_book_comm_strip_in": 20.3,
}

LADDER = {
    "n26ms_empty_1": 693.4,
    "n26ms_empty_2": 698.3,
    "n26ms_empty_3": 713.7,
    "n26ms_empty_4": 761.9,
    "n26ms_empty_5": 777.3,
    "n26ms_empty_6": 815.4,
    "n26ms_empty_7": 860.2,
    "n26ms_empty_8": 883.0,
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_battery_station_is_a_range_not_a_source():
    lo, hi = G.elec_book_battery_fs_range
    assert (lo, hi) == (0.0, 22.0)
    assert hi == G.fs_f22  # NG30 butts F22 (p79, derived in M2.4)
    assert lo > G.fs_nose  # the nose tip is FS -6.8
    assert lo <= G.elec_book_battery_model_fs <= hi
    assert G.elec_book_battery_model_fs == (lo + hi) / 2
    assert P["elec_book_battery_fs_range"]["status"] == "positioned-from-text"
    assert P["elec_book_battery_fs_range"]["confidence"] == "low"
    assert "A6" in P["elec_book_battery_fs_range"]["note"]
    assert P["elec_book_battery_model_fs"]["status"] == "unsourced"
    assert P["elec_book_battery_model_fs"]["source"] == ""


def test_relays_ride_on_the_front_of_f22():
    assert G.elec_book_relay_fs == G.fs_f22
    assert P["elec_book_relay_fs"]["status"] == "positioned-from-text"
    assert "F22" in P["elec_book_relay_fs"]["note"]


def test_starter_and_alternator_are_aft_of_the_firewall_lower_bound():
    assert G.elec_book_starter_fs_min == 150.0 > G.fs_firewall
    assert P["elec_book_starter_fs_min"]["status"] == "positioned-from-text"
    assert "lower bound" in P["elec_book_starter_fs_min"]["note"]


def test_nose_battery_delta_is_a_delta_not_a_weight():
    assert G.elec_book_battery_added_lb == 19.0
    assert P["elec_book_battery_added_lb"]["status"] == "derived"
    assert "not an absolute" in P["elec_book_battery_added_lb"]["note"]


def test_the_single_electrical_row_is_split_into_the_closure_rows():
    # Task 3 (ledger row 68): the 25 lb lump at FS 119.5 is now two rows, as the closure table has them.
    w = StructuralWeightParams()
    assert not hasattr(w, "electrical_weight_lb") and not hasattr(w, "electrical_arm_in")
    lo, hi = G.elec_book_battery_fs_range
    assert lo <= w.battery_arm_in <= hi  # the battery is in the nose
    assert w.battery_weight_lb == G.elec_book_battery_added_lb == 19.0
    assert w.starter_arm_in >= G.elec_book_starter_fs_min  # the starter and alternator are aft, FS 150 and aft
    for k in ("battery_weight_lb", "battery_arm_in", "starter_weight_lb", "starter_arm_in"):
        assert WEIGHT_PROVENANCE[k]["status"] == "derived"
    assert "nose" in WEIGHT_PROVENANCE["battery_arm_in"]["note"]


@pytest.mark.parametrize("name,w", LADDER.items())
def test_ladder_rows_are_cited_reference_data(name, w):
    row = load_ledger()["prototype_weights"]["rows"][name]
    assert row["weight_lb"] == w and row["cite"] == "cp-text:p27"
    check_citation(row["cite"])
    assert "N26MS" in row["note"] and "CP27 page 4" in row["note"]
    assert "reference only" in row["note"] and "not a ledger row" in row["note"]


def test_every_ladder_step_re_adds():
    v = [LADDER[f"n26ms_empty_{i}"] for i in range(1, 9)]
    assert v[1] == pytest.approx(v[0] + 4.9)  # small alternator
    assert v[2] == pytest.approx(v[1] + 15.4)  # com, nav, transponder
    assert v[3] == pytest.approx(v[0] + 68.5)  # 60 A alternator, starter, 25 Ah battery
    assert v[4] == pytest.approx(v[3] + 15.4)
    assert v[5] == pytest.approx(v[4] + 38.1)
    assert v[6] == pytest.approx(v[5] + 44.8)
    assert v[7] == pytest.approx(v[6] + 22.8)
    assert v == sorted(v)


def test_ladder_brackets_the_om_sample_empty_and_is_not_it():
    led = load_ledger()
    sample = led["empty"]["weight_lb"]
    rows = led["prototype_weights"]["rows"]
    assert sample == 730
    assert (
        rows["n26ms_empty_3"]["weight_lb"] < sample < rows["n26ms_empty_4"]["weight_lb"]
    )
    assert sample not in LADDER.values()


def test_ladder_rows_are_in_no_sum_and_move_no_cg():
    j = fuselage_ledger_json()
    for k in LADDER:
        assert k in j["prototype_weights"]["rows"]
        assert k not in {r["part"] for r in fuselage_ledger()}
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    for k in LADDER:
        assert k not in inc and k not in exc
    assert j["cg"]["arm_in"] is None and j["cg"]["weight_lb"] == 0.0
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)
    assert "gear" in j and "prototype_weights" not in load_ledger()["gear"]


def test_item_7_caveat_is_recorded_in_the_row():
    note = load_ledger()["prototype_weights"]["rows"]["n26ms_empty_7"]["note"]
    assert "1.8 in forward" in note and "102.2" in note
    assert 103.0 - 102.2 == pytest.approx(0.8)
