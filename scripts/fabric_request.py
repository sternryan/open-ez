#!/usr/bin/env python3
"""Build a fabric-task request for the cpu-test profile from the committed tree.

usage: python scripts/fabric_request.py [--suite fast|full] [--out out/fabric-requests] [--allow-dirty]

Writes <out>/<request_id>/request.json and bundle-manifest.json. Submission is an operator action;
this script only produces the files, after the public leakcheck and the vendored client's validator.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))

from fabric_task_client import validate_request

from guide.leakcheck import leaks

# From the cpu-test profile release; a new profile release changes it. Override with --impl.
IMPLEMENTATION_SHA256 = (
    "dc9951939c5bb583255dbcf71b73d85d343d0d5d6805f87f399537328cfac6ce"
)
ENV_LOCK_FILES = (
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-guide-dev.txt",
    "guide/lab/package.json",
    "guide/lab/package-lock.json",
)
SUITES = "fabric/suites.json"


# guide.leakcheck guards the published site. Applied to the source tree, its plans-reference and
# legal-wording patterns match design docs and graph YAML that are tracked on purpose, so the bundle
# gate keeps only the categories that mean "node names, addresses, scans or private files".
_BUNDLE_LEAK_KINDS = (
    "tailnet hostname",
    "tailnet IP",
    "image/scan file type",
    "private/ directory",
)


def _is_bundle_leak(finding: str) -> bool:
    return any(kind in finding for kind in _BUNDLE_LEAK_KINDS)


def _git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, check=True
    ).stdout


def bundle_files() -> list[str]:
    names = _git("ls-files", "-z").decode().split("\0")
    return sorted(
        f
        for f in names
        if f
        and not f.startswith("private/")
        and (ROOT / f).is_file()
        and not (ROOT / f).is_symlink()
    )


def env_lock_sha256() -> str:
    h = hashlib.sha256()
    for f in ENV_LOCK_FILES:
        h.update(
            f.encode()
            + b"\0"
            + hashlib.sha256((ROOT / f).read_bytes()).hexdigest().encode()
            + b"\n"
        )
    return h.hexdigest()


def build(
    suite: str, impl: str, allow_dirty: bool = False
) -> tuple[dict, list[dict], list[str]]:
    """Return (request, bundle records, leak findings)."""
    if (
        not allow_dirty
        and _git("status", "--porcelain", "--untracked-files=no").strip()
    ):
        raise SystemExit(
            "tracked files are modified: commit first, or pass --allow-dirty"
        )
    files = bundle_files()
    if SUITES not in files:
        raise SystemExit(f"{SUITES} is not tracked")
    records = []
    for f in files:
        data = (ROOT / f).read_bytes()
        records.append(
            {"path": f, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        )
    digest = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    suites = json.loads((ROOT / SUITES).read_text())
    if suite not in suites["suites"]:
        raise SystemExit(f"unknown suite {suite!r}; have {sorted(suites['suites'])}")
    request = {
        "schema_version": "fabric-task-request-v1",
        "request_id": str(uuid.uuid4()),
        "consumer": "open-ez",
        "source": {
            "revision": _git("rev-parse", "HEAD").decode().strip(),
            "bundle_sha256": digest,
        },
        "profile": {"id": "cpu-test", "version": "1", "implementation_sha256": impl},
        "inputs": [
            {
                "name": "source",
                "artifact_ref": "approved://open-ez/source",
                "sha256": digest,
                "bytes": sum(r["bytes"] for r in records),
            }
        ],
        "parameters": {
            "suite": suite,
            "suite_manifest_sha256": hashlib.sha256(
                (ROOT / SUITES).read_bytes()
            ).hexdigest(),
            "env_lock_sha256": env_lock_sha256(),
        },
        "requirements": {
            "capabilities": ["cpu.python"],
            "privacy": "public-only",
            "network": "none",
            "paid_access": False,
        },
        "limits": {
            "wall_ms": 2700000,
            "artifact_bytes": 67108864,
            "usd_micros": 0,
            "model_tokens": 0,
            "attempts": 1,
        },
        "outputs": ["junit", "collection-manifest", "execution-manifest"],
    }
    found: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            dest = Path(tmp) / f
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / f, dest)
        found = [f for f in leaks(Path(tmp)) if _is_bundle_leak(f)]
    return request, records, found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suite", default="fast")
    ap.add_argument("--out", default=str(ROOT / "out" / "fabric-requests"))
    ap.add_argument("--impl", default=IMPLEMENTATION_SHA256)
    ap.add_argument("--allow-dirty", action="store_true")
    a = ap.parse_args(argv)
    request, records, found = build(a.suite, a.impl, a.allow_dirty)
    if found:
        for f in found:
            print("LEAK", f, file=sys.stderr)
        return 1
    validate_request(request)
    dest = Path(a.out) / request["request_id"]
    dest.mkdir(parents=True)
    (dest / "request.json").write_text(json.dumps(request, indent=1) + "\n")
    (dest / "bundle-manifest.json").write_text(json.dumps(records))
    print(
        json.dumps(
            {
                "request_dir": str(dest),
                "files": len(records),
                "bundle": request["source"]["bundle_sha256"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
