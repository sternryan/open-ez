import test from 'node:test'
import assert from 'node:assert/strict'
import { Player } from '../src/player'
import { compileStep, type Beat } from '../src/logic/actions'

// Three steps: a: two beats (place 1.2 s, wet-out 1.0 s); b: caption only (2.5 s); c: one squeegee beat (1.4 s).
const beats = (): Map<string, Beat[]> =>
  new Map([
    ['a', compileStep([{ do: 'place', ply: 1, who: 'owner' }, { do: 'wet-out', ply: 1, tool: 'brush', who: 'owner' }], 'Step A', 1)],
    ['b', compileStep(undefined, 'Step B', 0)],
    ['c', compileStep([{ do: 'squeegee', ply: 1, tool: 'squeegee', who: 'owner' }], 'Step C', 1)],
  ])
const order = ['a', 'b', 'c']

test('a new player sits paused at the start of the first step', () => {
  const p = new Player(beats(), order)
  assert.equal(p.step, 'a')
  assert.equal(p.playing, false)
  assert.equal(p.speed, 1)
  const r = p.tick(5)
  assert.deepEqual([r.step, r.k, r.changed], ['a', 0, false], 'paused: time does not move')
  assert.equal(r.beat?.caption, 'place ply 1 of 1')
})

test('tick crosses beat and step boundaries; changed is true only on the tick that enters a step', () => {
  const p = new Player(beats(), order)
  p.play()
  let r = p.tick(0.6)
  assert.equal(r.step, 'a')
  assert.equal(r.beat?.action?.do, 'place')
  assert.ok(Math.abs(r.k - 0.5) < 1e-9, `k ${r.k}`)
  assert.equal(r.changed, false)
  r = p.tick(0.7) // 1.3 s into a: the wet-out beat
  assert.equal(r.beat?.action?.do, 'wet-out')
  assert.ok(Math.abs(r.k - 0.1) < 1e-9, `k ${r.k}`)
  r = p.tick(1.0) // past a's 2.2 s
  assert.equal(r.step, 'b')
  assert.equal(r.changed, true)
  assert.equal(r.k, 0)
  r = p.tick(0.1)
  assert.equal(r.step, 'b')
  assert.equal(r.changed, false)
})

test('a tick enters at most one new step, so every step is seen', () => {
  const p = new Player(beats(), order)
  p.play()
  const seen: string[] = []
  for (let i = 0; i < 20; i++) {
    const r = p.tick(100)
    if (r.changed) seen.push(r.step)
  }
  assert.deepEqual(seen, ['b', 'c'])
})

test('speed scales sim time', () => {
  const p = new Player(beats(), order)
  p.setSpeed(4)
  assert.equal(p.speed, 4)
  p.play()
  const r = p.tick(0.15) // 0.6 s of sim time
  assert.ok(Math.abs(r.k - 0.5) < 1e-9, `k ${r.k}`)
  p.setSpeed(16)
  const r2 = p.tick(0.1) // 1.6 s more: 2.2 s into a, the end of a, so b is entered
  assert.equal(r2.step, 'b')
  assert.equal(r2.changed, true)
})

test('seekStep resets to the start of that step and keeps the play state', () => {
  const p = new Player(beats(), order)
  p.play()
  p.tick(1.5)
  p.seekStep('c')
  assert.equal(p.step, 'c')
  assert.equal(p.playing, true)
  const r = p.tick(0)
  assert.equal(r.k, 0)
  assert.equal(r.beat?.action?.do, 'squeegee')
  assert.equal(r.changed, false, 'a seek is not a tick entering a step: the caller applies it')
  p.pause()
  p.seekStep('a')
  assert.equal(p.playing, false)
  assert.equal(p.tick(1).k, 0)
  p.seekStep('nope')
  assert.equal(p.step, 'a', 'an unknown id is ignored')
})

test('next and prev move whole steps and stop at the ends', () => {
  const p = new Player(beats(), order)
  p.prev()
  assert.equal(p.step, 'a')
  p.next()
  assert.equal(p.step, 'b')
  p.next()
  p.next()
  assert.equal(p.step, 'c')
  p.prev()
  assert.equal(p.step, 'b')
})

test('a caption-only step advances after its finite duration', () => {
  const p = new Player(beats(), order)
  p.seekStep('b')
  p.play()
  let r = p.tick(2.4)
  assert.equal(r.step, 'b')
  assert.equal(r.beat?.action, null)
  assert.equal(r.beat?.caption, 'Step B')
  r = p.tick(0.2)
  assert.equal(r.step, 'c')
  assert.equal(r.changed, true)
})

test('a step with no beats at all still advances (a caption-only default)', () => {
  const p = new Player(new Map([['x', []], ['y', compileStep(undefined, 'Y', 0)]]), ['x', 'y'])
  p.play()
  const r = p.tick(10)
  assert.equal(r.step, 'y')
})

test('the end of the last step pauses on the last step', () => {
  const p = new Player(beats(), order)
  p.seekStep('c')
  p.play()
  const r = p.tick(5)
  assert.equal(r.step, 'c')
  assert.equal(r.k, 1)
  assert.equal(p.playing, false)
  assert.equal(p.tick(1).changed, false)
  p.play() // play at the end starts over from the first step
  assert.equal(p.step, 'a')
  assert.equal(p.playing, true)
})

test('time never runs on NaN or negative input', () => {
  const p = new Player(beats(), order)
  p.play()
  for (const dt of [Number.NaN, -1, Number.POSITIVE_INFINITY]) {
    const r = p.tick(dt)
    assert.ok(Number.isFinite(r.k) && r.k >= 0 && r.k <= 1, `dt ${dt} gave k ${r.k}`)
  }
})

test('an empty order makes a player that does nothing', () => {
  const p = new Player(new Map(), [])
  p.play()
  const r = p.tick(1)
  assert.equal(r.step, '')
  assert.equal(r.beat, null)
  assert.equal(p.playing, false)
})
