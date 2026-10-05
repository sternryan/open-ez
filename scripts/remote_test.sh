#!/usr/bin/env bash
# Run the open-ez test suite on a remote CPU node.
# Usage: bash scripts/remote_test.sh [pytest args]      e.g. -k lab, tests/guide
#        Adds -m "not local_render" unless the args carry their own -m (local_render tests are judged on the laptop).
# Env:   OPEN_EZ_TEST_HOST (required: ssh name of the node), OPEN_EZ_TEST_N (xdist workers, default 16),
#        OPENEZ_REQUIRE_VSPAERO / VSP_RUNNER (forwarded to the remote pytest: the VSPAERO leg fails instead of skipping),
#        OPEN_EZ_TEST_TIMEOUT (wall cap for the remote run in seconds, default 1500; needs `timeout` on PATH)
# Remote layout: ~/open-ez-test (tree), ~/open-ez-test-venv (python 3.12 + deps + playwright chromium).
# Tests build their own GLB (guide.export_glb) into tmp dirs, so output/ is not synced.
# Fast loop (skips software-GL browser tests, ~20s): bash scripts/remote_test.sh --ignore=tests/guide/test_lab_e2e.py --ignore=tests/guide/test_viewer_e2e.py
set -uo pipefail
HOST="${OPEN_EZ_TEST_HOST:?set OPEN_EZ_TEST_HOST to the ssh name of the test node}"
N="${OPEN_EZ_TEST_N:-16}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T0=$(date +%s)
# A stalled node must fail loudly within about a minute, not hang the run: bounded connect, keepalives that give up.
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
# Keepalives catch a dead link, not a remote run that is alive but stuck: cap the whole remote run too (OPEN_EZ_TEST_TIMEOUT, s).
CAP=()
command -v timeout >/dev/null && CAP=(timeout "${OPEN_EZ_TEST_TIMEOUT:-1500}")

rsync -a --delete -e "ssh ${SSH_OPTS[*]}" \
  --exclude .venv --exclude node_modules --exclude .git --exclude output/ \
  --exclude site/ --exclude private/ --exclude .claude/ \
  --exclude __pycache__ --exclude .pytest_cache --exclude .mypy_cache --exclude .ruff_cache \
  --exclude guide/lab/dist/ \
  "$ROOT"/ "$HOST":open-ez-test/ || { echo "rsync failed" >&2; exit 2; }

# Prime the lab build once, serially: build_site.build_lab() runs `npm ci` / `vite build` on its own
# input-digest stamps, and 16 xdist workers doing that concurrently corrupt node_modules.
# Default: deselect the laptop-only render tests, unless the caller chose its own -m expression.
ARGS=("$@")
has_m=0
for a in "${ARGS[@]+"${ARGS[@]}"}"; do case "$a" in -m|-m*) has_m=1 ;; esac; done
[ "$has_m" = 1 ] || ARGS=(-m "not local_render" "${ARGS[@]+"${ARGS[@]}"}")
# ssh joins its arguments into one remote command line, so quote every argument (a multi-word -m must stay one word).
# The REMOTE heredoc is quoted, so local env does not cross ssh: OPENEZ_REQUIRE_VSPAERO and VSP_RUNNER ride as positional args (after N).
REMOTE_ARGS=$(printf '%q ' "$N" "${OPENEZ_REQUIRE_VSPAERO:-}" "${VSP_RUNNER:-}" "${ARGS[@]}")
"${CAP[@]+"${CAP[@]}"}" ssh "${SSH_OPTS[@]}" "$HOST" "bash -s -- $REMOTE_ARGS" <<'REMOTE'
set -uo pipefail
N="$1"; shift
export OPENEZ_REQUIRE_VSPAERO="$1"; shift
export VSP_RUNNER="$1"; shift
[ -n "$OPENEZ_REQUIRE_VSPAERO" ] || unset OPENEZ_REQUIRE_VSPAERO
[ -n "$VSP_RUNNER" ] || unset VSP_RUNNER
cd ~/open-ez-test
V=~/open-ez-test-venv/bin
sum() { cat requirements*.txt | sha256sum | cut -c1-16; }
[ "$(cat .req-stamp 2>/dev/null)" = "$(sum)" ] || { $V/pip install -q -r requirements-dev.txt -r requirements-guide-dev.txt pytest-xdist && sum > .req-stamp; }
ln -sfn ~/open-ez-test-venv .venv   # render_cutaway.sh hardcodes <repo>/.venv/bin/python
$V/python -c "from guide.build_site import build_lab; build_lab()" || { echo "lab prime failed"; exit 2; }
exec $V/python -m pytest -q -p no:cacheprovider -n "$N" "$@"
REMOTE
RC=$?
[ "$RC" = 124 ] && echo "remote_test: the remote run passed its ${OPEN_EZ_TEST_TIMEOUT:-1500}s cap and was stopped" >&2
echo "--- remote_test: exit $RC, wall $(( $(date +%s) - T0 ))s, host $HOST"
exit "$RC"
