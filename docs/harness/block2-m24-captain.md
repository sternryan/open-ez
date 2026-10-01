# Block 2 milestone 2.4 (chapters 11-13): captain log

Captain: Sonnet 5.5 (brief: Sonnet crews only, smithy local-anvil first for op YAML, /conduct for eligible
one-file modules). Start: main at 12bcc57. Spec
`docs/superpowers/specs/2026-10-01-block2-m24-elevators-canard-install-nose-design.md`, evidence
`docs/harness/m24-ch11-13-research.md`.

## Page reads (captain, on the page images, before anything enters the model)

Pages rendered at 200 dpi from the owner's scan into the scratchpad (p171 nose tip also at 500 dpi crop);
never committed. Pages read: p77, p79, p81, p82, p83, p171.

- **Evidence correction 1: `fs_nose` is already -6.8, book.** The brief and the research say `fs_nose` is
  -45.5 converted-unsourced. The tree (config line 121, provenance line 423) already carries -6.8 as
  `book` from p171, set in the datum retirement. So there is nothing to reconcile and no physics test
  moves on account of the nose tip. The spec's `fs_nose_tip` would duplicate it; not added.
- **p171 nose tip label.** Reads "F.S. -6.8" with the 500 dpi crop; the first digit's glyph is closer to
  a 6 than the 4 in "W.L. 66.4" on the same page but is not crisp. Confidence lowered from high to
  medium in provenance with that note. The value stays -6.8.
- **p171 nose wheel:** "F.S. 17" at the cross-hair; typeset W.L. label struck, hand "-22" written, owner
  note "Nosegear CL is at W.L. -22 not -23". Matches M2.3.
- **p81 (13-9):** strut length "25.5 IN", pivot to pivot, "see A6 & A7"; the decimal is thin but present.
  Medium confidence, kept as 25.5. Gear-down: lower pivot vertical or canted bottom-forward up to 5 deg.
- **p77 (13-5):** NG30 foam 0.2 thick; 3.0 in inside between the plates; pad lengths "2.8 inches" (section
  A-A) and "1.2 in" (section B-B); "15 ply pad", "4 ply skin". The 2.8 decimal is faint: kept medium-low,
  pad is representational anyway. NG30 outline is A6/A7: not on the page.
- **p79 (13-7):** floor block top view: 20.9 along the top edge, 1.6 at the left (shallow) end, 8.2 at the
  right end, 11 in dish span, 6.1 and 6 and 7.35 labels, 5 deg end bevels. Orientation as the research
  reads it. Side block: 21.9 long, 15.6 at F22 (left), 5.5 above and 2.8 below the NG31 end, 17 deg
  bevel, 0.5/1.0 dish. Pedal block X = 3 (2 to 4), 1.6 thick, 1 x 0.7 plate.
- **p82 (13-10):** static port left side, 8 forward of the panel, 10 below the top longerons "(W.L. 13)";
  pitot 6 and 38 in 1/4 tube, through F22 on the centreline about 3 in under the canard. Top block: top
  view, 19.3 long, 19.6 on the aft (taller) edge, 7.0 on the forward edge.
- **p83 (13-11):** door dimensions are drawn along the contour with loose dimension lines (6.5, 9.9, 8.9,
  2.0, 0.7; top piece 7.0 wide by 8.5 long). I cannot tell which edge each spans, so the door is a
  representational cut: size from the 8.9 overall and 9.9 along the contour only as a fitted shape, no
  value gets book provenance except the 0.7 flange and ten screws.

## Review Focus (each pinned by a test; test names are added to the report)

1. **Nose-wheel station stays a conflict.** `fs_nose_wheel` provenance is `conflict`; 17 and 20 travel as a
   pair (ledger row, readout row, gear point maths). No strut rake, NG6 position or fork offset is a number
   in config or geometry. Pin: provenance test, a test that fails if any new gear field carries book or
   derived status for the axle station, e2e on the readout row.
2. **Representational shown as book.** Every new solid has a fidelity tag with a valid citation; the
   elevator section, NG30 outline, NG6 hole, NG31, F6, strut, fork, nose outline and the door are
   representational; the lab stripes them. Pin: tag-completeness test, lab e2e.
3. **Elevator hinge BLs shown as verified.** They are `positioned-from-text` with a low flag and the
   59-vs-57 note. Pin: provenance test, label e2e.
4. **GU or manual travel leaking into the Roncz row.** Travel is 15 up (12.5 floor) and 30 down from cobelu;
   20/22 deg never appear on the Roncz elevator. Pin: config + graph tests.
5. **A mass or CG invented.** Only NG-1L 2.8, F22 1.44, F28 0.19, panel 2.13 (prototype note) are new
   sourced rows; the elevator 3.9/3.6 lb is a check bound, not a mass; CG stays "not yet computed".
   Pin: ledger tests, readout e2e.
6. **No regression.** Canard chapters and ch4-9 e2e assertions unchanged; the canard-only cutaway export
   still writes `output/guide/canard/` and is not changed by the canard joining the fuselage. Pin: diff
   of test_lab_e2e.py vs 12bcc57 loses no assertion; export test.
7. **Graph integrity.** The stub `r30.elevators` is replaced or aliased; every new op has requires that
   resolve; the overlap gate and own-words rule pass. Pin: ch11-13 graph test.
8. **Public hygiene.** No hostnames, IPs, home or scan paths, plans quotes. Pin: leakcheck run + existing
   hygiene tests.

## Lane log (call, lane, reason)

