# tests/test_gear_ledger.py
"""The retired 45 lb gear lump is decomposed into cited rows (Review Focus 3, captain Decisions)."""

import dataclasses

import pytest

from config.aircraft_config import StructuralWeightParams
from core.analysis import PhysicsEngine
from core.ledger import fuselage_cg, fuselage_ledger_json, gear_cg, gear_rows
from core.sources import check_citation


def _by_name():
    return {r.name: r for r in gear_rows()}


def test_the_free_constants_are_gone():  # Review Focus 3
    names = {f.name for f in dataclasses.fields(StructuralWeightParams)}
    assert "landing_gear_weight_lb" not in names and "landing_gear_arm_in" not in names
    assert not hasattr(StructuralWeightParams(), "landing_gear_arm_in")


def test_main_strut_row_is_22_lb_at_the_axle_with_p50_p8_cites():
    r = _by_name()["main_strut"]
    assert r.weight_lb == 22.0 and r.arm_in == pytest.approx(110.5)
    assert r.status == "book"
    for c in r.cite:
        check_citation(c)
    assert any(c.startswith("plans-1980:p50") for c in r.cite)
    assert any(c.startswith("plans-1980:p8") for c in r.cite)
    assert r.arm_status == "approximate" and "strut CG not printed" in r.note


def test_nose_strut_weight_is_book_and_its_station_is_a_conflict():
    r = _by_name()["nose_strut"]
    assert r.weight_lb == 2.8 and r.arm_in == 17.0 and r.status == "book"
    assert r.arm_status == "conflict" and "about 20" in r.note
    for c in r.cite:
        check_citation(c)


def test_every_unsourced_row_is_flagged():
    rows = gear_rows()
    unsourced = [r for r in rows if r.status == "unsourced"]
    assert [r.name for r in unsourced] == ["wheels_brakes_tyres_axles"]
    r = unsourced[0]
    assert r.arm_status == "unsourced" and r.cite == () and "no source" in r.note
    assert r.weight_lb == pytest.approx(45.0 - 22.0 - 2.8)
    assert all(r.cite for r in rows if r.status != "unsourced")


def test_physics_items_are_the_three_rows_and_total_45():
    wb = PhysicsEngine().get_weight_balance()
    items = {i.name: i for i in wb.items}
    assert "Landing Gear" not in items
    assert items["Main Gear Strut"].weight == 22.0 and items[
        "Main Gear Strut"
    ].arm == pytest.approx(110.5)
    assert (
        items["Nose Gear Strut"].weight == 2.8 and items["Nose Gear Strut"].arm == 17.0
    )
    assert items["Wheels and Brakes (unsourced)"].weight == pytest.approx(20.2)
    total = sum(
        items[n].weight
        for n in ("Main Gear Strut", "Nose Gear Strut", "Wheels and Brakes (unsourced)")
    )
    assert total == pytest.approx(45.0)
    assert gear_cg()[0] == pytest.approx(45.0)


def test_gear_cg_sourced_only_drops_the_unsourced_row():
    w, arm = gear_cg(sourced_only=True)
    assert w == pytest.approx(24.8)
    assert arm == pytest.approx((22.0 * 110.5 + 2.8 * 17.0) / 24.8)


def test_cg_lower_bound_includes_the_two_sourced_gear_rows_only():
    j = fuselage_ledger_json()
    lb = j["cg_lower_bound"]
    assert "main_strut" in lb["included"] and "nose_strut" in lb["included"]
    assert "wheels_brakes_tyres_axles" not in lb["included"]
    assert "wheels_brakes_tyres_axles" in lb["excluded"] and lb["excluded"][
        "wheels_brakes_tyres_axles"
    ].startswith("not yet computed")
    fw, _, _, _ = fuselage_cg(lower_bound=True)
    assert lb["weight_lb"] == pytest.approx(fw + 24.8)
    assert "sourced gear rows" in " ".join(j["notes"])


def test_strict_cg_is_unchanged_and_still_not_yet_computed():
    j = fuselage_ledger_json()
    assert (
        "main_strut" not in j["cg"]["included"]
        and "nose_strut" not in j["cg"]["included"]
    )
    assert j["cg"]["weight_lb"] == fuselage_cg()[0]


def test_ground_handling_block_is_in_the_readout_with_no_numeric_verdict():  # Review Focus 4
    g = fuselage_ledger_json()["gear"]
    gh = g["ground_handling"]
    assert gh["main_axle_fs"] == 110.5 and gh["tip_back_line_deg"] == 12.0
    assert gh["tip_back_check"].startswith("not yet computed") and gh[
        "tip_over_check"
    ].startswith("not yet computed")
    assert [r["name"] for r in g["rows"]] == [
        "main_strut",
        "nose_strut",
        "wheels_brakes_tyres_axles",
    ]
    assert g["total_lb"] == pytest.approx(45.0) and g["sourced_lb"] == pytest.approx(
        24.8
    )


def test_empty_cg_moment_uses_the_rows_not_the_retired_lump():
    items = {i.name: i for i in PhysicsEngine().get_weight_balance().items}
    gear_moment = sum(
        items[n].weight * items[n].arm
        for n in ("Main Gear Strut", "Nose Gear Strut", "Wheels and Brakes (unsourced)")
    )
    assert gear_moment == pytest.approx(22.0 * 110.5 + 2.8 * 17.0 + 20.2 * 110.5)
    assert gear_moment != pytest.approx(45.0 * 84.5)  # the retired lump
