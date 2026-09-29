# Geometry correction ledger (planform correction, 2026-09-29)

Record of the planform correction: where the canard chord came from (or didn't), every test that
moved when the geometry switched to book values, and the neutral-point gap. Spec:
`docs/superpowers/specs/2026-09-29-planform-correction-design.md`.

## Chord search

Searched the Canard Pusher sections text (CP1–82) and the cobelu plans transcription (all chapters,
incl. ch 30, R1149MS canard) for the Long-EZ canard chord or area. Regexes, case-insensitive:
`canard (chord|area)`, `chord of the canard`, `R114[59]`, `Roncz.*(chord|area|sq)`,
`canard.*sq\.? ?f`, plus follow-ups for spec tables (`Canard Span/Area`, `Canard <number>`) and any
`chord` in cobelu ch 10 / ch 30 / ch 1.

| Hit | Source | Paraphrase (≤10 words) | Usable? |
|---|---|---|---|
| 1 | CP (early newsletter, VariEze prototype specs) | VariEze prototype: canard area 14 sq ft, span 12 ft | No: VariEze, not Long-EZ |
| 2 | CP (VariEze spec table, several issues) | VariEze canard span/area 13.2 ft / 13.7 sq ft | No: VariEze |
| 3 | CP (VariEze brochure, repeated) | VariEze canard span/area 12.5 ft / 13 sq ft | No: VariEze |
| 4 | CP (VariViggen brochure, repeated) | VariViggen canard span/area 8 ft / 18.3 sq ft | No: VariViggen |
| 5 | CP (R1145MS canard articles) | R1145MS canard introduced; no chord or area given | No value |
| 6 | CP (canard span trim article) | Long-EZ canard trimmed from 150 to 142 in span | Span only |
| 7 | cobelu ch 30 Step 18 | outboard jig blocks bonded 126 in apart | Span only (core to BL ±63) |
| 8 | cobelu `I/images/30/C-3.PNG` | templates A–D: labels W.L. 19.8, B.L. 0, B.L. 54.0 | No printed chord dimension |

**Result: no sourced value found.** No CP entry or cobelu line gives the Long-EZ (Roncz R1145MS)
canard chord or area, and template sheet C-3 prints no chord dimension (it was not measured, per the
plan's rule against measuring undimensioned images).

**Decision:** Task 3 uses `canard_chord = 15.25` (the mean of the old 17.0 / 13.5 pair) with status
`unsourced` and an empty source.

## Test ledger

Every test that moved when the geometry switched to book values in the published frame
(`datum_offset_in = 0`, single canard chord, canard span 126 in). Computed after the change:
NP 125.85 in (published 108.0, gap +17.85); CG fwd 116.85 (published 99.0, gap +17.85); CG aft
121.85 (published 104.0, gap +17.85). No tolerance or bound was widened.

- **(a)** Pinned to a retired number: the expectation was updated to the new value.
- **(b)** A physics sanity bound that book geometry now fails: strict `xfail` citing its row; the
  bound itself is unchanged.
- **(c)** Test-oracle defect: the test's own method was unreliable; the oracle was fixed, bounds kept.

The pre-existing failure `scripts/assembly_test.py::test_full_assembly` is out of scope and has no row.

| # | test | old expectation | new value | category | why |
|---|---|---|---|---|---|
| 1 | `tests/guide/test_export_glb.py::test_real_export_nests_plies_and_keeps_inches` (also `tests/guide/render_fixture.py`, `tests/guide/test_layup.py::test_layup_json_shape`, `tests/guide/test_build_site.py::test_renders_stale_layup` (its replace target): same retired number) | max Y (semi-span) 73.5 in | 63.0 in | (a) | 73.5 came from the retired 147 in canard span; book span is 126 in (semi-span 63.0). |
| 2 | `tests/guide/test_layup_geometry.py::test_foam_volume_is_core_minus_cutters` | cutter volumes from `core.intersect(cutter)` on the generator core | cutter volumes from the ruled loft `build_layup` cuts, plus assert loft volume within 1% of generator core; original 1% asserts kept | (c) | `core.intersect` on the BSPLINE core is nondeterministic in OCCT (bottom spar cap 0.0 on first call, 32.4 on repeats, same inputs). |
| 3 | `tests/test_canard_stall_and_downwash.py::TestCanardMAC::test_canard_mac_less_than_root_chord` | MAC < root chord 17.0 and > tip chord 13.5 | renamed `test_canard_mac_equals_chord_for_rectangle`: MAC == `canard_chord`, root == tip | (a) | Pinned to the retired 17.0 / 13.5 taper; the canard is now a rectangle. |
| 4 | `tests/test_datum_resolution.py::TestDatumOffset::test_datum_offset_field_exists` | float, > 0 | float, == 0.0 | (a) | Retired fitted offset 45.5. |
| 5 | `tests/test_datum_resolution.py::TestDatumOffset::test_np_translates_to_published_range` | `to_published_datum(153.5)` in [98, 114] | renamed `test_to_published_datum_is_identity`: `to_published_datum(x) == x` | (a) | Pinned to retired offset (153.5 - 45.5). |
| 6 | `tests/test_datum_resolution.py::TestDatumOffset::test_offset_is_positive` | offset > 0 | renamed `test_offset_is_zero`: offset == 0.0 | (a) | Retired fitted offset 45.5. |
| 7 | `tests/test_datum_resolution.py::TestDatumReferenceDataConsistency::test_published_np_matches_translation` | computed NP within 8 in of 108.0 | unchanged, strict xfail; gap +17.85 in (125.85 vs 108.0) | (b) | Physics bound; book geometry does not yet reproduce the published NP. Reported in Task 5. |
| 8 | `tests/test_datum_resolution.py::TestDatumReferenceDataConsistency::test_published_cg_range_is_reasonable` | CG fwd/aft within 10 in of 99.0 / 104.0 | unchanged, strict xfail; gap fwd +17.85 in (116.85 vs 99.0), aft +17.85 in (121.85 vs 104.0) | (b) | Physics bound, same NP offset carried into the CG limits. |
| 9 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_canard_span_is_reasonable` | span within 5% of 147.0 in | span == 126.0 in | (a) | 147 is retired. 126 = Roncz core, jig blocks 126 in apart (cobelu ch 30); the 142 in GU span (plans p.54) is reference only. Note: `reference_data.json` `canard_span_in` 147 (labelled raf-cp31) was not found in the CP1-82 text search and is contradicted by the book; left unchanged, flagged for the lead. |
| 10 | `tests/test_physics_regression.py::test_physics_regressions_match_accuracy_report` | matches old `accuracy_report.json` (Phase 5 fit, NP 108.0007) | not changed now | (a) | Baseline is the retired Phase 5 report. Stays red until Task 5 regenerates the report. |
| 11 | `tests/test_precision_validation.py::test_np_precision_2inch` | NP within 2 in of 108.0 | unchanged, strict xfail; gap +17.85 in | (b) | Physics bound (2.0 in tolerance); Phase 5 fit retired. |
| 12 | `tests/test_precision_validation.py::test_cg_fwd_limit_precision` | CG fwd within 1 in of 99.0 | unchanged, strict xfail; gap +17.85 in | (b) | Physics bound (1.0 in tolerance); Phase 5 fit retired. |
| 13 | `tests/test_precision_validation.py::test_cg_aft_limit_precision` | CG aft within 1 in of 104.0 | unchanged, strict xfail; gap +17.85 in | (b) | Physics bound (1.0 in tolerance); Phase 5 fit retired. |
| 14 | `tests/test_regression_lock.py::test_regression_neutral_point_external_truth` (split from `test_regression_neutral_point`) | NP within 2 in of 108.0 (reference_data) | unchanged, strict xfail; gap +17.85 in | (b) | External-truth half of the split. |
| 15 | `tests/test_regression_lock.py::test_regression_neutral_point_drift` (split) | NP within 0.01 in of `LOCKED_NP_PUBLISHED` (108.0007) | `LOCKED_NP_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 16 | `tests/test_regression_lock.py::test_regression_cg_fwd_external_truth` (split from `test_regression_cg_fwd`) | CG fwd within 1 in of 99.0 | unchanged, strict xfail; gap +17.85 in | (b) | External-truth half of the split. |
| 17 | `tests/test_regression_lock.py::test_regression_cg_fwd_drift` (split) | CG fwd within 0.01 in of `LOCKED_CG_FWD_PUBLISHED` | `LOCKED_CG_FWD_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 18 | `tests/test_regression_lock.py::test_regression_cg_aft_external_truth` (split from `test_regression_cg_aft`) | CG aft within 1 in of 104.0 | unchanged, strict xfail; gap +17.85 in | (b) | External-truth half of the split. |
| 19 | `tests/test_regression_lock.py::test_regression_cg_aft_drift` (split) | CG aft within 0.01 in of `LOCKED_CG_AFT_PUBLISHED` | `LOCKED_CG_AFT_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 20 | `tests/test_regression_lock.py::test_regression_values_match_accuracy_report` (split; external half is `test_regression_locked_metrics_all_pass`) | 9 locked metrics are PASS in the report, and each LOCKED_* equals its PASS metric | traceability half: each LOCKED_* equals the report `computed` whatever the grade (passes); PASS half unchanged, strict xfail; 6 PASS, NP/CG fwd/CG aft now FAIL, gap +17.85 in | (a) + (b) | Found in Task 6 after the Task 5 report regeneration (Task 5 verify ran only the report tests, so this went red at 8525552 and was fixed here). The grade requirement is external truth (b); the constant-to-report link is bookkeeping (a). |

## NP gap

Values read from `data/validation/accuracy_report.json` (regenerated 2026-09-29).

| Quantity | Computed (FS in) | Reference (FS in) | Gap (computed - reference, in) | Grade |
|---|---|---|---|---|
| Neutral point | 125.8549 | 108.0 (RAF CP-29 p.18) | +17.8549 | FAIL (tol 2.0 in) |
| CG fwd limit | 116.8532 | 99.0 | +17.8532 | FAIL |
| CG aft limit | 121.8536 | 104.0 | +17.8536 | FAIL |

The geometry is book-true and the NP is checked against the published value, not fitted to it; the +17.85 in gap is reported as found.

The CG limits are computed as the NP minus fixed fractions of the MAC (the retired Phase 5 margins,
still in `core.analysis`), so their gaps mirror the NP gap and are not independent evidence. The
report's `static_margin_pct` moved from 1.91 to 36.05 (reference 12.0); it failed before and still
fails.
