# Block 1 report: baseline truth

Range: `d308d44..HEAD`, 2026-09-29. Citations are `<registry id>:p<page>` (`data/sources/registry.yaml`).
Source notes: `docs/block1-source-notes.md`. Test-by-test changes: `docs/geometry-correction-ledger.md`.

## Follow-up round (lead rulings)

Four commits after `6b94177` apply five lead rulings: `3e48ca3` (captain log and report), `774204c`
(wing panels and fuselage length), `a704dfa` (gross weight and static margin), `e038f65` (airfoil_data audit).
(1) Wing panels run root BL 23.3 to tip BL span/2 156.6 (panel 133.3); new properties `wing_tip_bl`,
`wing_panel_span`, `wing_area_sqft`; AR = (2 * panel)^2 / panel area. (2) `fuselage_length` is a property,
`fs_tail - fs_nose`, used by both VSP builders. (3) Config gross weight 1425 to 1325 (om-1980:p4); 1425 stays the
ledger's takeoff-only band. (4) One static margin: metric and check both use the ledger aft limit FS 103.
(5) `airfoil_data` audited: all eight values unverified, sources deleted, the four airfoil metrics NOT GRADED.
Ledger rows 12, 13, 16, 18, 20, 22, 30, 31, 34 to 42 carry the test-level changes.

## Follow-up (2026-09-29): reference wing and the two-method NP

Two commits after `c866d50`: `af5841d` (wing reference area to the centreline; the VSPAERO NP leg
runs) and the two-method reconciliation commit (ledger C1 to C3, rows 43 to 53).
Values below are current; the sections that follow were updated in place where they state a
current value, with the earlier value kept as "was".

- **Wing reference area 81.70 sq ft** (gross trapezoid, panel LE/TE extended to BL 0, chord 55.13
  at the centreline), within 0.4% of the manual's 81.99 (om-1980:p3): the wing-area metric PASSES.
  **AR 8.34** (span^2 / reference area). The exposed panels alone stay available as 64.71 sq ft.
- **One configuration for both NP methods**: that reference trapezoid plus the canard; no strakes,
  fuselage or winglets in either (the config has no sourced strake outline a VLM could be given).
  **MAC 40.30 in** (reference trapezoid; was 39.59, a panel+strake blend).
- **Formula fixes, each justified before it was run** (ledger reconciliation section): half-chord
  sweep tan L_LE - (c_r - c_t)/b (Raymer sec. 7; was 2/(1 + lam) too large); wing AC at the
  quarter chord of the reference MAC (same planform as the area); canard downwash applied to the
  wing, the aft surface (Raymer eq. 16.9; was applied to the canard).
- **NP (analytic) FS 106.50**, NOT GRADED (reference unverified). Before/after: 108.50, 108.41 (C1),
  116.19 (C2), 106.50 (C3).
- **NP (VSPAERO VLM) FS 112.36** (OpenVSP 3.48.2, same planform; was 111.13 for the panels only).
- **Two-method NP: FAIL**, delta +5.86 in against the 1.0 in bound, left failing (strict xfail,
  ledger row 53). Each surface alone agrees between the methods (wing AC 127.41 vs 128.28, canard
  AC 21.96 vs 21.77, slopes within 1.5%); the gap is the interference model: the analytic method
  applies the far-field canard downwash (0.306) to the whole wing, the VLM's net effect is about
  0.05. The canard waterline (flagged conflict) was not changed.
- **Static margin at FS 103: 8.69 % MAC** ((106.50 - 103.0) / 40.30), stability check PASS, but it
  rests on an NP the second method does not confirm.
- **CG limits** 99.57 / 103.42 against 97 / 103: forward FAIL (+2.57 in), aft PASS (+0.42 in). Both
  are NP minus the retired fixed MAC fractions, so the aft PASS is not independent evidence.
- **Report**: 12 metrics, 3 PASS (CG aft, max gross, wing area), 2 FAIL (CG fwd, empty weight), 7
  NOT GRADED.

## Follow-up (2026-09-29): partial-span canard downwash (C4) and the canard waterline

- **C4, method fixed in the ledger before it was run** (commit `0c44b10`): the canard as one
  horseshoe vortex (vortex span b' = (pi/4) b_c, McCormick; Anderson sec. 5), Biot-Savart for the
  bound segment and trailing legs (Katz and Plotkin), downwash averaged over the whole wing span
  weighted by chord (strip theory), each strip at its own quarter chord, z = 1.5 in. It replaces
  the far-field constant applied to the whole wing. Red-first unit tests against hand-computed
  horseshoe cases (`tests/test_partial_span_downwash.py`).
- **d eps/d alpha on the wing 0.0899** (was 0.306): downwash inboard of the canard tip vortices
  (BL +-55.6), upwash outboard.
- **NP (analytic) FS 110.68** (was 106.50), NOT GRADED. **NP (VLM) FS 112.36** (not re-run).
- **Two-method NP: still FAIL**, delta +1.68 in against the unchanged 1.0 in bound; row 53's
  strict xfail stays (ledger row 54). One method, one run; no second method was tried against the
  check. Diagnosis: the analytic formula places the wash-induced lift change at the wing AC,
  whereas on the swept wing the lift lost is inboard (forward) and the lift gained outboard (aft);
  placing it at its own strip centroid (diagnostic only, not adopted) gives 113.42, 1.06 in past
  the VLM. Agreement within 1 in would need d eps/d alpha at most 0.044.
- **Static margin at FS 103: 19.06 % MAC** ((110.68 - 103.0) / 40.30), stability check PASS
  (5 to 20 %), but the NP it rests on is still not confirmed by the second method.
- **CG limits** 103.75 / 107.60 against 97 / 103: both FAIL (+6.75, +4.60 in); CG aft strict
  xfail restored with the bound unchanged. Both are NP minus retired MAC fractions.
- **Report**: 12 metrics, 2 PASS (max gross, wing area), 3 FAIL (CG fwd, CG aft, empty weight),
  7 NOT GRADED.
- **Canard waterline**: cobelu C-3's W.L. 19.8 labels the level jig line of the R1145MS hot-wire
  core templates (it runs through the section nose); p171's 18.9 is the GU first-edition side view
  at the canard lower surface. Different canard and different point, not a transposition. The
  model keeps 1.5 in (18.9 - 17.4); status stays `conflict`. NP moves 0.012 in across the book's
  1.5 to 2.4 in range (block1-source-notes, Canard waterline).

## 1. Changed values

Generated by loading `config/aircraft_config.py` at `d308d44` and at HEAD and diffing the
`GeometricParams`, `StrakeConfig` and `StructuralWeightParams` defaults and `CHORD`, plus a diff of
the `aircraft_specs` entries in `data/validation/reference_data.json`. Lengths are inches unless noted.

### 1a. `config/aircraft_config.py`, `GeometricParams` and `CHORD`

| field | was | now | citation or flag |
|---|---|---|---|
| wing_span | 316.8 | 313.2 | book, om-1980:p3 (26.1 ft); was unsourced |
| wing_root_chord | 68.0 | 49.90 | derived (straight taper through the printed chords 42.7 at BL 55.5 and 20.0 at BL 157, extrapolated to BL 23.3), plans-1980:p126; was unsourced |
| wing_tip_chord | 32.0 | 20.0 | book, plans-1980:p126 (BL 157); was unsourced |
| wing_sweep_le | 25.0 deg | 22.98 deg | book, plans-1980:p126; was unsourced |
| wing_dihedral | -4.5 deg | 0.0 deg | book, plans-1980:p134 (jigged flat, no angle printed; medium confidence); was unsourced |
| canard_span | 126.0 | 141.6 | FLAG conflict. GU planform, om-1980:p3 (11.8 ft). Roncz planform unconfirmed (130 elevator tip-to-tip cp-43:p1; core jig blocks 126 apart cobelu:p13). Was "book" (Roncz core) |
| canard_chord (and `CHORD`) | 15.25 | 13.02 | FLAG conflict. 12.8 sq ft * 144 / 141.6 from om-1980:p3. Was unsourced |
| canard_le_wl | 12.0 | 1.5 | FLAG conflict. Model z is relative to the wing plane (book W.L. 17.4); plans-1980:p171 W.L. 18.9 at the canard gives 1.5. No page labels it the LE. Was unsourced |
| canard_vertical_offset_in | 12.0 | 1.5 | FLAG conflict. Same evidence as canard_le_wl. Was unsourced |
| fs_nose | -45.5 | -6.8 | book, plans-1980:p171 (nose tip); was converted-unsourced |
| fs_pilot_seat | 34.5 | 59.0 | book, om-1980:p25 (pilot CG station; not the F22 bulkhead); was converted-unsourced |
| fs_rear_seat | 69.5 | 103.0 | book, om-1980:p25 (passenger CG station; not the F28 bulkhead); was converted-unsourced |
| fs_firewall | 134.5 | 125.0 | book, plans-1980:p101; was converted-unsourced |
| gross_weight_lb (`AircraftConfig`) | 1425 | 1325 | book, om-1980:p4 (max gross); 1425 stays the ledger's takeoff-only band, om-1980:p28 |
| fuselage_length | 214.0 (stored field) | 175.3 (read-only property, `fs_tail - fs_nose`) | FLAG conflict, kept vs 201.4 overall (om-1980:p3); one basis for both VSP builders |
| wing_tip_bl, wing_panel_span (new properties) | none | 156.6 (`wing_span / 2`), 133.3 (tip BL minus wing_root_bl) | derived from wing_span and wing_root_bl; panels now end at the book tip BL |
| wing_area_sqft (property) | 76.02 | 81.70 (was 64.71 at `c866d50`) | derived: gross reference trapezoid, panel LE/TE extended to BL 0 (`af5841d`); the exposed panels are `wing_exposed_area_sqft` 64.71 |
| wing aspect ratio (property) | full span^2 / panel area | 8.34 (was 7.63 at `c866d50`) | derived, span^2 / reference area (one planform) |

Provenance status or source only (value unchanged): canard_sweep_le book plans-1980:p71;
fs_canard_le book plans-1980:p171 (owner by-eye check recorded in the ledger); wing_le_anchor
cp-corrected cp-text:p25 LPC 7 (113.9); datum_offset_in stays 0.0, now book om-1980:p25 (datum F.S. 0.0); canard_incidence, canard_oswald_e still unsourced.
New entry: fuselage_length, FLAG conflict, now a property (see part 3).

### 1b. `StrakeConfig` and `StructuralWeightParams`

| field | was | now | citation or flag |
|---|---|---|---|
| StrakeConfig.fs_leading_edge | 64.5 | 50.0 | book, plans-1980:p147 (LE at the fuselage side; p171 agrees; the LE is swept) |
| StructuralWeightParams.canard_arm_in | -0.5 | 21.955 (computed: fs_canard_le + 0.25 * canard_chord) | derived in code, "canard structural weight at the canard (quarter chord)"; inherits the canard chord FLAG |
| StructuralWeightParams.fuel_arm_in | 82.0 | 104.5 | book, om-1980:p26 (fuel station) |

Unchanged but re-labelled "unsourced, Block 2 replaces": wing_arm_in 94.5, fuselage_arm_in 54.5,
landing_gear_arm_in 84.5, electrical_arm_in 119.5, instruments_arm_in 29.5, interior_arm_in 49.5.
`StrakeConfig.fs_trailing_edge` 99.5 unchanged, labelled converted-unsourced. `fs_tail` 168.5
unchanged, still converted-unsourced.

### 1c. `data/validation/reference_data.json` (`aircraft_specs`)

Every entry now carries `status` (confirmed with a registry `cite`, derived with a `formula`, or
unverified with `was_cited` and `why`). Only confirmed and derived entries count as truth (`core/reference.py`).

| field | was | now | citation or flag |
|---|---|---|---|
| wing_span_in | 316.8 (raf-cp31) | 313.2 | confirmed, om-1980:p3 |
| wing_area_sqft | 94.2 (raf-cp31) | 81.99 | confirmed, om-1980:p3 (excludes canard; manual total 94.8) |
| canard_span_in | 147.0 (raf-cp31) | 141.6 | confirmed, om-1980:p3 (GU canard) |
| canard_area_sqft | 15.6 (raf-cp31) | 12.8 | confirmed, om-1980:p3 (GU canard) |
| aspect_ratio | 7.3 (raf-cp31) | 8.31 | derived, 313.2^2 / (81.99 * 144) |
| max_gross_weight_lb | 1425 (raf-cp29) | 1325 | confirmed, om-1980:p4 (1425 is a takeoff-only band, om-1980:p28) |
| empty_weight_lb | 850, range 800-920 (raf-cp29) | 750 | confirmed, om-1980:p4 (approximate, normal equipped) |
| useful_load_lb | 575 (raf-cp29) | 575 | derived, max gross - empty (1325 - 750); value same, basis changed |
| cg_range_fwd_fs | 99.0 (raf-cp29) | 97.0 | confirmed, om-1980:p28 (chart) |
| cg_range_aft_fs | 104.0 (raf-cp29) | 103.0 | confirmed, om-1980:p28 (chart) |
| cruise_speed_ktas | 160 (raf-cp29) | 161 | confirmed, om-1980:p15 (max true cruise, Lycoming) |
| vne_ktas | 200 (raf-cp29) | 190 | confirmed, om-1980:p23 (red line) |
| neutral_point_fs | 108.0 (raf-cp29 p.18) | 108.0, status unverified | FLAG unverified: not found in CP-29, CP-31, the manual, or CP 1-82 text; history only |
| stall_speed_ktas | 56 (raf-cp29 p.20) | 56, unverified | FLAG unverified: not found in the sources |
| range_nm | 800 (raf-cp29 p.20) | 800, unverified | FLAG unverified: not found in the sources |
| static_margin_pct | 12.0 (derived from the NP) | 12.0, unverified | FLAG unverified: derives from the unverified NP |
| metadata datum_note, description | RAF CP-29/CP-31 datum note | published datum F.S. 0.0, om-1980:p25 | text |

Removed from `reference_data.json`:

- `community_builds` (5 builder weigh-in records): unsourced.
- Sources `raf-cp29`, `raf-cp31` (page and table cites in them not found in the texts), `csa-newsletter`, `builder-weigh-in`.
- Sources `roncz-wt` and `eppler-report`: deleted in the airfoil_data follow-up (neither was found in any corpus text).

`airfoil_data` (follow-up audit, none found in the corpus or public web; UIUC lists coordinates only):

| airfoil | fields | was | now |
|---|---|---|---|
| roncz_r1145ms | cl_max 1.35, cm_zero -0.05, alpha_zero_lift_deg -3.0, cd_min 0.006 | cited to `roncz-wt` | unverified, with `was_cited` and `why`; not truth (`truth_airfoil`) |
| eppler_1230 | cl_max 1.45, cm_zero -0.02, alpha_zero_lift_deg -2.0, cd_min 0.0055 | cited to `eppler-report` | unverified, with `was_cited` and `why`; not truth (`truth_airfoil`) |

### 1d. New files

- `data/sources/registry.yaml`: registry of citable documents; every citation is `<id>:p<page>` and an unknown id is rejected (`core/sources.py`).
- `data/mass_ledger.yaml`: empty aircraft as one row plus cited loads, the manual's CG envelope (97.0 to 103.0, 1325 lb, 1425 lb takeoff-only), the two sample loadings and four recorded book errata (`core/ledger.py`).
- Supporting: `core/reference.py` (`truth_specs`), `scripts/fetch_sources.py` (private corpus fetcher), `docs/block1-source-notes.md`.

## 2. Check results

From `data/validation/accuracy_report.json` (`metadata.checks`, `metrics`, `summary`).

| check | result |
|---|---|
| Stability at the aft limit | PASS. NP 106.50 in vs aft limit 103.0; MAC 40.300 in; static margin 8.6897 % MAC at the ledger aft limit FS 103 (was NP 105.94, MAC 39.594, 7.4208 % at `c866d50`) |
| Two-method NP | FAIL, left failing (strict xfail, ledger row 53). Analytic 106.50, VSPAERO VLM 112.36 (OpenVSP 3.48.2, `data/validation/vspaero_np.json`, same reference-trapezoid wing + canard), delta +5.86 in, bound 1.0 in. Diagnosis in the ledger's reconciliation section (far-field canard downwash applied to the whole wing). Was `not run` at `c866d50` (no OpenVSP), then FAIL at `af5841d` (108.50 vs 111.13, models of different wings) |
| NP value | 106.5020 reported, NOT GRADED ("reference unverified"): the 108 reference was not found in CP-29, CP-31, the manual, or CP 1-82 text (was 105.9382) |
| CG limits, computed vs manual | fwd 99.57 vs 97.0 (+2.57 in, FAIL at 1.0 in tolerance); aft 103.42 vs 103.0 (+0.42 in, PASS) (was 99.12 / 102.91). The computed limits are NP minus fixed MAC fractions (the retired Phase 5 margins, `core.analysis`), not independent of the NP |
| Summary counts | 12 metrics: 3 pass, 0 marginal, 2 fail, 0 ungraded, 7 not graded (was 2 / 3) |
| Pass | CG aft 103.42 vs 103.0; max gross weight 1325 vs 1325; wing area 81.70 vs 81.99 sq ft (-0.29) |
| Fail | CG fwd 99.57 vs 97.0 (+2.57 in); empty weight 640 vs 750 (-110 lb) |
| Not graded | neutral point 106.50, static margin 8.6897 % MAC (same number as the stability check), stall speed 55.30 KTAS, and the four airfoil metrics (canard CLmax 1.35, wing CLmax 1.45, canard alpha0L -3.0, wing alpha0L -2.0; airfoil_data unverified) |
| Mass-ledger sample gate | Both manual sample loadings reproduce from the ledger: light pilot 1113 lb at CG 103.96 (outside the envelope, as the manual shows) and heavy pilot 1323 lb at CG 101.06 (inside). Four book errata recorded: light pilot pilot moment (book 7865, computed 7965); heavy pilot total moment (book 122706, computed 133706; the printed CG matches the computed value); light pilot total moment (book 115708, computed 115706); light pilot CG divisor in the prose (11133 for 1113) |

## 3. Still flagged

Each item names the evidence that would clear it.

**GEOMETRY_PROVENANCE, status not book / cp-corrected / derived**

| entry | status | what clears it |
|---|---|---|
| canard_span 141.6, canard_chord 13.02 | conflict | The Roncz canard planform sheets (span and chord of the airplane as built with the Roncz canard). Today they are the GU numbers from the manual |
| canard_le_wl 1.5, canard_vertical_offset_in 1.5 | conflict | A page that labels the canard LE (or chord line) waterline for the model's canard. 18.9 (p171 side view), 19.4 (GU template level line) and 19.8 (Roncz template level line) are different references and none says LE |
| canard_incidence -1.5 | unsourced | A printed incidence angle. CP 47 gives the method (level to the top longeron) but no angle |
| canard_oswald_e | unsourced | Aero estimate, not a plans value; clears by a measurement or by being relabelled a model assumption |
| fuselage_length 175.3 | conflict | One basis now: the property `fs_tail - fs_nose` = 175.3, used by both VSP builders. It still conflicts with the manual's 201.4 overall (om-1980:p3). A printed aft-end station for the fuselage would settle it |
| fs_tail 168.5 | converted-unsourced | A printed aft-end station (none is printed in Section I) |
| wing_root_bl 23.3 | unsourced | A page giving the root butt line for the model's root chord. Plans-1980:p126 has the TE meeting the cowl at BL 23, which is not a root chord station. It sets the panel span 133.3 and the exposed area; the reference area extends the taper to BL 0 and does not depend on it |
| StrakeConfig.fs_trailing_edge 99.5 | converted-unsourced | A printed strake TE station. 99.5 coincides with the book LE at BL 45 |
| StructuralWeightParams wing / fuselage / landing gear / electrical / instruments / interior arms | unsourced | Block 2 replaces them with cited ledger rows |

**reference_data.json, unverified**

| entry | what clears it |
|---|---|
| neutral_point_fs 108.0 | A page in CP-29, CP-31, the manual, or a later Canard Pusher that prints the value |
| static_margin_pct 12.0 | Follows the NP; also needs a stated MAC. The report's computed margin (8.6897 % MAC on the 40.30 in reference MAC; was 7.4208) is a separate NOT GRADED metric |
| stall_speed_ktas 56 | A page that prints it, or flight-test data with a stated weight and configuration |
| airfoil_data, all eight values (cl_max, cm_zero, alpha_zero_lift_deg, cd_min for roncz_r1145ms and eppler_1230) | A page or report that prints each value, registered with a page cite; UIUC lists coordinates only |
| range_nm 800 | A page that prints it with fuel and reserve assumptions |

**Other open items**

- **Manual edition.** The transcription includes LPC 116 (CP 37, 1983), so it is later than the May 1980 first edition; the original first-edition date is unconfirmed. Clears with the dated original manual or a page that dates the revision.
- **Wing area gap: closed.** Was 64.71 sq ft (exposed panels) against the manual's 81.99. The reference area is now the gross trapezoid to the centreline, 81.70 (-0.29, 0.35%; ledger row 43), which shows the manual uses the standard convention. The strakes are outside that planform and outside both NP models.
- **Strict xfails from physics bounds.** D-box weight 4.72 lb against the 5 lb floor (ledger row 37), Anderson lift slope 4.780 /rad against the 4.6 ceiling (ledger rows 36, 47, 49; was 4.682) and the two-method NP, delta +5.86 in against 1.0 (ledger row 53). All are bounds left unchanged.
- **Stall speed computation.** The computed 55.30 KTAS uses a CLmax that is unverified (airfoil_data), so it stays NOT GRADED even apart from the unverified 56 reference.
- **Empty weight.** Model 640 lb against the manual's approximate 750. The model's structural sum is a partial model. Clears with the Block 2 decomposition of the empty weight.
- **CG limits.** Computed 99.57 / 103.42 against 97 / 103 (ledger rows 12, 13, 16, 18, 45, 52; was 99.12 / 102.91). Forward is +2.57 in off (FAIL); aft passes. They follow the NP by construction. Clears with an independent CG-limit calculation, or a source for the NP.
- **Two-method NP fails.** Analytic 106.50 vs VLM 112.36, +5.86 in against the 1.0 in bound (ledger row 53). Both methods now model the same wing; the gap is the analytic interference model (full-span far-field canard downwash). Clears with a partial-span downwash model chosen from a textbook source before it is run, and the canard waterline conflict resolved.
- **Wing structural arms and canard arm.** The canard arm uses the canard chord FLAG; wing arms wait for Block 2. Empty weight stays FAIL until then. (M2.8 correction: the CG limits are NP-derived and graded against the loaded envelope FS 97 to 103; they do not wait on the ledger, and the empty CG is 111.7 in the OM sample, never graded against that band; ledger row 63.)

## 4. Spec section 4, "Done when"

Verified by reading the file or test named and by running the Block 1 test files
(`tests/test_sources_registry.py`, `test_mass_ledger.py`, `test_stability_checks.py`,
`test_reference_truth.py`, `test_geometry_provenance.py`: 49 passed).

1. **Every reference_data value is confirmed, derived or unverified, and no check uses an unverified value as truth.**
   `tests/test_reference_truth.py::test_every_spec_has_an_audit_status`, `::test_truth_excludes_unverified`,
   `::test_no_consumer_reads_aircraft_specs_directly`; in the report the NP, static margin and stall speed
   carry grade NOT GRADED. `airfoil_data` is covered too:
   `::test_every_airfoil_value_has_an_audit_status`, `::test_truth_airfoil_excludes_unverified`,
   `::test_airfoil_sources_removed`, `::test_no_consumer_reads_airfoil_data_directly`; its four report metrics
   carry grade NOT GRADED.
2. **Every GEOMETRY_PROVENANCE entry cites a registry id and page, or is flagged.**
   `tests/test_geometry_provenance.py::test_sourced_entries_cite_the_registry` (book, cp-corrected and derived
   entries must pass `check_citation`) and `::test_provenance_entries_are_well_formed`; the entries that are not
   cited carry conflict, unsourced or converted-unsourced (part 3).
3. **The ledger reproduces both sample loadings.**
   `tests/test_mass_ledger.py::test_manual_sample_loadings_reproduce[light_pilot]` and `[heavy_pilot]`, to within
   0.5 lb and 0.01 in of the book totals (1113 lb at 103.96; 1323 lb at 101.06).
4. **The stability-at-aft-limit check has a result.**
   `data/validation/accuracy_report.json` `metadata.checks.stability`: pass true, NP 106.50 vs aft limit 103.0,
   margin 8.6897 % MAC (was 105.94, 7.4208); `tests/test_stability_checks.py::test_report_carries_both_checks` and
   `::test_static_margin_metric_is_the_check_number` (metric and check agree).
5. **The two-method NP check runs, or reports "not run".**
   It runs: FAIL, analytic 106.50 vs VLM 112.36, delta +5.86 in (was "not run" at `c866d50`: OpenVSP module not installed);
   `tests/test_stability_checks.py::test_two_method_not_run_is_not_a_pass` and `::test_report_carries_both_checks`
   (a not-run check is not counted in the pass total).
6. **Every gate has been shown to fail on a broken input.**
   `tests/test_sources_registry.py::test_unknown_id_rejected`,
   `tests/test_mass_ledger.py::test_sample_gate_fails_on_a_wrong_arm`,
   `tests/test_stability_checks.py::test_unstable_at_aft_limit_fails`,
   `tests/test_stability_checks.py::test_two_method_disagreement_fails`. All four pass.
7. **A report lists each value the model changed, from what to what, and the page that justifies it.**
   This file, part 1.
