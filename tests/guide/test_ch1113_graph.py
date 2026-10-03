"""Chapters 11-13 (Roncz elevators, canard installation gaps, nose and nose gear) in the committed graph."""

import re
from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

ELEV = [
    "r30.elev-nc2-inserts",
    "r30.elev-bond-cores",
    "r30.elev-skin-bottom",
    "r30.elev-skin-top",
    "r30.elev-trim-ends",
    "r30.elev-hinges",
    "r30.elev-hinge-slots",
    "r30.elev-uptravel-test",
    "r30.elev-flox-hinges",
    "r30.elev-nc12a",
    "r30.elev-balance-check",
    "r30.elev-travel-check",
    "r30.canard-tips",
    "r30.elev-trim-belcrank",
    "r30.elev-mass-balance",
    "r30.elev-balance-pockets",
    "r30.elev-ice-shield",
    "r30.elev-cs11",
]
GAP = [
    "r30.f22-drill-tabs",
    "r30.elev-fuselage-clearance",
    "r30.lift-tab-bushings",
    "r30.f28-pins-permanent",
]
NOSE = [
    "f13.strut-reinforce",
    "f13.worm-drive-bench",
    "f13.ng30-plates",
    "f13.ng-box-assemble",
    "f13.ng3-ng4",
    "f13.ng31-f6",
    "f13.floor-blocks",
    "f13.pedal-pivot-blocks",
    "f13.side-pieces",
    "f13.canard-attach-reinforce",
    "f13.rudder-pedals",
    "f13.lower-gear",
    "f13.strut-slot-sc",
    "f13.nb-box",
    "f13.rig-nose-gear",
    "f13.pitot-static",
    "f13.top-foam",
    "f13.carve-glass-nose",
    "f13.nose-door",
    "f13.shock-strut",
]


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
    return " ".join([op.title, op.summary, *op.completion])


def test_counts_and_ids(g):
    assert len(ELEV) == 18 and len(GAP) == 4 and len(NOSE) == 20
    assert [
        o.id for o in g.ops.values() if o.chapter == 11 and o.id.startswith("r30.")
    ] == ELEV
    assert [
        o.id for o in g.ops.values() if o.chapter == 12 and o.id.startswith("r30.")
    ] == GAP
    assert not [
        o.id
        for o in g.ops.values()
        if o.chapter == 30 and (o.id in ELEV or o.id in GAP)
    ]
    assert (
        g.ops["r30.install-pins"].chapter == 30
        and g.ops["r30.align-canard"].chapter == 30
    )
    assert [o.id for o in g.ops.values() if o.chapter == 13] == NOSE
    assert validate(g) == []


def test_every_op_is_complete_and_reaches_layup_skills(g):
    for i in ELEV + GAP + NOSE:
        op = g.ops[i]
        assert (
            not op.stub
            and op.summary.strip()
            and op.completion
            and op.sources
            and op.components
        ), i
        assert 2 <= len(op.completion) <= 6, i
        assert "c03.layup-skills" in needs(g, i), i
        assert op.variants == (("roncz",) if i.startswith("r30.") else ("both",)), i
        assert op.chapter == (13 if i.startswith("f13.") else 12 if i in GAP else 11), i


def test_stub_replaced(g):
    assert "r30.elevators" not in g.ops
    assert "r30.elev-cs11" in g.ops["r30.install-pins"].requires
    assert "r30.elev-cs11" in needs(g, "r30.install-pins")
    assert "r30.top-skin" in needs(
        g, "r30.elev-nc2-inserts"
    )  # book order: elevators follow the canard skins
    assert "r30.elev-balance-check" in needs(g, "r30.elev-cs11")
    assert "r30.elev-travel-check" in needs(g, "r30.install-pins")
    assert "r30.elev-ice-shield" not in needs(g, "r30.install-pins")
    assert "r30.elev-travel-check" in needs(g, "r30.canard-tips")


def test_order_and_prerequisites(g):
    for i in ELEV[1:]:
        assert needs(g, i) & set(ELEV), i
    assert {"r30.top-skin", "r30.hinge-foam"} <= needs(g, "r30.elev-hinge-slots")
    assert "r30.templates-cores" in needs(g, "r30.elev-bond-cores")
    assert "r30.align-canard" in needs(g, "f13.ng31-f6")
    assert "r30.lift-tab-bushings" in needs(g, "f13.canard-attach-reinforce")
    assert "r30.elev-travel-check" in g.ops["r30.elev-fuselage-clearance"].requires


def test_travel_check_has_roncz_numbers_only(g):
    t = text(g.ops["r30.elev-travel-check"])
    assert "15" in t and "30" in t and "12.5" in t
    for i in ELEV + GAP + NOSE:
        assert not re.search(r"\b(20|22)\s*(deg|°|degrees)", text(g.ops[i])), i
    assert (
        g.ops["r30.elev-travel-check"].inspection
        and g.ops["r30.elev-balance-check"].inspection
    )
    assert "CP57-8" in text(g.ops["r30.elev-balance-check"]) + text(
        g.ops["r30.elev-travel-check"]
    )
    assert "CP66-9" in text(g.ops["r30.elev-balance-check"]) + text(
        g.ops["r30.elev-travel-check"]
    )


def test_nose_wheel_station_is_never_a_single_number(g):
    for i in NOSE:
        t = text(g.ops[i])
        assert not re.search(r"\bF\.?S\.?\s*-?\s*(17|20|19\.6)\b", t, re.I), i


def test_book_numbers(g):
    assert "6.71" in text(g.ops["f13.ng3-ng4"])
    assert "0.2" in text(g.ops["f13.ng30-plates"])
    assert "3.0" in text(g.ops["f13.ng-box-assemble"])
    assert (
        "BL" in text(g.ops["r30.elev-hinge-slots"])
        and "text" in text(g.ops["r30.elev-hinge-slots"]).lower()
    )
    assert "0.2" in text(g.ops["r30.elev-hinge-slots"])


def test_materials_parse(g):
    for i in ELEV + GAP + NOSE:
        for m in g.ops[i].materials:
            assert (
                m["cloth"] in {"UND", "BID"}
                and isinstance(m["plies"], int)
                and m["plies"] > 0
                and m["where"]
            ), (i, m)
    assert g.ops["r30.elev-skin-bottom"].materials[0]["cloth"] == "UND"
    assert any(m["plies"] == 4 for m in g.ops["f13.ng30-plates"].materials)


def test_sources(g):
    for i in GAP + NOSE:
        scans = [s for s in g.ops[i].sources if s.doc == "scan-1980"]
        assert scans and all(71 <= s.scan_pp <= 83 for s in scans), i
        assert all(s.doc in ("scan-1980", "cobelu") for s in g.ops[i].sources), i
    for i in ELEV:
        assert all(s.doc == "cobelu" and s.heading for s in g.ops[i].sources), i


def test_change_links(g):
    got = {
        (c.cp, c.lpc): o.id
        for o in g.ops.values()
        if o.chapter in (13, 30)
        for c in o.changes
    }
    assert got[(25, 23)] == "f13.ng31-f6"
    assert got[(25, 27)] == "f13.shock-strut"
    assert got[(30, 86)] == "f13.rudder-pedals"
    assert got[(30, 87)] == "f13.worm-drive-bench"


def test_no_cycles_and_own_words(g):
    assert validate(g) == []
    for loc, t in authored_texts(g):
        assert "‑" not in t and len(t) < 700, loc
