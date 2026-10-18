import test from 'node:test'
import assert from 'node:assert/strict'
import { detectMode, reduce, type HealthResponse, type State } from '../src/hangar/briefingState'

function base(over: Partial<State> = {}): State {
  return {
    recordId: 'powerplant-fuel-resin',
    mode: 'live',
    status: 'open',
    transcript: [],
    error: null,
    busy: false,
    decideEnabled: true,
    ...over,
  }
}

function probe(status: number, body: unknown): (url: string) => Promise<HealthResponse> {
  return async (url) => {
    assert.equal(url, 'api/health')
    return {
      ok: status >= 200 && status < 300,
      json: async () => body,
    }
  }
}

test('detectMode is read-only when the health probe rejects', async () => {
  const mode = await detectMode(async (url) => {
    assert.equal(url, 'api/health')
    throw new Error('offline')
  })
  assert.equal(mode, 'read-only')
})

test('detectMode is read-only on a non-ok health response', async () => {
  assert.equal(await detectMode(probe(404, { ok: true })), 'read-only')
  assert.equal(await detectMode(probe(500, { ok: true })), 'read-only')
})

test('detectMode is live only when health returns ok true', async () => {
  assert.equal(await detectMode(probe(200, { ok: true })), 'live')
})

test('detectMode is read-only when the health body is not ok true', async () => {
  const bad: unknown[] = [{ ok: false }, {}, null, 'ok', { ok: 'true' }, { ok: 1 }, []]
  for (const body of bad) {
    assert.equal(await detectMode(probe(200, body)), 'read-only', JSON.stringify(body))
  }
  const mode = await detectMode(async (url) => {
    assert.equal(url, 'api/health')
    return {
      ok: true,
      json: async () => {
        throw new SyntaxError('not json')
      },
    }
  })
  assert.equal(mode, 'read-only')
})

test('sent then errored keeps the transcript and shows the error', () => {
  const start = base({
    transcript: [{ who: 'council', text: 'earlier note' }],
    error: null,
    busy: false,
  })
  const sent = reduce(start, { type: 'sent', text: 'why this resin' })
  assert.deepEqual(sent.transcript, [
    { who: 'council', text: 'earlier note' },
    { who: 'owner', text: 'why this resin' },
  ])
  assert.equal(sent.busy, true)
  assert.equal(sent.error, null)
  assert.deepEqual(start.transcript, [{ who: 'council', text: 'earlier note' }])

  const failed = reduce(sent, { type: 'errored', message: 'council unavailable' })
  assert.deepEqual(failed.transcript, sent.transcript)
  assert.equal(failed.error, 'council unavailable')
  assert.equal(failed.busy, false)
  assert.equal(failed.status, 'open')
  assert.equal(failed.decideEnabled, true)
  assert.equal(sent.busy, true)
  assert.equal(sent.error, null)
})

test('replied appends a council line and clears busy', () => {
  const waiting = base({
    transcript: [{ who: 'owner', text: 'why this resin' }],
    busy: true,
    error: 'stale',
  })
  const next = reduce(waiting, { type: 'replied', text: 'the scores favor the lighter engine' })
  assert.deepEqual(next.transcript, [
    { who: 'owner', text: 'why this resin' },
    { who: 'council', text: 'the scores favor the lighter engine' },
  ])
  assert.equal(next.busy, false)
  assert.equal(next.error, null)
  assert.equal(waiting.busy, true)
})

test('decided disables the decide control and reopened enables it', () => {
  const open = base({
    transcript: [{ who: 'owner', text: 'closing on the book engine' }],
    error: 'ignored',
    busy: true,
  })
  const decided = reduce(open, { type: 'decided' })
  assert.equal(decided.status, 'decided')
  assert.equal(decided.decideEnabled, false)
  assert.deepEqual(decided.transcript, open.transcript)
  assert.equal(decided.error, 'ignored')
  assert.equal(decided.busy, true)
  assert.equal(open.status, 'open')
  assert.equal(open.decideEnabled, true)

  const reopened = reduce(decided, { type: 'reopened' })
  assert.equal(reopened.status, 'reopened')
  assert.equal(reopened.decideEnabled, true)
  assert.deepEqual(reopened.transcript, decided.transcript)
  assert.equal(decided.decideEnabled, false)
})

test('loaded sets status and whether decide is enabled', () => {
  const decided = reduce(base({ decideEnabled: true }), { type: 'loaded', status: 'decided' })
  assert.equal(decided.status, 'decided')
  assert.equal(decided.decideEnabled, false)

  const opened = reduce(base({ status: 'decided', decideEnabled: false }), { type: 'loaded', status: 'open' })
  assert.equal(opened.status, 'open')
  assert.equal(opened.decideEnabled, true)

  const reopened = reduce(base({ status: 'decided', decideEnabled: false }), { type: 'loaded', status: 'reopened' })
  assert.equal(reopened.status, 'reopened')
  assert.equal(reopened.decideEnabled, true)
  assert.deepEqual(reopened.transcript, [])
})
