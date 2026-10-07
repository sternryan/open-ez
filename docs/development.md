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

## Optional remote tooling and environment variables

Some scripts need a remote host (a GPU box, a private web host, or a test node). They read their
settings from environment variables and stop with a message naming the missing one. Nothing
site-specific is stored in the repo. You can keep the values in a local env file outside the
repository and load it with `set -a; . /path/to/your.env; set +a`.

| variable | needed by | what it is |
|---|---|---|
| `OPENEZ_RENDER_HOST` | `guide/render_cutaway.sh` | ssh name of the remote GPU host that runs Blender |
| `OPENEZ_BLENDER_SCRIPTS` | `guide/render_cutaway.sh`, `scripts/publish_public.sh`, `scripts/deploy_guide.sh` | local directory holding the Blender job scripts |
| `OPENEZ_GPU_RUNNER` | `guide/render_cutaway.sh` | local command that dispatches the GPU job |
| `OPENEZ_LEASE_CHECK_CMD` | `guide/render_cutaway.sh` | command run on the host; non-zero exit means the GPU is in use |
| `OPENEZ_RENDER_DEPLOYED_DIR` | `guide/render_cutaway.sh` | directory on the host where the Blender scripts are installed |
| `OPENEZ_RENDER_JOB_ROOT` | `guide/render_cutaway.sh` | directory on the host where job folders are created |
| `LONGEZ_RENDER_CACHE` | render, publish and deploy scripts (optional) | local render cache; default `~/.cache/long-ez/renders` |
| `LONGEZ_EXPORT_DIR`, `LONGEZ_POLL_S` | `guide/render_cutaway.sh` (optional) | export folder and poll interval overrides |
| `LONGEZ_DEPLOY_HOST` | `scripts/deploy_guide.sh` | ssh name of the private web host |
| `LONGEZ_SITE_URL` | `scripts/deploy_guide.sh` | URL the deployed site is served from |
| `LONGEZ_DEPLOY_ROOT` | `scripts/deploy_guide.sh` | directory on the web host that holds `site/` |
| `LONGEZ_PRIVATE_DIR` | `scripts/deploy_guide.sh` | directory on the web host that holds private page scans |
| `OPEN_EZ_TEST_HOST` | `scripts/remote_test.sh` | ssh name of a remote node to run the test suite on |
| `OPEN_EZ_TEST_N`, `OPEN_EZ_TEST_TIMEOUT` | `scripts/remote_test.sh` (optional) | parallel workers, and a wall-clock cap in seconds |
| `OPEN_EZ_TEST_HOSTS` | `scripts/remote_test_all.sh` | two ssh names, `"<linux-host> <mac-host>"` |
| `OPEN_EZ_TEST_N_LINUX`, `OPEN_EZ_TEST_N_MAC` | `scripts/remote_test_all.sh` (optional) | parallel workers per node |
| `VSP_RUNNER` | `tests/test_vspaero_leg.py`, `scripts/remote_test.sh` (optional) | script that runs the VSPAERO job on a remote runner; without it the test uses local OpenVSP or skips |
| `VSP_JOB_ROOT` | `tests/test_vspaero_leg.py` (optional) | job directory used with `VSP_RUNNER`; default `/tmp/vsp-jobs` |
| `OPENEZ_REQUIRE_VSPAERO` | `tests/test_vspaero_leg.py` (optional) | set to `1` to fail, not skip, when OpenVSP is absent |
| `LONGEZ_SOURCE_CACHE`, `LONGEZ_COBELU_DIR`, `LONGEZ_CP_SECTIONS` | `scripts/fetch_sources.py` | where your own copies of the source documents live and are cached |
| `LONGEZ_SCAN_PAGES`, `LONGEZ_SCAN_TEXT_DIR` | `scripts/vision_bakeoff.py`, `guide/sources.py` (optional) | your own plans page images and text, kept outside the repo |

`scripts/publish_public.sh` force-pushes the built site to the `gh-pages` branch only; it never touches `main`.

## About `main.py`

`main.py` is an early command-line entry point. Its flags have not been re-checked against the current
model, so this repository does not document them. Use the commands above.
