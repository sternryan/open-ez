"""M3.1 lamina kernel against printed textbook values (spec section 5; vectors in vectors/clt_textbook.yaml)."""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.lamina",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.lamina import (
    Ply,
    reduced_stiffness,
    stress_to_material,
    transformed_stiffness,
)

from tests.kernels._vectors import load, printed_close

V = load("clt_textbook.yaml")
G = V["glass_epoxy_lamina"]


def test_reduced_stiffness_matches_printed_q():
    Q = reduced_stiffness(G["E1"], G["E2"], G["G12"], G["nu12"])
    assert printed_close(Q, G["Q_printed"])


def test_reduced_stiffness_broken_input_is_caught():  # E1 and E2 swapped must not match
    Q = reduced_stiffness(G["E2"], G["E1"], G["G12"], G["nu12"])
    assert not printed_close(Q, G["Q_printed"])


def test_zero_degree_transform_is_identity():
    Q = reduced_stiffness(G["E1"], G["E2"], G["G12"], G["nu12"])
    assert np.allclose(transformed_stiffness(Q, 0.0), Q)


def test_stress_to_material_matches_printed():
    T = V["tsai_wu_30deg_lamina"]
    local = stress_to_material(np.array(T["global_stress_per_S"]), T["theta_deg"])
    assert printed_close(local, T["local_stress_per_S"])
    flipped = stress_to_material(np.array(T["global_stress_per_S"]), -T["theta_deg"])
    assert not printed_close(flipped, T["local_stress_per_S"])


def test_ply_is_frozen():
    import dataclasses

    p = Ply(G["E1"], G["E2"], G["G12"], G["nu12"], 0.005, 30.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.t = 1.0  # type: ignore[misc]
