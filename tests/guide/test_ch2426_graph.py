"""Chapters 24 to 26 (covers and consoles, finishing, upholstery) in the committed graph."""

from pathlib import Path

import pytest

from guide.schema import load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH24 = [
    "f24.aft-cover",
    "f24.console-lc1",
    "f24.consoles-left",
    "f24.thigh-support",
    "f24.canard-cover",
    "f24.gap-seal",
]
CH25 = [
    "f25.inspect-repair",
    "f25.coarse-fill",
    "f25.feather-fill",
    "f25.primer",
    "f25.paint-seals",
]
CH26 = ["f26.cushions-headrests", "f26.suitcases"]
ALL = CH24 + CH25 + CH26
PAGES = {24: range(159, 162), 25: range(162, 170), 26: range(170, 171)}
COMPONENTS = {
    "cover.aft",
    "cover.console_lc1",
    "cover.consoles",
    "cover.thigh",
    "cover.valve",
    "cover.canard",
    "cover.seal",
    "finish.fill",
    "finish.primer",
    "finish.paint",
    "upholstery.cushions",
    "upholstery.headrests",
    "upholstery.suitcases",
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


def test_ops_valid_and_no_unknown_ids(g):
    assert [o.id for o in g.ops.values() if o.chapter == 24] == CH24
    assert [o.id for o in g.ops.values() if o.chapter == 25] == CH25
    assert [o.id for o in g.ops.values() if o.chapter == 26] == CH26
    assert validate(g) == []
    for i in ALL:
        op = g.ops[i]
        assert all(r in g.ops for r in op.requires), i
        assert all(c in g.components for c in op.components), i
        assert op.sources and 2 <= len(op.completion) <= 6 and not op.stub, i
        assert op.summary.strip() and op.variants == ("both",), i
        assert all(s.scan_pp in set(PAGES[op.chapter]) | {134} for s in op.sources), i
        assert "c03.layup-skills" in needs(g, i) | {i}, i


def test_order_follows_the_plans(g):
    order = topo_order(g)
    assert [i for i in order if i in ALL] == ALL
    pos = {i: order.index(i) for i in ALL}
    assert max(pos[i] for i in CH24) < min(pos[i] for i in CH25)
    assert max(pos[i] for i in CH25) < min(pos[i] for i in CH26)
    assert pos["f24.console-lc1"] < pos["f24.consoles-left"] < pos["f24.thigh-support"]
    assert pos["f24.canard-cover"] < pos["f24.gap-seal"]
    assert pos["f25.coarse-fill"] < pos["f25.feather-fill"] < pos["f25.primer"]
    assert pos["f25.primer"] < pos["f25.paint-seals"]
    # nothing before chapter 24 waits on chapters 24 to 26
    assert not [
        o.id for o in g.ops.values() if o.chapter < 24 and needs(g, o.id) & set(ALL)
    ]


def test_earlier_chapters_come_first(g):
    # the gap seal needs the wing on; the cover and the finishing need the airframe complete
    assert "f19.attach" in g.ops["f24.gap-seal"].requires
    for i in ("f21.fairing-caps", "f22.antennas", "f23.root-rib"):
        assert i in needs(g, "f25.inspect-repair"), i
    assert "f24.gap-seal" in g.ops["f25.inspect-repair"].requires
    assert {"f23.root-rib", "f15.stainless-firewall", "f09.position-gear"} <= needs(
        g, "f24.aft-cover"
    )
    # interior paint precedes the upholstery
    assert "f25.paint-seals" in g.ops["f26.cushions-headrests"].requires
    # the left suitcase is shortened for the landing brake console
    assert "f24.consoles-left" in needs(g, "f26.suitcases")


def test_components_are_the_agreed_set(g):
    used = {c for i in ALL for c in g.ops[i].components}
    assert used == COMPONENTS and COMPONENTS <= set(g.components)
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)
    hidden = {i for i in ALL if not g.ops[i].geometry_visible}
    assert hidden == {"f25.inspect-repair"}
    assert g.ops["f25.inspect-repair"].inspection


def test_chapter_24_values_and_conflicts_are_in_words(g):
    aft = g.ops["f24.aft-cover"]
    t = text(aft)
    assert "18 by 20 by 2" in t and "1/8 in" in t and "1/2 in" in t
    assert "conflict" in t and "LPC 54" in t and "transcription" in t
    assert (28, 54) in {(c.cp, c.lpc) for c in aft.changes}
    lc1 = text(g.ops["f24.console-lc1"])
    assert "FS 52 to FS 60" in lc1 and "9.1 in by 8 in" in lc1 and "WL 11.6" in lc1
    left = text(g.ops["f24.consoles-left"])
    assert "30.6" in left and "30.8" in left and "unresolved" in left
    assert "18.2 by 1.9" in left and "fitted shapes" in left
    thigh = text(g.ops["f24.thigh-support"])
    assert "10.8" in thigh and "3.65" in thigh and "17 by 12.3" in thigh
    assert "6.6 by 5.0" in thigh and "not hold" in thigh
    seal = text(g.ops["f24.gap-seal"])
    assert "1/2 in" in seal and "1/16 in" in seal and "3/4" in seal
    assert "chapter 19" in seal
    assert "2 in green urethane" in text(g.ops["f24.canard-cover"])


def test_chapter_25_is_thicknesses_and_a_colour_rule_never_a_weight(g):
    feather = text(g.ops["f25.feather-fill"])
    assert "0.02 to 0.03" in feather and "70 F" in feather and "conflict" in feather
    assert "0.004 to 0.008" in text(g.ops["f25.primer"])
    paint = g.ops["f25.paint-seals"]
    t = text(paint)
    assert "white only on the upper wing and canard" in t
    assert "No finish weight is printed" in t
    assert "+1.0 lb" in t and "+0.275 lb" in t and "+2.2 lb" in t and "references" in t
    assert "70 F" in text(g.ops["f25.inspect-repair"])
    for i in CH25:  # no op states a finish mass as a fact
        assert not any(ch.isdigit() for ch in "") and "lb of finish" not in text(
            g.ops[i]
        )


def test_chapter_26_is_sizes_only(g):
    t = text(g.ops["f26.cushions-headrests"]) + text(g.ops["f26.suitcases"])
    assert "46 by 16.5" in t and "4.5 by 4.5 by 2" in t and "4.5 by 4.5 by 1.5" in t
    assert "30 in on the long edge" in t and "15 in long" in t
    assert "No weight is printed" in t
    assert "last page of the plans" in text(g.ops["f26.suitcases"])
