import calendar
import json
from datetime import date, timedelta

import pytest

from guide.build_site import build
from guide.schema import SchemaError
from tests.guide.render_fixture import ROOT, make_export, make_renders
from tests.guide.test_schema import gdir as _schema_gdir

_graph_dir = pytest.fixture(name="gdir")(_schema_gdir.__wrapped__)


def test_build_writes_site(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base="/private/scan-1980/pages/", docs=None)
    g = json.loads((out / "graph.json").read_text())
    assert g["order"][0] == "c03.layup-skills"
    assert {o["id"] for o in g["ops"]} == {
        "c03.layup-skills",
        "c10.cores",
        "c10.twist-check",
    }
    assert (
        g["ops"][1]["id"] == "c10.cores" and g["ops"][1]["changes"][0]["class"] == "MEO"
    )
    assert (
        json.loads((out / "config.json").read_text())["scanBase"]
        == "/private/scan-1980/pages/"
    )
    assert (out / "index.html").exists() and not (out / "tests").exists()


def test_build_refuses_invalid_graph(gdir, tmp_path):
    p = gdir / "ch10.yaml"
    p.write_text(p.read_text().replace("requires: [c10.cores]", "requires: [nope]"))
    with pytest.raises(SchemaError):
        build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)


REPO_GRAPH = ROOT / "guide" / "graph"


def test_no_renders_means_m1_output(
    tmp_path,
):  # CRITICAL regression: M1 builds unchanged
    e = make_export(tmp_path / "e")
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
    )
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["cutaway"] is None and not (tmp_path / "site" / "renders").exists()
    assert [p["order"] for p in g["plies"]["canard.skin_top"]] == [1, 2, 3, 4]


def test_no_models_no_plies(gdir, tmp_path):
    build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["plies"] == {} and g["cutaway"] is None


def test_renders_wired(tmp_path):
    e = make_export(tmp_path / "e")
    r = make_renders(tmp_path / "r", e)
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
        renders=r,
    )
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    c = g["cutaway"]
    assert c["ops"]["r30.bottom-skin"]["src"] == "renders/op-r30-bottom-skin.png"
    assert [h["bl"] for h in c["heroes"]] == [5.0, 40.0]
    assert c["heroes"][0]["alt"].startswith("Section at BL 5: bottom skin 3 plies")
    assert "shear web 6 at BL 5, 2 at BL 40" in c["count_note"]
    assert (tmp_path / "site" / "renders" / "hero-bl40.png").exists()


@pytest.mark.parametrize(
    "kw,needle",
    [
        ({"drop": "hero-bl40"}, "hero-bl40"),
        ({"bad_png": "op-r30-top-skin"}, "op-r30-top-skin"),
    ],
)
def test_renders_strict(tmp_path, kw, needle):
    e = make_export(tmp_path / "e")
    r = make_renders(tmp_path / "r", e, **kw)
    with pytest.raises(SchemaError, match=needle):
        build(
            REPO_GRAPH,
            tmp_path / "site",
            models=e / "longez.glb",
            scan_base=None,
            docs=None,
            renders=r,
        )


def test_renders_stale_layup(tmp_path):
    e = make_export(tmp_path / "e")
    r = make_renders(tmp_path / "r", e)
    (e / "layup.json").write_text(
        (e / "layup.json").read_text().replace('"semi_span": 63.0', '"semi_span": 70')
    )
    with pytest.raises(SchemaError, match="layup.json"):
        build(
            REPO_GRAPH,
            tmp_path / "site",
            models=e / "longez.glb",
            scan_base=None,
            docs=None,
            renders=r,
        )


def test_renders_need_models(tmp_path):
    with pytest.raises(SchemaError, match="--renders needs --models"):
        build(
            REPO_GRAPH,
            tmp_path / "site",
            models=None,
            scan_base=None,
            docs=None,
            renders=tmp_path,
        )


def test_legend_states_planform_source():  # Block 1: GU planform stands in until the Roncz one is sourced
    from guide.build_site import LEGEND

    assert any(
        e["text"]
        == "Canard planform: GU size from the Owner's Manual; Roncz planform unconfirmed"
        for e in LEGEND
    )


def test_ply_rows_carry_op(
    tmp_path,
):  # build progression reads the owning op from graph.plies
    e = make_export(tmp_path / "e")
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
    )
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    ops = {o["id"] for o in g["ops"]}
    rows = [r for rs in g["plies"].values() for r in rs]
    assert rows and all(r["op"] in ops for r in rows)
    assert sum(r["op"] == "r30.shear-web" for r in g["plies"]["canard.shear_web"]) == 6


def test_layup_shipped_when_next_to_models(tmp_path):
    e = make_export(tmp_path / "e")
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
    )
    g = json.loads((tmp_path / "site" / "graph.json").read_text())
    assert g["layup"] == json.loads((e / "layup.json").read_text())
    assert (
        set(g["layup"]) == {"ops", "semi_span", "nodes"}
        and g["layup"]["semi_span"] == 63.0
    )


def test_ledger_json_ships_beside_the_data_when_the_export_has_one(tmp_path):
    e = make_export(tmp_path / "e")
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
    )
    assert not (
        tmp_path / "site" / "ledger.json"
    ).exists()  # an export without a ledger ships none (the lab says so)
    led = {
        "cg": {
            "weight_lb": 0,
            "arm_in": None,
            "included": [],
            "excluded": {"f22": "not yet computed: x"},
        }
    }
    (e / "ledger.json").write_text(json.dumps(led))
    build(
        REPO_GRAPH,
        tmp_path / "site2",
        models=e / "longez.glb",
        scan_base=None,
        docs=None,
    )
    assert json.loads((tmp_path / "site2" / "ledger.json").read_text()) == led


def test_no_layup_means_null(gdir, tmp_path):
    build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
    assert json.loads((tmp_path / "site" / "graph.json").read_text())["layup"] is None
    glb = tmp_path / "bare" / "longez.glb"
    glb.parent.mkdir()
    glb.write_bytes(b"glTF")
    build(
        gdir, tmp_path / "site2", models=glb, scan_base=None, docs=None
    )  # models without a layup.json beside it
    assert json.loads((tmp_path / "site2" / "graph.json").read_text())["layup"] is None


def test_site_root_is_the_lab_and_the_classic_viewer_sits_under_classic(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base=None, docs=None)
    root = (out / "index.html").read_text()
    assert (
        'id="gl"' in root and 'id="opbar"' in root and "Long-EZ build lab" in root
    )  # the lab, not the classic viewer
    assert 'id="ops"' not in root
    assert list((out / "assets").glob("*.js"))
    assert not (
        out / ".stamp"
    ).exists()  # the build stamp is bookkeeping, not site content
    assert not (out / "lab").exists()  # the /lab/ copy is gone: one engine, served at /
    classic = (out / "classic" / "index.html").read_text()
    assert 'id="ops"' in classic and 'name="data-base" content="../"' in classic
    assert (
        (out / "classic" / "js" / "app.js").is_file()
        and (out / "classic" / "vendor").is_dir()
        and not (out / "classic" / "tests").exists()
    )
    assert (
        'name="data-base" content="./"' in root
    )  # the lab reads the data beside itself
    for shared in (
        "graph.json",
        "config.json",
        "models",
    ):  # one copy of the data, at the site root
        assert (out / shared).exists() and not (out / "classic" / shared).exists()


def test_classic_and_lab_docs_links_and_renders_still_resolve(tmp_path):
    e = make_export(tmp_path / "e")
    r = make_renders(tmp_path / "r", e)
    docs = tmp_path / "docs"
    (docs / "specs").mkdir(parents=True)
    (docs / "plans").mkdir()
    (docs / "specs" / "2026-01-01-build-guide-design.md").write_text("# hello\n")
    build(
        REPO_GRAPH,
        tmp_path / "site",
        models=e / "longez.glb",
        scan_base=None,
        docs=docs,
        renders=r,
    )
    out = tmp_path / "site"
    assert (out / "docs" / "index.html").is_file() and (
        out / "renders" / "hero-bl40.png"
    ).is_file()
    page = (out / "docs" / "2026-01-01-build-guide-design.html").read_text()
    href = page.split("href='")[1].split("'")[0]
    assert (
        (out / "docs" / href).resolve().is_file()
    )  # the docs page still finds its stylesheet


def _months_ago(today: date, months: int = 6) -> date:
    """Calendar months back; the day clamps to the target month. Equal is not stale."""
    year, month = today.year, today.month - months
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, min(today.day, calendar.monthrange(year, month)[1]))


def test_plan_json_payload_and_iso_dates(gdir, tmp_path):
    from tests.guide.test_schema import write

    write(
        gdir,
        "groups.yaml",
        """
        groups:
          - {id: bulkheads-firewall, label: "Seat bulkheads and firewall"}
          - {id: fuselage-sides, label: "Fuselage sides"}
        required_files: []
        """,
    )
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base=None, docs=None)
    plan = json.loads((out / "plan.json").read_text())
    assert set(plan) == {"groups", "resins", "catalog", "scripts", "today"}
    assert plan["groups"] == [
        {"id": "bulkheads-firewall", "label": "Seat bulkheads and firewall"},
        {"id": "fuselage-sides", "label": "Fuselage sides"},
    ]
    assert plan["scripts"] == {}
    assert plan["today"] == date.today().isoformat()
    bid = plan["catalog"]["bid-7725"]
    assert set(bid) == {"label", "url", "price_usd", "unit", "flag", "read", "stale"}
    assert bid["read"] == "2026-10-08"
    assert bid["price_usd"] == 10.50
    resin = plan["resins"]["mgs-285-287"]
    assert set(resin) == {"min_temp_c", "gate_hours", "flag", "source"}
    assert resin["flag"] == "unsourced" and resin["source"] == "mgs-l285-tds:p1"
    assert resin["min_temp_c"] == 10 and resin["gate_hours"] == []


def test_plan_json_six_month_staleness(gdir, tmp_path):
    out = tmp_path / "site"
    build(gdir, out, models=None, scan_base=None, docs=None)
    shipped = json.loads((out / "plan.json").read_text())
    today = date.fromisoformat(shipped["today"])
    cutoff = _months_ago(today)
    for item in shipped["catalog"].values():
        if item["read"] is None:
            assert item["stale"] is True
        else:
            assert item["stale"] is (date.fromisoformat(item["read"]) < cutoff)
    old = (cutoff - timedelta(days=1)).isoformat()

    def row(item_id, label, read, flag, url, price):
        url_yaml = "null" if url is None else f"'{url}'"
        read_yaml = "null" if read is None else read
        price_yaml = "null" if price is None else price
        return (
            f"- {{id: {item_id}, label: {label}, vendor: null, part: null, "
            f"url: {url_yaml}, price_usd: {price_yaml}, unit: each, "
            f"read: {read_yaml}, flag: {flag}}}"
        )

    catalog = tmp_path / "catalog" / "prices.yaml"
    catalog.parent.mkdir()
    catalog.write_text(
        "\n".join(
            [
                row(
                    "fresh",
                    "Fresh",
                    today.isoformat(),
                    "page",
                    "https://example.com/f",
                    1,
                ),
                row(
                    "edge",
                    "Edge",
                    cutoff.isoformat(),
                    "page",
                    "https://example.com/e",
                    1,
                ),
                row("old", "Old", old, "page", "https://example.com/o", 1),
                row("blank", "Blank", None, "unsourced", None, None),
            ]
        )
        + "\n"
    )
    build(
        gdir,
        out,
        models=None,
        scan_base=None,
        docs=None,
        catalog=catalog,
        resins=ROOT / "data" / "resins",
    )
    plan = json.loads((out / "plan.json").read_text())
    assert plan["today"] == today.isoformat()
    assert plan["catalog"]["fresh"]["stale"] is False
    assert plan["catalog"]["edge"]["read"] == cutoff.isoformat()
    assert plan["catalog"]["edge"]["stale"] is False
    assert plan["catalog"]["old"]["stale"] is True
    assert plan["catalog"]["blank"]["read"] is None
    assert plan["catalog"]["blank"]["stale"] is True


def test_lab_build_fails_loudly_without_npm(gdir, tmp_path, monkeypatch):
    import guide.build_site as bs

    monkeypatch.setattr(bs.shutil, "which", lambda name, *a, **k: None)
    with pytest.raises(RuntimeError, match="npm"):
        build(gdir, tmp_path / "site", models=None, scan_base=None, docs=None)
