# Block 3 captain handoff (2026-10-07, end of the pre-10-09 wave, part 1)

Commits 78f8319 to the commit that adds this file.

Read these first: the spec (`docs/superpowers/specs/2026-10-07-block3-equivalence-engine-design.md`, rev 2),
the plan (`docs/superpowers/plans/2026-10-07-block3-equivalence-engine.md`), the review record
(`docs/harness/block3-spec-review.md`), and the source notes (`docs/harness/block3-source-notes.md`).

## Done (commits 78f8319..14b3a18)

- **Spec, plan and review:** rev 2, with all 18 review findings applied.
- **S1, Report 45:** the primary text was obtained from the NTIS copy; DTIC was down.
  - Registered as `faa-report-45` and transcribed to `data/criteria/report45.yaml`.
  - The captain re-read the wing criterion (p4) and Fig 2 (p10). The crew's Fig 2 intercept of 4.73
    was superseded by the captain's pixel calibration of 4.80 ± 0.04.
  - Figs 3 and 4 and the tab constant on p8 are NOT yet re-read. They gate nothing today, because the
    elevator and rudder criteria need fuselage frequencies that we do not have.
- **S2, sources registered:** NCAMP 8552 AS4, NCAMP 7781/MTM45-1, AGATE wet-layup 114 and 115, Kaw's
  course decks and NASA TN D-3125. The captain re-read NCAMP p30–45 (text layer) and Kaw p4 and p16
  (slide images), and recomputed the Kaw vectors independently.
- **S3:** recorded in the source notes.
  - No designer V_D was found.
  - The 190 kt red line is an indicated speed (om-1980:p43).
  - The elevator and aileron balance procedures are sourced; the weight masses are not printed.
  - The CP flutter history is recorded.
  - NTSB was not queried successfully.
- **T1 and T2:** `data/materials.yaml`, `core/materials.py` (`get_material` raises on an unknown id),
  and the kernel purity guard.
- **T3:** M3.1 vectors and tests in `tests/kernels/`. They skip, via `importorskip`, until the T4
  bodies exist. The bounds are frozen in ledger row 73.
- **False claim corrected:** the "textbook E-glass case" claim in the roadmap and TODOS, recorded as
  ledger row 72 with a learnings entry.
- **T11 part 1:** `data/laminates/canard_book.yaml`, extracted by a crew. **The captain re-read is
  PENDING** (`reread: pending` in the file).

## Done by captain #2 (2026-10-07, pre-10-09 wave part 2)

- **T11 re-read:** `canard_book.yaml` is `reread: done` with a `reread_log`. Shear-web UND plies are
  +-45 (Fig 30-16, p11); BID web extents confirmed; pads centred on BL 8 (Fig 30-13), extent open;
  cap ply-1 cite p15; top-skin BID cut at 35 to 45 (Fig 30-34, noted); balance strips wrap
  chordwise (Fig 30-55).
- **T11 part 2:** `docs/harness/block3-sizing-rule.md`; `data/laminates/canard_carbon.yaml` (structure
  only, every count null and flagged); inputs freeze row 74 with seven hashes
  (`core/equivalence_inputs.py`, `scripts/equivalence_inputs_hash.py`, a pinning test).
- **Stere registered** (`incas-stere-2010`); **T6** vectors and tests (`thinwall_textbook.yaml`,
  `test_thinwall.py`, skipped until T7); M3.2 bounds frozen in row 75.
- **Latent defect fixed:** 52 vector numbers (38.6e9 style) loaded as strings; `_vectors.load` now
  parses them, with a guard test.
- **T12 tests:** `tests/test_equivalence_canard.py` (skipped until the crew writes
  `scripts/equivalence_report.py`; the contract is in the module docstring).
- **vne_ktas label:** "knots indicated airspeed", row 76.
- **Warp-direction search:** nothing citable. AGATE-106 makes the fill-only matrices deliberate.
  See the source notes, "S2 follow-up".

## Done by captain #3 (2026-10-08, paper only, no outreach)

- **`requires_original_test` notation (row 77).**
  - It is a second property flag in `core/materials.py`. It needs:
    - a null value;
    - `search`: the evidence;
    - `closing_test`: an ASTM method plus a coupon id matching `B5-<MAT>-<T0|T90|C0|C90|S45>`;
    - `test_plan`.
  - It is applied only to `carbon3k_mgs418_wet` E1, nu12 and F1t (closed by B5-CPW-T0, D3039) and F1c
    (closed by B5-CPW-C0, D6641). A test pins that exact set, and also checks that each coupon and
    method appears in the plan.
  - The book lamina and the 7781 proxy stay `unsourced`.
- **Gate contract** (`tests/test_equivalence_canard.py` docstring, for the T12 crew):
  - It adds the state `open` and the reason `requires_original_test`, carried by a `test_required`
    map, plus the outputs `test_required_inputs` and `closing_coupons`.
  - `open` applies only when that is the sole reason. With any other reason the gate reads `blocked`.
  - A gate can never read `pass` while either flag is present.
  - The new gate tests passed against a scratch implementation outside the tree. The real script is
    still pending.
- **Freeze test** now reads row 77. Only carbon_lamina changed hash, and only labels changed.
- **Coupon test plan:** `docs/superpowers/specs/2026-10-08-block5-coupon-test-plan.md`. The
  oven/kiln and lab section is a placeholder for the separate agent.
- **Draft purchase order:** `docs/harness/block5-coupon-purchase-order.md`.

## Next, added by captain #3

1. **Before any panel exists:** buy the standards (Ryan), so the NOT READ values in plan §5 can be
   filled. Fill the lab and oven placeholder in plan §10 when that search reports.
2. **Before the first record panel:** write `data/validation/block5_coupon_predictions.yaml` and freeze
   its hash in a row (plan §8).
3. **The T12 crew:** implement `gate()` to the extended contract.

## Next, in order

1. **T12 script (Sonnet crew):** implement `scripts/equivalence_report.py` to the test contract and
   commit `data/validation/equivalence_canard.json`. Every gate will read blocked today. The
   `station_capacities` test needs T4 and T7.
2. **T5** (NCAMP and glass comparisons) after T4.
3. **Warp data:** the untried leads in the source notes. A supplier request is outward contact, so it
   is the owner's call.
4. **S3:** retry the NTSB lookups for N25063 and N707LT.
5. **Report 45:** re-read Figs 3 and 4 and the p8 tab constant before T10.

## Held for after the 10-09 remote-runner gate

- The local-model kernel bodies: T4 (`lamina.py`, `laminate.py`, `tsai_wu.py`), T7 (thin-wall) and
  T10 (Report 45 kernel).
- The remote test fan-out.

When T4 lands, the M3.1 tests run for the first time against the frozen bounds. A miss is a strict xfail
with a new row; the bound is never widened.

## Traps found this wave

- **Concurrent browser downloads mix files.** The shared browser automation saved one crew's download
  under another crew's name: a Report 45 PDF landed in the NCAMP folder. Give each crew its own headless
  downloader.
- **The Report 45 wing criterion uses cumulative twist.** θ is twist relative to the centreline under
  unit torque applied outboard of the aileron end, not local twist per unit length (p4). The T10 kernel
  must integrate dy/GJ from the root.
- **The wing criterion's speed unit is an inference.** p4 gives Vd as IAS with no unit; mph comes from
  p6 and the Fig 2 axis.
- **NCAMP 7781 mixes bases.** Its summary moduli are normalised but its CVs are measured (flagged in
  the vector file).
- **Ruff.** Run `.venv/bin/ruff check --fix` and `ruff format` on new tests before committing; the crews'
  files needed fixes.

## Done by captain #4 (2026-10-08, kernels, T12 and the Report 45 kernel)

- **T4, M3.1 kernels:** `core/kernels/lamina.py`, `laminate.py` (adds `ply_stresses`, top and bottom
  face per ply) and `tsai_wu.py`, written by the local-model lane, each checked by a fresh grader.
  - The textbook vectors pass. The Tsai-Wu printed match now starts from the printed global stress:
    the printed local stress is rounded and missed by 0.0002 (row 78; vector and bound unchanged).
- **T5:** NCAMP moduli against the frozen row-73 bound: five of six AS4 cases pass; [10/80/10]
  tension misses (CLT 4.800 against 4.570 +- 0.182 Msi) and is a strict xfail citing row 78.
  - 7781 glass sits inside the bound, but it compares normalised means with measured CVs, so it is
    not counted: **M3.1 stays open on glass** and the gates keep `glass_unvalidated`.
  - Measured NCAMP strengths beside FPF (not a gate) are **not done**: never transcribed, PDFs not held.
- **T7, M3.2 kernels:** `core/kernels/thinwall.py` (local lane, after one re-brief) and
  `thinwall_sc.py` (captain, after the local lane missed twice). The grader found the shear centre
  ignored Ixz; fixed, with asymmetric and rigid-shift tests. The Stere case passes the row-75 bounds.
- **T12:** `scripts/equivalence_report.py` (Sonnet crew) and `data/validation/equivalence_canard.json`.
  Every gate is blocked today. The grader found geometry flags missing from the strength gate, NaN
  capacities passing, and fabric angle pairs expanded as UND; all fixed.
- **T10, kernel only:** `core/kernels/flutter_r45.py` (local lane), tests and vectors frozen in
  row 79 against the registered IA-100 paper (`caia-2023-ia100`). Grader hardening applied.

Pushed: 2428e7f (kernels and T12) and the commit that adds this section (T10 kernel).

## Next, added by captain #4

1. **T10 book run is blocked:** the twist per unit torque needs the wing laminate (T13, not typed)
   and the BID and UND shear moduli (unsourced). `data/validation/flutter_inputs_book.yaml`,
   `scripts/flutter_screen.py` and `tests/test_flutter_screen.py` are not written. The elevator
   criteria also need fuselage frequencies. Figs 3 and 4 and the p8 tab constant are still not re-read.
2. **Glass:** transcribe the 7781 measured (not normalised) laminate means (ncamp-7781-mtm45 p51, p53),
   captain re-read, then decide whether M3.1 closes on glass (a new row).
3. **T5 strengths:** transcribe the AS4 measured UNT and UNC strengths (p40 to p45) and report them
   beside FPF and a fibre-failure estimate, labelled not a gate.
4. **T8:** point `fea_adapter` at the kernels (Sonnet crew; a row for every moved number).

## Traps found by captain #4

- **Conduct commit messages carry a lane prefix and a job trailer.** Rewrite them before pushing
  (the repo is public); `git filter-branch --msg-filter` over the branch range works.
- **Kernel test modules skip rather than fail before a body exists** (`importorskip`), so a conduct
  verify must import the module first, or a missing body reads green.
- **The purity guard rejects a data path even in a docstring.** Cite pages, not repo paths, in kernels.

## Rotation note, captain #4 (2026-10-08)

Captain #4 rotated on context before starting the lead's second list. Still open, in order:

1. **T5 strengths:** fetch the public NCAMP reports (AS4/8552 CAM-RP-2010-002 Rev A; 7781/MTM45-1)
   into the private source cache, transcribe the measured UNT and UNC strengths (p40 to p45) and
   report them beside first-ply failure and a fibre-failure estimate, labelled not a gate.
2. **7781 glass:** transcribe the measured, not normalised, laminate means (p51, p53), re-read them,
   and close M3.1 on glass or record the miss, in a new row.
3. **T13:** a crew types `data/laminates/wing_book.yaml` like `canard_book.yaml`; the captain re-reads
   it against the page images. Then `scripts/flutter_screen.py` runs Report 45 on the sourced inputs
   and lists exactly which inputs are missing if V_D,max cannot be computed.
4. **Report 45:** re-read Figs 3 and 4 and the p8 tab constant (printed 63, handwritten 48).
5. **Test-input changes need a fresh grader's confirmation in their ledger row.** The Tsai-Wu
   input-path change in row 78 passed the T4 grader's full run, but the grader was not asked about
   that change specifically: get an explicit confirmation and add it to row 78's notes.
6. **Close the local-lane ledger jobs** for this wave (the lead has their ids) with the grader verdicts.

## Done by captain #5 (2026-10-08, the free items)

- **7781 glass (row 80):** the laminate means now use the as-measured columns (UNT 2.92, UNC 3.17 Msi),
  which match the measured CVs and lamina. Both cases are inside the frozen bound, so **M3.1 closes on
  glass moduli** (one woven 7781 prepreg laminate only, not strength) and the strength gate drops
  `glass_unvalidated`. A fresh grader confirmed this test-input change specifically.
- **T5 strengths (row 81):** `scripts/ncamp_strength_report.py` puts the AS4 measured strengths
  (p40 to p45) beside first-ply failure and a fibre-failure estimate. It is not a gate.
- **T13 schedule and the T10 book run (row 82):**
  - `wing_book.yaml` was typed by a crew and re-read by the captain. Cap and web lengths run along
    the swept spar, and the BL 106.25 leading edge is a conflict pair.
  - `flutter_inputs_book.yaml` is frozen by hash.
  - `scripts/flutter_screen.py` reads `blocked: inputs_unsourced` with 21 missing inputs, and
    V_D,max is not computed.
- **Report 45 re-read:** Fig 3 is confirmed. One Fig 4 point is corrected, (0.145, 1.359) to 1.22.
  The tab constant is printed 63, struck through, with 48 handwritten. Both are carried as a
  conflict, and no code uses them; the book wing has no tabs.
- **Row 78:** a fresh grader explicitly confirmed the Tsai-Wu input-path change (note added to
  the row).
- **Ledger jobs:** T4 f0217499, T7 313bd0d9 and T10 c0d6b11e are closed as merged, with their grader
  verdicts. This wave's job 948a7fe8 closes after the push.

## Next, added by captain #5

1. **The book V_D,max needs, in order:**
   - BID and UND wet-layup lamina properties (E1, E2, G12, nu12, t_ply). There is no free source
     yet; the 7781 MGS 418 proxy is not the book cloth;
   - the skin UND angle;
   - the wing airfoil contour, from a registered source;
   - the centre-section spar (ch14, not typed);
   - the root-attach flexibility.

   When any of these clears, a crew (not the captain) re-assembles the inputs, and a new row
   freezes them before the run.
2. **T13 remainder:** `wing_carbon.yaml`, `equivalence_wing.json` and `test_equivalence_wing.py`.
   They follow the canard pattern and are blocked on the same lamina flags.
3. **The plan's elevator balance-weight control test** needs fuselage frequencies and elevator mass
   properties, none of which are held.
4. **T8** (`fea_adapter` onto the kernels) is still open.
