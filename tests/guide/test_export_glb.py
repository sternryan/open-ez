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
    # the canard's meshes only: the fuselage (chapters 4-6) shares the file and spans both sides of B.L. 0
    under = lambda i: j["nodes"][i]["name"].startswith("canard.") or (i in parent and under(idx[parent[i]]))  # noqa: E731
    acc = {prim["attributes"]["POSITION"] for i, n in enumerate(j["nodes"]) if "mesh" in n and under(i)
           for prim in j["meshes"][n["mesh"]]["primitives"]}
    ys = [v for k in acc for a in [j["accessors"][k]] for v in (a["min"][1], a["max"][1])]
    assert ys and min(ys) >= -1e-6 and abs(max(ys) - 70.8) < 0.01  # inches, BL 0..semi-span (canard_span 141.6 / 2) before the root Z-up→Y-up rotation


# ---- fuselage box (chapters 4-6) in the lab export (Block 2 M2.2 Task 5) ----
import math  # noqa: E402
import re  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture(scope="module")
def fuse_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("fuse") / "longez.glb"
    export_main(["--out", str(out)])
    return out


def _parents(j):
    return {c: j["nodes"][i]["name"] for i, n in enumerate(j["nodes"]) for c in n.get("children", ())}


def test_fuselage_parts_and_plies_are_glb_nodes_nested_like_the_canard(fuse_export):
    from core.fuselage_book import build_fuselage
    from core.fuselage_plies import plies

    j = _glb_json(fuse_export)
    names = [n["name"] for n in j["nodes"]]
    idx = {n: i for i, n in enumerate(names)}
    parent = _parents(j)
    parts = build_fuselage()
    for part in parts:
        assert f"fuselage.{part}" in idx, part  # one node per part
    pl = plies()
    with_plies = {p.part for p in pl}
    for p in pl:
        assert parent[idx[p.node]] == f"fuselage.{p.part}", p.node  # a child of its part's sub-assembly
    for part in parts:
        kids = [names[c] for c in j["nodes"][idx[f"fuselage.{part}"]].get("children", ())]
        if part in with_plies:
            assert sorted(k for k in kids if re.search(r"\.p\d+$", k)) == sorted(p.node for p in pl if p.part == part)


def test_layup_json_fuselage_section_carries_every_ch4_6_ply_or_its_exclusion(fuse_export):
    from core import fuselage_plies as fp
    from core.fuselage_book import build_fuselage

    lj = json.loads((fuse_export.parent / "layup.json").read_text())
    assert {"ops", "semi_span", "nodes"} <= set(lj)  # the canard's keys are untouched
    assert not any(k.startswith("fuselage.") for k in lj["nodes"])
    fz = lj["fuselage"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    pl = fp.plies(g)
    assert set(fz["nodes"]) == {p.node for p in pl}
    for p in pl:
        n = fz["nodes"][p.node]
        assert (n["op"], n["cloth"], n["orientation_deg"], n["fidelity"], n["lower_bound"], n["part"]) == (
            p.op, p.cloth, p.orientation_deg, p.fidelity, p.lower_bound, p.part)
        assert n["fs_min"] <= n["fs_max"]
    # every chapter 4-6 material row is either laid (as many plies as it says, on every target) or excluded with its reason
    excluded = {(e["op"], e["where"]) for e in fz["excluded"]}
    for op_id, op in g.ops.items():
        if op.chapter not in (4, 5, 6):
            continue
        for m in op.materials:
            key = (op_id, m["where"])
            laid = [n for n in fz["nodes"].values() if (n["op"], n["where"]) == key]
            if key in excluded:
                assert not laid, key
            else:
                assert len(laid) == int(m["plies"]) * len(fp.SCOPE[key].targets), key
    # within an op the lay order runs 1..n with no gaps, in the order the plies are laid
    for op_id in fz["ops"]:
        orders = sorted(n["op_order"] for n in fz["nodes"].values() if n["op"] == op_id)
        assert orders == list(range(1, len(orders) + 1)), op_id
    parts = build_fuselage()
    assert set(fz["parts"]) == set(parts)
    for name, part in parts.items():
        e = fz["parts"][name]
        assert e["node"] == f"fuselage.{name}" and e["fidelity"] == part.fidelity
        assert e["component"] in {c.id for c in g.components.values()}, name
        # a fitted shape is never labelled as book, and a book part never claims to be fitted
        assert ("fitted shape" in e["label"]) == (part.fidelity == "representational"), (name, e["label"])
    for n in fz["nodes"].values():
        assert n["fidelity"] == fz["parts"][n["part"]]["fidelity"]  # a ply on a fitted part is fitted too
    for name, e in fz["parts"].items():  # every bulkhead's forward face points forward (the lab lays it flat on it)
        assert (e["fwd_normal"] is not None) == (name in ("front_seat_bkhd", "rear_seat_bkhd", "f22", "f28", "panel", "firewall")), name
        assert e["fwd_normal"] is None or e["fwd_normal"][0] <= -0.5, (name, e["fwd_normal"])


def test_fuselage_ply_shells_sit_on_their_region_and_stack_outward(fuse_export):
    from guide.fuselage_export import PLY_T, ply_shells

    shells = ply_shells()
    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    for node, n in fz["nodes"].items():
        bb = shells[node].val().BoundingBox()
        assert bb.xmin == pytest.approx(n["fs_min"], abs=1e-4) and bb.xmax == pytest.approx(n["fs_max"], abs=1e-4)
    # the second UND on the front seat bulkhead's front face lies one ply further forward than the first
    a = shells["fuselage.front_seat_bkhd.p1"].val().BoundingBox()
    b = shells["fuselage.front_seat_bkhd.p2"].val().BoundingBox()
    assert a.xmin - b.xmin >= 0.5 * PLY_T - 1e-9  # the front face's normal is at least half along -x (the region rule)


def test_ledger_json_is_written_beside_layup_json_and_says_the_cg_is_not_computed(fuse_export):
    from core.ledger import fuselage_ledger_json

    lj = json.loads((fuse_export.parent / "ledger.json").read_text())
    assert lj == json.loads(json.dumps(fuselage_ledger_json()))
    assert lj["cg"]["arm_in"] is None and lj["cg"]["weight_lb"] == 0  # no part is fully sourced yet

