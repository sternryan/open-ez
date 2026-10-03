"""python -m guide.check — schema + verbatim-overlap gate + annotation recall. Full mode is the pre-commit gate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from guide.linker import candidates, recall
from guide.lpc import parse_lpcs
from guide.overlap import SourceIndex
from guide.schema import SchemaError, authored_texts, load_graph, validate
from guide.sources import (
    ENV,
    load_markers,
    load_source_texts,
    source_paths,
    source_problems,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.check")
    ap.add_argument("--graph", default="guide/graph")
    ap.add_argument("--schema-only", action="store_true")
    ap.add_argument("--chapters", default="4,5,6,7,8,9,10,12")
    a = ap.parse_args(argv)

    try:
        g = load_graph(Path(a.graph))
    except SchemaError as e:
        print(f"SCHEMA: {e}")
        return 1
    fails = [f"SCHEMA: {e}" for e in validate(g)]

    if a.schema_only:
        print("OVERLAP GATE NOT RUN (--schema-only)")
    else:
        # Parse chapters early to catch errors
        try:
            chapters_set = {int(c) for c in a.chapters.split(",")}
        except ValueError:
            print(
                f"--chapters parse error: '{a.chapters}' is not a comma-separated list of integers"
            )
            return 2

        paths = source_paths()
        missing = [ENV[k] for k, p in paths.items() if p is None]
        problems = source_problems(paths)

        if missing or problems:
            if missing:
                print(
                    f"SOURCES MISSING: {', '.join(missing)} — full-mode gate cannot run"
                )
            for p in problems:
                print(p)
            return 2

        texts = load_source_texts(paths)
        idx = SourceIndex(texts)

        if len(idx) == 0:
            print("SOURCES: 0 shingles indexed — vacuous gate, FAIL")
            return 2

        print(f"SOURCES: {len(texts)} texts, {len(idx)} shingles indexed")

        for loc, text in authored_texts(g):
            for h in idx.hits(text):
                # Truncate to first 3 words + "…"
                words = h.split()[:3]
                truncated = " ".join(words) + "…"
                fails.append(f"OVERLAP: {loc}: '{truncated}'")

        cands = candidates(
            g,
            parse_lpcs(paths["cp"].read_text(errors="ignore")),
            load_markers(paths["cobelu"]),
        )
        hits, misses = recall(g, cands, chapters_set)

        total = len(hits) + len(misses)
        if total == 0:
            print("RECALL: 0/0 (no confirmed annotations in scope)")
        else:
            print(f"RECALL: {len(hits)}/{total} confirmed annotations recovered")

        fails += [
            f"RECALL MISS: scan_pp {m.scan_pp} CP {m.cp} LPC {m.lpc}" for m in misses
        ]

    for f in fails:
        print(f)
    print("OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
