# tests/test_strake_stations.py
"""Chapter 21 values (strakes and fuel): provenance, the p147 arithmetic, the fuel capacity conflict, and the ledger reference rows."""

import math
from pathlib import Path

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, StrakeConfig, config
from core.ledger import fuselage_cg, fuselage_ledger, fuselage_ledger_json, load_ledger
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE
TAN = math.tan(math.radians(G.stk_book_spar_slope_deg))

BOOK = {
    "stk_book_le_fs_fuselage": 50.0,
    "stk_book_le_fs_bl_23": 73.3,
    "stk_book_le_fs_bl_45": 99.5,
    "stk_book_spar_fwd_fs_bl_23": 118.5,
    "stk_book_bab_fuselage_fs": 103.5,
    "stk_book_foam_thickness_in": 0.35,
    "stk_book_tle_in": (33.5, 2.55),
    "stk_book_ble_in": (25.5, 2.55),
    "stk_book_b23_in": (21.3, 7.3),
    "stk_book_bab_in": (13.4, 7.3, 7.75),
    "stk_book_db_in": (28.5, 7.3, 6.5),
    "stk_book_b23_hole_in": (5.0, 3.0),
    "stk_book_notch_radius_in": (0.8, 1.3),
    "stk_book_skin_top_in": (23.9, 44.3, 44.3, 67.2),
    "stk_book_skin_bottom_in": (23.7, 44.1, 44.1, 67.0),
    "stk_book_skin_spar_edge_in": (32.0, 4.9),
    "stk_book_jig_rib_height_in": (2.65, 3.45),
    "stk_book_sump_blister_in": (21.0, 2.75, 0.5),
    "stk_book_baggage_limit_lb": 100.0,
    "fuel_book_lb_per_gal": 6.0,
    "fuel_book_arm_fs": 104.5,
    "fuel_book_capacity_om_total_gal": 52.0,
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_cutout_tables_are_book_and_in_order():
    fwd = G.stk_book_cutout_fwd_in
    assert len(fwd) == 7 and fwd[0][0] == 65.8 and fwd[-1][0] == 42.0
    assert [r[0] for r in fwd] == sorted((r[0] for r in fwd), reverse=True)
    for _st, top, bottom in fwd:
        assert 0 < top < bottom  # depths below WL 23, the top edge shallower
    assert G.stk_book_cutout_aft_in == (30.0, 15.0, 1.40, 9.15)
    for k in ("stk_book_cutout_fwd_in", "stk_book_cutout_aft_in"):
        assert P[k]["status"] == "book" and P[k]["confidence"] == "medium"
        check_citation(P[k]["source"])


def test_cutout_top_depth_190_vs_140_is_a_conflict():
    assert G.stk_book_cutout_aft_top_alt_in == 1.90
    assert G.stk_book_cutout_aft_in[2] == 1.40
    assert P["stk_book_cutout_aft_top_alt_in"]["status"] == "conflict"


def test_le_is_a_polyline_not_a_line():
    a = (G.stk_book_le_fs_fuselage, G.stk_book_fuselage_side_bl[0])
    b = (G.stk_book_le_fs_bl_23, 23.0)
    c = (G.stk_book_le_fs_bl_45, 45.0)
    d = G.wing_le_anchor  # (113.9, 58.0)

    def deg(p, q):
        return math.degrees(math.atan2(q[0] - p[0], q[1] - p[1]))

    assert deg(a, b) == pytest.approx(65.0, abs=1.0)  # FS per BL from the BL axis
    assert deg(b, c) == pytest.approx(50.0, abs=1.0)
    assert deg(c, d) == pytest.approx(47.9, abs=1.0)
    assert deg(a, b) - deg(b, c) > 10  # the kink at BL 23 is real
    assert d == (113.9, 58.0)  # the wing LE junction, CP25 LPC 7 (M2.7)


def test_strake_te_99_5_is_the_le_at_bl_45_not_a_trailing_edge():
    cfg = StrakeConfig()
    assert (
        cfg.fs_trailing_edge == G.stk_book_le_fs_bl_45
    )  # the coincidence the flag names
    assert G.stk_book_spar_fwd_fs_bl_23 - cfg.fs_trailing_edge == pytest.approx(19.0)
    src = (
        Path(__file__).resolve().parents[1] / "config" / "aircraft_config.py"
    ).read_text()
    assert "NOT a strake TE" in src


def test_spar_face_slope_and_the_two_page_agreement():
    assert G.stk_book_spar_slope_deg == 8.57
    assert math.degrees(math.atan(4.9 / 32.5)) == pytest.approx(8.57, abs=0.01)  # p118
    p142 = math.degrees(
        math.atan(G.stk_book_skin_spar_edge_in[1] / G.stk_book_skin_spar_edge_in[0])
    )
    assert p142 == pytest.approx(8.71, abs=0.01)  # p142 prints 4.9 over 32.0
    assert abs(p142 - G.stk_book_spar_slope_deg) < 0.2
    assert P["stk_book_spar_slope_deg"]["status"] == "derived"
    assert P["stk_book_spar_slope_deg"]["confidence"] == "medium"


def test_junction_closes_b23_and_db_against_the_printed_lengths():
    assert G.stk_book_junction_fs == pytest.approx(97.2)
    # p147 scaling puts the junction at 97.3, so B23 derives 21.2 against the printed 21.3
    assert G.stk_book_spar_fwd_fs_bl_23 - 97.3 == pytest.approx(21.2)
    assert abs(21.2 - G.stk_book_b23_in[0]) < 0.15
    assert G.stk_book_db_far_fs == pytest.approx(115.3, abs=0.05)
    # DB derived from the p147 junction and corner (97.3, 23) to (115, 45) is 28.2 to 28.3, printed 28.5
    assert math.hypot(115.0 - 97.3, 22.0) == pytest.approx(28.24, abs=0.05)
    assert abs(28.24 - G.stk_book_db_in[0]) < 0.3
    # BAB from the junction to the fuselage side
    bab = math.hypot(
        G.stk_book_junction_fs - G.stk_book_bab_fuselage_fs,
        23.0 - G.stk_book_fuselage_side_bl[1],
    )
    assert bab == pytest.approx(13.2, abs=0.3)
    assert abs(bab - G.stk_book_bab_in[0]) < 0.4
    for k in (
        "stk_book_junction_fs",
        "stk_book_db_far_fs",
        "stk_book_spar_fwd_fs_bl_45",
    ):
        assert P[k]["status"] == "derived"


def test_r45_meets_the_spar_at_121_8():
    assert G.stk_book_spar_fwd_fs_bl_45 == pytest.approx(121.8, abs=0.05)
    r45 = G.stk_book_spar_fwd_fs_bl_45 - G.stk_book_le_fs_bl_45
    assert r45 == pytest.approx(22.3, abs=0.1)


def test_inboard_skin_d_closes_against_the_spar_face_at_the_fuselage_side():
    spar_fs_at_side = (
        G.stk_book_spar_fwd_fs_bl_23 - (23.0 - G.stk_book_fuselage_side_bl[0]) * TAN
    )
    run = spar_fs_at_side - G.stk_book_le_fs_fuselage
    assert run == pytest.approx(66.8, abs=0.2)
    assert abs(run - G.stk_book_skin_bottom_in[3]) < 0.4
    # the top and bottom edges differ by the 1 in bevel offset, 0.2 each
    for t, b in zip(G.stk_book_skin_top_in, G.stk_book_skin_bottom_in):
        assert t - b == pytest.approx(0.2, abs=1e-9)
    assert G.stk_book_skin_top_in[1] == G.stk_book_skin_top_in[2]


def test_outboard_skin_spar_edge_ends_near_the_wing_root_joint():
    long_, off = G.stk_book_skin_spar_edge_in
    bl_end = 23.0 + math.sqrt(long_**2 - off**2)
    assert bl_end == pytest.approx(54.6, abs=0.1)
    assert abs(bl_end - 55.5) < 1.0  # the BL 55.5 foam joint, 0.9 away


def test_sump_runs_to_the_firewall():
    assert G.stk_book_sump_fs == (103.5, 125.0)
    assert G.stk_book_sump_fs[0] == G.stk_book_bab_fuselage_fs
    assert G.stk_book_sump_fs[1] == G.fs_firewall
    assert G.stk_book_sump_fs[0] + G.stk_book_sump_blister_in[0] == pytest.approx(124.5)
    assert P["stk_book_sump_fs"]["status"] == "derived"


def test_forward_cutout_reaches_the_le_and_the_seat_bulkhead():
    spar_at_side = (
        G.stk_book_spar_fwd_fs_bl_23 - (23.0 - G.stk_book_fuselage_side_bl[0]) * TAN
    )
    fwd = G.stk_book_cutout_fwd_in
    assert spar_at_side - fwd[0][0] == pytest.approx(
        51.0, abs=0.3
    )  # LE at the side is FS 50
    assert spar_at_side - fwd[-1][0] == pytest.approx(
        74.8, abs=0.3
    )  # front seat bulkhead face
    # the tank cutout aft edge 15.0 forward of the spar sits against BAB at 103.5
    assert spar_at_side - G.stk_book_cutout_aft_in[1] == pytest.approx(101.8, abs=0.3)


def test_fuselage_side_bl_is_scaled_not_a_source():
    assert P["stk_book_fuselage_side_bl"]["status"] == "derived-unsourced"
    assert P["stk_book_fuselage_side_bl"]["confidence"] == "low"
    assert G.stk_book_fuselage_side_bl[0] == pytest.approx(G.cockpit_width / 2, abs=1.0)


def test_fuel_arm_and_rate_close_the_om_rows():
    assert 240 * G.fuel_book_arm_fs == 25080
    assert 150 * G.fuel_book_arm_fs == 15675
    assert 40 * G.fuel_book_lb_per_gal == 240
    assert G.fuel_book_arm_fs == config.structural_weights.fuel_arm_in


def test_fuel_capacity_is_a_conflict_pair_and_the_model_keeps_26():
    assert (G.fuel_book_capacity_plans_gal, G.fuel_book_capacity_om_gal) == (25.5, 28.0)
    assert P["fuel_book_capacity_plans_gal"]["status"] == "conflict"
    assert P["fuel_book_capacity_om_gal"]["status"] == "conflict"
    assert 2 * G.fuel_book_capacity_plans_gal == 51
    assert 2 * G.fuel_book_capacity_om_gal == 56
    assert (
        G.fuel_book_capacity_om_total_gal / 2 == 26.0 == StrakeConfig().tank_volume_gal
    )
    assert config.propulsion.fuel_capacity_gal == G.fuel_book_capacity_om_total_gal
    assert "28 each" in P["fuel_book_capacity_plans_gal"]["note"]
    assert "25.5" in P["fuel_book_capacity_plans_gal"]["note"]
    assert "52" in P["fuel_book_capacity_om_gal"]["note"]


def test_every_new_strake_field_cites_a_page_or_names_a_conflict():
    for k, e in P.items():
        if not k.startswith(("stk_book_", "fuel_book_")):
            continue
        if e["status"] in ("book", "cp-corrected", "derived"):
            check_citation(e["source"])
        else:
            assert e["status"] in ("conflict", "derived-unsourced"), k
            assert e["note"], k


def test_strake_has_no_builder_weight_row_and_no_part_is_named_for_it():
    rows = load_ledger()["prototype_weights"]["rows"]
    assert not any("strake" in k for k in rows)  # CP26 p3 weights are all "no strakes"
    parts = {r["part"] for r in fuselage_ledger()}
    assert not any("strake" in p for p in parts)


def test_ledger_json_cg_is_unchanged_by_the_new_reference_rows():
    j = fuselage_ledger_json()
    assert j["cg"]["arm_in"] is None and j["cg"]["weight_lb"] == 0.0
    _w, _arm, inc, exc = fuselage_cg(lower_bound=True)
    # the lower bound (fuselage rows plus the sourced gear rows) is the value it had before these rows existed
    assert j["cg_lower_bound"]["weight_lb"] == pytest.approx(55.6195531, abs=1e-6)
    for k in j["prototype_weights"]["rows"]:
        if k.startswith("n26ms_empty_") or k in (
            "dynafocal_mount",
            "cowl_glass",
            "cowl_graphite",
        ):
            assert k not in inc and k not in exc
