"""Electrical system (plans chapter 22, pdf pages p149 to p155): battery shelf, battery, relays, wire runs, lights, antennas.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Printed (config ``elec_book_*``, ``GEOMETRY_PROVENANCE``): a 12 V 25 Ah battery in the nose on a shelf bonded to NG30 and F6 (p149, p150, p155), shelf and
cover dimensions (p155), the start relay and over-voltage unit on the front of F22 (p149), wire gauges, antenna strip lengths (CP30 LPC 78, CP26). NOT
printed anywhere held: the battery station (A6 only: the model draws it at the middle of the nose box, F.S. 11, for illustration), its size and weight, every
wire length, the strobe supply station, the light sizes. Every solid is therefore ``representational``.

The nose of the box model is foam-filled (``core.nose_book``: side blocks, floor blocks, top block); the real battery sits in a pocket carved from it. The
pocket is not modelled, so the battery group, the relays and the battery cable overlap those foam blocks by design (``POCKET_PARTS``).
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq

from .fuselage_book import FusePart, G, z_of_wl

_P149, _P150, _P151, _P152, _P153, _P154, _P155 = (
    f"plans-1980:p{n}" for n in range(149, 156)
)

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_BATTERY_IN = (
    7.0,
    4.2,
    4.4,
)  # fitted, not book: battery length (F.S.), width (B.L.) and height; no battery dimension is printed
FITTED_BATTERY_Y0 = 2.4  # fitted, not book: the battery's inboard face, clear of the NG30 plates (B.L. 1.7) and the pedal arms (B.L. 2.3)
FITTED_FLOOR_TOP_WL = 2.5  # derived: the top of the nose floor blocks, model z -14.9 (WL 2.5), read from core.nose_book (the shelf rests on it)
FITTED_COVER_GAP = 0.1  # fitted, not book: clearance between the battery and its BID cover (the p155 0.4 is a duct-tape wrap gap, not drawn)
FITTED_COVER_T = (
    0.11  # book: p155 three BID plies at 0.0375 laid thickness each (p85 laid ply)
)
FITTED_STRAP_W = 0.5  # fitted, not book: width of the stainless worm clamp band
FITTED_STRAP_T = 0.03  # fitted, not book: band thickness
FITTED_STRAP_X = (
    2.0  # fitted, not book: how far from the battery's forward face the band sits
)
FITTED_RELAY_IN = (
    1.7,
    1.5,
    1.5,
)  # fitted, not book: size of the start relay and of the over-voltage unit (along F.S., B.L., height)
FITTED_RELAY_Y = (
    (3.0, 4.5),
    (5.0, 6.5),
)  # fitted, not book: B.L. spans of the two units on the front of F22
FITTED_RELAY_WL = 5.9  # fitted, not book: WL of the bottom of the units (model z -11.5), above the floor blocks and clear of the pedal arms
FITTED_CABLE_R = 0.15  # fitted, not book: battery cable radius (2 AWG, p152)
FITTED_BUNDLE_R = 0.3  # fitted, not book: panel bundle radius
FITTED_RUN_R = 0.15  # fitted, not book: cable radius along the cockpit corner
FITTED_BUNDLE_WL = 14.4  # fitted, not book: WL of the bundle across the forward face of the panel (p153 says only 'forward side of the panel')
FITTED_BUNDLE_BL = 9.6  # fitted, not book: B.L. of the bundle where it turns down the right lower corner
FITTED_BUNDLE_DOWN_WL = (
    4.4  # fitted, not book: WL where the bundle turns aft along the floor corner
)
FITTED_BUNDLE_STAND = (
    0.35  # fitted, not book: gap between the bundle and the panel face
)
FITTED_LIGHT_IN = (
    2.4,
    1.6,
    1.0,
)  # fitted, not book: position light size (along F.S., across, height); the Whelen A600 dimensions are not in the plans
FITTED_LIGHT_GAP = 0.05  # fitted, not book: gap between the light and the wing tip face
FITTED_LIGHT_WL = 18.0  # fitted, not book: WL of the light bottom (the tip's chord-line plane is WL 17.4)
FITTED_STROBE_IN = (
    4.0,
    3.0,
    2.0,
)  # fitted, not book: strobe power supply size (along F.S., across, height); not printed
FITTED_STROBE_Y = -10.8  # fitted, not book: B.L. of the strobe supply's outboard face (left side), clear of the left side panel; it extends inboard from here
FITTED_STROBE_WL = (
    9.4  # fitted, not book: WL of the bottom of the strobe supply (model z -8.0)
)
FITTED_STROBE_GAP = (
    0.3  # fitted, not book: gap behind the front seat bulkhead's aft face
)
FITTED_NAV_W = 0.5  # book: p152 copper tape 1/2 in wide
FITTED_NAV_T = 0.02  # fitted, not book: foil thickness drawn
FITTED_NAV_BL0 = 13.0  # fitted, not book: B.L. where each strip starts, just outside the fuselage side (the page draws a V on the canard underside, no dimensions)
FITTED_NAV_X_FRAC = 0.4  # fitted, not book: strip at this fraction of the canard chord
FITTED_NAV_DROP = 0.25  # fitted, not book: how far under the canard LE plane the strip lies (the canard skin bottom is 0.16 below)
FITTED_COMM_W = 0.5  # fitted, not book: foil width
FITTED_COMM_T = 0.02  # fitted, not book: foil thickness
FITTED_COMM_BELOW_TE = (
    1.0  # book: cp-text:p26 the strips lie 1 in ahead of the trailing edge
)
FITTED_COMM_GAP = 0.125  # book: cp-text:p26 1/8 in gap between the two strips
FITTED_COMM_WL0 = 30.0  # fitted, not book: WL where the strips start on the winglet, just above the rudder top (WL 28.9) so the foil is in the fin's own trailing edge
FITTED_WIRE_END_GAP = (
    0.2  # fitted, not book: wire runs stop this far short of the firewall face
)

# parts that sit in a pocket carved from the nose foam (not modelled): they overlap the foam blocks by design
POCKET_PARTS = frozenset(
    {
        "shelf",
        "battery",
        "cover",
        "strap",
        "start_relay",
        "overvoltage_unit",
        "battery_cable",
    }
)
POCKET_FOAM = frozenset({"side_blocks", "floor_blocks", "top_block", "skin"})
# the run along the cockpit corner passes the seat bulkheads at their access holes (not drawn)
PASS_THROUGH = {
    "firewall_cable": frozenset({"front_seat_bkhd", "rear_seat_bkhd", "panel"})
}
# thin foil laid inside the winglet foam by design
IN_FOAM_PARTS = frozenset({"comm_strips"})
WORKSHOP_PARTS: frozenset = frozenset()
FIDELITIES_USED = frozenset({"representational"})


# ---- helpers --------------------------------------------------------------------------------------------------------------------------
def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _compound(solids) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound(list(solids)))


def _tube(points, r) -> cq.Workplane:
    """A polyline of cylinders joined by spheres: a representational wire run."""
    solids = []
    for a, b in zip(points, points[1:]):
        d = cq.Vector(*b) - cq.Vector(*a)
        solids.append(cq.Solid.makeCylinder(r, d.Length, cq.Vector(*a), d))
    for p in points[1:-1]:
        solids.append(
            cq.Solid.makeSphere(r, cq.Vector(*p), angleDegrees1=-90, angleDegrees2=90)
        )
    return _compound(solids)


def _bar(p0, p1, width_dir, w, t) -> cq.Solid:
    """A thin rectangular strip from p0 to p1: ``w`` wide along ``width_dir`` (a unit vector) and ``t`` thick across both."""
    d = cq.Vector(*p1) - cq.Vector(*p0)
    wv = cq.Vector(*width_dir).normalized()
    tv = d.cross(wv).normalized()

    def rect(p):
        c = cq.Vector(*p)
        pts = [
            c + wv * (w / 2) + tv * (t / 2),
            c - wv * (w / 2) + tv * (t / 2),
            c - wv * (w / 2) - tv * (t / 2),
            c + wv * (w / 2) - tv * (t / 2),
        ]
        return cq.Wire.makePolygon(pts + [pts[0]])

    s = cq.Solid.makeLoft([rect(p0), rect(p1)], True)
    return s if s.Volume() > 0 else cq.Solid(s.wrapped.Reversed())


# ---- the solids ---------------------------------------------------------------------------------------------------------------------------
def _battery_box() -> tuple[float, float, float, float, float, float]:
    length, width, height = FITTED_BATTERY_IN
    x0 = G.elec_book_battery_model_fs - length / 2
    z0 = z_of_wl(FITTED_FLOOR_TOP_WL) + G.elec_book_shelf_in[0]
    return (
        x0,
        x0 + length,
        FITTED_BATTERY_Y0,
        FITTED_BATTERY_Y0 + width,
        z0,
        z0 + height,
    )


def shelf() -> cq.Workplane:
    """The shelf pad under the battery, 0.6 thick from the floor mark (p155)."""
    x0, x1, y0, y1, z0, _z1 = _battery_box()
    pad = G.elec_book_shelf_in[0]
    return _solid(_box(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, z0 - pad, z0))


def battery() -> cq.Workplane:
    x0, x1, y0, y1, z0, z1 = _battery_box()
    return _solid(_box(x0, x1, y0, y1, z0, z1))


def cover() -> cq.Workplane:
    """The three-ply BID cover over the battery: a shell round its top and four sides, open at the bottom."""
    x0, x1, y0, y1, z0, z1 = _battery_box()
    g, t = FITTED_COVER_GAP, FITTED_COVER_T
    outer = _box(x0 - g - t, x1 + g + t, y0 - g - t, y1 + g + t, z0, z1 + g + t)
    inner = _box(x0 - g, x1 + g, y0 - g, y1 + g, z0 - 1.0, z1 + g)
    return _solid(outer.cut(inner))


def strap() -> cq.Workplane:
    """The stainless worm clamp: a U-shaped band over the cover, standing on the shelf."""
    x0, _x1, y0, y1, z0, z1 = _battery_box()
    g, t = FITTED_COVER_GAP + FITTED_COVER_T, FITTED_STRAP_T
    xa = x0 + FITTED_STRAP_X
    outer = _box(xa, xa + FITTED_STRAP_W, y0 - g - t, y1 + g + t, z0, z1 + g + t)
    inner = _box(xa - 1, xa + FITTED_STRAP_W + 1, y0 - g, y1 + g, z0 - 1, z1 + g)
    return _solid(outer.cut(inner))


def _relay(y0, y1) -> cq.Solid:
    length, _w, height = FITTED_RELAY_IN
    z0 = z_of_wl(FITTED_RELAY_WL)
    xf = G.fs_f22
    return _box(xf - length, xf, y0, y1, z0, z0 + height)


def start_relay() -> cq.Workplane:
    return _solid(_relay(*FITTED_RELAY_Y[0]))


def overvoltage_unit() -> cq.Workplane:
    return _solid(_relay(*FITTED_RELAY_Y[1]))


def battery_cable() -> cq.Workplane:
    """Battery to the relays on F22 (representational run, 2 AWG)."""
    x0, x1, y0, y1, z0, z1 = _battery_box()
    zr = z_of_wl(FITTED_RELAY_WL) + FITTED_RELAY_IN[2] / 2
    yb = (y0 + y1) / 2
    yr = sum(FITTED_RELAY_Y[0]) / 2
    xr = G.fs_f22 - FITTED_RELAY_IN[0]
    pts = [(x1 + FITTED_COVER_GAP + FITTED_COVER_T + 0.05, yb, zr), (xr - 0.1, yr, zr)]
    return _tube(pts, FITTED_CABLE_R)


def panel_bundle() -> cq.Workplane:
    """The panel wire bundle: across the forward face of the panel, then down the right lower corner (p153; representational)."""
    x = G.fs_panel - FITTED_BUNDLE_STAND
    zt = z_of_wl(FITTED_BUNDLE_WL)
    zd = z_of_wl(FITTED_BUNDLE_DOWN_WL)
    pts = [
        (x, -FITTED_BUNDLE_BL, zt),
        (x, FITTED_BUNDLE_BL, zt),
        (x, FITTED_BUNDLE_BL, zd),
    ]
    return _tube(pts, FITTED_BUNDLE_R)


def firewall_cable() -> cq.Workplane:
    """From the foot of the bundle aft along the cockpit floor corner to the firewall, passing the seat bulkheads at their access holes (not drawn)."""
    x = G.fs_panel - FITTED_BUNDLE_STAND
    zd = z_of_wl(FITTED_BUNDLE_DOWN_WL)
    pts = [
        (x, FITTED_BUNDLE_BL, zd),
        (G.fs_firewall - FITTED_WIRE_END_GAP, FITTED_BUNDLE_BL, zd),
    ]
    return _tube(pts, FITTED_RUN_R)


def _light(side: int) -> cq.Solid:
    length, width, height = FITTED_LIGHT_IN
    tip_bl = G.wing_book_rib_bl[3]
    x0 = G.wing_book_le_fs_tip
    z0 = z_of_wl(FITTED_LIGHT_WL)
    y0 = tip_bl + FITTED_LIGHT_GAP
    return _box(x0, x0 + length, y0, y0 + width, z0, z0 + height)


def light_right() -> cq.Workplane:
    return _solid(_light(1))


def light_left() -> cq.Workplane:
    return _solid(_light(1).mirror("XZ"))


def strobe_supply() -> cq.Workplane:
    """The strobe power supply behind the front seat bulkhead on the left (one of the three printed places; no station is printed)."""
    length, width, height = FITTED_STROBE_IN
    xa = G.fs_front_seat_bkhd_top + G.front_seat_bkhd_thickness + FITTED_STROBE_GAP
    z0 = z_of_wl(FITTED_STROBE_WL)
    return _solid(
        _box(xa, xa + length, FITTED_STROBE_Y, FITTED_STROBE_Y + width, z0, z0 + height)
    )


def _nav(side: int) -> cq.Solid:
    x = G.fs_canard_le + FITTED_NAV_X_FRAC * G.canard_chord
    z = (
        G.canard_le_wl - FITTED_NAV_DROP
    )  # canard_le_wl is already a model z (above the wing plane)
    y0 = side * FITTED_NAV_BL0
    y1 = side * (FITTED_NAV_BL0 + G.elec_book_nav_strip_in)
    return _bar((x, y0, z), (x, y1, z), (1.0, 0.0, 0.0), FITTED_NAV_W, FITTED_NAV_T)


def nav_strip_right() -> cq.Workplane:
    return _solid(_nav(1))


def nav_strip_left() -> cq.Workplane:
    return _solid(_nav(-1))


def comm_strips() -> cq.Workplane:
    """The two comm foil strips inside the right winglet foam, 20.3 in long, 1 in ahead of the trailing edge, 1/8 in apart (CP26 p8)."""
    from . import winglet_book as wl

    length = G.elec_book_comm_strip_in
    wl0 = FITTED_COMM_WL0
    dz = (
        length
        * (wl.TOP_WL - wl.ROOT_WL)
        / math.hypot(wl.TOP_WL - wl.ROOT_WL, wl.te_fs(wl.TOP_WL) - wl.te_fs(wl.ROOT_WL))
    )
    wl1 = wl0 + dz
    solids = []
    for k in (-1, 1):
        off = k * (FITTED_COMM_GAP + FITTED_COMM_T) / 2
        pts = []
        for w in (wl0, wl1):
            pts.append(
                (
                    wl.te_fs(w) - FITTED_COMM_BELOW_TE,
                    wl.y_centre(w) + off,
                    z_of_wl(w),
                )
            )
        solids.append(
            _bar(pts[0], pts[1], (1.0, 0.0, 0.0), FITTED_COMM_W, FITTED_COMM_T)
        )
    return _compound(solids)


# ---- assembly ------------------------------------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "elec.battery_shelf": ("shelf", "cover", "strap"),
    "elec.battery": ("battery",),
    "elec.relays": ("start_relay", "overvoltage_unit"),
    "elec.wiring": ("battery_cable", "panel_bundle", "firewall_cable"),
    "elec.lights": ("light_right", "light_left", "strobe_supply"),
    "elec.antennas": ("nav_strip_right", "nav_strip_left", "comm_strips"),
}


@lru_cache(maxsize=1)
def build_electrical() -> dict[str, FusePart]:
    rep = "representational"
    pocket = "sits in a pocket carved from the nose foam (the pocket is not modelled, so it overlaps the foam blocks by design)"
    return {
        "shelf": FusePart(
            "shelf",
            shelf(),
            rep,
            (_P155,),
            f"battery shelf pad, 0.6 thick from the floor mark (printed, small hand digits), 4 BID plies laid on wax paper; plan size fitted; {pocket}",
        ),
        "battery": FusePart(
            "battery",
            battery(),
            rep,
            (_P150, _P151, _P155),
            f"12 V 25 Ah battery (Gill PSG-9, printed); its station is on A6 (not held), so it is drawn at the middle of the nose box, F.S. 11, for illustration only; size and weight are not printed (the nose battery adds about 19 lb over the small one, CP27 p4); {pocket}",
        ),
        "cover": FusePart(
            "cover",
            cover(),
            rep,
            (_P155,),
            f"three-ply BID cover over the battery, drawn at its laid thickness with a fitted clearance; {pocket}",
        ),
        "strap": FusePart(
            "strap",
            strap(),
            rep,
            (_P155,),
            f"stainless worm clamp band over the cover and shelf; the page puts it round the cover, battery, shelf and F6 through the F6 strap slot, which this fitted band does not reach; {pocket}",
        ),
        "start_relay": FusePart(
            "start_relay",
            start_relay(),
            rep,
            (_P149, _P152),
            f"start relay on the front face of F22 (printed place, as far forward as practical); size and position across fitted; {pocket}",
        ),
        "overvoltage_unit": FusePart(
            "overvoltage_unit",
            overvoltage_unit(),
            rep,
            (_P149,),
            f"over-voltage unit beside the start relay on the front of F22; size and position fitted; {pocket}",
        ),
        "battery_cable": FusePart(
            "battery_cable",
            battery_cable(),
            rep,
            (_P152,),
            f"battery cable to the relays, 2 AWG (printed), length and route fitted; {pocket}",
        ),
        "panel_bundle": FusePart(
            "panel_bundle",
            panel_bundle(),
            rep,
            (_P153,),
            "panel wire bundle along the forward side of the panel and down the right lower corner (printed in words); route and size fitted, potted every 10 in",
        ),
        "firewall_cable": FusePart(
            "firewall_cable",
            firewall_cable(),
            rep,
            (_P153,),
            "run from the bundle aft along the cockpit floor corner to the firewall wire hole (printed place, p148); route fitted; passes the seat bulkheads at their access holes, which are not drawn",
        ),
        "light_right": FusePart(
            "light_right",
            light_right(),
            rep,
            (_P151, _P155),
            "green position light at the right wing tip (Whelen A600, silicone-bonded); size fitted, drawn on the tip leading edge outboard of the tip rib",
        ),
        "light_left": FusePart(
            "light_left",
            light_left(),
            rep,
            (_P151, _P155),
            "red position light at the left wing tip (Whelen A600); size fitted, the mirror of the right",
        ),
        "strobe_supply": FusePart(
            "strobe_supply",
            strobe_supply(),
            rep,
            (_P149, _P155),
            "strobe power supply (Whelen A413A) behind the front seat bulkhead on the left, one of three printed places; no station or size is printed",
        ),
        "nav_strip_right": FusePart(
            "nav_strip_right",
            nav_strip_right(),
            rep,
            (_P152,),
            "right nav antenna copper strip, 22.8 in (CP30 LPC 78) by 1/2 in, on the canard underside outside the fuselage; the V angle, station and thickness are not printed",
        ),
        "nav_strip_left": FusePart(
            "nav_strip_left",
            nav_strip_left(),
            rep,
            (_P152,),
            "left nav antenna copper strip, the mirror of the right",
        ),
        "comm_strips": FusePart(
            "comm_strips",
            comm_strips(),
            rep,
            (_P152,),
            "two comm foil strips in the right winglet, 20.3 in long, 1 in ahead of the trailing edge and 1/8 in apart (CP26 p8); laid in the foam, so they overlap the winglet core by design; start height fitted",
        ),
    }
