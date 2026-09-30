# Block 2: Rehearsal complete

Status: design approved in conversation 2026-09-30, pending written review.
Roadmap: `docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`, Block 2.

## 1. Intent

The owner can rehearse the whole Section I build in the browser and understand it:
- what is built at each step;
- how the plies go down;
- what the structure looks like inside at any station;
- how loads travel through it.

Along the way, the book airplane becomes data (ply schedules, materials, per-part mass) that closes
the Block 1 mass/CG ledger.

The visual bar is the airsup.ai lab (MIT-licensed, `AirsupHQ/airsup-lab`). The product shape is
different: airsup shows finished machines, and this shows a build in sequence.

## 2. Milestones

| # | Milestone | Proves |
|---|---|---|
| 2.1 | **Build progression, canard chapters** (ch 10 GU, ch 30 Roncz, ch 12 install) | the rehearsal interaction works at the visual bar, on existing content |
| 2.2+ | Remaining Section I chapters, in build order, one spec each | coverage |
| 2.n | Ledger closure | per-part mass from geometry and ply schedules closes on the manual's empty weight and CG |

Milestone 2.1 is specified here. Later milestones reuse its viewer and get their own short specs.

## 3. Milestone 2.1: build progression

### 3.1 What the owner sees

- **Build state at the selected operation.**
  - Everything completed in earlier operations is solid.
  - The current operation's plies are highlighted.
  - Future work is hidden by default, with a toggle to show it as a faint ghost.
- **Ply scrubber.** Within an operation, a scrubber lays that operation's plies in lay order
  (animated, or stepped by hand).
  - The plies it steps through are the ones the operation's `materials` list (for example 4 BID
    plies for the top skin) and the layup geometry give it.
  - The existing lay-order numbers stay on the section.
- **Live section plane.** A plane the owner drags along the span, by touch on iPad, cuts every
  visible layer and shows filled caps.
  - Foam and each ply read as solids, and the cap colours follow the existing legend (UND, BID,
    foam, unverified striping).
  - A readout names the station (B.L.) and lists the layers cut there.
  - The pre-rendered Blender heroes stay as share-quality stills, and stop being the main view.
- **Load-path lines.** Glowing lines, in the style of airsup's flows, show how load travels through
  what has been built so far. Examples: lift from the skins into the spar caps, bending along the
  caps to the lift tabs, shear through the web.
  - A line appears only once every part it passes through exists.
  - Each line is labelled qualitatively ("bending", "shear"). It shows no magnitudes until Block 3
    computes them.
- **Tour.** Each chapter gets a scripted camera walk through its operations, driven by a
  deterministic step function so it can later be recorded to video.

### 3.2 Deferred on purpose

- The CG control. CG only means something once the canard sits on the airplane, so it arrives with
  the fuselage and install chapters.
- Exploded views, unless the owner asks for them.
- Load magnitudes, which belong to Block 3.

### 3.3 How it is built

- **Geometry.** The per-ply meshes `guide.export_glb` already exports are tagged in the glb with
  `op` (operation id) and `lay` (lay order within the op).
  - A test checks that every ply mesh has both tags, and that every operation's `materials` ply
    count matches its tagged meshes. Where the plans give "as required" (spar caps), the rule is
    stated in the export.
- **Build-state function.** A pure function, `visibleSet(graph, opId, layIndex)`, returns which
  meshes are solid, highlighted, ghosted or hidden. It is unit-tested in node, so the rules can't
  silently drift.
- **Section cut.** A three.js clipping plane with stencil-buffer caps, adapted from airsup's
  `core/cut.ts` with attribution in the file header and a `NOTICE` entry.
  - Thin plies are capped as solids, not left hollow.
  - The station readout comes from the plane position and the model's B.L. frame.
- **Load paths.** A small data file per chapter lists each path: its parts, and polyline anchor
  points in model coordinates. The viewer draws a path only when `visibleSet` says every part on it
  is built.
- **Tours.** A data file per chapter lists camera shots per operation. The tour steps through them
  using the same state function.
- **Rendering stays in the browser.** No GPU job is needed per change. The Blender render cache
  and deploy check continue for the stills.

### 3.4 Performance and device

- The target device is the owner's iPad (Safari).
- The canard's full ply set must hold interactive frame rates while the plane is dragged. A
  performance test on the e2e browser records the frame time with the plane moving, and fails
  above a stated budget.
- Phone width stays usable. The 3D view gets priority, and the section readout collapses.

### 3.5 Testing

Tests cover the parts that can silently lie:
- `visibleSet` for every operation: which meshes are built, highlighted, ghosted and hidden.
- Ply order within each operation matches its materials list.
- The cut's station readout matches the plane position at a known B.L., and cap colours match the
  legend.
- A load path never draws before its parts exist.
- The tour visits every operation, in order.
- Each gate is shown to fail on a broken input first, for example a mesh missing its `op` tag.

## 4. Done when (milestone 2.1)

- On the owner's iPad, every canard operation can be stepped and its plies scrubbed.
- A cut at any station along the span shows the layup at that station, with its readout.
- The load paths follow the build, and each chapter's tour runs.
- The owner can explain the canard build from the rehearsal alone. The owner judges this on a
  walk-through.
- The tests above pass, and each gate has been shown to fail first.

## 5. Out of scope

- The chapters after the canard chapters (milestones 2.2+).
- Ledger closure (milestone 2.n).
- Load magnitudes and any carbon comparison (Block 3).
- Publishing plans content. Operation text stays in the owner's own words and passes `guide.check`.
