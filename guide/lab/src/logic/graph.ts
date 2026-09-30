// Ported from guide/viewer/js/graph.js (visibleOps, makeStore); same behaviour, typed.

export interface Op {
  id: string
  chapter: number
  title: string
  summary: string
  variants: string[]
  completion?: string[]
  stub?: boolean
}
export interface GraphLite {
  ops: Op[]
  order: string[]
  tours?: Record<string, { target: [number, number, number]; position: [number, number, number] }>
}
export type Variant = 'roncz' | 'gu'

export function visibleOps(graph: GraphLite, variant: string): Op[] {
  const byId = new Map(graph.ops.map((o) => [o.id, o]))
  return graph.order
    .map((id) => byId.get(id))
    .filter((o): o is Op => !!o && (o.variants.includes('both') || o.variants.includes(variant)))
}

/** Reference chapters (the plans' cover, layup skills, fuselage) are not part of the canard build. */
const NON_CANARD = new Set([0, 3, 6])

/**
 * The ops the bottom bar shows: the variant's canard build chapters, in graph order.
 * Stubs (ops with no written text yet) are omitted, not dimmed: a chip that opens an empty card is worse than no chip.
 */
export function barOps(graph: GraphLite, variant: string): Op[] {
  return visibleOps(graph, variant).filter((o) => !NON_CANARD.has(o.chapter) && !o.stub)
}

interface Storage2 { getItem(k: string): string | null; setItem(k: string, v: string): void }

export function makeStore(storage: Storage2) {
  const mem = new Map<string, Set<number>>()
  const key = (id: string) => `longez.check.${id}`
  const get = (opId: string): Set<number> => {
    if (!mem.has(opId)) {
      let v: number[] = []
      try {
        const p = JSON.parse(storage.getItem(key(opId)) || '[]')
        if (Array.isArray(p)) v = p.filter(Number.isInteger)
      } catch { /* storage blocked or invalid JSON */ }
      mem.set(opId, new Set(v))
    }
    return mem.get(opId)!
  }
  return {
    get,
    toggle(opId: string, i: number) {
      const s = get(opId)
      if (s.has(i)) s.delete(i); else s.add(i)
      try { storage.setItem(key(opId), JSON.stringify([...s])) } catch { /* keep in memory */ }
    },
  }
}
