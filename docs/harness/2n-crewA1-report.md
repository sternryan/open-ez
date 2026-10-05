# 2.n crew A1 report: closure table (Task 1 steps 1 to 4)

No sum, total or CG of the rows was written or run. Nothing was compared to 730 or 111.7.

## Row table

| name | weight | band | arm FS | arm band | status (arm) | cite |
|---|---|---|---|---|---|---|
| fuselage | 183.0 | [173.85, 192.15] | 68.1 | [58.1, 78.1] | builder (unsourced) | cp-text:p26 |
| wings | 132.4 | [128.0, 132.6] | 127.5 | [117.4, 141.6] | derived (derived) | cp-text:p26; cp-text:p27 |
| canard | 18.5 | [17.58, 19.43] | 21.96 | [18.7, 31.72] | builder (derived) | cp-text:p27; plans-1980:p171 |
| elevators | 6.5 | [6.18, 6.83] | 29.77 | [26.5, 31.72] | builder (derived) | cp-text:p27 |
| canopy | 17.0 | [16.0, 17.0] | 79.3 | [69.3, 89.3] | builder (derived) | cp-text:p27; cp-text:p26 |
| strakes_with_tanks | 30.0 | [15.0, 45.0] | 104.5 | [94.5, 114.5] | unsourced (derived) | none |
| engine | 243.0 | [243.0, 249.1] | 125.0 | [125.0, 160.0] | conflict (unsourced) | plans-1980:p156 |
| engine_mount | 5.19 | [4.93, 5.45] | 130.0 | [125.0, 140.0] | builder (derived) | cp-text:p26 |
| cowl | 15.0 | [12.0, 18.0] | 140.0 | [130.0, 150.0] | builder (unsourced) | cp-text:p27 |
| prop_spinner | 20.0 | [10.0, 30.0] | 175.0 | [165.0, 185.0] | unsourced (unsourced) | none |
| battery_25ah | 19.0 | [0.0, 19.0] | 11.0 | [0.0, 22.0] | derived (derived) | cp-text:p27 |
| starter_ring_alternator | 49.5 | [0.0, 49.5] | 150.0 | [150.0, 170.0] | derived (derived) | cp-text:p27 |
| instruments | 15.0 | [10.0, 20.0] | 40.0 | [35.0, 45.0] | allowance (derived) | cp-text:p27; om-1980:p35 |
| interior | 20.0 | [10.0, 30.0] | 81.0 | [71.0, 91.0] | allowance (derived) | om-1980:p26 |
| finish_unweighed | 10.0 | [6.0, 18.0] | 85.0 | [75.0, 95.0] | allowance (unsourced) | cp-text:p27; cp-text:p12 |
| wheels_brakes | 20.2 | [0.0, 30.3] | 110.5 | [100.5, 120.5] | unsourced (derived) | none |

`method_check_rows`: 14 rows, aliases of the rows above minus battery_25ah and starter_ring_alternator, with cowl_graphite (12, [11.4, 12.6]) replacing cowl.

## Unsourced or placeholder

- strakes_with_tanks: weight unsourced (the 183 lb fuselage excludes strakes; no page weighs strakes or tanks). Placeholder 30 lb, +-50 percent. Arm is the printed fuel station 104.5 used as a tank centre (derived).
- prop_spinner: no page gives weight or station. Placeholder 20 lb, FS 175, +-50 percent and +-10 in.
- wheels_brakes: weight unsourced (remainder of the retired 45 lb lump). Band reaches 0 because CP26's 183 lb names brake cylinders, nose and main gear but not wheels or tyres, so overlap cannot be excluded.
- engine: status conflict (243 vs 249.1). ARM IS A PLACEHOLDER, firewall FS 125, band [125, 160], arm_status unsourced. The captain replaces it.
- Arm-unsourced (centre is a stated stand-in, band +-10): fuselage (68.1, model lower-bound centroid), cowl 140, finish_unweighed 85.
- Config datum: datum_offset_in is 0 since 2026-09-29 and to_published_datum is the identity, so no 45.5 shift remained to convert; the 45.5 comments refer to retired internal values.

## Flags for the captain

- tests/test_closure_table.py deviates from the plan in one line: core.sources.check_citation returns None and raises on failure, so `all(check_citation(c) ...)` is always False. The test now calls it in a loop.
- Fail-first (Step 2) was not run as a separate step: closure.py and the yaml block landed before the first run. The freeze test did fail once on the missing hash, then passed after row 65.
- Row 65 is real (not DRAFT-hash PENDING): hash pasted. The 'never summed' notes in prototype_weights were NOT edited; row 65 records the relabel, the note edit is left for Task 3.
- finish_unweighed band [6, 18] and the allowances (instruments, interior) are my stated ranges, not page values.
- Weight half-bands: strakes_with_tanks (+-15) and wheels_brakes, starter and battery bands are wide and may push the exit test over the 20 lb cap by design.
- Rows not added: exhaust, engine accessories, nose-gear ballast, fuel system plumbing.

## Tests

- tests/test_closure_table.py + tests/test_mass_ledger.py + tests/test_m28_weight_flags.py: 34 passed, 1 xfailed.
- Full: `pytest --ignore=tests/guide -m "not local_render"`: 1018 passed, 2 skipped, 9 xfailed.
- Frozen block sha256: 491dcf4533ce42003ced1446c21de269460587655ed9d5a6dac0ec66ccd8145a

## Files changed (nothing staged or committed)

- data/mass_ledger.yaml (modified: closure block appended)
- docs/geometry-correction-ledger.md (modified: row 65)
- core/closure.py (new)
- scripts/closure_hash.py (new)
- tests/test_closure_table.py (new)
- docs/harness/2n-crewA1-report.md (new)
