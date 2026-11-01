"""A logged actual changes the meter, survives reload, and clear restores the estimate.

Same player harness as test_lab_e2e.py. The bench inputs this drives are not built yet:
``#bench input[data-k="actual-hours"]`` and ``#bench button[data-k="actual-clear"]``.
Actuals live in localStorage under ``longez.actuals`` and are never sent.
"""

import json

import pytest

import tests.guide.test_lab_e2e as lab


@pytest.fixture(scope="module", autouse=True, params=["chromium", "webkit"])
def _one_browser(request):
    yield from lab._one_browser.__wrapped__(request)


# lab.rsite returns the built site directory. It is not a generator.
rsite = pytest.fixture(scope="module")(lab.rsite.__wrapped__)


def test_actual_entered_survives_reload_and_clear_restores_estimate(rsite):
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url)
            before = pg.evaluate("() => window.__lab.meter()")
            step = pg.evaluate("() => window.__lab.navlog().current")
            net = []
            pg.on("request", lambda r: net.append((r.method, r.url)))
            hours = pg.locator('#bench input[data-k="actual-hours"]')
            hours.fill("0")
            hours.dispatch_event("change")
            mid = pg.evaluate("() => window.__lab.meter()")
            assert mid["hoursTotal"] != before["hoursTotal"], (before, mid)
            assert "NaN" not in pg.inner_text("#meter")
            raw = pg.evaluate("() => localStorage.getItem('longez.actuals')")
            assert raw, "actuals are kept in localStorage under longez.actuals"
            saved = json.loads(raw)
            assert saved[step]["hours"] == 0
            assert [m for m, _u in net if m != "GET"] == []
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.wait_for_selector("#navlog button.step[data-op]")
            assert (
                pg.locator('#bench input[data-k="actual-hours"]').input_value() == "0"
            )
            again = pg.evaluate("() => window.__lab.meter()")
            assert again["hoursTotal"] == mid["hoursTotal"]
            assert again["hoursTotal"] != before["hoursTotal"]
            pg.click('#bench button[data-k="actual-clear"]')
            restored = pg.evaluate("() => window.__lab.meter()")
            assert restored["hoursTotal"] == before["hoursTotal"]
            cleared = pg.evaluate("() => localStorage.getItem('longez.actuals')")
            left = json.loads(cleared) if cleared else {}
            assert left.get(step, {}).get("hours") is None
            assert "NaN" not in pg.inner_text("#meter")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
