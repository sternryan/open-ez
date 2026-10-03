"""Render key: which inputs produced a set of cutaway renders, and are those renders complete?

key = sha256 over sorted "name sha256" lines of the data files (longez.glb, layup.json, shots.json)
and the Blender scripts. The laptop computes it; the Blender job records per-file shas in manifest.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DATA = ("longez.glb", "layup.json", "shots.json")
SCRIPTS = ("layup_cutaway.py", "fabric_blender.py", "layup_contract.py")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def file_shas(export_dir: Path, scripts_dir: Path | None) -> dict[str, str]:
    shas = {f: sha256(export_dir / f) for f in DATA}
    if scripts_dir is not None:
        shas.update({f: sha256(scripts_dir / f) for f in SCRIPTS})
    return shas


def key_of(shas: dict[str, str]) -> str:
    return hashlib.sha256(
        "".join(f"{k} {shas[k]}\n" for k in sorted(shas)).encode()
    ).hexdigest()


def check_renders(
    renders: Path, export_dir: Path, scripts_dir: Path | None = None
) -> list[str]:
    mf = renders / "manifest.json"
    if not mf.is_file():
        return ["no manifest.json (incomplete render run)"]
    m = json.loads(mf.read_text())
    inputs, probs = m.get("inputs", {}), []
    for name, sha in file_shas(export_dir, scripts_dir).items():
        if inputs.get(name) != sha:
            probs.append(f"{name} changed since these renders (stale)")
    probs += [f"manifest lacks the {s} sha" for s in SCRIPTS if s not in inputs]
    for shot in json.loads((export_dir / "shots.json").read_text()):
        rec = m.get("shots", {}).get(shot["id"])
        png = renders / f"{shot['id']}.png"
        if rec is None or not png.is_file():
            probs.append(f"missing render for shot {shot['id']}")
        elif sha256(png) != rec["sha256"]:
            probs.append(f"render {shot['id']} does not match its manifest sha")
    return probs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="guide.render_key")
    ap.add_argument("--export", type=Path, required=True)
    ap.add_argument("--scripts", type=Path, default=None)
    ap.add_argument("--check", type=Path, default=None, metavar="RENDERS")
    a = ap.parse_args(argv)
    if a.check:
        probs = check_renders(a.check, a.export, a.scripts)
        for p in probs:
            print(p, file=sys.stderr)
        return 1 if probs else 0
    print(key_of(file_shas(a.export, a.scripts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
