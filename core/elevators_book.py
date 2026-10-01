"""
Open-EZ PDE: Roncz elevators as fitted shapes (cobelu ch30, figure C-1)
=======================================================================

Every part is ``representational``: the elevator contour is template-only (G, H, I, J, E; not held) and
the elevator chord fraction is fitted. What IS dimensioned (via ``config.geometry`` and
``core.elevators_kin``): the span ends (cobelu fig C-1; foam inboard ends flagged conflict vs the fuselage sides, left tube crosses to +7.7), the tube OD (ch30), the CS-10 and CS-11
lead sizes and positions along the span. Spans, hinge stations, pins and travel come from
``core.elevators_kin``; nothing is re-derived here.

Frame: canard-local, as ``guide.layup_geometry.Planform``: x chordwise aft from the canard leading edge,
y = signed B.L. (right positive, the left elevator spans negative y), z up from the airfoil outline.
"""

from __future__ import annotations

import cadquery as cq
import numpy as np

from config import config

from . import elevators_kin as ek
from .fuselage_book import FusePart

G = config.geometry

FITTED_ELEV_LE_XC = 0.70  # fitted, not book: elevator (tube) leading edge as a fraction of chord; contour templates G/H/I/J not held
FITTED_SLEEVE = 0.03  # in, fitted: outline inflation so the elevator does not z-fight with canard.core
FITTED_PLATE = (
    2.0,
    1.5,
    0.125,
)  # (x, y, z) NC-3 hinge plate from fig C-1, medium confidence
CS10_SECTION = (2.0, 0.8)  # (x, z) in, research: block section; profile not dimensioned
TE_TRIM_XC = 0.97  # as guide.layup_geometry.Planform.TE_TRIM_XC

SIDES = ek.SIDES


def _planform():
    from core.structures import CanardGenerator
    from guide.layup_geometry import Planform

    return Planform.from_generator(CanardGenerator())


def _chord() -> float:
    return _planform().chord(0.0)


def x_tube_le() -> float:
    return FITTED_ELEV_LE_XC * _chord()


def _z_mid(x: float) -> float:
    pf = _planform()
    top, bot = pf.surface(0.0, "top"), pf.surface(0.0, "bottom")
    return 0.5 * float(
        np.interp(x, top[:, 0], top[:, 1]) + np.interp(x, bot[:, 0], bot[:, 1])
    )


def hinge_axis_xz() -> tuple[float, float]:
    """Hinge line point (x, z) in the canard frame; constant along y (zero sweep)."""
    x = x_tube_le() + G.elevator_hinge_offset_in
    return (x, _z_mid(x))


def elevator_pose(side: str, deg_down: float) -> np.ndarray:
    """4x4 pose rotating the elevator about the hinge line (axis y); positive = trailing edge down.

    Same convention as ``elevators_kin.rotate_about_hinge`` (x' = hx + dx cos + dz sin, z' = hz - dx sin + dz cos).
    """
    ek._validate_side(side)
    hx, hz = hinge_axis_xz()
    t = np.radians(deg_down)
    c, s = np.cos(t), np.sin(t)
    m = np.eye(4)
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    m[0, 3] = hx - (c * hx + s * hz)
    m[2, 3] = hz - (-s * hx + c * hz)
    return m


def _section_polygon() -> list[tuple[float, float]]:
    pf = _planform()
    top, bot = pf.surface(0.0, "top"), pf.surface(0.0, "bottom")
    x0 = x_tube_le()
    zt, zb = (
        float(np.interp(x0, top[:, 0], top[:, 1])),
        float(np.interp(x0, bot[:, 0], bot[:, 1])),
    )
    t = [(x0, zt)] + [(float(x), float(z)) for x, z in top if x > x0]
    b = [(float(x), float(z)) for x, z in bot if x > x0][::-1] + [(x0, zb)]
    return t + b


def _extrude(poly, y0: float, y1: float, sleeve: float = 0.0) -> cq.Workplane:
    pts = [cq.Vector(x, y0, z) for x, z in poly]
    w = cq.Wire.makePolygon(pts + [pts[0]])
    if sleeve:
        w = w.offset2D(sleeve, "intersection")[0]
    return cq.Workplane("XY").add(
        cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), cq.Vector(0, y1 - y0, 0))
    )


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _wp(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def build_elevators() -> dict[str, FusePart]:
    """The Roncz elevator parts, name -> FusePart (all representational)."""
    parts: dict[str, FusePart] = {}
    poly = _section_polygon()
    x0 = x_tube_le()
    r = G.elevator_tube_od_in / 2
    hx, _hz = hinge_axis_xz()
    gap = G.balance_pocket_clearance_in
    for side in ("right", "left"):
        lo, hi = ek.elevator_span(side)
        parts[f"elevator_{side}"] = FusePart(
            f"elevator_{side}",
            _extrude(poly, lo, hi, FITTED_SLEEVE),
            "representational",
            note="fitted shape: the elevator contour is template-only (G, H, I, J, E; not held) and the elevator chord "
            f"fraction ({FITTED_ELEV_LE_XC}) is fitted; the span ends ARE dimensioned (cobelu:pC-1 figure C-1, via config)",
        )
        tz = _z_mid(x0 + r)
        tlo, thi = ek.tube_span(side)
        tube = cq.Solid.makeCylinder(
            r, thi - tlo, cq.Vector(x0 + r, tlo, tz), cq.Vector(0, 1, 0)
        )
        parts[f"elevator_tube_{side}"] = FusePart(
            f"elevator_tube_{side}",
            _wp(tube),
            "representational",
            note="fitted position (centre at the tube leading edge + OD/2, mid-height of the section); the 1.0 in OD is book (cobelu ch30); "
            "the left tube is 72.7 in (B.L. -65.0 to +7.7, cobelu C-1) and crosses the fuselage and the centreline, the foam does not",
        )
        hz = hinge_axis_xz()[1]
        px, py, pz = FITTED_PLATE
        plates = [
            _box(
                hx - px / 2,
                hx + px / 2,
                s - py / 2,
                s + py / 2,
                hz - pz / 2,
                hz + pz / 2,
            )
            for s in ek.hinge_stations(side)
        ]
        parts[f"hinges_{side}"] = FusePart(
            f"hinges_{side}",
            _wp(cq.Compound.makeCompound(plates)),
            "representational",
            note="stations positioned from text and figure at LOW confidence; text says seven slots, the figure stations place four "
            "(9.2 is 0.1 in outside the foam on BOTH sides and is NOT moved: see elevators_kin.unplaced_hinge_stations); "
            "plate size 2.0 x 1.5 x 0.125 from C-1 at medium confidence",
        )
        bx, bz = CS10_SECTION
        bzc = _z_mid(x0 - gap - bx / 2)
        out_y = G.elevator_outboard_end_bl_in
        ln = G.cs10_inboard_from_end_in
        y0, y1 = (out_y - ln, out_y) if side == "right" else (-out_y, -out_y + ln)
        parts[f"balance_weight_{side}"] = FusePart(
            f"balance_weight_{side}",
            _wp(_box(x0 - gap - bx, x0 - gap, y0, y1, bzc - bz / 2, bzc + bz / 2)),
            "representational",
            note="CS-10 lead: 7.5 in measured inboard from the outboard end (book per research); block section 2.0 x 0.8 not "
            "dimensioned; sits just forward of the tube leading edge",
        )
        dy, dx, dz = G.cs11_lead_dims
        cz = _z_mid(x0 - gap - dx / 2)
        # right: at the foam inboard end; left: at the TUBE end (+7.7), where the figure puts CS-11/NC-12A
        c0, c1 = (lo, lo + dy) if side == "right" else (thi - dy, thi)
        parts[f"cs11_weight_{side}"] = FusePart(
            f"cs11_weight_{side}",
            _wp(_box(x0 - gap - dx, x0 - gap, c0, c1, cz - dz / 2, cz + dz / 2)),
            "representational",
            note="CS-11 lead 2.0 x 0.6 x 0.8 (2.0 along the span) abutting the inboard end at the leading edge (right: foam end; left: tube end +7.7, "
            "where C-1 puts CS-11/NC-12A); position not dimensioned",
        )
    return parts
