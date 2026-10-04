// Chapter 18 in the lab: where the canopy is (bench upright, in place, upside down on the bench), the lift-off and the opening in sim time, the open pose
// against core.canopy_book.open_pose (tests/fixtures/kernels.json), the readout texts that carry the latch conflict and the unnamed front-cut datum, and the
// canopy reference row.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  canopyPlace, liftProgress, liftDuration, LIFT, openProgress, openDuration, OPEN, clampOpenDeg, openPoint, openText, openShort, latchText, frontCutText, padsText, checksText,
  canopyKin, canopyRow, PAD_ROLES, TRIM_OP, BLOCKS_OP, CUT_OP, BENCH_LAST_OP, HINGE_OP, LATCH_OP, CHECK_OP, CANOPY_REF_FROM, type CanopyData,
} from '../src/logic/canopy'
import { M25_CHAPTERS, FUSE_PREFIXES } from '../src/logic/m25'
import { FUSE_CHAPTERS, FUSE_TOUR_CHAPTERS, M25_TOUR_CHAPTERS, cutRangeFor } from '../src/logic/fuselage'
import { KIN_HOLD } from '../src/logic/kin'
import { fuseView, M26_VIEWS } from '../src/fuseShots'

const fx = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/kernels.json', import.meta.url)), 'utf8'))
const c: CanopyData = fx.extras.canopy
const near = (a: number, b: number, tol = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`)
const order = ['f17.fixed-trim-tab', TRIM_OP, BLOCKS_OP, CHECK_OP, 'f18.foam-core', 'f18.carve-outside', 'f18.glass-outside', CUT_OP, 'f18.carve-inside', 'f18.pads-inside-glass', 'f18.rear-cover-inside', BENCH_LAST_OP, HINGE_OP, 'f18.door', LATCH_OP, 'f18.front-cover', CANOPY_REF_FROM]

test('the open pose is core.canopy_book.open_pose (a turn of -deg about the right hinge line)', () => {
  assert.ok(fx.canopy.open.length >= 16)
  for (const r of fx.canopy.open) {
    const o = openPoint(r.pt, r.deg, c.hinge)
    for (let i = 0; i < 3; i++) near(o[i], r.out[i], 1e-8, JSON.stringify(r))
  }
  // it opens to the right (B.L. grows) and up, 105 deg being 15 past vertical
  const top = openPoint([80, 0, 12], 90, c.hinge)
  assert.ok(top[1] > c.hinge.y + 5, 'at vertical the canopy stands beside the hinge, outboard of nothing')
  assert.equal(c.hinge.max_open_deg, 105); assert.equal(c.hinge.past_vertical_deg, 15)
  assert.deepEqual(openPoint([80, 3, 9], 0, c.hinge), [80, 3, 9])
})

test('the canopy is on the bench upright while trimmed, in place on its blocks, upside down on the bench from the cut to the last op that works on its inside, and in place after', () => {
  for (const comp of c.lift) {
    assert.equal(canopyPlace(comp, c.lift, TRIM_OP, order), 'bench-up')
    assert.equal(canopyPlace(comp, c.lift, BLOCKS_OP, order), 'airplane')
    assert.equal(canopyPlace(comp, c.lift, 'f18.glass-outside', order), 'airplane')
    assert.equal(canopyPlace(comp, c.lift, CUT_OP, order), 'bench-down')
    assert.equal(canopyPlace(comp, c.lift, BENCH_LAST_OP, order), 'bench-down')
    assert.equal(canopyPlace(comp, c.lift, HINGE_OP, order), 'airplane')
    assert.equal(canopyPlace(comp, c.lift, null, order), 'airplane')
    assert.equal(canopyPlace(comp, c.lift, 'f17.fixed-trim-tab', order), 'airplane')
  }
  // the covers, the door, the hinges and the latches never leave the airplane
  for (const comp of ['fuselage.front_cover', 'fuselage.rear_cover', 'fuselage.door', 'canopy.hinges', 'canopy.latches', 'canopy.safety_catch']) assert.equal(canopyPlace(comp, c.lift, CUT_OP, order), 'airplane')
  assert.ok(c.lift.includes('canopy.plexi') && c.lift.includes('canopy.frame') && c.lift.includes('canopy.pads') && !c.lift.includes('canopy.blocks'))
})

test('the lift-off and the opening wait for the camera, run 0 to 1 and are monotone; the tour holds on both ops', () => {
  assert.equal(liftProgress(0), 0); assert.equal(liftProgress(LIFT.wait), 0); assert.equal(liftProgress(LIFT.wait + LIFT.seconds), 1)
  assert.equal(openProgress(0), 0); assert.equal(openProgress(OPEN.wait), 0); assert.equal(openProgress(OPEN.wait + OPEN.seconds), 1)
  let a = -1, b = -1
  for (let t = 0; t < 10; t += 0.1) { const l = liftProgress(t), o = openProgress(t); assert.ok(l >= a && o >= b && l <= 1 && o <= 1); a = l; b = o }
  assert.ok(liftDuration() > LIFT.wait + LIFT.seconds && openDuration() > OPEN.wait + OPEN.seconds)
  assert.equal(KIN_HOLD[CUT_OP], liftDuration()); assert.equal(KIN_HOLD[HINGE_OP], openDuration())
  assert.equal(clampOpenDeg(200, 105), 105); assert.equal(clampOpenDeg(-4, 105), 0)
})

test('the opening reads as an angle, and past vertical says so and says it is representational', () => {
  assert.equal(openText(0, c.hinge), 'Closed')
  assert.equal(openText(45, c.hinge), '45 deg open')
  assert.equal(openText(105, c.hinge), '105 deg open: 15 deg past vertical, representational')
  assert.equal(openText(97, c.hinge), '97 deg open: 7 deg past vertical, representational')
  assert.equal(openShort(0), 'Closed'); assert.equal(openShort(104.6), '105 deg')
})

test('the latch-pad conflict and the front cut\'s unnamed datum are always worded as such, never as a bare number', () => {
  const l = latchText(c)
  assert.equal(l.value, 'Pad centres FS 104.75, 74.75, 44.75 (derived)')
  assert.equal(l.sub, 'The printed labels read 104, 74, 44: 0.75 in apart, unresolved')
  assert.equal(frontCutText(c), 'Front cut about FS 41.65, datum not named (representational)')
  assert.equal(canopyKin(LATCH_OP, c, 0)!.value, l.value)
  assert.ok(canopyKin(LATCH_OP, c, 0)!.sub.includes('unresolved'))
  for (const op of [CUT_OP, 'f18.front-cover']) assert.ok(canopyKin(op, c, 0)!.value.includes('datum not named'), op)
  assert.equal(c.latch.gap_in, 0.75); assert.deepEqual(c.front_cut, { fs: 41.65, datum_named: false })
  assert.equal(canopyKin(HINGE_OP, c, 105)!.value, '105 deg open: 15 deg past vertical, representational')
  assert.equal(canopyKin('f18.door', c, 0), null)
})

test('the pads read by role in the readout and the A and B checks are the book heights above WL 23', () => {
  const p = padsText(c)
  assert.ok(p.value.includes('20, 25.5, 48, 53.5') && p.sub.includes('11, 41, 59 (safety catch), 71'), JSON.stringify(p))
  assert.ok(p.sub.includes('Hinge pads blue') && p.sub.includes('latch pads green') && p.sub.includes('catch pad red'))
  assert.deepEqual(Object.keys(PAD_ROLES).sort(), ['catch', 'hinge', 'latch'])
  assert.equal(new Set(Object.values(PAD_ROLES).map((r) => r.color)).size, 3, 'three colours')
  assert.equal(checksText(c), 'A at least 13.5 in, B 12.3 in, above WL 23')
  assert.equal(canopyKin(CHECK_OP, c, 0)!.value, checksText(c))
  assert.deepEqual(c.checks.map((k) => [k.id, k.height_in, k.wl0, k.wl1]), [['A', 13.5, 23, 36.5], ['B', 12.3, 23, 35.3]])
})

test('the canopy reference row: from the last op of the chapter on, worded as a reference not in the CG', () => {
  const led = { cg: {}, cg_lower_bound: {}, prototype_weights: { rows: { canopy: { weight_lb: 16, cite: 'cp-text:p26', note: 'builder weight, Melvill N26MS' } } } } as never
  assert.equal(canopyRow(led, 'f18.front-cover', order), null)
  assert.equal(canopyRow(led, CANOPY_REF_FROM, order)?.value, 'Canopy (CP26 builder weight, N26MS): 16.0 lb, reference, not in CG')
  assert.equal(canopyRow(led, 'f17.fixed-trim-tab', order), null)
  assert.equal(canopyRow(led, null, order), null)
  assert.equal(canopyRow(null, CANOPY_REF_FROM, order), null)
})

test('chapter 18 is the fuselage subject with its own tour, and its parts show on its ops only', () => {
  assert.ok(FUSE_CHAPTERS.has(18) && M25_CHAPTERS.has(18))
  assert.ok(FUSE_PREFIXES.includes('canopy.'))
  assert.ok(!FUSE_TOUR_CHAPTERS.includes(18) && !M25_TOUR_CHAPTERS.includes(18))
  assert.ok(cutRangeFor(18).max >= 129.9)
  // every op of the chapter has a shot of its own (not the default box view)
  const ops = ['f18.trim-plexi', 'f18.locate-blocks', 'f18.check-ab', 'f18.foam-core', 'f18.carve-outside', 'f18.glass-outside', 'f18.cut-remove', 'f18.carve-inside', 'f18.pads-inside-glass', 'f18.rear-cover-inside', 'f18.vent-brace', 'f18.hinges', 'f18.door', 'f18.latches', 'f18.front-cover', 'f18.safety-catch']
  assert.deepEqual(Object.keys(M26_VIEWS).sort(), ops.slice().sort())
  for (const id of ops) assert.equal(fuseView(id), M26_VIEWS[id], id)
})

import { fuselageTour, fuselageTourChapters, type Step, type TourGraph } from '../src/director'
const fop = (id: string) => ({ id, chapter: 18, title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })
const TG: TourGraph = { order: order.filter((o) => o.startsWith('f18.')), ops: order.filter((o) => o.startsWith('f18.')).map(fop) }
const clicksOf = (s: Step[], pre: string) => s.filter((x) => 'click' in x && x.click.startsWith(pre)) as { t: number; click: string }[]

test('the chapter 18 tour visits every op in order, plays only the five-ply op, holds on the lift-off and the opening, and closes on the last op', () => {
  assert.deepEqual(fuselageTourChapters(TG, 'roncz', HINGE_OP), [18])
  const s = fuselageTour(TG, 'roncz', (id) => (id === 'f18.glass-outside' ? 5 : 0), [18])
  const ops = clicksOf(s, '#chips').map((x) => x.click.match(/data-op="([^"]+)"/)![1])
  assert.deepEqual(ops, TG.order)
  assert.equal(clicksOf(s, '#play').length, 1)
  assert.equal((s.find((x) => 'card' in x && x.card) as { card: { title: string } }).card.title, 'Chapter 18 — Canopy')
  const fin = s.find((x) => 'act' in x && x.act === 'finish') as { op?: string }
  assert.equal(fin.op, CANOPY_REF_FROM)
  const chips = clicksOf(s, '#chips')
  for (const op of [CUT_OP, HINGE_OP]) {
    const i = chips.findIndex((x) => x.click.includes(`"${op}"`))
    assert.ok(chips[i + 1].t - chips[i].t >= KIN_HOLD[op], `${op}: the motion finishes before the next op`)
  }
})
