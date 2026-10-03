"""Export open-ez components to a single .glb whose node names are guide component IDs."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import cadquery as cq


GRAPH_DIR = Path(__file__).parent / "graph"


def export_components(components: dict, out: Path) -> Path:
    """Top-level keys are component ids. A dict value becomes a sub-assembly named by the component
    id whose children are named by ply node, so the viewer's parent walk resolves every ply. A
    (solid, {ply node: shape}) tuple is the same with the part's own solid on the sub-assembly
    (the fuselage parts: the part and the plies laid on it)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    assy = cq.Assembly(name="longez")
    for cid, v in components.items():
        if isinstance(v, tuple):
            obj, kids = v
            sub = cq.Assembly(obj, name=cid)
            for node, shape in kids.items():
                sub.add(shape, name=node)
            assy.add(sub, name=cid)
        elif isinstance(v, dict):
            sub = cq.Assembly(name=cid)
            for node, shape in v.items():
                sub.add(shape, name=node)
            assy.add(sub, name=cid)
        else:
            assy.add(v, name=cid)
    assy.export(str(out), exportType="GLTF")
    return out


def read_glb_node_names(path: Path) -> list[str]:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError(f"{path}: not a binary glTF")
    chunk_len, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:  # 'JSON'
        raise ValueError(f"{path}: first chunk is not JSON")
    doc = json.loads(data[20 : 20 + chunk_len])
    return [n.get("name", "") for n in doc.get("nodes", [])]


# The Blender cutaway (guide/render_cutaway.sh) renders the canard only, and its contract checks the scene
# spans B.L. 0..semi-span. It gets its own export in this subdirectory of the --out directory, with the
# contract's file names (longez.glb, layup.json, shots.json) and canard content only, so the render key
# moves only when a canard input moves.
CUTAWAY_DIR = "canard"


def canard_components() -> dict:
    from guide.layup_geometry import build_layup
    from guide.schema import load_graph

    return build_layup(load_graph(GRAPH_DIR))


def default_components() -> dict:
    from guide import fuselage_export

    # The lab sorts the glb's nodes into subjects by prefix: canard.* and elevator.* are the canard subject, fuselage.*, gear.* and nose.*
    # the fuselage subject (the canard and elevators are also shown installed on it for chapters 12-13). The canard-only cutaway export
    # (canard_components) stays canard alone.
    return {
        **canard_components(),
        **elevator_components(),
        **fuselage_export.components(),
        **nose_components(),
    }


def elevator_components() -> dict:
    """The Roncz elevator parts (core.elevators_book), one glb component per graph id. In default_components(); not in the canard-only cutaway export."""
    from core.elevators_book import build_elevators

    p = {n: part.solid.val().copy() for n, part in build_elevators().items()}
    out: dict = {
        "elevator.right": p["elevator_right"],
        "elevator.left": p["elevator_left"],
    }
    for cid, key in (
        ("elevator.tube", "elevator_tube"),
        ("elevator.hinges", "hinges"),
        ("elevator.balance_weight", "balance_weight"),
        ("elevator.cs11_weight", "cs11_weight"),
    ):
        out[cid] = {f"{cid}.{side}": p[f"{key}_{side}"] for side in ("right", "left")}
    return out


def nose_components() -> dict:
    """The nose structure and the nose gear (gear down), one glb component per graph id. In default_components(); not in the canard-only
    cutaway export. nose.worm_drive has no geometry and is absent."""
    from core.landing_gear_book import build_nose_gear
    from core.nose_book import COMPONENT_PARTS, build_nose

    parts = {n: p.solid.val().copy() for n, p in build_nose().items()}
    gear = {n: p.solid.val().copy() for n, p in build_nose_gear("plans").items()}
    out: dict = {}
    for cid, names in COMPONENT_PARTS.items():
        out[cid] = (
            parts[names[0]]
            if len(names) == 1
            else {f"{cid}.{n}": parts[n] for n in names}
        )
    out["nose.ng_hardware"] = gear["ng6_block"]
    out["gear.nose_strut"] = {
        f"gear.nose_strut.{n}": gear[n] for n in ("strut", "fork", "wheel")
    }
    return out


def _canard_layup(graph) -> dict:
    from core.structures import CanardGenerator
    from guide import layup

    return layup.layup_json(layup.plies(graph), CanardGenerator().span / 2)


def write_layup_files(graph, out_dir: Path) -> None:
    from core.ledger import fuselage_ledger_json
    from guide import fuselage_export, layup

    lj = _canard_layup(graph)
    lj["fuselage"] = (
        fuselage_export.layup_section()
    )  # chapters 4-6, beside the canard's keys (which are unchanged)
    (out_dir / "layup.json").write_text(json.dumps(lj, indent=1, sort_keys=True))
    (out_dir / "ledger.json").write_text(
        json.dumps(fuselage_ledger_json(), indent=1, sort_keys=True)
    )
    (out_dir / "shots.json").write_text(json.dumps(layup.shots(), indent=1))


def write_cutaway_export(graph, out_dir: Path) -> Path:
    """The canard-only inputs of the Blender cutaway: <out_dir>/canard/{longez.glb, layup.json, shots.json}."""
    from guide import layup

    d = out_dir / CUTAWAY_DIR
    export_components(canard_components(), d / "longez.glb")
    (d / "layup.json").write_text(
        json.dumps(_canard_layup(graph), indent=1, sort_keys=True)
    )
    (d / "shots.json").write_text(json.dumps(layup.shots(), indent=1))
    return d


def main(argv: list[str] | None = None) -> int:
    from guide.schema import load_graph

    ap = argparse.ArgumentParser(prog="guide.export_glb")
    ap.add_argument("--out", default="output/guide/longez.glb")
    a = ap.parse_args(argv)
    out = export_components(default_components(), Path(a.out))
    g = load_graph(GRAPH_DIR)
    write_layup_files(g, out.parent)
    cut = write_cutaway_export(g, out.parent)
    print(
        f"wrote {out} (+ layup.json, ledger.json, shots.json) nodes={len(read_glb_node_names(out))}; "
        f"cutaway inputs (canard only) in {cut}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
