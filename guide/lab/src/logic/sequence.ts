// Roncz-only build sequence. A later wave fills the bodies.

import type { GraphLite, Op } from './graph'
import type { PlanStep } from './sessions'

export const GU_NOTE = 'The 1980 plans built the GU canard. This build uses the Roncz.'

/** Group id phase 2 must use for the canard. */
export const CANARD_GROUP = 'canard'

export interface SeqGroup {
  id: string
  label: string
  steps: Op[]
}

export function buildSequence(graph: GraphLite, groups: { id: string; label: string }[]): SeqGroup[] {
  const ops = graph.order
    .map((id) => graph.ops.find((o) => o.id === id))
    .filter((o): o is Op => !!o && (o.variants.includes('both') || o.variants.includes('roncz')) && !o.stub)

  return groups.map((g) => ({
    id: g.id,
    label: g.label,
    steps: ops.filter((o) => o.group === g.id),
  }))
}

export function noteFor(seq: SeqGroup[], opId: string): string | null {
  const group = seq.find((g) => g.id === CANARD_GROUP)
  if (!group || group.steps.length === 0) return null
  if (group.steps[0].id === opId) return GU_NOTE
  return null
}

export function toPlanSteps(seq: SeqGroup[]): PlanStep[] {
  return seq.flatMap((g) =>
    g.steps.map((op) => ({
      id: op.id,
      group: g.id,
      hours: op.plan?.hours?.value ?? null,
      people: op.plan?.people ?? 1,
      cure: op.plan?.cure ?? 'none',
      resin: op.plan?.resin ?? null,
    })),
  )
}
