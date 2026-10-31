# tests/test_ledger_gate.py
"""The gear-row gate in core/ledger.py rejects a broken ledger: bad citation, no citation, drifted candidates."""

import copy

import pytest

from core import ledger


def _broken(monkeypatch, edit):
    data = copy.deepcopy(ledger.load_ledger())
    edit(data)
    monkeypatch.setattr(ledger, "load_ledger", lambda: data)


def _first_row(data):
    return data["gear"]["rows"][0]


def test_gear_row_with_an_unknown_source_id_is_rejected(monkeypatch):
    _broken(monkeypatch, lambda d: _first_row(d).update(cite=["nosuch-doc:p1"]))
    with pytest.raises(ValueError, match="unknown source id"):
        ledger.gear_rows()


def test_gear_row_with_a_malformed_citation_is_rejected(monkeypatch):
    _broken(monkeypatch, lambda d: _first_row(d).update(cite=["plans-1980 page 50"]))
    with pytest.raises(ValueError, match="citation must be"):
        ledger.gear_rows()


def test_sourced_gear_row_with_no_citation_is_rejected(monkeypatch):
    def edit(d):
        _first_row(d).update(status="book", cite=[])

    _broken(monkeypatch, edit)
    with pytest.raises(ValueError, match="a sourced row needs a citation"):
        ledger.gear_rows()


def test_unsourced_gear_row_may_have_no_citation(monkeypatch):  # the gate is not over-strict
    _broken(monkeypatch, lambda d: _first_row(d).update(status="unsourced", cite=[]))
    assert ledger.gear_rows()[0].cite == ()


def test_nose_arm_candidates_that_disagree_with_config_are_rejected(monkeypatch):
    def edit(d):
        d["gear"]["nose_arm_candidates"]["values_in"] = [17.0, 21.0]

    _broken(monkeypatch, edit)
    with pytest.raises(ValueError, match="disagree with config"):
        ledger.gear_json()
