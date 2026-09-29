"""Reference values the model may treat as truth: confirmed or derived entries only."""
TRUTH = {"confirmed", "derived"}


def truth_specs(ref: dict) -> dict[str, dict]:
    return {k: e for k, e in ref["aircraft_specs"].items() if e.get("status") in TRUTH}
