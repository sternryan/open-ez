"""Chapter 20 (winglets and rudders) in the committed graph."""

from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH20 = [
    "f20.cut-cores",
    "f20.skins",
    "f20.trim",
    "f20.jig",
    "f20.inside-layups",
    "f20.outside-layups",
    "f20.lower-fin",
    "f20.rudder-cut",
    "f20.rudder-hang",
]
COMPONENTS = {
    "winglet.cores",
    "winglet.skins",
    "winglet.jig",
    "winglet.layups",
    "winglet.block_a",
    "winglet.lower_fin",
    "winglet.rudder",
    "winglet.rudder_hinge",
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


def test_nine_ops_valid_and_no_unknown_ids(g):
    assert [o.id for o in g.ops.values() if o.chapter == 20] == CH20
    assert validate(g) == []
    for i in CH20:
        op = g.ops[i]
        assert all(r in g.ops for r in op.requires), i
        assert all(c in g.components for c in op.components), i
        assert op.sources and 2 <= len(op.completion) <= 6 and not op.stub, i
        assert all(
            135 <= s.scan_pp <= 140 for s in op.sources if s.doc == "scan-1980"
        ), i
        assert "c03.layup-skills" in needs(g, i) | {i}, i


def test_order_and_the_rudder_stub_is_replaced(g):
    order = topo_order(g)
    assert [i for i in order if i in CH20] == [
        "f20.cut-cores",
        "f20.skins",
        "f20.trim",
        "f20.jig",
        "f20.inside-layups",
        "f20.outside-layups",
        "f20.lower-fin",
        "f20.rudder-cut",
        "f20.rudder-hang",
    ]
    assert "f20.rudder-hang" in g.ops["f16.rudder-cable-rig"].requires
    assert "c20.winglets" not in g.ops
    assert "f20.rudder-cut" in g.ops["f20.rudder-hang"].requires


def test_earlier_chapters_come_first(g):
    assert "f19.cut-cores" in needs(g, "f20.cut-cores")
    assert "f19.top-skin" in needs(g, "f20.jig")
    assert {"f20.trim", "f19.top-skin"} <= set(g.ops["f20.jig"].requires)
    assert not [
        o.id for o in g.ops.values() if o.chapter < 16 and needs(g, o.id) & set(CH20)
    ]


def test_components_are_the_agreed_set_all_with_geometry(g):
    used = {c for i in CH20 for c in g.ops[i].components}
    assert used == COMPONENTS and COMPONENTS <= set(g.components)
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)
    assert all(g.ops[i].geometry_visible for i in CH20)


def test_book_values_are_in_the_ops(g):
    jig = text(g.ops["f20.jig"])
    for v in ("102.15", "108.35", "118.35", "149.6", "55.5", "0.05"):
        assert v in jig, v
    assert (25, 6) in {(c.cp, c.lpc) for c in g.ops["f20.jig"].changes}
    cut = text(g.ops["f20.rudder-cut"])
    for v in ("176.8", "12.14", "11.5", "14.5", "10.5"):
        assert v in cut, v
    assert "30 deg" in text(g.ops["f20.rudder-hang"])
    assert "9.8" in text(g.ops["f20.lower-fin"])
    sk = g.ops["f20.skins"]
    assert (34, 104) in {(c.cp, c.lpc) for c in sk.changes}
    assert "66.4" in text(sk) and "65.4" in text(sk)


def test_corner_ply_table_is_whole_and_the_tip_chord_is_not_stated_as_a_page_value(g):
    t = text(g.ops["f20.outside-layups"]) + " ".join(
        m["where"] for m in g.ops["f20.outside-layups"].materials
    )
    for pair in ("24/12", "22/11", "20/10", "18/9", "16/8", "14/7", "12/6"):
        assert pair in t, pair
    everything = " ".join(text(g.ops[i]) for i in CH20)
    assert "28.9" not in everything
    assert "11.4" not in everything.replace("11.45", "")


def test_own_words(g):
    for loc, t in authored_texts(g):
        if loc.startswith("f20."):
            assert isinstance(t, str) and "‑" not in t and len(t) < 700, loc


def test_book_order_the_wing_waiters_follow_their_chapter(g):
    """Chapters 17 and 18 come before 19 and 20; the two ch16 ops that wait on the wing and
    the winglet are walked right after the chapter they wait on."""
    order = topo_order(g)
    pos = {i: k for k, i in enumerate(order)}
    ch = lambda n: [i for i in order if g.ops[i].chapter == n]
    assert max(pos[i] for i in ch(18)) < pos["f19.jig"]
    assert max(pos[i] for i in ch(17)) < pos["f19.jig"]
    assert pos["f19.attach"] < pos["f16.aileron-linkage"] < pos["f20.cut-cores"]
    assert pos["f20.rudder-hang"] < pos["f16.rudder-cable-rig"]
    # ch16 minus the two deferred ops is all ahead of chapter 17
    held = {"f16.aileron-linkage", "f16.rudder-cable-rig", "f16.brake-cables"}
    assert (
        max(
            pos[i] for i in ch(16) if i not in held and pos[i] < pos["f17.mount-blocks"]
        )
        < pos["f17.mount-blocks"]
    )
