"""8-word shingle overlap gate: authored text must not share a verbatim run with plans/CP sources."""
from __future__ import annotations

import re
from typing import Iterable

WORD = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int = 8) -> set[tuple[str, ...]]:
    w = WORD.findall(text.lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


class SourceIndex:
    def __init__(self, texts: Iterable[str], n: int = 8):
        self.n = n
        self._set: set[tuple[str, ...]] = set()
        for t in texts:
            self._set |= shingles(t, n)

    def hits(self, text: str) -> list[str]:
        return sorted(" ".join(s) for s in shingles(text, self.n) & self._set)
