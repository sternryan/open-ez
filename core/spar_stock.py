"""Source-sized chapter 14 stock, before shaping, drilling or installation.

All shapes use a local stock frame and overlap at its origin.  They are not
installed airplane geometry or finished-part manufacturing models.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

import cadquery as cq

from config import config
from core.sources import check_citation

# The configuration BOM includes chapter 19 wing-side LWA2, LWA3 and LWA4.
# Chapter 14 installs only the following quantities (plans-1980:p86, p90).
SPAR_LWA_COUNTS = MappingProxyType(
    {"LWA1": 6, "LWA2": 2, "LWA3": 2, "LWA4": 4, "LWA5": 2}
)
SPRUCE_STOCK_COUNT = 4


@dataclass(frozen=True)
class SparStock:
    """One raw blank; eligibility says nothing about a finished fitting."""

    name: str
    solid: cq.Workplane
    cite: tuple[str, ...]
    note: str
    eligibility: Literal["stock-only"] = "stock-only"

    def __post_init__(self) -> None:
        if self.eligibility != "stock-only" or not self.cite:
            raise ValueError("spar stock requires citations and stock-only eligibility")
        for citation in self.cite:
            check_citation(citation)


def lwa_stock() -> dict[str, SparStock]:
    """Rectangular blanks: local x width, y height, z stock thickness.

    Corrected LWA4/LWA5 stock heights follow CP43.  No finished outline,
    corner radius, attachment hole or airplane transform is asserted.
    """
    stock: dict[str, SparStock] = {}
    for kind, height, thickness, width, _bom_count in config.geometry.spar_lwa_sizes:
        citations = ("plans-1980:p90",)
        if kind in {"LWA4", "LWA5"}:
            citations += ("cp-text:p43",)
        for number in range(1, SPAR_LWA_COUNTS[kind] + 1):
            name = f"{kind}.{number}"
            stock[name] = SparStock(
                name,
                cq.Workplane("XY").box(width, height, thickness, centered=False),
                citations,
                "rectangular chapter 14 stock only; chapter 19 wing-side blanks excluded; "
                "no finished outline, holes or installed placement",
            )
    return stock


def spruce_stock() -> dict[str, SparStock]:
    """Four unplaced raw spruce blocks, in a local stock frame."""
    dimensions = config.geometry.spar_spruce_block_in
    return {
        f"spruce.{number}": SparStock(
            f"spruce.{number}",
            cq.Workplane("XY").box(*dimensions, centered=False),
            ("plans-1980:p86",),
            "raw spruce stock only; no trough fit or installed placement",
        )
        for number in range(1, SPRUCE_STOCK_COUNT + 1)
    }
