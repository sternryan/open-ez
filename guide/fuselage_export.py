"""The fuselage box (plans chapters 4-6) for the lab: part solids, ply shells and the layup.json section.

    core.fuselage_book.build_fuselage() ─► one glb node per part  (fuselage.<part>)
    core.fuselage_plies.plies()         ─► one child per ply      (fuselage.<part>.p<n>), a thin shell on the
                                           same faces the ply's area is measured on (region_of / region_faces)
                                        ─► layup.json "fuselage" (ops, parts, nodes, excluded rows, plan bend)

Frame (as exported, inches): x = FS, y = B.L., z = W.L. - 17.4, the frame core.fuselage_book builds in.
Ply thickness is VISUAL, not to scale (a cured BID ply is about 0.01 in); plies stack outward from their face in
the order they are laid on it. Every part and ply carries the part's fidelity; a representational part's label
says "fitted shape".
"""
from __future__ import annotations

from functools import lru_cache

import cadquery as cq

from core import fuselage_plies as fp
from core.fuselage_book import (
    FusePart,
    build_fuselage,
    half_width,
    part_name,
    plan_bend_points,
)

CHAPTERS = (4, 5, 6)
BULKHEADS = ("front_seat_bkhd", "rear_seat_bkhd", "f22", "f28", "panel", "firewall")
PLY_T = 0.06  # in, VISUAL: thick enough to read in the section cut; not the cured thickness

# The graph's component for a part (guide/graph/components.yaml). Both top longerons belong to one component.
_COMPONENT = {"top_longeron_left": "fuselage.longerons", "top_longeron_right": "fuselage.longerons"}


def part_label(name: str, part: FusePart) -> str:
    """The lab's label: the plain name (core.fuselage_book.PART_NAMES), plus " (fitted shape)" for a representational part."""
    base = part_name(name)
    return base + " (fitted shape)" if part.fidelity == "representational" else base


def component_of(name: str) -> str:
    return _COMPONENT.get(name, f"fuselage.{name}")


def _stack_dir(part_name: str, face: cq.Face, rule: str) -> cq.Vector:
    """Which way plies stack off a face: its own normal when it is flat, else the region's rule direction."""
    if face.geomType() == "PLANE":
        return face.normalAt()
    return cq.Vector(*fp.region_direction(part_name, rule))


def _face_shell(part_name: str, face_name: str, stack: int) -> cq.Workplane:
    solids = []
    for f in fp.region_faces(part_name, face_name):
        n = _stack_dir(part_name, f, face_name)
        solids.append(f.translate(n * (PLY_T * (stack - 1))).thicken(PLY_T))
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solids))


def _tape_shell(part_name: str, tape: fp.CornerTape, stack: int) -> cq.Workplane:
    """The corner tape drawn as its leg on the bottom: a band tape.width / 2 wide inboard of each side's inside face.

    The leg up the side is not drawn (the area in layup.json is the measured contact length times the full width).
    """
    (face,) = fp.region_faces(part_name, "upper")
    shell = face.translate(cq.Vector(0, 0, PLY_T * (stack - 1))).thicken(PLY_T)
    bb = shell.BoundingBox()
    xs = [bb.xmin + i * 1.0 for i in range(int(bb.xmax - bb.xmin) + 1)] + [bb.xmax]
    leg = tape.width / 2
    band = None
    for sgn in (1, -1):
        outer = [(x, sgn * half_width(x)) for x in xs]
        inner = [(x, sgn * (half_width(x) - leg)) for x in reversed(xs)]
        prism = cq.Workplane("XY", origin=(0, 0, bb.zmin - 1)).polyline(outer + inner).close().extrude(bb.zmax - bb.zmin + 2)
        band = prism if band is None else band.union(prism)
    return cq.Workplane("XY").add(shell).intersect(band)


@lru_cache(maxsize=1)
def _shells() -> tuple[tuple[str, cq.Workplane, int], ...]:
    out = []
    seen: dict[tuple[str, str], int] = {}
    for p in fp.plies():
        reg = fp.region_of(p)
        base = reg.name if isinstance(reg, fp.Face) else "upper"  # a corner tape lies over the bottom's glass
        k = seen[(p.part, base)] = seen.get((p.part, base), 0) + 1
        shell = _face_shell(p.part, reg.name, k) if isinstance(reg, fp.Face) else _tape_shell(p.part, reg, k)
        out.append((p.node, shell, k))
    return tuple(out)


def ply_shells() -> dict[str, cq.Workplane]:
    """Ply node -> its thin solid (cached)."""
    return {node: shell for node, shell, _ in _shells()}


def components() -> dict:
    """glb components: a part with plies is (solid, {ply node: shell}); a part without plies is its solid."""
    # Deep copies: the glTF export tessellates what it is given, and a triangulation left on the cached part solids changes their
    # bounding boxes (BoundingBox uses it) for anything that measures them later in the same process.
    shells = ply_shells()
    by_part: dict[str, dict] = {}
    for p in fp.plies():
        by_part.setdefault(p.part, {})[p.node] = shells[p.node].val().copy()
    return {f"fuselage.{name}": ((part.solid.val().copy(), by_part[name]) if name in by_part else part.solid.val().copy())
            for name, part in build_fuselage().items()}


def _xrange(wp: cq.Workplane) -> tuple[float, float]:
    bb = wp.val().BoundingBox() if len(wp.vals()) == 1 else cq.Compound.makeCompound(wp.vals()).BoundingBox()
    return bb.xmin, bb.xmax


def layup_section() -> dict:
    """layup.json["fuselage"]: what the lab needs to lay, place, label and cut the chapter 4-6 plies."""
    parts = build_fuselage()
    pl = fp.plies()
    stack = {node: k for node, _, k in _shells()}
    shells = ply_shells()
    ops: list[str] = []
    lay: dict[str, int] = {}
    nodes = {}
    for p in pl:
        if p.op not in ops:
            ops.append(p.op)
        lay[p.op] = lay.get(p.op, 0) + 1
        x0, x1 = _xrange(shells[p.node])
        nodes[p.node] = {
            "part": p.part, "component": component_of(p.part), "op": p.op, "op_index": ops.index(p.op),
            "op_order": lay[p.op], "order": p.order, "stack": stack[p.node], "cloth": p.cloth,
            "orientation_deg": p.orientation_deg, "where": p.where, "region": p.region, "fidelity": p.fidelity,
            "lower_bound": p.lower_bound, "area_in2": round(p.area_in2, 3), "fs_min": round(x0, 4), "fs_max": round(x1, 4),
        }
    part_rows = {}
    for name, part in parts.items():
        x0, x1 = _xrange(part.solid)
        fwd = None
        if name in BULKHEADS:  # the lab lays a bulkhead flat with its forward or aft face up
            n = fp.region_faces(name, "fwd")[0].normalAt()
            fwd = [round(n.x, 6), round(n.y, 6), round(n.z, 6)]
        part_rows[name] = {
            "node": f"fuselage.{name}", "component": component_of(name), "fidelity": part.fidelity,
            "label": part_label(name, part), "cite": list(part.cite), "fs_min": round(x0, 4), "fs_max": round(x1, 4),
            "fwd_normal": fwd,
        }
    excluded = [{"op": op, "where": where, "reason": reason, "parts": list(affected)}
                for (op, where), (reason, affected) in fp.EXCLUDED.items()]
    return {
        "chapters": list(CHAPTERS),
        "frame": "inches as exported: x = FS, y = B.L., z = W.L. - 17.4",
        "ply_thickness_in": PLY_T,
        "ply_thickness_note": "visual, not to scale",
        "ops": ops,
        "parts": part_rows,
        "nodes": nodes,
        "excluded": excluded,
        "plan_bend": [[round(x, 4), round(h, 4)] for x, h in plan_bend_points()],
    }
