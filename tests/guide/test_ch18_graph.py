"""Chapter 18 (canopy) in the committed graph."""

from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH18 = [
    "f18.trim-plexi",
    "f18.locate-blocks",
    "f18.check-ab",
    "f18.foam-core",
    "f18.carve-outside",
    "f18.glass-outside",
    "f18.cut-remove",
    "f18.carve-inside",
    "f18.pads-inside-glass",
    "f18.rear-cover-inside",
    "f18.vent-brace",
    "f18.hinges",
    "f18.door",
    "f18.latches",
    "f18.front-cover",
    "f18.safety-catch",
]
COMPONENTS = {
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


def text(op):
    return " ".join(
        [op.title, op.summary, *op.completion, *(c.note for c in op.changes)]
    )


def test_sixteen_ops_valid_and_no_unknown_ids(g):
    assert [o.id for o in g.ops.values() if o.chapter == 18] == CH18
    assert validate(g) == []
    for i in CH18:
        op = g.ops[i]
        assert all(r in g.ops for r in op.requires), i
        assert all(c in g.components for c in op.components), i
        assert op.sources and 2 <= len(op.completion) <= 6 and not op.stub, i
        assert all(
            108 <= s.scan_pp <= 117 for s in op.sources if s.doc == "scan-1980"
        ), i
        assert "c03.layup-skills" in needs(g, i) | {i}, i


def test_order_follows_the_plans_with_the_door_before_the_latches(g):
    order = topo_order(g)
    pos = {i: order.index(i) for i in CH18}
    assert "f18.door" in g.ops["f18.latches"].requires
    assert pos["f18.door"] < pos["f18.latches"] < pos["f18.safety-catch"]
    assert pos["f18.cut-remove"] < pos["f18.carve-inside"] < pos["f18.pads-inside-glass"]
    assert pos["f18.glass-outside"] < pos["f18.cut-remove"]
    assert "f18.cut-remove" in needs(g, "f18.front-cover")
    assert "f18.hinges" in g.ops["f18.latches"].requires


def test_earlier_chapters_come_first(g):
    n = needs(g, "f18.locate-blocks")
    assert {"f05.top-longeron-glass", "f06.bond-panel", "f06.f28-install"} <= n
    assert {"f06.bond-firewall", "f14.fit-fuselage", "f08.roll-over-outside"} <= n
    assert "f07.skin-left" in needs(g, "f18.door")
    assert "f06.bond-firewall" in needs(g, "f18.hinges")
    # nothing earlier waits on the canopy
    assert not [o.id for o in g.ops.values() if o.chapter < 18 and needs(g, o.id) & set(CH18)]


def test_components_are_the_agreed_set_all_with_geometry(g):
    used = {c for i in CH18 for c in g.ops[i].components}
    assert used == COMPONENTS and COMPONENTS <= set(g.components)
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)


def test_book_values_are_in_the_ops_and_the_conflicts_are_flagged(g):
    assert "FS 117" in text(g.ops["f18.cut-remove"])
    assert "unnamed" in text(g.ops["f18.cut-remove"])
    t = text(g.ops["f18.latches"])
    assert "104" in t and "0.75" in t and "unresolved" in t
    assert "56.75" in text(g.ops["f18.safety-catch"])
    assert "4.3 by 3.7" in text(g.ops["f18.door"])
    chk = text(g.ops["f18.check-ab"])
    assert "13.5" in chk and "12.3" in chk and "WL 23" in chk
    assert (27, 43) in {(c.cp, c.lpc) for c in g.ops["f18.hinges"].changes}
    assert "right" in g.ops["f18.hinges"].summary
    assert "left" in g.ops["f18.latches"].summary


def test_pad_plies_and_schedule(g):
    rows = g.ops["f18.pads-inside-glass"].materials
    assert rows[0]["plies"] == 15
    glass = g.ops["f18.glass-outside"].materials
    assert {(m["cloth"], m["plies"]) for m in glass} == {("BID", 2), ("UND", 2), ("BID", 3)}


def test_own_words(g):
    for loc, t in authored_texts(g):
        assert isinstance(t, str) and "‑" not in t and len(t) < 700, loc
