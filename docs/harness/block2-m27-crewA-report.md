# M2.7 crew A report: config, graph, geometry (chapters 19 and 20)

Branch `m27-crewA`, three feature commits, nothing pushed. Full suite
(`pytest -m "not local_render" --ignore=tests/guide/test_lab_e2e.py`, serial, foreground): 1146 passed, 3 skipped,
9 xfailed, 1 deselected. `guide.check` (full mode): OK, 14/14 annotations recovered. Lab unit tests (node, 207) and viewer
tests (50) pass. Leak scan on the diff against main is empty; `git status` clean.

## Commits

| Commit | What |
|---|---|
| 4620a31 | Task 1: `config/aircraft_config.py` wing and winglet book blocks (about 75 new fields and the derived properties), `GEOMETRY_PROVENANCE` entries, provenance notes on `wing_span`, `wing_root_bl`, `wing_le_anchor`, new `unsourced` entries for `wing_washout` and the three `winglet_*` fields (values unmoved), five CP26 reference rows in `data/mass_ledger.yaml`, the 125.61 against 113.9 closure in `docs/geometry-correction-ledger.md`, `tests/test_wing_stations.py`, `tests/test_winglet_stations.py` |
| 4c78734 | Task 2: `guide/graph/ch19.yaml` (18 ops), `ch20.yaml` (9 ops), 20 components, pages 118 to 140, stubs removed, ch16 requires repointed, `tests/guide/test_ch19_graph.py`, `test_ch20_graph.py`, two older graph tests updated |
| 0911db5 | Task 3: `core/wing_book.py`, `core/winglet_book.py`, `guide/fuselage_export.py` (m27 components and section), `guide/export_glb.py`, `tests/test_wing_geometry.py`, `tests/test_winglet_geometry.py`, glb tests |

Suite grew from 1080 to 1146 passing tests over the three commits.

## Task 1 findings

- Two checks that agree to within print rounding and that the tests lock: the TE heights WL 16.95 and 18.35 on p126 come out of the printed
  twist (TE rise = chord times tan of the washout; model gives 16.953 and 18.343). The 18.42 deg web line closes to the printed 164.2 within 0.15.
- Field names avoid `attach` and `stop` tokens because `tests/test_spar_stations.py` forbids them in any field or provenance key (renamed
  `wing_spar_join_*`, `wing_aileron_max_up_deg`).
- A/B/C closure (p136): A residual -0.066 in, B -0.248 in (both inside the spec's closure), C only with the derived inward lean 3.58 in (upright C is 2+ in out).
- The ledger rows are in no sum (`fuselage_cg` matches by fuselage part name; test added).

## Task 2: local-model draft outcome (for the lane log)

27 ops drafted; all kept their ids, requires, components and pages from the op plan. Light edits (wording only): f19.mount-cores,
f19.hardpoints, f19.pads-plates, f19.le-cores, f19.bottom-skin, f19.top-skin, f20.cut-cores, f20.trim = 8. Substantive fixes: 19.
What was wrong in the drafts: four ops used `scan_pp: 124, 129` (schema break, 4 ops); five change entries were invented or mislabelled
(CP24 LPC 6 on the conduit, CP32 LPC 6 on the aileron, CP25 LPC 7 for the LWA7 rename on the ribs, CP26 LPC 8 and CP31 LPC 4 on ch20); LPC 31 was
classed `cp-hint`; A, B and C (and CP25 LPC 6) sat on the skins op instead of the jig op with no values; the jig op said "total span 125.6"
(it is a floor-line length); three conflicts and the printed UND table, rudder dimensions and cap lengths were missing. The lane stays skipped for
op YAML on this evidence (the drafts were a usable skeleton, not usable text).

## Task 3 geometry: what is drawn and how

- Frame as the fuselage: x = FS, y = BL, z = WL - 17.4. Both wings and winglets are placed in the airframe frame (no pose); the left side is the mirror.
- Cores FC1 to FC5 are ruled lofts of polygon sections, split at the shear web and the aileron hinge line (no booleans between near-coincident faces). FC1 has
  cut hard-point depressions, a torque-tube slot and a root bay. Aileron solid BL 55.5 to 118.1 behind the top hinge line (FS 149.7, 161.45 from the printed cuts).
- Section: the Eppler file scaled in thickness about its camber line to the printed 16.2 / 15.7 / 15.0 per cent, sheared by the washout. All tagged
  representational. Only the printed-size hardware (hinge pins, balance rod, torque tube, spar bolts, winglet jig lines) is tagged derived.
- Display plies (web 6, caps 5 + 7, wing skins 3 + 3, winglet skins 3 + 2, corner layup 3) float 0.02 in off the core surface; they are not in the non-overlap set.
- Poses: `wing_book.aileron_pose(shape, deg_up)` 0 to 20, `winglet_book.rudder_pose(shape, deg)` within 30 either way, positive TE outboard.
- Export: `wing.*` and `winglet.*` groups with children `<id>.<part>.<right|left>` (ply parts: one child per ply); `extras.m27` in layup.json carries part and ply rows, both
  hinge axes and stops, the three conflicts, the A/B/C closure, the lean and the tip chord as data. `wing.jigs` and `winglet.jig` are flagged workshop.
- Small edits outside the brief: `guide/lab/src/logic/graph.ts` NON_CANARD (19, 20), `guide/lab/src/logic/m25.ts` FUSE_PREFIXES (wing., winglet.), `guide/viewer/js/app.js` skip list.
  Crew B may want to revisit the lab ones.
- `/conduct` on local-model lane was not used: the kernels are small and were written and tested directly.

## Values and shapes I could not place (all fitted, tagged, and named in part notes)

- Jig BLs and outlines (page 19-1 is not on the scan): the five jigs are spread over BL 23.7 to 157 from the printed floor spacings; outline fitted.
- Hinge spans along the aileron (the p124 spacing digits are cramped): A3 8 in, A4 6 in twice placed by eye.
- Torque-tube slot, light-hole offsets, the 3 by 8 aileron chunk, the hollowed FC1 wedge and 0.6 in shell, W18 strips, LWA offsets: not drawn or fitted.
  LWA4 across-size is fitted (CP43 LPC 119 resizes it in chapter 14); plates behind the blocks are drawn at 1/8 in.
- Root bay controls: one belhorn arm, two CS127 and the CS128 as plates; CS132L, CS150 to CS152 shapes are on full-size patterns, not drawn.
- Cap offsets: four printed for seven top plies; plies 1 and 2 flush, the 6 in step continued to ply 7.
- Winglet: airfoil (14 per cent symmetric), lower fin outline (TE bottom FS about 190 follows from the printed 11.5 in rudder width; LE bottom FS 178 from the 12 in dimension, medium),
  block A, tip cap, corner layup extents along the chord, layups 1, 2 and 4 not drawn, the 14 in BID patch start.
- Cant: the lean 3.58 in is derived-low; the fin stands outboard of the tip rib by its half thickness plus 0.25 in so it does not overlap the wing (A/B/C are computed from BL 157).

## Open questions for the captain

1. p88 spar tip is BL 56.46 and its end bulkhead reaches BL 56.7, but p126 puts the foam joint at BL 55.5. FC4 starts at BL 56.75 to clear the spar (otherwise 20 in3 overlap).
   Is p88's half-span measured along the swept face?
2. The airfoil file's own thickness is 8.7 per cent against 15 to 16.2 printed. I scaled it (about 1.9x). Its provenance (and whether it is the p126 section) is unchecked.
3. `topo_order` now drops chapter 19 (18 ops) between chapter 16 ops and chapter 20 (8) before chapters 17 and 18, because ch16 waits on `f19.controls`, `f19.attach` and `f20.rudder-hang`.
   That follows the op plan; the lab's build order will show it.
4. Rod length: 65 in printed, 63.9 in hinge-line span. The model trims to the aileron (BL 55.5 to 118.1, 0.1 in short each end).
5. `wing_root_bl` 23.3 and `wing_span` 313.2 are unmoved; the build model uses BL 23 and 157. The strake region inboard of BL 55.5 forward of the web is not drawn.
6. The ruff in the shared venv (0.16) differs from the pre-commit pin (0.5.4): `config/aircraft_config.py` already reports 68 UP006 style errors on main and now 106 (the new `Tuple[...]`
   fields, like the canopy block). New `core/` and test files are clean under it.
7. `-n 8` is not available (no xdist in the shared venv); the suite ran serial in 5 to 8 minutes. The commit hook only credits an unpiped pytest run in the same repo, and `git -C` commits.
