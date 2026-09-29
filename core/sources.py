"""Registered source documents and the citation form `<id>:p<page>`."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parents[1] / "data/sources/registry.yaml"
_CITE = re.compile(r"^([a-z0-9][a-z0-9-]*):p([0-9A-Za-z.\-]+)(?: .*)?$")


@lru_cache(maxsize=1)
def load_registry() -> dict[str, dict]:
    return yaml.safe_load(REGISTRY.read_text())["sources"]


def parse_citation(s: str) -> tuple[str, str]:
    m = _CITE.match(s or "")
    if not m:
        raise ValueError(f"citation must be '<id>:p<page>', got {s!r}")
    return m.group(1), m.group(2)


def check_citation(s: str) -> None:
    sid, _ = parse_citation(s)
    if sid not in load_registry():
        raise ValueError(f"unknown source id {sid!r} in citation {s!r}")
