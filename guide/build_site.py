"""Assemble the static site: viewer + graph.json + config.json + model + rendered docs."""
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import shutil
import sys
from pathlib import Path

from guide.schema import SchemaError, load_graph, topo_order, validate

VIEWER = Path(__file__).parent / "viewer"


def _op_json(op) -> dict:
    d = dataclasses.asdict(op)
    for c in d["changes"]:
        c["class"] = c.pop("cls")
    return d


def _render_docs(docs: Path, out: Path) -> None:
    import markdown

    out.mkdir(parents=True, exist_ok=True)
    items = []
    for md in sorted(list((docs / "specs").glob("*build-guide*.md")) + list((docs / "plans").glob("*build-guide*.md"))):
        body = markdown.markdown(md.read_text(), extensions=["tables", "fenced_code"])
        (out / f"{md.stem}.html").write_text(
            f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(md.stem)}</title><link rel=stylesheet href='../css/app.css'>"
            f"<main style='display:block;max-width:860px;margin:auto;padding:16px;height:auto'>{body}</main>")
        items.append(f"<li><a href='{md.stem}.html'>{html.escape(md.stem)}</a></li>")
    (out / "index.html").write_text("<!doctype html><meta charset=utf-8><title>docs</title><ul>" + "".join(items) + "</ul>")


def build(graph_dir: Path, out: Path, models: Path | None, scan_base: str | None, docs: Path | None) -> None:
    g = load_graph(graph_dir)
    errs = validate(g)
    if errs:
        raise SchemaError("; ".join(errs))
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(VIEWER, out, ignore=shutil.ignore_patterns("tests"))
    payload = {
        "ops": [_op_json(g.ops[i]) for i in topo_order(g)],
        "order": topo_order(g),
        "components": {c.id: {"label": c.label, "fidelity": c.fidelity} for c in g.components.values()},
        "pages": {str(k): v for k, v in g.pages.items()},
        "annotations": [dataclasses.asdict(a) for a in g.annotations if a.confirmed],
    }
    (out / "graph.json").write_text(json.dumps(payload, indent=1))
    (out / "config.json").write_text(json.dumps({"scanBase": scan_base, "model": "models/longez.glb"}))
    (out / "models").mkdir()
    if models:
        shutil.copy(models, out / "models" / "longez.glb")
    if docs:
        _render_docs(docs, out / "docs")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.build_site")
    ap.add_argument("--graph", type=Path, default=Path("guide/graph"))
    ap.add_argument("--out", type=Path, default=Path("site"))
    ap.add_argument("--models", type=Path, default=None)
    ap.add_argument("--scan-base", default=None)
    ap.add_argument("--docs", type=Path, default=Path("docs/superpowers"))
    a = ap.parse_args(argv)
    build(a.graph, a.out, a.models, a.scan_base, a.docs)
    print(f"built {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
