"""Reference values the model may treat as truth: confirmed or derived entries only."""
TRUTH = {"confirmed", "derived"}


def truth_specs(ref: dict) -> dict[str, dict]:
    return {k: e for k, e in ref["aircraft_specs"].items() if e.get("status") in TRUTH}


def truth_airfoil(ref: dict) -> dict[str, dict[str, dict]]:
    """Confirmed/derived airfoil value entries only, per airfoil (unverified excluded)."""
    out: dict[str, dict[str, dict]] = {}
    for name, af in ref["airfoil_data"].items():
        out[name] = {
            k: e
            for k, e in af.items()
            if isinstance(e, dict) and e.get("status") in TRUTH
        }
    return out
