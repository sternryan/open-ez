"""The M3.4 inputs (sizing rule, lamina, plies, cell geometry, mass inputs) are frozen.

Row 74 froze them; row 77 re-recorded all seven hashes after the carbon warp flags changed (labels
only, no value). The test reads the latest freeze row.
"""

import copy

from core.equivalence_inputs import _sha, input_groups, inputs_sha256

LEDGER = "docs/geometry-correction-ledger.md"
FREEZE_ROW = 77


def _row(n: int) -> str:
    return next(
        line for line in open(LEDGER).read().splitlines() if line.startswith(f"| {n} |")
    )


def test_every_input_hash_is_recorded_in_the_freeze_row():
    row = _row(FREEZE_ROW)
    for name, digest in inputs_sha256().items():
        assert f"{name} `{digest}`" in row, (
            f"{name} changed since row {FREEZE_ROW}: needs a new row"
        )


def test_a_changed_input_changes_its_hash():
    g = input_groups()
    before = _sha(g["book_plies"])
    broken = copy.deepcopy(g["book_plies"])
    broken[0]["count"] += 1
    assert _sha(broken) != before
    assert _sha(g["book_plies"]) == before
