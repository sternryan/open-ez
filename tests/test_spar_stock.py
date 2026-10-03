"""Independent published dimensions for unplaced chapter 14 stock."""

import pytest

from core.spar_stock import SPAR_LWA_COUNTS, lwa_stock, spruce_stock


def dimensions(shape):
    bb = shape.val().BoundingBox()
    return bb.xlen, bb.ylen, bb.zlen


def test_lwa_stock_uses_spar_counts_and_corrected_published_dimensions():
    stock = lwa_stock()
    expected = {
        "LWA1": (6, (2.0, 1.5, 0.125)),
        "LWA2": (2, (2.0, 2.5, 0.125)),
        "LWA3": (2, (2.0, 6.4, 0.125)),
        "LWA4": (4, (2.0, 1.75, 0.25)),
        "LWA5": (2, (2.0, 2.25, 0.25)),
    }
    assert len(stock) == 16
    for kind, (count, dims) in expected.items():
        blanks = [blank for name, blank in stock.items() if name.startswith(f"{kind}.")]
        assert len(blanks) == count
        for blank in blanks:
            assert dimensions(blank.solid) == pytest.approx(dims)
            assert blank.solid.val().Volume() == pytest.approx(
                dims[0] * dims[1] * dims[2]
            )
            assert blank.solid.val().isValid()
            assert "plans-1980:p90" in blank.cite
            assert ("cp-text:p43" in blank.cite) == (kind in {"LWA4", "LWA5"})


def test_spruce_stock_has_four_one_by_one_by_three_blanks():
    stock = spruce_stock()
    assert len(stock) == 4
    for blank in stock.values():
        assert dimensions(blank.solid) == pytest.approx((1.0, 1.0, 3.0))
        assert blank.solid.val().Volume() == pytest.approx(3.0)
        assert blank.solid.val().isValid()
        assert blank.cite == ("plans-1980:p86",)


def test_stock_has_explicit_eligibility_and_no_airplane_transforms():
    for blank in [*lwa_stock().values(), *spruce_stock().values()]:
        assert blank.eligibility == "stock-only"
        assert "installed placement" in blank.note
        bb = blank.solid.val().BoundingBox()
        assert (bb.xmin, bb.ymin, bb.zmin) == pytest.approx((0.0, 0.0, 0.0))


def test_chapter_specific_quantity_mapping_cannot_be_mutated():
    with pytest.raises(TypeError):
        SPAR_LWA_COUNTS["LWA2"] = 4
