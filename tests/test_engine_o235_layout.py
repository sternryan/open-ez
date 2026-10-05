"""The O-235 layout is frozen and hashed (ledger row 70) before any CG code exists."""

import re
from pathlib import Path

import pytest

import core.engine_o235_book as L

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "geometry-correction-ledger.md"
NAMES = sorted(n for n in vars(L) if n.startswith(("FITTED_", "DENSITY_")))


def _row70() -> str:
    for line in LEDGER.read_text().splitlines():
        if re.match(r"^\| 70 \|", line):
            return line
    return ""


def test_the_layout_hash_is_recorded_in_ledger_row_70():
    row = _row70()
    assert row, "ledger row 70 is missing"
    assert L.layout_sha256() in row


def _mutate(v):
    if isinstance(v, dict):
        out = dict(v)
        k = sorted(out)[0]
        out[k] = out[k] + "_x"
        return out
    if isinstance(v, tuple):
        return (_mutate(v[0]),) + v[1:]
    return v + 1.0


@pytest.mark.parametrize("name", NAMES)
def test_moving_any_single_constant_changes_the_hash(name, monkeypatch):
    before = L.layout_sha256()
    monkeypatch.setattr(L, name, _mutate(getattr(L, name)))
    assert L.layout_sha256() != before


def test_the_hash_is_deterministic():
    assert L.layout_sha256() == L.layout_sha256()


def test_layout_is_admissible_between_the_flange_and_the_firewall():
    # geometric admissibility only: u >= 0 for everything but the flange disc, below the firewall
    u_firewall = L.config.geometry.eng_o235_flange_fs - 125.0
    allow = 2.0  # in, allowance for the 2 deg pitch and the lab-visible gap
    boxes = {
        "starter": (L.FITTED_STARTER_POS, L.FITTED_STARTER_SIZE),
        "alternator": (L.FITTED_ALTERNATOR_POS, L.FITTED_ALTERNATOR_SIZE),
        "mag_l": (L.FITTED_MAGNETO_LEFT_POS, L.FITTED_MAGNETO_SIZE),
        "mag_r": (L.FITTED_MAGNETO_RIGHT_POS, L.FITTED_MAGNETO_SIZE),
        "carb": (L.FITTED_CARB_POS, L.FITTED_CARB_SIZE),
        "pump": (L.FITTED_FUEL_PUMP_POS, L.FITTED_FUEL_PUMP_SIZE),
    }
    for name, (pos, size) in boxes.items():
        assert pos[0] - size[0] / 2 >= 0, name
        assert pos[0] + size[0] / 2 <= u_firewall - allow, name
    case_end = L.FITTED_CASE_U_START + L.FITTED_CASE_LEN
    assert L.FITTED_CASE_U_START >= 0
    assert case_end + L.FITTED_ACC_DEPTH <= u_firewall - allow
    for pos in L.FITTED_MOUNT_PAD_POS:
        assert pos[0] - L.FITTED_MOUNT_PAD_SIZE[1] / 2 >= 0
