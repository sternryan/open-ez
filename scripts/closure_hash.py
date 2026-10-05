"""Print the sha256 of the frozen closure block (record it in the geometry ledger)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.closure import block_sha256  # noqa: E402

print(block_sha256())
