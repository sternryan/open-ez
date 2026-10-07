# Block 3 equivalence engine: implementation plan

> **For agentic workers:** use superpowers:subagent-driven-development or superpowers:executing-plans,
> task by task. Steps use checkbox (`- [ ]`) syntax.

**Goal.** Use validated kernels to compute the strength and stiffness of the book glass laminate and of
a proposed carbon laminate for a given part, and report the deltas. Screen flutter with FAA Report 45.
The canard comes first, then the wing.

**Spec:** `docs/superpowers/specs/2026-10-07-block3-equivalence-engine-design.md`, rev 2 (§ refers to
it). **Review:** `docs/harness/block3-spec-review.md`.

## Global constraints

- **Public repo.**
  - No hostnames, IPs, home paths, private locations, plans pages, scans or OCR text.
  - Paraphrase sources in ten words or fewer.
  - Describe remote compute generically: "remote CPU test runner", "local-model implementation lane".
- **Sourcing.**
  - Every value is sourced (`<id>:p<page>` plus a table, figure or example) or flagged `unsourced`.
  - Never upgrade a flag without the page in hand.
  - Never measure an undimensioned image. A dimensioned chart may be read: record each point with its
    figure, and the captain re-reads it.
- **Bounds and gates.**
  - Never widen a bound.
  - Register every validation bound in a ledger freeze row BEFORE its comparison runs.
  - A gate counts only after it has been shown to fail on a broken input. Broken-input tests PASS by
    asserting that the comparison fails.
  - A failing bound stays a strict xfail that cites its ledger row.
- **Gate states** (§7). A gate reads `pass`, `fail` (strict xfail plus a row) or `blocked: <reason>`.
  A gate with any flagged input can never read `pass`.
- **Ledger rows.** Rows are numbered when they are written; the next free row today is 72. This plan
  names rows by purpose, never by number, so a moved-test row cannot collide with a freeze row.
- **Frozen.**
  - The `closure:` block in `data/mass_ledger.yaml` (row 65) and the O-235 layout (row 70). Block 3
    reads them and never edits them.
  - `config.flight_condition.v_ne_ktas` is not edited (§3).
- **Data rules.**
  - NCAMP 8552 AS4 is kernel-validation data only, never a design input: it is prepreg, and the build
    is wet layup.
  - Every speed carries its unit and its basis (IAS, CAS, EAS or TAS) in its field name or record.
- **Kernels.**
  - Kernels live in `core/kernels/` as pure functions. Airframe data comes in as arguments.
  - No generic airframe framework.
- **Arithmetic.** Deterministic code only. No language model computes a number that enters a test or a
  report.
- **Commits.**
  - Crews stage named files and do not commit. The captain sends the split; the lead commits and pushes
    through the push gate.
  - No session-link trailers.
  - The full suite must be green (expected strict xfails aside) before each commit.
- **UI is out of scope.**

## Lanes

| lane | used for | why |
|---|---|---|
| captain (Opus) | test vectors from published sources, freeze rows, the sizing rule, re-reading every value read off a page or chart, review | judgment: sourcing errors are the expensive failure |
| Sonnet crew | source search and registration, YAML and config data, reading values off held scans (captain re-reads the image), multi-file code, docs | config-heavy and research work; the local lane failed 19 of 27 op-YAML tasks |
| local-model implementation lane, with a Sonnet grader on every output | single-file kernel bodies: at most about 150 lines, exact signatures, RED tests supplied, briefs under 25 lines | shape-constrained code; the grader stays because local bodies have passed their own tests with real defects |
| script (remote CPU test runner) | full-suite fan-out before each commit | deterministic |

**Before the remote-runner gate (on or after 2026-10-09).** These tasks need only research, the
captain, Sonnet crews and the laptop suite:
- S1 to S3;
- T1 and T2;
- T3 and T6 (tests and vectors only);
- T9 (once S1 has landed);
- T11;
- T12's tests;
- the docs.

**After it:** the local-lane bodies (T4, T7 and T10's kernel) and the remote fan-out.

---

## Source lane (starts now)

### S1: Report 45 primary text
- **Lane:** Sonnet crew searches; the captain confirms. **Why:** the result gates M3.3.
- **Do:**
  - Obtain FAA Airframe and Equipment Engineering Report No. 45 (1955), NTIS/DTIC ADA955270, with its
    corrections (23.629(d) cites it "as corrected").
  - Try DTIC again, then NTIS, ROSAP, university libraries and the EAA. Record every attempt.
  - Register `faa-report-45`, `faa-ac23-629-1b`, `cfr14-23-629-2011` and `cfr14-23-1505-2011`.
- **Files:** `data/sources/registry.yaml`; `docs/harness/block3-source-notes.md`.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_sources_registry.py`
- **Done when:**
  - the primary text is registered;
  - the captain has read the wing (F), aileron, elevator and rudder criteria pages, and the
    23.629(d)-equivalent limits, with the page numbers in the notes;
  - every difference from the secondary paper is listed.
  - If the text cannot be obtained, the notes say so and M3.3 stays blocked.

### S2: Validation and design-input sources
- **Lane:** Sonnet crew; the captain checks every number against its page. **Why:** test vectors are
  judgment work.
- **Do:**
  - Register `ncamp-8552-as4` (CAM-RP-2010-002 Rev A).
    - Table 2-1 (p30) is an image: the crew reads it, then the captain re-reads it.
    - Then read Table 2-2 (p31).
  - Find:
    - a glass lamina-to-laminate dataset (NCAMP 7781/2510; CMH-17 Vol 2);
    - a textbook CLT worked example with printed ABD and Tsai-Wu numbers (Kaw 2nd ed., Jones, or
      Daniel & Ishai);
    - a **multi-cell** torsion worked example (Megson);
    - **design** lamina data for the book cloths (BID 7725, UND 7715) and for a wet-laid carbon cloth
      in an epoxy comparable to L285 (fabric data sheets, CMH-17 wet-layup data);
    - a citable f12 (Tsai & Hahn);
    - a citable statement that a mass centroid aft of the elastic axis is destabilising in
      bending-torsion flutter (Bisplinghoff, Ashley & Halfman; Hodges & Pierce).
  - Register `mgs-l285-tds`.
  - If a textbook has to be bought, stop and ask the lead; a purchase is the owner's call.
- **Files:** `data/sources/registry.yaml`, `docs/harness/block3-source-notes.md`.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_sources_registry.py`
- **Done when:** each row of the §5 table reads either "registered, with page/table" or "searched, not
  found, search recorded".

### S3: Speeds, balance data, fleet history
- **Lane:** Sonnet crew; the captain re-reads any image. **Why:** reading values off held scans.
- **Do:**
  - Search the plans, the Canard Pusher and the owner's manual for a designer V_D.
  - Confirm the speed basis of the 190 kt red line (om-1980:p23). If it is not true airspeed, correct the
    `vne_ktas` units label in `data/validation/reference_data.json` with a ledger row.
    `config.v_ne_ktas` is NOT edited (§3).
  - Extract the elevator balance weight mass and station (cobelu chapter 30, mass balance sections), and
    any aileron balance provision (plans chapter 19).
  - Query the NTSB database for in-flight flutter events on the Long-EZ and VariEze.
  - Open the primary records behind ASN wikibase 45809 and 39095.
  - Look for flutter notes in the Canard Pusher.
  - These records inform the §4.5 wording only. No VariEze case is transposed onto the Long-EZ.
  - Where a scan page is illegible, ask the owner for a photograph of that page.
- **Files:** `docs/harness/block3-source-notes.md`; registry entries for anything cited.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_sources_registry.py`
- **Done when:**
  - V_D is sourced, or recorded as not found;
  - the red line's basis is settled;
  - the fleet-history wording is settled;
  - the elevator balance-weight data is sourced (T10's balance-weight control needs it).

---

## M3.0 data skeleton

### T1: Materials file with provenance
- **Lane:** Sonnet crew. **Why:** config-heavy.
- **Files:**
  - Create `data/materials.yaml`, with these lamina sets:
    - `bid_7725_wet` and `und_7715_wet` (book);
    - `carbon_wet_tbd` (design; flagged until S2 finds data);
    - `as4_8552` (validation only, marked `use: validation`);
    - `legacy_uni_glass` and `legacy_bid_glass` (flagged `unsourced`).
  - Each set holds E1, E2, G12, nu12, F1t, F1c, F2t, F2c, F6, ply thickness and areal mass. Each property
    carries a `cite` or a `flag`.
  - Create `tests/test_materials_provenance.py`.
- **Test (write it first; it must be RED):**
  - Every property has exactly one of `cite` (which must pass `core.sources.check_citation`) or
    `flag: unsourced`. A fixture with neither fails.
  - A set marked `use: validation` cannot be referenced from `data/laminates/*` (checked here once that
    directory exists).
- **Verify:** `.venv/bin/python -m pytest -q tests/test_materials_provenance.py`
- **Done when:** the test passes, the broken fixture fails, and no unsourced value is labelled as sourced.

### T2: Kernel purity guard
- **Lane:** Sonnet crew. **Why:** small and mechanical.
- **Files:** `core/kernels/__init__.py` (empty) and `tests/kernels/test_kernels_are_airframe_free.py`.
- **Test.** An AST scan of every `core/kernels/*.py`, walked transitively.
  - Imports are allowed only from the standard library's math, dataclasses, typing and enum, from numpy,
    from scipy, and from `core.kernels.*`.
  - Calls to `open`, and any use of `pathlib` or `importlib`, are rejected.
  - Each of these modules, planted in `tmp_path`, must be reported:
    - one that imports `config` directly;
    - one that imports `core.simulation.fea_adapter`;
    - one that uses `Path("data")`.
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels/test_kernels_are_airframe_free.py`
- **Done when:** the test passes on the empty package and reports every planted module.

## M3.1 laminate kernel validated

### T3: Test vectors (captain)
- **Lane:** captain (Opus). **Why:** vectors from published sources are judgment work.
- **Files:**
  - `tests/kernels/test_lamina.py`, `tests/kernels/test_laminate.py`, `tests/kernels/test_tsai_wu.py`;
  - `tests/kernels/vectors/clt_textbook.yaml`;
  - `tests/kernels/vectors/ncamp_8552_as4.yaml`.
- **Signatures:**
  - `reduced_stiffness(E1, E2, G12, nu12) -> ndarray(3,3)`
  - `transformed_stiffness(Q, theta_deg) -> ndarray(3,3)`
  - `Ply(E1, E2, G12, nu12, t, theta_deg)`, a frozen dataclass
  - `abd(plies) -> (A, B, D)`
  - `laminate_constants(A, h) -> dict(Ex, Ey, Gxy, nuxy)`
  - `ply_stresses(plies, N, M) -> list[ndarray(3)]`, in material axes through the full ABD inverse
  - `tsai_wu_strength_ratio(sigma, F1t, F1c, F2t, F2c, F6, f12_star) -> float`
- **Broken-input tests:** E1 and E2 swapped, an angle's sign flipped, a ply dropped. Each asserts that
  the comparison fails.
- **Unknown material:** a test that asserts an error is raised.
- **Freeze row (validation-bounds freeze), written before T4 runs:**
  - the NCAMP **moduli** bound: mean ± 2 × CV × mean, with the factor 2 flagged as the captain's choice;
  - the textbook bound: the last printed digit;
  - the record that measured strengths are not compared with FPF (§5). FPF and a fibre-failure
    estimate are reported next to them as "not a gate".
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels` (RED: the modules do not exist yet)
- **Done when:**
  - the tests fail for the right reason (ImportError);
  - the freeze row is written;
  - the captain has re-read every vector value on its page.

### T4: Kernel bodies
- **Lane:** local-model implementation lane, one task per file, a Sonnet grader on each output.
  **Why:** each is a single file with an exact signature, fully specified by tests.
- **Files** (at most about 150 lines each):
  - `core/kernels/lamina.py`
  - `core/kernels/laminate.py`
  - `core/kernels/tsai_wu.py`
- **Verify:** each file's own test (for example `.venv/bin/python -m pytest -q tests/kernels/test_lamina.py`),
  then `tests/kernels`.
- **Done when:**
  - the textbook vectors pass to their printed digits;
  - the broken-input tests pass;
  - the purity test passes;
  - the grader found no defect when checking each diff against its source;
  - `fea_adapter.py` is unchanged.

### T5: NCAMP and glass comparison
- **Lane:** captain. **Why:** a pre-registered comparison and its record.
- **Files:**
  - `tests/kernels/test_ncamp_validation.py`
  - `tests/kernels/test_glass_validation.py`
  - a ledger row for the results
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels/test_ncamp_validation.py tests/kernels/test_glass_validation.py`
- **Done when:**
  - all three NCAMP layups' moduli are compared against the frozen bound. Misses are recorded as they
    are, as strict xfails with a row.
  - the strengths are reported next to the FPF and fibre-failure estimates, with no gate.
  - glass is compared, or recorded as having no source. In that case M3.1 stays open on glass, and the
    glass-side gates read `blocked: glass_unvalidated`.
  - the broken-input tests pass.

## M3.2 section kernel validated

### T6: Thin-wall vectors (captain)
- **Lane:** captain.
- **Files:** `tests/kernels/test_thinwall.py`, `tests/kernels/vectors/thinwall_textbook.yaml`.
- **Signatures:**
  - `Wall(x0, z0, x1, z1, t, Gt, Et, rho)`: a straight wall carrying laminate shear and axial stiffness
    per unit width, and mass per unit area
  - `multicell_torsion(walls, cells) -> (GJ, shear_flow_per_wall)`
  - `section_ei(walls, caps) -> float`: every wall contributes, and so do the caps
  - `shear_centre_x(walls, cells) -> float`
  - `mass_props(walls, extras) -> (mass_per_length, centroid_x, torsional_inertia)`
- **Vectors:**
  - the Megson multi-cell worked case (from S2);
  - the existing single-cell `test_gj_known_section` hand case;
  - a two-cell section with a web, which must differ from the same outline without the web;
  - broken-input tests.
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels/test_thinwall.py` (RED)
- **Done when:** the tests fail for the right reason, and every vector value has been re-read.

### T7: Thin-wall body
- **Lane:** local-model implementation lane, with a Sonnet grader.
- **Files:** `core/kernels/thinwall.py`. If it would exceed about 150 lines, split it into
  `thinwall_torsion.py` and `thinwall_props.py`, one task each.
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels/test_thinwall.py`
- **Done when:** the tests pass, the broken-input tests pass, and the grader passes the diff.

### T8: Point fea_adapter at the kernels
- **Lane:** Sonnet crew, with captain review. **Why:** a multi-file refactor is not eligible for the
  local lane.
- **Files:**
  - `core/simulation/fea_adapter.py`: `CompositeSection`, `TorsionSection` and `analyze_ply_by_ply`
    delegate to the kernels, and an unknown material raises an error.
  - A ledger row for every test whose number moves. This explicitly includes
    `tests/test_dbox_deflection.py::test_dbox_spar_cap_tsai_wu_margin` and `::test_dbox_skin_tsai_wu_margin`.
    They grade the margin > 0, and the margin's definition changes from `1 - F` to the strength ratio.
- **Verify:** `.venv/bin/python -m pytest -q`
- **Done when:**
  - every moved number has a row;
  - no bound has changed;
  - the row-68 strict xfails are still strict.

## M3.3 Report 45 screening (blocked until S1 is done)

### T9: Criteria data
- **Lane:** a Sonnet crew transcribes; the captain re-reads every value on its primary page or figure.
- **Files:**
  - `data/criteria/report45.yaml`, holding:
    - the wing F limit constant, its units and its speed basis;
    - the aileron, elevator and rudder limits;
    - the (d)(1) to (d)(3) limits;
    - chart points, each tagged with its figure and `chart-read`.
  - `tests/test_report45_data.py`: every entry cites `faa-report-45:p<n>`.
- **Freeze:** the file's sha256 goes into a criteria-freeze ledger row before T10 runs.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_report45_data.py`
- **Done when:** the file is frozen and hashed, and the captain's re-read is recorded.

### T10: Criterion kernel and book run
- **Lane:**
  - captain: the test vectors and the freeze;
  - local-model lane with a Sonnet grader: the kernel body;
  - a Sonnet crew assembles the book inputs, and does NOT run the criterion.
- **Files:**
  - `core/kernels/flutter_r45.py`, with these functions:
    - `wing_flexibility_factor(theta_per_torque, chord, ds)`
    - `wing_limit(v_d_mph, limit_const)`
    - `vd_max_cleared_mph(F, limit_const)`
    - the balance-parameter functions
  - `tests/kernels/test_flutter_r45.py`. It covers:
    - the IA-100 secondary case;
    - the primary examples;
    - the IA-100 case with GJ divided by 4, which must fail its fixed limit (§4.5);
    - a mixed-unit comparison, which must be rejected.
  - `data/validation/flutter_inputs_book.yaml`. It holds:
    - the cell geometry and ply schedule;
    - the lamina G;
    - the twist per unit torque by station;
    - the control-surface mass properties.

    It is frozen in an inputs-freeze ledger row, together with the registered prediction.
  - `scripts/flutter_screen.py`, which writes `data/validation/flutter_screen.json` with:
    - V_D,max, with its unit and basis;
    - the EAS conversion;
    - `applicability: {d1, d2, d3}`.
  - `tests/test_flutter_screen.py`: the book elevator with its balance weights removed must fail the
    elevator criterion.
- **Verify:** `.venv/bin/python -m pytest -q tests/kernels/test_flutter_r45.py tests/test_flutter_screen.py`
- **Done when:**
  - the book result is reported as V_D,max against the regulatory floor and any sourced V_D, carrying all
    three applicability flags;
  - a failure, or `not_applicable`, is recorded as a strict xfail with its own row;
  - the row-68 tests are unchanged apart from their reason text, which now points at the M3.3 row.
    Retiring them needs the outside reviewer's ruling.

## M3.4 canard equivalence

### T11: Book and carbon schedules, and the sizing rule
- **Lane:** a Sonnet crew extracts; the captain re-reads every value and writes the sizing rule.
- **Files:**
  - `data/laminates/canard_book.yaml`
    - Typed plies, each with: material id, angle, count, BL extent, region (cap, web or skin), a cite
      to its plans or cobelu page, and its `ch30.yaml` op id.
    - The cell geometry, cited to plans pages and not taken from the legacy 0.25c/0.10c D-box.
  - `data/laminates/canard_carbon.yaml`
    - Generated by the sizing rule from wet-layup carbon lamina data only.
  - `docs/harness/block3-sizing-rule.md`, the sizing rule
    - Priority: match EI and GJ at each station, then check strength.
    - A strength miss at matched stiffness is a finding, not a reason to re-size.
- **Inputs-freeze ledger row.** Written before any carbon number is computed. It holds:
  - the sizing rule;
  - hashes of the book lamina values, the mass-kernel inputs (resin fraction, foam density) and the
    cell geometry;
  - the stiffness flag threshold, labelled an unsourced captain choice.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_laminate_schedules.py`
- **Done when:** every ply cites a page or a `ch30.yaml` op and has been re-read, and the freeze row is
  written.

### T12: Equivalence report
- **Lane:**
  - captain: the tests;
  - a Sonnet crew: the script. **Why:** it reads several data files.
- **Files:** `scripts/equivalence_report.py`, `data/validation/equivalence_canard.json`,
  `tests/test_equivalence_canard.py`.
- **Computed per station:**
  - the strength ratio: the minimum, over ±unit M, ±unit T and both f12 values (the cited value and 0),
    of carbon FPF capacity over book FPF capacity;
  - the mass-centroid offset aft of the shear centre, for book and carbon;
  - EI, GJ, the torsional inertia and the mass per length;
  - F(carbon) against F(book), labelled a consistency check.
- **Computed for the whole canard:**
  - the book canard's mass against the closure row's canard mass, reported only;
  - the elevator balance check, applied by analogy. It reads `blocked: criterion_unavailable` while M3.3
    is blocked.
- **Tests:**
  - The strength gate and the mass-placement gate each read `pass`, `fail` or `blocked: <reason>`.
  - Flagging any single input turns `pass` into `blocked`.
  - `glass_unvalidated` and `inputs_unsourced` appear when their conditions hold.
  - The stiffness deltas are present, and flagged where they exceed the frozen threshold.
  - The report regenerates byte for byte.
  - A carbon schedule with one cap ply removed fails the strength gate.
  - F(carbon) doubled fails the relative F comparison.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_equivalence_canard.py`
- **Done when:**
  - every gate's state and reason are in the JSON. `blocked` is an acceptable outcome (§9).
  - the deltas and flags are present.

## M3.5 wing equivalence and relative flutter

### T13: Wing
- **Lane:** as T11 and T12.
- **Files:**
  - `data/laminates/wing_book.yaml`
  - `data/laminates/wing_carbon.yaml`
  - `data/validation/equivalence_wing.json`
  - `tests/test_equivalence_wing.py`
- **Gates:**
  - strength ratio of at least 1.0;
  - mass placement no worse than the book's;
  - the aileron balance criterion, run on both wings.
- **Reported:**
  - F(carbon) against F(book), as a consistency check;
  - V_D,max for both wings, with the applicability flags.
- **Verify:** `.venv/bin/python -m pytest -q tests/test_equivalence_wing.py`
- **Done when:** every gate has a state with its row, and the row-68 disposition is in the ledger.

## Close-out

### T14: Docs and the full run
- **Lane:**
  - docs: Sonnet crew;
  - the fan-out: script;
  - the grade: a fresh-context grader.
- **Files:**
  - `TODOS.md`: remove "one textbook E-glass case" and point at M3.1.
  - roadmap §5: make the same correction, recorded as a ledger row. It corrects a statement, not a
    bound.
  - `AGENTS.md`: add `core/kernels/` to Key Modules.
  - `docs/learnings.md`: one entry.
- **Verify:** the full suite on the remote CPU test runner (`scripts/remote_test_all.sh`), and on the
  laptop with the documented command.
- **Done when:**
  - the suite is green apart from the listed strict xfails;
  - the grader passes the diff;
  - the commits are pushed through the push gate.

## Definition of done (Block 3)

- **M3.1 and M3.2** are validated against registered published data, or their gaps are recorded along
  with what would clear them.
- **M3.3** screening is reported from the primary Report 45, with the (d)(1) to (d)(3) flags, or it is
  recorded as blocked.
- **The canard and wing equivalence reports** are generated by script. Every gate reads `pass`,
  `fail` (a strict xfail with its row) or `blocked: <reason>`.
- **Sourcing and gates.**
  - Every new value is sourced or flagged.
  - Every gate has been shown to fail on a broken input.
- **What stays fixed.**
  - No bound is widened.
  - Frozen rows 65 and 70 are untouched.
  - `v_ne_ktas` is unchanged.
