"""Propose plans-change links per operation and score recall against the prior owner's annotations."""
from __future__ import annotations

from dataclasses import dataclass

from guide.cobelu_markers import Marker
from guide.lpc import PlansChange
from guide.schema import Annotation, Graph, Operation


@dataclass(frozen=True)
class Candidate:
    op_id: str
    cp: int
    lpc: int
    cls: str
    origin: str


def _norm(h: str) -> str:
    return " ".join(h.lower().replace("–", "-").split()).rstrip(" -")


def op_pages(op: Operation, g: Graph) -> set[str]:
    out: set[str] = set()
    for s in op.sources:
        if s.page:
            out.add(s.page)
        elif s.scan_pp is not None and s.scan_pp in g.pages:
            out.add(g.pages[s.scan_pp])
    return out


def candidates(g: Graph, lpcs: list[PlansChange], markers: list[Marker]) -> list[Candidate]:
    out: list[Candidate] = []
    for op in g.ops.values():
        if op.stub:
            continue
        pages = op_pages(op, g)
        heads = {_norm(s.heading) for s in op.sources if s.heading}
        out += [Candidate(op.id, c.cp, c.lpc, c.cls, "lpc") for c in lpcs
                if c.chapter == op.chapter and c.page in pages]
        out += [Candidate(op.id, m.cp, m.lpc, m.cls, "marker") for m in markers
                if m.chapter == op.chapter and _norm(m.heading) in heads]
    return out


def _chapter(page: str | None) -> int | None:
    if page and page[0].isdigit():
        return int(page.split("-")[0])
    return None


def recall(g: Graph, cands: list[Candidate], chapters: set[int]) -> tuple[list[Annotation], list[Annotation]]:
    found = {(c.cp, c.lpc) for c in cands}
    scoped = [a for a in g.annotations if a.confirmed and _chapter(g.pages.get(a.scan_pp)) in chapters]
    hits = [a for a in scoped if (a.cp, a.lpc) in found]
    misses = [a for a in scoped if (a.cp, a.lpc) not in found]
    return hits, misses
