# Block 2 milestone 2.9: covers and consoles, finishing, upholstery (chapters 24 to 26)

Status: the captain approved this under the owner's delegation, 2026-10-04.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.8,
`docs/superpowers/specs/2026-10-04-block2-m28-strakes-electrical-engine-design.md`.

Evidence. Three Sonnet crews read the page images:
- `docs/harness/m29-research-a.md`: chapter 24, p159 to p161;
- `docs/harness/m29-research-b.md`: chapter 25, p162 to p169;
- `docs/harness/m29-research-c.md`: chapter 26, p170, plus the Owner's Manual weight-and-balance pages and an
  audit of the ledger rows.

The captain checked:
- the typed LC1 stations, FS 52 to 60 (plans-1980:p159);
- the OM sample loadings in the OM text (om-1980:p25).

## 1. Intent

The last three chapters close the airplane:
- **Chapter 24:** the lower aft cover, the left consoles LC1 to LC6, the thigh support and fuel-valve cover, the
  canard cover, and the seal for the gap between the wing and the centre section.
- **Chapter 25:** finishing. Feather fill, primer and paint, with white only on the upper wing and canard.
- **Chapter 26:** upholstery. Cushions, headrests and suitcases.

After this milestone every chapter of the book is in the rehearsal. Block 2's exit test, the ledger closure (2.n), is
the next milestone.

## 2. Evidence summary (model-bound values)

**Chapter 24.** Only one station is printed: LC1 runs FS 52 to 60 (plans-1980:p159, typed). The gap seal is
about 1/2 in, with 1/16 in left at the front (p161). The chapter prints no weights. Conflicts, carried:
- the aft-cover BID ply count: the scan's hand edit, LPC 54 and cobelu disagree;
- LC2 reads 30.6 on the scan, against 30.8 in cobelu.

**Chapter 25.** Thicknesses only: feather fill 0.02 to 0.03 in, primer 0.004 to 0.008 in. White only on the upper
wing and canard. Work at 70 F or above. No finish weight is printed. The N26MS finish deltas (CP26 p3 unfinished
against CP27 p1 painted) are references:
- canopy up to +1.0 lb;
- aileron +0.275 lb each;
- wing with winglets about +2.2 lb each.

**Chapter 26.** Sizes only for the cushions, headrests and suitcases. No weights, stations or materials.

**Owner's Manual, for the exit test:**
- Sample empty airplane: 730 lb at FS 111.7, moment 81541 (om-1980:p25, p35). The weighing table nets to 727.9;
  the moment closes once the printed left-main moment typo is read as 41106.
- Samples: the light pilot is 1113 lb at 103.96, and the OM itself says this is OUTSIDE the 103 aft limit. The heavy
  pilot is 1323 lb at 101.06, inside.
- Envelope: FS 97 to 103 up to 1325 lb. The takeoff-only band goes to 1425 (1420 in the p36 text, a conflict).

## 3. Rulings

- **Exit-test wording, corrected again.** The 2.n ledger closure must:
  - reproduce the OM sample empty airplane, 730 lb at FS 111.7, as the target. The 727.9 lb weighing-table net is
    noted, and the 2.n spec sets the tolerance;
  - reproduce both OM sample loadings exactly: the light pilot at 103.96, outside, as the manual says; the heavy
    pilot at 101.06, inside.

  "Both samples inside 97 to 103" was wrong, and the manual itself rules it out. Docs that say otherwise are fixed,
  with a ledger row if a test moves.
- **Finish weight.** No finish row is added on top of builder weights that are already painted. The N26MS ladder
  starts painted, so adding one would double-count. Finish enters the bottom-up ledger only in 2.n, from the per-part
  deltas or a stated allowance, flagged as such.
- The ledger cite "CP26 p16" for the painted wing weight is a page error; it is CP27 p1. Fix it.
- The chapter 25 colour rule appears in the lab as a white upper wing and canard. The rest of the finish is primer
  grey, a representational colour.
- The cushions and consoles are representational outlines, apart from LC1's printed stations.
- The op YAML is written by a Claude crew. The local-model lane is skipped, as in M2.8.

## 4. What the owner sees

- The consoles and covers go on.
- The gap seal is drawn at the wing root, and its 1/2 and 1/16 in read as text.
- The finish shows as fill, then primer grey, then the airplane in white on top. The readout gives the thicknesses,
  the 70 F rule, the N26MS finish deltas as references, and "no finish weight printed".
- The upholstery goes in: cushions, headrests and suitcases.
- The last op shows the whole airplane finished. The readout names the 2.n closure target: 730 lb at FS 111.7, both
  samples exact, the light pilot outside as the manual says. CG stays "not yet computed".

## 5. How it is built

**Crew A (Sonnet):**
1. The exit-test wording fix and the CP27 p1 cite fix.
2. Config and provenance for chapters 24 to 26, and the finish-delta reference rows.
3. The graph: `ch24` about 6 ops, `ch25` about 5, `ch26` about 2.
4. Geometry for the covers, consoles, seal and cushions, plus a finish layer (a colour and a thickness tag, not new
   solids) in the glb.

**Crew B (Sonnet):** the lab, with per-op shots and e2e. It must not change the readouts of earlier chapters (the M2.8
round-3 trap). The full `remote_test_all` must pass.

**Captain:** the Opus visual review, then the gates (`guide.check`, the leak scan, the grade). Then message the lead.

## 6. Done when

- Chapters 24 to 26 rehearse in WebKit.
- The finished airplane shows the white upper wing and canard.
- The exit-test wording is fixed everywhere.
- The gates are green, the visual review passes, and the lead verifies and pushes. Then deploy and republish.

## 7. Out of scope

The ledger closure itself (2.n). Upholstery mass, which no held source gives.
