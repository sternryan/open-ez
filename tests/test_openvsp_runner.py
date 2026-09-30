import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.analysis import OpenVSPRunner  # noqa: E402


@pytest.fixture()
def runner(tmp_path):
    # Write the cache to a throwaway dir so the suite never rewrites tracked files.
    return OpenVSPRunner(cache_dir=tmp_path / "validation")


def test_trim_and_clmax_cached(runner):
    model = runner.build_parametric_model()
    trim, clmax, cache_path = runner.run_validation(model, force_refresh=True)

    assert cache_path.exists()
    cache_data = json.loads(cache_path.read_text())

    assert clmax.cl_max >= 1.2
    assert trim.static_margin >= 0.05
    assert any(point.cl > 0.6 for point in trim.points)

    assert cache_data["model"]["project"] == model["project"]
    assert pytest.approx(cache_data["clmax"]["cl_max"], rel=1e-3) == clmax.cl_max


def test_structural_manifest_hook(runner, tmp_path):
    manifest = runner.export_structural_mesh_manifest(mesh_dir=tmp_path / "meshes")

    assert manifest.mesh_directory.exists()
    assert manifest.mesh_directory.name == "meshes"
    assert "wing" in manifest.surfaces and "canard" in manifest.surfaces

    manifest_file = manifest.mesh_directory / "manifest.json"
    data = json.loads(manifest_file.read_text())
    assert "Populate these paths" in data["notes"]
