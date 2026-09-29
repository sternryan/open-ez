# TODOS

## Build guide

### Canard planform plans check

**What:** Confirm open-ez's canard span, chord and sweep (147 in, 17 to 13.5 in, 13.5 deg) against the book.

**Why:** ch 30 describes 108 in inboard cores plus separate tips and a 130 in jig surface. Until this is checked, the M2 cutaway is labelled topology-only, not a dimensioned drawing.

**Context:** Logged in the M2 spec (`docs/superpowers/specs/2026-09-29-build-guide-m2-layup-cutaway-design.md` §9). Use the book only: the ch 30 pages and the back-cover 3-view (scan p.171). It is the same kind of job as M1's open wing-LE check (open-ez `fs_wing_le=125.61` vs plans-corrected 113.9, CP25 LPC7).

**Effort:** M
**Priority:** P2
**Depends on:** M2 task 0 (the flat-core fix) landing first.

### Source for the spar trough / shear web chordwise position

**What:** Find the trough templates ("C"/"D", page C-3) and replace the 0.25c placeholder, flipping `position_verified` to true.

**Why:** This is the one geometric unknown the M2 hero section carries as a label.

**Context:** Neither the owner's set nor cobelu has page C-3. cobelu ch 30 places the shear web at the forward edge of the spar trough, and the templates set that edge. Leads are unverified: TERF's RAF CD-ROM, community archives. Check a lead before claiming it exists.

**Effort:** S (once a source exists)
**Priority:** P3
**Depends on:** A source turning up.

## Completed
