# M2.9 crew B report: the lab for chapters 24 to 26

Worktree `m29`. Task 4 is DONE and VERIFIED, NOT COMMITTED (crew B cannot commit; the split is below).

## Commit split (named files, no trailers)
1. `feat(export): the m29 closure target carries both OM sample loadings; the kernels fixture covers m29`:
   `guide/fuselage_export.py`, `tests/guide/test_lab_kernels_fixture.py`, `guide/lab/tests/fixtures/kernels.json`
2. `feat(lab): chapters 24 to 26 (covers, consoles, gap seal, finish layer, upholstery) in the lab`:
   `guide/lab/src/logic/finish.ts`, `guide/lab/src/logic/m25.ts`, `guide/lab/src/logic/fuselage.ts`, `guide/lab/src/logic/graph.ts`,
   `guide/lab/src/core/materials.ts`, `guide/lab/src/fuselageBay.ts`, `guide/lab/src/fuseShots.ts`, `guide/lab/src/director.ts`, `guide/lab/src/main.ts`,
   `guide/lab/tests/m29.test.ts`, `guide/lab/tests/fuselage.test.ts`
3. `test(lab): m29 end-to-end tests and the chapter lists moved to 24 to 26`: `tests/guide/test_lab_e2e.py`
4. `docs: M2.9 crew B report`: `docs/harness/block2-m29-crewB-report.md`

## What is built
- `finish.ts` (pure): part placement (`m29Where`: in place from the op its row names), the finish stage by op (`finishStageAt`: bare, then fill from the coarse fill,
  primer, paint; it stays painted on chapter 26), colours (filler tint, primer grey, white on the upper wing and canard only), the readouts and the reference rows.
  Readouts are text: aft-cover plies (scan 1/1, transcription 1/2), LC2 30.6 vs 30.8, gap seal "1/2 in ... 1/16 in at the front", shop at 70 F and weave 0.009,
  feather fill 0.02 to 0.03, primer 0.004 to 0.008, "No finish weight printed" on the paint op, "No upholstery weight printed". References: the N26MS finish deltas
  (canopy 1, aileron 0.275, wing 2.2 lb) on the fill and paint ops; on the LAST op the closure target (730 lb at FS 111.7) with both OM samples (light 1113 @ 103.96,
  outside the 103 aft limit as the manual says; heavy 1323 @ 101.06, inside). CG stays "not yet computed". `m29Kin` and `m29Row` answer only `f24`, `f25`, `f26` ops.
- The finish is a shader layer, not geometry: `uFin` (colour plus cover) added to every `surf()` material in `core/materials.ts` (colour and roughness, off by default,
  never on a cut face); `fuselageBay.applyFinish` sets it per mesh from the `m29` finish rows, and `applyInstalledFinish` does the installed canard's skins.
- Lab wiring: `FUSE_PREFIXES` gets `cover.` and `upholstery.`; chapters 24 to 26 join `FUSE_CHAPTERS`, `M25_CHAPTERS`, the bar exclusion, the section-cut range, the tour set and
  the chapter cards; the installed canard shows on 24 to 26. Shots for all 13 ops (`M29_VIEWS`), tours for the three chapters (no plies played, close on the last op).
- Python addition (small, additive): `m29_section()["weights"]["closure_target"]["sample_loadings"]` carries the OM sample numbers from the ledger so the lab states
  them from data, never typed. Kernels fixture regenerated (only additions: `extras.m29`).

## Choices to know about
- The finish rows name `fuselage.skin_right/left`, which have no glb geometry (the glb carries `fuselage.side_*` and `fuselage.bottom`): the lab applies those rows to the
  sides through `FINISH_ALIAS`. The fill stage's data `from` is `f25.feather-fill`; the lab starts the filler tint at `f25.coarse-fill` (its first filler op) so the coarse fill
  changes the picture. The thickness text stays on the feather-fill op where the data puts it.
- Cockpit ops (LC1, consoles, thigh support, cushions, suitcases) leave the canopy out of the frame (it opens in life). The gap-seal op draws the airplane faint and the seal
  through it (it sits between the baffle and the wing skin). The rig clamps the eye inside the workshop, so the finish ops cannot frame the whole 26 ft airplane; they frame
  canard, cockpit and wing from the room side (canard and wing both show white at the paint op).
- Colours of covers, cushions and suitcases are representational (blue-grey covers, blue upholstery, tan cases, orange seal); everything but LC1 is striped and labelled "(fitted shape)".

## Tests
- Node `npm --prefix guide/lab test`: 252 pass (was 236; +16 in `m29.test.ts`); viewer tests 50 pass; `tsc --noEmit` clean. Includes: f13, f19 and f21 ops return null for
  `m29Kin` and `m29Row` (the M2.8 round 3 trap), and the finish stage / white-only-on-upper-wing tags.
- Python non-e2e (`-m "not local_render" --ignore=tests/guide/test_lab_e2e.py`): 1356 passed, 2 skipped plus 1 `test_fuselage_graph.py:94` skip ("source env not set": I ran
  without the private corpus env; crew A's 1357 had it), 9 xfailed.
- E2E on the Mac test node, FULL file (334 tests, chromium and webkit, in four 84-test chunks by node id plus a redo): the first pass had 11 failures, all from lists that stop at
  chapter 23 (see moved assertions) or load (below); after the fixes the 22 affected tests were re-run on the node: 22 passed. Every other test passed first time.
  New m29 e2e tests (11 tests, 24 runs): build order and bar, placement per op and the cockpit canopy, fitted-shape striping, per-op subject pixels plus context pixels, the
  finish by stage (mesh stages, frame diffs between coats), phone width x3, the gap seal through the faint airplane, readouts and the other chapters' readouts unchanged, references, the
  station-cut range, the three tours. The finish test was shown to fail with `finishStageAt` broken (returns null): FAILED as it must; restored.
- `test_play_lays_every_ply_then_cures_and_stops_and_time_only_moves_with_advance[webkit]` failed once under chunk load and passed on its re-run (timing, not related).
- Leak scan on the diff and new files: clean. `ruff check` on touched Python: only pre-existing findings (installed ruff 0.16 vs the pinned 0.5.4; `test_lab_e2e.py` was
  already not format-clean under 0.16, so I did not reformat it).

## Moved assertions (all chapter-list updates, no tolerance widened)
- `guide/lab/tests/fuselage.test.ts`: `FUSE_CHAPTERS` now ends at 26.
- `tests/guide/test_lab_e2e.py`: `_bar_ops` exclusion list and `_fuse_ops` default chapters extended to 24 to 26; `test_m28_the_chapters_follow_chapter_20...`: the chapter set after
  `f21.cut-parts` is now {21 to 26} (it was {21, 22, 23}).

## Screenshots (not committed)
the captain session scratchpad (not committed): `<op-id>.png` for all 13 ops (WebKit 1180x820) and `<op-id>-phone.png` for
`f24.consoles-left`, `f25.paint-seals`, `f26.suitcases` (390x844). A built site to look at live is in `.../scratchpad/m29-build/site` (serve it; `?test=1&freeze=1` for the hooks).

## Open nits
- The aft cover is a flat slab under the tail: it reads small (a blue strip in front of the strut) even from the best low view the floor clamp allows.
- The finish ops cannot show the whole airplane (room size); the card covers the bottom-left of the frame on the finish shots (the canard's tip sits behind it).
- The coarse-fill op has no readout of its own (the depth bands are not in the m29 data); it carries the finish deltas row.
- Front cushion path (about 39 vs 46 in printed) and the other fitted dimensions are crew A's open items, unchanged.
