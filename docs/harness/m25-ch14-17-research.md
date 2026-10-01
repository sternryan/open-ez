# Centre-section spar, firewall, control system, pitch trim: source research (2026-10-01)

A read-only research pass for milestone 2.5. Every cited value was read on a page image, not the
OCR. The 1980 plans are cited as `plans-1980:pNNN` (PDF page). Roncz figures are the cobelu
transcription of chapter 30 (images read directly). Paraphrases are ten words or fewer. The captain
re-verifies any value that goes into the model.

Page map (`plans-1980`, confirmed against the printed page numbers on the images):
- Ch14: p84 is 14-1, p85 is 14-2, p86 is 14-3, p87 is 14-4, p88 is 14-5 (top and plan views, number
  printed sideways), p89 is 14-6 (jig), p90 is 14-7 (parts), p91 is 14-8 (sections A-A, B-B), p92 is
  14-9 (C-C, D-D), p93 is 14-10 (E-E, F-F), p94 is 14-11 ("last page", G-G, H-H). All read.
- Ch15: p95 is 15-1, p96 is 15-2 ("last page, chap 15"). Both read.
- Ch16: p97 is 16-1, p98 is 16-2, p99 is 16-3, p100 is 16-4 (number printed sideways), p101 is 16-5
  (sideways), p102 is 16-6, p103 is 16-7, p104 is 16-8. All read. The p104 footer is smudged; it
  is the last ch16 page.
- Ch17: p105 is 17-1, p106 is 17-2, p107 is 17-3 ("last pg, chap 17"). All read. p108 is 18-1.
- Anchors read on other pages: p36 (5-1, side), p48 (8-2, aft harness note), p50 (9-1, spar aft
  face datum), p171 not re-read.
- The pages cite A-sheet full-size drawings (A4 firewall, A5, A7, A8 console and control layout,
  A11 spar-cap trough templates, A1 panel). The owner holds none of them. Anything only there is
  representational.
- Owner's Manual (om-1980, printed page numbers): control description p8, trim p9, stick on the
  right console p6, rigging limits p29.
- Cobelu ch14, ch15, ch16, ch17 markdown was checked against the scan. Its figure images for those
  chapters are redraws of the scan pages; the scan wins.

## Anchors: confirmed or corrected

| Claim | Result |
|---|---|
| Spar forward face FS 118.5 (p88) | Confirmed, top view, at the centreline out to BL 23. Plan view also prints FS 123.54 at BL 56.46 on the forward face. |
| Spar aft face FS 125.5 at BL 26.75 (p50) | Confirmed on p50 (datum board reference). It is the swept aft face, not 0.5 aft of the firewall. At the centreline the aft face is FS 125.0 (p88 plan view, p91 section A-A label). My arithmetic: 125 + (26.75 − 23) × tan 8.57° = 125.57, so 125.5 is consistent. |
| Side aft end / firewall FS 125 | Firewall line FS 125 is read on p101 (view looking inboard). p36 prints only the 103 in side length; "FS 125" for the side end is derived (22 + 103), not printed. The spar aft face at the centreline (p88, p91) is also FS 125.0. |
| Ch 8 reference on p9-1 becomes Ch 14 (CP36 LPC 112) | Confirmed. p50 is 9-1 and its datum paragraph sends the reader to the spar chapter. The CP text says the same correction. |
| Aft harness bolts to the spar tabs (ch14) | Confirmed twice: p48 (8-2, step 5) and p87 (SH1 part, step 13). |
| "Main gear extrusions Chapter 14" (CP25 LPC 19) | Corrected. The LPC is about the engine-mount extrusions on page A4 ("Chapter 6" should be "Chapter 14", two places). The EM12 extrusions (p87) are the ch14 engine-mount parts. The main-gear extrusions are ch5. |
| Ch17 starts p105 (17-1) | Confirmed. |
| p102 is 16-6 | Confirmed. |
| Elevator linkage uses an extra CS-202 spacer (CP note; ch16) | Confirmed in cobelu ch30 figure 30-72: one extra 0.4 in spacer, called CS-202. Cobelu BOM lists three CS-202. The GU plans list two (p99). Not a CP note; it is Roncz text. |
| NC-5A on the left elevator at BL 0 | Not supported. Cobelu fig C-1 puts NC-5A at the inboard end of the left tube, labelled BL 9.2 (left). BL 0 is the dimension datum on that drawing. Medium confidence (rotated figure, small labels). |

## Operations

Graph note: existing ids used as prerequisites come from ch04–ch09, ch12, ch13 and ch30. All new
ops also require `c03.layup-skills` (omitted below where another predecessor exists). Missing
edges worth adding to existing ops are listed after the tables.

### Chapter 14 (ids `f14.<slug>`; both canard variants)

| Op | Requires | What happens |
|---|---|---|
| `f14.jig` | `c03.layup-skills` | Cut a 112.92 × 12.5 particle-board upright, lay out the swept top view (23 in centre, 56.46 each side, 5.04 drop, 6.05 shelf), Bondo it true to the bench. Build shelf parts A, B, C on supports E, F, G at 90°. |
| `f14.foam-box` | `f14.jig` | Cut all foam. Lay CS1 aft-face PVC on the shelf, release-taped. Size urethane CS2 and CS3 flush to the jig. Bond CS2 and CS3 with micro, nail, pine-stick them. Fit end bulkheads CS5, CS8, 1/4 proud of the jig. Carve clearance dishes at the outboard attach points. |
| `f14.cs4-forward` | `c03.layup-skills` | Three PVC pieces for the forward face. One BID at 45° each, 1 in peel-ply border, knife-trim. |
| `f14.lwa-fabricate` | `c03.layup-skills` | Make the LWA1 to LWA5 aluminium pieces from the p90 patterns. Clean, sand dull. Radius corners (0.1 or 0.2). |
| `f14.interior-layups` | `f14.foam-box`, `f14.cs4-forward`, `f14.lwa-fabricate` | One wet session. Pull nails, slurry the inside, layup 2 (one BID at 45° on three faces and end bulkheads). Set CS6, CS7 27 in from centre with wet micro. Layup 3 inboard (3 UND strips 10, 8, 6 in, LWA1, BID over). Layup 4 outboard (3 UND strips 15, 13, 11 in, LWA1, BID over). Weight each with about 5 lb under plastic. |
| `f14.close-box` | `f14.interior-layups` | Wet-micro the three CS4 pieces on, butt joints. Cure 2 to 3 days. Pull the box from the jig. |
| `f14.cap-troughs` | `f14.close-box` | Forward face down. Mark the five trough points on the aft face and cut the sliver off through CS1. Carve eight cap troughs with the A11 templates and a 36-grit block. Cut the 1/2 × 1 in chamfer on the forward edges. Do not cut deep. |
| `f14.shearweb-lwa45` | `f14.cap-troughs` | Dremel pockets and flox LWA4 (four) and LWA5 (two) flush with the aft face. Radius foam corners. Layup 5 across the aft face under both caps (3 BID at 45°, or the UND option). Peel-ply it. |
| `f14.spar-caps` | `f14.shearweb-lwa45` | Dam the aft face. Top cap: 12 plies of 3 in UND, four full span, then tapering 5 in per ply each side. Bottom cap: 9 plies, three full, tapering 7 in per ply each side. Round the trailing edge about 3/16. Sand depth no more than 0.04. Check ply bulk first with a 5-ply test. |
| `f14.spruce-layup6` | `f14.spar-caps` | Four 1 × 1 × 3 spruce blocks at BL ±7.5, top and bottom, micro'd flush. Layup 6 (three BID at 45° around three sides, or the UND option). Flox LWA2 (two) and LWA3 (two) over the other metal. |
| `f14.lwa23-layup7` | `f14.spruce-layup6` | Radius LWA2/3 corners 1/8. Three 3 in UND plies over them (top and bottom outboard, top inboard). One 5 in BID at 45° over the UND, aft face only. Peel-ply the edges. |
| `f14.baggage-hole` | `f14.lwa23-layup7` | Cut the forward-face access panel, 5 high by 14 long, centred. Sand foam edges to glass-to-glass. Layup 8 (3 BID at 45°, full span, 1 in onto top and bottom, or the UND option). |
| `f14.end-bulkhead-layup9` | `f14.baggage-hole` | Flox corners round CS5 and CS8. One BID at 45° over each outboard bulkhead. |
| `f14.nut-access-hole` | `f14.end-bulkhead-layup9` | Cut a 2 1/4 in hole through the bottom at BL 53.5 for wing-nut access. Seal the foam edge with dry micro. |
| `f14.fit-fuselage` | `f14.nut-access-hole`, `f05.spar-cutout`, `f07.skin-left` | Slide the spar in from one side. Centre it on a firewall centreline. Check skew from the tips to the nose. Level the outboard fittings with level longerons. Shim or wedge as needed. CP25: shave a wedge off the aft seat bulkhead to clear the kink. |
| `f14.bond-spar` | `f14.fit-fuselage`, `f04.firewall-fwd` | Pull back 2 in, epoxy and flox, slide home. Two BID at 45°, 2 in wide, round the spar at the skin. One BID tape to the firewall inside. Epoxy four W16 spruce wedges. 10-ply BID bridges spar to longerons. Wet-install the EM12 extrusions 1.6 in aft of the firewall. Drill four 1/4 holes per corner, bolt 16 bolts. |
| `f14.sh1-tabs` | `f14.bond-spar` | Two SH1 plates bolted to the forward bolts on top of the spar carry the aft harness. Required by `f08.shoulder-harness` (aft half). |

### Chapter 15 (ids `f15.<slug>`)

| Op | Requires | What happens |
|---|---|---|
| `f15.parts-fab` | `c03.layup-skills` | Make CS15 (2), CS71 (4), CS72 (2), BA (2), CS75 bushing and the CS73 brackets from the p95/p96 patterns. Most are prefab. |
| `f15.stainless-firewall` | `f14.bond-spar`, `f15.parts-fab` | Trial-fit the stainless sheet over the extrusions and six studs. Caulk a 1/8 bead about an inch from the edge. Press on, bolt the pulley brackets (three #10 holes each), clamp top and bottom, cure two days. |
| `f15.belcrank-brackets` | `f15.stainless-firewall` | Offset the rudder/brake belcrank assembly from the cable slot. Drill #10 through stainless, insulation and ply. AN3-6A bolts. Inboard nuts in the baggage space. Outboard nuts via a ground hole, filled with dry micro. |
| `f15.master-cylinders` | `f15.belcrank-brackets` | Cleveland or Gerdes cylinders upright between the engine-mount fittings. Lower CS73 bracket, drill, countersink for flush AN509. Upper brake arm on CS75, free to move. Longer bolt later with the engine mount. |

### Chapter 16 (ids `f16.<slug>`)

| Op | Requires | What happens |
|---|---|---|
| `f16.side-consoles` | `f07.skin-left`, `f06.bond-panel`, `f06.bond-rear-seat` | Fabricate right front and rear consoles from 0.35 in dark-blue foam. 1 BID inside, bond to side, bulkheads and panel with micro. 2 BID over the outside, 1/2 in lap. Large stick opening left in the front console. |
| `f16.pivot-bulkheads` | `f16.side-consoles` | Bond CS109 (front) and CS118 (rear) 1/4 plywood to the consoles and sides with flox. 2 BID all round. |
| `f16.firewall-bearing` | `f15.stainless-firewall` | 1 in hole through the firewall at BL 6.2R, WL 12.3. Pot the flanged bronze bearing in flox, dimpled eight places. The torque tube must sit in place while it cures. |
| `f16.torque-tubes` | `f16.pivot-bulkheads`, `f16.firewall-bearing` | Build CS105, CS106, CS115, CS112 inserts. Pilot-drill both stick pivots in one plane, ream the 3/8 press fit for CS112. Install through the firewall. CS108 and CS117 phenolic bearings, CS107 ring. Bolt CS108 to CS109, CS117 to CS118. Bolt CS120 on CS121, flox CS123, cure unmoved. |
| `f16.sticks-pushrods` | `f16.torque-tubes` | Fit CS103 front stick and CS119 rear stick on tight 1/4 bolts. Make CS110 so both sticks stay parallel. Holding CS124 vertical and sticks 5° inboard, drill CS116 into CS120. Rod ends HM3 (roll) and HM4 (pitch), CS201 and CS202 spacers. Check rod-end thread. Grease five pivots. |
| `f16.pitch-pushrod` | `f16.sticks-pushrods`, `r30.elev-nc12a`, `r30.align-canard` | CS102 and CS136 pitch pushrods with HM4 ends and the quick disconnect. Roncz: one extra 0.4 in CS-202 offsets the elevator-end rod end outboard. |
| `f16.aileron-linkage` | `f16.sticks-pushrods` | After the wing is built (ch19, not in graph): CS125L, CS126L and quick disconnects with the two 90° angles held, ailerons neutral. Do not bend the rod-end threads. |
| `f16.rudder-conduit` | `f13.rudder-pedals`, `f16.firewall-bearing`, `f04.rear-seat-bkhd-hole` | Two 82 in nylon conduits at WL 8, through the four bulkhead holes, flox'd every 6 in. Over the LB17 block of the brake. Thimble a 3/32 cable to CS15. Slot the firewall. |
| `f16.rudder-cable-rig` | `f16.rudder-conduit`, `f15.belcrank-brackets` | After the winglet (ch20, not in graph): pedal vertical at full rudder, CS15 sleeve 0.7 in off the firewall. Pulley, 1/16 cable, quick disconnect. Rudder top trailing edge 6 in out (30°), wedge, swage. Keep 0.7 in overtravel at both ends. |
| `f16.brake-cables` | `f16.rudder-cable-rig`, `f15.master-cylinders` | 3/32 cable from CS15 to the master-cylinder arm, rubber sleeve on it, slack until full rudder. The cylinder is the rudder stop. Check smooth return. |
| `f16.adjustable-pedals` (optional) | `f16.rudder-conduit` | Adjustable pedal hardware about 8 in forward of the panel. |

### Chapter 17 (ids `f17.<slug>`)

| Op | Requires | What happens |
|---|---|---|
| `f17.mount-blocks` | `f16.side-consoles` | PT1 and RT3 from 1/4 birch. Dremel the skin for the AN3 bolts, bond PT1 to the left side with flox, 1 BID. Notch the right console 1/4 × 1, bond RT3, 1 BID. |
| `f17.parts` | `c03.layup-skills` | Make PTH, RT1, two RT2, four PW. Cut spring stock to unstretched length: PTS 6.0, RTS 2.0, CS 0.5. |
| `f17.pitch-trim` | `f17.mount-blocks`, `f17.parts`, `r30.elev-trim-belcrank`, `r30.align-canard` | Two 20 in cables swaged to PTH. Nylon sleeves in panel holes. Swage at the 5.6 and 6.2 dimensions with neutral trim. PTS springs to the elevator bracket with safety wire. Elevator at zero at neutral. Friction set, slot cut. Roncz: the bracket is the NC-5A on the left tube. |
| `f17.roll-trim` | `f17.mount-blocks`, `f17.parts`, `f16.torque-tubes` | RTS springs sewn to RT2 and RT1. Two RT2 bolted on CS105. RT1 on RT3 with friction hardware. Friction just holds full right trim against full left stick. Slot the cosmetic cover (ch24). |
| `f17.fixed-trim-tab` (optional) | `f17.pitch-trim` | Only if spring shortening is not enough: add a 1.2 × 10 × 0.02 aluminium tab on the elevator. |

Count: 17 ch14 ops, 4 ch15 ops, 11 ch16 ops (one optional, two rely on chapters 19 and 20, which
are not in the graph), 5 ch17 ops (one optional).

Edges to add to existing ops:
- `f09.position-gear` should require `f14.fit-fuselage` (datum board at the spar aft face; CP36
  LPC 112).
- `f08.shoulder-harness` aft half should require `f14.sh1-tabs`.
- `f06.bond-firewall` conflicts with the CP25 builder hint (see Conflicts).
- `f04.firewall-aft` already mentions stainless and insulation; `f15.stainless-firewall` is the
  book's actual install step. CP25 LPC 25 defers the insulation until after cowling. The graph
  may double-count this work.

Notes:
- Book order within step 4: layups 2, 3 and 4 are one session, with no cure between (p84, p85).
- Step 5 text: after trough carving, the spar-cap sketch is on p85.
- Layup 5, 6 and 8 each have a UND option (CP25 LPC 26, handwritten tables on p85, p86, p87).

## Materials (ch14 / ch15 / ch16 / ch17 `materials` shape)

**Ch14 (whole spar):**
- `{cloth: BID, plies: 1, where: "CS4 forward face pieces, 45 deg, layup 1"}`
- `{cloth: BID, plies: 1, where: "inside of box, all faces and bulkheads, 45 deg, layup 2"}`
- `{cloth: BID, plies: 1, where: "over interior bulkheads CS6 and CS7, 1 in lap (5 in at attach points), layup 3"}`
- `{cloth: UND, plies: 3, where: "inboard attach, 4 in wide, strips 10, 8 and 6 in, layup 3"}`
- `{cloth: BID, plies: 1, where: "over inboard LWA1, 1 in lap"}`
- `{cloth: BID, plies: 1, where: "over outboard bulkheads, 5 in inboard lap, layup 4"}`
- `{cloth: UND, plies: 3, where: "outboard attach, 4 in wide, strips 15, 13 and 11 in, layup 4"}`
- `{cloth: BID, plies: 1, where: "final over outboard LWA1, lapping onto the bulkhead"}`
- `{cloth: BID, plies: 3, where: "aft-face shear web, 45 deg, full span, layup 5 (or UND at +45 and -45)"}`
- `{cloth: UND, plies: 12, where: "top spar cap, 3 in wide, 4 full span then 5 in taper per side"}`
- `{cloth: UND, plies: 9, where: "bottom spar cap, 3 in wide, 3 full span then 7 in taper per side"}`
- `{cloth: BID, plies: 3, where: "around three sides, leading edge to leading edge, 45 deg, layup 6 (or UND, four plies at +45 and -45)"}`
- `{cloth: UND, plies: 3, where: "3 in wide over each LWA2 and LWA3, layup 7"}`
- `{cloth: BID, plies: 1, where: "5 in wide at 45 deg over layup 7, aft face only"}`
- `{cloth: BID, plies: 3, where: "full span at the baggage hole, glass to glass, layup 8 (or UND, two plies)"}`
- `{cloth: BID, plies: 1, where: "over each outboard bulkhead CS5 and CS8, layup 9"}`
- `{cloth: BID, plies: 2, where: "round the spar at the fuselage skin, 2 in wide, 45 deg"}`
- `{cloth: BID, plies: 1, where: "spar to firewall tape, inside"}`
- `{cloth: BID, plies: 10, where: "spar to longeron reinforcement at each of four W16 places; first two lap over the longeron"}`
- Stock: UND tape 3 in wide, 0.035 thick, 1677 in total. Spar cap strip lengths: top 113 ×4, then 100,
  90, 80, 70, 60, 50, 40, 30; bottom 113 ×3, then 96, 82, 68, 54, 40, 26 (the totals add to 1677 only
  with three bottom 113s, see Conflicts).
- Foam: 6 mm (0.25 in) PVC R100, 6 lb/ft³ (CS1, CS4, CS5 to CS8); 1 in green urethane, 2 lb/ft³ (CS2,
  CS3). Four spruce 1 × 1 × 3 blocks. Four W16 spruce wedges.
- Metal (2024-T3): LWA1 2 × 1.5 × 1/8 ×6; LWA2 2 × 2.5 × 1/8 ×4 (two are for ch19); LWA3 2 × 6.4 × 1/8
  ×4 (two for ch19); LWA4 2 × 1.5 × 1/4 ×8 (four for ch19); LWA5 2 × 2 × 1/4 ×2; SH1 2.3 × 0.7 × 1/8
  ×2; EM12 8 in of 1/8 × 1 × 1 angle ×4.
- Hardware: AN4-15A and AN4-16A through longeron, AN4-16AS through spar, AN960-416 washers, MS21042-4
  nuts, AN4-17A through each SH1 (two places).

**Ch15:**
- Stock: CS15 1/8 2024-T3 ×2; CS71 0.064 2024-T3 ×4; CS72 0.032 2024-T3 ×2; BA 1/8 2024-T3 ×2;
  CS75 steel bushing 5/16 OD × 1/4 ID × 0.15; CS73 from 1.5 × 1 × 0.125 2024-T3 angle.
- No cloth. Silicone sealant bead, 1/8 dia.
- Hardware: AN3-6A, AN3-7A, MS21042-3, AN960-10, AN509-10R8, AN470AD4-6 rivets (six per bearing),
  BC4-W10 bearing in each belcrank.

**Ch16:**
- `{cloth: BID, plies: 1, where: "inside of each console"}`
- `{cloth: BID, plies: 2, where: "outside of each console, 1/2 in lap"}`
- `{cloth: BID, plies: 2, where: "round CS109 and CS118 pivot bulkheads"}`
- Foam 0.35 in R45 dark blue. Plywood: CS109 and CS118 1/4 birch 5-ply. Phenolic 1/4: CS108, CS117.
- Tubes (p99 table; * = leave long and trim): CS136 1/2 × .035 2024-T3 8.5*; CS102 same 12.7; CS103
  5/8 × .049 4130 6.1; CS104 3/4 × .058 6061-T6 5.2 ×2; CS105 3/4 × .058 6061-T6 42.9*; CS106 5/8 × .049
  4130 3.8; CS107 3/4 × .058 6061-T6 0.75; CS110 1/2 × .035 2024-T3 39.2*; CS112 3/8 × .065 4130 0.8
  ×2; CS115 5/8 × .049 4130 4.2; CS116 3/4 × .058 6061-T6 4.4; CS119 5/8 × .049 4130, 4.1 (see
  Conflicts); CS121 3/4 × .058 6061-T6 29.5*; CS122 5/8 × .049 4130 2.6; CS125L 1/2 × .035 31.7*;
  CS126L 1/2 × .035 19.6*; CS129L 1/2 × .035 9.1 ×2; CS131 3/8 × .065 4130 0.65 ×2; CS202 3/8 × .065
  2024-T3 0.4 ×2 (Roncz BOM lists three); CS201 5/16 × .031 4130 0.1 ×2.
- Other: CS124 0.050 steel, CS1 insert ×10 (CS1A ×2 for 1/4-28), CS181 quick disconnect ×3, CS17
  spacer 5/16 OD × 3/16 ID × 0.25 ×4, Nylaflow 3/16 OD × .025 wall, two 82 in lengths; 3/32 7×19
  cable two 10 ft lengths; 1/16 7×7 cable 13 ft per side, 8 in from the pulley.

**Ch17:**
- `{cloth: BID, plies: 1, where: "over PT1 on the left fuselage side, 1/2 in lap"}`
- `{cloth: BID, plies: 1, where: "over RT3 on the right console and side, 1/2 in lap"}`
- Stock: PT1 and RT3 1/4 birch; PTH 1/8 2024-T3; RT1 and RT2 0.049 4130; four phenolic PW 1/16 × 0.5
  OD; two 20 in 1/16 7×7 cables; springs PTS (2), RTS (2), CS (2); 0.041 safety wire.

## Geometry (`plans-1980:p<pdf page>`; cobelu figures marked "cobelu")

### Centre-section spar (chapter 14)

| Item | Value | Citation | Status |
|---|---|---|---|
| Overall span (BL) | ±56.46 (112.92 total); jig length 112.92; end bulkhead at BL 56.46 | plans-1980:p88, p89 | dimensioned; two views agree |
| Forward face FS | 118.5 for BL 0 to 23; FS 123.54 at BL 56.46 | plans-1980:p88 (top view) | dimensioned |
| Aft face FS | 125.0 for BL 0 to 23; FS 129.9 at BL 55.5 | plans-1980:p88 (top view), p91 (FS 125.0) | dimensioned; the aft end digit "129.9" is hand-lettered, medium-high; my arithmetic gives 129.9 |
| Sweep kink and angle | kink at BL 23; outboard 8.57° | plans-1980:p88 | dimensioned (centre 23.0 labelled); angle checks: 5.04 / 33.46 = tan 8.6° |
| Chord (fore-aft) | 6.50 at the centreline; 6.43 square to the outboard face | plans-1980:p88, p91, p92 | dimensioned; 6.50 × cos 8.57° = 6.43 checks |
| Face lengths outboard of BL 23 | forward 33.834, aft 32.865 | plans-1980:p88 | dimensioned; both check against sweep |
| Depth at centre | 8.50 (WL 22.0 to 13.5) | plans-1980:p88 (view from aft), p91 | dimensioned |
| Top surface | flat WL 22.0 to BL 25, then tapers aft; WL 22.0 and 21.7 labels at the outboard end | plans-1980:p88, p85 text | dimensioned; the 21.7 label is the outer-end top aft corner, medium |
| Bottom surface | flat WL 13.5 to about BL 9, then rises to WL 15.15 at BL 56.46 (my arithmetic: about 2°) | plans-1980:p88, p86 text | dimensioned; BL 9 is printed as a tick and in text |
| End bulkheads CS5, CS8 | 6.30 wide × 6.83 tall | plans-1980:p90 | dimensioned |
| Inboard attach hard point | BL 25.0, WL 20.25 (one bolt per wing) | plans-1980:p88, p91, p85 ("LWA1 centre must be at BL 25.0") | dimensioned |
| Outboard attach hard point | BL 53.5, WL 20.5 and 16.3 (two bolts per wing) | plans-1980:p88, p92 | dimensioned |
| Attach bolt FS | not printed. Bolts are drilled to 5/8 with the wing in position (p88 note, "three fasteners per wing") | plans-1980:p88 | unsourced; must come from ch19 |
| Hard-point spacing along the aft face | 28.82 | plans-1980:p88 | dimensioned; (53.5 − 25) / cos 8.57° = 28.82 agrees |
| LWA placement sketch labels | 29.84, 2.0, 1.0, 1.5, 2.0 (p85 step 6) | plans-1980:p85 | hand sketch; which labels span what is unclear; low. Outboard LWA1 setback changed by CP25 LPC 28 |
| Spar cap width | 3.0 UND tape | plans-1980:p85 | dimensioned |
| Top cap | 12 plies; 4 full span; ply ends at BL 15, 20, 25, 30, 35, 40, 45, 50, 55.5; about 0.450 thick at centre, about 0.150 at the end | plans-1980:p86; CP32 | dimensioned; 12 × 0.0375 = 0.45 checks |
| Bottom cap | 9 plies; 3 full span; ply ends at BL 13, 20, 27, 34, 41, 48, 55.5; about 0.338 centre, 0.113 end | plans-1980:p86; CP32 | dimensioned; 9 × 0.0375 = 0.3375 checks |
| Cap strip lengths | top sum 972, bottom sum 705, total 1677 | plans-1980:p85 | dimensioned; sums check |
| Cap trough outline on the aft face | marks 0.50, 0.40, 0.55, 0.16, 0.39 with 10, 15, 13 along the span | plans-1980:p85 (14-2 top-right sketch) | hand sketch, medium; CP32 confirms the 0.55 and says the sketch is correct |
| Aft shear-web layup | 3 BID at 45°; under both caps; full span | plans-1980:p85; p86 UND option | dimensioned |
| Cap trough templates | eight templates on A11 | plans-1980:p85 | template only (A-sheet) |
| Spruce engine-mount blocks | 1 × 1 × 3, BL ±7.5, top and bottom (four) | plans-1980:p86 | dimensioned |
| Baggage hole | forward face, 14 long (7 each side of centre), 5 high, rounded outboard corners, top at about WL 20 | plans-1980:p87, p88 | dimensioned; WL 20 is a hand tick, medium |
| Nut access hole | 2 1/4 dia through the bottom at BL 53.5 | plans-1980:p87, p92 | dimensioned |
| Interior bulkheads CS6, CS7 | 27 in from centreline, square to the aft face | plans-1980:p84 text | dimensioned |
| Foam parts | CS1 centre 46 long (23 each side), 8.41 high at centre to 7.94 at BL 23, 6.83 at the ends; outboard 32.62 | plans-1980:p90 | dimensioned |
| Spar jig | upright 12.5 wide strip, 6.12 high at centre, 6.05 at the ends, 5.04 diagonal drop; shelf parts 8.41, 7.94, 6.83 | plans-1980:p89 | dimensioned (jig only) |
| EM12 | 8.0 long, 1 × 1 × 1/8 angle, four; extends 1.6 aft of the firewall | plans-1980:p87 | dimensioned |
| W16 spruce wedge | 1.0 high, 8.2 long (2 + 6.2), 0.3 thick end, four | plans-1980:p87 | dimensioned |
| SH1 aft harness plate | 2.3 × 0.7, 1/4 holes 1.6 apart, two | plans-1980:p87 | dimensioned; station labels 3.5, 3.4, 1.9 on the isometric are low confidence |
| Datum for main gear | aft face at BL 26.75, FS 125.5, axle FS 110.5 (15 forward) | plans-1980:p50 | dimensioned |

### Firewall and accessories (chapter 15)

| Item | Value | Citation | Status |
|---|---|---|---|
| Firewall station | FS 125 (line in the K-K and side views; FS 124 and 123 label the torque-tube end, FS 127 and 128 aft) | plans-1980:p101 | dimensioned |
| Torque-tube firewall hole | BL 6.2R, WL 12.3, 1 in dia | plans-1980:p98 text, p101 | dimensioned; two sources agree |
| Rudder/brake belcrank vertical position | between about WL 9 and 11 near the firewall bottom (ticks on the right half of p101 read as WL 9, 10, 11, 14, 15, not negative; the cables run at WL 8) | plans-1980:p101, p103 | low confidence, scale ticks only |
| CS15 belcrank | 1/8 plate, 1.6, 1.85, 1.40, 1.35 spans, 0.8R and 0.95R lobes, #12 and 1/4 holes | plans-1980:p95 | dimensioned; "0.95R" is medium |
| CS71 bracket | 0.064, 1.9 high, 0.5R top, 1/4R bend, two #10 | plans-1980:p95 | dimensioned |
| CS72 pulley bracket | 0.032, bent 29°, three #10 holes matching firewall studs | plans-1980:p95 | dimensioned; "29°" medium |
| Brake arm BA | 1/8, 5/16 dia, #10 and 1/4 holes | plans-1980:p95 | pattern only |
| Master cylinder | upright, between the upper and lower engine-mount fittings; no stations printed | plans-1980:p96 | unsourced stations (A4) |
| CS75 | 5/16 OD × 1/4 ID × 0.15 | plans-1980:p96 | dimensioned |
| Firewall outline | on A4, not held | plans-1980:p95 | template only; CP27 LPC 48 makes it taller at the top |

### Control system (chapter 16)

| Item | Value | Citation | Status |
|---|---|---|---|
| Front pivot plane | FS 45.5 (CS107/CS108/CS109 end, labelled on the drawing) | plans-1980:p100 | dimensioned; medium (label sits near the end of the tube) |
| Rear pivot plane | FS 89.7 (CS117/CS118 plane) | plans-1980:p100 | dimensioned; medium; the arrow points at a vertical line |
| Torque tube | one 5/8-bearing line from FS 45.5 to the firewall; CS105 42.9, CS106 3.8, CS115 4.2, CS116 4.4, CS121 29.5 | plans-1980:p99, p100 | dimensioned; CS121 is trim-to-fit |
| Stick fore-aft positions | not printed; front stick and rear stick pivots sit on CS105 and CS115 | plans-1980:p100 | unsourced FS |
| Stick tilt | 5° inboard at neutral aileron; 5° forward at neutral elevator | plans-1980:p98, p102 | dimensioned |
| Stick roll travel | ±20° from the 5° cant; aileron torque tube ±20° for ±20° aileron | plans-1980:p97, p98 | dimensioned |
| Stick length and rod-end holes | CS103 6.1 long; rod-end bolts 1.6 apart, 1.4 from the pivot | plans-1980:p99, p102 | dimensioned; which dimension spans which bolts is medium |
| Roll pushrod CS110 | 39.2 in (trim to length) between front and rear stick | plans-1980:p99 | dimensioned |
| Pitch pushrods | CS102 12.7, CS136 8.5, CS1A and CS1 inserts, HM4 ends | plans-1980:p99, p100 | dimensioned |
| Elevator arm (GU CS12) | 1.9 between pivot and rod-end bolt (as drawn) | plans-1980:p100 | medium; Roncz uses NC-12A, not read on the scan |
| Elevator travel (GU) | schematic shows 20° up and 22° down | plans-1980:p97 | hand lettering; read as up 20, down 22, medium |
| Elevator travel (manual) | 22° ± 2° up and 22° ± 2° down | om-1980:p29 | dimensioned |
| Elevator travel (Roncz) | about 15° up (12.5° floor), 30° down | cobelu ch30 text, template G | dimensioned |
| Control stops | no pitch stop dimension printed in ch16 or in cobelu ch30; roll stop is the stick against the console | plans-1980:p98; cobelu | unsourced |
| Firewall quick link CS124 | rod-end holes at about WL 14 to 16, torque-tube centre BL 6.2R, WL 12.3; BL labels 4.8, 6.2, 9.2 on tick scales | plans-1980:p101 | low confidence for the BL 4.8 and 9.2 features |
| Rudder conduits | 82 in long at WL 8, four bulkhead holes | plans-1980:p103 | dimensioned |
| Rudder travel | top trailing edge 6 in outboard (30°); 0.7 in overtravel at firewall and tip | plans-1980:p104; om-1980:p29 (6 ± 0.5) | dimensioned |
| Adjustable pedal hardware | about 8 in forward of the panel | plans-1980:p104 | dimensioned |
| Console geometry | front 30.1 long, 3.5 top width, side 9.1 high; rear 25.8 long, 3.1 wide, side 8.0 and 3.0; stick opening 6.0 and 5.0 | plans-1980:p97 | dimensioned; hand digits, medium; drawing is marked as 1/10 scale |
| Bearing stock | oil-impregnated bronze flanged, 5/8 bore (Boston FB1013-8) | plans-1980:p98, p101 | dimensioned |

### Pitch and roll trim (chapter 17)

| Item | Value | Citation | Status |
|---|---|---|---|
| Panel face | FS 40 | plans-1980:p106 | dimensioned (manual and model use 40 and 39.75) |
| PTH pivot / PT1 | pivot hex at WL 8.6 (14.4 below the top of the longeron, WL 23), lower friction bolt at WL 7.1 (1.5 below) | plans-1980:p106 | dimensioned; both agree; medium for which bolt is which |
| PTH leftmost end | FS 49.8 label, with a 9.5 in dimension from the panel | plans-1980:p106 | 40 + 9.5 = 49.5, not 49.8; see Conflicts |
| Pitch cables | two 20 in 1/16 7×7; swage at 5.6 (upper) and 6.2 (lower) from the panel sleeve | plans-1980:p106, p105 | dimensioned |
| Cable sleeve positions | BL 9.5; WL 9.6 (upper), 8.3 (lower) | CP25 addendum to CP24; cobelu ch17 | CP-corrected, not on the scan |
| PTH | 1/8 2024-T3; 5.2 long, 2.3 and 2.4 hole spacings, 1.5R and 0.375R lobes, 0.25 arc slot, 90° | plans-1980:p107 | dimensioned; one or two hand decimals, medium |
| Springs | PTS 0.350 OD, 0.05 wire, 6.0 free, 9.0 installed, two; RTS 2.0 / 3.0, two; CS 0.5 / 0.25, two | plans-1980:p105 | dimensioned |
| Trim authority | hands-off 60 kt at aft trim, 170 kt at forward trim | plans-1980:p105 | dimensioned (as text) |
| Spring shortening | one PTS up to 1 1/2 in shorter | plans-1980:p105 | dimensioned |
| Elevator bracket (GU) | PTB on the elevator arm, left side; chapter 11 | plans-1980:p105 | GU only; the cobelu ch11 figure is not on the scan |
| Elevator bracket (Roncz) | NC-5A belcrank on the left tube inboard end, replaces NC-12A; 12 pop rivets; label BL 9.2 (left) | cobelu ch30, fig C-1 | dimensioned; medium (rotated figure) |
| Roll trim | RT1 and two RT2 on CS105 left of the right console; RT3 notched 1/4 × 1; slot marked "Lt--Roll Trim--Rt" | plans-1980:p105, p107 | patterns; no stations |
| Fixed tab (optional) | 1.2 × 10 × 0.02 aluminium | plans-1980:p105 | dimensioned |

Hand-digit notes:
- p88 "129.9" and "123.54": hand-lettered; both check against the 8.57° sweep.
- p88 WL labels 20.25, 20.5, 16.3, 15.15: all legible. WL 21.7 at the outboard top is the smallest.
- p85 "29.84": cannot say what it spans. Treat as low.
- p101 BL ticks 4.8 and 9.2, and the WL ticks on the right half. Low.
- p104 footer page number is smudged; confirmed 16-8 from sequence.

## Spar geometry arithmetic

- Sweep from the printed numbers: (123.54 − 118.5) / (56.46 − 23) = 0.1506, which is 8.57°.
- Aft face FS at BL b (b > 23): 125 + 0.1506 (b − 23). At BL 25 this is 125.30, at BL 26.75 it is
  125.57, at BL 53.5 it is 129.3, at BL 55.5 it is 129.9.
- Mid-chord FS at BL 0 to 23: 121.75. Spar volume is symmetric in BL.
- The spar cutout in the sides (6.5 wide, 8.5 deep; p36) matches the spar section (6.50 × 8.50).
- The current config note "p88 forward face implies a 7 in spar" is wrong: p88 prints 6.50 at the
  centreline. The 7 in cannot come from 125.5 − 118.5, because 125.5 is a swept, outboard station.

## Mass notes

- **Book weight:** centre-section spar 29 lb 5 oz, weighed on the prototype (CP26 p2). It is the
  BID version of layups 5, 6 and 8 (that list predates the option table). It is part of the 183 lb
  complete fuselage figure.
- **UND option:** the plans-era option says it saves about 3 1/2 lb (cobelu ch14, CP25 LPC 26).
  Derived: 29.3 − 3.5 = about 25.8 lb. My arithmetic, uses the printed saving.
- **Dry-cloth mass of the caps (my arithmetic):** 1677 in × 3 in = 5031 in², 3.88 yd². At 7.02 oz per
  yd² (wicks-ra5177) that is 27.3 oz or 1.70 lb dry. Resin content is unsourced, so do not turn it
  into a cured cap mass.
- **Foam (my arithmetic, rough ±15%):** PVC R100 at 6 lb/ft³: CS1 about 0.74 lb, CS4 about 0.76 lb,
  bulkheads about 0.15 lb. Urethane at 2 lb/ft³: CS2 plus CS3 about 1.57 lb (6 in wide, carved
  away at the depressions). Total foam about 3.2 lb.
- **Metal (my arithmetic, 2024-T3 at 0.100 lb/in³ from general reference):** the ch14 pieces (six
  LWA1, two LWA2, two LWA3, four LWA4, two LWA5) are 11.7 in³, about 1.17 lb as printed. With the
  CP43 LPC 119 sizes for LWA4 and LWA5 it is 12.45 in³, about 1.25 lb. EM12 (four) about 0.75 lb.
  SH1 about 0.04 lb each (small).
- **Centroid of the spar (my arithmetic):** WL about 17.75 at the centreline mid-depth (22 and
  13.5). FS about 123 if mass is uniform over span (mid-chord 121.75 plus the swept outboard half);
  inboard-heavy caps pull it a little forward. Treat as a ledger placeholder, not a source.
- **Control torque tubes (my arithmetic, 6061-T6 at 0.0975 lb/in³):** CS105 about 0.53 lb, CS121
  about 0.36 lb; CS110 (2024-T3, 0.035 wall) about 0.20 lb. Steel tubes and rod ends not computed.
- **Unsourced:** stainless firewall, plywood firewall and insulation, consoles, CS15 and brackets,
  brake master cylinders, sticks and grips, NC-5A, springs, cables, conduits. Leave them
  `unsourced`.
- **Dependent mass limit:** wing attach weight and the aft CG limit depend on the 29.3 lb spar
  and on where the bolts sit in FS, which the plans only give with the wing.

## Canard Pusher changes

| Issue | Change |
|---|---|
| CP25 LPC 19 (A4) | engine-mount extrusions reference chapter 14, not chapter 6 |
| CP25 LPC 26 (OPT) | UND option for spar layups 5, 6 and 8; saves about 3.5 lb |
| CP25 LPC 28 (p14-2, step 4) | outboard LWA1 setback measured outside CS5 and CS8; use 0.75 |
| CP25 builder hint (ch14 step 13) | kink in the spar fouls the aft seat bulkhead; saw a wedge out, re-bond it. For new work, leave the plywood firewall unbonded until the spar is in |
| CP25 spar-cap note | if cloth bulks 0.025 per ply, add plies; top add 6, bottom add 4, with BL ends given |
| CP25 caution | do not carve the cap troughs too deep (ch14 step 5) |
| CP25 addendum to CP24 p11 | trim-cable nylon sleeves at BL 9.5, WL 9.6 and 8.3 |
| CP26 LPC 29 (p16-3) | CS119 is 4.1 in, not 3.1 |
| CP26 LPC 40 (p16-3) | jam nut not supplied; a tapped MS21042-3 nut will do |
| CP27 LPC 47 (DES) | left rudder pulley bracket 0.6 higher; or bend 0.2 aft |
| CP27 LPC 48 (DES, firewall A4) | firewall taller at the top for cowling room |
| CP20 (pitch rod ends) | primary pitch rod ends are HM-4, CS201 and CS202 spacers; already in the 1980 print (p99 Detail A note) |
| CP32 clarification (p14-2 sketch) | the 0.55 trough dimension is correct; caps are 0.150 (top) and 0.113 (bottom) thick at the ends |
| CP32 LPC 95 (DES, p16-2 step 3) | open the pivot holes with a letter U drill and a 3/8 press-fit reamer |
| CP32 LPC 99 (DES, p14-10/14-11) | UND layups 3 and 4 do not lap onto CS7 and CS8; see E-E, F-F, G-G, H-H |
| CP36 LPC 111 (MEO, p16-4) | CS120 universal is MS20271-B10, not AN271-B10 |
| CP36 LPC 112 (MEO, p9-1) | Chapter 8 should read Chapter 14 |
| CP43 LPC 119 (p14-7) | LWA4 and LWA5 grow in height (1.75 × 2 and 2.25 × 2) |

No CP entry was found that changes a printed spar station, depth, or the firewall station.

## Conflicts

- **Bottom spar cap strip count:** cobelu prints four 113 in strips; the scan (p85) prints three,
  and the text says first three plies are full span. Only three makes the printed 1677 in total
  work (972 + 705). Follow the scan.
- **LWA4 and LWA5 sizes:** p90 prints 1.5 × 2 and 2 × 2; CP43 LPC 119 enlarges them. The model
  should use the CP-corrected sizes.
- **Outboard LWA1 setback:** p85 shows 1.0; CP25 LPC 28 says 0.75 outside the end bulkhead.
- **Spar chord in the config note:** the config says forward face 118.5 implies 7 in; p88 prints
  6.50. FS 125.5 is the swept aft face at BL 26.75, not an offset from the firewall. The firewall
  and centreline aft face are both FS 125.0.
- **Firewall bonding order:** CP25 says leave the plywood firewall unbonded until the spar goes in
  from the rear; the graph has `f06.bond-firewall` before ch14. Needs a ruling. The existing ch14
  step 13 also says to mark a centreline on the firewall.
- **Hard-point spacing label:** p85 sketch 29.84 against p88 28.82 (the latter checks
  geometrically). Unresolved what 29.84 spans.
- **CS119 length:** p99 table was 3.1, hand-corrected to 4.1; CP26 LPC 29 agrees. Use 4.1.
- **CS202 count:** GU plans list two; the Roncz BOM lists three (one extra 0.4 in spacer).
- **Ch17 FS:** p106 shows FS 40 panel, a 9.5 dimension, and an FS 49.8 label. They differ by 0.3.
- **Trim belcrank station:** the brief says BL 0; cobelu C-1 labels the NC-5A as BL 9.2 (left).
- **Elevator travel:** GU plan schematic 20 up and 22 down (p97), manual 22 ± 2 each way (om p29),
  Roncz 15 up and 30 down. The model must carry a separate Roncz row. No stop is printed for
  the pitch system.
- **Plans edition mismatch:** CP20 hint says four pitch rod ends in ch16; p99 note says ten places,
  four in ch16 and six in ch19. They agree.
- **Pitch trim cable holes:** the scan does not print the BL 9.5 and WL values; they come from CP25
  and cobelu. The scan only gives WL 8.6 and 7.1 for the handle.
- **Cobelu naming:** the transcription says "W16" in text and "WA16" in the figure title; the scan
  figure title reads "WA16" (p87 shows both). Same part.

## Judgement

**Book-true from pages the owner holds:**
- Spar planform: FS 118.5 and 125.0 at the centreline, 8.57° sweep outboard of BL 23, span ±56.46,
  chord 6.50, depth 8.50, face lengths, hard-point BL and WL, cap ply schedule, strip lengths;
- the whole ch14 sequence and BID schedule, SH1, EM12, W16, spruce block positions;
- firewall line FS 125, the torque-tube hole at BL 6.2R and WL 12.3, the ch15 part patterns;
- control-system part list and stations FS 45.5 and 89.7 (medium), stick tilt and roll travel;
- trim handle pivot WL 8.6, cable swage dimensions, spring table.

**Roncz (cobelu, not on the scan):**
- elevator travel 15 up and 30 down, NC-12A and NC-5A, extra 0.4 in CS-202, hinge BLs 9.2 and
  7.7 or 7.8.

**Template-only or unprinted, so representational:**
- spar-cap trough templates (A11), firewall outline (A4), master cylinder and CS73 positions,
  console and stick fore-aft stations, wing attach bolt FS, elevator pitch stops, firewall bearing
  detail beyond the 5/8 bore.

**Top model-bound values (see the reply):** spar forward face FS 118.5, aft face FS 125.0 at
BL 0 to 23 (125.57 at BL 26.75), 8.57° outboard, span ±56.46, depth 8.50 (WL 22.0 to 13.5),
hard points BL 25 and 53.5, firewall FS 125, torque-tube hole BL 6.2R WL 12.3.

**Mass ledger:** only sourced row is the spar at 29.3 lb (CP26, prototype BID layup; about 25.8 lb
with the UND option, derived). Foam, metal and cap-cloth numbers above are my arithmetic and
should be tagged `derived`. Everything else in firewall, controls and trim stays `unsourced`.
