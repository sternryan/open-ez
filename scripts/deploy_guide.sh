#!/usr/bin/env bash
# Build, gate, and publish the guide to a private host.
# Required environment: LONGEZ_DEPLOY_HOST, LONGEZ_SITE_URL, LONGEZ_DEPLOY_ROOT, LONGEZ_PRIVATE_DIR, OPENEZ_BLENDER_SCRIPTS.
set -euo pipefail
: "${LONGEZ_DEPLOY_HOST:?set LONGEZ_DEPLOY_HOST (ssh target of the private host)}"
: "${LONGEZ_SITE_URL:?set LONGEZ_SITE_URL (https URL of the site)}"
: "${LONGEZ_DEPLOY_ROOT:?set LONGEZ_DEPLOY_ROOT (site dir parent on the host)}"
: "${LONGEZ_PRIVATE_DIR:?set LONGEZ_PRIVATE_DIR (host dir holding private/)}"
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[ -x "$PY" ] || { echo ".venv missing — run Task 0 setup" >&2; exit 1; }
SCAN_BASE=private/scan-1980/pages/
$PY -m guide.check                       # full mode; exits non-zero on any gate failure
$PY -m guide.export_glb --out output/guide/longez.glb
SCRIPTS=${OPENEZ_BLENDER_SCRIPTS:?set OPENEZ_BLENDER_SCRIPTS (local dir with the Blender job scripts)}
KEY=$($PY -m guide.render_key --export output/guide/canard --scripts "$SCRIPTS")
RENDERS="${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}/$KEY"
[ -f "$RENDERS/manifest.json" ] || { echo "no renders for key $KEY; run guide/render_cutaway.sh first" >&2; exit 1; }
$PY -m guide.build_site --out site --models output/guide/longez.glb --scan-base "$SCAN_BASE" --renders "$RENDERS"
rsync -a --delete --exclude private/ site/ "$LONGEZ_DEPLOY_HOST":"$LONGEZ_DEPLOY_ROOT"/site/
ssh "$LONGEZ_DEPLOY_HOST" "ln -sfn $LONGEZ_PRIVATE_DIR/private $LONGEZ_DEPLOY_ROOT/site/private"
want=$(python3 -c 'import json;print(len(json.load(open("site/graph.json"))["ops"]))')
body=$(curl -fsS "$LONGEZ_SITE_URL/graph.json")
got=$(python3 -c 'import json,sys;print(len(json.loads(sys.stdin.read())["ops"]))' <<<"$body")
[ "$got" = "$want" ] || { echo "DEPLOY VERIFY FAILED: site serves $got ops, built $want" >&2; exit 1; }
probe=$(ssh "$LONGEZ_DEPLOY_HOST" "ls $LONGEZ_PRIVATE_DIR/$SCAN_BASE | grep -i '\.jpg\$' | head -1")
[ -n "$probe" ] || { echo "DEPLOY VERIFY FAILED: no scan jpg found on host" >&2; exit 1; }
curl -fsS -o /dev/null "$LONGEZ_SITE_URL/$SCAN_BASE$probe" || { echo "DEPLOY VERIFY FAILED: private scan not served" >&2; exit 1; }
curl -fsS -o /dev/null "$LONGEZ_SITE_URL/renders/hero-bl5.png" || { echo "DEPLOY VERIFY FAILED: hero render not served" >&2; exit 1; }
echo "deployed and verified: $got ops at $LONGEZ_SITE_URL"
