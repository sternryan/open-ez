"""VSPAERO NP leg: runs where OpenVSP exists, FAILS (not skips) where it is required but absent.

Where it runs:
- VSP_RUNNER set and executable (a remote job runner script): through the cpu-job payload,
  so the lane venv never needs the bindings.
- else an interpreter that imports openvsp (the laptop under python3.13): in-process subprocess.
- OPENEZ_REQUIRE_VSPAERO=1 turns "neither available" into a failure instead of a skip.
"""

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
COMMITTED = REPO / "data" / "validation" / "vspaero_np.json"
REQUIRED = os.environ.get("OPENEZ_REQUIRE_VSPAERO") == "1"
RUNNER = os.environ.get("VSP_RUNNER")
JOB_ROOT = Path(os.environ.get("VSP_JOB_ROOT", "/srv/cpu-jobs/vsp"))

try:
    import openvsp  # noqa: F401

    HAS = True
except ImportError:
    HAS = False
RUNNER_OK = bool(RUNNER and Path(RUNNER).exists())
AVAILABLE = HAS or RUNNER_OK


def test_require_flag_turns_skip_into_failure():
    if REQUIRED and not AVAILABLE:
        pytest.fail(
            "OPENEZ_REQUIRE_VSPAERO=1 but neither openvsp nor VSP_RUNNER is usable: "
            "the VSPAERO leg did not run"
        )
    if not AVAILABLE:
        pytest.skip("openvsp absent and not required")


def _run_np(tmp_path):
    if RUNNER_OK:
        job = JOB_ROOT / f"oez-{uuid.uuid4().hex[:12]}"
        (job / "in").mkdir(parents=True)
        try:
            # vsp.sh runs the entry as `python entry <job_dir>`: argv[1] is the job dir. The shim
            # points the real script at <job>/out/np.json so the repo baseline is never touched.
            (job / "in" / "np_leg.py").write_text(
                "import runpy, sys\n"
                f"script = {str(REPO / 'scripts' / 'vspaero_np.py')!r}\n"
                "sys.argv = [script, '--out', sys.argv[1] + '/out/np.json']\n"
                "runpy.run_path(script, run_name='__main__')\n"
            )
            r = subprocess.run(
                [RUNNER, "np_leg.py", str(job)],
                capture_output=True,
                text=True,
                timeout=3900,
            )
            assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
            assert r.stdout.strip().endswith("VSP_JOB_RESULT rc=0")
            return json.loads((job / "out" / "np.json").read_text())
        finally:
            shutil.rmtree(job, ignore_errors=True)
    out_path = tmp_path / "np.json"
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "vspaero_np.py"),
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return json.loads(out_path.read_text())


@pytest.mark.skipif(
    not (AVAILABLE or REQUIRED), reason="openvsp absent and not required"
)
def test_np_leg_reproduces_committed(tmp_path):
    if (
        not AVAILABLE
    ):  # REQUIRED and absent: say so, rather than a bare subprocess failure
        pytest.fail(
            "OPENEZ_REQUIRE_VSPAERO=1 but no OpenVSP is usable: the VSPAERO leg did not run"
        )
    before = COMMITTED.read_bytes()
    got = _run_np(tmp_path)
    assert COMMITTED.read_bytes() == before, "the run overwrote the committed baseline"
    ref = json.loads(before)
    assert (
        got["geometry"] == ref["geometry"]
    ), "geometry drifted: regenerate the laptop baseline first"
    assert got["vsp_version"] == ref["vsp_version"], (
        got["vsp_version"],
        ref["vsp_version"],
    )
    assert abs(got["np_fs"] - ref["np_fs"]) < 0.01, (got["np_fs"], ref["np_fs"])
    assert len(got["sweep"]) == len(ref["sweep"])
