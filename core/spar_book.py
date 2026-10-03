"""Centre-section spar display solids from the published planform and cap schedule.

Frame: x = FS, y = signed BL, z = WL - 17.4.  The box and cap bands are
representational display geometry. They deliberately do not reproduce the A11
cap-trough templates or assert fabrication eligibility.
"""

from __future__ import annotations

import math

import cadquery as cq

from config import config

from . import spar_kin as kin
from .fuselage_book import WING_PLANE_WL, FusePart

G = config.geometry

_P84, _P85, _P86, _P87, _P88, _P89, _P90 = (
    f"plans-1980:p{n}" for n in (84, 85, 86, 87, 88, 89, 90)
)

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_CS67_INSET = (
    0.5  # fitted, not book: CS6 and CS7 stand this far inside the box envelope
)
FITTED_EM12_BL = (
    5.5,
    7.5,
)  # fitted, not book: BL of the inner leg edge of the two EM12 angles per side
FITTED_EM12_AFT = (
    1.6  # fitted, not book: p87's 1.6 read as the angle's aft extent past FS 125
)
FITTED_SH1_FS = 119.5  # fitted, not book: forward end of each SH1 on the spar top (bolt FS unprinted)
FITTED_SH1_BL = 5.0  # fitted, not book: SH1 centre BL (p87 gives no station)
FITTED_JIG_T = (
    0.75  # fitted, not book: particle-board thickness of the jig upright and shelf
)

_JIG_UPRIGHT_HEIGHT = 12.5  # p89 upright strip
_JIG_SHELF_WIDTH = 6.05  # p88 operation text
_MID_WL = (G.spar_bottom_wl + G.spar_top_wl) / 2


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


def _s() -> float:
    return math.radians(G.spar_outboard_sweep_deg)


def _face_x(bl: float, off: float) -> float:
    """FS of the point `off` aft of the aft face (square to it) whose BL is exactly `bl`."""
    if abs(bl) <= G.spar_kink_bl:
        return kin.face_fs(bl, "aft") + off
    return kin.face_fs(bl, "aft") + off / math.cos(_s())


def _plate(
    centre: tuple[float, float, float], t: float, w: float, h: float, swept: bool
) -> cq.Workplane:
    """Plate of thickness t along the face normal, width w along the face, height h in z."""
    wp = cq.Workplane("XY").box(t, w, h)
    if swept:
        wp = wp.rotate((0, 0, 0), (0, 0, 1), -G.spar_outboard_sweep_deg)
    return wp.translate(centre)


def _across(
    centre: tuple[float, float, float], t: float, w: float, h: float
) -> cq.Workplane:
    """Plate whose plane is square to the aft face (normal along the span direction)."""
    return (
        cq.Workplane("XY")
        .box(t, w, h)
        .rotate((0, 0, 0), (0, 0, 1), 90 - G.spar_outboard_sweep_deg)
        .translate(centre)
    )


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Compound.makeCompound([w.val() for w in solids]))


def _pair(wp: cq.Workplane) -> cq.Workplane:
    return _compound([wp, wp.mirror("XZ")])


def end_bulkheads() -> cq.Workplane:
    """CS5 and CS8: 1/4 PVC end plates, 6.30 x 6.83, abutting the spar's outboard end plane."""
    s, t = _s(), 0.25  # t: 6 mm PVC (p90 foam list)
    hs = G.spar_half_span_bl
    c = kin.chord_square(hs)
    cx = kin.face_fs(hs, "fwd") + (c / 2) * math.cos(s) + (t / 2) * math.sin(s)
    cy = hs - (c / 2) * math.sin(s) + (t / 2) * math.cos(s)
    h = G.spar_end_bulkhead_height_in
    z0 = _z(kin.bottom_wl(hs))
    return _pair(_across((cx, cy, z0 + h / 2), t, G.spar_end_bulkhead_width_in, h))


def interior_bulkheads() -> cq.Workplane:
    """CS6 and CS7: 1/4 PVC, 27 in from the centreline (p84 text), inside the box envelope."""
    bl = 27.0
    cx = (kin.face_fs(bl, "fwd") + kin.face_fs(bl, "aft")) / 2
    w = kin.chord_square(bl) - 2 * FITTED_CS67_INSET
    h = kin.depth(bl) - 2 * FITTED_CS67_INSET
    zc = _z(kin.bottom_wl(bl) + kin.depth(bl) / 2)
    return _pair(_across((cx, bl, zc), 0.25, w, h))


def lwa_layout() -> list[tuple[str, float, float, float]]:
    """(kind, BL, WL, offset from the aft face; negative is inside the box) per installed LWA.

    The hard points are book (p88). Which kind sits where is the reading that closes the p90
    counts (LWA1 6, LWA2 2, LWA3 2, LWA4 4, LWA5 2); the stacking order is a stand-in."""
    in_bl, in_wl = G.spar_hp_inboard_bl_in, G.spar_hp_inboard_wl_in
    out_bl, out_wls = G.spar_hp_outboard_bl_in, G.spar_hp_outboard_wl_in
    rows: list[tuple[str, float, float, float]] = []
    for sg in (1.0, -1.0):
        rows += [
            ("LWA5", sg * in_bl, in_wl, -0.125),
            ("LWA1", sg * in_bl, in_wl, -0.3125),
            ("LWA2", sg * in_bl, in_wl, 0.0625),
        ]
        for wl in out_wls:
            rows += [
                ("LWA4", sg * out_bl, wl, -0.125),
                ("LWA1", sg * out_bl, wl, -0.3125),
            ]
        rows.append(("LWA3", sg * out_bl, sum(out_wls) / 2, 0.0625))
    return rows


def lwa_plates() -> dict[str, cq.Workplane]:
    """Installed LWA plates by kind, each a compound; sizes are the CP-corrected p90 stock."""
    size = {k: (h, t, w) for k, h, t, w, _n in G.spar_lwa_sizes}
    solids: dict[str, list[cq.Workplane]] = {k: [] for k in size}
    for kind, bl, wl, off in lwa_layout():
        h, t, w = size[kind]
        solids[kind].append(
            _plate((_face_x(bl, off), bl, _z(wl)), t, w, h, abs(bl) > G.spar_kink_bl)
        )
    return {k.lower(): _compound(v) for k, v in solids.items()}


def spruce_blocks() -> cq.Workplane:
    """Four 1 x 1 x 3 spruce blocks at BL +/-7.5: under the top cap and over the bottom cap."""
    ly, lz, lx = G.spar_spruce_block_in
    top_cap = len(G.spar_top_cap_strips_in) * G.spar_ply_thickness_laid_in
    bot_cap = len(G.spar_bottom_cap_strips_in) * G.spar_ply_thickness_laid_in
    aft = kin.face_fs(G.spar_spruce_block_bl, "aft")
    blocks = []
    for sg in (1.0, -1.0):
        y = sg * G.spar_spruce_block_bl
        for z0 in (_z(G.spar_top_wl) - top_cap - lz, _z(G.spar_bottom_wl) + bot_cap):
            blocks.append(
                cq.Workplane("XY")
                .box(lx, ly, lz, centered=False)
                .translate((aft - lx, y - ly / 2, z0))
            )
    return _compound(blocks)


def _angle(x0: float, y0: float, z0: float, length: float) -> cq.Workplane:
    t, leg = 0.125, 1.0  # p87: 1 x 1 x 1/8 angle
    pts = [(0, 0), (leg, 0), (leg, t), (t, t), (t, leg), (0, leg)]
    return (
        cq.Workplane("XY").polyline(pts).close().extrude(length).translate((x0, y0, z0))
    )


def em12() -> cq.Workplane:
    """Four 8 in angles, upright, standing aft of the firewall stack (stainless and plywood)."""
    length = G.spar_em12_length_in
    z0 = _z(_MID_WL) - length / 2
    x0 = G.fs_firewall + FITTED_EM12_AFT - 1.0
    right = [_angle(x0, bl, z0, length) for bl in FITTED_EM12_BL]
    return _compound(right + [w.mirror("XZ") for w in right])


def sh1() -> cq.Workplane:
    """Two SH1 plates, 2.3 x 0.7 x 1/8, lying on the spar top."""
    top = _z(G.spar_top_wl)
    return _compound(
        [
            cq.Workplane("XY")
            .box(2.3, 0.7, 0.125, centered=False)
            .translate((FITTED_SH1_FS, sg * FITTED_SH1_BL - 0.35, top))
            for sg in (1.0, -1.0)
        ]
    )


def _aft_line() -> list[tuple[float, float]]:
    hs, kink = G.spar_half_span_bl, G.spar_kink_bl
    return [(kin.face_fs(bl, "aft"), bl) for bl in (-hs, -kink, kink, hs)]


def jig() -> cq.Workplane:
    """Workshop jig: the swept upright behind the aft face and the shelf the CS1 PVC lies on."""
    line, t = _aft_line(), FITTED_JIG_T
    board = (
        cq.Workplane("XY", origin=(0, 0, _z(_MID_WL) - _JIG_UPRIGHT_HEIGHT / 2))
        .polyline(line + [(x + t, y) for x, y in reversed(line)])
        .close()
        .extrude(_JIG_UPRIGHT_HEIGHT)
    )
    shelf = (
        cq.Workplane("XY", origin=(0, 0, _z(G.spar_bottom_wl) - t))
        .polyline([(x - _JIG_SHELF_WIDTH, y) for x, y in line] + list(reversed(line)))
        .close()
        .extrude(t)
    )
    return board.union(shelf)


SPAR_COMPONENT_PARTS = {
    "spar.box": ("box",),
    "spar.cap_top": ("cap_top",),
    "spar.cap_bottom": ("cap_bottom",),
    "spar.bulkheads": ("end_bulkheads", "interior_bulkheads"),
    "spar.lwa": ("lwa1", "lwa2", "lwa3", "lwa4", "lwa5"),
    "spar.spruce_blocks": ("spruce_blocks",),
    "spar.em12": ("em12",),
    "spar.sh1": ("sh1",),
    "spar.jig": ("jig",),
}
COMPONENT_PARTS = SPAR_COMPONENT_PARTS


def build_spar() -> dict[str, FusePart]:
    """Every M2.5 spar solid: the three OE1 display solids, the installed fittings and the workshop jig."""
    rep = "representational"
    parts = {
        "box": FusePart(
            "box",
            spar_box(),
            rep,
            (_P88,),
            "overlapping display envelope, not physical foam or additive mass; constant upper WL omits unresolved 21.7 tip label; no A11 trough profile or fabrication claim",
        ),
        "cap_top": FusePart(
            "cap_top",
            spar_caps("top"),
            rep,
            (_P85, _P86),
            "12 separately scheduled 3-in UND display bands; A11 trough profile is unavailable",
        ),
        "cap_bottom": FusePart(
            "cap_bottom",
            spar_caps("bottom"),
            rep,
            (_P85, _P86),
            "9 separately scheduled 3-in UND display bands; A11 trough profile is unavailable",
        ),
        "end_bulkheads": FusePart(
            "end_bulkheads",
            end_bulkheads(),
            rep,
            (_P90,),
            "CS5 and CS8, 6.30 x 6.83 printed size, abutting the outboard end plane; which CS number takes which side is not read from the scan",
        ),
        "interior_bulkheads": FusePart(
            "interior_bulkheads",
            interior_bulkheads(),
            rep,
            (_P84,),
            "CS6 and CS7 at BL 27 (text); section is the box less a fitted inset; inside the display envelope by design",
        ),
        "spruce_blocks": FusePart(
            "spruce_blocks",
            spruce_blocks(),
            rep,
            (_P86,),
            "four 1 x 1 x 3 blocks at BL 7.5, fore-aft along the 3 in cap tape; vertical position stacked against the cap plies; inside the display envelope by design",
        ),
        "em12": FusePart(
            "em12",
            em12(),
            rep,
            (_P87,),
            "four 8 in angles, upright aft of the firewall; BL and FS placement fitted (the scan gives only 1.6 aft of the firewall)",
        ),
        "sh1": FusePart(
            "sh1",
            sh1(),
            rep,
            (_P87,),
            "two aft-harness plates on the spar top; station unprinted, fitted",
        ),
        "jig": FusePart(
            "jig",
            jig(),
            rep,
            (_P88, _P89),
            "workshop jig, display only, not part of the installed airframe; upright height and shelf width printed, thickness and placement fitted",
        ),
    }
    for name, wp in lwa_plates().items():
        parts[name] = FusePart(
            name,
            wp,
            rep,
            (_P90, "cp-text:p43") if name in {"lwa4", "lwa5"} else (_P90,),
            "installed on the aft face at the p88 hard points; stacking and kind-to-point assignment are a stand-in; wing attach bolt FS unsourced (chapter 19)",
        )
    return parts
