"""Parse cobelu/Long-EZ inline change markers like '{CP27 PC44 MEO}' with their step heading."""
from __future__ import annotations

import re
from dataclasses import dataclass

MARK = re.compile(r"\{\s*CP\s*(\d+)\s+L?PC\s*(\d+)\s+([A-Z]{2,4})\s*\}")
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
            heading = h.group(1)
            continue
        for m in MARK.finditer(line):
            out.append(Marker(int(m.group(1)), int(m.group(2)), m.group(3), chapter, heading, i))
    return out
