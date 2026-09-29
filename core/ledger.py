"""Mass/CG ledger: cited rows, the manual's CG envelope, and its sample loadings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import yaml

LEDGER = Path(__file__).resolve().parents[1] / "data/mass_ledger.yaml"


class Row(NamedTuple):
    name: str
    weight_lb: float
    arm_in: float
    cls: str  # primary-structure | secondary | non-structural | payload | empty
    process: str
    cite: str


@lru_cache(maxsize=1)
def load_ledger() -> dict:
    return yaml.safe_load(LEDGER.read_text())


def cg(rows: list[Row]) -> tuple[float, float]:
    w = sum(r.weight_lb for r in rows)
    return w, sum(r.weight_lb * r.arm_in for r in rows) / w


def in_envelope(weight: float, cg_in: float, env: dict) -> bool:
    return weight <= env["max_lb"] and env["fwd_fs"] <= cg_in <= env["aft_fs"]
