"""Research spot-check by a different method, source registration, and the guarded data patch (hangar/spotcheck.py)."""

from __future__ import annotations

import copy
import threading
import time
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


# ---- review: fetch policy, number tokens, atomic registry and patch writes ----

_FORBIDDEN_URLS = [
    "http://foo.localhost/secret",
    "http://0x7f.1/",
    "http://2130706433/",
    "http://0177.0.0.1/",
    "http://127.1/",
    "http://a@127.0.0.1/",
    "http://a@0x7f.1/",
    "http://[::ffff:127.0.0.1]/",
    "http://[::ffff:7f00:1]/",
    "http://100.64.0.1/",
    "http://[fec0::1]/",
    "ftp://127.0.0.1/secret",
]


@pytest.mark.parametrize("url", _FORBIDDEN_URLS)
def test_name_and_literal_policy_runs_before_an_injected_fetch(url):
    calls = []
    r = sc.spotcheck_url(prop(url=url), fetch=fetch_of(PAGE, calls))
    assert calls == [] and r["fetched"] is False and r["matched"] is False and "refused" in r["detail"]


def test_injected_fetch_skips_dns_for_a_public_name():
    resolved = []
    calls = []

    def resolver(host):
        resolved.append(host)
        return ["127.0.0.1"]

    r = sc.spotcheck_url(prop(), fetch=fetch_of(PAGE, calls), resolver=resolver)
    assert r["matched"] is True and calls == ["https://example.org/engine.html"] and resolved == []


def test_rebind_connects_only_to_the_approved_address():
    lookups = []

    def resolver(host):
        lookups.append(host)
        return ["1.1.1.1"] if len(lookups) == 1 else ["127.0.0.1"]

    seen = []

    def transport(url, address, timeout):
        seen.append((url, address, timeout))
        if address == "127.0.0.1":
            return 200, {}, PAGE
        return 200, {}, "<html><body>public page without the quote</body></html>"

    r = sc.spotcheck_url(prop(), resolver=resolver, transport=transport, timeout=9)
    assert lookups == ["example.org"]
    assert seen == [("https://example.org/engine.html", "1.1.1.1", 9)]
    assert r["fetched"] is True and r["quote_found"] is False and r["matched"] is False


def test_every_resolved_address_must_be_global():
    seen = []

    def transport(url, address, timeout):
        seen.append(address)
        return 200, {}, PAGE

    r = sc.spotcheck_url(prop(), resolver=lambda host: ["1.1.1.1", "127.0.0.1"], transport=transport)
    assert seen == [] and r["fetched"] is False and "refused" in r["detail"]


@pytest.mark.parametrize("address", ["100.64.0.1", "fec0::1", "::ffff:10.1.2.3", "::ffff:7f00:1", "224.0.0.1", "0.0.0.0"])
def test_resolver_refuses_non_global_and_special_ranges(address):
    seen = []

    def transport(url, address_used, timeout):
        seen.append(address_used)
        return 200, {}, PAGE

    r = sc.spotcheck_url(prop(), resolver=lambda host: [address], transport=transport)
    assert seen == [] and r["fetched"] is False and "refused" in r["detail"]


@pytest.mark.parametrize("location", _FORBIDDEN_URLS)
def test_redirects_rerun_the_policy_and_do_not_follow_automatically(location):
    seen = []

    def transport(url, address, timeout):
        seen.append((url, address))
        return 302, {"Location": location}, b""

    r = sc.spotcheck_url(prop(), resolver=lambda host: ["1.1.1.1"], transport=transport)
    assert seen == [("https://example.org/engine.html", "1.1.1.1")]
    assert r["fetched"] is False and r["matched"] is False and "refused" in r["detail"]


def test_a_public_redirect_is_followed_and_pinned_again():
    seen = []

    def resolver(host):
        return {"example.org": ["1.1.1.1"], "cdn.example": ["8.8.8.8"]}[host]

    def transport(url, address, timeout):
        seen.append((url, address))
        if url.startswith("https://example.org/"):
            return 302, {"Location": "https://cdn.example/sheet"}, b""
        return 200, {}, PAGE

    r = sc.spotcheck_url(prop(), resolver=resolver, transport=transport)
    assert r["matched"] is True and r["quote_found"] is True
    assert seen == [
        ("https://example.org/engine.html", "1.1.1.1"),
        ("https://cdn.example/sheet", "8.8.8.8"),
    ]


def test_at_most_three_redirects():
    seen = []

    def transport(url, address, timeout):
        seen.append(url)
        return 302, {"Location": f"https://example.org/hop{len(seen)}"}, b""

    r = sc.spotcheck_url(prop(), resolver=lambda host: ["1.1.1.1"], transport=transport)
    assert r["fetched"] is False and "refused" in r["detail"]
    assert len(seen) == 4


@pytest.mark.parametrize("page", [
    "<script>installed weight is 75.4 kg (166.2 lb)</script > tail",
    "<script type='text/javascript'>installed weight is 75.4 kg (166.2 lb)</script foo=1> tail",
    "<script>installed weight is 75.4 kg (166.2 lb)",
    "<STYLE>installed weight is 75.4 kg (166.2 lb)</STYLE > tail",
    "<style>installed weight is 75.4 kg (166.2 lb)",
])
def test_script_and_style_run_to_a_real_closer_or_end_of_input(page):
    r = sc.spotcheck_url(prop(), fetch=fetch_of(page))
    assert r["fetched"] is True and r["quote_found"] is False and r["matched"] is False


def test_value_preceded_by_a_thousands_group_is_the_same_number():
    page = "<p>see 3 150 and also 3,150 units</p>"
    r = sc.spotcheck_url(prop(value=150, quote="see 3 150"), fetch=fetch_of(page))
    assert r["quote_found"] is True and r["value_found"] is False and r["matched"] is False


@pytest.mark.parametrize("spelling", ["1,000,000", "1 000 000"])
def test_grouped_candidates_cover_every_group_of_three(spelling):
    page = f"<p>cost {spelling} units</p>"
    r = sc.spotcheck_url(prop(value=1000000, quote=f"cost {spelling} units"), fetch=fetch_of(page))
    assert r["value_found"] is True and r["matched"] is True


def test_register_source_disk_full_leaves_the_old_file(tmp_path, monkeypatch):
    p = registry(tmp_path)
    before = p.read_bytes()

    def boom(handle, text):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(sc, "_emit", boom, raising=False)
    with pytest.raises(OSError):
        sc.register_source(p, prop(title="Weird title pwn yes"), today="2026-10-19")
    assert p.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


def test_concurrent_register_of_the_same_url_writes_one_entry(tmp_path):
    p = registry(tmp_path)
    ids = []
    errors = []
    barrier = threading.Barrier(8)

    def work():
        try:
            barrier.wait(timeout=5)
            ids.append(sc.register_source(p, prop(), today="2026-10-19"))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=work) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert errors == []
    assert len(set(ids)) == 1
    text = p.read_text()
    assert text.count(f"\n  {ids[0]}:\n") == 1
    assert len(yaml.safe_load(text)["sources"]) == 2


def test_apply_patch_alias_changes_only_the_named_entry(tmp_path):
    target = tmp_path / "powerplants.yaml"
    target.write_text(
        "rotax-912is:\n"
        "  installed_lb: &shared\n"
        "    v: 166.2\n"
        "    flag: derived\n"
        "    note: weighed\n"
        "  cg_arm_in: *shared\n"
    )
    sc.apply_patch(tmp_path, PATCH, "rotax-sheet")
    data = yaml.safe_load(target.read_text())["rotax-912is"]
    assert data["cg_arm_in"]["v"] == 139.2
    assert data["cg_arm_in"]["flag"] == "sourced"
    assert data["cg_arm_in"]["cite"] == "rotax-sheet:p1"
    assert data["installed_lb"] == {"v": 166.2, "flag": "derived", "note": "weighed"}


def test_apply_patch_holds_a_lock_and_concurrent_patches_both_land(tmp_path):
    import fcntl

    target = powerplants(tmp_path)
    lock_path = tmp_path / "powerplants.yaml.lock"
    before = target.read_text()
    with open(lock_path, "a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        finished = threading.Event()
        errors = []

        def go():
            try:
                sc.apply_patch(tmp_path, PATCH, "rotax-sheet")
            except Exception as exc:
                errors.append(exc)
            finally:
                finished.set()

        thread = threading.Thread(target=go)
        thread.start()
        time.sleep(0.2)
        assert target.read_text() == before
        assert not finished.is_set()
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    thread.join(timeout=5)
    assert errors == []
    assert yaml.safe_load(target.read_text())["rotax-912is"]["cg_arm_in"]["v"] == 139.2

    barrier = threading.Barrier(2)
    errors = []

    def patch(key, value):
        try:
            barrier.wait(timeout=5)
            sc.apply_patch(
                tmp_path,
                {**PATCH, "path": ["rotax-912is", key], "value": value},
                "rotax-sheet",
            )
        except Exception as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=patch, args=("cg_arm_in", 139.2)),
        threading.Thread(target=patch, args=("installed_lb", 170.0)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    assert errors == [] and not any(isinstance(item, FileNotFoundError) for item in errors)
    saved = yaml.safe_load(target.read_text())["rotax-912is"]
    assert saved["cg_arm_in"]["v"] == 139.2
    assert saved["installed_lb"]["v"] == 170.0
    assert not (tmp_path / "powerplants.yaml.tmp").exists()
