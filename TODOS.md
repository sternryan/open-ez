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
- **Empty weight and CG limits.** Wait on Block 2 ledger closure (per-part mass from geometry and
  ply schedules).

## Code

- **Fuselage and full-airframe assembly.** `core.structures.Fuselage` is an elliptical placeholder
  with unsourced dimensions and no `manufacturing_plan`, so `AircraftAssembly` cannot be built
  (`scripts/assembly_test.py`, strict xfail). Rebuild the fuselage from book stations in Block 2
  rather than patching the placeholder.
- **Kernel validation.** The laminate kernel has been checked against one textbook E-glass case.
  It needs published carbon and glass data before Block 3 relies on it (roadmap section 5).

## Completed

- Canard planform plans check: done by the 2026-09-29 planform correction; the result is the
  conflict flag above (`docs/geometry-correction-ledger.md`).
- Tests no longer rewrite tracked files: the suite writes to `tmp_path`, and `output/` is untracked.
