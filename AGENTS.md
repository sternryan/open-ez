# Open-EZ

This is the single instruction file for this repository; Claude Code, Codex and any other coding agent read it directly.

## Project Overview

open-ez models the Rutan Long-EZ (Model 61) as code: CadQuery geometry, an in-browser build
rehearsal (`guide/`), and physics checks, with every value traced to a registered source page or
visibly flagged. The direction is set by the roadmap,
`docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`: same airplane,
new process (rehearse the book build, then test changed parts on paper, then printed plugs, cast
molds and carbon).

This is a PUBLIC repository. See "Public-repo hygiene" below before adding anything.

## Tech Stack

- **Python 3.11+** (the local venv runs 3.12; CI runs 3.11)
- **CadQuery** (OpenCASCADE B-Rep kernel) for geometry
- **OpenVSP 3.53.1 / VSPAERO** for the vortex-lattice leg of the two-method NP check. Its Python
  bindings are not on pip; `scripts/install_openvsp.sh` installs them for a separate python3.13.
- **NumPy/SciPy**, **ezdxf**, **PyYAML**
- **Guide:** a static site built by `guide/build_site.py`; viewer in `guide/viewer/` (three.js,
  node tests); Playwright for the viewer end-to-end tests (`requirements-guide-dev.txt`)

## Commands

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -r requirements-guide-dev.txt
.venv/bin/python -m pytest -q                      # full Python suite
node --test guide/viewer/tests/*.test.mjs          # viewer unit tests
.venv/bin/python -m guide.check --schema-only      # guide schema gate (full mode needs the private corpus)
.venv/bin/python -m guide.export_glb --out output/guide/longez.glb
.venv/bin/python -m guide.build_site --out site --models output/guide/longez.glb
python3.13 scripts/vspaero_np.py                   # VSPAERO NP leg -> data/validation/vspaero_np.json
.venv/bin/python scripts/generate_accuracy_report.py  # -> data/validation/accuracy_report.json
pre-commit run --all-files                         # ruff, ruff-format, mypy (scripts/), smoke test
```

The test suite writes only to pytest's `tmp_path`. It does not rewrite tracked files; if a run
leaves `git status` dirty, that is a bug in a test, not something to restore by hand.

## Architecture

### Single Source of Truth (SSOT)
All dimensions derive from `config/aircraft_config.py`. Never hard-code dimensions; use the config
fields and derived properties (for example `fs_wing_le` is derived from `wing_le_anchor` and the
sweep, `fuselage_length` is `fs_tail - fs_nose`). Changes to config propagate through geometry,
analysis, the report and the guide.

### Sources and provenance (the rule every value follows)
- Every citable document is registered in `data/sources/registry.yaml`. A citation is
  `<id>:p<page>`; `core/sources.py` rejects unknown ids.
- Every geometry value in `GEOMETRY_PROVENANCE` (`config/aircraft_config.py`) is `book`,
  `cp-corrected` or `derived` with a registry citation, or is flagged `conflict`, `unsourced` or
  `converted-unsourced`. Never upgrade a flag without a page in hand.
- `data/validation/reference_data.json` entries are `confirmed`, `derived` or `unverified`. Only
  confirmed and derived values count as truth (`core/reference.py`); a check may not grade against
  an unverified value.
- Never measure an undimensioned image and call it a source.
- A physics bound that the book geometry fails is left failing (strict `xfail` citing its ledger
  row), never widened. Record every moved test in `docs/geometry-correction-ledger.md`.
- A gate counts only after it has been shown to fail on a deliberately broken input.

### Directory Structure
- `config/` aircraft configuration and `GEOMETRY_PROVENANCE`
- `core/` geometry, analysis, mass ledger, sources, manufacturing, compliance
- `guide/` build-rehearsal graph (`guide/graph/*.yaml`), site builder and viewer
- `data/` airfoils, source registry, mass ledger, validation data
- `scripts/` report generation, VSPAERO NP, source fetcher, smoke and CI checks
- `tests/` Python suite (`tests/guide/` for the guide)
- `docs/` reports, ledger, specs and plans (`docs/superpowers/`), captain logs (`docs/harness/`),
  and `docs/history/` for retired planning documents
- `output/` generated artifacts only, gitignored, nothing tracked

### Key Modules
- **AirfoilFactory** (`core/aerodynamics.py`): ingests .dat files, CubicSpline smoothing,
  trailing-edge closure, washout and reflex
- **WingGenerator / MainWingGenerator / CanardGenerator** (`core/structures.py`): lofted foam cores
- **Analysis** (`core/analysis.py`): NP, static margin, CG limits, partial-span canard downwash
- **Mass ledger** (`core/ledger.py`, `data/mass_ledger.yaml`): per-part mass and CG with sources
- **O-235 engine module** (`core/engine_o235_book.py`): representational component geometry placed from the prop
  flange, and `engine_mass_properties()` (sourced accessories plus a residual core); layout frozen by hash (ledger row 70)
- **GCodeWriter / GCodeEngine** (`core/manufacturing.py`): 4-axis hot-wire paths (never run on a machine)
- **ComplianceTracker** (`core/compliance/`): builder-credit tally for the 51% rule

### Base Class Pattern
Components inherit from `AircraftComponent` (`core/base.py`) and must implement
`_build_geometry()`, `export_dxf()` and `manufacturing_plan()`.

## Canard Airfoil Default

The canard airfoil defaults to the Roncz R1145MS, chosen for its behaviour in rain (the original
GU25-5(11)8 loses lift when wet). `AircraftConfig.validate()` reports an error if the canard airfoil
is changed. Do not remove that default. Note the planform is still GU-sized: no Roncz chord source
has been found (`docs/block1-report.md`, "Still flagged").

## Current State

Do not copy numbers into this file; they go stale. Read:
- `docs/block1-report.md`: Block 1 (baseline truth) results, current NP, CG and report counts, and
  the "Still flagged" list with what clears each item.
- `docs/geometry-correction-ledger.md`: every test that moved and why.
- `data/validation/accuracy_report.json`: the live report (`metadata.checks`, `summary`).
- `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`: Block 2 (rehearsal) in progress.
- `TODOS.md`: open items.

## Known Issues

- The two-method NP check fails (analytic vs VSPAERO, bound 1.0 in); left failing on purpose.
  Diagnosis and numbers: `docs/block1-report.md`.
- Canard planform is GU-sized (conflict flag); the Roncz planform is unconfirmed.
- The elevator torque tube is 1 in OD (book); the canard section is fitted to an airfoil file (`data/airfoils/roncz_r1145ms.dat`) that is thinner than the tube: unresolved, labelled so in the lab. Check the file's provenance and t/c in the Block 1 airfoil look before any printed plug.
- Empty weight: the closure table exists (`data/mass_ledger.yaml` `closure:`, frozen, ledger row 65) and its verdict against the target is read by the `empty_weight_closure` accuracy metric (currently over the weight cap, so it fails, as recorded in rows 65 to 68). The `empty_weight_lb` metric is graded against the manual's approximate 750 lb normally equipped, a different configuration. The closure target is the OM sample empty airplane, 730 lb at FS 111.7 (om-1980:p25, p35). The computed CG limits fail against FS 97 to 103, the LOADED CG envelope (om-1980:p28); they follow the neutral point and do not wait on the ledger. The empty CG is never graded against 97 to 103.
- The fuselage box (`core/fuselage_book.py`, chapters 4–9) and the nose (`core/nose_book.py`,
  chapter 13) tag every part `book`, `derived` or `representational`; F22, F28, the panel, the
  firewall, the bottom, the gear strut, the NG30 plates and the nose outline are fitted shapes (their
  outlines are on full-size sheets the owner does not hold). The model runs from the nose tip to the
  firewall; nothing aft of the firewall is modelled yet. The nose-wheel station is a conflict (17
  printed, about 20 in the manual) and both are carried.
- Regression snapshots (`tests/snapshots/`, `accuracy_report.json`) lock the code's current output;
  they are not external truth.
- Nothing has been validated against hardware. G-code has never run on a CNC machine.

## Commit Hygiene

- Stage named files; never `git add -A` or `git add .` (private material and build outputs live
  in the tree).
- Run the full suite green before committing.
- Commit messages say what changed and why; claims in a message must be true of the diff.

## Public-repo hygiene

- The Long-EZ plans remain under copyright. The repo holds its own code and its own words. Do not
  commit plans pages, scans, OCR text or long quotes; cite by registry id and page, paraphrase in
  ten words or fewer.
- `private/` (scan renders, OCR) and the source corpus (`$LONGEZ_SOURCE_CACHE`) are never
  committed.
- No hostnames, IP addresses, home-directory paths or private locations in tracked files. Deploy
  targets come from environment variables (`scripts/deploy_guide.sh`).
- Third-party code keeps its license notice in `NOTICE`.

## Regulatory

Outputs are fabrication aids for an amateur-built aircraft, not certified data. The
ComplianceTracker tallies builder credits toward the 51% rule, 14 CFR 21.191(g).

## History

Retired planning documents, including the original swarm personas, are in `docs/history/`.
