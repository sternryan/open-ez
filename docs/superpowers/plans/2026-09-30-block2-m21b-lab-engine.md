# Block 2 milestone 2.1b: Lab Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** rebuild the build-rehearsal viewer on airsup's MIT render engine, so the canard chapters
look and move like the airsup lab.

**Architecture:** a new TypeScript and Vite app at `guide/lab/`, built into `site/lab/`.
- Vendored airsup engine modules (pipeline, materials, cut, labels, camera, director, recorder),
  with attribution.
- Our content: the glb from `guide.export_glb`, and `graph.json` (layup, load paths, tours).
- The milestone 2.1 pure logic, ported to TypeScript.
- The old viewer stays at `/` until the lab reaches parity.

**Tech Stack:** three.js (the version airsup pins), TypeScript, Vite, `node --test` (via tsx or a
compiled build), Playwright e2e, ffmpeg for the film.

**Spec:** `docs/superpowers/specs/2026-09-30-block2-m21b-lab-engine-design.md`.

## Global Constraints

- **Attribution.** Every file adapted from airsup starts with:
  `// Adapted from AirsupHQ/airsup-lab <path> (MIT); see NOTICE.` plus one line saying what changed.
  `NOTICE` carries the MIT text. Their brand, logo, fonts, exhibits and hall scene are not copied.
- **Our look is our own.** The workshop scene, colours and typography are ours. airsup's
  typography stack is fine to match in spirit, using freely licensed fonts only.
- **No plans text** in any data or UI copy. Readout copy is our own words and passes `guide.check`.
- **No invented numbers.** The readout shows only counts and sourced values; anything else says
  "not yet computed".
- **Public repo.** No home paths or tailnet names, never the banned copyright phrase.
- **Commits.** Crew never commit. The captain commits after a green, unpiped run in a separate
  prior tool call. The full suite is `.venv/bin/python -m pytest -q -p no:cacheprovider`, which is
  clean with 0 failed; add lab e2e tests to it. Node tests: `node --test guide/viewer/tests/*.test.mjs`
  plus the lab's own test command. No trailers.
- **Visual verification.** Every visual task ends with Playwright screenshots at 1400×860 and at
  iPad 1180×820. The captain looks at them and compares them with airsup's turbopump page, captured
  the same way (for reference only, never committed). Put both in the log with a one-paragraph
  honest comparison.
- **Don't let the old viewer rot.** It must keep working at `/` until Task 8 switches.

## Review Focus

1. **Ported logic drifting from 2.1.** Expectation: the TypeScript `visibleSet`, `layersAt` and
   `tourSteps` pass the exact 2.1 node test cases.
2. **Looks rich, lies about the build.** An animated ply appears before its op, or the wet-out shows
   on a cured ply. Expectation: animation state derives from `visibleSet` and the scrubber only. It is
   tested at op and lay boundaries.
3. **Caps that disagree with the readout.** Expectation: the 2.1 cap-versus-`layup` parity test is
   ported to the lab.
4. **The recorder isn't deterministic.** Expectation: two renders of frames 0, 120 and 240 are
   byte-identical, or within a 1% pixel difference if the GPU path makes that impossible, with the
   reason stated.
5. **Frame rate collapses on iPad.** Expectation: quality tiers, and a low-tier headless budget test.
   The iPad itself is judged by the owner.

---

### Task 0: Engine skeleton renders our canard

- Scaffold `guide/lab/` (package.json, tsconfig, vite config, `index.html`) with `base: "./lab/"`.
- Vendor the pipeline, materials, noise and cut, with attribution. Add minimal glue: load
  `models/longez.glb` and `graph.json` from the site root, place the canard on a simple pedestal and
  light it with the airsup pipeline.
- `guide/build_site.py` runs `npm --prefix guide/lab ci && npm --prefix guide/lab run build`,
  copies `dist` into `site/lab/`, and adds a test that the site ships `lab/index.html`. If node isn't
  available, the build fails loudly; it never skips silently.
- **Verify** with screenshots, set side by side with the airsup capture. Commit.

### Task 1: Workshop scene and framing

- Our own scene:
  - a build table;
  - jig blocks at the chapter 30 stations the graph names, drawn as simple blocks and flagged as
    representational;
  - a shop backdrop that sits blurred by depth of field;
  - a floor.
- Named camera shots, in the airsup camera pattern: home, plus the ops from `tours.yaml`.
- Full-bleed layout: the canvas is 100% of the viewport. A floating step panel shows the op title,
  our summary text and the checklist. A floating control panel sits top-right. The op navigation is
  a bottom bar, like airsup's exhibit bar. The old sidebars are gone in the lab.
- **Verify** at both sizes, compare with airsup, commit.

### Task 2: Materials

- Foam, with a cell-noise normal and roughness.
- UND and BID glass, with a woven normal map generated in a shader (no bitmap assets). The UND fibre
  direction runs spanwise; BID sits at ±45°, per the `layup.json` orientation.
- Wet epoxy (clearcoat, transmission, gloss) and cured laminate (satin).
- Mesh-to-material mapping comes from the `layup.json` cloth and the component id.
- **Tests:** every ply mesh gets the material its cloth dictates (a unit test on the mapping), and
  screenshots.
- Commit.

### Task 3: Port the 2.1 logic to TypeScript, and the build progression

- Port `build.js`, `section.js` and `tour.js` to `guide/lab/src/logic/`, and run the 2.1 test cases
  verbatim against them (Review Focus 1).
- Wire the build state to the scene: built, current, ghost and hidden.
- **Ply lay-down animation:**
  - A clip plane on the current ply sweeps along the span, which unrolls it.
  - Then a wet-to-cured material lerp runs.
  - The scrubber and Play drive it through `step(dt)`, and the animation phase is a pure function
    of (op, lay, t).
- **Tests:** the phase function at boundaries (Review Focus 2), and an e2e check of the visible set
  after stepping backwards.
- Commit.

### Task 4: Section cut, labels and readout

- airsup's cut with caps, applied to our meshes. Cap materials read cloth colour and weave. The foam
  cap shows cells.
- Port the 2.1 cap-versus-`layup` parity e2e (Review Focus 3).
- **Labels:** airsup's label component, one per part group, hidden with its part.
- **Readout panel:** the station, layers at the station, plies laid so far out of the op's total,
  and cloth so far by type, as counts only.
- Commit.

### Task 5: Flows (load paths)

- Render `graph.loadpaths` segments as airsup flow lines (the glow-line material, speed-animated),
  gated by the build state and clipped by the cut.
- Port the 2.1 gating and clip tests.
- Commit.

### Task 6: Director tour and film

- Port airsup's director pattern into `guide/lab/src/director.ts`. The canard-chapter tour flies the
  named shots, scrubs each op's plies and shows the cut at one station per op.
- Add `tools/record.mjs` (adapted), and `npm run record -- canard out.mp4 60` renders with the
  deterministic step.
- **Test:** determinism (Review Focus 4). Render the film once, and put it in the report, not the
  repo.
- Commit.

### Task 7: Quality tiers and budget

- High, medium and low tiers (ambient occlusion, depth of field and bloom on or off, plus the
  pixel-ratio cap), with automatic step-down on sustained frames over 33 ms.
- **Test:** a headless low-tier median of 33 ms or less while dragging the cut (Review Focus 5).
  Never raise the budget.
- Commit.

### Task 8: Parity and switch-over

- Port or re-point every milestone 2.1 behaviour e2e (build state, scrubber, ghost, section,
  paths, tour, phone width) to the lab.
- When all pass, `/` serves the lab. The old viewer moves to `/classic/` for one milestone, then is
  deleted in the next.
- The full suite is green. Commit.

### Task 9: Owner review (lead)

- Deploy. Put the lab-versus-airsup screenshots and the film in front of the owner.
- The owner walks through on the iPad. Record the verdict and iterate on what they name.
- Grade, leak scan, push.
