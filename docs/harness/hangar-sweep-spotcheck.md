# Hangar H1: powerplant sweep spot-check

Date: 2026-10-18. Sweep under test: `docs/research/2026-10-18-powerplant-sweep.md` (made by a research crew with web search).

Method (different from the sweep's author, per the plan): each URL was fetched with a plain HTTP client, converted to text
(`pdftotext` for PDFs, tag-stripping for pages), and searched for the claimed value with a regular expression. A local
extraction model was then asked, from a 3,000-character window of the fetched text and without seeing the sweep, to quote the
value. A fact counts as `match` when the value appears in the fetched text; the extraction model's answer is shown where it
agreed. Facts the sweep marked unsourced stay unknown. Owner's-manual facts were checked against the community PDF of the
manual (printed page footers), not the web transcription the sweep cited.

| Fact | URL (registry id) | Value seen in the fetched text | Result |
|---|---|---|---|
| UL350i 118 hp | ulpower.com UL350i page (`ulpower-ul350i`) | "Horsepower: 118hp" | match |
| UL350i ready to fly 78.4 kg | same | "Ready-to-fly weight: 78,4 kg (173 lb)" | match |
| UL350i mogas minimum | same | 95 RON (91 AKI) below serial 223501; 91 RON (87 AKI) above; 100LL allowed if mogas is unavailable | match |
| UL350i ethanol limit | same | no ethanol percentage on the page | confirmed absent, stays unknown |
| UL350i cruise fuel about 18 L/h | same | "cruising estimated average is UL350 +/-18l" under a Liter/hour heading | match (figure read from running text) |
| UL350i / UL350iS operational 79.5 kg | ULPower technical data M0510 Rev 5 (`ulpower-techdata`) | "UL350i / UL350iS: 79,5 kg (175 lb)" | match |
| 912 iS 16.5 L/h at 75% | avsport.org operator's manual (`rotax-912is-om`) | "At 75 % continuous performance 16.5 l/h (4.3 gal/h)" | match |
| 912 iS 63.6 kg and add-on weights | flyrotax datasheet (`rotax-912is-datasheet`) | 63.6 kg (140.2 lb); exhaust 4.8, mount frame 2.0, alternator 3.0, air guide 0.4, fuel pumps 1.6 kg | match |
| Rotax maximum ethanol 10% | Rotax operating-fluids note (`rotax-fuel-si`) | "Fuels that contain more than 10% ethanol blend ... not permitted" | match |
| 916 iS 85.8 kg, 160 hp | flyrotax 916 iS page (`rotax-916is-page`) | "... turbocharger, intercooler, exhaust system 85.8" kg; 160 hp (117 kW) | match |
| 915 iS 82.2 kg, 141 hp | Rotax card (`rotax-915is-card`) | 82.2 kg and 141 hp found in the text | match (extraction model could not isolate the cell; regex hit both) |
| DeltaHawk DHK180 335 lb / 151 kg | DeltaHawk spec sheet (`deltahawk-spec-2025`) | "335lbs.(151kg) - INCLUDES STARTER ALTERNATOR, TURBO, & EXHAUST SYSTEM" (letter-spaced text layer, read after removing spaces) | match |
| Swift UL94 5.87 lb/gal, ethanol-free | Swift FAQ (`swift-ul94-faq`) | "UL94 weighs 5.87 pounds per gallon: identical to 100LL"; "super-premium ethanol-free auto-gasoline" | match |
| Ethanol dissolves composite tank resins | BMAA SB 2695 (`bmaa-sb2695`) | "many resins used in the construction of composite fuel tanks are partially dissolved by ethanol" | match |
| E-Z Poxy and Jeffco coupons in 100LL and E10 | Kitplanes article (`kitplanes-tank-epoxy-2018`) | 54 coupons, two per test, 18 months; E10 measured at 8.4% ethanol; "Neither aviation gas nor mogas test coupons showed any obvious physical degradation" | match (the extraction model returned "not stated" from its window; confirmed by direct text search) |
| Yates pack 525 lb, 450 V, 80 Ah | Wired 2013 (`wired-yates-2013`) | "It weighs 525 pounds and takes up the entire back seat ... 450-volt, 80 amp-hour" | match; 151 Wh/kg re-derived as 36,000 Wh / 238.1 kg = 151.2 |
| Amprius 500 Wh/kg cell | Amprius release (`amprius-sicore500`) | "500 Wh/kg at a 1C continuous discharge rate" | match (cell, company claim) |
| Owner's manual: autogas "can dissolve the epoxy in the fuel tanks"; two 28 gal tanks, 52 gal total | `om-1980` printed p8 (community PDF, pdftotext) | text on printed page 8 | match |
| Owner's manual: 161 knots maximum true cruise | `om-1980` printed p15 | "maximum true cruise speed of 161 knots (185 mph)" | match |

Disagreements with the sweep: the manual says two 28 gallon tanks (52 gal total); the sweep's prose says two 26 gal tanks.
The total (52 gal) agrees. The record uses the manual's 52 gal.

Not checked, so unknown in the record: BMAA and Rotax statements beyond those above, any UL350i ethanol limit, hybrid kit
availability, 916 iS fuel flow, coolant and radiator weights, tank-resin behavior with UL94, and every price.
