import test from 'node:test'
import assert from 'node:assert/strict'
import { barOps, makeStore, visibleOps, type GraphLite, type Op } from '../src/logic/graph'

const op = (id: string, chapter: number, variants: string[], stub = false): Op => ({ id, chapter, title: id, summary: '', variants, stub })
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

test('makeStore toggles, and survives storage that throws', () => {
  const mem = new Map<string, string>()
  const ok = makeStore({ getItem: (k) => mem.get(k) ?? null, setItem: (k, v) => { mem.set(k, v) } })
  ok.toggle('x', 1)
  assert.deepEqual([...makeStore({ getItem: (k) => mem.get(k) ?? null, setItem: () => {} }).get('x')], [1])
  const bad = makeStore({ getItem: () => { throw new Error('no') }, setItem: () => { throw new Error('no') } })
  bad.toggle('y', 2)
  assert.ok(bad.get('y').has(2))
})
