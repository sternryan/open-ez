# Planform correction: captain brief (Tasks 1–6)

The role, method (superpowers:subagent-driven-development: sonnet implementer → sonnet reviewer →
you re-verify), hard constraints, log/report rules and the "three states" rule are the same as in
`docs/harness/m2-s1-captain-brief.md`, with the commit and crew rules from
`docs/harness/m2-s2-captain-brief.md`. Read both first. This brief overrides them where they differ.

**Plan (the work):** `docs/superpowers/plans/2026-09-29-planform-correction.md`, Tasks **1 through 6
only**. Stop after Task 6. **Spec (the why):** `docs/superpowers/specs/2026-09-29-planform-correction-design.md`
(§2 is the evidence table). Read both in full. The plan's Global Constraints, Spec deviation and
Review Focus bind every task. Ryan approved the plan as written on 2026-09-29.

## Crew dispatch: FOREGROUND ONLY

Dispatch every crew Agent **in the foreground** (never `run_in_background`). Background crew
completion notices go to the lead, and you sit idle.

## Commits

- Crew leave work **uncommitted**. You re-run the task's verify commands, then commit.
- The `verify-before-commit` hook needs a green, **unpiped** test run in open-ez, in your own turn,
  right before each commit.
- Test runs rewrite `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json`. Restore them
  with `git checkout -- <paths>` before each commit and never commit them. Exception: Task 5
  deliberately regenerates `data/validation/accuracy_report.json`, which IS committed.
- Stage named files only. No trailers of any kind (no `Claude-Session:`, no co-author lines).

## Hard constraints

- **No push, no deploy, no remote writes.** No `gpu-runner`, no `ssh`. Tasks 7–8 are the lead's.
- open-ez is **PUBLIC**: no private-network hostnames or IPs, no home-directory paths, never the phrase
  claiming the plans are out of copyright. The Task 1 ledger quotes at most ~10 words paraphrased.
  Never print values from `~/.config/long-ez/env`.
- **Never loosen a physics tolerance.** A failing physics bound becomes a strict xfail citing a
  numbered ledger row. If a crew member widens a tolerance, reject the change.
- **Real numbers:** the NP gap, the re-locked values, and the chord decision come from actual runs
  and searches, never from the plan's examples.
- **Stop and report instead of guessing** if: book geometry makes CadQuery generation fail (invalid
  solids, generator exceptions) and 2 crew rounds can't fix it within the task's intent; or triage
  finds a failure that is neither category (a) nor (b).

## Files you write

- Log: `docs/harness/planform-captain.md` (one line per event: `time · task · lane/model · result · note`)
- Report: `docs/harness/planform-captain-report.md`. Per task: status, commit sha(s), verify command +
  result tail; the Task 1 chord decision; the NP gap (computed, 108.0, signed gap, grade); every
  ledger row that is a strict xfail; every deviation and escalation; anything the lead needs for
  Task 7 (re-export, re-render, deploy).

Commit both at the end (`docs: planform correction captain log and report`).

## Done means

Tasks 1–6 are committed in open-ez, and these pass when re-run by you:
- `.venv/bin/python -m pytest -q -p no:cacheprovider` (the only allowed non-xfail failure is the
  pre-existing `scripts/assembly_test.py::test_full_assembly`)
- `node --test guide/viewer/tests/*.test.mjs`
- `source ~/.config/long-ez/env && .venv/bin/python -m guide.check`

Note: `tests/guide` M2 tests pinned to `semi_span` 73.5 may fail after Task 3. Triage them in Task 4
as category (a) like any other failure (the plan's Task 7 Step 2 assumed they'd surface later; if
they surface now, handle them now and log it).

Your final message to the lead is the report's content, not its path.
