#!/usr/bin/env bash
# Build the public-safe lab and publish it as the sole content of the gh-pages branch of origin.
# Only gh-pages is ever force-pushed; main is never touched. Optional: LAB_FILM=/path/to/film.mp4 (<= 50 MB) ships as film.mp4.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python}"
REMOTE="$(git remote get-url origin)"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
SITE="$WORK/site"

"$PY" -m guide.export_glb --out "$WORK/export/longez.glb"
# Our own Blender stills, keyed to this export exactly as deploy_guide.sh does. Missing cache = loud failure, not a silent omission.
CF="${COMPUTE_FABRIC_DIR:-$HOME/compute-fabric-dev}"
KEY="$("$PY" -m guide.render_key --export "$WORK/export/canard" --scripts "$CF/deploy/anvil/jobs/blender")"
RENDERS="${LONGEZ_RENDER_CACHE:-$HOME/.cache/long-ez/renders}/$KEY"
[ -f "$RENDERS/manifest.json" ] || { echo "no renders for key $KEY; run guide/render_cutaway.sh first" >&2; exit 1; }
"$PY" -m guide.build_site --public --out "$SITE" --models "$WORK/export/longez.glb" --renders "$RENDERS"

if [ -n "${LAB_FILM:-}" ]; then
  [ -f "$LAB_FILM" ] || { echo "LAB_FILM not found: $LAB_FILM" >&2; exit 1; }
  size=$(wc -c < "$LAB_FILM")
  [ "$size" -le 52428800 ] || { echo "LAB_FILM is over 50 MB ($size bytes)" >&2; exit 1; }
  cp "$LAB_FILM" "$SITE/film.mp4"
fi
touch "$SITE/.nojekyll"

# Fail loudly on any leak, before anything leaves this machine.
"$PY" -m guide.leakcheck "$SITE"

# Orphan commit in a scratch repo, so the working tree and main are never involved.
git -C "$SITE" init -q -b gh-pages
git -C "$SITE" add -A
git -C "$SITE" -c user.name="open-ez publish" -c user.email="noreply@users.noreply.github.com" commit -q -m "Publish public lab build"
git -C "$SITE" push -f "$REMOTE" gh-pages:gh-pages
echo "pushed gh-pages"
