import { test } from 'node:test'
import assert from 'node:assert/strict'
import { coveFrom, inCove, coveExit, coveCap } from '../src/logic/cove'

// the export's numbers for the sake of the arithmetic: the elevators' leading edge x 9.11, the hinge slot gap 0.2, the outboard end B.L. 65
const c = coveFrom(9.11, 0.2, 65)

test('the cut is the elevators leading edge less the slot gap, and the span is the elevators', () => {
  assert.ok(Math.abs(c.xCut - 8.91) < 1e-12)
  assert.equal(c.blEnd, 65)
})

test('a point is removed only aft of the cut and inboard of the elevators outboard end; the tips and the nose keep their shape', () => {
  assert.ok(inCove(c, [12, 0.3, -30]))
  assert.ok(inCove(c, [12, 0.3, 30])) // either side of the centre line
  assert.ok(!inCove(c, [8.9, 0.3, -30])) // forward of the cut (the slot gap is the 0.2 in between)
  assert.ok(!inCove(c, [12, 0.3, -66])) // the tip, full chord
  assert.ok(!inCove(c, [12.9, 0.3, 70.8]))
  assert.ok(!inCove(c, [0.1, 0.3, 0]))
  // y does not matter: a through cut
  assert.equal(inCove(c, [11, -5, 10]), inCove(c, [11, 5, 10]))
})

test('a ray from aft leaves the box through the cut wall; from above it leaves through the wall after crossing the box', () => {
  const aft = coveExit(c, [20, 0.3, -30], [-1, 0, 0])
  assert.ok(aft && aft.face === 'x' && Math.abs(aft.t - (20 - c.xCut)) < 1e-9)
  const s = Math.SQRT1_2
  const above = coveExit(c, [12, 5, -30], [-s, -s, 0]) // down and forward: leaves the box at x = cut
  assert.ok(above && above.face === 'x' && Math.abs(above.t - (12 - c.xCut) / s) < 1e-9)
  // a ray that misses the box (beyond the outboard end, parallel to x) crosses nothing
  assert.equal(coveExit(c, [20, 0.3, -66], [-1, 0, 0]), null)
  // a ray travelling along the span inside the box leaves through the span end wall at B.L. 65 (its inward normal is +z)
  const along = coveExit(c, [11, 0.3, -10], [0, 0, -1])
  assert.ok(along && along.face === 'z+' && Math.abs(along.t - 55) < 1e-9)
})

test('the cap: a back face seen through the box is a cap at the wall, facing into the box, and only if the ray left the box before reaching it', () => {
  // the camera aft looking at the inside of the leading edge (a back face at x = 0.1): the wall at x = cut shows
  const cap = coveCap(c, [30, 0.3, -30], [0.1, 0.3, -30])
  assert.ok(cap && cap.face === 'x')
  assert.ok(Math.abs(cap.point[0] - c.xCut) < 1e-9 && Math.abs(cap.point[2] + 30) < 1e-9)
  assert.deepEqual(cap.normal, [1, 0, 0])
  // a back face that is itself inside the box lies in what was removed (the shader discards it before it can be a cap): the ray never leaves the box first
  assert.equal(coveCap(c, [30, 0.3, -30], [12, 0.3, -30]), null)
  // a ray that does not cross the box (a tip seen from outboard) shows no cap
  assert.equal(coveCap(c, [30, 0.3, -80], [0.1, 0.3, -70]), null)
})
