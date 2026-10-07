# Block 2 milestone 2.5 (chapters 14-17): captain log

Captain: Sonnet 5.5 (brief: Sonnet crews only, op YAML drafted by a Sonnet crew, /conduct for eligible one-file
kernels). Start: main at 56cf300. Spec
`docs/superpowers/specs/2026-10-01-block2-m25-spar-firewall-controls-trim-design.md`, evidence
`docs/harness/m25-ch14-17-research.md`.

## Page reads (captain, on the page images, before anything enters the model)

Pages rendered at 130 dpi from the owner's scan into the scratchpad; never committed. Read: p85, p86, p87 (rendered),
p88, p90, p100, p101, p106.

- **p88 confirmed in full.** Forward face FS 118.5, aft face FS 125 at the centreline, kink at BL 23.0, 6.50 chord, 8.57
  deg, forward face 33.834 and aft face 32.865 outboard of the kink, 6.43 square-to-face, 28.82 between hard points,
  FS 123.54 at BL 56.46, FS 129.9 at BL 55.5 (hand digits, both check against the sweep: 125 + 0.1506 x 32.5 = 129.89),
  depth 8.50 (WL 22.0 to 13.5), WL 20.25 at BL 25.0, WL 20.5 and 16.3 at BL 53.5, bottom WL 15.15 and top WL 22.0 with a
  21.7 label at the outboard end, BL 9 tick on the bottom. No change to the research.
- **p86 confirmed.** Top cap ply ends BL 15, 20, 25, 30, 35, 40, 45, 50, 55.5 (four full plies, then eight tapered, which
  matches strip lengths 100..30); bottom BL 13, 20, 27, 34, 41, 48, 55.5 (three full, six tapered, strips 96..26).
  Cap thickness about 0.450 and 0.150 (top), 0.338 and 0.113 (bottom). Spruce blocks at BL +/-7.5.
- **p90 confirmed.** LWA1 2 x 1.5 x 1/8 (6), LWA2 2 x 2.5 x 1/8 (4), LWA3 2 x 6.4 x 1/8 (4), LWA4 2 x 1.5 x 1/4 (8),
  LWA5 2 x 2 x 1/4 (2); CS1 7.94 at BL 23, 8.41 at the centreline, 6.83 at the ends; end bulkheads 6.30 x 6.83. CP43
  LPC 119 enlarges LWA4 and LWA5 (1.75 and 2.25 tall); the CP-corrected sizes are used and the printed ones are noted.
- **p85 hand label "29.84"** sits in the LWA placement sketch between the outboard LWA4 and the inboard LWA5, next to
  a "1.0" outboard setback. 29.84 - 28.82 = 1.02, so it plausibly includes the 1.0 setback, but the sketch does not
  say. Not used. Hard-point spacing stays 28.82 (p88, checks). Bottom cap is three full strips (the 1677 total only
  closes with three); cobelu's four rejected.
- **p100 stick pivot planes.** "F.S. 45.5" is lettered at the CS109/CS108 end of the front pivot tube, with a leader to
  the vertical plate; "F.S. 89.7" has its leader at the vertical edge by CS117/CS118. Both legible, both medium (the
  leader targets are plates, not dimension lines). Kept as 45.5 and 89.7 with the stated confidence.
- **p101 firewall.** FS 125 line, torque-tube hole at BL 6.2R, WL 12.3 (both views). The right-hand WL scale reads
  W.L.-15/-14/-11/-10/-9; the leading dash is a tick leader (the left view uses trailing dashes the same way), so the
  research's "not negative" stands. The belcrank height is still tick-read only: representational.
- **p106 trim handle.** Panel FS 40; dimension 9.5 from the panel to the handle's aft lobe; the label beside the lobe
  reads "F.S. 49.8". 40 + 9.5 = 49.5. The dimension is the book number; the 49.8 label is carried as a flagged
  disagreement of 0.3 in, nothing is moved to it. Pivot WL 8.6 with 14.4 to the top of the longeron (23 - 14.4 = 8.6
  checks), lower bolt WL 7.1 (1.5 below). Cable swages 5.6 and 6.2 from the panel sleeve.

## Review Focus (each pinned by a test; test names are added to the report)

1. **Spar planform.** Values come from p88 only; the "7 in spar" note is corrected; no attach-bolt FS is invented
   (unsourced until ch19). Pin: config and provenance tests, ledger row test.
2. **Representational shown as book.** Every new solid has a fidelity tag with a valid citation; trough templates
   (A11), firewall outline (A4), consoles, stick fore-aft positions, master cylinders, brackets and the pitch stops are
   representational and striped. Pin: tag-completeness tests, lab e2e.
3. **Roncz travel leaking GU or manual numbers.** The controls kinematics use only the Roncz row (15 up, 12.5 floor,
   30 down); 20/22 never appear. Pin: kinematics test, lab e2e.
4. **Spar mass.** 29.3 lb (CP26 prototype, BID layup) is the one sourced row; UND saving is `derived` and a note; no CG
   or empty weight is invented. Pin: ledger tests, readout e2e.
5. **Firewall bond order.** `f06.bond-firewall` moves after `f14.fit-fuselage` as a `cp-hint` change; chapters 4-9 lab
   and tour assertions are unchanged or each change is named. Pin: graph test, diff of the e2e file against 56cf300.
6. **No double counting.** Plywood stays in `f04.firewall-aft`; stainless and insulation only in
   `f15.stainless-firewall`. Pin: graph test.
7. **Honest dependency stubs.** `f16.aileron-linkage` and `f16.rudder-cable-rig` require `c19.wings` / `c20.winglets`
   stubs. Pin: graph test.
8. **Visible change at every op, nothing inside another solid unless labelled, no label contradicting the state**
   (the M2.4 review's defects). Pin: pixel e2e on each new op, `_legible` label checks, phone-width checks.
9. **Public hygiene.** No hostnames, IPs, home or scan paths, plans quotes. Pin: leakcheck and existing hygiene tests.

## Lane log (call, lane, reason)

- local-model op-YAML lane skipped for ch14-17 (spec section 5 ruling): in M2.4 all 7 drafts needed hand fixes; a Sonnet crew
  drafts the YAML directly.
