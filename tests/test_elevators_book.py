"""Roncz elevator parts (cobelu ch30 fig C-1): spans, tube, weights, hinges, pose, export wiring."""

import numpy as np
import pytest

from core import elevators_book as eb
from core import elevators_kin as ek
from core.fuselage_book import FIDELITIES
from core.sources import check_citation

G = eb.G
NAMES = {
    f"{k}_{s}"
    for k in ("elevator", "elevator_tube", "hinges", "balance_weight", "cs11_weight")
    for s in ("right", "left")
}


@pytest.fixture(scope="module")
def parts():
    return eb.build_elevators()


def _bb(p):
    return p.solid.val().BoundingBox()


def test_every_part_has_fidelity_note_and_valid_cites(parts):
    assert set(parts) == NAMES
    for n, p in parts.items():
        assert p.fidelity in FIDELITIES, n
        assert p.fidelity == "representational" and p.note, (
            n
        )  # no book/derived without a registry citation
        for c in p.cite:
            check_citation(c)
        assert p.solid.val().isValid(), n
        assert p.solid.val().Volume() > 0, n


def test_elevator_spans_match_the_kernel_and_sides(parts):
    for side in ("right", "left"):
        lo, hi = ek.elevator_span(side)
        bb = _bb(parts[f"elevator_{side}"])
        assert bb.ymin == pytest.approx(lo, abs=0.1) and bb.ymax == pytest.approx(
            hi, abs=0.1
        )
        tb = _bb(parts[f"elevator_tube_{side}"])
        assert tb.ymax - tb.ymin == pytest.approx(hi - lo, abs=1e-6)
        assert (
            tb.zmax - tb.zmin
            == pytest.approx(G.elevator_tube_od_in)
            == pytest.approx(1.0)
        )
    assert _bb(parts["elevator_left"]).ymin < 0 < _bb(parts["elevator_left"]).ymax
    assert _bb(parts["elevator_right"]).ymin > 0
    assert eb.FITTED_ELEV_LE_XC == 0.70 and eb.FITTED_SLEEVE == 0.03


def test_elevator_section_aft_of_tube_le_and_trimmed(parts):
    bb = _bb(parts["elevator_right"])
    c = eb._chord()
    assert bb.xmin == pytest.approx(0.70 * c - eb.FITTED_SLEEVE, abs=0.01)
    assert bb.xmax <= 0.97 * c + 0.1


def test_balance_weight_spans_7_5_and_ends_at_the_outboard_end(parts):
    r, left = _bb(parts["balance_weight_right"]), _bb(parts["balance_weight_left"])
    assert r.ymax - r.ymin == pytest.approx(7.5) and r.ymax == pytest.approx(65.0)
    assert r.ymin == pytest.approx(57.5)
    assert left.ymin == pytest.approx(-65.0) and left.ymax - left.ymin == pytest.approx(
        7.5
    )
    assert r.xmax <= eb.x_tube_le()


def test_cs11_at_inboard_end(parts):
    for side in ("right", "left"):
        lo, hi = ek.elevator_span(side)
        bb = _bb(parts[f"cs11_weight_{side}"])
        assert bb.ymax - bb.ymin == pytest.approx(2.0)
        assert (bb.ymin if side == "right" else bb.ymax) == pytest.approx(
            lo if side == "right" else hi
        )


def test_hinge_plate_counts_and_stations(parts):
    assert len(parts["hinges_right"].solid.val().Solids()) == 2
    assert len(parts["hinges_left"].solid.val().Solids()) == 3
    for side in ("right", "left"):
        ys = sorted(s.Center().y for s in parts[f"hinges_{side}"].solid.val().Solids())
        assert ys == pytest.approx(ek.hinge_stations(side))


def test_pose_identity_and_matches_kernel():
    for side in ("right", "left"):
        assert np.allclose(eb.elevator_pose(side, 0), np.eye(4))
    h = eb.hinge_axis_xz()
    te = (0.97 * eb._chord(), 0.1)
    for deg in (15.0, 30.0):
        m = eb.elevator_pose("right", deg)
        got = m @ np.array([te[0], 3.0, te[1], 1.0])
        want = ek.rotate_about_hinge(te, h, deg)
        assert (got[0], got[2]) == pytest.approx(want)
        assert got[1] == pytest.approx(3.0)
        assert np.allclose(m @ np.array([h[0], 0, h[1], 1.0]), [h[0], 0, h[1], 1.0])
    assert eb.elevator_pose("left", 30.0)[2, 0] < 0  # TE (aft of hinge) goes down


def test_elevator_components_have_the_six_ids_and_canard_only_does_not():
    from guide import export_glb as eg

    ids = {
        "elevator.right",
        "elevator.left",
        "elevator.tube",
        "elevator.hinges",
        "elevator.balance_weight",
        "elevator.cs11_weight",
    }
    assert ids == set(eg.elevator_components())
    import inspect

    assert "elevator_components()" in inspect.getsource(eg.default_components)  # in the default export: the lab sorts them into the canard subject by prefix (tests/guide/test_export_glb.py builds it)
    assert not any(k.startswith("elevator.") for k in eg.canard_components())


def test_canard_only_export_has_no_elevator_nodes(tmp_path):
    from guide.export_glb import (
        canard_components,
        export_components,
        read_glb_node_names,
    )

    names = read_glb_node_names(
        export_components(canard_components(), tmp_path / "c.glb")
    )
    assert names and not any(n.startswith("elevator.") for n in names)
