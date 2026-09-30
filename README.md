# open-ez

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **Safety notice.** This repository holds fabrication aids and study material for an
> amateur-built aircraft. It is not certified engineering data, and nothing in it has been
> validated against hardware or in flight. Several values are known to be unsourced or in
> conflict with the book (listed below). If you build anything from it, you are responsible for
> checking every dimension, load and number against the plans and independent sources. Mistakes
> in aircraft geometry or structure can kill people.

## What it is

open-ez models the Rutan Long-EZ (Model 61) as code. It has three parts:

- **Geometry.** Wing, canard and foam cores built in [CadQuery](https://github.com/CadQuery/cadquery)
  from one configuration file, `config/aircraft_config.py`.
- **Build rehearsal.** A static site with a 3D viewer (`guide/`) that walks through the book build
  as a sequence of operations: the canard chapters so far (the original GU canard and the Roncz
  canard that replaced it), with a section cut through the layup and load paths that follow the
  build.
- **Physics checks.** Neutral point, static margin, CG limits and a mass/CG ledger, with a
  two-method neutral point check (an analytic method against a VSPAERO vortex-lattice run).

The rule throughout is traceability to the book. Every value cites a registered source page or is
visibly flagged:

- `data/sources/registry.yaml` lists the documents a value may cite, as `<id>:p<page>`.
- `GEOMETRY_PROVENANCE` in `config/aircraft_config.py` gives each geometry value a status: `book`,
  `cp-corrected` or `derived` with a citation, or a flag (`conflict`, `unsourced`,
  `converted-unsourced`).
- `docs/geometry-correction-ledger.md` records every test that moved when the geometry was
  corrected, and why.

## Where it's going

The plan is "same airplane, new process". Keep the Long-EZ's outer shape, weights and CG envelope,
and change how it is made. First, rehearse the book build in full so the original airplane exists
as data. Then test changed parts on paper against the book parts. Then move to 3D-printed plugs,
cast molds and carbon fiber, with coupon tests and outside review before anything is trusted. The
roadmap, with its blocks and what each must prove, is in
[`docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`](docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md).

## Honest status

Block 1 (baseline truth) is done in the sense that every value is sourced or flagged. It is not
done in the sense of everything agreeing. The details and the evidence that would clear each flag
are in [`docs/block1-report.md`](docs/block1-report.md). In short:

- **Book-sourced:** wing span, tip chord and sweep; the main fuselage stations (nose, firewall,
  seats, strake leading edge); the wing leading-edge anchor (from a Canard Pusher correction); max
  gross weight, approximate empty weight and the CG envelope from the owner's manual. The wing
  reference area (81.70 sq ft) comes within 0.4% of the manual's 81.99.
- **Flagged:** the canard waterline and incidence, the fuselage tail station and length, the wing
  root butt line, the strake trailing edge, most structural weight arms, and the neutral point,
  stall speed and airfoil coefficients in the reference data (not found in any source held).
- **The canard is GU-sized.** The repo uses the Roncz R1145MS canard airfoil, but no source for the
  Roncz canard's chord was found, so the planform uses the GU canard's span and area from the
  owner's manual and is flagged as a conflict.
- **The two-method neutral point check fails.** The analytic method gives FS 110.68 and VSPAERO
  gives FS 112.36, against a bound of 1.0 in. It is left failing on purpose rather than tuned. The
  report's diagnosis is the analytic model of canard downwash on the swept wing.
- **Empty weight and CG limits fail** against the manual. The structural weight model is partial;
  the per-part ledger in Block 2 is meant to close it.
- **Nothing here is validated against hardware.** The G-code has never run on a machine, and no
  part has been built from these files.

Block 2 (rehearsing every chapter, and extracting ply schedules and materials as data) is in
progress.

## Canard airfoil

The repo defaults to the Roncz R1145MS canard airfoil for its rain behaviour: the original
GU25-5(11)8 canard loses lift when wet. `AircraftConfig.validate()` reports an error if the canard
airfoil is changed.

## Copyright and the plans

The Long-EZ plans remain under copyright. This repository holds its own code and its own words and
does not reproduce plans content: no page images, scans or OCR text are committed, and the guide's
operation summaries are written fresh and cite the book by page. To follow the build you need your
own copy of the plans. The guide can link to your own page scans if you point it at them (see
below).

## How to run

Requires Python 3.11 or newer.

```bash
git clone https://github.com/sternryan/open-ez.git
cd open-ez
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt -r requirements-guide-dev.txt   # lint, guide and viewer tests
```

Tests:

```bash
.venv/bin/python -m pytest -q                    # Python suite; writes only to temporary dirs
node --test guide/viewer/tests/*.test.mjs        # viewer unit tests (Node 18+)
```

The guide end-to-end tests use Playwright and need a browser: `.venv/bin/playwright install chromium`.

Build the guide site locally:

```bash
.venv/bin/python -m guide.check --schema-only
.venv/bin/python -m guide.export_glb --out output/guide/longez.glb
.venv/bin/python -m guide.build_site --out site --models output/guide/longez.glb
python3 -m http.server -d site 8000              # then open http://localhost:8000
```

`guide.check` without `--schema-only` also runs gates that need a local source corpus built by
`scripts/fetch_sources.py`. `guide.build_site` accepts `--scan-base` (your own plans page images)
and `--renders` (Blender renders); both are optional.

Physics report and the VSPAERO leg:

```bash
.venv/bin/python scripts/generate_accuracy_report.py   # writes data/validation/accuracy_report.json
```

The vortex-lattice leg of the neutral point check needs the OpenVSP 3.48.2 Python bindings, which
are not on pip and are built for Python 3.13. `scripts/install_openvsp.sh` installs them (macOS on
Apple Silicon). Then:

```bash
python3.13 scripts/vspaero_np.py     # writes data/validation/vspaero_np.json
```

The config module is standard-library only, so the script runs under that interpreter without the
project venv. The report treats the VSPAERO result as current only if its recorded geometry
matches the live config.

## Repository map

| path | contents |
|---|---|
| `config/` | aircraft configuration and `GEOMETRY_PROVENANCE` |
| `core/` | geometry, analysis, mass ledger, source registry checks, manufacturing, compliance |
| `guide/` | build-rehearsal graph (YAML), site builder, 3D viewer |
| `data/` | airfoil coordinates, source registry, mass ledger, validation data |
| `scripts/` | accuracy report, VSPAERO neutral point, source fetcher, smoke and CI checks |
| `tests/` | Python test suite (`tests/guide/` for the guide) |
| `docs/` | Block 1 report, geometry ledger, specs and plans, retired documents in `docs/history/` |
| `output/` | generated artifacts, not tracked |

Contributions and issues are welcome. Please read [`AGENTS.md`](AGENTS.md) first: it sets out the
sourcing rules every value follows.

## License

Apache License 2.0; see [LICENSE](LICENSE). Third-party code included here, and its license, is
listed in [NOTICE](NOTICE).
