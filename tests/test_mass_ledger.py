import pytest

from core.ledger import Row, cg, in_envelope, load_ledger
from core.sources import check_citation

L = load_ledger()


def _rows(sample):
    arms = L["loads"]
    rows = [Row("empty", L["empty"]["weight_lb"], L["empty"]["arm_in"], "empty", "n/a", L["empty"]["cite"])]
    rows += [Row(k, w, arms[k]["arm_in"], "payload", "n/a", arms[k]["cite"]) for k, w in sample["items"].items()]
    return rows


@pytest.mark.parametrize("name", ["light_pilot", "heavy_pilot"])
def test_manual_sample_loadings_reproduce(name):  # Review Focus 3
    s = L["samples"][name]
    w, c = cg(_rows(s))
    assert w == pytest.approx(s["book_total_lb"], abs=0.5)
    assert c == pytest.approx(s["book_cg_in"], abs=0.01)


def test_sample_gate_fails_on_a_wrong_arm():  # Review Focus 4
    s = L["samples"]["light_pilot"]
    rows = _rows(s)
    rows[1] = rows[1]._replace(arm_in=rows[1].arm_in + 5)
    assert cg(rows)[1] != pytest.approx(s["book_cg_in"], abs=0.01)


def test_envelope_matches_the_manual():
    env = L["envelope"]
    assert (env["fwd_fs"], env["aft_fs"], env["max_lb"], env["takeoff_only_max_lb"]) == (97.0, 103.0, 1325, 1425)
    assert not in_envelope(1113, 103.96, env)  # the manual shows the light-pilot sample outside
    assert in_envelope(1323, 101.06, env)


def test_every_row_is_cited():
    check_citation(L["empty"]["cite"])
    for k, v in L["loads"].items():
        check_citation(v["cite"])


def test_book_errata_recorded():
    assert {e["what"] for e in L["errata"]} >= {"light_pilot pilot moment", "heavy_pilot total moment"}


# --- fuselage box ledger (Block 2 M2.2 Task 4) ---------------------------------------------------
import copy
import json

from core import ledger as ledger_mod
from core.fuselage_book import build_fuselage


def _rows_by_part(rows):
    return {r["part"]: r for r in rows}


def _cited_leaves(node, path=""):
    """Yield (path, dict) for every dict in the materials block that carries a value."""
    if isinstance(node, dict):
        if "value" in node or "areal_oz_yd2" in node or "material" in node:
            yield path, node
        else:
            for k, v in node.items():
                yield from _cited_leaves(v, f"{path}/{k}")


def test_every_material_value_has_a_registered_cite():
    mats = L["materials"]
    leaves = list(_cited_leaves(mats))
    assert len(leaves) >= 8
    for path, leaf in leaves:
        assert "cite" in leaf, path
        check_citation(leaf["cite"])


def test_no_unsourced_number_in_the_materials_block():
    def walk(n, path=""):
        if isinstance(n, dict):
            if "cite" in n:
                return
            for k, v in n.items():
                walk(v, f"{path}/{k}")
        else:
            pytest.fail(f"bare value without a cite at {path}")

    walk(L["materials"])


def test_fuselage_ledger_has_one_row_per_part():
    rows = ledger_mod.fuselage_ledger()
    assert [r["part"] for r in rows] == [n for n in build_fuselage() if n in _bodies()]  # the canard cutout is a void
    assert {r["fidelity"] for r in rows} <= {"book", "derived", "representational"}


def _bodies() -> set[str]:
    return {n for n, p in build_fuselage().items() if not p.void}


def test_foam_core_mass_is_volume_times_sourced_density():
    parts = build_fuselage()
    r = _rows_by_part(ledger_mod.fuselage_ledger())
    dens = {"R45": 3.0, "R250": 16.0}  # lb/ft^3, cp-text:p34 (read from the page, not from the code)
    for name, mat in [("side_right", "R45"), ("bottom", "R45"), ("f22", "R250"), ("rear_seat_bkhd", "R45")]:
        vol = parts[name].solid.val().Volume()
        assert r[name]["volume_in3"] == pytest.approx(vol, rel=1e-9)
        assert r[name]["core_mass_lb"] == pytest.approx(vol * dens[mat] / 1728.0, rel=1e-9), name


def test_wood_parts_have_no_mass_until_their_density_is_sourced():
    r = _rows_by_part(ledger_mod.fuselage_ledger())
    for name in ("firewall", "top_longeron_left", "top_longeron_right"):
        assert r[name]["core_mass_lb"] is None
        assert r[name]["core_mass_reason"].startswith("not yet computed:")
        assert r[name]["total_mass_lb"] is None
        assert r[name]["volume_in3"] > 0  # the volume itself is geometry, always reported


def test_glass_mass_uses_area_areal_weight_and_resin_ratio():
    r = _rows_by_part(ledger_mod.fuselage_ledger())["firewall"]
    # firewall: 2 BID plies (aft + front), the plate's two big faces
    plate = build_fuselage()["firewall"].solid.val().BoundingBox()
    area = (plate.ymax - plate.ymin) * (plate.zmax - plate.zmin)
    assert r["ply_count"] == {"BID": 2}
    assert r["ply_area_in2"]["BID"] == pytest.approx(2 * area, rel=0.005)
    oz_per_in2 = 8.8 / 1296.0  # BID 8.8 oz/yd^2 (wicks page), 1 yd^2 = 1296 in^2
    want = 2 * area * oz_per_in2 / 16.0 * (1 + 0.5)  # resin = 0.5 x cloth (plans-1980:p21)
    assert r["glass_mass_lb"] == pytest.approx(want, rel=0.005)
    assert r["glass_complete"] is True


def test_incomplete_glass_never_reads_as_a_total():
    rows = _rows_by_part(ledger_mod.fuselage_ledger())
    for name in ("side_left", "side_right", "front_seat_bkhd", "panel", "f22", "bottom"):
        r = rows[name]
        assert r["glass_complete"] is False, name
        assert r["glass_unplaced_rows"], name
        assert r["total_mass_lb"] is None
        assert r["total_mass_reason"].startswith("not yet computed:")
        assert r["total_mass_lower_bound_lb"] is not None
        assert r["total_mass_lower_bound_lb"] >= r["core_mass_lb"]


def _patched(monkeypatch, edit):
    data = copy.deepcopy(ledger_mod.load_ledger())
    edit(data["materials"])
    monkeypatch.setattr(ledger_mod, "load_ledger", lambda: data)


def test_dropping_the_foam_density_makes_the_core_mass_not_computed(monkeypatch):
    before = _rows_by_part(ledger_mod.fuselage_ledger())["bottom"]
    assert before["core_mass_lb"] is not None
    _patched(monkeypatch, lambda m: m["foam_lb_ft3"].pop("R45"))
    after = _rows_by_part(ledger_mod.fuselage_ledger())
    assert after["bottom"]["core_mass_lb"] is None
    assert "R45" in after["bottom"]["core_mass_reason"]
    assert after["bottom"]["core_mass_reason"].startswith("not yet computed:")
    assert after["f22"]["core_mass_lb"] is not None  # R250 untouched


def test_dropping_the_areal_weight_makes_the_glass_mass_not_computed(monkeypatch):
    _patched(monkeypatch, lambda m: m["cloth"].pop("BID"))
    r = _rows_by_part(ledger_mod.fuselage_ledger())
    assert r["firewall"]["glass_mass_lb"] is None
    assert r["firewall"]["glass_mass_reason"].startswith("not yet computed:")
    assert "BID" in r["firewall"]["glass_mass_reason"]
    assert r["firewall"]["total_mass_lb"] is None and r["bottom"]["total_mass_lower_bound_lb"] is None


def test_dropping_the_resin_ratio_makes_every_glass_mass_not_computed(monkeypatch):
    _patched(monkeypatch, lambda m: m.pop("resin_to_cloth_weight"))
    for r in ledger_mod.fuselage_ledger():
        if r["ply_count"]:
            assert r["glass_mass_lb"] is None, r["part"]
            assert "resin" in r["glass_mass_reason"]
            assert r["total_mass_lb"] is None


def test_strict_cg_excludes_parts_with_unplaced_glass_and_says_why():
    w, arm, included, excluded = ledger_mod.fuselage_cg()
    assert w == 0.0 and arm is None and included == []
    assert set(excluded) == _bodies()  # the canard cutout is a void, not a ledger part
    assert all(v.startswith("not yet computed:") for v in excluded.values())


def test_lower_bound_cg_is_the_moment_sum_over_core_sourced_parts():
    rows = _rows_by_part(ledger_mod.fuselage_ledger())
    w, arm, included, excluded = ledger_mod.fuselage_cg(lower_bound=True)
    # no core source: the three wood parts as before, plus the belt pieces, roll-over inserts and step (wood species / metal not sourced)
    assert set(excluded) == {
        "firewall", "top_longeron_left", "top_longeron_right", "belt_insert", "belt_attach", "rollover_inserts", "step",
    }
    assert set(included) == _bodies() - set(excluded)
    assert w == pytest.approx(sum(rows[p]["total_mass_lower_bound_lb"] for p in included))
    want = sum(rows[p]["total_mass_lower_bound_lb"] * rows[p]["arm_lower_bound_in"] for p in included) / w
    assert arm == pytest.approx(want)
    assert 22.0 < arm < 125.0


@pytest.mark.xfail(strict=True, reason="geometry-correction-ledger row 57: the sourced chapter 7 skin glass takes the lower bound past 30 lb")
def test_lower_bound_weight_is_at_foam_and_glass_scale():
    w, _, _, _ = ledger_mod.fuselage_cg(lower_bound=True)
    assert 10 < w < 30  # foam-and-glass scale sanity, not a check against a book weight


def test_ledger_json_is_serialisable_and_carries_not_yet_computed_strings():
    out = ledger_mod.fuselage_ledger_json()
    again = json.loads(json.dumps(out))
    assert again == out
    assert [p["part"] for p in out["parts"]] == [n for n in build_fuselage() if n in _bodies()]
    assert out["cg"]["arm_in"] is None and out["cg"]["weight_lb"] == 0.0
    assert out["cg_lower_bound"]["arm_in"] is not None
    assert any("not yet computed" in str(v) for v in out["cg"]["excluded"].values())
    assert out["parts"][0]["core_mass_lb"] is not None


def test_ledger_reasons_name_parts_and_materials_in_plain_words_never_internal_ids():
    """The lab shows these strings; a builder reads "Left top longeron", not `top_longeron_left` (M2.2 Task 7)."""
    import re

    out = ledger_mod.fuselage_ledger_json()
    reasons = [v for c in (out["cg"], out["cg_lower_bound"]) for v in c["excluded"].values()]
    reasons += [r[k] for r in out["parts"] for k in ("core_mass_reason", "glass_mass_reason", "total_mass_reason") if r[k]]
    assert reasons
    ids = set(build_fuselage())
    for s in reasons:
        assert "_" not in s, s
        assert not any(re.search(rf"\b{re.escape(p)}\b", s) for p in ids), s
    assert "not yet computed: core material of Left top longeron not sourced" in reasons
    assert "not yet computed: density of birch plywood not sourced" in reasons
