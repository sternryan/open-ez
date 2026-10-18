// Decision records and the skin the Hangar shows. Pure: no DOM, no fetch.

export type Spot = {
  id: string
  label: string
  analogue: string
  state: string
  blurb: string
}

export type OptionFact = { text: string; cite?: string; flag?: string }

/** A fuel-path consequence: which tank resin that option forces, and where that claim comes from. */
export type Implies = { tank_resin: string; cite?: string; flag?: string }

export type Option = {
  id: string
  label: string
  kind: string
  facts: OptionFact[]
  why: string
  implies?: Implies
}

/** One axis of a decision. `options` are option ids, in display order. */
export type Axis = { id: string; options: string[] }

export type Position = {
  role: string
  picks: Record<string, string>
  confidence: string
  reasoning: string
  citations: string[]
  judgment: boolean
}

/** A gap no source fills. `text` (or `what`) is the gap; `how` is how it would be found. */
export type Unknown = { text?: string; what?: string; how?: string }

export type Decision = { picks: Record<string, string>; date: string; reason: string }

export type HistoryEntry = {
  date: string
  from: string
  to: string
  reason: string
  /** Present when `to` is `decided`: the option id chosen on each axis. */
  picks?: Record<string, string>
}

export type Evidence = {
  paper: string
  material: string
  outside_review: string
  flight: string
}

export type DecisionRecord = {
  id: string
  spot: string
  title: string
  status: string
  question: string
  coupled_with: string[]
  replaces: string[]
  book_choice: Record<string, unknown>
  axes: Axis[]
  options: Option[]
  positions: Position[]
  unknowns: Unknown[]
  mission_score: unknown
  decision: Decision | null
  history: HistoryEntry[]
  changes: Record<string, unknown> | null
  evidence: Evidence
}

export type HangarData = {
  spots: Spot[]
  records: Record<string, DecisionRecord>
}

export type Skin = {
  /** Winning option ids in axis order, joined with ` + `. Null when no axis has a majority. */
  recommendation: string | null
  /** Majority option id per axis. A tie, or no picks on that axis, is null. */
  recommendations: Record<string, string | null>
  why: string | null
  confidence: string | null
  disagreements: string[]
  unknowns: string[]
}

/** An advisor's opinion is shown as opinion, never as a sourced fact. */
function labelled(p: Position): string {
  const t = typeof p.reasoning === 'string' ? p.reasoning : ''
  return p.judgment && t ? `(judgment) ${t}` : t
}

const CONFIDENCE_RANK: Record<string, number> = { low: 0, medium: 1, high: 2 }

/** Open and reopened records wait. A decided record names the briefing that last closed it. */
export function statusLabel(r: DecisionRecord): string {
  if (r.status !== 'decided') return 'awaiting briefing'
  // N counts the briefings that closed this record: a first decision is 1, a re-decision after a reopen is 2.
  const decided = (r.history ?? []).filter((h) => h.to === 'decided').length
  return `decided in briefing ${Math.max(1, decided)}`
}

function unknownLine(u: Unknown | string): string {
  if (typeof u === 'string') return u.trim()
  const text = (u.text ?? u.what ?? '').trim()
  const how = (u.how ?? '').trim()
  if (text && how) return `${text} — ${how}`
  return text || how
}

/** Unique highest count among positions that picked on this axis. A tie or no picks is null. */
function axisMajority(positions: Position[], axisId: string): string | null {
  const counts = new Map<string, number>()
  for (const p of positions) {
    const pick = p.picks?.[axisId]
    if (typeof pick !== 'string' || pick.length === 0) continue
    counts.set(pick, (counts.get(pick) ?? 0) + 1)
  }
  let best: string | null = null
  let bestN = 0
  let tied = false
  for (const [option, n] of counts) {
    if (n > bestN) {
      best = option
      bestN = n
      tied = false
    } else if (n === bestN) {
      tied = true
    }
  }
  if (best === null || tied) return null
  return best
}

function lowestConfidence(positions: Position[]): string | null {
  let confidence: string | null = null
  let low = Infinity
  for (const p of positions) {
    const rank = CONFIDENCE_RANK[p.confidence] ?? 0
    if (rank < low) {
      low = rank
      confidence = p.confidence in CONFIDENCE_RANK ? p.confidence : 'low'
    }
  }
  return confidence
}

/**
 * The owner's skin, one majority per axis. `recommendation` joins the winning
 * option ids with ` + ` in axis order. Advisors who match a winning pick supply
 * the why and the lowest confidence; advisors who picked against a winner on
 * some axis supply the disagreements. A fully tied council (no axis has a
 * majority) recommends nothing and shows every reasoning.
 */
export function skin(r: DecisionRecord): Skin {
  const unknowns = (r.unknowns ?? []).map(unknownLine).filter((s) => s.length > 0)
  const axes = r.axes ?? []
  const positions = r.positions ?? []
  const recommendations: Record<string, string | null> = {}
  for (const axis of axes) recommendations[axis.id] = axisMajority(positions, axis.id)
  const winning = axes
    .map((axis) => recommendations[axis.id])
    .filter((id): id is string => typeof id === 'string' && id.length > 0)
  const recommendation = winning.length > 0 ? winning.join(' + ') : null
  if (recommendation === null) {
    return {
      recommendation: null,
      recommendations,
      why: null,
      confidence: null,
      disagreements: positions.map(labelled).filter((t) => t.length > 0),
      unknowns,
    }
  }
  const agrees = (p: Position) =>
    axes.some((axis) => {
      const win = recommendations[axis.id]
      return typeof win === 'string' && p.picks?.[axis.id] === win
    })
  const dissents = (p: Position) =>
    axes.some((axis) => {
      const win = recommendations[axis.id]
      const pick = p.picks?.[axis.id]
      return typeof win === 'string' && typeof pick === 'string' && pick !== win
    })
  const winners = positions.filter(agrees)
  const why = winners.map(labelled).filter((s) => s.length > 0).join(' ')
  return {
    recommendation,
    recommendations,
    why: why || null,
    confidence: lowestConfidence(winners),
    disagreements: positions.filter(dissents).map(labelled).filter((s) => s.length > 0),
    unknowns,
  }
}
