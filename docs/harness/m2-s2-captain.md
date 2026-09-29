# M2 session 2: captain log

`time · task · lane/model · result · note`

- 18:13Z · start · captain/opus · ok · HEAD 2c7f817, tree clean; read s1 brief/report, s2 brief, plan Tasks 8-9
- 18:18Z · T8 · implementer/sonnet · green · red 7 failed (KeyError plies / renders kwarg) → green 17 passed; from /tmp 9 passed. Deviations: ROOT-anchored paths, make_export mkdirs
- 18:18Z · T8 · reviewer/sonnet · APPROVE r1 · 5 nits; captain applied 2 one-liners: drop unused _P import; _cutaway raises SchemaError when layup.json/shots.json missing (was raw FileNotFoundError). Declined: pre-rmtree check (build still fails non-zero), CLI smoke test, swatch null (viewer guards it)
- 18:18Z · T8 · captain verify · done · full suite 1 failed (pre-existing test_full_assembly) 396 passed 2 skipped; tests/guide 153 passed · commit e31f6ab
- 18:51Z · T9 · implementer/sonnet · green · red: node ERR_MODULE_NOT_FOUND cutaway.js; e2e 4 failed 9 passed → green node 16/16, e2e 13 passed (root + /tmp), guide.check OK. Deviations: ROOT anchor; heroes full width height:auto, glance figures stacked; [hidden] override; glance-safe guards on `current` (line-53 highlight, variant onchange); pageerror sweep
- 18:51Z · T9 · reviewer/sonnet r1 · CHANGES · 3 must-fix: #c/#parts never hid (CSS display beat [hidden]; canvas stayed under the cutaway), phone viewport fixed 50vh vs stacked panes, tests blind to both. Nits: roving tabindex, blank zoom on failed PNG, no loading placeholder, sub-44px chips (→ Task 11)
- 18:51Z · T9 · fixer/sonnet r1 · green · global [hidden]{display:none!important}; #viewport.paned under 820px; tests strengthened (red first: 4 failed); roving tabindex; #cutzoom hidden on error; .loading placeholder. e2e 15 passed root + /tmp
- 18:51Z · T9 · reviewer/sonnet r2 · APPROVE · 3 nits deferred: showCut re-sets same src (placeholder flash), .loading untested, two wait_for_timeout sleeps
- 18:51Z · T9 · captain commit · hook block · marker keyed on hook cwd (thread cwd reset to memory dir) vs `cd open-ez &&` gate key; re-ran green from thread cwd, committed with git -C (same as s1)
- 18:51Z · T9 · captain verify · done · commit 6f050ff. Other lane landed 33d11d4 (render_cutaway lease holder/ETA) between my runs; re-verified at HEAD 6f050ff: full 1 failed (pre-existing) 406 passed 2 skipped; node 16/16; guide.check OK exit 0; tests/guide from /tmp 163 passed
- 18:52Z · end · captain/opus · done · report written; T8 e31f6ab, T9 6f050ff
