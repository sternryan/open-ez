#!/usr/bin/env bash
# Render the layup cutaway on anvil's GPU through fabric-gpu. HITL only; never put this on a timer.
# usage: guide/render_cutaway.sh [--only SHOT_ID] [--wait[=SECONDS]] [--dry-run]
#   --wait  queue behind a busy GPU lease via fabric-gpu (default 14400 s) instead of refusing
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
ANVIL=${LONGEZ_ANVIL:-anvil}
CF=${COMPUTE_FABRIC_DIR:-$HOME/compute-fabric-dev}
FABRIC_GPU=${FABRIC_GPU:-$CF/bin/fabric-gpu}
SCRIPTS=$CF/deploy/anvil/jobs/blender
# The canard-only cutaway inputs guide.export_glb writes beside longez.glb (the site glb also holds the fuselage).
EXPORT=${LONGEZ_EXPORT_DIR:-output/guide/canard}
CACHE=${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}
POLL_S=${LONGEZ_POLL_S:-10}
DEPLOYED=/opt/fabric/jobs/blender

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
  got=$(ssh "$ANVIL" "sha256sum $DEPLOYED/$s" | cut -d' ' -f1)
  [ "$want" = "$got" ] || { echo "deployed $s differs from $SCRIPTS/$s; redeploy to anvil first" >&2; exit 4; }
done
# Lease: report who holds it, for how long, and the ETA the holder stamped (if any), so the caller
# can decide: wait (--wait), or ask Ryan to pause the holder. A render has no frontier/CPU substitute.
if ! status=$(ssh "$ANVIL" flux-lock-status); then
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

JOB=/srv/gpu-jobs/blender/layup-${KEY:0:16}
if [ -n "$DRY" ]; then echo "dry run: would render key $KEY into $JOB"; exit 0; fi
N=$($PY -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$STAGE/shots.json")
EXPECT=$((60 + 45 * N))
ssh "$ANVIL" "rm -rf $JOB && mkdir -p $JOB/in"
rsync -a "$STAGE/" "$ANVIL:$JOB/in/"
if [ -n "$WAIT_S" ]; then LEASE_FLAGS=(--wait-s "$WAIT_S"); else LEASE_FLAGS=(--no-wait); fi
set +e; "$FABRIC_GPU" run blender.sh layup_cutaway "$JOB" "${LEASE_FLAGS[@]}" --expect-s "$EXPECT"; rc=$?; set -e
[ "$rc" = 0 ] || { echo "fabric-gpu run failed rc=$rc (payload log: ssh $ANVIL cat $JOB/out/log.txt)" >&2; exit "$rc"; }

waited=0
until ssh "$ANVIL" "test -f $JOB/out/manifest.json"; do
  if ssh "$ANVIL" "grep -q LAYUP_CUTAWAY_FAILED $JOB/out/log.txt 2>/dev/null"; then
    echo "render job failed on anvil:" >&2; ssh "$ANVIL" "tail -20 $JOB/out/log.txt" >&2; exit 5
  fi
  [ "$waited" -ge $((EXPECT + 300)) ] && { echo "no manifest after ${waited}s; see ssh $ANVIL cat $JOB/out/log.txt" >&2; exit 5; }
  sleep "$POLL_S"; waited=$((waited + POLL_S)); [ "$POLL_S" = 0 ] && waited=$((waited + 1))
done

DEST="$CACHE/$KEY"; TMP="$DEST.tmp"
rm -rf "$TMP"; mkdir -p "$TMP"
rsync -a "$ANVIL:$JOB/out/" "$TMP/"
if ! $PY -m guide.render_key --export "$STAGE" --scripts "$SCRIPTS" --check "$TMP"; then
  rm -rf "$TMP"; echo "render check failed for key $KEY" >&2; exit 5
fi
rm -rf "$DEST"; mv "$TMP" "$DEST"
echo "renders: $DEST"
