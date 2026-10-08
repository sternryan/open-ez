"""M3.1 Tsai-Wu strength ratio against Kaw's printed example (vectors/clt_textbook.yaml)."""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.tsai_wu",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.tsai_wu import tsai_wu_strength_ratio

from tests.kernels._vectors import load

T = load("clt_textbook.yaml")["tsai_wu_30deg_lamina"]
S = T["strengths_MPa"]


def ratio(sigma, **over):
    s = {**S, **over}
    return tsai_wu_strength_ratio(
        np.array(sigma), s["F1t"], s["F1c"], s["F2t"], s["F2c"], s["F6"], T["f12_star"]
    )


def test_strength_ratio_matches_printed():
    assert abs(ratio(T["local_stress_per_S"]) - T["S_max_MPa"]) <= 0.005


def test_ratio_scales_inversely_with_load():
    r1 = ratio(T["local_stress_per_S"])
    r3 = ratio([3 * x for x in T["local_stress_per_S"]])
    assert abs(r1 / r3 - 3.0) < 1e-9


def test_broken_swapped_transverse_strengths_is_caught():
    bad = ratio(T["local_stress_per_S"], F2t=S["F2c"], F2c=S["F2t"])
    assert abs(bad - T["S_max_MPa"]) > 0.005


def test_compression_and_tension_differ():  # F1t != F1c, so the sign of the load matters (spec section 7)
    r_pos = ratio(T["local_stress_per_S"])
    r_neg = ratio([-x for x in T["local_stress_per_S"]])
    assert abs(r_pos - r_neg) > 0.01
