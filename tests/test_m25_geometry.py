"""M2.5 installed geometry: spar fittings, firewall face and accessories, controls and trim.

Stations are asserted against literal book numbers, not against the builders' own constants.
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

from core import controls_book, firewall_book, spar_book
from core import controls_kin as ck
from core.fuselage_book import FIDELITIES, build_fuselage, z_of_wl

MODULES = (spar_book, firewall_book, controls_book)
REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
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


def volume(shape) -> float:
    """BRepGProp volume (Shape.Volume is unreliable on BSPLINE faces)."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, props, 1e-6, False, False)
    return props.Mass()


def vol_of(wp) -> float:
    return sum(volume(s) for s in wp.vals())


def is_left_right_symmetric(wp) -> bool:
    """Every solid has a mirror twin (same volume, centre at -y) in the same compound."""
    sols = wp.solids().vals()

    def key(s):
        c = s.Center()
        return (round(c.x, 5), round(c.y, 5), round(c.z, 5), round(volume(s), 5))

    have = {key(s) for s in sols}
    return all((k[0], -k[1] + 0.0, k[2], k[3]) in have for k in map(key, sols))


def overlap(a, b) -> float:
    return volume(a.val().intersect(b.val()))


@pytest.fixture(scope="module")
def parts():
    out = {}
    for mod in MODULES:
        built = (
            mod.build_spar()
            if mod is spar_book
            else mod.build_firewall()
            if mod is firewall_book
            else mod.build_controls()
        )
        out.update(built)
    return out


@pytest.fixture(scope="module")
def comps():
    out = {}
    for mod in MODULES:
        out.update(mod.COMPONENT_PARTS)
    return out


def part_wps(parts, comps, cid):
    return [parts[n].solid for n in comps[cid]]


def bbox(wps):
    return cq.Compound.makeCompound([w.val() for w in wps]).BoundingBox()


def test_every_new_component_has_parts_and_the_graph_agrees(comps):
    assert EXPECTED_COMPONENTS <= set(comps)
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    for cid in EXPECTED_COMPONENTS:
        assert (
            g.components[cid].fidelity == "unvalidated"
        ), cid  # representational in the graph's words


def test_every_solid_has_positive_volume_a_valid_fidelity_and_valid_cites(parts):
    for name, p in parts.items():
        assert vol_of(p.solid) > 1e-6, name
        assert p.fidelity in FIDELITIES, name
        assert p.fidelity == "representational" or p.cite, name
        for s in p.solid.solids().vals():
            assert s.isValid(), name


def test_no_part_is_tagged_book_where_a_position_is_fitted(parts):
    # every M2.5 installed solid here is a stand-in placement of a printed size
    assert {p.fidelity for p in parts.values()} == {"representational"}


# ---- spar stations ----------------------------------------------------------------------------------
def test_spar_faces_at_the_centreline(parts):
    bb = parts["box"].solid.val().BoundingBox()
    assert bb.xmin == pytest.approx(118.5, abs=1e-5)
    probe = cq.Workplane("XY").box(0.02, 0.02, 4).translate((124.99, 0, z_of_wl(17)))
    assert overlap(parts["box"].solid, probe) > 0
    probe2 = cq.Workplane("XY").box(0.02, 0.02, 4).translate((125.01, 0, z_of_wl(17)))
    assert overlap(parts["box"].solid, probe2) < 1e-9


@pytest.mark.parametrize("sign", [1, -1])
def test_lwa_plates_sit_on_the_hard_points(comps, parts, sign):
    # hard points: BL 25.0 at WL 20.25; BL 53.5 at WL 20.5 and 16.3 (p88)
    plates = []
    for n in comps["spar.lwa"]:
        plates += parts[n].solid.solids().vals()
    targets = [(25.0, 20.25), (53.5, 20.5), (53.5, 16.3)]
    for bl, wl in targets:
        hit = [
            s
            for s in plates
            if abs((s.BoundingBox().ymin + s.BoundingBox().ymax) / 2 - sign * bl) < 1e-3
            and s.BoundingBox().zmin < z_of_wl(wl) < s.BoundingBox().zmax
        ]
        assert hit, (bl, wl)


def test_lwa_counts_follow_the_spar_chapter_quantities(parts, comps):
    counts = {n: len(parts[n].solid.solids().vals()) for n in comps["spar.lwa"]}
    assert counts == {"lwa1": 6, "lwa2": 2, "lwa3": 2, "lwa4": 4, "lwa5": 2}


def test_lwa_plates_do_not_overlap_each_other_or_the_caps(parts, comps):
    plates = []
    for n in comps["spar.lwa"]:
        plates += [(n, s) for s in parts[n].solid.solids().vals()]
    for i, (_, a) in enumerate(plates):
        for _, b in plates[i + 1 :]:
            assert volume(a.intersect(b)) < 1e-7
    for _, a in plates:
        for cap in ("cap_top", "cap_bottom"):
            assert volume(a.intersect(parts[cap].solid.val())) < 1e-7


def test_corrected_lwa_sizes_are_used(parts):
    # CP43 LPC 119: LWA4 is 1.75 tall and LWA5 2.25 tall (printed 1.5 and 2.0)
    def thick_and_tall(name):
        s = parts[name].solid.solids().vals()[0]
        return sorted(
            [s.BoundingBox().xlen, s.BoundingBox().ylen, s.BoundingBox().zlen]
        )

    assert volume(parts["lwa4"].solid.solids().vals()[0]) == pytest.approx(
        1.75 * 2.0 * 0.25, rel=1e-6
    )
    assert volume(parts["lwa5"].solid.solids().vals()[0]) == pytest.approx(
        2.25 * 2.0 * 0.25, rel=1e-6
    )
    assert (
        thick_and_tall("lwa3")[-1] >= 6.4
    )  # tall plate, swept so its bbox is a little over


@pytest.mark.parametrize(
    "name", ["end_bulkheads", "interior_bulkheads", "spruce_blocks", "em12", "sh1"]
)
def test_spar_fittings_are_left_right_symmetric(parts, name):
    assert is_left_right_symmetric(parts[name].solid)


@pytest.mark.parametrize("name", ["lwa1", "lwa2", "lwa3", "lwa4", "lwa5"])
def test_lwa_plates_are_left_right_symmetric(parts, name):
    assert is_left_right_symmetric(parts[name].solid)


def test_spruce_blocks_at_bl_7_5_top_and_bottom(parts):
    blocks = parts["spruce_blocks"].solid.solids().vals()
    assert len(blocks) == 4
    for s in blocks:
        bb = s.BoundingBox()
        assert abs((bb.ymin + bb.ymax) / 2) == pytest.approx(7.5, abs=1e-6)
        assert volume(s) == pytest.approx(3.0, rel=1e-6)
        assert bb.xmax == pytest.approx(
            125.0, abs=1e-6
        )  # on the aft face, 3 in trough width
    assert sorted(
        round((s.BoundingBox().ymin + s.BoundingBox().ymax) / 2, 3) for s in blocks
    ) == [
        -7.5,
        -7.5,
        7.5,
        7.5,
    ]
    assert sum(1 for s in blocks if s.BoundingBox().zmax > z_of_wl(17.75)) == 2


def test_end_bulkheads_are_6_30_by_6_83_and_interior_ones_stand_27_from_centre(parts):
    ends = parts["end_bulkheads"].solid.solids().vals()
    assert len(ends) == 2
    for s in ends:
        assert volume(s) == pytest.approx(6.30 * 6.83 * 0.25, rel=1e-6)
        assert abs(s.BoundingBox().zmax - s.BoundingBox().zmin) == pytest.approx(
            6.83, abs=1e-6
        )
    ys = sorted((s.BoundingBox().ymin + s.BoundingBox().ymax) / 2 for s in ends)
    assert ys[0] < -56.0 and ys[1] > 56.0
    inner = parts["interior_bulkheads"].solid.solids().vals()
    assert len(inner) == 2
    cy = sorted((s.BoundingBox().ymin + s.BoundingBox().ymax) / 2 for s in inner)
    assert cy == pytest.approx([-27.0, 27.0], abs=1e-6)


def test_em12_four_angles_8_long_aft_of_the_firewall_face(parts):
    angles = parts["em12"].solid.solids().vals()
    assert len(angles) == 4
    for s in angles:
        bb = s.BoundingBox()
        assert bb.zlen == pytest.approx(8.0, abs=1e-6)
        assert bb.xmin > 125.25  # clear of the plywood
        assert bb.xmax == pytest.approx(125.0 + 1.6, abs=1e-6)


def test_sh1_two_plates_on_the_spar_top(parts):
    plates = parts["sh1"].solid.solids().vals()
    assert len(plates) == 2
    for s in plates:
        bb = s.BoundingBox()
        assert bb.xlen == pytest.approx(2.3, abs=1e-6) and bb.ylen == pytest.approx(
            0.7, abs=1e-6
        )
        assert bb.zmin == pytest.approx(z_of_wl(22.0), abs=1e-6)


def test_jig_is_workshop_geometry_and_the_spar_box_is_not_inside_it(parts, comps):
    assert "workshop" in parts["jig"].note
    assert overlap(parts["jig"].solid, parts["box"].solid) < 1e-6


def test_installed_spar_parts_clear_the_firewall_plywood_except_the_bonded_face():
    fus = build_fuselage()["firewall"].solid
    for name, p in spar_book.build_spar().items():
        if name in {"jig", "em12", "lwa"}:
            continue  # jig is workshop only; EM12 stands aft of the stack; LWA is outboard of the plywood
        assert overlap(fus, p.solid) < 1e-6, name
    bb = fus.val().BoundingBox()
    assert bb.xmin == pytest.approx(
        125.0, abs=1e-6
    )  # the spar's centreline aft face is this plane


# ---- firewall -------------------------------------------------------------------------------------------
def test_stainless_face_is_over_the_plywood_outline_with_the_torque_tube_hole():
    fw = firewall_book.build_firewall()
    ply = build_fuselage()["firewall"].solid.val().BoundingBox()
    st = fw["stainless"].solid.val().BoundingBox()
    assert st.xmin == pytest.approx(ply.xmax, abs=1e-6)  # the aft face of the plywood
    assert (st.ymin, st.ymax) == pytest.approx((ply.ymin, ply.ymax), abs=1e-6)
    hole = (
        cq.Workplane("YZ")
        .circle(0.49)
        .extrude(1.0)
        .translate((st.xmin - 0.3, 6.2, z_of_wl(12.3)))
    )
    assert (
        overlap(fw["stainless"].solid, hole) < 1e-9
    )  # the 1 in hole is open at BL 6.2 R, WL 12.3
    solid_probe = (
        cq.Workplane("YZ")
        .circle(0.05)
        .extrude(1.0)
        .translate((st.xmin - 0.3, -6.2, z_of_wl(12.3)))
    )
    assert overlap(fw["stainless"].solid, solid_probe) > 0  # and only on the right


def test_firewall_accessories_are_symmetric_and_aft_of_the_stainless():
    fw = firewall_book.build_firewall()
    st = fw["stainless"].solid.val().BoundingBox()
    for name in ("belcrank", "master_cylinders"):
        wp = fw[name].solid
        assert wp.val().BoundingBox().xmin >= st.xmax - 1e-9, name
        assert is_left_right_symmetric(wp), name
        assert overlap(wp, fw["stainless"].solid) < 1e-9, name


# ---- controls -----------------------------------------------------------------------------------------
def test_torque_tube_runs_from_the_front_pivot_plane_at_bl_6_2_wl_12_3(parts):
    bb = parts["torque_tube"].solid.val().BoundingBox()
    assert bb.xmin == pytest.approx(45.5, abs=1e-6)
    assert bb.xmax <= 125.0 + 1e-6
    assert (bb.ymin + bb.ymax) / 2 == pytest.approx(6.2, abs=1e-6)
    assert (bb.zmin + bb.zmax) / 2 == pytest.approx(z_of_wl(12.3), abs=1e-6)


def test_stick_pivot_planes_are_45_5_and_89_7():
    for which, plane in (("front", 45.5), ("rear", 89.7)):
        base, tip = controls_book.stick_axis(which)
        assert base.x == pytest.approx(plane, abs=1e-6)
        assert base.y == pytest.approx(6.2, abs=1e-6)
        assert base.z == pytest.approx(z_of_wl(12.3), abs=1e-6)
        # 5 deg forward cant (nose-ward, toward lower FS) and 5 deg inboard cant at neutral
        d = tip - base
        assert d.x < 0 < d.z and d.y < 0
        assert math.degrees(math.atan2(-d.x, d.z)) == pytest.approx(5.0, abs=0.5)
        assert math.degrees(math.atan2(-d.y, d.z)) == pytest.approx(5.0, abs=0.5)


def test_stick_pitch_uses_the_kinematics_and_the_roncz_clamp_only():
    neutral = controls_book.stick_axis("front")
    assert neutral[1].x - neutral[0].x < 0
    a = controls_book.stick_axis("front", elevator_deflection_deg=15.0)
    over = controls_book.stick_axis("front", elevator_deflection_deg=40.0)
    assert (a[1] - a[0]).x == pytest.approx(
        (over[1] - over[0]).x, abs=1e-9
    )  # 40 clamps to the 15 up limit
    lim20 = controls_book.stick_axis("front", elevator_deflection_deg=20.0)
    assert (lim20[1] - lim20[0]).x == pytest.approx(
        (a[1] - a[0]).x, abs=1e-9
    )  # 20 is not a limit
    down = controls_book.stick_axis("front", elevator_deflection_deg=-30.0)
    assert (down[1] - down[0]).x != pytest.approx((a[1] - a[0]).x)
    angle = ck.stick_angle_deg(15.0)
    d = a[1] - a[0]
    assert math.degrees(math.asin(-d.x / d.Length)) == pytest.approx(angle, abs=1.0)


def test_controls_source_has_no_gu_travel_number():
    src = Path(controls_book.__file__).read_text()
    nums = [
        t.string
        for t in tokenize.generate_tokens(io.StringIO(src).readline)
        if t.type == tokenize.NUMBER
    ]
    assert [n for n in nums if float(n) in (20.0, 22.0)] == []


def test_rudder_conduits_are_82_long_at_wl_8(parts):
    solids = parts["rudder_conduit"].solid.solids().vals()
    assert len(solids) == 2
    for s in solids:
        bb = s.BoundingBox()
        assert bb.xlen == pytest.approx(82.0, abs=1e-6)
        assert (bb.zmin + bb.zmax) / 2 == pytest.approx(z_of_wl(8.0), abs=1e-6)
    ys = sorted((s.BoundingBox().ymin + s.BoundingBox().ymax) / 2 for s in solids)
    assert ys[0] == pytest.approx(-ys[1], abs=1e-9)


def test_consoles_enclose_the_pivot_planes_with_the_printed_lengths(parts):
    front = parts["front_console"].solid.val().BoundingBox()
    rear = parts["rear_console"].solid.val().BoundingBox()
    assert front.xmin == pytest.approx(
        45.5 - 1.0, abs=1e-6
    )  # troughs start 1 in ahead of the pivot plane
    assert front.xlen == pytest.approx(30.1, abs=1e-6)
    assert rear.xmin == pytest.approx(89.7 - 1.0, abs=1e-6)
    assert rear.xlen == pytest.approx(25.8, abs=1e-6)
    assert front.ylen == pytest.approx(3.5, abs=1e-6) and rear.ylen == pytest.approx(
        3.1, abs=1e-6
    )


def test_trim_handle_aft_end_is_fs_49_5_not_the_49_8_label(parts):
    bb = parts["pth"].solid.val().BoundingBox()
    assert bb.xmax == pytest.approx(49.5, abs=1e-6)
    assert bb.xmax != pytest.approx(49.8, abs=0.1)
    assert bb.xlen == pytest.approx(5.2, abs=1e-6)
    pin = parts["pth_pivot"].solid.val().BoundingBox()
    assert (pin.zmin + pin.zmax) / 2 == pytest.approx(z_of_wl(8.6), abs=1e-6)


def test_controls_symmetric_pairs_and_no_unlabelled_overlaps(parts):
    for name in ("rudder_conduit",):
        wp = parts[name].solid
        assert is_left_right_symmetric(wp)
    names = [
        "front_console",
        "rear_console",
        "torque_tube",
        "front_stick",
        "rear_stick",
        "pitch_pushrod",
        "rudder_conduit",
        "pth",
        "pth_pivot",
        "pth_springs",
        "roll_trim",
        "roll_trim_springs",
    ]
    labelled_fits = {
        frozenset(p)
        for p in (
            ("torque_tube", "front_stick"),  # the stick clamps onto the tube
            ("torque_tube", "rear_stick"),
            ("pth", "pth_pivot"),  # the pivot bolt passes through the handle
            ("torque_tube", "roll_trim"),  # the roll-trim tabs clamp on the tube
        )
    }
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if frozenset((a, b)) in labelled_fits:
                continue
            assert overlap(parts[a].solid, parts[b].solid) < 1e-6, (a, b)


def test_component_parts_cover_every_part_exactly_once(parts, comps):
    used = [
        n
        for cid in EXPECTED_COMPONENTS | {"spar.box", "spar.cap_top", "spar.cap_bottom"}
        for n in comps[cid]
    ]
    assert sorted(used) == sorted(parts)


def test_fitted_constants_carry_the_comment_on_the_statement():
    for mod in MODULES:
        src = Path(mod.__file__).read_text()
        lines = src.splitlines()
        for node in ast.parse(src).body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id.startswith("FITTED_")
            ):
                block = "\n".join(lines[node.lineno - 1 : node.end_lineno])
                assert "# fitted, not book" in block, node.targets[0].id
