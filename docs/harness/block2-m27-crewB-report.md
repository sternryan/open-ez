# M2.7 crew B report: the lab for chapters 19 and 20

Branch `m27-crewA` (worktree `open-ez-wt/m27`), three commits on top of crew A, nothing pushed.

## Commits

| Commit | What |
|---|---|
| a0b060d | Task 4: `topo_order` fix and an order test |
| f4dbc3d | Task 5: the lab (`logic/wing.ts`, `fuselageBay.ts`, `main.ts`, shots, controls), export additions, unit tests, kernels fixture |
| (this commit) | Task 5: the m27 e2e tests and this report |

## Task 4: the build order

Cause: `topo_order` walks the ops by (chapter, authored position) and pulls each op's prerequisites in depth first. The walk reached the
chapter 16 op `f16.aileron-linkage` before chapter 17, and that op waits on `f19.controls` and `f19.attach`, so the whole of chapters 19
and 20 (and `f20.rudder-hang` for `f16.rudder-cable-rig`) was pulled in ahead of 17 and 18. No requires edge was wrong; the walk was.

Fix (`guide/schema.py`): an op that waits on chapters 19 to 29 is walked with the chapter it waits on, after that chapter's own ops.
Chapters 30 and up (canard revisions) and the older earlier-chapter pulls (the spar before the firewall bond, F22 before the gear) keep the plain
pull-in behaviour, so nothing in chapters 4 to 18 moves. Result: ch16 (less two ops), ch17, ch18, ch19, `f16.aileron-linkage`, ch20,
`f16.rudder-cable-rig`, then `f16.brake-cables` and `f16.adjustable-pedals` (they wait on the rudder rig). The two deferred ch16 ops sit
right after the chapter they wait on, not at the very end; that is where their prerequisite is satisfied and I judged it the more honest
reading of "deferred". Test: `test_book_order_the_wing_waiters_follow_their_chapter` in `tests/guide/test_ch20_graph.py`.

Moved assertion (mine to move, crew A's new test): `test_order_and_the_rudder_stub_is_replaced` listed `f20.lower-fin` last in chapter 20. That
was an artefact of the old walk (the rudder chain was pulled in first). The authored order, and the spec's wording, put the lower fin before
the rudder cut. No chapter 4 to 18 assertion moved.

## Task 5: what the owner sees

- `guide/lab/src/logic/wing.ts` (pure): placement per op, left wing and workshop-part windows, aileron and rudder kernels (Rodrigues turn,
  checked against the python poses), swing timings, readout strings, ply schedule from `extras.m27`, weight rows.
- The right wing is on its own bench: the five jigs go on the floor (`f19.jig`), the cores are cut and cut out flat on the table
  (bottom up, leading edge toward the room), then stood leading edge up in the jigs, flat on the table again for the bottom cap and skin,
  back in the jigs for the top cap, conduit, top skin, ribs, aileron and controls. The airplane is not drawn on those ops. `f19.attach`
  returns to the airplane on its gear with both wings; chapter 20 builds the winglet on the right wingtip. The jigs stay on the floor while
  the wing is on the table.
- Plies (web 6, caps 5 and 7, skins 3 and 3, winglet skins 3 and 2, corner layup 7) use the existing lay-down; the scrubber counts only the
  right wing's plies before the attach (the left wing's identical plies wait for it).
- Aileron: slider and the op's own sweep on `f19.aileron-build`, 0 to 20 deg up, "20 deg up: at the stop". Rudder: `f20.rudder-hang`, 30 deg
  either way, positive trailing edge outboard, the belhorn turns with it, the hinge stays. Right side only.
- A, B, C: cyan lines from the WPRP (BL 55.5, FS 149.6) to the three jig targets on `f20.jig`, labelled "A 102.15 in" and so on, with the
  reference point named, plus the closure and the derived lean in the readout.
- Readout text: `f19.cut-cores` (LE printed FS 134.95, FS 134.45 from the chord and TE), `f19.aileron-cut` (BL 54.3 on p171, BL 55.5 cut at the
  foam joint), `f19.attach` (28.85 drawing, 28.83 text), `f19.shear-web` (outboard 2 plies, CP26 LPC 31, plans print 3). Each conflict carries
  "unresolved".
- Reference rows (CP26 builder weights, "reference, not in CG"): aileron from its op, wing 51.5 lb each at the end of chapter 19, lower
  winglet from its op, wing with winglets and rudder 64 lb at the end of chapter 20 (upper winglet 6 lb beside it).
- Buried parts (hard points, the root controls, the attach bolts, the rudder hinge, which is on the outboard face the room cannot see) are
  shown through a faint wing: the op's own parts draw on top, everything else of the wing is translucent.
- Tour: chapters 19 and 20 each have a tour (`director.ts`: card names "Wings", "Winglets and rudders", close on the last op, hold on both swings). The
  fuselage tours live in code, not in `tours.yaml`, so no yaml entry was added.

Small additions outside the lab (needed by it): `guide/fuselage_export.py` m27 section gains `shear_web` (zones, printed outboard count),
`winglet.points` (WPRP and the three targets) and part rows for the two winglet skin ply parts (they had plies but no row, which broke the lab
load); the cores FC1 to FC3 now show from `f19.cut-cores` (they are cut then) instead of `f19.mount-cores`.

## Tests

| Lane | Result |
|---|---|
| Lab unit (`npm --prefix guide/lab test`) | 222 pass (207 before, 15 new in `m27.test.ts`); `tsc --noEmit` clean |
| Viewer (`node --test guide/viewer/tests/*.test.mjs`) | 50 pass |
| Python non-e2e (serial, foreground) | 1147 passed, 3 skipped, 9 xfailed, 1 deselected |
| E2E on the Mac test node, `-k "m27 or m26 or order"` | 66 passed (chromium and webkit), 430 s |
| E2E on the Mac test node, `-k "m25 or fuselage or finished_box or home_view"` | 44 passed, 368 s |

The captain's full two-node fan-out is still to run: I ran only the groups above (m27, m26, the order tests, m25 and the fuselage tests), not the
whole file.

New e2e tests (12, each on both engines): build order and placement per op for every part (both sides), striping and "(fitted shape)" tags,
per-op pixels (the new part changes pixels on its op), three phone shots (`f19.aileron-build`, `f20.jig`, `f20.rudder-hang`), aileron and
rudder travel, the A, B, C lines, the conflict text, the weight rows, ply lay-down counts and order, both tours.

Moved assertions in existing tests: `tests/guide/test_lab_e2e.py` `_bar_ops` and `_fuse_ops` chapter lists gain 19 and 20 (as M2.6 did for 18);
`guide/lab/tests/fuselage.test.ts` fuselage-chapters list gains 19 and 20; `tests/guide/test_export_glb.py` m27 part count 60 to 64 (the two
winglet skin ply parts). `_m25_ops` is left at 14 to 18 on purpose: its expectations are for airplane ops, and the wing bench ops do not draw the
airplane.

Leak scan on `git diff main`: empty. `ruff check` on touched files: no new findings from this crew (the shared venv ruff 0.15 differs from the
0.5.4 pin and reports older style findings in these files on main too; I did not run `ruff format` over `test_lab_e2e.py` or `test_export_glb.py`
for that reason, since it rewrites existing lines). One finding in crew A's code remains (`RUF034`, a useless if-else in the ply cloth lookup).

## Screenshots

`scratchpad/m27-shots/`: WebKit 1180x820 for all 27 chapter 19 and 20 ops (`<op-id>.png`) and phone 390x844 for `f19.aileron-build`,
`f20.jig` and `f20.rudder-hang` (`<op-id>-phone.png`). Not committed.

## Open nits for the captain's visual review

1. Framing is functional, not polished. The wing in the jigs is large and close (it stands 1.6 m high, leading edge up); a few shots
   (`f19.core-cutouts`, root-end ops) are tight, and the control card covers the lower left on the phone.
2. The hinge, belhorn, hard points, controls and attach bolts are a few inches long; their per-op pixel counts are 100 to 500 where the big
   parts give thousands. They read through the faint wing but are small. The test bars are 100 px at 1180 and 80 px on the phone for them.
3. The camera cannot go outboard of the right winglet (the room's wall), so the rudder hinge, which is on that face, is seen through the winglet.
4. Two ops cannot be judged by the hide test and are tested another way: `f20.jig` (the exported jig rods are thin; the cyan lines carry it) and
   `f20.inside-layups` (layups 1 and 2 are not drawn, crew A's note; the test asserts nothing is placed).
5. The left winglet's outboard face and the left wingtip poke through the room's near wall in the airplane shots (the span is 313 in).
6. The left aileron and rudder stay neutral; only the right side swings (the book's deflection model is one side).
7. `f19.cut-cores` and `f19.core-cutouts` now draw the cores on the table (they were invisible there before); the cores' own cut-outs
   (torque-tube slot, light holes, hollowed FC1) are still the crew A open items.
