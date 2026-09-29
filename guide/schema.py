"""Step-graph schema for the Long-EZ build guide. Content is YAML in guide/graph/; see the M1 spec §5."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

VARIANTS = {"gu", "roncz", "both"}
FIDELITY = {"no-geometry", "unvalidated", "plans-checked", "a-sheet-verified"}
STATUS = {"verified", "unresolved", "conflict"}
KIND = {"official", "community"}
RESERVED = {"components.yaml", "pages.yaml", "annotations.yaml"}


class SchemaError(ValueError):
    pass


@dataclass(frozen=True)
class Source:
    doc: str
    page: str | None = None
    scan_pp: int | None = None
    figure: str | None = None
    heading: str | None = None


@dataclass(frozen=True)
class Change:
    cp: int
    lpc: int
    cls: str
    status: str
    kind: str
    note: str
    annotation_pp: int | None = None


@dataclass(frozen=True)
class Operation:
    id: str
    chapter: int
    title: str
    summary: str = ""
    variants: tuple[str, ...] = ("both",)
    requires: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    geometry_visible: bool = True
    materials: tuple[dict, ...] = ()
    sources: tuple[Source, ...] = ()
    changes: tuple[Change, ...] = ()
    completion: tuple[str, ...] = ()
    inspection: bool = False
    stub: bool = False


@dataclass(frozen=True)
class Component:
    id: str
    label: str
    fidelity: str


@dataclass(frozen=True)
class Annotation:
    scan_pp: int
    cp: int
    lpc: int
    cls: str
    text: str
    confirmed: bool


@dataclass
class Graph:
    ops: dict[str, Operation] = field(default_factory=dict)
    components: dict[str, Component] = field(default_factory=dict)
    annotations: list[Annotation] = field(default_factory=list)
    pages: dict[int, str] = field(default_factory=dict)


def _read(path: Path):
    try:
        return yaml.safe_load(path.read_text()) or []
    except yaml.YAMLError as e:
        raise SchemaError(f"{path.name}: malformed YAML: {e}") from e


def _op(d: dict, file_name: str, idx: int) -> Operation:
    try:
        op_id = d.get("id", f"entry_{idx}")
        sources = []
        for s in d.get("sources", []):
            try:
                sources.append(Source(**s))
            except (TypeError, ValueError, AttributeError) as e:
                raise SchemaError(f"{file_name} entry {idx} ({op_id}): source error: {e}") from e

        changes = []
        for c in d.get("changes", []):
            try:
                changes.append(Change(cp=c["cp"], lpc=c["lpc"], cls=c["class"], status=c["status"], kind=c["kind"],
                       note=c.get("note", ""), annotation_pp=c.get("annotation_pp")))
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise SchemaError(f"{file_name} entry {idx} ({op_id}): change error: {e}") from e

        return Operation(
            id=d["id"],
            chapter=int(d["chapter"]),
            title=d["title"],
            summary=d.get("summary", ""),
            variants=tuple(d.get("variants", ["both"])),
            requires=tuple(d.get("requires", [])),
            components=tuple(d.get("components", [])),
            geometry_visible=bool(d.get("geometry_visible", True)),
            materials=tuple(d.get("materials", [])),
            sources=tuple(sources),
            changes=tuple(changes),
            completion=tuple(d.get("completion", [])),
            inspection=bool(d.get("inspection", False)),
            stub=bool(d.get("stub", False)),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        op_id = d.get("id", f"entry_{idx}")
        raise SchemaError(f"{file_name} entry {idx} ({op_id}): {e}") from e


def load_graph(graph_dir: Path) -> Graph:
    g = Graph()
    comp = graph_dir / "components.yaml"
    if comp.exists():
        for idx, c in enumerate(_read(comp)):
            try:
                g.components[c["id"]] = Component(c["id"], c.get("label", c["id"]), c["fidelity"])
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise SchemaError(f"components.yaml entry {idx}: {e}") from e
    pages = graph_dir / "pages.yaml"
    if pages.exists():
        try:
            pages_data = _read(pages)
            if not isinstance(pages_data, dict):
                raise SchemaError("pages.yaml: must be a mapping, not a list")
            g.pages = {int(k): str(v) for k, v in (pages_data or {}).items()}
        except SchemaError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise SchemaError(f"pages.yaml: {e}") from e
    ann = graph_dir / "annotations.yaml"
    if ann.exists():
        try:
            g.annotations = [
                Annotation(a["scan_pp"], a["cp"], a["lpc"], a["class"], a.get("text", ""), bool(a.get("confirmed", False)))
                for idx, a in enumerate(_read(ann))
            ]
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            raise SchemaError(f"annotations.yaml entry {idx}: {e}") from e
    for f in sorted(graph_dir.glob("*.yaml")):
        if f.name in RESERVED:
            continue
        try:
            ops_data = _read(f)
            if not isinstance(ops_data, list):
                raise SchemaError(f"{f.name}: must be a list of operations")
            for idx, d in enumerate(ops_data):
                op = _op(d, f.name, idx)
                if op.id in g.ops:
                    raise SchemaError(f"duplicate op id {op.id} in {f.name}")
                g.ops[op.id] = op
        except SchemaError:
            raise
        except (TypeError, ValueError, AttributeError) as e:
            raise SchemaError(f"{f.name}: {e}") from e
    return g


def _cycle(g: Graph) -> list[str]:
    state: dict[str, int] = {}
    errs: list[str] = []

    def visit(n: str, path: list[str]):
        if state.get(n) == 1:
            errs.append("cycle: " + " -> ".join(path + [n]))
            return
        if state.get(n) == 2 or n not in g.ops:
            return
        state[n] = 1
        for r in g.ops[n].requires:
            visit(r, path + [n])
        state[n] = 2

    for n in g.ops:
        visit(n, [])
    return errs


def validate(g: Graph) -> list[str]:
    errs: list[str] = []
    for c in g.components.values():
        if c.fidelity not in FIDELITY:
            errs.append(f"component {c.id}: bad fidelity {c.fidelity}")
    linked = {(ch.cp, ch.lpc) for op in g.ops.values() for ch in op.changes}
    for op in g.ops.values():
        for r in op.requires:
            if r not in g.ops:
                errs.append(f"{op.id}: requires unknown op {r}")
        # Check variants and components for ALL ops (including stubs)
        for v in op.variants:
            if v not in VARIANTS:
                errs.append(f"{op.id}: bad variant {v}")
        for cid in op.components:
            if cid not in g.components:
                errs.append(f"{op.id}: unknown component {cid}")
        # Check change status and kind for ALL ops (including stubs)
        for ch in op.changes:
            if ch.status not in STATUS:
                errs.append(f"{op.id}: bad change status {ch.status}")
            if ch.kind not in KIND:
                errs.append(f"{op.id}: bad change kind {ch.kind}")
            if ch.status == "verified" and ch.kind == "official" and (ch.cp <= 0 or ch.lpc <= 0):
                errs.append(f"{op.id}: verified official change needs cp and lpc")
        # Only non-stub ops need summary, sources, completion
        if op.stub:
            continue
        if not op.summary.strip():
            errs.append(f"{op.id}: summary required")
        if not op.sources:
            errs.append(f"{op.id}: at least one source required")
        if not op.completion:
            errs.append(f"{op.id}: completion checklist required")
        for s in op.sources:
            if s.scan_pp is not None and s.scan_pp not in g.pages:
                errs.append(f"{op.id}: scan_pp {s.scan_pp} not in pages.yaml")
    for a in g.annotations:
        if a.confirmed and (a.cp, a.lpc) not in linked:
            errs.append(f"annotation scan_pp {a.scan_pp} CP {a.cp} LPC {a.lpc} not linked to any op")
    errs.extend(_cycle(g))
    return errs


def topo_order(g: Graph) -> list[str]:
    order: list[str] = []
    seen: set[str] = set()

    def visit(n: str):
        if n in seen or n not in g.ops:
            return
        seen.add(n)
        for r in g.ops[n].requires:
            visit(r)
        order.append(n)

    for n in sorted(g.ops, key=lambda i: (g.ops[i].chapter, i)):
        visit(n)
    return order


def authored_texts(g: Graph) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for op in g.ops.values():
        if op.summary:
            out.append((f"{op.id}.summary", op.summary))
        out += [(f"{op.id}.completion[{i}]", t) for i, t in enumerate(op.completion)]
        out += [(f"{op.id}.changes[{i}].note", c.note) for i, c in enumerate(op.changes) if c.note]
    return out
