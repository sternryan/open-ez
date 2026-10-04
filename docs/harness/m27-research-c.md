# Winglets and rudders (chapter 20): source research (2026-10-03)

Read-only pass for milestone 2.7, chapter 20 only. Every value below was read on the page image
(plans-1980 PDF pages p135 to p140, plus p171 and p054 for cross-checks). Hand-lettered numbers were
cropped and enlarged 2x. OCR was used only as a finder. Cites: `plans-1980:pNNN` (PDF page),
`cobelu` (chapter 20 transcription, diffed against the scan; scan wins), `cp-text:CPnn p<page>` (+ LPC
number), `om-1980:p<printed>`. Paraphrases are ten words or fewer. Nothing in the repo was edited.
The owner holds no A-sheets: wherever a shape lives only there, the row says so.

## 1. Page map

| PDF | Printed | Content |
|---|---|---|
| p135 | 20-1 | Overview, step 1 (cut cores), full planform at 1/5 scale, core block layout, root and bottom templates; CP25 LPC 13 handwritten note |
| p136 | 20-2 | Step 2 (skin schedule, tip cap), step 3 start (trim template, WPRP, jigging); CP25 LPC 6 handwritten A, B, C |
| p137 | 20-3 | Step 3 end (Bondo lumps), step 4 (inside layups #1 and #2, block A, conduit position) |
| p138 | 20-4 | Step 5 (block A carve, layups #3 and #4, UND ply table), step 6 (lower winglet, layup #5, light, fairing block), step 7 start (rudder layout, hinge, layup #6) |
| p139 | 20-5 | Step 7 end (rudder foam removal, layup #7, hinge and belhorn install, rudder travel, return spring, rudder stop), full-size CS301 pattern |
| p140 | 20-6 | View B-B (half scale), sections A-A, C-C, D-D (full scale), light colours; printed "last pg chap 20" on the margin |
| p141 | 21-1 | Chapter 21 begins (out of scope). Handwritten margin "see back of 20-6" |

Chapter 20 is p135 to p140 (six pages, 20-1 to 20-6), confirmed on hand-lettered page footers. p140
carries an explicit last-page mark. Also read for cross-checks: p171 (three-view, winglet stations) and
p054 (chapter 10 step 1, for the LPC 51 conflict).

## 2. Dimensions, stations, materials, parts, weights

Status key: book = printed and cross-checked; derived = my arithmetic from printed values (shown);
repr = shape not printed, or A-sheet only. Planform values marked "pixel" were scaled off the 1/5
planform drawing using its own printed 10 in rudder dimension (19.5 px per inch on the page image), so
treat them as medium confidence and re-measure.

### 2.1 Planform and stations (p135)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Upper winglet top skin station (WL) | WL 65.4 (top of skin), WL 66.4 with the 1 in cap | p135 (crop) | high (digits crisp; "66.4"/"65.4" read twice) | p171 three-view prints WL 66.4 at the top; block1-source-notes lists 196.6 for the same corner | book |
| Top cap | 1 in urethane foam, rounded, skinned 1 ply BID | p135, p136 | high | consistent both pages | book |
| Winglet root level line | WL 18.4 (rudder, root template, lower fin joins here) | p135, p138 text, p140 | high | WL 18.4 printed 5+ times | book |
| Wing plane / wingtip outline | WL 17.4; wingtip nose FS 156; winglet root airfoil nose near FS 159.7; straight LE meets root at FS 160.5 | p135 | high (digits), medium (which label is the root nose) | p171: wing tip FS 156, BL 157, WL 17.4 | book |
| Top aft corner (TE tip) | FS 196.6 | p135, p171 | high | both pages print 196.6 | book |
| Top forward corner (LE tip) | about FS 167.7 at WL 65.4 | p135 pixel | medium | LE sweep check below | repr (pixel) |
| Root TE station | FS 186.8 at WL 18.4 | p135 | high | rudder dims below | book |
| Root chord | 186.8 - 160.5 = 26.3 in (or 27.1 if the airfoil nose FS 159.7 is the root nose) | p135 | medium | no printed chord value | derived |
| Tip chord at WL 65.4 | about 28.9 in (196.6 - 167.7) | p135 pixel | medium-low | fin is wider at the top than at the root in the drawing | derived (pixel) |
| Height, upper fin | 65.4 - 18.4 = 47.0 in (48.0 with cap) | p135 | high | | derived |
| Height, lower fin | 18.4 - 9.8 = 8.6 in | p135 | high (WL 9.8 printed twice, p171 also WL 9.8) | | derived |
| Total height, bottom to cap | 66.4 - 9.8 = 56.6 in | p135, p171 | high | | derived |
| LE sweep (upper) | 7.2 in aft over 47 in, about 8.7 deg | p135 pixel | medium | | derived (pixel) |
| TE sweep (upper) | 196.6 - 186.8 = 9.8 in aft over 47 in, about 11.8 deg | p135 | high (endpoints printed) | pixel slope of the straight TE gives about 12 deg | derived |
| Lower fin bottom | flat at WL 9.8; 12 in dimension along the bottom (FS 190 forward to about 178); a "3 in" dimension at the aft-bottom corner; LE bottom corner rounded | p135 | medium (what the 3 in measures) | dashed outline is the uncut template | repr |
| Lower fin tip | round the entire tip of the lower fin | p135 | high | | text |
| Winglet cant, upper | no angle printed. Set only through A, B, C jig lengths (section 2.3) | p136 | n/a | A and C solve to about 4.5 in inward lean at the tip (below) | repr |
| Winglet toe or incidence | no angle printed. Set through the A and B difference (TE sweep set by jig lengths) | p136 | n/a | | repr |
| Airfoil sections | shapes in sections A-A and D-D are drawn full scale but have no ordinates; upper fin undercambered outboard, lower fin cambered inward below WL 18.4 | p136, p140 | n/a | ordinates are on A-sheet templates (A3 root and tip, A14 bottom tip) not in hand | repr (A-sheet only) |

Cant (derived, assumptions flagged): WPRP at BL 55.5, winglet root at the original wingtip BL 157 gives
a lateral distance of 101.5 in. Then A = 102.15 implies the LE mark at about FS 161.2 (160.5 expected).
B = 108.35 implies the root TE at about FS 187.5 (186.8 expected). C = 118.35 with the 47 in height
closes only if the tip leans inward about 4.5 in (gives FS about 198.5 against 196.6). p136 prints two
"4.5" labels near the tip and side view whose meaning I could not pin down. This is arithmetic, not a
printed cant. Treat as a consistency check only.

### 2.2 Cores (p135)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Upper fin core source | wing outboard TE block 48 in long; end angles 78.64 and 101.36 deg ("same as wings") | p135 (crop) | high | 78.64 + 101.36 = 180.00 | book |
| Second upper-fin block | 4.3 in thick, 14 in tall, 41 in long, left from the canard chapter 10 cores; cut diagonally for the other winglet | p135 | high | p054 says two 4.3 x 14 x 41 blocks saved | book |
| Lower fin core | cut from left-over wing scrap; 8.5 in tall, 3.5 in offset between root and bottom templates | p135 | high | | book |
| Templates | root template (WL 18.4) used for top and bottom fin; bottom template for lower fin | p135 | high | A-sheet shapes | repr (A-sheet only) |
| Hot-wire sheets cited | A3 and A14 added by CP25 LPC 13; A11 is the winglet trim template (p136) | p135, p136, cp-text:CP25 p6 | high | | text |

### 2.3 Skins, jigging, A/B/C (p136, p137)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Outboard skin 1st ply | UND, diagonal root TE to LE | p136 | high | diagram shows 1st ply UND tip-ward | book |
| 2nd ply | UND, crossing, root LE to tip TE | p136 | high | | book |
| 3rd ply | BID at 45 deg, upper winglet only, up 18 in from root; patch 14 in wide | p136 | high (18 in), medium (14 in label, handwritten) | CP34 LPC 104 (below); cobelu agrees on 18 | book |
| Inboard skin | same schedule as outboard | p136 | high | cobelu agrees | book |
| Peel ply | the whole BID surface, knife trim all around | p136 | high | | text |
| Wing overlap detail | see wing chapter for LE and TE skin overlaps | p136 | n/a | cobelu adds "19 Figure 19-51" (cobelu only) | text |
| WPRP (reference point) | inboard front corner of the aileron cutout, BL 55.5, FS 149.6, "see page 19-10" | p136 | high | chapter 19 colleague should confirm same corner | book |
| A dimension | 102.15 in (WPRP to LE mark at wing top surface) | p136 handwritten (CP25 LPC 6) | high (crop read) | cobelu 102.15 | book |
| B dimension | 108.35 in (WPRP to root TE) | p136 handwritten | high | cobelu 108.35 | book |
| C dimension | 118.35 in (to tip TE) | p136 handwritten | high (crop read) | cobelu 118.35 | book |
| Tolerance | A and B within 0.05 in; C plus or minus 1 in | p136 | high | | book |
| Wing weight | about 50 lb of sand bags on the wing top-side up | p136 | high | | text |
| Wing cut at winglet root | cut the wing skin through along the winglet inboard edge, protect the rudder conduit | p136 | high | | text |
| Bondo lumps | 2 or 3 lumps, 3/4 in diameter; 3 ft of 1 x 2 lumber braces sideways | p137 | high | | text |
| Jig to flat table | leftover blocks glued to a flat table, root and tip level lines parallel | p136 | high | CP10 jig tip (VariEze era, not cited as Long-EZ) | text |

### 2.4 Inside and outside layups (p137, p138, p140)

| Layup | Schedule | Extent | Cite | Conf | Model use |
|---|---|---|---|---|---|
| #1 | 8 strips 45 deg BID, 4 in x 12 in; flox plus foam wedges fill the void; notch around wing shear web | inside corner, "small inside tapes" | p137, p140 C-C | high | book |
| Flox corner cut | triangular, 2 in deep in the "high stress area", 1/2 in deep elsewhere; label "0.6 x 2 in flox corners" on the sketch; "2 in typ", "1/2 in" corner trim | p137 | medium (0.6 x 2 vs the text's 2 and 1/2 not reconciled) | repr |
| High stress area | from the rudder conduit to the LE along the winglet and wing touching edges | p137 | high | | text |
| #2 | 8 plies BID forward of the rudder conduit; two of the eight run aft to the winglet TE; joggles over the conduit | inside ribs | p137, p140 | high | book |
| Rudder conduit position | 13.2 in from the winglet TE, along the outside edge | p137 | high | cobelu 13.2 | book |
| Block A | 2 lb (green) urethane foam, 2 pieces of 2 in laminated; carve to a flat diagonal, not round | wing TE to winglet LE | p137, p138 | high | repr (shape only in sketches, no dims) |
| #3 (outside, bottom) | 2 plies BID, up 15 in on the wing and 12 in on the winglet, tapered; plus 7 UND around the corner; 2nd BID ply about 2 in shorter | corner | p138 | high | book |
| UND ply table, #3 and #4 | ply, A in, B in: 1: 24, 12; 2: 22, 11; 3: 20, 10; 4: 18, 9; 5: 16, 8; 6: 14, 7; 7: 12, 6 | UND runs along A | p138 | high (printed type, cropped) | book |
| #4 (inside, top) | identical to #3; BID lapped 1 in onto the outside of the winglet at the lower LE | corner | p138 | high | book |
| #5 | 1 ply BID at 45 deg, 2 in wide tape, outside and inside of the lower fin joint | WL 18.4 | p138, p140 | high | book |
| Joint strength note | do not add plies; joint takes 90 deg sideslip at 170 mph | p138 | high | cobelu agrees | text |
| #6 (winglet hinge area) | 3 plies BID over the foam-removed area, plus one extra ply on the hinge edge | foam removed 0.6 in top and bottom, 1 in at the front | p138, p140 D-D | high | book |
| Hinge recess | trim hinge area forward 0.2 in x 7 1/2 in (the fraction glyph reads "1/2") | p138 | medium (fraction glyph) | notch drawing p139 shows 0.2 and 7.5 | book |
| #7 (rudder) | 3 plies BID plus an extra ply at the hinge and the belcrank depression | rudder edges and depression | p139 | high | book |
| Tip cap | 1 in urethane, 1 ply BID | top | p136 | high | book |
| Cure times | no hours printed in chapter 20. Allow partial cure before the next layup to avoid exotherm | p137 | high | CP25 gives no cure time for this chapter | text |

### 2.5 Rudder, hinge, conduit, controls (p135, p138, p139, p140)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Rudder TE station at WL 18.4 | FS 186.8 | p135 | high | | book |
| Rudder hinge line | FS 176.8 | p135 | high | | book |
| Rudder width at WL 18.4 | 10 in (hinge to TE) | p135, p138 | high | 186.8 - 176.8 = 10.0 | book |
| Rudder width at top | 12.14 in | p135, p138 | high | pixel TE slope gives FS 189.1 (176.8 + 12.14 = 188.94) | book |
| Rudder width at bottom | 11.5 in | p135, p138 | high | | book |
| Rudder height | 14.5 in total, 10.5 in above WL 18.4 and 4 in below | p135, p138 | high | 10.5 + 4 = 14.5 | book |
| Rudder top and bottom WL | top 18.4 + 10.5 = 28.9; bottom 18.4 - 4 = 14.4 | derived | n/a | | derived |
| Piano hinge | 7.5 in long, from WL 18.4 up, so WL 18.4 to 25.9 | p138 text, p139 notch sketch | high | hatched strip on p135 spans about 7 in | derived |
| Hinge part | MS20001P6 piano hinge, outboard edge | p139 | medium (part number printed small) | | book |
| Hinge screws | 3 x AN525-10R8, K-1000-3 nutplates on the hinge, trim hinge width to fit | p138, p139 | medium ("10R8" glyph read from small print) | cobelu AN525-10R8 | book |
| Rudder hinge fasteners | 7 pop rivets; 2 x AN525-10R8 screws with MS21042-3 nuts for the belhorn | p139 | high (counts) | washer: text says AN906-10L, section Y-Y says AN960-10L (conflict, section 5) | book |
| Rudder foam removal | 0.6 in top and bottom, 0.8 in on the forward face | p139 | high | | book |
| Belcrank depression | conical, 2.4 in deep from the hinge line, outboard side, centered at WL 18.7; section E-E labels 2.4 and 0.8 | p139 | high (2.4); medium (0.8 label) | | repr |
| Rudder travel | max 30 deg; swage must keep at least 0.7 in travel before it bottoms on the conduit | p139 | high | the brake master cylinder is the rudder stop | book |
| Rudder stop edge "A" | edge A can be trimmed or shimmed for ground-adjustable trim | p139, p140 | high | | text |
| CS301 belhorn | 0.040 in 4130N steel; two #10 holes; one 5/16 in hole; bend 90 deg up (left) or down (right); shown full size | p139 | high | full-size pattern, shape present on scan | repr (full-size pattern printed, no dims) |
| Return spring | 4 in length of 0.35 OD x 0.050 wire steel spring (same as pitch trim) | p140 | high | | book |
| Spring tube | 1 in OD x 0.035 wall aluminum tube, 4.5 in long, micro in place; 1/4 in birch plywood plug; hook from 3/32 piano wire, potted in flox | p140 | high | the 1 in hole in the foam is cut with a notched tube | book |
| Drain hole | 1/4 in, inboard side only, at the rudder bottom | p135, p140 | high | | book |
| Rudder conduit | position 13.2 in from winglet TE (above); cut wing through but do not cut the conduit; hooks up in ch 16 | p136, p137, p139 | high | | book |
| Cable | cable plus swage fitting at the belhorn; "see Chap 16" | p139 | high | | text |
| Section D-D | 3 ply BID at the rudder cut, 0.6 in typical | p140 | high | | repr |
| Section Z-Z | 2 in by 0.6 in notch at the 1 in hole | p139 | medium | | repr |
| Wingtip light | at the shown position on the wingtip, WHT and GRN lenses, no weight aft of it, no cuts into the structure | p138, p140 | high | CP31 LPC 90 changes the cross reference | text |
| Fairing block | optional, any foam covered with 2 plies BID, fairs wing tip to winglet; original wingtip BL 157 | p138, p140 | high | | repr |

### 2.6 Weights and build times (Long-EZ prototype log, not the plans)

| Item | Value | Cite | Conf | Model use |
|---|---|---|---|---|
| Upper winglet, with antenna and coax | 6 lb | cp-text:CP26 p3 | high | text |
| Lower winglet | 1 lb 3 oz | cp-text:CP26 p3 | high | text |
| Wing complete with both winglets and rudder, ready to finish | 64 lb | cp-text:CP26 p3 | high | text |
| Build time | upper winglets 11 mh (2), lower 6 mh (2), upper jigged and layups plus lower 23 mh per wing, rudder 7.5 mh | cp-text:CP26 p3 | high | text |

No weights are printed in chapter 20 itself. The VariEze-era "wing/winglet/rudder 41 lb" line in CP12
is for another airplane and is not used.

## 3. Build-order list (op candidates)

| # | Short name | What is done | Prerequisites | Jig or fixture |
|---|---|---|---|---|
| 1 | Cut winglet cores | hot-wire upper and lower fin cores | ch 3 and 7 hot-wiring, ch 10 leftover blocks, wing scrap, A3/A14 sheets (not held) | wing TE block and canard block layout |
| 2 | Round lower fin | round the lower LE and tip | op 1 | none |
| 3 | Skin outboard | two UND plies, BID patch on upper | op 1; ch 19 LE and TE overlap details | leftover blocks glued flat |
| 4 | Skin inboard | same schedule, 1 in cap, trim to size | op 3 | leftover blocks on table |
| 5 | Mark trim template | trim the inboard root to the wing | op 4; A11 template (not held) | coping saw |
| 6 | Jig upper fin to wing | set A, B, C, then Bondo | ch 19 wing ready, WPRP marked; ch 19 cutouts | table, sand bags, box and stick, 3 ft 1x2 |
| 7 | Cut wing skin | remove the wing piece under the winglet | op 6 | none |
| 8 | Inside layups 1 and 2 | cut flox corners, 8 BID tapes, 8 BID ribs | op 6, rudder conduit placed at 13.2 in | winglet hanging off the table |
| 9 | Install block A | carve, micro, weight in place | op 8 | weights or nails |
| 10 | Outside layups 3 and 4 | UND corner and 2 BID, then flip | op 9 | peel ply edges |
| 11 | Attach lower fin | trim root to WL 18.4, 2 in BID tape, layup 5 | op 10 | none |
| 12 | Wingtip light and fairing | install light, optional fairing block | op 11 | none |
| 13 | Rudder cutout | layout, razorsaw skins, remove rudder | op 10; ch 16 conduit | none |
| 14 | Hinge prep, winglet side | foam removal, layup 6, recess hinge | op 13 | wing leading edge down |
| 15 | Hinge prep, rudder side | foam removal, layup 7, belcrank depression | op 13 | none |
| 16 | Hang rudder | hinge screws, belhorn, cable, swage | ops 14 and 15; ch 16 return to finish | none |
| 17 | Return spring and stop | tube, plug, hook, stop A | op 16 | none |

## 4. CP corrections touching chapter 20

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP25 LPC 13 (cp-text:CP25 p6; plans-1980:p135 handwritten) | MEO | step 1: add pages A3 and A14 to the hot-wire reference | A-sheet only; none held |
| CP25 LPC 6 (cp-text:CP25 p6; plans-1980:p136 handwritten) | MEO | page 20-2: adds A = 102.15, B = 108.35, C = 118.35 | direct inputs for cant and incidence checks |
| CP31 LPC 90 (cp-text:CP31 p5) | MEO | page 20-4 step 6: "see section III" becomes see page 22-3 | none (cross reference) |
| CP34 LPC 104 (cp-text:CP34 p7) | MEO | page 20-2: "upper surface only" becomes "upper winglet only" | 3rd BID ply clarified, not a schedule change |
| CP27 LPC 51 (cp-text:CP27 p7) | MEO | chapter 10 page 10-1 refers to chapter 13 for winglets, should be 20 | none (cross reference), but see conflict 1 |
| CP26 p3 (cp-text:CP26 p3) | OBS (weights log) | prototype weights and build hours | text only |
| CP26 p8 (comm antenna in the winglet; cp-text:CP26 p8) | OPT | copper foil strips 20.3 in long, 1 in from the TE, installed before the inboard skin | affects inboard skin step; antenna shape is unmodeled |
| CP40 p2 and CP41 p4 LPC 118 (cp-text) | OPT/DES | optional high performance rudders replace chapter 20 steps 7 and rudder plans; hinge screws and nutplates in the winglet, rivets in the rudder | out of the 1980 scan; see section 6 |
| CP45 p4 LPC 121 (cp-text) | MEO (new construction, HP rudder) | conduit 1.5 in aft of the A12 pattern location | applies only if HP rudders are built |
| CP31 p4 (cp-text) | MAN | rudder hinges go into the rudder with flush pop rivets (Avex 1604-0412 or Cherry MSC 43) | rivet type for the 7 pop rivets |

Not Long-EZ, not used: CP11 "20-2 #38 drill should be #42" (VariEze plans), CP10 "wing/winglet/rudder
41 lb", CP14 and CP16 jigging and the "0.3 in becomes 0.75" cant change (VariEze), CP22 page 8 rudder
travel (VariEze).

## 5. Conflicts

1. LPC 51 chapter reference. cp-text:CP27 p7 says page 10-1 "refers to chapter 13 for winglets, should be
   chapter 20". On plans-1980:p054 (10-1) the printed chapter number is struck through by hand and
   replaced with "20". The struck digits read as "13" at 6x zoom, but the strike hides the second digit,
   so 18 or 19 cannot be fully excluded. I could not confirm the brief's "1980 edition says ch 19". The
   handwritten note above step 1 on p054 reads "CP27 LPC #14" (or #44), not #51; the number in that
   note is a different LPC, which I did not trace. Both sources agree on the corrected target (20).
   The cobelu chapter 10 text already says chapter 20 with the LPC tag; it does not preserve the old number.
2. Rudder hinge washer. plans-1980:p139 text says AN906-10L; the section Y-Y drawing on the same page says
   AN960-10L. Both are printed. Which part is meant is unsettled. (AN960 is a washer series; AN906 is not.
   I did not confirm either part number against a catalogue.)
3. Hinge length and position. p138 says 7.5 in from WL 18.4 up; p139 sketch shows 7.5 and 4 together. I
   read the 4 as the rudder portion below WL 18.4, consistent with p135 (14.5 = 10.5 + 4). Not a hard
   conflict, but the sketch could be read as a hinge reaching 4 below.
4. Flox corner depth. Text says 2 in and 1/2 in; the sketch on p137 is labelled "0.6 x 2 flox corners" at
   one corner. Two numbers for one feature. Both printed.
5. Cobelu additions not on the scan: "(13 in)" for the shorter 2nd BID ply (scan only says about 2 in
   shorter); "the winglet is over 44 inches long" (scan shows about 47 in above WL 18.4); the A11 sheet
   list; steps 7a to 7c (HP rudders, hidden belhorn) and step 2a comm antenna. Scan wins for the 1980
   chapter.
6. Config values. `winglet_height` 16.0, `winglet_root_chord` 20.0, `winglet_tip_chord` 12.0 in
   `config/aircraft_config.py`: no page supports any of them. Printed geometry: height 47.0 in upper (56.6
   in with cap and lower fin), root chord about 26.3 in, tip chord about 28.9 in (pixel). Chord values 20.0
   and 12.0 do not match anything on p135 or p171 (12 in appears only as the bottom flat of the lower fin;
   20 matches the wing tip chord, which suggests contamination from the wing). The comment cites
   "Ch.19"; winglets are chapter 20. There is no GEOMETRY_PROVENANCE entry. They are used in
   `core/openvsp_runner.py`. All three values are unsourced; replace with sourced values or mark repr.

## 6. Open questions and low-confidence reads

- Tip chord and LE sweep are pixel-scaled from the 1/5 planform (about 28.9 in and 8.7 deg). Re-measure
  with the printed 12.14 in rudder dimension as the scale, and check the top LE point against p171.
- Root chord: 26.3 (FS 160.5) or 27.1 (airfoil nose FS 159.7). Decide which label marks the root nose.
- Meaning of the two "4.5" labels on p136 and the "3 in" on the lower fin (p135).
- Hinge recess "7 1/2" glyph on p138 (could be 7 1/4).
- Hinge screw part "AN525-10R8" is printed small on p138 and p139; "R8" read from small print.
- Hinge part number "MS20001P6" on p139, small print.
- Layup 3 "14 in" patch width on p136 (handwritten label).
- Section E-E label 0.8 and section Z-Z 2 in by 0.6 in on p139.
- Cant, toe and airfoil ordinates live only in A-sheet hot-wire templates (A3, A11, A14); the owner holds
  none. The winglet airfoil must be modeled as representational. Note A and B ratios imply a small inward
  cant at the tip but no angle is printed.
- Lower fin shape below WL 18.4 (rounded corner radius) is representational.
- Optional HP rudder plans, hidden belhorn and comm antenna details are post-1980 and out of the scan.
- WPRP FS 149.6 and BL 55.5 should be cross-checked against the chapter 19 aileron cutout on p-ch19 pages.
