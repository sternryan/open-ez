# Block 2 milestone 2.1b: captain report (Tasks 0–8)

Plan `docs/superpowers/plans/2026-09-30-block2-m21b-lab-engine.md`, Tasks 0–8; spec
`docs/superpowers/specs/2026-09-30-block2-m21b-lab-engine-design.md`. The lab now serves `/` and the
2.1 viewer lives at `/classic/`. Nothing is pushed or deployed. The full log is
`docs/harness/block2-m21b-captain.md`.

**Method.** Crew were sonnet, run in the foreground. Opus crew were used twice, for visual reasons:
- Task 5, the look of the flows.
- Task 8a, the UI layout.

After each task the captain looked at GPU-path screenshots next to airsup's turbopump page, ran the suite unpiped, and committed.

The captain stalled for about 5.5 h during Task 5, waiting on a suite run that had been moved to the background and whose completion notice never arrived. The lead caught it. After that every wait ran in the foreground.

## Done-means (captain, at 927401d)

- **Full suite** (`.venv/bin/python -m pytest -q -p no:cacheprovider`, one foreground run, load about 5): **618 passed, 2 skipped, 9 xfailed, 0 failed in 333 s.** The test count dropped from 650 because the 2.1 tests moved from the classic file to the lab.
- **Node tests:**
  - `node --test guide/viewer/tests/*.test.mjs`: 50/50.
  - `npm --prefix guide/lab test`: 87/87.
  - `npm --prefix guide/lab run typecheck`: clean.
- **`guide.check` was not run.** This checkout has no `.env`, and the private sources it checks are absent.

## Per task

| # | Task | Status | Commit | Verify tail (captain, unpiped) |
|---|---|---|---|---|
| 0 | Engine skeleton | done | 243a088 | 613 passed, 2 skipped, 9 xfailed (338 s) |
| 1 | Workshop scene, shots, UI shell | done | 763b70e | 619 passed (431 s) |
| 2 | Materials | done | 9153393 | 620 passed (436 s) |
| 3 | 2.1 logic port, ply lay-down | done | 053366e | 623 passed (485 s) |
| 4 | Section cut, labels, readout | done | beea92b | 637 passed (578 s) |
| 5 | Flows (load paths) | done (opus escalation) | b7a1149 | 43 + 597 passed, split at the tool's 600 s cap |
| 6 | Director tour and film | done | 336bb36 | 645 passed (802 s) |
| 7 | Quality tiers and budget | done | 79ea865 | 51 + 599 passed, split |
| 8a | UI pass before switch-over | done (opus) | b6ec71b | lab e2e 54 passed |
| 8b | Parity and switch-over | done | 927401d | 618 passed (333 s) |

Every run had 2 skipped and 9 xfailed, and none had a failure.

## Screenshot comparisons, per visual task

All captures are headless Chromium on the Metal GPU path, at 1400×860 and 1180×820, taken the same way as airsup's turbopump page. They are in the scratchpad only and never committed.

**Task 0.**
- **Ours:** a lit, shadowed amber slab on a dark plinth in a dim dome, with DOF and a vignette.
- **airsup:** a place — walls, screens, a lit pedestal, and a subject with many materials.
- **Gap:** ours has no room, one colour, and a hard band at the horizon. That is acceptable for a skeleton.

**Task 1.**
- **Ours:** the home shot reads as a workshop: a plywood table with notched jig blocks, steel shelves with cloth rolls, a pegboard, a bright window and teal accent strips. All of it is soft behind the canard, with dark translucent cards in airsup's arrangement.
- **Gap:** the canard was still one flat amber, the op shots showed mostly floor behind the subject, and the jig blocks were crude.

**Task 2.**
- **Ours, close up:** four distinct materials — faint foam cells, straw UND tows with stitching, a cooler BID basket weave, and dark glossy wet epoxy.
- **Gap:** at the home distance the weave fades out to avoid moire, so the canard is a smooth satin slab. That is less rich than airsup's metal, which carries anisotropic highlights at every distance.

**Task 3.**
- **Ours:** the lay-down reads. Dry white cloth unrolls from the root with a clean edge, the wet front sweeps with a glossy leading edge, and the op settles to cured straw. It is the first thing that has airsup's "the machine is doing something".
- **Gap:** there is no squeegee prop, the dry cloth is flat white, and there is no glow yet.

**Task 4.**
- **Ours:** the close view of the cut at B.L. 20 is the first frame that belongs in airsup's lab. It shows layered teal and olive skin bands with resin lines, the web plies as separate strips, and foam cells. The shear-web op, cut at B.L. 10, finally shows the web between the core halves.
- **Gap:** the foam cap was grey cobblestone (fixed in Task 5), the labels cluster near the cut, and the left-hand UI stack was tall.

**Task 5.**
- **Sonnet version:** the flows read as painted ribbons.
- **After the opus pass:** neon threads with moving comet heads at the op shots, glowing streaks across the cut, and a blue beam into the web section.
- **Gap:** airsup's flows are glowing volumes of fluid in dark metal, so the whole machine glows. Ours are thin threads on a pale laminate. The halo comes mostly from a darkened band, not from bloom, which leaves a faint outline up close.

**Task 6 (film frames).**
- **Ours:** the title card, the lay-down, the cursor dragging the real section slider, and a closing orbit of the layered cut with comet flows. They read as airsup's grammar: cursor, cards, DOF and glow.
- **Gap:**
  - Mid-film frames are mostly plain pale laminate with little contrast.
  - Our overlays are heavier than airsup's.
  - The seven ops without plies are dwell shots where nothing moves.

**Task 7.**
- **Ours:** high and medium look alike except for DOF. Low is recognisably the same lab, but flat and aliased, with no shadows or weave.
- **Finding:** at the iPad size the UI buried the canard.

**Task 8.**
- **Ours:** after the opus UI pass the canard owns the frame at iPad and desktop sizes. There is one compact card top-right and one bottom-left card, as airsup has.
- **Gap:**
  - Our tiles are a joined strip, not separate floating tiles.
  - On the phone, the home shot still shows a small canard under a lot of backdrop.

**Honest overall.** The lab is now in airsup's family: lighting, PBR, AO/bloom/DOF, filled caps, flows, pill labels, cards, a cursor-driven film. The two gaps that remain are real:
- **The subject.** A long, pale, flat wing is less iconic than a turbopump, so mid-shots lack contrast.
- **The flows.** Ours are threads on a pale laminate, not glowing volumes in dark metal.

The owner's walk-through is the judge.

## The film

- **Path:** the captain session scratchpad, `film/canard-ch30.mp4` (the lead has the full local path), outside the repo.
- **Format:** 89.75 s, 1920×1080, 60 fps, about 127 MB.
- **Render:** 5 min 11 s on the Metal GPU path.
- **Tour:** Roncz chapter 30, all 12 non-stub ops in order.
  - The five ops with plies play their lay-down and show the cut at one station.
  - The film ends on a 9 s close orbit of the B.L. 20 cut face, then an end card.
- **Determinism:** two runs give byte-identical frames 0, 120 and 240 (e2e).
- **Caveat:** it was rendered at 336bb36. The UI pass and the switch-over came later, so the film shows the older, heavier cards. Re-render before showing it: `npm --prefix guide/lab run record -- canard <out.mp4> 60 http://127.0.0.1:<port>/` against a served, freshly built site.

## Deviations (all logged)

1. **The canard is inverted in the jig until `r30.turnover-twist-check` and flips on op change.** The spec says the bottom-side ops are shot from below the jig. From below, the camera looked up through the table's rails. The build really is upside down until the turnover, so the lab shows that. The "from below" shots are kept in the canard's frame, which with the canard inverted puts the camera above the table. **Flag this for the owner.**
2. **Lab shots.** `shots.ts` keeps every tours.yaml target and authors a 3/4 position for the room. The 2.1 positions looked straight down. A test holds the targets equal.
3. **Jig blocks are representational.** The graph names no ch30 jig stations, so five evenly spaced blocks are flagged in code. The glb holds one half-span, 70.8 in.
4. **The build_site stamp.** The lab is built only when its inputs change, and npm missing still fails loudly. This is not the plan's unconditional `npm ci`, which would add minutes across about 80 fixtures.
5. **The section keeps the outboard piece** (2.1's convention), so the cut face faces the root-side op shots.
6. **Wet epoxy uses a darker base with clearcoat, not true transmission.** Transmission would add a second scene render. There is no flox or micro geometry, so those materials are unused.
7. **The tour runs the build clock 2.5× faster** to fit about 90 s. A canvas drag also stops a tour. 2.1's "leave the 3D pane" stop has no lab equivalent.
8. **The low tier is flat-lit with an adaptive resolution** (see the risks below). Auto step-down uses 34 ms, so a 30 Hz display is not treated as slow, and it never steps back up by itself.
9. **`/lab/` was removed with no redirect.** The classic viewer reads its data through a `data-base` meta tag, the only logic change in app.js. Its cutaway `src` is now `../renders/...`.
10. **2.1 tests not applicable to the lab** (isolate, the ply dock, the cutaway/glance pane, light/dark schemes) stay covered only on `/classic/`, as M2 behaviour. The full mapping is below.

## For the lead (Task 9)

1. **Re-export and re-render.** `output/` is untracked, so re-export (`guide.export_glb`) and rebuild before deploying. Then re-render the film from the final UI.
2. **The low-tier budget proves less than it looks.** The 33 ms e2e passes (median 16.7 ms on three runs) only because the low tier's adaptive resolution shrinks the canvas to 70k–125k pixels, about 8–13% of 1180×820. Swiftshader measured 67 ms per frame at 0.5 MP even with three's plain material, so software fill rate is the wall. The number was never raised. The iPad itself is unmeasured.
3. **iPad risk: WebGL context loss.** The high tier uses MSAA-4 half-float targets and a 4096 shadow map at DPR 2, and Safari drops contexts under memory pressure. One test run showed a probable swiftshader context loss after back-to-back tier and resolution rebuilds. The lab has no context-lost message yet. If the iPad shows a black canvas, start there.
4. **Two things to put in front of the owner:** the inverted-jig decision (deviation 1), and the GU variant. GU has no layup in 3D, as in 2.1, and its tour is dwell-only chapters 10 and 12.
5. **Leak scan.** Clean over the lab, build_site and the lab tests. The 2.1-era findings in `docs/history/` are the lead's, from the previous report.
6. **The film is in the scratchpad.** It is not in the repo, and it needs the re-render above.

## Mapping of 2.1 behaviour tests to lab tests

Every Block 2 M2.1 test in `tests/guide/test_viewer_e2e.py` is now covered by a lab test in `tests/guide/test_lab_e2e.py`. NEW means ported in Task 8, and n/a means the feature does not exist in the lab.

| 2.1 test | Lab |
|---|---|
| scrubber_selects_web_plies_and_core_built | NEW |
| earlier_op_leaves_no_later_ply_visible | NEW |
| ghost_toggle_and_memory | NEW (popover), plus build-state test |
| play_steps_scrubber_and_second_press_stops | NEW, plus play/cure test |
| scrubber_hidden_without_plies_and_hooks_need_test_flag | NEW |
| build_controls_clear_of_other_controls | NEW (1180, 390) |
| isolate_* / play_stops_when_isolating_or_leaving_3d / isolate_stops_the_tour / leaving_3d_stops_the_tour / tour_restores_the_cutaway_view | n/a: no isolate or cutaway pane; covered on /classic/ |
| variant_change_keeps_isolate_rule | Build-state half NEW; the isolate half is n/a |
| phone_model_stays_visible_and_scrubber_reachable | NEW |
| section readout, only built layers, cut geometry at 6 stations, no caps hidden/disabled, not mirrored, caps follow build, section off | Ported in Task 4 |
| section_cap_pixels_at_the_cut_face | NEW: an on-vs-off pixel difference, since the lab's materials differ from 2.1's flat colours |
| section_control_hidden_without_layup | NEW |
| section_controls_are_touchable_and_inside | Card-overlap and 44 px test |
| load paths: clip, follow build, toggle and memory, storage throws, world points, own colours | Ported in Task 5. The lab has no light/dark scheme |
| tour: button, nothing selected, follows selected chapter, stub-only fallback | Film test, plus the three NEW 2.1 ports |
| escape, second press, op click, variant change, play press, scrub drag stop the tour | The user-actions-stop-the-tour test |
| tour_leaves_the_section_cut_and_paths_as_the_user_set_them | Storage test, plus NEW cut test |
| stopping_the_tour_leaves_no_animation | NEW (found and fixed a real bug) |
| tour_eases_to_each_authored_shot / order matches graph and scrubber completes | Film test, extended |
| tour_button_is_touch_sized_and_clear_of_other_controls | NEW, 44 px |
| frame_time_median_while_dragging_the_section | Task 7, 33 ms |
| frame_time_at_dpr2 (reported only) / section_at_dpr2_projection_and_cap_pixels / phone_section_readout_one_line | NEW |

## Follow-up after Task 8: test lanes, WebKit (61ab071)

Done at the lead's direction, after the Task 8 commit.
- **`local_render` marker.** It is registered in `pyproject.toml`. The number of collected tests is unchanged at 629 (counted before the WebKit parameter was added). Three tests are marked:
  - the viewer's `test_isolate_visibly_ghosts_other_plies_on_screen`;
  - the lab's `test_recorder_frames_are_reproducible`;
  - the lab's `test_frame_time_median_while_dragging_the_section_on_the_low_tier`.
  The viewer's 2.1 frame-time test no longer exists: it moved to the lab in Task 8.
- **`remote_test.sh`.** It now quotes every argument into the ssh command with `printf %q`. It adds `-m "not local_render"` unless the caller passes `-m` itself.
  - `remote_test_all.sh` drops its quoting workaround.
  - Its Mac `local_render` pass no longer deselects the lab file. Before, that deselect stopped the two lab `local_render` tests from running anywhere.
  - Quoting proof: `--collect-only -m "not local_render"` on the Linux node exits 0 and collects 683 tests. It used to exit 5.
- **The lab budget test's premise.** The old check `len(set(seen)) >= 100` failed on the Mac node: a 92-frame run gave 91 distinct stations, with a 16.7 ms median. That check measured frame count, not whether the plane moved. The new checks are:
  - at least 90% of drag ticks give a new station;
  - no tick jumps more than a tenth of the span.
  The 33 ms budget is unchanged.
- **WebKit.** Every lab e2e test is now parametrized over Chromium and WebKit, which is the iPad's engine. WebKit is skipped off macOS or when it is not installed, and it was installed in user space locally and on the Mac node.
  - All 61 WebKit tests passed locally in 131 s, so no lab code needed fixing (crew run). Chromium also passed 61 of 61, in 308 s.
  - The Linux shard never runs WebKit, because it ignores the lab file.
- **Captain's gate at 61ab071.**
  - `source ~/.config/long-ez/env && bash scripts/remote_test_all.sh` (host names stripped from the output):
    ```
    == linux (exit 0)
    556 passed, 2 skipped, 9 xfailed, 3 warnings in 60.79s (0:01:00)
    == mac (exit 0)
    118 passed, 12 warnings in 142.55s (0:02:22)
    5 passed, 23 warnings in 56.42s
    --- remote_test_all: linux=0 mac=0, wall 201s
    ```
  - Locally: `.venv/bin/python -m pytest -q -p no:cacheprovider -m local_render` gave `5 passed, 685 deselected, 8 warnings in 42.50s`.
