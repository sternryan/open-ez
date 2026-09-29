"""Render the owner's plans scan to private page images + OCR text + a proposed page map.
All outputs go OUTSIDE the repo (default ~/.cache/long-ez/scan-1980). Never commit them."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
import yaml

REF = re.compile(r"(?:PAGE|PG|P6)\s*\.?\s*(\d{1,2})\s*[-–—]\s*(\d{1,2})", re.I)


def parse_page_ref(text: str) -> str | None:
    m = REF.search(text)
    return f"{int(m.group(1))}-{int(m.group(2))}" if m else None


def render_pages(pdf: Path, out_dir: Path, dpi: int = 150) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(dpi=dpi).save(out_dir / f"{i:03d}.jpg", jpg_quality=80)
    return len(doc)


def _ocr(img: Path) -> str:
    return subprocess.run(["tesseract", str(img), "-", "--psm", "6"], capture_output=True, text=True, check=True).stdout


def ocr_pages(pages_dir: Path, text_dir: Path) -> int:
    text_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for img in sorted(pages_dir.glob("*.jpg")):
        (text_dir / f"{img.stem}.txt").write_text(_ocr(img))
        n += 1
    return n


def propose_page_map(pdf: Path) -> dict[int, str | None]:
    doc = fitz.open(pdf)
    out: dict[int, str | None] = {}
    tmp = Path(tempfile.mkdtemp()) / "strip.png"
    for i, page in enumerate(doc, start=1):
        r = page.rect
        ref = None
        for clip in (fitz.Rect(0, r.height * 0.86, r.width, r.height), fitz.Rect(0, 0, r.width, r.height * 0.10)):
            page.get_pixmap(dpi=150, clip=clip).save(tmp)
            ref = parse_page_ref(_ocr(tmp))
            if ref:
                break
        out[i] = ref
    tmp.unlink(missing_ok=True)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.scan_ingest")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, default=Path("~/.cache/long-ez/scan-1980").expanduser())
    a = ap.parse_args(argv)
    n = render_pages(a.pdf, a.out / "pages")
    ocr_pages(a.out / "pages", a.out / "text")
    (a.out / "page_map.proposed.yaml").write_text(yaml.safe_dump(propose_page_map(a.pdf)))
    print(f"rendered {n} pages -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
