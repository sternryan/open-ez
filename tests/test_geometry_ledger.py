# tests/test_geometry_ledger.py
"""Every strict xfail added for book geometry has a ledger row; tolerances weren't widened."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / "docs/geometry-correction-ledger.md").read_text()


def test_every_book_geometry_xfail_cites_a_ledger_row():
    for f in (ROOT / "tests").glob("test_*.py"):
        for m in re.finditer(
            r'reason="book geometry: see docs/geometry-correction-ledger\.md row (\d+)',
            f.read_text(),
        ):
            assert re.search(
                rf"^\|\s*{m.group(1)}\s*\|", LEDGER, re.M
            ), f"{f.name}: ledger row {m.group(1)} missing"


def test_reference_tolerances_unchanged():
    import json

    ref = json.loads((ROOT / "data/validation/reference_data.json").read_text())
    assert ref["aircraft_specs"]["neutral_point_fs"]["tolerance_abs"] == 2.0
