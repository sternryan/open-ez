# Build rehearsal player: design

Date: 2026-10-17. Status: design, awaiting owner approval. Scope: the guide's in-browser lab
(`guide/lab/`), the step graph (`guide/graph/`), and new planning data.

This is the full design pass on the guide's UI that earlier notes deferred. Mockups that informed it
(v1, v2, v3) were shown to the owner on a private preview; v3 is the chosen layout and is described in
words in section 4.

## 1. Intent

The owner wants to **chair-fly the whole build**: sit down, press play, and watch the airplane get
built step by step. A god's-eye camera can be moved to any angle. Hands do the work: they move the
materials, brush and squeegee the epoxy, and fit the pieces into place. The owner can let it run like
a tutorial, or step forward at their own pace and stop to look around.

The same timeline is also the **planner**. It answers, for any point in the build:

- when a second person (a buddy) is needed
- which materials and tools are on the bench
- when to buy what, and what it costs ("about $200 here, then you're covered through the canard")
- how many work sessions remain, and how cure waits stretch the calendar

The trigger was a small one. The current chapter navigation is a row of pill bookmarks ("Canard",
"Fuselage") and nothing else. The owner wants a real step-by-step walkthrough, organized by what is being built rather than by
plans chapter (section 4c).

## 2. Goals, non-goals, anti-goals

**Goals**

1. A rehearsal player over the step graph: play-through, step forward and back, and free orbit at any
   moment.
2. Animated work: floating gloves handle the real parts (from the CadQuery model and layup data) and
   tools, step by step.
3. A session-based nav log that replaces the pill bookmarks, with buddy, cure and spend markers
   (section 4).
4. A planning model: per-step people, hours, cure, materials and cost, rolled up into sessions,
   buy points and running totals (section 6).
5. Workspaces and environments the viewer can switch between (section 7). The workspace changes the
   scene; the environment changes the cure model.

**Non-goals**

- Generated video (text-to-video or image-to-video models). The animation is driven by the geometry
  and the step data, so it is exact and consistent.
- Realistic people. No bodies, no arms, no rigging.
- Travel, setup or teardown time in the session model. Workspaces change the visuals and the
  environment, not the logistics (owner, 2026-10-17).
- Choosing or booking a real shop space.
- A scheduler that wants dates. Sessions are the unit; a "weekend" is whatever the builder gets to.

**Anti-goals (it fails even if it works)**

- **Numbers that look sourced but aren't.** A dollar or hour figure with no source and no visible
  "estimate" flag breaks the repo's provenance rule. That is worse than showing "—".
- **Uncanny figures.** A bad human model is worse than no human. The gloves are the answer.
- **A demo reel that drifts from the build.** If the animation shows something the step data doesn't
  say (a ply count, an order), that's a defect, not an artistic choice.
- **Personal data in the public repo.** The owner's room scan, location and actual spend are private
  (section 9).

## 3. What exists today

Build on these; don't replace them.

- **The step graph:** `guide/graph/ch*.yaml`, 229 steps. Each has `requires` (so build order is a
  DAG for free), `components`, `completion` and sources. 101 steps carry `materials` (`cloth`,
  `plies`, `where`). The schema lives in `guide/schema.py` (`OP_KEYS`, `MATERIAL_KEYS`). No step
  records people, hours, cure or cost yet.
- **The lab** (`guide/lab/`, three.js, Vite, adapted from airsup-lab under MIT):
  - a workshop scene: `scene/workshop.ts` (`buildWorkshop`, `ROOM`, `TABLE_TOP_Y`) and `scene/env.ts`
  - a director (`director.ts`) with a timed step list (move, click, drag, act, orbit, cards) and a
    `chapterTour` builder
  - per-chapter logic under `logic/`, including tours, animation timing (`anim.ts`), kinematics
    (`kin.ts`) and materials (`materials.ts`)
- **The site model:** `site/models/longez.glb`, from `guide/export_glb.py`.
- **Blender renders:** `guide/render_cutaway.sh` renders the layup cutaway on a remote GPU host. It is
  run by hand (HITL), and all host details come from environment variables.
- **A hot box:** `docs/harness/block5-coupon-purchase-order.md`, lines 35 to 42. It is an owner-built
  post-cure box, priced at $338.82 (unverified). ⚠ It is sized for coupon panels: the interior is
  0.80 × 0.80 × 1.00 m, built for an 80 °C post-cure. It cannot hold a canard. A part-scale heated
  enclosure is a new item (section 7).
- **Resin in the existing purchase order:** MGS LR 285 with LH 287, priced from a vendor page.

## 4. The experience (v3 layout)

**Left column: the nav log, a vertical stack of work sessions.** This replaces the pill bookmarks.

- Each session is a card: "Session 3 · ~4 h · 👥 buddy". The steps for that sitting are inside it.
- The current session and step are highlighted; finished ones are dimmed and checked.
- Between sessions sit markers:
  - **cure** (dashed): "overnight minimum", "nothing else on the canard until it's done"
  - **buy point** (green): "next kit · $—"
- Each step row carries small chips for the buddy and anything else notable.
- A zoom switch has two levels:
  - **group:** the session cards for the current build group (section 4c)
  - **whole build:** every group collapses to one line, with its buddy, cure and spend markers kept
- The owner rejected a calendar grid of Sat/Sun columns (v2): it took space without adding value.
  Don't bring it back.

**Right column, which gets the larger share of the width:**

- **The 3D view.**
  - Free orbit, zoom, and top and side snaps. X-ray of plies is a later idea (section 10).
  - Transport controls: ▶ play-through, ⏸, ⏭ next step, and speed 1×/4×/16×.
  - A caption line names the current action ("squeegee UND ply 6 of 11").
  - Every step has a default camera that frames its action, so play-through looks directed. Grabbing
    the view takes over. *Builder's call:* whether the camera snaps back to the step's default on
    the next step.
- **The bench panel** under the view:
  - on the bench: materials with quantities, plus tools
  - 👥 why a buddy is needed for this step
  - ⏳ what cure follows

**Top meter:** spent so far, next buy (amount and when), shop hours (done / total), sessions left in
the group. On "whole build" zoom: total cost to date, total remaining, total sessions.

### 4a. Roncz canard only (owner, 2026-10-17)

- The player builds the Roncz canard, now and from here on. It never shows the GU canard steps
  (every `variants: [gu]` entry).
- **One asterisk:** the first canard step carries a single note. It says the first-edition plans
  built the GU canard, and that this build uses the Roncz. It shows once and is not repeated.
- The GU entries stay in the graph files as historical data, with their sources and changes. They
  are hidden in the player, not deleted. *My call.*
- `requires` links that only exist to satisfy GU steps must not leave a Roncz step unreachable. The
  packer works on the Roncz-filtered graph, and a test asserts that every Roncz step is reachable.

### 4b. Optional ground school (owner, 2026-10-17)

- **What it is:** an optional pre-tutorial before the build, covering the plans' introductory
  material: the introduction, shop, tools and materials, and the composite education pieces. The
  player offers it on first launch and lets you skip it. It is always reachable from the top of the
  nav log.
- **What it does:**
  - **Shop setup:** pick the workspace and environment (section 7). Lay out the bench, tools and
    materials, with an opening shop kit as the first buy point.
  - **Meet the gloves:** introduce the glove pair(s) and the tool props, and show what each action in
    the vocabulary looks like (section 5).
  - **Practice layups:** walk through the education pieces as real step scripts. It runs at a slower
    default speed and has longer captions that explain why, not just what. Their hours, materials and
    cure count toward the totals whether or not you watch them, because a builder makes them either
    way.
- **Graph change:** the education material is a single stub today (`c03.layup-skills` in
  `stubs.yaml`), and every first build step requires it. Ground school replaces the stub with real
  steps, written in our own words and cited to plans pages like every other step. The first build
  steps then require the last ground-school step.

### 4c. One continuous build, grouped by what's being built (owner, 2026-10-17)

- **There are no chapters in the player.** After the optional ground school, the player goes
  straight into the first build step. It then runs the whole airplane as one sequence in build
  order: the `requires` DAG, Roncz-filtered (section 4a).
- **Groups name the thing being built.** For example: seat bulkheads and firewall, fuselage sides,
  fuselage box, roll-over structure and harness, main gear, canard, elevators, and onward. The
  canard is just one group in the sequence, not a separate section.
- **Groups are the unit throughout:**
  - the nav log's group zoom
  - the meter's "sessions left"
  - buy points (kits sit at group boundaries)
  - the whole-build view (one line per group)
  - optional video export (one video per group)
- **Plans chapter becomes metadata.** A step still carries `chapter` for its sources and the
  plans-page citation, and that shows in the step's source detail. It never appears in navigation.
- **Groups follow build order, not the plans' page order.** Where the DAG lets the plans' chapters
  interleave, the groups follow the order the build actually happens in.
- *Builder's call:* how groups are derived (from `components` prefixes, an explicit group key per
  step, or both) and their exact names. Names are in our own words and describe the assembly.
  Assignment must be deterministic and tested so that every step belongs to exactly one group.

## 5. Motion: gloves, tools and step scripts

- **People are floating gloves**, cartoon-style in the spirit of Mickey's but not copies. One pair per
  person. When a step needs a buddy, a second pair appears in a contrasting color. This makes "when
  do I need help" readable at a glance.
- **Parts are the real geometry:** foam cores, each ply in order (from the layup data and
  `materials`), jigs and fixtures. Ply counts, order and orientation must come from the graph or
  layup data and never from the animation (anti-goal 3).
- **Tools** form a small prop set: squeegee, brush, scissors, hot wire, level, sanding block, mixing
  cup, peel ply roll, and a string line for straightness checks.
- **Motion comes from a small action vocabulary.** Each step compiles to a step script made of
  actions:
  - `cut`, `place`, `wet-out`, `squeegee`, `drape`, `flip`, `sand`, `check-level`, `check-string`,
    `bond`, `wait-cure`
  - each action takes a part or ply, a tool, and which glove pair(s) do it
- **Where step scripts come from:** generated from the graph and layup data where they can be (ply
  stacks become place, wet-out and squeegee per ply). Hand-written elsewhere, in a scripts file next
  to `tours.yaml`. *Builder's call:* the file format, and how the scripts extend the director's
  existing `Step` union.
- **Performance:** it must play smoothly on an iPad. That is the shop-side screen.

## 6. Planning model

New per-step data. Every value obeys the repo's provenance rule: a source citation, or a visible
`estimate` / `unsourced` flag. Unknown means "—" on screen, never a guess presented as fact.

- **people:** 1 or 2. Plus a short `why` when it's 2 ("draping the skin").
- **hours:** shop hours, with a source. Candidate sources are published builder logs, which are
  community sources and get the `community` kind. Plans text gives none.
- **cure:**
  - the resin system
  - what cure gates the next dependent step: the minimum before the next step can touch the part, and
    whether other work can continue in parallel
  - cure time comes from the resin datasheet as a function of temperature, so the environment model
    (section 7) can stretch or shrink it
- **tools:** consumables and tools needed, for the bench panel.
- **materials with quantities:** extends the existing `materials` (cloth, plies, where).
  - plies become area through the geometry
  - area becomes cloth length, and resin mass at the ratio the purchase order already uses
  - foam blocks, micro, flox and hardware are listed per step

**Prices** live in a catalog data file: item, vendor, part number, URL, price, and the date it was
read. Line items in the existing block 5 purchase order can seed it. A price older than *N* months
shows as stale. *Builder's call:* N, and the file location under `data/`.

**Sessions** are computed, not authored:

- Steps are packed in `requires` order into sessions of a user-set length (default 4 h).
- A session never continues past a cure gate on the same part.
- A buddy step marks its session as 👥.
- *Builder's call:* the packing heuristic, as long as it is deterministic and unit-tested.

**Buy points** group purchases into kits at build-group boundaries, placed before the first session
that needs them. A kit's total is the sum of its catalog lines. The owner said this matches what
they'd have designed.

**Owner actuals override estimates.** As the owner builds, their logged hours and receipts replace
the estimates for finished steps. Actuals are personal data and are never committed (section 9).

## 7. Workspaces and environments

These are two independent toggles.

**Workspace: the scene.** Three at launch.

1. **Workshop:** the lab's current scene, unchanged.
2. **Living room:** loaded from the owner's own phone LiDAR scan (for example a Polycam export to
   glTF/GLB). It is loaded at runtime from a private path or URL given by environment or config.
   It is never committed and never part of the public site build. The public build ships a generic
   stand-in room, so the toggle still works for everyone.
3. **Hangar bay:** a generic corner-of-a-hangar bay: concrete floor, a large door, a bench, a corner
   of the builder's own where parts stay out between sessions. Generic on purpose. No real location
   is named in the repo.

A workspace sets geometry, lighting, the size of the floor area, and where the bench and parts sit.
It does **not** add time (non-goal). *Builder's call:* whether a workspace also flags fit problems,
for example the canard (141.6 in, about 12 ft: `canard_span` in `config/aircraft_config.py`,
om-1980:p3) against a room's longest clear run. This is cheap and probably worth showing as a
warning chip.

**Environment: the cure model.**

- Inputs: ambient temperature, humidity, and heat source (none, space heater, part-scale hot box).
- Presets include "heated shop", "living room, winter", "unheated hangar, coastal" and "winter
  cellar". The cellar preset is the extreme case, for a builder in a cold basement over a long
  winter.
- The environment feeds cure time per resin from datasheet temperature curves. Below the resin's
  stated minimum, the cure gate shows a warning rather than a number.
- Changing the environment re-flows the sessions and cure markers live. That's the point: you can
  see what a hot box buys you.

**Part-scale heated enclosure** (new item):

- The block 5 hot box is coupon-sized (section 3). Curing a canard needs a tent or box about as long
  as the part.
- In the planner it is a buyable item: cost from catalog lines, and benefit shown as sessions or
  calendar time saved in the current environment.
- Its design and pricing are a separate small task. It is listed here so the planner has a slot for
  it. Until it's priced, it shows as "—".

## 8. Rendering and export

- The browser lab is the primary surface: desktop and iPad.
- **Group videos (optional):** the same step scripts can be exported to Blender on the GPU host
  through the existing render path. That path is HITL-only and never on a timer. *Builder's call:*
  whether this lands in the first phase or later. Recommended later.

## 9. Privacy and public-repo hygiene

open-ez is a public repo. From `AGENTS.md`: no hostnames, IPs, home paths or private locations in
tracked files.

- **Room scans:** loaded at runtime from a path or URL in config or environment. They are never in
  git or in `site/`. The public build uses the generic stand-in.
- **Owner actuals** (hours, receipts): stored locally, in browser storage or a gitignored file. Never
  committed.
- **Location names:** none in the repo. The hangar workspace is generic.
- **Plans copyright:** step scripts and captions use our own words, the same as step summaries today.

## 10. Later ideas (not in the first phase)

These were collected from saved examples of models adding visuals to engineering projects.

- **X-ray / peel the plies:** see the layup inside a finished part, like the X-ray house walkthrough.
- **Follow the load:** animate `loadpaths.yaml` through the structure, like the take-apart rocket
  engine that follows the propellant.
- **Exploded view** with every part named, driven by `components.yaml`.
- **Fit and clearance checks as CI:** does the part fit, and can a gloved hand with a squeegee reach
  it. This is the "design checks as a linter" idea.
- **Step text in ASD-STE100-style controlled English,** the aerospace maintenance writing standard,
  for captions and step text.
- **Style toggles** for the 3D view: blueprint, or IKEA-manual line art for printable step sheets.

## 11. Phasing (my call; owner can reorder)

1. **The first stretch of the build, from step one, in order.** This is the seat bulkheads and
   firewall, then the fuselage sides: about 17 steps, all of them in the continuous sequence
   (section 4c).
   - Why start there: it's where the player starts, it's ply- and bond-heavy enough to exercise the
     gloves and planner, and everything after builds on the same machinery.
   - **Sourcing comes first:** a research task fills hours from published builder logs (kind
     `community`, cited) and the cure curve from the MGS 285/287 datasheet. Then the packer runs.
   - In this phase:
     - build-group nav log with session cards
     - Roncz-only filter (no effect yet, but tested)
     - planning fields on those steps (sourced or flagged)
     - catalog file seeded from the block 5 purchase order
     - glove pair(s) and the action vocabulary
     - workshop scene only
     - environment toggle with that one resin curve
   - Done when the owner can play from step one through the fuselage sides on their iPad and read
     hours, sessions, cost, buddy and cure from it.
2. **Keep going down the sequence,** group by group: fuselage box, roll-over structure, main gear,
   canard (where the one GU note appears), and onward. Whole-build zoom arrives once there's enough
   build to zoom out on.
3. **Optional ground school (section 4b):** replaces the education stub and reuses the gloves and
   action vocabulary.
4. **Workspaces:** generic living room and hangar scenes, private scan loading, presets.
5. **Optional:** Blender group-video export, the part-scale enclosure design, and section 10 items.

## 12. Settled after the builder check (designer's calls, owner to confirm)

- **Hours:** sessions pack on hours flagged `estimate` or `community` with a citation. A step with no
  figure packs as a flagged default (1 h) and shows "—" in the meter. The packer must not be blocked on
  complete data.
- **Cure source:** the resin datasheet's pot-life and cure-vs-temperature figures, registered in
  `data/sources/registry.yaml` like any source. Until then, the curve is `unsourced` and cure gates show
  a warning, not a number. The minimum-temperature warning uses the datasheet's stated minimum.
- **Granularity:** people, hours, cure and tools are per step for planning. A step script may mark
  individual actions as two-person, and the second glove pair keys off that. Sessions never split a
  step.
- **Steps without geometry** (templates, jigs, string checks): simple primitive props (boxes,
  planks, a string line), labeled as stand-ins, are acceptable. A caption-only step is acceptable
  where even that's too much. No detailed jig modeling in the first phase.
- **Schema:** extend `OP_KEYS` and `MATERIAL_KEYS` in `guide/schema.py`, either inline or in a
  sidecar file. Either way, new fields go through `guide.check` and `leakcheck.py`, with no
  bypass. Provenance flags reuse the existing kinds and statuses where they fit (`official`,
  `community`), plus `estimate` and `unsourced` as value flags.
- **Quantities:** per-step quantities are net, with no scrap. The scrap and mixing-loss factor (the
  purchase order's 25%) is applied once, at kit level, and shown as its own line.
- **Partial kit totals:** show the partial sum with "n items unpriced". Never hide the known part,
  and never present a partial sum as the total.
- **iPad bar:** at least 30 fps during play-through on the owner's iPad, checked by hand on the
  device at each phase's end. Desktop Playwright covers function, not performance.

## 13. Left to the builder

- Schema shape for the new per-step fields, and where they live: inline in `ch*.yaml` or in a sidecar
  file.
- Step script format, and how it composes with `director.ts`.
- Session packing heuristic (deterministic, tested).
- Glove model and art direction within the brief: cartoon-adjacent, two contrasting colors.
- Catalog file location and the staleness threshold.
- Tests:
  - packing and kit rollups need unit tests
  - one gate must be shown to fail on a broken input, per the repo rule
  - phase 1 needs a Playwright check that play-through reaches the last step of the stretch
