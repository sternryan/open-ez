# Geometry correction ledger (planform correction, 2026-09-29)

Record of the planform correction: where the canard chord came from (or didn't), every test that
moved when the geometry switched to book values, and the neutral-point gap. Spec:
`docs/superpowers/specs/2026-09-29-planform-correction-design.md`.

## Chord search

Searched the Canard Pusher sections text (CP1–82) and the cobelu plans transcription (all chapters,
incl. ch 30, R1149MS canard) for the Long-EZ canard chord or area. Regexes, case-insensitive:
`canard (chord|area)`, `chord of the canard`, `R114[59]`, `Roncz.*(chord|area|sq)`,
`canard.*sq\.? ?f`, plus follow-ups for spec tables (`Canard Span/Area`, `Canard <number>`) and any
`chord` in cobelu ch 10 / ch 30 / ch 1.

| Hit | Source | Paraphrase (≤10 words) | Usable? |
|---|---|---|---|
| 1 | CP (early newsletter, VariEze prototype specs) | VariEze prototype: canard area 14 sq ft, span 12 ft | No: VariEze, not Long-EZ |
| 2 | CP (VariEze spec table, several issues) | VariEze canard span/area 13.2 ft / 13.7 sq ft | No: VariEze |
| 3 | CP (VariEze brochure, repeated) | VariEze canard span/area 12.5 ft / 13 sq ft | No: VariEze |
| 4 | CP (VariViggen brochure, repeated) | VariViggen canard span/area 8 ft / 18.3 sq ft | No: VariViggen |
| 5 | CP (R1145MS canard articles) | R1145MS canard introduced; no chord or area given | No value |
| 6 | CP (canard span trim article) | Long-EZ canard trimmed from 150 to 142 in span | Span only |
| 7 | cobelu ch 30 Step 18 | outboard jig blocks bonded 126 in apart | Span only (core to BL ±63) |
| 8 | cobelu `I/images/30/C-3.PNG` | templates A–D: labels W.L. 19.8, B.L. 0, B.L. 54.0 | No printed chord dimension |

**Result: no sourced value found.** No CP entry or cobelu line gives the Long-EZ (Roncz R1145MS)
canard chord or area, and template sheet C-3 prints no chord dimension (it was not measured, per the
plan's rule against measuring undimensioned images).

**Decision:** Task 3 uses `canard_chord = 15.25` (the mean of the old 17.0 / 13.5 pair) with status
`unsourced` and an empty source.
