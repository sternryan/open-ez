"""
Open-EZ PDE: Jig Factory
=========================

Generates 3D-printable assembly aids and fuselage jigs.

1. JigFactory: Incidence cradles, drill guides, vortilon templates.

These were previously embedded in core/manufacturing.py.

Backward compatibility: ``from core.manufacturing import JigFactory`` still
works because manufacturing.py re-exports this name.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import cadquery as cq

from .base import AircraftComponent  # noqa: E402
from config import config  # noqa: E402

logger = logging.getLogger(__name__)


class JigFactory:
    """
    Generates 3D printable tooling for aircraft assembly.

    Jig Types:
    1. Incidence Cradles: Hold wing at specific angle for fuselage attachment
    2. Drill Guides: Precision sleeves for bolt hole drilling
    3. Alignment Templates: Ensure correct positioning during layup
    """

    # Standard jig parameters
    CRADLE_WIDTH = 4.0  # Thickness in spanwise direction
    CRADLE_HEIGHT = 5.0  # Height from table surface
    CRADLE_LENGTH = 20.0  # Chordwise extent
    WALL_THICKNESS = 0.25  # Structural wall thickness
    CLEARANCE = 0.02  # Fit clearance for wing

    @staticmethod
    def generate_incidence_cradle(
        wing_component: AircraftComponent,
        station_bl: float,
        incidence_angle: float,
        cradle_width: float = 4.0,
        base_height: float = 5.0,
    ) -> cq.Workplane:
        """
        Create a cradle that conforms to the BOTTOM of the wing
        at a specific Butt Line (BL), with a flat base set to the
        correct incidence angle relative to the longerons.

        The cradle:
        1. Has a flat base for stable table placement
        2. Has a contoured top matching the wing lower surface
        3. Is rotated so the wing sits at the correct incidence angle
        4. Includes alignment marks and part labeling

        Args:
            wing_component: AircraftComponent with geometry
            station_bl: Butt Line station (spanwise position)
            incidence_angle: Wing incidence angle in degrees
            cradle_width: Width in spanwise direction
            base_height: Height from table to wing lower surface

        Returns:
            CadQuery Workplane with the cradle solid
        """
        # Get geometry from component if available
        try:
            wing_geom = wing_component.geometry
            has_geometry = wing_geom is not None
        except (ValueError, AttributeError):
            wing_geom = None
            has_geometry = False

        # Base block dimensions
        length = JigFactory.CRADLE_LENGTH
        width = cradle_width
        height = base_height + 3.0  # Extra height for wing contour

        # Create base block
        cradle = cq.Workplane("XY").box(length, width, height, centered=False)

        if has_geometry and wing_geom is not None:
            # Slice wing at station to get profile
            try:
                # Create slicing plane at the butt line
                slice_plane = cq.Workplane("XZ").workplane(offset=station_bl)

                # Intersect wing with plane to get cross-section
                # Then use that profile to cut the cradle top
                wing_section = wing_geom.section(slice_plane)

                # Offset section outward for clearance
                offset_section = wing_section.offset2D(JigFactory.CLEARANCE)

                # Create cutting solid from offset section
                cutter = offset_section.extrude(width * 2)

                # Position cutter at correct height
                cutter = cutter.translate((0, -width / 2, base_height))

                # Cut wing profile from cradle top
                cradle = cradle.cut(cutter)

            except Exception:
                # Fallback to parametric approximation
                cradle = JigFactory._add_parametric_contour(
                    cradle, length, width, height, base_height
                )
        else:
            # Use parametric approximation based on airfoil shape
            cradle = JigFactory._add_parametric_contour(
                cradle, length, width, height, base_height
            )

        # Apply incidence rotation
        if abs(incidence_angle) > 0.001:
            # Rotate about the quarter-chord axis
            pivot_x = length * 0.25
            pivot_z = base_height

            cradle = (
                cradle.translate((-pivot_x, 0, -pivot_z))
                .rotate((0, 0, 0), (0, 1, 0), -incidence_angle)
                .translate((pivot_x, 0, pivot_z))
            )

        # Add structural features
        cradle = JigFactory._add_structural_features(cradle, length, width, height)

        # Add alignment marks
        cradle = JigFactory._add_alignment_marks(cradle, length, width, station_bl)

        return cradle

    @staticmethod
    def _add_parametric_contour(
        cradle: cq.Workplane,
        length: float,
        width: float,
        height: float,
        base_height: float,
    ) -> cq.Workplane:
        """Add approximated airfoil contour cut to cradle top."""
        # Create airfoil-shaped cutter based on typical lower surface
        # Lower surface is approximately parabolic for cambered airfoils

        n_points = 50
        points = []

        for i in range(n_points):
            x = (i / (n_points - 1)) * length
            # Approximate lower surface: slight camber, max at ~30% chord
            t = x / length
            y_lower = -0.02 * length * (4 * t * (1 - t))  # Parabolic camber
            points.append((x, base_height + y_lower + JigFactory.CLEARANCE))

        # Add closing points above the profile
        points.append((length, height + 1))
        points.append((0, height + 1))

        # Create profile and extrude
        cutter = cq.Workplane("XZ").polyline(points).close().extrude(width)

        return cradle.cut(cutter)

    @staticmethod
    def _add_structural_features(
        cradle: cq.Workplane, length: float, width: float, height: float
    ) -> cq.Workplane:
        """Add lightening pockets and structural ribs."""
        wall = JigFactory.WALL_THICKNESS

        # Create lightening pocket (hollow out interior)
        pocket_length = length - 2 * wall - 1.0
        pocket_width = width - 2 * wall
        pocket_height = height - wall - 0.5

        if pocket_length > 2 and pocket_width > 1 and pocket_height > 1:
            pocket = (
                cq.Workplane("XY")
                .center(length / 2, width / 2)
                .rect(pocket_length, pocket_width)
                .extrude(pocket_height)
                .translate((0, 0, wall))
            )
            cradle = cradle.cut(pocket)

        return cradle

    @staticmethod
    def _add_alignment_marks(
        cradle: cq.Workplane, length: float, width: float, station_bl: float
    ) -> cq.Workplane:
        """Add centerline and station marks."""
        mark_depth = 0.05
        mark_width = 0.03

        # Centerline on top surface
        try:
            centerline = (
                cq.Workplane("XY")
                .center(length / 2, width / 2)
                .rect(length - 1, mark_width)
                .extrude(-mark_depth)
                .translate((0, 0, 10))  # Position at top
            )
            cradle = cradle.cut(centerline)
        except Exception:
            pass  # Skip if operation fails

        return cradle

    @staticmethod
    def generate_drill_guide(
        hole_diameter: float,
        guide_length: float = 1.5,
        flange_diameter: Optional[float] = None,
        flange_thickness: float = 0.25,
    ) -> cq.Workplane:
        """
        Generate a precision drill guide sleeve.

        Args:
            hole_diameter: Target hole diameter
            guide_length: Length of the guide sleeve
            flange_diameter: Diameter of alignment flange (default: 3x hole)
            flange_thickness: Thickness of the flange

        Returns:
            CadQuery Workplane with the drill guide
        """
        if flange_diameter is None:
            flange_diameter = hole_diameter * 3

        # Inner diameter with clearance for drill bit
        inner_d = hole_diameter + 0.005
        outer_d = hole_diameter + 0.125

        # Create sleeve
        guide = (
            cq.Workplane("XY")
            .circle(outer_d / 2)
            .extrude(guide_length)
            .faces(">Z")
            .circle(flange_diameter / 2)
            .extrude(flange_thickness)
        )

        # Cut center hole
        guide = guide.faces("<Z").circle(inner_d / 2).cutThruAll()

        return guide

    @staticmethod
    def generate_vortilon_template(
        height: float = 2.5, base_length: float = 3.0, thickness: float = 0.125
    ) -> cq.Workplane:
        """
        Generate a template for marking/cutting vortilons.

        Vortilons are small fences on the leading edge that control
        spanwise flow at high angles of attack.

        Args:
            height: Vortilon height perpendicular to wing surface
            base_length: Length along leading edge
            thickness: Template material thickness

        Returns:
            CadQuery Workplane with the template
        """
        # Vortilon shape: triangular fence
        template = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base_length, 0)
            .lineTo(base_length / 2, height)
            .close()
            .extrude(thickness)
        )

        # Add handle
        handle = (
            cq.Workplane("XY")
            .center(base_length / 2, -0.5)
            .rect(1.5, 1.0)
            .extrude(thickness)
        )

        return template.union(handle)

    @staticmethod
    def export_all_jigs(output_dir: Path):
        """
        Batch generate standard jig set.

        Generates:
        - Wing root incidence jig (BL 23.3)
        - Wing mid-span jig (BL 79)
        - Canard root jig
        - Standard drill guides (AN3, AN4 bolts)
        - Vortilon templates
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple placeholder component for jig generation
        class PlaceholderWing(AircraftComponent):
            def __init__(self):
                super().__init__("placeholder", "Placeholder for jig generation")

            def _build_geometry(self):
                self._geometry = cq.Workplane("XY").box(100, 50, 5)
                return self._geometry

            def export_dxf(self, path):
                return path

        placeholder = PlaceholderWing()

        # Wing root jig (BL 23.3)
        try:
            jig_root = JigFactory.generate_incidence_cradle(
                placeholder,
                station_bl=23.3,
                incidence_angle=config.geometry.wing_incidence,
            )
            cq.exporters.export(jig_root, str(output_dir / "JIG_wing_root_BL23.stl"))
        except Exception as e:
            print(f"  Warning: Could not generate wing root jig: {e}")

        # Wing mid-span jig (BL 79)
        try:
            jig_mid = JigFactory.generate_incidence_cradle(
                placeholder,
                station_bl=79.0,
                incidence_angle=config.geometry.wing_incidence,
            )
            cq.exporters.export(jig_mid, str(output_dir / "JIG_wing_mid_BL79.stl"))
        except Exception as e:
            print(f"  Warning: Could not generate wing mid jig: {e}")

        # Canard root jig
        try:
            jig_canard = JigFactory.generate_incidence_cradle(
                placeholder,
                station_bl=0.0,
                incidence_angle=config.geometry.canard_incidence,
            )
            cq.exporters.export(jig_canard, str(output_dir / "JIG_canard_root.stl"))
        except Exception as e:
            print(f"  Warning: Could not generate canard jig: {e}")

        # Drill guides for AN3 (3/16") and AN4 (1/4") bolts
        for name, diameter in [("AN3", 0.1875), ("AN4", 0.250)]:
            try:
                guide = JigFactory.generate_drill_guide(diameter)
                cq.exporters.export(guide, str(output_dir / f"DRILL_GUIDE_{name}.stl"))
            except Exception as e:
                print(f"  Warning: Could not generate {name} drill guide: {e}")

        # Vortilon template
        try:
            vortilon = JigFactory.generate_vortilon_template()
            cq.exporters.export(vortilon, str(output_dir / "TEMPLATE_vortilon.stl"))
        except Exception as e:
            print(f"  Warning: Could not generate vortilon template: {e}")


__all__ = ["JigFactory"]
