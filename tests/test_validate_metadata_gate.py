"""Broken-input tests for the artifact metadata gate (scripts/validate_metadata.py)."""

from __future__ import annotations

import json
import sys

import pytest

from core.metadata import REQUIRED_FIELDS
from scripts import validate_metadata as vm

ARTIFACT = "part.stl"


def _good_payload() -> dict:
    payload = {field: "x" for field in REQUIRED_FIELDS}
    payload["artifact"] = ARTIFACT
    return payload


def _write(tmp_path, payload=None, raw=None):
    (tmp_path / ARTIFACT).write_bytes(b"solid")
    meta = tmp_path / "part.metadata.json"
    meta.write_text(raw if raw is not None else json.dumps(payload))
    return tmp_path / ARTIFACT


def _run_main(monkeypatch, out_dir) -> int:
    monkeypatch.setattr(sys, "argv", ["validate_metadata", "--output", str(out_dir)])
    return vm.main()


def test_good_metadata_is_accepted(tmp_path, monkeypatch):
    art = _write(tmp_path, _good_payload())
    assert vm.validate_metadata_file(art) == (True, "")
    assert _run_main(monkeypatch, tmp_path) == 0


def test_missing_metadata_file_is_rejected(tmp_path, monkeypatch, capsys):
    (tmp_path / ARTIFACT).write_bytes(b"solid")
    ok, reason = vm.validate_metadata_file(tmp_path / ARTIFACT)
    assert not ok and "Missing metadata" in reason
    assert _run_main(monkeypatch, tmp_path) == 1
    assert "METADATA VALIDATION FAILED" in capsys.readouterr().out


def test_invalid_json_is_rejected(tmp_path, monkeypatch):
    art = _write(tmp_path, raw="{not json")
    ok, reason = vm.validate_metadata_file(art)
    assert not ok and "Invalid JSON" in reason
    assert _run_main(monkeypatch, tmp_path) == 1


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected(tmp_path, monkeypatch, field):
    payload = _good_payload()
    del payload[field]
    art = _write(tmp_path, payload)
    ok, reason = vm.validate_metadata_file(art)
    assert not ok and field in reason
    assert _run_main(monkeypatch, tmp_path) == 1


@pytest.mark.parametrize("key", ["revision", "config_hash", "contributor"])
@pytest.mark.parametrize("value", ["", "   "])
def test_empty_provenance_field_is_rejected(tmp_path, monkeypatch, key, value):
    payload = _good_payload()
    payload[key] = value
    art = _write(tmp_path, payload)
    ok, reason = vm.validate_metadata_file(art)
    assert not ok and key in reason
    assert _run_main(monkeypatch, tmp_path) == 1


def test_artifact_name_mismatch_is_rejected(tmp_path, monkeypatch):
    payload = _good_payload()
    payload["artifact"] = "other.stl"
    art = _write(tmp_path, payload)
    ok, reason = vm.validate_metadata_file(art)
    assert not ok and "mismatch" in reason
    assert _run_main(monkeypatch, tmp_path) == 1


def test_one_bad_artifact_fails_the_whole_run(tmp_path, monkeypatch, capsys):
    good = tmp_path / "good"
    good.mkdir()
    _write(good, _good_payload())
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "orphan.dxf").write_text("0")
    assert _run_main(monkeypatch, tmp_path) == 1
    assert "orphan.dxf" in capsys.readouterr().out


def test_ci_wrapper_fails_when_metadata_gate_fails(tmp_path, monkeypatch):
    from scripts import run_ci_checks

    (tmp_path / ARTIFACT).write_bytes(b"solid")
    monkeypatch.setattr(sys, "argv", ["run_ci_checks", "--output", str(tmp_path)])
    monkeypatch.setattr(run_ci_checks, "run_config_validation", lambda: 0)
    assert run_ci_checks.main() == 1
