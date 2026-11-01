"""
FAA amateur-built credit audit (14 CFR 21.191(g), cfr14-21-191-2011:p2).

Reads REAL builder task completions from data/compliance_progress.yaml and reports
the builder-credited share of the whole job against the 51% major-portion bar.
Nothing is simulated: with no recorded build the credit is 0.0%.

Modes:
  default             report; exit 0 unless the inputs have integrity errors
  --require-eligible  also exit 1 when credit is below 51% (the gate for an actual
                      airworthiness application)

Usage (from the repo root, no PYTHONPATH needed):
  python scripts/compliance_audit.py [--progress PATH] [--out-dir DIR] [--require-eligible]
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from core.compliance import ComplianceTracker, ManufacturingMethod  # noqa: E402

CITATION = "cfr14-21-191-2011:p2"
DEFAULT_PROGRESS = Path("data/compliance_progress.yaml")
DEFAULT_OUT_DIR = Path("output/compliance")


def _parse_iso(text: str) -> Optional[datetime]:
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def load_progress(tracker: ComplianceTracker, path: Path) -> List[str]:
    """Apply recorded completions to the tracker; return integrity errors."""
    errors: List[str] = []
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"cannot read progress file {path.name}: {exc}"]
    if not isinstance(doc, dict) or not isinstance(doc.get("completed"), list):
        return [f"{path.name}: top level must be a mapping with a `completed` list"]

    methods = {m.value: m for m in ManufacturingMethod}
    seen = set()
    for i, entry in enumerate(doc["completed"]):
        where = f"completed[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: entry must be a mapping")
            continue
        raw_id = entry.get("task_id")
        task_id = raw_id if isinstance(raw_id, str) else ""
        where = f"completed[{i}] ({raw_id})"
        if task_id in seen:
            errors.append(f"{where}: duplicate task_id")
            continue
        seen.add(task_id)
        raw_method = entry.get("method")
        method = methods.get(raw_method) if isinstance(raw_method, str) else None
        evidence = entry.get("evidence")
        ok = True
        try:
            tracker.get_task(task_id)
        except (ValueError, TypeError):
            errors.append(f"{where}: unknown task_id")
            ok = False
        if method is None:
            errors.append(f"{where}: unknown method {entry.get('method')!r}")
            ok = False
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"{where}: evidence missing or empty")
            ok = False
        when = entry.get("date")
        if isinstance(when, datetime):
            when_dt: Optional[datetime] = when
        elif isinstance(when, date):
            when_dt = datetime(when.year, when.month, when.day)
        elif isinstance(when, str) and _parse_iso(when) is not None:
            when_dt = _parse_iso(when)
        else:
            errors.append(f"{where}: date missing or not YYYY-MM-DD")
            when_dt = None
            ok = False
        if ok and method is not None and isinstance(evidence, str):
            tracker.complete_task(task_id, method, notes=evidence.strip())
            tracker.get_task(task_id).completion_date = when_dt
    return errors


def run(argv: Optional[List[str]] = None) -> Tuple[int, str]:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--progress", type=Path, default=DEFAULT_PROGRESS)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--require-eligible", action="store_true")
    args = ap.parse_args(argv)

    progress = args.progress
    if not progress.is_absolute():
        progress = REPO_ROOT / progress

    tracker = ComplianceTracker()  # fresh per run; never the module singleton
    errors = tracker.integrity_errors() + load_progress(tracker, progress)
    for err in errors:
        print(f"INTEGRITY ERROR: {err}", file=sys.stderr)
    if errors:
        return 1, "integrity errors; no report written"

    frac = tracker.total_credit
    n_done = len(tracker.get_completed_tasks())
    recorded = f"{n_done} task(s) recorded" if n_done else "no build recorded"
    print(
        f"Builder credit {frac:.1%} of the job; threshold "
        f"{tracker.REQUIRED_CREDIT:.1%}; {recorded} ({CITATION})"
    )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report = tracker.generate_report() + (
        f"\nBasis: 14 CFR 21.191(g), major portion fabricated and assembled by the "
        f"builder ({CITATION}). Credit is real recorded builder work only.\n"
    )
    report_file = out_dir / "FAA_compliance_audit.md"
    report_file.write_text(report, encoding="utf-8")
    json_file = tracker.export_json(out_dir)
    print(f"Report: {report_file}")
    print(f"JSON: {json_file}")

    if tracker.is_compliant:
        print("Status: ELIGIBLE (credit at or above threshold)")
    else:
        print("Status: NOT YET ELIGIBLE (credit below threshold)")
        if args.require_eligible:
            print(
                "FAILED: --require-eligible and credit below threshold", file=sys.stderr
            )
            return 1, "below threshold"
    return 0, "ok"


def main() -> None:
    code, _ = run()
    sys.exit(code)


if __name__ == "__main__":
    main()
