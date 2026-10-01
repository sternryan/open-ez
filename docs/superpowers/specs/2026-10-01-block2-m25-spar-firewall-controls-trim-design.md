# Block 2 milestone 2.5: centre-section spar, firewall, controls and trim (chapters 14–17)

Status: the lead approved this under the owner's delegation, 2026-10-01.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`. Follows M2.4,
`docs/superpowers/specs/2026-10-01-block2-m24-elevators-canard-install-nose-design.md`.
Evidence: `docs/harness/m25-ch14-17-research.md`, read from page images.

## 1. Intent

The centre-section spar is built in its jig and slid into the fuselage, the firewall gets its
stainless face and the rudder/brake hardware, and the control system is installed: sticks and
torque tubes, the pitch pushrod to the Roncz elevators, rudder conduits and cables, then pitch and
roll trim. After this milestone the fuselage is a closed structure with the wing attach hard points
in place, and the mass ledger gains its heaviest sourced structural row (the spar).

## 2. Evidence summary

- **Spar, book-true (scan, high confidence):** forward face FS 118.5 and aft face FS 125.0 from
  B.L. 0 to 23, swept 8.57° outboard of B.L. 23 (aft face FS 125.57 at B.L. 26.75, agreeing with
  the M2.3 gear datum); span ±56.46; chord 6.50 at the centreline; depth 8.50 (W.L. 13.5 to 22.0);
  wing attach hard points at B.L. 25.0 (W.L. 20.25) and B.L. 53.5 (W.L. 20.5 and 16.3); top cap
  12 plies, bottom cap 9 plies of 3 in UND (three full-span bottom strips, the count that makes the
  printed strip total close; cobelu's four is rejected).
- **Corrections to the model:** the config note "118.5 implies a 7 in spar" is wrong: the spar is
  6.50 deep fore-aft and its centreline aft face is the firewall line FS 125.0; FS 125.5 is the
  swept face at B.L. 26.75. Record in the ledger.
- **CP corrections applied:** LWA4/LWA5 enlarged (CP43 LPC 119); outboard LWA1 setback 0.75
  (CP25 LPC 28); CS119 4.1 (CP26 LPC 29); UND layup options (CP25 LPC 26) noted, BID baseline
  modelled.
- **Firewall and controls:** firewall FS 125; torque-tube bearing hole B.L. 6.2 right, W.L. 12.3;
  stick pivot planes FS 45.5 and 89.7 (medium); rudder conduits at W.L. 8; trim handle pivot
  W.L. 8.6.
- **Roncz differences (cobelu):** elevator travel 15° up / 30° down carried as its own row (the GU
  20/22 and the manual's 22 ± 2 never apply to it); an extra 0.4 in CS-202 spacer; the NC-5A trim
  belcrank at B.L. 9.2 left (not B.L. 0). No pitch stop is printed anywhere: stops are
  representational.
- **Template-only, so representational:** spar-cap trough templates (A11), firewall outline (A4),
  console and stick fore-aft positions beyond the two pivot planes, wing attach bolt FS, master
  cylinder and bracket positions.
- **Mass:** spar 29.3 lb (CP26 prototype weight, BID layup) is the one sourced row. Everything else
  in ch15–17 is `unsourced`; foam/metal/cloth arithmetic is `derived` and labelled as a lower bound.

## 3. Rulings made by the lead

- **Firewall bonding order follows the CP25 builder hint:** the firewall stays unbonded until the
  spar slides in from the rear. If the graph bonds the firewall in chapter 6, the bond moves to
  after `f14.fit-fuselage` and the move is recorded as a `cp-hint` change. Rationale: the plans
  change is the builder-verified order, and the rehearsal should show the order that works.
- **No double counting of the firewall face:** `f04.firewall-aft` keeps the plywood work;
  `f15.stainless-firewall` owns the stainless and insulation (deferred per CP25 LPC 25).
- **New edges into existing ops:** `f09.position-gear` requires `f14.fit-fuselage` (the gear datum
  is the spar aft face) and `f08.shoulder-harness` requires `f14.sh1-tabs`. The chapter 7–9 tour
  and e2e assertions must not change because of this; if they would, keep the edge as a soft
  "uses" link and say why.
- **Ops that need the wing or winglet** (`f16.aileron-linkage`, `f16.rudder-cable-rig`) are
  included as ops that require stubs `c19.wings` / `c20.winglets` (new stubs), so the graph is
  honest about the dependency.

## 4. What the owner sees

- The spar jig with its swept top view, the foam box, the cap troughs carved and the UND caps laid
  in tapering steps (animated ply lay-down like the canard), the hard-point plates, then the spar
  sliding into the fuselage from the side and bonded.
- The firewall with its stainless face and the rudder/brake belcrank and master cylinders
  (representational, striped).
- The control system: sticks moving in their two pivot planes with the torque tube, the pitch
  pushrod driving the Roncz elevators through 15° up and 30° down (stops striped as unprinted),
  rudder conduits to the pedals.
- Trim: the pitch trim handle and springs on the left elevator's belcrank, roll trim on the torque
  tube.
- Readout: the spar's 29.3 lb (prototype) row; CG still "not yet computed"; the lower bound grows.

## 5. How it is built

- Graph: `ch14.yaml` to `ch17.yaml`, owner's words, `guide.check`. Op YAML is drafted by a Sonnet
  crew directly: the M2.4 smithy drafts (7 of 7) all needed hand fixes, so the local lane is
  skipped for this task shape until the model or the prompt preparation changes (log it).
- Geometry: `core/spar_book.py` (planform, depth, caps as plies, hard points, LWA plates),
  firewall face plies in `core/fuselage_book.py`, `core/controls_book.py` (pivot planes, torque
  tube, pushrod kinematics against the elevator travel rows). One-file kernels whose behaviour is
  fully expressed by tests (spar planform maths, pushrod kinematics, cap taper schedule) go
  through `/conduct`; lab work stays with a Sonnet crew.
- Config gains the spar stations, depth, sweep, hard points and the trim/control stations with
  provenance; the "7 in spar" note is corrected; any physics test that moves gets a ledger row.
- Lab: spar jig and cap lay-down, slide-in animation, control-stick kinematics, trim; per-op shots;
  station cuts through the spar; a ch14–17 tour; a film of the spar going into the fuselage.

## 6. Done when

- Chapters 14–17 are rehearsable on the iPad (WebKit lane green), including the spar slide-in and
  the elevator travel driven from the stick.
- The spar row is in the ledger; every new solid has a fidelity tag; representational parts are
  marked; Roncz travel never shows a GU number.
- Gates green, Opus visual review passed, graded, pushed, deployed, public republished.

## 7. Out of scope

- The wings and winglets (ch 19–20): M2.7. The canopy (ch 18): M2.6.
- Electrical, the gear-down switch (ch 22). The engine installation (ch 23).
