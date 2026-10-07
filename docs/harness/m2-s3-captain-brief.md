# M2 session 3: captain brief (Task 11 + checklist nit)

The role, method, hard constraints, log/report rules, the "three states" rule, **foreground-only
crew** and the commit gate are the same as in `docs/harness/m2-s1-captain-brief.md` and
`docs/harness/m2-s2-captain-brief.md`. Read both, and the session 2 report
`docs/harness/m2-s2-captain-report.md`, first.

## Scope

1. **Plan Task 11: ply list with isolate** (`docs/superpowers/plans/2026-09-29-build-guide-m2.md`).
   - Anchor test paths with `ROOT`.
   - The global `[hidden]{display:none!important}` rule from session 2 already covers `#isobar` and
     `#plydock`.
   - The e2e must check what is **visible** and the isolated state, not just the internal state:
     inner web ply 3 isolated (the other meshes' opacity < 1), the bar text, Escape resets it,
     changing op resets it, and it works at 820 px wide.
   - The ply list must also be reachable by keyboard.
2. **Nit:** on the "Canard layup at a glance" view, the aside shows an empty "Checklist" heading. It
   is M1's static `<h3>Checklist</h3>`. Hide the heading whenever the checklist is empty, which also
   covers ops without completion items. Add an e2e assertion for it.

Stop after these two. Task 12 (final verification, grader, push question, Ryan's sign-off) belongs
to the lead. Do not deploy; the lead deploys.

## Files you write

- Log: `docs/harness/m2-s3-captain.md`
- Report: `docs/harness/m2-s3-captain-report.md`

Commit both at the end.

## Done means

Both items are committed, and these pass when re-run by you:
- the full open-ez suite (the only allowed failure is the pre-existing
  `scripts/assembly_test.py::test_full_assembly`)
- node tests
- `guide.check` (with `~/.config/long-ez/env` sourced)
- `tests/guide` run from `/tmp` with `--rootdir <repo>`

Your final message to the lead is the report's content.
