# TODOS

Near-term open items. The long view (blocks 1 to 7 and what each must prove) is the roadmap:
`docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`. Block 2 work is
planned in `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`.

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
- **Empty weight.** Waits on Block 2 ledger closure (per-part mass from geometry and ply schedules).
  Target: the OM sample empty airplane, 730 lb at FS 111.7 (om-1980:p25, p35), with a tolerance set in
  the 2.n spec; the OM also says about 750 lb normally equipped. The ledger sample loadings must land
  inside FS 97 to 103.
- **CG limits.** Computed from the NP, graded against the LOADED envelope FS 97 to 103 (om-1980:p28).
  They do not wait on the ledger. The empty CG (111.7 in the OM sample) is outside that band by design
  and is never graded against it (ledger row 63).

## Code

- **Fuselage and full-airframe assembly.** `core.structures.Fuselage` is an elliptical placeholder
  with unsourced dimensions and no `manufacturing_plan`, so `AircraftAssembly` cannot be built
  (`scripts/assembly_test.py`, strict xfail). Rebuild the fuselage from book stations in Block 2
  rather than patching the placeholder.
- **Kernel validation.** The laminate kernel has been checked against one textbook E-glass case.
  It needs published carbon and glass data before Block 3 relies on it (roadmap section 5).
- **Analysis wing and winglet fields (M2.8 update).** `wing_span` 314.0, `wing_root_bl` 23.0 and the
  `winglet_*` analysis fields now carry the book values (ledger rows 60 to 62); `wing_washout` 1.0 still
  matches no page (the book twist is in `wing_book_washout_deg`) and moving it changes the NP.
- **Wing weight (conflict).** `wing_weight_lb` 85.0 (both wings, unsourced) against 2 x 64 lb = 128 lb
  (CP26 p3, one builder's airplane, with winglets and rudder). Both are named in `WEIGHT_PROVENANCE`; decide at
  ledger closure (2.n).
- **Electrical row shape.** The single 25 lb row at FS 119.5 is wrong: the 25 Ah battery is in the nose
  (about FS 0 to 22, A6 only, about +19 lb over the small battery) and the starter, ring gear and alternator
  are at station 150+ (CP27 p4). Split it at ledger closure.
- **Engine arm and mass flags.** `engine_cg_arm_in` 8.0 ('forward of firewall') contradicts every source
  (the engine is aft of FS 125); `engine_mass_kg` 113 (249.1 lb) disagrees with `engine_dry_weight_lb` 243 and
  both sit near the 246 lb book limit (plans-1980:p156). No engine arm is printed in any held source
  (Sections IIA, IIC and IIL are not held). Fix at ledger closure.
- **VSPAERO leg.** Re-run 2026-10-04 on the M2.8 planform (delta +1.62 in, ledger row 62). Re-run it again after
  any change to the analysis planform or the strakes; the report reads `not run` when the stored run is stale.

## Completed

- Canard planform plans check: done by the 2026-09-29 planform correction; the result is the
  conflict flag above (`docs/geometry-correction-ledger.md`).
- Tests no longer rewrite tracked files: the suite writes to `tmp_path`, and `output/` is untracked.
