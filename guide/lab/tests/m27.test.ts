// Chapters 19 and 20 in the lab: where the wing is for each op (jigs, table, airplane), the aileron and rudder kernels against core.wing_book and
// core.winglet_book (tests/fixtures/kernels.json), the swing times, the readout texts that carry the three conflicts, the cp-corrected shear web, the A, B and C
// jig, the ply lay-down schedule, the reference weight rows, the chapter registration and the two tours.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  wingPlace, onWingBench, sideShown, workshopShown, rotateAbout, aileronPoint, rudderPoint, aileronProgress, aileronDuration, AILERON_SWING, rudderProgress, rudderDuration, RUDDER_SWING,
  clampAileronDeg, clampRudderDeg, aileronText, aileronShort, rudderText, rudderShort, leText, aileronEndText, boltText, webText, abcText, abcLabel, plySchedule, plyText, wingKin, wingRow,
  TABLE_OPS, WINGLET_BENCH_OPS, WING_GHOST_OPS, WING_XRAY_OPS, JIG_OP, CUT_CORES_OP, SHEAR_WEB_OP, AILERON_CUT_OP, AILERON_OP, CONTROLS_OP, ATTACH_OP, WINGLET_JIG_OP, LOWER_FIN_OP, RUDDER_OP, type WingData, type WingPlyRow,
} from '../src/logic/wing'
import { M25_CHAPTERS, FUSE_PREFIXES } from '../src/logic/m25'
import { FUSE_CHAPTERS, FUSE_TOUR_CHAPTERS, M25_TOUR_CHAPTERS, cutRangeFor } from '../src/logic/fuselage'
import { KIN_HOLD } from '../src/logic/kin'
import { fuseView, M27_VIEWS } from '../src/fuseShots'
import { fuselageTour, fuselageTourChapters, chapterCard, type Step, type TourGraph } from '../src/director'

const fx = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/kernels.json', import.meta.url)), 'utf8'))
const w: WingData & { nodes: Record<string, WingPlyRow> } = fx.extras.wing
const near = (a: number, b: number, tol = 1e-8, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`)

const CH19 = ['f19.jig', 'f19.cut-cores', 'f19.core-cutouts', 'f19.mount-cores', 'f19.hardpoints', 'f19.shear-web', 'f19.pads-plates', 'f19.le-cores', 'f19.bottom-cap', 'f19.bottom-skin', 'f19.top-cap', 'f19.rudder-conduit',
  'f19.top-skin', 'f19.ribs', 'f19.aileron-cut', 'f19.aileron-build', 'f19.controls', 'f19.attach']
const CH20 = ['f20.cut-cores', 'f20.skins', 'f20.trim', 'f20.jig', 'f20.inside-layups', 'f20.outside-layups', 'f20.lower-fin', 'f20.rudder-cut', 'f20.rudder-hang']
const order = ['f17.fixed-trim-tab', 'f18.safety-catch', ...CH19, 'f16.aileron-linkage', ...CH20, 'f16.rudder-cable-rig']

test('the aileron and rudder kernels are the python poses (a turn of -deg and of +deg about the hinge axes)', () => {
  assert.ok(fx.wing.aileron.length >= 15 && fx.wing.rudder.length >= 20)
  for (const r of fx.wing.aileron) { const o = aileronPoint(r.pt, r.deg, w); for (let i = 0; i < 3; i++) near(o[i], r.out[i], 1e-6, JSON.stringify(r)) }
  for (const r of fx.wing.rudder) { const o = rudderPoint(r.pt, r.deg, w); for (let i = 0; i < 3; i++) near(o[i], r.out[i], 1e-6, JSON.stringify(r)) }
  // a turn about an axis keeps points on the axis where they are, and a quarter turn takes +x to the right-hand side
  const a = w.aileron.axis[0], b = w.aileron.axis[1]
  const o = rotateAbout(a, a, b, 33); for (let i = 0; i < 3; i++) near(o[i], a[i], 1e-9)
  assert.deepEqual(rotateAbout([1, 0, 0], [0, 0, 0], [0, 0, 1], 90).map((x) => Math.round(x * 1e9) / 1e9), [0, 1, 0])
})

test('the aileron goes up (its trailing edge rises) and the rudder positive goes outboard', () => {
  const te = [168.0, 90.0, 1.6] // behind the aileron's hinge line (FS about 157 at B.L. 90)
  const up = aileronPoint(te, 20, w)
  assert.ok(up[2] > te[2] + 3, `the trailing edge rises: ${up[2]} from ${te[2]}`)
  const tailP = [184.0, 158.0, 20.0] // behind the rudder hinge (FS 176.8)
  const out = rudderPoint(tailP, 30, w), back = rudderPoint(tailP, -30, w)
  assert.ok(out[1] > tailP[1] && back[1] < tailP[1], `positive is outboard (+y): ${out[1]} ${back[1]}`)
  assert.equal(w.rudder.max_deg, 30); assert.equal(w.aileron.max_up_deg, 20)
})

test('the wing is on its bench from the jigs to the controls and on the airplane from the attach op: stood in the jigs, flat on the table for the cores and the bottom ops', () => {
  assert.deepEqual(TABLE_OPS, ['f19.cut-cores', 'f19.core-cutouts', 'f19.bottom-cap', 'f19.bottom-skin'])
  const want: Record<string, string> = {}
  for (const o of CH19.slice(0, -1)) want[o] = TABLE_OPS.includes(o) ? 'table' : 'jig'
  for (const [o, p] of Object.entries(want)) assert.equal(wingPlace(o, order), p, o)
  assert.deepEqual(WINGLET_BENCH_OPS, ['f20.cut-cores', 'f20.skins', 'f20.trim'])
  for (const o of WINGLET_BENCH_OPS) { assert.equal(wingPlace(o, order), 'winglet', o); assert.ok(onWingBench(o, order), 'the airplane is not drawn on the winglet bench ops') }
  for (const o of ['f20.jig', 'f20.inside-layups', 'f20.rudder-hang']) assert.equal(wingPlace(o, order), 'airplane', o)
  assert.ok(!WING_GHOST_OPS.has(ATTACH_OP) && WING_XRAY_OPS.has(ATTACH_OP) && WING_XRAY_OPS.has('f19.hardpoints') && !WING_GHOST_OPS.has('f19.hardpoints'))
  for (const o of [ATTACH_OP, 'f20.jig', 'f20.inside-layups', 'f20.outside-layups', 'f20.lower-fin', 'f20.rudder-cut', 'f20.rudder-hang', 'f16.aileron-linkage', 'f16.rudder-cable-rig', 'f18.safety-catch', null]) assert.equal(wingPlace(o, order), 'airplane', String(o))
  assert.ok(onWingBench(JIG_OP, order) && onWingBench(CONTROLS_OP, order) && !onWingBench(ATTACH_OP, order) && !onWingBench(null, order))
})

test('the left wing waits for the attach op; the jigs stand from their op to the attach and the winglet jig lines hold from f20.jig to the corner layups', () => {
  for (const o of CH19.slice(0, -1)) assert.ok(!sideShown('left', o, order) && sideShown('right', o, order), o)
  for (const o of [ATTACH_OP, ...CH20, null]) assert.ok(sideShown('left', o, order), String(o))
  for (const o of CH19.slice(0, -1)) assert.ok(workshopShown('wing.jigs', o, order), o)
  for (const o of [ATTACH_OP, ...CH20, 'f17.fixed-trim-tab', null]) assert.ok(!workshopShown('wing.jigs', o, order), String(o))
  for (const o of ['f20.jig', 'f20.inside-layups', 'f20.outside-layups']) assert.ok(workshopShown('winglet.jig', o, order), o)
  for (const o of ['f20.trim', 'f20.lower-fin', 'f20.rudder-hang', ATTACH_OP, null]) assert.ok(!workshopShown('winglet.jig', o, order), String(o))
  assert.ok(workshopShown('wing.aileron', 'f19.ribs', order))
})

test('the swings wait for the camera, run 0 to 1 and are monotone; the tour holds on both ops', () => {
  assert.equal(aileronProgress(0), 0); assert.equal(aileronProgress(AILERON_SWING.wait), 0); assert.equal(aileronProgress(AILERON_SWING.wait + AILERON_SWING.seconds), 1)
  assert.equal(rudderProgress(0), 0); assert.equal(rudderProgress(RUDDER_SWING.wait), 0); assert.equal(rudderProgress(RUDDER_SWING.wait + RUDDER_SWING.seconds), 1)
  let a = -1, b = -1
  for (let t = 0; t < 10; t += 0.1) { const x = aileronProgress(t), y = rudderProgress(t); assert.ok(x >= a && y >= b && x <= 1 && y <= 1); a = x; b = y }
  assert.ok(aileronDuration() > AILERON_SWING.wait + AILERON_SWING.seconds && rudderDuration() > RUDDER_SWING.wait + RUDDER_SWING.seconds)
  assert.equal(KIN_HOLD[AILERON_OP], aileronDuration()); assert.equal(KIN_HOLD[RUDDER_OP], rudderDuration())
  assert.equal(clampAileronDeg(40, 20), 20); assert.equal(clampAileronDeg(-3, 20), 0)
  assert.equal(clampRudderDeg(45, 30), 30); assert.equal(clampRudderDeg(-45, 30), -30)
})

test('the aileron reads as degrees up to its stop and the rudder as degrees with the way its trailing edge goes', () => {
  assert.equal(aileronText(0, 20), 'Neutral'); assert.equal(aileronText(12, 20), '12 deg up'); assert.equal(aileronText(20, 20), '20 deg up: at the stop')
  assert.equal(aileronShort(0), 'Neutral'); assert.equal(aileronShort(19.6), '20 deg up')
  assert.equal(rudderText(0, 30), 'Neutral'); assert.equal(rudderText(12, 30), '12 deg, trailing edge outboard'); assert.equal(rudderText(-30, 30), '30 deg, trailing edge inboard: at the limit')
  assert.equal(rudderShort(0), 'Neutral'); assert.equal(rudderShort(30), '30 deg out'); assert.equal(rudderShort(-7), '7 deg in')
})

test('the three conflicts are always worded as pairs, never as one bare number, on their own ops', () => {
  assert.equal(leText(w).value, 'Leading edge at BL 106.25: printed FS 134.95, FS 134.45 from the chord and the trailing edge')
  assert.ok(leText(w).sub.includes('unresolved'))
  assert.equal(aileronEndText(w).value, 'Aileron inboard end: BL 54.3 on p171, BL 55.5 cut at the foam joint')
  assert.ok(aileronEndText(w).sub.includes('unresolved'))
  assert.equal(boltText(w).value, 'Spar bolt spacing: 28.85 in on the drawing, 28.83 in in the text')
  assert.ok(boltText(w).sub.includes('unresolved'))
  assert.equal(wingKin(CUT_CORES_OP, w, 0, 0)!.value, leText(w).value)
  assert.equal(wingKin(AILERON_CUT_OP, w, 0, 0)!.value, aileronEndText(w).value)
  assert.equal(wingKin(ATTACH_OP, w, 0, 0)!.value, boltText(w).value)
  assert.deepEqual(w.conflicts.le_bl_106_25.printed_fs, 134.95); assert.deepEqual(w.conflicts.aileron_inboard, { p124_bl: 55.5, p171_bl: 54.3 })
  assert.equal(wingKin('f19.ribs', w, 0, 0), null)
})

test('the shear web outboard zone is 2 plies, cp-corrected, and says the plans print 3', () => {
  assert.equal(webText(w).value, 'BL 23 to 70: 6 plies, BL 70 to 120: 4 plies, BL 120 to 157: 2 plies (CP26 LPC 31; plans print 3)')
  assert.equal(wingKin(SHEAR_WEB_OP, w, 0, 0)!.value, webText(w).value)
  assert.deepEqual(w.shear_web.zones, [[23, 70, 6], [70, 120, 4], [120, 157, 2]])
})

test('the winglet jig: A, B and C from the reference point, the closure and the derived lean are all said', () => {
  const t = abcText(w)
  assert.equal(t.value, 'A 102.15, B 108.35, C 118.35 in from the reference point (BL 55.5, FS 149.6)')
  assert.ok(t.sub.includes('A -0.07, B -0.25, C 0') && t.sub.includes('lean (3.58 in) is derived, low confidence'), t.sub)
  assert.equal(abcLabel(w, 'a'), 'A 102.15 in'); assert.equal(abcLabel(w, 'c'), 'C 118.35 in')
  assert.deepEqual(w.winglet.wprp, [149.6, 55.5])
  for (const k of ['wprp', 'a', 'b', 'c'] as const) assert.equal(w.winglet.points[k].length, 3, k)
  assert.equal(wingKin(WINGLET_JIG_OP, w, 0, 0)!.value, t.value)
})

test('the aileron and rudder readouts follow the angles, the rudder with its sign', () => {
  assert.equal(wingKin(AILERON_OP, w, 20, 0)!.value, '20 deg up: at the stop')
  assert.ok(wingKin(AILERON_OP, w, 0, 0)!.sub.includes('20 deg stop') && wingKin(AILERON_OP, w, 0, 0)!.sub.includes('representational'))
  assert.equal(wingKin(RUDDER_OP, w, 0, 30)!.value, '30 deg, trailing edge outboard: at the limit')
  assert.ok(wingKin(RUDDER_OP, w, 0, 0)!.sub.includes('30 deg either way'))
})

test('the ply lay-down: the shear web 6, the bottom cap 5, the top cap 7, the skins 3 and 3, the winglet skins 3 and 2, the corner layup 7', () => {
  const s = plySchedule(w.nodes)
  const by = (op: string, part: string) => s.find((x) => x.op === op && x.part.includes(part))!
  assert.equal(by('f19.shear-web', 'shear_web').plies, 6)
  assert.equal(by('f19.bottom-cap', 'cap_bottom').plies, 5)
  assert.equal(by('f19.top-cap', 'cap_top').plies, 7)
  assert.equal(by('f19.bottom-skin', 'skin_bottom').plies, 3); assert.equal(by('f19.top-skin', 'skin_top').plies, 3)
  assert.equal(by('f20.skins', 'skin_out').plies, 3); assert.equal(by('f20.skins', 'skin_in').plies, 2)
  assert.equal(by('f20.outside-layups', 'layup_3').plies, 7)
  assert.equal(plyText(by('f19.shear-web', 'shear_web')), '6 plies: 6 UND')
  assert.equal(plyText(by('f19.bottom-skin', 'skin_bottom')), '3 plies: 2 UND + 1 BID')
  assert.ok(s.every((x) => ['f19', 'f20'].includes(x.op.slice(0, 3))))
})

test('the wing reference rows: the aileron from its op, the wing at the end of chapter 19, the lower winglet, the whole wing at the end of chapter 20; never in the CG', () => {
  const rows = { aileron: { weight_lb: 5.125, note: 'a' }, wing_ch19: { weight_lb: 51.5, note: 'b' }, wing_complete: { weight_lb: 64, note: 'c' }, upper_winglet: { weight_lb: 6, note: 'd' }, lower_winglet: { weight_lb: 1.19, note: 'e' } }
  const led = { cg: {}, cg_lower_bound: {}, prototype_weights: { rows } } as never
  assert.equal(wingRow(led, 'f19.controls', order)!.value, 'Aileron (CP26 builder weight, N26MS): 5.1 lb, reference, not in CG')
  assert.equal(wingRow(led, 'f19.aileron-cut', order), null)
  assert.equal(wingRow(led, ATTACH_OP, order)!.value, 'Wing to the end of chapter 19 (CP26 builder weight, N26MS): 51.5 lb each; aileron 5.1 lb, reference, not in CG')
  assert.equal(wingRow(led, 'f20.trim', order), null)
  assert.equal(wingRow(led, LOWER_FIN_OP, order)!.value, 'Lower winglet (CP26 builder weight, N26MS): 1.2 lb, reference, not in CG')
  assert.equal(wingRow(led, RUDDER_OP, order)!.value, 'Wing with winglets and rudder (CP26 builder weight, N26MS): 64.0 lb each, reference, not in CG')
  assert.ok(wingRow(led, RUDDER_OP, order)!.sub.includes('upper winglet 6.0 lb') && wingRow(led, RUDDER_OP, order)!.sub.includes('lower winglet 1.2 lb'))
  assert.equal(wingRow(led, 'f18.safety-catch', order), null); assert.equal(wingRow(led, null, order), null); assert.equal(wingRow(null, ATTACH_OP, order), null)
})

test('chapters 19 and 20 are the fuselage subject with a tour each, and every op of both has a shot of its own', () => {
  assert.ok(FUSE_CHAPTERS.has(19) && FUSE_CHAPTERS.has(20) && M25_CHAPTERS.has(19) && M25_CHAPTERS.has(20))
  assert.ok(FUSE_PREFIXES.includes('wing.') && FUSE_PREFIXES.includes('winglet.'))
  assert.ok(!FUSE_TOUR_CHAPTERS.includes(19) && !M25_TOUR_CHAPTERS.includes(19) && !M25_TOUR_CHAPTERS.includes(20))
  assert.ok(cutRangeFor(19).max >= 129.9 && cutRangeFor(20).max >= 129.9)
  assert.deepEqual(Object.keys(M27_VIEWS).sort(), [...CH19, ...CH20].sort())
  for (const id of [...CH19, ...CH20]) assert.equal(fuseView(id), M27_VIEWS[id], id)
})

const fop = (id: string, chapter: number) => ({ id, chapter, title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })
const clicksOf = (s: Step[], pre: string) => s.filter((x) => 'click' in x && x.click.startsWith(pre)) as { t: number; click: string }[]
for (const [ch, ops, last, holds] of [[19, CH19, ATTACH_OP, [AILERON_OP]], [20, CH20, RUDDER_OP, [RUDDER_OP]]] as const) {
  test(`the chapter ${ch} tour visits every op in order, plays only the ply ops, holds on the swing and closes on the last op`, () => {
    const TG: TourGraph = { order: ops.slice(), ops: ops.map((o) => fop(o, ch)) }
    assert.deepEqual(fuselageTourChapters(TG, 'roncz', ops[2]), [ch])
    const plyOps = new Map([['f19.shear-web', 6], ['f19.bottom-cap', 5], ['f19.top-cap', 7], ['f19.bottom-skin', 3], ['f19.top-skin', 3], ['f20.skins', 5], ['f20.outside-layups', 7]])
    const s = fuselageTour(TG, 'roncz', (id) => plyOps.get(id) ?? 0, [ch])
    const chips = clicksOf(s, '#chips')
    assert.deepEqual(chips.map((x) => x.click.match(/data-op="([^"]+)"/)![1]), ops)
    assert.equal(clicksOf(s, '#play').length, ops.filter((o) => plyOps.has(o)).length)
    assert.equal((s.find((x) => 'card' in x && x.card) as { card: { title: string } }).card.title, chapterCard(ch))
    assert.equal(chapterCard(ch), ch === 19 ? 'Chapter 19 — Wings' : 'Chapter 20 — Winglets and rudders')
    const fin = s.find((x) => 'act' in x && x.act === 'finish') as { op?: string }
    assert.equal(fin.op, last)
    for (const op of holds) {
      const i = chips.findIndex((x) => x.click.includes(`"${op}"`))
      assert.ok(i >= 0 && (i + 1 >= chips.length || chips[i + 1].t - chips[i].t >= KIN_HOLD[op]), `${op}: the swing finishes before the next op`)
    }
  })
}
