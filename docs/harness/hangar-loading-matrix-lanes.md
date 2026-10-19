# Hangar wave 3: loading matrix and research-before-decision

Date: 2026-10-19. Branch `feat/hangar-loading-matrix` from the follow-ups tip. Lanes are named by role; per-lane numbers live outside the repo.

## What was built
- `hangar/matrix.py`, `hangar/matrix_extra.py`: every mass/CG option is scored over a fixed public matrix (solo 120 to 220 lb in 10 lb steps, nine two-up pairs, no baggage or a light bag, full, mission and reserve fuel, at takeoff and landing). Forward CG, aft CG and max gross are all checked. Each option reports its worst cell per limit with the loading that produced it, and the solo pilot weights where a limit starts to bind. The private overlay (`pilots`, optional `bags_lb` in the private mission file) produces the same matrix for the real owners at request time, with labels and no weights, and is never written to a tracked file.
- `hangar/research.py`, `hangar/spotcheck.py`, `hangar/reopen.py` and the briefing service endpoints: unknowns carry an id, the options they affect and a state (`open`, `researching`, `sourced`, `unsourceable`). "Research this" is a briefing-room POST only (no timer): a public-text-only job, a spot-check by plain HTTP fetch and text search (a different method from the research model), then the owner accepts the proposal, which registers the source, patches one value, re-scores and flags decided records whose matrix moved. A decision taken with unknowns open records their ids and the matrix digests; a later change flags the decision for reopen (never edits it).
- The briefing room shows the matrix, the unknowns with their research state, the acknowledgement box and the reopen banner.

## Where tests ran
- Python (`pytest -n 20`, browser files excluded): the 24-core GPU node (lease checked free first), own clone and venv. Final tip: 2175 passed, 5 skipped, 21 xfailed in 6 min 21 s. `tests/hangar` alone: 464 passed.
- TypeScript tests and typecheck: 312 passed, typecheck clean.
- Browser e2e on the Apple-silicon test node (confirmed idle first): a new live end-to-end (`tests/guide/test_briefing_live_e2e.py`) drives the real companion service and a built site in Chromium through matrix, refused decision, research, accept, decision over open unknowns, reopen flag; plus the public read-only briefing test and the hangar index test: 3 passed.

## Lanes
| Role | Used for | Result |
|---|---|---|
| Deterministic script | scores CLI regeneration, fan-out harness, live-test scaffolding | first |
| Local GPU lane (served model, 3 streams per task) | research job module (20/20), spot-check module (43/43), both first try after the brief named every rule | the matrix module looped to the token cap in 4 of 4 rounds (9k, 13k, 12k tokens; an 18k budget hit the 120 s backend limit); escalated |
| Local laptop-class lane, second local node | probe only | timed out at 120 s; one node reported down |
| Subscription coding agent (pinned model, separate worktrees) | matrix modules, server/records side, TypeScript room, three fix rounds, one read-only review | never graded by itself |
| Hosted lanes | planned for concurrency speed tests | refused (the run grant expired the day before; no grant was minted), nothing spent |
| Fresh-context model reviews | four reviews: matrix, server and records, TypeScript, round two on the fixes | found real defects in every round |

## Escalations and what failed
- Matrix module: the local lane produced 100 to 300 lines of looping code each time; the spec was exact, so the fault was task size. Escalated after two failures per the brief.
- Review round one found: an SSRF through redirects and a second DNS lookup, filename collisions between job ids, a double run of one job, a half-written registry on a crash, a YAML alias that let one patch change two entries, a research unknown that could stay `researching` forever, an accept that changed the registry before it could fail, one bad record stopping the reflag of the others, hostile private input (no caps), and a mission value of `None` raising instead of marking cells unknown. Each has a test that was red first.
- Review round two found: a private number glued to a unit passed the leak check; short labels and round-number weights made the check refuse real briefs; a registry in flow style could be corrupted; the cause of an accept failure was not logged. Fixed with tests.
- The live browser run found two defects no unit test saw: the matrix and unknowns were inside a collapsed panel, and the accept path needed the same data root for the patch and the scorers (see limits).

## Known limits
- The gate on deciding counts a cell with unknown inputs and an option that cannot be scored yet (a candidate with no loading effect) as unknown; the owner acknowledges by ticking the box, which records the open unknown ids. The matrix cannot say an unknown value is large, only that it is missing.
- `assert_public` is defense in depth. The brief is built only from the unknown and the affected options' tracked text; an integer-valued private weight cannot be told apart from a public number, so only fractional weights and labels are checked.
- The scorers read `data/hangar/mod-ez`; the service patches `<records root>/<spot>`. Production runs with the repo's records root, where they are the same directory.
- The default research lane needs `HANGAR_RESEARCH_URL` and `HANGAR_RESEARCH_MODEL`; without them "Research this" fails loudly and the unknown returns to `open`.
- The private matrix carries gross weight and CG per cell; it is for the owners' eyes and is sent no-store, never persisted.
- A stale `*.lock` file may appear beside a data file after a crash; they are ignored by git.
