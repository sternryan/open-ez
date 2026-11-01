import test from 'node:test'
import assert from 'node:assert/strict'
import { nextRes, initialRes, holdRes, RES_MIN, CHANGE_SETTLE_MS } from '../src/quality'

const feedRes = (s: ReturnType<typeof initialRes>, ms: number, n: number) => { for (let i = 0; i < n; i++) s = nextRes(s, ms); return s }

test('a burst of slow frames during a step change does not lower res', () => {
  // the same burst with no step change is enough to step down
  assert.ok(feedRes(initialRes(), 100, 8).scale < 1)
  let s = holdRes(initialRes())
  assert.ok(s.settle >= CHANGE_SETTLE_MS)
  s = feedRes(s, 100, 8) // inside the settle window: the swap, not the device
  assert.equal(s.scale, 1)
})

test('sustained fast frames raise res back, and it never passes 1 or the floor', () => {
  let s = feedRes(initialRes(), 100, 400)
  assert.equal(s.scale, RES_MIN)
  s = feedRes(s, 8, 20000)
  assert.ok(s.scale > RES_MIN, `stayed at ${s.scale}`)
  assert.ok(s.scale <= 1)
  // already full, and a long slow run: the two ends of the range
  assert.equal(feedRes(initialRes(), 8, 20000).scale, 1)
  assert.ok(feedRes(initialRes(), 100, 5000).scale >= RES_MIN)
})

test('a steady slow device still steps down', () => {
  const s = feedRes(initialRes(), 100, 400)
  assert.equal(s.scale, RES_MIN)
  assert.ok(s.scale < 1)
})

test('resolution recovers across regular ten-second step changes', () => {
  // 100 smooth ten-second steps, starting at the floor. A step change excludes its settle window only.
  let s = feedRes(initialRes(), 100, 400)
  assert.equal(s.scale, RES_MIN)
  const frames = Math.round(10_000 / 16.7)
  for (let step = 0; step < 100; step++) {
    s = holdRes(s)
    s = feedRes(s, 16.7, frames)
  }
  assert.ok(s.scale > RES_MIN, `100 smooth ten-second steps stayed at ${s.scale}`)
})

test('a steady slow device still steps down across step changes', () => {
  let s = initialRes()
  const frames = Math.round(10_000 / 100)
  for (let step = 0; step < 30; step++) {
    s = holdRes(s)
    s = feedRes(s, 100, frames)
  }
  assert.equal(s.scale, RES_MIN)
})
