"""Real-data check of viewer build state: guide/viewer/js/build.js on the real graph + export."""
import json
import subprocess
from pathlib import Path

import pytest

from guide.build_site import build
from guide.export_glb import main as export_main, read_glb_node_names

ROOT = Path(__file__).resolve().parents[2]
BUILD_JS = (ROOT / "guide" / "viewer" / "js" / "build.js").as_uri()

JS = """
import { readFileSync } from "node:fs";
import { visibleOps } from "%(graph_js)s";
import { visibleSet } from "%(build_js)s";
const g = JSON.parse(readFileSync(process.argv[2], "utf8"));
const meshes = JSON.parse(readFileSync(process.argv[3], "utf8"));
const out = {};
for (const v of ["roncz", "gu"]) {
  out[v] = {};
  for (const o of visibleOps(g, v)) {
    out[v][o.id] = Object.fromEntries(visibleSet(g, v, o.id, Infinity, meshes));
  }
}
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def real(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("build_state")
    export_main(["--out", str(tmp / "longez.glb")])
    layup = json.loads((tmp / "layup.json").read_text())["nodes"]
    site = tmp / "site"
    build(ROOT / "guide" / "graph", site, tmp / "longez.glb", None, None)
    graph = json.loads((site / "graph.json").read_text())
    names = read_glb_node_names(tmp / "longez.glb")
    meshes = [{"name": n, "component": p["component"], "ply": {"op": p["op"], "order": p["order"]}}
              for n, p in layup.items()]
    # A glb node is a component mesh only if it is a graph component and holds no ply children;
    # group nodes (canard.shear_web, ...) and the scene root (longez) are not meshes.
    # The fuselage box, gear, nose (chapters 4-9, 13) and the elevators (chapter 11) share the glb; this viewer skips their nodes
    # (guide/viewer/js/app.js), so this does too.
    for n in names:
        if n.startswith(("fuselage.", "gear.", "nose.", "elevator.")):
            continue
        if n in graph["components"] and n not in layup and not any(k.startswith(n + ".") for k in layup):
            meshes.append({"name": n, "component": n, "ply": None})
    (tmp / "meshes.json").write_text(json.dumps(meshes))
    js = tmp / "run.mjs"
    js.write_text(JS % {"build_js": BUILD_JS, "graph_js": (ROOT / "guide" / "viewer" / "js" / "graph.js").as_uri()})
    r = subprocess.run(["node", str(js), str(site / "graph.json"), str(tmp / "meshes.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return {"states": json.loads(r.stdout), "layup": layup, "meshes": meshes, "graph": graph}


def test_component_meshes_are_the_leaf_components(real):
    comp = [m["name"] for m in real["meshes"] if m["ply"] is None]
    assert comp == ["canard.core"]


def test_roncz_current_counts_match_ply_counts(real):
    plies = {}
    for p in real["layup"].values():
        plies[p["op"]] = plies.get(p["op"], 0) + 1
    first = {}
    for o in real["graph"]["ops"]:
        if o["variants"] and ("both" in o["variants"] or "roncz" in o["variants"]):
            for c in o["components"]:
                first.setdefault(c, o["id"])
    core_ops = {first[m["component"]] for m in real["meshes"] if m["ply"] is None}
    assert core_ops == {"r30.templates-cores"}
    seen = 0
    for op, st in real["states"]["roncz"].items():
        cur = sum(1 for s in st.values() if s == "current")
        want = plies.get(op, 1 if op in core_ops else 0)
        assert cur == want, (op, cur, want)
        seen += 1
    assert seen > 0 and set(plies) <= set(real["states"]["roncz"])


def test_gu_hides_every_roncz_ply(real):
    ply_names = {m["name"] for m in real["meshes"] if m["ply"]}
    assert real["states"]["gu"]
    for op, st in real["states"]["gu"].items():
        assert {st[n] for n in ply_names} == {"hidden"}, op


def test_roncz_states_are_monotonic_over_the_build(real):
    ops = list(real["states"]["roncz"])
    assert ops == [o["id"] for o in real["graph"]["ops"] if o["id"] in real["states"]["roncz"]]
    for m in real["meshes"]:
        seq = [real["states"]["roncz"][op][m["name"]] for op in ops]
        assert seq.count("current") == 1, (m["name"], seq)
        i = seq.index("current")
        assert set(seq[:i]) <= {"hidden"}, (m["name"], seq)
        assert set(seq[i + 1:]) == {"built"} or i == len(seq) - 1, (m["name"], seq)
