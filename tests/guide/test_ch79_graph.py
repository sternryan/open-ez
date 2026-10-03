"""Chapters 7-9 (exterior skins, roll-over structure, main gear) in the committed graph: ids, order, prerequisites, data."""

from pathlib import Path

import pytest

from guide.schema import load_graph, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

IDS = {
    7: [
        "f07.carve-corners",
        "f07.canard-cutout",
        "f07.fuel-gauge-area",
        "f07.belt-insert",
        "f07.skin-right",
        "f07.skin-left",
    ],
    8: [
        "f08.roll-over-foam",
        "f08.roll-over-inside",
        "f08.roll-over-bond",
        "f08.roll-over-outside",
        "f08.access-holes",
        "f08.shoulder-harness",
        "f08.belt-attach",
        "f08.step",
    ],
    9: [
        "f09.strut-stiffen",
        "f09.jig-blocks",
        "f09.position-gear",
        "f09.tab-layup",
        "f09.tab-assembly",
        "f09.axles-brakes",
        "f09.brake-lines",
    ],
}


@pytest.fixture(scope="module")
def g():
    return load_graph(GRAPH)


def needs(g, op_id):
    seen, stack = set(), [op_id]
    while stack:
        for r in g.ops[stack.pop()].requires:
            if r not in seen:
                seen.add(r)
                stack.append(r)
    return seen


def test_ops_exist_in_book_order(g):
    assert sum(len(v) for v in IDS.values()) == 21
    for ch, ids in IDS.items():
        assert [o.id for o in g.ops.values() if o.chapter == ch] == ids
    assert validate(g) == []


def test_every_op_is_complete_and_reaches_layup_skills(g):
    for ids in IDS.values():
        for i in ids:
            op = g.ops[i]
            assert (
                not op.stub and op.summary.strip() and op.completion and op.sources
            ), i
            assert "c03.layup-skills" in needs(g, i), i
            assert op.components, i


def test_roll_order_and_prerequisites(g):
    assert "f07.skin-right" in g.ops["f07.skin-left"].requires
    assert "f07.skin-right" in needs(g, "f07.skin-left")
    ids = list(g.ops)
    assert ids.index("f07.skin-right") < ids.index("f07.skin-left")
    pos = needs(g, "f09.position-gear")
    assert {"f09.jig-blocks", "f09.strut-stiffen"} <= set(
        g.ops["f09.position-gear"].requires
    )
    assert "f05.gear-extrusions" in pos
    assert "f07.skin-left" in g.ops["f08.roll-over-bond"].requires
    assert "f07.skin-left" in needs(
        g, "f08.belt-attach"
    ) and "f07.belt-insert" in needs(g, "f08.belt-attach")


def test_materials_parse(g):
    for ids in IDS.values():
        for i in ids:
            for m in g.ops[i].materials:
                assert (
                    m["cloth"] in {"UND", "BID"}
                    and isinstance(m["plies"], int)
                    and m["plies"] > 0
                    and m["where"]
                ), (i, m)
    third = [m for m in g.ops["f07.skin-right"].materials if m["plies"] == 3]
    assert third and "FS 60 to 110" in third[0]["where"]


def test_change_links(g):
    got = {
        (c.cp, c.lpc): (o.id, c.status)
        for o in g.ops.values()
        if o.chapter in (7, 8, 9)
        for c in o.changes
    }
    for key, op in {
        (27, 46): "f07.canard-cutout",
        (27, 50): "f07.canard-cutout",
        (26, 37): "f08.roll-over-foam",
        (27, 52): "f08.roll-over-inside",
        (26, 35): "f09.strut-stiffen",
        (36, 112): "f09.position-gear",
        (27, 45): "f09.axles-brakes",
        (30, 83): "f09.tab-assembly",
        (31, 89): "f09.brake-lines",
    }.items():
        assert got[key][0] == op, key
        assert got[key][1] in {"verified", "conflict", "unresolved"}
    assert (26, 34) in {(c.cp, c.lpc) for c in g.ops["f05.gear-extrusions"].changes}


def test_position_gear_states_the_book_axle_station(g):
    op = g.ops["f09.position-gear"]
    assert "110.5" in op.summary and "15 in" in op.summary
    assert any(s.scan_pp == 171 for s in op.sources)
    assert "fitted" in " ".join(g.ops["f09.jig-blocks"].completion + op.completion)
