from guide.cobelu_markers import parse_markers, chapter_from_filename

MD = """# CHAPTER 10
### STEP 1 -
Place one {CP27 PC44 MEO} of your blocks.
### STEP 2 -
Mark a WL line {CP25 PC16 MEO} and also {CP 26 LPC 36 DES}.
"""

def test_markers_with_heading_context():
    ms = parse_markers(MD, 10)
    assert [(m.cp, m.lpc, m.cls, m.heading) for m in ms] == [
        (27, 44, "MEO", "STEP 1 -"), (25, 16, "MEO", "STEP 2 -"), (26, 36, "DES", "STEP 2 -")]
    assert ms[0].line == 3 and all(m.chapter == 10 for m in ms)

def test_chapter_from_filename():
    assert chapter_from_filename("10_CANARD CONSTRUCTION.md") == 10
    assert chapter_from_filename("30_R1149MS CANARD CONSTRUCTION.md") == 30
    assert chapter_from_filename("total materials tables.md") is None
