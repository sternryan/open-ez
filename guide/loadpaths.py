"""Qualitative load-path polylines, computed from the same CadQuery solids the glb is exported from.

COORDINATE FRAME (decision): points are in the frame of the `guide.layup_geometry.build_layup` solids,
in inches: X chordwise aft, Y = B.L. (span, right half), Z up. They are NOT world coordinates.
`guide.export_glb` writes those solids into the glb under a root node rotated -90 deg about X, so in the
viewer's three.js world (X chord, Y up, B.L. b at Z = -b) the same rotation maps (x, y, z) to (x, z, -y).
The viewer parents the lines under a group carrying exactly that rotation; nothing here is pre-rotated.

Shape: every path is a list of `segments`, each a polyline `[[x, y, z], ...]`. (The plan's single `points`
list could not draw the two spar caps, or four separate lift stations, without a line through air.)
These are qualitative lines, not stress paths. Tolerance: every point, and every segment midpoint, lies within 0.5 in of the
compound of the path's parts (distance to the union of all listed parts, not to each part in turn); the tests enforce it.

    cap-bending      one 9-point polyline per cap (8 steps, BL 0 -> the cap's end), through the cap section centre
    web-shear        one 9-point polyline along the shear web's mid-height, BL 0 -> the web's end
    lift-into-caps   per station (4) and side (top, bottom): a chordwise 2-point segment, mid-skin -> cap centre

Section centres are the bounding-box centre of a thin slab (SLAB in) cut out of the part's base ply (the
ply that runs furthest along the span), so a ply ending mid-span never makes the line jump.
"""

from __future__ import annotations

import cadquery as cq

from guide.layup_geometry import build_layup

STEPS = 8  # cap-bending and web-shear: 8 steps = 9 points
LIFT_STATIONS = 4  # lift-into-caps: stations spaced evenly along the caps
LIFT_REACH = (
    3.0  # in: how far aft of the cap centre the skin end of a lift segment sits
)
SLAB = 0.02  # in: thickness of the sectioning slab
BIG = 100.0


def _solids(built: dict, cid: str) -> list:
    v = built[cid]
    return list(v.values()) if isinstance(v, dict) else [v]


def _base(built: dict, cid: str):
    """The ply running furthest along the span (lowest ply order on a tie)."""
    return max(
        _solids(built, cid), key=lambda s: round(s.BoundingBox().ymax, 6)
    )  # max keeps the first of equals


def _end(built: dict, cid: str) -> float:
    return max(s.BoundingBox().ymax for s in _solids(built, cid))


def _centre(solids: list, bl: float, x: float | None = None) -> list[float]:
    """Bounding-box centre of `solids` cut by a thin slab at B.L. `bl` (and, if given, a thin chordwise slab at `x`)."""
    y0 = max(bl - SLAB, 0.0)
    xs = (-BIG, BIG) if x is None else (x - SLAB, x + SLAB)
    slab = (
        cq.Workplane("XY")
        .box(xs[1] - xs[0], SLAB, 2 * BIG, centered=False)
        .translate((xs[0], y0, -BIG))
        .val()
    )
    boxes = [cut.BoundingBox() for s in solids if (cut := s.intersect(slab)).Solids()]
    if not boxes:
        raise ValueError(
            f"no material at B.L. {bl}" + ("" if x is None else f", x {x}")
        )
    lo = [min(b.xmin for b in boxes), min(b.zmin for b in boxes)]
    hi = [max(b.xmax for b in boxes), max(b.zmax for b in boxes)]
    return [round((lo[0] + hi[0]) / 2, 4), round(bl, 4), round((lo[1] + hi[1]) / 2, 4)]


def _along(built: dict, cid: str) -> list[list[float]]:
    base, end = _base(built, cid), _end(built, cid)
    return [_centre([base], end * i / STEPS) for i in range(STEPS + 1)]


def _lift(built: dict, skin: str, cap: str) -> list[list[list[float]]]:
    base, end = _base(built, cap), _end(built, cap)
    out = []
    for i in range(LIFT_STATIONS):
        bl = end * (i + 0.5) / LIFT_STATIONS
        c = _centre([base], bl)
        out.append([_centre(_solids(built, skin), bl, x=c[0] + LIFT_REACH), c])
    return out


def polylines(graph, built: dict | None = None) -> dict[str, dict]:
    """{path_id: {"label", "kind", "parts", "segments"}}; `built` is build_layup(graph) (computed if omitted)."""
    built = built if built is not None else build_layup(graph)
    out = {}
    for lp in graph.loadpaths:
        if lp.id == "cap-bending":
            segs = [
                _along(built, c)
                for c in ("canard.spar_cap_top", "canard.spar_cap_bottom")
            ]
        elif lp.id == "web-shear":
            segs = [_along(built, "canard.shear_web")]
        elif lp.id == "lift-into-caps":
            segs = _lift(built, "canard.skin_top", "canard.spar_cap_top") + _lift(
                built, "canard.skin_bottom", "canard.spar_cap_bottom"
            )
        else:
            raise ValueError(f"no geometry rule for load path {lp.id}")
        out[lp.id] = {
            "label": lp.label,
            "kind": lp.kind,
            "parts": list(lp.parts),
            "segments": segs,
        }
    return out
