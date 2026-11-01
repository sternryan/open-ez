"""Builder pace scales known estimates in the lab and leaves logged hours alone.

Same player harness as test_lab_e2e.py. The control is ``#pace-choice``, beside the
shop environment. Pace is localStorage ``longez.pace`` and is never sent.
"""

import json

import pytest

import tests.guide.test_lab_e2e as lab


@pytest.fixture(scope="module", autouse=True, params=["chromium", "webkit"])
def _one_browser(request):
    yield from lab._one_browser.__wrapped__(request)


# lab.rsite returns the built site directory. It is not a generator.
rsite = pytest.fixture(scope="module")(lab.rsite.__wrapped__)


def test_pace_scales_shop_hours_and_survives_reload(rsite):
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=True)
            assert pg.input_value("#pace-choice") == "logged"
            assert "pace-scaled" not in pg.inner_text("#meter")
            assert "pace-scaled" not in pg.inner_text("#bench")
            assert "pace-scaled" not in pg.inner_text("#navlog")
            before = pg.evaluate("() => window.__lab.meter()")
            n0 = lab._sessions(pg)
            net = []
            pg.on("request", lambda r: net.append(r.method))
            pg.select_option("#pace-choice", "longez")
            mid = pg.evaluate("() => window.__lab.meter()")
            n1 = lab._sessions(pg)
            assert mid["hoursTotal"] < before["hoursTotal"]
            assert n1 <= n0
            hours = pg.inner_text('#bench [data-k="hours"]')
            assert "pace-scaled" in hours
            assert "1.5" not in hours
            assert "NaN" not in pg.inner_text("#meter")
            assert "NaN" not in pg.inner_text("#bench")
            assert "NaN" not in pg.inner_text("#navlog")
            assert "pace-scaled" in pg.inner_text("#navlog")
            if mid["hoursKnown"]:
                assert "pace-scaled" in pg.inner_text("#meter")
            raw = pg.evaluate("() => localStorage.getItem('longez.pace')")
            assert raw
            saved = json.loads(raw)
            assert saved["choice"] == "longez"
            assert saved["m"] == 0.653
            assert [m for m in net if m != "GET"] == []
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.wait_for_selector("#navlog button.step[data-op]")
            assert pg.input_value("#pace-choice") == "longez"
            again = pg.evaluate("() => window.__lab.meter()")
            assert again["hoursTotal"] == mid["hoursTotal"]
            pg.select_option("#pace-choice", "custom")
            pg.fill("#pace-custom", "9")
            pg.dispatch_event("#pace-custom", "change")
            held = pg.evaluate("() => window.__lab.meter().hoursTotal")
            assert held == mid["hoursTotal"]
            assert pg.input_value("#pace-custom") == "0.653"
            pg.evaluate("localStorage.setItem('longez.pace', '{not json')")
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.wait_for_selector("#navlog button.step[data-op]")
            assert pg.input_value("#pace-choice") == "logged"
            restored = pg.evaluate("() => window.__lab.meter()")
            assert restored["hoursTotal"] == before["hoursTotal"]
            assert "pace-scaled" not in pg.inner_text("#bench")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
