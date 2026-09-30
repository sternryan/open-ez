# Block 2 milestone 2.1: captain brief (Tasks 1–6)

Role, method (subagent-driven-development: sonnet implementer → sonnet reviewer → you re-verify),
log/report rules and the three-states rule are as in `docs/harness/block1-captain-brief.md` and the
briefs it points to. Read it first.

**Plan:** `docs/superpowers/plans/2026-09-30-block2-m21-build-progression.md`, Tasks **1–6**. Task 7
is the lead's. **Spec:** `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md` §3. The owner
has delegated approval: the plan is approved; execute it.

## Specific to this milestone

- **Crew in the foreground only.** You commit after your own green, unpiped run in open-ez, the same
  turn; restore the tracked test outputs first.
- **Another lane may be touching open-ez** (a Block 1 follow-up on `config/aircraft_config.py`,
  `scripts/generate_accuracy_report.py`, a new `scripts/vspaero_np.py`, validation JSON and physics
  tests). Do not edit, stage, stash or revert those files. If `git status` shows them modified,
  leave them alone and stage only your own files by name. If a test failure traces to that lane's
  uncommitted work, note it and re-run after it lands; don't "fix" it.
- **Visual work needs visual verification.** For every UI task, the captain takes Playwright
  screenshots (desktop 1180 px and phone 390 px) and looks at them before committing. Tests
  passing isn't enough.
- **airsup code:** read it with `gh api`, adapt with the attribution header, and add the MIT licence
  text to `NOTICE`. Never copy airsup's brand, text or images.
- **Performance budget:** never raise it. Fix the rendering instead.
- No push, no deploy, no ssh. No commit trailers. Public repo hygiene as before.

## Files you write

Log `docs/harness/block2-m21-captain.md`; report `docs/harness/block2-m21-captain-report.md` (per task:
status, sha, verify tail, screenshots taken and what they showed; deviations; anything for Task 7).
Your final message is the report content.
