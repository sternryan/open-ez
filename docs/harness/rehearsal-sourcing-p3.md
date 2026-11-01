# Rehearsal sourcing, P3-A (ground school)

Research for the education lessons that replace the `c03.layup-skills` stub. Read 2026-10-21.
Plans pages were not opened (the scan is private). Nothing in this file is a plans quotation.
Lesson text in the graph is our own words. A quote below is ten words or fewer.

Flag rules are the P1 ones (`rehearsal-sourcing-p1.md`). `official` is not used: no plans page
was opened. A builder's own stated chapter time, split by me, is `estimate`. A number with no
opened source is omitted (`unsourced`, value null), not invented. Buy quantities are net. No scrap.

## 1. Sources used

| key | what | URL | read | used for |
|---|---|---|---|---|
| TDS | MGS L285 / hardeners 285, 286, 287, edition `L285_eng_200106` (registry `mgs-l285-tds`) | https://www.aircraftspruce.com/catalog/pdf/mgs285tech.pdf | 2026-10-21, text of the PDF | processing range, mix ratio, density, fillers. Printed headers 1.1-10 through 1.1-14. The resin file already cites `mgs-l285-tds:p1` for the 10 °C floor, and 1.1-10 is the first page of this file, so p1 = 1.1-10, p2 = 1.1-11, p3 = 1.1-12, p4 = 1.1-13 |
| FAA | AC 43.13-1B with Change 1, 8 Sep 1998 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf | 2026-10-21, paras 1-18 to 1-20 and 3-1 to 3-2 only | ventilation, sanding dust, peel ply, the latex-glove note. The rest of the AC was not read |
| NIOSH | HHE 2011-0180-3193, dermatitis among sanders | https://www.cdc.gov/niosh/hhe/reports/pdfs/2011-0180-3193.pdf | 2026-10-21, the Personal Protective Equipment recommendation and the sensitization discussion | skin sensitization; which gloves do not stop DGEBA epoxy. Printed page breaks 9 to 11 did not survive the text extract; the glove paragraph sits after the page 8 header and before the page 12 header |
| AS-CLOTH | Aircraft Spruce, Rutan fiberglass cloths | https://www.aircraftspruce.com/catalog/cmpages/rutan.php | 2026-10-21 | 38 in width, BID vs UND fiber direction, 8.8 oz per square yard for 7725, 7 oz listed for 7715 |
| AS-KIT | Aircraft Spruce composite practice kit | https://www.aircraftspruce.com/catalog/cmpages/practicekit.php | 2026-10-21 | what that kit actually contains. Not used as a buy |
| GLANTZ-T | Long-EZ log, time and budget | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | 2026-10-21 | chapter 3, 9 h, 26 Jan to 5 Feb 2013, cost $160 |
| GLANTZ-FLAT | same log, the flat layup | https://www.aryjglantz.com/2013/03/the-flat-layup.html | 2026-10-21 | 6 BID plies, weight band, his result 10.1 oz |
| GLANTZ-BEAM | same log, the load beam | https://www.aryjglantz.com/2013/03/the-load-beam.html | 2026-10-21 | urethane beam, squeegee to the edges, his heater cure |
| GLANTZ-END | same log, the bookend | https://www.aryjglantz.com/2013/03/the-bookend.html | 2026-10-21 | urethane bookend, dry micro corner, 1/4 in flox bead, sand dull |
| MEAT | Long-EZ project blog, education part 1 | https://longezproject.blogspot.com/2011/11/chapter-3-education-part-1.html | 2026-10-21 | finished rectangle 10 by 16 in, same weight band, his result 10.06 oz |
| GLANTZ-SIDE | same log as P1, one side's inside glass | https://www.aryjglantz.com/2013/03/fuselage-wall-left-side-inside-glassing.html | not re-read this round; P1 opened it 2026-10-17 | the later pattern that one person mixes while another wets out. Used only as the reason the buddy pair exists |

Not used, and not opened in full:

- A 2022 MGS sheet (search snippet only) that prints volume ratio 51 ± 2. The 2006 sheet opened here prints 100:50 ± 2 by volume. The snippet is UNCONFIRMED.
- HexForce 7725 / 7715 PDFs. Not opened. Areal weight comes from AS-CLOTH, not from those sheets.
- Lutorm's practice-layup posts. The January 2013 URL returned 404. His 6.5 oz cloth figure is UNCONFIRMED and is not used.
- The MGS safety data sheet. Not opened. Which glove polymer that sheet names is UNCONFIRMED.
- Plans chapter 3. Not opened.

## 2. What the lessons are

Three practice pieces show up in the opened logs, in this order: a flat 6-ply BID rectangle, a urethane load beam, a urethane bookend. Glantz calls the bookend the last piece in the practice chapter. Shop, tools, mixing, cloth direction, peel ply, and micro/flox are the skills those pieces use. They are separate lessons so the player can show them. Their hours are not in any log.

| id | title | what a first layup has to teach |
|---|---|---|
| g00.shop-setup | Shop air, temperature, and skin | Where the resin may be worked, moving air, sanding dust, sensitization |
| g00.tools | Gloves and the bench tools | The owner pair, the buddy pair, and the prop set |
| g00.mix | Weigh the resin | 100:40 by weight, stir the cup walls |
| g00.orientation | Which way the fibers run | BID on the bias, UND along the warp |
| g00.flat-layup | Six-ply practice rectangle | Wet out, squeegee, cure, then weigh |
| g00.peel-ply | Peel ply over a wet face | Leave it on through the cure |
| g00.micro-flox | Micro corner and flox bead | Light filler versus structural paste |
| g00.foam-shape | Shape practice foam | Hot-wire pass, sand, string, level |
| g00.load-beam | Practice load beam | Urethane core, spare resin to the edges |
| g00.bookend | Practice bookend | Last practice piece. Later build steps require this id |

## 3. Shop, gloves, temperature

**Temperature.** TDS p1: processing at 10 to 50 °C, all usual methods. TDS p4: the optimum band is 20 to 40 °C; a 10 °C rise halves pot life; water in the cloth or the filler speeds the reaction. Storage on p2 is 15 to 30 °C. No work-again curve, same gap as P1. Gel time for hardener 287, 1 mm film, is about 5 to 6 h at 20 to 25 °C (p4). That is gel time, not the time until the part can be worked. It is not `gate_hours`. Practice layups that cure use `mgs-285-287` and `cure: part`. The gate stays empty, so the wait shows as unknown.

**Air and dust.** FAA para 1-20 sits in the wood chapter and names epoxy anyway: use the protection the product sheet calls for, and move shop air so adhesive fumes do not sit in the room. Para 3-2: sanding fiberglass dust can irritate skin and breathing unless protection is worn, and the dust carries a static charge that holds dirt. Moisture left on a laminate stops the resin curing (same paragraph). Those two points are the shop lesson.

**Skin.** NIOSH: people who get uncured epoxy on skin can become sensitized; hands and forearms first, face and neck if the hardener is airborne or carried by the hands. Once sensitized, stay away from it. Gloves they name for DGEBA epoxy are polyvinyl alcohol and the multilayer brands Barrier, Silver Shield/4H, and Tychem. Natural rubber, neoprene, polyethylene, and PVC do not stop it. The TDS (p2) says people who reacted to other epoxies have often been able to use L285, and in the same paragraph tells the reader to follow the industrial safety rules and Hexion's own safe-processing instructions. The tolerance sentence does not replace the glove rule. The MGS safety sheet was not opened, so the polymer MGS itself names is UNCONFIRMED.

**Conflict, left visible.** FAA para 3-1 says latex gloves and an approved mask when handling prepreg, prepared surfaces, or those materials, and to read the safety sheet. That note is about prepreg handling. This build is wet layup. NIOSH, opened the same day, says natural rubber does not protect against DGEBA epoxy. The lesson follows NIOSH for wet resin and does not teach the latex sentence as the glove for this shop.

**Buddy pair.** `g00.tools` is `people: 2` so the second glove pair appears. The reason is the later pattern P1 recorded from GLANTZ-SIDE: one person mixes, the other wets out. Laying tools on the bench does not itself need two people. The second pair is the demonstration the player uses from here on.

## 4. Cloth direction, mix, peel ply, fillers

**Direction (AS-CLOTH).** Both cloths are 38 in wide, sold by the yard. BID has half its fibers along the selvage and half across it, so the two directions match. It is generally cut at 45 degrees to the selvage, which lets it lie into a contour and carries shear. UND has 95 percent of its fibers along the selvage and is used where the load runs one way, such as skins and spar caps. A ply is one layer. The page's square-yard question is answered "8.8 oz/yd" for 01-00642 (BID 7725). The uni line on the same page says 7 oz at 38 in, and a different answer says approximately 7.0 oz per yard. Those two uni wordings are not the same unit. No UND buy uses them.

**Mix (TDS p4).** By weight 100:40 ± 2. By volume 100:50 ± 2. Extra or missing hardener does not speed or slow the cure; it leaves a cure that cannot be fixed. Stir until the cup is clear, including the walls and the bottom. The lesson weighs. It does not teach the volume ratio as the method.

**Fillers (TDS p2).** The sheet names microballoons and cotton flakes (and Aerosil and metal powder) as fillers you may add. It gives no ratio. Glantz's bookend uses dry micro so the glass does not turn a sharp inside corner, and a 1/4 in flox bead on the bottom lip before the last plies. He gives no length, so there is no volume. Micro and flox stay out of `buy`, the P1 rule.

**Peel ply (FAA para 3-2).** Cover the wet resin with peel ply so air stays off it while it cures, then take the ply off and sand to contour. No practice area is printed in any opened log, so there is no peel-ply buy. Glantz's flat-layup post does not mention peel ply.

## 5. The flat rectangle (the only quantified buy)

MEAT: after the cure, trim to a 10 by 16 in rectangle; the weight should fall between 10.5 and 12.5 oz. Heavier means too much epoxy, lighter means too little. His piece was 10.06 oz and he says he cut it slightly small. GLANTZ-FLAT: 6 BID plies, same 10.5 to 12.5 oz band, and he calls 11 oz the weight that means the ratio is right. His piece was 10.1 oz. He says he drew the rectangle the plans show, but he does not print the inches. The 10 by 16 in comes from MEAT, one builder. It is UNCONFIRMED as a plans dimension.

Finished cloth, no trim allowance (both builders trimmed after cure, so this reads low):

- 6 × 10 × 16 = 960 in².
- 38 × 36 = 1368 in² per linear yard. 960 / 1368 = 0.702 yd, bought as **0.70 yd** of `bid-7725`.
- 960 / 1296 = 0.7407 yd². × 8.8 oz/yd² = **6.52 oz of cloth**.

Resin from Glantz's 11 oz "right" weight, not from the 1:1 rule. 11.0 − 6.52 = 4.48 oz mixed. At 1:1 the same cloth wants 6.52 oz of resin and the rectangle would weigh 13.0 oz, over the 12.5 oz top of the band, so 1:1 is the wrong rule for this piece.

Split 100:40 (TDS p4): resin 4.48 × 100/140 = 3.20 oz, hardener 1.28 oz.

Density midpoints, my choice, TDS p3 ranges 1.18–1.23 and 0.93–0.96 g/cm³: 1.205 and 0.945. One gallon is 3785.4 cm³, so resin is 4.561 kg/gal. One quart is 946.35 cm³, so hardener 287 is 0.894 kg/qt. One ounce is 28.35 g.

- Resin 3.20 oz → 90.7 g → **0.020 gal** of `mgs-lr285-gal`.
- Hardener 1.28 oz → 36.3 g → **0.041 qt** of `mgs-h287s-qt`.

All three flags are `estimate`. The sourcing record is the citation. No scrap, no overlap, no peel ply.

## 6. Hours

GLANTZ-T: chapter 3 practice layups, **9 h**, 26 Jan to 5 Feb 2013, cost $160. His chapter index lists the flat layup, the load beam, and the bookend, and no other chapter 3 part. The $160 is not itemized, so it prices nothing.

No post times one piece. The 9 h is split evenly, **3 h** each, on `g00.flat-layup`, `g00.load-beam`, and `g00.bookend`, flag `estimate`. That even split is the weak number in this file. The other seven lessons have no timed log. They are `unsourced` with a null value. Some of those seven may already sit inside the 9 h. They are not given a share, so a session packer that budgets a default hour for a null will count them again. That double count is left visible rather than folded into the 3 h.

## 7. Opening kit, and the kit that was not used

The ground-school group is the first buy point. The only lines with a sourced quantity are the three on `g00.flat-layup` (section 5). Beam, bookend, micro, flox, peel ply, and UND have no opened size, so they are not bought here.

AS-KIT (01-15100 without the book, and the with-book table) was opened and rejected as this opening kit:

- The resin is West System 105 with 206 slow hardener, not MGS L285 / H287.
- The gloves are latex, part 01-01586. Section 3 records why latex is the wrong glove for this wet layup.
- Quantities are fractions of a retail pack (2.25 yd BID, 1.25 yd UND, and slices of foam, bubbles, and cups). They are that product's bill, not the Long-EZ practice pieces.
- One component line, part 01-14950, quantity 0.02, has a blank name on the page. What it is is UNCONFIRMED.
- The kit's own selling price was not on the page that loaded. UNCONFIRMED.

## 8. Per-lesson plan

| id | people | cure | hours | buy | notes |
|---|---|---|---|---|---|
| g00.shop-setup | 1 | none | none | none | TDS p1 and p4, FAA 1-20 and 3-2, NIOSH |
| g00.tools | 2 | none | none | none | buddy pair is the demonstration, section 3 |
| g00.mix | 1 | none | none | none | TDS p4, by weight |
| g00.orientation | 1 | none | none | none | AS-CLOTH. No UND quantity |
| g00.flat-layup | 1 | part | 3 est | BID 0.70 yd, resin 0.020 gal, hardener 0.041 qt | section 5 |
| g00.peel-ply | 1 | none | none | none | FAA 3-2. No area |
| g00.micro-flox | 1 | part | none | none | TDS p2 names the fillers; Glantz bead has no length |
| g00.foam-shape | 1 | none | none | none | hot-wire pass is the prop demonstration. No opened chapter 3 post describes a hot-wire cut. UNCONFIRMED as a plans step |
| g00.load-beam | 1 | part | 3 est | none | urethane, size not printed. His 160 °F for 3 h is his heater, not the TDS post-cure (80 °C for motor planes, p2, no 3 h figure) |
| g00.bookend | 1 | part | 3 est | none | last lesson. 2 in urethane from two 1 in boards in his shop; blank area not printed. Ply counts not printed |

## 9. Open gaps (UNCONFIRMED)

- Plans chapter 3 itself: pages, the practice-piece drawings, ply counts on the beam and the bookend, foam blank sizes, and whether the education chapter uses a hot wire.
- The 10 by 16 in rectangle as a plans dimension (one builder states it; the plans page was not opened).
- UND areal weight: the cloth page says both "7 oz" at 38 in and "approximately 7.0 oz / yd".
- MGS safety-sheet glove polymer.
- The 2022 sheet's volume ratio 51 ± 2 (snippet only).
- Lutorm's cloth weight and any 200 lb beam figure (post not opened; Glantz's beam post says he stood on it, and gives no pound figure).
- Peel ply, micro, flox, and beam/bookend cloth quantities.
- Practice-kit selling price, and part 01-14950's name.
- Per-piece hours. The 3 h split is even. Owner actuals are the real fix.
- Work-again time against temperature: still not in this TDS edition.
