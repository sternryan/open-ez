import itertools
import random

import pytest
from scipy.optimize import linprog

from core import closure as cl
from core.ledger import load_ledger

L = load_ledger()
T = L["empty"]
ROWS = L["closure"]["rows"]
METHOD_ROWS = L["closure"]["method_check_rows"]
C = cl.closure_sum()
_V = cl.verdict(ROWS, T["weight_lb"], T["arm_in"])
_LIGHT = cl.loaded_cg(C.weight_lb, C.cg_fs, "light_pilot")
_HEAVY = cl.loaded_cg(C.weight_lb, C.cg_fs, "heavy_pilot")


def _lp(rows, W, side):
    """CG extreme at total weight exactly W by scipy linprog (arms at the favourable end)."""
    arms = [r["arm_band_fs"][1 if side else 0] for r in rows]
    sign = -1.0 if side else 1.0
    res = linprog([sign * a / W for a in arms], A_eq=[[1.0] * len(rows)], b_eq=[W],
                  bounds=[tuple(r["weight_band_lb"]) for r in rows], method="highs")
    assert res.status == 0
    return sign * res.fun


def _random_rows(seed, n):
    rnd = random.Random(seed)
    rows = []
    for i in range(n):
        lo = rnd.uniform(0, 30); hi = lo + rnd.uniform(0, 20)
        alo = rnd.uniform(0, 100); ahi = alo + rnd.uniform(0, 30)
        rows.append({"name": f"r{i}", "weight_lb": (lo + hi) / 2, "weight_band_lb": [lo, hi],
                     "arm_fs": (alo + ahi) / 2, "arm_band_fs": [alo, ahi]})
    return rows


def test_caps_are_the_book_derived_values():
    # (103 - 103.96) x 1113 / 730 = 1.4637 -> 1.464 (the brief said 1.462; the formula gives 1.464)
    assert cl.CG_CAP_IN == 1.464
    assert cl.WEIGHT_CAP_LB == 20.0


def test_cg_band_at_matches_linprog_on_the_real_rows():
    lo, hi = cl.weight_band(ROWS)
    W = (lo + hi) / 2
    got = cl.cg_band_at(ROWS, W)
    assert got == pytest.approx((_lp(ROWS, W, 0), _lp(ROWS, W, 1)), abs=1e-6)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_cg_band_at_matches_linprog_on_random_fixtures(seed):
    rows = _random_rows(seed, 7)
    lo, hi = cl.weight_band(rows)
    for W in (lo + 0.3 * (hi - lo), (lo + hi) / 2):
        assert cl.cg_band_at(rows, W) == pytest.approx((_lp(rows, W, 0), _lp(rows, W, 1)), abs=1e-6)


def test_astra_counterexample_cg_is_graded_at_the_target_weight():
    rows = [
        {"name": "fixed", "weight_lb": 700, "weight_band_lb": [700, 700], "arm_fs": 111, "arm_band_fs": [111, 111]},
        {"name": "var", "weight_lb": 15, "weight_band_lb": [0, 30], "arm_fs": 120, "arm_band_fs": [120, 120]},
    ]
    lo, hi = cl.cg_band_at(rows, 730)
    assert (lo, hi) == pytest.approx((111.370, 111.370), abs=1e-3)
    assert cl.cg_band(rows)[0] == pytest.approx(111.0, abs=1e-6)   # the unconditional band is wider
    assert cl.verdict(rows, 730, 111.1) != "closes"


def _brute(rows):
    best = [float("inf"), float("-inf")]
    for ws in itertools.product(*[r["weight_band_lb"] for r in rows]):
        for side in (0, 1):
            arms = [r["arm_band_fs"][side] for r in rows]
            c = sum(w * a for w, a in zip(ws, arms)) / sum(ws)
            best = [min(best[0], c), max(best[1], c)]
    return tuple(best)


def test_bisection_cg_band_equals_brute_force_on_8_rows():
    rows = _random_rows(11, 8)
    assert cl.cg_band(rows) == pytest.approx(_brute(rows), abs=1e-6)


def test_validation_errors_raise():
    good = _random_rows(5, 3)
    bad = [dict(r) for r in good]; bad[0]["weight_lb"] = bad[0]["weight_band_lb"][1] + 1
    with pytest.raises(ValueError):
        cl.closure_sum(bad)
    bad = [dict(r) for r in good]; bad[0]["weight_band_lb"] = [5, 1]
    with pytest.raises(ValueError):
        cl.cg_band(bad)
    bad = [{k: v for k, v in r.items() if k != "arm_band_fs"} for r in good]
    with pytest.raises(ValueError):
        cl.weight_band(bad)
    zero = [{"name": "z", "weight_lb": 0, "weight_band_lb": [0, 0], "arm_fs": 1, "arm_band_fs": [1, 1]}]
    with pytest.raises(ValueError):
        cl.closure_sum(zero)
    lo, hi = cl.weight_band(good)
    with pytest.raises(ValueError):
        cl.cg_band_at(good, hi + 1)
    assert cl.verdict(good, lo - 5, 50) != "closes"   # out-of-band target is a reason string, not a raise
    bad = [dict(r) for r in good]; del bad[0]["weight_lb"]
    with pytest.raises(ValueError):
        cl.verdict(bad, 100, 50)


def test_method_check_reproduces_the_n26ms_step_1():
    c = cl.closure_sum(METHOD_ROWS)
    ref = L["prototype_weights"]["rows"]["n26ms_empty_1"]["weight_lb"]
    assert ref == 693.4
    assert c.weight_band[0] <= ref <= c.weight_band[1]


def test_moving_the_engine_arm_5_in_moves_the_nominal_cg_by_its_moment_share():
    rows = [dict(r) for r in ROWS]
    i = next(k for k, r in enumerate(rows) if r["name"] == "engine")
    eng = dict(rows[i]); rows[i] = eng
    base = cl.closure_sum(rows)
    eng["arm_fs"] -= 5
    eng["arm_band_fs"] = [a - 5 for a in eng["arm_band_fs"]]
    moved = cl.closure_sum(rows)
    assert base.cg_fs - moved.cg_fs == pytest.approx(243 * 5 / base.weight_lb, rel=1e-9)
    assert cl.loaded_cg(moved.weight_lb, moved.cg_fs, "light_pilot") < _LIGHT


def test_verdict_category_is_the_same_for_730_and_727_9():
    # A property of THIS table only (both targets fail the same, first, weight-cap check); not a general claim.
    a = cl.verdict(ROWS, 730, 111.7)
    b = cl.verdict(ROWS, 727.9, 81541 / 727.9)
    assert (a == "closes") == (b == "closes")
    assert a.split(" over")[0] == b.split(" over")[0]


@pytest.mark.xfail(_V != "closes", strict=True, reason=f"ledger row 65: {_V}")
def test_empty_closes_on_the_om_sample():
    assert _V == "closes"


@pytest.mark.xfail(not (_LIGHT > 103.0 and 97.0 <= _HEAVY <= 103.0), strict=True,
                   reason=f"ledger row 65: from the closure nominal empty ({C.weight_lb:.2f} lb, FS {C.cg_fs:.2f}) "
                          f"the light sample lands at {_LIGHT:.2f} (needs > 103) and the heavy at {_HEAVY:.2f} (needs 97 to 103)")
def test_om_samples_from_the_ledger_empty():
    assert cl.loaded_cg(C.weight_lb, C.cg_fs, "light_pilot") > 103.0
    assert 97.0 <= cl.loaded_cg(C.weight_lb, C.cg_fs, "heavy_pilot") <= 103.0
