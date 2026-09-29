# M2 session 3: captain log (Task 11 + checklist nit)

`time · task · lane/model · result · note`

- 19:05Z · start · captain/opus · ok · read s1/s2 briefs, s2 report, plan T11, spec §6.1–6.3; tree clean at 397986b
- 19:10Z · T11+nit · implementer/sonnet · green (claim) · 4 files; chips → buttons; #plydock moved after #parts (Tab order); meshOpacities() helper; #checklist-h + syncChecklistHeading; e2e 19 passed; checklist red was weak (missing id), reviewer to mutation-check
- 19:17Z · T11+nit · reviewer/sonnet r1 · CHANGES · mutations a–d all red (checklist red now strong); should-fix: dock+isobar+isolation linger over Cutaway (applyPane); dock covers wrapped chips at 1180 (fixed bottom:56px); isolate() pre-load label "undefined"/no re-apply; nit: #showall off-theme in dark
- 19:35Z · T11+nit · implementer/sonnet r1 fixes · green (claim, relayed by lead: resumed agent ran in background) · applyPane hides dock+showAll off-3D; #dockstack column-reverse keeps dock above chips; label cid from #plydock.dataset.cid + loader re-applies isolation; #showall themed; e2e 25, tests/guide 173
- 19:45Z · T11+nit · reviewer/sonnet r2 · CHANGES · fixes 1–4 verified real, mutations red (fix-2 test vacuous at 820); should-fix: #isobar covers #viewtoggle at 390 px (click intercepted); test should assert chips wrap at 1180; nit: empty #parts area swallows canvas clicks (pre-existing); nit: dock covers most of 3D at 390
- 19:52Z · T11+nit · fixer/sonnet r2 · green (claim) · isobar own row <820px; wrap guard at 1180; #parts pointer-events none, .chip auto; e2e 27, tests/guide 175
- 19:53Z · T11+nit · escalation · reviewer → opus · fix loop hit its 2-round cap; sonnet r1 and r2 each found new visible-layout defects (Cutaway linger, chip overlap, then isobar over toggle at 390) that the plan's tests and the implementer missed
- 20:00Z · T11+nit · reviewer/opus r3 · CHANGES · BLOCKER: isolate/showAll flip material.transparent without needsUpdate → three r186 keeps OPAQUE define, nothing ghosts on screen after first frame; all tests read meshOpacities() (internal state) so passed. SHOULD-FIX: GU c10.shear-web shows the Roncz ply schedule (plies keyed by shared component). What sonnet r1/r2 missed: both judged ghosting from screenshots/opacity values; opus compared canvas pixels before/after
- 20:10Z · T11+nit · fixer/sonnet r3 · green (claim) · needsUpdate + ghost depthWrite=false / isolated opaque; plies only on cutawayFor ops (GU gets none); role=group+aria-label dock, aria-live isotext, aria-expanded/controls chips (MutationObserver); pixel test 1180: 10837 → 3674 → 10837 dark px, red 10837→12888 without fix; 820 pixel clip too sparse (35%), 1180 only
- 20:14Z · T11+nit · captain verify · done · full 1 failed (pre-existing test_full_assembly) 420 passed 2 skipped; node 16/16; guide.check OK (202 texts, recall 5/5); tests/guide from /tmp 177 passed; viewer e2e 29 passed (root + thread cwd)
- 20:15Z · T11+nit · captain commit · hook block then ok · same cwd-key gate as s1/s2; re-ran green from thread cwd, committed with git -C: 645acc2
- 20:20Z · end · captain/opus · done · report written; T11+nit 645acc2
