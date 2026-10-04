# Wings, first half (chapter 19, p118 to p126): source research (2026-10-03)

Read-only research pass for milestone 2.7, crew A. Every value was read on the page image (hand digits
cropped and enlarged 2.5x to 10x), not the OCR. 1980 plans cited as `plans-1980:pNNN` (PDF page). Cobelu
text (`cobelu`, ch19 md) was diffed against the scan; scan wins. CP text cited as `cp-text:CPnn p<page>`
(+ LPC number). Paraphrases are ten words or fewer. Nothing in the repo was edited. The owner holds no
A-sheets (jig templates A9 to A13, hot-wire templates, rudder-conduit template A12): every shape that
lives only there is marked "repr".

## 0. Answer to the leading-edge question (read this first)

Four numbers get confused. They are four different points.

| Number | What it is | Where printed | Point |
|---|---|---|---|
| 112.9 | wing LE, FS, at BL 55.5 | plans-1980:p126 (label on the BL 55.5 dashed line) | outer-panel LE at the inboard foam joint |
| 113.9 (p171 prints 113.4) | wing LE, FS, at BL 58 | plans-1980:p171 label, CP25 LPC 7 | strake/wing LE kink, 2.5 in outboard of BL 55.5 |
| 125.6 | "FS of foam edge" at BL 23 | plans-1980:p126 | forward corner of inboard core FC1 (not a wing LE) |
| 125.61 | retired fitted value | git history, calibration commit | none (fit to a neutral-point target, internal frame) |

Arithmetic, all from printed values on p126 (LE line is declared straight from BL 55.5 to BL 157):

- Slope: (156 - 112.9) / (157 - 55.5) = 43.1 / 101.5 = 0.4246, atan = 22.99 deg. Printed 22.98 deg. Match.
- LE at BL 58: 112.9 + (58 - 55.5) x 0.42406 (tan 22.98) = 112.9 + 1.06 = 113.96.
  CP25 LPC 7 says 113.9: match within 0.06. The p171 print 113.4 would imply LE 112.34 at BL 55.5, which
  gives chord 155.6 - 112.34 = 43.26, not the printed 42.7. So 113.9 is the value consistent with p126.
- Chord at BL 55.5: TE 155.6 - LE 112.9 = 42.7, printed 42.7. Chord at tip: 176 - 156 = 20.0, printed 20.0.
- Chord at BL 106.25: TE 165.8 (computed 155.6 + 50.75 x 0.2010 = 165.80, printed 165.8) minus LE.
  With LE 134.45 the chord is 31.35, printed 31.35. With the printed LE label 134.95 it would be 30.85.
  So the p126 label 134.95 conflicts with the printed chord (section 5, C1).
- Model derivation check: `fs_wing_le` = 113.9 - (58 - 23.3) x tan 22.98 = 113.9 - 34.7 x 0.42406 = 99.19.
  This is the straight outer-panel LE line extended inboard to the model root BL 23.3. The book never
  prints a wing LE at BL 23 or 23.3. Inboard of BL 58 the leading edge belongs to the strake, so 99.19 is a
  model construct (the line extended through the strake), flagged as such by the model already.
- The book's inboard wing foam at BL 23 starts at FS 125.6 and ends at the TE FS 148.4 (chord 22.8 in the
  FS direction), matching the plans' "22.8 in check" on p118. At BL 55.5 foam LE is 130.5 and TE 155.6
  (25.1, matching the "25.1 in check" on p118). FC1 LE line length: sqrt(32.5^2 + 4.9^2) = sqrt(1080.26)
  = 32.867, matches the printed 32.87 on p118. The 8.57 deg slope: 4.9 / 32.5 = 0.1508, atan = 8.57 deg.
- The two 125.6 figures: p118 and p120 print a 125.6 / 125.59 "straight line" length for the jig base
  (distance between jig 5 and jig 1 on the floor). That is a jig spacing, not a station. The p126 125.6
  is the FC1 inboard corner station. The retired 125.61 was fitted (calibration commit, internal frame with
  a 45.5 offset, aimed at a neutral-point target), so its closeness to 125.6 is a numerical coincidence,
  not a source. Different point from 113.9: 125.61 - 113.9 = 11.71 in, about 27.6 in of LE run at 22.98 deg
  (BL 58 to BL 30.4), which is not a printed location.

Conclusion: 113.9 at BL 58 (strake/wing LE kink) is the right anchor and agrees with p126 geometry.
125.61 and 113.9 are different points; 125.61 has no book meaning and should stay retired. A reader must not
treat 125.6 on p126 as a wing LE.

## 1. Page map (`plans-1980`, confirmed on printed footers)

| PDF | Printed | Content |
|---|---|---|
| p117 | 18-10 | last page of chapter 18 (rotated latch parts sheet) |
| (none) | 19-1 | not on the scan; no page between p117 and p118 |
| p118 | 19-2 | step 2 (jig setup, floor line 125.6), step 3 (foam core cutting, angles, FC1 check 32.87) |
| p119 | 19-3 | torque-tube cutout, FC1 inboard shell, aileron cutouts, 1 in light hole; CP26 LPC 32 note |
| p120 | 19-4 | step 4 (assemble cores in jig, depressions, LWA4/LWA6, W18, layup 2 start) |
| p121 | 19-5 | layup 2 ply schedule, layup 3 pads, bond FC4/FC5; CP26 LPC 31 note |
| p122 | 19-6 | step 5 (bottom spar cap), step 6 (bottom skin); CP25 LPC 9, 10 notes |
| p123 | 19-7 | step 7 (top spar cap), step 8 (top skin, rudder conduit); CP25 LPC 11 note |
| p124 | 19-8 | incidence board, step 9 (ribs, layup 5 to 8), step 10 start (aileron cut); CP25 LPC 8, 12 |
| p125 | 19-9 | step 10 end (aileron hardware, hinges, balance), step 11 controls start |
| p126 | 19-10 | two-page spread: left is the hand-lettered CP24 LPC 2 tie-down note, right is the plan view |

19-1 is absent from the scan. Cobelu ch19 holds its text (step 1, jig templates): cobelu gives a five-template
jig, 1/2 in plywood, top WL 24.4 and bottom WL 10.4, WL 17.4 line, 17 links, 34 bolts. The captain should treat
those jig WLs as `cobelu` only (not scan-verified). Cobelu otherwise matches the scan on every number below
except where flagged in section 5. Cobelu folds in later CP edits (it prints "2 plies" for the BL 120 to 157
shear web; the scan prints 3). The cobelu figure numbers (19-49 and so on) are not the printed page numbers.

p127 is printed 19-11 (planform/block layout, 7x14 blocks; owner-relevant dimensions 33-29, 51-7, 6-20 appear
there) and is outside this scope; p127 to p134 are the second half.

## 2. Dimensions, stations, angles, materials

Status key: **book** = printed and cross-checked; **derived** = my arithmetic; **repr** = shape not printed or
A-sheet only; **text** = printed in prose.

### 2.1 Planform (plans-1980:p126, scale 1/10, "right wing, left is opposite")

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Airfoil family | modified Eppler 1230, all stations | p126 | high | cp-text not needed | book |
| Chord at BL 55.5 | 42.7 | p126 | high (clear) | 155.6 - 112.9 = 42.7 | book |
| Chord at BL 106.25 | 31.35 | p126 | high | 165.8 - 134.45 = 31.35 | book |
| Chord at BL 157 | 20.0 | p126 | high | 176 - 156 = 20.0 | book |
| Thickness at BL 55.5 / 106.25 / 157 | 16.2 pct / 15.7 pct / 15.0 pct | p126 | medium for 16.2 (trailing glyph smeared), high others | none | book |
| Twist at BL 55.5 | 0.6 deg washin | p126 | high | | book |
| Twist at BL 106.25 | 0.96 deg washout | p126 | high | | book |
| Twist at BL 157 | 2.7 deg washout | p126 | high | linear check: root 0.6 + 0.5 x (0.6 + 2.7) = 2.25 gives 1.65 mid; printed 1.56, near linear | book |
| LE sweep, outer panel | 22.98 deg | p126 | high | 43.1 / 101.5 gives 22.99 | book |
| LE at BL 55.5 | FS 112.9 | p126 | high | position on the FS axis gives 112.8; chord arithmetic | book |
| LE at BL 106.25 | FS 134.95 as printed (134.45 by arithmetic) | p126 | low on last-digit | see section 5 C1 | conflict |
| LE at BL 157 | FS 156 | p126, p171 | high | both print 156 | book |
| LE at BL 58 | FS 113.9 | CP25 LPC 7, p171 | high | 112.9 + 1.06 = 113.96 | derived agreement |
| TE at BL 55.5 | FS 155.6 | p126 | high | 148.4 + 7.2 | book |
| TE at BL 106.25 | FS 165.8 | p126 | high | arithmetic above | book |
| TE at BL 157 | FS 176 | p126 | high | | book |
| TE sweep outer | 11.36 deg | p126 | high | 20.4 / 101.5 = 0.2010, atan 11.37 | book |
| TE sweep inboard kink | 12.49 deg | p126 | high | 7.2 / 32.5 = 0.2215, atan 12.49 | book |
| TE at BL 23 | FS 148.4 (plan note reads 148.9 or 148.4) | p126 | medium | 155.6 - 32.5 x 0.2215 = 148.4 | book |
| Chord lines height | all intersect LE tangent point, all at WL 17.40 | p126 | medium (digit 4 reads like 9) | p118 "W.L.17.4" and cobelu WL 17.4 jig line | text |
| LE line | flat at WL 17.4 (digit ambiguous, 17.9 alt) | p126 | medium | model `wing_le_wl` uses 17.4 | text |
| TE height | slopes from WL 16.95 at BL 55.5 to WL 18.35 at BL 157 | p126 | high | | text |
| TE kink inboard of BL 55.5 | slopes up and forward to meet cowl line at FS 148.4, BL 23, WL 17.5 | p126 | medium (FS digit 4 vs 9) | 148.4 matches arithmetic | text |
| LE and TE | straight lines between BL 55.5 and BL 157 | p126 | high | | text |
| Shear web (spar) forward face at BL 23 | foam edge FS 125.6 | p126 | high (re-read; first read 123.6 was wrong, 5 not 3) | 130.5 - 4.9 = 125.6 | book |
| Shear web forward face at BL 55.5 | FS 130.5 | p126 | high | | book |
| Shear web face at BL 106.25 | FS 147.35 | p126 | high | 130.5 + 50.75 x 0.3320 = 147.35 | book |
| Shear web face at BL 157 | FS 164.2 | p126 | high | 130.5 + 101.5 x 0.3320 = 164.2 | book |
| Spar cap width at BL 157 (aft ref) | 167.2 (164.2 + 3.0) | p126 | high | 3.0 printed "spar cap" | book |
| Spar cap width | 3.0 | p126; p122 "3 in x .035 tape" | high | | book |
| Shear web sweep | 18.42 deg | p126 | high | atan 0.3320 = 18.37 (0.05 deg print rounding) | book |
| Centersection spar sweep, outboard | 8.57 deg | p126 | high | already in model (p88) | book |
| Centersection aft face at BL 55.5 (spar tip) | 129.9 inside region noted "12.9" at BL 55.5 on the LE | p126 | n/a | the label at BL 55.5 near 112.9 is the LE; keep distinct from model's 129.9 spar aft face | note |
| Aileron outboard end | BL 118.1 | p126, p119, p171 | high | three sources agree | book |
| Aileron inboard (p171) | BL 54.3 | p171 | high (clear digits) | plans cut at BL 55.5 foam joint (p124) with 1 in A10 tube overhang | see C3 |
| Inboard TE area removed during step 4 | triangle forward of BL 55.5 foam joint (FC1/FC4 face) | p126 | medium | | repr |
| Torque-tube line | FS 149.6 at BL 55.5 (digits medium) | p126 | medium | | repr |
| Planform region names | INBD = BL 23 to 55.5 (FC1), CENTER = 55.5 to 106.25 (FC2, FC4), OTBO = 106.25 to 157 (FC3, FC5) | p126, p118 | high | | book |
| Wing tip | BL 157, FS 156 LE to 176 TE | p126 | high | | book |
| Dihedral | not printed in these pages; wing is jigged flat | p118, p120 | high | | book |
| Root butt line | 23 printed throughout; 23.3 appears nowhere in p118 to p126 | p126, p118 | high | model uses 23.3 | see C4 |

### 2.2 Core blocks, template angles (p118)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Foam per wing | five 7x14x64 in, two 7x14x41 in styrofoam blocks | p118 | high | cobelu | book |
| Core pieces | FC1 inboard, FC2/FC3 aft (shear web aft), FC4/FC5 forward (LE) | p118, p119 | high | | book |
| Core cut angle center and outboard | 78.64 deg both sides | p118 | high | atan(42/8.44) = 78.64; 90 - 11.36 | book |
| Core cut angle inboard | 77.51 deg | p118 | high | 90 - 12.49 = 77.51; atan(28/6.20) | book |
| Right-triangle layout, center | up 42 over 8.44 | p118 | high | tan 11.36 x 42 = 8.44 | book |
| Right-triangle layout, outboard | up 28 over 5.63 | p118 | high | 28 x 0.2010 = 5.63 | book |
| Right-triangle layout, inboard | up 28 over 6.20 | p118 | high | 28 x 0.2215 = 6.20 | book |
| FC1 LE checks | 22.8 and 25.1 inch dims; LE length 32.87 | p118 | high | section 0 arithmetic | book |
| Inboard block thickness | thicker at one end than 7 in; scrap block on top | p118 | high | | text |
| BL 55.5 rib | used at outboard end of inboard block, forward of spar trough only | p118 | high | | text |
| Cut along shear web | vertical template at spar-trough forward edge, perpendicular to waterlines | p118 | high | | text |
| Shear-web cut sketch | WL 17.4 label, 90 deg | p118 | high | | repr |
| Jig floor line | 125.6 total; spacings 31.7, 51.7, 88.4 (p118 one decimal) | p118 | high | | book |
| Jig floor line, precise | 125.59 total; 31.72, 51.72, 88.44 from jig 1 | p120 | high | rounded p118 values agree | book |
| Jig edge offsets | 10, 10, 10 in (3 places), 5 in, 1 in as shown | p120 | high | cobelu says "1, 5, 10 (3 places)" | book |
| Jig references | five jigs, top WL 24.4 / bottom WL 10.4 | cobelu only (19-1 missing) | medium | | text |
| Core-cut wire | 1 in in 4 to 6 s, pause 2 to 3 s at "P" points | p118 | high | | text |
| Template stock | 1/16 birch ply, page A9 glued to A10 | p118 | high | owner has no A-sheets | repr |
| Hot-wire profile shapes | ribs and jig cutouts | A9 to A13 only | n/a | not owned | repr |

### 2.3 Inboard shell, torque tube, aileron cutouts, light hole (p119)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Torque-tube cutout | numbered cut 0 to 16, oval hole at BL 55.5 | p119 | high | | text |
| BL 23 torque-tube template | along top surface 9.2 in from TE | p119 | high | cobelu 9.2 | book |
| FC1 wedge | 6 in and 1 in layout; remove inboard wedge, hollow it, keep 0.6 in shell | p119 | high | | book |
| Shell tolerance | 0.6 in critical only at top forward attach edge; elsewhere plus or minus 0.25 | p119 | high | | text |
| FC2 aileron cutout | root and mid templates, cut 0 to 15 | p119 | high | | text |
| FC3 aileron cutout | 3 x 8 in chunk out, 12 in dimension, template nailed at BL 106.25; tip template BL 118.1 | p119 | high | | book |
| Light-wire hole | 1 in diameter, cut 0 to 12, near bottom surface | p119 | high | CP26 LPC 32 clarifies end position | text |
| Light-hole offsets | FC4 at BL 55.5: 2 in; BL 106.25: 3.5 in; FC5 at BL 157: 5.6 in | p119 | medium (3.5 vs 3-1/2) | | book |
| Template names | torque tube, aileron root/mid/tip, hole forms | p119 | high | | repr |

### 2.4 Assembly and layup 1 to 3 (p120, p121)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Attach depression width | 1.7 in, round inside corners | p120 | high | | book |
| Depression layout (FC1) | 3.4 long, 1.15 from FC1/FC2 edge, 1.7 wide | p120 | high | | book |
| Depression depth | top not equal to bottom; depth from section B-B (p128) | p120 | high | section B-B is on p128, out of scope | repr |
| Metal blocks | three 1/4 in 2024-T3: two LWA4 outboard, one LWA6 inboard | p120 | high | cobelu | book |
| LWA4 position | 2 in, 1.5 in, 1 in offsets | p120 | medium | | book |
| LWA6 position | 2.3 in, 2 in, 1 in | p120 | medium | | book |
| W18 aluminum strips | two, .016 2024-T3, 2 x 2.75, flange .30 (top) / .25 (bottom) | p120 | medium (flange digits small) | | book |
| Layup 1 | 2 plies BID "liner" in the access depressions | p120 | high | | book |
| Layup 2 (shear web) | 12 pieces 13 in wide, 45 deg UND, rolled | p120 | high | | book |
| Layup 2 pieces extent | ply 1 and 2 full span, crossed diagonals; foam edge radius about 0.2R | p121 | high | | book |
| Plies 3 and 4 | start 39 in from tip to inboard end, crossed | p121 | high | | book |
| Plies 5 and 6 | start 91 in from tip to inboard end, crossed | p121 | high | | book |
| Shear web thickness | 6 plies BL 23 to 70; 4 plies BL 70 to 120; 3 plies BL 120 to 157 | p121 | high | CP26 LPC 31 corrects 3 to 2 | cp-corrected |
| Layup 3 | 3 ply BID at 45 deg pads, 4x4 and 4x6, centered on metal, not onto spar cap | p121 | high | | book |
| Plate cure weight | 10 lb on each plate | p121 | high | | text |
| LWA3 and LWA2 plates | epoxied over pads | p121 | high | cobelu | book |
| Joggle matching | dimension A equal to B, full span | p121 | high | | text |
| 2 plies of 1.7 depth | "A" and "B" dims not numeric | p121 | n/a | | text |
| Shear web spar sketch FC1/FC2/FC3 | | p121 | n/a | | repr |

### 2.5 Spar caps, skins, rudder conduit (p122, p123)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Bottom cap | five plies, 3 in wide, .035 UND tape | p122 | high | cobelu | book |
| Bottom cap ply lengths | 142, 135, 84, 52, 19.5 (5th may read 17.5) | p122 | medium on the fifth, high others | cobelu image reads the same shape | book |
| Bottom cap inboard offsets | 5, 12, 19, 26 in (drawn marks) | p122 | high | drawing is not to scale vs BL span | text |
| Bottom cap span marks | BL 23 to BL 157 | p122 | high | | book |
| Top cap | seven plies | p123 | high | | book |
| Top cap ply lengths | 142, 142, 119, 90, 61, 39, 20 | p123 | high | tape length 142 is about 134 / cos 18.4 = 141.3 | book |
| Top cap offsets | 6, 12, 18, 24 in | p123 | high | | text |
| Dam | 1/4 in plywood at inboard end, butts to LWA3 | p122 | high | | text |
| Bottom skin | two plies UND, joints butted, selvage kept | p122 | high | | book |
| Skin roll width | 38 in | p122, p123 | high | | text |
| Skin angle | first and second ply diagonals, crossed | p122 | high | | text |
| Tip reinforcement | third bottom ply is BID at tip | p122 | high | | book |
| Top skin | two UND plies as bottom, third UND from hinge line forward only, then BID tip reinforcement | p123 | high | | book |
| UND third ply geometry | 5.9 in along BL 55.5; 4.35 in along BL 106.25; 38 in roll | p123 | high | | book |
| Bottom peel ply | 65 in long, 1 in wide; dims 7.3 at BL 55.5 and 5.6 at BL 106.25 from TE | p122 | high | | text |
| Top peel ply | 65 in long, 1 in wide, ahead of aileron gap | p123 | high | | text |
| Skin LE lap | 2 in onto bottom skin; 4 in lap down FC1 face | p122, p123 | high | | book |
| Bottom skin taper | last 0.5 in tapered, hard block | p123 | high | | text |
| Bottom skin trim | TE flush; LE at LE tangent line | p122 | high | | text |
| Peel ply strips at attach | 3 in wide strips near depressions, 3 x 12 | p122, p123 | high | | text |
| Rudder conduit | 3/16 OD, .025 wall Nylaflow, never Nylo-Seal | p123 | high | | book |
| Conduit position | 4.8 in at root drawn; curves down 0.7 in over 8 in at root; sticks out 2 in at ends | p123 | high | | book |
| Conduit tip curve | full-size template A12 | p123 | n/a | not owned | repr |
| Conduit routing | cobelu step 8a high-performance rudder route is a later CP45 change | cobelu | n/a | out of 1980 scan | OPT |

### 2.6 Incidence reference, ribs, aileron cut (p124)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Incidence reference | 2 ft straight board bondo'd on top skin, shimmed level in jig, parallel to a butt line | p124 | high | | text |
| Incidence value | none printed; wing set by jig WL 17.4 and the board | p124 | high | | text |
| Rib at inboard end | form 0.7 in rib with rotary file (CP25 LPC 8) | p124 | high | | cp-corrected |
| Layup 5 | 3 in wide UND, two plies, each 30 in long, lap back 12 in onto skins | p124 | high | CP31 clarifies 1 ply per V leg | book |
| Layup 6 | 3 plies BID in rib hollow, one laps 4 in inboard | p124 | high | | book |
| Wedge discard | 6 in and 1 in, face 90 deg to TE, drawn | p124 | high | | repr |
| Layup 7 | 3 ply rib, entire area | p124 | high | | book |
| Layup 8 | 3 plies UND 2.5 in wide over LWA6 piece, extends 1 below, 4 / 5.5 / 6 aft | p124 | high | | book |
| LWA7 plate | clamp in place; cover with 1 ply BID, 1 in around (CP25 corrects LWA8 to LWA7) | p124 | high | | cp-corrected |
| Aileron skin cut, top | 5.9 at BL 55.5, 4.35 at BL 106.25, 12 in at outboard, 90 deg ends | p124 | high | | book |
| Aileron skin cut, bottom | 7.6 at BL 55.5, 5.65 at BL 106.25, 12 in at outboard | p124 | high | | book |
| Aileron root clarification | vertical plane; does not pass through bottom 7.6 point (CP34 LPC 107) | cp-text:CP34 p6 | high | | cp-corrected |
| Aileron skin cut saw angle | 120 deg section view | p124 | medium | | repr |
| Layup 9 | wing TE spar glass, 3 plies BID at 45 deg, 1 extra at hinge locations | p124 | high | | book |
| Hinge notch | 0.2 in deep in top skin | p124 | high | | text |
| Layup 9 inboard extension | 1 in into torque tube hole | p124 | high | | text |
| Hinge spacing | 8, 26, 6, 6, 0.2, 51, 6 (top view, TE notches) | p124 | medium (cramped digits) | | text |

### 2.7 Aileron build, controls (p125)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Aileron LE rod | 3/8 dia steel rod bonded after slicing 3/8 foam, full span | p125 | high | | book |
| Hinge halves | reverse before sawing to length | p125 | high | | text |
| A10 tube | extends 1 in inboard of aileron inboard edge | p125 | high | | book |
| A2 and A5 | recess flush; layup 10, 1 ply BID at 45 deg, 1 in lap | p125 | high | | book |
| End ribs | remove 0.4 in foam, 2 plies BID (layup 11) | p125 | high | | book |
| Hinge holes | seven #12 holes (#30 pilot), A3 inboard 3, 3 in; A4 4 in, 0.5 typical | p125 | medium | | text |
| Hinge screws | AN525-10R8 with K1000-3 nutplates | p125 | medium | | text |
| Pop rivets | drill 24 holes; text says 23 rivets for 3 hinges | p125 | medium | see C5 | text |
| Balance | hang by fine wire; max 0.3 lb lead behind the steel bar | p125 | high | | book |
| Mass | no wing or aileron mass printed in p118 to p126 | p118 to p126 | high | | n/a |
| Control throw | stop bolt for 20 deg up (step 11) | p125 | high | | book |
| Belhorn parts | CS132L, CS151, CS152, CS127, CS128; bolts AN3-11A, MS20271-B10 | p125 | medium | cobelu | text |
| Phenolic block | full size on p134 (19-17) | p125 | n/a | out of scope | repr |

### 2.8 Back-cover 3-view (plans-1980:p171)

| Item | Value | Cite | Conf | Cross-check | Use |
|---|---|---|---|---|---|
| Wing root LE at BL 58 | F.S. 113.4 printed (hand marginal says 113.9) | p171 | high on digits as printed; the 4 is the style that reads like 9 | CP25 LPC 7 | cp-corrected |
| Strake/wing kink | labeled BL 58 at the corner, extension line to the FS label | p171 | high | image scale check agrees within about 1 in (low weight) | book |
| Wing tip | BL 157, FS 156 | p171 | high | p126 | book |
| Aileron | BL 54.3 inner, BL 118.1 outer | p171 | high | p126 118.1 | book |
| Canard | BL 71, FS 18.7 leading edge as in model | p171 | medium | | out of scope |
| Wing root | BL 23 shown at the strake edge | p171 | high | | book |
| Margin note | CP25 LPC 7, wing root LE should be 113.9, not 113.4 | p171 | high | | cp-corrected |

## 3. Build-order list (op candidates)

| # | Short name | What is done | Prerequisites | Jig or fixture |
|---|---|---|---|---|
| 0 | Jig templates (19-1, not in scan) | five rib-profile jigs, split with bolted links | ch3 foam and glass basics; A9 to A13 templates | plywood jig blanks |
| 1 | Set jigs LE up | line jigs up straight on floor, 125.6 span | step 0 | floor line, string, level, bondo |
| 2 | Cut planform blocks | lay out angles and cut cores | ch3 hot-wire practice; foam blocks | carpenter-square layout, hot wire |
| 3 | Core hot-wire | cut airfoil sections, spar troughs | step 2 | birch templates, tabs |
| 4 | Core joining | join 14 in blocks into FC1 to FC5 | step 3 | sticks, 5-min epoxy |
| 5 | Torque-tube cutout | cut aileron torque-tube channel in FC1 | step 4 | torque tube templates |
| 6 | FC1 shell | hollow inboard wedge, keep 0.6 in shell | step 4 | bandsaw |
| 7 | Aileron cutouts | inside hot-wire cuts in FC2 and FC3 | step 4 | aileron templates, 3x8 chunk |
| 8 | Light hole | 1 in wire passage in FC4 and FC5 | step 4 | hole templates |
| 9 | Mount cores in jig | FC1 to FC3 micro'd in jig, FC4/5 aside | steps 5 to 8 | jigs, flox dabs top only |
| 10 | Attach depressions | rotary-cut 1.7 in depressions top and bottom | step 9 | rotary file |
| 11 | Hardpoints | notch shear web, bond LWA4 and LWA6, W18 strips | step 10 | none |
| 12 | Shear web layup 2 | 6 plies 45 deg UND, tapering schedule | step 11 | peel ply |
| 13 | Pads and plates (layup 3) | 3-ply BID pads, LWA3 and LWA2 | step 12 | 10 lb weights |
| 14 | Bond LE cores | FC4 and FC5 over shear web | step 12 | jig front pieces |
| 15 | Flip wing, bottom cap | invert on table; 5-ply UND cap | step 14 | dam, hair dryer |
| 16 | Bottom skin | 2 plies UND, BID tip, peel plies | step 15 | 65 in peel ply |
| 17 | Top cap | re-jig; 7-ply UND cap | step 16 | jig top pieces |
| 18 | Rudder conduit | install Nylaflow tube in foam groove | step 17 (before top skin) | dremel, template A12 |
| 19 | Top skin | 2 plies UND, third UND forward of hinge, BID tip | step 18 | peel plies |
| 20 | Incidence board | bond level reference board to top skin | step 19 | level, shims |
| 21 | Wing ribs | rotary-file 0.7 in rib, layups 5 to 8 | step 19 | peel ply removal |
| 22 | Aileron cut | saw skins top and bottom to free aileron | step 19 | razor saw, layout |
| 23 | TE spar glass (layup 9) | 3 plies BID, hinge notches | step 22 | LE-down jig |
| 24 | Aileron hardware | LE rod, A2, A5, A10, layup 10 | step 22 | aileron TE-down |
| 25 | Hinges and balance | install hinges, rivets, balance check | steps 23, 24 | wire hang |
| 26 | Controls | belhorn, CS127, pushrods, stops | step 25 | angle finder |

## 4. CP corrections touching this chapter

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP24 LPC 2 (p19-10) | MEO | add a tie-down hole 13 in inboard, 9.5 in aft of LE; tube flush, AN4 bolts | none on structure; position data only (handwritten on plans-1980:p126) |
| CP25 LPC 7 (back cover) | MEO | wing root LE should be 113.9 not 113.4 | model anchor `wing_le_anchor` already 113.9 |
| CP25 LPC 8 (p19-8, step 9) | MEO | form the 0.7 in rib with a rotary file | text only |
| CP25 LPC 9, 10 (p19-6) | MEO | LWA7 should read LWA2 | part id only |
| CP25 LPC 11 (p19-7) | MEO | LWA7 should read LWA2 | part id only |
| CP25 LPC 12 (p19-8) | MEO | LWA8 should read LWA7 | part id only |
| CP26 LPC 31 (p19-5) | MEO | 3 plies should be 2 plies (BL 120 to 157 shear web) | ply schedule: scan 3, corrected 2 |
| CP26 LPC 32 (p19-3) | MEO | clarify 1 in hole ends at wing top, "0 to 12" | text only |
| CP25 p6 spar-cap box (ch19 step 5 and 7) | MAN-GRD | add extra UND plies if cloth is thin: bottom + BL 25 to 130, BL 40 to 90; top + BL 23 to 140, BL 33 to 92, BL 40 to 78 | ply count: conditional, 5+2 bottom, 7+3 top if tape under 0.18 per 5 ply |
| CP28 LPC 56 | MAN-GRD | the CP25 spar-cap box must be complied with | makes the extra plies mandatory for thin tape |
| CP31 clarification (p19-8) | MEO | layup 5 is one ply per V leg | ply count |
| CP34 LPC 107 (p19-8 step 10) | MEO | aileron root cut is vertical plane at 90 deg to TE | cut geometry |
| CP36 LPC 113 (OM p32) | MEO | aileron balance reads per p19-9 wording | none on geometry |
| CP31 LPC 91 (ch19) | MEO | optional access-hole covers from .016 aluminum | OPT |
| CP45 (cobelu step 8a) | OPT | high-performance rudder conduit reroute | later edition only |

CP numbers for LPC 56 (CP28 p9) and the spar-cap box (CP25 p6) follow the page footers; LPC 64 (snub aileron hinge
pins, p19-17) is CP28 p9 and is outside my pages.

## 5. Conflicts

- **C1. LE FS at BL 106.25.** plans-1980:p126 prints 134.95 (re-read at 10x, glyph pattern is clear as "9").
  The same page prints chord 31.35 and TE 165.8, which give LE 134.45; the 22.98 deg line gives 134.42. The
  hand-lettering renders "4" like "9" elsewhere on the page ("148.4" reads as 148.9 in one place). Graphic
  position on the FS axis gives about 134.3. Neither value is verified without a second page; the 0.5 in
  difference is a captain call. Model impact: none (model uses 22.98 and the root anchor, not this label).
- **C2. 113.4 against 113.9.** plans-1980:p171 prints 113.4; CP25 LPC 7 says 113.9; the p126 derivation gives 113.96.
  The correction and the geometry agree; the print disagrees.
- **C3. Aileron inboard end.** p171 prints BL 54.3; p124 cuts at the BL 55.5 foam joint with an A10 tube extending
  1 in inboard. Both could be true (tube vs skin cut). No page says which dimension p171 means.
- **C4. Root BL.** The plans print BL 23 on p118, p119 and p126; model `wing_root_bl` is 23.3. No page in p118 to
  p126 prints 23.3. The model's 23.3 is a model choice (check outside my scope).
- **C5. Hinge rivets.** p125 says drill 24 holes but names 3 hinges and 23 rivets; the count is internally odd
  (7 hinge screw holes plus 24 rivet holes is a separate matter).
- **C6. Shear web plies.** scan prints 3 plies for BL 120 to 157; cobelu and CP26 LPC 31 say 2.
- **C7. Model washout.** `wing_washout` is 1.0 deg (no cite shown); p126 prints 0.6 washin at BL 55.5, 0.96 washout
  at BL 106.25, 2.7 washout at tip. Reference datum of those angles is not printed.
- **C8. LE and chord line WL.** model `wing_le_wl` zero = WL 17.4 (p134); p126 digit reads 17.4 with a 17.9
  alternate; the jig top/bottom WLs 24.4 and 10.4 come from cobelu only. No conflict proven.
- **C9. Spar tip station.** the model's 129.9 centersection aft face at BL 55.5 (p88) differs from p126's
  shear web foam edge 130.5 by 0.6 in; model value is the spar aft face, p126 is the wing foam face. Different
  surfaces, not a conflict.

## 6. Open questions and low-confidence reads for the captain

1. p126 LE label at BL 106.25: 134.95 or 134.45 (C1). Re-read with the other hand-written 4s on the page.
2. p122 bottom cap ply 5 length: 19.5 or 17.5. Both crops show a hooked digit.
3. p126 note "FS 148.4" / "148.9" and the "FS 149.6" label at BL 55.5: meaning of 149.6 (torque tube line?)
   is not stated on the page.
4. p126 LE line WL: 17.4 or 17.9 (hand 4 versus 9). p118 "W.L.17.4" supports 17.4.
5. p126 thickness at BL 55.5: 16.2 pct (last glyph unclear).
6. Where the wing root chord at BL 23 is meant to start for modeling: book foam LE 125.6 and TE 148.4 give a 22.8
   in aft-only core, not a wing LE. The model's 49.90 root chord at BL 23.3 is a straight-taper extension through the
   strake, not a printed chord.
7. 19-1 (jig templates) is missing from the scan; jig WLs 24.4 and 10.4 are cobelu only.
8. p120 W18 flange dims (.30 top, .25 bottom) and LWA4/LWA6 offset digits are small hand figures; re-read before use.
9. p124 hinge spacing top view digits (8, 26, 6, 6, 0.2, 51, 6) are cramped.
10. Wing and aileron mass: none printed in p118 to p126; only the 0.3 lb aileron balance addition limit.
