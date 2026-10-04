# Wings (chapter 19, second half): source research B (2026-10-03)

Read-only research pass for milestone 2.7, pages p127 to p134 of the 1980 scan. Every cited value was read on
the page image (hand digits cropped and enlarged 2x), not the OCR. Cites: `plans-1980:pNNN` (PDF page),
`cobelu` (chapter 19 transcription, diffed against the scan; scan wins), `cp-text:CPnn p<page>` (+ LPC number),
`om-1980`. Paraphrases are ten words or fewer. Nothing in the repo was edited. The captain re-verifies any value
that enters the model.

Scope note: p126 (19-10, the wing plan view) and p125 (19-9, aileron text) belong to the other crew member, but I
read both because the aileron geometry on my pages hangs off them; values taken from them are flagged
"(p126, partner scope)".

## 1. Page map (`plans-1980`, confirmed against hand-lettered printed footers)

| PDF | Printed | Content |
|---|---|---|
| p125 | 19-9 | (partner) Step 10 aileron text, step 11 controls text, balance check sketch, build photos |
| p126 | 19-10 | (partner) LPC 2 tie-down note (CP24, handwritten), wing plan view, chords, washout, sweep, BL/FS |
| p127 | 19-11 | Foam block layout and hot-wiring: inboard, center, outboard blocks, planform angles, rib stations |
| p128 | 19-12 | Section A-A (chord section, skins, TE), Section B-B (wing attach fitting, full scale) |
| p129 | 19-13 | Section C-C (inboard attach, 0.6 shell), D-D (spar caps), F-F (root rib 0.7) |
| p130 | 19-14 | Aileron sections I-I, H-H, J-J, K-K, L-L, and E-E (torque tube and phenolic block) |
| p131 | 19-15 | View O-O (top view of aileron belcrank, CS127, CS128, stop bolt), CS128 full-size pattern |
| p132 | 19-16 | View G-G (root bay: belhorn, pushrod, CS127), Section N-N, View M-M |
| p133 | 19-17 | Metal parts: A10, A13, A2, A5, A3, A4, CS150, CS151, CS152, CS132L, LWA6, LWA7 |
| p134 | 19-18 | Step 11 text: wing-to-centersection attach, bolt hole layout, LWA9 bushing, hardware list. "Last page, chap 19" printed |
| p135 | 20-1 | Chapter 20 begins (winglet and rudder). Out of scope |

Chapter 19 is therefore p118 (19-2, per the m26 note) to p134 (19-18). Printed footers on every page 19-11 to 19-18
are legible (rotated hand lettering on p127 to p132, lower right on p133 and p134). The owner holds NO A-sheets:
the templates for the five jig templates (A1 to A8), the aileron and torque-tube hot-wire templates, the rib
templates, A9/A10 (core templates), A12 (rudder conduit curve), and A14 are not in the scan. Shapes that live only
there are marked "repr" below.

Step numbering oddity: p125 numbers the aileron step 10 and the controls step 11, and p134 also numbers the attach
step 11 (two "step 11" in 1980). `cobelu` renumbers controls 11 and attach 12 (plans-1980:p125, p134; cobelu).

## 2. Dimensions, stations, materials, parts, weights

Status key: **book** = printed and cross-checked; **derived** = my arithmetic from printed values;
**repr** = shape not printed or A-sheet only; **text** = process text only.

### 2.1 Foam block layout and hot-wiring (p127, 19-11)

Right wing drawn; left is a mirror (printed caution: reverse everything, watch for forward sweep). Page marked "not
drawn to scale".

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Inboard blocks | two, 7 x 14 x 41 in | plans-1980:p127 | high | cobelu says "two 7 x 14 x 41" | book |
| Center blocks | three, 7 x 14 x 64 in | plans-1980:p127 | high (6 vs 5 in "64": crop clear) | cobelu: five 64s total with outboard 2 | book |
| Outboard blocks | two, 7 x 14 x 64 in | plans-1980:p127 | high | 3 + 2 = five 64s, matches cobelu | book |
| Block stack depth (chord dir) inboard / outboard | 28.0 in (two 14s) | plans-1980:p127 | high | printed on all three | book |
| Block stack depth center | 42.0 in (three 14s) | plans-1980:p127 | high | | book |
| Cut-line offset, inboard / outboard / center | 6.20 / 5.63 / 8.44 in | plans-1980:p127 | high (crops 2x) | derived: 28/tan 77.51 = 6.202; 28/tan 78.64 = 5.625; 42/tan 78.64 = 8.438. All three match | book |
| Planform core angles (acute) | inboard 77.51 deg; center and outboard 78.64 deg | plans-1980:p127 | high | supplement 102.49 / 101.36 printed beside each; sums 180.00 | book |
| Core length along TE, inboard | 33.29 in (printed twice, top and bottom edge) | plans-1980:p127 | high | derived: (55.5 - 23) / cos 12.49 = 33.29 (12.49 from p126, partner scope) | book |
| Core length along TE, center and outboard | 51.76 in (each, printed twice) | plans-1980:p127 | high | derived: (106.25 - 55.5) / cos 11.36 = 51.76; and (157 - 106.25) / cos 11.36 = 51.76 (11.36 from p126, partner scope) | book |
| Sheared offset at block joint | 3.1 in inboard; 2.9 in center and outboard | plans-1980:p127 | high | cobelu does not repeat | book |
| Inboard core LE length after trimming | 32.87 in | plans-1980:p127 | high | cobelu 32.87, "important for attach points" | book |
| Inboard core other check dimensions | 22.8 in and 25.1 in (perp. distance LE to TE at the two ends) | plans-1980:p127 | high | cobelu quotes both | book |
| Rib stations used on cores | BL 23, BL 55.5 (inboard); BL 55.5, BL 106.25 (center); BL 106.25, BL 157 (outboard) | plans-1980:p127 | high | matches p126 section lines | book |
| Outboard blocks | align ribs high to leave foam for winglets | plans-1980:p127 | high | cobelu says same | text |
| BL 23 rib scrap pad | scrap block at BL 23, "parallel with BL 55.5 WL, not necessarily level" (handwritten correction) | plans-1980:p127 | medium (small hand print) | | text |
| Inboard core extra thickness | scrap block on top fills extra thickness | plans-1980:p127 | high | cobelu fig 19-6 | text |
| Core airfoil contour (templates BL 23, 55.5, 106.25, 157 ribs) | no digits printed | plans-1980:p127 | n/a | A-sheet only | repr |
| Stick spacers | five-minute epoxy only on stick ends so epoxy stays out of joint | plans-1980:p127 | high | cobelu: no Bondo | text |

### 2.2 Section A-A and B-B: skins, caps, TE, attach fitting (p128, 19-12)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Top skin | 3 plies UND | plans-1980:p128 | high | p129 D-D "3 plies UND"; cobelu: third ply forward of hinge line only | book |
| Bottom skin | 2 plies UND | plans-1980:p128 | high | p129 D-D "2 plies UND"; cobelu step 6 two plies, third ply BID at tip | book |
| Shear web | UND, layup 2 (circled 2) | plans-1980:p128 | high | cobelu: 45 deg UND, full span first two plies; 6/4/2 plies in zones (CP26 LPC 31 corrects 3 to 2 outboard) | book |
| Spar caps | top cap and bottom cap drawn; ply counts not printed here | plans-1980:p128 | n/a | cobelu: top 7 plies, bottom 5 strips of 3 in x 0.035 UND tape; CP25 adds plies | text |
| LE | overlapped leading edge, skin wraps; "caution, do not sand into skin" arrows | plans-1980:p128 | high | cobelu: 2 in lap onto bottom skin at LE | book |
| Waterline of chord line | WL 17.4 printed twice in A-A | plans-1980:p128 | high | p126 WL 17.4 LE; p134 "17.4 waterline plane" | book |
| TE close-out | glass-to-glass joint, minimum 0.5 in overlap, micro fill at TE | plans-1980:p128 | high | CP32 p6: wings printed lap 0.6, minimum 0.5 | book |
| Rudder conduit | small tube in top skin groove near TE, drawn in A-A | plans-1980:p128 | high | cobelu: .025 wall 3/16 OD Nylaflow; CP45 LPC 121 moves it 1.5 in aft for high-performance rudders | book |
| Nav light hole | wiring hole drawn at LE bottom, near BL end | plans-1980:p128 | medium | cobelu: 1 in hot-wire passage in FC4 and FC5 (CP26 LPC 32) | text |
| Attach bolt B-B | AN8-21A, 2 per wing | plans-1980:p128 | high | cobelu hardware table: 2 x AN8-21A | book |
| Washers in B-B | AN960-816L (thin, typ.) | plans-1980:p128 | high | cobelu: 3 thin washers per wing | book |
| Wing hard points in B-B | LWA3 (bottom), LWA4 (top and bottom stacks), outboard pair drawn full scale | plans-1980:p128 | medium on which LWA number sits where (labels read LWA4 twice, LWA3 once) | cobelu: outboard 2 pieces LWA4, inboard 1 piece LWA6, plates LWA3/LWA2 over them | book |
| Access depression liner | layup 1, 2 plies BID | plans-1980:p128 | high | cobelu layup 1 two ply BID | book |
| Access strip metal (W18 / WI8) | thin aluminum strip over the depression, drawn "W18"; thickness not printed on this page | plans-1980:p128 | low on name (W18 vs WI8; cobelu says WI8, 0.016) | cobelu | text |
| Skin lap at attach recess | layup 5 (circled 5, skin) wraps the recess | plans-1980:p128 | high | cobelu layup 5: 2 plies UND 3 in wide, 30 in long, 12 in lap on skins; CP31 clarifies 1 ply per leg of the V | book |
| Tools drawn | 3/8 drive ratchet, 3 in extension, 3/4 socket (full scale) | plans-1980:p128 | high | p134 tool list same | text |
| Wing section thickness profile | no digits | plans-1980:p128 | n/a | | repr |

### 2.3 Sections C-C, D-D, F-F (p129, 19-13)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Foam shell above inboard attach | 0.6 in | plans-1980:p129 | high | cobelu: critical only at top forward edge, elsewhere +/- 0.25 | book |
| Inboard attach hard point | LWA2 (plate, outside), LWA6 (block, spar side), LWA7 (inside) | plans-1980:p129 | high (labels read on 2x crop) | CP25 LPC 9-12 swap earlier LWA7/LWA8 mistakes: LWA7 should be LWA2 | book |
| Inboard bolt | AN8-23A, one per wing | plans-1980:p129 | high | cobelu 1 x AN8-23A; p134 note: order the right length after LWA9 install | book |
| Washer and nut C-C | AN960-816 (typ.), AN363-820 nut | plans-1980:p129 | high | cobelu: 6 AN960-816, 3 AN363-820 per wing | book |
| Nut access | reached through fuselage oval baggage panel | plans-1980:p129 | high | | text |
| Rib layup at root bay | layup 7 (circled), 8 (UND over LWA6), 4 (circled at top skin, hard-point UND), 3 (BID pad) | plans-1980:p129 | medium on which circle goes to which line | cobelu: layup 4 = 3 UND plies 3 in wide, 14/10/6 in long (CP25 LPC 11 renamed LWA7 to LWA2); layup 8 = 3 UND plies 2.5 in wide | book |
| Reference to chapter 24 | dashed line at bottom, "see Chap 24" (seal of wing/spar gap) | plans-1980:p129 | high | p134 note: gap sealed in chapter 24 | text |
| D-D skins | top skin 3 plies UND, bottom 2 plies UND, shear web UND (2) | plans-1980:p129 | high | A-A | book |
| Root rib F-F recess | 0.7 in from face | plans-1980:p129 | high | CP25 LPC 8: form the 0.7 in rib with a rotary file | book |
| Root rib F-F layup | 3 plies BID, layup 6 | plans-1980:p129 | high | cobelu layup 6 3 plies BID, one laps 4 in inboard | book |
| Spar cap taper | cap shown ending short of the wing root face, tapering | plans-1980:p129 | n/a | exact cap lengths on other pages | repr |

### 2.4 Aileron sections and TE spar (p130, 19-14). Measured along the foam joint, perpendicular to the TE

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Aileron root hinge-line cut, top skin, at BL 55.5 | 5.90 in along foam joint (a trailing .2 in step shown) | plans-1980:p130 | high (5.90, 2x crop) | CP34 LPC 107 prints "5.9" | book |
| Aileron root cut, bottom skin, BL 55.5 | 7.6 in along foam joint | plans-1980:p130 | high | CP34 LPC 107 prints "7.6" | book |
| Same, top skin, BL 106.25 | 4.35 in | plans-1980:p130 | medium (3rd digit reads 5, hand 3 vs 5 close) | no second print | book |
| Same, bottom skin, BL 106.25 | 5.65 in | plans-1980:p130 | high | | book |
| Hinge-line to TE trend | top 5.90 -> 4.35 and bottom 7.6 -> 5.65 over BL 55.5 -> 106.25 | derived | n/a | extrapolated linear: BL 118.1 top about 3.99, bottom about 5.19 (assumes straight lines; p126 shows straight TE) | derived |
| Aileron outboard end | BL 118.1 | cobelu ("aileron tip BL 118.1"); p126 reads "118.1" at outboard end (partner scope) | medium | not on my pages | book (partner) |
| Hinge-line gap between hinges, top skin | 0.03 to 0.1 in full span | plans-1980:p130 | high | CP27 p6 / CP43 p6 add bottom-gap rules (section 5) | book |
| Gap, aileron LE to bottom skin | 0.08 min, 0.20 max, full span | plans-1980:p130 | high | CP27 p6: at least 0.1; CP43 p6: at least 1/8 | book |
| End gaps K-K, L-L | 0.08 to 0.2 in | plans-1980:p130 | high | | book |
| End rib extent | aileron end rib 0.4 in, wing end rib 0.5 in (K-K, L-L) | plans-1980:p130 | high | cobelu: remove 0.4 in foam at the ends | book |
| TE spar layup | layup 9 (circled 9) in the wing, shown as a C-shape around the hinge trough | plans-1980:p130 | high | cobelu: 3 plies BID plus 1 extra at hinge locations; extends 1 in into torque tube hole | book |
| Aileron LE wrap | layup 10 (circled 10), over steel rod and A2/A5 | plans-1980:p130 | high | cobelu: 1 ply BID at 45 deg, laps 1 in onto skins | book |
| Aileron end ribs | layup 11 in K-K and L-L | plans-1980:p130 | high | cobelu: 2 plies BID | book |
| Mass balance rod | drawn as hatched circle labeled A11 in I-I, H-H, J-J | plans-1980:p130 | high | p133 labels the rod A13 (conflict, section 5) | book |
| Torque tube | A10 tube, round section 3/4 in OD, in I-I | plans-1980:p130 | high | p133 A10 3/4 x .058 | book |
| Aileron hinge parts | A3 inboard hinge half over layup 9; A4 mid/outboard; A2 and A5 brackets; AN525-10R8 screw, AN960-10L washer | plans-1980:p130 | high | p133 sizes | book |
| Hinge notch spacing in H-H | 0.5 in typical setback, 0.2 in step | plans-1980:p130 | high | cobelu: notch top skin 0.2 deep | book |
| Section E-E hardware | AN3-11A bolt, AN960-10 washer, MS21042-3 nut at CS151/CS152; AN3-7A at belhorn rod end | plans-1980:p130 | medium on AN3-7A (the number reads like 7 with a crossbar) | CP30 LPC 81 says the rod-end bolt head must sit on the belhorn side | book |
| Torque tube hot-wire hole | labeled as such, 1.6 in dia per cobelu | plans-1980:p130 | high (label); 1.6 is cobelu only | cobelu | book |
| Phenolic block cover | layup 12 (circled) in E-E | plans-1980:p130 | high | cobelu and p125 text call this layup 11 (conflict, section 5) | book |
| Root rib at E-E | layup 7 (circled 7) top and bottom | plans-1980:p130 | high | | book |
| Aileron shape (airfoil, chord at tip) | no digits | plans-1980:p130 | n/a | A-sheet only | repr |

### 2.5 Controls (p131, 19-15, and p132, 19-16)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Belcrank shown at neutral aileron | arm perpendicular to pushrod, 90 deg | plans-1980:p131 | high | p132 also 90 deg at neutral | book |
| Stop bolt position | 20 deg of belcrank travel from neutral | plans-1980:p131 | high (20 deg label on 2x crop) | p125 text: stop at 20 deg up aileron | book |
| Stop bolt offsets | 1.15 in and .55 in from CS127 edges | plans-1980:p131 | high | | book |
| Stop bolt hardware | AN3-16A, MS21042-3, AN960-10 | plans-1980:p131 | high | | book |
| Belcrank bearing | BC4W10 bearing, AN470AD4-6 rivets, 6 places | plans-1980:p131 | medium (rivet number read at 2x) | | book |
| CS128 belcrank | 0.125 in 2024T3 aluminum, two required, .75 D hole, full-size pattern printed | plans-1980:p131 | high | CP49 LPC 131 moves roll controls to 4130 steel (section 4) | book |
| CS127 bracket | two per wing on the root face, 0.032 2024T3 | plans-1980:p131 handwritten note; p132 | high | CP26 LPC 36, CP31 LPC 88 agree; no dimensions printed on p131/p132 (shape from drawings, not dimensioned) | repr (shape), book (material) |
| CS126, CS129 | quick disconnect pushrod (chap 16 p3); CS129 pushrod tube | plans-1980:p131 | high | | text |
| Detail A | three places (rod ends and inserts), chap 16 p3 | plans-1980:p131 | high | | text |
| CS150 | phenolic block drawn at TE end of torque tube | plans-1980:p131 | high | p133 | book |
| CS132L weldment | belhorn at wing root, shown arm perpendicular at neutral | plans-1980:p132 | high | | book |
| CS127 attach to shear web | AN3-5A, AN960-10 (two), MS21042-3, 4 places | plans-1980:p132 | high (2x crop) | p125 text says AN3-4A (conflict, section 5) | book |
| CS131 bolt | AN4-16A, MS21042-3, AN960-416 | plans-1980:p132 | high | | book |
| Rib layup at root | layup 7, 3 plies BID ("3 plies BID rib") | plans-1980:p132 | high | cobelu layup 7 3 plies | book |
| Rudder conduit at root | arrives in the bay, points at the rudder pulley, "see step 8" | plans-1980:p132 | high | cobelu: curves down 0.7 in over 8 in | book |
| View M-M | hex hole through rib with 0.6 foam retained above, layup 8 and 7 | plans-1980:p132 | medium | | repr |
| Stick-side clearance | none printed | | n/a | CP38 caution about stick bolt and conduit at full left aileron | n/a |

### 2.6 Metal parts (p133, 19-17)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| A10 torque tube | 3/4 in OD x .058, 6061-T6, 9 in long | plans-1980:p133 | high | p125: extends 1 in inboard of aileron root | book |
| A13 balance rod | 3/8 in dia steel, 65 in; shorter pieces may be butted | plans-1980:p133 | high (6.5 vs 65: the inch mark and drawn length favor 65) | derived: aileron BL 55.5 to 118.1 is 62.6 in; with TE angle about 11.4 deg the hinge line is 63.9 in; 65 fits within 1 in. The spans disagree by 1.1 in | book |
| A2 bracket | 9 in x 1.1 in flat plus 0.5, .032 2024T-3, bend up 65 deg | plans-1980:p133 | high | | book |
| A5 bracket | 7 in, same section | plans-1980:p133 | high | cobelu: A2 (2), A5 (4) per airplane | book |
| A2/A5 hole pattern | 0.6 in typical spacing, 0.5 in from edge | plans-1980:p133 | high | | book |
| Aileron hinge stock | MS20001-P6 extruded piano hinge | plans-1980:p133 | high | CP32: aileron hinge rivets 1/8 round head pop | book |
| A3 inboard hinge | 8 in | plans-1980:p133 | high | | book |
| A4 mid and outboard hinges | 6 in each, one leg trimmed to 0.85 | plans-1980:p133 | high | | book |
| Hinge halves | reverse before cutting to length | plans-1980:p133 | high | p125 same | text |
| Hinge rivet patterns | A3 inboard and A4 patterns drawn full size; counts about 13 and 9 holes | plans-1980:p133 | low on counts (pattern is full-size picture, count only) | p125: 24 holes drilled, 23 rivets (inconsistent) | repr |
| CS150 | 1/4 in phenolic, 5/8 hole, full size shown | plans-1980:p133 | high | | book |
| CS151 | 3/4 OD x .058 6061-T6 aluminum tube, approx 30 in | plans-1980:p133 | high | | book |
| CS152 | 5/8 OD x .049 wall 4130N steel tube, 3 in | plans-1980:p133 | high | | book |
| CS132L | .050 4130 steel, arm 2.50 in, tab 3/4 x .058 4130, #12 holes | plans-1980:p133 | high | CP58: failure, replace by CS132L-R | book |
| LWA6 | 2024T3 aluminum 1/4 in thick, 2.3 x 2 in, about 0.2 in radius, 2 required | plans-1980:p133 | high | cobelu: inboard single piece | book |
| LWA7 | 2024T3 aluminum 1/8 in thick, 1.7 x 2 in, 2 required | plans-1980:p133 | high | cobelu: clamped over rib, 1 ply BID after | book |
| Others needed | other metal parts in chapter 14 (LWA2, LWA3, LWA4 etc.) | plans-1980:p133 | high | CP43 LPC 119 resizes LWA4 in chapter 14 (not on my pages) | text |
| CS132L, CS127, CS128 | available prefab | plans-1980:p133 | high | cobelu: LWA9 (12), A2 (2), A5 (4) available from distributor | text |

### 2.7 Attachment to the centersection spar (p134, 19-18)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Hole layout, aft face, inboard hole | 1.75 in down from top edge and 6.25 in up from bottom edge (the two dims sum to the spar depth at that station) | plans-1980:p134 | high (2x crop) | cobelu fig 19-57 | book |
| Bolt spacing, inboard to outboard pair | 28.85 in | plans-1980:p134 | high (crop at 4x reads 28.85) | text note on the same page says 28.83 (conflict, section 5) | book |
| Outboard pair spacing | 4.2 in apart, 1.2 in from bottom edge | plans-1980:p134 | high | | book |
| Outboard end offset | 2.0 in from the end | plans-1980:p134 | high | | book |
| Pilot holes | #10 through spar; forward-face holes 1/4 in; then line-bore to 5/8 | plans-1980:p134 | high | CP26 p8: drill 1/4 through forward and aft face | text |
| Line-bore jig | fuselage level, longerons and spar level, wing butted to spar | plans-1980:p134 | high | | text |
| Sweep tolerance | fit to spar matters more; tips may be 3 in off correct sweep | plans-1980:p134 | high | | text |
| Dihedral | wing flat at WL 17.4; fit to spar even if tip moves 2 in | plans-1980:p134 | high | model wing_dihedral 0 and p126 | text |
| Incidence | reference board level, set exact; zero incidence even with shims | plans-1980:p134 | high | OM: wings within 0.3 deg of each other | text |
| Shim washer | one washer changes incidence 0.4 deg | plans-1980:p134 | high | | book |
| LWA9 bushing | 2024T3 aluminum, 12 total; 0.625 +/- .001 OD (wing hole), flange .875 +/-.010 dia, .062 +/-.010 thick, bore .50 +/- .001, length .9 +/- .04 | plans-1980:p134 | high (2x crop) | 12 = 6 per wing; cobelu same | book |
| Bushing length rule | trim to hole depth or .010 shorter; never longer | plans-1980:p134 | high | | text |
| Fill the inboard forward-face spar hole | foam plus 2 plies BID seals fuel | plans-1980:p134 | high | | text |
| Hardware per wing | 2 AN8-21A, 1 AN8-23A, 6 AN960-816, 3 AN960-816L, 3 AN363-820 | plans-1980:p134 | high | cobelu table identical | book |
| Bolt length note | AN8 lengths NOT in bill of materials; order after bushings fitted | plans-1980:p134 | high | | text |
| Tolerance note | .015 in clearance acceptable; 1/2 in bolts chosen for washer overlap | plans-1980:p134 | high | | text |
| Tools | 3/8 drive ratchet, 3 in extension, 3/4 socket (2 each) | plans-1980:p134 | high | | text |
| Wing/spar gap | sealed in chapter 24 | plans-1980:p134 | high | | text |
| Torque on reassembly | 150 to 200 in lb, estimate acceptable | om-1980 (text extract; printed page not image-checked) | medium | | text |

### 2.8 Weights, build times (not on scan pages; CP and OM only)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Wing skinned, no root ribs, ailerons cut out | 46 lb | cp-text:CP26 p3 | high (typed) | | book |
| Wing with root layups and TE spar, no aileron | 46 lb 8 oz | cp-text:CP26 p3 | high | | book |
| Aileron with mass balance, hinges, torque tube, universal | 5 lb 2 oz | cp-text:CP26 p3 | high | CP27 p1 filled and painted: 5.4 lb each | book |
| Wing complete to end of chapter 19 (board, ailerons, hinges, controls) | 51 lb 8 oz | cp-text:CP26 p3 | high | per wing (CP27 p1: 64 lb each with ailerons and rudders; 60 lb each with winglets, no ailerons, painted) | book |
| Wing with upper and lower winglet, rudder, ready to finish | 64 lb | cp-text:CP26 p3 | high | | book |
| Build time: both wings | 97 mh; root layups, aileron cutout and TE spar 15 mh; ailerons complete 32 mh; jig and drill to spar 6 mh | cp-text:CP26 p3 | high | | text |
| Model wing weight | 85.0 lb in config (no source) | open-ez config | n/a | CP26: 51.5 lb per wing, or 64 with winglets, so 103 lb to 128 lb for two wings with winglets | conflict (flag) |
| OM empty weight context | 750 lb normally equipped | om-1980 | medium | | text |

### 2.9 Cure times, process numbers

| Item | Value | Cite | Conf | Model use |
|---|---|---|---|---|
| Hot-wire speed | 1 in per 4 to 6 seconds, check on scrap | cobelu step 3 | text only | text |
| Pause at corners | 2 to 3 seconds at each talking number marked P | cobelu step 3 | text only | text |
| Bondo hold on bottom jigs, 5 minute epoxy | no cure times printed on p127 to p134 | | n/a | none |
| LWA plate cure | weight about 10 lb on each plate | cobelu step 4 | text only | text |
| Access cover RTV cure | at least 24 hours | cp-text:CP31 p5 LPC 91 | high | text |

No epoxy cure durations are printed on p127 to p134. Cure times for chapter 19 live on earlier pages or in chapter 3.

## 3. Build-order list (op candidates, p127 to p134 and the surrounding steps)

The chapter 19 order on these pages (cobelu numbering in brackets): layout blocks, hot-wire cores, build layups, aileron cut and hinge, controls, attach.

| # | Short name | What is done (paraphrase) | Prerequisites | Jig or fixture |
|---|---|---|---|---|
| 1 | Block stacks | Stack 14 in blocks, join with sticks and epoxy | foam, 5-min epoxy | flat table |
| 2 | Planform hot-wire | Cut planform using angle-offset method | step 1 | hot-wire frame, templates |
| 3 | Airfoil hot-wire | Hot-wire each core top then bottom | step 2; rib templates at BL 23, 55.5, 106.25, 157 | hot-wire, A-sheet templates (not held) |
| 4 | Inboard core trim | Trim inboard LE to 32.87 in | step 3 | vertical templates |
| 5 | Torque tube and attach cutouts | Cut torque-tube hole, cut inboard wedge and 0.6 shell | step 4; ch 14 spar dims | torque-tube templates (not held) |
| 6 | Aileron cutouts | Hot-wire interior aileron outline in FC2 and FC3 | step 3 | aileron templates (not held) |
| 7 | Nav-light passage | Hot-wire 1 in hole in FC4 and FC5 | step 3 | two small templates |
| 8 | Core assembly | Micro cores into jigs, layup shear web | steps 3 to 7; jigs from p118 to p124 (partner) | five jig templates (not held) |
| 9 | Spar caps, skins | Layup caps and skins bottom then top | step 8; ply data on p128, p129, p123 (partner) | jig on table |
| 10 | Root layups | Rib, LWA6, LWA7, layup 7 to 8 | step 9; ch 14 spar | clamps |
| 11 | Aileron cut and TE spar | Cut ailerons out, layup TE spar (layup 9) | step 9; p130 dims | razor saw, straight edge |
| 12 | Aileron build | Bond balance rod, A2, A5, A10; layup 10 and 11 | step 11; p133 parts | aileron jig |
| 13 | Hinges | Drill and rivet three hinges; check balance | step 12; p133 hinge stock | wire hang for balance |
| 14 | Torque tube controls | Make CS150, CS151, CS152, CS132L, layup 12 | step 13; ch 16 parts | none |
| 15 | Root bay controls | Mount CS127 and belcrank, set stop at 20 deg | step 14 | angle finder |
| 16 | Wing attach | Drill, line-bore, bush, shim | steps 10, 15; spar with holes | foam wedges, saw horses, bondo lumps |
| 17 | Later add-ons | Tie downs, vortilons, access covers, steel controls | steps 9 to 16 | see section 4 |

## 4. CP corrections touching chapter 19

Classes: MEO, MAN (MAN-GRD ground, MAN-GND, MAN/10HRS), DES, OPT, OBS. LPC numbers as printed. Page = issue page from sectioned footer.

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP24 p6 LPC 2 (pg 19-10) | MEO | Adds tie-down hole: 3/8 in hole, 13 in inboard along LE, 9.5 in aft of LE, with 3/8 x .049 2024T3 tube flushed in. Handwritten on plans-1980:p126 | Add a tie-down tube feature. Hole offset is from LE, perpendicular |
| CP24 p6 (VariEze list) "18-3 and 19-11" | MEO | Nyloseal .050 wall becomes Nylaflow .025 wall (rudder conduit) | Text only; conduit is .025 wall 3/16 OD |
| CP25 p5 hints | text | "BID tape" means 45 deg cut cloth; spar cap tape is the 3 in UND | text |
| CP25 p6 LPC 7 | MEO | Wing root LE 113.9, not 113.4 (back cover) | already in model |
| CP25 p6 LPC 8 | MEO | Rib 0.7 in made by rotary file (19-8) | p129 F-F 0.7 in |
| CP25 p6 LPC 9, 10, 11 | MEO | LWA7 should read LWA2 (19-6 and 19-7) | model part names LWA2 not LWA7 for the outer plate |
| CP25 p6 LPC 12 | MEO | LWA8 should read LWA7 (19-8) | LWA7 is 1/8 in, 1.7 x 2 in (p133) |
| CP25 p6 spar-cap thickness box | MAN-GRD (CP28 p9 LPC 56 confirms) | If 5-ply test is 0.125 in not 0.18 in, add plies. Chapter 19 bottom: add 1 ply BL 25 to 130 and 1 ply BL 40 to 90. Top: add 1 ply BL 23 to 140, BL 33 to 92, BL 40 to 78 | Spar cap ply schedule; model spar_cap_plies 17 differs; model is at odds with 7 top and 5 bottom |
| CP26 p3 weights | n/a | Wing and aileron weights above | see section 2.8 |
| CP26 p6 LPC 31 | MEO | 19-5: 3 plies should be 2 plies (outboard shear web) | shear web 2 plies BL 120 to 157 |
| CP26 p6 LPC 32 | MEO | 19-3: nav light hole text fixed, hot-wire 0 to 12 | text |
| CP26 p6 LPC 36 | MEO | CS127 can be made from the p19-15/16 drawings, .032 2024T3 | handwritten on plans-1980:p131 |
| CP26 p8 hints | text | Spar-cap clamp with foam; wing attach jigging with straps; spotface cuts 0.007 oversize, flox the bushings; round LE of aileron around mass balance | text |
| CP27 p6 | n/a (caution) | Keep 0.1 in minimum gap, aileron LE to wing bottom skin (icing) | p130 says .08 min, conflict section 5 |
| CP28 p8 | n/a (hint) | Bend aileron hinge pins into a slight S before install | |
| CP28 p9 LPC 64 | DES | 19-17: snub aileron hinge pins per newsletter | |
| CP28 p9 LPC 56 | MAN-GRD | Spar cap plies must be added as CP25 says | |
| CP29 p8 | hint | Extra spar ply: longest first, shortest last | |
| CP30 p9 LPC 77 | MEO | 19-18 step 11: "chapter 6 and 7" becomes pages 14-8 and 14-9 | cobelu cites Figure 14-25/14-26 for same |
| CP30 p9 LPC 81 | (listed in CP69 index) | 19-14 E-E: rod-end bolt head belongs on belhorn side | bolt head side in E-E; model hardware only |
| CP31 p4 | clarification | 19-8: layup 5 is one ply UND per leg of V (2 plies over web face) | Layup 5 plies |
| CP31 p4 | hint | Aileron balance: keep ailerons light, check hinge pivot, weight not too near hinge | |
| CP31 p5 LPC 88 | MEO | CS127 is .032 2024T3 | |
| CP31 p5 LPC 91 | MEO | Add access hole covers, .016 aluminum, RTV | add as optional covers |
| CP32 p6 | n/a (caution) | TE glass-lap minimums: wings 0.5 in (0.6 printed); aileron cutouts 0.75 top, 0.52 bottom (1.0 and 0.75 printed); ailerons 0.3 (0.5); wing root rib 0.4 (0.6) | lap widths |
| CP32 p6 | hint | Aileron hinge rivets are 1/8 round-head pop rivets | |
| CP33 p6 | OPT | Antenna may go in a root LE void like F-F and E-E | |
| CP34 p7 LPC 107 | MEO | Aileron root cut is perpendicular to TE through the 5.9 line, not the 7.6 | root cut geometry (vertical plane) |
| CP34 p7 (VariEze list) | MAN | Safety aileron hinge pins: shorten 1/4 in, drill and safety wire | |
| CP36 p6 LPC 113 | MEO | OM aileron mass balance wording fixed | OM p~32 |
| CP37 p3 | caution | Round the aileron lower LE corner per 19-14 to avoid vibration at 90 to 120 kt | |
| CP37 p3 | hint | Foam rubber trick to hold hinge against aileron at A2 and A5 | |
| CP38 p5 | caution | Check stick bolt vs rudder conduit at full left aileron | |
| CP38 p5 | hint | Ventilate outboard wing attach recess with a soda straw | |
| CP39 p7 | OPT | Teflon-lined hinge pin, spherical bearing instead of phenolic block (CS152 fit) | |
| CP43 p4 LPC 119 | MEO (chapter 14) | LWA4 1.5 x 2 becomes 1.75 x 2; LWA5 2 x 2 becomes 2.25 x 2 | size change; touches wing LWA4? Open question |
| CP43 p6 | caution | Keep aileron LE to wing TE gap 1/8 in minimum, esp. outboard end | conflict section 5 |
| CP45 p4 LPC 121 | MEO (new construction) | High-performance rudder: conduit 1.5 in aft of A-12 position; summary view fig 19-68 | Alter conduit route |
| CP47 p7 LPC 126 | MAN | Vortilons mandatory on the main wing LE. Cobelu step 16: three per side at BL 80.0, 106.5, 126.8; LE offsets 23, 47.25, 73.75 in; 6-ply BID, 8 x 8 in square cut into six | Add vortilons (shapes on A-sheet, not held) |
| CP49 p6 LPC 131 | MAN-GRD | Roll controls in the engine bay and wing roots go to 4130 or stainless; includes CS127 and CS128; intumescent coating | CS127, CS128 become steel (p131 prints aluminum) |
| CP58 p7 to p10 | MAN-GRD | CS132L belhorn failure: replace with two-arm CS132L-R within 25 hours; rebalance vibrating ailerons to top-level | CS132L replaced by CS132L-R. Aileron balance tightened |
| OM (text extract) | n/a | Aileron full travel 2.1 in plus or minus 0.3 at inboard end; wings within 0.3 deg of each other | travel check |

## 5. Conflicts (both sources cited)

1. **Wing attach bolt spacing**: drawing 28.85 in (plans-1980:p134, 4x crop) vs the text note printing 28.83 in (plans-1980:p134, same page; cobelu repeats 28.83). Not resolved.
2. **CS127 bolts**: drawing prints AN3-5A, 4 places (plans-1980:p132); the p125 text and cobelu print AN3-4A.
3. **Mass balance rod label**: A11 in sections (plans-1980:p130) vs A13 in parts sheet (plans-1980:p133).
4. **Layup 11 vs 12**: p130 K-K and L-L show 11 for the aileron end ribs and E-E shows 12 for the phenolic cover; p125 text calls both 11 (partner page).
5. **Aileron to wing bottom gap**: p130 .08 min .20 max; CP27 p6 0.1 min; CP43 p6 1/8 min (all consistent with each other only if you take the largest minimum).
6. **A13 balance rod length**: p133 "65 in" vs my derived hinge-line estimate 63.9 in from p126 values; not a source conflict, a 1.1 in margin.
7. **CS128 and CS127 material**: aluminum (plans-1980:p131, p133, CP26 LPC 36) vs steel (CP49 LPC 131). Later CP wins for as-built, not for the 1980 page.
8. **Hinge rivets**: p125 says 24 holes drilled and 23 rivets pop-riveted (partner page); no count on p133.
9. **Wing weight**: model 85.0 lb vs CP26 p3 about 51.5 lb per wing, CP27 p1 60 to 64 lb each with winglets.
10. **Spar cap plies**: model spar_cap_plies 17 and a 5-station [17,17,14,11,8] schedule do not match book top 7 and bottom 5 strips plus CP25 additions (cobelu step 5 and 7).
11. **Wing skin laminate**: model wing_skin is BID/BID/UND/BID; book is 3 UND top, 2 UND bottom plus BID reinforcements (plans-1980:p128, p129).
12. **Step numbering**: two "step 11" in 1980 (p125, p134); cobelu uses 11 and 12.

## 6. Open questions and low-confidence reads for the captain to re-read

- p130 H-H "4.35": third digit could be 3 or 5. Re-read on the original page. Used for the BL 106.25 top-skin chord.
- p130 E-E "AN3-7A": the digit reads 7 with a bar. A real AN3-7A would be reasonable but check against CP30 LPC 81 text.
- p131 BC4W10 rivets "AN470AD4-6, 6 places": a second look at the 2x crop recommended.
- p128 "W18 / WI8": is it a W-number part, or a letter I? Thickness not printed on my pages (cobelu .016).
- p128 B-B LWA labels: which LWA number sits on top vs bottom stack. CP43 LPC 119 resizes LWA4 (chapter 14, 8 pieces); are there 4 in the wings and 4 in the spar? Not shown.
- p133 hinge rivet counts (about 13 and 9): low confidence; p125 says 24 and 23.
- Cure times and layup cut lengths for caps/skins live on p121 to p124 (partner), not on my pages.
- The owner holds no A-sheets: jig templates, core templates, rib shapes, aileron templates, rudder conduit curve A12, vortilon outlines are all unavailable. Treat airfoil and aileron shape as "repr".
- Aileron outboard end BL 118.1 is only read from cobelu and the small label on p126 (partner scope).
- OM page numbers cited as "text extract" were not image-verified; re-read if the model uses them.
- Check whether the model's `aileron_mass_balance_pct` 100.0 means anything against the book rule (hang between top-level and bottom-level angles, up to 0.3 lb of added lead aft of the rod).
- Known-good cross-check: block geometry on p127 is internally consistent with the p126 sweep (11.36, 12.49 deg) and BL stations; the model's wing_sweep_le 22.98 and TE geometry could be re-derived from it.
