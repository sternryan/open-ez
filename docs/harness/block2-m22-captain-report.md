# Block 2 milestone 2.2 (fuselage box): captain report (Tasks 1–6)

Plan `docs/superpowers/plans/2026-09-30-block2-m22-fuselage.md`, Tasks 1–6. Spec
`docs/superpowers/specs/2026-09-30-block2-m22-fuselage-design.md`. Full log:
`docs/harness/block2-m22-captain.md`. Nothing is pushed or deployed.

**Method.** Crew ran in the foreground: sonnet by default, and opus for Task 5 (the lab), because it was cross-stack work with a visual bar. Every gate run was in the foreground. Before any value entered config or geometry, the captain read it on the page images (p9, p13, p21, p33–p44, rendered at 300 dpi into the scratchpad). The captain also looked at every visual result (PNGs, lab screenshots and film frames) before committing.

## Per task

| # | Task | Commit | Gate (captain, unpiped) |
|---|---|---|---|
| 1 | Source notes, config stations | 7e4e0c3 | linux 576 passed, 3 skipped, 9 xfailed; mac 124 + 5 |
| 3 | Chapters 4–6 in the graph | cfc3059 | same run as Task 1 |
| 2 | Book fuselage geometry, placeholder retired | 0cdf591 | linux 603 passed, 3 skipped, 8 xfailed; mac 124 + 5 |
| 4 | Ply areas, material weights, ledger | f41ac44 | linux 642 passed, 3 skipped, 8 xfailed; mac 124 + 5 |
| 5 | Fuselage in the lab (opus) | a92f15a | linux 649 passed, 3 skipped, 8 xfailed; mac 130 + 5 |
| 6 | Tour and chapter 6 film | 0fbbd08 | linux 649 passed, 3 skipped, 8 xfailed; mac 132 + 5 |

Every commit also passed:
- local `-m local_render`: 5 passed;
- the lab unit tests (105/105 at the end) and a clean typecheck;
- the viewer tests, 50/50;
- `guide.check` with the env sourced: OK, RECALL 9/9, with chapters 4, 5 and 6 now in scope.

Tasks 1 and 3 had disjoint files and ran in parallel. They were gated as one tree and committed separately.

## What changed in the evidence

- **The rear seat bulkhead was misread by the research pass.** On p34 (captain's 300 dpi read), 20.6 is the bottom width, 18.7 the top width and 16.1 the slant length. The research had it as a 20.6 height with an unprinted top width. p38 and p39 put its top at the spar cutout's lower forward corner, 8.5 below the top edge, not at the top edge. Three cross-checks agree:
  - the slant computes to 15.6;
  - the front view is wider than it is tall;
  - the widths show the sides converging aft (23 → 20.6 → 18.7).
  These three values are set to medium confidence.
- **Derived stations use the printed coordinates exactly.** The front seat bulkhead bottom is 63.55, not the rounded 63.6. The panel is 39.75, with a conflict note against the manual's 40.
- **CP35 LPC 110 is not a fuselage entry.** It is an Owner's Manual engine-out note. The "103 in BID ply at 45°" is CP30 LPC 82, and the research's "not an extra ply" claim was not found in the parsed text.
- **The owner's p34 note reads "LCP #7".** Its content is CP25 LPC 17.
- **Plans-internal conflict kept:** the dish is 0.5 deep in the text and 0.3 in section C-C. The model uses 0.5 and flags the conflict.

## Review Focus

1. **Representational shown as book.**
   - `FusePart` refuses a missing or unknown fidelity, and a book or derived part without a valid citation (tested).
   - F22, F28, the panel, the firewall and the bottom are representational.
   - In the lab they carry amber stripes on surfaces and cut caps, and are labelled "(fitted shape)". Their plies inherit the tag.
2. **Occupant arms vs bulkheads.** `fs_pilot_seat` 59 and `fs_rear_seat` 103 are unchanged. A test holds them apart from every bulkhead station. They were not renamed: the physics uses them, and the placeholder that misused them as loft stations is gone.
3. **Side profile.** Both side solids are sampled at the 12 printed stations: the bottom is within ±0.05, and the top is at W.L. 23, or at the cutout depth inside the spar cutout. The test hard-codes the printed table, and a perturbed height fails it.
4. **Book-order assembly.** Chapter 6 encodes the install order front seat → panel → F22 → rear seat → firewall as a requires chain, and a test walks it. The lab puts each bulkhead in at its own op, and an e2e test checks that F22 is absent after the panel op.
5. **Canard regression.** No M2.1b e2e assertion changed.
   - Task 5's crew diffed canard frames against HEAD: the home view has max diff 0, and the top-skin op with the cut at B.L. 20 differs by at most 1/255.
   - In Task 3 the e2e helper `_bar_ops` had to mirror the lab's canard-only chapter set, so its tuple changed from (0, 3, 6) to (0, 3, 4, 5, 6).
   - In Task 5, the canard B.L. range check and the build-state fixture now skip `fuselage.*` nodes, and the classic viewer ignores `fuselage.*` meshes.

## Outcomes the lead should know

- **The placeholder is retired.** `Fuselage`, `BulkheadProfile`, `FuselageJigFactory` and the unsourced bulkhead heights are gone. `scripts/assembly_test.py` now passes on book geometry, so its strict xfail is removed and the xfail count is 8. The assembly's weight and CG printout is the old rough volume estimate and means nothing.
- **Nothing gets a CG yet.** Every fuselage part's strict mass is "not yet computed":
  - birch ply and spruce densities are unsourced;
  - several tape rows print no width.
  The lab's CG row says so. A lower bound, labelled as one, is shown as "≥ 24.8 lb at FS 63.8, 8 parts".
  - The sourced inputs are RA5277 at 8.8 and RA5177 at 7.02 oz/yd² (Wicks listings under the plans' own cloth names, re-fetched by the captain), R45 at 3 and R250 at 16 lb/ft³ (CP34), and resin at about ½ the cloth weight (p21). The p21 figure is an "excellent layup" target, so the glass masses are a floor.
- **Captain fixes to crew work:**
  - the top longerons sat inside the side foam;
  - the sight gauge had a 6.0 opening instead of 5.0;
  - the front seat bulkhead poked 0.6 above the top, and the seat bulkheads are now clipped flush at the longerons, spar face and floor;
  - a crew-loosened test tolerance was replaced with exact geometry;
  - the rear bulkhead's UND subtracted the access hole twice;
  - its BID was limited to the 7–8 in ring, and is now the back face per section C-C;
  - the ch6 texts put the twelve-hour rest after the first bulkhead instead of the last;
  - in the film, labels of cut-away parts floated over the table, and the cut was a far view.
- **Not modelled:**
  - the front seat bulkhead's control holes (the page is not to scale);
  - the rear bulkhead's side bevels;
  - the lower triangular longerons;
  - the gear pad solid and the extrusions;
  - the bottom's carved contour.
  Forward of the front seat the inner width is held at 23 and flagged unsourced; p40's sketch narrows it, undimensioned.

## For Task 7 (lead)

1. **Re-export before deploying** (`guide.export_glb`, then `build_site`). `output/` is untracked, and the glb now carries the fuselage, `layup.json` a `fuselage` block, and the site a `ledger.json`.
2. **The film** is in the captain session's scratchpad at `t6/film/fuselage-ch6.mp4`: 60.08 s, 1920×1080, 60 fps, 111.8 MB. It is not in the repo. Re-render with `npm --prefix guide/lab run record -- fuselage6 <out.mp4> 60 <url>` against a served build.
3. **For the owner's walk:**
   - The four new owner's-note annotations (pp 34–36) are captain-read and marked confirmed so the recall gate scores them. They await the owner's look.
   - The rear seat bulkhead reading.
   - Chapter 4's bar starts with the firewall. The graph's topological order sorts by op id within a chapter, while the book's order is front seat, rear seat, panel, firewall. Changing the sort touches the canard's order, so it is left for you.
4. **Visual gaps against the canard chapters:**
   - labels crowd at the fuselage home view and along the top of the cut close-up;
   - the dock is tall at 1180×820 and covers the box's nose in some shots;
   - the stripes are loud on the large bottom plate;
   - the CG detail line shows an internal part id (`top_longeron`);
   - there is no flip animation when the box turns right side up;
   - the CG and legend rows are hidden on phones.
5. The label-hiding rule under the station cut is unit-tested on the pure rule only. No in-page e2e drives it; the film frames are its check.
