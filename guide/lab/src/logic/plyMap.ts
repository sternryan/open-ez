// Which drawn ply meshes a script's "ply N of T" lays. A script counts plies through the op's materials rows in order (ply 1 is the
// first ply of the first row, guide/scripts_schema.py _generated). The drawn plies carry the row they come from (cloth and `where`,
// the exported layup rows) and their lay order in the op (what the scrubber counts). Each authored ply is matched to its own rows'
// meshes, never to whatever mesh sits at the same proportion of the op: a row the model does not draw (an excluded pad, an
// undimensioned extra ply) has no mesh, and its plies play caption-only (`lay: null`) with the reason said in the caption.

export interface MaterialRow { cloth: string; plies: number; where: string }

export interface DrawnPly {
  /** mesh name (the layup node) */
  name: string
  /** the part or component the ply lies on */
  part: string
  cloth: string
  where: string
  /** 1-based lay order within its op */
  opOrder: number
}

export interface PlyTarget {
  /** the script's 1-based ply number */
  ply: number
  cloth: string
  where: string
  /** the drawn meshes this ply is, one per part it covers (sorted by lay order); empty when the model does not draw it */
  meshes: string[]
  /** the scrubber position that shows exactly the plies up to and including this one; null: play it caption-only */
  lay: number | null
  /** why it is caption-only (null when it is drawn) */
  why: string | null
}

const plyCount = (n: unknown): number => (typeof n === 'number' && Number.isInteger(n) && n > 0 ? n : 0)

/**
 * One target per authored ply (index = ply - 1). Rows are matched on cloth and `where`; within a row the k-th ply on each part is the
 * k-th of that part's matching meshes in lay order, so a row of two plies over three parts is two plies of three meshes each. A
 * target gets a scrubber position only if its meshes are exactly the next ones in lay order after everything already shown; any
 * other arrangement cannot be shown by the scrubber without showing a different ply, so it plays caption-only.
 */
export function mapPlies(materials: readonly MaterialRow[] | undefined, drawn: readonly DrawnPly[]): PlyTarget[] {
  const pool = new Map<string, Map<string, DrawnPly[]>>() // cloth|where -> part -> meshes in lay order
  for (const d of [...drawn].sort((a, b) => a.opOrder - b.opOrder)) {
    const key = `${d.cloth}|${d.where}`
    let parts = pool.get(key)
    if (!parts) pool.set(key, (parts = new Map()))
    let list = parts.get(d.part)
    if (!list) parts.set(d.part, (list = []))
    list.push(d)
  }
  const used = new Map<string, number>() // cloth|where|part -> meshes taken so far
  const out: PlyTarget[] = []
  let shown = 0 // the scrubber position after the last drawn ply
  for (const row of materials ?? []) {
    const n = plyCount(row.plies)
    const key = `${row.cloth}|${row.where}`
    for (let i = 0; i < n; i++) {
      const ply = out.length + 1
      const taken: DrawnPly[] = []
      for (const [part, list] of pool.get(key) ?? []) {
        const k = `${key}|${part}`
        const j = used.get(k) ?? 0
        if (j < list.length) { taken.push(list[j]); used.set(k, j + 1) }
      }
      taken.sort((a, b) => a.opOrder - b.opOrder)
      const meshes = taken.map((t) => t.name)
      if (!taken.length) { out.push({ ply, cloth: row.cloth, where: row.where, meshes, lay: null, why: 'not drawn in the model' }); continue }
      const orders = taken.map((t) => t.opOrder)
      const next = orders.every((o, idx) => o === shown + idx + 1)
      if (next) { shown += taken.length; out.push({ ply, cloth: row.cloth, where: row.where, meshes, lay: shown, why: null }) }
      else out.push({ ply, cloth: row.cloth, where: row.where, meshes, lay: null, why: 'drawn out of lay order' })
    }
  }
  return out
}

/** The drawn plies of an op that no authored ply claims (a stand-in mesh for many plies): they stay as drawn, never re-labelled. */
export function unclaimed(targets: readonly PlyTarget[], drawn: readonly DrawnPly[]): DrawnPly[] {
  const names = new Set(targets.flatMap((t) => t.meshes))
  return drawn.filter((d) => !names.has(d.name))
}

export interface PlyPlan {
  targets: PlyTarget[]
  /**
   * The op's drawn plies are a representational stand-in, not ply by ply (some drawn ply belongs to no authored row, or the drawn
   * order cannot follow the script): the whole layup stays drawn through the step and every ply beat plays caption-only.
   */
  standIn: boolean
}

export function plyPlan(materials: readonly MaterialRow[] | undefined, drawn: readonly DrawnPly[]): PlyPlan {
  const targets = mapPlies(materials, drawn)
  const standIn = drawn.length > 0 && (unclaimed(targets, drawn).length > 0 || targets.some((t) => t.why === 'drawn out of lay order'))
  if (!standIn) return { targets, standIn }
  const why = `the model draws this layup as ${drawn.length} representational ${drawn.length === 1 ? 'ply' : 'plies'}, not ply by ply`
  return { targets: targets.map((t) => ({ ...t, meshes: [], lay: null, why })), standIn }
}

/** The caption suffix for a ply: its cloth and row, and (when the model does not show it on its own geometry) why. */
export function plyNote(t: PlyTarget | undefined): string {
  if (!t) return ''
  return t.lay === null ? ` · ${t.cloth}, ${t.where} (${t.why}; caption only)` : ` · ${t.cloth}, ${t.where}`
}
