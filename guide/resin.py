"""Resin cure curves for the build rehearsal."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

from core.sources import check_citation
from guide.schema import FLAGS, SchemaError

_RESIN_KEYS = {"id", "source", "min_temp_c", "gate_hours", "flag"}


@dataclass(frozen=True)
class Resin:
    id: str
    source: str | None
    min_temp_c: float | None
    gate_hours: tuple[tuple[float, float], ...]
    flag: str


def _extra(row: object, where: str) -> dict:
    if not isinstance(row, dict):
        raise SchemaError(f"{where}: must be a mapping, got {type(row).__name__}")
    bad = sorted((k for k in row if k not in _RESIN_KEYS), key=str)
    if bad:
        raise SchemaError(f"{where}: unknown key(s) {bad}")
    return row


def _number(value: object, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError(f"{where}: must be a number, got {value!r}")
    number = float(value)
    if not math.isfinite(number):
        raise SchemaError(f"{where}: must be finite, got {value!r}")
    if number < 0:
        raise SchemaError(f"{where}: must be >= 0, got {value!r}")
    return number


def _source(source: object, flag: object, where: str) -> str | None:
    if flag not in FLAGS:
        raise SchemaError(f"{where}: bad flag {flag!r}")
    if flag == "estimate" or (flag == "unsourced" and source is None):
        if source is not None:
            raise SchemaError(f"{where}: {flag} carries no source")
        return None
    if not isinstance(source, str) or source.strip() == "":
        raise SchemaError(f"{where}: source must be a registry citation")
    try:
        check_citation(source)
    except ValueError as e:
        raise SchemaError(f"{where}: {e}") from e
    return source


def _gate_hours(raw: object, where: str) -> tuple[tuple[float, float], ...]:
    if not isinstance(raw, list):
        raise SchemaError(f"{where}: gate_hours must be a list")
    points: list[tuple[float, float]] = []
    for idx, pair in enumerate(raw):
        loc = f"{where} gate_hours {idx}"
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise SchemaError(f"{loc}: must be a [temp, hours] pair")
        temp = _number(pair[0], f"{loc} temp")
        hours = _number(pair[1], f"{loc} hours")
        if points and temp <= points[-1][0]:
            raise SchemaError(f"{loc}: temperatures must be ascending")
        points.append((temp, hours))
    return tuple(points)


def load_resin(path: Path) -> Resin:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise SchemaError(f"{path.name}: malformed YAML: {e}") from e
    where = path.name
    row = _extra(data, where)
    resin_id = row.get("id")
    if not isinstance(resin_id, str) or resin_id.strip() == "":
        raise SchemaError(f"{where}: id must be a non-empty string")
    flag = row.get("flag")
    source = _source(row.get("source"), flag, where)
    min_temp = row.get("min_temp_c")
    parsed_min = None if min_temp is None else _number(min_temp, f"{where} min_temp_c")
    # The work-again curve stays empty when unsourced. min_temp_c may still be set,
    # with a citation, when only the temperature floor is known.
    if flag == "unsourced" and row.get("gate_hours"):
        raise SchemaError(f"{where}: unsourced curve must be empty")
    return Resin(
        resin_id,
        source,
        parsed_min,
        _gate_hours(row.get("gate_hours"), where),
        flag,
    )


def load_resins(dir: Path) -> dict[str, Resin]:
    if not dir.is_dir():
        raise SchemaError(f"{dir.name}: not a directory")
    resins: dict[str, Resin] = {}
    for path in sorted(dir.glob("*.yaml")):
        resin = load_resin(path)
        if path.stem != resin.id:
            raise SchemaError(f"{path.name}: id {resin.id!r} does not match file name")
        resins[resin.id] = resin
    return resins
