"""Print the sha256 of each Block 3 M3.4 input group (record them in the geometry ledger, row 74)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.equivalence_inputs import inputs_sha256

for name, digest in inputs_sha256().items():
    print(f"{name} {digest}")
