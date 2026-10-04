VERDICT: FAIL (bounded, round 1)

# Block 2 M2.7 visual review (chapters 19 and 20, wings and winglets), Opus captain

Reviewed branch m27-crewA at 9fd18d0, using crew B's WebKit 1180x820 shots of all 27 f19/f20 ops and the phone shots of
`f19.aileron-build`, `f20.jig` and `f20.rudder-hang`. The shots stay in the session scratchpad and are not committed.

## Passes
- The wing bench reads as a build. There are five plywood jigs, the cores are on the table, and the wing is back in the jigs
  LE-up. The bottom and top caps and skins lay down ply by ply, with the readout counting plies (5/5, 7/7, 3/3).
- `f19.shear-web` carries "BL 120 to 157: 2 plies (CP26 LPC 31; plans print 3)". The three conflicts appear as text on
  their ops:
  - the 134.95 / 134.45 label on `f19.cut-cores`;
  - BL 54.3 / 55.5 on `f19.aileron-cut`;
  - 28.85 / 28.83 on `f19.attach`.
- `f19.aileron-build` deflects to the 20 deg stop with a slider, and `f20.rudder-hang` swings to 30 deg.
- `f20.jig` draws A 102.15, B 108.35 and C 118.35 from the reference point (BL 55.5, FS 149.6). The readout gives the
  closure residuals and calls the lean derived, low confidence. This is the best shot of the milestone.
- The CP26 builder-weight rows show as "reference, not in CG", and CG stays not computed. Representational parts are
  striped and labelled.

## Fails (must fix)
1. `f19.attach`: the camera is a close-up of the spar end and a striped wall. The owner cannot see a wing on the airplane.
   It must frame both wings on the fuselage at the spar, in a three-quarter view from above.
2. `f19.controls`, `f19.hardpoints` and `f19.pads-plates`: the camera sits inside or against the wing root. The frame is
   stripes and a translucent box, so nothing can be read. Pull back so the root bay, the hard points and the plates read
   against the inboard core, with the wing outline visible.
3. `f20.cut-cores`, `f20.skins` and `f20.trim`: the winglet already stands on the wingtip. In the book it is cut, skinned
   flat and trimmed on the table, and it meets the wing only at `f20.jig`. Show it on the bench, lying flat, until
   `f20.jig`.

## Nits (open, not blocking)
- Tiny hardware (hinges, bolts) reads small. It is labelled.
- `f19.core-cutouts`: the camera clips a jig face at the left edge.
- The rudder hinge is seen through the faint winglet, from the wall side.
