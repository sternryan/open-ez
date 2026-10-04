"""Winglets and rudders (plans chapter 20, pdf pages p135 to p140): upper fin, lower fin, tip cap, rudder, hinge, corner layups, block A, jig lines.

Same frame as ``core.fuselage_book`` and ``core.wing_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``. ``build_winglet("right")`` and
``build_winglet("left")`` return the two winglets (the left is the mirror, p135); each stands on its wingtip at BL 157.

Printed (config ``winglet_book_*``, ``GEOMETRY_PROVENANCE``): WL 18.4, 65.4, 66.4 and 9.8; the root LE line at FS 159.7 and TE at FS 186.8; the top TE corner FS 196.6;
the rudder hinge FS 176.8 with its 10, 12.14 and 11.5 in widths and its 14.5 in height; the A, B and C jig lengths from the reference point; the corner ply tables.
Derived, medium: the 11.4 in tip chord (a pixel read scaled by the printed rudder widths). Derived, low: the inward lean (about 3.6 in over 47) that closes C.
NOT printed: both airfoils (A-sheets), the lower fin outline, block A, the tip cap shape, cant and toe. So every solid is ``representational`` except the jig
lines (``derived``): the fin is a constant 14 per cent symmetric section, a fitted shape.

The lower fin outline is fitted so that it reproduces the printed 11.5 in rudder width at its bottom: the TE line from (FS 186.8, WL 18.4) to the bottom at FS 190 gives
FS 188.3 at WL 14.4, which is the hinge FS 176.8 plus 11.5. Each fin piece is a ruled loft between two WL sections, split at the rudder hinge line and at the rudder
top and bottom so no boolean is needed between near-coincident surfaces.
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq
import numpy as np

from . import wing_book as wb
from .fuselage_book import FusePart, G, z_of_wl

_P135, _P136, _P137, _P138, _P139, _P140 = (f"plans-1980:p{n}" for n in range(135, 141))

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_TC = 0.14  # fitted, not book: fin section thickness / chord (symmetric); keeps the root (about 3.8 in) inside the 4.3 in core block (p135)
FITTED_SECTION_N = 22  # fitted, not book: points per surface of every section polygon
FITTED_LOWER_LE_BOTTOM_FS = 178.0  # fitted, not book: p135 12 in dimension along the fin bottom (FS 190 forward to about 178), medium
FITTED_TIP_CLEAR = 0.25  # fitted, not book: the fin's inboard face stands this far outboard of the wing tip rib at the wing top
FITTED_PLY_T = (
    G.spar_ply_thickness_laid_in
)  # book p85 laid ply thickness, used as the drawn thickness of every ply here
FITTED_CAP_SHRINK = (
    0.7  # fitted, not book: the 1 in tip cap tapers to this fraction of the top section
)
FITTED_HINGE_R = 0.1  # fitted, not book: piano hinge pin radius
FITTED_BELHORN = (
    2.5,
    0.04,
    2.0,
)  # fitted, not book: belhorn plate (along FS, thick, tall); 0.040 in 4130 is printed (p139), the outline is on the full-size pattern
FITTED_BELHORN_WL = 18.7  # book: p139 belcrank depression centred at WL 18.7
FITTED_BLOCK_A = (
    10.0,
    7.0,
    4.0,
)  # fitted, not book: block A plan (along FS, along BL) and height (two 2 in pieces, p137)
FITTED_JIG_ROD_R = 0.05  # fitted, not book: jig dimension line radius
FITTED_PEG_R = 0.25  # fitted, not book: reference-point peg radius
FITTED_LEG_X = (
    G.winglet_book_root_le_fs_wing_top,
    G.wing_book_te_fs[2],
)  # fitted, not book: corner layup strips run over the wing tip chord, from the winglet LE mark to the wing TE (p136)
FITTED_PLY_GAP = (
    0.02  # fitted, not book: the first display ply floats this far off the core surface
)

ROOT_WL = G.winglet_book_root_wl
TOP_WL = G.winglet_book_top_wl
BOTTOM_WL = G.winglet_book_bottom_wl
HINGE_FS = G.winglet_book_rudder_hinge_fs
RUDDER_TOP_WL = ROOT_WL + G.winglet_book_rudder_height_in[0]
RUDDER_BOT_WL = ROOT_WL - G.winglet_book_rudder_height_in[1]
FIDELITIES_USED = frozenset({"representational", "derived"})
MAX_RUDDER_DEG = G.winglet_book_rudder_max_deg


def lower_te_bottom_fs() -> float:
    """TE FS at the fin bottom that reproduces the printed 11.5 in rudder width at WL 14.4: slope 0.375 in per in down from FS 186.8 at WL 18.4 (derived, about 190)."""
    w_bot = G.winglet_book_rudder_widths_in[2]
    slope = (HINGE_FS + w_bot - G.winglet_book_root_te_fs) / (ROOT_WL - RUDDER_BOT_WL)
    return G.winglet_book_root_te_fs + slope * (ROOT_WL - BOTTOM_WL)


# ---- planform lines and the lean ------------------------------------------------------------------------------------------------------
def le_fs(wl: float) -> float:
    if wl >= ROOT_WL:
        return np.interp(
            wl, (ROOT_WL, TOP_WL), (G.winglet_book_root_le_fs, G.winglet_top_le_fs)
        ).item()
    return np.interp(
        wl, (BOTTOM_WL, ROOT_WL), (FITTED_LOWER_LE_BOTTOM_FS, G.winglet_book_root_le_fs)
    ).item()


def te_fs(wl: float) -> float:
    if wl >= ROOT_WL:
        return np.interp(
            wl, (ROOT_WL, TOP_WL), (G.winglet_book_root_te_fs, G.winglet_book_top_te_fs)
        ).item()
    return np.interp(
        wl, (BOTTOM_WL, ROOT_WL), (lower_te_bottom_fs(), G.winglet_book_root_te_fs)
    ).item()


def chord(wl: float) -> float:
    return te_fs(wl) - le_fs(wl)


def root_half_thickness() -> float:
    return 0.5 * FITTED_TC * G.winglet_root_chord_book_in


def y_root() -> float:
    """Centre-plane BL at WL 18.4: the wing tip rib is BL 157, the fin's inboard face stands just outboard of it."""
    return G.wing_book_rib_bl[3] + root_half_thickness() + FITTED_TIP_CLEAR


def y_centre(wl: float) -> float:
    """Centre plane BL at a waterline: the fin leans inward by ``winglet_cant_in`` over the 47 in of the upper fin (the lean line is extended below the root)."""
    return y_root() - G.winglet_cant_in * (wl - ROOT_WL) / G.winglet_height_book_in


def _half(u: np.ndarray, c: float) -> np.ndarray:
    """Symmetric 4-digit section half thickness at fraction u, closed trailing edge."""
    t = FITTED_TC
    return (
        5.0
        * t
        * c
        * (
            0.2969 * np.sqrt(u)
            - 0.1260 * u
            - 0.3516 * u**2
            + 0.2843 * u**3
            - 0.1036 * u**4
        )
    )


def half_thickness(wl: float, x: float) -> float:
    c, le = chord(wl), le_fs(wl)
    u = np.clip((x - le) / c, 0.0, 1.0)
    return float(_half(np.asarray(u), c))


def _grid(wl: float, xa: float, xb: float, n: int = FITTED_SECTION_N) -> np.ndarray:
    """The cosine-spaced FS grid every section between xa and xb uses (denser at both ends), so a ply and its core share their points."""
    t = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    return xa + (xb - xa) * t


def section_poly(
    wl: float,
    xa: float | None = None,
    xb: float | None = None,
    n: int = FITTED_SECTION_N,
) -> list[tuple[float, float, float]]:
    """Closed fin section at a waterline between FS xa and xb: the +y (outboard) surface fore to aft, then the -y surface aft to fore."""
    le, c = le_fs(wl), chord(wl)
    xa = le if xa is None else xa
    xb = te_fs(wl) if xb is None else xb
    xs = _grid(wl, xa, xb, n)
    us = (xs - le) / c
    h = _half(us, c)
    yc, z = y_centre(wl), z_of_wl(wl)
    pts = [(float(x), yc + float(hh), z) for x, hh in zip(xs, h)] + [
        (float(x), yc - float(hh), z) for x, hh in zip(xs[::-1], h[::-1])
    ]
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 1e-6:
            out.append(p)
    if math.dist(out[0], out[-1]) < 1e-6:
        out.pop()
    return out


def _fin(wl0: float, wl1: float, xa_fn, xb_fn) -> cq.Solid:
    return wb._loft(
        section_poly(wl0, xa_fn(wl0), xb_fn(wl0)),
        section_poly(wl1, xa_fn(wl1), xb_fn(wl1)),
    )


def _hinge(_wl: float) -> float:
    return HINGE_FS


def upper_core() -> cq.Workplane:
    """Upper fin foam, WL 18.4 to 65.4: forward of the rudder hinge line up to the rudder top (WL 28.9), the full chord above."""
    a = _fin(ROOT_WL, RUDDER_TOP_WL, le_fs, _hinge)
    b = _fin(RUDDER_TOP_WL, TOP_WL, le_fs, te_fs)
    return wb._compound([a, b])


def tip_cap() -> cq.Workplane:
    """The 1 in urethane cap, WL 65.4 to 66.4, tapering to a fraction of the top section; a fitted shape."""
    top = section_poly(TOP_WL)
    cx = sum(p[0] for p in top) / len(top)
    cy = sum(p[1] for p in top) / len(top)
    z1 = z_of_wl(TOP_WL + G.winglet_book_cap_in)
    sm = [
        (cx + (p[0] - cx) * FITTED_CAP_SHRINK, cy + (p[1] - cy) * FITTED_CAP_SHRINK, z1)
        for p in top
    ]
    return wb._solid(wb._loft(top, sm))


def lower_fin() -> cq.Workplane:
    """Lower fin foam, WL 9.8 to 18.4: forward of the rudder hinge between WL 14.4 and 18.4, the full chord below WL 14.4; outline fitted."""
    a = _fin(RUDDER_BOT_WL, ROOT_WL, le_fs, _hinge)
    b = _fin(BOTTOM_WL, RUDDER_BOT_WL, le_fs, te_fs)
    return wb._compound([a, b])


def rudder() -> cq.Workplane:
    """The rudder: aft of the hinge line from WL 14.4 to 28.9 (4 in below and 10.5 above WL 18.4); 10 in wide at WL 18.4, 12.14 at the top, 11.5 at the bottom."""
    a = _fin(ROOT_WL, RUDDER_TOP_WL, _hinge, te_fs)
    b = _fin(RUDDER_BOT_WL, ROOT_WL, _hinge, te_fs)
    return wb._compound([b, a])


def rudder_axis() -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """The hinge axis, bottom to top: the vertical hinge line FS 176.8 on the leaning centre plane, WL 14.4 to 28.9."""
    return (
        (HINGE_FS, y_centre(RUDDER_BOT_WL), z_of_wl(RUDDER_BOT_WL)),
        (HINGE_FS, y_centre(RUDDER_TOP_WL), z_of_wl(RUDDER_TOP_WL)),
    )


def rudder_pose(shape: cq.Workplane, deg: float) -> cq.Workplane:
    """Rotate a rudder-attached solid about the hinge axis; positive swings the trailing edge outboard (+y), at most 30 deg either way (p139)."""
    if abs(deg) > MAX_RUDDER_DEG:
        raise ValueError(f"rudder deflection {deg} outside +/-{MAX_RUDDER_DEG}")
    if deg == 0.0:
        return shape
    a, b = rudder_axis()
    return shape.rotate(a, b, deg)


def _hinge_line(
    side: int,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """The 7.5 in piano hinge from WL 18.4 up, on the outboard (side +1) or inboard (-1) face at the hinge line."""
    pts = []
    for wl in (ROOT_WL, ROOT_WL + G.winglet_book_hinge_length_in):
        pts.append(
            (
                HINGE_FS,
                y_centre(wl) + side * (half_thickness(wl, HINGE_FS) + FITTED_HINGE_R),
                z_of_wl(wl),
            )
        )
    return pts[0], pts[1]


def rudder_hinge() -> cq.Workplane:
    """Piano hinge pin, 7.5 in from WL 18.4 up (p138) on the outboard edge; stands off the skin by its radius."""
    a, b = _hinge_line(+1)
    return wb._solid(wb._cyl(a, b, FITTED_HINGE_R))


def belhorn() -> cq.Workplane:
    """CS301 belhorn plate on the rudder's outboard side, centred at WL 18.7 (p139); turns with the rudder. Outline fitted (full-size pattern only)."""
    ln, th, ht = FITTED_BELHORN
    wl = FITTED_BELHORN_WL
    x0 = HINGE_FS + 0.6
    y = (
        y_centre(wl)
        + max(half_thickness(wl, x0 + f * ln) for f in np.linspace(0, 1, 6))
        + 0.08
    )
    z = z_of_wl(wl)
    return wb._solid(wb._box(x0, x0 + ln, y, y + th, z - ht / 2, z + ht / 2))


# display plies -------------------------------------------------------------------------------------------------------------------------
def _strip(
    side: int, k: int, wl0: float, wl1: float, xa: float | None, xb: float | None
) -> cq.Solid:
    """A thin ply on the +y (side 1) or -y (side -1) face, ply k stacked outward, between two waterlines and FS xa..xb (None = the LE or TE there)."""

    def sec(wl):
        a = le_fs(wl) if xa is None else xa
        b = te_fs(wl) if xb is None else xb
        xs = _grid(wl, a, b)
        yc = y_centre(wl)
        z = z_of_wl(wl)
        o0 = FITTED_PLY_GAP + (k - 1) * FITTED_PLY_T
        o1 = FITTED_PLY_GAP + k * FITTED_PLY_T
        s0 = [
            (float(x), yc + side * (half_thickness(wl, float(x)) + o0), z) for x in xs
        ]
        s1 = [
            (float(x), yc + side * (half_thickness(wl, float(x)) + o1), z) for x in xs
        ][::-1]
        return s0 + s1

    return wb._loft(sec(wl0), sec(wl1))


def skin_ply(side: int, k: int) -> cq.Workplane:
    """Skin ply k (1, 2: UND; 3: the BID patch, outboard only, 18 in up from the root, 14 in wide from the LE) of the upper fin."""
    if k == 3:
        up, wide = G.winglet_book_bid_patch_in
        return wb._solid(
            _strip(side, 3, ROOT_WL, ROOT_WL + up, None, le_fs(ROOT_WL) + wide)
        )
    return wb._solid(_strip(side, k, ROOT_WL, TOP_WL, None, None))


def layup_ply(k: int) -> cq.Workplane:
    """Corner layup 3 UND ply k (1..7) as two legs: A in over the wing tip top (inboard of BL 157) and B in up the fin's inboard face, thin strips; the
    table lengths are printed (p138), the strips' chordwise extent is fitted."""
    a_in, b_in = G.winglet_book_und_table_in[k - 1]
    x0, x1 = FITTED_LEG_X
    bl1 = G.wing_book_rib_bl[3]
    bl0 = bl1 - a_in
    t0, t1 = (k - 1) * FITTED_PLY_T, k * FITTED_PLY_T

    def wing_leg(bl):
        za, zb = wb.z_surface(bl, x0, +1), wb.z_surface(bl, x1, +1)
        return [
            (x0, bl, za + t0),
            (x1, bl, zb + t0),
            (x1, bl, zb + t1),
            (x0, bl, za + t1),
        ]

    leg_a = wb._loft(wing_leg(bl0), wing_leg(bl1))
    leg_b = _strip(-1, k, ROOT_WL, ROOT_WL + b_in, x0, x1)
    return wb._compound([leg_a, leg_b])


def block_a() -> cq.Workplane:
    """Block A: the 2 lb urethane corner block between the wing trailing edge and the winglet, a wedge in plan; size fitted (no dimensions printed)."""
    ln, wd, ht = FITTED_BLOCK_A
    x0 = G.wing_book_te_fs[2]
    y1 = G.wing_book_rib_bl[3]
    pts = [
        cq.Vector(x0, y1, 0.5),
        cq.Vector(x0 + ln, y1, 0.5),
        cq.Vector(x0, y1 - wd, 0.5),
    ]
    face = cq.Face.makeFromWires(cq.Wire.makePolygon(pts + [pts[0]]))
    return wb._solid(cq.Solid.extrudeLinear(face, cq.Vector(0, 0, ht)))


# jig lines (derived) -------------------------------------------------------------------------------------------------------------------
def abc_closure() -> dict[str, float]:
    """The A, B and C jig lengths the model geometry gives from the reference point, with the lean that closes C, against the printed values (p136, CP25 LPC 6)."""
    wprp_fs, wprp_bl = G.winglet_book_jig_wprp
    lateral = G.wing_book_rib_bl[3] - wprp_bl
    a = math.hypot(lateral, G.winglet_book_root_le_fs_wing_top - wprp_fs)
    b = math.hypot(lateral, G.winglet_book_root_te_fs - wprp_fs)
    lean = G.winglet_cant_in
    c = math.sqrt(
        (lateral - lean) ** 2
        + (G.winglet_book_top_te_fs - wprp_fs) ** 2
        + G.winglet_height_book_in**2
    )
    pa, pb, pc = G.winglet_book_jig_abc_in
    return {"A": a, "B": b, "C": c, "dA": a - pa, "dB": b - pb, "dC": c - pc}


def jig_points() -> dict[str, tuple[float, float, float]]:
    """WPRP and the three jig targets: the LE mark on the wing top (FS 160.5), the root TE (FS 186.8) and the tip TE (FS 196.6), at BL 157 and the leaned tip."""
    wprp_fs, wprp_bl = G.winglet_book_jig_wprp
    z0 = z_of_wl(ROOT_WL)
    bl = G.wing_book_rib_bl[3]
    return {
        "wprp": (wprp_fs, wprp_bl, z0),
        "a": (G.winglet_book_root_le_fs_wing_top, bl, z0),
        "b": (G.winglet_book_root_te_fs, bl, z0),
        "c": (
            G.winglet_book_top_te_fs,
            bl - G.winglet_cant_in,
            z_of_wl(ROOT_WL + G.winglet_height_book_in),
        ),
    }


def jig_lines() -> cq.Workplane:
    """Workshop dimension lines A, B and C from the reference point, thin rods, plus the reference peg."""
    p = jig_points()
    out = [wb._cyl(p["wprp"], p[k], FITTED_JIG_ROD_R) for k in ("a", "b", "c")]
    w = p["wprp"]
    out.append(wb._cyl(w, (w[0], w[1], w[2] + 1.0), FITTED_PEG_R))
    return wb._compound(out)


# ---- assembly ------------------------------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "winglet.cores": ("upper_core",),
    "winglet.skins": ("tip_cap",),
    "winglet.jig": ("jig_lines",),
    "winglet.layups": ("layup_3",),
    "winglet.block_a": ("block_a",),
    "winglet.lower_fin": ("lower_fin",),
    "winglet.rudder": ("rudder", "belhorn"),
    "winglet.rudder_hinge": ("rudder_hinge",),
}
RUDDER_ATTACHED = frozenset({"rudder", "belhorn"})
WORKSHOP_PARTS = frozenset({"jig_lines"})


@lru_cache(maxsize=1)
def _plies() -> dict[str, list[cq.Workplane]]:
    return {
        "skin_out": [skin_ply(+1, k) for k in (1, 2, 3)],
        "skin_in": [skin_ply(-1, k) for k in (1, 2)],
        "layup_3": [layup_ply(k) for k in range(1, 8)],
    }


def plies() -> dict[str, list[cq.Workplane]]:
    """Display plies: skin_out (UND, UND, BID patch), skin_in (UND, UND), layup_3 (seven UND corner plies, two legs each)."""
    return dict(_plies())


@lru_cache(maxsize=1)
def _right() -> dict[str, FusePart]:
    rep, der = "representational", "derived"
    note = "fitted symmetric section (14 per cent); the airfoils are on A-sheets the owner does not hold"
    ply = _plies()
    return {
        "upper_core": FusePart(
            "upper_core",
            upper_core(),
            rep,
            (_P135, _P136),
            f"upper fin foam WL 18.4 to 65.4, LE from FS 159.7 to the derived 185.2, TE FS 186.8 to 196.6 (printed), forward of the rudder hinge FS 176.8 below WL 28.9; the 11.4 in tip chord is a derived-medium read; {note}; leaning inward about 3.6 in (derived, low)",
        ),
        "tip_cap": FusePart(
            "tip_cap",
            tip_cap(),
            rep,
            (_P135, _P136),
            "1 in urethane tip cap, WL 65.4 to 66.4 (printed), tapering; shape fitted",
        ),
        "jig_lines": FusePart(
            "jig_lines",
            jig_lines(),
            der,
            (_P136,),
            "dimension lines A 102.15, B 108.35 and C 118.35 in from the reference point BL 55.5, FS 149.6 (printed, CP25 LPC 6), drawn to the model's own targets: A and B close within 0.1 and 0.25 in, C only with the derived lean; the peg is fitted; workshop geometry",
        ),
        "layup_3": FusePart(
            "layup_3",
            wb._compound([w.val() for w in ply["layup_3"]]),
            rep,
            (_P138,),
            "corner layup 3 UND plies, A in over the wing tip and B in up the fin (24/12 down to 12/6, printed); chordwise extent fitted; layup 4 is the same on the other side and is not drawn",
        ),
        "block_a": FusePart(
            "block_a",
            block_a(),
            rep,
            (_P137, _P138),
            "block A, 2 lb urethane in two 2 in pieces (printed), carved to a flat diagonal; plan and height fitted (no dimensions printed)",
        ),
        "lower_fin": FusePart(
            "lower_fin",
            lower_fin(),
            rep,
            (_P135, _P138),
            "lower fin foam WL 9.8 (printed) to 18.4; the outline is fitted to give the printed 11.5 in rudder width at its bottom (TE bottom FS about 190, LE bottom FS 178 from the 12 in dimension)",
        ),
        "rudder": FusePart(
            "rudder",
            rudder(),
            rep,
            (_P135, _P138),
            f"rudder aft of the hinge FS 176.8, WL 14.4 to 28.9, 10 in wide at WL 18.4, 12.14 at the top, 11.5 at the bottom, 14.5 tall (printed); {note}",
        ),
        "belhorn": FusePart(
            "belhorn",
            belhorn(),
            rep,
            (_P139,),
            "CS301 belhorn on the rudder outboard side at WL 18.7 (printed); 0.040 in 4130N printed, outline and size fitted (full-size pattern only); turns with the rudder",
        ),
        "rudder_hinge": FusePart(
            "rudder_hinge",
            rudder_hinge(),
            rep,
            (_P138, _P139),
            "piano hinge 7.5 in from WL 18.4 up on the outboard edge (printed); radius fitted",
        ),
    }


def build_winglet(side: str = "right", rudder_deg: float = 0.0) -> dict[str, FusePart]:
    """All chapter 20 solids of one winglet; the rudder-attached ones turned about the hinge axis by ``rudder_deg`` (positive TE outboard)."""
    if side not in ("right", "left"):
        raise ValueError(side)
    out = {}
    for n, p in _right().items():
        s = p.solid
        if n in RUDDER_ATTACHED:
            s = rudder_pose(s, rudder_deg)
        if side == "left":
            s = cq.Workplane("XY").add(s.val().mirror("XZ"))
        out[n] = FusePart(n, s, p.fidelity, p.cite, p.note)
    return out


def build_plies(side: str = "right") -> dict[str, list[cq.Workplane]]:
    p = plies()
    if side == "right":
        return p
    return {
        k: [cq.Workplane("XY").add(w.val().mirror("XZ")) for w in v]
        for k, v in p.items()
    }
