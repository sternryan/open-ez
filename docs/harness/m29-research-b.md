# Finishing (chapter 25, p162 to p169): source research (2026-10-04)

Read-only research pass for milestone 2.9, crew B. Every number below was read on the page image (key digits
cropped and enlarged 2x to 3x), not the OCR. 1980 plans cited as `plans-1980:pNNN` (PDF page). Cobelu chapter 25
text (`cobelu`) was diffed against the scan; scan wins. CP text cited as `cp-text:CPnn p<page>`. Owner's Manual cited
as `om-1980:p<printed>` (OM PDF page equals printed page). Paraphrases are ten words or fewer. Nothing in the repo
was edited. The owner holds NO A-sheets: chapter 25 has none (it is a text-and-sketch chapter), the ice-shield
template reference is to page 11-6 (chapter 11, not an A-sheet).

CP page convention used here (checked on a known case): the "CPnn, Page n" footer ends page n, so text between
footer n-1 and footer n is on page n. Check: the CP26 part-weight list sits just above the CP26 page 3 footer. Where a
footer is missing the page is inferred and marked (inferred).

## 0. Answers first (read this)

1. Chapter 25 is plans-1980:p162 to p169 (printed 25-1 to 25-8; p169 prints "last page"). p170 is chapter 26
   (printed 26-1, "last page of plans"); p171 is the back cover three-view.
2. **The chapter prints NO weight of filler, primer or paint and no per-part or total finish weight.** The only
   printed figures are thicknesses (feather fill 0.02 to 0.03 in, primer 0.004 to 0.008 in, weave 0.009 in), fill
   depth bands (0.03, 0.20 in), and mix ratios. All finish-weight data is in CP text (section 4).
3. Best direct finish-weight delta per part (N26MS, same parts weighed "ready to finish" in CP26 p3 and "filled and
   painted" in CP27 p1): canopy +1.0 lb at most, aileron +0.275 lb each, wing (with winglets) about +2.1 to +2.3 lb
   each (derived), elevators about 0 (left 0.00, right -0.25), canard at most +1.5 lb (cover included).
   The fuselage, strakes and cowl finish was never weighed in the held text.
4. Whole-airplane finish benchmarks (all VariEze or Defiant, not Long-EZ): N4EZ 18 lb "too heavy"; over 20 lb "a
   disservice"; builders range 12 lb to 85 lb; Defiant 18 lb. See section 4b.
5. Colour rule: white only on upper wing and canard; dark trim banned there; trim allowed on fuselage, vertical
   winglet surfaces, and underside of wing and canard (plans-1980:p162). Finish temp rule: shop and feather fill at
   least 70 F (p167). Ledger trap: N26MS ladder step 1 (693.4 lb) already contains N26MS's own finish; the OM sample
   730 lb (om-1980:p25) is a different airplane. So no separate finish row should be ADDED on top of a number that
   already includes finish. See section 7.

## 1. Page map (`plans-1980`, confirmed on printed footers)

| PDF | Printed | Content |
|---|---|---|
| p161 | 24-? | last page of chapter 24 (canard cover step 4, wing/centersection seal step 5); out of scope |
| p162 | 25-1 | intro, finish colours and heat, colour curve sheet, tools and materials, optional ice shields |
| p163 | 25-2 | sanding spline construction, five-step finishing process, step one start |
| p164 | 25-3 | step one structural inspection sketches, sections A-A to D-D, 1/16 in and 20 percent rules |
| p165 | 25-4 | step two coarse filling: depth check, hand-sand voids, no hard block |
| p166 | 25-5 | dry micro lump-on, sand to contour, urethane foam block over 0.20 in |
| p167 | 25-6 | step 3 feather fill |
| p168 | 25-7 | step 4 primer, step 5 paint, seals (RTV), mismatch treatment |
| p169 | 25-8 | cockpit interior paint, N-numbers, process photos; prints "last page" |
| p170 | 26-1 | chapter 26 upholstery (out of scope; printed "last page of plans") |
| p171 | none | back cover three-view with stations (used for distribution, section 5) |

Cobelu ch25 figure numbering differs (Figures 25-1 to 25-19) but text matches the scan except the OCR errors noted in section 8.

## 2. Dimension, material and process tables

### 2a. Materials, thicknesses, ratios, temperatures

| Item | Value | Cite | Conf (digit read + why) | Cross-check | Model use |
|---|---|---|---|---|---|
| Epoxy softening temp | 160 F | plans-1980:p162 | high | cobelu same | text |
| Foam softening temp | 250 F | plans-1980:p162 | high | cobelu same | text |
| Black airplane surface temp, still hot day | approaches 220 F | plans-1980:p162 | high | none | text |
| Solar absorption white / black | 10 percent / 95 percent | plans-1980:p162 | high | none | text |
| Colour curve sheet | peak surface temp vs ambient air temp, curves black to white; dashed lines at about 180 F and 95 F ambient | plans-1980:p162 | low: hand lettering on curve labels unreadable at 3x; curve values not read | cp-text:CP16 p6 red runs 50 F hotter than adjacent white; cp-text:CP6 p8 glass resin kept below 120 F by white | repr (graph only, no table printed) |
| Feather fill and shop minimum temp | at least 70 F | plans-1980:p167 | high | cobelu 70; cp-text:CP16 p8 same | text |
| Feather fill build thickness (brush coat) | 0.02 to 0.03 in | plans-1980:p167 text and sketch ".02 TO .03" | high | cobelu same | book |
| Feather fill micro-balloon addition | about 25 percent by volume | plans-1980:p167 | high | cp-text:CP21 p6 says 25 to 50 percent; see conflict C2 | book |
| Glass weave roughness | 0.009 in | plans-1980:p167 sketch (cropped 3x, reads ".009 INCH") | high | none | book |
| Primer coat thickness | 0.004 to 0.008 in | plans-1980:p168 sketch (cropped 3x) | high | none | book |
| Fill depth bands | under 0.03 in: feather fill; 0.03 to 0.20 in: dry micro; over 0.20 in: urethane foam block with 1 or 2 plies BID | plans-1980:p165, p166 | high | cobelu same | book |
| Micro cure before sanding | at least 24 hours | plans-1980:p166 | high | none | book |
| Sanding into skin allowance | first skin ply only, local areas up to 2 in diameter, total under 5 percent of surface area | plans-1980:p167 | high (read twice) | none | book |
| Over 95 percent of feather fill sanded off | sketch note | plans-1980:p167 | high | none | text (mass relevance: most feather fill leaves as dust) |
| Inspection thresholds | dip or hump over 1/16 in over more than 20 percent of local chord requires repair | plans-1980:p164 | high | cobelu same | text |
| Ruler check pointer | "12 in ruler check, page 3-13" | plans-1980:p163 | medium (hand-lettered) | cp-text:CP16 p4 feeler gauge: gap over 0.006 in too wavy | text |
| Sandpaper grits | 36 to 60 coarse (micro); 100 (feather fill); 220 then wet 320 (primer); 320 light before N-numbers | plans-1980:p162, p166, p167, p168, p169 | high | cobelu says "35 to 60" on p166 and "36 to 60" elsewhere; scan p166 text reads "35 to 60", sketch reads 36 to 60 | text |
| Sanding screen | 3M 18N Fabricut Wetordry silicon carbide 180 | plans-1980:p167 | high | cp-text:CP18 p5 (VariEze plans change) | text |
| Primers named | Dupont 70S, 100S, or 3011S dark grey lacquer primer/surfacer | plans-1980:p162 | high | cp-text:CP41 p4: 131S replaces discontinued 100S | text |
| Bondo density warning | not printed here | none | n/a | cp-text:CP12 p2 Bondo 12 lb per gal, dry micro 3 lb per gal | derived/text |
| RTV seal cure | at least 2 days before parts are separated; white silicone | plans-1980:p168 | high | none | text |
| Sanding spline | 9 in by 9 in; 4 to 6 ply BID over waxed paper; 9 in square blue polystyrene foam pad 3/8 to 1/2 in thick (digits "3/8 TO 1/2" medium, hand sketch); two 1x1 or 1x2 handles 9 in long | plans-1980:p163 | medium on foam thickness | none | text (shop tool, not an airframe mass) |
| Mismatch treatment | dry micro lumped on high, grey tape guard, sand fair | plans-1980:p168 | high | none | text |

### 2b. Ice shield (optional, canard balance weight)

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Ice shield layup | 3 plies BID over the balance weight | plans-1980:p162 | high | none | repr (optional, not in the standard airframe) |
| Shield trim height | 0.6 in below canard bottom | plans-1980:p162 (cropped 2x, "0.6") | high | none | repr |
| Overlap onto canard skin | 1/2 in | plans-1980:p162 | medium: fraction symbol small, text and OCR say 1/2 | cobelu 1/2 | repr |
| Clearance tape | at least 8 thicknesses grey duct tape | plans-1980:p162 | high | none | repr |
| Elevator position for layup | 10 degrees T.E. up, 2 hinge screws, template on page 11-6 | plans-1980:p162 | high | none | repr |
| Sand featherfill to bare glass | out to 1/2 in from balance weight | plans-1980:p162 | medium | none | repr |
| Shield mass | not printed | none | n/a | none | no arm, no weight (3 plies BID; area not printed) |

### 2c. Parts and surfaces: finish scope (no station, arm or weight printed in chapter 25)

Chapter 25 prints no FS, BL or WL. Parts it mentions, with the stations the back cover (plans-1980:p171) prints for
distributing finish mass, all read from the image (medium to high; small print, blurred ink spots):

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Nose tip | FS -6.8 | plans-1980:p171 | medium: "-6.8" small | none | book (extent) |
| Canard span station | BL 71 at tip, FS 18.7 | plans-1980:p171 | medium: "18.7" small | none | book (extent) |
| Wing root TE and tip | root LE FS 113.9 (hand-corrected from 113.4), tip FS 156 at BL 157 | plans-1980:p171; hand note CP25 LPC 7 | high on hand note | cp-text:CP25 LPC 7 (MEO) | book |
| Winglet top | FS 196.6, WL 66.4 | plans-1980:p171 | medium | none | book |
| Main wheel axle | FS 110.5, WL -22 | plans-1980:p171 | high | m28 report same | book |
| Nose wheel | FS 17, WL -22 (hand-corrected from -25 or -23, CP25 LPC 24) | plans-1980:p171 | high | m28 report same | book |

These give extents only. Finish mass placement uses the part arms from earlier chapters; chapter 25 gives no
distribution of filler, primer or paint over the airframe. Surface areas are not printed in chapter 25.

## 3. Build-order list (op candidates)

| Step | What is done (paraphrase) | Prerequisites | Jig/fixture |
|---|---|---|---|
| F0 spline | make hand sanding spline | ch3 education layup scrap | none |
| F1 inspect | inspect and repair every structure | chapters 3, 10 to 24 complete | 12 in ruler, feeler gauge |
| F2 coarse fill | hand-sand voids, lump dry micro | F1; epoxy tack coat | none |
| F2b gross fill | foam block plus 1 or 2 BID over 0.20 in | F2 | none |
| F2c contour | sand micro fair with 36 to 60 grit | F2 cured 24 h | spline, hard block |
| F3 feather fill | brush fill on glass, sand with 100 grit | F2c; shop at least 70 F | spline, soft block |
| F3b ice shield | optional 3 ply BID shield on canard | F3 sanded; elevator hung at 10 degrees | duct tape clearance |
| F4 primer | two coats UV primer, sand 220 then 320 | F3 (feather fill never over primer) | spray rig |
| F5 paint | finish coat per maker | F4 | spray rig |
| F6 seals | RTV gap seals wing root, canard, cowl | F5 colours chosen white | Saran Wrap release |
| F7 interior | one primer coat then colour on cockpit glass | F1 | mask nose-gear window, fuel gauges |
| F8 marks | adhesive or painted N-numbers | F5 | masking, 320 grit |

Dependency note: ice shield goes on AFTER featherfill but is optional; chapter 25 gives no order between canard
paint and the elevator hang.

## 4. Weights (the key ledger inputs)

### 4a. Direct N26MS finish deltas: CP26 p3 (ready to finish) vs CP27 p1 (filled and painted)

CP26 p3 and CP27 p1 are one airplane (Melvill N26MS). Figures read from cp-text, converted to decimal lb (oz/16).

| Part | CP26 p3 "ready to finish" | CP27 p1 "filled and painted" | Delta | Cite | Conf | Model use |
|---|---|---|---|---|---|---|
| Canopy | 16 lb ("complete ready to finish") | 17 lb "with hinges" | +1.0 (upper bound; hinges may be in only the painted figure) | cp-text:CP26 p3; CP27 p1 | medium: configuration wording differs | derived |
| Left elevator | 3 lb 8 oz = 3.5 | 3.5 | 0.0 | CP26 p3; CP27 p1 | medium | derived |
| Right elevator | 3 lb 4 oz = 3.25 | 3.0 | -0.25 | CP26 p3; CP27 p1 | medium: negative delta means weighing noise or sanding loss | derived |
| Aileron (each) | 5 lb 2 oz = 5.125 (mass balance, hinges, torque tube, universal) | 5.4 each (hinges, universal, torque tube) | +0.275 | CP26 p3; CP27 p1 | medium | derived |
| Canard | 17 lb "no hardware, no elevators" | 18.5 "with fairing cover" | +1.5 at most (includes the canard cover/fairing, so finish alone is less) | CP26 p3; CP27 p1 | low: configuration not matched | derived (bound) |
| Rudder (each) | not weighed alone | 1.2 | n/a | CP27 p1 | high | text |
| Wing with winglets, no rudder or aileron | 64 "before finish" incl. ailerons and rudders | 60 "filled and painted" (no rudders, no ailerons) | about +2.1 to +2.3 per wing | derived below | medium-low | derived |

Wing derivation. Unfinished wing 64 lb includes aileron and rudder. Remove aileron 5.125 and rudder r:
64 - 5.125 - r. With r = 1.2 (painted weight, so finish on rudder = 0): 57.675, delta to 60 = +2.325. With r = 1.0
(rudder finish 0.2): 57.875, delta +2.125. So +2.1 to +2.3 lb per wing, +4.2 to +4.7 lb for two wings.
Both ends carry a hidden assumption (the unfinished rudder weight is not printed).

Sum of measured N26MS finish on weighed parts (wings 2x(2.1..2.3), ailerons 2x0.275, elevators -0.25, rudders about 0..0.4,
canopy at most 1.0, canard at most 1.5): about 5.0 to 8.2 lb. Fuselage, strakes, cowl, speed brake, gear fairings
and cockpit interior paint have NO finish weight in any held source.

### 4b. Whole-airplane finish weight guidance (CP text; VariEze or Defiant unless marked)

| Item | Value | Cite | Conf | Note |
|---|---|---|---|---|
| N4EZ finish weight | 18 lb "too heavy" | cp-text:CP12 p2 | high | VariEze prototype; text also says over 20 lb added in finishing is "a disservice" |
| N4EZ materials used | 5 quarts feather fill, 1.3 gal paint | cp-text:CP12 p2 | high | gives 18 lb |
| Heavy example | 11 gal Featherfil, 6 gal white paint | cp-text:CP12 p2 | high | airplane 140 lb overweight overall |
| Cessna 150 comparison | leaves paint shop 13 lb heavier, twice VariEze area | cp-text:CP12 p2 | high | context |
| Range seen | finishes as light as 12 lb, as heavy as 85 lb | cp-text:CP14 p4 | high | VariEze era |
| N4EZ first flight | 570 lb "including an extra heavy paint job" | cp-text:CP13 p4 | high | conflicts mildly with CP12 18 lb "too heavy" (consistent: heavy for VariEze) |
| Defiant finish growth | 18 lb with 4 gal feather fill, 5 gal 70S, 1.5 gal Centari; 2 to 3 times VariEze area | cp-text:CP17 p5 | medium: 18 lb equals N4EZ despite larger area (see C4) | Defiant, twin |
| Featherfill cap (VariEze) | 1.5 gal at most; two or three applications | cp-text:CP21 p6 | high | supersedes Section V |
| Bondo / dry micro | 12 lb per gal / 3 lb per gal | cp-text:CP12 p2 | high | basis for "dry micro, not Bondo" |
| VariEze wing, before vs after finishing | complete wing/winglet/aileron 43 lb before, 46 lb after: +3 lb each | cp-text:CP20 p5 | high | VariEze; the Long-EZ equivalent delta is 2.1 to 2.3 lb (4a); both use the same 43 and 46 only as before/after of one build |
| VariEze canopy | 14.5 lb (end of its chapter 22) | cp-text:CP20 p5 | high | context for canopy 16 to 17 lb |
| Prefab VariEze wing | weight saving "negligible" | cp-text:CP24 p4 | high | no mass input |
| Empty weight add-on law | 3 to 10 percent of empty weight sneaks in | cp-text:CP28 p6 | high | seat cushion 5 lb vs 4 lb used as example; context only |

### 4c. OM weight items touching this chapter

| Item | Value | Cite | Conf | Model use |
|---|---|---|---|---|
| Normal equipped empty weight | about 750 lb | om-1980:p4 | high | text; sample is 730 lb at FS 111.7 (om-1980:p25, p35) |
| Sample empty weighing | R main 373.7 net at 110.5, L main 372.0 at 110.5, nose 7.2 at 19.6, ballast -25 at 40.0, empty 730 at 111.7, moment 81541 | om-1980:p35 | high on printed values | book (closure target) |
| Paint and colour statement | white acrylic enamel or lacquer, dark UV primer | om-1980:p44 | high | text |
| Equipment-list prompt | paint type, trim type, interior type listed as items that determine empty weight | om-1980:p65 | high | text |

## 5. Distribution of filler, primer and paint

Nothing printed in chapter 25 says how much goes where. What the held sources give:

- Finish thickness is area-based: feather fill 0.02 to 0.03 in brushed, primer 0.004 to 0.008 in, with 95 percent of
  feather fill sanded off (plans-1980:p167). Surface areas are not printed in chapter 25, so mass per area cannot be
  derived without them plus feather-fill and primer densities (neither is printed; micro 3 lb per gal is the only
  density, CP12 p2).
- Per-part N26MS finish deltas in 4a are the only measured distribution. Largest per wing about 2.2 lb including
  winglets; canopy up to 1.0 lb; canard up to 1.5 lb with cover.
- Interior: cockpit gets ONE primer coat, no fill (plans-1980:p169). CP27 p5 (inferred page) says Zolatone sprayed
  straight on scuffed glass, no fill; CP32 p6 says Zolatone is enough UV barrier, no primer. Weight: not printed.
- Colour distribution: white upper wing and canard (plans-1980:p162). Dark trim allowed on fuselage, vertical winglet
  surfaces, wing and canard undersides. Stripe not allowed on wing or canard except canard tip.

Suggested ledger placement if forced (labelled derived, not book): distribute finish mass in proportion to part wetted area
using the 4a deltas as the wing, canopy, canard anchors; fuselage and strakes remain unsourced.

## 6. CP corrections touching chapter 25

No LPC number in the CP text names page 25-x for the Long-EZ chapter (grep of "Page 25-" returns only a VariEze
plans-change line). Corrections that change chapter 25 content:

| CP entry | Class | What changes | Model impact |
|---|---|---|---|
| CP11 p7 (22-7 "blank should read See page 25-1", VariEze list) | MEO | pointer only | none |
| CP18 p5 (VariEze Section V p6) | MEO | 36 grit before feather fill; no wet sanding; no fill over primer; 18N screen | already folded into plans-1980:p167 |
| CP19 p5 (Section V) | MEO | Dupont 100S can replace 70S | already in plans-1980:p162 |
| CP16 p10 (Section V) | DES | add "check surface contour per CP16" (ruler and 0.006 in gap) | text only |
| CP16 p10 (Section V) | OBS | NUL-V paint discontinued; use acrylic lacquer, enamel or acrylic enamel | none |
| CP21 p6 (featherfill bulletin) | DES | fog coat 10 to 20 min, 25 to 50 percent micro balloons, 100 grit, 2 or 3 coats, 1.5 gal cap (VariEze) | text; conflicts with plans 25 percent (C2) |
| CP26 p7 (inferred page) finishing caution | DES | never wipe thinners on structure; seal pin holes with epoxy before featherfill or primer | text; no mass |
| CP27 p5 (inferred) cockpit paint | DES | Zolatone charcoal grey, 70 psi, scuff-sand, no filling; 70S best UV barrier | text; interior finish weight unsourced |
| CP28 p4 (care of composite structures) | DES | repair paint chips at once (UV and water) | none |
| CP32 p6 | DES | Zolatone no primer needed, scuff with 40 grit | none |
| CP41 p4 | DES | 131S replaces 100S primer; prefer urethane top coat; keep one maker's system | none |
| CP45 p5 | DES | West dry micro sands in 4 to 5 h; Sterling or Morton primer fill | none |
| CP22 p4 | OPT | sanding sponge tip for feather fill to colour coat | none |
| CP6 p8, CP16 p6 | DES | white only; red stripe ran 50 F hotter | text (colour rule) |
| CP25 LPC 7 (plans back cover) | MEO | wing root LE FS 113.9 not 113.4 | already hand-written on p171 |

## 7. Ledger-closure inputs: what the current ledger is missing or carries unsourced

Ledger has no finishing row at all (grep: "paint", "finish", "primer" appear only in config comments and in N26MS notes).
`config/aircraft_config.py` `task_credits.finishing` is a 51 percent rule credit, unrelated to mass.

| Mass | Best held source | Arm | Status |
|---|---|---|---|
| Finish (filler, primer, paint), whole airplane | N26MS part deltas 5.0 to 8.2 lb (4a); VariEze benchmarks 12 to 20 lb and N4EZ 18 lb | none printed; use part arms | derived range, fuselage unsourced |
| Canopy painted | 17 lb with hinges (CP27 p1) | no arm printed | already noted as reference only in ledger |
| Canard painted | 18.5 lb with cover (CP27 p1) | canard LE FS 18.7 region from p171 only | not in ledger |
| Elevators painted | 3.5 and 3.0 lb (CP27 p1) | no arm | not in ledger |
| Ailerons painted | 5.4 lb each | no arm | not in ledger |
| Rudder painted | 1.2 lb each | no arm | not in ledger |
| Cowl | glass 18 lb, graphite 12 lb (CP27 p5); ledger has these as reference | no arm printed | reference only |
| Upholstery (cushions, headrests, suitcase) | not weighed in held sources; CP28 p6 mentions a "5 lb vs 4 lb seat cushion" as example only | no arm | unsourced (chapter 26 is crew C's) |
| Seat belts, instruments | N26MS ladder step 6 and 8 lump items (38.1 and 22.8 lb) include "primer", upholstery, small items | no arm | unsourced |
| OM equipment list items | prompt only (om-1980:p65) | back cover says use plans back cover for station | no weights |

Closure traps:
- N26MS ladder step 1 (693.4 lb) is painted and complete as flown; it is not an unfinished weight. Adding a finish row to
  a total built from N26MS "ready to finish" part weights (CP26 p3) is correct; adding it to ladder step 1 double counts.
- Step 6 lists "primer" among extras (CP27 p4). It is not clear whether this is cockpit primer or a coat on
  something not in step 1. Flagged (Q3).
- OM 730 lb at 111.7 vs OM "about 750" (p4): the OM calls 750 normal equipped, 730 is the sample.

## 8. Conflicts

| ID | Sources | Disagreement |
|---|---|---|
| C1 | config WEIGHT_PROVENANCE cites "60 lb painted ... CP26 p16"; cp-text footer order puts that list at CP27 p1 (text sits after the CP26 p16 footer, before the CP27 p1 footer) | page citation differs by issue, not by value |
| C2 | plans-1980:p167 feather fill with about 25 percent micro balloons; cp-text:CP21 p6 25 to 50 percent and "supersedes Section V" (VariEze) | ratio differs; no Long-EZ-specific correction found |
| C3 | plans-1980:p166 text "35 to 60-grit"; sketch "36 to 60" same page; cobelu has both | one-digit typo in plans text |
| C4 | cp-text:CP17 p5 Defiant 18 lb on 2 to 3 times VariEze area vs cp-text:CP12 p2 N4EZ 18 lb "too heavy" | same weight on 2 to 3 times the area; not reconciled in text |
| C5 | CP26 p3 right elevator 3 lb 4 oz (3.25) vs CP27 p1 filled and painted 3.0 | painted lighter than unpainted; delta -0.25 |
| C6 | OM p4 "approximately 750" vs OM p25 and p35 sample 730 | OM internal, not a sourcing conflict |

## 9. Open questions and low-confidence reads

1. Colour curve sheet (plans-1980:p162): curve labels and the two dashed reference lines are too small to read; the
   graph gives only a shape. Needs a higher resolution scan or a human read.
2. Foam pad thickness on the spline (p163, "3/8 to 1/2"): hand sketch, medium.
3. "primer" in N26MS ladder step 6 (CP27 p4): ambiguous, ask whether step 1 includes cockpit primer.
4. CP26 p7 and CP27 p5 page numbers are inferred (missing footers: CP26 p7 and CP27 p5 footer lines absent).
5. Unfinished rudder weight is not printed; needed to tighten the wing finish delta (4a).
6. Canopy hinges in or out of CP26 p3's 16 lb? Changes the +1.0 delta to between 0 and +1.0.
7. No fuselage, strake, cowl or interior finish weight anywhere in the held text. Is there a CP weighing a painted fuselage
   (the CP26 p3 "183 lb fuselage" is ready-to-finish; no painted twin found)?
8. OM p25 and p35 close on 730 lb; whether the OM sample includes finish is not stated.
