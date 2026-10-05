# Crew A2 report: closure module (2026-10-04)

## Measured numbers
- Nominal sum: 754.79 lb at FS 106.26.
- Weight band: 645.54 to 880.26 lb (half-band 117.36 lb, cap 20).
- CG band at exactly 730 lb: 96.80 to 121.82 (half-width 12.51 in, cap 1.464). Unconditional CG band 96.71 to 122.01.
- Verdict (730 / 111.7 and 727.9 / 112.02, identical): `weight half-band 117.36 lb over the 20.0 lb cap`.
- Method check (N26MS step 1, reference 693.4): nominal 732.79 lb (+39.4), CG 108.60, band 644.94 to 806.36. The test passes on band containment only (weak).
- Loaded samples from the closure nominal empty: light 100.52 (needs > 103, FAILS), heavy 98.21 (inside 97 to 103).
- CG_CAP_IN = 1.464, NOT 1.462 as briefed: |103 - 103.96| x 1113 / 730 = 1.4637. Test asserts 1.464.
- New freeze hash: 1d19a2f912a1ba6970e0ee2eaa74c294fe908a98c24ff05260b41ceb0f88c6d8 (row 65 updated).

## Rows
No row value changed. The weight bands of the three unsourced rows (strakes 15-45, prop 10-30, wheels 0-30.3) and starter 0-49.5 dominate the weight band; I think those are too wide for a closure to mean anything, but left them.

## Tests
tests/test_ledger_closure.py: 11 pass, 2 strict xfail (test_empty_closes_on_the_om_sample: weight cap; test_om_samples_from_the_ledger_empty: light 100.52 / heavy 98.21). tests/test_closure_table.py: 6 pass with the new hash.

## Files changed
core/closure.py, tests/test_ledger_closure.py, docs/geometry-correction-ledger.md (row 65), docs/harness/2n-crewA2-report.md

## Full suite
`pytest -m "not e2e and not local_render" --ignore=tests/guide`: `1029 passed, 2 skipped, 11 xfailed, 8 warnings in 170.05s`. tests/guide (browser/site-build tests, 330 of 1358) was excluded: a first full run hung on Playwright and was killed, and the guide tree does not import core.closure.
