# Development setup

Everything here is for people who want to run or change the code. If you only want to look at the
airplane model, use the published site linked from the [README](../README.md).

Read [`AGENTS.md`](../AGENTS.md) first. It sets out the sourcing rules every value follows, and what
may not be committed to this public repository.

## What you need

| tool | used for |
|---|---|
| Python 3.11 or newer | the model, the physics checks, the site builder |
| Node 20 or newer, with npm | the 3D lab in `guide/lab` (built with Vite and TypeScript) |
| A browser driver (Playwright, optional) | the guide's end-to-end tests |
| OpenVSP 3.53.1 Python bindings under Python 3.13 (optional) | the second neutral point method (see below) |

The lab is a separate JavaScript project. `guide.build_site` runs `npm ci` and `npm run build` in
`guide/lab` for you, and stops with a clear error if Node and npm are not on your path.

## Install

```bash
git clone https://github.com/sternryan/open-ez.git
cd open-ez
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt -r requirements-guide-dev.txt
```

## Run the tests

```bash
.venv/bin/python -m pytest -q                    # Python suite; writes only to temporary dirs
node --test guide/viewer/tests/*.test.mjs        # viewer unit tests
npm --prefix guide/lab ci                        # once, to install the lab's packages
npm --prefix guide/lab run typecheck             # lab type check
npm --prefix guide/lab test                      # lab unit tests
.venv/bin/playwright install chromium            # once, for the end-to-end tests
```

Some tests are expected to fail on purpose (strict `xfail`). They mark places where the model
disagrees with the book, and each one points at a row in
[`geometry-correction-ledger.md`](geometry-correction-ledger.md). Do not widen a bound to make one
pass. If a test starts passing, the strict marker makes the suite fail until you update the ledger.

`pre-commit run --all-files` runs the linter, formatter, type check and a smoke test.

## Build the site locally

```bash
.venv/bin/python -m guide.check --schema-only
.venv/bin/python -m guide.export_glb --out output/guide/longez.glb
.venv/bin/python -m guide.build_site --out site --models output/guide/longez.glb
python3 -m http.server -d site 8000              # then open http://localhost:8000
```

`guide.check` without `--schema-only` also runs gates that need a local copy of the source documents,
built by `scripts/fetch_sources.py` (not committed). `guide.build_site` accepts `--scan-base`
(your own page images of the plans) and `--renders` (Blender renders); both are optional. The lab
reads its data (`graph.json` and friends) from the built site, so build the site first rather than
starting the Vite dev server on its own.

## Physics report and the second neutral point method

```bash
.venv/bin/python scripts/generate_accuracy_report.py   # writes data/validation/accuracy_report.json
```

The vortex-lattice leg of the neutral point check needs the OpenVSP Python bindings, which are not on
pip and are built for Python 3.13. `scripts/install_openvsp.sh` installs them (macOS on Apple
Silicon). Then:

```bash
python3.13 scripts/vspaero_np.py     # writes data/validation/vspaero_np.json
```

The report treats the VSPAERO result as current only if its recorded geometry matches the live
configuration.

## Optional remote tooling

Three scripts need a remote GPU host or a private web host. They read their settings from environment
variables and stop with a message naming the missing one. Nothing site-specific is stored in the repo.

| script | what it does | variables |
|---|---|---|
| `guide/render_cutaway.sh` | Blender cutaway renders on a remote GPU host | `OPENEZ_RENDER_HOST` and the `OPENEZ_*` variables listed at the top of the script |
| `scripts/publish_public.sh` | builds the public site and force-pushes it to `gh-pages` only | `OPENEZ_BLENDER_SCRIPTS` |
| `scripts/deploy_guide.sh` | publishes the full guide, with private scans, to a private host | `LONGEZ_DEPLOY_HOST`, `LONGEZ_SITE_URL`, `LONGEZ_DEPLOY_ROOT`, `LONGEZ_PRIVATE_DIR`, `OPENEZ_BLENDER_SCRIPTS` |

Tests for the VSPAERO leg can use a remote runner by setting `VSP_RUNNER`; without it they use a local
OpenVSP install or skip.

## About `main.py`

`main.py` is an early command-line entry point. Its flags have not been re-checked against the current
model, so this repository does not document them. Use the commands above.
