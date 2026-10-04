"""Strakes, baggage areas and fuel tanks (plans chapter 21, pdf pages p141 to p148): ribs, baffles, leading-edge strips, skins, sump blister, tank volume.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``. ``build_strake("right")`` and ``build_strake("left")`` return
the two strakes; the left is the mirror (p147 draws the right strake and says the left is its mirror).

Printed (config ``stk_book_*`` and ``fuel_book_*``, ``GEOMETRY_PROVENANCE``): the plan stations on p147 (LE F.S. 50 at the fuselage side, 73.3 at BL 23,
99.5 at BL 45, the wing LE at BL 58; the spar forward face 118.5 at BL 23, the BAB meeting 103.5), the part sizes (p141), the skin edges and the
fuselage-side cutout table (p142), the jig rib heights (p143), the sump blister (p144). NOT printed: the R23 and R45 outlines (A14), the OD outline, the
skin curvature, the tank outline beyond the dimensioned corners, the fittings' positions. Every solid is therefore ``representational`` except the
plates whose length, height and station are printed (``derived``).

Surfaces: the two inside faces of the tank are the two jig-table planes (the strake bottom follows the spar bottom, rising about 2.1 deg outboard; the top
inside plane is the cutout top edge, WL 21.6), each pulled toward the other near the leading edge by the p142 cutout table (the strake is only 2.55 in thick
at its nose). Measured only at the fuselage side, so the same profile against the distance aft of the LE is used everywhere (fitted). With those planes the
baffle heights printed on p141 (7.3 at BL 23, 6.5 at BL 45, 7.75 at the fuselage) come out without being typed here, which is the check the tests make.
Skins and the tank are ruled lofts through sections of constant F.S.; the plates are lofts of two planar faces, so no boolean is needed.
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator

from .fuselage_book import FusePart, G, half_width, z_of_wl

_P141, _P142, _P143, _P144, _P145, _P146, _P147, _P171 = (
    f"plans-1980:p{n}" for n in (141, 142, 143, 144, 145, 146, 147, 171)
)
_OM_P4 = "om-1980:p4"

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_CLEAR = 0.1  # fitted, not book: plates stand this far inside the skins (the ruled skin faces differ from the exact surface by hundredths)
FITTED_BLE_TRIM = 1.0  # fitted, not book: the BLE strip stops this far short of the fuselage side (its inner face would cut the side panel)
FITTED_END_GAP = 0.03  # fitted, not book: a plate ends this far short of the spar face (the face is slanted, the plate end is square)
FITTED_NX_STEP = (
    0.5  # fitted, not book: spacing of the F.S. sections of every ruled loft
)
FITTED_CLUSTER = 0.4  # fitted, not book: share of an even spacing in the section points (the rest is clustered toward the LE)
FITTED_NB = 28  # fitted, not book: points across each loft section
FITTED_PLATE_N = 24  # fitted, not book: samples along each plate's top and bottom edge
FITTED_TIP_X = 0.4  # fitted, not book: the skin lofts begin and end this far inside their sharp corners (a section needs a width)
FITTED_TANK_INSET = 0.6  # fitted, not book: the tank volume stands this far inside the leading-edge strips and the outer rib
FITTED_BLISTER_ENDS = (
    3.0  # fitted, not book: the sump blister tapers over this length at each end
)
FITTED_BLISTER_END_SCALE = (
    0.25  # fitted, not book: the blister's end sections are this fraction of full size
)
FITTED_BLISTER_BIAS = (
    0.02  # fitted, not book: the blister top stands this far under the spar bottom
)
FITTED_DROOP_TAIL = 12.0  # fitted, not book: the nose profile dies away this far aft of the last cutout station
FITTED_FAIR_INSET = 0.2  # fitted, not book: the fairing block stands this far inside the skins and the diagonal
FITTED_CAP_DIA = 2.25  # book: p145 the fuel cap hole is bored with a 2 1/4 in hole saw
FITTED_CAP_RIM_H = 0.3  # book: p145 cap height 0.300
FITTED_CAP_POS = (
    110.0,
    34.0,
)  # fitted, not book: (F.S., B.L.) of the cap, in the aft half of the tank between B23 and R45; the page draws it, the scan has no dimensions
FITTED_DRAIN_POS = (
    75.0,
    22.5,
)  # derived, scaled off p147: (F.S., B.L.) of the water drain at the forward corner where TLE, BLE and R23 meet
FITTED_DRAIN_SIZE = 1.0  # book: p146 drain insert 1 by 1 in
FITTED_DRAIN_T = 0.125  # book: p146 drain insert 1/8 in thick
FITTED_VENT_DIA = 0.25  # book: p143 1/4 in aluminium vent line
FITTED_VENT_RISE = 0.5  # book: p143 the vent opens 1/2 in above the top
FITTED_VENT_POS = (
    106.0,
    0.6,
)  # fitted, not book: (F.S., offset from the fuselage side) of the vent stub on the top skin; no station printed
FITTED_SCREEN_DIA = 1.25  # book: p143 the screen domes a 1 1/4 in hole
FITTED_SCREEN_POS = (
    115.8,
    14.0,
)  # derived, scaled off p147: (F.S., B.L.) of the hole near the aft inboard corner, about plus or minus 1 in
FITTED_SCREEN_RISE = 0.35  # fitted, not book: height of the screen dome
FITTED_TUBE_DIA = 0.375  # book: p144 the outlet tube is 3/8 in
FITTED_TUBE_OUT = 0.4  # book: p144 the tube sticks out 0.4 in
FITTED_TUBE_FWD_OF_FIREWALL = (
    13.0  # book: p144 the outlet hole is about 13 in forward of the firewall
)
FITTED_TUBE_BELOW_TANK = 3.0  # book: p144 the hole is 3.0 below the tank bottom line
FITTED_TUBE_ENTRY = 0.01  # fitted, not book: the stub starts this far outside the fuselage side outer face
FITTED_CUTOUT_AFT_ROUND = 1.0  # fitted, not book: the tank cutout's round forward end is drawn as a chamfer this long
FITTED_CUT_PAD = 0.05  # fitted, not book: the cutout void is this much wider than the side panel each way

STRAKE_PARTS_VOID = frozenset({"cutout_baggage", "cutout_tank"})
WORKSHOP_PARTS: frozenset = frozenset()
FIDELITIES_USED = frozenset({"representational", "derived"})

T = G.stk_book_foam_thickness_in
TAN_SPAR = math.tan(math.radians(G.stk_book_spar_slope_deg))
SIDE_T = G.side_panel_thickness
LE_FS0 = G.stk_book_le_fs_fuselage
SPAR_FS23 = G.stk_book_spar_fwd_fs_bl_23
JUNCTION = G.stk_book_junction_fs
_LONG, _OFF = G.stk_book_skin_spar_edge_in
BL_END = 23.0 + math.sqrt(
    _LONG**2 - _OFF**2
)  # derived: the outboard skin's spar edge ends here (about 54.6)


# ---- the plan lines ------------------------------------------------------------------------------------------------------------------
def side_outer(fs: float) -> float:
    """B.L. of the outer face of the fuselage side at F.S. ``fs`` (the plan-bent side of the box model)."""
    return half_width(fs) + SIDE_T


def spar_fs(bl: float) -> float:
    """The spar forward face at B.L. ``bl``: 118.5 at BL 23 swept aft 8.57 deg (p147, p118)."""
    return SPAR_FS23 + (bl - 23.0) * TAN_SPAR


def bl_spar(fs: float) -> float:
    """B.L. at which the spar forward face stands at F.S. ``fs``."""
    return 23.0 + (fs - SPAR_FS23) / TAN_SPAR


@lru_cache(maxsize=1)
def _le_points() -> tuple[tuple[float, float], ...]:
    """The LE polyline (F.S., B.L.): the fuselage side, BL 23, BL 45, then the wing LE at BL 58 (CP25 LPC 7)."""
    return (
        (LE_FS0, side_outer(LE_FS0)),
        (G.stk_book_le_fs_bl_23, 23.0),
        (G.stk_book_le_fs_bl_45, 45.0),
        tuple(G.wing_le_anchor),
    )


def le_fs(bl: float) -> float:
    """LE F.S. at B.L. ``bl``, along the printed polyline."""
    p = _le_points()
    return float(np.interp(bl, [q[1] for q in p], [q[0] for q in p]))


def le_bl(fs: float) -> float:
    """LE B.L. at F.S. ``fs`` (the inverse of ``le_fs``)."""
    p = _le_points()
    return float(np.interp(fs, [q[0] for q in p], [q[1] for q in p]))


def _spar_at_side() -> float:
    fs = SPAR_FS23
    for _ in range(8):
        fs = spar_fs(side_outer(fs))
    return fs


SPAR_AT_SIDE = (
    _spar_at_side()
)  # derived: the spar forward face where it meets the fuselage side (about 116.7)
X_END = spar_fs(BL_END)  # derived: the aft corner of the outboard skin


def jig_h(bl: float) -> float:
    """Height of the WL 17.4 mark above the jig table at B.L. ``bl``: 3.45 at R23 and 2.65 at R45 (p143), straight between."""
    h45, h23 = G.stk_book_jig_rib_height_in
    return h23 + (23.0 - bl) * (h23 - h45) / 22.0


def bot_outer_wl(bl: float) -> float:
    """The bottom skin's outside plane, as a waterline: the jig table plane, flush with the spar bottom."""
    return G.wing_book_chord_line_wl - jig_h(bl)


TOP_IN_WL = (
    G.side_panel_top_wl - G.stk_book_cutout_aft_in[2]
)  # derived: the cutout top edge, 1.40 below WL 23 (21.6)


@lru_cache(maxsize=1)
def _nose_profile() -> tuple[PchipInterpolator, PchipInterpolator, float]:
    """(droop of the top surface, rise of the bottom surface, last u) against u, the distance aft of the LE, from the p142 cutout table at the fuselage side."""
    tab = G.stk_book_cutout_fwd_in
    ref_top, ref_bot = tab[-1][1], tab[-1][2]
    us = [SPAR_AT_SIDE - st - LE_FS0 for st, _t, _b in tab]
    droop = [t - ref_top for _s, t, _b in tab]
    rise = [ref_bot - b for _s, _t, b in tab]
    xs = [0.0] + us + [us[-1] + FITTED_DROOP_TAIL]
    return (
        PchipInterpolator(xs, [droop[0]] + droop + [0.0]),
        PchipInterpolator(xs, [rise[0]] + rise + [0.0]),
        xs[-1],
    )


def droop_top(u: float) -> float:
    f, _g, umax = _nose_profile()
    return float(f(min(max(u, 0.0), umax)))


def rise_bot(u: float) -> float:
    _f, g, umax = _nose_profile()
    return float(g(min(max(u, 0.0), umax)))


def top_inner_wl(fs: float, bl: float) -> float:
    return TOP_IN_WL - droop_top(fs - le_fs(bl))


def bot_inner_wl(fs: float, bl: float) -> float:
    return bot_outer_wl(bl) + T + rise_bot(fs - le_fs(bl))


def top_inner_z(fs: float, bl: float) -> float:
    return z_of_wl(top_inner_wl(fs, bl))


def bot_inner_z(fs: float, bl: float) -> float:
    return z_of_wl(bot_inner_wl(fs, bl))


def inner_height(fs: float, bl: float) -> float:
    """Distance between the two inside faces (the part heights p141 prints) at (F.S., B.L.)."""
    return top_inner_wl(fs, bl) - bot_inner_wl(fs, bl)


# ---- lofts ----------------------------------------------------------------------------------------------------------------------------
def _wire(pts) -> cq.Wire:
    v = [cq.Vector(*p) for p in pts]
    return cq.Wire.makePolygon(v + [v[0]])


def _loft(wires: list[cq.Wire]) -> cq.Solid:
    s = cq.Solid.makeLoft(wires, True)
    if s.Volume() < 0:
        s = cq.Solid(s.wrapped.Reversed())
    return s


def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _compound(solids) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound([s for s in solids]))


def _xs_breaks() -> list[float]:
    """F.S. values where a plan line kinks: the LE polyline, the side's bend points, the spar corner."""
    from .fuselage_book import plan_bend_points

    ks = [p[0] for p in _le_points()] + [x for x, _h in plan_bend_points()]
    ks += [JUNCTION, G.stk_book_bab_fuselage_fs, SPAR_AT_SIDE, X_END, le_fs(BL_END)]
    return ks


def _xloft(x0, x1, lo, hi, z_top, z_bot) -> cq.Solid:
    """Ruled loft through sections of constant F.S. from ``x0`` to ``x1``: at each, B.L. from ``lo(x)`` to ``hi(x)``, top ``z_top(x, bl)``, bottom ``z_bot(x, bl)``."""
    xs = set(np.arange(x0, x1, FITTED_NX_STEP).tolist()) | {x1}
    xs |= {k for k in _xs_breaks() if x0 < k < x1}
    wires = []
    for x in sorted(xs):
        a, b = lo(x), hi(x)
        if b - a < 1e-6:
            continue
        t = np.linspace(0.0, 1.0, FITTED_NB)
        bls = a + (b - a) * (
            FITTED_CLUSTER * t + (1 - FITTED_CLUSTER) * (1 - (1 - t) ** 2)
        )  # denser toward the LE (the outboard end), where the nose profile is steep
        top = [(x, float(y), z_top(x, float(y))) for y in bls]
        bot = [(x, float(y), z_bot(x, float(y))) for y in bls][::-1]
        wires.append(_wire(top + bot))
    return _loft(wires)


def _plate(p0, p1, t, offset=0.0, trim0=0.0, trim1=0.0) -> cq.Solid:
    """A vertical plate of thickness ``t`` along the plan line p0 to p1 (F.S., B.L.), centred ``offset`` to the left of the line, from the bottom inside face up to
    the top inside face (each pulled in by FITTED_CLEAR), ends shortened by ``trim0`` and ``trim1``."""
    (x0, y0), (x1, y1) = p0, p1
    ln = math.hypot(x1 - x0, y1 - y0)
    dx, dy = (x1 - x0) / ln, (y1 - y0) / ln
    nx, ny = -dy, dx
    ss = np.linspace(trim0, ln - trim1, FITTED_PLATE_N)

    def face(off):
        pts_top, pts_bot = [], []
        for s in ss:
            bx, by = x0 + dx * s, y0 + dy * s  # on the line, for the surface heights
            px, py = bx + nx * off, by + ny * off
            pts_top.append((px, py, top_inner_z(bx, by) - FITTED_CLEAR))
            pts_bot.append((px, py, bot_inner_z(bx, by) + FITTED_CLEAR))
        return pts_top + pts_bot[::-1]

    return _loft([_wire(face(offset + t / 2)), _wire(face(offset - t / 2))])


# ---- the solids (right strake) ------------------------------------------------------------------------------------------------------
def _skin_lo(x):
    return max(side_outer(x), bl_spar(x))


def _skin_hi(x):
    return min(le_bl(x), BL_END)


def skin_top() -> cq.Workplane:
    """Top skin, 0.35 thick, over the whole strake plan (inboard and outboard skins together): the inside face is the top inside surface."""
    return _solid(
        _xloft(
            LE_FS0 + FITTED_TIP_X,
            X_END - FITTED_TIP_X,
            _skin_lo,
            _skin_hi,
            lambda x, y: top_inner_z(x, y) + T,
            top_inner_z,
        )
    )


def skin_bottom() -> cq.Workplane:
    return _solid(
        _xloft(
            LE_FS0 + FITTED_TIP_X,
            X_END - FITTED_TIP_X,
            _skin_lo,
            _skin_hi,
            bot_inner_z,
            lambda x, y: bot_inner_z(x, y) - T,
        )
    )


def _end_at_spar(bl: float) -> float:
    return spar_fs(bl) - FITTED_END_GAP


def rib_r23() -> cq.Workplane:
    """R23: along BL 23 from the TLE and BLE kink to the B23 junction."""
    return _solid(_plate((G.stk_book_le_fs_bl_23, 23.0), (JUNCTION, 23.0), T))


def rib_r45() -> cq.Workplane:
    """R45: along BL 45 from the LE to the spar face."""
    return _solid(
        _plate((G.stk_book_le_fs_bl_45, 45.0), (_end_at_spar(45.0), 45.0), T, trim0=T)
    )


def b23() -> cq.Workplane:
    """B23: along BL 23 from the junction to the spar face, 21.3 long (printed)."""
    return _solid(_plate((JUNCTION, 23.0), (_end_at_spar(23.0), 23.0), T))


def db() -> cq.Workplane:
    """DB: the diagonal baffle from the junction to R45 (28.5 printed; the plan closes at 28.2)."""
    return _solid(
        _plate(
            (JUNCTION, 23.0),
            (G.stk_book_db_far_fs, 45.0),
            T,
        )
    )


def bab() -> cq.Workplane:
    """BAB: from the junction to the fuselage side at F.S. 103.5."""
    side = side_outer(G.stk_book_bab_fuselage_fs)
    return _solid(
        _plate((JUNCTION, 23.0), (G.stk_book_bab_fuselage_fs, side), T, trim1=T)
    )


def od() -> cq.Workplane:
    """OD: the outboard diagonal from the TLE and R45 corner to the spar face near BL 54.6 (the outline is fitted)."""
    return _solid(
        _plate((G.stk_book_le_fs_bl_45, 45.0), (X_END, BL_END), T, trim1=2 * T)
    )


def tle() -> cq.Workplane:
    """TLE: the LE strip from the BL 23 kink to the BL 45 corner, standing just inside the LE line."""
    return _solid(
        _plate(
            (G.stk_book_le_fs_bl_23, 23.0),
            (G.stk_book_le_fs_bl_45, 45.0),
            T,
            offset=-T / 2,
        )
    )


def ble() -> cq.Workplane:
    """BLE: the LE strip from the fuselage side to the BL 23 kink."""
    return _solid(
        _plate(
            _le_points()[0],
            (G.stk_book_le_fs_bl_23, 23.0),
            T,
            offset=-T / 2,
            trim0=FITTED_BLE_TRIM,
        )
    )


def _od_bl(x: float) -> float:
    return 45.0 + (x - G.stk_book_le_fs_bl_45) * (BL_END - 45.0) / (
        X_END - G.stk_book_le_fs_bl_45
    )


def fairing() -> cq.Workplane:
    """The urethane LE block between the outboard diagonal and the LE line, BL 45 to the skin edge (fitted)."""
    a, b = G.stk_book_le_fs_bl_45, X_END
    return _solid(
        _xloft(
            a + 3 * FITTED_TIP_X,
            b - 3 * FITTED_TIP_X,
            lambda x: _od_bl(x) + T / 2 + FITTED_FAIR_INSET,
            lambda x: _skin_hi(x) - FITTED_FAIR_INSET,
            lambda x, y: top_inner_z(x, y) - FITTED_CLEAR,
            lambda x, y: bot_inner_z(x, y) + FITTED_CLEAR,
        )
    )


def _tank_lo(x: float) -> float:
    jn, bab_x = JUNCTION, G.stk_book_bab_fuselage_fs
    if x <= jn:
        return 23.0 + T / 2 + FITTED_CLEAR
    if x <= bab_x:
        s0 = side_outer(bab_x)
        return (
            max(23.0 + (x - jn) * (s0 - 23.0) / (bab_x - jn), side_outer(x))
            + FITTED_CLEAR
        )
    return max(side_outer(x), bl_spar(x)) + FITTED_CLEAR


def _tank_hi(x: float) -> float:
    return min(le_bl(x) - FITTED_TANK_INSET, 45.0 - T / 2 - FITTED_CLEAR, BL_END)


def tank() -> cq.Workplane:
    """The fuel tank volume (display envelope): the outboard trapezoid and the inboard lobe between the inside faces, shaded in the lab."""
    x0 = G.stk_book_le_fs_bl_23 + FITTED_TIP_X
    x1 = spar_fs(45.0) - 2 * FITTED_END_GAP
    return _solid(
        _xloft(
            x0,
            x1,
            _tank_lo,
            _tank_hi,
            lambda x, y: top_inner_z(x, y) - FITTED_CLEAR,
            lambda x, y: bot_inner_z(x, y) + FITTED_CLEAR,
        )
    )


def tank_volume_gal() -> float:
    """Gross volume of the tank envelope (one side) in US gallons (231 cu in)."""
    return tank().val().Volume() / 231.0


def sump_blister() -> cq.Workplane:
    """The sump blister: a right-triangle section in the corner between the fuselage side and the bottom skin, legs the printed 2.75 depth, 21 long from F.S. 103.5."""
    length, depth, _flange = G.stk_book_sump_blister_in
    x0 = G.stk_book_sump_fs[0]
    x1 = x0 + length
    top_wl = lambda bl: min(bot_outer_wl(bl), G.spar_bottom_wl - FITTED_BLISTER_BIAS)  # noqa: E731
    wires = []
    xs = sorted(set(np.arange(x0, x1, FITTED_NX_STEP).tolist()) | {x1})
    for x in xs:
        e = min(x - x0, x1 - x)
        k = FITTED_BLISTER_END_SCALE + (1 - FITTED_BLISTER_END_SCALE) * min(
            e / FITTED_BLISTER_ENDS, 1.0
        )
        y0 = side_outer(x) + FITTED_END_GAP / 3
        legs = depth * k
        z0 = z_of_wl(top_wl(y0))
        wires.append(
            _wire(
                [
                    (x, y0, z0),
                    (x, y0 + legs, z_of_wl(top_wl(y0 + legs))),
                    (x, y0, z0 - legs),
                ]
            )
        )
    return _solid(_loft(wires))


def _top_outer_z(x: float, y: float) -> float:
    return top_inner_z(x, y) + T


def fuel_cap() -> cq.Workplane:
    """The fuel cap: a 2 1/4 in rim disc on the top skin, in the aft half of the tank (position fitted)."""
    x, y = FITTED_CAP_POS
    z = _top_outer_z(x, y)
    return _solid(
        cq.Solid.makeCylinder(
            FITTED_CAP_DIA / 2,
            FITTED_CAP_RIM_H,
            cq.Vector(x, y, z + FITTED_END_GAP / 3),
            cq.Vector(0, 0, 1),
        )
    )


def drain_insert() -> cq.Workplane:
    """The 1 by 1 in drain insert, set into the bottom skin at the low corner (position scaled off p147)."""
    x, y = FITTED_DRAIN_POS
    zb = bot_inner_z(x, y)
    s = FITTED_DRAIN_SIZE
    return _solid(
        cq.Solid.makeBox(
            s,
            s,
            FITTED_DRAIN_T,
            cq.Vector(x - s / 2, y - s / 2, zb - T),
        )
    )


def vent_line() -> cq.Workplane:
    """The 1/4 in vent line: a stub standing 1/2 in above the top skin near the fuselage side (position fitted)."""
    x, off = FITTED_VENT_POS
    y = side_outer(x) + off
    return _solid(
        cq.Solid.makeCylinder(
            FITTED_VENT_DIA / 2,
            FITTED_VENT_RISE,
            cq.Vector(x, y, _top_outer_z(x, y)),
            cq.Vector(0, 0, 1),
        )
    )


def screen() -> cq.Workplane:
    """The domed outlet screen over the 1 1/4 in hole, on the inside of the bottom skin (a spherical cap)."""
    x, y = FITTED_SCREEN_POS
    r = FITTED_SCREEN_DIA / 2
    h = FITTED_SCREEN_RISE
    big_r = (r * r + h * h) / (2 * h)
    zb = bot_inner_z(x, y) + FITTED_CLEAR
    ball = cq.Solid.makeSphere(
        big_r, cq.Vector(x, y, zb + h - big_r), angleDegrees1=-90, angleDegrees2=90
    )
    keep = cq.Solid.makeBox(4 * r, 4 * r, 2 * h, cq.Vector(x - 2 * r, y - 2 * r, zb))
    return _solid(ball.intersect(keep))


def outlet_tube() -> cq.Workplane:
    """The 3/8 in outlet tube end: sticks 0.4 in out of the fuselage side, about 13 in forward of the firewall and 3 in below the tank bottom line."""
    x = G.fs_firewall - FITTED_TUBE_FWD_OF_FIREWALL
    y0 = side_outer(x)
    wl = bot_outer_wl(y0) - FITTED_TUBE_BELOW_TANK
    return _solid(
        cq.Solid.makeCylinder(
            FITTED_TUBE_DIA / 2,
            FITTED_TUBE_OUT,
            cq.Vector(x, y0 + FITTED_TUBE_ENTRY, z_of_wl(wl)),
            cq.Vector(0, 1, 0),
        )
    )


def _cut_extrude(pts_xz, x_lo, x_hi) -> cq.Workplane:
    """A void through the side panel: the polygon in the (F.S., z) plane extruded across the panel's thickness at the two ends of its F.S. range."""
    ys = [half_width(x) for x in np.linspace(x_lo, x_hi, 8)]
    y_in, y_out = min(ys) - FITTED_CUT_PAD, max(ys) + SIDE_T + FITTED_CUT_PAD
    wp = cq.Workplane("XZ").polyline(pts_xz).close().extrude(-(y_out - y_in))
    return wp.translate((0, y_in, 0))


def cutout_baggage() -> cq.Workplane:
    """The baggage opening in the fuselage side: the p142 table, each row a station forward of the spar face with its top and bottom depth below WL 23."""
    tab = G.stk_book_cutout_fwd_in
    top = [(SPAR_AT_SIDE - st, z_of_wl(G.side_panel_top_wl - t)) for st, t, _b in tab]
    bot = [(SPAR_AT_SIDE - st, z_of_wl(G.side_panel_top_wl - b)) for st, _t, b in tab]
    pts = top + bot[::-1]
    return _cut_extrude(pts, top[0][0], top[-1][0])


def cutout_tank() -> cq.Workplane:
    """The tank opening in the fuselage side (the round forward end drawn as a chamfer)."""
    fwd, aft, top_d, bot_d = G.stk_book_cutout_aft_in
    xa, xb = SPAR_AT_SIDE - fwd, SPAR_AT_SIDE - aft
    zt = z_of_wl(G.side_panel_top_wl - top_d)
    zb = z_of_wl(G.side_panel_top_wl - bot_d)
    zm = (zt + zb) / 2
    c = FITTED_CUTOUT_AFT_ROUND
    pts = [(xa + c, zt), (xb, zt), (xb, zb), (xa + c, zb), (xa, zm)]
    return _cut_extrude(pts, xa, xb)


# ---- assembly ----------------------------------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "strake.ribs": ("rib_r23", "rib_r45"),
    "strake.baffles": ("b23", "db", "bab", "od"),
    "strake.leading_edge": ("tle", "ble"),
    "strake.skins": ("skin_bottom", "skin_top", "cutout_baggage", "cutout_tank"),
    "strake.sump": ("sump_blister",),
    "strake.tank": ("tank",),
    "strake.fairing": ("fairing",),
    "strake.fittings": (
        "drain_insert",
        "vent_line",
        "screen",
        "outlet_tube",
        "fuel_cap",
    ),
}
# parts that are laid into another part by design (a set-in insert, a dome on the floor, the display envelope of the tank): not in the clearance set
INSET_PARTS = frozenset({"drain_insert", "tank"})
# plates that butt at the junction (floxed joints): the clearance test allows these pairs a small overlap
JOINTS = frozenset(
    {
        frozenset(p)
        for p in (
            ("rib_r23", "b23"),
            ("rib_r23", "db"),
            ("rib_r23", "bab"),
            ("b23", "db"),
            ("b23", "bab"),
            ("db", "bab"),
            ("db", "rib_r45"),
            ("tle", "ble"),
            ("tle", "rib_r23"),
            ("ble", "rib_r23"),
            ("tle", "rib_r45"),
            ("tle", "od"),
            ("od", "rib_r45"),
            ("bab", "ble"),
        )
    }
)
JOINT_MAX_CU_IN = 0.6


@lru_cache(maxsize=1)
def _right() -> dict[str, FusePart]:
    rep, der = "representational", "derived"
    surf = "inside faces from the jig planes and the p142 nose table, heights as printed on p141"
    return {
        "rib_r23": FusePart(
            "rib_r23",
            rib_r23(),
            rep,
            (_P141, _P147),
            f"R23 along BL 23 from the LE kink (F.S. 73.3) to the B23 junction, 0.35 thick, height from the {surf}; the A14 outline is not held, so the nose profile is fitted",
        ),
        "rib_r45": FusePart(
            "rib_r45",
            rib_r45(),
            rep,
            (_P141, _P147),
            f"R45 along BL 45 from the LE corner (F.S. 99.5) to the spar face, 0.35 thick, height from the {surf}; the A14 outline is not held, so the nose profile is fitted",
        ),
        "b23": FusePart(
            "b23",
            b23(),
            der,
            (_P141, _P147),
            "B23 baffle along BL 23 from the junction to the spar face, 21.3 long and 7.3 high as printed, 0.35 thick; the corner notches and the 5 by 3 oval hole are not drawn",
        ),
        "db": FusePart(
            "db",
            db(),
            der,
            (_P141, _P147),
            "DB diagonal baffle from the junction to R45, 28.5 long printed (the plan closes at 28.2), 7.3 high at the fore end and 6.5 at the aft end as printed, 0.35 thick; notches not drawn",
        ),
        "bab": FusePart(
            "bab",
            bab(),
            der,
            (_P141, _P147),
            "BAB baffle from the junction to the fuselage side at F.S. 103.5, 13.4 long printed, 7.3 high outboard and 7.75 inboard as printed, 0.35 thick",
        ),
        "od": FusePart(
            "od",
            od(),
            rep,
            (_P141, _P147),
            "OD outboard diagonal from the TLE and R45 corner to the spar face near BL 54.6, 0.35 thick; the outline is fitted to the skin contour (no length is printed)",
        ),
        "tle": FusePart(
            "tle",
            tle(),
            der,
            (_P141, _P147),
            "TLE fuel-tank LE strip from the BL 23 kink to the BL 45 corner, just inside the LE line, 0.35 thick; plan length 34.2 against the printed 33.5 (the ends are bevelled), height from the inside faces at the nose (about 2.6)",
        ),
        "ble": FusePart(
            "ble",
            ble(),
            der,
            (_P141, _P147),
            "BLE baggage LE strip from the fuselage side to the BL 23 kink, just inside the LE line, 0.35 thick; plan length 25.7 against the printed 25.5, height from the inside faces at the nose (about 2.6)",
        ),
        "skin_bottom": FusePart(
            "skin_bottom",
            skin_bottom(),
            rep,
            (_P142, _P143, _P147),
            "bottom skin, 0.35 foam, over the plan of both skins (edges from p147 and p142); the curvature is fitted: flat in B.L. on the jig plane, pulled up at the nose by the p142 cutout table",
        ),
        "skin_top": FusePart(
            "skin_top",
            skin_top(),
            rep,
            (_P142, _P143, _P147),
            "top skin, 0.35 foam, over the plan of both skins (edges from p147 and p142); the curvature is fitted: flat on the WL 21.6 plane, pulled down at the nose by the p142 cutout table",
        ),
        "cutout_baggage": FusePart(
            "cutout_baggage",
            cutout_baggage(),
            rep,
            (_P142,),
            "the baggage opening in the fuselage side from the p142 table (stations forward of the spar face, depths below WL 23; medium confidence); a void: material the opening removes, no mass",
            void=True,
        ),
        "cutout_tank": FusePart(
            "cutout_tank",
            cutout_tank(),
            rep,
            (_P142,),
            "the tank opening in the fuselage side, 30 to 15 in forward of the spar face, 1.40 to 9.15 below WL 23 (the 1.90 near the aft end is a conflict, not drawn); the round forward end is drawn as a chamfer; a void, no mass",
            void=True,
        ),
        "sump_blister": FusePart(
            "sump_blister",
            sump_blister(),
            rep,
            (_P144, _P147),
            "sump blister in the corner of the fuselage side and the bottom skin, F.S. 103.5 to 124.5 (21 long), 2.75 deep, tapered at the ends; the exact outline is not unambiguous on the page (the 5 in dimension)",
        ),
        "tank": FusePart(
            "tank",
            tank(),
            rep,
            (_P142, _P147, _OM_P4),
            "fuel tank volume (display envelope, overlaps the baffles by design): the outboard trapezoid and the inboard lobe between the inside faces; gross volume is about 24.6 gal a side against 25.5 (plans) and 28 (manual) a tank, which is order of magnitude only for a fitted shape; the capacity is a conflict, the model keeps 26",
        ),
        "fairing": FusePart(
            "fairing",
            fairing(),
            rep,
            (_P145, _P147),
            "urethane LE fairing block between the outboard diagonal and the LE line (2 lb/ft3, CP30 LPC 84); the block is carved to the rib noses on the airplane, so its outline is fitted",
        ),
        "drain_insert": FusePart(
            "drain_insert",
            drain_insert(),
            rep,
            (_P143, _P146, _P147),
            "1 by 1 by 1/8 in aluminium drain insert set into the bottom skin at the low corner; position scaled off p147 (plus or minus 1 in); the thread is 1/8-27 (CP28 LPC 60)",
        ),
        "vent_line": FusePart(
            "vent_line",
            vent_line(),
            rep,
            (_P143,),
            "1/4 in aluminium vent line opening 1/2 in above the top skin; position fitted (the OM puts the vents at the centre fuselage just aft of the canopy)",
        ),
        "screen": FusePart(
            "screen",
            screen(),
            rep,
            (_P143, _P147),
            "domed screen over the 1 1/4 in hole in the inboard bottom skin, about F.S. 115.8, BL 14 (scaled off p147, plus or minus 1 in)",
        ),
        "outlet_tube": FusePart(
            "outlet_tube",
            outlet_tube(),
            rep,
            (_P144,),
            "the 3/8 in outlet tube's end, 0.4 in out of the fuselage side about 13 in forward of the firewall and 3 in under the tank line; the eight-foot run to the cockpit floor is not drawn",
        ),
        "fuel_cap": FusePart(
            "fuel_cap",
            fuel_cap(),
            rep,
            (_P145,),
            "fuel cap rim, 2 1/4 in hole, 0.3 high, in the aft half of the tank; position fitted (the page draws it without dimensions)",
        ),
    }


def build_strake(side: str = "right") -> dict[str, FusePart]:
    """All chapter 21 solids of one strake. ``side`` is "right" or "left" (the mirror)."""
    if side not in ("right", "left"):
        raise ValueError(side)
    out = {}
    for n, p in _right().items():
        s = p.solid
        if side == "left":
            s = cq.Workplane("XY").add(s.val().mirror("XZ"))
        out[n] = FusePart(n, s, p.fidelity, p.cite, p.note, void=p.void)
    return out
