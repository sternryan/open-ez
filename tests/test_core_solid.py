"""The canard core must be a real solid: X chordwise, Y spanwise (BL), Z thickness."""

from core.structures import CanardGenerator


def test_canard_core_has_volume_and_thickness():
    gen = CanardGenerator()
    solid = gen.generate_geometry().val()
    bb = solid.BoundingBox()
    _, y = gen.root_airfoil.coordinates
    root_thickness = float(y.max() - y.min()) * gen.root_chord
    assert solid.isValid()
    assert solid.Volume() > 100.0  # cubic inches; it was 0.0 before the fix
    assert abs(bb.ylen - gen.span / 2) < 1.0
    assert abs(bb.zlen - root_thickness) < 0.15 * root_thickness
    assert bb.zmax > abs(bb.zmin)  # upper surface is +Z (a -90 deg rotation would flip it)
