// Owner actuals: logged hours and receipts override estimates.
// Stored only under longez.actuals. Never sent and never committed (spec §9).

import type { Storage2 } from './graph'
import type { PlanStep } from './sessions'

export interface Actual {
  hours?: number
  spentUsd?: number
}

/** localStorage key. Never sent and never committed. */
export const ACTUALS_KEY = 'longez.actuals'

/** Zero is valid. Negatives, NaN and infinities are not. */
const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v) && v >= 0

/** A stored entry with a bad hours or receipt field is dropped whole. A negative is a bad field. An empty entry is dropped. */
function readActual(v: unknown): Actual | undefined {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return undefined
  const o = v as Record<string, unknown>
  if ('hours' in o && !finite(o.hours)) return undefined
  if ('spentUsd' in o && !finite(o.spentUsd)) return undefined
  const out: Actual = {}
  if (finite(o.hours)) out.hours = o.hours
  if (finite(o.spentUsd)) out.spentUsd = o.spentUsd
  return out.hours === undefined && out.spentUsd === undefined ? undefined : out
}

/** The stored map, or {} when storage is missing, blocked, or not a map of actuals. Invalid entries are dropped. */
export function loadActuals(storage: Storage2 | null): Record<string, Actual> {
  try {
    const raw = storage?.getItem(ACTUALS_KEY)
    if (!raw) return {}
    const v = JSON.parse(raw) as unknown
    if (!v || typeof v !== 'object' || Array.isArray(v)) return {}
    const out: Record<string, Actual> = {}
    for (const id of Object.keys(v as Record<string, unknown>)) {
      const a = readActual((v as Record<string, unknown>)[id])
      if (a) out[id] = a
    }
    return out
  } catch {
    return {}
  }
}

/** Write the map under longez.actuals. A null or blocked store is a no-op. Nothing is fetched. */
export function saveActuals(storage: Storage2 | null, actuals: Record<string, Actual>): void {
  try {
    const clean: Record<string, Actual> = {}
    for (const [id, a] of Object.entries(actuals)) {
      const one = readActual(a)
      if (one) clean[id] = one
    }
    storage?.setItem(ACTUALS_KEY, JSON.stringify(clean))
  } catch {
    /* per-viewer convenience only; never sent */
  }
}

/**
 * Logged hours replace that step's estimate and are known (including zero).
 * A missing or negative hours field keeps the estimate. Does not mutate `steps`.
 * Receipts are not hours: the meter applies those, per step.
 */
export function applyActuals(steps: PlanStep[], actuals: Record<string, Actual>): PlanStep[] {
  return steps.map((s) => {
    const h = actuals[s.id]?.hours
    if (!finite(h)) return { ...s }
    return { ...s, hours: h }
  })
}
