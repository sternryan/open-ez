"""Block 3 M3.4 inputs freeze: sha256 of every input the canard equivalence reads (ledger row 74).

Each hash covers one input group, serialised as canonical JSON. A changed hash means a changed input,
which needs a new ledger row before any equivalence number is recomputed.
"""

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOK_MATERIALS = ("bid_7725_wet", "und_7715_wet")
CARBON_MATERIALS = ("carbon3k_mgs418_wet",)
STIFFNESS_FLAG_FRACTION = 0.10  # captain choice, unsourced (sizing rule, "Thresholds")


def _sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text())


def input_groups() -> dict:
    mats = _yaml("data/materials.yaml")["materials"]
    book = _yaml("data/laminates/canard_book.yaml")
    ledger_mats = _yaml("data/mass_ledger.yaml")["materials"]
    return {
        "sizing_rule": (ROOT / "docs/harness/block3-sizing-rule.md").read_text(),
        "book_lamina": {m: mats[m] for m in BOOK_MATERIALS},
        "carbon_lamina": {m: mats[m] for m in CARBON_MATERIALS},
        "book_plies": book["plies"],
        "cell_geometry": book["geometry"],
        "mass_inputs": {
            "cloth": ledger_mats["cloth"],
            "resin_to_cloth_weight": ledger_mats["resin_to_cloth_weight"],
            "core_foam_density": book["geometry"]["core_foam_density"],
        },
        "stiffness_flag_fraction": STIFFNESS_FLAG_FRACTION,
    }


def inputs_sha256() -> dict[str, str]:
    return {k: _sha(v) for k, v in input_groups().items()}
