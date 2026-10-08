import math

import numpy as np


def tsai_wu_strength_ratio(
    sigma: np.ndarray,
    F1t: float,
    F1c: float,
    F2t: float,
    F2c: float,
    F6: float,
    f12_star: float,
) -> float:
    """Calculate the Tsai-Wu strength ratio R for a given stress and strengths."""
    if any(s <= 0 for s in [F1t, F1c, F2t, F2c, F6]):
        raise ValueError("All strengths must be positive.")
    if sigma.size != 3:
        raise ValueError("Stress sigma must have 3 components.")

    s1, s2, t12 = sigma

    if s1 == 0 and s2 == 0 and t12 == 0:
        return math.inf

    f1 = 1 / F1t - 1 / F1c
    f2 = 1 / F2t - 1 / F2c
    f11 = 1 / (F1t * F1c)
    f22 = 1 / (F2t * F2c)
    f66 = 1 / (F6**2)
    f12 = f12_star * math.sqrt(f11 * f22)

    a = f11 * s1**2 + f22 * s2**2 + f66 * t12**2 + 2 * f12 * s1 * s2
    b = f1 * s1 + f2 * s2

    if a > 0:
        discriminant = b**2 + 4 * a
        if discriminant < 0:
            raise ValueError("Invalid Tsai-Wu parameters (negative discriminant).")
        return (-b + math.sqrt(discriminant)) / (2 * a)
    elif a == 0:
        if b > 0:
            return 1 / b
        else:
            return math.inf
    else:
        raise ValueError("Invalid Tsai-Wu parameters (a < 0).")
