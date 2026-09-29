"""Parse cobelu/Long-EZ inline change markers like '{CP27 PC44 MEO}' with their step heading."""
from __future__ import annotations

import re
from dataclasses import dataclass

# More tolerant marker regex: optional commas/spaces, optional class, accept LPC or PC
MARK = re.compile(r"\{\s*CP\s*(\d+)\s*[:,]?\s+L?PC\s*(\d+)\s*[:,]?\s*(?:([A-Z]{2,4}))?\s*\}", re.I)
HEAD = re.compile(r"^#{2,3}\s+(.*\S)\s*$")
FNAME = re.compile(r"^(\d{1,2})[_-]")


@dataclass(frozen=True)
class Marker:
    cp: int
    lpc: int
    cls: str
    chapter: int
    heading: str
    line: int


def chapter_from_filename(name: str) -> int | None:
    m = FNAME.match(name)
    return int(m.group(1)) if m else None


def parse_markers(md_text: str, chapter: int) -> list[Marker]:
    out: list[Marker] = []
    heading = ""
    for i, line in enumerate(md_text.splitlines(), start=1):
        h = HEAD.match(line)
        if h:
            heading_text = h.group(1)
            # Check for markers on the heading line itself
            for m in MARK.finditer(heading_text):
                cls_code = m.group(3) if m.group(3) else "?"
                # Strip markers from heading
                heading = MARK.sub("", heading_text).strip()
                out.append(Marker(int(m.group(1)), int(m.group(2)), cls_code, chapter, heading, i))
            if not MARK.search(heading_text):
                heading = heading_text
            continue
        for m in MARK.finditer(line):
            cls_code = m.group(3) if m.group(3) else "?"
            out.append(Marker(int(m.group(1)), int(m.group(2)), cls_code, chapter, heading, i))
    return out
