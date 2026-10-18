// Decision records and the skin the Hangar shows. Pure: no DOM, no fetch.

export type Spot = {
  id: string
  label: string
  analogue: string
  state: string
  blurb: string
}

export type OptionFact = { text: string; cite?: string; flag?: string }

export type Option = {
  id: string
  label: string
  kind: string
  facts: OptionFact[]
  why: string
}

export type Position = {
  role: string
  option: string
  confidence: string
  reasoning: string
  citations: string[]
  judgment: boolean
}

/** A gap no source fills. `text` (or `what`) is the gap; `how` is how it would be found. */
export type Unknown = { text?: string; what?: string; how?: string }

export type Decision = { option: string; date: string; reason: string }

export type HistoryEntry = { date: string; from: string; to: string; reason: string }

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
  recommendation: string | null
  why: string | null
  confidence: string | null
  disagreements: string[]
  unknowns: string[]
}

const CONFIDENCE_RANK: Record<string, number> = { low: 0, medium: 1, high: 2 }

/** Open and reopened records wait. A decided record names the briefing that last closed it. */
export function statusLabel(r: DecisionRecord): string {
  if (r.status !== 'decided') return 'awaiting briefing'
  const decided = (r.history ?? []).filter((h) => h.to === 'decided')
  const last = decided[decided.length - 1]
  if (!last) return 'decided in briefing 1'
  const ordered = [...decided].sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))
  return `decided in briefing ${ordered.indexOf(last) + 1}`
}

function unknownLine(u: Unknown): string {
  const text = (u.text ?? u.what ?? '').trim()
  const how = (u.how ?? '').trim()
  if (text && how) return `${text} — ${how}`
  return text || how
}

/**
 * The owner's skin: the option most advisors picked, their why and confidence,
 * the dissenters' reasoning, and the unknowns. No positions means no recommendation.
 */
export function skin(r: DecisionRecord): Skin {
  const unknowns = (r.unknowns ?? []).map(unknownLine).filter((s) => s.length > 0)
  const positions = r.positions ?? []
  if (positions.length === 0) {
    return { recommendation: null, why: null, confidence: null, disagreements: [], unknowns }
  }
  const counts = new Map<string, number>()
  for (const p of positions) counts.set(p.option, (counts.get(p.option) ?? 0) + 1)
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
  if (best === null || tied) {
    return { recommendation: null, why: null, confidence: null, disagreements: [], unknowns }
  }
  const winners = positions.filter((p) => p.option === best)
  let confidence = winners[0]?.confidence ?? null
  let low = Infinity
  for (const p of winners) {
    const rank = CONFIDENCE_RANK[p.confidence] ?? 0
    if (rank < low) {
      low = rank
      confidence = p.confidence in CONFIDENCE_RANK ? p.confidence : 'low'
    }
  }
  const why = winners.map((p) => p.reasoning).filter((s) => s.length > 0).join(' ')
  return {
    recommendation: best,
    why: why || null,
    confidence,
    disagreements: positions.filter((p) => p.option !== best).map((p) => p.reasoning),
    unknowns,
  }
}
