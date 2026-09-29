# Block 1 baseline truth: captain brief (Tasks 1–9)

The role, method (superpowers:subagent-driven-development: sonnet implementer → sonnet reviewer →
you re-verify), hard constraints, log/report rules and the "three states" rule are the same as in
`docs/harness/planform-captain-brief.md` and the M2 briefs it points to. Read it first. This brief
overrides it where they differ.

**Plan (the work):** `docs/superpowers/plans/2026-09-29-block1-baseline-truth.md`, Tasks **1
through 9 only**. Task 10 is the lead's.
**Spec (the why):** `docs/superpowers/specs/2026-09-29-block1-baseline-truth-design.md`.
Read both in full. The owner approved both on 2026-09-29.

## What's different from the planform run

- **Research tasks.** Tasks 2, 6 and 7 start with reading real pages: the manual text, the
  Canard Pusher OCR, and the plans scan images. Crew record what each page says in
  `docs/block1-source-notes.md` (≤10-word paraphrases, own words). **You spot-check every value
  that changes the model** against the page yourself before committing. A value read by a crew
  member alone is a claim.
- **Page images.** Where a number sits on a drawing or chart (the manual's p.28 CG chart, the plans
  station callouts, the canard waterline on p.171 and template C-3), read the image, not just the
  OCR. The manual is a transcription whose chart labels were retyped.
- **Decision rules are fixed in the plan** (the Roncz vs GU canard rule in Task 7, the
  NOT GRADED rule in Task 4). Follow them; don't improvise a third option. If the evidence fits
  neither branch, stop and report.
- **Network.** Task 2 downloads Canard Pusher PDFs from cozybuilders.org. That is the only network
  write-free fetch allowed. No other remote hosts, no ssh, no deploy, no push.

## Carried over (non-negotiable)

- Crew dispatched in the **foreground only**.
- Crew leave work uncommitted; **you** commit after your own green, unpiped test run in open-ez in
  the same turn. Restore `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json`
  before each commit. The regenerated `data/validation/accuracy_report.json` IS committed.
- Stage named files only. No commit trailers.
- Never loosen a tolerance; failing physics bounds become strict xfails citing a numbered ledger row
  (continue the existing numbering).
- Public repo: no home paths, tailnet names or IPs, no copied plans text, never the copyright
  phrase. Never print env values.
- Stop and report instead of guessing when a task's evidence fits no rule.

## Files you write

- Log: `docs/harness/block1-captain.md`
- Report: `docs/harness/block1-captain-report.md`. Per task: status, commit sha(s), verify tail;
  every value changed (from → to, citation); the Roncz decision and its evidence; the stability and
  two-method check results; the NP value; every new ledger row; deviations and escalations; anything
  the lead needs for Task 10.

Commit both at the end (`docs: Block 1 captain log and report`).

## Done means

Tasks 1–9 committed, and these pass when re-run by you: the full suite (only the pre-existing
`scripts/assembly_test.py::test_full_assembly` may fail; everything else passes or is a ledgered
strict xfail), node tests, and `guide.check` with the env sourced.

Your final message to the lead is the report's content, not its path.
