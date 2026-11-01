# Rehearsal player: lanes preflight (phase 0)

Date: 2026-10-17. Branch `feat/rehearsal-p1` at the plan commit `cc383e6`, based on `origin/main` `e09c22d`.
Host names are deliberately omitted (public repo); roles are named instead.

## Lanes

| Lane | Model id | Verified | Result |
|---|---|---|---|
| cursor-grok | `grok-4.7-medium` | 2026-10-17, Cursor model list + one live call | PASS: answered OK. |
| cursor web | same | 2026-10-18, re-probed with `--force` | HAS WEB (WebSearch, WebFetch). The 2026-10-17 "no web" result was a probe error: without `--force` the agent cannot use tools. Public research goes to cursor-grok. |
| opus | Claude subscription `opus` | harness id | available to the lead |
| astra | `gpt-6-astra` | 2026-10-17, Codex models catalog | available; budget ≤2 calls per phase |
| local | the local GPU lane | 2026-10-17, scheduler `/v1/models` | listed |
| hosted | two hosted open-weight lanes | 2026-10-17, scheduler `/v1/models` | listed |
| push-gate grader | `claude -p --model sonnet` (`grade-diff.sh`) | 2026-10-17, read the script | Sonnet, with a per-tree cached verdict. Independent of Grok-built work; Opus-built work also gets Astra's batched phase grade. |

## Baseline (untouched tree)

| Suite | Where | Result |
|---|---|---|
| TS (`npm test`, `npm run typecheck`) | authoring host | 260 passed, typecheck clean |
| PY (`pytest tests/guide`, browser files excluded) + `guide.check --schema-only` | authoring host | 321 passed, 1 skipped; check OK |
| E2E (`test_lab_e2e.py`, `test_viewer_e2e.py`) | authoring host | 2 failures (ghosting pixel check, low-tier frame time) and 3 h 17 m: software GL on a loaded host |
| same two failing tests | owner's laptop | 3 passed |
| E2E full | browser-test host (Apple silicon) | **408 passed**, chromium + webkit, 1 h 05 m |
| `conduct --lint` (empty plan) | authoring host | rc 0; one finding `ledger_missing`, so real plans set `ledger_cli` |

## Decisions recorded

- Authoring, unit suites and conduct run on the authoring host. **E2E runs on the browser-test host.** The authoring host's
  software-GL timings are not a valid environment for the frame-time and pixel tests.
- Sourcing research is `[cursor-grok]` with `--force` (public content only); the 10-17 move to `[opus]` rested on the probe error above.
