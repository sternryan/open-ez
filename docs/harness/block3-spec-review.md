# Block 3 spec: adversarial review (2026-10-07)

**Under review:**
- Spec: `docs/superpowers/specs/2026-10-07-block3-equivalence-engine-design.md`, rev 1
- Plan: `docs/superpowers/plans/2026-10-07-block3-equivalence-engine.md`, rev 1

**Reviewer:** one fresh-context Opus reviewer. It was told to prove the spec wrong, looking for
unsourced claims, a method chosen to pass, circularity between the book-airplane check and the method,
regulatory misreadings, dodging xfail dispositions and plan defects. It read the repo and fetched the
2011 CFR text of 23.629 and 23.1505. It edited nothing.

**Verdict on rev 1:** not ready. It raised 3 P0, 7 P1 and 8 P2 findings. Rev 2 of both documents
applies every finding, as listed below.

| # | sev | finding | rev 2 change |
|---|---|---|---|
| 1 | P0 | The carbon proposal was sized from NCAMP 8552 AS4, an autoclave prepreg, but the build is a wet layup. That pushes the strength ratio toward passing. | NCAMP is kernel-validation data only. It is never a design input, and a test enforces this (`use: validation`, plan T1). Carbon is sized only from wet-layup lamina data (spec §5, §7 M3.4; plan T11). |
| 2 | P0 | The book lamina values are unsourced, and they are the denominators of every ratio, so they can be steered. Rev 1 only said the results would "carry the flag". | Gate states were added. A gate with any flagged input can never read `pass`; it reads `blocked: inputs_unsourced`, and a test checks this. The book lamina values, the mass inputs and the cell geometry are frozen and hashed before any carbon number exists (spec §7; plan T11, T12). |
| 3 | P0 | The relative flutter gate F(carbon) <= F(book) is tautological when the sizing rule matches GJ. Report 45's wing criterion has no mass term, so the row-68 wing-mass question only "dissolved" inside the chosen criterion. | F(carbon) against F(book) is now labelled a consistency check, not a gate. A pre-registered mass-placement gate was added: the mass centroid may sit no further aft of the shear centre than the book's, with its flutter citation coming from S2. Torsional inertia is reported. The wing-mass question is stated as moot only inside Report 45 (spec §4.1, §6, §7). |
| 4 | P1 | Only 23.629(d)(3) was flagged. (d)(1), the 260 kt EAS limit, and (d)(2), large mass concentrations along the span (the winglets with rudders), were missed. | All three are checked separately and reported as `applicability: {d1, d2, d3}` (spec §4.4). |
| 5 | P1 | Knots and mph were mixed in V_D,max against the 211 floor. The 190 red line was assumed to be true airspeed, and if it is indicated, "lowers to 228" is wrong. | Every speed now carries its unit and basis, and a test rejects mixed units. The §3 text states both cases. S3 settles the basis and corrects the `reference_data.json` label through a ledger row. `config.v_ne_ktas` is still not edited, and no correction may lower the old bound. |
| 6 | P1 | "Halving GJ fails" could not go red on the book run, because that result is a speed, not a verdict. | The broken input is now set against a fixed threshold: on the IA-100 worked case, GJ divided by 4 makes F 2.95e-3, above the 2.428e-3 limit. The factor is the smallest power of two above the case's margin of 3.29, stated before the run. On the book side, doubling F(carbon) must fail the relative comparison (spec §4.5). |
| 7 | P1 | The section topology was wrong. The canard has a shear web inside full-chord skins, so it is two-cell, but rev 1 specified single-cell Bredt-Batho and `cap_ei` left out the skin UND plies. | M3.2 is now a multi-cell kernel, with a Megson multi-cell vector. EI comes from all walls. The kernel also computes web shear, the shear centre, the mass centroid and the torsional inertia. Cell geometry is cited to plans pages, not taken from the legacy D-box (spec §7 M3.2; plan T6, T11). |
| 8 | P1 | Strength-ratio load independence holds for one proportional load only. Rev 1 did not cover the sign asymmetry (F1t is not F1c), combined M/T, or the free choice of f12. | The gate takes the minimum over ±M, ±T and both values of f12. Combined M/T is out of scope and flagged until an envelope is sourced (spec §1, §7, §11). |
| 9 | P1 | Rev 1 compared first-ply failure with NCAMP's measured ultimate strengths. That forces either an automatic miss or a switch to another failure model after the fact. | Only moduli are gated against NCAMP. Measured strengths are reported next to the FPF and fibre-failure estimates as "not a gate", as recorded in the freeze row. The strength kernel is validated by textbook arithmetic. The M3.4 gate compares FPF with FPF, and its weakness is flagged (spec §5; plan T3, T5). |
| 10 | P1 | Stiffness matching, which the trust standard requires, was never gated, no deflection is computed, and equal stiffness conflicts with strength of at least 1. | §1 now states that Block 3 cannot close trust item 1 on stiffness. The sizing rule fixes the priority before the run: match stiffness first, then check strength, and report a miss as a finding (spec §1, §7; plan T11). |
| 11 | P2 | The §3 defect claim was wrong: `analyze_ply_by_ply` does apply Tsai-Wu per ply, in material axes. Its real defects are strain set to [kz, 0, 0] with no Poisson terms and no B/D coupling. Rev 1 also missed that `test_dbox_deflection.py` grades two margins. | Accepted. §3 is corrected, and plan T8 names both tests. The reviewer independently confirmed the "no laminate test exists" claim, so it stands. |
| 12 | P2 | The mass check could be fitted through resin fraction and foam density. | Both are frozen and hashed before the comparison (spec §6 row 65; plan T11). |
| 13 | P2 | The negative control transposed a VariEze accident onto the Long-EZ elevator. | Dropped. The fleet records only inform the wording. The control is now a deliberately broken input: the book elevator with its balance weights removed (spec §4.5). |
| 14 | P2 | "Not looser" cannot compare a rigidity criterion with a speed bound. | Removed. The row-68 tests can be retired only on the outside reviewer's ruling (spec §6). |
| 15 | P2 | Pre-assigned ledger rows 72 to 76 would collide with the moved-test rows from T8 and T5. | Rows are now named by purpose and numbered only when written (plan, global constraints). |
| 16 | P2 | The purity guard could be bypassed through `Path("data")` or a transitive import of `fea_adapter`. | It is now an import allow-list, walked transitively, with `open`, `pathlib` and `importlib` banned, and three planted violations (plan T2). |
| 17 | P2 | Ordering problems: T11 was missing from the before-the-gate list; the elevator check in M3.4 depends on M3.3; the "RED as intended" wording was ambiguous. | T11 has been added. The elevator check reads `blocked: criterion_unavailable` while M3.3 is blocked. Broken-input tests now "pass by asserting the comparison fails". |
| 18 | P2 | Rev 1 had no state for a glass-unvalidated report. | `blocked: glass_unvalidated` was added, and tests assert it (spec §5, §7; plan T12). |

**Not re-reviewed.** Rev 2 was not sent back to the reviewer, because this wave allows one adversarial
review. The panel-style ship gate belongs to Block 3's first code diff, where the push gate's
fresh-context grader runs.
