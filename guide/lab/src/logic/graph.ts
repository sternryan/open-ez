// Ported from guide/viewer/js/graph.js (visibleOps, makeStore); same behaviour, typed.

/** Per-step plan as shipped on an op. Tuples in the Python plan are arrays here. */
export interface PlanJson {
  people?: 1 | 2
  people_why?: string | null
  hours?: { value: number | null; flag: string; source?: string | null } | null
  cure?: 'none' | 'part' | 'all'
  resin?: string | null
  tools?: string[]
  /** source: the buy's evidence (a citation, a derivation note or a link) when the build carries one */
  buy?: { item: string; qty: number; flag: string; source?: string | null }[]
}

export interface Op {
  id: string
  chapter: number
  title: string
  summary: string
  variants: string[]
  requires?: string[]
  completion?: string[]
  /** the op's own ply schedule (cloth, plies, where), where the research gives one */
  materials?: { cloth: string; plies: number; where: string }[]
  stub?: boolean
  components: string[]
  group?: string | null
  plan?: PlanJson | null
  /** registry citations; `scan_pp` maps to a plans page through graph.json `pages` (absent from a public build) */
  sources?: { doc: string; page?: string | null; scan_pp?: number | null }[]
}
export interface GraphLite {
  ops: Op[]
  order: string[]
  tours?: Record<string, { target: [number, number, number]; position: [number, number, number] }>
  /** view state, not graph data: show future work as ghosts (2.1 keeps it on the graph object too) */
  __ghost?: boolean
}
export type Variant = 'roncz' | 'gu'

export function visibleOps(graph: GraphLite, variant: string): Op[] {
  const byId = new Map(graph.ops.map((o) => [o.id, o]))
  return graph.order
    .map((id) => byId.get(id))
    .filter((o): o is Op => !!o && (o.variants.includes('both') || o.variants.includes(variant)))
}

/**
 * Reference chapters (the plans' cover, layup skills) and the fuselage, gear and nose chapters (4-9, 13) and the spar, firewall, controls and trim chapters (14-17) are not part of the canard build.
 * Chapter 12 (the canard's installation: drilling F22, the bushings, the permanent F28 pins) is work done on the fuselage, so it is the
 * fuselage subject's. Chapter 11 (the elevators) stays on the canard's bar.
 */
const NON_CANARD = new Set([0, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26])

/**
 * The ops the bottom bar shows: the variant's canard build chapters, in graph order.
 * Stubs (ops with no written text yet) are omitted, not dimmed: a chip that opens an empty card is worse than no chip.
 */
export function barOps(graph: GraphLite, variant: string): Op[] {
  return visibleOps(graph, variant).filter((o) => !NON_CANARD.has(o.chapter) && !o.stub)
}

export interface Storage2 { getItem(k: string): string | null; setItem(k: string, v: string): void }

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

/** plan.json as guide/build_site.py ships it (contract 5): groups, resins, catalog, step scripts and the build date. */
export interface PlanFile {
  groups: { id: string; label: string }[]
  resins: Record<string, { min_temp_c: number | null; gate_hours: [number, number][]; flag: string; source: string | null }>
  catalog: Record<string, { label: string; url: string | null; price_usd: number | null; unit: string; flag: string; read: string | null; stale: boolean }>
  /** op id -> actions (logic/actions.ts Action); generated ply actions with the authored overrides applied */
  scripts: Record<string, { do: string; part?: string; ply?: number; tool?: string; who: 'owner' | 'buddy'; why?: string }[]>
  today: string
}
