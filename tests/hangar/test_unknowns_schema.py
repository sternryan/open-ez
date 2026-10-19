"""Unknown ids, decision digests and the reopen flag on a record (wave 3 schema)."""

from __future__ import annotations

import yaml

from hangar.matrix import matrix_for_effect
from hangar.matrix_extra import matrix_text
from hangar.records import load_records
from tests.hangar.test_records import base, decided, errs, make

CG_AFFECTS = {
    "radiator-coolant-weight": [
        "loading-limit", "fixed-aft-ballast", "battery-aft", "engine-arm-aft", "radiator-aft",
    ],
    "installed-cg-arm": [
        "loading-limit", "fixed-aft-ballast", "battery-aft", "engine-arm-aft", "radiator-aft",
    ],
    "large-battery-included": ["battery-aft"],
    "owners-own-margins": ["loading-limit", "fixed-aft-ballast", "battery-aft", "engine-arm-aft"],
    "propeller-weight-arm": ["fixed-aft-ballast", "battery-aft", "engine-arm-aft"],
}


def unk(**kw) -> dict:
    row = {
        "id": "coolant-weight",
        "text": "coolant weight",
        "how": "maker manual",
        "affects": ["alt"],
        "state": "open",
    }
    row.update(kw)
    return row


def with_unknowns(*rows) -> dict:
    d = base()
    d["unknowns"] = list(rows)
    return d


def test_id_unknown_is_valid_and_empty_affects_means_the_whole_record(tmp_path):
    assert errs(tmp_path, with_unknowns(unk())) == []
    assert errs(tmp_path, with_unknowns(unk(affects=[]))) == []


def test_legacy_unknown_without_id_stays_valid(tmp_path):
    assert errs(tmp_path, with_unknowns({"text": "ethanol limit", "how": "ask the maker"})) == []


def test_non_dict_unknown_stays_valid(tmp_path):
    assert errs(tmp_path, with_unknowns("a note carried over from earlier")) == []


def test_bad_id_affects_and_state_are_rejected(tmp_path):
    assert any("duplicate" in e for e in errs(tmp_path, with_unknowns(unk(), unk())))
    assert errs(tmp_path, with_unknowns(unk(id="")))
    assert errs(tmp_path, with_unknowns(unk(id=3)))
    assert any("ghost" in e for e in errs(tmp_path, with_unknowns(unk(affects=["ghost"]))))
    bare = unk()
    del bare["affects"]
    assert errs(tmp_path, with_unknowns(bare))
    assert errs(tmp_path, with_unknowns(unk(affects="alt")))
    assert errs(tmp_path, with_unknowns(unk(state="closed")))
    assert errs(tmp_path, with_unknowns(unk(source=3)))


def test_source_is_cited_only_when_the_unknown_is_sourced(tmp_path):
    # an open unknown may name a source that is not registered yet
    assert errs(tmp_path, with_unknowns(unk(source="not-a-real-source"))) == []
    assert errs(tmp_path, with_unknowns(unk(state="sourced", source="om-1980"))) == []
    assert errs(tmp_path, with_unknowns(unk(state="sourced"))) == []
    out = errs(tmp_path, with_unknowns(unk(state="sourced", source="not-a-real-source")))
    assert any("unknown source id" in e for e in out)


def test_over_unknowns_and_matrix_digest_name_real_ids(tmp_path):
    d = decided()
    d["unknowns"] = [unk(), unk(id="arm-measure", state="sourced", source="om-1980")]
    d["decision"] = dict(d["decision"], over_unknowns=["coolant-weight"], matrix_digest={"alt": "abc"})
    assert errs(tmp_path, d) == []
    d["decision"]["over_unknowns"] = ["missing-id"]
    assert errs(tmp_path, d)
    d["decision"]["over_unknowns"] = ["coolant-weight"]
    d["decision"]["matrix_digest"] = {"ghost": "abc"}
    assert errs(tmp_path, d)
    d["decision"]["matrix_digest"] = {"alt": 12}
    assert errs(tmp_path, d)
    d["decision"]["matrix_digest"] = []
    assert errs(tmp_path, d)


def test_reopen_flag_only_while_decided_and_load_keeps_it(tmp_path):
    flag = {
        "date": "2026-10-19",
        "reason": "the loading matrix changed after a sourced value",
        "unknowns": ["coolant-weight"],
        "digest_then": {"alt": "aa"},
        "digest_now": {"alt": "bb"},
    }
    open_rec = base()
    open_rec["reopen_flag"] = dict(flag)
    assert errs(tmp_path, open_rec)

    ok = decided()
    ok["reopen_flag"] = dict(flag)
    assert errs(tmp_path, ok) == []
    loaded = make(tmp_path, ok)
    assert loaded.reopen_flag["digest_then"] == {"alt": "aa"}

    thin = decided()
    thin["reopen_flag"] = {"date": "2026-10-19"}
    assert errs(tmp_path, thin)
    thin["reopen_flag"] = {"date": "2026-10-19", "reason": "x", "unknowns": [1]}
    assert errs(tmp_path, thin)

    again = decided()
    again["history"].append({"date": "2026-10-21", "from": "decided", "to": "reopened", "reason": "new data"})
    again["status"] = "reopened"
    again["reopen_flag"] = dict(flag)
    assert errs(tmp_path, again)


def test_real_records_give_every_unknown_an_id(tmp_path):
    """The three Mod-EZ records carry id, affects and state. Removing the migration fails this."""
    del tmp_path
    recs = load_records()
    counts = {"cg-ballast": 5, "powerplant-fuel-resin": 5, "propeller": 6}
    for rid, n in counts.items():
        rows = recs[rid].unknowns
        assert len(rows) == n
        opt_ids = {o["id"] for o in recs[rid].options}
        seen = []
        for row in rows:
            assert isinstance(row["id"], str) and 2 <= len(row["id"].split("-")) <= 4
            assert row["state"] in ("open", "researching")  # wave 4 stages three cg-ballast unknowns for the owner
            assert isinstance(row["affects"], list)
            assert set(row["affects"]) <= opt_ids
            assert row["text"] and row["how"]
            seen.append(row["id"])
        assert len(seen) == len(set(seen))
    by = {u["id"]: u["affects"] for u in recs["cg-ballast"].unknowns}
    assert by == CG_AFFECTS
    # the words that were already on the record stay, so the migration added fields rather than replacing rows
    blob = yaml.safe_dump(recs["cg-ballast"].unknowns).lower()
    for needle in ("coolant", "installed cg", "large battery", "margins", "propeller"):
        assert needle in blob


def test_radiator_aft_is_a_candidate_with_no_effect():
    """The mass record's unscored option. The decide gate has to see it; a later effect would retire this."""
    rec = load_records()["cg-ballast"]
    opt = next(item for item in rec.options if item["id"] == "radiator-aft")
    assert opt["kind"] == "candidate"
    assert not isinstance(opt.get("effect"), dict)


def test_cg_ballast_matrix_facts_match_the_generator():
    """Each option that has an effect carries one generated matrix fact. A hand-written sentence fails this."""
    rec = load_records()["cg-ballast"]
    seen = 0
    for opt in rec.options:
        facts = [f for f in opt["facts"] if isinstance(f, dict) and f.get("computed") == "matrix"]
        if isinstance(opt.get("effect"), dict):
            assert len(facts) == 1, opt["id"]
            assert facts[0]["flag"] == "derived"
            assert facts[0]["text"] == matrix_text(matrix_for_effect(opt["effect"]))
            seen += 1
        else:
            assert facts == [], opt["id"]
    assert seen == 5
