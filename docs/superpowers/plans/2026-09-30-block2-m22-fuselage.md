# Block 2 Milestone 2.2: Fuselage Box Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** chapters 4–6 are rehearsable in the lab on a book-built fuselage, with every part's fidelity
visible and the placeholder fuselage retired.

**Spec:** `docs/superpowers/specs/2026-09-30-block2-m22-fuselage-design.md`. §2 is the evidence.
Full research: `docs/harness/m22-fuselage-research.md`; Task 1 appends its geometry and CP rows to `docs/block1-source-notes.md`.

## Global Constraints

- **Source rules** (AGENTS.md "Sources and provenance"):
  - Every book or derived value cites `plans-1980:p<page>` or `cp-text:p<issue>`.
  - Template-only shapes are `representational`, never `book`.
  - Never measure an undimensioned image.
  - Quotes are ≤10 words, paraphrased.
- **Owner's words** for every op title, summary and checklist. `guide.check` must pass. No plans text
  in the repo.
- **Never loosen a tolerance.** Any physics bound the new fuselage moves gets the ledger
  discipline (docs/geometry-correction-ledger.md, continue the numbering).
- **Gates:**
  - `source ~/.config/long-ez/env && bash scripts/remote_test_all.sh` (two nodes);
  - locally `.venv/bin/python -m pytest -q -p no:cacheprovider -m local_render` (this satisfies the
    commit hook);
  - `node --test guide/viewer/tests/*.test.mjs` plus the lab's unit tests and typecheck;
  - `guide.check`.

  Every wait runs in the foreground. If a node stalls, report it and fall back to the laptop.
- **Visual tasks** end with GPU-path screenshots at 1180×820, which the captain looks at before
  committing, and a comparison against the canard chapters' standard.
- **Commits:** the captain commits, named files only, no trailers, no push or deploy.

## Review Focus

1. **A representational part shown as book.** Expectation: fidelity is a required field on every
   solid, the lab reads it, and a test fails on a missing tag or on a `book` tag without a citation.
2. **Occupant arms confused with bulkhead stations.** Expectation: a test asserts the seat
   bulkheads sit at their derived stations and the CG arms stay at the manual's values.
3. **The side profile drifting from the printed heights.** Expectation: a test samples the side
   solid's top and bottom at the 12 printed x-stations and matches them to ±0.05 in.
4. **The book-order jig assembly done out of order.** Expectation: the ch6 op prerequisites encode
   the bonding order (front seat, panel, F22, rear seat, firewall), and a test walks it.
5. **The canard chapters regressing.** Expectation: the M2.1b lab e2e suite stays green unchanged.

---

### Task 1: Source notes and config stations
- Append the fuselage research to `docs/block1-source-notes.md`: the geometry table, the derived
  stations with their arithmetic, and the 22 CP entries. Take them from the spec's §2; the captain
  re-reads p36 and p33–p34 on the page images to confirm the numbers before committing.
- `config/aircraft_config.py`:
  - add `fs_f22`, `fs_f28`, `fs_panel`, `fs_front_seat_bkhd_bottom`, `fs_front_seat_bkhd_top`,
    `fs_rear_seat_bkhd_bottom`, `fs_rear_seat_bkhd_top`, `side_panel_length` and the side-height
    table, each with a `GEOMETRY_PROVENANCE` entry (`derived`, citing plans-1980:p36);
  - give `fs_panel` a `conflict` note against om-1980's 40.
- Tests (red first): the provenance entries, and Review Focus 2 and 3. The side-height table
  matches the printed values.
- Commit.

### Task 2: Book fuselage geometry
- `core/fuselage_book.py` builds:
  - the side panels (foam 0.8 in, the printed outline, the spar cutout, the sight-gauge depression);
  - the front and rear seat bulkheads (printed outline, tapers, holes);
  - representational F22, F28, the panel and the firewall, fitted to the side profile at their
    stations;
  - the bottom block (partial contour, `representational`).
- Every solid is returned with `fidelity`, and with `cite` for `book` and `derived` solids.
- Replace the placeholder `Fuselage` usage in `core/assembly.py` and `scripts/assembly_test.py`.
  Re-run the assembly test. If it now passes on book geometry, remove the strict xfail. Otherwise
  update its reason honestly.
- Tests: Review Focus 1 and 3; the solids are valid and closed; the bulkheads sit inside the side
  profile at their stations.
- Commit.

### Task 3: Chapters 4–6 in the graph
- Author `guide/graph/ch04.yaml`, `ch05.yaml` and `ch06.yaml` from the research op list, in the
  owner's words, with `materials` in the ch30 shape and CP LPC links (with `status: conflict` where
  the CP and the page disagree, as in M1).
- Add cross-chapter prerequisites, and ch6's bonding order (Review Focus 4).
- `guide.check` passes, the schema tests pass, and the linker recall gate covers the new chapters'
  annotations.
- Commit.

### Task 4: Areal weights and ledger areas
- Source the glass styles and foam named in ch 2's bill of materials (the page is in the scan)
  from manufacturer datasheets fetched and read: areal weight in oz/yd², and density in lb/ft³.
  Register each source.
- `core/ledger.py` gains per-part ply areas and ply counts from the fuselage solids and the op
  materials, plus masses where the areal weights and resin ratio are sourced (the resin ratio from
  the plans' own text where it's stated). Otherwise the mass reads "not yet computed".
- Test that areas are positive and match the solid surfaces, and that masses appear only when every
  input is sourced.
- Commit.

### Task 5: Fuselage in the lab
- Export the fuselage parts plus their plies to the glb, with `layup.json` entries for the ch4–6
  plies.
- Grow the scene:
  - the fuselage jig (bench and levelled blocks, from the p39 dimensions);
  - side panels on the table for ch5;
  - the jig assembly for ch6;
  - camera shots per op.
- The representational material treatment (a hatch or stripe) and its labels.
- The station section cut along the fuselage, and the readout's CG row (Task 4 data).
- The build state across chapters. The canard stays on its own table until ch12, which is out of
  scope.
- Lab e2e for the new chapters, on both engines, plus screenshots.
- Commit.

### Task 6: Tour and film
- Add a chapter 4–6 tour to the director. Render a film of chapter 6's jig assembly, into the
  scratchpad, not the repo.
- Commit.

### Task 7 (lead)
- Deploy, publish the public build if the public-share lane has landed, grade, and push.
- The owner walks it.
