# Parametric O-235 engine module implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Model the book engine (Lycoming O-235, C-series / H2C on the dynafocal mount) as components with a sourced mass-properties table. The module's component-summed weight and CG must reproduce the FAA TCDS whole-engine values, and it must not touch the frozen 2.n closure row.

**Architecture:**
- **New file.** A new `core/engine_o235_book.py` holds the component geometry (CadQuery), placed from one datum: the propeller flange front face at FS 155.8. It also holds `engine_mass_properties()`, which gives each sourced accessory its published mass and makes the core a residual shared out by solid volume. The CG comes from the placed solids.
- **Wiring.** `core/engine_book.build_engine()` keeps its part keys (`block`, `bracket`, `cowl`, `rib_*`). The `block` part becomes the crankcase-and-cylinders compound, and the new accessory parts get new keys. That way the many consumers of `block` keep working.
- **What is tested.**
  - The weight check is bookkeeping.
  - The CG check is the falsifiable test. Its layout parameters are frozen and hashed before the CG is ever computed, the same freeze-then-sum discipline as 2.n.
  - A sensitivity test proves the CG check can actually discriminate.

**Tech Stack:** Python 3.12, CadQuery, PyYAML, pytest; the lab (TypeScript) only for the part list.

**Spec:** `docs/harness/engine-module-proposal.md` (crew R, 2026-10-05; Ryan GO 2026-10-05), inputs `docs/harness/2n-engine-inventory.md` and `2n-engine-research.md`. Frozen closure: ledger row 65; engine row FS 141.05, band 140.8 to 141.3, 243 lb.

## Global Constraints

- PUBLIC repo. No IPs, hostnames, home paths, plans pages, scans or OCR text. Paraphrase sources in 10 words or fewer. Never store CAD files: every public O-235 CAD found is licence-forbidden (inventory section 5).
- Never measure an undimensioned image and call it a source. Layout dimensions come from TCDS numbers (bore 4.375, stroke 3.875, four opposed cylinders) and stated proportions only. Every fitted value is a `FITTED_*` constant flagged `representational`.
- The `closure:` block in `data/mass_ledger.yaml` is frozen. The module reads the engine row and never edits it.
- A gate counts only after it has been shown to fail on a deliberately broken input.
- A failing bound stays failing (strict xfail citing its ledger row) and is never widened. Record moved tests in `docs/geometry-correction-ledger.md`; the next free row is 70 (row 69 is the visual-pass floor).
- Arithmetic is deterministic code. No LLM computes a sum.
- Crews stage named files and do not commit. The captain sends the split; the lead commits and pushes via push-gate. No Claude-Session trailers.
- The GLB/lab deploy render takes the GPU lease. Give the lead a heads-up first.

## Review Focus

1. **A CG check that is really a calibration.** About five fitted dimensions (case length, cylinder pitch, accessory offsets, and so on) can steer the CG into ±0.5 in. Expected:
   - `FITTED_*` values and densities are frozen and sha256-hashed (row 70) before `engine_mass_properties()` exists;
   - the crew that sets them never runs a CG;
   - `test_cg_check_discriminates` shows that moving any single fitted dimension by ±25 percent moves the CG by more than the tolerance for at least one dimension. If none does, the CG test is declared non-discriminating in its docstring and in row 70.
2. **Datum direction.** On the pusher the CG is FORWARD of the flange: CG_FS = 155.8 − 14.75 = 141.05. Expected: a break-it test that flips the sign and goes red.
3. **Disagreement with the frozen closure row.** Expected: the module's mass is 243 ± 0.5 and its CG FS falls inside [140.8, 141.3]. A mismatch fails the test; it never edits the row.
4. **Placement against the existing block.** The block currently starts at FS 127 (`eng_book_block_fwd_fs`, unsourced) and is 30 in long, so it ends at FS 157, aft of the 155.8 flange. Expected: the new crankcase is placed from the flange datum, and `eng_book_block_fwd_fs` is retired or derived (a ledger row). Nothing may be aft of the flange except the crank stub and flange disc.
5. **Consumers of the `block` part.** There are 11 files: the GLB export, fuselage_export, lab fuselage.ts, m28 tests, the kernels fixture and the e2e tests. Expected: the key `block` survives, with new parts added beside it, and the lab and e2e suites are green without editing old assertions except counts.

---

### Task 1: Sources and fields

**Files:**
- Modify: `data/sources/registry.yaml` (add `lyc-om-o235`, Operator's Manual 60297-9)
- Modify: `config/aircraft_config.py` (`eng_o235_flange_fs` 155.8 derived, `eng_o235_cg_from_flange_in` 14.75 book, `eng_o235_cg_below_cl_in` 1.13 book, `eng_o235_cg_left_in` 0.20 book, `eng_o235_bore_in` 4.375 book, `eng_o235_stroke_in` 3.875 book, plus `GEOMETRY_PROVENANCE` entries)
- Test: `tests/test_engine_o235_fields.py`

- [ ] **Step 1: Failing test**

```python
from config.aircraft_config import config, GEOMETRY_PROVENANCE
from core.sources import check_citation
G = config.geometry
FIELDS = {"eng_o235_flange_fs": 155.8, "eng_o235_cg_from_flange_in": 14.75, "eng_o235_cg_below_cl_in": 1.13,
          "eng_o235_cg_left_in": 0.20, "eng_o235_bore_in": 4.375, "eng_o235_stroke_in": 3.875}

def test_fields_carry_the_tcds_and_cp28_values():
    for k, v in FIELDS.items():
        assert getattr(G, k) == v, k
        p = GEOMETRY_PROVENANCE[k]
        assert p["status"] in {"book", "derived"} and p["cite"], k
        for c in p["cite"]: check_citation(c)

def test_flange_is_the_closure_arithmetic():
    from core.ledger import load_ledger
    eng = next(r for r in load_ledger()["closure"]["rows"] if r["name"] == "engine")
    assert round(G.eng_o235_flange_fs - G.eng_o235_cg_from_flange_in, 2) == eng["arm_fs"]
```

(The crew matches the existing `GEOMETRY_PROVENANCE` shape. Read one entry first; the keys above are illustrative.)

- [ ] **Step 2:** Run it. Expected: FAIL (AttributeError).
- [ ] **Step 3:** Add the fields and provenance, then run it. Expected: PASS.

### Task 2: Freeze the layout before any CG

**Files:**
- Create: `core/engine_o235_book.py`. In this task it holds ONLY the `FITTED_*` constants, `DENSITY_*`, and `layout_sha256()`.
- Modify: `docs/geometry-correction-ledger.md` (row 70: the layout's sources and reasons, and its hash)
- Test: `tests/test_engine_o235_layout.py` (the hash appears in row 70; the hash changes when any constant moves)

The fitted constants:
- crankcase length, width and height;
- cylinder pitch and bank stagger;
- barrel and head length;
- sump box;
- accessory-housing depth;
- positions of the starter, alternator, magnetos, carburettor and fuel pump, from their stated pad locations (TCDS NOTE 4 drives; CP27 p4 "station 150 and aft");
- the four dynafocal pad positions.

Densities are handbook aluminium 0.0975 lb/in³ and steel 0.283 lb/in³. Each gets a cite, or it is flagged unsourced.

- [ ] Step 1: write the test.
- [ ] Step 2: confirm it fails.
- [ ] Step 3: write the constants with a one-line reason each. **The crew writes no geometry or mass code and computes no CG.**
- [ ] Step 4: paste the hash into row 70 and run the test. Expected: PASS.

### Task 3: Geometry

**Files:**
- Modify: `core/engine_o235_book.py`. Add `crankcase()`, `cylinders()`, `sump()`, `accessory_housing()`, `crank_flange()`, `starter()`, `alternator()`, `magnetos()`, `carburettor()`, `fuel_pump()` and `mount_pads()`. Each returns a placed `cq.Workplane` in the fuselage frame (x = FS, `z_of_wl`), placed from the flange datum and pitched by `DOWN_THRUST_DEG` about the flange.
- Modify: `core/engine_book.py`:
  - `build_engine()["block"]` becomes the crankcase + cylinders + sump + housing compound;
  - new keys `starter`, `alternator`, `magnetos`, `carburettor`, `fuel_pump`, `mount_pads`, each with fidelity `representational` and cites;
  - retire `eng_book_block_fwd_fs`, or derive it from the flange (record in row 71).
- Test: `tests/test_engine_o235_geometry.py`

The tests:
- every part is a valid solid;
- no part's x extends aft of `eng_o235_flange_fs` except the flange disc and crank stub;
- no part is forward of the firewall (FS 125);
- the four cylinders are bore-sized;
- the pads are inside the cowl;
- `build_engine()` still has every old key.

- [ ] Steps: the failing test, implement, run `tests/test_engine_geometry.py tests/test_engine_stations.py` plus the new file, and fix only count or position assertions that moved by design (row 71).

### Task 4: Mass properties

**Files:**
- Modify: `core/engine_o235_book.py`. Add `engine_mass_properties(variant="H2C") -> EngineMass`, a NamedTuple `(total_lb, cg_fs, cg_bl, cg_wl, rows: list[MassRow])`. `MassRow` is `(name, mass_lb, band, cg_xyz, status, cite)`.
- Sourced rows:
  - starter, 17 lb [16.7, 17.2] (cp-text:p49);
  - alternator or generator, 7 lb [4.25, 9];
  - magnetos, 2 × the Slick weight for C1C/H2C (vendor page, registered).
- The core is a residual: TCDS 243 less the sourced rows, shared out by solid volume × the frozen density, then scaled to the residual.
- The CG of each row is its placed solid's centroid.

- [ ] Steps: failing tests first, then implement.

### Task 5: Acceptance and break-it tests

**Test file:** `tests/test_engine_o235_mass.py`

```python
import pytest
from core.engine_o235_book import engine_mass_properties
from config.aircraft_config import config
G = config.geometry
M = engine_mass_properties()

def test_weight_bookkeeping():
    assert M.total_lb == pytest.approx(243.0, abs=0.5)
    for r in M.rows:
        if r.status != "representational":
            assert r.band[0] <= r.mass_lb <= r.band[1], r.name

_LONG = (G.eng_o235_flange_fs - M.cg_fs)          # forward of the flange on the pusher
@pytest.mark.xfail(abs(_LONG - 14.75) > 0.5, strict=True, reason=f"ledger row 70: component CG {_LONG:.2f} in from the flange vs TCDS 14.75")
def test_cg_matches_tcds_from_the_flange():
    assert abs(_LONG - 14.75) <= 0.5
    # vertical 1.13 below the crank centreline +-0.3, lateral 0.20 left +-0.25, both in the engine frame (crew writes the transform)

def test_flipped_datum_goes_red():   # break-it: CG aft of the flange is wrong on a pusher
    assert abs((M.cg_fs - G.eng_o235_flange_fs) - 14.75) > 0.5

def test_cg_check_discriminates():   # Review Focus 1
    # move each FITTED_* dimension by +-25 percent in turn (monkeypatch, rebuild, recompute)
    # assert at least one moves |CG_long| by > 0.5 in; record the sensitivity table in the test output
    ...

def test_module_agrees_with_the_frozen_closure_row():
    from core.ledger import load_ledger
    eng = next(r for r in load_ledger()["closure"]["rows"] if r["name"] == "engine")
    assert eng["arm_band_fs"][0] <= M.cg_fs <= eng["arm_band_fs"][1]
    assert eng["weight_band_lb"][0] <= M.total_lb <= eng["weight_band_lb"][1]
```

(`test_cg_check_discriminates` is written in full by the crew. The `...` marks its body, which depends on the Task 2 constant names. It must print the sensitivity table.)

- [ ] Run: if the CG check fails honestly, it stays a strict xfail with the measured value, and the layout is NOT re-tuned. Re-tuning is a new ledger row with a new hash, and it has to be justified by a source, never by the result.

### Task 6: Lab and GLB wiring

**Files:**
- `guide/export_glb.py`, `guide/fuselage_export.py`, `guide/lab/src/logic/fuselage.ts` (the part list, alias group `engine.*`), and the mass-table JSON next to the parts for readouts.
- `guide/lab/tests/m28.test.ts` and `guide/lab/tests/fixtures/kernels.json` (regenerate the fixture).
- `tests/guide/test_export_glb.py`, `tests/guide/test_lab_e2e.py`: counts only.

The new parts are striped `representational`. The f23 engine-op readout shows "component model, CG x.xx in from the flange vs TCDS 14.75". It answers only its own ops: write a null test on an earlier op.

- [ ] Steps: failing tests, wire, lab unit tests, full fan-out.

### Task 7: Docs

`TODOS.md`: the engine module entry, with what stays unsourced (proposal section 8). `AGENTS.md`: Key Modules line. Ledger rows 70 and 71.

## NOT in scope

- The O-200 variant: a different datum (the lug rear face), needs a pad plane. That is a later milestone.
- Exhaust and baffles: not in the TCDS dry weight.
- Any change to the frozen closure, the 2.n verdict or the analysis config engine fields.
- Getting Section IIL or a Lycoming installation drawing: money or outward contact, which is Ryan's call.

## Crew and lane plan

| Wave | Lane / model | Why |
|---|---|---|
| T1 + T2 fields and frozen layout | Sonnet crew, no CG code | mechanical; independence from the result |
| T3 + T4 geometry and mass | Sonnet crew (a different session from T2) | pattern-following CadQuery |
| T5 acceptance + sensitivity | same crew as T4; captain reviews the sensitivity table | arithmetic in code |
| T6 lab/GLB wiring | Sonnet crew | follows existing alias patterns |
| Adversary on frozen layout + CG result | codex `-m gpt-6-astra`, 1 call | the one judgment call |
| Fan-out | script (remote_test_all, `OPEN_EZ_TEST_TIMEOUT=2700`; the Mac lane now runs past 1500 s) | deterministic |
| Deploy render | GPU lease, heads-up to the lead | lab and GLB |

## GSTACK REVIEW REPORT

This was a quick eng review, run by oez-captain (Opus) on 2026-10-05 against origin/main 2aee2d3. The lead asked for a quick review, so there was no second model. Every finding is folded into the plan above.

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| Eng Review | `/plan-eng-review` (quick) | Architecture & tests | 1 | CLEAR | 5 issues folded, 0 critical gaps |

Findings:

1. **The CG check is steerable (P1).** About five fitted dimensions can push the CG inside ±0.5 in. The fixes in the plan:
   - freeze the layout and record its hash (row 70) before any CG code exists;
   - have a different crew write the layout;
   - add a sensitivity test that must show the check can discriminate, or else declares that it cannot.
2. **The existing block runs past the flange (P1).** `eng_book_block_fwd_fs` is 127, and the block is 30 in long, so it ends at FS 157, aft of the 155.8 flange datum. Everything is now placed from the flange, and the old field is retired or derived (row 71).
3. **Blast radius of the `block` part (P2).** 11 consumers use it. The key is kept and the new parts are added beside it, so only test counts move.
4. **Undimensioned images (P2).** Layout values come only from TCDS numbers and stated proportions, and are flagged `representational`.
5. **Mac lane timeout (P2).** The visual pass pushed the Mac fan-out past its 1500 s cap. The plan's fan-out sets `OPEN_EZ_TEST_TIMEOUT=2700`. Raising the default is a separate infra change.

- **VERDICT:** ENG CLEARED. Ready to build after the visual pass ships (Ryan GO 2026-10-05).

NO UNRESOLVED DECISIONS
