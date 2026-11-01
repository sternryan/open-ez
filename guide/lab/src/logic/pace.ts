// Builder pace scales known estimated step hours in the lab, before sessions are packed.
// The graph keeps the logged hours. Owner actuals are applied after this and are not scaled.
// 0.653 is the ratio of two builders' logs on the chapters both recorded (GLANTZ 492 h, SPOD 753 h).
import type { Storage2 } from './graph'
import type { PlanStep } from './sessions'

/** localStorage key, beside longez.env. Never sent. */
export const PACE_KEY = 'longez.pace'

/** Long-EZ builder pace: GLANTZ / SPOD on the shared chapters, as stated (492 / 753 ≈ 0.653). */
export const PACE_LONG_EZ = 0.653

export const PACE_MIN = 0.25
export const PACE_MAX = 3

/** Visible mark on a hours figure that was multiplied. A logged number does not carry it. */
export const PACE_QUALIFIER = 'pace-scaled'

export type PaceChoice = 'logged' | 'longez' | 'custom'

export interface Pace {
  choice: PaceChoice
  /** Finite multiplier. 1 leaves every estimate as logged. */
  m: number
}

export const DEFAULT_PACE: Pace = { choice: 'logged', m: 1 }

export const PACE_LABELS: Record<PaceChoice, string> = {
  logged: 'As logged',
  // This control sits in #navlog. Spec §4c and contract 10 keep the plans chapter in the bench
  // source line, so the label says "sections" for the same overlap (GLANTZ 492 h / SPOD 753 h).
  longez: "Long-EZ builder pace, x0.653 (derived: ratio of two builders' logs on the sections both recorded)",
  custom: 'Custom',
}

const inCustomRange = (v: unknown): v is number =>
  typeof v === 'number' && Number.isFinite(v) && v >= PACE_MIN && v <= PACE_MAX

/** The stored pace, or As logged when storage is missing, blocked, or not a whole valid pace. */
export function loadPace(storage: Storage2 | null): Pace {
  try {
    const raw = storage?.getItem(PACE_KEY)
    if (!raw) return { ...DEFAULT_PACE }
    const v = JSON.parse(raw) as unknown
    if (!v || typeof v !== 'object' || Array.isArray(v)) return { ...DEFAULT_PACE }
    const o = v as Record<string, unknown>
    if (o.choice === 'logged') return { choice: 'logged', m: 1 }
    if (o.choice === 'longez') return { choice: 'longez', m: PACE_LONG_EZ }
    if (o.choice === 'custom' && inCustomRange(o.m)) return { choice: 'custom', m: o.m }
  } catch { /* blocked storage or invalid JSON */ }
  return { ...DEFAULT_PACE }
}

/** Write the pace under longez.pace. A null or blocked store is a no-op. Nothing is fetched. */
export function savePace(storage: Storage2 | null, pace: Pace): void {
  try {
    const clean: Pace | null = pace.choice === 'logged'
      ? { choice: 'logged', m: 1 }
      : pace.choice === 'longez'
        ? { choice: 'longez', m: PACE_LONG_EZ }
        : inCustomRange(pace.m)
          ? { choice: 'custom', m: pace.m }
          : null
    if (!clean) return
    storage?.setItem(PACE_KEY, JSON.stringify({ choice: clean.choice, m: clean.m }))
  } catch { /* per-viewer convenience only; never sent */ }
}

/** A custom multiplier in range, or `previous` itself when the value is rejected. */
export function withCustomPace(previous: Pace, raw: unknown): Pace {
  const n = typeof raw === 'number' ? raw : typeof raw === 'string' ? Number(raw) : Number.NaN
  if (!inCustomRange(n)) return previous
  return { choice: 'custom', m: n }
}

/** Known estimated hours times m. Null stays null. Never writes NaN. Does not mutate `steps`. */
export function applyPace(steps: PlanStep[], m: number): PlanStep[] {
  const scale = Number.isFinite(m) && m !== 1
  return steps.map((s) => {
    if (typeof s.hours !== 'number' || !Number.isFinite(s.hours)) return { ...s, hours: null }
    if (!scale) return { ...s }
    const hours = s.hours * m
    return { ...s, hours: Number.isFinite(hours) ? hours : null }
  })
}

/**
 * Step ids whose estimated hours applyPace will multiply.
 * An owner actual is not in the set: that hour is what happened.
 * Unknown hours are not in the set. m = 1 scales nothing.
 */
export function scaledEstimateIds(
  steps: PlanStep[],
  actuals: Record<string, { hours?: number }>,
  m: number,
): Set<string> {
  const ids = new Set<string>()
  if (!Number.isFinite(m) || m === 1) return ids
  for (const s of steps) {
    const logged = actuals[s.id]?.hours
    if (typeof logged === 'number' && Number.isFinite(logged)) continue
    if (typeof s.hours === 'number' && Number.isFinite(s.hours)) ids.add(s.id)
  }
  return ids
}
