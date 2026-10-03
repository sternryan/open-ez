"""OE1 spar solids: independent station, volume and schedule checks."""

import cadquery as cq
import pytest

from config import config
from core import spar_kin as kin
from core.spar_book import WING_PLANE_WL, build_spar, cap_plies

G = config.geometry


@pytest.fixture(scope="module")
def parts():
    return build_spar()


def test_only_sourced_display_parts_exist_with_citations(parts):
    assert set(parts) == {"box", "cap_top", "cap_bottom"}
    for part in parts.values():
        assert (
            part.fidelity == "representational"
            and part.cite
            and part.solid.val().Volume() > 0
        )
        assert "fabrication" in part.note or "trough" in part.note


def test_box_planform_and_wl_stations_are_independent_of_the_builder(parts):
    box = parts["box"].solid
    for bl in (0.0, 23.0, 56.46, -23.0, -56.46):
        probe = (
            cq.Workplane("XY")
            .box(0.02, 0.02, 40, centered=False)
            .translate((kin.face_fs(bl, "fwd") - 0.01, bl - 0.01, -20))
        )
        assert box.intersect(probe).val().Volume() > 0
    bb = box.val().BoundingBox()
    assert bb.xmin == pytest.approx(118.5, abs=1e-5)
    assert bb.xmax == pytest.approx(129.89809, abs=1e-4)
    assert bb.zmin == pytest.approx(13.5 - WING_PLANE_WL, abs=1e-5)
    assert bb.zmax == pytest.approx(22.0 - WING_PLANE_WL, abs=1e-5)


@pytest.mark.parametrize("cap,expected", [("top", 12), ("bottom", 9)])
def test_cap_volumes_preserve_every_published_ply_and_positive_volume(
    parts, cap, expected
):
    plies = cap_plies(cap)
    assert len(plies) == expected and all(s.Volume() > 0 and s.isValid() for s in plies)
    compound_volume = parts[f"cap_{cap}"].solid.val().Volume()
    assert compound_volume == pytest.approx(sum(s.Volume() for s in plies), rel=1e-9)


@pytest.mark.parametrize("cap", ["top", "bottom"])
def test_cap_span_schedule_matches_the_existing_independent_kernel(cap):
    plies = cap_plies(cap)
    lengths = kin.strip_lengths(cap)
    for solid, length in zip(plies, lengths):
        bb = solid.BoundingBox()
        assert max(abs(bb.ymin), abs(bb.ymax)) == pytest.approx(
            min(length / 2, 55.5), abs=1e-5
        )


def test_unknown_cap_is_rejected():
    with pytest.raises(ValueError):
        cap_plies("side")


def test_bottom_breakpoint_and_square_tip(parts):
    shape = parts["box"].solid.val()
    assert shape.isValid()
    for bl in (-9.0, 9.0):
        assert shape.isInside(cq.Vector(120, bl, 13.501 - 17.4))
        assert not shape.isInside(cq.Vector(120, bl, 13.499 - 17.4))
    assert not shape.isInside(cq.Vector(130.0, 56.0, 0.0))
    assert not shape.isInside(cq.Vector(130.0, -56.0, 0.0))


@pytest.mark.parametrize("cap", ["top", "bottom"])
def test_finished_caps_end_at_55_5_and_never_escape_display_envelope(parts, cap):
    box = parts["box"].solid
    for solid in cap_plies(cap):
        assert solid.BoundingBox().ymax <= 55.50001
        outside = cq.Workplane("XY").add(solid).cut(box).val().Volume()
        assert outside < 1e-6
