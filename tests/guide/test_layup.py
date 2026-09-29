# tests/guide/test_layup.py
"""Layup data from the REAL ch30 graph (fixtures can't catch premise defects in the data)."""
import re
from pathlib import Path

import pytest

from guide import layup
from guide.schema import load_graph

G = load_graph(Path("guide/graph"))


@pytest.mark.parametrize("where,expected", [
    ("crossed, full span (108 in)", ("crossed", 54.0)),
    ("crossed, inboard of BL 30", ("crossed", 30.0)),
    ("45 degrees, inboard of BL 10", ("45 degrees", 10.0)),
    ("45 degrees, full span", ("45 degrees", None)),
    ("spanwise, first ply", ("spanwise", None)),
    ("spanwise, final plies", ("spanwise", None)),
])
def test_parse_where_known(where, expected):
    assert layup.parse_where(where) == expected


@pytest.mark.parametrize("where", ["crossed, most of the span", "diagonal, full span", "full span",
                                   "crossed, full span (108)", ""])
def test_parse_where_rejects_unknown(where):
    with pytest.raises(layup.LayupError):
        layup.parse_where(where)


def test_shear_web_full_span_row_carries_108_in():
    rows = G.ops["r30.shear-web"].materials
    assert rows[0]["where"] == "crossed, full span (108 in)"


def test_real_graph_is_fully_scoped():
    assert layup.scope_problems(layup.material_rows(G), set(G.ops)) == []


def test_unscoped_row_is_a_problem():
    rows = layup.material_rows(G) + [("r30.top-skin", "spanwise, a new ply")]
    assert any("r30.top-skin" in p for p in layup.scope_problems(rows, set(G.ops)))
    rows = layup.material_rows(G) + [("r30.hinge-foam", "crossed, full span")]
    assert any("not in LAYUP_SCOPE" in p for p in layup.scope_problems(rows, set(G.ops)))


def test_missing_included_op_is_a_problem():
    assert any("r30.shear-web" in p
               for p in layup.scope_problems(layup.material_rows(G), set(G.ops) - {"r30.shear-web"}))


def test_acceptance_counts():  # spec §1: the numbers Ryan counts on the iPad
    pl = layup.plies(G)
    for bl in (5.0, 40.0):
        c = layup.counts_at(pl, bl)
        assert c["canard.skin_bottom"] == 3 and c["canard.skin_top"] == 4
    assert layup.counts_at(pl, 5.0)["canard.shear_web"] == 6
    assert layup.counts_at(pl, 40.0)["canard.shear_web"] == 2


def test_ply_order_follows_yaml():
    top = [p for p in layup.plies(G) if p.component == "canard.skin_top"]
    assert [p.cloth for p in top] == ["UND", "BID", "UND", "UND"]
    assert [p.order for p in top] == [1, 2, 3, 4]
    assert top[0].node == "canard.skin_top.p1"


def test_position_flags():
    pl = layup.plies(G)
    assert all(not p.position_verified for p in pl
               if p.component in ("canard.shear_web", "canard.spar_cap_bottom", "canard.spar_cap_top"))
    assert all(p.position_verified for p in pl if p.component.startswith("canard.skin_"))
    caps = [p for p in pl if p.op in layup.SPAR_CAP_OPS]
    assert len(caps) == 2 and all(p.bl_max == layup.SPAR_CAP_BL_MAX for p in caps)


def test_shots_cover_scope_and_are_filename_safe():
    s = layup.shots()
    assert [x["id"] for x in s[:2]] == ["hero-bl5", "hero-bl40"]
    assert [x["highlight"] for x in s[2:]] == list(layup.INCLUDED_OPS)
    assert all(re.fullmatch(r"[a-z0-9-]+", x["id"]) for x in s)
    assert layup.shot_id_for_op("r30.shear-web") == "op-r30-shear-web"


def test_alt_text_is_generated_from_counts():
    pl = layup.plies(G)
    hero = layup.shots()[0]
    assert layup.alt_text(G, pl, hero) == (
        "Section at BL 5: bottom skin 3 plies, top skin 4 plies, shear web 6 plies, "
        "spar caps filled to the trough (not to scale)")
    op = next(x for x in layup.shots() if x["highlight"] == "r30.bottom-skin")
    assert layup.alt_text(G, pl, op).startswith(f"After {G.ops['r30.bottom-skin'].title}:")


def test_layup_json_shape():
    j = layup.layup_json(layup.plies(G), 73.5)
    assert j["ops"] == list(layup.INCLUDED_OPS) and j["semi_span"] == 73.5
    n = j["nodes"]["canard.shear_web.p1"]
    assert n["component"] == "canard.shear_web" and n["cloth"] == "UND" and n["op_index"] == 0


def test_other_chapters_are_out_of_scope():
    rows = layup.material_rows(G)
    assert rows
    assert all(G.ops[op].chapter == 30 for op, _ in rows)
    assert any(op_id.startswith("c10.") and op.materials for op_id, op in G.ops.items())
