"""Step-script schema faults. Validators are stubs in this wave."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from guide.check import main
from guide.schema import SchemaError, load_graph
from guide.scripts_schema import (
    ACTION_KEYS,
    ACTIONS,
    PROPS,
    load_scripts,
    scripts_for,
    validate_scripts,
)
from tests.guide.test_schema import gdir as _schema_gdir

gdir = pytest.fixture(_schema_gdir.__wrapped__)
ROOT = Path(__file__).resolve().parents[2]


def _fault(op: str, i: int, detail: str) -> str:
    return f"scripts.yaml {op} action {i}: {detail}"


@pytest.fixture
def laid(gdir):
    path = gdir / "ch10.yaml"
    text = path.read_text()
    needle = "  components: [canard.core]\n"
    insert = (
        "  components: [canard.core]\n"
        "  materials: [{cloth: BID, plies: 2, where: skin}]\n"
        "  plan:\n"
        "    people: 2\n"
        "    people_why: draping the skin\n"
        "    tools: [brush, squeegee]\n"
    )
    assert needle in text
    path.write_text(text.replace(needle, insert, 1))
    return gdir


def test_action_vocabulary():
    assert ACTIONS == (
        "cut",
        "place",
        "wet-out",
        "squeegee",
        "drape",
        "flip",
        "sand",
        "check-level",
        "check-string",
        "bond",
        "wait-cure",
    )
    assert PROPS == (
        "squeegee",
        "brush",
        "scissors",
        "hot-wire",
        "level",
        "sanding-block",
        "cup",
        "peel-ply",
        "string-line",
        "stand-in",
    )
    assert ACTION_KEYS == {"do", "part", "ply", "tool", "who", "why"}


def test_rejects_unknown_action(gdir):
    g = load_graph(gdir)
    scripts = {"c10.cores": [{"do": "dance", "who": "owner"}]}
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "unknown action 'dance'")
    ]


def test_rejects_unknown_key(gdir):
    g = load_graph(gdir)
    scripts = {
        "c10.cores": [
            {"do": "place", "part": "canard.core", "who": "owner"},
            {"do": "place", "part": "canard.core", "who": "owner", "speed": 1},
        ]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 1, "unknown key 'speed'")
    ]


def test_rejects_unknown_op(gdir):
    g = load_graph(gdir)
    scripts = {"no.such": [{"do": "place", "part": "canard.core", "who": "owner"}]}
    assert validate_scripts(scripts, g) == [_fault("no.such", 0, "unknown op")]


def test_rejects_unknown_part(gdir):
    g = load_graph(gdir)
    scripts = {"c10.cores": [{"do": "place", "part": "no.such", "who": "owner"}]}
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "unknown part 'no.such'")
    ]


def test_rejects_unknown_tool(gdir):
    g = load_graph(gdir)
    scripts = {"c10.cores": [{"do": "place", "tool": "hammer", "who": "owner"}]}
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "unknown tool 'hammer'")
    ]


def test_rejects_ply_below_one(laid):
    g = load_graph(laid)
    scripts = {
        "c10.cores": [{"do": "wet-out", "ply": 0, "tool": "brush", "who": "owner"}]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "ply 0 is below 1"),
        _fault("c10.cores", 0, "wet-out plies [0] are not 1..2 in order"),
    ]


def test_rejects_ply_above_materials(laid):
    g = load_graph(laid)
    scripts = {
        "c10.cores": [{"do": "wet-out", "ply": 3, "tool": "brush", "who": "owner"}]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "ply 3 is above 2"),
        _fault("c10.cores", 0, "wet-out plies [3] are not 1..2 in order"),
    ]


def test_rejects_ply_when_the_op_has_no_materials(gdir):
    g = load_graph(gdir)
    scripts = {
        "c10.twist-check": [
            {"do": "wet-out", "ply": 1, "tool": "brush", "who": "owner"}
        ]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.twist-check", 0, "tool 'brush' is not in the step plan"),
        _fault("c10.twist-check", 0, "ply on an op with no materials"),
    ]


def test_rejects_who_outside_owner_and_buddy(gdir):
    g = load_graph(gdir)
    scripts = {"c10.cores": [{"do": "place", "part": "canard.core", "who": "crew"}]}
    assert validate_scripts(scripts, g) == [
        _fault("c10.cores", 0, "who 'crew' is not owner or buddy")
    ]


def test_rejects_buddy_when_the_plan_is_missing(gdir):
    g = load_graph(gdir)
    scripts = {
        "c10.twist-check": [
            {"do": "place", "part": "canard.spar_cap_bottom", "who": "buddy"}
        ]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.twist-check", 0, "who buddy needs people 2")
    ]


def test_rejects_buddy_when_people_is_one(gdir):
    path = gdir / "ch10.yaml"
    text = path.read_text()
    needle = "  title: Check for twist\n"
    assert needle in text
    path.write_text(text.replace(needle, needle + "  plan:\n    people: 1\n", 1))
    g = load_graph(gdir)
    scripts = {
        "c10.twist-check": [
            {"do": "place", "part": "canard.spar_cap_bottom", "who": "buddy"}
        ]
    }
    assert validate_scripts(scripts, g) == [
        _fault("c10.twist-check", 0, "who buddy needs people 2")
    ]


def test_valid_script_is_clean(laid):
    g = load_graph(laid)
    scripts = {
        "c10.cores": [
            {"do": "place", "part": "canard.core", "who": "owner"},
            {"do": "wet-out", "ply": 1, "tool": "brush", "who": "owner"},
            {"do": "wet-out", "ply": 2, "tool": "brush", "who": "owner"},
            {
                "do": "squeegee",
                "ply": 2,
                "tool": "squeegee",
                "who": "buddy",
                "why": "optional, ground school only",
            },
        ]
    }
    assert validate_scripts(scripts, g) == []


def test_real_graph_empty_scripts_are_valid(tmp_path):
    dest = tmp_path / "graph"
    shutil.copytree(ROOT / "guide" / "graph", dest)
    (dest / "scripts.yaml").write_text("\n")
    g = load_graph(dest)
    assert load_scripts(dest) == {}
    assert validate_scripts({}, g) == []


def test_missing_scripts_file_is_empty(tmp_path):
    assert load_scripts(tmp_path) == {}


def test_load_scripts_rejects_a_non_mapping(tmp_path):
    (tmp_path / "scripts.yaml").write_text("- not-a-mapping\n")
    with pytest.raises(SchemaError):
        load_scripts(tmp_path)


def test_scripts_for_generates_two_plies_in_order(laid):
    g = load_graph(laid)
    actions = scripts_for(g, {})["c10.cores"]
    assert actions == [
        {"do": "place", "part": "canard.core", "who": "owner"},
        {"do": "wet-out", "ply": 1, "tool": "brush", "who": "owner"},
        {"do": "squeegee", "ply": 1, "tool": "squeegee", "who": "owner"},
        {"do": "wet-out", "ply": 2, "tool": "brush", "who": "owner"},
        {"do": "squeegee", "ply": 2, "tool": "squeegee", "who": "owner"},
    ]
    assert len(actions) == 5


def test_scripts_for_override_wins(laid):
    g = load_graph(laid)
    custom = [{"do": "sand", "part": "canard.core", "who": "owner"}]
    scripts = scripts_for(g, {"c10.cores": custom})
    assert scripts["c10.cores"] == custom


def test_scripts_for_omits_ops_without_materials(laid):
    g = load_graph(laid)
    scripts = scripts_for(g, {})
    assert "c10.twist-check" not in scripts
    assert "c03.layup-skills" not in scripts


def _copy_graph(tmp_path: Path) -> Path:
    dest = tmp_path / "graph"
    shutil.copytree(ROOT / "guide" / "graph", dest)
    return dest


def _write_override(dest: Path, op_id: str, actions: list) -> None:
    path = dest / "scripts.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    data[op_id] = actions
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _front_seat_errs(dest: Path) -> list[str]:
    g = load_graph(dest)
    return validate_scripts(scripts_for(g, load_scripts(dest)), g)


@pytest.mark.parametrize(
    "actions",
    [
        [],
        [
            {"do": "wet-out", "ply": 2, "tool": "brush", "who": "owner"},
            {"do": "wet-out", "ply": 1, "tool": "brush", "who": "owner"},
        ],
        [{"do": "wet-out", "ply": 1, "tool": "brush", "who": "owner"}],
    ],
    ids=["empty", "reversed", "missing-ply"],
)
def test_real_graph_layup_override_must_cover_plies_in_order(tmp_path, actions):
    """The two-ply front-seat layup is generated today; a bad override must fail."""
    dest = _copy_graph(tmp_path)
    _write_override(dest, "f04.front-seat-bkhd-front", actions)
    errs = _front_seat_errs(dest)
    assert any(
        "f04.front-seat-bkhd-front" in err and "wet-out plies" in err for err in errs
    )
    assert main(["--schema-only", "--graph", str(dest)]) == 1


def test_script_tools_match_the_step_or_stand_in():
    """A prop the step does not list is a contradiction. stand-in is the fallback."""
    g, scripts = _real_graph_scripts()
    assert validate_scripts(scripts, g) == []


def test_hot_wire_on_a_wetout_step_fails_guide_check(tmp_path, capsys):
    """A wet-out tool the step does not list fails guide.check."""
    dest = _copy_graph(tmp_path)
    _write_override(
        dest,
        _FRONT,
        [
            {"do": "wet-out", "ply": 1, "tool": "hot-wire", "who": "owner"},
            {"do": "squeegee", "ply": 1, "tool": "squeegee", "who": "owner"},
            {"do": "wet-out", "ply": 2, "tool": "brush", "who": "owner"},
            {"do": "squeegee", "ply": 2, "tool": "squeegee", "who": "owner"},
        ],
    )
    rc = main(["--schema-only", "--graph", str(dest)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "hot-wire" in out


def test_bad_script_fails_guide_check(gdir, capsys):
    (gdir / "scripts.yaml").write_text("nope: [{do: dance, who: owner}]\n")
    g = load_graph(gdir)
    errs = validate_scripts(load_scripts(gdir), g)
    assert errs
    assert any(e.startswith("scripts.yaml ") for e in errs)
    rc = main(["--schema-only", "--graph", str(gdir)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "scripts.yaml" in out


_FRONT = "f04.front-seat-bkhd-front"


def _real_graph_scripts():
    """The scripts guide.check validates: generated actions, overrides on top."""
    g = load_graph(ROOT / "guide" / "graph")
    return g, scripts_for(g, load_scripts(ROOT / "guide" / "graph"))


def _checked_front_seat(actions: list) -> list[str]:
    """Reject a front-seat script through validate_scripts(scripts_for(...)).

    That is the call guide.check makes. The generated script is replaced in
    memory; nothing is written to the graph.
    """
    g, scripts = _real_graph_scripts()
    scripts[_FRONT] = actions
    return validate_scripts(scripts, g)


def test_real_unmutated_scripts_pass():
    """The shipped scripts, generated and overridden, pass the checker."""
    g, scripts = _real_graph_scripts()
    front = scripts[_FRONT]
    assert [a.get("do") for a in front] == [
        "place",
        "wet-out",
        "squeegee",
        "wet-out",
        "squeegee",
    ]
    assert [a.get("ply") for a in front] == [None, 1, 1, 2, 2]
    assert validate_scripts(scripts, g) == []


@pytest.mark.parametrize(
    "action",
    [
        {"do": "place", "ply": 2, "who": "owner"},
        {"do": "drape", "ply": 2, "who": "owner"},
        {"do": "squeegee", "ply": 2, "tool": "squeegee", "who": "owner"},
    ],
    ids=["place", "drape", "squeegee"],
)
def test_real_front_seat_rejects_an_early_ply_action(action):
    """A ply-2 place, drape or squeegee before ply 1 is wet out is rejected.

    The place case is the gate reproduction: prepend that action to the
    generated two-ply front-seat script.
    """
    _, scripts = _real_graph_scripts()
    actions = [action, *scripts[_FRONT]]
    assert _checked_front_seat(actions) == [
        _fault(_FRONT, 0, "ply 2 before ply 1 is wet out")
    ]


def test_reproduction_prepend_place_ply_2_on_front_seat():
    """Prepend {do: place, ply: 2, who: owner} to the generated front-seat script."""
    _, scripts = _real_graph_scripts()
    actions = [{"do": "place", "ply": 2, "who": "owner"}, *scripts[_FRONT]]
    assert _checked_front_seat(actions) == [
        _fault(_FRONT, 0, "ply 2 before ply 1 is wet out")
    ]


def test_real_front_seat_rejects_a_backwards_ply_reference():
    """After ply 2 is open, a later action that names ply 1 is rejected."""
    _, scripts = _real_graph_scripts()
    original = scripts[_FRONT]
    actions = [*original, {"do": "place", "ply": 1, "who": "owner"}]
    assert _checked_front_seat(actions) == [
        _fault(_FRONT, len(original), "ply 1 goes back from ply 2")
    ]
