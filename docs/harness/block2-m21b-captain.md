# Block 2 milestone 2.1b: captain log (Tasks 0–8)

Captain: Opus. Crew: sonnet in the foreground, opus where a sonnet visual result is weak (reason logged).
Start: main at a71c9a4, clean. airsup-lab read from a scratchpad clone at e21864b (not in the repo).

## Setup
- Toolchain: node v22.22.0, npm, ffmpeg present on the laptop.
- Screenshot method (ours and airsup's alike): headless chromium via Playwright with
  `--enable-gpu --ignore-gpu-blocklist --use-angle=metal` (WebGL renderer reported: ANGLE Metal, Apple M4),
  viewports 1400×860 and 1180×820, fixed settle wait. airsup reference captured from
  https://airsup.ai/rocket-engine/turbopump after 15 s. Captures live in the scratchpad only.
- Baseline (2.1 viewer, top-skin op): a small grey canard with flat hemisphere light on a blank page,
  three sidebars around it; the model fills about 15% of the frame. airsup: a full-bleed lit room, the
  pump fills about 60% of the frame on a pedestal, blurred background, filled cut faces, glowing flows,
  pill labels with dots, a dark translucent control card top-right, stats tiles bottom-left, an exhibit
  bar along the bottom.

## Task 0: engine skeleton (243a088)
- Crew: one sonnet implementer (foreground). Captain reviewed the diff (attribution headers, NOTICE list,
  gitignore, build_site) instead of a separate reviewer: the task is scaffolding and the diff is small.
- Deviation: build_site builds the lab only when its inputs change (a sha256 stamp over the lock, configs
  and src/, and a lock stamp for `npm ci`). The plan says it runs `npm ci && npm run build`; running that
  inside ~80 test fixtures would add minutes per run. It still raises when npm is missing (tested).
- Verify (captain, unpiped): node 50/50; lab test 1/1; typecheck clean; full suite 613 passed, 2 skipped,
  9 xfailed in 338 s.
- Screenshots: `t0-lab-desk.png` against `airsup-pump-desk.png`. Ours is a lit, shadowed amber slab on a
  dark turned plinth in a warm dim room, with DOF on the floor and a vignette, framed at about 70% of the
  width. airsup's reads as a place: walls, screens, a lit pedestal and a subject with many materials and
  glowing interior. Ours has no room (a dome and an empty floor, with a hard band at the horizon), one flat
  colour and an oversized plinth. That is acceptable for a skeleton and is exactly Tasks 1 and 2's work.

## Task 1: workshop scene and framing (763b70e)
- Crew: sonnet implementer, then a sonnet fix round on the captain's findings (the captain reviewed the
  screenshots and the diff in place of a separate reviewer; the findings were visual).
- Captain's findings from the first captures: the bottom-side shots put the camera under the table,
  looking up through the strongback rails (unusable); the top-skin shot looked straight down at a slab
  over a grey floor; the step card was too big.
- **Deviation (spec §2 "bottom-side ops are shot from below the jig").** The canard is built upside down
  in the jig until `r30.turnover-twist-check` ("lift the canard off the jigs, set it right side up"), so
  the lab now inverts it for the earlier Roncz ops and animates the flip on op change (a pure
  `orientation(graph, variant, op)`, unit-tested). The bottom-side shots are still authored "from below"
  in the canard's frame, which with the canard inverted puts the camera above the table. This keeps the
  spec's intent (look at the bottom face) and is truer to the build. Lead: flag for the owner.
- **Deviation (lab shots).** tours.yaml positions were authored for the 2.1 viewer (top skin looked
  straight down from 75 in). `guide/lab/src/shots.ts` keeps every tours.yaml target and authors a 3/4
  lab position around it; a test holds the targets equal.
- **Deviation (jig blocks).** The graph names no ch30 jig stations, so five evenly spaced blocks stand in,
  flagged `userData.representational` and in a comment.
- The glb carries one half of the canard (70.8 in of span), so the table is sized to it, not to the full
  130 in jig.
- Verify (captain): node 50/50; lab 10/10; typecheck clean; full suite (unpiped) 619 passed, 2 skipped,
  9 xfailed in 431 s. A piped run was refused by the verify hook, as it should be.
- Screenshots: `t1-lab-*`, `t1b-*` (home and the five toured ops at both sizes), against airsup's pump.
  Home now reads as a place: a plywood table with notched blocks, steel shelving with cloth rolls, a
  pegboard, a bright window and teal accent strips, all soft behind the canard, with dark translucent
  cards over it in airsup's arrangement. The op shots frame the working surface large at 3/4 with the
  room falling away. Still short of airsup: the canard is one flat amber (Task 2); the op shots show
  mostly floor behind the subject rather than a glowing set; the jig blocks are crude wedges; the
  room has no hero prop. The UI shell is in the right family; its typography is plainer than airsup's.

## Task 2: materials (9153393)
- Crew: sonnet implementer. Captain tuned the foam and BID parameters in `composite.ts` directly (four
  constants, one file) after looking at the close-ups, rather than a second crew round.
- Captain's findings: the foam close-up read as cobblestones (6 cells/in with 0.2 wall darkening and
  0.03 in bump) and BID read as bathroom tile (0.3 in tows, heavy gap darkening). Tried 14 and 9 cells/in:
  the anti-alias fade then removed the cells entirely at a 12 in view. Settled on 6 cells/in with 0.16 wall
  shading, 0.015 in bump and a slightly darker foam base (the old one clipped to white); BID tows at
  0.18 in with half the gap darkening.
- No flox or micro geometry exists in the export, so the two materials are in the palette and unused
  (not invented). Colours are representational and commented as such.
- Wet epoxy uses a darker base, full clearcoat and a softened weave instead of true transmission, which
  would add a second scene render the pipeline does not expect.
- Verify (captain): lab 16/16; typecheck clean; node 50/50; full suite 620 passed, 2 skipped, 9 xfailed
  in 436 s.
- Screenshots: `t2-*`, `t2e-*` (foam close-up and home), against airsup's pump. Close up, the four
  materials are distinct: faint foam cells, straw UND tows with stitching, a cooler green-grey BID basket
  weave, dark glossy wet epoxy with a hotspot. At the home distance the weave fades out (no moire), so
  the canard is a smooth pale-straw slab with a satin sheen. It is a clear step up from flat amber but
  still less rich than airsup's metal, which carries anisotropic highlights and roughness breakup at every
  distance. The build progression (Task 3) should do more for the home shot than more shader detail.

## Task 3: logic port and ply lay-down (053366e)
- Crew: sonnet implementer. Captain changed one shader line (wet colour) after looking at the captures.
- Review Focus 1: build, section and tour are ported to `guide/lab/src/logic/`; the lab's
  build/section/tour tests are the 2.1 files with only the import line changed, and `parity.test.ts`
  fails if either side is edited alone (captain spot-checked build with a diff). The verbatim copies are
  excluded from `tsc` (untyped JS bodies) but run under tsx.
- Review Focus 2: `plyPhase` is pure in (op index, order, lay, count, t) and returns the same state as
  `visibleSet`; earlier ops' plies are cured and never wet; the current op's laid plies stay wet until the
  op is complete, then all cure together (a wet layup cures as one). A sweep test over every op, lay and t
  in a synthetic graph checks both rules against `visibleSet`. e2e covers stepping backwards, the
  previous op cured at lay 0, and Play ending cured.
- Captain's finding: wet BID rendered as saturated green and wet UND as saturated amber (the wet mix
  raised saturation with a power curve). Changed to a darker, 45% desaturated colour with a faint amber
  cast, so wet cloth reads as going translucent. Recaptured (`t3b-*`): wet BID is a muted olive, wet UND
  a translucent straw with a gloss streak at the front.
- Shear web: the web ply is edge-on inside the core's slot, so its lay-down cannot be seen in the
  assembled view (the core is one mesh). The section cut (Task 4) and the tour's cut station are the
  answer; nothing is ghosted to fake it.
- Verify (captain): lab 60/60; typecheck clean; node 50/50; full suite 623 passed, 2 skipped, 9 xfailed
  in 485 s.
- Screenshots: `t3-*` and `t3b-*` against airsup's pump. The lay-down reads: dry white cloth unrolls
  from the root with a clean edge over the wet ply below, the wet front sweeps with a glossy leading
  edge, and the op settles to cured straw. This is the first thing in the lab that has airsup's "the
  machine is doing something" quality. Still short: no squeegee prop, the dry cloth is flat bright white,
  and the frame has none of airsup's glow, labels or cutaway yet.

## Task 4: section cut, labels and readout (beea92b)
- Crew: sonnet implementer. Captain reviewed the captures and the diff; no fix round.
- Deviation from the captain's own brief (not the plan): the crew kept 2.1's convention, removing the
  inboard side and keeping the outboard piece, because the lab's op shots look from the root and an
  outboard removal turns the cut face away from them. `planeConstant` reports 2.1's numbers
  (-25 at B.L. 25). Accepted: it is the 2.1 behaviour the parity tests encode.
- Review Focus 3: the 2.1 section e2e is ported to the lab (readout layers, only built layers, capped
  nodes equal the layup at B.L. 5/20/30/40/54/60, no caps for hidden/ghost/disabled, not mirrored, caps
  follow the build, off restores the view).
- The cap pass got a polygon offset: the core's cap z-fought the coincident inner face of the skins.
- Labels: six (core, web, both caps, both skins); lift tabs have no geometry, so no label. The vendored
  labels.ts sets text with textContent, not innerHTML.
- Readout: station, layers here (2.1 `summarize`), plies n/N, cloth so far by count, and mass as the
  literal "not yet computed".
- Verify (captain): lab 60/60; typecheck clean; node 50/50; full suite 637 passed, 2 skipped, 9 xfailed
  in 578 s. **Runtime:** the lab e2e now costs about 4 min on its own (40 tests with test_build_site);
  the suite is up from 5.6 to 9.6 min. Task 8 must consolidate the lab e2e (one browser per module)
  rather than add to it.
- Screenshots: `t4-*` against airsup's pump. The close view of the cut at B.L. 20 is the first frame that
  genuinely belongs in airsup's lab: layered teal and olive skin bands with resin lines, the web plies as
  separate strips, foam cells in the core, all crisp. The shear-web op with the cut at B.L. 10 finally
  shows the web between the two core halves. Short of airsup: the foam cap is greyer and more
  cobblestone than airsup's clean machined caps; labels cluster near the cut end and the shear-web label
  floats on the skin (no occlusion test); the readout dock plus step card stack is tall on the left
  (~40% of the height at 1180×820), where airsup's cards are more compact; the control card now spans
  the top edge.

## Task 5: flows (load paths)
- Crew: sonnet implementer, then **escalated to an opus crew member for the look**. Why: the sonnet flows
  worked and passed, but additive light washed out on the pale laminate, so it switched to a mix blend
  and the flows read as painted green and orange ribbons lying on the cut, and as thin wires at the op
  shots (`t5-grid.png`). The cheaper tier traded glow for saturation and did not find the combination
  that keeps both.
- Opus changes: a camera-facing ribbon with a hot core, a soft coloured halo and comet-shaped pulses
  (width held at 7–20 px on screen); light added over a slightly darkened band, which keeps the hue
  saturated through the ACES tone map; a `FOLLOW` value (eased through step(dt), no recompile) that dims
  and desaturates the laminate while load paths are shown, as airsup's follow mode does, with the cut
  faces barely touched. Also the Task 4 foam-cap finding: cells 2.5× finer, weaker walls, a clean pale
  face.
- Direction of travel: lift runs skin to cap as exported; bending and shear segments start at the root,
  so they are reversed and pulses run toward the root.
- The colour e2e samples pixels along each projected path; the crew checked it fails with the cut's
  clipping disabled in flow.ts. Its thresholds are unchanged.
- No path legend yet (2.1 had one); lift segments are 3 in long, so each shows about one pulse.
- Commit b7a1149. First full run: 1 failed (`test_the_section_cut_clips_load_paths_and_the_flows_are_drawn_in_their_own_colours`,
  the strongest pixel near the web flow was (255,255,255)). Cause: the lab tests froze the sim clock only
  after the page had run for a load-dependent time, so the pulse phase differed per run and a white-hot
  pulse head sat on the sample point. Fix: the lab e2e opens with `?freeze=1`, so the clock starts frozen
  and every frame is reproducible. Thresholds unchanged.
- Captain stalled here for about 5.5 h waiting on a backgrounded suite whose notice never arrived (the
  lead caught it). From here, waits run in the foreground.
- Verify (captain, unpiped, split because the Bash tool caps a foreground call at 600 s and another lane's
  `node phase2.mjs` held the load average at 40–67): lab e2e + build_site 43 passed (933 s under load);
  everything else 597 passed, 2 skipped, 9 xfailed (386 s). Total 640 passed, 0 failed. lab 60/60,
  typecheck clean, node 50/50.
- Screenshots: `t5-grid.png` (sonnet) and `t5b-*` (opus) against airsup's pump. After the escalation the
  flows read as neon threads with moving comet heads at the op shots and as glowing streaks across the
  cut close up; the web flow is a blue beam into the B.L. 10 section. Short of airsup: theirs are volumes
  of glowing fluid in dark metal so the whole machine glows; ours are thin threads on a pale laminate,
  and the halo comes mostly from our darkened band (global bloom 0.06 is too weak for thin lines), which
  leaves a faint dark outline up close.

## Task 6: director tour and film (336bb36)
- Crew: sonnet implementer, then a sonnet fix round on the captain's findings.
- Captain's findings from the first film's frames (`film/fr/grid.png`): the tour turned Part names and Load
  paths on through the normal handlers, so the setting persisted in localStorage (2.1's rule is that a
  tour never writes storage and restores what the user had); and the closing orbit showed the cut canard
  small and far away behind the removed half's empty jig blocks.
- Fixes: a tour-scoped override for paths/labels and a section snapshot restored on any stop; an e2e counts
  `Storage.prototype.setItem` calls during a tour (0). The ending is now a 9 s, 40° close orbit of the cut
  face at B.L. 20.
- Review Focus 4: frames 0, 120 and 240 of two independent runs are byte-identical on swiftshader (e2e);
  no 1% fallback needed. The recorder disables CSS transitions; nothing reads wall-clock or Math.random
  at render time.
- Deviations: during a tour the build clock runs 2.5× (`TOUR_BUILD_RATE`) to fit the film in ~90 s; a
  canvas drag also stops the tour (not in 2.1's list); 2.1's "leaving the 3D pane" stop has no lab
  equivalent (there is no other pane). `playwright` is a devDependency of the lab and reuses the
  Chromium the Python tests installed.
- **Film:** scratchpad `film/canard-ch30.mp4` (outside the repo): 89.75 s, 1920×1080, 60 fps, 127 MB,
  rendered in 5 min 11 s on the Metal GPU path with
  `npm --prefix guide/lab run record -- canard <out.mp4> 60 http://127.0.0.1:<port>/lab/`.
- Verify (captain, unpiped): lab 68/68; typecheck clean; node 50/50; full suite 645 passed, 2 skipped,
  9 xfailed in 802 s (the tool moved it to the background at 600 s; the captain blocked on it in the
  foreground).
- Frames (`film/fr2/grid.png`) against airsup's pump: the title card over the home shot, the ply lay-down,
  the section drag with the cursor on the real slider, and the closing orbit of the layered cut with
  comet flows all read as one lab with airsup's grammar (cursor, cards, DOF, glow). Short of airsup: the
  subject is a long pale slab, so mid-film frames are mostly plain laminate with little contrast; the UI
  overlays (top bar, tiles, step card, chip bar) are heavier than airsup's and crowd 1080p frames; the
  ops without plies are dwell shots with nothing happening.

## Task 7: quality tiers and budget (79ea865)
- Crew: sonnet implementer. Captain made one test change (below).
- Tiers (`quality.ts`, unit-tested): high (AO 8, DOF, bloom, MSAA 4, DPR cap 2, 4096 shadows), mid (AO 6 at
  0.4 scale, no DOF, bloom, MSAA 2, cap 1.5, 2048 shadows), low (flat baked key + sky/ground light in the
  surface shader, no shadows/env/AO/DOF/bloom, no weave or cell detail, MSAA 0, 0.5 MP ceiling, adaptive
  resolution that only shrinks). Auto: drop one tier when the 1.5 s median exceeds 34 ms (33.3 ms on a
  30 Hz display is not "slow"), first 3 s and 1 s after a drop ignored, never steps up by itself; a
  High/Med/Low/Auto control shows and overrides it. Off under `?q=`, `?freeze=1`, `?rec=1`.
- Review Focus 5: the 2.1 drag test is ported at **33 ms, unchanged**: medians 16.7 ms on three runs
  (load 4–6), 109–121 distinct stations, 63 draw calls, 17,625 triangles.
- **Lead, read this.** The low tier meets the headless budget only because its adaptive resolution
  shrinks the canvas to 70k–125k pixels (about 8–13% of 1180×820). The crew measured swiftshader at
  67 ms per frame at 0.5 MP even with three's plain MeshStandardMaterial, so the software rasteriser's
  fill rate, not our shaders, is the wall. The test honestly proves the step-down machinery and the cut
  path; it says little about the iPad, which is the owner's walk-through. The number was not raised.
- Captain's fix: `test_auto_step_down...` failed once in a full-file run with 0 draw calls after the
  drops; three reruns alone passed. three.js skips drawing while the GL context is lost, and the test
  had just rebuilt the tier and shrunk the resolution back to back, so a swiftshader context loss is the
  likely cause (not confirmed). The test now redraws until a frame lands (10 s cap) instead of reading
  one frame. Same assertion (> 20 calls). **iPad risk:** Safari drops WebGL contexts under memory
  pressure; the high tier's MSAA-4 half-float targets and 4096 shadow map at DPR 2 are heavy. The lab
  has no context-lost message yet.
- Verify (captain, unpiped, split at the 600 s tool cap): lab e2e + build_site 51 passed (197 s); the
  rest 599 passed, 2 skipped, 9 xfailed (313 s). Total 650 passed, 0 failed. lab 84/84, typecheck clean,
  node 50/50.
- Screenshots `t7-*` (1180×820, GPU): high and mid look alike except DOF; low is the same lab (lit,
  ply colours, cut layers, flows, labels) but flat and aliased with no shadows or weave. **Finding for
  Task 8:** at 1180×820 (the iPad size) the UI now buries the canard: the control card wraps to two rows
  and the readout dock plus step card cover the left third, including most of the canard in the home
  shot. That is the opposite of airsup's layout and is fixed before the switch-over.

## Task 8: parity and switch-over (b6ec71b, 927401d)
- **8a UI pass (b6ec71b), opus crew.** Why opus: the Task 7 captures showed the UI burying the canard at
  1180×820 (a two-row control band across the top, a readout dock plus step card over the left third),
  a layout taste call the owner judges first. Result: one ~400 px control card top-right (variant, home,
  tour, a Display popover for labels/paths/future work/quality; Play + ply scrubber; cut + slider), one
  bottom-left card with a row of stat tiles, a truncated layers line and a collapsible step. Every id kept.
  An e2e holds each card's overlap with the canard's projected box under 10% at 1400×860 and 1180×820
  (home and top skin) and 300 px of clear canvas at 390×844. Measured largest overlaps: home 0–0.3%,
  op shots 5–9%.
- **8b parity and switch (927401d), sonnet crew then a sonnet fix round.**
  - Every Block 2 M2.1 test in test_viewer_e2e.py is mapped to a lab test (existing or newly ported) or
    marked not applicable (isolate, ply dock, cutaway/glance pane, light/dark schemes: M2 or classic-only
    features). The mapping table is in the report. The M2.1 tests were then removed from the classic
    file; the M1/M2 tests stay against `/classic/`.
  - Captain's findings from the crew's own "needs your call" list, both fixed as parity regressions:
    the lab tour was hard-wired to chapter 30, so GU played an empty film (now 2.1's rule: selected op's
    chapter, else the variant's first chapter, stub-only falls back; the three 2.1 tests ported); and
    the ported touch tests asserted 40 px where 2.1 asserted 44 (the lab now uses 44 px on coarse
    pointers and the tests assert 44).
  - Switch-over: the lab dist is the site root, the viewer is at `classic/` with a
    `<meta name="data-base" content="../">` that app.js reads for its data URLs (the only logic touched);
    one copy of graph.json, config.json, models/, docs/ at the root; `/lab/` removed (no redirect).
  - One lab engine fix found by a ported test: stopping a tour now also stops the Play the tour pressed
    ("stopping leaves no animation").
  - Test lean-up: one chromium per module in test_lab_e2e.py. Suite 13.4 min → 5.5 min.
- Verify (captain, unpiped, one foreground run at load ~5): **618 passed, 2 skipped, 9 xfailed in 333 s**;
  lab 87/87; typecheck clean; node 50/50. `guide.check` not run: this checkout has no `.env` and the
  private sources it checks (CP file, cobelu, scan_text) are absent.
- Captures `t8a-*`, `t8b-*`, `t8c-root-*`: `/` is the lab with the canard clear of the cards at iPad
  size; `/classic/` is the old viewer with its model loaded.
- Leak grep over guide/lab, build_site and the lab tests (home paths, /private/tmp, tailnet IPs, the
  banned phrase, airsup brand/fonts): clean.

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
