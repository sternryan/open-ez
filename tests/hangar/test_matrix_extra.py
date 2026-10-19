"""Matrix extras: private owner overlay, change digest, record text."""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from hangar import matrix as mx
from hangar import matrix_extra as mxe
from hangar import mission
from hangar.mission import apply_effect, score_pilot


def option_effects():
    rec = yaml.safe_load(open("data/hangar/mod-ez/decisions/cg-ballast.yaml"))
    return {o["id"]: o["effect"] for o in rec["options"] if isinstance(o.get("effect"), dict)}


def public(effect):
    return mx.matrix_for_effect(effect)


def test_matrix_digest_is_stable_and_follows_the_numbers():
    eff = option_effects()["battery-aft"]
    d1 = mxe.matrix_digest(eff)
    assert d1 == mxe.matrix_digest(copy.deepcopy(eff)) and isinstance(d1, str) and len(d1) >= 16
    moved = copy.deepcopy(eff)
    moved["extras"][1]["arm_in"] = 120.0
    assert mxe.matrix_digest(moved) != d1
    assert mxe.matrix_digest(option_effects()["loading-limit"]) != d1


def test_matrix_text_names_the_worst_cells_and_crossings():
    t = mxe.matrix_text(public(option_effects()["battery-aft"]))
    assert "aft" in t and "forward" in t and "gross" in t
    assert "-1.3 in" in t or "-1.26" in t
    assert "151" in t  # the aft crossing weight
    assert "no owner weights" in t


# --- private overlay ---------------------------------------------------------------------------------------------------

def write_private(tmp_path, data):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump(data))
    return tmp_path


def test_private_matrix_uses_pilots_and_labels_and_leaks_no_weights(tmp_path):
    d = write_private(tmp_path, {"pilots": [{"label": "Pat", "lb": 133.37}, {"label": "Sam", "lb": 187.91}], "bags_lb": 31.43})
    m = mxe.private_matrix(option_effects()["battery-aft"], d)
    assert m is not None
    labels = {c["occupancy_label"] for c in m["cells"]}
    assert "Pat solo" in labels and "Sam solo" in labels and "Pat front, Sam rear" in labels and "Sam front, Pat rear" in labels
    # 2 solos + 2 ordered pairs, bags: none and the one private bag, 3 fuels, 2 states
    assert m["cell_count"] == (2 + 2) * 2 * 3 * 2
    assert m["crossings"] is None
    text = json.dumps(m)
    for secret in ("133.37", "187.91", "31.43"):
        assert secret not in text
    assert m["worst"]["aft"] is not None and any(n in m["worst"]["aft"]["loading"] for n in ("Pat", "Sam"))


def test_private_matrix_scores_the_real_weights(tmp_path):
    d = write_private(tmp_path, {"pilots": [{"label": "Pat", "lb": 133.37}]})
    m = mxe.private_matrix(option_effects()["loading-limit"], d)
    eng, extras, plants = apply_effect(option_effects()["loading-limit"])
    s = score_pilot(eng, 133.37, mission=mission.load_mission(None) | {"bags_lb": 15}, plants=plants, extras=extras)
    c = [x for x in m["cells"] if x["occupancy_label"] == "Pat solo" and x["fuel"] == "mission" and x["state"] == "landing"
         and x["bag"] == "light"]
    assert len(c) == 1 and c[0]["cg_in"] == pytest.approx(s.landing_cg.v, abs=1e-6)


def test_private_matrix_none_without_pilots_or_with_bad_file(tmp_path):
    assert mxe.private_matrix(option_effects()["battery-aft"], tmp_path) is None
    assert mxe.private_matrix(option_effects()["battery-aft"], None) is None
    write_private(tmp_path, {"pilots": []})
    assert mxe.private_matrix(option_effects()["battery-aft"], tmp_path) is None
    (tmp_path / "mission.yaml").write_text("pilots: [unclosed")
    assert mxe.private_matrix(option_effects()["battery-aft"], tmp_path) is None
    write_private(tmp_path, {"pilots": [{"label": "Bad", "lb": "heavy"}, {"label": "Neg", "lb": -5}, {"label": "NaN", "lb": float("nan")}]})
    assert mxe.private_matrix(option_effects()["battery-aft"], tmp_path) is None  # no usable pilot


def test_private_bags_may_be_a_list(tmp_path):
    d = write_private(tmp_path, {"pilots": [{"label": "Pat", "lb": 150}], "bags_lb": [10, 40]})
    m = mxe.private_matrix(option_effects()["loading-limit"], d)
    assert m["cell_count"] == 1 * 3 * 3 * 2  # bags: none, bag 1, bag 2
    assert {c["bag_label"] for c in m["cells"]} == {"no bag", "bag 1", "bag 2"}


def test_private_bags_default_to_none_and_the_public_light_bag(tmp_path):
    d = write_private(tmp_path, {"pilots": [{"label": "Pat", "lb": 150}]})
    m = mxe.private_matrix(option_effects()["loading-limit"], d)
    assert m["cell_count"] == 1 * 2 * 3 * 2
    assert {c["bag_label"] for c in m["cells"]} == {"no bag", "light overnight bag"}
