# Block 3 sizing rule: carbon canard from the book canard

Status: frozen 2026-10-07 in the geometry-correction ledger, row 74 (the M3.4 inputs freeze), before
any carbon number was computed. Changing any line below needs a new ledger row and a new hash.

Spec: `docs/superpowers/specs/2026-10-07-block3-equivalence-engine-design.md` (section 7, M3.4).
Plan: task T11.

## What the rule is for

The rule turns the book canard schedule (`data/laminates/canard_book.yaml`) into a carbon schedule
(`data/laminates/canard_carbon.yaml`) on the same geometry. The equivalence report then compares the
two. The rule is written before any carbon number exists, so that the carbon design cannot be tuned
toward a passing report.

## Priority

1. **Match stiffness first.** At every station, the carbon section's EI and GJ must each be at least
   the book section's.
2. **Then check strength.** Strength is computed on the stiffness-matched design and is never used
   to re-size it. A strength miss at matched stiffness is a finding, reported as such (carbon's lower
   failure strain can cause it).
3. **Then report mass and placement.** Mass, mass centroid and torsional inertia deltas are reported;
   they do not feed back into the sizing.

## Fixed inputs

- **Geometry.** The outer shape, the foam cores, the web position and the cap width are the book's.
  The section geometry is read from `canard_book.yaml` (`geometry:`), never from the legacy
  0.25c/0.10c D-box. The carbon laminate's thickness change is taken up inside the core; the outer
  shape does not move. Where a cap gets thinner or thicker than its trough, that is a Block 4 tooling
  item and is listed, not solved.
- **Material.** Every carbon ply uses `carbon3k_mgs418_wet` (`data/materials.yaml`) and nothing else.
  It is a design proxy: a plain-weave carbon wet-laid in MGS 418, not L285. NCAMP prepreg values
  (`as4_8552`) are never used for sizing. A balanced weave's fill value is NOT copied into its warp
  slot: the warp (1-axis) values stay unsourced until a source supplies them.
- **Book lamina values.** `bid_7725_wet` and `und_7715_wet`, as they stand in `data/materials.yaml`.

## Stations

Sections are evaluated just inboard and just outboard of every printed ply boundary of the book
schedule, and at the ends:

- BL 0;
- BL 10, BL 20 and BL 30, inboard and outboard of each;
- BL 54, the end of the shear web and of the cap troughs.

When a source fixes the cap ply terminations (now unsourced; template page C-3 is not held), each
termination becomes a station pair by the same rule, under a new ledger row.

## The rule, region by region

The regions are the book's. A region the book has is never dropped, and a region the book does not
have is never added.

1. **Keep the orientation family.** Each carbon ply takes the orientation of the book ply it
   replaces: spanwise (0) UND becomes carbon fabric at 0/90; BID at 45 becomes carbon fabric at 45;
   UND at +-45 (the shear web) becomes carbon fabric at 45. One carbon fabric ply at 45 supplies both
   +45 and -45 fibres, so a crossing UND pair maps to carbon at 45.
2. **Keep the extents.** A carbon ply runs over the same BL range as the book ply it replaces.
3. **Minimum one ply.** Every region keeps at least one carbon ply wherever the book has one. This is
   a captain choice (handling and damage tolerance), unsourced.
4. **Torsion first.** At each station, the number of carbon plies at 45 in the skins is the smallest
   integer for which GJ(carbon) is at least GJ(book), with the shear web set by rule 1 and rule 2. If
   the skins alone cannot reach it, the web gets one more 45 ply, then the skins again, alternating,
   until GJ is matched.
5. **Bending second.** With the skins and web fixed, the number of carbon cap plies is the smallest
   integer for which EI(carbon) is at least EI(book). Skin 0/90 plies are one per book spanwise skin
   ply (rule 1) and are not resized; the caps carry the bending match.
6. **Integer plies, matched from above.** Ply counts are integers and every match is from above, so
   the carbon section is at least as stiff as the book at every station. The overshoot is reported.
7. **Spanwise monotonic.** A ply count may not increase outboard. If the station rule gives a larger
   count outboard, the inboard count is raised to it.
8. **Deterministic.** The rule has no free parameter beyond the ones named here. The same inputs give
   the same schedule, byte for byte.

## Thresholds (registered in row 74, unsourced captain choices)

- **Stiffness flag.** An EI or GJ delta above +10 percent of the book value at any station is flagged
  in the report. It is a flag, not a gate: the stiffness band belongs to the outside reviewer
  (spec section 10). No lower flag exists, because rule 6 forbids a carbon section softer than the
  book.
- **Minimum ply count:** one per region (rule 3).

## Out of the rule

- **Pads, lift tabs and hard points** (the CL-1 pads, the PVC hinge inserts): load-introduction
  details, kept as the book's (glass) in the carbon schedule. They are not section properties.
- **Elevators.** The elevator is its own part. It is sized by the same rule on its own section after
  M3.3 has a balance criterion, because its mass balance depends on its skin mass.
- **Canard tips.** Non-structural in the book (the plans say so); kept as the book's.
- **Combined bending and torsion.** Needs an M/T envelope (spec section 1); not used for sizing.

## What happens while inputs are unsourced

Today every book lamina value and the carbon proxy's warp values are unsourced, the cap depth and web
position are unsourced, and the canard chord is a conflict. The rule cannot produce a ply count.
`canard_carbon.yaml` therefore carries the rule's ply structure (regions, orientations, extents) with
every count `null` and flagged, and every M3.4 gate reads `blocked: inputs_unsourced`. When an input
is sourced, its value goes in under a new ledger row with a new hash, and the schedule is regenerated
by script from this rule; the rule itself does not change.
