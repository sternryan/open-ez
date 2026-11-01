"""Ground school is offered once, can be skipped, and stays pinned for replay.

``longez.ground`` is ``"seen"`` after start or skip. Skip changes which step is
on screen. The kit, the hour total and the cure markers stay in the plan.
Spent and shop hours done stay at the fresh-start reading.
"""

import json

import pytest

import tests.guide.test_lab_e2e as lab


@pytest.fixture(scope="module", autouse=True, params=["chromium", "webkit"])
def _one_browser(request):
    yield from lab._one_browser.__wrapped__(request)


# lab.rsite returns the built site directory. It is not a generator.
rsite = pytest.fixture(scope="module")(lab.rsite.__wrapped__)

GROUND = "ground-school"
SHOP = "g00.shop-setup"


def _ordered(rsite):
    g = lab._graph(rsite)
    byid = {o["id"]: o for o in g["ops"]}
    _plan, ids = lab._grouped(rsite)
    return [(i, byid[i].get("group")) for i in ids]


def _shop_why(rsite):
    plan = json.loads((rsite / "plan.json").read_text())
    why = plan["scripts"][SHOP][0]["why"]
    assert isinstance(why, str) and why.strip()
    return why


def _meter(pg):
    return pg.evaluate("() => window.__lab.meter()")


def _label(pg):
    return pg.inner_text(f'#navlog .group[data-group="{GROUND}"] > .group-label')


def _markers(pg, kind):
    return pg.eval_on_selector_all(
        f'#navlog .group[data-group="{GROUND}"] .marker.{kind}',
        "els => els.map(e => e.textContent)",
    )


def test_ground_first_launch_offer(rsite):
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            assert pg.is_visible("#ground-offer")
            assert pg.is_visible("#ground-start")
            assert pg.is_visible("#ground-skip")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") is None
            assert pg.evaluate("() => window.__lab.player().step") == SHOP
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            assert (
                pg.get_attribute('#tp-speed [data-speed="1"]', "aria-pressed") == "true"
            )
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_skip_to_build(rsite):
    build = next(i for i, g in _ordered(rsite) if g != GROUND)
    why = _shop_why(rsite)
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            net = []
            pg.on("request", lambda r: net.append(r.method))
            pg.click("#ground-skip")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert pg.evaluate("() => window.__lab.player().step") == build
            assert pg.evaluate("() => window.__lab.player().speed") == 4
            assert (
                pg.get_attribute('#tp-speed [data-speed="4"]', "aria-pressed") == "true"
            )
            assert why not in pg.inner_text("#caption")
            assert [m for m in net if m != "GET"] == []
            pg.click('#tp-speed [data-speed="1"]')
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            pg.reload()
            pg.wait_for_function("window.__lab && window.__lab.ready", timeout=60000)
            pg.wait_for_selector("#navlog button.step[data-op]")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert pg.evaluate("() => window.__lab.player().step") == build
            assert pg.evaluate("() => window.__lab.player().speed") == 4
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_skip_preserves_totals(rsite):
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            before = _meter(pg)
            label = _label(pg)
            buys = _markers(pg, "buy")
            cures = _markers(pg, "cure")
            assert buys, "ground school buys a kit"
            assert cures, "ground school has a cure"
            assert before["hoursTotal"] > 0
            assert before["totalSessions"] > 0
            pg.click("#ground-skip")
            mid = _meter(pg)
            assert mid["hoursTotal"] == before["hoursTotal"]
            assert mid["totalSessions"] == before["totalSessions"]
            assert mid["hoursKnown"] == before["hoursKnown"]
            # The first build step is on screen. That view did not buy the
            # practice kit or spend the lesson hours.
            assert mid["spent"] == before["spent"]
            assert mid["hoursDone"] == before["hoursDone"]
            assert _label(pg) == label
            pg.click(f'#navlog .group[data-group="{GROUND}"] > .group-label')
            assert _markers(pg, "buy") == buys
            assert _markers(pg, "cure") == cures
            again = _meter(pg)
            assert again["hoursTotal"] == before["hoursTotal"]
            assert again["totalSessions"] == before["totalSessions"]
            assert "NaN" not in pg.inner_text("#meter")
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_why_and_slower_speed(rsite):
    why = _shop_why(rsite)
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            pg.click("#ground-start")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert pg.evaluate("() => window.__lab.player().step") == SHOP
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            caption = pg.inner_text("#caption")
            assert why in caption
            assert why in pg.evaluate("() => window.__lab.player().caption")
            assert pg.is_visible("#env-temp")
            assert pg.is_visible("#env-humidity")
            assert pg.is_visible("#env-heat")
            assert pg.get_attribute("#environment", "data-lesson") == "shop-setup"
            pg.click('#tp-speed [data-speed="4"]')
            assert pg.evaluate("() => window.__lab.player().speed") == 4
            assert (
                pg.get_attribute('#tp-speed [data-speed="4"]', "aria-pressed") == "true"
            )
            assert why in pg.inner_text("#caption")
            pg.click('#tp-speed [data-speed="1"]')
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_play_through(rsite):
    """Choosing Start plays the ground lessons in order, then the first build step.

    Plan P3-B: "skip to first build step, always pin ground group for replay".
    A returning visitor's play-through starts after these lessons. Skip changes viewing only.
    """
    want = lab._roncz_in_group(lab._graph(rsite), GROUND)
    assert want[0] == SHOP and len(want) >= 2
    build = next(i for i, grp in _ordered(rsite) if grp != GROUND)
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            pg.click("#ground-start")
            assert pg.evaluate("window.__lab.player().step") == SHOP
            assert pg.evaluate("window.__lab.player().speed") == 1
            pg.click('#tp-speed [data-speed="16"]')
            pg.click("#tp-play")
            seen = [pg.evaluate("window.__lab.player().step")]
            for _ in range(400):
                pg.evaluate("window.__lab.advance(0.5)")
                st = pg.evaluate("window.__lab.player()")
                if st["step"] != seen[-1]:
                    seen.append(st["step"])
                if seen[-1] == build or not st["playing"]:
                    break
            assert seen == want + [build], seen
            assert pg.is_visible(f'#navlog .group.pinned[data-group="{GROUND}"]')
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_replay(rsite):
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            pg.click("#ground-skip")
            groups = pg.eval_on_selector_all(
                "#navlog .group", "els => els.map(e => e.dataset.group)"
            )
            assert groups[0] == GROUND
            assert pg.is_visible(f'#navlog .group.pinned[data-group="{GROUND}"]')
            pg.click(f'#navlog .group[data-group="{GROUND}"] > .group-label')
            assert pg.evaluate("() => window.__lab.player().step") == SHOP
            # g00.tools is the two-person lesson. The build navlog check lists steps after ground school.
            assert (
                pg.locator(
                    '#navlog button.step[data-op="g00.tools"] .chip.buddy'
                ).count()
                == 1
            )
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            assert pg.is_visible("#env-temp")
            assert pg.is_visible("#env-humidity")
            assert pg.is_visible("#env-heat")
            assert pg.get_attribute("#environment", "data-lesson") == "shop-setup"
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def _first_build(rsite):
    """The first build group and its first step. Skip's button opens that step."""
    ordered = _ordered(rsite)
    group = next(g for _i, g in ordered if g != GROUND)
    step = next(i for i, g in ordered if g == group)
    return group, step


def _ground_hours(rsite):
    """Hours the meter counts for ground school. A lesson with no figure is packed as 1 h."""
    g = lab._graph(rsite)
    byid = {o["id"]: o for o in g["ops"]}
    total = 0.0
    for i in lab._roncz_in_group(g, GROUND):
        value = byid[i]["plan"]["hours"]["value"]
        total += 1.0 if value is None else value
    return total


def test_ground_play_answers_the_offer_as_start(rsite):
    """Play on a ground lesson is Start: the offer closes and the skip flag stays clear."""
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            assert pg.is_visible("#ground-offer")
            pg.click("#tp-play")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert (
                pg.evaluate("() => localStorage.getItem('longez.ground.skip')")
                != "skipped"
            )
            assert pg.evaluate("() => window.__lab.player().step") == SHOP
            assert pg.evaluate("() => window.__lab.player().playing") is True
            assert pg.evaluate("() => window.__lab.player().speed") == 1
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_selecting_outside_answers_the_offer_as_skip(rsite):
    """Choosing a build step is Skip: the offer closes, and spent hours stay at a fresh start.

    The step stays the one that was chosen. Skip does not jump to the first build step.
    """
    group, step = _first_build(rsite)
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            before = _meter(pg)
            # The open ground-school list covers this label, so a pointer click lands on a lesson.
            # Dispatching the click runs the label's own handler.
            pg.locator(
                f'#navlog .group[data-group="{group}"] > .group-label'
            ).dispatch_event("click")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert (
                pg.evaluate("() => localStorage.getItem('longez.ground.skip')")
                == "skipped"
            )
            assert pg.evaluate("() => window.__lab.player().step") == step
            mid = _meter(pg)
            # Fresh start: the lessons were not bought or spent, and no build hours are done.
            assert mid["spent"] is None
            assert mid["hoursDone"] == 0
            assert mid["hoursTotal"] == before["hoursTotal"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_play_on_a_build_step_answers_the_offer_as_skip(rsite):
    """Play while a build step is already on screen is Skip, and the step does not change.

    The step is the second build step, so a jump to the first would show. Ground-school
    hours drop out of the done total. The build step behind this one stays.
    """
    _group, first = _first_build(rsite)
    step = next(i for i, g in _ordered(rsite) if g != GROUND and i != first)
    ground_hours = _ground_hours(rsite)
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, query=f"&op={step}", ground_seen=False)
            assert pg.is_visible("#ground-offer")
            assert pg.evaluate("() => window.__lab.player().step") == step
            before = _meter(pg)
            pg.click("#tp-play")
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert (
                pg.evaluate("() => localStorage.getItem('longez.ground.skip')")
                == "skipped"
            )
            assert pg.evaluate("() => window.__lab.player().step") == step
            mid = _meter(pg)
            assert mid["spent"] is None
            assert mid["hoursDone"] == pytest.approx(before["hoursDone"] - ground_hours)
            assert mid["hoursTotal"] == before["hoursTotal"]
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()


def test_ground_selecting_another_lesson_answers_the_offer_as_start(rsite):
    """Choosing another ground lesson is Start: the offer closes and the skip flag stays clear."""
    second = lab._roncz_in_group(lab._graph(rsite), GROUND)[1]
    s, url = lab.serve(rsite)
    try:
        with lab.sync_playwright() as p:
            b, pg, errors = lab._player(p, url, ground_seen=False)
            pg.click(f'#navlog button.step[data-op="{second}"]')
            assert not pg.is_visible("#ground-offer")
            assert pg.evaluate("() => localStorage.getItem('longez.ground')") == "seen"
            assert (
                pg.evaluate("() => localStorage.getItem('longez.ground.skip')")
                != "skipped"
            )
            assert pg.evaluate("() => window.__lab.player().step") == second
            assert not errors, errors
            b.close()
    finally:
        s.shutdown()
