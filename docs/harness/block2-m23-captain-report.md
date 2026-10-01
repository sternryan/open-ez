# Block 2 milestone 2.3 (chapters 7–9): captain report

Spec `docs/superpowers/specs/2026-10-01-block2-m23-exterior-rollover-gear-design.md`; evidence
`docs/harness/m23-ch7-9-research.md`; full log `docs/harness/block2-m23-captain.md`. Start ec7ca75.
Nothing is pushed or deployed.

**Method.** Sonnet crew by default; opus for the lab (Task 5 and its fix pass: cross-stack with a
visual bar). Every crew call and every gate run in the foreground. Every value that entered config or
geometry was read by the captain on the page images (p8, p45–p53, p171; 200 dpi, with 400 dpi crops of
p46, p47, p48, p49, p171). The captain looked at every render, screenshot set and film frame set
before committing, and sent four of them back.

## Per task

| # | Task | Commit | Gate (captain, unpiped) |
|---|---|---|---|
| 1 | Source notes and config stations | 96187d9 | linux 670 passed, 3 skipped, 8 xfailed; mac 142 + 5 |
| 2 | Chapters 7–9 in the graph | e65bf84 | same run as Task 1 |
| 3+4 | Skins, roll-over, attachments, gear geometry; gear lump decomposed | 1828d49 | linux 737 passed, 3 skipped, 9 xfailed; mac 142 + 5 |
| 5 | Chapters 7–9 in the lab (opus) | 27576f8 | linux 741 passed, 3 skipped, 9 xfailed; mac 156 + 5 |
| 6 | Tour and chapter 9 film | 06b6d93 | linux 741 passed, 3 skipped, 9 xfailed; mac 160 + 5 |

Every commit also passed local `-m local_render` (5 passed), the lab unit tests (134/134 at the end)
and typecheck, the viewer tests (50/50) and `guide.check` (OK, RECALL 14/14, chapters 4–9 in scope).
Tasks 3 and 4 share one commit: both crews edited `core/ledger.py` and `data/mass_ledger.yaml` in
separate sections, and the hunks can't be staged apart without an interactive add.

## What changed in the evidence (captain's page reads)

- **Main axle F.S. 110.5 confirmed** (p50): the vertical reference is the spar's aft face "at B.L.
  26.75, and F.S. 125.5", and the axle goes 15 in forward of that straight edge; figure 1A prints
  110.5; p171 agrees. The research left out B.L. 26.75. W.L. −22 is typeset on p171.
- **Strip arithmetic confirmed** (p46): 50 in ending 15 in forward of F.S. 125, labelled F.S. 60 to 110.
- **Nose-wheel W.L. is not ambiguous in the owner's note.** The note reads "Nosegear CL is at W.L. −22
  not −23", matching CP25 LPC 24's text. The research had it reading −23. Only the struck typeset digit
  is unclear (−23 or −25). Kept flagged as `cp-corrected`; the nose gear is chapter 13.
- **Research corrections:** the rear baggage hole is 3¾ in, not ¾; the rear belts sit 8 in forward of
  the rear seat bulkhead, not "8 in between"; the harness insert's outboard edge is 4.0 from the box's
  outer end (CP27 LPC 52).
- **Roll-over placement** (not printed; view B-B is a sketch): the pieces fix it. The 2.7 in shoulder
  tops reach back to the seat back's top edge, so the front face is vertical at F.S. 79.05. The side
  pieces' 4.5 and 3 ends give the peak's depth, and then the back triangle's slant computes to 12.69
  against the printed 12.7. The first crew pass laid the box in the bulkhead's plane; the captain
  rejected it on the render.

## Review Focus

1. **Representational shown as book.** Every new solid has a fidelity, with citations checked. The
   strut, extrusions, tubes, axles, wheels, canard cutout and carved corners are representational.
   The jig blocks are book-shaped, but their placement follows the fitted tubes, so they are tagged
   representational. Lab e2e: these are striped and labelled "(fitted shape)", and book or derived
   parts and the ch7–8 plies are never striped.
2. **Axle station; track never measured.**
   - `fs_main_axle` is a property equal to `fs_spar_aft_face − 15`, and a test asserts 110.5 and W.L. −22.
   - The only track is `FITTED_TRACK` (84), a module constant. It is not in config, provenance, the
     ledger or the UI; tests check all of these, plus an e2e that no number follows "track".
   - The tip-over check is "not yet computed".
3. **Gear lump gone.** `landing_gear_weight_lb` and `landing_gear_arm_in` are removed. The physics
   items are now:
   - main strut, 22 lb at 110.5 (p50, p8);
   - nose strut, 2.8 lb at 17 (the station is a conflict);
   - "Wheels and brakes (unsourced)", 20.2 lb.

   Tests cover each row. The physics empty-structure CG moves from 103.35 to 104.77 in (correction
   ledger row 56). No test pinned it, and the accuracy report is unchanged.
4. **Ground handling.** The readout gives the main axle at F.S. 110.5 (book) and the 12° tip-back line
   (p171). Tip-back and tip-over are both "not yet computed". A unit test and an e2e refuse any digit
   in those checks.
5. **Bank order and sign.**
   - The graph requires skin-right before skin-left, and a test walks it.
   - TS and Python pose tests pin which side faces up.
   - The inversion starts at position-gear, and an e2e samples the poses.
6. **Skin schedule.** The third ply is clipped to the slanted front seat bulkhead line, and the strip
   spans F.S. 60–110 (±0.05). Both are tested; the ch4–6 ply areas are unchanged and pinned.
7. **No regression.** Against ec7ca75, `test_lab_e2e.py` lost no assertion line. Two helper tuples
   mirror the lab's chapter constants (`_bar_ops`, `_fuse_ops`). Canard frames are identical to HEAD
   (max diff 0).

   The Task 6 crew found that the chapter 6 film's closing cut showed the finished airplane on its
   gear. That is fixed, and an e2e now guards it.
8. **Nose-wheel conflict.** `fs_nose_wheel` is `conflict` (17 printed vs the manual's about 20), and
   this is tested.

## Outcomes the lead should know

- **Owner to confirm: the skinning pose.** The book says "45° left bank". A 45° roll from upright leaves
  the bottom half of each skin facing 45° down. p46 warns that glass falls off overhanging faces, and
  its cartoon shows the side and bottom up with the open top away. So the lab rolls the box 135°: the
  side and the bottom both face 45° up, and the box rests on its top corner. The UI keeps the book's
  words. This is a judgement call.
- **Correction-ledger rows 55–57.**
  - 55 (a): the gear tests now read the ledger rows; the total is still 45 lb.
  - 56: the CG shift.
  - 57 (b): the fuselage lower-bound weight sanity bound of 30 lb. The sourced ch7 skin glass takes it
    to 33.2 lb. A crew member had widened the bound to 40. The captain restored 30 and made it a
    strict xfail.
- **Captain fixes to crew work:**
  - **Roll-over:** it was in the bulkhead plane with a 10 in deep base, and the harness inserts were
    mislocated.
  - **Gear and datum:**
    - the gear strut was a bell with horizontal tips;
    - the datum board lay flat across the fuselage, when the page shows vertical boards at B.L. ±26.75;
    - the gear didn't follow the inversion.
  - **Lab:**
    - the finished airplane's gear passed through the bench; it now stands on its own feet on the
      floor, with wheels striped as fitted, because no tyre diameter is printed;
    - the home view had 17 labels; it now has 10;
    - the skinning pose (above).
  - **Smaller items:**
    - the strip wording in the ch7 text;
    - export tests now follow the exporter's chapter scope;
    - the ledger skips voids (the canard cutout).
- **Still flagged:**
  - **Roll-over roof length:** 13.28 computed from 8.4 × 12.6, against CP26's 13.
  - **Main-strut arm:** the axle station stands in for the strut's CG, which is not printed.
  - **Wheels-and-brakes row:** 20.2 lb, unsourced in weight and arm.
  - **Belt insert station:** F.S. 49.7–54.7, read at medium confidence.
  - **Not modelled:**
    - the extrusions' ⅜ holes (the ⅝ tube cannot pass them);
    - harness and tab hardware;
    - the 12-ply buildups, which have no printed outline.
  - **Lab weak spots:** the dry ply is pale at skin-right, the datum boards read as tall poles, and the
    axles and step are small in frame.
- **For deploy:** films are in the scratchpad only. `fuselage-ch9.mp4` runs 39.4 s and
  `fuselage-ch6.mp4` was re-recorded; re-render both at deploy. AGENTS.md's known-issues line on the
  fuselage box still describes chapters 4–6 only (no skins, roll-over or gear). Update it with the
  deploy.
- **Spec §5:** "the owner walks it" is the lead's.
