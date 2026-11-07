"""Direct tests for core/jig_factory.py (JigFactory assembly aids and tooling)."""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import pytest

from config import config
from core import jig_factory
from core.base import AircraftComponent
from core.jig_factory import JigFactory
from core.manufacturing import JigFactory as ManufacturingJigFactory


class _BoxWingComponent(AircraftComponent):
    """Minimal concrete AircraftComponent for fast incidence-cradle testing."""

    def __init__(self, name: str = "box_wing"):
        super().__init__(name, "Lightweight box wing for jig tests")

    def _build_geometry(self) -> cq.Workplane:
        self._geometry = cq.Workplane("XY").box(100.0, 50.0, 5.0)
        return self._geometry

    def export_dxf(self, output_path: Path) -> Path:
        return Path(output_path) / f"{self.name}.dxf"

    def manufacturing_plan(self, output_path: Path) -> dict:
        return {}


@pytest.fixture(scope="module")
def ungenerated_wing() -> _BoxWingComponent:
    return _BoxWingComponent("ungenerated_wing")


@pytest.fixture(scope="module")
def generated_wing() -> _BoxWingComponent:
    comp = _BoxWingComponent("generated_wing")
    comp.generate_geometry()
    return comp


@pytest.fixture(scope="module")
def default_wing_cradle(ungenerated_wing: _BoxWingComponent) -> cq.Workplane:
    return JigFactory.generate_incidence_cradle(
        ungenerated_wing,
        station_bl=config.geometry.wing_root_bl,
        incidence_angle=config.geometry.wing_incidence,
    )


# ---------------------------------------------------------------------------
# Group 1: Module exports and class-level geometry constants
# ---------------------------------------------------------------------------


def test_jig_factory_constants_and_manufacturing_reexport():
    assert ManufacturingJigFactory is JigFactory
    assert jig_factory.__all__ == ["JigFactory"]
    assert JigFactory.CRADLE_WIDTH == pytest.approx(4.0, abs=1e-9)
    assert JigFactory.CRADLE_HEIGHT == pytest.approx(5.0, abs=1e-9)
    assert JigFactory.CRADLE_LENGTH == pytest.approx(20.0, abs=1e-9)
    assert JigFactory.WALL_THICKNESS == pytest.approx(0.25, abs=1e-9)
    assert JigFactory.CLEARANCE == pytest.approx(0.02, abs=1e-9)


# ---------------------------------------------------------------------------
# Group 2: Incidence cradle generation, scaling, rotation, and fallbacks
# ---------------------------------------------------------------------------


def test_incidence_cradle_default_solid_volume_and_bbox(
    default_wing_cradle: cq.Workplane,
):
    assert isinstance(default_wing_cradle, cq.Workplane)
    solid = default_wing_cradle.val()
    bb = solid.BoundingBox()

    length = JigFactory.CRADLE_LENGTH
    width = JigFactory.CRADLE_WIDTH
    height = JigFactory.CRADLE_HEIGHT + 3.0
    wall = JigFactory.WALL_THICKNESS

    pocket_vol = (
        (length - 2.0 * wall - 1.0) * (width - 2.0 * wall) * (height - wall - 0.5)
    )
    expected_vol = length * width * height - pocket_vol

    assert solid.isValid()
    assert solid.Volume() > 0.0
    assert solid.Volume() == pytest.approx(expected_vol, rel=1e-4)
    assert bb.xmin == pytest.approx(0.0, abs=1e-4)
    assert bb.xmax == pytest.approx(length, abs=1e-4)
    assert bb.ymin == pytest.approx(0.0, abs=1e-4)
    assert bb.ymax == pytest.approx(width, abs=1e-4)
    assert bb.zmin == pytest.approx(0.0, abs=1e-4)
    assert bb.zmax == pytest.approx(height, abs=1e-4)


def test_incidence_cradle_scales_with_width_and_base_height(
    ungenerated_wing: _BoxWingComponent,
):
    custom_width = 6.0
    custom_base = 6.5
    expected_height = custom_base + 3.0
    length = JigFactory.CRADLE_LENGTH
    wall = JigFactory.WALL_THICKNESS

    cradle = JigFactory.generate_incidence_cradle(
        ungenerated_wing,
        station_bl=79.0,
        incidence_angle=0.0,
        cradle_width=custom_width,
        base_height=custom_base,
    )
    solid = cradle.val()
    bb = solid.BoundingBox()

    pocket_vol = (
        (length - 2.0 * wall - 1.0)
        * (custom_width - 2.0 * wall)
        * (expected_height - wall - 0.5)
    )
    expected_vol = length * custom_width * expected_height - pocket_vol

    assert solid.isValid()
    assert bb.xlen == pytest.approx(length, abs=1e-4)
    assert bb.ylen == pytest.approx(custom_width, abs=1e-4)
    assert bb.zlen == pytest.approx(expected_height, abs=1e-4)
    assert solid.Volume() == pytest.approx(expected_vol, rel=1e-4)

    # When cradle_width <= 1.5, pocket_width = width - 2*wall <= 1.0 so the pocket cut is skipped
    narrow_width = 1.2
    narrow = JigFactory.generate_incidence_cradle(
        ungenerated_wing,
        station_bl=23.3,
        incidence_angle=0.0,
        cradle_width=narrow_width,
        base_height=5.0,
    ).val()
    assert narrow.isValid()
    assert narrow.BoundingBox().ylen == pytest.approx(narrow_width, abs=1e-4)
    assert narrow.Volume() == pytest.approx(length * narrow_width * 8.0, rel=1e-4)


def test_incidence_cradle_rotation_and_small_angle_threshold(
    ungenerated_wing: _BoxWingComponent,
    default_wing_cradle: cq.Workplane,
):
    length = JigFactory.CRADLE_LENGTH
    width = JigFactory.CRADLE_WIDTH
    base_height = JigFactory.CRADLE_HEIGHT
    height = base_height + 3.0
    pivot_x = length * 0.25
    pivot_z = base_height

    # Angles with abs(incidence_angle) <= 0.001 bypass the rotation branch
    sub_threshold = JigFactory.generate_incidence_cradle(
        ungenerated_wing,
        station_bl=23.0,
        incidence_angle=0.0005,
    ).val()
    assert sub_threshold.isValid()
    assert sub_threshold.BoundingBox().zlen == pytest.approx(height, abs=1e-5)
    assert sub_threshold.Volume() == pytest.approx(
        default_wing_cradle.val().Volume(), rel=1e-6
    )

    low_x_slab = (
        cq.Workplane("XY")
        .box(5.0, width, 40.0, centered=False)
        .translate((0.0, 0.0, -20.0))
    )
    high_x_slab = (
        cq.Workplane("XY")
        .box(5.0, width, 40.0, centered=False)
        .translate((length - 5.0, 0.0, -20.0))
    )

    # Rotate about +Y by -incidence_angle around (pivot_x, 0, pivot_z) = (0.25 * length, 0, base_height)
    for angle_deg in (config.geometry.canard_incidence, -8.0, 8.0):
        rotated_wp = JigFactory.generate_incidence_cradle(
            ungenerated_wing,
            station_bl=0.0,
            incidence_angle=angle_deg,
        )
        rotated = rotated_wp.val()
        bb = rotated.BoundingBox()
        rad = math.radians(abs(angle_deg))
        expected_xlen = length * math.cos(rad) + height * math.sin(rad)
        expected_zlen = height * math.cos(rad) + length * math.sin(rad)

        if angle_deg > 0.0:
            expected_xmin = (
                pivot_x - pivot_x * math.cos(rad) - (height - pivot_z) * math.sin(rad)
            )
            expected_xmax = (
                pivot_x + (length - pivot_x) * math.cos(rad) + pivot_z * math.sin(rad)
            )
            expected_zmin = pivot_z - pivot_x * math.sin(rad) - pivot_z * math.cos(rad)
            expected_zmax = (
                pivot_z
                + (length - pivot_x) * math.sin(rad)
                + (height - pivot_z) * math.cos(rad)
            )
        else:
            expected_xmin = pivot_x - pivot_x * math.cos(rad) - pivot_z * math.sin(rad)
            expected_xmax = (
                pivot_x
                + (length - pivot_x) * math.cos(rad)
                + (height - pivot_z) * math.sin(rad)
            )
            expected_zmin = (
                pivot_z - (length - pivot_x) * math.sin(rad) - pivot_z * math.cos(rad)
            )
            expected_zmax = (
                pivot_z + pivot_x * math.sin(rad) + (height - pivot_z) * math.cos(rad)
            )

        assert rotated.isValid()
        assert rotated.Volume() > 0.0
        assert bb.ylen == pytest.approx(width, abs=1e-4)
        assert bb.xmin == pytest.approx(expected_xmin, abs=1e-3)
        assert bb.xmax == pytest.approx(expected_xmax, abs=1e-3)
        assert bb.zmin == pytest.approx(expected_zmin, abs=1e-3)
        assert bb.zmax == pytest.approx(expected_zmax, abs=1e-3)
        assert bb.xlen == pytest.approx(expected_xlen, abs=1e-3)
        assert bb.zlen == pytest.approx(expected_zlen, abs=1e-3)
        assert bb.zlen > height

        # Compare low-x end (x in [0, 5]) vs high-x end (x in [15, 20]) to pin rotation direction and 0.25*length pivot
        low_x_end = rotated_wp.intersect(low_x_slab).val()
        high_x_end = rotated_wp.intersect(high_x_slab).val()
        low_bb = low_x_end.BoundingBox()
        high_bb = high_x_end.BoundingBox()

        if angle_deg > 0.0:
            assert high_bb.zmin > low_bb.zmin
            assert high_bb.zmax > low_bb.zmax
            assert high_x_end.Center().z > low_x_end.Center().z
            assert (bb.zmax - height) > abs(bb.zmin)
        else:
            assert high_bb.zmin < low_bb.zmin
            assert high_bb.zmax < low_bb.zmax
            assert high_x_end.Center().z < low_x_end.Center().z
            assert abs(bb.zmin) > (bb.zmax - height)


def test_incidence_cradle_component_fallbacks_and_determinism(
    ungenerated_wing: _BoxWingComponent,
    generated_wing: _BoxWingComponent,
    default_wing_cradle: cq.Workplane,
):
    # None triggers AttributeError on .geometry; ungenerated triggers ValueError;
    # generated triggers Exception in wing_geom.section(slice_plane); all fall back cleanly.
    from_none = JigFactory.generate_incidence_cradle(
        None,  # type: ignore[arg-type]
        station_bl=config.geometry.wing_root_bl,
        incidence_angle=config.geometry.wing_incidence,
    ).val()
    from_generated = JigFactory.generate_incidence_cradle(
        generated_wing,
        station_bl=config.geometry.wing_root_bl,
        incidence_angle=config.geometry.wing_incidence,
    ).val()
    repeat_ungenerated = JigFactory.generate_incidence_cradle(
        ungenerated_wing,
        station_bl=config.geometry.wing_root_bl,
        incidence_angle=config.geometry.wing_incidence,
    ).val()

    ref_vol = default_wing_cradle.val().Volume()
    for solid in (from_none, from_generated, repeat_ungenerated):
        assert solid.isValid()
        assert solid.Volume() == pytest.approx(ref_vol, rel=1e-6)


# ---------------------------------------------------------------------------
# Group 3: Internal helper methods (_add_parametric_contour, _add_structural_features, _add_alignment_marks)
# ---------------------------------------------------------------------------


def test_helper_add_parametric_contour_parabolic_cut():
    length = 20.0
    width = 4.0
    base_height = 5.0
    height = base_height + 3.0

    # Workplane("XZ").extrude(width) extrudes along the XZ normal (-Y, i.e. Y in [-width, 0]).
    # On a box translated into Y in [-width, 0], the cutter removes the upper region down to
    # base_height + y_lower + CLEARANCE, where y_lower = -0.02 * length * 4 * t * (1 - t).
    neg_y_box = (
        cq.Workplane("XY")
        .box(length, width, height, centered=False)
        .translate((0.0, -width, 0.0))
    )
    contoured = JigFactory._add_parametric_contour(
        neg_y_box, length, width, height, base_height
    ).val()
    bb = contoured.BoundingBox()

    # Integral of 4*t*(1 - t) on [0, 1] is 2/3, so mean y_lower is -0.02 * length * (2/3)
    mean_profile_z = base_height + JigFactory.CLEARANCE - (0.04 / 3.0) * length
    expected_vol = length * width * mean_profile_z

    assert contoured.isValid()
    assert bb.zmax == pytest.approx(base_height + JigFactory.CLEARANCE, abs=1e-3)
    assert contoured.Volume() == pytest.approx(expected_vol, rel=5e-3)


def test_helper_add_structural_features_pocket_and_guard_thresholds():
    wall = JigFactory.WALL_THICKNESS
    length, width, height = 10.0, 3.0, 4.0
    box = cq.Workplane("XY").box(length, width, height, centered=False)

    hollowed = JigFactory._add_structural_features(box, length, width, height).val()
    pocket_vol = (
        (length - 2.0 * wall - 1.0) * (width - 2.0 * wall) * (height - wall - 0.5)
    )
    assert hollowed.isValid()
    assert hollowed.Volume() == pytest.approx(
        length * width * height - pocket_vol, rel=1e-5
    )

    # Guard requires pocket_length > 2, pocket_width > 1, and pocket_height > 1
    for l_in, w_in, h_in in ((3.5, 3.0, 4.0), (10.0, 1.5, 4.0), (10.0, 3.0, 1.75)):
        b = cq.Workplane("XY").box(l_in, w_in, h_in, centered=False)
        unchanged = JigFactory._add_structural_features(b, l_in, w_in, h_in).val()
        assert unchanged.isValid()
        assert unchanged.Volume() == pytest.approx(l_in * w_in * h_in, rel=1e-6)


def test_helper_add_alignment_marks_cuts_top_at_z10_and_catches_errors():
    # Centerline mark is extruded -0.05 from Z=10 (Z in [9.95, 10.0]) with rect(length - 1, 0.03)
    length, width, height = 12.0, 4.0, 10.0
    tall_box = cq.Workplane("XY").box(length, width, height, centered=False)
    marked = JigFactory._add_alignment_marks(
        tall_box, length, width, station_bl=23.3
    ).val()

    groove_vol = (length - 1.0) * 0.03 * 0.05
    assert marked.isValid()
    assert marked.Volume() == pytest.approx(
        length * width * height - groove_vol, rel=1e-5
    )

    # When length <= 1.0, rect(length - 1, mark_width) fails inside try/except and returns cradle unchanged
    short_box = cq.Workplane("XY").box(1.0, 2.0, 10.0, centered=False)
    fallback = JigFactory._add_alignment_marks(
        short_box, length=1.0, width=2.0, station_bl=0.0
    ).val()
    assert fallback.isValid()
    assert fallback.Volume() == pytest.approx(20.0, rel=1e-6)


# ---------------------------------------------------------------------------
# Group 4: Drill guides and vortilon templates
# ---------------------------------------------------------------------------


def test_generate_drill_guide_default_and_custom_dimensions():
    # AN3 (0.1875 in) and AN4 (0.250 in) standard drill guides
    for hole_d in (0.1875, 0.250):
        guide = JigFactory.generate_drill_guide(hole_d)
        assert isinstance(guide, cq.Workplane)
        solid = guide.val()
        bb = solid.BoundingBox()

        inner_d = hole_d + 0.005
        outer_d = hole_d + 0.125
        flange_d = hole_d * 3.0
        guide_len = 1.5
        flange_t = 0.25
        expected_vol = (math.pi / 4.0) * (
            (outer_d**2 - inner_d**2) * guide_len
            + (flange_d**2 - inner_d**2) * flange_t
        )

        assert solid.isValid()
        assert solid.Volume() > 0.0
        assert solid.Volume() == pytest.approx(expected_vol, rel=1e-3)
        assert bb.xlen == pytest.approx(flange_d, abs=1e-4)
        assert bb.ylen == pytest.approx(flange_d, abs=1e-4)
        assert bb.zmin == pytest.approx(0.0, abs=1e-4)
        assert bb.zmax == pytest.approx(guide_len + flange_t, abs=1e-4)

    # Custom guide length, explicit flange diameter, and flange thickness
    custom = JigFactory.generate_drill_guide(
        hole_diameter=0.250,
        guide_length=2.25,
        flange_diameter=1.10,
        flange_thickness=0.375,
    ).val()
    bb_custom = custom.BoundingBox()
    assert custom.isValid()
    assert bb_custom.xlen == pytest.approx(1.10, abs=1e-4)
    assert bb_custom.ylen == pytest.approx(1.10, abs=1e-4)
    assert bb_custom.zlen == pytest.approx(2.25 + 0.375, abs=1e-4)

    # Out-of-range flange_diameter <= inner_d is completely removed by cutThruAll()
    undersized_flange = JigFactory.generate_drill_guide(
        hole_diameter=0.250,
        guide_length=1.5,
        flange_diameter=0.20,
        flange_thickness=0.25,
    ).val()
    bb_under = undersized_flange.BoundingBox()
    assert undersized_flange.isValid()
    assert bb_under.xlen == pytest.approx(0.250 + 0.125, abs=1e-4)
    assert bb_under.zlen == pytest.approx(1.5, abs=1e-4)


def test_generate_vortilon_template_default_and_scaled_dimensions():
    default_tpl = JigFactory.generate_vortilon_template()
    assert isinstance(default_tpl, cq.Workplane)
    solid = default_tpl.val()
    bb = solid.BoundingBox()

    # Default: height=2.5, base_length=3.0, thickness=0.125; handle is 1.5 x 1.0 at y in [-1, 0]
    expected_default_vol = (0.5 * 3.0 * 2.5 + 1.5 * 1.0) * 0.125
    assert solid.isValid()
    assert solid.Volume() == pytest.approx(expected_default_vol, rel=1e-5)
    assert bb.xmin == pytest.approx(0.0, abs=1e-5)
    assert bb.xmax == pytest.approx(3.0, abs=1e-5)
    assert bb.ymin == pytest.approx(-1.0, abs=1e-5)
    assert bb.ymax == pytest.approx(2.5, abs=1e-5)
    assert bb.zmin == pytest.approx(0.0, abs=1e-5)
    assert bb.zmax == pytest.approx(0.125, abs=1e-5)

    # Scaled template: height=4.0, base_length=5.0, thickness=0.25
    scaled = JigFactory.generate_vortilon_template(
        height=4.0, base_length=5.0, thickness=0.25
    ).val()
    bb_scaled = scaled.BoundingBox()
    expected_scaled_vol = (0.5 * 5.0 * 4.0 + 1.5 * 1.0) * 0.25
    assert scaled.isValid()
    assert scaled.Volume() == pytest.approx(expected_scaled_vol, rel=1e-5)
    assert bb_scaled.xlen == pytest.approx(5.0, abs=1e-5)
    assert bb_scaled.ylen == pytest.approx(4.0 + 1.0, abs=1e-5)
    assert bb_scaled.zlen == pytest.approx(0.25, abs=1e-5)

    # When base_length < 1.5, the 1.5-inch handle sets the overall X width
    narrow = JigFactory.generate_vortilon_template(
        height=2.0, base_length=1.0, thickness=0.125
    ).val()
    assert narrow.isValid()
    assert narrow.BoundingBox().xlen == pytest.approx(1.5, abs=1e-5)


def test_drill_guide_and_vortilon_template_are_deterministic():
    g1 = JigFactory.generate_drill_guide(0.1875).val()
    g2 = JigFactory.generate_drill_guide(0.1875).val()
    v1 = JigFactory.generate_vortilon_template(height=3.0, base_length=3.5).val()
    v2 = JigFactory.generate_vortilon_template(height=3.0, base_length=3.5).val()

    assert g1.Volume() == pytest.approx(g2.Volume(), abs=1e-9)
    assert g1.BoundingBox().zlen == pytest.approx(g2.BoundingBox().zlen, abs=1e-9)
    assert v1.Volume() == pytest.approx(v2.Volume(), abs=1e-9)
    assert v1.BoundingBox().ylen == pytest.approx(v2.BoundingBox().ylen, abs=1e-9)


# ---------------------------------------------------------------------------
# Group 5: Batch STL export (export_all_jigs) into pytest's tmp_path
# ---------------------------------------------------------------------------


def test_export_all_jigs_bug_pin_placeholder_missing_manufacturing_plan(
    tmp_path: Path,
):
    # Bug-pin: PlaceholderWing in JigFactory.export_all_jigs omits the abstract
    # AircraftComponent.manufacturing_plan method, so instantiating it after
    # output_dir creation currently raises TypeError.
    out_dir = tmp_path / "unpatched_jigs"
    with pytest.raises(TypeError, match="manufacturing_plan"):
        JigFactory.export_all_jigs(out_dir)
    assert out_dir.is_dir()


def test_export_all_jigs_writes_all_six_nonempty_stl_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        AircraftComponent,
        "manufacturing_plan",
        lambda self, output_path: {},
    )
    monkeypatch.setattr(
        AircraftComponent,
        "__abstractmethods__",
        frozenset({"_build_geometry", "export_dxf"}),
    )

    out_dir = tmp_path / "mfg" / "jigs"
    JigFactory.export_all_jigs(out_dir)

    expected_files = (
        "JIG_wing_root_BL23.stl",
        "JIG_wing_mid_BL79.stl",
        "JIG_canard_root.stl",
        "DRILL_GUIDE_AN3.stl",
        "DRILL_GUIDE_AN4.stl",
        "TEMPLATE_vortilon.stl",
    )
    assert out_dir.is_dir()
    for filename in expected_files:
        stl_path = out_dir / filename
        assert stl_path.is_file(), filename
        assert stl_path.stat().st_size > 80, filename
    assert sorted(p.name for p in out_dir.iterdir()) == sorted(expected_files)
