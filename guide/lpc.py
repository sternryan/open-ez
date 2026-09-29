"""Parse Long-EZ plans-change (LPC) entries out of sectioned Canard Pusher text.

Format observed in CPs_1_to_82_Sections.txt:  'LPC #7, MEO, Back cover of plans.'  followed by
description lines until a blank line or the next entry. Attribution = nearest preceding
'THE CANARD PUSHER NO. N' header.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

HEADER = re.compile(r"^\s*THE CANARD PUSHER\s+NO\.?\s*(\d+)", re.I)
ENTRY = re.compile(r"^\s*LPC\s*#\s*(\d+)\s*[:,\-]?\s*(.*)$", re.I)
PAGE = re.compile(r"(?:page|pages|pg)s?\s+(\d{1,2})\s*[-–]\s*(\d{1,2})", re.I)
SECTION = re.compile(r"Section\s+([IV]+(?:[A-Z]+)?)", re.I)


@dataclass(frozen=True)
class PlansChange:
    lpc: int
    cls: str
    page: str | None
    chapter: int | None
    cp: int
    text: str


def _extract_cls_and_ref(rest: str) -> tuple[str, str]:
    """Extract class code (if present) from rest of line. Return (cls, ref)."""
    rest = rest.strip()
    # Try to match: 2-4 uppercase letters followed by whitespace or separator
    # But NOT "Section" or "Page"
    m = re.match(r'^([A-Z]{2,4})(?:\s|[:,\-])(.*)$', rest)
    if m:
        word = m.group(1)
        if word.upper() not in ("SECTION", "PAGE", "PAGES", "PG"):
            return word, m.group(2).strip()
    return "?", rest

def _page(ref: str, next_line: str = "") -> tuple[str | None, int | None]:
    """Extract page and chapter from ref text. Check next line if needed."""
    # Check for Section reference first
    section_m = SECTION.search(ref)
    is_section_i = section_m and section_m.group(1).upper() == "I"
    is_non_i_section = section_m and section_m.group(1).upper() != "I"

    # Check for page number in current ref
    m = PAGE.search(ref)
    if m:
        page_str = f"{int(m.group(1))}-{int(m.group(2))}"
        # Non-I section: chapter is None
        if is_non_i_section:
            return page_str, None
        # Section I or no section: chapter is from page number
        return page_str, int(m.group(1))

    # No page found - check for back-cover indicators
    if "back cover" in ref.lower() or "owner" in ref.lower():
        return "back-cover", None

    # Section I with no page number: return back-cover as placeholder, chapter None
    if is_section_i:
        return "back-cover", None

    # Non-I section with no page: return back-cover with chapter None
    if is_non_i_section:
        return "back-cover", None

    # Check next line for page (Section I without page yet)
    if next_line:
        m = PAGE.search(next_line)
        if m:
            return f"{int(m.group(1))}-{int(m.group(2))}", int(m.group(1))

    return None, None


def parse_lpcs(text: str) -> list[PlansChange]:
    out: list[PlansChange] = []
    cp = 0
    cur: dict | None = None
    lines_list = text.splitlines()

    def flush():
        if cur is not None and cp_of_cur is not None:
            # Try to get page from next line (first description line)
            next_line = cur["lines"][0] if cur["lines"] else ""
            page, chapter = _page(cur["ref"], next_line)
            out.append(PlansChange(cur["lpc"], cur["cls"], page, chapter, cp_of_cur, " ".join(cur["lines"]).strip()))

    cp_of_cur: int | None = None
    for i, line in enumerate(lines_list):
        h = HEADER.match(line)
        e = ENTRY.match(line)
        if h or e or not line.strip():
            flush()
            cur, cp_of_cur = None, None
        if h:
            cp = int(h.group(1))
            continue
        if e:
            if cp == 0:
                continue
            lpc_num = int(e.group(1))
            rest = e.group(2)
            cls_code, ref = _extract_cls_and_ref(rest)
            cur = {"lpc": lpc_num, "cls": cls_code, "ref": ref, "lines": []}
            cp_of_cur = cp
            continue
        if cur is not None and line.strip():
            cur["lines"].append(line.strip())
    flush()
    return out
