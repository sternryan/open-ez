# Engine installation (chapter 23, 23-1 to 23-3): source research (2026-10-04)

Read-only research pass for milestone 2.8, crew C. Values read on the page image (hand digits cropped and
enlarged 2x to 6x), not the OCR. 1980 plans cited `plans-1980:pNNN` (PDF page). Cobelu text (`cobelu`, ch23 md)
was diffed against the scan; scan wins. CP text cited `cp-text:CPnn p<page>` (+ LPC number), the page being the
one whose footer closes the passage. Owner's Manual cited `om-1980:p<printed>` (footer numbers sit at page
bottom). Paraphrases are ten words or fewer. Nothing in the repo was edited.

## 0. Read this first: chapter 23 is a three-page delta, not an engine installation

Chapter 23 does not contain an engine mount, a mount station, an engine weight, a prop-flange station or an
exhaust drawing. It says to build the engine installation from the VariEze Sections IIA (Continental) or IIC
(Lycoming), second editions, "with the exceptions shown in this chapter" (plans-1980:p156). The chapter's own
content is: engine choice, weight limits, six small corrections, a throttle/mixture bracket drawing, a
Continental starter-bearing keeper plug, the cowling trim-and-reinforce procedure, and the wing-root metal rib.

- The owner holds no Section II of any letter (cobelu holds only Section I and Section VI). Everything about the
  mount, baffles, exhaust, carb heat, prop extension and spinner lives in IIA, IIC, or the later IIL: all absent.
- CP27 p4 says IIC must NOT be used for a Long-EZ Lycoming; a new Section IIL replaced it (early 1981).
  CP37 p4 and CP38 p7 say IIL updates and supersedes Section I for everything aft of the firewall.
  So chapter 23 as printed (which cites IIA/IIC) was itself superseded by IIL for Lycoming builders.
- The exhaust drawings were promised on p158 ("will be supplied in CP 24") and are not on that page.
  CP25 p5 shows them (pages 7 and 8 of CP25), but the text transcription omits the drawings.
- Consequence for mass and CG: the book prints NO engine arm, NO mount arm, NO prop arm and NO engine weight.
  The only printed engine-side masses are limits (246 lb engine with accessories, 286 lb vibrating mass).
  The only printed engine-side arm is oil, FS 140.0 (om-1980:p25). See section 3 and section 6.

## 1. Page map (`plans-1980`, confirmed on printed footers)

| PDF | Printed | Content |
|---|---|---|
| p155 | 22-7 | last page of chapter 22 (electrical); not engine |
| p156 | 23-1 | General, engine selection, fuel, accessories and weight limits, throttle cables, instruments, exhaust, induction hose, baffles, Lycoming carb bracket drawing, Continental keeper plug drawings, start of cowl text |
| p157 | 23-2 | cowl: 9 in trim and 4-ply reinforcement, TE closeout jig and layups, screw counts, exhaust cutout gap, flange layup at wing, aluminum rib, 40 fasteners, turn-over note |
| p158 | 23-3 | "LAST PAGE": soft aluminum rib outline (6061-0, .020) and the note that exhaust drawings are not yet available |
| p159 | 24-1 | chapter 24 starts (confirmed by the footer and the chapter heading) |
| p010 | 2-5 | parts list: chapter 23 prefab and materials (end of chapter 2 BOM) |

The chapter is exactly 3 pages. The brief's "about p155 to p157" is off by one: it is p156 to p158.
Back cover (side view, plan view, FS/WL/BL callouts): plans-1980:p171.
OCR note: p158 text layer carries ghost bleed-through of a chapter 24 page; ignore it.

## 2. Dimensions, materials, plies

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Recommended engines | Continental O-200 and Lycoming O-235, any dash number | plans-1980:p156 | high, printed text | om-1980:p5 says both approved; OM p2 lists 100 hp and 115 hp | book |
| Higher-hp stripped engines | meet weight but "not recommended" (outside envelope) | plans-1980:p156 | high | om-1980:p5 says heavier/higher-hp not recommended | text |
| Max engine weight with accessories | 246 lb (VariEze 215) | plans-1980:p156 | high, read twice | CP20 p2 gives 215 for VariEze; cobelu 246 | book |
| Max "vibrating mass" (engine, accessories, exhaust, prop, extensions, oil) | 286 lb | plans-1980:p156 | high | CP20 p2 gives 240 for VariEze; 286-246 = 40 lb allowance, derived | book |
| Starter | approved; recommended against; adds weight | plans-1980:p156 | high | chapter 22 says "over 25 lb, most aft on the engine" (cobelu 22) | text |
| Heavy props / turbo | not recommended | plans-1980:p156 | high | om-1980:p5: wood fixed-pitch only | text |
| Fuel system | use chapter 21, not IIA/IIC fuel parts | plans-1980:p156 | high | cobelu 21 says supersedes | text |
| Throttle cables | ignore YT-3 bracket; tape to fuselage side, pot with silicone; no trough | plans-1980:p156 | high | | repr |
| Exhaust | Long-EZ-specific system (1979), fatigue-relief flanged joints, from Brock; drawing "page 23-3" | plans-1980:p156 | high | p158 says drawings not yet available, in CP24; CP25 p5 shows the system and says it is made by Brock | repr (no drawing held) |
| Induction hose | wire and cord safetying must be exact; cites IIC p13 and "IIC p17" | plans-1980:p156 | high | both cites read "IIC"; the second is likely IIA (p17); typo | text |
| Baffles | make 1 in oversize at cowl, trim to 1/4 in gap to cowl | plans-1980:p156 | medium: the "1/4" glyph is a small fraction; cobelu reads 1/4 | | repr |
| Lycoming carb bracket: plate | .063 2024-T3 aluminum | plans-1980:p156 (fig 23-1) | high | cobelu fig 23-1 | repr |
| bracket: view-from-below overall | 6.5 long, 2.5 wide | plans-1980:p156 | high | | repr |
| bracket: oil-drain hole | 2 in dia, centre 3.6 from the carb-hole centre | plans-1980:p156 | high (hand digits, 3x crop) | | repr |
| bracket: carb hole | 1.8 in dia (printed "1-8"), centre 1.25 from forward end | plans-1980:p156 | medium: 1.8 vs 1.6 on a hand "8" | | repr |
| bracket: upright angle | 2 x 2 formed aluminum angle, .063; 8 rivets AN470-4-5 (printed AN4?0-4-5) | plans-1980:p156 | medium (rivet prefix smudged) | | repr |
| bracket: side-view lengths | 8 overall top, 5 lower, 1.5 and 2.7 to the two cable clamps, 4 and 1 from aft view | plans-1980:p156 | high | | repr |
| bracket: cable-clamp holes | drill #22 | plans-1980:p156 | high | | text |
| bracket: aft tab strap | .063 x .6 aluminum strap to an oil-pan bolt | plans-1980:p156 | high | cobelu .063 x .6 | text |
| Throttle/mixture return springs | go to full open and full rich on cable failure; controls must work without them | plans-1980:p156 | high | CP27 p2 hint list (IIC page 27 bracket) | text |
| O-235 oil drain hole | location varies by dash number; check before cutting | plans-1980:p156 | high | CP25 p1 notes full-flow spin-on filter on L2C projects 1 in into the spar | text |
| Continental O-200-48 keeper plug | mandatory without a starter | plans-1980:p156 | high | CP24 p2 safety list also names the starter bearing plug | text |
| keeper plug: rod | 1/2 in dia 6061-T6, 3.15 long (printed "3-15") | plans-1980:p156 | high (digit crop) | cobelu 3.15 | repr |
| keeper plug: hole | 3/16 in "(#10 drill)" in text; drawing says "#12" | plans-1980:p156 | high both reads | see conflict C2 | repr |
| keeper plug: cover plate | 1/4 in plate; tap 10-32 in drill #21, 0.1 below the bolt-hole line, 2.5 each side | plans-1980:p156 | high | | repr |
| keeper plug: hardware | AN3-34A bolt, AN960-10 washers, MS21042-3 lock nut (text) | plans-1980:p156 | high | | text |
| Cowl: trim | about 9 in off each outboard end of the VariEze cowl | plans-1980:p157 | high | | repr (cowl moulds are prefab, shape not in book) |
| cowl end ribs | VariEze end ribs not used | plans-1980:p156-157 | high | | text |
| Cowl inside edge reinforcement | 4 plies BID at 45, 2 in wide, 4 places; band lies just inboard of the 9 in trim line | plans-1980:p157 | high for plies and width; medium for band position (dashed lines at 9 and 11 in) | cobelu says the same | derived band 9 to 11 in from the outboard end |
| Cowl TE closeout jig | cowl stood on trailing edge, TEs taped, front opened 8.5 in | plans-1980:p157 | high | | jig |
| TE closeout strips | 10 strips 45-degree BID, 4 x 15; 2 strips 3 x 15 | plans-1980:p157 | high | | text |
| TE closeout plies | 5-ply BID layup, then 1 ply BID lapping onto the top after popping the bottom half | plans-1980:p157 | high | section A-A shows 5 ply, 2 in wide | text |
| TE closeout width | 2 in as laid up; trim to 1.6 in | plans-1980:p157 | high | | repr |
| TE fasteners | 3 equally spaced per side | plans-1980:p157 | high | | text |
| TE tape release | shiny grey duct tape inside bottom TE; sand top TE dull; stiffener "supplied with cowl", 3 in dimension | plans-1980:p157 | medium for the "3 in" arrow | | repr |
| Forward screw spacing | 8 equally spaced along the top forward edge; 5 along each forward bottom side | plans-1980:p157 | high | | text |
| Wing-flange screws | 4 equally spaced per flange | plans-1980:p157 | high | | text |
| Total cowl fasteners | 40 | plans-1980:p157 | high | derived: 8 + 2x5 + 2x3 + 2x4 = 32, not 40 (see C4) | text |
| Exhaust gap | patch any gap over 1/4 in around exhaust exit; cut holes after install | plans-1980:p157 | high | | text |
| Wing flange layup | 5 plies BID at 45 on the wing flange, bottom first then top (aircraft inverted) | plans-1980:p157 | high | | text |
| flange outside ply | after removing cowl, 1 ply BID at 45 on the outside | plans-1980:p157 | high | | text |
| flange width callout | 1.2 (printed "1-2") | plans-1980:p157 | medium: decimal point is a mid-line dot | rib bend allowance on p158 also 1.2 | repr |
| Aluminum rib (text) | "0.20 6061-0" | plans-1980:p157 | high read | see conflict C1 | text |
| Aluminum rib (drawing, BOM) | .020 thick 6061-0; sheet 20 x 24 x .020 | plans-1980:p158, p010 | high | cobelu says 0.020 in BOM | book |
| rib features | edge offset .5; two 1.2 flanges (bend down, "bend up" on the aft edge); cutouts for rudder cable and aileron pushrod; held by cowl screws; butts to the spar at front | plans-1980:p158 | high for features; the outline is a hand drawing, no coordinates | A-sheet may exist | repr (shape only; no dimensions beyond .5 and 1.2) |
| Chapter 23 BOM | prefab CI cowl inlet, CCT/CCB or LCT/LCB cowl; glass 3 yd BID; epoxy 0.2 gal; metal 20 x 24 x .020 6061-0 | plans-1980:p010 (2-5) | high | cobelu matches | book |
| Prop max diameter (back cover) | 60 with a quote mark, "60 max dia" | plans-1980:p171 | medium (inch mark smudged) | om-1980:p5 table says 58 disc for both engines; CP42 p5 vendors list 62 for Long-EZ | repr |
| Firewall | FS 125 on the back cover | plans-1980:p171 | high | config fs_firewall 125 | book |
| Top-of-fuselage WL at the firewall | WL 32.8 | plans-1980:p171 | medium (hand digits, 3x crop) | not an engine item | derived context |
| Cowl lateral limit | cowl meets the wing at BL 23 (plan view label at the strake/cowl joint) | plans-1980:p171 | high | p126 prints BL 23 for the TE meeting the cowl (m27) | book |
| Nose station | FS -6.8 | plans-1980:p171 | medium (hand digit "8" vs "3") | om-1980:p3 length 201.4 | context |
| Aft-most station (vertical tail top) | FS 196.6 | plans-1980:p171 | medium | 196.6 + 6.8 = 203.4 against om-1980:p3 length 201.4 (2 in apart; see C6) | context |

## 3. Weights and stations (mass ledger inputs)

The book prints no engine, mount, prop, spinner or starter arm. Everything below is a builder or vendor weight
with no station, except where an arm is shown. Nothing here should be summed into the ledger as "book".

### 3a. Printed limits and arms

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Engine plus accessories, max | 246 lb | plans-1980:p156 | high | config `engine_dry_weight_lb` 243 | book (limit, not a weight) |
| Vibrating mass, max | 286 lb | plans-1980:p156 | high | derived allowance for prop, exhaust, extension, oil: 286 - 246 = 40 lb | derived |
| Oil weight and arm | 8 lb at FS 140.0 (moment 1120) | om-1980:p25 | high | ledger `oil` arm 140.0 | book |
| Fuel arm | 104.5 (26 gal per tank, strakes) | om-1980:p25-p26 | high | ledger fuel 104.5 | book |
| Empty aircraft sample | 730 lb at 111.7, moment 81541 | om-1980:p25, p35 | high | ledger row; OM p4 says "approximately 750 lb"; see C5 | book |
| Equipment list columns | "Engine", "Prop" rows blank: weight, arm, moment per item | om-1980:p65 | high | OM says use the plans back cover for FS | text |
| Starter, ring gear, alternator, brackets | "station 150+" (no exact value); needs nose ballast for light pilots | cp-text:CP27 p4 | medium (stated loosely) | oil at FS 140 is 15 in aft of the firewall | repr (use as lower bound only) |
| Engine CG relative to prop flange | about 15 in aft of the crankshaft prop flange | cp-text:CP54 p7 (builder letter citing Lord) | medium (builder letter) | prop flange FS not held | repr |
| Crankshaft attitude | on BL 0 in plan; 2 degrees down thrust, plus or minus 1 (prop flange higher than the magneto end) | cp-text:CP32 p5; cp-text:CP38 p5 | high (two CPs agree) | | book (CP) |
| Mount clearance to firewall | about .030 gap, but verify the mount is straight by station (Section IIL p14 conical, p15 dynafocal) | cp-text:CP32 p5 | high | IIL values not held | text |
| Cowl moved aft 0.7 in relative to VariEze; engine also moved aft with the dynafocal mount | 0.7 in | cp-text:CP27 p5 | high | CP27 p5 also gives cowl lip dimension 32.0 old, 32.7 new (sketch omitted) | repr |

### 3b. Builder and vendor weights (reference values, not ledger rows)

| Item | Weight | Cite | Conf | Note | Model use |
|---|---|---|---|---|---|
| Dynafocal engine mount (Brock weldment, N26MS) | 5 lb 3 oz = 5.19 lb | cp-text:CP26 p3 | high | the CP26 builder list; fuselage 183 lb excludes the mount | ref |
| Complete fuselage, no engine mount | 183 lb | cp-text:CP26 p3 | high | | ref (already in ledger) |
| Basic empty weight BEW, N26MS definition (conical mount and ram inlet, no starter or alternator, graphite cowl, VFR panel, small battery) | 693.4 lb | cp-text:CP27 p4 | high | no arm printed | ref |
| BEW plus small alternator | 698.3 lb (+4.9) | cp-text:CP27 p4 | high | derived 698.3 - 693.4 = 4.9, matches | ref |
| plus Com, Nav, transponder | 713.7 lb (+15.4) | cp-text:CP27 p4 | high | derived 713.7 - 698.3 = 15.4, matches | ref |
| BEW plus 60 A alternator, starter, ring gear, belt, brackets, relays, 25 AH battery | 761.9 lb (+68.5) | cp-text:CP27 p4 | high | derived 761.9 - 693.4 = 68.5, matches | ref |
| plus avionics | 777.3 lb (+15.4) | cp-text:CP27 p4 | high | derived 761.9 + 15.4 = 777.3 | ref |
| plus 500x5 tires, dynafocal mount, NACA inlet, lights, heat, etc. | 815.4 lb (+38.1) | cp-text:CP27 p4 | high | derived 777.3 + 38.1 = 815.4. The dynafocal mount's share is not split out | ref |
| plus light-pilot provisions (second battery, 15 lb lead; 44.8 lb) | 860.2 lb | cp-text:CP27 p4 | high | derived 815.4 + 44.8 = 860.2 | ref |
| plus 12 small extras (22.8 lb) | 883 lb | cp-text:CP27 p4 | high | derived 860.2 + 22.8 = 883.0 | ref |
| 25 AH battery in the nose | +19 lb (accept for light pilots) | cp-text:CP27 p4 | high | | ref |
| Standard Lycoming Long-EZ cowl (both halves) | 18 lb (glass) | cp-text:CP27 p5 | high | graphite 12 lb; Kevlar within 1 lb of graphite (cp-text:CP28 p10) | ref |
| Graphite cowl | 12 lb | cp-text:CP27 p5 | high | | ref |
| Small B&C alternator system | 4.25 to 4.75 lb | cp-text:CP26 p11 | high | CP27 p4 prices the small alternator at 4.9 with wiring and regulator | ref |
| B&C 8 A alternator | 3.8 lb | cp-text:CP34 p10 | high | | ref |
| 35 A alternator kit (Lycoming) | 9.3 lb | cp-text:CP34 p10 | high | | ref |
| Six-inch prop extension (versus 3 in) | +1.5 lb | cp-text:CP30 p5 | high | | ref |
| Normal 0-235 as delivered | 242 lb | cp-text (VariEze era, CP13 area, line near the Rutan "0-235 models" answer; not paged here) | low (page not confirmed) | stripped O-235 210 to 215 lb, cp-text:CP14 p4 | ref (not a ledger row) |
| Stripped engine weights quoted for VariEze | 195 lb (O-200 less electrics), 210-215 (stripped O-235) | cp-text:CP14 p4 | high | VariEze-era, before the 246 lb Long-EZ rule | ref |
| Built-airplane empty weights | 800 lb (strobes, nav, landing light, big alternator, no starter, O-235); 811 lb (standard alternator, vacuum, extra upholstery) | cp-text:CP34 p4 | high | context for the 750 lb OM figure | ref |

The ledger needs, for the engine group: engine with accessories (limit 246), mount (5.19 lb), prop, spinner,
exhaust, baffles, cowl (about 12 to 18 lb), oil (8 lb at 140), starter and alternator (CP27: 150+). Of these,
only oil has a printed arm. No prop weight, spinner weight or exhaust weight is printed in any held source.

## 4. Build-order steps (op candidates)

All of these depend on a Section II that is not held; the step names are mine. Prerequisites reference earlier
chapters. "Jig" marks a fixture.

| Op | Done (paraphrase) | Prerequisites | Jig/fixture |
|---|---|---|---|
| c23.select-engine | Choose O-200 or O-235 within weight limit | ch22 electrical choice (starter or none) | none |
| c23.mount-extrusions-clamp | Clamp mount to firewall extrusions while they cure | ch14/ch15 extrusions (CP27 p5, CP38 p7) | the welded mount itself |
| c23.mount-engine | Bolt engine to mount, set crank on BL 0, 2 deg down | mount fitted; firewall (ch15) | measure from firewall (IIL, not held) |
| c23.brake-cylinders-longer-bolt | Replace brake-arm bolt with longer one through mount | ch15 master cylinders | none |
| c23.throttle-cables | Tape cables to fuselage side; pot with silicone | ch16/ch24 console | tape |
| c23.carb-bracket | Make .063 bracket, gasket-style, two gaskets | O-235 fitted | drawing p156 |
| c23.keeper-plug | Make rod plug for O-200-48 starter bearing (no starter only) | Continental engine | none |
| c23.baffles | Make baffles 1 in large; trim to 1/4 in from cowl | engine mount; cowl on | cowl |
| c23.exhaust-fit | Install exhaust; cut cowl holes after | cowl fitted (done with exhaust off) | none |
| c23.cowl-reinforce | 4 plies BID at 45 on four inside edges, 2 in wide | prefab cowl; peel-ply sanding | none |
| c23.cowl-trim | Cut 9 in off each outboard end | reinforcement cured | none |
| c23.cowl-te-closeout | 5-ply BID TE with release tape, then 1 ply | cowl halves trimmed | cowl stood on TE, front opened 8.5 |
| c23.cowl-flange-wing | Build wing flange (5 ply BID) bottom first | cowl on engine; airplane inverted | grey tape release |
| c23.cowl-flange-outer-ply | Remove cowl; lay 1 ply BID outside | flange cured | none |
| c23.aluminum-rib | Form .020 rib; held by cowl screws | flange screws drilled | hand forming; shape on A-sheet (not held) |
| c23.turn-over | Invert airplane once to install cowl (7 people or hoist) | engine installed | hoist on crank flange |
| c23.skip-ahead | Do chapter 24 aft lower cover and chapter 25 bottom finishing first | | |

## 5. CP corrections touching chapter 23

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP27 p3-4 (text, no LPC) | MAN | do not use IIC for a Long-EZ Lycoming; new Section IIL; prototype-tested fuel, exhaust, baffles, dynafocal mount, carb controls | engine-side numbers should come from IIL (not held); chapter 23's IIC references are obsolete |
| CP27 p5 (text, no LPC) | DES | Lycoming cowl moved aft 0.7 in; engine moved aft with dynafocal; cowl lip 32.0 old, 32.7 new; mismatch to firewall top about 0.2 in | cowl and engine stations differ from VariEze; fit cowl before carving canopy aft cover |
| CP27 p5 (text, no LPC) | OPT | 6061-0 aluminum rib mentioned elsewhere; none | none |
| CP28 p9, LPC 61 | MEO | IIL BOM p37: 8 #6083 rubber bushings as alternative to #71032 (7/8 vs 1 in hole) | none for geometry |
| CP28 p9, LPC 63 | MEO | IIC p3: MA3-SPA should be MA3-PA | none |
| CP29 p7, LPC 69 | MEO | IIL p14 conical mount: 7/8 x .049 brace tube moves down for fuel pump | conical mount shape |
| CP31 p5, LPC 92 | MEO | ram inlet scoop floxed to lower cowl, pop rivets about every 2 in, 1 ply BID inside lapping 1 in | adds cowl/inlet layup; no weight given |
| CP31 p5, LPC 93-94 | MAN | replace listed aluminum fittings with steel fuel/oil fittings (AN822-6-2D, AN816-6D, AN823-6D, AN912-1D, AN823-4D) | fitting masses only |
| CP32 p5 (text, no LPC) | MAN-level caution | prop/spinner back plate must clear extension radius; torque 18-20 ft-lb; check mount station against IIL p14/p15 | prop/mount installation |
| CP32 p7, LPC 100 | MEO | IIL p6: 3 AN509-10R8 screws (later corrected to 4 by LPC 120, CP43 p4) | none |
| CP32 p7, LPC 101 | MEO | IIL p37: add two SP-5 spacers (gascolator stand-offs) | none |
| CP35 p9, LPC 108 | MEO | IIL p7/p13: brake master cylinder inboard of CS73 | none |
| CP35 p9, LPC 109 | MEO | adds Lycoming exhaust, dynafocal and conical mounts, A484 rings to the plans parts list (page 2-1) | BOM only |
| CP37 p4, LPC 116 | MEO | OM p30 CG aft limit 104 changed to 103 | CG limit 103 already used by the ledger |
| CP39 p6 (text, no LPC) | MAN-level caution | many builders skipped the metal shields in the wing-root areas of page 23-3; exhaust heat can damage wing foam | the aluminum rib must be modelled and built |
| CP40 p6, LPC 117 | MEO | IIL p10: replace Lycoming washer with AN970-6 (1.84 in spacer) | none |
| CP43 p4, LPC 120 | MEO | IIL p6: 4 AN509-10R8 screws per top attach point, not 3 | none |
| CP25 p6, LPC 19 | MEO | engine-mount extrusions: "Chapter 6" should be "Chapter 14" (A4) | chapter 14 and 15, not mine |
| CP25 p6, LPC 25 and VariEze change | DES | aluminum can replace steel firewall with fiberfrax; install after cowl | mass of firewall sheet; cp-text:CP25 p4 says about 2 lb saved |

LPC numbers for the CP27 text items do not exist (text-only notes). The page given is the footer-closing page.

## 6. Conflicts

| ID | Sources | Disagreement | Winner? |
|---|---|---|---|
| C1 | plans-1980:p157 text ("0.20 6061-0") against plans-1980:p158 and p010 (".020") | rib thickness 0.20 versus 0.020 | none stated; .020 is the drawing and BOM value, 0.20 is a typo by any reading (a 0.20 in sheet is not formable by hand), but no page declares it |
| C2 | plans-1980:p156 text says drill "3/16 (#10)"; same page drawing says "#12" | keeper plug center hole size | none; both digit reads are firm (#10 = 0.194, #12 = 0.189 in, so the difference is small) |
| C3 | plans-1980:p156 (any dash O-235 acceptable) against om-1980:p23 engine limits table and CP27 p5 | OM p23 lists limits for O-235 series C, E (80 octane) and F, L, G (100); CP25 p1 flags L2C Cessna 152 engines as bad for the Long-EZ (spin-on filter intrudes 1 in into the spar, no fuel pump) | not a direct conflict; open item for the model's L2C assumption |
| C4 | plans-1980:p157 fastener count: 8 + 5 + 5 + 3 + 3 + 4 + 4 = 32 against "40" | derived total 32 against printed 40 (the count of fasteners each side and the forward ones may not all be in the list; e.g. the 4 per flange on both flanges at both wings) | none; 40 is printed, my sum may omit uncounted holes; flag for the captain |
| C5 | om-1980:p4 ("approximately 750 lb") against om-1980:p25 sample (730) and cp-text:CP27 p4 (693.4 BEW to 883 lb) | empty weight 730 versus ~750; the exit test closes on 750 | none; 750 is "normally equipped" with starter and alternator (CP27 item 4 to 5: 761.9 to 777.3 lb); 730 is a sample |
| C6 | plans-1980:p171 (FS -6.8 to FS 196.6, 203.4 in) against om-1980:p3 (length 201.4 in) | 2 in apart; model `fuselage_length` already flags 175.3 versus 201.4 | none |
| C7 | om-1980:p36 (takeoff-only gross "1420") against om-1980:p4 and p28 ("1425") | max takeoff weight 1420 versus 1425; the ledger uses 1425 | none; both read from the text layer, hand-check the images (om pages) |
| C8 | om-1980:p32 "propeller bolts torque (180 inch lg)" against cp-text:CP32 p5 (18-20 ft-lb) and CP42 p5 (20-22 ft-lb) | 180 in-lb = 15 ft-lb versus 18-20 and 20-22 ft-lb | none; the OM text looks like "inch-lb" typo; vendor-specific higher value |
| C9 | plans-1980:p171 ("60 max dia") against om-1980:p5 (disc 58 in) and cp-text:CP42 p5 (62 in props for Long-EZ O-235) | prop diameter 60, 58 or 62 | none; the config's 60 matches the back cover only |
| C10 | config `engine_dry_weight_lb` 243 against `engine_mass_kg` 113 (= 249.1 lb; comment says "250 lb") | model internal mismatch; both under 246 only for 243 | model, not a source conflict |
| C11 | config `engine_cg_arm_in` 8.0, comment "Forward of firewall" against the pusher layout | the engine sits aft of FS 125 (oil FS 140, starter FS 150+) so a "forward of firewall" arm contradicts every held source | the config field is unsourced and the comment is wrong in direction |
| C12 | config `engine_rated_hp` 115 and `engine_rated_rpm` 2700 against om-1980:p23 (RPM max 2800 for O-235) and cp-text:CP25 p1 (O-235 L2C 118 hp at 2800) | rated rpm 2700 versus 2800; hp 115 (OM p2) versus 118 | none; OM p2 itself says 115 hp |

## 7. Open questions and low-confidence reads (captain's re-read list)

1. No engine arm exists in the held sources. Options for the ledger: leave "not yet computed"; or bracket the
   engine group from oil (FS 140) and starter (FS 150+). Do not invent a point value. Section IIL p14/p15 holds
   the mount station and is not held. CP54 p7 gives the engine CG as "about 15 in aft of the prop flange" (builder
   letter); the prop-flange FS is also not printed.
2. Carb bracket carb-hole diameter: printed "1-8" at plans-1980:p156; could be 1.6. Re-read at 8x.
3. Rivet callout "AN4?0-4-5 (8)": the middle character is smudged (likely AN470).
4. The 3 in arm in the TE stiffener sketch (plans-1980:p157) is unclear: crop and re-read.
5. Back cover "60 max dia": the inch mark may be a degree sign; the number itself reads 60 firmly.
6. Back cover FS -6.8 and WL 32.8: hand digits at 3x to 6x; FS -6.8 could read -6.3.
7. C4 fastener count: the printed 40 against my 32: ask whether the flange counts apply to each of four flanges.
8. CP page of the "normal 0-235 is 242 lb" statement: line found, page not confirmed; do not cite until paged.
9. Whether the owner has an A-sheet or Section II for the cowl moulds and exhaust: none held. The cowl outer
   shape, exhaust routing and baffle shapes exist only in Section II or the CP25 exhaust drawings (omitted in the
   transcription); all are "repr" for the model.
10. CP54 p7 prints a roll-angle tolerance "2o25'" (probably 2 degrees 25 minutes); not used.
11. Chapter 22 states "electric start adds over 25 lb" while CP27 p4 prices starter, alternator, belt, battery at
    68.5 lb (including the 25 AH battery, about 19 lb): consistent in kind, but not directly comparable.
