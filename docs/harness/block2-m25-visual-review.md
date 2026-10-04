VERDICT: PASS WITH NITS

# Block 2 M2.5 visual review (chapters 14-17), Opus captain

Reviewed: branch m25-crewB at 6532865. The crew built the site and captured every non-stub ch14-17 op in WebKit at
1180x820, plus phone shots (390x844) of `f14.fit-fuselage` and `f16.pitch-pushrod`. Screenshots stay in the session
scratchpad. They are not committed.

## Round 1 (ee1f4c7): FAIL, bounded
1. Ship-blocking: on `f16.pitch-pushrod` the stick-driven Roncz elevators were never on screen.
2. The spar CP26 prototype row (29.3 lb) was missing from the readout.
3. The spar jig shared the layup table's colour and did not read in `f14.jig`.
4. `f14.sh1-tabs`, `f17.mount-blocks` and `f16.sticks-pushrods` were occluded or framed too tightly.
5. Some labels showed only a dot, with no text.

## Round 2 (6532865): PASS WITH NITS
- `f16.pitch-pushrod`: the elevators are in frame along the canard trailing edge. A pixel e2e test pins the elevator
  region changing between 15 deg up and 30 deg down. The readout uses Roncz numbers only (30 down, 15 up, 12.5 floor).
- The spar row reads "Spar (CP26 prototype): 29.3 lb, reference, not in CG". It sits outside cg and cg_lower_bound,
  so CG stays "not yet computed".
- The jig is a distinct pale material, and its swept top view reads.
- Every new solid is striped and labelled "(fitted shape)". The pitch stops read "(not printed; fitted shape)".
- The spar slides in from the side (`f14.fit-fuselage`), per plans p87. CP25 only defers the firewall bond.

## Nits (open, not blocking)
- `f14.sh1-tabs` is still a busy close-up (263 px subject).
- `f17.mount-blocks`: the pivot bulkhead dominates the foreground. The roll-trim levers are visible.
- `f16.pitch-pushrod`: the front stick is not clearly in this shot (it is in `f16.sticks-pushrods`). On the phone
  shot the elevators are small.
- The firewall sits on the layup table through the ch6-7 ops. This follows from the CP25 bond order.
- `f14.lwa-fabricate` shows the plates installed, not laid out loose.
