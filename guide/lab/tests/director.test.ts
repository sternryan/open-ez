import { test } from 'node:test'
import assert from 'node:assert/strict'
import { canardTour, cutStation, layupSpan, playSeconds, type Step, type TourGraph } from '../src/director'
import { tourSteps } from '../src/logic/tour'

const op = (id: string, chapter: number, variants: string[], stub = false) => ({ id, chapter, title: id, summary: '', variants, stub, components: [] as string[] })
// shaped like the real chapter 30: ops with plies, ops without, a stub, another chapter
const G: TourGraph = {
  order: ['c10.x', 'r30.cores', 'r30.shear-web', 'r30.jig', 'r30.bcap', 'r30.bskin', 'r30.elev', 'r30.tskin'],
  ops: [op('c10.x', 10, ['gu']), op('r30.cores', 30, ['roncz']), op('r30.shear-web', 30, ['roncz']), op('r30.jig', 30, ['roncz']), op('r30.bcap', 30, ['roncz']),
    op('r30.bskin', 30, ['roncz']), op('r30.elev', 30, ['roncz'], true), op('r30.tskin', 30, ['roncz'])],
  plies: {
    web: [1, 2, 3, 4, 5, 6].map(() => ({ op: 'r30.shear-web' })),
    cap: [{ op: 'r30.bcap' }],
    skin: [1, 2, 3].map(() => ({ op: 'r30.bskin' })).concat([1, 2, 3, 4].map(() => ({ op: 'r30.tskin' }))),
  },
  layup: {
    semi_span: 70.8,
    nodes: {
      w1: { op: 'r30.shear-web', bl_max: 54 }, w2: { op: 'r30.shear-web', bl_max: 30 }, w3: { op: 'r30.shear-web', bl_max: 6 },
      c1: { op: 'r30.bcap', bl_max: 54 },
      s1: { op: 'r30.bskin', bl_max: null }, s2: { op: 'r30.tskin', bl_max: null },
    },
  },
}
const clicks = (s: Step[], pre: string) => s.filter((x) => 'click' in x && x.click.startsWith(pre)) as { t: number; click: string }[]

test('one segment per non-stub op of the chapter, in order', () => {
  const s = canardTour(G, 'roncz')
  const want = tourSteps(G, 'roncz', 30).map((x) => x.op)
  assert.deepEqual(want, ['r30.cores', 'r30.shear-web', 'r30.jig', 'r30.bcap', 'r30.bskin', 'r30.tskin'])
  assert.deepEqual(clicks(s, '#chips').map((c) => c.click.match(/data-op="([^"]+)"/)![1]), want)
  const seg = s.filter((x) => 'seg' in x) as { t: number; seg: number }[]
  assert.deepEqual(seg.map((x) => x.seg).filter((n, i, a) => a.indexOf(n) === i), want.map((_, i) => i))
  assert.ok(seg.every((x, i) => i === 0 || x.seg >= seg[i - 1].seg), 'the segment index never goes back')
})

test('step times are non-decreasing once ordered, and every step falls inside the film', () => {
  const s = canardTour(G, 'roncz')
  assert.equal(s[0].t, 0)
  for (const x of s) assert.ok(Number.isFinite(x.t) && x.t >= 0)
  const ts = s.map((x) => x.t)
  assert.deepEqual(ts, ts.slice().sort((a, b) => a - b), 'authored in time order')
  const end = Math.max(...s.map((x) => x.t + ('dur' in x ? x.dur : 'orbit' in x ? x.orbit.dur : 0)))
  assert.ok(end > 55 && end < 95, `film length ${end}`)
})

test('an op with plies presses Play and waits out the build; an op without plies does not', () => {
  const s = canardTour(G, 'roncz')
  const plays = clicks(s, '#play')
  assert.equal(plays.length, 4) // web, cap, both skins
  const web = clicks(s, '#chips').find((c) => c.click.includes('r30.shear-web'))!
  const p = plays.find((c) => c.t > web.t)!
  const cutOn = clicks(s, '#section-on').find((c) => c.t > p.t)!
  assert.ok(cutOn.t - p.t >= playSeconds(6) - 0.01, 'the cut waits for the last ply to cure')
  const jig = clicks(s, '#chips').find((c) => c.click.includes('r30.jig'))!
  assert.ok(!plays.some((c) => c.t > jig.t && c.t < jig.t + 2.5))
})

test('the cut opens and closes once per op with plies, at a station inside that op', () => {
  const s = canardTour(G, 'roncz')
  const toggles = clicks(s, '#section-on')
  const drags = s.filter((x) => 'drag' in x) as { t: number; from: number; to: number }[]
  // 4 ops with plies: on, off each; then on for the finale
  assert.equal(toggles.length, 4 * 2 + 1)
  const ops = ['r30.shear-web', 'r30.bcap', 'r30.bskin', 'r30.tskin']
  ops.forEach((id, i) => {
    const d = drags[i]
    assert.equal(d.to, cutStation(G, id))
    assert.ok(d.to >= 0 && d.to <= layupSpan(G, id), `${id} cut at ${d.to}`)
    if (i) assert.equal(d.from, drags[i - 1].to, 'the drag starts where the last one ended')
  })
  assert.equal(cutStation(G, 'r30.shear-web'), 10) // the web's layup reaches 54 in, so 10
  assert.equal(cutStation(G, 'r30.bcap'), 20)
})

test('a station never leaves a short layup', () => {
  const g: TourGraph = { ...G, layup: { semi_span: 70, nodes: { a: { op: 'r30.shear-web', bl_max: 6 } } } }
  assert.equal(cutStation(g, 'r30.shear-web'), 6)
  assert.equal(cutStation(g, 'r30.absent'), 0)
})

test('it starts from home, ends on a slow orbit with the cut on, then the closing card', () => {
  const s = canardTour(G, 'roncz')
  assert.deepEqual(s.find((x) => 'act' in x), { t: 0, act: 'reset' })
  const orbit = s.find((x) => 'orbit' in x) as { t: number; orbit: { dur: number; deg: number } }
  assert.ok(orbit.orbit.dur >= 8 && orbit.orbit.deg <= 120)
  const lastOn = clicks(s, '#section-on').pop()!
  assert.ok(lastOn.t < orbit.t, 'the cut is on before the orbit begins')
  const cards = s.filter((x) => 'card' in x) as { t: number; card: { title: string } | null }[]
  assert.equal(cards.at(-1)!.card!.title, 'Canard, chapter 30')
  assert.ok(cards.at(-1)!.t > orbit.t)
})

test('a graph without a layup still tours (no cut steps); a variant with no ops gives just the frame', () => {
  const s = canardTour({ ...G, layup: null }, 'roncz')
  assert.equal(clicks(s, '#section-on').length, 0)
  assert.ok(s.some((x) => 'orbit' in x))
  const e = canardTour(G, 'gu')
  assert.equal(clicks(e, '#chips').length, 0)
})

test('it is a pure function of graph and variant', () => {
  assert.deepEqual(canardTour(G, 'roncz'), canardTour(G, 'roncz'))
})
