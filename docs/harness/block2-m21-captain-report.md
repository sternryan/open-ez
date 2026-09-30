# Block 2 milestone 2.1: captain report (Tasks 1–6)

Plan `docs/superpowers/plans/2026-09-30-block2-m21-build-progression.md`, Tasks 1–6; spec §3. Method:
a sonnet implementer, then a sonnet reviewer, then at most one sonnet fix round per task, then the
captain re-verified and committed. The captain took and looked at Playwright screenshots (1180 px
and 390 px) of the real export before each UI commit. No reviewer escalated to opus: every review
converged in one fix round.

## Done-means (re-run by the captain at 700ae76)

- The full suite, `pytest -q -p no:cacheprovider --deselect scripts/assembly_test.py::test_full_assembly`, gave **609 passed, 2 skipped, 8 xfailed**. It took 328 s. The baseline at af5841d was 495 passed, 7 xfailed; the xfail count moved with the physics lane's merges, not with this work.
- `node --test guide/viewer/tests/*.test.mjs` gave **50/50**.
- `guide.check`, run with the env sourced, printed **OK**.

## Per task

| # | Status | Commit | Verify tail |
|---|---|---|---|
| 1 build state | done | ded63d6 | node 28/28; suite 499 passed |
| 2 scrubber, ghost, play | done | 8070fb3 | node 28/28; suite 517 passed |
| 3 section cut + readout | done | c67058b | node 35/35; suite 548 passed |
| 4 load paths | done | 59e153c | node 39/39; suite 569 passed; guide.check OK |
| 5 chapter tours | done | 1ba827b | node 50/50; suite 605 passed; guide.check OK |
| 6 frame budget + phone | done | 700ae76 | node 50/50; suite 609 passed |

**1. Build state (`visibleSet`, `firstOp`).**
- The rules follow the plan.
- An unowned mesh throws, and so does an op that isn't in the variant.
- A real-data test runs every op of both variants against a fresh export. It checks two things:
  - At each op, the number of `current` meshes equals the op's ply count.
  - At each op, every mesh reads hidden, then current, then built, in that order and never backwards.

**2. Scrubber, ghost and play.**
- Every change recomputes the build state from scratch.
- Test hooks exist only under `?test=1`.
- **Screenshot finding:** at 390 px the chips and build bar covered the model, leaving about a 60 px strip.
  - At 820 px and below the controls now sit below the canvas.
  - An e2e checks that at least 300 px of model stays uncovered.

**3. Section cut.**
- The glb is in inches, and B.L. b sits at model Z = −b. This was measured, not assumed.
- The plane normal is (0,0,−1). It sits 1e-3 in toward the root so that a ply ending exactly at the station still caps.
- The boundary rule is `bl <= bl_max`, the same rule as `counts_at`.
- An e2e checks that the capped nodes equal the layup data at BL 5, 20, 30, 40, 54 and 60.
- **Readout:** the review found it listing layers that aren't built yet. It now lists only built and current layers.
- **Performance:**
  - The meshes are merged per ply node when the glb loads, from about 1,800 per-face meshes down to 48 solids.
  - The stencil materials are shared and each cap is scissored to its solid.
  - Median frame time with the section on went from 83 ms to 33 ms.
- `NOTICE` carries airsup's MIT text verbatim; the reviewer diffed it against their LICENSE.
- The `cut.js` header matches the plan.
- **Screenshots:**
  - At the shear-web op, the cut shows the foam, the web plies and the empty spar-cap troughs.
  - At the top-skin op, it shows the layered skins.

**4. Load paths.**
- Every point and every segment midpoint lies within 0.5 in of its parts' solids, checked with BRepExtrema.
- A path appears only when every one of its parts is built or current.
- **Screenshot finding:** the plan's additive 1-px lines washed out to white on the light background.
  - They are now 0.25 in tubes with a scrolling stripe, in amber, blue and green by kind.
  - A pixel test checks the colours in light and dark mode.

**5. Chapter tours.**
- **Order:** `tourSteps` skips stubs. `stepTour(state, dt)` is pure and carries `n` and `dwell` in its state.
- **Camera shots:** the bottom-cap and bottom-skin shots view from below. Otherwise the current bottom plies hide under the core, which the Task 2 screenshots showed.
- **Captain's real run:** the tour visited all 12 non-stub ch30 ops in order at both widths.
- **Stopping:** the tour stops on Escape, an op click, a variant change, the scrubber, Play, isolating a ply, leaving the 3D pane, and a second press.
- **Flake check:** the tour e2e tests passed 5 of 5 captain re-runs, after crew saw one unexplained flake.

**6. Frame budget.**
- **Budget:** a median of 33 ms or less, **never raised**.
- **Cause:** MSAA on a stencilled render target in software GL, 50 ms in 5 of 5 runs.
- **Fix:** `antialias: false` plus `setPixelRatio(min(dpr, 2))`.
- **Result:** a 16.7 ms median on every run. The test also proves the section plane moved, with at least 100 distinct stations sampled.
- **Scene:** 51 draw calls and 23,060 triangles.
- **Phone:**
  - The readout collapses to one line with an ellipsis, and the full text sits in `title`.
  - A copy of the site without that CSS fails 4 of the test's assertions.

## Deviations (all logged)

- **`graph.json` fields:**
  - `graph.plies` rows lacked the `op` field the plan's Global Constraints assumed; `build_site` adds it from `layup.json`.
  - `graph.json` also now ships `layup`, `loadpaths` and `tours`.
- **GU variant:** the exported plies are Roncz r30 plies, so they are **hidden** in GU and not remapped. This matches M2's decision that the GU shear web offers no plies. In practice the GU 3D view shows no layup at any op.
- **Load-path interface:** it changed from `points` to `segments`, a list of polylines. The two caps and the four lift stations can't be drawn as one line without crossing air. The plan's Interfaces block was updated in the same commit (59e153c).
- **Midpoint gate negative test:** it uses 0.25 in, because a wing about 1 in thick can't hold a 0.5 in air gap. The main gate stays at 0.5 in.
- **`counts_at` parity:** `counts_at` counts by component, not by cloth, so parity is asserted both ways.
- **Tests edited, not weakened:** `test_isolate_visibly_ghosts_other_plies_on_screen` had its pixel clip adjusted twice, once for the build bar and once to hide the section bar and paths. Its thresholds are unchanged. The phone-canvas test guards what those edits give up.
- **`#tour` placement:** it sits top-right over the canvas on desktop, not in the build bar.
- **Section slider:** its step is 0.5, so it tops out at B.L. 70.5, not 70.8.

## Open items and notes for Task 7

1. **iPad:**
   - With MSAA off, edges on a DPR-1 screen are aliased; on the iPad the 2x pixel ratio covers it.
   - The fill-rate cost at 2x has not been measured on the device. The headless DPR-2 run is information only (16.7 ms).
   - The 16.7 ms figure is a headless swiftshader proxy, not an iPad measurement; the walk-through is the judge.
2. **The frame-time test is load-sensitive.** It read 66–200 ms when the machine's load average was 75–200. Run the Task 7 gate on a quiet machine.
3. **Not done:**
   - Striping on caps for unverified-position plies. The spec's legend has it; the caps use plain cloth colour.
   - There is no GU layup in 3D.
   - The spec's glb `op`/`lay` tags are not in the export (spec §3.3). The plan chose `layup.json` as the only mapping.
4. **Runtime:** the suite is now about 5.5 min, up from about 50 s. The ~85 e2e tests dominate, and each launches chromium.
5. **Leak scan, not this milestone's code:**
   - `docs/history/idea.md:5` claims the design is in the public domain.
   - `docs/history/REVIEW_PROMPT.md:380` has a home-directory path.
   - Both files were moved there by 05af411 from root files that are already public on origin/main.
   - Both break the public-repo rules. Fix or drop them before the push.
6. **Readout:** the layers it lists (for example "Top skin: 3 UND, 1 BID") come straight from the graph's `materials`. The top-skin summary says "four-ply", which is consistent. Whether 3 UND + 1 BID is right is a Block 1 data question, not a viewer one.
7. **Re-export:** `output/` is untracked now (bca9b0f), so Task 7 must re-export before deploying.
