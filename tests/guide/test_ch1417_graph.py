"""Chapters 14-17 (spar, firewall accessories, controls, trim) in the committed graph."""

import re
from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH14 = [
    "f14.jig",
    "f14.foam-box",
    "f14.cs4-forward",
    "f14.lwa-fabricate",
    "f14.interior-layups",
    "f14.close-box",
    "f14.cap-troughs",
    "f14.shearweb-lwa45",
    "f14.spar-caps",
    "f14.spruce-layup6",
    "f14.lwa23-layup7",
    "f14.baggage-hole",
    "f14.end-bulkhead-layup9",
    "f14.nut-access-hole",
    "f14.fit-fuselage",
    "f14.bond-spar",
    "f14.sh1-tabs",
]
CH15 = [
    "f15.parts-fab",
    "f15.stainless-firewall",
    "f15.belcrank-brackets",
    "f15.master-cylinders",
]
CH16 = [
    "f16.side-consoles",
    "f16.pivot-bulkheads",
    "f16.firewall-bearing",
    "f16.torque-tubes",
    "f16.sticks-pushrods",
    "f16.pitch-pushrod",
    "f16.aileron-linkage",
    "f16.rudder-conduit",
    "f16.rudder-cable-rig",
    "f16.brake-cables",
    "f16.adjustable-pedals",
]
CH17 = [
    "f17.mount-blocks",
    "f17.parts",
    "f17.pitch-trim",
    "f17.roll-trim",
    "f17.fixed-trim-tab",
]
ALL = CH14 + CH15 + CH16 + CH17
COMPONENTS = {
    "spar.box",
    "spar.cap_top",
    "spar.cap_bottom",
    "spar.bulkheads",
    "spar.lwa",
    "spar.spruce_blocks",
    "spar.em12",
    "spar.sh1",
    "spar.jig",
    "fuselage.firewall_stainless",
    "firewall.belcrank",
    "firewall.master_cylinders",
    "controls.consoles",
    "controls.torque_tube",
    "controls.sticks",
    "controls.pitch_pushrod",
    "controls.rudder_conduit",
    "trim.pitch_handle",
    "trim.roll_trim",
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
        [
            op.title,
            op.summary,
            *op.completion,
            *(c.note for c in op.changes),
            *(m["where"] for m in op.materials),
        ]
    )


def test_counts_ids_and_validity(g):
    assert (len(CH14), len(CH15), len(CH16), len(CH17)) == (17, 4, 11, 5)
    for ch, ids in ((14, CH14), (15, CH15), (16, CH16), (17, CH17)):
        assert [o.id for o in g.ops.values() if o.chapter == ch] == ids
    assert validate(g) == []


def test_every_op_is_complete_and_requires_resolve(g):
    for i in ALL:
        op = g.ops[i]
        assert (
            not op.stub
            and op.summary.strip()
            and op.sources
            and 2 <= len(op.completion) <= 6
        ), i
        assert all(r in g.ops for r in op.requires), i
        assert "c03.layup-skills" in needs(g, i), i
        assert all(s.doc in ("scan-1980", "cobelu") for s in op.sources), i
        assert all(
            84 <= s.scan_pp <= 107 or (i == "f14.sh1-tabs" and s.scan_pp == 48)
            for s in op.sources
            if s.doc == "scan-1980"
        ), i
        assert op.variants in (("both",), ("roncz",)), i
    for i in ("f16.adjustable-pedals", "f17.fixed-trim-tab"):
        assert "(optional)" in g.ops[i].title


def test_components_exist_and_are_only_the_agreed_set(g):
    used = set()
    for i in ALL:
        for c in g.ops[i].components:
            assert c in g.components, (i, c)
            used.add(c)
    assert used <= COMPONENTS and used == COMPONENTS
    assert COMPONENTS <= set(g.components)
    # M2.5 geometry: every component has a representational (graph word: unvalidated) display solid
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)


def test_wing_and_winglet_ops_replace_the_chapter_19_and_20_stubs(g):
    assert "c19.wings" not in g.ops and "c20.winglets" not in g.ops
    ail = g.ops["f16.aileron-linkage"].requires
    assert "f19.controls" in ail and "f19.attach" in ail
    assert "f20.rudder-hang" in g.ops["f16.rudder-cable-rig"].requires
    others = [
        o.id
        for o in g.ops.values()
        if o.id not in ("f16.aileron-linkage", "f16.rudder-cable-rig")
        and o.chapter < 19
    ]
    assert not [
        i
        for i in others
        if {"f19.controls", "f19.attach", "f20.rudder-hang"} & set(g.ops[i].requires)
    ]


def test_firewall_bond_moves_after_the_spar_fit_with_a_cp_hint(g):
    fw = g.ops["f06.bond-firewall"]
    assert "f14.fit-fuselage" in needs(g, "f06.bond-firewall")
    assert "f06.bond-firewall" not in needs(g, "f14.fit-fuselage")
    assert [c for c in fw.changes if c.cls == "cp-hint" and c.cp == 25]
    assert "f06.bond-firewall" in needs(
        g, "f14.bond-spar"
    ) and "f06.bond-firewall" in needs(g, "f15.stainless-firewall")
    # nothing in chapters 6-9 still waits on the firewall bond
    assert not [
        o.id
        for o in g.ops.values()
        if "f06.bond-firewall" in o.requires and o.chapter < 14
    ]
    order = topo_order(g)
    assert (
        order.index("f14.fit-fuselage")
        < order.index("f06.bond-firewall")
        < order.index("f14.bond-spar")
    )


def test_gear_and_harness_edges(g):
    assert "f14.fit-fuselage" in g.ops["f09.position-gear"].requires
    assert "f14.sh1-tabs" in g.ops["f08.shoulder-harness"].requires
    order = topo_order(g)
    assert order.index("f14.fit-fuselage") < order.index("f09.position-gear")
    assert order.index("f14.sh1-tabs") < order.index("f08.shoulder-harness")


def test_roncz_travel_numbers_only_and_no_unprinted_stops_or_stations(g):
    for i in ALL:
        t = text(g.ops[i])
        assert not re.search(r"\b(20|22)\s*(deg|°|degrees)", t), i
        assert (
            not re.search(r"\b(20|22)\b[^.]{0,40}\b(up|down)\b", t) or "20 in" in t
        ), i
        assert not re.search(r"49\.[58]", t), i
        low = t.lower()
        assert "gu only" not in low, i
        if "stop" in low and "pitch" in low:
            assert "not printed" in low or "no pitch stop is printed" in low, i
    t = text(g.ops["f16.pitch-pushrod"])
    assert "15" in t and "30" in t and "no pitch stop is printed" in t.lower()
    assert not [
        i
        for i in ALL
        if re.search(r"\bstops?\b", " ".join(g.ops[i].completion), re.I)
        and "printed" not in text(g.ops[i]).lower()
    ]


def test_nc5a_is_at_bl_9_2_on_the_left_tube(g):
    t = text(g.ops["f17.pitch-trim"])
    assert "NC-5A" in t and "BL 9.2" in t and "left" in t and "BL 0" not in t
    assert not [
        i for i in ALL if "NC-5A" in text(g.ops[i]) and "BL 0" in text(g.ops[i])
    ]


def test_spar_cap_rows_and_hardware_sizes(g):
    rows = {m["where"].split(",")[0]: m for m in g.ops["f14.spar-caps"].materials}
    assert rows["top spar cap"]["plies"] == 12 and rows["bottom spar cap"]["plies"] == 9
    assert all(m["cloth"] == "UND" for m in rows.values())
    t = text(g.ops["f14.spar-caps"])
    assert "three full" in t and "four full" in t and not re.search(r"\b113\b", t)
    lwa = text(g.ops["f14.lwa-fabricate"])
    assert (
        "1.75" in lwa
        and "2.25" in lwa
        and (43, 119) in {(c.cp, c.lpc) for c in g.ops["f14.lwa-fabricate"].changes}
    )
    inter = text(g.ops["f14.interior-layups"])
    assert "0.75" in inter and (25, 28) in {
        (c.cp, c.lpc) for c in g.ops["f14.interior-layups"].changes
    }
    assert "45.5" in text(g.ops["f16.pivot-bulkheads"]) and "medium" in text(
        g.ops["f16.pivot-bulkheads"]
    )
    assert "89.7" in text(g.ops["f16.pivot-bulkheads"])


def test_materials_parse(g):
    for i in ALL:
        for m in g.ops[i].materials:
            assert (
                m["cloth"] in {"UND", "BID"}
                and isinstance(m["plies"], int)
                and m["plies"] > 0
                and m["where"]
            ), (i, m)


def test_stainless_and_insulation_only_in_chapter_15_plywood_in_chapter_4(g):
    assert "stainless" in text(g.ops["f15.stainless-firewall"]).lower()
    assert (
        "insulation" in g.ops["f15.stainless-firewall"].summary.lower()
        and "cowling" in g.ops["f15.stainless-firewall"].summary
    )
    for i in ("f04.firewall-aft", "f04.firewall-fwd"):
        t = " ".join([g.ops[i].title, g.ops[i].summary, *g.ops[i].completion]).lower()
        assert "stainless" not in t, i
        assert "fitted in chapter 15" in g.ops["f04.firewall-aft"].summary
    assert "plywood" in g.ops["f04.firewall-aft"].summary.lower()
    assert not [
        i
        for i in ALL
        if i != "f15.stainless-firewall"
        and "stainless" in text(g.ops[i]).lower()
        and i not in ("f15.belcrank-brackets", "f16.firewall-bearing")
    ]
    assert not [
        i for i in CH15 + CH16 + CH17 if "plywood firewall" in text(g.ops[i]).lower()
    ]


def test_change_links_are_in_the_cp_text(g):
    got = {(c.cp, c.lpc) for i in ALL for c in g.ops[i].changes}
    assert {
        (25, 19),
        (25, 25),
        (25, 26),
        (25, 28),
        (26, 29),
        (26, 40),
        (27, 47),
        (32, 95),
        (32, 99),
        (36, 111),
        (43, 119),
    } <= got


def test_no_cycles_and_own_words(g):
    assert validate(g) == []
    for loc, t in authored_texts(g):
        assert isinstance(t, str) and "‑" not in t and len(t) < 700, loc
