"""Per-step plan block: shape, flags, citations, and round-trip."""

import textwrap

import pytest

from guide.schema import Buy, Plan, SchemaError, Value, load_graph
from tests.guide.test_schema import gdir as _schema_gdir

gdir = pytest.fixture(_schema_gdir.__wrapped__)


def with_plan(gdir, plan: str, title: str = "Cut the foam cores") -> None:
    path = gdir / "ch10.yaml"
    text = path.read_text()
    needle = f"  title: {title}\n"
    block = textwrap.indent(textwrap.dedent(plan).strip() + "\n", "  ")
    assert needle in text
    path.write_text(text.replace(needle, needle + block, 1))


@pytest.mark.parametrize("raw", ["0", "3", "'2'", "true"])
def test_invalid_people(gdir, raw):
    with_plan(gdir, f"plan:\n  people: {raw}\n")
    with pytest.raises(SchemaError, match="people must be 1 or 2"):
        load_graph(gdir)


@pytest.mark.parametrize(
    "plan",
    [
        "plan:\n  people: 2\n",
        "plan:\n  people: 2\n  people_why: ''\n",
        "plan:\n  people: 2\n  people_why: '   '\n",
    ],
)
def test_people_why_required_when_two(gdir, plan):
    with_plan(gdir, plan)
    with pytest.raises(SchemaError, match="people_why required when people is 2"):
        load_graph(gdir)


@pytest.mark.parametrize(
    ("plan", "match"),
    [
        ("plan:\n  hours: {value: 1, flag: guessed}\n", "bad flag 'guessed'"),
        (
            "plan:\n  buy: [{item: bid-7725, qty: 1, flag: community}]\n",
            "bad flag 'community'",
        ),
        (
            "plan:\n  buy: [{item: bid-7725, qty: 1, flag: unsourced}]\n",
            "bad flag 'unsourced'",
        ),
    ],
)
def test_invalid_flags(gdir, plan, match):
    with_plan(gdir, plan)
    with pytest.raises(SchemaError, match=match):
        load_graph(gdir)


@pytest.mark.parametrize(
    ("plan", "match"),
    [
        (
            "plan:\n  hours: {value: 1, flag: official}\n",
            "official needs a registry citation",
        ),
        (
            "plan:\n  hours: {value: 1, flag: official, source: nope}\n",
            "citation must be",
        ),
        (
            "plan:\n  hours: {value: 1, flag: official, source: 'not-a-source:p1'}\n",
            "unknown source id 'not-a-source'",
        ),
        (
            "plan:\n  hours: {value: 1, flag: community, source: aircraftspruce.com/x}\n",
            r"http\(s\) URL",
        ),
        (
            "plan:\n  hours: {value: 1, flag: derived, source: ''}\n",
            "derivation note",
        ),
        (
            "plan:\n  hours: {value: 1, flag: estimate, source: 'https://example.com/a'}\n",
            "estimate carries no source",
        ),
        (
            "plan:\n  hours: {value: 1, flag: unsourced}\n",
            "unsourced value must be null",
        ),
        (
            "plan:\n  hours: {value: null, flag: unsourced, source: 'https://example.com/a'}\n",
            "unsourced carries no source",
        ),
    ],
)
def test_invalid_citations(gdir, plan, match):
    with_plan(gdir, plan)
    with pytest.raises(SchemaError, match=match):
        load_graph(gdir)


@pytest.mark.parametrize(
    ("plan", "match"),
    [
        ("plan:\n  cure: partial\n", "bad cure 'partial'"),
        ("plan:\n  cure: part\n", "resin required when cure is not none"),
        ("plan:\n  cure: all\n", "resin required when cure is not none"),
    ],
)
def test_invalid_cure(gdir, plan, match):
    with_plan(gdir, plan)
    with pytest.raises(SchemaError, match=match):
        load_graph(gdir)


@pytest.mark.parametrize(
    ("plan", "match"),
    [
        ("plan:\n  people: 1\n  buddy: yes\n", r"unknown key\(s\) \['buddy'\]"),
        (
            "plan:\n  hours: {value: 1, flag: estimate, note: x}\n",
            r"unknown key\(s\) \['note'\]",
        ),
        (
            "plan:\n  buy: [{item: bid-7725, qty: 1, flag: estimate, source: x}]\n",
            r"unknown key\(s\) \['source'\]",
        ),
    ],
)
def test_unknown_plan_keys(gdir, plan, match):
    with_plan(gdir, plan)
    with pytest.raises(SchemaError, match=match):
        load_graph(gdir)


def test_round_trip(gdir):
    with_plan(
        gdir,
        """
        plan:
          people: 2
          people_why: draping the skin
          hours: {value: 3, flag: community, source: "https://example.com/log"}
          cure: part
          resin: mgs-285-287
          tools: [squeegee]
          buy: [{item: bid-7725, qty: 4.5, flag: estimate}]
        """,
    )
    plan = load_graph(gdir).ops["c10.cores"].plan
    assert plan == Plan(
        people=2,
        people_why="draping the skin",
        hours=Value(3.0, "community", "https://example.com/log"),
        cure="part",
        resin="mgs-285-287",
        tools=("squeegee",),
        buy=(Buy("bid-7725", 4.5, "estimate"),),
    )


def test_value_flags_and_defaults_round_trip(gdir):
    with_plan(
        gdir,
        """
        plan:
          hours: {value: 2, flag: official, source: "om-1980:p25"}
        """,
    )
    plan = load_graph(gdir).ops["c10.cores"].plan
    assert plan.people == 1 and plan.people_why is None
    assert plan.hours == Value(2.0, "official", "om-1980:p25")
    assert plan.cure == "none" and plan.resin is None
    assert plan.tools == () and plan.buy == ()
    assert load_graph(gdir).ops["c10.twist-check"].plan is None


@pytest.mark.parametrize(
    ("plan", "expected"),
    [
        (
            "plan:\n  hours: {value: 1.5, flag: derived, source: layup area times ply count}\n",
            Value(1.5, "derived", "layup area times ply count"),
        ),
        (
            "plan:\n  hours: {value: null, flag: unsourced}\n",
            Value(None, "unsourced", None),
        ),
        (
            "plan:\n  hours: {value: 1, flag: estimate}\n",
            Value(1.0, "estimate", None),
        ),
    ],
)
def test_sourced_and_unsourced_hours_round_trip(gdir, plan, expected):
    with_plan(gdir, plan)
    assert load_graph(gdir).ops["c10.cores"].plan.hours == expected
