# Build Rehearsal Player Implementation Plan

**Goal:** A continuous Roncz build rehearsal with floating gloves, session nav, sourced/flagged
planning, optional ground school, and switchable workspaces. Extend the existing graph, lab,
director, geometry and build pipeline. Spec: `docs/superpowers/specs/2026-10-17-build-rehearsal-player-design.md`.

Task briefs below are execution units; shared contracts at the end define their data and signatures.
Do not turn every bullet or test into a model call. No optional Phase 5 work is required for launch.

## Global Constraints

- Public repo. No hostnames, IPs, home paths or location names in tracked files. Room scans and owner
  actuals are never committed and never in `site/` (spec §9).
- Every planning value is sourced (registry citation) or visibly flagged `estimate` / `unsourced`.
  Unknown renders as "—", never a guessed number (spec §2 anti-goal 1, §6).
- Roncz only. No `variants: [gu]` step is ever rendered. There is exactly one GU note, at the first
  canard step (spec §4a).
- No chapters in navigation. `chapter` survives only in a step's source detail (spec §4c).
- People are floating cartoon gloves. A second pair in a contrasting color appears when two people
  are needed. No bodies, no rigging (spec §5).
- Workspaces change visuals and environment only. They never add time (spec §2 non-goals).
- Animation never contradicts step data. Ply counts, order and cloth come from `materials` / layup
  data (spec §2 anti-goal 3).
- Step captions and ground-school text are in our own words. Paraphrase of plans text is limited to
  ten words or fewer (AGENTS.md).
- Performance: ≥ 30 fps during play-through on the owner's iPad. It is checked by hand at each phase
  gate (spec §12).
- Session default length 4 h. A step with no hours figure packs as a flagged 1 h and shows "—" in
  the meter (spec §12).
- Kit scrap and mixing-loss factor: 25%, applied once at kit level as its own line (spec §12).
- A catalog price older than 6 months shows as stale (designer's call for spec §6's N).
- A gate counts only after it has been shown to fail on a deliberately broken input (AGENTS.md).

## Review Focus

The inputs most likely to bite a user, each pinned by a named test in the owning brief:
1. A Roncz step whose only `requires` path runs through a GU step is still present and ordered
   (P1-B `sequence` tests).
2. An environment below the resin minimum shows a cure warning, with no NaN, and still packs
   sessions (P1-B cure and packer tests).
3. A kit with unpriced lines shows the partial sum plus "n items unpriced", never as the total
   (P1-B kits tests).
4. A step with no script or geometry plays as caption-only and never stalls play-through (P1-C).
5. A missing or 404 room scan falls back to the stand-in with a quiet notice (P4
   `test_missing_scan_falls_back`).

## Execution lanes and hard call budgets

- **[script]:** deterministic edits, enumeration, validation, builds and proof capture first.
- **[cursor-grok]:** batch related research, drafting, schema wiring and test authoring into the
  named waves below. Each call has about 14K fixed tokens of overhead: never one call per tiny
  test, value or group. A wave may hand off several prepared atomic local jobs.
- **[conduct] / [hosted]:** atomic only: one file, one exact function signature (or YAML root
  shape), pre-written tests, and an exact focused verify command. For a file with several
  functions, use separate function briefs serially; never let two jobs edit the same file at once.
  Hosted YAML uses the relevant schema tests as its executable contract. No multi-file drafts.
- **[opus]:** one call per real multi-file implementation task below, not per helper or file.
- **[astra]: BULK ONLY. At most 2 calls per phase, including escalations and gate retries.**
  Call 1 grades the entire final phase diff + sourcing record + screenshots. Call 2 is reserved
  for one consolidated re-grade after fixes. No per-task, per-value, per-group, integration-only,
  glove-only or scene-only Astra calls. If still failing, stop and report; no third call.
- Phase budgets: **0: 0; 1: ≤2; 2: ≤2; 3: ≤2; 4: ≤2; 5: ≤2 total** if activated.
  Phase 5 items share that budget; opening another optional item does not reset it.
- **Owner-chosen lanes (2026-10-17):** Cursor = Grok in the included pool (`grok-4.7-medium` was
  listed 2026-10-17); Opus = the Claude subscription, not Cursor; Astra = `gpt-6-astra` (in the
  Codex catalog 2026-10-17). P0 re-enumerates and confirms before use.
- Enumerate current endpoint models before selecting: Cursor model list, Codex model catalog,
  scheduler `/models`, and the Claude subscription's available models. Record selected IDs and
  verification dates in `docs/harness/rehearsal-lanes-preflight.md`; no remembered defaults or
  silent substitutions. Cursor must use an explicit model in its included pool.
- Escalate only after recorded failure: local/hosted → Cursor → Opus. Astra remains the batched
  phase grader, not a worker fallback. Two red atomic briefs end that lane attempt.
- Cursor/Opus-built changes receive independent Astra review; Grok never grades. Push-gate's
  fresh-context grade remains mandatory. Reuse an accepted exact-tree verdict where supported;
  any push-gate Astra invocation counts against the same phase cap. If it cannot reuse the
  verdict within budget, stop for owner adjudication rather than launch another call.
- Log each wave using the configured lane log (`script`, `local`, `hosted` recorded as
  `workflow`, `cursor`, `subagent`, `grader` as applicable); no private account/path in this plan.

**Wave schedule (not individual task calls):**

| Phase | Cursor batches | Atomic local/hosted work | Opus work | Astra |
|---|---|---|---|---|
| 0 | One billing + public-web probe | None | None | 0 |
| 1 | A: schema/catalog/sourcing + all Python tests; B: TS types + all logic/UI tests after A | Catalog/resin loaders, cure, packer, kits, sequence, action compiler/validator; script YAML only where not generated | Data integration; player/UI/gloves/environment | One phase gate + at most one re-grade |
| 2 | A: all remaining group assignments/planning/script research + tests; B only for consolidated findings | One quantities function; one scripts YAML update; actuals storage functions | Whole-build + actuals integration | Same ≤2 |
| 3 | One ground-school research/data/test batch | One ground scripts YAML update | Ground-school UI | Same ≤2 |
| 4 | One tests/presets/catalog batch | None | Workspaces + private scan + presets | Same ≤2 |
| 5 | One batch for whichever optional scope is authorized | Only exact atomic briefs | Per approved multi-file task | Shared ≤2 |

## Common execution and verification

- Work on an isolated single-task worktree from `origin/main`; carry the approved design commits.
  No implementation in the shared checkout. This document-edit pass does not authorize shipping.
- Write named tests before implementation; demonstrate the relevant failure, then pass. For conduct,
  read its skill, commit tests first (clean tree required), put that test file in context, use
  `edit: replace` for an existing file, and keep each dispatched brief ≤25 lines.
- Python fixtures copy `tests/guide/test_schema.py::gdir` or the real graph to `tmp_path`;
  use `tests/guide/render_fixture.ROOT / "guide" / "graph"`. Never mutate tracked data for a test.
- TS tests use `node:test`/`node:assert/strict`. Focused local command:
  `cd guide/lab && npx tsx --test tests/<name>.test.ts`. Python equivalent:
  `.venv/bin/python -m pytest -q tests/guide/<name>.py`.
- Run labels used below (all expect PASS after implementation): **PY** =
  `.venv/bin/python -m pytest -q tests/guide` and
  `.venv/bin/python -m guide.check --schema-only`; **TS** = `cd guide/lab && npm test && npm run typecheck`;
  **E2E** = `.venv/bin/python -m pytest -q tests/guide/test_lab_e2e.py`.
- E2E reuses `serve(rsite)`, `_open(..., query="&player=1")`, `__lab.freeze(true)` and
  `__lab.advance(seconds)`. Use the sim clock, not sleeps. Run chromium and webkit where supported;
  record the existing Linux webkit skip, and use the owner's iPad for the device gate.
- Keep legacy selectors `#chips button[data-op]`, `#subject`, `#variant`, `#play` and recorder
  working. Player is opt-in until phase 1 approval; keep a `player=0` legacy route afterward.
- Stage named files only. Full suite green before implementation commits; group commits by real
  task, not helper. No attribution. No claims of live/done without the real running proof.
- At phase gates show failure on deliberately broken input in a temporary copy of real graph data
  (bad provenance/reference/script as appropriate), then pass on the real graph. Keep output in the
  gate record; do not make a separate test framework to prove the test framework.
- On-disk sourcing/gate records may be Markdown. Owner review is a served HTML view and live lab
  URL through the configured private preview service; never commit private URLs or screenshots.

## Phase 0: Preflight

### P0 — Verify lanes and baseline [script; one Cursor probe]

- [ ] **Files/output:** `docs/harness/rehearsal-lanes-preflight.md`; isolated implementation worktree.
- **Contract:** enumerate model IDs; one combined Cursor call says OK and retrieves a public page
  title. Check included-pool billing and zero-overage guard; stop if wrong. Record unavailable web
  research and its replacement lane. Read push-gate/grader and confirm verdict reuse and independence.
- **Run:** `cd guide/lab && npm ci && npm test`; **PY**, **E2E**; install Playwright browsers if needed;
  `conduct --lint` on an empty plan. **Expect:** clean baseline and usable lanes, or explicit
  blockers. No model calls just to test a model that will not be used.

## Phase 1: First stretch (seat bulkheads/firewall, fuselage sides)

### P1-A — Data foundation and sourcing [Cursor wave A; atomic conduct; Opus integration]

- [ ] **Files:** `guide/{schema,catalog,resin,check,build_site}.py`, `guide/graph/{groups,ch04,ch05}.yaml`,
  `data/catalog/prices.yaml`, `data/resins/mgs-285-287.yaml`, source registry as needed;
  `docs/harness/rehearsal-sourcing-p1.md`.
- **Signatures:** contracts 1–3, 5; atomic loaders get their own pre-written focused tests. Opus
  owns multi-file checker/build wiring; Cursor batches schema/data drafts and research together.
- **Do:** group the 17 first-stretch ops; source hours, buddy reasons, net buys and work-again cure
  data. Missing hours stay absent; missing prices/curve stay null/unsourced. Glass work has part
  cure. Seed catalog from the existing coupon purchase order, preserving its price flags/read date.
  Do not substitute pot life or post-cure time for work-again time. Astra verifies at phase gate.
- **Tests:** `test_groups.py`: ordered groups, required missing/unknown/duplicate groups, stub/GU
  exemptions, fixture without groups; `test_plan_fields.py`: invalid people/why/flags/citations/cure,
  unknown keys, round-trip; `test_catalog_resin.py`: duplicate IDs, invalid price/source/date/curve,
  unsourced empties, unknown references fail through check; `test_build_site.py`: payload, dates,
  staleness; `test_public_build.py::test_public_has_no_leaks`.
- **Run:** **PY**. **Expect:** five-key `plan.json`, schema-only checks cover new data, legacy fixtures
  pass. Record source matches and gaps for one batched grade, not individual review calls.

### P1-B — Planning logic [Cursor wave B tests/types; atomic conduct]

- [ ] **Files:** `guide/lab/src/logic/{graph,cure,sessions,kits,sequence}.ts`;
  `guide/lab/tests/{cure,sessions,kits,sequence}.test.ts`.
- **Signatures:** contracts 6–9. Cursor adds the `Op`/`PlanJson` types before atomic jobs.
- **Tests:** `cure`: interpolation/top clamp, below minimum/empty/unsourced → null, estimated heat;
  `sessions`: greedy order, oversize unsplit step, unknown 1h, buddy, group/cure boundaries, null cure,
  deterministic/non-mutating; `kits`: merged quantities, scrap once, partial/unpriced and empty kits,
  spent/next-buy, unknown calendar; `sequence`: GU/stub removal, every Roncz step reachable and after
  surviving prerequisites, deterministic groups, GU note exactly once, default plan mapping.
- **Run:** each exact focused test above per atomic function, then **TS**.
- **Expect:** unknowns never become NaN or authoritative totals. Validate group order against the DAG
  now; removing GU prerequisites must not orphan surviving steps. Do not build a scheduling engine.

### P1-C — Actions and scripts [wave A Python / wave B TS tests; atomic conduct/hosted]

- [ ] **Files:** `guide/scripts_schema.py`, `guide/graph/scripts.yaml`,
  `guide/lab/src/logic/actions.ts`, `guide/{check,build_site}.py`.
- **Signatures:** contract 12. Atomic YAML shape `Record<opId, Action[]>`; only this file per hosted
  call. Generate repeated ply actions deterministically; draft only exceptions from step data.
  Opus folds checker/build wiring into P1-A integration, after the validator exists.
- **Tests:** `test_scripts_schema.py`: reject each invalid action/key/op/part/tool/ply/who; real graph
  scripts clean; bad script fails `guide.check`; `actions.test.ts`: generated ply count/order/cloth,
  consecutive beats, captions, optional why, caption-only finite duration. No source-text regex test
  comparing Python constants to a TypeScript union.
- **Run:** focused Python/TS files, then **PY**, **TS**. **Expect:** no animation-invented plies,
  orientation or materials; scripts shipped through normal validation/leak checks.

### P1-D — One integrated player [Opus; tests prepared in Cursor wave B]

- [ ] **Files:** `guide/lab/src/{main,player}.ts`, `src/ui/{navlog,bench,environment}.ts`,
  `src/scene/{gloves,props}.ts`, `src/{style.css,logic/graph.ts}`, `index.html`;
  `guide/lab/tests/{player,gloves,environment}.test.ts`, `tests/guide/test_lab_e2e.py`.
- **Signatures:** contracts 10–14. Reuse `select(id)`, existing camera shots/orbit and sim clock;
  pure Player, direct DOM rendering, private pose helpers. No separate test-only `NavModel`.
- **Do:** session cards/checks, buy/cure markers, meter, bench/source detail, both glove pairs/tools,
  transport 1×/4×/16×, captions, default shot every step, top/side snaps, environment persistence.
  Expose user-set session hours (default 4); changing them repacks without changing shop hours.
  Hide whole-build zoom until phase 2; don't ship a switch whose two modes do the same thing.
- **Tests:** `player`: boundaries, speed, seek reset, caption-only advance, end pause; `gloves`:
  contrasting pairs/all props build headless, ≤4,000 triangles/pair; `environment`: invalid storage.
  E2E `test_player_{navlog_lists_the_first_stretch_groups,has_no_chapter_navigation,
  step_click_updates_bench_and_camera,meter_shows_dash_for_unknown_hours,
  play_through_reaches_the_last_step,orbit_does_not_stop_playback,step_change_flies_to_its_shot}`;
  `test_legacy_page_is_unchanged`, `test_session_length_repacks`, `test_env_{below_minimum_warns,enclosure_clears_the_warning,
  survives_reload,change_keeps_session_hours}`. Use a tmp known resin for temperature assertions.
- **Run:** **TS**, `cd guide/lab && npm run build`, **E2E**. **Expect:** reaches `f05.gear-extrusions`,
  readable unknowns/flags and no legacy regressions. Capture both glove pairs/props and layout for gate.

### P1 gate — Owner acceptance, default flip, one batched grade

- [ ] Run the common gate below. Owner first tries opt-in playback on iPad at ≥30 fps.
- **Files/signature after owner OK [Opus, part of P1-D]:** `main.ts` defaults to player; explicit
  `player=0` keeps legacy. E2E `_open`/`_open_rec` default legacy unless query names player;
  `tools/record.mjs` requests legacy. Add `test_player_is_default` using a raw URL, not that helper.
- **Run:** **E2E**, `node --test guide/lab/tools/record.test.mjs`, full gate.
- **Expect:** default flip included in the final phase diff BEFORE Astra and push-gate, not a second
  post-gate shipment. Astra call 1 includes data sourcing, main integration and glove screenshots;
  optional call 2 covers all fixes. If owner has not approved the flip, leave opt-in and gate pending.

## Phase 2: Rest of the build

### P2-A — Whole-build data in one wave [Cursor A; atomic hosted where needed]

- [ ] **Files:** `guide/graph/{groups,scripts}.yaml`, all `ch*.yaml`, catalog/resin/registry as needed;
  `docs/harness/rehearsal-sourcing-p2.md`; `tests/guide/{test_groups,test_scripts_schema}.py`.
- **Contract:** existing group/plan/action shapes; `canard` is the GU-note group. Pre-write grouping
  tests; draft one `groups.yaml` with complete op membership, then use a deterministic script to
  apply assignments to chapter files. Research planning for all groups together, not per group calls.
  Generate ply scripts; hosted exceptions edit only `scripts.yaml` against its validator.
- **Tests:** `test_every_roncz_step_grouped_once`, `test_groups_respect_dag`,
  `test_repo_scripts_are_clean`; E2E `test_gu_note_once` (only first canard step).
- **Run:** **PY**, **TS**, **E2E**. **Expect:** every non-stub Roncz step grouped and ordered; group
  ranks respect prerequisites, every chapter in required_files, unknown sourcing visibly retained.
  All sourcing and script findings go to the single phase gate.

### P2-B — Net quantities [Cursor A tests; atomic conduct; wiring with P2-C]

- [ ] **Files:** `guide/quantities.py`, `guide/build_site.py`, `tests/guide/test_quantities.py`.
- **Signature:** `cloth_m2_by_op(graph) -> dict[str, dict[str, float]]`, contract 18. Read actual
  `guide.layup.plies`/`guide.layup_geometry.build_layup` signatures before writing the atomic brief.
- **Tests:** `test_one_ply_area` within 1%, `test_no_solid_omitted`, `test_catalog_unit_conversion`,
  `test_missing_conversion_keeps_flag`, `test_site_derived_buy`; include resin ratio and no scrap here.
- **Run:** `.venv/bin/python -m pytest -q tests/guide/test_quantities.py`, **PY**.
- **Expect:** solids replace only supported authored quantities; no-surface or missing inputs keep
  estimates/unknowns. Opus handles build-site integration with P2-C, not another tiny worker call.

### P2-C — Whole-build UI and local actuals [Opus; Cursor A tests; atomic storage helpers]

- [ ] **Files:** `guide/lab/src/logic/{actuals,kits}.ts`, `src/ui/{navlog,bench}.ts`, `src/main.ts`,
  `guide/build_site.py`; `guide/lab/tests/{actuals,kits}.test.ts`, `tests/guide/test_lab_e2e.py`.
- **Signatures:** contracts 10, 20a; `meterAt(..., actuals = {})`. Keep step purchase attribution.
- **Do:** whole-build rows retain buddy/cure/spend; clicking enters group view. Meter shows cost
  to date/remaining/total sessions. Finished-step hours/receipt inputs persist locally, clearable.
- **Tests:** `test_build_zoom_rows_and_markers`, `test_build_zoom_enters_group`,
  `test_actual_hours_repack`, `test_clear_actual_restores_estimate`, `test_invalid_actual_storage`,
  `test_receipt_replaces_only_its_step`, `test_actuals_stay_local`; reload/edit E2E changes meter.
- **Run:** **TS**, **PY**, **E2E**. **Expect:** no duplicate estimated+actual spend or network writes;
  source/estimate labels survive rollups. Any wave-B Cursor call consolidates all phase findings.

### P2 gate

- [ ] Common gate; owner plays canard on iPad, sees GU note once, tests build zoom and actuals.
  Astra ≤2 for whole phase including sourcing, quantities and screenshots.

## Phase 3: Optional ground school

### P3-A — Replace stub with sourced lessons [one Cursor batch; atomic hosted scripts]

- [ ] **Files:** `guide/graph/{ch00_ground,groups,stubs,scripts}.yaml`, all current stub dependents,
  catalog/registry as needed, `docs/harness/rehearsal-sourcing-p3.md`, `tests/guide/test_ground_school.py`.
- **Contract:** existing group/plan/action schemas; `g00.*` IDs in `ground-school`, first group and
  required file. Identify lessons by group; no redundant `ground` boolean/schema extension.
  Add shop setup/opening kit, tools/materials, glove/action demos and practice pieces with why captions.
- **Do:** re-grep `c03.layup-skills` dependents; scripted replacement with final ground step. Remove
  real stub; keep tmp legacy fixtures legal. Use cited own words, quantities/hours/cure count normally.
- **Tests:** `test_stub_removed`, `test_all_stub_dependents_rewired`, `test_ground_precedes_build`,
  `test_ground_scripts_cover_action_vocabulary`; pre-written script validation for hosted YAML.
- **Run:** **PY**, full `guide.check` when corpus is available. **Expect:** dependency closure intact,
  real scripted education pieces; sources checked in the phase gate, not a separate Astra call.

### P3-B — Offer, skip and replay [Opus; same Cursor batch prepares tests]

- [ ] **Files:** `guide/lab/src/{main,player}.ts`, `src/ui/navlog.ts`, `index.html`,
  `tests/guide/test_lab_e2e.py`.
- **Contract:** `longez.ground = "seen"`; `#ground-offer`, `#ground-start`, `#ground-skip`;
  existing Player/Beat.why. Ground defaults 1×, build defaults 4×, user can override either.
- **Do:** offer on first launch, skip to first build step, always pin ground group for replay;
  shop setup exposes workspace/environment controls available in that phase.
- **Tests:** `test_ground_first_launch_offer`, `test_ground_skip_to_build`,
  `test_ground_skip_preserves_totals`, `test_ground_why_and_slower_speed`, `test_ground_replay`.
- **Run:** **TS**, **E2E**. **Expect:** skip changes viewing only, never kit/hours/cure totals.

### P3 gate

- [ ] Common gate; owner starts, skips and replays practice pieces on iPad. Astra ≤2 includes
  lesson citations and all screenshots. No per-lesson review calls.

## Phase 4: Workspaces and environments

### P4 — Scenes, runtime private scan and presets [one Cursor batch; one Opus task]

- [ ] **Files:** `guide/lab/src/scene/{workspaces,livingRoom,hangarBay}.ts`, `src/main.ts`,
  `src/ui/environment.ts`, `index.html`, catalog; `guide/lab/tests/workspaces.test.ts`,
  `tests/guide/{test_lab_e2e,test_public_build}.py`.
- **Signatures:** contract 25, existing `renderEnvironment`; `loadPrivateScan(url: string): Promise<THREE.Group>`
  in livingRoom. Runtime URL supplied locally by the owner (browser storage/config), never serialized
  into a site build. Reuse GLTFLoader; no scan copy or private URL in `site/` or git.
- **Do:** retain workshop; generic living room and hangar corner, lighting/floor/bench placement;
  missing/failed scan falls back with quiet notice. Presets 20/17/13/8 °C (heated shop/living room
  winter/unheated hangar coastal/winter cellar), all estimates. Add unpriced `part-enclosure` buy slot.
- **Tests:** `test_workspace_builds_and_bench_inside`, `test_workspace_keeps_hours`,
  `test_missing_scan_falls_back`, `test_runtime_scan_not_in_site`, `test_public_has_no_leaks`,
  `test_presets_set_temperature`, `test_enclosure_unknown_price_and_cure_savings`.
- **Run:** **TS**, **PY**, **E2E**. **Expect:** workspace never adds time. Show estimated cure-wait hours
  saved with enclosure (difference of known waits), or “—” if either unknown; the simple packer's
  session count does not vary with cure duration. Enclosure design/pricing and fit checks stay Phase 5.

### P4 gate

- [ ] Common gate; owner switches scenes and loads their private scan on iPad. Astra ≤2 includes
  both generic scene screenshots and privacy proof; no separate scene review calls.

## Common phase gate (phases 1–4)

1. **[script]** Run `.venv/bin/python -m pytest -q`, viewer `node --test guide/viewer/tests/*.test.mjs`,
   lab `npm test`, `npm run typecheck`, `npm run build`, and `pre-commit run --all-files`.
   Build and serve the actual site via the configured private preview service; record broken-input
   gate proof, sourcing gaps, screenshots, test results in `docs/harness/rehearsal-p<N>-gate.md`.
2. **Owner:** play that phase on iPad; ≥30 fps, readable hours/sessions/cost/buddy/cure, phase-specific
   checks above. If device proof is unavailable, say pending. Phase 1 default flip follows this OK,
   then rerun affected checks before review.
3. **[astra] call 1:** entire final phase diff + sourcing record + screenshots + test/device evidence.
   Includes every sourced/community claim, integration and visual review. Fix with the original
   worker lanes, retest, then at most **call 2** for a consolidated re-grade. No rolling review calls.
4. When authorized to ship, use `push-gate.sh --test-cmd "<full suite command>" --session <run-name>`
   from the implementation worktree. Fresh-context grade must match the exact pushed tree; honor
   the call cap above. Confirm remote HEAD; read the deploy receipt for the sha and quote its ID,
   or explicitly say not deploy-tracked. No direct push, PR, or unverified deployment claim.

## Phase 5: Optional, separate authorized scope

One short brief per selected item, written only when requested. No speculative implementation now.
Budget for this phase remains ≤2 Astra calls total: batched final gate + one possible re-grade.
Cursor research/test work is one batch; Opus handles each real multi-file task; atomic lanes keep
one file/signature/pre-written tests. Gate uses the same provenance, privacy and device rules.

- Group-video export through existing Blender render path, HITL-only, never scheduled.
- Part-scale heated enclosure design/pricing (coupon hot box is not canard-sized).
- X-ray plies, load-path animation, exploded view, fit/clearance checks (including optional room-fit
  warning), controlled-English captions, blueprint/manual styles. No span payload or fit API until then.

## Shared worker contracts

These are references for the brief that consumes them, not extra tasks or calls. Numbers retain the
original contract IDs for comparison. Flags and unknowns must remain visible all the way to the UI.

### Contract 1: Build groups in the graph

Add `group` and `plan` to `OP_KEYS`, `groups.yaml` and `scripts.yaml` to `RESERVED`
(otherwise the graph loader mistakes them for op files). Parse in `load_graph`, check in `validate`.

- Produces:
  - `groups.yaml` is a mapping (a YAML comment is not data, so the opt-in lives here, not in a
    chapter-file header):

    ```yaml
    groups:
      - {id: bulkheads-firewall, label: "Seat bulkheads and firewall"}
      - {id: fuselage-sides, label: "Fuselage sides"}
    required_files: [ch04.yaml, ch05.yaml]
    ```

  - `GROUP_FILE_KEYS = {"groups", "required_files"}`, `GROUP_KEYS = {"id", "label"}`
  - `@dataclass(frozen=True) class Group: id: str; label: str`
  - `Graph.groups: list[Group]` (file order = build order) and
    `Graph.groups_required: set[str]` (file names). A graph dir with no `groups.yaml` loads with
    both empty, so the tmp-graph fixtures in `test_schema.py` and `test_build_site.py` still pass.
  - `Operation.group: str | None = None`
  - validation messages (appended by `validate`, same style as the existing ones):
    - `"<op>: group '<g>' not in groups.yaml"`
    - `"<op>: missing group"` for an op in a file named in `required_files` that is not a stub and
      whose `variants` is not exactly `("gu",)`. Phase 1 lists ch04 and ch05; P2-A lists every
      chapter file.
    - `"groups.yaml: duplicate group <id>"`
  - `_op` must record the file name on the op for that check: add `Operation.file: str = ""`
    (excluded from `_op_json` in contract 5, or harmless if shipped).

### Contract 2: Per-step planning fields

- Produces:
  - `FLAGS = {"official", "community", "derived", "estimate", "unsourced"}` (spec §12 reuses the
    existing `KIND` words; `derived` is for values computed from geometry, contract 18)
  - `CURE = {"none", "part", "all"}`
  - `@dataclass(frozen=True) class Value: value: float | None; flag: str; source: str | None`.
    `official` needs a registry citation `<id>:p<page>` (checked with `core.sources.check_citation`);
    `community` needs a URL (`http://` or `https://`); `derived` needs a short derivation note
    (any non-empty string); `estimate` and `unsourced` carry no source, and `unsourced` carries
    `value: null`.
  - `@dataclass(frozen=True) class Buy: item: str; qty: float; flag: str`. `item` is a catalog id; `qty` is net, in the catalog item's `unit`; `flag` is `official | derived | estimate`.
  - `@dataclass(frozen=True) class Plan:` with fields:
    - `people: int = 1` (1 or 2)
    - `people_why: str | None = None` (required when `people == 2`)
    - `hours: Value | None = None` (None packs as a flagged 1 h, spec §12)
    - `cure: str = "none"`, one of `CURE`. `part` blocks further work on the same group; `all`
      blocks the shop.
    - `resin: str | None = None` (required when `cure != "none"`)
    - `tools: tuple[str, ...] = ()` (free strings in phase 1; contract 12 restricts them to `PROPS`)
    - `buy: tuple[Buy, ...] = ()`
  - A sourced buy carries its citation/derivation in the sourcing record keyed by op and item;
    UI links that evidence or labels the quantity estimate. Never display an unsupported flag as sourced.
  - `PLAN_KEYS`, `VALUE_KEYS = {"value", "flag", "source"}`, `BUY_KEYS = {"item", "qty", "flag"}`,
    all checked with `_extra` like every other block.
  - `Operation.plan: Plan | None = None`
  - YAML shape:

    ```yaml
    plan:
      people: 2
      people_why: draping the skin
      hours: {value: 3, flag: community, source: <url>}
      cure: part
      resin: mgs-285-287
      tools: [squeegee]
      buy: [{item: bid-7725, qty: 4.5, flag: estimate}]
    ```

  - The cross-file checks (`buy.item` exists in the catalog, `resin` exists in `data/resins/`) need
    the contract 3 loaders and are specified there as `validate_refs`. This task validates shape only.

### Contract 3: Catalog and resin data

- Produces:
  - `CATALOG_FLAGS = {"page", "unverified", "unsourced"}`, the purchase order's own vocabulary:
    `page` = read from the vendor page on `read` (needs `url` and `read`), `unverified` = from a
    snippet or a page that did not load, `unsourced` = no price (`price_usd: null`).
  - `@dataclass(frozen=True) class CatalogItem:` with fields `id: str`, `label: str`,
    `vendor: str | None`, `part: str | None`, `url: str | None`, `price_usd: float | None`,
    `unit: str` (`yd`, `gal`, `qt`, `ft`, `each`, ...), `read: date | None` and `flag: str`
  - `prices.yaml` is a list of those mappings. Ids are kebab-case from the line item:
    `bid-7725`, `und-7715`, `carbon-282`, `mgs-lr285-gal`, `mgs-h287s-qt`, `peel-ply-582c`, and so
    on. The PO's "Date of prices: 2026-10-08" is every seeded row's `read`.
  - Catalog flags `unverified`/`unsourced` render visibly as estimate/unknown; preserve source links.
  - `load_catalog(path: Path) -> dict[str, CatalogItem]` (raises `SchemaError` on a bad file)
  - `is_stale(item: CatalogItem, today: date, months: int = 6) -> bool` (`read` None → True)
  - `@dataclass(frozen=True) class Resin:` with fields `id: str`, `source: str | None` (when set
    it must be a registry citation, and for this file it cites `mgs-l285-tds:p<page>`),
    `min_temp_c: float | None`, `gate_hours: tuple[tuple[float, float], ...]` (pairs of (temp °C,
    hours until the part can be worked again), ascending temp) and `flag: str` in `FLAGS`
  - `load_resin(path: Path) -> Resin`; `load_resins(dir: Path) -> dict[str, Resin]` keyed by file
    stem, which must equal `id`
  - `validate_refs(g: Graph, catalog: dict[str, CatalogItem], resins: dict[str, Resin]) -> list[str]`
    in `guide/schema.py`: `"<op>: buy item '<x>' not in catalog"`, `"<op>: resin '<x>' not in
    data/resins"`. `guide/check.py` loads both from `DATA` (below) and appends these to its
    `SCHEMA:` failures, in both modes.
  - `DATA = Path(__file__).resolve().parent.parent / "data"` in `guide/catalog.py`, reused by
    `guide/check.py` and `guide/build_site.py`.

### Contract 5: Ship `plan.json`

`_plan_payload(g, catalog, resins, today) -> dict`; `build()` gains keyword-only
`catalog: Path | None = None, resins: Path | None = None`, defaulting to `DATA / "catalog" /
"prices.yaml"` and `DATA / "resins"`. Existing positional callers stay valid. Load/validate scripts
from the graph directory (absent → `{}`); `guide.check` invokes `validate_scripts` in both modes.

- Consumes: `Graph.groups`, `load_catalog`, `is_stale`, `load_resins`.
- Produces: `plan.json` with keys:
  - `groups`: `[{id, label}]`
  - `resins`: `{id: {min_temp_c, gate_hours, flag, source}}`
  - `catalog`: `{id: {label, url, price_usd, unit, flag, read, stale}}` (`read` as ISO string or
    null; `date` is not JSON-serializable, so convert explicitly)
  - `scripts`: `{}` (contract 12 fills it)
  - `today`: ISO date of the build

  Per-step plan data stays inside `graph.json` ops (`_op_json` already ships `plan` and `group`).

### Contract 6: Cure model (TS)

- Produces:
  - `export interface ResinLite { min_temp_c: number | null; gate_hours: [number, number][]; flag: string }`
  - `export interface Env { tempC: number; humidity: number; heat: 'none' | 'space-heater' | 'enclosure' }`
  - `export const HEAT_BOOST_C = { none: 0, 'space-heater': 5, enclosure: 15 }`. These boosts are
    `estimate`; the UI labels them so.
  - `export function cureGateHours(resin: ResinLite, env: Env): number | null`. It interpolates
    linearly on effective temp (`tempC + HEAT_BOOST_C[heat]`) and clamps at the top point. It returns
    `null` when effective temp < `min_temp_c`, when points are empty, or when the flag is
    `unsourced`. Humidity is recorded/displayed only until a source supplies its effect; no
    invented humidity multiplier. Below the first curve point, use null rather than extrapolate.

### Contract 7: Session packer (TS)

Greedy on ordered steps: add while `(hours + (step.hours ?? 1)) <= sessionHours`; a cure or group
boundary closes the session. An oversize step gets a session alone. Cure closes it even if hours
are unknown. Set `hoursKnown=false` for defaults, buddy if any step needs two; indices start at 0.

- Consumes: `cureGateHours`.
- Produces:
  - `export interface PlanStep { id: string; group: string; hours: number | null; people: 1 | 2; cure: 'none' | 'part' | 'all'; resin: string | null }`
  - `export interface Session { index: number; group: string; steps: string[]; hours: number; hoursKnown: boolean; buddy: boolean; cureAfter: { hours: number | null; scope: 'part' | 'all' } | null }`
  - `export function packSessions(steps: PlanStep[], resins: Record<string, ResinLite>, env: Env, sessionHours = 4): Session[]`

### Contract 8: Kits and the meter (TS)

- Consumes: `Session`.
- Produces:
  - `export interface Kit { group: string; lines: { item: string; qty: number; unitPrice: number | null; stale: boolean }[]; subtotal: number; scrap: number; unpriced: number }`
  - `export const SCRAP = 0.25`
  - `export function kitsFor(groups: string[], buysByGroup: Record<string, { item: string; qty: number }[]>, catalog: Record<string, { price_usd: number | null; stale: boolean }>): Kit[]`
  - `export interface Meter { spent: number | null; spentUnpriced: number; nextBuy: { group: string; amount: number; unpriced: number } | null; hoursDone: number; hoursTotal: number; hoursKnown: boolean; sessionsLeftInGroup: number; calendarHours: number | null }`
  - `export function meterAt(sessions: Session[], kits: Kit[], currentSession: number): Meter`
    - `spent`: sum of `subtotal + scrap` over kits whose group index is < the current session's
      group index, or null when there is no such kit; `spentUnpriced` counts their unpriced lines.
    - `nextBuy`: the first kit whose group index is ≥ the current session's group; `amount` is
      `subtotal + scrap`.
    - `hoursDone` / `hoursTotal`: session hours before the current session / over all sessions;
      `hoursKnown` is false if any counted session has `hoursKnown: false`.
    - `calendarHours`: `hoursDone` plus every `cureAfter.hours` before the current session; null if
      any of those is null.

### Contract 9: The sequence, Roncz-only (TS)

In `logic/graph.ts`, add `requires?: string[]`, `group?: string | null`, `plan?: PlanJson | null`
to `Op`; `PlanJson` mirrors contract 2 with arrays for tuples. Export existing `Storage2` for
storage helpers. Keep provenance in graph data even when planning arithmetic uses just numbers.

- Consumes: `Op`, `GraphLite`, `visibleOps` (`logic/graph.ts`), and `PlanStep`.
- Produces:
  - `export const GU_NOTE = 'The 1980 plans built the GU canard. This build uses the Roncz.'`
  - `export const CANARD_GROUP = 'canard'` (the group id P2-A must use)
  - `export interface SeqGroup { id: string; label: string; steps: Op[] }`
  - `export function buildSequence(graph: GraphLite, groups: { id: string; label: string }[]): SeqGroup[]`.
    It uses `visibleOps(graph, 'roncz')` and drops stubs. It buckets by `op.group` in the `groups`
    order, and keeps graph `order` within a group. Ungrouped ops are excluded (phase 1 covers only
    two groups). A group with no ops is still returned, with `steps: []`.
  - `export function noteFor(seq: SeqGroup[], opId: string): string | null`. It returns `GU_NOTE`
    only for the first step of the group whose id is `CANARD_GROUP`, and null otherwise. (Not "the
    first op with a `canard.` component": `f13.canard-attach-reinforce` carries one and belongs to
    the nose group.)
  - `export function toPlanSteps(seq: SeqGroup[]): PlanStep[]` with the mapping
    `hours = plan?.hours?.value ?? null`, `people = plan?.people ?? 1`, `cure = plan?.cure ?? 'none'`,
    `resin = plan?.resin ?? null`, `group = the SeqGroup id`.

### Contract 10: Nav log, meter and bench panel UI

Mount `#navlog`, `#meter`, `#bench`; player-only layout gives the 3D view/bench more width than
nav. Hide old opbar/variant in player mode but preserve DOM/handlers for legacy tours/recorder.
Fetch `plan.json` with graph/config; first stretch uses `setSubject('fuselage', false, false)`.
A step click and Player step change both use `select(id)` and refresh nav, meter and bench.

- Consumes: contracts 6–9.
- Produces:
  - `renderNavlog(root: HTMLElement, seq: SeqGroup[], sessions: Session[], kits: Kit[], currentStep: string, onStep: (id: string) => void, zoom: 'group' | 'build'): void`. Add build zoom only in phase 2.
  - `export function renderBench(root: HTMLElement, op: Op, catalog: Record<string, { label: string; unit: string }>): void`
  - `export function renderMeter(root: HTMLElement, m: Meter, zoom: 'group' | 'build'): void`
  - DOM contract (the e2e selectors):
    - `#navlog .group[data-group="<id>"] > .group-label` holds the group label
    - `#navlog .session[data-session="<index>"]` is a card; `.session.current`, `.session.done`
    - `#navlog button.step[data-op="<id>"]` is a step row; `.step.current`, `.step.done`;
      a `.chip.buddy` inside it when `people === 2`
    - `#navlog .marker.cure` (dashed) between cards after a session with `cureAfter`; it holds
      `.marker.cure.warn` when `cureAfter.hours` is null; `#navlog .marker.buy` (green) before the
      first session of a group with a non-empty kit
    - `#meter [data-k="spent"]`, `[data-k="next-buy"]`, `[data-k="hours"]`, `[data-k="sessions"]`,
      `[data-k="calendar"]`; an unknown value renders the single character `—`
    - `#bench [data-k="materials"]`, `[data-k="tools"]`, `[data-k="buddy"]`, `[data-k="cure"]`
    - `#bench .source` shows the step's chapter and page citation (the only place `chapter` appears)
  - test hooks on `window.__lab` (TEST only): `navlog(): { current: string; sessions: number }` and
    `meter(): Meter`

### Contract 11: Gloves and props

- Produces:
  - `export const GLOVE_COLORS = { owner: 0x3b6fd8, buddy: 0xe0892f }`
  - `export function makeGlovePair(who: 'owner' | 'buddy'): THREE.Group`. It is procedural: a
    rounded palm, 4 capsule fingers and a cuff, so no asset is needed. The children are named
    `left` / `right`.
  - `export type PropId = 'squeegee' | 'brush' | 'scissors' | 'hot-wire' | 'level' | 'sanding-block' | 'cup' | 'peel-ply' | 'string-line' | 'stand-in'`
  - `export function makeProp(id: PropId, label?: string): THREE.Object3D`. `stand-in` is a labeled
    box for steps without geometry (spec §12).
- Grip poses are private animation helpers, not a public API or a separate pose-test suite.

### Contract 12: Action vocabulary and step scripts

Use `scripts_schema.py`'s `scripts_for(g: Graph, overrides: dict) -> dict` during build to generate
ply defaults then apply overrides; validate the merged result before shipping. Its tests share
`test_scripts_schema.py`; it is a separate atomic signature, not a new service or module.

- Produces:
  - YAML, keyed by op id:

    ```yaml
    f04.firewall-aft:
      - {do: place, part: fuselage.firewall, who: owner}
      - {do: wet-out, ply: 1, tool: brush, who: owner}
      - {do: squeegee, ply: 1, tool: squeegee, who: owner, why: "optional, ground school only"}
    ```

    Generate place → wet-out → squeegee from ordered layup data where available. Explicit entries override generation; without either, use caption-only. `why` is optional on every action now, so P3-B needs no
    schema change; the player shows it only in ground school.
  - Python (`guide/scripts_schema.py`):
    - `ACTIONS = ("cut", "place", "wet-out", "squeegee", "drape", "flip", "sand", "check-level", "check-string", "bond", "wait-cure")`
    - `PROPS = ("squeegee", "brush", "scissors", "hot-wire", "level", "sanding-block", "cup", "peel-ply", "string-line", "stand-in")` (same accepted tools as TS; test actual action compilation, not TypeScript source text)
    - `ACTION_KEYS = {"do", "part", "ply", "tool", "who", "why"}`
    - `load_scripts(path: Path) -> dict[str, list[dict]]` (missing file → `{}`; raises
      `SchemaError` on a non-mapping)
    - `validate_scripts(scripts: dict, g: Graph) -> list[str]`, messages in the form
      `"scripts.yaml <op> action <i>: <fault>"`: unknown op, unknown action, unknown key, unknown
      part (not in `g.components`), unknown tool (not in `PROPS`), ply index < 1 or above the sum
      of the op's `materials[].plies`, a ply on an op with no `materials`, `who` not in
      `{"owner", "buddy"}`, and `who: buddy` on an op whose `plan` is None or has `people == 1`.
  - TS (`logic/actions.ts`):
    - `export interface Action { do: string; part?: string; ply?: number; tool?: PropId; who: 'owner' | 'buddy'; why?: string }`
    - `export interface Beat { t: number; dur: number; action: Action | null; caption: string; why?: string }`
    - `export const ACTION_SECONDS: Record<string, number>` (place 1.2, wet-out 1.0, squeegee 1.4,
      drape 1.6, cut 1.0, flip 2.0, sand 1.2, check-level 1.0, check-string 1.0, bond 1.2,
      wait-cure 0.8)
    - `export const CAPTION_ONLY_SECONDS = 2.5`
    - `export function compileStep(actions: Action[] | undefined, title: string, plyTotal: number): Beat[]`.
      `plyTotal` is the sum of the op's `materials[].plies` (0 when none). With undefined or empty
      actions it returns one beat `{ t: 0, dur: 2.5, action: null, caption: title }`. Beats are
      consecutive (`t` is the running sum of earlier `dur`).
    - Captions, in our own words: `place <part label or id>`, `cut <part>`, `wet out ply N of T`,
      `squeegee ply N of T`, `drape ply N of T`, `flip <part>`, `sand <part>`, `check level`,
      `check with the string line`, `bond <part>`, `wait for cure`. When `plyTotal` is 0 the
      `of T` is dropped.

### Contract 13: Player, transport and directed camera

Controls: `#tp-prev`, `#tp-play` (`aria-pressed`), `#tp-next`, `#tp-speed [data-speed="1|4|16"]`,
`#caption`. Tick from existing `step(dt)` simulation clock; never wall-clock timers. Animate
real components/ordered plies from each beat; use labeled primitive stand-ins or caption only.

- Consumes:
  - `Beat`, `compileStep`
  - `makeGlovePair`, `makeProp`
  - `buildSequence`
  - the directed camera is the existing per-op shot: on a step change main.ts calls `select(id)`
    (the chip path), which flies to the op's `fuseShots.ts` shot on the fuselage subject. The
    `tours.yaml` shots only cover `r30.*` and are not used here. An op with no shot frames its component bounds, or the labeled stand-in/bench for caption-only work; every step gets a default view.
  - the second glove pair appears when the current step's `plan.people === 2` or a beat's
    `action.who === 'buddy'`
- Produces: `export class Player` with:
  - `constructor(beatsByStep: Map<string, Beat[]>, order: string[])`
  - `play(): void`, `pause(): void`, `next(): void`, `prev(): void`, `seekStep(id: string): void`
  - `setSpeed(x: 1 | 4 | 16): void`
  - `tick(dt: number): { step: string; beat: Beat | null; k: number; changed: boolean }`. Pure
    sim time: `dt` is scaled by speed; `k` is progress through the current beat in `[0, 1]`;
    `changed` is true on the tick that enters a new step. A caption-only step (one null-action
    beat) advances like any other. At the end of the last step it pauses.
  - Camera ownership stays in main.ts: user orbit suspends directed movement until the next step; playback continues. No unused camera method on the pure Player.
  - `get playing(): boolean`, `get speed(): number`, `get step(): string`
  - test hook on `window.__lab` (TEST only): `player(): { step: string; playing: boolean; speed: number; caption: string }`

### Contract 14: Environment toggle (one resin)

- Consumes: `Env`, `cureGateHours`, `packSessions`.
- Produces:
  - `export function renderEnvironment(root: HTMLElement, env: Env, onChange: (e: Env) => void): void`
    into `#environment` (player mode only). Controls: `#env-temp` (range 5–30 °C, step 1),
    `#env-humidity` (range 20–90 %, step 5), `#env-heat` (`<select>` with `none`, `space-heater`,
    `enclosure`), each labeled; the heat options carry the text "estimate".
  - `export const DEFAULT_ENV: Env = { tempC: 20, humidity: 50, heat: 'none' }`
  - `export function loadEnv(storage: Storage2 | null): Env` / `saveEnv(storage, env)` on the
    `localStorage` key `longez.env`; invalid or missing JSON → `DEFAULT_ENV`; a null storage is
    fine (the lab already runs without storage).
  - main.ts: every change re-runs `packSessions`, `meterAt` and re-renders
    the nav log and meter. Nothing about the scene changes.

### Contract 18: Geometry-derived cloth quantities where layup solids exist

- Consumes: `guide.layup.plies(graph) -> list[Ply]`, `guide.layup_geometry.build_layup(graph)`
  (CadQuery; read both signatures and the `Ply` dataclass before writing the brief).
- Produces: `cloth_m2_by_op(graph) -> dict[str, dict[str, float]]` (op → cloth → m², net), computed
  as ply solid volume ÷ ply thickness from the layup data. Ply thickness per cloth comes from
  `data/materials.yaml` if it holds one, else the value is flagged: name the source in the brief.
- Convert m² to catalog cloth units using sourced/flagged roll width; derive resin mass from the purchase-order ratio and convert with sourced/flagged density/package size. If a conversion input is missing, keep authored estimates or unknowns. Never write m² into a yard quantity or upgrade an unsourced thickness to derived truth.

### Contract 20a: Owner actuals override estimates

- Produces:
  - `export interface Actual { hours?: number; spentUsd?: number }`
  - `export function loadActuals(storage: Storage2 | null): Record<string, Actual>`. The `localStorage` key
    is `longez.actuals`. It is never sent anywhere and never committed (spec §9).
  - `export function applyActuals(steps: PlanStep[], actuals: Record<string, Actual>): PlanStep[]`.
    An actual's hours replace `hours` and mark them known.
  - `saveActuals(storage: Storage2 | null, actuals: Record<string, Actual>): void`; invalid/missing storage → `{}` and safe no-op writes.
  - Receipt overrides replace the completed step's estimate, not an entire group kit; retain per-step buy attribution for that subtraction. Missing fields retain estimates; zero is a valid actual. Never add receipts on top of the same estimated purchase. Recompute the meter and sessions on edit/clear.

### Contract 25: Workspace registry and the two generic scenes

- Produces:
  - `export type WorkspaceId = 'workshop' | 'living-room' | 'hangar-bay'`
  - `export interface Workspace { id: WorkspaceId; label: string; build(): THREE.Group; bench: { x: number; z: number; y: number } }`
  - `export const WORKSPACES: Record<WorkspaceId, Workspace>`
