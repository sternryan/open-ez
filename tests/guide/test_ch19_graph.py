"""Chapter 19 (wings) in the committed graph."""

from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH19 = [
    "f19.jig",
    "f19.cut-cores",
    "f19.core-cutouts",
    "f19.mount-cores",
    "f19.hardpoints",
    "f19.shear-web",
    "f19.pads-plates",
    "f19.le-cores",
    "f19.bottom-cap",
    "f19.bottom-skin",
    "f19.top-cap",
    "f19.rudder-conduit",
    "f19.top-skin",
    "f19.ribs",
    "f19.aileron-cut",
    "f19.aileron-build",
    "f19.controls",
    "f19.attach",
]
COMPONENTS = {
    "wing.jigs",
    "wing.cores",
    "wing.hardpoints",
    "wing.shear_web",
    "wing.spar_caps",
    "wing.skins",
    "wing.conduit",
    "wing.ribs",
    "wing.aileron",
    "wing.aileron_hinges",
    "wing.controls",
    "wing.attach",
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


def test_eighteen_ops_valid_and_no_unknown_ids(g):
    assert [o.id for o in g.ops.values() if o.chapter == 19] == CH19
    assert validate(g) == []
    for i in CH19:
        op = g.ops[i]
        assert all(r in g.ops for r in op.requires), i
        assert all(c in g.components for c in op.components), i
        assert op.sources and 2 <= len(op.completion) <= 6 and not op.stub, i
        assert all(
            118 <= s.scan_pp <= 134
            for s in op.sources
            if s.doc == "scan-1980" and s.scan_pp != 171
        ), i
        assert "c03.layup-skills" in needs(g, i) | {i}, i


def test_order_follows_the_plans(g):
    order = topo_order(g)
    pos = {i: order.index(i) for i in CH19}
    assert [i for i in order if i in CH19] == CH19
    assert pos["f19.top-cap"] < pos["f19.rudder-conduit"] < pos["f19.top-skin"]
    assert pos["f19.bottom-cap"] < pos["f19.bottom-skin"] < pos["f19.top-cap"]
    assert pos["f19.top-skin"] < pos["f19.ribs"]
    assert pos["f19.aileron-cut"] < pos["f19.aileron-build"] < pos["f19.controls"]
    assert pos["f19.controls"] < pos["f19.attach"]


def test_earlier_chapters_come_first(g):
    assert "f14.lwa-fabricate" in needs(g, "f19.hardpoints")
    assert "f14.bond-spar" in g.ops["f19.attach"].requires
    assert "f16.sticks-pushrods" in g.ops["f19.controls"].requires
    assert "f19.ribs" in g.ops["f19.controls"].requires
    # the aileron linkage and the wing attach wait on the wing, as the old stub said
    assert {"f19.controls", "f19.attach"} <= set(g.ops["f16.aileron-linkage"].requires)
    assert "c19.wings" not in g.ops
    # nothing before chapter 16 waits on the wing
    assert not [
        o.id for o in g.ops.values() if o.chapter < 16 and needs(g, o.id) & set(CH19)
    ]


def test_components_are_the_agreed_set_all_with_geometry(g):
    used = {c for i in CH19 for c in g.ops[i].components}
    assert used == COMPONENTS and COMPONENTS <= set(g.components)
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)
    assert all(g.ops[i].geometry_visible for i in CH19)


def test_book_values_are_in_the_ops_and_the_conflicts_are_flagged(g):
    cut = text(g.ops["f19.cut-cores"])
    assert "134.95" in cut and "134.45" in cut and "unresolved" in cut
    ail = text(g.ops["f19.aileron-cut"])
    assert "54.3" in ail and "55.5" in ail and "unresolved" in ail
    assert "118.1" in ail and "5.9" in ail and "7.6" in ail
    att = text(g.ops["f19.attach"])
    assert "28.85" in att and "28.83" in att and "unresolved" in att
    assert "20 deg" in text(g.ops["f19.controls"])
    assert "AN3-5A" in text(g.ops["f19.controls"])
    cap = text(g.ops["f19.bottom-cap"])
    assert "142, 135, 84, 52 and 19.5" in cap and "5, 12, 19 and 26" in cap
    assert "142, 142, 119, 90, 61, 39 and 20" in text(g.ops["f19.top-cap"])


def test_shear_web_outboard_zone_is_cp_corrected(g):
    op = g.ops["f19.shear-web"]
    assert (26, 31) in {(c.cp, c.lpc) for c in op.changes}
    assert [m["plies"] for m in op.materials] == [6, 4, 2]
    assert "cp-corrected" in op.materials[2]["where"]
    assert "cp-corrected" in " ".join(op.completion)


def test_cap_ops_say_they_draw_the_base_plies(g):
    for i in ("f19.bottom-cap", "f19.top-cap"):
        assert (28, 56) in {(c.cp, c.lpc) for c in g.ops[i].changes}
        assert "base plies" in text(g.ops[i])
    assert [m["plies"] for m in g.ops["f19.bottom-cap"].materials] == [5]
    assert [m["plies"] for m in g.ops["f19.top-cap"].materials] == [7]


def test_part_renames_and_the_rib_rubric(g):
    assert {(25, 9), (25, 10)} <= {
        (c.cp, c.lpc) for c in g.ops["f19.bottom-cap"].changes
    }
    assert (25, 11) in {(c.cp, c.lpc) for c in g.ops["f19.top-cap"].changes}
    assert {(25, 8), (25, 12)} <= {(c.cp, c.lpc) for c in g.ops["f19.ribs"].changes}
    assert (34, 107) in {(c.cp, c.lpc) for c in g.ops["f19.aileron-cut"].changes}


def test_own_words(g):
    for loc, t in authored_texts(g):
        if loc.startswith("f19."):
            assert isinstance(t, str) and "‑" not in t and len(t) < 700, loc
