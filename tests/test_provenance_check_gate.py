"""validate_provenance must reject a broken table (a rule only asserted over shipped data proves nothing)."""

import copy

import pytest

from config.aircraft_config import GEOMETRY_PROVENANCE
from config.provenance_check import validate_provenance
from core.sources import check_citation

FIELDS = set(GEOMETRY_PROVENANCE)


def broken(mutate):
    table = copy.deepcopy(GEOMETRY_PROVENANCE)
    mutate(table)
    return table


def a_book_field(table):
    return next(k for k, e in table.items() if e["status"] == "book")


def test_the_clean_table_passes():
    assert validate_provenance(GEOMETRY_PROVENANCE, FIELDS, check_citation) == []


@pytest.mark.parametrize(
    "mutate, fragment",
    [
        (lambda t: t[a_book_field(t)].update(status="made-up"), "unknown status"),
        (lambda t: t[a_book_field(t)].update(source="  "), "needs a source"),
        (lambda t: t[a_book_field(t)].update(source="no-such-source-id:p1"), "bad citation"),
        (lambda t: t[a_book_field(t)].update(confidence="certain"), "unknown confidence"),
        (lambda t: t[a_book_field(t)].pop("note"), "keys"),
    ],
)
def test_a_broken_entry_is_rejected(mutate, fragment):
    errors = validate_provenance(broken(mutate), FIELDS, check_citation)
    assert any(fragment in e for e in errors), errors


def test_a_missing_entry_is_rejected():
    table = broken(lambda t: t.pop(a_book_field(t)))
    assert any("missing" in e for e in validate_provenance(table, FIELDS, check_citation))


def test_a_stale_entry_is_rejected():
    table = broken(lambda t: t.update(ghost_field=dict(status="unsourced", source="", confidence="n/a", note="")))
    assert any("stale" in e for e in validate_provenance(table, FIELDS, check_citation))
