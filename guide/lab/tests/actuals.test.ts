import test from 'node:test'
import assert from 'node:assert/strict'
import { ACTUALS_KEY, applyActuals, loadActuals, saveActuals } from '../src/logic/actuals'
import type { Storage2 } from '../src/logic/graph'
import type { Env } from '../src/logic/cure'
import { packSessions, type PlanStep } from '../src/logic/sessions'

const mem = (init: Record<string, string> = {}): Storage2 & { data: Record<string, string> } => {
  const data = { ...init }
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = v } }
}
const throwing: Storage2 = {
  getItem: () => { throw new Error('blocked') },
  setItem: () => { throw new Error('blocked') },
}

const env: Env = { tempC: 20, humidity: 50, heat: 'none' }
const step = (p: Partial<PlanStep> & Pick<PlanStep, 'id'>): PlanStep => ({
  group: 'g1',
  hours: 1,
  people: 1,
  cure: 'none',
  resin: null,
  ...p,
})

test('test_actual_hours_repack', () => {
  const steps = [step({ id: 'a', hours: 2 }), step({ id: 'b', hours: 2 })]
  const applied = applyActuals(steps, { a: { hours: 3 } })
  assert.equal(applied[0].hours, 3, 'an actual hour replaces the estimate before sessions are repacked')
  assert.equal(applied[1].hours, 2, 'a step with no actual keeps its estimate')
  assert.equal(steps[0].hours, 2, 'applyActuals does not mutate the estimate')
  assert.equal(steps[0].group, applied[0].group)
  assert.equal(applied[0].people, steps[0].people)

  const before = packSessions(steps, {}, env, 4)
  const after = packSessions(applied, {}, env, 4)
  assert.deepEqual(before.map((s) => s.steps), [['a', 'b']])
  assert.deepEqual(after.map((s) => s.steps), [['a'], ['b']], 'the longer actual no longer fits the old session')
  assert.deepEqual(after.map((s) => s.hours), [3, 2])
  assert.deepEqual(after.map((s) => s.hoursKnown), [true, true])

  const unk = [step({ id: 'u', hours: null })]
  assert.equal(packSessions(unk, {}, env, 4)[0].hoursKnown, false)
  const known = packSessions(applyActuals(unk, { u: { hours: 2 } }), {}, env, 4)
  assert.equal(known[0].hours, 2, 'an actual replaces the packed 1 h stand-in')
  assert.equal(known[0].hoursKnown, true, 'an actual marks the hours known')
  assert.equal(Number.isNaN(known[0].hours), false)
})

test('test_clear_actual_restores_estimate', () => {
  const steps = [step({ id: 'a', hours: 2, group: 'g' }), step({ id: 'b', hours: null, group: 'g' })]
  const estimate = packSessions(steps, {}, env, 4)
  const store = mem()
  saveActuals(store, { a: { hours: 5 }, b: { hours: 0 } })
  const applied = applyActuals(steps, loadActuals(store))
  assert.equal(applied[0].hours, 5, 'logged hours replace the estimate')
  assert.equal(applied[1].hours, 0, 'zero is a valid actual and is not "missing"')
  assert.equal(steps[0].hours, 2, 'the estimate stays on the step so clear can restore it')
  assert.equal(steps[1].hours, null)
  const logged = packSessions(applied, {}, env, 4)
  assert.equal(logged.every((s) => s.hoursKnown), true)
  assert.notDeepEqual(logged.map((s) => s.hours), estimate.map((s) => s.hours))

  saveActuals(store, {})
  const cleared = applyActuals(steps, loadActuals(store))
  assert.equal(cleared[0].hours, 2, 'clear restores the estimate')
  assert.equal(cleared[1].hours, null, 'clear restores an unknown hour')
  assert.deepEqual(packSessions(cleared, {}, env, 4), estimate)
})

test('test_invalid_actual_storage', () => {
  const loaded = loadActuals(mem({
    [ACTUALS_KEY]: JSON.stringify({ a: { hours: 2, spentUsd: 0 }, bad: { hours: 'no' }, extra: { spentUsd: '12' } }),
  }))
  assert.deepEqual(loaded, { a: { hours: 2, spentUsd: 0 } }, 'a valid actual loads from longez.actuals and invalid entries are dropped')
  assert.equal(ACTUALS_KEY, 'longez.actuals')
  assert.deepEqual(loadActuals(null), {})
  assert.deepEqual(loadActuals(throwing), {})
  for (const bad of ['{', 'null', '[]', '42', '"x"', '{"a":{"hours":NaN}}', '{"a":{"spentUsd":Infinity}}']) {
    assert.deepEqual(loadActuals(mem({ [ACTUALS_KEY]: bad })), {}, bad)
  }
  assert.doesNotThrow(() => saveActuals(null, { a: { hours: 1 } }))
  assert.doesNotThrow(() => saveActuals(throwing, { a: { hours: 1 } }))
})

test('test_negative_actuals_rejected_on_load_and_save', () => {
  const loaded = loadActuals(mem({
    [ACTUALS_KEY]: JSON.stringify({
      negH: { hours: -1 },
      negR: { spentUsd: -99 },
      mixedH: { hours: -0.5, spentUsd: 10 },
      mixedR: { hours: 2, spentUsd: -1 },
      zero: { hours: 0, spentUsd: 0 },
      ok: { hours: 1.5, spentUsd: 12 },
    }),
  }))
  assert.deepEqual(
    loaded,
    { zero: { hours: 0, spentUsd: 0 }, ok: { hours: 1.5, spentUsd: 12 } },
    'negative hours and receipts are dropped on load; zero stays',
  )

  const store = mem()
  saveActuals(store, {
    negH: { hours: -3 },
    negR: { spentUsd: -1 },
    mixed: { hours: 4, spentUsd: -2 },
    zero: { hours: 0, spentUsd: 0 },
    ok: { hours: 2, spentUsd: 12 },
  })
  assert.deepEqual(
    loadActuals(store),
    { zero: { hours: 0, spentUsd: 0 }, ok: { hours: 2, spentUsd: 12 } },
    'negative hours and receipts are not saved; a bad field drops the whole entry',
  )
  const raw = JSON.parse(store.data[ACTUALS_KEY]) as Record<string, { hours?: number; spentUsd?: number }>
  assert.equal(raw.negH, undefined)
  assert.equal(raw.negR, undefined)
  assert.equal(raw.mixed, undefined)
  assert.equal(raw.zero.hours, 0)
  assert.equal(raw.zero.spentUsd, 0)

  const steps = [step({ id: 'a', hours: 2 })]
  const applied = applyActuals(steps, { a: { hours: -5 } })
  assert.equal(applied[0].hours, 2, 'a negative hour does not replace the estimate or get packed')
  assert.equal(packSessions(applied, {}, env, 4)[0].hours, 2)
  assert.equal(applyActuals(steps, { a: { hours: 0 } })[0].hours, 0, 'zero hours stay valid')
  assert.equal(steps[0].hours, 2)
})

test('test_actuals_stay_local', () => {
  const calls: string[] = []
  const orig = globalThis.fetch
  globalThis.fetch = ((input: RequestInfo | URL) => {
    calls.push(String(input))
    throw new Error('actuals must not use the network')
  }) as typeof fetch
  try {
    const s = mem()
    saveActuals(s, { 'f04.firewall-aft': { hours: 3, spentUsd: 12 } })
    assert.deepEqual(Object.keys(s.data), [ACTUALS_KEY], 'actuals are stored only under longez.actuals')
    assert.equal(calls.length, 0, 'saving actuals must not fetch')
    assert.deepEqual(loadActuals(s), { 'f04.firewall-aft': { hours: 3, spentUsd: 12 } })
    assert.equal(calls.length, 0, 'loading actuals must not fetch')
    const raw = JSON.parse(s.data[ACTUALS_KEY]) as { 'f04.firewall-aft': { hours: number; spentUsd: number } }
    assert.equal(raw['f04.firewall-aft'].hours, 3)
    assert.equal(raw['f04.firewall-aft'].spentUsd, 12)
  } finally {
    globalThis.fetch = orig
  }
})
