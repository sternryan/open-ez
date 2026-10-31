"""The O-235 installation weights come from config.propulsion, not literals in core/systems.py."""

import pytest

from config.aircraft_config import config
from core.systems import LycomingO235

FIELDS = {
    "engine_mount": "engine_mount_weight_lb",
    "exhaust_system": "exhaust_weight_lb",
    "baffles": "baffles_weight_lb",
    "cowling": "cowling_weight_lb",
    "propeller": "prop_weight_lb",
}


def _weights():
    return {i.name: i.weight for i in LycomingO235().get_weight_items()}


@pytest.mark.parametrize("item,field", FIELDS.items())
def test_installation_weight_follows_config(monkeypatch, item, field):
    base = _weights()[item]
    assert base == getattr(config.propulsion, field)
    monkeypatch.setattr(config.propulsion, field, base + 7.0)
    assert _weights()[item] == pytest.approx(base + 7.0)
