from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import yaml

from hangar import matrix as mx
from hangar.mission import apply_effect, load_mission

_LIMITS = ("fwd", "aft", "gross")
_FIELDS = {"fwd": "fwd_margin_in", "aft": "aft_margin_in", "gross": "gross_margin_lb"}
_MAX_PILOTS = 8
_MAX_BAGS = 6
_LABEL_CHARS = 40
_OCCUPANCY_CHARS = 60


def _real(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def _one_line(text, limit: int) -> str:
    flat = str(text).replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ")
    flat = " ".join(flat.split())
    if len(flat) > limit:
        flat = flat[:limit].rstrip()
    return flat


def _pilots(rows) -> list[tuple[str, float]]:
    if not isinstance(rows, list):
        return []
    found = []
    seen: dict[str, int] = {}
    for index, row in enumerate(rows):
        if len(found) >= _MAX_PILOTS:
            break
        if not isinstance(row, dict):
            continue
        weight = _real(row.get("lb"))
        if weight is None or not 30.0 <= weight <= 500.0:
            continue
        fallback = f"pilot {index + 1}"
        label = _one_line(row.get("label", fallback), _LABEL_CHARS) or _one_line(fallback, _LABEL_CHARS)
        seen[label] = seen.get(label, 0) + 1
        if seen[label] > 1:
            suffix = f" ({seen[label]})"
            room = _LABEL_CHARS - len(suffix)
            label = f"{label[:room].rstrip()}{suffix}" if room > 0 else suffix[:_LABEL_CHARS]
        found.append((label, weight))
    return found


def _bags(data: dict) -> list[dict]:
    none = {"id": "none", "label": "no bag", "lb": 0.0}
    if "bags_lb" not in data:
        return [none, dict(mx.public_bags()[1])]
    raw = data["bags_lb"]
    chosen = []
    if isinstance(raw, list):
        number = 0
        for item in raw:
            weight = _real(item)
            if weight is None or weight < 0.0:
                continue
            if len(chosen) >= _MAX_BAGS:
                break
            number += 1
            chosen.append({"id": f"bag{number}", "label": f"bag {number}", "lb": weight})
    else:
        weight = _real(raw)
        if weight is not None and weight >= 0.0:
            chosen.append({"id": "bag", "label": "bag", "lb": weight})
    if not chosen:
        return [none, dict(mx.public_bags()[1])]
    return [none, *chosen]


def _words(text: str) -> str:
    return _one_line(text, _OCCUPANCY_CHARS)


def _occupancies(pilots: list[tuple[str, float]]) -> list[dict]:
    rows = []
    for index, (label, weight) in enumerate(pilots):
        rows.append(
            {
                "id": f"solo-{index}",
                "words": _words(f"{label} solo"),
                "front_lb": weight,
                "rear_lb": 0.0,
            }
        )
    for left, (front_label, front_lb) in enumerate(pilots):
        for right, (rear_label, rear_lb) in enumerate(pilots):
            if left == right:
                continue
            rows.append(
                {
                    "id": f"two-{left}-{right}",
                    "words": _words(f"{front_label} front, {rear_label} rear"),
                    "front_lb": front_lb,
                    "rear_lb": rear_lb,
                }
            )
    return rows


def private_matrix(effect, private_dir):
    if private_dir is None:
        return None
    try:
        loaded = yaml.safe_load((Path(private_dir) / "mission.yaml").read_text())
    except Exception:
        return None
    if not isinstance(loaded, dict):
        return None
    pilots = _pilots(loaded.get("pilots"))
    if not pilots:
        return None
    engine, extras, plants = apply_effect(effect)
    result = mx.build(engine, extras, plants, load_mission(None), _occupancies(pilots), _bags(loaded))
    result["crossings"] = None
    return result


def _rounded(value, places: int):
    if value is None:
        return None
    return round(float(value), places)


def matrix_digest(effect) -> str:
    made = mx.matrix_for_effect(effect)
    payload = {"worst": {}, "cross": {}, "unknown": made["unknown_cells"]}
    for limit in _LIMITS:
        worst = made["worst"][limit]
        if worst is None:
            payload["worst"][limit] = [None, None]
        else:
            payload["worst"][limit] = [worst["id"], _rounded(worst[_FIELDS[limit]], 2)]
        cross = made["crossings"][limit]
        payload["cross"][limit] = [
            _rounded(cross["fails_above_lb"], 1),
            _rounded(cross["fails_below_lb"], 1),
        ]
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _slot(worst, field: str, prec: int, unit: str) -> tuple[str, str]:
    if worst is None:
        return "unknown", "unknown"
    value = worst[field]
    if value < 0:
        text = f"{abs(value):.{prec}f} {unit} outside"
    else:
        text = f"{value:+.{prec}f} {unit}"
    return text, worst["loading"]


def matrix_text(m: dict) -> str:
    fwd, fwd_loading = _slot(m["worst"]["fwd"], "fwd_margin_in", 1, "in")
    aft, aft_loading = _slot(m["worst"]["aft"], "aft_margin_in", 1, "in")
    gross, gross_loading = _slot(m["worst"]["gross"], "gross_margin_lb", 0, "lb")
    phrases = "; ".join(
        f"{label}: {m['crossings'][key]['note']}"
        for label, key in (("forward", "fwd"), ("aft", "aft"), ("gross", "gross"))
    )
    return (
        "Loading matrix over the public range (solo 120 to 220 lb, two up, no baggage or a light bag, "
        "full, mission and reserve fuel, at takeoff and landing; no owner weights). "
        f"Forward limit worst: {fwd} ({fwd_loading}). "
        f"Aft limit worst: {aft} ({aft_loading}). "
        f"Gross worst: {gross} ({gross_loading}). "
        f"Solo pilots {phrases}."
    )
