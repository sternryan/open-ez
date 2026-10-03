import fitz
import pytest
from guide.scan_ingest import parse_page_ref, render_pages, main


@pytest.mark.parametrize(
    "raw,want",
    [
        ("PAGE 6-3", "6-3"),
        ("Pg 10 – 5", "10-5"),
        ("pg. 12-1", "12-1"),  # Review Focus 5
        ("P6 11-3", "11-3"),
        ("PAGE  3 -16", "3-16"),
        ("no ref here", None),
        ("xPG 1-2", None),
    ],
)  # word boundary test
def test_parse_page_ref(raw, want):
    assert parse_page_ref(raw) == want


def test_render_pages_zero_padded(tmp_path):
    pdf = tmp_path / "t.pdf"
    doc = fitz.open()
    [doc.new_page() for _ in range(2)]
    doc.save(pdf)
    assert render_pages(pdf, tmp_path / "pages", dpi=30) == 2
    assert sorted(p.name for p in (tmp_path / "pages").iterdir()) == [
        "001.jpg",
        "002.jpg",
    ]


def test_main_refuses_out_inside_repo_even_with_cwd_elsewhere(tmp_path, monkeypatch):
    from guide.scan_ingest import REPO_ROOT

    monkeypatch.chdir(
        tmp_path
    )  # no .git above CWD; guard must use the module's repo root
    pdf = tmp_path / "t.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf)
    target = REPO_ROOT / "private" / "scan-test-should-not-exist"
    assert main([str(pdf), "--out", str(target)]) == 2
    assert not target.exists()
