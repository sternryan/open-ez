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
| 2 | `tests/guide/test_layup_geometry.py::test_foam_volume_is_core_minus_cutters` | cutter volumes from `core.intersect(cutter)` on the generator core | cutter volumes from the ruled loft `build_layup` cuts, plus assert loft volume within 1% of generator core; original 1% asserts kept | (c) | Test oracle broken by the new geometry; a fix, not a tolerance change. OCCT boolean flake, repro: build `build_layup(G)`, then call `core.intersect(built["canard.spar_cap_bottom"]["canard.spar_cap_bottom.p1"])` on `CanardGenerator().generate_geometry().val()` three times in one process: volumes 0.0, 32.4, 32.4. Measured (BRepGProp `vol()`): generator core 596.17, ruled-loft base 595.71 (shoelace section 9.456 in² × 63), agree within 0.08%; foam 511.98 = base − 83.73 removed, against 83.75 summed from the cutter intersections. cq `Shape.Volume()` under-reads the BSPLINE core (511.30, section 9.085), a known trap, so never use it on the generator core. |
| 3 | `tests/test_canard_stall_and_downwash.py::TestCanardMAC::test_canard_mac_less_than_root_chord` | MAC < root chord 17.0 and > tip chord 13.5 | renamed `test_canard_mac_equals_chord_for_rectangle`: MAC == `canard_chord`, root == tip | (a) | Pinned to the retired 17.0 / 13.5 taper; the canard is now a rectangle. |
| 4 | `tests/test_datum_resolution.py::TestDatumOffset::test_datum_offset_field_exists` | float, > 0 | float, == 0.0 | (a) | Retired fitted offset 45.5. |
| 5 | `tests/test_datum_resolution.py::TestDatumOffset::test_np_translates_to_published_range` | `to_published_datum(153.5)` in [98, 114] | renamed `test_to_published_datum_is_identity`: `to_published_datum(x) == x` | (a) | Pinned to retired offset (153.5 - 45.5). |
| 6 | `tests/test_datum_resolution.py::TestDatumOffset::test_offset_is_positive` | offset > 0 | renamed `test_offset_is_zero`: offset == 0.0 | (a) | Retired fitted offset 45.5. |
| 7 | `tests/test_datum_resolution.py::TestDatumReferenceDataConsistency::test_published_np_matches_translation` (renamed `test_published_np_is_unverified_not_truth`) | computed NP within 8 in of 108.0 | asserts the NP reference entry is `unverified` and absent from `truth_specs`; the model NP is not compared to 108.0 | (a) | Task 4 audit: the 108.0 (labelled RAF CP-29 p.18) was not found in CP-29/CP-31 or the manual, so it is history, not truth. Was strict xfail (b) with gap +17.85 in; the NP is now NOT GRADED in the report. |
| 8 | `tests/test_datum_resolution.py::TestDatumReferenceDataConsistency::test_published_cg_range_is_reasonable` | CG fwd/aft within 10 in of 99.0 / 104.0 | CG fwd/aft within 10 in of 97.0 / 103.0 (manual chart, om-1980:p28); unchanged bound. Strict xfail after Task 4 (gaps +19.85 / +18.85); after Task 7 (book wing and canard planform) it passes: fwd +8.80 in (105.80 vs 97.0), aft +6.56 in (109.56 vs 103.0); xfail removed | (b) | Physics bound; the reference moved to the manual's values in Task 4 (was 99.0 / 104.0, gap +17.85 in). |
| 9 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_canard_span_is_reasonable` | span within 5% of 147.0 in | span == 126.0 in | (a) | 147 is retired. 126 = Roncz core, jig blocks 126 in apart (cobelu ch 30); the 142 in GU span (plans p.54) is reference only. Note: `reference_data.json` `canard_span_in` 147 (labelled raf-cp31) was not found in the CP1-82 text search and is contradicted by the book; left unchanged, flagged for the lead. |
| 10 | `tests/test_physics_regression.py::test_physics_regressions_match_accuracy_report` | matches old `accuracy_report.json` (Phase 5 fit, NP 108.0007) | not changed now | (a) | Baseline is the retired Phase 5 report. Stays red until Task 5 regenerates the report. |
| 11 | `tests/test_precision_validation.py::test_np_precision_2inch` (renamed `test_np_reference_is_unverified_not_graded`) | NP within 2 in of 108.0 | asserts the NP reference entry is `unverified` and absent from `truth_specs` | (a) | Task 4 audit: 108.0 is unverified, so the NP is not graded against it. Was strict xfail (b), gap +17.85 in. |
| 12 | `tests/test_precision_validation.py::test_cg_fwd_limit_precision` | CG fwd within 1 in of 99.0 | CG fwd within 1 in of 97.0 (om-1980:p28); unchanged bound, strict xfail; gap +2.12 in (99.12 vs 97.0) | (b) | Physics bound (1.0 in tolerance); reference corrected to the manual in Task 4 (was 99.0, gap +17.85 in). Re-triaged after the wing panel convention fix (each panel now runs BL 23.3 to 156.6): gap +19.85 in (116.85 vs 97.0) became +2.86 in. Re-triaged after the wing aspect ratio fix (AR now pairs the panel span with the panel area): gap +2.86 in (99.86 vs 97.0) became +2.12 in (99.12 vs 97.0). |
| 13 | `tests/test_precision_validation.py::test_cg_aft_limit_precision` | CG aft within 1 in of 104.0 | CG aft within 1 in of 103.0 (om-1980:p28); unchanged bound, xfail removed (XPASS); computed 102.91 vs 103.0, delta 0.09 in (103.65, delta 0.65, after the panel fix; 102.91 after the AR fix) | (b) | Physics bound (1.0 in tolerance); reference corrected to the manual in Task 4 (was 104.0, gap +17.85 in). Re-triaged after the wing panel convention fix: the gap was +18.85 in (121.85 vs 103.0) and the corrected planform now lands inside the bound, so the strict xfail XPASSed and was removed. The tolerance is unchanged and no value was fitted to it. |
| 14 | `tests/test_regression_lock.py::test_regression_neutral_point_external_truth` (split from `test_regression_neutral_point`) | NP within 2 in of 108.0 (reference_data) | asserts the NP reference is `unverified`, absent from `truth_specs`, and the report grades the NP metric NOT GRADED | (a) | Task 4 audit: 108.0 is unverified. Was strict xfail (b), gap +17.85 in. |
| 15 | `tests/test_regression_lock.py::test_regression_neutral_point_drift` (split) | NP within 0.01 in of `LOCKED_NP_PUBLISHED` (108.0007) | `LOCKED_NP_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 16 | `tests/test_regression_lock.py::test_regression_cg_fwd_external_truth` (split from `test_regression_cg_fwd`) | CG fwd within 1 in of 99.0 | CG fwd within 1 in of 97.0 (om-1980:p28); unchanged bound, strict xfail; gap +2.12 in (99.12 vs 97.0) | (b) | External-truth half of the split; reference corrected to the manual in Task 4 (was 99.0, gap +17.85 in). Re-triaged after the wing panel convention fix: gap +19.85 in (116.85 vs 97.0) became +2.86 in. Re-triaged after the wing aspect ratio fix (AR now pairs the panel span with the panel area): gap +2.86 in (99.86 vs 97.0) became +2.12 in (99.12 vs 97.0). |
| 17 | `tests/test_regression_lock.py::test_regression_cg_fwd_drift` (split) | CG fwd within 0.01 in of `LOCKED_CG_FWD_PUBLISHED` | `LOCKED_CG_FWD_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 18 | `tests/test_regression_lock.py::test_regression_cg_aft_external_truth` (split from `test_regression_cg_aft`) | CG aft within 1 in of 104.0 | CG aft within 1 in of 103.0 (om-1980:p28); unchanged bound, xfail removed (XPASS); computed 102.91 vs 103.0, delta 0.09 in (103.65, delta 0.65, after the panel fix; 102.91 after the AR fix) | (b) | External-truth half of the split; reference corrected to the manual in Task 4 (was 104.0, gap +17.85 in). Re-triaged after the wing panel convention fix: gap was +18.85 in (121.85 vs 103.0); the corrected planform now lands inside the bound, so the strict xfail XPASSed and was removed. Tolerance unchanged. |
| 19 | `tests/test_regression_lock.py::test_regression_cg_aft_drift` (split) | CG aft within 0.01 in of `LOCKED_CG_AFT_PUBLISHED` | `LOCKED_CG_AFT_PUBLISHED` unchanged for now; re-locked in Task 6 | (a) | Pinned to the retired Phase 5 fit. Stays red until Task 6. |
| 20 | `tests/test_regression_lock.py::test_regression_values_match_accuracy_report` (split; external half is `test_regression_locked_metrics_all_pass`) | 9 locked metrics are PASS in the report, and each LOCKED_* equals its PASS metric | traceability half: each LOCKED_* equals the report `computed` whatever the grade (passes); PASS half unchanged, strict xfail. After Task 4 the report has 12 metrics: 4 PASS (airfoil), 5 FAIL (CG fwd +19.85 in, CG aft +18.85 in, max gross +100 lb, empty weight -110 lb, wing area +28.01 sq ft) and 3 NOT GRADED (NP, static margin, stall speed). Separately, the 9 locked metrics are graded: 4 PASS, 5 FAIL (the 3 NOT GRADED are not locked). Re-triaged after the wing panel convention fix: the report is 5 PASS (4 airfoil + CG aft, delta 0.09 in), 4 FAIL (CG fwd +2.12 in, max gross +100 lb, empty weight -110 lb, wing area 64.71 vs 81.99 sq ft, gap -17.28 sq ft) and 3 NOT GRADED; of the 9 locked metrics, 5 PASS (CG aft joins the 4 airfoil), still short of 9 | (a) + (b) | Found in Task 6 after the Task 5 report regeneration. Counts superseded by rows 39-41: the 4 airfoil PASS became NOT GRADED (airfoil_data unverified); the report is now 2 PASS (CG aft, max gross), 3 FAIL (CG fwd, empty weight, wing area) and 7 NOT GRADED, and of the 9 locked metrics 2 PASS. The grade requirement is external truth (b); the constant-to-report link is bookkeeping (a). Task 4 moved the references and the counts. |
| 21 | `tests/test_precision_validation.py::test_stall_speed_within_5pct` (renamed `test_stall_speed_reference_is_unverified_not_graded`) | first-principles stall speed within 5% of 56 KTAS (areas 94.2 + 15.6 sq ft) | asserts the stall reference is `unverified` and absent from `truth_specs`; the stall speed is still computed from the confirmed areas (81.99 + 12.8 sq ft) and checked only for a physical range | (a) | Task 4 audit: 56 KTAS (labelled CP-29 p.20) was not found in the sources. Computed stall speed moved 53.29 to 57.35 KTAS with the confirmed areas; it is NOT GRADED. |
| 22 | `tests/test_precision_validation.py::test_gross_weight_matches_published` | config gross weight == 1325 lb exactly (om-1980:p4) | unchanged bound (exact match against the reference value); strict xfail removed, now a plain passing test; config `gross_weight_lb` 1425.0 -> 1325.0 | (a) | Resolved 2026-09-29 by lead ruling: the config flight-condition gross weight is the manual's normal max takeoff gross (om-1980:p4). The 1425 lb takeoff-only band (om-1980:p28) stays in `data/mass_ledger.yaml` (`takeoff_only_max_lb`). `test_regression_max_gross_weight` re-locked 1425.0 -> 1325.0. Stall drift lock moved: row 38. |
| 23 | `tests/test_regression_lock.py::test_regression_stall_speed` (split into `test_regression_stall_speed_external_truth` and `test_regression_stall_speed_drift`) | stall speed within 5 KTAS of 56 and within 0.5 KTAS of `LOCKED_STALL_KTAS` 53.2867 | external half asserts the stall reference is `unverified` and the report grades it NOT GRADED; drift half unchanged bound (0.5 KTAS), `LOCKED_STALL_KTAS` re-locked to 57.3507 | (a) | 56 is unverified. The lock was pinned to the retired reference areas (94.2 + 15.6); the confirmed areas are 81.99 + 12.8 sq ft. |
| 24 | `tests/test_accuracy_report.py::test_report_schema`, `test_all_grades_valid`, `test_summary_counts` | reference always numeric; grades in PASS/MARGINAL/FAIL/UNGRADED; summary counts without `not_graded` | a `NOT GRADED` metric has `reference: null` and `reason: "reference unverified"`; `NOT GRADED` is a valid grade; `summary.not_graded` matches the count | (a) | The report shape changed: unverified references are emitted NOT GRADED, counted separately from pass/fail. |
| 25 | `tests/test_accuracy_report_unit.py::test_validate_sources_accepts_reference_data_source` | fixture spec entry `{}` accepted as a source | fixture entry is `confirmed` with a registry `cite`; new test `test_validate_sources_rejects_confirmed_spec_with_bad_citation` | (a) | `validate_sources` now reads specs through `truth_specs` and checks each confirmed `cite`. |
| 26 | `tests/test_datum_resolution.py::TestReferenceDataSchema::test_top_level_structure`, `test_aircraft_specs_have_provenance`, `test_community_builds_array_with_provenance` (renamed `test_community_builds_removed`) | `community_builds` required; specs carry `source_id` + `confidence`; >= 3 community builds | `community_builds` absent; specs carry `status` plus `cite` / `formula` / `was_cited` and no `source_id` | (a) | The removed schema: `community_builds` was unsourced and is deleted in the Task 4 audit. |
| 27 | `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift` | computed within 0.01 in of `LOCKED_NP_PUBLISHED` 125.8549, `LOCKED_CG_FWD_PUBLISHED` 116.8532, `LOCKED_CG_AFT_PUBLISHED` 121.8536 | re-locked: `LOCKED_NP_PUBLISHED` 125.8549 to 123.1360, `LOCKED_CG_FWD_PUBLISHED` 116.8532 to 113.9798, `LOCKED_CG_AFT_PUBLISHED` 121.8536 to 119.0659; bound unchanged (0.01 in) | (a) | Task 6 moved the fuselage stations, the strake LE, and the canard and fuel weight arms to the book, which moved the computed NP and CG limits. Drift locks, not external truth. After the move the external-truth strict xfails (rows 8, 12, 13, 16, 18) still fail with smaller gaps: CG fwd +16.98 in (113.98 vs 97.0), CG aft +16.07 in (119.07 vs 103.0); NP 123.136 is NOT GRADED; static margin 37.15 % MAC (was 36.05). Empty weight is unchanged (640 lb, gap -110 lb; arms do not move weight). NP 123.14 is forward of the book firewall F.S. 125.0 by 1.86 in, so `test_neutral_point_is_forward_of_firewall` still passes; no xfail needed. |
| 28 | `tests/test_geometry_provenance.py::test_canard_is_a_book_rectangle`, `test_book_stations`; `test_provenance_entries_are_well_formed`, `test_sourced_entries_cite_the_registry` (extended); new `test_wing_planform_is_the_book`, `test_wing_root_chord_is_derived_from_the_printed_chords`, `test_canard_planform_is_the_gu_planform_flagged_conflict`, `test_canard_height_above_the_wing_plane`, `test_canard_arm_follows_the_chord`, `test_canard_area_matches_chord_times_span_and_the_manual`, `test_derived_status_is_recognised` | `canard_span == 126.0`; `fs_wing_le` 97.72 (25 deg sweep); source checks only for `book` / `cp-corrected` | `canard_span == 141.6`; `fs_wing_le` 99.19 (22.98 deg sweep, root BL 23.3); `derived` entries need a source that passes `check_citation`; new tests assert every Task 7 value, status and source exactly | (a) | Task 7 moved the wing and canard planform to the book. Pinned to retired numbers (canard span 126, wing sweep 25). `derived` is a new provenance status. |
| 29 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_wing_span_matches_published`, `test_canard_span_is_reasonable` | wing span within 1% of 316.8; canard span == 126.0 | wing span within 1% of 313.2 (om-1980:p3); canard span == 141.6 (GU planform, om-1980:p3; Roncz planform unconfirmed); tolerance unchanged | (a) | 316.8 (26.4 ft) and 126 are retired. Row 9 recorded 126 as the Roncz core; the Roncz overall span is not confirmed, so the GU span is used and flagged `conflict`. |
| 30 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_wing_area_within_published_range` | model wing_area within [80, 140] sq ft | unchanged bound, strict xfail; model wing_area 64.71 sq ft (was 76.02 before the panel fix, 110.0 before row 29), gap -15.29 sq ft under the floor | (b) | Physics bound. The model area is the trapezoid on the book planform (chords 49.90 at BL 23.3 / 20.0 at BL 156.6, panel span 133.3 in, both panels) and excludes the strake and the centre section inside BL 23.3; the manual gives wing area 81.99 sq ft (om-1980:p3), gap -17.28 sq ft, and does not say whether it includes the strakes. Re-triaged after the wing panel convention fix: each panel used to run span/2 outboard of BL 23.3 (tip near BL 180, past the book tip rib at B.L. 157, plans-1980:p126) and now runs BL 23.3 to 156.6, which cut the area from 76.02 to 64.71 sq ft. Not forced toward 81.99. |
| 31 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_wing_aspect_ratio_within_published_range` | model wing AR within [5.5, 8.5] | unchanged bound, now a plain passing test (strict xfail removed); model AR 7.63 (was 10.53 with the mixed definition, 8.96 before the panel fix, 6.34 at 110.0 sq ft) | (b) | Physics bound. AR = (2 * wing_panel_span)^2 / wing_area_sqft = (266.6 in)^2 / 64.71 sq ft: span and area now come from the same planform, the two exposed panels BL 23.3 to 156.6 (the strake and centre section are excluded from both). The old formula divided the full tip-to-tip span squared (26.1 ft) by the panel-only area, mixing two planforms, so AR read high (10.53). The definition was made consistent; the bound was not touched and the model was not forced toward it. |
| 32 | `tests/guide/test_export_glb.py::test_real_export_nests_plies_and_keeps_inches` | max exported BL == 63.0 | max exported BL == 70.8 (canard_span 141.6 / 2); tolerance unchanged | (a) | The M2 layup `semi_span` follows `canard_span`; 63.0 was the retired Roncz-core half span. |
| 33 | `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift` | computed within 0.01 in of `LOCKED_NP_PUBLISHED` 123.1360, `LOCKED_CG_FWD_PUBLISHED` 113.9798, `LOCKED_CG_AFT_PUBLISHED` 119.0659 | re-locked: `LOCKED_NP_PUBLISHED` 123.1360 to 112.5622, `LOCKED_CG_FWD_PUBLISHED` 113.9798 to 105.8012, `LOCKED_CG_AFT_PUBLISHED` 119.0659 to 109.5569; bound unchanged (0.01 in) | (a) | Task 7 moved the wing and canard planform to the book, which moved the computed NP and CG limits. Drift locks, not external truth. NP 112.56 is still forward of the firewall (125.0). |
| 34 | `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift` | computed within 0.01 in of `LOCKED_NP_PUBLISHED` 112.5622, `LOCKED_CG_FWD_PUBLISHED` 105.8012, `LOCKED_CG_AFT_PUBLISHED` 109.5569 | re-locked: `LOCKED_NP_PUBLISHED` 112.5622 to 105.9382, `LOCKED_CG_FWD_PUBLISHED` 105.8012 to 99.1241, `LOCKED_CG_AFT_PUBLISHED` 109.5569 to 102.9092; bound unchanged (0.01 in) | (a) | Two changes moved the computed NP and CG limits. The wing panel convention fix (each panel runs BL 23.3 to 156.6, panel span 133.3 in, area 76.02 to 64.71 sq ft, MAC 39.29 to 39.59 in) took NP to 106.6750, CG fwd 99.8609, CG aft 103.6461. The wing aspect ratio fix (AR 10.53 to 7.63, panel span with panel area; lowers the wing lift slope in the NP calculation) then took them to the final values above. Drift locks, not external truth. Static margin at the aft limit FS 103.0 went from 24.34% to 7.42% MAC (9.28% after the panel fix, before the AR fix). |
| 35 | `tests/test_geometry_provenance.py::test_other_stations_shift_uniformly`, `test_book_stations_block1`; `tests/test_lift_curve_theory.py` and `tests/test_physics_external_validation.py::test_wing_lift_slope_physical_bounds` (engine-replica lift slope) | `fuselage_length == 214.0` (stored field, conflict); lift-slope replicas used `wing_span` in the half-chord sweep term | `fuselage_length == fs_tail - fs_nose` (175.3), a read-only property still provenance-tracked with status `conflict` (tracked explicitly in `test_geometry_provenance.py`); replicas use `2 * wing_panel_span`, matching the engine; new `test_fuselage_length_is_a_read_only_property_not_a_stored_field` | (a) | One fuselage length basis for OpenVSP and analysis; the stored 214.0 was the unshifted internal tail. The panel span is the span the taper acts over. Bounds unchanged. |
| 36 | `tests/test_lift_curve_theory.py::TestLiftCurveSlopeWing::test_anderson_reference_value` | Anderson swept-wing lift slope in [3.8, 4.6] /rad for fixed AR 7.3, LE sweep 25 deg, taper 32/68 (the retired config) | inputs now read from config (exposed-panel AR 7.63, LE sweep 22.98 deg, taper 20.0/49.90); unchanged bound, strict xfail; a = 4.682 /rad, gap +0.082 over the ceiling | (b) | Physics bound. The test is labelled as the Long-EZ wing but had hard-coded the retired planform; tied to config in the Block 1 follow-up so it tests the model. |
| 37 | `tests/test_dbox_deflection.py::TestDBoxWeight::test_dbox_weight_range` (class as in the file) | D-box weight 5-25 lb per wing half at half_span = wing_span/2 (156.6 in) | half_span = wing_panel_span (133.3 in, cantilever length root BL 23.3 to tip); unchanged bound, strict xfail; 4.72 lb, gap -0.28 lb under the floor | (b) | Physics bound. The wing panel convention fix shortened the panel the D-box is integrated over. |
| 38 | `tests/test_regression_lock.py::test_regression_stall_speed_drift` | computed within 0.5 KTAS of `LOCKED_STALL_KTAS` 57.3507 | within 0.5 KTAS of 55.3018 (flight-condition gross weight 1425 -> 1325 lb, om-1980:p4; stall speed scales with sqrt(W)); tolerance unchanged | (a) | Drift re-lock only. The external-truth half (`test_regression_stall_speed_external_truth`) asserts the stall metric is NOT GRADED (row 23); unchanged and passes. Stall reference stays unverified / NOT GRADED. |
| 39 | `tests/test_precision_validation.py::test_roncz_clmax_matches_wind_tunnel`, `test_roncz_alpha_0l_matches_wind_tunnel`, `test_eppler_clmax_matches_wind_tunnel`, `test_eppler_alpha_0l_matches_wind_tunnel` (renamed `..._reference_is_unverified_not_graded`) | config canard CLmax within 0.05 of 1.35, canard alpha_0L within 0.5 deg of -3.0, wing CLmax within 0.05 of 1.45, wing alpha_0L within 0.5 deg of -2.0 (reference_data `airfoil_data`) | each asserts the reference entry is `unverified` and absent from `truth_airfoil`; nothing is compared against 1.35, -3.0, 1.45 or -2.0 | (a) | Block 1 follow-up 2: none of the eight `airfoil_data` values was found in the CP text, cobelu, plans OCR or the public web (docs/block1-source-notes.md), so the airfoil metrics are NOT GRADED. Not an xfail: the metric is not graded, not failing. |
| 40 | `tests/test_regression_lock.py::test_regression_canard_clmax`, `test_regression_wing_clmax`, `test_regression_canard_alpha_0l`, `test_regression_wing_alpha_0l` (each split; external halves are `..._external_truth`) | external-truth half: config value within 0.05 (CLmax) or 0.5 deg (alpha_0L) of the `airfoil_data` reference (1.35, 1.45, -3.0, -2.0); drift half: exact match to `LOCKED_*` | external-truth half asserts the reference is `unverified`, absent from `truth_airfoil`, and the report grades the metric NOT GRADED with reason `reference unverified`; drift half unchanged (exact match to `LOCKED_CANARD_CLMAX`, `LOCKED_WING_CLMAX`, `LOCKED_CANARD_ALPHA_0L_DEG`, `LOCKED_WING_ALPHA_0L_DEG`, no reference read) | (a) | Same audit as row 39. Drift locks need no reference, so they stay. The stall-speed metric's CLmax input (1.35) is also unverified; the metric was already NOT GRADED and its drift lock stays, with the input recorded in the metric notes. |
| 41 | `tests/test_regression_lock.py::test_regression_locked_metrics_all_pass` | 9 locked metrics are PASS in the report (strict xfail; 5 PASS of 9 at row 20) | unchanged expectation and bound, strict xfail; regenerated report has 12 metrics: 2 PASS (CG aft, max gross), 3 FAIL (CG fwd +2.12 in, empty weight -110 lb, wing area -17.28 sq ft) and 7 NOT GRADED (NP, static margin, stall speed, 4 airfoil); of the 9 locked metrics, 2 PASS (CG aft, max gross), CG fwd FAIL, 6 NOT GRADED (NP, stall speed, 4 airfoil) | (b) | Bookkeeping: the 4 airfoil PASS became NOT GRADED (rows 39-40). The xfail reason text now states the new counts. |
| 42 | `tests/test_datum_resolution.py::TestReferenceDataSchema::test_sources_have_required_fields` | `sources` is non-empty, and each entry has `title` and `type` | each entry (if any) has `title` and `type`; the non-empty assertion is removed | (a) | The only two sources (`roncz-wt`, `eppler-report`) were deleted because nothing may cite them (airfoil_data unverified), leaving `sources` as `{}`. The schema check on entries is unchanged. |
| 43 | `tests/test_physics_external_validation.py::TestGeometryAgainstPublishedPlans::test_wing_area_within_published_range` | model wing_area within [80, 140] sq ft (strict xfail, row 30; 64.71 sq ft) | unchanged bound, strict xfail removed (it XPASSed); model wing_area 81.70 sq ft | (a) | Closes row 30. The model's wing area is now the reference area: the gross trapezoid with the straight panel taper (chords 49.90 at BL 23.3, 20.0 at BL 156.6; printed chords 42.7 at BL 55.5, 31.35 at BL 106.25, 20.0 at BL 157, plans-1980:p126) extended to BL 0, where the chord is 55.13, both sides tip to tip. The manual's wing area is 81.99 sq ft (om-1980:p3), gap -0.29 (0.35%), so the manual uses the standard convention (LE/TE extended to the centreline). The report's wing-area metric now grades PASS. The exposed panels alone stay available as `wing_exposed_area_sqft` (64.71). |
| 44 | `tests/test_wing_planform.py::test_wing_area_matches_independent_trapezoid_from_config_fields` (renamed `test_exposed_wing_area_...`), `::test_aspect_ratio_pairs_the_panel_span_with_the_panel_area` (renamed `..._gross_span_with_the_gross_area`), `::test_calculate_mac_uses_the_same_planform`; `tests/test_physics_external_validation.py::TestLiftCurveSlopeSanity::test_wing_ar_consistent_with_published`; `tests/test_geometry_provenance.py` `TRACKED_PROPERTIES` | `wing_area_sqft` == exposed-panel trapezoid (64.71); AR == (2 * panel)^2 / panel area == 7.63; AR replica used the panel span | the exposed-panel trapezoid is compared against `wing_exposed_area_sqft`; AR == span^2 / gross reference area (8.34), with the retired mixed guard now against the exposed area; AR replica uses the full span over `wing_area`; `wing_centerline_chord` is a tracked derived property (provenance `derived`) | (a) | Same change as row 43: `wing_area_sqft` is the reference area and AR pairs the full span with it (one planform, the gross trapezoid). New tests: `test_centerline_chord_extends_the_printed_taper_to_bl_zero`, `test_reference_area_is_the_gross_trapezoid_to_the_centerline` (within 1% of 81.99), `test_exposed_area_fails_the_1pct_reference_check` (gate fails first on the old area), `test_aspect_ratio_is_span_squared_over_reference_area`. |
| 45 | `tests/test_precision_validation.py::test_cg_aft_limit_precision`, `tests/test_regression_lock.py::test_regression_cg_aft_external_truth` | computed CG aft within 1.0 in of 103.0 (om-1980:p28); plain passing tests (102.91) | unchanged bound, strict xfail; computed CG aft 105.47, gap +2.47 in | (b) | Physics bound. The NP weights the wing's lift by the reference area; 64.71 to 81.70 sq ft gives the wing more weight against the canard and moves the NP aft, 105.94 to 108.50. The CG limits are the NP minus fixed Phase 5 MAC fractions (`core.analysis`), so both limits move with it. MAC (39.59 in, panel + strake) and the wing AC are unchanged. |
| 46 | `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift` | computed within 0.01 in of `LOCKED_NP_PUBLISHED` 105.9382, `LOCKED_CG_FWD_PUBLISHED` 99.1241, `LOCKED_CG_AFT_PUBLISHED` 102.9092 | re-locked: 105.9382 to 108.5007, 99.1241 to 101.6866, 102.9092 to 105.4718; bound unchanged (0.01 in) | (a) | Drift locks, not external truth; moved by the reference area (row 45). NP 108.50 is reported NOT GRADED; its closeness to the old unverified 108.0 is not evidence of anything. |
| 47 | xfail reason text only: `tests/test_precision_validation.py::test_cg_fwd_limit_precision` (row 12), `tests/test_regression_lock.py::test_regression_cg_fwd_external_truth` (row 16), `::test_regression_locked_metrics_all_pass` (row 41), `tests/test_lift_curve_theory.py::TestLiftCurveSlopeWing::test_anderson_reference_value` (row 36) | gaps +2.12 in (99.12 vs 97.0); 2 PASS of 9 locked; a = 4.682/rad | gaps +4.69 in (101.69 vs 97.0); 1 PASS of 9 locked (max gross), CG fwd and CG aft FAIL; a = 4.827/rad (AR 8.34) | (b) | Bookkeeping; bounds and strictness unchanged. Regenerated report: 12 metrics, 2 PASS (max gross, wing area), 3 FAIL (CG fwd +4.69 in, CG aft +2.47 in, empty weight -110 lb), 7 NOT GRADED. |
| 48 | `tests/test_stability_checks.py::test_vlm_marker_requires_root_bl_and_panel_span` | `current_vlm_np(data_dir, wing_span, canard_span, wing_root_bl, panel_span)` read `vspaero_native_polars.json` (no NP, no geometry block: always "not run") | `current_vlm_np(data_dir, marker)` reads `vspaero_np.json` (written by `python3.13 scripts/vspaero_np.py`); the marker is `scripts.vspaero_np.geometry_marker(config.geometry)` (spans, wing root BL, panel span, chords, sweeps, washout, incidences, stations, waterlines); dropping wing_root_bl or the panel span still makes the run stale. New: `test_two_method_reads_vspaero_np_json_stale_geometry_is_not_run`, `test_two_method_missing_vlm_file_is_not_run`, `test_two_method_current_vlm_file_grades_by_the_1in_bound` | (a) | The two-method NP check now runs. VSPAERO 3.48.2 VLM (wing panels BL 23.3 to tip + canard, Mach 0, Y-symmetry, alpha -2 to 6 deg, Xref FS 103): NP FS 111.13, least-squares dCMy/dCL -0.2016 (r^2 0.992). Analytic 108.50. Delta 2.63 in against the 1.0 in bound: the check FAILS and is left failing; nothing was tuned. Diagnosis: (1) the analytic formula puts the wing's lift at the panel+strake blended MAC quarter chord, FS 118.70, while weighting it by the gross trapezoid area; the VLM wing alone (no strake, no centre section) has its AC at FS 134.96 (the panel-only MAC quarter chord is 132.69), so the two methods model different wings; (2) the analytic canard downwash factor is the far-field formula with a 1.5 in vertical offset; (3) the VLM's local NP between adjacent alpha points ranges FS 109.2 to 114.0, consistent with the canard wake passing 1.5 in above the wing plane, and a fixed wake gives the same 111.12. Moving Xref to FS 90 gives 111.12 (reference-independent, as it should). Extending the VLM wing to the centreline (diagnostic only, not recorded) gives 112.36. |
| 49 | `tests/test_half_chord_sweep.py` (new: `test_hand_computed_trapezoid`, `test_matches_the_raymer_form_with_the_trapezoids_own_aspect_ratio`, `test_constant_chord_keeps_the_le_sweep`, `test_panel_and_gross_trapezoid_share_the_half_chord_line`); `tests/test_lift_curve_theory.py` (module docstring, `TestLiftCurveSlopeWing.TAPER_RATIO`, `test_physics_engine_matches_anderson` replica, `TestLiftCurveSlopeCanard::test_canard_slope_has_sweep_correction` replica, `test_anderson_reference_value` xfail reason); `tests/test_physics_external_validation.py::TestLiftCurveSlopeSanity::test_wing_lift_slope_physical_bounds` replica | replicas used tan L_c/2 = tan L_LE - 2 c_r (1 - lam)/(b (1 + lam)) (the engine's own term); the helper was fed lam = c_t/c_r of the panel with the gross AR; xfail reason a = 4.827/rad | replicas use tan L_LE - (c_r - c_t)/b of the reference trapezoid; lam = c_t/c_0 with the gross AR; the xfail stays strict, reason a = 4.780/rad vs ceiling 4.6; tolerances (3%, 5%, [3.0, 5.5]) unchanged | (c) | Ledger C1. The replicas copied the engine's formula, so they could not catch it. The new hand-computed test was red on the old term (3 of 4 failing on the numeric assertion) before the fix. The new `core.analysis.half_chord_sweep_tan` is used by the NP and the canard stall-priority check. NP 108.50 to 108.41. |
| 50 | `tests/test_wing_planform.py::test_calculate_mac_uses_the_same_planform` | `calculate_mac()` equals the panel + strake area-weighted blend (MAC 39.59 in; strake at BL 0 to 23.3 with LE FS 50) | `calculate_mac()` equals the MAC of the reference trapezoid by direct numerical integration of c(y)^2 (not the closed form): MAC 40.30 in, LE FS 117.33, AC FS 127.41; the test also checks that planform's area is `wing_area_sqft` | (a) | Ledger C2: one wing planform. The static margin, the CG limits (NP minus fixed MAC fractions) and the canard stall-priority Reynolds number now use the 40.30 MAC; `GeometricParams.canard_arm` uses the same wing AC. NP 108.41 to 116.19. |
| 51 | `tests/test_stability_checks.py::test_vlm_marker_requires_root_bl_and_panel_span` | dropping `wing_root_bl` or `wing_panel_span_in` makes the run stale | also dropping `wing_centerline_chord_in` or `vlm_wing_inboard_bl` makes it stale | (a) | Ledger C2, VLM side. `scripts/vspaero_np.py` records the wing from BL 0 (the reference trapezoid); the af5841d panels-only run lacks both keys and reads as stale. `data/validation/vspaero_np.json` regenerated (OpenVSP 3.48.2): NP FS 112.36, dCMy/dCL -0.2323 (r^2 0.9987), cref 40.30. |
| 52 | `tests/test_canard_stall_and_downwash.py::TestDownwashModel::test_zero_vertical_offset_stronger_downwash`; drift locks `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift`; `tests/test_precision_validation.py::test_cg_aft_limit_precision`, `tests/test_regression_lock.py::test_regression_cg_aft_external_truth`; xfail reason text of `test_cg_fwd_limit_precision`, `test_regression_cg_fwd_external_truth`, `test_regression_locked_metrics_all_pass` | np_h0 > np_h100 (downwash cut the canard term); locks 108.5007 / 101.6866 / 105.4718; CG aft strict xfail (+2.47 in); reasons CG fwd +4.69 in, 1 PASS of 9 locked | np_h0 < np_h100 (106.50 vs 110.49); re-locked 106.5020 / 99.5663 / 103.4190, bound 0.01 in unchanged; CG aft strict xfail removed (it XPASSed): 103.42, gap +0.42 in, bound 1.0 unchanged; CG fwd still strict xfail, gap +2.57 in (99.57 vs 97.0); 2 PASS of 9 locked (max gross, CG aft) | (c) + (a) | Ledger C3: the downwash factor acts on the wing, the aft surface (Raymer eq. 16.9), so more downwash moves the NP forward; the old test encoded the wrong-surface model. The drift locks moved with C1 to C3 (NP 116.19 to 106.50 at C3). The CG aft PASS is NP minus the retired 0.0765 MAC fraction and inherits an NP that the two-method check does not confirm: it is not evidence. Regenerated report: 12 metrics, 3 PASS (CG aft, max gross, wing area), 2 FAIL (CG fwd +2.57 in, empty weight -110 lb), 7 NOT GRADED. |
| 53 | `tests/test_stability_checks.py::test_committed_report_two_method_np_agrees` (new) | none (the failing two-method check had no test) | committed report `two_method_np.status == "pass"`, strict xfail: analytic 106.50 vs VLM 112.36, delta +5.86 in, bound 1.0 in | (b) | The check fails after C1 to C3 and is left failing; see the reconciliation section for the diagnosis (far-field full-span downwash). The bound is unchanged. |
| 54 | `tests/test_partial_span_downwash.py` (new, 6 tests: hand-computed near-field point, outboard upwash, far-field centreline value, spanwise average over a wider aft span, zero net over an unbounded span, h -> 0 continuity); drift locks `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift`; `tests/test_precision_validation.py::test_cg_aft_limit_precision`, `tests/test_regression_lock.py::test_regression_cg_aft_external_truth`; xfail reason text of `test_cg_fwd_limit_precision`, `test_regression_cg_fwd_external_truth`, `test_regression_locked_metrics_all_pass`, `tests/test_stability_checks.py::test_committed_report_two_method_np_agrees` | none (new); locks 106.5020 / 99.5663 / 103.4190; CG aft plain passing (103.42, +0.42 in); reasons CG fwd +2.57 in, 2 PASS of 9, two-method +5.86 in | re-locked 110.6822 / 103.7465 / 107.5993, bound 0.01 in unchanged; CG aft strict xfail restored, 107.60 vs 103.0, gap +4.60 in, bound 1.0 unchanged; CG fwd still strict xfail, +6.75 in (103.75 vs 97.0); 1 PASS of 9 locked (max gross); two-method still strict xfail, analytic 110.68 vs VLM 112.36, +1.68 in, bound 1.0 unchanged | (a) + (b) | Ledger C4: the far-field full-span canard downwash (0.306) is replaced by a horseshoe-vortex (Biot-Savart) chord-weighted average over the wing span (0.0899), method fixed in the ledger before the run. NP 106.50 to 110.68. The CG limits are NP minus the retired MAC fractions and move with it; the CG aft PASS at row 52 was not evidence and its loss is not either. Regenerated report: 12 metrics, 2 PASS (max gross, wing area), 3 FAIL (CG fwd +6.75 in, CG aft +4.60 in, empty weight -110 lb), 7 NOT GRADED. |
| 55 | `tests/test_ssot_weights.py::test_structural_items_from_config`, `tests/test_physics_external_validation.py::TestGrossWeightSanityCheck` (both empty-weight sums), `tests/test_geometry_provenance.py::test_weight_arms_shift_uniformly`, `scripts/generate_accuracy_report.py` (empty-weight sum) | read `sw.landing_gear_weight_lb` (45) and `sw.landing_gear_arm_in` (84.5, shifted from 130.0) from `StructuralWeightParams`; the arms test listed `landing_gear_arm_in` among the uniformly shifted arms | read the decomposed gear rows from the ledger (`core.ledger.gear_rows`, `gear_cg`): main strut 22 lb, nose strut 2.8 lb, wheels and brakes (unsourced) 20.2 lb, total 45.0 lb unchanged; `landing_gear_arm_in` dropped from the arms list; bounds (200 to 700, 600 to 1200 lb) unchanged | (a) | Block 2 M2.3 Task 4 removed the unsourced lump (house rule: no free constants). The weight items assert the same thing in meaning, now per row. No tolerance moved and no test failed. |
| 56 | none failed. Recorded because it moves a computed value: the physics empty-structure CG (`PhysicsEngine` weight items, fixed structure plus propulsion, 640.0 lb) | 103.35 in (published datum) with the gear lump at 45 lb at F.S. 84.5 | 104.77 in, +1.42 in aft, empty weight unchanged at 640.0 lb | (a) | The gear rows moved aft: main strut 22 lb and the unsourced wheels row 20.2 lb sit at the axle station F.S. 110.5 (p50, p171), the nose strut 2.8 lb at F.S. 17 (p171; conflict with the manual's about 20). The lump's 84.5 was an unsourced shift of 130.0. The wheels row's arm is unsourced and only placed at the axle so the weight does not drop. No test pins this CG, the accuracy report's values are unchanged (regenerated and diffed: only the timestamp differs), and no bound was changed. The envelope limits derive from the NP, not from this CG. |
| 57 | `tests/test_mass_ledger.py::test_lower_bound_weight_is_at_foam_and_glass_scale` (split out of `test_lower_bound_cg_is_the_moment_sum_over_core_sourced_parts`, bound unchanged) | fuselage lower-bound weight 10 < w < 30 lb (24.8 lb at FS 63.8) | 33.2 lb | (b) | The chapter 7 skins (two crossed UND plies over both sides and the bottom, the third ply forward of the front seat bulkhead, the F.S. 60–110 strip) are sourced glass (RA5177 7.02 oz/yd², resin ½ the cloth, p21) and land on the side and bottom rows; the roll-over adds 0.66 lb. The 30 lb ceiling predates them. Strict xfail; the bound is not widened. |
| 58 | `tests/test_mass_ledger.py::test_lower_bound_cg_is_the_moment_sum_over_core_sourced_parts` (the excluded set only; new `test_lower_bound_leaves_out_parts_heavier_than_their_prototype`) | lower-bound exclusions: firewall, longerons, belt and roll-over inserts, step | the same plus `f22` and `f28` | (b) | The modelled lower bounds (F22 2.00 lb, F28 0.40 lb) exceed the CP26 prototype weights (1.44, 0.19 lb), so they are not a lower bound against that source. They are left out with the reason "under review"; the prototype numbers are not substituted. The excess (glass schedule or R250 core density) is for the ledger-closure test. The 30 lb sanity bound is unchanged (still a strict xfail). |
| 59 | `tests/test_elevators_kin.py` (spans, hinge placement, count note; new `tube_span` tests), `tests/test_elevators_book.py` (left foam no longer crosses Y=0, left tube does; left hinge plates 3 -> 2; CS-11 left at the tube end), lab e2e `test_ch12_installed_elevators...` label and `test_the_canard_and_elevators_stand_installed...` span checks | left elevator span (-65.0, +7.7) crossing the centreline; 5 hinge stations placed; one elevator label | foam spans mirror (right 9.3..65.0, left -65.0..-9.3); the left TUBE alone is (-65.0, +7.7); 4 hinge stations placed (9.2 is 0.1 in outside the foam on both sides) | (c) | Cobelu C-1 re-read by the captain (Evidence correction 3): the 72.7 in is the left tube, the foam is 55.7 in on both sides. Both foam inboard ends (`elevator_inboard_bl_right_in`, `_left_in`) are now flagged `conflict`: the drawn stock end vs the fuselage sides (about +/-11.5 at F22), which the 1/16 in clearance puts the trimmed end at; unresolved, not moved. No tolerance widened to place the 9.2 hinges. Lab: cove limited to the foam span, installed label says the span is unresolved. |
| 60 | `tests/test_geometry_provenance.py::test_book_stations`, `::test_wing_planform_is_the_book`, `::test_wing_root_chord_is_derived_from_the_printed_chords`; `tests/test_wing_planform.py::test_panel_runs_from_the_root_bl_not_span_over_two_outboard_of_it`, `::test_tip_leading_edge_fs_is_wing_le_plus_panel_times_tan_sweep`, `::test_centerline_chord_extends_the_printed_taper_to_bl_zero`, `::test_exposed_area_fails_the_1pct_reference_check`, `::test_aspect_ratio_is_span_squared_over_reference_area`; `tests/test_wing_stations.py::test_analysis_fields_carry_the_book_value_in_a_note` (renamed); `tests/test_winglet_stations.py::test_analysis_fields_carry_the_book_values` (renamed) | `wing_span` 313.2, `wing_root_bl` 23.3, `wing_root_chord` 49.90, `winglet_height` 16.0, `winglet_root_chord` 20.0, `winglet_tip_chord` 12.0 (status unsourced for the root BL and winglet fields); `fs_wing_le` 99.19; panel span 133.3; exposed area 64.71 sq ft; AR 8.34 | `wing_span` 314.0 (derived, 2 x BL 157, p126), `wing_root_bl` 23.0 (book, p118, p119, p126, p147), `wing_root_chord` 49.97 (the same straight taper at BL 23.0), `winglet_height` 47.0 (book, p135), `winglet_root_chord` 27.1 (derived, p135), `winglet_tip_chord` 11.4 (derived-unsourced); `fs_wing_le` 99.06; panel span 134.0; exposed area 65.11 sq ft; AR 8.36; centreline chord 55.11 | (a) | The M2.8 fold-ins (spec section 3). The tests pinned the retired analysis values; expectations moved to the new values and the status asserts to the new statuses, no tolerance changed. `wing_root_chord` moved with the root BL because the bound in `test_centerline_chord_extends_the_printed_taper_to_bl_zero` (0.02 in) fails if the chord stays at the BL 23.3 value (0.08 in off the printed taper). The OM span 26.1 ft = 313.2 in stays a noted conflict (26.17 ft rounds to 26.2). The exposed area still fails the 1 percent reference check. |
| 61 | `tests/test_regression_lock.py::test_regression_neutral_point_drift`, `test_regression_cg_fwd_drift`, `test_regression_cg_aft_drift`; `data/validation/accuracy_report.json` regenerated; xfail reason text only in `tests/test_regression_lock.py` (three) and `tests/test_precision_validation.py` (two) | `LOCKED_NP_PUBLISHED` 110.6822, `LOCKED_CG_FWD_PUBLISHED` 103.7465, `LOCKED_CG_AFT_PUBLISHED` 107.5993; static margin 19.0624 percent; MAC 40.3005; wing area 81.6999; CG fwd gap +6.75, CG aft gap +4.60 | NP 110.7880, CG fwd 103.8536, CG aft 107.7056; static margin 19.3285 percent; MAC 40.2929; wing area 81.8952 (error 0.09, 0.12 percent); CG fwd gap +6.85, CG aft gap +4.71 | (a) | Caused only by the row 60 values (the analytic NP reads `wing_span`, `wing_root_bl`, the root chord and the wing LE). The locks track the report's computed values, as they did at rows 27, 33, 34, 46 and 52; no bound changed and the strict xfails stay strict (CG fwd and aft still fail against 97 and 103, the loaded envelope). The winglet fields are not read by the analytic NP. |
| 62 | `tests/test_stability_checks.py::test_committed_report_two_method_np_agrees` (xfail reason text only); `data/validation/vspaero_np.json` re-run | analytic 110.68, VLM 112.36, delta +1.68 in; the stored VLM run carried the old geometry | analytic 110.79, VLM 112.41, delta +1.62 in against the 1.0 in bound | (b) | `scripts/vspaero_np.py` ran locally on python3.13 (OpenVSP 3.48.2) against the new planform; the run is committed and its geometry marker matches the config, so the report reads `fail`, not `not run`. The bound is unchanged and the xfail stays strict. The VLM leg models the wing and canard only (no strakes, fuselage or winglets), so the winglet fold-ins do not enter it. |
| 63 | none failed. Recorded because it relabels a target: README.md, AGENTS.md, TODOS.md, `docs/block1-report.md` (one bullet) and the comment above `empty` in `data/mass_ledger.yaml`; `tests/test_m28_weight_flags.py::test_om_sample_empty_is_the_closure_target_not_the_loaded_band` (new) | prose said empty weight and CG limits 'wait on the Block 2 ledger' and the ledger target read as FS 97 to 103 | the empty-weight target is the OM sample empty airplane, 730 lb at FS 111.7 (om-1980:p25, p35); FS 97 to 103 is the LOADED CG envelope (om-1980:p28); the computed CG limits follow the NP and do not wait on the ledger; the empty CG is never graded against 97 to 103 | (c) | The empty CG 111.7 is behind the 103 aft limit by the book's own sample. No test graded the empty CG against the band (searched `tests/`, `core/`, `scripts/`, `guide/`); the wording in four docs conflated the two. No numeric bound moved. The accuracy report's `empty_weight_lb` is still graded against the manual's approximate 750 lb normally equipped (om-1980:p4), which is a different configuration from the 730 lb sample. |

## Two-method NP reconciliation (2026-09-29, follow-up)

Written before any change was made or any comparison was run. Each change below is justified by a
textbook relation or by consistency between the two methods, not by its effect on the numbers; the
NP before and after each change is recorded in the table at the end of this section as it is run.

**One configuration for both methods.** Wing = the gross reference trapezoid: the straight panel
LE and TE extended to the centreline (chord 55.13 at BL 0, 20.0 at the tip BL 156.6, LE sweep
22.98 deg), both halves, 81.70 sq ft, AR 8.34. This is the planform whose area is already
`wing_area_sqft` (the reference area, within 0.4% of om-1980:p3). Canard = the config rectangle
(141.6 in x 13.02 in). No strakes, no fuselage, no winglets, in either method. The strakes are
excluded from both rather than modelled in both because the config has no strake planform that a
VLM could be given without inventing geometry: `StrakeConfig.fs_trailing_edge` (99.5) is
converted-unsourced, `calculate_mac()` places the strake at BL 0 to 23.3 with its LE at FS 50
blending into a root chord whose LE is at FS 99.2 (not a physical outline), and the book strake
(LE FS 50 at the fuselage side, 73.3 at BL 23, 99.5 at BL 45, meeting the wing LE at BL 58) exists
only in comments, with no fuselage-side BL and no TE. Consequence stated up front: the real strakes
add lifting area ahead of the wing, so the modelled configuration is not the whole aircraft; both
methods omit the same thing, so the comparison is like for like.

- **C1, half-chord sweep.** Raymer (Aircraft Design, sec. 7, sweep conversion) and DATCOM
  (sec. 2.2.2): tan L_n = tan L_m - (4/A)(n - m)(1 - lam)/(1 + lam). With m = 0 (LE), n = 1/2 and
  the trapezoid's own A = 2b/(c_r(1 + lam)) (b the full span), this is
  tan L_c/2 = tan L_LE - (c_r - c_t)/b. Geometrically: the half-chord line sits c/2 aft of the LE,
  so across a semispan b/2 it falls (c_r - c_t)/2 behind the LE line, a tangent change of
  (c_r - c_t)/b. `core/analysis.py` used 2 c_r (1 - lam)/(b (1 + lam)), which is the correct term
  times 2/(1 + lam): 1.43x for the wing (lam = 0.40), no effect on the constant-chord canard
  (lam = 1). The panel and the gross trapezoid share the same half-chord line (the gross trapezoid
  extends the panel taper linearly), so the corrected value does not depend on which is used. The
  fix goes in one helper used by both the NP and the canard stall-priority check, red-first
  against a hand-computed trapezoid. The test helper `_le_sweep_to_half_chord_sweep` in
  `tests/test_lift_curve_theory.py` is the textbook form but was fed the panel taper (c_t/c_r at
  BL 23.3) with the gross-trapezoid AR, mixing planforms; it now gets lam = c_t/c_0 of the same
  trapezoid as the AR.
- **C2, one wing planform in the analytic method.** The analytic NP weighted the wing's lift by the
  gross reference area but placed it at the quarter chord of a panel+strake blended MAC (FS 118.70).
  The area and the AC must describe the same planform. For a straight-tapered wing the subsonic AC
  is at the quarter chord of the MAC (Raymer sec. 4, MAC of a trapezoid; Anderson, Fundamentals of
  Aerodynamics, sec. 5; Etkin and Reid sec. 2): c_bar = (2/3) c_0 (1 + lam + lam^2)/(1 + lam),
  y_bar = (b/6)(1 + 2 lam)/(1 + lam), x_LE(y_bar) = x_LE(0) + y_bar tan L_LE, x_ac = x_LE +
  c_bar/4, all of the gross trapezoid. `calculate_mac()` returns this c_bar and x_LE, so the static
  margin is normalised by the MAC of the reference planform (the textbook SM = (x_np - x_cg)/c_bar
  pairs c_bar with S_ref) and equals the VLM's cref. The lift slope already uses the gross AR.
- **C2, same planform in the VLM.** The recorded VSPAERO run models the wing from BL 0 with the
  centreline chord (the gross trapezoid), not the exposed panels from BL 23.3. The VLM geometry
  marker gains `wing_centerline_chord_in` and `vlm_wing_inboard_bl` (0.0), so the previous
  panels-only run (no such keys) reads as stale, not current.
- **C3, downwash on the aft surface.** The analytic NP multiplied the CANARD term by
  (1 - d eps/d alpha). In the two-surface neutral point (Raymer eq. 16.9; Etkin and Reid sec. 2.3;
  Nelson, Flight Stability and Automatic Control, sec. 2.4) that factor belongs to the aft surface,
  which flies in the forward surface's downwash; for a canard layout the aft surface is the wing.
  The canard's own trailing vortices are already in its finite-AR slope a_c. The factor moves to the
  wing term: NP = [a_w S_w (1 - d eps/d alpha) x_w + a_c S_c x_c] / [a_w S_w (1 - d eps/d alpha) +
  a_c S_c]. The d eps/d alpha expression itself (far field 2 a_c/(pi A_c), times
  1/(1 + (2h/b_c)^2)) is unchanged. Approximations it keeps, recorded here and not changed: (i) the
  far-field value is applied to the whole wing, though the canard (141.6 in) spans 45% of the wing
  (313.2 in) and the wing outboard of the canard tip vortices sees upwash; (ii) the wing's upwash
  at the canard is omitted; (iii) the canard height h = 1.5 in is the flagged W.L. conflict and is
  not touched.

| Step | Analytic NP (FS) | VLM NP (FS) | Delta (VLM - analytic, in) | Two-method (bound 1.0 in) |
|---|---|---|---|---|
| before (af5841d) | 108.50 | 111.13 (panels only) | +2.63 | FAIL |
| after C1 | 108.41 | 111.13 (panels only; C1 does not touch the VLM) | +2.72 | FAIL |
| after C2 | 116.19 | 112.36 (gross reference wing) | -3.83 | FAIL |
| after C3 | 106.50 | 112.36 | +5.86 | FAIL |

**Result: the check still FAILS, and is left failing** (strict xfail, row 53). Nothing was tuned;
the canard waterline was not touched. Static margin at the manual's aft limit FS 103:
(106.50 - 103.0)/40.30 = 8.69% MAC (MAC now the reference trapezoid's, 40.30 in).

**Diagnosis of the remaining +5.86 in** (VSPAERO diagnostics, same geometry, not recorded runs):

| Component | Analytic | VLM | Agreement |
|---|---|---|---|
| wing alone AC (FS) | 127.41 (reference MAC quarter chord) | 128.28 | 0.87 in |
| wing alone lift slope (/rad, on S_ref) | 4.780 | 4.827 | 1.0% |
| canard alone AC (FS) | 21.96 | 21.77 | 0.19 in |
| canard lift slope x S_c/S_ref (/rad) | 0.820 | 0.808 | 1.5% |
| combined lift slope (/rad) | 4.136 | 5.555 | analytic 26% low |
| wing factor (1 - de/da), net | 0.694 | 0.953 (implied: the value that puts the isolated VLM components at the VLM NP) | |

Each surface alone agrees to within an inch and 1.5%; the whole gap is the interference model. The
analytic method applies the far-field downwash 2a_c/(pi A_c) = 0.306 to the entire wing; the VLM's
net effect (canard downwash on the wing plus wing upwash on the canard) is about 0.05. The
canard spans 45% of the wing, the wing outboard of its tip vortices sees upwash, and the far-field
value is the fully developed wake, not the value at a wing whose AC is ~105 in behind the canard AC.
C3 put the factor on the right surface, and that exposed its magnitude as the dominant error. The
canard height is not the driver in the analytic method (NP 106.50 at h = 0, 110.49 at h = 100 in;
the 1.5 in offset changes the vertical factor by 0.04%); in the VLM the wake passes 1.5 in above the
wing and a fixed wake gives 112.42, so wake relaxation is not the driver either. The next honest
step is a partial-span downwash model with a textbook source (e.g. DATCOM 4.4.1 or a
horseshoe-vortex average over the wing span) chosen before it is run, and the book W.L. conflict
resolved; neither is done here.

### C4, partial-span canard downwash on the wing (method fixed before running)

Written before the method was implemented or the comparison run. One method, one run; the result
is recorded whatever it is, and the method is not revised to chase the VLM.

**Method: the canard's trailing system as a single horseshoe vortex, its induced downwash on the
wing by Biot-Savart, averaged over the wing span by strip theory.** Sources: the horseshoe-vortex
model of a lifting surface and its downwash field (McCormick, Aerodynamics, Aeronautics and Flight
Mechanics, the downwash-at-the-tail estimate, with the vortex span b' = (pi/4) b for an elliptic
loading; Anderson, Fundamentals of Aerodynamics, sec. 5, the horseshoe vortex and b' for the
elliptic wing); the straight-segment Biot-Savart law (Katz and Plotkin, Low-Speed Aerodynamics,
sec. 2 and 10; Anderson sec. 5). Reason for this choice over the alternatives: DATCOM 4.4.1 and
Raymer's canard treatment give a downwash gradient at one point (the tail's MAC or plane of
symmetry) for an aft surface much smaller than the forward one; here the aft surface is 2.2x the
canard's span, and the quantity that matters is the average over a wing whose outboard 55% lies
outside the canard's tip vortices, where the flow is upwash. The horseshoe estimate is the
textbook model that gives that sign change explicitly and is the same singularity model the VLM
discretises, so it replaces the far-field constant without borrowing anything from the VLM run.

Equations (x aft, y starboard, z up; canard bound vortex on the canard quarter-chord line):
- Vortex semi-span s = b'/2 = (pi/8) b_c. Circulation from the canard lift L_c = rho V Gamma b',
  so Gamma / V = C_Lc S_c / (2 b').
- Semi-infinite trailing leg from (0, +-s, 0) to x = +inf, at a point (x, y, z), with
  d_y = y -+ s, r^2 = d_y^2 + z^2: w_z = +-(Gamma / (4 pi r^2)) d_y (1 + x / sqrt(x^2 + r^2))
  (+ for the starboard leg, which runs aft; - for the port leg).
- Bound segment from (0, -s, 0) to (0, +s, 0): with rho^2 = x^2 + z^2,
  w_z = -(Gamma x / (4 pi rho^2)) [(y + s)/sqrt((y + s)^2 + rho^2) - (y - s)/sqrt((y - s)^2 + rho^2)].
- Local downwash angle eps(y) = -w_z(y) / V, so d eps/d alpha (y) = a_c S_c / (2 b') * (-w_z/Gamma)(y).
  Far downstream on the centreline this is a_c S_c / (pi b'^2), the horseshoe's centreline value.
- Strip theory on the wing: the lift lost to the canard's wash is a_w (1/S_w) integral c(y) eps(y) dy,
  so the wing factor is 1 - d eps/d alpha_avg with the chord-weighted average
  d eps/d alpha_avg = integral_{-b_w/2}^{b_w/2} c(y) (d eps/d alpha)(y) dy / integral c(y) dy.
  Each strip is evaluated at its own quarter-chord station (x(y) = wing quarter-chord FS at |y| minus
  the canard quarter-chord FS) and at z = the canard height above the wing plane
  (`canard_vertical_offset_in`, the flagged 1.5 in, not touched). c(y) and x(y) are the reference
  trapezoid's (ledger C2), both halves, BL 0 to the tip. Trailing legs straight aft in the canard
  plane (fixed wake), no rollup, no vortex core.
- The NP formula is otherwise unchanged (C3): NP = [a_w S_w (1 - d eps/d alpha_avg) x_w +
  a_c S_c x_c] / [a_w S_w (1 - d eps/d alpha_avg) + a_c S_c]. The previous far-field factor
  2 a_c / (pi A_c) / (1 + (2h/b_c)^2) is retired from the NP.

Kept approximations, stated up front: (ii) the wing's upwash at the canard is still omitted (it
moves the NP forward, the VLM includes it); the trailing-leg singularity at the canard tip
stations is regularised only by z = 1.5 in, so the upwash just outboard of each tip is peaked; the
horseshoe is a single-vortex model of an elliptic spanload, not the rectangular canard's actual
loading.

Prediction procedure: implement the average red-first against a hand-computed single horseshoe
(closed-form spanwise average of the trailing legs far downstream over an aft span wider than the
vortex), then regenerate the accuracy report (the VLM is not re-run); record d eps/d alpha_avg, analytic NP before (106.50) and after, the VLM NP (112.36, the
committed run, unchanged: the VLM geometry does not change), the gap, and the check status against
the unchanged 1.0 in bound. If within 1.0 in, row 53's strict xfail comes off; if not, it stays and
the residual is diagnosed, with no second method.

**C4 result (one run, recorded as found).**

| Step | d eps/d alpha on the wing | Analytic NP (FS) | VLM NP (FS) | Delta (VLM - analytic, in) | Two-method (bound 1.0 in) |
|---|---|---|---|---|---|
| before (after C3) | 0.306 (far field, whole span) | 106.50 | 112.36 | +5.86 | FAIL |
| after C4 | 0.0899 (horseshoe, chord-weighted over the wing span) | 110.68 | 112.36 (committed run, not re-run) | +1.68 | FAIL |

The check still FAILS and row 53's strict xfail stays (reason text updated; bound unchanged). Static
margin at the manual's aft limit FS 103: (110.68 - 103.0)/40.30 = 19.06% MAC. Inside the canard's
vortex span (BL +-55.6) the wing sees downwash (0.274 on the centreline; chord-weighted contribution
+0.245), outboard it sees upwash (contribution -0.155), net 0.0899. Strip count converged to 1e-10
(4k, 40k, 400k strips per vortex semispan). The first implementation used equal strips across the
whole span; at h = 0 a strip midpoint fell next to a trailing leg and the NP jumped to 116.86
against 110.66 at h = 0.01 in. That is a quadrature defect in the same integral, not a method
change: strips now have edges on the vortex stations so each leg is straddled symmetrically (a
principal value at h = 0), red-first in `test_wing_average_is_continuous_as_the_canard_height_goes_to_zero`;
the h = 1.5 result was the same to 1e-10 before and after. NP vs h: 110.66 (h 0), 110.68 (1.5),
111.54 (100): the canard height is still not the driver.

**Diagnosis of the remaining +1.68 in** (diagnostics only, none adopted; no second method was run
against the check):
- For the analytic NP to reach the VLM's within the 1.0 in bound, d eps/d alpha would have to be
  at most 0.044 (0.047 is the VLM's implied net, above); C4 gives 0.0899. The kept omission (ii),
  the wing's upwash at the canard, raises the canard's effective slope and moves the NP forward,
  so it cannot close this gap; it widens it.
- What C4 leaves out that points aft: the formula applies the canard's wash to the wing's lift
  magnitude only, so the lift it removes and adds is placed at the wing AC (FS 127.41). On a swept
  wing the lost lift is inboard (forward) and the gained lift outboard (aft): the chord-weighted
  centroid of the wash-induced lift change, integral c eps x_qc dy / integral c eps dy, sits at
  FS 94.45, far forward of the wing AC because the net is a small difference of a forward loss and
  an aft gain. Placing that increment at its own centroid (the same strip integral, moment instead
  of force) gives NP 113.42: -1.06 in past the VLM on the other side. The VLM does resolve this
  moment. It is recorded as the leading candidate for the residual, not adopted: adopting it now
  would be a second method chosen after seeing the first result, and it overshoots by about as
  much as C4 undershoots, so it is not by itself the answer either.
- Other single-vortex simplifications (b' = (pi/4) b_c for an elliptic load on a rectangular canard,
  no rollup, no vortex core, fixed wake) are named, not quantified.

## NP gap

Superseded by Block 1 (2026-09-29): 108.0 is unverified; NP 112.56 is reported, not graded; CG references are 97/103 from om-1980:p28; see docs/block1-report.md.

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

## Owner by-eye check (2026-09-29)

Plans p.171 back-cover 3-view, read by the owner:
- **F.S. 18.7 at B.L. 71**, marked at the canard tip leading edge in plan view. Confirms
  `fs_canard_le = 18.7`; provenance raised to high confidence.
- **B.L. 71 is the tip station**, i.e. a 142 in total span. That is the GU canard span (p.54); the
  1980 first edition predates the Roncz canard. The Roncz core stays 126 in (BL ±63) with tips not
  modelled; the Roncz tip station is not confirmed by this drawing.
- **W.L. 18.9** is marked at the canard in the side view. The config's `canard_le_wl = 12.0` is
  unsourced, and cobelu template sheet C-3 labels **W.L. 19.8**. 18.9 vs 19.8 may be a digit
  transposition in one source or two different reference points (e.g. chord line vs a template
  datum). Not changed here: a Block 1 item.

## CP26 weight list attribution (M2.5 round 3)

| Row | Was | Is | Numbers |
|---|---|---|---|
| `prototype_weights` (F22 1.44, F28 0.19, panel 2.13, spar 29.3 lb) | cited as the RAF prototype, CP26 page 2 | Mike and Sally Melvill's builder airplane N26MS ("Mike and Dick's Long-EZ's"), CP26 printed page 3 | none change |

The data key stays `prototype_weights`; the cites, notes, lab readout and excluded-reason string now say "builder weight" and "N26MS".

## Wing LE 125.61 against 113.9 (M2.7, closed)

| Number | What it is | Source | Status |
|---|---|---|---|
| 113.9 | wing LE FS at BL 58, the strake and wing LE kink | CP25 LPC 7 (`cp-text:p25`); `plans-1980:p171` prints 113.4 | kept: `wing_le_anchor`. It agrees with p126: 112.9 + 2.5 tan 22.98 = 113.96 |
| 112.9 | wing LE FS at BL 55.5 | `plans-1980:p126` | book, `wing_book_le_fs_bl_55_5` |
| 125.6 | FS of the FC1 foam edge at BL 23, the shear web forward face | `plans-1980:p126` | book, `wing_book_shear_web_fwd_fs`; not a wing LE (p118 prints the same figure as a jig spacing, which is a different quantity) |
| 125.61 | the retired fitted value (old internal frame, aimed at a neutral-point target) | git history, calibration commit | no book meaning; it stays retired. Its nearness to 125.6 is a coincidence |

The two numbers named in the open question are different points, so there is nothing to choose between. No value or test moved.
The same milestone carries two conflict pairs on the wing (the BL 106.25 LE label 134.95 against 134.45 derived, and the aileron
inboard end BL 54.3 on p171 against 55.5 on p124) and records the analysis fields that match no page (`wing_washout`,
`winglet_height`, `winglet_root_chord`, `winglet_tip_chord`) as `unsourced` without changing them: moving the analysis planform moves the NP and belongs to Block 3.

## Analysis fold-ins landed (M2.8, closed)

M2.7 recorded `wing_span`, `wing_root_bl`, `wing_washout` and the `winglet_*` analysis fields as matching no page and left them. M2.8 moved the five the book settles (rows 60 to 62): `wing_span` 314.0, `wing_root_bl` 23.0, `winglet_height` 47.0, `winglet_root_chord` 27.1, `winglet_tip_chord` 11.4 (derived-unsourced, scaled off the 1/5 drawing). `wing_washout` 1.0 is not settled by the book and stays. `wing_weight_lb` 85.0 stays as well, flagged as a conflict with 2 x 64 lb (CP26 p3) in `WEIGHT_PROVENANCE`; the engine arm and mass fields and the single electrical row are flagged there too, values unchanged, for ledger closure.
