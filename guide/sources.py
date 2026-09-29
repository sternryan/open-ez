"""Locate private source corpora (never in git) via env vars."""
from __future__ import annotations

import os
from pathlib import Path

from guide.cobelu_markers import Marker, chapter_from_filename, parse_markers

ENV = {"cp": "LONGEZ_CP_SECTIONS", "cobelu": "LONGEZ_COBELU_DIR", "scan_text": "LONGEZ_SCAN_TEXT_DIR"}


def source_paths() -> dict[str, Path | None]:
    out: dict[str, Path | None] = {}
    for k, var in ENV.items():
        v = os.environ.get(var)
        p = Path(v).expanduser() if v else None
        out[k] = p if p and p.exists() else None
    return out


def _cobelu_md(cobelu: Path) -> list[Path]:
    return sorted((cobelu / "I" / "md").glob("*.md"))


def load_source_texts(paths: dict[str, Path]) -> list[str]:
    texts = [paths["cp"].read_text(errors="ignore")]
    texts += [p.read_text(errors="ignore") for p in _cobelu_md(paths["cobelu"])]
    texts += [p.read_text(errors="ignore") for p in sorted(paths["scan_text"].glob("*.txt"))]
    return texts


def load_markers(cobelu: Path) -> list[Marker]:
    out: list[Marker] = []
    for p in _cobelu_md(cobelu):
        ch = chapter_from_filename(p.name)
        if ch is not None:
            out += parse_markers(p.read_text(errors="ignore"), ch)
    return out
