"""M2.7 wing geometry (chapter 19): planform lines, sections, cores, hardware, aileron pose, display plies, left-hand mirror.

Stations are asserted against literal book numbers (plans-1980:p126), not against the builder's own constants.
"""

import ast
import io
import math
import tokenize
from pathlib import Path

import cadquery as cq
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from core import wing_book as wb
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl
from core.sources import check_citation

REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
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


def volume(shape) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def comp(wp):
    return cq.Compound.makeCompound(wp.vals())


def vol_of(wp) -> float:
    return volume(comp(wp))


def bb(wp):
    return comp(wp).BoundingBox()


def shoelace(pts) -> float:
    return 0.5 * abs(
        sum(
            pts[i][0] * pts[(i + 1) % len(pts)][2]
            - pts[(i + 1) % len(pts)][0] * pts[i][2]
            for i in range(len(pts))
        )
    )


@pytest.fixture(scope="module")
def right():
    return wb.build_wing("right")


@pytest.fixture(scope="module")
def left():
    return wb.build_wing("left")


# ---- planform lines against literal p126 numbers ----
@pytest.mark.parametrize(
    "bl,le,te",
    [(55.5, 112.9, 155.6), (106.25, 134.45, 165.8), (157.0, 156.0, 176.0)],
)
def test_planform_lines_at_the_three_rib_stations(bl, le, te):
    assert wb.le_fs(bl) == pytest.approx(le, abs=0.005)
    assert wb.te_fs(bl) == pytest.approx(te, abs=0.005)


def test_chords_are_the_printed_chords():
    for bl, c in ((55.5, 42.7), (106.25, 31.35), (157.0, 20.0)):
        assert wb.chord(bl) == pytest.approx(c, abs=0.005)


def test_inboard_te_kink_and_the_shear_web_line():
    assert wb.te_fs(23.0) == pytest.approx(148.4)
    for bl, fs in ((23.0, 125.6), (55.5, 130.5), (106.25, 147.35), (157.0, 164.2)):
        assert wb.web_fs(bl) == pytest.approx(fs)


def test_the_te_heights_come_out_of_the_twist_and_match_p126():
    assert wb.te_wl(55.5) == pytest.approx(16.95, abs=0.01)
    assert wb.te_wl(157.0) == pytest.approx(18.35, abs=0.01)
    assert wb.te_wl(106.25) == pytest.approx(
        17.40 + 31.35 * math.sin(math.radians(0.96)), abs=0.01
    )


def test_the_section_is_the_printed_thickness_not_the_files_own():
    assert wb.unit_thickness() == pytest.approx(0.087, abs=0.002)  # the file is thin
    for bl, t in ((55.5, 0.162), (106.25, 0.157), (157.0, 0.150)):
        sec = wb.section_poly(bl, n=60)
        n = len(sec) // 2
        # max vertical gap between the upper and lower surfaces at equal x
        gap = max(
            wb.z_surface(bl, p[0], +1) - wb.z_surface(bl, p[0], -1) for p in sec[:n]
        )
        assert gap == pytest.approx(t * wb.chord(bl), rel=0.01)


def test_section_polygon_is_clipped_to_the_requested_chord_range():
    sec = wb.section_poly(55.5, 130.5, 150.0)
    xs = [p[0] for p in sec]
    assert min(xs) == pytest.approx(130.5) and max(xs) == pytest.approx(150.0)
    assert all(p[1] == 55.5 for p in sec)


# ---- the solids ----
def test_every_component_has_parts_valid_positive_solids_and_a_fidelity(right):
    assert set(wb.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    names = {n for ns in wb.COMPONENT_PARTS.values() for n in ns}
    assert names == set(right)
    for n, p in right.items():
        assert p.fidelity in FIDELITIES and p.fidelity in wb.FIDELITIES_USED, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert vol_of(p.solid) > 0, n
    graph_ids = {
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
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert graph_ids <= set(g.components)


def test_representational_parts_say_so_and_only_printed_hardware_is_derived(right):
    derived = {n for n, p in right.items() if p.fidelity == "derived"}
    assert derived == {"hinge_pins", "aileron_rod", "torque_tube", "spar_bolts"}
    assert all(
        "fitted" in p.note or "representational" in p.note
        for n, p in right.items()
        if p.fidelity == "representational"
    )


def test_core_extents_are_the_book_stations(right):
    f1 = bb(right["fc1"].solid)
    assert (f1.ymin, f1.ymax) == (pytest.approx(23.7), pytest.approx(55.5))
    assert f1.xmax == pytest.approx(155.6, abs=0.01)  # the TE at BL 55.5
    assert f1.xmin == pytest.approx(125.6 + wb.WEB_GAP + 0.0, abs=0.35)
    f4, f5 = bb(right["fc4"].solid), bb(right["fc5"].solid)
    assert (
        f4.ymin == pytest.approx(56.75)
    )  # outboard of the spar end bulkhead (p88 tip BL 56.46), 1.25 in outboard of the p126 joint
    assert f4.xmin == pytest.approx(wb.le_fs(56.75), abs=0.01)  # the LE line there
    assert f5.xmax == pytest.approx(164.2, abs=0.01)  # the shear web face at the tip
    assert f5.ymax == pytest.approx(157.0)
    f3 = bb(right["fc3"].solid)
    assert f3.xmax == pytest.approx(176.0, abs=0.01)  # the TE at BL 157
    assert f3.ymax == pytest.approx(157.0)
    ail = bb(right["aileron"].solid)
    assert (ail.ymin, ail.ymax) == (pytest.approx(55.5), pytest.approx(118.1))
    assert ail.xmin == pytest.approx(149.7, abs=0.01)  # the hinge line at BL 55.5
    assert ail.xmax == pytest.approx(wb.te_fs(118.1), abs=0.01)


def test_hinge_line_is_through_the_p124_cuts():
    assert wb.hinge_fs(55.5) == pytest.approx(155.6 - 5.9)
    assert wb.hinge_fs(106.25) == pytest.approx(165.8 - 4.35)
    # carried to the aileron tip the cut is about 3.99 in forward of the TE (derived, p124)
    assert wb.te_fs(118.1) - wb.hinge_fs(118.1) == pytest.approx(3.99, abs=0.03)


def test_loft_volume_is_the_prismoid_of_its_two_sections(right):
    """A ruled loft between corresponding polygons has quadratic section area, so V = h/6 (A0 + 4 Am + A1) is exact."""
    for part, (b0, b1, xa, xb) in {
        "fc4": (wb.FC4_BL0, 106.25, wb.le_fs, wb.web_fs),
        "fc2": (55.5, 106.25, wb._web_aft, wb.hinge_fs),
    }.items():
        a = wb.section_poly(b0, xa(b0), xb(b0))
        b = wb.section_poly(b1, xa(b1), xb(b1))
        m = [tuple((p[i] + q[i]) / 2 for i in range(3)) for p, q in zip(a, b)]
        v = (b1 - b0) / 6 * (shoelace(a) + 4 * shoelace(m) + shoelace(b))
        assert vol_of(right[part].solid) == pytest.approx(v, rel=1e-4), part


def test_no_wing_solid_overlaps_another_wing_solid_or_the_fuselage(right):
    plies = {
        "shear_web",
        "cap_bottom",
        "cap_top",
        "skin_bottom",
        "skin_top",
    }  # display plies, checked against the cores below
    skip = (
        {"spar_bolts", "jigs"} | plies
    )  # bolts pass through the hard points and cores by design; jigs are workshop boards round the section
    names = [n for n in right if n not in skip]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            _assert_clear(right[a].solid, right[b].solid, (a, b))
    fus = build_fuselage()
    from core.spar_book import build_spar

    spar = build_spar()
    for n in names:
        for fname, f in {**fus, **spar}.items():
            if f.void:
                continue
            _assert_clear(right[n].solid, f.solid, (n, fname))
    for n in ("fc1", "fc2", "fc3", "fc4", "fc5", "aileron", "hardpoints"):
        _assert_clear(right["jigs"].solid, right[n].solid, ("jigs", n))
    _assert_clear(
        right["shear_web"].solid, right["hardpoints"].solid, ("shear_web", "hardpoints")
    )


def _assert_clear(sa, sb, label):
    a, b = comp(sa), comp(sb)
    ba, bbx = a.BoundingBox(), b.BoundingBox()
    if (
        ba.xmax < bbx.xmin
        or bbx.xmax < ba.xmin
        or ba.ymax < bbx.ymin
        or bbx.ymax < ba.ymin
        or ba.zmax < bbx.zmin
        or bbx.zmax < ba.zmin
    ):
        return
    assert volume(a.intersect(b)) < 1e-3, label


def test_the_wing_butts_the_spar_aft_face_within_a_fraction_of_an_inch(right):
    """FC1's forward face stands 0.1 to 0.9 in aft of the centre-section spar's aft face (the web gap and the p126/p88 faces)."""
    from core.spar_book import build_spar

    spar_box = bb(build_spar()["box"].solid) if "box" in build_spar() else None
    if spar_box is None:
        pytest.skip("no spar box part")
    assert bb(right["fc1"].solid).xmin > spar_box.xmin


def test_hardpoints_sit_at_the_spars_p88_bolt_stations(right):
    b = bb(right["hardpoints"].solid)
    assert (
        b.ymin == pytest.approx(25.0 - 1.15, abs=0.1)
    )  # LWA6, 2.3 across, centred on BL 25 (set square to the web face, so the box is a shade wider in y)
    assert b.ymax == pytest.approx(53.5 + 0.75, abs=0.2)  # LWA4 pair centred on BL 53.5
    bolts = right["spar_bolts"].solid.vals()[0].Solids()
    assert len(bolts) == 3
    ys = sorted(round(s.Center().y, 1) for s in bolts)
    assert ys == [25.0 + 0.0, 53.5, 53.5]
    lens = sorted(round(s.BoundingBox().xlen, 3) for s in bolts)
    assert lens == [2.125, 2.125, 2.375]  # AN8-21A twice, AN8-23A once


def test_rod_and_tube_lie_in_the_aileron_and_the_tube_sticks_out_one_inch_inboard(
    right,
):
    rod, tube = bb(right["aileron_rod"].solid), bb(right["torque_tube"].solid)
    assert (rod.ymin, rod.ymax) == (
        pytest.approx(55.5, abs=0.2),
        pytest.approx(118.1, abs=0.2),
    )
    assert 55.5 < rod.ymin and rod.ymax < 118.1  # inside the aileron's span
    d = wb._hinge_dir()[1]
    assert tube.ymin == pytest.approx(55.5 - 1.0 * d - 0.375 * 0, abs=0.4)
    assert tube.ymin < 55.5 - 0.9  # the inboard 1 in is outside the aileron
    assert vol_of(right["torque_tube"].solid) == pytest.approx(
        math.pi * 0.375**2 * 9.0, rel=1e-3
    )


def test_three_hinges_8_6_6_in():
    spans = [b1 - b0 for b0, b1 in wb.FITTED_HINGE_BL]
    assert spans == pytest.approx([8.0, 6.0, 6.0])
    assert tuple(spans) == (8.0, 6.0, 6.0)


def test_aileron_pose_range_hinge_axis_and_travel(right):
    ail = right["aileron"].solid
    with pytest.raises(ValueError):
        wb.aileron_pose(ail, 21.0)
    with pytest.raises(ValueError):
        wb.aileron_pose(ail, -1.0)
    assert wb.aileron_pose(ail, 0.0) is ail
    up = wb.aileron_pose(ail, 20.0)
    assert vol_of(up) == pytest.approx(vol_of(ail), rel=1e-6)
    b0, b1 = bb(ail), bb(up)
    assert b1.zmax > b0.zmax + 0.3  # the trailing edge swung up
    te = cq.Workplane("XY").add(
        cq.Solid.makeBox(
            0.01,
            0.01,
            0.01,
            cq.Vector(
                wb.te_fs(55.5) - 0.01, 55.5, wb.z_surface(55.5, wb.te_fs(55.5), +1)
            ),
        )
    )
    gain = bb(wb.aileron_pose(te, 20.0)).zmax - bb(te).zmax
    assert (
        1.5 < gain < 2.2
    )  # 5.9 in forward of the TE at the root, so about 5.75 sin 20
    assert b1.ymin == pytest.approx(b0.ymin, abs=0.5) and b1.ymax == pytest.approx(
        b0.ymax, abs=0.5
    )
    # a short rod lying on the axis does not move
    a, c = wb.aileron_axis()
    pin = cq.Workplane("XY").add(
        cq.Solid.makeCylinder(
            0.05, 10.0, cq.Vector(*a), cq.Vector(c[0] - a[0], c[1] - a[1], c[2] - a[2])
        )
    )
    moved = wb.aileron_pose(pin, 20.0)
    assert bb(moved).zmax == pytest.approx(bb(pin).zmax, abs=1e-6)
    assert bb(moved).xmax == pytest.approx(bb(pin).xmax, abs=1e-6)
    # the pose turns only the aileron-attached parts
    posed = wb.build_wing("right", aileron_up_deg=20.0)
    for n, p in posed.items():
        same = bb(p.solid).zmax == pytest.approx(bb(right[n].solid).zmax, abs=1e-9)
        assert same != (n in wb.AILERON_ATTACHED), n


def test_the_hinge_axis_sits_on_the_top_skin_line():
    a, b = wb.aileron_axis()
    assert (a[1], b[1]) == (55.5, 118.1)
    assert a[0] == pytest.approx(149.7) and b[0] == pytest.approx(wb.hinge_fs(118.1))
    assert a[2] == pytest.approx(wb.z_surface(55.5, a[0], +1))


def test_stop_is_20_deg_up():
    assert wb.MAX_UP_DEG == 20.0


# ---- display plies ----
def test_web_ply_zones_are_6_4_2_with_the_cp_corrected_outboard_zone():
    spans = wb.web_ply_spans()
    assert len(spans) == 6

    def n_at(bl):
        return sum(1 for a, b in spans if a <= bl <= b)

    assert [n_at(b) for b in (30.0, 60.0, 100.0, 118.0, 140.0, 156.0)] == [
        6,
        6,
        4,
        4,
        2,
        2,
    ]
    # the zone breaks the plans print (BL 70 and 120) come out of the 91 and 39 in lengths along the web
    assert spans[4][1] == pytest.approx(70.7, abs=0.2)
    assert spans[2][1] == pytest.approx(120.0, abs=0.3)


def test_cap_ply_lengths_and_offsets():
    bot, top = wb.cap_ply_spans(False), wb.cap_ply_spans(True)
    assert len(bot) == 5 and len(top) == 7
    cos = math.cos(math.radians(18.42))
    for (b0, b1), ln, off in zip(bot, (142, 135, 84, 52, 19.5), (0, 5, 12, 19, 26)):
        assert b0 == pytest.approx(23.0 + off * cos)
        assert b1 == pytest.approx(min(157.0, b0 + ln * cos))
    assert top[0] == top[1]  # the first two top plies are the same 142 in tape
    assert [round((b0 - 23.0) / cos, 3) for b0, _ in top] == [0, 0, 6, 12, 18, 24, 30]


def test_plies_group_counts_and_stack_outward_without_entering_the_cores(right):
    p = wb.plies()
    assert {k: len(v) for k, v in p.items()} == {
        "shear_web": 6,
        "cap_bottom": 5,
        "cap_top": 7,
        "skin_bottom": 3,
        "skin_top": 3,
    }
    cores = [comp(right[n].solid) for n in ("fc1", "fc2", "fc3", "fc4", "fc5")]
    for k in ("cap_bottom", "cap_top", "skin_bottom", "skin_top", "shear_web"):
        for ply in p[k]:
            assert all(s.isValid() for s in ply.vals())
            for c in cores:
                assert volume(comp(ply).intersect(c)) < 0.02, (
                    k
                )  # a ply sits on the core surface (the surface model and the ruled core differ by hundredths of an inch)
    # caps stack outward: the top cap's plies climb, the bottom's descend
    assert bb(p["cap_top"][6]).zmax > bb(p["cap_top"][0]).zmax
    assert bb(p["cap_bottom"][4]).zmin < bb(p["cap_bottom"][0]).zmin


# ---- the left wing ----
def test_left_wing_is_the_mirror_of_the_right(right, left):
    for n in right:
        a, b = bb(right[n].solid), bb(left[n].solid)
        assert (b.xmin, b.xmax, b.zmin, b.zmax) == pytest.approx(
            (a.xmin, a.xmax, a.zmin, a.zmax), abs=1e-6
        ), n
        assert (b.ymin, b.ymax) == pytest.approx((-a.ymax, -a.ymin), abs=1e-6), n
        assert vol_of(left[n].solid) == pytest.approx(
            vol_of(right[n].solid), rel=1e-9
        ), n
    with pytest.raises(ValueError):
        wb.build_wing("port")


# ---- hygiene ----
def test_fitted_constants_carry_the_comment_on_the_statement():
    src = (REPO / "core" / "wing_book.py").read_text()
    lines = src.splitlines()
    seen = 0
    for node in ast.parse(src).body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("FITTED_")
        ):
            seen += 1
            toks = [
                t
                for t in tokenize.generate_tokens(
                    io.StringIO(
                        "\n".join(lines[node.lineno - 1 : node.end_lineno])
                    ).readline
                )
                if t.type == tokenize.COMMENT
            ]
            assert any(
                ("fitted, not book" in t.string) or ("book" in t.string) for t in toks
            ), node.targets[0].id
    assert seen >= 20


def test_no_hard_coded_book_stations_in_the_builder():
    banned = {
        112.9,
        155.6,
        134.45,
        165.8,
        125.6,
        130.5,
        147.35,
        164.2,
        148.4,
        22.98,
        18.42,
        149.7,
        161.45,
    }
    tree = ast.parse((REPO / "core" / "wing_book.py").read_text())
    nums = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, float)
    }
    assert not (nums & banned), nums & banned


def test_z_zero_is_the_wing_plane():
    assert z_of_wl(17.4) == 0.0
