"""The SparStock gate rejects uncited, non-stock-only and unregistered-source blanks."""

import cadquery as cq
import pytest

from core.spar_stock import SparStock


def blank(**overrides):
    fields = {
        "name": "spruce.x",
        "solid": cq.Workplane("XY").box(1, 1, 1),
        "cite": ("plans-1980:p86",),
        "note": "raw spruce stock only",
    }
    fields.update(overrides)
    return SparStock(**fields)


def test_valid_blank_is_accepted():
    assert blank().eligibility == "stock-only"


def test_missing_citation_is_rejected():
    with pytest.raises(ValueError, match="requires citations"):
        blank(cite=())


def test_non_stock_only_eligibility_is_rejected():
    with pytest.raises(ValueError, match="stock-only eligibility"):
        blank(eligibility="finished")


def test_unknown_source_id_is_rejected():
    with pytest.raises(ValueError, match="unknown source id"):
        blank(cite=("no-such-source:p1",))


def test_one_unknown_id_among_valid_citations_is_rejected():
    with pytest.raises(ValueError, match="unknown source id"):
        blank(cite=("plans-1980:p86", "no-such-source:p1"))
