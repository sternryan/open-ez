# Block 2 milestone 2.4 (chapters 11-13): captain report

Spec `docs/superpowers/specs/2026-10-01-block2-m24-elevators-canard-install-nose-design.md`; evidence
`docs/harness/m24-ch11-13-research.md`; full log `docs/harness/block2-m24-captain.md`. Start 12bcc57.
Nothing is pushed, deployed or published. Every crew call and every gate run was in the foreground.

## What shipped per task

| # | Task | Commits | Gate at the last commit of the task |
|---|---|---|---|
| 1 | Source notes, config values, ledger reference rows | a823100 | linux 757 passed, 3 skipped, 9 xfailed; mac 160 + 5 |
| 2 | Graph: Roncz elevators (ch 11), ch 12 gaps, new ch13.yaml (20 ops) | 914a4b4 | linux 768 / mac 160 + 5 |
| 3 | Elevator kinematics kernel and fitted-shape geometry | eb614bf (config), c018ef5 | linux 797 / mac 160 + 5 |
| 4 | Nose structure and the retracting nose gear | 425688a (config), 4a86614 | linux 834 / mac 160 + 5 |
| 5 | The lab: chapters 11-13 | f2dbd77 | linux 838 / mac 180 + 5 |
| 6 | Tours and the canard12 film | 1e7af36 | linux 838 / mac 186 + 5 |

Every commit also passed local `-m local_render` (5 passed), lab unit and `tsc` (158/158 at the end),
viewer node tests (50/50) and `guide.check` (OK, RECALL 14/14). Note for the next captain: the
commit hook only credits a test run that is the last segment of the command; piping pytest to
`tail` or `head` earns no credit, so run it bare and commit in a separate call.

Per task:
1. Config fields with provenance for the ch13 block sizes, NG6/NG7/NG30 numbers, 25.5 strut, static
   port, NG31 as a derived range (0.1 to 1.1), the nose-wheel pair, Roncz elevator numbers, CP26
   prototype weights as reference data only. New status `positioned-from-text` for hinge BLs.
2. 17 elevator ops + 4 ch12 gap ops (ch30.yaml, chapters 11 and 12) and 20 ch13 ops. The stub
   `r30.elevators` is replaced by `r30.elev-cs11`. Four CP entries added and verified in the CP text.
3. `core/elevators_kin.py` (spans, hinge stations, travel classes, rotation, hang test) written on the
   local lane; `core/elevators_book.py` solids; glb components built.
4. `core/nose_gear_kin.py` (local lane), `core/nose_book.py`, nose gear in `core/landing_gear_book.py`,
   the ledger exposes both nose arms. Every nose and nose-gear part is representational.
5. Canard-subject elevators (travel readout 30 down then 15 up, hang test), the canard and elevators
   installed on the airplane for ch 12-13, nose parts per op, gear retracting over 6 s with a crank
   readout, both axle candidates labelled conflict, station cut to the nose tip, label cap of 10.
6. Chapter 11, 12, 13 tours and a 40 s `canard12` film (canard lowers 24 in onto F22).

## Evidence corrections against the research and the brief

- **`fs_nose` was never -45.5.** The tree already carried -6.8 as book (set in the datum retirement).
  Nothing to reconcile, no physics test moved, no `fs_nose_tip` added. Confidence lowered high to
  medium: on the 500 dpi crop the first digit reads closer to 6 than 4 but is not crisp.
- **Elevator placement (cobelu figure C-1, read by the captain, drawing rotated 90 degrees).** Both
  elevators end at |B.L.| 65.0. The right one runs +9.3 to +65.0 (55.7), the left one -65.0 to +7.7
  (72.7), so the left elevator crosses the centreline. 65.0 + 7.7 = 72.7 and 65.0 - 9.3 = 55.7 both
  check against the figure's labels. The research had left the placement open. This also explains the
  "57.0 near the outer CS-10": the weight's inboard face is at 65.0 - 7.5 = 57.5.
- **Hinge stations.** Text says seven slots; the stations 9.2 / 34.1 / 59.0 place five on the figure's
  elevator spans (left -59.0, -34.1, -9.2; right +34.1, +59.0). The right 9.2 lies 0.1 in outside the
  right elevator (inboard end 9.3) and is carried as unplaced, not moved. The research's "7.8 right"
  matched nothing on the figure; the review crew reworded it.
- **Page reads confirmed:** p81 25.5 (thin decimal, medium), p77 pads 2.8/1.2 (representational
  anyway), p79 floor and side block orientation, p82 static port 8 / 10 / W.L. 13 and the top block,
  p73 156 deg, 10.8 turns, five to seven seconds, p171 W.L. 0.9 at the fuselage bottom.
  Plan-view consistency check: floor block 1.6 + 8.2 = 9.8 = half of the top block's 19.6.
- **p83 door:** dimension lines are loose, so the door is a fitted shape with no book numbers.
- **Review crew fixes to op citations:** `f13.nb-box` is p81 only, `f13.shock-strut` also p73 (CP25 note),
  `f13.worm-drive-bench` also p75; canard-tips 1 in is a sand line, not where the foam goes.
- **Two scan-versus-CP facts to know:** NG17 wall 0.188 (CP30 LPC 87) is not on the scan (the scan has
  0.083 / 0.095); the cobelu figure says nine hinge places, its text seven.

## Review Focus (each pinned)

1. **Nose-wheel station stays a conflict.** `tests/test_nose_elevator_stations.py::test_nose_wheel_is_a_conflict_pair`
   and `::test_no_unprinted_gear_dimension_exists` (no rake, fork, trail, NG6-position field);
   `tests/test_nose_gear_book.py` (both candidates, axle at W.L. -22, strut 25.5);
   `tests/test_nose_gear_kin.py::test_candidates_are_the_conflict_pair`; lab e2e
   `test_both_nose_wheel_axle_candidates_show_with_the_word_conflict_and_the_station_is_never_a_bare_fact`.
   The NG6 pivot is solved from each candidate, 25.5 and zero fork offset; it is tagged representational.
2. **Representational shown as book.** Every nose, nose-gear and elevator part is representational
   (`tests/test_nose_book.py`, `tests/test_nose_gear_book.py`, `tests/test_elevators_book.py` tag and
   citation tests); lab e2e `test_ch11_elevators_appear_on_their_ops_are_fitted_shapes_...` and
   `test_nose_parts_appear_on_the_op_that_lists_them_...` check stripes and the "(fitted shape)" label.
3. **Hinge BLs never shown as verified.** `test_hinge_bls_are_flagged_positioned_from_text_low`;
   `tests/test_elevators_kin.py::test_hinge_count_note_says_the_text_and_the_figure_disagree` and
   `::test_hinge_stations_are_the_drawn_ones_that_fall_on_the_elevator`; the lab label reads
   "positioned from text, low confidence".
4. **GU or manual travel never on the Roncz row.** `test_elevator_travel_is_roncz_not_gu_or_manual`,
   `tests/test_elevators_kin.py::test_travel_range_is_roncz_not_gu_or_manual`, and the graph test on the
   travel-check text (no 20 or 22 degrees).
5. **No mass or CG invented.** `test_elevator_weight_is_a_check_bound_not_a_mass`,
   `test_prototype_weights_are_cited_reference_data`, `test_prototype_weights_are_not_in_any_sum`;
   gear ledger test for the nose arm pair; CG stays "not yet computed" in the readout; the hang test's CG
   offset is labelled "illustrative: masses not sourced".
6. **No regression.** Against 12bcc57, `tests/guide/test_lab_e2e.py` lost no assertion line: the only
   removed lines are the two helper chapter tuples (`_bar_ops`, `_fuse_ops`). One click line was added to
   `test_tour_follows_the_selected_ops_chapter` (the GU chapter 12 ops moved to the fuselage subject).
   The canard-only export is unchanged (`test_canard_only_export_has_no_elevator_nodes`, and the nose
   equivalent); canard-subject frames for chapter 30 are 0 px different at home and differ in other
   frames only by the step digit and chip scroll (crew's before/after set). `tests/guide/test_viewer_e2e.py`
   and `test_fuselage_graph.py` changed by op id only (`r30.elevators` is gone).
7. **Graph integrity.** `tests/guide/test_ch1113_graph.py` (counts, chapters 11/12/13, `r30.elev-cs11` in
   the needs of `r30.install-pins`, stub gone, `validate(g) == []`, no 20/22 degrees, 6.71, 0.2, 3.0,
   no nose-wheel station as fact); `guide.check` overlap gate OK.
8. **Hygiene.** No hostname, IP, home path or scan path in any tracked diff since 12bcc57 (grepped);
   the plan and ledger paths live outside the repo.

## Lane log

| Step | Lane | Detail |
|---|---|---|
| Op YAML drafts (T2) | smithy local-anvil | 7 calls, all attempt 1, no 503. Quality low: every draft needed hand fixes (truncation, wrong materials, junk rows, one unparseable). Used as a base only. |
| Elevator kernel (T3) | smithy-conduct, job 4bccf406, branch m24-kin | 1 task, local_pass first attempt. Captain fixed one defect (pin lengths hard-coded). |
| Nose-gear kernel (T4) | smithy-conduct, job dc839c40, branch m24-nosekin | Run 1 escalated after 4 attempts: my own test constant was wrong (8.8145 vs 8.81297); the worker's first attempt was right. Re-run: local_pass. Captain then added the clearance-based retracted angle. |
| T1, T2 integration, T3 solids, T4 solids, T6 | sonnet subagents | one wave each; reasons in the log. |
| T2 review | sonnet subagent | page-image review of ch13 and ch12 ops: 5 fixes. |
| T5 lab | sonnet subagent x2 | First pass ~97 min, fix pass ~34 min after the captain's screenshots (wrong authored shots, 13-15 labels, vacuous `or True` asserts, crank text). The brief said sonnet only; M2.3 used opus for this task. |
Rows are in the shared `lane-log.tsv`. No opus, no frontier call. Branches m24-kin and m24-nosekin hold
the conduct commits (the kernel files were copied into main and fixed there).

## Open owner items and known weak spots

- **Airfoil data vs the torque tube.** The repo's R1145MS ordinates give about 0.77 in maximum thickness
  at 13 in chord (about 6 percent); the elevator tube is 1.0 in OD, so in every render the tube sticks out
  of the elevator section. Either the airfoil file or the chord is off. Not touched here; worth a Block 1
  look before printed plugs.
- **Hinge count:** five placed against the text's seven; the unplaced right 9.2 stands.
- **Elevator placement** now follows C-1 (left crosses the centreline); the canard planform itself is
  still the GU-sized rectangle (existing conflict flag), so the 65.0 ends sit inside a 70.8 half span.
- **Fitted values, all flagged representational:** elevator chord fraction 0.70 and sleeve 0.03, hinge
  plate 2.0 x 1.5 x 0.125, CS-10/11 positions, NG31 at 0.6 (midpoint of the range), nose envelope (10.9 in
  half-width at F22, not 9.8: the 1.0 side block sits outboard of the 9.9 floor block), pitot height
  (W.L. 4.4, level), tire OD 9.0, retracted strut angle (about 97 deg, fitted so the tire clears the
  skin), zero fork offset. The static port station (F.S. 31.75) is aft of F22, on the fuselage side.
- **Weights:** the modelled finished F22 and F28 (core plus glass lower bound) are heavier than CP26's
  prototype numbers (F22 2.00 vs 1.44 lb, F28 0.40 vs 0.19). Not asserted; look when the ledger-closure
  test is written. CP23's 2.6 lb NG-1L stays a note.
- **Lab:** elevators are hidden on `r30.install-pins` and `r30.align-canard` to keep those canard frames
  pixel-identical. The canard subject draws the right half only (existing convention), so the left
  elevator shows only in the fuselage subject. The installed canard overlaps the side foam and the F28
  band by 0.5-0.9 in^3 per side. At the end of `f13.rig-nose-gear` the retracted wheel sits inside the NB
  box and is not visible. The crew reports a single-process run of `tests` without `tests/guide` fails
  about 75 tests from a cadquery MagicMock leak, same on a clean HEAD; the two-node script shards avoid
  it. I did not reproduce that run.
- **For deploy:** `canard12.mp4` (40.4 s) was rendered in the scratchpad only; re-render at deploy.
  AGENTS.md's known-issues line on the fuselage box still describes chapters 4-6 (and the M2.3 note);
  it should now say the model runs from the nose tip to the firewall, with the nose and gear fitted.
  `elevator_components()` and `nose_components()` are now in `default_components()`.
- **Owner-held evidence that would settle things:** the A6/A7 sheets (NG6 position, fork offset, strut
  rake, nose outline), or a nose-down weigh-in, for the nose-wheel station; the Roncz planform and
  elevator templates for the contours.
- **Spec section 5:** the Opus visual review, grading, push, deploy and public republish are the lead's.

## Fix round after the Opus visual review (FAIL, `docs/harness/block2-m24-visual-review.md`)

| Review item | Commit | What changed |
|---|---|---|
| 6 (F22/F28 above CP26 prototype weights) | fabd031 | Both are left out of the lower bound ("under review"); prototype numbers not substituted. Correction-ledger row 58; `test_lower_bound_cg_is_the_moment_sum_over_core_sourced_parts` gained `f22`, `f28` in its excluded set. |
| 1 (elevators inside the canard core) | ebf8510 | Canard materials discard what lies aft of the elevator LE less the 0.2 in slot gap (x_cut 8.914), over |B.L.| <= 65 only, wall capped and labelled "Cove cut for the elevators (fitted shape)". Shader clip, so no solid changes: the canard-only cutaway export is byte-identical (tested), chapter 30 frames are 0 px different. New e2e pixel tests failed on the old tree (elevator 6.5k px at 30 down vs 14k at 15 up; 1.9k px striped after hinge-slots; installed label collapsed) and pass now (86k vs 57k px; 70k; 85k). |
| 2, 3, 4, 5, 9 | d296412 | NG box on the bench from `f13.strut-reinforce` to `f13.ng3-ng4`, moved to F22 at `f13.ng31-f6`, shots re-aimed (also `f13.pitot-static`, `f13.shock-strut`); door shot and label (checks now require not collapsed and not hidden; failed first); phone `#t-kin` on its own line (failed first); wheel marks hidden once stowed, so no label says F.S. 17 at F.S. 34 (failed first); hang readout "about 94 deg"; hinge and tube labels shortened. |

Gate at d296412: linux 840 passed, 3 skipped, 9 xfailed; mac 204 + 5; local_render 5 passed; lab unit 162/162 and `tsc` clean;
`guide.check` OK. Existing e2e assertions edited (all in this round, listed by the crew): the placement expectation in
`test_nose_parts_appear...` now allows the bench; label-presence checks in two M2.4 tests use `_legible` (not collapsed, not
hidden); the hang readout string and the hinge/tube label strings are pinned to the new wording; `kin.test.ts` `hangText`.

Owner items added or changed:
- **Tube thicker than the section** (unsourced chord; the R1145MS file is about 6 percent thick): left as is, now labelled
  "(1 in OD book; section fitted, unresolved)" on the tube and in AGENTS.md known issues. Block 1 airfoil look item.
- **Weights inside the elevator skin:** the CS-10 and CS-11 lead blocks sit inside the elevator section, so they are labelled but
  not visible even with the cove open.
- **Nose door:** a flush 0.08 in panel, so from above only its outline and label read; making it stand out needs a geometry change.
- **Canard subject cove:** the canard subject draws the right half only, and the cove spans 0 to 65, so a 9.3 in root notch shows
  with no elevator in it (the left elevator would cross there).
- **F22/F28 excess** (2.00 vs 1.44 lb, 0.40 vs 0.19 lb): for the ledger-closure test (glass schedule or R250 density).
- The wheel hidden inside the NB box at the end of the rig op stays (correct end state); only the labels changed.
