"""render_cutaway.sh with stub ssh/rsync/fabric-gpu on PATH: every branch, no GPU, no anvil."""

import os
import re
import stat
import subprocess
from pathlib import Path

import pytest

from guide import render_key as rk
from tests.guide.test_render_key import make_export, make_renders, make_scripts

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "guide" / "render_cutaway.sh"
STUB_SSH = r"""#!/bin/bash
host="$1"; shift; cmd="$*"; echo "ssh $cmd" >> "$STUB_LOG"
case "$cmd" in
  flux-lock-status) if [ "${STUB_LEASE:-0}" = 3 ]; then
      printf 'HELD  — a flux job holds the anvil GPU lock:\n  holder| pid=42\n  holder| runner=w9-battery\n  holder| started=2026-09-29T18:11:58+00:00\n'
      [ -n "${STUB_ETA:-}" ] && printf '  holder| eta=%s\n' "$STUB_ETA"; exit 3; fi; echo "FREE"; exit 0;;
  sha256sum*) f="${cmd##*/}"; if [ -n "${STUB_SHA_BAD:-}" ]; then echo "0000  x"; else shasum -a 256 "$STUB_SCRIPTS/$f"; fi;;
  "test -f"*) exit 0;;
  *) exit 0;;
esac
"""
STUB_RSYNC = r"""#!/bin/bash
echo "rsync $*" >> "$STUB_LOG"
src="${@: -2:1}"; dst="${@: -1}"
case "$src" in *:*/out/) cp -R "$STUB_OUT"/. "$dst";; esac
"""
STUB_GPU = r"""#!/bin/bash
printf '%s\n' "$@" > "$STUB_GPU_ARGS"; exit "${STUB_GPU_RC:-0}"
"""


def exe(p: Path, body: str) -> None:
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IEXEC)


@pytest.fixture
def env(tmp_path):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    exe(bin_ / "ssh", STUB_SSH)
    exe(bin_ / "rsync", STUB_RSYNC)
    exe(bin_ / "fabric-gpu", STUB_GPU)
    cf = tmp_path / "cf"
    scripts = make_scripts(cf / "deploy/anvil/jobs/blender")
    export = make_export(tmp_path / "export")
    out = make_renders(tmp_path / "anvil_out", export, scripts)
    e = dict(
        os.environ,
        PATH=f"{bin_}:{os.environ['PATH']}",
        COMPUTE_FABRIC_DIR=str(cf),
        FABRIC_GPU=str(bin_ / "fabric-gpu"),
        LONGEZ_EXPORT_DIR=str(export),
        LONGEZ_RENDER_CACHE=str(tmp_path / "cache"),
        LONGEZ_POLL_S="0",
        PY=str(ROOT / ".venv" / "bin" / "python"),
        STUB_LOG=str(tmp_path / "log"),
        STUB_SCRIPTS=str(scripts),
        STUB_OUT=str(out),
        STUB_GPU_ARGS=str(tmp_path / "gpu_args"),
    )
    return e, tmp_path, export, scripts


def run(e, *args, **extra):
    return subprocess.run(
        ["bash", str(SH), *args], env={**e, **extra}, capture_output=True, text=True
    )


def test_lease_busy_stops_before_dispatch(env):
    e, t, *_ = env
    r = run(e, STUB_LEASE="3")
    assert r.returncode == 3
    assert "GPU lease held by w9-battery since 2026-09-29T18:11:58" in r.stderr
    assert "ETA: none stamped by the holder" in r.stderr and "--wait" in r.stderr
    assert not (t / "gpu_args").exists()


def test_lease_busy_reports_stamped_eta(env):
    e, t, *_ = env
    r = run(e, STUB_LEASE="3", STUB_ETA="2026-09-29T19:30:00Z")
    assert r.returncode == 3 and "ETA: 2026-09-29T19:30:00Z" in r.stderr


def test_wait_queues_through_fabric_gpu(env):
    e, t, *_ = env
    r = run(e, "--wait=600", STUB_LEASE="3")
    assert r.returncode == 0, r.stderr
    args = (t / "gpu_args").read_text().split()
    assert "--no-wait" not in args and args[args.index("--wait-s") + 1] == "600"
    assert "queuing behind w9-battery" in r.stderr


def test_wait_default_is_four_hours(env):
    e, t, *_ = env
    assert run(e, "--wait").returncode == 0
    args = (t / "gpu_args").read_text().split()
    assert args[args.index("--wait-s") + 1] == "14400"


def test_happy_path(env):
    e, t, export, scripts = env
    r = run(e)
    assert r.returncode == 0, r.stderr
    args = (t / "gpu_args").read_text().split()
    key = rk.key_of(rk.file_shas(export, scripts))
    assert args[:3] == ["run", "blender.sh", "layup_cutaway"] and re.fullmatch(
        r"[a-z0-9_]+", args[2]
    )
    assert args[3].endswith(f"layup-{key[:16]}") and args[4:6] == [
        "--no-wait",
        "--expect-s",
    ]  # no --wait: refuse, don't queue
    assert (t / "cache" / key / "manifest.json").exists() and not (
        t / "cache" / f"{key}.tmp"
    ).exists()


def test_gpu_failure_leaves_no_cache(env):
    e, t, *_ = env
    r = run(e, STUB_GPU_RC="1")
    assert r.returncode == 1
    assert not (t / "cache").exists() or not any((t / "cache").iterdir())


def test_deployed_script_mismatch(env):
    e, t, *_ = env
    r = run(e, STUB_SHA_BAD="1")
    assert (
        r.returncode == 4 and "redeploy" in r.stderr and not (t / "gpu_args").exists()
    )


def test_only_filters_shots_and_changes_key(env):
    e, t, export, scripts = env
    r = run(e, "--only", "hero-bl5", "--dry-run")
    assert r.returncode == 0 and "would render" in r.stdout
    assert rk.key_of(rk.file_shas(export, scripts)) not in r.stdout
    assert run(e, "--only", "nope", "--dry-run").returncode == 2


def test_incomplete_renders_fail_check(env, tmp_path):
    e, t, export, scripts = env
    bad = make_renders(tmp_path / "bad_out", export, scripts, drop="hero-bl5")
    r = run(e, STUB_OUT=str(bad))
    assert r.returncode == 5 and "hero-bl5" in r.stderr
    key = rk.key_of(rk.file_shas(export, scripts))
    assert not (t / "cache" / key).exists()


def test_stale_tmp_is_replaced(env):  # Review Focus 5
    e, t, export, scripts = env
    key = rk.key_of(rk.file_shas(export, scripts))
    (t / "cache" / f"{key}.tmp").mkdir(parents=True)
    (t / "cache" / f"{key}.tmp" / "junk.png").write_bytes(b"x")
    assert run(e).returncode == 0
    assert not (t / "cache" / key / "junk.png").exists()
