# tests/test_engine_stations.py
"""Chapter 23 values (engine): provenance, the limits, the oil arm, the representational block, and the ledger reference rows."""

import pytest

from config.aircraft_config import (
    GEOMETRY_PROVENANCE,
    WEIGHT_PROVENANCE,
    PropulsionConfig,
    config,
)
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

BOOK = {
    "eng_book_engine_max_lb": 246.0,
    "eng_book_vibrating_max_lb": 286.0,
    "eng_book_oil_lb": 8.0,
    "eng_book_oil_fs": 140.0,
    "eng_book_down_thrust_deg": 2.0,
    "eng_book_crank_bl": 0.0,
    "eng_book_cowl_trim_in": 9.0,
    "eng_book_cowl_reinf_in": (4, 2.0),
    "eng_book_cowl_aft_shift_in": 0.7,
    "eng_book_rib_in": (0.020, 20.0, 24.0, 1.2, 0.5),
    "eng_book_bracket_plate_in": (6.5, 2.5, 0.063),
    "eng_book_bracket_holes_in": (2.0, 3.6, 1.8, 1.25),
    "eng_book_bracket_angle_in": (2.0, 2.0, 0.063),
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_limits_are_limits_and_the_allowance_is_derived():
    assert G.eng_book_vibrating_allowance_lb == 40.0
    assert P["eng_book_vibrating_allowance_lb"]["status"] == "derived"
    assert "limit, not a weight" in P["eng_book_engine_max_lb"]["note"]


def test_down_thrust_and_crank_line_come_from_the_cp_not_the_chapter():
    for k in ("eng_book_down_thrust_deg", "eng_book_crank_bl"):
        assert P[k]["status"] == "cp-corrected"
        assert P[k]["source"].startswith("cp-text:p32")
    assert "CP38" in P["eng_book_down_thrust_deg"]["note"]


def test_the_block_is_representational_and_unsourced():
    for k in ("eng_book_block_in", "eng_book_block_fwd_fs", "eng_book_block_wl"):
        assert P[k]["status"] == "unsourced" and P[k]["source"] == ""
        assert P[k]["confidence"] == "low"
    assert "not held" in P["eng_book_block_in"]["note"]


def test_the_block_sits_aft_of_the_firewall_around_the_oil_and_the_starter():
    length, width, height = G.eng_book_block_in
    fwd = G.eng_book_block_fwd_fs
    aft = fwd + length
    assert fwd > G.fs_firewall  # a pusher: the engine is aft of the firewall
    assert fwd < G.eng_book_oil_fs < aft  # oil FS 140 is inside the block
    assert fwd < G.elec_book_starter_fs_min <= aft  # the starter end, station 150+
    assert width < 40 and height < 40  # inside a cowl, not a wing
    assert (
        G.eng_book_block_wl - height / 2 > G.wl_fuselage_bottom_3view
    )  # above the bottom line


def test_oil_station_is_the_only_printed_engine_arm_and_is_aft_of_the_firewall():
    assert G.eng_book_oil_fs > G.fs_firewall
    led = load_ledger()
    assert led["loads"]["oil"]["arm_in"] == G.eng_book_oil_fs
    assert led["loads"]["oil"]["cite"].startswith("om-1980:p25")


def test_engine_flags_are_flagged_and_values_are_unchanged():
    cfg = PropulsionConfig()
    assert (cfg.engine_cg_arm_in, cfg.engine_mass_kg, cfg.engine_dry_weight_lb) == (
        8.0,
        113.0,
        243.0,
    )
    assert (
        cfg.engine_cg_arm_in < G.fs_firewall
    )  # 'forward of the firewall': the contradiction
    assert cfg.engine_mass_kg * 2.20462 > G.eng_book_engine_max_lb  # 249.1 against 246
    assert cfg.engine_dry_weight_lb < G.eng_book_engine_max_lb
    for k in ("engine_cg_arm_in", "engine_mass_kg"):
        assert WEIGHT_PROVENANCE[k]["status"] == "conflict"
    assert WEIGHT_PROVENANCE["engine_dry_weight_lb"]["status"] == "unsourced"


def test_prop_diameter_is_a_three_way_conflict():
    assert G.eng_book_prop_dia_in == 60.0 == PropulsionConfig().engine_prop_diameter_in
    assert P["eng_book_prop_dia_in"]["status"] == "conflict"
    note = P["eng_book_prop_dia_in"]["note"]
    assert "58" in note and "62" in note and "60" in note


def test_rib_thickness_is_the_drawing_not_the_text_typo():
    t, sheet_l, sheet_w, flange, edge = G.eng_book_rib_in
    assert t == 0.020
    assert (
        "0.20" in P["eng_book_rib_in"]["note"]
        and "typo" in P["eng_book_rib_in"]["note"]
    )
    assert (sheet_l, sheet_w) == (20.0, 24.0)
    assert 2 * flange + edge < sheet_w  # two flanges and the edge offset fit the sheet


def test_bracket_holes_fit_the_plate():
    length, width, _t = G.eng_book_bracket_plate_in
    oil_d, oil_from_carb, carb_d, carb_from_fwd = G.eng_book_bracket_holes_in
    carb_x = carb_from_fwd
    oil_x = carb_x + oil_from_carb
    assert oil_x + oil_d / 2 <= length
    assert carb_x - carb_d / 2 >= 0 and carb_d < width and oil_d < width
    assert P["eng_book_bracket_holes_in"]["confidence"] == "medium"


def test_reference_rows_are_cited_and_in_no_sum():
    rows = load_ledger()["prototype_weights"]["rows"]
    assert rows["dynafocal_mount"]["weight_lb"] == 5.19
    assert rows["dynafocal_mount"]["weight_lb"] == pytest.approx(5 + 3 / 16, abs=0.005)
    assert rows["dynafocal_mount"]["cite"] == "cp-text:p26"
    assert "CP26 page 3" in rows["dynafocal_mount"]["note"]
    assert rows["cowl_glass"]["weight_lb"] == 18.0
    assert rows["cowl_graphite"]["weight_lb"] == 12.0
    for k in ("cowl_glass", "cowl_graphite"):
        assert rows[k]["cite"] == "cp-text:p27" and "CP27 page 5" in rows[k]["note"]
    for k in ("dynafocal_mount", "cowl_glass", "cowl_graphite"):
        check_citation(rows[k]["cite"])
        assert (
            "reference only" in rows[k]["note"]
            and "not a ledger row" in rows[k]["note"]
        )
        assert k not in {r["part"] for r in fuselage_ledger()}
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    for k in ("dynafocal_mount", "cowl_glass", "cowl_graphite"):
        assert k not in inc and k not in exc
    j = fuselage_ledger_json()
    assert j["cg"]["arm_in"] is None
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)


def test_dynafocal_mount_is_inside_the_builder_ladder_step_not_extra():
    rows = load_ledger()["prototype_weights"]["rows"]
    # step 6 of the ladder adds the dynafocal mount with the other extras (38.1 lb); the mount row is a part of that, never added to it
    assert "dynafocal mount" in rows["n26ms_empty_6"]["note"]
    assert rows["dynafocal_mount"]["weight_lb"] < 38.1
