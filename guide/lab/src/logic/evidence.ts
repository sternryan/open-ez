// What the bench may say about a sourced value (Contract 2: a sourced number shows its evidence). An official value shows its
// citation, a derived one its derivation note, a community one its link. A value flagged as sourced with no evidence on record
// is shown as an estimate: the flag alone is not evidence.

export interface Evidence {
  /** the flag the bench prints */
  flag: string
  /** how the evidence is shown: a citation, a derivation note, a link; null when there is none */
  kind: 'cite' | 'note' | 'link' | null
  text: string | null
}

const NONE = (flag: string): Evidence => ({ flag, kind: null, text: null })

export function evidenceOf(flag: string, source: string | null | undefined): Evidence {
  const s = typeof source === 'string' ? source.trim() : ''
  if (flag === 'official') return s ? { flag, kind: 'cite', text: s } : NONE('estimate')
  if (flag === 'derived') return s ? { flag, kind: 'note', text: s } : NONE('estimate')
  if (flag === 'community') return /^https?:\/\//.test(s) ? { flag, kind: 'link', text: s } : NONE('estimate')
  return NONE(flag)
}
