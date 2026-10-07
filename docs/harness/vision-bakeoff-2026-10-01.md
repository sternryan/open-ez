# Local-vision bake-off (2026-10-01)

**Verdict: local-vision lane does not take first-pass plans research. Research stays on Claude, and
the captain keeps re-reading every model-bound value on the page image.**

## What ran

- Lane: local-model `local-vision lane`, Qwen3-VL-8B-Instruct-4bit on the Mac node (mlx_vlm), temperature 0,
  one request at a time (the node is RAM-bound; swap rose from 7.7 to 8.1 GB over the run).
- Truth: 38 questions, 68 values, from the M2.2 and M2.3 research as corrected by the captain
  reports (`scripts/vision_bakeoff_truth.yaml`).
- Inputs: the 1980 scan page images, pp 33–53 and 171, at the resolution the research used.
- Script: `scripts/vision_bakeoff.py`. Numbers-only results: `data/validation/vision_bakeoff_2026-10-01.json`.
  Raw answers quote plans text, so they stay in the private cache.
- Score per value: exact, near (within 5% or 0.1 in), or wrong.

## Score

| | values | share |
|---|---|---|
| exact | 37 | 54% |
| near | 5 | 7% |
| wrong | 26 | 38% |

18 of 38 questions were fully right. About 16 s per question.

## What it got wrong, and why that decides it

- **Confidently wrong, with a plausible location.** Main strut weight read as 36 lb (truth 22),
  the tip-back angle as 60° (truth 12°), the firewall ply as 48×60 (truth 24×30). Each answer named
  a place on the page. A first pass that is wrong this way costs more to check than to redo.
- **Grabs the nearest number.** Side-layout stations came back as other dimensions on the same
  drawing (59.75 read as 20.5, 96.5 as 9.15, the spar cutout as the sight-gauge section).
- **Same trap as the Sonnet research pass.** It swapped the rear seat bulkhead's 20.6 bottom and
  16.1 slant, the misread the M2.2 captain caught.
- **Good at:** labelled single values (W.L. 23, W.L. 18.9, W.L. −22, FS 17, FS 125.5/15/110.5) and
  short stock lists (longeron, step, LMGA tube).

The bar for a first-pass researcher is that a verifier can trust what agrees and only re-read what
is flagged. At 54% exact with unflagged errors, every value would need a full re-read, so the lane
saves nothing and seeds wrong numbers.

## Lane mix for M2.4 onward

| Step | Lane |
|---|---|
| Research | Sonnet, page images; captain re-reads every model-bound value |
| Spec | session |
| Op YAML drafts | local-model lane (text from the research notes), `guide.check`, one Sonnet review |
| Geometry | `/conduct` (local-model lane writes bodies) |
| Captain | Sonnet; one Opus visual review per milestone |

Re-test local-vision lane when the model or the page resolution changes (a 300 dpi crop around the
asked-for view is the obvious next try).
