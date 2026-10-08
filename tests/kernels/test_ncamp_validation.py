"""M3.1 CLT in-plane moduli against NCAMP measured laminates (spec section 5).

The bound (measured mean +- 2 x CV x mean) was frozen in ledger row 73 before any prediction was computed.
A miss is recorded as a strict xfail citing a new ledger row; the bound is never widened.
"""

import numpy as np
import pytest

pytest.importorskip(
    "core.kernels.laminate",
    reason="M3.1 kernel body pending (plan T4, after the remote-runner gate)",
)

from core.kernels.lamina import Ply
from core.kernels.laminate import abd, laminate_constants
from tests.kernels._vectors import load

V = load("ncamp_laminates.yaml")
K = V["bound"]["k_sd"]
# Recorded misses against the frozen bound: strict xfails, each citing its ledger row. Never widened.
MISSES = {
    (
        "as4_8552",
        "10/80/10",
        "UNT",
    ): "ledger row 78: CLT 4.800 Msi vs measured 4.570 +- 0.182 Msi",
}
CASES = [
    pytest.param(
        mat,
        lam["name"],
        mode,
        marks=[pytest.mark.xfail(strict=True, reason=MISSES[(mat, lam["name"], mode)])]
        if (mat, lam["name"], mode) in MISSES
        else [],
        id=f"{mat}-{lam['name']}-{mode}",
    )
    for mat in ("as4_8552", "mtm45_7781")
    for lam in V[mat]["laminates"]
    for mode in ("UNT", "UNC")
]


def predicted_ex(mat: str, lam: dict, mode: str) -> float:
    m = V[mat]
    p = m["tension" if mode == "UNT" else "compression"]
    angles = lam["stack"] + (lam["stack"][::-1] if lam["symmetric"] else [])
    plies = [Ply(p["E1"], p["E2"], p["G12"], p["nu12"], m["t_ply"], a) for a in angles]
    A, B, _ = abd(plies)
    assert np.allclose(B, 0.0, atol=1e-6 * np.abs(A).max())
    return laminate_constants(A, m["t_ply"] * len(plies))["Ex"]


@pytest.mark.parametrize("mat,name,mode", CASES)
def test_inplane_modulus_within_frozen_bound(mat, name, mode):
    lam = next(x for x in V[mat]["laminates"] if x["name"] == name)
    meas = lam[mode]
    half = K * meas["cv_pct"] / 100.0 * meas["mean"]
    ex = predicted_ex(mat, lam, mode)
    print(
        f"{mat} {name} {mode}: CLT {ex / 1e6:.3f} Msi vs measured {meas['mean'] / 1e6:.3f} +- {half / 1e6:.3f}"
    )
    assert abs(ex - meas["mean"]) <= half


def test_broken_swapped_moduli_fails_the_bound():
    mat, lam = "as4_8552", V["as4_8552"]["laminates"][2]
    m = V[mat]
    p = dict(m["tension"])
    p["E1"], p["E2"] = p["E2"], p["E1"]
    angles = lam["stack"] + lam["stack"][::-1]
    plies = [Ply(p["E1"], p["E2"], p["G12"], p["nu12"], m["t_ply"], a) for a in angles]
    A, _, _ = abd(plies)
    ex = laminate_constants(A, m["t_ply"] * len(plies))["Ex"]
    meas = lam["UNT"]
    assert abs(ex - meas["mean"]) > K * meas["cv_pct"] / 100.0 * meas["mean"]
