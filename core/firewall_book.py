"""Firewall stainless face and the accessories bolted to it (plans chapter 15, pdf pages p95, p96, p101).

Same frame and fidelity labels as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Printed: the firewall line at F.S. 125 and the 1 in torque-tube hole at B.L. 6.2 R, W.L. 12.3 (p101); the CS15
belcrank spans (p95); CS75 bushing 5/16 OD x 0.15 (p96). NOT printed: the firewall outline (A4, not held), the stainless
and insulation thickness, the belcrank and master-cylinder stations, the cylinder size. Every solid here is
``representational``; the stainless face reuses the fitted plywood outline of ``core.fuselage_book``.
"""

from __future__ import annotations

import cadquery as cq

from .fuselage_book import (
    FITTED_FIREWALL_THICKNESS,
    FusePart,
    G,
    _bulkhead_plate,
    z_of_wl,
)

_P95, _P96, _P101 = (f"plans-1980:p{n}" for n in (95, 96, 101))

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_STAINLESS_T = (
    0.03  # fitted, not book: stainless sheet thickness (the scan gives none)
)
FITTED_BELCRANK_BL = (
    4.0  # fitted, not book: BL of each belcrank pivot (p101 ticks only)
)
FITTED_BELCRANK_WL = (
    10.0  # fitted, not book: belcrank pivot WL, inside the 9 to 11 tick read (p101)
)
FITTED_MC_BL = 3.0  # fitted, not book: BL of each upright master cylinder
FITTED_MC_DIA = 1.0  # fitted, not book: master cylinder body diameter
FITTED_MC_LEN = 4.0  # fitted, not book: master cylinder body length
FITTED_MC_STANDOFF = (
    0.1  # fitted, not book: gap between the stainless and each cylinder
)

_STAINLESS_AFT = G.fs_firewall + FITTED_FIREWALL_THICKNESS + FITTED_STAINLESS_T
_HOLE_BL, _HOLE_WL = G.ctl_torque_tube_hole_bl_in, G.ctl_torque_tube_hole_wl_in


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound([w.val() for w in solids]))


def stainless_face() -> cq.Workplane:
    """Stainless sheet on the aft face of the plywood, plywood outline, torque-tube hole open on the right."""
    sheet = _bulkhead_plate(G.fs_firewall, FITTED_STAINLESS_T, outer=True).translate(
        (FITTED_FIREWALL_THICKNESS, 0, 0)
    )
    hole = (
        cq.Workplane("YZ")
        .circle(G.ctl_torque_tube_hole_dia_in / 2)
        .extrude(1.0)
        .translate((G.fs_firewall, _HOLE_BL, z_of_wl(_HOLE_WL)))
    )
    return sheet.cut(hole)


def belcranks() -> cq.Workplane:
    """Two CS15 belcrank plates (1/8, 1.6 x 1.85) with the CS75 bushing, on the stainless aft face."""
    t = 0.125
    solids = []
    for sg in (1.0, -1.0):
        y, z = sg * FITTED_BELCRANK_BL, z_of_wl(FITTED_BELCRANK_WL)
        plate = (
            cq.Workplane("XY")
            .box(t, 1.6, 1.85, centered=False)
            .translate((_STAINLESS_AFT, y - 0.8, z - 0.925))
        )
        bush = (
            cq.Workplane("YZ")
            .circle(5 / 32)
            .extrude(0.15)
            .translate((_STAINLESS_AFT + t, y, z))
        )
        solids += [plate, bush]
    return _compound(solids)


def master_cylinders() -> cq.Workplane:
    """Two upright cylinders aft of the stainless, centred in height between the engine-mount fittings."""
    mid = z_of_wl((G.spar_bottom_wl + G.spar_top_wl) / 2)
    r = FITTED_MC_DIA / 2
    x = _STAINLESS_AFT + FITTED_MC_STANDOFF + r
    return _compound(
        [
            cq.Workplane("XY")
            .circle(r)
            .extrude(FITTED_MC_LEN)
            .translate((x, sg * FITTED_MC_BL, mid - FITTED_MC_LEN / 2))
            for sg in (1.0, -1.0)
        ]
    )


COMPONENT_PARTS = {
    "fuselage.firewall_stainless": ("stainless",),
    "firewall.belcrank": ("belcrank",),
    "firewall.master_cylinders": ("master_cylinders",),
}


def build_firewall() -> dict[str, FusePart]:
    rep = "representational"
    return {
        "stainless": FusePart(
            "stainless",
            stainless_face(),
            rep,
            (_P101,),
            "stainless face on the aft face of the fitted plywood firewall; outline is A4-only (fitted); torque-tube hole 1 in at BL 6.2 R, WL 12.3 is printed, sheet thickness is not",
        ),
        "belcrank": FusePart(
            "belcrank",
            belcranks(),
            rep,
            (_P95, _P96),
            "CS15 plate spans and CS75 bushing are printed; pivot BL and WL are tick-read or fitted (WL 9 to 11 band); one plate per side",
        ),
        "master_cylinders": FusePart(
            "master_cylinders",
            master_cylinders(),
            rep,
            (_P96,),
            "upright cylinders between the engine-mount fittings; the book prints no station or size, all fitted",
        ),
    }
