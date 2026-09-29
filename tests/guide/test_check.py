from pathlib import Path
from guide.check import main
from tests.guide.test_schema import gdir  # noqa: F401  (reuse fixture)

def src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nthis is a long enough text with many words to generate shingles for the overlap check\nx\n"):
    cp = tmp_path / "cp.txt"; cp.write_text(cp_text)
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nthis is a long enough text with many words to generate shingles\n")
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("this is a long enough text with many words to generate shingles")
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

def test_empty_cobelu_md_dir_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"; cp.write_text("THE CANARD PUSHER NO. 25 JULY 80\n")
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "no *.md" in capsys.readouterr().out

def test_empty_scan_dir_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"; cp.write_text("THE CANARD PUSHER NO. 25 JULY 80\n")
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"; scan.mkdir()
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "no *.txt" in capsys.readouterr().out

def test_empty_cp_file_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp = tmp_path / "cp.txt"; cp.write_text("")
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("unrelated words")
    monkeypatch.setenv("LONGEZ_CP_SECTIONS", str(cp))
    monkeypatch.setenv("LONGEZ_COBELU_DIR", str(tmp_path / "cobelu"))
    monkeypatch.setenv("LONGEZ_SCAN_TEXT_DIR", str(scan))
    assert main(["--graph", str(gdir)]) == 2
    assert "empty" in capsys.readouterr().out.lower()

def test_cp_sections_pointing_at_directory_exits_2(gdir, tmp_path, monkeypatch, capsys):
    cp_dir = tmp_path / "cp_dir"; cp_dir.mkdir()
    cob = tmp_path / "cobelu" / "I" / "md"; cob.mkdir(parents=True)
    (cob / "10_CANARD.md").write_text("### STEP 1 -\nnothing\n")
    scan = tmp_path / "scan"; scan.mkdir(); (scan / "058.txt").write_text("unrelated words")
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
    src_env(tmp_path, monkeypatch, cp_text="THE CANARD PUSHER NO. 25 JULY 80\nLPC #16, MEO, Page 10-5.\nhot wire the four canard cores from the templates today\n")
    assert main(["--graph", str(gdir)]) == 1
    out = capsys.readouterr().out
    assert "c10.cores.summary" in out
    # Check that the hit is truncated: should contain "hot wire the…" not the full phrase
    assert "hot wire the…" in out
