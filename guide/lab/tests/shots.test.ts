import test from 'node:test'
import assert from 'node:assert/strict'
import { labShots, type Tour } from '../src/shots'

const tours: Record<string, Tour> = {
  'r30.top-skin': { target: [6, 0.8, -33], position: [10, 75, 28] },
  'r30.bottom-skin': { target: [6, 0, -33], position: [10, -75, 28] },
  'x.unknown': { target: [1, 2, -3], position: [1, 50, -3] },
}

test('every tour op gets a lab shot that keeps the authored target', () => {
  const s = labShots(tours)
  assert.deepEqual(Object.keys(s).sort(), Object.keys(tours).sort())
  for (const [id, t] of Object.entries(tours)) assert.deepEqual(s[id].target, t.target)
})

test('the eye is 30-40 degrees above the working surface, on the leading-edge side, in the canard frame', () => {
  const s = labShots(tours)
  for (const [id, sign] of [['r30.top-skin', 1], ['r30.bottom-skin', -1]] as const) {
    const [dx, dy, dz] = s[id].position.map((v, i) => v - s[id].target[i])
    assert.equal(Math.sign(dy), sign)
    const el = (Math.atan2(Math.abs(dy), Math.hypot(dx, dz)) * 180) / Math.PI
    assert.ok(el >= 30 && el <= 40, `${id} elevation ${el}`)
    assert.ok(dx < 0, 'leading edge is -X')
    assert.ok(Math.hypot(dx, dy, dz) < 70, 'a close view, not the 2.1 fly-over')
  }
})

test('a vertical-face op (shear web) is viewed from above the table in either pose', () => {
  const t = { 'r30.shear-web': { target: [3, 0.4, -20], position: [9, 6, 8] } } as Record<string, Tour>
  assert.ok(labShots(t, () => 'upright')['r30.shear-web'].position[1] > 0.4)
  assert.ok(labShots(t, () => 'inverted')['r30.shear-web'].position[1] < 0.4) // canard frame: -Y is up in the world while inverted
})
