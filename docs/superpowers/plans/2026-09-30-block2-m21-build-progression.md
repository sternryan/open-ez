# Block 2 Milestone 2.1: Build Progression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the canard chapters play as a build.
- The 3D view shows exactly what exists at each operation.
- A scrubber lays the current operation's plies in order.
- A live section plane cuts the built layers, with a station readout.
- Load-path lines appear once their parts exist.
- Each chapter has a scripted tour.

**Architecture:**
- Pure, node-tested modules in `guide/viewer/js/`:
  - `build.js`: build state;
  - `section.js`: layers at a station;
  - `tour.js`: the tour step function.
- `app.js` wires them to three.js.
- The section cut is a clipping plane with stencil caps, adapted from the MIT-licensed airsup lab
  (`src/core/cut.ts`).
- Load-path polylines are computed in Python from the layup geometry, so they sit where the parts
  really are, and ship in `graph.json`.

**Tech Stack:** three.js (vendored), vanilla ES modules, `node --test`, pytest + Playwright
(chromium) for e2e, CadQuery for load-path anchors.

**Spec:** `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`, §3. Read it in full.

## Global Constraints

- **Data already in hand:** `graph.plies[cid]` rows carry `node`, `order` and `op`, and
  `layup.json` maps each glb ply node to `op`, `op_index`, `order`, `cloth` and `bl_max`. Read the
  build state from these; never invent a second mapping.
- **Node names:** GLTFLoader strips dots from node names, so map meshes via `userData.name`
  (existing `app.js` pattern).
- **Attribution:** any code adapted from airsup keeps an attribution header naming the source
  (`AirsupHQ/airsup-lab`, MIT), and a `NOTICE` file at the repo root records the MIT licence text
  for it.
- **Copyright:** operation text stays in the owner's words and passes `guide.check`. No plans text
  goes in new data files.
- **Public repo:** no home paths, no tailnet names or IPs, and never the copyright phrase.
- **Commits:** crew never commit. The captain commits after a green, unpiped run in open-ez, in the
  same turn. Restore `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json` before each
  commit. No trailers, and stage named files only.
- **Test commands:**
  - `node --test guide/viewer/tests/*.test.mjs`;
  - `.venv/bin/python -m pytest tests/guide -q -p no:cacheprovider`;
  - the full suite `.venv/bin/python -m pytest -q -p no:cacheprovider --deselect scripts/assembly_test.py::test_full_assembly`;
  - `source ~/.config/long-ez/env && .venv/bin/python -m guide.check`.

## Review Focus

1. **A ply shown before it's laid.** Stepping to an earlier operation leaves later plies visible.
   Expectation: `visibleSet` is recomputed from scratch on every change, and the e2e checks the
   visible mesh count after stepping backwards. Pinned in Tasks 1 and 2.
2. **An untagged mesh silently always-visible.** A glb mesh that no operation owns stays on
   screen at every step. Expectation: `visibleSet` throws on a mesh with no owning operation, and a
   test proves it. Pinned in Task 1.
3. **A cut readout that lies about the station.** A sign or frame error (model Y versus B.L.)
   makes the readout report the wrong station. Expectation: the plane is placed at a known B.L.,
   the readout shows that B.L., and the listed layers match Python's `layup.counts_at` for the same
   station. Pinned in Task 3.
4. **A load path drawn through air.** A path appears before its parts exist, or its polyline
   doesn't touch its parts. Expectation: paths are gated by `visibleSet`, and every anchor lies
   within 0.5 in of its part's solid. Pinned in Task 4.
5. **A tour that skips or reorders.** Expectation: the tour visits every visible operation of the
   chapter, in graph order. Pinned in Task 5.

## File map

| File | Responsibility |
|---|---|
| `guide/viewer/js/build.js` (new) | `firstOp`, `visibleSet`: pure build state |
| `guide/viewer/js/section.js` (new) | `layersAt`: layers cut at a B.L. |
| `guide/viewer/js/cut.js` (new) | clipping plane and stencil caps (adapted from airsup) |
| `guide/viewer/js/tour.js` (new) | `tourSteps`, `stepTour`: deterministic tour |
| `guide/viewer/js/app.js` | wiring: scrubber, ghost toggle, section slider, paths, tour |
| `guide/viewer/index.html`, `guide/viewer/css/*` | controls |
| `guide/loadpaths.py` (new) + `guide/graph/loadpaths.yaml` (new) | path definitions and anchor polylines |
| `guide/graph/tours.yaml` (new) | camera shots per operation |
| `guide/build_site.py`, `guide/schema.py` | ship `loadpaths` and `tours` in `graph.json`; validate them |
| `guide/viewer/tests/*.test.mjs`, `tests/guide/test_*.py` | tests |
| `NOTICE` (new) | the MIT licence text for the adapted code |

---

### Task 1: Build state (`build.js`)

**Files:** create `guide/viewer/js/build.js` and `guide/viewer/tests/build.test.mjs`.

**Interfaces:**
- Produces:
  - `firstOp(graph, variant) -> Map<componentId, opId>`: the first visible operation, in graph
    order, whose `components` lists the component.
  - `visibleSet(graph, variant, opId, layIndex, meshes) -> Map<meshName, "built"|"current"|"ghost"|"hidden">`.
    `meshes` is an array of `{name, component, ply}`, where `ply` is `{op, order}` or `null`.

Rules:
- **Mesh with a ply:** it takes its ply's `op` and `order`.
- **Component mesh (core):** it takes `firstOp`.
- **Built:** the mesh's op comes before the selected op in the visible order.
- **Current:** the mesh's op is the selected op, and for a ply, `order <= layIndex`. `layIndex` of
  `Infinity` means the whole op.
- **Ghost or hidden:** otherwise, the mesh's op is later, or it's a ply of the current op past
  `layIndex`. It's `ghost` when `graph.__ghost` is true, else `hidden`.
- **Out of variant:** a mesh whose component isn't used in the variant is `hidden`.
- **Unowned:** a mesh with no owning op throws `Error("unowned mesh <name>")`.

- [ ] **Step 1: Failing tests**

```js
// guide/viewer/tests/build.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { firstOp, visibleSet } from "../js/build.js";

const G = {
  order: ["r30.cores", "r30.shear-web", "r30.bottom-skin"],
  ops: [
    { id: "r30.cores", components: ["canard.core"], variants: ["roncz"] },
    { id: "r30.shear-web", components: ["canard.shear_web"], variants: ["roncz"] },
    { id: "r30.bottom-skin", components: ["canard.skin_bottom"], variants: ["roncz"] },
  ],
};
const M = [
  { name: "canard.core", component: "canard.core", ply: null },
  { name: "canard.shear_web.p1", component: "canard.shear_web", ply: { op: "r30.shear-web", order: 1 } },
  { name: "canard.shear_web.p2", component: "canard.shear_web", ply: { op: "r30.shear-web", order: 2 } },
  { name: "canard.skin_bottom.p1", component: "canard.skin_bottom", ply: { op: "r30.bottom-skin", order: 1 } },
];
const st = (op, lay, g = G) => Object.fromEntries(visibleSet(g, "roncz", op, lay, M));

test("firstOp maps components to their first op", () => {
  assert.equal(firstOp(G, "roncz").get("canard.core"), "r30.cores");
});

test("state at the shear web, ply 1 of 2", () => {
  assert.deepEqual(st("r30.shear-web", 1), {
    "canard.core": "built", "canard.shear_web.p1": "current",
    "canard.shear_web.p2": "hidden", "canard.skin_bottom.p1": "hidden" });
});

test("stepping backwards hides later work (Review Focus 1)", () => {
  st("r30.bottom-skin", Infinity);
  assert.equal(st("r30.cores", Infinity)["canard.shear_web.p1"], "hidden");
});

test("ghost mode shows future work as ghost", () => {
  assert.equal(st("r30.cores", Infinity, { ...G, __ghost: true })["canard.skin_bottom.p1"], "ghost");
});

test("an unowned mesh throws (Review Focus 2)", () => {
  assert.throws(() => visibleSet(G, "roncz", "r30.cores", Infinity,
    [...M, { name: "stray", component: "canard.elevator", ply: null }]), /unowned mesh stray/);
});
```

- [ ] **Step 2: Run** `node --test guide/viewer/tests/build.test.mjs`. Expected: fails on the import.
- [ ] **Step 3: Implement** `build.js` from the rules above. Import `visibleOps` and
  `componentsInVariant` from `./graph.js`.
- [ ] **Step 4: Run** all node tests. Expected: pass.
- [ ] **Step 5: Real-data test.** Add `tests/guide/test_build_state.py`:
  - build the site from the repo graph plus `output/guide` (run `guide.export_glb` first if
    missing);
  - run `node -e` to load `build.js` and apply `visibleSet` to every op;
  - assert no op throws, and that the count of `current` meshes at `layIndex=Infinity` equals that
    op's ply count in `layup.json` (1 for the core op).
- [ ] **Step 6: Commit** (`feat(viewer): pure build-state function for the rehearsal`).

---

### Task 2: Progression UI (ply scrubber, ghost toggle)

**Files:** modify `guide/viewer/js/app.js`, `guide/viewer/index.html` and `guide/viewer/css/*`;
add tests to `tests/guide/test_viewer_e2e.py`.

- [ ] **Step 1: Failing e2e tests** (follow the existing `site` fixture and page helpers):
  - Selecting `r30.shear-web` shows a `#scrub` range input with `max` equal to the op's ply count
    and the value at max. `window.__buildState()` (a test hook that returns the current
    `visibleSet` as an object) reports the core `built` and every shear-web ply `current`.
  - Setting `#scrub` to 1 leaves exactly one shear-web ply `current`, and the rest `hidden`.
  - Selecting `r30.bottom-skin` and then an earlier op leaves no bottom-skin mesh `visible` in three.js
    (Review Focus 1). Check `mesh.visible` through a second hook, `window.__visibleNames()`.
  - `#ghost` toggles future plies to `ghost`, rendered at opacity < 0.3.
  - `#play` animates the scrubber from 1 to max, and a second press stops it. Use Playwright's
    clock or a reduced interval (`?fast=1`).
- [ ] **Step 2: Run them.** Expected: fail.
- [ ] **Step 3: Implement.**
  - On every op or scrub change, recompute `visibleSet` and apply it to each mesh:
    - `built`: solid, base colour;
    - `current`: solid, with the existing highlight emissive;
    - `ghost`: transparent at 0.2;
    - `hidden`: `visible=false`.
  - The scrubber appears only for ops with plies.
  - The ghost toggle is remembered with the existing try/catch storage pattern.
  - Keep the M2 isolate behaviour: isolating a ply overrides the build state until it's cleared.
  - Expose the two test hooks only when `?test=1` is in the URL.
- [ ] **Step 4: Run** the e2e and node tests. Expected: pass. The existing e2e must stay green.
- [ ] **Step 5: Commit** (`feat(viewer): build progression with ply scrubber and ghost toggle`).

---

### Task 3: Live section cut and station readout

**Files:** create `guide/viewer/js/cut.js`, `guide/viewer/js/section.js`,
`guide/viewer/tests/section.test.mjs` and `NOTICE`; modify `app.js` and `index.html`;
add e2e tests.

**Interfaces:**
- `layersAt(plies, bl) -> Array<{node, component, cloth, order}>`: every ply whose `bl_max` is
  null (full span) or ≥ `bl`, sorted by `op_index` then `order`. `plies` is the `layup.json` `nodes`
  map.
- `makeCut(renderer, scene, meshes) -> {setStation(bl), enable(bool)}`: one clipping plane normal
  to the span axis, plus stencil caps.

- [ ] **Step 1: Read** airsup's `src/core/cut.ts` (`gh api repos/AirsupHQ/airsup-lab/contents/src/core/cut.ts`).
  Note how it builds its caps (stencil passes per solid) and how it treats thin skins.
- [ ] **Step 2: Failing tests.**
  - Node, `section.test.mjs`: `layersAt` on a fixture returns the right plies at BL 5, 25 and
    60 (a ply with `bl_max` 30 is present at 25 and absent at 60).
  - Python, `tests/guide/test_section_parity.py`: for BL in (5, 20, 40, 60), the node
    `layersAt(layup.json nodes, bl)` counts by cloth equal Python's
    `layup.counts_at(layup.plies(graph), bl)` (Review Focus 3).
  - e2e:
    - setting `#section` to BL 40 shows `B.L. 40` in `#section-readout`, and lists the same layers
      as `layersAt`;
    - a pixel probe at the cut face finds cap colours (UND or BID legend colours), not background;
    - `#section` off restores the unclipped view.
- [ ] **Step 3: Implement.**
  - `section.js` holds the pure layer logic.
  - `cut.js` adapts airsup's approach to our meshes, with the attribution header:

```js
// guide/viewer/js/cut.js
// Section cut with filled caps. Adapted from AirsupHQ/airsup-lab src/core/cut.ts (MIT);
// see NOTICE. Changes: one span-normal plane in the model's B.L. frame; every ply is capped as a
// solid (the plies are thin but closed), no hollow skins.
```

  - The model's span axis and sign come from the glb. The canard spans +Y from BL 0 in
    `layup_geometry`; verify this against the export before coding the plane.
  - The slider runs 0 to `semi_span` from `layup.json`.
  - `NOTICE` carries the airsup MIT licence text and names `cut.js`.
- [ ] **Step 4: Run** everything. Expected: pass.
- [ ] **Step 5: Commit** (`feat(viewer): live section cut with capped plies and a station readout`).

---

### Task 4: Load paths

**Files:** create `guide/loadpaths.py`, `guide/graph/loadpaths.yaml` and
`tests/guide/test_loadpaths.py`; modify `guide/build_site.py` and `guide/schema.py`, `app.js`.

**Interfaces:**
- `guide.loadpaths.polylines(graph) -> dict[path_id, {"label": str, "kind": "bending"|"shear"|"lift", "parts": [cid…], "points": [[x,y,z]…]}]`,
  in glb model coordinates.

- [ ] **Step 1: Author** `guide/graph/loadpaths.yaml` in the owner's words:

```yaml
# Qualitative load paths for the canard (no magnitudes until Block 3).
paths:
  - id: lift-into-caps
    label: Lift from the skins into the spar caps
    kind: lift
    parts: [canard.skin_top, canard.skin_bottom, canard.spar_cap_top, canard.spar_cap_bottom]
  - id: cap-bending
    label: Bending carried along the spar caps to the root
    kind: bending
    parts: [canard.spar_cap_top, canard.spar_cap_bottom]
  - id: web-shear
    label: Shear carried by the shear web
    kind: shear
    parts: [canard.shear_web]
```

- [ ] **Step 2: Failing tests.**
  - The schema rejects an unknown part id and an unknown `kind`.
  - Every polyline point lies within 0.5 in of at least one of its parts' solids from
    `layup_geometry.build_layup` (use `BRepExtrema_DistShapeShape`) (Review Focus 4).
  - `graph.json` carries `loadpaths`.
  - Node: a path's parts all `built`/`current` → drawn; any `hidden` → not drawn. Pure helper
    `pathVisible(path, state)` in `build.js`.
- [ ] **Step 3: Implement** `polylines`:
  - **cap-bending:** the cap centroid (x, z) sampled at BL 0 to cap `bl_max` in 8 steps.
  - **web-shear:** the web mid-height line.
  - **lift-into-caps:** short chordwise segments from mid-skin to the cap at 4 stations.

  Get the centroids from the solids' bounding boxes per slab, via the section at each BL. Then draw
  them in `app.js` as glow lines (`THREE.Line` with additive blending, animated dash offset), gated
  by `pathVisible`, with a `#paths` toggle.
- [ ] **Step 4: Run** everything. Expected: pass.
- [ ] **Step 5: Commit** (`feat(guide): qualitative load paths that follow the build`).

---

### Task 5: Chapter tours

**Files:** create `guide/graph/tours.yaml`, `guide/viewer/js/tour.js` and
`guide/viewer/tests/tour.test.mjs`; modify `build_site.py`, `schema.py`, `app.js` and
`index.html`.

**Interfaces:**
- `tourSteps(graph, variant, chapter) -> Array<{op, shot}>`: every visible op of the chapter in graph
  order, each with its shot, or the default shot if the op has none.
- `stepTour(state, dt) -> state`: a deterministic advance, `{i, t}`, with a fixed dwell per step.

- [ ] **Step 1: Failing tests.**
  - `tourSteps` covers every visible op of `ch30`, in order (Review Focus 5).
  - `stepTour` with a fixed dt sequence lands on the same step every run.
  - The schema rejects a shot for an unknown op.
  - e2e: `#tour` starts the tour and the selected op advances; Escape stops it.
- [ ] **Step 2: Implement.**
  - `tours.yaml` holds per-op camera `target` and `position` in model units, for the ops that
    need a specific view; the rest use the home view.
  - The tour drives `selectOp` and the scrubber, with the camera easing over 0.8 s.
  - `?fast=1` shortens dwell for tests.
- [ ] **Step 3: Run** everything. Expected: pass.
- [ ] **Step 4: Commit** (`feat(viewer): scripted chapter tours`).

---

### Task 6: Frame-time budget and phone width

**Files:** `tests/guide/test_viewer_e2e.py`.

- [ ] **Step 1: Add an e2e test.**
  - Load the Roncz variant at the top-skin op, with all plies and paths on.
  - Drag `#section` from 0 to max over 2 s.
  - Record `requestAnimationFrame` deltas through a `?test=1` hook.
  - Assert the median frame time is ≤ 33 ms in headless chromium.
  - Headless is a proxy. The iPad judgement is the owner's walk-through (Task 7), and the report says
    so.
- [ ] **Step 2:** Extend the existing phone-width test: at 390 px, no horizontal scroll, the section
  readout collapses to one line, and the scrubber stays reachable.
- [ ] **Step 3:** If the budget fails, fix performance: merge static built meshes into one draw
  call, and cap only the plies currently intersected. Never raise the budget.
- [ ] **Step 4: Commit** (`test(viewer): frame-time budget while cutting; phone-width controls`).

---

### Task 7: Deploy, owner walk-through, grade, push (lead)

- [ ] **Step 1:** Re-export (`guide.export_glb`), deploy (`scripts/deploy_guide.sh`), and verify in
  a browser that each control works on the live site.
- [ ] **Step 2:** The owner walks through the canard chapters on his iPad and judges the spec §4
  items. Record the verdict and any fixes.
- [ ] **Step 3:** Fetch and confirm behind 0, run `grade-diff.sh` and expect `VERDICT: PASS`, leak
  scan, run green unpiped, then `git push` in the same turn.
- [ ] **Step 4:** Update memory `project_longez_build_guide`.
