# tests/test_landing_gear_book.py
"""Main gear geometry (chapter 9, plans-1980:p50-p53, p171): stations, fidelity tags, jig, poses."""
import json

import numpy as np
import pytest
from cadquery import Vector

from config.aircraft_config import GEOMETRY_PROVENANCE, GeometricParams
from core import landing_gear_book as lg
from core.fuselage_book import FIDELITIES, Z_TOP, z_of_wl
from core.sources import check_citation

G = lg.G


@pytest.fixture(scope="module")
def parts():
    return lg.build_gear()


def test_axle_station_is_the_printed_one():  # Review Focus 2
    assert G.fs_main_axle == pytest.approx(G.fs_spar_aft_face - 15.0)
    assert G.fs_main_axle == pytest.approx(110.5)
    for ax in lg.axle_points().values():
        assert ax.fs == pytest.approx(110.5)
        assert ax.wl == pytest.approx(-22.0)
        assert ax.xyz[0] == pytest.approx(110.5)
        assert ax.xyz[2] == pytest.approx(z_of_wl(-22.0))
        assert ax.tags["fs"]["fidelity"] == "book" and ax.tags["wl"]["fidelity"] == "book"
        assert ax.tags["bl"]["fidelity"] == "representational"
        check_citation(ax.tags["fs"]["cite"].split(";")[0].split(" ")[0])
    ax = lg.axle_points()
    assert ax["left"].bl == pytest.approx(-ax["right"].bl)
    assert ax["right"].bl == pytest.approx(lg.FITTED_TRACK / 2)


def test_the_track_is_fitted_and_nowhere_else():  # Review Focus 2
    assert not hasattr(GeometricParams, "track") and not any("track" in f for f in GEOMETRY_PROVENANCE)
    assert not any("track" in f.lower() for f in GeometricParams.__dataclass_fields__)
    from core.ledger import fuselage_ledger_json

    blob = json.dumps(fuselage_ledger_json())
    assert str(lg.FITTED_TRACK) not in blob and "FITTED_TRACK" not in blob
    assert "track" not in json.dumps(lg.ground_handling()["main_axle_fs"])
    assert "fitted, not book" in open(lg.__file__).read().split("FITTED_TRACK =")[1].split("\n")[0]


def test_every_part_has_a_valid_fidelity_and_cites(parts):  # Review Focus 1
    assert set(parts) == {"strut", "extrusions", "gear_tubes", "jig_blocks", "datum_board", "axles"}
    for name, p in parts.items():
        assert p.fidelity in FIDELITIES, name
        if p.fidelity in {"book", "derived"}:
            assert p.cite, name
        for c in p.cite:
            check_citation(c)
        assert p.solid.val().isValid(), name
        assert p.solid.val().Volume() > 0, name
    for name in ("strut", "extrusions", "gear_tubes", "jig_blocks", "axles"):
        assert parts[name].fidelity == "representational", name
    assert parts["datum_board"].fidelity == "derived"
    assert "not printed" in parts["strut"].note and "1/4 x 2 x 2" in parts["extrusions"].note


def test_datum_boards_stand_vertical_at_the_spar_aft_face(parts):  # p50 figure 1A
    sol = parts["datum_board"].solid.val().Solids()
    assert len(sol) == 2  # one each side ("do this on both sides")
    ax_z = z_of_wl(G.wl_main_axle)
    for b in sol:
        bb = b.BoundingBox()
        assert bb.xmin == pytest.approx(125.5, abs=0.01) == pytest.approx(G.fs_spar_aft_face, abs=0.01)
        assert abs(b.Center().y) == pytest.approx(G.bl_gear_datum, abs=0.01)  # B.L. 26.75 each side
        assert bb.zmax == pytest.approx(Z_TOP)  # stands on the table plane when inverted
        assert bb.zmin < ax_z - 4  # long axis vertical, reaching past the (inverted) axle height
        assert (bb.zmax - bb.zmin) > 5 * (bb.ymax - bb.ymin) and (bb.zmax - bb.zmin) > 5 * (bb.xmax - bb.xmin)
    assert sol[0].Center().y * sol[1].Center().y < 0
    assert "chapter 14" in parts["datum_board"].note and "CP36 LPC 112" in parts["datum_board"].note


def _leg_slope_from_vertical_deg(path, end):
    p = np.array(path)
    d = (p[-1] - p[-4]) if end else (p[0] - p[3])
    return np.degrees(np.arctan2(abs(d[1]), abs(d[2])))


def test_strut_is_a_flat_bottomed_bow_with_steep_outboard_legs(parts):
    from core.fuselage_book import bottom_z

    path = np.array(lg.strut_path())
    ax = lg.axle_points()
    assert path[0] == pytest.approx(ax["left"].xyz) and path[-1] == pytest.approx(ax["right"].xyz)  # exact axle points
    assert path[0][0] == pytest.approx(110.5) and path[-1][2] == pytest.approx(z_of_wl(-22.0))
    ya = abs(lg.attach_points()["right"][1])
    centre = path[np.abs(path[:, 1]) <= ya + 1e-9]
    zc = lg._centre_z()
    assert np.allclose(centre[:, 2], zc)  # flat across the bottom between the attach tabs
    assert zc < bottom_z(lg._fs_tube()) - 1.0  # at the bottom's underside, below the side's bottom edge
    right = path[len(path) // 2:]
    assert np.all(np.diff(right[:, 2]) <= 1e-9)  # never rises on the way down the right leg
    assert np.all(np.diff(right[:, 1]) >= -1e-9)  # and keeps going outboard
    assert np.all(np.diff(right[:, 0]) <= 1e-9)  # raking forward going down (side view)
    ang = _leg_slope_from_vertical_deg(right, True)
    assert 20.0 <= ang <= 35.0  # p51 top figure: steep, outward-leaning, not horizontal
    assert np.allclose(path[:, 1], -path[::-1, 1]) and np.allclose(path[:, 2], path[::-1, 2])  # symmetric
    # the solid reaches the axle points and the centre section's underside
    bb = parts["strut"].solid.val().BoundingBox()
    assert bb.ymax >= ax["right"].bl - 0.5 and bb.zmin <= ax["right"].xyz[2] + 0.1


# --- inverted pose applies to the gear too ---------------------------------------------------------
def test_inverted_gear_axles_are_above_the_inverted_fuselage_top_at_fs_110_5():
    from core.fuselage_book import build_fuselage

    inv = lg.inverted_pose()
    fus_top = max(inv.apply([[bb.xmin, bb.ymin, bb.zmin]])[0][2]
                  for bb in (p.solid.val().BoundingBox() for p in build_fuselage().values()))
    pts = lg.inverted_axle_points()
    assert set(pts) == {"left", "right"}
    for name, p in pts.items():
        assert p[2] > fus_top, name  # legs point up: axles above the (inverted) top surface
        assert p[0] == pytest.approx(110.5)
        assert abs(p[1]) == pytest.approx(lg.FITTED_TRACK / 2)
    # the solids follow the same pose: every inverted gear part's axle stub sits above the fuselage
    g = lg.inverted_gear()
    assert g["axles"].val().BoundingBox().zmin > fus_top
    assert g["strut"].val().BoundingBox().zmax > fus_top + 20
    assert g["datum_board"].val().BoundingBox().zmin == pytest.approx(Z_TOP)  # boards stand on the table
    assert g["datum_board"].val().BoundingBox().zmax > pts["left"][2]  # and reach past the axle


def test_jig_block_dimensions_measured_on_the_solid():  # p53 figure 1
    b = lg.jig_block_solid().val()
    bb = b.BoundingBox()
    assert bb.ymax - bb.ymin == pytest.approx(2.0)
    assert bb.xmax - bb.xmin == pytest.approx(0.25)
    assert bb.zmax == pytest.approx(1.0)  # radius 1 above the hole centre
    assert bb.zmin == pytest.approx(-(0.7 + 0.8))
    # hole is 5/8 diameter, at the origin
    assert not b.isInside(Vector(0.125, 0, 0.3))
    assert not b.isInside(Vector(0.125, 0, -0.3))
    assert b.isInside(Vector(0.125, 0, 0.35))
    assert b.isInside(Vector(0.125, 0.35, 0))
    # round top of radius 1: inside at 0.98, outside at 1.02 along z; the corner at (1, 1) is cut away
    assert b.isInside(Vector(0.125, 0, 0.98)) and not b.isInside(Vector(0.125, 0, 1.02))
    assert not b.isInside(Vector(0.125, 0.9, 0.9))
    # bevelled to a sharp edge: full thickness at the top of the bevel, nothing but the edge at the bottom
    assert b.isInside(Vector(0.2, 0.5, -0.71)) and not b.isInside(Vector(0.2, 0.5, -1.45))
    assert b.isInside(Vector(0.001, 0.5, -1.49))


def test_four_blocks_two_per_tube_with_065_showing(parts):
    blocks = parts["jig_blocks"].solid.val().Solids()
    tubes = parts["gear_tubes"].solid.val().Solids()
    assert len(blocks) == 4 and len(tubes) == 2
    for t in tubes:
        tb = t.BoundingBox()
        assert tb.xmax - tb.xmin == pytest.approx(6.75)
        mine = sorted((b.BoundingBox() for b in blocks if tb.ymin - 1 < b.Center().y < tb.ymax + 1), key=lambda b: b.xmin)
        assert len(mine) == 2
        assert mine[0].xmin - tb.xmin == pytest.approx(0.65)
        assert tb.xmax - mine[1].xmax == pytest.approx(0.65)
    assert tubes[0].BoundingBox().zmax - tubes[0].BoundingBox().zmin == pytest.approx(0.625)


def test_tube_is_5_8_od_with_a_049_wall(parts):
    t = parts["gear_tubes"].solid.val().Solids()[0]
    import math

    ann = math.pi * (0.3125**2 - (0.3125 - 0.049) ** 2) * 6.75
    assert t.Volume() == pytest.approx(ann, rel=1e-6)


def test_extrusions_are_four_quarter_two_by_two_angles(parts):
    sol = parts["extrusions"].solid.val().Solids()
    assert len(sol) == 4
    for s in sol:  # section 1/4 x 2 x 2: two legs of 2 and 1/4 thick, the corner counted once
        assert s.Volume() == pytest.approx((2.0 + 2.0 - 0.25) * 0.25 * lg.FITTED_EXT_LENGTH, rel=0.15)


def test_attach_points_sit_in_the_gear_pad_area():
    from core.fuselage_book import G as FG

    aft = FG.fs_f22 + FG.side_panel_length
    for p in lg.attach_points().values():
        assert aft - 15.3 < p[0] < aft  # within the p38 pad length from the side's aft end


def test_toe_in_leans_the_outboard_ends_forward(parts):
    ax = parts["axles"].solid.val().Solids()
    assert len(ax) == 2
    for s in ax:  # the stub starts on the axle point and runs outboard, forward-leaning
        c, p = s.Center(), lg.axle_points()["left" if s.Center().y < 0 else "right"].xyz
        assert abs(c.y) > abs(p[1]) and c.x < p[0]
    d_l, d_r = lg._axle_dir(-1), lg._axle_dir(1)
    assert d_l[1] < 0 < d_r[1] and d_l[0] < 0 and d_r[0] < 0
    assert np.degrees(lg._toe_in_rad()) == pytest.approx(np.degrees(np.arctan(0.325 / 24)))


# --- poses (Review Focus 5) -------------------------------------------------------------------------
def test_left_bank_45_puts_the_right_side_up():
    pose = lg.bank_pose(45.0)
    n_right = pose.rotation @ np.array([0.0, 1.0, 0.0])  # outward normal of the right side
    n_left = pose.rotation @ np.array([0.0, -1.0, 0.0])
    assert n_right[2] > 0.7 and n_left[2] < -0.7
    right_pt = pose.apply([[60.0, 10.0, Z_TOP]])[0]
    left_pt = pose.apply([[60.0, -10.0, Z_TOP]])[0]
    assert right_pt[2] > left_pt[2]
    # the axis is longitudinal: x unchanged, and the pivot is fixed
    assert right_pt[0] == pytest.approx(60.0)
    assert lg.bank_pose(45.0).apply([[0.0, 0.0, Z_TOP]])[0] == pytest.approx([0.0, 0.0, Z_TOP])


def test_zero_bank_is_identity_and_right_bank_is_the_mirror():
    p0 = lg.bank_pose(0.0)
    assert np.allclose(p0.rotation, np.eye(3)) and np.allclose(p0.translation, 0)
    assert lg.bank_pose(-45.0).rotation @ np.array([0.0, -1.0, 0.0]) @ np.array([0, 0, 1]) > 0.7  # left side up


def test_inverted_pose_flips_up_and_keeps_the_longeron_tops_on_the_table():
    inv = lg.inverted_pose()
    assert np.linalg.det(inv.rotation) == pytest.approx(1.0)  # a rotation, not a mirror
    assert (inv.rotation @ np.array([0.0, 0.0, 1.0]))[2] == pytest.approx(-1.0)  # up goes down
    top = inv.apply([[70.0, 9.0, Z_TOP]])[0]
    assert top[2] == pytest.approx(Z_TOP)  # the longeron top stays on the table plane
    belly = inv.apply([[70.0, 0.0, Z_TOP - 20.0]])[0]
    assert belly[2] > Z_TOP  # the bottom is now up


# --- ground handling (Review Focus 4) ---------------------------------------------------------------
def test_ground_handling_has_no_numeric_verdict():
    gh = lg.ground_handling()
    assert gh["main_axle_fs"] == 110.5 and gh["main_axle_wl"] == -22.0 and gh["tip_back_line_deg"] == 12.0
    assert gh["tip_over_check"].startswith("not yet computed")
    assert gh["tip_back_check"].startswith("not yet computed")
    for k in ("tip_back_check", "tip_over_check"):
        assert isinstance(gh[k], str) and not any(ch.isdigit() for ch in gh[k])
    for c in gh["cite"].values():
        for part in c.split(";"):
            check_citation(part.strip().split(" ")[0])


# --- jig blocks vs extrusions (p50 "bevels to the outside") ------------------------------------------
def test_blocks_sit_on_the_tube_outboard_of_the_angles_with_bevels_outboard(parts):
    ext = parts["extrusions"].solid.val().Solids()
    tubes = parts["gear_tubes"].solid.val().Solids()
    blocks = parts["jig_blocks"].solid.val().Solids()
    for t in tubes:
        tb = t.BoundingBox()
        xc = (tb.xmin + tb.xmax) / 2
        mine_e = [e.BoundingBox() for e in ext if tb.ymin - 3 < e.Center().y < tb.ymax + 3]
        mine_b = sorted((b for b in blocks if tb.ymin - 1 < b.Center().y < tb.ymax + 1), key=lambda b: b.Center().x)
        assert len(mine_e) == 2 and len(mine_b) == 2
        # the angles are between the blocks, and the tube passes through both flanges
        e_in = max(e.xmin for e in mine_e), min(e.xmax for e in mine_e)
        for e in mine_e:
            assert mine_b[0].BoundingBox().xmax <= e.xmin + 1e-6 or mine_b[1].BoundingBox().xmin >= e.xmax - 1e-6
            assert tb.xmin < e.xmin and e.xmax < tb.xmax
        cy, cz = (tb.ymin + tb.ymax) / 2, (tb.zmin + tb.zmax) / 2
        for e in ext:
            eb = e.BoundingBox()
            if abs(e.Center().y - cy) < 3:
                assert eb.ymin - 1e-6 <= cy <= eb.ymax + 1e-6 and eb.zmin <= cz <= eb.zmax  # tube centre in the flange footprint
        # bevel outboard: the sharp (bevelled) bottom edge of a block lies on the side AWAY from the tube centre
        for b in mine_b:
            bb = b.BoundingBox()
            out = -1 if b.Center().x < xc else 1
            in_x = bb.xmin + 0.01 if out > 0 else bb.xmax - 0.01  # inboard face (towards the tube centre)
            out_x = bb.xmax - 0.01 if out > 0 else bb.xmin + 0.01  # outboard face (towards the tube end)
            z_probe = bb.zmax - 0.3  # near the sharp edge (the round top is at -z after the 180 roll)
            # the bevel is cut from the outboard face: near the sharp edge only the inboard face has material
            assert b.isInside(Vector(in_x, b.Center().y, z_probe)) and not b.isInside(Vector(out_x, b.Center().y, z_probe))


def test_the_135_degree_chapter_7_roll_puts_the_right_side_and_the_bottom_both_facing_up():
    # captain's reading of p46 ("45 degrees of left bank"): the side and the bottom being glassed both face up 45 degrees
    import re
    from pathlib import Path

    from guide.fuselage_export import BANK_DEG

    rot = lg.bank_pose(135).rotation
    assert (rot @ np.array([0.0, 1.0, 0.0]))[2] >= 0.7  # the right side's outward normal (B.L. > 0)
    assert (rot @ np.array([0.0, 0.0, -1.0]))[2] >= 0.7  # the bottom's outward normal (down)
    rot_l = lg.bank_pose(-135).rotation
    assert (rot_l @ np.array([0.0, -1.0, 0.0]))[2] >= 0.7 and (rot_l @ np.array([0.0, 0.0, -1.0]))[2] >= 0.7
    ts = (Path(__file__).resolve().parent.parent / "guide/lab/src/logic/fuselage.ts").read_text()
    m = re.search(r"export const BANK_DEG[^=]*=\s*\{\s*'f07\.skin-right':\s*(-?[\d.]+),\s*'f07\.skin-left':\s*(-?[\d.]+)\s*\}", ts)
    assert m, "BANK_DEG not found in fuselage.ts"
    assert BANK_DEG == {"f07.skin-right": float(m.group(1)), "f07.skin-left": float(m.group(2))}
