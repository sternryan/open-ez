"""Spar-cap lamina design allowables: a cited textbook glass/epoxy set knocked down to wet layup.

No cured lamina data exist for the book's unidirectional tape (docs/harness/block3-source-notes.md, S2
follow-up: a recorded search found none; the Block 5 coupons are the eventual source). Until then the
cap strengths are built from registered sources in three cited steps, each a ratio of measured
values, so the chain can be re-run when a better base set arrives:

1. Base. Mean unidirectional glass/epoxy lamina properties, `glass_epoxy_ud_kaw` in data/materials.yaml
   (kaw-ocw-ch2-engconst:p4, kaw-ocw-ch2-tsaiwu:p12). The slides state neither process nor fibre volume,
   so the base is treated as a well-consolidated laminate, not wet layup.
2. Process. Wet layup against prepreg of the SAME E-glass style 7781, room temperature dry means,
   fibre direction (the fill axis of a woven fabric is a fibre axis): AGATE report 114 wet layup
   (agate-wp33-114:p25) over NCAMP MTM45-1 prepreg (ncamp-7781-mtm45:p34), both as measured.
3. Statistics and environment, on the wet-layup data alone. 14 CFR 23.613(b)(1) asks for A-basis
   (99 percent probability, 95 percent confidence) for a single-load-path member, and the main spar cap
   is one (cfr14-23-613-2011:p1). AGATE 114 prints B-basis only, so A-basis is extrapolated from the
   printed mean and B-basis with the large-sample normal quantile ratio z99 / z90 = 2.326 / 1.282;
   finite samples give a smaller ratio, so this bound is low (conservative). The A-basis values are
   then interpolated to the operating limit temperature by the AGATE wet method (agate-wp33-114:p14,
   p15): estimated room-temperature-wet basis, then a straight line to the elevated-temperature-wet
   point. T_RTD 70 F and T_ETW 180 F are the AGATE test temperatures (agate-wp33-114:p9); the
   operating limit is 140 F, above which room-temperature-cured epoxy softens (plans-1980:p30).
   Extrapolation past the tested range is refused, as AGATE requires.

Design strength = base mean x process ratio x (A-basis at the operating limit, wet / RTD mean).
Moduli are not knocked down (stiffness means are used for stiffness). Shear has no prepreg shear
value at the same definition (NCAMP prints F12 at 5 percent strain), so shear takes the compression
process ratio, the smaller of the two.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from core.materials import get_material

BASE_SET = "glass_epoxy_ud_kaw"

# agate-wp33-114:p25, 7781 / MGS 418 wet layup, 2-axis (fill), as measured, ksi: (mean, B-basis)
AGATE_114 = {
    "tension": {"RTD": (48.99, 41.85), "ETD": (42.21, 36.06), "ETW": (36.34, 31.05)},
    "compression": {
        "RTD": (51.77, 45.11),
        "ETD": (31.45, 27.41),
        "ETW": (29.10, 25.35),
    },
    "shear": {"RTD": (15.45, 14.36), "ETD": (9.41, 8.74), "ETW": (8.26, 7.68)},
}
AGATE_CITE = "agate-wp33-114:p25"
# ncamp-7781-mtm45:p34, MTM45-1 / 7781 prepreg, F2tu and F2cu RTD mean, as measured, ksi
PREPREG_RTD_MEAN = {"tension": 61.58, "compression": 68.96}
PREPREG_CITE = "ncamp-7781-mtm45:p34"
T_RTD_F = 70.0  # agate-wp33-114:p9 (70 +- 10 F)
T_ETW_F = 180.0  # agate-wp33-114:p9 (180 +- 5 F)
T_MOL_F = 140.0  # plans-1980:p30, room-temperature-cured epoxy softens above 140 F
Z99 = (
    2.3263478740408408  # standard normal 0.99 quantile (A-basis population probability)
)
Z90 = (
    1.2815515655446004  # standard normal 0.90 quantile (B-basis population probability)
)

# which knockdown each strength takes: (process ratio kind, statistics/environment kind)
STRENGTH_KINDS = {
    "F1t": ("tension", "tension"),
    "F2t": ("tension", "tension"),
    "F1c": ("compression", "compression"),
    "F2c": ("compression", "compression"),
    "F6": ("compression", "shear"),
}
MODULI = ("E1", "E2", "G12", "nu12")


def a_basis_from_b(mean: float, b_basis: float, ratio: float = Z99 / Z90) -> float:
    """A-basis from a printed mean and B-basis: mean - (z99/z90)(mean - B). Large-sample bound."""
    if not (math.isfinite(mean) and math.isfinite(b_basis) and 0 < b_basis <= mean):
        raise ValueError(f"need 0 < B-basis <= mean, got mean {mean!r}, B {b_basis!r}")
    a = mean - ratio * (mean - b_basis)
    if a <= 0:
        raise ValueError(f"A-basis extrapolates to {a!r} <= 0")
    return a


def mol_wet_value(
    rtd: float,
    etd: float,
    etw: float,
    t_mol: float = T_MOL_F,
    t_rtd: float = T_RTD_F,
    t_etw: float = T_ETW_F,
) -> float:
    """AGATE wet interpolation (agate-wp33-114:p14, p15): B_RTW = B_RTD - (B_ETD - B_ETW), then a line
    from (T_RTW = T_RTD, B_RTW) to (T_ETW, B_ETW) evaluated at T_MOL. No extrapolation."""
    if not (t_rtd < t_mol < t_etw):
        raise ValueError(
            f"operating limit {t_mol} F is outside the tested range {t_rtd}..{t_etw} F; "
            "AGATE forbids extrapolation"
        )
    rtw = rtd - (etd - etw)
    return rtw - (rtw - etw) * (t_rtd - t_mol) / (t_rtd - t_etw)


@dataclass(frozen=True)
class Knockdown:
    kind: str
    process: float  # wet RTD mean / prepreg RTD mean (1.0 where no prepreg pair exists)
    env_stat: float  # A-basis at T_MOL, wet / wet RTD mean
    a_mol_ksi: float

    @property
    def total(self) -> float:
        return self.process * self.env_stat


def process_ratio(kind: str) -> float:
    return AGATE_114[kind]["RTD"][0] / PREPREG_RTD_MEAN[kind]


def env_stat_ratio(kind: str, t_mol: float = T_MOL_F) -> tuple[float, float]:
    d = AGATE_114[kind]
    a = {c: a_basis_from_b(*d[c]) for c in ("RTD", "ETD", "ETW")}
    a_mol = mol_wet_value(a["RTD"], a["ETD"], a["ETW"], t_mol)
    return a_mol / d["RTD"][0], a_mol


def knockdown(prop: str, t_mol: float = T_MOL_F) -> Knockdown:
    if prop not in STRENGTH_KINDS:
        raise ValueError(f"{prop!r} is not a strength ({sorted(STRENGTH_KINDS)})")
    proc_kind, env_kind = STRENGTH_KINDS[prop]
    env, a_mol = env_stat_ratio(env_kind, t_mol)
    return Knockdown(env_kind, process_ratio(proc_kind), env, a_mol)


@dataclass(frozen=True)
class Allowable:
    name: str
    value: float
    unit: str
    base_value: float
    base_cite: str
    knockdown: Knockdown | None

    def note(self) -> str:
        if self.knockdown is None:
            return f"base mean {self.base_value:g} {self.unit}, not knocked down (stiffness)"
        k = self.knockdown
        return (
            f"base mean {self.base_value:.0f} psi x process {k.process:.4f} x A-basis wet at "
            f"{T_MOL_F:g} F / RTD mean {k.env_stat:.4f} ({k.kind}; A_MOL {k.a_mol_ksi:.2f} ksi)"
        )


def design_allowables(t_mol: float = T_MOL_F) -> dict[str, Allowable]:
    """The cap lamina set the spar model uses, every value traced to its cited inputs."""
    props = get_material(BASE_SET)["properties"]
    out: dict[str, Allowable] = {}
    for k in MODULI:
        p = props[k]
        out[k] = Allowable(
            k, float(p["value"]), p["units"], float(p["value"]), p["cite"], None
        )
    for k in STRENGTH_KINDS:
        p = props[k]
        kd = knockdown(k, t_mol)
        base = float(p["value"])
        out[k] = Allowable(k, base * kd.total, p["units"], base, p["cite"], kd)
    return out
