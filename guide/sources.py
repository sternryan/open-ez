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
        if k == "cp":
            out[k] = p if p and p.is_file() else None
        else:
            out[k] = p if p and p.is_dir() else None
    return out


def source_problems(paths: dict[str, Path | None]) -> list[str]:
    problems: list[str] = []
    if paths["cp"] is None:
        problems.append("CP file missing or not a file")
    elif paths["cp"].stat().st_size == 0:
        problems.append("CP file is empty")
    if paths["cobelu"] is None:
        problems.append("cobelu directory missing or not a directory")
    else:
        md_dir = paths["cobelu"] / "I" / "md"
        if not md_dir.exists() or not list(md_dir.glob("*.md")):
            problems.append(f"{md_dir} has no *.md files")
    if paths["scan_text"] is None:
        problems.append("scan_text directory missing or not a directory")
    else:
        if not list(paths["scan_text"].glob("*.txt")):
            problems.append(f"{paths['scan_text']} has no *.txt files")
    return problems


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
