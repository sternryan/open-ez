"""Ground school replaces the education stub. Lessons are the ground-school group."""

from pathlib import Path

from guide.schema import load_graph, topo_order
from guide.scripts_schema import ACTIONS, load_scripts, scripts_for

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"
LAST = "g00.bookend"

# Ops whose requires listed c03.layup-skills when the stub was still real
# (re-grep of guide/graph on 2026-10-21, before the rewire).
FORMER_DEPENDENTS = (
    "c10.templates-cores",
    "f04.firewall-aft",
    "f04.front-seat-bkhd-front",
    "f04.panel-f22-f28-aft",
    "f04.rear-seat-bkhd-foam",
    "f05.side-blank",
    "f09.strut-stiffen",
    "f13.strut-reinforce",
    "f13.worm-drive-bench",
    "f14.cs4-forward",
    "f14.jig",
    "f14.lwa-fabricate",
    "f15.parts-fab",
    "f17.parts",
    "f18.trim-plexi",
    "f19.jig",
    "f21.cut-parts",
    "r30.elev-nc2-inserts",
    "r30.templates-cores",
)


def needs(g, op_id):
    seen, stack = set(), [op_id]
    while stack:
        for r in g.ops[stack.pop()].requires:
            if r not in seen:
                seen.add(r)
                stack.append(r)
    return seen


def test_stub_removed():
    g = load_graph(GRAPH)
    assert "c03.layup-skills" not in g.ops
    stub_text = (GRAPH / "stubs.yaml").read_text()
    assert "c03.layup-skills" not in stub_text
    assert g.ops["c11.elevators"].stub
    assert g.ops["ref.back-cover-3view"].stub


def test_all_stub_dependents_rewired():
    g = load_graph(GRAPH)
    assert len(FORMER_DEPENDENTS) == 19
    for op_id in FORMER_DEPENDENTS:
        op = g.ops[op_id]
        assert "c03.layup-skills" not in op.requires
        assert LAST in op.requires
        assert LAST in needs(g, op_id)
    for op in g.ops.values():
        assert "c03.layup-skills" not in op.requires


def test_ground_precedes_build():
    g = load_graph(GRAPH)
    assert g.groups[0].id == "ground-school"
    assert "ch00_ground.yaml" in g.groups_required
    ground = [op for op in g.ops.values() if op.group == "ground-school"]
    assert ground
    assert all(op.file == "ch00_ground.yaml" for op in ground)
    assert g.ops[LAST].group == "ground-school"
    order = topo_order(g)
    last_ground = max(order.index(op.id) for op in ground)
    first_build = min(
        order.index(op.id)
        for op in g.ops.values()
        if not op.stub and op.group != "ground-school"
    )
    assert last_ground < first_build
    for op in g.ops.values():
        if op.stub or op.group == "ground-school":
            continue
        assert LAST in needs(g, op.id), op.id


def test_ground_scripts_cover_action_vocabulary():
    g = load_graph(GRAPH)
    scripts = scripts_for(g, load_scripts(GRAPH))
    seen: set[str] = set()
    ground_ids = [op.id for op in g.ops.values() if op.group == "ground-school"]
    assert ground_ids
    for op_id in ground_ids:
        actions = scripts[op_id]
        assert actions, op_id
        for i, action in enumerate(actions):
            why = action.get("why")
            assert isinstance(why, str) and why.strip(), (op_id, i)
            seen.add(action["do"])
    assert seen == set(ACTIONS)
