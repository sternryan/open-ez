# M2.8 crew B report (the lab for chapters 21 to 23)

Worktree `m28`, branch `m28`, nothing pushed. Chapters 21 to 23 (23 ops) rehearse in the lab on WebKit and Chromium: the right strake's pieces on the layup
table, both strakes on the airplane, the shaded tank, the nose battery and the relays through a faint airplane, the striped engine block, the cowl and the root ribs.

## Commits

| commit | what |
|---|---|
| ef0007a | `guide/lab/src/logic/strake.ts` (where each part is per op, readouts, reference rows), the scene (kit on the table, jig table, faint-airplane x-ray, tank and opening looks), shots, tours, `m28.test.ts`, kernels fixture now carries `extras.m28` |
| next two | shot and x-ray tuning found by the pixel tests; the m28 e2e section and this report |

## What the owner sees (per op)

- **21.1 cut parts:** the right strake's kit lies on the layup table, the airplane is not drawn; the top skin core is lifted 12 in so the ribs and baffles under it read (an exploded layout, said here, not on screen).
- **21.2 cutouts:** the two openings per side as translucent red "material removed", the rest faint. **21.3 to 21.5:** both strakes stand in place on the airplane over a striped jig table ("Strake jig table (fitted shape)"), from the bond until the tank is closed.
- **21.6 and 21.10 tank ops:** the tank is a blue see-through volume, skins and airplane faint. **21.7 and 21.8:** the outboard diagonal and the sump blister read through faint skins. Plies are text, not drawn.
- **22:** panel wire bundle, battery shelf and battery, relays and cables, the right wingtip light, the canard's nav foil (the installed canard shows on that op) and the winglet comm foil, all through a faint airplane where they are buried.
- **23:** the striped engine block ("Engine block (installation in Section II, not held) (fitted shape)"), the bracket under it (block faint), the glass cowl, the thin root ribs (rest faint).
- Station cut range on these chapters runs FS -6.8 to 160 (nose battery to engine block).

## Readout text (exact, from python's `m28_section`; tests compare strings)

- Fuel: "Tank capacity: plans 2 x 25.5 gal, manual 2 x 28 gal (52 in all); model 26 a side"; sub: unresolved, envelope 24.6 gal a side (fitted shape, not measured), 6.0 lb per gal at FS 104.5. On 21.1, 21.6, 21.10, 21.11, 21.12.
- Battery "FS 0 to 22, not printed (A6 only)" (sub: drawn at FS 11 for illustration only); starter "station 150 or aft ... not drawn" (sub: a bound, not a station); engine 246 / 286 lb limits and oil, sub "Fitted shape; installation in Section II, not held".
- Cutout depth 1.9 vs 1.4, baggage arm FS 90 vs 80.6, layup 7 printed twice; ply schedules collapsed by cloth from each op's own materials ("5 plies: 3 BID + 2 UND").
- Reference rows, never in the CG: N26MS ladder 693.4 to 883.0 from the battery op; mount 5.19 on the engine op; cowl 18.0 glass / 12.0 graphite; at the last op "Closure target: OM sample empty airplane 730 lb at FS 111.7, reference, not in CG" with the ladder, sub says FS 97 to 103 is the loaded envelope, not the empty CG, CG not yet computed.

## Tests

| lane | result |
|---|---|
| node, `npm --prefix guide/lab test` | 236 pass (222 + 14 new in `m28.test.ts`); `tsc --noEmit` clean |
| viewer node tests | 50 pass |
| python non-e2e (serial, unpiped, `-m "not local_render"`, e2e ignored) | 1297 passed, 3 skipped, 9 xfailed |
| e2e m28 on the Mac test node (both engines) | 24 passed (12 tests x chromium and webkit): order, placement, striping and labels, per-op pixels, phone width x4, tank and jig table, conflict text, reference rows, station cut range, tours x3 |
| e2e `m27 or order` on the node | 51 passed, 1 failed: `test_recorder_url_exposes_rec_and_both_films_start[chromium-fuselage6]` timed out in `goto` under 16-worker load; the same test passed alone (4 passed with its siblings) |
| e2e `fuselage or station_cut or part_labels or home_view or chapter_12_and_13 or canard_bar` | 34 passed |
| e2e `m25 or m26` | 52 passed |

The full two-node fan-out is the captain's. Not run by me: the remaining e2e tests (canard chapters, viewer e2e).
Pixel gates (1180x820): each op's own parts and what it adds differ from the frame without them by 316 (vent screen, the weakest) to 356,000 pixels; every op is at least 100.
Kernels fixture: `tests/guide/test_lab_kernels_fixture.py` now dumps `fe.m28_section()` under `extras.m28`; regenerated with the documented command; there are no new numeric kernels (nothing in chapters 21 to 23 is computed in both languages).
Ruff (pinned v0.5.4 via pre-commit) and ruff-format clean on the touched Python. Leak scan on `git diff main` (no private-network addresses, hostnames or home paths): empty.

## Moved assertions

- `guide/lab/tests/fuselage.test.ts`: `FUSE_CHAPTERS` now lists 21, 22, 23.
- `tests/guide/test_lab_e2e.py`: `_bar_ops` excludes 21 to 23 from the canard bar and `_fuse_ops` defaults to 4 to 23 (as asked); the pinned ruff-format also rewrapped five M2.7 lines (formatting only).

## Things the captain should know

1. The left wing tip stands beyond the shop's wall (wing tip at 4.29 m, wall at 4.2 m: M2.7's room, unchanged), so the left position light is behind the wall; the wing-wiring shot looks at the right tip.
2. Faint-airplane x-ray: `setPlyLook` resets `transparent` every frame, so an x-rayed part sat in the opaque pass and the dozens of faint plies drew over it. For chapter 21 to 23 parts the x-ray now joins the transparent pass after `setPlyLook` (renderOrder 5, no depth write). The M2.5 and M2.7 x-ray parts keep the old behaviour; the same veil could hide thin ones there.
3. Phone width: the portrait pull-back is clamped by the room, so large strake shots show part of the subject, partly behind the readout card; the pixel gates pass (at least 150 px) but a human should look at `-phone` shots.
4. Ops with no part of their own (`f21.plumbing`, `f22.microswitches`, the layup ops) use a whole-airplane or default frame. The left strake appears with the right (the graph has no per-side op).
5. The engine block label is crew A's export text, "(installation in Section II, not held) (fitted shape)"; the spec's order is "(fitted shape; installation ...)". Left as is.
6. The commit hook credits a green run to the session's cwd repo and ignores a `cd` prefix; commits used `git -C <worktree>` after a green unpiped run. No hook was edited.
7. Screenshots for review (not committed): WebKit 1180x820 of every f21, f22, f23 op and 390x844 of four (`f21.cut-parts`, `f21.close-tank`, `f22.battery-shelf`, `f23.engine-install`) in the scratchpad `m28-shots/`.

## Round 2 (visual review round 1: four fails)

- `f21.vent-screen`: the vent line is now yellow and the screen cyan (fitted-shape colours) so the 1 in parts read as marked dots, and the camera is closer (about 56 in, 40 deg) between them.
- `f22.wing-wiring`: the right wing from above at about 250 in, the tip light at the end of the run (the room ceiling holds the eye at about 24 deg of elevation). No conduit is drawn by chapter 22 (the conduit is chapter 19's wing part), so only the lights are the op's own.
- `f22.antennas`: framed at 150 in from the left front, the canard (installed on this op) and the nose in view with the nav strips on it.
- `f23.root-rib`: seen from aft and left, level with the root (the rig will not take the eye lower), the two ribs read as white plates against the wing and the cowl.
- Pinned by `test_m28_round2_vent_screen_wing_wiring_antennas_and_root_rib_read_in_context`: subject pixels (400, 100, 600, 3000), context pixels (the strake 500, the wing 3000, the installed canard 3000, the wing 3000), camera distance under 2 m on the vent shot, from above on the wing shot, level or below on the rib shot.
- Results: node 236 pass, Python non-e2e 1297 passed / 3 skipped / 9 xfailed, Mac e2e `-k "m28 or order"` 50 passed, 2 chromium `goto` timeouts under load (`test_recorder_url_exposes_rec_and_both_films_start[chromium-fuselage6]`, a chapter 14 to 17 placement test) that passed on a solo re-run (6 passed).
- Re-shot the four ops (WebKit 1180x820) over the old files in `m28-shots/`.
