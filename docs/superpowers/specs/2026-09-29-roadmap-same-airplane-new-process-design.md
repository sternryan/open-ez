# Roadmap: same airplane, new process

Status: approved by the owner 2026-09-29.

## 1. Intent

The end state is a Long-EZ that the owner will trust with his life. It keeps the original outer
shape, weights and CG envelope, but uses a new process and modern systems:
- 3D-printed plugs, cast high-temperature molds and carbon fiber, instead of hot-wire foam and moldless
  fiberglass;
- a Rotax engine in place of the plans' Lycoming/Continental;
- a modern panel, avionics, gear and electrical system.

**Owner rulings (2026-09-29):** the Roncz canard, and a Rotax engine. The Rotax model is chosen
by a fit-and-CG trade (Block 6), not up front.

**Service assumptions (owner, 2026-09-29):** based at KOAK; design for outdoor tie-down (a hangar is
hoped for, not assumed); the airplane travels, so hot ramps elsewhere are in the envelope; paint is
chosen for thermal performance.

**Working epoxy (owner, 2026-09-29): MGS/Hexion L285 with H286 or H287, 80°C post-cure** (the
manufacturer's powered-aircraft schedule; LBA-approved for gliders, motor gliders and powered
aircraft). Design temperature 72–75°C: MGS's 72°C powered-aircraft standard, with a hot-ramp
allowance. After humidity conditioning, MGS gives Tg 78–82°C (H286) and 83–88°C (H287), which
clears the design temperature narrowly. Sources: MGS L285 technical data; EASA CS-22 AMC 22.613(c).
- **First question for the outside reviewer:** is that wet-Tg margin acceptable, with a light paint
  scheme and sun covers as operational mitigations? A common rule of thumb asks for about 28°C of
  margin, which no homebuilder-post-curable system meets. That rule is not yet sourced.
- L285 is a laminating resin, not an infusion resin, so the working process is vacuum-bagged wet
  layup. Infusion for large skins stays open until an infusion system meets the same Tg bar.

The 1970s plans are the baseline and the teacher, not the method. Rehearsing the build the way the
plans describe it surfaces the lessons, and the lessons become the requirements for the new build.

**Why "same airplane":** keeping the outer shape, weights and CG envelope inherits decades of fleet
flight experience for aerodynamics and handling. The burden of proof shrinks to "the new structure
is at least as strong, suitably stiff, and does not change how the airplane flies". One builder can
realistically carry that burden. Changes to the shape (planform, canard, winglets) are out of scope.
They stay candidates that the equivalence tools can evaluate later, each with its own analysis and
flight-test cost.

## 2. The trust standard

A changed part is trusted when all of these hold:
1. **On paper:** analysis shows it is at least as strong as the book part. Where stiffness governs
   flying qualities (canard and wing deflection, flutter), it is matched rather than simply
   maximised.
2. **In material:** standard coupon tests confirm the allowables the analysis used, and the actual
   part passes a proof load.
3. **By others:** a qualified outside reviewer (a composite engineer or an EAA technical counselor)
   reviews the evidence. The builder never grades his own work.
4. **In the air:** a written Phase 1 flight test program (AC 90-89A), with operating limitations
   agreed with the FAA inspector for a structure that differs from the plans.

Gates in software follow the same rule. A gate counts only after it has been shown to fail on a
deliberately broken input.

## 3. One home

open-ez is the single home. Earlier projects by the same author were first drafts of this intent,
and they are harvested rather than continued:
- **Kernels ported in, only as needed:** classical laminate theory, Tsai-Wu failure, the V-n diagram,
  flutter, beam and torsion, the canard neutral point and the CG envelope. Each ported kernel is
  re-validated against published data before anything depends on it.
- **Patterns ported in:** a per-part mass/CG ledger that tags each part's class and process, the
  two-method cross-check where disagreement is itself a failure, and a single parameter source.
- **Not ported:** statistical weight regressions, because they encode aluminum-era construction.

## 4. Building blocks

Each block proves something before the next one relies on it.

| # | Block | Proves | Depends on |
|---|---|---|---|
| 1 | Baseline truth | the book airplane's shape, weight and CG, each value sourced or visibly flagged | nothing |
| 2 | Rehearsal complete | the owner understands how the original is built; the book airplane exists as data | 1 |
| 3 | Equivalence engine | on paper, a changed part matches or beats the book part where it matters | 2 |
| 4 | Process lane | the owner can make what the model says, to the shape it says | 3 |
| 5 | Physical evidence | the paper answers hold in material, and outside review agrees | 4 |
| 6 | Engine and systems (runs in parallel from block 2) | the Rotax installation fits the cowl and keeps CG in the envelope; panel, avionics, gear and electrical fit the budget | 1, then 2 |
| 7 | Build and Phase 1 plan | the airplane is built to the evidence, with a flight test program | 5, 6 |

### Block 1: Baseline truth

- **Geometry.** Every station and planform value is in the published frame, with a source or a
  visible flag. The 2026-09-29 planform correction does the canard and the stations. The wing (span,
  chords, sweep, dihedral) gets the same treatment next.
- **Reference-data audit (first task).** `data/validation/reference_data.json` was assembled in an
  automated planning session in March 2026 without the documents in hand. Its canard entries prove
  the point: they cite "Section IIA, Table 1, p.4 (CP-31)" for a 147 in span and 15.6 sq ft area,
  but those are the code's own original values (147 × the average of an invented 17/13.5 taper), and
  neither number is in the Canard Pusher text. Every entry, including the anonymised builder
  weigh-ins, is re-checked against a document actually held. Anything that can't be found is
  demoted to an unverified claim, and no physics check may treat it as truth. The 15.25 in canard
  chord is that invented taper's average, so it carries no plans information at all.
- **Mass/CG ledger.** One row per part: mass, CG station, class (primary structure, secondary,
  non-structural), process, and source. Its targets are the book's published totals: empty weight,
  gross weight and CG limits.
- **Two-method NP check.** The analytic neutral point and the vortex-lattice neutral point must
  agree within a stated bound. Disagreement fails the build rather than becoming a note.
- **Done when:** every value is sourced or flagged; the NP gap against the published value is
  reported, not fitted; and every gate has been shown to fail on a broken input.

### Block 2: Rehearsal complete

- **Coverage.** Every Section I chapter is rehearsed as operations, the way M1 did the canard.
  - Each operation also records a lesson: why it was done this way then, and the modern equivalent.
- **Extraction as data.** The rehearsal records each part's materials as structured data:
  - ply schedules (cloth type, ply count, orientation);
  - foam type and density;
  - the epoxy system and its cure.

  This extends the canard materials data to every part.
- **Ledger closure (the key gate).** Per-part mass from geometry and ply schedules fills the Block 1
  ledger. The rollup must converge on the book's published empty weight and CG within a stated
  tolerance. If it does not, the extraction is missing something, and that must be found before
  any carbon comparison is trusted.
- **The visual bar.** Held to the standard of the airsup.ai lab (MIT-licensed):
  - a live section cut in the browser (a clipping plane with filled caps), adapted from that lab's
    approach; headless Blender stays for hero renders;
  - load-path and layup lines the viewer can follow;
  - one live control where the build has physics: the CG moving as parts are installed;
  - scripted tours per chapter.
- **Milestones.** First, the visual-bar upgrade on the existing canard chapters. Then the remaining
  chapters, in build order.
- **Done when:** every chapter is rehearsed; the ledger closes on the published empty weight and CG;
  and the owner can walk any chapter on an iPad and explain it.

### Blocks 3–7 (sketch; each gets its own spec when its turn comes)

- **3. Equivalence engine.** For a given part:
  1. compute the book laminate's stiffness and strength (laminate theory, Tsai-Wu);
  2. propose a carbon laminate;
  3. report the deltas in strength, stiffness, mass and CG.

  It flags stiffness changes that could affect flutter or how the canard and wing share load.
- **4. Process lane.**
  - **Step 0, scale prototype (the owner's first prints).** A small-scale model printed directly
    (no molds, no cure, ordinary filament), assembled into a little airplane that only has to fly
    briefly. It exercises the geometry pipeline end to end (sectioning, registration, assembly) and
    shows the shape in the hand. If it flies, it is a cheap look at canard-first stall behaviour and
    CG sensitivity, with the caveat that small-scale Reynolds numbers change airfoil behaviour, so
    it informs but never certifies. Filament purchasing for the mold trial waits until this step is
    done and the mold trial is actually next.
  - **Step 1, filament trial (can start now, in parallel with Blocks 1–3).** Decides "print the
    tool, or print the plug and cast the tool" from the owner's own data, on the owner's printer
    (Bambu P2S: 256 mm cube, 300°C nozzle, passive enclosure up to about 50°C; official list includes
    PC, PET-CF, PA6-CF, PAHT-CF and PPA-CF).
    - Print identical small mold plaques in PETG, ASA, PC, PAHT-CF and PPA-CF.
    - Seal them the same way, then run the chosen epoxy's real cure and post-cure on each.
    - Measure warp, surface transfer, release and porosity.
    - **Pass/fail bar:** the plaque holds shape and surface under vacuum through L285's 80°C
      post-cure. Datasheet heat deflection (Bambu, ISO 75 at 1.8 MPa): PETG 62°C (expected to
      fail), ASA 92°C (marginal), PC 117°C, PAHT-CF 170°C, PPA-CF 196°C. The two CF nylons have
      glass transitions of 70°C and 85°C, close to the cure temperature, so creep over a long cure
      is the thing to measure. Whether the CF values are for annealed parts is not yet confirmed.
    - Expected shape of the answer: printing the tool directly is plausible for small parts; large
      surfaces (many 256 mm sections) likely still favour plug → cast, because registration, bonded
      joints and thermal expansion over the span are the hard problems.
  - Printed jigs, drill guides and incidence blocks, and printed copies of the book's hot-wire
    templates (so the rehearsal can become physical), are in this lane too.
  - Print plugs from the CAD surfaces, sectioned to fit the printer.
  - Seal and fair the plugs, cast high-temperature molds from them, and plan the cure.
  - Check dimensions against the model.
  - The first physical outputs are a coupon panel and a non-structural part, such as a wheel pant
    or fairing, so the process is learned where mistakes are cheap.
- **5. Physical evidence.**
  - Run ASTM coupon tests (for example D3039 tension and D7264 flexure) to establish allowables.
  - Proof-load each primary part.
  - Package the evidence for outside review.
- **6. Engine and systems.**
  - **The engine comes first**, because it is the largest single mass at the tail and sets the CG.
    As soon as the Block 2 ledger closes, swap the book engine's row for each Rotax candidate
    (for example the 912 and 915 families) and check:
    - **CG:** a lighter engine at the tail moves the CG forward. Show the envelope still holds at
      every loading, and say what is moved or added aft to restore it.
    - **Size and cowl:** the engine, gearbox, radiator(s) and intake fit inside the book's cowl
      lines, or the cowl change is called out as a departure from the outer shape.
    - **Pusher specifics:** gearbox and propeller rotation in a pusher, cooling airflow for the
      liquid-cooled heads with no propwash over the engine, and the thrust line's effect on pitch
      trim.
    - **Performance:** power and propeller changes alter takeoff, climb and cruise, so the
      inherited flight evidence covers handling but not performance.
  - Engine weights, dimensions and the pusher installation facts come from the manufacturer's
    installation manuals and are cited, not recalled.
  - Panel, avionics, gear and electrical are mostly purchased, certified parts with a lighter proof
    burden. They feed the same mass/CG ledger.
- **7. Build and Phase 1.**
  - Build to the evidence.
  - Keep a photo and log trail. It doubles as the evidence for the major-portion (51%) rule.
  - Write the flight test plan.
  - Discuss the operating limitations with the local FAA office before first flight.

## 5. Known issues this roadmap must resolve

- **Canard choice: resolved, Roncz** (owner, 2026-09-29). Its span, vortilons and evidence base
  are the baseline.
- **Engine: Rotax, model open.** The engine swap is the one planned change that touches CG and
  possibly the cowl, so it is checked against the ledger before any structural work depends on
  the CG envelope.
- **Carbon-specific risks** the new process must answer:
  - RF blocking (antennas buried in glass structure today);
  - galvanic corrosion at metal fittings;
  - lightning and electrical bonding;
  - repair and inspection methods.
- **Mold accuracy.** Dimensional accuracy over the full span, and the mold's heat resistance at the
  chosen cure temperature. PLA softens at about 55–60°C, so a printed part is a plug, not the tool.
- **Kernel validation.** The laminate kernel has been checked against a single textbook E-glass case
  so far. Before Block 3 relies on it, it needs validation against published carbon and glass data.

## 6. Out of scope

- Changes to the outer shape or the aerodynamics, except a cowl change forced by the engine,
  which must be called out and analysed.
- Certification beyond experimental amateur-built.
- Publishing plans content. The plans remain under copyright, and the repo holds its own words and
  its own code only.
