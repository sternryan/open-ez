"""Ledger row 74: the M3.4 inputs (sizing rule, lamina, plies, cell geometry, mass inputs) are frozen."""

import copy

from core.equivalence_inputs import _sha, input_groups, inputs_sha256

LEDGER = "docs/geometry-correction-ledger.md"


def _row(n: int) -> str:
    return next(
        line for line in open(LEDGER).read().splitlines() if line.startswith(f"| {n} |")
    )


def test_every_input_hash_is_recorded_in_row_74():
    row = _row(74)
    for name, digest in inputs_sha256().items():
        assert f"{name} `{digest}`" in row, f"{name} changed since row 74: needs a new row"


def test_a_changed_input_changes_its_hash():
    g = input_groups()
    before = _sha(g["book_plies"])
    broken = copy.deepcopy(g["book_plies"])
    broken[0]["count"] += 1
    assert _sha(broken) != before
    assert _sha(g["book_plies"]) == before
