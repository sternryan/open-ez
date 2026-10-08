"""core/kernels must stay pure: no airframe data, no I/O, no config."""

import ast
from pathlib import Path

import pytest

KERNELS = Path(__file__).resolve().parents[2] / "core" / "kernels"

ALLOWED = {
    "math",
    "cmath",
    "dataclasses",
    "typing",
    "enum",
    "functools",
    "itertools",
    "collections",
    "numbers",
    "numpy",
    "scipy",
    "__future__",
}
BANNED_NAMES = {
    "pathlib",
    "Path",
    "importlib",
    "__import__",
    "os",
    "sys",
    "io",
    "yaml",
    "json",
    "open",
}


def _check_module(mod: str, level: int, where: str, out: list) -> None:
    if level > 0:
        return  # relative import inside the package
    top = mod.split(".")[0]
    if mod == "core.kernels" or mod.startswith("core.kernels."):
        return
    if top not in ALLOWED:
        out.append(f"{where}: forbidden import '{mod}'")


def violations(pkg_dir: Path) -> list:
    out: list = []
    for py in sorted(Path(pkg_dir).rglob("*.py")):
        tree = ast.parse(py.read_text(), filename=str(py))
        for node in ast.walk(tree):
            where = f"{py.name}:{getattr(node, 'lineno', 0)}"
            if isinstance(node, ast.Import):
                for a in node.names:
                    _check_module(a.name, 0, where, out)
            elif isinstance(node, ast.ImportFrom):
                _check_module(node.module or "", node.level, where, out)
            elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
                out.append(f"{where}: forbidden name '{node.id}'")
            elif isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES:
                out.append(f"{where}: forbidden attribute '{node.attr}'")
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if "data/" in s or s.endswith((".yaml", ".json")):
                    out.append(f"{where}: forbidden data-path string {s!r}")
    return out


def test_core_kernels_is_clean():
    assert violations(KERNELS) == []


BAD = {
    "import_config": "import config\n",
    "import_core_sibling": "from core.simulation import fea_adapter\n",
    "pathlib_path": "from pathlib import Path\nP = Path('data')\n",
    "open_call": "open('x')\n",
    "import_importlib": "import importlib\n",
}


@pytest.mark.parametrize("name", sorted(BAD))
def test_planted_bad_module_is_flagged(tmp_path, name):
    (tmp_path / "bad.py").write_text(BAD[name])
    assert violations(tmp_path)


def test_planted_good_module_passes(tmp_path):
    (tmp_path / "helper.py").write_text("def h(x):\n    return x\n")
    (tmp_path / "good.py").write_text(
        "import numpy as np\n"
        "from dataclasses import dataclass\n"
        "from .helper import h\n\n"
        "@dataclass\nclass K:\n    a: float\n\n"
        "def f(x):\n    return h(float(np.sum(x)))\n"
    )
    assert violations(tmp_path) == []
