"""The vendored fabric-task client (vendor/fabric_task_client, v1.0.0) and the request builder."""

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "vendor"))

from fabric_task_client import validate_request, validate_result

FIX = ROOT / "vendor" / "fabric_task_client" / "fixtures"


def _load(name):
    return json.loads((FIX / name).read_text())


def test_vendored_file_matches_release_digest():
    rel = json.loads((ROOT / "vendor/fabric_task_client/RELEASE.json").read_text())
    for rel_path, sha in rel["files"].items():
        got = hashlib.sha256((ROOT / "vendor" / rel_path).read_bytes()).hexdigest()
        assert got == sha


@pytest.mark.parametrize("path", sorted(FIX.glob("valid-*.json")), ids=lambda p: p.name)
def test_valid_requests_pass(path):
    validate_request(json.loads(path.read_text()))


@pytest.mark.parametrize(
    "path", sorted(FIX.glob("invalid-*.json")), ids=lambda p: p.name
)
def test_invalid_requests_rejected(path):
    with pytest.raises(ValueError):
        validate_request(json.loads(path.read_text()))


@pytest.mark.parametrize(
    "path", sorted(FIX.glob("result-valid-*.json")), ids=lambda p: p.name
)
def test_valid_results_pass(path):
    validate_result(json.loads(path.read_text()))


@pytest.mark.parametrize(
    "path", sorted(FIX.glob("result-invalid-*.json")), ids=lambda p: p.name
)
def test_invalid_results_rejected(path):
    with pytest.raises(ValueError):
        validate_result(json.loads(path.read_text()))


@pytest.mark.parametrize(
    "bad_name",
    [
        "hear" + "th",  # a fleet node name
        "100." + "85.83.97",  # an address
    ],
)
def test_result_names_must_be_opaque(bad_name):
    # Built here, not vendored as fixtures: the repo keeps node names and addresses out of tracked files.
    result = copy.deepcopy(_load("result-valid-succeeded.json"))
    result["execution"]["validation"][0]["name"] = bad_name
    with pytest.raises(ValueError):
        validate_result(result)


def test_fabric_request_validates():
    sys.path.insert(0, str(ROOT / "scripts"))
    import fabric_request

    request, records, _ = fabric_request.build(
        "fast", fabric_request.IMPLEMENTATION_SHA256, allow_dirty=True
    )
    validate_request(request)
    assert request["parameters"]["suite"] == "fast"
    assert all(not r["path"].startswith("private/") for r in records)
    assert any(r["path"] == "fabric/suites.json" for r in records)
