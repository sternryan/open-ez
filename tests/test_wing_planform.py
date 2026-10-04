# tests/test_wing_planform.py
"""Wing panel convention: each panel runs BL wing_root_bl (root chord) to BL span/2 (tip chord)."""

import math
import re
from pathlib import Path

import pytest

from config.aircraft_config import config
from core.analysis import PhysicsEngine, VSPBridge

G = config.geometry
REPO = Path(__file__).resolve().parents[1]


def _trapezoid_sqin(root_bl, tip_bl, root_chord, tip_chord):
    """Independent one-panel trapezoid area (sq in), straight from the config fields."""
    return (tip_bl - root_bl) * (root_chord + tip_chord) / 2


def test_tip_lands_at_the_book_tip_rib():
    assert G.wing_tip_bl == pytest.approx(156.6, abs=0.5)  # book tip rib BL 157


def test_panel_runs_from_the_root_bl_not_span_over_two_outboard_of_it():
    assert G.wing_panel_span == pytest.approx(G.wing_span / 2 - G.wing_root_bl)
    assert G.wing_root_bl + G.wing_panel_span == pytest.approx(G.wing_tip_bl)
    assert G.wing_panel_span == pytest.approx(134.0, abs=0.01)
    # the retired convention put the tip near BL 180
    assert G.wing_root_bl + G.wing_span / 2 > 175


def test_exposed_wing_area_matches_independent_trapezoid_from_config_fields():
    one_panel = _trapezoid_sqin(
        G.wing_root_bl, G.wing_span / 2, G.wing_root_chord, G.wing_tip_chord
    )
    assert G.wing_exposed_area_sqft == pytest.approx(2 * one_panel / 144, abs=0.01)


def test_aspect_ratio_pairs_the_gross_span_with_the_gross_area():
    """AR computed independently from the gross trapezoid; same planform for b and S."""
    area_sqin = 2 * _trapezoid_sqin(
        0.0, G.wing_span / 2, G.wing_centerline_chord, G.wing_tip_chord
    )
    expect = G.wing_span**2 / area_sqin
    assert G.wing_aspect_ratio == pytest.approx(expect, rel=1e-9)
    # guard the retired mixed definition (full tip-to-tip span over the exposed-panel area)
    mixed = (G.wing_span / 12) ** 2 / G.wing_exposed_area_sqft
    assert abs(G.wing_aspect_ratio - mixed) > 2.0


def test_tip_leading_edge_fs_is_wing_le_plus_panel_times_tan_sweep():
    """CadQuery-independent geometry fact: the tip LE sits panel*tan(sweep) aft of the root LE."""
    tip_le = G.fs_wing_le + G.wing_panel_span * math.tan(math.radians(G.wing_sweep_le))
    assert tip_le - G.fs_wing_le == pytest.approx(
        134.0 * math.tan(math.radians(G.wing_sweep_le)), abs=0.05
    )
    assert tip_le > G.fs_wing_le


def test_vsp_winglet_x_is_the_tip_leading_edge(tmp_path):
    text = Path(VSPBridge.export_vsp_script(tmp_path / "w.vsp")).read_text()
    tip_le = G.fs_wing_le + G.wing_panel_span * math.tan(math.radians(G.wing_sweep_le))
    assert f'vid, "X_Rel_Location", "XForm", {tip_le})' in text


def test_calculate_mac_uses_the_same_planform():
    """calculate_mac is the MAC of the reference trapezoid, the planform of wing_area_sqft (ledger C2)."""
    engine = PhysicsEngine()
    tan_le = math.tan(math.radians(G.wing_sweep_le))
    # centreline chord by hand: extend the panel taper from BL wing_root_bl to BL 0
    c0 = G.wing_root_chord + G.wing_root_bl * (G.wing_root_chord - G.wing_tip_chord) / (
        G.wing_tip_bl - G.wing_root_bl
    )
    ct = G.wing_tip_chord
    # the planform is the one whose area is the reference area
    assert _trapezoid_sqin(0.0, G.wing_tip_bl, c0, ct) * 2 / 144 == pytest.approx(
        G.wing_area_sqft, abs=0.01
    )

    # MAC by direct integration of c(y)^2 over the semispan (no closed form reused)
    n = 20000
    s_half = G.wing_tip_bl
    ys = [(k + 0.5) * s_half / n for k in range(n)]
    chord = [c0 + (ct - c0) * y / s_half for y in ys]
    area = sum(chord) * s_half / n
    expect_mac = sum(c * c for c in chord) * s_half / n / area
    y_bar = sum(c * y for c, y in zip(chord, ys)) * s_half / n / area
    expect_le = (G.fs_wing_le - G.wing_root_bl * tan_le) + y_bar * tan_le

    mac, mac_le = engine.calculate_mac()
    assert mac == pytest.approx(expect_mac, abs=1e-3)
    assert mac_le == pytest.approx(expect_le, abs=1e-3)


def test_vsp_script_wing_runs_root_bl_to_tip_bl(tmp_path):
    out = VSPBridge.export_vsp_script(tmp_path / "s.vsp")
    text = Path(out).read_text()
    assert re.search(rf'"Span", "XSec_1", {re.escape(str(G.wing_panel_span))}\)', text)
    assert re.search(
        rf'wid, "Y_Rel_Location", "XForm", {re.escape(str(G.wing_root_bl))}\)', text
    )
    assert re.search(
        rf'vid, "Y_Rel_Location", "XForm", {re.escape(str(G.wing_tip_bl))}\)', text
    )


def test_no_code_uses_a_literal_214_fuselage_length():
    offenders = []
    for path in list((REPO / "core").rglob("*.py")) + [
        REPO / "config" / "aircraft_config.py"
    ]:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if (
                re.search(r"\b214(\.0)?\b", line)
                and "fuselage" in line.lower()
                and "internal 214.0" not in line
            ):
                offenders.append(f"{path.name}:{i}")
    assert offenders == []


# --- Reference area: gross trapezoid to the centreline (Block 1 follow-up) ---
MANUAL_WING_AREA_SQFT = 81.99  # om-1980:p3


def _within_1pct_of_manual(area_sqft):
    return abs(area_sqft - MANUAL_WING_AREA_SQFT) / MANUAL_WING_AREA_SQFT <= 0.01


def _printed_taper_chord_at(bl):
    """Straight taper through the printed chords 42.7 at BL 55.5 and 20.0 at BL 157 (plans-1980:p126)."""
    return 42.7 + (55.5 - bl) * (42.7 - 20.0) / (157 - 55.5)


def test_centerline_chord_extends_the_printed_taper_to_bl_zero():
    # the model's own line (root 49.97 at BL 23.0, tip 20.0 at BL 157.0) extended to BL 0
    own = (
        G.wing_root_chord
        + G.wing_root_bl * (G.wing_root_chord - G.wing_tip_chord) / G.wing_panel_span
    )
    assert G.wing_centerline_chord == pytest.approx(own, rel=1e-12)
    # the model's tip is now the printed BL 157, so the two lines coincide
    assert G.wing_centerline_chord == pytest.approx(
        _printed_taper_chord_at(0.0), abs=0.02
    )
    # the root chord at BL 23.0 lies on the same line
    assert G.wing_root_chord == pytest.approx(
        _printed_taper_chord_at(G.wing_root_bl), abs=0.01
    )


def test_reference_area_is_the_gross_trapezoid_to_the_centerline():
    gross = (
        2
        * _trapezoid_sqin(0.0, G.wing_tip_bl, G.wing_centerline_chord, G.wing_tip_chord)
        / 144
    )
    assert G.wing_area_sqft == pytest.approx(gross, abs=0.01)
    assert G.wing_area == G.wing_area_sqft
    assert _within_1pct_of_manual(G.wing_area_sqft)


def test_exposed_area_fails_the_1pct_reference_check():
    """Gate fails first: the exposed-panel area (the old reference) must not pass the 1% check."""
    exposed = (
        2
        * _trapezoid_sqin(
            G.wing_root_bl, G.wing_tip_bl, G.wing_root_chord, G.wing_tip_chord
        )
        / 144
    )
    assert G.wing_exposed_area_sqft == pytest.approx(exposed, abs=0.01)
    assert G.wing_exposed_area_sqft == pytest.approx(65.11, abs=0.01)
    assert not _within_1pct_of_manual(G.wing_exposed_area_sqft)


def test_aspect_ratio_is_span_squared_over_reference_area():
    expect = (G.wing_span / 12) ** 2 / G.wing_area_sqft
    assert G.wing_aspect_ratio == pytest.approx(expect, rel=1e-9)
    assert G.wing_aspect_ratio == pytest.approx(8.36, abs=0.02)
