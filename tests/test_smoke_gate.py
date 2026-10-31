"""The CI smoke test must fail when the configuration does not validate."""

import pytest

from scripts import smoke_test

BROKEN = ["canard airfoil changed", "fs_tail precedes fs_nose"]


def test_validate_configuration_rejects_config_errors(monkeypatch):
    monkeypatch.setattr(smoke_test.config, "validate", lambda: list(BROKEN))
    with pytest.raises(RuntimeError, match="canard airfoil changed"):
        smoke_test._validate_configuration()


def test_main_exits_nonzero_on_config_errors(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(smoke_test.config, "validate", lambda: list(BROKEN))
    monkeypatch.setattr(
        "sys.argv", ["smoke_test.py", "--fast", "--artifacts-dir", str(tmp_path)]
    )
    assert smoke_test.main() == 1
    assert "Configuration validation failed" in capsys.readouterr().out
