# M2.5 geometry inventory and insertion ruling

Status: OE0 inventory with initial OE1 solids, 2026-10-03. This is an implementation inventory, not a
source for dimensions or a fabrication-eligibility statement. Source status remains
in `config/aircraft_config.py`, `guide/graph/components.yaml`, and the cited graph
operations.

## Insertion ruling

`f14.fit-fuselage` is authored and described as **side insertion**. The scanned-plan
research record (`plans-1980:p87`, with the operation recorded in
`docs/harness/m25-ch14-17-research.md`) says to slide the spar in from one side.
CP25's separate firewall-order hint uses rearward wording. It supports keeping the
plywood firewall loose until after the fit; it does not supersede the scanned-plan
insertion direction. The graph therefore records the distinction explicitly. No
geometry provenance status changes as a result.

## Implemented geometry

Every M2.5 component now has representational display geometry (`unvalidated` in
`guide/graph/components.yaml`), at its installed position in the fuselage frame (x = FS, y = BL,
z = WL less the wing plane). Code: `core/spar_book.py` (spar, fittings, jig),
`core/firewall_book.py` (stainless face, belcranks, master cylinders) and
`core/controls_book.py` (consoles, tube, sticks, pushrod, conduits, trim). `guide/export_glb.py`
writes them into the lab glb as nodes named by component id. Placements the book does not print are
`FITTED_` constants with a `# fitted, not book` comment; none is tagged book or derived.

| Components | What exists | Source-limited boundary |
|---|---|---|
| `spar.box`, `spar.cap_top`, `spar.cap_bottom` | Swept box and 12/9 cap bands from the published planform and schedules | Cap-trough profiles from A11 stay unavailable. |
| `spar.bulkheads` | CS5/CS8 end plates and CS6/CS7 at BL 27 | Which CS number takes which side is not read; CS6/CS7 section is a fitted inset. |
| `spar.lwa` | 16 plates on the aft face at the BL 25.0 and 53.5 hard points, CP-corrected sizes | Kind-to-point assignment and stacking are a stand-in; attach bolt FS is unsourced (chapter 19). |
| `spar.spruce_blocks`, `spar.em12`, `spar.sh1` | Blocks at BL 7.5 under and over the caps; four angles aft of the firewall stack; two plates on the spar top | EM12 and SH1 stations are fitted. |
| `spar.jig` | Upright and shelf from the printed widths | Workshop only: its glb node carries `extras.workshop`, and no installed view shows it. |
| `fuselage.firewall_stainless` | Face over the fitted plywood outline, 1 in torque-tube hole at BL 6.2 R, WL 12.3 | A4 outline unavailable; sheet thickness fitted; the plywood is not cut. |
| `firewall.belcrank`, `firewall.master_cylinders` | Plates, bushings and upright cylinders aft of the stainless | Heights are tick-read, cylinder size and stations fitted. |
| `controls.*` | Troughs, tube from the front pivot plane to the firewall, sticks in the FS 45.5 and 89.7 planes, pushrod, conduits at WL 8 | Console positions, grip, pitch stops and the Roncz arm are fitted or unavailable; stick pitch uses the Roncz travel only. |
| `trim.pitch_handle`, `trim.roll_trim` | Handle ending at FS 49.5 (panel 40 + 9.5), pivot WL 8.6, springs at installed length | The p106 49.8 label stays a flagged 0.3 in disagreement; roll-trim stations are fitted. |

Independent review corrected three initial defects: the bottom loft now retains
BL ±9, the planform clips to the square outboard end, and full cap bands stop at
BL ±55.5 rather than the stock strip length. The box is an overlapping display
envelope, not physical foam; cap volumes must not be added to its volume for mass.
The upper WL 21.7 corner interpretation and fitted A11 trough placement remain
unresolved, so all three solids are representational and ineligible for manufacturing.

`core/spar_stock.py` still provides the 16 unplaced LWA blanks (spar-only quantities
6/2/2/4/2) and four spruce blocks; they stay `stock-only`. The installed plates and blocks in
`core/spar_book.py` are separate display solids and are not stock.

## OE1 acceptance boundary

Each component left `no-geometry` with a positive-volume test and a fidelity expectation
(`tests/test_m25_geometry.py`), which assert stations, symmetry and control travel against
literal book numbers. Keep the CP26 builder-weight (N26MS) spar mass distinct from calculated material
mass. These display solids are not STEP/STL candidates merely because a GLB can show
them.

## Verified first-slice baseline

The full local Python suite on 2026-10-03 passed in one process: 1,125 passed,
3 skipped and 9 expected failures. The previously reported mock-related failure
batch did not recur in this run; this is not proof of collection-order independence.
The guide schema gate passed with its overlap gate explicitly not run.
Viewer unit tests passed (50); the lab's normal test command passed (190), including
25 deterministic recorder failure tests, and its type check passed.
Independent review accepted the display/stock boundaries and recorder failure
handling. This does not certify an actual recorded video, hardware fidelity,
source-private overlap checks or manufacturing eligibility. Visual release evidence
for the new solids is still outstanding.
