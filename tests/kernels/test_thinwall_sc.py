"""M3.2 shear centre of a closed thin-wall section (plan T7; core/kernels/thinwall_sc.py).

No published multi-cell shear-centre vector is held (ledger row 75). Besides symmetry and a rigid
shift (tests/kernels/test_thinwall.py) these are captain hand cases:
  - a 10 x 5 single-cell box whose right web is twice as thick as the rest, with axial and shear
    stiffness per unit width both proportional to thickness: x_sc = 200/33 (captain derivation
    2026-10-08, exact symbolic integration of the open-section flow cut at the top-left corner plus
    the zero-twist closing flow; not external validation);
  - mirroring a section about a vertical line mirrors its shear centre.

Contract: shear_centre_x(walls, cells) -> float. Walls carry x0, z0, x1, z1, Gt, Et (straight, endpoints
in the section plane, z up); cells carry wall_ids. Load is a vertical shear; the section has no caps.
"""

from types import SimpleNamespace

import pytest

pytest.importorskip(
    "core.kernels.thinwall_sc",
    reason="M3.2 shear-centre body pending (plan T7)",
)

from core.kernels.thinwall_sc import shear_centre_x

E = 1.0e6  # stiffness per unit thickness; the shear centre does not depend on its value


def wall(x0, z0, x1, z1, t):
    return SimpleNamespace(
        x0=x0, z0=z0, x1=x1, z1=z1, t=t, Gt=0.4 * E * t, Et=E * t, length=None
    )


def box(t_right=0.05, t=0.05, width=10.0, height=5.0, web_x=None):
    h2 = height / 2
    if web_x is None:
        walls = [
            wall(0, h2, width, h2, t),
            wall(width, h2, width, -h2, t_right),
            wall(width, -h2, 0, -h2, t),
            wall(0, -h2, 0, h2, t),
        ]
        return walls, [SimpleNamespace(wall_ids=(0, 1, 2, 3), area=width * height)]
    walls = [
        wall(0, h2, web_x, h2, t),
        wall(web_x, -h2, 0, -h2, t),
        wall(0, -h2, 0, h2, t),
        wall(web_x, h2, web_x, -h2, t),
        wall(web_x, h2, width, h2, t),
        wall(width, h2, width, -h2, t_right),
        wall(width, -h2, web_x, -h2, t),
    ]
    cells = [
        SimpleNamespace(wall_ids=(0, 1, 2, 3), area=web_x * height),
        SimpleNamespace(wall_ids=(3, 4, 5, 6), area=(width - web_x) * height),
    ]
    return walls, cells


def mirror(walls, about):
    return [
        SimpleNamespace(
            x0=2 * about - w.x0,
            z0=w.z0,
            x1=2 * about - w.x1,
            z1=w.z1,
            t=w.t,
            Gt=w.Gt,
            Et=w.Et,
            length=None,
        )
        for w in walls
    ]


def test_symmetric_box_is_centred():
    assert shear_centre_x(*box()) == pytest.approx(5.0, abs=1e-9)


def test_thicker_right_web_matches_hand_derivation():
    assert shear_centre_x(*box(t_right=0.10)) == pytest.approx(200 / 33, rel=1e-9)


def test_broken_thickness_on_the_wrong_web_fails():  # broken input: the wrong web thickened
    walls, cells = box(t_right=0.10)
    walls[1].Gt, walls[3].Gt = walls[3].Gt, walls[1].Gt
    walls[1].Et, walls[3].Et = walls[3].Et, walls[1].Et
    assert shear_centre_x(walls, cells) != pytest.approx(200 / 33, rel=1e-3)


def test_wall_direction_does_not_matter():
    walls, cells = box(t_right=0.10)
    w = walls[1]
    walls[1] = SimpleNamespace(
        x0=w.x1, z0=w.z1, x1=w.x0, z1=w.z0, t=w.t, Gt=w.Gt, Et=w.Et, length=None
    )
    assert shear_centre_x(walls, cells) == pytest.approx(200 / 33, rel=1e-9)


def test_two_cell_section_mirrors():
    walls, cells = box(t_right=0.10, web_x=2.0)
    x = shear_centre_x(walls, cells)
    assert 0.0 < x < 10.0
    assert shear_centre_x(mirror(walls, 5.0), cells) == pytest.approx(
        10.0 - x, abs=1e-9
    )


def test_symmetric_two_cell_section_is_centred():
    walls, cells = box(web_x=5.0)
    assert shear_centre_x(walls, cells) == pytest.approx(5.0, abs=1e-9)


# ---- asymmetric sections: the product of inertia must enter (T7 grader finding, 2026-10-08) ------


def polygon(points, Gt, Et, dx=0.0, dz=0.0):
    n = len(points)
    walls = [
        SimpleNamespace(
            x0=points[i][0] + dx,
            z0=points[i][1] + dz,
            x1=points[(i + 1) % n][0] + dx,
            z1=points[(i + 1) % n][1] + dz,
            t=1.0,
            Gt=Gt[i],
            Et=Et[i],
            length=None,
        )
        for i in range(n)
    ]
    return walls, [SimpleNamespace(wall_ids=tuple(range(n)), area=0.0)]


TRAPEZOID = ([(0, 0), (5, 0), (2, 3), (0, 3)], [1, 2, 1, 3], [1, 1, 1, 1])


def test_asymmetric_section_matches_independent_integral():
    # 1.2026: the T7 grader's independent fine-discretised cut-section integral with Ixz (not external
    # validation); ignoring Ixz gives 2.1185 and depends on the reference point.
    assert shear_centre_x(*polygon(*TRAPEZOID)) == pytest.approx(1.2026, abs=5e-5)


@pytest.mark.parametrize("dx,dz", [(3.0, 0.0), (0.0, -2.0), (7.0, -3.0)])
def test_asymmetric_section_follows_a_rigid_shift(dx, dz):
    x0 = shear_centre_x(*polygon(*TRAPEZOID))
    assert shear_centre_x(*polygon(*TRAPEZOID, dx=dx, dz=dz)) == pytest.approx(
        x0 + dx, abs=1e-9
    )


def test_zero_shear_stiffness_raises():
    walls, cells = polygon(TRAPEZOID[0], [1, 0, 1, 3], TRAPEZOID[2])
    with pytest.raises(ValueError):
        shear_centre_x(walls, cells)


def test_open_loop_raises():
    walls, _ = box()
    with pytest.raises(ValueError):
        shear_centre_x(walls, [SimpleNamespace(wall_ids=(0, 1, 2), area=50.0)])
