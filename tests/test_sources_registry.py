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
