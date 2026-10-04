# Block 2 milestone 2.7: wings and winglets (chapters 19 and 20)

Status: the captain approved this under the owner's delegation, 2026-10-03.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.6,
`docs/superpowers/specs/2026-10-03-block2-m26-canopy-design.md`.
Evidence: `docs/harness/m27-research-a.md` (ch19 p118-p126 and the wing LE question),
`m27-research-b.md` (ch19 p127-p134), `m27-research-c.md` (ch20 p135-p140), all read from page images
by Sonnet crews. The captain re-read the model-bound values on the images (section 2.4): p126, p122,
p135 and p136. One crew value was wrong and is corrected here (the winglet tip chord).

## 1. Intent

Each wing is built LE-up in five floor jigs from seven foam blocks: shear web, hard points, spar caps
and skins, then the ribs, the aileron cut-out and the aileron, the controls, and last the line-bored
attach to the centre-section spar. Chapter 20 hot-wires the winglets, skins them flat, jigs each one to
its wingtip by the A, B and C dimensions, joins it with the corner layups, adds the lower fin, and cuts
and hangs the rudder. After this milestone the airplane has its wings, and the ledger gains the sourced
wing, aileron and winglet builder weights as reference rows.

## 2. Evidence summary (model-bound values)

### 2.1 Wing planform, right wing (plans-1980:p126, scale 1/10; left is the mirror)
- **Book, high:** stations BL 55.5, 106.25, 157 (the three rib stations; BL 23 is the root rib).
  - LE: FS 112.9 at BL 55.5, FS 156 at BL 157, straight between, 22.98 deg.
  - TE: FS 155.6 at BL 55.5, 165.8 at BL 106.25, 176 at BL 157, 11.36 deg; inboard kink 12.49 deg
    to FS 148.4 at BL 23.
  - Chords 42.7 / 31.35 / 20.0; thickness 16.2 / 15.7 / 15.0 per cent; twist 0.6 washin / 0.96
    washout / 2.7 washout; airfoil modified Eppler 1230 throughout.
  - Shear web forward face (foam edge): FS 125.6 at BL 23, 130.5 at BL 55.5, 147.35 at BL 106.25,
    164.2 at BL 157 (18.42 deg). Spar cap 3.0 wide.
  - All chord lines at WL 17.4 (LE flat); TE rises from WL 16.95 at BL 55.5 to 18.35 at BL 157.
  - Aileron outboard end BL 118.1 (p126, p119, p171 agree).
- **Derived:** LE at BL 58 = 112.9 + 2.5 tan 22.98 = 113.96, which agrees with CP25 LPC 7 (113.9).
  The inboard core FC1 (BL 23 to 55.5) lies aft of the shear web only; forward of it, inboard of BL
  55.5, is the strake (chapter 21, not modelled here).
- **Conflict:** the p126 LE label at BL 106.25 prints 134.95; the same page's chord (31.35) and TE
  (165.8) give 134.45, and the 22.98 deg line gives 134.42. The page's hand renders 4 like 9 (it
  prints W.L. 17.40 that way, and 148.4 that way, both confirmed elsewhere). Carried as a conflict
  pair; the model uses the straight line and is unaffected.

### 2.2 Wing structure
- **Book, high:** seven blocks per wing (five 7x14x64, two 7x14x41); core angles 78.64 / 77.51 deg;
  FC1 LE check 32.87.
- Shear web layup 2: 45 deg UND, 6 plies BL 23-70, 4 plies BL 70-120, outboard BL 120-157 printed 3,
  **cp-corrected to 2** (CP26 LPC 31).
- Bottom cap 5 plies 3 in UND tape: 142, 135, 84, 52, 19.5 long (p122; the 5th digit medium).
  Top cap 7 plies: 142, 142, 119, 90, 61, 39, 20 (p123). The CP25 p6 thin-tape box adds plies only when
  the 5-ply test reads thin (CP28 LPC 56 makes it mandatory then); the model draws the base schedule and
  says so.
- Skins: bottom 2 UND + BID tip; top 2 UND + a third UND forward of the hinge line + BID tip; 2 in LE
  lap, 0.5 min TE lap (CP32).
- Hard points LWA4 (2, outboard) and LWA6 (1, inboard), plates LWA3 / LWA2 / LWA7 (CP25 LPC 9-12
  renames applied); attach bolts 2 x AN8-21A + 1 x AN8-23A per wing; LWA9 bushings, 6 per wing.
- Aileron: BL 55.5 (skin cut at the foam joint, vertical plane, CP34 LPC 107) to BL 118.1; skin cuts
  5.9 / 4.35 top and 7.6 / 5.65 bottom at BL 55.5 / 106.25; 3/8 steel LE rod (A13, 65 in), A10 torque
  tube 3/4 x .058 9 in long, three piano hinges (A3 8 in, A4 6 in x 2); stop at 20 deg up.
- **Conflict (carried, no winner):** p171 prints the aileron inboard end at BL 54.3, p124 cuts at
  55.5 (A10 overhangs 1 in); attach bolt spacing 28.85 (p134 drawing) vs 28.83 (p134 text).

### 2.3 Winglet and rudder (plans-1980:p135, p136)
- **Book, high:** upper fin WL 18.4 to 65.4 (47.0), 1 in urethane cap to WL 66.4; lower fin bottom
  WL 9.8. Root TE FS 186.8, top TE corner FS 196.6. Winglet root LE FS 160.5 at the wing top surface,
  4.5 in aft of the wingtip LE FS 156 (p136 side view). The straight LE line meets WL 18.4 at FS 159.7
  (p135). Rudder hinge FS 176.8; rudder 10 in wide at WL 18.4, 12.14 at its top, 11.5 at its bottom,
  14.5 tall (10.5 above WL 18.4, 4 below); 30 deg max travel.
- Jig: WPRP = inboard front corner of the aileron cut-out, BL 55.5, FS 149.6. A 102.15 (to the LE mark
  on the wing top), B 108.35 (root TE), C 118.35 (tip TE); A and B within .05, C within 1 (CP25 LPC 6).
- Skins: two crossed UND plies each side, a 3rd BID ply 18 x 14 on the upper winglet root (CP34 LPC
  104); corner layups 1-5 with the printed UND table (24/12 down to 12/6).
- **Derived, medium (captain pixel read, scaled by the printed 10 and 12.14 rudder widths):** tip chord
  at WL 65.4 about 11.4 (tip LE about FS 185.2); LE sweep about 28 deg; root chord at WL 18.4 about
  27.1 (to the 159.7 line). Crew C read the tip chord as 28.9; that is wrong (the fin tapers, it does
  not widen) and is not used.
- **Derived, low:** inward cant at the tip about 3.6 in over 47 (C 118.35 closes only with a lean; B
  closes within 0.25). No cant or toe angle is printed; both are representational.
- **Representational:** both airfoils (A3, A11, A14 are A-sheets the owner does not hold), the lower
  fin outline, block A, the tip cap, the fairing block, the CS301 belhorn outline.

### 2.4 Captain re-reads on the images (2026-10-03)
- p126: 112.9, 125.6, 130.5, 147.35, 155.6, 164.2, 167.2, 165.8, 176, 156, 42.7, 31.35, 20.0, 22.98,
  18.42, 11.36, 12.49, 8.57, 0.6 / 0.96 / 2.7, 118.1, WL 17.40, FS 148.4 in the note: confirmed. The
  134.95 label stays a conflict (section 2.1).
- p122: bottom cap 142 / 135 / 84 / 52 / 19.5 and the 5 / 12 / 19 / 26 offsets: confirmed.
- p135: 196.6, 65.4 / 66.4, 18.4, 9.8, 186.8, 176.8, 160.5, 159.7, 12.14, 10, 11.5, 14.5, 4, 48, 78.64 /
  101.36: confirmed. Tip chord re-measured (section 2.3).
- p136: A 102.15, B 108.35, C 118.35, WPRP BL 55.5 / FS 149.6, the 4.5 LE offset, 18 in BID patch:
  confirmed.

### 2.5 Mass (reference rows, never in a sum)
- cp-text:p26 (CP26 page 3, Melvill N26MS): wing skinned 46 lb; with root ribs and TE spar 46.5 lb;
  aileron complete 5.125 lb; wing complete to end of ch19 51.5 lb; upper winglet with antenna 6 lb;
  lower winglet 1.19 lb; wing with winglets and rudder 64 lb. CP27 (N26MS evaluation): wings with
  ailerons and rudders 64 lb each, rudders painted 1.2 lb each.
- The analysis's `wing_weight_lb` 85.0 (unsourced, both wings) stays as is until ledger closure (2.n),
  which must reconcile it with 2 x 64 = 128 lb. Recorded, not changed here.

## 3. Rulings

- **Wing LE 125.61 vs 113.9: closed.** They are different points. 113.9 is the strake/wing LE kink at
  BL 58 and agrees with p126. 125.6 on p126 is the FC1 foam edge at BL 23 (the shear web face), not a
  wing LE; the retired 125.61 was a fitted value in an old frame and has no book meaning. Recorded in
  `docs/geometry-correction-ledger.md` and the provenance note on `wing_le_anchor`.
- The analysis planform (`wing_span` 313.2, `wing_root_bl` 23.3, `wing_washout` 1.0) is not moved in
  this milestone: moving it changes the NP and belongs to Block 3. Each gets a provenance note naming
  the book value (BL 157 gives 314; the plans print BL 23; twist 0.6 washin / 0.96 / 2.7 washout).
  `wing_washout` gains a provenance entry (`unsourced`, with that note).
- The winglet analysis fields (`winglet_height` 16, `winglet_root_chord` 20, `winglet_tip_chord` 12)
  match no page. They get `unsourced` provenance entries naming the book geometry; the chapter 20
  build model uses new book-sourced `winglet_*_book` fields. The VSPAERO leg is not re-run here
  (openvsp is not installed locally); TODOS gets the item.
- The shear web outboard ply count is the cp-corrected 2. The spar caps are the base schedule.
- Book op order, except: the incidence board (p124) is placed with the ribs; the controls op
  (`f19.controls`) needs `f16.sticks-pushrods`; the attach (`f19.attach`) needs `f14` spar ops and
  replaces the `c19.wings` stub; `f20.rudder-hang` replaces the `c20.winglets` stub in ch16's
  requires.
- The left wing is the mirror of the right (p126, p135).

## 4. What the owner sees

- Five jigs on the floor, LE up; the seven blocks become FC1 to FC5 with their cut-outs; the cores go
  into the jig and the shear web plies lay down in their three span zones (2 outboard, labelled
  cp-corrected).
- Hard points and plates, the LE cores, the wing flipped onto the table for the bottom cap (5 plies,
  staggered) and skin, back in the jig for the top cap (7 plies), conduit and top skin.
- Ribs, the aileron cut free along its hinge line, the aileron built and hung, deflecting to its 20 deg
  stop; the belhorn and brackets at the root.
- The wing slides onto the centre-section spar and the three bolts go in (the fuselage scene).
- Chapter 20: winglet cores, flat skinning, the trim template, the winglet standing on the wingtip
  with the A, B and C dimension lines drawn from the WPRP; corner layups, block A, the lower fin; the
  rudder cut, hinged and swinging to 30 deg.
- Readout rows: wing (CP26 builder weight) 51.5 lb each to end of ch19, 64 lb with winglets and rudder,
  aileron 5.1 lb, winglets 6 / 1.2 lb; all "reference, not in CG". CG stays "not yet computed".
- The two conflicts on their ops as text (134.95 vs 134.45 on `f19.cut-cores`; aileron BL 54.3 vs 55.5
  on `f19.aileron-cut`), never bare numbers. Representational parts striped "(fitted shape)".

## 5. How it is built

- **Config and provenance** (`config/aircraft_config.py`): the p126 stations, structure counts, aileron
  and winglet book values, each with a `GEOMETRY_PROVENANCE` entry; the provenance notes in section 3;
  the ledger reference rows in `data/mass_ledger.yaml` `prototype_weights`.
- **Graph** `guide/graph/ch19.yaml` (about 18 ops) and `ch20.yaml` (about 9 ops), components, pages,
  stubs replaced. The smithy local-anvil lane drafts the op YAML first (requests under 20k tokens, one
  chapter half per request); a Sonnet crew fixes and finishes it; it must pass `guide.check`. If the
  drafts again need wholesale rewrites, the log says so and the lane stays skipped for op YAML.
- **Geometry** `core/wing_book.py` and `core/winglet_book.py`: planform from the p126 stations with the
  Eppler 1230 file at the printed thickness and twist (representational section, book planform); cores
  FC1-FC5 split at the shear web and rib stations; shear web and caps as plies; the aileron and rudder
  as separate solids on their hinge lines; the winglet placed from the A, B, C jig and the 4.5 offset.
  Small kernels fully expressed by tests (planform stations, the A/B/C closure, the aileron and rudder
  hinge poses) go through `/conduct` on local-anvil.
- **Lab**: a Sonnet crew, using the M2.5/M2.6 pattern: per-op shots, pixel e2e checks per op, the ply
  lay-downs, aileron and rudder travel, the ch19/ch20 tour. The wing bench is its own scene framing;
  the attach op returns to the fuselage scene.

## 6. Done when

- Chapters 19 and 20 rehearse in WebKit, including aileron and rudder travel and the winglet jig.
- Every new solid has a fidelity tag; representational parts are striped. Both conflicts are visible
  as text. The wing LE question is closed in the ledger.
- The reference weight rows are in the readout.
- The gates are green and the captain's visual review has passed. The milestone is graded, pushed
  (checked with ls-remote), deployed and republished.

## 7. Out of scope

Strakes, fuel and the wing/spar gap seal (chapters 21 and 24); vortilons and the high-performance
rudder (later CPs, noted only); re-running VSPAERO; moving the analysis planform.
