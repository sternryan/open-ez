VERDICT: PASS WITH NITS (round 2); round 1 FAIL (bounded)

# Block 2 M2.8 visual review (chapters 21 to 23), Opus captain

Reviewed branch m28 at 05f03d8, from crew B's WebKit 1180x820 shots of all 23 f21/f22/f23 ops plus four phone shots
(390x844). The shots stay in the session scratchpad and are not committed.

## Passes
- Chapter 21 reads as a build.
  - The kit lies on the table (`f21.cut-parts`), then the jig table and the inside layups.
  - The shaded blue tank volume shows inside both strakes (`f21.close-tank`, `f21.pressure-check`).
  - The skins, the sump blister and the leading-edge fairings follow.
- The readouts carry the uncertainties as text:
  - the capacity conflict (plans 2 x 25.5, manual 2 x 28 / 52, model 26, envelope 24.6);
  - the "layup 7 printed twice" note;
  - the cutout-depth conflict;
  - the battery station "FS 0 to 22, not printed (A6 only)";
  - the starter bound "station 150 or aft";
  - the engine limits 246 / 286 lb.
- The N26MS ladder and the closure target (730 lb at FS 111.7) are reference rows. CG stays not computed.
- `f22.battery-shelf` shows the battery, strap and shelf in the nose.
- `f23.engine-install` shows the striped block labelled "installation in Section II, not held".
- The phone shots are readable.

## Fails (must fix)
1. `f21.vent-screen`: the camera faces a striped translucent wall, and the vent line and screen are specks. Pull back
   so the vent line runs along the strake with the screen at its end.
2. `f22.wing-wiring`: the camera faces the shop window and a wall. Only the green position light is readable, and the
   conduit along the wing does not read. Frame the right wing's TE run from above, with the light at the tip.
3. `f22.antennas`: a top-down sliver with no airplane context. Frame the antenna strip on the canard or
   fuselage so its location reads.
4. `f23.root-rib`: the rib is lost in overlapping striped translucent volumes. Frame one wing root from aft and
   below, with the metal rib against the strake and wing.

## Nits (open, not blocking)
- The engine block dominates the chapter 23 shots. It is honest (the size is the 246 lb class envelope), but it is
  big.
- `f22.microswitches` and `f22.panel-wiring` read through layers of striping. They are acceptable.
- The left wingtip sits beyond the shop wall (a room-size limit from M2.7).

## Round 2 (captain, after crew B 6e188ba)
- `f22.antennas`: both nav antenna strips on the canard with F22/F28 and the fuselage behind. Pass.
- `f22.wing-wiring`: the right wing from above with the green position light at the tip. Pass.
- `f23.root-rib`: both wing-root metal ribs labelled against the strake and wing roots, aft-left. Pass.
- `f21.vent-screen`: closer, with the vent line and both screens coloured and labelled, but the striped tank wall still fills
  the frame; the parts are small by nature (a tube and a screen). Pass with nit.
