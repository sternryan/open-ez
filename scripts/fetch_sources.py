"""Build the private local source corpus (Owner's Manual text, Canard Pusher OCR).

Output goes under $LONGEZ_SOURCE_CACHE and is never committed. Only counts are printed.
Env: LONGEZ_SOURCE_CACHE, LONGEZ_COBELU_DIR, LONGEZ_CP_SECTIONS.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

CP_BASE = "http://www.cozybuilders.org/Canard_Pusher/"
OM_REL = "Owners Manual/Long-EZ Owners Manual.pdf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


def cp_url(issue: int, date: str) -> str:
    return f"{CP_BASE}{date}_cp-{issue}.pdf"


def split_printed_pages(text: str) -> dict[str, str]:
    """Split on form feeds; a page's printed number is its last non-empty line if all digits."""
    pages: dict[str, str] = {}
    for chunk in text.split("\x0c"):
        lines = chunk.split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines or not lines[-1].strip().isdigit():
            continue
        num = lines.pop().strip()
        pages[num] = "\n".join(lines).strip()
    return pages


def _cache() -> Path:
    raw = os.environ.get("LONGEZ_SOURCE_CACHE") or "~/.cache/long-ez/sources"
    p = Path(raw).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _pad(n: str | int) -> str:
    return f"{int(n):02d}"


def fetch_om(cache: Path) -> None:
    import pymupdf

    pdf = Path(os.environ["LONGEZ_COBELU_DIR"]) / OM_REL
    doc = pymupdf.open(pdf)
    text = "\x0c".join(page.get_text() for page in doc)
    pages = split_printed_pages(text)
    out = cache / "om-1980"
    out.mkdir(parents=True, exist_ok=True)
    for num, body in pages.items():
        (out / f"p{_pad(num)}.txt").write_text(body, encoding="utf-8")
    print(f"om-1980: {len(doc)} pdf pages, {len(pages)} with printed number, {len(doc) - len(pages)} without")


def _cp_date(issue: int) -> str:
    d = Path(os.environ["LONGEZ_CP_SECTIONS"]).parent
    for f in sorted(d.iterdir()):
        m = re.fullmatch(rf"(.+)_cp-{issue}\.txt", f.name)
        if m:
            return m.group(1)
    raise SystemExit(f"no date found for CP issue {issue}")


def fetch_cp(cache: Path, issue: int) -> None:
    import pymupdf

    url = cp_url(issue, _cp_date(issue))
    if not url.startswith(CP_BASE):
        raise SystemExit("refusing non-cozybuilders URL")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    (cache / f"cp-{issue}.pdf").write_bytes(data)
    out = cache / f"cp-{issue}"
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(stream=data, filetype="pdf")
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, page in enumerate(doc, start=1):
            png = Path(tmp) / f"p{i}.png"
            page.get_pixmap(dpi=300).save(png)
            res = subprocess.run(["tesseract", str(png), "stdout"], capture_output=True, text=True, check=True)
            (out / f"p{_pad(i)}.txt").write_text(res.stdout, encoding="utf-8")
            total += len(res.stdout)
    print(f"cp-{issue}: {len(doc)} pages, {total} chars")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--om", action="store_true")
    ap.add_argument("--cp", type=int, nargs="*", default=[])
    args = ap.parse_args(argv)
    cache = _cache()
    if args.om:
        fetch_om(cache)
    for n in args.cp:
        fetch_cp(cache, n)


if __name__ == "__main__":
    main()
