// Kit rollup and the planning meter. A later wave fills the bodies.

import type { Session } from './sessions'

export interface Kit {
  group: string
  lines: { item: string; qty: number; unitPrice: number | null; stale: boolean }[]
  subtotal: number
  scrap: number
  unpriced: number
}

/** Scrap and mixing loss, applied once at kit level. */
export const SCRAP = 0.25

export function kitsFor(
  groups: string[],
  buysByGroup: Record<string, { item: string; qty: number }[]>,
  catalog: Record<string, { price_usd: number | null; stale: boolean }>,
): Kit[] {
  return groups.map((group) => {
    const buys = buysByGroup[group] ?? []
    const merged: { item: string; qty: number }[] = []
    for (const buy of buys) {
      const existing = merged.find((m) => m.item === buy.item)
      if (existing) {
        existing.qty += buy.qty
      } else {
        merged.push({ item: buy.item, qty: buy.qty })
      }
    }

    const lines = merged.map((m) => {
      const entry = catalog[m.item]
      return {
        item: m.item,
        qty: m.qty,
        unitPrice: entry?.price_usd ?? null,
        stale: entry?.stale ?? false,
      }
    })

    let subtotal = 0
    let unpriced = 0
    for (const line of lines) {
      if (line.unitPrice !== null) {
        subtotal += line.qty * line.unitPrice
      } else {
        unpriced += 1
      }
    }

    const scrap = subtotal * SCRAP
    return {
      group,
      lines,
      subtotal,
      scrap,
      unpriced,
    }
  })
}

export interface Meter {
  spent: number | null
  spentUnpriced: number
  nextBuy: { group: string; amount: number; unpriced: number } | null
  hoursDone: number
  hoursTotal: number
  hoursKnown: boolean
  sessionsLeftInGroup: number
  calendarHours: number | null
}

export function meterAt(sessions: Session[], kits: Kit[], currentSession: number): Meter {
  const currentGroup = sessions[currentSession].group
  const currentKitIndex = kits.findIndex((k) => k.group === currentGroup)

  let spent: number | null = null
  let spentUnpriced = 0

  if (currentKitIndex > 0) {
    spent = 0
    for (let i = 0; i < currentKitIndex; i++) {
      spent += kits[i].subtotal + kits[i].scrap
      if (kits[i].unpriced > 0) {
        // The prompt says "spentUnpriced sums their unpriced".
        // Looking at tests, unpriced is a count of lines/items, not a dollar amount.
        // However, the test `atSides.spentUnpriced = 2` where `unpriced: 2` is in the kit
        // suggests we sum the `unpriced` property of the kits.
        spentUnpriced += kits[i].unpriced
      }
    }
  }

  let nextBuy: { group: string; amount: number; unpriced: number } | null = null
  if (currentKitIndex !== -1) {
    for (let i = currentKitIndex; i < kits.length; i++) {
      nextBuy = {
        group: kits[i].group,
        amount: kits[i].subtotal + kits[i].scrap,
        unpriced: kits[i].unpriced,
      }
      break
    }
  }

  const hoursDone = sessions.slice(0, currentSession).reduce((acc, s) => acc + s.hours, 0)
  const hoursTotal = sessions.reduce((acc, s) => acc + s.hours, 0)
  const hoursKnown = sessions.every((s) => s.hoursKnown)

  const sessionsLeftInGroup = sessions
    .slice(currentSession)
    .filter((s) => s.group === currentGroup).length

  // the calendar is real hours plus the cure waits behind them: a planning placeholder (hoursKnown false) behind us makes it unknown
  let calendarHours: number | null = hoursDone
  for (let i = 0; i < currentSession; i++) {
    const s = sessions[i]
    if (!s.hoursKnown) {
      calendarHours = null
      break
    }
    if (s.cureAfter) {
      const wait = s.cureAfter.hours
      if (wait === null) {
        calendarHours = null
        break
      }
      calendarHours += wait
    }
  }

  return {
    spent,
    spentUnpriced,
    nextBuy,
    hoursDone,
    hoursTotal,
    hoursKnown,
    sessionsLeftInGroup,
    calendarHours,
  }
}
