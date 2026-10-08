# open-ez learnings

Short, grep-able lessons from the work. Each entry names the problem, the cause, the fix, and the
non-obvious point. Read this before planning a milestone.

### Book geometry over fitted geometry; let the gap show
<!-- problem_type: architecture -->
<!-- component: config/aircraft_config.py, core/analysis.py -->
<!-- date: 2026-09-29 -->

**Problem:** The model's NP matched the published FS 108 to the tenth.
**Root Cause:** `datum_offset_in = 45.5` and `fs_wing_le = 125.61` were fitted to hit 108, the
canard had an invented taper and sweep, and the "published" 108 itself had no source.
**Solution:** Book geometry in the published frame, with a `GEOMETRY_PROVENANCE` table enforced by
test. Physics is a check, not a fit. Failing bounds become strict xfails citing numbered rows in
`docs/geometry-correction-ledger.md`, and no tolerance is ever widened.
**Key Insight:** A model that agrees with a reference too well was probably tuned to it. Honest
failures with a ledger are how the real errors were found: the wing-panel convention, a sweep-term
bug, and the downwash applied to the whole wing.

### The owner's eyes are a source; register them
<!-- problem_type: workflow -->
<!-- component: data/sources/registry.yaml (owner-check) -->
<!-- date: 2026-09-29 -->

**Problem:** Values read off a scanned drawing by an agent are claims. Agents misread hand-lettered
digits more than once.
**Root Cause:** OCR and model reads of hand lettering are unreliable, and some values exist only as
drawings.
**Solution:** The owner's by-eye reads are a registered source (`owner-check`), cited like any page.
Captains re-read every model-bound value on the page image before it enters config. Template-only
shapes (A-sheets the owner doesn't hold) are `representational`, striped in the lab and labelled
"(fitted shape)".
**Key Insight:** Fidelity has to be visible where people look (the lab), not only in a table.

### Deterministic time makes films and tests exact
<!-- problem_type: architecture -->
<!-- component: guide/lab (step(dt), ?rec=1, ?freeze=1) -->
<!-- date: 2026-09-30 -->

**Problem:** Flow animations and pulses made pixel tests flaky under load, and films need
frame-perfect output.
**Root Cause:** Wall-clock animation.
**Solution:**
- All simulation advances only through `step(dt)`, following the airsup lab's design.
- `?freeze=1` hands the clock to a test.
- `?rec=1` disables the frame loop so the recorder steps frames itself.
- Two renders of the same frames come out byte-identical (an e2e test checks it).
**Key Insight:** If you might ever record or screenshot-test an animated scene, make time an input
from the first commit.

### Keep render contracts narrow when the scene grows
<!-- problem_type: integration -->
<!-- component: guide/export_glb.py, guide/render_cutaway.sh, guide/render_key.py -->
<!-- date: 2026-09-30 -->

**Problem:** Adding the fuselage to the exported model broke the headless-Blender cutaway stills.
**Root Cause:** The render job's contract assumes a canard-only scene spanning B.L. 0 to semi-span.
A crew member had narrowed the export test's range check to canard meshes, which hid the break.
**Solution:** The export writes a canard-only copy (`output/guide/canard/`) for the render job and
the render key, with a test pinning its node set and extent. Every script that keys renders (deploy,
cutaway, public publish) points there.
**Key Insight:** When a downstream consumer has a contract, export exactly what it needs instead of
the growing whole. Treat any narrowing of a test's scope as a red flag in review.

### A validation claim needs a test id, like a value needs a page
<!-- problem_type: workflow -->
<!-- component: core/simulation/fea_adapter.py, TODOS.md, roadmap section 5 -->
<!-- date: 2026-10-07 -->

**Problem:** The roadmap and TODOS said the laminate kernel had been checked against a textbook
E-glass case. Block 3 planned around that.
**Root Cause:** No such test ever existed in this repo (ledger row 72). The sentence was most likely
carried over from an earlier project, and nobody asked for the test that backed it.
**Solution:** Before relying on "X was validated", grep the tests and git history for it. The
Block 3 kernels are validated from zero against registered published data.
**Key Insight:** A claimed check is a claim. Treat "validated against" without a test id as
`unsourced`.
