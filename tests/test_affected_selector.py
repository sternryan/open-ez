"""scripts/test-affected.py: the push-gate --affected selector. Runs it against throwaway git repos."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "test-affected.py"
SMOKE = ["tests/test_smoke_gate.py", "tests/test_sources_registry.py", "tests/test_config_validate_gate.py"]


def sh(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()


def put(repo, rel, text="x = 1\n"):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def make_repo(tmp_path):
    r = tmp_path / "r"
    r.mkdir()
    sh(r, "init", "-q")
    sh(r, "config", "user.email", "t@t")
    sh(r, "config", "user.name", "t")
    for s in SMOKE:
        put(r, s)
    put(r, "core/foo.py")
    put(r, "core/bar.py", "from core import foo\n")
    put(r, "core/lonely.py")
    put(r, "guide/viewer_glue.py", "import core.bar\n")
    put(r, "tests/test_foo.py", "import core.foo\n")
    put(r, "tests/test_bar_extra.py", "from core.bar import y\n")
    put(r, "tests/test_unrelated.py", "import os\n")
    put(r, "tests/test_glue_user.py", "from guide import (\n    other,\n    viewer_glue,\n)\n")
    put(r, "config/aircraft_config.py")
    put(r, "docs/superpowers/plan.md", "a\n")
    put(r, "README.md", "a\n")
    sh(r, "add", "-A")
    sh(r, "commit", "-qm", "base")
    return r, sh(r, "rev-parse", "HEAD")


def select(r, base):
    p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(r), "--base", base, "--print"], capture_output=True, text=True)
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("{") else None), p


def change(r, rel, text="x = 2\n"):
    put(r, rel, text)
    sh(r, "add", "-A")
    sh(r, "commit", "-qm", "c")


def checks(sel):
    return [c.split(":", 1)[1] for c in sel["selected_checks"]]


def test_leaf_module_selects_mirror_dependents_and_smoke(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "core/foo.py")
    rc, sel, _ = select(r, base)
    assert rc == 0 and not sel["full"]
    got = checks(sel)
    assert "tests/test_foo.py" in got                  # mirrors the name / imports it
    assert "tests/test_bar_extra.py" in got            # core.bar imports foo (transitive dependent)
    assert "tests/test_glue_user.py" in got            # guide.viewer_glue imports core.bar; multi-line from-import
    assert "tests/test_unrelated.py" not in got
    for s in SMOKE:
        assert s in got


def test_only_a_test_change_selects_that_test_plus_smoke(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "tests/test_unrelated.py", "import os\n# edit\n")
    rc, sel, _ = select(r, base)
    assert sorted(checks(sel)) == sorted(SMOKE + ["tests/test_unrelated.py"])


def test_unmapped_path_selects_full_suite(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "config/aircraft_config.py")
    rc, sel, _ = select(r, base)
    assert rc == 0 and sel["full"] and checks(sel) == ["full"]
    assert "unmapped:config/aircraft_config.py" in sel["reason"]


def test_module_without_any_test_selects_full_suite(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "core/lonely.py")
    rc, sel, _ = select(r, base)
    assert sel["full"] and "no-test-for:core/lonely.py" in sel["reason"]


def test_docs_only_is_smoke_only(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "docs/superpowers/plan.md", "b\n")
    change(r, "README.md", "b\n")
    rc, sel, _ = select(r, base)
    assert not sel["full"] and sorted(checks(sel)) == sorted(SMOKE)


def test_bad_base_fails_closed_with_exit_2(tmp_path):
    r, _ = make_repo(tmp_path)
    rc, _, p = select(r, "0" * 40)
    assert rc == 2 and "failed" in p.stderr


def test_ids_are_hex_and_evidence_tracks_selection(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "core/foo.py")
    _, a, _ = select(r, base)
    assert len(a["policy_id"]) == 64 and len(a["evidence_id"]) == 64 and a["base_sha"] == base
    change(r, "core/foo.py", "x = 3\n")
    _, b, _ = select(r, base)
    assert a["evidence_id"] != b["evidence_id"]            # different candidate tree
    assert a["policy_id"] == b["policy_id"]


def test_execute_prints_the_lines_push_gate_records(tmp_path):
    r, base = make_repo(tmp_path)
    change(r, "docs/superpowers/plan.md", "b\n")
    # the fake smoke files contain no tests, so pytest exits 5 (nothing collected); the header is what matters
    p = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(r), "--base", base, "--execute"], capture_output=True, text=True)
    for k in ("base_sha: " + base, "policy_id: ", "evidence_id: "):
        assert k in p.stdout, p.stdout
