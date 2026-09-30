# Block 2 milestone 2.1b: the lab engine

Status: owner direction 2026-09-30 ("look at the complexity of the video rendering... this isn't
it"). The design and plan are approved by the lead under the owner's delegation.
Parent: `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md`.

## 1. Intent

Milestone 2.1 made the rehearsal work but left it rendering like a default web page. The owner
walked it on the iPad and judged it rudimentary. The bar is the airsup.ai lab, for example its
turbopump:
- a full-bleed lit scene with an environment;
- physically based materials, ambient occlusion, bloom, tone mapping and depth of field;
- animated flows inside the cutaway;
- in-scene part labels with leader dots;
- a live readout panel;
- compact controls.

This milestone rebuilds the viewer on airsup's engine (MIT, `AirsupHQ/airsup-lab`) instead of
imitating it. The build logic and data from milestone 2.1 become the content that engine shows.

## 2. What the owner sees (the canard chapters)

- **A workshop scene, full-bleed.** The canard sits on its jig blocks on a build table, lit like a
  shop, with a softly blurred background. It is framed large, like airsup's pedestal exhibits. The
  UI floats over the scene.
- **Materials you can tell apart:**
  - foam, with visible cell texture;
  - UND and BID glass, each with its weave running in the ply's orientation;
  - wet epoxy, glossy and translucent, which turns into cured laminate;
  - flox and micro fillets where the graph names them.
- **The build is animated.** A ply rolls out along the span, wets out as the squeegee pass sweeps
  across it, then cures. The scrubber drives the same animation. Future work can still show as a
  ghost.
- **An airsup-grade section cut.** Filled caps show every layer, the foam cells and the laminate.
  The live readout names the station and the layers there.
- **Load paths as flows.** Glowing flow lines move along the spar caps and web, like airsup's
  "follow" mode, and appear only once their parts exist. They are qualitative, with no magnitudes.
- **In-scene labels** with leader dots on the parts (core, shear web, spar caps, skins, lift tabs).
  They follow the camera and hide when their part is hidden.
- **Readout panel.** It shows the step name, the ply count laid so far out of the op's total, and
  the cloth used so far. Any mass figure appears only once the Block 1 ledger sources it; until then
  the panel says "not yet computed" instead of inventing a number.
- **Named camera shots** per operation, and the tour flies between them. The bottom-side ops are
  shot from below the jig.
- **A film.** Using airsup's deterministic recorder, the canard chapter renders to an MP4 at
  60 fps, which the owner can watch or share.

## 3. How it is built

- **Port, don't reinvent.**
  - Vendor airsup's render pipeline (`src/render/pipeline.ts`), materials and noise
    (`src/core/materials.ts`, `noise.ts`), cut (`src/core/cut.ts`), labels (`src/ui/labels.ts`),
    the camera-shot pattern (`src/camera.ts`), the director (`src/director.ts`) and the recorder
    (`tools/record.mjs`) into `guide/lab/`, a TypeScript and Vite app.
  - Every adapted file keeps an attribution header, and `NOTICE` carries the MIT text.
  - Their exhibits, brand, fonts and hall scene are not copied. The workshop scene is our own.
- **Content stays ours.**
  - Geometry comes from `guide.export_glb`, from the config and CadQuery.
  - Build state, section layers and tour order come from the milestone 2.1 pure modules
    (`build.js`, `section.js`, `tour.js`), ported to TypeScript with their node tests kept.
  - Load paths and tours come from `graph.json`.
- **The engine is added at `/lab/`; the old viewer is not removed yet.** The milestone 2.1 viewer
  stays at `/` until the lab reaches parity with every tested behaviour. Then `/` switches over,
  and the milestone 2.1 e2e suite is re-pointed at the lab.
- **Deterministic time.** The simulation advances only through `step(dt)`, as in airsup, which is
  what makes the recorder and the tour tests exact.
- **Quality tiers.** Ambient occlusion, depth of field and bloom have a low tier for weak devices.
  The iPad starts on high and drops a tier if frames run long. The e2e frame budget stays at 33 ms
  median on the low tier in headless mode.

## 4. Acceptance

- **Visual.** Side-by-side screenshots of the lab canard and the airsup turbopump, at the same size
  and in both light and dark scenes, are put in front of the owner. The lead does not grade the
  look alone.
- **Owner walk-through.** On the iPad, the owner judges whether it now meets the bar.
- **Behaviour.** Every milestone 2.1 behaviour passes on the lab:
  - build state, the scrubber, ghost mode;
  - the section readout and its parity with `layup`;
  - paths gated by build state and clipped by the cut;
  - tour order.

  The existing tests are ported, not dropped.
- **Film.** The canard-chapter MP4 renders deterministically, meaning two runs produce identical
  frames at the same frame numbers.
- **Hygiene.** Attribution headers and `NOTICE` are present. There are no airsup brand assets and
  no plans text.

## 5. Out of scope

Chapters beyond the canard, the whole-airplane scene, load magnitudes, and any sound.
