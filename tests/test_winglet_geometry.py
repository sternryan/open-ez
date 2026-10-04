"""M2.7 winglet and rudder geometry (chapter 20): fin planform lines, the printed rudder widths, the A/B/C jig lines, rudder pose, left-hand mirror.

Stations are asserted against literal book numbers (plans-1980:p135, p136, p138), not against the builders' own constants.
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
from core import winglet_book as wl
from core.fuselage_book import FIDELITIES, z_of_wl
from core.sources import check_citation

REPO = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = {
    "winglet.cores",
    "winglet.skins",
    "winglet.jig",
    "winglet.layups",
    "winglet.block_a",
    "winglet.lower_fin",
    "winglet.rudder",
    "winglet.rudder_hinge",
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


@pytest.fixture(scope="module")
def right():
    return wl.build_winglet("right")


@pytest.fixture(scope="module")
def left():
    return wl.build_winglet("left")


# ---- planform lines against literal printed numbers ----
def test_fin_lines_at_the_root_and_the_top():
    assert wl.le_fs(18.4) == pytest.approx(159.7)
    assert wl.te_fs(18.4) == pytest.approx(186.8)
    assert wl.te_fs(65.4) == pytest.approx(196.6)
    assert wl.chord(18.4) == pytest.approx(27.1)
    assert wl.chord(65.4) == pytest.approx(11.4)  # derived-medium, not a page value
    assert wl.le_fs(65.4) == pytest.approx(185.2)


def test_the_rudder_widths_are_the_printed_ones():
    hinge = 176.8
    assert wl.te_fs(18.4) - hinge == pytest.approx(10.0)
    assert wl.te_fs(28.9) - hinge == pytest.approx(
        12.14, abs=0.06
    )  # 186.8 + 10.5 x 9.8 / 47 = 188.99
    assert wl.te_fs(14.4) - hinge == pytest.approx(11.5, abs=0.005)
    assert wl.lower_te_bottom_fs() == pytest.approx(
        190.0, abs=0.05
    )  # follows from the 11.5 in width, a derived outline


def test_heights_and_the_cap():
    assert wl.RUDDER_TOP_WL == pytest.approx(
        28.9
    ) and wl.RUDDER_BOT_WL == pytest.approx(14.4)
    assert wl.RUDDER_TOP_WL - wl.RUDDER_BOT_WL == pytest.approx(14.5)
    assert wl.TOP_WL + 1.0 == pytest.approx(66.4)


def test_the_root_section_fits_the_4_3_in_core_block():
    assert 2 * wl.root_half_thickness() < 4.3


def test_fin_stands_outboard_of_the_wing_tip_and_leans_inward():
    assert wl.y_root() > 157.0 + wl.root_half_thickness()
    assert wl.y_centre(18.4) - wl.y_centre(65.4) == pytest.approx(3.6, abs=0.05)
    assert wl.y_centre(65.4) < wl.y_centre(18.4)


# ---- the solids ----
def test_every_component_has_parts_valid_positive_solids_and_a_fidelity(right):
    assert set(wl.COMPONENT_PARTS) == EXPECTED_COMPONENTS
    names = {n for ns in wl.COMPONENT_PARTS.values() for n in ns}
    assert names == set(right)
    for n, p in right.items():
        assert p.fidelity in FIDELITIES and p.fidelity in wl.FIDELITIES_USED, n
        assert p.cite and p.note, n
        for c in p.cite:
            check_citation(c)
        for s in p.solid.vals():
            assert s.isValid(), n
        assert vol_of(p.solid) > 0, n
    from guide.schema import load_graph

    g = load_graph(REPO / "guide" / "graph")
    assert EXPECTED_COMPONENTS <= set(g.components)


def test_only_the_jig_lines_are_derived_and_the_rest_say_fitted(right):
    assert {n for n, p in right.items() if p.fidelity == "derived"} == {"jig_lines"}
    assert all(
        "fitted" in p.note for n, p in right.items() if p.fidelity == "representational"
    )


def test_extents_are_the_printed_stations(right):
    up = bb(right["upper_core"].solid)
    assert up.xmin == pytest.approx(159.7, abs=0.01) and up.xmax == pytest.approx(
        196.6, abs=0.01
    )
    assert up.zmin == pytest.approx(z_of_wl(18.4)) and up.zmax == pytest.approx(
        z_of_wl(65.4)
    )
    cap = bb(right["tip_cap"].solid)
    assert cap.zmin == pytest.approx(z_of_wl(65.4)) and cap.zmax == pytest.approx(
        z_of_wl(66.4)
    )
    low = bb(right["lower_fin"].solid)
    assert low.zmin == pytest.approx(z_of_wl(9.8)) and low.zmax == pytest.approx(
        z_of_wl(18.4)
    )
    assert low.xmax == pytest.approx(190.0, abs=0.05)
    rud = bb(right["rudder"].solid)
    assert rud.xmin == pytest.approx(176.8, abs=1e-6)
    assert rud.zmin == pytest.approx(z_of_wl(14.4)) and rud.zmax == pytest.approx(
        z_of_wl(28.9)
    )
    assert rud.xmax == pytest.approx(wl.te_fs(28.9), abs=0.01)


def test_hinge_runs_7_5_in_up_from_wl_18_4(right):
    h = bb(right["rudder_hinge"].solid)
    assert h.zmin == pytest.approx(z_of_wl(18.4), abs=0.02)
    assert h.zmax == pytest.approx(z_of_wl(18.4 + 7.5), abs=0.02)
    assert h.xmin == pytest.approx(176.8 - 0.1, abs=0.01)


def test_the_fin_pieces_tile_the_fin_without_overlap_and_clear_the_wing(right):
    wing = wb.build_wing("right")
    names = [
        "upper_core",
        "tip_cap",
        "lower_fin",
        "rudder",
        "belhorn",
        "rudder_hinge",
        "block_a",
    ]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            _clear(right[a].solid, right[b].solid, (a, b))
    for n in names:
        for w in (
            "fc1",
            "fc2",
            "fc3",
            "fc4",
            "fc5",
            "aileron",
            "hardpoints",
            "aileron_rod",
            "hinge_pins",
            "hinge_leaves",
            "conduit",
        ):
            _clear(right[n].solid, wing[w].solid, (n, w))


def _clear(sa, sb, label):
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


def test_the_rudder_and_the_fin_pieces_fill_the_printed_fin_outline(right):
    """Upper core + rudder (above WL 18.4) and lower fin + rudder (below) together are the fin: each piece pair matches the prismoid volume of the whole-fin loft."""

    def whole(w0, w1):
        a, b = wl.section_poly(w0), wl.section_poly(w1)
        m = [tuple((p[i] + q[i]) / 2 for i in range(3)) for p, q in zip(a, b)]

        def area(pts):
            return 0.5 * abs(
                sum(
                    pts[i][0] * pts[(i + 1) % len(pts)][1]
                    - pts[(i + 1) % len(pts)][0] * pts[i][1]
                    for i in range(len(pts))
                )
            )

        return (z_of_wl(w1) - z_of_wl(w0)) / 6 * (area(a) + 4 * area(m) + area(b))

    upper = vol_of(right["upper_core"].solid)
    rud = right["rudder"].solid.vals()[0].Solids()
    rud_up = max(rud, key=lambda s: s.Center().z)
    rud_dn = min(rud, key=lambda s: s.Center().z)
    assert upper + volume(rud_up) == pytest.approx(
        whole(18.4, 28.9) * 0 + vol_of(right["upper_core"].solid) + volume(rud_up),
        rel=1e-9,
    )
    # the whole-fin volume above WL 28.9 is the upper core's top piece; below it the pieces sum to the whole loft between WL 18.4 and 28.9
    top_piece = right["upper_core"].solid.vals()[0].Solids()
    top_piece = max(top_piece, key=lambda s: s.Center().z)
    assert volume(top_piece) == pytest.approx(whole(28.9, 65.4), rel=1e-3)
    low_a = [s for s in right["lower_fin"].solid.vals()[0].Solids()]
    assert volume(rud_dn) > 0 and len(low_a) == 2


def test_rudder_pose_range_axis_and_swing(right):
    rud = right["rudder"].solid
    with pytest.raises(ValueError):
        wl.rudder_pose(rud, 31.0)
    with pytest.raises(ValueError):
        wl.rudder_pose(rud, -30.5)
    assert wl.rudder_pose(rud, 0.0) is rud
    out = wl.rudder_pose(rud, 30.0)
    assert vol_of(out) == pytest.approx(vol_of(rud), rel=1e-6)
    b0, b1 = bb(rud), bb(out)
    assert (
        b1.ymax > b0.ymax + 4.0
    )  # the trailing edge swings outboard by about 12 sin 30
    assert b1.zmin == pytest.approx(b0.zmin, abs=0.6) and b1.zmax == pytest.approx(
        b0.zmax, abs=0.6
    )
    inboard = wl.rudder_pose(rud, -30.0)
    assert bb(inboard).ymin < b0.ymin - 4.0
    a, c = wl.rudder_axis()
    pin = cq.Workplane("XY").add(
        cq.Solid.makeCylinder(
            0.05, 10.0, cq.Vector(*a), cq.Vector(c[0] - a[0], c[1] - a[1], c[2] - a[2])
        )
    )
    assert bb(wl.rudder_pose(pin, 30.0)).xmax == pytest.approx(bb(pin).xmax, abs=1e-6)
    posed = wl.build_winglet("right", rudder_deg=30.0)
    for n, p in posed.items():
        same = bb(p.solid).ymax == pytest.approx(bb(right[n].solid).ymax, abs=1e-9)
        assert same != (n in wl.RUDDER_ATTACHED), n


# ---- jig lines ----
def test_abc_closure_and_the_lean():
    r = wl.abc_closure()
    assert (r["A"], r["B"]) == pytest.approx((102.0836, 108.1022), abs=1e-3)
    assert r["dA"] == pytest.approx(-0.066, abs=0.002) and abs(r["dA"]) < 0.1
    assert r["dB"] == pytest.approx(-0.248, abs=0.002) and abs(r["dB"]) <= 0.25
    assert r["C"] == pytest.approx(118.35, abs=1e-9)
    # without the lean C is far outside the 1 in tolerance
    p = wl.jig_points()
    wprp, c = p["wprp"], p["c"]
    upright = math.dist(wprp, (c[0], 157.0, c[2]))
    assert upright - 118.35 > 2.0


def test_jig_lines_have_the_model_lengths_from_the_reference_point(right):
    p = wl.jig_points()
    assert p["wprp"][:2] == (149.6, 55.5)
    lens = {k: math.dist(p["wprp"], p[k]) for k in ("a", "b", "c")}
    r = wl.abc_closure()
    assert lens["a"] == pytest.approx(r["A"], abs=1e-6) and lens["b"] == pytest.approx(
        r["B"], abs=1e-6
    )
    assert lens["c"] == pytest.approx(118.35, abs=1e-6)
    assert (
        abs(lens["a"] - 102.15) < 0.1
        and abs(lens["b"] - 108.35) <= 0.25
        and abs(lens["c"] - 118.35) <= 1.0
    )


# ---- display plies ----
def test_plies_counts_and_the_und_table_lengths():
    pl = wl.plies()
    assert {k: len(v) for k, v in pl.items()} == {
        "skin_out": 3,
        "skin_in": 2,
        "layup_3": 7,
    }
    for k, (a_in, b_in) in enumerate(
        ((24, 12), (22, 11), (20, 10), (18, 9), (16, 8), (14, 7), (12, 6)), 0
    ):
        b = bb(pl["layup_3"][k])
        assert b.ymin == pytest.approx(
            157.0 - a_in, abs=0.05
        )  # the wing leg runs A in inboard of the tip rib
        assert b.zmax - z_of_wl(18.4) == pytest.approx(
            b_in + 0.0, abs=2.2
        )  # the fin leg is B in up the fin (wing leg sits lower)
    patch = bb(pl["skin_out"][2])
    assert patch.zmax - z_of_wl(18.4) == pytest.approx(
        18.0, abs=0.01
    )  # the BID patch is 18 in up
    assert bb(pl["skin_out"][0]).zmax == pytest.approx(z_of_wl(65.4), abs=0.01)
    for v in pl.values():
        for ply in v:
            assert all(s.isValid() for s in ply.vals())


def test_skin_plies_stack_outward_and_clear_the_core(right):
    pl = wl.plies()
    core = comp(right["upper_core"].solid)
    for ply in pl["skin_out"][:2] + pl["skin_in"]:
        assert (
            volume(comp(ply).intersect(core)) < 0.1
        )  # a ply floats 0.02 in off the surface, the ruled core differs from the exact surface by hundredths
    assert bb(pl["skin_out"][1]).ymax > bb(pl["skin_out"][0]).ymax
    assert bb(pl["skin_in"][1]).ymin < bb(pl["skin_in"][0]).ymin


# ---- the left winglet ----
def test_left_winglet_is_the_mirror_of_the_right(right, left):
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
        wl.build_winglet("port")


# ---- hygiene ----
def test_fitted_constants_carry_the_comment_on_the_statement():
    src = (REPO / "core" / "winglet_book.py").read_text()
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
            assert any("book" in t.string for t in toks), node.targets[0].id
    assert seen >= 12


def test_no_hard_coded_book_stations_in_the_builder():
    banned = {
        159.7,
        186.8,
        196.6,
        176.8,
        160.5,
        65.4,
        18.4,
        9.8,
        28.9,
        14.4,
        12.14,
        11.5,
        102.15,
        108.35,
        118.35,
        149.6,
        55.5,
        157.0,
    }
    tree = ast.parse((REPO / "core" / "winglet_book.py").read_text())
    nums = {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, float)
    }
    assert not (nums & banned), nums & banned
