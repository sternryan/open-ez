"""Hangar index payload written beside the built site."""

from __future__ import annotations

import json

import pytest

import guide.leakcheck
from guide.build_site import build
from hangar.records import load_records, load_spots
from tests.guide.test_schema import gdir as _schema_gdir

_graph_dir = pytest.fixture(name="gdir")(_schema_gdir.__wrapped__)


def test_hangar_json(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base=None, docs=None, public=True)
    data = json.loads((out / "hangar.json").read_text())
    loaded = load_records()
    assert len(data["spots"]) == 4
    assert data["spots"] == load_spots()
    assert list(data["records"]) == list(loaded)
    assert "powerplant-fuel-resin" in data["records"]
    assert guide.leakcheck.main([str(out)]) == 0
