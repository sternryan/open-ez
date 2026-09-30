# Block 2 milestone 2.2: the fuselage box (chapters 4–6)

Status: the lead approved this under the owner's delegation, 2026-09-30.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Engine:
`docs/superpowers/specs/2026-09-30-block2-m21b-lab-engine-design.md`.

## 1. Intent

The rehearsal moves from the canard to the airplane. Chapters 4–6 (bulkheads, sides, assembly)
become lab operations. The model gets a fuselage built from the book, replacing the unsourced
elliptical placeholder. Every part says whether it is book-true, derived or representational.

## 2. Evidence (research 2026-09-30, read from page images)

- **Book-true (dimensioned on pages the owner holds, plans-1980 p33–p38):**
  - the fuselage side panels: 103 in long, the 12 printed heights, top at W.L. 23, plus bulkhead
    positions, the sight-gauge depression and the spar cutout;
  - the front and rear seat bulkheads: outline, tapers, holes and notches (the rear top width is
    not printed);
  - F28's offset from F22 (5.9 in);
  - the longeron sections;
  - the gear pad;
  - the jig.
- **Derived stations** (arithmetic from printed side-panel coordinates, with the side front edge at
  FS 22):
  - F22 at FS 22 and F28 at FS 27.65;
  - the panel at FS 39.75 (the Owner's Manual says 40; this is flagged as a conflict);
  - the front seat bulkhead from FS 63.6 (bottom) to 81.75 (top);
  - the rear seat bulkhead from FS 107 to 118.5 (118.5 is the spar's forward face, p88);
  - the side's aft end at FS 125, which is the firewall line on p101 and matches `fs_firewall`.
  - Cross-checks: the computed bulkhead slants match the printed widths within about 1 in, and the
    front bulkhead width (23) matches the manual's front cockpit width.
- **Template-only (full-size A1–A5, A7 and A8, which the owner does not hold):**
  - the instrument panel, F22, F28 and firewall outlines;
  - longeron placement;
  - the gear-extrusion positions.

  These are modelled as representational shapes fitted to the side profile, flagged in the model
  and in the lab, and never presented as book.
- **Plans changes.** 22 Canard Pusher entries touch chapters 4–6, for example CP29 LPC 70 (the side
  UND runs at ±30°, not ±45°), CP25 LPC 20 (the gear pad stops at W.L. 12.35) and CP34 LPC 105 (BID
  over the F28 doublers). The operations apply them, linked as in M1.

## 3. What the owner sees

- **Chapter operations** in the lab op bar, in build order, with the parallelism the book allows
  (chapter 4's seat bulkheads can run alongside its panel and firewall work).
- **The build:**
  - the side panels are cut from foam blanks on the table and glassed;
  - the bulkheads are made;
  - then the jig: the sides go upside down on levelled blocks, the bulkheads bond in, in the book's
    order, the bottom foam is fitted, carved and glassed;
  - plies lay down with the lab's animation, as on the canard.
- **Section cut** along the fuselage (a station plane), with the readout listing the layers there.
- **Fidelity is visible.** Representational parts carry the lab's "unverified" treatment (a hatch
  or stripe on surfaces and caps) and their label says so.
- **CG control.** Once the box exists, the readout panel gains a CG row built from the ledger: the
  empty-structure CG so far where masses are sourced, and "not yet computed" otherwise. This is the
  first step toward the roadmap's CG knob.
- The canard chapters keep working unchanged.

## 4. How it is built

- **Graph.** New `guide/graph/ch04.yaml`, `ch05.yaml` and `ch06.yaml`. Operations and checklists
  are in the owner's words and pass `guide.check`. They are linked to CP LPCs, with cross-chapter
  prerequisites.
- **Geometry.**
  - A new book fuselage (`core/fuselage_book.py`) builds the sides from the printed heights, the
    seat bulkheads from their printed outlines, and representational F22, F28, the panel and the
    firewall, fitted to the side profile at their stations.
  - Each solid carries a fidelity tag: `book`, `derived` or `representational`.
  - Config gains the derived bulkhead stations, with `GEOMETRY_PROVENANCE` entries citing
    `plans-1980:p36` and the arithmetic.
  - `fs_pilot_seat` and `fs_rear_seat` are occupant CG arms (om-1980). They stay as arms and are
    renamed where that doesn't break the physics. They are never treated as bulkhead stations.
- **Placeholder retired.** The elliptical `Fuselage` is replaced. The strict-xfail assembly test is
  re-evaluated: if it now runs on book geometry, its xfail is removed. Otherwise the reason is
  updated honestly.
- **Plies and materials.** Each operation's `materials` feed the lab's ply animation, and feed
  per-part ply areas for the ledger (areas and ply counts only).
- **Areal weights.** To put masses in the ledger, the glass styles and foam densities named in the
  plans' bill of materials (ch 2) are sourced from manufacturer datasheets and registered. Where a
  value can't be sourced, the mass stays "not yet computed".
- **Lab.** A glb export of the fuselage parts plus layup, the scene grown to hold the fuselage jig
  and the canard, camera shots per operation, the station cut, and the representational material
  treatment.

## 5. Done when

- Chapters 4–6 are rehearsable in the lab on the iPad, including the book-order bulkhead bonding in
  the jig.
- Every fuselage solid has a fidelity tag. Book and derived values cite pages, and representational
  parts are visibly marked in the lab.
- The placeholder fuselage is gone, and the assembly test's status is truthful.
- The ledger has per-part ply areas for the fuselage, plus masses wherever the areal weights are
  sourced.
- The gates are green on the two-node fan-out plus the local render tests. The owner walks it.

## 6. Out of scope

- Chapters 7 onward.
- Ledger closure on empty weight, which needs all chapters.
- Load paths for the fuselage (added once Block 3 has load cases).
