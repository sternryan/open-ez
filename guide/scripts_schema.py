"""Action vocabulary and step-script checks."""

from __future__ import annotations

from pathlib import Path

import yaml

from guide.schema import Graph, Operation, SchemaError

ACTIONS = (
    "cut",
    "place",
    "wet-out",
    "squeegee",
    "drape",
    "flip",
    "sand",
    "check-level",
    "check-string",
    "bond",
    "wait-cure",
)
PROPS = (
    "squeegee",
    "brush",
    "scissors",
    "hot-wire",
    "level",
    "sanding-block",
    "cup",
    "peel-ply",
    "string-line",
    "stand-in",
)
ACTION_KEYS = {"do", "part", "ply", "tool", "who", "why"}


def _fault(op: str, i: int, detail: str) -> str:
    return f"scripts.yaml {op} action {i}: {detail}"


def _ply_count(plies: object) -> int | None:
    if isinstance(plies, bool) or not isinstance(plies, int):
        return None
    return plies


def _ply_total(op: Operation) -> int:
    """Sum of ``materials[].plies``. Non-integers contribute nothing."""
    total = 0
    for mat in op.materials:
        if not isinstance(mat, dict):
            continue
        count = _ply_count(mat.get("plies", 0))
        if count is not None and count > 0:
            total += count
    return total


def load_scripts(graph_dir: Path) -> dict[str, list[dict]]:
    """Load ``<graph_dir>/scripts.yaml``. A missing file is ``{}``."""
    path = graph_dir / "scripts.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise SchemaError(f"{path.name}: malformed YAML: {e}") from e
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SchemaError(f"{path.name}: must be a mapping, got {type(data).__name__}")
    return data


def _step_tool(op: Operation, tool: str) -> str:
    """The step's own tool, or stand-in when the step does not list it."""
    listed = set(op.plan.tools) if op.plan is not None else set()
    if tool in listed:
        return tool
    return "stand-in"


def _generated(op: Operation) -> list[dict]:
    place: dict = {"do": "place", "who": "owner"}
    if op.components:
        place["part"] = op.components[0]
    actions = [place]
    n = 1
    for mat in op.materials:
        if not isinstance(mat, dict):
            continue
        count = _ply_count(mat.get("plies", 0))
        if count is None or count <= 0:
            continue
        for _ in range(count):
            actions.append(
                {
                    "do": "wet-out",
                    "ply": n,
                    "tool": _step_tool(op, "brush"),
                    "who": "owner",
                }
            )
            actions.append(
                {
                    "do": "squeegee",
                    "ply": n,
                    "tool": _step_tool(op, "squeegee"),
                    "who": "owner",
                }
            )
            n += 1
    return actions


def scripts_for(g: Graph, overrides: dict) -> dict[str, list[dict]]:
    """Place, then wet-out and squeegee for each ply. Overrides replace that list.

    An op with no materials and no override is omitted (caption-only).
    """
    out: dict[str, list[dict]] = {}
    for op_id, op in g.ops.items():
        if op_id in overrides:
            out[op_id] = overrides[op_id]
            continue
        if not op.materials:
            continue
        out[op_id] = _generated(op)
    for op_id, actions in overrides.items():
        if op_id not in out:
            out[op_id] = actions
    return out


def _action_faults(
    op_id: str, i: int, action: object, op: Operation | None, g: Graph
) -> list[str]:
    if not isinstance(action, dict):
        return [_fault(op_id, i, "must be a mapping")]
    faults: list[str] = []
    for key in sorted(action, key=str):
        if key not in ACTION_KEYS:
            faults.append(_fault(op_id, i, f"unknown key {key!r}"))
    do = action.get("do")
    if do not in ACTIONS:
        faults.append(_fault(op_id, i, f"unknown action {do!r}"))
    if op is None:
        faults.append(_fault(op_id, i, "unknown op"))
    if "part" in action and action["part"] not in g.components:
        faults.append(_fault(op_id, i, f"unknown part {action['part']!r}"))
    if "tool" in action and action["tool"] not in PROPS:
        faults.append(_fault(op_id, i, f"unknown tool {action['tool']!r}"))
    elif "tool" in action and action["tool"] != "stand-in":
        listed = set(op.plan.tools) if op is not None and op.plan is not None else set()
        if action["tool"] not in listed:
            faults.append(
                _fault(op_id, i, f"tool {action['tool']!r} is not in the step plan")
            )
    if "ply" in action:
        ply = action["ply"]
        if op is None or not op.materials:
            faults.append(_fault(op_id, i, "ply on an op with no materials"))
        elif isinstance(ply, bool) or not isinstance(ply, int):
            faults.append(_fault(op_id, i, f"ply {ply!r} is not an integer"))
        elif ply < 1:
            faults.append(_fault(op_id, i, f"ply {ply} is below 1"))
        else:
            total = _ply_total(op)
            if ply > total:
                faults.append(_fault(op_id, i, f"ply {ply} is above {total}"))
    who = action.get("who")
    if who not in {"owner", "buddy"}:
        faults.append(_fault(op_id, i, f"who {who!r} is not owner or buddy"))
    elif who == "buddy" and (op is None or op.plan is None or op.plan.people == 1):
        faults.append(_fault(op_id, i, "who buddy needs people 2"))
    return faults


def _wetout_plies(actions: list) -> list[int] | None:
    """Wet-out ply numbers, in order. ``None`` when a ply is not an integer.

    A non-integer ply already has its own fault, so coverage stays quiet.
    """
    plies: list[int] = []
    for action in actions:
        if not isinstance(action, dict) or action.get("do") != "wet-out":
            continue
        if "ply" not in action:
            continue
        ply = action["ply"]
        if isinstance(ply, bool) or not isinstance(ply, int):
            return None
        plies.append(ply)
    return plies


def _coverage_faults(op_id: str, actions: list, op: Operation | None) -> list[str]:
    """An op with materials must wet out plies 1..N in that order."""
    if op is None or not op.materials:
        return []
    got = _wetout_plies(actions)
    if got is None:
        return []
    total = _ply_total(op)
    if got == list(range(1, total + 1)):
        return []
    return [_fault(op_id, 0, f"wet-out plies {got} are not 1..{total} in order")]


def _display_ply(action: object, total: int) -> int | None:
    """Ply that can move the player display, or None.

    ``guide/lab/src/main.ts`` ``targetOf`` (~2011) is ``a?.ply ? targets[a.ply - 1]``.
    ``applyBeat`` (~2117) calls ``setLay`` for that target. ``do`` is not
    consulted: every action carrying an in-range ply can advance the count.
    Ply 0 is falsy in the player, and a ply past the target list has no
    target, so those do not move the display. They already have their own faults.
    """
    if not isinstance(action, dict) or "ply" not in action:
        return None
    ply = action["ply"]
    if isinstance(ply, bool) or not isinstance(ply, int):
        return None
    if ply < 1 or ply > total:
        return None
    return ply


def _ply_display_faults(op_id: str, actions: list, op: Operation | None) -> list[str]:
    """Stay on the current ply, or open the next one only after it is wet out.

    Repeated actions on the current ply are allowed. A lower ply steps back.
    """
    if op is None or not op.materials:
        return []
    total = _ply_total(op)
    current = 0
    wet: set[int] = set()
    faults: list[str] = []
    for i, action in enumerate(actions):
        ply = _display_ply(action, total)
        if ply is None:
            continue
        if current == 0:
            if ply != 1:
                faults.append(_fault(op_id, i, f"ply {ply} before ply 1 is wet out"))
                continue
            current = 1
        elif ply < current:
            faults.append(_fault(op_id, i, f"ply {ply} goes back from ply {current}"))
            continue
        elif ply > current:
            if ply != current + 1 or current not in wet:
                needed = current + 1
                faults.append(
                    _fault(op_id, i, f"ply {ply} before ply {needed} is wet out")
                )
                continue
            current = ply
        if isinstance(action, dict) and action.get("do") == "wet-out":
            wet.add(ply)
    return faults


def validate_scripts(scripts: dict, g: Graph) -> list[str]:
    if not isinstance(scripts, dict):
        return ["scripts.yaml: must be a mapping"]
    errs: list[str] = []
    for op_id, actions in scripts.items():
        op = g.ops.get(op_id)
        if not isinstance(actions, list):
            errs.append(_fault(str(op_id), 0, "must be a list"))
            continue
        for i, action in enumerate(actions):
            errs.extend(_action_faults(str(op_id), i, action, op, g))
        errs.extend(_coverage_faults(str(op_id), actions, op))
        errs.extend(_ply_display_faults(str(op_id), actions, op))
    return errs
