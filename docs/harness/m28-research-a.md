# Strakes, baggage, fuel tanks and fuel system (chapter 21, p141 to p148): source research (2026-10-04)

Read-only research pass for milestone 2.8, crew A. Every number below was read on the page image
(hand digits cropped and enlarged 2x to 4x), not from OCR. 1980 plans cited as `plans-1980:pNNN` (PDF
page). Cobelu transcription cited `cobelu` (ch21 md, diffed against the scan; scan wins). Canard Pusher
text cited `cp-text:CPnn p<page>` (+ LPC number). Owner's Manual cited `om-1980:p<printed>` (PDF page equals
printed page there). Paraphrases are ten words or fewer. Nothing in the repo was edited. The owner holds no
A-sheets: R23 and R45 rib outlines (A14, "shown full size") and the jig-board use (A14, A11) live only
there, so those shapes are marked "repr". The scan note "see back of 20-6" (hand-written on p141) points
at the blank back of p140 (page 20-6); that back is not in the scan.

Status key for the "Model use" column: **book** = printed and cross-checked; **derived** = my arithmetic
(shown); **repr** = shape not printed or A-sheet only; **text** = printed in prose.

## 0. Answers to the leading questions (read this first)

1. Strake LE meets the wing LE at BL 58, FS 113.9. Confirmed from two sides: plans-1980:p171 (back cover)
   labels FS 113.4 at BL 58 and carries the hand note "CP25 LCP 7: 113.9 not 113.4" in blue ink, and
   cp-text:CP25 p5 LPC 7 says the same. The M2.7 ruling (113.9) stands. Chapter 21 itself prints no wing LE.
2. Fuel arm 104.5 is verified: om-1980:p26 sample loading rows read Fuel, 240 lb (light pilot) and 150 lb
   (heavy pilot), station 104.5, moments 25080 and 15675. 240 x 104.5 = 25080 and 150 x 104.5 = 15675:
   both match. The same arm is on the blank "YOUR AIRPLANE" tables (p26, p27). The only fuel-weight
   rate printed is 40 gal = 240 lb, so 6.0 lb/gal (om p25 formula "gallons times 6.0" is lb per gallon
   mislabelled as moment; see conflict C4).
3. Independent geometry check of 104.5 (derived, not a fit): the tank plan outline built from p147 labels
   (outboard trapezoid plus inboard sump lobe, vertices in 2.1) has area 946 sq in and an area centroid at
   FS 103.85. That is 0.65 in from 104.5. At a nominal 7.3 in tank height the gross volume is 29.9 gal; the
   printed capacity is 25.5 gal, so the outline is about 15 percent more than the net tank (ribs,
   baffles, rounded edges, tapering height). Order-of-magnitude agreement only.
4. The model's `StrakeConfig.fs_trailing_edge` 99.5 is not a strake TE. The book strake aft boundary is the
   forward face of the centre-section spar: FS 118.5 at BL 23 (p147 label), sweeping aft 8.57 deg
   (see 2.1). 99.5 is the strake LE at BL 45. Likewise "LE FS 50 at BL 0 to 23.3" is wrong in shape:
   the LE is a polyline FS 50 (fuselage side, BL about 12) to FS 73.3 (BL 23) to FS 99.5 (BL 45) to
   FS 113.9 (BL 58), see 2.1.

## 1. Page map (`plans-1980`, confirmed on printed footers)

| PDF | Printed | Content |
|---|---|---|
| p140 | 20-6 | last page of chapter 20 (footer "LAST Pg CHAP 20"); not chapter 21 |
| p141 | 21-1 | chapter 21 title, overview, fuel-system sketch, step 1 start, part drawings TLE, BLE, B23, BAB, OD, DB; hand note (Safe-T-Poxy, top margin, blue ink) |
| p142 | 21-2 | strake skin foam outlines with dimension table A to D, fuselage side cutout dimensions |
| p143 | 21-3 | steps 2 to 5 (jig, inside layups 1 to 4, vent and screen, top skin cores) |
| p144 | 21-4 | step 5 end (layups 5, 6), step 6 (OD rib, 3/8 tube), step 7 (outside bottom, sump blister), step 8 (top skin) |
| p145 | 21-5 | steps 9 to 11, fuel cap section and parts T8-1, T8-2, T8-3, FT-18, fuel valve drawing |
| p146 | 21-6 | section views A-A to I-I (not to scale); footer "Pg 21-6" is rotated on the right edge |
| p147 | 21-7 | plan view of the right strake with stations; footer "Pg 21-7" rotated on the left edge |
| p148 | 21-8 | fuel plumbing at the firewall and engine; footer "PAGE 21-8, LAST Pg, Chap 21"; hand note CP24 LCP 1 |
| p149 | 22-1 | chapter 22 starts (outside this scope) |

Footers read on the images: p141 "Pg. 21-1", p142 "Pg. 21-2", p143 "Pg. 21-3", p144 "Pg. 21-4",
p145 "Pg 21-5". Chapter 21 is exactly p141 to p148 (eight pages), nothing missing between p140 and p149.
Cobelu (ch21) follows the same step order but renumbers figures (21-3 to 21-22) and folds in CP edits;
see section 5.

## 2. Dimensions, stations, angles, materials

### 2.1 Plan view and stations (plans-1980:p147, "right strake", scale not stated; left is a mirror)

Printed labels (read at 1.5x to 1.6x). Station labels and BL labels are the printed ones; the vertex
list in the last block is derived.

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Strake LE at fuselage side | FS 50 (label "F.S.50" at the left end) | plans-1980:p147; p171 also FS 50 | high, large print | `StrakeConfig.fs_leading_edge` 50.0 already agrees | book |
| TLE/BLE kink at BL 23 | FS 73.3 | p147 label "F.S.73.3" above BL 23; p171 label FS 73.3 | high | model note already says 73.3 at BL 23 | book |
| LE at BL 45 (R45 meets TLE) | FS 99.5 | p147 label "F.S.99.5" above BL 45 | high | model note already says 99.5 at BL 45 | book |
| Strake/wing LE at BL 58 | FS 113.9 | p171 print 113.4; CP25 LPC 7 corrects to 113.9; M2.7 ruling | high (see C1) | cp-text:CP25 p5 LPC 7 | book |
| Spar forward face at BL 23 | FS 118.5 (label "F.S.118.5" arrow lands on the B23 end) | p147 | high | B23 length check below (21.2 vs 21.3) | book |
| Spar forward face slope | 8.57 deg aft per BL out (tan 0.1508) | p118 4.9 / 32.5 (M2.7 report); p142 outboard skin edge 4.9 / 32.0 = 8.71 deg | medium (two sources differ 0.14 deg) | derived: spar face FS 121.8 at BL 45, 123.4 at BL 55.5, 123.8 at BL 58 | derived |
| Fuselage-side cutout aft edge / BAB inboard end | FS 103.5 (label "F.S.103.5") | p147 | high | sump blister FS 103.5 to 125 | book |
| Sump blister aft end | flush with the firewall, firewall FS 125 | p144 note "flush with firewall on aft end"; p171 label FS 125 | high | derived: blister 21 in long from FS 103.5 gives FS 124.5, within 0.5 | derived |
| Fuel tank sump outline | dashed arc from FS 103.5 to about FS 125 on the fuselage side | p147 | medium (dashed, scaled) | blister length 21 (p144) | repr |
| 1.25 in hole (screen) in inboard bottom skin | near the aft inboard corner, about FS 117, BL 13 (scaled off the image, plus or minus 1 in) | p147, p143 step 2 "see page 21-7" | medium-low (scaled) | p143 step 4 "dome screen over the 1 1/4 hole" | derived |
| Water drain (step 2) | at the forward corner where TLE/BLE meet R23, about FS 75, BL 22.5 (scaled) | p147 label "WATER DRAIN STEP 2" | medium | OM p8 "one in the leading edge of each strake" | derived |
| "DRAIN (STEP10)" | on the bottom skin between OD and R45 near the LE, about FS 100, BL 44.5 | p147; p145 step 10 says a 1/4 hole, vents the area and drains moisture | medium | not a tank drain (outside the tank between OD and R45); see C11 | text |
| Rib R23 | along BL 23; labelled "23 LONG" (hand print) | p147 | medium (print is small) | derived: FS 73.3 to the DB/B23 junction (about FS 97.3) is 24.0, 1 in more than the label | derived |
| B23 (BL 23 baffle) | along BL 23 from the DB junction (about FS 97.3) to the spar face FS 118.5 | p147, p141 length 21.3 | high | derived: 118.5 - 97.3 = 21.2 vs printed 21.3 | derived |
| R45 (BL 45 rib) | along BL 45, TLE (FS 99.5) to the spar face | p147 | high | derived length 121.8 - 99.5 = 22.3 | derived |
| DB (diagonal baffle) | from the R23/B23/BAB junction (FS about 97.3, BL 23) to the R45/spar corner (about FS 115, BL 45) | p147, p141 length 28.5 | medium | derived: sqrt(17.8^2 + 22^2) = 28.3 vs printed 28.5 | derived |
| OD (outboard diagonal) | from the TLE/R45 corner (FS 99.5, BL 45) to the spar face near BL 54 to 55 | p147; p141 gives only width figures (see 2.2) | medium-low (no length printed) | CP30 p6: trim OD if the top does not match the wing | repr |
| Spar-face edge of the outboard skin | 32.0 long, 4.9 aft offset (spar edge from BL 23 to about BL 54.6) | p142 | high | derived: sqrt(32^2 - 4.9^2) = 31.6 BL span, 23 + 31.6 = 54.6, near the BL 55.5 foam joint (wing root); 0.9 in short | derived |
| "CG RANGE" bar | printed as a bar from about FS 98 to FS 103 on the FS scale | p147 | medium (bar ends read from image) | matches om-1980:p28 envelope FS 97 to 103 (97 fwd, 103 aft) | text |
| Section cut letters | A-A across the spar face, B-B across the LEs, C-C and G-G along the fuselage side, D-D across R23/R45/BAB, E-E across B23/DB, F-F across OD, H-H at the sump, I-I at the water drain | p147 | high | p146 sections | text |
| BL axis ticks | BL 10, 20, 30, 40, 50 on the right edge; BL 20, 23, 30, 40, 45, 50 on the left | p147 | high | used for the scaling above | text |

Derived planform vertices (FS, BL), right strake, for the captain's outline (all derived by scaling labels
above; the p147 drawing is a plan view with no stated scale, so interior points are plus or minus 1 in):

- LE: (50, 12.1) fuselage side, (73.3, 23), (99.5, 45), (113.9, 58). Fuselage side BL scaled off the image
  at FS 50 is about 12; at FS 103.5 about 11.3. The OM cabin width 23 in supports a half-width near 11.5.
- LE slope inboard of BL 23: 23.3 FS per 10.9 BL (about 25 deg from the FS axis toward the BL axis);
  BL 23 to 45: 26.2 FS per 22 BL (40.0 deg); BL 45 to 58: 14.4 FS per 13 BL (42.1 deg); BL 23 to 58 as a
  single line: 40.6 FS per 35 BL (40.8 deg). The LE is therefore not straight from FS 50 to BL 58; the
  outboard fairing block (step 10, "flat" LE) fills the difference. CP30 LPC 84 says the LE
  flats get a urethane block.
- Aft boundary: spar forward face from (118.5, 23) sloping aft 0.1508 FS per BL (123.4 at BL 55.5).
- Tank plan area: outboard trapezoid (73.3,23) (99.5,45) (121.8,45) (118.5,23) = 742.7 sq in, centroid
  FS 102.45; inboard lobe (97.3,23) (118.5,23) (116.8,11.3) (103.5,11.3) approximately 203 sq in, centroid
  FS 108.96; total 946 sq in, centroid FS 103.85.
- Baggage plan area per side: (50,12.1) (73.3,23) (97.3,23) (103.5,11.3), 441 sq in, centroid FS 80.6,
  about 1.9 cu ft at a constant 7.3 in height (less in practice: the cutouts are 4.0 to 6.55 high at the
  front). OM W&B baggage arm is 90 (conflict C2).

### 2.2 Part drawings (plans-1980:p141), "drawings not to scale", all type 45 PV core, 0.35 in thick

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Foam | type 45 PV (R45), dark blue foam, 0.35 in thick | p141 note; p141 overview says "type 45R" | high | ledger R45 3 lb/ft3 (CP34 table, cited in the mass ledger) | text |
| TLE (fuel tank LE) | 33.5 long x 2.55 wide, 90 deg corners | p141 | high (printed, crop 2.5x) | derived LE run sqrt(26.2^2 + 22^2) = 34.2, ends bevelled | book |
| BLE (baggage LE) | 25.5 long x 2.55 wide, 90 deg corners | p141 | high | derived sqrt(23.3^2 + 10.9^2) = 25.7 | book |
| B23 | 21.3 long x 7.3 high; 90 deg corners; four notches radius 0.8 (top) and 1.3 (bottom); notch centres 2.0 from each end | p141 | high on 21.3, 7.3; medium on 0.8R vs 1.3R (small print) | derived 21.2 on p147 | book |
| B23 oval hole | 5 long x 3 high, 3 in from the right end, 3 in clear of the bottom edge; lets the outlet screen be seen from the cap | p141 | medium (hand digits, "5 - 3") | text beside the hole | book |
| B23 vent-line hole | 1/4 in (printed 1/4"), near the forward upper corner | p141 | medium | step 4 vent line is 1/4 aluminum | text |
| BAB | 13.4 long; 7.3 high at the outboard end, 7.75 high at the inboard end ("INBOARD" label); 90 deg corners | p141 | high on 13.4, 7.3; medium on 7.75 | derived (97.3,23) to (103.5,11.3) = 13.2 | book |
| OD | outline "to match tank outside contour in step 6"; hand-printed 8 (aft width, blue ink), 1.0 margin top and bottom, oval hole 4.0 deep at the forward end, 1.5 and 1.5 near the aft end | p141 | medium-low (hand digits, "1.5 1.5", "8" in blue ink looks later) | CP30 p6, CP33 LPC 102 | repr (outline shape A-sheet or fit-to-skin) |
| DB | 28.5 long; 7.3 high at the fore end, 6.5 high at the aft end; four notches "same as B23" | p141 | high on 28.5, 7.3; medium on 6.5 | derived 28.3 | book |
| R23 and R45 | "see pg A14", shown full size there | p141 | n/a | cp-text:CP25 p4: align RB45 and RB23 parallel to the BL | repr (A14 only) |
| Rib heights on the jig | WL 17.4 mark on R45 is 2.65 above the table; on R23 it is 3.45 above | p143 step 2 | high (typed) | derived: 0.80 drop over 22 BL gives atan(0.8/22) = 2.08 deg; ties to the strake bottom following the spar bottom | derived |
| Jig board | 35 x 1.45 x 2.15 wood or foam, supports lower-skin LE full span | p143 step 2 | high (typed) | cobelu same | text |
| Jig table | flat table or 4 x 4 ft plywood flush with the spar bottom; longerons level (WL 23 top of longeron per p142) | p143, p147 "Jig table (step 2): level to fuselage longerons, butt to bottom of spar" | high | p142 "WL 23" | text |

### 2.3 Strake skin foam outlines and cutouts (plans-1980:p142)

Skins (all type 45 PV 0.35 in; 6 sheets of 32 x 48 needed for the set per p143/cobelu step 1; sheet size is
in the cobelu step 1 prose and on p141 step 1 text "6 32" x 48" sheets").

| Item | Top skin | Bottom skin | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|---|
| Outboard skin A | 23.9 | 23.7 | p142 table | high (printed hand digits, crop 1.6x) | n/a | book |
| Outboard skin B (bottom edge) | 44.3 | 44.1 | p142 table | high | equals C | book |
| Outboard skin C (inboard skin top edge, same length) | 44.3 | 44.1 | p142 table | high | | book |
| Inboard skin D (length along fuselage) | 67.2 | 67.0 | p142 table | high | derived: spar face at fuselage FS 116.8 minus FS 50 = 66.8, within 0.2 | book |
| Bevel | top and bottom bevels are mirror: 1 in wide, Section X-X | p142 | high | the 0.2 difference in the table is this bevel offset | text |
| Outboard skin height at the kink | 22.4 | 22.4 | p142 | medium (figure not to scale; kink height does not scale to the 32.0) | text |
| Outboard skin spar edge | 32.0 along the bevel; offset aft 4.9; 90 deg at the aft corner | p142 | high | derived 8.71 deg | book |
| Inboard skin heights | 10.8 (forward end), 10.7 (start of C), 11.1, 13.0 at the spar end; 25 between the 11.1 line and the spar end | p142 | high on 13.0, 25; medium on 10.7, 10.8, 11.1 | derived BL span fuselage to BL 23 is about 11.7, plus overlap | text |
| "Curve should match fuselage" | the inboard skin bottom edge follows the fuselage side | p142 | text | | repr |

Fuselage side cutout (p142 lower drawing; "horizontal dimensions are distance to FORWARD face of spar;
vertical dimensions are to top of longeron (WL 23)"; left side shown, right similar; cutout lines are
the inside and outside of the tank skin, 0.35 apart):

| Hole | Station forward of the spar face (in) | Top-edge depth below WL 23 | Bottom-edge depth below WL 23 | Conf |
|---|---|---|---|---|
| Forward (baggage) hole | 65.8 | 4.0 | 6.55 | medium (forward end labelled "4.0" and "6.55") |
| | 63 | 2.9 | 7.35 | high |
| | 60 | 2.15 | 7.9 | high |
| | 56 | 1.7 | 8.45 | high |
| | 52 | 1.55 | 8.8 | high |
| | 47 | 1.45 | 9.05 | high |
| | 42 (aft edge flush with the front seat bulkhead face) | 1.40 | 9.1 | medium (a first look read the top as 1.90; the 2x crop reads 1.40) |
| Reference lines between the holes | 35 | 1.40 | 9.15 | medium |
| Aft (tank) hole | round forward end begins at 30.0; aft edge at 15.0 | 1.40 at mid, 1.90 near the aft end | 9.15 at both | medium: the aft-end "1.90" differs from "1.40" in the same drawing; crop reads both clearly (C14) |
| Fuel sight gauge | 0.5 aft of the aft edge; strip drawn dashed at the aft end | n/a | n/a | medium (gauge cut-out width about 0.7 per cp-text:CP24 p4) |

Derived check for the sight gauge: spar forward face at the fuselage is about FS 116.8 (118.5 minus
11.5 x 0.1508). The aft edge at 15.0 forward is FS 101.8, the gauge 0.5 aft is FS 102.3 to about 103.0,
and BAB meets the fuselage at FS 103.5. The gauge therefore sits against BAB; p147 draws "FUEL GAUGE" at
that corner. Forward hole stations in FS: 65.8 gives 51.0 (agrees with LE FS 50 at the fuselage plus 0.35
core), 42 gives 74.8 (front seat bulkhead face). Vertical dimension 9.15 below WL 23 places the lower
cut at WL 13.85; 1.40 places the upper cut at WL 21.6.

### 2.4 Jigging, layups, ply schedule (plans-1980:p143, p144, p146; cobelu diffed)

Ply-numbered schedule (sections on p146 label the layers 1 to 9):

| Layup | Ply schedule | Where | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|---|
| 1 | 1 ply BID, wet | whole fuel area inside, lapping 1 in up the fuselage side and the spar, fully onto both ribs, TLE and BAB; joints lap 1 in | p143 step 3; sections A-A, B-B, D-D, G-G | high (typed) | cobelu same | book |
| 2 | 1 ply BID each side of B23 and DB, lapping onto the bottom; B23 first so its glass laps onto the outside face of R23 | p143 step 3; section E-E | high | cobelu same | book |
| 3 | 1 ply BID on the outside face of R45, also covering the bottom skin and lapping 1 in onto the spar; plus a 2 in strip of 2 plies UND along the outer diagonal edge of the bottom skin, 1 in onto the spar, fibres along the long (22 in) dimension; plus 1 ply BID on the baggage floor lapping onto R23, BLE, BAB, fuselage and the sight gauge | p143 step 3; sections D-D, B-B, C-C, G-G, F-F | high on plies; medium on "22" (C15) | cobelu same | book |
| 4 | 1 ply BID on the inside of the top skin plus a 2 in strip of 2 plies UND at the outboard diagonal (section F-F); leave 1 in of BID dry along the inboard edge; cure only about 2 to 4 hours, still tacky | p143 step 5; sections A-A, F-F | high | cobelu same | book |
| 5 | tapes, 1 ply BID, joining the top to R45, R23 and BAB | p144 step 5 end; section D-D | high | cobelu same | book |
| 6 | 1 ply BID tape at section C-C; also 1 ply BID over any bare foam edge around the fuselage cutouts | p144; section C-C | high | cobelu same | book |
| 7a (printed "layup 7", step 6) | 1 ply BID on the inside of OD, floxed in with nails; should connect to the spar at the aft end of OD | p144 step 6; section F-F | high; but number clash (C5) | cp-text:CP33 LPC 102 rewrites this passage | book |
| 7b (printed "layup 7", step 7) | outside bottom skin: first ply UND over the whole strake, fibres parallel to the tank LE; second ply UND over the whole strake, fibres fore-aft; laps 4 in onto the spar, 3/4 in onto the fuselage, fully down the TLE and BLE faces and half way down OD; butt joints; third ply a 5 in UND strip (hand-lettered in capitals, blue-black ink) along the diagonal | p144 step 7 plus the sketch labels "FIRST PLY UND ENTIRE SURFACE", "SECOND PLY UND ENTIRE SURFACE", "THIRD PLY UND, 5 in", dimension 4 in | high on the first two plies; medium on the third ply (hand addition, matches CP28 LPC 59) | cp-text:CP28 LPC 59 says the third-ply outside strip was omitted from section F-F | book |
| 8 | sump blister: wet flox plus a 1 in wide tape of 1 ply BID all around | p144 step 7; section H-H | high | prefab blister "SB" is 3 ply BID | book |
| 9 | outside top skin: like layup 7b, plus a fourth ply UND on the left only (top of left strake) for stepping on the strake into the aft cockpit; peel ply the edges | p144 step 8, sketch "FORTH PLY UND TOP OF LEFT WING ONLY"; "layup 7 + 9" | high | cobelu same | book |
| 10 (fairing block skin) | solid urethane block (2 lb/ft3), 5-minute epoxy or micro, carved to R23/R45 nose; cobelu and CP30 LPC 84 say 2 plies UND crossing at 45 deg, lapping 1/2 in onto the top and bottom skins and fuselage | p145 step 10 (scan prints only "cross two plies UND"); cobelu; cp-text:CP30 LPC 84 | scan: high; lap 1/2 in only from CP and cobelu | cobelu merges LPC 84 text | text |

Sectional material notes from p146 (all "not to scale"): A-A shows skins butting the spar bevels with micro
(bottom) and flox (top); B-B is the LE section (inside ply 1 or 3, outside 7, top 4 and 9, flox at the top
joint); C-C (upper) shows a wood ledge at the fuselage side top with plies 6, 4, 9; C-C (lower) shows plies
3 and 7 (two drawings share the label, see C6); D-D shows a rib with plies 1, 3, 4, 5, 9 and flox; E-E shows
DB or B23 with ply 2 each side; F-F shows UND 2 in strips (plies "3-UND" bottom and "4-UND" top) lapping
onto the spar and the OD edge; G-G shows the fuselage-side joint with a wood ledge at the top; H-H shows
the sump blister, screen and tube outlet with plies 1, 7, 8; I-I shows the drain insert.

Jigging process figures: skins are heat-formed (1000 to 1500 W hair dryer or heat gun, weighted by 2
boards; CP34 p7 adds boiling-water towels); lumber with Bondo dabs holds the top-skin curve; top core fits
tank walls within 1/10 in (p143 step 5); flox ledge about 1/2 in tall under the top (p143 sketch,
medium); micro to avoid voids; small radius wiped in all corners.

### 2.5 Drain, vent, screen, outlet, sump, caps (plans-1980:p143 to p146)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Drain insert | 1/8 in thick 2024-T3, 1 x 1 in, tapped 1/8-27 NPT before installing; flush; set at the low point for nose-down parking; micro to correct the low point | p143 step 2 (scan prints 1/4-27), p146 section I-I label "1/8 x 1 x 1 alum drain insert" | high on size; 1/4-27 is a misprint | cp-text:CP28 LPC 60 (1/4 to 1/8) | text |
| Drain valve | SAF-AIR CAV-110 or Curtis CCA-1550 | p146 section I-I | medium (small print) | not in OM | text |
| Pressure check | 1500 ft altitude change (0.8 psi per cobelu; scan does not print psi) through a tee on the vent with an altimeter; plug the 3/8 line at the forward cockpit; wait several hours | p145 step 9 | high | cp-text:CP38 p6: mouth only, never a pump; max 1500 ft | text |
| Vent line | 1/4 in aluminium; wet flox both sides of the fuselage hole; vent opening 1/2 in above the top (sketch label "VENT 1/2 ABOVE TOP") | p143 step 4 | medium (label reads "1/2"") | OM p8: vent on the centre fuselage just aft of the canopy, each tank individually vented | text |
| Vent screen | standard hardware-store screen-door aluminium, dome shaped, over the 1 1/4 in hole in the inboard bottom skin (a finger strainer) | p143 step 4 | high | | text |
| Outlet tube | 3/8 x 0.035 1100-O soft aluminium, an eight-foot length from the front cockpit floor (right side) to a 7/16 hole in the fuselage under the tank; extends only 0.4 in outside; wood plug while curing | p144 step 6, sketch 0.4 | high | | text |
| Outlet hole position | hole about 13 in forward of the firewall face and 3.0 in below the tank bottom line on the aft seat bulkhead plane (sketch) | p144 sketch ("3.0", "13") | medium (which edge the 13 ends on is not clear) | derived: firewall FS 125 minus 13 = FS 112 | derived |
| Left tank line | routed aft of the aft seat bulkhead just below the large access hole; both lines run down the right cockpit side | p144 step 6 | high | | text |
| Sump blister | 21 in long, 2.75 deep (side view), 0.5 flange all around; centre symmetric; "5" dimension at the left; section is a 3.5 x 3.5 corner, symmetric about a 45 deg line; prefab "SB" 3-ply BID | p144 | high on 21, 2.75, 3.5, 0.5; medium on 5 | derived length from the p147 arc: FS 103.5 to 125 = 21.5 | text |
| Fuel cap | sealed, locked by a Dzus fastener; 2 in aluminium rim; bored with a 2 1/4 in hole saw; set in the aft half of the tank at the position drawn; "A5-45" Dzus part; O-ring seal; lockwire | p145 | high on hole saw 2 1/4 (small print) | cp-text:CP27 p8 says the cap is not airtight | text |
| Cap parts | T8-1 cap 6061-T6, dia 2.000, 1.980, 1.855, 1.750; height 0.300, lip 0.150, 0.040 sheet, 3/8 slot; T8-3 receptacle 6061-T6, dia 2.50, 2.080, 2.160, 2.000; 0.63 tall, 0.200, 0.380, 0.030; drill 3/32 for the wire; T8-2 wire 0.080 music wire, 2.30 long, 0.2 hook; complete cap assembly part number FT-18 | p145 | medium-high (hand dimension digits, crop 1.8x) | cp-text:CP24 p16 "Brock VariEze fuel cap (FT18)" | text |
| Cap slot orientation | screw slot fore-aft, checked on the pilot's checklist | p145 | high | cp-text:CP28 p8 checklist add | text |
| Cap grounding | cobelu adds a grounding cable inside the tank and an obstruction within a foot of the cap; cobelu cites "CP55 PCS134 MEO" | cobelu only | not in the scan; not found in the CP text (see 4) | cp-text:CP55 p3 describes a ground lug and an internal wire | text |

### 2.6 Fuel system plumbing and parts (plans-1980:p145, p148; plumbing is installation only, no model geometry)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| System | two tanks, selectable, pumped (not gravity); engine-driven pump plus an electric backup; float-type carb | p141 text and sketch | high | OM p8 | text |
| Selector valve | left-right-off, "108HD 1/4 in shut-off valve", on the instrument panel bulkhead; fittings AN818-6D, AN819-6D, AN822-6D, AN816-6D; screws AN3-6A with AN960-10; "left tank goes to right side of valve" (orientation per the drawing) | p145 | medium-high | LPC 96: bracket 0.062 2024-T3, trim handle; cp-text:CP60 p7 new valve orientation | text |
| Valve location | lower front floor, just below the instrument panel | p141 text | high | OM p8 "thigh support centre, aft of the nose wheel window" | text |
| Electric pump | Bendix; mounted high enough for filter removal; AN822-6-2 steel elbows (two places); AN3-6A, AN960-10, MS21042-3 two places | p148 | medium-high | cp-text:CP25 p16 Brock EFB square pump as alternate | text |
| Gascolator | all-metal, lower right of the firewall; AN822-6D, AN816-6D, AN818-6D, AN819-6D; MS21919-DG11 clamp; AN3-13A; spacer SP5 3/8 OD x 3/16 ID x 0.7 long aluminium; drain reached through the air intake | p148 | medium-high | | text |
| Fire sleeve | Aeroquip 303-6 hose with 491-6 fittings, optional -14 fire shield; pressure line AN910-1D | p148 | medium | | text |
| Engine side | Weatherhead 3600x4 male branch tee; AC pump adapter 6470069 and gasket; 0 to 10 lb fuel pressure gauge #82319; hose Aeroquip 303-3, 491-3; AN816-3D, AN912-1D | p148 | medium (small print) | | text |
| Non-pump engines | three candidate systems listed; details promised for CP24 or CP25; hand note CP24 LCP 1 about safetying the pump cap | p148 | high | cp-text:CP24 p5 | text |
| Firewall station | FS 125 (side view label on the back cover) | p171 | high | p144 sump blister flush with it | book |

Weights: chapter 21 prints no part weight. See section 2.7.

### 2.7 Weights and arms (mass closure inputs)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Fuel arm | FS 104.5 (rows read: 240 lb, 25080 and 150 lb, 15675) | om-1980:p26 | high | derived centroid 103.85 (2.1); `fuel_arm_in` 104.5 and ledger agree | book |
| Fuel weight rate | 6.0 lb per gal (40 gal = 240 lb; moment 6.0 x 104.5 = 627 in-lb per gal) | om-1980:p25, p26 | high | model `fuel_density_lb_per_gal` 6.01 | book |
| Fuel capacity | plans: two tanks of 25.5 gal (p141 text); OM p8: "two 28 gallon" tanks and "52 gallon capacity"; CP24 p13 spec table: Max Fuel 52 gal; fuel allowance with two adults 38 gal | plans-1980:p141; om-1980:p8; cp-text:CP24 p12, p13 | high on each printed digit; sources disagree (C1) | model 26 per side, 52 total | text |
| Fuel samples | 40 gal (240 lb) light pilot; 25 gal (150 lb) heavy pilot | om-1980:p26 | high | ledger samples | book |
| Strake baggage limit | structurally 100 lb each side | om-1980:p4 (text spans p4 to p5) | high | | text |
| Baggage arm | station 90 (one row; sample 15 lb heavy pilot) | om-1980:p26 | high | derived strake baggage centroid FS 80.6 (C2) | book |
| Oil | 8 lb at station 140 | om-1980:p25 | high | | book |
| Pilot, passenger arms | 59 and 103 | om-1980:p25, p26 | high | | book |
| Empty (sample) | 730 lb at FS 111.7 (moment 81541) | om-1980:p25, p26, p36 | high | ledger `empty` row | book |
| Typical empty weight | about 750 lb equipped ("normal equipped empty weight is approximately 750") | om-1980:p4 | high | CP24 p13: Empty Basic 710, Empty Equipped 750 | text |
| Main gear arm | 110.5 plus or minus 1 (empty-weighing table) | om-1980:p34, p35 | high | | book |
| Nose gear arm | about FS 19.6 in the sample (reference about FS 20) | om-1980:p35 | high | | book |
| Instrument panel reference | front face FS 40 | om-1980:p34 | high | selector valve sits below it | book |
| CG envelope | forward FS 97, aft FS 103, max gross 1325 lb, 1425 lb takeoff-only with conditions | om-1980:p28 chart (image read) | high | ledger envelope | book |
| Builder weights (N26MS, Melvill), no strakes | complete fuselage with centre section, brake cylinders, nose and main gear, no wing strakes, no canard, no canopy, no engine mount 183 lb | cp-text:CP26 p3 | high | already in the mass ledger as reference only | text |
| Other CP26 p3 weights | wing 46 lb skinned; 51 lb 8 oz to the end of chapter 19; 64 lb complete with winglets and rudder; aileron 5 lb 2 oz; canard 17 lb; canopy 16 lb; centre-section spar 29 lb 5 oz; dynafocal mount 5 lb 3 oz; elevators 3 lb 8 oz and 3 lb 4 oz | cp-text:CP26 p3 | high | ledger has most of these | text |
| N26MS painted weights | wings with ailerons and rudders 64 lb each; wing with winglets, no rudder or aileron 60 lb each; canard with fairing cover 18.5 lb; canopy with hinges 17 lb | cp-text:CP26 p16 | high | | text |
| N26MS empty weights | basic empty 693.4 lb (VFR panel, no starter or alternator, graphite cowl, per plans, includes strakes); with small alternator 698.3; plus Com/Nav/transponder 713.7; with 60 A alternator, starter, battery 761.9; plus avionics 777.3; fully equipped 815.4 | cp-text:CP27 p3 | high | OM 730 sample, 750 typical | text |
| Strake weight | not printed anywhere I could find (plans, CP26 p3, CP27 p3, OM) | | n/a | cannot be derived: BEW 693.4 includes engine, prop, wiring and instruments for which no weights are printed | open question |

Laminate and foam constants already in the ledger (cited there; I did not re-derive): BID 8.8 oz/yd2,
UND 7.02 oz/yd2, resin about half the cloth weight (best case), R45 foam 3 lb/ft3. Derived areal weights
with those constants: BID plus resin 0.000637 lb/sq in; UND plus resin 0.000508 lb/sq in; 0.35 in R45 foam
0.000608 lb/sq in. A strake bottom skin by the plans schedule (inside ply 1 BID, outside 2 UND, foam 0.35)
is therefore about 0.00226 lb/sq in, 0.325 lb/sq ft; the top adds the extra UND. The 5 in strip, the 2 in
UND strips and the lap areas are small and left to the captain. These are best-case figures: the plans
state resin half of cloth weight as the target (cited in the ledger).

## 3. Build-order list (op candidates)

Prerequisites name earlier parts; chapter numbers are given only where the page states them.

| # | Op candidate | What is done (paraphrase) | Prerequisites | Jig / fixture |
|---|---|---|---|---|
| 1 | Cut rib and baffle parts | Cut R23, R45, B23, BAB, BLE, TLE, OD, DB | foam sheets; A14 patterns (not held) | none |
| 2 | Cut skin cores | Cut two bottom and two top skin cores | six 32 x 48 PV sheets; skin outlines (2.3) | none |
| 3 | Cut fuselage side holes | Saw the two cutouts in each fuselage side | fuselage sides, front seat bulkhead, spar installed | WL 23 reference board on longerons |
| 4 | Jig and fit | Level the table and longerons, nail parts together | chapter 14 spar (flush with table), fuselage; step 3 | 4 x 4 ft table; 35 x 1.45 x 2.15 jig board; weights |
| 5 | Heat-form skins | Form skin curves with weights and heat | step 2 pieces | two boards, heat gun |
| 6 | Bond parts down | Glue bottom skins, ribs, TLE and BLE with micro | step 4 | table, plastic, grey tape |
| 7 | Cut sump hole, drain insert | Bevel the 1.25 in hole; set the tapped drain plate | step 6 | none |
| 8 | Inside layups 1 to 3 | Glass the tank bottom, B23 and DB sides, floor | step 7 | none |
| 9 | Vent and screen | Install the 1/4 vent line and dome screen | step 8 | none |
| 10 | Top skin cores | Fit and shape the top cores | step 8 cured; wing fit check per CP30 | lumber and Bondo shaping |
| 11 | Top inside layup 4, close tank | Glass top inside, then close it over the tank | step 10 | 2 to 4 people, weights |
| 12 | Tapes 5 and 6 | Tape top to ribs and the fuselage cutout edges | step 11 | none |
| 13 | OD rib and outlet tube | Make OD, glass it; install the 3/8 aluminium line | step 12 | wood plug in tube |
| 14 | Outside bottom skin and sump | Fair, glass layup 7b, bond the sump blister | step 13; turn the airframe over | hard 36-grit block |
| 15 | Outside top skin | Fair, glass layup 9, left-only 4th ply | step 14 | none |
| 16 | Pressure check, repair | Leak test at 1500 ft altitude change; repair | steps 14 and 15 | altimeter on the vent, tee |
| 17 | Fairing blocks | Carve urethane block to rib noses; two UND plies | step 16; wing fitted (p145) | wing on the airframe |
| 18 | Cap installation | Bore the 2 1/4 hole; flox the rim; clean foam chips | step 17; after paint (p145) | 2 1/4 hole saw, vacuum |
| 19 | Fuel valve, pumps, gascolator | Mount the valve, pump and gascolator; plumb | firewall, instrument panel | none |

## 4. CP corrections touching this chapter

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP24 p5 LCP 1 (hand note on p148) | MAN-GRD (printed) | Safety the Bendix pump cap: bend tab 90 deg, #50 hole, 0.032 wire | none |
| CP24 p5 LCP 4 and the VariEze-list line (hand note on p141) | DES | Use Safe-T-Poxy for interior fuel layups and fuselage sides (new construction) | material note only |
| CP24 p4 | none printed | Fuel gauge strip must be optically clear; cut-out about 0.7 in wide if not | sight-gauge width |
| CP25 p4 | none printed | Align R45 and R23 parallel to BL; 5/8 holes in spar by spotface tool | rib attitude (repr) |
| CP25 p5 LPC 7 | MEO | Wing root LE 113.9, not 113.4 (back cover) | M2.7 ruling, already closed |
| CP27 p8 | none printed | Long-EZ caps are not airtight; an airtight cap needs a second vent | text |
| CP28 p8 LPC 59 | MEO | Section F-F: add the third-ply outside UND strip for layups 7 and 9 | ply schedule (7b, 9) |
| CP28 p8 LPC 60 | MEO | Page 21-3: 1/4-27 NPT should be 1/8-27 NPT | text |
| CP28 p9 Q and A | none printed | Do not move the BL 45 rib outboard: aft CG | planform: R45 stays at BL 45 |
| CP30 p6 | none printed | Install wing before the tank top; trim OD to match the wing | fit note |
| CP30 p8 LPC 84 | MEO | Add 2 lb/ft3 urethane LE block, two UND plies at 45 deg, lap 1/2 in | LE shape and mass (small) |
| CP31 p4 | none printed | Tether fuel caps to the cross wire with short chain | text |
| CP32 p5 | none printed | Task Research strakes: remove peel ply; UND strip laps strake onto spar smoothly | text |
| CP32 p6 LPC 96 | MEO | Fuel-valve bracket 0.062 2024-T3; trim valve handle | text |
| CP33 p3 LPC 102 | MEO | Step 6 inside ply one BID floxed, step 7 laps 1 in onto spar forward face | ply laps |
| CP34 p7 | none printed | Boiling-water towels to form the top and bottom foam | text |
| CP37 p2 | none printed | Heavy coat of Safe-T-Poxy inside; tank to the spar face and baggage wall | seal note |
| CP38 p3, p6 | none printed | Pinholes in outboard ribs leak fuel into wing foam; leak check by mouth, 1500 ft | seal note |
| CP48 p2 | none printed | Never merge tank vents; each tank needs its own vent, two if caps are sealed | text |
| CP55 p3 | none printed | Ground lug on the cap ring; internal wire in the tank (cobelu cites PCS134, number not confirmed) | text |
| CP60 p7 | none printed | New fuel valve fits the original bracket; same left-right orientation | text |

The CP text carries class labels only in the digest and the LPC lists; where the class is blank it says
"none printed". The digest list (CP69 p5) for chapter 21 repeats LCP 4 and CP65 p7 only.

## 5. Conflicts

- **C1, fuel capacity per side.** plans-1980:p141 prints "two 25.5 gallon ... tanks". om-1980:p8 prints "two 28
  gallon" and "full 52 gallon capacity"; cp-text:CP24 p13 prints Max Fuel 52 gal. 2 x 25.5 = 51,
  2 x 28 = 56, 52 total is 26 per side. Model uses 26 per side. Do not pick a winner; the planform volume
  check (2.1) gives about 30 gal gross at 7.3 in, which fits any of these within the net-volume margin.
- **C2, baggage arm.** om-1980:p26 uses station 90. The derived plan centroid of the strake baggage floor is
  FS 80.6 (2.1). The OM row does not say which baggage area it covers (strake, behind the rear seat, or both).
- **C3, 1/4-27 vs 1/8-27 NPT.** p143 prints 1/4-27 for the drain insert tap; cp-text:CP28 LPC 60 and p145 step 9 and
  p146 section I-I print 1/8. Scan and CP agree on 1/8 for everything but that sentence.
- **C4, OM fuel moment rule.** om-1980:p25 prints "Fuel Moment = fuel gallons times 6.0", which gives 240 for 40 gal,
  but the sample row prints 25080 (240 lb at 104.5). It is a weight rate, not a moment rule. Already noted
  in the ledger errata (pilot moment 7865, heavy total 122706, light total 115708 vs 115706).
- **C5, "layup 7" used twice.** p144 step 6 (OD inside, 1 ply BID) and step 7 (outside bottom, 2 crossing UND
  plies) both say layup 7. p146 section views use 7 only for the outside layer. cp-text:CP33 LPC 102 rewrites the
  step 6 passage; the scan's step 6 shows corrected-looking sentences (one ply BID, flox in place, section
  F-F) yet step 7 lacks the LPC 102 "lapping 1 in onto the forward face of the spar" line. So the scan is
  partly corrected. Treat "7a" (OD inside) and "7b" (outside) as separate.
- **C6, two "Section C-C" on p146.** The upper C-C (left column) shows plies 6, 4, 9 with a wood ledge; the lower C-C
  (bottom of left column) shows plies 3 and 7. One is probably a mislabel (likely the lower is an unlabelled
  other cut). Plan view p147 marks C-C on the baggage side near FS 60 to 70.
- **C7, cap text.** p145 prints "fuel caps ... designed for VariEze"; cobelu changes it to Long-EZ.
- **C8, step 10 material.** p145: urethane or styrofoam, hollow or solid, 2 lb/ft3, "cross two plies UND". Cobelu
  (merged with CP30 LPC 84): solid urethane, styrofoam dissolved by fuel. LPC 84 says 2 lb/ft3 green urethane
  and a 45-deg crossed UND skin.
- **C9, foam type name.** p141 overview "type 45R rigid PV core" vs parts note "type 45 PV core": same material.
- **C10, LE FS at BL 58.** p171 prints 113.4 (typed) and a blue hand note 113.9 (CP25 LPC 7). Resolved in M2.7;
  here only re-confirmed.
- **C11, which drain.** p147 labels two drains: "WATER DRAIN STEP 2" (the tank low-point drain, I-I) and "DRAIN
  (STEP 10)" (a 1/4 in hole between OD and R45 that vents and drains moisture in the closed-off outboard
  area, not the tank). OM p8 counts "one in the leading edge of each strake". The step 2 drain at the forward
  corner matches the OM statement; the step 10 hole is not a fuel drain.
- **C12, drain tap vs p148.** None other.
- **C13, outboard skin spar edge.** p142 gives 32.0 x 4.9 (8.71 deg); p118 gives 32.5 x 4.9 (8.57 deg). Both rounded; the
  0.14 deg difference is within the print tolerance.
- **C14, cutout top-edge depth.** The aft-end value reads 1.90 while the mid value reads 1.40 (and one first-glance read at
  the forward hole read 1.90). The 2x crops read 1.90 at the aft end of the aft hole and 1.40 elsewhere.
  Cannot tell whether 1.90 is a real notch for the sight gauge region or a misprint.
- **C15, UND strip length.** p143 step 3 says fibre orientation along the long "22" dimension, while the printed 22.4 is the
  outboard skin kink height; the outer diagonal edge scaled off p147 is about 24 in. Not a hard conflict:
  unlabelled and not to scale.
- **C16, outboard-skin proportions.** The printed 22.4 kink height does not scale with 32.0 on the same drawing (the drawing
  is marked not to scale on p141; p142 does not repeat it). Use the printed numbers only.

## 6. Open questions and low-confidence reads for the captain

1. A14 rib outlines (R23, R45), the OD outline, and the jig-board use are not held. The R23 and R45 shapes
   (nose profile, heights, any joggle) need either a construction rule from the section views or a decision
   to use `repr`.
2. Strake mass is not printed. The mass-ledger exit test needs a derived strake mass from the ply schedule
   (2.4), foam area (p142 sizes) and the fairing blocks; the sump blister, caps, drain valve and tube are
   not weighed anywhere I could find. Fuel hardware has no printed weights in any source here.
3. Fuel arm 104.5 is the OM value for all fuel quantities. Derived tank centroid 103.85 (plan, area-weighted,
   constant height). Whether to model a tank centroid separately is a captain call; OM uses one arm.
4. Baggage arm 90 (OM) vs plan centroid FS 80.6: which volume is the 90 for? Strake limit is 100 lb per side.
5. Cutout value 1.90 vs 1.40 at the aft end of the aft hole (C14), and the forward-end "4.0" (could be 4.0 or 4.8;
   my crop reads 4.0).
6. Station "35" and the unlabelled middle arrow in the aft hole: the scale is not to size; the exact meaning of
   the arrows at stations 35 and mid-hole is my interpretation (tank-skin reference lines), not a printed label.
7. B23 notch radii (0.8R top, 1.3R bottom) and the "5 x 3" oval spacing digits: hand digits, crops 2.5x; medium.
8. Fuselage side BL at FS 50 and FS 103.5 (about 12 and 11.3) are scaled off p147, plus or minus 0.7 in; the
   baggage and tank outlines depend on them.
9. Whether the scan's step 6 (C5) already includes CP33 LPC 102 and CP28 LPC 59 hand-lettered third ply:
   the "third ply is a 5 inch UND strip" text on p144 is hand-lettered in capitals and matches LPC 59.
10. Cobelu's grounding-cable text cites "CP55 PCS134 MEO": the CP text carries the CP55 p3 article (ground lug
    and internal wire) but I did not find an LPC with that number; treat cobelu's detail as unverified.
11. Sump blister "5 in" dimension (p144 side view) and the exact blister outline are not unambiguous; the
    blister is also sold prefab (p144 note), so the outline may be A-sheet or purchased only.
12. The OD blue-ink "8" (p141) is a later hand insert; the printed outline has no length.
