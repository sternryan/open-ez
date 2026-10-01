"""Fuselage box (chapters 4-6) built from the book: fidelity, side profile, bulkheads, plan bend."""

import math
from itertools import pairwise

import cadquery as cq
import pytest

from config.aircraft_config import config
from core.fuselage_book import FusePart, build_fuselage

G = config.geometry
WING_PLANE_WL = 17.4  # book W.L. of the model zero (wing_le_wl), plans-1980:p134
Z_TOP = G.side_panel_top_wl - WING_PLANE_WL + G.wing_le_wl  # 5.6


# The printed depth table, plans-1980:p36 (captain's page read), kept independent of config so a
# wrong config value fails here too.
PRINTED_HEIGHTS = (
    (0, 19.8),
    (10, 20.3),
    (20, 20.5),
    (30, 20.5),
    (40, 20.5),
    (50, 20.5),
    (60, 20.5),
    (70, 20.4),
    (80, 19.8),
    (90, 18.4),
    (100, 16.6),
    (103, 16.0),
)


@pytest.fixture(scope="module")
def fuse():
    return build_fuselage()


def half_width(fs):
    """Independent re-derivation of the inner half width from config."""
    st = list(G.fuselage_inner_width_stations)
    if fs <= st[0][0]:
        return G.fuselage_inner_width_fwd / 2
    for (x0, w0), (x1, w1) in pairwise(st):
        if fs <= x1:
            return (w0 + (w1 - w0) * (fs - x0) / (x1 - x0)) / 2
    (x0, w0), (x1, w1) = st[-2], st[-1]
    return (w1 + (w1 - w0) * (fs - x1) / (x1 - x0)) / 2


def z_extent_at(solid, fs, y):
    """z extents of the solid inside a thin box at FS `fs` and lateral position y."""
    lo = max(fs - 0.005, G.fs_f22)
    hi = min(fs + 0.005, G.fs_f22 + G.side_panel_length)
    if hi - lo < 0.005:  # at the ends, take the inner 0.01
        lo, hi = (lo, lo + 0.01) if fs <= G.fs_f22 + 1 else (hi - 0.01, hi)
    box = (
        cq.Workplane("XY")
        .box(hi - lo, 0.02, 80, centered=False)
        .translate((lo, y - 0.01, -40))
    )
    cut = solid.intersect(box)
    assert cut.vals() and cut.val().Volume() > 0, f"no material at FS {fs}"
    bb = cut.val().BoundingBox()
    return bb.zmin, bb.zmax


# --- Review Focus 1: fidelity labelling --------------------------------------------------------
def test_every_part_has_a_valid_fidelity(fuse):
    assert fuse
    for name, p in fuse.items():
        assert p.fidelity in {"book", "derived", "representational"}, name
        assert p.name == name


def test_fusepart_rejects_bad_fidelity_and_missing_cite():
    solid = cq.Workplane("XY").box(1, 1, 1)
    with pytest.raises(ValueError):
        FusePart("x", solid, "")  # no fidelity
    with pytest.raises(ValueError):
        FusePart("x", solid, "maybe", ("plans-1980:p36",))  # unknown fidelity
    with pytest.raises(ValueError):
        FusePart("x", solid, "book")  # book with no cite
    with pytest.raises(ValueError):
        FusePart("x", solid, "derived")  # derived with no cite
    with pytest.raises(ValueError):
        FusePart("x", solid, "book", ("nosuchsource:p1",))  # unregistered source
    with pytest.raises(ValueError):
        FusePart("x", solid, "book", ("not a citation",))
    FusePart("x", solid, "representational")  # no cite is fine for representational


def test_fidelity_classes(fuse):
    for n in ("f22", "f28", "panel", "firewall", "bottom"):
        assert fuse[n].fidelity == "representational", n
    for n in (
        "side_left",
        "side_right",
        "front_seat_bkhd",
        "rear_seat_bkhd",
        "top_longeron_left",
        "top_longeron_right",
    ):
        p = fuse[n]
        assert p.fidelity == "book", n
        assert p.cite and all(c.startswith("plans-1980:p") for c in p.cite), n
    assert "plans-1980:p36" in fuse["side_left"].cite
    assert "plans-1980:p38" in fuse["side_left"].cite  # the spar cutout
    assert "plans-1980:p37" in fuse["side_right"].cite  # the dish depth
    assert "plans-1980:p33" in fuse["front_seat_bkhd"].cite
    assert {"plans-1980:p34", "plans-1980:p36", "plans-1980:p38"} <= set(
        fuse["rear_seat_bkhd"].cite
    )
    assert "plans-1980:p37" in fuse["top_longeron_left"].cite
    assert set(fuse) == {
        "side_left",
        "side_right",
        "front_seat_bkhd",
        "rear_seat_bkhd",
        "top_longeron_left",
        "top_longeron_right",
        "f22",
        "f28",
        "panel",
        "firewall",
        "bottom",
        # chapters 7-8 (their own checks are in test_fuselage_exterior.py)
        "canard_cutout",
        "belt_insert",
        "rollover",
        "rollover_inserts",
        "belt_attach",
        "step",
    }
    for n in ("f22", "f28", "panel", "firewall", "bottom"):
        assert "full-size sheet" in fuse[n].note or n == "bottom"
    assert (
        fuse["front_seat_bkhd"].note and "not to scale" in fuse["front_seat_bkhd"].note
    )


# --- Review Focus 3: side profile against the printed table -------------------------------------
@pytest.mark.parametrize("side", ["side_left", "side_right"])
def test_side_bottom_and_top_at_the_printed_stations(fuse, side):
    sign = 1 if side == "side_right" else -1
    cutout_w, cutout_d = G.side_spar_cutout
    for u, depth in PRINTED_HEIGHTS:
        fs = G.fs_f22 + u
        ymid = sign * (half_width(fs) + G.side_panel_thickness / 2)
        zmin, zmax = z_extent_at(fuse[side].solid, fs, ymid)
        assert zmin == pytest.approx(Z_TOP - depth, abs=0.05), (side, u)
        if u <= 90:
            assert zmax == pytest.approx(Z_TOP, abs=0.05), (side, u)
        else:
            assert u >= G.side_panel_length - cutout_w
            assert zmax == pytest.approx(Z_TOP - cutout_d, abs=0.05), (side, u)


def test_side_top_is_full_height_just_forward_of_the_cutout(fuse):
    fs = G.fs_f22 + G.side_panel_length - G.side_spar_cutout[0] - 0.3
    ymid = half_width(fs) + G.side_panel_thickness / 2
    _, zmax = z_extent_at(fuse["side_right"].solid, fs, ymid)
    assert zmax == pytest.approx(Z_TOP, abs=0.05)


# --- solids: valid, closed, dish only on the right ------------------------------------------------
def test_every_solid_is_valid_and_closed(fuse):
    for name, p in fuse.items():
        v = p.solid.val()
        assert v.isValid(), name
        assert v.Volume() > 0, name
        # the roll-over is one fused shell; the inserts and the belt pads are several small solids
        want = {"rollover_inserts": 3, "belt_attach": 4}.get(name, 1)
        assert len(p.solid.solids().vals()) == want, name


def test_right_side_is_lighter_than_left_by_the_dish(fuse):
    import math

    _, _, dia, depth = G.side_dish
    r = dia / 2
    cap = (
        math.pi * depth * (3 * r**2 + depth**2) / 6
    )  # spherical cap, chosen in the module
    dv = (
        fuse["side_left"].solid.val().Volume() - fuse["side_right"].solid.val().Volume()
    )
    assert dv == pytest.approx(cap, rel=0.05)


def test_sides_are_mirror_images(fuse):
    bl = fuse["side_left"].solid.val().BoundingBox()
    br = fuse["side_right"].solid.val().BoundingBox()
    assert bl.ymin == pytest.approx(-br.ymax, abs=1e-6)
    assert bl.ymax == pytest.approx(-br.ymin, abs=1e-6)


# --- plan bend ------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "fs, width", [(70.0, 23.0), (107.0, 20.6), (118.5, 18.7), (30.0, 23.0)]
)
def test_inside_faces_follow_the_plan_bend(fuse, fs, width):
    def inner_y(solid, sign):
        z = Z_TOP - 5.0  # well inside the side's height
        box = (
            cq.Workplane("XY")
            .box(0.01, 40, 0.01, centered=False)
            .translate((fs - 0.005, -20, z))
        )
        bb = solid.intersect(box).val().BoundingBox()
        return bb.ymin if sign > 0 else bb.ymax  # face nearest the centreline

    yr = inner_y(fuse["side_right"].solid, +1)
    yl = inner_y(fuse["side_left"].solid, -1)
    assert yr - yl == pytest.approx(width, abs=0.05)


def test_shear_leaves_heights_alone(fuse):
    bb = fuse["side_right"].solid.val().BoundingBox()
    assert bb.zmax == pytest.approx(Z_TOP, abs=1e-6)
    assert bb.zmin == pytest.approx(Z_TOP - 20.5, abs=0.06)


# --- seat bulkheads ----------------------------------------------------------------------------------
def test_front_seat_bulkhead_sits_between_the_sides_at_its_stations(fuse):
    bb = fuse["front_seat_bkhd"].solid.val().BoundingBox()
    assert bb.ymin >= -half_width(G.fs_front_seat_bkhd_bottom) - 0.05
    assert bb.ymax <= half_width(G.fs_front_seat_bkhd_bottom) + 0.05
    assert bb.ymax - bb.ymin == pytest.approx(G.front_seat_bkhd_width, abs=0.05)
    assert abs(bb.xmin - G.fs_front_seat_bkhd_bottom) <= 1.0
    assert abs(bb.xmax - G.fs_front_seat_bkhd_top) <= 1.0
    # clipped flush with the top longeron (p39)
    assert bb.zmax == pytest.approx(Z_TOP, abs=0.02)
    for v in fuse["front_seat_bkhd"].solid.vertices().vals():
        assert abs(v.Y) <= half_width(v.X) + 0.05


def test_rear_seat_bulkhead_sits_between_the_sides_and_tops_at_the_cutout(fuse):
    bb = fuse["rear_seat_bkhd"].solid.val().BoundingBox()
    for v in fuse["rear_seat_bkhd"].solid.vertices().vals():
        assert abs(v.Y) <= half_width(v.X) + 0.05, (v.X, v.Y)
    assert abs(bb.xmin - G.fs_rear_seat_bkhd_bottom) <= 1.0
    assert abs(bb.xmax - G.fs_rear_seat_bkhd_top) <= 1.0
    # The vertical clip at FS 118.5 puts the upper face's corner above the mid-plane end (at the
    # cutout depth) by half the thickness over cos(slope): exact geometry, not a tolerance.
    (x0, z0), (x1, z1) = _rear_segment()
    slope = math.atan2(z1 - z0, x1 - x0)
    z_mid = Z_TOP - G.side_spar_cutout[1]
    assert bb.zmax == pytest.approx(z_mid + (G.rear_seat_bkhd_thickness / 2) / math.cos(slope), abs=0.02)


def test_rear_seat_bulkhead_has_the_access_hole_and_the_foam_pocket(fuse):
    solid = fuse["rear_seat_bkhd"].solid
    full = G.rear_seat_bkhd_thickness

    def thickness_along_normal_at(radius):
        # probe straight through along the plate normal at the plate centre offset along the slant
        import math

        (x0, z0), (x1, z1) = _rear_segment()
        d = cq.Vector(x1 - x0, 0, z1 - z0).normalized()
        n = cq.Vector(-d.z, 0, d.x)
        c = cq.Vector((x0 + x1) / 2, 0, (z0 + z1) / 2) + d * radius
        line = cq.Solid.makeCylinder(0.01, 4.0, c - n * 2.0, n)
        hit = solid.val().intersect(line)
        return hit.Volume() / (math.pi * 0.01**2)

    assert thickness_along_normal_at(0.0) < 0.01  # 7 in hole: nothing there
    assert thickness_along_normal_at(3.75) == pytest.approx(
        0.05, abs=0.01
    )  # glass between 7 and 8
    assert thickness_along_normal_at(5.5) == pytest.approx(full, abs=0.01)


def _rear_segment():
    z_top = Z_TOP
    depth85 = _side_depth_at_u(G.fs_rear_seat_bkhd_bottom - G.fs_f22)
    return (G.fs_rear_seat_bkhd_bottom, z_top - depth85), (
        G.fs_rear_seat_bkhd_top,
        z_top - G.side_spar_cutout[1],
    )


def _side_depth_at_u(u):
    from core.fuselage_book import side_bottom_depth

    return side_bottom_depth(u)


# --- representational parts ------------------------------------------------------------------------
def test_firewall_spans_the_outer_width_and_sits_aft_of_fs125(fuse):
    bb = fuse["firewall"].solid.val().BoundingBox()
    assert bb.xmin == pytest.approx(G.fs_firewall, abs=1e-6)
    assert bb.xmax - bb.xmin == pytest.approx(0.25, abs=1e-6)
    want = 2 * (half_width(G.fs_firewall) + G.side_panel_thickness)
    assert bb.ymax - bb.ymin == pytest.approx(want, abs=1e-6)


def test_bottom_plate_is_under_the_sides(fuse):
    bb = fuse["bottom"].solid.val().BoundingBox()
    assert bb.xmin == pytest.approx(G.fs_f22, abs=1e-6)
    assert bb.xmax == pytest.approx(
        G.fs_rear_seat_bkhd_bottom + G.bottom_aft_trim, abs=1e-6
    )
    assert bb.ymax == pytest.approx(
        half_width(G.fs_front_seat_bkhd_top) + G.bottom_trim_outboard, abs=0.01
    )


def test_book_fuselage_component_exports_dxf(tmp_path):
    from core.fuselage_book import BookFuselage

    comp = BookFuselage()
    plan = comp.manufacturing_plan(tmp_path)
    assert plan["sheet_templates"]["format"] == "DXF"
    assert plan["sheet_templates"]["tolerance"] is None  # the book prints none
    for f in plan["sheet_templates"]["paths"]:
        assert f.exists()
    assert len(plan["sheet_templates"]["paths"]) == 4
    # every body except the canard cutout (a void): 11 box parts + belt insert + roll-over (1) + inserts (3) + pads (4) + step
    assert len(comp.generate_geometry().solids().vals()) == 21


# --- longerons bonded to the inside face (p37) ------------------------------------------------------
def _y_extent_at(solid, fs, z):
    box = cq.Workplane("XY").box(0.01, 80, 0.01, centered=False).translate((fs, -40, z))
    bb = solid.intersect(box).val().BoundingBox()
    return bb.ymin, bb.ymax


def test_top_longerons_lie_inboard_of_the_sides_inside_faces(fuse):
    hw = half_width(50.0)
    lo, hi = _y_extent_at(fuse["top_longeron_right"].solid, 50.0, Z_TOP - 0.5)
    assert lo == pytest.approx(hw - 0.7, abs=0.02)
    assert hi == pytest.approx(hw, abs=0.02)
    lo, hi = _y_extent_at(fuse["top_longeron_left"].solid, 50.0, Z_TOP - 0.5)
    assert lo == pytest.approx(-hw, abs=0.02)
    assert hi == pytest.approx(-hw + 0.7, abs=0.02)
    for lon, side in (
        ("top_longeron_right", "side_right"),
        ("top_longeron_left", "side_left"),
    ):
        common = fuse[side].solid.intersect(fuse[lon].solid)
        vol = common.val().Volume() if common.vals() else 0.0
        assert vol < 1e-6, (lon, vol)
        bb = fuse[lon].solid.val().BoundingBox()
        assert bb.zmax == pytest.approx(Z_TOP, abs=1e-6)
        assert bb.zmin == pytest.approx(Z_TOP - 1.0, abs=1e-6)


def test_front_seat_bulkhead_clears_the_longerons(fuse):
    for lon in ("top_longeron_right", "top_longeron_left"):
        common = fuse["front_seat_bkhd"].solid.intersect(fuse[lon].solid)
        vol = common.val().Volume() if common.vals() else 0.0
        assert vol < 0.01, (lon, vol)


# --- fuel sight gauge (p36 section B-B) -----------------------------------------------------------------
def _side_thickness_at(solid, u, v):
    fs = G.fs_f22 + u
    z = Z_TOP - v
    box = (
        cq.Workplane("XY")
        .box(0.01, 80, 0.01, centered=False)
        .translate((fs - 0.005, -40, z))
    )
    bb = solid.intersect(box).val().BoundingBox()
    return bb.ymax - bb.ymin


def test_sight_gauge_section(fuse):
    side = fuse["side_left"].solid  # the left side has no dish; same gauge
    assert _side_thickness_at(side, 81.5, 5.0) == pytest.approx(0.2, abs=0.02)
    assert _side_thickness_at(side, 78.0, 5.0) == pytest.approx(0.8, abs=0.02)
    assert _side_thickness_at(side, 86.0, 5.0) == pytest.approx(0.8, abs=0.02)
    # opening edges at the face: 79.5 and 84.5 (2.5 each side of the reference line at 82)
    assert _side_thickness_at(side, 79.6, 5.0) < 0.8 - 0.02
    assert _side_thickness_at(side, 79.4, 5.0) == pytest.approx(0.8, abs=0.02)
    assert _side_thickness_at(side, 84.4, 5.0) < 0.8 - 0.02
    assert _side_thickness_at(side, 84.6, 5.0) == pytest.approx(0.8, abs=0.02)
    # flat floor 81.0 to 82.0
    assert _side_thickness_at(side, 81.05, 5.0) == pytest.approx(0.2, abs=0.02)
    assert _side_thickness_at(side, 81.95, 5.0) == pytest.approx(0.2, abs=0.02)


def test_sight_gauge_dxf_outline_spans_79_5_to_84_5():
    from core.fuselage_book import _side_outline_wp

    pts = [
        v.X
        for w in _side_outline_wp(False).vals()
        for v in w.Vertices()
        if 79 < v.X < 85
    ]
    assert min(pts) == pytest.approx(79.5, abs=1e-6)
    assert max(pts) == pytest.approx(84.5, abs=1e-6)


# --- seat bulkhead ends: clipped flush (p39) ------------------------------------------------------------
def _side_bottom_z(fs):
    from core.fuselage_book import side_bottom_depth

    return Z_TOP - side_bottom_depth(fs - G.fs_f22)


def _long_face(solid, p0, p1):
    """Longest extent along the slope among the two big faces (independent re-derivation)."""
    import math

    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dz)
    d = (dx / n, dz / n)
    nrm = (-d[1], d[0])
    best = 0.0
    for f in solid.faces().vals():
        c = f.normalAt()
        if abs(c.x * nrm[0] + c.z * nrm[1]) < 0.999:
            continue
        s = [v.X * d[0] + v.Z * d[1] for v in f.Vertices()]
        best = max(best, max(s) - min(s))
    return best


def test_front_seat_bulkhead_is_clipped_flush_with_longerons_and_side_bottom(fuse):
    bb = fuse["front_seat_bkhd"].solid.val().BoundingBox()
    assert bb.zmax == pytest.approx(Z_TOP, abs=0.02)
    assert bb.zmin == pytest.approx(
        _side_bottom_z(G.fs_front_seat_bkhd_bottom), abs=0.05
    )
    seg = (
        (G.fs_front_seat_bkhd_bottom, _side_bottom_z(G.fs_front_seat_bkhd_bottom)),
        (G.fs_front_seat_bkhd_top, Z_TOP),
    )
    assert _long_face(fuse["front_seat_bkhd"].solid, *seg) == pytest.approx(
        G.front_seat_bkhd_length, abs=1.0
    )


def test_rear_seat_bulkhead_is_clipped_at_the_spar_and_the_side_bottom(fuse):
    bb = fuse["rear_seat_bkhd"].solid.val().BoundingBox()
    assert bb.xmax == pytest.approx(G.fs_rear_seat_bkhd_top, abs=0.02)
    assert bb.zmin == pytest.approx(
        _side_bottom_z(G.fs_rear_seat_bkhd_bottom), abs=0.05
    )
    assert _long_face(fuse["rear_seat_bkhd"].solid, *_rear_segment()) == pytest.approx(
        G.rear_seat_bkhd_length, abs=1.0
    )
