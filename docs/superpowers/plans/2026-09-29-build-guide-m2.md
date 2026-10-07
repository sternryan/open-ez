# Long-EZ Build Guide M2 (Layup Cutaway) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show what is inside the Roncz canard, ply by ply, as GPU-rendered cutaways in the build guide:
two hero sections (BL 5, BL 40), a highlight frame per layup op, and a reachable ply list in the 3D
viewer.

**Architecture:**
- CadQuery (open-ez) builds a real solid core plus one solid per ply from the step graph, and exports
  a glb with ply nodes nested under their components, plus `layup.json` and `shots.json`.
- `guide/render_cutaway.sh` stages those on the GPU host and runs `layup_cutaway.py` through
  `gpu-runner run blender.sh`, then pulls the PNGs and `manifest.json` into a cache directory named
  by a render key.
- `build_site --renders` verifies the renders against the current inputs and wires them into the
  viewer.

**Tech Stack:**
- Python 3.10+, CadQuery, numpy, pytest, Playwright
- Blender 5.2.2 (bpy) on the GPU host via the job scheduler/`gpu-runner`
- vanilla JS + three.js, node `--test`

**Spec:** `docs/superpowers/specs/2026-09-29-build-guide-m2-layup-cutaway-design.md` (rev 3).
Read it before any task.

## Global Constraints

- **CadQuery is the geometry SSOT; Blender output is derived.** No Blender wrapper, lease client or
  second GPU path: scripts go in `the render-tooling repo/deploy/<gpu-host>/jobs/blender/` and run through
  `gpu-runner`.
- **The step graph is the ply SSOT.** Nothing is drawn that `guide/graph/ch30.yaml` does not hold.
  Guesses carry `position_verified: false`.
- **Never claim the plans are out of copyright anywhere in the repo.** Label and legend text must pass
  `.venv/bin/python -m guide.check` (full mode).
- **`blender.sh` takes a bare script name** matching `^[a-z0-9_]+$`: `layup_cutaway`, never
  `layup_cutaway.py`. Flags go after positionals: `gpu-runner run blender.sh layup_cutaway <job_dir>
  --no-wait --expect-s N`.
- **Never run Blender on the GPU host outside `gpu-runner`**; it OOMs against vLLM's VRAM.
- **`BLENDER_REQUIRE_GPU=1` stays the default**; a CPU fallback is a failure.
- **Visual ply thickness is exaggerated** (PLY_T 0.10 in, PLY_GAP 0.03 in), and every view says
  "not to scale".
- **Renders are never committed.** They live in `~/.cache/long-ez/renders/<key>/`.
- **Anything scheduled is out of bounds:** render_cutaway and deploy are run by hand.
- **Node tests:** `node --test guide/viewer/tests/*.test.mjs` (Node 22 needs the file glob, not a dir).
- **Python tests:** `.venv/bin/python -m pytest …` from the open-ez root. the render-tooling repo tests:
  `cd <render-tooling repo> && python3 -m pytest deploy/<gpu-host>/tests -q`.
- **Commit messages** end with no session trailer of any kind. **Do not push** open-ez: it is public,
  and a push needs Ryan's per-instance OK.
- **The pre-commit hook may reject red-first commits.** Commit only when the task's tests are green.

## Spec deviations (decided while planning, all reversible)

1. **Atomic output.** `blender.sh` pre-creates `out/`, so the spec's `out.tmp/ → out/` rename would
   fight the payload. The equivalent guarantee comes from three things:
   - the job dir is deleted and restaged fresh per run;
   - `manifest.json` is written last;
   - the laptop pulls into `<key>.tmp/`, checks it, and renames to `<key>/` only if the check passes.
2. **Split module.** "layup.py" is split into `guide/layup.py` (pure data, no CadQuery; used by the
   site build) and `guide/layup_geometry.py` (CadQuery solids).
3. **Key computed on the laptop.** The render key is computed by `guide/render_key.py`. Blender only
   records per-file sha256s in the manifest.
4. **Hero camera.** Hero shots use an **orthographic camera looking straight along the span**, which
   is best for counting bands. The op frames use the 3/4 perspective the spec describes.
5. **Contract module.** A third Blender-side file, `layup_contract.py` (no `bpy`), holds the testable
   shot/manifest/colour logic, so it can be unit-tested on the laptop.

## Review Focus

The five most likely ways this breaks for a person using it that no spec line covers:

1. **Axis and units.** Blender's glTF import converts Y-up to Z-up. If CadQuery's export and Blender's
   import don't cancel, the "BL 5" cut lands on the wrong plane and the hero is garbage. Expectation:
   the job fails loudly. Pinned in Task 5 (`check_axes` raises unless the scene's Y extent ≈
   semi-span) and checked live in Task 7.
2. **Name suffixes.** Blender renames duplicate or long objects (`.001` suffixes), so a mesh maps to
   no layup node. Expectation: the suffix is stripped, and a truly unmapped mesh fails the job, never
   renders grey. Pinned in Task 5 (`resolve_node`).
3. **Op ids with dots.** Op ids like `r30.shear-web` must become filename-safe shot ids, and the
   viewer must find the PNG. Pinned in Task 2 (`shot_id_for_op`) and Task 9 (e2e).
4. **Missing picture.** On a layup op, the cutaway PNG 404s (partial deploy). Expectation: "Cutaway
   picture didn't load" with Retry, and the 3D toggle still works. Pinned in Task 9 (e2e).
5. **Interrupted pull.** A pull dies half-way and leaves `<key>.tmp/`. Expectation: the next run
   clears it, and deploy never reads a `.tmp`. Pinned in Task 6 (`test_stale_tmp_is_replaced`).

## File map

| File | Responsibility |
|---|---|
| `core/structures.py` (modify) | Task 0 fix: rotate station wires into XZ at loft placement |
| `tests/test_core_solid.py` (new) | Core is a real solid |
| `guide/layup.py` (new) | Parse `where`, `LAYUP_SCOPE`, plies, counts, shots, alt text, `layup.json` |
| `guide/layup_geometry.py` (new) | CadQuery ply solids + section-ready foam |
| `guide/export_glb.py` (modify) | Nested ply nodes; writes `layup.json` + `shots.json` |
| `guide/render_key.py` (new) | File shas, render key, render-dir check |
| `guide/render_cutaway.sh` (new) | Stage → gpu-runner → pull → check → atomic rename |
| `guide/build_site.py` (modify) | `plies` in graph.json; optional strict `--renders` |
| `guide/viewer/js/cutaway.js` (new) | Pure view logic (toggle memory, pane mode, ply rows) |
| `guide/viewer/js/app.js`, `index.html`, `css/app.css` (modify) | Toggle, glance view, states, ply dock, isolate |
| `scripts/deploy_guide.sh` (modify) | Always passes `--renders`; verifies a hero PNG |
| `guide/graph/ch30.yaml`, `components.yaml` (modify) | 108 in web span; fidelity uplift |
| `the render-tooling repo/deploy/<gpu-host>/jobs/blender/fabric_blender.py` (new) | GPU guard, scene reset, cut helpers (bpy) |
| `…/blender/layup_contract.py` (new) | Inputs/visibility/colour/manifest logic (no bpy) |
| `…/blender/layup_cutaway.py` (new) | The render job (bpy) |
| `…/blender/smoke.py` (modify) | Uses `fabric_blender` |
| `…/tests/test_layup_contract.py` (new) | Contract + DRY guard tests |

---

# Session 1: walking skeleton (Tasks 1–7), ends at Ryan's gate

### Task 1: Make the canard core a real solid (spec §3.1)

**Files:**
- Modify: `core/structures.py` (`_build_geometry`, the `wire.moved(...)` block)
- Test: `tests/test_core_solid.py`

**Interfaces:**
- Produces: `CanardGenerator().generate_geometry()` returns a solid with X chordwise, Y spanwise
  (BL 0 → semi-span) and Z thickness. Every later task relies on this frame.

- [ ] **Step 1: Record the suite baseline**

Run: `.venv/bin/python -m pytest -q -p no:cacheprovider 2>&1 | tail -3`
Record the pass/fail counts in the task notes. Later steps compare against them.

- [ ] **Step 2: Write the failing test**

```python
# tests/test_core_solid.py
"""The canard core must be a real solid: X chordwise, Y spanwise (BL), Z thickness."""
from core.structures import CanardGenerator


def test_canard_core_has_volume_and_thickness():
    gen = CanardGenerator()
    solid = gen.generate_geometry().val()
    bb = solid.BoundingBox()
    _, y = gen.root_airfoil.coordinates
    root_thickness = float(y.max() - y.min()) * gen.root_chord
    assert solid.isValid()
    assert solid.Volume() > 100.0  # cubic inches; it was 0.0 before the fix
    assert abs(bb.ylen - gen.span / 2) < 1.0
    assert abs(bb.zlen - root_thickness) < 0.15 * root_thickness
```

- [ ] **Step 3: Run it to confirm it fails**

Run: `.venv/bin/python -m pytest tests/test_core_solid.py -v`
Expected: FAIL at `solid.Volume() > 100.0` (volume is 0.0).

- [ ] **Step 4: Rotate each station wire into XZ at placement**

In `core/structures.py` `_build_geometry`, replace the block that builds `wire_moved`:

```python
            # Get airfoil wire at local chord. The profile is built in the XY plane
            # (x = chord, y = thickness); G-code and DXF export consume it that way, so
            # rotate it here, not in the airfoil: +90 deg about X maps thickness to +Z.
            wire = station.airfoil.get_cadquery_wire(station.chord)
            wire_xz = wire.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)

            # Place the station: sweep along X, span along Y (butt line), dihedral along Z.
            wire_moved = wire_xz.moved(
                cq.Location(
                    cq.Vector(station.x_offset, station.butt_line, station.z_offset)
                )
            )
```

Delete the old comment lines "Wire is in XY plane; we need to: 1…2…3…", which described the bug.

- [ ] **Step 5: Run the test and the full suite**

Run: `.venv/bin/python -m pytest tests/test_core_solid.py -v`. Expected: PASS.
Run: `.venv/bin/python -m pytest -q -p no:cacheprovider 2>&1 | tail -3`. Expected: the baseline
counts plus 1 passing.
- A newly failing G-code, DXF or segment test means a consumer read the placed wire. Stop and fix the
  consumer to use the 2D profile; do not revert the rotation.

- [ ] **Step 6: Commit**

```bash
git add core/structures.py tests/test_core_solid.py
git commit -m "fix(core): loft stations in XZ so the canard core is a solid (was volume 0)"
```

---

### Task 2: Layup data, scope and shots (pure Python) + ch30 span edit

**Files:**
- Create: `guide/layup.py`
- Modify: `guide/graph/ch30.yaml:44`, `guide/graph/components.yaml`
- Test: `tests/guide/test_layup.py`

**Interfaces:**
- Consumes: `guide.schema.load_graph(Path) -> Graph`. `Graph.ops` is a dict of id → Op; `Op.materials`
  is a tuple of dicts with keys `cloth`, `plies`, `where`; `Op.title` is a str.
- Produces (Tasks 3, 4, 8 and 9 rely on these exact names):
  - `LayupError(ValueError)`
  - `parse_where(where: str) -> tuple[str, float | None]`, returning (orientation, bl_max);
    None means the whole semi-span.
  - `INCLUDED_OPS: tuple[str, ...]`, `OP_COMPONENT: dict[str, str]`, `SPAR_CAP_OPS: frozenset[str]`,
    `SPAR_CAP_BL_MAX = 54.0`, `EXCLUDED_ROWS: dict[tuple[str, str], str]`, `HERO_BLS = (5.0, 40.0)`,
    `OP_FRAME_BL = 5.0`
  - `material_rows(graph) -> list[tuple[str, str]]`
  - `scope_problems(rows, op_ids) -> list[str]`
  - `@dataclass(frozen=True) Ply` with fields `node`, `component`, `op`, `op_index`, `order`, `cloth`,
    `orientation`, `where`, `bl_max`, `position_verified`
  - `plies(graph) -> list[Ply]`
  - `counts_at(plies, bl: float) -> dict[str, int]`
  - `shot_id_for_op(op_id: str) -> str`
  - `shots() -> list[dict]`, each with keys `id`, `kind`, `bl`, `highlight`, `upto`
  - `alt_text(graph, plies, shot: dict) -> str`
  - `count_note(plies) -> str`
  - `layup_json(plies, semi_span: float) -> dict`: records `semi_span` so the render job can
    check axes.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_layup.py
"""Layup data from the REAL ch30 graph (fixtures can't catch premise defects in the data)."""
import re
from pathlib import Path

import pytest

from guide import layup
from guide.schema import load_graph

G = load_graph(Path("guide/graph"))


@pytest.mark.parametrize("where,expected", [
    ("crossed, full span (108 in)", ("crossed", 54.0)),
    ("crossed, inboard of BL 30", ("crossed", 30.0)),
    ("45 degrees, inboard of BL 10", ("45 degrees", 10.0)),
    ("45 degrees, full span", ("45 degrees", None)),
    ("spanwise, first ply", ("spanwise", None)),
    ("spanwise, final plies", ("spanwise", None)),
])
def test_parse_where_known(where, expected):
    assert layup.parse_where(where) == expected


@pytest.mark.parametrize("where", ["crossed, most of the span", "diagonal, full span", "full span",
                                   "crossed, full span (108)", ""])
def test_parse_where_rejects_unknown(where):
    with pytest.raises(layup.LayupError):
        layup.parse_where(where)


def test_shear_web_full_span_row_carries_108_in():
    rows = G.ops["r30.shear-web"].materials
    assert rows[0]["where"] == "crossed, full span (108 in)"


def test_real_graph_is_fully_scoped():
    assert layup.scope_problems(layup.material_rows(G), set(G.ops)) == []


def test_unscoped_row_is_a_problem():
    rows = layup.material_rows(G) + [("r30.top-skin", "spanwise, a new ply")]
    assert any("r30.top-skin" in p for p in layup.scope_problems(rows, set(G.ops)))
    rows = layup.material_rows(G) + [("r30.hinge-foam", "crossed, full span")]
    assert any("not in LAYUP_SCOPE" in p for p in layup.scope_problems(rows, set(G.ops)))


def test_missing_included_op_is_a_problem():
    assert any("r30.shear-web" in p
               for p in layup.scope_problems(layup.material_rows(G), set(G.ops) - {"r30.shear-web"}))


def test_acceptance_counts():  # spec §1: the numbers Ryan counts on the iPad
    pl = layup.plies(G)
    for bl in (5.0, 40.0):
        c = layup.counts_at(pl, bl)
        assert c["canard.skin_bottom"] == 3 and c["canard.skin_top"] == 4
    assert layup.counts_at(pl, 5.0)["canard.shear_web"] == 6
    assert layup.counts_at(pl, 40.0)["canard.shear_web"] == 2


def test_ply_order_follows_yaml():
    top = [p for p in layup.plies(G) if p.component == "canard.skin_top"]
    assert [p.cloth for p in top] == ["UND", "BID", "UND", "UND"]
    assert [p.order for p in top] == [1, 2, 3, 4]
    assert top[0].node == "canard.skin_top.p1"


def test_position_flags():
    pl = layup.plies(G)
    assert all(not p.position_verified for p in pl
               if p.component in ("canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"))
    assert all(p.position_verified for p in pl if p.component.startswith("canard.skin_"))
    caps = [p for p in pl if p.op in layup.SPAR_CAP_OPS]
    assert len(caps) == 2 and all(p.bl_max == layup.SPAR_CAP_BL_MAX for p in caps)


def test_shots_cover_scope_and_are_filename_safe():
    s = layup.shots()
    assert [x["id"] for x in s[:2]] == ["hero-bl5", "hero-bl40"]
    assert [x["highlight"] for x in s[2:]] == list(layup.INCLUDED_OPS)
    assert all(re.fullmatch(r"[a-z0-9-]+", x["id"]) for x in s)
    assert layup.shot_id_for_op("r30.shear-web") == "op-r30-shear-web"


def test_alt_text_is_generated_from_counts():
    pl = layup.plies(G)
    hero = layup.shots()[0]
    assert layup.alt_text(G, pl, hero) == (
        "Section at BL 5: bottom skin 3 plies, top skin 4 plies, shear web 6 plies, "
        "spar caps filled to the trough (not to scale)")
    op = next(x for x in layup.shots() if x["highlight"] == "r30.bottom-skin")
    assert layup.alt_text(G, pl, op).startswith(f"After {G.ops['r30.bottom-skin'].title}:")


def test_layup_json_shape():
    j = layup.layup_json(layup.plies(G), 73.5)
    assert j["ops"] == list(layup.INCLUDED_OPS) and j["semi_span"] == 73.5
    n = j["nodes"]["canard.shear_web.p1"]
    assert n["component"] == "canard.shear_web" and n["cloth"] == "UND" and n["op_index"] == 0
```

- [ ] **Step 2: Run them to confirm they fail**

Run: `.venv/bin/python -m pytest tests/guide/test_layup.py -q`
Expected: collection error (`guide.layup` does not exist).

- [ ] **Step 3: Edit the graph**

In `guide/graph/ch30.yaml` line 44, change the shear-web full-span row to:

```yaml
    - {cloth: UND, plies: 2, where: "crossed, full span (108 in)"}
```

In `guide/graph/components.yaml`, set `fidelity: unvalidated` on these five lines:

```yaml
- {id: canard.shear_web, label: Shear web, fidelity: unvalidated}
- {id: canard.spar_cap_bottom, label: Bottom spar cap, fidelity: unvalidated}
- {id: canard.skin_bottom, label: Bottom skin, fidelity: unvalidated}
- {id: canard.spar_cap_top, label: Top spar cap, fidelity: unvalidated}
- {id: canard.skin_top, label: Top skin, fidelity: unvalidated}
```

- [ ] **Step 4: Write `guide/layup.py`**

```python
"""Layup data for the M2 cutaway: parse ch30 ply rows, scope them, expand plies, derive shots.

Pure Python (no CadQuery) so the site build can use it without geometry.

    ch30.yaml materials ─parse_where─► Ply(component, op, cloth, order, bl_max)
          │                                 │
    LAYUP_SCOPE (included ops,              ├─► counts_at(bl) ─► alt text, acceptance counts
    excluded rows with reasons)             ├─► shots() ─► shots.json (hero + one per op)
                                            └─► layup_json() ─► layup.json (glb node → ply)
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass


class LayupError(ValueError):
    pass


ORIENTATIONS = frozenset({"crossed", "45 degrees", "spanwise"})
_EXTENTS = (
    (re.compile(r"full span \((\d+(?:\.\d+)?) in\)"), lambda m: float(m.group(1)) / 2),
    (re.compile(r"full span"), lambda m: None),
    (re.compile(r"inboard of BL (\d+(?:\.\d+)?)"), lambda m: float(m.group(1))),
    (re.compile(r"first ply|last ply|final plies"), lambda m: None),
)

# Build order; op frames and op_index follow it.
INCLUDED_OPS = ("r30.shear-web", "r30.bottom-spar-cap", "r30.bottom-skin", "r30.top-spar-cap", "r30.top-skin")
OP_COMPONENT = {
    "r30.shear-web": "canard.shear_web",
    "r30.bottom-spar-cap": "canard.spar_cap_bottom",
    "r30.bottom-skin": "canard.skin_bottom",
    "r30.top-spar-cap": "canard.spar_cap_top",
    "r30.top-skin": "canard.skin_top",
}
SPAR_CAP_OPS = frozenset({"r30.bottom-spar-cap", "r30.top-spar-cap"})
SPAR_CAP_BL_MAX = 54.0  # troughs run the inboard cores only; the tip cores have none (cobelu ch 30)
SPAR_CAP_WHERE = "3 in UND tape, plies as required to fill trough (tapered)"
_LOCAL = "local feature, not at a section station"
EXCLUDED_ROWS = {
    ("r30.shear-web", "pad over each CL-1 nut plate"): f"CL-1 nut-plate pads: {_LOCAL}",
    ("r30.align-canard", "forward face of each rear tab"): f"rear tab: {_LOCAL}",
    ("r30.align-canard", "aft face of each rear tab"): f"rear tab: {_LOCAL}",
}
HERO_BLS = (5.0, 40.0)
OP_FRAME_BL = 5.0
UNVERIFIED_POSITION = frozenset({"canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"})
_LABEL = {"canard.skin_bottom": "bottom skin", "canard.skin_top": "top skin", "canard.shear_web": "shear web"}


def parse_where(where: str) -> tuple[str, float | None]:
    parts = [p.strip() for p in where.split(",")]
    if len(parts) != 2 or parts[0] not in ORIENTATIONS:
        raise LayupError(f"unrecognised ply location {where!r}")
    for rx, extent in _EXTENTS:
        m = rx.fullmatch(parts[1])
        if m:
            return parts[0], extent(m)
    raise LayupError(f"unrecognised ply extent {where!r}")


def material_rows(graph) -> list[tuple[str, str]]:
    return [(op_id, m["where"]) for op_id, op in graph.ops.items() for m in op.materials]


def scope_problems(rows, op_ids) -> list[str]:
    probs = [f"LAYUP_SCOPE op {o} is not in the graph" for o in INCLUDED_OPS if o not in op_ids]
    for op_id, where in rows:
        if (op_id, where) in EXCLUDED_ROWS:
            continue
        if op_id not in INCLUDED_OPS:
            probs.append(f"{op_id} row {where!r} is not in LAYUP_SCOPE (include the op or exclude the row)")
            continue
        try:
            parse_where(where)
        except LayupError as e:
            probs.append(f"{op_id}: {e}")
    return probs


@dataclass(frozen=True)
class Ply:
    node: str
    component: str
    op: str
    op_index: int
    order: int
    cloth: str
    orientation: str
    where: str
    bl_max: float | None
    position_verified: bool


def plies(graph) -> list[Ply]:
    probs = scope_problems(material_rows(graph), set(graph.ops))
    if probs:
        raise LayupError("; ".join(probs))
    out: list[Ply] = []
    for op_index, op_id in enumerate(INCLUDED_OPS):
        cid = OP_COMPONENT[op_id]
        verified = cid not in UNVERIFIED_POSITION
        if op_id in SPAR_CAP_OPS:
            out.append(Ply(f"{cid}.p1", cid, op_id, op_index, 1, "UND", "spanwise", SPAR_CAP_WHERE,
                           SPAR_CAP_BL_MAX, False))
            continue
        order = 0
        for m in graph.ops[op_id].materials:
            if (op_id, m["where"]) in EXCLUDED_ROWS:
                continue
            orientation, bl_max = parse_where(m["where"])
            for _ in range(int(m["plies"])):
                order += 1
                out.append(Ply(f"{cid}.p{order}", cid, op_id, op_index, order, m["cloth"], orientation,
                               m["where"], bl_max, verified))
    return out


def counts_at(pl, bl: float) -> dict[str, int]:
    c: dict[str, int] = {}
    for p in pl:
        if p.bl_max is None or bl <= p.bl_max:
            c[p.component] = c.get(p.component, 0) + 1
    return c


def shot_id_for_op(op_id: str) -> str:
    return "op-" + re.sub(r"[^a-z0-9]+", "-", op_id.lower()).strip("-")


def shots() -> list[dict]:
    s = [{"id": f"hero-bl{int(b)}", "kind": "hero", "bl": b, "highlight": None, "upto": None} for b in HERO_BLS]
    s += [{"id": shot_id_for_op(op), "kind": "op", "bl": OP_FRAME_BL, "highlight": op, "upto": i}
          for i, op in enumerate(INCLUDED_OPS)]
    return s


def alt_text(graph, pl, shot: dict) -> str:
    if shot["kind"] == "hero":
        c = counts_at(pl, shot["bl"])
        parts = [f"{_LABEL[k]} {c.get(k, 0)} plies" for k in ("canard.skin_bottom", "canard.skin_top", "canard.shear_web")]
        return f"Section at BL {shot['bl']:g}: " + ", ".join(parts) + ", spar caps filled to the trough (not to scale)"
    title = graph.ops[shot["highlight"]].title
    return f"After {title}: its plies accented, later steps not yet laid (not to scale)"


def count_note(pl) -> str:
    a, b = (counts_at(pl, bl) for bl in HERO_BLS)
    return (f"What to count: bottom skin {a['canard.skin_bottom']}, top skin {a['canard.skin_top']} at both "
            f"stations; shear web {a['canard.shear_web']} at BL {HERO_BLS[0]:g}, "
            f"{b['canard.shear_web']} at BL {HERO_BLS[1]:g}.")


def layup_json(pl, semi_span: float) -> dict:
    return {"ops": list(INCLUDED_OPS), "semi_span": semi_span,
            "nodes": {p.node: {k: v for k, v in dataclasses.asdict(p).items() if k != "node"} for p in pl}}
```

- [ ] **Step 5: Run the tests**

Run: `.venv/bin/python -m pytest tests/guide/test_layup.py tests/guide/test_repo_graph.py tests/guide/test_schema.py -q`
Expected: all PASS.

- [ ] **Step 6: Content gate**

Run: `.venv/bin/python -m guide.check`
Expected: exit 0. The `(108 in)` edit and the fidelity changes must pass the overlap gate.

- [ ] **Step 7: Commit**

```bash
git add guide/layup.py tests/guide/test_layup.py guide/graph/ch30.yaml guide/graph/components.yaml
git commit -m "feat(guide): layup scope, ply expansion and shots from the ch30 graph"
```

---

### Task 3: Ply solids and section-ready foam (CadQuery)

**Files:**
- Create: `guide/layup_geometry.py`
- Test: `tests/guide/test_layup_geometry.py`

**Interfaces:**
- Consumes: `guide.layup.plies`, `Ply`, `SPAR_CAP_BL_MAX`; `core.structures.CanardGenerator`
  (Task 1 frame).
- Produces:
  - `Planform.from_generator(gen)`, with methods `chord(bl)`, `le_x(bl)`, `outline(bl) -> (N,2)`
    array of (x, z), and `surface(bl, side) -> (M,2)` running LE→TE.
  - `build_layup(graph) -> dict[str, cq.Shape | dict[str, cq.Shape]]`. The keys are component ids:
    `"canard.core"` maps to the section-ready foam solid, and each ply component maps to
    `{ply.node: solid}`.
  - Constants `PLY_T`, `PLY_GAP`, `WEB_XC`, `TROUGH_W`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_layup_geometry.py
"""Ply solids: valid, exact BL extents, stacked outward, and no overlap with the foam."""
from pathlib import Path

import pytest

from guide import layup
from guide.layup_geometry import Planform, build_layup
from guide.schema import load_graph
from core.structures import CanardGenerator

G = load_graph(Path("guide/graph"))


@pytest.fixture(scope="module")
def built():
    return build_layup(G)


def ply_solids(built):
    return {n: s for cid, v in built.items() if isinstance(v, dict) for n, s in v.items()}


def test_every_ply_is_a_valid_solid(built):
    solids = ply_solids(built)
    assert set(solids) == {p.node for p in layup.plies(G)}
    for n, s in solids.items():
        assert s.isValid() and s.Volume() > 1e-3, n


def test_bl_extents_are_exact(built):
    semi = CanardGenerator().span / 2
    solids = ply_solids(built)
    for p in layup.plies(G):
        ymax = solids[p.node].BoundingBox().ymax
        assert abs(ymax - (p.bl_max if p.bl_max is not None else semi)) < 1e-3, p.node


def test_skin_plies_stack_outward(built):
    top = [built["canard.skin_top"][f"canard.skin_top.p{i}"] for i in range(1, 5)]
    bot = [built["canard.skin_bottom"][f"canard.skin_bottom.p{i}"] for i in range(1, 4)]
    assert [s.BoundingBox().zmax for s in top] == sorted(s.BoundingBox().zmax for s in top)
    assert [s.BoundingBox().zmin for s in bot] == sorted((s.BoundingBox().zmin for s in bot), reverse=True)
    for a, b in zip(top, top[1:]):
        assert a.intersect(b).Volume() < 1e-4


def test_foam_does_not_overlap_web_or_caps(built):
    foam = built["canard.core"]
    assert foam.isValid() and foam.Volume() > 100.0
    for cid in ("canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"):
        for n, s in built[cid].items():
            assert foam.intersect(s).Volume() < 1e-3, n


def test_surfaces_are_ordered_le_to_te_and_split_top_bottom():
    pf = Planform.from_generator(CanardGenerator())
    top, bot = pf.surface(5.0, "top"), pf.surface(5.0, "bottom")
    assert top[0, 0] < top[-1, 0] and bot[0, 0] < bot[-1, 0]
    assert top[:, 1].mean() > bot[:, 1].mean()
```

- [ ] **Step 2: Run them to confirm they fail**

Run: `.venv/bin/python -m pytest tests/guide/test_layup_geometry.py -q`
Expected: collection error (`guide.layup_geometry` missing).

- [ ] **Step 3: Write `guide/layup_geometry.py`**

```python
"""CadQuery solids for the layup cutaway, built off CanardGenerator's own planform.

Frame (core fix, Task 1): X chordwise aft, Y = BL (right half, 0..semi-span), Z up.
The planform is linear in BL (linear taper, straight LE sweep, one airfoil), so each ply is an exact
two-section ruled loft between its outline at BL 0 and at its end BL.

    outline(bl) ─surface(side)─► LE→TE polyline ─_band(d0, d1)─► 2D band ─_loft(0 → bl_max)─► ply
    web plane x_w(bl) = le_x(bl) + WEB_XC·chord(bl)   (placeholder: position_verified false)
    foam = core − (web plies ∪ spar caps)

Thicknesses are VISUAL (not to scale): at true scale a 4-ply skin is ~0.04 in on a 17 in chord.
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq
import numpy as np

from guide import layup

PLY_T = 0.10       # in, visual
PLY_GAP = 0.03     # in, visual separator between plies
WEB_XC = 0.25      # open-ez placeholder; the real trough edge is on template page C-3 (TODOS.md)
TROUGH_W = 3.0     # in: the spar cap is 3 in UND tape (cobelu ch 30 Step 22)
TROUGH_D_ROOT = 0.30   # in, visual cap depth at BL 0 ...
TROUGH_D_END = 0.10    # ... tapering to this at the trough end ("uniformly tapered")
TE_TRIM_XC = 0.97  # skins stop short of the sharp trailing edge so offsets stay simple


@dataclass(frozen=True)
class Planform:
    semi_span: float
    root_chord: float
    tip_chord: float
    sweep_deg: float
    xn: np.ndarray
    zn: np.ndarray

    @classmethod
    def from_generator(cls, gen) -> "Planform":
        x, y = gen.root_airfoil.coordinates
        return cls(gen.span / 2, gen.root_chord, gen.tip_chord, float(gen.sweep_angle), x, y)

    def chord(self, bl: float) -> float:
        return self.root_chord + (bl / self.semi_span) * (self.tip_chord - self.root_chord)

    def le_x(self, bl: float) -> float:
        return bl * float(np.tan(np.radians(self.sweep_deg)))

    def outline(self, bl: float) -> np.ndarray:
        c = self.chord(bl)
        return np.column_stack([self.le_x(bl) + self.xn * c, self.zn * c])

    def surface(self, bl: float, side: str) -> np.ndarray:
        o = self.outline(bl)
        i_le = int(np.argmin(self.xn))
        a, b = o[: i_le + 1][::-1], o[i_le:]
        top, bottom = (a, b) if a[:, 1].mean() > b[:, 1].mean() else (b, a)
        pts = top if side == "top" else bottom
        xc = (pts[:, 0] - self.le_x(bl)) / self.chord(bl)
        return pts[xc <= TE_TRIM_XC]


def _normals(p: np.ndarray, side: str) -> np.ndarray:
    t = np.gradient(p, axis=0)
    n = np.column_stack([-t[:, 1], t[:, 0]])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    want = 1.0 if side == "top" else -1.0
    return n if (n[:, 1].mean() * want) > 0 else -n


def _band(p: np.ndarray, side: str, d0: float, d1: float) -> np.ndarray:
    n = _normals(p, side)
    return np.vstack([p + d0 * n, (p + d1 * n)[::-1]])


def _wire(poly: np.ndarray, bl: float) -> cq.Wire:
    pts = [cq.Vector(float(x), float(bl), float(z)) for x, z in poly]
    return cq.Wire.makePolygon(pts + [pts[0]])


def _loft(poly_at, bl0: float, bl1: float) -> cq.Solid:
    return cq.Solid.makeLoft([_wire(poly_at(bl0), bl0), _wire(poly_at(bl1), bl1)], ruled=True)


def _z_at(pf: Planform, bl: float, x: float, side: str) -> float:
    s = pf.surface(bl, side)
    return float(np.interp(x, s[:, 0], s[:, 1]))


def _web_x(pf: Planform, bl: float) -> float:
    return pf.le_x(bl) + WEB_XC * pf.chord(bl)


def _skin_ply(pf: Planform, p: layup.Ply) -> cq.Solid:
    side = "top" if p.component == "canard.skin_top" else "bottom"
    d0 = (p.order - 1) * (PLY_T + PLY_GAP)
    end = p.bl_max if p.bl_max is not None else pf.semi_span
    return _loft(lambda bl: _band(pf.surface(bl, side), side, d0, d0 + PLY_T), 0.0, end)


def _web_ply(pf: Planform, p: layup.Ply) -> cq.Solid:
    # Plies stack forward from the web plane, ply 1 on the plane.
    def rect(bl: float) -> np.ndarray:
        x1 = _web_x(pf, bl) - (p.order - 1) * (PLY_T + PLY_GAP)
        x0 = x1 - PLY_T
        zb, zt = _z_at(pf, bl, x0, "bottom"), _z_at(pf, bl, x0, "top")
        return np.array([[x0, zb], [x1, zb], [x1, zt], [x0, zt]])
    return _loft(rect, 0.0, p.bl_max)


def _spar_cap(pf: Planform, p: layup.Ply) -> cq.Solid:
    side = "top" if p.component == "canard.spar_cap_top" else "bottom"

    def region(bl: float) -> np.ndarray:
        depth = TROUGH_D_ROOT + (bl / p.bl_max) * (TROUGH_D_END - TROUGH_D_ROOT)
        s = pf.surface(bl, side)
        x0 = _web_x(pf, bl)
        xs = np.linspace(x0, x0 + TROUGH_W, 24)
        seg = np.column_stack([xs, np.interp(xs, s[:, 0], s[:, 1])])
        return _band(seg, side, -depth, 0.0)
    return _loft(region, 0.0, p.bl_max)


def build_layup(graph) -> dict:
    from core.structures import CanardGenerator

    gen = CanardGenerator()
    pf = Planform.from_generator(gen)
    out: dict = {}
    cutters = []
    for p in layup.plies(graph):
        if p.op in layup.SPAR_CAP_OPS:
            solid = _spar_cap(pf, p)
            cutters.append(solid)
        elif p.component == "canard.shear_web":
            solid = _web_ply(pf, p)
            cutters.append(solid)
        else:
            solid = _skin_ply(pf, p)
        out.setdefault(p.component, {})[p.node] = solid
    core = gen.generate_geometry().val()
    out["canard.core"] = core.cut(*cutters)
    return out
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/guide/test_layup_geometry.py -v`
Expected: all PASS.
- If `test_skin_plies_stack_outward` fails on self-intersection near the LE, reduce the curvature by
  decimating: take every 2nd airfoil point in `surface`. Keep the `TE_TRIM_XC` trim.
- If a loft fails with mismatched vertex counts, both sections use the same `xn` mask. Check that
  `surface` trims by `xc` computed from normalized coordinates, not absolute x.

- [ ] **Step 5: Commit**

```bash
git add guide/layup_geometry.py tests/guide/test_layup_geometry.py
git commit -m "feat(guide): ply solids and section-ready foam from the layup data"
```

---

### Task 4: Export nested ply nodes + layup.json + shots.json

**Files:**
- Modify: `guide/export_glb.py`
- Test: `tests/guide/test_export_glb.py` (add tests; keep the existing one)

**Interfaces:**
- Consumes: `guide.layup_geometry.build_layup`, `guide.layup.plies/layup_json/shots`.
- Produces:
  - `export_components(components: dict[str, Node | dict[str, Node]], out: Path) -> Path`, where a
    nested dict becomes a sub-assembly named by the component id, with children named by ply node.
  - `write_layup_files(graph, out_dir: Path) -> None`, which writes `layup.json` and `shots.json`.
  - CLI `python -m guide.export_glb --out output/guide/longez.glb` writes all three files into
    `output/guide/`.

- [ ] **Step 1: Write the failing tests** (append to `tests/guide/test_export_glb.py`)

```python
import hashlib
import json
from pathlib import Path

from guide.export_glb import main as export_main, write_layup_files
from guide import layup
from guide.schema import load_graph


def test_nested_ply_nodes(tmp_path):
    out = export_components(
        {"canard.core": cq.Workplane().box(10, 2, 1),
         "canard.shear_web": {"canard.shear_web.p1": cq.Workplane().box(1, 1, 1),
                              "canard.shear_web.p2": cq.Workplane().box(1, 1, 2)}},
        tmp_path / "n.glb")
    names = read_glb_node_names(out)
    assert {"canard.core", "canard.shear_web", "canard.shear_web.p1", "canard.shear_web.p2"} <= set(names)


def test_layup_files_match_the_graph(tmp_path):
    g = load_graph(Path("guide/graph"))
    write_layup_files(g, tmp_path)
    j = json.loads((tmp_path / "layup.json").read_text())
    assert set(j["nodes"]) == {p.node for p in layup.plies(g)}
    assert json.loads((tmp_path / "shots.json").read_text()) == layup.shots()


def test_real_export_is_deterministic_and_complete(tmp_path):
    shas = []
    for i in (1, 2):
        export_main(["--out", str(tmp_path / f"r{i}" / "longez.glb")])
        shas.append(hashlib.sha256((tmp_path / f"r{i}" / "longez.glb").read_bytes()).hexdigest())
    assert shas[0] == shas[1]
    names = set(read_glb_node_names(tmp_path / "r1" / "longez.glb"))
    nodes = set(json.loads((tmp_path / "r1" / "layup.json").read_text())["nodes"])
    assert nodes <= names and "canard.core" in names
```

- [ ] **Step 2: Run to confirm they fail**

Run: `.venv/bin/python -m pytest tests/guide/test_export_glb.py -q`
Expected: ImportError (`write_layup_files`).

- [ ] **Step 3: Implement**

Replace `export_components`, `default_components` and `main` in `guide/export_glb.py`:

```python
GRAPH_DIR = Path(__file__).parent / "graph"


def export_components(components: dict, out: Path) -> Path:
    """Top-level keys are component ids. A dict value becomes a sub-assembly named by the component
    id whose children are named by ply node, so the viewer's parent walk resolves every ply."""
    out.parent.mkdir(parents=True, exist_ok=True)
    assy = cq.Assembly(name="longez")
    for cid, v in components.items():
        if isinstance(v, dict):
            sub = cq.Assembly(name=cid)
            for node, shape in v.items():
                sub.add(shape, name=node)
            assy.add(sub, name=cid)
        else:
            assy.add(v, name=cid)
    assy.export(str(out), exportType="GLTF")
    return out


def default_components() -> dict:
    from guide.layup_geometry import build_layup
    from guide.schema import load_graph

    return build_layup(load_graph(GRAPH_DIR))


def write_layup_files(graph, out_dir: Path) -> None:
    from core.structures import CanardGenerator
    from guide import layup

    pl = layup.plies(graph)
    lj = layup.layup_json(pl, CanardGenerator().span / 2)
    (out_dir / "layup.json").write_text(json.dumps(lj, indent=1, sort_keys=True))
    (out_dir / "shots.json").write_text(json.dumps(layup.shots(), indent=1))


def main(argv: list[str] | None = None) -> int:
    from guide.schema import load_graph

    ap = argparse.ArgumentParser(prog="guide.export_glb")
    ap.add_argument("--out", default="output/guide/longez.glb")
    a = ap.parse_args(argv)
    out = export_components(default_components(), Path(a.out))
    write_layup_files(load_graph(GRAPH_DIR), out.parent)
    print(f"wrote {out} (+ layup.json, shots.json) nodes={len(read_glb_node_names(out))}")
    return 0
```

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/guide/test_export_glb.py tests/guide/test_viewer_e2e.py -q`
Expected: all PASS. The e2e confirms M1's viewer still maps meshes; its fixture uses a flat dict.
- If `test_nested_ply_nodes` shows names prefixed (for example `canard.shear_web/canard.shear_web.p1`),
  make `read_glb_node_names` return the last `/`-segment. Also make app.js's `nm()` do the same in
  Task 11, and note it in the commit.

- [ ] **Step 5: Commit**

```bash
git add guide/export_glb.py tests/guide/test_export_glb.py
git commit -m "feat(guide): export ply nodes under their components, plus layup.json and shots.json"
```

---

### Task 5: Blender job: shared helper, contract, cutaway script (the render-tooling repo)

Work in `<render-tooling repo>`. Check `git status` first, and never commit another lane's files.

**Files:**
- Create: `deploy/<gpu-host>/jobs/blender/fabric_blender.py`, `deploy/<gpu-host>/jobs/blender/layup_contract.py`,
  `deploy/<gpu-host>/jobs/blender/layup_cutaway.py`
- Modify: `deploy/<gpu-host>/jobs/blender/smoke.py`
- Test: `deploy/<gpu-host>/tests/test_layup_contract.py`

**Interfaces:**
- Consumes: the job dir `in/` with `longez.glb`, `layup.json` (Task 2 `layup_json` shape) and
  `shots.json` (Task 2 `shots` shape).
- Produces, in `out/`: `<shot id>.png` (1600×1200, transparent background), `log.txt`, and
  `manifest.json` written LAST:
  `{"inputs": {"longez.glb": sha, "layup.json": sha, "shots.json": sha, "layup_cutaway.py": sha,
  "fabric_blender.py": sha, "layup_contract.py": sha}, "shots": {id: {"file": "<id>.png", "sha256": sha}}}`.

- [ ] **Step 1: Write the failing contract tests**

```python
# deploy/<gpu-host>/tests/test_layup_contract.py
"""layup_contract: pure logic of the cutaway job (runs on a Mac, no bpy)."""
import json
import re
import sys
from pathlib import Path

import pytest

JOBS = Path(__file__).parent.parent / "jobs"
sys.path.insert(0, str(JOBS / "blender"))
import layup_contract as lc  # noqa: E402

SHOTS = [{"id": "hero-bl5", "kind": "hero", "bl": 5.0, "highlight": None, "upto": None},
         {"id": "op-r30-bottom-skin", "kind": "op", "bl": 5.0, "highlight": "r30.bottom-skin", "upto": 2}]
LAYUP = {"ops": ["r30.shear-web", "r30.bottom-spar-cap", "r30.bottom-skin"],
         "nodes": {"canard.shear_web.p1": {"component": "canard.shear_web", "op": "r30.shear-web", "op_index": 0,
                                           "order": 1, "cloth": "UND", "position_verified": False},
                   "canard.skin_bottom.p2": {"component": "canard.skin_bottom", "op": "r30.bottom-skin",
                                             "op_index": 2, "order": 2, "cloth": "BID", "position_verified": True}}}


def write_inputs(d: Path, shots=SHOTS, lay=LAYUP):
    d.mkdir(parents=True, exist_ok=True)
    (d / "shots.json").write_text(json.dumps(shots)); (d / "layup.json").write_text(json.dumps(lay))
    (d / "longez.glb").write_bytes(b"glTF")


def test_load_inputs_ok(tmp_path):
    write_inputs(tmp_path)
    lay, shots = lc.load_inputs(tmp_path)
    assert [s["id"] for s in shots] == ["hero-bl5", "op-r30-bottom-skin"]


@pytest.mark.parametrize("bad", [{"id": "op-r30.x"}, {"kind": "movie"}, {"bl": "five"}])
def test_load_inputs_rejects_bad_shots(tmp_path, bad):
    write_inputs(tmp_path, shots=[{**SHOTS[0], **bad}])
    with pytest.raises(lc.ContractError):
        lc.load_inputs(tmp_path)


def test_visibility():
    web, skin = LAYUP["nodes"]["canard.shear_web.p1"], LAYUP["nodes"]["canard.skin_bottom.p2"]
    assert lc.visibility(web, SHOTS[0]) == "normal"
    assert lc.visibility(skin, SHOTS[1]) == "accent"
    assert lc.visibility(web, SHOTS[1]) == "normal"
    assert lc.visibility(skin, {**SHOTS[1], "upto": 1}) == "hidden"


def test_shades_alternate_and_match_css_hexes():
    assert lc.HEX["UND"] == ("#d9962b", "#a8681a") and lc.HEX["BID"] == ("#3a9e98", "#1f7a75")
    assert lc.shade_hex("UND", 1) != lc.shade_hex("UND", 2) and lc.shade_hex("UND", 1) == lc.shade_hex("UND", 3)
    r, g, b = lc.srgb_to_linear("#ffffff")
    assert (r, g, b) == pytest.approx((1.0, 1.0, 1.0))


@pytest.mark.parametrize("name,node", [("canard.shear_web.p1", "canard.shear_web.p1"),
                                        ("canard.shear_web.p1.001", "canard.shear_web.p1"),
                                        ("canard.core", "canard.core")])
def test_resolve_node(name, node):  # Review Focus 2
    assert lc.resolve_node(name, set(LAYUP["nodes"]) | {"canard.core"}) == node


def test_resolve_node_unmapped_fails():
    with pytest.raises(lc.ContractError):
        lc.resolve_node("Cube", {"canard.core"})


def test_check_axes():  # Review Focus 1
    lc.check_axes(ymin=0.0, ymax=73.5, expected_semi_span=73.5)
    with pytest.raises(lc.ContractError):
        lc.check_axes(ymin=-1.0, ymax=2.0, expected_semi_span=73.5)


def test_manifest_lists_inputs_scripts_and_shots(tmp_path):
    write_inputs(tmp_path / "in")
    png = tmp_path / "out" / "hero-bl5.png"; png.parent.mkdir(); png.write_bytes(b"png")
    m = lc.manifest(tmp_path / "in", JOBS / "blender", {"hero-bl5": png})
    assert set(m["inputs"]) == {"longez.glb", "layup.json", "shots.json",
                                "layup_cutaway.py", "fabric_blender.py", "layup_contract.py"}
    assert m["shots"]["hero-bl5"]["file"] == "hero-bl5.png" and len(m["shots"]["hero-bl5"]["sha256"]) == 64


def test_gpu_guard_lives_only_in_fabric_blender():  # DRY guard for the safety check
    for f in ("smoke.py", "layup_cutaway.py"):
        src = (JOBS / "blender" / f).read_text()
        assert "compute_device_type" not in src and "from fabric_blender import" in src, f
    assert "compute_device_type" in (JOBS / "blender" / "fabric_blender.py").read_text()


def test_script_names_pass_blender_sh_regex():
    for f in ("layup_cutaway.py", "smoke.py"):
        assert re.fullmatch(r"[a-z0-9_]+", Path(f).stem)
```

- [ ] **Step 2: Run to confirm failure**

Run: `cd <render-tooling repo> && python3 -m pytest deploy/<gpu-host>/tests/test_layup_contract.py -q`
Expected: ImportError (`layup_contract`).

- [ ] **Step 3: Write `layup_contract.py`**

```python
# deploy/<gpu-host>/jobs/blender/layup_contract.py — pure logic of the layup cutaway job (no bpy).
"""Inputs, visibility, colours and the manifest for layup_cutaway.py; unit-tested on a laptop."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SHOT_ID = re.compile(r"[a-z0-9-]+")
KINDS = {"hero", "op"}
# sRGB hexes; guide/viewer/css/app.css --und/--und2/--bid/--bid2/--foam use the same values.
HEX = {"UND": ("#d9962b", "#a8681a"), "BID": ("#3a9e98", "#1f7a75"), "FOAM": ("#dcdcd6", "#dcdcd6")}
SCRIPTS = ("layup_cutaway.py", "fabric_blender.py", "layup_contract.py")
DATA = ("longez.glb", "layup.json", "shots.json")


class ContractError(RuntimeError):
    pass


def load_inputs(inp: Path) -> tuple[dict, list[dict]]:
    for f in DATA:
        if not (inp / f).is_file():
            raise ContractError(f"missing input {f}")
    lay = json.loads((inp / "layup.json").read_text())
    shots = json.loads((inp / "shots.json").read_text())
    for s in shots:
        if not SHOT_ID.fullmatch(str(s.get("id", ""))):
            raise ContractError(f"bad shot id {s.get('id')!r}")
        if s.get("kind") not in KINDS:
            raise ContractError(f"bad shot kind {s.get('kind')!r}")
        if not isinstance(s.get("bl"), (int, float)):
            raise ContractError(f"bad shot bl {s.get('bl')!r}")
    return lay, shots


def visibility(node: dict, shot: dict) -> str:
    if shot["kind"] == "hero":
        return "normal"
    if node["op_index"] > shot["upto"]:
        return "hidden"
    return "accent" if node["op"] == shot["highlight"] else "normal"


def shade_hex(cloth: str, order: int) -> str:
    return HEX[cloth][(order - 1) % 2]


def srgb_to_linear(hexcode: str) -> tuple[float, float, float]:
    def ch(v: float) -> float:
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    h = hexcode.lstrip("#")
    return tuple(ch(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))


def resolve_node(name: str, nodes: set[str]) -> str:
    if name in nodes:
        return name
    base = re.sub(r"\.\d{3}$", "", name)
    if base in nodes:
        return base
    raise ContractError(f"mesh {name!r} maps to no layup node")


def check_axes(ymin: float, ymax: float, expected_semi_span: float) -> None:
    if abs((ymax - ymin) - expected_semi_span) > 0.05 * expected_semi_span or ymin < -1.0:
        raise ContractError(f"scene Y extent {ymin:.2f}..{ymax:.2f} is not 0..{expected_semi_span:.1f}: "
                            "glTF axis/units conversion changed; the BL cut would land on the wrong plane")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def manifest(inp: Path, script_dir: Path, shot_files: dict[str, Path]) -> dict:
    inputs = {f: sha256(inp / f) for f in DATA}
    inputs.update({f: sha256(script_dir / f) for f in SCRIPTS})
    return {"inputs": inputs,
            "shots": {sid: {"file": p.name, "sha256": sha256(p)} for sid, p in shot_files.items()}}
```

- [ ] **Step 4: Write `fabric_blender.py` (moves the GPU guard out of smoke.py)**

```python
# deploy/<gpu-host>/jobs/blender/fabric_blender.py — shared bpy helpers for fabric Blender jobs.
"""GPU guard, scene reset and section-cut helpers. Payload scripts import this; the GPU guard lives
ONLY here (a copy would drift and one script could fall back to CPU unnoticed)."""
import os

import bpy


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def gpu_setup(scene) -> str:
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    device = "CPU"
    for dtype in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = dtype
        except TypeError:
            continue
        prefs.get_devices()
        if [d for d in prefs.devices if d.type == dtype]:
            for d in prefs.devices:
                d.use = d.type == dtype
            device = dtype
            break
    if device != "CPU" and not prefs.has_active_device():
        device = "CPU"
    scene.cycles.device = "GPU" if device != "CPU" else "CPU"
    print(f"CYCLES_DEVICE={device}", flush=True)
    if device == "CPU" and os.environ.get("BLENDER_REQUIRE_GPU", "1") == "1":
        raise RuntimeError("no OPTIX/CUDA device visible to Blender; refusing CPU render")
    return device


def solidify_if_thin(o, thickness: float) -> None:
    dims = o.dimensions
    if min(dims) < 1e-4:
        m = o.modifiers.new("thicken", "SOLIDIFY")
        m.thickness = thickness


def section_cut(objs, cutter) -> None:
    for o in objs:
        m = o.modifiers.new("section", "BOOLEAN")
        m.operation, m.object, m.solver = "DIFFERENCE", cutter, "MANIFOLD"
```

- [ ] **Step 5: Refactor `smoke.py` onto the helper**

Replace the device-selection block (from `scene.render.engine = "CYCLES"` through the `raise
RuntimeError(...)`) with:

```python
scene = bpy.context.scene
device = gpu_setup(scene)
```

Replace the per-object SOLIDIFY + BOOLEAN loop with the two calls below. Keep the smoke's
unconditional thicken, because its fixture glb may be a surface:

```python
for o in meshes:
    sol = o.modifiers.new("thicken", "SOLIDIFY"); sol.thickness = max(span, 1e-6) * 0.005
section_cut(meshes, cutter)
```

At the top, after `import bpy`, add:

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fabric_blender import gpu_setup, section_cut  # noqa: E402
```

- [ ] **Step 6: Write `layup_cutaway.py`**

```python
# deploy/<gpu-host>/jobs/blender/layup_cutaway.py — Long-EZ layup cutaway renders (open-ez guide M2).
"""Render every shot in in/shots.json from in/longez.glb, coloured per in/layup.json.

    for shot: reset → import glb → map meshes to layup nodes → colour/hide/accent
              → cut at y = BL (keep outboard) → frame from the cut face → render out/<id>.png
    then: out/manifest.json LAST (the laptop treats a missing manifest as a failed run)
"""
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fabric_blender import gpu_setup, reset_scene, section_cut, solidify_if_thin  # noqa: E402
import layup_contract as lc  # noqa: E402

JOB = Path(sys.argv[sys.argv.index("--") + 1])
INP, OUT = JOB / "in", JOB / "out"
HERE = Path(os.path.dirname(os.path.abspath(__file__)))
_log = open(OUT / "log.txt", "a")


def log(msg: str) -> None:
    print(msg, flush=True); _log.write(msg + "\n"); _log.flush()


def material(name: str, hexcode: str, emission: float = 0.0, stripes: bool = False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    rgb = (*lc.srgb_to_linear(hexcode), 1.0)
    bsdf.inputs["Base Color"].default_value = rgb
    bsdf.inputs["Roughness"].default_value = 0.8
    if emission:
        bsdf.inputs["Emission Color"].default_value = rgb
        bsdf.inputs["Emission Strength"].default_value = emission
    if stripes:  # "position not verified": diagonal stripes of the base and a darker tone
        wave = nt.nodes.new("ShaderNodeTexWave"); wave.inputs["Scale"].default_value = 3.0
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
        mix.inputs[6].default_value = rgb
        mix.inputs[7].default_value = tuple(c * 0.55 for c in rgb[:3]) + (1.0,)
        nt.links.new(wave.outputs["Fac"], mix.inputs[0])
        nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return m


def section_bounds(objs, bl: float):
    dg = bpy.context.evaluated_depsgraph_get()
    xs, zs = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        for v in me.vertices:
            w = ev.matrix_world @ v.co
            if abs(w.y - bl) < 1e-3:
                xs.append(w.x); zs.append(w.z)
        ev.to_mesh_clear()
    if not xs:
        raise lc.ContractError(f"cut at BL {bl} produced no section face")
    return min(xs), max(xs), min(zs), max(zs)


def band_centre(o, bl: float):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh()
    pts = [ev.matrix_world @ v.co for v in me.vertices if abs((ev.matrix_world @ v.co).y - bl) < 1e-3]
    ev.to_mesh_clear()
    return sum(pts, Vector()) / len(pts) if pts else None


def render_shot(shot, lay, semi_span: float) -> Path:
    reset_scene()
    scene = bpy.context.scene
    gpu_setup(scene)
    bpy.ops.import_scene.gltf(filepath=str(INP / "longez.glb"))
    meshes = [o for o in scene.objects if o.type == "MESH"]
    ys = [(o.matrix_world @ Vector(c)).y for o in meshes for c in o.bound_box]
    lc.check_axes(min(ys), max(ys), semi_span)
    nodes = set(lay["nodes"]) | {"canard.core"}
    shown = []
    for o in meshes:
        node = lc.resolve_node(o.name, nodes)
        info = lay["nodes"].get(node)
        o.data.materials.clear()
        if info is None:  # foam
            o.data.materials.append(material("foam", lc.HEX["FOAM"][0])); shown.append(o); continue
        vis = lc.visibility(info, shot)
        if vis == "hidden":
            o.hide_render = True; continue
        o.data.materials.append(material(node, lc.shade_hex(info["cloth"], info["order"]),
                                         emission=0.6 if vis == "accent" else 0.0,
                                         stripes=not info["position_verified"]))
        solidify_if_thin(o, 0.02)
        shown.append(o)
    bl = float(shot["bl"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bl - 500, 0))
    cutter = bpy.context.active_object; cutter.scale = (2000, 1000, 2000); cutter.hide_render = True
    section_cut(shown, cutter)
    x0, x1, z0, z1 = section_bounds(shown, bl)
    cx, cz, w, h = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam)
    scene.camera = cam
    if shot["kind"] == "hero":  # straight along the span, orthographic: best for counting bands
        cam.data.type = "ORTHO"; cam.data.ortho_scale = max(w, h * 4 / 3) * 1.08
        cam.location = (cx, bl - 50, cz); cam.rotation_euler = (math.pi / 2, 0, 0)
        for o in shown:
            c = band_centre(o, bl)
            info = lay["nodes"].get(lc.resolve_node(o.name, nodes))
            if c is None or info is None:
                continue
            bpy.ops.object.text_add(location=(c.x, bl - 0.05, c.z), rotation=(math.pi / 2, 0, 0))
            t = bpy.context.active_object; t.data.body = str(info["order"]); t.data.size = 0.09
            t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
            t.data.materials.append(material("label", "#1d1d1b"))
    else:  # 3/4 perspective toward the section face
        target = bpy.data.objects.new("target", None); scene.collection.objects.link(target)
        target.location = (cx, bl, cz)
        cam.location = (cx - 0.9 * w, bl - 1.4 * w, cz + 0.7 * w)
        tr = cam.constraints.new("TRACK_TO"); tr.target = target
        tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.rotation_euler = (math.radians(60), 0, math.radians(-30)); sun.data.energy = 3.0
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("w"); world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1.0)
    scene.world = world
    scene.render.film_transparent = True
    scene.cycles.samples = 64
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1200
    out = OUT / f"{shot['id']}.png"
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    log(f"SHOT_OK {shot['id']} bl={bl} section={w:.2f}x{h:.2f}")
    return out


def main() -> None:
    import json
    lay, shots = lc.load_inputs(INP)
    semi_span = float(lay["semi_span"])
    files = {s["id"]: render_shot(s, lay, semi_span) for s in shots}
    (OUT / "manifest.json").write_text(json.dumps(lc.manifest(INP, HERE, files), indent=1))
    log(f"LAYUP_CUTAWAY_OK shots={len(files)}")


main()
```

- [ ] **Step 7: Run both suites**

Run: `cd <render-tooling repo> && python3 -m pytest deploy/<gpu-host>/tests -q`. Expected: all PASS,
including the existing `test_blender_payload.py`.
Run: `python3 -c "import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" deploy/<gpu-host>/jobs/blender/*.py`
(in the render-tooling repo). Expected: no output. It only checks that the bpy scripts parse; bpy itself
runs on the GPU host only.

- [ ] **Step 8: Commit**

```bash
cd <render-tooling repo>
git add deploy/<gpu-host>/jobs/blender/fabric_blender.py deploy/<gpu-host>/jobs/blender/layup_contract.py \
        deploy/<gpu-host>/jobs/blender/layup_cutaway.py deploy/<gpu-host>/jobs/blender/smoke.py \
        deploy/<gpu-host>/tests/test_layup_contract.py
git commit -m "feat(blender): layup cutaway job; GPU guard moved into shared fabric_blender"
```

---

### Task 6: Render key + `render_cutaway.sh`

**Files:**
- Create: `guide/render_key.py`, `guide/render_cutaway.sh` (chmod +x)
- Test: `tests/guide/test_render_key.py`, `tests/guide/test_render_cutaway.py`

**Interfaces:**
- Consumes: `output/guide/{longez.glb,layup.json,shots.json}`; the Blender scripts at
  `$OPENEZ_BLENDER_SCRIPTS/deploy/<gpu-host>/jobs/blender/`; the Task 5 manifest shape.
- Produces:
  - `render_key.file_shas(export_dir: Path, scripts_dir: Path | None) -> dict[str, str]`
  - `render_key.key_of(shas: dict[str, str]) -> str`
  - `render_key.check_renders(renders: Path, export_dir: Path, scripts_dir: Path | None = None) -> list[str]`
  - CLI: `python -m guide.render_key --export DIR --scripts DIR` prints the key.
    `--check RENDERS` exits 1 and prints the problems if there are any.
  - Script: `guide/render_cutaway.sh [--only SHOT_ID] [--dry-run]`. Exit codes: 0 ok, 2 usage or
    missing inputs, 3 lease busy, 4 deployed-script mismatch, 5 render check failed, any other code is
    gpu-runner's.

- [ ] **Step 1: Write the failing tests**

```python
# tests/guide/test_render_key.py
import json
from pathlib import Path

from guide import render_key as rk

SCRIPTS = ("layup_cutaway.py", "fabric_blender.py", "layup_contract.py")


def make_export(d: Path, shots=None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "longez.glb").write_bytes(b"glTF-x"); (d / "layup.json").write_text('{"nodes":{}}')
    (d / "shots.json").write_text(json.dumps(shots or [{"id": "hero-bl5"}, {"id": "op-r30-top-skin"}]))
    return d


def make_scripts(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    for s in SCRIPTS:
        (d / s).write_text(f"# {s}\n")
    return d


def make_renders(d: Path, export: Path, scripts: Path, drop: str | None = None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    shots = {}
    for s in json.loads((export / "shots.json").read_text()):
        if s["id"] == drop:
            continue
        (d / f"{s['id']}.png").write_bytes(s["id"].encode())
        shots[s["id"]] = {"file": f"{s['id']}.png", "sha256": rk.sha256(d / f"{s['id']}.png")}
    (d / "manifest.json").write_text(json.dumps({"inputs": rk.file_shas(export, scripts), "shots": shots}))
    return d


def test_key_changes_with_any_input(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    k1 = rk.key_of(rk.file_shas(e, s))
    (s / "layup_cutaway.py").write_text("# changed\n")
    assert rk.key_of(rk.file_shas(e, s)) != k1
    (e / "shots.json").write_text("[]")
    assert len(rk.key_of(rk.file_shas(e, s))) == 64


def test_check_ok(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    assert rk.check_renders(make_renders(tmp_path / "r", e, s), e, s) == []


def test_check_missing_shot_and_stale_data(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    r = make_renders(tmp_path / "r", e, s, drop="op-r30-top-skin")
    assert any("op-r30-top-skin" in p for p in rk.check_renders(r, e, s))
    r2 = make_renders(tmp_path / "r2", e, s)
    (e / "layup.json").write_text('{"nodes":{"x":{}}}')
    assert any("layup.json" in p for p in rk.check_renders(r2, e, s))


def test_check_without_scripts_still_requires_script_shas(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    r = make_renders(tmp_path / "r", e, s)
    m = json.loads((r / "manifest.json").read_text()); del m["inputs"]["fabric_blender.py"]
    (r / "manifest.json").write_text(json.dumps(m))
    assert any("fabric_blender.py" in p for p in rk.check_renders(r, e, None))


def test_check_missing_manifest(tmp_path):
    e = make_export(tmp_path / "e"); (tmp_path / "r").mkdir()
    assert rk.check_renders(tmp_path / "r", e, None) == ["no manifest.json (incomplete render run)"]
```

```python
# tests/guide/test_render_cutaway.py
"""render_cutaway.sh with stub ssh/rsync/gpu-runner on PATH: every branch, no GPU, no the GPU host."""
import json
import os
import re
import stat
import subprocess
from pathlib import Path

import pytest

from guide import render_key as rk
from tests.guide.test_render_key import make_export, make_renders, make_scripts

SH = Path("guide/render_cutaway.sh").resolve()
STUB_SSH = r'''#!/bin/bash
host="$1"; shift; cmd="$*"; echo "ssh $cmd" >> "$STUB_LOG"
case "$cmd" in
  lease-status) if [ "${STUB_LEASE:-0}" = 3 ]; then echo "LEASED — held by w9-battery"; exit 3; fi; echo "FREE"; exit 0;;
  sha256sum*) f="${cmd##*/}"; if [ -n "${STUB_SHA_BAD:-}" ]; then echo "0000  x"; else shasum -a 256 "$STUB_SCRIPTS/$f"; fi;;
  "test -f"*) exit 0;;
  *) exit 0;;
esac
'''
STUB_RSYNC = r'''#!/bin/bash
echo "rsync $*" >> "$STUB_LOG"
src="${@: -2:1}"; dst="${@: -1}"
case "$src" in *:*/out/) cp -R "$STUB_OUT"/. "$dst";; esac
'''
STUB_GPU = r'''#!/bin/bash
printf '%s\n' "$@" > "$STUB_GPU_ARGS"; exit "${STUB_GPU_RC:-0}"
'''


def exe(p: Path, body: str) -> None:
    p.write_text(body); p.chmod(p.stat().st_mode | stat.S_IEXEC)


@pytest.fixture
def env(tmp_path):
    bin_ = tmp_path / "bin"; bin_.mkdir()
    exe(bin_ / "ssh", STUB_SSH); exe(bin_ / "rsync", STUB_RSYNC); exe(bin_ / "gpu-runner", STUB_GPU)
    cf = tmp_path / "cf"; scripts = make_scripts(cf / "deploy/<gpu-host>/jobs/blender")
    export = make_export(tmp_path / "export")
    out = make_renders(tmp_path / "render_out", export, scripts)
    e = dict(os.environ, PATH=f"{bin_}:{os.environ['PATH']}", OPENEZ_BLENDER_SCRIPTS=str(cf),
             FABRIC_GPU=str(bin_ / "gpu-runner"), LONGEZ_EXPORT_DIR=str(export),
             LONGEZ_RENDER_CACHE=str(tmp_path / "cache"), LONGEZ_POLL_S="0",
             PY=str(Path(".venv/bin/python").resolve()),
             STUB_LOG=str(tmp_path / "log"), STUB_SCRIPTS=str(scripts), STUB_OUT=str(out),
             STUB_GPU_ARGS=str(tmp_path / "gpu_args"))
    return e, tmp_path, export, scripts


def run(e, *args, **extra):
    return subprocess.run(["bash", str(SH), *args], env={**e, **extra}, capture_output=True, text=True)


def test_lease_busy_stops_before_dispatch(env):
    e, t, *_ = env
    r = run(e, STUB_LEASE="3")
    assert r.returncode == 3 and "GPU lease busy: LEASED" in r.stderr
    assert not (t / "gpu_args").exists()


def test_happy_path(env):
    e, t, export, scripts = env
    r = run(e)
    assert r.returncode == 0, r.stderr
    args = (t / "gpu_args").read_text().split()
    key = rk.key_of(rk.file_shas(export, scripts))
    assert args[:3] == ["run", "blender.sh", "layup_cutaway"] and re.fullmatch(r"[a-z0-9_]+", args[2])
    assert args[3].endswith(f"layup-{key[:16]}") and args[4:6] == ["--no-wait", "--expect-s"]
    assert (t / "cache" / key / "manifest.json").exists() and not (t / "cache" / f"{key}.tmp").exists()


def test_gpu_failure_leaves_no_cache(env):
    e, t, *_ = env
    r = run(e, STUB_GPU_RC="1")
    assert r.returncode == 1
    assert not (t / "cache").exists() or not any((t / "cache").iterdir())


def test_deployed_script_mismatch(env):
    e, t, *_ = env
    r = run(e, STUB_SHA_BAD="1")
    assert r.returncode == 4 and "redeploy" in r.stderr and not (t / "gpu_args").exists()


def test_only_filters_shots_and_changes_key(env):
    e, t, export, scripts = env
    r = run(e, "--only", "hero-bl5", "--dry-run")
    assert r.returncode == 0 and "would render" in r.stdout
    assert rk.key_of(rk.file_shas(export, scripts)) not in r.stdout
    assert run(e, "--only", "nope", "--dry-run").returncode == 2


def test_incomplete_renders_fail_check(env, tmp_path):
    e, t, export, scripts = env
    bad = make_renders(tmp_path / "bad_out", export, scripts, drop="hero-bl5")
    r = run(e, STUB_OUT=str(bad))
    assert r.returncode == 5 and "hero-bl5" in r.stderr
    key = rk.key_of(rk.file_shas(export, scripts))
    assert not (t / "cache" / key).exists()


def test_stale_tmp_is_replaced(env):  # Review Focus 5
    e, t, export, scripts = env
    key = rk.key_of(rk.file_shas(export, scripts))
    (t / "cache" / f"{key}.tmp").mkdir(parents=True); (t / "cache" / f"{key}.tmp" / "junk.png").write_bytes(b"x")
    assert run(e).returncode == 0
    assert not (t / "cache" / key / "junk.png").exists()
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/guide/test_render_key.py tests/guide/test_render_cutaway.py -q`
Expected: ImportError / missing script.

- [ ] **Step 3: Write `guide/render_key.py`**

```python
"""Render key: which inputs produced a set of cutaway renders, and are those renders complete?

key = sha256 over sorted "name sha256" lines of the data files (longez.glb, layup.json, shots.json)
and the Blender scripts. The laptop computes it; the Blender job records per-file shas in manifest.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DATA = ("longez.glb", "layup.json", "shots.json")
SCRIPTS = ("layup_cutaway.py", "fabric_blender.py", "layup_contract.py")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def file_shas(export_dir: Path, scripts_dir: Path | None) -> dict[str, str]:
    shas = {f: sha256(export_dir / f) for f in DATA}
    if scripts_dir is not None:
        shas.update({f: sha256(scripts_dir / f) for f in SCRIPTS})
    return shas


def key_of(shas: dict[str, str]) -> str:
    return hashlib.sha256("".join(f"{k} {shas[k]}\n" for k in sorted(shas)).encode()).hexdigest()


def check_renders(renders: Path, export_dir: Path, scripts_dir: Path | None = None) -> list[str]:
    mf = renders / "manifest.json"
    if not mf.is_file():
        return ["no manifest.json (incomplete render run)"]
    m = json.loads(mf.read_text())
    inputs, probs = m.get("inputs", {}), []
    for name, sha in file_shas(export_dir, scripts_dir).items():
        if inputs.get(name) != sha:
            probs.append(f"{name} changed since these renders (stale)")
    probs += [f"manifest lacks the {s} sha" for s in SCRIPTS if s not in inputs]
    for shot in json.loads((export_dir / "shots.json").read_text()):
        rec = m.get("shots", {}).get(shot["id"])
        png = renders / f"{shot['id']}.png"
        if rec is None or not png.is_file():
            probs.append(f"missing render for shot {shot['id']}")
        elif sha256(png) != rec["sha256"]:
            probs.append(f"render {shot['id']} does not match its manifest sha")
    return probs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.render_key")
    ap.add_argument("--export", type=Path, required=True)
    ap.add_argument("--scripts", type=Path, default=None)
    ap.add_argument("--check", type=Path, default=None, metavar="RENDERS")
    a = ap.parse_args(argv)
    if a.check:
        probs = check_renders(a.check, a.export, a.scripts)
        for p in probs:
            print(p, file=sys.stderr)
        return 1 if probs else 0
    print(key_of(file_shas(a.export, a.scripts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write `guide/render_cutaway.sh`**

```bash
#!/usr/bin/env bash
# Render the layup cutaway on the GPU host's GPU through gpu-runner. HITL only; never put this on a timer.
# usage: guide/render_cutaway.sh [--only SHOT_ID] [--dry-run]
# exit: 0 ok · 2 usage/missing inputs · 3 GPU lease busy · 4 deployed scripts differ · 5 render check failed
set -euo pipefail
ONLY=""; DRY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --only) ONLY="${2:?--only needs a shot id}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    *) echo "usage: render_cutaway.sh [--only SHOT_ID] [--dry-run]" >&2; exit 2 ;;
  esac
done
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
ANVIL=${LONGEZ_ANVIL:-the GPU host}
CF=${OPENEZ_BLENDER_SCRIPTS:-<render-tooling repo>}
FABRIC_GPU=${FABRIC_GPU:-$CF/bin/gpu-runner}
SCRIPTS=$CF/deploy/<gpu-host>/jobs/blender
EXPORT=${LONGEZ_EXPORT_DIR:-output/guide}
CACHE=${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}
POLL_S=${LONGEZ_POLL_S:-10}
DEPLOYED=<deployed scripts dir>/blender

for f in longez.glb layup.json shots.json; do
  [ -f "$EXPORT/$f" ] || { echo "missing $EXPORT/$f; run: $PY -m guide.export_glb" >&2; exit 2; }
done
STAGE=$(mktemp -d); trap 'rm -rf "$STAGE"' EXIT
cp "$EXPORT/longez.glb" "$EXPORT/layup.json" "$STAGE/"
if [ -n "$ONLY" ]; then
  $PY - "$EXPORT/shots.json" "$ONLY" "$STAGE/shots.json" <<'EOF' || exit 2
import json, sys
s = [x for x in json.load(open(sys.argv[1])) if x["id"] == sys.argv[2]]
if not s:
    sys.exit(f"no such shot: {sys.argv[2]}")
json.dump(s, open(sys.argv[3], "w"), indent=1)
EOF
else
  cp "$EXPORT/shots.json" "$STAGE/"
fi
KEY=$($PY -m guide.render_key --export "$STAGE" --scripts "$SCRIPTS")

for s in layup_cutaway.py fabric_blender.py layup_contract.py; do
  want=$(shasum -a 256 "$SCRIPTS/$s" | cut -d' ' -f1)
  got=$(ssh "$ANVIL" "sha256sum $DEPLOYED/$s" | cut -d' ' -f1)
  [ "$want" = "$got" ] || { echo "deployed $s differs from $SCRIPTS/$s; redeploy to the GPU host first" >&2; exit 4; }
done
if ! status=$(ssh "$ANVIL" lease-status); then echo "GPU lease busy: $status" >&2; exit 3; fi

JOB=<job root>/blender/layup-${KEY:0:16}
if [ -n "$DRY" ]; then echo "dry run: would render key $KEY into $JOB"; exit 0; fi
N=$($PY -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$STAGE/shots.json")
EXPECT=$((60 + 45 * N))
ssh "$ANVIL" "rm -rf $JOB && mkdir -p $JOB/in"
rsync -a "$STAGE/" "$ANVIL:$JOB/in/"
set +e; "$FABRIC_GPU" run blender.sh layup_cutaway "$JOB" --no-wait --expect-s "$EXPECT"; rc=$?; set -e
[ "$rc" = 0 ] || { echo "gpu-runner run failed rc=$rc (payload log: ssh $ANVIL cat $JOB/out/log.txt)" >&2; exit "$rc"; }

waited=0
until ssh "$ANVIL" "test -f $JOB/out/manifest.json"; do
  [ "$waited" -ge $((EXPECT + 300)) ] && { echo "no manifest after ${waited}s; see ssh $ANVIL cat $JOB/out/log.txt" >&2; exit 5; }
  sleep "$POLL_S"; waited=$((waited + POLL_S)); [ "$POLL_S" = 0 ] && waited=$((waited + 1))
done

DEST="$CACHE/$KEY"; TMP="$DEST.tmp"
rm -rf "$TMP"; mkdir -p "$TMP"
rsync -a "$ANVIL:$JOB/out/" "$TMP/"
if ! $PY -m guide.render_key --export "$STAGE" --scripts "$SCRIPTS" --check "$TMP"; then
  rm -rf "$TMP"; echo "render check failed for key $KEY" >&2; exit 5
fi
rm -rf "$DEST"; mv "$TMP" "$DEST"
echo "renders: $DEST"
```

Run `chmod +x guide/render_cutaway.sh`.

- [ ] **Step 5: Run the tests**

Run: `.venv/bin/python -m pytest tests/guide/test_render_key.py tests/guide/test_render_cutaway.py -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add guide/render_key.py guide/render_cutaway.sh tests/guide/test_render_key.py tests/guide/test_render_cutaway.py
git commit -m "feat(guide): render key and render_cutaway.sh (lease check, atomic pull, stub-tested)"
```

---

### Task 7: First live run: one hero, then Ryan's gate (session 1 ends here)

**Files:** none. This task is operations plus a human gate.

- [ ] **Step 1: Export**

Run: `cd ~/open-ez && .venv/bin/python -m guide.export_glb`
Expected: `wrote output/guide/longez.glb (+ layup.json, shots.json) nodes=…`.

- [ ] **Step 2: Deploy the Blender scripts to the GPU host**

This is the same install the M1 payload used (the render-tooling repo plan 2026-09-28, deploy step):

```bash
cd <render-tooling repo>/deploy/<gpu-host>/jobs/blender
scp fabric_blender.py layup_contract.py layup_cutaway.py smoke.py <gpu-host>:/tmp/
ssh <gpu-host> 'sudo install -o root -g root -m 644 /tmp/fabric_blender.py /tmp/layup_contract.py \
  /tmp/layup_cutaway.py /tmp/smoke.py <deployed scripts dir>/blender/ && ls -l <deployed scripts dir>/blender/'
```

- [ ] **Step 3: Re-prove the refactored smoke**

```bash
ssh <gpu-host> 'rm -rf <job root>/blender/smoke-m2 && mkdir -p <job root>/blender/smoke-m2/in'
<render-tooling repo>/bin/gpu-runner run blender.sh smoke <job root>/blender/smoke-m2 --no-wait --expect-s 300
```

Expected: `CYCLES_DEVICE=OPTIX`, `GPU_JOB_RESULT rc=0 restore=restored`.
- If the lease is busy (exit 3), stop and tell Ryan who holds it. Do not wait in a loop.

- [ ] **Step 4: Render the BL 5 hero only**

Run: `cd ~/open-ez && guide/render_cutaway.sh --only hero-bl5`
Expected: `renders: ~/.cache/long-ez/renders/<key>`.
- On failure, read `ssh <gpu-host> cat <job root>/blender/layup-<key16>/out/log.txt`. A `check_axes`
  error means the glTF axis conversion does not cancel. In that case, fix the axis mapping in
  `render_shot` by rotating the imported root −90° about X. Do not weaken the check.

- [ ] **Step 5: Confirm vLLM came back**

Run: `curl -s http://the local-model gateway/v1/models | head -c 300`, or the fabric identity probe the M1
payload plan used. Expected: the GPU host's model is listed. Record the output.

- [ ] **Step 6: Put the hero in front of Ryan**

```bash
source ~/.config/long-ez/env
ssh "$LONGEZ_DEPLOY_HOST" 'mkdir -p <site root>/site/mockups/m2'
scp ~/.cache/long-ez/renders/<key>/hero-bl5.png "$LONGEZ_DEPLOY_HOST":<site root>/site/mockups/m2/
curl -fsS -o /dev/null -w '%{http_code}\n' "$LONGEZ_SITE_URL/mockups/m2/hero-bl5.png"
```

Ask Ryan, on the iPad at `$LONGEZ_SITE_URL/mockups/m2/hero-bl5.png`: "Can you count bottom skin 3,
top skin 4 and shear web 6?"
- **Pass:** continue to session 2.
- **Fail:** switch the hero to a flat SVG made from the same CadQuery slice. Add a Task 7b: write
  `guide/section_svg.py`, which takes `build_layup` solids, runs `.section()` at y=BL and writes an
  SVG with the same hexes. It is tested by counting `<path>` elements per component. Blender keeps
  the op frames. Record the decision in the spec §8.

---

# Session 2: full renders, strict build, deploy (Tasks 8–10)

### Task 8: `build_site`: plies in graph.json; optional strict `--renders`

**Files:**
- Modify: `guide/build_site.py`
- Test: `tests/guide/test_build_site.py` (add tests), `tests/guide/render_fixture.py` (new helper)

**Interfaces:**
- Consumes: `guide.render_key.check_renders`, `guide.layup` (`plies`, `shots`, `alt_text`,
  `count_note`, `HERO_BLS`), and `layup.json` next to `--models`.
- Produces: `build(graph_dir, out, models, scan_base, docs, renders=None)`. graph.json gains:
  - `"plies": {cid: [{"node","order","cloth","where","position_verified"}]}`, present only when
    `models/../layup.json` exists
  - `"cutaway": null | {"ops": {op_id: {"src","alt"}}, "heroes": [{"bl","src","alt"}], "legend": [{"swatch","text"}], "count_note": str}`
  - The site gets `renders/<shot>.png`.

- [ ] **Step 1: Write the fixture helper and failing tests**

```python
# tests/guide/render_fixture.py
"""A small but real export dir + renders dir that pass render_key.check_renders."""
import json
from pathlib import Path

import cadquery as cq

from guide import layup, render_key as rk
from guide.export_glb import export_components
from guide.schema import load_graph

PNG_1PX = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                        "1f15c4890000000d49444154789c6360f80f0000010100005a4d6e2e0000000049454e44ae426082")


def make_export(d: Path) -> Path:
    g = load_graph(Path("guide/graph"))
    pl = layup.plies(g)
    comps = {"canard.core": cq.Workplane().box(10, 2, 1)}
    for i, p in enumerate(pl):
        comps.setdefault(p.component, {})[p.node] = cq.Workplane().box(1, 1, 1).translate((i * 1.5, 0, 2))
    export_components(comps, d / "longez.glb")
    (d / "layup.json").write_text(json.dumps(layup.layup_json(pl, 73.5)))
    (d / "shots.json").write_text(json.dumps(layup.shots()))
    return d


def make_renders(d: Path, export: Path, drop: str | None = None, bad_png: str | None = None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    shots = {}
    for s in layup.shots():
        if s["id"] == drop:
            continue
        p = d / f"{s['id']}.png"; p.write_bytes(PNG_1PX)
        shots[s["id"]] = {"file": p.name, "sha256": rk.sha256(p)}
        if s["id"] == bad_png:
            p.write_bytes(b"not a png")  # manifest sha no longer matches
    inputs = rk.file_shas(export, None) | {s: "0" * 64 for s in rk.SCRIPTS}
    (d / "manifest.json").write_text(json.dumps({"inputs": inputs, "shots": shots}))
    return d
```

Append to `tests/guide/test_build_site.py`:

```python
from pathlib import Path as _P
from tests.guide.render_fixture import make_export, make_renders

REPO_GRAPH = _P("guide/graph")


def test_no_renders_means_m1_output(tmp_path):  # CRITICAL regression: M1 builds unchanged
    e = make_export(tmp_path / "e")
    build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["cutaway"] is None and not (tmp_path / "site" / "renders").exists()
    assert [p["order"] for p in g["plies"]["canard.skin_top"]] == [1, 2, 3, 4]


def test_no_models_no_plies(gdir, tmp_path):
    build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["plies"] == {} and g["cutaway"] is None


def test_renders_wired(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    c = g["cutaway"]
    assert c["ops"]["r30.bottom-skin"]["src"] == "renders/op-r30-bottom-skin.png"
    assert [h["bl"] for h in c["heroes"]] == [5.0, 40.0]
    assert c["heroes"][0]["alt"].startswith("Section at BL 5: bottom skin 3 plies")
    assert "shear web 6 at BL 5, 2 at BL 40" in c["count_note"]
    assert (tmp_path / "site" / "renders" / "hero-bl40.png").exists()


@pytest.mark.parametrize("kw,needle", [({"drop": "hero-bl40"}, "hero-bl40"),
                                       ({"bad_png": "op-r30-top-skin"}, "op-r30-top-skin")])
def test_renders_strict(tmp_path, kw, needle):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e, **kw)
    with pytest.raises(SchemaError, match=needle):
        build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)


def test_renders_stale_layup(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    (e / "layup.json").write_text((e / "layup.json").read_text().replace('"semi_span": 73.5', '"semi_span": 70'))
    with pytest.raises(SchemaError, match="layup.json"):
        build(REPO_GRAPH, tmp_path / "site", models=e / "longez.glb", scan_base=None, docs=None, renders=r)


def test_renders_need_models(tmp_path):
    with pytest.raises(SchemaError, match="--renders needs --models"):
        build(REPO_GRAPH, tmp_path / "site", models=None, scan_base=None, docs=None, renders=tmp_path)
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/guide/test_build_site.py -q`
Expected: failures on the `plies`/`cutaway` keys and the `renders=` kwarg.

- [ ] **Step 3: Implement** (in `guide/build_site.py`)

Add these imports: `from guide import layup, render_key`.

Add these functions:

```python
LEGEND = [
    {"swatch": "und", "text": "UND (unidirectional): light and dark alternate by ply"},
    {"swatch": "bid", "text": "BID (biaxial): light and dark alternate by ply"},
    {"swatch": "foam", "text": "Foam core"},
    {"swatch": "unverified", "text": "Striped: web/spar position not verified"},
    {"swatch": None, "text": "Numbers = lay order"},
    {"swatch": None, "text": "Spar caps: plies as required to fill trough"},
    {"swatch": None, "text": "Not to scale"},
]


def _plies(models: Path | None) -> dict:
    lj = models.parent / "layup.json" if models else None
    if not lj or not lj.is_file():
        return {}
    out: dict = {}
    for node, n in json.loads(lj.read_text())["nodes"].items():
        out.setdefault(n["component"], []).append(
            {"node": node, "order": n["order"], "cloth": n["cloth"], "where": n["where"],
             "position_verified": n["position_verified"]})
    for rows in out.values():
        rows.sort(key=lambda r: r["order"])
    return out


def _cutaway(g, models: Path, renders: Path, out: Path) -> dict:
    probs = render_key.check_renders(renders, models.parent, None)
    if probs:
        raise SchemaError("renders: " + "; ".join(probs))
    pl = layup.plies(g)
    (out / "renders").mkdir()
    shots = json.loads((models.parent / "shots.json").read_text())
    for s in shots:
        shutil.copy(renders / f"{s['id']}.png", out / "renders" / f"{s['id']}.png")
    src = lambda s: f"renders/{s['id']}.png"  # noqa: E731
    return {
        "ops": {s["highlight"]: {"src": src(s), "alt": layup.alt_text(g, pl, s)} for s in shots if s["kind"] == "op"},
        "heroes": [{"bl": s["bl"], "src": src(s), "alt": layup.alt_text(g, pl, s)} for s in shots if s["kind"] == "hero"],
        "legend": LEGEND,
        "count_note": layup.count_note(pl),
    }
```

Change `build`'s signature to
`def build(graph_dir, out, models, scan_base, docs, renders: Path | None = None) -> None:`.
At the top of the function body add:

```python
    if renders and not models:
        raise SchemaError("--renders needs --models (the renders are checked against its layup.json/shots.json)")
```

Add to `payload`:

```python
        "plies": _plies(models),
        "cutaway": None,
```

After `shutil.copytree(...)` and before writing graph.json, add:

```python
    if renders:
        payload["cutaway"] = _cutaway(g, models, renders, out)
```

In `main`, add `ap.add_argument("--renders", type=Path, default=None)` and pass `renders=a.renders`.

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/python -m pytest tests/guide/test_build_site.py tests/guide/test_viewer_e2e.py -q`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add guide/build_site.py tests/guide/test_build_site.py tests/guide/render_fixture.py
git commit -m "feat(guide): build_site --renders (strict when given) and ply rows in graph.json"
```

---

### Task 9: Viewer: 3D/Cutaway toggle, glance view, states, tokens (spec §6.1–6.3)

**Files:**
- Create: `guide/viewer/js/cutaway.js`, `guide/viewer/tests/cutaway.test.mjs`
- Modify: `guide/viewer/index.html`, `guide/viewer/js/app.js`, `guide/viewer/css/app.css`
- Test: `tests/guide/test_viewer_e2e.py` (add tests)

**Interfaces:**
- Consumes: graph.json `cutaway` and `plies` (Task 8).
- Produces:
  - Exports from `cutaway.js`: `GLANCE = "__glance"`, `VIEW_KEY = "longez.view"`,
    `cutawayFor(graph, opId)`, `hasGlance(graph)`, `readView(storage)`, `writeView(storage, v)`,
    `paneMode(graph, opId, remembered)` returning `"3d" | "cutaway" | "glance"`, `plyRows(graph, cid)`,
    `isolateLabel(graph, cid, node)`.
  - `window.__guide.paneMode()` for e2e.

- [ ] **Step 1: Write the failing node tests**

```js
// guide/viewer/tests/cutaway.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { GLANCE, cutawayFor, hasGlance, readView, writeView, paneMode, plyRows, isolateLabel } from "../js/cutaway.js";

const G = {
  components: { "canard.shear_web": { label: "Shear web" } },
  plies: { "canard.shear_web": [{ node: "canard.shear_web.p1", order: 1 }, { node: "canard.shear_web.p3", order: 3 }] },
  cutaway: { ops: { "r30.bottom-skin": { src: "renders/op-r30-bottom-skin.png", alt: "After" } }, heroes: [{ bl: 5 }] },
};
const mem = () => { const m = new Map(); return { getItem: k => m.get(k) ?? null, setItem: (k, v) => m.set(k, v) }; };
const throwing = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };

test("cutawayFor and hasGlance", () => {
  assert.equal(cutawayFor(G, "r30.bottom-skin").src, "renders/op-r30-bottom-skin.png");
  assert.equal(cutawayFor(G, "r30.jig-assemble"), null);
  assert.equal(cutawayFor({}, "x"), null);
  assert.equal(hasGlance(G), true); assert.equal(hasGlance({ cutaway: null }), false);
});

test("view memory survives blocked storage", () => {
  const s = mem(); assert.equal(readView(s), "3d");
  writeView(s, "cutaway"); assert.equal(readView(s), "cutaway");
  assert.equal(readView(throwing), "3d"); writeView(throwing, "cutaway");
});

test("paneMode: hidden toggle falls back to 3D; glance wins", () => {
  assert.equal(paneMode(G, "r30.bottom-skin", "cutaway"), "cutaway");
  assert.equal(paneMode(G, "r30.jig-assemble", "cutaway"), "3d");
  assert.equal(paneMode(G, "r30.bottom-skin", "3d"), "3d");
  assert.equal(paneMode(G, GLANCE, "3d"), "glance");
});

test("ply rows and isolate label", () => {
  assert.equal(plyRows(G, "canard.shear_web").length, 2);
  assert.deepEqual(plyRows(G, "canard.core"), []);
  assert.equal(isolateLabel(G, "canard.shear_web", "canard.shear_web.p3"), "Showing Shear web ply 3");
});
```

- [ ] **Step 2: Run to confirm failure**

Run: `node --test guide/viewer/tests/*.test.mjs`
Expected: failure resolving `../js/cutaway.js`.

- [ ] **Step 3: Write `guide/viewer/js/cutaway.js`**

```js
// guide/viewer/js/cutaway.js — pure view logic for the M2 layup cutaway (no DOM).
export const GLANCE = "__glance";
export const VIEW_KEY = "longez.view";

export function cutawayFor(graph, opId) { return graph.cutaway?.ops?.[opId] ?? null; }
export function hasGlance(graph) { return (graph.cutaway?.heroes?.length ?? 0) > 0; }

export function readView(storage) {
  try { return storage.getItem(VIEW_KEY) === "cutaway" ? "cutaway" : "3d"; } catch { return "3d"; }
}
export function writeView(storage, v) {
  try { storage.setItem(VIEW_KEY, v); } catch { /* per-viewer convenience only */ }
}
export function paneMode(graph, opId, remembered) {
  if (opId === GLANCE) return "glance";
  return cutawayFor(graph, opId) && remembered === "cutaway" ? "cutaway" : "3d";
}
export function plyRows(graph, cid) { return graph.plies?.[cid] ?? []; }
export function isolateLabel(graph, cid, node) {
  const r = plyRows(graph, cid).find(p => p.node === node);
  return `Showing ${graph.components?.[cid]?.label ?? cid} ply ${r?.order ?? "?"}`;
}
```

Run: `node --test guide/viewer/tests/*.test.mjs`. Expected: PASS.

- [ ] **Step 4: Add markup** (in `guide/viewer/index.html`)

Replace the `#viewport` section and the `<aside>` opening with:

```html
    <section id="viewport">
      <div id="viewtoggle" role="radiogroup" aria-label="View" hidden>
        <button role="radio" data-view="3d" aria-checked="true">3D</button>
        <button role="radio" data-view="cutaway" aria-checked="false">Cutaway</button>
      </div>
      <canvas id="c"></canvas><p id="model-status"></p>
      <figure id="cutpane" hidden>
        <button id="cutzoom" class="imgbtn" aria-label="Enlarge cutaway"><img id="cutimg" alt=""></button>
        <figcaption id="cutcap"></figcaption>
        <p id="cuterr" class="err" hidden>Cutaway picture didn't load. <button id="cutretry">Retry</button></p>
      </figure>
      <div id="glance" hidden></div>
      <div id="isobar" hidden><span id="isotext"></span><button id="showall">Show all</button></div>
      <div id="plydock" hidden></div>
      <div id="parts"></div>
    </section>
    <aside>
      <div id="legend" hidden></div>
```

Before `<script type="module" …>` add:

```html
  <dialog id="zoom" aria-label="Enlarged picture"><button id="zoomclose">Close</button><div id="zoombody"></div></dialog>
```

- [ ] **Step 5: Add styles** (append to `guide/viewer/css/app.css`)

```css
/* M2 cutaway. Cloth hexes match the render-tooling repo jobs/blender/layup_contract.py HEX. */
:root{--und:#d9962b;--und2:#a8681a;--bid:#3a9e98;--bid2:#1f7a75;--foam:#dcdcd6}
button{min-height:44px}
#viewtoggle{position:absolute;top:8px;left:8px;z-index:2;display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--bg)}
#viewtoggle button{border:0;background:none;color:var(--fg);padding:0 16px;font:inherit}
#viewtoggle button[aria-checked="true"]{background:var(--sel);color:var(--acc);font-weight:600}
#cutpane,#glance{position:absolute;inset:60px 8px 64px;margin:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;overflow:auto}
#cutpane[hidden],#glance[hidden]{display:none}
.imgbtn{border:0;padding:0;background:none;cursor:zoom-in;max-width:100%;max-height:100%}
.imgbtn img{max-width:100%;max-height:calc(100vh - 240px);display:block}
#cutcap,#glance figcaption{color:var(--mut);font-size:.9rem}
.err{color:var(--warn)}
#glance{flex-direction:row;flex-wrap:wrap}
#glance figure{flex:1 1 320px;margin:0;display:flex;flex-direction:column;align-items:center}
main.glance{grid-template-columns:260px 1fr 280px}
#ops li.glance{font-weight:600;border-bottom:1px solid var(--line);margin-bottom:6px;border-radius:6px 6px 0 0}
#legend ul{list-style:none;padding:0;margin:8px 0}#legend li{display:flex;gap:8px;align-items:center;margin:6px 0;font-size:.9rem}
.sw{width:22px;height:14px;border:1px solid var(--line);flex:none}
.sw.und{background:linear-gradient(90deg,var(--und) 50%,var(--und2) 50%)}
.sw.bid{background:linear-gradient(90deg,var(--bid) 50%,var(--bid2) 50%)}
.sw.foam{background:var(--foam)}
.sw.unverified{background:repeating-linear-gradient(45deg,var(--und) 0 4px,var(--und2) 4px 8px)}
#isobar{position:absolute;top:8px;right:8px;z-index:2;display:flex;gap:8px;align-items:center;background:var(--sel);border:1px solid var(--acc);border-radius:8px;padding:0 0 0 12px}
#viewport.isolating{outline:2px solid var(--acc);outline-offset:-2px}
#plydock{position:absolute;left:8px;bottom:56px;z-index:2;background:var(--bg);border:1px solid var(--line);border-radius:8px;max-height:50%;overflow:auto;min-width:240px}
#plydock button{display:flex;gap:8px;align-items:center;width:100%;border:0;border-bottom:1px solid var(--line);background:none;color:var(--fg);text-align:left;padding:0 12px;font:inherit}
#plydock button[aria-pressed="true"]{background:var(--sel);color:var(--acc)}
dialog#zoom{max-width:100vw;max-height:100vh;width:100vw;height:100vh;padding:0;border:0;background:var(--bg);color:var(--fg)}
#zoombody{overflow:auto;height:calc(100% - 52px);touch-action:pinch-zoom}
#zoombody img{max-width:none;width:100%}
@media (max-width:820px){main.glance{grid-template-columns:1fr} #cutpane,#glance{position:static;min-height:50vh} #glance{flex-direction:column}}
```

- [ ] **Step 6: Wire it** (in `guide/viewer/js/app.js`)

Add to the imports:

```js
import { GLANCE, cutawayFor, hasGlance, readView, writeView, paneMode } from "./cutaway.js";
```

After `const store = makeStore(...)`, add:

```js
let view = readView(storage ?? { getItem() { return null; } });
```

In `renderList()`, before the op loop, add:

```js
  if (hasGlance(graph)) {
    const li = document.createElement("li"); li.dataset.op = GLANCE; li.className = "glance";
    li.textContent = "Canard layup at a glance"; li.onclick = selectGlance; ol.append(li);
  }
```

Add these functions (before `window.__guide = …`):

```js
function applyPane() {
  const mode = current ? paneMode(graph, current, view) : "3d";
  $("#viewtoggle").hidden = !(current && current !== GLANCE && cutawayFor(graph, current));
  for (const b of document.querySelectorAll("#viewtoggle button")) b.setAttribute("aria-checked", String(b.dataset.view === view));
  $("#c").hidden = mode !== "3d"; $("#parts").hidden = mode !== "3d";
  $("#cutpane").hidden = mode !== "cutaway"; $("#glance").hidden = mode !== "glance";
  $("#legend").hidden = mode !== "glance"; document.querySelector("main").classList.toggle("glance", mode === "glance");
  if (mode === "cutaway") showCut(cutawayFor(graph, current));
  if (mode === "3d") resize();
}
function showCut(c) {
  const img = $("#cutimg"); $("#cuterr").hidden = true; img.hidden = false;
  img.onerror = () => { img.hidden = true; $("#cuterr").hidden = false; };
  img.alt = c.alt; img.src = c.src; $("#cutcap").textContent = c.alt;
}
function zoom(src, alt) {
  const im = document.createElement("img"); im.src = src; im.alt = alt;
  $("#zoombody").replaceChildren(im); $("#zoom").showModal();
}
function selectGlance() {
  current = GLANCE; markSelected([GLANCE]); showAll();
  $("#op-title").textContent = "Canard layup at a glance";
  $("#op-summary").textContent = graph.cutaway.count_note;
  for (const id of ["#parts", "#changes", "#source", "#checklist"]) $(id).replaceChildren();
  $("#glance").replaceChildren(...graph.cutaway.heroes.map(h => {
    const f = document.createElement("figure"), b = document.createElement("button"), im = document.createElement("img");
    b.className = "imgbtn"; b.setAttribute("aria-label", `Enlarge section at BL ${h.bl}`);
    im.src = h.src; im.alt = h.alt; im.onerror = () => { f.append(Object.assign(document.createElement("p"), { className: "err", textContent: "Section picture didn't load." })); };
    b.append(im); b.onclick = () => zoom(h.src, h.alt);
    const cap = document.createElement("figcaption"); cap.textContent = `BL ${h.bl} (${h.bl < 20 ? "inboard" : "outboard"})`;
    f.append(b, cap); return f;
  }));
  const ul = document.createElement("ul");
  for (const l of graph.cutaway.legend) {
    const li = document.createElement("li");
    if (l.swatch) { const s = document.createElement("i"); s.className = `sw ${l.swatch}`; li.append(s); }
    li.append(l.text); ul.append(li);
  }
  const h = document.createElement("h3"); h.textContent = "Legend";
  $("#legend").replaceChildren(h, ul);
  applyPane();
}
for (const b of document.querySelectorAll("#viewtoggle button")) {
  b.onclick = () => { view = b.dataset.view; writeView(storage ?? { setItem() {} }, view); applyPane(); };
  b.onkeydown = e => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); const o = [...document.querySelectorAll("#viewtoggle button")].find(x => x !== b); o.focus(); o.click(); }
  };
}
$("#cutzoom").onclick = () => zoom($("#cutimg").src, $("#cutimg").alt);
$("#cutretry").onclick = () => { const c = cutawayFor(graph, current); if (c) showCut({ ...c, src: `${c.src}?r=${Date.now()}` }); };
$("#zoomclose").onclick = () => $("#zoom").close();
document.addEventListener("keydown", e => { if (e.key === "Escape" && !$("#zoom").open) showAll(); });
```

`showAll` is defined in Task 11. For this task, add a stub that Task 11 replaces:

```js
function showAll() { /* replaced in Task 11 (ply isolate) */ }
```

At the end of `selectOp(id)`, add `showAll(); applyPane();`.
In `clearDetail()`, add `applyPane();`.
Add `paneMode: () => current ? paneMode(graph, current, view) : "3d"` to `window.__guide`.

- [ ] **Step 7: Write the e2e tests** (append to `tests/guide/test_viewer_e2e.py`)

```python
from tests.guide.render_fixture import make_export, make_renders


@pytest.fixture
def csite(tmp_path):
    e = make_export(tmp_path / "e"); r = make_renders(tmp_path / "r", e)
    out = tmp_path / "site"
    build(Path("guide/graph"), out, models=e / "longez.glb", scan_base=None, docs=None, renders=r)
    return out


def test_cutaway_toggle_memory_and_hidden_on_non_layup(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=1180)
        pg.select_option("#variant", "roncz")
        pg.click('#ops li[data-op="r30.bottom-skin"]')
        assert pg.is_visible("#viewtoggle")
        pg.click('#viewtoggle [data-view="cutaway"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        assert pg.get_attribute("#cutimg", "src") == "renders/op-r30-bottom-skin.png"
        assert pg.get_attribute("#cutimg", "alt").startswith("After ")
        pg.click('#ops li[data-op="r30.jig-assemble"]')
        assert not pg.is_visible("#viewtoggle") and pg.evaluate("window.__guide.paneMode()") == "3d"
        pg.click('#ops li[data-op="r30.top-skin"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"  # remembered
        b.close()
    s.shutdown()


def test_glance_view(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        for width in (1180, 820):
            b, pg = open_page(p, url, width=width)
            pg.click('#ops li[data-op="__glance"]')
            assert pg.locator("#glance img").count() == 2 and pg.is_visible("#legend")
            assert "shear web 6 at BL 5" in pg.text_content("#op-summary")
            b.close()
    s.shutdown()


def test_missing_cutaway_png_shows_retry(csite):  # Review Focus 4
    (csite / "renders" / "op-r30-bottom-skin.png").unlink()
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
        pg.click('#viewtoggle [data-view="cutaway"]')
        pg.wait_for_selector("#cuterr:not([hidden])")
        pg.click('#viewtoggle [data-view="3d"]')
        assert pg.evaluate("window.__guide.paneMode()") == "3d"
        b.close()
    s.shutdown()


def test_toggle_works_when_localstorage_throws(csite):
    s, url = serve(csite)
    init = "Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})"
    with sync_playwright() as p:
        b, pg = open_page(p, url, init=init)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.bottom-skin"]')
        pg.click('#viewtoggle [data-view="cutaway"]')
        assert pg.evaluate("window.__guide.paneMode()") == "cutaway"
        b.close()
    s.shutdown()


def test_site_without_renders_has_no_toggle_or_glance(site):
    s, url = serve(site)
    with sync_playwright() as p:
        b, pg = open_page(p, url)
        assert pg.locator('#ops li[data-op="__glance"]').count() == 0
        assert not pg.is_visible("#viewtoggle")
        b.close()
    s.shutdown()
```

- [ ] **Step 8: Run all viewer tests**

Run: `node --test guide/viewer/tests/*.test.mjs && .venv/bin/python -m pytest tests/guide/test_viewer_e2e.py -v`
Expected: all PASS, including M1's existing e2e tests.

- [ ] **Step 9: Commit**

```bash
git add guide/viewer tests/guide/test_viewer_e2e.py
git commit -m "feat(viewer): 3D/Cutaway toggle, layup-at-a-glance view, cutaway states"
```

---

### Task 10: Full render + deploy with `--renders`

**Files:**
- Modify: `scripts/deploy_guide.sh`

- [ ] **Step 1: Make deploy require and verify renders**

In `scripts/deploy_guide.sh`, replace the `export_glb` and `build_site` lines with:

```bash
$PY -m guide.export_glb --out output/guide/longez.glb
CF=${OPENEZ_BLENDER_SCRIPTS:-<render-tooling repo>}
KEY=$($PY -m guide.render_key --export output/guide --scripts "$CF/deploy/<gpu-host>/jobs/blender")
RENDERS="${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}/$KEY"
[ -f "$RENDERS/manifest.json" ] || { echo "no renders for key $KEY; run guide/render_cutaway.sh first" >&2; exit 1; }
$PY -m guide.build_site --out site --models output/guide/longez.glb --scan-base "$SCAN_BASE" --renders "$RENDERS"
```

Before the final `echo "deployed and verified…"`, add:

```bash
curl -fsS -o /dev/null "$LONGEZ_SITE_URL/renders/hero-bl5.png" || { echo "DEPLOY VERIFY FAILED: hero render not served" >&2; exit 1; }
```

- [ ] **Step 2: Render every shot**

Run: `.venv/bin/python -m guide.export_glb && guide/render_cutaway.sh`
Expected: `renders: …/<key>` with 7 PNGs and a manifest. Check the lease first. On exit 3, report
who holds it and stop; do not loop.

- [ ] **Step 3: Deploy**

Run: `source ~/.config/long-ez/env && bash scripts/deploy_guide.sh`
Expected: `deployed and verified: N ops at $LONGEZ_SITE_URL`.

- [ ] **Step 4: Verify live, end to end**

```bash
source ~/.config/long-ez/env
curl -fsS "$LONGEZ_SITE_URL/graph.json" | python3 -c 'import json,sys; g=json.load(sys.stdin); c=g["cutaway"]; print(len(c["ops"]), [h["bl"] for h in c["heroes"]]); print(c["count_note"])'
for f in hero-bl5 hero-bl40 op-r30-shear-web op-r30-top-skin; do curl -fsS -o /dev/null -w "$f %{http_code}\n" "$LONGEZ_SITE_URL/renders/$f.png"; done
```

Expected: `5 [5.0, 40.0]`, the count note, and four 200s.

- [ ] **Step 5: Commit**

```bash
git add scripts/deploy_guide.sh
git commit -m "feat(deploy): deploy requires current renders and verifies a hero is served"
```

---

# Session 3: viewer ply list (Tasks 11–12). First to cut if over time.

### Task 11: Ply list with isolate (spec §6.1 ply list)

**Files:**
- Modify: `guide/viewer/js/app.js`
- Test: `tests/guide/test_viewer_e2e.py` (add test)

**Interfaces:**
- Consumes: `plyRows`, `isolateLabel` (Task 9); graph.json `plies`; glb ply nodes nested under their
  components (Task 4).
- Produces: `window.__guide.isolated()`, which returns the isolated node or null, and
  `window.__guide.meshPlies()`, which returns the ply node names found on meshes.

- [ ] **Step 1: Write the failing e2e test**

```python
def test_ply_list_isolates_inner_web_ply(csite):
    s, url = serve(csite)
    with sync_playwright() as p:
        b, pg = open_page(p, url, width=1180)
        pg.select_option("#variant", "roncz"); pg.click('#ops li[data-op="r30.shear-web"]')
        pg.wait_for_function("window.__guide.meshPlies().length > 0")
        pg.click('#parts .chip[data-cid="canard.shear_web"]')
        assert pg.locator("#plydock button").count() == 6
        pg.click('#plydock button[data-node="canard.shear_web.p3"]')
        assert pg.evaluate("window.__guide.isolated()") == "canard.shear_web.p3"
        assert pg.is_visible("#isobar") and pg.text_content("#isotext") == "Showing Shear web ply 3"
        pg.keyboard.press("Escape")
        assert pg.evaluate("window.__guide.isolated()") is None and not pg.is_visible("#isobar")
        pg.click('#plydock button[data-node="canard.shear_web.p3"]')
        pg.click('#ops li[data-op="r30.bottom-skin"]')
        assert pg.evaluate("window.__guide.isolated()") is None  # changing op resets
        b.close()
    s.shutdown()
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/guide/test_viewer_e2e.py::test_ply_list_isolates_inner_web_ply -v`
Expected: FAIL (`meshPlies` is undefined).

- [ ] **Step 3: Implement**

Add `plyRows, isolateLabel` to the `./cutaway.js` import.

Next to `const meshes = new Map();`, add:

```js
const plyNode = new Map(); let isolated = null;
```

In the GLTF traverse, after computing `cid`, record the ply node by walking up to the first name
ending in `.p<n>`:

```js
    let q = o; while (q && !/\.p\d+$/.test(nm(q)) && q.parent) q = q.parent;
    if (/\.p\d+$/.test(nm(q))) plyNode.set(o, nm(q));
```

In `selectOp`, change the chip builder so a chip with ply rows toggles the dock:

```js
    const rows = plyRows(graph, cid);
    if (rows.length) b.textContent += ` · ${rows.length} plies`;
    b.onclick = () => { selectComponent(cid); if (rows.length) toggleDock(cid); };
```

Replace the Task 9 `showAll` stub:

```js
function isolate(node) {
  isolated = node;
  for (const [m] of meshes) {
    m.material.transparent = true;
    m.material.opacity = plyNode.get(m) === node ? 1 : 0.15;
  }
  const cid = [...meshes].find(([m]) => plyNode.get(m) === node)?.[1];
  $("#isotext").textContent = isolateLabel(graph, cid, node); $("#isobar").hidden = false;
  $("#viewport").classList.add("isolating");
  for (const b of document.querySelectorAll("#plydock button")) b.setAttribute("aria-pressed", String(b.dataset.node === node));
}
function showAll() {
  isolated = null;
  for (const [m] of meshes) { m.material.opacity = 1; m.material.transparent = false; }
  $("#isobar").hidden = true; $("#viewport").classList.remove("isolating");
  for (const b of document.querySelectorAll("#plydock button")) b.setAttribute("aria-pressed", "false");
}
function toggleDock(cid) {
  const dock = $("#plydock");
  if (!dock.hidden && dock.dataset.cid === cid) { dock.hidden = true; return; }
  dock.dataset.cid = cid;
  dock.replaceChildren(...plyRows(graph, cid).map(r => {
    const b = document.createElement("button"); b.dataset.node = r.node; b.setAttribute("aria-pressed", "false");
    const sw = document.createElement("i"); sw.className = `sw ${r.position_verified ? r.cloth.toLowerCase() : "unverified"}`;
    b.append(sw, `${r.order} · ${r.cloth} · ${r.where}`);
    b.onclick = () => (isolated === r.node ? showAll() : isolate(r.node));
    return b;
  }));
  dock.hidden = false;
}
$("#showall").onclick = showAll;
```

At the start of `selectOp`, add `$("#plydock").hidden = true;`. `showAll()` is already called there
(Task 9).

Add to `window.__guide`: `isolated: () => isolated, meshPlies: () => [...new Set(plyNode.values())]`.

- [ ] **Step 4: Run all viewer tests**

Run: `node --test guide/viewer/tests/*.test.mjs && .venv/bin/python -m pytest tests/guide/test_viewer_e2e.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit and deploy**

```bash
git add guide/viewer tests/guide/test_viewer_e2e.py
git commit -m "feat(viewer): per-component ply list with isolate and Show all"
source ~/.config/long-ez/env && bash scripts/deploy_guide.sh
```

---

### Task 12: Definition of done (spec §8)

- [ ] **Step 1: Full suites, run from two directories**

```bash
cd ~/open-ez && .venv/bin/python -m pytest -q -p no:cacheprovider && node --test guide/viewer/tests/*.test.mjs && .venv/bin/python -m guide.check
cd /tmp && ~/open-ez/.venv/bin/python -m pytest -q ~/open-ez/tests/guide -p no:cacheprovider --rootdir ~/open-ez
cd <render-tooling repo> && python3 -m pytest deploy/<gpu-host>/tests -q
```

Expected: all green. If the second command errors on relative `guide/graph` paths, that is a real
defect: the tests assume cwd. Fix the tests to use `Path(__file__).resolve().parents[2] / "guide/graph"`
and re-run.

- [ ] **Step 2: Live proof is recorded**

Record in the task notes:
- the `render_cutaway.sh` output, showing `CYCLES_DEVICE=OPTIX` in `ssh <gpu-host> cat …/out/log.txt`
- `GPU_JOB_RESULT rc=0 restore=restored`
- the vLLM probe output after the run
- the deploy script's `deployed and verified` line

- [ ] **Step 3: Grader**

Run `~/.claude/bin/grade-diff.sh` (house rule 2) on the M2 range of both repos. Push in the same turn
as the grade (memory `infra_grade_diff_mute_is_stop_hook_reaper`). Do not push open-ez (public)
without Ryan's per-instance OK; say so.

- [ ] **Step 4: Ryan's acceptance on the iPad**

Hand Ryan `$LONGEZ_SITE_URL`. Ask him to check "Canard layup at a glance": bottom 3,
top 4 at both stations, and shear web 6 vs 2. Also ask him to tap one op's Cutaway and isolate a
shear-web ply. M2 is done only on his yes.

- [ ] **Step 5: Close out**

- Update memory `project_longez_build_guide` with the live state and anything that bit.
- Append a lane-log row per wave to `~/.claude/state/lane-log.tsv`.
- Remove the throwaway mockups: `ssh "$LONGEZ_DEPLOY_HOST" rm -rf <site root>/site/mockups`.
  The next deploy's `rsync --delete` also removes them.
