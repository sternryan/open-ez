"""Book engine (O-235) whole-engine fields: values, provenance, and the closure arithmetic."""

import re

from config.aircraft_config import GEOMETRY_PROVENANCE, config
from core.ledger import load_ledger
from core.sources import check_citation

G = config.geometry
FIELDS = {
    "eng_o235_flange_fs": 155.8,
    "eng_o235_cg_from_flange_in": 14.75,
    "eng_o235_cg_below_cl_in": 1.13,
    "eng_o235_cg_left_in": 0.20,
    "eng_o235_bore_in": 4.375,
    "eng_o235_stroke_in": 3.875,
}


def test_fields_carry_the_tcds_and_cp28_values():
    for k, v in FIELDS.items():
        assert getattr(G, k) == v, k
        p = GEOMETRY_PROVENANCE[k]
        assert p["status"] in {"book", "derived"}, k
        assert p["source"], k
        for c in re.findall(r"[a-z0-9-]+:p\d+", p["source"]):
            check_citation(c)


def test_flange_is_the_closure_arithmetic():
    rows = load_ledger()["closure"]["rows"]
    eng = next(r for r in rows if r["name"] == "engine")
    assert round(G.eng_o235_flange_fs - G.eng_o235_cg_from_flange_in, 2) == eng["arm_fs"]


def test_new_sources_are_registered():
    check_citation("lyc-om-o235:p1")
    check_citation("vendor-slick-4300:p1")
