"""
Open-EZ PDE: Long-EZ nose structure forward of F22 (plans chapter 13, pdf pages p73-p83, p171)
==============================================================================================

Same fidelity labels and frame as ``core.fuselage_book``: model x = F.S. (aft positive), y = B.L. (right
positive), z = ``z_of_wl(W.L.)``.

What the book prints, and what it does not:

- Printed (medium to high confidence, hand-dimensioned sheets): NG30 plates 0.2 thick with 3.0 between them (p77);
  floor block 20.9 x 8.2 / 1.6 x 1.6 thick, side block 21.9 long, 15.6 high at F22 and 5.5 + 2.8 at the NG31 end
  (p79); pedal pivot block 6.1 from NG30 (p79); top block 19.3 long, 19.6 aft, 7.0 forward (p82); static port 8 in
  forward of the panel, W.L. 13, left side (p82); nose tip F.S. -6.8 (p171).
- NOT printed: every outline (the A6/A7 template sheets are not held), the nose skin's cross-section, where NG31
  sits inside the 0.1 to 1.1 range the two block lengths give, the plate heights, the pedal tube routing, the door,
  the strut cover and the nose-gear box. The cobelu figures for the NG31 disc (5.6 to the edge, 9.2 high) are not on
  the owner's scan.

Every part is therefore ``representational``: a printed size may be used, but the plate or block is a stand-in.
No part is tagged book or derived. Nothing here sets the nose-wheel axle station (that is the p171 / Owner's Manual
conflict, see ``core.landing_gear_book.build_nose_gear``).
"""

from __future__ import annotations

import math
from functools import lru_cache
from itertools import pairwise

import cadquery as cq

from .fuselage_book import FusePart, G, half_width, z_of_wl
from .nose_gear_kin import default_pivot_wl, ng6_pivot_for_axle

_P73, _P77, _P79, _P82, _P83, _P171 = (
    f"plans-1980:p{n}" for n in (73, 77, 79, 82, 83, 171)
)

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_FS_NG31 = (
    (G.fs_ng31_min + G.fs_ng31_max) / 2
)  # fitted, not book: the midpoint of the 0.1 to 1.1 range the p79 block lengths give
FITTED_SIDE_BLOCK_T = 1.0  # fitted, not book: side block thickness across (p79 prints length and height only)
FITTED_FLOOR_DISH = 0.4  # fitted, not book: how far the floor block's inboard edge dishes outboard at mid length (p79 says "dished")
FITTED_SKIN_T = 0.12  # fitted, not book: 2-ply BID drawn at the visual ply thickness of the fuselage plies (not to scale)
FITTED_TOP_BLOCK_T = (
    2.0  # fitted, not book: top block thickness (p82 gives the plan only)
)
FITTED_PLATE_CLEAR = (
    0.1  # fitted, not book: NG30 plate top stands this far under the top block
)
FITTED_PIVOT_BLOCK = (
    2.0,
    1.5,
)  # fitted, not book: (x length, y width) of the pedal pivot block; thickness is the printed 1.6
FITTED_PIVOT_BLOCK_X_FROM_F22 = (
    3.0  # fitted, not book: the "X = 3" default read as 3 in forward of F22
)
FITTED_NUTPLATE = (
    1.0,
    0.7,
    0.06,
)  # fitted, not book: aluminium nutplate 1 x 0.7 (read from the p79 sketch), thickness fitted
FITTED_PEDAL_OD = 0.5  # fitted, not book: 1/2 OD tube (read from the p79 sketch)
FITTED_PEDAL_LEGS = (
    5.75,
    6.2,
    7.0,
)  # fitted, not book: legs read as 5.75 inboard, 6.2 up, 7.0 forward
FITTED_NG31_DISC = (
    5.6,
    9.2,
)  # cobelu figures (half width, height), NOT on the owner's scan
FITTED_NG31_T = 0.25  # fitted, not book
FITTED_F6_T = 0.2  # fitted, not book
FITTED_F6_AFT_OF_NG31 = 0.4  # fitted, not book
FITTED_PITOT = (
    0.125,
    6.0,
    10.0,
    4.4,
)  # fitted, not book: (radius, forward of NG31, aft of F22, W.L.)
FITTED_STATIC_PORT = (0.5, 0.1)  # fitted, not book: (marker radius, thickness)
FITTED_DOOR = (
    6.7,
    15.3,
    4.0,
    0.7,
    0.08,
)  # fitted, not book: (x0, x1, half width, flange, thickness) of the door panel; p83 dimensions are loose
FITTED_COVER = (
    1.9,
    0.15,
)  # fitted, not book: (half width, thickness) of the strut cover
FITTED_NB_BOX = (
    31.0,
    3.2,
    10.0,
    0.2,
)  # fitted, not book: (forward F.S., half width, height, wall); aft end is the panel
FITTED_TIP_MIN = 0.02  # fitted, not book: smallest section scale at the tip station

NOSE_BOTTOM_Z = z_of_wl(
    G.wl_fuselage_bottom_3view
)  # the outside skin line (p171 side view W.L. 0.9)
_T30, _GAP = G.ng30_thickness_in, G.ng30_gap_in
_Y_IN = _GAP / 2  # inner face of each NG30 plate
_Y_OUT = _Y_IN + _T30  # outer face of each NG30 plate
_FS_AFT = G.fs_f22
_FS_FLOOR_FWD = _FS_AFT - G.floor_block_length_in
_FS_SIDE_FWD = _FS_AFT - G.side_block_length_in
_FLOOR_OUT_AFT = (
    _Y_OUT + G.floor_block_width_in
)  # 9.9: the plan "9.8" read of the captain, plus the plate's 0.1 on the inside
_FLOOR_OUT_FWD = _Y_OUT + G.floor_block_thickness_in  # the 1.6 end of the wedge (p79)
_FLOOR_SLOPE = (_FLOOR_OUT_AFT - _FLOOR_OUT_FWD) / G.floor_block_length_in
_H_AFT = G.side_block_height_f22_in
_H_FWD = G.side_block_height_ng31_above_in + G.side_block_height_ng31_below_in
_H_SLOPE = (_H_AFT - _H_FWD) / (_FS_AFT - FITTED_FS_NG31)
_BEVEL = math.radians(
    17.0
)  # fitted, not book: side block ends bevelled 17 deg, a reading of the p79 sketch
_TIP = G.fs_nose
_TIP_LEN = _FS_SIDE_FWD - _TIP  # the tip rounds over this length


def floor_outer_y(fs: float) -> float:
    """Outer edge of the floor wedge at fs (straight in plan, extended a little past its ends)."""
    return _FLOOR_OUT_FWD + _FLOOR_SLOPE * (fs - _FS_FLOOR_FWD)


def nose_height(fs: float) -> float:
    """Height of the side block (and the nose) over the skin line at fs, for fs in the straight run."""
    return _H_FWD + _H_SLOPE * (fs - FITTED_FS_NG31)


def nose_top_z(fs: float) -> float:
    return NOSE_BOTTOM_Z + nose_height(fs)


def _dims(fs: float) -> tuple[float, float]:
    """(half width, height) of the OUTER nose section at fs: straight run aft of the side block's forward end, an
    elliptic round-over to the tip forward of it."""
    x = max(fs, _FS_SIDE_FWD)
    w = floor_outer_y(x) + FITTED_SIDE_BLOCK_T
    h = nose_height(x)
    if fs < _FS_SIDE_FWD:
        phi = math.acos(max(-1.0, min(1.0, (_FS_SIDE_FWD - fs) / _TIP_LEN)))
        e = max(math.sin(phi), FITTED_TIP_MIN)
        w, h = w * e, h * e
    return w, h


def _section(fs: float, w: float, h: float, zb: float) -> cq.Wire:
    pts = [(fs, -w, zb), (fs, w, zb), (fs, w, zb + h), (fs, -w, zb + h)]
    return cq.Wire.makePolygon([cq.Vector(*p) for p in pts], close=True)


def _stations() -> list[float]:
    n = 8
    fwd = [
        _FS_SIDE_FWD - _TIP_LEN * math.cos(k * math.pi / (2 * n)) for k in range(n + 1)
    ]  # tip first, dense at the tip
    aft = [_FS_SIDE_FWD + (_FS_AFT - _FS_SIDE_FWD) * i / 10 for i in range(1, 11)]
    return fwd + aft


@lru_cache(maxsize=1)
def _envelope() -> cq.Workplane:
    """The outer nose envelope, tip to F22: a ruled loft of flat-bottomed rectangular sections."""
    wires = [_section(fs, *_dims(fs), NOSE_BOTTOM_Z) for fs in _stations()]
    return cq.Workplane(obj=cq.Solid.makeLoft(wires, True))


def _skin() -> cq.Workplane:
    t = FITTED_SKIN_T
    st = [fs for fs in _stations() if _dims(fs)[0] > 0.3 * _dims(_FS_SIDE_FWD)[0]]
    wires = []
    for fs in st:
        w, h = _dims(fs)
        wires.append(_section(fs, w - t, h - 2 * t, NOSE_BOTTOM_Z + t))
    # run the cavity past F22 so the shell is open at its aft end
    w, h = _dims(_FS_AFT)
    wires.append(_section(_FS_AFT + 0.5, w - t, h - 2 * t, NOSE_BOTTOM_Z + t))
    inner = cq.Workplane(obj=cq.Solid.makeLoft(wires, True))
    return _envelope().cut(inner)


# --- extrusion helpers ----------------------------------------------------------------------------------
def _plan(
    pts: list[tuple[float, float]], z0: float = -80.0, z1: float = 80.0
) -> cq.Workplane:
    return (
        cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    )


def _side(pts: list[tuple[float, float]]) -> cq.Workplane:
    return cq.Workplane("XZ").polyline(pts).close().extrude(40.0, both=True)


def _slab(plan_pts, side_pts) -> cq.Workplane:
    return _plan(plan_pts).intersect(_side(side_pts))


def _box(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
    )


def _cyl(p, q, r) -> cq.Workplane:
    p, q = cq.Vector(*p), cq.Vector(*q)
    return cq.Workplane(obj=cq.Solid.makeCylinder(r, (q - p).Length, p, q - p))


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in solids]))


SIDES = (-1, 1)


# --- the parts --------------------------------------------------------------------------------------------
def _plate_top(fs: float) -> float:
    return nose_top_z(fs) - FITTED_TOP_BLOCK_T - FITTED_PLATE_CLEAR


def _ng30_plates() -> cq.Workplane:
    x0, x1 = FITTED_FS_NG31, _FS_AFT
    side = [
        (x0, NOSE_BOTTOM_Z),
        (x1, NOSE_BOTTOM_Z),
        (x1, _plate_top(x1)),
        (x0, _plate_top(x0)),
    ]
    return _compound(
        [
            _slab(
                [(x0, s * _Y_IN), (x1, s * _Y_IN), (x1, s * _Y_OUT), (x0, s * _Y_OUT)],
                side,
            )
            for s in SIDES
        ]
    )


def _floor_blocks() -> cq.Workplane:
    x0, x1 = _FS_FLOOR_FWD, _FS_AFT
    n = 10
    dish = [
        (x0 + (x1 - x0) * i / n, _Y_OUT + FITTED_FLOOR_DISH * math.sin(math.pi * i / n))
        for i in range(n + 1)
    ]
    side = [
        (x0, NOSE_BOTTOM_Z),
        (x1, NOSE_BOTTOM_Z),
        (x1, NOSE_BOTTOM_Z + G.floor_block_thickness_in),
        (x0, NOSE_BOTTOM_Z + G.floor_block_thickness_in),
    ]
    sol = []
    for s in SIDES:
        plan = [(x, s * y) for x, y in dish] + [
            (x1, s * _FLOOR_OUT_AFT),
            (x0, s * _FLOOR_OUT_FWD),
        ]
        sol.append(_slab(plan, side))
    return _compound(sol)


def _side_blocks() -> cq.Workplane:
    x0, x1 = _FS_SIDE_FWD, _FS_AFT
    bev = FITTED_SIDE_BLOCK_T * math.tan(
        _BEVEL
    )  # forward end bevelled 17 deg in plan: the outer corner is further aft
    side = [
        (x0, NOSE_BOTTOM_Z),
        (x1, NOSE_BOTTOM_Z),
        (x1, nose_top_z(x1)),
        (x0, nose_top_z(x0)),
    ]
    sol = []
    for s in SIDES:
        yi0, yi1 = floor_outer_y(x0), floor_outer_y(x1)
        plan = [
            (x0, s * yi0),
            (x1, s * yi1),
            (x1, s * (yi1 + FITTED_SIDE_BLOCK_T)),
            (x0 + bev, s * (yi0 + FITTED_SIDE_BLOCK_T + _FLOOR_SLOPE * bev)),
        ]
        sol.append(_slab(plan, side))
    return _compound(sol)


def _top_block() -> cq.Workplane:
    x0, x1 = _FS_AFT - G.top_block_length_in, _FS_AFT
    hw0, hw1 = G.top_block_width_fwd_in / 2, G.top_block_width_aft_in / 2
    plan = [(x0, -hw0), (x1, -hw1), (x1, hw1), (x0, hw0)]
    t = FITTED_TOP_BLOCK_T
    side = [
        (x0, nose_top_z(x0) - t),
        (x1, nose_top_z(x1) - t),
        (x1, nose_top_z(x1)),
        (x0, nose_top_z(x0)),
    ]
    return _slab(plan, side)


def _pivot_x() -> float:
    return _FS_AFT - FITTED_PIVOT_BLOCK_X_FROM_F22


def _pivot_y() -> float:
    return _Y_OUT + G.pedal_block_from_ng30_in


def _pivot_top() -> float:
    return (
        NOSE_BOTTOM_Z + 2 * G.floor_block_thickness_in
    )  # on the floor block (1.6), plate 1.6 thick


def _pivot_blocks() -> cq.Workplane:
    lx, wy = FITTED_PIVOT_BLOCK
    nx, ny, nt = FITTED_NUTPLATE
    z0 = NOSE_BOTTOM_Z + G.floor_block_thickness_in
    sol = []
    for s in SIDES:
        yc = s * _pivot_y()
        blk = _box(
            _pivot_x() - lx / 2,
            _pivot_x() + lx / 2,
            yc - wy / 2,
            yc + wy / 2,
            z0,
            _pivot_top(),
        )
        nut = _box(
            _pivot_x() - nx / 2,
            _pivot_x() + nx / 2,
            yc - ny / 2,
            yc + ny / 2,
            _pivot_top(),
            _pivot_top() + nt,
        )
        sol.append(blk.union(nut))
    return _compound(sol)


def _pedal_path(s: int) -> list[tuple[float, float, float]]:
    inb, up, fwd = FITTED_PEDAL_LEGS
    p0 = (_pivot_x(), s * _pivot_y(), _pivot_top() + FITTED_PEDAL_OD / 2)
    p1 = (p0[0], p0[1] - s * inb, p0[2])
    p2 = (p1[0], p1[1], p1[2] + up)
    p3 = (p2[0] - fwd, p2[1], p2[2])
    return [p0, p1, p2, p3]


def _pedals() -> cq.Workplane:
    r = FITTED_PEDAL_OD / 2
    sol = []
    for s in SIDES:
        path = _pedal_path(s)
        for a, b in pairwise(path):
            sol.append(_cyl(a, b, r))
        for p in path[1:-1]:
            sol.append(
                cq.Workplane(
                    obj=cq.Solid.makeSphere(
                        r, cq.Vector(*p), angleDegrees1=-90, angleDegrees2=90
                    )
                )
            )
    return _compound(sol)


def _ng31_disc() -> cq.Workplane:
    hw, h = FITTED_NG31_DISC
    x0 = FITTED_FS_NG31
    prof = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .moveTo(-hw, NOSE_BOTTOM_Z)
        .lineTo(hw, NOSE_BOTTOM_Z)
        .lineTo(hw, NOSE_BOTTOM_Z + h - hw)
        .threePointArc((0, NOSE_BOTTOM_Z + h), (-hw, NOSE_BOTTOM_Z + h - hw))
        .close()
    )
    return prof.extrude(FITTED_NG31_T).intersect(_envelope())


def _f6_plate() -> cq.Workplane:
    x0 = FITTED_FS_NG31 + FITTED_F6_AFT_OF_NG31
    return _box(x0, x0 + FITTED_F6_T, -_Y_OUT, _Y_OUT, NOSE_BOTTOM_Z, _plate_top(x0))


def _pitot() -> cq.Workplane:
    r, fwd, aft, wl = FITTED_PITOT
    z = z_of_wl(wl)
    return _cyl((FITTED_FS_NG31 - fwd, 0.0, z), (_FS_AFT + aft, 0.0, z), r)


def _static_port() -> cq.Workplane:
    r, t = FITTED_STATIC_PORT
    fs = G.fs_static_port
    y_skin = -(
        half_width(fs) + G.side_panel_thickness
    )  # left side, the outer face of the side
    return cq.Workplane(
        obj=cq.Solid.makeCylinder(
            r,
            t,
            cq.Vector(fs, y_skin - t, z_of_wl(G.wl_static_port)),
            cq.Vector(0, 1, 0),
        )
    )


def strut_cover_fs_range() -> tuple[float, float]:
    """From the plans-candidate NG6 pivot (the forward one) aft to F22."""
    pivot_fs, _ = ng6_pivot_for_axle(
        G.fs_nose_wheel,
        G.wl_nose_wheel,
        default_pivot_wl(),
        G.nose_strut_pivot_to_pivot_in,
    )
    return pivot_fs, _FS_AFT


def _strut_cover() -> cq.Workplane:
    x0, x1 = strut_cover_fs_range()
    hw, t = FITTED_COVER
    return _box(x0, x1, -hw, hw, NOSE_BOTTOM_Z - t, NOSE_BOTTOM_Z)


def _nb_box() -> cq.Workplane:
    x0, hw, h, wall = FITTED_NB_BOX
    x1 = G.fs_panel
    outer = _box(x0, x1, -hw, hw, NOSE_BOTTOM_Z, NOSE_BOTTOM_Z + h)
    inner = _box(
        x0 + wall,
        x1 - wall,
        -hw + wall,
        hw - wall,
        NOSE_BOTTOM_Z - 1.0,
        NOSE_BOTTOM_Z + h - wall,
    )
    return outer.cut(inner)


def _door() -> cq.Workplane:
    x0, x1, hw, fl, t = FITTED_DOOR
    plan = [(x0, -hw - fl), (x1, -hw - fl), (x1, hw + fl), (x0, hw + fl)]
    side = [
        (x0, nose_top_z(x0)),
        (x1, nose_top_z(x1)),
        (x1, nose_top_z(x1) + t),
        (x0, nose_top_z(x0) + t),
    ]
    return _slab(plan, side)


@lru_cache(maxsize=1)
def build_nose() -> dict[str, FusePart]:
    rep = "representational"
    parts: dict[str, FusePart] = {}
    parts["skin"] = FusePart(
        "skin",
        _skin(),
        rep,
        (_P171,),
        note=(
            f"two-ply BID shell drawn {FITTED_SKIN_T:g} in thick (visual, not to scale) over a lofted fitted envelope "
            f"from the tip (F.S. {G.fs_nose:g}, p171, the one printed number) to F22: flat bottom on the W.L. "
            f"{G.wl_fuselage_bottom_3view:g} skin line, flat top and sides, plan half width {_dims(_FS_AFT)[0]:g} at F22 "
            f"narrowing to {_dims(FITTED_FS_NG31)[0]:.2f} at NG31 then rounding to the tip. The section shape is not "
            "printed (A6/A7 not held). Open at the aft end."
        ),
    )
    parts["ng30_plates"] = FusePart(
        "ng30_plates",
        _ng30_plates(),
        rep,
        (_P77,),
        note=(
            f"two plates, {_T30:g} thick, inner faces {_Y_IN:g} either side of the centre line (3.0 between, p77). "
            f"Printed: thickness and gap. Fitted: the outline (template-only, A6/A7 not held): aft edge on F22, forward "
            f"edge on NG31 at F.S. {FITTED_FS_NG31:g}, bottom on the skin line, top {FITTED_TOP_BLOCK_T + FITTED_PLATE_CLEAR:g} in under the nose top."
        ),
    )
    parts["ng31_disc"] = FusePart(
        "ng31_disc",
        _ng31_disc(),
        rep,
        (),
        note=(
            f"half width {FITTED_NG31_DISC[0]:g} and height {FITTED_NG31_DISC[1]:g} are cobelu figures, NOT on the owner's scan: "
            f"a fitted D shape trimmed to the fitted nose envelope, {FITTED_NG31_T:g} thick, at F.S. {FITTED_FS_NG31:g}. "
            f"NG31 sits at ONE fitted station, the midpoint of the range [{G.fs_ng31_min:g}, {G.fs_ng31_max:g}] the "
            "side and floor block lengths give (p79); the range is the evidence, the point is a stand-in."
        ),
    )
    parts["f6_plate"] = FusePart(
        "f6_plate",
        _f6_plate(),
        rep,
        (),
        note=f"F6 plate across the NG30 plates just aft of NG31, {FITTED_F6_T:g} thick, fitted; no dimension printed.",
    )
    parts["floor_blocks"] = FusePart(
        "floor_blocks",
        _floor_blocks(),
        rep,
        (_P79,),
        note=(
            f"one per side outboard of each NG30 plate: wedge in plan, {G.floor_block_width_in:g} wide at the F22 end and "
            f"{G.floor_block_thickness_in:g} at the NG31 end, {G.floor_block_length_in:g} long, {G.floor_block_thickness_in:g} thick "
            f"(p79, medium; which end is 8.2 is a reading). Inboard edge dished {FITTED_FLOOR_DISH:g} (fitted). Printed numbers "
            "are used but the shape is a stand-in."
        ),
    )
    parts["side_blocks"] = FusePart(
        "side_blocks",
        _side_blocks(),
        rep,
        (_P79,),
        note=(
            f"{G.side_block_length_in:g} long, {_H_AFT:g} high at F22 and {_H_FWD:g} (5.5 + 2.8) at the NG31 end (p79, medium), "
            f"outboard of the floor blocks; thickness {FITTED_SIDE_BLOCK_T:g} fitted; forward end bevelled 17 deg in plan "
            "(fitted reading). Height is measured from the skin line; the 5.5/2.8 split about a reference line is not modelled."
        ),
    )
    parts["top_block"] = FusePart(
        "top_block",
        _top_block(),
        rep,
        (_P82,),
        note=(
            f"{G.top_block_length_in:g} long, {G.top_block_width_aft_in:g} wide aft at F22 and {G.top_block_width_fwd_in:g} "
            f"forward (p82, medium; orientation is a reading), {FITTED_TOP_BLOCK_T:g} thick (fitted), following the nose top."
        ),
    )
    parts["pivot_blocks"] = FusePart(
        "pivot_blocks",
        _pivot_blocks(),
        rep,
        (_P79,),
        note=(
            f"rudder pedal pivot blocks {G.pedal_block_from_ng30_in:g} from NG30 (p79) on the floor blocks, {G.floor_block_thickness_in:g} "
            f"thick plate; plan size {FITTED_PIVOT_BLOCK[0]:g} x {FITTED_PIVOT_BLOCK[1]:g}, position along F.S. ({FITTED_PIVOT_BLOCK_X_FROM_F22:g} "
            f"forward of F22) and the {FITTED_NUTPLATE[0]:g} x {FITTED_NUTPLATE[1]:g} aluminium nutplate shape are fitted."
        ),
    )
    parts["pedals"] = FusePart(
        "pedals",
        _pedals(),
        rep,
        (),
        note=(
            f"1/2 OD tube, legs {FITTED_PEDAL_LEGS[0]:g} inboard, {FITTED_PEDAL_LEGS[1]:g} up, {FITTED_PEDAL_LEGS[2]:g} forward: the "
            "three lengths are read from the sketch (7.0 / 6.2 / 5.75), the routing is fitted; one per side from its pivot block."
        ),
    )
    parts["pitot"] = FusePart(
        "pitot",
        _pitot(),
        rep,
        (),
        note=(
            f"1/4 OD straight rod on the centre line at W.L. {FITTED_PITOT[3]:g}, from {FITTED_PITOT[1]:g} in forward of NG31 to "
            f"{FITTED_PITOT[2]:g} in aft of F22. The plans put the long run about 3 in under the canard; that height is not modelled "
            "(the rod is kept level so it stays inside the nose). Fitted."
        ),
    )
    parts["static_port"] = FusePart(
        "static_port",
        _static_port(),
        rep,
        (_P82,),
        note=(
            f"marker disc on the LEFT side's outer face at F.S. {G.fs_static_port:g} (8 forward of the panel, p82) and W.L. "
            f"{G.wl_static_port:g} (p82); disc size fitted. Note this station is aft of F22, on the fuselage side, not the nose."
        ),
    )
    parts["strut_cover"] = FusePart(
        "strut_cover",
        _strut_cover(),
        rep,
        (),
        note="thin cover on the bottom from the plans-candidate NG6 pivot aft to F22, over the retracted strut; fitted, no dimension printed. "
        "The pivot is a derived-from-assumption position (see the nose gear), not a measurement.",
    )
    parts["nb_box"] = FusePart(
        "nb_box",
        _nb_box(),
        rep,
        (),
        note=f"nose-gear box: an open-bottom shell from F.S. {FITTED_NB_BOX[0]:g} to the panel, fitted; not a clearance claim for the retracted wheel.",
    )
    parts["door"] = FusePart(
        "door",
        _door(),
        rep,
        (_P83,),
        note=(
            "nose door panel on the top block with a 0.7 flange; the p83 dimensions are loose so the size is fitted. "
            "The ten screws are not modelled."
        ),
    )
    return parts


# Graph component id -> part names (nose.worm_drive has no geometry and is absent).
COMPONENT_PARTS = {
    "nose.ng30_plates": ("ng30_plates",),
    "nose.ng31": ("ng31_disc", "f6_plate"),
    "nose.floor_blocks": ("floor_blocks",),
    "nose.pivot_blocks": ("pivot_blocks",),
    "nose.side_blocks": ("side_blocks",),
    "nose.pedals": ("pedals",),
    "nose.pitot": ("pitot",),
    "nose.static_port": ("static_port",),
    "nose.top_block": ("top_block",),
    "nose.strut_cover": ("strut_cover",),
    "nose.nb_box": ("nb_box",),
    "nose.skin": ("skin",),
    "nose.door": ("door",),
}
