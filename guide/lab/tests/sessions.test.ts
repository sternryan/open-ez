import test from 'node:test'
import assert from 'node:assert/strict'
import type { Env, ResinLite } from '../src/logic/cure'
import { packSessions, type PlanStep } from '../src/logic/sessions'

const resin: ResinLite = {
  min_temp_c: 10,
  gate_hours: [[10, 8], [30, 4]],
  flag: 'official',
}
const warm: Env = { tempC: 30, humidity: 50, heat: 'none' }
const cold: Env = { tempC: 5, humidity: 50, heat: 'none' }
const resins = { 'mgs-285-287': resin }

const step = (p: Partial<PlanStep> & Pick<PlanStep, 'id'>): PlanStep => ({
  group: 'g1',
  hours: 1,
  people: 1,
  cure: 'none',
  resin: null,
  ...p,
})

test('packSessions fills a session in order while the next step fits', () => {
  const steps = [step({ id: 'a', hours: 1.5 }), step({ id: 'b', hours: 1.5 }), step({ id: 'c', hours: 1.5 })]
  const sessions = packSessions(steps, resins, warm)
  assert.deepEqual(sessions.map((s) => s.index), [0, 1])
  assert.deepEqual(sessions.map((s) => s.steps), [['a', 'b'], ['c']])
  assert.deepEqual(sessions.map((s) => s.hours), [3, 1.5])
  assert.deepEqual(sessions.map((s) => s.group), ['g1', 'g1'])
  assert.deepEqual(sessions.map((s) => s.hoursKnown), [true, true])
  assert.deepEqual(sessions.map((s) => s.buddy), [false, false])
  assert.deepEqual(sessions.map((s) => s.cureAfter), [null, null])
})

test('an oversize step is one session and is not split', () => {
  const steps = [step({ id: 'a', hours: 1 }), step({ id: 'big', hours: 5 }), step({ id: 'c', hours: 1 })]
  const sessions = packSessions(steps, resins, warm, 4)
  assert.deepEqual(sessions.map((s) => s.steps), [['a'], ['big'], ['c']])
  assert.deepEqual(sessions.map((s) => s.hours), [1, 5, 1])
  assert.equal(sessions[1].hoursKnown, true)
})

test('a step with no hours packs as 1 h and marks the session unknown', () => {
  const steps = [
    step({ id: 'a', hours: null }),
    step({ id: 'b', hours: null }),
    step({ id: 'c', hours: null }),
    step({ id: 'd', hours: null }),
    step({ id: 'e', hours: null }),
  ]
  const sessions = packSessions(steps, resins, warm, 4)
  assert.deepEqual(sessions.map((s) => s.steps), [['a', 'b', 'c', 'd'], ['e']])
  assert.deepEqual(sessions.map((s) => s.hours), [4, 1])
  assert.deepEqual(sessions.map((s) => s.hoursKnown), [false, false])
})

test('a session is buddy when any step needs two people', () => {
  const alone = packSessions([step({ id: 'a' }), step({ id: 'b' })], resins, warm, 4)
  assert.equal(alone[0].buddy, false)
  const helped = packSessions([step({ id: 'a' }), step({ id: 'b', people: 2 })], resins, warm, 4)
  assert.equal(helped[0].buddy, true)
  assert.deepEqual(helped[0].steps, ['a', 'b'])
})

test('a group change closes the session even when hours remain', () => {
  const steps = [step({ id: 'a', hours: 1, group: 'g1' }), step({ id: 'b', hours: 1, group: 'g2' })]
  const sessions = packSessions(steps, resins, warm, 4)
  assert.deepEqual(sessions.map((s) => ({ group: s.group, steps: s.steps, hours: s.hours, cureAfter: s.cureAfter })), [
    { group: 'g1', steps: ['a'], hours: 1, cureAfter: null },
    { group: 'g2', steps: ['b'], hours: 1, cureAfter: null },
  ])
})

test('a cure closes the session, including when the step hours are unknown', () => {
  const steps = [
    step({ id: 'a', hours: 1, cure: 'part', resin: 'mgs-285-287' }),
    step({ id: 'b', hours: 1, cure: 'all', resin: 'mgs-285-287' }),
    step({ id: 'c', hours: 2 }),
    step({ id: 'd', hours: null, cure: 'part', resin: 'mgs-285-287' }),
  ]
  const sessions = packSessions(steps, resins, warm, 4)
  assert.deepEqual(sessions.map((s) => s.steps), [['a'], ['b'], ['c', 'd']])
  assert.equal(sessions[2].hours, 3)
  assert.equal(sessions[2].hoursKnown, false)
  assert.deepEqual(sessions.map((s) => s.cureAfter), [
    { hours: 4, scope: 'part' },
    { hours: 4, scope: 'all' },
    { hours: 4, scope: 'part' },
  ])
})

test('a null cure gate still packs the session', () => {
  const below = packSessions(
    [step({ id: 'a', hours: 2, cure: 'all', resin: 'mgs-285-287' })],
    resins,
    cold,
    4,
  )
  assert.deepEqual(below, [{
    index: 0,
    group: 'g1',
    steps: ['a'],
    hours: 2,
    hoursKnown: true,
    buddy: false,
    cureAfter: { hours: null, scope: 'all' },
  }])
  const missing = packSessions(
    [step({ id: 'b', hours: null, cure: 'part', resin: null })],
    resins,
    warm,
    4,
  )
  assert.equal(missing[0].hours, 1)
  assert.equal(missing[0].hoursKnown, false)
  assert.deepEqual(missing[0].cureAfter, { hours: null, scope: 'part' })
})

test('packSessions is deterministic and does not mutate its inputs', () => {
  const steps = [step({ id: 'a', hours: 2, people: 2 }), step({ id: 'b', hours: null, group: 'g2', cure: 'part', resin: 'mgs-285-287' })]
  const before = structuredClone({ steps, resins, env: warm })
  const first = packSessions(steps, resins, warm, 4)
  const second = packSessions(steps, resins, warm, 4)
  assert.deepEqual(first, second)
  assert.deepEqual({ steps, resins, env: warm }, before)
})
