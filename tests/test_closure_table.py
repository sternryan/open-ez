from core.ledger import load_ledger
from core.sources import check_citation
from core.closure import block_sha256

C = load_ledger()["closure"]; ROWS = C["rows"]
OK = {"book", "builder", "derived", "allowance", "unsourced", "conflict"}

def test_every_row_has_bands_status_and_cites():
    for r in ROWS:
        lo, hi = r["weight_band_lb"]; alo, ahi = r["arm_band_fs"]
        assert lo <= r["weight_lb"] <= hi and alo <= r["arm_fs"] <= ahi, r["name"]
        assert r["status"] in OK, r["name"]
        if r["status"] != "unsourced":
            assert r["cite"], r["name"]
            for c in r["cite"]:
                check_citation(c)   # raises on an unregistered source (it returns None when fine)

def test_no_ladder_step_is_a_row():
    assert not any(r["name"].startswith("n26ms_empty") for r in ROWS)

def test_book_rows_carry_no_weight_band():
    for r in ROWS:
        if r["status"] == "book":
            assert r["weight_band_lb"][0] == r["weight_band_lb"][1] == r["weight_lb"]

def test_engine_arm_method_and_prediction_are_written_down():
    assert C["engine_arm_method"]["text"] and C["predicted_gap"]["weight_lb"]

def test_table_is_the_frozen_one():   # editing the block needs a new ledger row with the new hash
    assert block_sha256() in open("docs/geometry-correction-ledger.md").read()

def test_hash_changes_when_a_row_moves(monkeypatch):   # the freeze gate fails on a broken input
    before = block_sha256()
    monkeypatch.setitem(ROWS[0], "weight_lb", ROWS[0]["weight_lb"] + 0.1)
    assert block_sha256() != before
