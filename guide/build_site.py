"""Assemble the static site: viewer + graph.json + config.json + model + rendered docs."""

from __future__ import annotations

import argparse
import fcntl
import dataclasses
import os
import html
import json
import hashlib
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from guide import layup, render_key
from guide.catalog import DATA, is_stale, load_catalog
from guide.resin import load_resins
from guide.schema import SchemaError, load_graph, topo_order, validate
from guide.scripts_schema import load_scripts, scripts_for, validate_scripts
from hangar.records import load_records, load_spots

VIEWER = Path(__file__).parent / "viewer"
LAB = Path(__file__).parent / "lab"
_LAB_INPUTS = (
    "package.json",
    "package-lock.json",
    "index.html",
    "hangar.html",
    "briefing.html",
    "tsconfig.json",
    "vite.config.mjs",
)


def _digest(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.relative_to(LAB)).encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def _lab_stamp() -> str:
    files = [LAB / n for n in _LAB_INPUTS if (LAB / n).is_file()]
    files += sorted(p for p in (LAB / "src").rglob("*") if p.is_file())
    return _digest(files)


def build_lab() -> Path:
    """Build guide/lab with npm (only when its inputs changed) and return its dist directory. Never skips silently.

    Holds an exclusive file lock for the whole check-and-build, so parallel callers (pytest -n) build once and the
    rest wait and reuse it; concurrent `npm ci` / `vite build` runs on one directory corrupt each other."""
    LAB.mkdir(parents=True, exist_ok=True)
    with open(LAB / ".build.lock", "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            return _build_lab_locked()
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _build_lab_locked() -> Path:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError(
            "building the lab needs node and npm on PATH (install Node 20+); it is not skipped silently"
        )
    dist, mods = LAB / "dist", LAB / "node_modules"
    lock_stamp = mods / ".lock-stamp"
    lock = _digest([LAB / "package-lock.json"])
    if not mods.is_dir() or not lock_stamp.is_file() or lock_stamp.read_text() != lock:
        if os.environ.get("FABRIC_SEALED_ENV") == "1":
            # A sealed (network-less, read-only node_modules) environment must fail loudly, never reach for `npm ci` or write the stamp.
            raise RuntimeError(
                "sealed environment: guide/lab/node_modules is missing or its .lock-stamp does not match package-lock.json; "
                "refusing to run `npm ci` (rebuild the sealed runtime for this lock instead)"
            )
        subprocess.run([npm, "--prefix", str(LAB), "ci"], check=True)
        lock_stamp.write_text(lock)
    stamp = _lab_stamp()
    if (
        not (dist / "index.html").is_file()
        or not (dist / ".stamp").is_file()
        or (dist / ".stamp").read_text() != stamp
    ):
        subprocess.run([npm, "--prefix", str(LAB), "run", "build"], check=True)
        (dist / ".stamp").write_text(stamp)
    return dist


def _op_json(op) -> dict:
    d = dataclasses.asdict(op)
    for c in d["changes"]:
        c["class"] = c.pop("cls")
    return d


def derive_cloth_buys(g, ops_json: list[dict], areas: dict | None = None) -> list[dict]:
    """Shipped ops with cloth buys replaced by geometry-derived yards (contract 18).

    Only cloth catalog items on ops that have layup solids change, and only when
    quantities.derived_cloth_buy has every conversion input; everything else keeps
    its authored qty and flag. ``areas`` defaults to quantities.cloth_m2_by_op(g),
    computed only if some buy could be derived. Returns new dicts; input unchanged.
    """
    from guide import quantities
    from guide.schema import Buy

    def candidates(o) -> bool:
        return o["id"] in layup.INCLUDED_OPS and any(
            quantities.can_derive(b["item"]) for b in (o["plan"] or {}).get("buy", [])
        )

    if not any(candidates(o) for o in ops_json):
        return ops_json
    if areas is None:
        areas = quantities.cloth_m2_by_op(g)
    out = []
    for o in ops_json:
        by_cloth = areas.get(o["id"])
        if not by_cloth or not o["plan"]:
            out.append(o)
            continue
        buys = []
        for b in o["plan"].get("buy", ()):
            cloth = quantities.CLOTH_OF_ITEM.get(b["item"])
            if cloth is not None and cloth in by_cloth:
                nb = quantities.derived_cloth_buy(Buy(**b), by_cloth[cloth])
                b = {"item": nb.item, "qty": nb.qty, "flag": nb.flag}
            buys.append(b)
        if buys == list(o["plan"].get("buy", ())):
            out.append(o)
        else:
            out.append({**o, "plan": {**o["plan"], "buy": buys}})
    return out


def _render_docs(docs: Path, out: Path) -> None:
    import markdown

    out.mkdir(parents=True, exist_ok=True)
    items = []
    for md in sorted(
        list((docs / "specs").glob("*build-guide*.md"))
        + list((docs / "plans").glob("*build-guide*.md"))
    ):
        body = markdown.markdown(md.read_text(), extensions=["tables", "fenced_code"])
        (out / f"{md.stem}.html").write_text(
            f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(md.stem)}</title><link rel=stylesheet href='../classic/css/app.css'>"
            f"<main style='display:block;max-width:860px;margin:auto;padding:16px;height:auto'>{body}</main>"
        )
        items.append(f"<li><a href='{md.stem}.html'>{html.escape(md.stem)}</a></li>")
    (out / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>docs</title><ul>"
        + "".join(items)
        + "</ul>"
    )


LEGEND = [
    {"swatch": "und", "text": "UND (unidirectional): light and dark alternate by ply"},
    {"swatch": "bid", "text": "BID (biaxial): light and dark alternate by ply"},
    {"swatch": "foam", "text": "Foam core"},
    {"swatch": "unverified", "text": "Striped: web/spar position not verified"},
    {"swatch": None, "text": "Numbers = lay order"},
    {"swatch": None, "text": "Spar caps: plies as required to fill trough"},
    {
        "swatch": None,
        "text": "Canard planform: GU size from the Owner's Manual; Roncz planform unconfirmed",
    },
    {"swatch": None, "text": "Not to scale"},
]


def _plies(models: Path | None) -> dict:
    lj = models.parent / "layup.json" if models else None
    if not lj or not lj.is_file():
        return {}
    out: dict = {}
    for node, n in json.loads(lj.read_text())["nodes"].items():
        out.setdefault(n["component"], []).append(
            {
                "node": node,
                "op": n["op"],
                "order": n["order"],
                "cloth": n["cloth"],
                "where": n["where"],
                "position_verified": n["position_verified"],
            }
        )
    for rows in out.values():
        rows.sort(key=lambda r: r["order"])
    return out


def _layup(models: Path | None) -> dict | None:
    lj = models.parent / "layup.json" if models else None
    return json.loads(lj.read_text()) if lj and lj.is_file() else None


def _loadpaths(g, models: Path | None) -> list[dict]:
    """Paths always ship; their geometry only when there is a model (it is computed from the layup solids, not the glb)."""
    if not g.loadpaths:
        return []
    if models:
        from guide import (
            loadpaths,
        )  # CadQuery: imported only when there is geometry to compute

        poly = loadpaths.polylines(g)
    else:
        poly = {}
    return [
        {
            "id": lp.id,
            "label": lp.label,
            "kind": lp.kind,
            "parts": list(lp.parts),
            "segments": poly[lp.id]["segments"] if lp.id in poly else [],
        }
        for lp in g.loadpaths
    ]


def _cutaway_export(models: Path) -> Path:
    """The renders were made from the canard-only export beside the site glb (guide.export_glb writes
    <dir>/canard/); an export without that directory is a flat canard export (the M2 layout)."""
    d = models.parent / "canard"
    return d if (d / "longez.glb").is_file() else models.parent


def _cutaway(g, models: Path, renders: Path, out: Path) -> dict:
    exp = _cutaway_export(models)
    if not all((exp / f).is_file() for f in ("layup.json", "shots.json")):
        raise SchemaError(
            "--renders needs layup.json and shots.json next to --models (run guide.export_glb)"
        )
    probs = render_key.check_renders(renders, exp, None)
    if probs:
        raise SchemaError("renders: " + "; ".join(probs))
    pl = layup.plies(g)
    (out / "renders").mkdir()
    shots = json.loads((exp / "shots.json").read_text())
    for s in shots:
        shutil.copy(renders / f"{s['id']}.png", out / "renders" / f"{s['id']}.png")
    src = lambda s: f"renders/{s['id']}.png"  # noqa: E731
    return {
        "ops": {
            s["highlight"]: {"src": src(s), "alt": layup.alt_text(g, pl, s)}
            for s in shots
            if s["kind"] == "op"
        },
        "heroes": [
            {"bl": s["bl"], "src": src(s), "alt": layup.alt_text(g, pl, s)}
            for s in shots
            if s["kind"] == "hero"
        ],
        "legend": LEGEND,
        "count_note": layup.count_note(pl),
    }


def _hangar_payload() -> dict:
    """Spots and decision records for the Hangar index. Records hold no private data, so a public build ships the same file."""
    return {
        "spots": load_spots(),
        "records": {i: dataclasses.asdict(r) for i, r in load_records().items()},
    }


def _plan_payload(g, catalog, resins, today: date, scripts: dict | None = None) -> dict:
    """Shipped plan.json: groups, resins, catalog, scripts and the build date."""
    return {
        "groups": [{"id": grp.id, "label": grp.label} for grp in g.groups],
        "resins": {
            resin_id: {
                "min_temp_c": resin.min_temp_c,
                "gate_hours": [list(pair) for pair in resin.gate_hours],
                "flag": resin.flag,
                "source": resin.source,
            }
            for resin_id, resin in resins.items()
        },
        "catalog": {
            item_id: {
                "label": item.label,
                "url": item.url,
                "price_usd": item.price_usd,
                "unit": item.unit,
                "flag": item.flag,
                "read": None if item.read is None else item.read.isoformat(),
                "stale": is_stale(item, today),
            }
            for item_id, item in catalog.items()
        },
        "scripts": {} if scripts is None else scripts,
        "today": today.isoformat(),
    }


def build(
    graph_dir: Path,
    out: Path,
    models: Path | None,
    scan_base: str | None,
    docs: Path | None,
    renders: Path | None = None,
    public: bool = False,
    *,
    catalog: Path | None = None,
    resins: Path | None = None,
) -> None:
    """public=True: a site safe for a public host. No scan base, no plans figure/page references, no classic viewer, no docs."""
    if public:
        scan_base, docs = None, None
    if renders and not models:
        raise SchemaError(
            "--renders needs --models (the renders are checked against its layup.json/shots.json)"
        )
    g = load_graph(graph_dir)
    errs = validate(g)
    if errs:
        raise SchemaError("; ".join(errs))
    catalog_items = load_catalog(
        DATA / "catalog" / "prices.yaml" if catalog is None else catalog
    )
    resin_curves = load_resins(DATA / "resins" if resins is None else resins)
    scripts = scripts_for(g, load_scripts(graph_dir))
    script_errs = validate_scripts(scripts, g)
    if script_errs:
        raise SchemaError("; ".join(script_errs))
    plan = _plan_payload(g, catalog_items, resin_curves, date.today(), scripts)
    if out.exists():
        shutil.rmtree(out)
    # The lab is the site: its index.html + assets sit at the root beside graph.json, config.json, models/ and docs/.
    # The milestone 2.1 viewer moves to /classic/ for one milestone and reads that shared data from "../".
    shutil.copytree(build_lab(), out, ignore=shutil.ignore_patterns(".stamp"))
    if not public:  # the classic viewer links plans figures and scans (graph.js), so it is not part of a public build
        shutil.copytree(VIEWER, out / "classic", ignore=shutil.ignore_patterns("tests"))
        ci = out / "classic" / "index.html"
        html_in = ci.read_text()
        assert (
            '<meta charset="utf-8">' in html_in
        ), "classic/index.html lost its charset meta; the data-base tag has nowhere to go"
        ci.write_text(
            html_in.replace(
                '<meta charset="utf-8">',
                '<meta charset="utf-8">\n  <meta name="data-base" content="../">',
                1,
            )
        )
    payload = {
        "ops": derive_cloth_buys(g, [_op_json(g.ops[i]) for i in topo_order(g)]),
        "order": topo_order(g),
        "components": {
            c.id: {"label": c.label, "fidelity": c.fidelity}
            for c in g.components.values()
        },
        "pages": {str(k): v for k, v in g.pages.items()},
        "annotations": [dataclasses.asdict(a) for a in g.annotations if a.confirmed],
        "plies": _plies(models),
        "layup": _layup(models),
        "loadpaths": _loadpaths(g, models),
        "tours": g.tours,
        "cutaway": None,
    }
    if public:
        for o in payload["ops"]:
            o["sources"] = [
                {k: v for k, v in s.items() if k in ("doc", "page")}
                for s in o["sources"]
                if s["doc"] != "cobelu"
            ]
        payload["pages"], payload["annotations"] = {}, []
    if renders:
        payload["cutaway"] = _cutaway(g, models, renders, out)
    (out / "graph.json").write_text(json.dumps(payload, indent=1))
    (out / "plan.json").write_text(json.dumps(plan, indent=1))
    (out / "config.json").write_text(
        json.dumps({"scanBase": scan_base, "model": "models/longez.glb"})
    )
    (out / "hangar.json").write_text(
        json.dumps(_hangar_payload(), indent=1, default=str)
    )
    (out / "models").mkdir()
    if models:
        shutil.copy(models, out / "models" / "longez.glb")
        ledger = (
            models.parent / "ledger.json"
        )  # the fuselage mass ledger (guide.export_glb writes it beside layup.json)
        if ledger.is_file():
            shutil.copy(ledger, out / "ledger.json")
    if docs:
        _render_docs(docs, out / "docs")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.build_site")
    ap.add_argument("--graph", type=Path, default=Path("guide/graph"))
    ap.add_argument("--out", type=Path, default=Path("site"))
    ap.add_argument("--models", type=Path, default=None)
    ap.add_argument("--scan-base", default=None)
    ap.add_argument("--renders", type=Path, default=None)
    ap.add_argument(
        "--public",
        action="store_true",
        help="public-safe build: no plans figures/scans/annotations, no classic viewer or docs",
    )
    ap.add_argument("--docs", type=Path, default=Path("docs/superpowers"))
    a = ap.parse_args(argv)
    build(
        a.graph,
        a.out,
        a.models,
        a.scan_base,
        a.docs,
        renders=a.renders,
        public=a.public,
    )
    print(f"built {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
