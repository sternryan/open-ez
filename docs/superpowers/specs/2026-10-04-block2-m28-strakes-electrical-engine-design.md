# Block 2 milestone 2.8: strakes, electrical, engine as built in the book (chapters 21 to 23)

Status: the captain approved this under the owner's delegation, 2026-10-04.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.7,
`docs/superpowers/specs/2026-10-03-block2-m27-wings-winglets-design.md`.
Evidence: `docs/harness/m28-research-a.md` (ch21 strakes and fuel, p141-p148), `m28-research-b.md` (ch22
electrical, p149-p155), `m28-research-c.md` (ch23 engine, p156-p158). All three were read from page images by
Sonnet crews. The captain re-read p147 (strake stations) and p156 (engine choice and the 246 lb limit) on the
images, and checked the Owner's Manual sample empty weight and CG in the text (730 lb at 111.7).

## 1. Intent

The strakes are built on a jig table level with the longerons, using ribs, baffles, the sump blister and skins,
and the fuel tanks are sealed inside them. The electrical system puts the 25 Ah battery in the nose and runs the
wiring, the relays and the lights. Chapter 23 is a three-page delta: engine choice, weight limits, the throttle
and mixture bracket, cowl trim and reinforcement, and the wing-root metal rib. The engine installation itself
lives in VariEze Sections IIA, IIC and IIL, which the owner does not hold. After this milestone the airplane is
complete as the plans draw it, and the ledger holds every sourced builder weight the exit test needs.

## 2. Evidence summary (model-bound values)

- **Strake planform** (plans-1980:p147, right strake; left is the mirror). Book, high, captain re-read:
  - LE at the fuselage side FS 50; kink FS 73.3 at BL 23; FS 99.5 at BL 45. It meets the wing LE at BL 58,
    FS 113.9 (CP25 LPC 7).
  - Spar forward face FS 118.5 at BL 23. BAB meets the fuselage side at FS 103.5. The sump runs FS 103.5 to
    about 125. Ribs R23 and R45 run along BL 23 and BL 45.
  - The printed parts sizes (p141) close against p147: B23 is 21.3 printed vs 21.2 derived; DB is 28.5 printed
    vs 28.3 derived.
- **Fuel:**
  - 6.0 lb/gal, arm FS 104.5 (om-1980:p25, p26).
  - Capacity is a conflict, carried: plans-1980:p141 says 2 x 25.5 gal; om-1980:p8 says 2 x 28 and 52 total.
    The model keeps 26 per side and flags the conflict.
- **Electrical:**
  - Battery: 12 V 25 Ah Gill PSG-9 on a nose shelf bonded to NG30 and F6 (plans-1980:p150, p151, p155).
  - Battery station: not printed (A6 only). It is carried as a range, FS 0 to 22, representational.
  - Starter, ring gear and alternator at "station 150+" (cp-text:p27 page 4).
  - The plans print no weights here except "electric start adds over 25 lb" (p149).
- **Engine:**
  - O-200 or O-235 only; engine with accessories at most 246 lb; vibrating mass at most 286 lb (plans-1980:p156).
  - Oil 8 lb at FS 140 (om-1980:p25).
  - No engine, mount, prop or spinner station is printed in any held source. The engine solid is
    representational: an O-235-sized block aft of the firewall, on BL 0, with 2 deg down thrust (CP32, CP38).
- **Builder weights** (reference rows, never summed), all from the N26MS empty-weight ladder in cp-text:p27
  page 4: 693.4 / 698.3 / 713.7 / 761.9 / 777.3 / 815.4 / 860.2 / 883.0 lb. Every step re-adds; the arithmetic is
  checked in research B section 3a. Also the dynafocal mount, 5.19 lb (CP26 p3), and the cowl, 18 lb glass or
  12 lb graphite (CP27 p5).

## 3. Rulings

- **Exit-test target, corrected.** The Owner's Manual sample empty airplane is 730 lb at FS 111.7
  (om-1980:p25, p35). The FS 97 to 103 band is the LOADED CG envelope (om-1980:p28), not the empty CG. The ledger
  closure (after 2.9) must:
  - reproduce an empty weight and CG comparable to 730 lb at 111.7, with the tolerance set in the 2.n spec;
  - reproduce both OM sample loadings exactly: the light pilot at 103.96, OUTSIDE 97 to 103 as the manual says, and
    the heavy pilot at 101.06, inside (corrected in M2.9; "both inside" was wrong).
  Any existing test or doc that grades the empty CG against 97 to 103 is wrong and gets fixed or re-labelled,
  with a ledger row.
- **Folded analysis values, where the book settles them** (lead instruction 2026-10-04):
  - `wing_span` 313.2 -> 314.0. The plans print the tip rib at BL 157 (p126, p171). The OM's 26.1 ft is
    313.2 in, which is not a rounding of 314 in (26.17 ft rounds to 26.2). So the OM figure becomes a
    noted conflict, and the plans govern geometry.
  - `wing_root_bl` 23.3 -> 23.0, because the plans print BL 23 on p118, p119, p126 and p147.
  - `winglet_height` 16.0 -> 47.0 (book, WL 18.4 to 65.4, p135).
  - `winglet_root_chord` 20.0 -> 27.1 (derived from printed FS 159.7 and 186.8, p135).
  - `winglet_tip_chord` 12.0 -> 11.4, status `derived-unsourced`. The value is scaled off the 1/5 drawing by
    its printed rudder widths, so it is not a source.
  - These move the analytic NP and the accuracy report. Every moved test gets a row in
    `docs/geometry-correction-ledger.md`. No physics bound is widened, and strict xfails stay strict.
  - The VSPAERO leg is re-run with the new geometry if openvsp can be run on any node. Otherwise its stored
    result is labelled stale, and the two-method check stays a strict xfail citing that.
- **Wing weight, not settled by the book.** `wing_weight_lb` is 85.0 and unsourced. CP26 p3 gives 64 lb per
  wing with winglets and rudder (N26MS), so 128 lb for both, but that is one builder's airplane. Kept as a
  conflict, with both values named in a provenance-style note and in TODOS. Ledger closure decides.
- The model's single electrical mass row (25 lb at FS 119.5, unsourced) is recorded as wrong in shape: the
  battery is in the nose and the starter and alternator are at FS 150+. It is fixed in the ledger closure
  (2.n), not here.
- `engine_cg_arm_in` 8.0, labelled "forward of firewall", contradicts every source; the engine is aft of
  FS 125. The `engine_mass_kg` 113 (249 lb) vs `engine_dry_weight_lb` 243 mismatch gets a provenance flag.
  Fixing the values is ledger closure.
- Chapter 23 ops cover only what the chapter prints. One op, `f23.engine-install`, stands for the absent
  Section II installation; its text says so, and its engine solid is striped representational.
- The op YAML is written by a Claude (Sonnet) crew from the research, not by the smithy lane: in M2.7, 19 of
  27 smithy drafts needed substantive fixes. Recorded in the lane log.

## 4. What the owner sees

- Strakes built on the jig table: ribs and baffles, sump blister, fuel gauge, tank sealing, then skins and
  the LE fairings. Tank volume is shaded, and the readout carries the capacity conflict as text.
- The nose battery shelf with the battery, the relays on F22, the wire runs (representational), lights and
  antenna.
- The engine block, striped "(fitted shape; installation in Section II, not held)", plus the throttle and
  mixture bracket, the cowl trim, and the wing-root metal rib.
- Readout reference rows: the N26MS empty-weight ladder (693.4 to 883 lb), mount 5.2 lb, cowl 18 / 12 lb.
  The OM sample empty 730 lb at 111.7 is shown as the closure target. CG stays "not yet computed".

## 5. How it is built

Same lanes as M2.7.

- **Crew A** (Sonnet), in order:
  - Task 0: the analysis fold-ins and the exit-test relabel (section 3), with ledger rows.
  - Task 1: config and provenance for chapters 21-23, plus the ledger reference rows.
  - Task 2: the graph (ch21, ch22, ch23).
  - Task 3: geometry (`core/strake_book.py`, `core/electrical_book.py`, `core/engine_book.py`) and the glb
    export.
  - `/conduct` for shape-constrained kernels where useful (strake outline stations, tank volume).
- **Crew B** (Sonnet): the lab, with per-op shots and e2e.
- **Captain:** the Opus visual review, the full `remote_test_all`, `guide.check`, the leak scan, the grade, and
  a message to the lead before any push.

## 6. Done when

- Chapters 21 to 23 rehearse in WebKit, and all representational parts are striped.
- The capacity and battery-station uncertainties are shown as text.
- The analysis fold-ins are landed with ledger rows, and the exit-test target is corrected.
- The gates are green and the visual review has passed. The milestone is pushed only after the lead's go,
  checked with ls-remote, then deployed and republished.

## 7. Out of scope

Sections IIA, IIC and IIL (not held). The ledger closure itself (2.n). Chapters 24 to 26 (M2.9).
