# Rehearsal player: phase 2 gate record

Date: 2026-10-20. Branch `feat/rehearsal-p2c`, on top of phase 1's final tree (`feat/rehearsal-p1-final`, itself rebased on
`origin/main` `8b30b1e`). Gate tree `eb5fc99`; after grade call 1, `e5f8849`. Host names are omitted (public repo).

## Scope

Phase 2 of `docs/superpowers/plans/2026-10-17-build-rehearsal-player.md`: build groups for the whole airplane, sourced
plan values for every remaining step, step-script overrides, net quantities (contract 18), whole-build zoom and local owner
actuals (P2-C, contract 20a).

Owner-approved additions beyond the plan text:

- **Builder pace** (approved 2026-10-18). Raw logged hours stay in the data. A lab setting next to the shop climate scales
  known estimated hours: "As logged" (default), "x0.653" (derived: the ratio of two builders' logs on the sections both
  recorded, `rehearsal-sourcing-p2.md`, Pace caveat), or a custom value from 0.25 to 3. Scaled figures carry a
  `pace-scaled` label. Unknown hours stay unknown and owner actuals are never scaled.
- **Tank resin** (decided 2026-10-20). MGS 285/287 stays the one resin, including the four fuel-wetted steps. The
  placeholder resin is deleted. No published UL94 immersion clears or rules out MGS
  (`docs/research/2026-10-20-ul94-tank-resin.md`), so those steps carry a validated `plan.fuel` flag
  (`resin_compat: unknown`, no source) and the bench shows "UL94 compatibility of this resin is unknown (coupon test
  pending)". The coupon test is a separate change to the Block 5 plan.
- **Adaptive resolution** (owner report, see Device evidence). Resolution could only step down, to a floor of 0.08 of the
  pixel count. Step changes now open a settle window that does not count toward a step-down, resolution recovers after a
  sustained fast window, and the floor is 0.2.
- **Camera on caption-only plies** (owner report). A ply with no drawn geometry now frames the step's drawn parts, or the
  group's assembly, at no less than 1.4 m, instead of a close-up of the nearest label.

## Tests (tree `e5f8849`, after grade call 1; `eb5fc99` before it had the same results apart from the counts noted)

| Suite | Result |
|---|---|
| Python, all files except the browser files | 2328 passed, 5 skipped, 21 xfailed (2312 at `eb5fc99`) |
| `guide.check --schema-only` | OK |
| Lab `npm test` / typecheck / build | pass 408 fail 0 / clean / built |
| Viewer node tests | 50 passed |
| Browser suites (lab, viewer, actuals, pace), chromium + webkit, 8 workers | 478 passed |
| Frame-time tests, serially | 4 passed |
| Context-restore test, serially (it timed out once under 8 workers on an earlier tree) | 2 passed |
| `pre-commit` on the phase's files (vs `8b30b1e`): ruff, ruff-format, mypy, geometry smoke | passed |

Phase 1 player tests that pinned the first stretch's end (`f05.gear-extrusions`) now take the last grouped step from the
graph (`f26.suitcases` today), and still require `f05.gear-extrusions` earlier in the sequence (plan P2-A). The GU-note
test opens the first step of the `canard` group, which phase 2 moved to `r30.templates-cores` (contract 9). One phase 1
test asserted "no buy is official"; it now holds an explicit, empty allowlist of official buys, and fails on any unread
official buy.

## Broken-input proof

Each new test was red before its change.

- Ply order: an early `place`, `drape` or `squeegee`, a backwards ply reference, and the grader's reproduction (prepend
  `place ply 2` to the two-ply front-seat script) each fail `guide.check` (7 red against the old validator).
- Script tools: a hot-wire on a step that does not list it fails `guide.check`.
- Official buys: adding an unread `official` buy to `f13.pitot-static` fails `test_sourced_buys_match_the_sourcing_record`.
- `plan.fuel`: `sourced` with no source, `unknown` with a source, an unknown key and a bad value each fail `guide.check`;
  the placeholder resin reference fails `test_fuel_compat.py` (6 red).
- Actuals (7 red), builder pace (7 red), the fuel line on the bench (1 red), adaptive resolution and caption framing (red
  on missing exports only, a weaker proof; the owner check below is the stronger one).

## Device evidence

- Owner, desktop Chrome and iPad Pro M5, tree `81eb937`: "very cool"; two nits on both devices: the camera did not track
  some parts (screenshot: session 15, main gear attach pad, ply 4 of 21, caption only, a close-up of the right side label),
  and the picture became pixelated late in the demo. Both are fixed above (`4eb8020`, `4ceef2f`).
- Owner re-check, iPad Pro M5, served build of `ab61b7f` (formatting-only difference from the gate tree): "some minor issues
  but all still really good". Accepted, with two open follow-ups seen in the owner's screenshots:
  - Pixelation is reduced but not gone late in the build at 16x (session 163, winglet "Block A and outside layups 3 and 4").
  - The camera frames the wrong area on some steps whose parts are elsewhere or not drawn: session 82 "Top elevator skin"
    shows the empty layup table, and session 163 shows the shop shelf and fuselage labels instead of the winglet.
- Headless chromium at 1440x900 and iPad/phone emulation (820x1180, 390x844), served build of `ab61b7f`: no page errors;
  the fuel line shows on `f21.close-tank`, the GU note on `r30.templates-cores`, `pace-scaled` at x0.653.

## Grade, call 1 of 2 (FAIL) and fixes

Astra call 1 failed the phase with seven must-fix findings. Each fix's test failed on an assertion first.

| Finding | Fix |
|---|---|
| 1. Unread hours shown as official (`f24.canard-cover`) | downgraded to estimate; every official, derived and community hour was checked (it was the only one); the sourcing test now covers hours (`e3b2c49`) |
| 2. A receipt on a step with no buys never counted | receipts count once by group membership, replacing only that step's own estimate (`bda6464`) |
| 3. Whole-build rollups printed raw `derived` flags | rollups use the bench's evidence policy (`3cdb673`) |
| 4. The quantity gate accepted null or unsourced conversion inputs | thickness and width must be finite, positive and sourced (`bfb15e3`) |
| 5. Resolution recovery reset on every step change | recovery credit survives step changes; only the settle window is excluded (`32dbac5`) |
| 6. Negative actuals accepted | rejected at entry and at load and save; zero stays valid (`2a4912c`) |
| 7. Collapsed whole-build rows were not compact | one row of counts and one cure marker per collapsed group (`057bb6d`) |

Follow-ups from the grade, open: the elevator and winglet camera framing (owner-accepted), and a measured iPad frame rate. The lab has
no frame-rate overlay, so the device check is visual only; a measured number needs one.

## Grade, call 2 of 2: PASS

Astra call 2 re-graded the tree after the fixes: all seven call-1 findings FIXED (each fix re-reproduced, and each regression
mutation fails its test). No must-fix findings. Follow-ups, open:

- `guide/quantities.py`: an input flagged `page` with an empty source still qualifies for derivation. No shipped quantity
  takes that path today (the thicknesses are unsourced). Require non-blank evidence, with a regression test, before any
  derived buy relies on it.
- `guide/lab/src/ui/navlog.ts`: once elapsed hours become a number, pace-scaled shop time would show without its
  `pace-scaled` label. Unknown cure gates mask it today. Label it, and test a known-cure sequence.
- Camera framing on the elevator and winglet steps, and a measured iPad frame rate (owner-accepted, above).

## Sourcing changes in this phase

- Five buys recorded as `official` had plans pages that were never read: `f13.pitot-static` 5052 tube, `f13.nose-door`
  screws and nutplates, `f21.cut-parts` foam sheets, `f22.battery-shelf` battery. All five are `estimate` now, quantities
  unchanged, and the sourcing record says so with the date.
- 69 step-script overrides were changed to meet phase 1's tool and ply-order rules (stand-ins labelled, one ply number
  removed from a peel-ply drape on `f19.top-skin`).

## Lanes

| Work | Lane | Result |
|---|---|---|
| Rebases, script audit, P2-C tests and body, builder pace, fuel flag, test triage, nits | Cursor `grok-4.7-high` | every task landed on the first call; no escalation |
| Tank-resin and coupon-method research | Cursor `grok-4.7-high`, public web | two notes; lead spot-checked the cited sheets |
| Full suites and browser runs | a separate test machine | one machine at a time |
| Hosted lanes | not used | the run grant is approved; the hosted lanes wait on a timeout fix |
