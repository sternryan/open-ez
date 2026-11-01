import test from 'node:test'
import assert from 'node:assert/strict'
import { nextTier, nextRes, initialStep, initialRes, holdTier, holdRes, type StepState, type ResState, type Tier } from '../src/quality'

// A 16x play-through on a 120 Hz device, fed to the real step-down and step-up rules.
// A caption step is 2.5 sim seconds, so 156 ms of frames. Most of those frames are 8.3 ms.
// Every tenth early step adds one 120 ms hitch, the way a step change compiles. One late layup
// is the canopy glass: 5.1 s of 50 ms frames, long enough to leave the 1 s settle and miss the
// budget twice. The tail is fast again (the cheap tier would be drawing it). Resolution follows
// main.ts: it moves only on the low tier, and a tier change resets it to 1.

const FAST = 8.3
const STEP_MS = 2500 / 16
const HITCH = 120
const HEAVY_MS = 5100

interface Run { tier: StepState; res: ResState; trace: string[] }

const begin = (): Run => ({ tier: initialStep('high', 3000), res: initialRes(3000), trace: [] })

const feed = (run: Run, ms: number): void => {
  const t0 = run.tier.tier
  const s0 = run.res.scale
  if (run.tier.tier === 'low') run.res = nextRes(run.res, ms)
  const n = nextTier(run.tier, ms)
  run.tier = n
  if (run.tier.tier !== t0) run.res = initialRes(1500)
  if (run.tier.tier !== t0 || Math.abs(run.res.scale - s0) > 1e-9) {
    run.trace.push(`${t0}->${run.tier.tier} res ${s0.toFixed(2)}->${run.res.scale.toFixed(2)}`)
  }
}

const change = (run: Run): void => {
  run.tier = holdTier(run.tier)
  run.res = holdRes(run.res)
}

const short = (run: Run, hitch: boolean): void => {
  change(run)
  let spent = 0
  if (hitch) { feed(run, HITCH); spent += HITCH }
  while (spent < STEP_MS) { feed(run, FAST); spent += FAST }
}

const heavy = (run: Run): void => {
  change(run)
  for (let spent = 0; spent < HEAVY_MS; spent += 50) feed(run, 50)
}

test('a fast device returns to its start tier after a heavy layup, and a steady slow one stays down', () => {
  const run = begin()
  for (let i = 0; i < 40; i++) short(run, i % 10 === 0)
  assert.equal(run.tier.tier, 'high', `early bursts left ${run.tier.tier}`)
  assert.equal(run.res.scale, 1)
  heavy(run)
  console.log('after heavy layup', run.tier.tier, 'res', run.res.scale.toFixed(2), 'trace', run.trace.join(' | '))
  // the layup itself is over budget: high falls to low, and the resolution scale never leaves 1
  assert.equal(run.tier.tier, 'low')
  assert.equal(run.res.scale, 1)
  for (let i = 0; i < 70; i++) short(run, false)
  assert.equal(run.tier.tier, 'low', `climbed to ${run.tier.tier} before a sustained fast window`)
  for (let i = 0; i < 110; i++) short(run, false)
  console.log('end of build', run.tier.tier, 'res', run.res.scale.toFixed(2), 'trace', run.trace.join(' | '))
  assert.equal(run.tier.tier, 'high', `stuck at ${run.tier.tier} with res ${run.res.scale}`)
  assert.equal(run.res.scale, 1)

  // the same rules, fed slow frames for two minutes of 10 s steps: it drops and does not come back
  const slow = begin()
  for (let step = 0; step < 12; step++) {
    change(slow)
    for (let spent = 0; spent < 10_000; spent += 100) feed(slow, 100)
  }
  console.log('steady slow', slow.tier.tier, 'res', slow.res.scale.toFixed(2))
  assert.equal(slow.tier.tier, 'low')
  assert.equal(slow.res.scale, 0.2)
})

test('short fast bursts do not flap the tier back up', () => {
  let tier = initialStep('high')
  const seen: Tier[] = ['high']
  const mark = () => { if (seen[seen.length - 1] !== tier.tier) seen.push(tier.tier) }
  for (let spent = 0; spent < 8000; spent += 50) { tier = nextTier(tier, 50); mark() }
  assert.equal(tier.tier, 'low')
  for (let cycle = 0; cycle < 30; cycle++) {
    tier = holdTier(tier)
    for (let spent = 0; spent < 2000; spent += FAST) tier = nextTier(tier, FAST)
    for (let spent = 0; spent < 2000; spent += 50) tier = nextTier(tier, 50)
    mark()
  }
  assert.equal(tier.tier, 'low')
  assert.deepEqual(seen, ['high', 'mid', 'low'])
})
