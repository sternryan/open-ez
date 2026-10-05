"""Engine installation (plans chapter 23, pdf pages p156 to p158): the engine block, the throttle and mixture bracket, the cowl outline, the wing-root metal rib.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Chapter 23 is a three-page delta, not an installation: the mount, the engine, the prop, the exhaust and the baffles live in Sections IIA, IIC and IIL, which the
owner does not hold. Printed here (config ``eng_book_*``, ``GEOMETRY_PROVENANCE``): the weight limits, the bracket sizes (fig 23-1), the cowl trim and
reinforcement, the rib sheet and flanges, the 2 deg down thrust (CP32 p5, CP38 p5). NOT printed anywhere held: any engine, mount, prop or exhaust
dimension or station. The engine solid is therefore an O-235-sized block, ``representational`` and striped in the lab, aft of the firewall on BL 0, with the
crankshaft pitched 2 deg (the prop flange end higher than the magneto end).
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq

from .fuselage_book import FusePart, G, z_of_wl

_P156, _P157, _P158, _P171 = (f"plans-1980:p{n}" for n in (156, 157, 158, 171))
_CP32 = "cp-text:p32"
_CP26, _CP27, _TCDS = "cp-text:p26", "cp-text:p27", "tcds-e223:p7"

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_COWL_FWD = 125.4  # fitted, not book: the cowl's forward edge, just aft of the stainless-faced firewall (F.S. 125.28)
FITTED_COWL_TOP_WL = 32.8  # book, medium: p171 top of the fuselage at the firewall WL 32.8 (hand digits, 3x crop)
FITTED_COWL_BOTTOM_WL = 11.0  # fitted, not book: cowl bottom, below the engine block and clear of the spar bottom (WL 13.5)
FITTED_COWL_T = 0.12  # fitted, not book: the glass cowl wall is drawn this thick
FITTED_BRACKET_X = 4.0  # fitted, not book: the bracket plate starts this far aft of the engine block's front face
FITTED_BRACKET_GAP = 0.05  # fitted, not book: the plate stands this far under the block
FITTED_ANGLE_LEN = 2.5  # fitted, not book: the upright angle's length across the plate (the plate is 2.5 wide)
FITTED_RIB_GAP = (
    0.05  # fitted, not book: the rib's front edge stands this far aft of the spar face
)
FITTED_RIB_HOLES = (
    (3.0, 0.9, 0.6),
    (10.0, 0.7, 0.5),
)  # fitted, not book: (F.S. aft of the rib's front edge, height above the wing plane, radius) of the rudder cable and aileron pushrod cut-outs
FITTED_RIB_Y_GAP = (
    0.03  # fitted, not book: the rib stands this far inboard of the wing root face
)

WORKSHOP_PARTS: frozenset = frozenset()
FIDELITIES_USED = frozenset({"representational"})
DOWN_THRUST_DEG = G.eng_book_down_thrust_deg


# ---- helpers --------------------------------------------------------------------------------------------------------------------------
def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


# ---- the block ---------------------------------------------------------------------------------------------------------------------------
# Ledger row 71: the block is now the O-235 component compound of core.engine_o235_book (crankcase, four cylinders, sump, accessory housing, crank stub
# and flange disc), placed from the prop flange datum (eng_o235_flange_fs) and pitched about the flange point. The old 30 by 32 by 18 box and its
# unsourced front station eng_book_block_fwd_fs are retired: the front face is derived below.
def block() -> cq.Workplane:
    """The engine block: crankcase + cylinders + sump + accessory housing + crank stub and flange disc, representational, placed from the flange."""
    from . import engine_o235_book as o

    shapes = []
    for wp in (
        o.crankcase(),
        o.cylinders(),
        o.sump(),
        o.accessory_housing(),
        o.crank_flange(),
    ):
        shapes.extend(wp.vals()[0].Solids())
    return _solid(cq.Compound.makeCompound(shapes))


def block_front_fs() -> float:
    """F.S. of the block's front (anti-prop) face: the smallest x of the block compound. Derived from the flange; replaces eng_book_block_fwd_fs."""
    return cq.Compound.makeCompound(block().vals()).BoundingBox().xmin


def block_bottom_z(x: float) -> float:
    """z of the engine's lowest underside (the carburettor bottom) at F.S. ``x`` on the centreline: a plane pitched with the crank, the aft end higher by the down thrust."""
    from . import engine_o235_book as o

    depth = -(o.FITTED_CARB_POS[2] - o.FITTED_CARB_SIZE[2] / 2)
    fx, _fy, fz = o._datum()
    th = math.radians(DOWN_THRUST_DEG)
    return fz - depth / math.cos(th) + (x - fx) * math.tan(th)


# ---- the bracket ---------------------------------------------------------------------------------------------------------------------------
def bracket() -> cq.Workplane:
    """The throttle and mixture bracket: the 0.063 plate (6.5 by 2.5) with the carb and oil-drain holes, and the 2 by 2 in upright angle riveted under its aft end."""
    length, width, t = G.eng_book_bracket_plate_in
    oil_d, oil_from_carb, carb_d, carb_from_fwd = G.eng_book_bracket_holes_in
    ang_a, ang_b, ang_t = G.eng_book_bracket_angle_in
    x0 = block_front_fs() + FITTED_BRACKET_X
    zt = (
        block_bottom_z(x0 + length) - FITTED_BRACKET_GAP
    )  # the lowest the block comes over the plate is its forward end
    zt = min(zt, block_bottom_z(x0) - FITTED_BRACKET_GAP)
    y0 = G.eng_book_crank_bl - width / 2
    plate = _box(x0, x0 + length, y0, y0 + width, zt - t, zt)
    for xc, d in (
        (x0 + carb_from_fwd, carb_d),
        (x0 + carb_from_fwd + oil_from_carb, oil_d),
    ):
        hole = cq.Solid.makeCylinder(
            d / 2,
            4 * t,
            cq.Vector(xc, G.eng_book_crank_bl, zt - 2 * t),
            cq.Vector(0, 0, 1),
        )
        plate = plate.cut(hole)
    # the angle: a horizontal leg under the plate's aft end and a vertical leg hanging down at the aft edge
    xa = x0 + length
    horiz = _box(xa - ang_a, xa, y0, y0 + FITTED_ANGLE_LEN, zt - t - ang_t, zt - t)
    vert = _box(xa - ang_t, xa, y0, y0 + FITTED_ANGLE_LEN, zt - t - ang_b, zt - t)
    return _solid(cq.Compound.makeCompound([plate, horiz.fuse(vert)]))


# ---- the cowl ---------------------------------------------------------------------------------------------------------------------------------
def cowl() -> cq.Workplane:
    """The cowl outline: flat top and bottom shells between the firewall and the wing trailing edge at the root, BL 23 each side (where the cowl meets the wing),
    left open at the sides (the wing-root rib closes them)."""
    x0, x1 = FITTED_COWL_FWD, G.wing_book_te_fs_bl_23
    half = G.wing_root_bl
    zb, zt = z_of_wl(FITTED_COWL_BOTTOM_WL), z_of_wl(FITTED_COWL_TOP_WL)
    outer = _box(x0, x1, -half, half, zb, zt)
    t = FITTED_COWL_T
    inner = _box(x0 - 1, x1 + 1, -half - 1, half + 1, zb + t, zt - t)
    return _solid(outer.cut(inner))


# ---- the wing-root rib ---------------------------------------------------------------------------------------------------------------------
def _spar_aft_face(bl: float) -> float:
    kink = G.spar_kink_bl
    return G.spar_aft_face_fs_centre + max(0.0, abs(bl) - kink) * math.tan(
        math.radians(G.spar_outboard_sweep_deg)
    )


def rib_right() -> cq.Workplane:
    """The right wing-root metal rib: a 0.020 plate on the inboard face of the wing root, from the spar face to the trailing edge, with the two cut-outs."""
    from . import wing_book as wb

    th, _sheet_l, _sheet_w, _flange, _edge = G.eng_book_rib_in
    bl = G.wing_root_bl
    xa = _spar_aft_face(bl) + FITTED_RIB_GAP
    xb = wb.te_fs(bl)
    n = 14
    xs = [xa + (xb - xa) * i / (n - 1) for i in range(n)]
    top = [(x, wb.z_surface(bl, x, +1)) for x in xs]
    bot = [(x, wb.z_surface(bl, x, -1)) for x in xs][::-1]
    pts = []
    for p in top + bot:
        if not pts or math.dist(p, pts[-1]) > 1e-6:
            pts.append(p)
    if math.dist(pts[0], pts[-1]) < 1e-6:
        pts.pop()
    y1 = bl - FITTED_RIB_Y_GAP
    wp = (
        cq.Workplane("XZ").polyline(pts).close().extrude(-th).translate((0, y1 - th, 0))
    )
    s = wp.val()
    for dx, zc, r in FITTED_RIB_HOLES:
        hole = cq.Solid.makeCylinder(
            r, 4 * th, cq.Vector(xa + dx, y1 - 2 * th, zc), cq.Vector(0, 1, 0)
        )
        s = s.cut(hole)
    return _solid(s)


def rib_left() -> cq.Workplane:
    return _solid(rib_right().val().mirror("XZ"))


# ---- assembly ----------------------------------------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "engine.block": ("block",),
    "engine.starter": ("starter",),
    "engine.alternator": ("alternator",),
    "engine.magnetos": ("magnetos",),
    "engine.carburettor": ("carburettor",),
    "engine.fuel_pump": ("fuel_pump",),
    "engine.mount_pads": ("mount_pads",),
    "engine.bracket": ("bracket",),
    "engine.cowl": ("cowl",),
    "engine.rib": ("rib_right", "rib_left"),
}


@lru_cache(maxsize=1)
def build_engine() -> dict[str, FusePart]:
    from . import engine_o235_book as o235

    rep = "representational"
    return {
        "block": FusePart(
            "block",
            block(),
            rep,
            (_P156, _P171, _CP32, _TCDS),
            "O-235 block compound (fitted shape; installation is in Section II, not held): crankcase, four cylinders sized from the TCDS bore, sump, accessory housing, crank stub and prop flange disc, placed from the prop flange face at F.S. 155.8 (cp-text:p28) on BL 0 with the crank pitched 2 deg down thrust (CP32 p5); nothing but the stub and disc lies aft of the flange; no engine, mount, prop or exhaust dimension is printed in any held source; striped in the lab",
        ),
        "bracket": FusePart(
            "bracket",
            bracket(),
            rep,
            (_P156,),
            "throttle and mixture bracket: the 0.063 plate 6.5 by 2.5 in with the 2 in oil-drain hole and the 1.8 in carb hole (printed; the 1.8 is medium) and a 2 by 2 in upright angle under its aft end; where it sits on the engine is fitted",
        ),
        "starter": FusePart(
            "starter",
            o235.starter(),
            rep,
            (_CP27, _TCDS),
            "starter at the prop end, station 150 and aft (CP27 p4), published mass 17 lb (cp-text:p49); fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "alternator": FusePart(
            "alternator",
            o235.alternator(),
            rep,
            (_CP27, _TCDS),
            "belt alternator at the prop end, published mass 7 lb (cp-text:p49, cp-text:p26); fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "magnetos": FusePart(
            "magnetos",
            o235.magnetos(),
            rep,
            (_CP27, _TCDS),
            "two magnetos on the anti-prop rear face, upper left and right (Slick, vendor-slick-4300); fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "carburettor": FusePart(
            "carburettor",
            o235.carburettor(),
            rep,
            (_CP27, _TCDS),
            "carburettor on the sump bottom pad; fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "fuel_pump": FusePart(
            "fuel_pump",
            o235.fuel_pump(),
            rep,
            (_CP27, _TCDS),
            "plunger fuel pump on the rear left pad (TCDS E-223 p4 NOTE 4); fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "mount_pads": FusePart(
            "mount_pads",
            o235.mount_pads(),
            rep,
            (_CP26, _TCDS),
            "four dynafocal mount pads on the case rear face; not in the engine dry weight (the closure row owns the mount, cp-text:p26); fitted size and position (core.engine_o235_book FITTED_*, ledger rows 70 and 71), no dimensioned drawing is held",
        ),
        "cowl": FusePart(
            "cowl",
            cowl(),
            rep,
            (_P156, _P157, _P171),
            "cowl outline: top and bottom shells from the firewall to the wing trailing edge at the root (F.S. 148.4, p126) and BL 23 each side (p171); the cowl shape, trim line and the 9 in trim are not drawn, only its extent; WL 32.8 top is medium",
        ),
        "rib_right": FusePart(
            "rib_right",
            rib_right(),
            rep,
            (_P157, _P158),
            "right wing-root metal rib, 6061-0 sheet 0.020 thick (the p157 text prints 0.20, a typo), on the inboard face of the wing root from the spar to the trailing edge; the outline is a hand drawing with no coordinates and the two cut-outs are fitted",
        ),
        "rib_left": FusePart(
            "rib_left",
            rib_left(),
            rep,
            (_P157, _P158),
            "left wing-root metal rib, the mirror of the right",
        ),
    }
