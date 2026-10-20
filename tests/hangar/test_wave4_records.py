"""The wave 4 records: cooling, fuel-system and electrical start open, validate, and stay sourced."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.sources import load_registry, parse_citation
from hangar.records import DATA_ROOT, validate_all

NEW = ("cooling", "fuel-system", "electrical")
ROOT = DATA_ROOT / "mod-ez" / "decisions"


def rec(name):
    return yaml.safe_load((ROOT / f"{name}.yaml").read_text())


def test_all_records_validate():
    assert validate_all() == []


@pytest.mark.parametrize("name", NEW)
def test_new_records_are_open_with_a_book_option_and_couplings(name):
    r = rec(name)
    assert r["status"] == "open" and r["decision"] is None and r["history"] == []
    kinds = {o["id"]: o["kind"] for o in r["options"]}
    assert "book" in kinds.values()
    assert "powerplant-fuel-resin" in r["coupled_with"]
    for c in r["coupled_with"]:
        assert (ROOT / f"{c}.yaml").exists()
    assert r["replaces"]
    for ax in r["axes"]:
        assert set(ax["options"]) <= set(kinds)


@pytest.mark.parametrize("name", NEW)
def test_unknowns_have_ids_options_and_state(name):
    r = rec(name)
    ids = [u["id"] for u in r["unknowns"]]
    assert len(ids) == len(set(ids)) and ids
    opts = {o["id"] for o in r["options"]}
    for u in r["unknowns"]:
        assert u["state"] == "open" and u["affects"] and set(u["affects"]) <= opts


@pytest.mark.parametrize("name", NEW)
def test_every_cited_fact_points_at_a_registered_web_source(name):
    reg = load_registry()
    n = 0
    for o in rec(name)["options"]:
        for f in o.get("facts", []):
            if "cite" in f:
                sid, _ = parse_citation(f["cite"])
                assert sid in reg and reg[sid]["obtain"].startswith("https://")
                n += 1
    assert n >= 5


def test_the_battery_options_state_the_makers_minimum_honestly():
    r = rec("electrical")
    by = {o["id"]: o for o in r["options"]}
    for oid in ("lifepo4-etx900", "lifepo4-etx680c"):
        text = " ".join(f["text"] for f in by[oid]["facts"])
        assert "below the maker's 16 Ah minimum" in text
    assert "16 Ah" in " ".join(f["text"] for f in by["agm-pc680"]["facts"])


def test_staged_cg_ballast_unknowns_are_researching_not_sourced():
    states = {u["id"]: u["state"] for u in rec("cg-ballast")["unknowns"]}
    for uid in ("installed-cg-arm", "radiator-coolant-weight", "propeller-weight-arm"):
        assert states[uid] == "researching"
    assert states["owners-own-margins"] == "open"


def test_shared_battery_versus_ground_isolation_is_an_open_unknown():
    r = rec("electrical")
    by = {o["id"]: o for o in r["options"]}
    ground = [f for f in by["ems-isolated-one-battery"]["facts"] if "must not be interconnected" in f["text"]]
    assert ground, "the one-battery option cites the ground-isolation rule"
    u = {u["id"]: u for u in r["unknowns"]}["shared-battery-ground-isolation"]
    assert u["state"] == "open" and "ems-isolated-one-battery" in u["affects"]
    assert "ems-isolated-two-batteries" not in u["affects"]


# physical PDF pages of the installation manual that the new records rest on
IM_PAGES = {"p51", "p52", "p53", "p55", "p57", "p60", "p64", "p96", "p97", "p104", "p108", "p115", "p132", "p136", "p138"}


@pytest.mark.parametrize("name", NEW)
def test_installation_manual_citations_name_a_physical_page_not_p1(name):
    n = 0
    for o in rec(name)["options"]:
        for f in o.get("facts", []):
            if f.get("cite", "").startswith("rotax-im-912i:"):
                sid, page = parse_citation(f["cite"])
                assert f"p{page}" in IM_PAGES, f["cite"]
                n += 1
    assert n >= 1


def test_the_installation_manual_registry_note_describes_physical_pages():
    note = load_registry()["rotax-im-912i"]["note"]
    assert "physical" in note and "cite p1" not in note
