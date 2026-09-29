import shutil
from pathlib import Path
from guide.check import main
from tests.guide.test_schema import gdir  # noqa: F401  (reuse fixture)

def src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nx\n"):
    cp = tmp_path / "cp.txt"; cp.write_text(cp_text)
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("unrelated words")
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
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nhot wire the four canard cores from the templates today\n")
    assert main(["--graph", str(gdir)]) == 1
    assert "c10.cores.summary" in capsys.readouterr().out

def test_recall_miss_fails(gdir, tmp_path, monkeypatch, capsys):
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\n")
    assert main(["--graph", str(gdir)]) == 1
    assert "recall" in capsys.readouterr().out.lower()
