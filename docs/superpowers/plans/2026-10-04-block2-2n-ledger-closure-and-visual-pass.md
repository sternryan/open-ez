# Block 2 exit (2.n ledger closure) and visual pass: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Block 2 with a per-system mass ledger whose empty weight and CG are graded against the OM sample empty airplane (730 lb at FS 111.7), with a tolerance derived and capped in advance, and clear the visual backlog: camera-aware near-wall culling plus the three M2.9 nits.

**Architecture:** Part A adds one closure table (`data/mass_ledger.yaml`, new `closure:` block) and one pure module (`core/closure.py`) that sums the table with interval bands. A strict test grades the target against the computed band and refuses a band too wide to decide the OM sample verdicts. The row values are fixed and committed before any code sums them. Part B splits the workshop's merged wall batch into per-plane meshes. A pure function (`logic/roomCull.ts`) picks which planes to hide from the camera position, and the render loop applies it every frame. An e2e test pins subject pixels at max zoom-out.

**Tech Stack:** Python 3.12 venv (pytest), PyYAML; TypeScript lab (three.js, `node:test` via `npm test` = `node --import tsx --test tests/*.test.ts`), Playwright e2e in `tests/guide/test_lab_e2e.py`.

**Spec:** Block 2 rehearsal design `docs/superpowers/specs/2026-09-30-block2-rehearsal-design.md` (2.n exit test), as corrected by ledger rows 63 and 64 and the 10-04 lead-accepted target in the 10-03 M2.6 handoff (COLD START). Inputs: `docs/harness/m29-research-c.md` sections 5, 7 and 8; `m28-research-b.md`; `config/aircraft_config.py` `WEIGHT_PROVENANCE`; `docs/harness/block2-m29-visual-review.md`.

## Global Constraints

- PUBLIC repo: no hostnames, IPs, home paths, plans pages, scans, OCR text; paraphrase sources in 10 words or fewer.
- Every value is `book`, `cp-corrected`, `derived` with a registry cite, or flagged `conflict` / `unsourced` / `converted-unsourced`. Never upgrade a flag without a page in hand. Never measure an undimensioned image and call it a source.
- A bound the book geometry fails stays failing (strict `xfail` citing its ledger row). Never widen it. Record every moved test in `docs/geometry-correction-ledger.md` (next free row: 65).
- A gate counts only after it has been shown to fail on a deliberately broken input.
- All arms in the closure table are PUBLISHED FS. The config's internal datum is shifted 45.5 in. Convert at the boundary only, in one named helper.
- Ledger arithmetic is a deterministic script. No LLM computes or checks a sum.
- Stage named files; never `git add -A`. Crews stage, the captain sends the split, the lead commits (`infra_captains_share_session_cwd_gate`).
- No push without the lead's go, via the push gate. Renders and deploys take the anvil GPU lease: heads-up to the lead first.
- Do not touch the two-method NP. It stays a strict xfail (ledger row 62, +1.62 in). The closure does not change the analysis planform, so VSPAERO is not re-run. The stale-marker guard is the check.
- Linux vs Mac float ties are fixed, not marked.
- Never write a Claude-Session trailer.

## Review Focus

1. **Tuning to the target.** If a row's value is chosen after the sum is seen, the closure proves nothing. Expected: the row table, the engine-arm METHOD and the predicted gap are committed (Task 1) before any sum code exists. `test_table_is_the_frozen_one` asserts that the content sha256 of the block (no git; the remote lanes rsync without `.git`) is the one recorded in ledger row 65.
2. **A vacuous band.** Wide enough bands make any target "inside". Expected: the CG half-band is capped at 1.46 in, the empty-CG shift that flips the light sample (computed below). The weight half-band is capped at 20 lb. Over either cap, the exit test strict-xfails with the cap named in its reason. It never passes, and the rest of the suite stays green. Task 2, `verdict()` and `test_empty_closes_on_the_om_sample`.
3. **Light-sample verdict from the ledger.** Expected: with the ledger's own empty weight and CG, the light sample lands aft of 103 and the heavy sample inside 97 to 103. Task 2, `test_om_samples_from_the_ledger_empty`.
4. **Wall culling while the camera flies.** During a shot transition the eye crosses a wall plane. Expected: no frame where a visible plane sits between eye and bench. Task 5, the 7.5 m sphere sweep in `roomCull.test.ts`. Task 6, the 232-op `blocks` sweep.
5. **Phone portrait.** `rig.scale` pulls every shot back up to 3.2x on portrait, so most phone shots leave the room. Expected: the subject still reads at 390x844. Task 6, `test_max_zoom_out_subject_pixels_hold` runs at 390x844 and 1180x820.

### Numbers the plan is built on (computed by script on 2026-10-04, deterministic)

| Quantity | Value |
|---|---|
| Light sample from the 730 @ 111.7 row | 1113 lb, moment 115706, CG 103.959 |
| Heavy sample | 1323 lb, moment 133706, CG 101.063 |
| Empty-CG shift that moves the light sample to 103 | -1.462 in (forward) |
| Empty-CG shift that moves the heavy sample to 103 / 97 | +3.511 / -7.363 in |
| Empty-weight error at FS 111.7 that moves the light sample to 103 | -122.6 lb (weight is not the sensitive axis) |
| 81541 / 727.9 (weighing-table net) | CG 112.022, 0.32 in aft of 111.7 |
| Engine 243 lb: empty-CG shift per 1 in of engine arm error | 0.333 in |

The engine arm alone flips the light-sample verdict at a 4.4 in error. The closure is effectively a one-unknown CG problem, and the unknown is the engine arm.

---

## Part A: 2.n ledger closure

```
 sources (OM, CP26/27, plans)          frozen before any sum           deterministic
 ───────────────────────────►  closure: block in mass_ledger.yaml ──► core/closure.py ──► tests/test_ledger_closure.py
   crew + captain page re-read   + sha256 of the block in row 65        exact interval      (1) method check: N26MS rows vs
   engine-arm METHOD written                                            CG band              N26MS ladder step 1 (693.4)
   before any arm value                                                                      (2) exit: OM 730 @ 111.7 within caps
                                                                                             (3) OM samples from the ledger empty
                                                    Task 3 fold-in (config, report) runs ONLY after (2) is measured
```

### Rulings this plan makes (captain, engineering-internal; recorded in ledger row 65)

- **Target 730, not 727.9.** The sample loadings all use 730, and 111.7 = 81541/730. The 2.1 lb net slip is an erratum (om-1980:p35). Task 2 asserts that the closure VERDICT is identical for both targets. If it is not, the choice matters and goes to Ryan.
- **Two airplanes, two checks (review D2).** The per-part rows are mostly N26MS builder weights. The target is the OM sample airplane. N26MS's own painted basic empty weight is 693.4 lb (CP27 p4 ladder step 1), already 36.6 lb under 730. So:
  - (1) **Method check, same airplane.** The N26MS-sourced rows plus the step-1 configuration must reproduce 693.4 lb within their own bands. This tests the per-part method with no inter-airplane offset.
  - (2) **Exit test.** The OM 730 @ 111.7 within the caps. The predicted gap is pre-registered in row 65 before the sum is run: weight about +17 to +37 lb from ladder steps 1 to 3 (basic electrical sits between them). A miss is the expected honest outcome.
- **Tolerance is computed, then capped.** Each row carries a weight band and an arm band from its source class:
  - `book`: zero band.
  - `builder` (N26MS): the published finish delta, else ±5 percent.
  - `derived`: the band in its derivation.
  - `allowance`: its stated range.
  - `unsourced`: ±50 percent and ±10 in.
  
  Caps:
  - CG 1.46 in: the empty-CG shift that moves the light sample to 103.
  - Weight 20 lb: the OM's own spread, 730 sample against about 750 normally equipped, om-1980:p4.
  
  Over a cap, or outside the band, the exit test is a strict xfail whose reason names which cap or bound failed and by how much. **Ryan ruling 10-04:** in that case Block 2 CLOSES with the failure recorded, as with the Block 1 NP. It never widens. The rest of the suite stays green (review D5).
- **Builder weights may enter closure rows.** Only single-part N26MS weights qualify. Ladder steps stay reference-only, except step 1 as the method-check target. Row 65 records the relabel of the "never summed" notes.
- **Wing:** 2 x 64 = 128 lb ready to finish (CP26 p3, with winglets, rudder and aileron), plus finish 2 x 2.2 (derived, CP27 p1). Row 132.4, band [128.0, 132.6].
- **Electrical:** two rows, from ladder deltas, `derived`.
  - Battery: nose, arm band FS 0 to 22.
  - Starter, ring gear, alternator: FS 150 and aft (CP27 p4). Weight band down to 0, since the OM airplane is basic electrical.
- **Engine:** mass 243 lb, `conflict` with 249.1, band [243, 249.1]. The book limit is 246 (plans-1980:p156).
  - **The arm method is written down before any arm value is computed (review D3)**, as at the C4 downwash precedent. First choice: a registerable O-235 installation CG. Else: firewall FS 125 + mount standoff + crankcase CG from a cited engine drawing.
  - The arm is the single degree of freedom that decides the CG (0.333 in of empty CG per inch). Whoever picks the method has seen 111.7, so the method text goes to the Task 4 adversary BEFORE the value is computed.

### Task 1: Closure row table and engine-arm method (frozen before any sum)

**Files:**
- Modify: `data/mass_ledger.yaml` (append `closure:` with `rows`, `method_check_rows` (the subset that is N26MS step-1 configuration), `predicted_gap`, `engine_arm_method`)
- Modify: `data/sources/registry.yaml` (only if an engine CG source is registered)
- Modify: `docs/geometry-correction-ledger.md` (row 65: rulings, the predicted gap, the engine-arm method text, and the sha256 of the canonical closure block)
- Create: `scripts/closure_hash.py` (prints sha256 of `json.dumps(closure_block, sort_keys=True, separators=(",", ":"))`)
- Test: `tests/test_closure_table.py`

**Interfaces:**
- Produces: `closure.rows[]`. Each row: `name, weight_lb, weight_band_lb: [lo, hi], arm_fs, arm_band_fs: [lo, hi], status (book|builder|derived|allowance|unsourced|conflict), cite: [..], note`.
- Produces: `core.closure.block_sha256() -> str`. Task 1 ships it alone, so the freeze test has no git dependency. The remote lanes rsync with `--exclude .git` (`scripts/remote_test.sh:22`).

- [ ] **Step 1: Write the table test**

```python
# tests/test_closure_table.py
from core.ledger import load_ledger
from core.sources import check_citation
from core.closure import block_sha256

C = load_ledger()["closure"]; ROWS = C["rows"]
OK = {"book", "builder", "derived", "allowance", "unsourced", "conflict"}

def test_every_row_has_bands_status_and_cites():
    for r in ROWS:
        lo, hi = r["weight_band_lb"]; alo, ahi = r["arm_band_fs"]
        assert lo <= r["weight_lb"] <= hi and alo <= r["arm_fs"] <= ahi, r["name"]
        assert r["status"] in OK, r["name"]
        if r["status"] != "unsourced":
            assert r["cite"] and all(check_citation(c) for c in r["cite"]), r["name"]

def test_no_ladder_step_is_a_row():
    assert not any(r["name"].startswith("n26ms_empty") for r in ROWS)

def test_book_rows_carry_no_weight_band():
    for r in ROWS:
        if r["status"] == "book":
            assert r["weight_band_lb"][0] == r["weight_band_lb"][1] == r["weight_lb"]

def test_engine_arm_method_and_prediction_are_written_down():
    assert C["engine_arm_method"]["text"] and C["predicted_gap"]["weight_lb"]

def test_table_is_the_frozen_one():   # editing the block needs a new ledger row with the new hash
    assert block_sha256() in open("docs/geometry-correction-ledger.md").read()

def test_hash_changes_when_a_row_moves(monkeypatch):   # the freeze gate fails on a broken input
    before = block_sha256()
    monkeypatch.setitem(ROWS[0], "weight_lb", ROWS[0]["weight_lb"] + 0.1)
    assert block_sha256() != before
```

- [ ] **Step 2:** Run `.venv/bin/python -m pytest -q tests/test_closure_table.py`. Expected: FAIL, `KeyError: 'closure'` / ImportError.
- [ ] **Step 2b (Ryan GO 10-04, ruling 2): public-source engine research, before the arm method is final.**
  - A Sonnet crew uses WebSearch and WebFetch on public sources:
    - the Lycoming installation and operator manuals for the book's engine model (dry weight, CG location and its datum);
    - the Canard Pusher and Central States Association archives;
    - published Long-EZ weight-and-balance data.
  - Each value is cited as URL + page and graded A (manufacturer document), B (designer or newsletter), C (builder or forum).
  - A value enters the table only after it is registered in `data/sources/registry.yaml` (a public URL is fine; no copyrighted text is committed).
  - Report: `docs/harness/2n-engine-research.md`. Astra stays the adversarial check on the arm method.
- [ ] **Step 3:** Add `block_sha256` to a new `core/closure.py` (only this function in Task 1):

```python
import hashlib, json
from core.ledger import load_ledger
def block_sha256() -> str:
    b = load_ledger()["closure"]
    return hashlib.sha256(json.dumps(b, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
```

- [ ] **Step 4:** The Sonnet sourcing crew fills `closure:` from `m29-research-c.md` section 7 and the rulings.
  - The captain re-reads every model-bound value on its page image.
  - The captain writes `engine_arm_method` and `predicted_gap` first.
  - The engine CG hunt is capped at 45 min.
  - **The crew writes and runs no sum.**
- [ ] **Step 5:** Run Task 4 (the adversary) on the method text, caps and prediction. Adjudicate, then compute the engine arm by the written method.
- [ ] **Step 6:** Run `.venv/bin/python scripts/closure_hash.py`, paste the hash into row 65, and run the tests. Expected: PASS. The crew stages the named files and the lead commits.

### Task 2: Closure module and the exit test

**Files:**
- Modify: `core/closure.py`
- Test: `tests/test_ledger_closure.py`

**Interfaces:**
- Consumes: `closure.rows`, `closure.method_check_rows`, `load_ledger`.
- Produces:
  - `Closure` NamedTuple: `(weight_lb, cg_fs, weight_band: tuple[float, float], cg_band: tuple[float, float])`;
  - `closure_sum(rows=None) -> Closure`;
  - `cg_band(rows) -> tuple[float, float]` (exact);
  - `loaded_cg(empty_w, empty_cg, sample) -> float`;
  - `verdict(c: Closure, target_w, target_cg) -> str`, which returns `'closes'` or a reason naming the failed cap or bound with its measured gap;
  - `CG_CAP_IN`, `WEIGHT_CAP_LB`.

- [ ] **Step 1: Failing tests**

```python
# tests/test_ledger_closure.py
import itertools, pytest
from core import closure as cl
from core.ledger import load_ledger

L = load_ledger(); T = L["empty"]

def test_caps_are_the_book_derived_values():
    assert cl.CG_CAP_IN == pytest.approx(1.462, abs=0.001) and cl.WEIGHT_CAP_LB == 20.0

def _brute(rows):
    best = [float("inf"), float("-inf")]
    for ws in itertools.product(*[r["weight_band_lb"] for r in rows]):
        for side in (0, 1):
            arms = [r["arm_band_fs"][side] for r in rows]
            c = sum(w * a for w, a in zip(ws, arms)) / sum(ws)
            best = [min(best[0], c), max(best[1], c)]
    return tuple(best)

def test_cg_band_is_exact_against_brute_force():   # 2^n weight corners; n <= 16 real rows is 65k, fine
    rows = L["closure"]["rows"]
    lo, hi = cl.cg_band(rows); blo, bhi = _brute(rows)
    assert (lo, hi) == pytest.approx((blo, bhi), abs=1e-6)

def test_cg_band_fails_on_a_one_pass_corner_rule():   # broken-input proof for the band math
    rows = [{"weight_band_lb": [1, 9], "arm_band_fs": [0, 0]}, {"weight_band_lb": [1, 9], "arm_band_fs": [100, 100]},
            {"weight_band_lb": [5, 5], "arm_band_fs": [40, 40]}]
    assert cl.cg_band(rows) == pytest.approx(_brute(rows), abs=1e-9)

def test_method_check_reproduces_the_n26ms_step_1():
    c = cl.closure_sum(L["closure"]["method_check_rows"])
    assert c.weight_band[0] <= L["prototype_weights"]["rows"]["n26ms_empty_1"]["weight_lb"] <= c.weight_band[1]

C = cl.closure_sum()
_V = cl.verdict(C, T["weight_lb"], T["arm_in"])

@pytest.mark.xfail(_V != "closes", strict=True, reason=f"ledger row 65: {_V}")
def test_empty_closes_on_the_om_sample():
    assert _V == "closes"

def test_verdict_is_the_same_for_727_9_and_730():
    assert (cl.verdict(C, 727.9, 81541 / 727.9) == "closes") == (_V == "closes")

def test_om_samples_from_the_ledger_empty():
    assert cl.loaded_cg(C.weight_lb, C.cg_fs, "light_pilot") > 103.0
    assert 97.0 <= cl.loaded_cg(C.weight_lb, C.cg_fs, "heavy_pilot") <= 103.0

def test_moving_the_engine_arm_5_in_moves_the_empty_cg_by_its_moment_share():
    rows = [dict(r) for r in L["closure"]["rows"]]
    eng = next(r for r in rows if r["name"] == "engine")
    base = cl.closure_sum(rows).cg_fs
    eng["arm_fs"] -= 5; eng["arm_band_fs"] = [a - 5 for a in eng["arm_band_fs"]]
    moved = cl.closure_sum(rows)
    assert base - moved.cg_fs == pytest.approx(eng["weight_lb"] * 5 / moved.weight_lb, rel=1e-9)
    assert cl.loaded_cg(moved.weight_lb, moved.cg_fs, "light_pilot") < cl.loaded_cg(C.weight_lb, C.cg_fs, "light_pilot")
```

`test_om_samples_from_the_ledger_empty` is a plain assert because it is the OM's own verdict. If the ledger empty flips it, that is a finding: strict-xfail it with the reason, under row 66.

- [ ] **Step 2:** Run the tests. Expected: FAIL (`cg_band` and friends are missing).
- [ ] **Step 3: Implement (exact band, no one-pass rule)**

```python
# core/closure.py (added to block_sha256 from Task 1)
from typing import NamedTuple
_E = load_ledger()["empty"]; _LIGHT = load_ledger()["samples"]["light_pilot"]
CG_CAP_IN = round((103.0 - _LIGHT["book_cg_in"]) * _LIGHT["book_total_lb"] / _E["weight_lb"], 3)  # 1.462
WEIGHT_CAP_LB = 20.0

class Closure(NamedTuple):
    weight_lb: float; cg_fs: float
    weight_band: tuple[float, float]; cg_band: tuple[float, float]

def _reach(rows, c, side) -> bool:
    """Is a CG beyond c (aft if side=1, fwd if 0) reachable? Each row picks the weight that helps most."""
    s = 1 if side else -1
    return sum(max(w * (r["arm_band_fs"][side] - c) * s for w in r["weight_band_lb"]) for r in rows) >= 0

def cg_band(rows) -> tuple[float, float]:
    out = []
    for side in (0, 1):
        lo = min(r["arm_band_fs"][0] for r in rows); hi = max(r["arm_band_fs"][1] for r in rows)
        for _ in range(80):   # bisection to well under 1e-9 in
            mid = (lo + hi) / 2
            if _reach(rows, mid, side) == bool(side): lo = mid
            else: hi = mid
        out.append((lo + hi) / 2)
    return out[0], out[1]

def closure_sum(rows=None) -> Closure:
    rows = rows if rows is not None else load_ledger()["closure"]["rows"]
    w = sum(r["weight_lb"] for r in rows); m = sum(r["weight_lb"] * r["arm_fs"] for r in rows)
    return Closure(w, m / w, (sum(r["weight_band_lb"][0] for r in rows), sum(r["weight_band_lb"][1] for r in rows)), cg_band(rows))

def verdict(c: Closure, tw: float, tcg: float) -> str:
    hw = (c.weight_band[1] - c.weight_band[0]) / 2; hc = (c.cg_band[1] - c.cg_band[0]) / 2
    if hc > CG_CAP_IN: return f"CG half-band {hc:.2f} in over the {CG_CAP_IN} in cap"
    if hw > WEIGHT_CAP_LB: return f"weight half-band {hw:.1f} lb over the {WEIGHT_CAP_LB} lb cap"
    if not c.weight_band[0] <= tw <= c.weight_band[1]: return f"weight {c.weight_lb:.1f} lb, band misses {tw} by {min(abs(tw - b) for b in c.weight_band):.1f} lb"
    if not c.cg_band[0] <= tcg <= c.cg_band[1]: return f"CG {c.cg_fs:.2f}, band misses {tcg} by {min(abs(tcg - b) for b in c.cg_band):.2f} in"
    return "closes"

def loaded_cg(empty_w: float, empty_cg: float, sample: str) -> float:
    L = load_ledger(); s = L["samples"][sample]; arms = L["loads"]
    W = empty_w + sum(s["items"].values())
    return (empty_w * empty_cg + sum(v * arms[k]["arm_in"] for k, v in s["items"].items())) / W
```

(The crew checks `_reach`'s bisection direction against the brute-force test. That test is the arbiter, not this sketch.)

- [ ] **Step 4:** Run the tests. Expected: everything passes, and the exit test reports XFAIL with its reason, or PASS when it closes. Record the verdict string in row 65.
- [ ] **Step 5:** The crew stages `core/closure.py tests/test_ledger_closure.py` and the lead commits.

### Task 3: Fold the closure into the analysis rows and report (after Task 2 is measured)

Fold only rows whose status is not `unsourced`. An unsourced row keeps its current config value and flag, so an unsourced guess never replaces another unsourced guess (review D1).

**Files:**
- Modify: `config/aircraft_config.py` (`structural_weights`):
  - `wing_weight_lb`;
  - electrical split into two field pairs;
  - `engine_cg_arm_in`;
  - `engine_mass_kg` / `engine_dry_weight_lb`;
  - `WEIGHT_PROVENANCE`.
- Modify: `scripts/generate_accuracy_report.py`. Add a new `empty_weight_closure` metric that reads `verdict()`. The 750 metric stays, labelled a different configuration (row 63).
- Regenerate: `data/validation/accuracy_report.json`
- Modify: `tests/test_m28_weight_flags.py`, `tests/test_ssot_weights.py`, `tests/test_regression_lock.py` (locks follow computed values only)
- Modify: `guide/fuselage_export.py` and the f26 readout. The closure card shows the ledger value and the verdict string beside the target.
- Modify: `docs/geometry-correction-ledger.md` row 66, `TODOS.md`, `AGENTS.md` Known Issues

- [ ] **Step 1:** Write `tests/test_closure_fold_in.py::test_config_rows_equal_the_sourced_closure_rows`, which goes through one datum helper (published FS = internal + 45.5). Also write `::test_analytic_np_does_not_read_any_weight_field`: perturb every `*_weight_lb` by +10 percent and assert the NP is unchanged to 1e-9. That turns the "NP won't move" claim into a test.
- [ ] **Step 2:** Run them. Expected: the fold-in test FAILS (85 != 132.4). The NP test PASSES now and must keep passing.
- [ ] **Step 3:** Change the config and provenance. Then run `.venv/bin/python scripts/generate_accuracy_report.py`.
- [ ] **Step 4:** Run the full Python suite, then `node --test guide/viewer/tests/*.test.mjs`, then the lab unit tests (`cd guide/lab && npm test`). Fix only computed-value locks.
- [ ] **Step 5:** Fan-out via the job runner (run-job + await-job). Poll the log's `remote_test_all:` line, never `pgrep -f`. The lead commits.

### Task 4: Adversarial second opinion (runs inside Task 1, Step 5, before any arm value)

- [ ] One `codex exec -m gpt-6-astra --skip-git-repo-check` call. Input: the rulings, the numbers table, the engine-arm method text, the caps, the predicted gap and `core/closure.py`. Ask it to break four things:
  1. the caps;
  2. the band math;
  3. the claim that 730 vs 727.9 cannot flip the verdict;
  4. whether the arm method can be steered toward 111.7.

  No Sol, Terra or Luna. The captain adjudicates. Divergence goes into row 65 as text.

---
## Part B: visual pass

### Diagnosis (read first)

`rig.clampPos` (`guide/lab/src/main.ts:364`) clamps only the rig's authored landing positions (`camera.ts` `scaled()`). The user's wheel or pinch dolly goes through OrbitControls up to `controls.maxDistance = 7.5` m (`main.ts:331`), unclamped. The room is 9.5 x 8.4 m with the bench near the middle, so a full zoom-out puts the eye outside a wall. The wall is a closed `BoxGeometry` slab (`workshop.ts:113-114`), so its outer face renders and fills the frame. That is Ryan's step 132 report. The cull is not a no-op, because the eye really does leave the room.

```
  eye (user dolly, unclamped) ──► outside wall plane? ──yes──► hide that plane's group (wall + wainscot + props on it)
        │                                   └─no──► visible
  authored shot (clamped inside) ──► never outside ──► all planes visible (unchanged look)
```

### Task 5: Per-plane room groups and the cull rule

**Files:**
- Create: `guide/lab/src/logic/roomCull.ts`
- Modify: `guide/lab/src/scene/workshop.ts:107-121` and the window, door, lamp and pegboard blocks.
  - Each plane gets its own `THREE.Group`: `room.back`, `room.door`, `room.window`, `room.side`, `room.ceiling`.
  - Every item fixed to a plane goes into that plane's group: the wall slab, wainscot, window glazing and frame, door, lamp strip and pegboard. Beams and fixtures go into `room.ceiling`.
  - `Batch.flush` takes a target group per key prefix.
  - Workshop returns `planes: RoomPlane[]` and `planeGroups: Record<string, THREE.Group>`.
  - The floor is never culled (`maxPolarAngle` keeps the eye above it).
- Test: `guide/lab/tests/roomCull.test.ts` (node:test, like the other lab tests)

**Interfaces:**
- Produces:
  - `type RoomPlane = { key: string; n: [number, number, number]; d: number }`: the inward normal, with inside meaning `n·p − d > 0`;
  - `roomPlanes(R): RoomPlane[]`;
  - `hiddenPlanes(eye: Vec3, planes: RoomPlane[], marginM = 0.05): Set<string>`;
  - `blocks(eye: Vec3, target: Vec3, planes: RoomPlane[], hidden: Set<string>): string[]`, the visible planes the eye-to-target segment crosses.

Hide is binary, with no transparent ghost (review D9). The lab renders through `Pipeline` with SSAO (`main.ts`, `new Pipeline(renderer, { ao: ... })`), and a transparent wall there would draw AO halos and sort wrongly.

- [ ] **Step 1: Failing test**

```ts
// guide/lab/tests/roomCull.test.ts
import test from 'node:test'
import assert from 'node:assert/strict'
import { hiddenPlanes, blocks, roomPlanes } from '../src/logic/roomCull'
import { ROOM } from '../src/scene/workshop'
const P = roomPlanes(ROOM)
const T: [number, number, number] = [0, 0.9, 0] // the bench
test('inside the room nothing hides', () => assert.equal(hiddenPlanes([0, 1.5, 0], P).size, 0))
test('beyond the room-side wall only that plane hides', () =>
  assert.deepEqual([...hiddenPlanes([0, 1.5, ROOM.z1 + 2], P)], ['room.side']))
test('beyond a corner both planes hide', () =>
  assert.deepEqual(new Set(hiddenPlanes([ROOM.x1 + 1, 1.5, ROOM.z1 + 1], P)), new Set(['room.back', 'room.side'])))
test('above the ceiling the ceiling hides', () => assert.ok(hiddenPlanes([0, ROOM.h + 1, 0], P).has('room.ceiling')))
test('no visible plane blocks the bench from any eye on a 7.5 m sphere', () => {
  for (let az = 0; az < 360; az += 5) for (let el = 2; el < 89; el += 6) {
    const a = (az * Math.PI) / 180, e = (el * Math.PI) / 180
    const eye: [number, number, number] = [T[0] + 7.5 * Math.cos(e) * Math.cos(a), T[1] + 7.5 * Math.sin(e), T[2] + 7.5 * Math.cos(e) * Math.sin(a)]
    assert.deepEqual(blocks(eye, T, P, hiddenPlanes(eye, P)), [], `az ${az} el ${el}`)
  }
})
test('broken input: with nothing hidden, an outside eye IS blocked (the gate can fail)', () =>
  assert.deepEqual(blocks([0, 1.5, ROOM.z1 + 2], T, P, new Set()), ['room.side']))
```

- [ ] **Step 2:** Run `cd guide/lab && node --import tsx --test tests/roomCull.test.ts`. Expected: FAIL, module missing.
- [ ] **Step 3: Implement**

```ts
// guide/lab/src/logic/roomCull.ts
export type Vec3 = [number, number, number]
export type RoomPlane = { key: string; n: Vec3; d: number }
type Room = { x0: number; x1: number; z0: number; z1: number; h: number }
/** Inward planes of the room box (the wall slabs stand just outside them). A target inside a convex room can be hidden by a
 *  plane only when the eye is outside that plane, so the rule needs only the eye. `blocks` is the check, not the rule. */
export const roomPlanes = (R: Room): RoomPlane[] => [
  { key: 'room.back', n: [-1, 0, 0], d: -R.x1 }, { key: 'room.door', n: [1, 0, 0], d: R.x0 },
  { key: 'room.window', n: [0, 0, 1], d: R.z0 }, { key: 'room.side', n: [0, 0, -1], d: -R.z1 },
  { key: 'room.ceiling', n: [0, -1, 0], d: -R.h },
]
const side = (p: RoomPlane, v: Vec3) => p.n[0] * v[0] + p.n[1] * v[1] + p.n[2] * v[2] - p.d
export function hiddenPlanes(eye: Vec3, planes: RoomPlane[], marginM = 0.05): Set<string> {
  return new Set(planes.filter((p) => side(p, eye) < marginM).map((p) => p.key))
}
export function blocks(eye: Vec3, target: Vec3, planes: RoomPlane[], hidden: Set<string>): string[] {
  return planes.filter((p) => !hidden.has(p.key) && side(p, eye) * side(p, target) < 0).map((p) => p.key)
}
```

- [ ] **Step 4:** Run it. Expected: PASS. Then `cd guide/lab && npm test`. `parity`/`smoke` mesh counts move, so update them with a one-line comment.
- [ ] **Step 5:** The crew stages the named files and the captain sends the split.

### Task 6: Apply the cull every frame and pin it in e2e

**Files:**
- Modify: `guide/lab/src/main.ts`.
  - In the tick, after `controls.update()`, compute `hiddenPlanes(camera.position)`. Set `planeGroups[k].visible` only on change.
  - The shadow map stays as rendered once.
  - Expose `__lab.room() -> {hidden: string[], blocks: string[]}` and `__lab.zoomTo(d)`, which dollies along the current view direction.
  - Honour a test-only `?nocull=1`.
- Test: `tests/guide/test_lab_e2e.py`

- [ ] **Step 1: Failing e2e (one page, stepped through ops; no page reload per op, review D10)**

```python
@pytest.mark.parametrize("w,h,dpr", [(1180, 820, 1), (390, 844, 2)])
def test_max_zoom_out_subject_pixels_hold(rsite, w, h, dpr):
    """Ryan 10-04: f19.shear-web zoomed out, the near wall filled the frame. Subject pixels are the frame difference with the op's
    parts hidden (the __lab.hide diff at test_lab_e2e.py:5662), so no colour guessing."""
    with _lab_session(rsite, w, h, dpr) as pg:               # new helper: one page, opened once with _open (:144)
        for op in ["f19.shear-web", "f24.gap-seal", "f25.paint-seals", "f12.canard-install"]:
            _step_to(pg, op)                                  # new helper: __lab.go(op) + __lab.advance until the rig lands
            base = _subject_pixels(pg, op)
            pg.evaluate("window.__lab.zoomTo(7.5); window.__lab.advance(0.5)")
            far = _subject_pixels(pg, op)
            assert far >= 400 * dpr * dpr, f"{op}: {far} px at max zoom-out (framed {base})"
            assert pg.evaluate("window.__lab.room().blocks") == [], op

def test_max_zoom_out_fails_without_cull(rsite):          # the gate fails on the real broken input
    with _lab_session(rsite, 1180, 820, 1, query="nocull=1") as pg:
        _step_to(pg, "f19.shear-web"); pg.evaluate("window.__lab.zoomTo(7.5); window.__lab.advance(0.5)")
        assert _subject_pixels(pg, "f19.shear-web") < 400 or pg.evaluate("window.__lab.room().blocks") != []

def test_every_op_at_max_zoom_out_has_no_blocking_wall(rsite):
    with _lab_session(rsite, 1180, 820, 1) as pg:
        for op in pg.evaluate("window.__lab.opIds()"):        # 232 ops, logic-only check, no screenshots
            _step_to(pg, op); pg.evaluate("window.__lab.zoomTo(7.5); window.__lab.advance(0.2)")
            assert pg.evaluate("window.__lab.room().blocks") == [], op
```

The 400 px floor is about 0.04 percent of a 1180x820 frame. The fix must clear it with margin at f19.shear-web. Before the cull, the near wall leaves 0 subject pixels there. The crew records both numbers in the commit message. Time `test_every_op...` on the Mac lane: budget ≤ 90 s, otherwise sample one op per chapter.

- [ ] **Step 2:** Add only the `__lab` hooks and helpers. Then run `-k "max_zoom_out or every_op_at_max"` on the Mac lane. Expected: FAIL at f19.shear-web on BOTH `blocks` and the pixel floor.
- [ ] **Step 3:** Wire `hiddenPlanes` into the tick.
- [ ] **Step 4:** Run them. Expected: PASS at both sizes, and `..._fails_without_cull` passes. Then run the whole e2e file on the Mac lane, then the fan-out.
- [ ] **Step 5:** The crew stages the files and the captain sends the split.

### Task 7: The three M2.9 nits

**Files:** `guide/lab/src/fuseShots.ts:279-292`, `guide/lab/src/logic/finish.ts`, `guide/lab/src/main.ts` (card dock), `tests/guide/test_lab_e2e.py`

- [ ] (a) **`f24.gap-seal` washed out.** The context airplane is dimmed hard and the eye at az 10 looks toward the window light.
  - Test: the subject's mean luminance contrast against its 12 px ring is ≥ 0.6 times the value at f24.console-lc1, at both sizes.
  - Fix: raise the context-dim floor for this op only, and move az to the room side (about 160), el 40.
- [ ] (b) **`f24.aft-cover` reads small.**
  - Test: subject pixel share ≥ 2 percent of the 3D viewport at 1180x820 and ≥ 1 percent at 390x844.
  - Fix: dist 125 → about 80, keeping el -8.
- [ ] (c) **The card covers the canard tip on f25 ops.**
  - Test: the projected canard-tip box does not intersect the step card's DOM rect at either size. This extends the existing no-label-under-a-card rule to model extents.
  - Fix: move the WHOLE() focus aft and to the right, or dock the card opposite.
- [ ] Each lands failing-test-first, then the Mac subset, then the fan-out.

### Task 7d (separate, optional this sprint): release the room clamp for whole-airplane shots

With the cull live, the carried nit "room clamp cuts wing tips" (f19.attach and the finish ops) is fixable: skip `clampPos` for shots tagged `outside: true`.
- Test: both wing tips are inside the viewport on those ops at both sizes, and `__lab.room().blocks` is empty.
- This is a behaviour change to the authored shots. It gets its own commit and its own visual-review line, and it is cut if it slips.

### Task 8: Visual review and deploy (lead go only)

- [ ] Opus captain visual review (WebKit 1180x820 plus three phone shots):
  - f19.shear-web at max zoom-out;
  - all 13 f24-26 ops;
  - one op per chapter at max zoom-out.

  Verdict written to `docs/harness/block2-2n-visual-review.md`.
- [ ] grade-diff PASS, leak scan, `guide.check`. Lead verify. GPU heads-up to the lead. Then `deploy_guide.sh` (expect 232 ops, unchanged), `LAB_FILM=... publish_public.sh`, and a check of the gh-pages author and public count.
- [ ] Ryan's iPad walk of ch19-26 stays owed. It does not block this.

## Crew and lane plan (sprint)

| Wave | Lane / model | Units | Why |
|---|---|---|---|
| A1 closure table sourcing | subagent / sonnet + captain page re-read | ~16 rows | page reading; Sonnet misreads digits, so the captain re-reads every bound value |
| A1 engine CG hunt | subagent / sonnet, 45 min cap | 1 | research only; no frontier |
| A2 sums, bands, caps | script (core/closure.py) written by a sonnet crew | 1 module | arithmetic is deterministic; the smithy lane fails arithmetic (09-10) |
| A3 config and report fold-in | subagent / sonnet, only after A2's verdict is recorded | ~8 files | mechanical, test-pinned; sourced rows only |
| A4 tolerance and arm-method adversary | codex / gpt-6-astra (`-m` always), inside Task 1 Step 5 | 1 call | independent method on the one judgment call, before the arm value exists |
| B5-B7 lab, cull and nits | subagent / sonnet (one crew, serial: shared main.ts; runs IN PARALLEL with Part A in its own worktree) | 3 tasks + 7d | TS + e2e, pattern-following |
| B8 visual review | captain / opus | 1 | taste ≥ 7 gate |
| Test fan-out | script (remote_test_all via run-job) | 2-3 runs | deterministic |
| VSPAERO | not run (planform unchanged) | 0 | Ryan's laptop has OpenVSP 3.48.2 (checked 10-04) if a fold-in ever moves the planform |
| smithy op-YAML | skipped | 0 | no new ops; M2.7 19/27 drafts needed fixes |

### Order and worktrees

```
Lane A (worktree the 2n worktree):  T1 table+method ─► T4 Astra ─► T1 freeze ─► T2 closure ─► T3 fold-in (sourced rows only)
Lane B (worktree the vis worktree): T5 cull logic ─► T6 wire + e2e ─► T7 nits ─► (T7d clamp release, optional)
Both lanes merge, then T8: visual review, grade, lead verify, GPU heads-up, deploy.
No shared module between lanes except tests/guide/test_lab_e2e.py (T3 touches only the f26 readout test lines; B appends new tests): merge B first.
```

## NOT in scope

- Two-method NP. It stays a strict xfail (row 62). Nothing here moves the planform, so VSPAERO is not re-run.
- Canard planform, Roncz chords, and the wing washout fold-in. These are Block 3.
- Finish mass on surfaces N26MS never weighed: an allowance row only, flagged. There is no chapter 25 weight to source.
- Sections IIA, IIC and IIL of the plans (the engine installation) are not held. Buying or requesting them is an outward or money call (Ryan).
- Other carried visual nits (tiny hardware reads small, f21.vent-screen wall). These are next pass, except where the cull fixes them for free.
- Ryan's iPad walk ch19-26. It is owed and does not block.

## What already exists (reused)

- `core/ledger.py` `Row`, `cg`, `load_ledger` and the `samples` / `loads` / `envelope` blocks. `test_manual_sample_loadings_reproduce` already reproduces both OM samples exactly from the 730 row, and stays.
- `prototype_weights` in `data/mass_ledger.yaml`, the source of the N26MS rows and ladder.
- `m29-research-c.md` section 7, the per-row best source.
- `WEIGHT_PROVENANCE` flags.
- Lab: the `__lab.hide` frame-diff pixel method (`test_lab_e2e.py:5662`), `_open` / `_lab_at` / `_bar_ops`, `rig.clampPos`, and the `Batch` merge in `workshop.ts`, which is extended rather than replaced.

## GSTACK REVIEW REPORT

Review mode: FULL_REVIEW, run by oez-captain (Opus) on 2026-10-04 against origin/main 7fbe337. This is a teammate session, so the captain auto-decided each issue on its recommended option, and each one is folded into the plan above. Ryan-held items are listed as unresolved.

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | — |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | — (outside voice ran on a Sonnet subagent; Astra is reserved for the sprint's tolerance call by lead rule) | — |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | ISSUES_OPEN (2 Ryan-held) | 12 issues, 0 critical gaps after folding |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

Decisions (D1-D12, all auto-chosen as recommended and folded in):

| # | Decision |
|---|---|
| D1 | Scope: A and B run in two parallel worktrees. T3 runs only after T2's verdict and folds only sourced rows. T7d (clamp release) is split out. |
| D2 | Two airplanes: add the N26MS same-airplane method check (rows vs ladder step 1, 693.4) and pre-register the predicted OM gap (+17 to +37 lb). |
| D3 | Engine arm: the method is written down and adversary-checked before any arm value exists. The arm alone decides the CG (0.333 in per in; 4.4 in flips the light sample). |
| D4 | Freeze: sha256 of the closure block, with no git dependency. Verified: the remote lanes rsync `--exclude .git`, `scripts/remote_test.sh:22`. |
| D5 | Caps: over a cap, the exit test is a strict xfail with the reason named; the suite does not go red. |
| D6 | Band math: exact bisection only. The one-pass corner rule is removed; a brute-force 2^n test arbitrates and also fails on a broken rule. |
| D7 | The broken-input test asserts the exact moment shift. The disjunction is gone. |
| D8 | The 727.9 test compares the closure verdicts for both targets. The constant-only tautology is gone. |
| D9 | Cull diagnosis: `rig.clampPos` covers authored landings only. The user dolly is unclamped to 7.5 m (`main.ts:331`, `camera.ts` `scaled()`). Fix: binary per-plane hide of the wall and the props on it, no transparency under the SSAO pipeline. |
| D10 | e2e: one page stepped through ops, an absolute 400 px floor, a nocull proof, a 232-op logic sweep timed to ≤ 90 s. |
| D11 | The "NP does not read weights" claim becomes a test (perturb weights, NP unchanged). |
| D12 | The Astra call moves inside Task 1 Step 5, before the arm value. |

- **CROSS-MODEL:** The Sonnet outside voice and this review agreed on D2, D4, D5, D6, D7, D8 and D10. One tension: the outside voice said the cull is likely a no-op under the clamp. The code shows the clamp never touches user zoom, so the cull stands, and its diagnosis is now written into the plan.
- **VERDICT:** Eng review run; the plan is ready to implement once the lead gives the GO. Status is ISSUES_OPEN only on the two Ryan-held items below. Neither blocks Part B, and neither blocks running Part A to its honest verdict.

Ryan ruled on both 2026-10-04 (via the lead): an honest strict xfail CLOSES Block 2 with the gap named, and the engine CG comes from public sources (Task 1 Step 2b).

NO UNRESOLVED DECISIONS
