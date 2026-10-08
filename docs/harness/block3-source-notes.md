# Block 3 source notes, S1-S3 (2026-10-07)

Record of the source lane for the equivalence engine. All wording is paraphrase; citations are
`<id>:p<n>` against `data/sources/registry.yaml`. "Eye-read" items were read by eye from an image
and await a captain re-read.

## S1. FAA Report 45 (flutter prevention criteria)

- Obtained from the NTIS technical reports library (accession ADA955270) after the DTIC copy was
  unreachable. Local copy is private. Printed page = pdf page - 1 for pp. 1-10.
- Wing criterion: F, the integral over the aileron span only of theta_i * c_i^2 ds, must not
  exceed 200 / Vd^2. theta_i is the wing twist at station i per unit torque applied outboard of the
  aileron end, rad/(ft-lb). So theta is the cumulative twist measured relative to the airplane
  centreline. c in ft, ds in ft, Vd the design dive speed, indicated (faa-report-45:p4).
- Unit trap: the report's other speed parameters state Vd in mph (faa-report-45:p6) and Figure 2's
  axis is mph (faa-report-45:p10).
- Aileron: K/I is compared with Figure 2, a straight line falling to zero at 300 mph. The intercept
  is to be digitised in task T9 (eye-read; captain re-read pending).
- Aileron free play limit: 2.5% of aileron chord (faa-report-45:p6).
- Elevator parallel- and perpendicular-axis criteria need fuselage vertical bending and torsion
  frequencies in cpm (faa-report-45:p6, p7). These are not available without a ground vibration
  test, so the elevator and rudder criteria are blocked: inputs_unsourced.
- Scope: the report calls its criteria preliminary (faa-report-45:p3) and says the wing criteria
  should apply to conventional airplanes without large wing mass concentrations (faa-report-45:p2).
- No worked example and no errata page were found. The secondary CAIA 2023 IA-100 paper remains the
  only numeric worked case.

## S2. Validation sources

- NCAMP 8552 AS4 (ncamp-8552-as4): lamina table 2-1 on p30, laminate table 2-2 on p31. Values are
  in `data/materials.yaml` set `as4_8552`. CVs: E1t 3.07% (p32), E2t 2.56% (p33), E1c 2.52% (p34),
  E2c 2.94% (p35), G12 3.41% (p38). Layup percentages are %0/%+-45/%90 (p19, Table 1-2 p21).
- AS4 laminate moduli, measured, Msi, with CV% and page, unnotched tension / compression:
  - [25/50/25]: 7.08 (2.56, p40) / 6.66 (3.57, p43)
  - [10/80/10]: 4.57 (1.99, p41) / 4.51 (3.05, p44)
  - [50/40/10]: 10.73 (3.27, p42) / 9.89 (2.32, p45)
- NCAMP 7781 / MTM45-1 (ncamp-7781-mtm45): Table 3-3 p34, Table 3-4 p35. QI [25/50/25] tension
  modulus 2.86 Msi (normalised; measured CV 7.19%, p51), compression 3.07 Msi (CV 8.53%, p53).
- AGATE wet layup (resin MGS 418, not L285): report 114, BGF 7781 glass (printed p25); report 115,
  Lancair 3K carbon (printed p24). The 2-axis values are recorded. The 1-axis values are not yet
  read and stay flagged unsourced.
- Kaw open course: glass/epoxy laminate example (kaw-ocw-ch4-laminate) and Tsai-Wu example
  (kaw-ocw-ch2-tsaiwu). The interaction term normalisation f12 = -1/2 follows Kaw's Tsai-Wu deck.
  Book pages not checked.
- Two-cell torsion check case: msstate-a610-ex1 (single web page, p1).
- Not found: Megson. Not opened: Tsai and Hahn.
- Mass-centroid versus elastic-axis: only NASA TN D-3125, printed p8, which states the converse
  (centre of mass forward of the elastic axis prevents flutter).
- Cured lamina data for BID 7725 and UND 7715 were not found, only dry-fabric sheets
  (hexforce-7715-pds). Both sets are fully flagged.

## S3. Long-EZ flutter inputs

- No designer V_D was found. The 190 kt red line (220 mph) is an indicated speed: the owner's
  manual has the builder placard the airspeed indicator with it (om-1980:p43) and p23 prints no
  basis. The "knots true airspeed" label in `data/validation/reference_data.json` is therefore
  unsupported. Correcting it is a separate ledger row, not done here.
- The owner's manual gives a builder flutter-envelope expansion procedure up to 190 kt in steps of
  at most 5 kt (om-1980:p43).
- VariEze flutter test points in the Canard Pusher record (cp-text): CP9; CP13, 240 mph indicated
  at 10,000 ft; CP19, cuffs, 215 kt.
- Elevator balance: outboard weight CS10 and inboard weight CS11 in lead. The elevator must hang
  12 to 25 deg leading edge down (cobelu ch11; GU ch11). Roncz chapter 30: must hang nose down,
  at most 0.3 lb of lead added to the outboard weight (cobelu ch30 p27, p31-32). The weights are
  about 3.3 and 3.6 lb (cobelu ch11 p12-13). The weight masses themselves are not printed.
- Aileron balance: a full-span 3/8 in steel rod on the leading edge acts as mass balance
  (cobelu ch19 p28). Balance check between top-level and bottom-level (cobelu ch19 p30; CP36
  LPC 113). At most 0.3 lb added.
- Rudder: no balance provision found (cobelu ch20).
- Canard Pusher flutter history (cp-text): CP5/6, CP12, CP13, CP14, CP18, CP19 (elevator flutter
  after unbalanced wide-chord elevators), CP21 (elevator flutter after weight added inboard
  only), CP26, CP31, CP35, CP36.
- NTSB was not queried successfully and the Aviation Safety Network pages were blocked, so no
  Long-EZ flutter accident record has been read. The validation wording stays "consistency
  check"; the Canard Pusher record shows elevator flutter on mis-balanced VariEze elevators.
- Pages to photograph if the owner can: plans p11-6 (elevator scale drawing) and p19-14 (aileron
  full-size sections).
