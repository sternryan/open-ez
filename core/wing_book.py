"""Wings (plans chapter 19, pdf pages p118 to p134): cores, shear web, spar caps, skins, hard points, aileron, hardware, jigs.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl`` (model z 0 = W.L. 17.4, the chord-line plane
of p126). ``build_wing("right")`` and ``build_wing("left")`` return the two wings; the left is the mirror of the right (p126, p127).

Printed (config ``wing_*`` fields, ``GEOMETRY_PROVENANCE``): the rib stations BL 23, 55.5, 106.25 and 157, the LE, TE and shear web lines, chords,
thickness, twist, the aileron cuts and ends, the cap and web ply schedules, the hardware counts. NOT printed: the airfoil ordinates (the Eppler 1230
modified file in ``data/airfoils`` is scaled to the printed thickness, which is about double its own 8.7 per cent), the jig outlines, the core and aileron
templates, the rib and bracket shapes. So every solid is ``representational`` except the hardware whose size and station are printed (``derived``).

Section model: every section is the file's unit airfoil scaled by the local chord and thickness, scaled in thickness about its camber line and sheared so its TE sits ``chord * tan(washout)`` above the
LE (the book's TE heights WL 16.95 and 18.35 come out of this, see ``te_wl``). The LE is flat at z = 0. Inboard of BL 55.5 the LE line is the model's
straight 22.98 deg extension (the strake, chapter 21, owns the real LE there); only the part aft of the shear web is drawn.

Cores are ruled lofts of polygon sections, split at the shear web (FC4 and FC5 forward, FC1 to FC3 aft) and at the aileron hinge line, so no boolean is
needed between near-coincident surfaces. The shear web plies, the spar cap plies and the skin plies are display plies (``plies``), stacked outward from the
core surface at a visual thickness; they are not part of the non-overlap set.
"""

from __future__ import annotations

import math
from functools import lru_cache
from itertools import pairwise
from pathlib import Path

import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator

from .fuselage_book import FusePart, G, z_of_wl

_P118, _P119, _P120, _P121, _P122, _P123, _P124, _P125, _P126, _P127 = (
    f"plans-1980:p{n}" for n in range(118, 128)
)
_P128, _P129, _P130, _P131, _P132, _P133, _P134 = (
    f"plans-1980:p{n}" for n in range(128, 135)
)
_P88 = "plans-1980:p88"

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_SECTION_N = 22  # fitted, not book: points per surface of every section polygon
FITTED_PLY_GAP = 0.02  # fitted, not book: the first display ply floats this far off the core surface (the surface model and the ruled cores differ by hundredths)
FITTED_ACROSS_N = 7  # fitted, not book: points across a cap strip or a hinge leaf, so the strip follows the surface curve
FITTED_PLY_T = (
    G.spar_ply_thickness_laid_in
)  # book p85 laid ply 0.0375, used as the drawn thickness of every ply here
FITTED_RIB_T = 0.7  # book: p124, p129 root rib 0.7 deep (CP25 LPC 8); drawn as its own slab at the root end of FC1
FITTED_JIG_T = 0.5  # fitted, not book: jig plywood thickness (cobelu only; page 19-1 is not on the scan)
FITTED_JIG_MARGIN = 4.0  # fitted, not book: jig board margin round the section
FITTED_JIG_HOLE = 0.3  # fitted, not book: the section hole is the airfoil offset outward by this (clearance for the aileron TE and hardware)
FITTED_HINGE_PIN_R = 0.1  # fitted, not book: hinge pin radius
FITTED_HINGE_LEAF_T = 0.06  # fitted, not book: hinge leaf thickness
FITTED_HINGE_LEAF_W = 0.9  # fitted, not book: hinge leaf width (flange 1.8 across the pin line in the plans, drawn as the aileron leaf only)
FITTED_ROD_R = 3 / 16  # book: p133 A13 3/8 in steel rod
FITTED_CONDUIT_LIFT = 0.45  # fitted, not book: the conduit is drawn this far above the top surface, clear of the hinge pins and leaves (really it lies under the skin in a groove)
FITTED_GROOVE_OVER = 0.01  # fitted, not book: grooves and slots are cut this much wider than the rod or tube they hold
FITTED_ROD_END_GAP = 0.1  # fitted, not book: the rod stops this far short of each aileron end (its slanted end face clears the neighbouring cores)
FITTED_ROD_OFFSET = 0.55  # fitted, not book: rod axis this far aft of the hinge line in the aileron nose
FITTED_TUBE_R = 3 / 8  # book: p133 A10 3/4 in OD tube
FITTED_TUBE_OFFSET = (
    1.5  # fitted, not book: tube axis this far aft of the hinge line (clear of the rod)
)
FITTED_CLEAR = 0.05  # fitted, not book: stand-off of the pins, leaves, conduit and board above the modelled top surface
FITTED_HINGE_BL = (
    (56.3, 64.3),
    (80.0, 86.0),
    (110.1, 116.1),
)  # fitted, not book: A3 (8 in) and the two A4 (6 in) spans; the plans print the spacing in cramped digits
FITTED_BAY_X = (
    138.0,
    150.0,
)  # fitted, not book: root bay void in FC1 (FS), where the belhorn, CS127 and CS128 sit
FITTED_BAY_BL = (24.5, 34.0)  # fitted, not book: root bay void in FC1 (BL)
FITTED_BOARD = (
    24.0,
    3.5,
    0.75,
)  # fitted, not book: incidence board (along BL, along FS, thick); 2 ft long (p124)
FITTED_BOARD_FS = 143.0  # fitted, not book: board centre FS on the inboard top skin
FITTED_BOARD_BL0 = 28.0  # fitted, not book: board inboard end BL
FITTED_LWA4_YZ = (
    1.5,
    2.0,
)  # fitted, not book: LWA4 plate across (CP43 LPC 119 resizes it to 1.75 in chapter 14)
FITTED_LWA6_YZ = (2.3, 2.0)  # book: p133 LWA6 2.3 by 2 in
FITTED_LWA_T = 0.25  # book: p133 LWA6 1/4 in 2024-T3 (LWA4 taken the same)
FITTED_PLATE_T = 0.125  # book: p133 LWA7 1/8 in
FITTED_BOLT_R = 0.25  # book: p134 AN8 is 1/2 in
FITTED_CONTROLS_T = 0.125  # book: p131 CS128 belcrank 0.125 in; the other pieces are drawn at the same thickness
_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "airfoils" / "eppler_1230_mod.dat"
)

STN = G.wing_book_rib_bl  # (23, 55.5, 106.25, 157)
WEB_GAP = (
    6 * FITTED_PLY_T
)  # the shear web at its thickest (6 plies) sits between the forward and aft cores
_SWEEP_TAN = math.tan(math.radians(G.wing_sweep_le))
_WEB_COS = math.cos(math.radians(G.wing_book_shear_web_sweep_deg))
AILERON_BL = (
    G.wing_aileron_inboard_bl,
    G.wing_aileron_outboard_bl,
)  # 55.5 (p124), 118.1
FIDELITIES_USED = frozenset({"representational", "derived"})
MAX_UP_DEG = G.wing_aileron_max_up_deg


# ---- planform lines (all from config) ------------------------------------------------------------------------------------------------
def _pl(bl: float, xs, ys) -> float:
    return float(np.interp(bl, xs, ys))


def le_fs(bl: float) -> float:
    """Leading edge FS: the p126 straight line outboard of BL 55.5, its 22.98 deg extension (a model construct) inboard."""
    if bl >= STN[1]:
        return _pl(
            bl,
            (STN[1], STN[2], STN[3]),
            (
                G.wing_book_le_fs_bl_55_5,
                G.wing_le_fs_bl_106_25_derived,
                G.wing_book_le_fs_tip,
            ),
        )
    return G.wing_book_le_fs_bl_55_5 - (STN[1] - bl) * _SWEEP_TAN


def te_fs(bl: float) -> float:
    """Trailing edge FS: the 12.49 deg kink inboard of BL 55.5, the 11.36 deg line outboard (p126)."""
    return _pl(
        bl,
        STN,
        (G.wing_book_te_fs_bl_23, *G.wing_book_te_fs),
    )


def web_fs(bl: float) -> float:
    """Shear web forward face (the foam edge) FS (p126)."""
    return _pl(bl, STN, G.wing_book_shear_web_fwd_fs)


def chord(bl: float) -> float:
    return te_fs(bl) - le_fs(bl)


def tc(bl: float) -> float:
    """Thickness / chord; held at the BL 55.5 value inboard of it (not printed there)."""
    return _pl(bl, STN[1:], [t / 100 for t in G.wing_book_thickness_pct])


def washout_deg(bl: float) -> float:
    """Washout (TE up) in degrees, the printed 0.6 washin as -0.6; held inboard of BL 55.5 (not printed there)."""
    return _pl(bl, STN[1:], G.wing_book_washout_deg)


def hinge_fs(bl: float) -> float:
    """Aileron hinge line (top-skin cut) FS, straight through the p124 cuts at BL 55.5 and 106.25, carried out to BL 118.1."""
    h0, h1 = G.wing_aileron_hinge_fs
    return h0 + (bl - STN[1]) * (h1 - h0) / (STN[2] - STN[1])


# ---- section model --------------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _unit():
    pts = np.loadtxt(_FILE, skiprows=1)
    i = int(np.argmin(pts[:, 0]))
    x0, y0 = pts[
        i
    ]  # the nose point (the file's nose is 0.0055 aft of x = 0): the unit section starts there so its two surfaces meet at one point
    ux = (pts[:, 0] - x0) / (1.0 - x0)
    pts = np.column_stack(
        [ux, (pts[:, 1] - y0) / (1.0 - x0) - ux * (pts[-1, 1] - y0) / (1.0 - x0)]
    )  # nose to TE is the chord line
    up = pts[: i + 1][::-1]
    lo = pts[i:]
    yu = PchipInterpolator(up[:, 0], up[:, 1])
    yl = PchipInterpolator(lo[:, 0], lo[:, 1])
    u = np.linspace(0, 1, 401)
    tmax = float(np.max(yu(u) - yl(u)))
    return yu, yl, tmax


def unit_thickness() -> float:
    """The airfoil file's own maximum thickness / chord (about 0.087); the build scales it to the printed value."""
    return _unit()[2]


def z_surface(bl: float, x: float, side: int) -> float:
    """Model z of the upper (+1) or lower (-1) surface at (FS x, BL bl): the file's unit section scaled and sheared by the washout."""
    yu, yl, tmax = _unit()
    le, c = le_fs(bl), chord(bl)
    u = min(max((x - le) / c, 0.0), 1.0)
    a, b = float(yu(u)), float(yl(u))
    # the file's thickness is scaled to the printed value about its own camber line (scaling about the chord line would leave it flat-bottomed)
    y = (0.5 * (a + b) + side * 0.5 * (a - b) * (tc(bl) / tmax)) * c
    return y + (x - le) * math.tan(math.radians(washout_deg(bl)))


def te_wl(bl: float) -> float:
    """TE height as a waterline: the chord line at WL 17.4 plus the TE rise from the washout (the p126 WL 16.95 and 18.35 check)."""
    return G.wing_book_chord_line_wl + z_surface(bl, te_fs(bl), +1)


def section_surface(
    bl: float, xa: float | None, xb: float | None, side: int, n: int = FITTED_SECTION_N
) -> list[tuple[float, float, float]]:
    """The upper (+1) or lower (-1) surface points (x, y = bl, z) between FS xa and xb on the cosine-spaced grid every core section uses."""
    le, c = le_fs(bl), chord(bl)
    xa = le if xa is None else xa
    xb = te_fs(bl) if xb is None else xb
    ua, ub = (xa - le) / c, (xb - le) / c
    t = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    xs = le + (ua + (ub - ua) * t) * c
    return [(float(x), bl, z_surface(bl, float(x), side)) for x in xs]


def section_poly(
    bl: float,
    xa: float | None = None,
    xb: float | None = None,
    n: int = FITTED_SECTION_N,
) -> list[tuple[float, float, float]]:
    """Closed section polygon (x, y = bl, z) between FS xa and xb (default the whole chord): upper surface fore to aft, then lower aft to fore."""
    pts = section_surface(bl, xa, xb, +1, n) + section_surface(bl, xa, xb, -1, n)[::-1]
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 1e-6:
            out.append(p)
    if math.dist(out[0], out[-1]) < 1e-6:
        out.pop()
    return out


def _wire(pts) -> cq.Wire:
    v = [cq.Vector(*p) for p in pts]
    return cq.Wire.makePolygon(v + [v[0]])


def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _loft(section_a, section_b) -> cq.Solid:
    s = cq.Solid.makeLoft([_wire(section_a), _wire(section_b)], True)
    if s.Volume() < 0:
        s = cq.Solid.makeLoft([_wire(section_a[::-1]), _wire(section_b[::-1])], True)
    return s


def _core(bl0: float, bl1: float, xa_fn, xb_fn) -> cq.Solid:
    """Ruled loft between the sections at bl0 and bl1, each clipped to FS [xa_fn(bl), xb_fn(bl)] (None = the LE or TE)."""
    return _loft(
        section_poly(bl0, xa_fn(bl0), xb_fn(bl0)),
        section_poly(bl1, xa_fn(bl1), xb_fn(bl1)),
    )


def _compound(solids) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound(list(solids)))


def _web_aft(bl: float) -> float:
    return web_fs(bl) + WEB_GAP


# ---- the solids (right wing) ---------------------------------------------------------------------------------------------------------
def fc1() -> cq.Workplane:
    """Inboard core, BL 23.7 to 55.5, aft of the shear web only (forward of it, inboard of BL 55.5, is the strake, chapter 21); the first 0.7 in is the root rib."""
    s = _core(STN[0] + FITTED_RIB_T, STN[1], _web_aft, te_fs)
    return _solid(s)


def root_rib() -> cq.Workplane:
    return _solid(_core(STN[0], STN[0] + FITTED_RIB_T, _web_aft, te_fs))


def fc2() -> cq.Workplane:
    """Centre aft core, BL 55.5 to 106.25, between the shear web and the aileron hinge line."""
    return _solid(_core(STN[1], STN[2], _web_aft, hinge_fs))


def fc3() -> cq.Workplane:
    """Outboard aft core, BL 106.25 to 157: the aileron cut-out to BL 118.1 (hinge line), then the full chord to the tip."""
    a = _core(STN[2], AILERON_BL[1], _web_aft, hinge_fs)
    b = _core(AILERON_BL[1], STN[3], _web_aft, te_fs)
    return _compound([a, b])


FC4_BL0 = 56.75  # fitted, not book: FC4 starts here, just outboard of the spar's end bulkhead (BL 56.7; the spar tip is BL 56.46, p88, 0.96 in outboard of the p126 joint at BL 55.5)


def fc4() -> cq.Workplane:
    """Centre leading-edge core, BL 56.75 (outboard of the spar tip, p88; the p126 joint is BL 55.5) to 106.25, from the LE to the shear web."""
    return _solid(_core(FC4_BL0, STN[2], le_fs, web_fs))


def fc5() -> cq.Workplane:
    return _solid(_core(STN[2], STN[3], le_fs, web_fs))


def aileron_solid() -> cq.Workplane:
    """The aileron foam: BL 55.5 to 118.1 aft of the top hinge line (a vertical cut, CP34 LPC 107); the bottom skin cut 1.7 in farther aft is not drawn."""
    return _solid(_core(AILERON_BL[0], AILERON_BL[1], hinge_fs, te_fs))


def _along_hinge(bl: float, off: float) -> tuple[float, float]:
    """(FS, z) of a point ``off`` aft of the hinge line at bl, on the mid-thickness of the aileron section there."""
    x = hinge_fs(bl) + off
    return x, 0.5 * (z_surface(bl, x, +1) + z_surface(bl, x, -1))


def _hinge_dir() -> tuple[float, float]:
    """Unit direction of the hinge line in plan (dFS, dBL)."""
    d = (hinge_fs(AILERON_BL[1]) - hinge_fs(AILERON_BL[0])) / (
        AILERON_BL[1] - AILERON_BL[0]
    )
    n = math.hypot(d, 1.0)
    return d / n, 1.0 / n


def _cyl(p0, p1, r: float) -> cq.Solid:
    a, b = cq.Vector(*p0), cq.Vector(*p1)
    return cq.Solid.makeCylinder(r, (b - a).Length, a, (b - a))


def _line_cyl(bl0: float, bl1: float, off: float, r: float) -> cq.Solid:
    x0, z0 = _along_hinge(bl0, off)
    x1, z1 = _along_hinge(bl1, off)
    return _cyl((x0, bl0, z0), (x1, bl1, z1), r)


def _tube_span() -> tuple[float, float]:
    """The 9 in tube starts 1 in inboard of the aileron (into the torque-tube slot of FC1) and runs outboard."""
    d = _hinge_dir()[1]
    b0 = AILERON_BL[0] - 1.0 * d
    return b0, b0 + G.wing_aileron_torque_tube_length_in * d


def aileron() -> cq.Workplane:
    """The aileron foam with the rod groove and the torque-tube groove cut so the hardware lies in it."""
    s = aileron_solid().val()
    s = s.cut(
        _line_cyl(
            AILERON_BL[0] + FITTED_ROD_END_GAP,
            AILERON_BL[1] - FITTED_ROD_END_GAP,
            FITTED_ROD_OFFSET,
            FITTED_ROD_R + FITTED_GROOVE_OVER,
        )
    )
    b0, b1 = _tube_span()
    s = s.cut(_line_cyl(b0, b1, FITTED_TUBE_OFFSET, FITTED_TUBE_R + FITTED_GROOVE_OVER))
    return _solid(s)


def aileron_rod() -> cq.Workplane:
    """A13, 3/8 steel rod along the hinge line in the aileron nose, BL 55.5 to 118.1: 63.9 in, trimmed from the printed 65 (the plans butt shorter pieces; 1.1 in over the aileron)."""
    return _solid(
        _line_cyl(
            AILERON_BL[0] + FITTED_ROD_END_GAP,
            AILERON_BL[1] - FITTED_ROD_END_GAP,
            FITTED_ROD_OFFSET,
            FITTED_ROD_R,
        )
    )


def torque_tube() -> cq.Workplane:
    """A10, 3/4 x .058 tube, 9 in, its inboard 1 in sticking out of the aileron into the FC1 slot."""
    b0, b1 = _tube_span()
    return _solid(_line_cyl(b0, b1, FITTED_TUBE_OFFSET, FITTED_TUBE_R))


def _hinge_span_solids(leaf: bool) -> list[cq.Solid]:
    out = []
    for b0, b1 in FITTED_HINGE_BL:
        x0, x1 = hinge_fs(b0), hinge_fs(b1)
        z0 = z_surface(b0, x0, +1)
        z1 = z_surface(b1, x1, +1)
        if (
            not leaf
        ):  # the pin lies on the hinge line just above the top skin, on the wing side
            out.append(
                _cyl(
                    (x0, b0, z0 + FITTED_CLEAR + FITTED_HINGE_PIN_R),
                    (x1, b1, z1 + FITTED_CLEAR + FITTED_HINGE_PIN_R),
                    FITTED_HINGE_PIN_R,
                )
            )
        else:  # the aileron leaf: a thin plate from the pin aft, over the aileron top skin
            w = FITTED_HINGE_LEAF_W

            def leaf_sec(bl, x, w=w):
                xs = np.linspace(x, x + w, FITTED_ACROSS_N)
                t = FITTED_HINGE_LEAF_T
                s0 = [
                    (float(xx), bl, z_surface(bl, float(xx), +1) + FITTED_CLEAR)
                    for xx in xs
                ]
                s1 = [
                    (float(xx), bl, z_surface(bl, float(xx), +1) + FITTED_CLEAR + t)
                    for xx in xs
                ][::-1]
                return s0 + s1

            out.append(
                _loft(
                    leaf_sec(b0, x0 + FITTED_HINGE_PIN_R),
                    leaf_sec(b1, x1 + FITTED_HINGE_PIN_R),
                )
            )  # the leaf starts at the pin's aft side
    return out


def hinge_pins() -> cq.Workplane:
    """The wing side of the three piano hinges (A3 8 in inboard, A4 6 in twice), a pin on the hinge line; lengths printed, stations fitted."""
    return _compound(_hinge_span_solids(False))


def hinge_leaves() -> cq.Workplane:
    """The aileron side of the three hinges: a leaf over the aileron's top skin; turns with the aileron."""
    return _compound(_hinge_span_solids(True))


# hard points and attach ----------------------------------------------------------------------------------------------------------------
def _hp_sites() -> list[tuple[str, float, float]]:
    """(name, BL, model z) of the three bolt sites from the spar's p88 hard-point stations: one inboard, two outboard."""
    z = z_of_wl
    return [
        ("lwa6", G.spar_hp_inboard_bl_in, z(G.spar_hp_inboard_wl_in)),
        ("lwa4a", G.spar_hp_outboard_bl_in, z(G.spar_hp_outboard_wl_in[0])),
        ("lwa4b", G.spar_hp_outboard_bl_in, z(G.spar_hp_outboard_wl_in[1])),
    ]


def _web_angle_deg(bl: float) -> float:
    """Plan angle of the shear web face at bl (8.57 deg inboard of BL 55.5, 18.4 deg outboard of it): the face the hard points are fixed to."""
    i = 0 if bl < STN[1] else (1 if bl < STN[2] else 2)
    dx = web_fs(STN[i + 1]) - web_fs(STN[i])
    return math.degrees(math.atan2(dx, STN[i + 1] - STN[i]))


def _pad(name: str, bl: float, z: float, x0: float, x1: float) -> cq.Solid:
    """A box on the shear web face at a hard-point site, from ``x0`` to ``x1`` behind the face (its sides parallel to the web line), centred on (bl, z)."""
    y, h = FITTED_LWA6_YZ if name == "lwa6" else FITTED_LWA4_YZ
    b = cq.Solid.makeBox(x1 - x0, y, h, cq.Vector(x0, -y / 2, -h / 2))
    b = b.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -_web_angle_deg(bl))
    return b.translate(cq.Vector(_web_aft(bl), bl, z))


def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def hardpoints() -> cq.Workplane:
    """LWA6 (inboard) and two LWA4 (outboard) 1/4 in plates in depressions on the FC1 forward face, each with a 1/8 in plate behind it (LWA2 and LWA3), set square to the web face."""
    out = []
    for name, bl, z in _hp_sites():
        out.append(_pad(name, bl, z, 0.0, FITTED_LWA_T))
        out.append(_pad(name, bl, z, FITTED_LWA_T, FITTED_LWA_T + FITTED_PLATE_T))
    return _compound(out)


def _bay_box() -> cq.Solid:
    return _box(
        FITTED_BAY_X[0], FITTED_BAY_X[1], FITTED_BAY_BL[0], FITTED_BAY_BL[1], -2.0, 2.0
    )


def fc1_cut() -> cq.Workplane:
    """FC1 with the three hard-point depressions, the torque-tube slot and the root bay cut out (the hollowed inboard wedge is not drawn)."""
    s = fc1().val()
    for name, bl, z in _hp_sites():
        s = s.cut(_pad(name, bl, z, -0.05, FITTED_LWA_T + FITTED_PLATE_T))
    b0, _b1 = _tube_span()
    s = s.cut(
        _line_cyl(
            b0, STN[1] + 1.0, FITTED_TUBE_OFFSET, FITTED_TUBE_R + FITTED_GROOVE_OVER
        )
    )  # past BL 55.5, where FC1 ends, so the slanted end face cuts nothing outside
    s = s.cut(_bay_box())
    return _solid(s)


def spar_bolts() -> cq.Workplane:
    """Two AN8-21A (outboard pair) and one AN8-23A (inboard) through the hard points along FS; lengths from the part numbers (2 1/8 and 2 3/8 in)."""
    out = []
    for name, bl, z in _hp_sites():
        ln = 2.375 if name == "lwa6" else 2.125
        x0 = web_fs(bl) + WEB_GAP - 0.3
        out.append(_cyl((x0, bl, z), (x0 + ln, bl, z), FITTED_BOLT_R))
    return _compound(out)


# controls in the root bay --------------------------------------------------------------------------------------------------------------
def controls() -> cq.Workplane:
    """Representational root-bay hardware inside the FC1 void: the CS132L belhorn (a 2.5 in arm), two CS127 brackets and the CS128 belcrank, as plates."""
    t = FITTED_CONTROLS_T
    x0 = FITTED_BAY_X[0]
    y0 = FITTED_BAY_BL[0]
    out = [
        _box(x0 + 1.0, x0 + 3.5, y0 + 0.5, y0 + 0.5 + t, -1.0, 0.5),  # belhorn arm
        _box(x0 + 1.0, x0 + 3.0, y0 + 2.0, y0 + 2.0 + t, -1.2, 1.2),  # CS127 left
        _box(x0 + 1.0, x0 + 3.0, y0 + 4.0, y0 + 4.0 + t, -1.2, 1.2),  # CS127 right
        _box(x0 + 5.0, x0 + 7.0, y0 + 3.0, y0 + 3.0 + t, -0.8, 0.8),  # CS128 belcrank
    ]
    return _compound(out)


def ribs() -> cq.Workplane:
    """The 0.7 in root rib slab and the 2 ft incidence board shimmed level on the inboard top skin."""
    bl0 = FITTED_BOARD_BL0
    ln, wd, th = FITTED_BOARD
    x0 = FITTED_BOARD_FS - wd / 2
    zmax = max(z_surface(b, x, +1) for b in (bl0, bl0 + ln) for x in (x0, x0 + wd))
    board = _box(
        x0,
        x0 + wd,
        bl0,
        bl0 + ln,
        zmax + FITTED_CLEAR + 0.15,
        zmax + FITTED_CLEAR + 0.15 + th,
    )
    return _compound([root_rib().val(), board])


# jigs ----------------------------------------------------------------------------------------------------------------------------------
def jig_stations() -> tuple[float, ...]:
    """BL of the five jigs: the printed floor spacings (0, 31.72, 51.72, 88.44, 125.59 from jig 1) spread over BL 23.7 to 157; their BL is not printed."""
    d = (0.0, 31.72, 51.72, 88.44, 125.59)
    b0 = STN[0] + FITTED_RIB_T
    return tuple(b0 + (STN[3] - b0) * x / d[-1] for x in d)


def jig(bl: float) -> cq.Solid:
    sec = section_poly(bl)
    xs = [p[0] for p in sec]
    zs = [p[2] for p in sec]
    m = FITTED_JIG_MARGIN
    rect = [
        (min(xs) - m, bl, min(zs) - m),
        (max(xs) + m, bl, min(zs) - m),
        (max(xs) + m, bl, max(zs) + m),
        (min(xs) - m, bl, max(zs) + m),
    ]
    hole = _wire(sec).offset2D(FITTED_JIG_HOLE, "intersection")[0]
    face = cq.Face.makeFromWires(_wire(rect), [hole])
    return cq.Solid.extrudeLinear(face, cq.Vector(0, FITTED_JIG_T, 0)).translate(
        cq.Vector(0, -FITTED_JIG_T / 2, 0)
    )


def jigs() -> cq.Workplane:
    return _compound([jig(b) for b in jig_stations()])


def _cuts(b0: float, b1: float) -> list[float]:
    """Loft break points for a display ply spanning b0..b1: the rib stations and the aileron end, so each piece is ruled between the same sections as the cores."""
    marks = (STN[0] + FITTED_RIB_T, STN[1], STN[2], AILERON_BL[1])
    return [b0, *[m for m in marks if b0 < m < b1], b1]


def _segments(b0: float, b1: float, section) -> cq.Workplane:
    cuts = _cuts(b0, b1)
    return _compound([_loft(section(p), section(q)) for p, q in pairwise(cuts)])


# display plies -------------------------------------------------------------------------------------------------------------------------
def web_ply_spans() -> list[tuple[float, float]]:
    """BL span of each of the six shear web plies: plies 1 and 2 full span, 3 and 4 from the inboard end to 39 in (along the web) from the tip, 5 and 6 to 91 in."""
    tip = STN[3]
    return [
        (STN[0], tip),
        (STN[0], tip),
        (STN[0], tip - 39.0 * _WEB_COS),
        (STN[0], tip - 39.0 * _WEB_COS),
        (STN[0], tip - 91.0 * _WEB_COS),
        (STN[0], tip - 91.0 * _WEB_COS),
    ]


def web_ply(k: int) -> cq.Workplane:
    """Ply k (1..6) of the shear web as a sheet in the web gap: aft of the forward face by (k - 1) ply thicknesses, spanning the airfoil there."""
    b0, b1 = web_ply_spans()[k - 1]

    def rect(bl):
        xa = web_fs(bl) + (k - 1) * FITTED_PLY_T
        xb = xa + FITTED_PLY_T
        return [
            (xa, bl, z_surface(bl, xa, -1)),
            (xb, bl, z_surface(bl, xb, -1)),
            (xb, bl, z_surface(bl, xb, +1)),
            (xa, bl, z_surface(bl, xa, +1)),
        ]

    return _segments(b0, b1, rect)


def cap_ply_spans(top: bool) -> list[tuple[float, float]]:
    """BL span of each cap ply: tape length and inboard offset are measured along the web line, so BL = 23 + s cos(web sweep). Plies stagger from the root end;
    the printed offsets are used as printed and ply 7 of the top cap carries the same 6 in step on."""
    lens = G.wing_cap_top_plies_in if top else G.wing_cap_bottom_plies_in
    offs = (
        (0.0, 0.0, *G.wing_cap_top_offsets_in, G.wing_cap_top_offsets_in[-1] + 6.0)
        if top
        else (0.0, *G.wing_cap_bottom_offsets_in)
    )
    out = []
    for ln, off in zip(lens, offs):
        b0 = STN[0] + off * _WEB_COS
        b1 = min(STN[3], b0 + ln * _WEB_COS)
        out.append((b0, b1))
    return out


def cap_ply(top: bool, k: int) -> cq.Workplane:
    """Ply k (1-based) of the top or bottom spar cap: a 3 in strip aft from the web forward face, stacked outward from the skin line."""
    b0, b1 = cap_ply_spans(top)[k - 1]
    w = G.wing_book_spar_cap_width_in
    side = 1 if top else -1

    def strip(bl):
        xs = np.linspace(web_fs(bl), web_fs(bl) + w, FITTED_ACROSS_N)
        o0, o1 = (
            side * (FITTED_PLY_GAP + (k - 1) * FITTED_PLY_T),
            side * (FITTED_PLY_GAP + k * FITTED_PLY_T),
        )
        s0 = [(float(x), bl, z_surface(bl, float(x), side) + o0) for x in xs]
        s1 = [(float(x), bl, z_surface(bl, float(x), side) + o1) for x in xs][::-1]
        return s0 + s1

    return _segments(b0, b1, strip)


def _skin_pieces():
    """(bl0, bl1, xa_fn, xb_fn): one piece per core (same FS range, so the same grid and the same ruled lines) plus the shear web gap between the leading-edge cores
    and the aft cores; the skin stops at the aileron hinge line over BL 55.5 to 118.1."""
    return [
        (STN[0] + FITTED_RIB_T, STN[1], _web_aft, te_fs),
        (FC4_BL0, STN[2], le_fs, web_fs),
        (STN[1], STN[2], web_fs, _web_aft),
        (STN[1], STN[2], _web_aft, hinge_fs),
        (STN[2], STN[3], le_fs, web_fs),
        (STN[2], STN[3], web_fs, _web_aft),
        (STN[2], AILERON_BL[1], _web_aft, hinge_fs),
        (AILERON_BL[1], STN[3], _web_aft, te_fs),
    ]


def skin_ply(top: bool, k: int) -> cq.Workplane:
    """Skin ply k of the top (3 UND) or bottom (2 UND + BID tip, drawn as 3) skin, stacked outward from the core surface, BL 23.7 to 157, in one piece per core."""
    side = 1 if top else -1
    o0 = side * (FITTED_PLY_GAP + (k - 1) * FITTED_PLY_T)
    o1 = side * (FITTED_PLY_GAP + k * FITTED_PLY_T)
    pieces = []
    for b0, b1, xa, xb in _skin_pieces():

        def strip(bl, xa=xa, xb=xb):
            surf = section_surface(bl, xa(bl), xb(bl), side)
            return [(x, y, z + o0) for x, y, z in surf] + [
                (x, y, z + o1) for x, y, z in surf
            ][::-1]

        pieces.append(_loft(strip(b0), strip(b1)))
    return _compound(pieces)


# ---- assembly ------------------------------------------------------------------------------------------------------------------------
COMPONENT_PARTS = {
    "wing.jigs": ("jigs",),
    "wing.cores": ("fc1", "fc2", "fc3", "fc4", "fc5"),
    "wing.hardpoints": ("hardpoints",),
    "wing.shear_web": ("shear_web",),
    "wing.spar_caps": ("cap_bottom", "cap_top"),
    "wing.skins": ("skin_bottom", "skin_top"),
    "wing.conduit": ("conduit",),
    "wing.ribs": ("ribs",),
    "wing.aileron": ("aileron",),
    "wing.aileron_hinges": ("hinge_pins", "hinge_leaves", "aileron_rod", "torque_tube"),
    "wing.controls": ("controls",),
    "wing.attach": ("spar_bolts",),
}
AILERON_ATTACHED = frozenset({"aileron", "aileron_rod", "torque_tube", "hinge_leaves"})
WORKSHOP_PARTS = frozenset({"jigs"})


def aileron_axis() -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """The aileron hinge axis, inboard to outboard: the hinge line on the top skin, FS from the p124 cuts, z from the section there."""
    pts = []
    for bl in AILERON_BL:
        x = hinge_fs(bl)
        pts.append((x, bl, z_surface(bl, x, +1)))
    return pts[0], pts[1]


def aileron_pose(shape: cq.Workplane, deg_up: float) -> cq.Workplane:
    """Rotate an aileron-attached solid about the hinge axis; 0 = neutral, ``MAX_UP_DEG`` (the 20 deg stop, p125) = trailing edge up. Right wing only."""
    if not 0.0 <= deg_up <= MAX_UP_DEG:
        raise ValueError(f"aileron deflection {deg_up} outside 0..{MAX_UP_DEG} up")
    if deg_up == 0.0:
        return shape
    a, b = aileron_axis()
    # a positive turn about +y sends +x (the TE) toward -z; trailing edge up is the other way
    return shape.rotate(a, b, -deg_up)


def conduit() -> cq.Workplane:
    """The rudder conduit (3/16 OD Nylaflow) drawn just above the top surface 4.8 in forward of the TE from 2 in inboard of BL 23 (it sticks out 2 in at the root, p123) to the wing tip at BL 157 (it continues in the winglet, chapter 20, not drawn), in straight pieces; the path and the groove depth are fitted (the curve template is an A-sheet), the 4.8 in is printed at the root."""
    r = 3 / 32
    bls = np.linspace(STN[0] - 2.0, STN[3], 15)
    pts = []
    for b in bls:
        x = te_fs(float(b)) - 4.8
        pts.append(
            (
                x,
                float(b),
                z_surface(min(max(float(b), STN[0]), STN[3]), x, +1)
                + FITTED_CONDUIT_LIFT
                + r,
            )
        )
    return _compound(_cyl(a, b, r) for a, b in pairwise(pts))


@lru_cache(maxsize=1)
def _plies() -> dict[str, list[cq.Workplane]]:
    web = [web_ply(k) for k in range(1, 7)]
    capb = [cap_ply(False, k) for k in range(1, 6)]
    capt = [cap_ply(True, k) for k in range(1, 8)]
    skb = [skin_ply(False, k) for k in range(1, 4)]
    skt = [skin_ply(True, k) for k in range(1, 4)]
    return {
        "shear_web": web,
        "cap_bottom": capb,
        "cap_top": capt,
        "skin_bottom": skb,
        "skin_top": skt,
    }


def plies() -> dict[str, list[cq.Workplane]]:
    """Display plies by group (shear_web 6, cap_bottom 5, cap_top 7, skin_bottom 3, skin_top 3), each a thin solid stacked outward (see the module docstring)."""
    return dict(_plies())


@lru_cache(maxsize=1)
def _right() -> dict[str, FusePart]:
    rep, der = "representational", "derived"
    ply = _plies()
    section_note = "planform book, section the Eppler 1230 modified file scaled to the printed thickness and twist (representational)"
    return {
        "jigs": FusePart(
            "jigs",
            jigs(),
            rep,
            (_P118, _P120),
            "five plywood jig boards, one per station; the printed floor spacings (31.72, 51.72, 88.44, 125.59 from jig 1) give the stations, their BL and outlines are not printed (page 19-1 is not on the scan); thickness fitted",
        ),
        "fc1": FusePart(
            "fc1",
            fc1_cut(),
            rep,
            (_P118, _P126, _P127),
            f"inboard core BL 23.7 to 55.5 aft of the shear web (FS 125.6 to 148.4 at BL 23, 130.5 to 155.6 at BL 55.5); {section_note}; hard-point depressions, torque-tube slot and root bay cut; the hollowed wedge and the 0.6 in shell are not drawn; the first 0.7 in is the root rib",
        ),
        "fc2": FusePart(
            "fc2",
            fc2(),
            rep,
            (_P118, _P126, _P127),
            f"centre aft core BL 55.5 to 106.25, shear web to the aileron hinge line; {section_note}",
        ),
        "fc3": FusePart(
            "fc3",
            fc3(),
            rep,
            (_P118, _P126, _P127),
            f"outboard aft core BL 106.25 to 157, shear web to the hinge line out to BL 118.1 then to the TE; {section_note}",
        ),
        "fc4": FusePart(
            "fc4",
            fc4(),
            rep,
            (_P118, _P126, _P127),
            f"centre leading-edge core BL 56.75 (outboard of the spar's end bulkhead, p88; the p126 joint is BL 55.5, 1.25 in inboard) to 106.25; the LE at BL 106.25 follows the straight line (the p126 label conflicts, FS 134.95 against 134.45); {section_note}",
        ),
        "fc5": FusePart(
            "fc5",
            fc5(),
            rep,
            (_P118, _P126, _P127),
            f"outboard leading-edge core BL 106.25 to 157; {section_note}",
        ),
        "hardpoints": FusePart(
            "hardpoints",
            hardpoints(),
            rep,
            (_P120, _P121, _P133),
            "LWA6 inboard and two LWA4 outboard at the spar's p88 bolt stations, each with a 1/8 in plate behind (LWA2, LWA3); thickness 1/4 and 1/8 and LWA6 2.3 by 2 printed (p133), LWA4 across size and depression size fitted",
        ),
        "shear_web": FusePart(
            "shear_web",
            _compound([p.val() for p in ply["shear_web"]]),
            rep,
            (_P120, _P121),
            "shear web plies 1 to 6 in the web gap; zone counts 6 (BL 23-70), 4 (70-120), 2 (120-157, cp-corrected from 3 by CP26 LPC 31); drawn at the laid ply thickness (fitted shape), the micro fills the rest",
        ),
        "cap_bottom": FusePart(
            "cap_bottom",
            _compound([p.val() for p in ply["cap_bottom"]]),
            rep,
            (_P122,),
            "bottom cap, five 3 in UND plies 142, 135, 84, 52 and 19.5 long, base schedule only (the CP25 thin-tape box adds plies); stagger read from the printed 5, 12, 19, 26 offsets; ply thickness drawn at the laid value (fitted shape)",
        ),
        "cap_top": FusePart(
            "cap_top",
            _compound([p.val() for p in ply["cap_top"]]),
            rep,
            (_P123,),
            "top cap, seven 3 in UND plies 142, 142, 119, 90, 61, 39 and 20 long, base schedule only; the 6 in step carried to ply 7 (fitted); ply thickness drawn at the laid value (fitted shape)",
        ),
        "skin_bottom": FusePart(
            "skin_bottom",
            _compound([p.val() for p in ply["skin_bottom"]]),
            rep,
            (_P122, _P128),
            "bottom skin plies, two UND and a BID tip ply drawn as a third; stops at the aileron hinge line; ply thickness drawn at the laid value (fitted shape)",
        ),
        "skin_top": FusePart(
            "skin_top",
            _compound([p.val() for p in ply["skin_top"]]),
            rep,
            (_P123, _P128),
            "top skin plies, two UND and the third UND ahead of the hinge line (drawn full chord of the cut); stops at the aileron hinge line (fitted shape)",
        ),
        "conduit": FusePart(
            "conduit",
            conduit(),
            rep,
            (_P123, _P128),
            "rudder conduit, 3/16 OD, 4.8 in forward of the TE at the root as drawn, drawn above the top surface in straight pieces, clear of the hinge hardware (really it lies under the skin in a groove); the path and the height are fitted (the curve template is on an A-sheet)",
        ),
        "ribs": FusePart(
            "ribs",
            ribs(),
            rep,
            (_P124, _P129),
            "0.7 in root rib slab (book depth) and the 2 ft incidence board (book length) on the inboard top skin; board position and size across fitted",
        ),
        "aileron": FusePart(
            "aileron",
            aileron(),
            rep,
            (_P124, _P126, _P130),
            "aileron foam BL 55.5 to 118.1 behind the top hinge line (FS 149.7 at BL 55.5, 161.45 at 106.25 from the printed cuts 5.9 and 4.35 forward of the TE, carried to BL 118.1); the inboard end BL 55.5 (p124) against BL 54.3 (p171) is a conflict; rod and tube grooves cut; section fitted",
        ),
        "hinge_pins": FusePart(
            "hinge_pins",
            hinge_pins(),
            der,
            (_P125, _P133),
            "wing-side pins of three piano hinges, 8, 6 and 6 in (printed); stations along the span fitted (the plans print the spacing in cramped digits)",
        ),
        "hinge_leaves": FusePart(
            "hinge_leaves",
            hinge_leaves(),
            rep,
            (_P125, _P133),
            "aileron-side hinge leaves, lengths 8, 6 and 6 in; leaf width and thickness fitted; turns with the aileron",
        ),
        "aileron_rod": FusePart(
            "aileron_rod",
            aileron_rod(),
            der,
            (_P125, _P133),
            "A13 mass-balance rod, 3/8 in steel (p133), along the hinge line in the aileron nose, BL 55.5 to 118.1, 63.9 in trimmed from the printed 65 (the plans butt shorter pieces); the offset aft of the hinge is fitted",
        ),
        "torque_tube": FusePart(
            "torque_tube",
            torque_tube(),
            der,
            (_P125, _P133),
            "A10 tube, 3/4 OD, 9 in long, sticking out 1 in inboard of the aileron (p125); the offset aft of the hinge is fitted",
        ),
        "controls": FusePart(
            "controls",
            controls(),
            rep,
            (_P125, _P131, _P132),
            "belhorn arm, two CS127 brackets and the CS128 belcrank as plates inside the FC1 root bay; the shapes are on full-size patterns, sizes and places fitted",
        ),
        "spar_bolts": FusePart(
            "spar_bolts",
            spar_bolts(),
            der,
            (_P88, _P128, _P129, _P134),
            "two AN8-21A (outboard pair) and one AN8-23A (inboard) at the spar's p88 stations (BL 53.5 and 25.0), 1/2 in, lengths from the part numbers (2 1/8 and 2 3/8); the bolt spacing prints 28.85 on the drawing and 28.83 in the note (unresolved), the model uses the spar stations",
        ),
    }


def build_wing(side: str = "right", aileron_up_deg: float = 0.0) -> dict[str, FusePart]:
    """All chapter 19 solids of one wing; the aileron-attached ones turned about the hinge axis by ``aileron_up_deg``. ``side`` is "right" or "left" (the mirror)."""
    if side not in ("right", "left"):
        raise ValueError(side)
    out = {}
    for n, p in _right().items():
        s = p.solid
        if n in AILERON_ATTACHED:
            s = aileron_pose(s, aileron_up_deg)
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
