"""Export open-ez components to a single .glb whose node names are guide component IDs."""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import cadquery as cq


def export_components(components: dict[str, cq.Workplane], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    assy = cq.Assembly(name="longez")
    for cid, wp in components.items():
        assy.add(wp, name=cid)
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


def default_components() -> dict[str, cq.Workplane]:
    from core.structures import CanardGenerator

    return {"canard.core": CanardGenerator().generate_geometry()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.export_glb")
    ap.add_argument("--out", default="output/guide/longez.glb")
    a = ap.parse_args(argv)
    out = export_components(default_components(), Path(a.out))
    print(f"wrote {out} nodes={read_glb_node_names(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
