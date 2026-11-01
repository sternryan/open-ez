"""Step-graph schema for the Long-EZ build guide. Content is YAML in guide/graph/; see the M1 spec §5."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from core.sources import check_citation

if TYPE_CHECKING:
    from guide.catalog import CatalogItem
    from guide.resin import Resin

VARIANTS = {"gu", "roncz", "both"}
FIDELITY = {"no-geometry", "unvalidated", "plans-checked", "a-sheet-verified"}
STATUS = {"verified", "unresolved", "conflict"}
KIND = {"official", "community"}
FLAGS = {"official", "community", "derived", "estimate", "unsourced"}
CURE = {"none", "part", "all"}
BUY_FLAGS = {"official", "derived", "estimate"}
RESERVED = {
    "components.yaml",
    "pages.yaml",
    "annotations.yaml",
    "loadpaths.yaml",
    "tours.yaml",
    "groups.yaml",
    "scripts.yaml",
}
LOADPATH_KINDS = {"bending", "shear", "lift"}


OP_KEYS = {
    "id",
    "chapter",
    "title",
    "summary",
    "variants",
    "requires",
    "components",
    "geometry_visible",
    "materials",
    "sources",
    "changes",
    "completion",
    "inspection",
    "stub",
    "group",
    "plan",
}
PLAN_KEYS = {"people", "people_why", "hours", "cure", "resin", "tools", "buy", "fuel"}
VALUE_KEYS = {"value", "flag", "source"}
BUY_KEYS = {"item", "qty", "flag"}
FUEL_KEYS = {"wetted", "fuel", "resin_compat", "why", "source"}
RESIN_COMPAT = {"unknown", "sourced"}
FUEL_GRADE = "UL94"
GROUP_FILE_KEYS = {"groups", "required_files"}
GROUP_KEYS = {"id", "label"}
CHANGE_KEYS = {"cp", "lpc", "class", "status", "kind", "note", "annotation_pp"}
MATERIAL_KEYS = {"cloth", "plies", "where"}
ANNOTATION_KEYS = {"scan_pp", "cp", "lpc", "class", "text", "confirmed"}
COMPONENT_KEYS = {"id", "label", "fidelity"}
LOADPATH_FILE_KEYS = {"paths"}
LOADPATH_KEYS = {"id", "label", "kind", "parts"}
TOUR_FILE_KEYS = {"shots"}
SHOT_KEYS = {"target", "position"}


class SchemaError(ValueError):
    pass


def _extra(d, allowed: set, where: str) -> None:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(d).__name__}")
    bad = sorted((k for k in d if k not in allowed), key=str)
    if bad:
        raise SchemaError(f"{where}: unknown key(s) {bad}")


def _bool(d: dict, key: str, default: bool, where: str) -> bool:
    v = d.get(key, default)
    if not isinstance(v, bool):
        raise SchemaError(f"{where}: {key} must be a boolean, got {v!r}")
    return v


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
class Group:
    id: str
    label: str


@dataclass(frozen=True)
class Value:
    value: float | None
    flag: str
    source: str | None


@dataclass(frozen=True)
class Buy:
    item: str
    qty: float
    flag: str


@dataclass(frozen=True)
class Fuel:
    wetted: bool
    fuel: str
    resin_compat: str
    why: str
    source: str | None


@dataclass(frozen=True)
class Plan:
    people: int = 1
    people_why: str | None = None
    hours: Value | None = None
    cure: str = "none"
    resin: str | None = None
    tools: tuple[str, ...] = ()
    buy: tuple[Buy, ...] = ()
    fuel: Fuel | None = None


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
    group: str | None = None
    file: str = ""
    plan: Plan | None = None


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


@dataclass(frozen=True)
class LoadPath:
    id: str
    label: str
    kind: str
    parts: tuple[str, ...]


@dataclass
class Graph:
    ops: dict[str, Operation] = field(default_factory=dict)
    components: dict[str, Component] = field(default_factory=dict)
    annotations: list[Annotation] = field(default_factory=list)
    pages: dict[int, str] = field(default_factory=dict)
    loadpaths: list[LoadPath] = field(default_factory=list)
    tours: dict[str, dict] = field(
        default_factory=dict
    )  # op id -> {"target": [x, y, z], "position": [x, y, z]} camera shot
    groups: list[Group] = field(default_factory=list)
    groups_required: set[str] = field(default_factory=set)


def _read(path: Path):
    try:
        return yaml.safe_load(path.read_text()) or []
    except yaml.YAMLError as e:
        raise SchemaError(f"{path.name}: malformed YAML: {e}") from e


def _number(v, where: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SchemaError(f"{where}: must be a number, got {v!r}")
    number = float(v)
    if not math.isfinite(number):
        raise SchemaError(f"{where}: must be finite, got {v!r}")
    if number < 0:
        raise SchemaError(f"{where}: must be >= 0, got {v!r}")
    return number


def _http_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))


def _value(d, where: str) -> Value:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(d).__name__}")
    _extra(d, VALUE_KEYS, where)
    flag = d.get("flag")
    if flag not in FLAGS:
        raise SchemaError(f"{where}: bad flag {flag!r}")
    raw = d.get("value")
    value = None if raw is None else _number(raw, f"{where} value")
    source = d.get("source")
    if flag == "unsourced":
        if value is not None:
            raise SchemaError(f"{where}: unsourced value must be null")
        if source is not None:
            raise SchemaError(f"{where}: unsourced carries no source")
    elif flag == "estimate":
        if source is not None:
            raise SchemaError(f"{where}: estimate carries no source")
    elif flag == "official":
        if not isinstance(source, str):
            raise SchemaError(f"{where}: official needs a registry citation")
        try:
            check_citation(source)
        except ValueError as e:
            raise SchemaError(f"{where}: {e}") from e
    elif flag == "community":
        if not isinstance(source, str) or not _http_url(source):
            raise SchemaError(f"{where}: community source must be an http(s) URL")
    elif not isinstance(source, str) or source.strip() == "":
        raise SchemaError(
            f"{where}: derived source must be a non-empty derivation note"
        )
    return Value(value, flag, source)


def _buy(d, where: str) -> Buy:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(d).__name__}")
    _extra(d, BUY_KEYS, where)
    item = d.get("item")
    if not isinstance(item, str) or item.strip() == "":
        raise SchemaError(f"{where}: item must be a non-empty string")
    if "qty" not in d:
        raise SchemaError(f"{where}: qty required")
    flag = d.get("flag")
    if flag not in BUY_FLAGS:
        raise SchemaError(f"{where}: bad flag {flag!r}")
    return Buy(item, _number(d["qty"], f"{where} qty"), flag)


def _fuel(d, where: str) -> Fuel:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(d).__name__}")
    _extra(d, FUEL_KEYS, where)
    wetted = d.get("wetted")
    if wetted is not True:
        raise SchemaError(f"{where}: wetted must be true, got {wetted!r}")
    grade = d.get("fuel")
    if grade != FUEL_GRADE:
        raise SchemaError(f"{where}: bad fuel {grade!r}")
    compat = d.get("resin_compat")
    if compat not in RESIN_COMPAT:
        raise SchemaError(f"{where}: bad resin_compat {compat!r}")
    why = d.get("why")
    if not isinstance(why, str) or why.strip() == "":
        raise SchemaError(f"{where}: why must be a non-empty string, got {why!r}")
    source = d.get("source")
    if compat == "sourced":
        if not isinstance(source, str) or source.strip() == "":
            raise SchemaError(f"{where}: sourced needs a source")
        try:
            check_citation(source)
        except ValueError as e:
            raise SchemaError(f"{where}: {e}") from e
    elif source is not None:
        raise SchemaError(f"{where}: unknown carries no source")
    return Fuel(True, grade, compat, why, source)


def _plan(d, where: str) -> Plan:
    if not isinstance(d, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(d).__name__}")
    _extra(d, PLAN_KEYS, where)
    people = d.get("people", 1)
    if isinstance(people, bool) or people not in (1, 2):
        raise SchemaError(f"{where}: people must be 1 or 2, got {people!r}")
    why = d.get("people_why")
    if people == 2 and (not isinstance(why, str) or why.strip() == ""):
        raise SchemaError(f"{where}: people_why required when people is 2")
    if why is not None and not isinstance(why, str):
        raise SchemaError(f"{where}: people_why must be a string, got {why!r}")
    hours = d.get("hours")
    parsed_hours = None if hours is None else _value(hours, f"{where} hours")
    cure = d.get("cure", "none")
    if cure not in CURE:
        raise SchemaError(f"{where}: bad cure {cure!r}")
    resin = d.get("resin")
    if cure != "none":
        if not isinstance(resin, str) or resin.strip() == "":
            raise SchemaError(f"{where}: resin required when cure is not none")
    elif resin is not None and not isinstance(resin, str):
        raise SchemaError(f"{where}: resin must be a string, got {resin!r}")
    tools = d.get("tools", [])
    if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
        raise SchemaError(f"{where}: tools must be a list of strings")
    raw_buy = d.get("buy", [])
    if not isinstance(raw_buy, list):
        raise SchemaError(f"{where}: buy must be a list")
    buy = tuple(_buy(b, f"{where} buy {i}") for i, b in enumerate(raw_buy))
    raw_fuel = d.get("fuel")
    parsed_fuel = None if raw_fuel is None else _fuel(raw_fuel, f"{where} fuel")
    return Plan(
        people=people,
        people_why=why,
        hours=parsed_hours,
        cure=cure,
        resin=resin,
        tools=tuple(tools),
        buy=buy,
        fuel=parsed_fuel,
    )


def _groups(path: Path) -> tuple[list[Group], set[str]]:
    data = _read(path)
    if not isinstance(data, dict):
        raise SchemaError("groups.yaml: must be a mapping")
    _extra(data, GROUP_FILE_KEYS, "groups.yaml")
    rows = data.get("groups", [])
    if not isinstance(rows, list):
        raise SchemaError("groups.yaml: groups must be a list")
    groups: list[Group] = []
    for idx, row in enumerate(rows):
        where = f"groups.yaml group {idx}"
        if not isinstance(row, dict):
            raise SchemaError(f"{where}: must be a mapping")
        _extra(row, GROUP_KEYS, where)
        gid, label = row.get("id"), row.get("label")
        if not isinstance(gid, str) or gid.strip() == "":
            raise SchemaError(f"{where}: id must be a non-empty string")
        if not isinstance(label, str) or label.strip() == "":
            raise SchemaError(f"{where}: label must be a non-empty string")
        groups.append(Group(gid, label))
    required = data.get("required_files", [])
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        raise SchemaError("groups.yaml: required_files must be a list of file names")
    return groups, set(required)


def _op(d: dict, file_name: str, idx: int) -> Operation:
    if not isinstance(d, dict):
        raise SchemaError(f"{file_name} entry {idx}: must be a mapping")
    op_id = d.get("id", f"entry_{idx}")
    where = f"{file_name} entry {idx} ({op_id})"
    _extra(d, OP_KEYS, where)
    group = d.get("group")
    if group is not None and not isinstance(group, str):
        raise SchemaError(f"{where}: group must be a string, got {group!r}")
    plan = _plan(d["plan"], f"{where} plan") if d.get("plan") is not None else None
    try:
        sources = []
        for s in d.get("sources", []):
            try:
                sources.append(Source(**s))
            except (TypeError, ValueError, AttributeError) as e:
                raise SchemaError(
                    f"{file_name} entry {idx} ({op_id}): source error: {e}"
                ) from e

        changes = []
        for ci, c in enumerate(d.get("changes", [])):
            _extra(c, CHANGE_KEYS, f"{where} change {ci}")
            try:
                changes.append(
                    Change(
                        cp=c["cp"],
                        lpc=c["lpc"],
                        cls=c["class"],
                        status=c["status"],
                        kind=c["kind"],
                        note=c.get("note", ""),
                        annotation_pp=c.get("annotation_pp"),
                    )
                )
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise SchemaError(
                    f"{file_name} entry {idx} ({op_id}): change error: {e}"
                ) from e

        for mi, m in enumerate(d.get("materials", [])):
            _extra(m, MATERIAL_KEYS, f"{where} material {mi}")

        return Operation(
            id=d["id"],
            chapter=int(d["chapter"]),
            title=d["title"],
            summary=d.get("summary", ""),
            variants=tuple(d.get("variants", ["both"])),
            requires=tuple(d.get("requires", [])),
            components=tuple(d.get("components", [])),
            geometry_visible=_bool(d, "geometry_visible", True, where),
            materials=tuple(d.get("materials", [])),
            sources=tuple(sources),
            changes=tuple(changes),
            completion=tuple(d.get("completion", [])),
            inspection=_bool(d, "inspection", False, where),
            stub=_bool(d, "stub", False, where),
            group=group,
            file=file_name,
            plan=plan,
        )
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        op_id = d.get("id", f"entry_{idx}")
        raise SchemaError(f"{file_name} entry {idx} ({op_id}): {e}") from e


def load_graph(graph_dir: Path) -> Graph:
    g = Graph()
    comp = graph_dir / "components.yaml"
    if comp.exists():
        comp_data = _read(comp)
        if not isinstance(comp_data, list):
            raise SchemaError("components.yaml: must be a list of components")
        for idx, c in enumerate(comp_data):
            _extra(c, COMPONENT_KEYS, f"components.yaml entry {idx}")
            try:
                g.components[c["id"]] = Component(
                    c["id"], c.get("label", c["id"]), c["fidelity"]
                )
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
        ann_data = _read(ann)
        if not isinstance(ann_data, list):
            raise SchemaError("annotations.yaml: must be a list of annotations")
        for idx, a in enumerate(ann_data):
            where = f"annotations.yaml entry {idx}"
            _extra(a, ANNOTATION_KEYS, where)
            try:
                g.annotations.append(
                    Annotation(
                        a["scan_pp"],
                        a["cp"],
                        a["lpc"],
                        a["class"],
                        a.get("text", ""),
                        _bool(a, "confirmed", False, where),
                    )
                )
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise SchemaError(f"{where}: {e}") from e
    lp = graph_dir / "loadpaths.yaml"
    if lp.exists():
        lp_data = _read(lp)
        _extra(lp_data, LOADPATH_FILE_KEYS, "loadpaths.yaml")
        if not isinstance(lp_data.get("paths"), list):
            raise SchemaError("loadpaths.yaml: paths must be a list")
        for idx, d in enumerate(lp_data["paths"]):
            where = f"loadpaths.yaml entry {idx}"
            _extra(d, LOADPATH_KEYS, where)
            parts = d.get("parts")
            if not isinstance(parts, list):
                raise SchemaError(f"{where}: parts must be a list")
            try:
                g.loadpaths.append(
                    LoadPath(d["id"], d.get("label", ""), d["kind"], tuple(parts))
                )
            except (KeyError, TypeError, ValueError, AttributeError) as e:
                raise SchemaError(f"{where}: {e}") from e
    tp = graph_dir / "tours.yaml"
    if tp.exists():
        t_data = _read(tp)
        _extra(t_data, TOUR_FILE_KEYS, "tours.yaml")
        shots = t_data.get("shots")
        if not isinstance(shots, dict):
            raise SchemaError("tours.yaml: shots must be a mapping of op id to shot")
        for op_id, shot in shots.items():
            where = f"tours.yaml shot {op_id}"
            _extra(shot, SHOT_KEYS, where)
            for k in SHOT_KEYS:
                v = shot.get(k)
                if not (
                    isinstance(v, list)
                    and len(v) == 3
                    and all(
                        isinstance(x, (int, float)) and not isinstance(x, bool)
                        for x in v
                    )
                ):
                    raise SchemaError(
                        f"{where}: {k} must be a list of 3 numbers, got {v!r}"
                    )
            g.tours[str(op_id)] = {
                k: [float(x) for x in shot[k]] for k in ("target", "position")
            }
    groups = graph_dir / "groups.yaml"
    if groups.exists():
        g.groups, g.groups_required = _groups(groups)
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
    seen_groups: set[str] = set()
    for grp in g.groups:
        if grp.id in seen_groups:
            errs.append(f"groups.yaml: duplicate group {grp.id}")
        seen_groups.add(grp.id)
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
        if op.group:
            if op.group not in seen_groups:
                errs.append(f"{op.id}: group '{op.group}' not in groups.yaml")
        elif op.file in g.groups_required and not op.stub and op.variants != ("gu",):
            errs.append(f"{op.id}: missing group")
        # Check change status and kind for ALL ops (including stubs)
        for ch in op.changes:
            if ch.status not in STATUS:
                errs.append(f"{op.id}: bad change status {ch.status}")
            if ch.kind not in KIND:
                errs.append(f"{op.id}: bad change kind {ch.kind}")
            if (
                ch.status == "verified"
                and ch.kind == "official"
                and (ch.cp <= 0 or ch.lpc <= 0)
            ):
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
            errs.append(
                f"annotation scan_pp {a.scan_pp} CP {a.cp} LPC {a.lpc} not linked to any op"
            )
    seen_paths: set[str] = set()
    for lp in g.loadpaths:
        if lp.id in seen_paths:
            errs.append(f"load path {lp.id}: duplicate id")
        seen_paths.add(lp.id)
        if not lp.label.strip():
            errs.append(f"load path {lp.id}: label required")
        if lp.kind not in LOADPATH_KINDS:
            errs.append(f"load path {lp.id}: bad kind {lp.kind}")
        if not lp.parts:
            errs.append(f"load path {lp.id}: at least one part required")
        for cid in lp.parts:
            if cid not in g.components:
                errs.append(f"load path {lp.id}: unknown component {cid}")
    for op_id in g.tours:
        if op_id not in g.ops:
            errs.append(f"tours.yaml: shot for unknown op {op_id}")
    errs.extend(_cycle(g))
    return errs


WING_CHAPTERS = (19, 30)


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

    # Within a chapter the authored order (the chapter file's list order) breaks ties, not the op id:
    # ids sort alphabetically, which put chapter 4's firewall ahead of the seat bulkheads.
    authored = {op_id: k for k, op_id in enumerate(g.ops)}

    # An op that waits on the wing or winglet chapters (19 to 29: the aileron linkage, the rudder
    # cable rig) is walked with the chapter it waits on, after that chapter's own ops. Walked at its
    # own chapter (16), its prerequisites were pulled in with it and put all of chapters 19 and 20
    # ahead of chapters 17 and 18. Chapters 30 and up (canard revisions) and the earlier-chapter
    # pulls (the spar before the firewall bond) keep the plain pull-in behaviour.
    eff: dict[str, int] = {}

    def effective(n: str) -> int:
        if n not in eff:
            eff[n] = g.ops[n].chapter  # cycle guard; validate() reports cycles
            late = [
                effective(r)
                for r in g.ops[n].requires
                if r in g.ops and WING_CHAPTERS[0] <= effective(r) < WING_CHAPTERS[1]
            ]
            eff[n] = max([g.ops[n].chapter, *late])
        return eff[n]

    def key(i: str) -> tuple[int, int, int, int]:
        e = effective(i)
        return (e, int(e != g.ops[i].chapter), g.ops[i].chapter, authored[i])

    for n in sorted(g.ops, key=key):
        visit(n)
    return order


def validate_refs(
    g: Graph,
    catalog: dict[str, CatalogItem],
    resins: dict[str, Resin],
) -> list[str]:
    """Shape is checked in validate; this checks catalog and resin ids only."""
    errs: list[str] = []
    for op in g.ops.values():
        if op.plan is None:
            continue
        for buy in op.plan.buy:
            if buy.item not in catalog:
                errs.append(f"{op.id}: buy item '{buy.item}' not in catalog")
        if op.plan.resin is not None and op.plan.resin not in resins:
            errs.append(f"{op.id}: resin '{op.plan.resin}' not in data/resins")
    return errs


def authored_texts(g: Graph) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for op in g.ops.values():
        if op.summary:
            out.append((f"{op.id}.summary", op.summary))
        out += [(f"{op.id}.completion[{i}]", t) for i, t in enumerate(op.completion)]
        out += [
            (f"{op.id}.changes[{i}].note", c.note)
            for i, c in enumerate(op.changes)
            if c.note
        ]
    out += [(f"loadpath.{lp.id}.label", lp.label) for lp in g.loadpaths if lp.label]
    return out
