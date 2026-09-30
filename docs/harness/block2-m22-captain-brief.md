# Block 2 milestone 2.2 (fuselage box): captain brief (Tasks 1–6)

Role and method are as in `docs/harness/block2-m21b-captain-brief.md` and the briefs it points to (read
them). Sonnet crew, with opus where visual or judgement quality needs it (log why). Every crew call and
every test run you wait on runs in the FOREGROUND. You commit after your own green gate. No push,
deploy or ssh beyond the test scripts. No trailers. The owner delegated approval to the lead, so the
spec and plan are approved.

**Plan:** `docs/superpowers/plans/2026-09-30-block2-m22-fuselage.md` (Tasks 1–6; Task 7 is the
lead's). **Spec:** `docs/superpowers/specs/2026-09-30-block2-m22-fuselage-design.md`. **Evidence:**
`docs/harness/m22-fuselage-research.md`.

## Specifics
- **Gates:** `source ~/.config/long-ez/env && bash scripts/remote_test_all.sh` (two nodes, ~3–4 min), plus
  locally `.venv/bin/python -m pytest -q -p no:cacheprovider -m local_render` (this satisfies the
  commit hook), plus the lab unit tests and typecheck, plus `guide.check`.
- **Page reads:** before any value enters config or geometry, open the page image yourself (the scan
  pages are under the private dir named by the env; never print its path) and confirm it. The
  research pass is a claim until you've seen the page.
- **Representational means representational.** Template-only outlines are fitted shapes. Tag them,
  hatch them in the lab, and never let a label or readout call them book.
- **Sharing a tree.** Another lane may still have uncommitted edits (a public-build mode in
  guide/build_site.py, guide/leakcheck.py and tests/guide/test_public_build.py). Don't touch those
  files. If you must change guide/build_site.py for the fuselage export, wait until they're committed
  (check `git status`), and tell the lead if that blocks you.

## Files you write
Log `docs/harness/block2-m22-captain.md`, report `docs/harness/block2-m22-captain-report.md`. Your
final message is the report content.
