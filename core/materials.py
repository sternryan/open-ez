"""Material property sets: each property is cited to a registered page or flagged unsourced."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from core.sources import check_citation

MATERIALS = Path(__file__).resolve().parents[1] / "data/materials.yaml"
PROPERTIES = (
    "E1", "E2", "G12", "nu12", "F1t", "F1c", "F2t", "F2c", "F6", "t_ply", "areal_mass",
)  # fmt: skip
USES = ("validation", "design-proxy", "book", "legacy")


@lru_cache(maxsize=1)
def load_materials() -> dict[str, dict]:
    return yaml.safe_load(MATERIALS.read_text())["materials"]


def check_material_set(name: str, m: dict) -> None:
    """Raise ValueError unless every property has exactly one of cite / flag: unsourced."""
    if m.get("use") not in USES:
        raise ValueError(f"{name}: use must be one of {USES}, got {m.get('use')!r}")
    props = m.get("properties", {})
    for key, p in props.items():
        has_cite, has_flag = "cite" in p, "flag" in p
        if has_cite and has_flag:
            raise ValueError(f"{name}.{key}: has both cite and flag")
        if not has_cite and not has_flag:
            raise ValueError(f"{name}.{key}: has neither cite nor flag")
        if has_flag and p["flag"] != "unsourced":
            raise ValueError(f"{name}.{key}: flag must be 'unsourced'")
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
