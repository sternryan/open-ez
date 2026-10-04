# Electrical system (chapter 22, p149 to p155): source research (2026-10-04)

Read-only research pass for milestone 2.8, crew B. Every number below was read on the page image
(hand digits cropped and enlarged 2.5x to 5x), not the OCR. 1980 plans cited as `plans-1980:pNNN` (PDF page).
Cobelu chapter 22 text (`cobelu`) was diffed against the scan; scan wins. CP text cited as
`cp-text:CPnn p<page>` (+ LPC number). Owner's Manual cited as `om-1980:p<printed>` (the OM PDF page equals
the printed page). Paraphrases are ten words or fewer. Nothing in the repo was edited. The owner holds NO
A-sheets: the battery full-size drawing (A6), the instrument-panel layout (A1), the nose/rudder-pedal
drawings (A6/A7) and the retractable landing/taxi light drawing (shipped separately, CP25 p4) are not
available, so every shape or station that lives only there is marked "repr".

## 0. Answers first (read this)

1. Chapter 22 is plans-1980:p149 to p155 (printed 22-1 to 22-7, last page says so on p155). No fuselage station,
   weight or arm is printed anywhere in chapter 22. It prints no weights at all except "electric start adds
   over 25 lb" (p149). Every electrical mass and arm in the model must come from the OM or CP text, or be derived.
2. Battery type and place: 12 V, 25 Ah, "Gill PSG-9" (p150, p151), in the nose on a shelf flox-bonded to the
   NG30 plates and F6 (p155). Both systems use the nose battery "to provide the correct CG" (p149). Station is not
   printed. The nose box runs from F22 (FS 22, derived in m24) forward to NG31 (about FS 0 to 1, derived in m24),
   so the battery arm is somewhere in FS 0 to 22 (derived range, see section 3).
3. The OM has no battery-location options. It only says to move the battery or add ballast to change the allowed
   pilot weight range (om-1980:p36). The CG effect of the nose location is spelled out in plans-1980:p149 and
   cp-text:CP27 p4 (section 6).
4. The model's electrical row (25 lb at FS 119.5, unsourced) is wrong in shape: the book puts the battery far
   forward (FS 0 to 22) and the alternator, starter and ring gear at FS 150 or more (cp-text:CP27 p4). The mass
   ledger needs at least two electrical rows, not one.
5. Ledger-closure trap: the OM's printed empty CG is 111.7 (om-1980:p25, p35), which is AFT of the 103 aft limit
   (om-1980:p28). The 97 to 103 band is the loaded CG, not the empty CG (section 5, C2).

## 1. Page map (`plans-1980`, confirmed on printed footers)

| PDF | Printed | Content |
|---|---|---|
| p148 | 21-? | last page of chapter 21 (fuel plumbing sheet); not in scope |
| p149 | 22-1 | text: System I vs II, battery in nose, starter advice, warning, strobes, landing light |
| p150 | 22-2 | System I schematic (solar, no starter); System II with generator schematic |
| p151 | 22-3 | System II with alternator; gear/canopy warning; lighting (position, strobe, landing) |
| p152 | 22-4 | engine instrumentation; starter circuit; antennas text and sketches |
| p153 | 22-5 | general installation notes: ground terminal, regulator, engine ground strap, panel wire routing, item key 1 to 22 |
| p154 | 22-6 | detail B breaker wiring and ring-tongue terminal table; detail C throttle microswitch; detail D canopy-lock microswitch |
| p155 | 22-7 | nose-gear microswitch, bottom strobe, wingtip night lights, strobe power-unit box, battery mounting; "last page, chap 22" |
| p156 | 23-1 | chapter 23 starts (not in scope) |

OM pages used: p3 (intro), p4 (weights), p10 (electrical diagram), p25 to p28 (W&B, limits), p33 to p36 (weighing),
p49 (inspection, battery), p65 (equipment list), p66, p67 (checklists).

## 2. Dimension, rating and part tables

### 2a. Battery, master, relays, charging, wire gauges

| Item | Value | Cite | Conf (digit read + why) | Cross-check | Model use |
|---|---|---|---|---|---|
| Battery | 12 V, 25 Ah, Gill PSG-9 | plans-1980:p150, p151 | high; letters "PSG" read twice, "G" and "6" look alike, OCR says "PS6" | om-1980:p10 diagram says 12 V 25 AH, no model | text |
| Battery location | nose, shelf on NG30 and F6; "both systems use the 25 amp-hour battery in the nose" | plans-1980:p149, p155 | high | cobelu ch22 same | text |
| Battery weight | not printed in chapter 22 | none | n/a | cp-text:CP27 p4: using a 25 Ah in the nose "accepts a 19 lb increase" vs the small battery | derived (19 lb delta, not an absolute) |
| Battery arm (FS) | not printed; F6 and NG30 only on A6 | plans-1980:p155 "see page A6" | n/a | nose box FS 0 to 22 from m24 (NG30 butts F22, p79) | repr |
| Battery shelf layup | 4 plies BID on wax paper, wet-set the battery on it, wrap glass up the sides | plans-1980:p155 | high | none | book |
| Battery shelf size | shelf 0.6 thick above floor mark; cover wrap 0.4 (duct tape gap, 4 thicknesses) | plans-1980:p155 | medium: "0.4" and "0.6" read at 2.5x, small hand digits | none | book |
| Battery cover | 3 plies BID over grey tape; remove tape after cure | plans-1980:p155 | high | none | book |
| Battery hold-down | long stainless worm clamp around cover, battery, shelf and F6 | plans-1980:p155 | high | F6 has a strap slot: plans-1980:p78 | book |
| F6 plate | 0.2 thick, dark red type 250 PV core, strap slot plus two round access holes | plans-1980:p78 | high | none | book (size only on A6: repr) |
| Battery access | large door in nose top (also canard removal) | plans-1980:p83 step 9 | high | om-1980:p49 lists battery in canard-off inspection | text |
| Master switch | AN3022-2 | plans-1980:p150, p151, p153 | high | om-1980:p10 same | text |
| Master relay | NONE shown; master switch carries all current; a relay "may be necessary" for lots of avionics | plans-1980:p149 | high | none | text |
| Master breaker | 40 A in System II alternator (shows "40" at the master); 30 A in generator system; none in System I (10 A fuse) | plans-1980:p151 (40), p150 (30, 10) | medium: "40" and "30" are hand digits, read at 2.5x | om-1980:p10 shows 40 | text |
| Alternator breaker | NOT drawn on p151 | plans-1980:p151 | high (absent) | cp-text:CP34 p7 LPC 106: needed, sized to max output (35 A alt, 40 A breaker) | text (DES) |
| Starter relay | "ST-77" relay, coil to ground, switched from the 12 V bus through a 2 A breaker | plans-1980:p152 | medium: "ST-77" hand digits | p151 and p150 show "start relay" with a 2 A bus tap | text |
| Starter switch | AN3022-6 with MS25224 guard, #18 control wire | plans-1980:p152 | high | p149 says use a guard | text |
| Starter and battery cables | #2 AWG each (to + on battery, to starter) | plans-1980:p152 | high ("#2" read at 2.5x) | p152 note: ground wire battery to engine goes #10 to #2 if starter | text |
| Ground (battery to engine) wire | #10 without starter; #2 AWG with starter | plans-1980:p152 note, p151 (#10) | high | cp-text:CP37 p3: #2 conduit-bond wire (OPT) | text |
| Braided ground strap | to engine mount, bolted copper strap about 1/16 thick, AN3 bolt | plans-1980:p153 | high | none | text |
| Firewall ground terminal | #10-32 screw, AN960 washers, MS21092-3 nut, ring-tongue terminals | plans-1980:p153 detail A | medium: "MS 21092-3" hand digits | none | text |
| Regulator | 12 V automotive type, on firewall or forward per section IIA note | plans-1980:p153 | high | none | text |
| Alternator output meter | 0 to 60 A face; "standard 60-amp alternator" per CP27 | plans-1980:p151 | high | cp-text:CP27 p4 item 4 | text |
| Generator output meter | 0 to 60 face | plans-1980:p150 | high | none | text |
| Optional 40 A fuse | between generator regulator A and generator | plans-1980:p150 | medium | none | text |
| Optional volt meter | VDO 332-044 (face 8 to 16) | plans-1980:p150, p151 | medium: last digit "4" vs "1" in p151 crop | cp-text:CP22 p5 lists VDO 332-044 | text |
| Clock | VDO 370-022, 1 A tap, #22 | plans-1980:p151 | high | cp-text:CP22 p5 same | text |

### 2b. Wire runs and gauges (every gauge printed)

| Run | Gauge | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Battery + to master (System II) | #10 | plans-1980:p151 | high | om-1980:p10 same | text |
| Master to 12 V bus | #10 | plans-1980:p151, p150 | high | none | text |
| Battery - to ground bus / terminal | #10 (braided to engine) | plans-1980:p151 | high | none | text |
| Alternator B+ (alternator to terminal block) | #10 | plans-1980:p151 | high | om-1980:p10 same | text |
| Alternator F and regulator leads | #18 | plans-1980:p151 | high | none | text |
| Regulator I terminal lead to bus | #18 | plans-1980:p151 | medium | none | text |
| Generator system leads A, F, B | #10 (A, B), #18 (F, G) | plans-1980:p150 | medium: small text | none | text |
| Clock and volt meter leads | #22 | plans-1980:p150, p151 | high | none | text |
| System I solar leads | #22 | plans-1980:p150 | high | "all wire not shown is #18" | text |
| Everything else on the System I and II diagrams not marked | #18 | plans-1980:p150 note | high | none | text |
| Engine instrumentation, all wire | #22 | plans-1980:p152 | high | none | text |
| Circuit-breaker interconnect | #12 | plans-1980:p154 detail B | high | cp-text:CP22 p8: "#12 can be #18" is a VariEze Section III note, not this chapter (section 4) | text |
| Wire from panel to alternator/battery via ammeter | #10 with RC10-8 terminals | plans-1980:p154 | high | none | text |
| Warning, lighting and strobe switch leads | #18 | plans-1980:p151 | high | none | text |

Wire LENGTHS and total wire weight are not printed. Panel-to-firewall run is "approx routing along the forward
side of the instrument panel then down the fuselage lower corner, potted every 10 in" (plans-1980:p153); no length.

### 2c. Breakers, fuses and bus taps (System II alternator unless noted)

| Circuit | Rating | Cite | Conf | Model use |
|---|---|---|---|---|
| Clock | 1 A | plans-1980:p151 | high | text |
| Engine instruments | 1 A (p153 key item 15 hand-corrected to 1 A) | plans-1980:p151 (1), p153 | high | text |
| Warning system | 3 A | plans-1980:p151, p153 item 17 | high | text |
| Nav/com | 5 A | plans-1980:p151, p153 item 14 | high | text |
| Gyro | 3 A | plans-1980:p151, p153 item 16 | high | text |
| Position lights | 10 A | plans-1980:p151, p153 item 22 (hand-written) | high | text |
| Fuel pump | 2 A | plans-1980:p151, p153 item 4 | high | text |
| Strobe | 10 A | plans-1980:p151, p153 item 18 | high | text |
| Instrument lights | 5 A | plans-1980:p151 | high | text |
| Landing light | 10 A (100 W lamp) | plans-1980:p151 | high | text |
| Starter relay tap | 2 A | plans-1980:p151, p152 | high | text |
| Alternator field (via micro 8A1011 switch) | 5 A | plans-1980:p151 | medium | text |
| Oil-pressure/hour-meter | 2 A (CP23 adds the wiring) | cp-text:CP23 p8 | medium | text |
| System I master fuse | 10 A; charge fuse 2 A; fuel pump 2 A | plans-1980:p150 | high | text |

### 2d. Lights, strobes, instruments, antennas

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Position lights | Whelen A600-PR-14 (red, left) and A600-PG-14 (green, right), wingtip, silicone-bonded | plans-1980:p151, p155 | high | none | text |
| Strobe power supply | Whelen A413A-HDA-14 single flash (30% less current than "DF" model) | plans-1980:p149, p151 | high | cp-text:CP30 p7 notes Wicks stocks it | text |
| Strobe supply location | center-spar fairing left side, or back of front seat bulkhead, or left thigh support | plans-1980:p149, p155 | high | none | repr (no station) |
| Single bottom strobe | Whelen A490 T, DF-14 supply, 1.7 A; unit A430 or equal, off-center hole to miss thigh-support bulkhead | plans-1980:p155 | high | none | text; "not legal for night" |
| Landing/taxi light | 100 W; prototype uses retractable lamp in right thigh-support cavity | plans-1980:p149, p151 | high | cp-text:CP25 p4: retract drawing now ships separately (not in owner's scan) | repr |
| Warning horn | Radio Shack mechanical buzzer 273-051 | plans-1980:p151 | medium: "273-051" | none | text |
| Warning relay | Calectro D1-974 | plans-1980:p151, p152 | medium: "01" vs "D1" ambiguity | none | text |
| Warning light | Radio Shack 272-327 | plans-1980:p153 item 6 | high | none | text |
| Warning switches | Radio Shack 275-1102 or micro V3-1001JV7 or SMJS-2 (throttle, gear, canopy) | plans-1980:p151, p153 | medium | none | text |
| Tach | Carr 206 gauge, Carr 207 sender | plans-1980:p152 | high | cp-text:CP22 p5 same | text |
| Oil pressure gauge | VDO 350-049 | plans-1980:p152 | high ("049" read at 5x; last glyph is a 9) | cp-text:CP22 p5 prints 350-044 (conflict C4) | text |
| Oil pressure sender | VDO 360-009 with kit 240-023 | plans-1980:p152 | medium: last digit 9 vs 4 | cp-text:CP22 p5 prints 360-004; cp-text:CP30 p9 says 240-023 is the wrong sender, use 360-25 | text |
| Oil temp gauge | VDO 310-019 | plans-1980:p152 | high at 5x | cp-text:CP22 p5 prints 310-014 | text |
| Oil temp sender | VDO 323-057 with kit 240-023 | plans-1980:p152 | medium | cp-text:CP22 p5 same | text |
| CHT / EGT gauges | Westach 2A1 and 2A2 | plans-1980:p152 | medium | none | text |
| CHT sender | Westach 712-5W (CP23 replaced VDO 323-701) | plans-1980:p152 | high | cp-text:CP23 p8 | text |
| EGT probe | Westach 712-2DW | plans-1980:p152 | medium | none | text |
| Hour meter | VDO, 12 V, circuit relayed on oil pressure | plans-1980:p152 | medium | cp-text:CP24 p7: part #1763-002-016 replaces 331-011 | text |
| Instrument panel station | front face FS 40 (reference for weighing, ballast) | om-1980:p33, p34 | high | model: fs_pilot_seat 59, instruments arm 29.5 (unsourced) | book |
| Antennas | nav V on canard underside; comm on main gear (plans) or in winglet (CP26) | plans-1980:p152; cp-text:CP26 p8 | high | cp-text:CP30 p9 LPC 78: nav strips 22.8 in, not 24 | text |
| Nav antenna copper tape | 48 in total, two 22.8 in strips (LPC 78), 1/2 in wide, four toroids | plans-1980:p152 (48 in, 1/2 in); cp-text:CP30 p9 | high | cobelu says 22.8 {CP30 PC78} | text |
| Comm antenna foil (winglet) | two strips 20.3 in, 1 in ahead of the TE, 1/8 in gap, three balums | cp-text:CP26 p8 | high | cobelu same | text |
| Transponder antenna | under the front thigh support or wing root LE; RST type in centersection spar | cp-text:CP30 p7, CP33 p6, CP34 p8 | medium | none | text |
| Ring-tongue terminals | RA18-n (22-18 ga), RB14-n (16-14), RC10-n (12-10); n = 6, 8, 10, 14 (1/4 in) bolt hole | plans-1980:p154 | high | none | text |
| Microswitch (throttle) | actuates within 1 in of knob travel from idle; music wire 1/16 dia; .025 alum bracket; #4-40 hardware | plans-1980:p154 detail C | medium | CP32 LPC 98: delete "yaw trim bracket" label | text |
| Microswitch (canopy lock) | on lock plate C9, 2 x #4-40, bend tab so it trips when locked | plans-1980:p154 detail D | high | detail cites "pg 22-10" (no such page here, section 5 C8) | text |
| Microswitch (nose gear) | trips in the last 0.10 in of down travel, .032 alum angle, on NG30 | plans-1980:p155 | medium: "0.10" and ".032" hand digits | "see chap 13" | text |

## 3. Weights and stations (everything printed, with source)

### 3a. Electrical-related masses

| Item | Weight | Station / arm | Cite | Conf | Model use |
|---|---|---|---|---|---|
| Electric start total add | "over 25 lb", mostly aft on the engine | aft, not given | plans-1980:p149 | high | text |
| Small alternator system (CP26) incl wiring and regulator | 4.9 lb | not printed | cp-text:CP27 p4 item 2 | high | book (CP) |
| B&C lightweight alternator system | 4.25 to 4.75 lb (gear or belt driven) | engine | cp-text:CP26 p11 | high | text |
| Kobuta-type 10 A alternator | under 5 lb | engine | cp-text:CP23 p8 | high | text |
| Com + nav + transponder + installation | 15.4 lb | not printed | cp-text:CP27 p4 items 3, 5 | high | book (CP) |
| Std 60 A alternator + starter + ring gear + belt + brackets + regulator + wiring + relays + 25 Ah battery | 68.5 lb (item 4 minus item 1: 761.9 - 693.4 = 68.5) | starter, ring gear, alternator "way back at station 150+"; battery far forward | cp-text:CP27 p4 | high | book (CP) |
| 25 Ah nose battery vs small battery | +19 lb | nose | cp-text:CP27 p4 prose | high | derived |
| Nose battery 2nd (N26MS only) plus 15 lb lead in front of NG31, plus wiring | 44.8 lb (item 7 minus item 6: 860.2 - 815.4) | nose (ahead of NG31) | cp-text:CP27 p4 | high | derived (N26MS only) |
| Landing light, nav lights, strobes, NACA inlet, 500x5 tires, dynafocal mount, cabin heat, primer, intercom, stereo (N26MS extras) | 38.1 lb | mixed | cp-text:CP27 p4 item 6 | high | reference |
| Upper winglet with RST comm antenna and coax | 6.0 lb | winglet | cp-text:CP26 p3 | high | already in ledger |
| Dynafocal engine mount | 5 lb 3 oz (5.19) | engine | cp-text:CP26 p3 | high | reference |
| Engine-installed light alternator (system tail-heavy) | VariEze: 11 lb alternator and lead nose ballast | n/a | cp-text:CP12 p3 | low, VariEze | not used |

N26MS build-up list as printed (CP27 p4), all with N26MS electrics, no CG printed per row:

| # | Configuration | Empty weight (lb) |
|---|---|---|
| 1 | BEW: VFR instruments, g meter, turn/bank, no alternator, no starter, graphite cowl, small battery for warning and fuel pump | 693.4 |
| 2 | 1 plus small alternator (4.9) | 698.3 |
| 3 | 2 plus com, nav, transponder (15.4) | 713.7 |
| 4 | 1 plus 60 A alt, starter, ring gear, brackets, relays, 25 Ah battery (68.5) | 761.9 |
| 5 | 4 plus avionics (15.4) | 777.3 |
| 6 | 5 plus lights, tires, heat etc (38.1) | 815.4 |
| 7 | 6 plus provisions for a 108 lb pilot at CG 102.2 (44.8) | 860.2 |
| 8 | 7 plus 12 "small" items (22.8) | 883 |

Arithmetic checks: 693.4 + 4.9 = 698.3 ok; 698.3 + 15.4 = 713.7 ok; 693.4 + 68.5 = 761.9 ok; 761.9 + 15.4 = 777.3 ok;
777.3 + 38.1 = 815.4 ok; 815.4 + 44.8 = 860.2 ok; 860.2 + 22.8 = 883.0 ok. Item 7: aft limit 103 - 102.2 = 0.8 in, but
the text says "1.8 in fwd of aft limit"; 103 - 102.2 = 0.8 (conflict C5).

The brief points to CP26 page 3 for the weight list. CP26 p3 has parts only (cp-text:CP26 p3, already in the
ledger); the electrical build-up list is cp-text:CP27 p4.

### 3b. Stations and arms that bound the electrical masses

| Item | Value | Cite | Conf | Cross-check | Model use |
|---|---|---|---|---|---|
| Instrument panel front face | FS 40 | om-1980:p33, p34 | high | none | book |
| Nose tip | FS -6.8 | plans-1980:p171 | high (labelled, read on image) | model fs_nose -6.8 | book |
| Nose gear axle | FS 17, WL -22 | plans-1980:p171 (hand correction -22 per CP25 LPC 24) | high | om-1980:p35 sample nose arm 19.6, text "about 20" (conflict C6) | book |
| Main gear axle | FS 110.5 | plans-1980:p171; om-1980:p34 (110.5 +/- 1) | high | om-1980:p35 sample 110.5 | book |
| Firewall | FS 125 | plans-1980:p171 (FS 125 label) | high | model fs_firewall 125 | book |
| F22 bulkhead | FS 22 | m24 derived (125 - 103), plans-1980:p79 | derived, not printed | model fs_f22 22.0 | derived |
| NG31 bulkhead | about FS 0 to 1 | m24 derived (22 - 21.9 or 20.9) | derived range | none | derived |
| Battery arm (derived range) | FS 0 to 22; mid-point FS 11 for illustration only | nose box between NG31 and F22 | low (A6 only) | none | repr |
| Starter, ring gear, alternator | "station 150+" | cp-text:CP27 p4 | high | engine aft of firewall FS 125 | text |
| Pilot | FS 59.0 | om-1980:p25 | high | model fs_pilot_seat 59 | book |
| Passenger | FS 103.0 | om-1980:p25 | high | none | book |
| Fuel | FS 104.5 (moment = gal x 6.0 per OM) | om-1980:p25, p26 | high | model fuel_arm 104.5 | book |
| Oil | FS 140.0 | om-1980:p25 | high | none | book |
| Baggage | FS 90 | om-1980:p25 | high | none | book |
| Empty (sample) | 730 lb at 111.7 (moment 81541) | om-1980:p25, p35, p36 | high | model mass_ledger empty row | book |
| CG limits | fwd 97, aft 103; first-flight box about FS 99 to 101.5, to 1100 lb | om-1980:p28 (image) | high at limits; box edges medium | ledger envelope | book |
| Weights limits | 1325 normal; 1425 takeoff-only (prose also says 1420) | om-1980:p4, p28, p36 | high | conflict C7 | book |

Sample-loading checks (om-1980:p25, p26): light pilot 730 + 8 + 240 + 135 = 1113 ok; moments 81541 + 1120 + 25080
+ 7965 = 115706, matches the prose 115706 and not the table 115708 (ledger errata already lists this). Weighing
table (om-1980:p35): 373.7 + 372.0 + 7.2 - 25 = 727.9, printed 730 (2.1 lb off); the left main moment prints 4110 but
372.0 x 110.5 = 41106 (typo). 41296 + 41106 + 141 - 1000 = 81543 vs printed 81541: close.

### 3c. Battery location and CG effect (what the sources say)

| Statement | Cite |
|---|---|
| The 25 Ah battery in the nose is required to "provide the correct CG" in both systems | plans-1980:p149 |
| System I (no starter, no alternator) keeps CG forward, matters for pilots under 160 lb | plans-1980:p149 |
| Electric start adds over 25 lb mostly aft; first flights at forward CG and light weight; leave starter and heavy cable out initially to avoid nose ballast (a double weight penalty) | plans-1980:p149 |
| Mount equipment as far forward as practical, e.g. start relay and over-voltage on the front of F22 | plans-1980:p149 |
| Under 170 lb front-seat pilot: use the 25 Ah nose battery and accept +19 lb; needed anyway to balance | cp-text:CP27 p4 |
| Under 150 lb pilot with starter: starter, ring gear, alternator at station 150+ need nose ballast, large empty-weight penalty | cp-text:CP27 p4 |
| N26MS needed a second 25 Ah battery plus 15 lb lead ahead of NG31 to let a 108 lb pilot fly at CG 102.2 | cp-text:CP27 p4 |
| Raise or lower the pilot weight range by moving the battery or adding ballast; start testing in the first-flight box | om-1980:p36 |
| An overweight aircraft over 1100 lb is preferred over an aft CG for first flights | om-1980:p34 |
| Weighing ballast sits at the instrument panel FS 40 (not a battery) | om-1980:p33 |
| VariEze analogue: 12 lb permanent ballast ahead of the battery keeps CG forward of FS 100 | cp-text:CP28 p5 (VariEze, N60SD) |

The OM names no alternative battery locations. The plans give one (nose shelf). Alternative locations appear only in
CP text: second battery paired in the nose (CP27 p4), two motorcycle batteries in a 24 V system (CP34 p8, CP35 p10),
battery access doors added by RAF (cp-text:CP46 p3). None is a plans-approved relocation.

CG sensitivity, derived from printed values, with an assumed battery arm (the arm is NOT printed):
- Change in empty CG when w lb moves from arm a to arm b: delta = w x (b - a) / W. With W = 730 lb, 1 lb moved 100 in
  shifts CG 100/730 = 0.137 in.
- Adding the 19 lb battery delta at an assumed FS 10 to a 713.7 lb airplane at arm 111.7: 19 x (10 - 111.7) / (713.7 + 19)
  = -2.64 in (forward). Assumption is the FS 10 arm; real range FS 0 to 22 gives -2.9 to -2.3 in.
- Moving the same 19 lb from FS 10 to a seat-area FS 100: +2.5 in aft (19 x 90 / 730 = 2.34, rounding of the
  base weight; use 2.3 to 2.5).

## 4. Build-order list (op candidates)

| # | Short name | What is done (<= 10 words) | Prerequisites | Jig or fixture |
|---|---|---|---|---|
| E1 | Pick system | choose System I or II alternator or generator | none; OM weights guidance | none |
| E2 | Firewall hole | cut wire pass-through hole per page 21-8 position | firewall, ch15 | none; position only on the chapter 21 page |
| E3 | Panel routing | lay panel wire bundle forward side, down fuselage corner | instrument panel (ch04), side consoles NOT yet glued (CP33 p6) | wire bundle potted with silicone every 10 in |
| E4 | Panel switches and breakers | mount switches, breakers, ground terminal on panel | panel, E3 | ring-tongue crimp tool |
| E5 | Throttle microswitch | music-wire trips switch within 1 in of idle | throttle (ch16 / section IIA), bracket, yaw trim bracket | drill #50, 1/4 hole |
| E6 | Canopy microswitch | tab on lock plate C9 trips when locked | canopy lock plate C9 (ch18) | none |
| E7 | Nose-gear microswitch | angle bracket on NG30 trips last 0.10 in down | nose gear box (ch13) | none |
| E8 | Battery shelf | 4 plies BID, wet-set battery on wax paper | nose box NG30 and F6 (ch13), battery on hand | battery wrapped in duct tape as a mould |
| E9 | Battery cover and strap | 3 plies BID cover, worm clamp around F6 | E8 | grey tape wrap, remove after cure |
| E10 | Firewall terminal block | mount terminal block, regulator, braided ground strap | firewall, engine mount (ch23 or ch15) | none |
| E11 | Wing wiring conduits | route nav and strobe wires through wing, spar, bulkheads | wings, centersection holes, CS6 and CS7 holes (CP30 p7) | male/female plug pair in spar |
| E12 | Position lights | silicone-bond A600 units at wingtips, not on winglet root | wingtips (ch19) | thin knife for later removal |
| E13 | Strobe supply | mount supply in spar fairing, left thigh support or seat bulkhead | centersection (ch14), strake / fairing block (ch21) | none |
| E14 | Nav antenna | stick two 22.8 in foil strips under canard | canard glassed (ch10), kit | peel-ply BID cover |
| E15 | Comm antenna | foil strips in winglet foam before inboard skin | winglet foam (ch20), ferrite beads | toothpicks to hold coax |
| E16 | Landing light | install retractable lamp in right thigh support | thigh support, separate drawing (not held) | drawing not held |
| E17 | Starter and cables | #2 cables to relay and starter (optional) | engine, ch23 | none |

Ordering notes: E2 and E3 must happen before the side consoles are glued (cp-text:CP33 p6). E8 needs ch13 parts built.
E14 needs the canard skinned. E15 must precede winglet inboard glassing (CP26 p8). Nothing in chapter 22 gives a cure time
(none printed).

## 5. CP corrections touching chapter 22

| Entry | Class | What changes | Model impact |
|---|---|---|---|
| CP27 p7 LPC 49 (plans p22-6) | MEO | circuit-breaker label "roll trim" becomes "fuel pump" | none; scan p154 already carries the hand note |
| CP32 p7 LPC 98 (plans p22-6, center drawing) | OBS | delete the "yaw trim bracket" label | none; label is still printed on p154 |
| CP34 p7 LPC 106 (plans p22-3) | DES | add a breaker between alternator B+ and battery sized to max output (35 A alt, 40 A breaker) | add a breaker row if the wiring is modelled; mass negligible |
| CP30 p9 LPC 78 (Section I, antennas) | DES | nav antenna strips 22.8 in, not 24 in | antenna foil length only; no mass impact |
| CP31 p5 LPC 90 (plans p20-4 step 6) | MEO | pointer to Section III becomes "see page 22-3" | none; chapter 20 pointer, confirms 22-3 is the warning/lighting page |
| CP26 p8 | OPT/info | com antenna moves to winglet: foil 2 x 20.3 in, 3 balums, kit about $25 | none for the ledger (6 lb winglet already includes it) |
| CP23 p8 | info | oil-pressure low warning light and hour meter wiring, 2 A breaker; CHT sender 712-5W | none |
| CP25 p4 | info | retractable landing/taxi light drawing now ships with plans (separate sheet) | drawing not held; repr |
| CP22 p8 (Sect III page 2: #12 wire can be #18), CP25 p6 (Section I page 22-5 canopy catch FS 57), CP26 "VariEze canopy chapter 22" | VariEze only | VariEze chapter 22 is the canopy; these are NOT Long-EZ electrical corrections | none; do not apply |
| CP30 p9 "VDO 240-023 sender not correct, use 360-25" | MEO (VariEze list) | oil-pressure sender number | text only; listed as VariEze plans change, scope unclear |
| CP24 p7 | info | hour meter replacement number 1763-002-016 | none |
| CP34 p4, CP35 p10 | info | heater needs a manifolded, overboard-vented battery; Yuasa YB14L-AZ pair is a 24 V system | none for the 12 V base model |
| CP37 p3, CP40 p3 | OPT | copper-tube conduit and ground #2 wire for Loran noise | none |

## 6. Conflicts (both sources cited; no winner picked without a page)

- C1 Empty weight: om-1980:p4 "approximately 750" vs om-1980:p25, p35, p36 sample 730 vs cp-text:CP26 p15 "710 basic, 750
  equipped" vs cp-text:CP27 p4 693.4 BEW and 761.9 (alternator, starter, 25 Ah). These are different configurations, not
  one number. Block 2 exit test says "~750"; the OM prose 750 pairs with CP26 p15 equipped and CP23 p2 "750 with electric".
  The page that closes it is the builder's own equipment list (om-1980:p65), which is blank.
- C2 CG band: om-1980:p35 empty CG 111.7 vs om-1980:p28 limits 97 to 103. The empty airplane is behind the aft limit by
  about 8.7 in; the pilot at FS 59 moves it forward. A ledger test of "empty CG in 97 to 103" will fail on the book's own
  sample. The sample loaded cases (om-1980:p26) are 103.96 (light pilot, outside the limit) and 101.06.
- C3 Electrical row: model electrical 25 lb at FS 119.5 (unsourced) vs book battery FS 0 to 22 and alternator/starter FS 150+.
- C4 VDO numbers: plans-1980:p152 prints 350-049, 360-009, 310-019; cp-text:CP22 p5 lists 350-044, 360-004, 310-014
  (same hand digits 4 and 9 look alike on the scan; 5x crop reads a 9). CP30 p9 says a different 360-25 for the sender.
  Part numbers only; no model effect.
- C5 N26MS item 7: cp-text:CP27 p4 says CG 102.2 is "1.8 in fwd of aft limit"; 103 - 102.2 = 0.8. The 102.2 vs 1.8 pair
  cannot both hold with an aft limit of 103 (limit would be 104.0). om-1980:p28 chart limit is 103.
- C6 Nose gear arm: om-1980:p35 sample 19.6, text "about F.S. 20" vs plans-1980:p171 label FS 17 (already in the model).
- C7 Takeoff gross: om-1980:p4 and p28 say 1425; om-1980:p36 prose says 1420.
- C8 Stale page refs: p154 detail D cites "Section I pg 22-10" for the C9 lock plate; chapter 22 has 7 pages, and
  cp-text:CP13 p6 / CP12 place the canopy catch at VariEze page 22-10 (VariEze canopy). Treat as a stale pointer to the Long-EZ
  canopy chapter 18.
- C9 Citation mismatch: cobelu ch22 cites "CP26 Page 7" for the broken gear-strut comm antenna; cp-text has that at CP29 p7
  (VariEze comm antennas), and the Long-EZ winglet antenna at CP26 p8.
- C10 Master breaker rating: p151 prints "40" at the master; p150 generator system prints "30"; p153 key item 11 only says
  "master circuit breaker". Different systems, not a conflict, but the model needs the one for its chosen system.

## 7. Open questions and low-confidence reads (for captain re-read)

1. Battery arm: only on A6 (not held). Needs NG30 and F6 stations on the full-size drawing; today only the range FS 0 to 22.
2. Gill PSG-9 weight is unprinted; the only handle is the +19 lb vs small battery (cp-text:CP27 p4). Is a ~20 lb absolute
   weight acceptable for the ledger, or leave it "not yet computed"?
3. Station of the starter, ring gear and alternator: "150+" (CP27 p4) is a lower bound, not an arm.
4. Whether to model System I (no alternator, no starter, solar) as the book-recommended baseline: that matches the OM's 750 lb
   only if "approximately" covers 713.7 + extras; no source states which system the OM's 730 or 750 is.
5. Hand digits worth a second look: the 40 vs 30 master breaker; "ST-77" relay; Calectro D1-974; VDO 332-044 final digit;
   0.4 and 0.6 shelf dimensions on p155; "0.10 in" nose-gear switch travel; strobe supply A413A-HDA-14.
6. CP27 p4 item 7 "1.8 in fwd of aft limit" (C5): ask which is right, 102.2 or 101.2.
7. Wire runs lengths and total harness weight are not in any source; the ledger must estimate or leave blank.
8. The VariEze CP22 "#12 can be #18" and CP25 "canopy catch FS 57" notes were classed as VariEze-only because VariEze chapter 22
   is the canopy; a Long-EZ reader should confirm from the Section list before closing.
9. The retractable landing/taxi light mass and location (right thigh-support cavity, plans-1980:p149) have no weight;
   drawing not held.
