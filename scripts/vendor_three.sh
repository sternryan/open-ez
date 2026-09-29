#!/usr/bin/env bash
set -euo pipefail
V="${1:-$(npm view three version)}"
D="$(cd "$(dirname "$0")/.." && pwd)/guide/viewer/vendor/three"
rm -rf "$D"; mkdir -p "$D/build" "$D/examples/jsm/controls" "$D/examples/jsm/loaders" "$D/examples/jsm/utils"
base="https://unpkg.com/three@$V"
for f in build/three.module.js build/three.core.js examples/jsm/controls/OrbitControls.js \
         examples/jsm/loaders/GLTFLoader.js examples/jsm/utils/BufferGeometryUtils.js examples/jsm/utils/SkeletonUtils.js LICENSE; do
  curl -fsSL "$base/$f" -o "$D/$f" || { echo "failed: $f" >&2; exit 1; }
done
printf 'three %s vendored %s from unpkg\n' "$V" "$(date +%F)" > "$D/VERSION"
echo "vendored three $V"
