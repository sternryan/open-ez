# open-ez Planform Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** make open-ez's canard and station geometry come from the Long-EZ plans (or be visibly
flagged), in the published station frame, and report the neutral-point (NP) gap honestly instead of
fitting it.

**Architecture:** all values live in `config/aircraft_config.py`.
- A `GEOMETRY_PROVENANCE` table next to the values records each one's source and status, and a test
  enforces it.
- Every consumer derives from config (the generators, the physics, OpenVSP, the M2 layup and renders),
  so the change is values + provenance, then an honest triage of what moved.

**Tech Stack:** Python 3.10+, CadQuery, pytest; the existing accuracy-report and regression-lock
tooling.

**Spec:** `docs/superpowers/specs/2026-09-29-planform-correction-design.md`. Read it first; §2 is the
evidence table.

## Global Constraints

- **The book is the source.** Every value marked `book` or `cp-corrected` carries a `source`: a scan
  page, a CP entry + LPC number, or a cobelu file + line.
- **Unknown values stay flagged** (`unsourced`, `derived-unsourced`, `converted-unsourced`,
  `conflict`), never guessed.
- **Never loosen a physics sanity bound.** A category (b) failure becomes a strict `xfail` citing its
  ledger row.
- **Scan hygiene:** no scan content in the repo; quote at most a few words of plans text. Never claim
  the plans are out of copyright.
- **open-ez is PUBLIC:** no private-network hostnames, no private-network IPs, no home-directory paths in any committed file.
- **Commit hygiene:**
  - Commit messages carry no trailers of any kind.
  - Stage named files only.
  - Test runs rewrite `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json`; restore
    them with `git checkout` before each commit and never commit them.
- **Commit gate:** the hook needs a green, unpiped test run in open-ez right before `git commit`, in the
  committer's own turn. Subagents cannot earn it, so the captain or lead commits.
- **Test commands:**
  - Python: `.venv/bin/python -m pytest -q -p no:cacheprovider` from the repo root. The pre-existing
    failure `scripts/assembly_test.py::test_full_assembly` is out of scope.
  - Node: `node --test guide/viewer/tests/*.test.mjs`.
  - Content gate: `source ~/.config/long-ez/env && .venv/bin/python -m guide.check`.

## Spec deviation (decided while planning)

- **The nose moves with the other stations.** Spec §3.2 keeps `fs_nose = 0.0` while the other
  stations shift by −45.5, which would shrink the modelled fuselage by 45.5 in. That is a physics
  change nobody asked for.
- **Instead, every internal station shifts uniformly by −45.5, nose included:** `fs_nose = −45.5`,
  `converted-unsourced`, with a conflict note against the book's FS 0 datum and its FS −6.8 nose tip.
  The fuselage stays exactly as modelled; only the canard and wing move to book values.
- `fuselage_length` is a length, not a station, and stays 214.0.

## Review Focus

The five most likely ways this bites someone:

1. **Physics silently loosened.** A physics bound that fails under book geometry "fixed" by widening a
   tolerance. Expectation: every failing bound is a strict `xfail` with a ledger row. Pinned in
   Task 4: a test scans the regression and validation test files for tolerance edits against the
   ledger.
2. **Old chord fields drift.** Code or data still reads `canard_root_chord`/`canard_tip_chord` as if
   they could differ. Expectation: both are read-only aliases of `canard_chord`, so the planform is a
   rectangle everywhere. Pinned in Task 3.
3. **A station missed in the shift.** One FS value, e.g. the strake's `fs_leading_edge`, is left in
   the old frame, and parts end up 45.5 in apart. Expectation: every FS-bearing field shifts, and
   their pairwise spacing is preserved except canard and wing. Pinned in Task 3.
4. **Provenance rot.** A new geometry field is added later without a provenance entry. Expectation:
   the enforcing test lists fields by pattern, not by a hand list, so new `fs_*`/`canard_*` fields
   fail until documented. Pinned in Task 2.
5. **Stale M2 layup data.** The semi-span in `layup.json` changes from 73.5 to 63.0, and the renders
   still show the old planform. Expectation: re-export and re-render, and the render key changes.
   Pinned in Task 7 (a live check).

## File map

| File | Change |
|---|---|
| `config/aircraft_config.py` | `GEOMETRY_PROVENANCE`; `canard_chord` + read-only aliases; `wing_le_anchor`, `wing_root_bl`; frame shift; `datum_offset_in = 0` |
| `tests/test_geometry_provenance.py` (new) | provenance enforcement + shift/spacing invariants |
| `docs/geometry-correction-ledger.md` (new) | one row per moved test |
| `tests/test_regression_lock.py`, `tests/test_datum_resolution.py`, and others as triage finds | category (a) updates, category (b) strict xfails |
| `data/validation/calibration_log.json`, `data/validation/reference_data.json`, `data/validation/accuracy_report.json` | retire Phase 5; datum note; regenerated report |
| `guide/…` M2 tests pinned to 73.5 | category (a) updates |

---

### Task 1: Chord source search (read-only)

**Files:** none (a report only).

- [ ] **Step 1:** Search the CP sections text (`$LONGEZ_CP_SECTIONS`, after
  `source ~/.config/long-ez/env`; never print env values) and cobelu
  (`~/.cache/long-ez/cobelu/I/md/`) for the canard chord or area. Try these regexes, case-insensitive:
  - `canard (chord|area)`
  - `chord of the canard`
  - `R1145`
  - `Roncz.*(chord|area|sq)`
  - `canard.*sq\.? ?f`

  Also check cobelu `I/images/30/C-3.png` for a printed dimension. Don't measure an undimensioned
  image.
- [ ] **Step 2:** Record the result in `docs/geometry-correction-ledger.md`, section "Chord search":
  each hit's source + a ≤10-word paraphrase, or "no sourced value found".
- [ ] **Step 3: Decide.** If a sourced chord (inches) or area (sq ft or sq in) is found, compute the
  chord (area / 126 for the Roncz core) and use it in Task 3 with status `book` or `cp-corrected`.
  Otherwise Task 3 uses 15.25 with status `unsourced`.
- [ ] **Step 4:** Commit the ledger file: `git add docs/geometry-correction-ledger.md && git commit -m "docs: canard chord source search"`.

---

### Task 2: Provenance table + enforcement

**Files:**
- Modify: `config/aircraft_config.py` (add `GEOMETRY_PROVENANCE` after the `GeometricParams` class)
- Test: `tests/test_geometry_provenance.py`

**Interfaces:**
- Produces: `config.aircraft_config.GEOMETRY_PROVENANCE: dict[str, dict]`, entry keys `status`,
  `source`, `confidence`, `note`.
- Produces: `PROVENANCE_STATUSES = frozenset({"book", "cp-corrected", "derived-unsourced",
  "converted-unsourced", "unsourced", "conflict"})`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_geometry_provenance.py
"""Every planform/station geometry value is sourced from the book or visibly flagged."""
import dataclasses
import re

from config.aircraft_config import GEOMETRY_PROVENANCE, PROVENANCE_STATUSES, GeometricParams

PATTERN = re.compile(r"^(fs_|canard_|wing_(span|root_chord|tip_chord|sweep_le|dihedral|root_bl|le_anchor)|datum_offset_in$)")


def geometry_fields() -> set[str]:
    return {f.name for f in dataclasses.fields(GeometricParams) if PATTERN.match(f.name)}


def test_every_geometry_field_has_provenance():
    missing = sorted(geometry_fields() - set(GEOMETRY_PROVENANCE))
    assert missing == [], f"add GEOMETRY_PROVENANCE entries for: {missing}"


def test_provenance_entries_are_well_formed():
    for field, e in GEOMETRY_PROVENANCE.items():
        assert set(e) == {"status", "source", "confidence", "note"}, field
        assert e["status"] in PROVENANCE_STATUSES, (field, e["status"])
        assert e["confidence"] in {"high", "medium", "low", "n/a"}, (field, e["confidence"])
        if e["status"] in {"book", "cp-corrected"}:
            assert e["source"].strip(), f"{field}: a {e['status']} value needs a source"


def test_no_stale_provenance_entries():
    stale = sorted(set(GEOMETRY_PROVENANCE) - geometry_fields())
    assert stale == [], f"provenance for fields that no longer exist: {stale}"
```

- [ ] **Step 2: Run it.** `.venv/bin/python -m pytest tests/test_geometry_provenance.py -q`.
  Expected: ImportError (`GEOMETRY_PROVENANCE`).

- [ ] **Step 3: Implement.** Add the table below `GeometricParams`. It is **honest about today's
  values** (Task 3 changes both the values and these entries):

```python
PROVENANCE_STATUSES = frozenset(
    {"book", "cp-corrected", "derived-unsourced", "converted-unsourced", "unsourced", "conflict"}
)


def _p(status: str, source: str = "", confidence: str = "n/a", note: str = "") -> dict:
    return {"status": status, "source": source, "confidence": confidence, "note": note}


# Where each planform/station value comes from. Statuses: book (plans page), cp-corrected (a
# Canard Pusher correction), derived-unsourced (computed from an unverified input),
# converted-unsourced (shifted between frames, never checked), unsourced, conflict.
# tests/test_geometry_provenance.py fails if a matching GeometricParams field lacks an entry.
GEOMETRY_PROVENANCE: dict[str, dict] = {
    "canard_span": _p("unsourced", note="147 has no source; see the planform-correction spec"),
    "canard_root_chord": _p("unsourced", note="taper has no source"),
    "canard_tip_chord": _p("unsourced", note="taper has no source"),
    "canard_sweep_le": _p("unsourced", note="book says zero sweep (p.71)"),
    "canard_incidence": _p("unsourced", note="set by incidence blocks; value not in the book"),
    "canard_oswald_e": _p("unsourced", note="aero estimate, not a plans value"),
    "canard_le_wl": _p("unsourced", note="not in the book"),
    "wing_span": _p("unsourced", note="not verified against the book"),
    "wing_root_chord": _p("unsourced", note="not verified against the book"),
    "wing_tip_chord": _p("unsourced", note="not verified against the book"),
    "wing_sweep_le": _p("unsourced", note="not verified against the book"),
    "wing_dihedral": _p("unsourced", note="not verified against the book"),
    "fs_nose": _p("unsourced"),
    "fs_canard_le": _p("unsourced", note="book: FS 18.7 (p.171)"),
    "fs_pilot_seat": _p("unsourced"),
    "fs_rear_seat": _p("unsourced"),
    "fs_wing_le": _p("unsourced", note="Phase 5 NP fit"),
    "fs_firewall": _p("unsourced"),
    "fs_tail": _p("unsourced"),
    "datum_offset_in": _p("unsourced", note="fitted so computed NP matched published FS 108"),
}
```

  Keep only entries whose field exists: run the test, and add or remove entries until
  `test_every_geometry_field_has_provenance` and `test_no_stale_provenance_entries` both pass. The
  field names above come from the current file; check `wing_*` and `canard_*` against
  `dataclasses.fields(GeometricParams)`.

- [ ] **Step 4: Run it.** `.venv/bin/python -m pytest tests/test_geometry_provenance.py -q`. Expected:
  3 passed.
- [ ] **Step 5: Commit.** Run the test unpiped, then
  `git add config/aircraft_config.py tests/test_geometry_provenance.py && git commit -m "feat(config): geometry provenance table and its enforcement test"`.

---

### Task 3: Book frame, book values, one canard chord

**Files:**
- Modify: `config/aircraft_config.py`: `GeometricParams` values, the new fields, the aliases,
  `StrakeConfig.fs_leading_edge`/`fs_trailing_edge`, and `GEOMETRY_PROVENANCE`
- Test: `tests/test_geometry_provenance.py` (add tests)

**Interfaces:**
- Consumes: the Task 1 decision (`CHORD`, `CHORD_STATUS`, `CHORD_SOURCE`).
- Produces:
  - Dataclass fields `canard_chord: float`, `wing_root_bl: float = 23.3`,
    `wing_le_anchor: tuple[float, float] = (113.9, 58.0)`.
  - Read-only properties `canard_root_chord` and `canard_tip_chord`, both returning `canard_chord`.
  - `fs_wing_le` becomes a **property** derived from the anchor. Existing readers keep working.
  - `datum_offset_in = 0.0`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_geometry_provenance.py`):

```python
import math

import pytest

from config.aircraft_config import config, StrakeConfig

OLD = {"fs_pilot_seat": 80.0, "fs_rear_seat": 115.0, "fs_firewall": 180.0, "fs_tail": 214.0, "fs_nose": 0.0}
SHIFT = 45.5


def test_canard_is_a_book_rectangle():
    g = config.geometry
    assert g.canard_sweep_le == 0.0
    assert g.canard_root_chord == g.canard_tip_chord == g.canard_chord
    assert g.canard_span == 126.0
    assert GEOMETRY_PROVENANCE["canard_sweep_le"]["status"] == "book"
    assert "p.71" in GEOMETRY_PROVENANCE["canard_sweep_le"]["source"]


def test_chord_aliases_are_read_only():  # Review Focus 2
    with pytest.raises(AttributeError):
        config.geometry.canard_root_chord = 17.0


def test_frame_is_published():
    assert config.geometry.datum_offset_in == 0.0
    assert config.geometry.to_published_datum(100.0) == 100.0


def test_book_stations():
    g = config.geometry
    assert g.fs_canard_le == 18.7
    fs, bl = g.wing_le_anchor
    assert (fs, bl) == (113.9, 58.0)
    expect = 113.9 - (58.0 - g.wing_root_bl) * math.tan(math.radians(g.wing_sweep_le))
    assert g.fs_wing_le == pytest.approx(expect)
    assert GEOMETRY_PROVENANCE["wing_le_anchor"]["status"] == "cp-corrected"
    assert "CP25" in GEOMETRY_PROVENANCE["wing_le_anchor"]["source"]


def test_other_stations_shift_uniformly():  # Review Focus 3
    g = config.geometry
    for name, old in OLD.items():
        assert getattr(g, name) == pytest.approx(old - SHIFT), name
        assert GEOMETRY_PROVENANCE[name]["status"] == "converted-unsourced", name
    s = StrakeConfig()
    assert (s.fs_leading_edge, s.fs_trailing_edge) == (110.0 - SHIFT, 145.0 - SHIFT)
    assert g.fuselage_length == 214.0
```

  Also change `PATTERN` in the same file to include the new fields:
  `…wing_(span|root_chord|tip_chord|sweep_le|dihedral|root_bl|le_anchor)…` already covers
  `wing_root_bl` and `wing_le_anchor`. Also add `canard_chord` (matched by `canard_`).

- [ ] **Step 2: Run them.** `.venv/bin/python -m pytest tests/test_geometry_provenance.py -q`.
  Expected: the new tests fail.

- [ ] **Step 3: Implement** in `GeometricParams`.
  - Replace `canard_span`, `canard_root_chord`, `canard_tip_chord` and `canard_sweep_le` with:

```python
    canard_span: float = 126.0  # Roncz structural core, BL ±63 (cobelu ch 30 jig blocks); tips not modelled
    canard_chord: float = CHORD  # constant chord (book planform is a rectangle); see GEOMETRY_PROVENANCE
    canard_sweep_le: float = 0.0  # zero sweep (plans p.71)
```

    with `CHORD` = the Task 1 value (15.25 if nothing was found).
  - Add, right after the dataclass fields, the read-only aliases so old readers see a rectangle:

```python
    @property
    def canard_root_chord(self) -> float:
        return self.canard_chord

    @property
    def canard_tip_chord(self) -> float:
        return self.canard_chord
```

  - Stations. Replace the `fs_*` block and the datum offset with the following. Note that `fs_wing_le`
    was a field and becomes a property, so remove the field line:

```python
    fs_nose: float = -45.5  # internal 0.0 shifted to the published frame (see provenance)
    fs_canard_le: float = 18.7  # plans back cover, p.171
    fs_pilot_seat: float = 34.5  # F-22 (internal 80.0 shifted)
    fs_rear_seat: float = 69.5  # F-28 (internal 115.0 shifted)
    fs_firewall: float = 134.5  # internal 180.0 shifted
    fs_tail: float = 168.5  # internal 214.0 shifted
    wing_root_bl: float = 23.3  # wing root butt line
    wing_le_anchor: tuple[float, float] = (113.9, 58.0)  # (FS, BL): wing LE at the strake junction, CP25 LPC 7

    datum_offset_in: float = 0.0  # stations are in the published frame
```

    and add the property:

```python
    @property
    def fs_wing_le(self) -> float:
        """Wing root LE station, derived from the book anchor via the (unverified) wing sweep."""
        fs, bl = self.wing_le_anchor
        return fs - (bl - self.wing_root_bl) * math.tan(math.radians(self.wing_sweep_le))
```

    Import `math` at the top of the file if it isn't already.
  - `wing_le_anchor` is a tuple default on a dataclass. Use
    `field(default=(113.9, 58.0))`. Tuples are immutable, so a plain default is also legal; keep
    whichever the file's style uses.
  - In `StrakeConfig`: `fs_leading_edge: float = 64.5` and `fs_trailing_edge: float = 99.5`, with
    comments "(internal 110.0 / 145.0 shifted)".
  - Replace `GEOMETRY_PROVENANCE`'s entries for the changed fields:

```python
    "canard_span": _p("book", "cobelu ch30 Step 18 / Fig 30-20: outboard jig blocks 126 in apart (core to BL ±63)", "high",
                      "Roncz core only; curled tips not modelled; GU span is 142 (p.54), reference only"),
    "canard_chord": _p(CHORD_STATUS, CHORD_SOURCE, "n/a" if CHORD_STATUS == "unsourced" else "high",
                       "constant chord per the book planform; value from the Task 1 chord search"),
    "canard_sweep_le": _p("book", "plans p.71 (zero sweep); p.171 planform", "high"),
    "fs_canard_le": _p("book", "plans p.171 back-cover 3-view, canard LE", "medium", "read from the image; confirm by eye"),
    "wing_le_anchor": _p("cp-corrected", "plans p.171 prints 113.4; CP25 LPC7 (MEO) corrects to 113.9", "high",
                         "the station is the strake/wing LE junction at BL 58"),
    "wing_root_bl": _p("unsourced", note="root butt line 23.3, carried from the existing config comment"),
    "fs_nose": _p("converted-unsourced", note="internal 0.0 shifted; CONFLICT: book datum FS 0 and nose tip FS -6.8 (p.171)"),
    "fs_pilot_seat": _p("converted-unsourced", note="internal 80.0 shifted by -45.5"),
    "fs_rear_seat": _p("converted-unsourced", note="internal 115.0 shifted by -45.5"),
    "fs_firewall": _p("converted-unsourced", note="internal 180.0 shifted by -45.5"),
    "fs_tail": _p("converted-unsourced", note="internal 214.0 shifted by -45.5"),
    "datum_offset_in": _p("book", "published frame by definition (offset 0)", "high", "was 45.5, fitted to NP; retired"),
```

  - Delete the `canard_root_chord`/`canard_tip_chord` provenance entries (they are properties now, not
    fields), and delete the `fs_wing_le` entry. Keep `fs_wing_le` covered by adding it to the **note**
    of `wing_le_anchor`: "fs_wing_le is derived from this anchor (derived-unsourced via wing sweep)".
  - `CHORD`, `CHORD_STATUS` and `CHORD_SOURCE` are module constants defined above `GeometricParams`
    from Task 1's decision. If nothing was found: `CHORD = 15.25`, `CHORD_STATUS = "unsourced"`,
    `CHORD_SOURCE = ""`.

- [ ] **Step 4: Run the provenance tests.** `.venv/bin/python -m pytest tests/test_geometry_provenance.py -q`.
  Expected: all pass.
- [ ] **Step 5: Commit** (config and its tests only; the rest of the suite is triaged in Task 4). Run
  the provenance test unpiped, then
  `git add config/aircraft_config.py tests/test_geometry_provenance.py && git commit -m "feat(config): book-true canard rectangle and stations in the published frame"`.

---

### Task 4: Suite triage and the ledger

**Files:**
- Modify: `docs/geometry-correction-ledger.md`; failing test files as classified;
  `data/validation/calibration_log.json`; `data/validation/reference_data.json` (the `datum_note` only)
- Test: `tests/test_geometry_ledger.py` (new)

- [ ] **Step 1: Run the whole suite.**
  `.venv/bin/python -m pytest -q -p no:cacheprovider -rf 2>&1 | tee /tmp/planform-triage.txt | tail -40`.
  List every failure.

- [ ] **Step 2: Classify each failure and write one ledger row** under a
  `## Test ledger` table: `| test | old expectation | new value | category | why |`.
  - **(a) Pinned to a retired number.** For example: `LOCKED_NP_PUBLISHED`, the datum-offset
    tests, the canard span or taper asserts, the M2 `semi_span` 73.5.
    **Fix:** update the expected value to the new computed one. The row names the retired source.
  - **(b) A physics sanity bound.** For example: NP within ±2 in of published, static margin range,
    CG limits vs published, area ranges.
    **Fix:** add `@pytest.mark.xfail(strict=True, reason="book geometry: see docs/geometry-correction-ledger.md row <n>; gap <value>")`.
    Never widen the tolerance.

  For `tests/test_regression_lock.py::test_regression_neutral_point`: split its two asserts.
  - The external-truth check against `reference_data` is category (b).
  - The `LOCKED_NP_PUBLISHED` drift check is category (a); set the new value in Task 6.

- [ ] **Step 3: Write the no-loosening guard** (Review Focus 1):

```python
# tests/test_geometry_ledger.py
"""Every strict xfail added for book geometry has a ledger row; tolerances weren't widened."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / "docs/geometry-correction-ledger.md").read_text()


def test_every_book_geometry_xfail_cites_a_ledger_row():
    for f in (ROOT / "tests").glob("test_*.py"):
        for m in re.finditer(r'reason="book geometry: see docs/geometry-correction-ledger\.md row (\d+)', f.read_text()):
            assert re.search(rf"^\|\s*{m.group(1)}\s*\|", LEDGER, re.M), f"{f.name}: ledger row {m.group(1)} missing"


def test_reference_tolerances_unchanged():
    import json
    ref = json.loads((ROOT / "data/validation/reference_data.json").read_text())
    assert ref["aircraft_specs"]["neutral_point_fs"]["tolerance_abs"] == 2.0
```

  Number the ledger rows (`| 1 | test … |`) so the citations resolve.

- [ ] **Step 4: Retire the fit.**
  - In `calibration_log.json`, add `"status": "retired", "retired_reason": "2026-09-29 planform correction: geometry now book-true; NP is checked, not fitted"`
    to the Phase 5 calibration entry (or entries). Don't delete history.
  - In `reference_data.json` `metadata.datum_note`, replace the "~45.5 inches" sentence with "Code
    stations use the published datum directly (datum_offset_in = 0)."

- [ ] **Step 5: Re-run.** `.venv/bin/python -m pytest -q -p no:cacheprovider`. Expected: only the
  pre-existing `assembly_test` failure; everything else passes or is a strict xfail. Restore the
  tracked outputs.
- [ ] **Step 6: Commit.** Run the suite unpiped, then stage the ledger, the changed tests and the two
  json files by name, and
  `git commit -m "test: triage book-geometry changes; strict xfails cite the ledger; retire the Phase 5 fit"`.

---

### Task 5: Report the NP gap

**Files:** modify `scripts/generate_accuracy_report.py`; regenerate `data/validation/accuracy_report.json`.

- [ ] **Step 1: Test first.** Append to `tests/test_accuracy_report_unit.py`:

```python
def test_report_records_geometry_basis():
    import json
    from pathlib import Path
    rep = json.loads((Path(__file__).resolve().parents[1] / "data/validation/accuracy_report.json").read_text())
    assert rep["metadata"]["geometry_basis"].startswith("book (planform correction 2026-09-29)")
    np_m = next(m for m in rep["metrics"] if m["metric_id"] == "neutral_point_fs")
    assert np_m["computed"] != 108.0007  # no longer the fitted value
```

  Run it. Expected: KeyError / assertion failure.

- [ ] **Step 2: Implement.** Where `generate_accuracy_report.py` builds `metadata`, add
  `"geometry_basis": "book (planform correction 2026-09-29); NP is a check, not a fit; see docs/geometry-correction-ledger.md"`.
  Then run `.venv/bin/python scripts/generate_accuracy_report.py` and confirm the NP metric's
  `computed` and `grade`.
- [ ] **Step 3:** Add a ledger section `## NP gap` giving the computed NP, the reference 108.0, the
  signed gap and the grade.
- [ ] **Step 4: Run and commit.** Run `tests/test_accuracy_report_unit.py tests/test_accuracy_report.py`
  unpiped, then commit the script, the report json and the ledger with
  `git commit -m "feat(report): accuracy report records the book geometry basis and the NP gap"`.

---

### Task 6: Regression re-snapshot (its own commit)

**Files:** `tests/test_regression_lock.py` (LOCKED_* constants for the category-(a) drift locks),
plus any snapshot file the triage marked (a).

- [ ] **Step 1:** For each category-(a) drift lock, set the locked constant to the new computed value
  (from the regenerated `accuracy_report.json`). Add a comment: `# re-locked 2026-09-29, planform
  correction; was <old> (Phase 5 fit)`. External-truth asserts are untouched.
- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_regression_lock.py tests/test_physics_regression.py -q`.
  Expected: pass, with strict xfails as ledgered.
- [ ] **Step 3: Commit** with `git commit -m "test: re-lock regression drift values to book geometry"`.
  The diff shows exactly which locked numbers moved.

---

### Task 7: Guide re-export, re-render, deploy (lead)

- [ ] **Step 1:** `.venv/bin/python -m guide.export_glb`. Check `output/guide/layup.json` has
  `"semi_span": 63.0`.
- [ ] **Step 2:** Run the M2 suites: `.venv/bin/python -m pytest tests/guide -q` and the node tests.
  Fix any M2 test pinned to 73.5 as category (a) with a ledger row. Commit.
- [ ] **Step 3:** `guide/render_cutaway.sh --wait` (it reports the lease holder and ETA first).
  Expect a **new render key**, because `layup.json` and the glb changed.
- [ ] **Step 4:** Update the cutaway legend's "not to scale" entry in `guide/build_site.py`
  `LEGEND` to add: "Canard planform from the plans; chord unsourced" (if Task 1 found no chord).
  Run the tests and commit.
- [ ] **Step 5:** `source ~/.config/long-ez/env && bash scripts/deploy_guide.sh`, then check in a
  browser that the heroes show the new section and the 3D canard is a rectangle.

---

### Task 8: Grade, leak scan, push (lead)

- [ ] **Step 1:** `git fetch origin`; confirm "behind 0".
- [ ] **Step 2:** `TMPDIR=/tmp <grader script> -s <session> -r origin/main..HEAD <repo>`,
  unsandboxed. Expect `VERDICT: PASS`.
- [ ] **Step 3:** Leak scan: run the pre-push leak check from the M1 plan
  (`docs/superpowers/plans/2026-09-28-build-guide-m1.md`, the `git diff origin/main | grep -nE …` line),
  restricted to added lines. It must find nothing.
- [ ] **Step 4:** Run a green test unpiped, then `git push origin main` in the same turn as the grade.
- [ ] **Step 5:** Update memory `project_longez_build_guide` with the NP gap and the chord status.
  Tell Ryan about the by-eye check on p.171 (FS 18.7).
