import test from 'node:test'
import assert from 'node:assert/strict'
import { orientation, TURNOVER_OP } from '../src/logic/pose'
import type { GraphLite, Op } from '../src/logic/graph'

const op = (id: string, variants: string[]): Op => ({ id, chapter: 30, title: id, summary: '', variants })
const g: GraphLite = {
  ops: [op('r30.a', ['roncz']), op('r30.bottom-skin', ['roncz']), op(TURNOVER_OP, ['roncz']), op('r30.top-skin', ['roncz']), op('c10.x', ['gu'])],
  order: ['c10.x', 'r30.a', 'r30.bottom-skin', TURNOVER_OP, 'r30.top-skin'],
}

test('Roncz ops before the turnover op are inverted', () => {
  assert.equal(orientation(g, 'roncz', 'r30.a'), 'inverted')
  assert.equal(orientation(g, 'roncz', 'r30.bottom-skin'), 'inverted')
})
test('the turnover op itself and later ops are upright', () => {
  assert.equal(orientation(g, 'roncz', TURNOVER_OP), 'upright')
  assert.equal(orientation(g, 'roncz', 'r30.top-skin'), 'upright')
})
test('GU, no selection, unknown ops, and a variant without the turnover op are upright', () => {
  assert.equal(orientation(g, 'gu', 'c10.x'), 'upright')
  assert.equal(orientation(g, 'gu', 'r30.a'), 'upright')
  assert.equal(orientation(g, 'roncz', null), 'upright')
  assert.equal(orientation(g, 'roncz', 'nope'), 'upright')
  const noTurn: GraphLite = { ops: [op('r30.a', ['roncz'])], order: ['r30.a'] }
  assert.equal(orientation(noTurn, 'roncz', 'r30.a'), 'upright')
})
