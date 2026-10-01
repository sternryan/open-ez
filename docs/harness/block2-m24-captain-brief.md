# Block 2 milestone 2.4 (chapters 11–13): captain brief

Role, method and gates are as in `docs/harness/block2-m22-captain-brief.md` and
`block2-m23-captain-brief.md` (read both):
- everything you wait on runs in the FOREGROUND, including every crew call and every test run;
- gates: `source ~/.config/long-ez/env && bash scripts/remote_test_all.sh`, plus local
  `.venv/bin/python -m pytest -q -p no:cacheprovider -m local_render`, plus the lab unit/typecheck,
  plus `guide.check`;
- you commit after your own green gate, named files, no trailers of any kind;
- no push, deploy or publish (the lead does those after grading).

The lead approved under the owner's delegation.

**Spec:** `docs/superpowers/specs/2026-10-01-block2-m24-elevators-canard-install-nose-design.md`.
**Evidence:** `docs/harness/m24-ch11-13-research.md`. No separate plan file; decompose spec §4 into
tasks yourself, in this order, each gated and committed:
1. source notes, config values and ledger rows (nose tip, NG31 range, nose-wheel conflict pair,
   static port, Roncz elevator travel, CP26 prototype weights);
2. graph: ch30 elevator and ch12-gap ops, new ch13.yaml;
3. elevator geometry;
4. nose structure and nose-gear geometry;
5. the lab (canard joins the fuselage, elevator travel and hang, gear retraction, striping, cuts,
   readout conflict row);
6. tour and the canard-onto-F22 film.

Write a Review Focus list in your log before Task 1 and pin each item with a test.

## Lanes (token budget is the constraint; follow this, log deviations with the reason)

- **Crew default is Sonnet.** Opus is not used by you; the lead runs one Opus visual review.
- **Op YAML drafts go to the smithy first.** `$LONGEZ_SMITHY_URL` (in the env file) is an
  OpenAI-compatible endpoint; model `local-anvil` (Gemma, 24k context: keep each request under
  ~20k tokens, so draft one chapter or ~8 ops per call). Feed it the op table and materials rows
  from the research, the existing `guide/graph/ch09.yaml` as the shape example, and the rule
  "own words, ten words or fewer per paraphrase". Then run `guide.check` and have one Sonnet crew
  review against the page images. If the lane returns 503, it is leased: retry after a minute,
  up to 10 minutes, then draft with a Sonnet crew and log why.
- **Geometry through `/conduct` where eligible.** Read `~/.claude/skills/conduct/SKILL.md`. For any
  one-file module whose behaviour is fully expressed by tests (e.g. `core/elevators_book.py`,
  the nose-gear point maths, ledger rows), you write the tests and `plan.json`, and
  `smithy-conduct` has local-anvil write the bodies; you review the diff. Lab/visual work and
  multi-file changes stay with a Sonnet crew.
- Have crews write long reports to a file and read the file.

## Specifics

- **Re-read every model-bound value on the page image yourself.** The research is a claim. The
  known traps: hand digits (p77 "2.8", p79 block lengths and orientation, p81 "25.5", p171 FS −6.8
  last digit), and which edge a p83 dimension spans. The Roncz numbers are on cobelu figures
  (`$LONGEZ_COBELU_DIR`), not the scan.
- **Nose-wheel station stays `conflict`.** Never measure the strut rake, NG6 position or fork offset
  off an image. Carry 17 and 20 as a pair.
- **`fs_nose` −45.5 is converted-unsourced against the book tip at FS −6.8.** Moving it will move
  physics tests: each one gets a ledger row in `docs/geometry-correction-ledger.md`, and no
  tolerance is loosened.
- **No regression:** the canard chapters and ch4–9 lab e2e assertions stay unchanged. The canard
  joining the fuselage must not break the canard-only Blender cutaway contract (it writes
  `output/guide/canard/`).
- Public repo: no hostnames, IPs, home paths, scan paths or plans quotes in tracked files;
  leak-check fixtures use 100.64.0.1.
- Log `docs/harness/block2-m24-captain.md`; report `docs/harness/block2-m24-captain-report.md`.
  Your final message is the report's path and a ≤15-line summary.
