// Ported from guide/viewer/js/build.js; same semantics and error messages, typed. Guarded by tests/build.test.ts (the 2.1 cases verbatim).
import { visibleOps, type GraphLite } from './graph'

export type BuildState = 'built' | 'current' | 'ghost' | 'hidden'
/** A merged mesh: named by its ply node, or by its component when it has no plies. */
export interface MeshInfo { name: string; component: string; ply: { op: string; order: number } | null }

export function firstOp(graph: GraphLite, variant: string): Map<string, string> {
  const m = new Map<string, string>()
  for (const o of visibleOps(graph, variant)) {
    for (const c of o.components) if (!m.has(c)) m.set(c, o.id)
  }
  return m
}

/** What each mesh looks like while `opId` is selected with plies 1..layIndex laid. Recomputed from scratch on every change. */
export function visibleSet(graph: GraphLite, variant: string, opId: string, layIndex: number, meshes: MeshInfo[]): Map<string, BuildState> {
  const idx = new Map(visibleOps(graph, variant).map((o, i) => [o.id, i]))
  const first = firstOp(graph, variant)
  const cur = idx.get(opId)
  if (cur === undefined) throw new Error(`op not in variant: ${opId}`)
  const known = new Set(graph.ops.map((o) => o.id))
  const owned = new Set(graph.ops.flatMap((o) => o.components))
  const later: BuildState = graph.__ghost ? 'ghost' : 'hidden'
  const out = new Map<string, BuildState>()
  for (const m of meshes) {
    const unowned = m.ply ? !known.has(m.ply.op) : !owned.has(m.component)
    if (unowned) throw new Error(`unowned mesh ${m.name}`)
    const op = m.ply ? m.ply.op : first.get(m.component)
    const i = op === undefined ? undefined : idx.get(op)
    if (i === undefined) out.set(m.name, 'hidden')
    else if (i < cur) out.set(m.name, 'built')
    else if (i === cur && (!m.ply || m.ply.order <= layIndex)) out.set(m.name, 'current')
    else out.set(m.name, later)
  }
  return out
}

// A part exists once ANY of its meshes is built or current (plies lie over one op: the first laid ply means the part exists).
// A component's meshes are named by the component id, or by its ply nodes (`<cid>.p<n>`). A part with no mesh in `state` does not exist.
// `state` is what visibleSet returns (a Map of mesh name -> state) or the same as a plain object.
export function pathVisible(path: { parts: string[] }, state: Map<string, string> | Record<string, string> | null | undefined): boolean {
  const get: [string, string][] = state instanceof Map ? [...state] : Object.entries(state ?? {})
  const exists = (cid: string) => get.some(([name, s]) => (name === cid || (name.startsWith(cid + '.p') && /^\d+$/.test(name.slice(cid.length + 2)))) && (s === 'built' || s === 'current'))
  return path.parts.length > 0 && path.parts.every(exists)
}
