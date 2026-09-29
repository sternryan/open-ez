# M2 session 1: captain brief (Tasks 1–6)

**Role:** you are the **captain** (Opus). You decompose, dispatch crew, review, re-run verification
yourself, and commit. You **never write the implementation** yourself, beyond one-line fixes a
reviewer found. You never push, merge or deploy.

**Plan (the work):** `docs/superpowers/plans/2026-09-29-build-guide-m2.md`, Tasks **1 through 6
only**. Stop after Task 6.
**Spec (the why):** `docs/superpowers/specs/2026-09-29-build-guide-m2-layup-cutaway-design.md` (rev 3).
Read both in full first. The plan's Global Constraints, Spec deviations and Review Focus bind every
task.

## Method: superpowers:subagent-driven-development

For each task, in order:

1. **Implementer:** dispatch an Agent with `model: sonnet`. Paste into its prompt the task's full
   text, the plan's Global Constraints, and the task's Interfaces block. Tell it:
   - TDD exactly as written: red first, then green;
   - run the task's verify commands and paste the output;
   - commit only the task's files, with the plan's message;
   - return its findings and the verify output in its final message, never a pointer to a file.
2. **Reviewer:** dispatch a fresh Agent with `model: sonnet`. It checks the diff against the task
   text and the spec section it cites: missing behaviour, extra scope, weak tests, names that don't
   match the Interfaces block.
   - Fix loop: at most 2 rounds.
   - After that, escalate the reviewer to `model: opus` once, and note what the cheaper tier missed.
3. **You re-run the task's verify commands yourself** before marking it done. Crew "green" is a
   claim until you have seen the output.
4. Append a line to the log (below) and move on.

**Crew returns nothing or returns only a pointer:** retry once. Then switch the lane (a fresh agent,
or opus) and log it.

## HARD CONSTRAINTS

- **No push** of any repo. **No writes to anvil, hearth or any remote host.** No `fabric-gpu run`,
  no `ssh … sudo`, no deploy. Task 7 onward is the lead's.
- **compute-fabric-dev (Task 5):** run `git status` first. Commit ONLY the Task 5 files. Never
  stage, stash, reset or commit another lane's changes. If the tree has unrelated dirt, leave it and
  note it in the log.
- **Never `git add -A` / `git add .`.** Stage named files only.
- **No commit trailers of any kind** (no `Claude-Session:`, no co-author lines).
- **Never write "public domain"** anywhere. Content edits must pass `.venv/bin/python -m guide.check`.
- **Real data over fixtures:** layup tests run on the repo's real `guide/graph`.
- **Surprises:** if a task's code does not work as written (for example a CadQuery API differs, or
  glTF node names come out nested or prefixed), the crew fixes it inside the task's intent, and you
  log the deviation. If the fix would change an interface later tasks rely on, update the plan's
  Interfaces block in the same commit and log it loudly.
- **Three states, never two:** a task is `done` (you re-verified), `failed` (with output), or
  `blocked` (with reason). Never report "done" from a crew claim.
- **Stop and report instead of guessing** if Task 1 breaks G-code/DXF tests in a way the plan's
  note doesn't cover, or if the Task 3 geometry cannot be made valid within 2 crew rounds.

## Files you write

- **Log:** `docs/harness/m2-s1-captain.md`. Append one line per event:
  `time · task · lane/model · result · note`.
- **Report:** `docs/harness/m2-s1-captain-report.md`, written at the end. Include:
  - per task: status, commit sha(s), verify command and result tail;
  - every deviation from the plan and why;
  - every escalation (what the cheaper tier missed);
  - anything the lead must know before Task 7 (the live anvil run).

Commit the log and report at the end (message `docs: M2 session 1 captain log and report`).

## Done means

Tasks 1–6 are committed in both repos, and these pass when re-run by you:
- `.venv/bin/python -m pytest -q -p no:cacheprovider` (whole open-ez suite)
- `node --test guide/viewer/tests/*.test.mjs`
- `.venv/bin/python -m guide.check`
- `cd ~/compute-fabric-dev && python3 -m pytest deploy/anvil/tests -q`

Your final message to the lead is the report's content, not its path.
