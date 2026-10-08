"""Laminate schedules in data/laminates/*.yaml: every ply and geometry value is cited or flagged."""

from pathlib import Path

import pytest
import yaml

from core.sources import check_citation

ROOT = Path(__file__).resolve().parents[1]
LAMINATES = sorted((ROOT / "data/laminates").glob("*.yaml"))
MATERIALS = ROOT / "data/materials.yaml"
REGIONS = {
    "shear_web",
    "spar_cap_bottom",
    "spar_cap_top",
    "skin_bottom",
    "skin_top",
    "elevator_skin",
    "pad",
    "other",
}
FLAGS = {"unsourced", "conflict", "representational"}
STATUSES = {"printed", "unsourced", "conflict", "rule"}
# "rule": set by the Block 3 sizing rule (design schedules only), not read off a page.
HAS_VALUE = {"printed", "rule"}


def _guide_op_ids() -> set[str]:
    ids: set[str] = set()
    for f in (ROOT / "guide/graph").glob("*.yaml"):
        for op in yaml.safe_load(f.read_text()) or []:
            if isinstance(op, dict) and "id" in op:
                ids.add(op["id"])
    return ids


def _material_ids() -> set[str]:
    data = yaml.safe_load(MATERIALS.read_text())
    if isinstance(data, dict):
        data = data.get("materials", data)
    if isinstance(data, dict):
        return set(data)
    return {m["id"] for m in data}


def cite_ok(cite) -> bool:
    if not cite:
        return False
    try:
        check_citation(cite)
    except ValueError:
        return False
    return True


def ply_problems(
    ply: dict, op_ids: set[str], material_ids: set[str] | None
) -> list[str]:
    pid = ply.get("id", "?")
    errs = []
    if material_ids is not None and ply.get("material") not in material_ids:
        errs.append(
            f"{pid}: material {ply.get('material')!r} not in data/materials.yaml"
        )
    if ply.get("region") not in REGIONS:
        errs.append(f"{pid}: region {ply.get('region')!r} not allowed")
    count, flag = ply.get("count"), ply.get("flag")
    if not (
        isinstance(count, int) and not isinstance(count, bool) and count > 0
    ) and not (count is None and flag):
        errs.append(f"{pid}: count must be int>0 or null with a flag")
    if ply.get("op") not in op_ids:
        errs.append(f"{pid}: op {ply.get('op')!r} not in guide/graph")
    if flag is not None and flag not in FLAGS:
        errs.append(f"{pid}: flag {flag!r} not allowed")
    if cite_ok(ply.get("cite")) == bool(flag):
        errs.append(f"{pid}: needs exactly one of a passing cite or a flag")
    if ply.get("cite") and not cite_ok(ply["cite"]):
        errs.append(f"{pid}: citation fails check_citation")
    for key, field in (("angle_status", "angle_deg"), ("extent_status", "bl_from")):
        st = ply.get(key)
        if st not in STATUSES:
            errs.append(f"{pid}: {key} must be one of {sorted(STATUSES)}")
        elif (ply.get(field) is None) != (
            st not in HAS_VALUE
        ) and key == "angle_status":
            errs.append(f"{pid}: {field} null iff {key} is not printed or rule")
        elif key == "extent_status" and (st in HAS_VALUE) != (
            ply.get("bl_from") is not None and ply.get("bl_to") is not None
        ):
            errs.append(
                f"{pid}: bl_from/bl_to numbers iff extent_status printed or rule"
            )
    return errs


def geometry_problems(geom: dict) -> list[str]:
    errs = []
    for name, g in geom.items():
        flag = g.get("flag")
        if flag is not None and flag not in FLAGS:
            errs.append(f"{name}: flag {flag!r} not allowed")
        if cite_ok(g.get("cite")) == bool(flag):
            errs.append(f"{name}: needs exactly one of a passing cite or a flag")
        if g.get("cite") and not cite_ok(g["cite"]):
            errs.append(f"{name}: citation fails check_citation")
        if g.get("value") is None and not flag:
            errs.append(f"{name}: null value needs a flag")
    return errs


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_laminate_files_exist():
    assert LAMINATES, "no data/laminates/*.yaml"


@pytest.mark.parametrize("path", LAMINATES, ids=lambda p: p.name)
def test_header_and_reread(path):
    d = _load(path)
    assert d.get("reread") in {"pending", "done"}
    assert d.get("frame") and d.get("units") == "in" and d.get("sources")


@pytest.mark.parametrize("path", LAMINATES, ids=lambda p: p.name)
def test_plies(path):
    d = _load(path)
    if MATERIALS.exists():
        mats = _material_ids()
    else:
        pytest.skip("data/materials.yaml does not exist yet")
    errs = []
    ids = [p["id"] for p in d["plies"]]
    assert len(ids) == len(set(ids)), "duplicate ply ids"
    for ply in d["plies"]:
        errs += ply_problems(ply, _guide_op_ids(), mats)
    assert not errs, "\n".join(errs)


@pytest.mark.parametrize("path", LAMINATES, ids=lambda p: p.name)
def test_plies_without_materials_check(path):
    """Everything except the material-id lookup, which needs data/materials.yaml."""
    d = _load(path)
    errs = []
    for ply in d["plies"]:
        errs += ply_problems(ply, _guide_op_ids(), None)
    assert not errs, "\n".join(errs)


@pytest.mark.parametrize("path", LAMINATES, ids=lambda p: p.name)
def test_geometry(path):
    d = _load(path)
    assert not geometry_problems(d["geometry"])


def test_canard_config_fields_flagged_like_provenance():
    from config.aircraft_config import GEOMETRY_PROVENANCE

    geom = _load(ROOT / "data/laminates/canard_book.yaml")["geometry"]
    for name, g in geom.items():
        if "config_field" in g:
            assert GEOMETRY_PROVENANCE[g["config_field"]]["status"] == g["flag"], name


def test_broken_ply_fails():
    ops = _guide_op_ids()
    good = {
        "id": "x",
        "region": "pad",
        "material": "m",
        "count": 1,
        "op": "r30.shear-web",
        "cite": "cobelu:p10 ch30",
        "flag": None,
        "angle_deg": 0,
        "angle_status": "printed",
        "bl_from": 0,
        "bl_to": 1,
        "extent_status": "printed",
    }
    assert ply_problems(good, ops, {"m"}) == []
    assert ply_problems({**good, "cite": None}, ops, {"m"})  # neither cite nor flag
    assert ply_problems({**good, "flag": "unsourced"}, ops, {"m"})  # both
    assert ply_problems({**good, "cite": "nosuch:p1"}, ops, {"m"})
    assert ply_problems({**good, "count": None}, ops, {"m"})
    assert ply_problems({**good, "region": "wing"}, ops, {"m"})
    assert ply_problems({**good, "op": "r99.nope"}, ops, {"m"})
    assert ply_problems({**good, "material": "zz"}, ops, {"m"})


def test_broken_geometry_fails():
    assert geometry_problems({"a": {"value": 1, "cite": None, "flag": None}})
    assert geometry_problems(
        {"a": {"value": None, "cite": "cobelu:p1 ch30", "flag": None}}
    )


def test_book_schedules_have_no_rule_values():
    """A book schedule is read off pages; only a design schedule may carry sizing-rule values."""
    for path in LAMINATES:
        d = _load(path)
        if d.get("kind") == "design":
            continue
        for ply in d["plies"]:
            assert "rule" not in (ply.get("angle_status"), ply.get("extent_status")), (
                ply["id"]
            )


def test_design_schedules_use_design_materials_only():
    mats = yaml.safe_load(MATERIALS.read_text())["materials"]
    for path in LAMINATES:
        d = _load(path)
        if d.get("kind") != "design":
            continue
        kept = set(d.get("kept_from_book", []))
        for ply in d["plies"]:
            assert mats[ply["material"]]["use"] == "design-proxy", ply["id"]
            assert ply["id"] not in kept
