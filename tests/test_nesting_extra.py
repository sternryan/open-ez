"""Additional unit and invariant tests for core/nesting.py."""

from __future__ import annotations

import math
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import core.nesting as nesting_mod
from config import config
from core.nesting import (
    GrainConstraint,
    NestingPlanner,
    Outline,
    Placement,
)


class _FakeText:
    """Lightweight stand-in for an ezdxf Text entity."""

    def __init__(
        self, text: str, height: float | None, dxfattribs: dict[str, object]
    ) -> None:
        self.text = text
        self.height = height
        self.dxfattribs = dxfattribs
        self.pos: tuple[float, float] | None = None
        self.align: str | None = None

    def set_pos(self, pos: tuple[float, float], align: str | None = None) -> _FakeText:
        self.pos = pos
        self.align = align
        return self


class _FakeEntity:
    """Lightweight stand-in for a source DXF graphic entity."""

    transform = True

    def __init__(self, tag: str = "outline_entity") -> None:
        self.tag = tag
        self.rotations: list[float] = []
        self.translations: list[tuple[float, float, float]] = []

    def copy(self) -> _FakeEntity:
        cloned = _FakeEntity(tag=self.tag)
        cloned.rotations = list(self.rotations)
        cloned.translations = list(self.translations)
        return cloned

    def rotate(self, angle_rad: float) -> None:
        self.rotations.append(angle_rad)

    def translate(self, dx: float, dy: float, dz: float) -> None:
        self.translations.append((dx, dy, dz))


class _FakeModelspace:
    """Captures entities emitted by NestingPlanner during DXF export."""

    def __init__(self, source_entities: list[_FakeEntity] | None = None) -> None:
        self._source_entities = list(source_entities or [])
        self.polylines: list[
            tuple[list[tuple[float, float]], bool, dict[str, object]]
        ] = []
        self.circles: list[tuple[tuple[float, float], float, dict[str, object]]] = []
        self.lines: list[
            tuple[tuple[float, float], tuple[float, float], dict[str, object]]
        ] = []
        self.texts: list[_FakeText] = []
        self.added_entities: list[_FakeEntity] = []

    def __iter__(self):
        return iter(self._source_entities)

    def add_lwpolyline(
        self,
        points: list[tuple[float, float]],
        close: bool = False,
        dxfattribs: dict[str, object] | None = None,
    ) -> None:
        self.polylines.append((list(points), close, dict(dxfattribs or {})))

    def add_circle(
        self,
        center: tuple[float, float],
        radius: float,
        dxfattribs: dict[str, object] | None = None,
    ) -> None:
        self.circles.append((center, radius, dict(dxfattribs or {})))

    def add_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        dxfattribs: dict[str, object] | None = None,
    ) -> None:
        self.lines.append((start, end, dict(dxfattribs or {})))

    def add_text(
        self,
        text: str,
        height: float | None = None,
        dxfattribs: dict[str, object] | None = None,
    ) -> _FakeText:
        entry = _FakeText(text, height, dict(dxfattribs or {}))
        self.texts.append(entry)
        return entry

    def add_entity(self, entity: _FakeEntity) -> None:
        self.added_entities.append(entity)


class _FakeLayers:
    """Records layer definitions added to a target DXF document."""

    def __init__(self) -> None:
        self.created: dict[str, int | None] = {}

    def add(self, name: str, color: int | None = None) -> None:
        self.created[name] = color


class _FakeDoc:
    """Lightweight stand-in for an ezdxf Drawing."""

    def __init__(self, source_entities: list[_FakeEntity] | None = None) -> None:
        self.msp = _FakeModelspace(source_entities=source_entities)
        self.layers = _FakeLayers()
        self.saved_path: Path | None = None

    def modelspace(self) -> _FakeModelspace:
        return self.msp

    def saveas(self, path: Path) -> None:
        target = Path(path)
        target.write_text("0\nSECTION\n0\nENDSEC\n0\nEOF\n")
        self.saved_path = target


def test_placement_rotated_label_and_area_conservation():
    """90° rotation swaps placed dimensions, shifts label center, and conserves area."""
    outline = Outline(
        name="f22_half",
        source=Path("/tmp/f22_half.dxf"),
        width=14.0,
        height=6.0,
    )
    p_unrotated = Placement(
        outline=outline, sheet_index=0, origin=(2.5, 4.0), rotation=0.0
    )
    p_rotated = Placement(
        outline=outline, sheet_index=0, origin=(2.5, 4.0), rotation=90.0
    )

    # For rotation=90°, label_position is (x0 + height/2, y0 + width/2)
    cx_rot, cy_rot = p_rotated.label_position
    assert cx_rot == pytest.approx(2.5 + 6.0 / 2.0, abs=1e-9)
    assert cy_rot == pytest.approx(4.0 + 14.0 / 2.0, abs=1e-9)

    # In both orientations, label_position is the geometric center of the placed box
    for placement in (p_unrotated, p_rotated):
        x0, y0 = placement.origin
        assert placement.label_position[0] == pytest.approx(
            x0 + placement.placed_width / 2.0, abs=1e-9
        )
        assert placement.label_position[1] == pytest.approx(
            y0 + placement.placed_height / 2.0, abs=1e-9
        )

    # Area conservation under rotation
    assert p_rotated.placed_width * p_rotated.placed_height == pytest.approx(
        outline.width * outline.height, abs=1e-9
    )
    assert p_unrotated.placed_width * p_unrotated.placed_height == pytest.approx(
        p_rotated.placed_width * p_rotated.placed_height, abs=1e-9
    )


def test_placement_grain_direction_periodicity_and_notes():
    """grain_direction_on_sheet is modulo-180 periodic and grain_note covers all 4 branches."""
    # 1. NONE constraint always reports "No constraint" even if grain_angle is non-zero
    none_outline = Outline(
        name="foam_core",
        source=Path("/tmp/core.dxf"),
        width=8.0,
        height=4.0,
        grain_constraint=GrainConstraint.NONE,
        grain_angle=42.0,
    )
    p_none = Placement(outline=none_outline, sheet_index=0, origin=(0.0, 0.0))
    assert p_none.grain_note == "No constraint"

    # 2. Horizontal branch: |direction| < 5 or |direction - 180| < 5
    for angle, rot in ((0.0, 0.0), (4.5, 0.0), (86.0, 90.0)):
        o_horiz = Outline(
            name="longeron_splice",
            source=Path("/tmp/l.dxf"),
            width=8.0,
            height=2.0,
            grain_constraint=GrainConstraint.SPECIFIC,
            grain_angle=angle,
        )
        p_horiz = Placement(
            outline=o_horiz, sheet_index=0, origin=(0.0, 0.0), rotation=rot
        )
        assert p_horiz.grain_note == "Grain horizontal (0°)"

    # 3. Vertical branch: |direction - 90| < 5
    for angle, rot in ((90.0, 0.0), (86.0, 0.0), (4.0, 90.0)):
        o_vert = Outline(
            name="bulkhead_web",
            source=Path("/tmp/w.dxf"),
            width=8.0,
            height=4.0,
            grain_constraint=GrainConstraint.PERPENDICULAR,
            grain_angle=angle,
        )
        p_vert = Placement(
            outline=o_vert, sheet_index=0, origin=(0.0, 0.0), rotation=rot
        )
        assert p_vert.grain_note == "Grain vertical (90°)"

    # 4. Oblique branch and 180° modulo wrap invariant
    o_oblique = Outline(
        name="bias_ply",
        source=Path("/tmp/b.dxf"),
        width=10.0,
        height=5.0,
        grain_constraint=GrainConstraint.SPECIFIC,
        grain_angle=135.0,
    )
    p_oblique_0 = Placement(
        outline=o_oblique, sheet_index=0, origin=(0.0, 0.0), rotation=0.0
    )
    p_oblique_90 = Placement(
        outline=o_oblique, sheet_index=0, origin=(0.0, 0.0), rotation=90.0
    )
    assert p_oblique_0.grain_direction_on_sheet == pytest.approx(135.0, abs=1e-9)
    assert p_oblique_0.grain_note == "Grain at 135.0°"
    # (135 + 90) % 180 = 45.0
    assert p_oblique_90.grain_direction_on_sheet == pytest.approx(45.0, abs=1e-9)
    assert p_oblique_90.grain_note == "Grain at 45.0°"

    # Periodicity: shifting grain_angle by 180° yields identical sheet grain direction
    o_shifted = Outline(
        name="bias_ply_shifted",
        source=Path("/tmp/bs.dxf"),
        width=10.0,
        height=5.0,
        grain_constraint=GrainConstraint.SPECIFIC,
        grain_angle=135.0 + 180.0,
    )
    p_shifted = Placement(
        outline=o_shifted, sheet_index=0, origin=(0.0, 0.0), rotation=90.0
    )
    assert p_shifted.grain_direction_on_sheet == pytest.approx(
        p_oblique_90.grain_direction_on_sheet, abs=1e-9
    )


def test_compute_required_rotation_across_grain_constraints():
    """_compute_required_rotation honors PARALLEL, PERPENDICULAR, and SPECIFIC thresholds."""
    planner = NestingPlanner(
        stock_sheets=config.manufacturing.stock_sheets,
        sheet_grain_direction=0.0,
    )

    # PARALLEL: target = sheet_grain_direction (0°)
    parallel_aligned = Outline(
        name="par_0",
        source=Path("/tmp/p0.dxf"),
        width=10.0,
        height=4.0,
        grain_constraint=GrainConstraint.PARALLEL,
        primary_load_direction=0.0,
    )
    parallel_cross = Outline(
        name="par_90",
        source=Path("/tmp/p90.dxf"),
        width=10.0,
        height=4.0,
        grain_constraint=GrainConstraint.PARALLEL,
        primary_load_direction=90.0,
    )
    assert planner._compute_required_rotation(parallel_aligned) == pytest.approx(
        0.0, abs=1e-9
    )
    assert planner._compute_required_rotation(parallel_cross) == pytest.approx(
        90.0, abs=1e-9
    )

    # PERPENDICULAR: target = (sheet_grain_direction + 90) % 180 = 90°
    perp_load_0 = Outline(
        name="perp_0",
        source=Path("/tmp/perp0.dxf"),
        width=10.0,
        height=4.0,
        grain_constraint=GrainConstraint.PERPENDICULAR,
        primary_load_direction=0.0,
    )
    perp_load_90 = Outline(
        name="perp_90",
        source=Path("/tmp/perp90.dxf"),
        width=10.0,
        height=4.0,
        grain_constraint=GrainConstraint.PERPENDICULAR,
        primary_load_direction=90.0,
    )
    assert planner._compute_required_rotation(perp_load_0) == pytest.approx(
        90.0, abs=1e-9
    )
    assert planner._compute_required_rotation(perp_load_90) == pytest.approx(
        0.0, abs=1e-9
    )

    # SPECIFIC: diff = (grain_angle - primary_load_direction) % 180
    # Rotation is 0° when diff < 45 or diff > 135, and 90° when 45 <= diff <= 135
    for diff_angle, expected_rot in (
        (44.9, 0.0),
        (45.0, 90.0),
        (90.0, 90.0),
        (135.0, 90.0),
        (135.1, 0.0),
    ):
        spec_outline = Outline(
            name=f"spec_{diff_angle}",
            source=Path("/tmp/spec.dxf"),
            width=8.0,
            height=3.0,
            grain_constraint=GrainConstraint.SPECIFIC,
            grain_angle=diff_angle,
            primary_load_direction=0.0,
        )
        assert planner._compute_required_rotation(spec_outline) == pytest.approx(
            expected_rot, abs=1e-9
        )


def test_pack_respect_grain_false_suppresses_rotation():
    """pack(respect_grain=False) leaves parts unrotated even with a perpendicular constraint."""
    planner = NestingPlanner(
        stock_sheets=[(48.0, 96.0)],
        margin=0.25,
        spacing=0.125,
        sheet_grain_direction=0.0,
    )
    part_a = Outline(
        name="part_a",
        source=Path("/tmp/a.dxf"),
        width=20.0,
        height=6.0,
        grain_constraint=GrainConstraint.PERPENDICULAR,
        primary_load_direction=0.0,
    )
    part_b = Outline(
        name="part_b",
        source=Path("/tmp/b.dxf"),
        width=10.0,
        height=6.0,
        grain_constraint=GrainConstraint.NONE,
    )

    placed_respect = planner.pack([part_a, part_b], respect_grain=True)
    placed_ignore = planner.pack([part_a, part_b], respect_grain=False)

    # With respect_grain=True, part_a rotates 90° -> placed_width = 6.0
    assert placed_respect[0].rotation == pytest.approx(90.0, abs=1e-9)
    assert placed_respect[0].placed_width == pytest.approx(6.0, abs=1e-9)
    assert placed_respect[1].origin[0] == pytest.approx(0.25 + 6.0 + 0.125, abs=1e-9)

    # With respect_grain=False, part_a stays at 0° -> placed_width = 20.0
    assert placed_ignore[0].rotation == pytest.approx(0.0, abs=1e-9)
    assert placed_ignore[0].placed_width == pytest.approx(20.0, abs=1e-9)
    assert placed_ignore[1].origin[0] == pytest.approx(0.25 + 20.0 + 0.125, abs=1e-9)


def test_pack_sorts_by_max_dimension_and_is_permutation_invariant():
    """pack() orders outlines by descending max(width, height) regardless of input order."""
    planner = NestingPlanner(
        stock_sheets=config.manufacturing.stock_sheets,
        margin=0.25,
        spacing=0.125,
    )
    small = Outline(name="small", source=Path("/tmp/s.dxf"), width=4.0, height=5.0)
    medium = Outline(name="medium", source=Path("/tmp/m.dxf"), width=3.0, height=12.0)
    large = Outline(name="large", source=Path("/tmp/l.dxf"), width=18.0, height=6.0)

    order_1 = planner.pack([small, medium, large])
    order_2 = planner.pack([large, small, medium])
    order_3 = planner.pack([medium, large, small])

    assert [p.outline.name for p in order_1] == ["large", "medium", "small"]
    for alt in (order_2, order_3):
        assert [p.outline.name for p in alt] == [p.outline.name for p in order_1]
        for p_ref, p_alt in zip(order_1, alt):
            assert p_alt.sheet_index == p_ref.sheet_index
            assert p_alt.origin[0] == pytest.approx(p_ref.origin[0], abs=1e-9)
            assert p_alt.origin[1] == pytest.approx(p_ref.origin[1], abs=1e-9)

    # Monotonicity: max dimension is non-increasing across the packed sequence
    max_dims = [max(p.outline.width, p.outline.height) for p in order_1]
    assert max_dims == sorted(max_dims, reverse=True)


def test_pack_quantity_expansion_and_row_wrapping_geometry():
    """Multiple quantities step horizontally by width + spacing and wrap shelves when full."""
    sheet_w, sheet_h = config.manufacturing.stock_sheets[0]  # (24.0, 48.0)
    margin = 0.25
    spacing = 0.125
    planner = NestingPlanner(
        stock_sheets=[(sheet_w, sheet_h)],
        margin=margin,
        spacing=spacing,
    )
    # Two 10"-wide parts fit on a 24"-wide sheet (0.25 + 10 + 0.125 + 10 + 0.25 = 20.625 <= 24);
    # the 3rd copy (20.5 + 10 + 0.25 = 30.75 > 24) must wrap to the second shelf.
    rib = Outline(
        name="rib",
        source=Path("/tmp/rib.dxf"),
        width=10.0,
        height=6.0,
        quantity=3,
    )
    placements = planner.pack([rib])

    assert len(placements) == rib.quantity
    assert placements[0].origin == pytest.approx((margin, margin), abs=1e-9)
    assert placements[1].origin == pytest.approx(
        (margin + 10.0 + spacing, margin), abs=1e-9
    )
    assert placements[2].origin == pytest.approx(
        (margin, margin + 6.0 + spacing), abs=1e-9
    )


def test_pack_multi_sheet_spillover_and_non_overlapping_bounds():
    """Parts exceeding sheet 0 height advance to sheet 1 and satisfy non-overlap invariants."""
    stock_sheets = config.manufacturing.stock_sheets  # [(24.0, 48.0), (48.0, 96.0)]
    margin = 0.25
    spacing = 0.125
    planner = NestingPlanner(
        stock_sheets=stock_sheets,
        margin=margin,
        spacing=spacing,
    )
    # Each panel is 20" x 18": only one fits per row on sheet 0 (width 24"),
    # and two rows use 0.25 + 18 + 0.125 + 18 = 36.375" of height, so copy 3 (36.5 + 18 + 0.25 > 48)
    # spills onto sheet 1 (48" x 96").
    panel = Outline(
        name="baffle_panel",
        source=Path("/tmp/baffle.dxf"),
        width=20.0,
        height=18.0,
        quantity=4,
    )
    placements = planner.pack([panel])

    assert [p.sheet_index for p in placements] == [0, 0, 1, 1]
    # Copy 2 resets to (margin, margin) on sheet 1; copy 3 fits beside it on the 48"-wide sheet 1
    assert placements[2].origin == pytest.approx((margin, margin), abs=1e-9)
    assert placements[3].origin == pytest.approx(
        (margin + 20.0 + spacing, margin), abs=1e-9
    )

    # Global invariants: every placement stays within sheet margins and no two overlap
    for idx, p1 in enumerate(placements):
        sw, sh = stock_sheets[p1.sheet_index]
        x1, y1 = p1.origin
        w1, h1 = p1.placed_width, p1.placed_height
        assert x1 >= margin - 1e-9
        assert y1 >= margin - 1e-9
        assert x1 + w1 <= sw - margin + 1e-9
        assert y1 + h1 <= sh - margin + 1e-9

        for p2 in placements[idx + 1 :]:
            if p1.sheet_index != p2.sheet_index:
                continue
            x2, y2 = p2.origin
            w2, h2 = p2.placed_width, p2.placed_height
            separated = (
                x1 + w1 + spacing <= x2 + 1e-9
                or x2 + w2 + spacing <= x1 + 1e-9
                or y1 + h1 + spacing <= y2 + 1e-9
                or y2 + h2 + spacing <= y1 + 1e-9
            )
            assert separated


def test_pack_exact_row_and_sheet_boundary_fits_do_not_wrap():
    """Parts whose right or top edge + margin equals sheet_w or sheet_h stay on the current row/sheet."""
    planner = NestingPlanner(
        stock_sheets=[(24.0, 22.0), (24.0, 22.0)],
        margin=0.5,
        spacing=1.0,
    )
    # Row 0: copy 0 at x=0.5..11.5; copy 1 at x=12.5..23.5 -> cursor_x + w + margin = 24.0 == sheet_w.
    # Row 1: copy 2 wraps to y=0.5 + 10.0 + 1.0 = 11.5 -> cursor_y + h + margin = 22.0 == sheet_h;
    # copy 3 at (12.5, 11.5) hits both exact width (24.0) and exact height (22.0) boundaries.
    part = Outline(
        name="exact_tile",
        source=Path("/tmp/exact_tile.dxf"),
        width=11.0,
        height=10.0,
        quantity=4,
    )
    placements = planner.pack([part])

    assert [p.sheet_index for p in placements] == [0, 0, 0, 0]
    assert placements[0].origin == (0.5, 0.5)
    assert placements[1].origin == (12.5, 0.5)
    assert placements[2].origin == (0.5, 11.5)
    assert placements[3].origin == (12.5, 11.5)


def test_pack_row_height_retains_tallest_part_after_shorter_part():
    """A shorter part placed after a taller part in the same row does not shrink row_height."""
    planner = NestingPlanner(
        stock_sheets=[(24.0, 48.0)],
        margin=0.5,
        spacing=1.0,
    )
    # Sorted by max(width, height) descending: tall (12.0), short (10.0), wrapped (8.0).
    # Row 0 holds tall at (0.5, 0.5) and short at (11.5, 0.5); row_height must remain 12.0 (not 4.0)
    # so wrapped starts at cursor_y = 0.5 + 12.0 + 1.0 = 13.5.
    tall = Outline(name="tall", source=Path("/tmp/tall.dxf"), width=10.0, height=12.0)
    short = Outline(name="short", source=Path("/tmp/short.dxf"), width=10.0, height=4.0)
    wrapped = Outline(
        name="wrapped", source=Path("/tmp/wrapped.dxf"), width=8.0, height=3.0
    )

    placements = planner.pack([tall, short, wrapped])

    assert [p.outline.name for p in placements] == ["tall", "short", "wrapped"]
    assert placements[0].origin == (0.5, 0.5)
    assert placements[1].origin == (11.5, 0.5)
    assert placements[2].origin == (0.5, 13.5)


def test_load_outlines_computes_extents_sorts_and_skips_invalid_files(
    tmp_path, monkeypatch
):
    """load_outlines reads sorted DXFs, computes bbox dimensions, and skips unreadable/empty files."""
    for filename in ("z_rib.dxf", "a_spar.dxf", "empty.dxf", "broken.dxf", "notes.txt"):
        (tmp_path / filename).write_text("placeholder")

    extents_by_name = {
        "a_spar.dxf": ((-2.5, 1.0, 0.0), (21.5, 5.5, 0.0)),  # 24.0 x 4.5
        "z_rib.dxf": ((0.0, 0.0, 0.0), (12.25, 6.75, 0.0)),  # 12.25 x 6.75
        "empty.dxf": None,
    }

    def fake_readfile(path: Path):
        if Path(path).name == "broken.dxf":
            raise OSError("corrupt DXF file")
        doc = MagicMock()
        doc.modelspace.return_value = Path(path).name
        return doc

    monkeypatch.setattr(nesting_mod.ezdxf, "readfile", fake_readfile)
    monkeypatch.setattr(
        nesting_mod.bbox, "extents", lambda msp_name: extents_by_name[msp_name]
    )

    planner = NestingPlanner(stock_sheets=config.manufacturing.stock_sheets)
    outlines = planner.load_outlines(tmp_path, laminate="wing_skin")

    assert [o.name for o in outlines] == ["a_spar", "z_rib"]
    assert outlines[0].source == tmp_path / "a_spar.dxf"
    assert outlines[0].width == pytest.approx(24.0, abs=1e-9)
    assert outlines[0].height == pytest.approx(4.5, abs=1e-9)
    assert outlines[0].laminate == "wing_skin"

    assert outlines[1].source == tmp_path / "z_rib.dxf"
    assert outlines[1].width == pytest.approx(12.25, abs=1e-9)
    assert outlines[1].height == pytest.approx(6.75, abs=1e-9)
    assert outlines[1].laminate == "wing_skin"


def test_corner_relief_and_label_annotations():
    """_add_corner_relief emits 4 corner circles only when radius > 0, and _add_label marks center."""
    dogbone_r = config.manufacturing.default_dogbone_radius  # 0.0625
    fillet_r = config.manufacturing.default_fillet_radius  # 0.125
    engrave_depth = config.manufacturing.engraving_depth  # 0.02

    planner = NestingPlanner(
        stock_sheets=config.manufacturing.stock_sheets,
        dogbone_radius=dogbone_r,
        fillet_radius=fillet_r,
    )
    outline = Outline(
        name="f28_bulkhead",
        source=Path("/tmp/f28.dxf"),
        width=10.0,
        height=4.0,
    )
    placement = Placement(outline=outline, sheet_index=0, origin=(1.5, 2.5))
    msp = _FakeModelspace()

    # Non-positive radii must be a no-op
    planner._add_corner_relief(msp, placement, 0.0, "DOGBONE")
    planner._add_corner_relief(msp, placement, -0.05, "FILLET")
    assert len(msp.circles) == 0

    # Positive radius adds 4 circles at the 4 corners of the outline
    planner._add_corner_relief(msp, placement, dogbone_r, "DOGBONE")
    assert len(msp.circles) == 4
    expected_corners = [
        (1.5, 2.5),
        (11.5, 2.5),
        (11.5, 6.5),
        (1.5, 6.5),
    ]
    for (center, radius, attribs), expected in zip(msp.circles, expected_corners):
        assert center == pytest.approx(expected, abs=1e-9)
        assert radius == pytest.approx(dogbone_r, abs=1e-9)
        assert attribs == {"layer": "DOGBONE"}

    # _add_label places centered text and vertical engraving line of length engraving_depth
    planner._add_label(msp, placement, engrave_depth)
    assert len(msp.texts) == 1
    assert msp.texts[0].text == "f28_bulkhead"
    assert msp.texts[0].pos == pytest.approx(placement.label_position, abs=1e-9)
    assert msp.texts[0].align == "MIDDLE_CENTER"
    assert msp.texts[0].dxfattribs == {"layer": "ENGRAVE_LABELS"}

    assert len(msp.lines) == 1
    start, end, line_attribs = msp.lines[0]
    cx, cy = placement.label_position
    assert start == pytest.approx((cx, cy), abs=1e-9)
    assert end == pytest.approx((cx, cy - engrave_depth), abs=1e-9)
    assert line_attribs == {"layer": "ENGRAVE_LABELS"}


def test_grain_arrow_and_sheet_grain_indicator_geometry():
    """_add_grain_arrow and _add_sheet_grain_indicator produce exact vector lengths and angles."""
    planner = NestingPlanner(
        stock_sheets=config.manufacturing.stock_sheets,
        sheet_grain_direction=30.0,
    )
    msp = _FakeModelspace()

    # Unconstrained part produces no grain arrow lines
    unconstrained = Placement(
        outline=Outline(
            name="plain",
            source=Path("/tmp/p.dxf"),
            width=6.0,
            height=4.0,
            grain_constraint=GrainConstraint.NONE,
        ),
        sheet_index=0,
        origin=(1.0, 1.0),
    )
    planner._add_grain_arrow(msp, unconstrained)
    assert len(msp.lines) == 0

    # Constrained part at 60° draws 1 shaft of length 2.0 + 2 arrowhead barbs of length 0.25
    constrained = Placement(
        outline=Outline(
            name="angled_ply",
            source=Path("/tmp/ap.dxf"),
            width=8.0,
            height=4.0,
            grain_constraint=GrainConstraint.SPECIFIC,
            grain_angle=60.0,
        ),
        sheet_index=0,
        origin=(2.0, 3.0),
        rotation=0.0,
    )
    arrow_length = 2.0
    planner._add_grain_arrow(msp, constrained, arrow_length=arrow_length)
    assert len(msp.lines) == 3

    (x1, y1), (x2, y2), shaft_attribs = msp.lines[0]
    assert shaft_attribs == {"layer": "GRAIN_DIRECTION", "color": 3}
    # Midpoint of shaft is label_position; Euclidean length is arrow_length; angle is 60°
    assert ((x1 + x2) / 2.0, (y1 + y2) / 2.0) == pytest.approx(
        constrained.label_position, abs=1e-9
    )
    assert math.hypot(x2 - x1, y2 - y1) == pytest.approx(arrow_length, abs=1e-9)
    assert math.degrees(math.atan2(y2 - y1, x2 - x1)) == pytest.approx(60.0, abs=1e-9)

    for (bx1, by1), (bx2, by2), barb_attribs in msp.lines[1:]:
        assert (bx1, by1) == pytest.approx((x2, y2), abs=1e-9)
        assert math.hypot(bx2 - bx1, by2 - by1) == pytest.approx(0.25, abs=1e-9)
        assert barb_attribs == {"layer": "GRAIN_DIRECTION", "color": 3}

    # Sheet grain indicator starts at (1.0, 1.0) with length 3.0 at sheet_grain_direction (30°)
    msp_sheet = _FakeModelspace()
    planner._add_sheet_grain_indicator(msp_sheet, 24.0, 48.0)
    assert len(msp_sheet.lines) == 1
    (sx0, sy0), (sx1, sy1), s_attribs = msp_sheet.lines[0]
    assert (sx0, sy0) == pytest.approx((1.0, 1.0), abs=1e-9)
    assert math.hypot(sx1 - sx0, sy1 - sy0) == pytest.approx(3.0, abs=1e-9)
    assert math.degrees(math.atan2(sy1 - sy0, sx1 - sx0)) == pytest.approx(
        30.0, abs=1e-9
    )
    assert s_attribs == {"layer": "SHEET_GRAIN", "color": 5}
    assert msp_sheet.texts[0].text == "SHEET GRAIN"
    assert msp_sheet.texts[0].pos == pytest.approx((1.0, 0.5), abs=1e-9)


def test_export_writes_dxf_and_manifest_with_laminate_cut_orders(tmp_path, monkeypatch):
    """export() writes per-sheet DXFs and a CSV manifest mapping laminate cut orders."""
    created_docs: list[_FakeDoc] = []

    def fake_new():
        doc = _FakeDoc()
        created_docs.append(doc)
        return doc

    monkeypatch.setattr(nesting_mod.ezdxf, "new", fake_new)
    monkeypatch.setattr(
        nesting_mod.ezdxf,
        "readfile",
        lambda _path: _FakeDoc(source_entities=[_FakeEntity("part_loop")]),
    )

    planner = NestingPlanner(
        stock_sheets=config.manufacturing.stock_sheets,
        dogbone_radius=config.manufacturing.default_dogbone_radius,
        fillet_radius=config.manufacturing.default_fillet_radius,
    )
    wing_steps = config.materials.laminates["wing_skin"].cut_order_steps()

    p1 = Placement(
        outline=Outline(
            name="skin_panel",
            source=tmp_path / "skin.dxf",
            width=12.0,
            height=5.5,
            laminate="wing_skin",
        ),
        sheet_index=0,
        origin=(0.25, 0.25),
    )
    p2 = Placement(
        outline=Outline(
            name="foam_template",
            source=tmp_path / "foam.dxf",
            width=8.0,
            height=4.0,
            laminate=None,
        ),
        sheet_index=0,
        origin=(12.375, 0.25),
    )

    out_dir = tmp_path / "cam_out"
    manifest_path = planner.export(
        [p1, p2],
        output_dir=out_dir,
        engraving_depth=config.manufacturing.engraving_depth,
        laminate_cut_orders={"wing_skin": wing_steps},
    )

    assert manifest_path == out_dir / "nest_manifest.csv"
    assert manifest_path.exists()
    assert (out_dir / "nested_sheet_0.dxf").exists()

    rows = manifest_path.read_text().splitlines()
    assert rows[0] == "sheet,part,x,y,width,height,laminate,cut_order"
    assert (
        rows[1]
        == "0,skin_panel,0.250,0.250,12.000,5.500,wing_skin,engrave_labels > pocket_features > profile_cut"
    )
    assert rows[2] == "0,foam_template,12.375,0.250,8.000,4.000,,ENGRAVE > PROFILE"

    # Stock outline and translated entities recorded in the target DXF
    sheet_doc = created_docs[0]
    assert sheet_doc.msp.polylines[0] == (
        [(0, 0), (24.0, 0), (24.0, 48.0), (0, 48.0)],
        True,
        {"layer": "STOCK"},
    )
    assert len(sheet_doc.msp.added_entities) == 2
    assert sheet_doc.msp.added_entities[0].translations == [(0.25, 0.25, 0)]
    assert sheet_doc.msp.added_entities[1].translations == [(12.375, 0.25, 0)]


def test_export_with_orientation_rotated_entities_and_manifest(tmp_path, monkeypatch):
    """export_with_orientation rotates 90° entities, records placed dimensions, and honors arrow toggle."""
    created_docs: list[_FakeDoc] = []

    def fake_new():
        doc = _FakeDoc()
        created_docs.append(doc)
        return doc

    monkeypatch.setattr(nesting_mod.ezdxf, "new", fake_new)
    monkeypatch.setattr(
        nesting_mod.ezdxf,
        "readfile",
        lambda _path: _FakeDoc(source_entities=[_FakeEntity("ply_outline")]),
    )

    planner = NestingPlanner(stock_sheets=config.manufacturing.stock_sheets)
    rotated_placement = Placement(
        outline=Outline(
            name="f22_doubler",
            source=tmp_path / "f22_doubler.dxf",
            width=15.0,
            height=5.0,
            laminate="canard_skin",
            grain_constraint=GrainConstraint.PERPENDICULAR,
            grain_angle=0.0,
            primary_load_direction=0.0,
        ),
        sheet_index=0,
        origin=(0.5, 0.75),
        rotation=90.0,
    )
    unrotated_placement = Placement(
        outline=Outline(
            name="longeron_cap",
            source=tmp_path / "longeron_cap.dxf",
            width=10.0,
            height=2.0,
            laminate="wing_skin",
            grain_constraint=GrainConstraint.PARALLEL,
            grain_angle=0.0,
            primary_load_direction=0.0,
        ),
        sheet_index=0,
        origin=(6.0, 0.75),
        rotation=0.0,
    )

    out_dir = tmp_path / "oriented_out"
    manifest_path, first_dxf = planner.export_with_orientation(
        [rotated_placement, unrotated_placement],
        output_dir=out_dir,
        include_grain_arrows=True,
    )

    assert manifest_path == out_dir / "nest_manifest.csv"
    assert first_dxf == out_dir / "nested_sheet_0.dxf"
    assert first_dxf.exists()
    assert created_docs[0].layers.created == {
        "GRAIN_DIRECTION": 3,
        "SHEET_GRAIN": 5,
    }

    # Manifest records placed_width/placed_height, rotation, and quoted grain_note
    rows = manifest_path.read_text().splitlines()
    assert (
        rows[0] == "sheet,part,x,y,width,height,rotation,laminate,grain_note,cut_order"
    )
    assert (
        rows[1]
        == '0,f22_doubler,0.500,0.750,5.000,15.000,90,canard_skin,"Grain vertical (90°)",ENGRAVE > PROFILE'
    )
    assert (
        rows[2]
        == '0,longeron_cap,6.000,0.750,10.000,2.000,0,wing_skin,"Grain horizontal (0°)",ENGRAVE > PROFILE'
    )

    # _copy_entities_rotated rotated the first entity by pi/2; _copy_entities left the second unrotated
    copied_rot, copied_unrot = created_docs[0].msp.added_entities
    assert len(copied_rot.rotations) == 1
    assert copied_rot.rotations[0] == pytest.approx(math.radians(90.0), abs=1e-9)
    assert copied_rot.translations == [(0.5, 0.75, 0)]
    assert copied_unrot.rotations == []
    assert copied_unrot.translations == [(6.0, 0.75, 0)]

    # With include_grain_arrows=True: 1 sheet grain line + 2*(1 label line + 3 grain arrow lines) = 9 lines
    assert len(created_docs[0].msp.lines) == 9

    # With include_grain_arrows=False: only the engraving label line is drawn (no grain lines)
    no_arrow_dir = tmp_path / "no_arrow_out"
    planner.export_with_orientation(
        [rotated_placement],
        output_dir=no_arrow_dir,
        include_grain_arrows=False,
    )
    assert len(created_docs[1].msp.lines) == 1
    assert created_docs[1].msp.lines[0][2] == {"layer": "ENGRAVE_LABELS"}

    # Empty placements fallback returns nested_sheet_0.dxf path alongside the header-only manifest
    empty_dir = tmp_path / "empty_out"
    empty_manifest, fallback_dxf = planner.export_with_orientation(
        [], output_dir=empty_dir
    )
    assert empty_manifest.read_text().splitlines() == [
        "sheet,part,x,y,width,height,rotation,laminate,grain_note,cut_order"
    ]
    assert fallback_dxf == empty_dir / "nested_sheet_0.dxf"
