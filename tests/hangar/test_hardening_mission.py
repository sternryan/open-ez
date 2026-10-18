"""Gaps the first-round reviews found: hostile input, bindings, and what must never leak (Hangar H1/H2)."""

from __future__ import annotations

import copy
import dataclasses
import io
import json
import os
import shutil
from pathlib import Path

import pytest
import yaml

from hangar import council, mission
from hangar.council import CouncilReply, CouncilUnavailable, ask, backbone
from hangar.records import DATA_ROOT, load_record, validate, validate_all
from tests.hangar.test_council import fake, pos, reply_of
from tests.hangar.test_records import GRAPH, base, decided, errs, fact, make

# ---------------------------------------------------------------- mission


def V(v, flag="sourced", note=""):
    return {"v": v, "flag": flag, "note": note}


MISSION = {
    "leg_nm": 300, "reserve_min": 30, "occupants_lb": [155, 155], "bags_lb": 15,
    "cruise_ktas": V(150), "fuel_capacity_gal": V(52), "fuel_density_lb_per_gal": V(6.0),
}


def plant(arm=V(141.05, "derived", "assumed same installed CG as the book engine"), ff=V(4.3), lb=V(173.0)):
    return {"x": {"installed_lb": lb, "cg_arm_in": arm, "cruise_ff_gph": ff}}


def test_unknown_cg_arm_does_not_crash():
    s = mission.score("x", MISSION, plant(arm=V(None, "unknown")))
    assert s.takeoff_cg.v is None and s.landing_cg.v is None and s.empty_cg.v is None
    assert s.in_envelope is None and s.worst_flag == "unknown"
    assert s.empty_lb.v is not None  # the weight does not need the arm


def test_null_value_is_unknown_whatever_the_flag():
    s = mission.score("x", MISSION, plant(ff=V(None, "derived")))
    assert s.fuel_needed_lb.v is None and s.fuel_needed_lb.flag == "unknown"
    assert s.worst_flag == "unknown"


def test_oil_is_in_the_takeoff_loading():
    s = mission.score("x", MISSION, plant())
    fuel = 4.3 * 2.5 * 6.0
    assert s.takeoff_lb.v == pytest.approx(s.empty_lb.v + 310 + 15 + 8 + fuel)


def test_private_override_reaches_score_and_is_derived(tmp_path, monkeypatch):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"cruise_ktas": 160}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(tmp_path))
    s = mission.score("o235-book")
    assert s.block_time_h.v == pytest.approx(300 / 160 + 0.5)
    assert s.block_time_h.flag == "derived"  # a bare private number is never "sourced"


def test_write_scores_ignores_the_private_dir(tmp_path, monkeypatch):
    root = tmp_path / "hangar"
    shutil.copytree(DATA_ROOT, root)
    mission.write_scores(root)
    before = (root / "mod-ez/decisions/powerplant-fuel-resin.yaml").read_text()
    priv = tmp_path / "priv"
    priv.mkdir()
    (priv / "mission.yaml").write_text(yaml.safe_dump({"occupants_lb": [250, 250], "cruise_ktas": 120}))
    monkeypatch.setenv("HANGAR_PRIVATE_DIR", str(priv))
    mission.write_scores(root)
    assert (root / "mod-ez/decisions/powerplant-fuel-resin.yaml").read_text() == before


def test_assumptions_surface_caveat_notes():
    a = " ".join(mission.score("rotax-912is").assumptions).lower()
    assert "coolant" in a  # the installed-weight caveat
    assert "assumed same installed cg" in a


