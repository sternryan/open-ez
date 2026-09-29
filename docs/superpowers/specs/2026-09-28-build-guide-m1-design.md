# Long-EZ Interactive Build Guide — M1 "Build Rehearsal" (canard slice)

Status: APPROVED 2026-09-28 (rev 2: public/private split)

## 1. Intent

A start-to-finish interactive Long-EZ build guide in the spirit of airsup.ai's browser "take-apart"
machines, built on open-ez's plans-as-code geometry. It has two modes over one step graph: an
**explorer** ("understand before committing") and, later, a **shop companion** (progress,
build log, 51% evidence). Sequencing is rehearsal-first: the first slice is explorer content held to
companion discipline (prerequisites, variants, completion criteria, non-geometric steps).

**Acceptance test:** after using it, the owner can explain the canard build sequence, which plans
corrections apply and why, and how the parts fit together in space.

## 2. Scope

| Milestone | Delivers | Status |
|---|---|---|
| **M1 Build Rehearsal** | ~17 authored operations across ch 10 (GU canard), ch 30 (Roncz canard), ch 12 (canard install), with checklists, verified plans-change links, and minimal selectable 3D | this spec |
| M2 Layup cutaway | one spatial explanation (canard layup cutaway linked to its steps), via the headless-Blender GPU payload. **Timeboxed**, and committed as M1's direct successor | next spec |
| C Shop companion | progress, build-log photos, 8000-38 evidence, BOM consumption | deferred until a real build |

**Out of M1:** whole-airframe geometry, fixing open-ez aero defects (§9), Sections II+.

## 3. Sources and authority order

1. **Owner's plans set**: Section I, March 1980 first edition, phone-scanned, 171 pp, no text layer.
   This is the page authority. Footer OCR puts ch 10 at about scan pp 54–70, ch 12 at pp 71–72, and
   ch 13 at pp 73–83; M1 confirms these. **Ch 30 (Roncz) is not in the first edition.**
2. **Prior-owner margin annotations** in that set, e.g. "CP#25 LCP#7 MEO wing root LE 113.9 not
   113.4". Each one is a claim until matched to its Canard Pusher entry. Together they are the
   **ground truth the automated change linker is scored against**.
3. **Canard Pusher** plans-change entries. The sectioned CP 1–82 text lists them in a structured
   form (`LPC #7, MEO, Back cover of plans.`), so linking is mostly a deterministic parse.
4. **cobelu/Long-EZ** (GitHub): chapter figure images, markdown transcriptions that carry inline
   change markers (`{CP27 PC44 MEO}`), BOM sheets. It is the only source for ch 30.
5. Community wiki: context only, never authority.

Conflicts are preserved, never resolved silently. Change links carry
`status: verified | unresolved | conflict` and `kind: official | community`.

## 4. Public/private boundary (hard rule)

**Legal status:** the plans carry "Copyright 1980 by Rutan Aircraft Factory Inc… All Rights
Reserved." Research on 2026-09-28 found **no public-domain release**. The claim traces to one
uncited README. Counter-evidence: EAA stated in 2005 that RAF "still owns the rights," and RAF
licensed TERF to publish the plans in 1996. Until a rights-holder says otherwise:

- **Public (this repo):** code (schema, validator, parsers, exporter, viewer, pipeline); step content
  **in our own words**; page references; plans-change *facts* (number, class, page, corrected value);
  links to cobelu's already-hosted figure images (linked, never re-hosted).
- **Private, never in git:** scan images of the owner's set, OCR text, verbatim plans or CP text.
  These live on the tailnet host under a private asset directory and are served only over the tailnet.
- **Enforced, not trusted:** an n-gram overlap gate (`python -m guide.check`) fails any authored
  text that shares an 8-word run with the plans or CP sources. It must run in full mode before any
  content commit.
- Nothing in this repo claims the plans are public domain.

## 5. Step graph schema

YAML in `guide/graph/`, one file per chapter, plus `components.yaml`, `pages.yaml` and
`annotations.yaml`. Operation fields: `id` (stable forever), `chapter`, `title`, `summary`,
`variants` (`gu|roncz|both`), `requires`, `components`, `geometry_visible`, `materials` (values only
from sources, never invented), `sources` (`doc`, `page`, `scan_pp`, `figure`, `heading`), `changes`,
`completion`, `inspection`, `stub` (a prerequisite outside the slice). Components carry a fidelity
badge: `no-geometry | unvalidated | plans-checked | a-sheet-verified`. Progress/evidence (C) is a
separate store keyed on `(op id, graph git sha)`. None of it is authored in M1; rehearsal checkboxes
live in browser localStorage.

## 6. Content pipeline

| Stage | Lane |
|---|---|
| Render scan pages, OCR text, footer page map | script (PyMuPDF + tesseract), output private |
| Transcribe margin annotations on slice pages (~20 pp) | session vision + owner confirmation (small; the full 171-pp pass goes to the smithy `local-vision` lane later) |
| Parse CP plans-change entries + cobelu markers | script |
| Draft operation text from sources | smithy `local-heavy`; session edits; overlap gate |
| Linker recall gate | script: every confirmed annotation on ch 10/12 pages must be recovered |

## 7. Geometry (minimal in M1)

Stand up a working CadQuery env (none exists on the dev laptop today) and confirm the canard
generator still runs. `python -m guide.export_glb` emits a `.glb` whose node names are component IDs.
M1 has one real part (`canard.core`); everything else is honestly badged `no-geometry`.

## 8. Viewer and serving

Static three.js site, vendored (no CDN at runtime). Layout: operation list · 3D · source pane
(private scan page when available, else the cobelu figure link) · checklist. Variant toggle (default
Roncz, per the repo's safety mandate). Bidirectional part↔operation selection. Works at phone
width. Served from the tailnet host behind `tailscale serve` (tailnet-only). The private scan
directory is symlinked in at deploy time, never built into the site.

## 9. Known accuracy issues surfaced (logged, not fixed in M1)

- `config/aircraft_config.py` `fs_wing_le = 125.61` ("calibrated Phase 5") vs plans-corrected wing
  root LE 113.9" (LPC #7). Not yet confirmed to be the same reference point.
- The existing AGENTS.md defects stand (canard AC sweep correction, self-referential baselines).

## 10. Definition of done (M1)

1. ~17 operations across ch 10/30/12, including ≥1 `geometry_visible: false` op, ≥1 stub
   prerequisite outside the slice, and both variants.
2. `python -m guide.check` green in full mode: schema, overlap gate, and every confirmed annotation
   on slice pages linked.
3. Linker recall 100% on confirmed ch 10/12 annotations.
4. Part↔operation selection works both ways; GU shows `no-geometry` cleanly.
5. The tailnet URL loads on the owner's iPad, verified by loading it.
6. A fresh-context grader tries to prove 1–5 false before anything is called done.
7. Acceptance per §1.
