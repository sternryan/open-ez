import test from 'node:test'
import assert from 'node:assert/strict'
import { barOps, makeStore, visibleOps, type GraphLite, type Op } from '../src/logic/graph'

const op = (id: string, chapter: number, variants: string[], stub = false): Op => ({ id, chapter, title: id, summary: '', variants, stub, components: [] })
const g: GraphLite = {
  ops: [op('ref', 0, ['both'], true), op('c10.a', 10, ['gu']), op('c11.s', 11, ['gu'], true), op('r30.a', 30, ['roncz']), op('r30.b', 30, ['roncz']), op('c03', 3, ['both'])],
  order: ['ref', 'c03', 'c10.a', 'c11.s', 'r30.a', 'r30.b'],
}

test('visibleOps keeps graph order and both-variant ops', () => {
  assert.deepEqual(visibleOps(g, 'roncz').map((o) => o.id), ['ref', 'c03', 'r30.a', 'r30.b'])
  assert.deepEqual(visibleOps(g, 'gu').map((o) => o.id), ['ref', 'c03', 'c10.a', 'c11.s'])
})

test('barOps drops reference chapters and stubs', () => {
  assert.deepEqual(barOps(g, 'roncz').map((o) => o.id), ['r30.a', 'r30.b'])
  assert.deepEqual(barOps(g, 'gu').map((o) => o.id), ['c10.a'])
})

test('barOps leaves out the fuselage chapters', () => {
  const f: GraphLite = { ops: [op('f04.a', 4, ['both']), op('f05.a', 5, ['both']), op('f06.a', 6, ['both']), ...g.ops], order: ['f04.a', 'f05.a', 'f06.a', ...g.order] }
  assert.deepEqual(barOps(f, 'roncz').map((o) => o.id), ['r30.a', 'r30.b'])
})

test('barOps leaves out chapters 7-9 until the lab adds them', () => {
  const f: GraphLite = { ops: [op('f07.a', 7, ['both']), op('f08.a', 8, ['both']), op('f09.a', 9, ['both']), ...g.ops], order: ['f07.a', 'f08.a', 'f09.a', ...g.order] }
  assert.deepEqual(barOps(f, 'roncz').map((o) => o.id), ['r30.a', 'r30.b'])
  assert.deepEqual(barOps(f, 'gu').map((o) => o.id), ['c10.a'])
})

test('barOps leaves out chapter 13 (nose) and chapter 12 (the canard installed, the fuselage subject\'s)', () => {
  const f: GraphLite = { ops: [op('f13.a', 13, ['both']), op('r30.i', 12, ['roncz']), op('c12.i', 12, ['gu']), ...g.ops], order: ['f13.a', 'r30.i', 'c12.i', ...g.order] }
  assert.deepEqual(barOps(f, 'roncz').map((o) => o.id), ['r30.a', 'r30.b'])
  assert.deepEqual(barOps(f, 'gu').map((o) => o.id), ['c10.a'])
})

test('barOps keeps chapter 11 (the elevators) on the canard bar, after the chapter 30 ops they follow, in graph order', () => {
  const f: GraphLite = { ops: [...g.ops, op('r30.elev-a', 11, ['roncz']), op('r30.elev-b', 11, ['roncz']), op('r30.install', 30, ['roncz']), op('r30.drill', 12, ['roncz'])],
    order: [...g.order, 'r30.elev-a', 'r30.elev-b', 'r30.install', 'r30.drill'] }
  assert.deepEqual(barOps(f, 'roncz').map((o) => o.id), ['r30.a', 'r30.b', 'r30.elev-a', 'r30.elev-b', 'r30.install'])
})

test('makeStore toggles, and survives storage that throws', () => {
  const mem = new Map<string, string>()
  const ok = makeStore({ getItem: (k) => mem.get(k) ?? null, setItem: (k, v) => { mem.set(k, v) } })
  ok.toggle('x', 1)
  assert.deepEqual([...makeStore({ getItem: (k) => mem.get(k) ?? null, setItem: () => {} }).get('x')], [1])
  const bad = makeStore({ getItem: () => { throw new Error('no') }, setItem: () => { throw new Error('no') } })
  bad.toggle('y', 2)
  assert.ok(bad.get('y').has(2))
})

test('barOps leaves out chapters 14-17 (spar, firewall, controls, trim) until the lab adds them', () => {
  const f: GraphLite = { ops: [op('f14.a', 14, ['both']), op('f15.a', 15, ['both']), op('f16.a', 16, ['both']), op('f17.a', 17, ['both']), ...g.ops],
    order: ['f14.a', 'f15.a', 'f16.a', 'f17.a', ...g.order] }
  assert.deepEqual(barOps(f, 'roncz').map((o) => o.id), ['r30.a', 'r30.b'])
  assert.deepEqual(barOps(f, 'gu').map((o) => o.id), ['c10.a'])
})
