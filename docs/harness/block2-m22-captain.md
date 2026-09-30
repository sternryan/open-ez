# Block 2 milestone 2.2 (fuselage box): captain log (Tasks 1–6)

Captain: Opus. Crew: sonnet in the foreground, opus where visual or judgement quality needs it (reason
logged). Start: main at 0c71719. Another lane has uncommitted `guide/build_site.py`,
`scripts/remote_test.sh`, `scripts/publish_public.sh`, `guide/leakcheck.py` and
`tests/guide/test_public_build.py`; this lane does not touch them.

## Page reads (captain, on the page images, before anything enters the model)

Pages rendered from the owner's scan at 300 dpi into the scratchpad (never committed). Footers confirmed
by eye: p33 4-1, p34 4-2, p35 4-3, p36 5-1, p37 5-2, p38 5-3, p39 6-1, p40 6-2, p41 6-3, p42 6-4,
p43 6-5, p44 6-6.

- **p36 side heights confirmed:** x = 0, 10 … 100, 103 give 19.8, 20.3, 20.5, 20.5, 20.5, 20.5, 20.5,
  20.4, 19.8, 18.4, 16.6, 16.0. At 300 dpi the "18.4" is a clear 4. Top edge straight at W.L. 23, both
  top corners square, overall 103.
- **p36 layout confirmed:** F28 5.65, panel 17.75, front seat bulkhead bottom 41.55 and top 59.75, top
  stiffener starts 17.0 aft of the panel line, rear seat bulkhead top 59.75 + 36.75 = 96.5, spar cutout
  6.5 wide by 8.5 deep at the aft end, rear seat bulkhead bottom 18.0 from the aft end (x = 85), sight
  gauge 82 from the front / 21 from the aft end, 9.15 down, section 2.5 / 2.5 / 1.0 with 0.2 foam left.
  Dish: 8 in diameter, centre 7 aft of the panel line and 7 below the top, right side only; text says 0.5
  deep, section C-C shows 0.3 (a conflict inside the page).
- **p33 front seat bulkhead confirmed:** 28.3 × 23 × 0.8, 0.7 taper at both ends, corner notches 0.7 ×
  1.5 at the top and 0.7 × 0.7 at the bottom, 2 UND ±45 front, 1 BID 45 back.
- **p34 rear seat bulkhead: the research pass misread it.** The research recorded 20.6 as the height and
  the top width as unprinted. On the page (300 dpi crop): the perspective block is labelled 20.6 on the
  edge the B-B section runs along (B-B shows the side slopes 1.3 / 1.5, so it is a width), 16.1 on the
  edge A-A runs along (A-A shows the 35° bottom and 45° TOP bevels, so it is the height), and 18.7 on the
  edge the "TOP" arrow points at. So: **bottom width 20.6, top width 18.7, length (slant) 16.1**, 0.95
  side taper, 0.7 × 1.4 lower-corner notches, 8 in foam circle, 7 in access hole. p38's spar-cutout
  sketch ("rear seat bkhd will go here") and p39 ("flush with the bottom and with the spar cutout") put
  its top at the cutout's lower forward corner, 8.5 below the top, not at the top edge.
  Cross-check: from (x 85, side bottom ≈ 19.1 down) to (x 96.5, 8.5 down) the slant is
  √(11.5² + 10.6²) = 15.6 against the printed 16.1 (bevels and tapers explain the 0.5). The front view's
  proportions (wider than tall) agree. The widths also say the sides converge aft: 23 at the front seat,
  20.6 at FS 107, 18.7 at FS 118.5.
- **p35 firewall:** outline is A4 only (template); 4 rectangular and 2 square 0.7 × 0.7 longeron holes;
  6 AN509-10R10; 0.040 Fiberfrax; handwritten CP25 LPC 25.
- **p37:** top longeron 1.0 × 0.7 × 103.5 (flush at front, 0.5 proud at rear), stiffener 0.7 × 0.4 × 55,
  LWY 9.0 / 7.0 / 2.0, LWX 14.7 / 12.4 / 35°, inside UND at ±30°, 1 BID over the longeron the full 103.
- **p38:** gear pad 6 BID 45 over the hatched area plus 15 more; 15.3 / 12 / 6.2 / 3.2 from the aft end;
  spar cutout 6.5 × 8.5; LMGA tube 6.75 × 5/8 × 0.049.
- **p39–p41:** jig blocks 2–3 ft long, 2–4 in thick, bench 85 in; bonding order front seat, instrument
  panel, F22, rear seat, firewall (p40, text); F28 5.9 in from F22's forward face (p41). p40's top-view
  sketch shows the sides narrowing toward both ends (undimensioned, not measured).
- **p42–p44:** bottom block 1.6 × 24 × 96 R45, butted to F22, trimmed 0.7 outboard of the side marks and
  1/4 aft of the rear seat mark; carved contours on p44 ("none critical").
- **Owner's handwritten notes** seen: p34 CP27 LPC 42 (OPT), p34 "CP#25 LCP #7 MEO" whose text is CP25
  LPC 17 ("both sides" means left and right, forward face only), p35 CP25 LPC 25, p36 CP25 LPC 5.
- **CP text checked** (parsed CP sections): CP25 LPC 5/17/19/20/25, CP26 34, CP27 42/43/46/47/48, CP28 58,
  CP29 67/68/70, CP30 82, CP34 105 read as the research says. CP29 LPC 70 corrects a CP28 builder hint
  (the plans already show ±30). **CP35 LPC 110 parses as an Owner's Manual engine-out note**, not the
  fuselage ply clarification the research names; Task 3 checks it before linking.

## Decisions
- FS = x + 22: side length 103 (p36) ends at `fs_firewall` 125 (p101). All derived stations use the
  printed coordinates exactly (front seat bottom 63.55, not the research's rounded 63.6).
- Plan-view inner width: 23 from the front seat bulkhead (p33) through its top station, then straight
  lines through 20.6 at FS 107 and 18.7 at FS 118.5 (derived, p34 + p36). Forward of the front seat the
  width is not printed; it is held at 23 and flagged unsourced (p40's sketch narrows, undimensioned).

## Task 1: source notes and config stations (7e4e0c3)
- Crew: one sonnet implementer (foreground), run in parallel with Task 3 (disjoint files). Captain
  reviewed the config diff and lowered the three reinterpreted rear-bulkhead values to medium confidence.
- 35 GeometricParams fields with provenance; `tests/test_fuselage_stations.py` (8 tests: provenance and
  citations, Review Focus 2 stations vs the 59/103 arms, the printed side table, both bulkhead slant
  cross-checks). Red first: 8 failed before the config; a broken x 90 height (18.9) and F28 (27.9) each
  fail their test.
- CP35 LPC 110 is not a fuselage entry; the only 103 in / 45° BID entry is CP30 LPC 82. The notes say
  "not found in the parsed CP text" for the research's "not an extra ply" claim.

## Task 3: chapters 4–6 in the graph (cfc3059)
- Crew: one sonnet implementer (foreground). 31 ops (ch4 8, ch5 9, ch6 14). The book's single wet
  assembly is split into ordered ops (front seat → panel → F22 → rear seat → firewall) so the order is
  machine-checkable; the captain rewrote those summaries so the twelve-hour rest follows the last bulkhead
  (the book floxes all five in one go after the dry run, p40–p41), not the first.
- CP links: 16 entries, all `verified`; CP25 LPC 19 (engine-mount extrusions) left out; CP48 LPC 128
  linked on the gear-extrusion op as an inspection note. Stub `c06.fuselage-assembled` replaced by
  `f06.bottom-tape` in ch12 and ch30. `guide.check` default chapters 4,5,6,10,12: RECALL 9/9, OK.
- **Lab kept canard-only for now.** The first gate run failed 12 lab e2e tests (Mac node): the bar and
  the "first chapter" tour now started at chapter 4. Fix: the lab's `NON_CANARD` gains 4 and 5, and
  `tourChapter` falls back to the first bar op. The e2e helper `_bar_ops` mirrors that constant, so its
  tuple changed from (0, 3, 6) to (0, 3, 4, 5, 6); no assertion changed. Task 5 adds the fuselage bench.
- Gate (both commits, one tree): two-node `remote_test_all.sh` linux 576 passed, 3 skipped (the new
  recall test skips without the corpus), 9 xfailed; mac 124 passed + 5 passed; local `-m local_render`
  5 passed; lab 88/88, typecheck clean; viewer 50/50; `guide.check` OK.

## Task 2: book fuselage geometry (0cdf591)
- Crew: sonnet implementer, then a sonnet fix pass (foreground). The captain looked at side, top and iso
  PNGs (scratchpad) after each pass.
- First pass problems the captain caught on the PNGs and page: the top longerons sat inside the side
  foam (they bond to the inside face, which is why the front seat bulkhead has 0.7-wide top notches);
  the sight gauge read as a 6.0 opening (the page gives 5.0: 2.5 either side of the x 82 line, a 1.0
  floor just forward of it, 0.2 foam left); the front seat bulkhead centred its 28.3 length and poked
  0.6 above the top. Fixed: the seat bulkheads are now inclined plates clipped flush with the top and
  floor (front, p39 "flush with the longerons") and with the spar face and floor (rear). Long faces
  come out 27.41 (printed 28.3) and 16.50 (printed 16.1); the DXF templates keep the printed sizes.
- The fix crew loosened its own new rear-bulkhead z test from 0.5 to 1.0; the captain replaced both
  loose bulkhead z checks with exact geometry (top at 5.6 ± 0.02; rear top at the cutout depth plus
  t/2 / cos(slope) ± 0.02). No committed tolerance moved.
- Retired: `Fuselage`, `BulkheadProfile`, `FuselageJigFactory`, `fuselage_bulkhead_heights`.
  `scripts/assembly_test.py` now passes on book geometry, so the strict xfail is removed (8 xfailed,
  was 9). AGENTS.md's known-issues line updated.
- Not modelled: the front seat bulkhead's small control holes (page not to scale), the rear bulkhead's
  side bevels, the lower triangular longerons, the gear pad solid and the extrusions.
- Gate: linux 603 passed, 3 skipped, 8 xfailed; mac 124 + 5 passed; local_render 5 passed.

## Task 4: areal weights and ledger areas (f41ac44)
- Crew: one sonnet implementer (foreground), web fetch allowed for the datasheets.
- Captain checks before commit: Wicks RA5277 page (8.8 oz/yd², 38 in) and RA5177 page (7.02 oz/yd²,
  38 in) re-fetched; CP34 foam table read in the CP text (R45 3, R250 16 lb/ft³); plans p21 page image
  read (resin about half the cloth weight on an excellent layup); p13 image (RA5277 BID, RA5177 UND).
  The chapter 2 bill of materials (p9) names the cloths only as BID and UND; the style numbers are on p13.
- Captain fixes: the rear seat bulkhead's front UND subtracted the 7 in hole from a face that already
  lacked it (244.8 in² for a 283.3 in² face). Its back BID covered only the 7–8 in ring; p34 section
  C-C runs it over the back face and into the circle. Both fixed (graph row reworded), the test that had
  encoded the double subtraction rewritten, the now-unused Annulus region removed.
- Result: every part's strict total is "not yet computed" (birch ply and spruce densities unsourced; the
  firewall and longerons have no core mass; several tape rows have no printed width). `fuselage_cg()`
  returns no weight; `fuselage_cg(lower_bound=True)` gives about 24.5 lb at FS 63.2 over 8 parts,
  labelled an undercount.
- Gate: linux 642 passed, 3 skipped, 8 xfailed; mac 124 + 5 passed; local_render 5 passed;
  guide.check OK.

## Task 5: fuselage in the lab (a92f15a)
- Crew: one **opus** implementer (foreground, about 60 min). Why opus: cross-stack (CadQuery export,
  build_site, a TS scene, cut shader, e2e on two engines) and the bar is visual; 2.1b's sonnet visual
  passes needed opus escalation twice.
- Design: a Canard | Fuselage subject control in the op bar. The canard is the default and unchanged:
  the crew diffed canard frames against HEAD built in a scratch worktree (home view max diff 0, top-skin
  op with the cut at B.L. 20 at most 1/255). No existing e2e assertion changed; two fixtures/range checks
  now skip `fuselage.*` nodes (the canard B.L. range check and the build-state fixture), and the classic
  viewer ignores `fuselage.*` meshes.
- Captain looked at the eight GPU-path screenshots (1180×820 and one 390×844, scratchpad `t5/`):
  - fuselage home: the finished box on its bench in the shop, labels "(fitted shape)" on F22, F28, panel,
    firewall and bottom, the stripes legend and the CG row reading "not yet computed";
  - f04 front seat bulkhead mid-lay: the bulkhead flat on the table, UND going down with the wet front,
    the same materials as the canard;
  - f05 inside layup: both sides flat inside-up with the longerons, spar cutouts and sight gauges; the
    ch4 bulkheads lie behind, the fitted ones striped;
  - f06 bond-panel: the box upside down on the jig (the panel's leg cutouts point up), the striped panel
    in, F22 not yet;
  - section at FS 72: the cut shows the box's caps and the readout lists the layers; weaker than the
    canard's cut because 0.06 in plies are hairlines at a whole-box view.
  Honest gap against the canard chapters: labels crowd at the fuselage home; the dock is tall and covers
  the box's nose in some shots; the stripes are loud on the large bottom plate; the CG detail line shows
  an internal part id ("top_longeron"). **Chapter 4's bar starts with the firewall**, because the graph's
  topological order sorts ops by id within a chapter; the book's order is front seat, rear seat, panel,
  firewall. Left for the lead (changing the sort would touch the canard's order).
- Gate: linux 649 passed, 3 skipped, 8 xfailed; mac 130 + 5 passed; local_render 5 passed; lab 101/101,
  typecheck clean; viewer 50/50; guide.check OK. Crew locally: lab e2e 67/67 chromium, 67/67 webkit.

## Task 6: tour and film (0fbbd08)
- Crew: sonnet implementer, then a sonnet follow-up after the captain looked at the film frames
  (foreground both).
- The fuselage tour gets chapter cards and, for chapter 6 alone, a closing station cut at FS 72 (front
  seat bulkhead) with the cursor dragging the real slider. The Tour button tours the selected op's chapter
  or all of 4–6. `record -- fuselage6` records the chapter 6 film; `record -- canard` is unchanged.
- Captain's look at the first film's frames: the cut was a far view with the box small, and the F22, F28
  and panel labels floated over the table where the cut had removed them. Follow-up: labels of parts
  wholly forward of the cut hide while it is on (unit test on the pure rule; no in-page e2e drives it,
  the film frames are its check), and the cut step flies to a close shot of the cut face and orbits it.
  Re-rendered frame at 46 s: the FS 72 face fills about two thirds of the frame (front seat bulkhead
  with its ply stripes, side walls, longeron caps, the striped bottom); only parts the plane passes
  through or that sit aft are labelled. Labels bunch along the top edge of that shot.
- Film: scratchpad `t6/film/fuselage-ch6.mp4`, 60.08 s, 1920×1080, 60 fps, 111.8 MB, rendered from a
  fresh export and site build on the Metal GPU path (first render 257 s).
- Gate: linux 649 passed, 3 skipped, 8 xfailed; mac 132 + 5 passed; local_render 5 passed; lab 105/105,
  typecheck clean; viewer 50/50; guide.check OK.

## Polish round (lead's request, after Task 6)
- **Book order (6190e5c), captain inline.** `topo_order` breaks ties within a chapter by the chapter
  file's list order instead of the op id. Chapter 4 now reads front seat, rear seat, panel/F22/F28,
  firewall. A snapshot of the canard chapters' 23-op order, taken before the change, is asserted equal
  after it; the test fails with the old tie-break.
- **Visual polish (7aee109), opus crew** (visual judgement): priority/collision label placement for the
  fuselage only; the CG and legend rows fold behind one remembered line (closed by default, openable on
  phones); stripes thin on large fitted faces (cut faces and bulkheads keep full stripes); the CG detail
  names parts in words (fixed at the ledger's reason strings); a 1 s eased flip at the bottom-bond op,
  reversible, on sim time; an in-page e2e drives the label-hiding rule under the station cut.
  Canard frames against HEAD built in a scratch worktree: home and top-skin-with-cut both max diff 0.
  Lab e2e 71/71 on each engine (3 new, each fails on HEAD's build).
- Captain's look (scratchpad `t7/`): the fuselage home now has nine non-overlapping labels and the nose
  is clear of the dock; the cut close-up has four labels; mid-flip reads (box lifted, bottom face-on);
  phone shows the opened CG reasons and legend. Still true: at the home view F28's label is dropped by
  the collision rule (the part stays striped); the bottom's inside face in the cut close-up is still
  boldly striped; one phone label collapses to a bare dot.
- The chapter 6 film was not re-rendered after the flip; re-render at deploy.
- Gate: linux 651 passed, 3 skipped, 8 xfailed; mac 138 + 5 passed; local_render 5 passed; lab 116/116,
  typecheck clean; viewer 50/50; guide.check OK.
