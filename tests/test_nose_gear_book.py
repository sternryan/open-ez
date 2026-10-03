"""M2.4 Task 4: the retracting nose gear (chapter 13) as geometry: both axle candidates, the pose, the ledger pair, the export ids."""

import json
import math

import cadquery as cq
import numpy as np
import pytest

from core import landing_gear_book as lg
from core import nose_book as nb
from core.fuselage_book import FIDELITIES, z_of_wl
from core.sources import check_citation

G = lg.G
CANDS = (("plans", 17.0), ("manual", 20.0))


@pytest.mark.parametrize("cand,fs", CANDS)
def test_every_nose_gear_part_is_valid_and_never_book_or_derived(cand, fs):
    parts = lg.build_nose_gear(cand)
    assert set(parts) == {"ng6_block", "strut", "fork", "wheel"}
    for name, p in parts.items():
        assert p.fidelity in FIDELITIES and p.note, name
        assert (
            p.fidelity == "representational"
        ), name  # the axle station is a conflict; the pivot is solved from it
        for c in p.cite:
            check_citation(c)
        assert p.solid.val().isValid() and p.solid.val().Volume() > 0, name
    assert "conflict" in parts["wheel"].note and "SOLVED" in parts["ng6_block"].note
    assert (
        "zero fork offset" in parts["strut"].note
        and "not a measurement" in parts["ng6_block"].note
    )


@pytest.mark.parametrize("cand,fs", CANDS)
def test_strut_is_25_5_pivot_to_axle_and_axle_is_on_the_candidate(cand, fs):
    pts = lg.nose_gear_points(cand)
    pivot, axle = np.array(pts["pivot"]), np.array(pts["axle"])
    assert (
        np.linalg.norm(axle - pivot)
        == pytest.approx(25.5, abs=1e-9)
        == pytest.approx(G.nose_strut_pivot_to_pivot_in)
    )
    assert axle[2] == pytest.approx(z_of_wl(-22.0)) and axle[0] == pytest.approx(fs)
    assert abs(pivot[1]) <= 1.5  # between the NG30 plates
    assert pivot[0] < axle[0]
    # the solved pivot sits inside the nose, forward of F22 and aft of NG31
    assert nb.FITTED_FS_NG31 < pivot[0] < G.fs_f22
    # the wheel solid is centred on the axle
    c = lg.build_nose_gear(cand)["wheel"].solid.val().Center()
    assert (c.x, c.y, c.z) == pytest.approx(tuple(axle), abs=1e-6)
    # the strut and fork solids span pivot to axle along the strut line
    bb = lg.build_nose_gear(cand)["strut"].solid.val().BoundingBox()
    assert bb.xmin < pivot[0] + 0.6 and bb.zmax >= pivot[2] - 0.3


def test_ng6_block_is_2_75_wide_between_the_plates_with_the_bore_1_25_above_the_base():
    for cand, _ in CANDS:
        bb = lg.build_nose_gear(cand)["ng6_block"].solid.val().BoundingBox()
        pts = lg.nose_gear_points(cand)
        assert bb.ymax - bb.ymin == pytest.approx(G.ng6_width_in)
        assert bb.ymax <= G.ng30_gap_in / 2 and bb.ymin >= -G.ng30_gap_in / 2
        assert pts["pivot"][2] - bb.zmin == pytest.approx(G.ng6_bore_height_in)
        assert bb.zmin == pytest.approx(
            nb.NOSE_BOTTOM_Z
        )  # the plate base is the skin line


@pytest.mark.parametrize("cand,fs", CANDS)
def test_retraction_pose_identity_at_0_and_retracted_forward_of_the_panel_and_clear_of_the_skin_at_1(
    cand, fs
):
    assert np.allclose(lg.nose_gear_pose(0.0, cand), np.eye(4))
    m = lg.nose_gear_pose(1.0, cand)
    pts = lg.nose_gear_points(cand)
    pivot, axle = np.array(pts["pivot"]), np.array(pts["axle"])
    up = m @ np.append(axle, 1.0)
    th = math.radians(lg.nose_retracted_theta_deg(cand))
    assert th > math.pi / 2  # tilted up from flat so the tire clears the skin
    assert up[2] == pytest.approx(pivot[2] - 25.5 * math.cos(th), abs=1e-9)
    assert up[0] == pytest.approx(pivot[0] + 25.5 * math.sin(th), abs=1e-9)
    assert (
        up[2] - lg.FITTED_TIRE_OD / 2 >= nb.NOSE_BOTTOM_Z - 1e-6
    )  # the tire clears the skin line
    assert up[0] < G.fs_panel  # wheel centre stays forward of the panel
    assert np.allclose(
        m @ np.append(pivot, 1.0), np.append(pivot, 1.0)
    )  # the pivot does not move
    # on the solids: no part of the strut or fork gets aft of the panel
    gear = lg.build_nose_gear(cand)
    for n in ("strut", "fork", "wheel"):
        sol = gear[n].solid.val().transformGeometry(cq.Matrix(m[:3, :4].tolist()))
        bb = sol.BoundingBox()
        assert bb.xmax < G.fs_panel + 0.01 or n == "wheel", n
    # a rigid motion at the midpoint, and monotonic
    mid = lg.nose_gear_pose(0.5, cand)
    assert np.allclose(mid[:3, :3] @ mid[:3, :3].T, np.eye(3)) and np.linalg.det(
        mid[:3, :3]
    ) == pytest.approx(1.0)
    xs = [(lg.nose_gear_pose(t / 4, cand) @ np.append(axle, 1.0))[0] for t in range(5)]
    assert xs == sorted(xs)
    with pytest.raises(ValueError):
        lg.nose_gear_pose(1.5, cand)
    with pytest.raises(ValueError):
        lg.nose_gear_points("nonsense")


def test_the_two_candidates_differ_only_by_the_axle_station():
    a, b = lg.nose_gear_points("plans"), lg.nose_gear_points("manual")
    assert b["axle"][0] - a["axle"][0] == pytest.approx(3.0)
    assert b["pivot"][0] - a["pivot"][0] == pytest.approx(3.0)
    assert a["theta_down_deg"] == pytest.approx(b["theta_down_deg"])


def test_main_gear_parts_are_unchanged():
    assert set(lg.build_gear()) == {
        "strut",
        "extrusions",
        "gear_tubes",
        "jig_blocks",
        "datum_board",
        "axles",
    }


def test_ledger_carries_the_nose_arm_pair_and_moves_nothing():
    from core.ledger import fuselage_ledger_json, gear_rows

    g = fuselage_ledger_json()["gear"]
    assert (
        g["nose_arm_candidates"] == [17.0, 20.0]
        and g["nose_arm_candidates_status"] == "conflict"
    )
    row = next(r for r in g["rows"] if r["name"] == "nose_strut")
    assert (
        row["arm_in"] == 17.0
        and row["nose_arm_candidates"] == [17.0, 20.0]
        and row["arm_status"] == "conflict"
    )
    assert [r.name for r in gear_rows()] == [
        "main_strut",
        "nose_strut",
        "wheels_brakes_tyres_axles",
    ]  # no mass added
    json.dumps(g)


def test_nose_components_keys_and_canard_only_export_has_none():
    from guide import export_glb as eg

    ids = set(eg.nose_components())
    assert ids == {
        "gear.nose_strut",
        "nose.ng_hardware",
        "nose.ng30_plates",
        "nose.ng31",
        "nose.floor_blocks",
        "nose.pivot_blocks",
        "nose.side_blocks",
        "nose.pedals",
        "nose.pitot",
        "nose.static_port",
        "nose.top_block",
        "nose.strut_cover",
        "nose.nb_box",
        "nose.skin",
        "nose.door",
    }
    assert "nose.worm_drive" not in ids  # no geometry
    for k in eg.canard_components():
        assert not (k.startswith("nose.") or k == "gear.nose_strut")
    import inspect

    assert (
        "nose_components()" in inspect.getsource(eg.default_components)
    )  # the lab's fuselage subject shows them (M2.4 Task 5; tests/guide/test_export_glb.py builds the export)


def test_nose_export_writes_one_node_per_graph_id(tmp_path):
    from guide import export_glb as eg

    out = eg.export_components(eg.nose_components(), tmp_path / "n.glb")
    names = set(eg.read_glb_node_names(out))
    assert set(eg.nose_components()) <= names
