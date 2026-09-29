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
    id whose children are named by ply node, so the viewer's parent walk resolves every ply."""
    out.parent.mkdir(parents=True, exist_ok=True)
    assy = cq.Assembly(name="longez")
    for cid, v in components.items():
        if isinstance(v, dict):
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


def default_components() -> dict:
    from guide.layup_geometry import build_layup
    from guide.schema import load_graph

    return build_layup(load_graph(GRAPH_DIR))


def write_layup_files(graph, out_dir: Path) -> None:
    from core.structures import CanardGenerator
    from guide import layup

    pl = layup.plies(graph)
    lj = layup.layup_json(pl, CanardGenerator().span / 2)
    (out_dir / "layup.json").write_text(json.dumps(lj, indent=1, sort_keys=True))
    (out_dir / "shots.json").write_text(json.dumps(layup.shots(), indent=1))


def main(argv: list[str] | None = None) -> int:
    from guide.schema import load_graph

    ap = argparse.ArgumentParser(prog="guide.export_glb")
    ap.add_argument("--out", default="output/guide/longez.glb")
    a = ap.parse_args(argv)
    out = export_components(default_components(), Path(a.out))
    write_layup_files(load_graph(GRAPH_DIR), out.parent)
    print(f"wrote {out} (+ layup.json, shots.json) nodes={len(read_glb_node_names(out))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
