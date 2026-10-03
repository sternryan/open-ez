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

## Unfinished geometry

The first OE1 slice has representational (`unvalidated` in the graph) display solids for `spar.box`,
`spar.cap_top`, and `spar.cap_bottom`; their exact implementation is
`core/spar_book.py`. Every other component below remains `no-geometry`. Labels and
fidelity remain authoritative in `guide/graph/components.yaml`; this table makes the
remaining implementation boundary reviewable.

| Components | OE1 representation | Source-limited boundary |
|---|---|---|
| `spar.box` | Implemented swept volumetric box from published stations and sections | Cap-trough profiles from A11 stay unavailable. |
| `spar.cap_top`, `spar.cap_bottom` | Implemented separate 12/9-ply display bands from the published schedules | Trough shape is not inferred from template-only outlines. |
| `spar.bulkheads` | CS5--CS8 volumes from published sections | Not implemented yet. |
| `spar.lwa`, `spar.spruce_blocks`, `spar.em12`, `spar.sh1` | Published-size fittings, blocks, angles and harness plates where placement is supported | Wing-attach bolt FS and unavailable attachment detail remain representational. |
| `spar.jig` | Display-only jig from its published top-view and shelf dimensions | It is workshop/display geometry, excluded from default visualization exports. |
| `fuselage.firewall_stainless` | Stainless face over the existing fitted plywood firewall | The A4 firewall outline is unavailable; no manufacturing claim. |
| `firewall.belcrank`, `firewall.master_cylinders` | Clearly striped representational volumes | Bracket, height and master-cylinder stations are template-only. |
| `controls.consoles`, `controls.sticks`, `controls.torque_tube`, `controls.pitch_pushrod` | Pivot-plane, bearing-hole and kinematic display geometry | Console outline, stick fore/aft placement, Roncz arm and pitch stops are unavailable or fitted. |
| `controls.rudder_conduit` | Conduit path at its sourced WL | Pedal/cable routing beyond available stations remains representational. |
| `trim.pitch_handle`, `trim.roll_trim` | Handle, spring and lever display geometry from available stations | Trim conflict stays visible; unavailable hardware placement is representational. |

Independent review corrected three initial defects: the bottom loft now retains
BL ±9, the planform clips to the square outboard end, and full cap bands stop at
BL ±55.5 rather than the stock strip length. The box is an overlapping display
envelope, not physical foam; cap volumes must not be added to its volume for mass.
The upper WL 21.7 corner interpretation and fitted A11 trough placement remain
unresolved, so all three solids are representational and ineligible for manufacturing.

`core/spar_stock.py` additionally provides 16 unplaced rectangular LWA blanks
(spar-only quantities 6/2/2/4/2) and four unplaced spruce blocks. Stock dimensions
and corrected citations are retained independently of installed geometry. All
blanks declare `stock-only` eligibility; `spar.lwa` and `spar.spruce_blocks` remain
`no-geometry` in the installed graph until their transforms are implemented.

## OE1 acceptance boundary

Before any component leaves `no-geometry`, add a component-specific positive-volume
test and a fidelity expectation. Assert stations, symmetry, cap schedule and control
travel independently. Keep the prototype spar mass distinct from calculated material
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
source-private overlap checks or manufacturing eligibility. Installed spar export,
remaining M2.5 solids and visual release evidence remain unfinished.
