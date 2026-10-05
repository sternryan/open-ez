"""Block 2 2.n Task 3: the analysis config rows equal the sourced closure rows (scope-matched only).

Folded only where the closure row is not `unsourced` and the scope is one-to-one with the config field.
NOT folded: fuselage_weight_lb (120 lump vs the closure's 183 lb fuselage, which includes the spar and gear
struts that already have their own rows in core/ledger.py)."""

import dataclasses

import pytest

from config.aircraft_config import (
    PropulsionConfig,
    StructuralWeightParams,
    WEIGHT_PROVENANCE,
    config,
)
from core.analysis import PhysicsEngine
from core.ledger import load_ledger
from core.systems import LycomingO235

ROWS = {r["name"]: r for r in load_ledger()["closure"]["rows"]}
KG_TO_LB = 2.20462


def _pub(fs):
    """Closure arms are published FS; the config frame is published too (datum_offset_in 0)."""
    return config.geometry.to_published_datum(fs)


# config field pair -> closure row. (weight field, arm field, closure row name)
FOLDED = [
    ("wing_weight_lb", "wing_arm_in", "wings"),
    ("canard_weight_lb", "canard_arm_in", "canard"),
    ("elevator_weight_lb", "elevator_arm_in", "elevators"),
    ("battery_weight_lb", "battery_arm_in", "battery_25ah"),
    ("starter_weight_lb", "starter_arm_in", "starter_ring_alternator"),
    ("instruments_weight_lb", "instruments_arm_in", "instruments"),
    ("interior_weight_lb", "interior_arm_in", "interior"),
]


@pytest.mark.parametrize("wf,af,row", FOLDED)
def test_config_rows_equal_the_sourced_closure_rows(wf, af, row):
    sw = StructuralWeightParams()
    r = ROWS[row]
    assert r["status"] != "unsourced"
    assert getattr(sw, wf) == pytest.approx(r["weight_lb"], abs=1e-9), wf
    assert _pub(getattr(sw, af)) == pytest.approx(r["arm_fs"], abs=0.01), af


def test_engine_row_in_the_analysis_weight_balance_equals_the_closure_row():
    r = ROWS["engine"]
    p = PropulsionConfig()
    assert p.engine_dry_weight_lb == r["weight_lb"]
    assert p.engine_mass_kg * KG_TO_LB == pytest.approx(r["weight_lb"], abs=0.01)
    item = {i.name: i for i in LycomingO235().get_weight_items()}["engine_dry"]
    assert item.weight == r["weight_lb"]
    # the field is inches AFT of the firewall; published FS = firewall + field
    assert config.geometry.fs_firewall + p.engine_cg_arm_in == pytest.approx(r["arm_fs"], abs=1e-9)
    assert item.arm == pytest.approx(r["arm_fs"], abs=1e-9)  # fails on the old firewall + 8.0 = 133.0


def test_engine_displacement_is_the_tcds_value():
    assert PropulsionConfig().engine_displacement_ci == 233.3
    assert "tcds-e223" in WEIGHT_PROVENANCE["engine_displacement_ci"]["source"]


def test_fuselage_lump_is_not_folded():
    # 120 lb is a different scope from the closure's 183 lb (spar and gear included); it stays flagged.
    assert StructuralWeightParams().fuselage_weight_lb == 120.0
    assert ROWS["fuselage"]["weight_lb"] == 183.0


def test_analysis_items_carry_the_folded_rows():
    wb = {i.name: i for i in PhysicsEngine().get_weight_balance().items}
    for name, row in (("Wing Structure", "wings"), ("Canard", "canard"), ("Elevators", "elevators"),
                      ("Battery (25 Ah)", "battery_25ah"), ("Starter, Ring Gear, Alternator", "starter_ring_alternator")):
        assert wb[name].weight == pytest.approx(ROWS[row]["weight_lb"], abs=1e-9), name


def test_analytic_np_does_not_read_any_weight_field(monkeypatch):
    base = PhysicsEngine().calculate_neutral_point()
    sw = config.structural_weights
    for f in dataclasses.fields(sw):
        if f.name.endswith("_weight_lb"):
            monkeypatch.setattr(sw, f.name, getattr(sw, f.name) * 1.10)
    p = config.propulsion
    for name in ("engine_dry_weight_lb",):
        monkeypatch.setattr(p, name, getattr(p, name) * 1.10)
    monkeypatch.setattr(p, "engine_mass_kg", p.engine_mass_kg * 1.10)
    assert PhysicsEngine().calculate_neutral_point() == pytest.approx(base, abs=1e-9)


def test_row_67_configuration_matched_nominal_is_reported_not_gated():
    """Ledger row 67 (record only): the method-check nominal against N26MS step 1, less a starter of about 17 lb."""
    from core.closure import closure_sum

    L = load_ledger()
    nominal = closure_sum(L["closure"]["method_check_rows"]).weight_lb
    step1 = L["prototype_weights"]["rows"]["n26ms_empty_1"]["weight_lb"]
    assert (round(nominal, 2), step1) == (732.79, 693.4)
    matched = nominal - 17.0  # starter about 17 lb (cp-text CP49 p4, CP27 p4); the generator weight is unsourced
    assert round(matched, 1) == 715.8 and round(matched - step1, 1) == 22.4
