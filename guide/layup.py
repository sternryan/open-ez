"""Layup data for the M2 cutaway: parse ch30 ply rows, scope them, expand plies, derive shots.

Pure Python (no CadQuery) so the site build can use it without geometry.

    ch30.yaml materials ─parse_where─► Ply(component, op, cloth, order, bl_max)
          │                                 │
    LAYUP_SCOPE (included ops,              ├─► counts_at(bl) ─► alt text, acceptance counts
    excluded rows with reasons)             ├─► shots() ─► shots.json (hero + one per op)
                                            └─► layup_json() ─► layup.json (glb node → ply)
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass


class LayupError(ValueError):
    pass


ORIENTATIONS = frozenset({"crossed", "45 degrees", "spanwise"})
_EXTENTS = (
    (re.compile(r"full span \((\d+(?:\.\d+)?) in\)"), lambda m: float(m.group(1)) / 2),
    (re.compile(r"full span"), lambda m: None),
    (re.compile(r"inboard of BL (\d+(?:\.\d+)?)"), lambda m: float(m.group(1))),
    (re.compile(r"first ply|last ply|final plies"), lambda m: None),
)

# Build order; op frames and op_index follow it.
INCLUDED_OPS = ("r30.shear-web", "r30.bottom-spar-cap", "r30.bottom-skin", "r30.top-spar-cap", "r30.top-skin")
OP_COMPONENT = {
    "r30.shear-web": "canard.shear_web",
    "r30.bottom-spar-cap": "canard.spar_cap_bottom",
    "r30.bottom-skin": "canard.skin_bottom",
    "r30.top-spar-cap": "canard.spar_cap_top",
    "r30.top-skin": "canard.skin_top",
}
SPAR_CAP_OPS = frozenset({"r30.bottom-spar-cap", "r30.top-spar-cap"})
SPAR_CAP_BL_MAX = 54.0  # troughs run the inboard cores only; the tip cores have none (cobelu ch 30)
SPAR_CAP_WHERE = "3 in UND tape, plies as required to fill trough (tapered)"
_LOCAL = "local feature, not at a section station"
EXCLUDED_ROWS = {
    ("r30.shear-web", "pad over each CL-1 nut plate"): f"CL-1 nut-plate pads: {_LOCAL}",
    ("r30.align-canard", "forward face of each rear tab"): f"rear tab: {_LOCAL}",
    ("r30.align-canard", "aft face of each rear tab"): f"rear tab: {_LOCAL}",
}
LAYUP_CHAPTER = 30  # the cutaway is the Roncz canard (ch 30); other chapters' rows (e.g. ch 10, the GU canard) are out of scope
HERO_BLS = (5.0, 40.0)
OP_FRAME_BL = 5.0
UNVERIFIED_POSITION = frozenset({"canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"})
_LABEL = {"canard.skin_bottom": "bottom skin", "canard.skin_top": "top skin", "canard.shear_web": "shear web"}


def parse_where(where: str) -> tuple[str, float | None]:
    parts = [p.strip() for p in where.split(",")]
    if len(parts) != 2 or parts[0] not in ORIENTATIONS:
        raise LayupError(f"unrecognised ply location {where!r}")
    for rx, extent in _EXTENTS:
        m = rx.fullmatch(parts[1])
        if m:
            return parts[0], extent(m)
    raise LayupError(f"unrecognised ply extent {where!r}")


def material_rows(graph) -> list[tuple[str, str]]:
    return [(op_id, m["where"]) for op_id, op in graph.ops.items() if op.chapter == LAYUP_CHAPTER
            for m in op.materials]


def scope_problems(rows, op_ids) -> list[str]:
    probs = [f"LAYUP_SCOPE op {o} is not in the graph" for o in INCLUDED_OPS if o not in op_ids]
    for op_id, where in rows:
        if (op_id, where) in EXCLUDED_ROWS:
            continue
        if op_id not in INCLUDED_OPS:
            probs.append(f"{op_id} row {where!r} is not in LAYUP_SCOPE (include the op or exclude the row)")
            continue
        try:
            parse_where(where)
        except LayupError as e:
            probs.append(f"{op_id}: {e}")
    return probs


@dataclass(frozen=True)
class Ply:
    node: str
    component: str
    op: str
    op_index: int
    order: int
    cloth: str
    orientation: str
    where: str
    bl_max: float | None
    position_verified: bool


def plies(graph) -> list[Ply]:
    probs = scope_problems(material_rows(graph), set(graph.ops))
    if probs:
        raise LayupError("; ".join(probs))
    out: list[Ply] = []
    for op_index, op_id in enumerate(INCLUDED_OPS):
        cid = OP_COMPONENT[op_id]
        verified = cid not in UNVERIFIED_POSITION
        if op_id in SPAR_CAP_OPS:
            out.append(Ply(f"{cid}.p1", cid, op_id, op_index, 1, "UND", "spanwise", SPAR_CAP_WHERE,
                           SPAR_CAP_BL_MAX, False))
            continue
        order = 0
        for m in graph.ops[op_id].materials:
            if (op_id, m["where"]) in EXCLUDED_ROWS:
                continue
            orientation, bl_max = parse_where(m["where"])
            for _ in range(int(m["plies"])):
                order += 1
                out.append(Ply(f"{cid}.p{order}", cid, op_id, op_index, order, m["cloth"], orientation,
                               m["where"], bl_max, verified))
    return out


def counts_at(pl, bl: float) -> dict[str, int]:
    c: dict[str, int] = {}
    for p in pl:
        if p.bl_max is None or bl <= p.bl_max:
            c[p.component] = c.get(p.component, 0) + 1
    return c


def shot_id_for_op(op_id: str) -> str:
    return "op-" + re.sub(r"[^a-z0-9]+", "-", op_id.lower()).strip("-")


def shots() -> list[dict]:
    s = [{"id": f"hero-bl{int(b)}", "kind": "hero", "bl": b, "highlight": None, "upto": None} for b in HERO_BLS]
    s += [{"id": shot_id_for_op(op), "kind": "op", "bl": OP_FRAME_BL, "highlight": op, "upto": i}
          for i, op in enumerate(INCLUDED_OPS)]
    return s


def alt_text(graph, pl, shot: dict) -> str:
    if shot["kind"] == "hero":
        c = counts_at(pl, shot["bl"])
        parts = [f"{_LABEL[k]} {c.get(k, 0)} plies" for k in ("canard.skin_bottom", "canard.skin_top", "canard.shear_web")]
        return f"Section at BL {shot['bl']:g}: " + ", ".join(parts) + ", spar caps filled to the trough (not to scale)"
    title = graph.ops[shot["highlight"]].title
    return f"After {title}: its plies accented, later steps not yet laid (not to scale)"


def count_note(pl) -> str:
    a, b = (counts_at(pl, bl) for bl in HERO_BLS)
    return (f"What to count: bottom skin {a['canard.skin_bottom']}, top skin {a['canard.skin_top']} at both "
            f"stations; shear web {a['canard.shear_web']} at BL {HERO_BLS[0]:g}, "
            f"{b['canard.shear_web']} at BL {HERO_BLS[1]:g}.")


def layup_json(pl, semi_span: float) -> dict:
    return {"ops": list(INCLUDED_OPS), "semi_span": semi_span,
            "nodes": {p.node: {k: v for k, v in dataclasses.asdict(p).items() if k != "node"} for p in pl}}
