"""Per-ply areas for the fuselage box (plans chapters 4-8).

Every ``materials`` row of a chapter 4-8 op in the guide graph is either MAPPED to a part and a
region (SCOPE) or EXCLUDED with a reason (EXCLUDED). ``scope_problems`` fails on any row that is
neither, so a new row cannot slip into the model unplaced.

    ch04-06 materials rows -> SCOPE (part, region, angles) -> FusePly(node, area_in2, arm_in, ...)
                          \\-> EXCLUDED (reason, parts whose glass is therefore incomplete)

A region is measured on the part solid from ``core.fuselage_book`` (faces are picked by normal, the
area is OCC ``Area()``), or is a stated patch (a circle from the page) or a corner tape (measured
length times the width the page states). A region that can only under-count what the row describes
(a wrap around an edge, corners that are not all counted) is flagged ``lower_bound``.

Plies on a representational part inherit that fidelity: the area is of the fitted stand-in, not of
a book outline.

Pure data plus CadQuery measurement; the lab export and the mass ledger read ``plies()``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import pairwise
from pathlib import Path
from typing import Any

import cadquery as cq

from config import config

from . import fuselage_book as fb
from .fuselage_book import FusePart, build_fuselage

G = config.geometry
CHAPTERS = (4, 5, 6, 7, 8)
_GRAPH_DIR = Path(__file__).resolve().parents[1] / "guide" / "graph"


class FusePlyError(ValueError):
    pass


# --- regions --------------------------------------------------------------------------------------

# face name -> (direction the face normal must point, minimum dot product, which faces count)
_FACES: dict[str, tuple[tuple[float, float, float], float, str]] = {
    "fwd": ((-1.0, 0.0, 0.0), 0.5, "largest"),
    "aft": ((1.0, 0.0, 0.0), 0.5, "largest"),
    "upper": ((0.0, 0.0, 1.0), 0.9, "largest"),
    "lower": ((0.0, 0.0, -1.0), 0.9, "largest"),
    # the side's outside face: normal away from the centreline (right +y, left -y), all pieces of the bent plan
    "outside": ((0.0, 0.0, 0.0), 0.9, "all"),
    # the flat top of each small block (belt-attach pads): every block's top face
    "pad_top": ((0.0, 0.0, 1.0), 0.99, "all"),
    # the side's inside face: normal toward the centreline, all pieces (bent plan, sight gauge, dish)
    "inside": ((0.0, 0.0, 0.0), 0.9, "all"),
}


def _direction(part_name: str, name: str) -> tuple[float, float, float]:
    if name == "inside":
        if part_name == "side_left":
            return (0.0, 1.0, 0.0)
        if part_name == "side_right":
            return (0.0, -1.0, 0.0)
        raise FusePlyError(f"{part_name} has no inside face rule")
    if name == "outside":
        if part_name == "side_left":
            return (0.0, -1.0, 0.0)
        if part_name == "side_right":
            return (0.0, 1.0, 0.0)
        raise FusePlyError(f"{part_name} has no outside face rule")
    return _FACES[name][0]


def _faces(part_name: str, part: FusePart, name: str):
    d = _direction(part_name, name)
    _, thr, how = _FACES[name]
    hits = []
    for f in part.solid.faces().vals():
        n = f.normalAt()
        if n.x * d[0] + n.y * d[1] + n.z * d[2] >= thr:
            hits.append(f)
    if not hits:
        raise FusePlyError(f"{part_name}: no {name} face found")
    if how == "largest":
        hits = [max(hits, key=lambda f: f.Area())]
    return hits


@dataclass(frozen=True)
class Face:
    """A face of the part solid, optionally less a round hole cut through the glass."""

    name: str
    less_circle_dia: float | None = None
    lower_bound: bool = False
    note: str = ""

    def label(self) -> str:
        s = f"face:{self.name}"
        if self.less_circle_dia:
            s += f" less {self.less_circle_dia:g} in hole"
        return s

    def measure(self, part_name: str, part: FusePart) -> tuple[float, float]:
        fs = _faces(part_name, part, self.name)
        area = sum(f.Area() for f in fs)
        arm = sum(f.Area() * f.Center().x for f in fs) / area
        if self.less_circle_dia:
            hole = math.pi / 4 * self.less_circle_dia**2
            area -= hole
        return area, arm

    def faces(self, part_name: str) -> list:
        """The faces this region covers on the part solid (the lab shells these; the area is measured on them)."""
        return _faces(part_name, build_fuselage()[part_name], self.name)


# Clips for ClipFace, hashable tuples: ("box", x0, x1, y0, y1, z0, z1) or ("fwd_of_front_bkhd",).
Clip = tuple


def _clip_solid(clip: Clip):
    if clip[0] == "box":
        return fb._box(*clip[1:])
    if clip[0] == "fwd_of_front_bkhd":
        # forward of the front seat bulkhead's line on the side (derived from the config segment, extended)
        z_lo, z_hi = -60.0, 60.0
        x_lo, x_hi = fb.front_bulkhead_line_fs(z_lo), fb.front_bulkhead_line_fs(z_hi)
        return (
            cq.Workplane("XZ")
            .polyline([(0.0, z_lo), (x_lo, z_lo), (x_hi, z_hi), (0.0, z_hi)])
            .close()
            .extrude(50.0, both=True)
        )
    raise FusePlyError(f"unknown clip {clip[0]}")


@dataclass(frozen=True)
class ClipFace(Face):
    """A named face of the part solid clipped to a stated region (a box or the front seat bulkhead's slanted line)."""

    clip: Clip = ("box", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def label(self) -> str:
        return f"face:{self.name} clipped ({self.clip[0]})"

    def faces(self, part_name: str) -> list:
        solid = _clip_solid(self.clip).val()
        out = []
        for f in _faces(part_name, build_fuselage()[part_name], self.name):
            out.extend(f.intersect(solid).Faces())
        if not out:
            raise FusePlyError(
                f"{part_name}: clip {self.clip[0]} leaves no {self.name} face"
            )
        return out

    def measure(self, part_name: str, part: FusePart) -> tuple[float, float]:
        fs = self.faces(part_name)
        area = sum(f.Area() for f in fs)
        return area, sum(f.Area() * f.Center().x for f in fs) / area


@dataclass(frozen=True)
class PadMargin:
    """Each block's top face grown by ``margin`` all round (a pad of glass lapping the insert, summed over blocks)."""

    margin: float
    face: str = "pad_top"
    lower_bound: bool = False
    note: str = ""

    def label(self) -> str:
        return f"pads: block tops plus {self.margin:g} in all round"

    def measure(self, part_name: str, part: FusePart) -> tuple[float, float]:
        total = moment = 0.0
        for f in _faces(part_name, part, self.face):
            bb = f.BoundingBox()
            a = (bb.xlen + 2 * self.margin) * (bb.ylen + 2 * self.margin)
            total += a
            moment += a * f.Center().x
        return total, moment / total


@dataclass(frozen=True)
class RolloverFaces:
    """The roll-over box's glass faces, measured on the part's planar faces (see core.fuselage_book)."""

    kind: str  # "inside" or "outside"
    lower_bound: bool = False
    note: str = ""

    def label(self) -> str:
        return f"roll-over {self.kind} faces"

    def measure(self, part_name: str, part: FusePart) -> tuple[float, float]:
        return fb.rollover_face_area(self.kind)


@dataclass(frozen=True)
class CornerTape:
    """A tape of stated width along the contact edge of the bottom with both sides."""

    width: float
    lower_bound: bool = True
    note: str = ""

    def label(self) -> str:
        return f"corner tape {self.width:g} in wide"

    def measure(self, part_name: str, part: FusePart) -> tuple[float, float]:
        length, arm = _side_contact(part)
        return self.width * length, arm


def _faces_all(part: FusePart, d: tuple[float, float, float], thr: float):
    return [
        f
        for f in part.solid.faces().vals()
        if f.normalAt().x * d[0] + f.normalAt().y * d[1] + f.normalAt().z * d[2] >= thr
    ]


def _side_contact(bottom: FusePart) -> tuple[float, float]:
    """Length (and x centroid) of the side-to-bottom contact: the sides' inside-face bottom edges
    from the front edge to the aft end of the bottom plate."""
    x_end = bottom.solid.val().BoundingBox().xmax
    parts = build_fuselage()
    total = 0.0
    moment = 0.0
    for side in ("side_left", "side_right"):
        p = parts[side]
        inside = _faces(side, p, "inside")
        low = _faces_all(p, (0.0, 0.0, -1.0), 0.9)
        for f in inside:
            for e in f.Edges():
                if not any(e.isSame(le) for lf in low for le in lf.Edges()):
                    continue
                n = 2000
                pts = [e.positionAt(i / n) for i in range(n + 1)]
                for a, b in pairwise(pts):
                    mx = (a.x + b.x) / 2
                    if mx > x_end:
                        continue
                    seg = math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))
                    total += seg
                    moment += seg * mx
    if total <= 0:
        raise FusePlyError("no side-to-bottom contact edge found")
    return total, moment / total


def corner_tape_length(part_name: str = "bottom") -> float:
    """Measured side-to-bottom contact length in inches (the tape is this long, width from the page)."""
    return _side_contact(build_fuselage()[part_name])[0]


Region = Face | ClipFace | PadMargin | RolloverFaces | CornerTape


# --- scope ----------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    part: str
    region: Region


@dataclass(frozen=True)
class Place:
    targets: tuple[Target, ...]
    angles: tuple[float | None, ...]  # ply i takes angles[i % len(angles)]
    cite: str


_P33, _P34, _P35, _P37, _P40, _P43, _P44 = (
    f"plans-1980:p{n}" for n in (33, 34, 35, 37, 40, 43, 44)
)


def _t(part: str, region: Region) -> Target:
    return Target(part, region)


_WRAP = "the wrap around the edges is not counted"
SCOPE: dict[tuple[str, str], Place] = {
    ("f04.front-seat-bkhd-front", "front face and tapered end, +/-45"): Place(
        (
            _t(
                "front_seat_bkhd",
                Face("fwd", lower_bound=True, note="tapered-end wrap not counted"),
            ),
        ),
        (45.0, -45.0),
        _P33,
    ),
    (
        "f04.front-seat-bkhd-back",
        "back face, 45 degrees, wrapped around the rounded edges",
    ): Place(
        (_t("front_seat_bkhd", Face("aft", lower_bound=True, note=_WRAP)),),
        (45.0,),
        _P33,
    ),
    ("f04.rear-seat-bkhd-foam", "one face, crossing at 45 degrees"): Place(
        (
            _t(
                "rear_seat_bkhd",
                Face(
                    "fwd",
                    note="the model's pocket is cut from the back, so the UND is on the front face; "
                    "the solid's face already lacks the 7 in hole",
                ),
            ),
        ),
        (45.0, -45.0),
        _P34,
    ),
    (
        "f04.rear-seat-bkhd-hole",
        "back face and into the 8 in circle where the foam was removed, 45 degrees",
    ): Place(
        (
            _t(
                "rear_seat_bkhd",
                Face(
                    "aft",
                    lower_bound=True,
                    note="p34 section C-C: the BID covers the back and runs down into the 8 in "
                    "circle; the pocket floor and walls are not counted",
                ),
            ),
        ),
        (45.0,),
        _P34,
    ),
    ("f04.panel-f22-f28-aft", "aft faces of panel, F22 and F28"): Place(
        tuple(_t(p, Face("aft")) for p in ("panel", "f22", "f28")),
        (None,),  # p34: fibre orientation is not critical
        _P34,
    ),
    ("f04.panel-f22-f28-fwd", "forward faces of panel, F22 and F28"): Place(
        tuple(_t(p, Face("fwd")) for p in ("panel", "f22", "f28")), (None,), _P34
    ),
    ("f04.firewall-aft", "aft face of the plywood"): Place(
        (_t("firewall", Face("aft")),), (None,), _P35
    ),
    ("f04.firewall-fwd", "front face of the firewall"): Place(
        (_t("firewall", Face("fwd")),), (None,), _P35
    ),
    ("f05.inside-layup", "inside face, crossing at +/-30 degrees"): Place(
        (_t("side_left", Face("inside")), _t("side_right", Face("inside"))),
        (30.0, -30.0),
        _P37,
    ),
    (
        "f06.bottom-glass",
        "whole bottom, 45 degrees, 1 in overlaps, 2 in excess at the aft end",
    ): Place(
        (
            _t(
                "bottom",
                Face(
                    "upper",
                    lower_bound=True,
                    note="1 in overlaps and the 2 in aft excess not counted",
                ),
            ),
        ),
        (45.0,),
        _P43,
    ),
    ("f06.bottom-tape", "all inside corners, 2 in wide, 45 degrees"): Place(
        (
            _t(
                "bottom",
                CornerTape(
                    2.0,
                    note="side corners only; bulkhead-to-bottom corners are not counted",
                ),
            ),
        ),
        (45.0,),
        _P44,
    ),
}

_SIDES = ("side_left", "side_right")
_NO_WIDTH = (
    "the row states no tape width (the page sketch labels it 2 ply BID tape only)"
)
EXCLUDED: dict[tuple[str, str], tuple[str, tuple[str, ...]]] = {
    ("f04.panel-f22-f28-aft", "over the wet doubler"): (
        "foam doubler outline is on a full-size sheet we do not hold and the doubler is not modelled",
        ("panel", "f22", "f28"),
    ),
    ("f04.panel-f22-f28-aft", "panel, above the leg cutouts"): (
        "extent above the leg cutouts is undimensioned and the model's cutouts are fitted",
        ("panel",),
    ),
    ("f04.panel-f22-f28-fwd", "upper panel, forward face, extra"): (
        "where 'upper panel' ends is undimensioned (panel outline is on a full-size sheet)",
        ("panel",),
    ),
    (
        "f04.panel-f22-f28-fwd",
        "F22 canard attach pad, left and right, forward face only",
    ): (
        "the pad is 5 in wide (p34) but its height is not printed, and F22's outline is on a sheet we do not hold",
        ("f22",),
    ),
    ("f05.top-longeron-glass", "along the 55 in stiffener"): (
        "the stiffener is 55 long (p37) but the page gives no width for the glass strip",
        _SIDES,
    ),
    ("f05.top-longeron-glass", "full 103 in length, 45 degrees, may be pieces"): (
        "the page gives no width for the 103 in strip",
        _SIDES,
    ),
    ("f05.gear-pad", "hatched pad area, 45 degrees"): (
        (
            "p38 gives only offsets from the aft end (15.3, 12, 6.2, 3.2); the hatched outline is "
            "undimensioned and the gear-pad solid is not modelled"
        ),
        _SIDES,
    ),
    ("f05.gear-pad", "gear pad stack, 45 degrees, ending at W.L. 12.35"): (
        "same undimensioned outline as the 6-ply pad; only its W.L. 12.35 top is stated",
        _SIDES,
    ),
    ("f06.bond-front-seat", "corner tapes, front seat bulkhead, 45 degrees"): (
        _NO_WIDTH,
        ("front_seat_bkhd", *_SIDES),
    ),
    ("f06.bond-panel", "corner tapes, instrument panel, 45 degrees"): (
        _NO_WIDTH,
        ("panel", *_SIDES),
    ),
    (
        "f06.f28-install",
        "over each doubler, 45 degrees, lapping about 0.4 onto F28, longeron and side",
    ): (
        "the ply covers a 1.0 x 0.7 x 3 wood doubler that is not modelled; only the 0.4 lap is stated",
        ("f28", *_SIDES),
    ),
    ("f06.rear-seat-tape", "rear seat bulkhead joint tape, 45 degrees"): (
        _NO_WIDTH,
        ("rear_seat_bkhd", *_SIDES),
    ),
    ("f06.bottom-glass", "rear seat entry area, extra"): (
        "extent of the rear seat entry area is undimensioned",
        ("bottom",),
    ),
}


# --- chapter 7 skins and chapter 8 roll-over / belt pads ------------------------------------------------
_P46, _P47, _P48, _P49 = (f"plans-1980:p{n}" for n in (46, 47, 48, 49))
_ANG = G.skin_ply_angle_deg
_WRAP_TOP = (
    "the wrap over the top longeron and the 0.5 in lap onto the firewall are not counted "
    "(neither is measured)"
)
_BOTTOM_AFT = (
    "the bottom foam behind the rear seat bulkhead is not modelled, so the skin there is not counted; "
    "the 0.5 in lap onto the firewall is not counted"
)
_HALF_OVERLAP = (
    G.skin_bottom_overlap / 2
)  # each skin runs this far past the centre line: 2 in overlap in all
_STRIP_FS = G.skin_third_ply_fs_range
_ROW_SKIN = "crossed 30 degrees to the longerons, whole skin"
_ROW_THIRD = "forward of the front seat bulkhead only, along the longerons"
_ROW_STRIP = "3 in strip, tapered 52/50/48 in, FS 60 to 110"
_STRIP_NOTE = (
    "tapered 52/50/48 in per ply on p46 (sum 150 = 3 x 50); the area uses the nominal 50 in (FS 60 to 110) for "
    "every ply, which is exact for the three plies together"
)


def _skin_place(side: str) -> dict[tuple[str, str], Place]:
    right = side == "right"
    op = f"f07.skin-{side}"
    part = f"side_{side}"
    y_lim = (-_HALF_OVERLAP, 50.0) if right else (-50.0, _HALF_OVERLAP)
    bottom = ClipFace(
        "lower",
        lower_bound=True,
        note=_BOTTOM_AFT,
        clip=("box", G.fs_f22 - 1.0, 300.0, y_lim[0], y_lim[1], -50.0, 50.0),
    )
    return {
        (op, _ROW_SKIN): Place(
            (
                _t(part, Face("outside", lower_bound=True, note=_WRAP_TOP)),
                _t("bottom", bottom),
            ),
            (_ANG, -_ANG),
            _P46,
        ),
        (op, _ROW_THIRD): Place(
            (
                _t(
                    part,
                    ClipFace(
                        "outside",
                        note="aft edge follows the front seat bulkhead's slanted line, FS 63.55 at the "
                        "floor to 81.75 at the top (derived from the config)",
                        clip=("fwd_of_front_bkhd",),
                    ),
                ),
            ),
            (0.0,),
            _P46,
        ),
        (op, _ROW_STRIP): Place(
            (
                _t(
                    part,
                    ClipFace(
                        "outside",
                        note=_STRIP_NOTE,
                        clip=(
                            "box",
                            _STRIP_FS[0],
                            _STRIP_FS[1],
                            -50.0,
                            50.0,
                            fb.Z_TOP - G.skin_strip_width,
                            fb.Z_TOP + 1.0,
                        ),
                    ),
                ),
            ),
            (None,),  # p46 does not print the strip's fibre direction
            _P46,
        ),
    }


SCOPE.update(_skin_place("right"))
SCOPE.update(_skin_place("left"))
SCOPE.update(
    {
        ("f08.roll-over-inside", "inside faces"): Place(
            (
                _t(
                    "rollover",
                    RolloverFaces(
                        "inside", note="edge faces and joint fillets not counted"
                    ),
                ),
            ),
            (None,),  # p48 does not print an orientation for the BID
            _P48,
        ),
        (
            "f08.roll-over-outside",
            "outside skin, 1 in overlap onto seat bulkhead and sides",
        ): Place(
            (
                _t(
                    "rollover",
                    RolloverFaces(
                        "outside",
                        lower_bound=True,
                        note="the 1 in lap onto the seat bulkhead and sides, the peak rounding and the edge "
                        "faces are not counted; the front piece's base on the bulkhead is not exposed",
                    ),
                ),
            ),
            (None,),
            _P48,
        ),
        ("f08.belt-attach", "each of 4 belt-attach pads"): Place(
            (
                _t(
                    "belt_attach",
                    PadMargin(
                        1.0,
                        note="p49 1 in all round the insert; the four pads summed; insert size is fitted",
                    ),
                ),
            ),
            (None,),
            _P49,
        ),
    }
)
EXCLUDED.update(
    {
        ("f08.roll-over-outside", "local reinforcement"): (
            "p48 names two plies of local reinforcement but does not say where or how large",
            ("rollover",),
        ),
        ("f08.roll-over-outside", "buildup over each of 3 inserts"): (
            "the 12-ply buildup's outline over each 1.25 in insert is not dimensioned",
            ("rollover", "rollover_inserts"),
        ),
        ("f08.roll-over-outside", "over the peak"): (
            "how far the 3 extra plies run down from the peak is not dimensioned (the peak is also radiused first)",
            ("rollover",),
        ),
        ("f08.shoulder-harness", "over the shoulder-harness pads"): (
            "the harness pads' outline is not dimensioned and the 4.0 insert spacing is not placeable",
            ("rollover", "rollover_inserts"),
        ),
    }
)


def material_rows(graph) -> list[tuple[str, str]]:
    return [
        (op_id, m["where"])
        for op_id, op in graph.ops.items()
        if op.chapter in CHAPTERS
        for m in op.materials
    ]


def scope_problems(rows, op_ids, scope=None, excluded=None) -> list[str]:
    scope = SCOPE if scope is None else scope
    excluded = EXCLUDED if excluded is None else excluded
    parts = build_fuselage()
    probs = []
    for key, place in scope.items():
        if key[0] not in op_ids:
            probs.append(f"SCOPE op {key[0]} is not in the graph")
        for t in place.targets:
            if t.part not in parts:
                probs.append(f"SCOPE {key[0]}: unknown part {t.part}")
    for key, (reason, affected) in excluded.items():
        if not reason or not affected:
            probs.append(
                f"EXCLUDED {key[0]} row {key[1]!r} needs a reason and affected parts"
            )
    for op_id, where in rows:
        key = (op_id, where)
        if key in scope and key in excluded:
            probs.append(f"{op_id} row {where!r} is both mapped and excluded")
        elif key not in scope and key not in excluded:
            probs.append(
                f"{op_id} row {where!r} is not in SCOPE or EXCLUDED (place it or exclude it with a reason)"
            )
    return probs


# --- plies ----------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FusePly:
    node: str
    part: str
    op: str
    op_index: int
    order: int
    cloth: str
    orientation_deg: float | None
    where: str
    region: str
    area_in2: float
    fidelity: str
    lower_bound: bool
    arm_in: float
    cite: str
    note: str = ""


def _load_graph():
    from guide.schema import load_graph  # lazy: core stays importable without the guide

    return load_graph(_GRAPH_DIR)


@lru_cache(maxsize=1)
def _default_plies() -> tuple[FusePly, ...]:
    return tuple(_plies(_load_graph(), None))


def plies(graph=None, extra_rows: list[tuple[str, str]] | None = None) -> list[FusePly]:
    """One FusePly per ply of every mapped row, in build order (cached for the committed graph)."""
    if graph is None and not extra_rows:
        return list(_default_plies())
    return _plies(graph if graph is not None else _load_graph(), extra_rows)


def _plies(graph, extra_rows) -> list[FusePly]:
    rows = material_rows(graph) + list(extra_rows or [])
    probs = scope_problems(rows, set(graph.ops))
    if probs:
        raise FusePlyError("; ".join(probs))
    parts = build_fuselage()
    measured: dict[tuple[str, Region], tuple[float, float]] = {}
    chapter_ops = [op_id for op_id, op in graph.ops.items() if op.chapter in CHAPTERS]
    order_of: dict[str, int] = {}
    out: list[FusePly] = []
    for op_index, op_id in enumerate(chapter_ops):
        for m in graph.ops[op_id].materials:
            place = SCOPE.get((op_id, m["where"]))
            if place is None:
                continue
            for k in range(int(m["plies"])):
                for t in place.targets:
                    mk = (t.part, t.region)
                    if mk not in measured:
                        measured[mk] = t.region.measure(t.part, parts[t.part])
                    area, arm = measured[mk]
                    order = order_of[t.part] = order_of.get(t.part, 0) + 1
                    out.append(
                        FusePly(
                            node=f"fuselage.{t.part}.p{order}",
                            part=t.part,
                            op=op_id,
                            op_index=op_index,
                            order=order,
                            cloth=m["cloth"],
                            orientation_deg=place.angles[k % len(place.angles)],
                            where=m["where"],
                            region=t.region.label(),
                            area_in2=area,
                            fidelity=parts[t.part].fidelity,
                            lower_bound=t.region.lower_bound,
                            arm_in=arm,
                            cite=place.cite,
                            note=t.region.note,
                        )
                    )
    return out


def region_of(p: FusePly) -> Region:
    """The Region object a ply was measured on (its SCOPE target for its part). The lab export builds the ply's
    shell on it, so the geometry and the area come from the same selection."""
    place = SCOPE[(p.op, p.where)]
    for t in place.targets:
        if t.part == p.part:
            return t.region
    raise FusePlyError(f"{p.node}: part {p.part} is not a target of {p.op}")


def region_direction(part_name: str, face_name: str) -> tuple[float, float, float]:
    """The direction a ``Face(face_name)`` region's faces point (the rule the faces are picked by)."""
    return _direction(part_name, face_name)


def region_faces(part_name: str, face_name: str):
    """The faces of a part solid that a ``Face(face_name)`` region measures (same normal rule as the areas)."""
    return _faces(part_name, build_fuselage()[part_name], face_name)


def region_shape_faces(p: FusePly) -> list:
    """The faces a ply's region covers (clipped faces for a ClipFace). Only Face-family regions have them."""
    reg = region_of(p)
    if not isinstance(reg, Face):
        raise FusePlyError(f"{p.node}: region {reg.label()} is not a face region")
    return reg.faces(p.part)


def skin_shell(side: str) -> cq.Workplane:
    """A thin solid over the region the skin's two crossed plies cover on ``side`` ('right' or 'left').

    The side's outside face plus the bottom's outer face from that side to 1 in past the centre line, offset
    outward by two UND plies' cured thickness (config uni_ply_thickness). Representational as a shape: the
    thickness is the cured ply stack, the covered region is the same selection the ply area is measured on, and the
    wrap over the top longeron is not drawn.
    """
    if side not in ("right", "left"):
        raise FusePlyError(f"side must be 'right' or 'left', not {side!r}")
    place = SCOPE[(f"f07.skin-{side}", _ROW_SKIN)]
    t = 2 * config.materials.uni_ply_thickness
    solids = []
    for tgt in place.targets:
        for f in tgt.region.faces(tgt.part):
            solids.append(f.thicken(t))
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solids))


def excluded_by_part() -> dict[str, list[str]]:
    """Excluded rows per affected part, as 'op: where' strings (glass there is not complete)."""
    out: dict[str, list[str]] = {}
    for (op_id, where), (_, affected) in EXCLUDED.items():
        for p in affected:
            out.setdefault(p, []).append(f"{op_id}: {where}")
    return out


def ply_summary(pl: list[FusePly]) -> dict[str, Any]:
    by: dict[str, dict[str, Any]] = {}
    for p in pl:
        d = by.setdefault(p.part, {"count": {}, "area": {}})
        d["count"][p.cloth] = d["count"].get(p.cloth, 0) + 1
        d["area"][p.cloth] = d["area"].get(p.cloth, 0.0) + p.area_in2
    return by
