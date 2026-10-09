"""build_lab() in a sealed fabric environment (FABRIC_SEALED_ENV=1): accept a stamped node_modules, never run npm ci."""
import subprocess

import pytest

from guide import build_site


@pytest.fixture
def lab(tmp_path, monkeypatch):
    root = tmp_path / "lab"
    (root / "dist").mkdir(parents=True)
    (root / "package-lock.json").write_text("{}")
    (root / "src").mkdir()
    monkeypatch.setattr(build_site, "LAB", root)
    monkeypatch.setattr(build_site.shutil, "which", lambda name: "/usr/bin/npm")
    calls = []
    monkeypatch.setattr(build_site.subprocess, "run", lambda *a, **k: calls.append(a[0]) or subprocess.CompletedProcess(a[0], 0))
    return root, calls


def test_sealed_env_with_a_matching_stamp_runs_no_npm_ci(lab, monkeypatch):
    root, calls = lab
    monkeypatch.setenv("FABRIC_SEALED_ENV", "1")
    (root / "node_modules").mkdir()
    (root / "node_modules" / ".lock-stamp").write_text(build_site._digest([root / "package-lock.json"]))
    (root / "dist" / "index.html").write_text("x")
    (root / "dist" / ".stamp").write_text(build_site._lab_stamp())
    build_site.build_lab()
    assert calls == []


@pytest.mark.parametrize("state", ["missing", "stale"])
def test_sealed_env_without_a_valid_node_modules_fails_loudly_and_never_calls_npm(lab, monkeypatch, state):
    root, calls = lab
    monkeypatch.setenv("FABRIC_SEALED_ENV", "1")
    if state == "stale":
        (root / "node_modules").mkdir()
        (root / "node_modules" / ".lock-stamp").write_text("stale")
    with pytest.raises(RuntimeError, match="sealed environment"):
        build_site.build_lab()
    assert calls == []


def test_unsealed_env_still_runs_npm_ci_as_before(lab, monkeypatch):
    root, calls = lab
    monkeypatch.delenv("FABRIC_SEALED_ENV", raising=False)
    (root / "node_modules").mkdir()
    build_site.build_lab()
    assert any("ci" in call for call in calls)
