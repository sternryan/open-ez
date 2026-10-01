/**
 * The fuselage box and main gear (plans chapters 4-9) as a lab subject. Pure: no three.js, no DOM.
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
 *   chapter 7  right side up; the corners carved and the canard opening cut (the shapes change: layup.json "stages"), then the box
 *              rolled to 45 degrees of left bank for the right skin and through to 45 of right bank for the left (plans-1980:p46).
 *   chapter 8  the roll-over box is made on the table, bonded on the front seat bulkhead and glassed outside in the jig.
 *   chapter 9  the strut is stiffened on the table; at the gear positioning the box turns upside down onto a level table on its top
 *              longerons (the roll-over hangs through an opening in it) and stays so to the end of the chapter (plans-1980:p50).
 */
import { visibleOps, type GraphLite, type Op } from './graph'

export type Subject = 'canard' | 'fuselage'
export const SUBJECTS: Subject[] = ['canard', 'fuselage']
export const SUBJECT_KEY = 'longez.subject'
export const parseSubject = (s: string | null | undefined): Subject => (s === 'fuselage' ? 'fuselage' : 'canard')

export const FUSE_CHAPTERS = new Set([4, 5, 6, 7, 8, 9])

export type Fidelity = 'book' | 'derived' | 'representational'
/** When a part is shown besides its component's build state: from an op on, until one (exclusive), or at one op only (logic: shownAt) */
export interface ShowWindow { from?: string; until?: string; only?: string }
export interface FusePartRow {
  node: string; component: string; fidelity: Fidelity; label: string; cite: string[]; fs_min: number; fs_max: number; fwd_normal?: number[] | null
  /** the material an opening removes (the canard cutout): no mass, shown lifted out at its op */
  void?: boolean
  show?: ShowWindow
}
/** a node's later shapes: from op `from` on the lab shows `node` in its place (the carve, the canard opening, the access holes) */
export interface FuseStage { from: string; node: string }
/** the book's gear datum (plans-1980:p50 figure 1A, p171), as exported; no track, which has no source */
export interface GearMarks { axle_fs: number; board_fs: number; board_bl: number; axle_fwd_of_board_in: number; axle_z: number; cite: string }
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
  stages?: Record<string, FuseStage[]>
  bank_deg?: Record<string, number>
  gear_marks?: GearMarks
}

/** The ops the bottom bar shows for the fuselage: chapters 4-9, not stubs, in graph order. The variant only changes the canard. */
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
  // chapters 7-9
  'fuselage.gear_extrusions': 'f06.trial-fit', // on the sides from chapter 5; hidden while the sides lie on the table (no table pose)
  'fuselage.canard_cutout': 'f07.canard-cutout',
  'fuselage.belt_insert': 'f07.belt-insert',
  'fuselage.rollover': 'f08.roll-over-bond', // made and glassed inside on the table first
  'fuselage.rollover_inserts': 'f08.roll-over-bond',
  'fuselage.belt_attach': 'f08.belt-attach',
  'fuselage.step': 'f08.step',
  'gear.jig_blocks': 'f09.jig-blocks',
  'gear.strut': 'f09.position-gear', // stiffened on the table first
  'gear.datum_board': 'f09.position-gear',
  'gear.axles': 'f09.axles-brakes',
}
/** Components with no place on the layup table: before their install op they are not shown (the extrusions go on the flat sides in
 * chapter 5, which the lab does not draw). */
export const JIG_ONLY = new Set(['fuselage.gear_extrusions', 'fuselage.canard_cutout', 'fuselage.belt_insert', 'fuselage.belt_attach', 'fuselage.step', 'gear.jig_blocks', 'gear.datum_board', 'gear.axles'])
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

/** From this op to the end of chapter 9 the box is upside down on its top longerons on the level gear table (plans-1980:p50); the
 * book turns it right side up "on its own feet" after the chapter, which the lab shows as the finished box (nothing selected). */
export const TURN_GEAR = 'f09.position-gear'
/** The last op of chapter 9: after it (and with nothing selected) the box stands on its own gear on the shop floor ('on-gear'). */
export const LAST_GEAR_OP = 'f09.brake-lines'
/**
 * Chapter 7's rolls: the book's words are "45 degrees of left bank" for the right skin, 45 of right bank for the left (plans-1980:p46).
 * The captain's reading: the side AND the bottom being glassed both face up 45 degrees (the right skin covers the right side and the
 * bottom to 1 in past the centre line, and the glass falls off an overhanging face), so the box is rolled 135 degrees from upright
 * (45 degrees past on its side, resting on its top-left corner). Judgement call, flagged for the owner. Positive is a left bank, as
 * core.landing_gear_book.bank_pose and layup.json "bank_deg" (guide/fuselage_export.py BANK_DEG, which tests/ compare); the lab rolls
 * the box about its long axis by that angle (tests/fuselage.test.ts checks the right side's and the bottom's normals point up).
 */
export const BANK_DEG: Record<string, number> = { 'f07.skin-right': 135, 'f07.skin-left': -135 }

/**
 * 'on-gear': right side up on its own main gear on the shop floor beside the bench (the finished box, once the build has its gear).
 * A build with no chapter 9 (no gear op in the order) finishes upright on the jig blocks, as chapter 6 left it.
 */
export type JigPose = 'inverted' | 'upright' | 'bank-left-45' | 'bank-right-45' | 'gear-table' | 'on-gear'
export function jigPose(opId: string | null, order: string[], bank: Record<string, number> = BANK_DEG): JigPose {
  const g = order.indexOf(TURN_GEAR)
  if (!opId) return g >= 0 ? 'on-gear' : 'upright'
  const i = order.indexOf(opId)
  const t = order.indexOf(TURN_UPRIGHT)
  if (!(t >= 0 && i >= t)) return 'inverted'
  const last = order.indexOf(LAST_GEAR_OP)
  if (g >= 0 && last >= 0 && i > last) return 'on-gear'
  if (g >= 0 && i >= g) return 'gear-table'
  const b = bank[opId]
  if (b) return b > 0 ? 'bank-left-45' : 'bank-right-45'
  return 'upright'
}

/** A part's own show window (layup.json "show") at `opId`; nothing selected shows a part only when it has no end. */
export function shownAt(w: ShowWindow | undefined, opId: string | null, order: string[]): boolean {
  if (!w) return true
  if (!opId) return !w.until && !w.only
  if (w.only) return opId === w.only
  const i = order.indexOf(opId)
  if (w.from && i < order.indexOf(w.from)) return false
  if (w.until && i >= order.indexOf(w.until)) return false
  return true
}

/** Which of a node's shapes shows at `opId`: the last stage whose op is at or before it (nothing selected: the last), else null (the node's own). */
export function stageAt(stages: FuseStage[] | undefined, opId: string | null, order: string[]): string | null {
  if (!stages?.length) return null
  if (!opId) return stages[stages.length - 1].node
  const i = order.indexOf(opId)
  let out: string | null = null
  for (const s of stages) if (order.indexOf(s.from) <= i) out = s.node
  return out
}

/** How long the box takes to turn over (seconds of sim time), as the canard's turnover (main.ts FLIP_SECONDS). */
export const FLIP_SECONDS = 1.0
/** the turn starts this long after the step is picked (seconds of sim time), so the camera, flying in from the layup table, sees it */
export const FLIP_DELAY = 0.6
/** extra lift at mid-turn (inches), so the turn reads as picked up and set down rather than rolled over the blocks */
export const FLIP_CLEARANCE = 1.5
/** the roll of each pose about the box's long axis (radians; positive = left bank, the right side up), and how high its support is
 * above the jig blocks' tops (inches; the gear table stands clear of the roll-over) */
export function poseAngle(p: JigPose, bank: Record<string, number> = BANK_DEG): number {
  if (p === 'inverted' || p === 'gear-table') return Math.PI
  if (p === 'bank-left-45') return ((bank['f07.skin-right'] ?? BANK_DEG['f07.skin-right']) * Math.PI) / 180 // signed, as exported
  if (p === 'bank-right-45') return ((bank['f07.skin-left'] ?? BANK_DEG['f07.skin-left']) * Math.PI) / 180
  return 0
}
/**
 * The key light's strength in each pose, against the canard's (main.ts aimKey). Banked 45 degrees, the side being glassed faces the
 * overhead key square on and sits closer to it than a part flat on the layup table, so the dry cloth burned out to white; the key is
 * dimmed there so the weave reads as it does on the canard and in chapters 4-6.
 */
export const KEY_BANK = 0.5
/** and the dry cloth on the box is toned down there (core/composite.ts uDryTone), from the bright white it is on a flat table */
export const DRY_TONE_BANK = 0.65
const banked = (p: JigPose) => p === 'bank-left-45' || p === 'bank-right-45'
export const keyScale = (p: JigPose): number => (banked(p) ? KEY_BANK : 1)
export const dryTone = (p: JigPose): number => (banked(p) ? DRY_TONE_BANK : 1)

/** a turn between the jig and the floor is not animated: the box is carried off the bench, not rolled (logic: setPose) */
export const animatedTurn = (from: JigPose, to: JigPose): boolean => from !== 'on-gear' && to !== 'on-gear'

/**
 * The main wheels drawn under the finished box. REPRESENTATIONAL (fitted, striped, labelled): the plans name the tyre size, 3.40 x 5
 * (plans-1980:p6, p9), but print no outer diameter, so the drawn diameter is a fitted number; the section width and rim diameter are
 * read from the size name. Each wheel sits on its axle stub, centred on the stub. The wheel's position comes from the fitted track
 * (core.landing_gear_book.FITTED_TRACK), which is never printed in the lab.
 */
export const FITTED_TYRE_OD = 11.0 // in, fitted: no outer diameter printed for the 3.40-5 tyre
export const TYRE_SECTION = 3.4 // in, the size name's section width (p6, p9)
export const RIM_DIA = 5.0 // in, the size name's rim diameter (p6, p9)

/**
 * At the home view (nothing selected) the finished box shows one label per family of parts, so the view reads at a glance: a part
 * listed here gives its words to the part it names, when that part is there (a chain: the extrusions to the strut, the strut to the
 * wheels). Every part is still drawn, and a fitted one still striped; only its label waits for its own op. With an op selected every
 * part keeps its own label rule (main.ts).
 */
export const LABEL_FAMILY: Record<string, string> = {
  rollover_inserts: 'rollover',
  extrusions: 'strut', gear_tubes: 'strut', axles: 'strut', strut: 'wheels',
  side_right: 'side_left', top_longeron_left: 'side_left', top_longeron_right: 'side_left', step: 'side_left',
  carved_corners: 'bottom', belt_insert: 'bottom', belt_attach: 'bottom',
}
/** a part's label at the home view: it carries its family's words unless the part it gives them to is there */
export function homeLabel(part: string, present: (p: string) => boolean): boolean {
  const to = LABEL_FAMILY[part]
  return !to || !present(to)
}

/** the level table chapter 9 inverts the box onto (inches above the block tops): high enough that the roll-over (12.6 in above the
 * longerons) hangs through its opening clear of the bench. REPRESENTATIONAL: the book says only "level it on the top longerons". */
export const GEAR_TABLE_RISE = 11
export const poseBase = (p: JigPose): number => (p === 'gear-table' ? GEAR_TABLE_RISE : 0)
/** the box's long axis above the support at rest in `angle` (inches): its lowest corner touches the support */
export const restLift = (angle: number, half: { h: number; w: number }): number => {
  const c = Math.abs(Math.cos(angle)), s = Math.abs(Math.sin(angle))
  return half.h * (c > 1 - 1e-12 ? 1 : c) + half.w * (s < 1e-12 ? 0 : s) // upright and inverted rest exactly half the height up
}
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
/**
 * The box mid-turn, `k` (0..1) of the way from `from` to `to`: its roll about its long axis (FS, the jig frame's X) through the box's
 * middle, and how high that axis is above the block tops (inches). `half` is half the box's height (h) and width (w). At rest the axis
 * is h above the blocks (the box sits on them); mid-turn it rises just enough that no corner of the section goes below the block tops,
 * plus a small arc. Eased like the canard's turnover. Pure: the same k gives the same pose, so a recorded film repeats exactly.
 */
export function turnPose(from: JigPose, to: JigPose, k: number, half: { h: number; w: number }, bank: Record<string, number> = BANK_DEG): { angle: number; lift: number } {
  const t = Math.min(1, Math.max(0, k))
  const e = ease(t)
  const a0 = poseAngle(from, bank), a1 = poseAngle(to, bank)
  // the short way round: the right skin's 135 to the left skin's -135 rolls 90 degrees over the top, not 270 back through upright
  let d = a1 - a0
  if (d > Math.PI + 1e-9) d -= 2 * Math.PI
  else if (d < -Math.PI - 1e-9) d += 2 * Math.PI
  const angle = t >= 1 ? a1 : t <= 0 ? a0 : a0 + d * e
  const base = t >= 1 ? poseBase(to) : t <= 0 ? poseBase(from) : poseBase(from) + (poseBase(to) - poseBase(from)) * e
  const lift = t <= 0 || t >= 1 ? base + restLift(angle, half) : base + restLift(angle, half) + FLIP_CLEARANCE * Math.sin(Math.PI * e)
  return { angle, lift }
}

/**
 * How much to soften the amber stripes on a fitted part's surface, 0 (full) to 1 (softest), from its largest face area (in^2). Small
 * parts (the bulkheads, up to about 300 in^2) keep the full stripes; a large plate (the 24 x 96 in bottom) gets thinner, lighter ones so it does not shout. Cut caps always
 * draw the full stripes (core/composite.ts).
 */
export const HATCH_SOFT_AREA: [number, number] = [300, 1500]
export function hatchSoftness(areaIn2: number): number {
  const [a, b] = HATCH_SOFT_AREA
  if (!(areaIn2 > a)) return 0
  if (areaIn2 >= b) return 1
  return Math.log(areaIn2 / a) / Math.log(b / a)
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
/** True when the plane at `fs` passes through the part (its cut face is what the section shows). */
export const crossedByStationCut = (row: { fs_min: number; fs_max: number }, fs: number): boolean => row.fs_min - FS_EPS <= fs && fs <= row.fs_max + FS_EPS

/**
 * A fuselage label's priority when labels collide on screen (logic/declutter.ts): the selected op's parts win, then the parts the
 * station cut passes through (the face being looked at), then fitted shapes (their label is how the fidelity is read), then the rest.
 */
export function labelPriority(p: { inOp: boolean; cut: boolean; fitted: boolean }): number {
  return p.inOp ? 3 : p.cut ? 2 : p.fitted ? 1 : 0
}

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
export interface GearRowLite { name: string; label: string; weight_lb: number; arm_in: number; status: string; arm_status: string; cite: string[] }
export interface GroundLite {
  main_axle_fs: number; main_axle_wl: number; tip_back_line_deg: number; cite: Record<string, string>
  tip_back_check: string; tip_over_check: string
}
export interface LedgerLite { cg: CgLite; cg_lower_bound: CgLite; gear?: { rows: GearRowLite[]; sourced_lb: number; ground_handling?: GroundLite } }

const r1 = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
/**
 * The empty-structure CG so far. `value` is the CG only when the strict ledger has a weight; otherwise "not yet computed" with the
 * reason. The lower bound (core plus the glass that is placed, plus the sourced gear rows) is an undercount, so it is only ever shown
 * labelled as one, and it says how much of it is gear. An unsourced gear row is listed as excluded, never with its placeholder weight.
 */
export function cgRow(ledger: LedgerLite | null): { value: string; sub: string | null } {
  if (!ledger) return { value: 'not yet computed', sub: 'no mass ledger in this build' }
  const { cg, cg_lower_bound: lb } = ledger
  const rows = ledger.gear?.rows ?? []
  const gearIn = rows.filter((r) => lb?.included.includes(r.name))
  const gearLb = gearIn.reduce((a, r) => a + r.weight_lb, 0)
  const nParts = (lb?.included.length ?? 0) - gearIn.length
  const struts = gearIn.map((r) => r.label.toLowerCase().replace(/ gear strut$/, ''))
  const gearWhat = gearIn.every((r) => / gear strut$/i.test(r.label)) ? `${struts.join(' and ')} strut${struts.length > 1 ? 's' : ''}` : struts.join(', ')
  const gearWords = gearIn.length ? ` and ${r1(gearLb)} lb of gear (${gearWhat})` : ''
  const lower = lb && lb.weight_lb > 0 && lb.arm_in != null ? `≥ ${r1(lb.weight_lb)} lb at FS ${r1(lb.arm_in)}, lower bound, ${nParts} parts${gearWords}` : null
  const unsourced = rows.filter((r) => r.status === 'unsourced').map((r) => `${r.label.replace(/\s*\(unsourced\)\s*$/, '')}: excluded, no source`)
  if (cg.weight_lb > 0 && cg.arm_in != null) {
    const n = Object.keys(cg.excluded).length
    return { value: `${r1(cg.weight_lb)} lb at FS ${r1(cg.arm_in)}`, sub: `${cg.included.length} parts${n ? `; ${n} not yet computed` : ''}` }
  }
  const ex = Object.values(cg.excluded)
  const total = cg.included.length + ex.length
  const counts = new Map<string, number>()
  // the reason without its detail in brackets ("glass rows not fully placed (1 excluded row(s))" counts as "glass rows not fully placed")
  // and one reason for a left and right pair ("core material of Left top longeron" and "Right top longeron" are one reason, twice)
  for (const r of ex) { const k = r.replace(/^not yet computed:\s*/, '').replace(/\s*\(.*\)\s*$/, '').replace(/\b(Left|Right) (\w)/g, (_m, _s, c: string) => c.toLowerCase()); counts.set(k, (counts.get(k) ?? 0) + 1) }
  const ranked = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  const listed = ranked.slice(0, 2).map(([k, n]) => `${k} (${n})`).join('; ') + (ranked.length > 2 ? `; ${ranked.length - 2} more` : '')
  const why = `${ex.length} of ${total} parts have no sourced mass${listed ? `: ${listed}` : ''}`
  const segs = [why, ...unsourced, ...(lower ? [lower] : [])]
  return { value: 'not yet computed', sub: segs.join(' · ') }
}

/** A check's text as shown: only ever "not yet computed (why)". Anything else (a number, a verdict) is not shown until the code that
 * shows it is written on purpose with its source in hand (Review Focus 4). */
const checkText = (s: string | undefined): string => {
  const m = /^not yet computed:?\s*(.*)$/.exec(s ?? '')
  if (!m || /\d/.test(s ?? '')) return 'not yet computed'
  return m[1] ? `not yet computed (${m[1]})` : 'not yet computed'
}
/**
 * The ground-handling note (ledger.json gear.ground_handling, core.landing_gear_book.ground_handling): the book's main-axle station
 * and its tip-back line, and the two checks, which stay "not yet computed": no CG height source (tip-back), no track source
 * (tip-over). It never carries the fitted track or a numeric verdict.
 */
export function groundRow(ledger: LedgerLite | null): { value: string; sub: string } | null {
  const g = ledger?.gear?.ground_handling
  if (!g) return null
  return {
    value: `Main axle F.S. ${g.main_axle_fs} (book)`,
    sub: [`${g.tip_back_line_deg}° tip-back line from the main tyre contact (p171)`, `tip-back check: ${checkText(g.tip_back_check)}`, `tip-over check: ${checkText(g.tip_over_check)}`].join(' · '),
  }
}
