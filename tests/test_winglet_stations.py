# tests/test_winglet_stations.py
"""Chapter 20 values (winglet and rudder): provenance, derived stations, the A/B/C jig closure, the unsourced analysis fields."""

import math

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE, config
from core.sources import check_citation

G = config.geometry
P = GEOMETRY_PROVENANCE

BOOK = {
    "winglet_book_root_wl": 18.4,
    "winglet_book_top_wl": 65.4,
    "winglet_book_cap_in": 1.0,
    "winglet_book_bottom_wl": 9.8,
    "winglet_book_root_le_fs": 159.7,
    "winglet_book_root_le_fs_wing_top": 160.5,
    "winglet_book_root_te_fs": 186.8,
    "winglet_book_top_te_fs": 196.6,
    "winglet_book_rudder_hinge_fs": 176.8,
    "winglet_book_rudder_widths_in": (10.0, 12.14, 11.5),
    "winglet_book_rudder_height_in": (10.5, 4.0),
    "winglet_book_rudder_max_deg": 30.0,
    "winglet_book_hinge_length_in": 7.5,
    "winglet_book_core_angle_deg": (78.64, 101.36),
    "winglet_book_core_length_in": 48.0,
    "winglet_book_jig_wprp": (149.6, 55.5),
    "winglet_book_jig_abc_in": (102.15, 108.35, 118.35),
    "winglet_book_jig_tol_in": (0.05, 0.05, 1.0),
    "winglet_book_bid_patch_in": (18.0, 14.0),
    "winglet_book_conduit_from_te_in": 13.2,
}


@pytest.mark.parametrize("name,val", BOOK.items())
def test_book_values_and_provenance(name, val):
    assert getattr(G, name) == val
    assert P[name]["status"] in ("book", "cp-corrected")
    check_citation(P[name]["source"].split(" ")[0])


def test_und_table_steps_by_two_and_one():
    t = G.winglet_book_und_table_in
    assert len(t) == 7 and t[0] == (24.0, 12.0) and t[-1] == (12.0, 6.0)
    assert all(a == 2 * b for a, b in t)
    assert all(t[i][0] - t[i + 1][0] == 2.0 for i in range(6))


def test_heights_and_chords_are_derived_from_the_printed_stations():
    assert G.winglet_height_book_in == pytest.approx(47.0)
    assert G.winglet_lower_height_book_in == pytest.approx(8.6)
    assert G.winglet_root_chord_book_in == pytest.approx(27.1)
    assert G.winglet_book_top_wl + G.winglet_book_cap_in == pytest.approx(66.4)
    for k in (
        "winglet_height_book_in",
        "winglet_lower_height_book_in",
        "winglet_root_chord_book_in",
    ):
        assert P[k]["status"] == "derived"


def test_tip_chord_is_11_4_and_not_crew_cs_28_9():
    assert G.winglet_book_tip_chord_in == 11.4
    assert G.winglet_top_le_fs == pytest.approx(185.2)
    assert P["winglet_book_tip_chord_in"]["status"] == "derived-unsourced"
    assert "28.9" in P["winglet_book_tip_chord_in"]["note"]
    assert G.winglet_book_tip_chord_in < G.winglet_root_chord_book_in  # the fin tapers
    sweep = math.degrees(
        math.atan((G.winglet_top_le_fs - G.winglet_book_root_le_fs) / 47.0)
    )
    assert sweep == pytest.approx(28.5, abs=0.5)


def test_rudder_widths_close_with_the_hinge_and_the_te():
    w = G.winglet_book_rudder_widths_in
    assert G.winglet_book_root_te_fs - G.winglet_book_rudder_hinge_fs == pytest.approx(
        w[0]
    )
    assert sum(G.winglet_book_rudder_height_in) == 14.5
    # the top width puts the TE at FS 188.94 at WL 28.9, on the line toward the printed 196.6 at the tip
    assert G.winglet_book_rudder_hinge_fs + w[1] == pytest.approx(188.94)


def test_winglet_le_offset_is_4_5_aft_of_the_wingtip():
    assert G.winglet_book_root_le_fs_wing_top - G.wing_book_le_fs_tip == pytest.approx(
        4.5
    )
    assert (
        G.winglet_book_root_le_fs_wing_top - G.winglet_book_root_le_fs
        == pytest.approx(0.8)
    )


def _dist(dx, dy, dz=0.0):
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def test_jig_a_and_b_close_within_a_quarter_inch_and_c_needs_a_lean():
    wprp_fs, wprp_bl = G.winglet_book_jig_wprp
    a_book, b_book, c_book = G.winglet_book_jig_abc_in
    lateral = G.wing_book_rib_bl[3] - wprp_bl
    a = _dist(lateral, G.winglet_book_root_le_fs_wing_top - wprp_fs)
    b = _dist(lateral, G.winglet_book_root_te_fs - wprp_fs)
    assert a - a_book == pytest.approx(-0.07, abs=0.02)
    assert b - b_book == pytest.approx(-0.25, abs=0.02)
    assert abs(a - a_book) < 0.1 and abs(b - b_book) <= 0.25 + 1e-6
    dx = G.winglet_book_top_te_fs - wprp_fs
    c_upright = _dist(lateral, dx, G.winglet_height_book_in)
    assert c_upright - c_book > 2.0  # outside the 1 in tolerance without a lean
    lean = G.winglet_cant_in
    assert lean == pytest.approx(3.6, abs=0.05)
    c_lean = _dist(lateral - lean, dx, G.winglet_height_book_in)
    assert c_lean == pytest.approx(c_book, abs=1e-6)
    assert P["winglet_cant_in"]["confidence"] == "low"
    assert P["winglet_cant_in"]["status"] == "derived-unsourced"


def test_analysis_fields_carry_the_book_values():
    # M2.8: the analysis winglet moved to the p135 values (ledger rows)
    assert (G.winglet_height, G.winglet_root_chord, G.winglet_tip_chord) == (
        pytest.approx(G.winglet_height_book_in),
        pytest.approx(G.winglet_root_chord_book_in),
        pytest.approx(G.winglet_book_tip_chord_in),
    )
    assert (G.winglet_height, G.winglet_root_chord, G.winglet_tip_chord) == (
        47.0,
        27.1,
        11.4,
    )
    assert P["winglet_height"]["status"] == "book"
    assert P["winglet_root_chord"]["status"] == "derived"
    assert P["winglet_tip_chord"]["status"] == "derived-unsourced"
    for k in ("winglet_height", "winglet_root_chord", "winglet_tip_chord"):
        assert "plans-1980:p135" in P[k]["source"]
