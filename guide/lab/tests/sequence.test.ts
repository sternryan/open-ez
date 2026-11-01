import test from 'node:test'
import assert from 'node:assert/strict'
import type { GraphLite, Op, PlanJson } from '../src/logic/graph'
import { CANARD_GROUP, GU_NOTE, buildSequence, noteFor, toPlanSteps } from '../src/logic/sequence'

const op = (p: Partial<Op> & Pick<Op, 'id' | 'variants'>): Op => ({
  chapter: 4,
  title: p.id,
  summary: '',
  components: [],
  ...p,
})

const groups = [
  { id: 'bulkheads-firewall', label: 'Seat bulkheads and firewall' },
  { id: 'empty-group', label: 'Empty' },
  { id: 'fuselage-sides', label: 'Fuselage sides' },
  { id: 'nose', label: 'Nose' },
  { id: CANARD_GROUP, label: 'Canard' },
]

const fullPlan: PlanJson = {
  people: 2,
  people_why: 'draping the skin',
  hours: { value: 3, flag: 'community', source: 'https://example.com/a' },
  cure: 'part',
  resin: 'mgs-285-287',
  tools: ['squeegee'],
  buy: [{ item: 'bid-7725', qty: 4.5, flag: 'estimate' }],
}

const graph: GraphLite = {
  ops: [
    op({ id: 'canard.second', variants: ['roncz'], group: CANARD_GROUP, requires: ['canard.first'] }),
    op({ id: 'gu.only', chapter: 10, variants: ['gu'], group: CANARD_GROUP }),
    op({ id: 'stub.roncz', variants: ['roncz'], stub: true, group: 'bulkheads-firewall' }),
    op({ id: 'both.keep', variants: ['both'], group: 'bulkheads-firewall', requires: ['stub.roncz', 'gu.only'] }),
    op({ id: 'roncz.viaGu', variants: ['roncz'], group: 'bulkheads-firewall', requires: ['gu.only'], plan: fullPlan }),
    op({ id: 'ungrouped', variants: ['roncz'], group: null }),
    op({ id: 'other.group', variants: ['roncz'], group: 'wing' }),
    op({
      id: 'roncz.after',
      variants: ['roncz'],
      group: 'fuselage-sides',
      requires: ['roncz.viaGu', 'gu.only'],
      plan: { hours: { value: null, flag: 'unsourced' }, cure: 'none' },
    }),
    op({
      id: 'nose.canardish',
      chapter: 13,
      variants: ['roncz'],
      group: 'nose',
      components: ['f13.canard-attach-reinforce'],
      plan: { hours: { value: 0, flag: 'estimate' } },
    }),
    op({
      id: 'canard.first',
      chapter: 30,
      variants: ['roncz'],
      group: CANARD_GROUP,
      plan: { people: 2, people_why: 'the lift', hours: { value: 4, flag: 'estimate' }, cure: 'all', resin: 'mgs-285-287' },
    }),
  ],
  order: [
    'gu.only',
    'stub.roncz',
    'roncz.viaGu',
    'both.keep',
    'ungrouped',
    'other.group',
    'roncz.after',
    'nose.canardish',
    'canard.first',
    'canard.second',
  ],
}

test('GU_NOTE and CANARD_GROUP are the single canard asterisk', () => {
  assert.equal(GU_NOTE, 'The 1980 plans built the GU canard. This build uses the Roncz.')
  assert.equal(CANARD_GROUP, 'canard')
})

test('buildSequence drops GU ops and stubs and keeps every Roncz step', () => {
  const seq = buildSequence(graph, groups)
  const ids = seq.flatMap((g) => g.steps.map((s) => s.id))
  assert.deepEqual(ids, ['roncz.viaGu', 'both.keep', 'roncz.after', 'nose.canardish', 'canard.first', 'canard.second'])
  assert.deepEqual(seq.map((g) => ({ id: g.id, label: g.label, n: g.steps.length })), [
    { id: 'bulkheads-firewall', label: 'Seat bulkheads and firewall', n: 2 },
    { id: 'empty-group', label: 'Empty', n: 0 },
    { id: 'fuselage-sides', label: 'Fuselage sides', n: 1 },
    { id: 'nose', label: 'Nose', n: 1 },
    { id: CANARD_GROUP, label: 'Canard', n: 2 },
  ])
  const via = seq[0].steps[0]
  assert.equal(via.plan?.hours?.value, 3)
  assert.equal(via.plan?.hours?.flag, 'community')
})

test('every Roncz step stays reachable and after the prerequisites that survived', () => {
  const seq = buildSequence(graph, groups)
  const ids = seq.flatMap((g) => g.steps.map((s) => s.id))
  const present = new Set(ids)
  assert.equal(present.has('gu.only'), false)
  assert.equal(present.has('stub.roncz'), false)
  assert.equal(present.has('roncz.viaGu'), true)
  for (const step of seq.flatMap((g) => g.steps)) {
    for (const req of step.requires ?? []) {
      if (!present.has(req)) continue
      assert.ok(ids.indexOf(req) < ids.indexOf(step.id), `${req} before ${step.id}`)
    }
  }
})

test('group buckets follow the groups list and graph order, and repeat', () => {
  const once = buildSequence(graph, groups)
  const twice = buildSequence(graph, groups)
  assert.deepEqual(once, twice)
  assert.deepEqual(once[0].steps.map((s) => s.id), ['roncz.viaGu', 'both.keep'])
  assert.deepEqual(once[1].steps, [])
  assert.deepEqual(once[4].steps.map((s) => s.id), ['canard.first', 'canard.second'])
})

test('the GU note is on the first canard-group step and nowhere else', () => {
  const seq = buildSequence(graph, groups)
  const notes = seq.flatMap((g) => g.steps.map((s) => noteFor(seq, s.id)))
  assert.deepEqual(notes.filter((n) => n !== null), [GU_NOTE])
  assert.equal(noteFor(seq, 'canard.first'), GU_NOTE)
  assert.equal(noteFor(seq, 'canard.second'), null)
  assert.equal(noteFor(seq, 'both.keep'), null)
  assert.equal(noteFor(seq, 'nose.canardish'), null)
  assert.equal(noteFor(seq, 'missing'), null)
  assert.equal(noteFor([{ id: CANARD_GROUP, label: 'Canard', steps: [] }], 'canard.first'), null)
})

test('toPlanSteps maps a missing plan to the defaults and keeps a zero hour', () => {
  const steps = toPlanSteps(buildSequence(graph, groups))
  assert.deepEqual(steps, [
    { id: 'roncz.viaGu', group: 'bulkheads-firewall', hours: 3, people: 2, cure: 'part', resin: 'mgs-285-287' },
    { id: 'both.keep', group: 'bulkheads-firewall', hours: null, people: 1, cure: 'none', resin: null },
    { id: 'roncz.after', group: 'fuselage-sides', hours: null, people: 1, cure: 'none', resin: null },
    { id: 'nose.canardish', group: 'nose', hours: 0, people: 1, cure: 'none', resin: null },
    { id: 'canard.first', group: CANARD_GROUP, hours: 4, people: 2, cure: 'all', resin: 'mgs-285-287' },
    { id: 'canard.second', group: CANARD_GROUP, hours: null, people: 1, cure: 'none', resin: null },
  ])
})
