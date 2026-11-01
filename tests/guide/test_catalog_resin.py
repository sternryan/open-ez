"""Catalog and resin loaders, plus reference checks.

Loader tests call the unimplemented functions and stay red until those land.
`validate_refs` itself is in guide.schema and is checked here directly.
"""

import calendar
import textwrap
from datetime import date
from pathlib import Path

import pytest

from guide.catalog import DATA, CatalogItem, is_stale, load_catalog
from guide.check import main
from guide.resin import Resin, load_resin, load_resins
from guide.schema import SchemaError, load_graph, validate_refs
from tests.guide.test_plan_fields import with_plan
from tests.guide.test_schema import gdir as _schema_gdir

gdir = pytest.fixture(_schema_gdir.__wrapped__)


def _months_ago(today: date, months: int) -> date:
    """Calendar months back; the day clamps to the target month."""
    year, month = today.year, today.month - months
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, min(today.day, calendar.monthrange(year, month)[1]))


def _item(**kw) -> CatalogItem:
    base = {
        "id": "sample",
        "label": "Sample",
        "vendor": None,
        "part": None,
        "url": "https://example.com/sample",
        "price_usd": 1.0,
        "unit": "each",
        "read": date(2026, 10, 8),
        "flag": "page",
    }
    base.update(kw)
    return CatalogItem(**base)


def test_duplicate_ids(tmp_path):
    path = tmp_path / "prices.yaml"
    path.write_text(
        textwrap.dedent(
            """
            - {id: bid-7725, label: A, vendor: null, part: null, url: "https://example.com/a", price_usd: 1, unit: yd, read: 2026-10-08, flag: page}
            - {id: bid-7725, label: B, vendor: null, part: null, url: "https://example.com/b", price_usd: 2, unit: yd, read: 2026-10-08, flag: page}
            """
        )
    )
    with pytest.raises(SchemaError, match="(?i)duplicate"):
        load_catalog(path)


@pytest.mark.parametrize(
    "body",
    [
        "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: -1, unit: each, read: 2026-10-08, flag: page}\n",
        "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: 5, unit: each, read: 2026-10-08, flag: unsourced}\n",
        "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: null, unit: each, read: 2026-10-08, flag: page}\n",
        "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: 5, unit: each, read: 2026-10-08, flag: page}\n",
        "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: 5, unit: each, read: null, flag: page}\n",
        "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: 5, unit: each, read: yesterday, flag: page}\n",
        "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: 5, unit: each, read: 2026-10-08, flag: guessed}\n",
    ],
)
def test_invalid_price_source_and_date(tmp_path, body):
    path = tmp_path / "prices.yaml"
    path.write_text(body)
    with pytest.raises(SchemaError):
        load_catalog(path)


def test_invalid_resin_source_and_curve(tmp_path):
    source = tmp_path / "bad-source.yaml"
    source.write_text(
        "id: bad-source\nsource: nope\nmin_temp_c: 15\n"
        "gate_hours: [[15, 24]]\nflag: official\n"
    )
    with pytest.raises(SchemaError):
        load_resin(source)
    curve = tmp_path / "bad-curve.yaml"
    curve.write_text(
        'id: bad-curve\nsource: "om-1980:p25"\nmin_temp_c: 15\n'
        "gate_hours: [[25, 8], [15, 24]]\nflag: official\n"
    )
    with pytest.raises(SchemaError):
        load_resin(curve)
    pair = tmp_path / "bad-pair.yaml"
    pair.write_text(
        'id: bad-pair\nsource: "om-1980:p25"\nmin_temp_c: 15\n'
        "gate_hours: [[15]]\nflag: official\n"
    )
    with pytest.raises(SchemaError):
        load_resin(pair)
    stem = tmp_path / "resins"
    stem.mkdir()
    (stem / "other.yaml").write_text(
        "id: mgs-285-287\nsource: null\nmin_temp_c: null\ngate_hours: []\nflag: unsourced\n"
    )
    with pytest.raises(SchemaError):
        load_resins(stem)


def test_unsourced_empties(tmp_path):
    prices = tmp_path / "prices.yaml"
    prices.write_text(
        textwrap.dedent(
            """
            - id: tab-adhesive
              label: Toughened paste adhesive
              vendor: null
              part: null
              url: null
              price_usd: null
              unit: each
              read: 2026-10-08
              flag: unsourced
            """
        )
    )
    resins = tmp_path / "resins"
    resins.mkdir()
    resin_path = resins / "sample.yaml"
    resin_path.write_text(
        "id: sample\nsource: null\nmin_temp_c: null\ngate_hours: []\nflag: unsourced\n"
    )
    catalog = load_catalog(prices)
    assert catalog["tab-adhesive"].price_usd is None
    assert catalog["tab-adhesive"].flag == "unsourced"
    resin = load_resin(resin_path)
    assert resin == Resin("sample", None, None, (), "unsourced")
    assert load_resins(resins)["sample"] == resin


def test_is_stale_null_read_and_six_month_boundary():
    today = date(2026, 10, 17)
    cutoff = _months_ago(today, 6)
    assert cutoff == date(2026, 4, 17)
    blank = _item(read=None, price_usd=None, flag="unsourced", url=None)
    assert is_stale(blank, today) is True
    assert is_stale(_item(read=date(2026, 4, 16)), today) is True
    assert is_stale(_item(read=cutoff), today) is False
    assert is_stale(_item(read=date(2026, 10, 8)), today) is False
    clamp_today = date(2026, 3, 31)
    assert is_stale(_item(read=date(2025, 9, 30)), clamp_today) is False
    assert is_stale(_item(read=date(2025, 9, 29)), clamp_today) is True


def test_seeded_catalog_and_resin_load():
    catalog = load_catalog(DATA / "catalog" / "prices.yaml")
    bid = catalog["bid-7725"]
    assert bid.price_usd == 10.50 and bid.unit == "yd" and bid.flag == "page"
    assert bid.read == date(2026, 10, 8)
    assert bid.url == "aircraftspruce.com/catalog/pnpages/01-00642.php"
    assert catalog["vacuum-pump-15500"].price_usd == 469.00
    assert catalog["vacuum-pump-15500"].flag == "unverified"
    assert catalog["tab-adhesive"].price_usd is None
    assert catalog["tab-adhesive"].flag == "unsourced"
    assert catalog["g10-sheet-85345k211"].price_usd is None
    assert catalog["g10-sheet-85345k211"].flag == "unverified"
    rosette = catalog["rosette-cea-06-125uta-350"]
    assert rosette.price_usd is None and rosette.flag == "unverified"
    resins = load_resins(DATA / "resins")
    resin = Resin("mgs-285-287", "mgs-l285-tds:p1", 10.0, (), "unsourced")
    assert resins["mgs-285-287"] == resin
    assert load_resin(DATA / "resins" / "mgs-285-287.yaml") == resin


def test_validate_refs_unknown_buy_and_resin(gdir):
    with_plan(
        gdir,
        """
        plan:
          cure: part
          resin: no-such-resin
          buy:
            - {item: no-such, qty: 1, flag: estimate}
            - {item: bid-7725, qty: 2, flag: estimate}
        """,
    )
    g = load_graph(gdir)
    known = {"bid-7725": _item(id="bid-7725")}
    errs = validate_refs(g, known, {})
    assert "c10.cores: buy item 'no-such' not in catalog" in errs
    assert "c10.cores: buy item 'bid-7725' not in catalog" not in errs
    assert "c10.cores: resin 'no-such-resin' not in data/resins" in errs
    resins = {"no-such-resin": Resin("no-such-resin", None, None, (), "unsourced")}
    catalog = {"bid-7725": _item(id="bid-7725"), "no-such": _item(id="no-such")}
    assert validate_refs(g, catalog, resins) == []


def test_unknown_references_fail_through_check(gdir, capsys):
    with_plan(
        gdir,
        """
        plan:
          cure: part
          resin: no-such-resin
          buy: [{item: no-such, qty: 1, flag: estimate}]
        """,
    )
    code = main(["--schema-only", "--graph", str(gdir)])
    out = capsys.readouterr().out
    assert code == 1
    assert "c10.cores: buy item 'no-such' not in catalog" in out
    assert "c10.cores: resin 'no-such-resin' not in data/resins" in out


def test_paths_are_the_repo_data_dir():
    assert DATA == Path(__file__).resolve().parents[2] / "data"
    assert (DATA / "catalog" / "prices.yaml").is_file()
    assert (DATA / "resins" / "mgs-285-287.yaml").is_file()
