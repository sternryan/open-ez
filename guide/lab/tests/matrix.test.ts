import test from 'node:test'
import assert from 'node:assert/strict'
import type { DecisionRecord } from '../src/hangar/model'
import type { State } from '../src/hangar/briefingState'
import { buildDecidePayload, decideErrorMessage, decidePayloadFor, matrixLoadIsCurrent, renderBriefingHtml } from '../src/hangar/briefing'
import {
  MATRIX_POLL_CAP,
  asMatrixResponse,
  isSamePaint,
  needsPolling,
  openUnknownIds,
  renderMatrix,
  renderUnknowns,
  shouldPoll,
  type MatrixCell,
  type MatrixResponse,
  type MatrixUnknown,
} from '../src/hangar/matrixView'

function rec(over: Partial<DecisionRecord> = {}): DecisionRecord {
  return {
    id: 'cg-ballast',
    spot: 'mod-ez',
    title: 'Where the weight sits',
    status: 'open',
    question: 'Which loading change?',
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

function base(over: Partial<State> = {}): State {
  return {
    recordId: 'cg-ballast',
    mode: 'live',
    status: 'open',
    transcript: [],
    error: null,
    busy: false,
    decideEnabled: true,
    ...over,
  }
}

function cell(over: Partial<MatrixCell> = {}): MatrixCell {
  return {
    id: 'solo-120|none|mission|landing',
    occupancy: 'solo-120',
    occupancy_label: 'solo 120',
    bag: 'none',
    bag_label: 'no bag',
    fuel: 'mission',
    state: 'landing',
    fuel_lb: 20,
    gross_lb: 1100,
    cg_in: 104.2,
    fwd_margin_in: 2.77,
    aft_margin_in: -1.26,
    gross_margin_lb: -173.24,
    ok: false,
    flag: 'derived',
    loading: 'solo 120, no bag, mission, landing',
    ...over,
  }
}

function crossing(note: string, above: number | null = null, below: number | null = null) {
  return { fails_above_lb: above, fails_below_lb: below, note }
}

const record = rec({
  options: [
    { id: 'battery', label: 'Battery aft', kind: 'candidate', facts: [], why: '' },
    { id: 'arm', label: 'Engine arm', kind: 'candidate', facts: [], why: '' },
  ],
})

test('asMatrixResponse returns null for a non-object body', () => {
  for (const body of [null, undefined, 'matrix', 0, 4, true, [], () => undefined]) {
    assert.equal(asMatrixResponse(body), null, JSON.stringify(body))
  }
})

test('asMatrixResponse keeps a valid body and drops malformed options, cells, and unknowns', () => {
  const goodCell = cell({ loading: 'kept loading' })
  const parsed = asMatrixResponse({
    record_id: 'cg-1',
    options: [
      {
        option: 'battery',
        label: 'Battery aft',
        public: {
          engine: 'plant-a',
          cells: [goodCell, 'not-a-cell', null, { foo: 1 }, { id: 'bare' }],
          cell_count: 99,
          unknown_cells: 2,
          flag: 'derived',
          worst: { fwd: cell({ fwd_margin_in: 2.77, loading: 'fwd load' }), aft: 'nope', gross: null },
          crossings: { aft: crossing('binds light', null, 140), fwd: 'bad', gross: null },
        },
        private: null,
      },
      { option: 'missing-label', public: null },
      { label: 'No id', public: null },
      null,
      'nope',
      { option: 'bad-public', label: 'Bad', public: { cells: 'nope' }, private: null },
      { option: 'bad-private', label: 'Bad private', public: null, private: 5 },
    ],
    unknowns: [
      {
        id: 'u-coolant',
        text: 'coolant mass',
        how: 'weigh it',
        state: 'open',
        affects: ['battery', 3, null],
        job: { id: 'job-1', state: 'queued', error: null, proposal: null, spotcheck: null },
      },
      { id: 'u-nostate', text: 'missing state', how: 'look', affects: [] },
      { text: 'no id', state: 'open', how: 'look' },
      { id: 'u-banana', text: 'weird', state: 'banana', how: '' },
      null,
      'string-unknown',
    ],
  })
  assert.ok(parsed)
  assert.equal(parsed.record_id, 'cg-1')
  assert.equal(parsed.options.length, 1)
  assert.equal(parsed.options[0].option, 'battery')
  assert.equal(parsed.options[0].label, 'Battery aft')
  assert.equal(parsed.options[0].public?.engine, 'plant-a')
  assert.equal(parsed.options[0].public?.unknown_cells, 2)
  assert.deepEqual(
    parsed.options[0].public?.cells.map((c) => c.loading || c.id),
    ['kept loading', 'bare'],
  )
  assert.equal(parsed.options[0].public?.worst.fwd?.loading, 'fwd load')
  assert.equal(parsed.options[0].public?.worst.aft, null)
  assert.equal(parsed.options[0].public?.worst.gross, null)
  assert.equal(parsed.options[0].public?.crossings?.aft?.note, 'binds light')
  assert.equal(parsed.options[0].public?.crossings?.fwd, null)
  assert.equal(parsed.unknowns.length, 1)
  assert.equal(parsed.unknowns[0].id, 'u-coolant')
  assert.deepEqual(parsed.unknowns[0].affects, ['battery'])
  assert.equal(parsed.unknowns[0].job?.state, 'queued')
  assert.deepEqual(asMatrixResponse({ record_id: 7 }), { record_id: '', options: [], unknowns: [] })
})

test('a null text or how still parses and keeps the unknown id', () => {
  const parsed = asMatrixResponse({
    record_id: 'cg-1',
    options: [],
    unknowns: [
      { id: 'u-null', text: null, how: null, state: 'open', affects: ['battery'] },
      { id: 'u-missing', state: 'researching', affects: [] },
      { id: 'u-how-null', text: 'arm', how: null, state: 'open', affects: [] },
      { id: 'u-text-null', text: null, how: 'weigh it', state: 'researching', affects: [] },
      { id: 'u-bad', text: 4, how: 'look', state: 'open', affects: [] },
      { id: 'u-sourced', text: null, how: undefined, state: 'sourced', affects: [] },
    ],
  })
  assert.ok(parsed)
  assert.deepEqual(
    parsed.unknowns.map((item) => item.id),
    ['u-null', 'u-missing', 'u-how-null', 'u-text-null', 'u-sourced'],
  )
  assert.equal(parsed.unknowns[0].text, '')
  assert.equal(parsed.unknowns[0].how, '')
  assert.equal(parsed.unknowns[2].text, 'arm')
  assert.equal(parsed.unknowns[2].how, '')
  assert.equal(parsed.unknowns[3].text, '')
  assert.equal(parsed.unknowns[3].how, 'weigh it')
  assert.deepEqual(openUnknownIds(parsed), ['u-null', 'u-missing', 'u-how-null', 'u-text-null'])
  const html = renderUnknowns(record, parsed, true)
  assert.match(html, /data-unknown="u-null"/)
  assert.match(html, /data-unknown="u-how-null"/)
  const room = renderBriefingHtml(rec({ axes: [{ id: 'engine', options: ['battery'] }] }), 'live', base(), parsed)
  assert.match(room, /name="ack-unknowns"/)
  assert.match(room, /title="u-null, u-missing, u-how-null, u-text-null"/)
})

function sampleMatrix(): MatrixResponse {
  const fwd = cell({ id: 'fwd', fwd_margin_in: 2.77, aft_margin_in: 1.2, gross_margin_lb: 40, loading: 'fwd loading' })
  const aft = cell({
    id: 'aft',
    fwd_margin_in: 4,
    aft_margin_in: -1.26,
    gross_margin_lb: 10,
    loading: 'light pilot <script>alert(1)</script>',
  })
  const gross = cell({
    id: 'gross',
    fwd_margin_in: 1,
    aft_margin_in: 1,
    gross_margin_lb: -173.24,
    gross_lb: null,
    cg_in: null,
    loading: 'heavy pair',
  })
  return {
    record_id: 'cg-ballast',
    options: [
      {
        option: 'battery',
        label: 'Battery aft',
        public: {
          engine: 'plant-a',
          cells: [fwd, aft, gross],
          cell_count: 3,
          unknown_cells: 2,
          flag: 'derived',
          worst: { fwd, aft, gross },
          crossings: {
            fwd: crossing('   '),
            aft: crossing('aft limit binds below 140 lb', null, 140),
            gross: crossing(''),
          },
        },
        private: {
          engine: 'plant-a',
          cells: [],
          cell_count: 0,
          unknown_cells: 0,
          flag: 'derived',
          worst: {
            fwd: cell({ fwd_margin_in: 1.5, loading: 'Pat solo' }),
            aft: cell({ aft_margin_in: -0.4, loading: 'Sam solo' }),
            gross: null,
          },
          crossings: {
            fwd: crossing('SHOULD-NOT-SHOW'),
            aft: crossing('SHOULD-NOT-SHOW'),
            gross: crossing('SHOULD-NOT-SHOW'),
          },
        },
      },
      { option: 'none', label: 'No change', public: null, private: null },
      { option: 'broken', label: 'Broken effect', public: null, private: null, error: 'bad effect' },
    ],
    unknowns: [],
  }
}

test('an unscored option with no public matrix is not scored yet', () => {
  const parsed = asMatrixResponse({
    record_id: 'cg-1',
    options: [
      { option: 'bare', label: 'Bare candidate', public: null, private: null, unscored: true },
      { option: 'scored', label: 'Scored', public: null, unscored: false },
      { option: 'plain', label: 'Plain', public: null },
      { option: 'weird', label: 'Weird', public: null, unscored: 'yes' },
      {
        option: 'battery',
        label: 'Battery aft',
        unscored: true,
        public: {
          engine: 'plant-a',
          cells: [cell({ loading: 'kept loading' })],
          cell_count: 1,
          unknown_cells: 0,
          flag: 'derived',
          worst: { fwd: null, aft: null, gross: null },
          crossings: null,
        },
        private: null,
      },
    ],
    unknowns: [],
  })
  assert.ok(parsed)
  assert.equal(parsed.options[0].unscored, true)
  assert.equal(parsed.options[1].unscored, false)
  assert.equal(parsed.options[2].unscored, false)
  assert.equal(parsed.options[3].unscored, false)
  assert.equal(parsed.options[4].unscored, true)
  const html = renderMatrix(record, parsed)
  const bareAt = html.indexOf('Bare candidate')
  const scoredAt = html.indexOf('>Scored<')
  const plainAt = html.indexOf('>Plain<')
  const weirdAt = html.indexOf('>Weird<')
  const batteryAt = html.indexOf('Battery aft')
  assert.ok(bareAt >= 0 && scoredAt > bareAt && plainAt > scoredAt && weirdAt > plainAt && batteryAt > weirdAt)
  const bare = html.slice(bareAt, scoredAt)
  assert.match(bare, /<p class="unknown">not scored yet: no weight or arm is known for this option<\/p>/)
  assert.equal(bare.includes('no loading effect'), false)
  assert.match(html.slice(scoredAt, plainAt), /no loading effect/)
  assert.match(html.slice(plainAt, weirdAt), /no loading effect/)
  assert.match(html.slice(weirdAt, batteryAt), /no loading effect/)
  assert.match(html.slice(batteryAt), /kept loading/)
  assert.equal(html.slice(batteryAt).includes('not scored yet'), false)
})

test('renderMatrix shows worst rows, crossings, unknown cells, the private block, and escapes loading text', () => {
  const html = renderMatrix(record, sampleMatrix())
  assert.match(html, /<section class="panel matrix" data-test="matrix">/)
  assert.match(html, /<h3>Loading matrix<\/h3>/)
  assert.match(html, /Battery aft/)
  assert.match(html, /data-limit="fwd"[\s\S]*Forward limit[\s\S]*\+2\.8 in/)
  assert.match(html, /data-limit="fwd"[\s\S]*fwd loading/)
  const aft = html.match(/<p class="out" data-limit="aft">([\s\S]*?)<\/p>/)
  assert.ok(aft)
  assert.match(aft[1], /-1\.3 in/)
  assert.match(aft[1], /outside/)
  assert.match(aft[1], /light pilot &lt;script&gt;alert\(1\)&lt;\/script&gt;/)
  const gross = html.match(/<p class="out" data-limit="gross">([\s\S]*?)<\/p>/)
  assert.ok(gross)
  assert.match(gross[1], /-173 lb/)
  assert.match(gross[1], /outside/)
  assert.match(gross[1], /heavy pair/)
  assert.match(html, /aft limit binds below 140 lb/)
  assert.match(html, /<p class="unknown">2 cells unknown<\/p>/)
  assert.match(html, /<summary>All cells \(3\)<\/summary>/)
  assert.match(html, /<td class="out">-1\.3 in<\/td>/)
  assert.match(html, /<td>\u2013<\/td>/)
  assert.match(html, /Your loadings/)
  assert.match(html, /Pat solo/)
  assert.match(html, /Sam solo/)
  assert.match(html, /<p class="out" data-limit="aft">[\s\S]*Sam solo/)
  assert.equal(html.includes('SHOULD-NOT-SHOW'), false)
  assert.equal(html.includes('<script'), false)
  assert.match(html, /No change[\s\S]*no loading effect/)
  assert.match(html, /Broken effect[\s\S]*bad effect/)
  const brokenAt = html.indexOf('Broken effect')
  assert.equal(html.slice(brokenAt, brokenAt + 200).includes('no loading effect'), false)
  assert.equal(html.includes('null'), false)
})

test('renderMatrix uses an en dash for a null worst cell and is empty without data', () => {
  const html = renderMatrix(record, {
    record_id: 'cg-ballast',
    options: [
      {
        option: 'battery',
        label: 'Battery aft',
        public: {
          engine: 'plant-a',
          cells: [cell({ gross_lb: null, cg_in: null, fwd_margin_in: null, aft_margin_in: null, gross_margin_lb: null })],
          cell_count: 1,
          unknown_cells: 0,
          flag: 'unknown',
          worst: { fwd: null, aft: null, gross: null },
          crossings: null,
        },
        private: null,
      },
    ],
    unknowns: [],
  })
  assert.match(html, /data-limit="fwd"[\s\S]*\u2013/)
  assert.match(html, /data-limit="aft"[\s\S]*\u2013/)
  assert.match(html, /data-limit="gross"[\s\S]*\u2013/)
  assert.equal(html.includes('class="out"'), false)
  assert.equal(html.includes('outside'), false)
  assert.equal(html.includes('cells unknown'), false)
  assert.equal(renderMatrix(record, null), '')
  assert.equal(renderMatrix(record, { record_id: 'cg-ballast', options: [], unknowns: [] }), '')
})

function unknownsResponse(): MatrixResponse {
  return {
    record_id: 'cg-ballast',
    options: [],
    unknowns: [
      { id: 'u-open', text: 'coolant mass', how: 'weigh it', state: 'open', affects: [], job: null },
      {
        id: 'u-run',
        text: 'arm position',
        how: 'measure it',
        state: 'researching',
        affects: ['battery', 'missing-opt'],
        job: { id: 'job-run', state: 'queued', error: null, proposal: null, spotcheck: null },
      },
      {
        id: 'u-proposed',
        text: 'bag allowance',
        how: 'read the sheet',
        state: 'researching',
        affects: ['arm'],
        job: {
          id: 'job-ok',
          state: 'proposed',
          error: null,
          proposal: { claim: 'the sheet says 15 lb', url: 'https://example.test/spec', title: 'Spec sheet' },
          spotcheck: { matched: true, detail: 'quote found' },
        },
      },
      {
        id: 'u-miss',
        text: 'oil mass',
        how: 'read the plate',
        state: 'researching',
        affects: [],
        job: {
          id: 'job-bad',
          state: 'proposed',
          error: null,
          proposal: { claim: 'a different number', url: 'https://example.test/other', title: '' },
          spotcheck: { matched: false, detail: 'value differs' },
        },
      },
      {
        id: 'u-failed',
        text: 'hose weight',
        how: 'ask the shop',
        state: 'researching',
        affects: ['battery'],
        job: { id: 'job-fail', state: 'failed', error: 'lane down', proposal: null, spotcheck: null },
      },
      {
        id: 'u-sourced',
        text: 'known mass',
        how: 'already filed',
        state: 'sourced',
        affects: [],
        source: 'src-manual',
        job: null,
      },
    ],
  }
}

test('renderUnknowns shows research only for an open live unknown, job state, and the proposal verdict', () => {
  const live = renderUnknowns(record, unknownsResponse(), true)
  assert.match(live, /<section class="panel unknowns" data-test="unknowns">/)
  assert.match(live, /<h3>Unknowns<\/h3>/)
  assert.match(live, /coolant mass/)
  assert.match(live, /weigh it/)
  assert.match(live, /data-state="open"/)
  assert.match(live, /Whole record/)
  assert.match(live, /<button type="button" data-action="research" data-unknown="u-open">Research this<\/button>/)
  assert.match(live, /data-state="researching"/)
  assert.match(live, /queued/)
  assert.match(live, /Battery aft/)
  assert.match(live, /missing-opt/)
  assert.match(live, /Engine arm/)
  assert.match(live, /the sheet says 15 lb/)
  assert.match(live, /<a href="https:\/\/example\.test\/spec" target="_blank" rel="noopener noreferrer">Spec sheet<\/a>/)
  assert.match(live, /spot-check: matched quote found/)
  assert.match(live, /spot-check: not matched value differs/)
  assert.match(live, /<a href="https:\/\/example\.test\/other" target="_blank" rel="noopener noreferrer">https:\/\/example\.test\/other<\/a>/)
  const acceptOk = live.match(/<button type="button" data-action="resolve" data-outcome="accept" data-job="job-ok">/)
  assert.ok(acceptOk)
  const acceptBad = live.match(/<button type="button" data-action="resolve" data-outcome="accept" data-job="job-bad"[^>]*>/)
  assert.ok(acceptBad)
  assert.match(acceptBad[0], /\bdisabled\b/)
  assert.match(live, /data-action="resolve" data-outcome="dismiss" data-job="job-ok"/)
  assert.match(live, /data-action="resolve" data-outcome="unsourceable" data-job="job-bad"/)
  assert.match(live, /lane down/)
  assert.match(live, /data-action="research" data-unknown="u-failed"/)
  assert.match(live, /src-manual/)

  const readOnly = renderUnknowns(record, unknownsResponse(), false)
  assert.match(readOnly, /coolant mass/)
  assert.match(readOnly, /queued/)
  assert.match(readOnly, /spot-check: matched/)
  assert.equal(readOnly.includes('<button'), false)
  assert.equal(renderUnknowns(record, null, true), '')
})

function proposalUnknown(url: string, title = 'Click'): MatrixResponse {
  return {
    record_id: 'cg-ballast',
    options: [],
    unknowns: [
      {
        id: 'u-link',
        text: 'gap',
        how: 'look',
        state: 'researching',
        affects: [],
        job: {
          id: 'job-link',
          state: 'proposed',
          error: null,
          proposal: { claim: 'a claim', url, title },
          spotcheck: { matched: false, detail: '' },
        },
      },
    ],
  }
}

function polledUnknown(id: string, state: MatrixUnknown['state'], jobState: string | null): MatrixUnknown {
  return {
    id,
    text: 'gap',
    how: 'look',
    state,
    affects: [],
    job: jobState ? { id: `job-${id}`, state: jobState, error: null, proposal: null, spotcheck: null } : null,
  }
}

function polled(unknowns: MatrixUnknown[]): MatrixResponse {
  return { record_id: 'cg-ballast', options: [], unknowns }
}

test('needsPolling follows the newest job, and the paint and poll cap are pure', () => {
  assert.equal(MATRIX_POLL_CAP, 150)
  assert.equal(needsPolling(null), false)
  assert.equal(needsPolling(polled([])), false)
  assert.equal(needsPolling(polled([polledUnknown('u-open', 'open', null)])), false)
  assert.equal(needsPolling(polled([polledUnknown('u-prop', 'researching', 'proposed')])), false)
  assert.equal(needsPolling(polled([polledUnknown('u-fail', 'researching', 'failed')])), false)
  assert.equal(needsPolling(polled([polledUnknown('u-none', 'researching', null)])), false)
  assert.equal(needsPolling(polled([polledUnknown('u-q', 'researching', 'queued')])), true)
  assert.equal(needsPolling(polled([polledUnknown('u-r', 'open', 'running')])), true)
  assert.equal(
    needsPolling(polled([polledUnknown('u-prop', 'researching', 'proposed'), polledUnknown('u-r', 'researching', 'running')])),
    true,
  )
  assert.equal(shouldPoll(0, polled([polledUnknown('u-q', 'researching', 'queued')])), true)
  assert.equal(shouldPoll(MATRIX_POLL_CAP - 1, polled([polledUnknown('u-r', 'researching', 'running')])), true)
  assert.equal(shouldPoll(MATRIX_POLL_CAP, polled([polledUnknown('u-r', 'researching', 'running')])), false)
  assert.equal(shouldPoll(MATRIX_POLL_CAP + 1, polled([polledUnknown('u-q', 'researching', 'queued')])), false)
  assert.equal(shouldPoll(0, polled([polledUnknown('u-prop', 'researching', 'proposed')])), false)
  assert.equal(shouldPoll(0, null), false)
  assert.equal(isSamePaint('same', 'same'), true)
  assert.equal(isSamePaint('', ''), true)
  assert.equal(isSamePaint('<section>a</section>', '<section>b</section>'), false)
})

test('a proposal url becomes a link only for http(s)', () => {
  const safe = renderUnknowns(record, proposalUnknown('HTTPS://example.test/Spec'), true)
  assert.match(safe, /<a href="HTTPS:\/\/example\.test\/Spec" target="_blank" rel="noopener noreferrer">Click<\/a>/)
  const http = renderUnknowns(record, proposalUnknown('http://example.test/a', ''), true)
  assert.match(http, /<a href="http:\/\/example\.test\/a" target="_blank" rel="noopener noreferrer">http:\/\/example\.test\/a<\/a>/)

  const unsafe = [
    'javascript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'Javascript:alert(1)',
  ]
  for (const url of unsafe) {
    const html = renderUnknowns(record, proposalUnknown(url), true)
    assert.equal(html.includes('href='), false, url)
    assert.equal(html.includes('<a '), false, url)
    assert.equal(html.includes('<script'), false, url)
    assert.ok(html.includes(url.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')), url)
  }
})

test('decidePayloadFor keeps acknowledged unknowns exactly when the box is checked', () => {
  const ids = openUnknownIds(unknownsResponse())
  assert.deepEqual(ids, ['u-open', 'u-run', 'u-proposed', 'u-miss', 'u-failed'])
  const axes = [{ id: 'engine' }]
  const fields: Record<string, unknown> = {
    'pick-engine': 'battery',
    reason: ' because ',
    'ack-unknowns': 'on',
  }
  const get = (name: string) => (Object.hasOwn(fields, name) ? fields[name] : null)
  const checked = decidePayloadFor({ get }, axes, ids)
  assert.deepEqual(checked.picks, { engine: 'battery' })
  assert.equal(checked.reason, 'because')
  assert.deepEqual(checked.acknowledged_unknowns, ids)

  fields['ack-unknowns'] = null
  const unchecked = decidePayloadFor({ get }, axes, ids)
  assert.equal(Object.hasOwn(unchecked, 'acknowledged_unknowns'), false)
  assert.deepEqual(unchecked.picks, { engine: 'battery' })
  assert.equal(unchecked.reason, 'because')
})

test('buildDecidePayload adds acknowledged unknowns only when the box is checked', () => {
  const axes = [{ id: 'engine' }]
  const fields: Record<string, unknown> = {
    'pick-engine': 'a',
    reason: ' because ',
    'ack-unknowns': 'on',
  }
  const get = (name: string) => (Object.hasOwn(fields, name) ? fields[name] : null)
  const acked = buildDecidePayload({ get }, axes, ['u-open', 'u-run'])
  assert.deepEqual(acked.picks, { engine: 'a' })
  assert.equal(acked.reason, 'because')
  assert.deepEqual(acked.acknowledged_unknowns, ['u-open', 'u-run'])

  fields['ack-unknowns'] = null
  const plain = buildDecidePayload({ get }, axes, ['u-open', 'u-run'])
  assert.equal(Object.hasOwn(plain, 'acknowledged_unknowns'), false)
  assert.deepEqual(plain.picks, { engine: 'a' })

  fields['ack-unknowns'] = 'on'
  const noList = buildDecidePayload({ get }, axes)
  assert.equal(Object.hasOwn(noList, 'acknowledged_unknowns'), false)
})

test('a decide 409 that was not acknowledged explains the checkbox', () => {
  assert.equal(
    decideErrorMessage(409, { error: 'unknown cells not acknowledged', unknowns: ['u-open'] }),
    'Some loading cells depend on unknown values: tick the box to decide with them open, or research them first',
  )
  assert.equal(decideErrorMessage(409, { error: 'already decided' }), 'already decided')
  assert.equal(decideErrorMessage(500, { error: 'unknown cells not acknowledged' }), 'unknown cells not acknowledged')
})

test('a slower matrix response is stale once a newer request or generation is current', () => {
  assert.equal(matrixLoadIsCurrent(1, 1, 3, 3), true)
  assert.equal(matrixLoadIsCurrent(1, 2, 3, 3), false)
  assert.equal(matrixLoadIsCurrent(2, 2, 3, 4), false)
  assert.equal(matrixLoadIsCurrent(2, 2, 4, 4), true)
})

test('a 409 for unacknowledged unknowns mentions the box only when it is rendered', () => {
  const body = { error: 'unknown cells not acknowledged', unknowns: ['u-open'] }
  assert.equal(
    decideErrorMessage(409, body, true),
    'Some loading cells depend on unknown values: tick the box to decide with them open, or research them first',
  )
  assert.equal(
    decideErrorMessage(409, body, false),
    'Some loading cells depend on unknown values; reload the briefing room and try again',
  )
})

test('the decide form lists open unknowns and the reopen flag banner sits above reopen', () => {
  const matrix = unknownsResponse()
  const html = renderBriefingHtml(
    rec({
      status: 'decided',
      axes: [{ id: 'engine', options: ['battery'] }],
      options: [{ id: 'battery', label: 'Battery aft', kind: 'candidate', facts: [], why: '' }],
      decision: { picks: { engine: 'battery' }, date: '2026-10-19', reason: 'settled' },
      reopen_flag: { date: '2026-10-19', reason: 'digest moved', unknowns: ['u-open', 'u-run'] },
    }),
    'live',
    base({ mode: 'live', status: 'decided', decideEnabled: false }),
    matrix,
  )
  assert.match(html, /name="ack-unknowns"/)
  assert.match(html, /Decide with these unknowns still open \(5\)/)
  assert.match(html, /title="u-open, u-run, u-proposed, u-miss, u-failed"/)
  assert.match(html, /<small>u-open, u-run, u-proposed, u-miss, u-failed<\/small>/)
  assert.match(html, /data-test="reopen-flag"/)
  assert.match(html, /A sourced value changed the loading matrix after this decision \(unknowns: u-open, u-run\)\. Reopen it in the briefing room\./)
  const flagAt = html.indexOf('data-test="reopen-flag"')
  const reopenAt = html.indexOf('data-test="reopen"')
  assert.ok(flagAt >= 0 && reopenAt > flagAt)

  const quiet = renderBriefingHtml(rec(), 'live', base())
  assert.equal(quiet.includes('data-test="reopen-flag"'), false)
  assert.equal(quiet.includes('ack-unknowns'), false)
  const nulled = renderBriefingHtml(rec({ reopen_flag: null }), 'live', base())
  assert.equal(nulled.includes('data-test="reopen-flag"'), false)

  const readOnly = renderBriefingHtml(rec(), 'read-only', base({ mode: 'read-only' }), matrix)
  assert.equal(readOnly.includes('ack-unknowns'), false)
  assert.equal(readOnly.includes('data-test="matrix"'), false)
  assert.equal(readOnly.includes('data-test="unknowns"'), false)
})

test('read-only mode shows the reopen-flag banner only when the record carries one', () => {
  const flagged = renderBriefingHtml(
    rec({
      status: 'decided',
      decision: { picks: { engine: 'battery' }, date: '2026-10-19', reason: 'settled' },
      reopen_flag: { date: '2026-10-19', reason: 'digest moved', unknowns: ['u-open', 'u-run'] },
    }),
    'read-only',
    base({ mode: 'read-only', status: 'decided' }),
  )
  assert.match(flagged, /data-test="reopen-flag"/)
  assert.match(
    flagged,
    /A sourced value changed the loading matrix after this decision \(unknowns: u-open, u-run\)\. Reopen it in the briefing room\./,
  )
  assert.equal(flagged.includes('data-test="reopen"'), false)
  assert.equal(flagged.includes('data-test="decide"'), false)

  const absent = renderBriefingHtml(rec({ status: 'decided' }), 'read-only', base({ mode: 'read-only', status: 'decided' }))
  assert.equal(absent.includes('data-test="reopen-flag"'), false)
  const nulled = renderBriefingHtml(
    rec({ status: 'decided', reopen_flag: null }),
    'read-only',
    base({ mode: 'read-only', status: 'decided' }),
  )
  assert.equal(nulled.includes('data-test="reopen-flag"'), false)
})

test('a structured unknown still renders its text first in the skin', () => {
  const html = renderBriefingHtml(
    rec({
      unknowns: [{ id: 'u-open', text: 'coolant mass', how: 'weigh it', affects: ['battery'], state: 'open', source: 'src-manual' }],
    }),
    'read-only',
    base({ mode: 'read-only' }),
  )
  assert.match(html, /coolant mass — weigh it/)
})
