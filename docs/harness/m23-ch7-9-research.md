# Fuselage chapters 7–9: source research (2026-09-30)

A read-only research pass. Every cited value was read on the page images, not the OCR.
Paraphrases are ten words or fewer. The captain re-verifies any value that goes into the model.

Page map: `plans-1980` p45–46 are ch7 pages 7-1 and 7-2, p47–49 are 8-1 to 8-3, and p50–53 are
9-1 to 9-4. The page map lists only p45 (7-1). The printed page numbers on the images fix the
rest. p44 is 6-6, the last page of chapter 6. p171 is the back cover with the three-view. Ch7
has no A-sheet dependence beyond the canard cutout, and ch9 has no strut-mold geometry in hand.

## Operations (ids `f0N.<slug>`; all require `c03.layup-skills`)

| Op | Requires | What happens |
|---|---|---|
| `f07.carve-corners` | `f06.bottom-tape` | Sand the corners round, long block parallel to longerons. Keep the lower aft corner high at the gear bolts. |
| `f07.canard-cutout` | `f06.bond-bulkheads`, `f06.f28-install` | Cut the full-size pattern, remove the longeron forward of F28, trim the F22 tab above WL 18.9 (CP27 LPC 46, 50). |
| `f07.fuel-gauge-area` | `f07.carve-corners` | Mark and sand the sight-gauge depression, remove the grey tape. Micro foam chips into the bolt holes. Round the plywood firewall edge 1/8 in. Trim Fiberfrax back 1/2 in where skin laps. |
| `f07.belt-insert` | `f06.bottom-foam-fit` | Left side only: remove bottom foam, micro a small wood insert into the lower corner. |
| `f07.skin-right` | the four above, `f05.gear-extrusions` | Jig the fuselage at 45° left bank, glass the right side. |
| `f07.skin-left` | `f07.skin-right` | Roll to 45° right bank, glass the left side. Peel-ply the strake bond areas. |
| `f08.roll-over-foam` | `f04.front-seat-bkhd-back` | Cut 0.35 in R45 PV pieces, trial-fit on the seat back, chamfer. |
| `f08.roll-over-inside` | `f08.roll-over-foam` | Cut three plywood inserts, flush with the inside faces. 1 BID inside, cure, trim. |
| `f08.roll-over-bond` | `f08.roll-over-inside`, `f07.skin-left` | Micro-bond the box to the seat back and sides. Sand the cured skins first. |
| `f08.roll-over-outside` | `f08.roll-over-bond` | Radius the peak. 2 BID outside, 12 plies local over each insert, +3 plies over the peak. |
| `f08.access-holes` | `f08.roll-over-outside`, after cure | Map-case slot on the right side only. Small baggage hole in the rear only. |
| `f08.shoulder-harness` | `f08.roll-over-outside` | Drill 1/4, bolt the front harness. The aft harness bolts to the spar tabs (ch14, later). |
| `f08.belt-attach` | `f07.belt-insert`, `f07.skin-left` | Four places: rough plywood insert in wet flox, 7 BID, drill 1/4, bolt the 2 in angle. |
| `f08.step` | `f08.belt-attach` | Bend the aluminium step, drill four 1/4 csk holes, mount it. |
| `f09.strut-stiffen` | none beyond skills | Sand dull, glue on 3 nails, epoxy coat, 8 plies UND at 30–40°. Do it before tabs and axles. |
| `f09.jig-blocks` | `f05.gear-extrusions` | Make four plywood blocks, bevel to a sharp edge, bolt the tubes between the angles. |
| `f09.position-gear` | `f09.jig-blocks`, `f09.strut-stiffen` | Invert and level on the top longerons. Centre the leg and set the axle 15 in forward of the datum. Bondo, scribe tube marks, remove. |
| `f09.tab-layup` | `f09.position-gear` | Wet out and clamp the UND and BID pads on each tab. Trim flush, bore 5/8 through. |
| `f09.tab-assembly` | `f09.tab-layup` | Reinsert the tubes at the scribe marks, flox fillets, UND and BID pads in the corners. 2 BID wrap over a foam block, washers, plugs. |
| `f09.axles-brakes` | `f09.tab-assembly` | Plates, toe-in set with squares, 3 BID each face, four bolts per axle, calipers. |
| `f09.brake-lines` | `f09.axles-brakes`, `f04.firewall-fwd` | Nylaflow up the trailing edge, 1 BID tape, #10 firewall hole, pot with RTV. |

Cross-chapter notes:
- The landing-brake text points to Section VI. CP26 LPC 35 and CP28 point to page 24-1. The p7-2
  "chapter 17" reference is stale, because ch17 is pitch trim (p105).
- The gear datum (p9-1) is a straight board at the spar's aft face. Whether the spar is installed
  is unclear, since ch14 comes later.
- Hard dependence of f09 is on the ch5 extrusions. Ordering after f07 is book sequence, not
  physical need.

## Materials (ch30.yaml `materials` shape)

**Ch7:**
- `{cloth: UND, plies: 2, where: "crossed 30 deg to longerons, whole skin"}`
- `{cloth: UND, plies: 1, where: "forward of front seat bulkhead only, along longerons"}`
- `{cloth: UND, plies: 3, where: "3 in strip, 52/50/48 in tapered, FS 60 to 110"}`
- Stock: 0.85 gal epoxy, 14 yd UND (p2 list via the cobelu transcription; scan p9 not re-read for
  these rows).

**Ch8:**
- `{cloth: BID, plies: 1, where: "inside faces"}`
- `{cloth: BID, plies: 2, where: "outside skin, 1 in overlap onto seat back and sides"}`
- `{cloth: BID, plies: 2, where: "local reinforcement"}`
- `{cloth: BID, plies: 12, where: "buildup over each of 3 inserts"}`
- `{cloth: BID, plies: 3, where: "over the peak"}`
- `{cloth: BID, plies: 2, where: "over the shoulder-harness pads"}`
- `{cloth: BID, plies: 7, where: "each of 4 belt-attach pads"}`
- Stock: 0.35 in R45 PV foam, 3 plywood inserts 1.25×1.25×1/4.
- Hardware: 6 AN525-416R16, 2 AN509-416R18, 2 AN509-416R14 (read as R14 on p8-3), 4 AN4-5A,
  2 AN4-10A.

**Ch9:**
- `{cloth: UND, plies: 8, where: "gear strut at 30-40 deg, 4 each face"}`
- `{cloth: UND, plies: 18, where: "per attach tab, pad 2.5 x 12 in, 4 tabs"}`
- `{cloth: BID, plies: 18, where: "per tab, 2.5 x 3.5 over leading edge"}`
- `{cloth: BID, plies: 18, where: "per tab, 2.5 x 2.5 pad"}`
- `{cloth: BID, plies: 2, where: "45 deg wrap round each tube"}`
- `{cloth: BID, plies: 2, where: "over each washer"}`
- `{cloth: BID, plies: 3, where: "inside and outside of lower leg at axle"}`
- `{cloth: BID, plies: 1, where: "45 deg tape over the brake line, 1 in lap"}`
- Hardware: 8 AN4-22A, 4 more AN960-1016 (CP30 LPC 83 gives 1016, not the printed 1018).
- Stock: 4130N tubes 5/8 OD ×0.049 ×6.75, 4 plugs, 0.063 2024T3 squares 2.5×2.5, 3/16 Nylaflow
  about 72 in each side.
- The 72/72/72 cut counts equal 18 per tab times 4. The figure 5 stack labels are ambiguous, so
  use the counts.

## Geometry (`plans-1980:p<pdf page>`)

| Item | Value | Citation | Status |
|---|---|---|---|
| Sight gauge | 21 in to firewall (FS 104), 9.15 down, 2.5 wide section | plans-1980:p46 | dimensioned; matches model x=82 |
| Skin lap | 1/2 in onto firewall over 6.5 in; 2 in bottom overlap | plans-1980:p46 | dimensioned |
| 3rd-ply strip span | 50 in ending 15 in forward of FS 125 (FS 60–110) | plans-1980:p46 | dimensioned |
| Lower-corner insert | 5 in long, 32.7 in from the forward edge | plans-1980:p46 | 32.7 is dimensioned from the left edge; reading it as an FS is mine |
| Canard cutout floor | WL 18.9 | plans-1980:p45 | dimensioned; outline on A3 (template only) |
| Roll-over front wall | 23 wide, 4 high, 8.4 top flat, 7.3 each shoulder, 12.6 peak, 0.7×1.4 notches | plans-1980:p47 | dimensioned; 7.3+8.4+7.3 = 23 checks |
| Roll-over sides | 12.7 long, 3 and 4.5 ends; small piece 6.9×2.7; triangle 8.1×12.7 | plans-1980:p47 | dimensioned; sides become 13 (LPC 37) |
| Harness insert / canopy-cable insert | 1.25×1.25×1/4; 4.0 spacing; 1.5 and 1.25 from the peak | plans-1980:p47, p48 | dimensioned (4.5 became 4.0, LPC 52) |
| Map slot / baggage hole | slot 1.8×8 right side; 3/4 dia rear | plans-1980:p48 | dimensioned |
| Belt attach | belts 5 in forward of and 8 in between the seat bulkheads | plans-1980:p49 | hand-sketched, approximate |
| Step | 1.8×4.5×4.5, 0.5 min bend radius | plans-1980:p49 | dimensioned |
| Main axle station | FS 110.5, 15 in forward of FS 125.5 | plans-1980:p50 | dimensioned; arithmetic checks |
| Axle height | WL -22 | plans-1980:p171 | read on image |
| Jig block | 1/4 ply, 1 in radius, 5/8 hole, bevel 0.8, 0.65 in tube showing | plans-1980:p50, p53 | dimensioned |
| Gear tube | 4130N 5/8 OD ×0.049 ×6.75; plug 0.526/0.625/1.0 | plans-1980:p53 | dimensioned |
| Gear tabs | pads 2.5×12, 2.5×3.5, 2.5×2.5 | plans-1980:p51, p53 | dimensioned |
| Extrusions | 1/4×2×2 6061-T6, 3/8 holes, 1.1 edge, 3/4 lightening | plans-1980:p52 | full-size outline, hand digits ok |
| Toe-in | B minus A = 0.2 to 0.45 over 24 in squares | plans-1980:p52 | dimensioned |
| Gear strut mold | none printed | plans-1980:p50 | prefab, not dimensioned |

Hand-digit notes:
- The p8-1 digits (7.3, 12.6, 12.7, 6.9, 2.7) are clear.
- The "22" in "22 lb" on p9-1 has a print overstrike. The 22 lb is confirmed on p8 (the 2-1
  parts list).
- The 40° in the p9-1 overview is bold, while the body says 30–40°.

## Landing gear for the CG and ground-handling checks

- **Main wheel station:** FS 110.5, set as 125.5 minus 15 (plans-1980:p50). The back cover also
  prints FS 110.5 at the axle (plans-1980:p171). Owner's Manual p34 says FS 110.5 ±1. CP32 says
  hold the axle within 1/2 in.
- **Axle height:** WL -22 (plans-1980:p171). The nose wheel is also at WL -22 after CP25 LPC 24.
  The hand correction reads "-23" in the note and "-22" in the figure, so the digit is ambiguous.
  The printed nose-wheel station is FS 17, against "about 20" in the manual (p34) and 19.6 in
  its sample.
- **Tip-back:** the back cover draws a 12° line from the main contact (plans-1980:p171).
- **Track:** not printed on pp 7–9 or the back cover. It is fixed by the molded strut and the A5
  sheet, which the owner does not hold. Leave it representational or unsourced rather than
  measuring it off the image. A lateral tip-over check is blocked until a track source is found.
- **Toe-in:** 0.2–0.45 in total over 24 in, equal to about 1/4–1/2° per side (my arithmetic).
  The manual also says 0.25–0.5° per side (p31).
- **Weights:**
  - Main strut is 22 lb (plans-1980:p50 text, and the p8 list as MG-1L). The nose strut is
    2.8 lb (plans-1980:p8, NG-1L).
  - The wheels, brakes, tires and axles have no printed weight. The manual gives about 750 lb
    empty (p4), and the ledger sample uses 730.
  - Tires are 3.40×5 on the scan (p6, p9). The cobelu transcription has a 3.50 typo in one
    place.

## Canard Pusher changes

| Issue | Change |
|---|---|
| CP25 LPC 24 | nose gear CL at WL -22 (hand note on p171) |
| CP26 LPC 34 | LMGA belongs to ch5 |
| CP26 LPC 35 | page 9-1 landing brake: add "and other important landing brake details" |
| CP26 LPC 37 | roll-over sides 13, not 12.7 |
| CP27 LPC 45 (OPT) | extrusion 3/8 holes up 0.4 in (gear up 0.4 in, no station change) |
| CP27 LPC 46 (OPT) | F28 longeron notch lowered 0.25 in |
| CP27 LPC 50 | p7-1 section A-A inaccurate; use A2 |
| CP27 LPC 52 | roll-over 4.5 becomes 4.0, harness insert moves outboard 1/2 in |
| CP27 p5 hint | use Weatherhead #2030X4 tube for the Nylaflow end |
| CP30 LPC 75 | axle bolt location sketch; 1/16 in strut-to-caliper clearance is mandatory |
| CP30 LPC 83 | AN960-1016, six total, not 1018 |
| CP30 LPC 80, 85 | A5 reference is p9-3 |
| CP30 hint | set toe-in against a tight centreline wire; B−A halves 0.1–0.2 |
| CP31 LPC 89 | brake line runs round the inboard face of the strut |
| CP32 hint | axle station within 1/2 in; toe-in 1/4–1/2° |
| CP36 LPC 112 | "Chapter 8" on p9-1 becomes Chapter 14 |
| CP48 LPC 127 / CP69 | inspect nylon brake lines (mandatory ground item) |

## Conflicts

- **Gear arm:** `landing_gear_arm_in` is 84.5 and `landing_gear_weight_lb` is 45. Both are
  unsourced, and the arm is a lump of main and nose. The book has main at FS 110.5, nose near
  17–20, strut 22 lb and nose strut 2.8 lb. The wheels and brakes weight is unknown. Decompose
  the row; do not keep 84.5.
- **Spar aft face:** FS 125.5 against `fs_firewall` 125. That is plausible, and it implies a 7 in
  spar from the p88 forward face at 118.5.
- **Fuselage:** `core/fuselage_book.py` has nothing from ch7–9. The sight gauge matches. The
  roll-over front wall's 23 in width equals the front bulkhead's 23 in.
- **Internal to the plans:**
  - The aft harness bolt is AN4-6A on p8-2, but the parts list shows AN4-5A.
  - The p7-2 "chapter 17" landing-brake reference is stale.
  - The p9-1 overview says 40° and the body says 30–40°.

## Judgement

**Book-true from pages the owner holds:**
- the skin schedule and laps, and the sight gauge;
- the whole roll-over box and belt-attach set;
- the main axle station and height, the toe-in limits, and the gear weight.

**Template-only or unprinted:**
- the canard cutout outline (A3);
- the extrusion placement on the fuselage (A5);
- the strut mold, so the track and the strut CG have no source.

**Mass ledger:** a 22 lb strut at FS 110.5 is the only sourced gear row. Everything else in the
gear lump stays unsourced until someone supplies it.
