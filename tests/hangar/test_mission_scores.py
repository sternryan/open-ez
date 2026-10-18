"""Mission scores are generated into the record, never typed (Hangar H1, Task 3)."""

from __future__ import annotations

import dataclasses
import shutil

import yaml

from hangar import mission
from hangar.records import DATA_ROOT, load_records, validate_all

OPTS = ["o235-book", "ul350i", "ul350is", "rotax-912is", "rotax-915is", "rotax-916is", "deltahawk-dhk180"]


def test_mission_scores_attached():
    r = load_records()["powerplant-fuel-resin"]
    assert list(r.mission_score) == OPTS
    for o in OPTS:
        assert r.mission_score[o] == yaml.safe_load(yaml.safe_dump(dataclasses.asdict(mission.score(o))))


def test_write_scores_is_idempotent(tmp_path):
    root = tmp_path / "hangar"
    shutil.copytree(DATA_ROOT, root)
    before = load_records(root)["powerplant-fuel-resin"].mission_score
    assert mission.main(["--write-scores", "--root", str(root)]) == 0
    after = load_records(root)["powerplant-fuel-resin"].mission_score
    assert before == after
    assert validate_all(root) == []


def test_book_engine_is_in_envelope_and_known_option_values_flow():
    s = mission.score("rotax-912is")
    assert s.empty_lb.v is not None and s.empty_lb.v < 730
    assert s.fuel_needed_lb.flag in ("sourced", "derived")
    assert mission.score("ul350i").empty_cg.v < mission.score("o235-book").empty_cg.v
    assert mission.score("deltahawk-dhk180").range_full_fuel_nm.flag == "unknown"
