# Block 2 milestone 2.6: canopy (chapter 18)

Status: the captain approved this under the owner's delegation, 2026-10-03.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.5,
`docs/superpowers/specs/2026-10-01-block2-m25-spar-firewall-controls-trim-design.md`.
Evidence: `docs/harness/m26-ch18-research.md`, read from page images. The captain re-read p111 and
p112 on the images: rear cut at FS 117, pad stations, pad length 2.5 in, hinges on the right.

## 1. Intent

The plexiglass bubble is trimmed and set on the fuselage, and a foam and glass frame is built
around it in place. The frame is then cut free, which leaves the front and rear covers on the
fuselage. The inside is carved and the hinge and latch pads are glassed. Last come the vent,
the brace tubes, the right-hand hinges, the left-hand latches, the door and the safety catch.
After this milestone the fuselage is closed on top, and the ledger gains a sourced canopy
weight.

## 2. Evidence summary (model-bound values)

- **Book, high confidence:**
  - Rear cut at FS 117: 8 in forward of the firewall. Three checks agree: p111, CP27 LPC 43,
    and the safety-catch arithmetic.
  - Plexiglass 68 in long, trimmed with 0.5 and 0.75 in offsets.
  - Five-ply frame: sides 2 BID + 2 UND, front and rear 3 BID, all BID at 45 degrees. Foam
    carved 0.06 in low.
  - Eight pads, each 2.5 in long. Stations are measured forward from FS 117 to the pad's aft
    edge:
    - left: 11, 41, 59 and 71 (the 59 pad is the safety catch);
    - right: 20, 25.5, 48 and 53.5 (hinge pads).
  - Each pad takes 15 BID plies plus flox.
  - Safety catch SC-1 at FS 56.75.
  - Door 4.3 x 3.7 in, on the left.
  - Checks A (at least 13.5 in) and B (12.3 in) above WL 23.
- **Derived, medium confidence:**
  - Hinge spans FS 89-97 and FS 61-69.
  - Latch pad centres 104.75, 74.75 and 44.75. The p117 labels say 104, 74 and 44, so that
    0.75 in disagreement is carried as a flagged conflict.
  - Front cut about FS 41.65 at the longeron. Its datum is unnamed, so it is representational.
- **Representational:**
  - the bubble contour and the outer frame surface (the bubble is a vendor part with no
    section);
  - the front and rear cover profiles;
  - the vent teardrop, the latch linkage geometry and the door position;
  - the canopy opening arc.
- **Mass:**
  - Canopy 16 lb ready to finish: CP26 p3, N26MS (Melvill), a builder weight, not the
    prototype.
  - 17 lb with hinges, filled and painted: CP27 p1, same airplane.
  - Both are reference rows, like the spar. They do not enter the CG. There is no sourced
    split between the bubble, the frame and the hardware.

## 3. Rulings

- Rear cut FS 117 is book. The front cut is representational at about FS 41.65, labelled as
  having an unnamed datum.
- The latch-pad conflict (derived 104.75, 74.75, 44.75 against the printed 104, 74, 44) is
  carried as a conflict pair, in the same way as the nose wheel. The lab shows the derived
  centres and names the printed labels.
- The ledger gets the canopy as a reference row in `prototype_weights` (the key name is kept
  for historical reasons, and its rows are builder weights): `canopy`, 16.0 lb, cited
  `cp-text:p26`, with a note giving N26MS, page 3, and the 17 lb painted figure from CP27 p1.
  It enters no sum.
- Fuselage 183 lb (CP26) already includes the front and rear canopy frames. Nothing is
  double counted.
- No wood inserts under the pads: that detail comes from Solitaire SPC 20, not the Long-EZ.
- Op order follows the plans, except that `f18.door` comes before `f18.latches` (p115 says so).
  `f18.front-cover` is done while the canopy is off.

## 4. What the owner sees

- The bubble is trimmed on the bench, then set on its blocks on the longerons.
- The A and B checks are drawn as dimension lines above WL 23.
- The foam frame grows around the bubble and is carved. The five plies are laid with the
  animated lay-down: the groove ply first, then the plies over the top.
- The hacksaw cuts happen at the front and rear. The covers stay on the fuselage, and the
  canopy lifts off and turns upside down on the bench.
- Inside carving and the eight pads are coloured by role: hinge, latch and catch.
- The canopy hinges open on the right, at about 15 degrees past vertical. The latches, the door
  and the safety catch are on the left.
- Readout: the canopy reference row ("Canopy (CP26 builder weight, N26MS): 16.0 lb, reference,
  not in CG"). CG stays "not yet computed".
- Every representational part is striped and labelled "(fitted shape)".

## 5. How it is built

- Graph: `guide/graph/ch18.yaml`. A Sonnet crew drafts the ops in the owner's words from
  research section 4, and they must pass `guide.check`. The local-model op-YAML lane is skipped
  for the same reason as in M2.5.
- Config and provenance: the canopy stations (rear cut, pad stations, SC-1, door size, checks A
  and B) go into `config/aircraft_config.py`, each with a `GEOMETRY_PROVENANCE` entry and a
  citation. The ledger reference row is added.
- Geometry: `core/canopy_book.py`.
  - The bubble is a representational loft built from the frame constraints in research
    section 5.
  - The frame is a band around the bubble's footprint on the longerons.
  - The pads are placed at the book stations, with the hinges on the right and the latches,
    door and catch on the left.
  - Front and rear covers are representational.
  - The open pose (a hinge axis on the right longeron) is computed in a small kernel. If it is
    eligible, it is built with `/conduct` on local-model lane; otherwise a crew does it.
- Lab: a Sonnet crew, using the M2.5 pattern: per-op shots, pixel e2e checks for each op,
  the open/close animation, and the ch18 tour.

## 6. Done when

- Chapter 18 can be rehearsed in WebKit, including the canopy opening on its right-hand hinges.
- Every new solid has a fidelity tag and representational parts are striped. The latch conflict
  and the front-cut datum are visible, never shown as bare facts.
- The canopy reference row is in the readout.
- The gates are green and the captain's visual review has passed. The milestone is graded,
  pushed (checked with ls-remote), deployed and republished.

## 7. Out of scope

Wings and winglets (M2.7); electrical and avionics; and any change to the plexiglass shape
from the book.
