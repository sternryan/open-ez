# Proposal: a parametric O-235 engine module with a sourced mass-properties table

Crew R, round 2, 2026-10-05. Draft for the captain. No code written. Inputs are in `2n-engine-inventory.md` (sources) and `2n-engine-research.md` (round 1).

## 1. Recommendation up front

Build it, but sell it for what it can honestly deliver:

- **Layout and envelope for the lab and the GLB**: yes, representational, fitted to what the whole-engine data allows.
- **Component masses**: only the accessories (starter, alternator, magnetos), the mount and the cowl have a public weight. The crankcase, crankshaft, cylinders, sump, accessory housing, carburettor, exhaust and baffles have none. They can only be a **residual**: TCDS dry weight minus the sourced accessories, shared out by geometry. That is a model, not a measurement, and every row says so.
- **The whole-engine numbers (243 lb, CG 14.75 in from the flange) stay the truth.** The module is a decomposition that must reproduce them, not a competing source. It must not move the frozen 2.n closure row.

Existing code: `core/engine_book.py` already builds a single representational block, a bracket, a cowl and two ribs. The module replaces the block only. Put the new code in `core/engine_o235_book.py` (new file, so the book-fidelity chapter 23 geometry stays untouched) and let `build_engine()` call it for the `block` part.

## 2. Frame and parameters

Same frame as `core.fuselage_book`: x = F.S. (aft positive), y = B.L., z = `z_of_wl`. The engine axis runs along x, pitched by `DOWN_THRUST_DEG` (2 deg, CP38 p5). The engine CG offset from the flange runs **toward the crankcase, which is forward on a pusher**: CG_FS = flange_FS - 14.75. (Round 1 flagged this direction; the closure row already applies it.)

Parameters, each a `config.geometry` field with a `GEOMETRY_PROVENANCE` entry (flags per AGENTS.md):

| Parameter | Value | Flag | Source or reason |
|---|---|---|---|
| `eng_o235_flange_fs` | 155.8 | derived | cp-text:p28 hub forward face 158.8 less the 3 in extension; the same arithmetic as the closure row. The hub-versus-flange offset beyond the extension is unconfirmed |
| `eng_o235_cg_from_flange_in` | 14.75 | book | tcds-e223:p7 NOTE 8 (14.51 for E/G/M/P) |
| `eng_o235_cg_below_cl_in` | 1.13 | book | tcds-e223:p7 |
| `eng_o235_cg_left_in` | 0.20 | book | tcds-e223:p7 |
| `eng_o235_bore_in`, `_stroke_in` | 4.375, 3.875 | book | tcds-e223:p1 |
| `eng_o235_displacement_ci` | 233 | book | tcds-e223:p1; the config carries 235, flag as a conflict |
| `eng_o235_dry_lb` | 243 (band 236 to 247) | derived | tcds-e223:p7, same figure as the closure row |
| `eng_o235_oil_station_fs` | 140 | book | om-1980:p25; a placement check, not an input |
| `eng_o235_cyl_pitch_in` | fitted | representational | no public dimension; chosen so the four cylinders span the crankcase |
| `eng_o235_case_len_in`, `_width_in`, `_height_in` | fitted | representational | no public dimension; the existing `eng_book_block_in` is the starting point |
| `eng_o235_mount_pad_xy` (four dynafocal pads) | fitted | representational | Section IIL not held; one builder's top cups at FS 134.2 (grade C) is a plausibility check only |
| `eng_o235_flange_diam_in` | fitted | representational | AS-127 flange size not retrieved |

Fitted values live as `FITTED_*` constants in the module, like `fuselage_book`, and never enter `GEOMETRY_PROVENANCE` as book.

## 3. Geometry (CadQuery)

One function per component, each returning a `cq.Workplane` in engine axes, then placed once by the pitch and flange transform:

- crankcase (two half boxes split on the centreline), oil sump below it, accessory housing aft of it;
- four cylinders: barrel plus head, two per bank, sized from bore and a fitted barrel length; centred at the cylinder pitch;
- crankshaft stub and prop flange disc at x = 0 (the datum), pointing aft on the airplane;
- accessories as simple primitives: starter and alternator at the aft end (station 150 and aft, CP27 p4), two magnetos upper rear, carburettor on the sump bottom pad, fuel pump on the rear left pad;
- exhaust and baffles as optional envelopes, off by default because they are not in the TCDS dry weight;
- four mount pads as small cylinders on the dynafocal ring, for the lab to show the mount interface.

Each part is a `FusePart` with fidelity `representational` and the cite tuple of the nearest source. `FIDELITIES_USED` stays `{"representational"}`. Nothing is labelled `book` except values that are TCDS printed numbers.

## 4. Mass-properties table

Every row: mass, cite, provenance flag, and a position derived from the geometry in section 3 (volume centroid of the placed solid, never a typed number).

| Component | Mass rule | Cite | Flag |
|---|---|---|---|
| Starter | 17 lb (band 16.7 to 17.2) | cp-text:p49 | derived |
| Alternator or generator | 7 lb (band 4.25 to 9) | cp-text:p49, cp-text:p26 | derived |
| Magnetos, two | 2 x 3.75 lb Slick, or 2 x 6.25 lb for TCM; use the type named by the dash number | tcds-e223:p7, vendor page | derived |
| Accessory sum | about 31 lb whole stripped-to-standard budget cross-check | cp-text:p10 | derived (check only) |
| Core (crankcase, crankshaft, cylinders, sump, accessory housing, carburettor, fuel pump) | residual = dry weight less the three sourced accessory rows, shared by solid volume times a fixed material density per part (aluminium or steel), densities from handbook values | tcds-e223:p7 | representational |
| Mount, dynafocal | 5.19 lb | cp-text:p26 | builder; outside the engine dry weight, shown separately |
| Cowl | 18 lb glass | cp-text:p27 | builder; outside the engine |
| Exhaust, baffles | none, excluded | none | unsourced |

Output: `engine_mass_properties(variant="C1C")` returning total mass, the CG in published FS, BL, WL, and the per-component table, with flags. The residual means the table's mass sum equals the dry weight by construction; section 5 explains why that alone proves nothing.

## 5. Acceptance test

Two parts, and only the second can fail for a real reason.

1. **Weight (bookkeeping, not evidence).** Component sum equals `eng_o235_dry_lb` to 0.5 lb (the printed integer rounding), and each sourced accessory sits inside its published band. This catches a wrong subtraction, nothing more.
2. **CG (the real test).** The CG of the placed components, with layout parameters and densities **frozen before the test is run**, must match the TCDS CG measured from the flange:
   - longitudinal 14.75 in, tolerance **+-0.5 in**;
   - vertical 1.13 in below the shaft centreline, tolerance **+-0.3 in**;
   - lateral 0.20 in left, tolerance **+-0.25 in**.

Why these tolerances. The TCDS prints the longitudinal CG to 0.01 in but the dash-number groups differ by 0.24 in (14.75 against 14.51), and the newsletter cross-check is "about 15 in" (CP54 p6), a 0.25 in rounding. A uniform-density decomposition of an engine with unpublished cylinder and case dimensions cannot honestly resolve better than about twice the group spread, so 0.5 in. Vertical and lateral offsets are small numbers (1.13 and 0.20 in); 0.3 and 0.25 in are about a quarter of the first and more than the whole second, which is the most the layout can be trusted to. These bands are set from the sources' own spread, not from how the model happens to land. If the model misses them it is left failing as a strict `xfail` with a ledger row, per AGENTS.md ("a physics bound that the book geometry fails is left failing").

Caveat the test must state: if the fitted layout parameters are tuned until the CG passes, the test becomes a calibration and proves nothing. The record shows the layout parameters as fixed inputs, set from engine proportions before the check, and any later tuning is a ledger event.

Break-it check (AGENTS: a gate counts only after it fails on a bad input): flip the CG direction (flange plus 14.75 instead of minus) and assert the test goes red; swap a magneto weight for the heavy type and assert the residual and CG move beyond tolerance or the band check trips.

## 6. How it plugs in

- **Closure engine row.** `data/mass_ledger.yaml` row `engine` (243 lb, arm FS 141.05, band 140.8 to 141.3) is frozen by content hash (ledger row 65). The module does not change it. It adds a cross-test: the module's total mass equals the row weight, and its CG FS lies inside `arm_band_fs`. A mismatch fails the test; it never edits the row. A change to the row needs a new ledger row.
- **Mount and cowl rows.** The module reports the dynafocal mount (5.19 lb) and cowl but the closure rows own them; no double count.
- **Electrical double-count.** The module exposes whether the starter and alternator are inside the engine mass (they are, by the TCDS heading), so the closure's "electrical" row stays nominal 0 as already noted.
- **GLB and lab export.** `build_engine()` returns `dict[str, FusePart]`; the new parts register as `engine.crankcase`, `engine.cyl1` and so on, grouped under the existing `engine.*` aliases, striped as `representational` in the lab. The mass table exports as JSON next to the parts for lab tooltips. I did not read the GLB exporter, so the one thing to confirm before building is how the lab lists part ids (the `engine.rib` alias group in `engine_book.py` suggests an id-to-names map).
- **Sources.** Register `tcds-e223` (done), plus `lyc-om-o235` (Operator's Manual 60297-9) and `tcds-e252` for the O-200 variant, and cite cp-text pages 26, 27, 28, 49, 54 as existing `cp-text:pN` ids.

## 7. Tasks and sizes

| # | Task | Size | Blocks |
|---|---|---|---|
| 1 | Register `lyc-om-o235`, `tcds-e252` in `data/sources/registry.yaml`; add the cp-text pages cited | S | none |
| 2 | Add `eng_o235_*` fields and provenance entries; fix the displacement 235 versus 233 flag | S | 1 |
| 3 | `core/engine_o235_book.py`: component geometry, placement, `FusePart` map | M | 2 |
| 4 | Mass-properties function: sourced accessories, residual core, per-component CG | M | 3 |
| 5 | Tests: weight bookkeeping, CG against TCDS with frozen parameters, the two break-it checks | S | 4 |
| 6 | Closure cross-test against the frozen engine row (read only) | S | 4 |
| 7 | Wire into `build_engine()`, lab striping, mass-table JSON for the lab | M | 3, 4 |
| 8 | O-200 variant (190 lb, CG 4.6 in forward of the rear face of the mounting lugs; different datum, needs a pad plane) | M | 4; optional |
| 9 | Ledger row and docs entry for the module and its tolerances | S | 5, 6 |

Total about two medium and several small tasks. Tasks 3 to 5 are the work; the rest is bookkeeping.

## 8. What stays unsourced after all of this

- Any dimension of the engine: length, case size, cylinder pitch, flange size, pad positions. No public dimensioned drawing exists (inventory section 4).
- Every core component mass, and the carburettor, fuel pump, exhaust and baffles. The residual is a modelling choice.
- The standoff from the firewall to the mount pads (Section IIL pp 14 to 15, not held).
- Which starter and alternator the TCDS dry weight actually includes (it says starter and generator, no weights).
- The prop-hub-to-flange offset beyond the 3 in extension.
- No CAD model is usable (inventory section 5), so layout proportions come from the operator manual's description and the TCDS numbers only.

Honest summary for the ledger: after this module the engine row stays exactly as frozen; the module adds a visible, falsifiable CG check and a lab model, and states plainly that component masses are modelled, not published.
