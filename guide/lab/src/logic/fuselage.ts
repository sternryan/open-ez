/**
 * The fuselage box (plans chapters 4-6) as a lab subject. Pure: no three.js, no DOM.
 *
 * The data comes from layup.json's "fuselage" section (guide/fuselage_export.py): one entry per part (its fidelity, label and FS
 * extent) and one per ply (its op, lay order in the op, stack on its face, cloth, orientation and FS extent). Frame as exported,
 * inches: x = FS, y = B.L., z = W.L. - 17.4.
 *
 * Where each part is, per op:
 *   chapter 4  the bulkheads are made flat on the layup table, the face being glassed up;
 *   chapter 5  the sides lie flat on the table, inside face up, and get their plies (the bulkheads wait on the table);
 *   chapter 6  the sides stand upside down on the jig blocks (the book builds the box inverted), the bulkheads go in one op at a
 *              time in the book's order, the bottom is fitted on the box, lifted off for its inside glass, and bonded with the box
 *              turned right side up.
 */
import { visibleOps, type GraphLite, type Op } from './graph'

export type Subject = 'canard' | 'fuselage'
export const SUBJECTS: Subject[] = ['canard', 'fuselage']
export const SUBJECT_KEY = 'longez.subject'
export const parseSubject = (s: string | null | undefined): Subject => (s === 'fuselage' ? 'fuselage' : 'canard')

export const FUSE_CHAPTERS = new Set([4, 5, 6])

export type Fidelity = 'book' | 'derived' | 'representational'
export interface FusePartRow { node: string; component: string; fidelity: Fidelity; label: string; cite: string[]; fs_min: number; fs_max: number; fwd_normal?: number[] | null }
export interface FusePlyRow {
  part: string; component: string; op: string; op_index: number
  /** 1-based lay order within its op (what the scrubber counts) */
  op_order: number
  /** order of the ply on its part across ops */
  order: number
  /** 1-based position in the stack on its face */
  stack: number
  cloth: string; orientation_deg: number | null; where: string; region: string; fidelity: Fidelity; lower_bound: boolean; area_in2: number
  fs_min: number; fs_max: number
}
export interface FuseLayup {
  chapters: number[]; ops: string[]; parts: Record<string, FusePartRow>; nodes: Record<string, FusePlyRow>
  excluded: { op: string; where: string; reason: string; parts: string[] }[]
  plan_bend: [number, number][]; ply_thickness_in: number
}

/** The ops the bottom bar shows for the fuselage: chapters 4-6, not stubs, in graph order. The variant only changes the canard. */
export function fuseBarOps(graph: GraphLite, variant: string): Op[] {
  return visibleOps(graph, variant).filter((o) => FUSE_CHAPTERS.has(o.chapter) && !o.stub)
}

/**
 * The op that puts each component in the jig. The sides stand on the blocks for the trial fit; the bulkheads are bonded in the book's
 * order (front seat, instrument panel, F22, rear seat, firewall; plans-1980:p40), then F28 (p41); the bottom is fitted on the box.
 */
export const INSTALL: Record<string, string> = {
  'fuselage.side_left': 'f06.trial-fit',
  'fuselage.side_right': 'f06.trial-fit',
  'fuselage.longerons': 'f06.trial-fit',
  'fuselage.front_seat_bkhd': 'f06.bond-front-seat',
  'fuselage.panel': 'f06.bond-panel',
  'fuselage.f22': 'f06.bond-f22',
  'fuselage.rear_seat_bkhd': 'f06.bond-rear-seat',
  'fuselage.firewall': 'f06.bond-firewall',
  'fuselage.f28': 'f06.f28-install',
  'fuselage.bottom': 'f06.bottom-foam-fit',
}
/** The dry fit: the components it lists stand in the jig for that op only, then go back out to be bonded one by one. */
export const TRIAL_FIT = 'f06.trial-fit'
/** Ops during which an installed component is off the box, on the table (the bottom's inside glass, before it is bonded). */
export const OFF_THE_BOX: Record<string, string[]> = { 'fuselage.bottom': ['f06.bottom-glass'] }
/** From this op on the box is right side up: the structure is inverted onto the glassed bottom and weighted down. */
export const TURN_UPRIGHT = 'f06.bottom-bond'

export type Placement = 'table' | 'jig'

/** Where a component is while `opId` is selected. Nothing selected shows the finished box. `dryFit` is the trial fit's components. */
export function placement(component: string, opId: string | null, order: string[], dryFit: string[] = []): Placement {
  if (!opId) return 'jig'
  const at = order.indexOf(opId)
  if (opId === TRIAL_FIT && dryFit.includes(component)) return 'jig'
  if (OFF_THE_BOX[component]?.includes(opId)) return 'table'
  const inst = INSTALL[component]
  const i = inst ? order.indexOf(inst) : -1
  return i >= 0 && at >= i ? 'jig' : 'table'
}

export type JigPose = 'inverted' | 'upright'
export function jigPose(opId: string | null, order: string[]): JigPose {
  if (!opId) return 'upright'
  const t = order.indexOf(TURN_UPRIGHT)
  return t >= 0 && order.indexOf(opId) >= t ? 'upright' : 'inverted'
}

/** Which face of a flat bulkhead is up on the table: the face the latest glassing op (up to `opId`) worked on; 'fwd' before any. */
export function upFace(part: string, opId: string | null, order: string[], nodes: Record<string, FusePlyRow>): 'fwd' | 'aft' {
  const at = opId ? order.indexOf(opId) : order.length
  let best = -1, face: 'fwd' | 'aft' = 'fwd'
  for (const n of Object.values(nodes)) {
    if (n.part !== part) continue
    const i = order.indexOf(n.op)
    if (i < 0 || i > at || i < best) continue
    if (n.region.startsWith('face:fwd')) { best = i; face = 'fwd' } else if (n.region.startsWith('face:aft')) { best = i; face = 'aft' }
  }
  return face
}

/** Half the inner width at `fs` from the exported plan-bend points (linear between them, held past the ends). */
export function planHalfWidth(bend: [number, number][], fs: number): number {
  if (!bend.length) return 0
  if (fs <= bend[0][0]) return bend[0][1]
  for (let i = 1; i < bend.length; i++) {
    const [x0, h0] = bend[i - 1], [x1, h1] = bend[i]
    if (fs <= x1) return h0 + ((h1 - h0) * (fs - x0)) / (x1 - x0)
  }
  return bend[bend.length - 1][1]
}

// ---- the station cut ----
/** The fuselage CutState's range: its plane constant is depth + (extent - depth) * (1 - amount) (core/cut.ts), normal +X. */
export const STATION_CUT = { extent: 0, depth: -200 }
/** The CutState amount that puts the plane at x = fs (constant -fs): the forward side is removed, the aft side kept. */
export const stationAmount = (fs: number): number => fs / (STATION_CUT.extent - STATION_CUT.depth)
export const fmtFs = (fs: number): string => `FS ${Math.round(fs * 10) / 10}`
/** tolerance on a ply's FS extent, as the canard's EPS on B.L. */
export const FS_EPS = 1e-3

/** True when the station cut at `fs` removes the whole part: its FS extent lies forward of the plane. A part the plane passes through stays. */
export const removedByStationCut = (row: { fs_max: number }, fs: number): boolean => row.fs_max < fs - FS_EPS

export interface StationLayer { node: string; part: string; cloth: string }
/** The plies cut at `fs` (fs_min <= fs <= fs_max), in lay order; `alive` limits them to the ones built so far. */
export function stationLayers(nodes: Record<string, FusePlyRow>, fs: number, alive?: Set<string>): StationLayer[] {
  return Object.entries(nodes)
    .filter(([k, n]) => n.fs_min - FS_EPS <= fs && fs <= n.fs_max + FS_EPS && (!alive || alive.has(k)))
    .sort(([, a], [, b]) => a.op_index - b.op_index || a.op_order - b.op_order)
    .map(([node, n]) => ({ node, part: n.part, cloth: n.cloth }))
}

/** "Left side · Front seat bulkhead: 2 UND, 1 BID": the parts cut (in the export's part order), each with its plies there by cloth. */
export function stationSummary(parts: Record<string, FusePartRow>, cut: string[], layers: StationLayer[]): string {
  // sides, then longerons, then the bulkheads front to back, then the bottom: the order a builder reads a section in
  const rank = (p: string) => (p.startsWith('side_') ? 0 : p.startsWith('top_longeron') ? 1 : p === 'bottom' ? 3 : 2)
  const names = Object.keys(parts).filter((p) => cut.includes(p) || layers.some((l) => l.part === p))
    .sort((a, b) => rank(a) - rank(b) || (parts[a]?.fs_min ?? 0) - (parts[b]?.fs_min ?? 0) || a.localeCompare(b))
  if (!names.length) return 'Nothing in the jig is cut here'
  return names.map((p) => {
    const c = new Map<string, number>()
    for (const l of layers) if (l.part === p) c.set(l.cloth, (c.get(l.cloth) ?? 0) + 1)
    const label = parts[p]?.label ?? p
    return c.size ? `${label}: ${[...c].map(([k, n]) => `${n} ${k}`).join(', ')}` : label
  }).join(' · ')
}

// ---- the CG row (ledger.json from core.ledger.fuselage_ledger_json) ----
export interface CgLite { weight_lb: number; arm_in: number | null; included: string[]; excluded: Record<string, string> }
export interface LedgerLite { cg: CgLite; cg_lower_bound: CgLite }

const r1 = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
/**
 * The empty-structure CG so far. `value` is the CG only when the strict ledger has a weight; otherwise "not yet computed" with the
 * reason. The lower bound (core plus the glass that is placed) is an undercount, so it is only ever shown labelled as one.
 */
export function cgRow(ledger: LedgerLite | null): { value: string; sub: string | null } {
  if (!ledger) return { value: 'not yet computed', sub: 'no mass ledger in this build' }
  const { cg, cg_lower_bound: lb } = ledger
  const lower = lb && lb.weight_lb > 0 && lb.arm_in != null ? `≥ ${r1(lb.weight_lb)} lb at FS ${r1(lb.arm_in)}, lower bound, ${lb.included.length} parts` : null
  if (cg.weight_lb > 0 && cg.arm_in != null) {
    const n = Object.keys(cg.excluded).length
    return { value: `${r1(cg.weight_lb)} lb at FS ${r1(cg.arm_in)}`, sub: `${cg.included.length} parts${n ? `; ${n} not yet computed` : ''}` }
  }
  const ex = Object.values(cg.excluded)
  const total = cg.included.length + ex.length
  const counts = new Map<string, number>()
  // the reason without its detail in brackets ("glass rows not fully placed (1 excluded row(s))" counts as "glass rows not fully placed")
  // and one reason for a left and right pair ("core material of top_longeron_left" and "_right" are one reason, twice)
  for (const r of ex) { const k = r.replace(/^not yet computed:\s*/, '').replace(/\s*\(.*\)\s*$/, '').replace(/_(left|right)\b/g, ''); counts.set(k, (counts.get(k) ?? 0) + 1) }
  const ranked = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  const listed = ranked.slice(0, 2).map(([k, n]) => `${k} (${n})`).join('; ') + (ranked.length > 2 ? `; ${ranked.length - 2} more` : '')
  const why = `${ex.length} of ${total} parts have no sourced mass${listed ? `: ${listed}` : ''}`
  return { value: 'not yet computed', sub: lower ? `${why} · ${lower}` : why }
}
