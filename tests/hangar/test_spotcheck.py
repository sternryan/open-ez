"""Research spot-check by a different method, source registration, and the guarded data patch (hangar/spotcheck.py)."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from core import sources
from hangar import spotcheck as sc

PAGE = """<html><head><script>var secret = 99999;</script><style>.x{}</style></head>
<body><h1>Engine data</h1><p>The&nbsp;installed   weight is 75.4&nbsp;kg (166.2 lb)
including exhaust.</p><p>Coolant: 3,150 g</p></body></html>"""


def prop(**kw):
    p = {"claim": "installed weight 166.2 lb", "value": 166.2, "unit": "lb", "url": "https://example.org/engine.html",
         "title": "Example engine data sheet", "quote": "installed weight is 75.4 kg (166.2 lb)"}
    p.update(kw)
    return p


def fetch_of(text, calls=None):
    def fetch(url):
        if calls is not None:
            calls.append(url)
        return text
    return fetch


def test_match_quote_and_value_after_whitespace_and_tags_are_normalized():
    r = sc.spotcheck_url(prop(), fetch=fetch_of(PAGE))
    assert r["fetched"] is True and r["matched"] is True and r["quote_found"] is True and r["value_found"] is True
    assert isinstance(r["method"], str) and "fetch" in r["method"]


def test_case_insensitive_and_quote_normalization():
    r = sc.spotcheck_url(prop(quote="THE INSTALLED WEIGHT IS 75.4 KG (166.2 LB)"), fetch=fetch_of(PAGE))
    assert r["matched"] is True


def test_quote_missing_is_not_a_match():
    r = sc.spotcheck_url(prop(quote="weighs a ton"), fetch=fetch_of(PAGE))
    assert r["fetched"] is True and r["matched"] is False and r["quote_found"] is False


def test_value_missing_is_not_a_match_even_if_the_quote_is_found():
    r = sc.spotcheck_url(prop(value=999.9), fetch=fetch_of(PAGE))
    assert r["quote_found"] is True and r["value_found"] is False and r["matched"] is False


def test_value_none_checks_the_quote_only():
    r = sc.spotcheck_url(prop(value=None), fetch=fetch_of(PAGE))
    assert r["matched"] is True and r["value_found"] is None


def test_thousand_separator_value_matches():
    r = sc.spotcheck_url(prop(value=3150, quote="Coolant: 3,150 g"), fetch=fetch_of(PAGE))
    assert r["matched"] is True


def test_script_and_style_text_is_ignored():
    r = sc.spotcheck_url(prop(value=99999, quote="var secret = 99999"), fetch=fetch_of(PAGE))
    assert r["matched"] is False


def test_value_must_match_as_a_whole_number():
    # 66.2 must not match inside 166.2
    r = sc.spotcheck_url(prop(value=66.2, quote="installed weight is 75.4 kg (166.2 lb)"), fetch=fetch_of(PAGE))
    assert r["value_found"] is False and r["matched"] is False


def test_bytes_are_decoded_and_fetch_errors_never_raise():
    assert sc.spotcheck_url(prop(), fetch=fetch_of(PAGE.encode("utf-8")))["matched"] is True

    def boom(url):
        raise OSError("down")

    r = sc.spotcheck_url(prop(), fetch=boom)
    assert r["fetched"] is False and r["matched"] is False and "down" in r["detail"]


@pytest.mark.parametrize("url", ["http://127.0.0.1/x", "http://localhost:8080/x", "http://10.1.2.3/x", "http://192.168.1.5/x",
                                 "http://172.20.0.1/x", "http://169.254.169.254/latest", "http://[::1]/x", "ftp://example.org/x",
                                 "file:///etc/passwd", "http://nas.local/x", "http://box.internal/x", "not a url", ""])
def test_private_and_non_http_urls_are_refused_without_fetching(url):
    calls = []
    r = sc.spotcheck_url(prop(url=url), fetch=fetch_of(PAGE, calls))
    assert calls == [] and r["fetched"] is False and r["matched"] is False and "refused" in r["detail"]


def test_bad_proposal_shapes_do_not_raise():
    for bad in (None, {}, {"url": "https://example.org/", "quote": ""}, {"url": 3, "quote": "x"}, "text"):
        r = sc.spotcheck_url(bad, fetch=fetch_of(PAGE))
        assert r["matched"] is False and r["fetched"] is False


def test_text_size_is_capped():
    big = "x" * 3_000_000 + " installed weight is 75.4 kg (166.2 lb)"
    r = sc.spotcheck_url(prop(), fetch=fetch_of(big))
    assert r["matched"] is False  # the quote sits past the 2 MB cap


# ---- register_source ----

def registry(tmp_path):
    p = tmp_path / "registry.yaml"
    p.write_text("# header comment\nsources:\n  old-one:\n    title: Old\n    edition: e\n    obtain: https://example.org/old\n"
                 "    copy: document\n    page_basis: pdf\n")
    return p


def test_register_source_appends_a_valid_entry_and_keeps_the_header(tmp_path):
    p = registry(tmp_path)
    sid = sc.register_source(p, prop(), today="2026-10-19")
    text = p.read_text()
    assert text.startswith("# header comment") and "old-one:" in text
    entry = yaml.safe_load(text)["sources"][sid]
    assert entry["obtain"] == "https://example.org/engine.html" and entry["copy"] == "document" and entry["page_basis"] == "pdf"
    assert set(entry) >= {"title", "edition", "obtain", "copy", "page_basis"} and "2026-10-19" in entry["edition"]
    assert sid.islower() and " " not in sid and sid != "old-one"
    assert sources._CITE.match(f"{sid}:p1")


def test_register_source_is_idempotent_per_url_and_ids_do_not_collide(tmp_path):
    p = registry(tmp_path)
    a = sc.register_source(p, prop(), today="2026-10-19")
    assert sc.register_source(p, prop(), today="2026-10-20") == a
    assert len(yaml.safe_load(p.read_text())["sources"]) == 2
    b = sc.register_source(p, prop(url="https://example.org/other.html"), today="2026-10-19")
    assert b != a and len(yaml.safe_load(p.read_text())["sources"]) == 3


def test_register_source_rejects_non_http_url_and_missing_title(tmp_path):
    p = registry(tmp_path)
    with pytest.raises(ValueError):
        sc.register_source(p, prop(url="file:///etc/passwd"), today="2026-10-19")
    with pytest.raises(ValueError):
        sc.register_source(p, prop(title=""), today="2026-10-19")
    assert len(yaml.safe_load(p.read_text())["sources"]) == 1


def test_register_source_quotes_hostile_text_safely(tmp_path):
    p = registry(tmp_path)
    sid = sc.register_source(p, prop(title="Weird: title # with 'quotes' and\nnewline", url="https://example.org/a?b=c#d"), today="2026-10-19")
    entry = yaml.safe_load(p.read_text())["sources"][sid]
    assert "Weird" in entry["title"] and "\n" not in entry["title"]
    assert entry["obtain"].startswith("https://example.org/a")


# ---- apply_patch ----

def powerplants(tmp_path):
    p = tmp_path / "powerplants.yaml"
    p.write_text(yaml.safe_dump({"rotax-912is": {"installed_lb": {"v": 166.2, "flag": "derived", "note": "n"},
                                                 "cg_arm_in": {"v": 141.05, "flag": "derived", "note": "assumed"},
                                                 "label": "text"}}, sort_keys=False))
    return p


PATCH = {"file": "powerplants.yaml", "path": ["rotax-912is", "cg_arm_in"], "value": 139.2, "note": "weighed on the maker jig"}


def test_apply_patch_sets_value_flag_sourced_and_cite(tmp_path):
    p = powerplants(tmp_path)
    sc.apply_patch(tmp_path, PATCH, "rotax-sheet")
    cg = yaml.safe_load(p.read_text())["rotax-912is"]["cg_arm_in"]
    assert cg == {"v": 139.2, "flag": "sourced", "note": "weighed on the maker jig", "cite": "rotax-sheet:p1"}
    assert yaml.safe_load(p.read_text())["rotax-912is"]["installed_lb"]["v"] == 166.2  # untouched


@pytest.mark.parametrize("patch", [
    {**PATCH, "file": "../../etc/passwd"},
    {**PATCH, "file": "records.yaml"},
    {**PATCH, "path": ["rotax-912is", "nope"]},
    {**PATCH, "path": ["nope", "cg_arm_in"]},
    {**PATCH, "path": ["rotax-912is", "label"]},      # not a Value-shaped entry
    {**PATCH, "path": []},
    {**PATCH, "value": "heavy"},
    {**PATCH, "value": True},
    {**PATCH, "value": float("nan")},
    {**PATCH, "value": float("inf")},
    {"file": "powerplants.yaml"},
    "text",
    None,
])
def test_apply_patch_refuses_bad_patches_and_leaves_the_file_alone(tmp_path, patch):
    p = powerplants(tmp_path)
    before = p.read_text()
    with pytest.raises(ValueError):
        sc.apply_patch(tmp_path, patch, "rotax-sheet")
    assert p.read_text() == before


def test_apply_patch_can_target_mission_values(tmp_path):
    (tmp_path / "mission.yaml").write_text(yaml.safe_dump({"leg_nm": 300, "cruise_ktas": {"v": 150, "flag": "derived", "note": "n"}}, sort_keys=False))
    sc.apply_patch(tmp_path, {"file": "mission.yaml", "path": ["cruise_ktas"], "value": 148.0, "note": "flight test"}, "src")
    assert yaml.safe_load((tmp_path / "mission.yaml").read_text())["cruise_ktas"]["v"] == 148.0
