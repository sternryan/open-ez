"""Chapters 21 to 23 (strakes and fuel, electrical, engine) in the committed graph."""

from pathlib import Path

import pytest

from guide.schema import authored_texts, load_graph, topo_order, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"

CH21 = [
    "f21.cut-parts",
    "f21.fuselage-cutouts",
    "f21.jig-bond",
    "f21.inside-layups",
    "f21.vent-screen",
    "f21.close-tank",
    "f21.od-outlet",
    "f21.outside-bottom",
    "f21.outside-top",
    "f21.pressure-check",
    "f21.fairing-caps",
    "f21.plumbing",
]
CH22 = [
    "f22.panel-wiring",
    "f22.microswitches",
    "f22.battery-shelf",
    "f22.firewall-terminals",
    "f22.wing-wiring",
    "f22.antennas",
]
CH23 = [
    "f23.engine-install",
    "f23.carb-bracket",
    "f23.cowl-trim",
    "f23.cowl-closeout",
    "f23.root-rib",
]
ALL = CH21 + CH22 + CH23
PAGES = {21: range(141, 149), 22: range(149, 156), 23: range(156, 159)}
COMPONENTS = {
    "strake.ribs",
    "strake.baffles",
    "strake.leading_edge",
    "strake.skins",
    "strake.sump",
    "strake.tank",
    "strake.fairing",
    "strake.fittings",
    "elec.battery_shelf",
    "elec.battery",
    "elec.relays",
    "elec.wiring",
    "elec.lights",
    "elec.antennas",
    "engine.block",
    "engine.bracket",
    "engine.cowl",
    "engine.rib",
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
    assert [o.id for o in g.ops.values() if o.chapter == 21] == CH21
    assert [o.id for o in g.ops.values() if o.chapter == 22] == CH22
    assert [o.id for o in g.ops.values() if o.chapter == 23] == CH23
    assert validate(g) == []
    for i in ALL:
        op = g.ops[i]
        assert all(r in g.ops for r in op.requires), i
        assert all(c in g.components for c in op.components), i
        assert op.sources and 2 <= len(op.completion) <= 6 and not op.stub, i
        assert op.summary.strip() and op.variants == ("both",), i
        ok = set(PAGES[op.chapter]) | {171}
        assert all(s.scan_pp in ok for s in op.sources if s.doc == "scan-1980"), i
        assert "c03.layup-skills" in needs(g, i) | {i}, i


def test_order_follows_the_plans(g):
    order = topo_order(g)
    assert [i for i in order if i in ALL] == ALL
    pos = {i: order.index(i) for i in ALL}
    assert pos["f21.inside-layups"] < pos["f21.vent-screen"] < pos["f21.close-tank"]
    assert pos["f21.close-tank"] < pos["f21.od-outlet"] < pos["f21.outside-bottom"]
    assert pos["f21.outside-bottom"] < pos["f21.outside-top"]
    assert pos["f21.outside-top"] < pos["f21.pressure-check"] < pos["f21.fairing-caps"]
    assert pos["f22.battery-shelf"] < pos["f22.firewall-terminals"]
    assert pos["f23.engine-install"] < pos["f23.cowl-trim"] < pos["f23.cowl-closeout"]
    assert pos["f23.cowl-closeout"] < pos["f23.root-rib"]
    assert max(pos[i] for i in CH21) < min(pos[i] for i in CH22)
    assert max(pos[i] for i in CH22) < min(pos[i] for i in CH23)


def test_earlier_chapters_come_first(g):
    # strakes need the spar bonded, the fuselage sides skinned and the wing on
    assert "f14.bond-spar" in g.ops["f21.cut-parts"].requires
    assert {"f19.attach", "f21.cut-parts", "f21.fuselage-cutouts"} <= set(
        g.ops["f21.jig-bond"].requires
    )
    assert {"f07.skin-right", "f07.skin-left", "f14.bond-spar"} <= set(
        g.ops["f21.fuselage-cutouts"].requires
    )
    assert "f15.stainless-firewall" in needs(g, "f21.plumbing")
    # electrical needs the nose and the panel
    assert "f13.ng31-f6" in g.ops["f22.battery-shelf"].requires
    assert "f13.nose-door" in g.ops["f22.battery-shelf"].requires
    assert "f06.bond-panel" in g.ops["f22.panel-wiring"].requires
    assert {"f18.latches", "f13.rig-nose-gear"} <= set(
        g.ops["f22.microswitches"].requires
    )
    # the engine needs the firewall
    assert "f15.stainless-firewall" in needs(g, "f23.engine-install")
    assert "f22.firewall-terminals" in g.ops["f23.engine-install"].requires
    # nothing before chapter 21 waits on chapters 21 to 23
    assert not [
        o.id for o in g.ops.values() if o.chapter < 21 and needs(g, o.id) & set(ALL)
    ]


def test_components_are_the_agreed_set(g):
    used = {c for i in ALL for c in g.ops[i].components}
    assert used == COMPONENTS and COMPONENTS <= set(g.components)
    assert all(g.components[c].fidelity == "unvalidated" for c in COMPONENTS)
    hidden = {i for i in ALL if not g.ops[i].geometry_visible}
    assert hidden == {"f21.plumbing", "f22.microswitches"}
    assert all(not g.ops[i].components for i in hidden)


def test_chapter_21_values_and_conflicts_are_in_words(g):
    cut = text(g.ops["f21.cut-parts"])
    assert "25.5" in cut and "28 gal" in cut and "26 gal" in cut and "52 gal" in cut
    assert "21.3" in cut and "28.5" in cut and "13.4" in cut and "33.5" in cut
    cuts = text(g.ops["f21.fuselage-cutouts"])
    assert "65.8" in cuts and "1.90" in cuts and "1.40" in cuts and "unresolved" in cuts
    assert "90" in cuts and "80.6" in cuts
    jig = text(g.ops["f21.jig-bond"])
    assert "2.65" in jig and "3.45" in jig and "1/4-27" in jig and "1/8-27" in jig
    assert (28, 60) in {(c.cp, c.lpc) for c in g.ops["f21.jig-bond"].changes}
    od = text(g.ops["f21.od-outlet"])
    assert "layup 7" in od and "7a" in od and "7b" in od and "0.4 in" in od
    assert (33, 102) in {(c.cp, c.lpc) for c in g.ops["f21.od-outlet"].changes}
    bottom = g.ops["f21.outside-bottom"]
    assert (28, 59) in {(c.cp, c.lpc) for c in bottom.changes}
    assert "21 in long" in text(bottom) and "2.75" in text(bottom)
    assert "left strake only" in text(g.ops["f21.outside-top"])
    assert g.ops["f21.pressure-check"].inspection
    assert "1500 ft" in text(g.ops["f21.pressure-check"])
    fc = text(g.ops["f21.fairing-caps"])
    assert "2 1/4 in" in fc and "not a tank drain" in fc
    assert (30, 84) in {(c.cp, c.lpc) for c in g.ops["f21.fairing-caps"].changes}
    assert {(24, 1), (32, 96)} <= {(c.cp, c.lpc) for c in g.ops["f21.plumbing"].changes}
    assert (24, 4) in {(c.cp, c.lpc) for c in g.ops["f21.inside-layups"].changes}


def test_chapter_22_battery_station_is_stated_as_unprinted(g):
    b = text(g.ops["f22.battery-shelf"])
    assert "12 V" in b and "25 Ah" in b and "FS 11" in b and "illustration" in b
    assert "does not hold" in b or "not hold" in b
    assert "19 lb" in b
    assert [m["plies"] for m in g.ops["f22.battery-shelf"].materials] == [4, 3]
    t = text(g.ops["f22.firewall-terminals"])
    assert "F22" in t and "150 or more" in t and "lower bound" in t
    assert {(27, 49), (32, 98), (34, 106)} <= {
        (c.cp, c.lpc) for c in g.ops["f22.panel-wiring"].changes
    }
    assert (30, 78) in {(c.cp, c.lpc) for c in g.ops["f22.antennas"].changes}
    assert "22.8" in text(g.ops["f22.antennas"]) and "20.3" in text(
        g.ops["f22.antennas"]
    )
    assert "0.10 in" in text(g.ops["f22.microswitches"])
    assert "22-10" in text(g.ops["f22.microswitches"])


def test_chapter_23_engine_op_stands_for_the_absent_installation(g):
    e = text(g.ops["f23.engine-install"])
    assert "stands for" in e and "none of which" in e
    assert "246 lb" in e and "286 lb" in e and "2 deg" in e and "BL 0" in e
    assert "not held" in e and "fitted shape" in e
    assert all(w in e for w in ("IIA", "IIC", "IIL"))
    rib = text(g.ops["f23.root-rib"])
    assert "0.20 in" in rib and "0.020 in" in rib
    close = text(g.ops["f23.cowl-closeout"])
    assert "40" in close and "32" in close and "unresolved" in close
    assert g.ops["f23.cowl-trim"].materials[0]["plies"] == 4
    assert (31, 92) in {(c.cp, c.lpc) for c in g.ops["f23.cowl-trim"].changes}
    assert "1.8 in" in text(g.ops["f23.carb-bracket"])
    assert "drill 12" in text(g.ops["f23.carb-bracket"])


def test_no_op_states_an_unprinted_station_as_a_page_value(g):
    # the battery and engine stations are not printed anywhere held; the ops must say so
    for i in ("f22.battery-shelf", "f23.engine-install"):
        t = text(g.ops[i])
        assert "illustration" in t or "not held" in t, i


def test_own_words(g):
    for loc, t in authored_texts(g):
        if loc.startswith(("f21.", "f22.", "f23.")):
            assert isinstance(t, str) and "‑" not in t and len(t) < 700, loc
