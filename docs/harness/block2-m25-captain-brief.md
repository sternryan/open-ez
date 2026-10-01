# Block 2 milestone 2.5 (chapters 14–17): captain brief

Role, method, gates and hygiene are exactly as in `docs/harness/block2-m24-captain-brief.md` (read
it, and the M2.4 captain log for what worked). Restated because they bit:
- everything you wait on runs in the FOREGROUND, every crew call and every test run;
- the commit hook credits a test run only when it is the last segment of its command: run pytest
  bare, then commit in a separate call;
- no push, deploy or publish; named files; no trailers of any kind.

The lead approved under the owner's delegation.

**Spec:** `docs/superpowers/specs/2026-10-01-block2-m25-spar-firewall-controls-trim-design.md`
(§3 holds the lead's rulings: firewall bond order, no double count, new edges, wing/winglet stubs).
**Evidence:** `docs/harness/m25-ch14-17-research.md`. Decompose spec §5 into tasks, in this order,
each gated and committed:
1. source notes, config values (spar stations, depth, sweep, hard points, control and trim
   stations, Roncz travel already present) and the ledger spar row; correct the "7 in spar" note;
2. graph ch14–17, the moved firewall bond and the new edges, the c19/c20 stubs;
3. spar geometry (planform, caps as plies, hard points, LWA plates);
4. firewall face and controls geometry (pivot planes, torque tube, pushrod kinematics);
5. the lab (spar jig and cap lay-down, slide-in, stick-driven elevator travel, trim, striping, cuts);
6. tour and the spar slide-in film.

## Lanes

- Op YAML: a Sonnet crew drafts directly (the smithy drafts all needed hand fixes in M2.4; log the
  skip with that reason).
- `/conduct` for one-file kernels fully expressed by tests (planform maths, cap taper schedule,
  pushrod kinematics). It worked in M2.4; keep using it.
- Sonnet crews for multi-file and lab work. No Opus; the lead runs the visual review.

## Specifics

- Re-read every model-bound value on the page image yourself. Low-confidence items from the
  research: the p85 "29.84" label (p88's 28.82 checks), p101 hand ticks, stick pivot FS 45.5 and
  89.7, the p106 FS 49.8 vs 49.5.
- Moving `f06.bond-firewall` after `f14.fit-fuselage` must not silently change the chapter 4–9
  lab assertions. If an e2e assertion has to move, say which and why in the report.
- The Roncz elevator travel row is the only one the controls kinematics may use.
- Log `docs/harness/block2-m25-captain.md`; report `docs/harness/block2-m25-captain-report.md`.
  Your final message is the report path and a ≤15-line summary.
