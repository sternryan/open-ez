# Planform correction: captain report (Tasks 1–6)

All six tasks are **done** and re-verified by the captain. Nothing was pushed.

## Done-means (captain runs at the end, HEAD d50714a)

- `.venv/bin/python -m pytest -q -p no:cacheprovider`: `1 failed, 428 passed, 2 skipped, 9 xfailed`.
  - The one failure is the pre-existing `scripts/assembly_test.py::test_full_assembly`.
  - All 9 xfails are strict and cite ledger rows 7, 8, 11–14, 16, 18 and 20.
- `node --test guide/viewer/tests/*.test.mjs`: 16 pass, 0 fail.
- `source <env> && .venv/bin/python -m guide.check`: `RECALL: 5/5 … OK`.
- Leak scan of the lines added since 5eb2113 (home paths, tailnet names/IPs, the copyright phrase): clean.

## Per task

| Task | Status | Commit(s) | Verify (captain) |
|---|---|---|---|
| 1 Chord search | done | 902e9c9 | ledger written; the search was a grep lookup the captain ran directly |
| 2 Provenance table | done | 7caaf39 | `test_geometry_provenance.py` 3 passed; regression + datum 25 passed |
| 3 Book frame and values | done | e0acbcc | provenance 9 passed. The full suite then showed 16 new failures, all handed to Task 4 |
| 4 Triage and ledger | done | 10c4ce9 | full suite: 5 failed (pre-existing; row 10 until Task 5; 3 drift locks until Task 6), 423 passed, 8 xfailed |
| 5 NP gap | done | 8525552 | report, unit and physics_regression tests: 21 passed |
| 6 Re-lock | done | 2d3d55b (split, row 20), d50714a (re-lock only) | regression_lock + physics_regression: 14 passed, 4 xfailed |

## Chord decision

- **No sourced value was found.** The CP 1–82 text had canard span and area figures for the VariEze
  and VariViggen only. No CP entry or cobelu line gives the Long-EZ Roncz canard chord or area.
- Template sheet C-3 prints no chord dimension. It carries only W.L. 19.8, B.L. 0 and B.L. 54.0 labels,
  and I did not measure it.
- **Result:** `canard_chord = 15.25`, status `unsourced`, empty source.
- Ledger: "Chord search".

## NP gap

| | Computed | Published | Signed gap | Grade |
|---|---|---|---|---|
| NP | 125.8549 | 108.0 | **+17.8549 in** | FAIL (tol 2.0) |
| CG fwd | 116.8532 | 99.0 | +17.8532 | FAIL |
| CG aft | 121.8536 | 104.0 | +17.8536 | FAIL |

- The CG limits are the NP minus fixed MAC fractions: the fitted Phase 5 margins 0.1721/0.0765, still
  used in `core.analysis`. Their gaps mirror the NP gap and are not independent evidence.
- `static_margin_pct` went from 1.91 to 36.05 against a reference of 12.0. It failed before and still fails.
- The report summary went from 9 pass / 3 fail to 6 pass / 6 fail.

## Strict-xfail ledger rows (category b)

- **7:** datum NP vs 108 within 8 in.
- **8:** datum CG range within 10 in.
- **11–13:** precision NP (2 in), CG fwd (1 in), CG aft (1 in).
- **14, 16, 18:** regression-lock external truth for NP, CG fwd and CG aft.
- **20:** the locked metrics all grade PASS (9 expected, 6 now).
- Every one has gap +17.85 in, and no tolerance was changed. The guard test
  `tests/test_geometry_ledger.py` checks the citations and the 2.0 NP tolerance.

## Deviations and escalations

1. **Weight arms shifted (Task 3).**
   - All eight `StructuralWeightParams` arms and `fuel_arm_in` moved by −45.5. The plan's Task 3 omitted
     them, but Review Focus 3 requires it: left in the old frame, the CG would sit 45.5 in off.
   - Consequence: `canard_arm_in` is −0.5, while the canard itself moved to FS 18.7. The canard's
     structural weight no longer sits at the canard. Follow-up, not fixed.
2. **OpenVSP fuselage never positioned (Task 3, found by the reviewer).**
   - `X_Rel_Location` defaulted to 0, which was the old nose. It is now set to `fs_nose` in
     `core/openvsp_runner.py` and `core/analysis.py`.
   - Untested at runtime, because the `openvsp` module is not installed locally.
3. **Foam-volume test: category (c), test-oracle defect (Task 4, row 2).** The lead was messaged.
   - OCCT `core.intersect(spar cap)` on the generator's BSPLINE core is nondeterministic. The same call
     with the same inputs returned 0.0, then 32.4.
   - The oracle now intersects the ruled loft that `build_layup` cuts. A new assert checks that the
     loft is within the existing 1% of the generator core. Both original 1% asserts are kept.
   - The foam itself was always correct: one solid, valid, base minus foam = 83.73 against 83.75 removed.
   - The lead ruled "fix the oracle" (matches what shipped). Ledger row 2 now records the repro and the
     BRepGProp numbers.
   - **Withdrawn claim.** My first note said the generator's spline section is about 4% under the true
     airfoil area (9.085 against 9.456 in²). Re-measured with BRepGProp, the generator section is 9.463
     against 9.456, a 0.07% difference. The 9.085, and the 511.3 and 571.4 volumes, came from cq's
     `Volume()`, which under-reads BSPLINE solids. They did not come from the flaky boolean. There is no
     generator area deficit, so nothing was added to open issues.
4. **Red intermediate commits.**
   - 10c4ce9 carried row 10 (fixed at 8525552) and three drift locks (fixed at d50714a), as the plan's
     task order implies.
   - 8525552 also carried `test_regression_values_match_accuracy_report` red, because Task 5's verify
     ran only the report tests. I caught it in Task 6 and split it into a traceability half (a) and a
     PASS-grade half (b, strict xfail, row 20) in 2d3d55b. d50714a holds only the three re-locked numbers.
5. **Calibration log.** The two fitted-margin entries are marked retired, and the wording says the
   fitted values are still used by `core.analysis`, not re-fitted.
6. **Review lane.** For Tasks 2 and 6, the captain reviewed or edited the diff directly instead of
   using a sonnet reviewer. Both diffs were mechanical: the plan's verbatim table, and 3 constants plus
   a test split.
7. **Minor slips.**
   - One probe printed the CP-sections file path, not a secret, to my transcript. Nothing was committed.
   - A redirect typo created a stray file, which I deleted uncommitted.
8. **Interleaved commits.** bf7c657, 5433b2a and dac2f89 (roadmap docs, by others) sit between the
   planform commits. I did not touch them.

## For the lead (Task 7 and beyond)

- **Already done in Task 4 (category a, row 1):** the `tests/guide` 73.5 → 63.0 pins, in
  `test_export_glb`, `render_fixture`, `test_layup` and `test_build_site`.
  - Task 7 Step 2 should find none left.
  - `output/guide/layup.json` has not been re-exported. Re-exporting it is Task 7 Step 1.
- **Ordering hazard.** `tests/guide/test_layup_geometry` and `test_export_glb` fail with MagicMock
  cadquery when run after some physics test files in a hand-ordered subset. They are green in normal
  collection order. This looks pre-existing; I did not investigate it further.
- **`reference_data.json` needs a ruling.**
  - `canard_span_in` is 147 and `canard_area_sqft` is 15.6, both labelled raf-cp31 "published", and
    the span entry's note says it "Matches config".
  - Neither number appears in the CP 1–82 text, and the book gives 142 (GU) and 126 (Roncz core).
  - I left both unchanged. Code now computes a canard area of 13.34 sq ft.
- **Legend line (Task 7 Step 4):** the chord is unsourced, so add "chord unsourced".
- **Wing LE and nose (from the NP gap).**
  - The wing root LE is now derived as FS 97.72 (anchor 113.9 at BL 58, 25° sweep, root BL 23.3).
  - The modelled nose sits at FS −45.5, 38.7 in ahead of the book's nose tip at FS −6.8, because the
    fuselage keeps its converted-unsourced stations.
  - Both feed the +17.85 NP gap. Verifying the main wing planform is already out of scope (spec §5).
- **Ryan's by-eye check:** FS 18.7 on p.171.
