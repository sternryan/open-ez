# Main-wing spar cap sizing model

**This is a design-analysis model. It is NOT a certification or airworthiness substantiation.** It has
not been checked against any test, and its lamina strength allowables are unsourced.

Code: `core/spar_sizing.py` (`size_spar_caps`). Report: `python scripts/spar_sizing_report.py [--out f.json]`.
Tests: `tests/test_spar_sizing.py`. It replaces `CompositeFEAAdapter.analyze_spar_cap`, which now
delegates here (the old method bent a 0.153 in plate about its own thickness, saturated at margin
-0.995, fixed the count at 43 plies by a heuristic and charged every station's extra plies over the
full span, 121 lb).

## Scope

One main-wing panel, chapter 19 caps, BL 23 (root rib) to BL 157 (tip rib). The centre-section spar
(chapter 14, `core/spar_kin.py`) and the hard-point load path at the root are not modelled.

## Equations

Load. Ultimate lift per side `L = n_limit * FoS * W * wing_share / 2`, elliptic over BL 0 to `s`
(`s = wing_span / 2 = 157`). With `a = y / s`:

    M_bl(y) = (4 L s / pi) * [ (1 - a^2)^1.5 / 3 - a * (pi/4 - (a sqrt(1 - a^2) + asin a) / 2) ]
    M(y)    = M_bl(y) / cos(web sweep)          (arms along the swept web line)
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

Stress. Plane sections, one cap material: `sigma_x(z) = -M (z - z_na) / I`. Each cap laminate gets the
resultants of that field per unit width, `N = sigma(z_c) n t` and `M_own = -(M / I)(n t)^3 / 12`, and
`core.kernels.laminate.ply_stresses` solves it with free transverse edges (so `sigma_2 = 0` for 0 deg
plies, and the outer-face stress equals `M c / I`). `core.kernels.tsai_wu` gives the strength ratio
`R` at every ply face; the governing `R` is the minimum. **Margin = R - 1** everywhere. Because R
scales inversely with load, the limit margin is `FoS * R - 1`.

Re-solve. Smallest integer `n >= 1`, same for both caps, with `R(n) - 1 >= required margin` at
ultimate. Bisection over `[1, n_max]`, the section rebuilt at every trial `n`; `n_max` is the largest
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

UNSOURCED (flagged in the output `unsourced` list and the inputs table):

- `n_limit` 3.8 and `factor_of_safety` 1.5: no registered source in the repo defines them (14 CFR
  23.337 and 23.303 are not registered). They are the old adapter's numbers, kept as flagged
  assumptions so the change of model is visible on its own.
- `wing_share` 1.0: the wing lifts the whole weight (canard lift ignored; conservative).
- spanload shape: elliptic over BL 0 to the tip; inertia relief ignored (conservative).
- cap lamina properties E1, E2, G12, nu12, F1t 150000, F1c 100000, F2t, F2c, F6: the
  `legacy_uni_glass` set in `data/materials.yaml`, flagged unsourced there. The book UND
  (`und_7715_wet`) has no cured lamina data in the repo.
- density 0.072 lb/in3: the legacy adapter value; the unit is assumed.
- Tsai-Wu `f12*` = -0.5 (legacy).
- required margin 0.0 at ultimate: the repo defines none.
- airfoil shape (sets the depth at the cap), the LE extension inboard of BL 55.5 (sets chord and
  cap x/c there), and the 6 in step carried on to top ply 7: all representational in `core.wing_book`.

## Result (default stations, per wing)

`python scripts/spar_sizing_report.py` prints the full table. Summary:

- Solved count: 3 plies per cap at BL 23 to 31, 2 to BL 64, 1 from BL 72 to the tip. Non-increasing
  outboard.
- Compression in the top cap governs (F1c < F1t) for the symmetric solved section.
- Cap mass, both caps: solved 3.27 lb, book 8.44 lb, extra plies over the book 0.17 lb (all of it at
  the root station).

## Validation against the plans

The repo holds the book base schedule (`wing_cap_top_plies_in`, `wing_cap_bottom_plies_in` and their
offsets, plans-1980:p122, p123), read per station by `core.wing_book.cap_ply_spans`. Station by station:

- Outboard of about BL 31 the book layup has a large margin under this load case (3.7 at BL 55.5,
  9.5 at BL 106.25) and the solved count is far below it (2 or 1 against 7/5 to 2/1).
- At the root rib, BL 23, the staggered ply starts leave the book only 2 top and 1 bottom plies, and
  its margin is -0.45 under this load. The root moment really enters through the hard points and the
  centre-section spar, which this model does not represent, so this is a limit of the model at the
  root end, not a finding against the plans.
- So the model does not reproduce the book schedule. The book is heavier than the strength solve
  outboard. Plausible reasons, none tested here: stiffness, fatigue, damage tolerance, handling, a
  higher design load, a lower real allowable for wet-layup UND than the legacy 100 ksi in compression.
  No input was tuned to close the gap.
- The book adds plies by the CP25 thin-tape box; that is not modelled.

## Limits

No torsion, no shear-web check, no buckling of the compression cap, no skin contribution, no
attachment load path, no fatigue or environmental knock-down, unsourced allowables. Not hardware-
validated. `materials.spar_cap_ply_schedule` (17, 17, 14, 11, 8) and `spar_cap_plies` 17 in config
are unsourced and not used.
