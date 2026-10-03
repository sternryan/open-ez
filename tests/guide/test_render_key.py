import json
from pathlib import Path

from guide import render_key as rk

SCRIPTS = ("layup_cutaway.py", "fabric_blender.py", "layup_contract.py")


def make_export(d: Path, shots=None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "longez.glb").write_bytes(b"glTF-x")
    (d / "layup.json").write_text('{"nodes":{}}')
    (d / "shots.json").write_text(
        json.dumps(shots or [{"id": "hero-bl5"}, {"id": "op-r30-top-skin"}])
    )
    return d


def make_scripts(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    for s in SCRIPTS:
        (d / s).write_text(f"# {s}\n")
    return d


def make_renders(d: Path, export: Path, scripts: Path, drop: str | None = None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    shots = {}
    for s in json.loads((export / "shots.json").read_text()):
        if s["id"] == drop:
            continue
        (d / f"{s['id']}.png").write_bytes(s["id"].encode())
        shots[s["id"]] = {
            "file": f"{s['id']}.png",
            "sha256": rk.sha256(d / f"{s['id']}.png"),
        }
    (d / "manifest.json").write_text(
        json.dumps({"inputs": rk.file_shas(export, scripts), "shots": shots})
    )
    return d


def test_key_changes_with_any_input(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    k1 = rk.key_of(rk.file_shas(e, s))
    (s / "layup_cutaway.py").write_text("# changed\n")
    assert rk.key_of(rk.file_shas(e, s)) != k1
    (e / "shots.json").write_text("[]")
    assert len(rk.key_of(rk.file_shas(e, s))) == 64


def test_check_ok(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    assert rk.check_renders(make_renders(tmp_path / "r", e, s), e, s) == []


def test_check_missing_shot_and_stale_data(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    r = make_renders(tmp_path / "r", e, s, drop="op-r30-top-skin")
    assert any("op-r30-top-skin" in p for p in rk.check_renders(r, e, s))
    r2 = make_renders(tmp_path / "r2", e, s)
    (e / "layup.json").write_text('{"nodes":{"x":{}}}')
    assert any("layup.json" in p for p in rk.check_renders(r2, e, s))


def test_check_without_scripts_still_requires_script_shas(tmp_path):
    e, s = make_export(tmp_path / "e"), make_scripts(tmp_path / "s")
    r = make_renders(tmp_path / "r", e, s)
    m = json.loads((r / "manifest.json").read_text())
    del m["inputs"]["fabric_blender.py"]
    (r / "manifest.json").write_text(json.dumps(m))
    assert any("fabric_blender.py" in p for p in rk.check_renders(r, e, None))


def test_check_missing_manifest(tmp_path):
    e = make_export(tmp_path / "e")
    (tmp_path / "r").mkdir()
    assert rk.check_renders(tmp_path / "r", e, None) == [
        "no manifest.json (incomplete render run)"
    ]
