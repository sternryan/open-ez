# Engine module (O-235 parametric): captain's report

Captain oez-captain, 2026-10-05. Plan: `docs/superpowers/plans/2026-10-05-engine-o235-module.md`. Crews:
- crew-layout (Sonnet): T1 and T2. It computed no CG.
- crew-geom (Sonnet, a different session): T3 to T5.
- crew-wire (Sonnet): T6.
- Captain: T7, plus one Codex `gpt-6-astra` adversary call.

## Result

- **Weight.** The total is 243.0 lb. That is bookkeeping: the core is a residual, so the total equals 243 by construction.
- **CG.** The CG is 11.09 in forward of the prop flange (FS 144.74). TCDS is 14.75 ± 0.5 (FS 141.05, band 140.8 to 141.3), so this is a strict xfail, row 70.
- **Vertical.** 0.56 in below the crank line against 1.13 ± 0.3: strict xfail, row 70.
- **Lateral.** 0.13 in engine-left against 0.20 ± 0.25: passes, but only under the assumed Lycoming left/right convention (`FITTED_LYCOMING_LEFT_V_SIGN` = +1, unsourced). With the sign flipped it would miss by 0.33.
- **Closure row.** The frozen closure engine row is untouched. The module's weight agrees with it; its CG does not (strict xfail, row 70).
- **Layout hash** (row 70): `93b6f317ecdaa617fe3cac1252bed0e2a6a0cbc662f4284800b7b0970ee76cc1`. The frozen constants block is the first 134 lines of `core/engine_o235_book.py`. It is byte-identical to the block written before any geometry or mass code existed. This was checked by diff against the freeze-time copy, and the hash was recomputed from it.
- **Sensitivity.** Each fitted scalar was moved ±25 percent on its own, and the move counted as admissible only if it created no new overlap and kept the engine between the flange and FS 125. Two of 70 inputs move the CG by more than 0.5 in, and one of those is admissible (`FITTED_CYL_FRONT_U`, ±0.80). The other, `FITTED_CASE_LEN` (+0.51), creates a case/housing overlap and does not count. Verdict: the check discriminates, but thinly. No single admissible change comes near the 3.66 in miss. A dependency-consistent sensitivity run is still open (row 70).
- **Codex adversary** (one call). It confirmed that the transform, its inverse, the residual and the centroid arithmetic are correct, and that the 3.66 in miss is an honest model miss. It raised two P1 and three P2 findings, all fixed before the fan-out:
  - P1: the CG xfails were conditional on their own failure predicate.
  - P1: the overlap test had been widened with measured allowances.
  - P2: the carburettor was skipped in the airframe collision check.
  - P2: the sensitivity run included inadmissible layouts.
  - P2: the break-it test never called the acceptance predicate.

## Strict xfails (all cite a ledger row)

| Test | Row | Measured |
|---|---|---|
| `test_cg_matches_tcds_from_the_flange` | 70 | 11.09 in vs 14.75 ± 0.5 |
| `test_cg_vertical_below_the_crank_centreline` | 70 | 0.56 in vs 1.13 ± 0.3 |
| `test_module_cg_agrees_with_the_frozen_closure_row` | 70 | FS 144.74 vs 140.8 to 141.3 |
| `test_engine_parts_are_clear_of_each_other[block-starter]` | 71 | 0.45 cu in |
| `test_engine_parts_are_clear_of_each_other[carburettor-cowl]` | 71 | 2.30 cu in |
| `test_the_carburettor_and_sump_clear_the_cowl_bottom` | 71 | carburettor bottom WL 10.25 vs cowl bottom 11.0; the sump clears |
| `test_bracket_is_inside_the_cowl` | 71 | bracket WL 8.04 to 10.11 vs cowl inner bottom 11.12 |

## Open issues

- **Unsourced inputs.** The crank-line WL (`eng_book_block_wl` 23) is unsourced, and it is the likely lever on the cowl and bracket misses. It was not re-tuned.
- **Lycoming left/right.** The convention is unsourced. The adversary rated it about 8/10 likely, from a Lycoming cylinder-orientation diagram. Register that source before upgrading the flag.
- **Magneto weight.** The registered figure is the Slick 4300 series. The TCDS names the 4251 and 4250.
- **Deploy render.** The GLB carries six new parts. The deploy render needs the GPU lease, has not run, and the lead gives the heads-up.

## Commit split

The lead commits and pushes. Stage named files only, and add no session trailer.

**Commit 1: `feat(engine): O-235 TCDS fields and sources`**

Add the O-235 flange datum (155.8, derived), the TCDS CG from the flange, below the crank line and left (14.75, 1.13, 0.20), and the bore and stroke, with provenance. Register the Lycoming operator's manual and the Slick 4300 vendor page.

Files:
- `config/aircraft_config.py`
- `data/sources/registry.yaml`
- `tests/test_engine_o235_fields.py`
- `tests/test_geometry_provenance.py` (prefix regex now `eng_(book|o235)_`)

**Commit 2: `feat(engine): O-235 component module, mass properties and lab wiring`**

The layout constants were frozen and hashed (row 70) before any CG code existed. The component geometry is placed from the prop flange, and the block becomes the crankcase, cylinders, sump, housing and flange compound. Six new representational parts are added. `engine_mass_properties()` gives the sourced starter, alternator and magnetos and shares the residual core by volume times density. The CG misses TCDS (11.09 against 14.75 in from the flange) and stays a strict xfail, with the layout not re-tuned. `eng_book_block_fwd_fs` is retired for `block_front_fs()` (row 71). The lab gets striped parts, a mass table and the f23 readout.

Files:
- `core/engine_o235_book.py`
- `core/engine_book.py`
- `tests/test_engine_o235_layout.py`
- `tests/test_engine_o235_geometry.py`
- `tests/test_engine_o235_mass.py`
- `tests/test_engine_geometry.py`
- `docs/geometry-correction-ledger.md` (rows 70 and 71)
- `guide/fuselage_export.py`
- `guide/graph/ch23.yaml`
- `guide/graph/components.yaml`
- `guide/lab/src/logic/strake.ts`
- `guide/lab/tests/m28.test.ts`
- `guide/lab/tests/fixtures/kernels.json`
- `tests/guide/test_export_glb.py`
- `tests/guide/test_ch2123_graph.py`
- `tests/guide/test_lab_e2e.py`
- `TODOS.md`
- `AGENTS.md`
- `docs/harness/engine-module-report.md`

Commit 2 cannot be split further without breaking the suite at an intermediate commit: the new `build_engine()` keys fail the guide graph tests until the wiring lands. The freeze order is evidenced by the hash and the byte-identical frozen block, not by commit order.
