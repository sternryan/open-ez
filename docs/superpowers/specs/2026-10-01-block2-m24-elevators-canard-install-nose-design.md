# Block 2 milestone 2.4: elevators, canard installation, nose and nose gear (chapters 11–13)

Status: the lead approved this under the owner's delegation, 2026-10-01.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.3,
`docs/superpowers/specs/2026-10-01-block2-m23-exterior-rollover-gear-design.md`.
Evidence: `docs/harness/m24-ch11-13-research.md`, read from page images. Lane plan:
`docs/harness/vision-bakeoff-2026-10-01.md`.

## 1. Intent

The canard meets the fuselage. The Roncz elevators are built and hung (the `r30.elevators` stub
becomes real ops), the canard is pinned and bolted to F22, and the nose is built forward of F22:
nose-gear box, floor, side and top blocks, rudder pedals, retracting nose gear, pitot and static,
nose skin and door. After this milestone the airplane is modelled from the nose tip to the
firewall.

## 2. Evidence summary

- **Chapter 11 means the Roncz elevators.** The airplane uses the Roncz canard, and the cobelu
  chapter 30 transcription replaces chapters 10–12 for it. The 1980 chapter 11 pages are GU
  reference only (settled 2026-09-30). The elevator numbers come from the cobelu text and
  figures (the `cobelu` registry id), not from the owner's scan:
  - lengths right 55.7, left 72.7 (stock 57 and 74, the 1.3 trim agrees);
  - travel 15° up target (12.5° floor), 30° down;
  - hinge slot gap about 0.2; hinge offset 0.55 aft of the tube leading edge;
  - 1 in OD tube; pins trimmed to 36 right and 61 left;
  - CS-11 lead 2 × 0.6 × 0.8; CS-10 inboard face 7.5 from the elevator end; pocket clearance 0.06.
  - Hinge BLs 9.2/34.1/59 have low confidence at the tip (59 vs 57.0 on C-1): render the hinges
    as positioned-from-text with that flag, never as verified.
  - Contours (templates G, H, I, J, E, M) are template-only: the elevator section is
    representational.
- **Chapter 12:** the existing `r30.install-pins` and `r30.align-canard` cover pins, sweep,
  incidence and shims. Added: drilling F22 through the tabs, elevator-to-fuselage clearance
  (1/16 in, 0.1 round the tubes), CNL bushings (5/8 × 1/4), and the F28 pins flox'd in. Incidence
  is zero to the top longerons (template G). The control-rod connection is chapter 16 (reference
  op only).
- **Chapter 13, book-true from the scan:** the build order and ply schedules; NG6 2.75 wide with
  the bore 1.25 up; NG7 2.75 long; NG30 plates 0.2 thick, 3.0 apart; NG3 bolt to NG7 6.71 ± 0.05;
  strut pivot to pivot 25.5 (medium); floor block 20.9 × 8.2 × 1.6; side block 21.9 long,
  15.6 high at F22; top block 19.3 long, 19.6 and 7.0 wide; pedal block 6.1 from NG30; static
  port 8 forward of the panel at W.L. 13; nose tip FS −6.8 (p171, medium on the last digit); nose
  wheel W.L. −22.
- **Template-only, so representational:** the NG30 outline and NG6 hole position (A6/A7), the
  strut rake, fork offset and trail, the NG31 and F6 outlines, and the nose outline between the
  printed block sizes.
- **The nose-wheel station stays a conflict.** p171 prints FS 17; the manual's weigh procedure
  says about 20 (sample 19.6). The chapter 13 numbers put NG31 at about FS 0–1, but the axle's
  station depends on the unprinted NG6 position and fork offset, which span both candidates.
  `fs_nose_wheel` stays `conflict`; the ledger carries both arms and the readout says so. What
  would settle it is an A6/A7 sheet or a nose-down weigh-in, both owner-held.
- **Weights:** NG-1L 2.8 lb (p8; CP23 says 2.6, recorded). CP26 p2 prototype weights for F22
  1.44, F28 0.19 and the panel 2.13 lb become ledger rows (`cp-*` source, "prototype" note). GU
  elevator weights are not used for the Roncz; the manual's 3.9/3.6 lb ceilings become a check
  bound, not a mass. Everything else in the nose and elevators is `unsourced`.
  The CP26 "complete fuselage 183 lb" is recorded for the Block 2 ledger-closure test (2.n), not
  used here.
- **Plans changes:** 13 CP entries, applied as in M2.3 (CP25 LPC 23 R100 NG31, LPC 24 W.L. −22,
  LPC 27 shock strut optional, CP30 LPC 86 pedal tab, LPC 87 NG17 wall, the mandatory elevator
  inspections as notes).

## 3. What the owner sees

- **Elevators:** the tube held airborne in its jigs while the cores go on, the ±30° skins, the
  hinges slotted into the canard's trailing edge at a 0.2 gap, the up-travel check with an angle
  readout (15° target, 12.5° floor), the hang test (nose falls down), the lead weights and their
  pockets. Elevator sections are striped as fitted shapes.
- **Canard install:** the canard lowers onto the fuselage at the ch7 cutout, F22 is drilled
  through the tabs, the bushings go in, and the elevators clear the fuselage sides. The canard
  becomes part of the fuselage assembly in the lab (the canard and fuselage scenes join).
- **Nose:** the nose-gear box built on the bench and mounted to F22, then floor, side and top
  blocks, pedals, the gear retracting into its slot (animated crank), pitot and static, the nose
  carved and glassed, and the door cut. Representational parts are striped and labelled.
- **Readout:** the nose-wheel arm row shows both candidates (17 and 20) with "conflict"; the CG
  stays "not yet computed" while unsourced rows remain, and the lower bound gains the sourced
  rows. The ground-handling note adds the nose-wheel W.L. −22.

## 4. How it is built

- Graph: ch30.yaml gains the `r30.elev-*`, `r30.canard-tips` and ch12-gap ops, with the stub
  `r30.elevators` replaced by `r30.elev-cs11` (or kept as an alias that requires it); new
  `ch13.yaml` with the `f13.*` ops. Owner's words; `guide.check` overlap gate. Op YAML is drafted
  by the smithy `local-anvil` lane from the research notes and reviewed once by a Sonnet crew.
- Geometry:
  - `core/elevators_book.py`: tube, hinge points, lead weights, travel limits; section
    representational.
  - `core/nose_book.py`: NG30 plates, floor, side and top blocks, pedal blocks, NG31 (fitted),
    nose skin to FS −6.8 (fitted between printed block sizes), door.
  - Nose gear in `core/landing_gear_book.py`: pivot on NG30 (representational position), strut
    25.5, axle at W.L. −22, axle station carried as the conflict pair.
  - Config gains `fs_nose_tip` (book, medium), `fs_ng31` (derived range), `wl_static_port`,
    elevator travel limits (Roncz, cobelu), each with provenance. `fs_nose` −45.5
    (converted-unsourced) is reconciled against the book tip: record the move in the ledger.
  - Code with one-file, test-expressible behaviour goes through `/conduct` (tests written first,
    local-anvil writes the bodies). Lab layout and visual work stays with a Claude implementer.
- Ledger and physics: new rows as in §2; any physics test that moves gets a ledger row and no
  loosened tolerance. Two nose arms mean the readout CG, if ever computed, shows a band.
- Lab: canard joins the fuselage; elevator hang and travel animation; nose-gear retraction on sim
  time; per-op shots; station cuts through the nose; a ch11–13 tour; a film of the canard
  lowering onto F22.

## 5. Done when

- Chapters 11–13 are rehearsable on the iPad (WebKit lane green), including the elevator travel
  check, the canard on the fuselage, and the nose gear retracting.
- The model runs from the nose tip to the firewall; every new solid has a fidelity tag;
  representational parts are marked.
- The nose-wheel conflict is visible, not hidden; no value is measured off an undimensioned
  drawing.
- Gates green (two-node suite, local_render, lab unit/typecheck, `guide.check`), Opus visual
  review passed, graded, pushed, deployed, public republished.

## 6. Out of scope

- The spar, firewall hardware, controls and trim (ch 14–17): M2.5.
- The control-rod connection to the elevators (ch 16).
- The gear-down switch and electrical (ch 22).
- Settling the nose-wheel station (owner-held evidence).
