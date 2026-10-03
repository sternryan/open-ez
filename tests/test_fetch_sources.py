# tests/test_fetch_sources.py
from scripts.fetch_sources import cp_url, split_printed_pages


def test_cp_url():
    assert (
        cp_url(29, "1981-07")
        == "http://www.cozybuilders.org/Canard_Pusher/1981-07_cp-29.pdf"
    )


def test_split_printed_pages_uses_footer_numbers():
    text = "alpha\n27\n\x0cbeta\nWeight and C G Limits\n28\n\x0c"
    assert split_printed_pages(text) == {
        "27": "alpha",
        "28": "beta\nWeight and C G Limits",
    }
