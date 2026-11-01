// Kit rollup and the planning meter. A receipt replaces that step's estimated buys once, and is not added on top.
// A step with no buys is still a member of its group: its receipt is counted once and nothing is subtracted.

import type { Actual } from './actuals'
import { isGroundGroup } from './ground'
import type { Session } from './sessions'

export interface Kit {
  group: string
  lines: { item: string; qty: number; unitPrice: number | null; stale: boolean; step?: string }[]
  subtotal: number
  scrap: number
  unpriced: number
}

/** Scrap and mixing loss, applied once at kit level. */
export const SCRAP = 0.25

export function kitsFor(
  groups: string[],
  buysByGroup: Record<string, { item: string; qty: number; step?: string }[]>,
  catalog: Record<string, { price_usd: number | null; stale: boolean }>,
): Kit[] {
  return groups.map((group) => {
    const buys = buysByGroup[group] ?? []
    // Same item on the same step merges. A step id is kept so a receipt can replace that step only.
    const merged: { item: string; qty: number; step?: string }[] = []
    for (const buy of buys) {
      const existing = merged.find((m) => m.item === buy.item && m.step === buy.step)
      if (existing) {
        existing.qty += buy.qty
      } else {
        merged.push(buy.step !== undefined ? { item: buy.item, qty: buy.qty, step: buy.step } : { item: buy.item, qty: buy.qty })
      }
    }

    const lines = merged.map((m) => {
      const entry = catalog[m.item]
      const line: Kit['lines'][number] = {
        item: m.item,
        qty: m.qty,
        unitPrice: entry?.price_usd ?? null,
        stale: entry?.stale ?? false,
      }
      if (m.step !== undefined) line.step = m.step
      return line
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
  /** kits from the current group onward, after receipts. null when this session's group is not in the kit list */
  remaining: number | null
  remainingUnpriced: number
  totalSessions: number
}

const receiptFor = (step: string | undefined, actuals: Record<string, Actual>): number | undefined => {
  if (!step) return undefined
  const v = actuals[step]?.spentUsd
  return typeof v === 'number' && Number.isFinite(v) ? v : undefined
}

/** Step ids in this group, once each. Membership comes from the sessions, not from buy lines. */
function stepsInGroup(sessions: Session[], group: string): string[] {
  const seen = new Set<string>()
  const ids: string[] = []
  for (const s of sessions) {
    if (s.group !== group) continue
    for (const id of s.steps) {
      if (seen.has(id)) continue
      seen.add(id)
      ids.push(id)
    }
  }
  return ids
}

/**
 * A kit's price after receipts. Each receipt counts once, for a step in the group. It replaces that
 * step's own lines (priced and unpriced) and is not scrapped. A step with no buys has nothing to
 * subtract, so the receipt is added. Scrap stays on the estimated priced lines only.
 * No receipt: the kit's own subtotal, scrap and unpriced.
 */
function priceKit(kit: Kit, actuals: Record<string, Actual>, memberSteps: readonly string[]): { amount: number; unpriced: number } {
  const members = new Set<string>(memberSteps)
  for (const line of kit.lines) {
    if (line.step) members.add(line.step)
  }
  const replaced = new Set<string>()
  for (const step of members) {
    if (receiptFor(step, actuals) !== undefined) replaced.add(step)
  }
  if (replaced.size === 0) return { amount: kit.subtotal + kit.scrap, unpriced: kit.unpriced }

  let estimated = 0
  let unpriced = 0
  for (const line of kit.lines) {
    if (line.step && replaced.has(line.step)) continue
    if (line.unitPrice === null || !Number.isFinite(line.unitPrice) || !Number.isFinite(line.qty)) {
      unpriced += 1
      continue
    }
    estimated += line.qty * line.unitPrice
  }
  let receipts = 0
  for (const step of replaced) {
    const receipt = receiptFor(step, actuals)
    if (receipt !== undefined) receipts += receipt
  }
  return { amount: receipts + estimated + estimated * SCRAP, unpriced }
}

export function meterAt(
  sessions: Session[],
  kits: Kit[],
  currentSession: number,
  actuals: Record<string, Actual> = {},
  view: { groundSkipped?: boolean } = {},
): Meter {
  const currentGroup = sessions[currentSession].group
  const currentKitIndex = kits.findIndex((k) => k.group === currentGroup)
  // Skip changes the step on screen. Ground lessons behind that step were not bought or spent,
  // and their kit stays in the remaining estimate. A real start still counts them.
  const skipGround = view.groundSkipped === true
  const doneGroup = (group: string) => !(skipGround && isGroundGroup(group))

  let spent: number | null = null
  let spentUnpriced = 0

  const priced = (kit: Kit) => priceKit(kit, actuals, stepsInGroup(sessions, kit.group))

  if (currentKitIndex > 0) {
    for (let i = 0; i < currentKitIndex; i++) {
      if (!doneGroup(kits[i].group)) continue
      const p = priced(kits[i])
      if (spent === null) spent = 0
      spent += p.amount
      spentUnpriced += p.unpriced
    }
  }

  let nextBuy: { group: string; amount: number; unpriced: number } | null = null
  let remaining: number | null = null
  let remainingUnpriced = 0
  if (currentKitIndex !== -1) {
    const here = priced(kits[currentKitIndex])
    nextBuy = { group: kits[currentKitIndex].group, amount: here.amount, unpriced: here.unpriced }
    remaining = 0
    if (skipGround) {
      for (let i = 0; i < currentKitIndex; i++) {
        if (!isGroundGroup(kits[i].group)) continue
        const p = priced(kits[i])
        remaining += p.amount
        remainingUnpriced += p.unpriced
      }
    }
    for (let i = currentKitIndex; i < kits.length; i++) {
      const p = priced(kits[i])
      remaining += p.amount
      remainingUnpriced += p.unpriced
    }
  }

  const hoursDone = sessions.slice(0, currentSession).reduce((acc, s) => acc + (doneGroup(s.group) ? s.hours : 0), 0)
  const hoursTotal = sessions.reduce((acc, s) => acc + s.hours, 0)
  const hoursKnown = sessions.every((s) => s.hoursKnown)

  const sessionsLeftInGroup = sessions
    .slice(currentSession)
    .filter((s) => s.group === currentGroup).length

  // the calendar is real hours plus the cure waits behind them: a planning placeholder (hoursKnown false) behind us makes it unknown.
  // A skipped ground lesson is not behind us as work, so its placeholder does not blank the calendar.
  let calendarHours: number | null = hoursDone
  for (let i = 0; i < currentSession; i++) {
    const s = sessions[i]
    if (!doneGroup(s.group)) continue
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
    remaining,
    remainingUnpriced,
    totalSessions: sessions.length,
  }
}
