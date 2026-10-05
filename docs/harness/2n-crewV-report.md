# Crew V report: room cull + M2.9 nits (Part B, Tasks 5, 6, 7a-c)

Worktree `vis`, nothing committed. Task 7d not done (out of scope).

## What changed
**Task 5 (per-plane room groups + cull rule)**
- New `guide/lab/src/logic/roomCull.ts` (`roomPlanes`, `hiddenPlanes`, `blocks`), new `guide/lab/tests/roomCull.test.ts` (the plan's 6 tests; failed on missing module first, then 6/6).
- `scene/workshop.ts`: `Batch` has a `plane` setter, merges per (plane, material), `flush` takes the plane groups. Groups `room.back/door/window/side/ceiling` hold the wall, wainscot, window, frame, sill, pegboard + tools + back-wall shelving/bins/LED/lamp, ceiling, beams, fixtures. Floor, seams, rack, chest, table, jig stay in the shop group (never culled). `Workshop` now returns `planes` and `planeGroups`. Mesh names unchanged (`shop.<mat>`). parity/smoke counts did not move (no edit needed).
**Task 6 (apply per frame + e2e)**
- `main.ts`: `applyCull()` runs at the top of `render()` (so it also covers `setCamera`, `zoomTo`, tours, recorder), visible flag set only on change; binary hide, no transparency; shadow map not dirtied. Hooks `__lab.room()`, `__lab.zoomTo(d)`, `__lab.opIds()`; test-only `?nocull=1`.
- e2e: `_lab_session`, `_step_to`, `_subject_pixels` (new thin wrappers), `test_max_zoom_out_subject_pixels_hold` (1180x820 dpr1, 390x844 dpr2, ops f19.shear-web, f24.gap-seal, f24.aft-cover, f25.paint-seals, f14.fit-fuselage), `test_max_zoom_out_fails_without_cull`, `test_every_op_at_max_zoom_out_has_no_blocking_wall`.
- Deviations: the plan's `f12.canard-install` does not exist (ch12 ids are `c12.*`), so I used `f14.fit-fuselage`. f25 ops change a material, not a part, so for `f25.*` the subject is the airframe skins (fuselage./wing./strake./winglet./nose./engine./cover. prefixes). The sweep covers both subjects (192 fuselage + 30 canard = 222 ops, not 232; `opIds()` is the current subject's op bar).
**Task 7**
- (a) gap-seal: `GHOST_OPACITY` / `m29GhostOpacity` in `logic/finish.ts` (0.4 for `f24.gap-seal` only), `PlyLook.ghostA` in `core/composite.ts`, used in `fuselageBay.ts` for the faint context of that op; view az 10 -> 160, el 55 -> 40.
- (b) aft-cover: dist 125 -> 60 (plan said about 80; 80 gave only 1.43 % / 0.68 %), el stays -8.
- (c) f25 WHOLE(): focus (60,0,16) -> (18,0,4), dist/el/az unchanged. Eye is clamped at 390 so az changes did nothing there; only the focus moved the canard tip out from under the dock.

## Before / after pixels (f19.shear-web, max zoom-out, subject pixels, chromium; webkit within 1 %)
- 1180x820: before cull 0 (framed 10598); after 4216 (WebKit 4249). Floor 400.
- 390x844 dpr2: after 11246 (WebKit 11707), floor 1600.
- Before the cull `blocks` was `['room.door','room.side','room.ceiling']` (nocull test); the first run stopped on the pixel assert (0 < 400), the blocks assert after it.
- Others after cull, 1180: gap-seal 973, aft-cover 1152 (pre-7b), f25.paint-seals 81073, f14.fit-fuselage 6794.

## Honest flags
1. **7a pixel test cannot fail first with the plan's metric.** Subject-vs-12px-ring contrast at f24.gap-seal is 52.1 (1180) / 34.0 (390) against f24.console-lc1 4.4 / 12.2, so it already passes at 0.6x. The test stays as a guard (`test_m29_gap_seal_is_not_washed_out`). The fail-first gate is the node test in `m29.test.ts` (opacity floor for that op only, az 130-190, el 40), which failed on the missing export. The real wash-out is the context (ring luminance 173), not the subject. Needs a visual call.
2. **7b needed dist 60, not 80** (shares at 60: 2.62 % at 1180, 1.22 % at 390).
3. **7c test ground truth:** "card" = `#dock` (readout + step), tip = outer 20 % of each installed canard half's world box along its long axis. At 1180 it never failed; at 390 it failed on all five f25 ops until the focus moved. WHOLE() no longer frames the whole airplane at 1180 (the canard is big at left, tail out); visual review should judge. Alternative if rejected: leave WHOLE alone and dock the card on top at phone width.
4. **Sweep timing (222 ops, dt 0.55 steps, loaded Mac, load avg about 8):** chromium 144.9 s, WebKit 37.4 s. Over the plan's 90 s budget on chromium only; not sampled per chapter, your call.
5. One WebKit boot timeout (`test_part_labels_follow_the_build_the_camera_and_the_toggle[webkit]`, 60 s wait_for_function) in the full run; passed alone on re-run. Load flake, not related.

## Commands and results
- `cd guide/lab && node --import tsx --test tests/roomCull.test.ts`: pass 6, fail 0 (after a failing run on the missing module).
- `cd guide/lab && npm test`: tests 259, pass 259, fail 0 (final). `npx tsc --noEmit -p .` clean.
- `node --test guide/viewer/tests/*.test.mjs`: tests 50, pass 50, fail 0.
- Full Mac e2e: `python -m pytest tests/guide/test_lab_e2e.py -s -p no:cacheprovider -q` (chromium+webkit): `5 failed, 369 passed in 6099.59s`. The 5 = 4 aft_cover (dist 80, since fixed) + the WebKit boot flake. After the dist-60 fix, `-k "aft_cover_reads or (part_labels_follow_the_build and webkit)"`: `5 passed, 369 deselected in 98.60s`. The full file was not re-run after that one-number change.
- Focused: `-k "max_zoom_out or every_op_at"`: 8 passed (before the 7 changes); `-k "chromium and dock_card_does_not"`: 10 passed.

## Screenshots (WebKit, never commit)
`(session scratchpad, not committed) vis-shots/final/` : f19.shear-web-zoomout, f24.gap-seal, f24.aft-cover, f25.paint-seals, each at `-1180x820.png` and `-390x844.png`. Earlier `before/` (pre-7) and `after/` (pre-dist-60) sets are in the same parent.

## Proposed commit split (stage by name, no trailer)
1. `feat(lab): cull the room walls the eye is outside of`: `guide/lab/src/logic/roomCull.ts`, `guide/lab/tests/roomCull.test.ts`, `guide/lab/src/scene/workshop.ts`, `guide/lab/src/main.ts`, `tests/guide/test_lab_e2e.py` (room-cull block only, the first appended section). Message body: f19.shear-web max zoom-out subject px 0 -> 4216 at 1180x820; 222-op sweep, per-plane groups, binary hide.
2. `fix(lab): m29 visual nits (gap-seal context, aft-cover size, canard tip clear of the dock)`: `guide/lab/src/logic/finish.ts`, `guide/lab/src/core/composite.ts`, `guide/lab/src/fuselageBay.ts`, `guide/lab/src/fuseShots.ts`, `guide/lab/tests/m29.test.ts`, `tests/guide/test_lab_e2e.py` (the nits block). Note `test_lab_e2e.py` holds both blocks, so either split with `git add -p` or take it in commit 1 and 2 together; `main.ts` also carries only cull changes.

---

# Round 2 (supersedes the round-1 nit fixes and the round-1 commit split)

Cull untouched. Final state: `git status` shows only the files below (never stage `guide/lab/node_modules`, a symlink).

## What changed
- **Outside shots (plan 7d):** `Shot.outside` / `FuseView.outside`; `rig.scaled` skips `clampPos` for them; `rig.outsideScale` (1.8 on portrait, else the normal scale) because the room pull-back cannot fit the 8 m wing span in 390 px; `rig.onShot` lifts `controls.maxDistance` to the shot's own distance and puts it back to 7.5 m for every other shot. Tagged: the five f25 ops (WHOLE: focus (60,0,16), dist 800, el 50, az 0, up 150), `f19.attach` (same framing), `f24.aft-cover`. The round-1 focus move (18,0,4) is reverted.
- **f24.aft-cover:** outside, from aft and below (dist 55, el -15, az 270). Shares 2.92 % at 1180, 2.99 % at 390 (floors 2 / 1), `blocks == []`.
- **f24.gap-seal:** context drawn opaque and darkened (`m29ContextDim` = 0.38, `dimColor` colour multiplier, no transparency); seal keeps its colour (x-ray as before). Haze test: mean luminance of the view outside the seal <= f24.console-lc1 x 1.10. Failed first with the ghost path: 140.1 vs limit 128.1 (1180) and 112.9 vs 99.7 (390). Passes now.
- **Black void:** `workshop.ts` adds a 400 m matte `apron` box under the slab (colour 0x4d4a45), in the never-culled shop group. Test `test_m29_outside_shots_show_no_black_void` (f25.paint-seals and f19.attach at 1180x820, near-black < 2 %). Failed first: 55.41 % near-black; after: 0.12 % / 0.13 %.
- **Whole-airplane test:** `test_m29_whole_airplane_fits_clear_of_the_card` (5 f25 ops + f19.attach, both sizes): both wingtips, both canard tips, the nose (fuselage side end away from the firewall) inside the viewport, clear of `#dock`, and `blocks == []`. Not shown failing first on the old build: the old views were replaced before the test existed; the round-1 failure was the captain's visual review.
- **Sweep:** WebKit sweeps all 222 ops (37 s), chromium one op per chapter. Max-zoom tests now call `zoomTo(99)` (clamped to the orbit range: 7.5 m for inside shots, the shot's distance for outside shots). f19.shear-web numbers unchanged (4216 / 11246).
- **Floors moved, with reason:** m27 `f19.attach` subject floor 100 -> 10 (whole-airplane shot, bolts are a few pixels); m29 finish test `top >= 3000` -> 1500 (airplane stands further back, was 2114).
- Round-1 contrast test and dock-card tip test are gone (superseded).

## Verification
- `cd guide/lab && npm test`: tests 259, pass 259, fail 0. `npx tsc --noEmit -p .` clean.
- Full Mac e2e, run-job/await-job, unpiped, final build (with apron): `1 failed, 379 passed, 56 warnings in 6662.91s (1:51:02)`. The one failure is `test_frame_time_median_while_dragging_the_section_on_the_low_tier[chromium]`, a software-GL frame-time budget on a machine at load average about 8; the same single test failed in the previous full run (pre-apron). Not run on a clean baseline, so I cannot say it is pre-existing. The previous 35 `Page.goto` timeouts in an earlier full run were a transient stall and did not recur.
- Screenshots (WebKit): `vis-shots/r2/` (f19.shear-web-zoomout, f19.attach, f24.gap-seal, f24.aft-cover, f25.paint-seals at both sizes, pre-apron) and `vis-shots/r3/` (f25.paint-seals and f19.attach at both sizes, with apron), under `(session scratchpad, not committed) `.

## Carried nits (not this round)
- gap-seal stripe clutter; aft-cover at 390 has labels stacked from forward parts; f19.attach's bolts read small at whole-airplane framing; leaving an outside shot snaps the camera back inside the 7.5 m orbit range on the first frame of the flight (not seen in review, not tested).

## Final commit split (no trailer)
**Commit 1, `feat(lab): cull the room walls the eye is outside of`:**
- whole files: `guide/lab/src/logic/roomCull.ts`, `guide/lab/tests/roomCull.test.ts`, `guide/lab/src/scene/workshop.ts` (the apron hunk is in this file; it is harmless to commit 1 but really belongs with commit 2, so use `git add -p` and leave the two `apron` hunks, the `apron:` material line and the `B.box('apron'...)` line, for commit 2)
- `guide/lab/src/main.ts` hunks: the `roomCull` import; the `LabHook` doc/members `room`, `zoomTo`, `opIds`; the hook defaults; the `noCull`/`applyCull` block and `applyCull()` in `render`; `shopCull = ...` after `scene.add(shop.group)`; `hook.room`/`zoomTo`/`opIds`. Skip the two round-2 hunks (`rig.onShot = ...` and `rig.outsideScale = ...`).
- `tests/guide/test_lab_e2e.py`: only the region from `# ---- room cull` through `# ---- END room cull block ----` (one contiguous hunk at the end of the file; use `git add -p` and take that hunk alone).
**Commit 2, `fix(lab): visual pass nits (outside whole-airplane shots, gap-seal context, aft cover, ground apron)`:**
- `guide/lab/src/camera.ts`, `guide/lab/src/core/composite.ts`, `guide/lab/src/fuselageBay.ts`, `guide/lab/src/fuseShots.ts`, `guide/lab/src/logic/finish.ts`, `guide/lab/tests/m29.test.ts`
- `guide/lab/src/scene/workshop.ts` apron hunks, `guide/lab/src/main.ts` the two round-2 hunks
- `tests/guide/test_lab_e2e.py`: everything after `# ---- BEGIN nits block` plus the three edited floors in older tests (m27 `floor` lambda and the `wing.attach >= 10` line, m29 `top >= 1500`, and the unchanged-but-checked aft-cover 3000 row).
Commit 1 builds and passes on its own: its test block uses only helpers defined inside it, `_step_to`, `_pixels_of` and existing fixtures. (Not run in isolation; staged-subset check is the captain's.)

---

# Round 4 (supersedes the round-2 commit split)

## Changes
- **f19.attach** is back to its pre-round-2 framing (no `outside`), its subject floors are back to 100 px (m27 tests untouched against origin), and it is out of the whole-airplane and black-void tests. Carried nit: wing tips are cut at this op (room clamp).
- **m29 finish `top` floor 3000 -> 1480** (0.7 x the smallest in-test value, 2114 on WebKit; chromium 2160). Before the camera moved: 24727 (chromium, 1180x820, old WHOLE view; floor was 3000). The test now prints it. Per-op values in a bare session with the new framing (diff px of top skins, finish colour changes how much the diff sees): 1180: inspect-repair 17246, coarse-fill 584, feather-fill 584, primer 15127, paint-seals 966; 390: 6525, 364, 367, 5675, 441. Only paint-seals is the asserted op; the floor moved because the camera moved (whole-airplane framing, Ryan's nit).
- **Red-first for the whole-airplane test:** with the pre-round-2 `WHOLE()` (`finAt(60,0,16,200,25,35)`, no outside) in the tree: `10 failed, 2 passed` (chromium), all ten `test_m29_whole_airplane_fits_clear_of_the_card[chromium-f25.{inspect-repair,coarse-fill,feather-fill,primer,paint-seals}-{1180-820,390-844}]` FAILED. The old view was then removed; my views are back and the test passes.
- **Frame-time regression, root cause (a):** the per-plane groups split every merged batch (and (b) the apron was always drawn). Fix: `Batch.flush` now builds one merged mesh per material holding everything (the pre-cull draw count) PLUS per-plane meshes and a `.rest` mesh only for materials with plane parts; `Workshop.setHidden(hidden)` shows the combined set while the eye is inside, and the plane/rest/apron set only while some plane is hidden. The apron is a separate mesh, visible only then. `applyCull` calls it only when the hidden set changes (a sorted-key compare).
- **Regression test** `test_room_cull_adds_no_draw_calls_while_the_eye_is_inside`: r30.top-skin, eye inside: calls 47 (clean origin/main 2aee2d3: 47), limit 47 + 2, `hidden == []`, `apron == False`. Not shown red on the old build (that build was replaced by the fix; the captain's pre-fix evidence was 67 calls / median 33.3 ms in the frame-time test).
- **Frame-time test** (`...low_tier[chromium]`): 3 of 3 passed on vis, median 16.7 ms each, stats calls 63 (clean origin/main: calls 63, median 16.7, pixels 40080; the captain's failing vis run read calls 67, 33.3 ms).

## Verification
- `cd guide/lab && npm test`: tests 259, pass 259, fail 0.
- Commit 1 in isolation (temp worktree from origin/main 2aee2d3, only commit-1 files/hunks, node_modules symlinked, removed afterwards): lab unit `tests 258, pass 258, fail 0`; e2e `-k "max_zoom_out or every_op_at_max or room or frame_time_median_while_dragging"`: `12 passed, 336 deselected in 226.75s` (both engines; sweep chromium 23 ops 15.0 s, WebKit 222 ops 28.2 s; draw calls 47, apron False).
- Full Mac e2e, run-job/await-job, unpiped, final tree: `378 passed, 56 warnings in 4602.45s (1:16:42)`.

## Carried nits
Wing tips cut at f19.attach (room clamp); gap-seal stripe clutter; aft-cover at 390 stacked labels from forward parts; f19.attach bolts small was dropped (framing reverted); first-frame camera snap when leaving an outside shot (untested).

## Final commit split (no trailer)
**Commit 1: `feat(lab): cull the room walls the eye is outside of`** (verified in isolation, above)
- `guide/lab/src/logic/roomCull.ts`, `guide/lab/tests/roomCull.test.ts` (new)
- `guide/lab/src/scene/workshop.ts` (whole file: plane groups, combined/rest meshes, apron, `setHidden`)
- `guide/lab/src/main.ts`: everything except the two round-2 hunks, which are the comment+`rig.onShot = ...` lines and the `rig.outsideScale = ...` line in `resize`
- `tests/guide/test_lab_e2e.py`: the one appended region from `# ---- room cull` to `# ---- END room cull block ----` (includes the draw-call regression test). No other hunk.
**Commit 2: `fix(lab): visual pass nits (whole-airplane finish shots from outside, gap-seal context, aft cover)`**
- `guide/lab/src/camera.ts`, `guide/lab/src/core/composite.ts`, `guide/lab/src/fuselageBay.ts`, `guide/lab/src/fuseShots.ts`, `guide/lab/src/logic/finish.ts`, `guide/lab/tests/m29.test.ts`
- `guide/lab/src/main.ts`: the two round-2 hunks (`rig.onShot`, `rig.outsideScale`)
- `tests/guide/test_lab_e2e.py`: the region from `# ---- BEGIN nits block` to end of file (haze, aft-cover, whole-airplane, black-void tests) and the one-line `top` floor edit in `test_m29_the_finish_goes_on_in_stages...` (print plus `>= 1480`, docstring-comment: moved because the camera moved).
