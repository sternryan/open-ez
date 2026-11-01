import test from 'node:test'
import assert from 'node:assert/strict'
import { DEFAULT_ENV, DEFAULT_SESSION_HOURS, loadEnv, saveEnv, loadSessionHours, saveSessionHours } from '../src/ui/environment'
import type { Storage2 } from '../src/logic/graph'

const mem = (init: Record<string, string> = {}): Storage2 & { data: Record<string, string> } => {
  const data = { ...init }
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = v } }
}
const throwing: Storage2 = { getItem: () => { throw new Error('blocked') }, setItem: () => { throw new Error('blocked') } }

test('the default environment is 20 °C, 50 %, no heat', () => {
  assert.deepEqual(DEFAULT_ENV, { tempC: 20, humidity: 50, heat: 'none' })
})

test('missing, null or blocked storage gives the default', () => {
  assert.deepEqual(loadEnv(null), DEFAULT_ENV)
  assert.deepEqual(loadEnv(mem()), DEFAULT_ENV)
  assert.deepEqual(loadEnv(throwing), DEFAULT_ENV)
})

test('invalid stored values give the default, never a half-parsed env', () => {
  for (const bad of ['{', 'null', '[]', '"x"', '42', '{"tempC":"warm","humidity":50,"heat":"none"}', '{"tempC":20,"humidity":50,"heat":"oven"}',
    '{"tempC":20,"humidity":50}', '{"tempC":null,"humidity":50,"heat":"none"}', '{"tempC":99,"humidity":50,"heat":"none"}', '{"tempC":20,"humidity":-5,"heat":"none"}']) {
    const r = loadEnv(mem({ 'longez.env': bad }))
    assert.deepEqual(r, DEFAULT_ENV, bad)
    assert.notEqual(r, DEFAULT_ENV, 'a copy, so a caller cannot change the default')
  }
})

test('save then load round-trips on longez.env', () => {
  const s = mem()
  saveEnv(s, { tempC: 12, humidity: 70, heat: 'enclosure' })
  assert.ok('longez.env' in s.data)
  assert.deepEqual(loadEnv(s), { tempC: 12, humidity: 70, heat: 'enclosure' })
})

test('saving to null or blocked storage is a quiet no-op', () => {
  saveEnv(null, DEFAULT_ENV)
  saveEnv(throwing, DEFAULT_ENV)
  saveSessionHours(null, 6)
  saveSessionHours(throwing, 6)
})

test('session hours default to 4 and reject invalid values', () => {
  assert.equal(DEFAULT_SESSION_HOURS, 4)
  assert.equal(loadSessionHours(null), 4)
  assert.equal(loadSessionHours(throwing), 4)
  for (const bad of ['', 'x', '0', '-2', '99', 'NaN']) assert.equal(loadSessionHours(mem({ 'longez.sessionHours': bad })), 4, bad)
  const s = mem()
  saveSessionHours(s, 6.5)
  assert.equal(loadSessionHours(s), 6.5)
})
