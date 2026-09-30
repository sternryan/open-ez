// Which composite material a mesh gets. Pure (no three.js): the mapping is tested against the real layup export.

export type MaterialKind = 'foam' | 'und' | 'bid' | 'part'

export interface LayupNodeLite {
  cloth?: string
  order?: number
  orientation?: string
  component?: string
}

export interface MaterialSpec {
  kind: MaterialKind
  /** Fibre direction(s) in degrees from the span axis, in the ply's own plane. UND has one, BID two (warp, weft). */
  angles: number[]
  ply?: { node: string; order: number; cloth: 'UND' | 'BID' }
}

/** Degrees from the span axis for the ply's first tow direction. `order` is the ply's layup order (1-based). */
function towAngle(orientation: string, order: number): number {
  switch (orientation) {
    case 'spanwise': return 0
    case '45 degrees': return 45
    case 'crossed': return order % 2 === 1 ? 45 : -45 // shear web UND alternates +45 / -45 by ply order
    default: throw new Error(`unknown ply orientation "${orientation}"`)
  }
}

export function materialFor(node: string | null, component: string, layupNodes?: Record<string, LayupNodeLite> | null): MaterialSpec {
  if (!node) return component === 'canard.core' ? { kind: 'foam', angles: [] } : { kind: 'part', angles: [] }
  const n = layupNodes?.[node]
  if (!n) throw new Error(`ply ${node} is not in the layup`)
  const order = n.order ?? 0
  const a = towAngle(n.orientation ?? '', order)
  if (n.cloth === 'UND') return { kind: 'und', angles: [a], ply: { node, order, cloth: 'UND' } }
  if (n.cloth === 'BID') return { kind: 'bid', angles: [a, a - 90], ply: { node, order, cloth: 'BID' } }
  throw new Error(`unknown cloth "${n.cloth}" on ${node}`)
}
