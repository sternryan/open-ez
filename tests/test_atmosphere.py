"""Unit tests for core.atmosphere ISA troposphere model."""

import pytest

import core.atmosphere as atm
from core.atmosphere import (
    density,
    pressure,
    speed_of_sound,
    temperature,
    viscosity,
)


def test_sea_level_reference_values() -> None:
    """Verify all five atmosphere functions at sea level (0 ft)."""
    assert temperature(0) == pytest.approx(518.67, rel=1e-9)
    assert pressure(0) == pytest.approx(2116.22, rel=1e-9)
    assert density(0) == pytest.approx(0.002377, rel=1e-9)
    assert viscosity(0) == pytest.approx(3.737e-07, rel=1e-9)
    assert speed_of_sound(0) == pytest.approx(1116.4267175323241, rel=1e-9)


def test_10000_ft_reference_values() -> None:
    """Verify all five atmosphere functions at 10,000 ft."""
    assert temperature(10000) == pytest.approx(483.00999999999993, rel=1e-9)
    assert pressure(10000) == pytest.approx(1455.3361777967218, rel=1e-9)
    assert density(10000) == pytest.approx(0.0017553620280135243, rel=1e-9)
    assert viscosity(10000) == pytest.approx(3.533975224040779e-07, rel=1e-9)
    assert speed_of_sound(10000) == pytest.approx(1077.3646406208065, rel=1e-9)


def test_tropopause_reference_values() -> None:
    """Verify all five atmosphere functions at the tropopause (36,089 ft)."""
    assert temperature(36089) == pytest.approx(389.976626, rel=1e-9)
    assert pressure(36089) == pytest.approx(472.69326952880726, rel=1e-9)
    assert density(36089) == pytest.approx(0.0007061554858526824, rel=1e-9)
    assert viscosity(36089) == pytest.approx(2.968985266571537e-07, rel=1e-9)
    assert speed_of_sound(36089) == pytest.approx(968.0637222145223, rel=1e-9)


def test_clamping_high_above_tropopause() -> None:
    """Altitudes above 36,089 ft are clamped to 36,089 ft for all functions."""
    assert temperature(50000) == temperature(36089)
    assert pressure(50000) == pressure(36089)
    assert density(50000) == density(36089)
    assert viscosity(50000) == viscosity(36089)
    assert speed_of_sound(50000) == speed_of_sound(36089)


def test_clamping_low_below_sea_level() -> None:
    """Altitudes below 0 ft are clamped to 0 ft for all functions."""
    assert temperature(-500) == temperature(0)
    assert pressure(-500) == pressure(0)
    assert density(-500) == density(0)
    assert viscosity(-500) == viscosity(0)
    assert speed_of_sound(-500) == speed_of_sound(0)


def test_monotonic_decrease_across_troposphere() -> None:
    """All five properties strictly decrease with altitude across the troposphere."""
    altitudes = [0, 5000, 10000, 20000, 30000, 36089]
    for fn in (temperature, pressure, density, speed_of_sound, viscosity):
        values = [fn(h) for h in altitudes]
        for prev_val, next_val in zip(values, values[1:]):
            assert prev_val > next_val


def test_temperature_linear_in_altitude() -> None:
    """Temperature decreases linearly with altitude below the tropopause."""
    assert temperature(0) - temperature(10000) == pytest.approx(10000 * 0.003566)
    assert temperature(5000) == pytest.approx((temperature(0) + temperature(10000)) / 2)


def test_ideal_gas_speed_of_sound_consistency() -> None:
    """Speed of sound squared matches gamma * R * T at 0 and 10,000 ft."""
    for h in (0, 10000):
        assert speed_of_sound(h) ** 2 == pytest.approx(1.4 * 1716.49 * temperature(h))


def test_pressure_density_ratio_at_10000_ft() -> None:
    """Pressure-to-density ratio at 10,000 ft matches the reference table values."""
    assert pressure(10000) / density(10000) == pytest.approx(
        1455.3361777967218 / 0.0017553620280135243
    )


def test_private_constants() -> None:
    """Verify module-level ISA constants."""
    assert atm._TROPOPAUSE_FT == 36089.0
    assert atm._T0 == 518.67
    assert atm._LAPSE_RATE == 0.003566


def test_clamp_boundary_transition() -> None:
    """Just inside the upper clamp differs from the boundary while above is clamped."""
    assert temperature(36088.0) > temperature(36089.0)
    assert temperature(36090.0) == temperature(36089.0)


def test_matches_published_isa_table_loosely():
    """Independent of the module's own constants: US Standard Atmosphere 1976 values at 10,000 ft."""
    import core.atmosphere as atm

    assert atm.pressure(10000) == pytest.approx(1455.6, rel=2e-3)
    assert atm.density(10000) == pytest.approx(0.001756, rel=2e-3)
    assert atm.speed_of_sound(10000) == pytest.approx(1077.4, rel=1e-3)
    assert atm.temperature(36089) == pytest.approx(389.97, rel=1e-4)
