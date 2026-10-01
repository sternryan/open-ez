"""Chapters 7-8: skins, carved corners, canard cutout, belt insert, roll-over box, belt pads, step.

Review Focus 1 (every new solid carries a fidelity and a valid citation; fitted shapes are never book) and
Review Focus 6 (the skin schedule: the third ply ends on the front seat bulkhead's line, the strip spans
F.S. 60 to 110) are pinned here, plus the roll-over's printed dimensions measured on the solid.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from core import fuselage_book as fb
from core import fuselage_plies as fp
from core.fuselage_book import FIDELITIES, build_fuselage, half_width
from core.sources import check_citation
from guide.schema import load_graph

G = fb.G
ROOT = Path(__file__).resolve().parents[1]
GRAPH = load_graph(ROOT / "guide" / "graph")
NEW_PARTS = ("canard_cutout", "belt_insert", "rollover", "rollover_inserts", "belt_attach", "step")


@pytest.fixture(scope="module")
def fuse():
    return build_fuselage()


@pytest.fixture(scope="module")
def plies():
    return fp.plies(GRAPH)


def _verts(solid):
    return [(v.X, v.Y, v.Z) for v in solid.val().Vertices()]


def _bb(solid):
    b = solid.val().BoundingBox()
    return b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax


# --- Review Focus 1: fidelity and citations ----------------------------------------------------------------
def test_every_new_part_has_a_valid_fidelity(fuse):
    for n in NEW_PARTS:
        assert n in fuse, n
        assert fuse[n].fidelity in FIDELITIES, n
        assert n in fb.PART_NAMES  # the owner's words, never the internal name


def test_book_and_derived_new_parts_cite_a_registered_page(fuse):
    for n in NEW_PARTS:
        p = fuse[n]
        if p.fidelity in {"book", "derived"}:
            assert p.cite, n
            for c in p.cite:
                check_citation(c)
                assert c.startswith("plans-1980:p4"), (n, c)  # p45-p49


def test_canard_cutout_and_carved_corners_are_representational(fuse):
    assert fuse["canard_cutout"].fidelity == "representational"
    carved = fb.carved_box()
    assert set(carved) == {"bottom", "side_left", "side_right"}
    for n, p in carved.items():
        assert p.fidelity == "representational", n
        assert "fitted" in p.note, n
    assert fb.FITTED_CORNER_RADIUS > 0


def test_canard_cutout_floor_is_the_printed_waterline_and_outline_is_fitted(fuse):
    p = fuse["canard_cutout"]
    x0, x1, y0, y1, z0, z1 = _bb(p.solid)
    assert z0 == pytest.approx(fb.z_of_wl(18.9), abs=1e-6)  # book, plans-1980:p45
    assert x0 == pytest.approx(G.fs_f22, abs=1e-6)
    assert x1 > G.fs_f28 + fb.FITTED_F28_THICKNESS  # just aft of F28
    assert "plans-1980:p45" in p.note or "p45" in p.note
    assert "fitted" in p.note


def test_rollover_note_names_the_fitted_reading_and_the_12_7_check(fuse):
    p = fuse["rollover"]
    assert p.fidelity == "derived"
    assert {"plans-1980:p47", "plans-1980:p48"} <= set(p.cite)
    assert "FITTED_ROLLOVER_SHOULDER_WL" in p.note and "fitted" in p.note and "12.7" in p.note
    assert not hasattr(fb, "FITTED_ROLLOVER_TILT_DEG")
    assert fb.FITTED_ROLLOVER_SHOULDER_WL == G.side_panel_top_wl


def test_canard_cutout_is_a_void_and_the_rest_are_not(fuse):
    assert fuse["canard_cutout"].void
    assert not any(p.void for n, p in fuse.items() if n != "canard_cutout")


def test_new_parts_are_valid_closed_solids(fuse):
    for n in NEW_PARTS:
        for s in fuse[n].solid.solids().vals():
            assert s.isValid() and s.Volume() > 0, n
            assert s.Shells()[0].Closed(), n


def test_carved_parts_are_valid_and_lose_a_little_material(fuse):
    for n, p in fb.carved_box().items():
        v, v0 = p.solid.val().Volume(), fuse[n].solid.val().Volume()
        assert p.solid.val().isValid(), n
        assert 0.97 * v0 < v < v0, n  # corners rounded, nothing else
    # the uncarved parts stay (chapters 4-6 build the uncarved box)
    assert fuse["bottom"].solid.val().Volume() == pytest.approx(3278.757, rel=1e-4)


def test_lower_aft_corner_stays_sharp_where_the_gear_bolts_pass(fuse):
    # the bottom foam ends ahead of the gear pad (FS 125 - 15.3 = 109.7), and no side lower edge is carved
    assert fuse["bottom"].solid.val().BoundingBox().xmax < 125.0 - 15.3
    carved = fb.carved_box()
    for n in ("side_left", "side_right"):
        lo = max(f.Area() for f in carved[n].solid.faces().vals() if f.normalAt().z < -0.9)
        lo0 = max(f.Area() for f in fuse[n].solid.faces().vals() if f.normalAt().z < -0.9)
        assert lo == pytest.approx(lo0, rel=1e-6), n


# --- belt insert ------------------------------------------------------------------------------------------------
def test_belt_insert_is_left_only_5_in_long_in_the_lower_corner(fuse):
    x0, x1, y0, y1, z0, z1 = _bb(fuse["belt_insert"].solid)
    assert (x0, x1) == pytest.approx(G.belt_insert_fs_range, abs=0.05)
    assert x1 - x0 == pytest.approx(5.0, abs=0.05)
    assert y1 < 0  # left side only
    out = half_width(x0) + G.bottom_trim_outboard
    assert y0 == pytest.approx(-out, abs=0.05)  # at the bottom's outer edge
    assert z0 == pytest.approx(fuse["bottom"].solid.val().BoundingBox().zmin, abs=0.1)  # at the lower corner
    assert fuse["belt_insert"].fidelity == "derived" and "plans-1980:p46" in fuse["belt_insert"].cite


# --- belt pads ----------------------------------------------------------------------------------------------------
def test_belt_attach_pads_front_5_forward_and_rear_8_forward(fuse):
    solids = fuse["belt_attach"].solid.solids().vals()
    assert len(solids) == 4
    front, rear = fb.belt_attach_stations()
    assert front == pytest.approx(G.fs_front_seat_bkhd_bottom - 5.0)
    assert rear == pytest.approx(G.fs_rear_seat_bkhd_bottom - 8.0)
    centres = sorted((s.Center().x, 1 if s.Center().y > 0 else -1) for s in solids)
    assert [c[0] for c in centres] == pytest.approx([front, front, rear, rear], abs=0.05)
    assert sorted(c[1] for c in centres) == [-1, -1, 1, 1]  # a pad on each side at each station
    for s in solids:  # against the side's inside face, on the bottom foam
        bb = s.BoundingBox()
        hw = half_width(s.Center().x)
        assert max(abs(bb.ymin), abs(bb.ymax)) == pytest.approx(hw, abs=0.05)
    assert fuse["belt_attach"].fidelity == "derived" and "plans-1980:p49" in fuse["belt_attach"].cite


# --- step -----------------------------------------------------------------------------------------------------------
def test_step_is_a_bent_eighth_plate_on_the_left_at_the_front_belt(fuse):
    p = fuse["step"]
    x0, x1, y0, y1, z0, z1 = _bb(p.solid)
    w, a, b = G.step_size
    front = fb.belt_attach_stations()[0]
    assert x1 - x0 == pytest.approx(w, abs=0.01)
    assert y1 - y0 == pytest.approx(a, abs=0.01) and z1 - z0 == pytest.approx(b, abs=0.01)
    assert (x0 + x1) / 2 == pytest.approx(front, abs=0.01)
    assert y1 < 0  # left side
    # plate volume: legs 4.5 + 4.5 less the shared corner, 1/8 thick, 1.8 wide, with a rounded inside bend
    t, ri = G.step_thickness, G.step_min_bend_radius
    area = 2 * a * t - t * t - (1 - math.pi / 4) * ((ri + t) ** 2 - ri**2)
    assert p.solid.val().Volume() == pytest.approx(w * area, rel=0.01)
    assert p.fidelity == "derived" and "plans-1980:p49" in p.cite


# --- roll-over ---------------------------------------------------------------------------------------------------
X_FRONT = G.fs_front_seat_bkhd_top - G.rollover_shoulder_top[1]  # 79.05, derived: the tops run 2.7 back to the bulkhead top
HB, PH = G.rollover_base_height, G.rollover_peak_height


def test_rollover_front_piece_is_vertical_at_fs_79_05_and_23_wide():
    pc = fb.rollover_pieces()
    assert pc["x_front"] == pytest.approx(79.05, abs=1e-9) == pytest.approx(X_FRONT)
    plate = pc["plate"]
    x0, x1, y0, y1, z0, z1 = _bb(plate)
    assert x0 == pytest.approx(79.05, abs=0.02)  # a plane of constant F.S.
    assert x1 - x0 == pytest.approx(G.rollover_foam_thickness, abs=0.02)
    assert y1 - y0 == pytest.approx(G.rollover_width, abs=0.02)
    front = [f for f in plate.faces().vals() if f.normalAt().x < -0.999]
    assert front and all(abs(f.Center().x - 79.05) < 0.02 for f in front)
    assert (y0, y1) == pytest.approx((-11.5, 11.5), abs=0.02)


def test_rollover_peak_is_at_wl_35_6_and_12_6_above_the_shoulder_line():
    pc = fb.rollover_pieces()
    assert pc["z_shoulder"] == pytest.approx(fb.z_of_wl(23.0))  # fitted: level with the top longerons
    z1 = _bb(pc["plate"])[5]
    assert z1 == pytest.approx(fb.z_of_wl(35.6), abs=0.05)
    assert z1 - pc["z_shoulder"] == pytest.approx(PH, abs=0.05)
    # the shoulder line on the plate: the top edge between the peak's foot and the notches
    vs = [(v.Y, v.Z) for v in pc["plate"].vertices().vals()]
    assert max(z for y, z in vs if 4.1 < abs(y) < 10.9) == pytest.approx(pc["z_shoulder"], abs=1e-6)


def test_rollover_front_piece_outline():
    """Shoulders 7.3, peak base 8.4, notches 0.7 x 1.4, read off the uncarved front piece (Y across, Z up)."""
    plate = fb.rollover_pieces()["plate_full"]
    zs = fb.rollover_pieces()["z_shoulder"]
    face = [f for f in plate.faces().vals() if f.normalAt().x < -0.999][0]
    vs = [(round(v.Y, 6), round(v.Z, 6)) for v in face.Vertices()]
    shoulder_line = sorted(y for y, z in vs if abs(z - zs) < 1e-6)  # notch inner corners, peak base, mirrored
    peak_base = [y for y in shoulder_line if abs(y) < 5.0]
    assert max(peak_base) - min(peak_base) == pytest.approx(G.rollover_peak_base)  # 8.4
    assert G.rollover_width / 2 - max(peak_base) == pytest.approx(G.rollover_shoulder)  # 7.3 out to the edge
    assert max(y for y, _ in vs) - min(y for y, _ in vs) == pytest.approx(23.0)
    notch = {z for y, z in vs if abs(y - (G.rollover_width / 2 - G.rollover_notch[0])) < 1e-6}
    assert round(zs - G.rollover_notch[1], 6) in notch  # the notch floor, 1.4 below the shoulder line
    assert min(z for _, z in vs) == pytest.approx(zs - HB)  # the printed 4 in base, before it is carved to the bulkhead


def test_rollover_base_is_carved_to_the_bulkhead():
    pc = fb.rollover_pieces()
    carved_bottom = _bb(pc["plate"])[4]
    assert carved_bottom > pc["z_shoulder"] - HB + 0.5  # it meets the bulkhead above its printed bottom
    # the bulkhead's back face crosses the plane 0.75 above the printed bottom (the captain's "about 1 in"); the piece
    # that remains starts where the bulkhead's front face leaves it, 1.56 above
    assert carved_bottom < pc["z_shoulder"] - HB + 2.0
    assert len(pc["plate"].solids().vals()) == 1  # no loose strip left under the bulkhead


def test_rollover_depth_is_4_5_at_the_shoulder_line_and_3_at_the_peak():
    pc = fb.rollover_pieces()
    x_front, zs = pc["x_front"], pc["z_shoulder"]
    tri = pc["triangle"]
    aft = [f for f in tri.faces().vals() if f.geomType() == "PLANE" and f.normalAt().x > 0.9 and f.Area() > 10][0]
    pts = [(v.X, v.Z) for v in aft.Vertices()]
    base = [x for x, z in pts if abs(z - zs) < 0.05]
    apex = max(pts, key=lambda p: p[1])
    assert max(base) - x_front == pytest.approx(max(G.rollover_side_ends), abs=0.05)  # 4.5 at the shoulder line
    assert apex[0] - x_front == pytest.approx(min(G.rollover_side_ends), abs=0.05)  # 3.0 at the peak
    assert apex[1] - zs == pytest.approx(PH, abs=0.05)


def test_back_triangle_slant_is_the_printed_12_7_and_it_leans_forward():
    pc = fb.rollover_pieces()
    tri = pc["triangle"]
    aft = [f for f in tri.faces().vals() if f.geomType() == "PLANE" and f.normalAt().x > 0.9 and f.Area() > 10][0]
    pts = [(v.X, v.Y, v.Z) for v in aft.Vertices()]
    apex = max(pts, key=lambda p: p[2])
    base = [p for p in pts if abs(p[2] - pc["z_shoulder"]) < 0.05]
    slant = math.dist(apex, (sum(p[0] for p in base) / 2, 0.0, base[0][2]))
    assert slant == pytest.approx(12.7, abs=0.05)  # 12.69: sqrt(12.6**2 + 1.5**2) checks the 4.5 -> 3 depth
    assert slant == pytest.approx(math.hypot(PH, 4.5 - 3.0))
    assert pc["lean_deg"] == pytest.approx(math.degrees(math.atan(1.5 / PH)), abs=1e-6)
    assert max(p[1] for p in base) - min(p[1] for p in base) == pytest.approx(G.rollover_back_triangle[0], abs=0.02)  # 8.1 base


def test_rollover_roof_sides_run_4_5_wide_at_the_bottom_3_at_the_top():
    pc = fb.rollover_pieces()
    for sgn, roof in zip((-1, 1), pc["roofs"]):
        g = pc["roof_geom"][sgn]
        # in the roof's plane: the front edge A-B, the back edge D-C, the end widths 4.5 and 3.0
        assert math.dist(g["A"], g["D"]) == pytest.approx(max(G.rollover_side_ends), abs=0.05)
        assert math.dist(g["B"], g["C"]) == pytest.approx(min(G.rollover_side_ends), abs=0.05)
        assert g["length"] == pytest.approx(G.rollover_side_length, abs=0.35)  # printed 13 (CP26 LPC 37); 13.28 from 8.4 x 12.6
        assert roof.val().isValid()


def test_map_slot_in_the_right_roof_side_only():
    pc = fb.rollover_pieces()
    left, right = pc["roofs"]
    sh, sl = G.rollover_map_slot
    T = G.rollover_foam_thickness
    ci = G.rollover_insert
    # the left roof minus the right equals the slot's volume plus the canopy pocket (both right only), measured on the solids
    d = left.val().Volume() - right.val().Volume()
    assert d == pytest.approx(sh * sl * T + ci[0] * ci[1] * ci[2], rel=0.02)
    # the slot is open: probe the right roof's mid-thickness at its centre
    g = pc["roof_geom"][1]
    s0, c0 = fb.FITTED_ROLLOVER_SLOT_CENTRE
    import numpy as np
    xd, yd, n = g["xd"], g["yd"], g["n"]
    centre = g["A"] + s0 * xd + c0 * yd - n * T / 2
    ball = fb._box(*(centre[0] - 0.2, centre[0] + 0.2, centre[1] - 0.2, centre[1] + 0.2, centre[2] - 0.2, centre[2] + 0.2))
    assert not right.intersect(ball).vals() or right.intersect(ball).val().Volume() < 1e-9
    mirror = centre * np.array([1, -1, 1])
    ball_l = fb._box(*(mirror[0] - 0.2, mirror[0] + 0.2, mirror[1] - 0.2, mirror[1] + 0.2, mirror[2] - 0.2, mirror[2] + 0.2))
    assert left.intersect(ball_l).val().Volume() > 0.01  # the left roof is whole there
    # no round hole anywhere but the back triangle
    assert not [f for f in pc["main"].faces().vals() if f.geomType() == "CYLINDER"]


def test_baggage_hole_in_the_back_triangle_only(fuse):
    pc = fb.rollover_pieces()
    cyl = [f for f in fuse["rollover"].solid.faces().vals() if f.geomType() == "CYLINDER"]
    assert cyl
    assert [f for f in pc["triangle"].faces().vals() if f.geomType() == "CYLINDER"]
    for f in cyl:
        cy = f._geomAdaptor().Cylinder()
        assert cy.Radius() == pytest.approx(G.rollover_baggage_hole_dia / 2)
        d = cy.Axis().Direction()  # through the back triangle, along its normal (leaning 6.8 degrees)
        assert abs(d.X()) > 0.99 and abs(d.Y()) < 1e-6


def test_rollover_sits_inside_the_fuselage_width(fuse):
    r = fuse["rollover"].solid
    for x, y, _z in _verts(r):
        assert abs(y) <= half_width(min(x, 120.0)) + 0.05, (x, y)


def test_rollover_touches_the_front_seat_bulkhead_without_entering_it(fuse):
    r = fuse["rollover"].solid
    bk = fuse["front_seat_bkhd"].solid
    assert r.val().distance(bk.val()) <= 0.05
    inter = r.intersect(bk)
    assert (inter.val().Volume() if inter.vals() else 0.0) <= 0.01
    # the box overhangs the bulkhead top aft: 4.5 - 2.7 = 1.8 at the peak base
    assert _bb(r)[1] - G.fs_front_seat_bkhd_top == pytest.approx(max(G.rollover_side_ends) - G.rollover_shoulder_top[1], abs=0.05)


@pytest.mark.parametrize("name", ["top_longeron_left", "top_longeron_right"])
def test_rollover_does_not_intersect_the_longerons(fuse, name):
    inter = fuse["rollover"].solid.intersect(fuse[name].solid)
    assert (inter.val().Volume() if inter.vals() else 0.0) <= 0.02


def test_rollover_shell_is_one_solid(fuse):
    assert len(fuse["rollover"].solid.solids().vals()) == 1


def test_rollover_inserts_three_flush_with_the_inside_face(fuse):
    ins = fuse["rollover_inserts"]
    assert ins.fidelity == "derived" and {"plans-1980:p47", "plans-1980:p48"} <= set(ins.cite)
    solids = ins.solid.solids().vals()
    assert len(solids) == 3
    ix, iy, it = G.rollover_insert
    for s in solids:
        assert s.Volume() == pytest.approx(ix * iy * it, rel=0.03)  # a harness insert loses a sliver to the bevel at the bulkhead
    pc = fb.rollover_pieces()
    T = G.rollover_foam_thickness
    harness = [s for s in solids if s.Center().z < pc["z_shoulder"]]
    canopy = [s for s in solids if s.Center().z >= pc["z_shoulder"]]
    assert len(harness) == 2 and len(canopy) == 1
    W = G.rollover_width / 2
    for s in harness:  # in the shoulder tops: lower face flush with the underside; outboard edge 4.0 from the outer end
        bb = s.BoundingBox()
        assert bb.zmin == pytest.approx(pc["z_shoulder"] - T, abs=1e-6)
        assert W - max(abs(bb.ymin), abs(bb.ymax)) == pytest.approx(G.rollover_harness_insert_spacing, abs=0.02)  # 4.0
        assert max(abs(bb.ymin), abs(bb.ymax)) - min(abs(bb.ymin), abs(bb.ymax)) == pytest.approx(ix, abs=0.02)
        assert (bb.xmin + bb.xmax) / 2 == pytest.approx(pc["x_front"] + G.rollover_shoulder_top[1] / 2, abs=0.05)
    assert sorted(1 if s.Center().y > 0 else -1 for s in harness) == [-1, 1]
    # canopy insert: right roof only, 1.5 below the peak (along the slope), flush with the inside face
    (c,) = canopy
    assert c.Center().y > 0
    g = pc["roof_geom"][1]
    along = [(v.X - g["A"][0]) * g["xd"][0] + (v.Y - g["A"][1]) * g["xd"][1] + (v.Z - g["A"][2]) * g["xd"][2] for v in c.Vertices()]
    assert g["length"] - max(along) == pytest.approx(G.rollover_canopy_insert_from_peak[0], abs=0.02)
    assert max(along) - min(along) == pytest.approx(G.rollover_canopy_insert_from_peak[1], abs=0.02)
    depth = [-((v.X - g["A"][0]) * g["n"][0] + (v.Y - g["A"][1]) * g["n"][1] + (v.Z - g["A"][2]) * g["n"][2]) for v in c.Vertices()]
    assert max(depth) == pytest.approx(T, abs=1e-6)  # its inner face is the foam's inside face
    # the pockets leave the insert and the foam non-overlapping
    inter = fuse["rollover"].solid.intersect(ins.solid)
    assert (inter.val().Volume() if inter.vals() else 0.0) < 1e-6


# --- Review Focus 6: the skin schedule ------------------------------------------------------------------------
def _third(side):
    return fp.SCOPE[(f"f07.skin-{side}", "forward of the front seat bulkhead only, along the longerons")].targets[0]


def _strip(side):
    return fp.SCOPE[(f"f07.skin-{side}", "3 in strip, tapered 52/50/48 in, FS 60 to 110")].targets[0]


@pytest.mark.parametrize("side", ["right", "left"])
def test_third_ply_ends_on_the_front_seat_bulkhead_line(side):
    t = _third(side)
    faces = t.region.faces(t.part)
    assert faces
    pts = []
    for f in faces:
        pts += [(v.X, v.Z) for v in f.Vertices()]
        for e in f.Edges():
            for i in range(21):
                q = e.positionAt(i / 20)
                pts.append((q.x, q.z))
    for x, z in pts:  # nothing aft of the slanted line (63.55 at the floor to 81.75 at the top)
        assert x <= fb.front_bulkhead_line_fs(z) + 1e-6, (x, z)
    # and the ply reaches it: at the top edge the ply ends at FS 81.75, at the side's bottom at FS 63.55
    top = [x for x, z in pts if abs(z - fb.Z_TOP) < 1e-6]
    assert max(top) == pytest.approx(G.fs_front_seat_bkhd_top, abs=0.05)
    zb = fb.bottom_z(G.fs_front_seat_bkhd_bottom)
    low = [x for x, z in pts if abs(z - zb) < 0.05]
    assert max(low) == pytest.approx(G.fs_front_seat_bkhd_bottom, abs=0.1)
    # no area at all aft of the line
    aft = fp._clip_solid(("fwd_of_front_bkhd",))
    side_face_area = sum(f.Area() for f in fp._faces(t.part, build_fuselage()[t.part], "outside"))
    in_area = sum(f.Area() for f in faces)
    assert 0 < in_area < side_face_area


@pytest.mark.parametrize("side", ["right", "left"])
def test_strip_spans_fs_60_to_110_and_is_3_in_wide(side):
    t = _strip(side)
    faces = t.region.faces(t.part)
    xs = [v.X for f in faces for v in f.Vertices()]
    zs = [v.Z for f in faces for v in f.Vertices()]
    assert min(xs) == pytest.approx(G.skin_third_ply_fs_range[0], abs=0.05)
    assert max(xs) == pytest.approx(G.skin_third_ply_fs_range[1], abs=0.05)
    assert max(zs) - min(zs) == pytest.approx(G.skin_strip_width, abs=0.05)
    assert max(zs) == pytest.approx(fb.Z_TOP, abs=1e-6)  # along the top of the side
    area = sum(f.Area() for f in faces)
    assert area == pytest.approx(3.0 * 50.0, rel=0.01)
    assert sum(G.skin_strip_lengths) == pytest.approx(3 * 50.0)  # taper 52/50/48: nominal 50 is exact for the three


def test_skin_rows_are_mapped_in_book_order(plies):
    ops = [p.op for p in plies if p.op.startswith("f07.skin")]
    assert ops.index("f07.skin-right") < ops.index("f07.skin-left")
    right = [p for p in plies if p.op == "f07.skin-right"]
    # two crossed UND plies at +-30 on the side and on the bottom, then the third ply (0), then three strip plies
    by_part = {}
    for p in right:
        by_part.setdefault(p.part, []).append(p)
    assert [p.orientation_deg for p in by_part["side_right"]] == [30.0, -30.0, 0.0, None, None, None]
    assert [p.orientation_deg for p in by_part["bottom"]] == [30.0, -30.0]
    assert all(p.cloth == "UND" for p in right)
    assert all(p.cite == "plans-1980:p46" for p in right)
    assert all(p.lower_bound for p in right if p.where.startswith("crossed"))  # wrap and aft lap not counted


def test_bottom_skin_runs_one_inch_past_the_centre_line_from_each_side():
    for side, sgn in (("right", 1), ("left", -1)):
        t = [x for x in fp.SCOPE[(f"f07.skin-{side}", "crossed 30 degrees to the longerons, whole skin")].targets if x.part == "bottom"][0]
        ys = [v.Y for f in t.region.faces("bottom") for v in f.Vertices()]
        assert min(ys) * sgn if sgn < 0 else True
        far = -min(ys) if sgn > 0 else max(ys)
        assert far == pytest.approx(G.skin_bottom_overlap / 2, abs=0.05)  # 2 in overlap in all


def test_skin_shell_covers_one_side_and_the_bottom_to_one_inch_past_the_centre_line():
    for side, sgn in (("right", 1), ("left", -1)):
        sh = fp.skin_shell(side)
        for s in sh.solids().vals():
            assert s.isValid()
        bb = sh.val().BoundingBox() if len(sh.vals()) == 1 else __import__("cadquery").Compound.makeCompound(sh.vals()).BoundingBox()
        assert (bb.ymax if sgn > 0 else -bb.ymin) > 12.0  # the side's outer face
        far = -bb.ymin if sgn > 0 else bb.ymax
        assert far == pytest.approx(1.0, abs=0.1)
    with pytest.raises(fp.FusePlyError):
        fp.skin_shell("up")


# --- plies: scope and chapters 4-6 unchanged ------------------------------------------------------------------
def test_scope_problems_empty_for_chapters_4_to_8():
    rows = fp.material_rows(GRAPH)
    assert {GRAPH.ops[o].chapter for o, _ in rows} == {4, 5, 6, 7, 8}
    assert fp.scope_problems(rows, set(GRAPH.ops)) == []


def test_chapter_7_and_8_rows_mapped_or_excluded_with_reasons():
    rows = [(o, w) for o, w in fp.material_rows(GRAPH) if GRAPH.ops[o].chapter in (7, 8)]
    assert len(rows) == 13
    mapped = [r for r in rows if r in fp.SCOPE]
    excluded = [r for r in rows if r in fp.EXCLUDED]
    assert len(mapped) + len(excluded) == 13 and not set(mapped) & set(excluded)
    assert len(mapped) == 9 and len(excluded) == 4
    for r in excluded:
        reason, affected = fp.EXCLUDED[r]
        assert len(reason) > 20 and affected


def test_belt_pads_glass_is_the_insert_plus_one_inch_all_round(plies):
    pads = [p for p in plies if p.part == "belt_attach"]
    assert len(pads) == 7 and {p.cloth for p in pads} == {"BID"}
    ln, wd = fb.FITTED_BELT_PAD
    assert pads[0].area_in2 == pytest.approx(4 * (ln + 2) * (wd + 2))


def test_rollover_ply_areas_follow_the_rebuilt_faces(plies):
    ro = [p for p in plies if p.part == "rollover"]
    assert ro[0].area_in2 == pytest.approx(fb.rollover_face_area("inside")[0])
    assert ro[1].area_in2 == pytest.approx(fb.rollover_face_area("outside")[0])
    pc = fb.rollover_pieces()
    # outside >= the roof sides' outer faces (2 x 13.3 x ~3.7) plus the peak above the shoulder line (8.4 x 12.6 / 2)
    assert ro[1].area_in2 > 2 * 13.0 * 3.5 + 0.5 * 8.4 * 12.6 - 1
    assert pc["tops"]


def test_rollover_plies_inside_and_outside(plies):
    ro = [p for p in plies if p.part == "rollover"]
    assert [p.where for p in ro] == ["inside faces"] + ["outside skin, 1 in overlap onto seat bulkhead and sides"] * 2
    assert ro[0].area_in2 > 0 and not ro[0].lower_bound
    assert ro[1].lower_bound  # the 1 in lap onto the bulkhead and sides is not counted
    assert all(p.fidelity == "derived" for p in ro)


# Areas of the 28 chapter 4-6 plies before chapters 7 and 8 entered the model (plies() at e65bf84, rounded to 6 places).
CH46_AREAS = [
    ("fuselage.front_seat_bkhd.p1", 626.438932),
    ("fuselage.front_seat_bkhd.p2", 626.438932),
    ("fuselage.front_seat_bkhd.p3", 626.438932),
    ("fuselage.rear_seat_bkhd.p1", 283.267315),
    ("fuselage.rear_seat_bkhd.p2", 283.267315),
    ("fuselage.rear_seat_bkhd.p3", 241.053569),
    ("fuselage.rear_seat_bkhd.p4", 241.053569),
    ("fuselage.panel.p1", 343.045089),
    ("fuselage.f22.p1", 455.4),
    ("fuselage.f28.p1", 92.0),
    ("fuselage.panel.p2", 343.045089),
    ("fuselage.f22.p2", 455.4),
    ("fuselage.f28.p2", 92.0),
    ("fuselage.panel.p3", 343.045089),
    ("fuselage.f22.p3", 455.4),
    ("fuselage.f28.p3", 92.0),
    ("fuselage.panel.p4", 343.045089),
    ("fuselage.f22.p4", 455.4),
    ("fuselage.f28.p4", 92.0),
    ("fuselage.firewall.p1", 307.617391),
    ("fuselage.firewall.p2", 307.617391),
    ("fuselage.side_left.p1", 1994.758071),
    ("fuselage.side_right.p1", 1995.960765),
    ("fuselage.side_left.p2", 1994.758071),
    ("fuselage.side_right.p2", 1995.960765),
    ("fuselage.bottom.p1", 2050.96172),
    ("fuselage.bottom.p2", 2050.96172),
    ("fuselage.bottom.p3", 382.21354),
]


def test_chapter_4_to_6_plies_unchanged(plies):
    now = [p for p in plies if p.op[:3] in {"f04", "f05", "f06"}]
    assert [(p.node, round(p.area_in2, 6)) for p in now] == CH46_AREAS
    # chapter 4-6 plies keep their node numbers: new plies on the same parts come after them
    for p in plies:
        if p.op[:3] in {"f07", "f08"} and p.part in {"side_left", "side_right", "bottom"}:
            assert p.order > max(q.order for q in now if q.part == p.part)
