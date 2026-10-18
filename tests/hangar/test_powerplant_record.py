"""The first Mod-EZ decision record: powerplant + fuel + tank resin (Hangar H1, Task 3)."""

from __future__ import annotations

import yaml

from hangar.records import DATA_ROOT, load_records, validate_all

RID = "powerplant-fuel-resin"
OPTIONS = {"o235-book", "ul350i", "ul350is", "rotax-912is", "rotax-915is", "rotax-916is",
           "deltahawk-dhk180", "electric", "hybrid"}


def rec():
    return load_records()[RID]


def test_record_valid():
    assert validate_all() == []
    assert RID in load_records()


def test_options_cover_spec():
    r = rec()
    by = {o["id"]: o for o in r.options}
    assert OPTIONS <= set(by)
    assert by["o235-book"]["kind"] == "book"
    assert by["deltahawk-dhk180"]["kind"] == "dropped"
    assert by["electric"]["kind"] == "dropped"
    assert by["hybrid"]["kind"] == "unavailable"
    for o in r.options:
        assert o["facts"] and o["why"].strip()


def test_fuel_paths_present():
    r = rec()
    blob = yaml.safe_dump({"book": r.book_choice, "options": r.options})
    assert "ul94-ethanol-free" in blob and "mogas-e10" in blob
    paths = [o for o in r.options if o["id"] in ("ul94-ethanol-free", "mogas-e10")]
    # the two fuel paths are listed as options of their own, each with a tank-resin consequence fact
    assert {o["id"] for o in paths} == {"ul94-ethanol-free", "mogas-e10"}
    for o in paths:
        assert any("resin" in f["text"].lower() for f in o["facts"])
        assert all(f.get("cite") or f.get("flag") for f in o["facts"])


def test_replaces_engine_and_tanks():
    r = rec()
    assert "f23.engine-install" in r.replaces
    assert any(i.startswith("f21.") for i in r.replaces)


def test_status_open_no_decision():
    r = rec()
    assert r.status == "open" and r.decision is None and r.positions == []
    assert r.spot == "mod-ez" and r.history == []


def test_ul_power_ethanol_unknown():
    r = rec()
    assert any("ethanol" in u["text"].lower() and ("ul" in u["text"].lower()) for u in r.unknowns)
    assert all(u.get("how") for u in r.unknowns)


def test_no_private_or_lane_text():
    text = (DATA_ROOT / "mod-ez" / "decisions" / f"{RID}.yaml").read_text().lower()
    for bad in ("tailnet", "hearth", "anvil", "grok", "local-", "hosted-", "@"):
        assert bad not in text
