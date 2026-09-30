"""Assemble the static site: viewer + graph.json + config.json + model + rendered docs."""
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import shutil
import sys
from pathlib import Path

from guide import layup, render_key
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


LEGEND = [
    {"swatch": "und", "text": "UND (unidirectional): light and dark alternate by ply"},
    {"swatch": "bid", "text": "BID (biaxial): light and dark alternate by ply"},
    {"swatch": "foam", "text": "Foam core"},
    {"swatch": "unverified", "text": "Striped: web/spar position not verified"},
    {"swatch": None, "text": "Numbers = lay order"},
    {"swatch": None, "text": "Spar caps: plies as required to fill trough"},
    {"swatch": None, "text": "Canard planform: GU size from the Owner's Manual; Roncz planform unconfirmed"},
    {"swatch": None, "text": "Not to scale"},
]


def _plies(models: Path | None) -> dict:
    lj = models.parent / "layup.json" if models else None
    if not lj or not lj.is_file():
        return {}
    out: dict = {}
    for node, n in json.loads(lj.read_text())["nodes"].items():
        out.setdefault(n["component"], []).append(
            {"node": node, "op": n["op"], "order": n["order"], "cloth": n["cloth"], "where": n["where"],
             "position_verified": n["position_verified"]})
    for rows in out.values():
        rows.sort(key=lambda r: r["order"])
    return out


def _cutaway(g, models: Path, renders: Path, out: Path) -> dict:
    if not all((models.parent / f).is_file() for f in ("layup.json", "shots.json")):
        raise SchemaError("--renders needs layup.json and shots.json next to --models (run guide.export_glb)")
    probs = render_key.check_renders(renders, models.parent, None)
    if probs:
        raise SchemaError("renders: " + "; ".join(probs))
    pl = layup.plies(g)
    (out / "renders").mkdir()
    shots = json.loads((models.parent / "shots.json").read_text())
    for s in shots:
        shutil.copy(renders / f"{s['id']}.png", out / "renders" / f"{s['id']}.png")
    src = lambda s: f"renders/{s['id']}.png"  # noqa: E731
    return {
        "ops": {s["highlight"]: {"src": src(s), "alt": layup.alt_text(g, pl, s)} for s in shots if s["kind"] == "op"},
        "heroes": [{"bl": s["bl"], "src": src(s), "alt": layup.alt_text(g, pl, s)} for s in shots if s["kind"] == "hero"],
        "legend": LEGEND,
        "count_note": layup.count_note(pl),
    }


def build(graph_dir: Path, out: Path, models: Path | None, scan_base: str | None, docs: Path | None,
          renders: Path | None = None) -> None:
    if renders and not models:
        raise SchemaError("--renders needs --models (the renders are checked against its layup.json/shots.json)")
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
        "plies": _plies(models),
        "cutaway": None,
    }
    if renders:
        payload["cutaway"] = _cutaway(g, models, renders, out)
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
    ap.add_argument("--renders", type=Path, default=None)
    ap.add_argument("--docs", type=Path, default=Path("docs/superpowers"))
    a = ap.parse_args(argv)
    build(a.graph, a.out, a.models, a.scan_base, a.docs, renders=a.renders)
    print(f"built {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
