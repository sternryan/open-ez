import fitz
import pytest
from pathlib import Path
from guide.scan_ingest import parse_page_ref, render_pages, main


@pytest.mark.parametrize("raw,want", [
    ("PAGE 6-3", "6-3"), ("Pg 10 – 5", "10-5"), ("pg. 12-1", "12-1"),   # Review Focus 5
    ("P6 11-3", "11-3"), ("PAGE  3 -16", "3-16"), ("no ref here", None),
    ("xPG 1-2", None)])  # word boundary test
def test_parse_page_ref(raw, want):
    assert parse_page_ref(raw) == want


def test_render_pages_zero_padded(tmp_path):
    pdf = tmp_path / "t.pdf"
    doc = fitz.open(); [doc.new_page() for _ in range(2)]; doc.save(pdf)
    assert render_pages(pdf, tmp_path / "pages", dpi=30) == 2
    assert sorted(p.name for p in (tmp_path / "pages").iterdir()) == ["001.jpg", "002.jpg"]


def test_main_refuses_out_inside_repo(tmp_path, monkeypatch):
    """main() should refuse if --out points inside the git repo root"""
    # Create a tmp repo-like structure
    repo_root = tmp_path / "fake_repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    (repo_root / "guide").mkdir()
    monkeypatch.chdir(repo_root / "guide")

    out_inside_repo = repo_root / "output"
    pdf = tmp_path / "t.pdf"
    doc = fitz.open(); doc.new_page(); doc.save(pdf)

    # Call main with --out inside repo
    exit_code = main([str(pdf), "--out", str(out_inside_repo)])

    # Should refuse with exit 2
    assert exit_code == 2
    # Should not create output directory
    assert not out_inside_repo.exists()
