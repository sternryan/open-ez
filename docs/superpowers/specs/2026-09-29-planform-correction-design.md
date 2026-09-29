# open-ez planform correction: book-true canard and stations

Status: DRAFT 2026-09-29, design approved in session, written spec awaiting review

## 1. Intent

open-ez's canard and several fuselage stations do not come from the Long-EZ plans. A read-only check
of the 1980 first-edition plans against the Canard Pusher (CP) corrections and cobelu (2026-09-29)
found three problems:

- **The canard is modelled wrongly.** open-ez has it tapered (17 → 13.5 in) and swept 13.5°, with no
  source for any of those numbers. The book's canard is a constant-chord rectangle with zero sweep.
- **The datum offset is fitted.** `datum_offset_in = 45.5` was fitted so the computed neutral point
  (NP) lands on the published ~FS 108.
- **The wing LE is fitted.** `fs_wing_le = 125.61` is labelled "calibrated Phase 5".

So the geometry was tuned to make the physics hit a published answer.

**Goal (Ryan's ruling):**
- The geometry comes from the book, in the book's own station frame.
- The physics is a **check**, not a fit. It reports how far the computed NP lands from the published
  one.
- Values the book does not give stay visibly flagged, never quietly guessed.

**Success:**
- Every planform and station field is either sourced (scan page, CP entry or cobelu line) or flagged,
  and a test enforces it.
- The canard is a zero-sweep constant-chord rectangle.
- The M2 cutaways re-render from it.
- The NP gap is reported.
- Every physics test that moved is accounted for in a ledger.

## 2. Evidence (spike, 2026-09-29)

| Field | Was | Book | Source | Confidence |
|---|---|---|---|---|
| canard sweep | 13.5° | 0° | scan p.71 ("zero sweep, zero dihedral"); p.171 planform | high |
| canard chord | 17 → 13.5 | constant; value not dimensioned in the book | p.54, p.171 rectangles; ch 30 templates A/B at both core ends | high (shape) |
| canard span, GU | 147 | 142 | p.54 callout; the cores sum to 142 | high |
| canard span, Roncz core | 147 | to BL ±63 (jig blocks 126 apart); curled tips not given | cobelu ch 30 line ~304, Fig 30-20 | high (core) |
| shear web end, Roncz | derived | BL ±54 | C-3 template D; ch 30 "full span (108 in)" | high |
| `fs_canard_le` | 36.0 (internal) | FS 18.7 | p.171 (image only, not in the OCR) | medium; Ryan to confirm by eye |
| `fs_wing_le` | 125.61 (fitted) | FS 113.9 at **BL 58** (the strake/wing LE junction) | p.171 prints 113.4; CP25 LPC 7 (MEO) corrects it; the owner's margin note matches | high (value), medium (which BL) |
| nose | FS 0 | FS 0 (RAF CP-29 datum) vs nose tip at FS −6.8 (p.171) | `reference_data.json`; p.171 | conflict |
| canard incidence | −1.5° | not in the book (set by blocks to "zero with the longerons") | p.71, A-13 | unresolved |
| canard LE waterline | 12.0 | not in the book | — | unresolved |

## 3. Design

### 3.1 Frame

- All `fs_*` stations move to the published frame, and `datum_offset_in` becomes 0.
- `to_published_datum()` stays, as an identity function, so callers don't break.
- `reference_data.json`'s `datum_note` is rewritten: code now uses the published frame.

### 3.2 Values

- **Canard sweep:** `canard_sweep_le = 0.0`, status `book`.
- **Canard chord:** a new `canard_chord` field replaces root and tip.
  - Its provisional value is 15.25 (the mean of the old pair), status `unsourced`, until plan task 1's
    search finds a sourced value.
  - `canard_root_chord` and `canard_tip_chord` stay as read-only properties that return
    `canard_chord`.
- **Canard span:** `canard_span = 126.0` (the Roncz structural core to BL ±63), status `book`.
  - The curled tips are recorded as `unsourced / not modelled`.
  - GU 142 is recorded in provenance as reference only; the Roncz canard is mandated.
- **Canard LE station:** `fs_canard_le = 18.7`, status `book`, confidence medium, note "confirm on
  p.171 by eye".
- **Wing LE:**
  - A new `wing_le_anchor = (113.9, 58.0)`, meaning FS at BL, status `cp-corrected`.
  - `fs_wing_le` (the root LE the code uses) is **derived** from the anchor and the existing
    `wing_sweep_le`: FS 113.9 minus (58 − root BL) · tan(sweep). The root BL comes from config.
    Status `derived-unsourced`, because the wing sweep itself is unverified.
- **Nose:** `fs_nose = 0.0`, status `conflict`, with the p.171 tip at −6.8 noted.
- **Other `fs_*`** (seats, firewall, tail, …): the internal value − 45.5, status
  `converted-unsourced`. This keeps their spacing.
- **Incidence and canard LE waterline:** values unchanged, status `unsourced`.

### 3.3 Provenance table

`GEOMETRY_PROVENANCE: dict[str, dict]` in `config/aircraft_config.py`.

- **Entry shape:** field → `{status, source, confidence, note}`.
- **`status`** is one of: `book`, `cp-corrected`, `derived-unsourced`, `converted-unsourced`,
  `unsourced`, `conflict`.
- **Enforcing test:** every planform and station field (`canard_*`, `wing_*` planform, `fs_*`,
  `datum_offset_in`, `canard_le_wl`, `wing_le_anchor`) has an entry with a valid status, and the
  `book`/`cp-corrected` entries have a non-empty `source`.

### 3.4 Physics and tests

- **Run the full suite after the value change.** Classify every failure in
  `docs/geometry-correction-ledger.md`, one row each: test, old expectation, new value, category, why.
  - **(a) Pinned to a retired calibrated number:** update the expectation.
  - **(b) A physics sanity bound:** never loosen it. If book-true geometry fails it, mark it a strict
    `xfail` citing the ledger row and the measured gap.
- **NP check:** the accuracy report gains "NP (book geometry) vs published NP", with the signed gap in
  inches. The existing "NP within ±6 in of published" test is category (b).
- **Phase 5 calibration:** `data/validation/calibration_log.json` Phase 5 is marked `retired` (kept
  for history).
- **Regression locks** (`test_regression_lock.py`, `test_physics_regression.py`, snapshots) are
  re-snapshotted only after the ledger is complete, in their own commit.

### 3.5 Consumers

- **Automatic followers:** `CanardGenerator`, the OpenVSP scripts, the M2 layup geometry and the
  viewer glb all derive from config.
- **The guide:** re-export, run `guide/render_cutaway.sh --wait`, deploy. Update the cutaway's
  "topology only" note. `canard.core` stays `unvalidated` while the chord is `unsourced`.
- **M2 layup tests:** the tests that assume the old planform (for example the semi-span 73.5 in
  `layup.json`) update to 63.0, category (a).

## 4. Order

1. **Chord search** (read-only): CP text and cobelu for the Roncz canard chord or area. It decides
   `unsourced` vs sourced.
2. **Provenance table** and its enforcing test.
3. **Frame switch, value changes** and the `canard_chord` field.
4. **Suite triage** into the ledger; fix category (a); strict-`xfail` category (b).
5. **NP gap** in the accuracy report.
6. **Regression re-snapshot**, its own commit.
7. **Guide:** re-export, re-render, deploy, and a live check.
8. **Grader, leak scan** (open-ez is public), push.

## 5. Out of scope (TODOS.md)

- Verifying the main wing planform (sweep, span, chords are also unchecked).
- The canard tips.
- Canard incidence and waterline (they need the A-sheets).
- A real source for the web/trough chordwise position (existing TODO).
- Ryan's by-eye check of FS 18.7 on p.171 is a follow-up, not a blocker.
