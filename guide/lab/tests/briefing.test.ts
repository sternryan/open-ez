import test from 'node:test'
import assert from 'node:assert/strict'
import type { DecisionRecord, Option } from '../src/hangar/model'
import type { State } from '../src/hangar/briefingState'
import { linesFromTurns, renderBriefingHtml } from '../src/hangar/briefing'

function rec(over: Partial<DecisionRecord> = {}): DecisionRecord {
  return {
    id: 'powerplant-fuel-resin',
    spot: 'mod-ez',
    title: 'Powerplant, fuel and tank resin',
    status: 'open',
    question: 'Which engine, on which fuel, and with which tank resin?',
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

function base(over: Partial<State> = {}): State {
  return {
    recordId: 'powerplant-fuel-resin',
    mode: 'read-only',
    status: 'open',
    transcript: [],
    error: null,
    busy: false,
    decideEnabled: true,
    ...over,
  }
}

const ulOption: Option = {
  id: 'ul350i',
  label: 'UL350i',
  kind: 'candidate',
  facts: [{ text: '118 hp', cite: 'ulpower-ul350i:p1' }],
  why: 'lighter',
}

test('read-only render has no live controls and shows awaiting briefing', () => {
  const html = renderBriefingHtml(
    rec({
      status: 'open',
      options: [ulOption],
      positions: [
        { role: 'propulsion', option: 'ul350i', confidence: 'high', reasoning: 'lighter', citations: [], judgment: false },
        { role: 'structures', option: 'ul350i', confidence: 'high', reasoning: 'mogas', citations: [], judgment: false },
        { role: 'fuel-systems', option: 'rotax-912is', confidence: 'low', reasoning: 'burns less', citations: [], judgment: false },
      ],
      unknowns: [{ text: 'ethanol limit', how: 'ask the maker' }],
    }),
    'read-only',
    base(),
  )
  assert.equal(html.includes('data-test="chat"'), false)
  assert.equal(html.includes('data-test="decide"'), false)
  assert.equal(html.includes('data-test="reopen"'), false)
  assert.match(html, /data-test="recommendation"/)
  assert.match(html, /awaiting briefing/)
  assert.match(html, /ul350i/)
  assert.match(html, /lighter/)
  assert.match(html, /high/)
  assert.match(html, /burns less/)
  assert.match(html, /ethanol limit/)

  const reopened = renderBriefingHtml(rec({ status: 'reopened' }), 'read-only', base({ status: 'reopened' }))
  assert.match(reopened, /awaiting briefing/)
  assert.equal(reopened.includes('data-test="chat"'), false)
  assert.equal(reopened.includes('data-test="decide"'), false)
  assert.equal(reopened.includes('data-test="reopen"'), false)
})

test('live render has chat, decide, and reopen', () => {
  const html = renderBriefingHtml(
    rec({ options: [ulOption] }),
    'live',
    base({
      mode: 'live',
      transcript: [{ who: 'owner', text: 'why <i>this</i> resin' }],
      error: 'council <b>unavailable</b>',
    }),
  )
  assert.match(html, /data-test="chat"/)
  assert.match(html, /data-test="decide"/)
  assert.match(html, /data-test="reopen"/)
  const decideAt = html.indexOf('data-test="decide"')
  const reopenAt = html.indexOf('data-test="reopen"')
  assert.ok(decideAt >= 0 && reopenAt > decideAt)
  const decide = html.slice(decideAt, reopenAt)
  assert.match(decide, /<select\b/)
  assert.match(decide, /required/)
  assert.match(decide, /name="reason"/)
  assert.match(html, /why &lt;i&gt;this&lt;\/i&gt; resin/)
  assert.match(html, /council &lt;b&gt;unavailable&lt;\/b&gt;/)
  assert.equal(html.includes('<i>'), false)
  assert.equal(html.includes('<b>'), false)
})

test('a record title containing script is escaped', () => {
  const html = renderBriefingHtml(
    rec({
      title: '<script>alert(1)</script>',
      question: '<script>q</script>',
      book_choice: { text: '<script>book</script>', cite: '<script>cite</script>' },
      options: [
        {
          id: 'x',
          label: '<script>label</script>',
          kind: 'book',
          facts: [{ text: '<script>fact</script>', cite: 'om-1980:p4', flag: '<script>flag</script>' }],
          why: '<script>why</script>',
        },
      ],
      mission_score: {
        x: { worst_flag: '<script>score</script>', assumptions: ['<script>assume</script>'] },
      },
    }),
    'read-only',
    base(),
  )
  assert.equal(html.includes('<script'), false)
  assert.match(html, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;q&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;book&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;cite&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;label&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;fact&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;flag&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;why&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;score&lt;\/script&gt;/)
  assert.match(html, /&lt;script&gt;assume&lt;\/script&gt;/)
})

test('decided record shows decided in briefing 1', () => {
  const html = renderBriefingHtml(
    rec({
      status: 'decided',
      history: [{ date: '2026-10-20', from: 'open', to: 'decided', reason: 'settled' }],
    }),
    'read-only',
    base({ status: 'decided', decideEnabled: false }),
  )
  assert.match(html, /decided in briefing 1/)
  assert.equal(html.includes('data-test="decide"'), false)
})

test('a decided live room keeps decide in the page and disables it', () => {
  const html = renderBriefingHtml(
    rec({
      status: 'decided',
      options: [ulOption],
      history: [{ date: '2026-10-20', from: 'open', to: 'decided', reason: 'settled' }],
    }),
    'live',
    base({ mode: 'live', status: 'decided', decideEnabled: false }),
  )
  assert.match(html, /decided in briefing 1/)
  const decideAt = html.indexOf('data-test="decide"')
  const reopenAt = html.indexOf('data-test="reopen"')
  assert.ok(decideAt >= 0 && reopenAt > decideAt)
  assert.match(html.slice(decideAt, reopenAt), /\bdisabled\b/)
})

test('backbone lists options, the book choice, and mission-score flags', () => {
  const html = renderBriefingHtml(
    rec({
      book_choice: { text: 'the book engine', cite: 'om-1980:p15' },
      options: [
        {
          id: 'o235-book',
          label: 'Lycoming O-235',
          kind: 'book',
          facts: [{ text: '243 lb dry', cite: 'tcds-e223:p7' }, { text: 'ethanol limit', flag: 'unknown' }],
          why: 'baseline',
        },
      ],
      mission_score: {
        'o235-book': {
          empty_lb: { v: 730, flag: 'sourced', note: '' },
          worst_flag: 'derived',
          assumptions: ['book engine arm'],
          in_envelope: true,
        },
      },
    }),
    'read-only',
    base(),
  )
  assert.match(html, /<details\b/)
  assert.match(html, /Backbone/)
  assert.match(html, /the book engine/)
  assert.match(html, /om-1980:p15/)
  assert.match(html, /243 lb dry/)
  assert.match(html, /tcds-e223:p7/)
  assert.match(html, /ethanol limit/)
  assert.match(html, /unknown/)
  assert.match(html, /sourced/)
  assert.match(html, /derived/)
  assert.match(html, /book engine arm/)
})

test('linesFromTurns reads the server transcript shape and shows council errors', () => {
  const lines = linesFromTurns([
    { ts: 't', message: 'hi', reply: { reply_text: 'view', positions: [], unknowns: [], error: null } },
    { ts: 't', message: 'again', reply: { reply_text: '', positions: [], unknowns: [], error: 'council call failed: TimeoutError' } },
  ])
  assert.deepEqual(lines, [
    { who: 'owner', text: 'hi' },
    { who: 'council', text: 'view' },
    { who: 'owner', text: 'again' },
    { who: 'error', text: 'council call failed: TimeoutError' },
  ])
})
