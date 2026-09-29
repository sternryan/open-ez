# Long-EZ Interactive Build Guide — M2 "Layup cutaway" (Roncz canard)

Status: DRAFT 2026-09-29, design approved in session, written spec awaiting review

## 1. Intent

M1 §2 commits one spatial explanation as M1's direct successor: the canard layup cutaway, linked to
its steps and rendered through the headless-Blender GPU payload. Timeboxed.

The cutaway answers "what is inside the canard, and in what order was it laid", which is the thing
the plans figures show worst. It has two views of one scene:

- **Hero section stack:** chordwise slices at two stations showing core, shear web, spar caps and
  skins, every ply a distinct band in lay order, so the spanwise ply change is visible.
- **Per-op highlight frames:** the same 3D cutaway rendered once per layup op, with that op's plies
  highlighted and everything laid earlier shown, everything later absent.

**Acceptance test (legibility):** on the hero, at iPad size, someone reading it cold can count the
plies in each skin and see that BL 5 carries more plies than BL 40. Ryan judges this on the iPad;
the builder does not self-grade it.

## 2. Scope

In: Roncz canard (ch 30) layup ops that carry `materials`, plus both spar-cap ops.

Out: GU (ch 10) layups; the 9-BID nut-plate pads and rear-tab detail (local features, not at the
section stations); animation; fixing open-ez canard dimensions (§8).

## 3. Rulings this design follows

- **CadQuery is the geometry SSOT; Blender output is derived** (throughline capabilities.md,
  "Headless 3D render"). No Blender wrapper, lease client, or second GPU path: add a script to
  `jobs/blender/` and dispatch via `fabric-gpu`.
- **The step graph is the ply SSOT.** Nothing is drawn that the graph does not hold.
- M1 §4 public/private boundary is unchanged. Renders derive from open-ez geometry and our own ply
  data, not the plans, so they are public-safe; any label text still passes `python -m guide.check`.

## 4. Layup geometry (open-ez)

New module `guide/layup.py`:

- Reads `materials` from the ch30 ops and builds per-ply CadQuery solids off `CanardGenerator`'s core.
- **Skins:** offset shells over the core surface, bottom then top, in YAML order.
- **Shear web:** a vertical ply stack at the core split line (ch30 step 7, "cut center cores along
  shear web"), span-limited by each ply's extent.
- **`where` parsing:** each `where` string maps to `(span extent, orientation)` through an explicit
  lookup table (e.g. `"inboard of BL 20"` → `|BL| ≤ 20`, `"full span"`, `"45 degrees"`). **Unknown
  phrasing is a hard error, never a guess.**
- **Spar caps:** `r30.bottom-spar-cap` and `r30.top-spar-cap` have no verified ply count in the graph.
  They render as the trough filled with one solid labelled "UND, count not verified", with
  `verified: false` on the node. open-ez's `spar_cap_plies = 17` is a main-wing value and is not used.
- **Thickness:** config ply thicknesses (UND 0.009", BID 0.013") set order only. Rendered bands use a
  fixed exaggerated visual thickness, and every view carries a "not to scale" callout. At true scale
  a 4-ply skin is ~0.04" on a 17" chord, which is invisible.
- **Stations:** BL 5 (inside every inboard drop) and BL 40 (full-span plies only).

**Export:** `guide/export_glb.py` adds ply nodes named `<component>.p<n>` (e.g.
`canard.skin_bottom.p1`) and writes a sidecar `layup.json`:
`node → {component, op, cloth, order, extent, verified}`. The Blender script and the viewer both read it.

**Fidelity:** `canard.shear_web`, `canard.skin_bottom`, `canard.skin_top`, `canard.spar_cap_bottom`
and `canard.spar_cap_top` move from `no-geometry` to `unvalidated`. Ply counts are verified against
ch30; geometry stays unvalidated (§8).

## 5. Render job (anvil)

Script `compute-fabric-dev/deploy/anvil/jobs/blender/layup_cutaway.py`, beside `smoke.py`, deployed
by hand to `/opt/fabric/jobs/`.

- **`in/`:** `longez.glb`, `layup.json`, `shots.json` (the two hero stations plus one frame per layup
  op: shear web, bottom spar cap, bottom skin, top spar cap, top skin).
- **Per shot:** import, solidify thin surfaces before any boolean (known CadQuery trap), MANIFOLD
  boolean cut at the station plane, one material per class (UND, BID, foam, not-verified), camera
  framed **from the cut face's bounds** looking spanwise with a slight 3/4 offset (fixes the smoke's
  y/z-centred framing). Op frames keep earlier ops at full colour, the highlighted op accented, later
  ops hidden.
- **`out/`:** one PNG per shot at 1600×1200; `manifest.json` (shot → file, sha256, input glb sha256);
  `log.txt` with payload stdout (Nomad alloc logs are GC'd within seconds while anvil disk is >80%).
- GPU required (`BLENDER_REQUIRE_GPU=1`); CPU fallback fails the job.

**Dispatch:** `guide/render_cutaway.sh` (open-ez), HITL only, never on a timer.

1. `ssh anvil flux-lock-status`; if another job holds the lease, print the holder and exit non-zero.
   No retry loop.
2. Stage inputs to `/srv/gpu-jobs/blender/layup-<glb-hash>/in`.
3. `fabric-gpu run blender.sh layup_cutaway.py <job_dir> --expect-s N` (flags after positionals).
4. Pull `out/` to `~/.cache/long-ez/renders/<glb-hash>/`.

Renders are **not committed**. The site build copies them in and `scripts/deploy_guide.sh` ships them.

## 6. Guide wiring

- Each layup op page gets a **Cutaway** panel with its highlight frame.
- A canard-level **Layup section** view shows both hero stations side by side, with a legend: cloth
  colour, lay-order numbers, "not to scale", "spar cap count not verified".
- `build_site.py` reads `manifest.json`. **The build fails** if an op with `materials` (or a spar-cap
  op) has no render, or if the manifest's glb hash does not match the current glb, so a stale render
  cannot ship silently.
- The three.js viewer gets the ply nodes as selectable meshes, mapped via `userData.name` (GLTFLoader
  strips dots from node names).

## 7. Testing and definition of done

**open-ez pytest:**
- `where` parsing, including rejection of unknown phrasing.
- Ply order equals YAML order per op.
- The BL 5 section intersects every inboard-limited ply; BL 40 intersects none of them.
- Glb node names round-trip through `read_glb_node_names`; `layup.json` covers every ply node.
- Spar-cap nodes carry `verified: false`.
- `build_site` fails on a missing render and on a glb-hash mismatch.

**compute-fabric-dev:** extend `deploy/anvil/tests/test_blender_payload.py` to check the shot and
manifest contract without a GPU.

**Definition of done:**
1. Both suites green, run with the documented commands.
2. One live `fabric-gpu` run on anvil: `CYCLES_DEVICE=OPTIX`, `GPU_JOB_RESULT rc=0 restore=restored`,
   vLLM identity probe passing afterwards.
3. Deployed; the Cutaway panels and Layup section load at https://nas.tail857f5c.ts.net:7485 over the
   tailnet.
4. Ryan passes the §1 legibility test on the iPad.

## 8. Known accuracy issue (logged, not fixed in M2)

open-ez's canard is 147" span, 17"→13.5" tapered chord, 13.5° LE sweep (`config/aircraft_config.py`),
while ch30 op text references a 130" jig surface. The canard planform needs a plans check before
anyone reads dimensions off the cutaway. The cutaway is a **topology picture, not a dimensioned
drawing**, and says so. Aero and dimension fixes stay out of scope, as in M1 §9.

## 9. Timebox

**Two working sessions.**

- **Session 1:** layup geometry and export, `layup_cutaway.py`, one hero still from a live run.
  **Gate:** if the hero fails the §1 legibility bar at the end of session 1, the hero switches to a
  flat SVG drawn from the same CadQuery slice (no GPU), and Blender keeps only the per-op 3D frames.
- **Session 2:** per-op frames, guide wiring, deploy.

Anything unfinished at the end of session 2 is cut, not extended.
