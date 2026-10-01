# Elevators, canard installation, nose and nose gear: source research (2026-09-30)

A read-only research pass for milestone 2.4. Every cited value was read on a page image, not the
OCR. The 1980 plans are cited as `plans-1980:pNNN` (PDF page). The Roncz text and its figures are
the cobelu transcription of chapter 30. Paraphrases are ten words or fewer. The captain
re-verifies any value that goes into the model.

Page map (`plans-1980`, confirmed against the printed page numbers on the images):
- Ch11 GU elevators: p65 is 11-1 (read). p66–p70 are 11-2 to 11-6 by OCR labels only; they were
  not read, because the Roncz text replaces them.
- Ch12: p71 is 12-1 and p72 is 12-2 (both read; p72 says "last page, chap 12").
- Ch13: p73 is 13-1, p74 is 13-2, p75 is 13-3, p76 is 13-4, p77 is 13-5, p78 is 13-6, p79 is 13-7,
  p80 is 13-8, p81 is 13-9, p82 is 13-10, p83 is 13-11 ("last page"). All read.
- p8 (2-1) is the parts list. p171 is the back cover.
- The pages cite "A6/A7" full-size drawings (nose outline, strut position, NG30 outline). The
  owner does not hold the A-sheets, so everything that depends on them is representational.
- The Roncz figures (C-1 to C-4, 30-xx) are in the cobelu transcription. They are not on the
  owner's scan.

## Operations

### Chapter 11 (Roncz path, ids `r30.<slug>`; all require `c03.layup-skills`)

These replace the stub `r30.elevators`. The existing `r30.install-pins` requires it, so the last
op below is the natural stub replacement.

| Op | Requires | What happens |
|---|---|---|
| `r30.elev-nc2-inserts` | none beyond skills | Press five NC-2 inserts into the torque-tube pockets. Drill #30, grease the pin holes, pop-rivet, seal the edges. Deepen the tube slots. |
| `r30.elev-bond-cores` | `r30.elev-nc2-inserts`, `r30.templates-cores` | Sand the tube. Hold it "airborne" on NC-7 jigs in two NC-2s. Micro the cores on, outboard ends flush. |
| `r30.elev-skin-bottom` | `r30.elev-bond-cores` | Fair the cores to templates H and I (bottom flat). Two crossed UND plies at ±30°. Trim the trailing edge, dig out foam for a glass-to-glass closeout. |
| `r30.elev-skin-top` | `r30.elev-skin-bottom` | Two crossed UND plies at ±30°, at least 1/2 in lap onto the bottom skin. Dry micro under peel ply along the trailing edge. |
| `r30.elev-trim-ends` | `r30.elev-skin-top` | Knife-trim and plane the trailing edge straight, check against H and I. Fit NC-6 plugs (#10 hole, #30 hole, pop rivet). Close the outboard end with 1 BID. |
| `r30.elev-hinges` | `r30.elev-trim-ends` | Clear glass over the NC-2s. Pin the NC-3 and NC-3A hinges (oilite bushings, washers) with NC-8 pins. Slip the NC-12A weldments in temporarily. |
| `r30.elev-hinge-slots` | `r30.elev-hinges`, `r30.top-skin`, `r30.hinge-foam` | Canard upside down. Jig each elevator with two L jigs at a uniform 0.2 in slot gap. Mark and rout seven hinge slots with a 1/4 drill. |
| `r30.elev-uptravel-test` | `r30.elev-hinge-slots` | Hot-glue the NC-3s temporarily. Measure up-travel with an angle finder. Shim the NC-3s out until at least 15°. |
| `r30.elev-flox-hinges` | `r30.elev-uptravel-test` | Fill each slot 2/3 with wet flox, sand the buried hinge area, seat the hinges, top up, wipe. |
| `r30.elev-nc12a` | `r30.elev-flox-hinges` | Recess the CS-11 screw heads (100° countersink). Set each NC-12A with the 0.55 in offset, drill #12 through tube and arm. AN3-12A bolt. |
| `r30.elev-balance-check` | `r30.elev-nc12a` | Hang each elevator on its hinge points. It must fall nose down. If not, sand up to half the top UND ply. Up to 0.3 lb may be added forward. |
| `r30.elev-travel-check` | `r30.elev-balance-check` | Remount on the canard. Check with template G: +30° trailing edge down, about 15° up. 12.5° up is the absolute floor. |
| `r30.canard-tips` | `r30.elev-travel-check` | Foam tip blocks micro'd on (1 in above the trailing edge, template M swoop). 2 crossed UND or BID plies each side. Trim hinge pins to 36 in right, 61 in left. |
| `r30.elev-trim-belcrank` | `r30.canard-tips` | Left elevator only. Swap the NC-12A inboard end for the NC-5A belcrank, 12 pop rivets, clear of the pin. |
| `r30.elev-mass-balance` | `r30.elev-trim-belcrank` | Bond foam spacer and CS-10 lead to each elevator's leading edge on the J jig. Two UND strips round it. The inboard side of the weight is 7.5 in from the elevator end. |
| `r30.elev-balance-pockets` | `r30.elev-mass-balance` | Cut a pocket in the canard's bottom skin and foam so the weight clears by 0.06 in. Flox corner and 1 BID inside. Same at the tip rib. |
| `r30.elev-ice-shield` (optional) | `r30.elev-balance-pockets` | Fiberglass fence ahead of each weight, 1.4 × 4 in, over a foam core. Skip unless icing is possible. |
| `r30.elev-cs11` | `r30.elev-balance-check` | CS-11 lead on the left side of each NC-12A (both elevators). Drill two #16 holes, recess the nut side, AN509-10A screws. Replaces stub `r30.elevators`. |

Notes:
- The text calls the second step 11 twice ("test up-travel", then "flox the NC-3s"). I treated
  them as two ops.
- The mass-balance and pocket sections are not numbered in the transcription. Their book order is
  after the belcrank, as listed.
- GU ch11 differs in tube size, hinge parts, layup counts and travel. GU-only reference ids
  `c11.*` stay as they are.

### Chapter 12 (gaps in `r30.install-pins` / `r30.align-canard` only)

The existing ops cover pins, fuselage-side lowering, clamping, sweep, incidence, rear tabs and
shim-to-BID. Missing (cobelu ch30 "Install Canard" steps 4, 7, 8, 9, 10; GU ch12 is the same
except as noted below):

| Op | Requires | What happens |
|---|---|---|
| `r30.f22-drill-tabs` | `r30.align-canard` | Drill #10 through F22 from the tabs' pilot holes. Pass a temporary AN3 through, clamp. This is not explicit in the existing summary. |
| `r30.elev-fuselage-clearance` | `r30.elev-travel-check`, `r30.f22-drill-tabs` | Trim each elevator's inboard end to about 1/16 in from the fuselage side. Keep 0.1 in round the tubes at 15° up and 30° down. |
| `r30.lift-tab-bushings` | `r30.f22-drill-tabs` | Open tabs and F22 to 1/4. Counterbore F22 to 5/8 for the CNL bushings. Leave them untrimmed and unbonded until ch13. CN-2 bushings go in the tab holes earlier. |
| `r30.f28-pins-permanent` | `r30.lift-tab-bushings` | Pull the pins. 1 BID over the marked F28 area with 1/4 flox corners. Drill out #10, flox the pins in. |
| `r30.control-connection` (reference only) | none | Elevator NC-11 to the control rod uses an extra CS-202 spacer. Chapter 16 work. |

### Chapter 13 (ids `f13.<slug>`; all require `c03.layup-skills` plus the listed predecessor)

Book order assumes the canard is already aligned and F22's front-face glass added (ch12 note).
Use `r30.align-canard` for Roncz, or `c12.align-canard` for GU.

| Op | Requires | What happens |
|---|---|---|
| `f13.strut-reinforce` | none beyond skills | Round the NG-1L edges. 1 BID at 45° on three sides, full length. After cure, 1 BID from the fourth side. Trim the strut to fit castings. |
| `f13.worm-drive-bench` | none beyond skills | Build or buy the worm drive, NG3/NG4 brackets, NG8 plates, NG6 assembly, lower fork assembly. Check for binding. Friction damper: wheel pivots at about 5 lb side load. |
| `f13.ng30-plates` | `f13.worm-drive-bench` | Two NG30 plates cut from 0.2 in high-density PV foam. 4 BID inside. Drill five pilot holes. Strip foam to glass at pads, lay BID pads, 4-ply outer skin, open holes to 5/16 and 1/4. |
| `f13.ng-box-assemble` | `f13.ng30-plates`, `f13.strut-reinforce` | Bolt NG6/NG23/NG7/NG8, NG51 plates, NG14 spacers between the plates (3.0 in inside). Strut and NG5 on NG6 in wet flox. Check square and strut centred. |
| `f13.ng3-ng4` | `f13.ng-box-assemble` | Fit NG3 snug with 2–3 dry BID plies. Re-lay wet, flox, clamp. Drill 1/4, rod end. Bolt to NG7 centre must be 6.71 ± 0.05 in. |
| `f13.ng31-f6` | `f13.ng3-ng4`, `r30.align-canard` | NG31 disc, 1 BID on one face. Flox it on the NG30 fronts with tapes. Mount the assembly on F22 with flox and BID tapes, nailed. F6 across the plates, 2 BID at 45°. |
| `f13.floor-blocks` | `f13.ng31-f6` | Carve 2 in urethane floor blocks, dished inboard. Fit level with the floor at F22. 2 BID, 1 in lap onto NG30, NG31, floor. Extra ply on the aft 3 in. |
| `f13.pedal-pivot-blocks` | `f13.floor-blocks` | Drill #10 through NG30 for the pivot bolt. Rivet nutplates on 0.063 plates, 5-min to dark-red foam blocks. Blocks 6.1 in from NG30, butted to F22. |
| `f13.side-pieces` | `f13.pedal-pivot-blocks` | Carve 2 in urethane side blocks to fit. 2 BID inside, mount in wet micro. Pivot blocks wet micro, 4 BID over, holes kept open. |
| `f13.canard-attach-reinforce` | `f13.side-pieces`, `r30.lift-tab-bushings` | 3 BID in the F22 top corner. After cure open the lift holes to 5/8. CNL bushings wet in flox, flush both sides. AN970 bonded to F22 under 1 BID. |
| `f13.rudder-pedals` | `f13.canard-attach-reinforce` | Open the pivot holes and bolt on the left and right pedals with CS13 spacers (clamped tight). Light return spring on a small tab. |
| `f13.lower-gear` | `f13.ng-box-assemble`, `f13.floor-blocks` | Trim the strut end to nest in NG15A at the printed length. Bond wet with flox. Forward door on four screws. |
| `f13.strut-slot-sc` | `f13.lower-gear` | Fuselage upside down. Cut the bottom skin and foam from F22 aft to the wheel cutout so the strut retracts flush. Bond the SC strut cover, 2 BID over bare foam. |
| `f13.nb-box` | `f13.strut-slot-sc` | Tire-clearance check, then bond the NB box with 1 BID tape. Plexiglass window in the panel bulkhead. Aft door on three screws, rounded aft edge. |
| `f13.rig-nose-gear` | `f13.nb-box` | Crank to fully retracted, drill #12 in the universal and NG61. Adjust the LST (or NG10A) rod ends, then shorten one turn. Check down position. Gear-down switch is ch22. |
| `f13.pitot-static` | `f13.side-pieces` | 1/4 5052 tubing, 6 in and 38 in. 1/4 hole in NG31. Long piece through F22 on centreline. Static port in the left side, tube pinched and potted, three 1/16 holes. |
| `f13.top-foam` | `f13.pitot-static` | 2 in green urethane top block, temporarily bonded to sides and NG31 with dabs. |
| `f13.carve-glass-nose` | `f13.top-foam`, `f13.nb-box` | Carve to shape, gear retracted. Gaps filled at the strut front. 2 BID, 1 in lap. 3 BID with 1/4 flox corners round the canard cutout. 4-ply BID bumper flange (45°). |
| `f13.nose-door` | `f13.carve-glass-nose` | 4-BID door over release film. Mark 0.7 in flange. Cut top block off, bare-glass flange, 1 BID inside plus 2 locally. Reflox, 1 in BID strip, ten flush screws and nutplates. |
| `f13.shock-strut` (optional, CP25 LPC 27) | `f13.rig-nose-gear` | Spring assembly in place of NG9/NG10A for rough fields. The cobelu text assumes it is fitted. |

Count: 18 Roncz ch11 ops (one optional), 5 ch12 gap ops (one reference only), 20 ch13 ops (one
optional).

## Materials (ch30.yaml `materials` shape)

**Ch30 elevators (per pair unless stated):**
- `{cloth: UND, plies: 2, where: "elevator bottom skin, crossed at +/-30 deg, each elevator"}`
- `{cloth: UND, plies: 2, where: "elevator top skin, crossed at +/-30 deg, each elevator"}`
- `{cloth: BID, plies: 1, where: "outboard end of each elevator"}`
- `{cloth: UND, plies: 2, where: "strips round each CS-10 spacer and weight"}`
- `{cloth: UND, plies: 2, where: "each canard tip upper surface, crossed (BID allowed)"}`
- `{cloth: UND, plies: 2, where: "each canard tip lower surface, crossed (BID allowed)"}`
- `{cloth: BID, plies: 1, where: "inside each balance-weight pocket, and the tip rib"}`
- `{cloth: BID, plies: 2, where: "each optional ice shield"}`
- Stock: 1 in OD ×0.035 2024-T3 tubes, 57 in and 74 in. 3/16 stainless rod, 61 in ×2. Seven
  hinges (5 NC-3, 2 NC-3A), five NC-2. CS-10 and CS-11 lead, two each.
- Hardware: 17 BSPQ-43 rivets, 2 BSCQ-44, four AN509-10R14 and four AN365C-1032 for CS-11.

**Ch12 gap ops:**
- `{cloth: BID, plies: 1, where: "F28 pin area, 1/4 in flox corners"}`
- Stock: two AN3-20/-20A pin blanks, two CNL, two CN-2.

**Ch13:**
- `{cloth: BID, plies: 1, where: "NG-1L strut, 45 deg, three sides full length"}`
- `{cloth: BID, plies: 1, where: "NG-1L strut, fourth side"}`
- `{cloth: BID, plies: 4, where: "inside face of each NG30 plate"}`
- `{cloth: BID, plies: 15, where: "each NG30 pad over a pivot or bolt hole"}`
- `{cloth: BID, plies: 4, where: "outside skin of each NG30 plate"}`
- `{cloth: BID, plies: 3, where: "dry wrap so NG3 fits snug (2 to 3)"}`
- `{cloth: BID, plies: 1, where: "NG31 disc, one face"}`
- `{cloth: BID, plies: 2, where: "F6 wrap, 45 deg, 1 in overlap onto NG30"}`
- `{cloth: BID, plies: 2, where: "each floor block, 1 in lap up NG30 and NG31"}`
- `{cloth: BID, plies: 1, where: "extra ply on aft 3 in of the floor"}`
- `{cloth: BID, plies: 2, where: "inside of each side piece"}`
- `{cloth: BID, plies: 4, where: "over each rudder pedal pivot block"}`
- `{cloth: BID, plies: 3, where: "F22 top corner over each canard lift hole"}`
- `{cloth: BID, plies: 1, where: "over the AN970 washer on F22"}`
- `{cloth: BID, plies: 2, where: "SC strut cover, over bare foam aft"}`
- `{cloth: BID, plies: 1, where: "NB nose gear box tape, inside"}`
- `{cloth: BID, plies: 2, where: "whole nose skin, 1 in lap onto SC, sides, bottom"}`
- `{cloth: BID, plies: 3, where: "bare foam round the canard cutout"}`
- `{cloth: BID, plies: 4, where: "bumper flange, 45 deg"}`
- `{cloth: BID, plies: 4, where: "door"}`
- `{cloth: BID, plies: 1, where: "inside of top block, plus 2 locally on flanges"}`
- `{cloth: BID, plies: 1, where: "1 in strip over the cut edges"}`
- Foam: 0.2 in dark-red PV (NG30, F6, pivot blocks); NG31 is R100 1/4 red per CP25 LPC 23;
  2 in green urethane (floor, sides, top).
- Hardware, selected: ten AN509-8R8 with K1000-08 nutplates (door). Six rudder-pedal nutplates
  are K1000-3. Pitot is 1/4 5052-0 tube.
- The "15 ply" pad is read from both p77 sections. CP20 p4 mentions 30 plies for NG30 bolt-hole
  circles. This may be both plates cut as one stack. It is unresolved (see Conflicts).

## Geometry (`plans-1980:p<pdf page>`; cobelu figures marked "cobelu")

### Elevators (Roncz, cobelu ch30; the owner holds no scan of it)

| Item | Value | Citation | Status |
|---|---|---|---|
| Elevator lengths | right 55.7, left 72.7 (stock tubes 57 and 74) | cobelu fig C-1 | dimensioned; 57−55.7 = 74−72.7 = 1.3 trim, which agrees |
| Hinge stations | BL 9.2 (left), 7.8 (right, as drawn), 34.1, 59, both sides | cobelu fig 30-33 | dimensioned; C-1 shows 57.0 near the outer CS-10, so the 59 vs 57 relationship is unclear, confidence low |
| Hinge slot gap | about 0.2 in canard trailing edge to elevator top | cobelu ch30 text | dimensioned |
| Hinge pivot offset | 0.55 aft of torque-tube leading edge | cobelu fig 30-46 | dimensioned |
| Travel | 15° up target, 12.5° up floor, +30° down | cobelu ch30 text | dimensioned |
| Tube and pins | 1 in OD tube; pin right 36 in, left 61 in | cobelu ch30 text | dimensioned |
| CS-10 | 2 × 0.8 in section, profile not dimensioned; inboard side 7.5 in from elevator end | cobelu fig 30-53, C-1 | partly template only |
| CS-11 | 2 × 0.6 × 0.8 in lead block | cobelu fig 30-59 | dimensioned |
| Balance pocket clearance | 0.06 in all sides | cobelu ch30 text | dimensioned |
| Ice shield | 1.4 × 4 in, 1.3 high tapering to 0.5 | cobelu ch30 text | dimensioned |
| Canard tip | tip foam 1 in above the trailing edge; shape is template M | cobelu ch30 text | template only |
| Elevator shape (templates H, I, G, J, E) | not printed as numbers | cobelu fig C-3 | template only, A-sheet class |
| GU reference: tubes | 62 and 80 in, 1.25 or 1.5 in OD (digit ambiguous on p65) | plans-1980:p65 | GU only; low confidence |

### Canard on the fuselage

| Item | Value | Citation | Status |
|---|---|---|---|
| Alignment pins | AN3-20 bolt, cut head, round nose, 1.5 in deep holes | plans-1980:p71; cobelu ch30 | dimensioned |
| Pin stick-out | about 1/2 in | plans-1980:p71 | GU text only; Roncz text omits it |
| Rear tabs | GU 2 in wide, 3/4 high, 5 mm dark red foam; Roncz 1/4 ply | plans-1980:p71; cobelu ch30 | the Roncz figure was not located |
| Shim thickness | BID at about 0.013 in per ply | plans-1980:p72 | dimensioned |
| CN-2 bushing | 1/4 OD, 3/16 ID, 0.030 flange, 0.38 long (GU figure) | plans-1980:p72 | dimensioned |
| CNL bushing | 5/8 OD × 1/4 ID, trimmed to F22 thickness | plans-1980:p72 | dimensioned |
| Elevator fit | 1/16 in to fuselage, 0.1 in round tubes | plans-1980:p72; cobelu ch30 | dimensioned |
| Incidence | zero with the top longerons, template G (Roncz). Long-EZ has 0.6° more than a VariEze | plans-1980:p72 (hand note) | dimensioned; the template is an A-sheet |
| Canard cutout floor | WL 18.9 | plans-1980:p171 (via ch7 research) | dimensioned |
| F22 | FS 22 | model, derived | derived |

### Nose and nose gear (chapter 13)

| Item | Value | Citation | Status |
|---|---|---|---|
| Strut pivot to pivot (NG6 to NG15A) | 25.5 in | plans-1980:p81 | dimensioned, read in the "retracted" sketch. Medium confidence: "25.5" has a thin decimal |
| NG6 assembly | width 2.75 ± 0.02; bore centre 1.25 above the base | plans-1980:p73 | dimensioned; CP11 hint and CP10 LPC agree on 1.25 and NG7 2.75 |
| NG7 spacer | 0.5 OD × 5/16 ID × 2.75 long | plans-1980:p73 | dimensioned |
| NG30 plate thickness / gap | 0.2 in foam; 3.0 in inside between plates | plans-1980:p77 | dimensioned |
| NG30 outline | double-tick pattern on A6/A7 | plans-1980:p77 | template only |
| NG30 pad lengths | 2.8 (low confidence) and 1.2 in | plans-1980:p77 | hand-lettered; the decimal in "2.8" is ambiguous |
| NG3 bolt to NG7 centre | 6.71 ± 0.05 in | plans-1980:p78 | dimensioned |
| NG31 outline | half-disc template, no numbers | plans-1980:p78 | template only. The cobelu note gives 5.6 (CL to edge) and 9.2 high, which are not on the scan image |
| F6 | 0.2 in dark red PV, full-size outline | plans-1980:p78 | the cobelu note says 3.2 × 6.7; not on the scan image |
| Floor block | 20.9 long, 8.2 wide, 1.6 thick, 11 in dish, 6.1, 6, 7.35 labels, 5° end bevels | plans-1980:p79 | dimensioned; the 1.6 end vs 8.2 end orientation is my reading, medium |
| Side block | 21.9 long, 15.6 high at F22, 5.5 and 2.8 at the NG31 end, 17° bevel | plans-1980:p79 | dimensioned, medium (hand digits) |
| Pedal pivot block | parallel to NG30 at 6.1 in; X = 3 (2 to 4 adjustment) | plans-1980:p79, p80 | dimensioned |
| Rudder pedal | tube 1/2 OD ×0.035; 7.0, 6.2, 5.75, 0.18 stub, 2.0 tab, 6° offset | plans-1980:p75 | dimensioned |
| Top foam block | 19.3 long, 19.6 aft width, 7.0 forward width | plans-1980:p82 | dimensioned; view is a top view; orientation is my reading, medium |
| Door | 0.7 flange, ten screws; 6.5 and 9.9 along contour, 8.9 wide, 2.0 and 0.7 margins; top piece 7.0 × 8.5 | plans-1980:p83 | dimensioned; dimension lines are loose, low-to-medium |
| Static port | left side, 8 in forward of the panel, 10 in below top longeron (WL 13) | plans-1980:p82 | dimensioned |
| Tubes | pitot 6 in and 38 in, 1/4 OD | plans-1980:p82 | dimensioned |
| Worm drive | NG50 travel 156°, 10.8 crank turns, 5–7 s; NG61 20 in; crank 11.5 in to floor centres | plans-1980:p73, p74 | dimensioned |
| Gear-down position | lower pivot 85–90° to the waterline; canted bottom-forward up to 5° | plans-1980:p73, p81 | dimensioned |
| Nose wheel | 4 in wheel, 2.80/2.50-4 tire | plans-1980:p76; om-1980:p6 | dimensioned; tire OD not printed |
| Fork, NG15A, NG16 | no dimensions for axle offset or trail | plans-1980:p76 | template only |
| Nose tip | FS −6.8 | plans-1980:p171 | read on image, medium (last digit) |
| Nose-wheel centre | FS 17, WL −22 (−25 or −23 struck, −22 written in) | plans-1980:p171 | read on image |

Hand-digit notes:
- The p171 struck-out digit reads as −25 on the image. CP25 LPC 24 says the printed value was −23.
  The corrected −22 is clear.
- On p77, "28 inches" with a faint dot is the only unclear pad label. Medium-low.
- On p83 the dimension line positions mean I cannot say which edge each of 6.5, 9.9 and 8.9 spans.

## Nose-wheel station: arithmetic from the plans

Source claims to reconcile:
- p171 prints FS 17 at the nose-wheel cross-hair. The cross-hair is the axle centre, drawn at WL −22.
- The Owner's Manual (om-1980:p35, corrected from the prior p34) says the nose arm is
  "about" F.S. 20.0. The sample table prints 19.6. Its method is arm = 40 − B, where B is the
  plumb distance from the panel front (FS 40) to the nose axle.
  - The sample implies B = 40 − 19.6 = 20.4.
  - FS 17 would imply B = 40 − 17 = 23.0, a 2.6 in difference.
  - The sample row checks arithmetically: 7.2 × 19.6 = 141.1, printed 141. It is a worked
    example, not a design dimension.

What chapter 13 prints, with FS = F22 FS 22 minus distance forward:
- NG30 butts F22, so the plate back edge is FS 22 (plans-1980:p79).
- Side block length 21.9, so NG31 is at about 22 − 21.9 = 0.1.
- Floor block length 20.9, so NG31 is at about 22 − 20.9 = 1.1.
- Range: NG31 is at about FS 0 to 1. That puts the nose tip (FS −6.8) about 7 to 8 in forward of
  NG31. The block lengths are hand-dimensioned and may not be along the same line, hence a range.
- The NG6 pivot is on NG30, but its position on the plate is only on A6/A7. It is not printed.
- Strut pivot to pivot is 25.5 in. NG6 bore centre is 1.25 above the plate base, and the NG30
  bottom edge lines up with the outside skin (p79).
- With the fuselage bottom at WL 0.9 on p171 (a label read on the image), NG6 is at about
  WL 0.9 + 1.25 = 2.15. Axle at WL −22 is therefore 24.15 below the pivot. (Skin thickness is
  ignored, so this is rough.)
- Axle-to-lower-pivot vertical offset "a" is not printed. The strut's horizontal run is then
  √(25.5² − (24.15 − a)²):
  - a = 0 gives √(650.25 − 583.2) = 8.2 in.
  - a = 2 gives √(650.25 − 490.6) = 12.6 in.
  - a = 4 gives √(650.25 − 406.0) = 15.6 in.
- Axle FS is NG6 FS plus that run plus the fork's fore-aft offset (not printed). With NG6 at
  FS 1 to 4, axle FS can land anywhere from about 9 to 20+ depending on two unprinted fork
  numbers.

Finding: the plans do not resolve the conflict. FS 17 and "about 20" both fit inside the
unprinted fork and pivot dimensions. The 2.6 in gap is far smaller than those unknowns. What
would settle it: the A6/A7 full-size side view (NG6 hole position, fork offset, strut rake), or a
measured nose-down weigh-in per the manual. The model should keep `fs_nose_wheel` flagged
`conflict`. The only plans-printed number is p171's FS 17, and the manual's 20 is an owner-weigh
procedure, not a build dimension. Strut rake is representational until the A-sheet is held.

## Landing gear and mass notes

- **Nose gear height:** WL −22 at the axle centre (p171, CP25 LPC 24).
- **Weights printed:**
  - NG-1L nose strut 2.8 lb S-glass (plans-1980:p8). CP23 p2 gives 2.6 lb for the RAF-made part.
    They differ by 0.2 lb. The scan wins for the model until the part is weighed.
  - F22 bulkhead 1 lb 7 oz (1.44 lb), F28 3 oz, instrument panel 2 lb 2 oz (CP26 p2,
    prototype-built, uncured finish).
  - Canard, no hardware, no elevators: 17 lb. Elevators bare: left 2 lb 2 oz, right 1 lb 13 oz.
    Elevators ready to finish with hinges and counterweights: left 3 lb 8 oz, right 3 lb 4 oz
    (CP26 p2). These are GU-canard numbers. Roncz elevator weights are unsourced.
  - Elevator ceiling with balance installed: 3.9 lb left, 3.6 lb right (om-1980:p30).
  - Complete fuselage including centresection, main and nose gear, brakes, no strakes, canard,
    canopy or engine mount: 183 lb (CP26 p2).
  - Max added balance weight: 0.3 lb (cobelu ch30).
  - CS-11 lead block: 2 × 0.6 × 0.8 in = 0.96 in³. At lead's 0.41 lb/in³ that is about 0.39 lb
    each (my arithmetic, lead density from general reference). CS-10's profile is not dimensioned,
    so its mass is not computed.
- **Unsourced weights:** NG30 box and plates, NG6/NG15A/NG16 castings, worm drive and crank, nose
  wheel and tire, fork assembly, rudder pedals, nose foam, NB box, door. Leave them `unsourced`.
- **Station notes for the ledger:**
  - Panel is FS 39.75 in the model against the manual's FS 40.
  - F22 is FS 22.
  - Nose-wheel arm is conflict, as above.
  - NG31 is about FS 0–1 (range above).
- **CG relevance:** the nose arm (17 versus about 20) moves the nose reaction. The manual's empty CG
  is computed from it, so keep both candidates until the A-sheet or a weigh-in settles it.

## Canard Pusher changes

| Issue | Change |
|---|---|
| CP25 LPC 23 (p13-6) | NG31 foam is R100 1/4 red, not R45 dark blue; F28 can be cut from the panel sheet |
| CP25 LPC 24 (back cover) | nose gear CL at WL −22 |
| CP25 LPC 27 (DES) | spring/shock assembly in place of NG9/NG10A on rough fields; later called the LST |
| CP26 LPC 33 (p11-2) | "2 strips, not 3" in the GU elevator text |
| CP27 LPC 51 (p10-1) | winglet reference should be ch 20 (CP) versus ch 19 (1980 edition) |
| CP30 LPC 76 (p11-5) | detail reference should read page 11-4 (GU) |
| CP30 LPC 79 (p2-4) | SC strut cover listed twice in the ch13 list |
| CP30 LPC 86 (MAN/10 hrs) | reinforce the rudder pedal top tab; change the p13-3 drawing |
| CP30 LPC 87 (p13-4) | NG17 wall 0.188; spring wire 0.083 |
| CP57-8 (mandatory ground list, CP69) | inspect or certify elevator weight, stiffness and shape |
| CP66-9 (mandatory inspection) | check elevator torque tubes for corrosion |
| CP13 hint (VariEze-era) | nose bumper under the NG31 bulkhead, with extra BID |
| CP11 and CP10 hints (VariEze-era) | NG6 is 1.25 and NG7 is 2.75, as p13-1 prints |

No CP entry was found that alters a ch12 dimension. CP27 LPC 46 (F28 notch lowered 0.25) and CP27
LPC 42 (alternate BID/UND on F22 front face) are in the ch7 and ch4 notes.

## Conflicts

- **Nose-wheel station:** FS 17 (p171) against "about 20" and 19.6 (manual p35). Unresolved above.
- **Elevator travel:** GU 20° up and 22° down (plans-1980:p72). Manual 22° ± 2° each way
  (om-1980:p29). Roncz 15° up (12.5° floor) and 30° down. The manual's balance check is 12°–25°
  nose down (om-1980:p30). The Roncz canard needs its own travel row. The model should not take
  the GU or manual angle for a Roncz elevator.
- **Pin lengths and stock:** BOM lists two 61 in pins. The trim step says 36 in right and 61 in
  left. Follow the trim step.
- **Hinge station near the tip:** BL 59 (fig 30-33) against BL 57.0 near the outer CS-10 in C-1.
  They are probably different items, but this is unverified.
- **NG30 pads:** 15 plies per pad on p77 against "30 plies" for bolt-hole circles in a CP20 hint.
  Probably the pair cut together. Unresolved.
- **NG-1L weight:** 2.8 lb (p8) against 2.6 lb (CP23 p2).
- **ch30 cross-references:** the ch30 text cites Figure 30-58 for the F28 holes. The figure is
  30-61. Its sweep check cites Figure 30-60; that is 30-64.
- **Winglet reference (p10-1):** CP27 LPC 51 says chapter 13 should be chapter 20, and the 1980
  edition prints chapter 19. Not a ch11–13 dimension; flagged only.
- **ch30 canard name:** the file is titled R1149MS and the text calls the airfoil R1145MS. The
  repo default is R1145MS.

## Judgement

**Book-true from pages the owner holds:**
- the ch12 pin, bushing and shim procedure and the incidence note;
- the whole ch13 build sequence, BID schedules, NG6 and NG7 dimensions, NG30 spacing, the 6.71 bolt
  distance, floor, side and top block dimensions, door and static port;
- the nose-wheel centre at WL −22 and the p171 FS 17 (as a printed label).

**Roncz (cobelu transcription, not on the scan):**
- every elevator number above. Its figures are public cobelu images. They are not the A-sheets.

**Template-only or unprinted, so representational:**
- NG30 outline and NG6 hole position (A6/A7);
- strut rake, fork and axle offset, wheel trail;
- NG31 and F6 outlines (cobelu's sizes are not on the scan);
- elevator contour templates G, H, I, J, E, M;
- the Roncz rear tab outline.

**Top model-bound values (see the reply):** nose-wheel WL −22, strut 25.5 in, NG30 gap 3.0 in,
NG31 at about FS 0–1, elevator travel 15°/30° with hinge BLs 9.2/34.1/59.

**Mass ledger:** the only sourced rows are NG-1L 2.8 lb, F22 1.44 lb, F28 0.19 lb, panel 2.13 lb
(CP26, prototype), and the elevator ceiling weights from the manual. Everything else in the nose
and elevator groups is `unsourced`.
