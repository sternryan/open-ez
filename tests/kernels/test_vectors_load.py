"""Every number in the vector files loads as a number (YAML 1.1 reads 38.6e9 as a string)."""

import pytest
import yaml

from tests.kernels._vectors import VEC, load

FILES = sorted(p.name for p in VEC.glob("*.yaml"))


def _numeric_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _numeric_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _numeric_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        try:
            float(obj)
        except ValueError:
            return
        yield path, obj


@pytest.mark.parametrize("name", FILES)
def test_no_number_loads_as_a_string(name):
    assert list(_numeric_strings(load(name))) == []


def test_plain_safe_load_would_have_read_a_string():
    assert yaml.safe_load("a: 38.6e9")["a"] == "38.6e9"
    assert list(_numeric_strings(yaml.safe_load("a: 38.6e9")))
