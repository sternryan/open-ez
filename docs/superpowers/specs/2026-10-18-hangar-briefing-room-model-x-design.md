# The Hangar, the briefing room, and the Model X restomod

Status: design, from the owner brainstorm of 2026-10-18. Not yet approved.

## 1. Intent

The roadmap (`2026-09-29-roadmap-same-airplane-new-process-design.md`) ends in a Long-EZ the owner trusts
with their life: the book's outer shape, weights and CG envelope, built with a modern process and modern
systems. The rehearsal player (`2026-10-17-build-rehearsal-player-design.md`) is rebuilding the 1980 book
airplane as data. This design covers the step after that: **customizing** the airplane, so that it is
built the way it would be built today, while it keeps the full record of how the original got there,
including what was tried and dropped.

The owner's picture of the finished airplane: 3D-printed prototypes and plugs, molds cast from them,
vacuum-bagged glass and carbon in place of hot-wire foam and moldless glass, and a modern powerplant.

How the owner wants it to feel: **every piece of information should read as if a real team had
researched it**, people educated from the foundations of their field to its frontier. The backbone
(sources, the book's reasoning, the dropped options) is always there, but the owner looks at the skin:
a recommendation, a sentence or two of why, and a confidence. The owner should never have to read the book
material to make a decision.

### 1a. The Hangar

The top level is **the Hangar**, the aviation version of a car enthusiast's garage. Each airplane has
a spot in it:

| Spot | What it is | Car-world analogue | State in this design |
|---|---|---|---|
| 1980 Rutan Long-EZ (Model 61, plans Section I, March 1980 first edition) | the book airplane, built exactly as the plans say: the knowledge foundation | concours restoration | exists as the rehearsal player; unchanged |
| Stern Model X (working name; the owner names it) | the modern Long-EZ: the same shape with a modern process, powerplant and systems | restomod | **designed here** |
| Van's RV-12 | the second airplane the code is proven on | kit car | reserved spot |
| Stern Model 1 (bikeboatplane) | the owner's own design | scratch build | reserved spot |

The Hangar is a frame, not a new product. Two things are shared by every spot: the **shop** and the
**briefing room** (section 3).

## 2. Goals, non-goals, anti-goals

**Goals**
1. A Hangar index that shows the four spots. The Long-EZ spot opens the rehearsal player, the Model X
   spot opens its decisions, and the reserved spots say what they are and that they are reserved.
2. A **decision record** for every departure Model X makes from the book, which traces back to the
   book steps it replaces and to its sources (section 4).
3. A **briefing room** where the owner talks a decision through with an advisor council and closes it
   (section 3).
4. Model X's first decision, **powerplant + fuel + tank resin**, run through the briefing room end to
   end (section 5).
5. A Model X path through the shop: the player shows the Model X build, swapping in each decided
   departure, and marks the steps whose decisions are still open.

**Non-goals**
- The RV-12 and Model 1 spots beyond their reserved placeholders. The engine is made general by pulling
  it out for a concrete second airplane when that airplane's turn comes, not by designing it generic up
  front (owner, 2026-10-07).
- The council's ideas-generator mode for Model 1 ("bring your own idea"). It is named here so the
  council isn't designed in a way that forbids it, but it isn't designed.
- Changes to the outer shape or aerodynamics. The roadmap's out-of-scope list still applies to Model X,
  except for a cowl change the engine forces, which must be called out and analysed.
- Any change to the book build. The Long-EZ spot keeps the book engine, the book fuel and every book step.

**Anti-goals (what would make this a failure even if it works)**
- The shop turns into a debate. In the shop it is time to execute, not discuss.
- The council improvises: a number or a claim with no registered source behind it, presented with the
  same confidence as a sourced one.
- The council papers over a gap, or hides a disagreement between advisors, to give a tidy answer.
- A decision reached in the briefing room silently changes later, or the shop shows something the
  owner never decided.
- The owner has to read book pages to make a decision.

## 3. Two rooms: the shop and the briefing room

**Shop: execution.** This is the rehearsal player as it exists: steps, materials, cure times, the
gloves. In the Model X path it shows *what was decided*, never the debate. A step changed by a decision
carries a small marker (for example "UL350i, decided in briefing 3") that the owner can tap to jump to
the record. A step whose decision is still open shows **awaiting briefing** instead of guessing.

**Briefing room: deliberation.** The owner talks an open decision through with the council. The
briefing room fits where the player's optional ground school already sits: a place the owner visits
around the build, not a phase to pass through. Decisions are closed only here and reopened only
here.

### 3a. The council

A fixed set of advisor roles, each speaking from foundations to frontier in its field:

| Role | Covers |
|---|---|
| Propulsion | engines, propellers, cooling, the thrust line |
| Structures and composites | laminates, molds, cure, the trust standard's structural evidence |
| Fuel and systems | fuel types, tanks, lines and pumps, electrical, avionics |
| Aerodynamics and flight test | performance, handling, CG, the Phase 1 program |
| Plans historian | what the 1980 book did and why, the Canard Pusher changes, and the options that were dropped along the way |

How the council behaves (each of these is testable):
1. **It cites.** Every factual claim comes from a registered source (`data/sources/registry.yaml`) or
   from the plans graph. A claim with no source is shown as the advisor's judgment and labeled as such,
   never as a fact.
2. **It says "unknown".** A value no source gives (for example a published ethanol limit for an engine)
   is reported as unknown, with what it would take to find out.
3. **It disagrees out loud.** When advisors disagree (the fuel lead's pick worries the composites lead
   because of the tanks), the record keeps both positions.
4. **It names couplings.** When one choice constrains another (fuel and tank resin are one decision),
   the council says so and the decision is taken as a group.
5. **It answers against the yardstick.** Every powerplant or systems recommendation is scored against
   the mission in section 5a.
6. **It does not grade its own evidence.** The council writes the paper case. The roadmap's trust
   standard (material tests, outside review, flight test) still has to clear it.

The skin the owner sees for each decision is the same shape every time: the recommendation, a
sentence or two of why, a confidence, the disagreements, the unknowns, and a way down into the
backbone.

## 4. The decision record

One record per decision, stored as data in the repo (format is the builder's call; YAML beside
`guide/graph/` is the natural fit). Fields:

- `id`, `spot` (`model-x`), `title`, `status` (`open` | `decided` | `reopened`)
- `question`: what is being decided, in one sentence
- `coupled_with`: other decision ids taken together
- `replaces`: the book steps and parts (plans-graph ids) this departs from. Every Model X departure
  must name at least one book step; that is what keeps the lineage.
- `book_choice`: what the 1980 book did and the book's reason, with citations
- `options`: every option considered, **including the book's choice and the dropped ones**, each with
  its sourced facts and why it was kept or dropped
- `positions`: each advisor's recommendation, confidence and reasoning; dissent is kept, not merged
- `unknowns`: what no source gives, and how it would be found
- `mission_score`: the option scored against the yardstick (section 5a), with stated assumptions.
  *(Designer's call:)* computed by a deterministic mission calculator built on the existing mass/CG
  ledger and analysis modules (installed weight and CG shift, cruise power, fuel burn, range, VFR
  reserve), never written by the council. The council cites its output. An option with no published
  fuel flow gets an estimate from a stated method, flagged `derived`, or `unknown` when no method
  applies.
- `decision`: the owner's pick, the date, and the reason, in the owner's words. Empty until closed in the
  briefing room.
- `changes`: what the decision puts in the shop. A structured patch against the plans graph: the book
  steps it removes, and the substitute steps, parts and materials it adds. Substitute content follows
  the same provenance rule as book content; for the powerplant that means the manufacturer's
  installation manual, cited. *(Designer's call: the shop shows real Model X execution, not only a
  marker on the book step, because the shop is where the owner understands the execution.)*
- `evidence`: where the decision stands against the roadmap trust standard (paper, material, outside
  review, flight). A decided record is a design choice, not a trusted part.

Gates (each must be shown to fail on a broken input, per the roadmap):
- A record that cites an id missing from the registry fails.
- A Model X record with an empty `replaces` fails.
- A shop step tied to an `open` or `reopened` record renders **awaiting briefing**, never a default.
  When several coupled records touch one step, the step shows "awaiting briefing" if any of them is
  open or reopened, and otherwise lists every decided record in its marker.
- A `decided` record can't change its `decision` without going back to `reopened` first, and that
  transition records a date and a reason.

## 5. Model X's first decision: powerplant + fuel + tank resin

The roadmap ruled "Rotax, model open" (2026-09-29). **For Model X the owner opened the door wider
(2026-10-18):** UL Power, hybrid, electric and alternative fuels are all in scope. The roadmap spec
needs a one-line amendment saying so.

**Owner constraints (2026-10-18)**
- **No 100LL.** It is being phased out, so Model X does not design around it. Mogas or electric only;
  unleaded aviation gasolines count as "not 100LL".
- The Long-EZ spot keeps the book engine and 100LL as the foundation.

### 5a. The yardstick mission

- A round trip with a leg of about 300 nm, two adults (about 310 lb together), light overnight bags
  only (toiletries and sundries).
- Fly it at the best combination of speed and fuel efficiency, with VFR reserves.
- The stretch case is the same trip at the longest possible range.
- The actual airports and people stay out of the repo (public-repo hygiene); they live in the owner's
  private notes.

### 5b. First research, to be registered before the council cites it

A sourced research sweep, made 2026-10-18, carries a URL for every number. It is public material only
and is handed to the builder as `docs/research/2026-10-18-powerplant-sweep.md` (committed with this
spec). It has not yet been spot-checked. Each fact the council uses must first be registered in
`data/sources/registry.yaml`. The registry already takes web pages (the Wicks product-page entries:
`edition` records the page and the date read; the citation has no page number). The spot-check is
done by a different model or method than the one that made the sweep, never by the builder of the
record. Its findings, as leads:

- **UL Power UL350i:** about 173 lb ready to fly vs about 252 lb for the book O-235. It makes 118 hp
  direct drive, ram-air cooled, with no radiators, and runs on mogas at 91 AKI minimum. Its ethanol
  limit was not found.
- **Rotax 912 iS / 915 iS / 916 iS:** approved for mogas up to E10. The 912 iS has the only published
  fuel flow that fits the derived cruise power: about 65 lb of fuel for the mission.
- **Diesel (DeltaHawk):** about 335 lb at the tail, the wrong direction for this CG. A candidate to drop.
- **Electric:** doesn't close the mission. At a claimed 500 Wh/kg cell, about 600 lb of cells before
  pack structure. The flown electric Long-EZ pack was about 151 Wh/kg. Record it as considered and
  dropped for now, with the numbers, so it can be reopened when cells improve.
- **Hybrid:** no homebuilder kit with a published price was found. Considered, not available.
- **Fuel, coupled to tank resin:** the Long-EZ owner's manual warns that autogas can dissolve the
  epoxy in the fuel tanks, and safety bulletins say the same of ethanol. Two paths:
  (a) ethanol-free unleaded (Swift UL94 is sold today), which may keep a conventional tank resin;
  (b) E10 mogas, which needs a fuel-resistant tank resin (the rehearsal's open
  `fuel-resistant-tbd` placeholder; E-Z Poxy is the leading candidate) plus attention to vapor lock in
  a pusher's hot engine bay.

**What this decision feeds next:** the propeller (it follows the engine), cooling and the cowl, the
fuel system architecture, and CG ballast. Each becomes its own decision record, coupled to this one.

## 6. Relationship to the roadmap

Model X isn't a new phase after the roadmap. It is roadmap Blocks 3 to 6 seen as one airplane:
- Block 3 (equivalence engine) supplies the paper case for structural departures;
- Block 4 (process lane) holds the printed plugs, cast molds and vacuum-bagged layups;
- Block 6 (engine and systems) is where section 5 sits.

The decision record is the frame that makes them one design. Model X records for process changes (for
example "printed plug + cast mold instead of hot-wire foam" for a part) follow the same schema as the
powerplant one.

## 7. Phasing

1. **H1: records and the Hangar index.** The decision-record schema and its gates (section 4); the
   Hangar index with four spots; the powerplant + fuel + tank resin record created as `open`, its
   options and sources filled in from section 5b once registered.
2. **H2: the briefing room for one decision.** The council over that one record: the owner talks it
   through and closes it. Done when the owner has closed it in the briefing room and the record shows
   the decision and reason.
3. **H3: Model X in the shop.** A Model X path through the player that applies decided records,
   shows markers, and renders "awaiting briefing" for open ones.

**Dependencies.** H1 and H2 need only `main`. H3 depends on rehearsal player phases 1 and 2
(`feat/rehearsal-p1`, `feat/rehearsal-p2`), which were not yet merged on 2026-10-18; it starts after they
land, against their plans-graph step ids. The "hangar bay" rename (section 8) waits for the same landing.

Later, each by the owner's word: more Model X decisions, the RV-12 spot, Model 1 and the ideas
generator.

## 8. Constraints

- **Public repository.** No owner or family names, no airports or addresses, no personal weights
  beyond the abstract mission, no lane or host names. Private mission notes and any owner chat
  transcripts from the briefing room never enter the repo, the same rule as the room scan and owner
  actuals.
- **Sources.** The project's provenance rule applies unchanged: registry ids, page or URL citations,
  and visible flags for anything unsourced.
- **The book build is untouched.** No Model X work changes the Long-EZ spot's data or steps.
- **Models.** The council is the only part that needs a language model. It runs only when the owner is
  in the briefing room, never on a timer. Shop content stays fixed data, so the shop works with no
  model at all.
- **Where the briefing room sits (owner, 2026-10-18):** inside the player, as part of one
  self-contained app, not in a chat tool. The public static site keeps working with no backend: there
  the briefing room shows decided records read-only. Talking to the council needs a small companion
  service the owner runs privately (tailnet-only, never public), which serves the model calls, keeps
  transcripts off the repo, and writes record updates for the owner to commit. The shop's
  "decided in briefing N" marker opens the room on that record.
- **Naming.** The rehearsal player has a workspace called "hangar bay". Rename it (for example "rental
  T-hangar") once phases 1 and 2 of the player land, so it never collides with the Hangar.

## 9. Left to the builder

- The record file format and location, and how records join the plans graph.
- How the council is implemented: one model playing the roles, or one call per role. Prompt design.
  Which model lane serves it, following the project's cheapest-capable-lane rule.
- How a conversation becomes a record update (the owner should not have to hand-edit YAML).
- The Hangar index's look; it should match the player's.
- The Model X path's mechanics in the player (overlay on the book DAG vs a derived DAG).

## 10. Open for the owner

- The Model X name.
