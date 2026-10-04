# tests/test_canopy_stations.py
"""Chapter 18 values (canopy): provenance, derived stations, the latch-pad conflict, and the ledger reference row."""

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, config
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

BOOK = {
    "canopy_plexi_length_in": 68.0,
    "canopy_rear_cut_fs": 117.0,
    "canopy_pad_length_in": 2.5,
    "canopy_pad_aft_edge_left_in": (11.0, 41.0, 59.0, 71.0),
    "canopy_pad_aft_edge_right_in": (20.0, 25.5, 48.0, 53.5),
    "canopy_safety_catch_fs": 56.75,
    "canopy_door_size_in": (4.3, 3.7),
    "canopy_check_a_min_in": 13.5,
    "canopy_check_b_in": 12.3,
    "canopy_check_datum_wl": 23.0,
    "canopy_open_past_vertical_deg": 15.0,
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_rear_cut_is_cp_corrected_with_the_three_agreeing_checks():
    assert P["canopy_rear_cut_fs"]["status"] == "cp-corrected"
    assert P["canopy_rear_cut_fs"]["source"].startswith("cp-text:p27")
    assert G.fs_firewall - G.canopy_rear_cut_fs == 8.0  # p111: 8 in to the firewall
    sc = G.canopy_rear_cut_fs - G.canopy_pad_aft_edge_left_in[2] - 2.5 / 2
    assert sc == pytest.approx(G.canopy_safety_catch_fs)


def test_front_cut_is_representational_not_a_book_value():
    assert G.canopy_front_cut_fs == 41.65
    assert P["canopy_front_cut_fs"]["status"] == "derived-unsourced"
    assert "unnamed" in P["canopy_front_cut_fs"]["source"]
    # 27.65 + 14.0: the F28 reading
    assert G.fs_f28 + 14.0 == pytest.approx(G.canopy_front_cut_fs)


def test_latch_pad_centres_are_a_conflict_pair_with_the_printed_labels():
    assert G.canopy_latch_pad_centres_fs == pytest.approx((104.75, 74.75, 44.75))
    assert G.canopy_latch_labels_fs == (104.0, 74.0, 44.0)
    for k in ("canopy_latch_pad_centres_fs", "canopy_latch_labels_fs"):
        assert P[k]["status"] == "conflict"
    d = [a - b for a, b in zip(G.canopy_latch_pad_centres_fs, G.canopy_latch_labels_fs)]
    assert d == pytest.approx([0.75] * 3)


def test_hinge_spans_and_checks_are_derived():
    assert G.canopy_hinge_spans_fs == ((89.0, 97.0), (61.0, 69.0))
    assert G.canopy_check_a_wl == pytest.approx(36.5)
    assert G.canopy_check_b_wl == pytest.approx(35.3)
    assert G.canopy_check_b_fs == 110.0
    for k in ("canopy_hinge_spans_fs", "canopy_check_a_wl", "canopy_check_b_wl"):
        assert P[k]["status"] == "derived"


def test_canopy_mass_row_is_sourced_reference_not_in_any_sum():
    row = load_ledger()["prototype_weights"]["rows"]["canopy"]
    assert row["weight_lb"] == 16.0 and row["cite"] == "cp-text:p26"
    check_citation(row["cite"])
    assert "N26MS" in row["note"] and "CP26 page 3" in row["note"]
    assert "17 lb with hinges, filled and painted (CP27 p1)" in row["note"]
    assert "canopy" not in {r["part"] for r in fuselage_ledger()}
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    assert "canopy" not in inc and "canopy" not in exc


def test_ledger_json_shape_and_cg_unchanged():
    j = fuselage_ledger_json()
    row = j["prototype_weights"]["rows"]["canopy"]
    assert set(row) == {"weight_lb", "cite", "note"} and row["weight_lb"] == 16.0
    assert {"f22", "f28", "panel", "spar", "canopy"} <= set(
        j["prototype_weights"]["rows"]
    )
    for cg in (j["cg"], j["cg_lower_bound"]):
        assert "canopy" not in cg["included"] + list(cg["excluded"])
    assert j["cg"]["arm_in"] is None and j["cg"]["weight_lb"] == 0.0
    # the lower bound (fuselage rows plus the sourced gear rows) is the value it had before the canopy row existed
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)
