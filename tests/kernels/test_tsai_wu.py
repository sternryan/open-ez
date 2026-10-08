"""M3.1 Tsai-Wu strength ratio against Kaw's printed example (vectors/clt_textbook.yaml)."""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.tsai_wu",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.lamina import stress_to_material
from core.kernels.tsai_wu import tsai_wu_strength_ratio
from tests.kernels._vectors import load

T = load("clt_textbook.yaml")["tsai_wu_30deg_lamina"]
S = T["strengths_MPa"]


def ratio(sigma, **over):
    s = {**S, **over}
    return tsai_wu_strength_ratio(
        np.array(sigma), s["F1t"], s["F1c"], s["F2t"], s["F2c"], s["F6"], T["f12_star"]
    )


def local_stress():
    """The material-axis stress per unit S from the printed global stress, not the printed local one.

    The printed local stress is rounded to 4 figures; fed in directly it gives 21.8252, which misses the
    printed 21.82 by 0.0002 beyond half a unit. The exact chain from the printed inputs gives 21.8248,
    which meets it (ledger row 78; the vector and the bound are unchanged).
    """
    return stress_to_material(np.array(T["global_stress_per_S"]), T["theta_deg"])


def test_strength_ratio_matches_printed():
    assert abs(ratio(local_stress()) - T["S_max_MPa"]) <= 0.005


def test_ratio_scales_inversely_with_load():
    r1 = ratio(T["local_stress_per_S"])
    r3 = ratio([3 * x for x in T["local_stress_per_S"]])
    assert abs(r1 / r3 - 3.0) < 1e-9


def test_broken_swapped_transverse_strengths_is_caught():
    bad = ratio(local_stress(), F2t=S["F2c"], F2c=S["F2t"])
    assert abs(bad - T["S_max_MPa"]) > 0.005


def test_compression_and_tension_differ():  # F1t != F1c, so the sign of the load matters (spec section 7)
    r_pos = ratio(T["local_stress_per_S"])
    r_neg = ratio([-x for x in T["local_stress_per_S"]])
    assert abs(r_pos - r_neg) > 0.01


def test_bad_inputs_raise():  # T4 grader: NaN strengths and malformed stress were not rejected
    sig = local_stress()
    with pytest.raises(ValueError):
        ratio(sig, F1t=float("nan"))
    with pytest.raises(ValueError):
        ratio([[1.0, 2.0, 3.0]])
    with pytest.raises(ValueError):
        ratio([float("nan"), 0.0, 0.0])
    assert ratio(list(sig)) == ratio(sig)
