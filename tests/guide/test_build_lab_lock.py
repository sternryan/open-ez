"""build_lab() under parallel callers (pytest -n): one npm ci and one build, never two at once."""
import subprocess
import threading
import time

from guide import build_site


def test_parallel_build_lab_runs_npm_once_and_never_concurrently(tmp_path, monkeypatch):
    root = tmp_path / "lab"
    (root / "src").mkdir(parents=True)
    (root / "package-lock.json").write_text("{}")
    monkeypatch.setattr(build_site, "LAB", root)
    monkeypatch.setattr(build_site.shutil, "which", lambda name: "/usr/bin/npm")
    monkeypatch.delenv("FABRIC_SEALED_ENV", raising=False)
    calls, active, peak, guard = [], [0], [0], threading.Lock()

    def fake_run(cmd, **kw):
        with guard:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
            calls.append(cmd[-1])
        time.sleep(0.05)
        if cmd[-1] == "ci":
            (root / "node_modules").mkdir(exist_ok=True)
        else:
            (root / "dist").mkdir(exist_ok=True)
            (root / "dist" / "index.html").write_text("x")
        with guard:
            active[0] -= 1
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(build_site.subprocess, "run", fake_run)
    threads = [threading.Thread(target=build_site.build_lab) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert peak[0] == 1
    assert calls == ["ci", "build"]
