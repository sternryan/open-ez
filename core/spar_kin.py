"""Centre-section spar planform and cap maths (plans-1980 p86, p88).

The WL 21.7 label at the outer aft corner is unmodelled.
"""

from __future__ import annotations

import math

from config import config

G = config.geometry


def face_fs(bl: float, face: str) -> float:
    """Return the FS of the fwd or aft face at a given BL."""
    if face not in ("fwd", "aft"):
        raise ValueError(f"Invalid face: {face}")

    kink = G.spar_kink_bl
    sweep_rad = math.radians(G.spar_outboard_sweep_deg)
    slope = math.tan(sweep_rad)

    if face == "fwd":
        base = G.spar_fwd_face_fs
        if abs(bl) <= kink:
            return base
        return base + (abs(bl) - kink) * slope
    else:
        base = G.spar_aft_face_fs_centre
        if abs(bl) <= kink:
            return base
        return base + (abs(bl) - kink) * slope


def chord_fore_aft(bl: float) -> float:
    """Return the fore-aft chord (aft face FS minus forward face FS) at a given BL."""
    return face_fs(bl, "aft") - face_fs(bl, "fwd")


def chord_square(bl: float) -> float:
    """Return the chord square at a given BL."""
    if abs(bl) <= G.spar_kink_bl:
        return G.spar_chord_centreline_in
    return G.spar_chord_centreline_in * math.cos(
        math.radians(G.spar_outboard_sweep_deg)
    )


def plan_outline_right() -> list[tuple[float, float]]:
    """Return the 6 points of the right-side spar planform outline."""
    s = math.radians(G.spar_outboard_sweep_deg)
    fwd0 = face_fs(0.0, "fwd")
    aft0 = face_fs(0.0, "aft")
    kink = G.spar_kink_bl
    half_span = G.spar_half_span_bl

    fwd_tip = (half_span, face_fs(half_span, "fwd"))
    c = chord_square(half_span)
    aft_tip = (fwd_tip[0] - c * math.sin(s), fwd_tip[1] + c * math.cos(s))

    return [
        (0.0, fwd0),
        (kink, fwd0),
        fwd_tip,
        aft_tip,
        (kink, aft0),
        (0.0, aft0),
    ]


def bottom_wl(bl: float) -> float:
    """Return the bottom WL at a given BL."""
    if abs(bl) <= G.spar_bottom_flat_to_bl:
        return G.spar_bottom_wl
    bl_flat = G.spar_bottom_flat_to_bl
    bl_out = G.spar_half_span_bl
    wl_flat = G.spar_bottom_wl
    wl_out = G.spar_bottom_wl_outboard
    return wl_flat + (abs(bl) - bl_flat) * (wl_out - wl_flat) / (bl_out - bl_flat)


def top_wl(bl: float) -> float:
    """Return the top WL at a given BL."""
    return G.spar_top_wl


def depth(bl: float) -> float:
    """Return the spar depth at a given BL."""
    return top_wl(bl) - bottom_wl(bl)


def cap_end_bls(cap: str) -> list[float]:
    """Return the BLs where tapered cap strips end."""
    if cap not in ("top", "bottom"):
        raise ValueError(f"Invalid cap: {cap}")

    strips = G.spar_top_cap_strips_in if cap == "top" else G.spar_bottom_cap_strips_in
    tapered_count = len(
        G.spar_top_cap_partial_end_bl
        if cap == "top"
        else G.spar_bottom_cap_partial_end_bl
    )
    tapered_strips = strips[len(strips) - tapered_count :]
    return [length / 2 for length in tapered_strips]


def cap_plies(bl: float, cap: str) -> int:
    """Return the number of cap plies at a given BL."""
    if cap not in ("top", "bottom"):
        raise ValueError(f"Invalid cap: {cap}")

    ends = cap_end_bls(cap)
    full_count = len(strip_lengths(cap)) - len(ends)

    if abs(bl) > G.spar_full_ply_end_bl:
        return 0

    count = full_count
    for end_bl in ends:
        if abs(bl) <= end_bl:
            count += 1
    return count


def cap_thickness(bl: float, cap: str) -> float:
    """Return the cap thickness at a given BL."""
    return cap_plies(bl, cap) * G.spar_ply_thickness_laid_in


def strip_lengths(cap: str) -> tuple[float, ...]:
    """Return the lengths of the cap strips."""
    if cap not in ("top", "bottom"):
        raise ValueError(f"Invalid cap: {cap}")
    return tuple(
        G.spar_top_cap_strips_in if cap == "top" else G.spar_bottom_cap_strips_in
    )


def strip_total(cap: str) -> float:
    """Return the total length of the cap strips."""
    return sum(strip_lengths(cap))


def hard_points() -> list[dict[str, float]]:
    """Return the three hard points."""
    bl_in = G.spar_hp_inboard_bl_in
    wl_in = G.spar_hp_inboard_wl_in
    bl_out = G.spar_hp_outboard_bl_in
    wl_out_pair = G.spar_hp_outboard_wl_in

    fs_in = face_fs(bl_in, "aft")
    fs_out = face_fs(bl_out, "aft")

    return [
        {"bl": bl_in, "wl": wl_in, "fs_aft_face": fs_in},
        {"bl": bl_out, "wl": wl_out_pair[0], "fs_aft_face": fs_out},
        {"bl": bl_out, "wl": wl_out_pair[1], "fs_aft_face": fs_out},
    ]


def hard_point_spacing_along_aft_face() -> float:
    """Return the spacing between outboard hard points along the aft face."""
    bl_in = G.spar_hp_inboard_bl_in
    bl_out = G.spar_hp_outboard_bl_in
    sweep_rad = math.radians(G.spar_outboard_sweep_deg)
    return (bl_out - bl_in) / math.cos(sweep_rad)
