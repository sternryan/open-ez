"""Per-ply areas for the fuselage box (chapters 4-6): scope, geometry, counts, fidelity."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from core import fuselage_plies as fp
from core.fuselage_book import build_fuselage
from guide.schema import load_graph

ROOT = Path(__file__).resolve().parents[1]
GRAPH = load_graph(ROOT / "guide" / "graph")
ROWS = fp.material_rows(GRAPH)


@pytest.fixture(scope="module")
def plies():
    return fp.plies(GRAPH)


@pytest.fixture(scope="module")
def parts():
    return build_fuselage()


def test_material_rows_cover_chapters_4_to_6():
    assert len(ROWS) == 25
    assert {op.split(".")[0] for op, _ in ROWS} == {"f04", "f05", "f06"}


def test_every_row_is_mapped_or_excluded():
    assert fp.scope_problems(ROWS, set(GRAPH.ops)) == []
    assert not set(fp.SCOPE) & set(fp.EXCLUDED)
    assert set(fp.SCOPE) | set(fp.EXCLUDED) == set(ROWS)  # nothing stale either


def test_scope_check_fails_on_an_unmapped_row():
    probs = fp.scope_problems(
        ROWS + [("f06.bottom-tape", "a row nobody placed")], set(GRAPH.ops)
    )
    assert len(probs) == 1 and "a row nobody placed" in probs[0]
    # dropping a real mapping must also fail the check
    scope = dict(fp.SCOPE)
    dropped = next(iter(scope))
    del scope[dropped]
    probs = fp.scope_problems(ROWS, set(GRAPH.ops), scope=scope)
    assert any(dropped[1] in p for p in probs)


def test_plies_refuses_an_unscoped_graph_row():
    with pytest.raises(fp.FusePlyError):
        fp.plies(GRAPH, extra_rows=[("f06.bottom-tape", "a row nobody placed")])


def test_every_exclusion_has_a_reason_and_a_part():
    for key, (reason, affected) in fp.EXCLUDED.items():
        assert len(reason) > 20, key
        assert affected and all(p in build_fuselage() for p in affected), key


def test_every_ply_area_is_positive(plies):
    assert plies
    for p in plies:
        assert p.area_in2 > 0 and math.isfinite(p.area_in2), p.node


# Independent of the region code: choose the face by its normal in the test itself.
def _faces_area(part, direction, thr):
    tot = 0.0
    for f in part.solid.faces().vals():
        n = f.normalAt()
        if n.x * direction[0] + n.y * direction[1] + n.z * direction[2] >= thr:
            tot += f.Area()
    return tot


def _largest(part, direction, thr):
    best = 0.0
    for f in part.solid.faces().vals():
        n = f.normalAt()
        if n.x * direction[0] + n.y * direction[1] + n.z * direction[2] >= thr:
            best = max(best, f.Area())
    return best


@pytest.mark.parametrize(
    "part,op",
    [
        ("f22", "f04.panel-f22-f28-aft"),
        ("f28", "f04.panel-f22-f28-fwd"),
        ("firewall", "f04.firewall-fwd"),
    ],
)
def test_plate_ply_areas_match_the_box(parts, plies, part, op):
    bb = parts[part].solid.val().BoundingBox()
    box = (bb.ymax - bb.ymin) * (bb.zmax - bb.zmin)
    mine = [p for p in plies if p.part == part and p.op == op]
    assert mine
    for p in mine:
        assert p.area_in2 == pytest.approx(box, rel=0.005)


FACE_CASES = [
    # (part, op, where-substring, direction, threshold, all-faces-or-largest)
    (
        "front_seat_bkhd",
        "f04.front-seat-bkhd-front",
        "front face",
        (-1, 0, 0),
        0.5,
        "largest",
    ),
    (
        "front_seat_bkhd",
        "f04.front-seat-bkhd-back",
        "back face",
        (1, 0, 0),
        0.5,
        "largest",
    ),
    ("panel", "f04.panel-f22-f28-aft", "aft faces", (1, 0, 0), 0.9, "largest"),
    ("panel", "f04.panel-f22-f28-fwd", "forward faces", (-1, 0, 0), 0.9, "largest"),
    ("f28", "f04.panel-f22-f28-fwd", "forward faces", (-1, 0, 0), 0.9, "largest"),
    ("firewall", "f04.firewall-aft", "aft face", (1, 0, 0), 0.9, "largest"),
    ("bottom", "f06.bottom-glass", "whole bottom", (0, 0, 1), 0.9, "largest"),
    ("side_right", "f05.inside-layup", "inside face", (0, -1, 0), 0.9, "all"),
    ("side_left", "f05.inside-layup", "inside face", (0, 1, 0), 0.9, "all"),
]


@pytest.mark.parametrize("part,op,frag,direction,thr,how", FACE_CASES)
def test_face_ply_area_equals_measured_face(
    parts, plies, part, op, frag, direction, thr, how
):
    f = _faces_area if how == "all" else _largest
    want = f(parts[part], direction, thr)
    mine = [p for p in plies if p.part == part and p.op == op and frag in p.where]
    assert mine, (part, op)
    for p in mine:
        assert p.area_in2 == pytest.approx(want, rel=0.005), p.node


def test_rear_bulkhead_plies_count_the_access_hole_once(parts, plies):
    # The solid already has the 7 in hole, so the measured face lacks it; subtracting it again was
    # a bug the captain caught (the UND read 244.8 in^2 against a 283.3 in^2 face).
    from config import config

    g = config.geometry
    fwd = _largest(parts["rear_seat_bkhd"], (-1, 0, 0), 0.5)
    aft = _largest(parts["rear_seat_bkhd"], (1, 0, 0), 0.5)
    hole = math.pi / 4 * g.rear_seat_bkhd_access_dia**2
    trapezoid = (g.rear_seat_bkhd_bottom_width + g.rear_seat_bkhd_top_width) / 2 * 16.5
    assert fwd < trapezoid - hole + 5  # the hole is in the solid's face
    und = [p for p in plies if p.part == "rear_seat_bkhd" and p.cloth == "UND"]
    bid = [p for p in plies if p.part == "rear_seat_bkhd" and p.op == "f04.rear-seat-bkhd-hole"]
    assert len(und) == 2 and len(bid) == 2
    for p in und:
        assert p.area_in2 == pytest.approx(fwd, rel=0.005)
    for p in bid:  # p34 C-C: the BID covers the back face (pocket walls not counted: lower bound)
        assert p.area_in2 == pytest.approx(aft, rel=0.005) and p.lower_bound

def test_bottom_corner_tape_is_length_times_stated_width(plies):
    (tape,) = [p for p in plies if p.op == "f06.bottom-tape"]
    assert tape.region.startswith("corner tape")
    assert tape.area_in2 == pytest.approx(
        2.0 * fp.corner_tape_length("bottom"), rel=1e-6
    )
    assert tape.lower_bound  # bulkhead-to-bottom corners are not counted
    assert 2 * 90 < tape.area_in2 < 2 * 260


def test_ply_count_per_op_matches_rows(plies):
    want: dict[str, int] = {}
    for op_id, op in GRAPH.ops.items():
        if op.chapter not in (4, 5, 6):
            continue
        for m in op.materials:
            key = (op_id, m["where"])
            if key in fp.EXCLUDED:
                continue
            want[op_id] = want.get(op_id, 0) + int(m["plies"]) * len(
                fp.SCOPE[key].targets
            )
    got: dict[str, int] = {}
    for p in plies:
        got[p.op] = got.get(p.op, 0) + 1
    assert got == want


def test_nodes_are_unique_and_ordered_per_part(plies):
    nodes = [p.node for p in plies]
    assert len(nodes) == len(set(nodes))
    by_part: dict[str, list] = {}
    for p in plies:
        by_part.setdefault(p.part, []).append(p)
    for part, ps in by_part.items():
        assert [p.order for p in ps] == list(range(1, len(ps) + 1)), part
        assert all(p.node == f"fuselage.{part}.p{p.order}" for p in ps)
        ops = [p.op_index for p in ps]
        assert ops == sorted(ops), part


def test_orientations_follow_the_rows(plies):
    side = [p for p in plies if p.part == "side_right" and p.op == "f05.inside-layup"]
    assert [p.orientation_deg for p in side] == [30, -30]
    assert all(p.cloth == "UND" for p in side)
    fsb = [
        p
        for p in plies
        if p.part == "front_seat_bkhd" and p.op == "f04.front-seat-bkhd-front"
    ]
    assert [p.orientation_deg for p in fsb] == [45, -45]
    bottom = [p for p in plies if p.part == "bottom" and p.op == "f06.bottom-glass"]
    assert [p.orientation_deg for p in bottom] == [45, 45]
    # the plans say orientation is not critical on the panel/F22/F28 aft faces
    assert all(
        p.orientation_deg is None for p in plies if p.op == "f04.panel-f22-f28-aft"
    )


def test_ply_fidelity_is_inherited_from_the_part(parts, plies):
    for p in plies:
        assert p.fidelity == parts[p.part].fidelity, p.node
    rep = {n for n, part in parts.items() if part.fidelity == "representational"}
    assert {"f22", "f28", "panel", "firewall", "bottom"} <= rep
    assert {p.part for p in plies if p.fidelity == "representational"} == rep & {
        p.part for p in plies
    }


def test_wrapped_and_partial_regions_are_flagged_lower_bound(plies):
    lb = {(p.part, p.op) for p in plies if p.lower_bound}
    assert ("front_seat_bkhd", "f04.front-seat-bkhd-front") in lb
    assert ("front_seat_bkhd", "f04.front-seat-bkhd-back") in lb
    assert ("bottom", "f06.bottom-glass") in lb
    assert ("firewall", "f04.firewall-aft") not in lb


def test_ply_arms_lie_inside_their_part(parts, plies):
    for p in plies:
        bb = parts[p.part].solid.val().BoundingBox()
        assert bb.xmin - 1e-6 <= p.arm_in <= bb.xmax + 1e-6, p.node
