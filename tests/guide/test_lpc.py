from guide.lpc import parse_lpcs

FIXTURE = """Table of Contents

THE CANARD PUSHER NO. 24 APR  80
THE CANARD PUSHER NO. 25 JULY 80

THE CANARD PUSHER NO. 24 APR  80
some news text
LPC #3, MEO, Page 10-2.
Synthetic description one.

THE CANARD PUSHER NO. 25 JULY 80
LPC #7, MEO, Back cover of plans.
Synthetic description about a station value,
continued on a second line.

LPC #16, MEO, Page 10-5 Step 2.
Synthetic description two.
LPC #17, OPT, Page 12-1
"""

def test_parses_entries_with_issue_attribution():
    got = {c.lpc: c for c in parse_lpcs(FIXTURE)}
    assert set(got) == {3, 7, 16, 17}
    assert got[3].cp == 24 and got[16].cp == 25

def test_page_and_chapter():
    got = {c.lpc: c for c in parse_lpcs(FIXTURE)}
    assert (got[16].page, got[16].chapter) == ("10-5", 10)
    assert (got[17].page, got[17].chapter, got[17].cls) == ("12-1", 12, "OPT")

def test_no_page_entry_is_kept():  # Review Focus 4
    c = {c.lpc: c for c in parse_lpcs(FIXTURE)}[7]
    assert c.page == "back-cover" and c.chapter is None

def test_multiline_description_joined():  # Review Focus 4
    c = {c.lpc: c for c in parse_lpcs(FIXTURE)}[7]
    assert "continued on a second line" in c.text

def test_toc_headers_do_not_attribute():
    assert all(c.cp in (24, 25) for c in parse_lpcs(FIXTURE))

def test_body_header_without_period():  # Header without period should still match
    fixture_no_period = """THE CANARD PUSHER  NO 26 Oct 80
LPC #40, MEO, Page 12-1."""
    got = {c.lpc: c for c in parse_lpcs(fixture_no_period)}
    assert got[40].cp == 26

def test_no_comma_after_number():  # LPC #99  MEO, Section I, ...
    fixture = """THE CANARD PUSHER NO. 25
LPC #50  MEO, Section I, Canard"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[50].cls == "MEO" and got[50].page == "back-cover"

def test_no_commas_at_all():  # LPC #99  MEO  Page 9-9
    fixture = """THE CANARD PUSHER NO. 25
LPC #51  MEO  Page 9-9"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[51].cls == "MEO" and got[51].page == "9-9" and got[51].chapter == 9

def test_missing_class_code():  # LPC #99  Section I, page 9-9
    fixture = """THE CANARD PUSHER NO. 25
LPC #52  Section I, page 9-9"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[52].cls == "?" and got[52].page == "9-9" and got[52].chapter == 9

def test_no_separator_after_class():  # LPC #99  MEO Page 9-9
    fixture = """THE CANARD PUSHER NO. 25
LPC #53  MEO Page 9-9"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[53].cls == "MEO" and got[53].page == "9-9" and got[53].chapter == 9

def test_comma_after_number():  # LPC #999, Section III
    fixture = """THE CANARD PUSHER NO. 25
LPC #54, Section III, Page 10-5"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[54].cls == "?" and got[54].page == "10-5" and got[54].chapter is None

def test_section_ii_has_no_chapter():  # Section II → chapter None
    fixture = """THE CANARD PUSHER NO. 25
LPC #55, MEO, Section II, Page 12-1"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[55].page == "12-1" and got[55].chapter is None

def test_page_on_next_line():  # Page may be on next line
    fixture = """THE CANARD PUSHER NO. 25
LPC #56, MEO, Fuselage bulkhead template
Page 10-2 shows the layout."""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[56].page == "10-2" and got[56].chapter == 10

def test_pages_plural():  # Accept "Pages" (case-insensitive)
    fixture = """THE CANARD PUSHER NO. 25
LPC #57, MEO, Pages 10-5"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[57].page == "10-5" and got[57].chapter == 10

def test_pg_abbreviation():  # Accept "pg" (case-insensitive)
    fixture = """THE CANARD PUSHER NO. 25
LPC #58, MEO, pg 10-5"""
    got = {c.lpc: c for c in parse_lpcs(fixture)}
    assert got[58].page == "10-5" and got[58].chapter == 10
