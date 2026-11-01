import pytest

from guide.check import main
from tests.guide.test_plan_fields import with_plan
from tests.guide.test_schema import gdir as _schema_gdir

_graph_dir = pytest.fixture(name="gdir")(_schema_gdir.__wrapped__)


def src_env(
    tmp_path,
    monkeypatch,
    cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nthis is a long enough text with many words to generate shingles for the overlap check\nx\n",
):
    cp = tmp_path / "cp.txt"
    cp.write_text(cp_text)
    cob = tmp_path / "cobelu" / "I" / "md"
    cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text(
        "### STEP 1 -\nthis is a long enough text with many words to generate shingles\n"
    )
    scan = tmp_path / "scan"
    scan.mkdir()
    (scan / "058.txt").write_text(
        "this is a long enough text with many words to generate shingles"
    )
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))


def test_schema_only_passes(gdir):
    assert main(["--graph", str(gdir), "--schema-only"]) == 0


def test_full_mode_missing_sources_exits_2(gdir, monkeypatch):
    for v in ("LONGEZ_CP_SECTIONS", "LONGEZ_COBELU_DIR", "LONGEZ_SCAN_TEXT_DIR"):
        monkeypatch.delenv(v, raising=False)
    assert main(["--graph", str(gdir)]) == 2


def test_full_mode_green(gdir, tmp_path, monkeypatch):
    src_env(tmp_path, monkeypatch)
    assert main(["--graph", str(gdir)]) == 0


def test_overlap_fails(gdir, tmp_path, monkeypatch, capsys):
    src_env(
        tmp_path,
        monkeypatch,
        cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nhot wire the four canard cores from the templates today\n",
    )
    assert main(["--graph", str(gdir)]) == 1
    assert "c10.cores.summary" in capsys.readouterr().out


def test_recall_miss_fails(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\n")
    assert main(["--graph", str(gdir)]) == 1
    assert "recall" in capsys.readouterr().out.lower()


def test_empty_cobelu_md_dir_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"
    cp.write_text("THE CANARD PUSHER NO. 25 JULY 80\n")
    cob = tmp_path / "cobelu" / "I" / "md"
    cob.mkdir(parents=True)
    scan = tmp_path / "scan"
    scan.mkdir()
    (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "no *.md" in capsys.readouterr().out


def test_empty_scan_dir_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"
    cp.write_text("THE CANARD PUSHER NO. 25 JULY 80\n")
    cob = tmp_path / "cobelu" / "I" / "md"
    cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"
    scan.mkdir()
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "no *.txt" in capsys.readouterr().out


def test_empty_cp_file_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"
    cp.write_text("")
    cob = tmp_path / "cobelu" / "I" / "md"
    cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"
    scan.mkdir()
    (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "empty" in capsys.readouterr().out.lower()


def test_cp_sections_pointing_at_directory_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp_dir = tmp_path / "cp_dir"
    cp_dir.mkdir()
    cob = tmp_path / "cobelu" / "I" / "md"
    cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"
    scan.mkdir()
    (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp_dir))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "missing" in capsys.readouterr().out.lower()


def test_chapters_parse_error_exits_2(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch)
    assert main(["--graph", str(gdir), "--chapters", "a"]) == 2
    assert "parse error" in capsys.readouterr().out.lower()


def test_overlap_truncates_to_three_words(gdir, tmp_path, monkeypatch, capsys):
    src_env(
        tmp_path,
        monkeypatch,
        cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nhot wire the four canard cores from the templates today\n",
    )
    assert main(["--graph", str(gdir)]) == 1
    out = capsys.readouterr().out
    assert "c10.cores.summary" in out
    # Check that the hit is truncated: should contain "hot wire the…" not the full phrase
    assert "hot wire the…" in out


@pytest.mark.parametrize(
    ("plan", "needle"),
    [
        ("plan:\n  hours: {value: .nan, flag: estimate}\n", "finite"),
        ("plan:\n  hours: {value: .inf, flag: estimate}\n", "finite"),
        ("plan:\n  hours: {value: -1, flag: estimate}\n", ">="),
        (
            "plan:\n  buy: [{item: bid-7725, qty: .nan, flag: estimate}]\n",
            "finite",
        ),
        (
            "plan:\n  buy: [{item: bid-7725, qty: .inf, flag: estimate}]\n",
            "finite",
        ),
        (
            "plan:\n  buy: [{item: bid-7725, qty: -0.5, flag: estimate}]\n",
            ">=",
        ),
    ],
)
def test_check_rejects_bad_plan_numbers(gdir, capsys, plan, needle):
    with_plan(gdir, plan)
    assert main(["--schema-only", "--graph", str(gdir)]) == 1
    assert needle in capsys.readouterr().out


def _point_check_at(monkeypatch, tmp_path, prices: str, resin: str) -> None:
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "prices.yaml").write_text(prices)
    resins = tmp_path / "resins"
    resins.mkdir()
    (resins / "sample.yaml").write_text(resin)
    monkeypatch.setattr("guide.check.DATA", tmp_path)


@pytest.mark.parametrize(
    ("prices", "resin", "needle"),
    [
        (
            "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: .nan, unit: each, read: 2026-10-08, flag: page}\n",
            "id: sample\nsource: null\nmin_temp_c: null\ngate_hours: []\nflag: unsourced\n",
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: .inf, unit: each, read: 2026-10-08, flag: page}\n",
            "id: sample\nsource: null\nmin_temp_c: null\ngate_hours: []\nflag: unsourced\n",
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: 'https://example.com/a', price_usd: -1, unit: each, read: 2026-10-08, flag: page}\n",
            "id: sample\nsource: null\nmin_temp_c: null\ngate_hours: []\nflag: unsourced\n",
            ">=",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            "id: sample\nsource: null\nmin_temp_c: .nan\ngate_hours: []\nflag: unsourced\n",
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            "id: sample\nsource: null\nmin_temp_c: .inf\ngate_hours: []\nflag: unsourced\n",
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            "id: sample\nsource: null\nmin_temp_c: -5\ngate_hours: []\nflag: unsourced\n",
            ">=",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            'id: sample\nsource: "om-1980:p25"\nmin_temp_c: 10\ngate_hours: [[.nan, 24]]\nflag: official\n',
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            'id: sample\nsource: "om-1980:p25"\nmin_temp_c: 10\ngate_hours: [[10, .inf]]\nflag: official\n',
            "finite",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            'id: sample\nsource: "om-1980:p25"\nmin_temp_c: 10\ngate_hours: [[-1, 24]]\nflag: official\n',
            ">=",
        ),
        (
            "- {id: a, label: A, vendor: null, part: null, url: null, price_usd: null, unit: each, read: null, flag: unsourced}\n",
            'id: sample\nsource: "om-1980:p25"\nmin_temp_c: 10\ngate_hours: [[10, -2]]\nflag: official\n',
            ">=",
        ),
    ],
)
def test_check_rejects_bad_catalog_and_resin_numbers(
    gdir, tmp_path, monkeypatch, capsys, prices, resin, needle
):
    _point_check_at(monkeypatch, tmp_path, prices, resin)
    assert main(["--schema-only", "--graph", str(gdir)]) == 1
    assert needle in capsys.readouterr().out


def test_zero_shingles_reads_as_failure(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD\n")
    (tmp_path / "cobelu" / "I" / "md" / "10_CANARD.md").write_text("tiny\n")
    (tmp_path / "scan" / "058.txt").write_text("tiny")
    assert main(["--graph", str(gdir)]) == 2
    out = capsys.readouterr().out
    assert "vacuous gate, FAIL" in out and "passes" not in out
