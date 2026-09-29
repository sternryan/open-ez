"""Test glb export with component-ID node names."""
import cadquery as cq
from guide.export_glb import export_components, read_glb_node_names


def test_node_names_are_component_ids(tmp_path):
    out = export_components(
        {
            "canard.core": cq.Workplane().box(10, 2, 1),
            "canard.spar_cap_top": cq.Workplane().box(10, 1, 0.1),
        },
        tmp_path / "t.glb",
    )
    names = read_glb_node_names(out)
    assert "canard.core" in names and "canard.spar_cap_top" in names
    assert out.read_bytes()[:4] == b"glTF"


import hashlib
import json
from pathlib import Path

from guide.export_glb import main as export_main, write_layup_files
from guide import layup
from guide.schema import load_graph


def test_nested_ply_nodes(tmp_path):
    out = export_components(
        {"canard.core": cq.Workplane().box(10, 2, 1),
         "canard.shear_web": {"canard.shear_web.p1": cq.Workplane().box(1, 1, 1),
                              "canard.shear_web.p2": cq.Workplane().box(1, 1, 2)}},
        tmp_path / "n.glb")
    names = read_glb_node_names(out)
    assert {"canard.core", "canard.shear_web", "canard.shear_web.p1", "canard.shear_web.p2"} <= set(names)


def test_layup_files_match_the_graph(tmp_path):
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    write_layup_files(g, tmp_path)
    j = json.loads((tmp_path / "layup.json").read_text())
    assert set(j["nodes"]) == {p.node for p in layup.plies(g)}
    assert json.loads((tmp_path / "shots.json").read_text()) == layup.shots()


def test_real_export_is_deterministic_and_complete(tmp_path):
    shas = []
    for i in (1, 2):
        export_main(["--out", str(tmp_path / f"r{i}" / "longez.glb")])
        shas.append(hashlib.sha256((tmp_path / f"r{i}" / "longez.glb").read_bytes()).hexdigest())
    assert shas[0] == shas[1]
    names = set(read_glb_node_names(tmp_path / "r1" / "longez.glb"))
    nodes = set(json.loads((tmp_path / "r1" / "layup.json").read_text())["nodes"])
    assert nodes <= names and "canard.core" in names


def _glb_json(p: Path) -> dict:
    b = p.read_bytes()
    n = int.from_bytes(b[12:16], "little")
    return json.loads(b[20 : 20 + n])


def test_real_export_nests_plies_and_keeps_inches(tmp_path):  # viewer parent walk + Blender check_axes
    export_main(["--out", str(tmp_path / "longez.glb")])
    j = _glb_json(tmp_path / "longez.glb")
    parent = {c: j["nodes"][i]["name"] for i, n in enumerate(j["nodes"]) for c in n.get("children", ())}
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    for node, info in json.loads((tmp_path / "layup.json").read_text())["nodes"].items():
        assert parent[idx[node]] == info["component"], node
    ys = [v for a in j["accessors"] if "max" in a and len(a["max"]) == 3 for v in (a["min"][1], a["max"][1])]
    assert min(ys) >= -1e-6 and abs(max(ys) - 63.0) < 0.01  # inches, BL 0..semi-span before the root Z-up→Y-up rotation
