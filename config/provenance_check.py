"""Rules for a geometry-provenance table, callable on any dict (the shipped one or a broken one)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping

from config.aircraft_config import PROVENANCE_STATUSES

ENTRY_KEYS = {"status", "source", "confidence", "note"}
CONFIDENCES = {"high", "medium", "low", "n/a"}
SOURCED_STATUSES = {"book", "cp-corrected", "derived"}


def validate_provenance(
    provenance: Mapping[str, Mapping],
    fields: Iterable[str],
    check_citation: Callable[[str], object] | None = None,
) -> list[str]:
    """Return every rule violation (empty list = clean).

    Rules: every field has an entry, no entry for a field that no longer exists, each entry has exactly
    the four keys, a known status and confidence, a book/cp-corrected/derived entry has a source, and
    (when check_citation is given) that source passes the registry check.
    """
    fields = set(fields)
    errors: list[str] = []
    missing = sorted(fields - set(provenance))
    if missing:
        errors.append(f"missing provenance entries: {missing}")
    stale = sorted(set(provenance) - fields)
    if stale:
        errors.append(f"stale provenance entries: {stale}")
    for name, e in provenance.items():
        if set(e) != ENTRY_KEYS:
            errors.append(f"{name}: keys {sorted(e)} != {sorted(ENTRY_KEYS)}")
            continue
        if e["status"] not in PROVENANCE_STATUSES:
            errors.append(f"{name}: unknown status {e['status']!r}")
        if e["confidence"] not in CONFIDENCES:
            errors.append(f"{name}: unknown confidence {e['confidence']!r}")
        if e["status"] in SOURCED_STATUSES:
            if not str(e["source"]).strip():
                errors.append(f"{name}: a {e['status']} value needs a source")
            elif check_citation is not None:
                try:
                    check_citation(e["source"])
                except Exception as exc:  # the registry raises on unknown id or bad form
                    errors.append(f"{name}: bad citation {e['source']!r}: {exc}")
    return errors
