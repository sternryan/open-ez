"""Control system and pitch/roll trim (plans chapters 16 and 17, pdf pages p97 to p107, with the CP-corrected values).

Same frame and fidelity labels as ``core.fuselage_book``: x = F.S., y = B.L. (right positive), z = ``z_of_wl``.

Printed: the stick pivot planes F.S. 45.5 and 89.7 (medium confidence), the torque-tube hole B.L. 6.2 R, W.L. 12.3,
console lengths and widths, tube and stick lengths, the rudder conduit (82 in at W.L. 8), the trim handle's panel dimension
(F.S. 40 + 9.5 = 49.5), pivot W.L. 8.6 and the spring sizes. NOT printed: console outlines and positions, stick fore-aft
placement and grip, the pitch stops, the Roncz elevator arm, the roll-trim stations. Every solid is ``representational``.
Stick angles come from ``core.controls_kin`` (Roncz travel only); this module holds no travel number of its own.
"""

from __future__ import annotations

import math

import cadquery as cq

from . import controls_kin as ck
from .fuselage_book import FusePart, G, z_of_wl

_P97, _P98, _P99, _P103, _P105, _P106, _P107 = (
    f"plans-1980:p{n}" for n in (97, 98, 99, 103, 105, 106, 107)
)

# Fitted, not book. Each is a stand-in; none enters config, GEOMETRY_PROVENANCE or a ledger readout.
FITTED_CONSOLE_LEAD = (
    1.0  # fitted, not book: console starts this far forward of its stick pivot plane
)
FITTED_CONSOLE_BELOW_TUBE = (
    1.5  # fitted, not book: console floor this far below the torque-tube axis
)
FITTED_GRIP_LEN = 3.0  # fitted, not book: stick grip length above the printed stub
FITTED_GRIP_R = 0.4  # fitted, not book: stick grip radius
FITTED_CONDUIT_BL = 5.0  # fitted, not book: BL of each rudder conduit (p103 prints the WL and length only)
FITTED_CONDUIT_R = 0.25  # fitted, not book: conduit outside radius
FITTED_PTH_BL = (
    -9.5
)  # fitted, not book: handle plane on the left, at the sleeve BL magnitude (CP25)
FITTED_PTH_PIN_R = 0.25  # fitted, not book: pivot pin radius
FITTED_PTS_GAP = 1.0  # fitted, not book: gap between the panel and the forward end of each PTS spring
FITTED_PTS_R = 0.175  # fitted, not book: spring radius, from the printed 0.350 OD
FITTED_RT_X = (
    80.5,
    82.0,
    83.5,
)  # fitted, not book: F.S. of RT2, RT1, RT2 in the gap between the consoles
FITTED_RT_TAB = (1.0, 2.0)  # fitted, not book: RT2 width (y) and height (z)
FITTED_RT1_H = 3.5  # fitted, not book: RT1 lever height above the tube top
FITTED_RTS_R = 0.15  # fitted, not book: roll-trim spring radius
FITTED_RTS_Z = 3.0  # fitted, not book: roll-trim spring height above the tube axis

_TUBE_BL, _TUBE_WL = G.ctl_torque_tube_hole_bl_in, G.ctl_torque_tube_hole_wl_in
_TUBE_OD, _TUBE_WALL = 0.75, 0.058  # p99 CS105 3/4 x .058
_STICK_R = 5 / 16  # p99 CS103 and CS119 are 5/8 OD
_WALL = 0.35  # p97 console foam
_PLANES = {"front": G.ctl_stick_pivot_fs_front, "rear": G.ctl_stick_pivot_fs_rear}
_STUB = {"front": G.ctl_cs103_length_in, "rear": G.ctl_cs119_length_in}


def _cyl(
    r: float, length: float, start: cq.Vector, direction: cq.Vector
) -> cq.Workplane:
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(r, length, start, direction))


def _compound(solids: list[cq.Workplane]) -> cq.Workplane:
    return cq.Workplane("XY").add(
        cq.Compound.makeCompound([s for w in solids for s in w.vals()])
    )


def torque_tube_axis() -> tuple[cq.Vector, cq.Vector]:
    """Axis ends of the torque tube: the front pivot plane to the firewall's forward face."""
    z = z_of_wl(_TUBE_WL)
    return (
        cq.Vector(G.ctl_stick_pivot_fs_front, _TUBE_BL, z),
        cq.Vector(G.fs_firewall, _TUBE_BL, z),
    )


def stick_axis(
    which: str, elevator_deflection_deg: float = 0.0, roll_deg: float = 0.0
) -> tuple[cq.Vector, cq.Vector]:
    """(base on the tube axis, grip tip) of a stick. Pitch comes from the Roncz-clamped kinematics."""
    if which not in _PLANES:
        raise ValueError(f"unknown stick {which!r}")
    a = math.radians(
        ck.stick_angle_deg(ck.clamp_deflection_deg(elevator_deflection_deg))
    )
    b = math.radians(G.ctl_stick_cant_inboard_deg + ck.torque_tube_roll_deg(roll_deg))
    direction = cq.Vector(
        -math.sin(a), -math.cos(a) * math.sin(b), math.cos(a) * math.cos(b)
    )
    base = cq.Vector(_PLANES[which], _TUBE_BL, z_of_wl(_TUBE_WL))
    return base, base + direction * (_STUB[which] + FITTED_GRIP_LEN)


def torque_tube() -> cq.Workplane:
    a, b = torque_tube_axis()
    d = cq.Vector(1, 0, 0)
    n = b.x - a.x
    outer = _cyl(_TUBE_OD / 2, n, a, d)
    return outer.cut(_cyl(_TUBE_OD / 2 - _TUBE_WALL, n, a, d))


def _console(
    which: str, length: float, width: float, h_fwd: float, h_aft: float
) -> cq.Workplane:
    """Open-topped, open-ended trough: floor and two foam walls, sloping top if the heights differ."""
    x0 = _PLANES[which] - FITTED_CONSOLE_LEAD
    zb = z_of_wl(_TUBE_WL) - FITTED_CONSOLE_BELOW_TUBE
    y0 = _TUBE_BL - width / 2
    profile = [(x0, zb), (x0 + length, zb), (x0 + length, zb + h_aft), (x0, zb + h_fwd)]
    outer = (
        cq.Workplane("XZ", origin=(0, y0 + width, 0))
        .polyline(profile)
        .close()
        .extrude(width)
    )
    cavity = (
        cq.Workplane("XY")
        .box(length + 1, width - 2 * _WALL, h_fwd + 1, centered=False)
        .translate((x0 - 0.5, y0 + _WALL, zb + _WALL))
    )
    return outer.cut(cavity)


def front_console() -> cq.Workplane:
    return _console("front", 30.1, 3.5, 9.1, 9.1)


def rear_console() -> cq.Workplane:
    return _console("rear", 25.8, 3.1, 8.0, 3.0)


def stick(
    which: str, elevator_deflection_deg: float = 0.0, roll_deg: float = 0.0
) -> cq.Workplane:
    """One stick: the printed stub on the tube axis and a fitted grip above it."""
    base, tip = stick_axis(which, elevator_deflection_deg, roll_deg)
    d = (tip - base).normalized()
    stub_end = base + d * _STUB[which]
    return _compound(
        [
            _cyl(_STICK_R, _STUB[which], base, d),
            _cyl(FITTED_GRIP_R, FITTED_GRIP_LEN, stub_end, d),
        ]
    )


def pitch_pushrod(elevator_deflection_deg: float = 0.0) -> cq.Workplane:
    """CS102 + CS136 (12.7 + 8.5) from the front stick's rod end, running forward, clear of the stick."""
    base, tip = stick_axis("front", elevator_deflection_deg)
    rod_end = base + (tip - base).normalized() * G.ctl_stick_lever_fit_in
    length = 12.7 + 8.5  # p99 CS102 + CS136
    start = cq.Vector(rod_end.x - _STICK_R - 0.1 - length, rod_end.y, rod_end.z)
    return _cyl(0.25, length, start, cq.Vector(1, 0, 0))  # p99 1/2 OD tube


def rudder_conduits() -> cq.Workplane:
    x0 = G.fs_firewall - G.ctl_rudder_conduit_length_in
    z = z_of_wl(G.ctl_rudder_conduit_wl_in)
    return _compound(
        [
            _cyl(
                FITTED_CONDUIT_R,
                G.ctl_rudder_conduit_length_in,
                cq.Vector(x0, sg * FITTED_CONDUIT_BL, z),
                cq.Vector(1, 0, 0),
            )
            for sg in (1.0, -1.0)
        ]
    )


def pth_pivot_xz() -> tuple[float, float]:
    """(F.S., Z) of the handle's pivot: the 1.5 R lobe, 5.2 in forward-to-aft overall, aft end at FS 49.5."""
    return (G.trim_pth_leftmost_fs - 5.2 + 1.5, z_of_wl(G.trim_handle_pivot_wl_in))


def pth() -> cq.Workplane:
    """1/8 plate, 5.2 long: a 1.5 R pivot lobe and a 0.375 R end lobe joined by their common tangents."""
    r1, r2, t = 1.5, 0.375, 0.125
    px, pz = pth_pivot_xz()
    ex = G.trim_pth_leftmost_fs - r2
    d = ex - px
    nx = (r1 - r2) / d
    nz = math.sqrt(1 - nx * nx)
    quad = [
        (px + r1 * nx, pz + r1 * nz),
        (ex + r2 * nx, pz + r2 * nz),
        (ex + r2 * nx, pz - r2 * nz),
        (px + r1 * nx, pz - r1 * nz),
    ]
    y1 = FITTED_PTH_BL + t / 2
    wp = cq.Workplane("XZ", origin=(0, y1, 0))
    body = wp.polyline(quad).close().extrude(t)
    big = wp.center(px, pz).circle(r1).extrude(t)
    small = wp.center(ex, pz).circle(r2).extrude(t)
    return body.union(big).union(small)


def pth_pivot() -> cq.Workplane:
    """Pivot pin through the handle's 1.5 R lobe, standing proud 0.1 each side."""
    px, pz = pth_pivot_xz()
    length = 0.125 + 0.2
    return _cyl(
        FITTED_PTH_PIN_R,
        length,
        cq.Vector(px, FITTED_PTH_BL - length / 2, pz),
        cq.Vector(0, 1, 0),
    )


def pth_springs() -> cq.Workplane:
    """Two PTS springs at their installed length, forward of the panel at the cable sleeve WLs."""
    inst = G.trim_spring_pts_in[1]
    x1 = G.trim_panel_face_fs_in - FITTED_PTS_GAP
    return _compound(
        [
            _cyl(
                FITTED_PTS_R,
                inst,
                cq.Vector(x1 - inst, FITTED_PTH_BL, z_of_wl(wl)),
                cq.Vector(1, 0, 0),
            )
            for wl in G.trim_sleeve_wl_in
        ]
    )


def roll_trim() -> cq.Workplane:
    """Two RT2 tabs clamped on the torque tube with the RT1 lever between them."""
    zc = z_of_wl(_TUBE_WL)
    t = 0.125
    w, h = FITTED_RT_TAB
    tabs = [
        cq.Workplane("XY")
        .box(t, w, h, centered=False)
        .translate((x - t / 2, _TUBE_BL - w / 2, zc))
        for x in (FITTED_RT_X[0], FITTED_RT_X[2])
    ]
    lever = (
        cq.Workplane("XY")
        .box(t, w, FITTED_RT1_H, centered=False)
        .translate((FITTED_RT_X[1] - t / 2, _TUBE_BL - w / 2, zc + _TUBE_OD / 2))
    )
    return _compound(tabs + [lever])


def roll_trim_springs() -> cq.Workplane:
    """Two RTS springs at their installed length, either side of the RT1 lever."""
    inst = G.trim_spring_rts_in[1]
    w = FITTED_RT_TAB[0]
    z = z_of_wl(_TUBE_WL) + FITTED_RTS_Z
    x = FITTED_RT_X[1]
    return _compound(
        [
            _cyl(
                FITTED_RTS_R,
                inst,
                cq.Vector(x, _TUBE_BL + w / 2, z),
                cq.Vector(0, 1, 0),
            ),
            _cyl(
                FITTED_RTS_R,
                inst,
                cq.Vector(x, _TUBE_BL - w / 2, z),
                cq.Vector(0, -1, 0),
            ),
        ]
    )


COMPONENT_PARTS = {
    "controls.consoles": ("front_console", "rear_console"),
    "controls.torque_tube": ("torque_tube",),
    "controls.sticks": ("front_stick", "rear_stick"),
    "controls.pitch_pushrod": ("pitch_pushrod",),
    "controls.rudder_conduit": ("rudder_conduit",),
    "trim.pitch_handle": ("pth", "pth_pivot", "pth_springs"),
    "trim.roll_trim": ("roll_trim", "roll_trim_springs"),
}


def build_controls(
    elevator_deflection_deg: float = 0.0, roll_deg: float = 0.0
) -> dict[str, FusePart]:
    """Controls and trim solids at the given (Roncz-clamped) elevator deflection; neutral by default."""
    rep = "representational"
    stick_parts = {
        f"{w}_stick": stick(w, elevator_deflection_deg, roll_deg)
        for w in ("front", "rear")
    }
    return {
        "front_console": FusePart(
            "front_console",
            front_console(),
            rep,
            (_P97,),
            "30.1 long, 3.5 wide, 9.1 high are printed (medium); an open trough starting 1 in ahead of the pivot plane, position and BL fitted; stick opening and pivot bulkhead not modelled",
        ),
        "rear_console": FusePart(
            "rear_console",
            rear_console(),
            rep,
            (_P97,),
            "25.8 long, 3.1 wide, sides 8.0 tapering to 3.0 are printed (medium); an open trough, position and BL fitted; stick opening not modelled",
        ),
        "torque_tube": FusePart(
            "torque_tube",
            torque_tube(),
            rep,
            (_P98, _P99),
            "3/4 x .058 tube along BL 6.2 R, WL 12.3 from the front pivot plane to the firewall's forward face; the plywood firewall outline is fitted and not cut, so the tube stops at it",
        ),
        **{
            n: FusePart(
                n,
                wp,
                rep,
                (_P98, _P99),
                "stick on the torque tube at its pivot plane (FS 45.5 front, 89.7 rear; medium), 5 deg forward and 5 deg inboard at neutral, pitch from the Roncz travel only; printed stub length, grip fitted",
            )
            for n, wp in stick_parts.items()
        },
        "pitch_pushrod": FusePart(
            "pitch_pushrod",
            pitch_pushrod(elevator_deflection_deg),
            rep,
            (_P99,),
            "CS102 plus CS136 lengths, straight and forward from the stick lever (fitted 5 in); the Roncz arm and the route to the elevator are not printed",
        ),
        "rudder_conduit": FusePart(
            "rudder_conduit",
            rudder_conduits(),
            rep,
            (_P103,),
            "82 in at WL 8 from the firewall, as printed; BL and diameter fitted",
        ),
        "pth": FusePart(
            "pth",
            pth(),
            rep,
            (_P106, _P107),
            "5.2 long 1/8 plate with 1.5 R and 0.375 R lobes; aft end FS 49.5 = panel 40 + 9.5 (the 49.8 label disagrees by 0.3 in and is not used); pivot WL 8.6; side and outline fitted",
        ),
        "pth_pivot": FusePart(
            "pth_pivot",
            pth_pivot(),
            rep,
            (_P106,),
            "pivot pin at WL 8.6; radius fitted",
        ),
        "pth_springs": FusePart(
            "pth_springs",
            pth_springs(),
            rep,
            (_P105,),
            "two PTS springs at the printed installed length 9.0, solid proxies at the cable sleeve WLs; placement fitted",
        ),
        "roll_trim": FusePart(
            "roll_trim",
            roll_trim(),
            rep,
            (_P105, _P107),
            "RT1 and two RT2 on the tube; the book gives patterns and no stations, all placement fitted",
        ),
        "roll_trim_springs": FusePart(
            "roll_trim_springs",
            roll_trim_springs(),
            rep,
            (_P105,),
            "two RTS springs at the printed installed length 3.0, solid proxies; placement fitted",
        ),
    }
