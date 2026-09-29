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

def test_marker_on_heading_line():  # Marker on heading, not in body
    md = """### STEP 1 - {CP27 PC44 MEO}
Description text below."""
    ms = parse_markers(md, 10)
    assert len(ms) == 1
    assert (ms[0].cp, ms[0].lpc, ms[0].cls) == (27, 44, "MEO")
    assert ms[0].heading == "STEP 1 -"  # Heading should be stripped of marker

def test_comma_separated_marker():  # {CP27, PC44, MEO}
    md = """### STEP 1 -
Text with {CP27, PC44, MEO} marker."""
    ms = parse_markers(md, 10)
    assert len(ms) == 1
    assert (ms[0].cp, ms[0].lpc, ms[0].cls) == (27, 44, "MEO")

def test_optional_class_in_marker():  # {CP27 PC44} → cls "?"
    md = """### STEP 1 -
Text with {CP27 PC44} marker."""
    ms = parse_markers(md, 10)
    assert len(ms) == 1
    assert (ms[0].cp, ms[0].lpc, ms[0].cls) == (27, 44, "?")

def test_lpc_instead_of_pc():  # {CP27 LPC 44 MEO}
    md = """### STEP 1 -
Text with {CP27 LPC 44 MEO} marker."""
    ms = parse_markers(md, 10)
    assert len(ms) == 1
    assert (ms[0].cp, ms[0].lpc, ms[0].cls) == (27, 44, "MEO")

def test_invalid_class_rejected():  # {CP1 PC2 the} → no match (invalid class)
    md = """### STEP 1 -
Text with {CP1 PC2 the} marker."""
    ms = parse_markers(md, 10)
    assert len(ms) == 0  # Invalid class code → no marker accepted


def test_heading_updates_when_marker_class_invalid():
    md = """### STEP A
### STEP B {CP1 PC2 the}
Body {CP3 PC4 MEO} here."""
    ms = parse_markers(md, 10)
    assert len(ms) == 1 and ms[0].heading == "STEP B"
