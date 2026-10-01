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


# The Blender cutaway's inputs are canard-only (render_cutaway.sh; its contract checks the WHOLE scene spans
# B.L. 0..semi-span). The M2.2 site glb gained the fuselage and broke that contract on anvil; the node set
# below is the pre-M2.2 export's (f41ac44), so the cutaway input cannot pick up anything else again.
PRE_M22_CANARD_NODES = {
    "longez", "canard.core",
    "canard.shear_web", *(f"canard.shear_web.p{i}" for i in range(1, 7)),
    "canard.skin_bottom", *(f"canard.skin_bottom.p{i}" for i in range(1, 4)),
    "canard.skin_top", *(f"canard.skin_top.p{i}" for i in range(1, 5)),
    "canard.spar_cap_bottom", "canard.spar_cap_bottom.p1", "canard.spar_cap_top", "canard.spar_cap_top.p1",
}


def test_cutaway_export_is_the_canard_alone(tmp_path):
    export_main(["--out", str(tmp_path / "longez.glb")])
    d = tmp_path / "canard"
    assert set(read_glb_node_names(d / "longez.glb")) == PRE_M22_CANARD_NODES
    j = _glb_json(d / "longez.glb")
    ys = [v for n in j["nodes"] if "mesh" in n for prim in j["meshes"][n["mesh"]]["primitives"]
          for a in [j["accessors"][prim["attributes"]["POSITION"]]] for v in (a["min"][1], a["max"][1])]
    assert ys and min(ys) >= -1e-6 and abs(max(ys) - 70.8) < 0.01  # every mesh: B.L. 0..semi-span
    lj = json.loads((d / "layup.json").read_text())
    full = json.loads((tmp_path / "layup.json").read_text())
    assert "fuselage" not in lj and lj == {k: v for k, v in full.items() if k != "fuselage"}
    assert (d / "shots.json").read_text() == (tmp_path / "shots.json").read_text()


# ---- fuselage box and main gear (chapters 4-9) in the lab export (Block 2 M2.2 Task 5, M2.3 Task 5) ----
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
    from guide import fuselage_export as fe

    j = _glb_json(fuse_export)
    names = [n["name"] for n in j["nodes"]]
    idx = {n: i for i, n in enumerate(names)}
    parent = _parents(j)
    parts = fe._parts()  # the exported chapters' parts (fe.EXPORT_CHAPTERS): the box, the carved band and the gear
    assert set(fe.EXPORT_CHAPTERS) == {4, 5, 6, 7, 8, 9}
    from core.fuselage_book import build_fuselage
    from core.landing_gear_book import build_gear
    assert set(build_fuselage()) | set(build_gear()) <= set(parts)  # every part of the model, none left out
    for part in parts:
        assert fe.node_of(part) in idx, part  # one node per part
        assert fe.node_of(part).startswith("gear." if part in build_gear() else "fuselage."), part
    pl = fe._plies()
    from core import fuselage_plies as fp
    assert {p.node for p in pl} == {p.node for p in fp.plies()}  # every chapter 4-8 ply
    with_plies = {p.part for p in pl}
    for p in pl:
        assert parent[idx[p.node]] == fe.node_of(p.part), p.node  # a child of its part's sub-assembly
    for part in parts:
        kids = [names[c] for c in j["nodes"][idx[fe.node_of(part)]].get("children", ())]
        if part in with_plies:
            assert sorted(k for k in kids if re.search(r"\.p\d+$", k)) == sorted(p.node for p in pl if p.part == part)


def test_layup_json_fuselage_section_carries_every_ch4_9_ply_or_its_exclusion(fuse_export):
    from core import fuselage_plies as fp

    lj = json.loads((fuse_export.parent / "layup.json").read_text())
    assert {"ops", "semi_span", "nodes"} <= set(lj)  # the canard's keys are untouched
    assert not any(k.startswith("fuselage.") for k in lj["nodes"])
    fz = lj["fuselage"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    from guide import fuselage_export as fe

    keep = tuple(f"f{c:02d}." for c in fe.EXPORT_CHAPTERS)
    pl = [p for p in fp.plies(g) if p.op.startswith(keep)]  # the exported chapters' plies
    assert set(fz["nodes"]) == {p.node for p in pl}
    for p in pl:
        n = fz["nodes"][p.node]
        assert (n["op"], n["cloth"], n["orientation_deg"], n["fidelity"], n["lower_bound"], n["part"]) == (
            p.op, p.cloth, p.orientation_deg, p.fidelity, p.lower_bound, p.part)
        assert n["fs_min"] <= n["fs_max"]
    # every chapter 4-9 material row is either laid (as many plies as it says, on every target) or excluded with its reason
    excluded = {(e["op"], e["where"]) for e in fz["excluded"]}
    assert all(e["reason"] and e["parts"] for e in fz["excluded"])
    for op_id, op in g.ops.items():
        if op.chapter not in fe.EXPORT_CHAPTERS:
            continue
        for m in op.materials:
            key = (op_id, m["where"])
            laid = [n for n in fz["nodes"].values() if (n["op"], n["where"]) == key]
            if key in excluded:
                assert not laid, key
            else:
                assert key in fp.SCOPE, key  # chapter 9's rows are all excluded (no ply model for the gear)
                assert len(laid) == int(m["plies"]) * len(fp.SCOPE[key].targets), key
    # within an op the lay order runs 1..n with no gaps, in the order the plies are laid
    for op_id in fz["ops"]:
        orders = sorted(n["op_order"] for n in fz["nodes"].values() if n["op"] == op_id)
        assert orders == list(range(1, len(orders) + 1)), op_id
    parts = fe._parts()
    assert set(fz["parts"]) == set(parts)
    for name, part in parts.items():
        e = fz["parts"][name]
        assert e["node"] == fe.node_of(name) and e["fidelity"] == part.fidelity
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



# ---- Block 2 M2.3 Task 5: chapters 7-9 in the lab export ----
def test_rollover_ply_shells_cover_the_faces_the_ledger_measures():
    from core import fuselage_book as fb
    from guide import fuselage_export as fe

    for kind in ("inside", "outside"):
        area = sum(f.Area() for f in fe.rollover_glass_faces(kind))
        assert area == pytest.approx(fb.rollover_face_area(kind)[0], rel=1e-9), kind


def test_stages_carve_cut_and_hole_the_shapes_from_their_ops(fuse_export):
    import cadquery as cq
    from guide import fuselage_export as fe

    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    names = set(read_glb_node_names(fuse_export))
    st = fz["stages"]
    # the sides: carved, then cut; the bottom carved; the longerons and F22 cut; the roll-over holed after its outside glass
    assert [x["from"] for x in st["fuselage.side_left"]] == [fe.CARVE_OP, fe.CUTOUT_OP]
    assert [x["from"] for x in st["fuselage.bottom"]] == [fe.CARVE_OP]
    for n in ("fuselage.top_longeron_left", "fuselage.top_longeron_right", "fuselage.f22"):
        assert [x["from"] for x in st[n]] == [fe.CUTOUT_OP], n
    assert [x["from"] for x in st["fuselage.rollover"]] == [fe.HOLES_OP]
    for node, stages in st.items():
        for x in stages:
            assert x["node"] in names and x["node"].startswith(node + "~"), x
    # F28 and its plies keep their shape: the opening stops at F28
    assert not any(k.startswith("fuselage.f28") for k in st)
    base, stg = fe._base_and_stages()
    vol = lambda wp: sum(v.Volume() for v in wp.vals())  # noqa: E731
    cut_side = dict((n, sh) for _op, n, sh in stg["fuselage.side_left"])["fuselage.side_left~cut"]
    assert vol(cut_side) < vol(base["side_left"]) - 1.0  # the opening takes foam out
    # nothing of a cut part or of a ply laid on it after the cut stays inside the opening (F22's forward plies go with its tab)
    region = fe._cutout_region().val()
    for node, sh in [(n, s) for v in stg.values() for _op, n, s in v if n.endswith("~cut")] + [
        (p.node, fe.ply_shells()[p.node]) for p in fe._plies() if p.part in fe.CUT_PARTS and p.op.startswith(("f07.skin", "f08."))
    ]:
        inside = sum(cq.Workplane("XY").add(x).intersect(cq.Workplane("XY").add(region)).val().Volume() for x in sh.vals())
        assert inside < 1e-6, node
    # the roll-over shows filled before the access holes are cut, holed after (the part's own shape)
    from core.fuselage_book import build_fuselage

    assert vol(base["rollover"]) > vol(build_fuselage()["rollover"].solid) + 1.0


def test_gear_parts_are_gear_nodes_with_their_fidelity_and_the_axle_marks_are_book(fuse_export):
    from config import config
    from core.landing_gear_book import bank_pose, build_gear
    from guide import fuselage_export as fe
    import numpy as np

    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    comps = {c.id for c in g.components.values()}
    for name, part in build_gear().items():
        e = fz["parts"][name]
        assert e["node"] == f"gear.{name}" and e["component"] in comps and e["fidelity"] == part.fidelity
        assert ("fitted shape" in e["label"]) == (part.fidelity == "representational")
    # the strut, extrusions, tubes and axles are fitted shapes (striped in the lab); the datum board is derived from p50
    for name in ("strut", "extrusions", "gear_tubes", "axles"):
        assert fz["parts"][name]["fidelity"] == "representational", name
    assert fz["parts"]["datum_board"]["fidelity"] == "derived"
    assert fz["parts"]["carved_corners"]["fidelity"] == "representational"
    assert fz["parts"]["canard_cutout"]["fidelity"] == "representational" and fz["parts"]["canard_cutout"]["void"] is True
    G = config.geometry
    gm = fz["gear_marks"]
    assert gm["axle_fs"] == G.fs_spar_aft_face - 15 == 110.5 and gm["board_fs"] == 125.5 and gm["board_bl"] == 26.75
    assert gm["axle_fwd_of_board_in"] == 15.0
    # the bank sign: at the right skin the right side's AND the bottom's outward normals point up (core.landing_gear_book.bank_pose);
    # 135 degrees is the captain's reading of p46's "45 degrees of left bank" (was 45; changed by the 135 decision)
    assert fz["bank_deg"] == {"f07.skin-right": 135.0, "f07.skin-left": -135.0}
    rot = bank_pose(fz["bank_deg"]["f07.skin-right"]).rotation
    assert (rot @ np.array([0.0, 1.0, 0.0]))[2] > 0.7 and (rot @ np.array([0.0, 0.0, -1.0]))[2] > 0.7
    # the track has no source: it appears nowhere in what the lab reads
    txt = json.dumps(fz)
    assert not re.search(r"track\D{0,20}\d", txt, re.I) and "84" not in json.dumps({k: v for k, v in fz.items() if k in ("gear_marks", "bank_deg")})


# ---- Block 2 M2.4 Task 5: chapters 11-13 in the lab export ----
def test_default_export_sorts_into_the_labs_subjects_by_prefix_and_the_cutaway_stays_canard_alone(fuse_export, tmp_path):
    from guide.export_glb import canard_components, default_components

    comps = default_components()
    fam = ("canard.", "elevator.", "fuselage.", "gear.", "nose.")
    assert all(k.startswith(fam) for k in comps), [k for k in comps if not k.startswith(fam)]
    for f in fam:
        assert any(k.startswith(f) for k in comps), f
    assert all(k.startswith("canard.") for k in canard_components())
    names = set(read_glb_node_names(fuse_export))
    assert {"elevator.right", "elevator.left", "nose.skin", "nose.nb_box", "gear.nose_strut", "nose.ng_hardware"} <= names
    j = _glb_json(fuse_export)
    parent = _parents(j)
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    assert parent[idx["elevator.tube.right"]] == "elevator.tube"  # the lab splits an elevator part into its right and left by name
    assert parent[idx["elevator.hinges.left"]] == "elevator.hinges"


def test_layup_extras_carry_the_nose_the_elevators_the_install_and_the_nose_gear_inputs(fuse_export):
    import json as _json
    import re as _re

    from core import elevators_kin as ek

    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    ex = fz["extras"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    comps = {c.id for c in g.components.values()}
    names = set(read_glb_node_names(fuse_export))
    # the chapter 4-9 part rows are unchanged (the lab's existing contract); the nose has rows of its own
    assert not any(k.startswith(("nose_", "gear_nose")) for k in fz["parts"])
    assert len(ex["nose_parts"]) == 15  # 13 nose components, the NG hardware, the nose strut group (nose.worm_drive has no geometry)
    for name, row in ex["nose_parts"].items():
        assert row["node"] in names and row["component"] in comps and row["node"] == row["component"], name
        assert row["fidelity"] == "representational" and row["label"].endswith("(fitted shape)"), name
        assert row["fs_min"] <= row["fs_max"]
    nose_x = [r["fs_min"] for r in ex["nose_parts"].values()]
    assert min(nose_x) < 0 and min(nose_x) == pytest.approx(-6.8, abs=0.01)  # the model runs to the nose tip
    assert ex["nose_parts"]["gear_nose_strut"]["show"] == {"from": "f13.lower-gear"}
    el = ex["elevators"]
    assert set(el["parts"]) == {"elevator.right", "elevator.left", "elevator.tube", "elevator.hinges", "elevator.balance_weight", "elevator.cs11_weight"}
    assert all(p["node"] in names and p["fidelity"] == "representational" and p["label"].endswith("(fitted shape)") for p in el["parts"].values())
    assert "positioned from text, low confidence" in el["parts"]["elevator.hinges"]["label"]  # the hinge plates say how well placed they are
    assert el["travel"] == {"up_target_deg": 15.0, "up_floor_deg": 12.5, "down_deg": 30.0}
    assert ek.travel_range_deg() == (15.0, 30.0)
    assert "masses not sourced" in el["hang_cg"]["note"] and el["hang_cg"]["fitted"] is True and el["hang_cg"]["dx"] < 0  # forward of the hinge
    ci = ex["canard_install"]
    assert ci["fs_le"] == 18.7 and ci["z_le"] == 1.5 and ci["incidence_deg"] == 0.0 and "unsourced" in ci["incidence_note"]
    ng = ex["nose_gear"]
    assert ng["status"] == "conflict" and {c["axle_fs"] for c in ng["candidates"].values()} == {17.0, 20.0}
    assert ng["book_seconds"][0] <= ng["retract_seconds"] <= ng["book_seconds"][1] and ng["crank_turns"] == 10.8
    # the nose wheel's F.S. is never stated alone: nothing in the extras words one candidate as the station
    assert not _re.search(r"nose wheel[^\"]{0,30}F\.S\. ?\d", _json.dumps(ex), _re.I)
    led = json.loads((fuse_export.parent / "ledger.json").read_text())["gear"]
    assert led["ground_handling"]["nose_wheel_wl"] == -22.0 and "CP25 LPC 24" in led["ground_handling"]["cite"]["nose_wheel_wl"]
    assert led["nose_arm_candidates"] == [17.0, 20.0] and led["nose_arm_candidates_status"] == "conflict"


# ---- M2.4 fix 1: the elevators' cove is lab data (layup.json extras), never geometry in the glb or the canard-only cutaway export ----
def test_the_cove_is_the_elevator_leading_edge_less_the_slot_gap_over_the_elevator_span_and_the_cutaway_export_is_untouched(fuse_export, tmp_path):
    from config.aircraft_config import config
    from core import elevators_book as eb
    from guide.export_glb import canard_components

    G = config.geometry
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]["extras"]["elevators"]
    cove = ex["cove"]
    assert cove["x_cut"] == pytest.approx(eb.x_tube_le() - G.elevator_slot_gap_in, abs=1e-6)  # read from the book numbers, never hard-coded
    assert cove["slot_gap"] == G.elevator_slot_gap_in == 0.2 and cove["bl_end"] == G.elevator_outboard_end_bl_in == 65.0
    assert cove["x_cut"] == pytest.approx(ex["tube_le_x"] - 0.2, abs=1e-6) and cove["label"].endswith("(fitted shape)")  # the cove is a fitted shape
    # the Blender cutaway's canard-only export does not know the cove: same nodes, same bytes as an export of the canard's own components,
    # and no cove or elevator key in its layup.json
    d = fuse_export.parent / "canard"
    again = export_components(canard_components(), tmp_path / "again" / "longez.glb")
    assert (d / "longez.glb").read_bytes() == again.read_bytes()
    assert set(read_glb_node_names(d / "longez.glb")) == PRE_M22_CANARD_NODES
    assert "cove" not in (d / "layup.json").read_text() and "elevator" not in (d / "layup.json").read_text()
