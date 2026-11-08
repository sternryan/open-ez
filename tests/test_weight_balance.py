"""Tests for core.weight_balance (WeightItem and WeightBalance)."""

import pytest

import core.weight_balance as weight_balance_module
from core.analysis import (
    WeightBalance as AnalysisWeightBalance,
    WeightItem as AnalysisWeightItem,
)
from core.weight_balance import WeightBalance, WeightItem


def _build_reference_wb() -> WeightBalance:
    wb = WeightBalance()
    wb.add_item("pilot", 180, 59.0, "payload")
    wb.add_item("fuel", 60, 110.0, "fuel")
    wb.add_item("airframe", 700, 100.0)
    return wb


def test_weight_item_moment() -> None:
    pilot = WeightItem("pilot", 180, 59.0, "payload")
    fuel = WeightItem("fuel", 60, 110.0, "fuel")
    airframe = WeightItem("airframe", 700, 100.0)

    assert pilot.moment == 180 * 59.0
    assert pilot.moment == 10620.0
    assert fuel.moment == 60 * 110.0
    assert fuel.moment == 6600.0
    assert airframe.moment == 700 * 100.0
    assert airframe.moment == 70000.0


def test_weight_item_default_category() -> None:
    item = WeightItem("airframe", 700, 100.0)
    assert item.category == "fixed"

    custom = WeightItem("pilot", 180, 59.0, "payload")
    assert custom.category == "payload"


def test_reference_case_totals_and_cg() -> None:
    wb = _build_reference_wb()

    assert wb.total_weight == 940
    assert wb.total_moment == 87220.0
    assert wb.cg_location == pytest.approx(92.7872340425532, rel=1e-12)
    assert wb.cg_location == pytest.approx(87220.0 / 940, rel=1e-12)


def test_add_item_appends_weight_item_with_fields_and_category() -> None:
    wb = _build_reference_wb()

    assert len(wb.items) == 3
    assert wb.items[0] == WeightItem("pilot", 180, 59.0, "payload")
    assert wb.items[1] == WeightItem("fuel", 60, 110.0, "fuel")
    assert wb.items[2] == WeightItem("airframe", 700, 100.0, "fixed")
    assert [item.moment for item in wb.items] == [10620.0, 6600.0, 70000.0]


def test_empty_weight_balance() -> None:
    wb = WeightBalance()

    assert wb.items == []
    assert wb.total_weight == 0
    assert wb.total_moment == 0
    assert wb.cg_location == 0.0


def test_zero_total_weight_guard() -> None:
    wb = WeightBalance()
    wb.add_item("pos", 5.0, 50.0)
    wb.add_item("neg", -5.0, 100.0)

    assert wb.total_weight == 0.0
    assert wb.cg_location == 0.0


def test_default_items_list_not_shared_between_instances() -> None:
    wb1 = WeightBalance()
    wb2 = WeightBalance()

    wb1.add_item("pilot", 180, 59.0, "payload")

    assert len(wb1.items) == 1
    assert wb2.items == []
    assert wb1.items is not wb2.items


def test_reference_summary_exact_text() -> None:
    wb = _build_reference_wb()
    expected = "\n".join(
        [
            "Weight & Balance Summary",
            "========================================",
            "Item                        Weight      Arm     Moment",
            "----------------------------------------",
            "pilot                        180.0     59.0    10620.0",
            "fuel                          60.0    110.0     6600.0",
            "airframe                     700.0    100.0    70000.0",
            "----------------------------------------",
            "TOTAL                        940.0     92.8    87220.0",
            "",
            "Center of Gravity: 92.79 in (FS)",
        ]
    )

    assert wb.summary() == expected


def test_empty_summary_format() -> None:
    wb = WeightBalance()
    text = wb.summary()

    assert "TOTAL                          0.0      0.0        0.0" in text
    assert text.endswith("\n\nCenter of Gravity: 0.00 in (FS)")


def test_cg_moves_toward_added_heavy_aft_item() -> None:
    wb = _build_reference_wb()
    initial_cg = wb.cg_location

    wb.add_item("ballast", 100, 150.0)

    assert wb.total_weight == 1040
    assert wb.total_moment == 102220.0
    assert wb.cg_location == pytest.approx(102220.0 / 1040)
    assert initial_cg < wb.cg_location < 150.0


def test_reexport_from_core_analysis_identity() -> None:
    assert AnalysisWeightItem is WeightItem
    assert AnalysisWeightBalance is WeightBalance


def test_module_dunder_all() -> None:
    assert weight_balance_module.__all__ == ["WeightItem", "WeightBalance"]
