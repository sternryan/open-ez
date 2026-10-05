# 2n engine research (crew R) for the Block 2 mass-ledger closure

Date: 2026-10-04. Research only. Grades: A = manufacturer or FAA, B = designer/RAF/newsletter, C = builder site or forum.
Rules honoured: no Long-EZ engine arm computed here; the captain's target values are not used. Raw datums and directions only.

## 0. Which engine models does the book allow (held text)

- plans-1980 p156 (m28-research-c.md): "Continental O-200 and Lycoming O-235, any dash number". om-1980 p5 says both approved.
- **No O-320 appears in the held Long-EZ text as an approved Long-EZ engine.** The only O-320 hits in m28-research-c.md are none for the Long-EZ; the O-320 shows up only in public CP text as a larger-engine flight example (CP29 p2, a Long-EZ with an O-320 flown in a record attempt; CP10 p9 says Lycoming O-290/O-320/O-340/O-360 are "out of the question" for the VariEze). Treat O-320 as non-book. Data for it is given in section 2 only so the ledger can price the option.
- Correction to the task brief: **E-286 is the O-360 sheet, not the O-320.** The O-320 sheet is **E-274**. (Verified by reading both PDFs.)
- Book-allowed O-200 (Continental, TCDS E-252) is also given, since plans p156 allows it.

## 1. (a) Dry weight, with accessory configuration

### 1.1 O-235 TCDS E-223 (grade A)

Source: FAA TCDS E-223, Revision 22, 31 Jan 2020. URL: https://cdn.piperforum.com/attach/31/31224-O-235-TCSD-E-223-Rev22.pdf (hosted copy of the FAA sheet; FAA canonical landing is the DRS entry https://drs.faa.gov/browse/excelExternalWindow/C7BF8C45A9443A6686256E4D005E73C3.0001, which would not render for me). Page 7 of 7, NOTE 8 table "Ignition, C.G. and Weights". Heading of the table: C.G. location "(dry) including starter and generator"; column "Weight (dry) lb".

| Model | Magnetos (per table) | Weight (dry), lb |
|---|---|---|
| O-235-C1, -C2A | TCM S4LN-21/-20 | 246 |
| O-235-C1A | TCM SF4LN | 236 |
| O-235-C1B | TCM S4LN-200/-204 | 245 |
| O-235-C1C, -H2C | Slick 4251/4250 | 243 |
| O-235-C2B | TCM S4LN-1227/-1209 | 247 |
| O-235-C2C | Slick 4251/4250 | 244 |
| O-235-E1B, -F1B, -L2C/-N2C | various | 249 |
| O-235-L2A, -N2A, -K2A, -J2A | TCM | 252 |
| O-235-M1, -P1, -P2A | TCM | 255 |

Accessory configuration behind the figure: the sheet does not itemize it. NOTE 4 (p4-5) lists the "Standard" drives for the C-series: starter, generator, plunger fuel pump, tachometer drive; vacuum pump and alternator are optional. NOTE 3 says generators, fuel pumps etc. are not integral engine accessories. Reading: the dry weight is a standard engine with starter and generator drive-side accessories and dual magnetos; carburetor and exhaust are not itemized. Unconfirmed: whether the carburetor is in the figure (the sheet is silent). Flag this as the main ambiguity.

### 1.2 O-235 Operator's Manual 60297-9 (grade A)

URL: https://www.lycoming.com/sites/default/files/file/2025-02/60297-9%20-%20O-235%20and%20O-290%20Series.pdf (5th edition). Section 2, "Detail Weights", p2-6: "Standard engine (average)", lb.

| Model | lb |
|---|---|
| O-235-C | 240 |
| O-235-C1B | 241 |
| O-235-C1, -C2A | 242 |
| O-235-C1C, -C2B, -H2C | 243 |
| O-235-C2C | 244 |
| O-235-E1B, -F1B, -N2C | 249 |
| O-235-L2C, -K2C | 248 |

Conflict: the OM "average standard engine" figure (242 for C1) differs from the TCDS dry weight (246 for C1) by 4 lb; for C1C both give 243. The OM and TCDS do not state the accessory list for the average figure. Treat the TCDS as the certified maximum-style dry value and the OM as the average.

**Finding for the ledger:** `engine_dry_weight_lb` 243 matches **O-235-C1C / C2B(OM) / H2C** in both E-223 (C1C = 243) and the OM detail weights, so it is not an orphan number: it is the Slick-magneto C1C/H2C dry weight. It just is not on a Long-EZ page.

### 1.3 Newsletter engine weights (grade B)

All from the public Canard Pusher text compilation, URL http://www.cozybuilders.org/Canard_Pusher/CPs_1_to_82_Sections.txt (cp-text).

| Value | Where | Context |
|---|---|---|
| 242 lb | CP10 p9 | "normally equipped" O-235; too heavy structurally (VariEze text) |
| 211 lb | CP10 p9 | O-235 stripped to mags and carburetor only |
| 210 to 215 lb | CP14 p4 | stripped O-235 weight for VariEze |
| 195 lb | CP14 p4 | O-200 less electrical system |
| 215 lb | CP20 p2 | max engine and accessory weight (VariEze); 240 lb vibrating mass |
| 242 lb | VariViggen newsletter VVN6 area (cp-text line ~1918) | Lycoming-listed O-235 dry weight; O-320 273, IO-320 292, O-360 285 |
| 15 lb | CP18 p3 | O-235 weighs about 15 lb more than a similar O-200 |

### 1.4 O-200 TCDS E-252 (grade A, book-allowed)

URL: https://cessna120140.com/wp-content/uploads/2019/06/Type-Certificate-Data-Sheet-E-252.pdf (FAA sheet, Rev 29, 15 Sep 1982), p1. Models columns: C90-8F | C90-12F/-14F/-16F | O-200-A/-B/-C ("---" = same as preceding). Weight (dry): 184 | 188 | 190 lb. So the O-200 family is 190 lb. "C.G. location (with accessories)": see 2.2.

### 1.5 O-320 TCDS E-274 (grade A, non-book option)

URL: https://data.ntsb.gov/Docket/Document/docBLOB?ID=40381291&FileExtension=.PDF&FileName=Engine+Type+Certificate+Data+Sheet+for+Lycoming+O-320-E2D-Master.PDF (FAA E-274 Rev 21), NOTE 9. Weight (dry): O-320-A1A/A1B/A2A/A2B/A3A/A3B 244 lb; -A2D 249; -A2C/A3C 243; -B series 249-250; -E1A/E2A 244; -E1B/E2B 243; -E2D/E2G 249; -D series 251-256. The sheet lists magnetos only; accessories not itemized. The ledger "O-320 option" at 243 to 250 is a plausible dry weight of a 150 hp -A/-E class engine; not book.

## 2. (b) Engine CG and its datum

### 2.1 O-235 (grade A)

E-223 Rev 22 p7 NOTE 8 (URL in 1.1). Datum: **propeller flange front face** (Lycoming datum). Value for the C-series (C1, C1A, C1B, C1C, C2A/B/C, F, H2C, J, K, L, N): **14.75 in** from the prop flange front face (toward the engine body, i.e. rearward on a tractor installation). Below prop shaft centerline: **1.13 in**. Off shaft CL: **0.20 in left**. For -E1/-E2/-G/-M/-P: 14.51 in, 1.17 below, 0.15 left. The table says the CG is "(dry) including starter and generator".

Direction caveat for the captain: Lycoming's "from the flange front face" runs toward the crankcase, which on a Long-EZ pusher points **forward** (toward the firewall). I have not turned this into a station.

### 2.2 O-200 (grade A)

E-252 Rev 29 p1: "C.G. location (with accessories)": **4.6 in forward of the rear face of the mounting lugs** (O-200 column by the "---" convention; C90-8F is 6.2, C90-12F/-14F/-16F is 4.6), and **1.2 in below crankshaft centerline** for the O-200 column (C90-8F 1.5, -12F 1.3). Datum here is the **rear face of the engine mounting lugs**, a datum that ties directly to a mount pad plane without needing engine length. Column-mapping caveat: the O-200 column prints only the vertical value (1.2); the fore/aft value for O-200 is the "---" dash and inherits 4.6 from the C90-12F column to its left. Confirm against the sheet scan before use.

### 2.3 O-320 (grade A, non-book)

E-274 Rev 21 p2 (URL in 1.5): C.G. (dry) **from face of propeller mounting flange**: 14.25 in (A, C-series), 14.57 (B?), 14.25, 14.25, 14.70 in for the column groups; 0.97 below (and 0.71, 0.79 for the column variants) shaft CL. The sheet gives column groupings without a clean model key in the extract; read the scan for the -A/-E/-C exact mapping.

### 2.4 Newsletter cross-check (grade B)

CP54 p6, a Long-EZ Squadron builder (Dick Kreidel) quoting Lord Manufacturing: engine CG "about 15 in aft of the crankshaft prop flange" for the Lycoming O-235 on dynafocal mounts. URL: http://www.cozybuilders.org/Canard_Pusher/CPs_1_to_82_Sections.txt. Agrees with E-223's 14.75 within rounding. Same datum (prop flange); no mount-pad datum is given by anyone for the O-235.

## 3. (c) Geometry to tie the datum to the firewall

### Found

| Value | Source | Grade | Note |
|---|---|---|---|
| Forward face of prop hub at **FS 158.8 in**, **WL 21.83**, "includes the recommended 3 in prop extension" | CP28 p8, "Long-EZ - Prop Position" (cp-text URL above) | B | The only RAF-published absolute Long-EZ prop station. Hub forward face, not engine flange face: the 3 in extension is in the figure. Unconfirmed: whether the hub forward face meets the extension aft face with zero crush-plate thickness. |
| Prop extension, recommended **3 in** long | same CP28 p8 | B | |
| Dynafocal-era engine was moved **aft** with the new mount, cowl moved aft 0.7 in (old 32.0, new 32.7) | CP27 p5 | B | Qualitative; no engine-move number given. Section IIL holds the numbers and is not in the corpus. |
| Top engine mount cups at **FS 134.2** | longezpush.com Chapter 23 build log, https://www.longezpush.com/chapter-23-engine-mount-install/ | C | Builder site, N916WP. Mount cup station, not the pad face. |
| Mount pad stations are shown on the plans' engine-mount drawing only | CP footnote in the Long-EZ errata (cp-text, plans change list) | B | |
| Dynafocal mount weight **5 lb 3 oz** (welded Brock mount) | CP26 p3, Mike Melvill part list (cp-text) | B | |
| Crankshaft CL angle about 2 deg down-thrust, on BL 0 | CP38 p5 | B | affects a CG vertical offset only |

### NOT found

- Dynafocal mount standoff (firewall to mount pad face) in inches, for any source. It is in Section IIL pages 14-15 per CP40 p6, not held.
- O-235 overall length, mounting-pad plane to prop flange distance, or crankcase front-face to flange distance. Not in the TCDS, the Operator's Manual (Figures 7-1 to 7-3 are annotated drawings without dimensions, pp 7-3, 7-4), or SSP-110-3 (https://www.lycoming.com/sites/default/files/file/2025-07/SSP-110-3%20Certified%20Engines.pdf has ratings only). The Lycoming installation drawing with dimensions is not in public view; Lycoming sells it by drawing number.
- Any datum relation between the Lycoming flange datum and the Long-EZ mount pads other than via the CP28 prop station (above).

## 4. (d) Published Long-EZ W&B data with an engine or powerplant arm

**Not found.** Checked:

- CP archive text (cozybuilders.org), searched for engine arm/station/moment/CG phrases: no Long-EZ engine arm anywhere.
- iflyez.com Long-EZ W&B page and downloadable spreadsheet (https://iflyez.com/LongEZ_Weight_and_Balance.shtml, http://iflyez.com/LongEZ_Weight_and_Balance.xls), grade C: the sheet takes scale readings against main gear FS 110.5, nose gear FS 19.5, canard FS 18.6, wing root FS 113.9, wing tip FS 156.0 (reference stations only). It has a single "adjustment to W&B i.e. engine change" row and **no engine arm**.
- Pilot's Operating Handbook scan from iflyez (https://iflyez.com/DOWNLOAD/PilotOperatingHandbook.PDF): image-only PDF; text extraction found no engine arm.
- canardzone.com threads (403 on fetch; search snippets only): no arm.
- pilotsofamerica.com thread 85612: discussion only, no numbers.
- Canard Pusher issue 43 (https://ez.canardaircraft.com/www.ez.org/t/cpc-043.html): Defiant data only.

Aft CG limit change FS 104 to 103 (iflyez, grade C; matches the OM LPC 116 in the held text).

## 5. (e) Published Long-EZ empty-weight breakdown by component

Partial, from the prototype build (CP26 p3, Mike Melvill, cp-text; grade B; weights of parts N26MS/N79 era, pre-finish):

| Item | lb |
|---|---|
| Fuselage complete with centersection, gear, no strakes/canard/canopy/engine mount | 183 |
| Wing complete with winglets and rudder | 64 |
| Canard, no hardware, no elevators | 17 |
| Canopy complete | 16 |
| Main gear with attach tabs | 27 |
| Centersection spar | 29.3 |
| Dynafocal engine mount | 5.2 |
| Standard Lycoming Long-EZ cowl, glass | 18 (CP27 p5) |
| 35 A alternator kit | 9.3 (CP34 p10) |

Empty weights of built aircraft (grade B, CP34 p4): 800 lb (O-235, strobes, nav, landing light, large alternator, no starter); 811 lb (standard alternator, vacuum, upholstery). CP18 p3: all surveyed Lycoming EZs were over 650 lb (VariEze fleet). A full per-component builder breakdown that includes the engine, and the OM's own weight table, are not published in anything I could reach.

## 6. Conflicts and uncertainties

1. O-235 dry weight: 242 (OM average and VariViggen newsletter) vs 246 (TCDS C1) vs 243 (C1C), 211 (stripped). The ledger's 243 equals the C1C / H2C figure; the book's 246 limit ("with accessories") equals the TCDS C1 figure. Plans p156 246 lb likely is the TCDS-class number.
2. TCDS says the CG includes starter and generator; whether the weight figure includes carburetor and exhaust is unstated. Newsletter "stripped = mags and carb only" gives 211, implying roughly 31 to 35 lb of removable accessories (starter, generator, fuel pump, vacuum, plumbing); this is an inference, not a published breakdown.
3. CP54 "about 15 in" vs TCDS 14.75: consistent, same datum.
4. Prop hub forward face FS 158.8 is a CP28 dynafocal-era figure; CP27 says the dynafocal engine sits farther aft than the older conical position. If the held plans (conical drawing) disagree, the CP value is later and the plans are older.
5. The task brief's "E-286 for O-320" is wrong: E-286 is the O-360/HO-360 sheet.

## 7. Proposed registry entries

| id | title | edition | obtain URL | page_basis |
|---|---|---|---|---|
| tcds-e223 | FAA Type Certificate Data Sheet E-223, Lycoming O-233/O-235 | Revision 22, 31 Jan 2020 | https://cdn.piperforum.com/attach/31/31224-O-235-TCSD-E-223-Rev22.pdf (FAA DRS entry: https://drs.faa.gov/browse/excelExternalWindow/C7BF8C45A9443A6686256E4D005E73C3.0001) | printed ("Page 7 of 7", NOTE 8) |
| lyc-om-o235 | Lycoming Operator's Manual, O-235 and O-290 Series, P/N 60297-9 | 5th edition | https://www.lycoming.com/sites/default/files/file/2025-02/60297-9%20-%20O-235%20and%20O-290%20Series.pdf | printed (section-page, e.g. 2-6 detail weights, 7-3 install drawings) |
| tcds-e252 | FAA Type Certificate Data Sheet E-252, Continental C90 / O-200 | Revision 29, 15 Sep 1982 | https://cessna120140.com/wp-content/uploads/2019/06/Type-Certificate-Data-Sheet-E-252.pdf | printed (page 1) |
| tcds-e274 | FAA Type Certificate Data Sheet E-274, Lycoming O-320 | Revision 21 | https://data.ntsb.gov/Docket/Document/docBLOB?ID=40381291&FileExtension=.PDF&FileName=Engine+Type+Certificate+Data+Sheet+for+Lycoming+O-320-E2D-Master.PDF | printed (page 2 C.G., NOTE 9) |
| cp-text (existing) | Canard Pusher text; new uses CP28 p8 (prop position), CP54 p6 (engine CG), CP26 p3 (part weights), CP10 p9 (engine weights) | existing | http://www.cozybuilders.org/Canard_Pusher/CPs_1_to_82_Sections.txt | issue (existing) |
| iflyez-wb | iflyez.com Long-EZ weight and balance page and spreadsheet (builder, reference stations only; no engine arm) | 2007 spreadsheet | https://iflyez.com/LongEZ_Weight_and_Balance.shtml | not paged (grade C) |

## 8. Best values

| Quantity | Value | Grade | Source | Caveat |
|---|---|---|---|---|
| Book engine models | O-200 and O-235 (any dash); no O-320 | book | plans-1980 p156 | |
| O-235 dry weight, standard C-series (C1/C2A) | 246 lb | A | tcds-e223 p7 NOTE 8 | accessories: standard starter+generator drives, carb/exhaust unstated |
| O-235 dry weight, C1C/C2B/H2C (Slick) | 243 lb | A | tcds-e223 p7; lyc-om-o235 p2-6 | equals ledger 243 |
| O-235 average standard (C1) | 242 lb | A | lyc-om-o235 p2-6 | average vs TCDS 246 |
| O-235 stripped (mags + carb only) | 211 lb | B | CP10 p9 | |
| O-200 dry weight | 190 lb | A | tcds-e252 p1 | with accessories per sheet |
| O-235 engine CG, longitudinal | 14.75 in from prop flange front face, toward the crankcase (C-series); 14.51 in for E/G/M/P | A | tcds-e223 p7 | direction on a pusher points forward |
| O-235 engine CG, vertical | 1.13 in below shaft CL (C); 1.17 (E/G/M/P) | A | tcds-e223 p7 | |
| O-235 engine CG, lateral | 0.20 in left of shaft CL (C); 0.15 | A | tcds-e223 p7 | |
| Newsletter CG cross-check | about 15 in aft of prop flange | B | CP54 p6 | |
| O-200 CG | 4.6 in forward of rear face of mounting lugs; 1.2 in below crankshaft CL | A | tcds-e252 p1 | column mapping to confirm |
| Long-EZ prop hub forward face | FS 158.8, WL 21.83, includes 3 in extension | B | CP28 p8 | dynafocal-era; hub vs flange offset unconfirmed |
| Dynafocal mount weight | 5.2 lb | B | CP26 p3 | |
| Dynafocal standoff, O-235 length, mount-pad to flange distance | NOT FOUND | | | Section IIL pp 14-15 (not held) and Lycoming installation drawing |
| Long-EZ engine/powerplant arm or moment | NOT FOUND | | | |
| Long-EZ per-component empty weight incl. engine | NOT FOUND (airframe parts only) | | | |
