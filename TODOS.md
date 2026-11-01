# TODOS

Near-term open items. The long view (blocks 1 to 7 and what each must prove) is the roadmap:
`docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`. Block 2 work is
planned in `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`.

## When Block 4 (process lane) starts

- **Retire the forge exports.** `data/forge-3dprinting-context.md`, `data/forge-aviation-context.md`,
  `data/forge-bridges.md` and `data/forge_context.py` are personal knowledge-base exports kept as
  context, not sourced references. Fold anything still useful into the process-lane docs with real
  citations, then delete them (and the pointer in `data/knowledge_base_sources.md`).

## Sources to find (Block 1 "still flagged")

Each clears a flag in `docs/block1-report.md` part 3. Book or registered source only; never measure
an undimensioned image.

- **Roncz canard planform.** Span and chord of the Roncz canard as built. Today the model uses the
  GU planform from the owner's manual (conflict flag). P1: it moves the canard AC and the NP.
- **Canard waterline and incidence.** A page that labels the canard LE or chord-line waterline, and
  a printed incidence angle. P2.
- **Fuselage aft end.** A printed aft-end station, which settles `fs_tail` and the fuselage length
  conflict with the manual's overall length. P3.
- **Wing root butt line and strake trailing edge.** Printed stations for `wing_root_bl` and
  `StrakeConfig.fs_trailing_edge`. P3.
- **Reference values.** A printed neutral point, stall speed, range, and airfoil coefficients for
  the R1145MS and Eppler 1230, each registered with a page cite. P2 for the NP.
- **Manual edition.** The date of the owner's manual revision the transcription follows. P3.
- **Spar trough / shear web chordwise position.** The trough templates (page C-3) to replace the
  0.25c placeholder and set `position_verified` true. Neither the owner's set nor cobelu has C-3. P3.

## Checks that fail on purpose

- **Two-method NP.** Analytic vs VSPAERO disagree by more than the 1.0 in bound. The next step is a
  method chosen from a textbook source before it is run, per the ledger. Do not widen the bound.
- **Empty weight.** The Block 2 closure table exists (`data/mass_ledger.yaml` `closure:`, frozen, ledger row 65) and
  its verdict against the target is over the weight cap, so `tests/test_ledger_closure.py::test_empty_closes_on_the_om_sample`
  and `test_om_samples_from_the_ledger_empty` are strict xfail (rows 65 to 68). Target: the OM sample empty airplane,
  730 lb at FS 111.7 (om-1980:p25, p35); the OM also says about 750 lb normally equipped. The open work is what
  moves the closure rows (row 68 lists the unresolved weights), not a missing ledger.
- **CG limits.** Computed from the NP, graded against the LOADED envelope FS 97 to 103 (om-1980:p28).
  They do not wait on the ledger. The empty CG (111.7 in the OM sample) is outside that band by design
  and is never graded against it (ledger row 63).
- **O-235 engine component CG.** The component model (`core/engine_o235_book.py`, layout frozen and hashed in
  ledger row 70) reproduces the TCDS 243 lb by construction, but its CG sits 11.09 in forward of the prop flange against
  TCDS 14.75 (+-0.5) and 0.56 in below the crank line against 1.13 (+-0.3): strict xfail, rows 70 and 71. Do not re-tune
  the layout to pass; a re-tune needs a source, a new row and a new hash. Also strict xfail on the frozen layout: the
  carburettor pokes through the cowl bottom and the throttle bracket hangs below it (row 71).

## Code

- **Fuselage and full-airframe assembly.** The elliptical placeholder was retired in d9b8f53; the fuselage is the
  book box in `core/fuselage_book.py` (chapters 4 to 9, parts tagged `book`, `derived` or `representational`) and
  `scripts/assembly_test.py` no longer carries an xfail. Still open: nothing aft of the firewall is modelled
  (AGENTS.md, Known Issues).
- **Kernel validation.** Block 3 M3.1 and M3.2 landed as `core/kernels/` (laminate, Tsai-Wu, thin-wall), tested
  against registered published data in `tests/kernels/` (ledger rows 73, 75, 78). One recorded miss is strict xfail
  (AS4/8552 [10/80/10] UNT, row 78); glass is not counted as validated by the textbook vectors (rows 78 and 80).
  `core/simulation/fea_adapter.py` (`CompositePly`, `CompositeSection`, `TorsionSection.gj`,
  `analyze_ply_by_ply`) now delegates to those kernels (`tests/test_fea_adapter_kernels.py`); `dbox_failure_checks`
  still computes its own inline Tsai-Wu margin, and `tests/test_dbox_deflection.py` only checks that margin is
  positive, which is not validation (ledger rows 72 and 83). Design: `docs/superpowers/specs/2026-10-07-block3-equivalence-engine-design.md` section 5.
- **Analysis wing and winglet fields (M2.8 update).** `wing_span` 314.0, `wing_root_bl` 23.0 and the
  `winglet_*` analysis fields now carry the book values (ledger rows 60 to 62); `wing_washout` 1.0 still
  matches no page (the book twist is in `wing_book_washout_deg`) and moving it changes the NP.
- **Wing weight, electrical, engine arm (resolved at ledger closure, row 68).** `wing_weight_lb` 132.4 at FS 127.5, canard
  18.5 plus elevators 6.5, electrical split into a nose battery (19 lb at FS 11) and starter (0 lb nominal at FS 150),
  `engine_cg_arm_in` 16.05 aft of the firewall (published FS 141.05) and `engine_displacement_ci` 233.3 now equal the frozen
  closure rows (ledger row 65). Still open: `fuselage_weight_lb` 120 (the closure fuselage is 183 lb with spar and gear),
  the hardcoded propulsion installation weights in `core/systems.py` (mount, exhaust, baffles, cowl, prop), and the
  flutter estimate, which fell to 203 KTAS (240 required) with the 132.4 lb wing mass: two tests are strict xfail,
  Decided 2026-11-01: the all-in wing mass (132.4 lb incl. winglets, rudders, ailerons) belongs in the flutter estimate, because everything attached to the panel moves with it in bending and torsion, and it is the conservative choice. The strict xfails stay (203.2 KTAS estimated vs 240 required; the bound is not widened) (row 68).
- **VSPAERO leg.** Re-run 2026-10-04 on the M2.8 planform (delta +1.63 in, ledger rows 62 and 66). Re-run it again after
  any change to the analysis planform or the strakes; the report reads `not run` when the stored run is stale.

- **O-235 engine module, what stays unsourced** (engine-module proposal section 8). Every engine dimension (length,
  case, cylinder pitch, flange, mount pads), every core component mass (the residual is a modelling choice), the
  firewall-to-pad standoff (Section IIL, not held), which starter and alternator the TCDS weight includes, the
  hub-to-flange offset beyond the 3 in extension, the crank-line WL (`eng_book_block_wl`), the Lycoming left/right
  convention (`FITTED_LYCOMING_LEFT_V_SIGN`), the handbook densities, and the Slick 4251/4250 weight (the registered
  figure is the 4300 series). The CG sensitivity check discriminates thinly: one admissible fitted input moves it by
  more than 0.5 in (row 70). A dependency-consistent sensitivity run is open. The O-200 variant is a later milestone.

## Completed

- Canard planform plans check: done by the 2026-09-29 planform correction; the result is the
  conflict flag above (`docs/geometry-correction-ledger.md`).
- Tests no longer rewrite tracked files: the suite writes to `tmp_path`, and `output/` is untracked.

## Decided 2026-11-01 (OEZ2 intent ledger)

- L028 Shop companion: not built until a real build starts; trigger is the first real part logged.
- L036 Engine model: an output of the Block 6 fit-and-CG trade; book O-235 stays modelled until then; pick the candidate keeping loaded CG in FS 97 to 103 (om-1980:p23) with least ballast, then least installed weight.
- L083 M2.1b Task 9 owner review: non-blocking; milestone stands on its tests; later findings open a new row.
- L091 M2.2 Task 7 owner walk: same as L083.
- L115 Block 3 UI: none until a Block 3 result has all inputs sourced or marked assumptions.
- L118 Block 5 testing route: owner makes panels and specimens; lab with an E4-verified frame runs record tests; university materials facility asked first; no owner frame unless part proof tests need one. Contact and spend stay the owner's action.
- L127 RV-12 and Model 1 spots: stay reserved, no work scheduled.
- L138 STEP/STL export (OE7): entry task of the printed-plug block (step after Block 3).
- L139 OE3 showcase/inspector/URL state: deferred, not scheduled.
- L142 Vortilons, high-performance rudder, later-CP mods: not modelled; plans baseline plus plans changes only.
- L160 Flutter wing mass: all-in 132.4 lb belongs in the estimate; strict xfails stay, bound not widened.
- L167 canard_oswald_e: stays `unsourced`; clears by measurement or a derived value from a registered method.
- L199 Block 5 lab fees: placeholder until the owner contacts the lab (owner's action).
- L200 Block 3 standards: buy the ASTM standards the plan cites first (owner's spend).
- L203 Warp-direction data: no supplier contact; Block 5 coupons are the source; main-wing spar uses a cited textbook glass/epoxy set with wet-layup knockdowns as a design proxy (separate change).
