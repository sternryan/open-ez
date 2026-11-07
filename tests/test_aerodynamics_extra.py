"""Additional unit tests for core/aerodynamics.py."""

from pathlib import Path

import cadquery as cq
import numpy as np
import pytest

from config import AirfoilType, config
from core.aerodynamics import (
    Airfoil,
    AirfoilCoordinates,
    AirfoilFactory,
    airfoil_factory,
)


@pytest.fixture(scope="module")
def factory() -> AirfoilFactory:
    """Shared AirfoilFactory instance for module tests."""
    return AirfoilFactory()


def _make_symmetric_coords(
    n: int = 40, thickness: float = 0.12, name: str = "SYM"
) -> AirfoilCoordinates:
    """Create a cosine-spaced symmetric airfoil for fast deterministic tests."""
    beta = np.linspace(0.0, np.pi, n)
    x = 0.5 * (1.0 - np.cos(beta))
    yt = (thickness / 0.2) * (
        0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4
    )
    return AirfoilCoordinates(
        name=name,
        x_upper=x,
        y_upper=yt,
        x_lower=x.copy(),
        y_lower=-yt,
    )


def _make_uniform_arc_spike_coords(n_total: int) -> AirfoilCoordinates:
    """Build coordinates where every segment has exact arc length ds = 0.10.

    Uses a 3-4-5 right triangle (dx=0.08, dy=+-0.06, ds=0.10) around index 5
    so s_norm equals np.linspace(0, 1, n_total) and CubicSpline evaluates at
    its exact knots.
    """
    x_upper = np.array([0.0, 0.10, 0.20, 0.30, 0.40, 0.48, 0.56])
    y_upper = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.06, 0.0])
    n_lower = n_total - len(x_upper) + 1
    x_lower = 0.56 - 0.10 * np.arange(n_lower)[::-1]
    y_lower = np.zeros(n_lower)
    return AirfoilCoordinates(
        name="SPIKE",
        x_upper=x_upper,
        y_upper=y_upper,
        x_lower=x_lower,
        y_lower=y_lower,
    )


def test_airfoil_coordinates_concatenation_and_deduplication():
    """AirfoilCoordinates.x and .y reverse lower surface and drop its first reversed point."""
    coords = AirfoilCoordinates(
        name="ASYM_TEST",
        x_upper=np.array([0.0, 0.25, 0.75, 1.0]),
        y_upper=np.array([0.0, 0.06, 0.04, 0.01]),
        x_lower=np.array([0.0, 0.50, 1.0]),
        y_lower=np.array([0.0, -0.03, -0.01]),
    )

    assert coords.name == "ASYM_TEST"
    expected_x = np.array([0.0, 0.25, 0.75, 1.0, 0.50, 0.0])
    expected_y = np.array([0.0, 0.06, 0.04, 0.01, -0.03, 0.0])

    assert len(coords.x) == 6
    assert len(coords.y) == 6
    assert coords.x == pytest.approx(expected_x, rel=1e-6)
    assert coords.y == pytest.approx(expected_y, rel=1e-6)


def test_trailing_edge_closure_threshold_boundary_and_defensive_copy():
    """_close_trailing_edge averages endpoints only when |y[0] - y[-1]| > 1e-6."""
    x_side = np.linspace(0.0, 1.0, 11)
    y_upper = np.zeros(11)
    y_lower = np.zeros(11)
    y_upper[0] = 0.004
    y_lower[0] = -0.002

    coords = AirfoilCoordinates("TE_GAP", x_side, y_upper, x_side.copy(), y_lower)
    airfoil = Airfoil(coords, n_points=21, smooth=False)
    _x_out, y_out = airfoil.coordinates

    # Difference 0.006 > 1e-6: averaged to (0.004 + -0.002) / 2 = +0.001
    assert y_out[0] == pytest.approx(0.001, rel=1e-6)
    assert y_out[-1] == pytest.approx(0.001, rel=1e-6)

    # Exact boundary |y[0] - y[-1]| == 1e-6: strict '>' does NOT average
    airfoil._y[0] = 0.0
    airfoil._y[-1] = -1e-6
    airfoil._close_trailing_edge()
    assert airfoil._y[0] == 0.0
    assert airfoil._y[-1] == pytest.approx(-1e-6, rel=1e-6)

    # Above boundary |y[0] - y[-1]| == 3e-6 > 1e-6: averaged to -1.5e-6
    airfoil._y[0] = 0.0
    airfoil._y[-1] = -3e-6
    airfoil._close_trailing_edge()
    assert airfoil._y[0] == pytest.approx(-1.5e-6, rel=1e-6)
    assert airfoil._y[-1] == pytest.approx(-1.5e-6, rel=1e-6)

    # coordinates property returns defensive copies
    x_mut, y_mut = airfoil.coordinates
    x_mut[0] = 99.0
    y_mut[0] = -99.0
    x_fresh, y_fresh = airfoil.coordinates
    assert x_fresh[0] == pytest.approx(0.0, abs=1e-9)
    assert y_fresh[0] == pytest.approx(-1.5e-6, rel=1e-6)


def test_savgol_smoothing_branches_and_min_window():
    """Pin Savitzky-Golay n_points >= 11 boundary and both branches of min(11, n_points // 2 * 2 - 1)."""
    # Branch 1: n_points = 10 (< 11) with smooth=True skips savgol_filter
    coords_10 = _make_uniform_arc_spike_coords(10)
    af_10_smooth = Airfoil(coords_10, n_points=10, smooth=True)
    _, y_10 = af_10_smooth.coordinates
    assert y_10[5] == pytest.approx(0.06, rel=1e-6)

    # Branch 2: n_points = 11 (exact >= 11 boundary) -> window = min(11, 9) = 9 (right side of min wins)
    # Cubic Savitzky-Golay center weight for window=9 (m=4): 3*(3*16 + 12 - 1)/(7*9*11) = 59/231
    coords_11 = _make_uniform_arc_spike_coords(11)
    af_11_smooth = Airfoil(coords_11, n_points=11, smooth=True)
    af_11_raw = Airfoil(coords_11, n_points=11, smooth=False)
    assert af_11_raw.coordinates[1][5] == pytest.approx(0.06, rel=1e-6)
    assert af_11_smooth.coordinates[1][5] == pytest.approx(
        0.06 * 59.0 / 231.0, rel=1e-6
    )

    # Branch 3: n_points = 21 -> window = min(11, 19) = 11 (left side of min wins)
    # Cubic Savitzky-Golay center weight for window=11 (m=5): 3*(3*25 + 15 - 1)/(9*11*13) = 89/429
    coords_21 = _make_uniform_arc_spike_coords(21)
    af_21_smooth = Airfoil(coords_21, n_points=21, smooth=True)
    af_21_raw = Airfoil(coords_21, n_points=21, smooth=False)
    x_21_smooth, y_21_smooth = af_21_smooth.coordinates
    x_21_raw, y_21_raw = af_21_raw.coordinates

    assert y_21_raw[5] == pytest.approx(0.06, rel=1e-6)
    assert y_21_smooth[5] == pytest.approx(0.06 * 89.0 / 429.0, rel=1e-6)
    # x coordinates are never filtered by savgol_filter
    assert x_21_smooth == pytest.approx(x_21_raw, rel=1e-6)


def test_apply_washout_quarter_chord_pivot_and_te_direction():
    """apply_washout rotates clockwise about x_pivot = 0.25: LE moves down, pivot stays fixed, TE moves up."""
    coords = _make_symmetric_coords(n=40, thickness=0.12, name="SYM")
    airfoil = Airfoil(coords, n_points=80, smooth=False)
    # Place index 10 exactly at the quarter-chord pivot (0.25, 0.0)
    airfoil._x[10] = 0.25
    airfoil._y[10] = 0.0

    # Rotate by +30 deg: theta = -30 deg, cos(theta) = sqrt(3)/2, sin(theta) = -0.5
    washed = airfoil.apply_washout(30.0)
    assert washed.name == "SYM_washout_30.0deg"

    theta = np.radians(-30.0)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    expected_x = (airfoil._x - 0.25) * cos_t + airfoil._y * sin_t + 0.25
    expected_y = -(airfoil._x - 0.25) * sin_t + airfoil._y * cos_t
    half = len(airfoil._x) // 2

    assert washed._raw.x_upper == pytest.approx(expected_x[:half], rel=1e-6)
    assert washed._raw.y_upper == pytest.approx(expected_y[:half], rel=1e-6)
    assert washed._raw.x_lower == pytest.approx(expected_x[half:][::-1], rel=1e-6)
    assert washed._raw.y_lower == pytest.approx(expected_y[half:][::-1], rel=1e-6)

    # Index 0 (LE at x = 0.0, y = 0.0): x_rot = 0.25 - 0.25*cos(30), y_rot = -0.125 (moves down)
    assert washed._raw.x_upper[0] == pytest.approx(
        0.25 - 0.25 * np.cos(np.radians(30.0)), rel=1e-6
    )
    assert washed._raw.y_upper[0] == pytest.approx(-0.125, rel=1e-6)

    # Index 10 (x = 0.25, y = 0.0 quarter-chord pivot): invariant at (0.25, 0.0)
    assert washed._raw.x_upper[10] == pytest.approx(0.25, rel=1e-6)
    assert washed._raw.y_upper[10] == pytest.approx(0.0, abs=1e-12)

    # Trailing edge moves upward (positive y) under positive washout
    assert np.max(washed.coordinates[1]) > 0.35


def test_apply_reflex_boundary_and_linear_ramp():
    """apply_reflex leaves x <= 0.70 unchanged and adds a linear ramp over x in (0.70, 1.0]."""
    coords = _make_symmetric_coords(n=20, name="REFLEX_BASE")
    airfoil = Airfoil(coords, n_points=9, smooth=False)
    airfoil._x = np.array([0.0, 0.35, 0.70, 0.85, 1.0, 1.0, 0.85, 0.70, 0.35, 0.0])
    airfoil._y = np.full(10, 0.01)

    reflexed_pos = airfoil.apply_reflex(3.0)
    assert reflexed_pos.name == "REFLEX_BASE_reflex_3.0pct"
    # Baseline y = 0.01; for percent = 3.0 (reflex_amount = 0.03):
    # x = 0.0, 0.35, 0.70 (boundary of x > 0.70) -> unchanged at 0.01
    # x = 0.85 (t = 0.15 / 0.30 = 0.5) -> 0.01 + 0.03 * 0.5 = 0.025
    # x = 1.00 (t = 0.30 / 0.30 = 1.0) -> 0.01 + 0.03 * 1.0 = 0.040
    assert reflexed_pos._raw.y_upper == pytest.approx(
        np.array([0.01, 0.01, 0.01, 0.025, 0.04]), rel=1e-6
    )
    assert reflexed_pos.coordinates[1][4] == pytest.approx(0.04, rel=1e-6)

    # Negative reflex deflects trailing edge downward
    reflexed_neg = airfoil.apply_reflex(-1.5)
    assert reflexed_neg._raw.y_upper == pytest.approx(
        np.array([0.01, 0.01, 0.01, 0.0025, -0.005]), rel=1e-6
    )


def test_blend_clamp_branches_and_asymmetric_weights():
    """blend clamps fraction to [0.0, 1.0] and weights self by (1 - fraction), other by fraction."""
    af_thin = Airfoil(
        _make_symmetric_coords(n=40, thickness=0.08, name="THIN"),
        n_points=80,
        smooth=False,
    )
    af_thick = Airfoil(
        _make_symmetric_coords(n=40, thickness=0.20, name="THICK"),
        n_points=80,
        smooth=False,
    )

    # Lower clamp branch: fraction = -0.4 -> clamped to 0.0 (self wins)
    blend_low = af_thin.blend(af_thick, -0.4)
    blend_zero = af_thin.blend(af_thick, 0.0)
    assert blend_low.name == "THIN_blend_0.00"
    assert blend_low.coordinates[1] == pytest.approx(
        blend_zero.coordinates[1], rel=1e-6
    )

    # Upper clamp branch: fraction = 1.6 -> clamped to 1.0 (other wins)
    blend_high = af_thin.blend(af_thick, 1.6)
    blend_one = af_thin.blend(af_thick, 1.0)
    assert blend_high.name == "THIN_blend_1.00"
    assert blend_high.coordinates[1] == pytest.approx(
        blend_one.coordinates[1], rel=1e-6
    )

    # Asymmetric interior fraction = 0.25: 0.75 * thin + 0.25 * thick
    blend_qtr = af_thin.blend(af_thick, 0.25)
    assert blend_qtr.name == "THIN_blend_0.25"
    expected_raw_upper = 0.75 * af_thin._y[:40] + 0.25 * af_thick._y[:40]
    assert blend_qtr._raw.y_upper == pytest.approx(expected_raw_upper, rel=1e-6)


def test_blend_resamples_mismatched_point_counts():
    """blend linearly interpolates other when len(self._x) != len(other._x)."""
    af_120 = Airfoil(
        _make_symmetric_coords(n=40, thickness=0.10, name="AF120"),
        n_points=120,
        smooth=False,
    )
    af_60 = Airfoil(
        _make_symmetric_coords(n=40, thickness=0.22, name="AF60"),
        n_points=60,
        smooth=False,
    )

    blended = af_120.blend(af_60, 0.25)
    x_b, y_b = blended.coordinates

    assert len(x_b) == 120
    assert len(y_b) == 120
    # Peak upper y scales as 0.75 * (0.10 / 2) + 0.25 * (0.22 / 2) = 0.0375 + 0.0275 = 0.065
    assert np.max(y_b) == pytest.approx(0.065, rel=1e-2)


def test_offset_inward_exact_normal_displacement_and_te_truncation():
    """offset_inward shifts horizontal upper segments by -thickness/chord and truncates crossed TE points."""
    coords = _make_symmetric_coords(n=20, name="HEX")
    airfoil = Airfoil(coords, n_points=11, smooth=False)
    airfoil._x = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
    airfoil._y = np.array(
        [0.0, 0.10, 0.10, 0.10, 0.10, 0.0, -0.10, -0.10, -0.10, -0.10, 0.0]
    )

    # t_norm = 0.5 / 25.0 = 0.02; horizontal upper interior points at x=0.4, 0.6 shift y from 0.10 to 0.08
    offset = airfoil.offset_inward(0.5, 25.0)
    assert offset.name == "HEX_offset_0.500in"
    assert offset._raw.x_upper[2] == pytest.approx(0.4, rel=1e-6)
    assert offset._raw.y_upper[2] == pytest.approx(0.08, rel=1e-6)
    assert offset._raw.x_upper[3] == pytest.approx(0.6, rel=1e-6)
    assert offset._raw.y_upper[3] == pytest.approx(0.08, rel=1e-6)

    # Profile where TE crossing occurs at i = 1 (cut_u = 5 < nu = 6), triggering array truncation
    airfoil._x = np.array([0.0, 0.2, 0.4, 0.6, 0.9, 1.0, 0.9, 0.6, 0.4, 0.2, 0.0])
    airfoil._y = np.array(
        [0.0, 0.10, 0.10, 0.08, 0.08, 0.0, -0.01, -0.41, -0.41, -0.20, 0.0]
    )
    truncated = airfoil.offset_inward(5.0, 10.0)
    assert len(truncated._raw.x_upper) == 5
    assert len(truncated._raw.x_lower) == 5
    assert len(truncated.coordinates[0]) == 9

    # Exact tie at TE (i = 0: yu_off[5] == yl_off[0]) with crossing at i = 1 (yu_off[4] < yl_off[1]):
    # '<=' breaks at i = 0 (keeping all 6 upper/lower points), whereas '<' would continue to i = 1 and truncate to 5.
    airfoil._x = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
    airfoil._y = np.array(
        [0.0, 0.10, 0.10, 0.08, 0.08, 0.0, -0.08, -0.80, -0.80, -0.20, 0.0]
    )
    te_tie_i0 = airfoil.offset_inward(5.0, 10.0)
    expected_te_y = -0.2 / np.sqrt(0.2**2 + (-0.08) ** 2) * 0.5
    assert len(te_tie_i0._raw.x_upper) == 6
    assert len(te_tie_i0._raw.x_lower) == 6
    assert len(te_tie_i0.coordinates[0]) == 11
    assert te_tie_i0._raw.y_upper[-1] == pytest.approx(expected_te_y, abs=1e-9)
    assert te_tie_i0._raw.y_lower[-1] == pytest.approx(expected_te_y, abs=1e-9)

    # Exact tie at i = 1 (yu_off[4] == yl_off[1] == 0.0) while i = 0 stays uncrossed (yu_off[5] > yl_off[0]):
    # '<=' detects collapse at i = 1 and truncates to 5 points, whereas '<' would miss the tie and keep 6.
    airfoil._x = np.array([0.0, 0.2, 0.4, 0.6, 0.95, 1.0, 0.80, 0.6, 0.4, 0.2, 0.0])
    airfoil._y = np.array(
        [0.0, 0.50, 0.50, 0.0, 0.05, 0.0, 0.05, 0.0, 0.05, -0.20, 0.0]
    )
    te_tie_i1 = airfoil.offset_inward(0.5, 10.0)
    assert len(te_tie_i1._raw.x_upper) == 5
    assert len(te_tie_i1._raw.x_lower) == 5
    assert len(te_tie_i1.coordinates[0]) == 9
    assert te_tie_i1._raw.y_upper[-1] == pytest.approx(0.0, abs=1e-9)
    assert te_tie_i1._raw.y_lower[-1] == pytest.approx(0.0, abs=1e-9)


def test_scale_and_cadquery_wire_and_face_geometry():
    """scale multiplies coordinates by chord; get_cadquery_wire and get_cadquery_face build valid planar shapes."""
    airfoil = Airfoil(
        _make_symmetric_coords(n=25, thickness=0.12, name="CAD_AF"),
        n_points=51,
        smooth=False,
    )

    x_s, y_s = airfoil.scale(25.0)
    assert x_s == pytest.approx(airfoil._x * 25.0, rel=1e-6)
    assert y_s == pytest.approx(airfoil._y * 25.0, rel=1e-6)

    x_20, y_20 = airfoil.scale(20.0)
    wire_20 = airfoil.get_cadquery_wire(20.0)
    face_20 = airfoil.get_cadquery_face(20.0)
    face_40 = airfoil.get_cadquery_face(40.0)

    assert isinstance(wire_20, cq.Wire)
    assert wire_20.isValid()
    bb = wire_20.BoundingBox()
    expected_x_span = float(np.max(x_20) - np.min(x_20))
    expected_y_span = float(np.max(y_20) - np.min(y_20))
    assert bb.xmax - bb.xmin == pytest.approx(expected_x_span, rel=1e-2)
    assert bb.ymax - bb.ymin == pytest.approx(expected_y_span, rel=1e-2)
    assert bb.zmin == pytest.approx(0.0, abs=1e-6)
    assert bb.zmax == pytest.approx(0.0, abs=1e-6)
    for vertex in wire_20.Vertices():
        assert vertex.Z == pytest.approx(0.0, abs=1e-12)

    assert isinstance(face_20, cq.Face)
    assert face_20.isValid()
    shoelace_area_20 = float(
        0.5 * np.abs(np.dot(x_20, np.roll(y_20, -1)) - np.dot(y_20, np.roll(x_20, -1)))
    )
    assert face_20.Area() == pytest.approx(shoelace_area_20, rel=2e-2)
    # Doubling chord quadruples 2D face area
    assert face_40.Area() / face_20.Area() == pytest.approx(4.0, rel=1e-3)


def test_factory_constants_caching_and_error_paths(
    factory: AirfoilFactory, tmp_path: Path
):
    """Pin AirfoilFactory file mapping, cache key identity, unknown type ValueError, and missing FileNotFoundError."""
    assert AirfoilFactory.AIRFOIL_FILES == {
        AirfoilType.RONCZ_R1145MS: "roncz_r1145ms.dat",
        AirfoilType.EPPLER_1230_MOD: "eppler_1230_mod.dat",
        AirfoilType.GU25_5_11_8: "gu25_5_11_8.dat",
    }
    assert isinstance(airfoil_factory, AirfoilFactory)
    assert airfoil_factory.data_dir == AirfoilFactory.DATA_DIR

    af_a = factory.load(AirfoilType.RONCZ_R1145MS, n_points=60, smooth=True)
    af_b = factory.load(AirfoilType.RONCZ_R1145MS, n_points=60, smooth=True)
    af_diff_pts = factory.load(AirfoilType.RONCZ_R1145MS, n_points=80, smooth=True)
    af_diff_smooth = factory.load(AirfoilType.RONCZ_R1145MS, n_points=60, smooth=False)
    af_diff_type = factory.load(AirfoilType.EPPLER_1230_MOD, n_points=60, smooth=True)

    assert af_a is af_b
    assert af_a is not af_diff_pts
    assert af_a is not af_diff_smooth
    assert af_a is not af_diff_type

    with pytest.raises(ValueError, match="Unknown airfoil type"):
        factory.load("not_an_airfoil_type")  # type: ignore[arg-type]

    empty_factory = AirfoilFactory(data_dir=tmp_path)
    with pytest.raises(FileNotFoundError, match="Airfoil data file not found"):
        empty_factory.load(AirfoilType.RONCZ_R1145MS)

    with pytest.raises(FileNotFoundError, match="Airfoil data file not found"):
        factory.load_from_file(tmp_path / "nonexistent.dat")


def test_parse_selig_format_and_minimum_point_boundary(
    factory: AirfoilFactory, tmp_path: Path
):
    """_parse_selig rejects <10 points, accepts >=10 points, and reverses upper surface to run LE -> TE."""
    pts_10 = [
        (1.0, 0.0),
        (0.75, 0.04),
        (0.50, 0.06),
        (0.25, 0.05),
        (0.0, 0.0),
        (0.20, -0.02),
        (0.40, -0.03),
        (0.60, -0.025),
        (0.80, -0.01),
        (1.0, 0.0),
    ]

    # 9 coordinate lines (< 10 boundary): must raise ValueError
    selig_9 = tmp_path / "selig_9.dat"
    selig_9.write_text(
        "SELIG_9\n" + "\n".join(f"{x:.4f} {y:.4f}" for x, y in pts_10[:9]) + "\n"
    )
    with pytest.raises(ValueError, match=r"Insufficient coordinate data \(Selig\)"):
        factory.load_from_file(selig_9)

    # Exact 10 coordinate lines (with comments, blank lines, and non-numeric lines ignored)
    selig_10 = tmp_path / "selig_10.dat"
    selig_10.write_text(
        "  SELIG_10_NAME  \n# comment line\n\ninvalid_x invalid_y\nsingle_token\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in pts_10)
        + "\n"
    )
    af = factory.load_from_file(selig_10, n_points=25, smooth=False)
    assert af.name == "SELIG_10_NAME"
    # Upper surface is reversed from TE->LE to LE->TE
    assert af._raw.x_upper == pytest.approx(
        np.array([0.0, 0.25, 0.50, 0.75, 1.0]), rel=1e-6
    )
    assert af._raw.y_upper == pytest.approx(
        np.array([0.0, 0.05, 0.06, 0.04, 0.0]), rel=1e-6
    )
    assert af._raw.x_lower == pytest.approx(
        np.array([0.0, 0.20, 0.40, 0.60, 0.80, 1.0]), rel=1e-6
    )
    assert af._raw.y_lower == pytest.approx(
        np.array([0.0, -0.02, -0.03, -0.025, -0.01, 0.0]), rel=1e-6
    )


def test_parse_lednicer_format_and_count_boundaries(
    factory: AirfoilFactory, tmp_path: Path
):
    """_parse_lednicer enforces >=5 points per surface and _parse_dat_file bounds Lednicer headers to [5, 500]."""
    upper_5 = [(0.0, 0.0), (0.25, 0.05), (0.50, 0.06), (0.75, 0.03), (1.0, 0.0)]
    lower_5 = [(0.0, 0.0), (0.25, -0.02), (0.50, -0.03), (0.75, -0.01), (1.0, 0.0)]

    # 4 upper points (< 5 boundary): must raise ValueError
    led_4u = tmp_path / "led_4u.dat"
    led_4u.write_text(
        "LED_4U\n5 5\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in upper_5[:4])
        + "\n\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in lower_5)
        + "\n"
    )
    with pytest.raises(ValueError, match=r"Insufficient coordinate data \(Lednicer\)"):
        factory.load_from_file(led_4u)

    # 4 lower points (< 5 boundary): must raise ValueError
    led_4l = tmp_path / "led_4l.dat"
    led_4l.write_text(
        "LED_4L\n5 5\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in upper_5)
        + "\n\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in lower_5[:4])
        + "\n"
    )
    with pytest.raises(ValueError, match=r"Insufficient coordinate data \(Lednicer\)"):
        factory.load_from_file(led_4l)

    # Exact 5 upper and 5 lower points with float-formatted count line "5. 5."
    led_5 = tmp_path / "led_5.dat"
    led_5.write_text(
        "LED_5_VALID\n5. 5.\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in upper_5)
        + "\n\n"
        + "\n".join(f"{x:.4f} {y:.4f}" for x, y in lower_5)
        + "\n"
    )
    af = factory.load_from_file(led_5, n_points=25, smooth=False)
    assert af.name == "LED_5_VALID"
    assert af._raw.x_upper == pytest.approx(
        np.array([0.0, 0.25, 0.50, 0.75, 1.0]), rel=1e-6
    )
    assert af._raw.y_upper == pytest.approx(
        np.array([0.0, 0.05, 0.06, 0.03, 0.0]), rel=1e-6
    )
    assert af._raw.x_lower == pytest.approx(
        np.array([0.0, 0.25, 0.50, 0.75, 1.0]), rel=1e-6
    )
    assert af._raw.y_lower == pytest.approx(
        np.array([0.0, -0.02, -0.03, -0.01, 0.0]), rel=1e-6
    )

    # Count 501 (> 500 upper limit) is NOT detected as Lednicer and falls through to Selig
    over_500 = tmp_path / "over_500.dat"
    over_500.write_text("OVER_500\n501 501\n0.0 0.0\n1.0 0.0\n")
    with pytest.raises(ValueError, match=r"Insufficient coordinate data \(Selig\)"):
        factory.load_from_file(over_500)


def test_get_canard_airfoil_safety_override_and_warning(
    factory: AirfoilFactory, monkeypatch: pytest.MonkeyPatch
):
    """get_canard_airfoil returns Roncz R1145MS silently by default and warns+overrides if config is altered."""
    canard_default = factory.get_canard_airfoil()
    assert canard_default.name == "RONCZ R1145MS (Rain-Safe Canard Airfoil)"

    monkeypatch.setattr(config.airfoils, "canard", AirfoilType.GU25_5_11_8)
    with pytest.warns(
        UserWarning, match="SAFETY: Overriding canard airfoil to Roncz R1145MS"
    ):
        canard_override = factory.get_canard_airfoil()
    assert canard_override is canard_default


def test_get_wing_airfoil_reflex_toggle_and_zero_boundary(
    factory: AirfoilFactory, monkeypatch: pytest.MonkeyPatch
):
    """get_wing_airfoil applies config.airfoils.wing_reflex_percent only when apply_reflex=True and percent > 0."""
    assert config.airfoils.wing_reflex_percent == 2.5

    wing_base = factory.get_wing_airfoil(apply_reflex=False)
    wing_reflexed = factory.get_wing_airfoil(apply_reflex=True)

    assert wing_base.name == "EPPLER 1230 MODIFIED (Main Wing - Reflex Applied)"
    assert (
        wing_reflexed.name
        == "EPPLER 1230 MODIFIED (Main Wing - Reflex Applied)_reflex_2.5pct"
    )

    x_base, y_base = wing_base.coordinates
    y_raw_ref = np.concatenate(
        [wing_reflexed._raw.y_upper, wing_reflexed._raw.y_lower[::-1]]
    )
    te_base = int(np.argmax(x_base))
    t_te = (x_base[te_base] - 0.70) / (1.0 - 0.70)
    assert y_raw_ref[te_base] - y_base[te_base] == pytest.approx(0.025 * t_te, abs=1e-9)
    assert (y_raw_ref[te_base] - y_base[te_base]) / t_te == pytest.approx(
        0.025, abs=1e-9
    )
    expected_shift = np.where(
        x_base > 0.70, 0.025 * (x_base - 0.70) / (1.0 - 0.70), 0.0
    )
    assert y_raw_ref - y_base == pytest.approx(expected_shift, abs=1e-9)

    # Boundary wing_reflex_percent == 0.0: strict '> 0' skips apply_reflex
    monkeypatch.setattr(config.airfoils, "wing_reflex_percent", 0.0)
    wing_zero_pct = factory.get_wing_airfoil(apply_reflex=True)
    assert wing_zero_pct is wing_base
