# Hangar H2 proof run (plan Task 8)

Date: 2026-10-18. Host names are omitted (public repo); roles are named instead.

## Setup
- Site built from the branch with `guide.build_site` (private build) and served with the GLB from the rehearsal preview.
- `hangar.briefing_server` ran on the authoring host as the unprivileged build user, bound to loopback, behind a
  private tailnet proxy (`--allow-origin`). Council: the local GPU lane through the scheduler's OpenAI-compatible
  endpoint, set by environment variables on the host only. `HANGAR_PRIVATE_DIR` outside the repo.

## What happened
- Smoke tests before the owner's session found three defects, fixed and tested before the run: proxied requests
  were refused by the Host check; the council's numeric confidence and sentence-valued judgment were collapsed to
  "low, opinion" and comment-only advice was dropped; then the record gate rejected comment-only positions (a 409 to
  the owner's first question). After the fixes all five roles answered in about 7-8 s per turn.
- The owner opened the Hangar index and the briefing room on the iPad, asked the council about the 912 iS against the
  915/916 iS, and closed the record.

## Verification (observed)
- `validate_all()` on the decided tree: `[]`.
- Record `powerplant-fuel-resin`: `status: decided`, picks `engine: rotax-912is`, `fuel_path: ul94-ethanol-free`,
  dated 2026-10-18, with the owner's reason; one history entry `open -> decided` carrying the same picks.
- `GET /api/records` through the proxy returned the decided status and picks.
- `git status` on the authoring clone: only the record file modified.
- The transcript exists only under the private directory; no `*.jsonl` in the repo.

## Known follow-ups
- The service re-dumps YAML at the default line width, so a decision diff also re-wraps long strings. Dump with the
  repo's existing width so owner reviews show only real changes.
- The 915/916 iS cruise fuel flows and installed weights were still being sourced when the owner decided; if they
  change the case, the record is reopened in the briefing room, not edited.
