"""M2.4 Task 4: the nose structure forward of F22 (plans-1980:p73-p83, p171): sizes, fidelity tags, no overlaps, export ids."""

import pytest

from core import nose_book as nb
from core.fuselage_book import FIDELITIES, half_width, z_of_wl
from core.nose_book import G
from core.sources import check_citation


@pytest.fixture(scope="module")
def parts():
    return nb.build_nose()


def _bb(p):
    return p.solid.val().BoundingBox()


def test_every_part_is_valid_tagged_and_cited(parts):
    assert set(parts) == {
        "skin",
        "ng30_plates",
        "ng31_disc",
        "f6_plate",
        "floor_blocks",
        "side_blocks",
        "top_block",
        "pivot_blocks",
        "pedals",
        "pitot",
        "static_port",
        "strut_cover",
        "nb_box",
        "door",
    }
    for name, p in parts.items():
        assert p.fidelity in FIDELITIES, name
        assert p.note, name
        if p.fidelity in {"book", "derived"}:
            assert p.cite, name
        for c in p.cite:
            check_citation(c)
        assert p.solid.val().isValid(), name
        assert p.solid.val().Volume() > 0, name
    # every outline is template-only or fitted: nothing forward of F22 is book or derived
    assert {p.fidelity for p in parts.values()} == {"representational"}


def test_ng30_plates_are_the_printed_thickness_and_gap_ending_on_f22(parts):
    sol = parts["ng30_plates"].solid.val().Solids()
    assert len(sol) == 2
    for s in sol:
        bb = s.BoundingBox()
        assert (
            bb.ymax - bb.ymin
            == pytest.approx(G.ng30_thickness_in, abs=1e-6)
            == pytest.approx(0.2, abs=1e-6)
        )
        assert bb.xmax == pytest.approx(G.fs_f22, abs=1e-6)
        assert bb.zmin == pytest.approx(
            nb.NOSE_BOTTOM_Z
        )  # bottom edge on the skin line
    inner = sorted(
        abs(y) for s in sol for y in (s.BoundingBox().ymin, s.BoundingBox().ymax)
    )
    assert inner[0] == pytest.approx(1.5, abs=1e-6) and inner[1] == pytest.approx(
        1.5, abs=1e-6
    )  # 3.0 between
    assert sol[0].Center().y * sol[1].Center().y < 0


def test_ng31_is_one_fitted_station_inside_the_printed_range(parts):
    assert G.fs_ng31_min <= nb.FITTED_FS_NG31 <= G.fs_ng31_max
    assert nb.FITTED_FS_NG31 == pytest.approx((G.fs_ng31_min + G.fs_ng31_max) / 2)
    assert _bb(parts["ng30_plates"]).xmin == pytest.approx(nb.FITTED_FS_NG31, abs=1e-6)
    assert _bb(parts["ng31_disc"]).xmin == pytest.approx(nb.FITTED_FS_NG31, abs=1e-6)
    note = parts["ng31_disc"].note
    assert "range" in note and "cobelu" in note and "NOT on the owner's scan" in note


def test_floor_block_is_the_printed_wedge(parts):
    sol = parts["floor_blocks"].solid.val().Solids()
    assert len(sol) == 2
    for s in sol:
        bb = s.BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(
            G.floor_block_length_in, abs=0.01
        )  # 20.9
        assert bb.ymax - bb.ymin == pytest.approx(
            G.floor_block_width_in, abs=0.01
        )  # 8.2 at the F22 end (the maximum)
        assert bb.zmax - bb.zmin == pytest.approx(
            G.floor_block_thickness_in, abs=0.01
        )  # 1.6
        assert bb.xmax == pytest.approx(G.fs_f22, abs=0.01)
    # a wedge: the NG31 end is 1.6 wide (cut the solid just inside each end)
    import cadquery as cq

    s = next(x for x in sol if x.Center().y > 0)
    probe = (
        cq.Workplane("XY").box(0.2, 40, 40).translate((G.fs_ng31_max + 0.1, 0, 0)).val()
    )
    bb = cq.Workplane(obj=s).intersect(cq.Workplane(obj=probe)).val().BoundingBox()
    assert bb.ymax - bb.ymin == pytest.approx(G.floor_block_thickness_in, abs=0.3)


def test_side_block_is_21_9_long_and_15_6_high_at_f22(parts):
    for s in parts["side_blocks"].solid.val().Solids():
        bb = s.BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(
            G.side_block_length_in, abs=0.01
        )  # 21.9
        assert bb.xmax == pytest.approx(G.fs_f22, abs=0.01)
        # height at the F22 end: the nose top over the skin line
        assert nb.nose_height(G.fs_f22) == pytest.approx(G.side_block_height_f22_in)
        assert nb.nose_height(nb.FITTED_FS_NG31) == pytest.approx(
            G.side_block_height_ng31_above_in + G.side_block_height_ng31_below_in
        )
        assert bb.zmin == pytest.approx(nb.NOSE_BOTTOM_Z)
        assert bb.zmax == pytest.approx(
            nb.NOSE_BOTTOM_Z + G.side_block_height_f22_in, abs=1e-3
        )


def test_top_block_is_19_3_long_19_6_aft_7_0_forward(parts):
    import cadquery as cq

    s = parts["top_block"].solid.val()
    bb = s.BoundingBox()
    assert bb.xmax - bb.xmin == pytest.approx(G.top_block_length_in, abs=0.01)
    assert bb.xmax == pytest.approx(G.fs_f22, abs=0.01)
    assert bb.ymax - bb.ymin == pytest.approx(G.top_block_width_aft_in, abs=0.01)
    for x, want in (
        (bb.xmax - 0.05, G.top_block_width_aft_in),
        (bb.xmin + 0.05, G.top_block_width_fwd_in),
    ):
        probe = cq.Workplane("XY").box(0.02, 60, 60).translate((x, 0, 0)).val()
        b = cq.Workplane(obj=s).intersect(cq.Workplane(obj=probe)).val().BoundingBox()
        assert b.ymax - b.ymin == pytest.approx(want, abs=0.35)  # slope over 0.05 in


def test_nose_skin_reaches_the_printed_tip(parts):
    assert (
        _bb(parts["skin"]).xmin
        == pytest.approx(G.fs_nose, abs=0.05)
        == pytest.approx(-6.8, abs=0.05)
    )
    assert _bb(parts["skin"]).xmax == pytest.approx(G.fs_f22, abs=0.05)
    assert (
        "representational" == parts["skin"].fidelity
        and "not to scale" in parts["skin"].note
    )


def test_static_port_is_on_the_left_outer_skin_at_the_printed_station(parts):
    c = parts["static_port"].solid.val().Center()
    assert (
        c.x
        == pytest.approx(G.fs_static_port, abs=0.01)
        == pytest.approx(31.75, abs=0.01)
    )
    assert c.z == pytest.approx(z_of_wl(13.0), abs=0.01)
    assert c.y < 0  # left
    assert (
        abs(c.y) > half_width(G.fs_static_port) + G.side_panel_thickness - 0.01
    )  # on the outer face


def test_no_large_overlap_between_plates_and_floor_blocks_or_each_other(parts):
    vol = (
        parts["ng30_plates"].solid.intersect(parts["floor_blocks"].solid).val().Volume()
    )
    assert vol < 1.0
    pairs = [
        ("floor_blocks", "side_blocks"),
        ("top_block", "side_blocks"),
        ("top_block", "ng30_plates"),
        ("floor_blocks", "pivot_blocks"),
    ]
    for a, b in pairs:
        assert parts[a].solid.intersect(parts[b].solid).val().Volume() < 1.0, (a, b)


def test_pedals_sit_6_1_from_ng30_and_pitot_is_a_quarter_inch_rod(parts):
    ys = sorted(abs(s.Center().y) for s in parts["pivot_blocks"].solid.val().Solids())
    assert ys[0] == pytest.approx(1.7 + G.pedal_block_from_ng30_in, abs=0.01)
    pb = _bb(parts["pitot"])
    assert pb.ymax - pb.ymin == pytest.approx(0.25, abs=1e-3)
    assert pb.xmin == pytest.approx(
        nb.FITTED_FS_NG31 - 6.0, abs=0.01
    )  # about 6 in forward of NG31


def test_nothing_in_the_nose_is_tagged_for_the_axle_station(parts):
    # the nose structure never carries a nose-wheel station; the notes say what is printed and what is fitted
    for p in parts.values():
        assert p.fidelity == "representational"
    assert (
        "fitted" in parts["ng30_plates"].note.lower()
        and "printed" in parts["ng30_plates"].note.lower()
    )


def test_component_parts_cover_every_nose_id_but_the_worm_drive():
    from pathlib import Path

    from guide.schema import load_graph

    g = load_graph(Path(nb.__file__).resolve().parents[1] / "guide" / "graph")
    nose_ids = {c for c in g.components if c.startswith("nose.")}
    assert set(nb.COMPONENT_PARTS) == nose_ids - {"nose.worm_drive", "nose.ng_hardware"}
    for cid in nb.COMPONENT_PARTS:
        assert g.components[cid].fidelity == "unvalidated", cid
    assert g.components["nose.worm_drive"].fidelity == "no-geometry"
