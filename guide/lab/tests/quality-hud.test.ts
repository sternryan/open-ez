import test from 'node:test'
import assert from 'node:assert/strict'
import { emptyFrames, frameStats, formatHud, noteTransition, pushFrameWindow, HUD_LOG_KEEP, HUD_WINDOW_MS, type HudSnapshot } from '../src/quality'

const snap = (over: Partial<HudSnapshot> = {}): HudSnapshot => ({
  tier: 'high', auto: true, resScale: 1, pixelRatio: 2, devicePixelRatio: 2,
  medianMs: 8.3, p75Ms: 9.1, tierSteps: 0, resSteps: 0, lastTierAtMs: null, lastResAtMs: null,
  step: 'f20.inside-layups', log: [], ...over,
})

test('frame window keeps about the last two seconds and reports median and p75', () => {
  let w = emptyFrames()
  w = pushFrameWindow(w, 400) // old hitch, must fall out of the window
  for (let i = 0; i < 400; i++) w = pushFrameWindow(w, 10)
  assert.ok(w.sum >= HUD_WINDOW_MS && w.sum < HUD_WINDOW_MS + 10, `sum ${w.sum}`)
  assert.ok(w.frames.every((ms) => ms === 10))
  const s = frameStats(w)
  assert.equal(s.n, w.frames.length)
  assert.equal(s.medianMs, 10)
  assert.equal(s.p75Ms, 10)
  // a known mix: twenty 100 ms frames fill the window exactly
  let even = emptyFrames()
  for (let i = 0; i < 25; i++) even = pushFrameWindow(even, 100)
  assert.equal(even.frames.length, 20)
  assert.equal(frameStats(even).medianMs, 100)
  assert.equal(frameStats(even).p75Ms, 100)
  assert.equal(frameStats(emptyFrames()).medianMs, 0)
  assert.equal(frameStats(emptyFrames()).p75Ms, 0)
})

test('the readout names tier, auto, resolution, pixel ratios, frame times, step counts and the recent log', () => {
  const text = formatHud(snap({
    tierSteps: 2, lastTierAtMs: 12400, resSteps: 1, lastResAtMs: 4000,
    log: [
      { atMs: 12400, kind: 'tier', from: 'high', to: 'mid', step: 'f18.pads-inside-glass' },
      { atMs: 18100, kind: 'tier', from: 'mid', to: 'low', step: 'f18.pads-inside-glass' },
    ],
  }))
  assert.equal(text, [
    'High · auto',
    'res 1.00 · px 2.00 / dpr 2.00',
    'med 8.3 · p75 9.1 ms',
    'tier ×2 @ 12.4s · res ×1 @ 4.0s',
    'f20.inside-layups',
    '12.4s tier high -> mid f18.pads-inside-glass',
    '18.1s tier mid -> low f18.pads-inside-glass',
  ].join('\n'))
  const manual = formatHud(snap({ tier: 'low', auto: false, resScale: 0.2, pixelRatio: 0.59, devicePixelRatio: 2, medianMs: 33.3, p75Ms: 40, step: '' }))
  assert.equal(manual.split('\n')[0], 'Low · manual')
  assert.match(manual, /res 0\.20 · px 0\.59 \/ dpr 2\.00/)
  assert.match(manual, /med 33\.3 · p75 40\.0 ms/)
  assert.match(manual, /tier ×0 @ — · res ×0 @ —/)
})

test('the transition log keeps only the last few', () => {
  let log: HudSnapshot['log'] = []
  for (let i = 0; i < 6; i++) log = noteTransition(log, { atMs: i * 1000, kind: 'tier', from: 'high', to: 'mid', step: `s${i}` })
  assert.equal(HUD_LOG_KEEP, 4)
  assert.equal(log.length, 4)
  assert.equal(log[0].step, 's2')
  assert.equal(log[3].step, 's5')
  assert.deepEqual(noteTransition([], log[0]), [log[0]])
})
