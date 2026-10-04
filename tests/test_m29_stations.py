# tests/test_m29_stations.py
"""Chapters 24 to 26 values (covers, finishing, upholstery): provenance, the two ch24 conflicts, the finish-delta reference rows."""

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, config
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE
M29 = ("cov_book_", "fin_book_", "upl_book_")

BOOK = {
    "cov_book_lc1_fs": (52.0, 60.0),
    "cov_book_lc1_in": (9.1, 8.0),
    "cov_book_lc1_offset_in": 2.0,
    "cov_book_console_core_in": 0.35,
    "cov_book_lc3_in": (10.6, 9.1),
    "cov_book_lc3_step_in": 3.0,
    "cov_book_lc4_in": (11.7, 9.1),
    "cov_book_lc5_in": (18.2, 1.9),
    "cov_book_aft_cover_block_in": (18.0, 20.0, 2.0),
    "cov_book_aft_cover_strut_gap_in": 0.125,
    "cov_book_thigh_rib_in": (10.8, 3.65),
    "cov_book_thigh_floor_in": (17.0, 12.3),
    "cov_book_thigh_notch_in": (5.6, 4.5),
    "cov_book_valve_cover_in": (6.6, 5.0, 0.025),
    "cov_book_canard_cover_foam_in": 2.0,
    "cov_book_seal_gap_in": 0.5,
    "cov_book_seal_front_gap_in": 0.0625,
    "fin_book_fill_in": (0.02, 0.03),
    "fin_book_primer_in": (0.004, 0.008),
    "fin_book_min_temp_f": 70.0,
    "upl_book_suitcase_in": (30.0, 18.0, 14.0, 5.0),
    "upl_book_front_cushion_in": (46.0, 16.5, 2.0),
    "upl_book_rear_cushion_in": (12.0, 16.0, 18.0, 2.0),
    "upl_book_front_headrest_in": (4.5, 4.5, 2.0),
    "upl_book_rear_headrest_in": (4.5, 4.5, 1.5),
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] == "book"
    check_citation(P[name]["source"].split(" ")[0])


def test_lc1_stations_are_the_only_printed_station_and_the_panel_agrees():
    a, b = G.cov_book_lc1_fs
    assert b - a == G.cov_book_lc1_in[1] == 8.0
    assert P["cov_book_lc1_fs"]["confidence"] == "high"
    assert (
        a - 12.0 == 40.0
    )  # 12 in forward to the panel: the OM front-of-panel station (om-1980:p34)
    assert G.cov_book_lc1_in[0] == pytest.approx(
        11.6 - 2.5
    )  # WL 11.6 less the derived floor line


def test_lc2_length_is_a_conflict_pair():
    assert (G.cov_book_lc2_len_in, G.cov_book_lc2_len_cobelu_in) == (30.6, 30.8)
    for k in ("cov_book_lc2_len_in", "cov_book_lc2_len_cobelu_in"):
        assert P[k]["status"] == "conflict" and P[k]["note"]
    assert "30.8" in P["cov_book_lc2_len_in"]["note"]


def test_aft_cover_ply_count_is_a_conflict_pair():
    assert G.cov_book_aft_cover_plies == (1, 1)
    assert G.cov_book_aft_cover_plies_cobelu == (1, 2)
    for k in ("cov_book_aft_cover_plies", "cov_book_aft_cover_plies_cobelu"):
        assert P[k]["status"] == "conflict"
    note = P["cov_book_aft_cover_plies"]["note"]
    assert "LPC 54" in note and "cobelu" in note


def test_thigh_floor_area_and_rib_spacing_close():
    a = G.cov_book_thigh_floor_in
    n = G.cov_book_thigh_notch_in
    assert a[0] * a[1] - n[0] * n[1] == pytest.approx(183.9)
    assert G.cov_book_thigh_rib_spacing_in == n[0]


def test_finish_is_thicknesses_and_a_colour_rule_no_weight():
    assert G.fin_book_fill_in[0] < G.fin_book_fill_in[1] <= G.fin_book_fill_bands_in[0]
    assert G.fin_book_white_surfaces == ("wing_upper", "canard_upper")
    assert not any(k.startswith("fin_book_") and "lb" in k for k in P)


def test_every_new_field_cites_a_page_or_names_a_conflict():
    found = [k for k in P if k.startswith(M29)]
    assert len(found) >= 30
    for k in found:
        assert hasattr(G, k), k
        if P[k]["status"] in ("book", "cp-corrected", "derived"):
            check_citation(P[k]["source"].split(" ")[0])
        else:
            assert P[k]["status"] == "conflict", k
            assert P[k]["note"], k


def test_no_new_field_name_contains_rake():  # tests/test_nose_elevator_stations.py bans it (gear rake)
    assert not [k for k in vars(G) if k.startswith(M29) and "rake" in k]


def test_finish_deltas_are_reference_rows_never_summed():
    rows = load_ledger()["prototype_weights"]["rows"]
    d = {k: r for k, r in rows.items() if k.startswith("finish_delta_")}
    assert set(d) == {
        "finish_delta_canopy",
        "finish_delta_aileron",
        "finish_delta_wing",
    }
    assert d["finish_delta_canopy"]["weight_lb"] == 1.0
    assert d["finish_delta_aileron"]["weight_lb"] == pytest.approx(5.4 - 5.125)
    assert 2.1 <= d["finish_delta_wing"]["weight_lb"] <= 2.3
    assert rows["wing_painted"]["weight_lb"] == 60.0
    for r in (*d.values(), rows["wing_painted"]):
        check_citation(r["cite"])
        assert "never summed" in r["note"] or "reference only" in r["note"]
        assert "N26MS" in r["note"]
    for k in ("finish_delta_canopy", "finish_delta_aileron", "finish_delta_wing"):
        assert "CP26 page 3" in rows[k]["note"] and "CP27 page 1" in rows[k]["note"]
    # no finish ROW (a part mass) exists besides the deltas
    assert not any(
        k == "finish" or k.startswith("finish_") and not k.startswith("finish_delta_")
        for k in rows
    )
    parts = {r["part"] for r in fuselage_ledger()}
    assert not any("finish" in p or "paint" in p for p in parts)


def test_painted_wing_weight_cite_is_cp27_p1_not_cp26_p16():
    from config.aircraft_config import WEIGHT_PROVENANCE

    note = WEIGHT_PROVENANCE["wing_weight_lb"]["note"]
    assert "CP26 p16" not in note and "CP27 p1" in note


def test_ledger_json_cg_is_unchanged_by_the_finish_rows():
    j = fuselage_ledger_json()
    assert j["cg"]["arm_in"] is None and j["cg"]["weight_lb"] == 0.0
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    for k in j["prototype_weights"]["rows"]:
        if k.startswith("finish_delta_") or k == "wing_painted":
            assert k not in inc and k not in exc
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)
