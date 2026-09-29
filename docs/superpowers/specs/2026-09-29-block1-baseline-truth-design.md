# Block 1: Baseline truth

Status: design approved in conversation 2026-09-29, pending written review.
Roadmap: `docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`, Block 1.

## 1. Intent

Every number the model treats as the book's comes from a page someone can open. Everything else is
visibly flagged. With that done, the NP and CG checks measure the model against the real airplane
instead of against numbers the project wrote itself.

## 2. Why this block exists

- **The planform correction (2026-09-29) exposed the problem.** Book geometry moved the computed NP
  17.85 in aft of the "published" FS 108.
- **The reference file behind that 108 was never checked.** `data/validation/reference_data.json`
  was written by an automated planning session in March 2026 without the documents in hand:
  - its canard entries (147 in, 15.6 sq ft) are the code's own invented values, given a citation;
  - the Canard Pusher issues it cites for everything (CP-29, CP-31) are empty in the local corpus;
  - its five "community build records" have no traceable origin.
- **The Long-EZ Owner's Manual (first edition, May 1980) contradicts most of the file.** A
  transcription is in the cobelu repository.

| Value | Owner's Manual | reference_data.json |
|---|---|---|
| Canard span / area | 11.8 ft / 12.8 sq ft | 147 in / 15.6 sq ft |
| Wing span / area | 26.1 ft / 81.99 sq ft (94.8 total) | 26.4 ft / 94.2 sq ft |
| Empty weight | about 750 lb | 850 lb |
| Max takeoff gross | 1325 lb (1425 only under conditions) | 1425 lb |
| CG limits | FS 97 to FS 103 (weight and CG chart) | FS 99 to FS 104 |
| Neutral point | not given | FS 108 |
| Length | 201.4 in | model 214 in |

The manual also gives the loading arms: pilot FS 59, passenger 103, baggage 90, fuel 104.5 and
oil 140. It gives the instrument panel reference at FS 40, the main gear at FS 110.5 ± 1, and the
nose gear at about FS 20.

## 3. Design

### 3.1 One sources registry

- **A single registry lists every document the model may cite:**
  - the Owner's Manual;
  - the 1980 Section I plans;
  - the Canard Pusher issues;
  - the cobelu transcription;
  - owner checks, such as the 2026-09-29 by-eye read of p.171.
- **Each registry entry records:** id, title, edition or date, where a builder can obtain it, and
  whether the local copy is a scan or a transcription.
- **Every citation points at a registry id plus a page.**
  - `GEOMETRY_PROVENANCE`, the reference data and the mass/CG ledger all use this form.
  - A citation may carry a quote of at most a few words.
  - Plans content is never copied into the repository.
- **Private locations stay out of the repository.** Scan paths live in the local environment file.
- **Enforcement:** a test fails when a citation names an id missing from the registry, or when a
  value claims `book` or `cp-corrected` status without a page.

This extends the provenance table from the planform correction rather than creating a second system.

### 3.2 Source corpus

Build the corpus before the audit, so every check runs against a real page.

- **Owner's Manual:**
  - page-numbered text extracted from the cobelu PDF;
  - its charts read by eye (the weight and CG chart on p.28);
  - flagged as a transcription, so any value that matters is checked against its chart image as well.
- **Canard Pusher:**
  - CP-29 and CP-31 fetched as PDFs from the public Canard Pusher archive, then OCR'd;
  - every other issue the audit needs, fetched the same way.
- **Plans:** the existing Section I scan OCR, plus page-image reads for dimensions.

### 3.3 Reference-data audit

- **Each entry in `reference_data.json` is resolved one of three ways:**
  - **confirmed:** a registry id and page, with the value corrected to what the page says;
  - **derived:** computed from confirmed values, with the formula stated;
  - **unverified:** kept for history, excluded from every check.
- **Two items are removed outright:**
  - the five community build records, which have no source;
  - the CP-29/CP-31 bibliography entries, unless those issues turn out to contain the cited values.
- **The published NP (FS 108) becomes unverified** unless a source is found. Physics checks stop
  using it as truth.
- **Tests that depended on removed or corrected values are triaged with the same ledger discipline
  as the planform correction:**
  - a test pinned to a retired number gets an updated expectation;
  - a physics bound that now fails becomes a strict xfail citing a ledger row;
  - no tolerance is ever widened.

### 3.4 Geometry to the book

Each value gets a registry citation, or stays flagged.

- **Fuselage stations:**
  - check the model's stations against the manual: panel FS 40, main gear FS 110.5, nose gear
    about FS 20;
  - check them against the station callouts in the Section I plans;
  - resolve the length conflict (model 214 in; manual 201.4 in overall; book nose tip FS −6.8);
  - retire the uniform −45.5 shift wherever a book station exists.
- **Wing:** span, area and strake area from the manual and the plans; the leading-edge anchor already
  comes from CP25 LPC7. Sweep, root and tip chords, and dihedral are taken from plans pages where
  they are printed. Where they are not, they stay flagged.
- **Canard:**
  - the manual gives 11.8 ft and 12.8 sq ft for the first-edition GU canard, a chord of about
    13.0 in (the 142 in tip-to-tip span matches the owner's B.L. 71 read);
  - the Roncz chord, span and incidence are searched for in the Canard Pusher issues;
  - if the Roncz values are found, they are used as `cp-corrected`;
  - if not, the model uses the GU planform, flagged `conflict: Roncz planform unconfirmed`, never a
    guess;
  - the canard waterline conflict (p.171 W.L. 18.9, template sheet C-3 W.L. 19.8, config 12.0) is
    resolved or flagged.
- **Weight arms** move to the parts they describe. In particular, the canard's structural weight is
  placed at the canard.

### 3.5 Mass/CG ledger (first version)

- **One row per item:** mass, arm, class (primary structure, secondary, non-structural, payload),
  process, and a registry citation.
- **In Block 1 the empty aircraft is a single row.** Block 2 breaks it into parts from the ply
  schedules. The loading rows (pilot, passenger, baggage, fuel, oil) carry the manual's arms.
- **Gate: reproduce the manual's own sample loadings.**
  - The ledger must recompute the light-pilot sample: 1,113 lb at 103.96 in, which the manual shows
    outside the aft limit.
  - It must also recompute the heavy-pilot sample, from the manual's own inputs.
  - A result that differs from the book's arithmetic fails. This proves the ledger's arithmetic and
    arms before any of the model's own masses go in.
- **Envelope:** the CG limits (FS 97 to FS 103, 1325 lb, with the 1425 lb takeoff-only band) are
  encoded from the chart, with the chart page cited.

### 3.6 Physics checks, re-anchored

- **Stability at the aft limit.** The computed NP must lie aft of the manual's aft CG limit
  (FS 103), with a positive static margin there. This is a physical necessity, not a fit.
- **Two methods agree.**
  - The analytic NP and the vortex-lattice NP must agree within a bound set in the plan.
  - Disagreement fails the check.
  - The vortex-lattice leg needs OpenVSP installed. Until it is, the check reports "not run" and
    never passes silently.
- **The NP value itself is reported, not graded,** unless a published NP is found and confirmed.

### 3.7 Gates must fail first

Each new gate is shown to fail on a deliberately broken input before it counts:
- the registry test, on an unknown id;
- the sample-loading gate, on a wrong arm;
- the stability check, on an NP forward of FS 103;
- the two-method check, on an injected disagreement.

## 4. Done when

- Every value in `reference_data.json` is confirmed, derived or unverified, and no check uses an
  unverified value as truth.
- Every `GEOMETRY_PROVENANCE` entry cites a registry id and page, or is flagged.
- The ledger reproduces both of the manual's sample loadings exactly.
- The stability-at-aft-limit check has a result.
- The two-method NP check runs (OpenVSP installed) or reports "not run".
- Every gate has been shown to fail on a broken input.
- A report lists each value the model changed, from what to what, and the page that justifies it.

## 5. Out of scope

- Decomposing the empty weight into parts (Block 2).
- Rehearsing the chapters or extracting ply schedules (Block 2).
- Anything in Blocks 3–7.

## 6. Risks

- **The manual is a transcription.** cobelu retyped some chart labels, so values that matter are
  checked against the chart image and the original edition where possible.
- **First-edition versus Roncz.** The manual and the 1980 plans describe the GU airplane. The Roncz
  canard changed the canard, and possibly the CG limits, in later Canard Pusher issues. Any Roncz
  value without a source stays flagged.
- **The NP may never get a published value.** The stability check and the two-method check are
  designed to be meaningful without one.
