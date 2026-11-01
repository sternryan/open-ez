# Rehearsal sourcing, P1 (chapters 4 and 5, 17 ops)

Research only. Read 2026-10-17. No repo file was changed. The values file is `p1-plan-values.yaml`
in this directory. This record holds the evidence, the arithmetic and the gaps for it.

Plans text: I did not read the plans pages, because the scan is private. Step content comes from the
repo's own summaries in `guide/graph/ch04.yaml` and `ch05.yaml`, and dimensions from
`config/aircraft_config.py` (book-cited) or the fitted model in `core/fuselage_book.py`.

## 1. Sources used

| key | what | URL | used for |
|---|---|---|---|
| GLANTZ-T | Long-EZ build blog, time and budget page | https://www.aryjglantz.com/2013/11/time-and-budget-tracking.html | ch3 9 h, **ch4 33 h** (2/25 to 3/13/2013), **ch5 41 h** (3/15 to 4/14/2013), ch6 60 h |
| GLANTZ-SIDE | same blog, left side inside glassing | https://www.aryjglantz.com/2013/03/fuselage-wall-left-side-inside-glassing.html | one side's two UND plies took about 3 h with a friend mixing resin; "half a quart of resin"; lower longeron nailed and floxed alone |
| GLANTZ-PREP | same blog, side walls prep | https://www.aryjglantz.com/2013/03/fuselage-side-walls-prep.html | blank joined alone with a tape hinge; 0.8 in H45 foam; router dish |
| GLANTZ-FS | same blog, front seat | https://www.aryjglantz.com/2013/03/front-seat_13.html | knife trim after 4 h; "24 hrs for a full cure" |
| GLANTZ-RS, -IP, -F28, -F22 | same blog, rear seat / panel / F28 / F22 posts | https://www.aryjglantz.com/2013/03/rear-seat.html, .../instrument-panel.html, .../f28-bulkhead.html, .../f22.html | method, foam (H45 0.8, H250 1/4), all done alone |
| GLANTZ-MLG | same blog, main gear attachments | https://www.aryjglantz.com/2013/07/main-landing-gear-attachments.html | gear brackets fitted in ch6, not ch5, so they are not in his 41 h |
| PUSH-5 | Long-EZ N916WP log, chapter 5 | https://www.longezpush.com/chapter-5-fuselage/ | 9 May 2011: right side inside UNI layup "about 8 hours from initial prep to final peel ply"; peel ply on sides and gear pad |
| PUSH-4 | same log, chapter 4 | https://www.longezpush.com/chapter-4-bulkheads | no hours; front seat peel plied; firewall front face peel ply |
| SPOD | Cozy MKIV log (mykitlog, Spodman), CH04 per-entry hours | http://www.mykitlog.com/users/category.php?user=Spodman&project=2369&category=9910 | per-part weights to split the Long-EZ ch4 total (the log totals 64 h over 36 entries) |
| BOM | builder BOM by chapter, Google Sheets "BOM master.xlsx", author not named | https://docs.google.com/spreadsheets/d/0B8ljui4BNLG8Z2NibkF1dEVwM0k/edit | foam blanks, ply blank, longeron stock, AN509 count, LMGA count |
| AS-* | Aircraft Spruce product pages | listed in section 5 | cloth weights, prices |
| TDS | MGS L285 TDS, registry `mgs-l285-tds` | https://www.aircraftspruce.com/catalog/pdf/mgs285tech.pdf | resin section 3 |

Other logs checked and found to give no usable hours: https://www.deford.com/cozy/chap_04.html and
chap_05.html (Cozy; ch4 bulkheads all glassed in about a week, with a father-in-law helping cut
foam), http://www.n451bx.com/bulkheads.html (Cozy; "about eight months", chapter-time fields
blank), https://blog.familjenjonsson.org/blog/long-ez-build-log/ (no ch4/5 entries).

## 2. Hours method (every hours value is `estimate`)

I found no public log that gives hours for one of these exact steps. The best Long-EZ figure is
GLANTZ-T's chapter totals, so I split those totals per op. These are one builder's hours (first
person; the page does not say whether helper time is counted).

**Chapter 4, 33 h, split with SPOD per-part weights.** SPOD is a Cozy, which has different parts,
so these weights are a proxy. SPOD entries mapped to each Long-EZ group (I excluded the entries
marked as redos, and the Cozy-only panel stiffeners; shared entries are split 50/50):

| Long-EZ group | SPOD entries (h) | weight | × 33/48.15 | op split (SPOD face ratio) |
|---|---|---|---|---|
| front seat | seatback: 2.15 + 2.2 + 1.85 | 6.2 | 4.25 | front 2.15/6.2 → **1.5**; back → **2.8** |
| rear seat | MLG bulkheads: 2.3 + 2.0 + 0.7 + 1.0 + 1.0 (weak analog) | 7.0 | 4.80 | no analog for the hole work, so 50/50 → **2.4 / 2.4** |
| panel, F22, F28 | panel 15.1 + F22 7.25 + F28 5.5 | 27.85 | 19.09 | aft faces 4.3 h vs forward faces 9.3 h in SPOD → aft **6.0**, fwd **13.1** |
| firewall | ply prep 2.0 + glass aft 1.0 + layup/trim front 2.1 + hard points 2.0 | 7.1 | 4.87 | aft 3.0/7.1 → **2.1**; fwd **2.8** |
| total | | 48.15 | 33.0 | sum of ops 33.1 (rounding) |

**Chapter 5, 41 h.** GLANTZ-MLG shows the gear brackets were done in ch6, and GLANTZ's ch5 posts
say that cutouts wait for later chapters. So the 41 h covers 7 ops, and `f05.spar-cutout` and
`f05.gear-extrusions` get **no hours**. `f05.inside-layup` = 2 sides × 5.5 h (the midpoint of the
two one-side figures: 3 h GLANTZ-SIDE, 8 h PUSH-5) = **11.0**. The remaining 30 h is split evenly
over the other six ops, **5.0** each. That even split is the weakest number in this file. I do not
know whether GLANTZ's 41 h includes the gear pad.

## 3. Resin: MGS L285 / H287 TDS (registry `mgs-l285-tds`, page_basis pdf)

I fetched the file from the registry's `obtain` location (8 PDF pages, title `L285_eng_200106`,
Hexion, January 2006; sha256 `ddc93387…be7a`). Pages below are PDF pages, with the sheet's printed
page number in brackets.

- **Minimum application temperature: 10 °C.** Processing is stated as 10 to 50 °C (50 to 122 °F),
  `mgs-l285-tds:p1` [1.1-10]. The optimum is 20 to 40 °C, `p4` [1.1-13].
- **Work-again (green/handling) time against temperature: NOT GIVEN.** The TDS has no table or curve
  of time until a laminate can be worked again. What it does give:
  - After an initial room-temperature cure, parts are "workable and demouldable", with no time and
    no temperature stated: `p2` [1.1-11].
  - The test samples got 24 h at room temperature before heat treatment: `p6` [1.1-15]. That is a
    sample-preparation schedule, not a work-again time.
  - Gel time, 1 mm film, with hardener 287: about 5 to 6 h at 20 to 25 °C, and about 80 to 120 min
    at 40 to 45 °C, `p4` [1.1-13]. (285: 2 to 3 h / 45 to 60 min; 286: 3 to 4 h / 60 to 90 min.)
    This is the only temperature-dependent cure-time data. **Gel time is not work-again time.** Per
    the plan's rule, do not use it as `gate_hours`.
  - Pot life is about 45 min to 4 h across the hardeners, `p1`. A rise of 10 °C halves pot life,
    `p4`. This is not work-again time either.
  - Post-cure: 50 to 55 °C for glider standards, 80 °C for motor planes, `p2`. Mechanical-data cure:
    24 h at 23 °C + 15 h at 60 °C (`p7` [1.1-16]) or + 15 h at 80 °C (`p8` [1.1-17]). This is not
    work-again time.
  - Mix ratio: 100:40 by weight, 100:50 by volume, `p4`. Density: resin 1.18 to 1.23, hardener 287
    0.93 to 0.96 g/cm³, `p3` [1.1-12].
  - The sheet's own contents table puts gel time on printed page 14, but it is actually on 1.1-13.
- Community, not TDS: GLANTZ-FS knife-trimmed BID 4 h after layup and waited 24 h for a full cure
  (no temperature given). This could fill a separate community-flagged field, but not the TDS curve.
- **Suggested `data/resins/mgs-285-287.yaml` content (Contract 3):** `min_temp_c: 10`,
  `source: mgs-l285-tds:p1`, `gate_hours: []` (empty: not in the TDS), `flag: unsourced` for the
  curve. Note that `Resin` has a single flag. `min_temp_c` is sourced while the curve is not, so the
  integrator must decide how one flag carries both. I did not resolve that.

## 4. Per-op findings

Arithmetic constants, used by every buy:
- 38 in roll: 1368 in² per linear yd.
- AS-cloth weights: UND 7 oz/yd², BID 8.8 oz/yd², so 0.2095 and 0.2633 kg per linear yd.
- The 1.1 overlap/trim factor is my assumption.
- Resin to cloth is about 1:1 by weight. That is the coupon PO's assumption, and it checks against
  GLANTZ-SIDE: one side computes to 0.69 kg mixed, about 0.6 qt, and he reports half a quart.
- Split 100:40 (TDS p4), using the TDS p3 density midpoints: LR285 4.561 kg/gal, H287 0.894 kg/qt.
- Net quantities; no scrap.

Not quantified anywhere:
- **Micro and flox.** No dimensions exist, so they are not in `buy`. They are listed as catalog
  items. Resin for slurry and flox is not in the resin figures, which therefore read low on every
  op that slurries foam.
- **Peel ply.** It appears only where a community log shows it. The unit is the PO's 5 yd × 60 in
  pack (60 in × 5 yd = 10800 in²).

| op | people | cure | hours | buys (arithmetic) | unsourced / notes |
|---|---|---|---|---|---|
| f04.front-seat-bkhd-front | 1 | part | 1.5 est | foam 28.3×23/144 = 4.52 sq ft; UND 2×650.9×1.1 = 1432 in² → 1.05 yd; 0.219 kg cloth → 0.034 gal / 0.070 qt; peel ply 716 in² / 10800 = 0.066 pack (PUSH-4 peel plied) | taper-end overlap is inside the 1.1 factor |
| f04.front-seat-bkhd-back | 1 | part | 2.8 est | BID 1×(650.9 + 102.6 edge wrap at 1 in)×1.1 = 829 in² → 0.61 yd → 0.025 gal / 0.051 qt | flox corner (GLANTZ-FS), qty unsourced; the wrap width is my assumption |
| f04.rear-seat-bkhd-foam | 1 | part | 2.4 est | foam 20.6×16.1/144 = 2.30 sq ft (rectangular blank); UND 2×316.4 (trapezoid)×1.1 → 0.51 yd → 0.017 gal / 0.034 qt | |
| f04.rear-seat-bkhd-hole | 1 | part | 2.4 est | BID 2×(316.4 + π×8×0.8 scoop wall)×1.1 → 0.54 yd → 0.022 gal / 0.046 qt | |
| f04.panel-f22-f28-aft | 1 | part | 6.0 est | thin foam = fitted model faces (panel 343 + F22 455.5 + F28 92 = 890.5 in²) → 6.18 sq ft; BID 2×890.5×1.1 → 1.43 yd → 0.059 gal / 0.121 qt | the outlines are fitted, not book; F28 is modelled as a top band only, so it reads low. BOM blanks (2 × 24.8×27.75 = 1376 in²) are an upper bound. Doubler plies and the leg-cutout ply have no area: excluded |
| f04.panel-f22-f28-fwd | 1 | part | 13.1 est | BID 2×890.5×1.1 → 1.43 yd → 0.059 gal / 0.121 qt | the extra upper-panel ply and the F22 pads (5 UND + 4 BID each side) have no printed area in the repo: excluded, so the cloth and resin read low. GLANTZ-F22 did the pads alone |
| f04.firewall-aft | 1 | part | 2.1 est | ply: BOM blank 24×30 / (48×48 sheet) = 0.31 sheet; BID 1×307.6 (fitted face)×1.1 → 0.25 yd → 0.010 gal / 0.021 qt | the fitted face (307.6 in²) is well under the BOM blank (720 in²); outline on template A4, not held |
| f04.firewall-fwd | 1 | part | 2.8 est | AN509-10R10 ×6 (`estimate`: count in the op's completion text, cited to plans-1980:p35 through the graph; I did not read the page; BOM also lists 6); BID 0.25 yd → 0.010 gal / 0.021 qt; peel ply 338/10800 = 0.031 pack (PUSH-4) | AN509 price unsourced |
| f05.side-blank | 1 (GLANTZ-PREP, alone) | part (micro joint) | 5.0 est | foam 2 blanks × 103×21/144 = 30.04 sq ft (BOM: 32 sq ft) | micro qty unsourced |
| f05.side-profile | 1 | none | 5.0 est | none | |
| f05.side-layout | 1 | none | 5.0 est | none | release tape: qty and price unsourced |
| f05.inside-layup | **2**: one mixes, one wets out (GLANTZ-SIDE) | part | 11.0 est | UND 2 sides × 2 plies × 2044.9 in² (trapezoid sum on `side_panel_heights`) × 1.1 → 6.58 yd → 1.378 kg → 0.216 gal / 0.440 qt; spruce 3 pcs × 104 in (BOM; two longerons + LWX/LWY) = 26 ft; peel ply 2×2044.9×1.1/10800 = 0.42 pack (PUSH-5) | stiffener stock size unsourced (GLANTZ says 0.4 in thick per plans); flox unsourced |
| f05.top-longeron-glass | 1 | part | 5.0 est | none quantified | strip widths for the 3 UND and the full-length BID ply are not in the repo, so the cloth is unsourced |
| f05.lower-longeron | 1 (GLANTZ-SIDE, alone) | part (flox) | 5.0 est | triangular spruce 2 × 104 in / 12 = 17.3 ft (assumed to match the top-longeron stock length) | doubler and urethane-block sizes unsourced; nails unsourced; the 3/4 in triangle size is a proposal, not read from plans |
| f05.gear-pad | 1 | part | 5.0 est | none quantified | the hatched-area and stack dimensions are on p38, not in the repo; PUSH-5 describes a 6-ply base and two 15-ply pads but gives no size |
| f05.spar-cutout | 1 | none | **none** | none | no log times this step |
| f05.gear-extrusions | 1 (GLANTZ-MLG, alone) | none | **none** | LMGA 2 (`derived`: one tube per side × 2; BOM lists 2); extrusions 4 (`derived`: two per side × 2) | bolts: 16 holes, but the bolt count is not derivable from the summary, so left out; AN363 nuts per CP29 LPC67, count unsourced; prices unsourced (BOM: LMGA from CG Products) |

Buddy steps: 1 (`f05.inside-layup`). DeFord's father-in-law helped cut ch4 foam, but I treat that
as convenience, not a second person the step requires. Builders report every other step done solo.

## 5. New catalog items (not in the coupon PO)

Read 2026-10-17 unless noted. Flags use the Contract 3 vocabulary.

| id | label | vendor | part | URL | price | unit | flag |
|---|---|---|---|---|---|---|---|
| foam-pvc-0p8 | PVC foam, 0.8 in thick (BOM: R45/H45) | none found at 0.8 in | | https://www.aircraftspruce.com/catalog/cmpages/divinycellfoam.php | null | sqft | unsourced. The nearest stock size is H45 3/4 in × 32×48, 01-12700, $91.85 (page). The repo's plans word is "thick blue foam"; whether 3/4 H45 is acceptable is a builder call, not made here |
| foam-pvc-0p2 | high-density PVC foam, 0.2 to 1/4 in (BOM: R250; GLANTZ: H250 1/4) | none found | | | null | sqft | unsourced. AS lists no H250 |
| birch-ply-6mm-48x48 | Finnish birch plywood 6 mm, 48×48 (a component of the AS Long-EZ wood kit) | Aircraft Spruce | 02-20800 | https://www.aircraftspruce.com/catalog/pnpages/02-20800.php | 138.90 | each | page. Alternate: 1/4 in birch/poplar 5-ply 2×4, 02-27140, $335.00 (page) |
| spruce-capstrip-075x1 | spruce capstrip 3/4 × 1 in (the AS Long-EZ wood kit lists 26 ft) | Aircraft Spruce | 02-341 | https://www.aircraftspruce.com/catalog/pnpages/02-341.php | 4.35 | ft | page. BOM says 0.7×1 in longeron stock |
| spruce-triangle-075 | triangular corner blocking, 3/4 in (in the AS Long-EZ wood kit, 21.5 ft) | Aircraft Spruce | 02-18200 | https://www.aircraftspruce.com/catalog/pnpages/02-18200.php | 3.25 | ft | page. Size match to the lower longeron unverified |
| an509-10r10 | AN509-10R10 flat-head screw | not found | | | null | each | unsourced |
| lmga-assembly | main gear attach tube assembly (BOM: from CG Products) | | | | null | each | unsourced |
| main-gear-extrusion | main gear attach extrusion | | | | null | each | unsourced |
| flox-cotton-1lb | flocked cotton fiber, 1 lb | Aircraft Spruce | 01-14800 | https://www.aircraftspruce.com/catalog/pnpages/01-14800.php | 4.85 | each | page |
| micro-bubbles-1lb | 3M glass bubbles, 1 lb | Aircraft Spruce | 01-14600 | https://www.aircraftspruce.com/catalog/pnpages/01-14600.php | 13.25 | each | page |
| urethane-foam-1x24x48 | urethane foam 1×24×48 (for the small block in f05.lower-longeron; qty unsourced, so it is not in buy) | Aircraft Spruce | 01-11500 | https://www.aircraftspruce.com/catalog/pnpages/01-11500.php | 25.60 | each (sheet) | page |
| release-tape | release tape for bond areas | | | | null | roll | unsourced |

Checks on existing PO ids (no change proposed):
- The AS pages still show BID 7725 01-00642 at $10.50/yd and UND 7715 01-00641 at $12.55/yd on
  2026-10-17, the same as the PO's 2026-10-08 read.
- `peel-ply-582c` is a 5 yd pack in the PO, so the qty in `p1-plan-values.yaml` is in packs. If the
  catalog unit is set to yd instead, multiply by 5.

## 6. Open gaps (what would clear them)

- Per-step hours: someone's own timed log of these steps. The owner's actuals (Contract 20a) are
  the real fix.
- Panel, F22, F28, firewall and gear-pad areas, and the strip widths: need the p34, p35 and p37/p38
  dimensions and the full-size templates, or Contract 18 geometry where layup solids exist.
- Work-again time against temperature: not in this TDS edition. A newer Hexion/Westlake LR285 sheet
  might state demould times. I did not find one. A search snippet of R&G's L285 pages (https://www.r-g.de/en/art/110100,
  not opened) gives 24 h at room temperature, then 15 h at 55 °C, which is a cure schedule, not a
  work-again time.
