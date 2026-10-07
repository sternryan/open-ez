# Long-EZ Build Guide M1 "Build Rehearsal" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A private-network-served interactive canard build rehearsal (ch 10/30/12): a validated step graph, plans-change links scored against the prior owner's annotations, a selectable 3D canard, and a source pane.

**Architecture:** A new `guide/` package inside open-ez (public) holds the schema, parsers, gates, exporter, and a static three.js viewer. Authored content is YAML in `guide/graph/`, in our own words. Private assets (scan page images, OCR text) never enter git. They are built into a cache dir, rsynced to the private-network host, and symlinked into the served site.

**Tech Stack:** Python 3.12 (uv venv), CadQuery ≥2.4, PyYAML, PyMuPDF, tesseract, markdown; three.js (vendored ES modules); node:test for viewer logic; Playwright (Python) for e2e.

**Spec:** `docs/superpowers/specs/2026-09-28-build-guide-m1-design.md`

## Global Constraints

- open-ez is a **PUBLIC** repo. Never commit: scan images, OCR text, verbatim plans or Canard Pusher text, private-network hostnames/IPs, personal filesystem paths. Deploy targets come from env vars (`LONGEZ_DEPLOY_HOST`, `LONGEZ_SITE_URL`), with no defaults in code.
- Never claim the plans are public domain anywhere in the repo.
- `python -m guide.check` (full mode, sources present) must pass before any commit touching `guide/graph/`.
- Materials/plies/dimensions in content come only from sources. Never invented.
- Default variant in the viewer is `roncz` (AGENTS.md safety mandate).
- No runtime CDN: three.js is vendored; its version is enumerated at vendoring time (`npm view three version`) and recorded with the date in `guide/viewer/vendor/three/VERSION`.
- Commit messages: conventional prefix; **no `Claude-Session:` trailer** (owner's house rule 10).
- Private asset layout on the host: `<host private dir>/private/scan-1980/pages/NNN.jpg` (NNN = zero-padded scan page).
- Local caches (outside repo): `~/.cache/long-ez/scan-1980/{pages,text}`, `~/.cache/long-ez/cobelu` (a git clone of cobelu/Long-EZ).
- All local paths and the deploy target live in `~/.config/long-ez/env` (never committed). Source env vars for the overlap gate: `LONGEZ_CP_SECTIONS` (path to `CPs_1_to_82_Sections.txt`), `LONGEZ_COBELU_DIR`, `LONGEZ_SCAN_TEXT_DIR`. Full-mode check exits **2** if any is missing.
- Log each implementation wave to `~/.claude/state/lane-log.tsv`.

## Review Focus

1. **Viewer opened off-private-network / no private assets** (`scanBase: null`): the source pane shows the cobelu figure link or "scan not available", never a broken image. Pinned in Task 11.
2. **localStorage throws** (private browsing): checklist ticks still work in memory; no crash. Pinned in Task 11.
3. **Model file missing/404**: ops, sources and checklists still render with a "3D unavailable" notice. Pinned in Task 11.
4. **CP entry with no page** (`LPC #7, MEO, Back cover of plans.`) or a multi-line description: parsed, not dropped. Pinned in Task 2.
5. **OCR noise in page refs** (`Pg 10 – 5`, en-dash, stray spaces): normalized to `10-5`. Pinned in Task 8.

---

### Task 0: Working CadQuery env + baseline

**Files:**
- Modify: `requirements.txt` (append `pyyaml>=6.0`, `pymupdf>=1.24`, `markdown>=3.5`)
- Create: `requirements-guide-dev.txt` (`playwright>=1.45`)
- Modify: `.gitignore` (append `site/`, `.venv/`, `output/guide/`)

**Interfaces:** Produces `.venv/` with `import cadquery` working; later tasks run `.venv/bin/python`.

- [ ] **Step 1: Create the venv and install**

```bash
cd ~/open-ez
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt -r requirements-dev.txt -r requirements-guide-dev.txt
.venv/bin/python -m playwright install chromium
```

- [ ] **Step 2: Prove CadQuery works and the canard still generates**

Run: `.venv/bin/python -c "import cadquery; print(cadquery.__version__)" && .venv/bin/python scripts/generate_canard.py`
Expected: a version ≥2.4 prints; the script ends with `GENERATION COMPLETE` and writes `output/STEP/canard_core.step`. If the loft fails, STOP and report BLOCKED with the traceback. Do not patch geometry in this plan.

- [ ] **Step 3: Record the test baseline (do not fix failures)**

Run: `.venv/bin/python -m pytest -q -x --co -q | tail -3 && .venv/bin/python -m pytest -q 2>&1 | tail -5`
Expected: record the pass/fail summary line verbatim in the commit message body. Pre-existing failures are baseline, not this plan's job.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt requirements-guide-dev.txt .gitignore
git commit -m "chore(guide): add guide deps and ignore build outputs" -m "Baseline pytest: <paste summary line>"
```

---

### Task 1: Step-graph schema, loader, validator

**Files:**
- Create: `guide/__init__.py` (empty), `guide/schema.py`
- Test: `tests/guide/__init__.py` (empty), `tests/guide/test_schema.py`

**Interfaces:**
- Produces:
  - dataclasses `Source(doc: str, page: str|None, scan_pp: int|None, figure: str|None, heading: str|None)`, `Change(cp: int, lpc: int, cls: str, status: str, kind: str, note: str, annotation_pp: int|None)`, `Operation(id, chapter: int, title: str, summary: str, variants: tuple[str,...], requires: tuple[str,...], components: tuple[str,...], geometry_visible: bool, materials: tuple[dict,...], sources: tuple[Source,...], changes: tuple[Change,...], completion: tuple[str,...], inspection: bool, stub: bool)`, `Component(id: str, label: str, fidelity: str)`, `Annotation(scan_pp: int, cp: int, lpc: int, cls: str, text: str, confirmed: bool)`, `Graph(ops: dict[str, Operation], components: dict[str, Component], annotations: list[Annotation], pages: dict[int, str])`
  - `load_graph(graph_dir: Path) -> Graph` (raises `SchemaError` on duplicate op ids or malformed YAML)
  - `validate(g: Graph) -> list[str]` (empty list = valid)
  - `topo_order(g: Graph) -> list[str]`
  - `authored_texts(g: Graph) -> list[tuple[str, str]]` → `(location, text)` for summary, completion items, change notes (annotation text is excluded: it is a transcription, gated by review)

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_schema.py
from pathlib import Path
import textwrap
import pytest
from guide.schema import load_graph, validate, topo_order, authored_texts, SchemaError

def write(d: Path, name: str, body: str):
    (d / name).write_text(textwrap.dedent(body))

@pytest.fixture
def gdir(tmp_path):
    write(tmp_path, "components.yaml", """
        - {id: canard.core, label: Canard foam core, fidelity: unvalidated}
        - {id: canard.spar_cap_bottom, label: Bottom spar cap, fidelity: no-geometry}
    """)
    write(tmp_path, "pages.yaml", """
        58: "10-5"
        59: "10-6"
    """)
    write(tmp_path, "annotations.yaml", """
        - {scan_pp: 58, cp: 25, lpc: 16, class: MEO, text: "WL 19.4 not centerline", confirmed: true}
    """)
    write(tmp_path, "ch10.yaml", """
        - id: c03.layup-skills
          chapter: 3
          title: Composite layup skills
          stub: true
        - id: c10.cores
          chapter: 10
          title: Cut the foam cores
          summary: Hot-wire the four canard cores from the templates.
          variants: [gu]
          requires: [c03.layup-skills]
          components: [canard.core]
          geometry_visible: true
          sources: [{doc: scan-1980, scan_pp: 58}]
          changes:
            - {cp: 25, lpc: 16, class: MEO, status: verified, kind: official, note: Shear web line moves to WL 19.4., annotation_pp: 58}
          completion: [Four cores cut and labeled]
        - id: c10.twist-check
          chapter: 10
          title: Check for twist
          summary: Level the jigged cores and confirm zero twist before skinning.
          variants: [gu]
          requires: [c10.cores]
          components: []
          geometry_visible: false
          inspection: true
          sources: [{doc: scan-1980, scan_pp: 59}]
          completion: [Incidence matches at both ends]
    """)
    return tmp_path

def test_valid_graph_has_no_errors(gdir):
    g = load_graph(gdir)
    assert validate(g) == []
    assert topo_order(g) == ["c03.layup-skills", "c10.cores", "c10.twist-check"]

def test_unknown_requires_and_component(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("requires: [c10.cores]", "requires: [c10.nope]").replace("components: [canard.core]", "components: [canard.ghost]"))
    errs = validate(load_graph(gdir))
    assert any("c10.twist-check" in e and "c10.nope" in e for e in errs)
    assert any("canard.ghost" in e for e in errs)

def test_cycle_detected(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("requires: [c03.layup-skills]", "requires: [c10.twist-check]"))
    assert any("cycle" in e for e in validate(load_graph(gdir)))

def test_duplicate_id_raises(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text() + "\n- {id: c10.cores, chapter: 10, title: dup, stub: true}\n")
    with pytest.raises(SchemaError, match="duplicate"):
        load_graph(gdir)

def test_scan_page_must_be_mapped(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("scan_pp: 59", "scan_pp: 99"))
    assert any("scan_pp 99" in e for e in validate(load_graph(gdir)))

def test_confirmed_annotation_must_be_linked(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("lpc: 16, class: MEO, status: verified", "lpc: 99, class: MEO, status: verified"))
    assert any("annotation" in e and "LPC 16" in e for e in validate(load_graph(gdir)))

def test_bad_enums(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("variants: [gu]\n  requires: [c03", "variants: [vari]\n  requires: [c03").replace("status: verified", "status: maybe"))
    errs = validate(load_graph(gdir))
    assert any("vari" in e for e in errs) and any("maybe" in e for e in errs)

def test_non_stub_needs_summary_source_completion(gdir):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("completion: [Four cores cut and labeled]", "completion: []"))
    assert any("c10.cores" in e and "completion" in e for e in validate(load_graph(gdir)))

def test_authored_texts_excludes_annotations(gdir):
    locs = [loc for loc, _ in authored_texts(load_graph(gdir))]
    assert "c10.cores.summary" in locs and "c10.cores.changes[0].note" in locs
    assert not any(loc.startswith("annotation") for loc in locs)
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/guide/test_schema.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'guide.schema'`

- [ ] **Step 3: Implement**

```python
# guide/schema.py
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


def _op(d: dict) -> Operation:
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
        sources=tuple(Source(**s) for s in d.get("sources", [])),
        changes=tuple(
            Change(cp=c["cp"], lpc=c["lpc"], cls=c["class"], status=c["status"], kind=c["kind"],
                   note=c.get("note", ""), annotation_pp=c.get("annotation_pp"))
            for c in d.get("changes", [])
        ),
        completion=tuple(d.get("completion", [])),
        inspection=bool(d.get("inspection", False)),
        stub=bool(d.get("stub", False)),
    )


def load_graph(graph_dir: Path) -> Graph:
    g = Graph()
    comp = graph_dir / "components.yaml"
    if comp.exists():
        for c in _read(comp):
            g.components[c["id"]] = Component(c["id"], c.get("label", c["id"]), c["fidelity"])
    pages = graph_dir / "pages.yaml"
    if pages.exists():
        g.pages = {int(k): str(v) for k, v in (_read(pages) or {}).items()}
    ann = graph_dir / "annotations.yaml"
    if ann.exists():
        g.annotations = [
            Annotation(a["scan_pp"], a["cp"], a["lpc"], a["class"], a.get("text", ""), bool(a.get("confirmed", False)))
            for a in _read(ann)
        ]
    for f in sorted(graph_dir.glob("*.yaml")):
        if f.name in RESERVED:
            continue
        for d in _read(f):
            op = _op(d)
            if op.id in g.ops:
                raise SchemaError(f"duplicate op id {op.id} in {f.name}")
            g.ops[op.id] = op
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
        if op.stub:
            continue
        for v in op.variants:
            if v not in VARIANTS:
                errs.append(f"{op.id}: bad variant {v}")
        for cid in op.components:
            if cid not in g.components:
                errs.append(f"{op.id}: unknown component {cid}")
        if not op.summary.strip():
            errs.append(f"{op.id}: summary required")
        if not op.sources:
            errs.append(f"{op.id}: at least one source required")
        if not op.completion:
            errs.append(f"{op.id}: completion checklist required")
        for s in op.sources:
            if s.scan_pp is not None and s.scan_pp not in g.pages:
                errs.append(f"{op.id}: scan_pp {s.scan_pp} not in pages.yaml")
        for ch in op.changes:
            if ch.status not in STATUS:
                errs.append(f"{op.id}: bad change status {ch.status}")
            if ch.kind not in KIND:
                errs.append(f"{op.id}: bad change kind {ch.kind}")
            if ch.status == "verified" and ch.kind == "official" and (ch.cp <= 0 or ch.lpc <= 0):
                errs.append(f"{op.id}: verified official change needs cp and lpc")
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
```

Note: in `test_valid_graph_has_no_errors` the topo order must be deterministic. `topo_order` sorts roots by `(chapter, id)`, so `c03.layup-skills` (chapter 3) comes first.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/guide/test_schema.py -q`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add guide/__init__.py guide/schema.py tests/guide/__init__.py tests/guide/test_schema.py
git commit -m "feat(guide): step-graph schema, loader and validator"
```

---

### Task 2: Canard Pusher plans-change parser

**Files:**
- Create: `guide/lpc.py`
- Test: `tests/guide/test_lpc.py`

**Interfaces:**
- Produces: `PlansChange(lpc: int, cls: str, page: str|None, chapter: int|None, cp: int, text: str)`; `parse_lpcs(text: str) -> list[PlansChange]`.
- `text` is held in memory only (never written to the repo).

- [ ] **Step 1: Write the failing tests** (synthetic fixture in the real format, no verbatim CP content)

```python
# tests/guide/test_lpc.py
from guide.lpc import parse_lpcs

FIXTURE = """Table of Contents

THE CANARD PUSHER NO. 24 APR  80
THE CANARD PUSHER NO. 25 JULY 80

THE CANARD PUSHER NO. 24 APR  80
some news text
LPC #3, MEO, Page 10-2.
Synthetic description one.

THE CANARD PUSHER NO. 25 JULY 80
LPC #7, MEO, Back cover of plans.
Synthetic description about a station value,
continued on a second line.

LPC #16, MEO, Page 10-5 Step 2.
Synthetic description two.
LPC #17, OPT, Page 12-1
"""

def test_parses_entries_with_issue_attribution():
    got = {c.lpc: c for c in parse_lpcs(FIXTURE)}
    assert set(got) == {3, 7, 16, 17}
    assert got[3].cp == 24 and got[16].cp == 25

def test_page_and_chapter():
    got = {c.lpc: c for c in parse_lpcs(FIXTURE)}
    assert (got[16].page, got[16].chapter) == ("10-5", 10)
    assert (got[17].page, got[17].chapter, got[17].cls) == ("12-1", 12, "OPT")

def test_no_page_entry_is_kept():  # Review Focus 4
    c = {c.lpc: c for c in parse_lpcs(FIXTURE)}[7]
    assert c.page == "back-cover" and c.chapter is None

def test_multiline_description_joined():  # Review Focus 4
    c = {c.lpc: c for c in parse_lpcs(FIXTURE)}[7]
    assert "continued on a second line" in c.text

def test_toc_headers_do_not_attribute():
    assert all(c.cp in (24, 25) for c in parse_lpcs(FIXTURE))
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/guide/test_lpc.py -q`
Expected: FAIL, `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# guide/lpc.py
"""Parse Long-EZ plans-change (LPC) entries out of sectioned Canard Pusher text.

Format observed in CPs_1_to_82_Sections.txt:  'LPC #7, MEO, Back cover of plans.'  followed by
description lines until a blank line or the next entry. Attribution = nearest preceding
'THE CANARD PUSHER NO. N' header.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

HEADER = re.compile(r"^\s*THE CANARD PUSHER\s+NO\.\s*(\d+)", re.I)
ENTRY = re.compile(r"^\s*LPC\s*#\s*(\d+)\s*,\s*([A-Z]{2,4})\s*,?\s*(.*)$")
PAGE = re.compile(r"Page\s+(\d{1,2})\s*[-–]\s*(\d{1,2})", re.I)


@dataclass(frozen=True)
class PlansChange:
    lpc: int
    cls: str
    page: str | None
    chapter: int | None
    cp: int
    text: str


def _page(ref: str) -> tuple[str | None, int | None]:
    m = PAGE.search(ref)
    if m:
        return f"{int(m.group(1))}-{int(m.group(2))}", int(m.group(1))
    if "back cover" in ref.lower():
        return "back-cover", None
    return None, None


def parse_lpcs(text: str) -> list[PlansChange]:
    out: list[PlansChange] = []
    cp = 0
    cur: dict | None = None

    def flush():
        if cur is not None and cp_of_cur is not None:
            page, chapter = _page(cur["ref"])
            out.append(PlansChange(cur["lpc"], cur["cls"], page, chapter, cp_of_cur, " ".join(cur["lines"]).strip()))

    cp_of_cur: int | None = None
    for line in text.splitlines():
        h = HEADER.match(line)
        e = ENTRY.match(line)
        if h or e or not line.strip():
            flush()
            cur, cp_of_cur = None, None
        if h:
            cp = int(h.group(1))
            continue
        if e:
            if cp == 0:
                continue
            cur = {"lpc": int(e.group(1)), "cls": e.group(2), "ref": e.group(3), "lines": []}
            cp_of_cur = cp
            continue
        if cur is not None and line.strip():
            cur["lines"].append(line.strip())
    flush()
    return out
```

Why TOC headers are harmless: all TOC lines come before the first body header, and an entry takes the *latest* header seen, which is always its own issue's body header.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m pytest tests/guide/test_lpc.py -q`
Expected: 5 passed

- [ ] **Step 5: Sanity-check against the real corpus (no output committed)**

Run: `.venv/bin/python -c "from guide.lpc import parse_lpcs; import os; cs=parse_lpcs(open(os.environ['LONGEZ_CP_SECTIONS']).read()); print(len(cs)); print([ (c.cp,c.lpc,c.page) for c in cs if c.lpc in (7,16)])"` after `source ~/.config/long-ez/env`
Expected: a count in the low hundreds (grep found 154 "LPC" lines), and LPC 7 attributed to CP 25 with page `back-cover`, matching the prior owner's "CP#25 LCP#7" note. If LPC 7 is not CP 25, STOP and report the mismatch.

- [ ] **Step 6: Commit**

```bash
git add guide/lpc.py tests/guide/test_lpc.py
git commit -m "feat(guide): parse Canard Pusher plans-change entries"
```

---

### Task 3: cobelu inline change-marker parser

**Files:**
- Create: `guide/cobelu_markers.py`
- Test: `tests/guide/test_cobelu_markers.py`

**Interfaces:**
- Produces: `Marker(cp: int, lpc: int, cls: str, chapter: int, heading: str, line: int)`; `parse_markers(md_text: str, chapter: int) -> list[Marker]`; `chapter_from_filename(name: str) -> int|None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_cobelu_markers.py
from guide.cobelu_markers import parse_markers, chapter_from_filename

MD = """# CHAPTER 10
### STEP 1 -
Place one {CP27 PC44 MEO} of your blocks.
### STEP 2 -
Mark a WL line {CP25 PC16 MEO} and also {CP 26 LPC 36 DES}.
"""

def test_markers_with_heading_context():
    ms = parse_markers(MD, 10)
    assert [(m.cp, m.lpc, m.cls, m.heading) for m in ms] == [
        (27, 44, "MEO", "STEP 1 -"), (25, 16, "MEO", "STEP 2 -"), (26, 36, "DES", "STEP 2 -")]
    assert ms[0].line == 3 and all(m.chapter == 10 for m in ms)

def test_chapter_from_filename():
    assert chapter_from_filename("10_CANARD CONSTRUCTION.md") == 10
    assert chapter_from_filename("30_R1149MS CANARD CONSTRUCTION.md") == 30
    assert chapter_from_filename("total materials tables.md") is None
```

- [ ] **Step 2: Run to confirm failure**: `.venv/bin/python -m pytest tests/guide/test_cobelu_markers.py -q` → FAIL `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# guide/cobelu_markers.py
"""Parse cobelu/Long-EZ inline change markers like '{CP27 PC44 MEO}' with their step heading."""
from __future__ import annotations

import re
from dataclasses import dataclass

MARK = re.compile(r"\{\s*CP\s*(\d+)\s+L?PC\s*(\d+)\s+([A-Z]{2,4})\s*\}")
HEAD = re.compile(r"^#{2,3}\s+(.*\S)\s*$")
FNAME = re.compile(r"^(\d{1,2})[_-]")


@dataclass(frozen=True)
class Marker:
    cp: int
    lpc: int
    cls: str
    chapter: int
    heading: str
    line: int


def chapter_from_filename(name: str) -> int | None:
    m = FNAME.match(name)
    return int(m.group(1)) if m else None


def parse_markers(md_text: str, chapter: int) -> list[Marker]:
    out: list[Marker] = []
    heading = ""
    for i, line in enumerate(md_text.splitlines(), start=1):
        h = HEAD.match(line)
        if h:
            heading = h.group(1)
            continue
        for m in MARK.finditer(line):
            out.append(Marker(int(m.group(1)), int(m.group(2)), m.group(3), chapter, heading, i))
    return out
```

- [ ] **Step 4: Run tests**: expected 2 passed
- [ ] **Step 5: Commit**: `git add guide/cobelu_markers.py tests/guide/test_cobelu_markers.py && git commit -m "feat(guide): parse cobelu inline change markers"`

---

### Task 4: Verbatim-overlap gate

**Files:**
- Create: `guide/overlap.py`
- Test: `tests/guide/test_overlap.py`

**Interfaces:**
- Produces: `shingles(text: str, n: int = 8) -> set[tuple[str, ...]]`; `class SourceIndex(texts: Iterable[str], n: int = 8)` with `.hits(text: str) -> list[str]` (each hit = the shared n-gram joined by spaces).

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_overlap.py
from guide.overlap import SourceIndex, shingles

SRC = ["Place one of your seven by fourteen foam blocks on the table and trim it square."]

def test_verbatim_run_is_caught():
    idx = SourceIndex(SRC)
    assert idx.hits("First, place one of your seven by fourteen foam blocks on the bench.")

def test_paraphrase_passes():
    idx = SourceIndex(SRC)
    assert idx.hits("Set a 7x14 block on the bench and square it with the trim templates.") == []

def test_normalization_ignores_case_and_punctuation():
    idx = SourceIndex(SRC)
    assert idx.hits('PLACE ONE, of your "seven" by fourteen foam blocks!')

def test_short_text_has_no_shingles():
    assert shingles("too short to match", 8) == set()
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/overlap.py
"""8-word shingle overlap gate: authored text must not share a verbatim run with plans/CP sources."""
from __future__ import annotations

import re
from typing import Iterable

WORD = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int = 8) -> set[tuple[str, ...]]:
    w = WORD.findall(text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


class SourceIndex:
    def __init__(self, texts: Iterable[str], n: int = 8):
        self.n = n
        self._set: set[tuple[str, ...]] = set()
        for t in texts:
            self._set |= shingles(t, n)

    def hits(self, text: str) -> list[str]:
        return sorted(" ".join(s) for s in shingles(text, self.n) & self._set)
```

- [ ] **Step 4: Run tests**: expected 4 passed
- [ ] **Step 5: Commit**: `git add guide/overlap.py tests/guide/test_overlap.py && git commit -m "feat(guide): verbatim-overlap gate"`

---

### Task 5: Change linker + recall

**Files:**
- Create: `guide/linker.py`
- Test: `tests/guide/test_linker.py`

**Interfaces:**
- Consumes: `Graph, Operation` (Task 1), `PlansChange` (Task 2), `Marker` (Task 3).
- Produces: `Candidate(op_id: str, cp: int, lpc: int, cls: str, origin: str)` (origin `lpc|marker`); `op_pages(op, g) -> set[str]`; `candidates(g, lpcs, markers) -> list[Candidate]`; `recall(g, cands, chapters: set[int]) -> tuple[list[Annotation], list[Annotation]]` → `(hits, misses)` over **confirmed** annotations whose `pages[scan_pp]` chapter is in `chapters`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_linker.py
from guide.schema import Graph, Operation, Source, Annotation
from guide.lpc import PlansChange
from guide.cobelu_markers import Marker
from guide.linker import candidates, recall, op_pages

def graph():
    g = Graph()
    g.pages = {58: "10-5", 171: "back-cover", 71: "12-1"}
    g.ops["c10.cores"] = Operation(id="c10.cores", chapter=10, title="t", summary="s",
        sources=(Source(doc="scan-1980", scan_pp=58), Source(doc="cobelu", heading="STEP 2 -")), completion=("x",))
    g.ops["c12.pins"] = Operation(id="c12.pins", chapter=12, title="t", summary="s",
        sources=(Source(doc="scan-1980", page="12-1"),), completion=("x",))
    g.annotations = [Annotation(58, 25, 16, "MEO", "t", True), Annotation(71, 26, 40, "MEO", "t", True),
                     Annotation(171, 25, 7, "MEO", "t", True), Annotation(58, 30, 1, "MEO", "t", False)]
    return g

LPCS = [PlansChange(16, "MEO", "10-5", 10, 25, ""), PlansChange(7, "MEO", "back-cover", None, 25, ""),
        PlansChange(99, "MEO", "10-9", 10, 27, "")]
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
    assert [(a.cp, a.lpc) for a in misses] == [(26, 40)]  # back-cover and unconfirmed excluded
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/linker.py
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
```

- [ ] **Step 4: Run tests**: expected 3 passed
- [ ] **Step 5: Commit**: `git add guide/linker.py tests/guide/test_linker.py && git commit -m "feat(guide): change linker with annotation recall"`

---

### Task 6: `guide.check` CLI

**Files:**
- Create: `guide/check.py`, `guide/sources.py`
- Test: `tests/guide/test_check.py`

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces:
  - `guide/sources.py`: `source_paths() -> dict[str, Path|None]` (reads the three env vars); `load_source_texts(paths) -> list[str]` (CP sections text; every `*.md` under `$LONGEZ_COBELU_DIR/I/md`; every `*.txt` under `$LONGEZ_SCAN_TEXT_DIR`); `load_markers(cobelu_dir) -> list[Marker]`
  - `guide/check.py`: `main(argv: list[str] | None = None) -> int`. Flags: `--graph PATH` (default `guide/graph`), `--schema-only`, `--chapters 10,12`. Exit 0 ok · 1 failures · 2 sources missing in full mode.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_check.py
import shutil
from pathlib import Path
from guide.check import main
from tests.guide.test_schema import gdir  # noqa: F401  (reuse fixture)

def src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nx\n"):
    cp = tmp_path / "cp.txt"; cp.write_text(cp_text)
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))

def test_schema_only_passes(gdir):
    assert main(["--graph", str(gdir), "--schema-only"]) == 0

def test_full_mode_missing_sources_exits_2(gdir, monkeypatch):
    for v in ("LONGEZ_CP_SECTIONS", "LONGEZ_COBELU_DIR", "LONGEZ_SCAN_TEXT_DIR"):
        monkeypatch.delenv(v, raising=False)
    assert main(["--graph", str(gdir)]) == 2

def test_full_mode_green(gdir, tmp_path, monkeypatch):
    src_env(tmp_path, monkeypatch)
    assert main(["--graph", str(gdir)]) == 0

def test_overlap_fails(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nhot wire the four canard cores from the templates today\n")
    assert main(["--graph", str(gdir)]) == 1
    assert "c10.cores.summary" in capsys.readouterr().out

def test_recall_miss_fails(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\n")
    assert main(["--graph", str(gdir)]) == 1
    assert "recall" in capsys.readouterr().out.lower()
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/sources.py
"""Locate private source corpora (never in git) via env vars."""
from __future__ import annotations

import os
from pathlib import Path

from guide.cobelu_markers import Marker, chapter_from_filename, parse_markers

ENV = {"cp": "LONGEZ_CP_SECTIONS", "cobelu": "LONGEZ_COBELU_DIR", "scan_text": "LONGEZ_SCAN_TEXT_DIR"}


def source_paths() -> dict[str, Path | None]:
    out: dict[str, Path | None] = {}
    for k, var in ENV.items():
        v = os.environ.get(var)
        p = Path(v).expanduser() if v else None
        out[k] = p if p and p.exists() else None
    return out


def _cobelu_md(cobelu: Path) -> list[Path]:
    return sorted((cobelu / "I" / "md").glob("*.md"))


def load_source_texts(paths: dict[str, Path]) -> list[str]:
    texts = [paths["cp"].read_text(errors="ignore")]
    texts += [p.read_text(errors="ignore") for p in _cobelu_md(paths["cobelu"])]
    texts += [p.read_text(errors="ignore") for p in sorted(paths["scan_text"].glob("*.txt"))]
    return texts


def load_markers(cobelu: Path) -> list[Marker]:
    out: list[Marker] = []
    for p in _cobelu_md(cobelu):
        ch = chapter_from_filename(p.name)
        if ch is not None:
            out += parse_markers(p.read_text(errors="ignore"), ch)
    return out
```

```python
# guide/check.py
"""python -m guide.check — schema + verbatim-overlap gate + annotation recall. Full mode is the pre-commit gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from guide.linker import candidates, recall
from guide.lpc import parse_lpcs
from guide.overlap import SourceIndex
from guide.schema import SchemaError, authored_texts, load_graph, validate
from guide.sources import ENV, load_markers, load_source_texts, source_paths


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.check")
    ap.add_argument("--graph", default="guide/graph")
    ap.add_argument("--schema-only", action="store_true")
    ap.add_argument("--chapters", default="10,12")
    a = ap.parse_args(argv)

    try:
        g = load_graph(Path(a.graph))
    except SchemaError as e:
        print(f"SCHEMA: {e}")
        return 1
    fails = [f"SCHEMA: {e}" for e in validate(g)]

    if a.schema_only:
        print("OVERLAP GATE NOT RUN (--schema-only)")
    else:
        paths = source_paths()
        missing = [ENV[k] for k, p in paths.items() if p is None]
        if missing:
            print(f"SOURCES MISSING: {', '.join(missing)} — full-mode gate cannot run")
            return 2
        idx = SourceIndex(load_source_texts(paths))
        for loc, text in authored_texts(g):
            for h in idx.hits(text):
                fails.append(f"OVERLAP: {loc}: '{h}'")
        cands = candidates(g, parse_lpcs(paths["cp"].read_text(errors="ignore")), load_markers(paths["cobelu"]))
        hits, misses = recall(g, cands, {int(c) for c in a.chapters.split(",")})
        print(f"RECALL: {len(hits)}/{len(hits) + len(misses)} confirmed annotations recovered")
        fails += [f"RECALL MISS: scan_pp {m.scan_pp} CP {m.cp} LPC {m.lpc}" for m in misses]

    for f in fails:
        print(f)
    print("OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**: `.venv/bin/python -m pytest tests/guide/test_check.py -q` → 5 passed
- [ ] **Step 5: Commit**: `git add guide/check.py guide/sources.py tests/guide/test_check.py && git commit -m "feat(guide): check CLI with overlap and recall gates"`

---

### Task 7: glTF export with component-ID node names

**Files:**
- Create: `guide/export_glb.py`
- Test: `tests/guide/test_export_glb.py`

**Interfaces:**
- Produces: `export_components(components: dict[str, cq.Workplane], out: Path) -> Path`; `default_components() -> dict[str, cq.Workplane]` (M1: `{"canard.core": CanardGenerator().generate_geometry()}`); `read_glb_node_names(path: Path) -> list[str]`; CLI `python -m guide.export_glb --out output/guide/longez.glb`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_export_glb.py
import cadquery as cq
from guide.export_glb import export_components, read_glb_node_names

def test_node_names_are_component_ids(tmp_path):
    out = export_components({"canard.core": cq.Workplane().box(10, 2, 1),
                             "canard.spar_cap_top": cq.Workplane().box(10, 1, 0.1)}, tmp_path / "t.glb")
    names = read_glb_node_names(out)
    assert "canard.core" in names and "canard.spar_cap_top" in names
    assert out.read_bytes()[:4] == b"glTF"
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/export_glb.py
"""Export open-ez components to a single .glb whose node names are guide component IDs."""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import cadquery as cq


def export_components(components: dict[str, cq.Workplane], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    assy = cq.Assembly(name="longez")
    for cid, wp in components.items():
        assy.add(wp, name=cid)
    assy.save(str(out), exportType="GLTF")
    return out


def read_glb_node_names(path: Path) -> list[str]:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError(f"{path}: not a binary glTF")
    chunk_len, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:  # 'JSON'
        raise ValueError(f"{path}: first chunk is not JSON")
    doc = json.loads(data[20:20 + chunk_len])
    return [n.get("name", "") for n in doc.get("nodes", [])]


def default_components() -> dict[str, cq.Workplane]:
    from core.structures import CanardGenerator

    return {"canard.core": CanardGenerator().generate_geometry()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.export_glb")
    ap.add_argument("--out", default="output/guide/longez.glb")
    a = ap.parse_args(argv)
    out = export_components(default_components(), Path(a.out))
    print(f"wrote {out} nodes={read_glb_node_names(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

If the test fails because OCCT writes names that differ from the assembly child names (e.g. suffixed), STOP and report BLOCKED with the actual `read_glb_node_names` output. Do not add a fuzzy matcher.

- [ ] **Step 4: Run tests and the real export**

Run: `.venv/bin/python -m pytest tests/guide/test_export_glb.py -q && .venv/bin/python -m guide.export_glb`
Expected: 1 passed; `wrote output/guide/longez.glb nodes=[... 'canard.core' ...]`

- [ ] **Step 5: Commit**: `git add guide/export_glb.py tests/guide/test_export_glb.py && git commit -m "feat(guide): glb export keyed by component id"`

---

### Task 8: Scan ingest (private outputs) + page map

**Files:**
- Create: `guide/scan_ingest.py`
- Test: `tests/guide/test_scan_ingest.py`

**Interfaces:**
- Produces: `parse_page_ref(text: str) -> str|None`; `render_pages(pdf: Path, out_dir: Path, dpi: int = 150) -> int`; `ocr_pages(pages_dir: Path, text_dir: Path) -> int`; `propose_page_map(pdf: Path) -> dict[int, str|None]`; CLI `python -m guide.scan_ingest PDF --out ~/.cache/long-ez/scan-1980` → `pages/NNN.jpg`, `text/NNN.txt`, `page_map.proposed.yaml` (all outside the repo).

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_scan_ingest.py
import fitz
import pytest
from guide.scan_ingest import parse_page_ref, render_pages

@pytest.mark.parametrize("raw,want", [
    ("PAGE 6-3", "6-3"), ("Pg 10 – 5", "10-5"), ("pg. 12-1", "12-1"),   # Review Focus 5
    ("P6 11-3", "11-3"), ("PAGE  3 -16", "3-16"), ("no ref here", None)])
def test_parse_page_ref(raw, want):
    assert parse_page_ref(raw) == want

def test_render_pages_zero_padded(tmp_path):
    pdf = tmp_path / "t.pdf"
    doc = fitz.open(); [doc.new_page() for _ in range(2)]; doc.save(pdf)
    assert render_pages(pdf, tmp_path / "pages", dpi=30) == 2
    assert sorted(p.name for p in (tmp_path / "pages").iterdir()) == ["001.jpg", "002.jpg"]
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/scan_ingest.py
"""Render the owner's plans scan to private page images + OCR text + a proposed page map.
All outputs go OUTSIDE the repo (default ~/.cache/long-ez/scan-1980). Never commit them."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
import yaml

REF = re.compile(r"(?:PAGE|PG|P6)\s*\.?\s*(\d{1,2})\s*[-–—]\s*(\d{1,2})", re.I)


def parse_page_ref(text: str) -> str | None:
    m = REF.search(text)
    return f"{int(m.group(1))}-{int(m.group(2))}" if m else None


def render_pages(pdf: Path, out_dir: Path, dpi: int = 150) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(dpi=dpi).save(out_dir / f"{i:03d}.jpg", jpg_quality=80)
    return len(doc)


def _ocr(img: Path) -> str:
    return subprocess.run(["tesseract", str(img), "-", "--psm", "6"], capture_output=True, text=True, check=True).stdout


def ocr_pages(pages_dir: Path, text_dir: Path) -> int:
    text_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for img in sorted(pages_dir.glob("*.jpg")):
        (text_dir / f"{img.stem}.txt").write_text(_ocr(img))
        n += 1
    return n


def propose_page_map(pdf: Path) -> dict[int, str | None]:
    doc = fitz.open(pdf)
    out: dict[int, str | None] = {}
    tmp = Path(tempfile.mkdtemp()) / "strip.png"
    for i, page in enumerate(doc, start=1):
        r = page.rect
        ref = None
        for clip in (fitz.Rect(0, r.height * 0.86, r.width, r.height), fitz.Rect(0, 0, r.width, r.height * 0.10)):
            page.get_pixmap(dpi=150, clip=clip).save(tmp)
            ref = parse_page_ref(_ocr(tmp))
            if ref:
                break
        out[i] = ref
    tmp.unlink(missing_ok=True)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.scan_ingest")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, default=Path("~/.cache/long-ez/scan-1980").expanduser())
    a = ap.parse_args(argv)
    n = render_pages(a.pdf, a.out / "pages")
    ocr_pages(a.out / "pages", a.out / "text")
    (a.out / "page_map.proposed.yaml").write_text(yaml.safe_dump(propose_page_map(a.pdf)))
    print(f"rendered {n} pages -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**: expected 7 passed
- [ ] **Step 5: Run on the real scan and publish privately**

```bash
.venv/bin/python -m guide.scan_ingest "$LONGEZ_SCAN_PDF"     # owner's scan path, set in the shell, never committed
ssh "$LONGEZ_DEPLOY_HOST" 'mkdir -p <host private dir>/private/scan-1980/pages'
rsync -a ~/.cache/long-ez/scan-1980/pages/ "$LONGEZ_DEPLOY_HOST":<host private dir>/private/scan-1980/pages/
git clone --depth 1 https://github.com/cobelu/Long-EZ ~/.cache/long-ez/cobelu
```

Expected: 171 pages rendered; `ls ~/.cache/long-ez/scan-1980/text | wc -l` = 171; `git status` shows **no** new files under the repo from this step.

- [ ] **Step 6: Commit** (code only): `git add guide/scan_ingest.py tests/guide/test_scan_ingest.py && git commit -m "feat(guide): private scan ingest and page-map proposal"`

---

### Task 9: Author the canard slice content (session + owner; not delegable to a code worker)

**Files:**
- Create: `guide/graph/components.yaml`, `guide/graph/pages.yaml`, `guide/graph/annotations.yaml`, `guide/graph/ch10.yaml`, `guide/graph/ch12.yaml`, `guide/graph/ch30.yaml`

**Interfaces:** Consumes the Task 1 schema; content must pass `python -m guide.check` in full mode.

**Operation list** (ids fixed now; titles are ours):

| id | variant | groups | notes |
|---|---|---|---|
| `c03.layup-skills` | stub | ch 3 | prerequisite outside slice |
| `c06.fuselage-assembled` | stub | ch 6 | prerequisite for ch 12 |
| `c10.templates-cores` | gu | ch10 STEP 1 | carries `{CP27 PC44 MEO}` |
| `c10.shear-web` | gu | ch10 STEP 2 | carries `{CP25 PC16 MEO}` |
| `c10.bottom-spar-skin` | gu | ch10 STEP 3 | |
| `c10.flag-spar-cap` | gu | ch10 STEP 4 | |
| `c10.top-spar-skin` | gu | ch10 STEP 5 | |
| `r30.templates-cores` | roncz | ch30 Steps 1–6 | |
| `r30.shear-web` | roncz | ch30 Steps 7, 9, 14 | |
| `r30.lift-tabs` | roncz | ch30 Steps 8, 10–13, 15 | |
| `r30.jig-assemble` | roncz | ch30 Steps 16–20 | |
| `r30.bottom-spar-cap` | roncz | ch30 Steps 21–22 | |
| `r30.bottom-skin` | roncz | ch30 Step 23 | |
| `r30.turnover-twist-check` | roncz | ch30 Steps 24–25 | `geometry_visible: false`, `inspection: true` |
| `r30.hinge-foam` | roncz | ch30 Step 26 | |
| `r30.top-spar-cap` | roncz | ch30 Step 27 | |
| `r30.top-skin` | roncz | ch30 Step 28 | |
| `c12.alignment-pins` | both | ch12 STEP 1 | requires `c06.fuselage-assembled` + either canard |
| `c12.align-canard` | both | ch12 STEP 2 | `inspection: true` |

Components: `canard.core` (`unvalidated`, the only one with geometry); `canard.shear_web`, `canard.spar_cap_bottom`, `canard.spar_cap_top`, `canard.skin_bottom`, `canard.skin_top`, `canard.lift_tabs`, `canard.hinge_foam`, `canard.alignment_pins` (all `no-geometry`).

Because `requires` is AND-only, `c12.alignment-pins` lists `c06.fuselage-assembled` and `r30.top-skin` (the default variant). The GU path is noted in its summary. Variant-OR requires are deferred to C.

- [ ] **Step 1: Confirm the page map for slice pages.** Open `~/.cache/long-ez/scan-1980/page_map.proposed.yaml` and view each scan page 50–75 and 171 image. Write only **confirmed** `scan_pp: "chapter-page"` entries into `guide/graph/pages.yaml`, plus `171: back-cover`.
- [ ] **Step 2: Transcribe annotations** on scan pp 50–75 and 171 (session vision on the page images). For each handwritten note write `{scan_pp, cp, lpc, class, text: <≤15-word factual gist>, confirmed: false}` into `annotations.yaml`. **The owner reviews each entry** against the page image and flips it to `confirmed: true`. Nothing is confirmed by the agent alone.
- [ ] **Step 3: Draft op text via the local-model lane.** For each non-stub op, send the local-model local-model lane lane (fabric scheduler, model `local-model lane`) the relevant cobelu section plus scan OCR text. Instruction: "Write a 1–3 sentence summary and 2–5 checklist items IN YOUR OWN WORDS; do not copy any phrase of 5+ words; do not invent dimensions or ply counts. Copy numbers only if they appear in the source." Log the wave (`lane=local-model-local`).
- [ ] **Step 4: Session edit.** Fix accuracy against the scan page, add `sources` (`scan-1980` scan_pp for ch 10/12; `cobelu` with `heading` and `figure: I/images/<ch>/<file>.png` for ch 30), `materials` only where a source states them, and `changes` for every confirmed annotation (`status: verified` only after reading the matching CP entry in `CPs_1_to_82_Sections.txt`, otherwise `unresolved`).
- [ ] **Step 5: Run the full gate**

```bash
source ~/.config/long-ez/env   # local-only file holding source paths + deploy target
.venv/bin/python -m guide.check
```

Expected: `RECALL: N/N confirmed annotations recovered` and `OK`. On OVERLAP, rewrite the flagged text. On RECALL MISS, either the op is missing a source page or the annotation is misread; fix it, never delete the annotation.

- [ ] **Step 6: Commit** (content, gate green): `git add guide/graph && git commit -m "content(guide): canard slice ops, page map and annotations"`

---

### Task 10: Viewer logic (pure JS)

**Files:**
- Create: `guide/viewer/js/graph.js`
- Test: `guide/viewer/tests/graph.test.mjs`

**Interfaces:**
- Consumes: `graph.json` shape written by Task 12: `{ops: Op[], order: string[], components: {[id]: {label, fidelity}}, pages: {[scan_pp]: string}, annotations: Annotation[]}` where `Op` mirrors Task 1 field names in snake_case (`geometry_visible`, `scan_pp`, `class`).
- Produces (ES module exports): `visibleOps(graph, variant) -> Op[]` (topo order, stubs always kept, variant match or `both`); `opsForComponent(graph, cid) -> string[]`; `badge(graph, cid) -> string`; `scanView(source, cfg) -> {kind: 'scan'|'figure'|'none', url: string|null}`; `makeStore(storage) -> {get(opId): Set<number>, toggle(opId, i): void}` (in-memory fallback when storage throws).

- [ ] **Step 1: Write the failing tests**

```js
// guide/viewer/tests/graph.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { visibleOps, opsForComponent, badge, scanView, makeStore } from "../js/graph.js";

const G = {
  order: ["s", "a", "b", "c"],
  ops: [
    { id: "a", variants: ["gu"], components: ["canard.core"], stub: false },
    { id: "b", variants: ["roncz"], components: ["canard.core", "canard.skin_top"], stub: false },
    { id: "c", variants: ["both"], components: [], stub: false },
    { id: "s", variants: ["both"], components: [], stub: true },
  ],
  components: { "canard.core": { label: "Core", fidelity: "unvalidated" } },
};

test("visibleOps filters by variant and keeps order + stubs", () => {
  assert.deepEqual(visibleOps(G, "roncz").map(o => o.id), ["s", "b", "c"]);
  assert.deepEqual(visibleOps(G, "gu").map(o => o.id), ["s", "a", "c"]);
});

test("opsForComponent", () => {
  assert.deepEqual(opsForComponent(G, "canard.core"), ["a", "b"]);
});

test("badge falls back to no-geometry", () => {
  assert.equal(badge(G, "canard.core"), "unvalidated");
  assert.equal(badge(G, "canard.skin_top"), "no-geometry");
});

test("scanView: private scan, figure fallback, none", () => {  // Review Focus 1
  const cfg = { scanBase: "/private/scan-1980/pages/" };
  assert.deepEqual(scanView({ scan_pp: 58 }, cfg), { kind: "scan", url: "/private/scan-1980/pages/058.jpg" });
  assert.deepEqual(scanView({ scan_pp: 58, figure: "I/images/10/10_02.png" }, { scanBase: null }),
    { kind: "figure", url: "https://raw.githubusercontent.com/cobelu/Long-EZ/master/I/images/10/10_02.png" });
  assert.deepEqual(scanView({ scan_pp: 58 }, { scanBase: null }), { kind: "none", url: null });
});

test("makeStore survives a throwing storage", () => {  // Review Focus 2
  const bad = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };
  const s = makeStore(bad);
  s.toggle("a", 1);
  assert.deepEqual([...s.get("a")], [1]);
});
```

- [ ] **Step 2: Run to confirm failure**: `node --test guide/viewer/tests/*.test.mjs` → FAIL (module not found)
- [ ] **Step 3: Implement**

```js
// guide/viewer/js/graph.js — pure logic, no DOM, no three.js.
const COBELU_RAW = "https://raw.githubusercontent.com/cobelu/Long-EZ/master/";

export function visibleOps(graph, variant) {
  const byId = new Map(graph.ops.map(o => [o.id, o]));
  return graph.order.map(id => byId.get(id)).filter(o =>
    o && (o.stub || o.variants.includes("both") || o.variants.includes(variant)));
}

export function opsForComponent(graph, cid) {
  return graph.ops.filter(o => o.components.includes(cid)).map(o => o.id);
}

export function badge(graph, cid) {
  return graph.components[cid]?.fidelity ?? "no-geometry";
}

export function scanView(source, cfg) {
  if (source.scan_pp != null && cfg.scanBase) {
    return { kind: "scan", url: `${cfg.scanBase}${String(source.scan_pp).padStart(3, "0")}.jpg` };
  }
  if (source.figure) return { kind: "figure", url: COBELU_RAW + source.figure };
  return { kind: "none", url: null };
}

export function makeStore(storage) {
  const mem = new Map();
  const key = id => `longez.check.${id}`;
  return {
    get(opId) {
      if (!mem.has(opId)) {
        let v = [];
        try { v = JSON.parse(storage.getItem(key(opId)) || "[]"); } catch { /* storage blocked */ }
        mem.set(opId, new Set(v));
      }
      return mem.get(opId);
    },
    toggle(opId, i) {
      const s = this.get(opId);
      s.has(i) ? s.delete(i) : s.add(i);
      try { storage.setItem(key(opId), JSON.stringify([...s])); } catch { /* keep in memory */ }
    },
  };
}
```

- [ ] **Step 4: Run tests**: `node --test guide/viewer/tests/*.test.mjs` → 5 pass
- [ ] **Step 5: Commit**: `git add guide/viewer/js/graph.js guide/viewer/tests && git commit -m "feat(guide): viewer graph logic"`

---

### Task 11: Viewer UI + e2e

**Files:**
- Create: `scripts/vendor_three.sh`, `guide/viewer/index.html`, `guide/viewer/css/app.css`, `guide/viewer/js/app.js`, `guide/viewer/vendor/three/**` (vendored)
- Test: `tests/guide/test_viewer_e2e.py`

**Order note:** this task's e2e test imports `guide.build_site`, so run Task 12 Steps 1–4 before Step 2 here.

**Interfaces:**
- Consumes: `graph.js` (Task 10); `site/graph.json`, `site/config.json` (`{"scanBase": string|null, "model": "models/longez.glb"}`), `site/models/longez.glb` from Task 12's `build()`.
- Produces DOM contract used by the e2e test: `#ops li[data-op]`, `li.selected`, `#variant` (`<select>` with `roncz`/`gu`), `#parts .chip[data-cid]` with `data-badge`, `#source img` or `#source .none`, `#checklist input[type=checkbox]`, `#model-status` (text `3D unavailable` on load failure), `window.__guide.selectComponent(cid)` (test hook, the same path a canvas raycast hit calls).

- [ ] **Step 1: Vendor three.js**

```bash
# scripts/vendor_three.sh
#!/usr/bin/env bash
set -euo pipefail
V="${1:-$(npm view three version)}"
D="$(cd "$(dirname "$0")/.." && pwd)/guide/viewer/vendor/three"
rm -rf "$D"; mkdir -p "$D/build" "$D/examples/jsm/controls" "$D/examples/jsm/loaders" "$D/examples/jsm/utils"
base="https://unpkg.com/three@$V"
for f in build/three.module.min.js build/three.core.min.js examples/jsm/controls/OrbitControls.js \
         examples/jsm/loaders/GLTFLoader.js examples/jsm/utils/BufferGeometryUtils.js; do
  curl -fsSL "$base/$f" -o "$D/$f" || { [ "$f" = build/three.core.min.js ] && continue; exit 1; }
done
printf 'three %s vendored %s from unpkg\n' "$V" "$(date +%F)" > "$D/VERSION"
echo "vendored three $V"
```

Run: `bash scripts/vendor_three.sh && cat guide/viewer/vendor/three/VERSION`
Expected: `three <version> vendored <today>`. (`three.core.min.js` exists only on newer builds; it is optional.)

- [ ] **Step 2: Write the failing e2e test**

```python
# tests/guide/test_viewer_e2e.py
import functools, http.server, json, shutil, threading
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from guide.build_site import build
from tests.guide.test_schema import gdir  # noqa: F401

@pytest.fixture
def site(tmp_path, gdir):
    import cadquery as cq
    from guide.export_glb import export_components
    glb = export_components({"canard.core": cq.Workplane().box(10, 2, 1)}, tmp_path / "m.glb")
    out = tmp_path / "site"
    build(gdir, out, models=glb, scan_base=None, docs=None)
    return out

def serve(root: Path):
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}/"

def open_page(p, url, width=1280, init=None):
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": width, "height": 900})
    if init:
        pg.add_init_script(init)
    pg.goto(url); pg.wait_for_selector("#ops li[data-op]")
    return b, pg

def test_variant_and_bidirectional_selection(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "gu")
        ids = pg.eval_on_selector_all("#ops li[data-op]", "els => els.map(e => e.dataset.op)")
        assert "c10.cores" in ids
        pg.click('#ops li[data-op="c10.cores"]')
        assert pg.get_attribute('#parts .chip[data-cid="canard.core"]', "data-badge") == "unvalidated"
        pg.evaluate("window.__guide.selectComponent('canard.core')")
        assert pg.eval_on_selector_all("#ops li.selected", "els => els.map(e => e.dataset.op)") == ["c10.cores"]
        b.close()
    s.shutdown()

def test_no_private_assets_shows_none_not_broken(site):  # Review Focus 1
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.cores"]')
        assert pg.locator("#source .none").count() == 1 and pg.locator("#source img").count() == 0
        b.close()
    s.shutdown()

def test_localstorage_throwing_checklist_still_works(site):  # Review Focus 2
    s, url = serve(site)
    init = "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})"
    with sync_playwright() as p:
        b, pg = open_page(p, url, init=init)
        pg.select_option("#variant", "gu"); pg.click('#ops li[data-op="c10.cores"]')
        pg.check("#checklist input[type=checkbox] >> nth=0")
        assert pg.is_checked("#checklist input[type=checkbox] >> nth=0")
        b.close()
    s.shutdown()

def test_missing_model_degrades(site):  # Review Focus 3
    (site / "models" / "longez.glb").unlink()
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.wait_for_function("document.querySelector('#model-status').textContent.includes('3D unavailable')")
        pg.select_option("#variant", "gu")
        assert pg.locator("#ops li[data-op]").count() >= 2
        b.close()
    s.shutdown()

def test_phone_width_no_horizontal_scroll(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=390)
        assert pg.evaluate("document.documentElement.scrollWidth") <= 390
        b.close()
    s.shutdown()
```

- [ ] **Step 3: Run to confirm failure**: `.venv/bin/python -m pytest tests/guide/test_viewer_e2e.py -q` → FAIL (`guide.build_site` missing; Task 12 creates it. Do Task 12 Steps 1–3 first if executing strictly in order, or implement both before running.)

- [ ] **Step 4: Implement the page**

```html
<!-- guide/viewer/index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Long-EZ Build Rehearsal</title>
  <link rel="stylesheet" href="css/app.css">
  <script type="importmap">
    {"imports": {"three": "./vendor/three/build/three.module.min.js",
                 "three/addons/": "./vendor/three/examples/jsm/"}}
  </script>
</head>
<body>
  <header>
    <h1>Long-EZ Build Rehearsal <small>canard</small></h1>
    <label>Canard <select id="variant"><option value="roncz">Roncz (ch 30)</option><option value="gu">GU (ch 10, original)</option></select></label>
  </header>
  <main>
    <nav><ol id="ops"></ol></nav>
    <section id="viewport"><canvas id="c"></canvas><p id="model-status"></p><div id="parts"></div></section>
    <aside>
      <h2 id="op-title"></h2><p id="op-summary"></p>
      <div id="changes"></div>
      <div id="source"></div>
      <h3>Checklist</h3><ul id="checklist"></ul>
    </aside>
  </main>
  <script type="module" src="js/app.js"></script>
</body>
</html>
```

```css
/* guide/viewer/css/app.css */
:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#e3e1db;--acc:#1f5f8b;--sel:#e8f0f7;--warn:#9a5b00}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--fg:#e9e7e2;--mut:#9a978f;--line:#2c2b29;--acc:#7fb6de;--sel:#1d2a35;--warn:#e0a54a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
header{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:1.1rem;margin:0} h1 small{color:var(--mut);font-weight:400}
main{display:grid;grid-template-columns:260px 1fr 360px;height:calc(100vh - 54px)}
nav,aside{overflow-y:auto;padding:8px 16px;border-right:1px solid var(--line)} aside{border-right:0;border-left:1px solid var(--line)}
#ops{list-style:none;padding:0;margin:0} #ops li{padding:6px 8px;border-radius:6px;cursor:pointer}
#ops li.selected{background:var(--sel)} #ops li.stub{color:var(--mut);font-style:italic}
#viewport{position:relative;min-height:320px} #c{width:100%;height:100%;display:block}
#model-status{position:absolute;top:8px;left:12px;color:var(--warn);margin:0}
#parts{position:absolute;bottom:8px;left:8px;right:8px;display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);border-radius:999px;padding:2px 10px;background:var(--bg);font-size:.85rem;cursor:pointer}
.chip[data-badge="no-geometry"]{color:var(--mut);border-style:dashed}
#source img{max-width:100%;border:1px solid var(--line)} #source .none{color:var(--mut)}
.change{border-left:3px solid var(--acc);padding:4px 8px;margin:6px 0;font-size:.9rem}
@media (max-width:820px){main{grid-template-columns:1fr;height:auto} nav,aside{border:0} #viewport{height:50vh}}
```

```js
// guide/viewer/js/app.js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { visibleOps, opsForComponent, badge, scanView, makeStore } from "./graph.js";

const $ = s => document.querySelector(s);
let storage; try { storage = window.localStorage; } catch { storage = null; }
const store = makeStore(storage ?? { getItem() { return null; }, setItem() {} });
const [graph, cfg] = await Promise.all([fetch("graph.json").then(r => r.json()), fetch("config.json").then(r => r.json())]);
const byId = new Map(graph.ops.map(o => [o.id, o]));
const meshes = new Map();
let current = null;

// ---- 3D
const canvas = $("#c");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 10000);
const controls = new OrbitControls(camera, canvas);
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2.2));
function resize() {
  const r = canvas.parentElement.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / Math.max(r.height, 1); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas.parentElement);
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });

new GLTFLoader().load(cfg.model, gltf => {
  scene.add(gltf.scene);
  gltf.scene.traverse(o => {
    if (!o.isMesh) return;
    let n = o; while (n && !graph.components[n.name] && n.parent) n = n.parent;
    const cid = graph.components[n?.name] ? n.name : o.name;
    o.material = new THREE.MeshStandardMaterial({ color: 0xc9c4b8 });
    meshes.set(o, cid);
  });
  const box = new THREE.Box3().setFromObject(gltf.scene), c = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();
  controls.target.copy(c); camera.position.copy(c).add(new THREE.Vector3(size * 0.6, size * 0.5, size * 0.8));
  camera.near = size / 1000; camera.far = size * 10; camera.updateProjectionMatrix();
  if (current) highlight(byId.get(current).components);
}, undefined, () => { $("#model-status").textContent = "3D unavailable — steps and sources still work"; });

function highlight(cids) {
  for (const [m, cid] of meshes) m.material.emissive?.setHex(cids.includes(cid) ? 0x1f5f8b : 0x000000);
}
const ray = new THREE.Raycaster();
canvas.addEventListener("click", e => {
  const r = canvas.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
  const hit = ray.intersectObjects([...meshes.keys()])[0];
  if (hit) selectComponent(meshes.get(hit.object));
});

// ---- UI
function renderList() {
  const ol = $("#ops"); ol.replaceChildren();
  for (const op of visibleOps(graph, $("#variant").value)) {
    const li = document.createElement("li");
    li.dataset.op = op.id; li.textContent = op.title; if (op.stub) li.className = "stub";
    li.onclick = () => selectOp(op.id); ol.append(li);
  }
}
function markSelected(ids) {
  for (const li of document.querySelectorAll("#ops li")) li.classList.toggle("selected", ids.includes(li.dataset.op));
}
function selectOp(id) {
  current = id; const op = byId.get(id); markSelected([id]);
  $("#op-title").textContent = op.title;
  $("#op-summary").textContent = op.stub ? "Prerequisite outside this slice." : op.summary;
  $("#parts").replaceChildren(...op.components.map(cid => {
    const b = document.createElement("span"); b.className = "chip"; b.dataset.cid = cid; b.dataset.badge = badge(graph, cid);
    b.textContent = `${graph.components[cid]?.label ?? cid} · ${b.dataset.badge}`; b.onclick = () => selectComponent(cid); return b;
  }));
  $("#changes").replaceChildren(...(op.changes ?? []).map(c => {
    const d = document.createElement("div"); d.className = "change";
    d.textContent = `CP ${c.cp} · LPC ${c.lpc} · ${c.class} · ${c.status}: ${c.note}`; return d;
  }));
  const src = $("#source"); src.replaceChildren();
  for (const s of op.sources ?? []) {
    const v = scanView(s, cfg);
    if (v.kind === "none") { const p = document.createElement("p"); p.className = "none"; p.textContent = `Plans ${s.page ?? "p." + s.scan_pp}: scan not available here`; src.append(p); }
    else { const img = document.createElement("img"); img.src = v.url; img.alt = `Plans ${s.page ?? s.scan_pp}`; img.loading = "lazy"; src.append(img); }
  }
  const ul = $("#checklist"); ul.replaceChildren();
  const done = store.get(id);
  (op.completion ?? []).forEach((t, i) => {
    const li = document.createElement("li"), cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = done.has(i); cb.onchange = () => store.toggle(id, i);
    li.append(cb, " ", t); ul.append(li);
  });
  highlight(op.components);
}
function selectComponent(cid) {
  const visible = new Set(visibleOps(graph, $("#variant").value).map(o => o.id));
  const ids = opsForComponent(graph, cid).filter(i => visible.has(i));
  markSelected(ids); highlight([cid]);
}
window.__guide = { selectComponent };
$("#variant").onchange = () => { renderList(); current = null; };
renderList();
```

- [ ] **Step 5: Run e2e + node tests**: `.venv/bin/python -m pytest tests/guide/test_viewer_e2e.py -q && node --test guide/viewer/tests/*.test.mjs` → 5 passed; 5 pass
- [ ] **Step 6: Commit**: `git add scripts/vendor_three.sh guide/viewer tests/guide/test_viewer_e2e.py && git commit -m "feat(guide): three.js build-rehearsal viewer"`

---

### Task 12: Site build + deploy

**Files:**
- Create: `guide/build_site.py`, `scripts/deploy_guide.sh`
- Test: `tests/guide/test_build_site.py`

**Interfaces:**
- Consumes: Task 1 (`load_graph`, `validate`, `topo_order`), Task 7 glb.
- Produces: `build(graph_dir: Path, out: Path, models: Path|None, scan_base: str|None, docs: Path|None) -> None`. It writes `out/` = the viewer copy (minus `tests/`), `graph.json`, `config.json`, `models/longez.glb`, and `docs/*.html` rendered from `docs/superpowers/{specs,plans}/*build-guide*`. Raises `SchemaError` if `validate` returns errors. CLI: `python -m guide.build_site --out site [--models output/guide/longez.glb] [--scan-base /private/scan-1980/pages/]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/guide/test_build_site.py
import json
import pytest
from guide.build_site import build
from guide.schema import SchemaError
from tests.guide.test_schema import gdir  # noqa: F401

def test_build_writes_site(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base="/private/scan-1980/pages/", docs=None)
    g = json.loads((out / "graph.json").read_text())
    assert g["order"][0] == "c03.layup-skills"
    assert {o["id"] for o in g["ops"]} == {"c03.layup-skills", "c10.cores", "c10.twist-check"}
    assert g["ops"][1]["id"] == "c10.cores" and g["ops"][1]["changes"][0]["class"] == "MEO"
    assert json.loads((out / "config.json").read_text())["scanBase"] == "/private/scan-1980/pages/"
    assert (out / "index.html").exists() and not (out / "tests").exists()

def test_build_refuses_invalid_graph(gdir, tmp_path):
    p = gdir / "ch10.yaml"; p.write_text(p.read_text().replace("requires: [c10.cores]", "requires: [nope]"))
    with pytest.raises(SchemaError):
        build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
```

- [ ] **Step 2: Run to confirm failure**: FAIL `ModuleNotFoundError`
- [ ] **Step 3: Implement**

```python
# guide/build_site.py
"""Assemble the static site: viewer + graph.json + config.json + model + rendered docs."""
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import shutil
import sys
from pathlib import Path

from guide.schema import SchemaError, load_graph, topo_order, validate

VIEWER = Path(__file__).parent / "viewer"


def _op_json(op) -> dict:
    d = dataclasses.asdict(op)
    for c in d["changes"]:
        c["class"] = c.pop("cls")
    return d


def _render_docs(docs: Path, out: Path) -> None:
    import markdown

    out.mkdir(parents=True, exist_ok=True)
    items = []
    for md in sorted(list((docs / "specs").glob("*build-guide*.md")) + list((docs / "plans").glob("*build-guide*.md"))):
        body = markdown.markdown(md.read_text(), extensions=["tables", "fenced_code"])
        (out / f"{md.stem}.html").write_text(
            f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(md.stem)}</title><link rel=stylesheet href='../css/app.css'>"
            f"<main style='display:block;max-width:860px;margin:auto;padding:16px;height:auto'>{body}</main>")
        items.append(f"<li><a href='{md.stem}.html'>{html.escape(md.stem)}</a></li>")
    (out / "index.html").write_text("<!doctype html><meta charset=utf-8><title>docs</title><ul>" + "".join(items) + "</ul>")


def build(graph_dir: Path, out: Path, models: Path | None, scan_base: str | None, docs: Path | None) -> None:
    g = load_graph(graph_dir)
    errs = validate(g)
    if errs:
        raise SchemaError("; ".join(errs))
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(VIEWER, out, ignore=shutil.ignore_patterns("tests"))
    payload = {
        "ops": [_op_json(g.ops[i]) for i in topo_order(g)],
        "order": topo_order(g),
        "components": {c.id: {"label": c.label, "fidelity": c.fidelity} for c in g.components.values()},
        "pages": {str(k): v for k, v in g.pages.items()},
        "annotations": [dataclasses.asdict(a) for a in g.annotations if a.confirmed],
    }
    (out / "graph.json").write_text(json.dumps(payload, indent=1))
    (out / "config.json").write_text(json.dumps({"scanBase": scan_base, "model": "models/longez.glb"}))
    (out / "models").mkdir()
    if models:
        shutil.copy(models, out / "models" / "longez.glb")
    if docs:
        _render_docs(docs, out / "docs")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.build_site")
    ap.add_argument("--graph", type=Path, default=Path("guide/graph"))
    ap.add_argument("--out", type=Path, default=Path("site"))
    ap.add_argument("--models", type=Path, default=None)
    ap.add_argument("--scan-base", default=None)
    ap.add_argument("--docs", type=Path, default=Path("docs/superpowers"))
    a = ap.parse_args(argv)
    build(a.graph, a.out, a.models, a.scan_base, a.docs)
    print(f"built {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```bash
# scripts/deploy_guide.sh — build, gate, and publish the guide to the private-network host.
#!/usr/bin/env bash
set -euo pipefail
: "${LONGEZ_DEPLOY_HOST:?set LONGEZ_DEPLOY_HOST (ssh target of the private-network host)}"
: "${LONGEZ_SITE_URL:?set LONGEZ_SITE_URL (private-network https URL of the site)}"
cd "$(dirname "$0")/.."
PY=.venv/bin/python
$PY -m guide.check                       # full mode; exits non-zero on any gate failure
$PY -m guide.export_glb --out output/guide/longez.glb
$PY -m guide.build_site --out site --models output/guide/longez.glb --scan-base private/scan-1980/pages/
rsync -a --delete --exclude private/ site/ "$LONGEZ_DEPLOY_HOST":<site root>/site/
ssh "$LONGEZ_DEPLOY_HOST" 'ln -sfn <host private dir>/private <site root>/site/private'
want=$(python3 -c 'import json;print(len(json.load(open("site/graph.json"))["ops"]))')
body=$(curl -fsS "$LONGEZ_SITE_URL/graph.json")
got=$(python3 -c 'import json,sys;print(len(json.loads(sys.stdin.read())["ops"]))' <<<"$body")
[ "$got" = "$want" ] || { echo "DEPLOY VERIFY FAILED: site serves $got ops, built $want" >&2; exit 1; }
curl -fsS -o /dev/null "$LONGEZ_SITE_URL/private/scan-1980/pages/058.jpg" || { echo "DEPLOY VERIFY FAILED: private scan not served" >&2; exit 1; }
echo "deployed and verified: $got ops at $LONGEZ_SITE_URL"
```

`--scan-base` is relative (`private/scan-1980/pages/`), so the same build works under any host. The host already runs the static service (`long-ez-guide.service`, 127.0.0.1:7485 behind `a private reverse proxy`, set up 2026-09-28). The rsync `--delete` excludes `private/`, so the symlink survives.

- [ ] **Step 4: Run tests**: `.venv/bin/python -m pytest tests/guide/test_build_site.py tests/guide/test_viewer_e2e.py -q` → all pass
- [ ] **Step 5: Deploy for real**

Run: `source ~/.config/long-ez/env && bash scripts/deploy_guide.sh`
Expected: `deployed and verified: 19 ops at <url>` (17 ops + 2 stubs).

- [ ] **Step 6: Retire the scratch doc repo.** The host site previously served docs from `~/long-ez-guide` (a local-only scratch repo from the design session). After Step 5 serves `docs/` from this build, `rm -rf ~/long-ez-guide`.
- [ ] **Step 7: Commit**: `git add guide/build_site.py scripts/deploy_guide.sh tests/guide/test_build_site.py && git commit -m "feat(guide): site build and verified private-network deploy"`

---

### Task 13: Grade, push, acceptance

- [ ] **Step 1: Full suite**: `.venv/bin/python -m pytest tests/guide -q && node --test guide/viewer/tests/*.test.mjs && .venv/bin/python -m guide.check`. All green, with output pasted into the report.
- [ ] **Step 2: Leak sweep before the public push**

```bash
git diff origin/main --stat
git diff origin/main | grep -nE 'ts\.net|100\.[0-9]+\.[0-9]+\.[0-9]+|/Users/|Downloads|public domain' && echo "LEAK — fix before push" || echo "clean"
git ls-files | grep -iE '\.(jpg|jpeg|png|pdf|tif)$' | grep -v '^data/' || echo "no images tracked"
```

Expected: `clean` and `no images tracked`.

- [ ] **Step 3: Fresh-context grader** (house rule 2): run `~/.claude/bin/grade-diff.sh` from the repo root. The grader tries to prove the spec DoD items 1–5 false. Push in the **same turn** as a PASS (the grader's files are reaped at turn end).
- [ ] **Step 4: Push**: `git push origin main` (public push authorized by the owner 2026-09-28 for guide code + own-words content under the overlap gate; scans never).
- [ ] **Step 5: Owner acceptance.** The owner opens the site on the iPad over the private-network and walks through the Roncz path. Done when they can explain the sequence, the applicable corrections and the spatial fit (spec §1). Log the outcome to lane-log.
