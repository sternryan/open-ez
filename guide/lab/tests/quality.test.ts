import test from 'node:test'
import assert from 'node:assert/strict'
import { nextRes, initialRes, RES_MIN, tierPixelRatio, TIERS, TIER_ORDER, parseTier, startTier, nextTier, initialStep, median, SLOW_MS, WINDOW_MS, SETTLE_MS, type StepState } from '../src/quality'

const feed = (s: StepState, ms: number, n: number) => { for (let i = 0; i < n; i++) s = nextTier(s, ms); return s }

test('the table gets cheaper at every step', () => {
  const [h, m, l] = TIER_ORDER.map((t) => TIERS[t])
  assert.deepEqual([h.ao, h.dof, h.bloom, h.msaa, h.dprCap], [true, true, true, 4, 2])
  assert.deepEqual([m.ao, m.dof, m.bloom, m.dprCap], [true, false, true, 1.5])
  assert.deepEqual([l.ao, l.dof, l.bloom, l.msaa, l.dprCap, l.cheapShaders], [false, false, false, 0, 1, true])
  assert.ok(h.aoSamples > m.aoSamples && h.aoScale > m.aoScale)
  assert.ok(m.msaa > 0 && m.msaa < h.msaa)
  assert.ok(h.shadowMap > m.shadowMap && m.shadowMap > l.shadowMap)
  assert.equal(h.cheapShaders || m.cheapShaders, false)
  assert.ok(l.maxPixels < 1_000_000 && l.shadowMap === 0 && h.shadowMap > 0)
})

test('pixel ratio: device ratio under the tier cap, and the low tier stays under its pixel ceiling', () => {
  assert.equal(tierPixelRatio(TIERS.high, 2, 1180, 820), 2)
  assert.equal(tierPixelRatio(TIERS.high, 3, 390, 844), 2)
  assert.equal(tierPixelRatio(TIERS.mid, 2, 1180, 820), 1.5)
  const r = tierPixelRatio(TIERS.low, 2, 1180, 820)
  assert.ok(r < 1 && 1180 * r * 820 * r <= TIERS.low.maxPixels + 1)
  assert.equal(tierPixelRatio(TIERS.low, 2, 390, 844), 1) // a phone screen is already under the ceiling
  assert.ok(tierPixelRatio(TIERS.low, 1, 100000, 100000) >= 0.25)
})

test('?q= parsing', () => {
  assert.equal(parseTier('high'), 'high'); assert.equal(parseTier('mid'), 'mid'); assert.equal(parseTier('MEDIUM'), 'mid'); assert.equal(parseTier('low'), 'low')
  assert.equal(parseTier(null), null); assert.equal(parseTier(''), null); assert.equal(parseTier('ultra'), null)
})

test('start tier: high on desktop and iPad-class, medium on phones', () => {
  assert.equal(startTier({ coarse: false, width: 1400, height: 860 }), 'high')
  assert.equal(startTier({ coarse: false, width: 390, height: 844 }), 'high') // a narrow desktop window is still a desktop
  assert.equal(startTier({ coarse: true, width: 1180, height: 820 }), 'high') // iPad landscape
  assert.equal(startTier({ coarse: true, width: 820, height: 1180 }), 'high') // iPad portrait
  assert.equal(startTier({ coarse: true, width: 768, height: 1024 }), 'high')
  assert.equal(startTier({ coarse: true, width: 390, height: 844 }), 'mid') // phone
  assert.equal(startTier({ coarse: true, width: 844, height: 390 }), 'mid') // phone landscape
})

test('steady 60 Hz never drops', () => {
  let s = initialStep('high')
  s = feed(s, 16.7, 600)
  assert.equal(s.tier, 'high')
})

test('a 30 Hz display is not slow, a 25 Hz one is', () => {
  assert.equal(feed(initialStep('high'), 33.3, 300).tier, 'high')
  assert.equal(feed(initialStep('high'), 40, 45).tier, 'mid')
})

test('drops after about 1.5 s of slow frames, not before', () => {
  let s = initialStep('high')
  let t = 0
  while (s.tier === 'high' && t < 5000) { s = nextTier(s, 50); t += 50 }
  assert.equal(s.tier, 'mid')
  assert.ok(t >= WINDOW_MS && t <= WINDOW_MS + 100, `dropped at ${t} ms`)
})

test('a short hitch does not drop: the median has to be slow', () => {
  let s = initialStep('high')
  for (let i = 0; i < 20; i++) { s = feed(s, 16.7, 10); s = nextTier(s, 200); s = nextTier(s, 200) } // 2 spikes in every 12 frames
  assert.equal(s.tier, 'high')
})

test('one huge frame (tab back from the background) counts as at most half a second', () => {
  let s = feed(initialStep('high'), 16.7, 50)
  s = nextTier(s, 30000)
  assert.equal(s.tier, 'high')
})

test('steps one tier at a time, settles after each drop, never goes below low', () => {
  let s = initialStep('high')
  s = feed(s, 60, 40)
  assert.equal(s.tier, 'mid')
  assert.ok(s.settle > 0 || s.frames.length > 0)
  // frames right after a drop (the recompile) are ignored
  s = { ...s, frames: [], sum: 0, settle: SETTLE_MS }
  s = feed(s, 400, 2)
  assert.equal(s.tier, 'mid')
  s = feed(s, 60, 60)
  assert.equal(s.tier, 'low')
  s = feed(s, 500, 200)
  assert.equal(s.tier, 'low')
})

test('no step-up: fast frames after a drop keep the lower tier', () => {
  let s = feed(initialStep('high'), 60, 40)
  assert.equal(s.tier, 'mid')
  s = feed(s, 8, 5000)
  assert.equal(s.tier, 'mid')
})

test('median helper and constants', () => {
  assert.equal(median([3, 1, 2]), 2); assert.equal(median([]), 0)
  assert.ok(SLOW_MS >= 33 && WINDOW_MS === 1500)
})

const feedRes = (s: ReturnType<typeof initialRes>, ms: number, n: number) => { for (let i = 0; i < n; i++) s = nextRes(s, ms); return s }

test('adaptive resolution: steady 60 Hz keeps full resolution', () => {
  assert.equal(feedRes(initialRes(), 16.7, 1000).scale, 1)
})

test('adaptive resolution: slow frames shrink the pixel count in steps, never below the floor, and never grow back', () => {
  let s = initialRes()
  const seen: number[] = []
  for (let i = 0; i < 3000; i++) { s = nextRes(s, 100); if (!seen.length || s.scale !== seen[seen.length - 1]) seen.push(s.scale) }
  assert.ok(seen.length >= 4 && seen[0] === 1)
  assert.ok(seen.every((v, i) => i === 0 || v < seen[i - 1]))
  assert.equal(s.scale, RES_MIN)
  const after = feedRes(s, 8, 2000)
  assert.equal(after.scale, RES_MIN) // no step back up
})

test('adaptive resolution: a step is at most half, and the frames right after it are ignored', () => {
  let s = feedRes(initialRes(), 400, 3)
  assert.equal(s.scale, 0.5)
  assert.ok(s.settle > 0)
  s = feedRes(s, 400, 1)
  assert.equal(s.scale, 0.5)
})

test('adaptive resolution: a mostly-on-time run with the odd long frame is left alone (the 75th percentile decides)', () => {
  let s = initialRes()
  for (let i = 0; i < 40; i++) { s = feedRes(s, 16.7, 5); s = nextRes(s, 50) }
  assert.equal(s.scale, 1)
})
