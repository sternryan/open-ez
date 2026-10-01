import test from 'node:test'
import assert from 'node:assert/strict'
import { lowerLift, lowerProgress, LOWER_HEIGHT, LOWER_SECONDS } from '../src/logic/lower'

test('the canard hangs 24 in up until the descent starts and is exactly at its installed pose when it ends', () => {
  assert.equal(LOWER_HEIGHT, 24)
  assert.equal(lowerLift(-3), 24)
  assert.equal(lowerLift(0), 24)
  assert.equal(lowerLift(LOWER_SECONDS), 0)
  assert.equal(lowerLift(LOWER_SECONDS + 5), 0)
})

test('the descent is eased: monotone down, never below the installed pose, slow at both ends', () => {
  let prev = Infinity
  for (let t = 0; t <= LOWER_SECONDS; t += 0.05) {
    const h = lowerLift(t)
    assert.ok(h <= prev + 1e-12 && h >= 0 && h <= LOWER_HEIGHT, `t=${t} h=${h}`)
    prev = h
  }
  assert.ok(24 - lowerLift(0.35) < 0.5, 'a gentle start')
  assert.ok(lowerLift(LOWER_SECONDS - 0.35) < 0.5, 'a gentle landing')
  assert.ok(Math.abs(lowerLift(LOWER_SECONDS / 2) - 12) < 1e-9, 'half way at half time')
})

test('progress is 0 hanging, 1 installed', () => {
  assert.equal(lowerProgress(-1), 0)
  assert.equal(lowerProgress(LOWER_SECONDS), 1)
  assert.ok(Math.abs(lowerProgress(LOWER_SECONDS / 2) - 0.5) < 1e-9)
})
