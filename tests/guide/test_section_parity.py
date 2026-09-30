"""Review Focus 3: the viewer's layersAt agrees with Python's counts_at on the real layup."""
import json
import subprocess
from collections import Counter
from pathlib import Path

import pytest

from guide import layup
from guide.schema import load_graph

ROOT = Path(__file__).resolve().parents[2]
SECTION_JS = (ROOT / "guide" / "viewer" / "js" / "section.js").as_uri()
BLS = (5, 20, 40, 60)

JS = """
import { readFileSync } from "node:fs";
import { layersAt } from "%(section_js)s";
const lj = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = {};
for (const bl of %(bls)s) out[bl] = layersAt(lj.nodes, bl);
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def parity(tmp_path_factory):
    from core.structures import CanardGenerator

    tmp = tmp_path_factory.mktemp("section_parity")
    pl = layup.plies(load_graph(ROOT / "guide" / "graph"))
    lj = layup.layup_json(pl, CanardGenerator().span / 2)
    (tmp / "layup.json").write_text(json.dumps(lj))
    (tmp / "run.mjs").write_text(JS % {"section_js": SECTION_JS, "bls": list(BLS)})
    r = subprocess.run(["node", str(tmp / "run.mjs"), str(tmp / "layup.json")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return pl, {int(k): v for k, v in json.loads(r.stdout).items()}


@pytest.mark.parametrize("bl", BLS)
def test_by_component_matches_counts_at(parity, bl):
    pl, js = parity
    got = dict(Counter(row["component"] for row in js[bl]))
    assert got == layup.counts_at(pl, bl) and got, (bl, got)


@pytest.mark.parametrize("bl", BLS)
def test_by_cloth_matches_python_filter(parity, bl):
    pl, js = parity
    want = Counter(p.cloth for p in pl if p.bl_max is None or bl <= p.bl_max)
    assert Counter(row["cloth"] for row in js[bl]) == want


def test_stations_actually_differ(parity):
    """A vacuous parity (every station identical) would prove nothing."""
    _, js = parity
    assert len({tuple(sorted(r["node"] for r in js[bl])) for bl in BLS}) >= 3
