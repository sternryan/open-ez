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
