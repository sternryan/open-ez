"""Covers and consoles (plans chapter 24, pdf pages p159 to p161): lower aft cover, left consoles LC1 to LC6, thigh support, fuel-valve cover, canard cover, gap seal.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive; every console here is on the LEFT, y < 0), z = ``z_of_wl``.

Printed (config ``cov_book_*``, ``GEOMETRY_PROVENANCE``): LC1's stations FS 52 to FS 60 (p159, typed), the part sizes (p159 to p161), the gap seal sizes. NOT printed:
where LC2 to LC6, the thigh support, the canard cover and the seal sit, and every outline between the dimensioned corners (the thigh-rib curve is on A8,
the console locations are on sheets the owner does not hold). So only LC1 is ``book`` (its stations); every other solid is ``representational``, a fitted shape.
The cushions, headrests and suitcases of chapter 26 are in ``core.upholstery_book``. The finish of chapter 25 is NOT a solid: it is a per-part tag in the layup
(``finish_tags``), applied by the lab.

Positions that the book does not give are read from the model (the fuselage side, the front seat bulkhead, the canard install) and never typed here.
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq

from .fuselage_book import (
    FusePart,
    G,
    front_bulkhead_line_fs,
    half_width,
    z_of_wl,
)

_P159, _P160, _P161, _P162, _P171 = (
    f"plans-1980:p{n}" for n in (159, 160, 161, 162, 171)
)
_CP26, _CP27, _CP28 = "cp-text:p26", "cp-text:p27", "cp-text:p28"

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_FLOOR_Z = -14.75  # fitted, not book: pieces stand on the cockpit floor (the bottom's top face is -14.9 to -14.8; the book's floor line is WL 2.5)
FITTED_WALL_CLEAR = 0.05  # fitted, not book: pieces stand this far inside the fuselage side's inner face
FITTED_BULKHEAD_CLEAR = 0.6  # fitted, not book: the front console top stops this far short of the front seat bulkhead
FITTED_PANEL_CLEAR = 0.1  # fitted, not book: the thigh support starts this far aft of the instrument panel
FITTED_AFT_COVER_TOP_Z = -14.5  # fitted, not book: the aft cover's top face, just below the gear extrusions and tubes (z -14.4) so it clears them
FITTED_AFT_COVER_FWD = 107.4  # fitted, not book: the cover butts the fuselage bottom block (it ends at FS 107.3)
FITTED_AFT_COVER_HALF_W = (
    10.0  # book: p159 chunk 20 in across (half of it each side of the centre line)
)
FITTED_STRUT_CLEAR = (
    G.cov_book_aft_cover_strut_gap_in
)  # book: p159 about 1/8 in clear round the strut
FITTED_DISH_DEPTH = (
    1.0  # fitted, not book: the dish is hollowed this deep into the 2 in block
)
FITTED_LC4_HOLE_DIA = 1.0  # derived: cp-text CP24 p8 pitch-trim lever hole, 1 in kept; the plans print no size
FITTED_LC4_HOLE_FS_FROM_FRONT = (
    6.0  # fitted, not book: hole centre this far aft of LC4's front edge
)
FITTED_LC2_THROTTLE_CUT = (
    1.0,
    1.0,
)  # fitted, not book: the rear cutout for the throttle (aft end, inboard corner), no size printed
FITTED_LC5_FROM_BULKHEAD = 1.4  # fitted, not book: LC5 starts this far aft of the front bulkhead's front face at the top (the plate is 0.8 thick and leans)
FITTED_RIB_ARCH_R = 1.0  # fitted, not book: radius of the fuel-line notch in one rib (the dashed arch on p160)
FITTED_FLOOR_HALF_W = (
    G.cov_book_thigh_floor_in[0] / 2
)  # book: p160 the floor is 17 in wide
FITTED_RIB_CLEAR = (
    0.02  # fitted, not book: ribs stand this far below the floor's underside
)
FITTED_CANARD_BLOCK_X = (
    22.3,
    27.5,
)  # fitted, not book: the canard cover's F.S. extent: from just aft of F22 to just short of F28 (which stays)
FITTED_CANARD_BLOCK_HALF_W = 10.0  # fitted, not book: the canard cover block's half width (the nose top block is 9.8)
FITTED_CANARD_TOP_Z = 2.4  # fitted, not book: the canard core's top at the root (z_le 1.5 + about 0.85); the block stands on it
FITTED_SEAL_X = (
    113.5,
    118.4,
)  # fitted, not book: the seal's F.S. extent at the wing root, from the wing LE to the centre-section spar's forward face
FITTED_SEAL_Y_OFF = 0.22  # fitted, not book: the seal stands this far outboard of the wing root plane, clear of the strake baffle B23 (BL 22.8 to 23.2) and of the wing skins (from BL 23.7)
FITTED_SEAL_Z = (
    -1.5,
    4.0,
)  # fitted, not book: the seal's height range at the root (the wing root section is about 6 in deep)

LC1_TOP_Z = z_of_wl(G.cov_book_lc1_top_wl)
T_CORE = G.cov_book_console_core_in  # book: p159 0.35 in R45 PV, every console piece

WORKSHOP_PARTS: frozenset = frozenset()
FIDELITIES_USED = frozenset({"book", "representational"})

COMPONENT_PARTS = {
    "cover.aft": ("aft_cover",),
    "cover.console_lc1": ("lc1",),
    "cover.consoles": ("lc2", "lc3", "lc4", "lc5", "lc6"),
    "cover.thigh": ("thigh_floor", "thigh_rib_a", "thigh_rib_b"),
    "cover.valve": ("valve_cover",),
    "cover.canard": ("canard_cover",),
    "cover.seal": ("seal_right", "seal_left"),
}


# ---- helpers --------------------------------------------------------------------------------------------------------------------------
def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def prism_xz(pts, y0: float, y1: float) -> cq.Workplane:
    """The polygon ``pts`` (x, z) extruded across y from ``y0`` to ``y1``."""
    wp = cq.Workplane("XZ").polyline(pts).close().extrude(-(y1 - y0))
    bb = wp.val().BoundingBox()
    return wp.translate((0.0, y0 - bb.ymin, 0.0))


def wall_y(x0: float | None = None, x1: float | None = None) -> float:
    """The fuselage side's inner face on the left (y < 0), the narrowest over ``x0`` to ``x1`` (the cockpit narrows aft of FS 80)."""
    a = G.cov_book_lc1_fs[0] if x0 is None else x0
    b = a if x1 is None else x1
    n = 12
    hw = min(half_width(a + (b - a) * i / n) for i in range(n + 1))
    return -hw + FITTED_WALL_CLEAR


def floor_top_z(x: float) -> float:
    return FITTED_FLOOR_Z


def lc2_span() -> tuple[float, float]:
    """(x0, x1) of the console top LC2: the printed 30.6 in, ending at the front seat bulkhead's face where LC2's underside meets it."""
    x1 = front_bulkhead_line_fs(LC1_TOP_Z) - FITTED_BULKHEAD_CLEAR
    return x1 - G.cov_book_lc2_len_in, x1


# ---- chapter 24, step 1: lower aft cover ---------------------------------------------------------------------------------------------
def _strut_box() -> tuple[float, float, float, float]:
    from . import landing_gear_book as lg

    b = cq.Compound.makeCompound(lg.build_gear()["strut"].solid.vals()).BoundingBox()
    return b.xmin, b.xmax, b.zmin, b.zmax


@lru_cache(maxsize=1)
def aft_cover() -> cq.Workplane:
    """The 18 by 20 by 2 in block under the aft fuselage: dished 1/2 in inside the outline, slotted 1/8 in clear round the main gear strut."""
    ln, wd, th = G.cov_book_aft_cover_block_in
    x0 = FITTED_AFT_COVER_FWD
    x1 = (
        x0 + ln - 0.4
    )  # the book's 18 less the bottom block overlap: it ends at the firewall's front face (FS 125.0)
    z1 = FITTED_AFT_COVER_TOP_Z
    z0 = z1 - th
    hw = wd / 2
    block = _box(x0, x1, -hw, hw, z0, z1)
    d = G.cov_book_aft_cover_dish_in
    dish = _box(x0 + d, x1 - d, -hw + d, hw - d, z1 - FITTED_DISH_DEPTH, z1 + 0.01)
    sx0, sx1, _sz0, _sz1 = _strut_box()
    slot = _box(
        sx0 - FITTED_STRUT_CLEAR,
        sx1 + FITTED_STRUT_CLEAR,
        -hw - 1,
        hw + 1,
        z0 - 1,
        z1 + 1,
    )
    return _solid(block.cut(dish).cut(slot))


# ---- chapter 24, step 2: left consoles -----------------------------------------------------------------------------------------------
def lc1() -> cq.Workplane:
    """9.1 by 8 in, FS 52 to FS 60, 2.0 in off the fuselage side, top at WL 11.6 (printed); the foot is trimmed to the floor."""
    x0, x1 = G.cov_book_lc1_fs
    y_out = -half_width(x0) + G.cov_book_lc1_offset_in
    return _solid(
        prism_xz(
            [
                (x0, FITTED_FLOOR_Z),
                (x1, FITTED_FLOOR_Z),
                (x1, LC1_TOP_Z),
                (x0, LC1_TOP_Z),
            ],
            y_out,
            y_out + T_CORE,
        ).val()
    )


def lc2() -> cq.Workplane:
    """Front console top: 30.6 by 2.35 by 0.35, on LC1, LC3 and LC4, throttle cutout at the aft inboard corner."""
    x0, x1 = lc2_span()
    y0 = wall_y()
    y1 = y0 + G.cov_book_lc2_width_in
    plate = _box(x0, x1, y0, y1, LC1_TOP_Z, LC1_TOP_Z + T_CORE)
    cx, cy = FITTED_LC2_THROTTLE_CUT
    cut = _box(
        x1 - cx,
        x1 + 0.01,
        y1 - cy,
        y1 + 0.01,
        LC1_TOP_Z - 0.01,
        LC1_TOP_Z + T_CORE + 0.01,
    )
    return _solid(plate.cut(cut))


def lc3() -> cq.Workplane:
    """Sloped side: 10.6 along the top, 9.1 tall, 3 in step at the bottom, at the outboard edge of LC2 (foot trimmed to the floor)."""
    x0 = lc2_span()[0]
    along, _tall = G.cov_book_lc3_in
    step = (
        G.cov_book_lc3_step_in
    )  # book: p160 the 3 in step at the bottom; the slope between the corners is fitted
    y0 = wall_y()
    return _solid(
        prism_xz(
            [
                (x0, FITTED_FLOOR_Z),
                (x0 + along - step, FITTED_FLOOR_Z),
                (x0 + along, LC1_TOP_Z),
                (x0, LC1_TOP_Z),
            ],
            y0,
            y0 + T_CORE,
        ).val()
    )


def lc4() -> cq.Workplane:
    """Side rectangle 11.7 by 9.1 at the inboard edge of LC2, with the pitch-trim lever hole (1 in, from cp-text CP24 p8; the plans print no size)."""
    x0 = lc2_span()[0]
    along, _tall = G.cov_book_lc4_in
    y1 = wall_y() + G.cov_book_lc2_width_in
    plate = prism_xz(
        [
            (x0, FITTED_FLOOR_Z),
            (x0 + along, FITTED_FLOOR_Z),
            (x0 + along, LC1_TOP_Z),
            (x0, LC1_TOP_Z),
        ],
        y1,
        y1 + T_CORE,
    )
    hole = (
        cq.Workplane("XZ")
        .center(x0 + FITTED_LC4_HOLE_FS_FROM_FRONT, (FITTED_FLOOR_Z + LC1_TOP_Z) / 2)
        .circle(FITTED_LC4_HOLE_DIA / 2)
        .extrude(-(T_CORE + 2.0))
        .translate((0, y1 - 1.0, 0))
    )
    return _solid(plate.cut(hole).val())


def lc5_x0() -> float:
    return front_bulkhead_line_fs(LC1_TOP_Z) + FITTED_LC5_FROM_BULKHEAD


def lc5() -> cq.Workplane:
    """Rear console top: 18.2 by 1.9 by 0.35 behind the front seat bulkhead, level with LC2 (fitted)."""
    length, width = G.cov_book_lc5_in
    x0 = lc5_x0()
    y0 = wall_y(x0, x0 + length)
    return _solid(_box(x0, x0 + length, y0, y0 + width, LC1_TOP_Z, LC1_TOP_Z + T_CORE))


def lc6() -> cq.Workplane:
    """Triangular side under LC5, 8.0 deep, base angles 50 and 45 deg (the base is 8/tan50 + 8/tan45 = 14.7 in, inside LC5's 18.2)."""
    depth = G.cov_book_lc6_depth_in
    a_fwd, a_aft = (
        math.radians(50.0),
        math.radians(45.0),
    )  # base angles as printed; which end is which is not read
    x0 = lc5_x0()
    left = depth / math.tan(
        a_fwd
    )  # horizontal run from the forward base corner to the apex
    base = left + depth / math.tan(a_aft)
    y0 = wall_y(x0, x0 + base)
    return _solid(
        prism_xz(
            [(x0, LC1_TOP_Z), (x0 + base, LC1_TOP_Z), (x0 + left, LC1_TOP_Z - depth)],
            y0,
            y0 + T_CORE,
        ).val()
    )


# ---- chapter 24, step 3: thigh support ------------------------------------------------------------------------------------------------
def thigh_x() -> tuple[float, float]:
    """(front, aft) F.S. of the thigh floor: from the instrument panel's aft face, 12.3 in long (the printed 17 by 12.3, 17 across)."""
    x0 = G.fs_panel + 0.2 + FITTED_PANEL_CLEAR  # the panel plate is 0.2 thick
    return x0, x0 + G.cov_book_thigh_floor_in[1]


def _floor_z_under(x: float) -> float:
    """Underside of the thigh floor at F.S. ``x``: 3.65 in above the cockpit floor at the front (the rib height), down to the floor at the aft edge."""
    x0, x1 = thigh_x()
    rib_h = G.cov_book_thigh_rib_in[1]
    return FITTED_FLOOR_Z + rib_h * (x1 - x) / (x1 - x0) + FITTED_RIB_CLEAR


def thigh_floor() -> cq.Workplane:
    """Floor, 17 by 12.3 with a 5.6 by 4.5 notch at the aft edge, sloping from the rib height down to the floor (the book bends it; the curve is fitted), 0.35 thick."""
    x0, x1 = thigh_x()
    hw = FITTED_FLOOR_HALF_W
    pts = [
        (x0, _floor_z_under(x0)),
        (x1, _floor_z_under(x1)),
        (x1, _floor_z_under(x1) + T_CORE),
        (x0, _floor_z_under(x0) + T_CORE),
    ]
    slab = prism_xz(pts, -hw, hw).val()
    nw, nd = G.cov_book_thigh_notch_in
    notch = _box(
        x1 - nd, x1 + 0.01, -nw / 2, nw / 2, FITTED_FLOOR_Z - 1, FITTED_FLOOR_Z + 20
    )
    return _solid(slab.cut(notch))


def _rib(y_centre: float, arch: bool) -> cq.Workplane:
    x0, _x1 = thigh_x()
    ln, _h = G.cov_book_thigh_rib_in
    x1 = x0 + ln
    pts = [
        (x0, FITTED_FLOOR_Z),
        (x1, FITTED_FLOOR_Z),
        (x1, _floor_z_under(x1)),
        (x0, _floor_z_under(x0)),
    ]
    rib = prism_xz(pts, y_centre - T_CORE / 2, y_centre + T_CORE / 2).val()
    if arch:
        c = (
            cq.Workplane("XZ")
            .center(x0 + ln / 2, FITTED_FLOOR_Z)
            .circle(FITTED_RIB_ARCH_R)
            .extrude(-(T_CORE + 2.0))
            .translate((0, y_centre - T_CORE / 2 - 1.0, 0))
        )
        rib = rib.cut(c.val())
    return _solid(rib)


def thigh_rib_a() -> cq.Workplane:
    return _rib(
        -G.cov_book_thigh_rib_spacing_in / 2, True
    )  # the notched rib (fuel lines)


def thigh_rib_b() -> cq.Workplane:
    return _rib(G.cov_book_thigh_rib_spacing_in / 2, False)


def valve_cover() -> cq.Workplane:
    """Fuel-valve cover: 6.6 across by 5.0 fore-aft by 0.025 aluminium, lying on the floor over the notch (the notch is 5.6 by 4.5, so it laps 0.5 each way)."""
    cw, cl, ct = G.cov_book_valve_cover_in
    _x0, x1 = thigh_x()
    nd = G.cov_book_thigh_notch_in[1]
    xa = x1 - nd - (cl - nd) / 2
    pts = [
        (xa, _floor_z_under(xa) + T_CORE),
        (xa + cl, _floor_z_under(xa + cl) + T_CORE),
        (xa + cl, _floor_z_under(xa + cl) + T_CORE + ct),
        (xa, _floor_z_under(xa) + T_CORE + ct),
    ]
    return _solid(prism_xz(pts, -cw / 2, cw / 2).val())


# ---- chapter 24, step 4: canard cover ------------------------------------------------------------------------------------------------
def canard_cover() -> cq.Workplane:
    """2 in block of urethane on the canard's top at the fuselage, forward of F28 (which stays); the plans print no other size (fitted)."""
    x0, x1 = FITTED_CANARD_BLOCK_X
    z0 = FITTED_CANARD_TOP_Z + 0.05
    return _solid(
        _box(
            x0,
            x1,
            -FITTED_CANARD_BLOCK_HALF_W,
            FITTED_CANARD_BLOCK_HALF_W,
            z0,
            z0 + G.cov_book_canard_cover_foam_in,
        )
    )


# ---- chapter 24, step 5: wing and centre-section gap seal -----------------------------------------------------------------------------
def _seal(sign: int) -> cq.Workplane:
    """The wedge in the 1/2 in gap at the wing root: 1/2 in wide, ending at 1/16 in at the front (a wedge in plan), on the inboard face of the root (fitted)."""
    gap, front = G.cov_book_seal_gap_in, G.cov_book_seal_front_gap_in
    xa, xb = FITTED_SEAL_X
    z0, z1 = FITTED_SEAL_Z
    root = (
        G.wing_root_bl + FITTED_SEAL_Y_OFF
    )  # just outboard of the wing root plane (the wing skins start at BL 23.7)
    pts = [
        (xa, root),
        (xb, root),
        (xb, root + gap),
        (xa, root + front),
    ]  # (x, y) in plan: 1/2 wide at the back, 1/16 at the front  # (x, y) in plan
    wp = cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))
    if sign < 0:
        wp = wp.mirror("XZ")
    return _solid(wp.val())


def seal_right() -> cq.Workplane:
    return _seal(1)


def seal_left() -> cq.Workplane:
    return _seal(-1)


# ---- chapter 25: the finish layer (tags, not solids) ------------------------------------------------------------------------------------
PRIMER_GREY = "primer-grey"  # representational: the book prints no airplane colour
WHITE = "white"  # book: p162 white only on the upper wing and canard

# (graph component id, node substring or None for the whole component, finish surface). The lab tags the matching glb nodes.
FINISH_SURFACES = (
    ("wing.skins", "skin_top", "wing_upper"),
    ("wing.skins", "skin_bottom", "wing_lower"),
    ("canard.skin_top", None, "canard_upper"),
    ("canard.skin_bottom", None, "canard_lower"),
    ("cover.canard", None, "canard_upper"),  # the canard cover lies on the canard's top
    ("fuselage.skin_right", None, "fuselage"),
    ("fuselage.skin_left", None, "fuselage"),
    ("fuselage.bottom", None, "fuselage"),
    ("nose.skin", None, "fuselage"),
    ("strake.skins", None, "fuselage"),
    ("winglet.skins", None, "winglet"),
    ("engine.cowl", None, "cowl"),
    ("cover.aft", None, "fuselage"),
)


def finish_rows() -> list[dict]:
    """The finish layer as data for the lab: one row per surface-bearing component, with the three coats (fill, primer, paint), their thicknesses in inches
    (book, p167 and p168; the paint has none printed) and the colour of the last coat: white on the upper wing and canard only (book, p162), primer grey elsewhere
    (representational). A layer drawn on the part, never a solid, and it carries no weight (none is printed)."""
    rows = []
    for cid, match, surface in FINISH_SURFACES:
        colour = WHITE if surface in G.fin_book_white_surfaces else PRIMER_GREY
        rows.append(
            {
                "component": cid,
                "match": match,
                "surface": surface,
                "stages": [
                    {
                        "stage": "fill",
                        "from": "f25.feather-fill",
                        "thickness_in": list(G.fin_book_fill_in),
                        "colour": PRIMER_GREY,
                    },
                    {
                        "stage": "primer",
                        "from": "f25.primer",
                        "thickness_in": list(G.fin_book_primer_in),
                        "colour": PRIMER_GREY,
                    },
                    {
                        "stage": "paint",
                        "from": "f25.paint-seals",
                        "thickness_in": None,
                        "colour": colour,
                    },
                ],
                "final_colour": colour,
            }
        )
    return rows


# ---- the parts ------------------------------------------------------------------------------------------------------------------------
def build_covers() -> dict[str, FusePart]:
    rep = "representational"
    return {
        "aft_cover": FusePart(
            "aft_cover",
            aft_cover(),
            rep,
            (_P159, _CP28),
            "lower aft cover: the printed 18 by 20 by 2 in block (a flat slab under the aft fuselage; the outline follows the strut and firewall and is not drawn), dished 1/2 in inside the outline, slotted 1/8 in clear round the main gear strut; the ply count is a conflict (scan, LPC 54 and the transcription disagree)",
        ),
        "lc1": FusePart(
            "lc1",
            lc1(),
            "book",
            (_P159,),
            "LC1, the landing-brake console piece: 9.1 by 8 in from 0.35 in R45, FS 52 to FS 60 (printed), 2.0 in off the fuselage side, top at WL 11.6; its foot is trimmed to the floor",
        ),
        "lc2": FusePart(
            "lc2",
            lc2(),
            rep,
            (_P160,),
            "LC2, the front console top, 30.6 in long (the transcription reads 30.8, unresolved), 2.35 wide, 0.35 R45; where it sits is fitted (it ends at the front seat bulkhead); the throttle cutout size is not printed; the 0.3 in bevel is not drawn",
        ),
        "lc3": FusePart(
            "lc3",
            lc3(),
            rep,
            (_P160,),
            "LC3, the sloped front console side: 10.6 in along the top, 9.1 tall, 3 in step at the bottom (printed); the slope between the corners and the foot trimmed to the floor are fitted",
        ),
        "lc4": FusePart(
            "lc4",
            lc4(),
            rep,
            (_P160, "cp-text:p24"),
            "LC4, the front console side: 11.7 by 9.1 in with one hole for the pitch-trim adjust; the hole size (1 in) is from CP24, not the plans, and its place is fitted",
        ),
        "lc5": FusePart(
            "lc5",
            lc5(),
            rep,
            (_P160, _P159),
            "LC5, the rear console top, 18.2 by 1.9 in (printed); left short of the right one to leave room for the left suitcase; where it sits is fitted; the 0.35 bevel is not drawn",
        ),
        "lc6": FusePart(
            "lc6",
            lc6(),
            rep,
            (_P160,),
            "LC6, the triangular rear console side, 8.0 deep, base angles 50 and 45 deg (hand digits, medium); the bottom is trimmed to the floor in the book and drawn as a point here",
        ),
        "thigh_floor": FusePart(
            "thigh_floor",
            thigh_floor(),
            rep,
            (_P160,),
            "thigh-support floor, 17 by 12.3 in with the 5.6 by 4.5 in notch (printed), 0.35 R45, 1 ply BID inside and 2 outside; the rib curve (A8) is not held, so the heat-formed bend is a straight slope from the rib height to the floor",
        ),
        "thigh_rib_a": FusePart(
            "thigh_rib_a",
            thigh_rib_a(),
            rep,
            (_P160,),
            "thigh-support rib, 10.8 in long and 3.65 in tall at the front (printed), notched for the fuel lines (fitted arch); the curved top is on A8, not held",
        ),
        "thigh_rib_b": FusePart(
            "thigh_rib_b",
            thigh_rib_b(),
            rep,
            (_P160,),
            "the second thigh-support rib, 5.6 in from the first with the fuel valve between (printed)",
        ),
        "valve_cover": FusePart(
            "valve_cover",
            valve_cover(),
            rep,
            (_P160,),
            "fuel-valve cover, 0.025 in 2024-T3, 6.6 by 5.0 in (printed), silicone-bonded; drawn lapping the floor notch, which is where the book's valve sits only by inference",
        ),
        "canard_cover": FusePart(
            "canard_cover",
            canard_cover(),
            rep,
            (_P161,),
            "canard cover: the 2 in urethane block is the only printed size; its plan, its place on the canard and its carving are fitted, and it stops short of F28",
        ),
        "seal_right": FusePart(
            "seal_right",
            seal_right(),
            rep,
            (_P161,),
            "right gap seal: a wedge about 1/2 in wide at the back, 1/16 in at the front (printed; the 1/2 reads as 3/4 on a poor scan); where it runs along the root is fitted (drawn at the wing root's forward edge, between baffle B23 and the wing skin)",
        ),
        "seal_left": FusePart(
            "seal_left",
            seal_left(),
            rep,
            (_P161,),
            "left gap seal, the mirror of the right",
        ),
    }
