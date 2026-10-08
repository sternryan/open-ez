"""Every material property is either cited to a registered source page or flagged.

The flags are `unsourced` and `requires_original_test` (ledger row 77); the second carries its search
evidence, its closing test and a link to the Block 5 coupon test plan.
"""

from pathlib import Path

import pytest

from core.materials import FLAGS, PROPERTIES, USES, check_material_set, load_materials
from core.sources import check_citation


def _prop(**kw):
    return {"value": 1.0, "units": "psi", **kw}


def _set(prop, use="design-proxy"):
    return {"use": use, "properties": {k: dict(prop) for k in PROPERTIES}}


def test_shipped_materials_file_is_clean():
    mats = load_materials()
    assert {
        "as4_8552",
        "mtm45_7781",
        "bgf7781_mgs418_wet",
        "carbon3k_mgs418_wet",
        "bid_7725_wet",
        "und_7715_wet",
        "legacy_uni_glass",
        "legacy_bid_glass",
    } <= set(mats)
    for name, m in mats.items():
        check_material_set(name, m)
        assert set(m["properties"]) == set(PROPERTIES), name
        for p in m["properties"].values():
            if "cite" in p:
                check_citation(p["cite"])


def test_cited_and_flagged_properties_pass():
    check_material_set("ok", _set(_prop(cite="om-1980:p23")))
    check_material_set("ok", _set({"value": None, "units": "psi", "flag": "unsourced"}))


def test_property_with_neither_fails():
    with pytest.raises(ValueError, match="neither"):
        check_material_set("bad", _set(_prop()))


def test_property_with_both_fails():
    with pytest.raises(ValueError, match="both"):
        check_material_set("bad", _set(_prop(cite="om-1980:p23", flag="unsourced")))


def test_unknown_citation_fails():
    with pytest.raises(ValueError, match="not-a-source"):
        check_material_set("bad", _set(_prop(cite="not-a-source:p1")))


def test_use_must_be_known():
    assert set(USES) == {"validation", "design-proxy", "book", "legacy"}
    with pytest.raises(ValueError, match="use"):
        check_material_set("bad", _set(_prop(cite="om-1980:p23"), use="whatever"))


def test_all_unsourced_set_cannot_be_validation():
    flagged = {"value": None, "units": "psi", "flag": "unsourced"}
    with pytest.raises(ValueError, match="validation"):
        check_material_set("bad", _set(flagged, use="validation"))
    check_material_set("fine", _set(flagged, use="book"))


def test_unknown_material_raises_instead_of_falling_back():
    # The legacy fea_adapter silently used UNI glass for an unknown name (Block 3 spec section 3).
    import pytest as _pytest

    from core.materials import get_material

    assert get_material("as4_8552")["use"] == "validation"
    with _pytest.raises(KeyError, match="no_such_cloth"):
        get_material("no_such_cloth")


# ---- requires_original_test (ledger row 77) ----------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/superpowers/specs/2026-10-08-block5-coupon-test-plan.md"


def _rot(**kw):
    p = {
        "value": None,
        "units": "psi",
        "flag": "requires_original_test",
        "search": "searched: X, Y; why none is public",
        "closing_test": {"method": "ASTM D3039/D3039M", "coupon": "B5-CPW-T0"},
        "test_plan": PLAN,
    }
    p.update(kw)
    return {k: v for k, v in p.items() if v is not ...}


def test_requires_original_test_is_a_distinct_flag():
    assert FLAGS == ("unsourced", "requires_original_test")
    check_material_set("ok", _set(_rot()))


@pytest.mark.parametrize("field", ["search", "closing_test", "test_plan"])
def test_requires_original_test_must_carry_evidence_test_and_plan(field):
    with pytest.raises(ValueError, match=field):
        check_material_set("bad", _set(_rot(**{field: ...})))


def test_requires_original_test_cannot_hold_a_value():
    with pytest.raises(ValueError, match="null"):
        check_material_set("bad", _set(_rot(value=1.0)))


@pytest.mark.parametrize(
    "test",
    [
        {"method": "tension test", "coupon": "B5-CPW-T0"},
        {"method": "ASTM D3039/D3039M", "coupon": "CPW-T0"},
        {"method": "ASTM D3039/D3039M", "coupon": "B5-CPW-T45"},
    ],
)
def test_closing_test_needs_an_astm_method_and_a_coupon_id(test):
    with pytest.raises(ValueError, match="closing_test"):
        check_material_set("bad", _set(_rot(closing_test=test)))


def test_unsourced_cannot_borrow_the_test_fields():
    flagged = {"value": None, "units": "psi", "flag": "unsourced", "closing_test": {}}
    with pytest.raises(ValueError, match="requires_original_test only"):
        check_material_set("bad", _set(flagged))


def test_unknown_flag_fails():
    with pytest.raises(ValueError, match="flag must be"):
        check_material_set("bad", _set({"value": None, "units": "psi", "flag": "tbd"}))


def test_shipped_requires_original_test_is_scoped_and_linked():
    # Only inputs with recorded search evidence carry the flag (row 77); everything else stays
    # unsourced. Adding one is a deliberate edit here plus a new ledger row.
    tagged = {
        f"{name}.{key}": p
        for name, m in load_materials().items()
        for key, p in m["properties"].items()
        if p.get("flag") == "requires_original_test"
    }
    assert set(tagged) == {
        "carbon3k_mgs418_wet.E1",
        "carbon3k_mgs418_wet.nu12",
        "carbon3k_mgs418_wet.F1t",
        "carbon3k_mgs418_wet.F1c",
    }
    for name, p in tagged.items():
        plan = (ROOT / p["test_plan"]).read_text()
        coupon, method = p["closing_test"]["coupon"], p["closing_test"]["method"]
        assert coupon in plan, f"{name}: {coupon} is not in the test plan"
        assert method in plan, f"{name}: {method} is not in the test plan"
        assert "S2 follow-up" in p["search"], name
