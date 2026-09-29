import fitz
import pytest
from guide.scan_ingest import parse_page_ref, render_pages


@pytest.mark.parametrize("raw,want", [
    ("PAGE 6-3", "6-3"), ("Pg 10 – 5", "10-5"), ("pg. 12-1", "12-1"),   # Review Focus 5
    ("P6 11-3", "11-3"), ("PAGE  3 -16", "3-16"), ("no ref here", None)])
def test_parse_page_ref(raw, want):
    assert parse_page_ref(raw) == want


def test_render_pages_zero_padded(tmp_path):
    pdf = tmp_path / "t.pdf"
    doc = fitz.open(); [doc.new_page() for _ in range(2)]; doc.save(pdf)
    assert render_pages(pdf, tmp_path / "pages", dpi=30) == 2
    assert sorted(p.name for p in (tmp_path / "pages").iterdir()) == ["001.jpg", "002.jpg"]
