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
SECTION = re.compile(r"Section\s+((?:I|II|III|IV|V|VI|VII|VIII|IX|X)[ABCL]?)\b")
KNOWN_CLASSES = {"MEO", "MAN", "DES", "OPT", "OBS"}


@dataclass(frozen=True)
class PlansChange:
    lpc: int
    cls: str
    page: str | None
    chapter: int | None
    cp: int
    text: str


def _extract_cls_and_ref(rest: str) -> tuple[str, str]:
    """Extract class code (if present, must be a known class) from rest of line.
    Return (cls, ref). cls defaults to "?" if no known class found.
    """
    rest = rest.strip()
    # Try to match: 2-4 uppercase letters followed by whitespace or separator
    m = re.match(r'^([A-Z]{2,4})(?:\s|[:,\-])(.*)$', rest)
    if m:
        word = m.group(1)
        if word in KNOWN_CLASSES:
            return word, m.group(2).strip()
    return "?", rest

OWNER = re.compile(r"owner[\u2019']?s?[\u2019']?\s+manual", re.I)
BACK_COVER = re.compile(r"back\s+cover", re.I)


def _has_location_cue(text: str) -> bool:
    """Check if text contains a location cue: page reference, section, back cover, or owner manual."""
    if not text:
        return False
    return bool(PAGE.search(text) or SECTION.search(text) or BACK_COVER.search(text) or OWNER.search(text))


def _page(ref: str, next_line: str = "") -> tuple[str | None, int | None]:
    """Extract (page, chapter) from the entry ref plus the first description line.

    All cues are evaluated on the combined text (ref first, then next line):
    - numbered page wins over back-cover; back-cover only when literally present.
    - chapter None if a non-Section-I section or an owner's manual is named anywhere.
    - Section I (word-bounded) keeps the page's chapter; no page -> (None, None).
    """
    # Precedence: entry ref's own location cue wins; description line only as fallback.
    loc = ref if _has_location_cue(ref) else next_line
    # Page number alone may still come from the description line when the ref has none.
    page_m = PAGE.search(loc) or (PAGE.search(next_line) if next_line else None)
    sections = {m.group(1) for m in SECTION.finditer(loc)}
    no_chapter = bool(OWNER.search(loc)) or any(x != "I" for x in sections)

    if page_m:
        chapter = None if no_chapter else int(page_m.group(1))
        return f"{int(page_m.group(1))}-{int(page_m.group(2))}", chapter
    if BACK_COVER.search(loc):
        return "back-cover", None
    return None, None


def parse_lpcs(text: str) -> list[PlansChange]:
    out: list[PlansChange] = []
    cp = 0
    cur: dict | None = None

    def flush():
        if cur is not None and cp_of_cur is not None:
            # Entry acceptance: must have known class OR location cue
            has_known_class = cur["cls"] in KNOWN_CLASSES
            next_line = cur["lines"][0] if cur["lines"] else ""
            has_location_cue = _has_location_cue(cur["ref"]) or _has_location_cue(next_line)
            if not (has_known_class or has_location_cue):
                return  # Reject prose lines
            page, chapter = _page(cur["ref"], next_line)
            out.append(PlansChange(cur["lpc"], cur["cls"], page, chapter, cp_of_cur, " ".join(cur["lines"]).strip()))

    cp_of_cur: int | None = None
    for line in text.splitlines():
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
