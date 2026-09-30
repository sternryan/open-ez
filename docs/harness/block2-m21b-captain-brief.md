# Block 2 milestone 2.1b (lab engine): captain brief (Tasks 0–8)

Role and method are as in `docs/harness/block2-m21-captain-brief.md` (read it): subagent-driven
development, sonnet crew in the FOREGROUND only, you commit after your own green unpiped run in a
separate prior tool call, no trailers, named files only, no push/deploy/ssh. The owner delegated
approval to the lead: the spec and plan are approved; execute them.

**Plan:** `docs/superpowers/plans/2026-09-30-block2-m21b-lab-engine.md`, Tasks 0–8 (Task 9 is the
lead's). **Spec:** `docs/superpowers/specs/2026-09-30-block2-m21b-lab-engine-design.md`.

## Why this milestone exists

The owner walked milestone 2.1 on his iPad and called it rudimentary next to the airsup lab video.
The bar is visual: airsup's turbopump page (full-bleed lit scene, PBR, AO, bloom, DOF, flows in the
cut, in-scene labels). **Your judgement of the look matters more than in any earlier milestone.**
For every visual task, capture airsup's turbopump page and our lab the same way, look at both, and
write an honest comparison in the log. "Tests pass" is not done. "Looks like it belongs in that lab"
is the bar. Where a sonnet crew member's visual result is weak, escalate that task's implementation
to an opus crew member and say what the cheaper tier missed.

## Specifics

- **airsup source.** Read it with `gh api repos/AirsupHQ/airsup-lab/contents/<path>`, or clone it
  into your scratchpad, never into the repo. Vendor only the engine modules the plan names, with
  attribution headers and `NOTICE`. No airsup brand, fonts, logos, exhibits or hall scene.
- **Node toolchain.** npm and node are on the laptop; ffmpeg is needed for the film. If something
  is missing, stop and report; don't install system-wide without saying so.
- **Suite runtime** is about 5.5 min, dominated by e2e. Keep new e2e lean; reuse the site fixtures.
- **The old viewer must keep working at `/`** until Task 8.

## Files you write

Log `docs/harness/block2-m21b-captain.md`, report `docs/harness/block2-m21b-captain-report.md`:
per task, the status, sha, verify tail and the screenshot comparison paragraph; the film's path
(outside the repo) and length; deviations; anything the lead needs for Task 9. Your final message is
the report content.
