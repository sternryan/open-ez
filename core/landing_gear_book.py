"""
Open-EZ PDE: Long-EZ main landing gear from the book (plans chapter 9, back cover)
=================================================================================

Same fidelity labels as ``core.fuselage_book`` (``FusePart``): ``book``, ``derived``, ``representational``.
Same frame: model x = F.S. (aft positive), y = B.L. (right positive), z = W.L. - 17.4 + wing_le_wl.

What the book prints, and what it does not:

- Printed: the axle centre line at F.S. 110.5 (p50 figure 1A, p171), 15 in forward of the spar's aft
  face at F.S. 125.5; the axle height W.L. -22 and the 12 degree tip-back line (p171); the jig block
  (p53 figure 1, p51), the tube (p53), the extrusion section (p52), the toe-in (p52), the straight
  board's datum (B.L. 26.75, F.S. 125.5, p50).
- NOT printed: the strut outline (strut mold), the gear track, where the extrusions sit on the side
  (template A5, not held), the CG height. Everything that rests on those is fitted below and tagged
  representational. The track is never measured off an image and appears in no config, provenance or
  ledger readout.

No tip-back or tip-over verdict is computed here; ``ground_handling`` says why.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple

import cadquery as cq
import numpy as np

from . import nose_gear_kin as ngk
from .fuselage_book import (
    FusePart,
    G,
    Z_TOP,
    bottom_z,
    half_width,
    z_of_wl,
)

_P50, _P51, _P52, _P53, _P171 = (f"plans-1980:p{n}" for n in (50, 51, 52, 53, 171))

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_TRACK = 84.0  # fitted, not book: the track has no source (strut mold and A5 not held)
FITTED_ATTACH_AFT_OF_SIDE_END = 8.0  # fitted, not book: tube centre this far forward of the side's aft end (inside the p38 pad)
FITTED_TUBE_BELOW_SIDE_EDGE = 1.5  # fitted, not book: tube centre below the side's bottom edge (= jig block hole to sharp edge)
FITTED_TUBE_OUT_OF_SIDE = 1.1  # fitted, not book: tube centre outboard of the side face (p52 prints the 3/8 hole 1.1 from the edge)
FITTED_EXT_LENGTH = 3.0  # fitted, not book: the extrusion's length (the p52 sheet gives the section, not the length)
FITTED_STRUT_CHORD = 4.4  # fitted, not book: strut section chord (strut mold not printed)
FITTED_STRUT_THICK = 1.0  # fitted, not book: strut section thickness
FITTED_AXLE_STUB = (0.5, 5.0)  # fitted, not book: (radius, length) of the drawn axle stub
FITTED_BOARD_THICK = 0.75  # fitted, not book: datum board thickness (along F.S.)
FITTED_BOARD_WIDTH = 3.0  # fitted, not book: datum board width (along B.L., centred on B.L. +/-26.75)
FITTED_BOARD_OVER_AXLE = 5.0  # fitted, not book: the board stands this far past the axle height (inverted pose)
FITTED_LEG_ANGLE = 25.0  # fitted, not book: arrival angle of each leg at the axle, from vertical, outboard-leaning (p51 top figure reads 20-35)
FITTED_BEND_HANDLE = 8.0  # fitted, not book: length of the flat-tangent handle at each side-corner bend (sets how generous the bend is)
FITTED_AXLE_HANDLE = 28.0  # fitted, not book: length of the straight run-in handle at the axle end of each leg

_THICK_ANGLE = G.gear_extrusion[0]  # 1/4, book p52
_BLOCK_W, _BLOCK_R, _BLOCK_HOLE, _BLOCK_BELOW, _BLOCK_BEVEL, _BLOCK_T = G.gear_jig_block
_TUBE_OD, _TUBE_WALL, _TUBE_LEN = G.gear_tube

SIDES = (-1, 1)  # -1 left (B.L. negative), +1 right


# --- the axle (book station, representational lateral) --------------------------------------------
class AxlePoint(NamedTuple):
    side: str
    fs: float
    bl: float
    wl: float
    xyz: tuple[float, float, float]  # model frame
    tags: dict


def axle_points() -> dict[str, AxlePoint]:
    """Left and right axle centres. F.S. (p50, p171) and W.L. (p171) are book; B.L. is fitted."""
    assert abs(G.fs_main_axle - (G.fs_spar_aft_face - G.main_axle_fwd_of_spar)) < 1e-9
    tags = {
        "fs": {"fidelity": "book", "cite": f"{_P50} figure 1A F.S. 110.5; {_P171}"},
        "wl": {"fidelity": "book", "cite": f"{_P171} main axle W.L. -22"},
        "bl": {"fidelity": "representational", "cite": None,
               "note": "fitted, not book: the track has no source (strut mold and A5 not held)"},
    }
    out = {}
    for s, name in ((-1, "left"), (1, "right")):
        bl = s * FITTED_TRACK / 2
        out[name] = AxlePoint(name, G.fs_main_axle, bl, G.wl_main_axle,
                              (G.fs_main_axle, bl, z_of_wl(G.wl_main_axle)), tags)
    return out


def _toe_in_rad() -> float:
    lo, hi = G.gear_toe_in_b_minus_a
    return math.atan(((lo + hi) / 2) / G.gear_toe_in_square_in)


def _axle_dir(side: int) -> np.ndarray:
    """Unit axle axis pointing outboard, toed in (midpoint of the p52 range): the outboard end leans forward."""
    phi = _toe_in_rad()
    return np.array([-math.sin(phi), side * math.cos(phi), 0.0])


# --- fitted attach geometry ------------------------------------------------------------------------
def _fs_tube() -> float:
    return G.fs_f22 + G.side_panel_length - FITTED_ATTACH_AFT_OF_SIDE_END


def _tube_y(side: int) -> float:
    fs = _fs_tube()
    return side * (half_width(fs) + G.side_panel_thickness + FITTED_TUBE_OUT_OF_SIDE)


def _tube_z() -> float:
    return bottom_z(_fs_tube()) - FITTED_TUBE_BELOW_SIDE_EDGE


def attach_points() -> dict[str, tuple[float, float, float]]:
    """Strut attach points at the lower aft corners (fitted inside the p38 gear pad; A5 not held)."""
    return {n: (_fs_tube(), _tube_y(s), _tube_z()) for s, n in ((-1, "left"), (1, "right"))}


def _box(x0, x1, y0, y1, z0, z1) -> cq.Workplane:
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane(obj=cq.Compound.makeCompound([s.val() for s in solids]))


# --- strut -----------------------------------------------------------------------------------------
def _centre_z() -> float:
    """Centre line of the strut's flat centre section: the strut's top face touches the underside of the
    bottom (the side bottom edge carried aft past the bottom plate, less the bottom foam thickness)."""
    return bottom_z(_fs_tube()) - G.bottom_foam_thickness - FITTED_STRUT_THICK / 2


def _leg_curve(side: int, n: int = 16) -> list[tuple[float, float, float]]:
    """One leg, side corner to axle centre: a cubic Bezier in (y, z) that leaves the flat centre section
    horizontally (a generous bend) and arrives at the axle FITTED_LEG_ANGLE from vertical, leaning outboard.
    F.S. runs from the attach station to 110.5 on a smoothstep, so the leg rakes forward going down."""
    ax = axle_points()["right" if side > 0 else "left"].xyz
    ya = abs(attach_points()["right"][1])
    zc, xa = _centre_z(), _fs_tube()
    ang = math.radians(FITTED_LEG_ANGLE)
    p0 = np.array([ya, zc])
    p3 = np.array([abs(ax[1]), ax[2]])
    p1 = p0 + np.array([FITTED_BEND_HANDLE, 0.0])
    p2 = p3 - FITTED_AXLE_HANDLE * np.array([math.sin(ang), -math.cos(ang)])
    out = []
    for i in range(n + 1):
        t = i / n
        yz = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3
        sm = 3 * t**2 - 2 * t**3
        out.append((xa + (ax[0] - xa) * sm, side * yz[0], yz[1]))
    out[-1] = tuple(ax)  # exactly the axle point
    return out


def strut_path() -> list[tuple[float, float, float]]:
    """Centre line of the one-piece bow, left axle to right axle: up the left leg, flat across the bottom
    between the attach tabs at the lower side corners, down the right leg."""
    left = list(reversed(_leg_curve(-1)))  # axle -> corner
    right = _leg_curve(1)  # corner -> axle
    zc, xa = _centre_z(), _fs_tube()
    return left + [(xa, 0.0, zc)] + right


def _strut() -> cq.Workplane:
    pts = [cq.Vector(*p) for p in strut_path()]
    path = cq.Workplane("XY").spline(pts, includeCurrent=False)
    # elliptical section (an airfoil stand-in), chord along x, at the left axle end, normal to the path there
    t0 = (pts[1] - pts[0]).normalized()
    xd = cq.Vector(1, 0, 0)
    xd = (xd - t0 * xd.dot(t0)).normalized()
    plane = cq.Plane(origin=pts[0], xDir=xd, normal=t0)
    prof = cq.Workplane(plane).ellipse(FITTED_STRUT_CHORD / 2, FITTED_STRUT_THICK / 2)
    return prof.sweep(path, transition="round")


# --- extrusions, tubes, blocks ---------------------------------------------------------------------
def _tube_x_ends() -> tuple[float, float]:
    xc = _fs_tube()
    return xc - _TUBE_LEN / 2, xc + _TUBE_LEN / 2


def _flange_x(which: int) -> tuple[float, float]:
    """x range of the outstanding flange of the forward (-1) or aft (+1) angle: just inboard of its jig block."""
    xe0, xe1 = _tube_x_ends()
    inset = G.gear_tube_showing + _BLOCK_T  # tube showing, then the block
    if which < 0:
        return xe0 + inset, xe0 + inset + _THICK_ANGLE
    return xe1 - inset - _THICK_ANGLE, xe1 - inset


def _extrusions() -> cq.Workplane:
    t, a, _ = G.gear_extrusion
    z0 = _tube_z() - a / 2 - 0.0
    sol = []
    for s in SIDES:
        face = s * (half_width(_fs_tube()) + G.side_panel_thickness)  # outer face of the side
        for w in (-1, 1):
            fx0, fx1 = _flange_x(w)
            # outstanding flange (in the y-z plane, a deep, a tall) and the leg on the side face, running toward the gap
            y0, y1 = sorted((face, face + s * a))
            flange = _box(fx0, fx1, y0, y1, z0, z0 + FITTED_EXT_LENGTH)
            # legs run toward each other, into the gap between the pair, so the angles sit between the jig blocks
            lx0, lx1 = (fx0, fx1 + a) if w < 0 else (fx0 - a, fx1)
            ly0, ly1 = sorted((face, face + s * t))
            leg = _box(lx0, lx1, ly0, ly1, z0, z0 + FITTED_EXT_LENGTH)
            sol.append(flange.union(leg))
    return _compound(sol)


def _gear_tubes() -> cq.Workplane:
    xe0, _ = _tube_x_ends()
    sol = []
    for s in SIDES:
        t = (cq.Workplane("YZ").workplane(offset=xe0).center(_tube_y(s), _tube_z())
             .circle(_TUBE_OD / 2).circle(_TUBE_OD / 2 - _TUBE_WALL).extrude(_TUBE_LEN))
        sol.append(t)
    return _compound(sol)


def jig_block_solid() -> cq.Workplane:
    """One jig block, local frame: hole centre at the origin, thickness along x, round top up (+z), the
    sharp bevelled edge down at z = -(below + bevel). p53 figure 1 and p51: 1/4 ply, 2 wide, 1 radius, 5/8 hole,
    0.7 below the hole then 0.8 bevelled (here: thickness tapering to zero) to a sharp edge."""
    h_low = _BLOCK_BELOW + _BLOCK_BEVEL
    w2 = _BLOCK_W / 2
    prof = (cq.Workplane("YZ").moveTo(-w2, -h_low).lineTo(w2, -h_low).lineTo(w2, 0)
            .threePointArc((0, _BLOCK_R), (-w2, 0)).close())
    blk = prof.extrude(_BLOCK_T)
    blk = blk.cut(cq.Workplane("YZ").circle(_BLOCK_HOLE / 2).extrude(_BLOCK_T))
    wedge = (cq.Workplane("XZ").moveTo(0, -h_low).lineTo(_BLOCK_T, -h_low).lineTo(_BLOCK_T, -h_low + _BLOCK_BEVEL)
             .close().extrude(w2 + 0.01, both=True))  # the XZ normal is -y; both=True spans +/- y
    return blk.cut(wedge)


def _jig_blocks() -> cq.Workplane:
    xe0, xe1 = _tube_x_ends()
    sol = []
    for s in SIDES:
        for x_out in (xe0 + G.gear_tube_showing, xe1 - G.gear_tube_showing - _BLOCK_T):
            b = jig_block_solid().rotate((0, 0, 0), (1, 0, 0), 180)  # round top toward -z (down in the upright frame)
            if x_out < _fs_tube():  # forward block: mirror in x so the bevel faces forward, outboard (p50 "bevels to the outside")
                b = b.mirror("YZ").translate((_BLOCK_T, 0, 0))
            sol.append(b.translate((x_out, _tube_y(s), _tube_z())))
    return _compound(sol)


# --- datum board and axles -------------------------------------------------------------------------
def _datum_board() -> cq.Workplane:
    """Two straight boards, one each side, standing VERTICAL (long axis along W.L.) with the forward edge on
    F.S. 125.5, the station the spar's aft face will occupy, centred on B.L. +/-26.75 (p50 figure 1A). Upright
    frame: they hang from the table plane Z_TOP down past the axle height; with the fuselage inverted (the
    book's pose) they stand on the table and reach FITTED_BOARD_OVER_AXLE past the axle."""
    z_lo = z_of_wl(G.wl_main_axle) - FITTED_BOARD_OVER_AXLE
    x0 = G.fs_spar_aft_face
    sol = []
    for s in SIDES:
        yc = s * G.bl_gear_datum
        sol.append(_box(x0, x0 + FITTED_BOARD_THICK, yc - FITTED_BOARD_WIDTH / 2, yc + FITTED_BOARD_WIDTH / 2, z_lo, Z_TOP))
    return _compound(sol)


def _axles() -> cq.Workplane:
    r, ln = FITTED_AXLE_STUB
    sol = []
    for s, name in ((-1, "left"), (1, "right")):
        p = np.array(axle_points()[name].xyz)
        d = _axle_dir(s)
        sol.append(cq.Workplane(obj=cq.Solid.makeCylinder(r, ln, cq.Vector(*p), cq.Vector(*d))))
    return _compound(sol)


_AXLE_NOTE = (
    "toe-in drawn at the midpoint of the p52 range (B-A 0.325 over 24 in, 0.78 deg), outboard ends leaning forward; "
    "stub size fitted"
)


@lru_cache(maxsize=1)
def build_gear() -> dict[str, FusePart]:
    parts: dict[str, FusePart] = {}
    parts["strut"] = FusePart(
        "strut", _strut(), "representational", (),
        note=("one-piece airfoil-section bow: flat across the underside of the bottom between the attach tabs at the "
              "lower side corners, then each leg bends outboard and down to the axle, arriving ~25 deg from vertical, "
              "raking forward going down (p50, p51 top figure); the strut mold is not printed "
              f"and the track has no source (fitted {FITTED_TRACK:g} in). Attach points fitted inside the p38 gear pad "
              "(15.3, 12, 6.2, 3.2 from the side's aft end); template A5 not held."))
    parts["extrusions"] = FusePart(
        "extrusions", _extrusions(), "representational", (),
        note=(f"four 1/4 x 2 x 2 6061-T6 angles (section size book, {_P52}); placement fitted (template A5 not held) "
              f"and length {FITTED_EXT_LENGTH:g} in fitted; the 3/8, 3/4 and 1/4 holes are not modelled."))
    parts["gear_tubes"] = FusePart(
        "gear_tubes", _gear_tubes(), "representational", (),
        note=(f"4130N 5/8 OD x 0.049 x 6.75 (size book, {_P53}); one per side between the angle pairs, tube axis "
              "along F.S.; placement fitted at the extrusions."))
    parts["jig_blocks"] = FusePart(
        "jig_blocks", _jig_blocks(), "representational", (_P53, _P50, _P51),
        note=("shape book (p53 figure 1: 1/4 ply, 2 wide, 1 in radius top, 5/8 hole, 0.7 + 0.8 below with the 0.8 "
              "bevelled to a sharp edge; p50: 0.65 of tube showing; p51); two per tube. Placement follows the fitted "
              "tubes, so the part is representational, not derived: the book fixes the block on its tube, not the "
              "tube on the fuselage."))
    parts["datum_board"] = FusePart(
        "datum_board", _datum_board(), "derived", (_P50,),
        note=("straight edge vertical against the spar's aft face at F.S. 125.5, datum at B.L. 26.75 (p50); "
              "two vertical boards, one each side of the centre line, long axis along W.L., standing at the station the "
              "spar's aft face will occupy (the spar is chapter 14, p9-1 reference 8 -> 14 by CP36 LPC 112, and is not "
              f"modelled); cross-section fitted ({FITTED_BOARD_THICK:g} thick x {FITTED_BOARD_WIDTH:g} wide), height fitted "
              f"to reach {FITTED_BOARD_OVER_AXLE:g} in past the axle height when the fuselage is inverted."))
    parts["axles"] = FusePart(
        "axles", _axles(), "representational", (),
        note=("stubs at the axle points: F.S. 110.5 and W.L. -22 book (p50, p171), B.L. fitted. " + _AXLE_NOTE))
    return parts


# --- poses -----------------------------------------------------------------------------------------
class Pose(NamedTuple):
    """p' = R @ p + t, in the fuselage model frame (x aft, y right, z up)."""

    rotation: np.ndarray  # 3x3
    translation: np.ndarray  # 3

    def apply(self, pts) -> np.ndarray:
        p = np.asarray(pts, dtype=float)
        return p @ self.rotation.T + self.translation


def _rot_x(deg: float) -> np.ndarray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def _about(R: np.ndarray, centre: np.ndarray) -> Pose:
    return Pose(R, centre - R @ centre)


def bank_pose(deg: float, pivot: tuple[float, float] = (0.0, Z_TOP)) -> Pose:
    """Roll about the longitudinal axis through (y, z) = pivot. Positive degrees are a LEFT bank: the
    right side goes up (chapter 7 glasses the right side at 45 deg left bank, then rolls to 45 deg right)."""
    return _about(_rot_x(deg), np.array([0.0, pivot[0], pivot[1]]))


def inverted_pose() -> Pose:
    """Chapter 9: the fuselage upside down and levelled on the top longerons. A half roll about the
    longitudinal axis at the longeron tops, so the longeron tops stay on the plane z = Z_TOP (the table)."""
    return bank_pose(180.0)


def inverted_gear() -> dict[str, cq.Workplane]:
    """Every gear solid in the inverted pose (the book builds the gear on the upside-down fuselage: legs up)."""
    pose = inverted_pose()
    ang = 180.0
    assert np.allclose(pose.rotation, _rot_x(ang))
    return {n: p.solid.rotate((0, 0, Z_TOP), (1, 0, Z_TOP), ang) for n, p in build_gear().items()}


def inverted_axle_points() -> dict[str, np.ndarray]:
    pose = inverted_pose()
    return {n: pose.apply(a.xyz) for n, a in axle_points().items()}


# --- ground handling -------------------------------------------------------------------------------
def ground_handling() -> dict:
    """The book's ground-handling facts. No numeric verdict: CG height and the track have no source."""
    return {
        "main_axle_fs": G.fs_main_axle,
        "main_axle_wl": G.wl_main_axle,
        "tip_back_line_deg": G.gear_tip_back_deg,
        "cite": {
            "main_axle_fs": f"{_P50} figure 1A; {_P171}",
            "main_axle_wl": _P171,
            "tip_back_line_deg": f"{_P171} 12 deg line from the main tyre contact",
        },
        "tip_back_check": "not yet computed: no source for the CG height",
        "tip_over_check": "not yet computed: the track has no source",
    }


# --- nose gear (chapter 13), forward of F22 ----------------------------------------------------------
# Fitted, not book. The strut rake, fork offset, NG6 position and trail appear in no config or provenance field.
FITTED_NG6_BLOCK = (
    2.5,
    2.5,
)  # fitted, not book: (x length, height) of the NG6 casting block; the 2.75 width and the 1.25 bore height are book (p73)
FITTED_NG6_BORE_R = 0.3  # fitted, not book: pivot bore radius
FITTED_NG_STRUT = (
    20.3,
    1.0,
    1.8,
)  # fitted, not book: (length from the pivot, depth along F.S., width across) of the NG-1L box section
FITTED_NG_FORK = (
    6.6,
    2.0,
    3.8,
    3.0,
)  # fitted, not book: (length, depth, width, slot width) of the lower fork block, below the strut end
FITTED_NG_FORK_SLOT_TOP = (
    0.55  # fitted, not book: the fork's bridge is this thick at its top
)
FITTED_TIRE_OD = 9.0  # fitted, not book: 2.80/2.50-4 tire OD is NOT printed
FITTED_RIM_OD = 4.0  # the 4 in wheel rim (a size name, not a drawn dimension)
FITTED_TIRE_WIDTH = 2.8  # the 2.80 of 2.80/2.50-4, a section width
FITTED_RIM_WIDTH = 2.2  # fitted, not book

NOSE_CANDIDATES = {
    "plans": G.fs_nose_wheel,
    "manual": G.fs_nose_wheel_manual,
}  # the p171 / Owner's Manual conflict pair
assert tuple(NOSE_CANDIDATES.values()) == ngk.AXLE_FS_CANDIDATES

_NOSE_CONFLICT = (
    "the axle station is the p171 (F.S. 17) versus Owner's Manual (about 20) conflict, so the pivot F.S. is SOLVED by "
    "core.nose_gear_kin from the candidate, a derived-from-assumption position, not a measurement. Assumptions: strut "
    f"pivot to axle exactly {G.nose_strut_pivot_to_pivot_in:g} (p81) with zero fork offset, pivot W.L. = skin line "
    f"{G.wl_fuselage_bottom_3view:g} + bore height {G.ng6_bore_height_in:g}. No strut rake, fork offset, trail or NG6 position is printed."
)


def nose_gear_points(candidate: str = "plans") -> dict:
    """Pivot and axle centre (model frame), the strut's lean from vertical, for one axle candidate."""
    if candidate not in NOSE_CANDIDATES:
        raise ValueError(f"candidate must be one of {sorted(NOSE_CANDIDATES)}")
    axle_fs = NOSE_CANDIDATES[candidate]
    length = G.nose_strut_pivot_to_pivot_in
    pivot_wl = ngk.default_pivot_wl()
    pivot_fs, _ = ngk.ng6_pivot_for_axle(axle_fs, G.wl_nose_wheel, pivot_wl, length)
    return {
        "candidate": candidate,
        "pivot": (pivot_fs, 0.0, z_of_wl(pivot_wl)),
        "axle": (axle_fs, 0.0, z_of_wl(G.wl_nose_wheel)),
        "strut_length": length,
        "theta_down_deg": ngk.theta_down_deg(pivot_wl, G.wl_nose_wheel, length),
    }


def _strut_frame(solid: cq.Workplane, pts: dict) -> cq.Workplane:
    """Move a solid built hanging straight down from the origin (local -z along the strut) to the gear-down strut."""
    px, _, pz = pts["pivot"]
    return solid.rotate((0, 0, 0), (0, 1, 0), -pts["theta_down_deg"]).translate(
        (px, 0.0, pz)
    )


def _ng6_block(pts: dict) -> cq.Workplane:
    lx, h = FITTED_NG6_BLOCK
    w = G.ng6_width_in
    px, _, pz = pts["pivot"]
    base = (
        pz - G.ng6_bore_height_in
    )  # the bore centre is 1.25 above the plate base (p73)
    blk = _box(px - lx / 2, px + lx / 2, -w / 2, w / 2, base, base + h)
    return blk.cut(
        cq.Workplane(
            obj=cq.Solid.makeCylinder(
                FITTED_NG6_BORE_R,
                w + 1,
                cq.Vector(px, -w / 2 - 0.5, pz),
                cq.Vector(0, 1, 0),
            )
        )
    )


def _strut_box(pts: dict) -> cq.Workplane:
    ln, dep, wid = FITTED_NG_STRUT
    return _strut_frame(_box(-dep / 2, dep / 2, -wid / 2, wid / 2, -ln, 0.0), pts)


def _fork_block(pts: dict) -> cq.Workplane:
    ln, dep, wid, slot = FITTED_NG_FORK
    top = -FITTED_NG_STRUT[0]
    blk = _box(-dep / 2, dep / 2, -wid / 2, wid / 2, top - ln, top)
    cut = _box(
        -dep / 2 - 1,
        dep / 2 + 1,
        -slot / 2,
        slot / 2,
        top - ln - 1,
        top - FITTED_NG_FORK_SLOT_TOP,
    )
    return _strut_frame(blk.cut(cut), pts)


def _wheel(pts: dict) -> cq.Workplane:
    ax = pts["axle"]
    d = cq.Vector(0, 1, 0)

    def cyl(r, w):
        return cq.Solid.makeCylinder(r, w, cq.Vector(ax[0], ax[1] - w / 2, ax[2]), d)

    tire = cq.Workplane(obj=cyl(FITTED_TIRE_OD / 2, FITTED_TIRE_WIDTH)).cut(
        cq.Workplane(obj=cyl(FITTED_RIM_OD / 2, FITTED_TIRE_WIDTH + 1))
    )
    rim = cq.Workplane(obj=cyl(FITTED_RIM_OD / 2, FITTED_RIM_WIDTH))
    return _compound([tire, rim])


@lru_cache(maxsize=2)
def build_nose_gear(candidate: str = "plans") -> dict[str, FusePart]:
    """The retracting nose gear in the gear-down pose, for one axle candidate ("plans" F.S. 17 or "manual" F.S. 20)."""
    pts = nose_gear_points(candidate)
    ax, pv = pts["axle"], pts["pivot"]
    fs = f"axle F.S. {ax[0]:g} ({candidate} candidate), W.L. {G.wl_nose_wheel:g}"
    rep = "representational"
    return {
        "ng6_block": FusePart(
            "ng6_block",
            _ng6_block(pts),
            rep,
            ("plans-1980:p73",),
            note=(
                f"NG6 casting block {G.ng6_width_in:g} wide, centred between the NG30 plates, bore centre {G.ng6_bore_height_in:g} above "
                f"the plate base (p73); block length and height fitted. Pivot F.S. {pv[0]:.2f} is SOLVED, not measured: "
                + _NOSE_CONFLICT
            ),
        ),
        "strut": FusePart(
            "strut",
            _strut_box(pts),
            rep,
            ("plans-1980:p81",),
            note=(
                f"NG-1L as a fitted box section ({FITTED_NG_STRUT[1]:g} x {FITTED_NG_STRUT[2]:g}) from the pivot toward the lower pivot; the "
                f"pivot-to-axle length is the printed {pts['strut_length']:g} (p81, medium) with the fork's drop folded in. "
                f"Lean from vertical {pts['theta_down_deg']:.1f} deg is derived, not printed. "
                + _NOSE_CONFLICT
            ),
        ),
        "fork": FusePart(
            "fork",
            _fork_block(pts),
            rep,
            (),
            note=(
                f"fitted lower fork block, {FITTED_NG_FORK[1]:g} x {FITTED_NG_FORK[2]:g} with a {FITTED_NG_FORK[3]:g} slot for the wheel; "
                f"no fork offset is modelled (axle centred on the strut line). Axle: {fs}."
            ),
        ),
        "wheel": FusePart(
            "wheel",
            _wheel(pts),
            rep,
            (),
            note=(
                f"4 in rim, 2.80/2.50-4 tire drawn {FITTED_TIRE_WIDTH:g} wide at OD {FITTED_TIRE_OD:g} (tire OD is NOT printed: fitted); "
                f"centre at {fs}, which is the conflict pair p171 / Owner's Manual: "
                + _NOSE_CONFLICT
            ),
        ),
    }


def nose_retracted_theta_deg(candidate: str = "plans") -> float:
    """Fitted retracted strut angle: the tire's lowest point clears the skin line W.L. 0.9 (the retracted angle is not printed)."""
    pts = nose_gear_points(candidate)
    pivot_wl = G.wl_fuselage_bottom_3view + G.ng6_bore_height_in
    clear = G.wl_fuselage_bottom_3view + FITTED_TIRE_OD / 2
    return ngk.theta_up_for_clearance_deg(pivot_wl, G.nose_strut_pivot_to_pivot_in, clear)


def nose_gear_pose(t: float, candidate: str = "plans") -> np.ndarray:
    """4x4 homogeneous matrix taking the gear-down solids to retraction progress t in [0, 1].

    Rotation about the NG6 axis (along Y through the pivot): t=0 is the identity (gear down), t=1 has the strut
    pointing aft and slightly up (theta from nose_retracted_theta_deg, fitted so the tire clears the skin line).
    """
    pts = nose_gear_points(candidate)
    delta = ngk.retraction_theta_deg(t, pts["theta_down_deg"], nose_retracted_theta_deg(candidate)) - pts["theta_down_deg"]
    c, s = math.cos(math.radians(-delta)), math.sin(math.radians(-delta))
    rot = np.array(
        [[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float
    )  # R_y(-delta): sweeps the lower end aft
    pivot = np.array(pts["pivot"], dtype=float)
    m = np.eye(4)
    m[:3, :3] = rot
    m[:3, 3] = pivot - rot @ pivot
    return m
