"""Every material property is either cited to a registered source page or flagged unsourced."""

import pytest

from core.materials import PROPERTIES, USES, check_material_set, load_materials
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
