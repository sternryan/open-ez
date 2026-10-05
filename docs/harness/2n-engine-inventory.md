# Engine source inventory and whole-engine values (crew R, round 2)

Date: 2026-10-05. Research only; no code edited. Grades: A = manufacturer or FAA (a maker's claim read on a retailer page is marked A-vendor), B = designer, RAF or newsletter, C = builder site, forum or marketplace.
Paraphrases are 10 words or fewer. No CAD file was downloaded or stored. Public URLs only.

Scope: the O-235 C-series the book allows (plans-1980:p156), with the O-200 noted. Round-1 values are in `2n-engine-research.md`; this file confirms them and adds the component level.

## 1. Short answer

- **Whole engine is well sourced** (section 3): dry weight, CG from the prop flange, and the accessory set the CG includes.
- **Components are almost not sourced.** No public document gives a crankcase, crankshaft, cylinder, sump or accessory-housing weight. The overhaul manual and the illustrated parts catalogue (IPC) carry no part weights. What exists: accessory weights from makers and newsletters, the mount weight, and a stripped-engine weight that bounds the accessory total.
- **No dimensioned installation drawing is public.** Lycoming's Operator's Manual Section 7 drawings carry connection labels only (section 4).
- **No open-licensed CAD model of an O-235 was found** (section 5).

## 2. Component inventory

Position datum for engine-internal values is the prop flange front face (Lycoming's TCDS datum). Station values are published FS.

| Component | Weight | Position or dimension | Source (id, page or figure) | Context, 10 words | Grade |
|---|---|---|---|---|---|
| Whole engine | 246 lb (C1/C2A), 243 (C1C/H2C) | CG 14.75 in from flange face | tcds-e223 p7 NOTE 8 | dry weight and CG table by dash number | A |
| Whole engine, average | 242 lb (C1), 243 (C1C) | none | lyc-om-o235 p2-6 "Detail Weights" | average standard engine by model | A |
| Bore, stroke, displacement | none | 4.375 x 3.875 in, 233 cu in | tcds-e223 p1; lyc-om-o235 Section 1 table | cylinder size, model data | A |
| Crankcase | NOT FOUND | two aluminium castings split on the engine centreline | lyc-om-o235 Section 1 | construction text only | A |
| Cylinders and heads | NOT FOUND (per cylinder) | four, horizontally opposed; no. 1 front right, no. 2 front left, 3 rear right, 4 rear left; no pitch printed | lyc-om-o235 Section 1; ipc PC-302 Fig 10, 12, 13 | numbering and part list, no dimensions | A |
| Crankshaft and prop flange | NOT FOUND | flange front face is the CG datum; SAE Type 1 or Type 2 flange by dash number | tcds-e223 p1 and p7 | flange type per model | A |
| Accessory housing | NOT FOUND | rear of crankcase, top rear of sump | lyc-om-o235 Section 1; ipc Fig 17, 18 | housing for oil pump and drives | A |
| Oil sump | NOT FOUND (oil 6 qt, 4 usable, not in dry weight) | carb mounting pad and suction screen on its underside; oil station FS 140 on the Long-EZ | tcds-e223 p1; lyc-om-o235 p7-3 Fig 7-1; om-1980:p25 | sump contents and Long-EZ oil station | A |
| Starter (standard) | about 17 lb, derived | at the accessory end, station 150+ on the Long-EZ | cp-text CP49 p4; CP27 p4 | lightweight starter 10.2 lb is 6.5 to 7 lb lighter | B |
| Starter, B&C lightweight | 10.2 lb | same pad | cp-text CP49 p4 | 1986 maker claim relayed by RAF | B |
| Starter, Sky-Tec 149-12LS | 7.8 lb | same pad | https://www.aircraftspruce.com/catalog/pnpages/07-06246.php | product page weight line | A-vendor |
| Alternator or generator | 4.25 to 4.75 lb (B&C small), 7 lb (Pelican 35 A), 9 lb (Pelican 55 A), 6.1 lb (B&C L-40) | belt-driven, aft end, station 150+ | cp-text CP26 p11, CP49 p4; https://www.aircraftspruce.com/catalog/eppages/L40alt.php | belt alternators for the O-235 | B and A-vendor |
| Alternator kit, 35 A | 9.3 lb | none | cp-text CP34 p10 | kit weight for the Lycoming | B |
| Magnetos (two) | 3.75 lb each (Slick 4300 series); 6.25 lb typical older style | at the rear, upper left and right of the housing | https://www.aircraftspruce.com/catalog/pnpages/08-43720.php | maker's weight claim against old magnetos | A-vendor |
| Magneto types by model | none | C1 TCM S4LN-21/-20; C1C and C2C Slick 4251/4250 | tcds-e223 p7 NOTE 8 | ignition column by dash number | A |
| Carburettor | NOT FOUND | Marvel-Schebler MA-3A or MA-3SPA on the sump bottom pad | lyc-om-o235 Section 1; maker pages list no weight | model and mounting location only | A |
| Fuel pump (plunger, standard) | NOT FOUND | rear pad, left side | tcds-e223 p4 NOTE 4; lyc-om-o235 Fig 7-1 | standard drive on C-series | A |
| Vacuum pump pad, tach drive | NOT FOUND | rear, top | tcds-e223 p4; Fig 7-1 | optional drives | A |
| Accessory total | about 31 lb, derived | none | cp-text CP10 p9 (242 normal, 211 stripped to mags and carb) | normal less stripped O-235 weight | B |
| Exhaust (Long-EZ 4-pipe) | NOT FOUND | none | https://www.aircraftspruce.com/catalog/eppages/longezehaust.php | product page lists no weight | A-vendor |
| Baffles | NOT FOUND | cooling-air baffles around cylinders | lyc-om-o235 Section 1; ipc Fig 13 | cooling description only | A |
| Cowl | 18 lb glass, 12 lb graphite | none | cp-text CP27 p5 | standard Lycoming Long-EZ cowl, both halves | B |
| Dynafocal mount | 5.19 lb (5 lb 3 oz) | mount cups top at FS 134.2 (one builder) | cp-text CP26 p3; https://www.longezpush.com/chapter-23-engine-mount-install/ | welded Brock mount weight; builder cup station | B and C |
| Mount rubber travel | none | engine moves up to 0.34 in vertical at the CG | cp-text CP54 p6 | Lord mount limits, quoted by a builder | B |
| Prop extension | none | 3 in recommended | cp-text CP28 p8 | extension included in hub station | B |
| Prop hub forward face | none | FS 158.8, WL 21.83 | cp-text CP28 p8 | Long-EZ prop position | B |
| Down thrust | none | about 2 deg | cp-text CP38 p5 | prop flange higher than magneto end | B |
| Electrical set on the airplane | 68.5 lb | starter, ring gear, 60 A alternator, battery, wiring | cp-text CP27 p4 | ladder step 4 delta, includes a 19 lb battery | B |
| Small alternator add | 4.9 lb | none | cp-text CP27 p4 | ladder step 2 with regulator | B |

Part catalogue structure (usable as a component list, no weights): IPC PC-302-L2A/-L2C, https://www.lycoming.com/sites/default/files/attachments/O-235-L2A%2526%2520-L2C%2520Parts%2520Catalog%2520PC-302-L2A-L2C_0.pdf, Figures 4 to 30 cover crankcase, crankshaft, connecting rods and pistons, cylinders, valves, intake pipes, oil sump, accessory housing, pumps, carburettor, magnetos, alternator, starter. Grade A. It covers the L2A/L2C dynafocal models, not the C-series.

## 3. Whole-engine values for the book engine (confirmed)

| Quantity | Value | Datum or accessory set | Source | Grade |
|---|---|---|---|---|
| Dry weight, C1 and C2A | 246 lb | standard set | tcds-e223 p7 NOTE 8 | A |
| Dry weight, C1C and H2C (Slick) | 243 lb | standard set | tcds-e223 p7; lyc-om-o235 p2-6 | A |
| Dry weight, dynafocal models L2C and N2C | 249 lb | standard set | tcds-e223 p7 | A |
| Dry weight, C-series spread | 236 to 247 lb | | tcds-e223 p7 | A |
| CG longitudinal | 14.75 in from prop flange front face, toward the crankcase | C-series and F, H2C, J, K, L, N; 14.51 for E, G, M, P | tcds-e223 p7 | A |
| CG vertical | 1.13 in below shaft centreline | same grouping; 1.17 for E, G, M, P | tcds-e223 p7 | A |
| CG lateral | 0.20 in left of shaft centreline | same grouping; 0.15 for E, G, M, P | tcds-e223 p7 | A |
| Set the CG includes | "including starter and generator" | table heading | tcds-e223 p7 | A |
| Standard drives, C-series | starter, generator, plunger fuel pump, tachometer standard; vacuum pump optional | | tcds-e223 p4 NOTE 4 | A |
| Newsletter CG cross-check | about 15 in aft of prop flange | | cp-text CP54 p6 | B |
| O-200 dry weight and CG | 190 lb; CG 4.6 in forward of rear face of mounting lugs, 1.2 in below crankshaft CL | "with accessories" | tcds-e252 p1 | A |

What the weight does not state: whether carburettor and exhaust are in the 243 or 246 figure. The accessory table in the TCDS says generators and fuel pumps are not integral to the type design. The stripped-engine newsletter figure (211 lb) implies about 31 lb of removable accessories, a derived bound, not a breakdown.

Conflicts and flags:
1. TCDS dry weight (246 lb for C1) differs from the OM average (242) by 4 lb. Both are real; they are different statistics.
2. The config `engine_displacement_ci` of 235 differs from the TCDS and OM displacement of 233 cu in for the C-series (the model name is 235). Flag for the config provenance.
3. Mount type: the C-series (C1, C1B, C1C, C2x) are conical-mount engines; the dynafocal ones are H2C, J2A/B, L2A/C, M, N and P (tcds-e223 p5 to p6 model notes, and the Lycoming ratings table SSP-110-3, https://www.lycoming.com/sites/default/files/file/2025-07/SSP-110-3%20Certified%20Engines.pdf). The Long-EZ dynafocal mount (CP26, CP27) fits the dynafocal group. TCDS CG is identical (14.75 in) for H2C, J, L and N, so the arm does not change; the dry weight does (H2C 243, J 252, L2C and N2C 249). The ledger's 243 equals the H2C figure, so it is consistent with a dynafocal engine; C1C is the conical equivalent.
4. N26MS's basic empty weight excludes the starter and alternator (CP27 p4), so a TCDS dry weight that includes them double-counts against any airplane figure that lacks them. The closure row already notes this.

### Installation drawing

Lycoming Operator's Manual 60297-9 Figures 7-1 to 7-3 (https://www.lycoming.com/sites/default/files/file/2025-02/60297-9%20-%20O-235%20and%20O-290%20Series.pdf, pp 7-3 and 7-4, 5th edition; the 4th edition at https://yankee-aviation.com/docs/Lycoming%20O-235%20Owners.pdf has the same drawings at 7-5 and 7-6) show side and rear views with connection labels (starter, vacuum pad, carb pad, oil screen, fuel pump). They carry no dimensions. The 4th-edition rear view marks a target symbol near the crankshaft centreline that looks like a CG mark. It has no dimension, so it is not a source (AGENTS: never measure an undimensioned image). Lycoming's dimensioned installation drawing, and the mount pad dimensions (Service Supply drawings), were not found public.

## 4. Where the geometry would have to come from, and did not

| Needed for geometry | Public? |
|---|---|
| Overall length, crankcase length, front face to mount plane | No |
| Cylinder pitch (axial spacing of the four cylinders), bank offset | No |
| Mount pad positions on the crankcase (conical and dynafocal) | No |
| Dynafocal ring diameter, rubber mount spacing, focal angle | Dynafocal I is 18 degrees (forum, grade C; not a Long-EZ drawing); nothing else |
| Section IIL pp 14 to 15 (Long-EZ standoff from firewall to mount pads) | Not held (named in CP40 p6) |
| Prop flange diameter, bolt circle (SAE AS-127 Type 1 or 2) | Standard exists; not retrieved |

## 5. CAD models and licences

| Item | URL | Author | Licence | Reuse |
|---|---|---|---|---|
| Aero Engine Lycoming O-320 (marketplace listing) | https://www.turbosquid.com/3d-models/aero-engine-lycoming-o-320-old-3d-model-1987015 | not recorded (page not read) | royalty-free marketplace licence, as listed in the search result | FORBIDDEN: marketplace licences bar redistributing the source file |
| Lycoming IO-360 / accessory plate (marketplace listing) | https://www.cgtrader.com/3d-models/aircraft/aircraft-part/accessory-plate-lycoming-io-390 | not recorded | royalty-free marketplace licence | FORBIDDEN: same |
| Lycoming 360 special STL | https://www.cgtrader.com/3d-models/aircraft/helicopter/lycoming-360-special-stl | not recorded | royalty-free marketplace licence | FORBIDDEN: same |
| Lycoming O-360 Cessna 172 engine STL | https://cults3d.com/en/3d-models/gadget/lycoming-o-360-cessna-172-engine | not recorded | not read; Cults listings are usually personal-use | FORBIDDEN until the licence is read |
| GrabCAD, Thingiverse, Onshape public, Printables | searched | none found for an O-235 | not applicable | no model to reuse |
| OpenVSP Hangar | searched | no Lycoming, Long-EZ or VariEze model found | not applicable | none |

None is an O-235, none carries an open licence I could see, and none is usable as a source for dimensions: a mesh of an unknown engine measured by eye breaks the AGENTS rule on undimensioned images. Recommendation: use none. If one is later found under CC0 or CC-BY, record author and licence here and use it for layout proportions only, flagged `representational`.

## 6. Coverage gaps

| Component | Weight known? | Position known? | Best source | Gap |
|---|---|---|---|---|
| Whole engine | Yes (A) | CG yes (A) | tcds-e223 p7 | carb and exhaust inclusion unstated |
| Crankcase | No | Only that it is two castings | lyc-om-o235 Section 1 | no weight, no dimensions |
| Cylinders and heads, each | No | Numbering only | lyc-om-o235 Section 1; ipc Fig 10 | no weight, no pitch |
| Crankshaft and prop flange | No | Flange face is the datum | tcds-e223 p7 | no weight; flange dimensions not fetched |
| Accessory housing | No | Rear of crankcase | lyc-om-o235 Section 1 | none |
| Oil sump | No (oil 6 qt) | Oil station FS 140 (om-1980:p25) | om-1980:p25 | sump size |
| Starter | Yes, about 17 lb (B), 7.8 to 10.2 lb light types | Station 150+ (B) | cp-text CP49 p4, CP27 p4 | exact standard-starter weight; which one the TCDS includes |
| Alternator or generator | Yes, 4.25 to 9 lb by type | Station 150+ | cp-text CP26 p11, CP49 p4 | which type the TCDS includes |
| Magnetos | Yes, 3.75 lb Slick, 6.25 lb old | Rear, upper | Slick catalogue page | per dash number |
| Carburettor | No | Sump bottom pad | lyc-om-o235 Section 1 | weight |
| Fuel pump | No | Rear pad | tcds-e223 p4 | weight |
| Exhaust | No | none | vendor page | weight and routing |
| Baffles | No | around cylinders | OM text | weight and shape |
| Mount pads, dynafocal ring | Mount 5.19 lb (B) | Top cups FS 134.2 (C) | cp-text CP26 p3 | pad positions, ring geometry, Section IIL |
