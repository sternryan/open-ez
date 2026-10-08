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

## Next, in order

1. **T11 re-read.** Re-read the canard schedule against the cobelu chapter 30 page images the crew
   listed:
   - p11, Fig 30-16: shear-web extents and crossing angle;
   - p12, Fig 30-17: pads;
   - p8: nutplate BL;
   - p14 and p15: cap ply 1;
   - p21, Fig 30-34: top skin order and angles;
   - p23 and p24, Fig 30-41: elevator ±30;
   - p32, Fig 30-54: strip angle.

   Also check the crew's interpretation of the shear-web BID "inboard of BL 20/10" extents. Then set
   `reread` in the file.
2. **T11 part 2 (captain).**
   - Write `docs/harness/block3-sizing-rule.md`. Priority: match EI and GJ per station, then check
     strength; a strength miss at matched stiffness is a finding.
   - Generate `data/laminates/canard_carbon.yaml` from `carbon3k_mgs418_wet` only. It is a design proxy:
     MGS 418, not L285, and its 1-axis values are still unsourced, so every carbon gate will read
     `blocked: inputs_unsourced` until those are read from AGATE 115.
   - Write the inputs-freeze ledger row (next free row: 74) BEFORE any carbon number is computed.
3. **S2 follow-up results (done after part 1).**
   - **AGATE 114 and 115 test the FILL direction only** (Table 1.5.1, printed p8). No warp (1-axis)
     values exist in either report, so the wet-layup design proxies cannot be completed from AGATE. The
     notes in `data/materials.yaml` say so. Every carbon and glass design gate therefore reads
     `blocked: inputs_unsourced` until a warp-direction source is found (another AGATE report, a supplier
     sheet) or Block 5 coupons supply one. Finding that source is the next S2 task.
   - **A multi-cell torsion vector was found and checked.** M. Stere, "The torsion of the multicell
     sections", INCAS Bulletin vol 2 no 3 (2010), section 5, Example 1, printed pp104-105. It is a
     three-cell wing section from Megson 3rd ed.
     - Inputs: T 11.3 kNm, G 27600 N/mm2, cell areas 258000, 355000 and 161000 mm2, and the wall
       length/thickness table.
     - Printed results: q = 6.9764, 8.6951 and 4.7412 N/mm, and J = 6.4708e4 cm4.
     - A crew recomputation from the printed geometry agrees to about 0.03%.
     - The topology (cell I = wall 12 plus web 12i; II = 13, 24, 12i, 34; III = 35, 46, 34, 56) was
       inferred from the wall labels and reproduces the printed web flows.
     - The printed GJ units look a factor of 10 off. Use q and J, not GJ.
     - To do: register it (`incas-stere-2010`), and the captain re-reads the figure for the topology.
       Freeze its bound BEFORE T7 runs; the printed figures carry about 3 to 4 significant digits of
       agreement, so 0.1 percent is the natural bound.
4. **T6.** Write the thin-wall vectors from the Stere/Megson case plus the existing single-cell hand
   case.
5. **T12 tests (captain).** Gate states (`pass`, `fail`, `blocked: <reason>`); flagging any single
   input forces `blocked`; strength ratio minimum over ±M, ±T and both f12 values; the mass-placement
   gate; byte-identical regeneration; and the broken carbon schedule fails.
6. **S3 follow-ups.**
   - Correct the `vne_ktas` units label in `reference_data.json` (indicated, not true) with a ledger
     row. `config.v_ne_ktas` is NOT edited.
   - Retry the NTSB lookups for N25063 and N707LT (ASN 45809 and 39095).

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
