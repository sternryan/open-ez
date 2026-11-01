"""Net cloth and resin quantities from layup solids (contract 18).

Area is ply-solid volume divided by the loft thickness. Catalog yards and a
derived buy need a positive finite sourced roll width and a sourced ply
thickness. A null, non-finite, non-positive, unsourced, or estimate-only
input keeps the authored estimate. Resin mass is the purchase-order ratio
with no scrap.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from guide.schema import Buy


@dataclass(frozen=True)
class Measure:
    """A length used in a conversion, with the flag that says whether it is truth."""

    value: float | None
    flag: str
    source: str


# Exact international inch and yard.
M_PER_IN = 0.0254
M_PER_YD = 0.9144

# Per-cloth cured-ply thickness. A derived buy needs it sourced. The area
# division itself uses the loft thickness PLY_T (see cloth_m2_by_op).
# data/materials.yaml bid_7725_wet and und_7715_wet t_ply.value are null
# (flag unsourced), so nothing there can be a cured thickness.
# unsourced: the value is the visual loft thickness in guide/layup_geometry.py
# (PLY_T). It turns a solid into area. It is not a cured-ply measurement and
# must not upgrade a buy to derived.
PLY_THICKNESS_IN = {
    "BID": Measure(
        0.10,
        "unsourced",
        "guide/layup_geometry.py PLY_T; data/materials.yaml bid_7725_wet t_ply is null",
    ),
    "UND": Measure(
        0.10,
        "unsourced",
        "guide/layup_geometry.py PLY_T; data/materials.yaml und_7715_wet t_ply is null",
    ),
}

# Roll width named in the catalog label. Unit on each row is yd.
# data/catalog/prices.yaml (flag page on the row).
ROLL_WIDTH_IN = {
    "bid-7725": Measure(
        38.0,
        "page",
        "data/catalog/prices.yaml bid-7725 label, 38 in, unit yd",
    ),
    "und-7715": Measure(
        38.0,
        "page",
        "data/catalog/prices.yaml und-7715 label, 38 in, unit yd",
    ),
    "carbon-282": Measure(
        50.0,
        "page",
        "data/catalog/prices.yaml carbon-282 label, 50 in, unit yd",
    ),
}

# The layup solids are the right half of a symmetric canard; "full span
# (108 in)" parses to bl_max 54 in guide/layup.py.
HALVES = 2

# Catalog cloth id -> layup cloth code (guide graph materials use UND / BID).
CLOTH_OF_ITEM = {
    "bid-7725": "BID",
    "und-7715": "UND",
}

# A derived yard buy needs both lengths sourced. estimate and unsourced are
# not enough (contract 18). "page" is a catalog page the record opened.
_SOURCED_LENGTH_FLAGS = frozenset({"official", "community", "derived", "page"})


def _sourced_positive_length(measure: Measure | None) -> bool:
    """True when a conversion input is finite, positive, and sourced."""
    if measure is None or measure.value is None:
        return False
    if measure.flag not in _SOURCED_LENGTH_FLAGS:
        return False
    return math.isfinite(measure.value) and measure.value > 0


# Mixed resin system per unit cloth mass, by weight, with no scrap.
# docs/harness/block5-coupon-purchase-order.md sizing note: roughly 1:1
# resin to cloth by weight. The 25% mixing loss in that note is kit-level
# scrap (spec section 12) and is not applied here. The 4.5 kg/gal figure in
# that note was not read from a TDS, so it is not a constant here.
RESIN_TO_CLOTH_BY_WEIGHT = 1.0


def cloth_m2_by_op(graph) -> dict[str, dict[str, float]]:
    """Net square meters, op id -> cloth code -> m², from layup solids only.

    Each ply solid is lofted PLY_T thick, so volume / PLY_T is its surface
    area. That divisor is the loft thickness, not PLY_THICKNESS_IN, which is
    the cured-ply value a derived buy waits on. Spar caps are left out: their
    solid fills the trough to a visual depth and the plans give the ply count
    only as "as required", so no area follows from it. Ops with no ply solid
    are absent. The solids model the right half (BL 0..semi-span, see
    guide/layup_geometry.py), and each layup op covers both halves, so the
    half-model area is doubled.
    """
    from guide import layup
    from guide.layup_geometry import PLY_T, build_layup

    ply_of = {p.node: p for p in layup.plies(graph)}
    solids = build_layup(graph)
    out: dict[str, dict[str, float]] = {}
    for component, nodes in solids.items():
        if component == "canard.core":
            continue
        for node, solid in nodes.items():
            p = ply_of[node]
            if p.op in layup.SPAR_CAP_OPS:
                continue
            m2 = HALVES * solid.Volume() / PLY_T * M_PER_IN**2
            by_cloth = out.setdefault(p.op, {})
            by_cloth[p.cloth] = by_cloth.get(p.cloth, 0.0) + m2
    return out


def m2_to_catalog_qty(area_m2: float, roll_width_in: float, unit: str) -> float:
    """Net m² to the catalog length unit, using roll width. No scrap."""
    length = area_m2 / (roll_width_in * M_PER_IN)
    if unit == "yd":
        return length / M_PER_YD
    if unit == "ft":
        return length / 0.3048
    if unit == "m":
        return length
    raise ValueError(f"Unknown unit: {unit}")


def can_derive(item: str) -> bool:
    """True when a buy of ``item`` has every input a derived yard qty needs.

    Both the cured-ply thickness and the roll width must be finite, positive,
    and sourced. A null, non-positive, non-finite, unsourced, or estimate-only
    input keeps the authored buy (contract 18).
    """
    cloth = CLOTH_OF_ITEM.get(item)
    if cloth is None:
        return False
    return _sourced_positive_length(
        PLY_THICKNESS_IN.get(cloth)
    ) and _sourced_positive_length(ROLL_WIDTH_IN.get(item))


def derived_cloth_buy(authored: Buy, area_m2: float) -> Buy:
    """Yard buy from net area.

    A null, non-finite, non-positive, missing, unsourced, or estimate-only
    roll width or ply thickness keeps ``authored`` qty and flag. Never store
    m² in a yard quantity.
    """
    if not can_derive(authored.item):
        return authored
    qty = m2_to_catalog_qty(area_m2, ROLL_WIDTH_IN[authored.item].value, "yd")
    return Buy(item=authored.item, qty=qty, flag="derived")


def resin_mass_kg(cloth_mass_kg: float) -> float:
    """Mixed-system mass at RESIN_TO_CLOTH_BY_WEIGHT. No scrap."""
    return cloth_mass_kg * RESIN_TO_CLOTH_BY_WEIGHT
