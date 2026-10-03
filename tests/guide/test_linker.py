from guide.schema import Graph, Operation, Source, Annotation
from guide.lpc import PlansChange
from guide.cobelu_markers import Marker
from guide.linker import candidates, recall, op_pages


def graph():
    g = Graph()
    g.pages = {58: "10-5", 171: "back-cover", 71: "12-1"}
    g.ops["c10.cores"] = Operation(
        id="c10.cores",
        chapter=10,
        title="t",
        summary="s",
        sources=(
            Source(doc="scan-1980", scan_pp=58),
            Source(doc="cobelu", heading="STEP 2 -"),
        ),
        completion=("x",),
    )
    g.ops["c12.pins"] = Operation(
        id="c12.pins",
        chapter=12,
        title="t",
        summary="s",
        sources=(Source(doc="scan-1980", page="12-1"),),
        completion=("x",),
    )
    g.annotations = [
        Annotation(58, 25, 16, "MEO", "t", True),
        Annotation(71, 26, 40, "MEO", "t", True),
        Annotation(171, 25, 7, "MEO", "t", True),
        Annotation(58, 30, 1, "MEO", "t", False),
    ]
    return g


LPCS = [
    PlansChange(16, "MEO", "10-5", 10, 25, ""),
    PlansChange(7, "MEO", "back-cover", None, 25, ""),
    PlansChange(99, "MEO", "10-9", 10, 27, ""),
]
MARKERS = [Marker(27, 44, "MEO", 10, "STEP 2 -", 5)]


def test_op_pages_resolves_scan_and_page_refs():
    g = graph()
    assert op_pages(g.ops["c10.cores"], g) == {"10-5"}
    assert op_pages(g.ops["c12.pins"], g) == {"12-1"}


def test_candidates_by_page_and_heading():
    got = {(c.op_id, c.cp, c.lpc, c.origin) for c in candidates(graph(), LPCS, MARKERS)}
    assert ("c10.cores", 25, 16, "lpc") in got
    assert ("c10.cores", 27, 44, "marker") in got
    assert not any(c[2] == 99 for c in got)  # page 10-9 is not a source page


def test_recall_scoped_to_chapters_and_confirmed():
    g = graph()
    hits, misses = recall(g, candidates(g, LPCS, MARKERS), {10, 12})
    assert [(a.cp, a.lpc) for a in hits] == [(25, 16)]
    assert [(a.cp, a.lpc) for a in misses] == [
        (26, 40)
    ]  # back-cover and unconfirmed excluded
