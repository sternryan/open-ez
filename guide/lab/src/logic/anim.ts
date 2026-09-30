/**
 * The ply lay-down animation as a pure function. No clock, no scene: the caller passes the time since the lay index last changed.
 *
 * It derives its state from the same inputs as build.ts's visibleSet (the ply's op index against the current op index, and its
 * order against `lay`), so a ply can never animate before its op, and a ply of an earlier op is never wet.
 *
 * One ply, in time: it unrolls along the span over ROLL (dry white cloth), then the wet-out front sweeps along it over WET (dry
 * ahead of the front, resin behind it). A laid ply stays wet until the whole op cures. When the op is complete (lay === count)
 * every ply of it cures over CURE, starting once the last ply has finished its roll and wet-out.
 */
import type { BuildState } from './build'

export const ROLL = 1.2 // seconds to unroll one ply along the span
export const WET = 1.0 // seconds for the wet-out front to sweep along it
export const CURE = 1.5 // seconds for the completed op to go from wet to cured
export const DWELL = 0.35 // Play only: pause after a ply finishes before the next one starts
export const PLY_TIME = ROLL + WET
/** The time at which everything has settled. A step that opens fully built starts here. */
export const DONE_T = ROLL + WET + CURE

export interface PhaseInput {
  /** index (in the variant's visible ops) of the op this mesh belongs to; undefined when the op is outside the variant */
  meshOpIndex: number | undefined
  /** index of the selected op */
  curOpIndex: number
  /** the ply's order in its op, 1-based */
  order: number
  /** plies laid so far in the selected op */
  lay: number
  /** plies in the selected op */
  count: number
  /** seconds since `lay` last changed */
  t: number
  /** show future work as ghosts (as build.ts does) */
  ghost?: boolean
}
export interface Phase {
  state: BuildState
  /** 0..1 of the span (root to tip) that has been rolled out; the rest is not drawn */
  unroll: number
  /** 0..1 of the span, from the root, that the wet-out has reached; beyond it the cloth is dry */
  front: number
  /** 0 = still wet, 1 = fully cured (only meaningful behind the front) */
  cure: number
}

const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x)
const CURED: Phase = { state: 'built', unroll: 1, front: 1, cure: 1 }

/** The phase of a ply. `t` is clamped to [0, DONE_T], so the result is a pure function of (op, lay, t). */
export function plyPhase(p: PhaseInput): Phase {
  const t = Math.min(Math.max(Number.isFinite(p.t) ? p.t : DONE_T, 0), DONE_T)
  const i = p.meshOpIndex
  if (i === undefined) return { ...CURED, state: 'hidden' }
  if (i < p.curOpIndex) return { ...CURED } // an earlier op: built, cured, never wet
  if (i > p.curOpIndex || p.order > p.lay) return { ...CURED, state: p.ghost ? 'ghost' : 'hidden' } // not laid: nothing is wet
  // the current op, laid so far
  const cure = p.lay >= p.count ? clamp01((t - PLY_TIME) / CURE) : 0 // a wet layup stays wet until the whole op cures
  if (p.order < p.lay) return { state: 'current', unroll: 1, front: 1, cure }
  return { state: 'current', unroll: clamp01(t / ROLL), front: clamp01((t - ROLL) / WET), cure } // the ply being laid
}

/** A mesh with no plies (the core, a part) that follows its first op: built or current, always cured. */
export function partPhase(state: BuildState): Phase {
  return { state, unroll: 1, front: 1, cure: 1 }
}

/** Is any of this ply visibly wet right now? */
export const isWet = (ph: Phase): boolean => ph.state === 'current' && ph.front > 0 && ph.cure < 1

/** When the play sequence advances past the ply that is being laid (time since lay changed). */
export const PLAY_ADVANCE_T = PLY_TIME + DWELL
