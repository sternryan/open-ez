from guide.overlap import SourceIndex, shingles

SRC = [
    "Place one of your seven by fourteen foam blocks on the table and trim it square."
]


def test_verbatim_run_is_caught():
    idx = SourceIndex(SRC)
    assert idx.hits(
        "First, place one of your seven by fourteen foam blocks on the bench."
    )


def test_paraphrase_passes():
    idx = SourceIndex(SRC)
    assert (
        idx.hits("Set a 7x14 block on the bench and square it with the trim templates.")
        == []
    )


def test_normalization_ignores_case_and_punctuation():
    idx = SourceIndex(SRC)
    assert idx.hits('PLACE ONE, of your "seven" by fourteen foam blocks!')


def test_short_text_has_no_shingles():
    assert shingles("too short to match", 8) == set()
