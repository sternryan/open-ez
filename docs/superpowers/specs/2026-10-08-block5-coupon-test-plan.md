# Block 5 coupon test plan (pulled forward for Block 3 M3.4)

Status: draft, 2026-10-08, Block 3 captain #3. Paper only: nothing is bought, booked or cured from
this document. The purchase order is `docs/harness/block5-coupon-purchase-order.md`.

## 1. Why now

Block 3's M3.4 strength gate needs lamina strengths and moduli for the book cloths (BID 7725, UND 7715)
and for the candidate carbon. None of them has a public wet-layup source in the warp direction:

- AGATE's wet-layup methodology tests only the fill direction, so report 115 (carbon) and report 114
  (glass) have no warp companion by design.
- No cured lamina data were found for BID 7725 or UND 7715.
- The search record is in `docs/harness/block3-source-notes.md`, "S2 follow-up".

Owner-made coupons are the only realistic source. Ledger row 77 made this visible in the data: the
carbon proxy's warp values (E1, nu12, F1t, F1c) read `flag: requires_original_test`, and each one
names its closing coupon below. The book lamina stays `unsourced` because its search did not show
that no source exists.

The coupons also measure the real system, which the proxies never could. They use MGS L285 resin and
the owner's own process, where the proxies used MGS 418 and AGATE's process.

## 2. What closes what

Material codes: **BID** is style 7725 glass, **UND** is style 7715 glass, and **CPW** is 3K plain-weave
carbon at about 5.8 oz/yd2 (the closest commercial match to the AGATE 115 cloth). All three are in
MGS L285 with hardener 287.

Coupon ids are `B5-<material>-<condition>`. The conditions are:

| condition | test | measures | lamina inputs closed |
|---|---|---|---|
| T0 | ASTM D3039/D3039M, warp along the load | strength, chord modulus, Poisson's ratio (0/90 rosette or biaxial extensometer) | F1t, E1, nu12 |
| T90 | ASTM D3039/D3039M, fill along the load | strength, chord modulus | F2t, E2 |
| C0 | ASTM D6641/D6641M, warp along the load | compressive strength | F1c |
| C90 | ASTM D6641/D6641M, fill along the load | compressive strength | F2c |
| S45 | ASTM D3518/D3518M, ±45 tension | shear strength (at failure or 5% shear strain), shear modulus | F6, G12 |

That gives 15 conditions: three materials times five tests. Every panel also yields:

- cured ply thickness, which closes t_ply;
- areal mass per ply (panel mass divided by area and ply count), which closes areal_mass;
- fibre volume and void content (section 6).

**The row-77 closures:**

- **B5-CPW-T0** closes `carbon3k_mgs418_wet` E1, F1t and nu12.
- **B5-CPW-C0** closes F1c.

The results land as a new owner-test material set. The MGS 418 proxy keeps its nulls (section 9).

**Which Block 3 gates this feeds:**

| Block 3 item | inputs | conditions |
|---|---|---|
| Strength gate (M3.4, M3.5) | all nine lamina strengths and moduli, for BID, UND and CPW | all 15 |
| EI, GJ and stiffness deltas (reported) | E1, E2, G12, nu12, t_ply | T0, T90, S45, panel thickness |
| Mass placement and mass deltas | areal_mass, t_ply | panel mass and thickness |

**What the coupons do not close:**

- `glass_unvalidated`: that is kernel validation against NCAMP (plan T5).
- The cell geometry flags: the cap depth, the web position and the chord conflict.
- `criterion_unavailable` (Report 45).

So the strength gate will still read `blocked` after the coupons, until those clear too. The
coupons remove the material reasons only.

### Compression is in; short-beam shear is out

**Compression (D6641) is needed.**

- Tsai-Wu takes F1c and F2c directly.
- The canard's top cap is in compression under positive bending.
- Compression is the classic weak direction for carbon, and the reason carbon matched for stiffness
  may still fail strength (spec §9).
- AGATE gives a fill-direction compression value only for MGS 418 carbon. Nothing gives warp
  compression, and nothing gives either direction for the book cloths.

**Short-beam shear (D2344) is not needed for any gate.**

- It measures interlaminar shear. The ASTM summary calls it resin- and interlaminar-dominated and
  suitable for quality control and process specification.
- The M3.4 failure criterion is in-plane first-ply failure, so no gate input comes from it.
- It is cheap: no tabs, small loads, a three-point fixture. That makes it a good process-control
  check once Block 4 fixes the build process.
- It is listed as optional (section 11) and is not in the counts.

## 3. Laminates and panels

**Every panel is laid with the fabric axes aligned to the panel edges.** These are lamina tests, so the
book's ±45 skin orientation is applied later in the laminate model, not in the coupon.

| panel | plies | size (mm) | yields |
|---|---|---|---|
| PT, tension | 8 at 0 (warp along the 600 side) | 600 × 300 | T0 strips from one 300 × 300 half, T90 strips from the other |
| PC, compression | 12 at 0 (UND: 14) | 350 × 300 | C0 and C90 zones |
| PS, shear | fabric: 8 plies cut at 45; UND: [+45/-45]2s | 300 × 300 | S45 strips |

- **Ply counts** follow D3039's thickness guidance of about 2 to 2.5 mm, and the D6641 buckling check
  in section 5.
- **Cure batches.** Each material gets a PT, a PC and a PS panel in each of two independent cure
  batches, A and B, which makes 18 panels. "Independent" means a separate resin mix, a separate bag,
  a separate day, and a separate post-cure run.
- **Rehearsal panels.** One PT-size rehearsal panel per material is laid first to practise the process.
  It is not tested for record.

### Process

Every value here is a process parameter. The build must use the same value, or the coupons do not
describe the build. Each is registered in the predictions row before the first panel (section 8).

**Resin.**

- MGS LR 285 with hardener LH 287, mixed 100:40 ± 2 by weight (L285 technical data sheet, Hexion,
  March 2010).
- LH 287 is chosen for its long pot life: a 5 to 6 h gel time at 20 to 25 °C (TDS). A 14-ply panel
  must be laid and bagged by one person well inside the pot life.
- If the build uses LH 285, that is a different condition and needs its own batches.

**Layup.**

- The shop temperature is 20 to 30 °C. The TDS gives 20 to 40 °C as the optimum, and pot life halves
  for every 10 °C rise. Shop temperature is logged.
- The panels are laid on a waxed tool plate with a PVA release coat.
- Each ply is wet out and squeegeed, and the resin and cloth masses going in are recorded.

**Bag schedule, from the laminate out:**

1. release-coated nylon peel ply;
2. perforated release film;
3. one layer of 4 oz polyester breather;
4. nylon bag film, sealed with sealant tape;
5. the through-bag port at one end and a gauge port at the far end.

The breather is weighed before and after, so the bled resin mass is known.

**Vacuum.**

- The target is 20 inHg (about 68 kPa below ambient), ± 1 inHg, read at the gauge port.
  - This is an unsourced captain choice. A wet layup has no resin control other than the bleed, and
    full vacuum through perforated film can starve the laminate.
  - The build adopts the same value, or these coupons do not describe it.
- The vacuum is held from bag closure until the 24 h room-temperature cure ends. It is logged at
  least hourly; a gauge reading photographed with a timestamp is acceptable.
- **Leak check, on the dry bag, before any resin is mixed:** pull to the target, isolate the pump,
  and require a drop of 1 inHg or less in 5 minutes. This is an unsourced captain choice.

**Book glass in the new process.** The book laid its glass by hand with no bag. The coupons bag the
glass too, so one process is learned and the book denominators come out as high as they can.

- **Why that is conservative.** Strength and stiffness are fibre-dominated per ply. A bagged ply
  carries the same fibre, in less resin. The book denominators of the strength and stiffness ratios
  should therefore come out equal or higher, never lower. Carbon must then beat a book that is at
  least as strong as the airplane's real one.
- **The exception is the matrix-dominated values** (F2t, F2c, F6). For those the direction is not
  proven.
- **The check.** The optional unbagged BID condition (section 11) measures the difference. Whether
  to run it is Ryan's call.

### Cure and post-cure

| step | value | source |
|---|---|---|
| Room-temperature cure | 24 h at 20 °C or above, under vacuum, shop logged | TDS reinforced-data cure: 24 h at 23 °C |
| Debag, then post-cure | 15 h hold at 80 °C | TDS reinforced data: cured 24 h at 23 °C plus 15 h at 80 °C. The TDS states the 80 °C treatment for the German motor-plane approval, -60 to +72 °C, but prints no hold time for it; the 15 h comes from the reinforced-data footnote. |
| Ramp up | 10 °C/h or slower, room temperature to 80 °C (about 6 h) | unsourced captain choice. The TDS gives no ramp. A slow ramp keeps the part near its rising Tg so a flat panel does not sag. |
| Hold band | every panel thermocouple within 77 to 83 °C for the full 15 h; air overshoot no more than +5 °C | unsourced captain choice. A lower hold gives a lower Tg, so the band the coupons claim is the band the build oven must hold. |
| Cool down | 10 °C/h or slower, to below 40 °C, before the oven is opened | unsourced captain choice |
| Support | each panel flat on an aluminium caul, unrestrained | |

**Thermocouple record.**

- Three type K thermocouples go on the panels of each run, spread across the load, at the centre and
  at opposite corners. One more reads air at panel height.
- The logger samples once a minute or faster.
- The combined thermocouple and logger error must be within ±1.5 °C. It is checked at the ice point
  and in boiling water before each campaign, with the local boiling point corrected for altitude.
  - This is an unsourced captain choice. The type K tolerance in ASTM E230 was not read; do not rely
    on a datasheet tolerance in its place.
- The log file for each run is kept with the batch record. A run with any panel thermocouple outside
  the band for more than 15 minutes is a failed cure. Its panels are re-made, not tested.

**Oven requirement.** This is the hand-off to the oven search. The oven must:

- hold 80 °C within the band above over a working zone that takes the batch's nine panels: either
  0.7 × 0.7 m of floor, or three shelves that each take 600 × 350 mm flat;
- have a programmable ramp-and-soak controller;
- reach 80 °C from room temperature with the ramp set to 10 °C/h.

A kiln that also reaches 565 °C serves the glass burn-off (section 6). That temperature is the usual
ignition value; it was not read from ASTM D2584 or D3171.

## 4. Specimen counts and statistics

**Count per condition:** 10 cut (5 from each cure batch), 8 tested (4 per batch), 2 spares.

- The spares replace invalid failures: a failure in the grip or tab, or within one width of the grip.
- The floor is 6 valid results with at least 2 per batch. D3039's minimum is five per condition
  (secondary read: Forney).
- Below the floor, the condition is re-run with a new batch.

**Totals:**

- 150 specimens cut, and 120 tested in the baseline.
- 18 record panels plus 3 rehearsal panels.
- 3 fibre-volume and void samples and 3 density samples per record panel, which is 108 small samples.

**Why 8 from 2 batches.** It mirrors the sample used for an equivalency check against a qualified
database: a minimum of 8 strength specimens from 2 separate panels and processing cycles. The source
is NCAMP NCP-RP-2010-001, which follows CMH-17-1G §8.4.1 and DOT/FAA/AR-03/19 §6.1 (secondary; the
AR-03/19 report itself was not read).

- **No equivalency claim.** L285 wet layup has no qualified database to compare against, so this plan
  makes no equivalency claim.
- **What it does buy.** The sample has a recognised structure, and it gives a first look at
  cure-to-cure variation. For wet layup that variation is probably the largest scatter source.

**What is reported per condition:**

- n, mean, standard deviation and CV;
- the batch A and batch B means;
- a **single-lot estimate**, x̄ − kB·s, labelled exactly that:
  - kB is the one-sided normal B-basis factor: 2.583 at n = 8, 2.756 at n = 7 and 3.007 at n = 6.
  - These were read from NCAMP NCP-RP-2008-004 Rev B Table 2-1, which quotes CMH-17-1G (secondary).
  - A batch-mean difference larger than the scatter explains is reported. The lower batch's
    statistics then govern.

**How the gates use them.** The ratio gates are computed twice: once on the means and once on the
single-lot estimates. A ratio passes only if it reaches 1.0 or more both ways.

- **Means** give a like-for-like comparison: the same resin, process, lab and conditioning.
- **The estimates** penalise the material with more scatter, which is the honest direction.

**Knockdown for absolute use.** The ratio gate is RTD-only and needs no knockdown, because both sides
saw the same environment. Any absolute use (part margins, proof-load sizing) takes the single-lot
estimate times 0.8 on the matrix-dominated values F2t, F2c, F6 and F1c.

- The 0.8 is an unsourced captain choice, standing in for the hot/wet tests this plan does not run.
- The L285 TDS shows Tg falling 5 to 15 °C after conditioning at 40 °C and 90% RH, so the
  environment is not free.
- Fibre-dominated values take the estimate unchanged.

### What full B-basis would cost, and what the gates can claim without it

A CMH-17 B-basis needs at least **3 batches and 18 data points per condition**. That is NCAMP's
statistical report quoting CMH-17-1G (secondary). With only 3 batches, the ANOVA values are labelled
estimates. A CMH-17 batch is a material lot, here a fabric lot plus a resin lot, not a cure.

- **Cost.** Full B-basis means 15 × 18 = 270 tests against 120, about 2.25 times the specimens and lab
  fees. It also needs three certified lots of each cloth and of the resin. A distributor ships
  whatever lot it has, so lot control means asking for lot certificates and buying on three
  occasions (not verified as possible).
- **Hot/wet.** Adding hot/wet conditions would roughly double the count again.
- **Out of reach.** For one person that is out of reach for now.

**What the gates can claim on this plan:**

- "Carbon is at least as strong and as stiff as the book laminate, at room temperature and dry, on
  means and on single-lot estimates."
- The coupons are owner-made, lab-tested and flagged owner-generated.

**What they cannot claim:**

- B-basis allowables;
- environmental (hot/wet) allowables;
- lot-to-lot variation;
- fatigue;
- damage tolerance;
- any absolute margin without the 0.8 knockdown and the part proof tests of Block 5.

### What an outside reviewer would likely accept

This has not been asked of any reviewer; asking is outward contact and is Ryan's call. For an
amateur-built aircraft the coupons are evidence, not certification. A structures reviewer would most
likely want the following.

1. **Process.** A written process spec that the coupons and the build both follow, plus a cure record
   (a thermocouple log and a vacuum log) for every batch.
2. **Testing.** Tests run by a lab with a load frame calibrated to ASTM E4, ideally an ISO/IEC 17025
   lab, with raw load and strain files, a failure-mode code and a photo for every specimen.
   - An owner-run frame without E4 calibration would likely be discounted.
   - The lab route is the recommendation for the record tests (section 10).
3. **Panel quality.** Fibre volume and voids reported for every panel, with the acceptance limits
   fixed in advance (section 6).
4. **Predictions.** Predictions registered before the test (section 8), so the results were not tuned.
5. **Part evidence.** Part proof tests. Coupons qualify a material and process, not a structure, and
   the roadmap's Block 5 proof-loads every primary part.

## 5. Specimens

Almost everything here is a secondary read, because the ASTM standards are paywalled. Values marked
NOT READ must be checked against a purchased copy of the standard before any panel is cut. Buying the
three standards (D3039, D3518, D6641) is a Ryan decision.

| condition | specimen L × W (mm) | thickness | tabs | source |
|---|---|---|---|---|
| T0 and T90 (BID, CPW) | 250 × 25 | 8 plies, about 2 to 2.2 mm | emery cloth, or bonded G-10 56 mm long × 1.6 mm | MTS TechNote and Zwick (secondary): for fabric, abrasive cloth or bonded tabs |
| T0, UND | 250 × 15 | 8 plies, about 1.8 mm | bonded G-10, 56 × 1.6 mm, bevelled | MTS and Zwick (secondary). Bevel angle NOT READ (Zwick allows 7 to 90 degrees). |
| T90, UND | 175 × 25 | 8 plies, about 1.8 mm | bonded G-10, 25 mm long, straight (90 degrees) | MTS and Zwick (secondary) |
| C0 and C90 | 140 × 13, 13 mm gauge | 12 plies (UND 14) | untabbed for BID, CPW and UND C90; G-10 1.6 mm tabs for UND C0 | ASTM summary: untabbed suits low-orthotropy laminates. Geometry from CompositesWorld (secondary). |
| S45 | 250 × 25 | 8 plies | as T0 for the same material | MTS (secondary); ply-count rule NOT READ |

**The D6641 thickness check.** The buckling formula used is h ≥ ℓ / (0.9069 · √[(1 − 1.2σ/Gxz)(E/σ)]).

- The formula was read in CompositesWorld (secondary); its wording in the standard was not read.
- The inputs were ℓ = 12.7 mm and Gxz = 3 GPa (assumed); σ and E were taken from the load estimates
  in section 7. With a 20% margin the minimums come to:

| material | minimum thickness | plan |
|---|---|---|
| CPW | 2.0 mm | 12 plies, about 3.0 mm |
| BID | 3.0 mm | 12 plies, about 3.2 mm |
| UND | 3.0 mm | 14 plies, about 3.1 mm. 12 plies (2.6 mm) would fail the check, hence 14. |

**Test details.**

- **Tab adhesive.** It must be a toughened paste adhesive (section 10 of the purchase order). Neat
  L285 is too brittle for tabs. That is a captain judgment from common practice; it has not been
  tested.
- **Rate.** D3039 runs at 2 mm/min, or at 0.01/min strain rate (Zwick, secondary). The rates for D3518
  and D6641 are NOT READ.
- **CLC clamping torque** is 2.5 to 3.0 N·m per screw (CompositesWorld, secondary).
- **Modulus range.** The D3039 chord-modulus strain range is NOT READ: Element's blog says 1000 to
  6000 microstrain is common. Use the standard's range once it is read.
- **Strain is measured on:**
  - 4 of the 8 specimens in T0 and T90, with 0/90 rosettes or a biaxial extensometer (NCAMP's
    equivalency report uses 4 specimens for modulus);
  - every S45 specimen, because the 5% shear-strain cutoff needs strain. Foil gauges can debond
    before 5%, so an extensometer is preferred for S45.
  - C0 and C90 need no strain measurement: compression strength only, and modulus comes from tension.
- **Conditioning.** Specimens are tested RTD, as fabricated, after at least 40 h at 23 ± 2 °C and
  50 ± 5% RH. That is ASTM D618 Procedure A as quoted by a lab page (secondary); the D5229 wording
  was not read.
- **Specimen ids.** Each specimen is `B5-<material>-<condition>-<batch><n>`, for example
  B5-CPW-T0-A3. Panel ids are `B5-<material>-<PT|PC|PS>-<batch>`.
- **Cutting and marking.** Specimens are cut with a continuous-rim diamond blade, wet, and the edges
  are finished smooth. The panel id, position and fibre direction are marked before cutting.

## 6. Fibre volume and voids

| material | fibre volume | voids | density |
|---|---|---|---|
| BID, UND | burn-off: ASTM D3171 Procedure G or ASTM D2584 (ignition loss), 3 samples per panel | ASTM D2734, from the measured density, the resin density (1.18 to 1.20 g/cm3, TDS) and the E-glass density (from the fabric maker's datasheet, NOT READ yet) | ASTM D792, 3 per panel |
| CPW | ASTM D3171 Method II: areal weight, ply count, fibre density and cured thickness | not available from Method II. At the lab, D3171 Method I by matrix digestion. Owner fallback: a polished cross-section count, which is not an ASTM method and is labelled so. | ASTM D792, 3 per panel |

- D2584 applies only when glass is the sole reinforcement, so carbon cannot be burned off in air (ASTM
  summary).
- The fibre densities must come from the fibre makers' datasheets and be registered before use.

**Acceptance.** These limits are fixed now, before any panel exists, as unsourced captain choices.

- Each panel's void content must be 4% or less. For scale, one wet-layup vacuum-bag glass study
  reported 3.4% (secondary).
- Each panel's fibre volume must be within 5 percentage points of its material's mean.
- A panel outside either limit is re-made before its specimens are tested.

## 7. Equipment and peak loads

**Peak-load estimates.** These are for sizing equipment only. They are not design data and are never
used as a prediction.

| condition | estimate (kN) | upper (kN) | basis |
|---|---|---|---|
| CPW T0 | 27.5 | 33 | L285 TDS reinforced data, carbon plain weave 200 g/m2: 510 to 550 MPa at 43% fibre volume (0.25 mm per ply); 8 plies × 25 mm |
| CPW T90 | 23 | 28 | AGATE 115 F2t 61,980 psi at t_ply 0.0104 in (MGS 418) |
| BID T0 | 25 | 38 | TDS glass 8H satin, 460 to 500 MPa (0.25 mm per ply). The upper value scales by the 7725 warp/fill difference: vendor tow count 54 × 18 and dry break 440/366 lbf/in. |
| BID T90 | 21 | 32 | as above × 366/440 |
| UND T0 | 22 | 27 | rule of mixtures: effective fibre strength 2,000 MPa (2,400 upper) over a 0.0925 mm fibre-equivalent thickness per ply (236 g/m2 warp ÷ 2.55 g/cm3); 8 plies × 15 mm. The fibre strength is a captain assumption. |
| UND T90 | 2 | 3 | transverse strength 40 MPa, captain assumption |
| CPW C0 and C90 | 20 | 24 | TDS carbon compression, 460 to 510 MPa; 3.0 × 13 mm |
| BID C0 | 18 | 24 | TDS glass compression 410 to 440 MPa (570 upper); 3.2 × 13 mm |
| UND C0 | 26 | 32 | 650 MPa (800 upper), captain assumption; 3.1 × 13 mm |
| UND C90 | 5 | 6 | 120 MPa, captain assumption |
| S45 (all) | 9 | 12 | P = 2τwt with τ up to 110 MPa |

**Load frame.**

- 100 kN class preferred. 50 kN is the minimum: the highest upper estimate, 38 kN, is 76% of it.
- It must be E4-verified.
- The load cell must also be verified at the low end. UND T90 fails near 2 kN, so the calibrated range
  must reach down to about 1 kN; check where the lab's E4 range starts.

**Fixtures.**

- **Grips:** wedge-action, mechanical or hydraulic, rated at the frame capacity, with 25 mm wide
  serrated faces opening to at least 7 mm. A tabbed UND specimen is about 1.8 + 2 × 1.6 = 5 mm thick.
- **D6641 CLC fixture:** 13 mm gauge, for 140 × 13 mm specimens. Its price was NOT READ.
- **Strain:** a biaxial clip-on extensometer, or 0/90 foil rosettes (350 ohm). D3518 needs strain out
  to 5% shear strain, so an extensometer, or validated digital image correlation, is preferred over
  foil gauges for S45.

**Panel equipment.**

- **Oven:** section 3.
- **Thermocouples and logger:** at least four type K channels, logging once a minute or faster, with
  the combined error checked to ±1.5 °C.
- **Vacuum:** a pump that holds 20 inHg on a sealed bag for 24 h. A two-stage rotary vane HVAC pump
  of about 5 cfm will do, with a resin trap, a bleed valve to set the level, and gauges at both ports.
- **Release and tools:** a tool plate (24 × 24 in, 1/4 in tempered glass or MIC-6 aluminium), wax and
  PVA.
- **Fibre volume:** a kiln to 565 °C and a 0.001 g balance (owner route only).

## 8. Predictions, frozen before any panel is cured

Before the first record panel is laid, the captain writes `data/validation/block5_coupon_predictions.yaml`
and registers its sha256 in a ledger row. A test pins the hash, as row 74 pins the M3.4 inputs.

**For each of the 15 conditions** the file gives a predicted mean, a band, and the source of both:

- **CPW T90, C90 and S45:** AGATE 115 (MGS 418) fill-direction and shear values. This is the
  cross-resin bridge. A result outside the band says L285 or the owner's process differs from
  AGATE's, and that is a finding.
- **CPW T0 and C0:** the L285 TDS plain-weave carbon row.
- **BID and UND:** rule of mixtures from the fabric datasheets, plus the TDS glass row.
- **The process limits** (section 3) and the acceptance limits (section 6).

**The rules once results arrive:**

- A miss outside the band gets a new row as a finding. Bands are never widened after a result is seen.
- Results are not used to choose which panels count: panel rejection runs on the void and fibre-volume
  limits only.

## 9. How results flow back

1. **Raw records.** Each specimen's dimensions, failure code, photo id and reduced curve go under
   `data/coupons/b5/<condition>/`. The lab's raw files are kept privately if they carry lab or
   personal details. Only numbers are committed.
2. **Reduction.** A pure reduction function (in `core/`, tested on a fixture first) computes each
   condition's statistics. A script writes a canonical report. The report is registered as a source
   (for example `b5-coupons-r1`), so a property can cite it as `<id>:p<n>`.
3. **New material sets.** Results go into `data/materials.yaml` as new sets, `bid_7725_l285_b5`,
   `und_7715_l285_b5` and `cpw3k_l285_b5`.
   - Their `use` is `owner-test`. That is a new use value, added under its own row.
   - Each property cites the report and records n, CV and basis (`mean` or `single_lot_estimate`).
   - The owner-generated flag travels with every gate that reads them.
4. **Re-freeze before the run.** One row re-points the sizing rule's carbon material and the book
   lamina, and re-records the input hashes. That happens before any carbon number is computed, as row
   74 required.
5. **The proxy keeps its nulls.** `carbon3k_mgs418_wet` keeps `requires_original_test` and its nulls.
   It is MGS 418, and the coupons are L285. The flag records that the public record has no warp
   value, which stays true.

## 10. Testing route

**Recommendation.** The owner makes every panel and specimen: the process is what is being qualified,
so this cannot be outsourced. A lab with an E4-calibrated frame runs the record tests (section 4,
reviewer item 2).

**Owner testing.** An owner frame would need:

- a frame;
- grips;
- a CLC fixture;
- an extensometer or rosettes;
- E4 verification.

That is worth it only if Block 5's part proof tests need the same frame. Decided 2026-11-01: no owner test frame unless Block 5 part proof tests need one.

**Testing labs.** None of the candidates below was contacted. Decided 2026-11-01, on merit as recommended above: the owner makes every panel and specimen, a lab with an E4-verified frame runs the record tests, and the university materials facility is the first lab to ask. Contacting labs and spending stay the owner's action.

- **Primary candidate: a university materials characterization facility** with a published external
  rate of about $124/hr for an Instron 34TM-50. Open questions:
  - Does the 50 mean 50 kN? If it does, is that enough? The section 7 estimates peak at 38 kN, and
    50 kN is the minimum this plan accepts.
  - Does it have wedge grips suited to composite specimens, and a CLC fixture or a way to mount one?
  - Does it hold E4 verification, and does the calibrated range reach down to about 1 kN for UND T90?
  - Is a strain extensometer available, and is ISO/IEC 17025 status held?
- **Secondary:**
  - a university structures lab that takes industry work;
  - commercial testing labs, none of which published coupon pricing;
  - a commercial thermal-analysis lab, which could run a Tg check (DMA or DSC) on the post-cure to
    confirm the 80 °C cure reached the expected Tg.
- Per-specimen prices for D3039, D6641 and D3518 are not known for any candidate.

**Oven.** No rentable oven was found locally in public research. Kiln controllers can program low
holds, but their uniformity at 80 °C is unproven. The recommended route is an owner-built hot box
(insulated enclosure, heater and fan, PID controller with SSR, and the existing thermocouple logger),
sized for the section 3 working zone. Its parts list is in the purchase order, lines 35 to 42, at
about $339 before shipping and tax, all prices unverified. **Before any panel is cured,** an empty-box
survey at 80 °C across the working zone must show every position within ±3 °C (the section 3 band) or
tighter. A member or shop oven would need the same survey.

## 11. Optional conditions (not in the counts)

- **D2344 short-beam shear,** per material: process control. Cheap; recommended once Block 4 fixes the
  build process.
- **B5-BIDH-T0:** BID laid by the book's unbagged hand process, against B5-BID-T0. It measures how
  much bagging raises the book denominator (section 3).
- **3K 2×2 twill carbon,** about 5.7 oz: a drape alternate. A UD carbon (about 9 oz) for caps would
  need a new sizing-rule row, since the rule allows only the plain-weave set.
- **Hot/wet conditions:** they replace the 0.8 knockdown with data.

## 12. UL94 fuel immersion (tank interior resin)

Status: draft addition, 2026-10-20. Paper only: nothing is bought, booked, or cured from this section. These specimens sit outside the section 4 totals and outside the 18 record panels.

### Purpose

This section closes the open tank-resin question for UL94. The build keeps one laminating resin, MGS L285 with hardener 287, on the fuel-wetted strake interior and on the aft side skins, and the engine is a Rotax 912 iS on ethanol-free UL94. No immersion opened for this note clears that resin in UL94, and none shows that a replacement is required (`docs/research/2026-10-20-ul94-tank-resin.md`, 20 October 2026). The comparison resin is E-Z 10A with E-Z 87B. The result is a keep-or-change rule for those wetted layups. It is written below, before any panel is laid. Ethanol-blend mogas is outside this section.

### Methods opened, and the one this test uses

The record exposure is the finished-laminate soak in PAFI-MTP-002 §19.3: 28 days, room temperature, in the candidate fuel and in high-aromatic 100LL. The tank is a cured BID laminate, so that is the article under test. The neat-resin screen in §19.1 is a different article (no cloth, 5 days, 60 °C). It is described in the table so the choice is visible. It is not run.

D543, D570, and D5229 were opened because they are the general immersion and absorption methods. None of them prints a pass limit for avgas in a wet-layup tank. SAE J1681 is named by D543 and was not opened. No MIL method for a composite tank laminate was opened. ISO 175 is named by D543-21 and was not opened.

| method | what was opened | specimen | exposure | measures | pass limit |
|---|---|---|---|---|---|
| ASTM D543-21, practices for chemical resistance of plastics, including laminates | ASTM product page, scope and §4. PDF text through the first sentence of Procedure I, §11.1. The rest of the 8-page PDF did not come through. Duration in the -21 text is UNCONFIRMED. | At least 3 per material, reagent, time, and strain (§9.1). Weight and dimensions: molded disk 50.80 mm diameter by 3.175 mm, or a sheet bar 76.20 by 25.40 mm by the sheet thickness (§9.1.1.1, §9.1.2.1). | Condition at least 40 h at 23 ± 2 °C and 50 ± 10 % RH (§10.1). Immersion is the procedure when the part is a container (§1.2). §4.1 calls the duration, the temperature, and the reported properties arbitrary. | Weight, dimensions, appearance, colour, strength, other mechanical properties (§1.2). Laminates: thickness at the centre and at the edges when the edge swells (§11.1, sentence opened). | None in the opened sections. |
| ASTM D543-06, same title, older edition | A copy not hosted by ASTM, procedures opened. | Same family of practices. At least three specimens in the -21 text above. | Procedure I: 7 days (168 h) in the standard laboratory atmosphere, specimen suspended, reagent stirred every 24 h. Other times, if agreed: 24 h, 72 h, then 4-week steps. Practice B, if used: 7 days at room temperature, or 3 days at elevated temperature, unless agreed otherwise. | Procedure II: mechanical properties of immersed and unexposed specimens from the same lot, tested immediately after removal. Tensile is the usual property. Flexure is allowed when surface attack matters. | None printed in the opened procedures. |
| ASTM D570-22, water absorption of plastics | iTeh sample, approved 1 September 2022, published September 2022. Procedures after the start of the 24 h immersion were past the sample. Those later procedures are UNCONFIRMED. | Three specimens (§7.1). Molded disk 50.8 mm by 3.2 mm. Sheet bar 76.2 by 25.4 mm by the thickness. | Distilled water, 23 ± 1 °C, 24 h, specimen on edge and fully immersed (§8.1, opened). This method is water. | Weight to 0.001 g after wiping. The significance section also names dimensions, appearance, and strength as reasons for the test. | None in the opened text. |
| ASTM D5229/D5229M-12, moisture absorption and equilibrium conditioning of polymer-matrix composites | Full text opened, approved 1 February 2012, published June 2012. ASTM D5229-20 was not opened. Identity with the 2020 edition is UNCONFIRMED. | Mass at least 5.0 g (§8.2.2). No minimum thickness. Procedure A uses a thin coupon and a thick coupon; three replicates are recommended. Procedures B–E weigh at least three specimens or three travelers. | Includes a non-water fluid, to equilibrium (Procedure BFEP) or for a fixed time (Procedure BFFF). Table 3 prints no default temperature for those two fluid procedures. | Average moisture content from successive masses. Effective equilibrium: change under 0.020 % across each of two consecutive reference periods, and the mass-versus-square-root-of-time plot agrees (§10.2). | None. The 0.020 % figure is the equilibrium definition, not a fuel pass limit. |
| PAFI-MTP-002 Rev 0, 15 May 2024, FAA PAFI materials test plan | Public PDF text opened for the preface, §1, objective 16, §19, §23.8, and Appendix I. | Neat resin: at least 3, five preferred; size set by the Tg instrument; a separate about 1 in square piece for weight and density (§19.1.2). Finished laminate, per fluid: five tensile, five short-beam, five V-notch, five lap-shear where adhesives are in the matrix, plus five unexposed of each (§19.2.14 to §19.2.17). Travelers 1 by 3 in, three per exposure recommended (§19.2.13). | Neat resin, §19.1.3: 5 days at 60 °C in Reference Fuel B, high-aromatic 100LL, the candidate fuel, and air. Finished laminate, §19.3: 28 days, room temperature, specimens suspended, jars topped up, no fuel exchange. §19.3 prints no numeric room-temperature band. | Neat: weight, density, Tg, visual (§19.1.4). Finished: dimensions, hardness, density, visual, tensile, short-beam, V-notch (§19.2 and objective 16). Objective 16 names weight gain, tensile, elongation, and break strength. | §23.8.1, neat resin: a property change that is statistically different and greater than 10 % from the 100LL set is a fail. §23.8.2, finished composite: the same 10 % test on median hardness, tensile, elongation, V-notch, or short-beam. Objective 16: those changes no greater than with 100LL. §23.8 does not name the statistical test. |
| ASTM D471, rubber in liquids, as cited by PAFI | PAFI §12.1.1 states Reference Fuel B as 70 vol % isooctane and 30 vol % toluene, and points at Table 4 of D471 revision 16a. That 16a table was not opened. D471-98e1 was opened; there the same blend is Table 3. Whether 16a moved the table is UNCONFIRMED. | A rubber method. PAFI uses the fuel, not the rubber coupon, for the resin screen. | PAFI puts Reference Fuel B in the neat-resin screen (§19.1.1), not in the §19.2.1 finished-laminate materials list. | PAFI also cites D471 for density change on the resin screen. | The rubber limits in D471 were not used. |
| SAE J1681 | Named in D543-21 §2.5 as gasoline, alcohol, and diesel surrogates for materials testing. The SAE text was not opened. Specimen size, duration, and any pass limit are UNCONFIRMED. | | | | |
| MIL | D543-21 §2.2 lists military fluids as reagents, including MIL-G-5572 aviation gasoline. No MIL immersion method for a composite tank laminate was opened. | | | | |
| ISO 175 | Named in D543-21 Note 2. The ISO text was not opened. D543-21 says the technical content differs, so the results cannot be compared directly. | | | | |

High-aromatic 100LL, for every PAFI comparison in this section, is the fuel in PAFI §1: 15 % toluene by volume, minus 0 % plus 3 %, measured by ASTM D3606, with the other ASTM D910 Table 1 properties met. Pump 100LL is a different fuel. The test does not start on pump 100LL.

### Resins and laminate

Both panels are the build's BID, style 7725, eight plies at 0, warp along the 600 mm side. The bag, the 20 inHg vacuum, the leak check, and the shop log are section 3. The fuel coupons then describe the same process as the build. One panel per resin. One cure batch per resin. Section 4's two-batch sample is for lamina allowables. It is not applied here. That is an unsourced captain choice.

| item | MGS panel | E-Z panel | source |
|---|---|---|---|
| Resin | MGS L285 with hardener 287, 100:40 ± 2 by weight | E-Z 10A with E-Z 87B, 100:44 by weight | MGS: this plan, section 3. E-Z: Endurance bulletin, revised August 2007, as read in `docs/research/2026-10-20-ul94-tank-resin.md`; the bulletin prints no mix tolerance |
| Room cure | 24 h at 20 °C or above, under vacuum | 3 days at 25 °C, supported. The panel is held at 23 to 27 °C for those 3 days | MGS: section 3. E-Z duration and 25 °C: the same bulletin. The ±2 °C band is an unsourced captain choice |
| Post-cure | 15 h at 80 °C, ramp and cool-down as section 3 | 4 h at 66 °C (150 °F). Ramp and cool-down use the section 3 rates, 10 °C/h or slower. Hold 63 to 69 °C | MGS: section 3. E-Z time and temperature: the bulletin, which also says the post-cure is unsupported. The ramp and the 63 to 69 °C band are unsourced captain choices. The bulletin does not tie this 4 h schedule to the 196 °F Tg column |
| Support | Flat on an aluminium caul, unrestrained | Same caul, unrestrained. The bulletin's word is unsupported | Caul: section 3. Using it for E-Z is an unsourced captain choice so the panel stays flat |
| Panel | `B5-BID-UL-MGS`, 600 × 300 mm | `B5-BID-UL-EZ`, 600 × 300 mm | Size matches the section 3 tension panel, so the bag and the oven survey cover it. One panel, rather than a PT in each of two batches, is an unsourced captain choice |
| Mixing temperature | Section 3 shop, 20 to 30 °C | Bulletin: material temperature not below 65 °F (18 °C) at mixing. The section 3 shop satisfies that floor | Bulletin, via `docs/research/2026-10-20-ul94-tank-resin.md` |

PAFI Appendix I lists EZ10A with EZ87B, and L285 with H287 and with H285. Its table calls H287 a fast cure and H285 a slow cure. Section 3 of this plan has the opposite gel times (H287 about 5 to 6 h, H285 about 2 to 3 h, 1 mm film, 20 to 25 °C). This section does not use PAFI's speed names. The hardener on the MGS panel is 287, because that is the build hardener.

The green highlighting in Appendix I was not visible in the text extract. Which rows are green is UNCONFIRMED. The prose that requires finished-composite testing names L285 with H285 twice, Hexion 8014 with TETA, and Derakane 470-350 (§19.1.4). It does not, in that sentence, name H287.

### Exposure

| item | value | source |
|---|---|---|
| Fluids | UL94, as the candidate fuel. High-aromatic 100LL, as §1 defines it. Air, the unexposed set, stored in the same cabinet | §19.1.3 puts air with the neat-resin fluids. §19.2.14 requires an unexposed baseline for the finished-laminate properties. Both are used here |
| Reference Fuel B | Not in this exposure | §19.1.1 includes it for neat resin. §19.2.1 does not list it for the finished laminate |
| Duration | 28 days | §19.3. Objective 16 states the same 28 days at ambient for the composite matrices |
| Temperature | 23 ± 2 °C, logged at least daily | §19.3 says room temperature and prints no band. The band is D543-21 §10.2, adopted because the PAFI sentence has no number. Adopting it is an unsourced captain choice |
| Jars | One resin per jar. Tensile, short-beam, and traveler coupons of that resin may share the jar. Specimens suspended, not piled on the glass. Fill to one marked level. Top up with the same fuel. No fuel change | §19.3 |
| Cabinet | Flammables cabinet. Fuel kept out of sunlight | §19.3 for the cabinet. §1 tells the lab to limit light on 100LL because lead can precipitate. The same dark storage is used for the UL94 jars. Extending that sentence to UL94 is an unsourced captain choice |
| Rinse | Blot with a lint-free cloth. No solvent rinse | §19.4 says to repeat the pre-exposure measurements. A solvent rinse is printed for hoses, not for §19.4. Skipping it is an unsourced captain choice |
| Clock | This is a fixed 28-day exposure, not a D5229 equilibrium stop | §19.3. D5229 §10.2 would hold the coupons until the mass change stayed under 0.020 %. That is a different test |

Condition the cut specimens at least 40 h at 23 ± 2 °C and 50 ± 5 % RH before the first weighing. That is the section 5 conditioning. D543-21 §10.1 allows 50 ± 10 % RH. The tighter band is the one already written for the other coupons.

### Measures

Travelers, tensile coupons, and short-beam coupons are three separate sets. A traveler is not loaded.

| set | size | measured | source |
|---|---|---|---|
| Traveler, `W` | 25 by 76 mm (PAFI's 1 by 3 in) | Mass to 0.001 g. Length and width. Thickness at the centre and at one edge. Photograph, both faces, before and after, with the specimen id in the frame | Size: §19.2.13. Edge thickness: D543-21 §11.1, for laminates. The 0.001 g place is D570-22's opened weighing place, used here for a fuel mass. The traveler must weigh at least 5.0 g or it is lengthened until it does (D5229 §8.2.2) |
| Tensile, `T` | 254 by 25.4 mm, tabs at test time | Tensile strength and elongation at break. Strain on every coupon. Modulus is recorded and is not a gate | PAFI §19.2.14 prints 2.54 cm by 25.4 cm. Objective 16 names tensile, elongation, and break strength. Section 5's 250 by 25 mm lamina coupon is a different population and is not pooled with these |
| Short-beam, `S` | 38 by 13 mm (PAFI's 1.5 by 0.5 in) | Short-beam strength | §19.2.15. The span, the nose radius, and the rate inside ASTM D2344 were not read. Strips are not cut until D2344 is in hand. Same rule as the NOT READ cells in section 5 |

Hardness (PAFI cites ASTM D2583) and V-notch shear (ASTM D5379) are in §23.8.2. Those two standards were not opened. They are not gates in this section. A keep closes mass, tensile strength, elongation, short-beam strength, and appearance only.

Tabs. Emery cloth in the grips, fitted when the specimen is mounted, which is the section 5 option for BID fabric. Bonded tabs are not used on the soaked set, so the coupon can be broken immediately after blotting. Immediate testing is D543-06 Procedure II. Choosing emery cloth so that "immediately" can be met is an unsourced captain choice. A grip failure or a failure inside one width of the grip is invalid, as in section 4, and the spare replaces it.

Weigh and measure every traveler within 5 minutes of blotting. The 5 minutes are an unsourced captain choice. D543-06 says to weigh immediately and prints no minute limit. Break the strength coupons the same day, after blotting.

Ids. `B5-BID-UL-<MGS|EZ>-<UL94|100LL|AIR>-<T|S|W><n>`. Example: `B5-BID-UL-MGS-UL94-T3`.

### Counts

Five valid results per strength cell is the PAFI minimum (§19.2.14, §19.2.15). Three travelers per fluid is the §19.2.13 recommendation.

| per resin | cut | tested | note |
|---|---|---|---|
| Tensile, three fluids | 18 (6 per fluid) | 15 (5 per fluid) | 1 spare per fluid |
| Short-beam, three fluids | 18 | 15 | 1 spare per fluid |
| Travelers, three fluids | 9 | 9 | no spare |

Two resins: 72 strength coupons cut, 60 tested, 18 travelers, 2 panels. A strength cell with fewer than five valid results is remade before the decision. A traveler that is dropped or chipped is replaced from the same panel's leftover if the leftover was cut and conditioned with the set. Otherwise that fluid's traveler set is remade.

Report, per cell: n, median, minimum, maximum, and the mass change of each traveler as a percent of its own conditioned mass. Means are reported beside the medians. The decision uses medians, because §23.8.2 says median.

### Decision rule

This rule is fixed before the first panel is laid. It is not revised after a result is seen.

Score each resin on its own. The UL94 set is compared with that resin's high-aromatic 100LL set, and each fuel set is compared with that resin's unexposed set.

A numeric row fails when both of the following are true. The absolute gap between the UL94 median and the 100LL median is greater than 10 % of the absolute value of the 100LL median. The two ranges do not overlap. The 10 % is §23.8.2 for tensile strength, elongation, and short-beam, and §23.8.1 for weight on neat resin. Using that 10 % on a laminate traveler's mass change is an unsourced captain choice. Objective 16 says the weight gain shall be no greater than with 100LL and prints no percent. Requiring a non-overlapping range is an unsourced captain choice standing in for the words "statistically different," because §23.8 names no test.

If the median gap exceeds 10 % and the ranges overlap, that cell is repeated once, on a new panel of the same resin and the same cure schedule. A second overlap fails the row. The one repeat is an unsourced captain choice.

If the 100LL median mass change lies within 0.020 percentage points of zero, the mass row uses 0.020 percentage points in place of that median as the denominator. The 0.020 figure is the D5229 §10.2 equilibrium criterion. Using it as a floor, so the ratio is defined, is an unsourced captain choice.

A tensile, elongation, or short-beam row also fails when either the UL94 median or the 100LL median is below 90 % of that resin's unexposed median. The 90 % is an unsourced captain choice. It applies the same 10 % figure against the air set. §23.8 compares the candidate fuel with 100LL and does not print a retained fraction against air for the finished laminate.

Appearance fails when a UL94 specimen shows a crack, a blister, or a ply separation, and no 100LL specimen of that resin shows the same feature. That sentence is an unsourced captain choice. §19.4 requires the inspection and prints no visual limit for composites.

**Keep MGS L285/H287, including the fuel-wetted strake interior and the aft side skins, only if every MGS row passes.**

E-Z is scored on the same rows. It does not have to beat MGS. A passing MGS stays the one resin even when E-Z takes up less fuel.

If MGS fails a row and E-Z passes every row, the fuel-wetted layups are E-Z 10A/87B on the cure in this section, and the unwetted structure stays MGS. Limiting the change to the wetted layups is an unsourced captain choice.

If both resins fail, this test has not cleared a bare tank interior. It does not choose a lining or a third resin.

### Test fuel

UL94 for the jars comes from Swift Fuels. The opened FAQ, page undated, retrieved 20 October 2026, says UL94 is ASTM D7547 avgas with a 94-plus motor octane number, without tetraethyl lead, and calls it ethanol-free. The same FAQ says UL94 has been produced and sold solely by Swift from its Indiana facility since 2015, and that an airfield buys it by Swift's order form. Swift then quotes and arranges shipping. UL94 is stored in an airport tank independently from 100LL. The order-form URL returned a loading shell and no form fields, so the form itself is UNCONFIRMED: `https://www.swiftfuelsavgas.com/order-form`. The FAQ is `https://www.swiftfuelsavgas.com/faq`, heading "How can my airfield buy UL94 Unleaded Avgas?" and the heading "What is UL94 Unleaded Avgas?".

No page opened here sells a laboratory bottle of UL94. Drawing the soak fuel from a retail Swift or Avfuel UL94 tank, and keeping the ticket that identifies the fuel as ASTM D7547 UL94, is an unsourced captain choice. Avfuel's unleaded-avgas page, retrieved 20 October 2026, describes UL94 as Swift's ASTM D7547 fuel and prints no aromatic content: `https://www.avfuel.com/unleaded-avgas/`.

Aromatic content. Swift's one-page letter, Chris D'Acosta, hosted by AVweb, written on or after Lycoming's 12 April 2024 release, says moderate toluene use in UL94 is typically 10 to 20 %. The letter also quotes language it attributes to ASTM D7547: no explicit aromatic maximum, toluene limited to about 24 % by heating value, xylenes not higher than 10 %, total aromatics above 25 % extremely unlikely. That quotation was not checked against an opened D7547 appendix. The attribution is UNCONFIRMED. The words were read as Swift's letter: `https://avweb.com/wp-content/uploads/2024/04/swift-response.pdf`. The letter is a composition note. It is not a pass limit for these coupons. D7547 itself was not re-opened for this section.

The high-aromatic 100LL is bought to the §1 blend, with a certificate that shows the toluene result by D3606. If that certificate cannot be had, the panels wait.

### Sources

| item | title | date | section | URL |
|---|---|---|---|---|
| PAFI plan | PAFI Materials Compatibility Test Plan, PAFI-MTP-002 Rev 0 | 15 May 2024 | Preface, §1, objective 16, §19, §23.8, Appendix I | https://flyeagle.org/wp-content/uploads/2024/05/PAFI-MTP-002.pdf |
| D543-21 | Standard Practices for Evaluating the Resistance of Plastics to Chemical Reagents | edition 2021; product page undated, retrieved 20 October 2026 | §1, §4, §9, §10, §11.1 first sentence. Later procedure text UNCONFIRMED | https://www.astm.org/d0543-21.html |
| D543-06 | Same title, 2006 edition | 2006 | Procedure I, Procedure II, Practice B exposure times | ASTM International; the copy read was not ASTM-hosted, so no link |
| D570-22 | Standard Test Method for Water Absorption of Plastics | approved 1 September 2022, published September 2022 | §1, §6, §7.1, §8.1 start. Later procedures UNCONFIRMED | https://standards.iteh.ai/catalog/standards/astm/96e87ef8-a79c-4880-a714-dbd20160c276/astm-d570-22 |
| D5229-12 | Standard Test Method for Moisture Absorption Properties and Equilibrium Conditioning of Polymer Matrix Composite Materials | approved 1 February 2012, published June 2012 | §8.2.2, §10.2, Table 3 Procedures BFEP and BFFF | ASTM International; the copy read was not ASTM-hosted, so no link |
| D471-98e1 | Standard Test Method for Rubber Property—Effect of Liquids | 1998, Table 3 editorial update September 1999 | Table 3, Reference Fuel B. PAFI's 16a Table 4 was not opened | ASTM International; the copy read was not ASTM-hosted, so no link |
| Swift FAQ | Swift Fuels FAQ | page undated, retrieved 20 October 2026 | "What is UL94 Unleaded Avgas?"; "How can my airfield buy UL94 Unleaded Avgas?" | https://www.swiftfuelsavgas.com/faq |
| Swift letter | Swift Fuels response, Chris D'Acosta | on or after 12 April 2024 | full page, toluene paragraph | https://avweb.com/wp-content/uploads/2024/04/swift-response.pdf |
| Avfuel | Unleaded Avgas: UL94 Available Now | page undated, retrieved 20 October 2026 | UL94 fast facts. No aromatic figure on the page | https://www.avfuel.com/unleaded-avgas/ |
| E-Z bulletin | E-Z Poxy technical data bulletin, Endurance Technologies | revised August 2007 | Handling properties and post-cure, as read in `docs/research/2026-10-20-ul94-tank-resin.md` | https://www.aircraftspruce.com/catalog/pdf/EZpoxytechbulletin.pdf |

## 13. Needs Ryan

- **Buying the standards.** D3039, D3518 and D6641, plus ideally D6641's buckling note and CMH-17-1G
  Vol 1 Ch 8. The NOT READ values above wait on them.
- **The testing route** (section 10) and the lab choice, once the placeholder is filled.
- **The process parameters,** which bind the build: the vacuum level (20 inHg), hardener LH 287, and
  the post-cure of 15 h at 80 °C.
- **Optional conditions:** whether to run the unbagged BID condition and short-beam shear.
- **Spending.** All purchasing; the purchase order is a draft.
