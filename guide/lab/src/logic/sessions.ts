// Greedy session packer. A later wave fills the body.

import { type Env, type ResinLite, cureGateHours } from './cure'

export interface PlanStep {
  id: string
  group: string
  hours: number | null
  people: 1 | 2
  cure: 'none' | 'part' | 'all'
  resin: string | null
}

export interface Session {
  index: number
  group: string
  steps: string[]
  hours: number
  hoursKnown: boolean
  buddy: boolean
  cureAfter: { hours: number | null; scope: 'part' | 'all' } | null
}

export function packSessions(
  steps: PlanStep[],
  resins: Record<string, ResinLite>,
  env: Env,
  sessionHours = 4,
): Session[] {
  const sessions: Session[] = []
  let current: Session | null = null

  for (const step of steps) {
    const stepHours = step.hours ?? 1
    const stepIsUnknown = step.hours === null

    if (current) {
      if (step.group !== current.group || current.hours + stepHours > sessionHours) {
        sessions.push(current)
        current = null
      }
    }

    if (!current) {
      current = {
        index: 0,
        group: step.group,
        steps: [step.id],
        hours: stepHours,
        hoursKnown: !stepIsUnknown,
        buddy: step.people === 2,
        cureAfter: null,
      }
    } else {
      current.steps.push(step.id)
      current.hours += stepHours
      if (stepIsUnknown) current.hoursKnown = false
      if (step.people === 2) current.buddy = true
    }

    if (step.cure !== 'none' && current) {
      const resin = step.resin ? resins[step.resin] : null
      const gate = resin ? cureGateHours(resin, env) : null
      current.cureAfter = { hours: gate, scope: step.cure }
      sessions.push(current)
      current = null
    }
  }

  if (current) {
    sessions.push(current)
  }

  return sessions.map((s, i) => ({ ...s, index: i }))
}
