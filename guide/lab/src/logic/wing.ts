/**
 * Chapters 19 and 20 in the lab (the wings and the winglets with their rudders). Pure: no three.js, no DOM.
 *
 * The right wing is built on its own bench: the five floor jigs are set (f19.jig), the cores are cut and cut out flat on the table, then stood leading edge up in
 * the jigs, laid flat on the table with the bottom up for the bottom cap and skin, back in the jigs for the top cap and skin, and so through the ribs, the aileron
 * and the root controls. The attach op slides both wings
 * onto the airplane at the spar, where chapter 20 builds the winglets on the wingtips and hangs the rudders.
 * Frame as exported (python): x = F.S., y = B.L. (right positive), z = W.L. - 17.4.
 */
import type { LedgerLite } from './fuselage'

export const WING_CHAPTER = 19
export const WINGLET_CHAPTER = 20
export const JIG_OP = 'f19.jig'
export const CUT_CORES_OP = 'f19.cut-cores'
export const SHEAR_WEB_OP = 'f19.shear-web'
export const BOTTOM_CAP_OP = 'f19.bottom-cap'
export const BOTTOM_SKIN_OP = 'f19.bottom-skin'
export const TOP_CAP_OP = 'f19.top-cap'
export const TOP_SKIN_OP = 'f19.top-skin'
export const AILERON_CUT_OP = 'f19.aileron-cut'
export const AILERON_OP = 'f19.aileron-build'
export const CONTROLS_OP = 'f19.controls'
export const ATTACH_OP = 'f19.attach'
export const WINGLET_JIG_OP = 'f20.jig'
export const LAYUPS_OUT_OP = 'f20.outside-layups'
export const LOWER_FIN_OP = 'f20.lower-fin'
export const RUDDER_CUT_OP = 'f20.rudder-cut'
export const RUDDER_OP = 'f20.rudder-hang'
/** the ops the wing lies flat on the table, bottom up, for (the cores are cut and cut out on it; the bottom cap and the bottom skin are laid with it this way up); it stands in the jigs on every other bench op */
export const TABLE_OPS = [CUT_CORES_OP, 'f19.core-cutouts', BOTTOM_CAP_OP, BOTTOM_SKIN_OP]
/** the wing is complete to the end of chapter 19 from its last op; the winglets and the rudder are complete from the last op of chapter 20 */
export const WING_REF_FROM = ATTACH_OP
export const WINGLET_REF_FROM = RUDDER_OP

/** the ops that work on something buried in the wing (or, the rudder's hinge, on the far side of the winglet from the room): the rest of the wing is drawn faint for them, so the op's own parts read through it */
export const WING_GHOST_OPS = new Set(['f19.controls', RUDDER_OP])
/** the ops whose own parts draw over the solid wing (the hard points sit in the core's face; the rest of the wing stays solid so they read against it) */
export const WING_XRAY_OPS = new Set([...WING_GHOST_OPS, 'f19.hardpoints', 'f19.pads-plates', ATTACH_OP])
export const wingXrayAt = (op: { id: string } | null): boolean => !!op && WING_XRAY_OPS.has(op.id)
export const wingGhostAt = (op: { id: string } | null): boolean => !!op && WING_GHOST_OPS.has(op.id)

export interface ConflictLe { printed_fs: number; derived_fs: number; line_fs: number }
/** layup.json "fuselage"."extras"."m27" (guide/fuselage_export.py m27_section), the parts the lab reads as data */
export interface WingData {
  aileron: { axis: number[][]; max_up_deg: number; inboard_bl: number; inboard_bl_p171: number; outboard_bl: number; hinge_fs: number[]; note: string }
  rudder: { axis: number[][]; max_deg: number; hinge_fs: number; widths_in: number[]; positive: string }
  conflicts: { le_bl_106_25: ConflictLe; aileron_inboard: { p124_bl: number; p171_bl: number }; attach_bolt_spacing: { drawing_in: number; text_in: number } }
  shear_web: { zones: number[][]; outboard_plies_printed: number; note: string }
  winglet: {
    abc_book_in: number[]; abc_model_in: number[]; abc_residual_in: number[]; abc_tol_in: number[]; lean_in: number; lean_status: string
    tip_chord_in: number; tip_chord_status: string; wprp: number[]; points: Record<'wprp' | 'a' | 'b' | 'c', number[]>
  }
  weights: { rows: string[]; note: string }
}
/** a ply node row's fields the schedule reads */
export interface WingPlyRow { part: string; component: string; side: string; op: string; op_order: number; cloth: string }

/** 'winglet': the right winglet lies flat on the table while it is cut, skinned and trimmed (chapter 20 up to the jig op); nothing else of the wing or airplane is drawn */
export type WingPlace = 'jig' | 'table' | 'airplane' | 'winglet'
export const WINGLET_BENCH_OPS = ['f20.cut-cores', 'f20.skins', 'f20.trim']
/**
 * Where the wing parts (the right wing's bench set) are while `opId` is selected: stood leading edge up in the jigs from f19.jig, flat on the table
 * for the two bottom ops, back in the jigs, and on the airplane from the attach op on. Nothing selected: on the airplane.
 */
export function wingPlace(opId: string | null, order: string[]): WingPlace {
  if (!opId) return 'airplane'
  if (WINGLET_BENCH_OPS.includes(opId)) return 'winglet'
  const i = order.indexOf(opId)
  if (i < order.indexOf(JIG_OP) || i >= order.indexOf(ATTACH_OP)) return 'airplane'
  return TABLE_OPS.includes(opId) ? 'table' : 'jig'
}
/** the wing is on its own bench (not the airplane) for this op */
export const onWingBench = (opId: string | null, order: string[]): boolean => wingPlace(opId, order) !== 'airplane'

/** the left wing is not built until the attach op: the right wing is the one on the bench (the left is its mirror, p126, p135) */
export function sideShown(side: string, opId: string | null, order: string[]): boolean {
  return side !== 'left' || !opId || order.indexOf(opId) >= order.indexOf(ATTACH_OP)
}

/** the workshop parts (the five jigs, the winglet's jig lines) are on the floor, not on the airplane: the jigs stand on the floor from f19.jig until the wing is attached, the jig lines hold from f20.jig to the corner layups */
export function workshopShown(component: string, opId: string | null, order: string[]): boolean {
  if (!opId) return false
  const i = order.indexOf(opId)
  if (component === 'wing.jigs') return wingPlace(opId, order) === 'jig' || wingPlace(opId, order) === 'table'
  if (component === 'winglet.jig') return i >= order.indexOf(WINGLET_JIG_OP) && i <= order.indexOf(LAYUPS_OUT_OP)
  return true
}

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const clamp01 = (x: number) => Math.min(1, Math.max(0, x))
/** the aileron swings up to its stop on the hinge op, in sim seconds since it was picked: the camera comes round first, then the sweep (and it stays up) */
export const AILERON_SWING = { wait: 1.6, seconds: 3.4 }
export const aileronProgress = (t: number): number => ease(clamp01((t - AILERON_SWING.wait) / AILERON_SWING.seconds))
export const aileronDuration = (): number => AILERON_SWING.wait + AILERON_SWING.seconds + 1.4
/** the rudder swings to its 30 deg, trailing edge outboard, on the hang op */
export const RUDDER_SWING = { wait: 1.6, seconds: 3.4 }
export const rudderProgress = (t: number): number => ease(clamp01((t - RUDDER_SWING.wait) / RUDDER_SWING.seconds))
export const rudderDuration = (): number => RUDDER_SWING.wait + RUDDER_SWING.seconds + 1.4

export const clampAileronDeg = (d: number, max: number): number => Math.max(0, Math.min(max, d))
export const clampRudderDeg = (d: number, max: number): number => Math.max(-max, Math.min(max, d))

/**
 * A point (x = F.S., y = B.L., z up, as exported) turned `deg` degrees about the line a to b (right-hand rule, as cadquery's rotate does): the same
 * kernel the aileron (a turn of -deg_up, core.wing_book.aileron_pose) and the rudder (a turn of +deg, core.winglet_book.rudder_pose) use.
 */
export function rotateAbout(p: number[], a: number[], b: number[], deg: number): [number, number, number] {
  const k = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], n = Math.hypot(k[0], k[1], k[2])
  const u = [k[0] / n, k[1] / n, k[2] / n]
  const v = [p[0] - a[0], p[1] - a[1], p[2] - a[2]]
  const th = (deg * Math.PI) / 180, c = Math.cos(th), s = Math.sin(th)
  const d = u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
  const cr = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
  return [0, 1, 2].map((i) => a[i] + v[i] * c + cr[i] * s + u[i] * d * (1 - c)) as [number, number, number]
}
/** the aileron up `deg` degrees (0 to the stop): a turn of -deg about its hinge axis */
export const aileronPoint = (p: number[], deg: number, w: Pick<WingData, 'aileron'>): [number, number, number] => rotateAbout(p, w.aileron.axis[0], w.aileron.axis[1], -deg)
/** the rudder out `deg` degrees (positive: the trailing edge outboard): a turn of +deg about its hinge axis */
export const rudderPoint = (p: number[], deg: number, w: Pick<WingData, 'rudder'>): [number, number, number] => rotateAbout(p, w.rudder.axis[0], w.rudder.axis[1], deg)

const r2 = (x: number) => (Math.round(x * 100) / 100).toString()
const r1 = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
/** the aileron's readout: neutral, an angle up, and at the stop it says so */
export function aileronText(deg: number, max: number): string {
  const d = Math.round(deg)
  if (d <= 0) return 'Neutral'
  return d >= Math.round(max) ? `${d} deg up: at the stop` : `${d} deg up`
}
export const aileronShort = (deg: number): string => (Math.round(deg) <= 0 ? 'Neutral' : `${Math.round(deg)} deg up`)
/** the rudder's readout: neutral, an angle with the way its trailing edge goes, and at the limit it says so */
export function rudderText(deg: number, max: number): string {
  const d = Math.round(deg)
  if (d === 0) return 'Neutral'
  return `${Math.abs(d)} deg, trailing edge ${d > 0 ? 'outboard' : 'inboard'}${Math.abs(d) >= Math.round(max) ? ': at the limit' : ''}`
}
export const rudderShort = (deg: number): string => (Math.round(deg) === 0 ? 'Neutral' : `${Math.abs(Math.round(deg))} deg ${deg > 0 ? 'out' : 'in'}`)

/** the leading edge at BL 106.25: the printed station and the one the chord and the trailing edge give. Always worded as a pair. */
export function leText(w: WingData): { value: string; sub: string } {
  const c = w.conflicts.le_bl_106_25
  return {
    value: `Leading edge at BL 106.25: printed FS ${r2(c.printed_fs)}, FS ${r2(c.derived_fs)} from the chord and the trailing edge`,
    sub: `${r2(Math.abs(c.printed_fs - c.derived_fs))} in apart, unresolved; the model uses the chord and the trailing edge`,
  }
}
/** the aileron's inboard end: the p124 cut at the foam joint and the p171 figure. */
export function aileronEndText(w: WingData): { value: string; sub: string } {
  const c = w.conflicts.aileron_inboard
  return {
    value: `Aileron inboard end: BL ${r2(c.p171_bl)} on p171, BL ${r2(c.p124_bl)} cut at the foam joint`,
    sub: `${r2(Math.abs(c.p124_bl - c.p171_bl))} in apart, unresolved; the model cuts at BL ${r2(c.p124_bl)}`,
  }
}
/** the spar-bolt spacing: the drawing and the text. */
export function boltText(w: WingData): { value: string; sub: string } {
  const c = w.conflicts.attach_bolt_spacing
  return {
    value: `Spar bolt spacing: ${r2(c.drawing_in)} in on the drawing, ${r2(c.text_in)} in in the text`,
    sub: `${r2(Math.abs(c.drawing_in - c.text_in))} in apart, unresolved`,
  }
}
/** the shear web's plies by span zone, the outboard one cp-corrected: "2 plies (CP26 LPC 31; plans print 3)". */
export function webText(w: WingData): { value: string; sub: string } {
  const z = w.shear_web.zones
  const out = z[z.length - 1]
  const inner = z.slice(0, -1).map((q) => `BL ${r2(q[0])} to ${r2(q[1])}: ${q[2]} plies`).join(', ')
  return {
    value: `${inner}, BL ${r2(out[0])} to ${r2(out[1])}: ${out[2]} plies (CP26 LPC 31; plans print ${w.shear_web.outboard_plies_printed})`,
    sub: 'Two plies run the full span; the others step in 39 and 91 in from the tip',
  }
}
/** the winglet jig: A, B and C from the reference point, the model's closure and the derived lean. */
export function abcText(w: WingData): { value: string; sub: string } {
  const [a, b, c] = w.winglet.abc_book_in, [da, db, dc] = w.winglet.abc_residual_in
  const [fs, bl] = w.winglet.wprp
  return {
    value: `A ${r2(a)}, B ${r2(b)}, C ${r2(c)} in from the reference point (BL ${r2(bl)}, FS ${r2(fs)})`,
    sub: `The model closes to A ${r2(da)}, B ${r2(db)}, C ${r2(dc)} in; the winglet's lean (${r2(w.winglet.lean_in)} in) is derived, low confidence`,
  }
}
/** the winglet's labels for its three jig lines, "A 102.15 in" */
export function abcLabel(w: WingData, k: 'a' | 'b' | 'c'): string {
  const i = { a: 0, b: 1, c: 2 }[k]
  return `${k.toUpperCase()} ${r2(w.winglet.abc_book_in[i])} in`
}

/** the ply lay-down by op, from the exported ply rows: one entry per op and part (right wing and winglet; the left is the mirror) */
export interface PlyStep { op: string; part: string; plies: number; cloth: string[] }
export function plySchedule(nodes: Record<string, WingPlyRow>): PlyStep[] {
  const by = new Map<string, PlyStep & { rows: WingPlyRow[] }>()
  for (const r of Object.values(nodes)) {
    if (r.side !== 'right') continue
    const k = `${r.op}|${r.part}`
    if (!by.has(k)) by.set(k, { op: r.op, part: r.part, plies: 0, cloth: [], rows: [] })
    by.get(k)!.rows.push(r)
  }
  return [...by.values()].map(({ op, part, rows }) => {
    const s = rows.slice().sort((a, b) => a.op_order - b.op_order)
    return { op, part, plies: s.length, cloth: s.map((x) => x.cloth) }
  })
}
/** how a lay-down reads: "6 plies, UND" or "3 plies, UND, UND, BID" collapsed as "2 UND + 1 BID" */
export function plyText(s: PlyStep): string {
  const n = new Map<string, number>()
  for (const c of s.cloth) n.set(c, (n.get(c) ?? 0) + 1)
  return `${s.plies} plies: ${[...n].map(([c, k]) => `${k} ${c}`).join(' + ')}`
}

/** the ops with a readout of their own, and what it says (null: none) */
export function wingKin(opId: string | null, w: WingData, aileronDeg: number, rudderDeg: number): { label: string; value: string; sub: string } | null {
  switch (opId) {
    case CUT_CORES_OP: return { label: 'Core cut', ...leText(w) }
    case SHEAR_WEB_OP: return { label: 'Shear web plies', ...webText(w) }
    case AILERON_CUT_OP: return { label: 'Aileron cut', ...aileronEndText(w) }
    case AILERON_OP: return { label: 'Aileron travel', value: aileronText(aileronDeg, w.aileron.max_up_deg), sub: `Up to the ${w.aileron.max_up_deg} deg stop (p125, p131); the arc is representational` }
    case ATTACH_OP: return { label: 'Wing attach', ...boltText(w) }
    case WINGLET_JIG_OP: return { label: 'Winglet jig', ...abcText(w) }
    case RUDDER_OP: return { label: 'Rudder travel', value: rudderText(rudderDeg, w.rudder.max_deg), sub: `Swings to ${w.rudder.max_deg} deg either way (p139); positive is the trailing edge outboard; the arc is representational` }
    default: return null
  }
}

/**
 * The reference weight rows (CP26 builder weights, Melvill N26MS): never in the CG. The aileron's from the op that hangs it, the wing's at the end of chapter 19,
 * the lower winglet's from its op, and the whole wing with winglets and rudder at the end of chapter 20 (the upper winglet with antenna beside it).
 */
export function wingRow(ledger: LedgerLite | null, opId: string | null, order: string[]): { value: string; sub: string } | null {
  const rows = ledger?.prototype_weights?.rows
  if (!rows || !opId || !/^f(19|20)\./.test(opId)) return null
  const at = (op: string) => order.indexOf(opId) >= order.indexOf(op)
  const tag = '(CP26 builder weight, N26MS)'
  const ref = ', reference, not in CG'
  if (at(WINGLET_REF_FROM) && rows.wing_complete) {
    const extra = [rows.upper_winglet && `upper winglet ${r1(rows.upper_winglet.weight_lb)} lb`, rows.lower_winglet && `lower winglet ${r1(rows.lower_winglet.weight_lb)} lb`].filter(Boolean).join(', ')
    return { value: `Wing with winglets and rudder ${tag}: ${r1(rows.wing_complete.weight_lb)} lb each${ref}`, sub: `${extra}; ${rows.wing_complete.note}` }
  }
  if (at(LOWER_FIN_OP) && opId.startsWith('f20.') && rows.lower_winglet) return { value: `Lower winglet ${tag}: ${r1(rows.lower_winglet.weight_lb)} lb${ref}`, sub: rows.lower_winglet.note }
  if (at(WING_REF_FROM) && opId.startsWith('f19.') && rows.wing_ch19) {
    const al = rows.aileron ? `; aileron ${r1(rows.aileron.weight_lb)} lb` : ''
    return { value: `Wing to the end of chapter 19 ${tag}: ${r1(rows.wing_ch19.weight_lb)} lb each${al}${ref}`, sub: rows.wing_ch19.note }
  }
  if (at(AILERON_OP) && opId.startsWith('f19.') && rows.aileron) return { value: `Aileron ${tag}: ${r1(rows.aileron.weight_lb)} lb${ref}`, sub: rows.aileron.note }
  return null
}
