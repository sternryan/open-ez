#!/usr/bin/env bash
# Run the open-ez suite sharded across two remote test nodes, concurrently, via scripts/remote_test.sh.
# Usage: bash scripts/remote_test_all.sh [extra pytest args, applied to both shards]
# Env:   OPEN_EZ_TEST_HOSTS   (required) "<linux-host> <mac-host>": ssh names, in that order
#        OPEN_EZ_TEST_N_LINUX (xdist workers on the Linux node, default 16)
#        OPEN_EZ_TEST_N_MAC   (xdist workers on the Mac node, default 4: it also runs always-on services)
# Shards: Linux = everything not `local_render`, minus tests/guide/test_lab_e2e.py (software-GL browser).
#         Mac   = tests/guide/test_lab_e2e.py, then every `local_render` test (Mac rendering matches the
#                 laptop, so pixel/frame tests mean something there). If the `local_render` marker isn't
#                 registered in the repo yet, the second Mac pass is skipped with a note.
# Exits non-zero if any shard failed. Per-host logs: $LOGDIR (default: a mktemp dir, printed at the end).
set -uo pipefail
read -r LINUX MAC _ <<<"${OPEN_EZ_TEST_HOSTS:?set OPEN_EZ_TEST_HOSTS to \"<linux-host> <mac-host>\"}"
: "${MAC:?OPEN_EZ_TEST_HOSTS needs two hosts: <linux-host> <mac-host>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RT="$ROOT/scripts/remote_test.sh"
LOGDIR="${LOGDIR:-$(mktemp -d)}"
T0=$(date +%s)

MARKER_REGISTERED=0
for f in pyproject.toml pytest.ini setup.cfg tox.ini conftest.py tests/conftest.py; do
  [ -f "$ROOT/$f" ] && grep -q local_render "$ROOT/$f" && MARKER_REGISTERED=1
done

# remote_test.sh forwards args through ssh unquoted, so the multi-word -m expression carries its own quotes.
linux_shard() {
  OPEN_EZ_TEST_HOST="$LINUX" OPEN_EZ_TEST_N="${OPEN_EZ_TEST_N_LINUX:-16}" \
    bash "$RT" -m "'not local_render'" --ignore=tests/guide/test_lab_e2e.py "$@"
}

mac_shard() {
  export OPEN_EZ_TEST_HOST="$MAC" OPEN_EZ_TEST_N="${OPEN_EZ_TEST_N_MAC:-4}"
  local rc=0
  bash "$RT" tests/guide/test_lab_e2e.py "$@" || rc=$?
  if [ "$MARKER_REGISTERED" = 1 ]; then
    bash "$RT" -m local_render --deselect tests/guide/test_lab_e2e.py "$@"
    local rc2=$?
    [ "$rc2" = 5 ] && rc2=0   # no local_render tests collected
    [ "$rc" = 0 ] && rc=$rc2
  else
    echo "note: local_render marker not registered yet; Mac ran only tests/guide/test_lab_e2e.py"
  fi
  return "$rc"
}

linux_shard "$@" >"$LOGDIR/linux.log" 2>&1 & PL=$!
mac_shard "$@" >"$LOGDIR/mac.log" 2>&1 & PM=$!
wait "$PL"; RL=$?
wait "$PM"; RM=$?

for role in linux mac; do
  echo "== $role (exit $([ $role = linux ] && echo $RL || echo $RM))"
  # pytest summary line(s) + remote_test footer; host names are stripped from the footer
  grep -E '^=*.*(passed|failed|error|no tests ran).* in [0-9.]+s|^(FAILED|ERROR) |^note:' "$LOGDIR/$role.log" | sed 's/, host .*//'
  grep '^--- remote_test' "$LOGDIR/$role.log" | sed 's/, host .*//'
done
echo "--- remote_test_all: linux=$RL mac=$RM, wall $(( $(date +%s) - T0 ))s, logs $LOGDIR"
[ "$RL" = 0 ] && [ "$RM" = 0 ]
