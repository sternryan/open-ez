import test from 'node:test'
import assert from 'node:assert/strict'
import { skin, statusLabel, type DecisionRecord, type Position, type Spot } from '../src/hangar/model'
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

function pos(role: string, option: string, reasoning: string, confidence: string): Position {
  return { role, option, confidence, reasoning, citations: [], judgment: false }
}

test('statusLabel: open and reopened await a briefing; a first decision is briefing 1', () => {
  assert.equal(statusLabel(rec({ status: 'open' })), 'awaiting briefing')
  assert.equal(statusLabel(rec({ status: 'reopened' })), 'awaiting briefing')
  assert.equal(
    statusLabel(rec({
      status: 'decided',
      history: [{ date: '2026-10-20', from: 'open', to: 'decided', reason: 'settled' }],
    })),
    'decided in briefing 1',
  )
})

test('statusLabel counts the last decided entry among decided entries ordered by date', () => {
  assert.equal(
    statusLabel(rec({
      status: 'decided',
      history: [
        { date: '2026-10-20', from: 'open', to: 'decided', reason: 'first close' },
        { date: '2026-10-21', from: 'decided', to: 'reopened', reason: 'new data' },
        { date: '2026-10-22', from: 'reopened', to: 'decided', reason: 'settled' },
      ],
    })),
    'decided in briefing 2',
  )
})

test('skin recommends the majority option and keeps the dissent', () => {
  const s = skin(rec({
    positions: [
      pos('fuel-systems', 'rotax-912is', '912 iS burns less fuel on the published flow', 'low'),
      pos('propulsion', 'ul350i', 'lighter', 'high'),
      pos('structures', 'ul350i', 'mogas', 'high'),
    ],
  }))
  assert.equal(s.recommendation, 'ul350i')
  assert.equal(s.confidence, 'high')
  assert.ok(s.why && s.why.includes('lighter'))
  assert.deepEqual(s.disagreements, ['912 iS burns less fuel on the published flow'])
})

test('skin with no positions is empty', () => {
  assert.deepEqual(skin(rec()), {
    recommendation: null,
    why: null,
    confidence: null,
    disagreements: [],
    unknowns: [],
  })
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
