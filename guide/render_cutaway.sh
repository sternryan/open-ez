#!/usr/bin/env bash
# Render the layup cutaway on a remote GPU host through a GPU-job runner. HITL only; never put this on a timer.
# Required environment (site-specific, deliberately not in the repo):
#   OPENEZ_RENDER_HOST         ssh name of the remote GPU host
#   OPENEZ_BLENDER_SCRIPTS     local dir holding layup_cutaway.py, fabric_blender.py, layup_contract.py
#   OPENEZ_GPU_RUNNER          local command that dispatches a Blender job on the host
#   OPENEZ_LEASE_CHECK_CMD     command run on the host; exit 0 = GPU free, non-zero = lease held (prints holder| fields)
#   OPENEZ_RENDER_DEPLOYED_DIR dir on the host where the Blender scripts are installed
#   OPENEZ_RENDER_JOB_ROOT     dir on the host under which job dirs are created
# usage: guide/render_cutaway.sh [--only SHOT_ID] [--wait[=SECONDS]] [--dry-run]
#   --wait  queue behind a busy GPU lease via the runner (default 14400 s) instead of refusing
# exit: 0 ok · 2 usage/missing inputs · 3 GPU lease busy · 4 deployed scripts differ · 5 render check failed
set -euo pipefail
ONLY=""; DRY=""; WAIT_S=""
while [ $# -gt 0 ]; do
  case "$1" in
    --only) ONLY="${2:?--only needs a shot id}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --wait) WAIT_S=14400; shift ;;
    --wait=*) WAIT_S="${1#--wait=}"; [[ "$WAIT_S" =~ ^[0-9]+$ ]] || { echo "--wait=SECONDS needs a number" >&2; exit 2; }; shift ;;
    *) echo "usage: render_cutaway.sh [--only SHOT_ID] [--wait[=SECONDS]] [--dry-run]" >&2; exit 2 ;;
  esac
done
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
RENDER_HOST=${OPENEZ_RENDER_HOST:?set OPENEZ_RENDER_HOST (ssh name of the remote GPU host)}
SCRIPTS=${OPENEZ_BLENDER_SCRIPTS:?set OPENEZ_BLENDER_SCRIPTS (local dir with the Blender job scripts)}
FABRIC_GPU=${OPENEZ_GPU_RUNNER:?set OPENEZ_GPU_RUNNER (local command that dispatches the GPU job)}
LEASE_CMD=${OPENEZ_LEASE_CHECK_CMD:?set OPENEZ_LEASE_CHECK_CMD (remote command; non-zero = GPU lease held)}
# The canard-only cutaway inputs guide.export_glb writes beside longez.glb (the site glb also holds the fuselage).
EXPORT=${LONGEZ_EXPORT_DIR:-output/guide/canard}
CACHE=${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}
POLL_S=${LONGEZ_POLL_S:-10}
DEPLOYED=${OPENEZ_RENDER_DEPLOYED_DIR:?set OPENEZ_RENDER_DEPLOYED_DIR (host dir with the installed scripts)}
JOB_ROOT=${OPENEZ_RENDER_JOB_ROOT:?set OPENEZ_RENDER_JOB_ROOT (host dir for job dirs)}

for f in longez.glb layup.json shots.json; do
  [ -f "$EXPORT/$f" ] || { echo "missing $EXPORT/$f; run: $PY -m guide.export_glb" >&2; exit 2; }
done
STAGE=$(mktemp -d); trap 'rm -rf "$STAGE"' EXIT
cp "$EXPORT/longez.glb" "$EXPORT/layup.json" "$STAGE/"
if [ -n "$ONLY" ]; then
  $PY - "$EXPORT/shots.json" "$ONLY" "$STAGE/shots.json" <<'EOF' || exit 2
import json, sys
s = [x for x in json.load(open(sys.argv[1])) if x["id"] == sys.argv[2]]
if not s:
    sys.exit(f"no such shot: {sys.argv[2]}")
json.dump(s, open(sys.argv[3], "w"), indent=1)
EOF
else
  cp "$EXPORT/shots.json" "$STAGE/"
fi
KEY=$($PY -m guide.render_key --export "$STAGE" --scripts "$SCRIPTS")

for s in layup_cutaway.py fabric_blender.py layup_contract.py; do
  want=$(shasum -a 256 "$SCRIPTS/$s" | cut -d' ' -f1)
  got=$(ssh "$RENDER_HOST" "sha256sum $DEPLOYED/$s" | cut -d' ' -f1)
  [ "$want" = "$got" ] || { echo "deployed $s differs from $SCRIPTS/$s; redeploy to the render host first" >&2; exit 4; }
done
# Lease: report who holds it, for how long, and the ETA the holder stamped (if any), so the caller
# can decide: wait (--wait), or ask Ryan to pause the holder. A render has no frontier/CPU substitute.
if ! status=$(ssh "$RENDER_HOST" "$LEASE_CMD"); then
  field() { sed -n "s/^ *holder| $1=//p" <<<"$status" | head -1; }
  holder=$(field runner); started=$(field started); eta=$(field eta)
  held=$($PY -c 'import sys,datetime as d; s=sys.argv[1]
try: print(int((d.datetime.now(d.timezone.utc)-d.datetime.fromisoformat(s.replace("Z","+00:00"))).total_seconds()//60),"min")
except Exception: print("unknown time")' "$started")
  echo "GPU lease held by ${holder:-unknown} since ${started:-unknown} (${held}); ETA: ${eta:-none stamped by the holder}" >&2
  if [ -z "$WAIT_S" ]; then
    echo "re-run with --wait[=SECONDS] to queue behind it, or ask Ryan whether to pause the holder" >&2; exit 3
  fi
  echo "queuing behind ${holder:-the holder} for up to ${WAIT_S}s" >&2
fi

JOB=$JOB_ROOT/layup-${KEY:0:16}
if [ -n "$DRY" ]; then echo "dry run: would render key $KEY into $JOB"; exit 0; fi
N=$($PY -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$STAGE/shots.json")
EXPECT=$((60 + 45 * N))
ssh "$RENDER_HOST" "rm -rf $JOB && mkdir -p $JOB/in"
rsync -a "$STAGE/" "$RENDER_HOST:$JOB/in/"
if [ -n "$WAIT_S" ]; then LEASE_FLAGS=(--wait-s "$WAIT_S"); else LEASE_FLAGS=(--no-wait); fi
set +e; "$FABRIC_GPU" run blender.sh layup_cutaway "$JOB" "${LEASE_FLAGS[@]}" --expect-s "$EXPECT"; rc=$?; set -e
[ "$rc" = 0 ] || { echo "GPU runner failed rc=$rc (payload log: ssh $RENDER_HOST cat $JOB/out/log.txt)" >&2; exit "$rc"; }

waited=0
until ssh "$RENDER_HOST" "test -f $JOB/out/manifest.json"; do
  if ssh "$RENDER_HOST" "grep -q LAYUP_CUTAWAY_FAILED $JOB/out/log.txt 2>/dev/null"; then
    echo "render job failed on the render host:" >&2; ssh "$RENDER_HOST" "tail -20 $JOB/out/log.txt" >&2; exit 5
  fi
  [ "$waited" -ge $((EXPECT + 300)) ] && { echo "no manifest after ${waited}s; see ssh $RENDER_HOST cat $JOB/out/log.txt" >&2; exit 5; }
  sleep "$POLL_S"; waited=$((waited + POLL_S)); [ "$POLL_S" = 0 ] && waited=$((waited + 1))
done

DEST="$CACHE/$KEY"; TMP="$DEST.tmp"
rm -rf "$TMP"; mkdir -p "$TMP"
rsync -a "$RENDER_HOST:$JOB/out/" "$TMP/"
if ! $PY -m guide.render_key --export "$STAGE" --scripts "$SCRIPTS" --check "$TMP"; then
  rm -rf "$TMP"; echo "render check failed for key $KEY" >&2; exit 5
fi
rm -rf "$DEST"; mv "$TMP" "$DEST"
echo "renders: $DEST"
