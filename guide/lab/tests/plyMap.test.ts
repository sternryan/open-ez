import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { mapPlies, plyPlan, plyNote, type DrawnPly, type MaterialRow } from '../src/logic/plyMap'

// Real rows: the op materials and drawn ply rows of a real build (tests/fixtures/ply-map.json says where they came from).
const real = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/ply-map.json', import.meta.url)), 'utf8')) as Record<string, { materials: MaterialRow[]; drawn: DrawnPly[] }>
const PANEL = real['f04.panel-f22-f28-fwd']

test('the panel forward faces: plies 1 and 2 are the BID face plies on panel, F22 and F28, in lay order', () => {
  const { targets, standIn } = plyPlan(PANEL.materials, PANEL.drawn)
  assert.equal(standIn, false)
  assert.equal(targets.length, 12) // 2 + 1 + 5 + 4 authored plies
  assert.deepEqual(targets[0], { ply: 1, cloth: 'BID', where: 'forward faces of panel, F22 and F28', meshes: ['fuselage.panel.p3', 'fuselage.f22.p3', 'fuselage.f28.p3'], lay: 3, why: null })
  assert.deepEqual(targets[1], { ply: 2, cloth: 'BID', where: 'forward faces of panel, F22 and F28', meshes: ['fuselage.panel.p4', 'fuselage.f22.p4', 'fuselage.f28.p4'], lay: 6, why: null })
  // every drawn mesh's cloth is the cloth of the authored ply it is laid as
  const cloth = new Map(PANEL.drawn.map((d) => [d.name, d.cloth]))
  for (const t of targets) for (const m of t.meshes) assert.equal(cloth.get(m), t.cloth, `${m} is laid as ply ${t.ply}`)
})

test('the panel forward faces: ply 5 is an UND canard-attach pad ply, not drawn, and never lands on a BID face ply', () => {
  const { targets } = plyPlan(PANEL.materials, PANEL.drawn)
  const p5 = targets[4]
  assert.equal(p5.cloth, 'UND')
  assert.equal(p5.where, 'F22 canard attach pad, left and right, forward face only')
  assert.deepEqual(p5.meshes, [])
  assert.equal(p5.lay, null)
  assert.match(plyNote(p5), /UND, F22 canard attach pad.*not drawn in the model; caption only/)
  // the upper-panel extra (ply 3) and all pad plies (4 to 12) are caption-only too: the model draws none of them
  assert.deepEqual(targets.slice(2).map((t) => t.lay), Array(10).fill(null))
  // the old proportional rule put ply 5 of 12 at lay 3 of 6: F28's first BID face ply
  const old = Math.min(6, Math.max(1, Math.ceil((5 * 6) / 12)))
  assert.equal(PANEL.drawn.find((d) => d.opOrder === old)!.name, 'fuselage.f28.p3')
  assert.notDeepEqual(p5.meshes, ['fuselage.f28.p3'])
})

test('the canard shear web: the excluded nut-plate pad plies play caption-only; the drawn plies keep their own rows', () => {
  const op = real['r30.shear-web']
  const { targets, standIn } = plyPlan(op.materials, op.drawn)
  assert.equal(standIn, false)
  assert.deepEqual(targets.slice(0, 6).map((t) => [t.cloth, t.meshes, t.lay]), op.drawn.map((d, i) => [d.cloth, [d.name], i + 1]))
  for (const t of targets.slice(6)) { assert.equal(t.where, 'pad over each CL-1 nut plate'); assert.equal(t.lay, null) }
})

test('representational plies that no authored row names (the chapter 14 spar caps): a labelled stand-in, never re-numbered', () => {
  const op = real['f14.spar-caps']
  const { targets, standIn } = plyPlan(op.materials, op.drawn)
  assert.equal(standIn, true)
  assert.equal(targets.length, 21)
  for (const t of targets) { assert.deepEqual(t.meshes, []); assert.equal(t.lay, null); assert.match(t.why!, /21 representational plies, not ply by ply/) }
})

test('a ply whose meshes are not the next ones in lay order is never shown by the scrubber', () => {
  const mats: MaterialRow[] = [{ cloth: 'BID', plies: 1, where: 'a' }, { cloth: 'UND', plies: 1, where: 'b' }]
  const drawn: DrawnPly[] = [
    { name: 'b1', part: 'x', cloth: 'UND', where: 'b', opOrder: 1 },
    { name: 'a1', part: 'x', cloth: 'BID', where: 'a', opOrder: 2 },
  ]
  const t = mapPlies(mats, drawn)
  assert.deepEqual(t.map((x) => [x.meshes, x.lay, x.why]), [[['a1'], null, 'drawn out of lay order'], [['b1'], 1, null]])
  // the op as a whole cannot follow the script, so it plays as a stand-in: no ply beat moves the scrubber
  const plan = plyPlan(mats, drawn)
  assert.equal(plan.standIn, true)
  assert.deepEqual(plan.targets.map((x) => x.lay), [null, null])
})

test('a row with the same where but another cloth is not this ply', () => {
  const t = mapPlies([{ cloth: 'UND', plies: 1, where: 'a' }], [{ name: 'a1', part: 'x', cloth: 'BID', where: 'a', opOrder: 1 }])
  assert.deepEqual(t[0].meshes, [])
  assert.equal(t[0].lay, null)
})
