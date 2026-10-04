// Chapters 24 to 26 in the lab: where each cover, console, seal, cushion and suitcase is for every op, the finish layer by stage (fill, primer, paint; white on the
// upper wing and canard only), the ch24 conflicts, the seal fractions, the finish thicknesses and the 70 F rule as text, "no finish weight printed", the N26MS finish
// deltas and the 2.n closure target as references, the chapter registration, the book order and the three tours. The part rows and figures come from python
// (tests/fixtures/kernels.json extras.m29 = guide.fuselage_export.m29_section), so a drift on either side fails here.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  m29Where, finishStageAt, finishColour, finishRowFor, frac, aftCoverText, lc2Text, sealText, shopText, fillText, primerText, paintText, upholsteryText, layupText, m29Kin, m29Row,
  m29GhostAt, cockpitOpenAt, CH24, CH25, CH26, FILL_COLOUR, FINISH_COLOURS, M29_GHOST_OPS, COCKPIT_OPS, AFT_COVER_OP, CONSOLES_OP, GAP_SEAL_OP, INSPECT_OP, COARSE_FILL_OP,
  FEATHER_FILL_OP, PRIMER_OP, PAINT_OP, CUSHIONS_OP, SUITCASES_OP, type M29Data,
} from '../src/logic/finish'
import { M25_CHAPTERS, FUSE_PREFIXES } from '../src/logic/m25'
import { FUSE_CHAPTERS, FUSE_TOUR_CHAPTERS, M25_TOUR_CHAPTERS, cutRangeFor } from '../src/logic/fuselage'
import { barOps } from '../src/logic/graph'
import { fuseView, M29_VIEWS } from '../src/fuseShots'
import { fuselageTour, fuselageTourChapters, chapterCard, type Step, type TourGraph } from '../src/director'

const fx = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/kernels.json', import.meta.url)), 'utf8'))
const d: M29Data = fx.extras.m29
const rows = Object.entries(d.parts)

// the book order in the graph: the chapter 23 ops, then 24, 25, 26 (nothing of 14 to 23 after f24.aft-cover)
const order = ['f19.attach', 'f21.plumbing', 'f22.antennas', 'f23.engine-install', 'f23.root-rib', ...CH24, ...CH25, ...CH26]
const where = (part: string, op: string | null) => m29Where(d.parts[part], op, order)

test('the python section has 14 cover parts and 6 upholstery parts: every part row names an op of chapters 24 or 26 and is a fitted shape unless it is LC1', () => {
  const all = new Set([...CH24, ...CH26])
  for (const [k, r] of rows) {
    assert.ok(all.has(r.show.from), `${k} shows from ${r.show.from}`)
    assert.ok(r.fidelity === 'representational' || k === 'cover_console_lc1_lc1', k)
  }
  assert.equal(rows.filter(([, r]) => r.component.startsWith('cover.')).length, 14)
  assert.equal(rows.filter(([, r]) => r.component.startsWith('upholstery.')).length, 6)
  assert.equal(d.parts.cover_console_lc1_lc1.fidelity, 'book')
})

test('each part stands in its place from the op its row names and never before; nothing before chapter 24 shows any of them', () => {
  assert.equal(where('cover_aft_aft_cover', 'f23.root-rib'), 'none')
  assert.equal(where('cover_aft_aft_cover', AFT_COVER_OP), 'jig')
  assert.equal(where('cover_console_lc1_lc1', AFT_COVER_OP), 'none')
  assert.equal(where('cover_console_lc1_lc1', 'f24.console-lc1'), 'jig')
  for (const p of ['cover_consoles_lc2', 'cover_consoles_lc3', 'cover_consoles_lc4', 'cover_consoles_lc5', 'cover_consoles_lc6']) {
    assert.equal(where(p, 'f24.console-lc1'), 'none', p)
    assert.equal(where(p, CONSOLES_OP), 'jig', p)
  }
  assert.equal(where('cover_thigh_thigh_floor', CONSOLES_OP), 'none')
  assert.equal(where('cover_thigh_thigh_floor', 'f24.thigh-support'), 'jig')
  assert.equal(where('cover_valve_valve_cover', 'f24.thigh-support'), 'jig')
  assert.equal(where('cover_canard_canard_cover', 'f24.thigh-support'), 'none')
  assert.equal(where('cover_canard_canard_cover', 'f24.canard-cover'), 'jig')
  for (const side of ['right', 'left']) {
    assert.equal(where(`cover_seal_seal_${side}`, 'f24.canard-cover'), 'none')
    assert.equal(where(`cover_seal_seal_${side}`, GAP_SEAL_OP), 'jig')
  }
  // the finish ops keep every cover; the upholstery waits for chapter 26
  for (const op of CH25) { assert.equal(where('cover_seal_seal_left', op), 'jig', op); assert.equal(where('upholstery_cushions_front_cushion', op), 'none', op) }
  assert.equal(where('upholstery_cushions_front_cushion', CUSHIONS_OP), 'jig')
  assert.equal(where('upholstery_headrests_rear_headrest', CUSHIONS_OP), 'jig')
  assert.equal(where('upholstery_suitcases_suitcase_right', CUSHIONS_OP), 'none')
  assert.equal(where('upholstery_suitcases_suitcase_left', SUITCASES_OP), 'jig')
  // by the last op every part stands
  assert.ok(rows.every(([k]) => where(k, SUITCASES_OP) === 'jig'))
  for (const op of ['f19.attach', 'f21.plumbing', 'f23.root-rib', null]) assert.ok(rows.every(([k]) => where(k, op) === 'none'), String(op))
})

test('the gap seal buries itself in the wing root, so its op draws the airplane faint; the cockpit ops leave the canopy out of the frame', () => {
  assert.deepEqual([...M29_GHOST_OPS], [GAP_SEAL_OP])
  assert.ok(m29GhostAt({ id: GAP_SEAL_OP }) && !m29GhostAt({ id: 'f24.canard-cover' }) && !m29GhostAt(null))
  assert.deepEqual([...COCKPIT_OPS].sort(), ['f24.console-lc1', 'f24.consoles-left', 'f24.thigh-support', 'f26.cushions-headrests', 'f26.suitcases'])
  assert.ok(cockpitOpenAt({ id: CUSHIONS_OP }) && !cockpitOpenAt({ id: PAINT_OP }) && !cockpitOpenAt(null))
})

// ---- the finish ----
const finRows = d.finish.rows
const rowFor = (component: string, node: string) => finishRowFor(finRows, component, node)!
const WING_TOP = rowFor('wing.skins', 'wing.skins.skin_top.right')
const WING_BOTTOM = rowFor('wing.skins', 'wing.skins.skin_bottom.left')
const CANARD_TOP = rowFor('canard.skin_top', 'canard.skin_top')

test('the finish stage follows the op: bare before the filler, fill from the coarse fill, primer, then paint; it stays painted on the upholstery ops and on no earlier chapter', () => {
  const stage = (r: typeof WING_TOP, op: string | null) => finishStageAt(r, op, order)
  for (const op of ['f19.attach', 'f23.root-rib', ...CH24, INSPECT_OP, null]) assert.equal(stage(WING_TOP, op), null, String(op))
  assert.equal(stage(WING_TOP, COARSE_FILL_OP), 'fill')
  assert.equal(stage(WING_TOP, FEATHER_FILL_OP), 'fill')
  assert.equal(stage(WING_TOP, PRIMER_OP), 'primer')
  assert.equal(stage(WING_TOP, PAINT_OP), 'paint')
  assert.equal(stage(WING_TOP, CUSHIONS_OP), 'paint')
  assert.equal(stage(WING_TOP, SUITCASES_OP), 'paint')
})

test('white goes on the upper wing and canard only: every other surface is filler tint, then primer grey, and stays grey after the paint', () => {
  assert.deepEqual(finRows.filter((r) => r.final_colour === 'white').map((r) => r.surface).sort(), ['canard_upper', 'canard_upper', 'wing_upper'])
  assert.equal(finishColour(WING_TOP, 'fill'), FILL_COLOUR)
  assert.equal(finishColour(WING_TOP, 'primer'), FINISH_COLOURS['primer-grey'])
  assert.equal(finishColour(WING_TOP, 'paint'), FINISH_COLOURS.white)
  assert.equal(finishColour(CANARD_TOP, 'paint'), FINISH_COLOURS.white)
  assert.equal(finishColour(rowFor('cover.canard', 'cover.canard.canard_cover'), 'paint'), FINISH_COLOURS.white) // the cover lies on the canard's top
  for (const [c, n] of [['wing.skins', 'wing.skins.skin_bottom.right'], ['canard.skin_bottom', 'canard.skin_bottom'], ['strake.skins', 'strake.skins.skin_top.right'], ['nose.skin', 'nose.skin'], ['winglet.skins', 'winglet.skins.skin_in.right'], ['cover.aft', 'cover.aft.aft_cover']] as const) {
    const r = rowFor(c, n)
    assert.equal(finishColour(r, 'paint'), FINISH_COLOURS['primer-grey'], c)
    assert.equal(finishColour(r, 'primer'), FINISH_COLOURS['primer-grey'], c)
  }
  assert.equal(finishColour(WING_BOTTOM, 'paint'), FINISH_COLOURS['primer-grey'])
  assert.notEqual(FILL_COLOUR, FINISH_COLOURS['primer-grey'])
})

test('the fuselage skins are the sides and bottom in the glb (the graph skin components have no geometry), so the finish row applies to them; an unfinished part gets none', () => {
  assert.ok(finishRowFor(finRows, 'fuselage.side_left', 'fuselage.side_left'))
  assert.ok(finishRowFor(finRows, 'fuselage.side_right', 'fuselage.side_right.p3'))
  assert.ok(finishRowFor(finRows, 'fuselage.bottom', 'fuselage.bottom'))
  assert.equal(finishRowFor(finRows, 'fuselage.firewall', 'fuselage.firewall'), null)
  assert.equal(finishRowFor(finRows, 'cover.consoles', 'cover.consoles.lc2'), null) // the consoles are inside the cockpit, not on the painted surfaces
  assert.equal(finishRowFor(finRows, 'canopy.plexi', 'canopy.plexi'), null)
  assert.equal(finishRowFor(finRows, 'wing.skins', 'wing.skins.tip_cap.right'), null) // a skin_top / skin_bottom match, not any wing skin node
})

// ---- the readouts ----
test('the aft cover plies and the LC2 length are text on their ops with both printed figures; never a bare number', () => {
  assert.equal(aftCoverText(d).value, 'Aft cover plies: scan 1 inside and 1 outside, transcription 1 inside and 2 outside')
  assert.ok(aftCoverText(d).sub.startsWith('Unresolved.') && aftCoverText(d).sub.includes('LPC 54'), aftCoverText(d).sub)
  assert.equal(lc2Text(d).value, 'Console top LC2 length: 30.6 in on the scan, 30.8 in in the transcription')
  assert.ok(lc2Text(d).sub.startsWith('Unresolved.'))
  assert.equal(m29Kin(AFT_COVER_OP, d)!.value, aftCoverText(d).value)
  assert.equal(m29Kin(CONSOLES_OP, d)!.value, lc2Text(d).value)
  assert.deepEqual([d.conflicts.aft_cover_plies.scan_inside_outside, d.conflicts.aft_cover_plies.transcription_inside_outside, d.conflicts.lc2_length_in.scan, d.conflicts.lc2_length_in.transcription], [[1, 1], [1, 2], 30.6, 30.8])
})

test('the gap seal reads 1/2 in with 1/16 in at the front, as fractions of an inch', () => {
  assert.equal(frac(0.5), '1/2'); assert.equal(frac(0.0625), '1/16'); assert.equal(frac(0.75), '3/4'); assert.equal(frac(0.3), '0.3')
  assert.equal(sealText(d).value, 'Gap seal: 1/2 in gap at the wing root, 1/16 in at the front')
  assert.ok(sealText(d).sub.includes('cannot be told from 3/4'), sealText(d).sub)
  assert.equal(m29Kin(GAP_SEAL_OP, d)!.value, sealText(d).value)
})

test('the finish thicknesses, the weave and the 70 F rule are text on the finishing ops; the paint op says no finish weight is printed', () => {
  assert.equal(shopText(d).value, 'Finishing: shop held at 70 F or above; glass weave 0.009 in rough')
  assert.equal(fillText(d).value, 'Feather fill 0.02 to 0.03 in over the 0.009 in weave, shop at 70 F or above')
  assert.equal(primerText(d).value, 'Primer 0.004 to 0.008 in over the sanded fill')
  assert.equal(paintText(d).value, 'No finish weight printed. White on the upper wing and canard only; primer grey elsewhere')
  assert.equal(m29Kin(INSPECT_OP, d)!.value, shopText(d).value)
  assert.equal(m29Kin(FEATHER_FILL_OP, d)!.value, fillText(d).value)
  assert.equal(m29Kin(PRIMER_OP, d)!.value, primerText(d).value)
  assert.equal(m29Kin(PAINT_OP, d)!.value, paintText(d).value)
  assert.equal(m29Kin(COARSE_FILL_OP, d), null)
  assert.equal(upholsteryText().value, 'No upholstery weight printed')
  assert.equal(m29Kin(CUSHIONS_OP, d)!.value, upholsteryText().value)
  assert.equal(m29Kin(SUITCASES_OP, d)!.value, upholsteryText().value)
})

test('the layup schedules come from the ops own materials; an op with a conflict carries both', () => {
  const m = [{ cloth: 'BID', plies: 1, where: 'inside' }, { cloth: 'BID', plies: 1, where: 'outside' }]
  assert.deepEqual(layupText(m), { value: '2 plies: 2 BID', sub: '1 BID, inside; 1 BID, outside' })
  assert.equal(layupText([]), null)
  const both = m29Kin(AFT_COVER_OP, d, m)!
  assert.equal(both.value, aftCoverText(d).value)
  assert.ok(both.sub.includes('Plies: 2 plies: 2 BID'), both.sub)
  assert.equal(m29Kin('f24.canard-cover', d, m)!.label, 'Layup schedule')
  assert.equal(m29Kin('f24.canard-cover', d, [])!, null)
})

test('the readouts answer ONLY chapters 24 to 26: an f13, f19 or f21 op returns null even with a layup schedule (the M2.8 round 3 trap)', () => {
  const m = [{ cloth: 'BID', plies: 4, where: 'anywhere' }]
  for (const op of ['f13.carve-glass-nose', 'f13.nose-wheel', 'f19.top-skin', 'f19.attach', 'f21.inside-layups', 'f21.close-tank', 'f22.battery-shelf', 'f23.root-rib', 'f27.something', 'r30.a', null]) {
    assert.equal(m29Kin(op, d, m), null, String(op))
    assert.equal(m29Kin(op, d), null, String(op))
    assert.equal(m29Row(d, op, order), null, String(op))
  }
  for (const op of [...CH24, ...CH25, ...CH26]) assert.ok(/^f2[456]\./.test(op))
})

test('the reference rows: the N26MS finish deltas on the finishing ops, the closure target and both OM samples on the last op; never in the CG', () => {
  const ref = ', reference, not in CG'
  assert.equal(m29Row(d, AFT_COVER_OP, order), null)
  assert.equal(m29Row(d, 'f24.gap-seal', order), null)
  assert.equal(m29Row(d, INSPECT_OP, order), null)
  const deltas = `N26MS finish deltas (CP26 page 3 against CP27 page 1): canopy 1 lb, aileron 0.275 lb, wing 2.2 lb${ref}`
  for (const op of [COARSE_FILL_OP, FEATHER_FILL_OP, PRIMER_OP, PAINT_OP]) assert.equal(m29Row(d, op, order)!.value, deltas, op)
  assert.ok(m29Row(d, PAINT_OP, order)!.sub.includes('no finish weight is printed'), m29Row(d, PAINT_OP, order)!.sub)
  assert.equal(m29Row(d, CUSHIONS_OP, order), null)
  const end = m29Row(d, SUITCASES_OP, order)!
  assert.equal(end.value, `Closure target: OM sample empty airplane 730 lb at FS 111.7${ref}`)
  assert.ok(end.sub.includes('light pilot 1113 lb at FS 103.96 (outside the 103 aft limit, as the manual says)'), end.sub)
  assert.ok(end.sub.includes('heavy pilot 1323 lb at FS 101.06 (inside)'), end.sub)
  assert.ok(end.sub.includes('FS 97 to 103 is the loaded envelope, not the empty CG') && end.sub.includes('CG not yet computed'), end.sub)
  assert.equal(m29Row(null, SUITCASES_OP, order), null)
  assert.deepEqual(Object.keys(d.weights.finish_deltas).sort(), ['finish_delta_aileron', 'finish_delta_canopy', 'finish_delta_wing'])
})

test('chapters 24 to 26 are the fuselage subject with a tour each, every op has a shot of its own, and they follow chapter 23 in book order', () => {
  assert.deepEqual([24, 25, 26].filter((c) => !FUSE_CHAPTERS.has(c) || !M25_CHAPTERS.has(c)), [])
  assert.ok(['cover.', 'upholstery.'].every((p) => FUSE_PREFIXES.includes(p)))
  assert.ok(![24, 25, 26].some((c) => FUSE_TOUR_CHAPTERS.includes(c) || M25_TOUR_CHAPTERS.includes(c)))
  assert.deepEqual(cutRangeFor(24), { min: -6.8, max: 160 })
  assert.deepEqual(cutRangeFor(26), { min: -6.8, max: 160 })
  assert.ok(cutRangeFor(20).min === 22 && cutRangeFor(13).min === -6.8)
  assert.deepEqual(Object.keys(M29_VIEWS).sort(), [...CH24, ...CH25, ...CH26].sort())
  for (const id of [...CH24, ...CH25, ...CH26]) assert.equal(fuseView(id), M29_VIEWS[id], id)
  const ch = (id: string) => Number(/^f(\d+)\./.exec(id)![1])
  const i24 = order.indexOf('f24.aft-cover')
  assert.ok(order.slice(i24).every((o) => ch(o) >= 24) && order.slice(0, i24).every((o) => ch(o) <= 23))
  const chs = order.slice(i24).map(ch)
  assert.deepEqual(chs, [...chs].sort((a, b) => a - b))
  const G = { order, ops: order.map((id) => ({ id, chapter: ch(id), title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })) }
  assert.deepEqual(barOps(G as never, 'roncz').filter((o) => ch(o.id) >= 24), [])
  // the finish ops frame the same whole-airplane view, the seats the cockpit from above
  assert.equal(M29_VIEWS['f25.primer'].dist, M29_VIEWS['f25.paint-seals'].dist)
  assert.ok(M29_VIEWS['f26.suitcases'].el >= 60)
})

const fop = (id: string, chapter: number) => ({ id, chapter, title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })
const clicksOf = (s: Step[], pre: string) => s.filter((x) => 'click' in x && x.click.startsWith(pre)) as { t: number; click: string }[]
for (const [ch, ops, last] of [[24, CH24, 'f24.gap-seal'], [25, CH25, 'f25.paint-seals'], [26, CH26, 'f26.suitcases']] as const) {
  test(`the chapter ${ch} tour visits every op in order, plays no plies (none are drawn), and closes on the last op`, () => {
    const TG: TourGraph = { order: ops.slice(), ops: ops.map((o) => fop(o, ch)) }
    assert.deepEqual(fuselageTourChapters(TG, 'roncz', ops[1]), [ch])
    const s = fuselageTour(TG, 'roncz', () => 0, [ch])
    assert.deepEqual(clicksOf(s, '#chips').map((x) => x.click.match(/data-op="([^"]+)"/)![1]), ops)
    assert.equal(clicksOf(s, '#play').length, 0)
    assert.equal((s.find((x) => 'card' in x && x.card) as { card: { title: string } }).card.title, chapterCard(ch))
    assert.equal(chapterCard(ch), ch === 24 ? 'Chapter 24 — Covers and consoles' : ch === 25 ? 'Chapter 25 — Finishing' : 'Chapter 26 — Upholstery')
    assert.equal((s.find((x) => 'act' in x && x.act === 'finish') as { op?: string }).op, last)
  })
}
