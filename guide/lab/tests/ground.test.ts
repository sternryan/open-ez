import test from 'node:test'
import assert from 'node:assert/strict'
import {
  DEFAULT_SPEED,
  GROUND_GROUP,
  GROUND_KEY,
  GROUND_SEEN,
  GROUND_SKIP_KEY,
  GROUND_SKIPPED,
  SHOP_SETUP,
  choiceForOffer,
  clearGroundSkipped,
  firstBuildStep,
  firstGroundStep,
  isGroundGroup,
  loadGroundSeen,
  loadGroundSkipped,
  saveGroundSeen,
  saveGroundSkipped,
  showsShopControls,
  speedFor,
} from '../src/logic/ground'
import type { Storage2 } from '../src/logic/graph'

const mem = (init: Record<string, string> = {}): Storage2 & { data: Record<string, string> } => {
  const data = { ...init }
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = v } }
}
const throwing: Storage2 = {
  getItem: () => { throw new Error('blocked') },
  setItem: () => { throw new Error('blocked') },
}

test('an open offer starts ground school, and leaves it only by skipping', () => {
  assert.equal(choiceForOffer('play', true), 'start')
  assert.equal(choiceForOffer('select', true), 'start')
  assert.equal(choiceForOffer('play', false), 'skip')
  assert.equal(choiceForOffer('select', false), 'skip')
})

test('ground school is unseen until the offer is answered', () => {
  assert.equal(GROUND_KEY, 'longez.ground')
  assert.equal(GROUND_SEEN, 'seen')
  assert.equal(loadGroundSeen(null), false)
  assert.equal(loadGroundSeen(mem()), false)
  assert.equal(loadGroundSeen(throwing), false)
  assert.equal(loadGroundSeen(mem({ [GROUND_KEY]: 'yes' })), false)
  const s = mem()
  saveGroundSeen(s)
  assert.equal(s.data[GROUND_KEY], 'seen')
  assert.equal(loadGroundSeen(s), true)
  saveGroundSeen(null)
  saveGroundSeen(throwing)
})

test('skip is remembered apart from the offer, and start clears it', () => {
  assert.equal(GROUND_SKIP_KEY, 'longez.ground.skip')
  assert.equal(GROUND_SKIPPED, 'skipped')
  assert.equal(loadGroundSkipped(null), false)
  assert.equal(loadGroundSkipped(mem()), false)
  assert.equal(loadGroundSkipped(throwing), false)
  assert.equal(loadGroundSkipped(mem({ [GROUND_SKIP_KEY]: 'seen' })), false)
  const s = mem()
  saveGroundSkipped(s)
  assert.equal(s.data[GROUND_SKIP_KEY], 'skipped')
  assert.equal(s.data[GROUND_KEY], undefined)
  assert.equal(loadGroundSkipped(s), true)
  assert.equal(loadGroundSeen(s), false)
  clearGroundSkipped(s)
  assert.equal(loadGroundSkipped(s), false)
  saveGroundSkipped(null)
  saveGroundSkipped(throwing)
  clearGroundSkipped(null)
  clearGroundSkipped(throwing)
})

test('ground lessons default to 1x and build steps to 4x, and either side can be overridden', () => {
  assert.deepEqual(DEFAULT_SPEED, { ground: 1, build: 4 })
  assert.equal(speedFor(GROUND_GROUP, DEFAULT_SPEED), 1)
  assert.equal(speedFor('bulkheads-firewall', DEFAULT_SPEED), 4)
  assert.equal(speedFor(null, DEFAULT_SPEED), 4)
  const choice = { ground: 16 as const, build: 1 as const }
  assert.equal(speedFor(GROUND_GROUP, choice), 16)
  assert.equal(speedFor('canard', choice), 1)
})

test('skip lands on the first step outside ground school, and shop setup is the lesson with the shop controls', () => {
  const steps = [
    { id: 'g00.shop-setup', group: GROUND_GROUP },
    { id: 'g00.bookend', group: GROUND_GROUP },
    { id: 'f04.front-seat-bkhd-front', group: 'bulkheads-firewall' },
  ]
  assert.equal(GROUND_GROUP, 'ground-school')
  assert.equal(SHOP_SETUP, 'g00.shop-setup')
  assert.equal(isGroundGroup(GROUND_GROUP), true)
  assert.equal(isGroundGroup('canard'), false)
  assert.equal(isGroundGroup(null), false)
  assert.equal(firstGroundStep(steps), 'g00.shop-setup')
  assert.equal(firstBuildStep(steps), 'f04.front-seat-bkhd-front')
  assert.equal(firstBuildStep([{ id: 'g00.bookend', group: GROUND_GROUP }]), null)
  assert.equal(firstGroundStep([{ id: 'f04.front-seat-bkhd-front', group: 'bulkheads-firewall' }]), null)
  assert.equal(showsShopControls(SHOP_SETUP), true)
  assert.equal(showsShopControls('g00.bookend'), false)
  assert.equal(showsShopControls('f04.front-seat-bkhd-front'), false)
})
