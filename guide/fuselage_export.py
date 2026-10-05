"""The fuselage box and main gear (plans chapters 4-9) for the lab: part solids, ply shells and the layup.json section.

    core.fuselage_book.build_fuselage() ─► one glb node per part  (fuselage.<part>)
    core.landing_gear_book.build_gear() ─► one glb node per part  (gear.<part>)
    core.fuselage_plies.plies()         ─► one child per ply      (fuselage.<part>.p<n>), a thin shell on the
                                           same faces the ply's area is measured on (region_of / region_faces)
                                        ─► layup.json "fuselage" (ops, parts, nodes, stages, excluded rows, plan bend)

Frame (as exported, inches): x = FS, y = B.L., z = W.L. - 17.4, the frame core.fuselage_book builds in. The gear is
exported upright (hanging under the box); the lab turns the whole box over for chapter 9.

Ply thickness is VISUAL, not to scale (a cured BID ply is about 0.01 in); plies stack outward from their face in
the order they are laid on it. Every part and ply carries the part's fidelity; a representational part's label
says "fitted shape".

Stages. A few chapter 7-8 ops change a shape that already exists: the corners are carved round (f07.carve-corners),
the canard opening comes out of the sides, longerons and F22 (f07.canard-cutout, and out of every ply laid on them
before it), and the roll-over gets its two access holes (f08.access-holes). The part's own node carries its shape
before the op; the shape after it is a separate top-level node (`<node>~carved`, `~cut`, `~holes`), and
layup.json "stages" says from which op the lab shows it instead. The carved corners themselves are a thin
representational band over the rounded faces (`carved_corners`), so the fitted radius is striped while the sides'
book faces are not.
"""

from __future__ import annotations

from functools import lru_cache

import cadquery as cq

from config import config
from core import fuselage_book as fb
from core import fuselage_plies as fp
from core.fuselage_book import (
    FusePart,
    build_fuselage,
    half_width,
    part_name,
    plan_bend_points,
)

G = config.geometry
CHAPTERS = (4, 5, 6, 7, 8, 9)
EXPORT_CHAPTERS = CHAPTERS  # the lab shows chapters 4-9; every chapter 4-8 ply is exported (chapter 9 has no ply model)
BULKHEADS = ("front_seat_bkhd", "rear_seat_bkhd", "f22", "f28", "panel", "firewall")
PLY_T = (
    0.06  # in, VISUAL: thick enough to read in the section cut; not the cured thickness
)
CARVE_T = 0.05  # in, VISUAL: the carved-corner band's thickness over the rounded faces

CARVE_OP, CUTOUT_OP, HOLES_OP = (
    "f07.carve-corners",
    "f07.canard-cutout",
    "f08.access-holes",
)
# the parts the canard opening cuts (core.fuselage_book._canard_cutout); F28 stays
CUT_PARTS = (
    "side_left",
    "side_right",
    "top_longeron_left",
    "top_longeron_right",
    "f22",
)
# Chapter 7 rolls the box: the right skin goes on at "45 degrees of left bank" (plans-1980:p46), the left skin at 45 of right bank.
# Sign as core.landing_gear_book.bank_pose: positive degrees = left bank, the right side up. The book's words are "45 degrees of
# left bank"; the captain's reading: the side AND the bottom being glassed both face up 45 degrees (the right skin covers the right
# side and the bottom to 1 in past the centre line, and the glass falls off an overhanging face), so the box is rolled 135 degrees
# from upright (45 degrees past on its side, resting on its top-left corner). Judgement call, flagged for the owner.
BANK_DEG = {"f07.skin-right": 135.0, "f07.skin-left": -135.0}

# The graph's component for a part (guide/graph/components.yaml). Both top longerons belong to one component; the carved
# band is the box's own skin of foam, made in the carve op whose components are the sides and bottom.
_COMPONENT = {
    "top_longeron_left": "fuselage.longerons",
    "top_longeron_right": "fuselage.longerons",
    "carved_corners": "fuselage.bottom",
    # gear (chapter 9, and the chapter 5 extrusions): components.yaml ids
    "strut": "gear.strut",
    "extrusions": "fuselage.gear_extrusions",
    "gear_tubes": "fuselage.gear_extrusions",
    "jig_blocks": "gear.jig_blocks",
    "datum_board": "gear.datum_board",
    "axles": "gear.axles",
}
GEAR_NAMES = {
    "strut": "Main gear strut",
    "extrusions": "Gear extrusions",
    "gear_tubes": "Gear tubes",
    "jig_blocks": "Gear jig blocks",
    "datum_board": "Datum boards at the spar aft face",
    "axles": "Axles",
}
_NAMES = {"carved_corners": "Carved corners"}
# When the lab shows a part that is not simply "from its component's first op on": a window of ops (until is exclusive),
# or one op only. Nothing selected (the finished box) shows a part only if it has no `until` and no `only`.
SHOW = {
    "canard_cutout": {
        "only": CUTOUT_OP
    },  # the material the opening removes, lifted out at its op
    "carved_corners": {"from": CARVE_OP},
    "gear_tubes": {
        "from": "f09.jig-blocks"
    },  # bolted between the angles with the jig blocks (p50, p53)
    "jig_blocks": {
        "until": "f09.tab-layup"
    },  # a tool: Bondo'd for the leg's positioning, gone once the tabs are laid
    "datum_board": {
        "until": "f09.tab-layup"
    },  # a tool: the straight edge the axle is measured from
}
# chapter 9's material rows: the strut and its tabs are not modelled as plies (the strut outline is not printed)
_CH9_REASON = {
    "f09.strut-stiffen": "the strut's outline is not printed (strut mold), so the 8 UND wrap has no measured face; the strut is a fitted shape",
    "f09.tab-layup": "the tab pads sit on the fitted strut; the pads' sizes are printed but not where they land on it",
    "f09.tab-assembly": "the wraps and washer plies go round the tubes and washers, which are not placed on a printed outline",
    "f09.axles-brakes": "the lower leg's faces are fitted (strut mold not printed)",
    "f09.brake-lines": "the brake line's path along the fitted strut is not measured",
}


@lru_cache(maxsize=1)
def _gear() -> dict[str, FusePart]:
    from core.landing_gear_book import (
        build_gear,
    )  # lazy: the canard-only callers never build the gear

    return build_gear()


def is_gear(name: str) -> bool:
    return name in _COMPONENT and _COMPONENT[name].startswith(
        ("gear.", "fuselage.gear_")
    )


def node_of(name: str) -> str:
    """The glb node of a part: `gear.<part>` for the landing gear, `fuselage.<part>` for the box."""
    return f"gear.{name}" if is_gear(name) else f"fuselage.{name}"


def _plies() -> list[fp.FusePly]:
    """The plies of the exported chapters (a ply's op id starts with its chapter, f04 to f08)."""
    keep = tuple(f"f{c:02d}." for c in EXPORT_CHAPTERS)
    return [p for p in fp.plies() if p.op.startswith(keep)]


def _carved_band() -> FusePart:
    """The rounded faces the carve leaves on the sides and the bottom (core.fuselage_book.carved_box), as a thin shell."""
    solids = []
    for part in fb.carved_box().values():
        for f in part.solid.faces().vals():
            n = f.normalAt()
            if (
                f.geomType() != "PLANE" and abs(n.y) > 0.3 and abs(n.z) > 0.3
            ):  # a fillet: neither a side, top nor bottom face
                solids.append(f.thicken(CARVE_T))
    return FusePart(
        "carved_corners",
        cq.Workplane("XY").add(cq.Compound.makeCompound(solids)),
        "representational",
        note=f"the rounded faces of the carve (radius {fb.FITTED_CORNER_RADIUS} fitted, template A2 not held), drawn {CARVE_T} in thick",
    )


@lru_cache(maxsize=1)
def _all_parts() -> tuple[tuple[str, FusePart], ...]:
    parts = dict(build_fuselage())
    parts["carved_corners"] = _carved_band()
    parts.update(_gear())
    return tuple(parts.items())


def _parts() -> dict[str, FusePart]:
    """Every exported part by name: the box (chapters 4-8, the canard opening's removed material included), the carved band, the gear."""
    return dict(_all_parts())


def part_label(name: str, part: FusePart) -> str:
    """The lab's label: the plain name (core.fuselage_book.PART_NAMES), plus " (fitted shape)" for a representational part."""
    base = GEAR_NAMES.get(name) or _NAMES.get(name) or part_name(name)
    return base + " (fitted shape)" if part.fidelity == "representational" else base


def component_of(name: str) -> str:
    return _COMPONENT.get(name, f"fuselage.{name}")


# ---- shells ----------------------------------------------------------------------------------------
def _stack_dir(part_name: str, face: cq.Face, rule: str) -> cq.Vector:
    """Which way plies stack off a face: its own normal when it is flat, else the region's rule direction."""
    if face.geomType() == "PLANE":
        return face.normalAt()
    return cq.Vector(*fp.region_direction(part_name, rule))


def _face_shell(part_name: str, region: fp.Face, stack: int) -> cq.Workplane:
    solids = []
    for f in region.faces(
        part_name
    ):  # a ClipFace gives its clipped faces: the shell covers exactly what is measured
        n = _stack_dir(part_name, f, region.name)
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
        prism = (
            cq.Workplane("XY", origin=(0, 0, bb.zmin - 1))
            .polyline(outer + inner)
            .close()
            .extrude(bb.zmax - bb.zmin + 2)
        )
        band = prism if band is None else band.union(prism)
    return cq.Workplane("XY").add(shell).intersect(band)


def rollover_glass_faces(kind: str) -> list[cq.Face]:
    """The roll-over's glass faces, the same selection core.fuselage_book._rollover_faces measures (a test checks the areas)."""
    pc = fb.rollover_pieces()
    zs = pc["z_shoulder"]
    out: list[cq.Face] = []

    def planar(shape):
        return [
            f
            for f in shape.faces().vals()
            if f.geomType() == "PLANE" and f.Area() >= 1.0
        ]

    def dot(f, n):
        nf = f.normalAt()
        return nf.x * n[0] + nf.y * n[1] + nf.z * n[2]

    if kind == "inside":
        out += [f for f in planar(pc["plate"]) if f.normalAt().x > 0.999]
    else:
        above = pc["plate_full"].intersect(fb._box(0, 500, -50, 50, zs, zs + 100))
        out += [f for f in planar(above) if f.normalAt().x < -0.999]
    for t in pc["tops"]:
        out += [
            f
            for f in planar(t)
            if (f.normalAt().z < -0.999 if kind == "inside" else f.normalAt().z > 0.999)
        ]
    for sgn, roof in zip((-1, 1), pc["roofs"]):
        n = pc["roof_geom"][sgn]["n"]
        out += [
            f
            for f in planar(roof)
            if (dot(f, n) < -0.999 if kind == "inside" else dot(f, n) > 0.999)
        ]
    nt = pc["tri_normal"]
    out += [
        f
        for f in planar(pc["triangle"])
        if (dot(f, nt) < -0.999 if kind == "inside" else dot(f, nt) > 0.999)
    ]
    return out


def _rollover_shell(kind: str, stack: int) -> cq.Workplane:
    """Plies on the roll-over's inside or outside faces, stacked off each face along its own outward normal (away from the foam)."""
    solids = [
        f.translate(f.normalAt() * (PLY_T * (stack - 1))).thicken(PLY_T)
        for f in rollover_glass_faces(kind)
    ]
    return cq.Workplane("XY").add(cq.Compound.makeCompound(solids))


def _pad_shell(part_name: str, pad: fp.PadMargin, stack: int) -> cq.Workplane:
    """A pad of glass over each block's top, grown by the margin fore and aft and inboard (outboard it would run into the side)."""
    m = pad.margin
    boxes = []
    for f in fp.region_faces(part_name, pad.face):
        bb = f.BoundingBox()
        y0, y1 = (bb.ymin - m, bb.ymax) if bb.ymax > 0 else (bb.ymin, bb.ymax + m)
        z0 = bb.zmax + PLY_T * (stack - 1)
        boxes.append(fb._box(bb.xmin - m, bb.xmax + m, y0, y1, z0, z0 + PLY_T).val())
    return cq.Workplane("XY").add(cq.Compound.makeCompound(boxes))


def _stack_key(p: fp.FusePly) -> str:
    reg = fp.region_of(p)
    if isinstance(reg, fp.Face):
        return reg.name
    if isinstance(reg, fp.RolloverFaces):
        return f"rollover:{reg.kind}"
    if isinstance(reg, fp.PadMargin):
        return reg.face
    return "upper"  # a corner tape lies over the bottom's glass


def _ply_shell(p: fp.FusePly, k: int) -> cq.Workplane:
    reg = fp.region_of(p)
    if isinstance(reg, fp.Face):
        return _face_shell(p.part, reg, k)
    if isinstance(reg, fp.CornerTape):
        return _tape_shell(p.part, reg, k)
    if isinstance(reg, fp.RolloverFaces):
        return _rollover_shell(reg.kind, k)
    if isinstance(reg, fp.PadMargin):
        return _pad_shell(p.part, reg, k)
    raise TypeError(
        f"{p.node}: no shell for region {reg!r}"
    )  # a new region type must get a shell or be excluded


# ---- stages ----------------------------------------------------------------------------------------
def _cutout_region() -> cq.Workplane:
    """The canard opening's box (core.fuselage_book._canard_cutout), 1 in further forward so F22's forward plies go with its tab."""
    x1 = G.fs_f28 + fb.FITTED_F28_THICKNESS + fb.FITTED_CUTOUT_AFT_OF_F28
    return fb._box(
        G.fs_f22 - 1.0,
        x1,
        -20.0,
        20.0,
        fb.z_of_wl(fb.CANARD_CUTOUT_FLOOR_WL),
        fb.Z_TOP + 1.0,
    )


def _cut(wp: cq.Workplane) -> cq.Workplane:
    return cq.Workplane("XY").add(wp.cut(_cutout_region()).val())


def _vol(wp: cq.Workplane) -> float:
    return sum(s.Volume() for s in wp.vals())


@lru_cache(maxsize=1)
def _op_index() -> dict[str, int]:
    from pathlib import Path

    from guide.schema import load_graph, topo_order

    return {
        op: i
        for i, op in enumerate(topo_order(load_graph(Path(__file__).parent / "graph")))
    }


@lru_cache(maxsize=1)
def _shells() -> tuple[tuple[str, cq.Workplane, int], ...]:
    """(ply node, shell as laid, its stack position). A ply laid on a part after the canard opening is cut is cut with it."""
    out = []
    seen: dict[tuple[str, str], int] = {}
    after_cut = _op_index()[CUTOUT_OP]
    for p in _plies():
        key = (p.part, _stack_key(p))
        k = seen[key] = seen.get(key, 0) + 1
        shell = _ply_shell(p, k)
        if p.part in CUT_PARTS and _op_index()[p.op] > after_cut:
            shell = _cut(shell)
        out.append((p.node, shell, k))
    return tuple(out)


def ply_shells() -> dict[str, cq.Workplane]:
    """Ply node -> its thin solid (cached)."""
    return {node: shell for node, shell, _ in _shells()}


@lru_cache(maxsize=1)
def _base_and_stages() -> (
    tuple[dict[str, cq.Workplane], dict[str, tuple[tuple[str, str, cq.Workplane], ...]]]
):
    """(the shape each part node shows first, {node: ((op, stage node, shape), ...)} in graph order)."""
    parts = _parts()
    base = {name: part.solid for name, part in parts.items()}
    stages: dict[str, list[tuple[str, str, cq.Workplane]]] = {}
    carved = fb.carved_box()
    for name, c in carved.items():
        stages.setdefault(node_of(name), []).append(
            (CARVE_OP, f"{node_of(name)}~carved", c.solid)
        )
    for name in CUT_PARTS:
        last = stages.get(node_of(name), [(None, None, base[name])])[-1][2]
        stages.setdefault(node_of(name), []).append(
            (CUTOUT_OP, f"{node_of(name)}~cut", _cut(last))
        )
    # the belt insert is cut into the carved bottom (f07.belt-insert follows the carve)
    base["belt_insert"] = cq.Workplane("XY").add(
        parts["belt_insert"].solid.intersect(carved["bottom"].solid).val()
    )
    # the roll-over before its access holes (f08.access-holes cuts the map slot and the baggage hole after the outside glass)
    pc = fb.rollover_pieces()
    base["rollover"] = cq.Workplane("XY").add(
        parts["rollover"].solid.union(pc["slot_fill"]).union(pc["hole_fill"]).val()
    )
    stages[node_of("rollover")] = [
        (HOLES_OP, f"{node_of('rollover')}~holes", parts["rollover"].solid)
    ]
    # plies laid on a cut part before the opening is cut lose what the opening takes
    after_cut = _op_index()[CUTOUT_OP]
    for p in _plies():
        if p.part not in CUT_PARTS or _op_index()[p.op] > after_cut:
            continue
        shell = ply_shells()[p.node]
        cut = _cut(shell)
        if _vol(shell) - _vol(cut) > 1e-6:
            stages[p.node] = [(CUTOUT_OP, f"{p.node}~cut", cut)]
    order = _op_index()
    return base, {
        n: tuple(sorted(s, key=lambda t: order[t[0]])) for n, s in stages.items()
    }


def components() -> dict:
    """glb components: a part with plies is (solid, {ply node: shell}); a part without plies is its solid; each stage is its own node."""
    # Deep copies: the glTF export tessellates what it is given, and a triangulation left on the cached part solids changes their
    # bounding boxes (BoundingBox uses it) for anything that measures them later in the same process.
    shells = ply_shells()
    base, stages = _base_and_stages()
    by_part: dict[str, dict] = {}
    for p in _plies():
        by_part.setdefault(p.part, {})[p.node] = shells[p.node].val().copy()
    out: dict = {}
    for name in _parts():
        solid = base[name].val().copy()
        out[node_of(name)] = (solid, by_part[name]) if name in by_part else solid
    for st in stages.values():
        for _op, node, shape in st:
            out[node] = shape.val().copy()
    return out


def _xrange(wp: cq.Workplane) -> tuple[float, float]:
    bb = (
        wp.val().BoundingBox()
        if len(wp.vals()) == 1
        else cq.Compound.makeCompound(wp.vals()).BoundingBox()
    )
    return bb.xmin, bb.xmax


def _ch9_excluded() -> list[dict]:
    from pathlib import Path

    from guide.schema import load_graph

    g = load_graph(Path(__file__).parent / "graph")
    return [
        {
            "op": op_id,
            "where": m["where"],
            "reason": _CH9_REASON[op_id],
            "parts": ["strut"],
        }
        for op_id, op in g.ops.items()
        if op.chapter == 9
        for m in op.materials
    ]


# ---- chapters 11-13 in the lab (M2.4 Task 5): the elevators, the nose, the nose gear --------------------------------------------------
NOSE_GEAR_RETRACT_SECONDS = 6.0  # fitted: the lab's crank takes this long, inside the book's 5-7 s (plans-1980:p73)
HANG_CG = (
    -1.5,
    0.1,
)  # fitted (dx, dz) in from the hinge line, in: forward of the hinge. The elevator masses are NOT sourced, so the hang test
# is illustrative: the kernel (core.elevators_kin.hang_pitch_deg) gives the pitch for whatever CG it is handed
CANARD_INCIDENCE_DEG = 0.0  # book: the canard is set level to the top longerons (plans-1980:p72 template G); config canard_incidence is unsourced, not used
_CH13_NOSE_CITE = ("plans-1980:p73",)


def _labelled(cid: str, fidelity: str) -> str:
    from pathlib import Path

    from guide.schema import load_graph

    label = load_graph(Path(__file__).parent / "graph").components[cid].label
    return label + (" (fitted shape)" if fidelity == "representational" else "")


def _extent(shapes) -> tuple[float, float]:
    bb = cq.Compound.makeCompound(
        [s.val() if hasattr(s, "val") else s for s in shapes]
    ).BoundingBox()
    return round(bb.xmin, 4), round(bb.xmax, 4)


def extras_section() -> dict:
    """layup.json["fuselage"]["extras"]: what the lab needs for the elevators (canard subject, and installed on the airplane), the nose and
    the nose gear (fuselage subject, chapter 13): part rows, the elevator kernel's inputs and the nose-gear kinematics' inputs. The lab
    re-implements core.elevators_kin and core.nose_gear_kin from these inputs (guide/lab/src/logic/kin.ts; parity fixture in
    guide/lab/tests/fixtures/kernels.json)."""
    from core import elevators_kin as ek
    from core import landing_gear_book as lgb
    from core import nose_gear_kin as ngk
    from core.elevators_book import build_elevators, hinge_axis_xz, x_tube_le
    from core.nose_book import COMPONENT_PARTS, build_nose

    nose = build_nose()
    gear = lgb.build_nose_gear("plans")
    rows: dict[str, dict] = {}

    def add(cid: str, parts: list[FusePart]) -> None:
        fid = (
            "representational"
            if any(p.fidelity == "representational" for p in parts)
            else parts[0].fidelity
        )
        lo, hi = _extent([p.solid for p in parts])
        rows[cid.replace(".", "_")] = {
            "node": cid,
            "component": cid,
            "fidelity": fid,
            "label": _labelled(cid, fid),
            "cite": sorted({c for p in parts for c in p.cite}),
            "fs_min": lo,
            "fs_max": hi,
            "fwd_normal": None,
        }

    for cid, names in COMPONENT_PARTS.items():
        add(cid, [nose[n] for n in names])
    add("nose.ng_hardware", [gear["ng6_block"]])
    add("gear.nose_strut", [gear[n] for n in ("strut", "fork", "wheel")])
    # the strut group is built on the bench (chapter 13's first ops show no geometry for it): it is drawn from the op that lowers it into the box
    rows["gear_nose_strut"]["show"] = {"from": "f13.lower-gear"}

    el = build_elevators()
    elev_rows = {}
    for cid, keys in (
        ("elevator.right", ("elevator_right",)),
        ("elevator.left", ("elevator_left",)),
        ("elevator.tube", ("elevator_tube_right", "elevator_tube_left")),
        ("elevator.hinges", ("hinges_right", "hinges_left")),
        ("elevator.balance_weight", ("balance_weight_right", "balance_weight_left")),
        ("elevator.cs11_weight", ("cs11_weight_right", "cs11_weight_left")),
    ):
        fid = (
            "representational"
            if any(el[k].fidelity == "representational" for k in keys)
            else el[keys[0]].fidelity
        )
        label = _labelled(cid, fid)
        if (
            cid == "elevator.hinges"
        ):  # the stations are placed from the text and the figure at low confidence (core.elevators_book); one parenthetical, short enough for a phone
            label = "Elevator hinges (from text, low confidence; fitted shape)"
        elif (
            cid == "elevator.tube"
        ):  # the tube is the book's 1 in; the airfoil file the canard section is fitted to is thinner than it (owner item, unresolved)
            label = "Elevator torque tubes (1 in OD book; section fitted, unresolved)"
        elev_rows[cid] = {"node": cid, "fidelity": fid, "label": label}
    hx, hz = hinge_axis_xz()
    G_ = config.geometry
    up_t, down = ek.travel_range_deg()
    pts = lgb.nose_gear_points("plans")
    return {
        "frame": "canard frame as exported for the elevators (x chord aft, y up, z = -B.L., inches); the box frame for the nose",
        "nose_parts": rows,
        "elevators": {
            "parts": elev_rows,
            "hinge_xz": [round(hx, 6), round(hz, 6)],
            "tube_le_x": round(x_tube_le(), 6),
            # the canard's own core and skins are not drawn aft of x_cut over the elevators' span while the elevators show (lab only; the glb
            # and the canard-only cutaway export are untouched): the elevators' leading edge (the fitted tube LE) less the book's hinge slot gap
            "cove": {
                "x_cut": round(x_tube_le() - G_.elevator_slot_gap_in, 6),
                "slot_gap": G_.elevator_slot_gap_in,
                # the cove is limited to the FOAM span: |B.L.| from the foam inboard end (the drawn stock end, span vs fuselage sides unresolved) to the outboard end
                "bl_start": round(
                    min(ek.elevator_span("right")[0], -ek.elevator_span("left")[1]), 6
                ),
                "bl_end": G_.elevator_outboard_end_bl_in,
                "label": "Cove cut for the elevators (fitted shape)",
            },
            "travel": {
                "up_target_deg": up_t,
                "up_floor_deg": G_.elevator_travel_up_floor_deg,
                "down_deg": down,
            },
            "hang_cg": {
                "dx": HANG_CG[0],
                "dz": HANG_CG[1],
                "note": "illustrative CG: masses not sourced",
                "fitted": True,
            },
            "jig_label": "NC-7 tube jig (fitted shape)",
            "installed_label": "Elevators (fitted shape; span vs fuselage sides unresolved)",
        },
        "canard_install": {
            "fs_le": G_.fs_canard_le,
            "z_le": G_.canard_le_wl,
            "z_le_status": "conflict",
            "incidence_deg": CANARD_INCIDENCE_DEG,
            "incidence_note": "zero to the longerons (book, p72 template G); config canard_incidence is unsourced and is not used",
        },
        "nose_gear": {
            "strut_length": G_.nose_strut_pivot_to_pivot_in,
            "axle_wl": G_.wl_nose_wheel,
            "pivot_wl": ngk.default_pivot_wl(),
            "clearance_wl": G_.wl_fuselage_bottom_3view + lgb.FITTED_TIRE_OD / 2,
            "wl_zero": -fb.z_of_wl(0.0),  # model z = W.L. - wl_zero
            "crank_turns": G_.nose_crank_turns,
            "retract_seconds": NOSE_GEAR_RETRACT_SECONDS,
            "book_seconds": list(ngk.crank_seconds_range()),
            "tire_od": lgb.FITTED_TIRE_OD,
            "tire_width": lgb.FITTED_TIRE_WIDTH,
            "candidates": {
                "plans": {
                    "axle_fs": lgb.NOSE_CANDIDATES["plans"],
                    "cite": "plans-1980:p171",
                },
                "manual": {
                    "axle_fs": lgb.NOSE_CANDIDATES["manual"],
                    "cite": "om-1980:p35",
                },
            },
            "status": "conflict",
            "theta_down_deg": round(pts["theta_down_deg"], 6),
            "theta_up_deg": round(lgb.nose_retracted_theta_deg("plans"), 6),
        },
    }


# ---- chapters 14-17 (M2.5): the spar, firewall face, controls and trim ----------------------------------------------------------------
M25_JIG_OPS = (
    "f14.jig",
    "f14.cap-troughs",
)  # the spar jig shows from the first and goes when the box is lifted out (until is exclusive)
M25_CAP_OP = "f14.spar-caps"
# a part's own window when it is shown later than its component's first op (a fitting is on the spar only once its op fits it)
M25_SHOW = {
    "spar.jig": {"from": M25_JIG_OPS[0], "until": M25_JIG_OPS[1]},
    "spar.bulkheads.end_bulkheads": {"from": "f14.foam-box"},
    "spar.bulkheads.interior_bulkheads": {"from": "f14.interior-layups"},
    "trim.pitch_handle.pth": {"from": "f17.pitch-trim"},
    "trim.pitch_handle.pth_springs": {"from": "f17.pitch-trim"},
    "trim.roll_trim.roll_trim_springs": {"from": "f17.roll-trim"},
}
M25_LABELS = {
    "spar.box": "Spar foam box",
    "spar.cap_top": "Top spar cap, 12 UND plies",
    "spar.cap_bottom": "Bottom spar cap, 9 UND plies",
    "spar.bulkheads.end_bulkheads": "Spar end bulkheads",
    "spar.bulkheads.interior_bulkheads": "Spar interior bulkheads",
    "spar.lwa.lwa1": "Wing attach plates LWA1 to LWA5",
    "spar.lwa.lwa2": "Wing attach plates LWA2",
    "spar.lwa.lwa3": "Wing attach plates LWA3",
    "spar.lwa.lwa4": "Wing attach plates LWA4",
    "spar.lwa.lwa5": "Wing attach plates LWA5",
    "spar.spruce_blocks": "Spruce blocks",
    "spar.em12": "Engine-mount angles EM12",
    "spar.sh1": "Harness plates SH1",
    "spar.jig": "Spar jig",
    "fuselage.firewall_stainless": "Stainless firewall face",
    "firewall.belcrank": "Rudder and brake belcrank",
    "firewall.master_cylinders": "Brake master cylinders",
    "controls.consoles.front_console": "Front console",
    "controls.consoles.rear_console": "Rear console",
    "controls.torque_tube": "Torque tube",
    "controls.sticks.front_stick": "Front stick",
    "controls.sticks.rear_stick": "Rear stick",
    "controls.pitch_pushrod": "Pitch pushrod",
    "controls.rudder_conduit": "Rudder cable conduits",
    "trim.pitch_handle.pth": "Pitch trim handle",
    "trim.pitch_handle.pth_pivot": "Handle pivot pin",
    "trim.pitch_handle.pth_springs": "Pitch trim springs",
    "trim.roll_trim.roll_trim": "Roll trim levers",
    "trim.roll_trim.roll_trim_springs": "Roll trim springs",
}


@lru_cache(maxsize=1)
def _m25_built() -> dict:
    """{component id: [(node, part name, FusePart or None)]} for every M2.5 component; the caps are per-ply nodes (part None)."""
    from core import controls_book, firewall_book, spar_book

    out: dict = {}
    for build, mapping in (
        (spar_book.build_spar, spar_book.COMPONENT_PARTS),
        (firewall_book.build_firewall, firewall_book.COMPONENT_PARTS),
        (controls_book.build_controls, controls_book.COMPONENT_PARTS),
    ):
        parts = build()
        for cid, names in mapping.items():
            out[cid] = [
                (cid if len(names) == 1 else f"{cid}.{n}", n, parts[n]) for n in names
            ]
    return out


def m25_cap_solids() -> dict[str, list]:
    """cap component -> its plies in lay order, drawn the way the lab shows them: stacked outward from the box face, each ply
    PLY visual thickness (spar_book.CAP_VISUAL_PLY_T), not the published 0.0375 in."""
    from core import spar_book

    return {
        f"spar.cap_{c}": spar_book.cap_plies(
            c, thickness=spar_book.CAP_VISUAL_PLY_T, outward=True
        )
        for c in ("top", "bottom")
    }


def m25_components() -> dict:
    """glb components for chapters 14-17 (see guide.export_glb.m25_components)."""
    out: dict = {}
    caps = m25_cap_solids()
    for cid, rows in _m25_built().items():
        if cid in caps:
            out[cid] = {
                f"{cid}.p{i + 1}": solid.copy() for i, solid in enumerate(caps[cid])
            }
        elif len(rows) == 1:
            out[cid] = rows[0][2].solid.val().copy()
        else:
            out[cid] = {node: part.solid.val().copy() for node, _n, part in rows}
    return out


def m25_section() -> dict:
    """layup.json["fuselage"]["extras"]["m25"]: part rows (by lab part name), the cap plies as ply rows, and the jig's rest offset."""
    from core import spar_book

    parts: dict[str, dict] = {}
    nodes: dict[str, dict] = {}
    caps = m25_cap_solids()
    ops_order = list(_op_index())
    for cid, rows in _m25_built().items():
        if cid in caps:
            fid = rows[0][2].fidelity
            part = cid.replace(".", "_")
            solids = caps[cid]
            lo, hi = _extent(solids)
            parts[part] = {
                "node": cid,
                "component": cid,
                "fidelity": fid,
                "label": M25_LABELS[cid] + " (fitted shape; ply thickness exaggerated)",
                "cite": list(rows[0][2].cite),
                "fs_min": lo,
                "fs_max": hi,
                "fwd_normal": None,
            }
            for i, solid in enumerate(solids):
                x0, x1 = _extent([solid])
                nodes[f"{cid}.p{i + 1}"] = {
                    "part": part,
                    "component": cid,
                    "op": M25_CAP_OP,
                    "op_index": ops_order.index(M25_CAP_OP),
                    "op_order": i + 1 + (12 if cid.endswith("bottom") else 0),
                    "order": i + 1,
                    "stack": i + 1,
                    "cloth": "UND",
                    "orientation_deg": 0.0,
                    "where": f"{cid.split('.')[1]} spar cap, ply {i + 1}",
                    "region": "cap",
                    "fidelity": fid,
                    "lower_bound": False,
                    "area_in2": round(solid.Volume() / spar_book.CAP_VISUAL_PLY_T, 3),
                    "fs_min": x0,
                    "fs_max": x1,
                }
            continue
        for node, _n, part in rows:
            lo, hi = _extent([part.solid])
            row = {
                "node": node,
                "component": cid,
                "fidelity": part.fidelity,
                "label": M25_LABELS[node]
                + (" (fitted shape)" if part.fidelity == "representational" else ""),
                "cite": list(part.cite),
                "fs_min": lo,
                "fs_max": hi,
                "fwd_normal": None,
            }
            if node in M25_SHOW:
                row["show"] = dict(M25_SHOW[node])
            parts[node.replace(".", "_")] = row
    from core import controls_book as cb
    from core import controls_kin as ck

    base_f, _tip = cb.stick_axis("front")
    base_r, _tip = cb.stick_axis("rear")
    up_t, down = ck.travel_limits_deg()
    controls = {
        "arm_in": G.ctl_elevator_arm_fit_in,
        "lever_in": G.ctl_stick_lever_fit_in,
        "cant_forward_deg": G.ctl_stick_cant_forward_deg,
        "cant_inboard_deg": G.ctl_stick_cant_inboard_deg,
        "up_target_deg": up_t,
        "up_floor_deg": G.elevator_travel_up_floor_deg,
        "down_deg": down,
        "pivot_fs": {
            "front": G.ctl_stick_pivot_fs_front,
            "rear": G.ctl_stick_pivot_fs_rear,
        },
        "tube_bl": G.ctl_torque_tube_hole_bl_in,
        "tube_wl": G.ctl_torque_tube_hole_wl_in,
        "wl_zero": -fb.z_of_wl(0.0),
        "stop_label": "Pitch stops (not printed; fitted shape)",
        "stop_size_in": [1.0, 1.0, 0.6],
        "note": "stick pitch from the Roncz travel row only (15 up, 30 down; 12.5 is the floor); the arm and stop positions are fitted",
    }
    return {
        "parts": parts,
        "nodes": nodes,
        "controls": controls,
        "jig_t": spar_book.FITTED_JIG_T,
        "cap_visual_ply_in": spar_book.CAP_VISUAL_PLY_T,
        "cap_note": "cap plies are drawn stacked outward from the box face at a visual thickness, not the published 0.0375 in laid ply",
    }


# ---- chapter 18 (M2.6): the canopy ----------------------------------------------------------------------------------------------------
M26_LIFT = (
    "canopy.plexi",
    "canopy.frame",
    "canopy.pads",
    "canopy.vent",
    "canopy.brace_tubes",
)  # the components that come off with the canopy at f18.cut-remove and sit upside down on the bench until it is hinged back on
M26_BENCH_OPS = (
    "f18.trim-plexi",
    "f18.cut-remove",
    "f18.vent-brace",
)  # trimmed on the bench; lifted off at the cut; the last op on the bench
M26_GLASS_OP = "f18.glass-outside"
# a part's own window: the temporary blocks while the canopy rests on them and until it is carved inside; the frame's three shapes in turn
M26_SHOW = {
    "canopy.blocks": {"from": "f18.locate-blocks", "until": "f18.carve-inside"},
    "canopy.frame_foam": {"from": "f18.foam-core", "until": "f18.carve-outside"},
    "canopy.frame_carved": {"from": "f18.carve-outside", "until": "f18.carve-inside"},
    "canopy.frame": {"from": "f18.carve-inside"},
}
M26_LABELS = {
    "canopy.plexi": "Plexiglass canopy",
    "canopy.frame_foam": "Foam frame, uncarved",
    "canopy.frame_carved": "Foam frame, carved",
    "canopy.frame": "Frame, inside carved",
    "canopy.frame_glass": "Frame glass, five plies",
    "canopy.blocks": "Temporary blocks",
    "canopy.vent": "Vent block",
    "canopy.brace_tubes": "Brace tubes",
    "canopy.pads.pads_hinge": "Hinge pads, right, 4",
    "canopy.pads.pads_latch": "Latch pads, left, 3",
    "canopy.pads.pad_catch": "Safety-catch pad, left",
    "canopy.hinges.hinge_fuselage": "Hinges, fuselage leaves",
    "canopy.hinges.hinge_canopy": "Hinges, canopy leaves",
    "canopy.latches": "Latches",
    "canopy.safety_catch.sc1": "Safety catch SC-1",
    "canopy.safety_catch.sc1_bolt": "Catch bolt",
    "fuselage.front_cover": "Front cover",
    "fuselage.rear_cover": "Rear cover",
    "fuselage.door": "Door",
}
# the role of each pad kind (what the lab colours and names it by)
M26_PAD_ROLE = {
    "canopy.pads.pads_hinge": "hinge",
    "canopy.pads.pads_latch": "latch",
    "canopy.pads.pad_catch": "catch",
}


@lru_cache(maxsize=1)
def _m26_built() -> dict:
    """{component id: [(node, part name, FusePart)]} (core.canopy_book.COMPONENT_PARTS), plus the display-only frame shapes."""
    from core import canopy_book as cbk

    parts = cbk.build_canopy()
    out: dict = {}
    for cid, names in cbk.COMPONENT_PARTS.items():
        out[cid] = [
            (cid if len(names) == 1 else f"{cid}.{n}", n, parts[n]) for n in names
        ]
    return out


@lru_cache(maxsize=1)
def _m26_display() -> dict:
    """The frame's uncarved and carved shapes and its five glass plies (display only: not part of core.canopy_book.build_canopy, which the
    non-overlap checks read)."""
    from core import canopy_book as cbk

    rep = "representational"
    return {
        "foam": FusePart(
            "frame_foam",
            cbk.frame_foam(),
            rep,
            ("plans-1980:p109",),
            "2 in urethane blocks fitted round the plexiglass before they are carved; taller and proud of the side; shape fitted",
        ),
        "carved": FusePart(
            "frame_carved",
            cbk.frame_carved(),
            rep,
            ("plans-1980:p109", "plans-1980:p110"),
            "the foam carved to the fuselage contour, 0.06 in low for the glass; no pad pockets yet; shape fitted",
        ),
        "plies": cbk.frame_plies(),
    }


def m26_components() -> dict:
    """glb components for chapter 18 (see guide.export_glb.m26_components): the canopy.frame node carries the frame with the five plies as
    children (canopy.frame.p1..p5); the uncarved and carved frame shapes are their own display nodes."""
    out: dict = {}
    disp = _m26_display()
    for cid, rows in _m26_built().items():
        if cid == "canopy.frame":
            out[cid] = (
                rows[0][2].solid.val().copy(),
                {
                    f"{cid}.p{i + 1}": ply.val().copy()
                    for i, ply in enumerate(disp["plies"])
                },
            )
        elif len(rows) == 1:
            out[cid] = rows[0][2].solid.val().copy()
        else:
            out[cid] = {node: part.solid.val().copy() for node, _n, part in rows}
    out["canopy.frame_foam"] = disp["foam"].solid.val().copy()
    out["canopy.frame_carved"] = disp["carved"].solid.val().copy()
    return out


def m26_section() -> dict:
    """layup.json["fuselage"]["extras"]["m26"]: part rows (by lab part name) and the frame's five plies as ply rows, the canopy's hinge line and
    open range, the A and B checks, the latch-pad conflict and the front cut's unnamed datum, as the lab states them."""
    from core import canopy_book as cbk

    ops_order = list(_op_index())
    parts: dict[str, dict] = {}
    nodes: dict[str, dict] = {}
    disp = _m26_display()

    def row(node, cid, fid, cite, label, lo, hi, turns):
        r = {
            "node": node,
            "component": cid,
            "fidelity": fid,
            "label": label + (" (fitted shape)" if fid == "representational" else ""),
            "cite": list(cite),
            "fs_min": lo,
            "fs_max": hi,
            "fwd_normal": None,
        }
        if node in M26_SHOW:
            r["show"] = dict(M26_SHOW[node])
        if turns:
            r["turns"] = True
        if node in M26_PAD_ROLE:
            r["role"] = M26_PAD_ROLE[node]
        return r

    for cid, rows in _m26_built().items():
        for node, pname, part in rows:
            lo, hi = _extent([part.solid])
            parts[node.replace(".", "_")] = row(
                node,
                cid,
                part.fidelity,
                part.cite,
                M26_LABELS[node],
                lo,
                hi,
                pname in cbk.CANOPY_ATTACHED,
            )
    for key, node in (("foam", "canopy.frame_foam"), ("carved", "canopy.frame_carved")):
        part = disp[key]
        lo, hi = _extent([part.solid])
        parts[node.replace(".", "_")] = row(
            node,
            "canopy.frame",
            part.fidelity,
            part.cite,
            M26_LABELS[node],
            lo,
            hi,
            True,
        )
    frame_part = _m26_built()["canopy.frame"][0][2]
    glass_lo, glass_hi = _extent(disp["plies"])
    parts["canopy_frame_glass"] = {
        "node": "canopy.frame_glass",
        "component": "canopy.frame",
        "fidelity": "representational",
        "label": M26_LABELS["canopy.frame_glass"]
        + " (fitted shape; ply thickness exaggerated)",
        "cite": list(frame_part.cite),
        "fs_min": glass_lo,
        "fs_max": glass_hi,
        "fwd_normal": None,
        "turns": True,
    }
    for i, (ply, (cloth, kind, deg)) in enumerate(
        zip(disp["plies"], cbk.FRAME_PLY_SCHEDULE)
    ):
        x0, x1 = _extent([ply])
        nodes[f"canopy.frame.p{i + 1}"] = {
            "part": "canopy_frame_glass",
            "component": "canopy.frame",
            "op": M26_GLASS_OP,
            "op_index": ops_order.index(M26_GLASS_OP),
            "op_order": i + 1,
            "order": i + 1,
            "stack": i + 1,
            "cloth": cloth,
            "orientation_deg": deg if cloth == "BID" else 0.0,
            "where": f"frame ply {i + 1}, {kind}" + (", groove ply" if i == 0 else ""),
            "region": kind,
            "fidelity": "representational",
            "lower_bound": False,
            "area_in2": round(
                sum(s.Volume() for s in ply.solids().vals()) / cbk.FITTED_PLY_VIS_T, 3
            ),
            "fs_min": x0,
            "fs_max": x1,
        }
    lat = G.canopy_latch_pad_centres_fs
    labels = G.canopy_latch_labels_fs
    fa, fb_ = G.canopy_check_a_wl, G.canopy_check_b_wl
    return {
        "parts": parts,
        "nodes": nodes,
        "canopy": {
            "lift": list(M26_LIFT),
            "wl_zero": -fb.z_of_wl(0.0),  # model y = W.L. - wl_zero
            "hinge": {
                "y": cbk.HINGE_Y,
                "z": cbk.HINGE_Z,
                "max_open_deg": cbk.MAX_OPEN_DEG,
                "past_vertical_deg": G.canopy_open_past_vertical_deg,
                "note": "the opening arc is representational (the plans give the hinge line and about 15 deg past vertical, p115)",
            },
            "checks": [
                {
                    "id": "A",
                    "fs": cbk.FITTED_HEADREST_FS - 6.0,
                    "fs_status": "fitted",
                    "wl0": G.canopy_check_datum_wl,
                    "wl1": fa,
                    "min": True,
                    "height_in": G.canopy_check_a_min_in,
                },
                {
                    "id": "B",
                    "fs": G.canopy_check_b_fs,
                    "fs_status": "book",
                    "wl0": G.canopy_check_datum_wl,
                    "wl1": fb_,
                    "min": False,
                    "height_in": G.canopy_check_b_in,
                },
            ],
            "latch": {
                "derived_centres_fs": [round(c, 4) for c in lat],
                "printed_labels_fs": list(labels),
                "gap_in": round(max(abs(a - b) for a, b in zip(lat, labels)), 4),
            },
            "front_cut": {"fs": G.canopy_front_cut_fs, "datum_named": False},
            "rear_cut_fs": G.canopy_rear_cut_fs,
            "pads": {
                "left_aft_edge_fwd_of_cut": list(G.canopy_pad_aft_edge_left_in),
                "right_aft_edge_fwd_of_cut": list(G.canopy_pad_aft_edge_right_in),
                "length_in": G.canopy_pad_length_in,
                "catch_fs": G.canopy_safety_catch_fs,
            },
        },
    }


# ---- chapters 19 and 20 (M2.7): the wings and the winglets -----------------------------------------------------------------------------
SIDES = ("right", "left")
M27_PLY_PARTS = {  # part name -> (op the plies are laid in, component)
    "shear_web": ("f19.shear-web", "wing.shear_web"),
    "cap_bottom": ("f19.bottom-cap", "wing.spar_caps"),
    "cap_top": ("f19.top-cap", "wing.spar_caps"),
    "skin_bottom": ("f19.bottom-skin", "wing.skins"),
    "skin_top": ("f19.top-skin", "wing.skins"),
    "skin_out": ("f20.skins", "winglet.skins"),
    "skin_in": ("f20.skins", "winglet.skins"),
    "layup_3": ("f20.outside-layups", "winglet.layups"),
}
M27_PLY_CLOTH = {  # (part, ply k) -> cloth; the rest are UND (the wing cores' skins, caps, web) or BID (the winglet's)
    ("skin_bottom", 3): "BID",
    ("skin_out", 3): "BID",
}
M27_SHOW_FROM = {  # a part's first op (the lab shows it from here on)
    "jigs": "f19.jig",
    "fc1": "f19.cut-cores",
    "fc2": "f19.cut-cores",
    "fc3": "f19.cut-cores",
    "fc4": "f19.le-cores",
    "fc5": "f19.le-cores",
    "hardpoints": "f19.hardpoints",
    "conduit": "f19.rudder-conduit",
    "ribs": "f19.ribs",
    "aileron": "f19.aileron-cut",
    "hinge_pins": "f19.aileron-build",
    "hinge_leaves": "f19.aileron-build",
    "aileron_rod": "f19.aileron-build",
    "torque_tube": "f19.aileron-build",
    "controls": "f19.controls",
    "spar_bolts": "f19.attach",
    "upper_core": "f20.cut-cores",
    "tip_cap": "f20.skins",
    "jig_lines": "f20.jig",
    "block_a": "f20.outside-layups",
    "lower_fin": "f20.lower-fin",
    "rudder": "f20.rudder-cut",
    "belhorn": "f20.rudder-hang",
    "rudder_hinge": "f20.rudder-hang",
}
M27_LABELS = {
    "jigs": "Wing jigs",
    "fc1": "Core FC1, inboard",
    "fc2": "Core FC2, centre aft",
    "fc3": "Core FC3, outboard aft",
    "fc4": "Core FC4, centre leading edge",
    "fc5": "Core FC5, outboard leading edge",
    "hardpoints": "Hard points and plates",
    "shear_web": "Shear web plies",
    "cap_bottom": "Bottom spar cap plies",
    "cap_top": "Top spar cap plies",
    "skin_bottom": "Bottom skin plies",
    "skin_top": "Top skin plies",
    "conduit": "Rudder conduit",
    "ribs": "Root rib and incidence board",
    "aileron": "Aileron",
    "hinge_pins": "Aileron hinges, wing side",
    "hinge_leaves": "Aileron hinges, aileron side",
    "aileron_rod": "Aileron balance rod",
    "torque_tube": "Aileron torque tube",
    "controls": "Root bay controls",
    "spar_bolts": "Wing attach bolts",
    "upper_core": "Upper fin core",
    "tip_cap": "Tip cap",
    "jig_lines": "Jig lines A, B and C",
    "layup_3": "Corner layup 3, UND plies",
    "block_a": "Block A",
    "lower_fin": "Lower fin",
    "rudder": "Rudder",
    "belhorn": "Rudder belhorn",
    "rudder_hinge": "Rudder hinge",
    "skin_out": "Winglet skin, outboard plies",
    "skin_in": "Winglet skin, inboard plies",
}


@lru_cache(maxsize=1)
def _m27_built() -> dict:
    """{side: ({part: FusePart}, {part: [ply solids]})} for the wings and the winglets together (core.wing_book, core.winglet_book)."""
    from core import wing_book as wb
    from core import winglet_book as wl

    out = {}
    for side in SIDES:
        parts = {**wb.build_wing(side), **wl.build_winglet(side)}
        plies = {**wb.build_plies(side), **wl.build_plies(side)}
        out[side] = (parts, plies)
    return out


def _m27_component_parts() -> dict:
    from core import wing_book as wb
    from core import winglet_book as wl

    return {**wb.COMPONENT_PARTS, **wl.COMPONENT_PARTS}


def m27_components() -> dict:
    """glb components for chapters 19 and 20 (see guide.export_glb.m27_components). A component is a group node named by its id; the children are
    ``<id>.<part>.<right|left>`` and, for the ply parts, one child per ply (``<id>.<part>.<side>.p<k>``) instead of the merged solid. The winglet skins
    are plies only. All solids are in the airplane frame with the wings and winglets in place and the aileron and rudder neutral."""
    built = _m27_built()
    out: dict = {}
    for cid, names in _m27_component_parts().items():
        nodes: dict = {}
        for side in SIDES:
            parts, plies = built[side]
            for n in names:
                if n in M27_PLY_PARTS:
                    for k, ply in enumerate(plies[n], 1):
                        nodes[f"{cid}.{n}.{side}.p{k}"] = ply.val().copy()
                else:
                    nodes[f"{cid}.{n}.{side}"] = parts[n].solid.val().copy()
            if cid == "winglet.skins":
                for n in ("skin_out", "skin_in"):
                    for k, ply in enumerate(plies[n], 1):
                        nodes[f"{cid}.{n}.{side}.p{k}"] = ply.val().copy()
        out[cid] = nodes
    return out


def m27_section() -> dict:
    """layup.json["fuselage"]["extras"]["m27"]: part rows and ply rows by node, the aileron and rudder hinge axes and stops, the three wing conflicts, the
    A, B and C closure and the derived lean, as the lab states them. Representational parts say "fitted shape"."""
    from core import wing_book as wb
    from core import winglet_book as wl

    ops_order = list(_op_index())
    built = _m27_built()
    comp = {n: cid for cid, names in _m27_component_parts().items() for n in names}
    comp["skin_out"] = comp["skin_in"] = "winglet.skins"
    parts: dict[str, dict] = {}
    nodes: dict[str, dict] = {}
    for side in SIDES:
        fparts, plies = built[side]
        for n, part in fparts.items():
            if n in M27_PLY_PARTS and n != "layup_3":
                pass
            node = f"{comp[n]}.{n}.{side}"
            bb = cq.Compound.makeCompound([part.solid.val()]).BoundingBox()
            row = {
                "node": node,
                "component": comp[n],
                "side": side,
                "fidelity": part.fidelity,
                "label": M27_LABELS[n]
                + (" (fitted shape)" if part.fidelity == "representational" else ""),
                "cite": list(part.cite),
                "fs_min": round(bb.xmin, 4),
                "fs_max": round(bb.xmax, 4),
                "bl_min": round(bb.ymin, 4),
                "bl_max": round(bb.ymax, 4),
                "show": {"from": M27_SHOW_FROM.get(n) or M27_PLY_PARTS[n][0]},
            }
            if n in wb.AILERON_ATTACHED:
                row["turns"] = "aileron"
            if n in wl.RUDDER_ATTACHED:
                row["turns"] = "rudder"
            if n in wb.WORKSHOP_PARTS or n in wl.WORKSHOP_PARTS:
                row["workshop"] = True
            if n in M27_PLY_PARTS:
                row["plies"] = len(plies[n])
            parts[f"{comp[n]}_{n}_{side}".replace(".", "_")] = row
        # laid plies with no merged solid: a part row each so the lab can name and stripe them
        for n in ("skin_out", "skin_in"):
            bbs = [ply.val().BoundingBox() for ply in plies[n]]
            parts[f"winglet_skins_{n}_{side}"] = {
                "node": f"winglet.skins.{n}.{side}",
                "component": "winglet.skins",
                "side": side,
                "fidelity": "representational",
                "label": M27_LABELS[n] + " (fitted shape)",
                "cite": list(fparts["tip_cap"].cite),
                "fs_min": round(min(b.xmin for b in bbs), 4),
                "fs_max": round(max(b.xmax for b in bbs), 4),
                "bl_min": round(min(b.ymin for b in bbs), 4),
                "bl_max": round(max(b.ymax for b in bbs), 4),
                "show": {"from": M27_PLY_PARTS[n][0]},
                "plies": len(plies[n]),
            }
        for n, (op, cid) in M27_PLY_PARTS.items():
            for k, ply in enumerate(plies[n], 1):
                bb = ply.val().BoundingBox()
                nodes[f"{cid}.{n}.{side}.p{k}"] = {
                    "part": f"{comp[n]}_{n}_{side}".replace(".", "_"),
                    "component": cid,
                    "side": side,
                    "op": op,
                    "op_index": ops_order.index(op),
                    "op_order": k,
                    "order": k,
                    "stack": k,
                    "cloth": M27_PLY_CLOTH.get(
                        (n, k), "UND" if n != "layup_3" else "UND"
                    ),
                    "fidelity": "representational",
                    "lower_bound": False,
                    "fs_min": round(bb.xmin, 4),
                    "fs_max": round(bb.xmax, 4),
                }
    a0, a1 = wb.aileron_axis()
    r0, r1 = wl.rudder_axis()
    abc = wl.abc_closure()
    return {
        "parts": parts,
        "nodes": nodes,
        "aileron": {
            "axis": [list(a0), list(a1)],
            "max_up_deg": wb.MAX_UP_DEG,
            "inboard_bl": G.wing_aileron_inboard_bl,
            "inboard_bl_p171": G.wing_aileron_inboard_bl_p171,
            "outboard_bl": G.wing_aileron_outboard_bl,
            "hinge_fs": list(G.wing_aileron_hinge_fs),
            "note": "the 20 deg stop is printed (p125, p131); the deflection arc is representational",
        },
        "rudder": {
            "axis": [list(r0), list(r1)],
            "max_deg": wl.MAX_RUDDER_DEG,
            "hinge_fs": G.winglet_book_rudder_hinge_fs,
            "widths_in": list(G.winglet_book_rudder_widths_in),
            "positive": "trailing edge outboard (+y)",
        },
        "conflicts": {
            "le_bl_106_25": {
                "printed_fs": G.wing_book_le_fs_bl_106_25_printed,
                "derived_fs": round(G.wing_le_fs_bl_106_25_derived, 4),
                "line_fs": round(G.wing_le_fs_bl_106_25_line, 4),
            },
            "aileron_inboard": {
                "p124_bl": G.wing_aileron_inboard_bl,
                "p171_bl": G.wing_aileron_inboard_bl_p171,
            },
            "attach_bolt_spacing": {
                "drawing_in": G.wing_spar_join_bolt_spacing_in,
                "text_in": G.wing_spar_join_bolt_spacing_text_in,
            },
        },
        "shear_web": {
            "zones": [list(z) for z in G.wing_shear_web_zones],
            "outboard_plies_printed": G.wing_shear_web_outboard_plies_printed,
            "note": "CP26 LPC 31: the outboard zone is 2 plies, the plans print 3",
        },
        "winglet": {
            "abc_book_in": list(G.winglet_book_jig_abc_in),
            "abc_model_in": [round(abc[k], 4) for k in ("A", "B", "C")],
            "abc_residual_in": [round(abc[k], 4) for k in ("dA", "dB", "dC")],
            "abc_tol_in": list(G.winglet_book_jig_tol_in),
            "lean_in": round(G.winglet_cant_in, 4),
            "lean_status": "derived-unsourced, low: no cant or toe is printed",
            "tip_chord_in": G.winglet_book_tip_chord_in,
            "tip_chord_status": "derived-unsourced, medium: a pixel read, not a page value",
            "wprp": list(G.winglet_book_jig_wprp),
            "points": {k: [round(c, 4) for c in v] for k, v in wl.jig_points().items()},
        },
        "weights": {
            "rows": [
                "wing_ch19",
                "wing_complete",
                "aileron",
                "upper_winglet",
                "lower_winglet",
            ],
            "note": "CP26 builder weights, reference only, in no sum",
        },
    }


# ---- chapters 21 to 23 (M2.8): strakes and fuel, electrical, engine -------------------------------------------------------------------
M28_SHOW_FROM = {  # a part's first op (the lab shows it from here on)
    "rib_r23": "f21.jig-bond",
    "rib_r45": "f21.jig-bond",
    "b23": "f21.jig-bond",
    "db": "f21.jig-bond",
    "bab": "f21.jig-bond",
    "od": "f21.od-outlet",
    "tle": "f21.jig-bond",
    "ble": "f21.jig-bond",
    "skin_bottom": "f21.jig-bond",
    "skin_top": "f21.close-tank",
    "cutout_baggage": "f21.fuselage-cutouts",
    "cutout_tank": "f21.fuselage-cutouts",
    "sump_blister": "f21.outside-bottom",
    "tank": "f21.close-tank",
    "fairing": "f21.fairing-caps",
    "drain_insert": "f21.jig-bond",
    "vent_line": "f21.vent-screen",
    "screen": "f21.vent-screen",
    "outlet_tube": "f21.od-outlet",
    "fuel_cap": "f21.fairing-caps",
    "shelf": "f22.battery-shelf",
    "battery": "f22.battery-shelf",
    "cover": "f22.battery-shelf",
    "strap": "f22.battery-shelf",
    "start_relay": "f22.firewall-terminals",
    "overvoltage_unit": "f22.firewall-terminals",
    "battery_cable": "f22.firewall-terminals",
    "panel_bundle": "f22.panel-wiring",
    "firewall_cable": "f22.firewall-terminals",
    "light_right": "f22.wing-wiring",
    "light_left": "f22.wing-wiring",
    "strobe_supply": "f22.wing-wiring",
    "nav_strip_right": "f22.antennas",
    "nav_strip_left": "f22.antennas",
    "comm_strips": "f22.antennas",
    "block": "f23.engine-install",
    "bracket": "f23.carb-bracket",
    "cowl": "f23.cowl-trim",
    "rib_right": "f23.root-rib",
    "rib_left": "f23.root-rib",
}
M28_LABELS = {
    "rib_r23": "Rib R23",
    "rib_r45": "Rib R45",
    "b23": "Baffle B23",
    "db": "Diagonal baffle DB",
    "bab": "Baffle BAB",
    "od": "Outboard diagonal OD",
    "tle": "Tank leading-edge strip TLE",
    "ble": "Baggage leading-edge strip BLE",
    "skin_bottom": "Strake bottom skin",
    "skin_top": "Strake top skin",
    "cutout_baggage": "Baggage opening in the fuselage side (material removed)",
    "cutout_tank": "Tank opening in the fuselage side (material removed)",
    "sump_blister": "Sump blister",
    "tank": "Fuel tank volume",
    "fairing": "Leading-edge fairing block",
    "drain_insert": "Drain insert",
    "vent_line": "Vent line",
    "screen": "Outlet screen",
    "outlet_tube": "Outlet tube end",
    "fuel_cap": "Fuel cap",
    "shelf": "Battery shelf",
    "battery": "Battery, 25 Ah (station not printed)",
    "cover": "Battery cover",
    "strap": "Battery strap",
    "start_relay": "Start relay",
    "overvoltage_unit": "Over-voltage unit",
    "battery_cable": "Battery cable",
    "panel_bundle": "Panel wire bundle",
    "firewall_cable": "Cable to the firewall",
    "light_right": "Right position light (green)",
    "light_left": "Left position light (red)",
    "strobe_supply": "Strobe power supply",
    "nav_strip_right": "Right nav antenna strip",
    "nav_strip_left": "Left nav antenna strip",
    "comm_strips": "Comm antenna strips (in the right winglet)",
    "block": "Engine block (installation in Section II, not held)",
    "bracket": "Throttle and mixture bracket",
    "cowl": "Cowl outline",
    "rib_right": "Right wing-root metal rib",
    "rib_left": "Left wing-root metal rib",
}


def _closure_readout(led: dict) -> dict:
    """The frozen closure table's nominal sum and verdict, shown beside the 730 lb at FS 111.7 target (ledger row 65).

    Reference readout only: the sum is never used by the model; the verdict string is core.closure.verdict verbatim."""
    from core.closure import closure_sum, verdict

    rows = led["closure"]["rows"]
    t = closure_sum(rows)
    return {
        "ledger_lb": round(t.weight_lb, 2),
        "ledger_cg_fs": round(t.cg_fs, 2),
        "verdict": verdict(rows, led["empty"]["weight_lb"], led["empty"]["arm_in"]),
    }


@lru_cache(maxsize=1)
def _m28_built() -> dict:
    """{"strake": {side: {part: FusePart}}, "elec": {part: FusePart}, "engine": {part: FusePart}} (core.strake_book, electrical_book, engine_book)."""
    from core import electrical_book as eb
    from core import engine_book as ng
    from core import strake_book as sb

    return {
        "strake": {side: sb.build_strake(side) for side in SIDES},
        "elec": eb.build_electrical(),
        "engine": ng.build_engine(),
    }


def _m28_component_parts() -> dict:
    """{component id: (family, part names)}; family is "strake" (a node per side) or "elec" or "engine" (one node per part)."""
    from core import electrical_book as eb
    from core import engine_book as ng
    from core import strake_book as sb

    out = {cid: ("strake", names) for cid, names in sb.COMPONENT_PARTS.items()}
    out.update({cid: ("elec", names) for cid, names in eb.COMPONENT_PARTS.items()})
    out.update({cid: ("engine", names) for cid, names in ng.COMPONENT_PARTS.items()})
    return out


def m28_components() -> dict:
    """glb components for chapters 21 to 23 (see guide.export_glb.m28_components). A component is a group node named by its id; the children are
    ``<id>.<part>.<right|left>`` for the strakes (both sides) and ``<id>.<part>`` for the electrical and engine parts (which name their own side where there
    is one: the lights, the nav strips, the ribs). All solids are in the airplane frame, in place."""
    built = _m28_built()
    out: dict = {}
    for cid, (fam, names) in _m28_component_parts().items():
        nodes: dict = {}
        for n in names:
            if fam == "strake":
                for side in SIDES:
                    nodes[f"{cid}.{n}.{side}"] = (
                        built["strake"][side][n].solid.val().copy()
                    )
            else:
                nodes[f"{cid}.{n}"] = built[fam][n].solid.val().copy()
        out[cid] = nodes
    return out


def m28_section() -> dict:
    """layup.json["fuselage"]["extras"]["m28"]: a row per part (node, component, side, fidelity, label, cite, extents, the op it shows from), the fuel capacity conflict
    with the tank envelope's own volume, the battery range, the engine inputs, and the weights that are reference only. Representational parts say "fitted shape"."""
    from core import electrical_book as eb
    from core import strake_book as sb
    from core.ledger import load_ledger

    built = _m28_built()
    ops_order = list(_op_index())
    parts: dict[str, dict] = {}
    for cid, (fam, names) in _m28_component_parts().items():
        for n in names:
            sides = SIDES if fam == "strake" else (None,)
            for side in sides:
                part = built[fam][side][n] if fam == "strake" else built[fam][n]
                node = f"{cid}.{n}.{side}" if side else f"{cid}.{n}"
                bb = cq.Compound.makeCompound([part.solid.val()]).BoundingBox()
                op = M28_SHOW_FROM[n]
                row = {
                    "node": node,
                    "component": cid,
                    "side": side,
                    "fidelity": part.fidelity,
                    "label": M28_LABELS[n]
                    + (
                        " (fitted shape)" if part.fidelity == "representational" else ""
                    ),
                    "cite": list(part.cite),
                    "fs_min": round(bb.xmin, 4),
                    "fs_max": round(bb.xmax, 4),
                    "bl_min": round(bb.ymin, 4),
                    "bl_max": round(bb.ymax, 4),
                    "show": {"from": op},
                    "op_index": ops_order.index(op),
                }
                if part.void:
                    row["void"] = True
                if n in eb.POCKET_PARTS:
                    row["pocket"] = (
                        True  # sits in a carved pocket the nose foam does not show
                    )
                if n in eb.IN_FOAM_PARTS:
                    row["in_foam"] = True
                if n in sb.INSET_PARTS:
                    row["inset"] = True
                parts[
                    f"{cid}_{n}_{side}".replace(".", "_")
                    if side
                    else f"{cid}_{n}".replace(".", "_")
                ] = row
    led = load_ledger()
    rows = led["prototype_weights"]["rows"]
    ladder = [k for k in rows if k.startswith("n26ms_empty_")]
    return {
        "parts": parts,
        "fuel": {
            "model_gal_per_side": config.strakes.tank_volume_gal,
            "plans_gal_per_tank": G.fuel_book_capacity_plans_gal,
            "om_gal_per_tank": G.fuel_book_capacity_om_gal,
            "om_total_gal": G.fuel_book_capacity_om_total_gal,
            "envelope_gal_per_side": round(sb.tank_volume_gal(), 2),
            "lb_per_gal": G.fuel_book_lb_per_gal,
            "arm_fs": G.fuel_book_arm_fs,
            "note": "capacity is a conflict, kept as text: the plans print 25.5 per tank, the manual 28 per tank and 52 in all; the model keeps 26 per side; the shaded envelope is a fitted shape, not a measurement",
        },
        "conflicts": {
            "cutout_aft_top_depth": {
                "mid_in": G.stk_book_cutout_aft_in[2],
                "aft_end_in": G.stk_book_cutout_aft_top_alt_in,
            },
            "baggage_arm": {"om_fs": 90.0, "plan_centroid_fs": 80.6},
            "layup_7_numbering": ["f21.od-outlet", "f21.outside-bottom"],
        },
        "battery": {
            "fs_range": list(G.elec_book_battery_fs_range),
            "model_fs": G.elec_book_battery_model_fs,
            "status": "positioned-from-text, low: the station is on A6 (not held); drawn at the middle of the range for illustration only",
            "added_lb": G.elec_book_battery_added_lb,
            "starter_fs_min": G.elec_book_starter_fs_min,
            "relay_fs": G.elec_book_relay_fs,
        },
        "engine": {
            "down_thrust_deg": G.eng_book_down_thrust_deg,
            "crank_bl": G.eng_book_crank_bl,
            "block_in": list(G.eng_book_block_in),
            "block_fwd_fs": G.eng_book_block_fwd_fs,
            "limits_lb": [G.eng_book_engine_max_lb, G.eng_book_vibrating_max_lb],
            "oil": {"lb": G.eng_book_oil_lb, "fs": G.eng_book_oil_fs},
            "striped": ["engine.block.block"],
            "note": "installation is in Sections IIA, IIC and IIL, not held; no engine, mount, prop or exhaust station is printed",
        },
        "weights": {
            "rows": ladder + ["dynafocal_mount", "cowl_glass", "cowl_graphite"],
            "note": "CP27 page 4 N26MS empty-weight ladder, the dynafocal mount (CP26) and the cowl (CP27): reference only, in no sum",
            "closure_target": {
                "empty_lb": led["empty"]["weight_lb"],
                "empty_arm_in": led["empty"]["arm_in"],
                "cite": led["empty"]["cite"],
                **_closure_readout(led),
                "loaded_envelope_fs": [
                    led["envelope"]["fwd_fs"],
                    led["envelope"]["aft_fs"],
                ],
                "note": "the OM sample empty airplane is the closure target; FS 97 to 103 is the loaded envelope, not the empty CG",
            },
            "cg": "not yet computed",
        },
    }


# ---- chapters 24 to 26 (M2.9): covers and consoles, finishing, upholstery ---------------------------------------------------------------
M29_SHOW_FROM = {  # a part's first op (the lab shows it from here on)
    "aft_cover": "f24.aft-cover",
    "lc1": "f24.console-lc1",
    "lc2": "f24.consoles-left",
    "lc3": "f24.consoles-left",
    "lc4": "f24.consoles-left",
    "lc5": "f24.consoles-left",
    "lc6": "f24.consoles-left",
    "thigh_floor": "f24.thigh-support",
    "thigh_rib_a": "f24.thigh-support",
    "thigh_rib_b": "f24.thigh-support",
    "valve_cover": "f24.thigh-support",
    "canard_cover": "f24.canard-cover",
    "seal_right": "f24.gap-seal",
    "seal_left": "f24.gap-seal",
    "front_cushion": "f26.cushions-headrests",
    "rear_cushion": "f26.cushions-headrests",
    "front_headrest": "f26.cushions-headrests",
    "rear_headrest": "f26.cushions-headrests",
    "suitcase_right": "f26.suitcases",
    "suitcase_left": "f26.suitcases",
}
M29_LABELS = {
    "aft_cover": "Lower aft cover",
    "lc1": "Console piece LC1 (landing brake)",
    "lc2": "Console top LC2",
    "lc3": "Console side LC3",
    "lc4": "Console side LC4",
    "lc5": "Rear console top LC5",
    "lc6": "Rear console side LC6",
    "thigh_floor": "Thigh-support floor",
    "thigh_rib_a": "Thigh-support rib (notched for the fuel lines)",
    "thigh_rib_b": "Thigh-support rib",
    "valve_cover": "Fuel-valve cover",
    "canard_cover": "Canard cover",
    "seal_right": "Right gap seal",
    "seal_left": "Left gap seal",
    "front_cushion": "Front seat cushion",
    "rear_cushion": "Rear seat cushion",
    "front_headrest": "Front headrest",
    "rear_headrest": "Rear headrest",
    "suitcase_right": "Right suitcase",
    "suitcase_left": "Left suitcase (shortened)",
}


@lru_cache(maxsize=1)
def _m29_built() -> dict:
    """{part name: FusePart} for chapters 24 and 26 (core.covers_book, core.upholstery_book)."""
    from core import covers_book as cv
    from core import upholstery_book as up

    return {**cv.build_covers(), **up.build_upholstery()}


def _m29_component_parts() -> dict:
    from core import covers_book as cv
    from core import upholstery_book as up

    return {**cv.COMPONENT_PARTS, **up.COMPONENT_PARTS}


def m29_components() -> dict:
    """glb components for chapters 24 and 26 (see guide.export_glb.m29_components). A component is a group node named by its id; the children are ``<id>.<part>``.
    All solids are in the airplane frame, in place. The finish of chapter 25 is not geometry: it is the ``finish`` rows of the layup m29 section."""
    built = _m29_built()
    return {
        cid: {f"{cid}.{n}": built[n].solid.val().copy() for n in names}
        for cid, names in _m29_component_parts().items()
    }


def m29_section() -> dict:
    """layup.json["fuselage"]["extras"]["m29"]: a row per part (node, component, fidelity, label, cite, extents, the op it shows from), the finish layer (a tag per
    surface: three coats, thicknesses and colours, applied by the lab), the chapter 24 conflicts, and the weight references (never summed)."""
    from core import covers_book as cv
    from core.ledger import load_ledger

    built = _m29_built()
    ops_order = list(_op_index())
    parts: dict[str, dict] = {}
    for cid, names in _m29_component_parts().items():
        for n in names:
            part = built[n]
            bb = cq.Compound.makeCompound([part.solid.val()]).BoundingBox()
            op = M29_SHOW_FROM[n]
            parts[f"{cid}_{n}".replace(".", "_")] = {
                "node": f"{cid}.{n}",
                "component": cid,
                "fidelity": part.fidelity,
                "label": M29_LABELS[n]
                + (" (fitted shape)" if part.fidelity == "representational" else ""),
                "cite": list(part.cite),
                "fs_min": round(bb.xmin, 4),
                "fs_max": round(bb.xmax, 4),
                "bl_min": round(bb.ymin, 4),
                "bl_max": round(bb.ymax, 4),
                "show": {"from": op},
                "op_index": ops_order.index(op),
            }
    rows = load_ledger()["prototype_weights"]["rows"]
    led = load_ledger()
    return {
        "parts": parts,
        "finish": {
            "rows": cv.finish_rows(),
            "colours": {
                "white": "upper wing and canard only (book, plans-1980:p162)",
                "primer-grey": "everything else; representational, the book prints no airplane colour",
            },
            "min_temp_f": G.fin_book_min_temp_f,
            "weave_in": G.fin_book_weave_in,
            "note": "a layer drawn on the part, never a solid; no finish weight is printed in chapter 25",
        },
        "conflicts": {
            "aft_cover_plies": {
                "scan_inside_outside": list(G.cov_book_aft_cover_plies),
                "transcription_inside_outside": list(G.cov_book_aft_cover_plies_cobelu),
                "note": "the scan blanks the inside number and hand-edits the outside to one; LPC 54 says one ply; the transcription keeps one and two",
            },
            "lc2_length_in": {
                "scan": G.cov_book_lc2_len_in,
                "transcription": G.cov_book_lc2_len_cobelu_in,
            },
        },
        "seal": {
            "gap_in": G.cov_book_seal_gap_in,
            "front_gap_in": G.cov_book_seal_front_gap_in,
            "note": "the 1/2 in glyph cannot be told from 3/4 at this scan resolution",
        },
        "weights": {
            "finish_deltas": {
                k: {"weight_lb": rows[k]["weight_lb"]}
                for k in ("finish_delta_canopy", "finish_delta_aileron", "finish_delta_wing")
            },
            "note": "N26MS finish deltas (CP26 page 3 ready to finish against CP27 page 1 filled and painted): references, never summed; no finish weight is printed and the whole airplane's finish was never weighed in any held source. No upholstery weight is printed.",
            "closure_target": {
                "empty_lb": led["empty"]["weight_lb"],
                "empty_arm_in": led["empty"]["arm_in"],
                **_closure_readout(led),
                "samples": "both OM sample loadings reproduced exactly: the light pilot 103.96, outside the 103 aft limit as the manual says; the heavy pilot 101.06, inside",
                "loaded_envelope_fs": [led["envelope"]["fwd_fs"], led["envelope"]["aft_fs"]],
                "sample_loadings": [
                    {
                        "name": k,
                        "total_lb": led["samples"][k]["book_total_lb"],
                        "cg_in": led["samples"][k]["book_cg_in"],
                        "inside_envelope": led["envelope"]["fwd_fs"]
                        <= led["samples"][k]["book_cg_in"]
                        <= led["envelope"]["aft_fs"],
                    }
                    for k in ("light_pilot", "heavy_pilot")
                ],
                "note": "the OM sample empty airplane, 730 lb at FS 111.7, is the closure target; FS 97 to 103 is the loaded envelope, not the empty CG",
            },
            "cg": "not yet computed",
        },
    }


def layup_section() -> dict:
    """layup.json["fuselage"]: what the lab needs to lay, place, label and cut the chapter 4-9 parts and plies."""
    parts = _parts()
    pl = _plies()
    stack = {node: k for node, _, k in _shells()}
    shells = ply_shells()
    base, stages = _base_and_stages()
    ops: list[str] = []
    lay: dict[str, int] = {}
    nodes = {}
    for p in pl:
        if p.op not in ops:
            ops.append(p.op)
        lay[p.op] = lay.get(p.op, 0) + 1
        x0, x1 = _xrange(shells[p.node])
        nodes[p.node] = {
            "part": p.part,
            "component": component_of(p.part),
            "op": p.op,
            "op_index": ops.index(p.op),
            "op_order": lay[p.op],
            "order": p.order,
            "stack": stack[p.node],
            "cloth": p.cloth,
            "orientation_deg": p.orientation_deg,
            "where": p.where,
            "region": p.region,
            "fidelity": p.fidelity,
            "lower_bound": p.lower_bound,
            "area_in2": round(p.area_in2, 3),
            "fs_min": round(x0, 4),
            "fs_max": round(x1, 4),
        }
    part_rows = {}
    for name, part in parts.items():
        x0, x1 = _xrange(base[name])
        fwd = None
        if (
            name in BULKHEADS
        ):  # the lab lays a bulkhead flat with its forward or aft face up
            n = fp.region_faces(name, "fwd")[0].normalAt()
            fwd = [round(n.x, 6), round(n.y, 6), round(n.z, 6)]
        row = {
            "node": node_of(name),
            "component": component_of(name),
            "fidelity": part.fidelity,
            "label": part_label(name, part),
            "cite": list(part.cite),
            "fs_min": round(x0, 4),
            "fs_max": round(x1, 4),
            "fwd_normal": fwd,
        }
        if part.void:
            row["void"] = True
        if name in SHOW:
            row["show"] = dict(SHOW[name])
        part_rows[name] = row
    keep = tuple(f"f{c:02d}." for c in EXPORT_CHAPTERS)
    excluded = [
        {"op": op, "where": where, "reason": reason, "parts": list(affected)}
        for (op, where), (reason, affected) in fp.EXCLUDED.items()
        if op.startswith(keep)
    ]
    gh = {
        "axle_fs": G.fs_main_axle,
        "board_fs": G.fs_spar_aft_face,
        "board_bl": G.bl_gear_datum,
        "axle_fwd_of_board_in": G.main_axle_fwd_of_spar,
        "axle_z": round(fb.z_of_wl(G.wl_main_axle), 4),
        "cite": "plans-1980:p50 figure 1A (axle C.L. F.S. 110.5, 15 in forward of the board at the spar aft face); plans-1980:p171",
    }
    return {
        "chapters": list(CHAPTERS),
        "frame": "inches as exported: x = FS, y = B.L., z = W.L. - 17.4",
        "ply_thickness_in": PLY_T,
        "ply_thickness_note": "visual, not to scale",
        "ops": ops,
        "parts": part_rows,
        "nodes": nodes,
        "stages": {
            n: [{"from": op, "node": node} for op, node, _ in st]
            for n, st in stages.items()
        },
        "bank_deg": dict(BANK_DEG),
        "bank_note": "positive = left bank, the right side up (core.landing_gear_book.bank_pose); plans-1980:p46",
        "gear_marks": gh,
        "excluded": excluded + _ch9_excluded(),
        "extras": {
            **extras_section(),
            "m25": m25_section(),
            "m26": m26_section(),
            "m27": m27_section(),
            "m28": m28_section(),
            "m29": m29_section(),
        },
        "plan_bend": [[round(x, 4), round(h, 4)] for x, h in plan_bend_points()],
    }
