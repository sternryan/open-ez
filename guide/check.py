"""python -m guide.check — schema + verbatim-overlap gate + annotation recall. Full mode is the pre-commit gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from guide.linker import candidates, recall
from guide.lpc import parse_lpcs
from guide.overlap import SourceIndex
from guide.schema import SchemaError, authored_texts, load_graph, validate
from guide.sources import ENV, load_markers, load_source_texts, source_paths


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.check")
    ap.add_argument("--graph", default="guide/graph")
    ap.add_argument("--schema-only", action="store_true")
    ap.add_argument("--chapters", default="10,12")
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
        paths = source_paths()
        missing = [ENV[k] for k, p in paths.items() if p is None]
        if missing:
            print(f"SOURCES MISSING: {', '.join(missing)} — full-mode gate cannot run")
            return 2
        idx = SourceIndex(load_source_texts(paths))
        for loc, text in authored_texts(g):
            for h in idx.hits(text):
                fails.append(f"OVERLAP: {loc}: '{h}'")
        cands = candidates(g, parse_lpcs(paths["cp"].read_text(errors="ignore")), load_markers(paths["cobelu"]))
        hits, misses = recall(g, cands, {int(c) for c in a.chapters.split(",")})
        print(f"RECALL: {len(hits)}/{len(hits) + len(misses)} confirmed annotations recovered")
        fails += [f"RECALL MISS: scan_pp {m.scan_pp} CP {m.cp} LPC {m.lpc}" for m in misses]

    for f in fails:
        print(f)
    print("OK" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
