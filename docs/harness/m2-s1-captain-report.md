# M2 session 1: captain report (Tasks 1–6)

All six tasks are **done**: each was re-verified by the captain and committed. Nothing was pushed and nothing touched the GPU host, the home server or any remote host. No commit carries a trailer.

## Per task

| Task | Status | Commit | Verify (captain re-run) |
|---|---|---|---|
| 1 Core is a real solid | done | open-ez `053f619` | `tests/test_core_solid.py` 1 passed; full suite `1 failed, 343 passed, 2 skipped`. The failure is pre-existing, see below. |
| 2 Layup data, scope, shots | done | open-ez `2aa3ac8` | `tests/guide` 122 passed; `source ~/.config/long-ez/env && python -m guide.check` gives `OK`, `EXIT=0` (202 texts, recall 5/5) |
| 3 Ply solids + foam | done | open-ez `8ca32f2` | `tests/guide` 130 passed (`test_layup_geometry.py` 8 passed) |
| 4 Nested export + layup/shots json | done | open-ez `1b7369d` | `tests/guide` 134 passed; the viewer e2e ran (8 tests), none skipped |
| 5 Blender job (the render-tooling repo) | done | the render-tooling repo `39ed122` | `python3 -m pytest deploy/<gpu-host>/tests -q` 200 passed; ast parse OK |
| 6 Render key + render_cutaway.sh | done | open-ez `630afa2` | `tests/guide` 146 passed |
| (fix) test paths anchored | done | open-ez `ab913fc` | `tests/guide` 146 passed from the repo root AND from /tmp |

Done-means commands, final captain run:
- `.venv/bin/python -m pytest -q -p no:cacheprovider`: `1 failed, 389 passed, 2 skipped`.
  - The one failure is `scripts/assembly_test.py::test_full_assembly`: `TypeError: Can't instantiate abstract class AircraftAssembly without an implementation for abstract method 'manufacturing_plan'`.
  - It also fails at the session-start baseline on a clean tree (1 failed, 342 passed), so it is unrelated to M2. It was not fixed because it is out of scope.
- `node --test guide/viewer/tests/*.test.mjs`: 12 pass, 0 fail.
- `.venv/bin/python -m guide.check` (with the env sourced): `OK`, `EXIT=0`.
- `cd <render-tooling repo> && python3 -m pytest deploy/<gpu-host>/tests -q`: 200 passed. It also passes from `~`.

## Deviations from the plan

1. **Method: task text was referenced, not pasted.** Implementer prompts pointed at the committed plan by exact line range instead of pasting about 450 lines. Global Constraints and Interfaces were pasted inline.
2. **Commits by the captain.** The `verify-before-commit` hook blocks subagent commits, because subagents earn no marker. The blocked hook also unstages files. So crew left their work uncommitted and the captain committed after re-verifying. For Task 1, this thread's Bash cwd was pinned to the render-tooling repo, so the commit used `git -C`. The cwd moved to open-ez afterwards.
3. **Task 2: scope restricted to chapter 30.** The real graph has materials rows in `ch10.yaml` (the GU canard), which the plan's `material_rows` would have treated as unscoped.
   - The fix adds `LAYUP_CHAPTER = 30` and filters on `Operation.chapter`, plus a real-data test, `test_other_chapters_are_out_of_scope`.
   - Signatures are unchanged. The lead accepted this and corrected the comment: ch 10 is the GU canard, not the main wing.
4. **Task 3: `Planform.surface` split.** The airfoil coordinates are a closed loop that starts at the LE. The plan's `argmin` split produced a one-point top surface.
   - Both sides now run LE to TE (split at the LE and TE, with wrap), and the repeated LE point is dropped.
   - Vertex counts are stable across BL (top 98 / bottom 96), so the ruled lofts match.
5. **Task 3: foam base (lead-accepted).** Cutting the generator's BSPLINE core returned garbage: 766.8 in³ out of a 598.6 core, negative fragments, and a 0.05-in sliver at BL 5. The plan's tests still passed.
   - The foam is now a ruled loft of `Planform.outline`, cut by cavity tools padded with `CUT_PAD = 0.05 in` so no tool face is coplanar with the skin surface. The loft is within 0.08% of the true core volume; the planform is linear in BL, so it is the same solid.
   - New tests: volume conservation, a BL 5 section check (whole chord, cavities present), and a check that the cutters overshoot the surface (added by the captain).
   - `cq.Shape.Volume()` under-reads the BSPLINE core (598.6 against 698.6 from BRepGProp), so the tests use a `vol()` helper. Task 1's `Volume() > 100` assertion still holds despite the under-read.
6. **Task 1: extra assertion.** Added `bb.zmax > abs(bb.zmin)` so a flipped (-90°) rotation fails. This was a reviewer suggestion.
7. **Task 4: extra test.** Added `test_real_export_nests_plies_and_keeps_inches`. It pins that each ply is parented under its component (the viewer's parent walk depends on this) and that the accessor Y span is 0..73.5 in inches (Review Focus 1, laptop side).
8. **Tests anchored to the repo root.** Every new M2 test was cwd-relative, as written in the plan, and failed from another directory (17 failed, 6 errors). They are now anchored with `ROOT = Path(__file__).resolve().parents[2]`, the M1 idiom. Only test files changed.
9. **Tracked outputs rewritten by the suite.** Test runs rewrite `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json` (timestamps only). They were restored with `git checkout` before every commit and never committed. This is worth a follow-up: either the tests should write to tmp, or the files should be untracked.

## Escalations

- **None to opus.** Every review finished within 2 rounds on sonnet.
- The one real defect, the foam boolean, was caught by the round-1 sonnet reviewer, not by the plan's tests. The cheaper tier did not miss it.
- The Task 2 implementer stopped correctly on the ch10 surprise instead of weakening a test.
- Task 7 must not repeat one captain slip: my first ruling to the crew called ch 10 "main wing". The lead corrected it before commit.

## What the lead must know before Task 7 (live the GPU host run)

1. **The glb axes and units look right for `check_axes`.** The export keeps inches, and accessor Y runs 0..73.5. The root node `longez` carries a -90° X rotation (Z-up to Y-up), which Blender's glTF import should undo, leaving scene Y at 0..73.5. This is unproven until the live run, where `check_axes` fails loud if it is wrong.
2. **glTF node names are flat**, e.g. `canard.shear_web.p1` with no `/` prefix. Task 11's `nm()` needs no last-segment handling.
3. **Deploy all three sibling scripts together.** `smoke.py` and `layup_cutaway.py` import `fabric_blender.py` and `layup_contract.py` from their own directory. `blender.sh` reads `<deployed scripts dir>/blender` (`BLENDER_SCRIPTS_DIR`), which matches `render_cutaway.sh`'s `DEPLOYED`. `fleet.yaml` does not deploy that directory; it is a manual `install`, as in plan step 2.
4. **`render_cutaway.sh` against the real tooling** (Task 6 reviewer, desk-checked only):
   - `lease-status` returns 0 when free, 3 when held and 4 when wedged. Any non-zero maps to exit 3 "GPU lease busy". So a missing `lease-status` (rc 127) or an ssh failure would also report "busy". Check `ssh <gpu-host> 'command -v lease-status'` first; it was a hand install to `/usr/local/bin`.
   - If a deployed script is missing, the sha step dies under `set -e` with rc 1, not rc 4.
   - `gpu-runner run --no-wait` returns at dispatch, so if the payload dies early the laptop polls for `EXPECT+300` s before exiting 5. `gpu-runner status <id>` gives the cause faster.
   - `gpu-runner` needs `~/.config/fabric/nomad-dispatch.token` or `$NOMAD_TOKEN`.
   - The stub prints `LEASED —` while the real tool prints `HELD  —`. Only the exit codes matter to the script.
5. **Blender-side risks** (Task 5 reviewer, desk-checked, bpy never run):
   - `solidify_if_thin` only acts when a dimension is below 1e-4, which is fine for real ply solids.
   - `section_bounds` and `band_centre` match cut vertices at `|y-bl| < 1e-3`. If the job fails with "produced no section face", loosen that tolerance.
   - `read_factory_settings` runs per shot; confirm the cycles addon is still enabled afterwards (the GPU guard fails loud if not).
   - An op shot with `upto: null` would raise a bare `TypeError`, because `load_inputs` does not validate `upto`. Real `shots.json` always sets it.
   - `log.txt` is opened in append mode. The job dir is restaged fresh on each run, so this is fine.
6. **Section appearance.** Foam fills the 0.03-in `PLY_GAP` between shear-web plies, so the web shows as thin foam-coloured separators between the bands. This is the intended visual separator, but the lead should know it when judging the hero.
7. **the render-tooling repo moved.** Another lane committed `4b7c15a` on top of our `39ed122`. Ours is intact. The two other-lane untracked docs were never touched.
