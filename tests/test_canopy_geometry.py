"""M2.6 installed canopy geometry: bubble, frame, pads, covers, hinges, latches, catch, door.

Stations are asserted against literal book numbers, not against the builders' own constants.
"""

import ast
import io
import tokenize
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from core import canopy_book as cb
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl

REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
    "canopy.plexi",
    "canopy.frame",
    "canopy.pads",
    "canopy.blocks",
    "canopy.vent",
    "canopy.brace_tubes",
    "canopy.hinges",
    "canopy.latches",
    "canopy.safety_catch",
    "fuselage.front_cover",
    "fuselage.rear_cover",
    "fuselage.door",
}
Z_SILL = z_of_wl(23.0)


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def vol_of(wp) -> float:
    return sum(volume(s) for s in wp.vals())


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


def bb(wp):
    return comp(wp).BoundingBox()


@pytest.fixture(scope="module")
def parts():
    return cb.build_canopy()


@pytest.fixture(scope="module")
def fus():
    return build_fuselage()


def test_every_component_has_parts_and_the_graph_agrees(parts):
    from guide.schema import load_graph

    assert set(cb.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    g = load_graph(REPO / "guide" / "graph")
    for cid in EXPECTED_COMPONENTS:
        assert g.components[cid].fidelity == "unvalidated", cid
    used = [n for names in cb.COMPONENT_PARTS.values() for n in names]
    assert sorted(used) == sorted(parts)  # every part in exactly one component


def test_every_solid_has_positive_volume_a_fidelity_and_valid_cites(parts):
    for name, p in parts.items():
        assert vol_of(p.solid) > 1e-6, name
        assert p.fidelity in FIDELITIES, name
        assert p.fidelity == "representational" or p.cite, name
        assert p.cite, name
        for s in p.solid.solids().vals():
            assert s.isValid(), name
    # nothing here is a book-shaped solid: the bubble, covers and hardware are fitted
    assert {p.fidelity for p in parts.values()} == {"representational"}


def test_rear_cut_is_fs_117_front_cut_is_about_41_65(parts):
    assert bb(parts["frame"].solid).xmax == pytest.approx(117.0, abs=1e-3)
    assert bb(parts["rear_cover"].solid).xmin == pytest.approx(117.0, abs=1e-3)
    assert bb(parts["rear_cover"].solid).xmax == pytest.approx(125.0, abs=1e-3)
    assert bb(parts["frame"].solid).xmin == pytest.approx(41.65, abs=1e-3)
    assert bb(parts["front_cover"].solid).xmax == pytest.approx(41.65, abs=1e-3)


def test_plexi_is_68_long_with_the_nose_5_aft_of_the_panel(parts):
    b = bb(parts["plexi"].solid)
    assert b.xmin == pytest.approx(39.75 + 5.0, abs=1e-3)
    assert b.xmax - b.xmin == pytest.approx(68.0, abs=1e-3)


def _top_at(part, fs):
    slab = cq.Workplane("XY").box(0.02, 1.0, 80, centered=(True, True, False)).translate((fs, 0, -30))
    return part.solid.intersect(slab).val().BoundingBox().zmax


def test_checks_a_and_b_are_met(parts):
    # A: top at least WL 36.5 (13.5 above WL 23) 6 in forward of the headrest; B: WL 35.3 (12.3 above) at FS 110
    z_a_min = z_of_wl(36.5)
    z_b = z_of_wl(35.3)
    top_a = max(_top_at(parts["plexi"], fs) for fs in (80.0, 82.0, 84.0, 86.0))
    assert top_a >= z_a_min - 1e-6
    assert _top_at(parts["plexi"], 110.0) == pytest.approx(z_b, abs=0.02)
    # the bubble is the highest thing in the fuselage-plus-canopy there (above the roll-over peak, WL 35.6)
    assert top_a > z_of_wl(35.6) + 0.5


PAD_AFT_EDGES = {
    "pads_hinge": (20.0, 25.5, 48.0, 53.5),
    "pads_latch": (11.0, 41.0, 71.0),
    "pad_catch": (59.0,),
}


@pytest.mark.parametrize("name,edges", PAD_AFT_EDGES.items())
def test_pad_stations_and_sides(parts, name, edges):
    sols = parts[name].solid.solids().vals()
    assert len(sols) == len(edges)
    got = sorted((s.BoundingBox().xmin, s.BoundingBox().xmax) for s in sols)
    want = sorted((117.0 - e - 2.5, 117.0 - e) for e in edges)
    for (a0, a1), (w0, w1) in zip(got, want):
        assert a0 == pytest.approx(w0, abs=1e-6) and a1 == pytest.approx(w1, abs=1e-6)
    for s in sols:  # hinge pads on the right (BL > 0), latch and catch pads on the left
        yc = s.Center().y
        assert (yc > 0) == (name == "pads_hinge")
        assert abs(yc) > 9.0


def test_safety_catch_is_at_fs_56_75_on_the_left(parts):
    for n in ("sc1", "sc1_bolt"):
        c = bb(parts[n].solid)
        assert (c.xmin + c.xmax) / 2 == pytest.approx(56.75, abs=1e-6), n
        assert c.ymax < 0, n
    pad = bb(parts["pad_catch"].solid)
    assert (pad.xmin + pad.xmax) / 2 == pytest.approx(56.75, abs=1e-6)  # 117 - 59 - 1.25


def test_hinges_are_on_the_right_and_latches_door_and_catch_on_the_left(parts):
    for n in ("hinge_fuselage", "hinge_canopy"):
        assert bb(parts[n].solid).ymin > 0, n
    sols = parts["hinge_canopy"].solid.solids().vals()
    spans = sorted((s.BoundingBox().xmin, s.BoundingBox().xmax) for s in sols)
    assert spans == [pytest.approx((61.0, 69.0)), pytest.approx((89.0, 97.0))]
    for n in ("latches", "sc1", "sc1_bolt", "door"):
        assert bb(parts[n].solid).ymax < 0, n


def test_latch_fittings_are_at_the_derived_centres_not_the_printed_labels(parts):
    fittings = [
        s
        for s in parts["latches"].solid.solids().vals()
        if s.BoundingBox().xmax - s.BoundingBox().xmin < 2.0
    ]
    centres = sorted((s.BoundingBox().xmin + s.BoundingBox().xmax) / 2 for s in fittings)
    assert centres == pytest.approx([44.75, 74.75, 104.75])  # the p117 labels read 44, 74, 104
    rods = [
        s
        for s in parts["latches"].solid.solids().vals()
        if s.BoundingBox().xmax - s.BoundingBox().xmin > 20
    ]
    assert len(rods) == 2
    assert all(s.BoundingBox().xmax - s.BoundingBox().xmin == pytest.approx(28.4) for s in rods)


def test_door_is_4_3_by_3_7_on_the_left(parts):
    b = bb(parts["door"].solid)
    assert b.xmax - b.xmin == pytest.approx(4.3)
    assert b.zmax - b.zmin == pytest.approx(3.7)
    assert b.ymax < 0


def test_canopy_sits_on_the_top_longerons(parts, fus):
    lon = bb(fus["top_longeron_right"].solid)
    assert lon.zmax == pytest.approx(Z_SILL)
    for n in ("plexi", "frame", "pads_hinge", "pads_latch", "pad_catch"):
        assert bb(parts[n].solid).zmin == pytest.approx(Z_SILL, abs=1e-6), n
    # base outline stays on the side's top edge: inside its outer face at every station
    pl = bb(parts["plexi"].solid)
    assert pl.ymax <= 12.3 and pl.ymin >= -12.3
    assert bb(parts["frame"].solid).ymax == pytest.approx(12.3, abs=1e-6)


def test_no_canopy_solid_overlaps_the_fuselage_or_another_canopy_part(parts, fus):
    for n, p in parts.items():
        for fname, f in fus.items():
            if f.void:
                continue
            a, b = comp(p.solid), comp(f.solid)
            ba, bbx = a.BoundingBox(), b.BoundingBox()
            if (
                ba.xmax < bbx.xmin
                or bbx.xmax < ba.xmin
                or ba.ymax < bbx.ymin
                or bbx.ymax < ba.ymin
                or ba.zmax < bbx.zmin
                or bbx.zmax < ba.zmin
            ):
                continue
            assert volume(a.intersect(b)) < 1e-4, (n, fname)
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert volume(comp(parts[a].solid).intersect(comp(parts[b].solid))) < 1e-4, (a, b)


def test_canopy_clears_the_roll_over_structure(parts, fus):
    """The frame bears on the roll-over's canopy insert (ch8) only in the real airplane; here nothing touches it."""
    for n in ("plexi", "frame", "brace_tubes", "vent"):
        d = BRepExtrema_DistShapeShape(comp(parts[n].solid).wrapped, comp(fus["rollover"].solid).wrapped)
        d.Perform()
        assert d.Value() > 0.5, n


def test_open_pose_turns_the_canopy_about_the_right_hinge_line(parts):
    pts = {n: p.solid for n, p in parts.items()}
    c = bb(pts["plexi"])
    o90 = cb.build_canopy(90.0)
    assert o90["plexi"].fidelity == "representational"
    b = bb(o90["plexi"].solid)
    # a quarter turn about the hinge line: the old top now points out to the right at the same distance from the line,
    # and the old left edge points up at its distance from the line
    assert b.ymax == pytest.approx(cb.HINGE_Y + (c.zmax - cb.HINGE_Z), abs=0.05)
    assert b.zmax == pytest.approx(cb.HINGE_Z + (cb.HINGE_Y - c.ymin), abs=0.05)
    assert b.ymin > cb.HINGE_Y - 1.5  # nothing is left over the fuselage
    # parts that stay on the fuselage do not move
    for n in ("hinge_fuselage", "sc1_bolt", "door", "front_cover", "rear_cover", "blocks"):
        assert bb(o90[n].solid).xmin == pytest.approx(bb(pts[n]).xmin)
        assert bb(o90[n].solid).ymax == pytest.approx(bb(pts[n]).ymax)
        assert bb(o90[n].solid).zmax == pytest.approx(bb(pts[n]).zmax)
    # closed = the same solids
    assert cb.build_canopy(0.0)["plexi"].solid is parts["plexi"].solid


def test_open_pose_keeps_the_hinge_line_fixed():
    y, z = cb.HINGE_Y, cb.HINGE_Z
    probe = cq.Workplane("YZ").circle(0.01).extrude(10.0).translate((60.0, y, z))
    for deg in (15.0, 45.0, 90.0, cb.MAX_OPEN_DEG):
        b = bb(cb.open_pose(probe, deg))
        assert (b.xmin, b.xmax) == pytest.approx((60.0, 70.0), abs=1e-6)
        assert (b.ymin + b.ymax) / 2 == pytest.approx(y, abs=1e-6)
        assert (b.zmin + b.zmax) / 2 == pytest.approx(z, abs=1e-6)
    # the pins are the hinge line and stay put in every pose
    for deg in (0.0, 60.0, cb.MAX_OPEN_DEG):
        pins = cb.build_canopy(deg)["hinge_fuselage"].solid
        cyl = [s for s in pins.solids().vals() if s.BoundingBox().ymax - s.BoundingBox().ymin < 0.5 and s.BoundingBox().zmax - s.BoundingBox().zmin < 0.5]
        assert len(cyl) == 2
        for s in cyl:
            c = s.Center()
            assert (c.y, c.z) == pytest.approx((y, z), abs=1e-6)


def test_open_pose_range_and_the_15_deg_past_vertical():
    assert cb.MAX_OPEN_DEG == 105.0  # 90 + the printed 15 degrees past vertical (representational arc)
    with pytest.raises(ValueError):
        cb.open_pose(cq.Workplane("XY").box(1, 1, 1), 106.0)
    with pytest.raises(ValueError):
        cb.open_pose(cq.Workplane("XY").box(1, 1, 1), -1.0)


def test_fitted_constants_carry_the_comment_on_the_statement():
    src = (REPO / "core" / "canopy_book.py").read_text()
    lines = src.splitlines()
    seen = 0
    for node in ast.parse(src).body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("FITTED_")
        ):
            seen += 1
            toks = [
                t
                for t in tokenize.generate_tokens(io.StringIO("\n".join(lines[node.lineno - 1 : node.end_lineno])).readline)
                if t.type == tokenize.COMMENT
            ]
            assert any("fitted, not book" in t.string for t in toks), node.targets[0].id
    assert seen >= 30


def test_no_hard_coded_fuselage_numbers_for_the_longeron_or_half_width():
    src = (REPO / "core" / "canopy_book.py").read_text()
    for banned in ("11.5", "12.3", "5.6", "8.07", "9.47"):
        assert banned not in src, banned
