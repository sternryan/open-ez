"""Upholstery (plans chapter 26, pdf page p170): front and rear seat cushions, front and rear headrests, left and right suitcases.

Same frame as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Printed (config ``upl_book_*``, ``GEOMETRY_PROVENANCE``): outline sizes only. NOT printed: any station, any weight, the foam, the fabric, the notch of the front
cushion, the length the left suitcase is shortened by. Chapter 26 has no A-sheet. Every solid is therefore ``representational``: the slabs follow the model's
own floor and seat-bulkhead faces (read from ``core.fuselage_book``, never typed here) and carry the printed thickness, width and height.
The suitcase's front edge slopes at the front seat bulkhead's own slope (printed 16 in of top edge against 18 high gives 0.889, the bulkhead leans 0.888),
which is how the suitcases are placed: hard behind the front seat bulkhead, beside the rear seat.

No upholstery mass is printed and none is stated; the cushions carry no weight in any ledger sum.
"""

from __future__ import annotations

import math
from functools import lru_cache

import cadquery as cq

from .fuselage_book import FusePart, G, build_fuselage

_P170 = "plans-1980:p170"

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_CLEAR = (
    0.1  # fitted, not book: slabs stand this far off the faces they lie against
)
FITTED_FRONT_FLOOR_Z = -14.0  # fitted, not book: the front cushion's underside (the bottom's top face is -14.9 to -14.8, the seat-belt plates -14.1)
FITTED_REAR_FLOOR_Z = -13.95  # fitted, not book: the rear cushion's and suitcases' underside (the bottom's top face rises to -14.0 at FS 103)
FITTED_FRONT_FROM_THIGH = 0.3  # fitted, not book: the front cushion starts this far aft of the thigh-support floor
FITTED_FRONT_HEADREST_Z = 6.0  # fitted, not book: the front headrest's bottom, just above the bulkhead's top (z 5.6)
FITTED_REAR_HEADREST_POS = (
    113.0,
    4.0,
)  # fitted, not book: (F.S. of the front face, z of the bottom) of the rear headrest, forward of the spar and above the sill
FITTED_SUITCASE_Y_SPAN = 5.2  # fitted, not book: the suitcases stand this far off the centre line (each is 5 thick)
FITTED_SUITCASE_RIGHT_CLEAR = 0.1  # fitted, not book: the right suitcase is notched this far clear of the control console beside it
FITTED_LEFT_SHORTEN_IN = 4.0  # fitted, not book: the left suitcase is shortened by this much at the aft end (the dashed cut on p170 has no length)

WORKSHOP_PARTS: frozenset = frozenset()
FIDELITIES_USED = frozenset({"representational"})

COMPONENT_PARTS = {
    "upholstery.cushions": ("front_cushion", "rear_cushion"),
    "upholstery.headrests": ("front_headrest", "rear_headrest"),
    "upholstery.suitcases": ("suitcase_right", "suitcase_left"),
}


# ---- helpers --------------------------------------------------------------------------------------------------------------------------
def _thigh_aft() -> float:
    from . import covers_book as cv

    return cv.thigh_x()[1]


@lru_cache(maxsize=1)
def _keepouts() -> tuple:
    """The solids the cushions and suitcases are fitted round (cut to, never overlapped): the floor and seat-belt plates, the roll-over, the controls (ch16) and the
    electrical parts (ch22). The book draws no cut-outs for them; the slabs are simply fitted to what the model already holds."""
    from . import controls_book as cb
    from . import electrical_book as eb

    fus = build_fuselage()
    out = [
        fus[n].solid.val()
        for n in ("bottom", "belt_attach", "rollover", "rollover_inserts")
    ]
    out += [p.solid.val() for p in cb.build_controls().values() if not p.void]
    out += [p.solid.val() for p in eb.build_electrical().values() if not p.void]
    return tuple(out)


def _fit(wp: cq.Workplane, also: tuple = ()) -> cq.Workplane:
    """``wp`` cut round every keepout (and ``also``), keeping only the largest piece's compound."""
    shape = wp.val()
    for k in (*_keepouts(), *also):
        shape = shape.cut(k)
    return cq.Workplane("XY").add(shape)


def _solid(shape) -> cq.Workplane:
    return cq.Workplane("XY").add(shape)


def _box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _prism_xz(pts, y0: float, y1: float) -> cq.Workplane:
    wp = cq.Workplane("XZ").polyline(pts).close().extrude(-(y1 - y0))
    bb = wp.val().BoundingBox()
    return wp.translate((0.0, y0 - bb.ymin, 0.0))


@lru_cache(maxsize=1)
def _faces() -> dict:
    """The seat bulkheads' faces as lines x = a + m (z - z_ref), measured on the built solids (probed across z, never typed here).

    Returns {"front": (front_face_x_at_z0, slope, z0), "front_aft": ..., "rear": ..., "rear_top_z": top z of the rear bulkhead, "front_top_z": ...}.
    """
    parts = build_fuselage()
    out: dict = {}
    for key, name, y, lo, hi, zs in (
        ("front", "front_seat_bkhd", 0.0, 55.0, 90.0, (-12.0, 4.0)),
        ("rear", "rear_seat_bkhd", 4.0, 95.0, 125.0, (-12.0, -4.0)),
    ):
        solid = cq.Compound.makeCompound(parts[name].solid.vals())
        bb = solid.BoundingBox()
        rows = []
        for z in zs:
            first = last = None
            x = lo
            while x < hi:
                if (
                    solid.intersect(
                        cq.Solid.makeBox(0.05, 0.04, 0.04, cq.Vector(x, y, z))
                    ).Volume()
                    > 1e-9
                ):
                    first = x if first is None else first
                    last = x + 0.05
                x += 0.05
            rows.append((z, first, last))
        (za, fa, la), (zb, fb, _lb) = rows
        slope = (fb - fa) / (zb - za)
        out[key] = {
            "x_front": fa,
            "x_aft": la,
            "z_ref": za,
            "slope": slope,
            "top_z": bb.zmax,
            "bottom_z": bb.zmin,
        }
    return out


def face_front_x(which: str, z: float) -> float:
    """F.S. of the front (forward-facing) face of the front or rear seat bulkhead at height ``z`` (measured, to about 0.05 in)."""
    f = _faces()[which]
    return f["x_front"] + f["slope"] * (z - f["z_ref"])


def face_aft_x(which: str, z: float) -> float:
    f = _faces()[which]
    return f["x_aft"] + f["slope"] * (z - f["z_ref"])


def bent_slab(
    x_start: float,
    z0: float,
    face: str,
    t: float,
    width: float,
    top_z: float,
    path_len: float | None = None,
) -> cq.Workplane:
    """A slab of thickness ``t`` and width ``width`` (centred on y = 0) on the floor at ``z0`` from ``x_start`` to the bulkhead ``face``, then up that face to
    ``top_z`` (or until ``path_len`` of path is used). The cockpit side is forward: the slab lies against the bulkhead's front face."""
    m = _faces()[face]["slope"]
    k = math.sqrt(1.0 + m * m)
    xb = face_front_x(face, z0) - FITTED_CLEAR  # where the floor part meets the face
    zc = top_z
    xc = face_front_x(face, zc) - FITTED_CLEAR
    if path_len is not None:
        used = xb - x_start
        left = max(path_len - used, 0.0)
        zc = min(top_z, z0 + left / k)
        xc = face_front_x(face, zc) - FITTED_CLEAR
    # offset (inner) polyline: the floor part lifted by t, the face part moved along its forward normal by t, mitred at the corner
    nx, nz = -1.0 / k, m / k
    xb_i = xb + t * (m - k)
    pts = [
        (x_start, z0),
        (xb, z0),
        (xc, zc),
        (xc + t * nx, zc + t * nz),
        (xb_i, z0 + t),
        (x_start, z0 + t),
    ]
    return _prism_xz(pts, -width / 2, width / 2)


# ---- cushions ---------------------------------------------------------------------------------------------------------------------------
def front_cushion() -> cq.Workplane:
    """Front cushion: 16.5 wide, 2 in thick (printed), on the floor behind the thigh support and up the front seat bulkhead's face to its top edge. The printed 46 in is
    the cut length; the drawn slab is as long as the model's floor and bulkhead allow (about 39 in of path), so it falls short of 46 (fitted)."""
    length, width, t = G.upl_book_front_cushion_in
    f = _faces()["front"]
    slab = bent_slab(
        _thigh_aft() + FITTED_FRONT_FROM_THIGH,
        FITTED_FRONT_FLOOR_Z,
        "front",
        t,
        width,
        f["top_z"],
        path_len=length,
    )
    return _fit(slab, (front_headrest().val(),))


def front_cushion_path_in() -> float:
    """Length of the front cushion's path (floor part plus face part), inches."""
    f = _faces()["front"]
    m = f["slope"]
    k = math.sqrt(1.0 + m * m)
    x0 = _thigh_aft() + FITTED_FRONT_FROM_THIGH
    xb = face_front_x("front", FITTED_FRONT_FLOOR_Z) - FITTED_CLEAR
    return (xb - x0) + (f["top_z"] - FITTED_FRONT_FLOOR_Z) * k


def rear_cushion() -> cq.Workplane:
    """Rear cushion: seat part 12 deep by 16 wide, back up the rear seat bulkhead's face (about 17 in of it against the printed 18), 2 in thick, cut round the suitcases."""
    seat_d, width, _back_h, t = G.upl_book_rear_cushion_in
    f = _faces()["rear"]
    xb = face_front_x("rear", FITTED_REAR_FLOOR_Z) - FITTED_CLEAR
    slab = bent_slab(xb - seat_d, FITTED_REAR_FLOOR_Z, "rear", t, width, f["top_z"])
    return _fit(slab, (suitcase_right().val(), suitcase_left().val()))


# ---- headrests --------------------------------------------------------------------------------------------------------------------------
def front_headrest() -> cq.Workplane:
    """4.5 by 4.5 by 2 in, cemented to the roll-over's front face, above the front seat bulkhead's top (fitted height)."""
    w, h, t = G.upl_book_front_headrest_in
    from . import fuselage_book as fb

    xf = fb.rollover_front_fs() - FITTED_CLEAR
    z0 = FITTED_FRONT_HEADREST_Z
    return _solid(_box(xf - t, xf, -w / 2, w / 2, z0, z0 + h))


def rear_headrest() -> cq.Workplane:
    """4.5 by 4.5 by 1.5 in, held by two snapped flaps over the canopy braces; where it hangs is fitted."""
    w, h, t = G.upl_book_rear_headrest_in
    xf, z0 = FITTED_REAR_HEADREST_POS
    return _solid(_box(xf, xf + t, -w / 2, w / 2, z0, z0 + h))


# ---- suitcases --------------------------------------------------------------------------------------------------------------------------
def _suitcase_x0() -> float:
    """Front-bottom corner: hard behind the front seat bulkhead's aft face at the floor (the suitcase's front edge slopes as the bulkhead does)."""
    return face_aft_x("front", FITTED_REAR_FLOOR_Z) + FITTED_CLEAR


def _suitcase(sign: int) -> cq.Workplane:
    long_, high, top, thick = G.upl_book_suitcase_in
    x0 = _suitcase_x0()
    z0 = FITTED_REAR_FLOOR_Z
    pts = [
        (x0, z0),
        (x0 + long_, z0),
        (x0 + long_, z0 + high),
        (x0 + long_ - top, z0 + high),
    ]
    ya = FITTED_SUITCASE_Y_SPAN
    wp = _prism_xz(pts, ya, ya + thick)
    return wp if sign > 0 else wp.mirror("XZ")


@lru_cache(maxsize=1)
def _right_console_box():
    from . import controls_book as cb

    b = cq.Compound.makeCompound(
        cb.build_controls()["rear_console"].solid.vals()
    ).BoundingBox()
    c = FITTED_SUITCASE_RIGHT_CLEAR
    return _box(b.xmin - c, b.xmax + c, b.ymin - c, b.ymax + c, b.zmin - c, b.zmax + c)


def suitcase_right() -> cq.Workplane:
    """Right suitcase, 30 by 18 by 14 by 5 in (printed), notched where the ch16 rear control console stands in its way (fitted)."""
    return _fit(_solid(_suitcase(1).val().cut(_right_console_box())))


def left_cut_fs() -> float:
    """F.S. the left suitcase is cut off at: its rear end is shortened by a fitted 4 in (the dashed cut on p170 has no length)."""
    return _suitcase_x0() + G.upl_book_suitcase_in[0] - FITTED_LEFT_SHORTEN_IN


def suitcase_left() -> cq.Workplane:
    """Left suitcase: shortened at the aft end (the cut is dashed on p170 and no length is printed) and notched round the left rear console LC5 and LC6."""
    from . import covers_book as cv

    sc = _suitcase(-1).val()
    keep = _box(left_cut_fs() - 100.0, left_cut_fs(), -50.0, 50.0, -50.0, 50.0)
    parts = cv.build_covers()
    return _fit(
        _solid(sc.intersect(keep)), (parts["lc5"].solid.val(), parts["lc6"].solid.val())
    )


def build_upholstery() -> dict[str, FusePart]:
    rep = "representational"
    return {
        "front_cushion": FusePart(
            "front_cushion",
            front_cushion(),
            rep,
            (_P170,),
            "front cushion: 16.5 wide and 2 in thick (printed, the point in 16.5 is faint), laid on the floor behind the thigh support and up the front seat bulkhead; the printed 46 in is the cut length, the drawn slab is shorter because the model's floor and bulkhead end first; the notch (6 to 8 by 6) is not placed; foam and fabric are not named",
        ),
        "rear_cushion": FusePart(
            "rear_cushion",
            rear_cushion(),
            rep,
            (_P170,),
            "rear cushion: seat part 12 deep by 16 wide, back up the rear seat bulkhead, 2 in thick (printed); the 4 in front edge height is not drawn; cut round the suitcases",
        ),
        "front_headrest": FusePart(
            "front_headrest",
            front_headrest(),
            rep,
            (_P170,),
            "front headrest, 4.5 by 4.5 by 2 in (printed), cemented to the roll-over front face; its height is fitted",
        ),
        "rear_headrest": FusePart(
            "rear_headrest",
            rear_headrest(),
            rep,
            (_P170,),
            "rear headrest, 4.5 by 4.5 by 1.5 in (printed; the 1.5 is medium); the two snapped flaps are not drawn and where it hangs is fitted",
        ),
        "suitcase_right": FusePart(
            "suitcase_right",
            suitcase_right(),
            rep,
            (_P170,),
            "right suitcase: 30 long, 18 high at the rear edge, 14 across the top, 5 thick (printed; the 4.5 collapsed is a small read), placed hard behind the front seat bulkhead and notched round the ch16 rear console; the shell (ABS 0.06 to 0.09 in or 4 plies BID) and the bag are not drawn",
        ),
        "suitcase_left": FusePart(
            "suitcase_left",
            suitcase_left(),
            rep,
            (_P170,),
            "left suitcase, shortened to clear the left rear console (the dashed cut on p170 has no length; the cut here is fitted)",
        ),
    }
