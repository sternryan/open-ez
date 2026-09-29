from pathlib import Path
from guide.schema import load_graph, validate

GRAPH = Path(__file__).resolve().parents[2] / "guide" / "graph"


def test_committed_graph_is_valid_and_covers_dod():
    g = load_graph(GRAPH)
    assert validate(g) == []
    ops = list(g.ops.values())
    assert any(o.stub for o in ops)
    assert any(not o.geometry_visible for o in ops)
    variants = {v for o in ops for v in o.variants}
    assert {"gu", "roncz"} <= variants
    linked = {(c.cp, c.lpc) for o in ops for c in o.changes}
    confirmed = [a for a in g.annotations if a.confirmed]
    assert confirmed and all((a.cp, a.lpc) in linked for a in confirmed)
