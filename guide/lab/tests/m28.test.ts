// Chapters 21 to 23 in the lab: where each strake, electrical and engine part is for every op (the right strake's kit on the layup table, then on the airplane, the
// openings in the fuselage side on their own op), the fuel capacity conflict, the battery range, the starter bound and the engine limits as text, the ply
// schedules from the ops' own materials, the reference weight rows, the chapter registration, the book order and the three tours. The part rows and figures come
// from python (tests/fixtures/kernels.json extras.m28 = guide.fuselage_export.m28_section), so a drift on either side fails here.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  m28Where, partBase, strakeBenchAt, strakeTableShown, m28GhostAt, m28Exposed, fuelText, cutoutText, layup7Text, batteryText, starterText, engineText, engineCgText, layupText, m28Kin, m28Row,
  CH21, CH22, CH23, KIT_PARTS, KIT_LIFT_IN, M28_GHOST_OPS, TANK_OPS, CUT_PARTS_OP, CUTOUTS_OP, JIG_BOND_OP, CLOSE_TANK_OP, BATTERY_OP, ROOT_RIB_OP, ENGINE_OP, type M28Data,
} from '../src/logic/strake'
import { M25_CHAPTERS, FUSE_PREFIXES } from '../src/logic/m25'
import { FUSE_CHAPTERS, FUSE_TOUR_CHAPTERS, M25_TOUR_CHAPTERS, cutRangeFor } from '../src/logic/fuselage'
import { barOps } from '../src/logic/graph'
import { fuseView, M28_VIEWS } from '../src/fuseShots'
import { fuselageTour, fuselageTourChapters, chapterCard, type Step, type TourGraph } from '../src/director'

const fx = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/kernels.json', import.meta.url)), 'utf8'))
const d: M28Data = fx.extras.m28
const rows = Object.entries(d.parts)

// the book order in the graph: chapters 14 to 20, the two chapter 16 ops that wait on the wings, then 21, 22, 23 (nothing of 14 to 20 after f21.cut-parts)
const order = ['f17.fixed-trim-tab', 'f18.safety-catch', 'f19.attach', 'f16.aileron-linkage', 'f20.rudder-hang', 'f16.rudder-cable-rig', 'f16.brake-cables', ...CH21, ...CH22, ...CH23]
const where = (part: string, op: string | null) => m28Where(d.parts[part], op, order)

test('the python section has 20 strake parts a side, 15 electrical and 11 engine parts: every part row names an op of chapters 21 to 23', () => {
  const all = new Set([...CH21, ...CH22, ...CH23])
  for (const [k, r] of rows) {
    assert.ok(all.has(r.show.from), `${k} shows from ${r.show.from}`)
    assert.ok(order.includes(r.show.from))
    assert.ok(['right', 'left', null].includes(r.side), k)
  }
  assert.equal(rows.filter(([, r]) => r.component.startsWith('strake.')).length, 40)
  assert.equal(rows.filter(([, r]) => r.component.startsWith('elec.')).length, 15)
  assert.equal(rows.filter(([, r]) => r.component.startsWith('engine.')).length, 11)
  assert.equal(partBase(d.parts.strake_ribs_rib_r23_right), 'rib_r23')
  assert.equal(partBase(d.parts.elec_battery_shelf_shelf), 'shelf')
  assert.equal(partBase(d.parts.engine_rib_rib_left), 'rib_left')
})

test('the right strake kit lies on the layup table on the cutting op, then each piece stands in its place from its own op, both sides', () => {
  assert.deepEqual([...KIT_PARTS].sort(), ['b23', 'bab', 'ble', 'db', 'od', 'rib_r23', 'rib_r45', 'skin_bottom', 'skin_top', 'tle'])
  for (const p of ['strake_ribs_rib_r23', 'strake_baffles_db', 'strake_baffles_od', 'strake_leading_edge_tle', 'strake_skins_skin_bottom', 'strake_skins_skin_top']) {
    assert.equal(where(`${p}_right`, CUT_PARTS_OP), 'table', p)
    assert.equal(where(`${p}_left`, CUT_PARTS_OP), 'none', p) // the left is the mirror, cut the same way
  }
  assert.equal(where('strake_skins_skin_bottom_right', CUTOUTS_OP), 'none') // the kit waits on the table; the airplane is the subject of the cutouts op
  for (const side of ['right', 'left']) {
    assert.equal(where(`strake_ribs_rib_r45_${side}`, JIG_BOND_OP), 'jig')
    assert.equal(where(`strake_baffles_od_${side}`, JIG_BOND_OP), 'none')
    assert.equal(where(`strake_baffles_od_${side}`, 'f21.od-outlet'), 'jig')
    assert.equal(where(`strake_skins_skin_top_${side}`, 'f21.inside-layups'), 'none')
    assert.equal(where(`strake_skins_skin_top_${side}`, CLOSE_TANK_OP), 'jig')
    assert.equal(where(`strake_tank_tank_${side}`, 'f21.vent-screen'), 'none')
    assert.equal(where(`strake_tank_tank_${side}`, CLOSE_TANK_OP), 'jig')
    assert.equal(where(`strake_sump_sump_blister_${side}`, 'f21.od-outlet'), 'none')
    assert.equal(where(`strake_sump_sump_blister_${side}`, 'f21.outside-bottom'), 'jig')
    assert.equal(where(`strake_sump_sump_blister_${side}`, 'f23.root-rib'), 'jig')
    assert.equal(where(`strake_fittings_fuel_cap_${side}`, 'f21.pressure-check'), 'none')
    assert.equal(where(`strake_fittings_fuel_cap_${side}`, 'f21.fairing-caps'), 'jig')
  }
  assert.equal(where('strake_ribs_rib_r23_right', null), 'none')
  assert.equal(where('strake_ribs_rib_r23_right', 'f18.safety-catch'), 'none')
})

test('the openings in the fuselage side (material removed) show on their own op only', () => {
  for (const p of ['strake_skins_cutout_baggage_right', 'strake_skins_cutout_baggage_left', 'strake_skins_cutout_tank_right', 'strake_skins_cutout_tank_left']) {
    assert.equal(d.parts[p].void, true, p)
    assert.equal(where(p, CUTOUTS_OP), 'jig', p)
    for (const op of ['f21.cut-parts', JIG_BOND_OP, 'f21.plumbing', 'f22.battery-shelf']) assert.equal(where(p, op), 'none', `${p} ${op}`)
  }
})

test('the electrical and engine parts stand from their own ops, striped (representational) unless python says otherwise', () => {
  assert.equal(where('elec_battery_shelf_shelf', 'f22.microswitches'), 'none')
  assert.equal(where('elec_battery_shelf_shelf', BATTERY_OP), 'jig')
  assert.equal(where('elec_relays_start_relay', BATTERY_OP), 'none')
  assert.equal(where('elec_relays_start_relay', 'f22.firewall-terminals'), 'jig')
  assert.equal(where('elec_wiring_panel_bundle', 'f22.panel-wiring'), 'jig')
  assert.equal(where('elec_lights_light_left', 'f22.firewall-terminals'), 'none')
  assert.equal(where('elec_lights_light_left', 'f22.wing-wiring'), 'jig')
  assert.equal(where('elec_antennas_comm_strips', 'f22.wing-wiring'), 'none')
  assert.equal(where('elec_antennas_comm_strips', 'f22.antennas'), 'jig')
  assert.equal(where('engine_block_block', 'f22.antennas'), 'none')
  assert.equal(where('engine_block_block', ENGINE_OP), 'jig')
  assert.equal(where('engine_bracket_bracket', ENGINE_OP), 'none')
  assert.equal(where('engine_bracket_bracket', 'f23.carb-bracket'), 'jig')
  assert.equal(where('engine_cowl_cowl', 'f23.cowl-trim'), 'jig')
  assert.equal(where('engine_rib_rib_right', 'f23.cowl-closeout'), 'none')
  assert.equal(where('engine_rib_rib_right', ROOT_RIB_OP), 'jig')
  assert.ok(rows.every(([, r]) => r.fidelity === 'representational' || r.fidelity === 'derived'))
  assert.ok(d.engine.striped.includes('engine.block.block') && d.parts.engine_block_block.fidelity === 'representational')
  for (const c of ['starter', 'alternator', 'magnetos', 'carburettor', 'fuel_pump', 'mount_pads']) {
    const r = d.parts[`engine_${c}_${c}`]
    assert.equal(r.fidelity, 'representational', c)
    assert.ok(d.engine.striped.includes(`engine.${c}.${c}`) && r.label.includes('(fitted shape'), c)
    assert.equal(where(`engine_${c}_${c}`, 'f22.antennas'), 'none', c)
    assert.equal(where(`engine_${c}_${c}`, ENGINE_OP), 'jig', c)
  }
  assert.ok(d.parts.engine_block_block.label.includes('Section II, not held') && d.parts.engine_block_block.label.includes('(fitted shape'))
  assert.ok(d.parts.elec_battery_battery.label.includes('station not printed'))
})

test('the kit is the only thing on the table: the airplane is not drawn then; the jig table stands from the bond to the tank closing; faint ops and what stays solid', () => {
  assert.ok(strakeBenchAt(CUT_PARTS_OP) && !strakeBenchAt(CUTOUTS_OP) && !strakeBenchAt(null) && !strakeBenchAt('f19.attach'))
  for (const [op, on] of [['f21.cut-parts', false], ['f21.fuselage-cutouts', false], ['f21.jig-bond', true], ['f21.inside-layups', true], ['f21.vent-screen', true], ['f21.close-tank', true], ['f21.od-outlet', false], ['f21.plumbing', false], ['f22.battery-shelf', false], [null, false]] as const) {
    assert.equal(strakeTableShown(op, order), on, String(op))
  }
  assert.ok(KIT_LIFT_IN > 8, 'the top core clears the ribs and baffles')
  assert.deepEqual([...M28_GHOST_OPS].sort(), ['f21.close-tank', 'f21.fuselage-cutouts', 'f21.od-outlet', 'f21.outside-bottom', 'f21.pressure-check', 'f21.vent-screen', 'f22.antennas', 'f22.battery-shelf', 'f22.firewall-terminals', 'f22.panel-wiring', 'f23.carb-bracket', 'f23.root-rib'])
  assert.ok(m28GhostAt({ id: BATTERY_OP }) && !m28GhostAt({ id: 'f21.jig-bond' }) && !m28GhostAt(null))
  const op = (id: string, components: string[]) => ({ id, components })
  // the tank ops expose only the tank (the skins would hide it); the others their own components
  assert.deepEqual([...TANK_OPS].sort(), ['f21.close-tank', 'f21.pressure-check'])
  assert.ok(m28Exposed(op(CLOSE_TANK_OP, ['strake.skins', 'strake.tank']), 'strake.tank') && !m28Exposed(op(CLOSE_TANK_OP, ['strake.skins', 'strake.tank']), 'strake.skins'))
  assert.ok(m28Exposed(op(BATTERY_OP, ['elec.battery_shelf', 'elec.battery']), 'elec.battery') && !m28Exposed(op(BATTERY_OP, ['elec.battery_shelf', 'elec.battery']), 'fuselage.firewall'))
})

test('the fuel capacity conflict is text with both printed figures, the model and the envelope; never a bare number', () => {
  const t = fuelText(d)
  assert.equal(t.value, 'Tank capacity: plans 2 x 25.5 gal, manual 2 x 28 gal (52 in all); model 26 a side')
  assert.equal(t.sub, 'Unresolved. Shaded envelope 24.6 gal a side (fitted shape, not measured); fuel 6.0 lb per gal at FS 104.5')
  for (const op of ['f21.cut-parts', 'f21.close-tank', 'f21.pressure-check', 'f21.fairing-caps', 'f21.plumbing']) assert.equal(m28Kin(op, d)!.value, t.value, op)
  assert.deepEqual([d.fuel.plans_gal_per_tank, d.fuel.om_gal_per_tank, d.fuel.om_total_gal, d.fuel.model_gal_per_side], [25.5, 28, 52, 26])
})

test('the other conflicts are text on their ops: the cutout depth and baggage arm, the layup 7 numbering', () => {
  assert.equal(cutoutText(d).value, 'Tank hole aft end: 1.9 in below WL 23 once, 1.4 in elsewhere on the page')
  assert.ok(cutoutText(d).sub.includes('Unresolved') && cutoutText(d).sub.includes('FS 90 in the manual, FS 80.6 from the floor'), cutoutText(d).sub)
  assert.equal(m28Kin(CUTOUTS_OP, d)!.value, cutoutText(d).value)
  assert.ok(layup7Text(d).value.includes('printed twice') && layup7Text(d).sub.includes('Unresolved'))
  assert.equal(m28Kin('f21.od-outlet', d)!.value, layup7Text(d).value)
  assert.equal(m28Kin('f21.outside-bottom', d)!.value, layup7Text(d).value)
})

test('the battery station is a range, the starter and alternator a bound, the engine its two limits and what the block stands for', () => {
  assert.equal(batteryText(d).value, 'Battery station: FS 0 to 22, not printed (A6 only)')
  assert.ok(batteryText(d).sub.includes('Drawn at FS 11 for illustration only') && batteryText(d).sub.includes('reference, not in CG'))
  assert.equal(starterText(d).value, 'Starter, ring gear and alternator: station 150 or aft (CP27 page 4), not drawn')
  assert.ok(starterText(d).sub.startsWith('A bound, not a station'))
  assert.equal(engineText(d).value, 'Engine with accessories at most 246 lb, vibrating mass at most 286 lb; oil 8 lb at FS 140')
  assert.ok(engineText(d).sub.startsWith('Fitted shape; installation in Section II, not held') && engineText(d).sub.includes('O-235 component model (fitted shape) placed from the prop flange, 2 deg down thrust') && !engineText(d).sub.includes('30 x 32 x 18'), engineText(d).sub)
  assert.equal(m28Kin('f22.battery-shelf', d)!.value, batteryText(d).value)
  assert.equal(m28Kin('f22.firewall-terminals', d)!.value, starterText(d).value)
  assert.equal(m28Kin(ENGINE_OP, d)!.value, engineText(d).value)
  for (const op of ['f21.jig-bond', 'f21.vent-screen', 'f22.microswitches', 'f22.antennas', 'f23.carb-bracket', 'f23.root-rib', null]) assert.equal(m28Kin(op, d), null, String(op))
})

test('the f23 engine-op readout states the component-model CG from the exported table and answers only its own op', () => {
  const t = engineCgText(d)
  const u = d.engine.mass.cg_from_flange_in.toFixed(2)
  assert.equal(t, `component model, CG ${u} in from the flange vs TCDS 14.75`)
  assert.ok(Number(u) > 0 && Number(u) < 30 && d.engine.mass.tcds_cg_from_flange_in === 14.75)
  assert.ok(m28Kin(ENGINE_OP, d)!.sub.includes(t), m28Kin(ENGINE_OP, d)!.sub)
  // the number follows the export: change it and the text follows
  const moved = { ...d, engine: { ...d.engine, mass: { ...d.engine.mass, cg_from_flange_in: 13.37 } } }
  assert.ok(m28Kin(ENGINE_OP, moved)!.sub.includes('CG 13.37 in from the flange'))
  // null test: no other op shows it, earlier ones in chapters 21 to 23 included
  for (const op of [...CH21, ...CH22, ...CH23].filter((o) => o !== ENGINE_OP)) {
    const k = m28Kin(op, d)
    assert.ok(!k || !(k.value + k.sub).includes('component model'), op)
  }
  assert.equal(m28Kin('f19.top-skin', d), null)
})

test('the layup schedules come from the ops own materials: collapsed by cloth, with where each ply goes; an op with a conflict carries both', () => {
  const m = [{ cloth: 'BID', plies: 1, where: 'layup 1' }, { cloth: 'BID', plies: 1, where: 'layup 2' }, { cloth: 'BID', plies: 1, where: 'layup 3' }, { cloth: 'UND', plies: 2, where: 'layup 3 strip' }]
  assert.deepEqual(layupText(m), { value: '5 plies: 3 BID + 2 UND', sub: '1 BID, layup 1; 1 BID, layup 2; 1 BID, layup 3; 2 UND, layup 3 strip' })
  assert.equal(layupText([]), null)
  assert.equal(m28Kin('f21.inside-layups', d, m)!.label, 'Layup schedule')
  assert.equal(m28Kin('f21.inside-layups', d, m)!.value, '5 plies: 3 BID + 2 UND')
  const both = m28Kin(CLOSE_TANK_OP, d, m)!
  assert.equal(both.value, fuelText(d).value)
  assert.ok(both.sub.includes('Plies: 5 plies: 3 BID + 2 UND'), both.sub)
  assert.equal(m28Kin('f21.jig-bond', d, []), null)
  // another chapter's op keeps its own readout, however many plies it has (chapter 13's nose wheel conflict was displaced by a layup schedule)
  assert.equal(m28Kin('f13.carve-glass-nose', d, m), null)
  assert.equal(m28Kin('f19.top-skin', d, m), null)
  assert.equal(m28Kin(null, d, m), null)
})

const rowsLed = {
  n26ms_empty_1: 693.4, n26ms_empty_2: 698.3, n26ms_empty_3: 713.7, n26ms_empty_4: 761.9, n26ms_empty_5: 777.3, n26ms_empty_6: 815.4, n26ms_empty_7: 860.2, n26ms_empty_8: 883.0,
  dynafocal_mount: 5.19, cowl_glass: 18, cowl_graphite: 12,
}
const led = { cg: {}, cg_lower_bound: {}, prototype_weights: { rows: Object.fromEntries(Object.entries(rowsLed).map(([k, w]) => [k, { weight_lb: w, cite: 'x', note: `${k} note` }])) } } as never
test('the reference rows: the N26MS ladder from the battery op, the mount, the cowl, the closure target at the end; never in the CG', () => {
  const ladder = '693.4 / 698.3 / 713.7 / 761.9 / 777.3 / 815.4 / 860.2 / 883.0'
  assert.equal(m28Row(led, d, 'f21.plumbing', order), null)
  assert.equal(m28Row(led, d, 'f22.panel-wiring', order), null)
  assert.equal(m28Row(led, d, BATTERY_OP, order)!.value, `N26MS empty-weight ladder (CP27 page 4): ${ladder} lb, reference, not in CG`)
  assert.equal(m28Row(led, d, 'f22.antennas', order)!.value, m28Row(led, d, BATTERY_OP, order)!.value)
  assert.equal(m28Row(led, d, ENGINE_OP, order)!.value, 'Dynafocal mount (CP26 builder weight, N26MS): 5.19 lb, reference, not in CG')
  assert.equal(m28Row(led, d, 'f23.carb-bracket', order)!.value, m28Row(led, d, ENGINE_OP, order)!.value)
  assert.equal(m28Row(led, d, 'f23.cowl-trim', order)!.value, 'Cowl (CP27 page 5): 18.0 lb in glass, 12.0 lb in graphite, reference, not in CG')
  assert.equal(m28Row(led, d, 'f23.cowl-closeout', order)!.value, m28Row(led, d, 'f23.cowl-trim', order)!.value)
  const end = m28Row(led, d, ROOT_RIB_OP, order)!
  assert.equal(end.value, `Closure target: OM sample empty airplane 730 lb at FS 111.7, reference, not in CG; N26MS ladder ${ladder} lb`)
  assert.ok(end.sub.includes('FS 97 to 103 is the loaded envelope, not the empty CG') && end.sub.includes('CG not yet computed'), end.sub)
  assert.equal(m28Row(led, d, 'f20.rudder-hang', order), null); assert.equal(m28Row(led, d, null, order), null); assert.equal(m28Row(null, d, BATTERY_OP, order), null); assert.equal(m28Row(led, null, BATTERY_OP, order), null)
  assert.deepEqual(d.weights.rows.slice(0, 8), Object.keys(rowsLed).slice(0, 8))
})

test('chapters 21 to 23 are the fuselage subject with a tour each, every op has a shot of its own, and they follow chapter 20 in book order', () => {
  assert.deepEqual([21, 22, 23].filter((c) => !FUSE_CHAPTERS.has(c) || !M25_CHAPTERS.has(c)), [])
  assert.ok(['strake.', 'elec.', 'engine.'].every((p) => FUSE_PREFIXES.includes(p)))
  assert.ok(![21, 22, 23].some((c) => FUSE_TOUR_CHAPTERS.includes(c) || M25_TOUR_CHAPTERS.includes(c)))
  assert.deepEqual(cutRangeFor(22), { min: -6.8, max: 160 }) // the nose battery (FS 7 to 15) and the engine block (to FS 157) are both reachable
  assert.ok(cutRangeFor(20).min === 22 && cutRangeFor(13).min === -6.8)
  assert.deepEqual(Object.keys(M28_VIEWS).sort(), [...CH21, ...CH22, ...CH23].sort())
  for (const id of [...CH21, ...CH22, ...CH23]) assert.equal(fuseView(id), M28_VIEWS[id], id)
  assert.equal(M28_VIEWS['f21.cut-parts'].focus, 'strake-table')
  // book order: nothing of chapters 14 to 20 (the deferred chapter 16 ops included) after the first op of 21, then 21, 22, 23 in that order
  const ch = (id: string) => Number(/^f(\d+)\./.exec(id)![1])
  const i21 = order.indexOf('f21.cut-parts')
  assert.ok(order.slice(i21).every((o) => ch(o) >= 21), 'nothing earlier than chapter 21 after f21.cut-parts')
  assert.ok(order.slice(0, i21).every((o) => ch(o) <= 20))
  const chs = order.slice(i21).map(ch)
  assert.deepEqual(chs, [...chs].sort((a, b) => a - b))
  // the bar: these ops are the fuselage subject's, never the canard's
  const G = { order, ops: order.map((id) => ({ id, chapter: ch(id), title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })) }
  assert.deepEqual(barOps(G as never, 'roncz').filter((o) => ch(o.id) >= 21), [])
})

const fop = (id: string, chapter: number) => ({ id, chapter, title: id, summary: '', variants: ['roncz'], stub: false, components: [] as string[] })
const clicksOf = (s: Step[], pre: string) => s.filter((x) => 'click' in x && x.click.startsWith(pre)) as { t: number; click: string }[]
for (const [ch, ops, last] of [[21, CH21, 'f21.plumbing'], [22, CH22, 'f22.antennas'], [23, CH23, ROOT_RIB_OP]] as const) {
  test(`the chapter ${ch} tour visits every op in order, plays no plies (none are drawn), and closes on the last op`, () => {
    const TG: TourGraph = { order: ops.slice(), ops: ops.map((o) => fop(o, ch)) }
    assert.deepEqual(fuselageTourChapters(TG, 'roncz', ops[1]), [ch])
    const s = fuselageTour(TG, 'roncz', () => 0, [ch])
    assert.deepEqual(clicksOf(s, '#chips').map((x) => x.click.match(/data-op="([^"]+)"/)![1]), ops)
    assert.equal(clicksOf(s, '#play').length, 0)
    assert.equal((s.find((x) => 'card' in x && x.card) as { card: { title: string } }).card.title, chapterCard(ch))
    assert.equal(chapterCard(ch), ch === 21 ? 'Chapter 21 — Strakes and fuel' : ch === 22 ? 'Chapter 22 — Electrical system' : 'Chapter 23 — Engine and cowl')
    assert.equal((s.find((x) => 'act' in x && x.act === 'finish') as { op?: string }).op, last)
  })
}
