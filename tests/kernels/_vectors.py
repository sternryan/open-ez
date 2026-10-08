"""Shared loader for the published test vectors in tests/kernels/vectors."""

from pathlib import Path

import numpy as np
import yaml

VEC = Path(__file__).resolve().parent / "vectors"


def load(name: str) -> dict:
    return yaml.safe_load((VEC / name).read_text())


def printed_close(actual, printed) -> bool:
    """True when every value matches its printed figure to half a unit in the 4th significant digit.

    The vectors print four significant figures; a printed 0 must be zero to 1e-9 of the largest entry.
    """
    a, p = np.asarray(actual, float), np.asarray(printed, float)
    if a.shape != p.shape:
        return False
    mag = np.where(p == 0.0, 1.0, np.abs(p))
    tol = np.where(
        p == 0.0, 1e-9 * np.max(np.abs(p)), 0.5 * 10.0 ** (np.floor(np.log10(mag)) - 3)
    )
    return bool(np.all(np.abs(a - p) <= tol * (1 + 1e-9)))
