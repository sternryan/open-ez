#!/usr/bin/env bash
# Build, gate, and publish the guide to the tailnet host.
set -euo pipefail
: "${LONGEZ_DEPLOY_HOST:?set LONGEZ_DEPLOY_HOST (ssh target of the tailnet host)}"
: "${LONGEZ_SITE_URL:?set LONGEZ_SITE_URL (tailnet https URL of the site)}"
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[ -x "$PY" ] || { echo ".venv missing — run Task 0 setup" >&2; exit 1; }
SCAN_BASE=private/scan-1980/pages/
$PY -m guide.check                       # full mode; exits non-zero on any gate failure
$PY -m guide.export_glb --out output/guide/longez.glb
$PY -m guide.build_site --out site --models output/guide/longez.glb --scan-base "$SCAN_BASE"
rsync -a --delete --exclude private/ site/ "$LONGEZ_DEPLOY_HOST":/opt/long-ez-guide/site/
ssh "$LONGEZ_DEPLOY_HOST" 'ln -sfn /tank/share/long-ez/private /opt/long-ez-guide/site/private'
want=$(python3 -c 'import json;print(len(json.load(open("site/graph.json"))["ops"]))')
body=$(curl -fsS "$LONGEZ_SITE_URL/graph.json")
got=$(python3 -c 'import json,sys;print(len(json.loads(sys.stdin.read())["ops"]))' <<<"$body")
[ "$got" = "$want" ] || { echo "DEPLOY VERIFY FAILED: site serves $got ops, built $want" >&2; exit 1; }
probe=$(ssh "$LONGEZ_DEPLOY_HOST" "ls /tank/share/long-ez/$SCAN_BASE | grep -i '\.jpg\$' | head -1")
[ -n "$probe" ] || { echo "DEPLOY VERIFY FAILED: no scan jpg found on host" >&2; exit 1; }
curl -fsS -o /dev/null "$LONGEZ_SITE_URL/$SCAN_BASE$probe" || { echo "DEPLOY VERIFY FAILED: private scan not served" >&2; exit 1; }
echo "deployed and verified: $got ops at $LONGEZ_SITE_URL"
