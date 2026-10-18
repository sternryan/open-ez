# Hangar H1+H2: what ran where

Date: 2026-10-18. Branch `feat/hangar-h1h2`, plan Tasks 1 to 7 (Task 8, the owner proof run, is not part of this record).
Lanes are named by role; the private per-lane numbers live outside the repo.

## Where tests ran

- Authoring and git: the shared authoring host. Batched Python suite (`pytest -n 20`, browser files excluded): the 24-core GPU node (GPU lease checked free first), in its own clone and venv built from the dev requirements, then the pinned CAD packages matched to the authoring host. 1846 passed, 5 skipped, 21 xfailed in 8 min 16 s; the same suite on the 8-core authoring host took 9 min 25 s, so the gain is small because a few heavy tests dominate.
- TypeScript tests and typecheck: the authoring host.
- Browser e2e: the Apple-silicon test node, `-n 8` then frame-time tests serially, only after confirming it was idle (its earlier high load was this build's own e2e run).

## Lanes used

| Role | Used for | Notes |
|---|---|---|
| Deterministic script | scaffolding, the lane fan-out harness (one brief, several lanes at once, tests decide), the source spot-check (HTTP fetch, text extraction, regex), score generation (`python -m hangar.mission --write-scores`) | cheapest and first |
| Local GPU lane (one 24 GB card, served model) | first drafts of the Python bodies for Tasks 1, 2, 3 (data), 5; hardening rounds | three concurrent streams per task, first passing stream kept |
| Local laptop-class lane (small MLX model) | tried on the micro task and T1/T2 | too slow for file-sized output (about 18 tokens/s, backend timeout); not used again |
| Subscription coding agent (pinned model) | Task 4 (index page and `hangar.json`), the Task 7 state module and page, Task 6 (companion service) | runs in separate worktrees, never graded by itself |
| Hosted lanes (five) | concurrency speed tests only | about $0.10 of a $5 cap; see the private speed-test table |
| Fresh-context model reviews | one fresh-context review per task | every review found real defects |
| Second-vendor model | one batched phase grade of the whole H1+H2 diff | recorded at the end of this file |

## Escalations and what failed

- T1/T2/T5: first-round local output passed 3 to 20 of the task's tests because the briefs left rules implicit. A corrected brief (named rules, exact ledger keys) fixed T1, T2 and T5. After the fresh-context reviews, hardening tests were written first (red), then the local lane was re-briefed with the failing tests and its best attempt as the current file. Three residual defects were fixed by hand after two rounds: the graph directory default in `records.py`, the unknown-arm branch in `mission.py`, and per-position type guards in `council.py`.
- T6 (a 300-line server with 15 tests) was beyond one local shot (1 to 6 of 15 passing); escalated to the subscription coding agent.
- Hosted lanes timed out (the scheduler gives hosted lanes 90 seconds) or spent the whole budget reasoning on file-sized tasks; they were only useful on short outputs.
- Reviewer-found fixes (records: malformed files, hostile values, status/history/option binding; mission: oil, unknown arm, private override that never reaches public records; council: schema in the prompt, env model, per-position validation; index: dissent on a tie, string unknowns, date objects in `hangar.json`) each have a test that was red first.

## Known limits

- The council's citations are checked for membership (the cited source is in the pack the model was shown), not for support: a position can cite a real source and still misstate it, and `reply_text` is not citation-checked. The roadmap's trust standard, not the council, is the gate.
- Council positions are written into the tracked record. The owner reviews the record diff before committing; nothing checks positions for private details the owner typed into the chat.
- The decision closes one option id. Engine, fuel path and tank resin are coupled, so the owner's reason must name all three; the record schema does not yet hold a composite pick.
- The Hangar index shows the build-time copy of the records on a public site; with the companion service running it reads the live copy.

- The decision gate sees only the file as it is now. A hand edit of `decision.option` is caught because each `to: decided` history entry records the option the owner picked; an edit of both together passes. A git-aware check (compare with the committed version) would close that and belongs in the push gate, not in the validator.
- Published fuel flows for the candidate engines sit at different power points. The mission scores compare them roughly and the record says so under `unknowns`.
- The owner proof run (Task 8) is not done: no decision has been closed in the briefing room.
