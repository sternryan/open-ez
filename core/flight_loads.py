"""Main-wing limit load case for the spar model: load factors, canard/wing split, spanload shape.

THIS IS A DESIGN-ANALYSIS LOAD CASE, NOT A CERTIFICATION LOADS REPORT.

Category. The plans call the Long-EZ a utility category aircraft (plans-1980:p31); the manual limits
the over-gross band only (1325 to 1420 lb) to normal category (om-1980:p37), so the design gross 1325 lb
(om-1980:p4) is taken at utility category. Part 23 as it stood before amendment 23-64 gives:

* manoeuvre: n = +4.4 utility (cfr14-23-337-2011:p1, (a)(2)); negative 0.4 n (same page, (b)(1));
* gust: 50 ft/s derived gust at V_C (cfr14-23-333-2011:p1, (c)(1)(i)), 25 ft/s at V_D, load factor
  by the 23.341(c) formula (cfr14-23-341-2011:p1); for a canard airplane 23.341(b) asks for a
  rational split of the gust load between the surfaces (below);
* factor of safety 1.5 (cfr14-23-303-2011:p1); ultimate load without failure (cfr14-23-305-2011:p1).

V_C. No design V_C is published. The manual's maximum continuous cruise, 161 kt TRUE at 8000 ft
(om-1980:p58), is used as an EQUIVALENT airspeed at sea level: that over-states the real V_C (EAS is
below TAS at altitude), so the gust load is high. It meets the 23.335(a)(1) floor 33 sqrt(W/S)
(cfr14-23-335-2011:p1). V_D is the largest of 1.25 V_C (23.335(b)(1)), 1.5 V_C,min (utility,
23.335(b)(2)) and the red line 190 kt (om-1980:p23) over 0.9 (cfr14-23-1505-2011:p1).

Split. A steady manoeuvre is trimmed: the total lift n W acts at the CG, so the wing carries
    share_cg = (x_cg - x_ac,canard) / (x_ac,wing - x_ac,canard)
of it. A gust adds lift through angle of attack with the elevator fixed; that increment acts at the
neutral point, so the wing carries
    share_np = a_w S_w (1 - de/da) / (a_w S_w (1 - de/da) + a_c S_c) = (x_np - x_ac,c) / (x_ac,w - x_ac,c)
of the increment. Slopes, areas, aerodynamic centres and downwash are core.analysis's
(PhysicsEngine.lift_surface_terms, the same terms as the neutral point). The analytic and VSPAERO
neutral points disagree (AGENTS.md, Known Issues); the more aft one is used, which loads the wing
more. CG at both loaded limits FS 97 and 103 (om-1980:p23); wing pitching moment, thrust and drag
moments are ignored (the reflexed wing's nose-down moment needs more canard lift, so ignoring it
loads the wing more).

The gust is evaluated at gross weight (largest gust lift, since K_g grows with weight) and, for the
negative case, combined with the 1 g lift of the lightest flight weight (the manual's sample empty
730 lb plus its sample minimum pilot 135 lb, om-1980:p36, zero fuel), which bounds both from the
severe side. Mass ratio uses sea-level density with the area-weighted mean geometric chord of wing
and canard (the smaller chord, so K_g is higher).

Spanload. Schrenk's method (naca-tm-948:p2): the mean of the chord distribution and the ellipse of
equal area, untwisted (the 1 degree washout would unload the tip, so leaving it out loads the root
more). Planform: the gross reference trapezoid BL 0 to tip, as the neutral point uses. Inertia relief
(wing weight) is ignored, which loads the wing more.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from config import config as _default_config
from core.inputs import ASSUMPTION, DERIVED, SOURCED, Input

VSPAERO_NP_JSON = (
    Path(__file__).resolve().parents[1] / "data" / "validation" / "vspaero_np.json"
)

N_UTILITY = 4.4
NEG_FACTOR = 0.4
FACTOR_OF_SAFETY = 1.5
U_DE_VC_FPS = 50.0
U_DE_VD_FPS = 25.0
VC_KEAS = 161.0
V_REDLINE_KIAS = 190.0
CG_LIMITS_FS = (97.0, 103.0)
W_SAMPLE_EMPTY_LB = 730.0
W_SAMPLE_MIN_PILOT_LB = 135.0
RHO_SL_SLUG_FT3 = (
    0.0023769  # ISA sea level (the 23.341 formula's 498 constant assumes it for EAS)
)
G_FT_S2 = 32.174


def gust_load_factor(
    w_over_s_psf: float,
    v_keas: float,
    u_de_fps: float,
    a_per_rad: float,
    mgc_ft: float,
    rho: float = RHO_SL_SLUG_FT3,
) -> tuple[float, float]:
    """(delta n, K_g) by 14 CFR 23.341(c): n = 1 +- K_g U V a / (498 W/S), mu = 2 (W/S) / (rho c a g)."""
    for v, what in (
        (w_over_s_psf, "W/S"),
        (v_keas, "V"),
        (u_de_fps, "U_de"),
        (a_per_rad, "lift slope"),
        (mgc_ft, "chord"),
        (rho, "density"),
    ):
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"{what} must be positive, got {v!r}")
    mu = 2 * w_over_s_psf / (rho * mgc_ft * a_per_rad * G_FT_S2)
    kg = 0.88 * mu / (5.3 + mu)
    return kg * u_de_fps * v_keas * a_per_rad / (498.0 * w_over_s_psf), kg


def schrenk_moment(
    y: float, lift_half: float, semispan: float, c_root: float, c_tip: float
) -> float:
    """Bending moment at y of a Schrenk spanload (naca-tm-948:p2) carrying lift_half over 0..semispan.

    Mean of the elliptic moment and the moment of a load proportional to the linear chord, each
    carrying lift_half. Closed form: with l = s - y and c1 = c(y), the chord part is
    (lift_half / A) (c1 l^2 / 2 + d l^3 / 3), A = s (c_root + c_tip) / 2, d = (c_tip - c_root) / s.
    """
    from core.spar_sizing import elliptic_moment

    if not (c_root > 0 and c_tip > 0):
        raise ValueError("chords must be positive")
    m_e = elliptic_moment(y, lift_half, semispan)
    d = (c_tip - c_root) / semispan
    area = semispan * (c_root + c_tip) / 2
    ll = semispan - y
    c1 = c_root + d * y
    m_c = lift_half / area * (c1 * ll**2 / 2 + d * ll**3 / 3)
    return 0.5 * (m_e + m_c)


@dataclass
class WingLoadCase:
    """Wing lift factors k (wing lift = k x gross weight, both halves) at limit, by case."""

    gross_lb: float
    factor_of_safety: float
    k_pos: float
    k_neg: float
    governing_pos: str
    governing_neg: str
    cases: dict[str, float]
    share_cg: dict[float, float]
    share_np: float
    n_gust_vc: float
    n_gust_vd: float
    v_d_keas: float
    c_root_in: float
    c_tip_in: float
    rows: list[Input] = field(default_factory=list)

    @property
    def neg_over_pos(self) -> float:
        return self.k_neg / self.k_pos


def _vspaero_np() -> float:
    return float(json.loads(VSPAERO_NP_JSON.read_text())["np_fs"])


def wing_load_case(
    cfg=None, engine=None, vspaero_np_fs: float | None = None
) -> WingLoadCase:
    """The governing positive and negative wing lift factors; see the module docstring."""
    from core.analysis import PhysicsEngine

    cfg = cfg or _default_config
    eng = engine or PhysicsEngine()
    t = eng.lift_surface_terms()
    np_analytic = (t.wing_term * t.ac_wing_fs + t.canard_term * t.ac_canard_fs) / (
        t.wing_term + t.canard_term
    )
    np_vlm = _vspaero_np() if vspaero_np_fs is None else vspaero_np_fs
    x_np = max(np_analytic, np_vlm)
    arm = t.ac_wing_fs - t.ac_canard_fs
    if arm <= 0:
        raise ValueError("wing aerodynamic centre must be aft of the canard's")
    share_np = (x_np - t.ac_canard_fs) / arm
    share_cg = {x: (x - t.ac_canard_fs) / arm for x in CG_LIMITS_FS}
    for x, s in share_cg.items():
        if not 0 < s < share_np:
            raise ValueError(
                f"CG FS {x}: wing share {s:.3f} not in (0, share at NP {share_np:.3f}); "
                "a CG at or aft of the neutral point has no stable trim"
            )

    g = cfg.geometry
    gross = cfg.flight_condition.gross_weight_lb
    s_tot = t.s_wing_sqft + t.s_canard_sqft
    w_s = gross / s_tot
    a_air = (t.wing_term + t.canard_term) / s_tot
    mgc_w = t.s_wing_sqft * 144 / g.wing_span / 12
    mgc_c = t.s_canard_sqft * 144 / g.canard_span / 12
    mgc = (t.s_wing_sqft * mgc_w + t.s_canard_sqft * mgc_c) / s_tot
    vc_min = 33 * math.sqrt(w_s)
    if VC_KEAS < vc_min:
        raise ValueError(f"V_C {VC_KEAS} below the 23.335(a)(1) floor {vc_min:.1f}")
    v_d = max(1.25 * VC_KEAS, 1.5 * vc_min, V_REDLINE_KIAS / 0.9)
    dn_c, kg = gust_load_factor(w_s, VC_KEAS, U_DE_VC_FPS, a_air, mgc)
    dn_d, _ = gust_load_factor(w_s, v_d, U_DE_VD_FPS, a_air, mgc)
    dn = max(dn_c, dn_d)
    w_min = W_SAMPLE_EMPTY_LB + W_SAMPLE_MIN_PILOT_LB

    cases: dict[str, float] = {}
    for x, s in share_cg.items():
        cases[f"manoeuvre +{N_UTILITY} g, CG {x:g}"] = N_UTILITY * s
        cases[f"manoeuvre -{NEG_FACTOR * N_UTILITY:g} g, CG {x:g}"] = (
            -NEG_FACTOR * N_UTILITY * s
        )
        cases[f"gust +, gross, CG {x:g}"] = s + dn * share_np
        cases[f"gust -, light 1 g with gross gust, CG {x:g}"] = (
            w_min * s - gross * dn * share_np
        ) / gross
    pos = max(cases, key=cases.__getitem__)
    neg = min(cases, key=cases.__getitem__)

    rows = [
        Input("design_category", "utility", "-", SOURCED, "plans-1980:p31",
              "plans: considered a utility category aircraft; manual limits only the over-gross band to normal",
              ),
        Input("n_limit_manoeuvre", N_UTILITY, "g", SOURCED, "cfr14-23-337-2011:p1",
              "23.337(a)(2) utility; replaces the unsourced 3.8 (the normal-category cap, om-1980:p37 over-gross band)"),
        Input("n_limit_negative_factor", NEG_FACTOR, "1", SOURCED, "cfr14-23-337-2011:p1",
              "23.337(b)(1): negative manoeuvre not less than 0.4 x positive"),
        Input("factor_of_safety", FACTOR_OF_SAFETY, "1", SOURCED, "cfr14-23-303-2011:p1",
              "23.303; 23.305(b) ultimate without failure is the required margin 0 at ultimate"),
        Input("u_de_vc", U_DE_VC_FPS, "ft/s", SOURCED, "cfr14-23-333-2011:p1", "23.333(c)(1)(i)"),
        Input("u_de_vd", U_DE_VD_FPS, "ft/s", SOURCED, "cfr14-23-333-2011:p1", "23.333(c)(1)(ii)"),
        Input("v_c", VC_KEAS, "kt EAS", SOURCED, "om-1980:p58",
              "161 kt TRUE at 8000 ft taken as EAS at sea level: over-states V_C, so the gust is high"),
        Input("v_d", v_d, "kt EAS", DERIVED, "cfr14-23-335-2011:p1",
              "max(1.25 V_C, 1.5 V_C,min, red line / 0.9)", ("cfr14-23-1505-2011:p1", "om-1980:p23")),
        Input("gross_weight_lb", gross, "lb", SOURCED, "om-1980:p4", "normal max takeoff gross"),
        Input("light_flight_weight_lb", w_min, "lb", SOURCED, "om-1980:p36",
              "sample empty 730 plus sample minimum pilot 135, zero fuel (a lower bound)"),
        Input("cg_limits_fs", CG_LIMITS_FS, "in FS", SOURCED, "om-1980:p23", "placard fwd 97.0, aft 103.0"),
        Input("wing_share_trim", {str(k): v for k, v in share_cg.items()}, "1", DERIVED, "cfr14-23-341-2011:p1",
              "share of trimmed lift on the wing at each CG limit; replaces the unsourced 1.0 "
              "(core.analysis lift_surface_terms, which inherits the canard-planform conflict flag)",
              ("om-1980:p23",)),
        Input("wing_share_increment", share_np, "1", DERIVED, "cfr14-23-341-2011:p1",
              f"gust increment at the more aft neutral point FS {x_np:.2f} "
              f"(analytic {np_analytic:.2f}, VSPAERO {np_vlm:.2f}); 23.341(b) rational split"),
        Input("n_gust_vc", 1 + dn_c, "g", DERIVED, "cfr14-23-341-2011:p1",
              f"23.341(c), W/S {w_s:.2f} psf on wing + canard, a {a_air:.3f}/rad, c {mgc:.3f} ft, K_g {kg:.4f}",
              ("cfr14-23-333-2011:p1", "om-1980:p58")),
        Input("spanload_shape", "Schrenk (mean of chord and equal-area ellipse), untwisted", "-",
              DERIVED, "naca-tm-948:p2",
              "replaces the unsourced pure ellipse; gross trapezoid BL 0 to tip; washout ignored (loads the root more)"),
        Input("inertia_relief", "none", "-", ASSUMPTION, None,
              "wing and fuel weight relief ignored: the wing carries more load than it would, never less"),
        Input("wing_lift_factor_pos", cases[pos], "x gross", DERIVED, "cfr14-23-341-2011:p1",
              f"governing positive: {pos}", ("cfr14-23-337-2011:p1",)),
        Input("wing_lift_factor_neg", cases[neg], "x gross", DERIVED, "cfr14-23-341-2011:p1",
              f"governing negative: {neg}", ("cfr14-23-337-2011:p1",)),
    ]  # fmt: skip
    return WingLoadCase(
        gross_lb=gross,
        factor_of_safety=FACTOR_OF_SAFETY,
        k_pos=cases[pos],
        k_neg=cases[neg],
        governing_pos=pos,
        governing_neg=neg,
        cases=cases,
        share_cg=share_cg,
        share_np=share_np,
        n_gust_vc=1 + dn_c,
        n_gust_vd=1 + dn_d,
        v_d_keas=v_d,
        c_root_in=g.wing_centerline_chord,
        c_tip_in=g.wing_tip_chord,
        rows=rows,
    )
