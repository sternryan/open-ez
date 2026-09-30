"""Half-chord sweep of a straight-tapered trapezoid (ledger C1).

Raymer sec. 7 / DATCOM 2.2.2: tan L_n = tan L_LE - (4n/A)(1 - lam)/(1 + lam). With n = 1/2 and
the trapezoid's own A = 2b/(c_r(1 + lam)) this is tan L_LE - (c_r - c_t)/b, b the full span.
"""

import math
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.setdefault("cadquery", MagicMock())
sys.modules.setdefault("OCP", MagicMock())

import pytest

from core.analysis import half_chord_sweep_tan


def test_hand_computed_trapezoid():
    # c_r 10, c_t 5, full span 40 (semispan 20), LE sweep 30 deg.
    # Half-chord points by hand: root (y 0) x = 10/2 = 5.0;
    # tip (y 20) x = 20 tan 30 + 5/2 = 11.5470 + 2.5 = 14.0470.
    # tan L_c/2 = (14.0470 - 5.0) / 20 = 0.45235 = tan 30 - (10 - 5)/40.
    got = half_chord_sweep_tan(math.tan(math.radians(30.0)), 10.0, 5.0, 40.0)
    assert got == pytest.approx(0.45235, abs=1e-5)


def test_matches_the_raymer_form_with_the_trapezoids_own_aspect_ratio():
    cr, ct, b, le = 55.0, 20.0, 313.0, 23.0
    lam = ct / cr
    ar = b**2 / (b * (cr + ct) / 2)
    raymer = math.tan(math.radians(le)) - (4 * 0.5 / ar) * (1 - lam) / (1 + lam)
    assert half_chord_sweep_tan(math.tan(math.radians(le)), cr, ct, b) == pytest.approx(raymer, abs=1e-12)


def test_constant_chord_keeps_the_le_sweep():
    assert half_chord_sweep_tan(0.3, 13.0, 13.0, 140.0) == pytest.approx(0.3, abs=1e-12)


def test_panel_and_gross_trapezoid_share_the_half_chord_line():
    from config.aircraft_config import config

    g = config.geometry
    tan_le = math.tan(math.radians(g.wing_sweep_le))
    panel = half_chord_sweep_tan(tan_le, g.wing_root_chord, g.wing_tip_chord, 2 * g.wing_panel_span)
    gross = half_chord_sweep_tan(tan_le, g.wing_centerline_chord, g.wing_tip_chord, g.wing_span)
    assert panel == pytest.approx(gross, abs=1e-9)
