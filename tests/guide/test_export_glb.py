"""Test glb export with component-ID node names."""

import hashlib
import json
import re
from pathlib import Path

import cadquery as cq
import pytest

from guide import layup
from guide.export_glb import export_components, read_glb_node_names, write_layup_files
from guide.export_glb import main as export_main
from guide.schema import load_graph


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


def test_nested_ply_nodes(tmp_path):
    out = export_components(
        {
            "canard.core": cq.Workplane().box(10, 2, 1),
            "canard.shear_web": {
                "canard.shear_web.p1": cq.Workplane().box(1, 1, 1),
                "canard.shear_web.p2": cq.Workplane().box(1, 1, 2),
            },
        },
        tmp_path / "n.glb",
    )
    names = read_glb_node_names(out)
    assert {
        "canard.core",
        "canard.shear_web",
        "canard.shear_web.p1",
        "canard.shear_web.p2",
    } <= set(names)


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
        shas.append(
            hashlib.sha256((tmp_path / f"r{i}" / "longez.glb").read_bytes()).hexdigest()
        )
    assert shas[0] == shas[1]
    names = set(read_glb_node_names(tmp_path / "r1" / "longez.glb"))
    nodes = set(json.loads((tmp_path / "r1" / "layup.json").read_text())["nodes"])
    assert nodes <= names and "canard.core" in names


def _glb_json(p: Path) -> dict:
    b = p.read_bytes()
    n = int.from_bytes(b[12:16], "little")
    return json.loads(b[20 : 20 + n])


def test_real_export_nests_plies_and_keeps_inches(
    tmp_path,
):  # viewer parent walk + Blender check_axes
    export_main(["--out", str(tmp_path / "longez.glb")])
    j = _glb_json(tmp_path / "longez.glb")
    parent = {
        c: j["nodes"][i]["name"]
        for i, n in enumerate(j["nodes"])
        for c in n.get("children", ())
    }
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    for node, info in json.loads((tmp_path / "layup.json").read_text())[
        "nodes"
    ].items():
        assert parent[idx[node]] == info["component"], node

    # the canard's meshes only: the fuselage (chapters 4-6) shares the file and spans both sides of B.L. 0
    def under(i):
        return j["nodes"][i]["name"].startswith("canard.") or (
            i in parent and under(idx[parent[i]])
        )

    acc = {
        prim["attributes"]["POSITION"]
        for i, n in enumerate(j["nodes"])
        if "mesh" in n and under(i)
        for prim in j["meshes"][n["mesh"]]["primitives"]
    }
    ys = [
        v for k in acc for a in [j["accessors"][k]] for v in (a["min"][1], a["max"][1])
    ]
    assert (
        ys and min(ys) >= -1e-6 and abs(max(ys) - 70.8) < 0.01
    )  # inches, BL 0..semi-span (canard_span 141.6 / 2) before the root Z-up→Y-up rotation


# The Blender cutaway's inputs are canard-only (render_cutaway.sh; its contract checks the WHOLE scene spans
# B.L. 0..semi-span). The M2.2 site glb gained the fuselage and broke that contract on anvil; the node set
# below is the pre-M2.2 export's (f41ac44), so the cutaway input cannot pick up anything else again.
PRE_M22_CANARD_NODES = {
    "longez",
    "canard.core",
    "canard.shear_web",
    *(f"canard.shear_web.p{i}" for i in range(1, 7)),
    "canard.skin_bottom",
    *(f"canard.skin_bottom.p{i}" for i in range(1, 4)),
    "canard.skin_top",
    *(f"canard.skin_top.p{i}" for i in range(1, 5)),
    "canard.spar_cap_bottom",
    "canard.spar_cap_bottom.p1",
    "canard.spar_cap_top",
    "canard.spar_cap_top.p1",
}


def test_cutaway_export_is_the_canard_alone(tmp_path):
    export_main(["--out", str(tmp_path / "longez.glb")])
    d = tmp_path / "canard"
    assert set(read_glb_node_names(d / "longez.glb")) == PRE_M22_CANARD_NODES
    j = _glb_json(d / "longez.glb")
    ys = [
        v
        for n in j["nodes"]
        if "mesh" in n
        for prim in j["meshes"][n["mesh"]]["primitives"]
        for a in [j["accessors"][prim["attributes"]["POSITION"]]]
        for v in (a["min"][1], a["max"][1])
    ]
    assert (
        ys and min(ys) >= -1e-6 and abs(max(ys) - 70.8) < 0.01
    )  # every mesh: B.L. 0..semi-span
    lj = json.loads((d / "layup.json").read_text())
    full = json.loads((tmp_path / "layup.json").read_text())
    assert "fuselage" not in lj and lj == {
        k: v for k, v in full.items() if k != "fuselage"
    }
    assert (d / "shots.json").read_text() == (tmp_path / "shots.json").read_text()


# ---- fuselage box and main gear (chapters 4-9) in the lab export (Block 2 M2.2 Task 5, M2.3 Task 5) ----


@pytest.fixture(scope="module")
def fuse_export(tmp_path_factory):
    out = tmp_path_factory.mktemp("fuse") / "longez.glb"
    export_main(["--out", str(out)])
    return out


def _parents(j):
    return {
        c: j["nodes"][i]["name"]
        for i, n in enumerate(j["nodes"])
        for c in n.get("children", ())
    }


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

    assert set(build_fuselage()) | set(build_gear()) <= set(
        parts
    )  # every part of the model, none left out
    for part in parts:
        assert fe.node_of(part) in idx, part  # one node per part
        assert fe.node_of(part).startswith(
            "gear." if part in build_gear() else "fuselage."
        ), part
    pl = fe._plies()
    from core import fuselage_plies as fp

    assert {p.node for p in pl} == {p.node for p in fp.plies()}  # every chapter 4-8 ply
    with_plies = {p.part for p in pl}
    for p in pl:
        assert parent[idx[p.node]] == fe.node_of(
            p.part
        ), p.node  # a child of its part's sub-assembly
    for part in parts:
        kids = [names[c] for c in j["nodes"][idx[fe.node_of(part)]].get("children", ())]
        if part in with_plies:
            assert sorted(k for k in kids if re.search(r"\.p\d+$", k)) == sorted(
                p.node for p in pl if p.part == part
            )


def test_layup_json_fuselage_section_carries_every_ch4_9_ply_or_its_exclusion(
    fuse_export,
):
    from core import fuselage_plies as fp

    lj = json.loads((fuse_export.parent / "layup.json").read_text())
    assert {"ops", "semi_span", "nodes"} <= set(lj)  # the canard's keys are untouched
    assert not any(k.startswith("fuselage.") for k in lj["nodes"])
    fz = lj["fuselage"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    from guide import fuselage_export as fe

    keep = tuple(f"f{c:02d}." for c in fe.EXPORT_CHAPTERS)
    pl = [
        p for p in fp.plies(g) if p.op.startswith(keep)
    ]  # the exported chapters' plies
    assert set(fz["nodes"]) == {p.node for p in pl}
    for p in pl:
        n = fz["nodes"][p.node]
        assert (
            n["op"],
            n["cloth"],
            n["orientation_deg"],
            n["fidelity"],
            n["lower_bound"],
            n["part"],
        ) == (p.op, p.cloth, p.orientation_deg, p.fidelity, p.lower_bound, p.part)
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
                assert (
                    key in fp.SCOPE
                ), key  # chapter 9's rows are all excluded (no ply model for the gear)
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
        assert ("fitted shape" in e["label"]) == (
            part.fidelity == "representational"
        ), (name, e["label"])
    for n in fz["nodes"].values():
        assert (
            n["fidelity"] == fz["parts"][n["part"]]["fidelity"]
        )  # a ply on a fitted part is fitted too
    for name, e in (
        fz["parts"].items()
    ):  # every bulkhead's forward face points forward (the lab lays it flat on it)
        assert (e["fwd_normal"] is not None) == (
            name
            in ("front_seat_bkhd", "rear_seat_bkhd", "f22", "f28", "panel", "firewall")
        ), name
        assert e["fwd_normal"] is None or e["fwd_normal"][0] <= -0.5, (
            name,
            e["fwd_normal"],
        )


def test_fuselage_ply_shells_sit_on_their_region_and_stack_outward(fuse_export):
    from guide.fuselage_export import PLY_T, ply_shells

    shells = ply_shells()
    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    for node, n in fz["nodes"].items():
        bb = shells[node].val().BoundingBox()
        assert bb.xmin == pytest.approx(
            n["fs_min"], abs=1e-4
        ) and bb.xmax == pytest.approx(n["fs_max"], abs=1e-4)
    # the second UND on the front seat bulkhead's front face lies one ply further forward than the first
    a = shells["fuselage.front_seat_bkhd.p1"].val().BoundingBox()
    b = shells["fuselage.front_seat_bkhd.p2"].val().BoundingBox()
    assert (
        a.xmin - b.xmin >= 0.5 * PLY_T - 1e-9
    )  # the front face's normal is at least half along -x (the region rule)


def test_ledger_json_is_written_beside_layup_json_and_says_the_cg_is_not_computed(
    fuse_export,
):
    from core.ledger import fuselage_ledger_json

    lj = json.loads((fuse_export.parent / "ledger.json").read_text())
    assert lj == json.loads(json.dumps(fuselage_ledger_json()))
    assert (
        lj["cg"]["arm_in"] is None and lj["cg"]["weight_lb"] == 0
    )  # no part is fully sourced yet


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
    for n in (
        "fuselage.top_longeron_left",
        "fuselage.top_longeron_right",
        "fuselage.f22",
    ):
        assert [x["from"] for x in st[n]] == [fe.CUTOUT_OP], n
    assert [x["from"] for x in st["fuselage.rollover"]] == [fe.HOLES_OP]
    for node, stages in st.items():
        for x in stages:
            assert x["node"] in names and x["node"].startswith(node + "~"), x
    # F28 and its plies keep their shape: the opening stops at F28
    assert not any(k.startswith("fuselage.f28") for k in st)
    base, stg = fe._base_and_stages()
    vol = lambda wp: sum(v.Volume() for v in wp.vals())  # noqa: E731
    cut_side = dict((n, sh) for _op, n, sh in stg["fuselage.side_left"])[
        "fuselage.side_left~cut"
    ]
    assert vol(cut_side) < vol(base["side_left"]) - 1.0  # the opening takes foam out
    # nothing of a cut part or of a ply laid on it after the cut stays inside the opening (F22's forward plies go with its tab)
    region = fe._cutout_region().val()
    for node, sh in [
        (n, s) for v in stg.values() for _op, n, s in v if n.endswith("~cut")
    ] + [
        (p.node, fe.ply_shells()[p.node])
        for p in fe._plies()
        if p.part in fe.CUT_PARTS and p.op.startswith(("f07.skin", "f08."))
    ]:
        inside = sum(
            cq.Workplane("XY")
            .add(x)
            .intersect(cq.Workplane("XY").add(region))
            .val()
            .Volume()
            for x in sh.vals()
        )
        assert inside < 1e-6, node
    # the roll-over shows filled before the access holes are cut, holed after (the part's own shape)
    from core.fuselage_book import build_fuselage

    assert vol(base["rollover"]) > vol(build_fuselage()["rollover"].solid) + 1.0


def test_gear_parts_are_gear_nodes_with_their_fidelity_and_the_axle_marks_are_book(
    fuse_export,
):
    from config import config
    from core.landing_gear_book import bank_pose, build_gear
    import numpy as np

    fz = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"]
    g = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    comps = {c.id for c in g.components.values()}
    for name, part in build_gear().items():
        e = fz["parts"][name]
        assert (
            e["node"] == f"gear.{name}"
            and e["component"] in comps
            and e["fidelity"] == part.fidelity
        )
        assert ("fitted shape" in e["label"]) == (part.fidelity == "representational")
    # the strut, extrusions, tubes and axles are fitted shapes (striped in the lab); the datum board is derived from p50
    for name in ("strut", "extrusions", "gear_tubes", "axles"):
        assert fz["parts"][name]["fidelity"] == "representational", name
    assert fz["parts"]["datum_board"]["fidelity"] == "derived"
    assert fz["parts"]["carved_corners"]["fidelity"] == "representational"
    assert (
        fz["parts"]["canard_cutout"]["fidelity"] == "representational"
        and fz["parts"]["canard_cutout"]["void"] is True
    )
    G = config.geometry
    gm = fz["gear_marks"]
    assert (
        gm["axle_fs"] == G.fs_spar_aft_face - 15 == 110.5
        and gm["board_fs"] == 125.5
        and gm["board_bl"] == 26.75
    )
    assert gm["axle_fwd_of_board_in"] == 15.0
    # the bank sign: at the right skin the right side's AND the bottom's outward normals point up (core.landing_gear_book.bank_pose);
    # 135 degrees is the captain's reading of p46's "45 degrees of left bank" (was 45; changed by the 135 decision)
    assert fz["bank_deg"] == {"f07.skin-right": 135.0, "f07.skin-left": -135.0}
    rot = bank_pose(fz["bank_deg"]["f07.skin-right"]).rotation
    assert (rot @ np.array([0.0, 1.0, 0.0]))[2] > 0.7 and (
        rot @ np.array([0.0, 0.0, -1.0])
    )[2] > 0.7
    # the track has no source: it appears nowhere in what the lab reads
    txt = json.dumps(fz)
    assert not re.search(r"track\D{0,20}\d", txt, re.I) and "84" not in json.dumps(
        {k: v for k, v in fz.items() if k in ("gear_marks", "bank_deg")}
    )


# ---- Block 2 M2.4 Task 5: chapters 11-13 in the lab export ----
def test_default_export_sorts_into_the_labs_subjects_by_prefix_and_the_cutaway_stays_canard_alone(
    fuse_export, tmp_path
):
    from guide.export_glb import canard_components, default_components

    comps = default_components()
    fam = (
        "canard.",
        "elevator.",
        "fuselage.",
        "gear.",
        "nose.",
        "spar.",
        "firewall.",
        "controls.",
        "trim.",
        "canopy.",
        "wing.",
        "winglet.",
        "strake.",
        "elec.",
        "engine.",
        "cover.",
        "upholstery.",
    )
    assert all(k.startswith(fam) for k in comps), [
        k for k in comps if not k.startswith(fam)
    ]
    for f in fam:
        assert any(k.startswith(f) for k in comps), f
    assert all(k.startswith("canard.") for k in canard_components())
    names = set(read_glb_node_names(fuse_export))
    assert {
        "elevator.right",
        "elevator.left",
        "nose.skin",
        "nose.nb_box",
        "gear.nose_strut",
        "nose.ng_hardware",
    } <= names
    j = _glb_json(fuse_export)
    parent = _parents(j)
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    assert (
        parent[idx["elevator.tube.right"]] == "elevator.tube"
    )  # the lab splits an elevator part into its right and left by name
    assert parent[idx["elevator.hinges.left"]] == "elevator.hinges"


def test_layup_extras_carry_the_nose_the_elevators_the_install_and_the_nose_gear_inputs(
    fuse_export,
):
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
    assert (
        len(ex["nose_parts"]) == 15
    )  # 13 nose components, the NG hardware, the nose strut group (nose.worm_drive has no geometry)
    for name, row in ex["nose_parts"].items():
        assert (
            row["node"] in names
            and row["component"] in comps
            and row["node"] == row["component"]
        ), name
        assert row["fidelity"] == "representational" and row["label"].endswith(
            "(fitted shape)"
        ), name
        assert row["fs_min"] <= row["fs_max"]
    nose_x = [r["fs_min"] for r in ex["nose_parts"].values()]
    assert min(nose_x) < 0 and min(nose_x) == pytest.approx(
        -6.8, abs=0.01
    )  # the model runs to the nose tip
    assert ex["nose_parts"]["gear_nose_strut"]["show"] == {"from": "f13.lower-gear"}
    el = ex["elevators"]
    assert set(el["parts"]) == {
        "elevator.right",
        "elevator.left",
        "elevator.tube",
        "elevator.hinges",
        "elevator.balance_weight",
        "elevator.cs11_weight",
    }
    assert all(
        p["node"] in names
        and p["fidelity"] == "representational"
        and "fitted" in p["label"]
        for p in el["parts"].values()
    )
    assert (
        el["parts"]["elevator.hinges"]["label"]
        == "Elevator hinges (from text, low confidence; fitted shape)"
    )  # the hinge plates say how well placed they are, in one parenthetical
    assert (
        el["parts"]["elevator.tube"]["label"]
        == "Elevator torque tubes (1 in OD book; section fitted, unresolved)"
    )  # M2.4 review 7: the tube is the book's, the section is not
    assert all(
        p["label"].endswith("(fitted shape)")
        for c, p in el["parts"].items()
        if c not in ("elevator.hinges", "elevator.tube")
    )
    assert el["travel"] == {
        "up_target_deg": 15.0,
        "up_floor_deg": 12.5,
        "down_deg": 30.0,
    }
    assert ek.travel_range_deg() == (15.0, 30.0)
    assert (
        "masses not sourced" in el["hang_cg"]["note"]
        and el["hang_cg"]["fitted"] is True
        and el["hang_cg"]["dx"] < 0
    )  # forward of the hinge
    ci = ex["canard_install"]
    assert (
        ci["fs_le"] == 18.7
        and ci["z_le"] == 1.5
        and ci["incidence_deg"] == 0.0
        and "unsourced" in ci["incidence_note"]
    )
    ng = ex["nose_gear"]
    assert ng["status"] == "conflict" and {
        c["axle_fs"] for c in ng["candidates"].values()
    } == {17.0, 20.0}
    assert (
        ng["book_seconds"][0] <= ng["retract_seconds"] <= ng["book_seconds"][1]
        and ng["crank_turns"] == 10.8
    )
    # the nose wheel's F.S. is never stated alone: nothing in the extras words one candidate as the station
    assert not _re.search(r"nose wheel[^\"]{0,30}F\.S\. ?\d", _json.dumps(ex), _re.I)
    led = json.loads((fuse_export.parent / "ledger.json").read_text())["gear"]
    assert (
        led["ground_handling"]["nose_wheel_wl"] == -22.0
        and "CP25 LPC 24" in led["ground_handling"]["cite"]["nose_wheel_wl"]
    )
    assert (
        led["nose_arm_candidates"] == [17.0, 20.0]
        and led["nose_arm_candidates_status"] == "conflict"
    )


# ---- M2.4 fix 1: the elevators' cove is lab data (layup.json extras), never geometry in the glb or the canard-only cutaway export ----
def test_the_cove_is_the_elevator_leading_edge_less_the_slot_gap_over_the_elevator_span_and_the_cutaway_export_is_untouched(
    fuse_export, tmp_path
):
    from config.aircraft_config import config
    from core import elevators_book as eb
    from guide.export_glb import canard_components

    G = config.geometry
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"][
        "extras"
    ]["elevators"]
    cove = ex["cove"]
    assert cove["x_cut"] == pytest.approx(
        eb.x_tube_le() - G.elevator_slot_gap_in, abs=1e-6
    )  # read from the book numbers, never hard-coded
    assert (
        cove["slot_gap"] == G.elevator_slot_gap_in == 0.2
        and cove["bl_end"] == G.elevator_outboard_end_bl_in == 65.0
    )
    # M2.4 fix 3: the cove is the FOAM span only (inner bound read from the book spans, not a literal), so the canard keeps its root
    assert (
        cove["bl_start"]
        == pytest.approx(G.elevator_inboard_bl_right_in)
        == pytest.approx(-G.elevator_inboard_bl_left_in)
        == pytest.approx(9.3)
    )
    assert (
        ex["installed_label"]
        == "Elevators (fitted shape; span vs fuselage sides unresolved)"
    )
    assert cove["x_cut"] == pytest.approx(ex["tube_le_x"] - 0.2, abs=1e-6) and cove[
        "label"
    ].endswith("(fitted shape)")  # the cove is a fitted shape
    # the Blender cutaway's canard-only export does not know the cove: same nodes, same bytes as an export of the canard's own components,
    # and no cove or elevator key in its layup.json
    d = fuse_export.parent / "canard"
    again = export_components(canard_components(), tmp_path / "again" / "longez.glb")
    assert (d / "longez.glb").read_bytes() == again.read_bytes()
    assert set(read_glb_node_names(d / "longez.glb")) == PRE_M22_CANARD_NODES
    assert (
        "cove" not in (d / "layup.json").read_text()
        and "elevator" not in (d / "layup.json").read_text()
    )


# ---- M2.5: spar, firewall face, controls and trim in the lab export ----
M25_IDS = {
    "spar.box",
    "spar.cap_top",
    "spar.cap_bottom",
    "spar.bulkheads",
    "spar.lwa",
    "spar.spruce_blocks",
    "spar.em12",
    "spar.sh1",
    "spar.jig",
    "fuselage.firewall_stainless",
    "firewall.belcrank",
    "firewall.master_cylinders",
    "controls.consoles",
    "controls.torque_tube",
    "controls.sticks",
    "controls.pitch_pushrod",
    "controls.rudder_conduit",
    "trim.pitch_handle",
    "trim.roll_trim",
}


def test_m25_components_are_glb_nodes_named_by_component_id_with_part_children(
    fuse_export,
):
    j = _glb_json(fuse_export)
    names = {n["name"] for n in j["nodes"]}
    assert M25_IDS <= names
    parent = _parents(j)
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    for child, par in (
        ("spar.bulkheads.end_bulkheads", "spar.bulkheads"),
        ("spar.lwa.lwa4", "spar.lwa"),
        ("controls.sticks.front_stick", "controls.sticks"),
        ("trim.pitch_handle.pth", "trim.pitch_handle"),
    ):
        assert parent[idx[child]] == par
    graph = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    assert M25_IDS <= set(graph.components)
    assert all(graph.components[c].fidelity != "no-geometry" for c in M25_IDS)


def test_the_jigs_and_the_canopy_blocks_are_flagged_workshop_and_nothing_else_is(
    fuse_export,
):
    j = _glb_json(fuse_export)
    flagged = {
        n["name"] for n in j["nodes"] if n.get("extras", {}).get("workshop") is True
    }
    assert flagged == {"spar.jig", "canopy.blocks", "wing.jigs", "winglet.jig"} | {
        n["name"]
        for n in j["nodes"]
        if n["name"].startswith(("wing.jigs.", "winglet.jig."))
    }


def test_m25_installed_nodes_sit_in_the_airframe_frame(fuse_export):
    j = _glb_json(fuse_export)
    acc = j["accessors"]
    mesh_of = {n["name"]: n["mesh"] for n in j["nodes"] if "mesh" in n}
    pos = j["meshes"][mesh_of["spar.box"]]["primitives"][0]["attributes"]["POSITION"]
    assert acc[pos]["min"][0] == pytest.approx(118.5, abs=1e-3)  # FS, inches
    assert acc[pos]["max"][0] == pytest.approx(129.898, abs=1e-2)


# ---- M2.6: the canopy in the lab export ----
M26_SINGLE = {
    "canopy.plexi",
    "canopy.blocks",
    "canopy.vent",
    "canopy.brace_tubes",
    "canopy.latches",
    "fuselage.front_cover",
    "fuselage.rear_cover",
    "fuselage.door",
}
M26_GROUPS = {
    "canopy.pads": ("pads_hinge", "pads_latch", "pad_catch"),
    "canopy.hinges": ("hinge_fuselage", "hinge_canopy"),
    "canopy.safety_catch": ("sc1", "sc1_bolt"),
}


def test_m26_components_are_glb_nodes_named_by_component_id_with_part_children(
    fuse_export,
):
    j = _glb_json(fuse_export)
    names = {n["name"] for n in j["nodes"]}
    assert M26_SINGLE <= names
    parent = _parents(j)
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    for cid, kids in M26_GROUPS.items():
        assert cid in names
        for k in kids:
            assert parent[idx[f"{cid}.{k}"]] == cid
    graph = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    # the frame is a group like a fuselage part: its own solid (canopy.frame_part) and the five glass plies (canopy.frame.p1..p5)
    assert parent[idx["canopy.frame_part"]] == "canopy.frame"
    for k in range(1, 6):
        assert parent[idx[f"canopy.frame.p{k}"]] == "canopy.frame"
    ids = M26_SINGLE | set(M26_GROUPS) | {"canopy.frame"}
    assert ids <= set(graph.components)
    assert all(graph.components[c].fidelity != "no-geometry" for c in ids)
    # the single-part components carry their own mesh; the groups carry it in their children
    assert all("mesh" in j["nodes"][idx[c]] for c in M26_SINGLE)


def test_m26_nodes_sit_in_the_airframe_frame_in_inches(fuse_export):
    j = _glb_json(fuse_export)
    acc = j["accessors"]
    mesh_of = {n["name"]: n["mesh"] for n in j["nodes"] if "mesh" in n}

    def x_range(name):
        ps = [
            acc[p["attributes"]["POSITION"]]
            for p in j["meshes"][mesh_of[name]]["primitives"]
        ]
        return min(a["min"][0] for a in ps), max(a["max"][0] for a in ps)

    lo, hi = x_range("canopy.plexi")
    assert lo == pytest.approx(44.75, abs=1e-3)  # nose, 5.0 aft of the panel
    assert hi == pytest.approx(112.75, abs=1e-3)  # 68 in long
    lo, hi = x_range("fuselage.rear_cover")
    assert lo == pytest.approx(117.0, abs=1e-3)  # the rear cut
    assert hi == pytest.approx(125.0, abs=1e-3)  # the firewall


def test_m26_layup_section_names_every_canopy_part_the_five_plies_and_the_conflicts(
    fuse_export,
):
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"][
        "extras"
    ]["m26"]
    parts, nodes, c = ex["parts"], ex["nodes"], ex["canopy"]
    assert all(r["fidelity"] == "representational" for r in parts.values())
    assert all("(fitted shape" in r["label"] for r in parts.values())
    # the five-ply schedule (p110): groove ply first, BID at 45, 2 BID + 2 UND on the sides, 3 BID front and rear
    order = sorted(nodes, key=lambda k: nodes[k]["op_order"])
    assert order == [f"canopy.frame.p{i}" for i in range(1, 6)]
    assert [nodes[k]["cloth"] for k in order] == ["BID", "BID", "UND", "BID", "UND"]
    assert [nodes[k]["region"] for k in order] == [
        "overall",
        "overall",
        "sides",
        "ends",
        "sides",
    ]
    assert all(nodes[k]["op"] == "f18.glass-outside" for k in order)
    assert all(
        nodes[k]["orientation_deg"] == 45.0 for k in order if nodes[k]["cloth"] == "BID"
    )
    # the temporary blocks have their own window, the frame's three shapes follow one another
    assert parts["canopy_blocks"]["show"] == {
        "from": "f18.locate-blocks",
        "until": "f18.carve-inside",
    }
    assert parts["canopy_frame_foam"]["show"]["until"] == "f18.carve-outside"
    assert parts["canopy_frame_carved"]["show"]["from"] == "f18.carve-outside"
    assert parts["canopy_frame"]["show"] == {"from": "f18.carve-inside"}
    # pads carry their role; the conflicts are carried as data, never resolved
    assert {parts[k]["role"] for k in parts if k.startswith("canopy_pads_")} == {
        "hinge",
        "latch",
        "catch",
    }
    assert c["latch"]["derived_centres_fs"] == [104.75, 74.75, 44.75]
    assert c["latch"]["printed_labels_fs"] == [104.0, 74.0, 44.0]
    assert c["latch"]["gap_in"] == 0.75
    assert c["front_cut"] == {"fs": 41.65, "datum_named": False}
    assert (
        c["hinge"]["max_open_deg"] == 105.0 and c["hinge"]["past_vertical_deg"] == 15.0
    )
    assert [(k["id"], k["height_in"], k["wl0"]) for k in c["checks"]] == [
        ("A", 13.5, 23.0),
        ("B", 12.3, 23.0),
    ]


# ---- M2.7: the wings and winglets in the lab export ----
M27_WING = {
    "wing.jigs",
    "wing.cores",
    "wing.hardpoints",
    "wing.shear_web",
    "wing.spar_caps",
    "wing.skins",
    "wing.conduit",
    "wing.ribs",
    "wing.aileron",
    "wing.aileron_hinges",
    "wing.controls",
    "wing.attach",
}
M27_WINGLET = {
    "winglet.cores",
    "winglet.skins",
    "winglet.jig",
    "winglet.layups",
    "winglet.block_a",
    "winglet.lower_fin",
    "winglet.rudder",
    "winglet.rudder_hinge",
}


def test_m27_components_are_group_nodes_with_a_child_per_part_and_side_and_per_ply(
    fuse_export,
):
    j = _glb_json(fuse_export)
    names = {n["name"] for n in j["nodes"]}
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    parent = _parents(j)
    assert M27_WING | M27_WINGLET <= names
    graph = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    assert M27_WING | M27_WINGLET <= set(graph.components)
    for cid, kid in (
        ("wing.cores", "wing.cores.fc1.right"),
        ("wing.cores", "wing.cores.fc5.left"),
        ("wing.aileron", "wing.aileron.aileron.right"),
        ("wing.aileron_hinges", "wing.aileron_hinges.aileron_rod.left"),
        ("wing.attach", "wing.attach.spar_bolts.right"),
        ("winglet.rudder", "winglet.rudder.rudder.right"),
        ("winglet.rudder", "winglet.rudder.belhorn.left"),
        ("winglet.cores", "winglet.cores.upper_core.right"),
        ("wing.shear_web", "wing.shear_web.shear_web.right.p6"),
        ("wing.spar_caps", "wing.spar_caps.cap_top.left.p7"),
        ("wing.spar_caps", "wing.spar_caps.cap_bottom.right.p5"),
        ("wing.skins", "wing.skins.skin_top.right.p3"),
        ("winglet.skins", "winglet.skins.skin_out.left.p3"),
        ("winglet.layups", "winglet.layups.layup_3.right.p7"),
    ):
        assert parent[idx[kid]] == cid, kid
    # the ply parts are plies only: the merged solid is not exported beside them
    assert "wing.shear_web.shear_web.right" not in names
    assert all(
        "mesh" in j["nodes"][idx[n]]
        for n in names
        if n.startswith(("wing.cores.", "winglet.rudder.")) and n.count(".") == 3
    )


def test_m27_nodes_sit_in_the_airframe_frame_in_inches(fuse_export):
    j = _glb_json(fuse_export)
    acc = j["accessors"]
    mesh_of = {n["name"]: n["mesh"] for n in j["nodes"] if "mesh" in n}

    def box(name):
        ps = [
            acc[p["attributes"]["POSITION"]]
            for p in j["meshes"][mesh_of[name]]["primitives"]
        ]
        return (
            [min(a["min"][i] for a in ps) for i in range(3)],
            [max(a["max"][i] for a in ps) for i in range(3)],
        )

    lo, hi = box("wing.cores.fc5.right")
    assert hi[0] == pytest.approx(164.2, abs=1e-2)  # the shear web face at the tip, FS
    assert hi[1] == pytest.approx(157.0, abs=1e-3)  # the tip rib, BL
    lo, hi = box("wing.cores.fc5.left")
    assert lo[1] == pytest.approx(-157.0, abs=1e-3)  # the left wing is the mirror
    lo, hi = box("wing.aileron.aileron.right")
    assert (lo[1], hi[1]) == (
        pytest.approx(55.5, abs=1e-3),
        pytest.approx(118.1, abs=1e-3),
    )
    lo, hi = box("winglet.cores.upper_core.right")
    assert hi[0] == pytest.approx(196.6, abs=1e-2)  # the top TE corner FS
    assert hi[2] == pytest.approx(48.0, abs=1e-3)  # WL 65.4, model z = WL - 17.4
    lo, hi = box("winglet.rudder.rudder.right")
    assert lo[0] == pytest.approx(176.8, abs=1e-3)  # the rudder hinge FS


def test_m27_layup_section_names_every_part_the_plies_the_axes_and_the_conflicts(
    fuse_export,
):
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"][
        "extras"
    ]["m27"]
    parts, nodes = ex["parts"], ex["nodes"]
    # 32 parts a side (the two winglet skin ply parts have a row of their own, so the lab can name and stripe them), 36 plies a side
    assert len(parts) == 64 and len(nodes) == 72
    assert {n["part"] for n in nodes.values()} <= set(
        parts
    ), "every ply's part has a row"
    assert ex["shear_web"]["zones"] == [
        [23.0, 70.0, 6],
        [70.0, 120.0, 4],
        [120.0, 157.0, 2],
    ]
    assert ex["shear_web"]["outboard_plies_printed"] == 3
    pts = ex["winglet"]["points"]
    assert pts["wprp"][:2] == [149.6, 55.5] and set(pts) == {"wprp", "a", "b", "c"}
    assert {r["fidelity"] for r in parts.values()} == {"representational", "derived"}
    assert all(
        "(fitted shape" in r["label"]
        for r in parts.values()
        if r["fidelity"] == "representational"
    )
    assert all(r["component"] in (M27_WING | M27_WINGLET) for r in parts.values())
    turns = {r["turns"] for r in parts.values() if "turns" in r}
    assert turns == {"aileron", "rudder"}
    assert {r["node"] for r in parts.values() if r.get("workshop")} == {
        "wing.jigs.jigs.right",
        "wing.jigs.jigs.left",
        "winglet.jig.jig_lines.right",
        "winglet.jig.jig_lines.left",
    }
    # the ply schedules: 6 web plies, 5 + 7 caps, 3 + 3 skin plies, 7 corner plies (a side)
    by_op = {}
    for k, v in nodes.items():
        if v["side"] == "right":
            by_op.setdefault(v["op"], []).append(k)
    assert {op: len(ks) for op, ks in by_op.items()} == {
        "f19.shear-web": 6,
        "f19.bottom-cap": 5,
        "f19.top-cap": 7,
        "f19.bottom-skin": 3,
        "f19.top-skin": 3,
        "f20.skins": 5,
        "f20.outside-layups": 7,
    }
    assert nodes["wing.skins.skin_bottom.right.p3"]["cloth"] == "BID"
    assert nodes["winglet.skins.skin_out.right.p3"]["cloth"] == "BID"
    # the aileron and rudder kinematics inputs, and the stops
    a, r = ex["aileron"], ex["rudder"]
    assert a["max_up_deg"] == 20.0 and r["max_deg"] == 30.0
    assert a["axis"][0][:2] == [149.7, 55.5] or a["axis"][0][1] == 55.5
    assert a["inboard_bl"] == 55.5 and a["inboard_bl_p171"] == 54.3
    assert r["hinge_fs"] == 176.8 and r["widths_in"] == [10.0, 12.14, 11.5]
    # the three conflicts are carried as data, never resolved
    c = ex["conflicts"]
    assert c["le_bl_106_25"]["printed_fs"] == 134.95
    assert c["le_bl_106_25"]["derived_fs"] == pytest.approx(134.45)
    assert (
        c["attach_bolt_spacing"]["drawing_in"],
        c["attach_bolt_spacing"]["text_in"],
    ) == (28.85, 28.83)
    w = ex["winglet"]
    assert w["abc_book_in"] == [102.15, 108.35, 118.35]
    assert w["abc_residual_in"][2] == pytest.approx(0.0, abs=1e-3)
    assert abs(w["abc_residual_in"][0]) < 0.1 and abs(w["abc_residual_in"][1]) <= 0.25
    assert w["lean_in"] == pytest.approx(3.58, abs=0.02) and "low" in w["lean_status"]
    assert w["tip_chord_in"] == 11.4 and "not a page value" in w["tip_chord_status"]
    assert ex["weights"]["rows"] == [
        "wing_ch19",
        "wing_complete",
        "aileron",
        "upper_winglet",
        "lower_winglet",
    ]


# ---- M2.8: the strakes, electrical system and engine in the lab export ----
M28_STRAKE = {
    "strake.ribs",
    "strake.baffles",
    "strake.leading_edge",
    "strake.skins",
    "strake.sump",
    "strake.tank",
    "strake.fairing",
    "strake.fittings",
}
M28_ELEC = {
    "elec.battery_shelf",
    "elec.battery",
    "elec.relays",
    "elec.wiring",
    "elec.lights",
    "elec.antennas",
}
M28_ENGINE = {"engine.block", "engine.bracket", "engine.cowl", "engine.rib"}


def test_m28_components_are_group_nodes_with_a_child_per_part_and_side(fuse_export):
    j = _glb_json(fuse_export)
    names = {n["name"] for n in j["nodes"]}
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    parent = _parents(j)
    assert M28_STRAKE | M28_ELEC | M28_ENGINE <= names
    graph = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    assert M28_STRAKE | M28_ELEC | M28_ENGINE <= set(graph.components)
    for cid, kid in (
        ("strake.ribs", "strake.ribs.rib_r23.right"),
        ("strake.ribs", "strake.ribs.rib_r45.left"),
        ("strake.baffles", "strake.baffles.od.right"),
        ("strake.skins", "strake.skins.skin_top.left"),
        ("strake.skins", "strake.skins.cutout_tank.right"),
        ("strake.tank", "strake.tank.tank.right"),
        ("strake.fittings", "strake.fittings.fuel_cap.left"),
        ("elec.battery", "elec.battery.battery"),
        ("elec.wiring", "elec.wiring.panel_bundle"),
        ("elec.lights", "elec.lights.light_left"),
        ("elec.antennas", "elec.antennas.comm_strips"),
        ("engine.block", "engine.block.block"),
        ("engine.rib", "engine.rib.rib_left"),
    ):
        assert parent[idx[kid]] == cid, kid
    assert all(
        "mesh" in j["nodes"][idx[n]]
        for n in names
        if n.startswith(("strake.", "elec.", "engine.")) and n.count(".") >= 2
    )
    # no part of chapters 21 to 23 is workshop geometry
    assert not [
        n["name"]
        for n in j["nodes"]
        if n["name"].startswith(("strake.", "elec.", "engine."))
        and n.get("extras", {}).get("workshop")
    ]


def test_m28_nodes_sit_in_the_airframe_frame_in_inches(fuse_export):
    j = _glb_json(fuse_export)
    acc = j["accessors"]
    mesh_of = {n["name"]: n["mesh"] for n in j["nodes"] if "mesh" in n}

    def box(name):
        ps = [
            acc[p["attributes"]["POSITION"]]
            for p in j["meshes"][mesh_of[name]]["primitives"]
        ]
        return (
            [min(a["min"][i] for a in ps) for i in range(3)],
            [max(a["max"][i] for a in ps) for i in range(3)],
        )

    lo, hi = box("strake.skins.skin_top.right")
    assert lo[0] == pytest.approx(50.4, abs=0.1)  # the LE at the fuselage side, FS 50
    assert hi[1] == pytest.approx(54.6, abs=0.05)  # the skin's outboard edge
    assert hi[2] == pytest.approx(
        21.6 + 0.35 - 17.4, abs=1e-3
    )  # top outside plane, model z = WL - 17.4
    lo, hi = box("strake.skins.skin_top.left")
    assert lo[1] == pytest.approx(-54.6, abs=0.05)  # the left strake is the mirror
    lo, hi = box("strake.ribs.rib_r45.right")
    assert (lo[1], hi[1]) == (
        pytest.approx(44.825, abs=1e-3),
        pytest.approx(45.175, abs=1e-3),
    )
    lo, hi = box("elec.relays.start_relay")
    assert hi[0] == pytest.approx(22.0)  # the front face of F22
    lo, hi = box("elec.battery.battery")
    assert (lo[0] + hi[0]) / 2 == pytest.approx(11.0)  # the illustration station
    lo, hi = box("engine.block.block")
    assert lo[0] > 125.28 and (lo[1], hi[1]) == (
        pytest.approx(-16.0),
        pytest.approx(16.0),
    )
    lo, hi = box("engine.cowl.cowl")
    assert hi[0] == pytest.approx(148.4)  # the wing TE at the root


def test_m28_layup_section_names_every_part_the_conflicts_and_the_reference_weights(
    fuse_export,
):
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"][
        "extras"
    ]["m28"]
    parts = ex["parts"]
    # 20 strake parts a side, 15 electrical parts, 5 engine parts
    assert len(parts) == 20 * 2 + 15 + 5
    assert {
        r["component"] for r in parts.values()
    } == M28_STRAKE | M28_ELEC | M28_ENGINE
    assert {r["fidelity"] for r in parts.values()} == {"representational", "derived"}
    assert all(
        "(fitted shape" in r["label"]
        for r in parts.values()
        if r["fidelity"] == "representational"
    )
    assert all(
        r["show"]["from"]
        in {
            o
            for o in load_graph(
                Path(__file__).resolve().parents[2] / "guide" / "graph"
            ).ops
        }
        for r in parts.values()
    )
    assert {r["node"] for r in parts.values() if r.get("void")} == {
        f"strake.skins.{n}.{s}"
        for n in ("cutout_baggage", "cutout_tank")
        for s in ("right", "left")
    }
    assert {r["node"] for r in parts.values() if r.get("pocket")} >= {
        "elec.battery.battery",
        "elec.relays.start_relay",
    }
    assert all(
        r["side"] in ("right", "left")
        for r in parts.values()
        if r["component"].startswith("strake.")
    )
    # the fuel capacity conflict is carried as data and as text
    f = ex["fuel"]
    assert (f["plans_gal_per_tank"], f["om_gal_per_tank"], f["om_total_gal"]) == (
        25.5,
        28.0,
        52.0,
    )
    assert f["model_gal_per_side"] == 26.0 and 22.0 < f["envelope_gal_per_side"] < 28.0
    assert "conflict" in f["note"] and f["arm_fs"] == 104.5 and f["lb_per_gal"] == 6.0
    assert ex["conflicts"]["cutout_aft_top_depth"] == {"mid_in": 1.4, "aft_end_in": 1.9}
    b = ex["battery"]
    assert b["fs_range"] == [0.0, 22.0] and b["model_fs"] == 11.0
    assert "illustration only" in b["status"] and "A6" in b["status"]
    e = ex["engine"]
    assert e["down_thrust_deg"] == 2.0 and e["limits_lb"] == [246.0, 286.0]
    assert e["oil"] == {"lb": 8.0, "fs": 140.0} and e["striped"] == [
        "engine.block.block"
    ]
    assert "not held" in e["note"]
    w = ex["weights"]
    assert w["rows"][:8] == [f"n26ms_empty_{i}" for i in range(1, 9)]
    assert w["rows"][8:] == ["dynafocal_mount", "cowl_glass", "cowl_graphite"]
    c = w["closure_target"]
    assert (c["empty_lb"], c["empty_arm_in"]) == (730, 111.7) and c[
        "loaded_envelope_fs"
    ] == [97.0, 103.0]
    assert "not the empty CG" in c["note"] and w["cg"] == "not yet computed"


def test_m28_adds_no_ledger_sum_the_cg_stays_not_yet_computed(fuse_export):
    led = json.loads((fuse_export.parent / "ledger.json").read_text())
    assert led["cg"]["arm_in"] is None and led["cg"]["weight_lb"] == 0.0
    rows = led["prototype_weights"]["rows"]
    assert {f"n26ms_empty_{i}" for i in range(1, 9)} | {
        "dynafocal_mount",
        "cowl_glass",
        "cowl_graphite",
    } <= set(rows)
    for cg in (led["cg"], led["cg_lower_bound"]):
        new = {f"n26ms_empty_{i}" for i in range(1, 9)} | {
            "dynafocal_mount",
            "cowl_glass",
            "cowl_graphite",
        }
        assert not [k for k in new if k in cg["included"] + list(cg["excluded"])]


# ---- Block 2 M2.9: chapters 24 and 26 in the lab export; the chapter 25 finish as tags in layup.json ----
M29_COVERS = {
    "cover.aft",
    "cover.console_lc1",
    "cover.consoles",
    "cover.thigh",
    "cover.valve",
    "cover.canard",
    "cover.seal",
}
M29_UPH = {"upholstery.cushions", "upholstery.headrests", "upholstery.suitcases"}


def test_m29_components_are_group_nodes_with_a_child_per_part(fuse_export):
    j = _glb_json(fuse_export)
    names = {n["name"] for n in j["nodes"]}
    idx = {n["name"]: i for i, n in enumerate(j["nodes"])}
    parent = _parents(j)
    assert M29_COVERS | M29_UPH <= names
    graph = load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph")
    assert M29_COVERS | M29_UPH <= set(graph.components)
    for cid, kid in (
        ("cover.aft", "cover.aft.aft_cover"),
        ("cover.console_lc1", "cover.console_lc1.lc1"),
        ("cover.consoles", "cover.consoles.lc4"),
        ("cover.thigh", "cover.thigh.thigh_rib_a"),
        ("cover.valve", "cover.valve.valve_cover"),
        ("cover.canard", "cover.canard.canard_cover"),
        ("cover.seal", "cover.seal.seal_left"),
        ("upholstery.cushions", "upholstery.cushions.rear_cushion"),
        ("upholstery.headrests", "upholstery.headrests.front_headrest"),
        ("upholstery.suitcases", "upholstery.suitcases.suitcase_left"),
    ):
        assert parent[idx[kid]] == cid, kid
    assert all(
        "mesh" in j["nodes"][idx[n]]
        for n in names
        if n.startswith(("cover.", "upholstery.")) and n.count(".") >= 2
    )
    assert not [
        n["name"]
        for n in j["nodes"]
        if n["name"].startswith(("cover.", "upholstery."))
        and n.get("extras", {}).get("workshop")
    ]


def test_m29_nodes_sit_in_the_airframe_frame_in_inches(fuse_export):
    j = _glb_json(fuse_export)
    acc = j["accessors"]
    mesh_of = {n["name"]: n["mesh"] for n in j["nodes"] if "mesh" in n}

    def box(name):
        ps = [
            acc[p["attributes"]["POSITION"]]
            for p in j["meshes"][mesh_of[name]]["primitives"]
        ]
        return (
            [min(a["min"][i] for a in ps) for i in range(3)],
            [max(a["max"][i] for a in ps) for i in range(3)],
        )

    lo, hi = box("cover.console_lc1.lc1")
    assert (lo[0], hi[0]) == (
        pytest.approx(52.0, abs=1e-3),
        pytest.approx(60.0, abs=1e-3),
    )
    assert hi[2] == pytest.approx(11.6 - 17.4, abs=1e-3)  # WL 11.6, model z = WL - 17.4
    assert hi[1] < 0  # the consoles are on the left
    lo, hi = box("cover.aft.aft_cover")
    assert lo[0] == pytest.approx(107.4, abs=1e-3) and hi[0] <= 125.0 + 1e-3
    lo, hi = box("upholstery.suitcases.suitcase_right")
    assert hi[2] - lo[2] == pytest.approx(18.0, abs=1e-3)


def test_m29_layup_section_names_every_part_the_finish_the_conflicts_and_the_reference_weights(
    fuse_export,
):
    ex = json.loads((fuse_export.parent / "layup.json").read_text())["fuselage"][
        "extras"
    ]["m29"]
    parts = ex["parts"]
    assert len(parts) == 14 + 6
    assert {r["component"] for r in parts.values()} == M29_COVERS | M29_UPH
    assert {r["fidelity"] for r in parts.values()} == {"book", "representational"}
    assert [r["node"] for r in parts.values() if r["fidelity"] == "book"] == [
        "cover.console_lc1.lc1"
    ]
    assert all(
        "(fitted shape" in r["label"]
        for r in parts.values()
        if r["fidelity"] == "representational"
    )
    ops = set(load_graph(Path(__file__).resolve().parents[2] / "guide" / "graph").ops)
    assert all(r["show"]["from"] in ops for r in parts.values())
    # the finish: a tag per surface, white only on the upper wing and canard, no weight
    f = ex["finish"]
    white = {r["component"] for r in f["rows"] if r["final_colour"] == "white"}
    assert white == {"wing.skins", "canard.skin_top", "cover.canard"}
    assert {r["final_colour"] for r in f["rows"]} == {"white", "primer-grey"}
    assert f["min_temp_f"] == 70.0 and "never a solid" in f["note"]
    assert "no finish weight" in f["note"]
    # conflicts and references
    c = ex["conflicts"]
    assert c["aft_cover_plies"]["scan_inside_outside"] == [1, 1]
    assert c["aft_cover_plies"]["transcription_inside_outside"] == [1, 2]
    assert (c["lc2_length_in"]["scan"], c["lc2_length_in"]["transcription"]) == (
        30.6,
        30.8,
    )
    assert (ex["seal"]["gap_in"], ex["seal"]["front_gap_in"]) == (0.5, 0.0625)
    w = ex["weights"]
    assert {k: v["weight_lb"] for k, v in w["finish_deltas"].items()} == {
        "finish_delta_canopy": 1.0,
        "finish_delta_aileron": 0.275,
        "finish_delta_wing": 2.2,
    }
    assert (
        "never summed" in w["note"] and "No upholstery weight is printed" in w["note"]
    )
    t = w["closure_target"]
    assert (t["empty_lb"], t["empty_arm_in"]) == (730, 111.7)
    assert t["loaded_envelope_fs"] == [97.0, 103.0]
    assert (
        "103.96" in t["samples"]
        and "outside" in t["samples"]
        and "101.06" in t["samples"]
    )
    assert "not the empty CG" in t["note"] and w["cg"] == "not yet computed"


def test_m29_adds_no_ledger_sum_the_finish_rows_are_references(fuse_export):
    led = json.loads((fuse_export.parent / "ledger.json").read_text())
    assert led["cg"]["arm_in"] is None and led["cg"]["weight_lb"] == 0.0
    new = {
        "finish_delta_canopy",
        "finish_delta_aileron",
        "finish_delta_wing",
        "wing_painted",
    }
    assert new <= set(led["prototype_weights"]["rows"])
    for cg in (led["cg"], led["cg_lower_bound"]):
        assert not [k for k in new if k in cg["included"] + list(cg["excluded"])]
