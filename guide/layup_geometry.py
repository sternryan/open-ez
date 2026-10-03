"""CadQuery solids for the layup cutaway, built off CanardGenerator's own planform.

Frame (core fix, Task 1): X chordwise aft, Y = BL (right half, 0..semi-span), Z up.
The planform is linear in BL (linear taper, straight LE sweep, one airfoil), so each ply is an exact
two-section ruled loft between its outline at BL 0 and at its end BL.

    outline(bl) ─surface(side)─► LE→TE polyline ─_band(d0, d1)─► 2D band ─_loft(0 → bl_max)─► ply
    web plane x_w(bl) = le_x(bl) + WEB_XC·chord(bl)   (placeholder: position_verified false)
    foam = core − (web plies ∪ spar caps)

Thicknesses are VISUAL (not to scale): at true scale a 4-ply skin is ~0.04 in on a 17 in chord.
"""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq
import numpy as np

from guide import layup

PLY_T = 0.10  # in, visual
PLY_GAP = 0.03  # in, visual separator between plies
WEB_XC = (
    0.25  # open-ez placeholder; the real trough edge is on template page C-3 (TODOS.md)
)
TROUGH_W = 3.0  # in: the spar cap is 3 in UND tape (cobelu ch 30 Step 22)
TROUGH_D_ROOT = 0.30  # in, visual cap depth at BL 0 ...
TROUGH_D_END = 0.10  # ... tapering to this at the trough end ("uniformly tapered")
CUT_PAD = 0.05  # in: cavity tools overshoot the skin surface so booleans never see coplanar faces
TE_TRIM_XC = 0.97  # skins stop short of the sharp trailing edge so offsets stay simple


@dataclass(frozen=True)
class Planform:
    semi_span: float
    root_chord: float
    tip_chord: float
    sweep_deg: float
    xn: np.ndarray
    zn: np.ndarray

    @classmethod
    def from_generator(cls, gen) -> "Planform":
        x, y = gen.root_airfoil.coordinates
        return cls(
            gen.span / 2, gen.root_chord, gen.tip_chord, float(gen.sweep_angle), x, y
        )

    def chord(self, bl: float) -> float:
        return self.root_chord + (bl / self.semi_span) * (
            self.tip_chord - self.root_chord
        )

    def le_x(self, bl: float) -> float:
        return bl * float(np.tan(np.radians(self.sweep_deg)))

    def outline(self, bl: float) -> np.ndarray:
        c = self.chord(bl)
        return np.column_stack([self.le_x(bl) + self.xn * c, self.zn * c])

    def surface(self, bl: float, side: str) -> np.ndarray:
        o = self.outline(bl)
        # The airfoil file is a closed loop that starts at the LE; split at LE and TE (wrapping).
        # The loop's first and last points are both the LE; take the FIRST of any tie (a bare argmin picks
        # whichever is 1 ULP lower, which differs by platform).
        i_le = int(np.flatnonzero(self.xn <= self.xn.min() + 1e-9)[0])
        i_te = int(np.argmax(self.xn))
        a = o[i_le : i_te + 1]
        b = np.vstack([o[i_te:], o[: i_le + 1]])[::-1]
        top, bottom = (a, b) if a[:, 1].mean() > b[:, 1].mean() else (b, a)
        pts = top if side == "top" else bottom
        keep = np.r_[
            True, np.linalg.norm(np.diff(pts, axis=0), axis=1) > 1e-9
        ]  # closed loop repeats the LE point
        pts = pts[keep]
        xc = (pts[:, 0] - self.le_x(bl)) / self.chord(bl)
        return pts[xc <= TE_TRIM_XC]


def _normals(p: np.ndarray, side: str) -> np.ndarray:
    t = np.gradient(p, axis=0)
    n = np.column_stack([-t[:, 1], t[:, 0]])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    want = 1.0 if side == "top" else -1.0
    return n if (n[:, 1].mean() * want) > 0 else -n


def _band(
    p: np.ndarray, side: str, d0: float, d1: float, le_forward: bool = False
) -> np.ndarray:
    n = _normals(p, side)
    if le_forward:  # skins start at the LE: offset straight forward there so top and bottom meet at the nose
        n[0] = (-1.0, 0.0)
    return np.vstack([p + d0 * n, (p + d1 * n)[::-1]])


def _wire(poly: np.ndarray, bl: float) -> cq.Wire:
    pts = [cq.Vector(float(x), float(bl), float(z)) for x, z in poly]
    return cq.Wire.makePolygon(pts + [pts[0]])


def _loft(poly_at, bl0: float, bl1: float) -> cq.Solid:
    return cq.Solid.makeLoft(
        [_wire(poly_at(bl0), bl0), _wire(poly_at(bl1), bl1)], ruled=True
    )


def _z_at(pf: Planform, bl: float, x: float, side: str) -> float:
    s = pf.surface(bl, side)
    return float(np.interp(x, s[:, 0], s[:, 1]))


def _web_x(pf: Planform, bl: float) -> float:
    return pf.le_x(bl) + WEB_XC * pf.chord(bl)


def _skin_ply(pf: Planform, p: layup.Ply) -> cq.Solid:
    side = "top" if p.component == "canard.skin_top" else "bottom"
    d0 = (p.order - 1) * (PLY_T + PLY_GAP)
    end = p.bl_max if p.bl_max is not None else pf.semi_span
    return _loft(
        lambda bl: _band(pf.surface(bl, side), side, d0, d0 + PLY_T, le_forward=True),
        0.0,
        end,
    )


def _web_ply(pf: Planform, p: layup.Ply, pad: float = 0.0) -> cq.Solid:
    # Plies stack forward from the web plane, ply 1 on the plane.
    def rect(bl: float) -> np.ndarray:
        x1 = _web_x(pf, bl) - (p.order - 1) * (PLY_T + PLY_GAP)
        x0 = x1 - PLY_T
        zb, zt = _z_at(pf, bl, x0, "bottom") - pad, _z_at(pf, bl, x0, "top") + pad
        return np.array([[x0, zb], [x1, zb], [x1, zt], [x0, zt]])

    return _loft(rect, 0.0, p.bl_max)


def _spar_cap(pf: Planform, p: layup.Ply, pad: float = 0.0) -> cq.Solid:
    side = "top" if p.component == "canard.spar_cap_top" else "bottom"

    def region(bl: float) -> np.ndarray:
        depth = TROUGH_D_ROOT + (bl / p.bl_max) * (TROUGH_D_END - TROUGH_D_ROOT)
        s = pf.surface(bl, side)
        x0 = _web_x(pf, bl)
        xs = np.linspace(x0, x0 + TROUGH_W, 24)
        seg = np.column_stack([xs, np.interp(xs, s[:, 0], s[:, 1])])
        return _band(seg, side, -depth, pad)

    return _loft(region, 0.0, p.bl_max)


def build_layup(graph) -> dict:
    from core.structures import CanardGenerator

    gen = CanardGenerator()
    pf = Planform.from_generator(gen)
    out: dict = {}
    cutters = []
    for p in layup.plies(graph):
        if p.op in layup.SPAR_CAP_OPS:
            solid = _spar_cap(pf, p)
            cutters.append(_spar_cap(pf, p, CUT_PAD))
        elif p.component == "canard.shear_web":
            solid = _web_ply(pf, p)
            cutters.append(_web_ply(pf, p, CUT_PAD))
        else:
            solid = _skin_ply(pf, p)
        out.setdefault(p.component, {})[p.node] = solid
    # The generator core is a BSPLINE-faced solid that OCCT's boolean cut mangles (volume grows, fragments);
    # cut a ruled loft of the same planform outlines instead (planform is linear in BL, so it is the same solid).
    base = _loft(
        lambda bl: pf.outline(bl)[:-1], 0.0, pf.semi_span
    )  # outline repeats its first point
    out["canard.core"] = base.cut(*cutters)
    return out
