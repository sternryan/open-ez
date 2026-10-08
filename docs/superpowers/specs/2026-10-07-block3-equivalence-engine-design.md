# Block 3: equivalence engine (design)

Status: rev 2, 2026-10-07. Rev 2 applies the adversarial review findings
(`docs/harness/block3-spec-review.md`). The owner's rulings are fixed inputs (section 2).

- Parent: `docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md` (section 4,
  Block 3; section 5, kernel validation).
- Plan: `docs/superpowers/plans/2026-10-07-block3-equivalence-engine.md`.

## 1. What Block 3 must prove

On paper, for a given part, Block 3 must show whether a proposed carbon laminate matches or beats the
book glass laminate where it matters. "Where it matters" follows the roadmap's trust standard
(section 2, item 1):

- strength at least equal;
- stiffness matched where it governs flying qualities;
- mass and CG deltas stated.

Three properties make the answer worth trusting.

1. **Validated kernels.** Each kernel is validated against published data that the code did not
   produce, before anything depends on it (section 5).
2. **A sourced flutter method.** The flutter method comes from a citable source and was chosen before
   it was run. The book Long-EZ checks the method and is never used to fit it (section 4).
3. **Relative comparisons.** Every comparison is made against the book part on the same geometry, so
   Block 3 needs neither absolute loads, the neutral point, the empty-weight closure nor the engine CG.
   - Under one proportional load, the Tsai-Wu strength ratio scales as 1/k with load magnitude. The
     ratio of carbon to book first-ply-failure capacity under the same load direction therefore does
     not depend on how large the load is.
   - This holds for one load direction at a time only. The gate takes the minimum over positive and
     negative bending and positive and negative torsion, separately (section 7, M3.4).
   - Combined bending plus torsion needs an absolute M/T ratio. It is out of scope and flagged until an
     M/T envelope is sourced.

**What Block 3 cannot close.** Block 3 does not close trust item 1 on stiffness. It computes no
deflection (all loads are unit loads), and no stiffness band has been set. Stiffness deltas are
reported and flagged; the band belongs to the outside reviewer (section 10).

Block 3 also proves nothing about material allowables (Block 5, coupons) or manufacturability
(Block 4). Its outputs are paper answers. Every input is sourced or flagged, and a gate cannot read
`pass` while any of its inputs is flagged (section 7, gate states).

## 2. Fixed inputs (owner rulings, not re-opened here)

- **Flutter.** The flutter estimate (203 KTAS against 240 required, strict xfail, ledger row 68) is
  replaced by a real, sourced method inside Block 3. It is not a Block 2 gate.
- **Kernel validation.** The laminate kernel is validated against published carbon and glass data
  before Block 3 relies on it.
- **Hard rules:**
  - never widen a bound;
  - never re-tune the frozen engine layout without a new source, a new ledger row and a new hash;
  - every value is sourced or flagged;
  - gates fail first;
  - never measure an undimensioned image.
- **Reuse.** Kernels carry no Long-EZ assumptions; airframe data lives in `config/` and `data/`. No
  generic multi-airframe framework is built now. It is extracted when a second airframe needs it.
- **No UI work.** A separate design pass covers it later.

## 3. What exists today (checked 2026-10-07)

### Laminate kernel

`core/simulation/fea_adapter.py` holds `CompositePly` (Q, Q-bar), `CompositeSection` (`abd_matrices`,
`tsai_wu_margin`) and `analyze_ply_by_ply`.

The roadmap and `TODOS.md` say it was checked against "one textbook E-glass case". No such test
exists, in the tree or in git history: `git log -S abd_matrices -- tests` is empty, and no test imports
`CompositeSection` or `CompositePly`. Validation therefore starts from zero.

Defects found on reading, before any test was written:

- An unknown material name silently falls back to the UNI glass properties.
- `CompositeSection.tsai_wu_margin` applies Tsai-Wu to one stress state, using the minimum allowables
  across all plies.
- `analyze_ply_by_ply` does work per ply in material axes. But it sets the strain to `[kappa z, 0, 0]`,
  so there are no Poisson strains and it ignores `D^-1` and the `B` coupling.
- The "margin" is `1 - F`, not the Tsai-Wu strength ratio.
- `f12 = -0.5 sqrt(f11 f22)` has no citation.
- Every lamina property is unsourced.
- `tests/test_dbox_deflection.py` grades two Tsai-Wu margins as greater than 0 today, so moving the
  adapter onto the new kernel moves them (plan T8).

### Flutter estimate

`FlutterEstimator.flutter_speed_ktas` computes `omega_theta * b / pi`. The formula is not traced to a
page, and the docstring calls it "a preliminary heuristic". The bound is
`required = v_ne_ktas * 1.2 = 240`.

The 200 for `v_ne_ktas` is unsourced. The owner's manual gives a 190 knot red line (om-1980:p23).
`reference_data.json` labels it "knots true airspeed", but a red line is normally an indicated speed,
and the basis is not confirmed (plan S3). Which way a correction would move the old bound depends on
that basis:

- 190 as true airspeed lowers the required speed to 228, a widening;
- 190 as indicated airspeed at the config's 8000 ft design altitude is about 214 knots true, which
  raises it.

In either case the 1.2 factor in old 23.629 applies to V_D, not V_NE (section 4.3). **Block 3 does not
edit `v_ne_ktas`.** Any correction is its own ledger row after S3 settles the basis, and it may not
lower the old test's bound. If the sourced value would lower it, the bound stays and the discrepancy is
recorded.

### Torsion and section geometry

`TorsionSection` is single-cell Bredt-Batho, with one hand-calculated test. `build_wing_torsion_section`
assumes a D-box at 0.25c with a depth of 0.10c. Both are unsourced placeholders.

The real canard is a foam-core sandwich. It has full-chord skins and a shear web inside, which makes it
at least a two-cell section (`guide/graph/ch30.yaml`, shear web op).

### Ply data

Block 2 recorded the book ply schedules as op materials in `guide/graph/*.yaml`: cloth, ply count, and
free-text orientation and extent. They are not yet a typed laminate schedule.

### Control-surface fields

`config.flutter.elevon_mass_balance_pct`: the Long-EZ has elevators and ailerons, not elevons. The field
is a declaration, not data, and Block 3 does not use it.

## 4. Flutter method selection

### 4.1 Chosen method

The method is **FAA Airframe and Equipment Engineering Report No. 45, "Simplified Flutter Prevention
Criteria for Personal Type Aircraft"** (FAA, 1955, "as corrected"; NTIS/DTIC ADA955270). Reasons:

- **The regulation names it.** Old 14 CFR 23.629(d) (2011 CFR edition) allows "the rigidity and mass
  balance criteria (pages 4–12), in Airframe and Equipment Engineering Report No. 45 (as corrected)",
  within the limits in (d)(1) to (d)(3).
- **The FAA's guidance accepts it.** FAA AC 23.629-1B (2004), chapter 1, paragraph 3a, accepts it as a
  means of compliance within those limits. The AC also says the report rests on a statistical study of
  airplanes that had flutter.
- **Its inputs come from the Block 3 kernels**, with no fitted constants: twist per unit torque along
  the span, chord, V_D, and control-surface mass properties.
- **It is a screening result only.** The AC says the criterion alone is not enough. A rational analysis
  or ground vibration test remains Block 5 work, and flight flutter testing is Block 7, Phase 1.

What the criterion contains, as read so far from **secondary sources only** (see 4.4):

- **Wing.** A torsional flexibility factor F, the sum of theta_i c_i^2 ds over the semispan carrying
  the aileron. The limit is F <= 200 / V_D^2. Units: theta in rad per lb·ft, c and ds in ft, V_D in mph.
  The speed basis is to be confirmed from the primary text.
  - Source: CAIA 2023 conference paper (Universidad Nacional de La Plata) on the IA-100.
  - Worked case: F = 7.379e-4 against a limit of 2.428e-3 at V_D = 287 mph.
- **Control surfaces.** Aileron, elevator and rudder balance criteria (K/I against a V_D-dependent
  limit), and tail parameters read from the report's figures.

**The wing criterion has no mass or inertia term.** It screens rigidity only. Mass enters Report 45 only
through the control-surface balance criteria. Section 7 adds relative mass gates for that reason.

### 4.2 Alternatives not chosen now

- **Rational analysis to 1.2 V_D** (23.629(c)). It needs mode shapes and frequencies the model cannot
  support yet. Deferred to Block 5, after a ground vibration test.
- **The existing heuristic.** Rejected: it has no page source.
- **Comparison with dynamically similar aircraft** (AC 23.629-1B, chapter 1, paragraph 1). Rejected:
  there is no ground vibration data for a Long-EZ.

### 4.3 Speeds, units and basis

Every speed in Block 3 code and reports carries its unit and its basis (IAS, CAS, EAS or TAS) in the
field name or the record. Speeds are converted before any comparison, and a test rejects comparisons
of mixed units.

The designer's V_D is **not sourced** (plan S3). Old 23.1505(a) bounds it from below: V_NE <= 0.9 V_D.
With the 190 knot red line, V_D >= 211 knots in the red line's basis. That basis is unconfirmed. Old
23.629(d)(1) states V_D in EAS.

Using that minimum as the gate would be choosing to pass, so the result is never a verdict at an
assumed V_D:

- **The absolute result is a speed.** It is the highest V_D the book wing clears, V_D,max = sqrt(200 / F).
  The criterion produces it in mph, in the primary text's basis. The report states it in that unit and
  basis and also converts it to knots EAS, then sets it next to:
  - the regulatory floor, converted to EAS once S3 settles the red line's basis;
  - the designer's V_D, if S3 finds it.

  Only a sourced designer V_D turns this into a pass or a fail.
- **Relative gates** do not depend on V_D (section 7).

### 4.4 Applicability and the primary text

**Primary text.** On 2026-10-07 the DTIC copy was offline for maintenance. **M3.3 does not start until
the primary Report 45, with its corrections, is held and registered.** Every constant in the code cites
a page, figure or equation in it. If the primary and secondary sources disagree, the primary wins and
the difference is recorded. Building the gate from the secondary paper alone is not allowed.

**Applicability.** Old 23.629(d) limits the method on three counts, and each is checked and recorded
separately:

- **(d)(1): V_D under 260 knots EAS and under Mach 0.5.** Checked against the V_D,max produced and any
  sourced V_D.
- **(d)(2): the wing and aileron criteria are limited to airplanes without large mass concentrations
  along the span.** The Long-EZ carries winglets with rudders at each wingtip. Whether these count is
  **not established**, so the flag is raised.
- **(d)(3): no T-tail or other unconventional tail, no unusual mass distribution or design features,
  and fixed fins and stabilizers.** The Long-EZ is a canard pusher, with its pitch control on a lifting
  foreplane. The texts read so far do not mention canards. Flagged.

Every result carries `applicability: {d1, d2, d3}` with each item marked `met`, `not met` or
`unconfirmed`.

- **Main wing.** The wing criterion is applied as written, with these flags attached.
- **Canard.** Applying the wing criterion to the canard is by analogy, as is applying the tail criteria
  to the elevator. Both are labelled that way.
- **Who decides.** Whether Report 45 applies at all goes to the outside reviewer (roadmap trust
  standard, item 3).

### 4.5 How the book airplane is used, and why it is not a fit

1. **Method fixed before any run.** This spec fixes the method. Report 45's constants, transcribed with
   page cites, are frozen and hashed before the book inputs are assembled. There are no free
   constants.
2. **Inputs frozen before the result is seen.** Before the criterion runs, these book inputs are
   frozen with a sha256 in a ledger row:
   - the ply schedule;
   - the lamina shear moduli;
   - the cell geometry, cited to plans pages;
   - the twist per unit torque derived from them;
   - the control-surface mass properties.

   The crew that assembles the inputs never runs the criterion.
3. **Prediction registered.** The freeze row states the expected result, and why, before the run.
4. **Independent kernels.** The twist comes from kernels validated in M3.1 and M3.2. Changing either
   kernel after M3.3 has run needs a new ledger row.
5. **Discrimination.** A pass on the book airplane alone says little, because a criterion that always
   passes would also pass it. The gate therefore has to do three more things.
   - **Worked cases.** It reproduces the secondary worked case, and any worked example in the primary
     text.
   - **A broken input against a fixed threshold.** On the worked case, GJ is divided by 4, which
     multiplies F by 4: 7.379e-4 becomes 2.95e-3, above the 2.428e-3 limit. The factor 4 is the
     smallest power of two that crosses the case's own margin of 3.29. It is stated here before the
     run.
     - The book run itself has no pass or fail to break, so its broken input is tested in the relative
       gate instead: F(carbon) is doubled and must fail.
   - **A balance-weight control.** The book elevator with its balance weights removed must fail the
     elevator balance criterion. This is a deliberately broken input, not fleet evidence.
6. **A failure is a finding.** If the book airplane fails a sourced criterion, or the method does not
   apply, the result is reported and recorded as a strict xfail citing a new ledger row. The method is
   not changed.

**The fleet-history premise is unsourced.** The claim is that the fleet has flown for about 40 years
without flutter. A first search found VariEze elevator and canard flutter accidents, which the records
trace to builder balancing errors and to modifications. Only search snippets were seen; the primary
records were not opened. The VariEze is a different airframe, and its elevator geometry is not held,
so no VariEze case is transposed onto the Long-EZ.

Plan task S3 queries the NTSB database and the Canard Pusher. The validation wording becomes whatever
that search supports. Until then the book check is described as a consistency check, not a
fleet-validated one.

## 5. Kernel validation sources

Every source is registered in `data/sources/registry.yaml` before its values enter a test. A citation
takes the form `<id>:p<page>` plus the table, example or figure.

| use | source | where the numbers are | status (2026-10-07) |
|---|---|---|---|
| Carbon: lamina in, measured laminate **moduli** out (independent check of CLT stiffness) | NCAMP Test Report CAM-RP-2010-002 Rev A, Hexcel 8552 AS4 unitape (Wichita State NIAR, 2011) | Table 2-1, p30 (lamina); Table 2-2, p31 (laminates [25/50/25], [10/80/10], [50/40/10]: unnotched tension and compression modulus and strength) | Opened. The lamina table is an image, read by eye and re-read by the captain. **Kernel validation only. Never a design input**: it is autoclave prepreg, and the build is wet layup. |
| Glass: lamina in, laminate out | candidates: NCAMP 7781 E-glass/2510 report; CMH-17 Vol 2 E-glass/epoxy | to find | not opened (plan S2) |
| Arithmetic of Q, Q-bar, ABD and the Tsai-Wu strength ratio, to printed precision | candidates: Kaw, *Mechanics of Composite Materials*, 2nd ed. (CRC 2006), ch. 2–4 worked examples; Jones; Daniel & Ishai | example numbers cited once a book is in hand | not opened (plan S2) |
| Multi-cell thin-wall torsion and bending | candidate: Megson, *Aircraft Structures for Engineering Students*, multi-cell torsion worked examples | to find | not opened (plan S2); the existing single-cell hand case stays |
| Wet-layup laminates with the owner's epoxy: plausibility band | MGS/Hexion L285 technical data, "Data of reinforced resin" table (8H satin glass 296 g/m^2; plain-weave carbon 200 g/m^2; 43 vol%) | table near the end of the data sheet | Opened. Laminate values only, with no lamina inputs: a plausibility band, not a CLT validation. |
| **Design inputs**: lamina properties of the book cloths (BID 7725, UND 7715) and of the proposed carbon cloth, wet-laid in the build's epoxy | candidates: fabric data sheets; CMH-17 wet-layup data; otherwise Block 5 coupons | to find | Not opened (plan S2). Until found, both sides are `unsourced`, and no ratio gate can read `pass`. |
| Tsai-Wu interaction term f12 | candidates: Tsai & Hahn, *Introduction to Composite Materials*; Kaw ch. 2 | to find | not opened. Gates take the minimum over the cited f12 and f12 = 0. |

Validation rules:

- **Stiffness and strength are validated differently.** CLT predicts laminate moduli, and those
  predictions are gated against NCAMP's measured moduli. First-ply failure is not a prediction of
  measured ultimate strength, so the measured strengths are **not compared with FPF**.
  - FPF and a fibre-failure (last-ply) estimate are reported next to the measured strengths, labelled
    "not a gate".
  - The strength kernel is validated by the textbook arithmetic only.
  - The M3.4 strength gate compares FPF with FPF, the same model on both sides. Its known weakness
    (glass and carbon progress to ultimate differently) is flagged in the report.
- **Bounds are registered before the comparison runs**, in a ledger freeze row. The moduli bound is
  the measured mean plus or minus two standard deviations, with the standard deviation taken as the
  table's reported coefficient of variation times the mean. The factor of two is a flagged captain
  choice and is never widened. The textbook arithmetic must match the last printed digit.
- **Each validation gate is shown to fail on a broken input**: E1 and E2 swapped, a ply angle's sign
  flipped, and a ply dropped. These tests pass by asserting that the comparison fails.
- **Glass is required.** The book baseline is glass, so validating on carbon alone does not validate
  the comparison. Without a glass lamina-to-laminate source, M3.1 stays open on glass, and glass-side
  gates read `blocked: glass_unvalidated`.

## 6. Strict-xfail dispositions

### Row 68: flutter estimate

**Check.** The estimate is 203 KTAS against 240 required (`test_flutter_speed_exceeds_240_ktas`,
`test_flutter_check_safe_with_dbox`).

**Owner.** Block 3, M3.3.

**Disposition.** Report 45 supersedes the heuristic as the flutter method (section 4), but the two
tests are not deleted, re-bounded or re-pointed, and `v_ne_ktas` is not edited (section 3). Only their
reason text changes, to point at M3.3's result. They can be retired **only on the outside reviewer's
ruling** (Block 5), recorded in a ledger row. No claim that the replacement is "not looser" is made,
because a rigidity criterion and a speed bound cannot be ordered against each other.

**The wing-mass question.** Row 68 also asks whether the all-in 132.4 lb wing mass belongs in the
estimate. That question is moot only *inside* Report 45, whose wing criterion has no mass term. It
returns with any rational analysis (Block 5). Until then, Block 3's relative mass gates (section 7)
carry it.

### Row 53: two-method NP

**Check.** Analytic against VSPAERO, delta +1.63 in, bound 1.0 in.

**Owner.** Deferred: a Block 1 follow-up, needed before Block 6.

**Disposition.** Block 3 keeps the outer shape, and its gates read only section properties under unit
loads. No Block 3 input or gate reads the NP or the CG limits. The fix stays as `docs/block1-report.md`
states it: a partial-span downwash method from a textbook. Block 6's engine CG trade is the consumer
that forces it.

### Rows 70 and 71: O-235 component CG and cowl clearance

**Check.** The component CG is 11.09 in from the flange against 14.75 in, and 0.56 in below the crank
line against 1.13 in. Separately, the carburettor and bracket sit below the cowl.

**Owner.** Deferred to Block 6 (engine).

**Disposition.** Block 3 never reads engine mass or CG, because its loads are unit loads and not
inertia loads. The book engine is replaced by a Rotax in Block 6. These rows clear only with a new
source plus a new row and hash, and are never re-tuned.

### Row 65: empty-weight closure

**Check.** The weight half-band is 117.36 lb, over the 20 lb cap.

**Owner.** Stays Block 2's frozen record; Block 3 contributes evidence only.

**Disposition.** Block 3's mass outputs are deltas, so they need no closure. M3.4 reports the book
canard's computed mass against the closure's canard row, after its unsourced inputs (resin fraction,
foam density) have been frozen and hashed. If that reveals a closure input error, it becomes a new
Block 2 row with a new hash. Block 3 never edits `closure:`.

## 7. Milestones and exit tests

Each exit test is written first and shown to fail, then made to pass. Each gate is shown to fail on a
broken input.

**Gate states.** Every Block 3 gate reports one of four states:

- `pass`;
- `fail`, carried as a strict xfail with a ledger row;
- `blocked: <reason>`. The reasons are `inputs_unsourced`, `glass_unvalidated`, `criterion_unavailable`
  and `not_applicable`.
- `open: requires_original_test` (ledger row 77). Every input that keeps the gate from a result is
  one that a recorded search shows has no public source, so only an owner test can close it.
  - The input carries `flag: requires_original_test` in `data/materials.yaml`, with three fields:
    - `search`: what was searched and why no public source exists;
    - `closing_test`: an ASTM method and a Block 5 coupon id;
    - `test_plan`: a link to the coupon test plan (`docs/superpowers/specs/2026-10-08-block5-coupon-test-plan.md`).
  - The gate lists those inputs (`test_required_inputs`) and their coupons (`closing_coupons`).
  - If any other reason also holds, the gate reads `blocked` and lists `requires_original_test`
    among its reasons.
  - The flag is applied only where the search evidence exists. Today that is the carbon proxy's
    warp values (E1, nu12, F1t, F1c). Everything else stays `unsourced`.

A gate whose inputs include any flagged value **cannot report `pass`**, under either flag. Tests
enforce this: flagging a single input turns a `pass` into `blocked`, a single test-required input turns
it into `open`, and `requires_original_test` cannot be asserted without its inputs and coupons.

### M3.0: sources and data skeleton

- **Sources.** The sources marked "opened" in section 5 are registered.
- **Materials file.** `data/materials.yaml` exists, and every property in it carries a cite or a flag
  (`unsourced`, or `requires_original_test` with its search, closing test and plan link). A test
  rejects a property that has neither.
- **Kernel purity guard.** A purity test is written. Modules under `core/kernels/` may import only:
  - the standard library's math, dataclasses, typing and enum;
  - numpy;
  - scipy;
  - `core.kernels.*`.

  The guard also bans `open`, `pathlib` and `importlib`. It walks imports transitively, and a planted
  module that breaks the rule must be caught.

### M3.1: laminate kernel validated

Files: `core/kernels/lamina.py`, `core/kernels/laminate.py`, `core/kernels/tsai_wu.py`.

**What the kernel computes:**
- Q, Q-bar, ABD and the laminate engineering constants;
- ply strains and stresses in material axes from (N, M), through the full ABD inverse;
- the per-ply Tsai-Wu strength ratio.

**Exit tests:**
- The textbook arithmetic is reproduced to its printed digits.
- NCAMP moduli are predicted for all three layups, within the pre-registered bound.
- The same is done for glass, or M3.1 is recorded as open on glass.
- The broken-input tests are in place.
- An unknown material raises an error.
- `fea_adapter` is unchanged.

### M3.2: section kernel validated

File: `core/kernels/thinwall.py`.

**What the kernel computes:**
- multi-cell Bredt-Batho torsion (GJ and the shear flow per wall), with the laminate shear stiffness
  per wall;
- EI from every wall's axial stiffness: caps, skin UND plies and the web;
- web shear stress;
- the shear centre;
- mass per length, the chordwise mass centroid and the torsional mass inertia.

**Exit tests:**
- The Megson multi-cell worked examples and the existing hand case are reproduced.
- The broken-input tests are in place.
- Moving the `fea_adapter` callers onto the kernel records a ledger row for every number that moves,
  including the two `test_dbox_deflection.py` Tsai-Wu margins. No bound changes.

### M3.3: Report 45 screening

Files: `core/kernels/flutter_r45.py`, `data/criteria/report45.yaml`.

**Precondition:** the primary text is held. Chart values are read from dimensioned figures, each point
citing its figure. The captain re-reads every one.

**Exit tests:**
- The worked cases are reproduced.
- The divide-GJ-by-4 case is shown red.
- The book elevator with its balance weights removed is shown red.
- The book inputs are frozen and hashed before the run, with the prediction registered.
- The book result is reported as V_D,max (unit and basis stated), with the (d)(1) to (d)(3) flags.

### M3.4: first equivalence, the canard

Files: `data/laminates/canard_book.yaml`, `data/laminates/canard_carbon.yaml`,
`scripts/equivalence_report.py`, `data/validation/equivalence_canard.json`.

**Before any comparison runs:**
- The book schedule is typed from `ch30.yaml` and its source pages, and the captain re-reads every value.
- The book lamina values, the mass-kernel inputs and the cell geometry are frozen and hashed **before
  any carbon number is computed**.
- The sizing rule is written and registered in a ledger row. It states its priority:
  - First, match EI and GJ station by station.
  - Then check strength.
  - If carbon at matched stiffness fails strength (carbon's lower failure strain can cause this), that
    is reported as a finding. The rule is not quietly re-sized.

  The rule uses only the lamina data for the wet-layup carbon system, never NCAMP prepreg values.

**Gates:**
- **Strength.** At every station, the ratio of carbon to book FPF capacity is at least 1.0. The ratio
  is the minimum over plus and minus a unit moment, plus and minus a unit torque, and both values of
  f12.
- **Mass placement.** The mass centroid's offset aft of the shear centre is no larger than the book's.
  - Basis: the classical result that a CG aft of the elastic axis is destabilising in bending-torsion
    flutter. The citation comes from plan task S2 (candidates: Bisplinghoff, Ashley & Halfman;
    Hodges & Pierce). Until it is registered, this gate reads `blocked: inputs_unsourced`.
- **Torsional inertia.** Reported against the book. It is a flag, not a gate, because Report 45 gives
  it no sourced direction.
- **Elevator balance.** The balance check runs on the book elevator and on the proposal. It is labelled
  by analogy, and it depends on M3.3; while M3.3 is blocked it reads `blocked: criterion_unavailable`.

**Reported only:**
- The EI and GJ deltas, flagged past a threshold that is registered before the run and labelled an
  unsourced captain choice. This is a flag, not a gate.
- F(carbon) against F(book). It is labelled a **consistency check**: the sizing rule matches GJ, so
  F(carbon) is about equal to F(book) by construction, and the comparison cannot discriminate.
- Mass and CG deltas.
- The book canard's mass against the closure row.

**Report checks:**
- The report is generated by script and regenerates byte-identical.
- With one cap ply removed from the carbon schedule, the strength gate fails.

### M3.5: wing equivalence and relative flutter

M3.5 runs the M3.4 pipeline on the wing.

**Gates:**
- the strength gate;
- the mass-placement gate;
- the aileron balance criterion, run on both wings.

**Reported:**
- F(carbon) against F(book), again a consistency check;
- V_D,max for both wings, with the applicability flags.

**Exit test:** the row-68 disposition is recorded in the ledger.

## 8. The first part: the canard

The canard goes first, for four reasons.

- **Best-sourced ply schedule.** It was rehearsed twice: in M1, then in the Roncz chapter 30 rows of
  `ch30.yaml`. It was also drawn in the M2 layup cutaway.
- **Simplest primary laminate.** It is a foam core with UND caps and shear web, and BID and UND skins.
- **Its stiffness matters.** Its deflection and load sharing are the stiffness question the roadmap
  names.
- **Flutter history.** The flutter history found so far points at canard elevators.

**The planform conflict does not block it.** The canard is GU-sized, and the Roncz span is unsourced.
That does not matter here, because the comparison is book against carbon on the same geometry.

**The wing goes second** (M3.5). Report 45's wing criterion was written for a main wing.

## 9. Risks

- **Report 45 may not apply** under (d)(2) or (d)(3). In that case Block 3's flutter output is a
  flagged screening number, and the answer moves to Block 5 (ground vibration test plus a rational
  analysis). It is stated now so that nobody reads the screening number as clearance.
- **Design inputs may stay unsourced.** If no lamina data is found for the book cloths or for wet-layup
  carbon, every ratio gate stays `blocked: inputs_unsourced` until Block 5 coupons supply allowables.
  Where the search shows no public source exists (the wet-layup warp values), the input reads
  `requires_original_test` and names its coupon (row 77). The coupon plan is
  `docs/superpowers/specs/2026-10-08-block5-coupon-test-plan.md`.
  Block 3 then delivers validated kernels, a frozen pipeline and reported deltas, but no green
  equivalence. That is an honest outcome.
- **No designer V_D.** The absolute flutter result stays a speed.
- **No primary Report 45.** M3.3 stays blocked. A gate built from the secondary paper is not allowed.
- **Stiffness and strength may conflict.** Carbon matched for stiffness may fail the strength ratio.
  That is reported as a finding, and the band belongs to the outside reviewer.
- **The mass kernel may disagree with the closure.** That is evidence for Block 2, recorded and not
  fitted.
- **Scope creep.** Kernels stay pure functions, guarded by the purity test. Extraction for the RV-12
  waits for the RV-12.
- **Remote compute.** The local-model implementation lane and the remote test fan-out resume once the
  remote runners are back (on or after 2026-10-09). The source lane, test vectors and RED tests do not
  need them.

## 10. What the owner must supply

- **Nothing up front.**
- **On a crew's request:** photographs of plan pages that are illegible in the held scan. The likely
  pages are chapter 19 (ailerons, and any balance provision) and the elevator balance weight pages.
- **A decision only if one is needed:** whether to buy a composites textbook, if no library or open
  copy with worked examples is found. That is a purchase.
- **Recorded for the outside reviewer, not asked of the owner:**
  - the stiffness-match band;
  - Report 45's applicability under (d)(2) and (d)(3);
  - retiring the row-68 heuristic tests.

## 11. Out of scope

- UI and lab work, and changes to the outer shape.
- Coupons and allowables, rational flutter analysis and ground vibration tests (all Block 5), and the
  engine (Block 6).
- Combined bending-torsion strength, which needs an M/T envelope (flagged).
- A generic multi-airframe framework.
