import test from 'node:test'
import assert from 'node:assert/strict'
import { HEAT_BOOST_C, cureGateHours, type Env, type ResinLite } from '../src/logic/cure'

// Curve: 20 h at 10 °C, 10 h at 20 °C, 5 h at 30 °C. Midpoints land on exact halves.
const curve: ResinLite = {
  min_temp_c: 10,
  gate_hours: [[10, 20], [20, 10], [30, 5]],
  flag: 'official',
}
const env = (tempC: number, heat: Env['heat'], humidity = 50): Env => ({ tempC, humidity, heat })

test('HEAT_BOOST_C is the estimate table', () => {
  assert.deepEqual(HEAT_BOOST_C, { none: 0, 'space-heater': 5, enclosure: 15 })
})

test('cureGateHours interpolates linearly between curve points', () => {
  assert.equal(cureGateHours(curve, env(10, 'none')), 20)
  assert.equal(cureGateHours(curve, env(15, 'none')), 15)
  assert.equal(cureGateHours(curve, env(20, 'none')), 10)
  assert.equal(cureGateHours(curve, env(30, 'none')), 5)
})

test('cureGateHours clamps at the top curve point', () => {
  assert.equal(cureGateHours(curve, env(40, 'none')), 5)
  assert.equal(cureGateHours(curve, env(30, 'none')), 5)
})

test('cureGateHours is null below the resin minimum', () => {
  assert.equal(cureGateHours(curve, env(9, 'none')), null)
})

test('cureGateHours is null below the first curve point instead of extrapolating', () => {
  const wide: ResinLite = { min_temp_c: 5, gate_hours: curve.gate_hours, flag: 'official' }
  assert.equal(cureGateHours(wide, env(7, 'none')), null)
})

test('cureGateHours is null when the curve is empty', () => {
  const empty: ResinLite = { min_temp_c: 10, gate_hours: [], flag: 'official' }
  assert.equal(cureGateHours(empty, env(20, 'none')), null)
})

test('cureGateHours is null when the resin flag is unsourced', () => {
  const unsourced: ResinLite = { ...curve, flag: 'unsourced' }
  assert.equal(cureGateHours(unsourced, env(20, 'none')), null)
})

test('estimated heat boosts the effective temperature and humidity does not', () => {
  assert.equal(cureGateHours(curve, env(10, 'space-heater')), 15)
  assert.equal(cureGateHours(curve, env(15, 'enclosure')), 5)
  // 5 °C is under the minimum until the enclosure boost lifts it onto the 20 °C point.
  assert.equal(cureGateHours(curve, env(5, 'none')), null)
  assert.equal(cureGateHours(curve, env(5, 'enclosure')), 10)
  assert.equal(cureGateHours(curve, env(20, 'none', 20)), cureGateHours(curve, env(20, 'none', 90)))
  const estimated: ResinLite = { ...curve, flag: 'estimate' }
  assert.equal(cureGateHours(estimated, env(20, 'none')), 10)
})
