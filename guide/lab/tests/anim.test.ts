import test from 'node:test'
import assert from 'node:assert/strict'
import { plyPhase, partPhase, isWet, ROLL, WET, CURE, DONE_T, PLY_TIME, type PhaseInput } from '../src/logic/anim'
import { visibleSet, type MeshInfo } from '../src/logic/build'
import type { GraphLite, Op } from '../src/logic/graph'

// a: core (no plies). b: 3 plies. c: 2 plies. d: 1 ply.
const op = (id: string, components: string[]): Op => ({ id, chapter: 30, title: id, summary: '', variants: ['roncz'], components })
const G: GraphLite = { order: ['a', 'b', 'c', 'd'], ops: [op('a', ['core']), op('b', ['skin']), op('c', ['web']), op('d', ['cap'])] }
const PLIES = { a: 0, b: 3, c: 2, d: 1 } as const
const OPS = ['a', 'b', 'c', 'd'] as const
const meshes: MeshInfo[] = [{ name: 'core', component: 'core', ply: null }]
for (const [o, comp] of [['b', 'skin'], ['c', 'web'], ['d', 'cap']] as const) for (let k = 1; k <= PLIES[o]; k++) meshes.push({ name: `${comp}.p${k}`, component: comp, ply: { op: o, order: k } })

const base = (over: Partial<PhaseInput>): PhaseInput => ({ meshOpIndex: 1, curOpIndex: 1, order: 1, lay: 1, count: 3, t: 0, ...over })

test('the last ply of the previous op is cured, not wet, at lay 0 of the next op', () => {
  for (const t of [0, ROLL, PLY_TIME, DONE_T]) {
    const ph = plyPhase(base({ meshOpIndex: 1, curOpIndex: 2, order: 3, lay: 0, count: 2, t }))
    assert.deepEqual(ph, { state: 'built', unroll: 1, front: 1, cure: 1 })
    assert.equal(isWet(ph), false)
  }
})

test('lay boundary: order lay-1 is laid and wet, lay is unrolling dry, lay+1 is hidden or ghost', () => {
  const at = (order: number, t: number, ghost = false) => plyPhase(base({ order, lay: 2, count: 3, t, ghost }))
  for (const t of [0, ROLL, PLY_TIME]) {
    assert.deepEqual(at(1, t), { state: 'current', unroll: 1, front: 1, cure: 0 }) // laid, wet, however far t is
    assert.equal(at(3, t).state, 'hidden')
    assert.equal(at(3, t, true).state, 'ghost')
  }
  assert.deepEqual(at(2, 0), { state: 'current', unroll: 0, front: 0, cure: 0 }) // t=0: nothing rolled yet
  assert.deepEqual(at(2, ROLL), { state: 'current', unroll: 1, front: 0, cure: 0 }) // rolled, still dry
  assert.deepEqual(at(2, ROLL + WET), { state: 'current', unroll: 1, front: 1, cure: 0 }) // wet-out complete, not cured: lay < count
  const mid = at(2, ROLL * 0.5)
  assert.equal(mid.unroll, 0.5)
  assert.equal(mid.front, 0)
  assert.equal(at(2, ROLL + WET * 0.25).front, 0.25)
})

test('cure runs only when lay === count, after the last ply has rolled and wet out', () => {
  const at = (lay: number, order: number, t: number) => plyPhase(base({ order, lay, count: 3, t }))
  for (const t of [0, ROLL, PLY_TIME, DONE_T]) assert.equal(at(2, 1, t).cure, 0) // lay 2 of 3: everything stays wet
  assert.equal(at(3, 1, 0).cure, 0)
  assert.equal(at(3, 3, PLY_TIME).cure, 0)
  assert.equal(at(3, 1, PLY_TIME + CURE / 2).cure, 0.5) // every ply of the op cures together
  assert.equal(at(3, 3, PLY_TIME + CURE / 2).cure, 0.5)
  assert.equal(at(3, 1, DONE_T).cure, 1)
  assert.equal(isWet(at(3, 1, DONE_T)), false)
  assert.equal(isWet(at(3, 1, PLY_TIME)), true)
})

test('t is clamped: below zero is 0, past the end is settled, NaN settles', () => {
  const a = plyPhase(base({ order: 3, lay: 3, count: 3 }))
  assert.deepEqual(plyPhase(base({ order: 3, lay: 3, count: 3, t: -5 })), a)
  assert.deepEqual(plyPhase(base({ order: 3, lay: 3, count: 3, t: DONE_T + 100 })), plyPhase(base({ order: 3, lay: 3, count: 3, t: DONE_T })))
  assert.deepEqual(plyPhase(base({ order: 3, lay: 3, count: 3, t: NaN })), plyPhase(base({ order: 3, lay: 3, count: 3, t: DONE_T })))
})

test('a ply of a later op or an op outside the variant never animates', () => {
  assert.equal(plyPhase(base({ meshOpIndex: 2, curOpIndex: 1, order: 1, lay: 3 })).state, 'hidden')
  assert.equal(plyPhase(base({ meshOpIndex: 2, curOpIndex: 1, order: 1, lay: 3, ghost: true })).state, 'ghost')
  assert.equal(plyPhase(base({ meshOpIndex: undefined })).state, 'hidden')
})

test('a part follows its state and is always cured', () => {
  assert.deepEqual(partPhase('built'), { state: 'built', unroll: 1, front: 1, cure: 1 })
  assert.equal(isWet(partPhase('current')), false)
})

test('sweep: every op, lay and t agrees with visibleSet, and wet only ever shows on the current op', () => {
  const idx = new Map(OPS.map((o, i) => [o, i]))
  const info = new Map(meshes.map((m) => [m.name, m]))
  for (const ghost of [false, true]) {
    const g = { ...G, __ghost: ghost }
    for (const cur of OPS) {
      const count = PLIES[cur]
      for (let lay = 0; lay <= count; lay++) {
        const st = visibleSet(g, 'roncz', cur, lay, meshes)
        for (let t = -0.5; t <= DONE_T + 1; t += 0.1) {
          for (const [name, s] of st) {
            const m = info.get(name)!
            if (!m.ply) continue
            const ph = plyPhase({ meshOpIndex: idx.get(m.ply.op as (typeof OPS)[number]), curOpIndex: idx.get(cur)!, order: m.ply.order, lay, count, t, ghost })
            const where = `${name} @ ${cur} lay ${lay} t ${t.toFixed(2)}`
            assert.equal(ph.state, s, `state disagrees with visibleSet: ${where}`)
            if (isWet(ph)) assert.equal(m.ply.op, cur, `wet outside the current op: ${where}`)
            if (m.ply.op !== cur && s === 'built') assert.deepEqual(ph, { state: 'built', unroll: 1, front: 1, cure: 1 }, where)
            if (s === 'hidden') assert.equal(isWet(ph), false, where)
            for (const v of [ph.unroll, ph.front, ph.cure]) assert.ok(v >= 0 && v <= 1, where)
          }
        }
      }
    }
  }
})
