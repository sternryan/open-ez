"""Catalog prices for the build rehearsal."""

from __future__ import annotations

import calendar
import math
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import yaml

from guide.schema import SchemaError

DATA = Path(__file__).resolve().parent.parent / "data"
CATALOG_FLAGS = {"page", "unverified", "unsourced"}
_ITEM_KEYS = {
    "id",
    "label",
    "vendor",
    "part",
    "url",
    "price_usd",
    "unit",
    "read",
    "flag",
}


@dataclass(frozen=True)
class CatalogItem:
    id: str
    label: str
    vendor: str | None
    part: str | None
    url: str | None
    price_usd: float | None
    unit: str
    read: date | None
    flag: str


def _extra(row: object, where: str) -> dict:
    if not isinstance(row, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(row).__name__}")
    bad = sorted((k for k in row if k not in _ITEM_KEYS), key=str)
    if bad:
        raise SchemaError(f"{where}: unknown key(s) {bad}")
    return row


def _text(row: dict, key: str, where: str, *, required: bool) -> str | None:
    value = row.get(key)
    if value is None:
        if required:
            raise SchemaError(f"{where}: {key} must be a non-empty string")
        return None
    if not isinstance(value, str) or value.strip() == "":
        raise SchemaError(f"{where}: {key} must be a non-empty string, got {value!r}")
    return value


def _price(value: object, where: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError(f"{where}: price_usd must be a number, got {value!r}")
    if not math.isfinite(value):
        raise SchemaError(f"{where}: price_usd must be finite, got {value!r}")
    if value < 0:
        raise SchemaError(f"{where}: price_usd must be >= 0, got {value!r}")
    return float(value)


def _read_date(value: object, where: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime) or not isinstance(value, date):
        raise SchemaError(f"{where}: read must be a date, got {value!r}")
    return value


def _item(row: object, where: str) -> CatalogItem:
    data = _extra(row, where)
    item_id = _text(data, "id", where, required=True)
    label = _text(data, "label", where, required=True)
    assert item_id is not None and label is not None
    vendor = _text(data, "vendor", where, required=False)
    part = _text(data, "part", where, required=False)
    url = _text(data, "url", where, required=False)
    price = _price(data.get("price_usd"), where)
    unit = _text(data, "unit", where, required=True)
    assert unit is not None
    read = _read_date(data.get("read"), where)
    flag = data.get("flag")
    if flag not in CATALOG_FLAGS:
        raise SchemaError(f"{where}: bad flag {flag!r}")
    if flag == "unsourced":
        if price is not None:
            raise SchemaError(f"{where}: unsourced price_usd must be null")
    elif flag == "page":
        if price is None:
            raise SchemaError(f"{where}: page needs a price")
        if url is None:
            raise SchemaError(f"{where}: page needs a url")
        if read is None:
            raise SchemaError(f"{where}: page needs a read date")
    return CatalogItem(item_id, label, vendor, part, url, price, unit, read, flag)


def load_catalog(path: Path) -> dict[str, CatalogItem]:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise SchemaError(f"{path.name}: malformed YAML: {e}") from e
    if not isinstance(data, list):
        raise SchemaError(f"{path.name}: must be a list")
    catalog: dict[str, CatalogItem] = {}
    for idx, row in enumerate(data):
        item = _item(row, f"{path.name} item {idx}")
        if item.id in catalog:
            raise SchemaError(f"{path.name}: duplicate id {item.id!r}")
        catalog[item.id] = item
    return catalog


def _months_before(today: date, months: int) -> date:
    """Calendar months back; the day clamps to the target month."""
    year, month = today.year, today.month - months
    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(today.day, last))


def is_stale(item: CatalogItem, today: date, months: int = 6) -> bool:
    if item.read is None:
        return True
    return item.read < _months_before(today, months)
