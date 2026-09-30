"""Leak scan for a public site build: plans content, private locations and network identifiers must not ship."""
from __future__ import annotations

import re
import sys
from pathlib import Path

TEXT = {".html", ".js", ".mjs", ".css", ".json", ".txt", ".svg", ".map", ".md", ".yaml", ".yml", ".webmanifest"}
BAD_FILES = {".jpg", ".jpeg", ".tif", ".tiff", ".pdf"}
PATTERNS = {
    "private/ path": re.compile(r"private/"),
    "cobelu": re.compile(r"cobelu", re.I),
    "plans figure url": re.compile(r"images/\d+/\d+_\d+"),
    "tailnet hostname": re.compile(r"\.ts\.net"),
    "tailnet IP (100.x)": re.compile(r"(?<![\d.])100\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])"),
    "home path": re.compile(r"/Users/"),
    "forbidden phrase 'public domain'": re.compile(r"public domain", re.I),
    "airsup": re.compile(r"airsup", re.I),
}


def leaks(root: Path) -> list[str]:
    """Every problem found under root, as 'path: what'. Empty means clean."""
    out: list[str] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if p.suffix.lower() in BAD_FILES:
            out.append(f"{rel}: image/scan file type {p.suffix}")
        if "private" in rel.parts:
            out.append(f"{rel}: private/ directory")
        if p.suffix.lower() == ".png" and not (rel.parts[0] == "renders"):
            out.append(f"{rel}: png outside renders/ (our own stills only)")
        if p.suffix.lower() in TEXT:
            t = p.read_text(errors="ignore")
            for name, rx in PATTERNS.items():
                if (m := rx.search(t)):
                    out.append(f"{rel}: {name} ({t[max(0, m.start() - 20):m.end() + 20]!r})")
    return out


def main(argv: list[str] | None = None) -> int:
    root = Path((argv or sys.argv[1:])[0])
    found = leaks(root)
    for f in found:
        print("LEAK", f, file=sys.stderr)
    print(f"leakcheck {root}: {'FAIL' if found else 'clean'}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
