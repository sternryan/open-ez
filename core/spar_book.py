"""Centre-section spar display solids from the published planform and cap schedule.

Frame: x = FS, y = signed BL, z = WL - 17.4.  The box and cap bands are
representational display geometry. They deliberately do not reproduce the A11
cap-trough templates or assert fabrication eligibility.
"""

from __future__ import annotations

import cadquery as cq

from config import config

from . import spar_kin as kin
from .fuselage_book import WING_PLANE_WL, FusePart

G = config.geometry


def _z(wl: float) -> float:
    return wl - WING_PLANE_WL + G.wing_le_wl


def _wire(bl: float, x0: float, x1: float, z0: float, z1: float) -> cq.Wire:
    points = [
        cq.Vector(x0, bl, z0),
        cq.Vector(x1, bl, z0),
        cq.Vector(x1, bl, z1),
        cq.Vector(x0, bl, z1),
    ]
    return cq.Wire.makePolygon(points + [points[0]])


def _stations(half_span: float) -> list[float]:
    """Symmetric loft stations, retaining the published planform kink."""
    half = min(half_span, G.spar_half_span_bl)
    if half <= 0:
        raise ValueError("spar half span must be positive")
    values = {-half, half}
    if half > G.spar_bottom_flat_to_bl:
        values.update((-G.spar_bottom_flat_to_bl, G.spar_bottom_flat_to_bl))
    if half > G.spar_kink_bl:
        values.update((-G.spar_kink_bl, 0.0, G.spar_kink_bl))
    else:
        values.add(0.0)
    return sorted(values)


def _loft(half_span: float, section) -> cq.Workplane:
    wires = [section(bl) for bl in _stations(half_span)]
    return cq.Workplane("XY").add(cq.Solid.makeLoft(wires, True))


def spar_box() -> cq.Workplane:
    """Closed foam-box envelope from the p88 face and WL stations."""
    envelope = _loft(
        G.spar_half_span_bl,
        lambda bl: _wire(
            bl,
            kin.face_fs(bl, "fwd"),
            kin.face_fs(bl, "aft"),
            _z(kin.bottom_wl(bl)),
            _z(kin.top_wl(bl)),
        ),
    )
    right = kin.plan_outline_right()
    outline = [(fs, bl) for bl, fs in right] + [
        (fs, -bl) for bl, fs in reversed(right) if bl != 0
    ]
    plan = (
        cq.Workplane("XY", origin=(0, 0, _z(G.spar_bottom_wl)))
        .polyline(outline)
        .close()
        .extrude(G.spar_depth_in)
    )
    return envelope.intersect(plan)


def cap_plies(cap: str) -> list[cq.Solid]:
    """One volume per published UND strip, placed on the corresponding face.

    The 3-in tape width and laid ply thickness are published.  The missing A11
    trough profile is intentionally not inferred; these are disclosed display
    bands whose span schedule follows the published strip lengths.
    """
    if cap not in {"top", "bottom"}:
        raise ValueError(f"invalid cap {cap!r}")
    solids: list[cq.Solid] = []
    for index, length in enumerate(kin.strip_lengths(cap)):
        half_span = min(length / 2, G.spar_full_ply_end_bl)
        thickness = G.spar_ply_thickness_laid_in

        def section(
            bl: float, *, ply_index: int = index, ply_thickness: float = thickness
        ) -> cq.Wire:
            aft = kin.face_fs(bl, "aft")
            if cap == "top":
                z1 = _z(kin.top_wl(bl)) - ply_index * ply_thickness
                z0 = z1 - ply_thickness
            else:
                z0 = _z(kin.bottom_wl(bl)) + ply_index * ply_thickness
                z1 = z0 + ply_thickness
            return _wire(bl, aft - G.spar_cap_tape_width_in, aft, z0, z1)

        solids.append(_loft(half_span, section).val())
    return solids


def spar_caps(cap: str) -> cq.Workplane:
    """Compound of every separately scheduled cap ply."""
    return cq.Workplane("XY").add(cq.Compound.makeCompound(cap_plies(cap)))


def build_spar() -> dict[str, FusePart]:
    """Return only the sourced OE1 spar solids currently suitable for display."""
    return {
        "box": FusePart(
            "box",
            spar_box(),
            "representational",
            ("plans-1980:p88",),
            "overlapping display envelope, not physical foam or additive mass; constant upper WL omits unresolved 21.7 tip label; no A11 trough profile or fabrication claim",
        ),
        "cap_top": FusePart(
            "cap_top",
            spar_caps("top"),
            "representational",
            ("plans-1980:p85", "plans-1980:p86"),
            "12 separately scheduled 3-in UND display bands; A11 trough profile is unavailable",
        ),
        "cap_bottom": FusePart(
            "cap_bottom",
            spar_caps("bottom"),
            "representational",
            ("plans-1980:p85", "plans-1980:p86"),
            "9 separately scheduled 3-in UND display bands; A11 trough profile is unavailable",
        ),
    }
