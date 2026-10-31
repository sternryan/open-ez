"""Push/CI gate: a decided hangar record may not have its decision rewritten in place.

The record validator sees one file. An edit of decision.picks together with the matching
history entry passes it. This compares each decision file with the committed version at a
base ref: a record that was decided there must still exist, keep its old history as a
prefix (appending does not excuse a rewrite), and its whole decision may change only if
the history grew (a reopen and a new decision).

    python scripts/check_decided_records.py [--base HEAD~1] [--root data/hangar]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _git_show(repo: Path, ref: str, rel: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{rel}"], capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def _load(text: str | None) -> dict | None:
    if text is None:
        return None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _base_decision_paths(repo: Path, base: str, root: str) -> list[str]:
    """Decision yaml paths at `base`, same shape as the working-tree glob."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", base, "--", root],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    prefix = root.strip("/") + "/"
    paths = []
    for rel in proc.stdout.splitlines():
        if not rel.startswith(prefix) or not rel.endswith(".yaml"):
            continue
        parts = rel[len(prefix) :].split("/")
        if len(parts) == 3 and parts[1] == "decisions":
            paths.append(rel)
    return paths


def _verify_base(repo: Path, base: str) -> str | None:
    try:
        cmd = ["git", "-C", str(repo), "rev-parse", "--verify", f"{base}^{{commit}}"]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return None
    except (subprocess.CalledProcessError, OSError) as e:
        msg = f"invalid base ref: {base}"
        if hasattr(e, "stderr") and e.stderr:
            msg += f" {e.stderr}"
        return msg


def check(repo: Path, base: str, root: str = "data/hangar") -> list[str]:
    """Problems for every decided record under `root` that was rewritten or removed."""
    lookup_error = _verify_base(repo, base)
    if lookup_error:
        return [lookup_error]

    errors: list[str] = []
    present = {
        path.relative_to(repo).as_posix()
        for path in (repo / root).glob("*/decisions/*.yaml")
    }
    for rel in _base_decision_paths(repo, base, root):
        if rel in present:
            continue
        old = _load(_git_show(repo, base, rel))
        if old is None or old.get("status") != "decided":
            continue
        errors.append(f"{rel}: a decided record was deleted")

    for path in sorted((repo / root).glob("*/decisions/*.yaml")):
        rel = path.relative_to(repo).as_posix()
        old = _load(_git_show(repo, base, rel))
        if old is None or old.get("status") != "decided":
            continue
        new = _load(path.read_text(encoding="utf-8"))
        if new is None:
            errors.append(f"{rel}: a decided record is no longer readable")
            continue
        old_hist = old.get("history") if isinstance(old.get("history"), list) else []
        new_hist = new.get("history") if isinstance(new.get("history"), list) else []
        if new_hist[: len(old_hist)] != old_hist:
            errors.append(f"{rel}: history of a decided record was rewritten, not appended")
        elif new.get("decision") != old.get("decision") and len(new_hist) == len(old_hist):
            errors.append(f"{rel}: decision changed without a new history entry")
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="HEAD~1")
    ap.add_argument("--root", default="data/hangar")
    args = ap.parse_args(argv)
    errors = check(PROJECT_ROOT, args.base, args.root)
    for err in errors:
        print(err)
    if errors:
        return 1
    print("decided records: no in-place rewrites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
