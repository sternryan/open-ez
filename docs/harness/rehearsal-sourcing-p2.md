# Rehearsal sourcing, P2

## p2-ch06-09-sourcing.md

# Rehearsal sourcing, P2 (chapters 6 to 9, 35 ops)

Research only. Read 2026-10-18. No repo file was changed. The values file is
`p2-ch06-09-plan-values.yaml` in this directory; this record holds the evidence, the arithmetic and
the gaps for it. Method, constants and flag rules are the P1 ones (`rehearsal-sourcing-p1.md`).

Plans text: I did not read the plans pages. Step content comes from the repo's summaries in
`guide/graph/ch06.yaml` to `ch09.yaml`, dimensions from `config/aircraft_config.py`, and cloth areas
from the repo's ply model `core/fuselage_plies.py` (run read-only on the committed graph; it
measures the book or fitted solids). No op in these four files is a stub or `[gu]`-only, so all 35
are covered.

Every value passes the repo's own Contract 2 parser (`guide.schema._plan`), checked 2026-10-18.

## 1. Sources used

| key | what | URL | used for |
|---|---|---|---|
| GLANTZ-T | Long-EZ blog, time and budget page | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | **ch6 60 h** (4/15 to 6/9/2013), **ch7 39 h** (6/10 to 7/22), ch8 17 h (not used, see ch8), **ch9 part 2 main gear 54 h** (9/16 to 11/29); part 1 (speed brake, 48 h) is not a graph op |
| GLANTZ-RIG | same blog, rigging and floxing the fuselage | https://www.aryjglantz.com/2013/04/rigging-and-floxing-fuselage.html | one session, "after 6 hours in the garage": dry fit, level, then flox front seat, rear seat, firewall, panel, F22; tapes deferred; no helper named |
| GLANTZ-FLOOR | same blog, glassing and bonding the floor | https://www.aryjglantz.com/2013/06/glassing-and-bonding-floor.html | "after 5 hours of glassing"; bonded next day; edges peel plied; "With Elle's help" positioning the floor |
| GLANTZ-CORNER | same blog, BID tape to bottom corners | https://www.aryjglantz.com/2013/06/applying-bid-tape-to-bottom-corners.html | 2-ply tapes, peel ply over the tape transition |
| GLANTZ-F28 | same blog, F28 and doublers | https://www.aryjglantz.com/2013/06/f28-and-doublers-installation.html | method, peel ply strips; no time |
| GLANTZ-7 | same blog, July 2013 archive (exterior glassing, chapter 7 intro, conduit) | https://www.aryjglantz.com/2013/07/ | exterior glass "13 hours", both sides, girlfriend helping throughout; lower belt hard points done in his ch7; no step fitted; a non-plans conduit |
| GLANTZ-MLG | same blog, main gear attachments (July 2013) | https://www.aryjglantz.com/2013/07/main-landing-gear-attachments.html | brackets done after fuselage assembly; posted in his ch7 date window |
| GLANTZ-8 | same blog, chapter 8 and Rollbar posts | http://www.aryjglantz.com/2013/08/chapter-8-rollover-structure-and-seat.html, https://www.aryjglantz.com/2013/08/ | he built a welded 4130 rollbar, not the plans foam box |
| GLANTZ-9 | same blog, Sep to Nov 2013 archives | https://www.aryjglantz.com/2013/09/, /2013/10/, /2013/11/ | prefab strut, 8 UND stiffening, Bondo jigs, tabs, tubes and washers; no axle, brake or brake-line post by 11/29 |
| PUSH-6 | Long-EZ N916WP log, chapter 6 part 1 | https://www.longezpush.com/?page_id=198 | assembly solo; bottom foam joined with micro, routed and sanded mid-morning to late afternoon; no totals |
| PUSH-7 | same log, final fuselage glassing | https://www.longezpush.com/chapter-7-final-fuselage-glassing/ | both sides in one solo session, about 1930 to 1430 next day (19 h); peel ply on critical areas and seams |
| PUSH-8 | same log, chapter 8 | https://www.longezpush.com/chapter-8-step-6-seatbelts/ | 1/4 birch hard points with 7 BID (matches the plans); no step; steel roll bar and a different headrest; no hours |
| PUSH-9 | same log, chapter 9 main gear | https://www.longezpush.com/chapter-9-main-gear-landing-brake/ | 12 July 2012: "about 2-1/2 hours at the wood shop", cut 4 gear mount jigs with 5/8 holes; other times are fragments |
| MULLINS | Long-EZ kitlog (Nathan Mullins), Main Landing Gear category, per-entry hours | http://www.mykitlog.com/users/category.php?user=jenatepilot&project=2121&category=7801 | 2013-06-08 8.0 h axles, wheels, brakes on a leg set up by a previous builder; 2013-06-10 4.0 h brake lines and fittings; 2013-06-16 0.5 h one-ply glass over the lines |
| BOM | builder BOM by chapter, "BOM master.xlsx" (same file as P1) | https://docs.google.com/spreadsheets/d/0B8ljui4BNLG8Z2NibkF1dEVwM0k/edit | cross-checks (ch6 1.6 in R45 16 sq ft, BID 6 yd; ch7 UND 14 yd; ch8 belt hardware; ch9 strut, AN4-22A x8, AN960-1016 x4). Its notes point to "see blog" and match GLANTZ posts (EZ-Poxy, conduit, ServoCity actuator), so it is probably his, but the sheet does not name an author |
| AS-* | Aircraft Spruce product pages (JSON-LD offer price read) | listed in section 5 | prices |
| AERO | Aero Composites Long-EZ price list | https://aerocomposites.aero/the-hangar-price-lists/ | main gear strut price |

Other sources checked and found to give no usable hours: Cozy DeFord chapter 8
(https://www.deford.com/cozy/chap_08.html), Spodman's Cozy kitlog (it has no CH05 to CH07
categories, and a Cozy MkIV gear is a different design), and searches for any book-method ch8
roll-over box log with times (none found).

## 2. Hours method

Community hours are a builder's own stated time for that step. Everything else is `estimate`.

**Chapter 6 (GLANTZ-T 60 h).** Two pieces are timed: GLANTZ-RIG's 6 h fit-and-flox session and
GLANTZ-FLOOR's 5 h floor glassing (`f06.bottom-glass`, **community**).
- The 6 h session covers seven ops: trial-fit, jig-check, the four bulkhead flox bonds and the
  firewall flox bond (he bonded the firewall in ch6, not after the spar as CP25 suggests). It is
  split evenly, 6/7 = **0.86** each.
- The remaining 60 − 6 − 5 = 49 h is split over six shares, 8.17 h each: bulkhead taping (one
  session per GLANTZ, split three ways over the front-seat tapes, the panel tapes and
  `f06.rear-seat-tape`, 2.72 h each), `f28-install`, `bottom-foam-fit`, `bottom-contour`,
  `bottom-bond` and `bottom-tape`.
- Values: trial-fit 0.9, jig-check 0.9, bond-front-seat 0.86 + 2.72 = 3.6, bond-panel 3.6,
  bond-f22 0.9, bond-rear-seat 0.9, rear-seat-tape 2.7, f28-install 8.2, bottom-foam-fit 8.2,
  bottom-contour 8.2, bottom-glass 5.0 (community), bottom-bond 8.2, bottom-tape 8.2,
  bond-firewall 0.9. The sum is 60.4 because of rounding.
- Known inflation inside the 49 h, size unknown: a 2-week fix of a side sitting about 1 in aft
  (GLANTZ May post). The gear brackets may also be in his ch6 hours or in his ch7 hours (he calls
  them ch6 work, but the post falls in his ch7 dates). P1 gave `f05.gear-extrusions` no hours.
  This 8.2 h even split is the weakest number in the file.

**Chapter 7 (GLANTZ-T 39 h).** The exterior glass took 13 h for both sides, with a helper
(GLANTZ-7). That gives `skin-right` and `skin-left` **6.5** h each. These are estimates, because the
graph cures the right side before the left, and he did both in one session. For comparison, PUSH-7
did both sides alone in about 19 h (9.5 per side) and says he would pre-cut or stop halfway next
time. The other 26 h is split over six shares of **4.33**: carve-corners, canard-cutout,
fuel-gauge-area, belt-insert, his belt hard points (graph op `f08.belt-attach`, so the share goes
there) and his non-plans conduit (dropped).

**Chapter 8.** There are no hours for the six roll-over and harness ops or for the step. The
GLANTZ 17 h is a welded steel rollbar, and PUSH built a steel bar and a different headrest. Both
skipped the step. `f08.belt-attach` = **4.3** (the GLANTZ ch7 share above).

**Chapter 9 (GLANTZ-T main gear 54 h).** His posts by 11/29 cover the stiffening, jigs,
positioning, tabs and tubes. They have nothing on axles, brakes or brake lines, so the 54 h is
spread over five ops. `f09.jig-blocks` = **2.5 community** (PUSH-9). The rest is (54 − 2.5)/4 =
**12.9** each for strut-stiffen, position-gear, tab-layup and tab-assembly. Subtracting one
builder's time from another's total is my choice; an even 54/5 = 10.8 split is the alternative.
- `f09.axles-brakes` = **8.0**, from the MULLINS 2013-06-08 entry: axles, wheels and brakes on a
  leg a previous builder had set up. It excludes the toe-in setting and the 3-ply BID, so it reads
  low. Mullins logged a further 8 h toe-in session in 2014, but that was rework.
- `f09.brake-lines` = **4.5**: MULLINS 4.0 h (lines and fittings) + 0.5 h (one-ply glass over the
  lines). His line is braided Teflon in a conduit, not the plans' nylon line, so the method differs.
  His 6 h entry mixes in a relief tube and a wiring conduit, so it is excluded.

Buddy steps: 2, `f07.skin-right` and `f07.skin-left` (people_why: one mixes, one wets out). This is
the same pattern P1 used for `f05.inside-layup`: GLANTZ had a helper "throughout", and these are the
largest wet layups so far. PUSH-7 did both alone in a 19 h push, so the rehearsal can drop either
op to 1. GLANTZ also had help positioning the floor and with tab prepregs, and PUSH had a friend cut
tab glass. I treat those as convenience, not as a second person the step needs.

## 3. Resin

As in P1: `mgs-285-287` (`data/resins/mgs-285-287.yaml`) is on every op whose cure is not none.
Glass work, flox bonds and micro fills are `part`. No op is `all`. `f06.bond-firewall` holds the
assembly for 12 h per the summary; that is still `part` (the group, not the shop).
`f09.position-gear` is `none`, because its Bondo is not the MGS system and sets in minutes.

**One gap to note:** GLANTZ-7 used EZ-Poxy on the exterior skins because the aft side skin is part
of the fuel tank, and he says his Aeropoxy is not fuel resistant. I did not check MGS L285 for fuel
resistance. The integrator should look before `f07.skin-*` and the strake chapters rely on it.

## 4. Per-op findings

Constants (P1): 38 in roll = 1368 in² per yd. UND 0.2095 kg/yd, BID 0.2633 kg/yd. A 1.1
overlap/trim factor. Resin = cloth by weight, split 100:40, LR285 4.561 kg/gal, H287 0.894 kg/qt.
Peel ply in packs of 10800 in², only where a community log shows it. Areas marked "ply model" are
`core/fuselage_plies.py` values; several are flagged lower bound there. Micro, flox, Bondo and RTV
are never quantified (no dimensions).

| op | people | cure | hours | buys (arithmetic) | unsourced / notes |
|---|---|---|---|---|---|
| f06.trial-fit | 1 | none | 0.9 est | none | GLANTZ made three threaded-rod clamps (BOM "custom clamps"); hardware not priced |
| f06.jig-check | 1 | none | 0.9 est | none | jig blocks are shop lumber |
| f06.bond-front-seat | 1 | part | 3.6 est | none quantified | BID tape width not in the repo (ply model EXCLUDED: no width); flox qty unsourced |
| f06.bond-panel | 1 | part | 3.6 est | none quantified | same tape-width gap |
| f06.bond-f22 | 1 | part | 0.9 est | none | flox only; tape only where the page shows it (not dimensioned) |
| f06.bond-rear-seat | 1 | part | 0.9 est | none | flox only |
| f06.f28-install | 1 | part | 8.2 est | spruce 2 doublers × 3 in / 12 = **0.5 ft** (`spruce-capstrip-075x1`, 3/4×1 stock for a 1.0×0.7×3 doubler, size from the ply model note) | BID over each doubler: only the 0.4 in lap is stated, so it is not quantified. BOM: doublers from longeron offcuts |
| f06.rear-seat-tape | 1 | part | 2.7 est | none quantified | no tape width |
| f06.bottom-foam-fit | 1 | none | 8.2 est | 1.6 in foam, bottom upper face 2051.0 in² (ply model, representational) / 144 = **14.24 sq ft** (NEW `foam-pvc-1p6`) | BOM 16 sq ft of 1.6 in R45; PUSH used two 1-3/4 Divinycell panels micro'd together (micro unsourced) |
| f06.bottom-contour | 1 | none | 8.2 est | none | PUSH routed and sanded most of a day |
| f06.bottom-glass | 1 | part | **5.0 community** (GLANTZ-FLOOR) | BID 2 × 2051.0 × 1.1 / 1368 = **3.30 yd** → 0.868 kg → 0.136 gal / 0.278 qt | the extra ply under the rear-seat entry is undimensioned (excluded), and the 1 in overlaps and 2 in aft excess are not counted, so this reads low. GLANTZ peel plied the edges only, area unknown, so no peel ply buy |
| f06.bottom-bond | 1 | part | 8.2 est | none | flox; weights are shop items |
| f06.bottom-tape | 1 | part | 8.2 est | BID 382.2 in² (ply model: 191.1 in of side corners × 2 in) × 1.1 / 1368 = **0.31 yd** → 0.013 gal / 0.026 qt; peel ply 382.2 × 1.1 / 10800 = **0.039 pack** (GLANTZ-CORNER) | bulkhead-to-bottom corners not counted (lower bound). If F22, panel ×2, front seat ×2 at 23 in and rear seat at 20.6 in are added, that is about 135.6 in more, roughly +0.22 yd. Not added, because those corner widths are partly unsourced |
| f06.bond-firewall | 1 | part | 0.9 est | none quantified | lap width of the edge BID ply not stated |
| f07.carve-corners | 1 | none | 4.3 est | none | |
| f07.canard-cutout | 1 | none | 4.3 est | none | outline from the A sheet (CP27 LPC50), not held |
| f07.fuel-gauge-area | 1 | part | 4.3 est | none | micro unsourced; grey tape is a ch5 leftover |
| f07.belt-insert | 1 | part | 4.3 est | none | insert about 5 in long (config FS 49.7 to 54.7, fitted); section and wood type unsourced |
| f07.skin-right | **2** | part | 6.5 est | UND (ply model) 2 × (1993.2 side + 1110.8 bottom half) + 1033.3 third ply + 3 × 150.1 strip = 7691.6 in² × 1.1 / 1368 = **6.18 yd** → 1.296 kg → 0.203 gal / 0.414 qt | wrap over the top longeron, the 0.5 in firewall lap and the skin aft of the rear seat are not counted (lower bound). Both sides total 12.4 yd, against the BOM's 14 yd bought. PUSH peel plied seams, area unknown, so no peel ply buy |
| f07.skin-left | **2** | part | 6.5 est | same as the right: **6.18 yd**, 0.203 gal / 0.414 qt | peel ply on the strake bond areas, spar cutout, firewall and F22: areas undimensioned, so not quantified |
| f08.roll-over-foam | 1 | none | **none** | 0.35 in foam, inside-face area 259.9 in² (ply model, derived) / 144 = **1.80 sq ft** (NEW `foam-pvc-0p35`) | foam type not in the repo; edge chamfers ignored |
| f08.roll-over-inside | 1 | part | **none** | BID 259.9 × 1.1 / 1368 = **0.21 yd** → 0.009 gal / 0.018 qt; plywood 3 × 1.25 × 1.25 = 4.69 in² / 2304 = **0.002 sheet** | 6 mm stock against a 0.25 in insert |
| f08.roll-over-bond | 1 | part | **none** | none | micro unsourced |
| f08.roll-over-outside | 1 | part | **none** | BID 2 × 214.8 × 1.1 / 1368 = **0.35 yd** → 0.014 gal / 0.029 qt | 12-ply buildups over 3 inserts, 3 peak plies and 2 local plies are all undimensioned (ply model EXCLUDED), so this reads well low |
| f08.access-holes | 1 | none | **none** | none | map slot 1.8 × 8, baggage hole 3.75 (config) |
| f08.shoulder-harness | 1 | part | **none** | none | pad outline undimensioned; bolt count not derivable; the harness itself (BOM lists 2 belt/harness sets for ch8) not put in buy |
| f08.belt-attach | 1 | part | 4.3 est | BID 7 × 48.0 (ply model, 4 pads with 1 in margin) × 1.1 / 1368 = **0.27 yd** → 0.011 gal / 0.023 qt; 4 places × 1 hole → **4** AN525-416R16, **4** MS21042-4, **4** AN960-416 (`derived`); aluminium angle **0.67 ft** (BOM 8 in / 12, estimate) | insert size fitted, so plywood not quantified (BOM: firewall offcuts). BOM lists 8 screws (one builder, no step); the step text says one hole per place, so I used 4 |
| f08.step | 1 | none | **none** | none | step 1.8 × 4.5 × 4.5, 0.125 thick, 4 countersunk 1/4 holes (config); alloy and screw type not stated. GLANTZ and PUSH both skipped it |
| f09.strut-stiffen | 1 | part | 12.9 est | strut **1** (NEW `main-gear-strut`, `derived`) | 8 UND plies: the strut surface is not printed (fitted outline), so not quantified. PUSH cut 16 strips 9 in wide, length not given |
| f09.jig-blocks | 1 | none | **2.5 community** (PUSH-9) | plywood 4 × 3.464 in² (model block solid, volume/thickness) / 2304 = **0.006 sheet** | the gear tubes are the ch5 LMGA |
| f09.position-gear | 1 | none | 12.9 est | none | Bondo qty unsourced (catalog item below, not in buy); datum board is shop lumber |
| f09.tab-layup | 1 | part | 12.9 est | UND 18 × 4 tabs × (2.5 × 12) = 2160 in² × 1.1 / 1368 = **1.74 yd**; BID 18 × 4 × (2.5×3.5 + 2.5×2.5) = 1080 in² → **0.87 yd**; 0.593 kg → 0.093 gal / 0.189 qt | printed pad sizes from the graph row. PUSH and GLANTZ both used prepreg between plastic |
| f09.tab-assembly | 1 | part | 12.9 est | AN960-1016 **6** (`derived`: 2 called out + 4 more per CP30 LPC83, the graph's change note) | the BOM says 4 total, which conflicts with the CP note's "four more". Corner pads, tube wrap over a foam block, plugs and flox: undimensioned |
| f09.axles-brakes | 1 | part | 8.0 est | AN4-22A **8** (4 per axle × 2; BOM also 8), MS21042-4 **8** (one per bolt; BOM 8), axle **2**, wheel and brake **2** (one per side) | 3 BID plies each face at the axle: pad size not in the repo (PUSH used 3 × 3 in). Axle plates (BOM: 0.063 2024-T3, 2.5 × 2.5) and AN960-416 washers (BOM 16) not derivable from the summary |
| f09.brake-lines | 1 | part | 4.5 est | nylon line 2 × 72 in / 12 = **12 ft** (`derived` from "about 72 in each side"); BID tape 2 × 72 × 2 in (the two 1 in laps) × 1.1 / 1368 = **0.23 yd** → 0.010 gal / 0.020 qt | line width under the tape not counted (lower bound); RTV unsourced; fittings depend on the brake choice |

## 5. New catalog items (not in `data/catalog/prices.yaml`)

Read 2026-10-18. Flags use the Contract 3 vocabulary. Prices are the Aircraft Spruce page's
single-unit offer price unless noted.

| id | label | vendor | part | URL | price | unit | flag |
|---|---|---|---|---|---|---|---|
| foam-pvc-1p6 | PVC foam, 1.6 in (BOM: R45) | none at 1.6 in | | https://www.aircraftspruce.com/catalog/cmpages/divinycellfoam.php | null | sqft | unsourced. The nearest is H45 1-3/4 in, 32×48, 01-12900, $187.75 (page); PUSH used 1-3/4. Whether 1-3/4 is acceptable is a builder call |
| foam-pvc-0p35 | PVC foam, about 0.35 in (repo `rollover_foam_thickness`) | none at 0.35 in | | same page | null | sqft | unsourced. Nearest: H45 3/8 in, 32×48, 01-12400, $53.75 (page); the plans foam type is not in the repo |
| an525-416r16 | AN525-416R16 washer-head screw (BOM belt brackets) | Aircraft Spruce | AN525-416R16 | https://www.aircraftspruce.com/catalog/pnpages/AN525-416R16.php | 1.34 | each | page |
| ms21042-4 | MS21042-4 stop nut | Aircraft Spruce | MS21042-4 | https://www.aircraftspruce.com/catalog/pnpages/MS21042-4.php | 0.56 | each | page |
| an960-416 | AN960-416 flat washer | Aircraft Spruce | AN960-416 | https://www.aircraftspruce.com/catalog/pnpages/AN960-416.php | 0.12 | each | page |
| an960-1016 | AN960-1016 flat washer (CP30 LPC83) | Aircraft Spruce | AN960-1016 | https://www.aircraftspruce.com/catalog/pnpages/AN960-1016.php | 0.40 | each | page |
| an4-22a | AN4-22A bolt, undrilled (axle bolts) | Aircraft Spruce | AN4-22A | https://www.aircraftspruce.com/catalog/pnpages/AN4-22A.php | 1.20 | each | page (pack of 5 is $5.70) |
| alu-angle-2024-1x1x0125 | 2024-T3 angle 1 × 1 × 1/8 (BOM belt brackets) | | | | null | ft | unsourced |
| main-gear-strut | Long-EZ main gear strut, prefabricated (BOM: MG1-L, Feather Lite) | Aero Composites | none listed | https://aerocomposites.aero/the-hangar-price-lists/ | 1120.00 | each | page. The listing names no part number, so it is not confirmed to be the MG1-L. The BOM's $558 Feather Lite price is from about 2013 |
| main-axle | main gear axle (BOM: Grove 1-1/4 with pant stub) | | | | null | each | unsourced |
| wheel-brake-5in | 5 in wheel and brake assembly (BOM: Grove 57-224) | | | | null | each | unsourced |
| brake-line-nylon-316 | Nylaflow 3/16 OD × .138 ID nylon tube | Aircraft Spruce | 05-00110 | https://www.aircraftspruce.com/catalog/pnpages/05-00110.php | 0.75 | ft | page. Size match to the plans line not verified |
| bondo-body-filler | body filler for the gear-position fix (qty unsourced, so not in buy) | | | | null | each | unsourced |
| rtv-sealant | RTV for potting the brake line through the firewall (qty unsourced, so not in buy) | | | | null | each | unsourced |

Existing ids reused: `bid-7725`, `und-7715`, `mgs-lr285-gal`, `mgs-h287s-qt`, `peel-ply-582c`,
`birch-ply-6mm-48x48`, `spruce-capstrip-075x1`. Micro and flox (`micro-bubbles-1lb`,
`flox-cotton-1lb`) are used on many of these ops, but no op has a dimension to size them.

## 6. Open gaps (what would clear them)

- **Per-step hours.** Only 2 of 35 are a builder's time for that exact step. The owner's actuals
  (Contract 20a) are the real fix.
- **Ch8 roll-over hours.** None of the logs found build the plans foam box. A builder who built it
  to plans and logged time would clear six ops.
- **Tape widths and pad outlines.** Needed for the ch6 bulkhead tapes, the F28 doubler ply, the
  firewall lap, the ch8 buildups and harness pads, the ch9 corner pads, the axle pads and the strut
  UND. They are on pages and full-size sheets not held, or come from Contract 18 geometry.
- **Fuel resistance of MGS L285** for the tank-wall skin (section 3).
- **Hardware counts not derivable from the summaries:** harness bolts, step screws, axle washers,
  axle plates, plugs.

## p2-ch11-14-sourcing.md

# Rehearsal sourcing, P2 (chapters 11 to 14, 37 ops)

Research only. Read 2026-10-18. No repo file was changed. The values file is `p2-ch11-14-plan-values.yaml`
in this directory. This record holds the evidence, the arithmetic and the gaps for it. Method and
conventions follow `rehearsal-sourcing-p1.md` (the P1 record).

Plans text: not read (the scan is private). Step content comes from the repo summaries in
`guide/graph/ch13.yaml` and `ch14.yaml`. Dimensions come from `config/aircraft_config.py` (book-cited) or
from the repo's representational/fitted models (`core/nose_book.py`, `core/spar_book.py`,
`core/landing_gear_book.py`), measured by running the model code read-only.

## 0. Scope

| chapter | graph | ops taken | skipped |
|---|---|---|---|
| 11 | no `ch11.yaml`; only stub `c11.elevators` in `stubs.yaml`, variants [gu] | 0 | stub, [gu] |
| 12 | `ch12.yaml`: `c12.alignment-pins`, `c12.align-canard`, both [gu] | 0 | both [gu] (Roncz installs per ch30) |
| 13 | `ch13.yaml`, all [both] | 20 | none |
| 14 | `ch14.yaml`, all [both] | 17 | none |

## 1. Sources used

| key | what | URL | used for |
|---|---|---|---|
| GLANTZ-T | Long-EZ build blog, time and budget page | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | **ch13 143 h** (1/3 to 12/9/2014; page says "a lot of mods"), **ch14 121 h** (1/3 to 4/12/2015). ch11 and ch12 "still to come", no hours |
| GLANTZ-TSW | same blog, troughs and shear web | https://www.aryjglantz.com/2015/02/troughs-and-shear-web.html | troughs plus shear web took "more than 15" h; shear web used "about a quart or more" of resin; six 19 in BID strips at 45 deg for 3 plies |
| GLANTZ-INT | same blog, spar interior layup | https://www.aryjglantz.com/2015/01/spar-interior-layup.html | "more than half a quart" of epoxy; about 3 h for the first ply; LWA bar sold as T4 |
| GLANTZ-LID | same blog, spar lid CS4 | https://www.aryjglantz.com/2015/01/spar-lid-cs4.html | 3-day cure wait before removing from the jig |
| GLANTZ-OUT | same blog, spar outside layup | https://www.aryjglantz.com/2015/03/spar-outside-layup.html | layup 6 done by two: one brushes, one squeegees (his wife helped); he used the CP25 UND option |
| GLANTZ-BSC | same blog, bottom spar cap | https://www.aryjglantz.com/2015/03/bottom-spar-cap.html | helper held a card while he pulled cross threads (convenience, see section 4) |
| GLANTZ-SC | same blog, strut cover and wheel well | https://www.aryjglantz.com/2014/11/strut-cover-and-wheel-well-installation.html | a friend helped install and sand the strut cover |
| GLANTZ-SCM | same blog, making the strut cover | https://www.aryjglantz.com/2014/07/making-of-strut-cover.html | he made the SC instead of buying it; helper hot-glued foam |
| GLANTZ-13 | same blog, ch13 posts Jan to Dec 2014 | https://www.aryjglantz.com/2014/01/chapter-13-nose-and-nose-gear.html and the monthly archive | extended round nose and electric actuator mods; no step hours |
| SPOD13 | Cozy MKIV log (mykitlog, Spodman), CH13 Nose, per-entry hours | http://www.mykitlog.com/users/category.php?user=Spodman&project=2369&category=10332 | 144 entries, 260.5 h; per-step weights (section 2) |
| SPOD14 | same log, CH14 Center Spar, per-entry hours and detail pages | http://www.mykitlog.com/users/category.php?user=Spodman&project=2369&category=10333 | 53 entries, 117.2 h; per-step weights; resin used: layup 6 (4 UND) 2.1 kg, layup 8 (2 UND) 0.6 kg |
| PUSH-14 | Long-EZ N916WP log, mounting spar to fuselage | https://www.longezpush.com/?p=14522 | alignment "about 30 minutes"; 45+ min cutting tapes; done alone; wings already on the spar (different order), so not used for hours |
| AERO | Aero Composites price list (page dated 2025-01-12) | https://aerocomposites.aero/?p=1167 | Long-EZ nose gear strut $170, Strut Cover SC $50, Nose Wheel Cover NB $50 |
| AS-* | Aircraft Spruce product pages | section 5 | prices |

Logs checked with no usable hours: https://www.longezpush.com/?p=5498 (NG30 plates, H250, no time),
https://www.deford.com/cozy/chap_14.html (Cozy, no hours). No VariEze log with ch13/14 hours was found.

## 2. Hours method (every hours value is `estimate`)

Same as P1: no public log times these exact steps, so GLANTZ-T's chapter totals are split per op using a
Cozy MKIV log's per-entry hours as weights. The Cozy parts differ, so the weights are a proxy. Shared
entries are split evenly between the ops they name. Each op's hours = (its SPOD hours / mapped SPOD
total) x Glantz chapter total, rounded to 0.1 h.

**Chapter 14, 121 h, SPOD14 mapped total 117.2 h (all 53 entries used).** The Cozy spar sequence
matches the Long-EZ one closely (jig, foam, internal layup, lid, troughs, shear web, caps, outer
layups, access holes, install).

| op | SPOD14 entries (h) | SPOD h | est h |
|---|---|---|---|
| f14.jig | jig 4.1 + 3.3 + 1.9 + 3.8 | 13.10 | 13.5 |
| f14.foam-box | foam 1.0 + 1.5 + 2.4 + 1.9; 1/3 of "parts" 2.0 | 7.47 | 7.7 |
| f14.cs4-forward | 1/2 of 9-9 4.1; 1/2 of 9-10 2.2 | 3.15 | 3.3 |
| f14.lwa-fabricate | 1/3 of "parts" 2.0; 1/2 of 8-30 1.0 (sanding, alodine) | 1.17 | 1.2 |
| f14.interior-layups | 1/3 "parts"; 1/3 of 8-25 0.8; glass cutting 1.0 + 1.0; 1/2 of 8-30; layup 6.5 + 0.1; 1/2 of 9-9; 1/2 of 9-10 | 13.18 | 13.6 |
| f14.close-box | 0.2 + jig removal 1.0 | 1.20 | 1.2 |
| f14.cap-troughs | 1/3 of 8-25 (cap templates); 2.0 + 0.1 + 3.0 + 6.0 | 11.37 | 11.7 |
| f14.shearweb-lwa45 | 5.5 + 0.5 + 3.3 | 9.30 | 9.6 |
| f14.spar-caps | upper 2.0 + 0.3 + 0.7 + 6.3 + 1.2; bottom 1.3 + 0.3 + 4.5; trim/radius 2.8 + 2.4 | 21.80 | 22.5 |
| f14.spruce-layup6 | layup 8.5; 1/2 of 11-11 1.1; 1/2 of 11-16 3.3 (LWA2/3 flox) | 10.70 | 11.0 |
| f14.lwa23-layup7 | 1/2 of 11-16 3.3 | 1.65 | 1.7 |
| f14.baggage-hole | 1/2 of 11-11; 1.0; 5.6 (edges + 2 UND forward face) | 7.15 | 7.4 |
| f14.end-bulkhead-layup9 | 1/2 of 11-17 1.0 | 0.50 | 0.5 |
| f14.nut-access-hole | 1/2 of 11-17; 1.0 (2.25 in hole saw, dry micro) | 1.50 | 1.5 |
| f14.fit-fuselage | 1.3 + 3.0 + 1.4 | 5.70 | 5.9 |
| f14.bond-spar | 1.9 + 1.0 + 2.0 + 1.5 + 0.6; EM hard points 0.5 + 0.5 | 8.00 | 8.3 |
| f14.sh1-tabs | 1/3 of 8-25 (Cozy harness blocks, weak analog) | 0.27 | 0.3 |
| total | | 117.2 | 120.9 |

Cross-check: GLANTZ-TSW says troughs plus shear web took more than 15 h; the split gives 21.3 h. That fits.

**Chapter 13, 143 h, SPOD13 mapped total 154.15 of 260.5 h.** Excluded as Cozy-only or rework:
ballast compartment and nose-weight storage (all), spar weight tubes, elevator root fairings, canard
brace, the Cozy nose gear doors, 2023 strut and door fettling, the nose wheel tube, and half of 11-20
(ballast). Pools: "fitting nose gear" halves (G = 14.4 h) are split three ways over ng3-ng4,
lower-gear and rig-nose-gear; "pedals" halves (P = 13.3 h) are split evenly over pivot blocks and
pedals. **Weakness:** Glantz's 143 h includes his mods (extended round nose, electric actuator), so it
likely reads high for a plans nose.

| op | SPOD13 entries (h) | SPOD h | est h |
|---|---|---|---|
| f13.strut-reinforce | prep 1.0; 1/2 of strut-wrap/NG-30 entries (9.3 + 0.8 ... 1.7 = 10.1) | 6.05 | 5.6 |
| f13.worm-drive-bench | none (no entry; builders often buy the drive) | none | **none** |
| f13.ng30-plates | doublers 0.3 + 1.0 + 0.5; the other half of the wrap entries; outer layup 2.2; trim/drill 1.6; pivot mount 1.8 | 12.45 | 11.5 |
| f13.ng-box-assemble | trial assembly 2.0; hardware 1.3; NG-5 1.5; strut 3.6; NG-30 assembly 3.3 | 11.70 | 10.9 |
| f13.ng3-ng4 | G/3 | 4.80 | 4.5 |
| f13.ng31-f6 | fitting NG-30 assembly to nose 6.0 | 6.00 | 5.6 |
| f13.floor-blocks | floor 2.4 + 3.0 + 2.9; 1/2 of floor-and-sides 1.0 | 8.80 | 8.2 |
| f13.pedal-pivot-blocks | P/2 | 6.65 | 6.2 |
| f13.side-pieces | 1/2 of 1.0; 1.7 + 1.3 + 3.0 + 5.5; 1/2 of 3.8 | 13.90 | 12.9 |
| f13.canard-attach-reinforce | canard mounts 1.7; 1/2 of mounts-and-pedals 2.7 + 2.7 + 1.4 | 5.10 | 4.7 |
| f13.rudder-pedals | P/2; 2019 pedals/hardware 5.4 | 12.05 | 11.2 |
| f13.lower-gear | G/3 | 4.80 | 4.5 |
| f13.strut-slot-sc | SC fit 2.0; outer strut cover 2.1; 1/2 of 2.0 and 0.9 | 5.55 | 5.1 |
| f13.nb-box | wheel cover 0.5; windows 0.5 + 1.2 + 0.7 + 1.0 | 3.90 | 3.6 |
| f13.rig-nose-gear | G/3; final installation 1.9 | 6.70 | 6.2 |
| f13.pitot-static | static 0.5 + 0.8; 1/2 of ballast-and-pitot 1.0 | 1.80 | 1.7 |
| f13.top-foam | 1/2 of top foam 5.6 | 2.80 | 2.6 |
| f13.carve-glass-nose | 1/2 of top foam; nose cone, shaping, lower and upper skins, bumper (19 entries) | 31.90 | 29.6 |
| f13.nose-door | door 0.3 + 1.7 + 1.2 + 1.6; reattach top 1.3; 1/2 of door/cover 4.0; 1/2 of 2.2 | 9.20 | 8.5 |
| f13.shock-strut | none (optional; no log times it) | none | **none** |
| total | | 154.15 | 143.1 |

## 3. Resin

Unchanged from P1: `mgs-285-287` (min 10 C, `mgs-l285-tds:p1`; no work-again curve). Community
cure notes for this stretch: GLANTZ-LID waited 3 days before pulling the closed box (the repo summary
says 2 to 3 days); most nose layups were trimmed after an overnight cure.

## 4. Per-op findings

Constants (P1): 1368 in2 per linear yd; BID 0.2633 and UND 0.2095 kg/yd; x1.1 overlap/trim (my
assumption); resin = cloth by weight; split 100:40; LR285 4.561 kg/gal, H287 0.894 kg/qt. Peel ply in
5 yd x 60 in packs (10800 in2). Micro and flox are never quantified (P1 rule). Resin for slurry and
flox is not counted, so every resin figure reads low.

Model areas (representational, run read-only from the repo): spar box faces: aft 873.8, forward 887.2,
top 727.8, bottom 728.2, ends 88.2 in2 (built from book stations, p88/p90). Nose: NG30 face 210.8 per
plate, NG31 disc 69.5, F6 21.5 (3.4 x 6.3), SC 50.1, door 85.4 (8.6 x 9.4), skin shell 2804.7 total,
taken as 1402.4 outside (half). NG-1L fitted box 20.3 x 1.0 x 1.8.

Resin checks against community figures: interior layups compute to 0.70 kg mixed (about 0.65 qt);
GLANTZ-INT says more than half a quart, consistent. Shear web computes to 0.56 kg (about 0.52 qt);
GLANTZ-TSW says a quart or more, so this op reads about half low. Layup 6 computes to 1.48 kg; SPOD14's
Cozy spar used 2.1 kg for its 4-UND version (a bigger spar).

| op | people | cure | hours | buys (arithmetic) | unsourced / notes |
|---|---|---|---|---|---|
| f13.strut-reinforce | 1 | part | 5.6 est | strut 1 (`derived`: one NG-1L); BID 2(1.0+1.8) x 20.3 = 113.7 in2 x 1.1 → 0.09 yd → 0.004 gal / 0.008 qt | strut section is fitted, not book; wrap overlap inside x1.1 |
| f13.worm-drive-bench | 1 | none | **none** | none | build-or-buy; no vendor found for the plans worm drive; NG3/NG4/NG8/NG6 parts unsourced; NG17 per CP30 LPC 87 |
| f13.ng30-plates | 1 | part | 11.5 est | PVC 0.2 2 x 210.8 / 144 = 2.93 sq ft; BID 8 x 2 x 210.8 x 1.1 → 2.71 yd → 0.112 gal / 0.228 qt | plate outline fitted (A6/A7 not held); 15-ply pads have no size, excluded. PUSH used H250 |
| f13.ng-box-assemble | 1 | part (flox) | 10.9 est | none quantified | NG14 spacers, NG51 plates, bolts: counts unsourced |
| f13.ng3-ng4 | 1 | part | 4.5 est | none | 2-3 dry BID plies, no size |
| f13.ng31-f6 | 1 | part | 5.6 est | R100 1/4 blank 8.4 x 8.4 / (42.1 x 42.5) = 0.039 sheet; BID (69.5 + 2 x 5.4 x 6.3) x 1.1 → 0.11 yd → 0.005 gal / 0.009 qt | NG31 size is a model fit (cobelu figure); F22 tapes no size; R100 per CP25 LPC 23, H100 assumed equivalent |
| f13.floor-blocks | 1 | part | 8.2 est | urethane 2 x 20.9 x (8.2+1.6)/2 = 204.8 / 1152 = 0.178 sheet; BID 2 x 2 x 102.4 + 2 x 3 x 8.2 = 458.8 x 1.1 → 0.37 yd → 0.015 gal / 0.031 qt | which end is 8.2 is a reading; extra aft ply assumes the 8.2 end is aft |
| f13.pedal-pivot-blocks | 1 | part | 6.2 est | none quantified | nutplate count, 0.063 plate size, foam block size unsourced |
| f13.side-pieces | 1 | part (micro) | 12.9 est | urethane 2 x 21.9 x (15.6+8.3)/2 = 523.4 / 1152 = 0.454 sheet; BID 2 x 2 x 261.7 x 1.1 → 0.84 yd → 0.035 gal / 0.071 qt | 4-ply covers over pivot blocks: no size, excluded |
| f13.canard-attach-reinforce | 1 | part | 4.7 est | none quantified | corner ply size; CNL bushing and AN970 counts unsourced |
| f13.rudder-pedals | 1 | none | 11.2 est | pedals 2 (`derived`: left and right) | weldment source and price unsourced; CS13 spacers, spring unsourced; CP30 LPC 86 tab reinforcement |
| f13.lower-gear | 1 | part (flox) | 4.5 est | none | NG15A not bought here (AS lists a "nosegear mounting plate" 01-00838, MFR NG15-A1, $8.40; identity with NG15A not confirmed); door screws spec unsourced |
| f13.strut-slot-sc | 1 (GLANTZ-SC had a friend help; convenience) | part | 5.1 est | SC 1 (`derived`); BID 2 x 50.1 x 1.1 → 0.08 yd → 0.003 gal / 0.007 qt | the fuselage is flipped for this step; GLANTZ made his own SC |
| f13.nb-box | 1 | part | 3.6 est | NB 1 (`derived`) | Aero lists "Nose Wheel Cover NB"; taken as the NB box by name only. BID tape and plexiglass sizes unsourced |
| f13.rig-nose-gear | 1 | none | 6.2 est | none | |
| f13.pitot-static | 1 | part (potting) | 1.7 est | 5052 tube (6 + 38) in / 72 in = 0.61 length (`estimate`, was `official`; downgraded 2026-10-20 because the page was not read: lengths in the completion text, `plans-1980:p82` through the graph; page not read) | wall thickness not in the repo; .035 assumed |
| f13.top-foam | 1 | part (dabs) | 2.6 est | urethane 19.3 x (19.6+7.0)/2 = 256.7 / 1152 = 0.223 sheet | adhesive for the dabs not stated; AS urethane colour not checked against "green" |
| f13.carve-glass-nose | 1 | part | 29.6 est | BID 2 x 1402.4 x 1.1 → 2.26 yd → 0.093 gal / 0.190 qt | skin area is half of a fitted shell; 3-ply cutout and 4-ply bumper excluded; flox corners not counted |
| f13.nose-door | 1 | part | 8.5 est | BID (4 + 1) x 85.4 + 36 edge strip = 463 x 1.1 → 0.37 yd → 0.015 gal / 0.031 qt; screws 10 and nutplates 10 (`estimate`, was `official`; downgraded 2026-10-20, plans text not read: `plans-1980:p83` through the graph) | door outline fitted; release film not quantified; screw/nutplate spec unsourced |
| f13.shock-strut | 1 | none | **none** | none | optional (CP25 LPC 27); spring assembly unsourced |
| f14.jig | 1 | none (Bondo sets fast, not epoxy) | 13.5 est | particle board 112.92 x 12.5 / (48 x 96) = 0.31 sheet | the upright is longer than a 96 in sheet; shelf/support sizes and Bondo qty unsourced |
| f14.foam-box | 1 | part (micro) | 7.7 est | PVC (873.8 aft face + 2 x 6.30 x 6.83) / 1536 = 0.62 sheet | CS5/CS8 are 1/4 PVC (p90, per the repo); CS1 thickness not in the repo, assumed 1/4; CS2/CS3 urethane core sizes unsourced |
| f14.cs4-forward | 1 | part | 3.3 est | PVC 887.2 / 1536 = 0.58 sheet; BID 887.2 x 1.1 → 0.71 yd → 0.029 gal / 0.060 qt; peel ply 1 in x 241 in / 10800 = 0.022 pack | CS4 thickness assumed 1/4 |
| f14.lwa-fabricate | 1 | none | 1.2 est | 2024 1/8 x 2: (6 x 1.5 + 4 x 2.5 + 4 x 6.4) = 44.6 in = 3.72 ft; 1/4 x 2: (8 x 1.75 + 2 x 2.25) = 18.5 in = 1.54 ft (`derived`: `config.spar_lwa_sizes`, `plans-1980:p90`, `cp-text:p43`) | counts follow the op text, which includes ch19 wing-side blanks (ch14 installs 6/2/2/4/2). AS stock is T4 unless T3 requested |
| f14.interior-layups | 1 | part | 13.6 est | BID (873.8 + 727.8 + 728.2 + 88.2 inner faces + 149.2 CS6/CS7 two faces + 6 x 4 x 3.5 LWA1 covers + 265.5 end laps at 5 in) = 2916.8 x 1.1 → 2.35 yd; UND 504 x 1.1 → 0.41 yd → 0.110 gal / 0.225 qt | outer-face areas stand in for inner faces; LWA1 lap 1 in assumed |
| f14.close-box | 1 | part (micro) | 1.2 est | none | 3-day wait (GLANTZ-LID) |
| f14.cap-troughs | 1 | none | 11.7 est | none | A11 templates not held |
| f14.shearweb-lwa45 | 1 | part | 9.6 est | BID 3 x 873.8 x 1.1 → 2.11 yd → 0.087 gal / 0.177 qt; peel ply 0.089 pack | reads low on resin vs GLANTZ-TSW; LWA4/5 bought in lwa-fabricate; UND option (CP25 LPC 26) not costed |
| f14.spar-caps | 1 (GLANTZ-BSC: helper held a card; convenience) | part | 22.5 est | UND (972 top + 705 bottom) in x 3 in = 5031 x 1.1 → 4.05 yd → 0.133 gal / 0.271 qt | strip lengths are book (p86, via config); cut from the 38 in roll |
| f14.spruce-layup6 | **2**: one brushes, one squeegees (GLANTZ-OUT) | part | 11.0 est | spruce 4 x 3 in = 1.0 ft (`derived`, p86); BID 3 x 2329.8 x 1.1 → 5.62 yd → 0.232 gal / 0.473 qt | LE-to-LE wrap taken as aft + top + bottom faces; forward chamfers inside x1.1 |
| f14.lwa23-layup7 | 1 | part | 1.7 est | none quantified | UND 3 in and BID 5 in strip lengths not in the repo |
| f14.baggage-hole | 1 | part | 7.4 est | BID 3 x (887.2 + 2 x 113.67 lap) x 1.1 → 2.69 yd → 0.111 gal / 0.226 qt | hole 5 x 14 not subtracted |
| f14.end-bulkhead-layup9 | 1 | part | 0.5 est | BID 88.2 x 1.1 → 0.07 yd → 0.003 gal / 0.006 qt | flox corners not counted |
| f14.nut-access-hole | 1 | part (dry micro) | 1.5 est | none | |
| f14.fit-fuselage | 1 | none | 5.9 est | none | shims unsourced; CP25 hint wedge cut |
| f14.bond-spar | 1 | part | 8.3 est | BID 2 plies x 2 in x 2 sides x 2(6.5 + 8.08) at BL 21 = 233.3 x 1.1 → 0.19 yd → 0.008 gal / 0.016 qt; EM12 angle 4 x 8 in = 2.67 ft (`derived`, p87) | firewall tape and the 10-ply W16 bridges have no size: excluded, so cloth reads very low; W16 wedge size, 16 bolts: unsourced; EM12 alloy not in the repo |
| f14.sh1-tabs | 1 | none | 0.3 est | none | SH1 plate stock and AN4-17A count unsourced |

Buddy steps: 1 (`f14.spruce-layup6`). Other helpers seen in logs (bottom cap card, strut cover) are
convenience, not a second person the step needs.

## 5. New catalog items (not in prices.yaml)

Read 2026-10-18 unless noted. Flags use the Contract 3 vocabulary.

| id | label | vendor | part | URL | price | unit | flag |
|---|---|---|---|---|---|---|---|
| foam-pvc-0p25 | PVC foam 1/4 in, H45, 32 x 48 sheet | Aircraft Spruce | 01-12300 | https://www.aircraftspruce.com/catalog/cmpages/divinycellfoam.php | 43.50 | each (sheet) | page. Density match to the spar list not checked |
| foam-pvc-h100-0p25 | PVC foam 1/4 in, H100, 42.1 x 42.5 sheet (for R100 per CP25) | Aircraft Spruce | 01-01310 | https://www.aircraftspruce.com/catalog/cmpages/divinycellfoam.php | 97.75 | each (sheet) | page. H100 as an R100 equivalent is my assumption |
| urethane-foam-2x24x48 | urethane foam 2 x 24 x 48 | Aircraft Spruce | 01-11900 | https://www.aircraftspruce.com/catalog/pnpages/01-11900.php | 51.75 | each (sheet) | page |
| spruce-1x1 | spruce capstrip 1 x 1 in | Aircraft Spruce | 02-11 | https://www.aircraftspruce.com/catalog/pnpages/02-11.php | 6.50 | ft | page |
| al-2024-bar-0125x2 | 2024 bar 1/8 x 2 in | Aircraft Spruce | 03-42900 | https://www.aircraftspruce.com/catalog/mepages/alumbar.php | 15.50 | ft | page. Listed as T3/T4; T3 must be requested |
| al-2024-bar-025x2 | 2024 bar 1/4 x 2 in | Aircraft Spruce | 03-43700 | https://www.aircraftspruce.com/catalog/mepages/alumbar.php | 13.60 | ft | page (cheaper per ft than the 1/8 bar, as listed) |
| al-2024-angle-1x1x0125 | 2024-T3 angle 1 x 1 x 1/8 | Aircraft Spruce | 03-47300 | https://www.aircraftspruce.com/catalog/mepages/alumangle.php | 7.50 | ft | page. EM12 alloy not confirmed |
| al-tube-5052-0p25-6ft | 5052-O tube 1/4 x .035, 6 ft length | Aircraft Spruce | 03-39300-6 | https://www.aircraftspruce.com/catalog/mepages/alumtube_5052.php | 12.60 | each (6 ft) | page. Sold in 6 ft steps |
| ng-strut-longez | Long-EZ nose gear strut | Aero Composites | none listed | https://aerocomposites.aero/?p=1167 | 170.00 | each | page (page dated 2025-01-12) |
| strut-cover-sc | Long-EZ strut cover SC | Aero Composites | none listed | https://aerocomposites.aero/?p=1167 | 50.00 | each | page |
| nose-wheel-cover-nb | Long-EZ nose wheel cover NB | Aero Composites | none listed | https://aerocomposites.aero/?p=1167 | 50.00 | each | page. Same part as the NB box by name only |
| rudder-pedal-longez | Long-EZ rudder pedal weldment | not found | | | null | each | unsourced |
| flush-screw-nose-door | nose door flush screw | | | | null | each | unsourced (spec not in the repo) |
| nutplate-nose-door | nose door nutplate | | | | null | each | unsourced |
| particle-board-sheet | particle board 4 x 8 sheet (jig) | | | | null | each | unsourced (any lumber yard) |

Existing ids reused: `bid-7725`, `und-7715`, `mgs-lr285-gal`, `mgs-h287s-qt`, `peel-ply-582c`,
`foam-pvc-0p2`. Not re-read for price this round: `micro-bubbles-1lb` and `flox-cotton-1lb` (used
throughout but not quantified).

## 6. Open gaps (what would clear them)

- Per-step hours: someone's own timed Long-EZ log for ch13 and ch14. The Glantz ch13 total includes
  mods, and the worm drive and shock strut have no time at all. Owner actuals (Contract 20a) are the
  real fix.
- Nose outlines (A6/A7) and the spar cap-trough templates (A11): every nose area above is a fitted
  model. The plies with no printed size (NG30 pads, pivot-block covers, canard-cutout and bumper
  plies, F22 corner plies, firewall tape, W16 bridges, layup 7 strips) are excluded, so cloth and
  resin read low on those ops.
- Foam specs: CS1/CS4 thickness and the CS2/CS3 urethane core sizes (p90 foam list), and the NG31 R100
  substitute.
- Hardware: worm drive parts, NG14/NG51/CS13, CNL bushings, AN970, nutplates, door screws, the 16
  EM12 bolts, AN4-17A count, W16 wedges, pedal weldments. A plans hardware list or the AS Long-EZ
  hardware kit (01-01200, $2067.34 on the kit page; components not opened) would close most of them.

## p2-ch15-19-sourcing.md

# Rehearsal sourcing, P2 (chapters 15 to 19, 54 ops)

Research only. Read 2026-10-18. No repo file was changed. The values file is
`p2-ch15-19-plan-values.yaml` in this directory. This record holds the evidence, the arithmetic and
the gaps behind it. Method and constants follow `docs/harness/rehearsal-sourcing-p1.md`.

Scope: every op in `guide/graph/ch15.yaml` to `ch19.yaml`. None is a stub and none is GU-only (two
are `[roncz]`: `f16.pitch-pushrod`, `f17.pitch-trim`). Ops: ch15 4, ch16 11, ch17 5, ch18 16, ch19 18.

Plans text: not read (the scan is private). Step content comes from the graph summaries and
completions. Wing dimensions come from `config/aircraft_config.py` (book-cited fields, plans-1980
p118 and p126).

## 1. Sources used

| key | what | URL | used for |
|---|---|---|---|
| GLANTZ-T | Long-EZ time and budget page | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | checked: ch15 to ch19 are listed as "still to come", no hours |
| PUSH-15 | Long-EZ N916WP log, ch15 | https://www.longezpush.com/chapter-15-firewall-assembly/ | no ch15-accessory hours (the timed work is ch4/ch14 firewall mounting) |
| PUSH-16 | same log, ch16 | https://www.longezpush.com/chapter-16-flight-control-systems/ | console foam: one 32x48 sheet of 3/8 foam (28 Jun 2012); no step hours |
| PUSH-17 | same log, ch17 | https://www.longezpush.com/chapter-17-pitch-roll-trim-systems/ | builder fitted an aftermarket trim, not the plans parts: not used |
| PUSH-18 | same log, ch18 | https://www.longezpush.com/chapter-18-canopy/ | canopy foam, carve, outside glass, removal, pads, inside glass, hinges (dated times below) |
| PUSH-18L | same log, latch hardware | https://www.longezpush.com/chapter-18-canopy-latch-hardware/ | builder used four latches and a custom handle (a mod): not used for hours |
| PUSH-19P | same log, wing prep | https://www.longezpush.com/chapter-19-wings-ailerons-wings-attach/ | cores bought pre-cut from Feather Lite, so no core-cutting hours; jig segments 2.5 h (one sitting only) |
| PUSH-19R | same log, right wing | https://www.longezpush.com/chapter-19-wing-build/ | helpers: Gina on the epoxy station for the shear web (30 Jul 2012) and the spar cap (4 Aug 2012); bottom cap laid as 7 plies, top 10 (CP25 extra plies); resin cross-check |
| PUSH-19L | same log, left wing | https://www.longezpush.com/chapter-19-left-wing-build/ | Kevin on the epoxy station and laying glass for the upper skin (22 Aug 2012); 65 x 1 in peel ply strip at the aileron |
| PUSH-19A | same log, ailerons | https://www.longezpush.com/chapter-19-ailerons/ | P6 hinge cut to 2 x 8 in and 4 x 6 in (supports the hinge item); no hours |
| PUSH-19M | same log, wing mount | https://www.longezpush.com/chapter-19-mounting-wings-to-cs-spar/ | `f19.attach` hours; 12 LWA9 bushings; worked alone |
| SPOD-15/16/18/19 | Cozy MKIV log (mykitlog, Spodman), per-entry hours, categories CH15 Firewall (45 h), CH16 Controls (90 h), CH18 Canopy (481 h), CH19 Wings (409 h) | http://www.mykitlog.com/users/category.php?user=Spodman&project=2369&category=12774 (15), =11429 (16), =12944 (18), =12636 (19) | per-entry hours, summed by entry title |
| AS-* | Aircraft Spruce product pages | listed in section 5 | prices |

SPOD caveats: a Cozy MKIV, not a Long-EZ. Its ch17 is the speed brake (not trim), so it is not used
for ch17. Its canopy is front-hinged (entries say "FHC"), so it is used only for plexiglass trimming
and the safety catch. Brakes are on the pedals, so there is no brake-cable entry. I used the wing
entries most, since the Cozy wing is built the same way (cores, shear web, caps, skins, ailerons).
SPOD entries that look like repairs ("BL31 rib repair", "leading edge foam glitch") or cosmetics
("engine turning", "making pretty") are left out.

## 2. Hours method

- **community** = one log times this step. Either a single entry, or a sum of entries whose title
  names this step and nothing else. The URL is the log page. 19 ops.
- **estimate** = entries split across ops, an entry with a mixed title split in half, or a log that
  is a weak analog (a different canopy, a different pitch system). 17 ops.
- **omitted** = no log times the step. 18 ops.
- All hours cover the whole airplane: both wings in ch19, both consoles and so on.

### Chapter 15 (SPOD-15, Jan 2023 entries)

| op | hours | flag | arithmetic |
|---|---|---|---|
| f15.parts-fab | 1.0 | estimate | one entry, "control hardware of various sorts" (12 Feb 2018). Most parts are bought, and whether this entry covers the CS/BA parts is not confirmed |
| f15.stainless-firewall | 13.3 | estimate | metal firewall 3.7 + installation frame 4.0 + metal/fibrefrax install 1.3 + installing 1.8 + half of "steel firewall and rudder clickbonds" 5.0/2. Leaves out the fibrefrax-only entry (insulation is deferred per the op) and 9.8 h of engine-turning and cosmetics. Cozy fits with a frame; Long-EZ uses silicone |
| f15.belcrank-brackets | 9.8 | estimate | rudder hardware clickbonds 3.0 + 4.3 + the other half of the mixed entry 2.5. The Cozy uses clickbonds, not through-bolts |
| f15.master-cylinders | none | | the Cozy has cylinders on the pedals; no Long-EZ log times this |

### Chapter 16 (SPOD-16)

| op | hours | flag | arithmetic |
|---|---|---|---|
| f16.side-consoles | none | | PUSH gives no total; Spodman's consoles are in his ch24 and are a different part |
| f16.pivot-bulkheads | 1.0 | estimate | "CS109/118 bulkhead install" 0.3 + "fuselage bearing supports" 0.7. The glassing does not appear to be logged, so this reads low |
| f16.firewall-bearing | 0.6 | community | "firewall bearing installation" 0.4 + 0.2 |
| f16.torque-tubes | 24.1 | estimate | Controls-Roll 9.6 + roll control hardware 2.0 + roll control installation 5.2 + forward control bearings 4.0 + 1.3 + half of "bearings/rudder pulleys" 4.0/2 |
| f16.sticks-pushrods | none | | only stick-grip entries, which are not this step |
| f16.pitch-pushrod | 3.9 | estimate | pitch control push rods 1.9 + 1.0 + pitch controls 1.0. The Cozy pitch run differs |
| f16.aileron-linkage | 13.8 | estimate | roll control rigging 4.0 + 4.0 + 4.1 + refit aileron hardware 1.0 + reinstall 0.7 |
| f16.rudder-conduit | 4.5 | estimate | conduits 3.0 + rudder/brakeline conduit 0.5 + right rudder cable conduit 1.0. The electrical-conduit entries are excluded |
| f16.rudder-cable-rig | 8.8 | community | "installing rudder cables" (14 Feb 2025) |
| f16.brake-cables | none | | no Cozy equivalent |
| f16.adjustable-pedals | none | | optional; not logged |

### Chapter 17: no hours

The Long-EZ log (PUSH-17) fitted an aftermarket pitch trim and a modified roll trim. The Cozy's ch17 is
a different system. All five ops are left without hours.

### Chapter 18 (PUSH-18 unless noted)

| op | hours | flag | evidence (post date) |
|---|---|---|---|
| f18.trim-plexi | 7.8 | community | SPOD-18: canopy trimming 1.5 + initial 4.4 + middle 1.1 + final 0.8 (Apr 2021). Trimming plexiglass is the same task on either canopy |
| f18.locate-blocks | 2.0 | estimate | 11 Jun 2018, "a couple of hours" test-fitting the canopy; the blocks and tape are not timed |
| f18.check-ab | none | | a measurement |
| f18.foam-core | 4.8 | community | 30 Jun: about 2 h aft blocks + almost 2 h forward blocks; 7 Jul: about 45 min centre front block |
| f18.carve-outside | 4.0 | community | 9 Jul: over 4 h prepping the frame for glass |
| f18.glass-outside | 11.0 | community | 9 Jul: 8 h external layup; 10 Jul: 3+ h trimming the overhang |
| f18.cut-remove | 0.5 | community | 14 Jul: canopy off in a little over half an hour. Building the brace is untimed, so this reads low |
| f18.carve-inside | 0.5 | community | 25 Jul: half an hour removing inside foam. Reads low |
| f18.pads-inside-glass | 16.5 | community | 17 Jul: about 5 h glassing all hard points; 18 Jul: 1 h cleanup; 30 Jul: 3.5 h right rail; 31 Jul: 3 h aft frame; 1 Aug: about 4 h left side. His hard points include his extra latch, so this reads slightly high |
| f18.rear-cover-inside | none | | 30 Jul has 1 h of cleanup on the turtleback ply, but the layup itself is untimed |
| f18.vent-brace | none | | his cross brace is a different part |
| f18.hinges | 1.8 | community | 28 Jul: 45 min on the hinge hard points; 2 Aug: 1 h on hinge angles. Reads low |
| f18.door | none | | |
| f18.latches | none | | PUSH used four latches and a custom handle (a mod); the Cozy's latches are a different design |
| f18.front-cover | none | | SPOD's panel cover (about 22 h) is built differently |
| f18.safety-catch | 5.0 | estimate | SPOD-18: canopy safety catch 3.0 (16 May 2021) + 2.0 (27 Mar 2026), on a front-hinged canopy |

### Chapter 19 (SPOD-19 both wings; PUSH-19M for attach)

| op | hours | flag | arithmetic |
|---|---|---|---|
| f19.jig | 13.9 | estimate | wing jigs 4.2 + 2.4 + 2.2 + "jigs #2" 1.3 + 1.3 + half of "jigs and cores" (2.5 + 2.5)/2. Spodman built a second set; on a Long-EZ the jigs may be reused |
| f19.cut-cores | 26.8 | estimate | hot-wire templates 6.1 + the other half of "jigs and cores" 2.5 + 1/3 of the core pool. Pool = right cores 7.6 + 20.9 + TE core assembly 3.0 + left cores 23.1 = 54.6, so 1/3 = 18.2 |
| f19.core-cutouts | 18.2 | estimate | 1/3 of the core pool. **The even three-way split is the weakest number in the ch19 set** |
| f19.mount-cores | 20.7 | estimate | 1/3 of the core pool + attach-bolt access 1.4 + 1.1 |
| f19.hardpoints | 11.4 | community | right hardpoints 3.7 + 1.6 + 1.7 + 1.1, left 2.4 + 0.9 |
| f19.shear-web | 25.8 | community | right 1.5 + 2.0 + 1.1 + 0.4 + 7.0 + 3.8; left prep 1.7 + 1.6; left 5.5 + 1.2 |
| f19.pads-plates | none | | not a separate entry |
| f19.le-cores | 6.6 | community | fitting LE cores 2.6 + nose core prep 1.0 + nose block assembly 3.0 |
| f19.bottom-cap | 23.9 | community | left cap prep 2.4 + 3.0 + 0.7 + lower cap prep 1.0 + 1.0 + 2.4 + 0.9 + lower cap 2.6; right prep 2.0 + 1.7 + lower cap 2.2 + 4.0 |
| f19.bottom-skin | 38.4 | community | left prep 3.0 + 2.3, layup 8.0, skin 8.2; right prep 3.0, layup 5.9 + 8.0 |
| f19.top-cap | 27.3 | community | right prep 1.3 + 2.9 + 1.2 + 1.2, layup 5.4, cap 6.2; left 2.5 + 2.7 + 3.9 |
| f19.rudder-conduit | none | | not logged separately |
| f19.top-skin | 20.1 | community | right 6.0 + 1.8; left prep 2.7 + 0.6 + 0.6 + 1.7 + 0.7, layup 6.0 |
| f19.ribs | 12.9 | community | right ribs 0.9 + 1.8 + 2.6; left inner ribs prep 2.0 + 1.8 + 1.2, layup 2.0 + 0.6 |
| f19.aileron-cut | 46.3 | estimate | half of the aileron pool. No entry names the cut. Pool 92.65 = right aileron entries 59.7 (including hinges 16.2 and hardware 6.9 + 2.0 + 0.8 + 2.0 + 1.0) + left 27.95 (with half of "installation, prep for wing attach") + "complete aileron installation" 5.0 (2022) |
| f19.aileron-build | 46.3 | estimate | the other half. The cut likely takes far less than half, so the split overstates the cut and understates the build; together the two are sound. The Cozy entries include cove work that may be a mod |
| f19.controls | 9.8 | estimate | CS-127 hardware 1.2 + aileron control hardware 5.0 + port bellcrank 1.1 + 0.5 + aileron control runs 2.0 |
| f19.attach | 11.0 | community | PUSH-19M, 13 Sep 2016: about 2 h per wing levelling (4 h) + a bit over 2 h drilling; 14 Sep: "about 5 hours total today". Read as 4 + 2 + 5. If the 14 Sep "5 hours" already includes the previous evening, the figure is 9. Bushing trim (15 Sep) is untimed. For comparison, SPOD-19 logs 35.6 h for the same step |

## 3. People (buddy steps: 3)

`people: 2` only where a log shows a second person doing the work the plans layup needs:
- `f19.shear-web`: Gina on the epoxy station for the shear web (PUSH-19R, 30 Jul 2012).
- `f19.bottom-cap`: Gina working the epoxy station for the bottom spar cap (PUSH-19R, 4 Aug 2012).
- `f19.top-skin`: Kevin on the epoxy station and laying glass for the upper skin (PUSH-19L, 22 Aug 2012).

Not counted, because it was convenience or not the work itself: Gina and Kevin helping pull and align
the cores (27 Jul 2012); "could have used another person" when moving a wing (root-rib post). The
bottom skin, the top cap and the canopy work all show one person.

## 4. Per-op buys and cure

Constants are the P1 set: 38 in roll = 1368 in² per yd; UND 0.2095, BID 0.2633 kg per yd; 1.1 trim
factor; resin = cloth by weight; 100:40 split; LR285 4.561 kg/gal, H287 0.894 kg/qt; peel ply pack =
10800 in². Micro, flox and slurry are not in any buy, so every resin figure reads low.

**Resin cross-check.** PUSH-19R (8 Aug 2012) says he had used almost 1.3 gal of slow hardener by then,
partway through the wings. By our method, all of ch19's glass comes to about 2.97 qt of hardener for
both wings (0.36 + 0.14 + 1.01 + 0.20 + 1.01 + 0.02 + 0.02). So the 1:1 rule, without slurry and
flox, reads several times low on wing work. I did not resolve what PUSH's figure includes.

Wing geometry (config, book p126): chords 49.97 (derived) / 42.7 / 31.35 / 20.0 at BL 23 / 55.5 /
106.25 / 157. Planform per wing = (49.97+42.7)/2×32.5 + (42.7+31.35)/2×50.75 + (31.35+20)/2×50.75 =
4687.9 in².

| op | buy (arithmetic) | gaps |
|---|---|---|
| f15.master-cylinders | `master-cylinder` 2, derived (one per brake) | model not in the repo ("Cleveland or Gerdes"); no price |
| f15.stainless-firewall | none | stainless sheet size and gauge, silicone, studs: not in the summary. **Cure:** set to `none` because the two-day cure is silicone and Contract 2 ties `cure != none` to a resin. The integrator decides whether silicone needs a resin entry |
| f15.belcrank-brackets | none | AN3 bolt count not printed in the summary; dry micro fill is unquantified |
| f16.side-consoles | `foam-pvc-0p375-32x48` 1 sheet, estimate (PUSH-16: "a FRESH piece" of 32x48 3/8 foam for consoles and armrests) | the summary says only "thin foam"; 3/8 is PUSH's choice. BID areas unknown |
| f16.rudder-conduit | `rudder-conduit-nylon` 2 × 82 in / 12 = 13.67 ft, derived (printed, p103) | conduit size not in the summary; 3/32 cable length unknown |
| f16 others | none | cable lengths, rod ends, bearings, bolts: counts not printed in the summaries |
| f17 all | none | PT1/RT3 birch sizes, spring stock, phenolic: not dimensioned in the repo. The optional tab is left out of the buy |
| f18.trim-plexi | `canopy-bubble` 1, derived | |
| f18.vent-brace | `arrow-shaft-5-16` 3, estimate | the count is printed in the op text, but two source pages are cited and I did not pin which one, so it is not marked `official`. Shaft length is not printed |
| f18 glass ops | none | frame width, pad width and cover areas are not in the repo, so BID/UND for glass-outside, pads (15 plies × 8 pads), inside glass, rear cover, vent block and front cover are all unquantified. The 2 in urethane volume is unknown. Hinges are not in the buy: the size is not in the repo (PUSH bought MS20001-series hinges) |
| f19.cut-cores | `styrofoam-8x16x67` 10 and `styrofoam-8x16x42` 4, derived: 5 × 7×14×64 and 2 × 7×14×41 blocks per wing (config `wing_book_foam_blocks`, book p118) × 2 wings. Each block cut from the next stock size up | the summary says "seven blocks ... into five core pairs", and config says "per wing". I followed config; if the seven are for the whole airplane, halve both quantities. Styrofoam vs other core foam is not stated in the repo |
| f19.shear-web | UND 5.45 yd; LR285 0.179 gal; H287 0.365 qt | web height taken as the section's maximum thickness (t/c × chord): 6.92 / 4.92 / 3.00 in at BL 55.5 / 106.25 / 157, and **8.10 at BL 23 assuming BL 55.5's 16.2 %**. Zone areas (linear): BL 23–70 340.1, 70–120 268.4, 120–157 136.9 in²; ply-area 6×340.1 + 4×268.4 + 2×136.9 = 3388 in² per wing; × 1.1 × 2 / 1368. The web sits near max thickness, so this reads slightly high. Edge wraps are left out |
| f19.pads-plates | BID 3 × (16 + 24) × 1.1 × 2 / 1368 = 0.193 yd; 0.008 gal; 0.016 qt | one 4×4 and one 4×6 pad per wing **assumed** (one per plate) |
| f19.bottom-cap | UND 3 in × 432.5 in (142+135+84+52+19.5) × 1.1 × 2 / 1368 = 2.087 yd; 0.069 gal; 0.140 qt | tape cut from the 38 in roll, along the warp. Base plies only: the CP25 box adds plies when the tape is thin, and PUSH laid 7 bottom / 10 top |
| f19.bottom-skin | UND 2 × 4687.9 × 1.1 × 2 / 1368 = 15.08 yd; 0.495 gal; 1.010 qt; peel ply 2 × 65 × 1 / 10800 = 0.012 pack | tip BID ply size not printed (excluded); the 1 in strip width is PUSH's |
| f19.top-cap | UND 3 × 613 (142+142+119+90+61+39+20) × 1.1 × 2 / 1368 = 2.957 yd; 0.097 gal; 0.198 qt | base plies only, as above |
| f19.rudder-conduit | `nylaflow-3-16` (TE length 32.5/cos 12.49° + 101.5/cos 11.36° = 136.8 in, + 2 × 2 in) × 2 / 12 = 23.47 ft, estimate | the run is taken as parallel to the TE; the A-sheet curve is not held. 05-00110's 0.138 ID gives the 0.025 wall the op prints |
| f19.top-skin | as the bottom skin: 15.08 yd, 0.495 gal, 1.010 qt, peel ply 0.012 | the third UND ply ahead of the hinge line has no area I can compute from the repo (excluded); tip BID excluded |
| f19.ribs | layup 5 only: UND 2 × 3 × 30 × 1.1 × 2 / 1368 = 0.289 yd; 0.010 gal; 0.019 qt | layups 6 to 8 have no area (rib section not held) |
| f19.aileron-build | `steel-rod-0p375` 65 × 2 / 12 = 10.83 ft, derived; `piano-hinge-p6-3ft` (8+6+6) × 2 = 40 in / 36 = 1.11 pieces, derived | rod material not stated; P6 matches PUSH-19A, not the repo. Torque tube stock, rivets and lead: not quantified |
| f19.attach | `an8-21a` 4, `an8-23a` 2, derived | the summary says "two AN8-21A and one AN8-23A" after "three holes"; I read that as per wing (× 2). LWA9 bushings (twelve, printed) come from the ch14 LWA work, so they are not bought here |
| f19 others | none | jig plywood (outlines on templates), hard-point liner (depression length unknown), layup 9/10/11 areas, CS127/CS128 stock (4130 per CP49): unquantified |

Cure: glass, flox and micro ops are `part` with `mgs-285-287`. Mechanical, fitting, carving and
measuring ops are `none`. `f18.locate-blocks` is `none`: its temporary blocks are tacked on, and
the adhesive is not named in the summary. `f18.cut-remove` is `none` too: the lumber is tacked on
with Bondo, which is not the MGS resin.

## 5. New catalog items

Read 2026-10-18. Flags use the Contract 3 vocabulary.

| id | label | vendor | part | URL | price | unit | flag | in buy |
|---|---|---|---|---|---|---|---|---|
| styrofoam-8x16x67 | Styrofoam large cell 8 x 16 x 67 | Aircraft Spruce | 01-10800 | https://www.aircraftspruce.com/catalog/pnpages/01-10800.php | 199.75 | each | page | yes |
| styrofoam-8x16x42 | Styrofoam large cell 8 x 16 x 42 | Aircraft Spruce | 01-10600 | https://www.aircraftspruce.com/catalog/pnpages/01-10600.php | 126.75 | each | page | yes |
| foam-pvc-0p375-32x48 | H45 PVC foam 3/8 x 32 x 48 | Aircraft Spruce | 01-12400 | https://www.aircraftspruce.com/catalog/pnpages/01-12400.php | 53.75 | each | page | yes |
| nylaflow-3-16 | Nylaflow tube 3/16 OD x .138 ID | Aircraft Spruce | 05-00110 | https://www.aircraftspruce.com/catalog/pnpages/05-00110.php | 0.75 | ft | page | yes |
| piano-hinge-p6-3ft | piano hinge MS20001P6, 3 ft | Aircraft Spruce | 03-00055-3 | https://www.aircraftspruce.com/catalog/pnpages/03-00055-3.php | 189.00 | each | page | yes |
| an8-21a | bolt AN8-21A | Aircraft Spruce | AN8-21A | https://www.aircraftspruce.com/catalog/hapages/an8.php | 5.85 | each | page | yes |
| an8-23a | bolt AN8-23A | Aircraft Spruce | AN8-23A | https://www.aircraftspruce.com/catalog/hapages/an8.php | 4.35 | each | page | yes |
| master-cylinder | brake master cylinder ("Cleveland or Gerdes") | | | | null | each | unsourced. A Cleveland 10-30 (05-13319) reads $960.00 at https://www.aircraftspruce.com/catalog/pnpages/05-13319.php, but nothing in the repo says the 10-30 is the plans part | yes |
| canopy-bubble | Long-EZ plexiglass canopy | none found | | | null | each | unsourced. AS does not list one; PUSH sourced a new canopy through a builder contact | yes |
| steel-rod-0p375 | 3/8 in steel rod (aileron) | | | | null | ft | unsourced. Grade not in the repo | yes |
| rudder-conduit-nylon | nylon rudder conduit (fuselage) | | | | null | ft | unsourced. Size not in the repo; it may be the same Nylaflow as the wing | yes |
| arrow-shaft-5-16 | 5/16 in arrow shaft (canopy brace) | | | | null | each | unsourced | yes |
| urethane-foam-2in | green urethane foam, 2 in (canopy frame) | | | | null | sqft | unsourced. The AS foam page lists no 2 in urethane | no (qty unknown) |
| stainless-firewall-sheet | stainless firewall sheet | | | | null | each | unsourced. Size and gauge not in the repo | no (qty unknown) |

The existing ids reused are `und-7715`, `bid-7725`, `mgs-lr285-gal`, `mgs-h287s-qt` and
`peel-ply-582c` (counted in packs, as in P1).

## 6. Open gaps (what would clear them)

- Ch17, ch15 master cylinders, ch16 consoles and sticks, and most ch18 latch, door and cover work have
  no hours: they need a Long-EZ log that builds the plans parts. The owner's actuals (Contract 20a)
  are the real fix.
- The core-pool and aileron-pool splits are even splits. A log that times cutting separately from
  mounting, and the aileron cut separately from the build, would replace them.
- Canopy glass areas and wing tip, rib and aileron layup areas need the A-sheets or Contract 18
  layup geometry.
- The BL 23 web height uses an assumed t/c. A root thickness from the A-sheet would clear it.
- Resin reads low (see the PUSH cross-check). A per-op slurry/flox allowance needs a measured basis.
- Check the per-wing reading of the foam block count (config vs the op wording) and the AN8 count
  against p118 and p134.

## p2-ch20-30-sourcing.md

# Rehearsal sourcing, P2 (chapters 20 to 26 and 30, 79 ops)

Research only. Read 2026-10-18. No repo file was changed. The values file is
`p2-ch20-30-plan-values.yaml` in this directory; this record holds the evidence, the arithmetic and
the gaps for it. Method and conventions follow `rehearsal-sourcing-p1.md` (same constants, same
flags), with one change to the hours rule, explained in section 2.

Scope: every op in `guide/graph/ch20.yaml` to `ch26.yaml` and `ch30.yaml`. None is a stub and none has
variants exactly `[gu]` (all of ch30 is `[roncz]`), so nothing was skipped. Step content comes from
the graph summaries and `config/aircraft_config.py`; I did not read the plans pages. Every value
file entry parses with `guide.schema._plan`, and every buy item is either an existing catalog id or
one of the 12 NEW ids in section 5.

## 1. Sources used

| key | what | URL | used for |
|---|---|---|---|
| SPOD | Cozy MKIV log (mykitlog, Spodman), per-entry hours by chapter | http://www.mykitlog.com/users/category.php?user=Spodman&project=2369&category=N (N below) | most hours. CH20 winglets 12772 (178.9 h, 94 entries), CH21 strakes 13817 (389.1 h), CH22 electrical 14194 (7.7 h), CH23 engine and cowl 13161 (440 h), CH24 seats/armrests 12773 (244 h), CH25 finishing 14195 (541.2 h), CH10 canard 10248 (114.6 h), CH11 elevators 10558 (57.6 h), CH12 fit canard 10872 (18.6 h) |
| GLANTZ-T | Long-EZ log, time and budget page | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | ch10 canard 55 h (Roncz; his ch10 post names the Roncz plans). Chapters 15 to 26 are listed as still to come, with no hours |
| GLANTZ-BOT | same blog, canard bottom spar cap and skin | https://www.aryjglantz.com/2015/06/canard-bottom-spar-cap-and-skin.html | cap about 4 h; cap and skin a 7+ h layup with a helper; "can't imagine doing this one solo" |
| GLANTZ-TOP | same blog, canard top cap and skin | https://www.aryjglantz.com/2015/08/canard-top-cap-and-skin.html | cap and skin 8 h start to finish with a helper; would not do it solo |
| GLANTZ-INS | same blog, prep for top skin and hinge inserts | https://www.aryjglantz.com/2015/06/prep-for-top-skin-glassing-and-hinge.html | about an hour to set all 7 inserts |
| GLANTZ-WPP | same blog, winglets preinstall prep | https://www.aryjglantz.com/2018/01/winglets-preinstall-prep.html | "10+ hours" carving the winglet flox corners |
| GLANTZ-STB, -STT, -FL | same blog, strake outside bottom / outside top / fuel lines and OD ribs | https://www.aryjglantz.com/2019/10/strake-outside-bottom-layups.html, .../2019/12/strake-outside-top-layups.html, .../2019/08/fuel-lines-and-od-ribs.html | two friends for the bottom layups and for lifting the fuselage; a helper outside the outlet-tube hole |
| PUSH-ST | Long-EZ N916WP log, strake build | https://www.longezpush.com/strake-build/ | about 2 h marking the fuselage cutouts (19 Nov 2020) |
| PUSH-10 | same log, chapter 10 Roncz canard | https://www.longezpush.com/chapter-10-roncz-canard/ | about 2.5 h aligning the canard before the top layups |
| AS-* | Aircraft Spruce product pages | section 5 | prices |

Checked and found to give no usable per-step hours: the other PUSH chapter 20 to 26 pages
(winglets, cowlings, consoles, thigh support, finishing, upholstery, electrical: hours there are cure
waits or a 30 h total for a much larger panel), and the other GLANTZ chapter 20 to 24 posts (no times).
GLANTZ's time page stops at chapter 14, so there is no Long-EZ chapter total for 20 to 26.

## 2. Hours method

**Rule change from P1.** P1 had no step-level logs, so it split Long-EZ chapter totals and flagged
everything `estimate`. Here SPOD logs each work session with a label, so:

- `community` = one builder's own logged time for the step: SPOD entries whose labels name exactly
  the op's work, summed (unscaled), or a GLANTZ or PUSH statement of hours for that step. The URL is
  the chapter category page (SPOD) or the post. Where the log covers only part of the op, the value
  is a floor, and the table says so.
- `estimate` = anything I had to apportion: a pool of SPOD entries split over several ops, a
  remainder (55 h less the parts GLANTZ timed), or figures from two builders added together.
- omitted = no log times the step (20 ops). Never invented.

**Caveats that apply to every SPOD number.**
- SPOD is a Cozy MKIV. The winglets/rudders and the Roncz canard and elevators are the shared design,
  so those map well. The strakes (sump tanks, smoke-oil tank, sight gauges), the cowl (not a trimmed
  VariEze cowl), the armrests (for the Long-EZ consoles) and the whole-airframe finishing differ
  more. I left out entries for Cozy-only or mod work: smoke oil, landing light, sight gauges,
  capacitance probes, NACA ducts, vortilons, armrest mods.
- Pace. On the chapters both logged (4, 5, 6, 7, 10, 13, 14), GLANTZ took 492 h and SPOD 753 h, a
  ratio of 0.653. So SPOD values probably read about 1.5x high for a GLANTZ-pace builder. I did not
  scale them, because scaling would add one ratio to every number. Apply 0.653 downstream if wanted.
- Redos and rework entries from years later (2019 canard refit, 2021 rudder stops) are left out, as
  in P1.

**Ch30, Roncz canard.** GLANTZ's 55 h ch10 total, less the steps he timed himself (bottom cap and
skin 7, top cap and skin 8, hinge inserts 1), leaves 39 h. I split that over templates/cores, shear
web and jig assembly with SPOD CH10 weights (26.6, 17.5 and 12.7 h; × 39/56.8). Lift tabs get no
hours: SPOD logs only 1.1 h fitting tabs he appears to have bought. The turnover/twist check uses
PUSH's 2.5 h, so GLANTZ's 39 h (which includes his own turnover) reads slightly high. Elevator and
installation ops use SPOD CH11 and CH12.

## 3. Resin

As in P1. `mgs-285-287` is the only resin file, so every op with cure `part` points at it. Two
things are left open:
- **Fuel-proof epoxy.** The ch21 inside layups call for a fuel-proof epoxy (the graph names
  Safe-T-Poxy; GLANTZ used EZ-Poxy 87 on fuel surfaces). There is no resin file for it, so
  `f21.inside-layups` and `f21.close-tank` carry mgs-285-287 and the resin figures. This is wrong
  for the tank interior, and the integrator should decide on a second resin file.
  2026-10-20 owner decision: keep MGS L285/H287 (`mgs-285-287`) on `f07.skin-right`, `f07.skin-left`, `f21.inside-layups` and `f21.close-tank`; delete the `fuel-resistant-tbd` placeholder; UL94 compatibility stays unknown until a Block 5 coupon test.
- **Primer and paint.** These are not epoxy, so `f25.primer` and `f25.paint-seals` are cure `none`.
  The two-day silicone wait before parts come apart is not modelled. `f25.coarse-fill` and
  `f25.feather-fill` are `part` (micro and epoxy).

## 4. Per-op findings

Constants (same as P1): 38 in roll = 1368 in² per yd; UND 0.2095 and BID 0.2633 kg per linear yd;
×1.1 overlap/trim; resin to cloth 1:1 by weight, split 100:40, LR285 4.561 kg/gal, H287 0.894 kg/qt;
net, no scrap. New in P2: foam sheets are 32 × 48 = 1536 in²; the strake planform is the shoelace area
of (BL, FS) = (12.1, 50), (23, 73.3), (45, 99.5), (45, 121.82), (23, 118.5), (11.3, 116.74) from the
config `stk_book_*` stations, with the spar face swept 8.57°. That gives **1380.2 in² per side**,
a spar edge of 34.08 in and a fuselage edge of 66.75 in. The winglet face is a trapezoid,
(27.1 + 11.4)/2 × 47 = 904.75 in²; the 11.4 tip chord is a derived-medium value. Micro, flox and
slurry resin are not in any buy, so resin reads low wherever foam is slurried.

Columns: people, cure, hours, hours evidence, buys (arithmetic → item qty (flag: note)), gaps.

| op | people | cure | hours | hours evidence | buys | gaps |
|---|---|---|---|---|---|---|
| f20.cut-cores | 1 | none | 18.7 community | SPOD CH20 core prep 9.3 + cutting 1.5 + core assembly 7.9; the shared "cores and thigh supports" 4.0 entry left out | none |  |
| f20.skins | 1 | part | 22.5 community | SPOD CH20 winglet tips 3.0 + outer skin 7.6 + inner skin 11.9 | winglet face (27.1+11.4)/2 x 47 = 904.75 in2; 2 winglets x 2 faces x 2 UND; BID patch 18 x 14 x 2 -> und-7715 5.82 (estimate: 7238.0 in2 x 1.1 / 1368); bid-7725 0.405 (estimate: 504.0 in2 x 1.1 / 1368); mgs-lr285-gal 0.208 (estimate: cloth 1.326 kg -> mix 1:1); mgs-h287s-qt 0.424 (estimate: 100:40 split) | lower-fin skins and the tip-cap ply have no printed area: excluded; cores reuse wing and canard offcuts, so no foam buy |
| f20.trim | 1 | none | 8.6 est | SPOD "upper winglet installation prep" 17.2 split 50/50 with f20.jig | none |  |
| f20.jig | 1 | none | 8.6 est | the other half of the 17.2. That prep may also hold flox-corner time, so it may double count with the next op | none |  |
| f20.inside-layups | 1 | part | 16.8 est | SPOD layups #1 and #2 6.8 + GLANTZ "10+ hours" carving the flox corners (preinstall-prep post). Two builders, so estimate | layup 1 only: 8 strips 4 x 12 per winglet x 2; layup 2 sizes not printed -> bid-7725 0.618 (estimate: 768.0 in2 x 1.1 / 1368); mgs-lr285-gal 0.025 (estimate: cloth 0.163 kg -> mix 1:1); mgs-h287s-qt 0.052 (estimate: 100:40 split) | layup 2 ply sizes not printed: excluded; flox unsourced |
| f20.outside-layups | 1 | part | 6.0 community | SPOD layup #3 prep and layup 6.0. 13.2 h of generic SPOD "winglet installation" entries are unassigned | per layup BID (15+12)+(25) in x 27.1 chord, UND sum(A+B)=189 in x 27.1; x 2 layups x 2 winglets; width = root chord (assumed, upper bound) -> und-7715 16.474 (estimate: 20487.6 in2 x 1.1 / 1368); bid-7725 4.532 (estimate: 5636.8 in2 x 1.1 / 1368); mgs-lr285-gal 0.727 (estimate: cloth 4.645 kg -> mix 1:1); mgs-h287s-qt 1.484 (estimate: 100:40 split) | ply width along the chord is not printed. The root chord is an upper bound; block A urethane size unprinted |
| f20.lower-fin | 1 | part | 12.7 community | SPOD "lower winglet installation" x 7 | 2 fins x 2 tapes x 2 in x 27.1 (root chord at WL 18.4 assumed) -> bid-7725 0.174 (estimate: 216.8 in2 x 1.1 / 1368); mgs-lr285-gal 0.007 (estimate: cloth 0.046 kg -> mix 1:1); mgs-h287s-qt 0.015 (estimate: 100:40 split) | joint length taken as the 27.1 in root chord at WL 18.4 (assumed) |
| f20.rudder-cut | 1 | none | 6.2 community | SPOD "rudder cut out", one entry | none |  |
| f20.rudder-hang | 1 | part | 53.3 community | SPOD 31 rudder entries 2019 (hinges, coves, bellhorn, springs, cables). 2021 stop and fin-gap mods left out | piano-hinge-ms20257p2-3ft 0.417 (derived: 2 rudders x 7.5 in / 36 in piece); nutplate-rudder-hinge 6 (derived: 3 per rudder x 2); pop-rivet-flush 14 (derived: 7 per rudder x 2) | layup 6 and 7 areas not printed; nutplate and rivet types not printed; whether MS20257P2 is the right hinge is unverified |
| f21.cut-parts | 1 | none | 11.6 community | SPOD "strake bulkheads" x 3 | foam-pvc-0p35-32x48 6 (estimate, was official; downgraded 2026-10-20, plans pages not read: six 32 x 48 sheets, op summary, plans-1980:p141 via the graph) | I read the six sheets as the whole-airplane total. AS sells 3/8 in, the plans say 0.35 (GLANTZ bought 8 sheets) |
| f21.fuselage-cutouts | 1 | none | 2.0 community | PUSH 19 Nov 2020: about 2 h marking the cutouts; the cutting is not timed, so this reads low | none |  |
| f21.jig-bond | 1 | part | 57.7 community | SPOD strake table 13.6 + lower skins 17.5 + assembly 26.6 | none |  |
| f21.inside-layups | 1 | part | 9.3 community | SPOD starboard "taping bulkheads" only; port side and luggage tapes are mixed with other work and left out, so low | per side BID: planform 1380.2 + 1 in laps 34.08 + 66.75 + B23 2 x 155.5 + DB 2 x 196.65; UND 2 plies x 2 in x 33.5 (TLE length used for the diagonal) -> und-7715 0.215 (estimate: 268.0 in2 x 1.1 / 1368); bid-7725 3.514 (estimate: 4370.6 in2 x 1.1 / 1368); mgs-lr285-gal 0.152 (estimate: cloth 0.970 kg -> mix 1:1); mgs-h287s-qt 0.31 (estimate: 100:40 split) | R45 outside face area (fitted outline) and rib laps excluded; the diagonal strip uses the 33.5 in TLE length (planform diagonal computes 34.2) |
| f21.vent-screen | 1 | part | **none** | none: SPOD vents and strainers are logged only with other work | none | vent tube length and screen size not printed |
| f21.close-tank | **2**: closing the wet tank top (plans: a few helpers) | part | 46.3 community | SPOD top-skin prep, cores, inner skins and top-skin install, Apr to Jul 2020 (the 8.8 h day may include a redo) | BID planform per side x 2; UND 2 plies x 2 in x 33.5 x 2 -> und-7715 0.215 (estimate: 268.0 in2 x 1.1 / 1368); bid-7725 2.22 (estimate: 2760.4 in2 x 1.1 / 1368); mgs-lr285-gal 0.099 (estimate: cloth 0.630 kg -> mix 1:1); mgs-h287s-qt 0.201 (estimate: 100:40 split) | layup 5 and 6 tape lengths not printed: excluded; fuel-proof epoxy (the plans want it inside the tank) is not the MGS used here: open |
| f21.od-outlet | 1 | part | 15.1 community | SPOD "OD bulkheads and fuel lines" 8.4 + "fuel feed pipes" 6.7 | tube-5052-0375-6ft 2.667 (derived: 2 tanks x about 8 ft / 6 ft piece) | plans say soft aluminium; the AS 5052-O is stiffer than 3003-O; OD glass area not printed |
| f21.outside-bottom | **2**: turning the airframe over (GLANTZ: two friends) | part | 38.6 community | SPOD inverting prep 3.0 + turnover/prep 18.5 + lower skin 12.3 + blisters 4.8 | per side 2 x (1380.2 + 4 x 34.08 + 0.75 x 66.75 + 33.5 x 2.55 + 25.5 x 2.55) + 5 x 33.5 = 3601.6; x 2 sides -> und-7715 5.792 (estimate: 7203.1 in2 x 1.1 / 1368); mgs-lr285-gal 0.19 (estimate: cloth 1.213 kg -> mix 1:1); mgs-h287s-qt 0.388 (estimate: 100:40 split) | half-OD lap and the sump blister tape (blister width unprinted) excluded |
| f21.outside-top | **2**: righting the airframe (GLANTZ: two friends lifted it) | part | 17.8 community | SPOD Aug 2020 top-skin prep 6.5 + top skin 11.3 | as bottom, 3601.6 per side x 2, + 4th ply 1380.2 on the left only -> und-7715 6.902 (estimate: 8583.3 in2 x 1.1 / 1368); mgs-lr285-gal 0.226 (estimate: cloth 1.446 kg -> mix 1:1); mgs-h287s-qt 0.462 (estimate: 100:40 split) | edge peel ply length not printed |
| f21.pressure-check | 1 | none | 3.1 community | SPOD fuel-tank pressure test entries; the shared smoke-oil test left out | none |  |
| f21.fairing-caps | 1 | part | 33.6 community | SPOD fairing blocks 21.6 + fuel cap installation 12.0 | fuel-cap-dzus-2in 2 (derived: one per tank x 2) | urethane block and its UND skin have no printed size; cap part not found |
| f21.plumbing | 1 | none | **none** | none: SPOD logs the gascolator only with the blisters; the engine side is Section II | none |  |
| f22.panel-wiring | 1 | none | **none** | none: PUSH gives about 30 h for a much larger glass-panel system, not this one | none |  |
| f22.microswitches | 1 | none | **none** | none | none |  |
| f22.battery-shelf | 1 | part | 10.0 community | SPOD "battery cover" x 2 (cover only; the shelf is not timed), so low | battery-rg25xc 1 (estimate, was official; downgraded 2026-10-20, plans pages not read: one 12 V 25 Ah battery, plans-1980:p150 via config) | AS RG-25XC is 24 Ah against the plans 25 Ah; shelf and cover glass need battery dimensions, not printed |
| f22.firewall-terminals | 1 | none | **none** | none | none |  |
| f22.wing-wiring | 1 | none | 1.2 community | SPOD "nav/strobe light install" only, so low | none |  |
| f22.antennas | 1 | none | 6.2 community | SPOD winglet antenna planning and install (comm only; the canard nav strips are not timed) | copper-foil-tape 7.183 (derived: nav 2 x 22.8 + comm 2 x 20.3 in (one winglet) / 12) | one comm antenna assumed; toroids, balums, coax not priced |
| f23.engine-install | 1 | none | **none** | none: Section II work is not held | none |  |
| f23.carb-bracket | 1 | none | **none** | none: SPOD fitted a throttle body, logged with linkages | none | 2024-T3 0.063 plate and angle not bought here (angle length unprinted) |
| f23.cowl-trim | 1 | part | 11.4 community | SPOD upper 4.0 + lower 7.4 cowl trimming; a Cozy cowl, not a trimmed VariEze cowl | cowl-variez 1 (derived: one cowl set) | cowl part and vendor not found; reinforcing-band length not printed |
| f23.cowl-closeout | 1 | part | 8.0 community | SPOD "cowling trailing edge flange" x 4; the wing flange is not separable | none | fastener count conflict 40 printed vs 32 counted; fastener type not printed |
| f23.root-rib | 1 | none | 3.5 community | SPOD wing-root heat shields 1.5 + 2.0 | al-6061-0-020-20x24 2 (estimate: one 20 x 24 sheet per wing root (assumed 2)) | one sheet per wing root is my assumption; 6061-0 sheet not found at AS |
| f24.aft-cover | 1 | part | **none** | none | 1 ply inside + 1 outside on 18 x 20 (ply count is a conflict; the transcription says 1 + 2) -> urethane-foam-2x24x48 0.312 (estimate: 18 x 20 / (24 x 48)); bid-7725 0.579 (estimate: 720.0 in2 x 1.1 / 1368); mgs-lr285-gal 0.024 (estimate: cloth 0.152 kg -> mix 1:1); mgs-h287s-qt 0.049 (estimate: 100:40 split) | inside/outside ply count is a conflict (1+1 used); dish area and laps ignored |
| f24.console-lc1 | 1 | part | 4.0 est | SPOD 2019 left armrest entries 24.2 split by piece count, LC1 1 of 6 pieces | 1 + 2 plies on 72.8 in2 + 1/2 in floor lap x 8 -> foam-pvc-0p35-32x48 0.047 (estimate: 9.1 x 8 / 1536); bid-7725 0.179 (estimate: 222.4 in2 x 1.1 / 1368); mgs-lr285-gal 0.007 (estimate: cloth 0.047 kg -> mix 1:1); mgs-h287s-qt 0.015 (estimate: 100:40 split) |  |
| f24.consoles-left | 1 | part | 20.2 est | the other 5/6 of the 24.2 (Cozy armrests stand in for LC2 to LC6) | 2 plies on LC2 + LC5 tops, 1 ply on LC3 + LC4 sides -> foam-pvc-0p35-32x48 0.201 (estimate: LC2 71.9 + LC3 96.5 (rect) + LC4 106.5 + LC5 34.6 = 309.4 / 1536; LC6 base not printed); bid-7725 0.334 (estimate: 415.9 in2 x 1.1 / 1368); mgs-lr285-gal 0.014 (estimate: cloth 0.088 kg -> mix 1:1); mgs-h287s-qt 0.028 (estimate: 100:40 split) | LC3 taken as its bounding rectangle; LC6 base not printed |
| f24.thigh-support | 1 | part | 11.8 community | SPOD front thigh support entries 2018 and 2020 | ribs 1 ply one face 78.8 + floor 3 plies x 183.9 -> foam-pvc-0p35-32x48 0.171 (estimate: ribs 2 x 10.8 x 3.65 + floor 17 x 12.3 - 5.6 x 4.5 = 262.7 / 1536); bid-7725 0.507 (estimate: 630.5 in2 x 1.1 / 1368); mgs-lr285-gal 0.021 (estimate: cloth 0.133 kg -> mix 1:1); mgs-h287s-qt 0.043 (estimate: 100:40 split) | rib curve on an unheld sheet, so the ribs are rectangles (upper bound); aluminium cover 6.6 x 5.0 x 0.025 not bought |
| f24.canard-cover | 1 | part | 4.0 est | four man-hour ceiling (`estimate`, was `official`; downgraded 2026-10-20, page not read: plans-1980:p161 through the graph). A ceiling, not a log | none | block size not printed, so no foam or glass buy |
| f24.gap-seal | 1 | part | 10.4 community | SPOD "wing/centerspar seal" x 10 | none |  |
| f25.inspect-repair | 1 | part | **none** | none: SPOD has 1.3 h of one elevator repair, too thin to stand for the op | none |  |
| f25.coarse-fill | 1 | part | 339.7 est | SPOD CH25 entries labelled fill, sand, fair or finishing (89 entries), less those mixed with NACA ducts, brakes or gear fairings. Whole Cozy airframe, bigger than a Long-EZ | none | micro quantity not printed |
| f25.feather-fill | 1 | part | 42.0 est | SPOD epoxy-wipe entries 42.0 (he used epoxy wipes in place of feather fill) | none |  |
| f25.primer | 1 | none | **none** | none: SPOD logs no primer step | none | primer (Dupont 131S per the bulletin) and paint not priced |
| f25.paint-seals | 1 | none | 27.7 est | SPOD paint entries 17.7 + interior paint 10.0 | none |  |
| f26.cushions-headrests | 1 | none | **none** | none: PUSH bought commercial cushions | foam-rubber-2in 8.604 (estimate: front 46 x 16.5 + rear 12 x 16 + back 18 x 16 = 1239 in2 / 144; headrests left out) | foam rubber and cover fabric not found |
| f26.suitcases | 1 | part | **none** | none | none |  |
| r30.templates-cores | 1 | none | 18.3 est | GLANTZ ch10 55 h, less his own figures (7 bottom, 8 top, 1 inserts) = 39 h, split by SPOD CH10 weights: templates/cores 26.6, shear web 17.5, jig 12.7 (x 39/56.8) | none |  |
| r30.lift-tabs | 1 | none | **none** | none: SPOD logs 1.1 h "fit attach tabs" and seems to have bought them; no log times making them | none |  |
| r30.shear-web | 1 | part | 12.0 est | 17.5 x 39/56.8 | none |  |
| r30.jig-assemble | 1 | part | 8.7 est | 12.7 x 39/56.8 | none |  |
| r30.bottom-spar-cap | **2**: holding UNI tape while threads are pulled (GLANTZ) | part | 4.0 community | GLANTZ: about 4 h for the cap layup, setup included | none |  |
| r30.bottom-skin | **2**: full-span wet skin (GLANTZ: could not do it solo) | part | 3.0 est | GLANTZ: cap and skin a 7+ h layup, less the 4 h cap = 3 | planform 141.6 x 13.02 = 1843.6 in2 (GU planform, conflict; Roncz unconfirmed); 2 UND + 1 BID -> und-7715 2.965 (estimate: 3687.3 in2 x 1.1 / 1368); bid-7725 1.482 (estimate: 1843.6 in2 x 1.1 / 1368); mgs-lr285-gal 0.158 (estimate: cloth 1.011 kg -> mix 1:1); mgs-h287s-qt 0.323 (estimate: 100:40 split); peel-ply-582c 0.026 (estimate: 2 in TE strip x 141.6 / 10800) | planform is the GU 141.6 x 13.02 (conflict, Roncz unconfirmed) and includes the elevator chord, so it reads high; spar-cap UND tape and shear-web plies not quantified |
| r30.turnover-twist-check | 1 | none | 2.5 community | PUSH: about 2.5 h aligning with straightedges, string and laser before the top layups | none |  |
| r30.hinge-foam | 1 | part | 1.0 community | GLANTZ: about an hour to set all 7 inserts (pocket cutting may be outside it) | none |  |
| r30.top-spar-cap | **2**: holding UNI tape while threads are pulled (GLANTZ) | part | 4.6 est | GLANTZ: cap and skin 8 h with a helper, split by his bottom ratio 4/7 | none |  |
| r30.top-skin | **2**: full-span wet skin (GLANTZ: would not do it solo) | part | 3.4 est | the other 3/7 of 8 | same planform; 3 UND + 1 BID -> und-7715 4.447 (estimate: 5530.9 in2 x 1.1 / 1368); bid-7725 1.482 (estimate: 1843.6 in2 x 1.1 / 1368); mgs-lr285-gal 0.207 (estimate: cloth 1.322 kg -> mix 1:1); mgs-h287s-qt 0.422 (estimate: 100:40 split) | as bottom skin |
| r30.elev-nc2-inserts | 1 | part | 2.2 est | SPOD CH11 "assembling elevator hardware" pool 10.9 split evenly over 5 hardware ops | none |  |
| r30.elev-bond-cores | 1 | part | 3.9 community | SPOD "fitting elevator cores to torque tubes" | none |  |
| r30.elev-skin-bottom | 1 | part | 3.3 community | SPOD bottom-skin prep 1.8 + layup 1.5 | none |  |
| r30.elev-skin-top | 1 | part | 8.0 community | SPOD top-skin prep 3.6 + layup 4.4 | none |  |
| r30.elev-trim-ends | 1 | part | 2.7 community | SPOD "trimming elevator top skin" only; NC-6 plugs and end ply not timed, so low | none |  |
| r30.elev-hinges | 1 | none | 2.2 est | hardware pool share | none |  |
| r30.elev-hinge-slots | 1 | none | 2.2 est | SPOD "mounting elevators on canard" pool 6.5 split over 3 ops | none |  |
| r30.elev-uptravel-test | 1 | none | 2.2 est | mounting pool share | none |  |
| r30.elev-flox-hinges | 1 | part | 2.2 est | mounting pool share | none |  |
| r30.elev-nc12a | 1 | none | 2.2 est | hardware pool share | none |  |
| r30.elev-balance-check | 1 | none | **none** | none (inspection) | none |  |
| r30.elev-travel-check | 1 | none | **none** | none (inspection) | none |  |
| r30.canard-tips | 1 | part | 12.5 community | SPOD "canard tips" x 10; 5.3 h shared with counterweights left out | none |  |
| r30.elev-trim-belcrank | 1 | none | 2.2 est | hardware pool share | none |  |
| r30.elev-mass-balance | 1 | part | 1.4 community | SPOD "elevator counterweights", one entry; shared entries left out, so low | none |  |
| r30.elev-balance-pockets | 1 | part | **none** | none | none |  |
| r30.elev-ice-shield | 1 | part | **none** | none (optional step) | none |  |
| r30.elev-cs11 | 1 | none | 2.2 est | hardware pool share | none |  |
| r30.install-pins | 1 | none | 1.2 community | SPOD "preparing canard locating pins" | none |  |
| r30.align-canard | 1 | part | 7.6 community | SPOD aligning 2.9 + rear tabs 4.7 | none |  |
| r30.f22-drill-tabs | 1 | none | **none** | none | none |  |
| r30.elev-fuselage-clearance | 1 | none | 2.0 community | SPOD "fitting elevators", one entry | none |  |
| r30.lift-tab-bushings | 1 | none | **none** | none | none |  |
| r30.f28-pins-permanent | 1 | part | **none** | none: SPOD only logs fixing the pins (a redo) | none |  |
Buddy steps: 7 (`f21.close-tank`, `f21.outside-bottom`, `f21.outside-top`, `r30.bottom-spar-cap`,
`r30.bottom-skin`, `r30.top-spar-cap`, `r30.top-skin`). The close-tank helpers come from the op
summary itself. The other six come from GLANTZ posts where he says he could not, or would not, work
alone, or where the airframe had to be turned. I treated the following as convenience, not required,
as P1 did: GLANTZ's helper at the outlet-tube hole (`f21.od-outlet`), his parents at the strake ribs,
and a helper at the winglet A/B/C measurement.

## 5. New catalog items (not in prices.yaml)

Read 2026-10-18. Flags use the Contract 3 vocabulary.

| id | label | vendor | part | URL | price | unit | flag |
|---|---|---|---|---|---|---|---|
| foam-pvc-0p35-32x48 | H45 PVC foam 3/8 in, 32 × 48 (plans: 0.35 in type 45) | Aircraft Spruce | 01-12400 | https://www.aircraftspruce.com/catalog/cmpages/divinycellfoam.php | 53.75 | each (sheet) | page. 3/8 is the nearest stock to 0.35; GLANTZ used it |
| tube-5052-0375-6ft | 5052-O aluminium tube 3/8 × 0.035, 6 ft | Aircraft Spruce | 03-39500-6 | https://www.aircraftspruce.com/catalog/pnpages/03-39500-6.php | 15.24 | each (6 ft) | page. A search snippet of the catalog table showed $27.50; the page shows $15.24 |
| piano-hinge-ms20257p2-3ft | piano hinge MS20257P2, 3 ft (in the AS Long-EZ misc kit) | Aircraft Spruce | 03-00048-3 | https://aircraftspruce.com/catalog/kitspages/longez.php | 39.50 | each (3 ft) | page (kit component list). That it is the rudder hinge is unverified |
| battery-rg25xc | Concorde RG-25XC, 12 V 24 Ah | Aircraft Spruce | 11-03880 | https://www.aircraftspruce.com/catalog/pnpages/11-03880.php | 436.00 | each | page. 24 Ah against the plans' 25 Ah; nearest found |
| urethane-foam-2x24x48 | urethane foam 2 × 24 × 48, 2 lb/ft³ | Aircraft Spruce | 01-11900 | https://www.aircraftspruce.com/catalog/pnpages/01-11900.php | 51.75 | each (sheet) | page |
| nutplate-rudder-hinge | nutplate for the rudder hinge screws (type not printed) | | | | null | each | unsourced. AS kit lists MS21047L3 at $1.90; the size match is not shown |
| pop-rivet-flush | flush pop rivet for the rudder hinge (type not printed) | | | | null | each | unsourced |
| fuel-cap-dzus-2in | Dzus fuel cap with 2 in aluminium rim | not found | | | null | each | unsourced. The Usher UD-3 (2 in opening, AS 05-01061) is a different cap style |
| copper-foil-tape | copper foil tape for the nav and comm antennas | | | | null | ft | unsourced |
| cowl-variez | VariEze/Long-EZ cowl set | not found | | | null | each | unsourced |
| al-6061-0-020-20x24 | aluminium sheet 6061-0, 0.020 in, 20 × 24 | not found | | | null | each | unsourced |
| foam-rubber-2in | 2 in foam rubber for cushions | | | | null | sqft | unsourced |

Mentioned but not given an id (no printed quantity): fuel-proof epoxy (resin file, section 3);
1/4 in aluminium vent tube; aluminium screen mesh; 1 in aluminium drain plate and 1/8-27 NPT tap;
2024-T3 0.063 plate and 0.025 sheet; worm clamp; toroids, balums and coax; Camloc-type cowl
fasteners; Dupont 131S primer and finish paint; white silicone; cushion fabric and snaps; ABS sheet
for the suitcases; Roncz hardware (NC-2, NC-3, NC-12A, CS-10, CS-11). The AS Long-EZ hardware kit
01-00900 is listed at $370.24 on the kits page and $684.05 on its own page (search snippet, not
opened). Unresolved.

## 6. Open gaps (what would clear them)

- A Long-EZ log with chapter 20 to 26 times: GLANTZ's time page is the obvious candidate if it is ever updated. Until then the strakes, cowl,
  consoles and finishing hours are Cozy proxies. The owner's actuals (Contract 20a) are the real fix.
- Ply widths and outlines on full-size sheets the owner does not hold: winglet corner plies, layups
  2, 6 and 7, R45/OD, block A, cowl bands, the canard cover, the battery size.
- The Roncz canard planform: the skins use the GU 141.6 × 13.02 planform (conflict) and include the
  elevator chord, so they read high. Elevator skins, spar caps and shear web are not quantified.
- 20 ops have no hours: f21.vent-screen, f21.plumbing, f22.panel-wiring, f22.microswitches,
  f22.firewall-terminals, f23.engine-install, f23.carb-bracket, f24.aft-cover, f25.inspect-repair,
  f25.primer, f26.cushions-headrests, f26.suitcases, r30.lift-tabs, r30.elev-balance-check,
  r30.elev-travel-check, r30.elev-balance-pockets, r30.elev-ice-shield, r30.f22-drill-tabs,
  r30.lift-tab-bushings, r30.f28-pins-permanent.
