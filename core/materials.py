"""Material property sets: each property is cited to a registered page or flagged.

Two flags. `unsourced`: no source found yet. `requires_original_test`: a recorded search shows no public
source exists, so only an owner test can supply the value; the property then carries the search
evidence, the closing test (ASTM method plus a Block 5 coupon id) and a link to the coupon test plan.
Neither flag can let a gate pass.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from core.sources import check_citation

MATERIALS = Path(__file__).resolve().parents[1] / "data/materials.yaml"
PROPERTIES = (
    "E1", "E2", "G12", "nu12", "F1t", "F1c", "F2t", "F2c", "F6", "t_ply", "areal_mass",
)  # fmt: skip
USES = ("validation", "design-proxy", "book", "legacy")
FLAGS = ("unsourced", "requires_original_test")
TEST_FIELDS = ("search", "closing_test", "test_plan")
COUPON_ID = re.compile(r"^B5-[A-Z0-9]+-(T0|T90|C0|C90|S45)$")


def _check_test_fields(where: str, p: dict) -> None:
    if p["flag"] != "requires_original_test":
        extra = [f for f in TEST_FIELDS if f in p]
        if extra:
            raise ValueError(f"{where}: {extra} belong to requires_original_test only")
        return
    if p.get("value") is not None:
        raise ValueError(f"{where}: requires_original_test must have value null")
    missing = [f for f in TEST_FIELDS if not p.get(f)]
    if missing:
        raise ValueError(f"{where}: requires_original_test needs {missing}")
    test = p["closing_test"]
    if not str(test.get("method", "")).startswith("ASTM D"):
        raise ValueError(f"{where}: closing_test.method must be an ASTM method")
    if not COUPON_ID.match(str(test.get("coupon", ""))):
        raise ValueError(
            f"{where}: closing_test.coupon {test.get('coupon')!r} is not a coupon id"
        )
    if not str(p["test_plan"]).endswith(".md"):
        raise ValueError(f"{where}: test_plan must link the coupon test plan")


@lru_cache(maxsize=1)
def load_materials() -> dict[str, dict]:
    return yaml.safe_load(MATERIALS.read_text())["materials"]


def check_material_set(name: str, m: dict) -> None:
    """Raise ValueError unless every property has exactly one of cite / flag (one of FLAGS)."""
    if m.get("use") not in USES:
        raise ValueError(f"{name}: use must be one of {USES}, got {m.get('use')!r}")
    props = m.get("properties", {})
    for key, p in props.items():
        has_cite, has_flag = "cite" in p, "flag" in p
        if has_cite and has_flag:
            raise ValueError(f"{name}.{key}: has both cite and flag")
        if not has_cite and not has_flag:
            raise ValueError(f"{name}.{key}: has neither cite nor flag")
        if has_flag and p["flag"] not in FLAGS:
            raise ValueError(f"{name}.{key}: flag must be one of {FLAGS}")
        if has_flag:
            _check_test_fields(f"{name}.{key}", p)
        if "units" not in p:
            raise ValueError(f"{name}.{key}: units missing")
        if has_cite:
            check_citation(p["cite"])
    if m["use"] == "validation" and props and all("flag" in p for p in props.values()):
        raise ValueError(
            f"{name}: a set with every property unsourced cannot be validation"
        )


def get_material(name: str) -> dict:
    """Return a material set by id; an unknown id raises instead of falling back to another material."""
    mats = load_materials()
    if name not in mats:
        raise KeyError(f"unknown material {name!r}; known: {sorted(mats)}")
    return mats[name]
