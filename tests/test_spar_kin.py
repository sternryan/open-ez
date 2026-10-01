"""Centre-section spar planform and cap maths (plans-1980 p86, p88). All numbers come from config."""

import math

import pytest

from config import config
from core import spar_kin as sk

G = config.geometry
SWEEP = math.radians(8.57)


def test_module_says_the_21_7_label_is_unmodelled():
    doc = sk.__doc__.lower()
    assert "21.7" in doc and "unmodelled" in doc


def test_face_fs_inboard_is_constant():
    for bl in (0.0, 10.0, 23.0, -23.0, -5.0):
        assert sk.face_fs(bl, "fwd") == pytest.approx(118.5)
        assert sk.face_fs(bl, "aft") == pytest.approx(125.0)


def test_face_fs_outboard_pins():
    assert sk.face_fs(56.46, "fwd") == pytest.approx(123.54, abs=0.01)
    assert sk.face_fs(55.5, "aft") == pytest.approx(129.90, abs=0.02)
    assert sk.face_fs(26.75, "aft") == pytest.approx(
        125.57, abs=0.01
    )  # p50 gear datum is 125.5
    assert sk.face_fs(25.0, "aft") == pytest.approx(125.30, abs=0.01)
    # the research file says 129.3 here; that is an arithmetic slip, 125 + 30.5 tan 8.57 = 129.59
    assert sk.face_fs(53.5, "aft") == pytest.approx(129.59, abs=0.01)
    slope = math.tan(SWEEP)
    assert slope == pytest.approx(0.1507, abs=1e-4)  # tan 8.57 deg = 0.15070
    assert sk.face_fs(33.0, "fwd") - sk.face_fs(23.0, "fwd") == pytest.approx(
        10.0 * slope
    )


def test_face_fs_is_symmetric_in_bl():
    for bl in (10.0, 25.0, 40.0, 56.46):
        for face in ("fwd", "aft"):
            assert sk.face_fs(-bl, face) == pytest.approx(sk.face_fs(bl, face))


def test_face_fs_rejects_a_bad_face():
    with pytest.raises(ValueError):
        sk.face_fs(10.0, "top")


def test_chords():
    for bl in (0.0, 10.0, 23.0, 40.0, 55.5, -40.0):
        assert sk.chord_fore_aft(bl) == pytest.approx(6.50)
    assert sk.chord_square(10.0) == pytest.approx(6.50)
    assert sk.chord_square(23.0) == pytest.approx(6.50)
    assert sk.chord_square(40.0) == pytest.approx(6.427, abs=0.001)
    assert sk.chord_square(-40.0) == pytest.approx(6.50 * math.cos(SWEEP))


def test_plan_outline_corners():
    pts = sk.plan_outline_right()
    assert len(pts) == 6
    assert pts[0] == pytest.approx((0.0, 118.5))
    assert pts[1] == pytest.approx((23.0, 118.5))
    assert pts[2] == pytest.approx((56.46, 123.54), abs=0.01)
    assert pts[3] == pytest.approx((55.50, 129.90), abs=0.02)
    assert pts[4] == pytest.approx((23.0, 125.0))
    assert pts[5] == pytest.approx((0.0, 125.0))


def test_end_edge_is_square_to_the_outboard_faces():
    pts = sk.plan_outline_right()
    face = (pts[2][0] - pts[1][0], pts[2][1] - pts[1][1])
    end = (pts[3][0] - pts[2][0], pts[3][1] - pts[2][1])
    dot = face[0] * end[0] + face[1] * end[1]
    assert dot == pytest.approx(0.0, abs=1e-9)
    assert math.hypot(*end) == pytest.approx(6.427, abs=0.001)


def test_outboard_face_lengths():
    pts = sk.plan_outline_right()
    assert math.dist(pts[1], pts[2]) == pytest.approx(33.834, abs=0.01)
    assert math.dist(pts[4], pts[3]) == pytest.approx(32.865, abs=0.02)
    assert G.spar_face_length_fwd_outboard_in == pytest.approx(33.834)


def test_wl_profile():
    assert sk.bottom_wl(0.0) == pytest.approx(13.5)
    assert sk.bottom_wl(9.0) == pytest.approx(13.5)
    assert sk.bottom_wl(-9.0) == pytest.approx(13.5)
    assert sk.bottom_wl(56.46) == pytest.approx(15.15)
    assert sk.bottom_wl(-56.46) == pytest.approx(15.15)
    mid = (9.0 + 56.46) / 2
    assert sk.bottom_wl(mid) == pytest.approx((13.5 + 15.15) / 2)
    for bl in (0.0, 30.0, 55.5):
        assert sk.top_wl(bl) == pytest.approx(22.0)
    assert sk.depth(0.0) == pytest.approx(8.50)
    assert sk.depth(56.46) == pytest.approx(22.0 - 15.15)


def test_cap_end_bls_match_p86():
    assert sk.cap_end_bls("top") == pytest.approx([50, 45, 40, 35, 30, 25, 20, 15])
    assert sk.cap_end_bls("bottom") == pytest.approx([48, 41, 34, 27, 20, 13])
    assert sorted(sk.cap_end_bls("top")) == pytest.approx(
        list(G.spar_top_cap_partial_end_bl)
    )
    assert sorted(sk.cap_end_bls("bottom")) == pytest.approx(
        list(G.spar_bottom_cap_partial_end_bl)
    )
    assert G.spar_full_ply_end_bl == pytest.approx(55.5)


def test_cap_ply_counts_top():
    assert sk.cap_plies(0.0, "top") == 12
    assert sk.cap_plies(15.0, "top") == 12  # a ply ends AT its end BL, inclusive
    assert sk.cap_plies(15.5, "top") == 11
    assert sk.cap_plies(17.5, "top") == 11
    assert sk.cap_plies(30.0, "top") == 9
    assert sk.cap_plies(47.5, "top") == 5
    assert sk.cap_plies(50.0, "top") == 5
    assert sk.cap_plies(50.5, "top") == 4
    assert sk.cap_plies(55.5, "top") == 4
    assert sk.cap_plies(-17.5, "top") == 11
    assert sk.cap_plies(56.0, "top") == 0


def test_cap_ply_counts_bottom():
    assert sk.cap_plies(0.0, "bottom") == 9
    assert sk.cap_plies(13.0, "bottom") == 9
    assert sk.cap_plies(20.0, "bottom") == 8
    assert sk.cap_plies(30.0, "bottom") == 6
    assert sk.cap_plies(48.0, "bottom") == 4
    assert sk.cap_plies(55.5, "bottom") == 3
    assert sk.cap_plies(56.0, "bottom") == 0


def test_cap_thickness():
    assert sk.cap_thickness(0.0, "top") == pytest.approx(0.4500)
    assert sk.cap_thickness(55.5, "top") == pytest.approx(0.1500)
    assert sk.cap_thickness(0.0, "bottom") == pytest.approx(0.3375)
    assert sk.cap_thickness(55.5, "bottom") == pytest.approx(0.1125)
    assert G.spar_ply_thickness_laid_in == pytest.approx(0.0375)


def test_strip_lengths_and_totals():
    assert sk.strip_lengths("top") == tuple(G.spar_top_cap_strips_in)
    assert sk.strip_lengths("bottom") == tuple(G.spar_bottom_cap_strips_in)
    assert sk.strip_total("top") == pytest.approx(972)
    assert sk.strip_total("bottom") == pytest.approx(705)
    assert sk.strip_total("top") + sk.strip_total("bottom") == pytest.approx(1677)


@pytest.mark.parametrize("cap", ["top", "bottom"])
def test_each_tapered_strip_is_twice_its_end_bl(cap):
    strips = sk.strip_lengths(cap)
    ends = sk.cap_end_bls(cap)
    tapered = strips[len(strips) - len(ends) :]
    assert [2 * e for e in ends] == pytest.approx(list(tapered))


def test_bad_cap_is_rejected():
    for f in (sk.cap_end_bls, sk.strip_lengths, sk.strip_total):
        with pytest.raises(ValueError):
            f("side")
    with pytest.raises(ValueError):
        sk.cap_plies(0.0, "side")


def test_hard_points():
    hp = sk.hard_points()
    assert len(hp) == 3
    want = [(25.0, 20.25, 125.30), (53.5, 20.5, 129.59), (53.5, 16.3, 129.59)]
    for got, (bl, wl, fs) in zip(hp, want):
        assert got["bl"] == pytest.approx(bl)
        assert got["wl"] == pytest.approx(wl)
        assert got["fs_aft_face"] == pytest.approx(fs, abs=0.01)
        assert got["fs_aft_face"] == pytest.approx(sk.face_fs(bl, "aft"))


def test_hard_point_spacing():
    assert sk.hard_point_spacing_along_aft_face() == pytest.approx(28.82, abs=0.01)
    assert sk.hard_point_spacing_along_aft_face() == pytest.approx(
        G.spar_hard_point_spacing_aft_in, abs=0.01
    )
