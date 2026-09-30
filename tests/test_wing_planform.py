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
    assert G.wing_panel_span == pytest.approx(133.3, abs=0.01)
    # the retired convention put the tip near BL 180
    assert G.wing_root_bl + G.wing_span / 2 > 175


def test_wing_area_matches_independent_trapezoid_from_config_fields():
    one_panel = _trapezoid_sqin(G.wing_root_bl, G.wing_span / 2, G.wing_root_chord, G.wing_tip_chord)
    assert G.wing_area_sqft == pytest.approx(2 * one_panel / 144, abs=0.01)
    assert G.wing_area == G.wing_area_sqft


def test_aspect_ratio_pairs_the_panel_span_with_the_panel_area():
    """AR computed independently from root/tip chord, root BL and span; same planform for b and S."""
    panel = G.wing_span / 2 - G.wing_root_bl
    area_sqin = 2 * _trapezoid_sqin(G.wing_root_bl, G.wing_span / 2, G.wing_root_chord, G.wing_tip_chord)
    expect = (2 * panel) ** 2 / area_sqin
    assert G.wing_aspect_ratio == pytest.approx(expect, rel=1e-9)
    assert G.wing_aspect_ratio == pytest.approx(7.63, abs=0.02)
    # guard the retired mixed definition (full tip-to-tip span over the panel-only area)
    mixed = (G.wing_span / 12) ** 2 / G.wing_area_sqft
    assert abs(G.wing_aspect_ratio - mixed) > 2.0


def test_tip_leading_edge_fs_is_wing_le_plus_panel_times_tan_sweep():
    """CadQuery-independent geometry fact: the tip LE sits panel*tan(sweep) aft of the root LE."""
    tip_le = G.fs_wing_le + G.wing_panel_span * math.tan(math.radians(G.wing_sweep_le))
    assert tip_le - G.fs_wing_le == pytest.approx(133.3 * math.tan(math.radians(G.wing_sweep_le)), abs=0.05)
    assert tip_le > G.fs_wing_le


def test_vsp_winglet_x_is_the_tip_leading_edge(tmp_path):
    text = Path(VSPBridge.export_vsp_script(tmp_path / "w.vsp")).read_text()
    tip_le = G.fs_wing_le + G.wing_panel_span * math.tan(math.radians(G.wing_sweep_le))
    assert f'vid, "X_Rel_Location", "XForm", {tip_le})' in text


def test_calculate_mac_uses_the_same_planform():
    engine = PhysicsEngine()
    cr, ct = G.wing_root_chord, G.wing_tip_chord
    lam = ct / cr
    panel = G.wing_tip_bl - G.wing_root_bl
    mac_wing = (2 / 3) * cr * (1 + lam + lam**2) / (1 + lam)
    y_mac = (panel / 3) * (1 + 2 * lam) / (1 + lam)
    x_le_wing = G.fs_wing_le + y_mac * math.tan(math.radians(G.wing_sweep_le))
    s_wing_side = _trapezoid_sqin(G.wing_root_bl, G.wing_tip_bl, cr, ct)
    # the wing's own area agrees with the config property (both panels)
    assert 2 * s_wing_side / 144 == pytest.approx(G.wing_area_sqft, abs=0.01)

    strake = config.strakes
    s_chord_in = strake.fs_trailing_edge - strake.fs_leading_edge
    s_strake_side = (s_chord_in + cr) / 2 * G.wing_root_bl
    taper_s = cr / s_chord_in
    mac_strake = (2 / 3) * s_chord_in * (1 + taper_s + taper_s**2) / (1 + taper_s)
    total = s_wing_side + s_strake_side
    expect_mac = (mac_wing * s_wing_side + mac_strake * s_strake_side) / total
    expect_le = (x_le_wing * s_wing_side + strake.fs_leading_edge * s_strake_side) / total

    mac, mac_le = engine.calculate_mac()
    assert mac == pytest.approx(expect_mac, abs=1e-6)
    assert mac_le == pytest.approx(expect_le, abs=1e-6)


def test_vsp_script_wing_runs_root_bl_to_tip_bl(tmp_path):
    out = VSPBridge.export_vsp_script(tmp_path / "s.vsp")
    text = Path(out).read_text()
    assert re.search(rf'"Span", "XSec_1", {re.escape(str(G.wing_panel_span))}\)', text)
    assert re.search(rf'wid, "Y_Rel_Location", "XForm", {re.escape(str(G.wing_root_bl))}\)', text)
    assert re.search(rf'vid, "Y_Rel_Location", "XForm", {re.escape(str(G.wing_tip_bl))}\)', text)


def test_no_code_uses_a_literal_214_fuselage_length():
    offenders = []
    for path in list((REPO / "core").rglob("*.py")) + [REPO / "config" / "aircraft_config.py"]:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if re.search(r"\b214(\.0)?\b", line) and "fuselage" in line.lower() and "internal 214.0" not in line:
                offenders.append(f"{path.name}:{i}")
    assert offenders == []
