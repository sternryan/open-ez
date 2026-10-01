VERDICT: FAIL (bounded: one geometry/lab fix plus shot and CSS fixes, then re-review of the affected frames only)

# Block 2 M2.4 visual review (chapters 11-13), Opus reviewer

Reviewed: main at c6a0ce1 (milestone 12bcc57..c6a0ce1). Site built fresh into the reviewer's scratchpad
(`guide.export_glb` + `guide.build_site`, as `tests/guide/test_lab_e2e.py::rsite` does), served on 127.0.0.1,
driven through `window.__lab` with `?test=1&freeze=1` and `advance()`, as the e2e tests do. Captured every non-stub
chapter 11, 12 and 13 op in Playwright WebKit at 1180x820, key frames at 390x844 (WebKit) and 1180x820 (Chromium,
`q=low`), the `canard12` film through `window.__rec` in WebKit, and probe cameras where the authored shot hid
something. No page errors on either engine. Screenshots live in the reviewer's scratchpad only, under
`.../scratchpad/m24rev/shots/` (file names below; prefix `webkit-1180-` unless stated).

Rubric: spec section 3 ("What the owner sees") and section 5 ("Done when"). Trust bar: nothing representational reads
as book, nothing invented. Visual bar: the earlier milestones' lab.

## What passes

- The nose-wheel conflict is visible and never a bare fact. The CG detail row reads "Nose wheel arm: F.S. 17 (plans) /
  about 20 (manual): conflict"; the motion row's note says "Axle station is a conflict: F.S. 17 (plans, drawn) or about
  20 (manual, ghost)" on every op from `f13.lower-gear` on; CG stays "not yet computed"; the ground note carries "nose
  wheel W.L. -22 (CP25 LPC 24)" and both tip checks "not yet computed" (`readout-expanded-nose-door.png`).
- Striping and "(fitted shape)" labels are on every nose and nose-gear part (NG30 plates, NG31/F6, floor, side and top
  blocks, pedal blocks, pedals, SC cover, NB box, strut, wheel marks, door, pitot) and on every elevator part in the
  canard subject, including the hinges' "positioned from text, low confidence".
- The travel readout uses the Roncz numbers only: "Down 30.0 deg (limit 30)" then "Up 15.0 deg (target 15, floor
  12.5)"; no 20 or 22 anywhere.
- Bond cores and skins read well: tube and cores held aft on the NC-7 jigs, striped (`r30.elev-bond-cores.png`,
  `r30.elev-skin-top.png`). The hang test shows the elevator hanging on its hinge line, labelled illustrative
  (`hang-settled.png`).
- The gear lowers and retracts on sim time with the crank readout (`f13.lower-gear.png`, `rig-mid.png`, `rig-end.png`).
- The `canard12` film descends cleanly from 24 in up onto F22 and holds (`film-canard12-*.png`).
- No regressions: `r30.top-skin`, `f06.trial-fit` and `f07.canard-cutout` render as before (`regress-*.png`, `misc-sheet.png`).
  Chromium matches WebKit (`chromium-sheet.png`).

## Findings

1. **Ship-blocking. The elevators sit inside the canard's own volume, so most of chapter 11 and the chapter 12
   clearance op show nothing.**
   Ops: `r30.elev-hinges`, `r30.elev-hinge-slots`, `r30.elev-uptravel-test`, `r30.elev-flox-hinges`, `r30.elev-nc12a`,
   `r30.elev-travel-check`, `r30.elev-mass-balance`, `r30.elev-balance-pockets`, `r30.elev-cs11`,
   `r30.elev-fuselage-clearance` (and every installed view in chapters 12 and 13).
   Evidence, in model inches (`__lab.plyBox`): `canard.core` x 0.07 to 12.97, y -0.06 to 0.77; `elevator.right` x 9.08 to
   12.62, y -0.03 to 0.49. The elevator, tube, hinges and CS-10/CS-11 weights are inside the canard's full-chord core and
   skins. Once the elevator comes home (`mode none`, `slide 0`), it cannot be seen. The travel readout counts 30 down and
   15 up while the frame does not change: only a sliver of stripe shows under the trailing edge at 30 deg down, and only
   from a low aft probe camera. The authored frames show a canard with labels pointing at parts you cannot see.
   Shots: `r30.elev-hinge-slots.png`, `r30.elev-hinges.png`, `uptravel-up.png`, `travel-down.png`,
   `r30.elev-mass-balance.png`, `r30.elev-balance-pockets.png`, `probe-down-aft-oblique.png`,
   `probe-travel30-from-aft-low.png`, `r30.elev-fuselage-clearance.png`.
   This fails spec section 3 ("hinges slotted into the canard's trailing edge at a 0.2 gap, the up-travel check with an
   angle readout, the lead weights and their pockets", "the elevators clear the fuselage sides") and the section 5
   "elevator travel check" item. The e2e tests pass because they check transforms and states, not what is visible.
   Fix: once the elevators are shown on the canard (from `r30.elev-hinges` on, and in the installed group), stop drawing
   the canard's core and skins aft of the elevator leading edge minus the book 0.2 in slot gap. A clip plane on the
   `canard.*` materials, or an exported canard-with-cove variant, would do it. Either way the cove is a fitted shape: it
   follows the fitted 0.70 chord fraction, so stripe or note it. The chapter 30 frames are untouched, because the
   elevators are hidden there. Then re-shoot the travel, hinge-slot and pocket ops with a spanwise or aft camera that
   shows the deflection. Add an e2e assertion that the elevator's screen box changes pixels between 30 down and 15 up.

2. **Fix before push. Chapter 13 bench ops show an empty floor, and the "box built on the bench" never happens.**
   Ops: `f13.strut-reinforce` and `f13.worm-drive-bench` frame the floor and the nose stand, with the airplane cropped
   behind the top-right control card (`f13.strut-reinforce.png`, `f13.worm-drive-bench.png`). `f13.ng30-plates`,
   `f13.ng-box-assemble` and `f13.ng31-f6` show the NG30 plates already mounted on F22, again with the box partly under
   the control card (`f13.ng30-plates.png`, `f13.ng-box-assemble.png`). Spec section 3 says "the nose-gear box built on
   the bench and mounted to F22".
   Fix: re-author those fuse shots to frame the nose zone left of the control card. Give the NG box `placement: table`
   (on the bench) for `f13.ng30-plates` to `f13.ng3-ng4`, then `jig` from `f13.ng31-f6`. Show the NG-1L strut on the bench
   for `f13.strut-reinforce`. If the bench stage is not built, say in the step card that the box is shown in place.

3. **Fix before push. The `f13.nose-door` frame does not show the door.**
   The door is a thin outline on top of the nose, visible only from above (`probe-door-close.png`). The authored side
   view hides it, and its label is collapsed to a dot at the top (`f13.nose-door.png`; `labelsAll` reports
   `nose.door collapsed: true`). The e2e still passes because it counts a collapsed label (opacity 1) as shown.
   Fix: author the door shot from above and forward of the nose. Make the e2e require `collapsed` false and `hidden`
   false for the op's own part.

4. **Fix before push. The phone readout overlaps (new in M2.4).**
   At 390 wide, the new `#t-kin` tile (class `layers`) joins the one-line readout row. Its value prints over "Turn on the
   section…" and is truncated: "Hangs nose down 93.8 deg (illustrative CG:" and "Crank 0.0 of 10.8 turns (gear"
   (`webkit-390-hang.png`, `webkit-390-lower-gear.png`, `phone-sheet.png`).
   Fix: in `@media (max-width: 640px)`, give `#t-kin` `flex-basis: 100%`, its own line and a top border, and clamp or hide
   `#ro-kin-sub`. iPad is fine.

5. **Fix before push (cheap). The nose-wheel marks keep saying "F.S. 17" after the wheel is stowed.**
   At the end of `f13.rig-nose-gear` and on every later op, the marks "Nose wheel, plans candidate F.S. 17: conflict" and
   the ghost's label anchor on the stowed wheels at about F.S. 34 and 37, inside the NB box (`rig-end.png`,
   `top-nose-ch13.png`, `f13.carve-glass-nose.png`). A label at F.S. 34 that reads "F.S. 17" is what a sceptical owner
   will catch.
   Fix: while `noseGear().t == 1`, hide both wheel marks (the motion and CG rows keep the conflict), or reword them to
   "axle F.S. 17 / about 20 when down: conflict". Mid-rig (3.5 s) the manual ghost's label is `hidden: true`, yet the e2e
   counts it as on via opacity. Tighten that test too.

6. **Captain item 3: the retracted wheel is hidden in the NB box. Ruling: ignore (correct), with finding 5 applied.**
   A stowed nose wheel inside the NB box is the real end state, and the retraction itself is visible on sim time. Only the
   stale labels on the hidden wheel are a problem (finding 5). Optional: ghost the NB box for the last second of the rig
   op so the stowed wheel reads.

7. **Captain item 1: the R1145MS section (about 0.77 in thick) is thinner than the 1 in tube. Ruling: owner-visible note
   now; Block 1 fix later, not here.**
   `data/airfoils/roncz_r1145ms.dat` gives t/c of about 0.064 (y -0.005 to 0.059), and the canard chord is the GU
   rectangle, which is already flagged conflict. So the section scale has no source, and nothing in M2.4 should be
   adjusted to hide it. Once finding 1 opens the cove, the tube poking out of the striped elevator becomes more visible.
   That is honest, because the stripes already say "fitted shape". Add one line to the elevator label or legend, and to
   AGENTS.md known issues: "tube is 1 in (book); the section is fitted to an airfoil file that is thinner than the tube:
   unresolved". Fold the file's provenance and t/c check into the Block 1 airfoil look before any printed plug.

8. **Captain item 2: the modelled F22/F28 exceed CP26's prototype weights. Ruling: fix before push (cheap). This is on
   screen, not just a ledger note.**
   The captain's report calls these weights "not asserted". But `ledger.json` `cg_lower_bound.included` contains `f22`
   (lower bound 2.00 lb) and `f28` (0.40 lb). Those values feed the readout's "≥ 58.0 lb … lower bound", while CP26
   records 1.44 and 0.19 lb for the prototype parts. A "≥" figure that contains terms a cited source contradicts is not a
   lower bound.
   Fix: exclude `f22` and `f28` from the bound, with an excluded reason such as "modelled above the CP26 prototype weight:
   under review". The bound drops by about 2.4 lb and stays true. Investigate the excess (glass area, or the R250 core
   density) at the 2.n ledger-closure test. Do not substitute the prototype numbers.

9. **Low. Readout and label wording.**
   - `r30.elev-balance-check`: on iPad the value is clipped ("…masses not sourced" loses its closing parenthesis;
     `hang-settled.png`), and "93.8 deg" claims precision for a CG that is labelled illustrative. Show "Hangs nose down"
     plus "about 94 deg", and leave "illustrative" to the sub-line, which already says it.
   - The hinge label "…(positioned from text, low confidence) (fitted shape)" has two parentheticals and runs off both
     edges at 390 wide. Shorten it to "Elevator hinges (from text, low confidence; fitted shape)".
   - Once finding 1 is fixed, the installed elevators on chapter 12 ops need a "(fitted shape)" label. Today only the
     striped tube is visible, and it has no label (`r30.f22-drill-tabs.png`).

10. **Ignore for this push (pre-existing M2.2 wording).** The CG detail reads "16 of 16 parts have no sourced mass" next
    to "lower bound, 9 parts". This wording comes from `logic/fuselage.ts`, commit 4f986d7, not from M2.4. Reword it at
    the next readout touch.

## Re-review scope after fixes

Re-shoot and re-review only these frames: chapter 11 from `r30.elev-hinges` to `r30.elev-cs11`, plus
`r30.elev-fuselage-clearance`, `f13.strut-reinforce` to `f13.ng31-f6`, `f13.rig-nose-gear` (end), `f13.nose-door`, and the
390-wide readout. Do this in WebKit at 1180x820 and 390x844. Nothing else in the milestone needs another look.

---

# Re-review (fix round: fabd031, ebf8510, d296412, bfa261c)

VERDICT: PASS WITH FIXES (one cheap trust fix, R1, before push; the rest are notes)

Method: the same as round 1, with fresh evidence and none of the captain's shots used. I rebuilt the site at bfa261c into the
scratchpad and drove it through `window.__lab` in WebKit at 1180x820 and 390x844. Screenshots are under
`.../scratchpad/m24rev/shots2/`. To check for regressions I built c6a0ce1 in a scratch worktree (since removed) and
compared fresh-page captures pixel by pixel, the same op on both trees. No page errors on either tree.

## The six fixes, checked

1. **Elevators visible: pass.** From `r30.elev-hinge-slots` on, the elevator sits in its cove behind the canard and is
   labelled "Cove cut for the elevators (fitted shape)" (`webkit-1180-hinge-slots.png`, `-hinges.png`, `-pockets.png`,
   `-cs11.png`). At exactly 30 down and 15 up, the trailing edge visibly drops and rises, matching the readout ("Down 30.0
   deg (limit 30)" / "Up 15.0 deg (target 15, floor 12.5)"; `travel-pair.png`). The chapter 12 installed views now show
   the elevators and the striped tube with a legible "Elevators (fitted shape)" label (`-drill-tabs.png`,
   `-clearance.png`). The tube label reads "1 in OD book; section fitted, unresolved", which is my item 7 handled honestly.
2. **Bench and box: pass.** `f13.strut-reinforce` and `f13.worm-drive-bench` show the NG-1L strut on the bench. NG30 and
   the castings build up on the bench through `f13.ng3-ng4`, then the box sits on F22 at `f13.ng31-f6` (`C.png`, `D.png`).
3. **Nose door: pass.** The shot is from above and the "Nose door (fitted shape)" label is legible (not collapsed, not
   hidden). The panel itself reads only as an outline, because it is a flush 0.08 in panel (`-door.png`).
4. **Phone readout: pass.** At 390 the motion row has its own line, with no overlap or truncation (`G.png`).
5. **Stowed-wheel labels: pass.** After retraction both wheel marks have opacity 0, so nothing reads "F.S. 17" at
   F.S. 34 (`-rig-end.png`). Mid-rig, both conflict marks are legible (`-rig-mid.png`), and the readout keeps the conflict
   row throughout.
6. **Lower bound: pass.** `cg_lower_bound.included` no longer contains `f22` or `f28`. Both are excluded with "modelled …
   above the CP26 prototype weight …: under review". The readout reads "≥ 55.6 lb at FS 82.3, lower bound, 7 parts …";
   prototype numbers were not substituted.

**Regression spot-check: pass, 0 px different.** I compared fresh-page captures at c6a0ce1 and bfa261c of
`r30.top-skin`, `r30.align-canard`, `r30.install-pins`, `f07.canard-cutout`, `f06.trial-fit` and `f09.brake-lines`.
Every one diffs to `None` (`cmp-old-*.png` against `cmp-new-*.png`).

## New finding, made visible by the cove

**R1. Fix before push (cheap). The installed elevators run through the fuselage, on the op that checks they clear it.**
The placement comes from the captain's reading of cobelu C-1: right elevator B.L. +9.3 to +65, left -65 to +7.7. But the
fuselage's inner width at F22 is 23 in (`cockpit_width`, book), so its sides stand at about B.L. ±11.5 to ±12. Both
elevators therefore pass inside the fuselage sides, and the left one crosses the cockpit. The top view of
`r30.elev-fuselage-clearance` shows the striped elevator band continuous across the box between the sides
(`webkit-1180-installed-top-centreline.png`). The op's own text is "elevator-to-fuselage clearance 1/16 in", which this
geometry contradicts. Nothing here is invented: it is a figure-datum reading that a book clearance contradicts. That
makes it a conflict, and the lab currently draws it as settled.

Fix:
- Flag the elevator span placement (inboard ends 9.3 / 7.7) as `conflict` in provenance, citing both C-1 and the 1/16 in
  side clearance.
- Extend the installed label: "Elevators (fitted shape; span vs fuselage sides unresolved)".
- Add an owner item to re-read C-1's datum.

Do not move the elevators to make the picture tidy.

## Rulings on the captain's new owner items

- **The 9.3 in root notch with no elevator in it (canard subject, right half only): owner-visible note; optional cheap
  fix.** The notch is the inboard end of the same span question as R1. Once R1 flags the span, the empty notch says the
  same thing and needs nothing more. If it is cheap, limit the canard-subject clip to the right elevator's own span
  (9.3 to 65) so the canard frames show no empty slot. Not blocking.
- **CS-10/CS-11 lead hidden inside the elevator skin: ignore (correct).** Lead set into the foam under the skin is the
  real state, and the labels mark where it is. If wanted, the skin could be ghosted on `r30.elev-balance-pockets` and
  `r30.elev-cs11` only.

## Small notes (no action needed to push)

- At 390 wide, the `f13.worm-drive-bench` frame shows the strut small at the top while "Instrument panel" and "Bottom
  foam" labels take the foreground (`webkit-390-worm-drive.png`). iPad is fine.
- The CG sub-line hides the new "under review" reasons behind "4 more". That is acceptable, because the ledger carries
  them.
