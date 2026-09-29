# Long-EZ Interactive Build Guide — M2 "Layup cutaway" (Roncz canard)

Status: APPROVED 2026-09-29 (rev 2: /plan-eng-review decisions folded in, see the report at the end)

## 1. Intent

M1 §2 commits one spatial explanation as M1's direct successor: the canard layup cutaway, linked to
its steps and rendered through the headless-Blender GPU payload. Timeboxed.

The cutaway answers "what is inside the canard, and in what order was it laid", which is the thing
the plans figures show worst. It has three surfaces over one set of layup geometry:

- **Hero section stack:** chordwise slices at BL 5 and BL 40 showing foam, shear web, spar caps and
  skins, every ply a distinct countable band in lay order.
- **Per-op highlight frames:** the same 3D cutaway rendered once per layup op, with that op's plies
  accented, earlier plies at full colour and later plies absent.
- **Viewer plies:** the ply solids in the three.js viewer, reachable through a per-component ply list.

**Acceptance test (legibility, human-judged on the iPad by Ryan, never self-graded):** reading the
hero cold, a person counts **bottom skin 3 plies and top skin 4 plies at both stations**, and **shear
web 6 plies at BL 5 against 2 at BL 40**. A layup.py unit test asserts the same numbers from the data.

## 2. Scope

In:
- Roncz canard (ch 30) layup ops listed in `LAYUP_SCOPE` (§4.4): shear web, bottom spar cap, bottom
  skin, top spar cap, top skin.
- Prerequisite fix: the open-ez canard core is a flat sheet (volume 0, see §3.1).
- Viewer ply list with isolate.

Out (reasoned, recorded as exclusions in `LAYUP_SCOPE`): GU (ch 10) layups; the 9-BID CL-1 nut-plate
pads and the rear tabs (local features, not at the section stations); animation; fixing open-ez
canard planform dimensions (§9, TODOS.md).

## 3. Rulings and prerequisites

- **CadQuery is the geometry SSOT; Blender output is derived** (throughline capabilities.md,
  "Headless 3D render"). No Blender wrapper, lease client, or second GPU path: add a script to
  `jobs/blender/` and dispatch via `fabric-gpu`.
- **The step graph is the ply SSOT.** Nothing is drawn that the graph does not hold. Where the
  geometry has to guess, the node says so (`position_verified: false`) and the legend states it.
- M1 §4 public/private boundary is unchanged. Renders derive from open-ez geometry and our own ply
  data, not the plans, so they are public-safe. Label and legend text passes `python -m guide.check`.

### 3.1 Task 0: the canard core is degenerate

Verified 2026-09-29: `CanardGenerator().generate_geometry()` has volume 0.0 and a bounding-box z
extent of 0. `Airfoil.get_cadquery_wire` builds the profile in the XY plane (`core/aerodynamics.py`,
"in XY plane, Z=0"). `_build_geometry` in `core/structures.py` then translates each station along Y
(`cq.Vector(x_offset, butt_line, z_offset)`) without rotating it, so every station is coplanar. This
is also why the smoke glb "arrives thin".

**Fix at placement, not in the airfoil.** The XY wire is what hot-wire G-code and DXF export consume.
Rotate each station wire into the XZ plane (chord along X, thickness along Z, span along Y) inside
`_build_geometry`, which the wing shares. Regression tests assert volume > 0 and a z thickness of
about t/c times chord at the root. Existing G-code/DXF tests must stay green. M1's viewer framing
may shift; the viewer e2e test is re-run.

## 4. Layup geometry (open-ez)

New module `guide/layup.py`.

### 4.1 Ply construction

- Plies are built **per ply by lofting numerically offset 2D station outlines**, not by an OCCT
  offset or shell of the core.
- Each station's airfoil points are offset along their normals in numpy by the ply's cumulative
  visual thickness.
- Stations are inserted exactly at each ply's start and end BL, so extents are exact with no booleans.
- The trailing edge is closed by clamping the offset.
- Each ply is lofted on its own.
- **Skins:** offset outward from the foam outline, bottom then top, in YAML order.
- **Shear web:** a vertical ply stack at the web plane, placed at the forward edge of the spar trough.
  That position comes from template page C-3, which no source we hold has, so it uses open-ez's
  **0.25c placeholder with `position_verified: false`** (TODOS.md).
- **Spar caps:** a tapered solid filling each trough, with `position_verified: false`, labelled
  "3 in UND tape, plies as required to fill trough (tapered)". The label is sourced to ch 30 Step 22,
  where the plans give no count: plies are added, each shorter, until the trough is full. open-ez's
  `spar_cap_plies = 17` is a main-wing value and is not used.
- **Section-ready foam:** the web slab and both troughs are subtracted from the (now solid) core, so no
  ply solid overlaps foam. A test asserts foam ∩ web/caps volume ≈ 0.
- **Thickness:** config ply thicknesses (UND 0.009", BID 0.013") set order only. Bands use a fixed
  exaggerated visual thickness with a thin gap between plies. Every view carries "not to scale".

### 4.2 `where` parsing

Each `where` string maps to `(span extent, orientation)` through an explicit lookup table.

- An explicit inch span is read as a symmetric extent: `"crossed, full span (108 in)"` → |BL| ≤ 54.
- A bare `"full span"` is the whole canard.
- `"inboard of BL n"` → |BL| ≤ n.
- **Unknown phrasing is a hard error, never a guess.**

**Content change riding in M2:** the ch30.yaml shear-web full-span row becomes
`"crossed, full span (108 in)"`. The source is cobelu ch 30 Step 14: "Two crossing plies of UND full
span (108")". The tip cores have no spar troughs (cobelu, "tip cores have no spar troughs"), so the web
stops at the inboard cores. The edit passes `guide.check` full mode.

### 4.3 Export

- `guide/export_glb.py` adds the ply solids to `longez.glb` **nested under their component nodes**:
  a sub-assembly `canard.skin_bottom` with children `p1…pn`. The viewer's parent walk
  (`app.js`, `userData.name`) then resolves every ply to its component.
- Alongside the glb it writes:
  - `layup.json`: `node → {component, op, cloth, order, extent, position_verified}`
  - `shots.json`, derived from `LAYUP_SCOPE`: the BL 5 and BL 40 hero sections plus one frame per
    included op.
- Export stays byte-deterministic (verified for M1's glb: two exports give the same sha256).

### 4.4 `LAYUP_SCOPE`: one inclusion rule

`layup.py` exports `LAYUP_SCOPE`: the included op ids, plus an explicit list of excluded material rows,
each with a reason string:

- `r30.align-canard` rear tabs: local feature, not at a section station.
- The `r30.shear-web` CL-1 pad row: local feature.

Geometry, `shots.json` and `build_site` strict mode all read it. A test fails if any ch30 materials
row is neither included nor excluded, so a new row forces a decision.

**Fidelity:** `canard.shear_web`, `canard.skin_bottom`, `canard.skin_top`, `canard.spar_cap_bottom`
and `canard.spar_cap_top` move from `no-geometry` to `unvalidated`. Ply counts come from ch 30;
geometry stays unvalidated (§9).

## 5. Render job (anvil)

```
 open-ez (laptop)                                   anvil (fabric-gpu, single-flight lease)
 ─────────────────                                  ───────────────────────────────────────
 export_glb ─► longez.glb ─┐
 layup.py  ─► layup.json ──┼─► render_cutaway.sh ─► /srv/gpu-jobs/blender/layup-<key>/in
           └► shots.json ──┘   (lease check,        blender.sh layup_cutaway <job_dir>
                                key = sha256 of all   └─ layup_cutaway.py + fabric_blender.py
                                inputs + scripts)          └─ out.tmp/ ─► out/ (manifest LAST)
 ~/.cache/long-ez/renders/<key>/ ◄── pull out/ ─────────────┘
 build_site --renders <dir> (strict: key match, every shot present) ─► site ─► deploy
```

- **Scripts:**
  - `compute-fabric-dev/deploy/anvil/jobs/blender/layup_cutaway.py`.
  - A new shared helper, `jobs/blender/fabric_blender.py`, holds `gpu_setup()` (the OPTIX/CUDA
    selection and the `BLENDER_REQUIRE_GPU` refusal) and `solidify_and_cut()`.
  - `smoke.py` is refactored to import it too, so the existing payload test is its regression test.
  - Blender's `--python` does not put the script dir on `sys.path`, so each script inserts it.
  - Both are deployed by hand to `/opt/fabric/jobs/`.
- **`in/`:** `longez.glb`, `layup.json`, `shots.json`.
- **Per shot:**
  1. Import the glb.
  2. Solidify only surfaces that are still thin.
  3. MANIFOLD boolean cut at the station plane.
  4. Materials: hue by cloth class (UND, BID, foam, position-unverified), with shade alternating by
     lay order so adjacent same-cloth plies stay distinct.
  5. Camera framed **from the cut face's bounds**, looking spanwise with a slight 3/4 offset.
  6. Op frames: earlier ops at full colour, the highlighted op accented, later ops hidden.
- **Output, atomic:**
  - Blender writes to `out.tmp/`: one PNG per shot at 1600×1200, and `log.txt` with the payload
    stdout (Nomad alloc logs are GC'd within seconds while anvil's disk is >80%).
  - `manifest.json` is written **last**, carrying shot → file + sha256 and the render key.
  - `out.tmp/` is renamed to `out/` only on success.
- GPU required (`BLENDER_REQUIRE_GPU=1`); a CPU fallback fails the job.

**Render key:** sha256 over `longez.glb`, `layup.json`, `shots.json`, `layup_cutaway.py` and
`fabric_blender.py`. Any input or renderer change invalidates old renders.
- `render_cutaway.sh` asserts that the local script bytes match `/opt/fabric/jobs` before it
  dispatches.
- `build_site` recomputes the data part of the key and checks the script hashes recorded in the
  manifest.

**Dispatch:** `guide/render_cutaway.sh` (open-ez). HITL only, never on a timer.

1. `ssh anvil flux-lock-status`. If another job holds the lease, print the holder and exit non-zero.
   No retry loop.
2. Stage inputs to `/srv/gpu-jobs/blender/layup-<key>/in`.
3. `fabric-gpu run blender.sh layup_cutaway <job_dir> --expect-s N`.
   - The script name is **bare**: blender.sh refuses anything outside `^[a-z0-9_]+$`.
   - Flags go after the positionals.
4. On success, pull `out/` to `~/.cache/long-ez/renders/<key>/`. A fabric-gpu failure exits non-zero.

Renders are **not committed**. The site build copies them in, and `scripts/deploy_guide.sh` ships them.

## 6. Guide wiring

- `build_site --renders <dir>` is **optional**, mirroring `--models`:
  - **Absent:** the build emits no cutaway panels and M1 output is unchanged.
  - **Present:** the build is strict. It fails on a missing manifest, a key mismatch, or any
    `LAYUP_SCOPE` shot without a file.
  - `deploy_guide.sh` always passes `--renders`.
- Each included layup op page gets a **Cutaway** panel with its highlight frame.
- A canard-level **Layup section** view shows both hero stations side by side, with a legend:
  - cloth hue
  - lay-order numbers
  - "not to scale"
  - "web/spar position not verified"
  - "spar caps: plies as required to fill trough"
- **Viewer ply list:** each component in the parts panel (`#parts`) expands to its plies. Tapping a
  ply isolates it, and the others ghost at low opacity. Without this, the outer skin wins every ray
  pick (`app.js` nearest hit) and the inner plies are unreachable.

## 7. Testing

**open-ez pytest:**
- Task 0: canard core volume > 0; z thickness ≈ t/c·chord at the root; G-code/DXF suites green.
- `where` parsing: known phrases, the explicit `(108 in)` span against a bare `full span`, and
  rejection of unknown phrasing.
- `LAYUP_SCOPE`: every ch30 materials row is included or excluded with a reason.
- Station insertion: plies start and end at their exact BL; the trailing-edge clamp keeps every
  offset outline closed; ply n lies strictly outside ply n−1.
- Acceptance counts: at BL 5 and BL 40, bottom 3, top 4, web 6 vs 2.
- Section-ready foam: foam ∩ web/caps volume ≈ 0; web and trough nodes carry
  `position_verified: false`.
- Export: ply nodes nest under their component nodes; `layup.json` covers every ply node;
  `shots.json` equals the `LAYUP_SCOPE`-derived list; export stays byte-deterministic.
- `build_site` (**CRITICAL regression**): without `--renders` the output matches M1. With `--renders`:
  panels are emitted when complete, and the build fails on a missing shot, a missing manifest, or a key
  mismatch.
- `render_cutaway.sh`, driven with stub `ssh`/`fabric-gpu`/`rsync` on PATH:
  - lease held → exit ≠ 0 with the holder in stderr
  - lease free → bare `layup_cutaway` passed (matches blender.sh's regex), job dir keyed on the render
    key, `out/` pulled to the cache
  - fabric-gpu rc ≠ 0 → exit ≠ 0
  - local/deployed script mismatch → exit ≠ 0

**Viewer (node `--test` on `*.test.mjs`, plus the browser e2e):** tap an inner shear-web ply in the
ply list and assert it is isolated and highlighted.

**compute-fabric-dev:** extend `deploy/anvil/tests/test_blender_payload.py`:
- The shot/manifest contract, checked without a GPU.
- The manifest is written last, and `out/` appears only on success.
- smoke.py still passes through `fabric_blender.py`.

## 8. Timebox, sessions and definition of done

**Three sessions, walking skeleton first.**

- **Session 1:** Task 0 (core fix), layup geometry and export, `fabric_blender.py` + `layup_cutaway.py`,
  and **one hero (BL 5) end to end**: CadQuery → anvil → PNG.
  **Gate:** Ryan judges it on the iPad against §1. If it fails, the hero becomes a flat SVG drawn
  from the same CadQuery slice (no GPU), and Blender keeps the per-op 3D frames.
- **Session 2:** BL 40 hero, per-op frames, `build_site --renders` strict mode, deploy.
- **Session 3:** viewer ply list and isolate.

**Cut order if over:** viewer ply list first, then per-op frames. **Minimum shippable:** Task 0 plus
both hero stations deployed.

**Definition of done:**
1. All suites green, run with the documented commands from two directories.
2. One live `fabric-gpu` run on anvil: `CYCLES_DEVICE=OPTIX`, `GPU_JOB_RESULT rc=0 restore=restored`,
   vLLM identity probe passing afterwards.
3. Deployed; the Cutaway panels, Layup section and ply list load at https://nas.tail857f5c.ts.net:7485
   over the tailnet.
4. Ryan passes the §1 acceptance test on the iPad.

## 9. Known accuracy issue (logged, not fixed in M2)

open-ez's canard is 147" span, 17"→13.5" tapered chord and 13.5° LE sweep (`config/aircraft_config.py`).
ch 30 describes 108" inboard cores plus separate tips and a 130" jig. The planform needs a plans check
before anyone reads dimensions off the cutaway (TODOS.md). The cutaway is a **topology picture, not a
dimensioned drawing**, and says so. Aero and dimension fixes stay out of scope, as in M1 §9.

## 10. Review outputs

### What already exists (reused, not rebuilt)

- `guide/export_glb.py`: the assembly → glb path, byte-deterministic, extended with nested ply nodes.
- `guide/build_site.py`: the optional-input pattern (`--models`), copied for `--renders`.
- `guide/viewer/js/app.js`: the parent walk to a component (`userData.name`) and the `#parts` button
  list, extended into the ply list.
- `jobs/blender/smoke.py`: the GPU guard and solidify/MANIFOLD cut, extracted into `fabric_blender.py`.
- `blender.sh` + `fabric-gpu`: used as-is, with no new GPU path.
- `python -m guide.check`: gates the content edit and the legend text.

### NOT in scope

- GU (ch 10) layups: M2 is the Roncz slice; GU has no generated core.
- CL-1 pads and rear tabs: local features, not at the section stations (recorded in `LAYUP_SCOPE`).
- Animation: stills answer the question; motion is cost without a reader need.
- Canard planform correction: needs the book check first (TODOS.md).
- A real source for the web/trough position: tracked in TODOS.md; labelled in the meantime.

### Failure modes

| Codepath | Realistic failure | Test | Handling | Visible? |
|---|---|---|---|---|
| Task 0 rotation | wing/G-code consumers get rotated wires | G-code/DXF suites | fix at placement only | test fails |
| `where` parse | new phrasing in ch30.yaml | reject test | hard error | loud |
| per-ply loft | TE offset self-intersects | closed-outline test | clamp | test fails |
| foam cavities | boolean leaves slivers | overlap-volume test | assert ≈ 0 | test fails |
| dispatch | lease held by another job | stub test | exit ≠ 0 + holder | loud |
| Blender job | crash mid-run | manifest-last test | `out.tmp`, no rename | loud (no `out/`) |
| stale renders | script or json changed, glb same | key-mismatch test | strict build fails | loud |
| no renders locally | laptop build/tests | regression test | panels omitted | intended |
| viewer | inner plies unreachable | e2e isolate test | ply list | test fails |

No critical gaps remain: every failure mode has a test and fails loud.

### Parallelization

| Step | Modules | Depends on |
|---|---|---|
| Task 0 core fix | `core/` | — |
| layup geometry + scope + export | `guide/` | Task 0 |
| Blender helper + script + payload tests | `compute-fabric-dev/deploy/anvil/jobs/` | — (contract from §5) |
| dispatch script + stub tests | `guide/`, `tests/guide/` | layup export |
| build_site `--renders` | `guide/`, `tests/guide/` | layup export |
| viewer ply list | `guide/viewer/` | layup export |

- **Lane A:** Task 0 → layup → dispatch → build_site. These run in sequence because they share `guide/`.
- **Lane B:** the Blender helper and script, in compute-fabric-dev, independent of Lane A.
- Launch A and B in parallel. The viewer ply list (Session 3) follows the layup export.
- Conflict flag: A's dispatch and build_site both touch `guide/`, so keep them sequential.

### Implementation tasks

- [ ] **T0 (P1, human ~4h / CC ~30min)** — core — Rotate station wires into XZ at placement; volume and thickness regression tests. Surfaced by: outside voice OV1. Files: `core/structures.py`, `tests/`. Verify: `pytest` + G-code/DXF suites.
- [ ] **T1 (P1, human ~1d / CC ~45min)** — layup — `guide/layup.py`: `where` parser, `LAYUP_SCOPE`, per-ply numeric-offset lofts, section-ready foam, `shots.json`. Surfaced by: issues 1, 2, 4, 7, 8; OV2, OV3, OV5. Files: `guide/layup.py`, `guide/graph/ch30.yaml`, `guide/graph/components.yaml`, `tests/guide/test_layup.py`. Verify: `pytest tests/guide` + `python -m guide.check`.
- [ ] **T2 (P1, human ~2h / CC ~15min)** — export — nest ply nodes under their components; write `layup.json` + `shots.json`. Surfaced by: D1, issue 8. Files: `guide/export_glb.py`, `tests/guide/test_export_glb.py`.
- [ ] **T3 (P1, human ~1d / CC ~45min)** — blender — `fabric_blender.py` helper, `smoke.py` refactor, `layup_cutaway.py`, atomic output, per-ply shading. Surfaced by: issue 6; OV4, OV6. Files: `compute-fabric-dev/deploy/anvil/jobs/blender/*`, `deploy/anvil/tests/test_blender_payload.py`.
- [ ] **T4 (P1, human ~3h / CC ~20min)** — dispatch — `render_cutaway.sh` with the render key, lease check, bare script name, and PATH-stub tests. Surfaced by: issues 5, 9; OV6. Files: `guide/render_cutaway.sh`, `tests/guide/test_render_cutaway.py`.
- [ ] **T5 (P1, human ~3h / CC ~20min)** — site — optional strict `--renders`, panels, Layup section and legend; deploy passes `--renders`. Surfaced by: issue 3. Files: `guide/build_site.py`, `guide/viewer/*`, `scripts/deploy_guide.sh`, `tests/guide/test_build_site.py`.
- [ ] **T6 (P2, human ~4h / CC ~30min)** — viewer — ply list with isolate, plus the e2e test. Surfaced by: OV7. Files: `guide/viewer/js/app.js`, `tests/guide/test_viewer_e2e.py`.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | — |
| Codex Review | `/codex review` | Independent 2nd opinion | 1 | issues_found | 8 outside-voice findings, all accepted (OV1 flat core verified independently) |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | clean | 9 issues + 8 outside-voice, 0 critical gaps, all resolved |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **CROSS-MODEL:** Codex surfaced what the Claude pass missed: the degenerate core, foam overlap, ply band merging, render-key coverage, and viewer occlusion. One tension with D1 (viewer plies unreachable) was resolved by adding a ply list, which keeps the D1 choice.
- **VERDICT:** ENG CLEARED — ready for writing-plans.

NO UNRESOLVED DECISIONS
