"""Main-wing spar cap sizing: a two-cap beam per spanwise station, ply stresses from core.kernels.

THIS IS A DESIGN-ANALYSIS MODEL. It is NOT a certification or airworthiness substantiation, it has
not been checked against any test, and its strength allowables are unsourced (see below).

What it does, per spanwise station of one wing panel (BL 23 to the tip, chapter 19 caps):

* Load. Ultimate wing lift per side L = n_limit * FoS * W_gross * wing_share / 2, spread as an
  elliptic spanload over BL 0 to the tip (half-span s). Bending moment about the streamwise axis,
  closed form with a = y / s:
      M_bl(y) = (4 L s / pi) * [ (1 - a^2)^1.5 / 3 - a * (pi/4 - (a sqrt(1 - a^2) + asin a) / 2) ]
  Moment arms are taken along the swept web line, so the moment the caps see is
  M(y) = M_bl(y) / cos(web sweep). Torsion and inertia relief are not modelled.
* Section. Two 0-degree UND caps of width w and ply thickness t, outer faces on the airfoil surface
  at the cap's mid-width station (web forward face + w/2), plies stacking INWARD. Surface depth
  h = z_upper - z_lower from core.wing_book (printed chord and t/c, airfoil shape representational).
  Neutral axis at the area centroid (same material both caps); I by parallel axis
      I = sum over caps of [ w (n t)^3 / 12 + w n t (z_c - z_na)^2 ]
  which for equal caps is I = 2 (I_own + A d^2), d = half the centroid separation. The shear web
  and the skins are EXCLUDED (conservative for stress); the skin thickness is not subtracted from h.
* Stress. Plane sections with one cap material: sigma_x(z) = -M (z - z_na) / I. Each cap gets the
  force and moment resultants of that field per unit width, N = sigma(z_c) * n t and
  M_own = -(M / I) (n t)^3 / 12, and core.kernels.laminate.ply_stresses solves the cap laminate
  (free transverse edges). core.kernels.tsai_wu gives the strength ratio R at every ply face;
  margin = R - 1 (the only margin convention used here). Positive M puts the top cap in compression.
* Re-solve. Smallest integer n >= 1 (same n both caps) with margin(n) >= required margin at
  ultimate, by bisection over n with the section rebuilt at each n. The upper bound is the largest n
  for which the two caps do not meet (2 n t < h). No feasible n raises InfeasibleError.
* Mass. Per station: plies * t * w * density * (BL tributary length / cos(web sweep)), summed over
  both caps; the tributary length is the midpoint rule over the station spacing. Never the full span.

Every input is an `Input` row (value, unit, status, citation, note). A row is SOURCED only with a
registered citation (core.sources.check_citation); config geometry rows take their status from
GEOMETRY_PROVENANCE, and a field that must be sourced but is not is rejected. Everything else is
flagged UNSOURCED in the output.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path

import numpy as np
import yaml

from config import config as _default_config
from config.aircraft_config import GEOMETRY_PROVENANCE
from config.provenance_check import SOURCED_STATUSES
from core.kernels import lamina, laminate
from core.kernels.tsai_wu import tsai_wu_strength_ratio
from core.sources import check_citation

SOURCED = "sourced"
UNSOURCED = "UNSOURCED"
MATERIALS_YAML = Path(__file__).resolve().parents[1] / "data" / "materials.yaml"
CAP_MATERIAL = "legacy_uni_glass"  # the only UND set in data/materials.yaml with every property filled
_MAT_KEYS = ("E1", "E2", "G12", "nu12", "F1t", "F1c", "F2t", "F2c", "F6")


class InfeasibleError(ValueError):
    """No ply count up to the geometric limit meets the required margin."""


@dataclass(frozen=True)
class Input:
    """One model input. SOURCED needs a registered citation; UNSOURCED carries none."""

    name: str
    value: object
    unit: str
    status: str
    source: str | None
    note: str = ""

    def __post_init__(self) -> None:
        if self.status not in (SOURCED, UNSOURCED):
            raise ValueError(
                f"{self.name}: status must be {SOURCED!r} or {UNSOURCED!r}"
            )
        if self.status == SOURCED:
            if not self.source or not str(self.source).strip():
                raise ValueError(f"{self.name}: a sourced input needs a citation")
            check_citation(self.source)  # raises on an unknown registry id or bad form
        elif self.source:
            raise ValueError(
                f"{self.name}: an UNSOURCED input may not carry a citation"
            )

    def as_row(self) -> dict:
        v = self.value
        if isinstance(v, tuple):
            v = list(v)
        return {
            "name": self.name,
            "value": v,
            "unit": self.unit,
            "source": self.source if self.status == SOURCED else UNSOURCED,
            "note": self.note,
        }


def geometry_input(
    name: str,
    unit: str,
    cfg=None,
    provenance: Mapping[str, Mapping] | None = None,
    require_sourced: bool = True,
    note: str = "",
) -> Input:
    """A config.geometry field as an Input, status from GEOMETRY_PROVENANCE.

    A field with no provenance entry is rejected; so is a field that must be sourced but whose
    entry is not book, cp-corrected or derived."""
    cfg = cfg or _default_config
    prov = GEOMETRY_PROVENANCE if provenance is None else provenance
    if name not in prov:
        raise ValueError(f"{name}: no provenance entry")
    e = prov[name]
    value = getattr(cfg.geometry, name)
    if e["status"] in SOURCED_STATUSES:
        return Input(name, value, unit, SOURCED, e["source"], note or e.get("note", ""))
    if require_sourced:
        raise ValueError(f"{name}: provenance status {e['status']!r} is not sourced")
    return Input(
        name, value, unit, UNSOURCED, None, f"provenance {e['status']}; {note}"
    )


@dataclass(frozen=True)
class CapMaterial:
    E1: float
    E2: float
    G12: float
    nu12: float
    F1t: float
    F1c: float
    F2t: float
    F2c: float
    F6: float
    f12_star: float


@dataclass(frozen=True)
class Section:
    """Two-cap section; z measured up from mid-depth of the surface depth h."""

    depth_in: float
    width_in: float
    t_ply_in: float
    n_top: int
    n_bot: int
    z_top_c: float
    z_bot_c: float
    z_na: float
    I_in4: float

    @property
    def separation_in(self) -> float:
        return self.z_top_c - self.z_bot_c


def _check_count(n, what: str) -> int:
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise TypeError(f"{what} must be an integer, got {n!r}")
    if n < 1:
        raise ValueError(f"{what} must be >= 1, got {n}")
    return int(n)


def cap_section(
    depth_in: float, width_in: float, t_ply_in: float, n_top: int, n_bot: int
) -> Section:
    """Parallel-axis section of two caps stacked inward from the surfaces. Web excluded."""
    for v, what in (
        (depth_in, "depth"),
        (width_in, "cap width"),
        (t_ply_in, "ply thickness"),
    ):
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"{what} must be positive, got {v!r}")
    n_top = _check_count(n_top, "top ply count")
    n_bot = _check_count(n_bot, "bottom ply count")
    tt, tb = n_top * t_ply_in, n_bot * t_ply_in
    if tt + tb >= depth_in:
        raise ValueError(
            f"caps {tt:.4f} + {tb:.4f} in fill the depth {depth_in:.4f} in"
        )
    z_t = depth_in / 2 - tt / 2
    z_b = -depth_in / 2 + tb / 2
    a_t, a_b = width_in * tt, width_in * tb
    z_na = (a_t * z_t + a_b * z_b) / (a_t + a_b)
    I = (
        width_in * tt**3 / 12
        + a_t * (z_t - z_na) ** 2
        + width_in * tb**3 / 12
        + a_b * (z_b - z_na) ** 2
    )
    return Section(depth_in, width_in, t_ply_in, n_top, n_bot, z_t, z_b, z_na, I)


def _cap_ratio(
    sec: Section, moment: float, mat: CapMaterial, top: bool
) -> tuple[float, float]:
    """(max |sigma_1|, min Tsai-Wu R) over every ply face of one cap, via core.kernels."""
    n = sec.n_top if top else sec.n_bot
    z_c = sec.z_top_c if top else sec.z_bot_c
    t_cap = n * sec.t_ply_in
    k = moment / sec.I_in4
    Nx = -k * (z_c - sec.z_na) * t_cap  # force resultant per unit width
    Mx = -k * t_cap**3 / 12  # moment resultant per unit width about the cap mid-plane
    plies = [lamina.Ply(mat.E1, mat.E2, mat.G12, mat.nu12, sec.t_ply_in, 0.0)] * n
    s_max, r_min = 0.0, math.inf
    for top_s, bot_s in laminate.ply_stresses(
        plies, np.array([Nx, 0.0, 0.0]), np.array([Mx, 0.0, 0.0])
    ):
        for s in (top_s, bot_s):
            s_max = max(s_max, abs(float(s[0])))
            r = tsai_wu_strength_ratio(
                s, mat.F1t, mat.F1c, mat.F2t, mat.F2c, mat.F6, mat.f12_star
            )
            r_min = min(r_min, r)
    return s_max, r_min


def section_response(
    sec: Section, moment: float, mat: CapMaterial
) -> tuple[float, float]:
    """(peak |sigma_1| in psi, governing strength ratio R) of both caps under moment M (in-lbf)."""
    st, rt = _cap_ratio(sec, moment, mat, True)
    sb, rb = _cap_ratio(sec, moment, mat, False)
    return max(st, sb), min(rt, rb)


def margin_from_ratio(R: float) -> float:
    """The margin convention of this module: R - 1."""
    return R - 1.0


def max_plies(depth_in: float, t_ply_in: float) -> int:
    """Largest n with 2 n t < depth (the two caps must not meet)."""
    n = math.floor(depth_in / (2 * t_ply_in))
    while n >= 1 and 2 * n * t_ply_in >= depth_in:
        n -= 1
    return n


def solve_plies(
    moment: float,
    depth_in: float,
    width_in: float,
    t_ply_in: float,
    mat: CapMaterial,
    required_margin: float = 0.0,
) -> int:
    """Smallest n >= 1 (both caps) with margin(n) >= required_margin; bisection, section rebuilt per n."""
    _check_required_margin(required_margin)

    def ok(n: int) -> bool:
        sec = cap_section(depth_in, width_in, t_ply_in, n, n)
        return (
            margin_from_ratio(section_response(sec, moment, mat)[1]) >= required_margin
        )

    hi = max_plies(depth_in, t_ply_in)
    if hi < 1 or not ok(hi):
        raise InfeasibleError(
            f"no ply count up to {hi} meets margin {required_margin} at M = {moment:.0f} in-lbf"
        )
    lo = 1
    if ok(lo):
        return lo
    while hi - lo > 1:  # invariant: ok(hi), not ok(lo)
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def _check_required_margin(m: float) -> None:
    if not (math.isfinite(m) and m > -1.0):
        raise ValueError(
            f"required margin {m!r} is not an R - 1 margin (must be finite and > -1)"
        )


def elliptic_moment(y: float, lift_half: float, semispan: float) -> float:
    """Bending moment at y of an elliptic spanload carrying lift_half over 0..semispan (closed form)."""
    if semispan <= 0:
        raise ValueError("semispan must be positive")
    a = y / semispan
    if not 0.0 <= a <= 1.0:
        raise ValueError(f"y {y} outside 0..{semispan}")
    q = math.sqrt(max(0.0, 1 - a * a))
    bracket = (1 - a * a) ** 1.5 / 3 - a * (math.pi / 4 - (a * q + math.asin(a)) / 2)
    return 4 * lift_half * semispan / math.pi * max(0.0, bracket)


@dataclass
class StationResult:
    y_in: float
    chord_in: float
    cap_depth_in: float
    cap_width_in: float
    moment_limit: float
    moment_ultimate: float
    I_in4: float
    sigma_psi: float
    R: float
    margin: float
    margin_limit: float
    plies_solved: int
    plies_book_top: int
    plies_book_bottom: int
    R_book: float
    margin_book: float
    tributary_bl_in: float
    mass_lb: float
    mass_book_lb: float

    def __post_init__(self) -> None:
        # the margin convention gate: every margin here is R - 1 at its own load level
        for m, r, what in (
            (self.margin, self.R, "margin"),
            (self.margin_book, self.R_book, "margin_book"),
        ):
            if not _same(m, margin_from_ratio(r)):
                raise ValueError(f"{what} {m!r} is not R - 1 for R = {r!r}")
        if self.plies_solved < 1:
            raise ValueError("plies_solved must be >= 1")

    @property
    def plies_book(self) -> tuple[int, int]:
        return (self.plies_book_top, self.plies_book_bottom)

    def as_row(self) -> dict:
        d = {k: _jsonable(v) for k, v in self.__dict__.items()}
        d["plies_book"] = [self.plies_book_top, self.plies_book_bottom]
        return d


def _same(a: float, b: float) -> bool:
    if math.isinf(a) or math.isinf(b):
        return a == b
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def _jsonable(v):
    if isinstance(v, float) and math.isinf(v):
        return "inf"
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


@dataclass
class SparSizingResult:
    stations: list[StationResult]
    inputs: list[Input]
    notes: list[str]
    required_margin: float
    total_mass_solved_lb: float
    total_mass_book_lb: float
    extra_ply_mass_lb: float
    book_schedule_sourced: bool = True
    unsourced: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "disclaimer": "design-analysis model, NOT a certification or airworthiness substantiation",
            "margin_convention": "R - 1 (Tsai-Wu strength ratio minus one)",
            "required_margin_ultimate": self.required_margin,
            "stations": [s.as_row() for s in self.stations],
            "totals_lb_per_wing": {
                "cap_mass_solved": self.total_mass_solved_lb,
                "cap_mass_book": self.total_mass_book_lb,
                "extra_ply_mass_over_book": self.extra_ply_mass_lb,
            },
            "book_schedule_sourced": self.book_schedule_sourced,
            "inputs": [i.as_row() for i in self.inputs],
            "unsourced": self.unsourced,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class Assumptions:
    """Inputs the repo does not source. Each becomes an UNSOURCED row."""

    n_limit: float = 3.8
    factor_of_safety: float = 1.5
    wing_share: float = 1.0
    density_lb_in3: float = 0.072
    f12_star: float = -0.5
    required_margin: float = 0.0

    def rows(self) -> list[Input]:
        return [
            Input(
                "n_limit",
                self.n_limit,
                "g",
                UNSOURCED,
                None,
                "positive limit load factor; no registered source in the repo (14 CFR 23.337 is not registered)",
            ),
            Input(
                "factor_of_safety",
                self.factor_of_safety,
                "1",
                UNSOURCED,
                None,
                "ultimate / limit; 14 CFR 23.303 is not registered",
            ),
            Input(
                "wing_share",
                self.wing_share,
                "1",
                UNSOURCED,
                None,
                "share of the airplane's weight lifted by the wing; 1.0 ignores canard lift (conservative)",
            ),
            Input(
                "spanload_shape",
                "elliptic over BL 0 to tip",
                "-",
                UNSOURCED,
                None,
                "assumed; fuselage and strake carry-through lumped into the elliptic shape",
            ),
            Input(
                "inertia_relief",
                "none",
                "-",
                UNSOURCED,
                None,
                "wing and fuel weight relief ignored (conservative)",
            ),
            Input(
                "density",
                self.density_lb_in3,
                "lb/in3",
                UNSOURCED,
                None,
                "legacy fea_adapter uni-glass density 0.072; data/materials.yaml says unit unstated; lb/in3 assumed",
            ),
            Input(
                "f12_star",
                self.f12_star,
                "1",
                UNSOURCED,
                None,
                "Tsai-Wu interaction term kept from the legacy adapter",
            ),
            Input(
                "required_margin",
                self.required_margin,
                "R-1 at ultimate",
                UNSOURCED,
                None,
                "no repo-defined required margin; 0.0 at ultimate chosen",
            ),
        ]


def load_cap_material(
    name: str = CAP_MATERIAL, f12_star: float = -0.5
) -> tuple[CapMaterial, list[Input]]:
    """Cap lamina properties from data/materials.yaml; each property row keeps its cite or flag."""
    mats = yaml.safe_load(MATERIALS_YAML.read_text())["materials"]
    if name not in mats:
        raise ValueError(f"unknown material {name!r}")
    props = mats[name]["properties"]
    vals, rows = {}, []
    for k in _MAT_KEYS:
        p = props.get(k) or {}
        v = p.get("value")
        if v is None:
            raise ValueError(f"{name}.{k} has no value")
        vals[k] = float(v)
        if p.get("cite"):
            rows.append(
                Input(
                    f"cap_{k}",
                    float(v),
                    p.get("units", ""),
                    SOURCED,
                    p["cite"],
                    p.get("note", ""),
                )
            )
        else:
            rows.append(
                Input(
                    f"cap_{k}",
                    float(v),
                    p.get("units", ""),
                    UNSOURCED,
                    None,
                    f"data/materials.yaml {name}: {p.get('note', 'flagged')}",
                )
            )
    return CapMaterial(f12_star=f12_star, **vals), rows


def default_stations(cfg=None) -> list[float]:
    """Rib stations BL 23, 55.5, 106.25, 157 with each bay split into steps of at most 8.5 in."""
    g = (cfg or _default_config).geometry
    ribs = list(g.wing_book_rib_bl)
    out = [ribs[0]]
    for a, b in pairwise(ribs):
        k = math.ceil((b - a) / 8.5)
        out += [a + (b - a) * i / k for i in range(1, k + 1)]
    return [round(y, 6) for y in out]


def book_plies(y: float) -> tuple[int, int]:
    """(top, bottom) plies of the chapter 19 base schedule covering BL y (core.wing_book.cap_ply_spans)."""
    from core import wing_book as wb

    def count(top: bool) -> int:
        return sum(1 for b0, b1 in wb.cap_ply_spans(top) if b0 - 1e-9 <= y <= b1 + 1e-9)

    return count(True), count(False)


def _tributary(ys: Sequence[float]) -> list[float]:
    n = len(ys)
    if n == 1:
        return [0.0]
    out = []
    for i in range(n):
        lo = ys[i] if i == 0 else 0.5 * (ys[i - 1] + ys[i])
        hi = ys[i] if i == n - 1 else 0.5 * (ys[i] + ys[i + 1])
        out.append(hi - lo)
    return out


def cap_mass_lb(
    plies_total: int, t_ply_in: float, width_in: float, density: float, length_in: float
) -> float:
    """Mass of plies_total strips (summed over both caps) of one station's length. Never the full span."""
    return plies_total * t_ply_in * width_in * density * length_in


def size_spar_caps(
    config=None,
    stations: Sequence[float] | None = None,
    provenance: Mapping[str, Mapping] | None = None,
    assumptions: Assumptions | None = None,
) -> SparSizingResult:
    """Size the main-wing spar caps at each station; see the module docstring for the model."""
    from core import wing_book as wb

    cfg = config or _default_config
    asm = assumptions or Assumptions()
    _check_required_margin(asm.required_margin)
    for v, what in (
        (asm.n_limit, "n_limit"),
        (asm.factor_of_safety, "factor_of_safety"),
        (asm.wing_share, "wing_share"),
        (asm.density_lb_in3, "density"),
    ):
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"{what} must be positive, got {v!r}")

    gi = lambda n, u, **k: geometry_input(n, u, cfg, provenance, **k)
    rows = [
        gi("wing_book_rib_bl", "in BL"),
        gi("wing_span", "in"),
        gi("wing_book_chord", "in"),
        gi("wing_book_le_fs_bl_55_5", "in FS"),
        gi("wing_book_le_fs_tip", "in FS"),
        gi("wing_book_te_fs", "in FS"),
        gi("wing_book_te_fs_bl_23", "in FS"),
        gi(
            "wing_book_thickness_pct",
            "% chord",
            note="held at the BL 55.5 value inboard (not printed there)",
        ),
        gi("wing_book_shear_web_fwd_fs", "in FS"),
        gi("wing_book_shear_web_sweep_deg", "deg"),
        gi("wing_book_spar_cap_width_in", "in"),
        gi(
            "spar_ply_thickness_laid_in",
            "in",
            note="chapter 14 p85 laid UND ply; cobelu:p16 ch19 gives 0.035 to 0.038 for the wing caps",
        ),
        gi("wing_cap_top_plies_in", "in"),
        gi("wing_cap_top_offsets_in", "in"),
        gi("wing_cap_bottom_plies_in", "in"),
        gi("wing_cap_bottom_offsets_in", "in"),
    ]
    gross = cfg.flight_condition.gross_weight_lb
    rows.append(
        Input(
            "gross_weight_lb",
            gross,
            "lb",
            SOURCED,
            "om-1980:p4",
            "normal max takeoff gross (config flight_conditions comment)",
        )
    )
    rows.append(
        Input(
            "airfoil_shape",
            "data/airfoils/eppler_1230_mod.dat",
            "-",
            UNSOURCED,
            None,
            "ordinates not printed; file scaled to the printed t/c (core.wing_book, representational): sets the depth at the cap",
        )
    )
    rows.append(
        Input(
            "le_inboard_of_bl_55_5",
            "22.98 deg extension",
            "-",
            UNSOURCED,
            None,
            "model construct in core.wing_book; the strake owns the real LE; sets chord and cap x/c inboard",
        )
    )
    rows.append(
        Input(
            "cap_top_ply7_offset",
            30.0,
            "in",
            UNSOURCED,
            None,
            "core.wing_book carries the 6 in step on to top ply 7 (representational)",
        )
    )
    mat, mat_rows = load_cap_material(CAP_MATERIAL, asm.f12_star)
    rows += mat_rows
    rows += asm.rows()

    g = cfg.geometry
    root, tip = g.wing_book_rib_bl[0], g.wing_book_rib_bl[-1]
    semispan = g.wing_span / 2
    w = g.wing_book_spar_cap_width_in
    t = g.spar_ply_thickness_laid_in
    cos_web = math.cos(math.radians(g.wing_book_shear_web_sweep_deg))
    lift_half_ult = asm.n_limit * asm.factor_of_safety * gross * asm.wing_share / 2

    ys = sorted(
        float(y) for y in (default_stations(cfg) if stations is None else stations)
    )
    if not ys:
        raise ValueError("no stations")
    for y in ys:
        if not (math.isfinite(y) and root <= y <= tip):
            raise ValueError(f"station BL {y!r} outside the wing panel {root}..{tip}")
    trib = _tributary(ys)

    out = []
    for y, dy in zip(ys, trib):
        chord = wb.chord(y)
        x_cap = wb.web_fs(y) + w / 2
        depth = wb.z_surface(y, x_cap, 1) - wb.z_surface(y, x_cap, -1)
        m_ult = elliptic_moment(y, lift_half_ult, semispan) / cos_web
        m_lim = m_ult / asm.factor_of_safety
        n = solve_plies(m_ult, depth, w, t, mat, asm.required_margin)
        sec = cap_section(depth, w, t, n, n)
        sigma, R = section_response(sec, m_ult, mat)
        nt, nb = book_plies(y)
        if nt >= 1 and nb >= 1:
            R_b = section_response(cap_section(depth, w, t, nt, nb), m_ult, mat)[1]
        else:
            R_b = (
                0.0  # a station with no book cap has no bending strength in this model
            )
        length = dy / cos_web
        out.append(
            StationResult(
                y_in=y,
                chord_in=chord,
                cap_depth_in=depth,
                cap_width_in=w,
                moment_limit=m_lim,
                moment_ultimate=m_ult,
                I_in4=sec.I_in4,
                sigma_psi=sigma,
                R=R,
                margin=margin_from_ratio(R),
                margin_limit=margin_from_ratio(R * asm.factor_of_safety),
                plies_solved=n,
                plies_book_top=nt,
                plies_book_bottom=nb,
                R_book=R_b,
                margin_book=margin_from_ratio(R_b),
                tributary_bl_in=dy,
                mass_lb=cap_mass_lb(2 * n, t, w, asm.density_lb_in3, length),
                mass_book_lb=cap_mass_lb(nt + nb, t, w, asm.density_lb_in3, length),
            )
        )

    extra = sum(
        cap_mass_lb(
            max(0, s.plies_solved - s.plies_book_top)
            + max(0, s.plies_solved - s.plies_book_bottom),
            t,
            w,
            asm.density_lb_in3,
            s.tributary_bl_in / cos_web,
        )
        for s in out
    )
    notes = [
        "Design-analysis model, NOT a certification or airworthiness substantiation.",
        "Margin = R - 1 everywhere (Tsai-Wu strength ratio); infinite R at zero moment is written 'inf'.",
        "Web and skins excluded from the section (conservative); skin thickness not subtracted from the depth.",
        "Caps stack inward from the airfoil surface at the cap mid-width; the depth shrinks by n t per cap.",
        "Solved count is the same n for both caps; the book layup is asymmetric (top 7, bottom 5 at the root) and is evaluated as laid.",
        "Moment arms along the swept web line (1/cos web sweep); torsion and inertia relief not modelled.",
        "Stress allowables are the legacy unsourced uni-glass set: no cured UND lamina data are registered (data/materials.yaml und_7715_wet).",
        "Book schedule is the chapter 19 base schedule; the CP25 thin-tape box adds plies and is not modelled.",
        "Station masses use the midpoint rule over the station spacing; per wing, both caps.",
    ]
    return SparSizingResult(
        stations=out,
        inputs=rows,
        notes=notes,
        required_margin=asm.required_margin,
        total_mass_solved_lb=sum(s.mass_lb for s in out),
        total_mass_book_lb=sum(s.mass_book_lb for s in out),
        extra_ply_mass_lb=extra,
        book_schedule_sourced=True,
        unsourced=[r.name for r in rows if r.status == UNSOURCED],
    )
