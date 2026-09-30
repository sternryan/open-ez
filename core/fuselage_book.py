"""
Open-EZ PDE: Long-EZ fuselage box built from the book (plans chapters 4-6)
==========================================================================

Every part carries a fidelity label:

- ``book``: dimensions printed on a registered page (cited).
- ``derived``: computed from printed dimensions (cited).
- ``representational``: a stand-in whose outline the book prints only on full-size sheets we do
  not hold, or does not print. Never labelled or tagged book.

Frame: model x = FS (aft positive), y = B.L. (right positive), z = W.L. - 17.4 (the model zero
is the book wing plane, W.L. 17.4, ``wing_le_wl``). Side coordinate u (0 at the front edge, 103
at the aft end) maps to FS = fs_f22 + u; depth v below the top edge maps to
z = (side_panel_top_wl - 17.4) - v.

Every dimension comes from ``config.geometry``. The only literals here are the named fitted
sizes (``FITTED_*``) which are representational, not book.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import pairwise
from pathlib import Path
from typing import Any

import cadquery as cq
import numpy as np
from scipy.interpolate import CubicSpline

from config import config

from .base import AircraftComponent
from .sources import check_citation

logger = logging.getLogger(__name__)

G = config.geometry

# Book W.L. of the model's zero (the wing plane), plans-1980:p134; see config wing_le_wl.
WING_PLANE_WL = 17.4

# Fitted, not book: representational bulkhead sizes the book prints only on full-size sheets
# (A1/A2/A3/A4, not held). Each is a stand-in chosen to fit the side profile.
FITTED_F22_THICKNESS = 0.2  # fitted, not book: 5 mm PVC foam
FITTED_F28_THICKNESS = 0.2  # fitted, not book: 5 mm PVC foam
FITTED_PANEL_THICKNESS = 0.2  # fitted, not book: 5 mm PVC foam
FITTED_FIREWALL_THICKNESS = 0.25  # fitted, not book: birch ply
FITTED_F28_BAND_DEPTH = 4.0  # fitted, not book: F28 modelled as a top band this deep
FITTED_PANEL_LEG_CUTOUT = (
    8.0,
    8.0,
)  # fitted, not book: (width y, height z) leg cutouts
FITTED_PANEL_LEG_INSET = 2.0  # fitted, not book: cutout edge this far from each side
_SHEET_NOTE = (
    "outline on full-size sheet A1/A2/A3/A4 (not held); fitted to the side profile"
)

FIDELITIES = frozenset({"book", "derived", "representational"})

# Plain names for people (the lab's labels, the ledger's reasons). Never show a part's internal name instead.
PART_NAMES = {
    "side_left": "Left side",
    "side_right": "Right side",
    "front_seat_bkhd": "Front seat bulkhead",
    "rear_seat_bkhd": "Rear seat bulkhead",
    "top_longeron_left": "Left top longeron",
    "top_longeron_right": "Right top longeron",
    "f22": "F22 bulkhead",
    "f28": "F28 bulkhead",
    "panel": "Instrument panel",
    "firewall": "Firewall",
    "bottom": "Bottom foam",
}


def part_name(name: str) -> str:
    """A part's plain name ("Left top longeron" for `top_longeron_left`)."""
    return PART_NAMES.get(name, name.replace("_", " ").capitalize())


_P36, _P37, _P38 = "plans-1980:p36", "plans-1980:p37", "plans-1980:p38"
_P33, _P34 = "plans-1980:p33", "plans-1980:p34"


@dataclass(frozen=True)
class FusePart:
    """One fuselage-box part with its fidelity and citations."""

    name: str
    solid: cq.Workplane
    fidelity: str
    cite: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        if self.fidelity not in FIDELITIES:
            raise ValueError(
                f"{self.name}: fidelity {self.fidelity!r} not in {sorted(FIDELITIES)}"
            )
        if self.fidelity in {"book", "derived"} and not self.cite:
            raise ValueError(f"{self.name}: a {self.fidelity} part needs a citation")
        for c in self.cite:
            check_citation(c)


# --- frame helpers -------------------------------------------------------------------------------
def z_of_wl(wl: float) -> float:
    return wl - WING_PLANE_WL + G.wing_le_wl


Z_TOP = z_of_wl(G.side_panel_top_wl)
_T = G.side_panel_thickness
_PTS = np.array(G.side_panel_heights, dtype=float)
_BOTTOM = CubicSpline(_PTS[:, 0], _PTS[:, 1], bc_type="natural")


def side_bottom_depth(u: float) -> float:
    """Depth of the side's bottom edge below the top edge at side coordinate u (smooth curve)."""
    return float(_BOTTOM(u))


def bottom_z(fs: float) -> float:
    return Z_TOP - side_bottom_depth(fs - G.fs_f22)


def _w_pieces() -> list[tuple[float, float, float, float]]:
    """(x0, x1, half width at x0, d(half width)/dx) pieces of the plan bend.

    Breakpoints are the config stations; forward of the front seat bulkhead the width is held at
    ``fuselage_inner_width_fwd`` (unsourced, equal to the first station's width), and the last
    printed segment is extrapolated aft (to the firewall and the longeron's 0.5 overhang).
    """
    st = list(G.fuselage_inner_width_stations)
    if abs(G.fuselage_inner_width_fwd - st[0][1]) > 1e-9:
        raise ValueError(
            "forward inner width must equal the first station width (no kink modelled)"
        )
    far = G.fs_f22 + G.side_panel_length + 100.0
    pieces = [(G.fs_f22, st[1][0], st[0][1] / 2, 0.0)]
    for (x0, w0), (x1, w1) in pairwise(st[1:]):
        pieces.append((x0, x1, w0 / 2, (w1 - w0) / (x1 - x0) / 2))
    (x0, w0), (x1, w1) = st[-2], st[-1]
    pieces.append((x1, far, w1 / 2, (w1 - w0) / (x1 - x0) / 2))
    return pieces


_W_PIECES = _w_pieces()


def plan_bend_points() -> list[tuple[float, float]]:
    """(FS, half width) at every breakpoint of the plan bend, forward edge to the longeron's aft overhang.

    Linear between points. The sides, longerons and inside plies are bent by y' = y + half_width(x), so a
    reader can flatten them again (the lab lays the sides flat on the table for chapter 5).
    """
    end = G.fs_f22 + G.side_panel_length + 1.0
    pts = [(x0, h0) for x0, _x1, h0, _s in _W_PIECES if x0 < end]
    return pts + [(end, half_width(end))]


def half_width(fs: float) -> float:
    """Half of the inner width between the sides at FS (the plan bend)."""
    for x0, x1, h0, s in _W_PIECES:
        if fs <= x1:
            return h0 + s * (fs - x0)
    raise ValueError(fs)


# --- side ------------------------------------------------------------------------------------------
def _bottom_samples() -> list[tuple[float, float]]:
    """Bottom edge (x, z) sampled every 1 in of u; includes every printed station (0, 10 .. 100, 103)."""
    n = round(G.side_panel_length)
    return [(G.fs_f22 + u, Z_TOP - side_bottom_depth(u)) for u in range(n + 1)]


def _flat_side() -> cq.Workplane:
    """Flat side, inside face at y = 0, thickness out to +y, plan not yet bent."""
    L = G.side_panel_length
    cw, cd = G.side_spar_cutout
    x0 = G.fs_f22
    bottom = _bottom_samples()
    wp = (
        cq.Workplane("XZ")
        .moveTo(x0, Z_TOP)
        .lineTo(x0 + L - cw, Z_TOP)
        .lineTo(x0 + L - cw, Z_TOP - cd)
        .lineTo(x0 + L, Z_TOP - cd)
        .lineTo(*bottom[-1])
        .spline(list(reversed(bottom[:-1])), includeCurrent=True)
        .close()
    )
    return wp.extrude(
        -_T
    )  # the XZ workplane normal is -y, so a negative extrude goes +y


def _sight_gauge_cutter() -> cq.Workplane:
    """Trapezoid groove on the inside face, read from p36 section B-B.

    Tuple (u, down, reach, floor, foam): the opening at the face runs ``reach`` forward and
    ``reach`` aft of the reference line at u; the flat floor is ``floor`` wide, just forward of the
    reference line (u - floor to u), leaving ``foam`` of the side (depth thickness - foam). The
    forward flank runs from u - reach to u - floor, the aft flank from u to u + reach. Vertically
    from v 1.0 (below the longeron) down to v ``down``.
    """
    u, down, reach, floor, foam = G.side_sight_gauge
    depth = _T - foam
    over = 0.2  # overshoot past the face so the cut is clean; extended along the flank slopes
    cx = G.fs_f22 + u
    fwd_slope = depth / (reach - floor)
    aft_slope = depth / reach
    pts = [
        (cx - reach - over / fwd_slope, -over),
        (cx - floor, depth),
        (cx, depth),
        (cx + reach + over / aft_slope, -over),
    ]
    v0 = 1.0
    return (
        cq.Workplane("XY", origin=(0, 0, Z_TOP - down))
        .polyline(pts)
        .close()
        .extrude(down - v0)
    )


def _dish_cutter() -> cq.Workplane:
    """Spherical-cap dish on the inside face: diameter ``dia`` at the face, ``depth`` deep."""
    u, down, dia, depth = G.side_dish
    r = dia / 2
    big_r = (r**2 + depth**2) / (2 * depth)
    return (
        cq.Workplane("XY")
        .sphere(big_r)
        .translate((G.fs_f22 + u, depth - big_r, Z_TOP - down))
    )


def _bend(solid: cq.Workplane) -> cq.Workplane:
    """Bend the flat part in plan: piecewise affine shear y' = y + a + b*x, then fuse the pieces."""
    parts = []
    for x0, x1, h0, slope in _W_PIECES:
        box = (
            cq.Workplane("XY")
            .box(x1 - x0, 80, 160, centered=False)
            .translate((x0, -40, -80))
        )
        clip = solid.intersect(box)
        if not clip.vals() or clip.val().Volume() < 1e-9:
            continue
        a = h0 - slope * x0
        m = cq.Matrix([[1, 0, 0, 0], [slope, 1, 0, a], [0, 0, 1, 0]])
        parts.append(cq.Workplane("XY").add(clip.val().transformGeometry(m)))
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p, clean=True)
    return out


def _sides() -> tuple[cq.Workplane, cq.Workplane]:
    flat = _flat_side().cut(_sight_gauge_cutter())
    right = _bend(flat.cut(_dish_cutter()))
    left = _bend(flat).mirror("XZ")
    return left, right


def _longerons() -> tuple[cq.Workplane, cq.Workplane]:
    vert, horiz, length = 1.0, 0.7, 103.5  # plans-1980:p37; also in the part note
    # bonded to the side's inside face (flat frame: inside face at y = 0), so the 0.7 lies inboard
    flat = (
        cq.Workplane("XY")
        .box(length, horiz, vert, centered=False)
        .translate((G.fs_f22, -horiz, Z_TOP - vert))
    )
    right = _bend(flat)
    return right.mirror("XZ"), right


# --- seat bulkheads ---------------------------------------------------------------------------------
def _place(
    solid: cq.Workplane, p0: tuple[float, float], p1: tuple[float, float]
) -> tuple[cq.Workplane, float]:
    """Move a local-frame plate (X along its length, Z along its thickness) onto the segment p0->p1.

    Returns the placed solid and the segment length.
    """
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    phi = math.degrees(math.atan2(dz, dx))
    mid = ((p0[0] + p1[0]) / 2, 0.0, (p0[1] + p1[1]) / 2)
    return solid.rotate((0, 0, 0), (0, 1, 0), -phi).translate(mid), math.hypot(dx, dz)


def _front_segment() -> tuple[tuple[float, float], tuple[float, float]]:
    return (
        (G.fs_front_seat_bkhd_bottom, bottom_z(G.fs_front_seat_bkhd_bottom)),
        (G.fs_front_seat_bkhd_top, Z_TOP),
    )


def _rear_segment() -> tuple[tuple[float, float], tuple[float, float]]:
    return (
        (G.fs_rear_seat_bkhd_bottom, bottom_z(G.fs_rear_seat_bkhd_bottom)),
        (G.fs_rear_seat_bkhd_top, Z_TOP - G.side_spar_cutout[1]),
    )


def front_bkhd_outline() -> list[tuple[float, float]]:
    """(s, y) outline of the front seat bulkhead, s along its length, with the corner notches."""
    half_l, half_w = G.front_seat_bkhd_length / 2, G.front_seat_bkhd_width / 2
    (ty, ts), (by, bs) = G.front_seat_bkhd_notch_top, G.front_seat_bkhd_notch_bottom
    right = [
        (-half_l, half_w - by),
        (-half_l + bs, half_w - by),
        (-half_l + bs, half_w),
        (half_l - ts, half_w),
        (half_l - ts, half_w - ty),
        (half_l, half_w - ty),
    ]
    left = [(s, -y) for s, y in reversed(right)]
    return right + left


def rear_bkhd_outline() -> list[tuple[float, float]]:
    """(s, y) outline of the rear seat bulkhead: trapezoid, lower corners notched."""
    half_l = G.rear_seat_bkhd_length / 2
    hb, ht = G.rear_seat_bkhd_bottom_width / 2, G.rear_seat_bkhd_top_width / 2
    ny, ns = G.rear_seat_bkhd_notch
    y_at = lambda s: hb + (ht - hb) * (s + half_l) / (2 * half_l)
    right = [
        (-half_l, hb - ny),
        (-half_l + ns, hb - ny),
        (-half_l + ns, y_at(-half_l + ns)),
        (half_l, ht),
    ]
    left = [(s, -y) for s, y in reversed(right)]
    return right + left


_EXT = 2.5  # the inclined plates are built this much longer than needed at each end, then clipped


def _front_plate_outline(h: float, front_t_half: float) -> list[tuple[float, float]]:
    """(s, y) outline of the long front plate, s from the segment midpoint (ends at +-h), with the
    corner notches measured from the segment ends (top 0.7 y x 1.5 along s, bottom 0.7 x 0.7)."""
    half_w = G.front_seat_bkhd_width / 2
    (ty, ts), (by, bs) = G.front_seat_bkhd_notch_top, G.front_seat_bkhd_notch_bottom
    # the horizontal clip ends the two big faces at s = h -+ shift; measure the notches from the
    # nearer face end so they clear the longerons (1.0 deep) on both faces
    f0, f1 = _front_segment()
    shift = front_t_half * (f1[0] - f0[0]) / (f1[1] - f0[1])
    right = [
        (-h - _EXT, half_w - by),
        (-h + shift + bs, half_w - by),
        (-h + shift + bs, half_w),
        (h - shift - ts, half_w),
        (h - shift - ts, half_w - ty),
        (h + _EXT, half_w - ty),
    ]
    return right + [(s, -y) for s, y in reversed(right)]


def _rear_plate_outline(h: float) -> list[tuple[float, float]]:
    """(s, y) outline of the long rear plate: trapezoid through 20.6 at s = -h and 18.7 at s = +h
    (extended past both ends), lower corners notched from the bottom end."""
    hb, ht = G.rear_seat_bkhd_bottom_width / 2, G.rear_seat_bkhd_top_width / 2
    ny, ns = G.rear_seat_bkhd_notch
    y_at = lambda s: hb + (ht - hb) * (s + h) / (2 * h)
    right = [
        (-h - _EXT, hb - ny),
        (-h + ns, hb - ny),
        (-h + ns, y_at(-h + ns)),
        (h + _EXT, y_at(h + _EXT)),
    ]
    return right + [(s, -y) for s, y in reversed(right)]


def _plate(outline: list[tuple[float, float]], t: float) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0, 0, -t / 2)).polyline(outline).close().extrude(t)
    )


def long_face_length(
    solid: cq.Workplane, p0: tuple[float, float], p1: tuple[float, float]
) -> float:
    """Longest extent along the slope p0->p1 of the plate's two big faces."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dz)
    d = (dx / n, dz / n)
    best = 0.0
    for f in solid.faces().vals():
        c = f.normalAt()
        if abs(-c.x * d[1] + c.z * d[0]) < 0.999:
            continue
        s = [v.X * d[0] + v.Z * d[1] for v in f.Vertices()]
        best = max(best, max(s) - min(s))
    return best


def _seat_bulkheads() -> tuple[cq.Workplane, cq.Workplane, dict[str, float]]:
    # front: long inclined plate on the mid-plane line, clipped flush with the longerons (top,
    # z = Z_TOP) and the side bottom (bottom) by horizontal planes (p39)
    t = G.front_seat_bkhd_thickness
    f0, f1 = _front_segment()
    hf = math.hypot(f1[0] - f0[0], f1[1] - f0[1]) / 2
    front, front_seg = _place(_plate(_front_plate_outline(hf, t / 2), t), f0, f1)
    front = front.intersect(_box(0, 500, -50, 50, f0[1], Z_TOP))

    # rear: clipped at the spar's forward face (vertical plane) and the side-bottom horizontal
    tr = G.rear_seat_bkhd_thickness
    r0, r1 = _rear_segment()
    hr = math.hypot(r1[0] - r0[0], r1[1] - r0[1]) / 2
    rear = _plate(_rear_plate_outline(hr), tr)
    glass = (
        0.05  # p34: the glass left over the 8 in foam circle (a book fact, not config)
    )
    pocket = (
        cq.Workplane("XY", origin=(0, 0, -tr / 2))
        .circle(G.rear_seat_bkhd_foam_circle_dia / 2)
        .extrude(tr - glass)
    )
    hole = (
        cq.Workplane("XY", origin=(0, 0, -tr / 2 - 1))
        .circle(G.rear_seat_bkhd_access_dia / 2)
        .extrude(tr + 2)
    )
    rear = rear.cut(pocket).cut(hole)
    rear, rear_seg = _place(rear, r0, r1)
    rear = rear.intersect(_box(0, r1[0], -50, 50, r0[1], 100))
    return front, rear, {"front": front_seg, "rear": rear_seg}


# --- representational parts ---------------------------------------------------------------------------
def _box(
    x0: float, x1: float, y0: float, y1: float, z0: float, z1: float
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def _bulkhead_plate(
    fs: float, thickness: float, z_low: float | None = None, outer: bool = False
) -> cq.Workplane:
    """Plate whose forward face is at ``fs``, spanning the inner (or outer) width, top at Z_TOP."""
    hw = half_width(fs) + (_T if outer else 0.0)
    return _box(
        fs, fs + thickness, -hw, hw, bottom_z(fs) if z_low is None else z_low, Z_TOP
    )


def _bottom_plate() -> cq.Workplane:
    x0 = G.fs_f22
    x1 = G.fs_rear_seat_bkhd_bottom + G.bottom_aft_trim
    n = math.floor(x1 - x0)
    xs = [x0 + i for i in range(n + 1)] + [x1]
    t = G.bottom_foam_thickness
    upper = [(x, bottom_z(x)) for x in xs]
    lower = [(x, bottom_z(x) - t) for x in xs]
    prof = (
        cq.Workplane("XZ", origin=(0, -40, 0))
        .moveTo(*upper[0])
        .spline(upper[1:], includeCurrent=True)
        .lineTo(*lower[-1])
        .spline(list(reversed(lower[:-1])), includeCurrent=True)
        .close()
        .extrude(-80)
    )
    out = G.bottom_trim_outboard
    bps = (
        [x0]
        + [
            b
            for b in (G.fs_front_seat_bkhd_top, G.fs_rear_seat_bkhd_bottom)
            if x0 < b < x1
        ]
        + [x1]
    )
    right = [(x, half_width(x) + out) for x in bps]
    plan = (
        cq.Workplane("XY", origin=(0, 0, -60))
        .polyline(right + [(x, -y) for x, y in reversed(right)])
        .close()
        .extrude(120)
    )
    return prof.intersect(plan)


_SIDE_CITE = (_P36, _P38, _P37)


def _build() -> dict[str, FusePart]:
    parts: dict[str, FusePart] = {}
    left, right = _sides()
    parts["side_left"] = FusePart(
        "side_left",
        left,
        "book",
        (_P36, _P38),
        note=(
            "0.8 in foam, 103 long; bottom edge a natural cubic spline through the 12 printed "
            "depths (p36); spar cutout 6.5 x 8.5 (p36/p38); fuel sight gauge on the inside face "
            "(p36 section B-B: opening u 79.5 to 84.5 at the face, 1.0 flat floor u 81.0 to 82.0 "
            "leaving 0.2 of foam, v 1.0 to 9.15). "
            "Plan bend by piecewise shear through the derived inner-width stations; thickness is "
            "kept along y, not normal to the bent face."
        ),
    )
    parts["side_right"] = FusePart(
        "side_right",
        right,
        "book",
        (_P36, _P38, _P37),
        note=(
            "as side_left, plus the dish on the inside face: spherical cap, 8 in dia, 0.5 deep "
            "(the text says 0.5, section C-C shows 0.3: conflict inside p36/p37)."
        ),
    )
    front, rear, seg = _seat_bulkheads()
    front_long = long_face_length(front, *_front_segment())
    rear_long = long_face_length(rear, *_rear_segment())
    logger.info(
        "seat bulkhead long faces: front %.2f (printed %.2f), rear %.2f (printed %.2f)",
        front_long,
        G.front_seat_bkhd_length,
        rear_long,
        G.rear_seat_bkhd_length,
    )
    parts["front_seat_bkhd"] = FusePart(
        "front_seat_bkhd",
        front,
        "book",
        (_P33, _P36),
        note=(
            "0.8 x 23 inclined plate on the mid-plane line from (FS 63.55, side bottom) to "
            f"(FS 81.75, top edge), segment {seg['front']:.2f} in, built long and clipped by "
            "horizontal planes at the top edge (flush with the longerons) and at the side bottom "
            "(p39); the 0.7 end tapers are what that fit leaves on the plate. "
            f"Long-face length {front_long:.2f} in (printed {G.front_seat_bkhd_length}). "
            "Corner notches per p33. The small control holes are not modelled: the page is not "
            "to scale."
        ),
    )
    parts["rear_seat_bkhd"] = FusePart(
        "rear_seat_bkhd",
        rear,
        "book",
        (_P34, _P36, _P38),
        note=(
            "0.8 trapezoid 20.6 bottom / 18.7 top on the mid-plane line from (FS 107, side "
            f"bottom) to (FS 118.5, cutout depth), segment {seg['rear']:.2f} in, built long and "
            "clipped at the spar's forward face (vertical plane FS 118.5, the 45 degree bevel's "
            "job) and at the side bottom at FS 107 (horizontal plane, the 35 degree bevel's job). "
            f"Long-face length {rear_long:.2f} in (printed slant {G.rear_seat_bkhd_length}). "
            "7 in through hole, 8 in pocket from the back face leaving 0.05 of glass. Side "
            "tapers are omitted."
        ),
    )
    lon_left, lon_right = _longerons()
    lon_note = (
        "spruce 1.0 (vertical) x 0.7 (y) x 103.5, flush with the top edge and the front, "
        "0.5 proud aft (p37). Bonded to the side's inside face: the 0.7 lies inboard of it, "
        "so it does not overlap the side foam; it runs across the spar cutout."
    )
    parts["top_longeron_left"] = FusePart(
        "top_longeron_left", lon_left, "book", (_P37,), note=lon_note
    )
    parts["top_longeron_right"] = FusePart(
        "top_longeron_right", lon_right, "book", (_P37,), note=lon_note
    )

    parts["f22"] = FusePart(
        "f22",
        _bulkhead_plate(G.fs_f22, FITTED_F22_THICKNESS),
        "representational",
        note=_SHEET_NOTE,
    )
    f28 = _bulkhead_plate(
        G.fs_f28, FITTED_F28_THICKNESS, z_low=Z_TOP - FITTED_F28_BAND_DEPTH
    )
    parts["f28"] = FusePart(
        "f28", f28, "representational", note=_SHEET_NOTE + "; top band only"
    )
    leg_w, leg_h = FITTED_PANEL_LEG_CUTOUT
    panel = _bulkhead_plate(G.fs_panel, FITTED_PANEL_THICKNESS)
    hw = half_width(G.fs_panel)
    zb = bottom_z(G.fs_panel)
    for sgn in (-1, 1):
        y_far = sgn * (hw - FITTED_PANEL_LEG_INSET)
        y_near = y_far - sgn * leg_w
        panel = panel.cut(
            _box(
                G.fs_panel - 1,
                G.fs_panel + 1,
                min(y_far, y_near),
                max(y_far, y_near),
                zb - 1,
                zb + leg_h,
            )
        )
    parts["panel"] = FusePart(
        "panel", panel, "representational", note=_SHEET_NOTE + "; leg cutouts fitted"
    )
    parts["firewall"] = FusePart(
        "firewall",
        _bulkhead_plate(G.fs_firewall, FITTED_FIREWALL_THICKNESS, outer=True),
        "representational",
        note=_SHEET_NOTE
        + "; aft of FS 125, spans the outer width (p35 prints A4 only)",
    )
    parts["bottom"] = FusePart(
        "bottom",
        _bottom_plate(),
        "representational",
        note=(
            "uncarved 1.6 plate under the sides, FS 22 to the rear seat bulkhead bottom plus the "
            "aft trim, 0.7 outboard of the inside faces (p42/p44); the carved contour on p44 is "
            "partial, so none is modelled."
        ),
    )
    return parts


@lru_cache(maxsize=1)
def _cached() -> dict[str, FusePart]:
    return _build()


def build_fuselage() -> dict[str, FusePart]:
    """All fuselage-box parts by name (cached; the returned dict is a copy)."""
    return dict(_cached())


# --- DXF ---------------------------------------------------------------------------------------------
def _side_outline_wp(right: bool) -> cq.Workplane:
    """Flat side outline in (u, -v) for a DXF, plus the sight gauge and (right only) dish."""
    L = G.side_panel_length
    cw, cd = G.side_spar_cutout
    n = round(L)
    bottom = [(u, -side_bottom_depth(u)) for u in range(n + 1)]
    wp = (
        cq.Workplane("XY")
        .moveTo(0, 0)
        .lineTo(L - cw, 0)
        .lineTo(L - cw, -cd)
        .lineTo(L, -cd)
        .lineTo(*bottom[-1])
        .spline(list(reversed(bottom[:-1])), includeCurrent=True)
        .close()
    )
    u, length, reach, _, _ = G.side_sight_gauge
    wp = (
        wp.moveTo(u - reach, -1.0)
        .lineTo(u + reach, -1.0)
        .lineTo(u + reach, -length)
        .lineTo(u - reach, -length)
        .close()
    )
    if right:
        du, down, dia, _ = G.side_dish
        wp = wp.moveTo(du, -down).circle(dia / 2)
    return wp


def _bkhd_outline_wp(points: list[tuple[float, float]]) -> cq.Workplane:
    return cq.Workplane("XY").polyline(points).close()


class BookFuselage(AircraftComponent):
    """The fuselage box from the book: sides, seat bulkheads, longerons, fitted bulkheads, bottom."""

    def __init__(
        self,
        name: str = "fuselage_book",
        description: str = "Long-EZ fuselage box, plans chapters 4-6",
    ):
        super().__init__(name, description)

    @property
    def parts(self) -> dict[str, FusePart]:
        return build_fuselage()

    def _build_geometry(self) -> cq.Workplane:
        compound = cq.Compound.makeCompound(
            [p.solid.val() for p in self.parts.values()]
        )
        self._geometry = cq.Workplane("XY").add(compound)
        self.add_metadata("fidelity", {n: p.fidelity for n, p in self.parts.items()})
        return self._geometry

    def _dxf_outlines(self) -> dict[str, cq.Workplane]:
        return {
            "side_left": _side_outline_wp(False),
            "side_right": _side_outline_wp(True),
            "front_seat_bkhd": _bkhd_outline_wp(front_bkhd_outline()),
            "rear_seat_bkhd": _bkhd_outline_wp(rear_bkhd_outline())
            .moveTo(0, 0)
            .circle(G.rear_seat_bkhd_foam_circle_dia / 2)
            .moveTo(0, 0)
            .circle(G.rear_seat_bkhd_access_dia / 2),
        }

    def export_dxf(self, output_path: Path) -> Path:
        """Write the two side outlines and the two seat bulkhead outlines; returns the directory."""
        output_path.mkdir(parents=True, exist_ok=True)
        for name, wp in self._dxf_outlines().items():
            f = output_path / f"{self.name}_{name}.dxf"
            cq.exporters.export(wp, str(f), exportType="DXF")
            self._write_artifact_metadata(f, artifact_type="DXF")
        return output_path

    def manufacturing_plan(self, output_path: Path) -> dict[str, Any]:
        """Write the DXF outlines. The book prints no tolerance for them, so none is reported."""
        directory = self.export_dxf(output_path)
        paths = sorted(directory.glob(f"{self.name}_*.dxf"))
        return {
            "sheet_templates": {
                "paths": paths,
                "format": "DXF",
                "tolerance": None,
                "artifact": "fuselage_side_and_seat_bulkhead_outlines",
            }
        }


__all__ = ["BookFuselage", "FusePart", "build_fuselage", "side_bottom_depth"]
