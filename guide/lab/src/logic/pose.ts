import { visibleOps, type GraphLite } from './graph'

export type Pose = 'inverted' | 'upright'

/**
 * Chapter 30 assembles the Roncz canard in the jigs with the bottom spar cap and bottom skin laid while it is upside down
 * (bottom surface up). This op lifts it off the jigs and sets it right side up, so every Roncz op before it is 'inverted'.
 */
export const TURNOVER_OP = 'r30.turnover-twist-check'

/** Which way up the canard sits in the jig for an op. GU, and any variant without the turnover op, is always upright. */
export function orientation(graph: GraphLite, variant: string, opId: string | null): Pose {
  if (variant !== 'roncz' || !opId) return 'upright'
  const order = visibleOps(graph, variant).map((o) => o.id)
  const turn = order.indexOf(TURNOVER_OP)
  const at = order.indexOf(opId)
  if (turn < 0 || at < 0) return 'upright'
  return at < turn ? 'inverted' : 'upright'
}
