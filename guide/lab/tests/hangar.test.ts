import test from 'node:test'
import assert from 'node:assert/strict'
import { skin, statusLabel, type DecisionRecord, type HangarData, type Position, type Spot } from '../src/hangar/model'
import { renderHangarHtml } from '../src/hangar/index'

function rec(over: Partial<DecisionRecord> = {}): DecisionRecord {
  return {
    id: 'powerplant-fuel-resin',
    spot: 'mod-ez',
    title: 'Powerplant, fuel and tank resin',
    status: 'open',
    question: 'Which powerplant and fuel?',
    coupled_with: [],
    replaces: [],
    book_choice: {},
    axes: [],
    options: [],
    positions: [],
    unknowns: [],
    mission_score: null,
    decision: null,
    history: [],
    changes: null,
    evidence: { paper: 'none', material: 'none', outside_review: 'none', flight: 'none' },
    ...over,
  }
}

function pos(
  role: string,
  picks: Record<string, string>,
  reasoning: string,
  confidence: string,
  judgment = false,
): Position {
  return { role, picks, confidence, reasoning, citations: [], judgment }
}

test('statusLabel: open and reopened await a briefing; a first decision is briefing 1', () => {
  assert.equal(statusLabel(rec({ status: 'open' })), 'awaiting briefing')
  assert.equal(statusLabel(rec({ status: 'reopened' })), 'awaiting briefing')
  assert.equal(
    statusLabel(rec({
      status: 'decided',
      history: [{ date: '2026-10-20', from: 'open', to: 'decided', reason: 'settled', picks: { engine: 'ul350i' } }],
    })),
    'decided in briefing 1',
  )
})

test('statusLabel counts the last decided entry among decided entries ordered by date', () => {
  assert.equal(
    statusLabel(rec({
      status: 'decided',
      history: [
        { date: '2026-10-20', from: 'open', to: 'decided', reason: 'first close', picks: { engine: 'a' } },
        { date: '2026-10-21', from: 'decided', to: 'reopened', reason: 'new data' },
        { date: '2026-10-22', from: 'reopened', to: 'decided', reason: 'settled', picks: { engine: 'b' } },
      ],
    })),
    'decided in briefing 2',
  )
})

test('skin recommends the majority option and keeps the dissent', () => {
  const s = skin(rec({
    axes: [{ id: 'engine', options: ['ul350i', 'rotax-912is'] }],
    positions: [
      pos('fuel-systems', { engine: 'rotax-912is' }, '912 iS burns less fuel on the published flow', 'low'),
      pos('propulsion', { engine: 'ul350i' }, 'lighter', 'high'),
      pos('structures', { engine: 'ul350i' }, 'mogas', 'high'),
    ],
  }))
  assert.equal(s.recommendation, 'ul350i')
  assert.deepEqual(s.recommendations, { engine: 'ul350i' })
  assert.equal(s.confidence, 'high')
  assert.ok(s.why && s.why.includes('lighter'))
  assert.deepEqual(s.disagreements, ['912 iS burns less fuel on the published flow'])
})

test('skin with no positions is empty', () => {
  assert.deepEqual(skin(rec()), {
    recommendation: null,
    recommendations: {},
    why: null,
    confidence: null,
    disagreements: [],
    unknowns: [],
  })
})

test('skin: per-axis majority joins winning picks and keeps dissent on each axis', () => {
  const s = skin(rec({
    axes: [
      { id: 'engine', options: ['ul350i', 'rotax-912is'] },
      { id: 'fuel_path', options: ['mogas-e10', 'ul94-ethanol-free'] },
    ],
    positions: [
      pos('propulsion', { engine: 'ul350i', fuel_path: 'mogas-e10' }, 'both modern', 'high'),
      pos('structures', { engine: 'ul350i', fuel_path: 'ul94-ethanol-free' }, 'lighter engine', 'medium', true),
      pos('fuel-systems', { engine: 'rotax-912is', fuel_path: 'mogas-e10' }, 'published flow', 'low'),
    ],
  }))
  assert.deepEqual(s.recommendations, { engine: 'ul350i', fuel_path: 'mogas-e10' })
  assert.equal(s.recommendation, 'ul350i + mogas-e10')
  assert.equal(s.why, 'both modern (judgment) lighter engine published flow')
  assert.equal(s.confidence, 'low')
  assert.deepEqual(s.disagreements, ['(judgment) lighter engine', 'published flow'])
})

test('skin: a tie on one axis leaves that axis unset and keeps the other', () => {
  const s = skin(rec({
    axes: [
      { id: 'engine', options: ['a', 'b'] },
      { id: 'fuel_path', options: ['f1', 'f2'] },
    ],
    positions: [
      pos('propulsion', { engine: 'a', fuel_path: 'f1' }, 'one', 'high'),
      pos('structures', { engine: 'a', fuel_path: 'f2' }, 'two', 'low'),
      pos('fuel-systems', { engine: 'a', fuel_path: 'f1' }, 'three', 'medium'),
      pos('historian', { engine: 'b', fuel_path: 'f2' }, 'four', 'high'),
    ],
  }))
  assert.deepEqual(s.recommendations, { engine: 'a', fuel_path: null })
  assert.equal(s.recommendation, 'a')
  assert.equal(s.why, 'one two three')
  assert.equal(s.confidence, 'low')
  assert.deepEqual(s.disagreements, ['four'])
})

test('skin: partial picks vote only on the axes a position named', () => {
  const s = skin(rec({
    axes: [
      { id: 'engine', options: ['a', 'b'] },
      { id: 'fuel_path', options: ['f1', 'f2'] },
    ],
    positions: [
      pos('propulsion', { engine: 'a' }, 'engine only', 'high'),
      pos('structures', { engine: 'a', fuel_path: 'f1' }, 'both', 'medium'),
      pos('fuel-systems', { fuel_path: 'f1' }, 'fuel only', 'low'),
      pos('historian', { engine: 'b' }, 'not a', 'high'),
    ],
  }))
  assert.deepEqual(s.recommendations, { engine: 'a', fuel_path: 'f1' })
  assert.equal(s.recommendation, 'a + f1')
  assert.equal(s.why, 'engine only both fuel only')
  assert.equal(s.confidence, 'low')
  assert.deepEqual(s.disagreements, ['not a'])
})

const spots: Spot[] = [
  { id: 'long-ez-1980', label: 'Long-EZ', analogue: 'book build', state: 'foundation', blurb: 'The book airplane.' },
  { id: 'mod-ez', label: 'Mod-EZ', analogue: 'restomod', state: 'active', blurb: 'The modern airplane.' },
  { id: 'rv-12', label: 'RV-12', analogue: 'kit', state: 'reserved', blurb: 'A reserved spot for a kit airplane.' },
  { id: 'model-1', label: 'Model 1', analogue: 'scratch build', state: 'reserved', blurb: 'A reserved spot for an original design.' },
]

test('renderHangarHtml draws four spots, reserved marks, a briefing link, and escaped text', () => {
  const html = renderHangarHtml({
    spots,
    records: {
      'powerplant-fuel-resin': rec({ title: '<script>alert(1)</script>', status: 'open' }),
    },
  })
  const ids = [...html.matchAll(/data-spot="([^"]*)"/g)].map((m) => m[1])
  assert.deepEqual(ids, ['long-ez-1980', 'mod-ez', 'rv-12', 'model-1'])
  assert.equal((html.match(/<article\b/g) ?? []).length, 4)
  assert.equal((html.match(/Reserved/g) ?? []).length, 2)
  assert.match(html, /A reserved spot for a kit airplane\./)
  assert.match(html, /A reserved spot for an original design\./)
  assert.match(html, /href="\.\/"/)
  assert.match(html, /href="briefing\.html#powerplant-fuel-resin"/)
  assert.match(html, /awaiting briefing/)
  assert.equal(html.includes('<script'), false)
  assert.match(html, /&lt;script&gt;/)
})

test('statusLabel counts the briefings that closed the record', () => {
  const r = {
    id: 'x', title: 't', status: 'decided',
    history: [
      { date: '2026-10-20', from: 'open', to: 'decided', reason: 'a', picks: { engine: 'a' } },
      { date: '2026-10-21', from: 'decided', to: 'reopened', reason: 'b' },
      { date: '2026-10-22', from: 'reopened', to: 'decided', reason: 'c', picks: { engine: 'b' } },
    ],
  } as unknown as DecisionRecord
  assert.equal(statusLabel(r), 'decided in briefing 2')
})

test('skin: a tied council shows every position as dissent and recommends nothing', () => {
  const r = {
    id: 'x', title: 't', status: 'open', unknowns: ['bare string unknown', { text: 'ethanol limit', how: 'ask' }],
    axes: [{ id: 'engine', options: ['a', 'b'] }],
    positions: [
      { role: 'propulsion', picks: { engine: 'a' }, confidence: 'high', reasoning: 'for a', citations: [], judgment: false },
      { role: 'structures', picks: { engine: 'b' }, confidence: 'low', reasoning: 'for b', citations: [], judgment: false },
    ],
  } as unknown as DecisionRecord
  const s = skin(r)
  assert.equal(s.recommendation, null)
  assert.deepEqual(s.recommendations, { engine: null })
  assert.equal(s.why, null)
  assert.equal(s.confidence, null)
  assert.deepEqual(s.disagreements, ['for a', 'for b'])
  assert.deepEqual(s.unknowns, ['bare string unknown', 'ethanol limit — ask'])
})

test('renderHangarHtml survives a spot with a missing blurb and encodes the record id', () => {
  const data = {
    spots: [{ id: 'mod-ez', label: 'Mod-EZ', analogue: 'restomod', state: 'active' }],
    records: { 'a b': { id: 'a b', spot: 'mod-ez', title: 'T', status: 'open', history: [] } },
  } as unknown as HangarData
  const html = renderHangarHtml(data)
  assert.ok(html.includes('briefing.html#a%20b'))
})

test('skin labels an advisor judgment as judgment', () => {
  const r = {
    id: 'x', title: 't', status: 'open',
    axes: [{ id: 'engine', options: ['a', 'b'] }],
    positions: [
      { role: 'propulsion', picks: { engine: 'a' }, confidence: 'high', reasoning: 'I prefer a', citations: ['om-1980:p4'], judgment: true },
      { role: 'historian', picks: { engine: 'a' }, confidence: 'high', reasoning: 'the book did a', citations: ['om-1980:p4'], judgment: false },
      { role: 'structures', picks: { engine: 'b' }, confidence: 'low', reasoning: 'b is heavier', citations: [], judgment: false },
    ],
  } as unknown as DecisionRecord
  const s = skin(r)
  assert.equal(s.recommendation, 'a')
  assert.equal(s.why, '(judgment) I prefer a the book did a')
  assert.deepEqual(s.disagreements, ['b is heavier'])
})
