"""Roncz elevator kinematics: spans, hinge stations, travel classes, hinge rotation, hang test.

Frame for the 2-D helpers: x aft along the chord, z up. All values come from config (cobelu fig C-1 and the
ch30 text); no number is measured off an image.
"""

import math

import pytest

from config import config
from core import elevators_kin as ek

G = config.geometry


def test_spans_match_the_figure_and_the_lengths():
    assert ek.elevator_span("right") == pytest.approx((9.3, 65.0))
    assert ek.elevator_span("left") == pytest.approx((-65.0, 7.7))
    for side, length in (
        ("right", G.elevator_length_right_in),
        ("left", G.elevator_length_left_in),
    ):
        lo, hi = ek.elevator_span(side)
        assert hi - lo == pytest.approx(length)


def test_left_elevator_crosses_the_centreline_and_right_does_not():
    assert ek.elevator_span("left")[0] < 0 < ek.elevator_span("left")[1]
    assert ek.elevator_span("right")[0] > 0


def test_bad_side_is_rejected():
    for f in (
        ek.elevator_span,
        ek.hinge_stations,
        ek.unplaced_hinge_stations,
        ek.pin_length,
    ):
        with pytest.raises(ValueError):
            f("middle")


def test_hinge_stations_are_the_drawn_ones_that_fall_on_the_elevator():
    assert ek.hinge_stations("left") == pytest.approx([-59.0, -34.1, -9.2])
    assert ek.hinge_stations("right") == pytest.approx([34.1, 59.0])
    # 9.2 on the right lies 0.1 in off the inboard end (9.3): carried as unplaced, never moved
    assert ek.unplaced_hinge_stations("right") == pytest.approx([9.2])
    assert ek.unplaced_hinge_stations("left") == []
    for side in ("left", "right"):
        lo, hi = ek.elevator_span(side)
        assert all(lo <= b <= hi for b in ek.hinge_stations(side))


def test_hinge_count_note_says_the_text_and_the_figure_disagree():
    n = ek.hinge_count_note()
    assert n["slots_in_text"] == 7
    assert n["stations_placed"] == 5
    assert n["stations_placed"] < n["slots_in_text"]


def test_pin_lengths_are_the_trim_step_values():
    assert ek.pin_length("right") == 36.0
    assert ek.pin_length("left") == 61.0


def test_travel_range_is_roncz_not_gu_or_manual():
    assert ek.travel_range_deg() == (15.0, 30.0)


@pytest.mark.parametrize(
    "deg,cls",
    [
        (-1.0, "below floor"),
        (0.0, "below floor"),
        (12.4, "below floor"),
        (12.5, "floor only"),
        (14.99, "floor only"),
        (15.0, "target"),
        (22.0, "target"),
    ],
)
def test_up_travel_classes(deg, cls):
    assert ek.classify_up_travel(deg) == cls


def test_rotate_about_hinge_trailing_edge_down():
    x, z = ek.rotate_about_hinge((1.0, 0.0), (0.0, 0.0), 90.0)
    assert (x, z) == pytest.approx((0.0, -1.0), abs=1e-9)
    x, z = ek.rotate_about_hinge(
        (1.0, 0.0), (0.0, 0.0), -90.0
    )  # negative = trailing edge up
    assert (x, z) == pytest.approx((0.0, 1.0), abs=1e-9)
    x, z = ek.rotate_about_hinge((3.0, 2.0), (2.0, 2.0), 0.0)
    assert (x, z) == pytest.approx((3.0, 2.0))


def test_rotation_keeps_distance_to_the_hinge():
    h = (4.0, 1.5)
    p = (9.0, 2.0)
    r0 = math.dist(p, h)
    for a in (-30, -12.5, 15, 30, 77):
        assert math.dist(ek.rotate_about_hinge(p, h, a), h) == pytest.approx(r0)


def test_hang_nose_down_when_cg_is_forward_of_the_hinge():
    assert ek.hangs_nose_down(-2.0, 0.0) is True
    assert ek.hangs_nose_down(-1.0, -1.0) is True
    assert ek.hangs_nose_down(2.0, 0.0) is False
    assert ek.hangs_nose_down(1.0, 1.0) is False


def test_hang_pitch_sign_and_size():
    assert ek.hang_pitch_deg(-2.0, 0.0) == pytest.approx(90.0)
    assert ek.hang_pitch_deg(2.0, 0.0) == pytest.approx(-90.0)
    assert ek.hang_pitch_deg(-1.0, -1.0) == pytest.approx(45.0)
    assert -180.0 < ek.hang_pitch_deg(0.3, 5.0) <= 180.0


def test_hang_needs_a_cg_off_the_hinge():
    with pytest.raises(ValueError):
        ek.hang_pitch_deg(0.0, 0.0)
    with pytest.raises(ValueError):
        ek.hangs_nose_down(0.0, 0.0)


def test_cs11_block_volume_is_the_printed_block():
    assert ek.cs11_volume_in3() == pytest.approx(2.0 * 0.6 * 0.8)
