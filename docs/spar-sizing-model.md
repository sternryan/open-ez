# Main-wing spar cap sizing model

**This is a design-analysis model. It is NOT a certification or airworthiness substantiation.** It has
not been checked against any test. Its cap strengths are a cited textbook set knocked down to wet
layup, not coupon data for the book's tape.

Code: `core/spar_sizing.py` (`size_spar_caps`), load case `core/flight_loads.py`, allowables
`core/cap_allowables.py`. Report: `python scripts/spar_sizing_report.py [--out f.json]`.
Tests: `tests/test_spar_sizing.py`, `tests/test_flight_loads.py`, `tests/test_cap_allowables.py`.
It replaces `CompositeFEAAdapter.analyze_spar_cap`, which now delegates here.

## Scope

One main-wing panel, chapter 19 caps, BL 23 (root rib) to BL 157 (tip rib). The centre-section spar
(chapter 14, `core/spar_kin.py`) and the hard-point load path at the root are not modelled.

## Equations

Load (`core/flight_loads.py`). Wing lift = k x W at limit, both halves, for the governing positive
and negative k over these cases, each at both CG limits FS 97 and 103 (om-1980:p23):

- manoeuvre +4.4 g, utility category (cfr14-23-337-2011:p1; the plans call the Long-EZ utility,
  plans-1980:p31; the manual's normal-category +3.8 applies only to the over-gross band, om-1980:p37),
  and -0.4 x 4.4;
- gust 50 ft/s at V_C by the 23.341(c) formula (cfr14-23-333-2011:p1, cfr14-23-341-2011:p1), V_C = the
  manual's 161 kt true at 8000 ft taken as EAS at sea level (om-1980:p58; over-states V_C), and 25 ft/s
  at V_D = max(1.25 V_C, 1.5 V_C,min, 190 / 0.9) = 211 kt; the negative gust is combined with the 1 g
  lift of the lightest flight weight (865 lb, om-1980:p36).

Canard/wing split (23.341(b) asks for a rational one): trimmed lift acts at the CG, so the wing
carries `(x_cg - x_ac,c) / (x_ac,w - x_ac,c)`; the gust increment acts at the neutral point, so the wing
carries `(x_np - x_ac,c) / (x_ac,w - x_ac,c)`, with the more aft of the analytic and VSPAERO neutral
points. Slopes, areas, centres and downwash are `PhysicsEngine.lift_surface_terms`, the terms behind
the neutral point. `L = k * FoS * W / 2` per side, FoS 1.5 (cfr14-23-303-2011:p1).

Spanload: Schrenk (naca-tm-948:p2), the mean of the elliptic and the chord-proportional load on the
gross trapezoid, BL 0 to the tip, untwisted:

    M_bl(y) = 0.5 * ( M_ellipse(y) + (L / A) (c(y) l^2 / 2 + d l^3 / 3) ),   l = s - y, d = (c_t - c_0) / s
    M(y)    = M_bl(y) / cos(web sweep)          (arms along the swept web line)
    M_neg   = M * k_neg / k_pos
    M_limit = M / FoS

Section. Cap mid-width at `x = web forward face + w / 2`; surface depth `h = z_upper - z_lower` from
`core.wing_book.z_surface` (printed chord and t/c, representational airfoil shape). Caps stack inward
from the surfaces, so with `n_top`, `n_bot` plies of thickness `t`:

    z_top = h/2 - n_top t / 2,   z_bot = -h/2 + n_bot t / 2
    z_na  = (A_top z_top + A_bot z_bot) / (A_top + A_bot),   A = w n t
    I     = sum over caps of [ w (n t)^3 / 12 + A (z_c - z_na)^2 ]

For equal caps this is `I = 2 (I_own + A d^2)` with `d` half the centroid separation. The shear web
and the skins are excluded (conservative for stress); the skin thickness is not taken off `h`
(slightly unconservative).

Stress. Both signs at every station (the negative case puts the bottom cap in compression). Plane sections, one cap material: `sigma_x(z) = -M (z - z_na) / I`. Each cap laminate gets the
resultants of that field per unit width, `N = sigma(z_c) n t` and `M_own = -(M / I)(n t)^3 / 12`, and
`core.kernels.laminate.ply_stresses` solves it with free transverse edges (so `sigma_2 = 0` for 0 deg
plies, and the outer-face stress equals `M c / I`). `core.kernels.tsai_wu` gives the strength ratio
`R` at every ply face; the governing `R` is the minimum. **Margin = R - 1** everywhere. Because R
scales inversely with load, the limit margin is `FoS * R - 1`.

Re-solve. Smallest integer `n >= 1`, same for both caps, with `R(n) - 1 >= 0` at ultimate in both
cases (23.305(b), cfr14-23-305-2011:p1). Bisection over `[1, n_max]`, the section rebuilt at every trial `n`; `n_max` is the largest
`n` with `2 n t < h`. No feasible `n` raises `InfeasibleError`. Margin rises strictly with `n` because
`I = w [h^3 - (h - 2 n t)^3] / 12` grows with `n` at a fixed outer-fibre distance.

Mass. Per station: `plies (both caps) * t * w * density * (tributary BL / cos(web sweep))`, the
tributary length being the midpoint rule over the station spacing (the tributaries sum to the panel
once). Extra-ply mass counts `max(0, n - n_book)` per cap per station.

## Inputs

Sourced (status from `GEOMETRY_PROVENANCE`, checked against `data/sources/registry.yaml`):

| Input | Value | Source |
|---|---|---|
| rib stations | BL 23, 55.5, 106.25, 157 | plans-1980:p126, p127 |
| wing span (tip BL x 2) | 314 in | plans-1980:p126 (derived) |
| chords, LE and TE stations | 42.7, 31.35, 20.0; FS lines | plans-1980:p126 |
| thickness | 16.2, 15.7, 15.0 % | plans-1980:p126 (16.2 medium) |
| shear web forward face, sweep | FS 125.6 to 164.2; 18.42 deg | plans-1980:p126 |
| cap width | 3.0 in | plans-1980:p126, p122 |
| ply thickness, as laid | 0.0375 in | plans-1980:p85 (chapter 14 text; cobelu:p16 ch19 gives 0.035 to 0.038) |
| cap ply lengths and offsets | top 7, bottom 5 plies | plans-1980:p122, p123 |
| gross weight | 1325 lb | om-1980:p4 |

Load case (cited; full rows in the report's `inputs`):

| Input | Value | Source | Replaced |
|---|---|---|---|
| design category | utility | plans-1980:p31 | (none) |
| n limit, manoeuvre | +4.4, negative 0.4 x | cfr14-23-337-2011:p1 | 3.8 unsourced |
| factor of safety | 1.5 | cfr14-23-303-2011:p1 | 1.5 unsourced |
| gust | 50 ft/s at V_C, 25 at V_D; 23.341(c) | cfr14-23-333-2011:p1, cfr14-23-341-2011:p1 | none (no gust case) |
| V_C | 161 kt (true at 8000 ft, used as EAS) | om-1980:p58 | (none) |
| CG limits | FS 97, 103 | om-1980:p23 | (none) |
| wing share, trimmed | 0.711 (FS 97), 0.768 (FS 103) | derived, core.flight_loads | wing share 1.0 unsourced |
| wing share, gust increment | 0.857 (NP FS 112.42, VSPAERO) | derived | (none) |
| governing wing lift factor | +4.058 (gust, FS 103), -2.826 (negative gust, FS 97, light weight) | derived | +3.8 |
| spanload | Schrenk | naca-tm-948:p2 | elliptic unsourced |
| required margin | 0 at ultimate | cfr14-23-305-2011:p1 | 0 unsourced |
| Tsai-Wu f12* | -0.5 (Mises-Hencky) | kaw-ocw-ch2-tsaiwu:p10 | -0.5 unsourced (no effect: sigma_2 = 0) |

Cap allowables (`core/cap_allowables.py`): base = mean unidirectional glass/epoxy lamina, Kaw Table
2.1 (`glass_epoxy_ud_kaw`: E1 38.6 GPa, E2 8.27, G12 4.14, nu12 0.26, kaw-ocw-ch2-engconst:p4; F1t 1062
MPa, F1c 610, F2t 31, F2c 118, F6 72, kaw-ocw-ch2-tsaiwu:p12). Strength = base x process x environment:

- process: 7781 E-glass wet layup over the same fabric in prepreg, RTD means as measured, tension
  48.99 / 61.58 = 0.796, compression 51.77 / 68.96 = 0.751 (agate-wp33-114:p25, ncamp-7781-mtm45:p34);
- statistics and environment: A-basis (23.613(b)(1), single load path, cfr14-23-613-2011:p1) estimated
  from the AGATE mean and B-basis with z99 / z90, interpolated wet to the 140 F operating limit
  (plans-1980:p30) by the AGATE method (agate-wp33-114:p14, p15, test temperatures p9), over the
  RTD mean: tension 0.583, compression 0.540, shear 0.591.

Result: F1t 71.4 ksi, F1c 35.9 ksi, F2t 2.08, F2c 6.94, F6 4.63 ksi (legacy unsourced: 150, 100, and
the rest). Moduli are the base means.

ASSUMPTION (no source; the conservative choice, stated in the output `assumptions` list):

- inertia relief none: wing and fuel weight never unload the wing in this model.
- density 0.072 lb/in3, mass only: heavier than rule-of-mixtures glass/epoxy at 45 % fibre (0.065).

UNSOURCED (output `unsourced` list): the airfoil shape (sets the depth at the cap), the LE extension
inboard of BL 55.5 (sets chord and cap x/c there), and the 6 in step carried on to top ply 7, all
representational in `core.wing_book`, settled only by the full-size sheets.

## Result (default stations, per wing)

`python scripts/spar_sizing_report.py` prints the full table. Selected stations (ultimate moments in
in-lbf; margin R - 1 of the book layup as laid):

| BL | M_ult + | M_ult - | solved n | book top/bottom | book margin |
|---|---|---|---|---|---|
| 23.0 | 194339 | -135329 | 9 | 2/1 | -0.82 |
| 31.1 | 167699 | -116778 | 8 | 3/2 | -0.59 |
| 39.2 | 143319 | -99801 | 7 | 4/3 | -0.34 |
| 47.4 | 121144 | -84359 | 6 | 6/4 | 0.12 |
| 55.5 | 101112 | -70410 | 5 | 7/5 | 0.57 |
| 72.4 | 66002 | -45961 | 4 | 6/4 | 0.83 |
| 106.2 | 20221 | -14081 | 2 | 4/3 | 2.21 |
| 157.0 | 0 | -0 | 1 | 2/1 | inf |

- Solved count falls from 9 plies per cap at the root rib to 1 outboard of about BL 114.
- Cap mass, both caps: solved 7.64 lb, book 8.44 lb, extra plies over the book 1.91 lb (all inboard of BL 47).
- Against the previous unsourced case (3.8 g x wing share 1.0, elliptic, F1c 100 ksi): the root
  moment rose 6.7 % (182 189 to 194 339 in-lbf) and the compression allowable fell 64 %, so the book
  margin at BL 55.5 went from 3.73 to 0.57 and at the root rib from -0.45 to -0.82.

## Validation against the plans

- The solved mass now lands within 10 % of the book's (7.64 against 8.44 lb); the old model's 3.27 lb
  was 39 % of it. Outboard of about BL 47 the book layup has a positive margin under this load case,
  and its margin is smallest (0.12 to 0.83) between BL 47 and BL 72, where the book drops plies.
- Inboard of about BL 45 the book layup shows negative margins (-0.82 at BL 23). The staggered ply
  starts leave the root rib with 2 top and 1 bottom plies; the real root moment enters through the
  hard points, the centre-section spar and the CP25 thin-tape box, none modelled here. A Long-EZ
  six-g static test reported only about half the allowable stresses reached (cp-text:p25), so
  the structure as built is stronger than this model's inboard end; it is a limit of the model, not
  a finding against the plans.
- No input was tuned to close any gap.

## Limits

No torsion, no shear-web check, no buckling of the compression cap, no skin contribution, no
attachment load path, no winglet side-load moment, no fatigue; allowables are a textbook set with
measured wet-layup ratios, not coupon data (the Block 5 coupons replace them). Not hardware-
validated. `materials.spar_cap_ply_schedule` (17, 17, 14, 11, 8) and `spar_cap_plies` 17 in config
are unsourced and not used.
