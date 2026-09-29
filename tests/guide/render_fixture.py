"""A small but real export dir + renders dir that pass render_key.check_renders."""
import json
from pathlib import Path

import cadquery as cq

from guide import layup, render_key as rk
from guide.export_glb import export_components
from guide.schema import load_graph

ROOT = Path(__file__).resolve().parents[2]

PNG_1PX = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                        "1f15c4890000000d49444154789c6360f80f0000010100005a4d6e2e0000000049454e44ae426082")


def make_export(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    g = load_graph(ROOT / "guide" / "graph")
    pl = layup.plies(g)
    comps = {"canard.core": cq.Workplane().box(10, 2, 1)}
    for i, p in enumerate(pl):
        comps.setdefault(p.component, {})[p.node] = cq.Workplane().box(1, 1, 1).translate((i * 1.5, 0, 2))
    export_components(comps, d / "longez.glb")
    (d / "layup.json").write_text(json.dumps(layup.layup_json(pl, 63.0)))
    (d / "shots.json").write_text(json.dumps(layup.shots()))
    return d


def make_renders(d: Path, export: Path, drop: str | None = None, bad_png: str | None = None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    shots = {}
    for s in layup.shots():
        if s["id"] == drop:
            continue
        p = d / f"{s['id']}.png"; p.write_bytes(PNG_1PX)
        shots[s["id"]] = {"file": p.name, "sha256": rk.sha256(p)}
        if s["id"] == bad_png:
            p.write_bytes(b"not a png")  # manifest sha no longer matches
    inputs = rk.file_shas(export, None) | {s: "0" * 64 for s in rk.SCRIPTS}
    (d / "manifest.json").write_text(json.dumps({"inputs": inputs, "shots": shots}))
    return d
