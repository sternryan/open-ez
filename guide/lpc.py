"""Parse Long-EZ plans-change (LPC) entries out of sectioned Canard Pusher text.

Format observed in CPs_1_to_82_Sections.txt:  'LPC #7, MEO, Back cover of plans.'  followed by
description lines until a blank line or the next entry. Attribution = nearest preceding
'THE CANARD PUSHER NO. N' header.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

HEADER = re.compile(r"^\s*THE CANARD PUSHER\s+NO\.\s*(\d+)", re.I)
ENTRY = re.compile(r"^\s*LPC\s*#\s*(\d+)\s*,\s*([A-Z]{2,4})\s*,?\s*(.*)$")
PAGE = re.compile(r"Page\s+(\d{1,2})\s*[-–]\s*(\d{1,2})", re.I)


@dataclass(frozen=True)
class PlansChange:
    lpc: int
    cls: str
    page: str | None
    chapter: int | None
    cp: int
    text: str


def _page(ref: str) -> tuple[str | None, int | None]:
    m = PAGE.search(ref)
    if m:
        return f"{int(m.group(1))}-{int(m.group(2))}", int(m.group(1))
    if "back cover" in ref.lower():
        return "back-cover", None
    return None, None


def parse_lpcs(text: str) -> list[PlansChange]:
    out: list[PlansChange] = []
    cp = 0
    cur: dict | None = None

    def flush():
        if cur is not None and cp_of_cur is not None:
            page, chapter = _page(cur["ref"])
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
            cur = {"lpc": int(e.group(1)), "cls": e.group(2), "ref": e.group(3), "lines": []}
            cp_of_cur = cp
            continue
        if cur is not None and line.strip():
            cur["lines"].append(line.strip())
    flush()
    return out
