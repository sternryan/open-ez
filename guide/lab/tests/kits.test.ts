import test from 'node:test'
import assert from 'node:assert/strict'
import { GROUND_GROUP } from '../src/logic/ground'
import { SCRAP, kitsFor, meterAt, type Kit } from '../src/logic/kits'
import type { Session } from '../src/logic/sessions'

const catalog = {
  bid: { price_usd: 10, stale: false },
  peel: { price_usd: null, stale: true },
  carbon: { price_usd: 4, stale: true },
}

test('SCRAP is 25 percent once at kit level', () => {
  assert.equal(SCRAP, 0.25)
})

test('kitsFor merges quantities, prices the partial sum, and scraps once', () => {
  const kits = kitsFor(
    ['bulkheads', 'sides', 'nose'],
    {
      sides: [{ item: 'carbon', qty: 2 }],
      bulkheads: [
        { item: 'bid', qty: 2 },
        { item: 'peel', qty: 1 },
        { item: 'bid', qty: 2 },
        { item: 'missing', qty: 3 },
      ],
      extra: [{ item: 'bid', qty: 9 }],
    },
    catalog,
  )
  assert.deepEqual(kits, [
    {
      group: 'bulkheads',
      lines: [
        { item: 'bid', qty: 4, unitPrice: 10, stale: false },
        { item: 'peel', qty: 1, unitPrice: null, stale: true },
        { item: 'missing', qty: 3, unitPrice: null, stale: false },
      ],
      subtotal: 40,
      scrap: 10,
      unpriced: 2,
    },
    {
      group: 'sides',
      lines: [{ item: 'carbon', qty: 2, unitPrice: 4, stale: true }],
      subtotal: 8,
      scrap: 2,
      unpriced: 0,
    },
    { group: 'nose', lines: [], subtotal: 0, scrap: 0, unpriced: 0 },
  ] satisfies Kit[])
  assert.equal(kits[0].scrap, kits[0].subtotal * SCRAP)
  assert.equal(kits[1].scrap, kits[1].subtotal * SCRAP)
})

test('an empty buy list is an empty kit', () => {
  assert.deepEqual(kitsFor(['g1', 'g2'], { g1: [] }, {}), [
    { group: 'g1', lines: [], subtotal: 0, scrap: 0, unpriced: 0 },
    { group: 'g2', lines: [], subtotal: 0, scrap: 0, unpriced: 0 },
  ])
})

const session = (p: Partial<Session> & Pick<Session, 'index' | 'group'>): Session => ({
  steps: [p.group],
  hours: 2,
  hoursKnown: true,
  buddy: false,
  cureAfter: null,
  ...p,
})

test('spent is earlier kits and next buy is this group onward', () => {
  const kits = kitsFor(
    ['bulkheads', 'sides', 'nose'],
    {
      bulkheads: [
        { item: 'bid', qty: 4 },
        { item: 'peel', qty: 1 },
        { item: 'missing', qty: 3 },
      ],
      sides: [{ item: 'carbon', qty: 2 }],
    },
    catalog,
  )
  const sessions = [
    session({ index: 0, group: 'bulkheads' }),
    session({ index: 1, group: 'sides' }),
    session({ index: 2, group: 'nose' }),
  ]
  const atBulk = meterAt(sessions, kits, 0)
  assert.equal(atBulk.spent, null)
  assert.equal(atBulk.spentUnpriced, 0)
  assert.deepEqual(atBulk.nextBuy, { group: 'bulkheads', amount: 50, unpriced: 2 })

  const atSides = meterAt(sessions, kits, 1)
  assert.equal(atSides.spent, 50)
  assert.equal(atSides.spentUnpriced, 2)
  assert.deepEqual(atSides.nextBuy, { group: 'sides', amount: 10, unpriced: 0 })

  const atNose = meterAt(sessions, kits, 2)
  assert.equal(atNose.spent, 60)
  assert.equal(atNose.spentUnpriced, 2)
  assert.deepEqual(atNose.nextBuy, { group: 'nose', amount: 0, unpriced: 0 })
})

test('calendar hours include earlier cure waits and are null when one wait is unknown', () => {
  const kits: Kit[] = []
  const sessions = [
    session({ index: 0, group: 'g', hours: 2, cureAfter: { hours: 3, scope: 'part' } }),
    session({ index: 1, group: 'g', hours: 2, cureAfter: { hours: null, scope: 'all' } }),
    session({ index: 2, group: 'g', hours: 2 }),
  ]
  assert.equal(meterAt(sessions, kits, 0).calendarHours, 0)
  assert.equal(meterAt(sessions, kits, 1).calendarHours, 5)
  assert.equal(meterAt(sessions, kits, 2).calendarHours, null)
})

test('calendar hours are null when an earlier session has placeholder hours, even with every cure wait known', () => {
  const sessions = [
    session({ index: 0, group: 'g', hours: 2, cureAfter: { hours: 3, scope: 'part' } }),
    session({ index: 1, group: 'g', hours: 1, hoursKnown: false, cureAfter: { hours: 4, scope: 'part' } }),
    session({ index: 2, group: 'g', hours: 2 }),
  ]
  assert.equal(meterAt(sessions, [], 1).calendarHours, 5) // only session 0 is behind: its hours are real
  assert.equal(meterAt(sessions, [], 2).calendarHours, null) // session 1's 1 h is the planning placeholder
  assert.equal(meterAt(sessions, [], 2).hoursDone, 3) // shop hours still show (the meter says they include a placeholder)
})

test('the meter sums shop hours and counts sessions left in the group', () => {
  const sessions = [
    session({ index: 0, group: 'g1', hours: 2 }),
    session({ index: 1, group: 'g1', hours: 2, cureAfter: { hours: null, scope: 'part' } }),
    session({ index: 2, group: 'g2', hours: 2, hoursKnown: false }),
    session({ index: 3, group: 'g2', hours: 1 }),
    session({ index: 4, group: 'g3', hours: 2, cureAfter: { hours: 5, scope: 'all' } }),
  ]
  const atStart = meterAt(sessions, [], 0)
  assert.equal(atStart.hoursDone, 0)
  assert.equal(atStart.hoursTotal, 9)
  assert.equal(atStart.hoursKnown, false)
  assert.equal(atStart.sessionsLeftInGroup, 2)

  const inGroup = meterAt(sessions, [], 2)
  assert.equal(inGroup.hoursDone, 4)
  assert.equal(inGroup.sessionsLeftInGroup, 2)

  const atEnd = meterAt(sessions, [], 4)
  assert.equal(atEnd.hoursDone, 7)
  assert.equal(atEnd.sessionsLeftInGroup, 1)

  const known = [
    session({ index: 0, group: 'a', hours: 1 }),
    session({ index: 1, group: 'a', hours: 1 }),
  ]
  const done = meterAt(known, [], 1)
  assert.equal(done.hoursKnown, true)
  assert.equal(done.hoursDone, 1)
  assert.equal(done.hoursTotal, 2)
  assert.equal(done.sessionsLeftInGroup, 1)
  assert.equal(done.spent, null)
  assert.equal(done.nextBuy, null)
  assert.equal(done.spentUnpriced, 0)
  assert.equal(done.calendarHours, 1)
})

test('skipping ground school leaves spent and hours done at the start; playing the lessons counts them', () => {
  // Practice kit is 25 plus one unpriced line. The two build kits are 10 and 12.5.
  const kits = kitsFor(
    [GROUND_GROUP, 'sides', 'nose'],
    {
      [GROUND_GROUP]: [
        { item: 'bid', qty: 2 },
        { item: 'peel', qty: 1 },
      ],
      sides: [{ item: 'carbon', qty: 2 }],
      nose: [{ item: 'bid', qty: 1 }],
    },
    catalog,
  )
  const sessions = [
    session({ index: 0, group: GROUND_GROUP, hours: 2, cureAfter: { hours: 3, scope: 'part' } }),
    session({ index: 1, group: GROUND_GROUP, hours: 2 }),
    session({ index: 2, group: 'sides', hours: 2 }),
    session({ index: 3, group: 'nose', hours: 2 }),
  ]
  const atStart = meterAt(sessions, kits, 0)
  assert.equal(atStart.spent, null)
  assert.equal(atStart.hoursDone, 0)
  assert.equal(atStart.remaining, 47.5)
  assert.equal(atStart.hoursTotal, 8)
  assert.equal(atStart.totalSessions, 4)

  // Start, then watch through to the first build step. Today's reading: the lessons are done.
  const played = meterAt(sessions, kits, 2)
  assert.equal(played.spent, 25)
  assert.equal(played.spentUnpriced, 1)
  assert.equal(played.hoursDone, 4)
  assert.equal(played.remaining, 22.5)
  assert.equal(played.calendarHours, 7)
  assert.equal(played.hoursTotal, atStart.hoursTotal)
  assert.equal(played.totalSessions, atStart.totalSessions)

  // Skip lands on that same step. The lessons were not bought or spent. The practice kit stays
  // in the remaining estimate. Plan totals do not move.
  const skipped = meterAt(sessions, kits, 2, {}, { groundSkipped: true })
  assert.equal(skipped.spent, atStart.spent)
  assert.equal(skipped.spentUnpriced, 0)
  assert.equal(skipped.hoursDone, atStart.hoursDone)
  assert.equal(skipped.remaining, atStart.remaining)
  assert.equal(skipped.remainingUnpriced, atStart.remainingUnpriced)
  assert.equal(skipped.calendarHours, atStart.calendarHours)
  assert.equal(skipped.hoursTotal, atStart.hoursTotal)
  assert.equal(skipped.totalSessions, atStart.totalSessions)
  assert.deepEqual(skipped.nextBuy, { group: 'sides', amount: 10, unpriced: 0 })

  // Later build steps still count. The skipped practice kit does not.
  const further = meterAt(sessions, kits, 3, {}, { groundSkipped: true })
  assert.equal(further.spent, 10)
  assert.equal(further.spentUnpriced, 0)
  assert.equal(further.hoursDone, 2)
  assert.equal(further.remaining, 37.5)
  assert.equal(further.remainingUnpriced, 1)
  assert.equal(further.calendarHours, 2)
  assert.equal(further.hoursTotal, atStart.hoursTotal)
  assert.equal(further.totalSessions, atStart.totalSessions)

  const playedFurther = meterAt(sessions, kits, 3)
  assert.equal(playedFurther.spent, 35)
  assert.equal(playedFurther.hoursDone, 6)
  assert.equal(playedFurther.remaining, 12.5)
  assert.equal(playedFurther.calendarHours, 9)
})

test('a skipped ground lesson with placeholder hours does not make elapsed time unknown', () => {
  const sessions = [
    session({ index: 0, group: GROUND_GROUP, hours: 1, hoursKnown: false }),
    session({ index: 1, group: 'sides', hours: 2 }),
  ]
  const skipped = meterAt(sessions, [], 1, {}, { groundSkipped: true })
  assert.equal(skipped.hoursDone, 0)
  assert.equal(skipped.calendarHours, 0)
  const played = meterAt(sessions, [], 1)
  assert.equal(played.hoursDone, 1)
  assert.equal(played.calendarHours, null)
})
