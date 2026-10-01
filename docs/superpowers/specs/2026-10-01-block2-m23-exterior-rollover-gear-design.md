# Block 2 milestone 2.3: exterior, roll-over and main gear (chapters 7–9)

Status: the lead approved this under the owner's delegation, 2026-10-01.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.2,
`docs/superpowers/specs/2026-09-30-block2-m22-fuselage-design.md`.
Evidence: `docs/harness/m23-ch7-9-research.md`, read from page images.

## 1. Intent

The fuselage box gets its outer skins, roll-over structure, seat-belt and harness attachments, and
main landing gear. The lab rehearses the book's distinctive moves:
- glassing each side with the fuselage jigged at 45° of bank;
- positioning the gear legs against a datum board at the spar's aft face.

The mass ledger gains its first sourced landing-gear row, and the model's unsourced gear lump goes.

## 2. Evidence summary

- **Book-true:**
  - the skin schedule and laps, and the sight gauge, which matches M2.2;
  - the roll-over box: 23 wide (equal to the front bulkhead), the printed walls and sides, sides
    13 after CP26 LPC 37, and the insert spacing 4.0 after CP27 LPC 52;
  - belt and harness attachments, and the step;
  - the **main axle at FS 110.5**: 15 in forward of the spar's aft face at FS 125.5 (p50), the
    back-cover 3-view agrees (p171), and the Owner's Manual says 110.5 ±1;
  - axle height W.L. −22 (p171);
  - toe-in of 0.2–0.45 in over 24 in;
  - the main strut at 22 lb (p50 and the p8 parts list) and the nose strut at 2.8 lb (p8);
  - the 12° tip-back line from the main contact (p171).
- **Template-only or unprinted:**
  - the canard cutout outline (A3), though its floor is at W.L. 18.9;
  - the extrusion placement (A5);
  - the strut mold, so **the track has no source** and the lateral tip-over check stays blocked;
  - wheel, brake and tire weights.
- **Conflicts:**
  - The model's `landing_gear_arm_in` 84.5 and `landing_gear_weight_lb` 45 are an unsourced lump
    of main and nose gear. They are replaced by sourced rows: the main strut is 22 lb at FS 110.5,
    the nose strut is 2.8 lb at FS 17 to 20 (the printed nose-wheel station is FS 17, against the
    manual's "about 20", flagged as a conflict), and wheels and brakes are flagged unsourced.
  - The spar aft face at FS 125.5 versus `fs_firewall` 125 is recorded.
- **Plans changes:** 17 Canard Pusher entries, applied as in M2.2.

## 3. What the owner sees

- **Chapter 7:**
  - the box's corners are carved round;
  - the canard cutout is made (a fitted outline, hatched);
  - the fuselage rolls to 45° left bank and the right skin is glassed, then rolls to 45° right
    bank for the left skin (animated in the jig);
  - peel ply goes on the strake bond areas.
- **Chapter 8:** the roll-over box is built on the front seat back, inside glass, bonded, outside
  glass with its local buildups, then access holes, harness and belt attachments, and the step.
- **Chapter 9:**
  - the gear strut is stiffened (8 UND);
  - the fuselage is inverted and levelled on its top longerons;
  - the jig blocks and datum board go in, and the leg is set with the axle at FS 110.5;
  - the tabs and pads are laid up;
  - axles, brakes and toe-in follow;
  - the strut and extrusions are representational (striped and labelled), while the axle position
    is book.
- **The readout's CG row** uses the new ledger rows (main strut 22 lb at FS 110.5). The CG stays
  "not yet computed" while other rows are unsourced, but the lower-bound line now includes the
  gear.
- **A ground-handling note** in the readout states the book's main-axle station and its 12°
  tip-back line. The CG-height check needed to grade tip-back is "not yet computed" (no CG height
  source). It is never invented.

## 4. How it is built

- Graph files `ch07.yaml`, `ch08.yaml` and `ch09.yaml`, in the owner's words, with prerequisites
  back into chapters 4–6 and CP links.
- Geometry:
  - `core/fuselage_book.py` grows the skins (as plies over the box, with the third-ply strip from
    FS 60 to 110), the roll-over box, the inserts and the step.
  - A new `core/landing_gear_book.py`: the axle point at FS 110.5, W.L. −22 (book); the strut and
    extrusions (representational); the jig blocks and datum board (book dimensions).
  - The config gains `fs_main_axle`, `wl_main_axle`, `fs_spar_aft_face` and `fs_nose_wheel`
    (conflict), each with provenance.
- Ledger and config: decompose the gear lump into sourced and unsourced rows; remove
  `landing_gear_arm_in` and `landing_gear_weight_lb`, or derive them from the rows. Any physics
  test that moves gets ledger discipline, with no loosened tolerance.
- Lab:
  - the 45° bank rolls and the inversion, run on sim time;
  - representational striping for the gear;
  - per-op camera shots;
  - station cuts through the skins and roll-over;
  - a chapter 7–9 tour, and a film of the chapter 9 gear positioning.

## 5. Done when

- Chapters 7–9 are rehearsable on the iPad, including the 45° bank skinning and the gear set to
  FS 110.5.
- The gear lump is gone; sourced rows are in, and unsourced ones are flagged.
- Every new solid has a fidelity tag, and representational parts are marked in the lab.
- The gates are green, and the owner walks it.

## 6. Out of scope

- The nose gear (ch 13).
- The spar (ch 14).
- The landing brake (Section VI or ch 24).
- The lateral tip-over check, until a track source exists.
