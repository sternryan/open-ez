#!/usr/bin/env python3
"""Select the pytest files affected by BASE...HEAD (push-gate --affected contract).

Selection (fail closed; every success is non-empty):
  * a changed .py under core/, guide/, hangar/  -> tests that mirror it by name (tests/**/test_<mod>*.py)
    and tests that import it, for the module and (transitively) every in-repo module that imports it;
  * a changed tests/**/test_*.py                -> that file;
  * always: the SMOKE tests below (fast structural/provenance gates);
  * anything else (config/, data/, requirements*, pyproject, conftest, scripts/, workflows, non-.py files
    under core/guide/hangar, the viewer, this selector...) is unmapped -> the FULL suite;
  * docs/superpowers/**, docs/harness/**, docs/history/** and top-level *.md carry no test input -> ignored.
A changed module with no related test also selects the full suite (a silent empty mapping is a gap).
policy_id = sha256(this file). The narrow run is NOT a full-suite green: the full suite stays required
nightly and before releases (AGENTS.md).

usage: test-affected.py --base SHA [--repo .] [--staged] (--print | --execute)
Exit: 0 ok, 2 fail closed, otherwise the failing check's code.
--print emits the selection JSON (base_sha, policy_id, evidence_id, selected_checks, reason, full, ...).
--execute prints `base_sha:`/`policy_id:`/`evidence_id:` lines (what push-gate records) then runs pytest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SMOKE = [
    "tests/test_smoke_gate.py",
    "tests/test_sources_registry.py",
    "tests/test_config_validate_gate.py",
]
PKGS = ("core", "guide", "hangar")
IGNORED_PREFIXES = ("docs/superpowers/", "docs/harness/", "docs/history/")
MAP_VERSION = "open-ez-1"


class Closed(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise Closed(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def changed_paths(repo: Path, base: str, staged: bool = False) -> list[str]:
    git(repo, "cat-file", "-e", f"{base}^{{commit}}")
    if staged:  # pre-commit: the change under test is the index vs HEAD
        out = git(repo, "diff", "--cached", "--name-only", "--no-renames", base)
        return sorted(p for p in out.splitlines() if p)
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", base, "HEAD"]).returncode != 0:
        raise Closed(f"base is not an ancestor of HEAD: {base}")
    out = git(repo, "diff", "--name-only", "--no-renames", f"{base}...HEAD")
    return sorted(p for p in out.splitlines() if p)


def dotted(path: str) -> str:
    return path[:-3].replace("/", ".")


def module_pat(path: str) -> re.Pattern:
    """Matches text that imports module `path` (pkg/sub/mod.py), in any common import spelling."""
    parts = dotted(path).split(".")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    full = r"\.".join(map(re.escape, parts))
    leaf = re.escape(parts[-1])
    parent = r"\.".join(map(re.escape, parts[:-1]))
    alts = [rf"\b{full}\b"]
    if parent:  # `from pkg import mod`, incl. multi-line / parenthesised lists and `import pkg.sub as x` users
        alts.append(rf"\bfrom\s+{parent}\s+import\b[^\n]*\b{leaf}\b")
        alts.append(rf"\bfrom\s+{parent}\s+import\s*\([^)]*\b{leaf}\b")
    return re.compile("|".join(alts))


def all_py(repo: Path) -> list[str]:
    files = git(repo, "ls-files", "*.py").splitlines()
    return [f for f in files if f]


def affected_modules(repo: Path, seeds: set[str]) -> set[str]:
    """Reverse-import closure over core/guide/hangar/scripts sources (module path strings)."""
    srcs = [f for f in all_py(repo) if f.split("/")[0] in PKGS + ("scripts",)]
    text = {f: (repo / f).read_text(errors="replace") for f in srcs if (repo / f).exists()}
    seen, todo = set(seeds), list(seeds)
    while todo:
        cur = todo.pop()
        pat = module_pat(cur)
        for f, t in text.items():
            if f not in seen and pat.search(t):
                seen.add(f)
                todo.append(f)
    return seen


def tests_for(repo: Path, mods: set[str]) -> tuple[set[str], list[str]]:
    tests = [f for f in all_py(repo) if f.startswith("tests/") and Path(f).name.startswith("test_")]
    text = {f: (repo / f).read_text(errors="replace") for f in tests if (repo / f).exists()}
    picked: set[str] = set()
    unmatched: list[str] = []
    for m in sorted(mods):
        if m.split("/")[0] not in PKGS:
            continue
        stem = Path(m).stem
        pat = module_pat(m)
        hit = {f for f, t in text.items() if re.match(rf"test_{re.escape(stem)}(_|\.|$)", Path(f).name) or pat.search(t)}
        if hit:
            picked |= hit
        else:
            unmatched.append(m)
    return picked, unmatched


def select(repo: Path, base: str, staged: bool = False) -> dict:
    changed = changed_paths(repo, base, staged)
    head = git(repo, "rev-parse", "HEAD").strip()
    tree = git(repo, "write-tree").strip() if staged else git(repo, "rev-parse", "HEAD^{tree}").strip()
    reasons: list[str] = []
    full = False
    seeds: set[str] = set()
    tests: set[str] = set(SMOKE)
    for p in changed:
        top = p.split("/")[0]
        if p.startswith(IGNORED_PREFIXES) or ("/" not in p and p.endswith(".md")):
            reasons.append(f"ignored:{p}")
        elif p.startswith("tests/") and Path(p).name.startswith("test_") and p.endswith(".py"):
            if (repo / p).exists():
                tests.add(p)
            reasons.append(f"test:{p}")
        elif top in PKGS and p.endswith(".py"):
            seeds.add(p)
            reasons.append(f"module:{p}")
        else:
            full = True
            reasons.append(f"unmapped:{p}")
    if seeds:
        mods = affected_modules(repo, seeds)
        picked, _ = tests_for(repo, mods)
        tests |= picked
        # a changed (seed) module with no related test at all is a gap -> full
        _, seed_unmatched = tests_for(repo, seeds)
        for m in seed_unmatched:
            full = True
            reasons.append(f"no-test-for:{m}")
    if full:
        checks = ["pytest:full"]
    else:
        checks = sorted(f"pytest:{t}" for t in tests if (repo / t).exists())
    if not checks:
        raise Closed("fail closed: empty selection")
    sel = {
        "ok": True,
        "candidate_sha": head,
        "candidate_tree": tree,
        "base_sha": base,
        "map_version": MAP_VERSION,
        "policy_id": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "selected_checks": checks,
        "changed_paths": changed,
        "reason": "; ".join(sorted(set(reasons))) or "no-changes",
        "full": full,
        "tradeoff": "A narrow run is not a full-suite green; the full suite is required nightly and before releases.",
    }
    body = {k: sel[k] for k in ("base_sha", "candidate_sha", "candidate_tree", "full", "map_version", "policy_id", "selected_checks")}
    sel["evidence_id"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return sel


def execute(repo: Path, sel: dict) -> int:
    for k in ("base_sha", "policy_id", "evidence_id"):
        print(f"{k}: {sel[k]}")
    print(f"full: {str(sel['full']).lower()}")
    print(f"reason: {sel['reason']}")
    print(f"tradeoff: {sel['tradeoff']}", flush=True)
    args = [sys.executable, "-m", "pytest", "-q"]
    if not sel["full"]:
        files = [c.split(":", 1)[1] for c in sel["selected_checks"]]
        print("selected_checks:\n" + "\n".join(f"- {f}" for f in files), flush=True)
        args += files
    return subprocess.run(args, cwd=str(repo)).returncode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--print", dest="do_print", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--staged", action="store_true", help="select for the staged change vs --base (pre-commit hook)")
    a = ap.parse_args(argv)
    if not (a.do_print or a.execute):
        print("fail closed: pass --print or --execute", file=sys.stderr)
        return 2
    repo = Path(a.repo).resolve()
    try:
        sel = select(repo, a.base, a.staged)
    except Closed as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # fail closed on anything unexpected
        print(f"fail closed: {e}", file=sys.stderr)
        return 2
    if a.execute:
        return execute(repo, sel)
    print(json.dumps(sel, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
