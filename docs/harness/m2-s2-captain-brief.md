# M2 session 2: captain brief (Tasks 8–9)

The role, method, hard constraints, log/report rules and the "three states" rule are the same as in
`docs/harness/m2-s1-captain-brief.md`. Read that file first; everything in it applies unless this file
says otherwise.

**Scope:** plan `docs/superpowers/plans/2026-09-29-build-guide-m2.md`, **Tasks 8 and 9 only**. Stop
after Task 9. Task 10 (the full render and deploy) belongs to the lead.

## Session 1 results you build on

Read `docs/harness/m2-s1-captain-report.md`. In short:

- **Heroes are wide frames**, 3200 px across with a variable height (the spec said 4:3). Viewer CSS
  must not assume 4:3. Hero images go full width with `height:auto`.
- **`layup.json` carries `semi_span`**, and `layup_json(pl, semi_span)` is the signature.
- **The real `shots.json`** has 7 shots: `hero-bl5`, `hero-bl40`, and one `op-…` per op in
  `INCLUDED_OPS`.
- **Tests anchor paths** with `ROOT = Path(__file__).resolve().parents[2]` (the M1 idiom), never
  cwd-relative paths. The plan's Task 8/9 test code uses `Path("guide/graph")`; convert it.

## Crew dispatch: FOREGROUND ONLY

Dispatch every crew Agent **in the foreground** (never `run_in_background`). In session 1, background
crew completion notices went to the lead and you sat idle.

## Commits

The `verify-before-commit` hook needs a green test run in the same repo, in your own turn, unpiped,
before each commit. Crew leave work uncommitted; you re-verify and then commit, as in session 1.
Test runs rewrite `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json`: restore them
with `git checkout` before each commit, and never commit them.

## Files you write

- Log: `docs/harness/m2-s2-captain.md`
- Report: `docs/harness/m2-s2-captain-report.md`

Commit both at the end.

## Done means

Tasks 8 and 9 are committed, and these pass when re-run by you:
- `.venv/bin/python -m pytest -q -p no:cacheprovider` (the only allowed failure is the pre-existing
  `scripts/assembly_test.py::test_full_assembly`)
- `node --test guide/viewer/tests/*.test.mjs`
- `.venv/bin/python -m guide.check` (with `~/.config/long-ez/env` sourced)

Also `tests/guide` passes when run from `/tmp` with `--rootdir ~/open-ez`.

Your final message to the lead is the report's content.
