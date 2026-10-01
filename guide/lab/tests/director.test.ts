import { test } from 'node:test'
import assert from 'node:assert/strict'
import { chapterTour, tourChapter, cutStation, layupSpan, playSeconds, type Step, type TourGraph } from '../src/director'
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
  const s = chapterTour(G, 'roncz', 30)
  const want = tourSteps(G, 'roncz', 30).map((x) => x.op)
  assert.deepEqual(want, ['r30.cores', 'r30.shear-web', 'r30.jig', 'r30.bcap', 'r30.bskin', 'r30.tskin'])
  assert.deepEqual(clicks(s, '#chips').map((c) => c.click.match(/data-op="([^"]+)"/)![1]), want)
  const seg = s.filter((x) => 'seg' in x) as { t: number; seg: number }[]
  assert.deepEqual(seg.map((x) => x.seg).filter((n, i, a) => a.indexOf(n) === i), want.map((_, i) => i))
  assert.ok(seg.every((x, i) => i === 0 || x.seg >= seg[i - 1].seg), 'the segment index never goes back')
})

test('step times are non-decreasing once ordered, and every step falls inside the film', () => {
  const s = chapterTour(G, 'roncz', 30)
  assert.equal(s[0].t, 0)
  for (const x of s) assert.ok(Number.isFinite(x.t) && x.t >= 0)
  const ts = s.map((x) => x.t)
  assert.deepEqual(ts, ts.slice().sort((a, b) => a - b), 'authored in time order')
  const end = Math.max(...s.map((x) => x.t + ('dur' in x ? x.dur : 'orbit' in x ? x.orbit.dur : 0)))
  assert.ok(end > 55 && end < 95, `film length ${end}`)
})

test('an op with plies presses Play and waits out the build; an op without plies does not', () => {
  const s = chapterTour(G, 'roncz', 30)
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
  const s = chapterTour(G, 'roncz', 30)
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
  const s = chapterTour(G, 'roncz', 30)
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
  const s = chapterTour({ ...G, layup: null }, 'roncz', 30)
  assert.equal(clicks(s, '#section-on').length, 0)
  assert.ok(s.some((x) => 'orbit' in x))
  const e = chapterTour(G, 'gu', 30)
  assert.equal(clicks(e, '#chips').length, 0)
})

test('it is a pure function of graph and variant', () => {
  assert.deepEqual(chapterTour(G, 'roncz', 30), chapterTour(G, 'roncz', 30))
})

// a GU chapter: two ops with no plies and no lab shots, a stub-only chapter before it
const GU: TourGraph = {
  order: ['c03.skills', 'c10.cores', 'c12.pins', 'c12.align'],
  ops: [op('c03.skills', 3, ['both'], true), op('c10.cores', 10, ['gu']), op('c12.pins', 12, ['gu']), op('c12.align', 12, ['gu'])],
}

test('a chapter without plies dwells on each op and never touches Play or the cut; the cards name the chapter', () => {
  const s = chapterTour(GU, 'gu', 12)
  assert.deepEqual(clicks(s, '#chips').map((c) => c.click), ['#chips button[data-op="c12.pins"]', '#chips button[data-op="c12.align"]'])
  assert.equal(clicks(s, '#play').length + clicks(s, '#section-on').length, 0)
  const cards = s.filter((x) => 'card' in x && x.card) as { card: { title: string; sub?: string } }[]
  assert.deepEqual(cards.map((c) => [c.card.title, c.card.sub]), [['GU canard', 'Chapter 12'], ['Canard, chapter 12', 'Build rehearsal']])
  assert.ok(s.some((x) => 'orbit' in x))
})

test('the ch30 film is the same whichever way it is asked for', () => {
  assert.deepEqual(chapterTour(G, 'roncz', 30).filter((x) => 'card' in x && x.card).map((x) => (x as { card: { sub?: string } }).card.sub), ['Chapter 30', 'Build rehearsal'])
})

test('tourChapter: the selected op\'s chapter, else the first real chapter, also from a stub-only chapter', () => {
  assert.equal(tourChapter(GU, 'gu', 'c12.align'), 12)
  assert.equal(tourChapter(GU, 'gu', null), 10)
  assert.equal(tourChapter(GU, 'gu', 'c03.skills'), 10) // stub only: nothing to build there
  assert.equal(tourChapter(G, 'roncz', 'c10.x'), 30) // an op this variant does not show
  assert.equal(tourChapter(G, 'gu', null), 10)
  assert.equal(tourChapter({ ops: [], order: [] }, 'gu', null), undefined)
})

test('the fuselage tour clicks every chapter 4-6 op in graph order, Plays only ops with plies, and has no section steps', async () => {
  const { fuselageTour } = await import('../src/director')
  const op = (id: string, chapter: number) => ({ id, chapter, title: id, summary: '', variants: ['both'], components: [] as string[] })
  const g = { ops: [op('f04.a', 4), op('f05.a', 5), op('f06.a', 6), op('r30.a', 30)], order: ['f04.a', 'f05.a', 'f06.a', 'r30.a'] }
  const steps = fuselageTour(g, 'roncz', (id) => (id === 'f05.a' ? 2 : 0))
  const clicks = steps.filter((s) => 'click' in s).map((s) => (s as { click: string }).click)
  assert.deepEqual(clicks, ['#chips button[data-op="f04.a"]', '#chips button[data-op="f05.a"]', '#play', '#chips button[data-op="f06.a"]'])
  assert.ok(!steps.some((s) => 'drag' in s))
})

// shaped like chapters 4-6: bond ops listed in the book's order, a stub, a no-ply op
const fop = (id: string, chapter: number, stub = false) => ({ id, chapter, title: id, summary: '', variants: ['both'], stub, components: [] as string[] })
const FG: TourGraph = {
  order: ['f04.a', 'f04.b', 'f05.a', 'f05.s', 'f06.trial-fit', 'f06.bond-front-seat', 'f06.bond-panel', 'f06.bond-f22', 'f06.bond-rear-seat', 'f06.bond-firewall', 'f06.tape'],
  ops: [fop('f04.a', 4), fop('f04.b', 4), fop('f05.a', 5), fop('f05.s', 5, true), fop('f06.trial-fit', 6), fop('f06.bond-front-seat', 6), fop('f06.bond-panel', 6),
    fop('f06.bond-f22', 6), fop('f06.bond-rear-seat', 6), fop('f06.bond-firewall', 6), fop('f06.tape', 6)],
}
const fplies = (id: string) => (['f06.bond-front-seat', 'f06.bond-f22', 'f06.tape', 'f04.a'].includes(id) ? 3 : 0)
const opsOf = (s: Step[]) => clicks(s, '#chips').map((c) => c.click.match(/data-op="([^"]+)"/)![1])

test('the chapter 6 fuselage tour: ch6 ops in graph order, Play only with plies, title card, cut inside the front seat bulkhead, orbit, end card', async () => {
  const { fuselageTour, FUSE_CUT_FS } = await import('../src/director')
  const s = fuselageTour(FG, 'roncz', fplies, [6])
  assert.deepEqual(opsOf(s), ['f06.trial-fit', 'f06.bond-front-seat', 'f06.bond-panel', 'f06.bond-f22', 'f06.bond-rear-seat', 'f06.bond-firewall', 'f06.tape'])
  const plays = clicks(s, '#play')
  assert.equal(plays.length, 3)
  for (const p of plays) { // each Play follows the chip of an op that has plies
    const chip = clicks(s, '#chips').filter((c) => c.t < p.t).pop()!
    assert.ok(fplies(chip.click.match(/data-op="([^"]+)"/)![1]) > 0)
  }
  const cards = s.filter((x) => 'card' in x && x.card) as { t: number; card: { title: string } }[]
  assert.equal(cards[0].card.title, 'Chapter 6 — Fuselage assembly')
  assert.equal(cards.at(-1)!.card.title, 'Fuselage, chapter 6')
  const on = clicks(s, '#section-on')
  assert.equal(on.length, 1, 'the cut is turned on and left on')
  const drags = s.filter((x) => 'drag' in x) as { t: number; to: number }[]
  const last = drags.at(-1)!
  assert.equal(last.to, FUSE_CUT_FS)
  assert.ok(last.to > 63.55 && last.to < 81.75, 'inside the front seat bulkhead FS range')
  assert.ok(on[0].t < last.t)
  const orbit = s.find((x) => 'orbit' in x) as { t: number }
  assert.ok(last.t < orbit.t && orbit.t < cards.at(-1)!.t, 'cut, then the close orbit, then the end card')
  const ts = s.map((x) => x.t)
  assert.deepEqual(ts, ts.slice().sort((a, b) => a - b))
})

test('the ch4-6 fuselage tour visits every op in order, a card at each chapter change, and no section steps', async () => {
  const { fuselageTour } = await import('../src/director')
  const s = fuselageTour(FG, 'roncz', fplies)
  assert.deepEqual(opsOf(s), ['f04.a', 'f04.b', 'f05.a', 'f06.trial-fit', 'f06.bond-front-seat', 'f06.bond-panel', 'f06.bond-f22', 'f06.bond-rear-seat', 'f06.bond-firewall', 'f06.tape'])
  const titles = s.filter((x) => 'card' in x && x.card).map((x) => (x as { card: { title: string } }).card.title)
  assert.deepEqual(titles, ['Fuselage box', 'Chapter 5 — Fuselage sides', 'Chapter 6 — Fuselage assembly', 'Fuselage box'])
  assert.equal(clicks(s, '#section-on').length, 0)
  assert.ok(!s.some((x) => 'drag' in x))
})

test('the fuselage Tour button: the selected fuselage op\'s chapter, else all of chapters 4-9', async () => {
  const { fuselageTourChapters } = await import('../src/director')
  assert.deepEqual(fuselageTourChapters(FG, 'roncz', 'f05.a'), [5])
  assert.deepEqual(fuselageTourChapters(FG, 'roncz', 'f06.bond-panel'), [6])
  assert.deepEqual(fuselageTourChapters(FG, 'roncz', null), [4, 5, 6, 7, 8, 9])
  assert.deepEqual(fuselageTourChapters(FG, 'roncz', 'f05.s'), [4, 5, 6, 7, 8, 9]) // a stub has no stop
})
