"""Closure table helpers for the 2.n ledger closure."""

import hashlib
import json
from typing import NamedTuple

from core.ledger import load_ledger


def block_sha256() -> str:
    b = load_ledger()["closure"]
    return hashlib.sha256(json.dumps(b, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ---- closure sum, exact bands and verdict (crew A2, 2026-10-04) ----
_L = load_ledger()
_E = _L["empty"]
_LIGHT = _L["samples"]["light_pilot"]
# CG shift of the empty airplane that carries the light sample from its book CG to the 103 limit.
CG_CAP_IN = round(abs(103.0 - _LIGHT["book_cg_in"]) * _LIGHT["book_total_lb"] / _E["weight_lb"], 3)  # 1.462
WEIGHT_CAP_LB = 20.0


class Closure(NamedTuple):
    weight_lb: float
    cg_fs: float
    weight_band: tuple
    cg_band: tuple


def _validate(rows) -> None:
    if not rows:
        raise ValueError("no rows")
    for r in rows:
        try:
            lo, hi = r["weight_band_lb"]
            alo, ahi = r["arm_band_fs"]
            w, a = r["weight_lb"], r["arm_fs"]
        except KeyError as e:
            raise ValueError(f"row {r.get('name', '?')} is missing key {e}") from e
        n = r.get("name", "?")
        if lo > hi or alo > ahi:
            raise ValueError(f"row {n}: band lo > hi")
        if not (lo <= w <= hi and alo <= a <= ahi):
            raise ValueError(f"row {n}: nominal outside its own band")
    if sum(r["weight_lb"] for r in rows) <= 0 or sum(r["weight_band_lb"][1] for r in rows) <= 0:
        raise ValueError("total weight must be positive")


def weight_band(rows) -> tuple:
    _validate(rows)
    return (sum(r["weight_band_lb"][0] for r in rows), sum(r["weight_band_lb"][1] for r in rows))


def cg_band_at(rows, W) -> tuple:
    """Exact min and max CG with total weight exactly W (greedy LP optimum)."""
    wlo, whi = weight_band(rows)
    if not (wlo - 1e-9 <= W <= whi + 1e-9):
        raise ValueError(f"W {W} outside the weight band ({wlo}, {whi})")
    if W <= 0:
        raise ValueError("W must be positive")
    out = []
    for side in (0, 1):
        order = sorted(rows, key=lambda r: r["arm_band_fs"][side], reverse=bool(side))
        rem = W - sum(r["weight_band_lb"][0] for r in rows)
        m = 0.0
        for r in order:
            lo, hi = r["weight_band_lb"]
            add = min(max(rem, 0.0), hi - lo)
            rem -= add
            m += (lo + add) * r["arm_band_fs"][side]
        out.append(m / W)
    return out[0], out[1]


def cg_band(rows) -> tuple:
    """Unconditional CG band (any total weight in the band), exact by bisection. Reporting only."""
    _validate(rows)
    out = []
    for side in (0, 1):
        lo = min(r["arm_band_fs"][0] for r in rows)
        hi = max(r["arm_band_fs"][1] for r in rows)
        for _ in range(100):
            c = (lo + hi) / 2
            if side:   # is a CG >= c reachable?
                ok = sum(max(w * (r["arm_band_fs"][1] - c) for w in r["weight_band_lb"]) for r in rows) >= 0
                lo, hi = (c, hi) if ok else (lo, c)
            else:      # is a CG <= c reachable?
                ok = sum(min(w * (r["arm_band_fs"][0] - c) for w in r["weight_band_lb"]) for r in rows) <= 0
                lo, hi = (lo, c) if ok else (c, hi)
        out.append((lo + hi) / 2)
    return out[0], out[1]


def closure_sum(rows=None) -> Closure:
    rows = rows if rows is not None else load_ledger()["closure"]["rows"]
    _validate(rows)
    w = sum(r["weight_lb"] for r in rows)
    m = sum(r["weight_lb"] * r["arm_fs"] for r in rows)
    return Closure(w, m / w, weight_band(rows), cg_band(rows))


def verdict(rows, target_w, target_cg) -> str:
    """'closes', or the first failing reason. Programming errors raise."""
    wlo, whi = weight_band(rows)
    nominal = sum(r["weight_lb"] for r in rows)
    hw = (whi - wlo) / 2
    if hw > WEIGHT_CAP_LB:
        return f"weight half-band {hw:.2f} lb over the {WEIGHT_CAP_LB} lb cap"
    if not wlo <= target_w <= whi:
        miss = min(abs(target_w - wlo), abs(target_w - whi))
        return f"target weight {target_w} lb outside the weight band ({wlo:.1f}, {whi:.1f}); nominal sum {nominal:.1f} lb, miss {miss:.1f} lb"
    clo, chi = cg_band_at(rows, target_w)
    hc = (chi - clo) / 2
    if hc > CG_CAP_IN:
        return f"CG half-band {hc:.2f} in at {target_w} lb over the {CG_CAP_IN} in cap"
    if not clo <= target_cg <= chi:
        miss = min(abs(target_cg - clo), abs(target_cg - chi))
        return f"target CG {target_cg:.2f} outside the CG band ({clo:.2f}, {chi:.2f}) at {target_w} lb, miss {miss:.2f} in"
    return "closes"


def loaded_cg(empty_w: float, empty_cg: float, sample: str) -> float:
    L = load_ledger()
    s = L["samples"][sample]
    arms = L["loads"]
    W = empty_w + sum(s["items"].values())
    return (empty_w * empty_cg + sum(v * arms[k]["arm_in"] for k, v in s["items"].items())) / W
