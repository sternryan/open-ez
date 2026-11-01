# Rehearsal player: phase 1 gate record

Date: 2026-10-18. Branch `feat/rehearsal-p1`, base `origin/main` `e09c22d`. Host names are omitted (public repo).

## Scope

Phase 1 of `docs/superpowers/plans/2026-10-17-build-rehearsal-player.md`: groups, plan fields, catalog and resin
data, `plan.json`, the planning logic (cure, sessions, kits, sequence, actions), step-script validation and
generation, sourced plan values for the first stretch (seat bulkheads and firewall, fuselage sides), and the
integrated player, which is now the default page (`?player=0` keeps the legacy page).

## Tests (tree `698e067` unless noted)

| Suite | Result |
|---|---|
| Python, all files except the two browser files | 1785 passed, 5 skipped, 21 xfailed |
| `guide.check --schema-only` | OK |
| Viewer node tests | 50 passed |
| Lab `npm test` / typecheck / build | 317 passed / clean / built |
| Recorder `tools/record.test.mjs` | 26 passed |
| Browser suites (`test_lab_e2e.py`, `test_viewer_e2e.py`), chromium + webkit, 8 workers | 465 passed, 1 failed (frame-time median under parallel CPU load) |
| The four frame-time tests, serially | 4 passed |
| pre-commit on every branch-touched file (tree `2365675`) | ruff, ruff-format, geometry smoke passed |

`2365675` is formatting only (ruff-format of `tests/guide/test_lab_e2e.py` plus one lambda turned into a `def`); the
file still collects 436 tests.

## Broken-input proof

- A catalog row with an unknown flag, a `page` row with a null price, and an unparseable `read` date each raise
  `SchemaError` (`tests/guide/test_catalog_resin.py`).
- An unknown buy item or resin id fails `guide.check` (`test_unknown_references_fail_through_check`).
- A bad step script fails `guide.check` (`test_bad_script_fails_guide_check`).
- With the meter forced to print a number for unknown hours, and with environment persistence removed,
  `test_player_meter_shows_dash_for_unknown_hours` and `test_env_survives_reload` failed; both pass on the real code.

## Device evidence

- Owner, phone, portrait: playback good on the first build; the layout was crowded, so the narrow layout followed
  (`9833ef3`, `cf141e1`). The owner accepts the phone as device proof.
- Owner, iPad (2026-10-18): "ran just fine". The default flip (`698e067`) rests on these two checks.
- The served default page at 390x844 in headless chromium: player by default, no horizontal overflow, no page errors.

## Grade, call 1 of 2 (FAIL) and fixes

Astra call 1 failed the phase with seven must-fix findings. Each fix's test failed first.

| Finding | Fix |
|---|---|
| 1. Ply beats mapped onto the wrong ply and cloth | `logic/plyMap.ts` maps each authored ply to its own meshes; plies without geometry play caption-only (`1703734`) |
| 2. Phone meter hid "partial" and "unpriced" | the collapsed strip keeps the qualifier (`1703734`) |
| 3. Script tools contradicted the step | every override audited; unlisted tools are labelled stand-ins (`9b60aa1`) |
| 4. Device acceptance missing before the flip | phone and iPad, above |
| 5. Ply coverage and order not enforced | `validate_scripts` requires wet-out plies 1..N in order (`9b60aa1`) |
| 6. `official` without readable evidence | the AN509 screws are now `estimate` (`33c27cd`); the bench shows each value's evidence or prints "estimate" (`1703734`) |
| 7. NaN accepted | non-finite and negative values rejected (`9268f2d`) |
| Follow-ups | the GU note renders once, on the bench; calendar hours are unknown after a placeholder session (`ba51280`, `1703734`) |

On the combined tree: lab 327 passed, typecheck clean, guide Python 418 passed, `guide.check` OK.
Still open after the fixes: many ops (spar caps, canopy frame, wing and winglet plies) animate caption-only per ply, because
the exporter does not tag drawn plies with their materials row; buy rows have no `source` field yet.

## Sourcing record

`docs/harness/rehearsal-sourcing-p1.md`. Hours are all `estimate` (one builder's chapter totals split per op);
two ops have none. The MGS 285/287 datasheet gives a 10 °C minimum (p1) and no work-again time, so every cure gate
shows a warning, not a number. Six new catalog items are priced, six are unsourced.

## Lanes

| Work | Lane | Result |
|---|---|---|
| Schema, data, tests, wiring | Cursor `grok-4.7-medium` | 6 batched calls |
| Catalog, resin and `plan.json` bodies | local GPU lane | 0 of 3 landed; escalated to Cursor |
| Planning logic bodies | local GPU lane | 5 of 6 landed; the script validator escalated |
| Step-script overrides | local GPU lane | 12 of 17 kept after the ply-coverage filter; one written by hand |
| Sourcing research, integrated player, narrow layout, default flip | Opus | |
| Hosted lanes | not used | they need a live run grant; owner decision pending |
