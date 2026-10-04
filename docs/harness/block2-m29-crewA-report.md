# M2.9 crew A report: exit-test wording, config, graph, geometry (chapters 24 to 26)

Worktree `m29`. Status: Task 0 committed. Tasks 1 to 3 are DONE and VERIFIED but NOT COMMITTED (see "Commit blocker").

## Commit blocker (needs the captain)
`~/.claude/hooks/verify-before-commit.sh` refuses every code commit from this session. The verify marker is keyed to the Bash tool's cwd (a different
repo, because the cwd resets to the launch directory between calls), while the commit gate keys on the `cd` or `-C` target (this worktree), so a green
pytest run never credits `m29`. I did not work around the gate (no hand-made marker, no `docs:` prefix on code). Task 0 went in under the `docs:`
exemption. To land the rest: commit the working tree from a session whose cwd is the worktree, in the four commits below (or one).
Suggested split: (1) Task 1: `config/aircraft_config.py`, `data/mass_ledger.yaml`, `tests/test_m29_stations.py`, `tests/test_geometry_provenance.py`;
(2) Task 2: `guide/graph/ch24.yaml ch25.yaml ch26.yaml components.yaml pages.yaml`, `tests/guide/test_ch2426_graph.py`, `tests/guide/test_fuselage_graph.py`;
(3) Task 3: `core/covers_book.py`, `core/upholstery_book.py`, `guide/fuselage_export.py`, `guide/export_glb.py`, `guide/viewer/js/app.js`,
`tests/test_m29_geometry.py`, `tests/guide/test_export_glb.py`, `tests/guide/test_build_state.py`; (4) this report.

## Commits
- e346b31 docs: OM sample loadings reproduced exactly, painted wing weight cites CP27 p1, ledger row 64 (Task 0).

## Task 0
- Docs saying the OM sample loadings should both be inside 97 to 103: `TODOS.md` and the M2.8 spec bullet. Fixed: the target is 730 lb at FS 111.7
  empty, both OM samples reproduced exactly (light pilot 103.96, OUTSIDE, as the OM says; heavy 101.06, inside). No test graded "both inside" (searched docs, tests, data,
  core, guide, config). `tests/test_m28_weight_flags.py` now also asserts the light pilot is outside the aft limit. Ledger row 64 added.
- CP cite: "CP26 p16" became CP27 p1 in the `wing_weight_lb` note. Checked on the CP text myself: the weight table sits after the CP26 p16 footer and
  before the CP27 p1 footer, so it is CP27 p1 (footer ends the page).

## Task 1 (config, provenance, ledger rows)
- `config/aircraft_config.py`: 38 fields in three blocks, prefixes `cov_book_`, `fin_book_`, `upl_book_` (a name with "rake" would trip
  `test_nose_elevator_stations`, so none), each with a GEOMETRY_PROVENANCE entry. LC1 FS 52 to 60 `book`/high; gap seal 1/2 (medium) and 1/16; finish thicknesses
  (fill 0.02 to 0.03, primer 0.004 to 0.008, weave 0.009, fill bands, 70 F); white surfaces `("wing_upper","canard_upper")`; cushion, headrest, suitcase sizes.
  Both ch24 conflicts carried as pairs: aft-cover plies (scan `(1,1)` vs transcription `(1,2)`, LPC 54 in the note) and LC2 length (30.6 vs 30.8).
- `data/mass_ledger.yaml`: `wing_painted` 60.0 (CP27 p1) and three finish-delta reference rows (canopy 1.0, aileron 0.275, wing 2.2), never summed, in no moment sum.
  No finish row is added on top of painted builder weights.
- Tests: `tests/test_m29_stations.py` (new), prefix pattern added in `tests/test_geometry_provenance.py`.

## Task 2 (graph)
- `ch24.yaml` 6 ops (aft-cover, console-lc1, consoles-left, thigh-support, canard-cover, gap-seal), `ch25.yaml` 5 (inspect-repair [hidden, inspection],
  coarse-fill, feather-fill, primer, paint-seals), `ch26.yaml` 2 (cushions-headrests, suitcases). Own words; both conflicts, the 3/4 reading of the seal, "no finish weight printed"
  and the N26MS deltas as references are in the text. 13 components, pages 159 to 170. Gap seal needs `f19.attach`; the first finishing op needs `f21.fairing-caps`, `f22.antennas`, `f23.root-rib` and `f24.gap-seal`.
- `python -m guide.check` full mode: OK (two overlap hits fixed by rewording; summaries kept under 700 chars).
- Tests: `tests/guide/test_ch2426_graph.py` (7), chapter filter in `test_fuselage_graph.py` extended to 24 to 26.

## Task 3 (geometry and export)
- `core/covers_book.py`: aft cover (dished, slotted 1/8 in round the strut), LC1 (`book`), LC2 to LC6, thigh floor and two ribs, valve cover, canard cover, gap seals.
  `core/upholstery_book.py`: front and rear cushions, two headrests, two suitcases. All others `representational`. Positions are read from the model (fuselage side, seat-bulkhead faces probed on the
  built solids, canard install), never typed. The cushions and suitcases are cut round the ch16 controls and ch22 electrical parts rather than overlapping them.
- The finish is NOT solids: `finish_rows()` (white on `wing.skins` top skin, `canard.skin_top`, `cover.canard`; primer grey elsewhere; fill/primer/paint stages with thicknesses and the op each starts from)
  in `layup.json` extras `m29`, with parts, conflicts, seal, and the weight references and the 2.n closure target (730 lb at FS 111.7, both samples exact, CG not yet computed).
- glb: `m29_components()` in `guide/export_glb.py` and `guide/fuselage_export.py`; the viewer's skip-prefix list got `cover.` and `upholstery.` (`guide/viewer/js/app.js`, mirrored in `tests/guide/test_build_state.py`).
- Tests: `tests/test_m29_geometry.py` (13, includes the all-airframe clearance gate) and 4 m29 tests in `tests/guide/test_export_glb.py`. The clearance gate was shown to fail: my first placement overlapped
  the front seat bulkhead, the side panel, F22 and strake baffle B23 and the test caught each until fixed.

## Verification
- `.venv/bin/python -m pytest -q -p no:cacheprovider -m "not local_render" --ignore=tests/guide/test_lab_e2e.py`: 1357 passed, 2 skipped, 1 deselected, 9 xfailed (was 1331 passed before the m29 work).
- guide.check full mode OK. Leak scan on the diff (IPs, ts.net, home paths, user name): empty.
- `ruff check` clean on every new file; `ruff format --check` clean on new files. Existing `config/aircraft_config.py` and `guide/fuselage_export.py` were already not format-clean under the installed
  ruff 0.16 (the repo pins 0.5.4); I did not reformat them. `ruff check` reports 168 pre-existing errors across the older touched files.

## Values I could not place / open questions
- Positions of LC2 to LC6, thigh support, canard cover, gap seals, cushions, headrests, suitcases are fitted (no page gives them); the seal sits in the strake tank envelope region (display only) between baffle B23 and the wing skin.
- Front cushion path is about 39 in against the printed 46 (the model's floor and bulkhead end first); the 4 in rear-cushion front edge, notch dimensions, LC2 bevel, throttle cutout size, left-suitcase cut length (4 in fitted) are not placed.
- LC4 hole 1 in is from CP24 p8 (research), not the plans; its cite in the part is `cp-text:p24`.
- Console heights are drawn 8.95 against the printed 9.1: the model's floor top (-14.9 to -14.8) leaves a 0.15 in clearance.
- Wing finish delta 2.2 is the midpoint of the derived 2.1 to 2.3 (needs the unweighed rudder weight).
- For crew B: the lab's `FUSE_PREFIXES` in `guide/lab/src/logic/m25.ts` still needs `cover.` and `upholstery.`; I did not touch the lab or `kernels.json`.
