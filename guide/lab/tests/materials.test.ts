import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { materialFor, type LayupNodeLite } from '../src/logic/materials'

// A copy of the real layup nodes (guide.layup.layup_json), so a change to the layup that the mapping cannot handle fails here.
const nodes = JSON.parse(readFileSync(new URL('./fixtures/layup-nodes.json', import.meta.url), 'utf8')) as Record<string, LayupNodeLite & { component: string; cloth: string; orientation: string; order: number }>

test('every ply of every component gets the material its cloth dictates', () => {
  assert.ok(Object.keys(nodes).length >= 10)
  for (const [node, n] of Object.entries(nodes)) {
    const m = materialFor(node, n.component, nodes)
    assert.equal(m.kind, n.cloth === 'UND' ? 'und' : 'bid', node)
    assert.equal(m.ply?.node, node)
    assert.equal(m.ply?.order, n.order)
    assert.equal(m.angles.length, n.cloth === 'UND' ? 1 : 2, node)
  }
})

test('spanwise UND runs along the span', () => {
  const n = { p: { cloth: 'UND', orientation: 'spanwise', order: 1 } }
  assert.deepEqual(materialFor('p', 'canard.skin_top', n).angles, [0])
})

test('45 degree BID has tows at +45 and -45', () => {
  const n = { p: { cloth: 'BID', orientation: '45 degrees', order: 1 } }
  assert.deepEqual(materialFor('p', 'canard.skin_top', n).angles, [45, -45])
})

test('crossed UND alternates +45 / -45 by ply order', () => {
  const n = { a: { cloth: 'UND', orientation: 'crossed', order: 1 }, b: { cloth: 'UND', orientation: 'crossed', order: 2 }, c: { cloth: 'UND', orientation: 'crossed', order: 3 } }
  assert.deepEqual([materialFor('a', 'w', n).angles, materialFor('b', 'w', n).angles, materialFor('c', 'w', n).angles], [[45], [-45], [45]])
  const real = Object.entries(nodes).filter(([, v]) => v.orientation === 'crossed' && v.cloth === 'UND')
  assert.ok(real.length >= 2)
  for (const [k, v] of real) assert.deepEqual(materialFor(k, v.component, nodes).angles, [v.order % 2 === 1 ? 45 : -45], k)
})

test('the core is foam and other plain parts are parts', () => {
  assert.equal(materialFor(null, 'canard.core', nodes).kind, 'foam')
  assert.equal(materialFor(null, 'jig.block', nodes).kind, 'part')
})

test('unknown cloth, orientation or ply throws', () => {
  assert.throws(() => materialFor('p', 'c', { p: { cloth: 'CSM', orientation: 'spanwise', order: 1 } }), /unknown cloth/)
  assert.throws(() => materialFor('p', 'c', { p: { cloth: 'UND', orientation: 'sideways', order: 1 } }), /orientation/)
  assert.throws(() => materialFor('zz', 'c', nodes), /not in the layup/)
})
