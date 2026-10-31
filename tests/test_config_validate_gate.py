"""AircraftConfig.validate() must reject a deliberately broken config."""

import copy
from dataclasses import replace

from config.aircraft_config import AirfoilType, config


def _broken(**sections):
    """Deep copy of the shared config with whole sections swapped; the global is untouched."""
    c = copy.deepcopy(config)
    for name, value in sections.items():
        setattr(c, name, value)
    return c


def test_clean_config_has_no_errors():
    assert copy.deepcopy(config).validate() == []


def test_gu_canard_is_a_safety_violation():
    gu = next(a for a in AirfoilType if a is not AirfoilType.RONCZ_R1145MS)
    c = _broken(airfoils=replace(config.airfoils, canard=gu))
    assert any(e.startswith("SAFETY VIOLATION") for e in c.validate())


def test_low_builder_credit_is_a_compliance_violation():
    c = _broken(compliance=replace(config.compliance, task_credits={"finishing": 0.06}))
    assert any(e.startswith("COMPLIANCE VIOLATION") for e in c.validate())


def test_wing_stalling_first_is_a_stability_warning():
    # Canard CLmax far above the wing's: canard no longer stalls first.
    c = _broken(aero_limits=replace(config.aero_limits, canard_clmax=3.0))
    assert any(e.startswith("STABILITY WARNING") for e in c.validate())
