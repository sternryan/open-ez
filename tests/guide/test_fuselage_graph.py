"""Chapters 4-6 (fuselage box) in the committed graph: structure, ordering and recall."""

from pathlib import Path

import pytest

from guide.linker import candidates, recall
from guide.lpc import parse_lpcs
from guide.schema import load_graph, validate
from guide.sources import load_markers, source_paths

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"


@pytest.fixture(scope="module")
def g():
    return load_graph(GRAPH)


def fuselage_ops(g):
    return [o for o in g.ops.values() if o.chapter in (4, 5, 6)]


def needs(g, op_id):
    seen, stack = set(), [op_id]
    while stack:
        for r in g.ops[stack.pop()].requires:
            if r not in seen:
                seen.add(r)
                stack.append(r)
    return seen


# (op id, item, sourcing-record line). A row stays only when that line shows a
# page the record opened and gives the quantity. Reviewed against
# docs/harness/rehearsal-sourcing-p1.md and rehearsal-sourcing-p2.md: the
# phase-2 candidates cite plans pages the record did not open, so none qualify.
OFFICIAL_BUYS: tuple[tuple[str, str, str], ...] = ()

# (op id, citation). Official hours need the same review: the sourcing record
# opened the page. Reviewed against the same two files. The one official hour,
# f24.canard-cover, cites plans-1980:p161, which rehearsal-sourcing-p2.md says
# was not read (a four-hour ceiling, not a log). No derived hours exist.
# Community hours cite log URLs those records opened, so they stay.
OFFICIAL_HOURS: tuple[tuple[str, str], ...] = ()


def test_sourced_buys_match_the_sourcing_record(g):
    """Official means a page the sourcing record read. Derived means a derivation it records."""
    buys = [
        (op.id, buy.item, buy.flag)
        for op in g.ops.values()
        if op.plan is not None
        for buy in op.plan.buy
        if buy.flag in {"official", "derived"}
    ]
    assert ("f04.firewall-fwd", "an509-10r10", "official") not in buys
    assert ("f04.firewall-fwd", "an509-10r10", "estimate") in [
        (op.id, buy.item, buy.flag)
        for op in g.ops.values()
        if op.plan is not None
        for buy in op.plan.buy
    ]
    assert [(op, item) for op, item, flag in buys if flag == "official"] == [
        row[:2] for row in OFFICIAL_BUYS
    ]
    # Exact set, graph order. The gear pair stays. The rest are phase-2
    # derivations the sourcing record writes down; a new derived buy fails.
    assert [row for row in buys if row[2] == "derived"] == [
        ("f05.gear-extrusions", "lmga-assembly", "derived"),
        ("f05.gear-extrusions", "main-gear-extrusion", "derived"),
        ("f08.belt-attach", "an525-416r16", "derived"),
        ("f08.belt-attach", "ms21042-4", "derived"),
        ("f08.belt-attach", "an960-416", "derived"),
        ("f09.strut-stiffen", "main-gear-strut", "derived"),
        ("f09.tab-assembly", "an960-1016", "derived"),
        ("f09.axles-brakes", "an4-22a", "derived"),
        ("f09.axles-brakes", "ms21042-4", "derived"),
        ("f09.axles-brakes", "main-axle", "derived"),
        ("f09.axles-brakes", "wheel-brake-5in", "derived"),
        ("f09.brake-lines", "brake-line-nylon-316", "derived"),
        ("f13.strut-reinforce", "ng-strut-longez", "derived"),
        ("f13.rudder-pedals", "rudder-pedal-longez", "derived"),
        ("f13.strut-slot-sc", "strut-cover-sc", "derived"),
        ("f13.nb-box", "nose-wheel-cover-nb", "derived"),
        ("f14.lwa-fabricate", "al-2024-bar-0125x2", "derived"),
        ("f14.lwa-fabricate", "al-2024-bar-025x2", "derived"),
        ("f14.spruce-layup6", "spruce-1x1", "derived"),
        ("f14.bond-spar", "al-2024-angle-1x1x0125", "derived"),
        ("f15.master-cylinders", "master-cylinder", "derived"),
        ("f16.rudder-conduit", "rudder-conduit-nylon", "derived"),
        ("f18.trim-plexi", "canopy-bubble", "derived"),
        ("f19.cut-cores", "styrofoam-8x16x67", "derived"),
        ("f19.cut-cores", "styrofoam-8x16x42", "derived"),
        ("f19.aileron-build", "steel-rod-0p375", "derived"),
        ("f19.aileron-build", "piano-hinge-p6-3ft", "derived"),
        ("f19.attach", "an8-21a", "derived"),
        ("f19.attach", "an8-23a", "derived"),
        ("f20.rudder-hang", "piano-hinge-ms20257p2-3ft", "derived"),
        ("f20.rudder-hang", "nutplate-rudder-hinge", "derived"),
        ("f20.rudder-hang", "pop-rivet-flush", "derived"),
        ("f21.od-outlet", "tube-5052-0375-6ft", "derived"),
        ("f21.fairing-caps", "fuel-cap-dzus-2in", "derived"),
        ("f22.antennas", "copper-foil-tape", "derived"),
        ("f23.cowl-trim", "cowl-variez", "derived"),
    ]
    # Official hours follow the buy rule. An unread official hour is not on
    # the allowlist, so it fails here. f24.canard-cover keeps the four-hour
    # ceiling and is an estimate: the plans page was not read.
    official_hours = [
        (op.id, op.plan.hours.source)
        for op in g.ops.values()
        if op.plan is not None
        and op.plan.hours is not None
        and op.plan.hours.flag == "official"
    ]
    assert official_hours == [row[:2] for row in OFFICIAL_HOURS]
    cover = g.ops["f24.canard-cover"].plan
    assert cover is not None and cover.hours is not None
    assert (cover.hours.flag, cover.hours.value, cover.hours.source) == (
        "estimate",
        4.0,
        None,
    )
    assert "Not over four man-hours." in g.ops["f24.canard-cover"].summary


def test_graph_valid_and_complete(g):
    assert validate(g) == []
    by_ch = {c: [o for o in fuselage_ops(g) if o.chapter == c] for c in (4, 5, 6)}
    assert all(by_ch.values())
    for o in fuselage_ops(g):
        assert not o.stub and o.sources and o.completion and o.summary.strip(), o.id
    assert "c06.fuselage-assembled" not in g.ops


def test_bonding_order_front_panel_f22_rear_firewall(g):
    order = [
        "f06.bond-front-seat",
        "f06.bond-panel",
        "f06.bond-f22",
        "f06.bond-rear-seat",
        "f06.bond-firewall",
    ]
    for i, later in enumerate(order):
        for earlier in order[:i]:
            assert earlier in needs(g, later), (earlier, later)
    assert "f06.trial-fit" in needs(g, order[0]) and "f06.jig-check" in needs(
        g, order[0]
    )


def test_trial_fit_needs_every_ch4_op_and_gear_extrusions(g):
    n = needs(g, "f06.trial-fit")
    assert {o.id for o in g.ops.values() if o.chapter == 4} <= n
    assert "f05.gear-extrusions" in n


def test_ch4_groups_are_independent(g):
    ch4 = [o.id for o in g.ops.values() if o.chapter == 4]
    seat = [i for i in ch4 if "seat-bkhd" in i]
    rest = [i for i in ch4 if i not in seat]
    assert len(seat) == 4 and len(rest) == 4
    for a in seat:
        assert not needs(g, a) & set(rest)
    for b in rest:
        assert not needs(g, b) & set(seat)
    for i in ch4:
        assert "g00.bookend" in needs(g, i)


def test_ch5_chain_independent_of_ch4(g):
    ch5 = [o.id for o in g.ops.values() if o.chapter == 5]
    for i in ch5:
        assert not any(g.ops[r].chapter == 4 for r in needs(g, i) if r in g.ops)


def test_side_inside_layup_is_und_at_30(g):
    op = next(
        o for o in g.ops.values() if any(c.cp == 29 and c.lpc == 70 for c in o.changes)
    )
    assert any(m["cloth"] == "UND" and "30" in m["where"] for m in op.materials)


def test_recall_finds_the_four_new_annotations(g):
    paths = source_paths()
    if any(p is None for p in paths.values()):
        pytest.skip("source env not set")
    cands = candidates(
        g,
        parse_lpcs(paths["cp"].read_text(errors="ignore")),
        load_markers(paths["cobelu"]),
    )
    hits, misses = recall(g, cands, {4, 5, 6})
    got = {(a.scan_pp, a.cp, a.lpc) for a in hits}
    assert {(34, 27, 42), (34, 25, 17), (35, 25, 25), (36, 25, 5)} <= got
    assert misses == []


# Snapshot of the canard chapters' order taken before the authored-order tie-break (2026-09-30);
# the tie-break must not move any of them.
CANARD_ORDER = [
    "ref.back-cover-3view",
    # the education stub's place in this order is the ground-school group
    "g00.shop-setup",
    "g00.tools",
    "g00.mix",
    "g00.orientation",
    "g00.flat-layup",
    "g00.peel-ply",
    "g00.micro-flox",
    "g00.foam-shape",
    "g00.load-beam",
    "g00.bookend",
    "c10.templates-cores",
    "c10.shear-web",
    "c10.jig-cores",
    "c10.bottom-spar-skin",
    "c10.top-spar-skin",
    "r30.templates-cores",
    "r30.lift-tabs",
    "r30.shear-web",
    "r30.jig-assemble",
    "r30.bottom-spar-cap",
    "r30.bottom-skin",
    "r30.turnover-twist-check",
    "r30.hinge-foam",
    "r30.top-spar-cap",
    "r30.top-skin",
    # the GU stub chain moved here when the Roncz elevator ops became chapter 11 (it sorts by chapter, then by authored order)
    "c11.elevators",
    "c12.alignment-pins",
    "c12.align-canard",
    "r30.install-pins",
    "r30.align-canard",
]

# The chapter 14-17 ops (2.5) are checked in test_ch1417_graph.py and excluded from CANARD_ORDER above.
# The chapter 11 / 12 Roncz ops added in 2.4 (r30.* ids, chapters 11 and 12) are checked in test_ch1113_graph.py.
NEW_R30 = {
    "r30.f22-drill-tabs",
    "r30.elev-fuselage-clearance",
    "r30.lift-tab-bushings",
    "r30.f28-pins-permanent",
    "r30.canard-tips",
}


def test_topo_order_keeps_the_canard_order_and_follows_the_book_in_chapter_4():
    from guide.schema import topo_order

    g = load_graph(GRAPH)
    order = topo_order(g)
    assert [
        i
        for i in order
        if g.ops[i].chapter
        not in (
            4,
            5,
            6,
            7,
            8,
            9,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
        )
        and i not in NEW_R30
        and not i.startswith("r30.elev-")
    ] == CANARD_ORDER
    # plans pp 4-1 to 4-3: front seat, rear seat, panel/F22/F28, firewall
    assert [i for i in order if g.ops[i].chapter == 4] == [
        "f04.front-seat-bkhd-front",
        "f04.front-seat-bkhd-back",
        "f04.rear-seat-bkhd-foam",
        "f04.rear-seat-bkhd-hole",
        "f04.panel-f22-f28-aft",
        "f04.panel-f22-f28-fwd",
        "f04.firewall-aft",
        "f04.firewall-fwd",
    ]
    for ch in (5, 6):  # each chapter follows its file's list order
        assert [i for i in order if g.ops[i].chapter == ch] == [
            i for i in g.ops if g.ops[i].chapter == ch
        ]
