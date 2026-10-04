"""Canopy (plans chapter 18, pdf pages p108 to p117): bubble, frame, pads, covers, hinges, latches, catch, door.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Printed (config, ``GEOMETRY_PROVENANCE``): the 68 in plexiglass length, the rear cut FS 117, the eight pad stations (2.5 long, measured forward
from FS 117 to each pad's aft edge), SC-1 at FS 56.75, the 4.3 by 3.7 door, checks A (WL 36.5 at least) and B (WL 35.3 at FS 110), the nose tip
5.0 in aft of the panel. NOT printed: the bubble contour (a vendor part with no section), the frame surface, the cover profiles, the vent, the
latch linkage, the door position and the hinge length. Every solid is therefore ``representational``: the bubble is a lofted fitted shape that
meets the printed constraints, sitting on the fuselage side top edge at the existing model's half-width and longeron WL (read from
``core.fuselage_book``, never typed here).

Hinges are on the right, latches, door and safety catch on the left. ``open_pose`` rotates the canopy about the right hinge line (0 deg = closed).
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator

from .fuselage_book import (
    FusePart,
    G,
    Z_TOP,
    half_width,
    plan_bend_points,
    z_of_wl,
)

_P108, _P109, _P110, _P111, _P112, _P113, _P114, _P115, _P116, _P117 = (
    f"plans-1980:p{n}" for n in range(108, 118)
)

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_PLEXI_T = 0.125  # fitted, not book: plexiglass thickness (not in the plans)
FITTED_PLEXI_INSET = 0.6  # fitted, not book: bubble base sits this far inside the side's outer face (the glass frame takes the rest)
FITTED_FRAME_H = (
    1.0  # fitted, not book: height of the foam and glass sill band above the longerons
)
FITTED_SUPER_N = 3.0  # fitted, not book: section squareness (2 = ellipse); picked so the bubble clears the roll-over structure
FITTED_HEADREST_FS = 88.0  # fitted, not book: headrest station (chapter 26); only sets where check A is taken
FITTED_TOP_MARGIN_A = 0.3  # fitted, not book: bubble top above the check A minimum, so A is met with margin
FITTED_NOSE_TOP_WL = 25.0  # fitted, not book: bubble top at the nose tip
FITTED_NOSE_HALF_W = 1.5  # fitted, not book: bubble half width at the nose tip
FITTED_NOSE_BLEND_FS = (
    62.0  # fitted, not book: station where the plan outline reaches full width
)
FITTED_TOP_KNOTS = (
    (52.0, 31.0),
    (66.0, 35.9),
    (96.0, 36.6),
)  # fitted, not book: bubble top (FS, WL) between the printed constraints
FITTED_AFT_END_TOP_WL = 30.0  # fitted, not book: bubble top at its aft end (the rear edge trim line cants aft, p108)
FITTED_ARCH_T = 0.6  # fitted, not book: extra frame thickness outside the glass at the rear arch (equals the frame band width)
FITTED_FRONT_COVER_H = (
    1.0,
    2.5,
)  # fitted, not book: front cover height above the sill at F28 and at the front cut
FITTED_REAR_COVER_H = (
    7.0,
    0.5,
)  # fitted, not book: rear cover height above the sill at the rear cut and at the firewall
FITTED_PAD_H = (
    FITTED_FRAME_H  # fitted, not book: pads fill the frame band to its full height
)
FITTED_HINGE_PIN_R = 0.15  # fitted, not book: hinge pin radius
FITTED_HINGE_LEAF_T = 0.0625  # fitted, not book: hinge leaf thickness
FITTED_HINGE_LEAF_H = 1.5  # fitted, not book: hinge leaf height each side of the pin
FITTED_LATCH_LEN = 1.5  # fitted, not book: fore-aft length of each C7/C8 fitting
FITTED_LATCH_LEG = (
    0.45,
    0.6,
)  # fitted, not book: C7/C8 leg and height (printed 0.45 and 0.6 on p117), placed on the frame
FITTED_LATCH_ROD_R = (
    5 / 32
)  # fitted, not book: C6 tube radius (printed 5/16 OD); stand-off from the frame is fitted
FITTED_LATCH_ROD_LEN = (
    28.4  # fitted, not book: C6 length as printed (p117), centred between two latches
)
FITTED_LATCH_ROD_OUT = (
    0.9  # fitted, not book: C6 stand-off outboard of the frame outer face
)
FITTED_SC1_LEN = 2.5  # fitted, not book: SC-1 plate fore-aft length (pad length)
FITTED_SC1_DROP = (
    1.2  # fitted, not book: SC-1 hangs this far below the sill to reach the catch bolt
)
FITTED_SC1_BOLT_DROP = (
    0.8  # fitted, not book: catch bolt this far below the longeron WL
)
FITTED_SC1_BOLT_R = 0.125  # fitted, not book: catch bolt radius
FITTED_SC1_BOLT_OUT = (
    0.6  # fitted, not book: catch bolt protrudes this far out of the side
)
FITTED_DOOR_FS = (
    3.0 + G.fs_panel
)  # fitted, not book: p116 "3 in aft of the instrument panel", panel station itself in conflict; low confidence
FITTED_DOOR_TOP_BELOW = (
    3.0  # fitted, not book: p116 "3 in below the top of the longeron", hand digit
)
FITTED_DOOR_T = 0.1  # fitted, not book: door plate thickness (printed .025 aluminium, thickened to show)
FITTED_VENT_H = 0.8  # fitted, not book: vent block depth under the bubble roof
FITTED_VENT_FS = (
    52.0,
    58.0,
)  # fitted, not book: vent block fore and aft stations (p112 gives clear area 4.5 by 6 only)
FITTED_VENT_W = 4.5  # fitted, not book: vent width (printed 4.5 clear, medium)
FITTED_BRACE_FS = (
    90.0,
    100.0,
    104.5,
)  # fitted, not book: front tube and aft pair; the derived front tube FS 82 hits the roll-over (FS 79 to 83.6)
FITTED_BRACE_WL = 30.0  # fitted, not book: brace tube height
FITTED_BRACE_R = 5 / 32  # fitted, not book: printed 5/16 OD arrow shaft
FITTED_BLOCKS_FS = (
    (63.0, 67.0),
    (72.0, 76.0),
    (98.0, 102.0),
    (106.0, 110.0),
)  # fitted, not book: four temporary blocks (full-size outlines are on p108 only)
FITTED_SKIN_STANDOFF = 0.4  # fitted, not book: the lab draws the fuselage skin plies about 0.36 in outside the side's face (guide.fuselage_export), so fittings on the side stand off by this
FITTED_FOAM_EXTRA_H = 1.2  # fitted, not book: the uncarved foam blocks stand this far above the finished sill band (2 in blocks, p109)
FITTED_FOAM_PROUD = 0.5  # fitted, not book: the uncarved foam stands this far outside the fuselage side before it is carved to the contour
FITTED_PLY_VIS_T = 0.07  # fitted, not book: drawn thickness of one glass ply (visual only; a cured BID ply is about 0.01 in)
FITTED_ENDS_FS = (
    52.0,
    106.0,
)  # fitted, not book: where the front and rear regions of the frame end and begin (BID front and rear, UND sides)
FITTED_BLOCK_W = 1.0  # fitted, not book: block width inboard of the side
FITTED_BLOCK_H = 2.0  # fitted, not book: block height above the longerons

UND_LAP_IN = 3.0  # book: p110 the side UND laps 3 in onto the front and rear BID

# derived from the printed values (not fitted)
NOSE_FS = (
    G.fs_panel + 5.0
)  # p109: nose tip 5.0 in aft of the instrument panel (FS 44.75)
PLEXI_AFT_FS = NOSE_FS + G.canopy_plexi_length_in  # p108: 68 in long (FS 112.75)
_SIDE_T = G.side_panel_thickness  # the side's outer face is half_width + this
HINGE_Y = (
    max(
        half_width(f)
        for f in (G.canopy_hinge_spans_fs[1][0], G.canopy_hinge_spans_fs[1][1])
    )
    + _SIDE_T
    + FITTED_SKIN_STANDOFF
    + FITTED_HINGE_LEAF_T
    + FITTED_HINGE_PIN_R
)  # the straight hinge line stands off the widest hinge station; the aft hinge leaf stands further off
HINGE_Z = Z_TOP
FIDELITIES_USED = frozenset({"representational"})

_PLAN_STEP = 0.5
_N_ARC = 24
_LOFT_STEP = 1.5  # bubble sections every 1.5 in (ruled between them), plus the side's plan bends and both ends


def outer_y(fs: float) -> float:
    """Outer face of the fuselage side (half width plus the side thickness)."""
    return half_width(fs) + _SIDE_T


def plexi_half_width(fs: float) -> float:
    """Bubble half width at the sill: inside the side's outer face, rounded at the nose in plan."""
    full = outer_y(fs) - FITTED_PLEXI_INSET
    if fs >= FITTED_NOSE_BLEND_FS:
        return full
    u = (FITTED_NOSE_BLEND_FS - fs) / (FITTED_NOSE_BLEND_FS - NOSE_FS)
    return max(FITTED_NOSE_HALF_W, full * math.sqrt(max(0.0, 1.0 - u * u)))


def _top_curve() -> PchipInterpolator:
    pts = [
        (NOSE_FS, FITTED_NOSE_TOP_WL),
        *FITTED_TOP_KNOTS,
        (
            FITTED_HEADREST_FS - 6.0,
            G.canopy_check_a_wl + FITTED_TOP_MARGIN_A,
        ),  # check A is taken 6 in forward of the headrest
        (G.canopy_check_b_fs, G.canopy_check_b_wl),  # check B, FS 110
        (PLEXI_AFT_FS, FITTED_AFT_END_TOP_WL),
    ]
    pts.sort()
    return PchipInterpolator([p[0] for p in pts], [p[1] for p in pts])


_TOP = _top_curve()


def top_wl(fs: float) -> float:
    """Outside top of the bubble at the centreline, WL."""
    return float(_TOP(fs))


def _arc(
    w: float, h: float, base_z: float, reverse: bool = False
) -> list[tuple[float, float]]:
    """Half super-ellipse over the sill, from the right base (+w) over the top to the left base (-w)."""
    pts = []
    for i in range(_N_ARC + 1):
        th = math.pi * i / _N_ARC
        c, s = math.cos(th), math.sin(th)
        pts.append(
            (
                w * math.copysign(abs(c) ** (2 / FITTED_SUPER_N), c),
                base_z + h * abs(s) ** (2 / FITTED_SUPER_N),
            )
        )
    return pts[::-1] if reverse else pts


def section_points(fs: float, extra_out: float = 0.0) -> list[tuple[float, float]]:
    """Closed crescent (y, z) of the glass at FS; ``extra_out`` thickens the outside (the frame's rear arch)."""
    w = plexi_half_width(fs)
    h = top_wl(fs) - G.canopy_check_datum_wl
    outer = _arc(w + extra_out, h + extra_out, Z_TOP)
    inner = _arc(w - FITTED_PLEXI_T, h - FITTED_PLEXI_T, Z_TOP, reverse=True)
    return outer + inner


def inner_y_at(fs: float, wl: float) -> float:
    """Inside surface half width of the glass at FS and WL (for tube ends)."""
    w = plexi_half_width(fs) - FITTED_PLEXI_T
    h = top_wl(fs) - G.canopy_check_datum_wl - FITTED_PLEXI_T
    v = (z_of_wl(wl) - Z_TOP) / h
    if not 0 <= v < 1:
        raise ValueError((fs, wl))
    return w * (1 - v**FITTED_SUPER_N) ** (1 / FITTED_SUPER_N)


def _loft_stations() -> list[float]:
    """Section stations of the bubble: every 1.5 in from the nose, the side's plan bends, and the aft end."""
    n = int((PLEXI_AFT_FS - NOSE_FS) / _LOFT_STEP)
    fs = {NOSE_FS + i * _LOFT_STEP for i in range(n)} | {PLEXI_AFT_FS}
    fs.update(x for x, _h in plan_bend_points() if NOSE_FS < x < PLEXI_AFT_FS)
    fs.update(
        (FITTED_HEADREST_FS - 6.0, G.canopy_check_b_fs)
    )  # the stations of checks A and B, so the ruled bubble meets them exactly
    return sorted(fs)


def _loft(stations: list[float], pts_fn) -> cq.Workplane:
    wp = cq.Workplane("YZ").workplane(offset=stations[0])
    prev = stations[0]
    for fs in stations:
        if fs != prev:
            wp = wp.workplane(offset=fs - prev)
            prev = fs
        wp = wp.polyline(pts_fn(fs)).close()
    return wp.loft(
        ruled=True, combine=True
    )  # ruled: the base edge follows the plan polyline exactly


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound([w.val() for w in solids]))


def _plan_prism(pts: list[tuple[float, float]], z0: float, z1: float) -> cq.Workplane:
    """Plan polygon (FS, y) extruded between two z levels."""
    return (
        cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    )


def _stations(a: float, b: float, step: float = _PLAN_STEP) -> list[float]:
    """Plan breakpoints of the side plus a fixed step, in [a, b]."""
    fs = {a, b}
    fs.update(x for x, _h in plan_bend_points() if a < x < b)
    n = int((b - a) / step)
    fs.update(a + i * step for i in range(1, n))
    return sorted(fs)


def _side_ring(a: float, b: float, y_of) -> list[tuple[float, float]]:
    st = _stations(a, b)
    right = [(f, y_of(f)) for f in st]
    left = [(f, -y_of(f)) for f in reversed(st)]
    return right + left


def _band_poly(
    f0: float, f1: float, y_in, y_out, sign: float
) -> list[tuple[float, float]]:
    """A side strip (plan view) between two lines, y_in and y_out are functions of FS."""
    st = _stations(f0, f1)
    a = [(f, sign * y_in(f)) for f in st]
    b = [(f, sign * y_out(f)) for f in reversed(st)]
    return a + b


def _frame_band_in(fs: float) -> float:
    return (
        outer_y(fs) - FITTED_PLEXI_INSET
    )  # the bubble's outer face at the sill, same as plexi_half_width past the nose blend


# ---- the solids ----------------------------------------------------------------------------------------------
def plexi() -> cq.Workplane:
    """Plexiglass bubble: a lofted super-elliptic shell, open underneath, FS 44.75 to 112.75."""
    return _loft(_loft_stations(), section_points)


def _ring(h_extra: float = 0.0, proud: float = 0.0) -> cq.Workplane:
    """The sill band round the bubble's footprint, ``h_extra`` taller and ``proud`` further out (the uncarved foam, the glass plies)."""
    f_front = G.canopy_front_cut_fs
    outer = _plan_prism(
        _side_ring(f_front, PLEXI_AFT_FS, lambda f: outer_y(f) + proud),
        Z_TOP,
        Z_TOP + FITTED_FRAME_H + h_extra,
    )
    # the bubble footprint (plan), nose rounded; extended past the aft end so the cut is clean
    st = (
        _loft_stations()
    )  # the same stations as the bubble, so the cut follows its ruled base edge exactly
    right = [(f, plexi_half_width(f)) for f in st]
    foot = (
        right
        + [(PLEXI_AFT_FS + 1.0, right[-1][1]), (PLEXI_AFT_FS + 1.0, -right[-1][1])]
        + [(f, -plexi_half_width(f)) for f in reversed(st)]
    )
    inner = _plan_prism(foot, Z_TOP - 0.5, Z_TOP + FITTED_FRAME_H + h_extra + 0.5)
    return outer.cut(inner)


def _arch(extra: float = 0.0) -> cq.Workplane:
    return _loft(
        [PLEXI_AFT_FS, G.canopy_rear_cut_fs], lambda fs: _arch_points(fs, extra)
    )


def _arch_points(fs: float, extra: float = 0.0) -> list[tuple[float, float]]:
    """Rear arch section: the glass section at the aft end, thickened outside, base width following the fuselage side."""
    w = outer_y(fs) - FITTED_PLEXI_INSET
    h = top_wl(PLEXI_AFT_FS) - G.canopy_check_datum_wl
    outer = _arc(w + FITTED_ARCH_T + extra, h + FITTED_ARCH_T + extra, Z_TOP)
    inner = _arc(w - FITTED_PLEXI_T, h - FITTED_PLEXI_T, Z_TOP, reverse=True)
    return outer + inner


def frame_ring() -> cq.Workplane:
    """Foam and glass sill band round the bubble, plus the rear arch. Pads are cut out of it by ``frame``."""
    return _ring().union(_arch())


def frame_foam() -> cq.Workplane:
    """The foam frame before it is carved (f18.foam-core): taller and proud of the fuselage side, as fitted blocks."""
    return _ring(FITTED_FOAM_EXTRA_H, FITTED_FOAM_PROUD).union(_arch(FITTED_FOAM_PROUD))


# the five-ply schedule (p110 box): 1 BID overall, 2 BID overall, 3 UND sides, 4 BID front and rear, 5 UND sides (all BID at 45 deg)
FRAME_PLY_SCHEDULE = (
    ("BID", "overall", 45.0),
    ("BID", "overall", 45.0),
    ("UND", "sides", 0.0),
    ("BID", "ends", 45.0),
    ("UND", "sides", 0.0),
)


def _fs_slab(f0: float, f1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(f1 - f0, 200.0, 80.0, centered=False)
        .translate((f0, -100.0, Z_TOP - 5.0))
    )


def _ply_region(kind: str) -> cq.Workplane | None:
    front, rear = FITTED_ENDS_FS
    if kind == "overall":
        return None
    if kind == "sides":  # the side UND laps 3 in onto the front and rear
        return _fs_slab(front - UND_LAP_IN, rear + UND_LAP_IN)
    return _fs_slab(0.0, front).union(_fs_slab(rear, 200.0))


def frame_plies() -> list[cq.Workplane]:
    """The five glass plies over the frame, in lay order: thin shells grown outward from the sill band's top and the rear arch's outer face,
    each FITTED_PLY_VIS_T thick (drawn, not to scale), restricted to the region the schedule gives it."""
    env = [
        _ring(k * FITTED_PLY_VIS_T).union(_arch(k * FITTED_PLY_VIS_T))
        for k in range(len(FRAME_PLY_SCHEDULE) + 1)
    ]
    out = []
    for k, (_cloth, kind, _deg) in enumerate(FRAME_PLY_SCHEDULE, start=1):
        shell = env[k].cut(env[k - 1])
        reg = _ply_region(kind)
        out.append(shell if reg is None else shell.intersect(reg))
    return out


def frame_carved() -> cq.Workplane:
    """The frame carved to the fuselage contour, before the inside is carved (f18.carve-outside): the band and arch with no pad pockets."""
    return frame_ring()


def _pad_box(fs_aft_edge_fwd: float, left: bool) -> cq.Workplane:
    """One pad: in the sill band, 2.5 long, aft edge ``fs_aft_edge_fwd`` forward of the rear cut."""
    aft = G.canopy_rear_cut_fs - fs_aft_edge_fwd
    fwd = aft - G.canopy_pad_length_in
    sg = -1.0 if left else 1.0
    poly = _band_poly(fwd, aft, _frame_band_in, outer_y, sg)
    return _plan_prism(poly, Z_TOP, Z_TOP + FITTED_PAD_H)


def pads_hinge() -> cq.Workplane:
    return _compound([_pad_box(e, False) for e in G.canopy_pad_aft_edge_right_in])


def pads_latch() -> cq.Workplane:
    e = G.canopy_pad_aft_edge_left_in
    return _compound([_pad_box(e[i], True) for i in (0, 1, 3)])


def pad_catch() -> cq.Workplane:
    return _pad_box(G.canopy_pad_aft_edge_left_in[2], True)


def frame() -> cq.Workplane:
    out = frame_ring()
    for e in G.canopy_pad_aft_edge_right_in:
        out = out.cut(_pad_box(e, False))
    for e in G.canopy_pad_aft_edge_left_in:
        out = out.cut(_pad_box(e, True))
    return out


def _wedge(f0: float, f1: float, h0: float, h1: float) -> cq.Workplane:
    """Cover: plan footprint between the side outer faces, top sloping from height h0 at f0 to h1 at f1 above the sill."""
    foot = _plan_prism(_side_ring(f0, f1, outer_y), Z_TOP, Z_TOP + max(h0, h1) + 1.0)
    prof = (
        cq.Workplane("XZ")
        .polyline([(f0, Z_TOP), (f1, Z_TOP), (f1, Z_TOP + h1), (f0, Z_TOP + h0)])
        .close()
        .extrude(-40, both=True)
    )
    return foot.intersect(prof)


def front_cover() -> cq.Workplane:
    return _wedge(G.fs_f28 + 0.2, G.canopy_front_cut_fs, *FITTED_FRONT_COVER_H)


def rear_cover() -> cq.Workplane:
    return _wedge(G.canopy_rear_cut_fs, G.fs_firewall, *FITTED_REAR_COVER_H)


def blocks() -> cq.Workplane:
    out = []
    for f0, f1 in FITTED_BLOCKS_FS:
        for sg in (1.0, -1.0):
            poly = _band_poly(
                f0, f1, lambda f: half_width(f) - FITTED_BLOCK_W, half_width, sg
            )
            out.append(_plan_prism(poly, Z_TOP, Z_TOP + FITTED_BLOCK_H))
    return _compound(out)


def vent() -> cq.Workplane:
    """Vent block: a teardrop (pointed forward, round aft) filling FITTED_VENT_H under the bubble roof."""
    f0, f1 = FITTED_VENT_FS
    r = FITTED_VENT_W / 2
    c = f1 - r
    arc = [
        (c + r * math.cos(a), r * math.sin(a))
        for a in np.radians(np.linspace(-150, 150, 25))
    ]
    prism = _plan_prism([(f0, 0.0), *arc], Z_TOP, Z_TOP + 60.0)
    inner_filled = _inner_filled()
    return prism.intersect(inner_filled).cut(
        inner_filled.translate((0, 0, -FITTED_VENT_H))
    )


def _inner_filled() -> cq.Workplane:
    """The volume inside the glass (ruled, same stations as the bubble)."""
    return _loft(_loft_stations(), _filled_inner)


def _filled_inner(fs: float) -> list[tuple[float, float]]:
    w = plexi_half_width(fs) - FITTED_PLEXI_T
    h = top_wl(fs) - G.canopy_check_datum_wl - FITTED_PLEXI_T
    return _arc(w, h, Z_TOP)


def brace_tubes() -> cq.Workplane:
    """Three tubes across the canopy, trimmed to the inside surface of the glass."""
    inside = _inner_filled()
    tubes = []
    for fs in FITTED_BRACE_FS:
        long = (
            cq.Workplane("XZ")
            .circle(FITTED_BRACE_R)
            .extrude(20.0, both=True)
            .translate((fs, 0, z_of_wl(FITTED_BRACE_WL)))
        )
        tubes.append(long.intersect(inside))
    return _compound(tubes)


def hinge_fuselage() -> cq.Workplane:
    """Pins and the fuselage leaves, on the right: the straight hinge line stands off the side outer face."""
    out = []
    for f0, f1 in G.canopy_hinge_spans_fs:
        out.append(
            cq.Workplane("YZ")
            .circle(FITTED_HINGE_PIN_R)
            .extrude(f1 - f0)
            .translate((f0, HINGE_Y, HINGE_Z))
        )
        y0 = HINGE_Y - FITTED_HINGE_PIN_R - FITTED_HINGE_LEAF_T
        out.append(
            cq.Workplane("XY")
            .box(f1 - f0, FITTED_HINGE_LEAF_T, FITTED_HINGE_LEAF_H, centered=False)
            .translate((f0, y0, HINGE_Z - FITTED_HINGE_LEAF_H))
        )
    return _compound(out)


def hinge_canopy() -> cq.Workplane:
    """The canopy leaves of the two hinges, on the frame side."""
    out = []
    for f0, f1 in G.canopy_hinge_spans_fs:
        y0 = HINGE_Y - FITTED_HINGE_PIN_R - FITTED_HINGE_LEAF_T
        out.append(
            cq.Workplane("XY")
            .box(f1 - f0, FITTED_HINGE_LEAF_T, FITTED_HINGE_LEAF_H, centered=False)
            .translate((f0, y0, HINGE_Z))
        )
    return _compound(out)


def latches() -> cq.Workplane:
    """Three C7/C8 fittings on the left frame at the derived pad centres, joined by the two 28.4 in C6 tubes."""
    out = []
    centres = G.canopy_latch_pad_centres_fs
    leg, hgt = FITTED_LATCH_LEG
    for c in centres:
        y = max(outer_y(c - FITTED_LATCH_LEN / 2), outer_y(c + FITTED_LATCH_LEN / 2))
        out.append(
            cq.Workplane("XY")
            .box(FITTED_LATCH_LEN, leg, hgt, centered=False)
            .translate((c - FITTED_LATCH_LEN / 2, -y - leg, Z_TOP + 0.15))
        )
    for a, b in zip(
        centres[:-1], centres[1:]
    ):  # centres[0] is the rear latch, centres[2] the front
        mid = (a + b) / 2
        y = -(max(outer_y(a), outer_y(b)) + FITTED_LATCH_ROD_OUT)
        out.append(
            cq.Workplane("YZ")
            .circle(FITTED_LATCH_ROD_R)
            .extrude(FITTED_LATCH_ROD_LEN)
            .translate(
                (mid - FITTED_LATCH_ROD_LEN / 2, y, Z_TOP + FITTED_FRAME_H * 0.5 + 0.3)
            )
        )
    return _compound(out)


def _sc1_x() -> tuple[float, float]:
    c = G.canopy_safety_catch_fs
    return c - FITTED_SC1_LEN / 2, c + FITTED_SC1_LEN / 2


def sc1() -> cq.Workplane:
    """SC-1: a thin plate on the left safety-catch pad that hangs below the sill, with a slot for the catch bolt."""
    x0, x1 = _sc1_x()
    c = G.canopy_safety_catch_fs
    y = outer_y(c) + FITTED_SKIN_STANDOFF
    plate = (
        cq.Workplane("XY")
        .box(x1 - x0, 0.02, FITTED_SC1_DROP + FITTED_FRAME_H, centered=False)
        .translate((x0, -y - 0.02, Z_TOP - FITTED_SC1_DROP))
    )
    slot = (
        cq.Workplane("XZ")
        .circle(FITTED_SC1_BOLT_R + 0.06)
        .extrude(1.0, both=True)
        .translate((c, -y, Z_TOP - FITTED_SC1_BOLT_DROP))
    )
    return plate.cut(slot)


def sc1_bolt() -> cq.Workplane:
    """The catch bolt on the fuselage side at FS 56.75, through the SC-1 slot."""
    c = G.canopy_safety_catch_fs
    y = outer_y(c) + FITTED_SKIN_STANDOFF
    return (
        cq.Workplane("XZ")
        .circle(FITTED_SC1_BOLT_R)
        .extrude(-FITTED_SC1_BOLT_OUT)  # XZ normal is -y, so this runs toward +y
        .translate((c, 0, Z_TOP - FITTED_SC1_BOLT_DROP))
        .translate((0, -y - FITTED_SC1_BOLT_OUT, 0))
        .translate((0, 0, 0))
    )


def door() -> cq.Workplane:
    """Left door plate on the side outer face, 4.3 long by 3.7 high; its station is a low-confidence fit."""
    ln, ht = G.canopy_door_size_in
    y = outer_y(FITTED_DOOR_FS) + FITTED_SKIN_STANDOFF
    z_top = z_of_wl(G.canopy_check_datum_wl - FITTED_DOOR_TOP_BELOW)
    return (
        cq.Workplane("XY")
        .box(ln, FITTED_DOOR_T, ht, centered=False)
        .translate((FITTED_DOOR_FS, -y - FITTED_DOOR_T, z_top - ht))
    )


# ---- assembly ------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "canopy.plexi": ("plexi",),
    "canopy.frame": ("frame",),
    "canopy.pads": ("pads_hinge", "pads_latch", "pad_catch"),
    "canopy.blocks": ("blocks",),
    "canopy.vent": ("vent",),
    "canopy.brace_tubes": ("brace_tubes",),
    "canopy.hinges": ("hinge_fuselage", "hinge_canopy"),
    "canopy.latches": ("latches",),
    "canopy.safety_catch": ("sc1", "sc1_bolt"),
    "fuselage.front_cover": ("front_cover",),
    "fuselage.rear_cover": ("rear_cover",),
    "fuselage.door": ("door",),
}
# the parts that turn with the canopy (the rest stay on the fuselage)
CANOPY_ATTACHED = frozenset(
    {
        "plexi",
        "frame",
        "pads_hinge",
        "pads_latch",
        "pad_catch",
        "vent",
        "brace_tubes",
        "hinge_canopy",
        "latches",
        "sc1",
    }
)
MAX_OPEN_DEG = 105.0  # fitted, not book: 90 plus the printed 15 deg past vertical (p115), the arc itself is representational
HINGE_AXIS = ((0.0, HINGE_Y, HINGE_Z), (1.0, HINGE_Y, HINGE_Z))


def open_pose(solid: cq.Workplane, deg: float) -> cq.Workplane:
    """Rotate a canopy-attached solid about the right hinge line; 0 = closed, ``MAX_OPEN_DEG`` fully open (canopy goes up and out to the right)."""
    if not 0.0 <= deg <= MAX_OPEN_DEG:
        raise ValueError(f"open angle {deg} outside 0..{MAX_OPEN_DEG}")
    if deg == 0.0:
        return solid
    # a positive turn about +x moves the canopy toward -y; the canopy opens toward +y, so turn by -deg
    return solid.rotate(HINGE_AXIS[0], HINGE_AXIS[1], -deg)


@lru_cache(maxsize=1)
def _closed() -> dict[str, FusePart]:
    rep = "representational"
    return {
        "plexi": FusePart(
            "plexi",
            plexi(),
            rep,
            (_P108, _P109),
            "68 in, FS 44.75 to 112.75, nose 5.0 aft of the panel; contour is a fitted super-elliptic loft that meets check A (WL 36.5 at 6 in forward of the headrest) and check B (WL 35.3 at FS 110); the bubble is a vendor part with no printed section; thickness fitted",
        ),
        "frame": FusePart(
            "frame",
            frame(),
            rep,
            (_P109, _P110, _P111),
            "foam and glass sill band round the bubble plus a rear arch to the rear cut at FS 117; front cut about FS 41.65 (unnamed datum, representational); outer surface fitted; the eight pad places are left open",
        ),
        "pads_hinge": FusePart(
            "pads_hinge",
            pads_hinge(),
            rep,
            (_P112, _P113),
            "four right pads, 2.5 long, aft edges 20, 25.5, 48 and 53.5 forward of FS 117 (book); width and height of the pad fitted",
        ),
        "pads_latch": FusePart(
            "pads_latch",
            pads_latch(),
            rep,
            (_P112, _P113),
            "three left latch pads, 2.5 long, aft edges 11, 41 and 71 forward of FS 117 (book), centres 104.75, 74.75 and 44.75 (derived; the p117 labels read 104, 74 and 44); width and height fitted",
        ),
        "pad_catch": FusePart(
            "pad_catch",
            pad_catch(),
            rep,
            (_P112, _P116),
            "left safety-catch pad, aft edge 59 forward of FS 117 (book), centre FS 56.75; width and height fitted",
        ),
        "blocks": FusePart(
            "blocks",
            blocks(),
            rep,
            (_P108,),
            "four temporary blocks (two front, two rear) on the longerons; the printed full-size outlines are not modelled; stations and size fitted; discarded after step 9",
        ),
        "vent": FusePart(
            "vent",
            vent(),
            rep,
            (_P112, _P113, _P114),
            "teardrop block under the bubble roof, 4.5 wide (medium); stations and depth fitted",
        ),
        "brace_tubes": FusePart(
            "brace_tubes",
            brace_tubes(),
            rep,
            (_P114,),
            "three 5/16 OD arrow shafts across the canopy; stations fitted (the derived front tube FS 82 would cut through the roll-over structure) and height fitted",
        ),
        "hinge_fuselage": FusePart(
            "hinge_fuselage",
            hinge_fuselage(),
            rep,
            (_P112, _P114, _P115),
            "pins and fuselage leaves of two hinges on the right, spans FS 89 to 97 and 61 to 69 (derived from the pad stations; hinge length not printed); one straight line standing off the side; leaf and pin sizes fitted",
        ),
        "hinge_canopy": FusePart(
            "hinge_canopy",
            hinge_canopy(),
            rep,
            (_P114, _P115),
            "canopy leaves of the two right hinges; turns with the canopy about the hinge line",
        ),
        "latches": FusePart(
            "latches",
            latches(),
            rep,
            (_P115, _P117),
            "three C7/C8 fittings on the left at the derived pad centres (conflict with the p117 labels 0.75 in) and the two 28.4 in C6 tubes between them; linkage geometry is on the full-size drawing only; sizes and stand-off fitted",
        ),
        "sc1": FusePart(
            "sc1",
            sc1(),
            rep,
            (_P116,),
            "SC-1 plate on the left safety-catch pad with a slot over the catch bolt; shape fitted",
        ),
        "sc1_bolt": FusePart(
            "sc1_bolt",
            sc1_bolt(),
            rep,
            (_P116,),
            "catch bolt on the left side at FS 56.75 (book); height and length fitted",
        ),
        "front_cover": FusePart(
            "front_cover",
            front_cover(),
            rep,
            (_P111, _P116),
            "foam left on the fuselage forward of the front cut, F28 to about FS 41.65; profile fitted to the fuselage sides",
        ),
        "rear_cover": FusePart(
            "rear_cover",
            rear_cover(),
            rep,
            (_P111, _P113),
            "rear cover from the cut at FS 117 to the firewall; profile fitted (it fairs into the firewall top)",
        ),
        "door": FusePart(
            "door",
            door(),
            rep,
            (_P116,),
            "left door 4.3 long by 3.7 high (book); its station is derived from a panel station in conflict and is low confidence; plate thickened to show",
        ),
    }


def build_canopy(open_deg: float = 0.0) -> dict[str, FusePart]:
    """All canopy-chapter solids; the canopy-attached ones turned about the right hinge line by ``open_deg`` (0 = closed)."""
    base = _closed()
    if open_deg == 0.0:
        return dict(base)
    out = {}
    for n, p in base.items():
        if n in CANOPY_ATTACHED:
            p = FusePart(n, open_pose(p.solid, open_deg), p.fidelity, p.cite, p.note)
        out[n] = p
    return out
