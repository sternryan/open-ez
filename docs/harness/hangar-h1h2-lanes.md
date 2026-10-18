# Hangar H1+H2: what ran where

Date: 2026-10-18. Branch `feat/hangar-h1h2`, plan Tasks 1 to 7 (Task 8, the owner proof run, is not part of this record).
Lanes are named by role; the private per-lane numbers live outside the repo.

## Lanes used

| Role | Used for | Notes |
|---|---|---|
| Deterministic script | scaffolding, the lane fan-out harness (one brief, several lanes at once, tests decide), the source spot-check (HTTP fetch, text extraction, regex), score generation (`python -m hangar.mission --write-scores`) | cheapest and first |
| Local GPU lane (one 24 GB card, served model) | first drafts of the Python bodies for Tasks 1, 2, 3 (data), 5; hardening rounds | three concurrent streams per task, first passing stream kept |
| Local laptop-class lane (small MLX model) | tried on the micro task and T1/T2 | too slow for file-sized output (about 18 tokens/s, backend timeout); not used again |
| Subscription coding agent (Grok, pinned model) | Task 4 (index page and `hangar.json`), the Task 7 state module and page, Task 6 (companion service) | runs in separate worktrees, never graded by itself |
| Hosted lanes (five) | concurrency speed tests only | about $0.10 of a $5 cap; see the private speed-test table |
| Claude Sonnet reviews | one fresh-context review per task | every review found real defects |
| Codex | one batched phase grade of the whole H1+H2 diff | recorded at the end of this file |

## Escalations and what failed

- T1/T2/T5: first-round local output passed 3 to 20 of the task's tests because the briefs left rules implicit. A corrected brief (named rules, exact ledger keys) fixed T1, T2 and T5. After the Sonnet reviews, hardening tests were written first (red), then the local lane was re-briefed with the failing tests and its best attempt as the current file. Three residual defects were fixed by hand after two rounds: the graph directory default in `records.py`, the unknown-arm branch in `mission.py`, and per-position type guards in `council.py`.
- T6 (a 300-line server with 15 tests) was beyond one local shot (1 to 6 of 15 passing); escalated to the subscription coding agent.
- Hosted lanes timed out (the scheduler gives hosted lanes 90 seconds) or spent the whole budget reasoning on file-sized tasks; they were only useful on short outputs.
- Reviewer-found fixes (records: malformed files, hostile values, status/history/option binding; mission: oil, unknown arm, private override that never reaches public records; council: schema in the prompt, env model, per-position validation; index: dissent on a tie, string unknowns, date objects in `hangar.json`) each have a test that was red first.

## Known limits

- The decision gate sees only the file as it is now. A hand edit of `decision.option` is caught because each `to: decided` history entry records the option the owner picked; an edit of both together passes. A git-aware check (compare with the committed version) would close that and belongs in the push gate, not in the validator.
- Published fuel flows for the candidate engines sit at different power points. The mission scores compare them roughly and the record says so under `unknowns`.
- The owner proof run (Task 8) is not done: no decision has been closed in the briefing room.
