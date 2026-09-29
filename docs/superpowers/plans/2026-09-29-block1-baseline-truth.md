# Block 1: Baseline Truth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** every value open-ez treats as the book's comes from a registered document and page, or is
visibly flagged; the NP and CG checks are re-anchored on the Owner's Manual instead of self-written
numbers.

**Architecture:**
- A sources registry (`data/sources/registry.yaml` + `core/sources.py`) is the one place a
  citation can point.
- `GEOMETRY_PROVENANCE`, `reference_data.json` and a new mass/CG ledger all cite `id:page`.
- Research tasks (corpus, audit, geometry) record what each page says, then change values under the
  same ledger discipline as the planform correction.

**Tech Stack:** Python 3.10+, CadQuery, pytest, PyYAML, PyMuPDF, tesseract (already used for the
scan OCR).

**Spec:** `docs/superpowers/specs/2026-09-29-block1-baseline-truth-design.md`. Read it in full; §2 is
the evidence table and §3 the design.

## Global Constraints

- **A citation is `<registry-id>:p<page>`**, optionally followed by a space and ≤10 words of
  context. Page is the document's printed page number where one exists, else the PDF page, and the
  registry entry says which.
- **Quotes from plans, the manual or the Canard Pusher are at most a few words.** Never copy plans
  content into the repo. Never claim the plans are out of copyright.
- **Private material stays private.** Local source copies live under `LONGEZ_SOURCE_CACHE` (new env
  var in `~/.config/long-ez/env`, default `~/.cache/long-ez/sources`). No committed file contains a
  home path, tailnet hostname or tailnet IP. Never print env values.
- **Never loosen a physics tolerance.** A failing physics bound becomes
  `@pytest.mark.xfail(strict=True, reason="book geometry: see docs/geometry-correction-ledger.md row <n>; …")`
  with a numbered ledger row. Continue the ledger's existing numbering.
- **Unknown stays flagged** (`unsourced`, `conflict`, `unverified`), never guessed.
- **Commit hygiene:** no trailers of any kind; stage named files only; restore
  `output/test_mfg/dxf/*` and `data/validation/openvsp_validation.json` with `git checkout` before
  every commit; the committer (captain or lead, never crew) runs a green, unpiped test run in open-ez
  right before `git commit`.
- **Test commands:**
  - `.venv/bin/python -m pytest -q -p no:cacheprovider` (the pre-existing
    `scripts/assembly_test.py::test_full_assembly` failure is out of scope);
  - `node --test guide/viewer/tests/*.test.mjs`;
  - `source ~/.config/long-ez/env && .venv/bin/python -m guide.check`.

## Review Focus

1. **A citation that points nowhere.** A `book`/`cp-corrected` value whose `source` names a registry
   id that doesn't exist, or omits the page. Expectation: the registry test fails. Pinned in Task 1
   and Task 3.
2. **Unverified numbers sneaking back in as truth.** A physics check or report reads an
   `unverified` reference entry. Expectation: a single accessor returns only confirmed or derived
   entries, and every consumer uses it. Pinned in Task 4.
3. **The sample-loading gate agreeing with a wrong table.** The manual's printed moments contain
   typos (the light-pilot pilot moment prints 7865 for 135 × 59 = 7965; the heavy-pilot total prints
   122706 for a sum of 133706). Expectation: the gate checks the printed **CG and total weight**
   (103.96 at 1113 lb; 101.06 at 1323 lb), recomputes moments itself, and records the typos as book
   errata rather than matching them. Pinned in Task 5.
4. **A gate that can't fail.** Each new gate has a test that feeds it a broken input and expects a
   failure. Pinned in Tasks 1, 5 and 8.
5. **A silent "not run".** The two-method NP check without OpenVSP reports a pass. Expectation: it
   reports `not run` and the report says so. Pinned in Task 8.

## File map

| File | Change |
|---|---|
| `data/sources/registry.yaml` (new) | registered documents |
| `core/sources.py` (new) | load the registry; parse and validate citations |
| `tests/test_sources_registry.py` (new) | registry and citation enforcement |
| `scripts/fetch_sources.py` (new) | build the private corpus (CP PDFs + OCR, manual text) |
| `docs/block1-source-notes.md` (new) | what each page says, per value (≤10-word paraphrases) |
| `config/aircraft_config.py` | provenance citations; stations; wing; canard; weight arms |
| `data/validation/reference_data.json` | audit statuses; corrected values; community builds removed |
| `core/reference.py` (new) | `truth_specs()` accessor: confirmed/derived only |
| `core/ledger.py` + `data/mass_ledger.yaml` (new) | mass/CG ledger + envelope |
| `scripts/generate_accuracy_report.py`, `core/simulation/regression.py` | use `truth_specs()`; NP reported not graded; new stability check |
| `tests/…` | triage per ledger |
| `docs/geometry-correction-ledger.md` | new rows |
| `docs/block1-report.md` (new) | every changed value: from, to, citation |

---

### Task 1: Sources registry and citation enforcement

**Files:**
- Create: `data/sources/registry.yaml`, `core/sources.py`, `tests/test_sources_registry.py`

**Interfaces:**
- Produces: `core.sources.load_registry() -> dict[str, dict]`;
  `core.sources.parse_citation(s: str) -> tuple[str, str]` (id, page) raising `ValueError` on bad
  form; `core.sources.check_citation(s: str) -> None` raising `ValueError` for an unknown id.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_sources_registry.py
"""The sources registry is the only thing a citation may point at."""
import pytest

from core.sources import check_citation, load_registry, parse_citation

REQUIRED = {"title", "edition", "obtain", "copy", "page_basis"}


def test_registry_entries_are_well_formed():
    reg = load_registry()
    assert {"om-1980", "plans-1980", "cp-text", "cobelu", "owner-check"} <= set(reg)
    for sid, e in reg.items():
        assert set(e) >= REQUIRED, sid
        assert e["copy"] in {"scan", "transcription", "ocr", "owner"}, sid
        assert e["page_basis"] in {"printed", "pdf", "issue"}, sid


def test_parse_citation():
    assert parse_citation("om-1980:p28") == ("om-1980", "28")
    assert parse_citation("cp-25:p3 LPC 7 wing LE") == ("cp-25", "3")


@pytest.mark.parametrize("bad", ["om-1980", "om-1980:28", ":p3", "om 1980:p3", ""])
def test_malformed_citation_rejected(bad):
    with pytest.raises(ValueError):
        parse_citation(bad)


def test_unknown_id_rejected():  # the gate fails on a broken input (Review Focus 1, 4)
    with pytest.raises(ValueError, match="not-a-source"):
        check_citation("not-a-source:p1")
```

- [ ] **Step 2: Run** `.venv/bin/python -m pytest tests/test_sources_registry.py -q`. Expected:
  ImportError.

- [ ] **Step 3: Implement.**

```python
# core/sources.py
"""Registered source documents and the citation form `<id>:p<page>`."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parents[1] / "data/sources/registry.yaml"
_CITE = re.compile(r"^([a-z0-9][a-z0-9-]*):p([0-9A-Za-z.\-]+)(?: .*)?$")


@lru_cache(maxsize=1)
def load_registry() -> dict[str, dict]:
    return yaml.safe_load(REGISTRY.read_text())["sources"]


def parse_citation(s: str) -> tuple[str, str]:
    m = _CITE.match(s or "")
    if not m:
        raise ValueError(f"citation must be '<id>:p<page>', got {s!r}")
    return m.group(1), m.group(2)


def check_citation(s: str) -> None:
    sid, _ = parse_citation(s)
    if sid not in load_registry():
        raise ValueError(f"unknown source id {sid!r} in citation {s!r}")
```

```yaml
# data/sources/registry.yaml
# Every citation in open-ez points at one of these ids. `copy` says what the local copy is;
# `page_basis` says which page numbers citations use. Local copies are private and never committed.
sources:
  om-1980:
    title: Long-EZ Owner's Manual
    edition: first edition, May 1980 (Rutan Aircraft Factory)
    obtain: public transcription in the cobelu/Long-EZ repository ("Owners Manual")
    copy: transcription
    page_basis: printed
  plans-1980:
    title: Long-EZ plans, Section I
    edition: March 1980 first edition
    obtain: owner's printed set (phone scan, private)
    copy: scan
    page_basis: pdf
  cp-text:
    title: The Canard Pusher, issues 1-82, sectioned text
    edition: RAF newsletter 1974-1994, community text compilation
    obtain: cozybuilders.org Canard Pusher archive (CPs_1_to_82_Sections.txt)
    copy: transcription
    page_basis: issue
  cobelu:
    title: cobelu/Long-EZ plans transcription
    edition: community markdown transcription of Section I
    obtain: github.com/cobelu/Long-EZ
    copy: transcription
    page_basis: pdf
  owner-check:
    title: Owner by-eye reads of the plans scan
    edition: dated per citation
    obtain: recorded in docs/geometry-correction-ledger.md
    copy: owner
    page_basis: pdf
```

  Task 2 adds one `cp-<n>` entry per Canard Pusher issue it fetches (`page_basis: printed`,
  `copy: ocr`).

- [ ] **Step 4: Run** the test file. Expected: all pass. Confirm `pyyaml` is importable from `.venv`
  (it is used by `guide/`); if not, add it to `requirements.txt`.
- [ ] **Step 5: Commit** `data/sources/registry.yaml core/sources.py tests/test_sources_registry.py`
  with `feat(sources): registry of citable documents and the id:page citation form`.

---

### Task 2: Source corpus (private) and source notes

**Files:**
- Create: `scripts/fetch_sources.py`, `tests/test_fetch_sources.py`, `docs/block1-source-notes.md`
- Modify: `data/sources/registry.yaml` (add `cp-<n>` entries)

**Interfaces:**
- Produces: `scripts.fetch_sources.cp_url(issue: int, date: str) -> str`; private files under
  `$LONGEZ_SOURCE_CACHE`: `om-1980/p<NN>.txt` (one per printed page), `cp-<n>/p<NN>.txt` and
  `cp-<n>.pdf`.

- [ ] **Step 1: Failing test** (pure functions only; no network in tests):

```python
# tests/test_fetch_sources.py
from scripts.fetch_sources import cp_url, split_printed_pages


def test_cp_url():
    assert cp_url(29, "1981-07") == "http://www.cozybuilders.org/Canard_Pusher/1981-07_cp-29.pdf"


def test_split_printed_pages_uses_footer_numbers():
    text = "alpha\n27\n\x0cbeta\nWeight and C G Limits\n28\n\x0c"
    assert split_printed_pages(text) == {"27": "alpha", "28": "beta\nWeight and C G Limits"}
```

- [ ] **Step 2: Run it.** Expected: ImportError.
- [ ] **Step 3: Implement** `scripts/fetch_sources.py`:
  - `cp_url(issue, date)` returns the cozybuilders URL (pattern above).
  - `split_printed_pages(text)` splits on form feeds (`\x0c`), takes each page's last non-empty
    line as its printed number when it is all digits, and returns `{number: body}`.
  - `main()` (argparse, `--cp 29 31 …`, `--om`):
    - `--om`: extract the cobelu Owner's Manual PDF with PyMuPDF (one `\x0c` per page), then
      write `om-1980/p<NN>.txt` per printed page.
    - `--cp N`: look up the issue's date from the file names in the Canard Pusher text directory
      (`YYYY-MM_cp-N.txt`), download the PDF with a browser user-agent, render each page at
      300 dpi, run `tesseract <png> stdout`, and write `cp-N/p<NN>.txt` plus the PDF.
    - All output goes under `$LONGEZ_SOURCE_CACHE`, created if missing. Print counts only, never
      paths.
- [ ] **Step 4: Run** the unit tests (pass), then the real fetch:
  `source ~/.config/long-ez/env && .venv/bin/python -m scripts.fetch_sources --om --cp 29 31`.
  Add `LONGEZ_SOURCE_CACHE` to `~/.config/long-ez/env` first if it is missing. Confirm page 28 of the
  manual contains "Weight and C G Limits", and that the CP-29 OCR is non-empty.
- [ ] **Step 5: Research and record.** In `docs/block1-source-notes.md`, one row per value the spec
  §2 table and §3.4 name: `| value | citation | what the page says (≤10 words, own words) | copy
  caveat |`.
  - Search the CP text and the CP-29/CP-31 OCR for every `reference_data.json` claim; record hits or
    "not found in CP-29/CP-31".
  - Search the Canard Pusher text for the **Roncz canard** chord, span, area, incidence and any CG
    limit change (terms: `Roncz`, `R1145`, `new canard`, `canard.*(chord|area|span)`,
    `C\.?G\.? limit`). Fetch any further issue that the hits point to (`--cp N`) and register it.
  - For the manual's CG chart (p.28), record the limits read from the chart image, not the retyped
    labels (the transcription retyped them): forward FS 97, aft FS 103, 1325 lb, 1425 lb band.
- [ ] **Step 6: Commit** the script, its test, the registry additions and the notes
  (`docs(sources): private source corpus fetcher and Block 1 source notes`).

---

### Task 3: Provenance cites the registry

**Files:**
- Modify: `config/aircraft_config.py` (`GEOMETRY_PROVENANCE` source strings), `tests/test_geometry_provenance.py`

- [ ] **Step 1: Failing test** (append to `tests/test_geometry_provenance.py`):

```python
from core.sources import check_citation


def test_sourced_entries_cite_the_registry():  # Review Focus 1
    for field, e in GEOMETRY_PROVENANCE.items():
        if e["status"] in {"book", "cp-corrected"}:
            check_citation(e["source"])  # raises on unknown id or bad form
```

- [ ] **Step 2: Run.** Expected: fails on the current free-text sources.
- [ ] **Step 3: Rewrite each sourced entry's `source` as a citation.** Keep the prose in `note`:
  - `fs_canard_le`: `plans-1980:p171 F.S. 18.7 at B.L. 71`, with the note naming the
    owner check.
  - `wing_le_anchor`: `cp-text:p25 LPC 7 wing root LE 113.9` (issue 25 as the page under
    `page_basis: issue`), note keeps the p.171 113.4 context.
  - `canard_span`: `cobelu:p<pdf page of ch30 Step 18>`, with the exact page taken from the cobelu
    file.
  - `canard_sweep_le`: `plans-1980:p71`.
  - `datum_offset_in`: status stays `book`, source `om-1980:p25 datum F.S. 0.0`. Verify the page
    number in the manual's text first.
- [ ] **Step 4: Run** the provenance tests. Expected: all pass.
- [ ] **Step 5: Commit** (`refactor(config): provenance sources are registry citations`).

---

### Task 4: Reference-data audit

**Files:**
- Modify: `data/validation/reference_data.json`, `scripts/generate_accuracy_report.py`,
  `core/simulation/regression.py`, `tests/test_datum_resolution.py`, and other tests as triage finds
- Create: `core/reference.py`, `tests/test_reference_truth.py`

**Interfaces:**
- Produces: `core.reference.truth_specs(ref: dict) -> dict[str, dict]`, which returns only
  `aircraft_specs` entries whose `status` is `confirmed` or `derived`. Every metric consumer uses it.

- [ ] **Step 1: Failing tests**

```python
# tests/test_reference_truth.py
import json
from pathlib import Path

import pytest

from core.reference import truth_specs
from core.sources import check_citation

REF = json.loads((Path(__file__).resolve().parents[1] / "data/validation/reference_data.json").read_text())


def test_every_spec_has_an_audit_status():
    for k, e in REF["aircraft_specs"].items():
        assert e.get("status") in {"confirmed", "derived", "unverified"}, k
        if e["status"] == "confirmed":
            check_citation(e["cite"])
        if e["status"] == "derived":
            assert e.get("formula"), k


def test_truth_excludes_unverified():  # Review Focus 2
    fake = {"aircraft_specs": {"a": {"status": "confirmed", "cite": "om-1980:p3", "value": 1},
                               "b": {"status": "unverified", "value": 2}}}
    assert set(truth_specs(fake)) == {"a"}


def test_community_builds_removed():
    assert "community_builds" not in REF


def test_no_consumer_reads_aircraft_specs_directly():  # Review Focus 2
    root = Path(__file__).resolve().parents[1]
    for rel in ("scripts/generate_accuracy_report.py", "core/simulation/regression.py"):
        src = (root / rel).read_text()
        assert '["aircraft_specs"]' not in src, rel
```

- [ ] **Step 2: Run.** Expected: failures.
- [ ] **Step 3: Audit** every `aircraft_specs` entry against `docs/block1-source-notes.md`:
  - **Found:** set `status: confirmed`, `cite`, and the page's value (for example
    `max_gross_weight_lb` → 1325 from `om-1980:p3`; `cg_range_aft_fs` → 103 and `cg_range_fwd_fs`
    → 97 from `om-1980:p28`; `empty_weight_lb` → 750 from `om-1980:p3`; wing and canard span/area
    from `om-1980:p3`). Keep each entry's existing `tolerance_abs`. A corrected value is not a
    tolerance change.
  - **Computed from confirmed entries:** set `status: derived` and `formula`.
  - **Not found:** set `status: unverified` and leave the value for history. `neutral_point_fs`
    (108) is expected here unless Task 2 found it. The same goes for `static_margin_pct`, which
    derives from it.
  - Delete `community_builds` and any source entry nothing cites. Update `metadata` with
    `audit: "2026-09-29 Block 1; see docs/block1-source-notes.md"`.
- [ ] **Step 4: Implement** `core/reference.py`:

```python
"""Reference values the model may treat as truth: confirmed or derived entries only."""
TRUTH = {"confirmed", "derived"}


def truth_specs(ref: dict) -> dict[str, dict]:
    return {k: e for k, e in ref["aircraft_specs"].items() if e.get("status") in TRUTH}
```

  Then switch `generate_accuracy_report.collect_metrics`, `validate_sources` and
  `core/simulation/regression.py` to read specs through `truth_specs(ref_data)`:
  - A metric whose reference is not in `truth_specs` is emitted with `grade: "NOT GRADED"` and
    `reason: "reference unverified"`. It is never skipped silently.
  - Remove the community-builds block from the report.
- [ ] **Step 5: Triage** the full suite exactly as the planform plan's Task 4 did. Tests asserting
  the removed schema (`test_datum_resolution.py` required keys, community builds) are category (a).
  Physics bounds that now fail are category (b): strict xfail plus a ledger row.
- [ ] **Step 6: Regenerate** the report: `.venv/bin/python scripts/generate_accuracy_report.py`.
  Then run the suite unpiped, restore the tracked outputs, and commit
  (`feat(reference): audit reference data against the sources; unverified values stop being truth`).

---

### Task 5: Mass/CG ledger and the manual's sample loadings

**Files:**
- Create: `core/ledger.py`, `data/mass_ledger.yaml`, `tests/test_mass_ledger.py`

**Interfaces:**
- Produces:
  - `core.ledger.Row(name, weight_lb, arm_in, cls, process, cite)`;
  - `core.ledger.load_ledger() -> dict` (keys `empty`, `loads`, `envelope`, `samples`,
    `errata`);
  - `core.ledger.cg(rows: list[Row]) -> tuple[float, float]` (weight, CG);
  - `core.ledger.in_envelope(weight, cg, env) -> bool`.

- [ ] **Step 1: Failing tests**

```python
# tests/test_mass_ledger.py
import pytest

from core.ledger import Row, cg, in_envelope, load_ledger
from core.sources import check_citation

L = load_ledger()


def _rows(sample):
    arms = L["loads"]
    rows = [Row("empty", L["empty"]["weight_lb"], L["empty"]["arm_in"], "empty", "n/a", L["empty"]["cite"])]
    rows += [Row(k, w, arms[k]["arm_in"], "payload", "n/a", arms[k]["cite"]) for k, w in sample["items"].items()]
    return rows


@pytest.mark.parametrize("name", ["light_pilot", "heavy_pilot"])
def test_manual_sample_loadings_reproduce(name):  # Review Focus 3
    s = L["samples"][name]
    w, c = cg(_rows(s))
    assert w == pytest.approx(s["book_total_lb"], abs=0.5)
    assert c == pytest.approx(s["book_cg_in"], abs=0.01)


def test_sample_gate_fails_on_a_wrong_arm():  # Review Focus 4
    s = L["samples"]["light_pilot"]
    rows = _rows(s)
    rows[1] = rows[1]._replace(arm_in=rows[1].arm_in + 5)
    assert cg(rows)[1] != pytest.approx(s["book_cg_in"], abs=0.01)


def test_envelope_matches_the_manual():
    env = L["envelope"]
    assert (env["fwd_fs"], env["aft_fs"], env["max_lb"], env["takeoff_only_max_lb"]) == (97.0, 103.0, 1325, 1425)
    assert not in_envelope(1113, 103.96, env)  # the manual shows the light-pilot sample outside
    assert in_envelope(1323, 101.06, env)


def test_every_row_is_cited():
    check_citation(L["empty"]["cite"])
    for k, v in L["loads"].items():
        check_citation(v["cite"])


def test_book_errata_recorded():
    assert {e["what"] for e in L["errata"]} >= {"light_pilot pilot moment", "heavy_pilot total moment"}
```

- [ ] **Step 2: Run.** Expected: ImportError.
- [ ] **Step 3: Implement** `core/ledger.py`:

```python
"""Mass/CG ledger: cited rows, the manual's CG envelope, and its sample loadings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import yaml

LEDGER = Path(__file__).resolve().parents[1] / "data/mass_ledger.yaml"


class Row(NamedTuple):
    name: str
    weight_lb: float
    arm_in: float
    cls: str  # primary-structure | secondary | non-structural | payload | empty
    process: str
    cite: str


@lru_cache(maxsize=1)
def load_ledger() -> dict:
    return yaml.safe_load(LEDGER.read_text())


def cg(rows: list[Row]) -> tuple[float, float]:
    w = sum(r.weight_lb for r in rows)
    return w, sum(r.weight_lb * r.arm_in for r in rows) / w


def in_envelope(weight: float, cg_in: float, env: dict) -> bool:
    return weight <= env["max_lb"] and env["fwd_fs"] <= cg_in <= env["aft_fs"]
```

  `data/mass_ledger.yaml`. Values come from the manual. **Verify each page number against the
  Task 2 page files before committing.**

```yaml
# Mass/CG ledger. Block 1: the empty aircraft is one row (Block 2 decomposes it).
empty: {weight_lb: 730, arm_in: 111.7, cite: "om-1980:p27 sample empty aircraft"}
loads:
  oil:       {arm_in: 140.0, cite: "om-1980:p27"}
  fuel:      {arm_in: 104.5, cite: "om-1980:p27"}
  pilot:     {arm_in: 59.0,  cite: "om-1980:p26 pilot moment = weight x 59"}
  passenger: {arm_in: 103.0, cite: "om-1980:p26"}
  baggage:   {arm_in: 90.0,  cite: "om-1980:p27"}
envelope: {fwd_fs: 97.0, aft_fs: 103.0, max_lb: 1325, takeoff_only_max_lb: 1425,
           cite: "om-1980:p28 weight and CG limits chart (read from the chart image)"}
samples:
  light_pilot: {items: {oil: 8, fuel: 240, pilot: 135}, book_total_lb: 1113, book_cg_in: 103.96,
                cite: "om-1980:p27"}
  heavy_pilot: {items: {oil: 8, fuel: 150, pilot: 210, passenger: 210, baggage: 15},
                book_total_lb: 1323, book_cg_in: 101.06, cite: "om-1980:p27"}
errata:
  - {what: "light_pilot pilot moment", book: 7865, computed: 7965, cite: "om-1980:p27"}
  - {what: "heavy_pilot total moment", book: 122706, computed: 133706, cite: "om-1980:p27",
     note: "the printed CG 101.06 matches the computed moment, so the total is a typo"}
```

  `in_envelope` uses `max_lb` (1325). The 1425 band is recorded but takeoff-only.
- [ ] **Step 4: Run** the tests. Expected: all pass. If a sample fails by more than 0.01, re-read
  the page before touching anything. The gate exists to catch a wrong arm.
- [ ] **Step 5: Commit** (`feat(ledger): mass/CG ledger reproduces the Owner's Manual sample loadings`).

---

### Task 6: Fuselage stations and weight arms to the book

**Files:**
- Modify: `config/aircraft_config.py` (`fs_*`, `fuselage_length`, `StrakeConfig`,
  `StructuralWeightParams`, `GEOMETRY_PROVENANCE`), `tests/test_geometry_provenance.py`, and tests
  as triage finds

- [ ] **Step 1: Research** (record in `docs/block1-source-notes.md`):
  - The book stations: the instrument-panel reference FS 40 (`om-1980`), main gear FS 110.5 ± 1,
    nose gear ≈ FS 20.
  - The Section I station callouts found in the scan OCR (FS 49.8, 116, 120, 148.4 and others).
    Read each one on its page image, with the bulkhead or part it labels.
  - The overall length, 201.4 in (`om-1980:p3`), and the nose tip at FS −6.8 (`plans-1980:p171`).
  - Map each model field (`fs_nose`, `fs_pilot_seat`, `fs_rear_seat`, `fs_firewall`, `fs_tail`,
    strake LE/TE) to the book feature it represents. Where no book feature matches, the field stays
    `converted-unsourced`.
- [ ] **Step 2: Failing test** (append to `tests/test_geometry_provenance.py`, then extend it with
  every other station Step 1 sources):

```python
def test_book_stations_block1():
    g = config.geometry
    assert g.fs_nose == pytest.approx(-6.8)
    assert GEOMETRY_PROVENANCE["fs_nose"]["status"] == "book"
```

  Update `test_other_stations_shift_uniformly` from the planform plan: fields that become `book`
  leave its `OLD` dict, and its assertion now covers only the fields still `converted-unsourced`.
- [ ] **Step 3: Implement.**
  - Set each sourced station, with `book` status and a citation.
  - Set `fuselage_length` from the sourced nose and tail. If the tail station isn't sourced, leave
    `fuselage_length` and flag it `conflict` against 201.4.
  - Move `StructuralWeightParams` arms: `canard_arm_in` to the canard's quarter-chord station
    (`fs_canard_le + 0.25 * canard_chord`), with a comment. Leave the other arms `unsourced`, with a
    note that Block 2 replaces them.
- [ ] **Step 4: Triage** the suite (strict xfails plus ledger rows, no loosening). Regenerate the
  report.
- [ ] **Step 5: Commit** (`feat(config): fuselage stations from the book; canard weight at the canard`).

---

### Task 7: Wing and canard to the book

**Files:** as Task 6.

- [ ] **Step 1: Research** (record in the notes):
  - Wing span and area (`om-1980:p3`), the strake share of the 94.8 sq ft total, and root chord,
    tip chord, sweep and dihedral wherever the plans print them.
  - The Roncz canard results from Task 2. Decision rule:
    - Roncz chord and span found in the Canard Pusher: use them, status `cp-corrected`.
    - Not found: use the GU planform from the manual (11.8 ft, 12.8 sq ft, so chord =
      12.8 × 144 / 141.6 ≈ 13.02 in). Set `canard_span = 141.6`, `canard_chord = 13.02`, status
      `conflict`, with the note "GU planform (om-1980 p3); Roncz planform unconfirmed".
    - Update `CHORD`, `CHORD_STATUS` and `CHORD_SOURCE` accordingly.
  - The canard waterline: p.171 side view W.L. 18.9 vs cobelu C-3 W.L. 19.8 vs config 12.0. Read
    both images. If they are the same reference point, set `canard_le_wl` with `book` status.
    Otherwise set the better-attested value with status `conflict`, naming both.
- [ ] **Step 2: Failing tests.** Assert the new values and statuses exactly as decided in Step 1.
  Also add a test that `canard_area` (computed) matches `canard_chord × canard_span / 144` to 0.01
  sq ft.
- [ ] **Step 3: Implement.** Update the values and provenance. The M2 layup (`semi_span`) follows
  `canard_span`, so update its pinned tests as category (a).
- [ ] **Step 4: Triage** and regenerate the report.
- [ ] **Step 5: Commit** (`feat(config): wing and canard planform from the Owner's Manual and CP`).

---

### Task 8: Physics checks re-anchored

**Files:**
- Modify: `scripts/generate_accuracy_report.py`, `core/analysis.py` (only if a helper is needed)
- Create: `tests/test_stability_checks.py`

**Interfaces:**
- Produces: `scripts.generate_accuracy_report.stability_at_aft_limit(np_fs: float, aft_fs: float, mac_in: float) -> dict`,
  returning `{"np_fs", "aft_limit_fs", "static_margin_pct", "pass"}`;
  `two_method_np(analytic: float, vlm: float | None, bound_in: float) -> dict` with
  `status ∈ {"pass", "fail", "not run"}`.

- [ ] **Step 1: Failing tests**

```python
# tests/test_stability_checks.py
from scripts.generate_accuracy_report import stability_at_aft_limit, two_method_np


def test_stable_at_aft_limit():
    r = stability_at_aft_limit(np_fs=106.0, aft_fs=103.0, mac_in=40.0)
    assert r["pass"] and r["static_margin_pct"] == 7.5


def test_unstable_at_aft_limit_fails():  # gate fails on a broken input
    assert not stability_at_aft_limit(np_fs=102.0, aft_fs=103.0, mac_in=40.0)["pass"]


def test_two_method_not_run_is_not_a_pass():  # Review Focus 5
    assert two_method_np(110.0, None, 1.0)["status"] == "not run"


def test_two_method_disagreement_fails():
    assert two_method_np(110.0, 113.0, 1.0)["status"] == "fail"
    assert two_method_np(110.0, 110.4, 1.0)["status"] == "pass"
```

- [ ] **Step 2: Run.** Expected: ImportError.
- [ ] **Step 3: Implement** both functions:
  - static margin = (NP − aft limit) / MAC × 100;
  - `pass` = NP > aft limit;
  - two-method: `None` → `not run`, else `|a − v| ≤ bound` → `pass`, else `fail`.

  Wire them into the report under `metadata.checks`:
  - Stability uses the ledger envelope's `aft_fs` and the model's MAC.
  - Two-method uses the VSPAERO NP when `data/validation/vspaero_native_polars.json` holds a
    current run, else `None`. The bound is **1.0 in**.
  - The NP metric is emitted `NOT GRADED` while `neutral_point_fs` is unverified.
- [ ] **Step 4: Run** the tests, regenerate the report, and triage.
- [ ] **Step 5: Commit** (`feat(report): stability at the manual's aft limit and the two-method NP check`).

---

### Task 9: Block 1 report and done check

**Files:** create `docs/block1-report.md`; modify `docs/geometry-correction-ledger.md`.

- [ ] **Step 1:** Write the report with three parts:
  - **Changed values:** every value that changed in Tasks 3–8, as `| field | was | now | citation or
    flag |`. Generate it from `git diff` of `config/aircraft_config.py` and
    `reference_data.json` since the Block 1 start commit.
  - **Check results:** the stability check, the two-method check (`not run` if OpenVSP is still
    missing) and the NP value.
  - **Still flagged:** every remaining flag, each with the evidence that would clear it.
- [ ] **Step 2:** Verify each "Done when" item in spec §4 and write one line of evidence for each.
- [ ] **Step 3:** Full suite, node tests and `guide.check`, all unpiped. Leak scan the added lines.
  Commit the report and the ledger (`docs: Block 1 report`).

---

### Task 10: Re-export, deploy, grade, push (lead)

- [ ] **Step 1:** `.venv/bin/python -m guide.export_glb`, then run `guide/render_cutaway.sh --wait` if
  the glb or layup changed (expect a new render key), then deploy with
  `source ~/.config/long-ez/env && bash scripts/deploy_guide.sh` and verify it in a browser.
- [ ] **Step 2:** `git fetch`, confirm behind 0, then run
  `TMPDIR=/tmp ~/.claude/bin/grade-diff.sh -s <session> -r origin/main..HEAD ~/open-ez` unsandboxed.
  Expect `VERDICT: PASS`.
- [ ] **Step 3:** Leak scan of the added lines (the pattern from the M1 plan), a green unpiped test
  run, and `git push origin main` in the same turn.
- [ ] **Step 4:** Update memory `project_longez_build_guide`, and republish the roadmap and Block 1
  HTML pages if they changed.
