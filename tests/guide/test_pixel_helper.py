"""The pixel tests read images through pixels(), not the Image.getdata that Pillow removes in 14."""

import re
import warnings
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent


def test_no_guide_test_calls_deprecated_image_getdata():
    this = Path(__file__).name
    hits = [
        p.name
        for p in HERE.glob("*.py")
        if p.name != this and re.search(r"\.getdata\(", p.read_text())
    ]
    assert hits == []


def test_pixels_matches_getdata_without_warning():
    from tests.guide.render_fixture import pixels

    rgb = Image.new("RGB", (3, 2))
    rgb.putpixel((1, 0), (10, 20, 30))
    gray = rgb.convert("L")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert pixels(rgb)[1] == (10, 20, 30) and len(pixels(rgb)) == 6
        assert pixels(gray) == [gray.getpixel((x, y)) for y in range(2) for x in range(3)]
