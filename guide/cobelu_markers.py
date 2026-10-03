"""Parse cobelu/Long-EZ inline change markers like '{CP27 PC44 MEO}' with their step heading."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Marker regex: tolerant separators (commas/spaces between parts), class optional
# Matches {CP1,PC2,MEO} or {CP1 PC2 MEO} or {CP1 PC2}
MARK = re.compile(
    r"\{\s*CP\s*(\d+)\s*,?\s*L?PC\s*(\d+)\s*,?\s*([A-Z]{2,4})?\s*\}", re.I
)
HEAD = re.compile(r"^#{2,3}\s+(.*\S)\s*$")
FNAME = re.compile(r"^(\d{1,2})[_-]")
KNOWN_CLASSES = {"MEO", "MAN", "DES", "OPT", "OBS"}


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
    for line_num, line in enumerate(md_text.splitlines(), start=1):
        h = HEAD.match(line)
        if h:
            heading_text = h.group(1)
            heading = MARK.sub("", heading_text).strip()
            # Check for markers on the heading line itself
            for m in MARK.finditer(heading_text):
                cls_text = m.group(3)
                # Only accept known classes or None (default to "?")
                if cls_text and cls_text not in KNOWN_CLASSES:
                    continue  # Skip markers with invalid class codes
                cls_code = cls_text if cls_text in KNOWN_CLASSES else "?"
                # Strip markers from heading
                out.append(
                    Marker(
                        int(m.group(1)),
                        int(m.group(2)),
                        cls_code,
                        chapter,
                        heading,
                        line_num,
                    )
                )
            continue
        for m in MARK.finditer(line):
            cls_text = m.group(3)
            # Only accept known classes or None (default to "?")
            if cls_text and cls_text not in KNOWN_CLASSES:
                continue  # Skip markers with invalid class codes
            cls_code = cls_text if cls_text in KNOWN_CLASSES else "?"
            out.append(
                Marker(
                    int(m.group(1)),
                    int(m.group(2)),
                    cls_code,
                    chapter,
                    heading,
                    line_num,
                )
            )
    return out
