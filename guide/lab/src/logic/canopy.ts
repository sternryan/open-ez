/**
 * Chapter 18 in the lab (the canopy). Pure: no three.js, no DOM.
 *
 * The bubble is trimmed on the layup table (f18.trim-plexi), then set on its temporary blocks on the longerons and built up in place: the foam
 * frame, its carving and the five glass plies. The cut (f18.cut-remove) frees the canopy, which lifts off and turns upside down on the bench; its
 * inside is carved and glassed there. From f18.hinges on it is back on the airplane, hinged on the right, and opens through MAX_OPEN_DEG.
 * Frame as exported (python): x = F.S., y = B.L. (right positive), z = W.L. - 17.4.
 */
import type { LedgerLite } from './fuselage'

export const CANOPY_CHAPTER = 18
export const TRIM_OP = 'f18.trim-plexi'
export const BLOCKS_OP = 'f18.locate-blocks'
export const CHECK_OP = 'f18.check-ab'
export const CUT_OP = 'f18.cut-remove'
export const CARVE_INSIDE_OP = 'f18.carve-inside'
export const PADS_OP = 'f18.pads-inside-glass'
/** the last op the canopy is upside down on the bench for; it is hinged back onto the airplane by HINGE_OP */
export const BENCH_LAST_OP = 'f18.vent-brace'
export const HINGE_OP = 'f18.hinges'
export const LATCH_OP = 'f18.latches'
export const FRONT_COVER_OP = 'f18.front-cover'
/** the canopy is complete from this op (the last of the chapter): the readout carries its CP26 builder weight (N26MS) as a reference row, never in the CG */
export const CANOPY_REF_FROM = 'f18.safety-catch'

export interface CanopyCheck { id: string; fs: number; fs_status: string; wl0: number; wl1: number; min: boolean; height_in: number }
/** layup.json "fuselage"."extras"."m26"."canopy" (guide/fuselage_export.py m26_section) */
export interface CanopyData {
  lift: string[]
  /** model y = W.L. - wl_zero */
  wl_zero: number
  hinge: { y: number; z: number; max_open_deg: number; past_vertical_deg: number; note: string }
  checks: CanopyCheck[]
  latch: { derived_centres_fs: number[]; printed_labels_fs: number[]; gap_in: number }
  front_cut: { fs: number; datum_named: boolean }
  rear_cut_fs: number
  pads: { left_aft_edge_fwd_of_cut: number[]; right_aft_edge_fwd_of_cut: number[]; length_in: number; catch_fs: number }
}

export type CanopyPlace = 'bench-up' | 'bench-down' | 'airplane'
/** Where a canopy component is while `opId` is selected: the parts that come off (`lift`) are on the bench upright while the bubble is trimmed,
 * upside down on it from the cut to the last op that works on its inside, and on the airplane otherwise. Nothing selected: on the airplane. */
export function canopyPlace(component: string, lift: string[], opId: string | null, order: string[]): CanopyPlace {
  if (!opId || !lift.includes(component)) return 'airplane'
  const i = order.indexOf(opId)
  if (i >= order.indexOf(TRIM_OP) && i < order.indexOf(BLOCKS_OP)) return 'bench-up'
  if (i >= order.indexOf(CUT_OP) && i <= order.indexOf(BENCH_LAST_OP)) return 'bench-down'
  return 'airplane'
}

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const clamp01 = (x: number) => Math.min(1, Math.max(0, x))

/** The lift-off at the cut, in sim seconds since the cut op was picked: the camera comes round first, then the canopy goes up, over and down onto the bench. */
export const LIFT = { wait: 1.4, seconds: 4.6 }
/** 0 = on the airplane, 1 = upside down on the bench */
export const liftProgress = (t: number): number => ease(clamp01((t - LIFT.wait) / LIFT.seconds))
export const liftDuration = (): number => LIFT.wait + LIFT.seconds + 1.4

/** The opening on the hinge op, in sim seconds since it was picked: the camera comes round first, then the canopy swings open. */
export const OPEN = { wait: 1.8, seconds: 3.8 }
export const openProgress = (t: number): number => ease(clamp01((t - OPEN.wait) / OPEN.seconds))
export const openDuration = (): number => OPEN.wait + OPEN.seconds + 1.4

export const clampOpenDeg = (d: number, max: number): number => Math.max(0, Math.min(max, d))

/**
 * A point (x = F.S., y = B.L., z up, as exported) with the canopy opened `deg` degrees about the right hinge line (core.canopy_book.open_pose:
 * a turn of -deg about +x through (y = hinge.y, z = hinge.z); a positive opening takes the canopy up and out to the right).
 */
export function openPoint(p: [number, number, number], deg: number, hinge: { y: number; z: number }): [number, number, number] {
  const th = (-deg * Math.PI) / 180, c = Math.cos(th), s = Math.sin(th)
  const dy = p[1] - hinge.y, dz = p[2] - hinge.z
  return [p[0], hinge.y + dy * c - dz * s, hinge.z + dy * s + dz * c]
}

const r2 = (x: number) => (Math.round(x * 100) / 100).toString()
/** The opening's readout: the angle, and past 90 degrees how far past vertical (the arc is representational). */
export function openText(deg: number, _h: { max_open_deg: number }): string {
  const d = Math.round(deg)
  if (d <= 0) return 'Closed'
  if (d <= 90) return `${d} deg open`
  return `${d} deg open: ${d - 90} deg past vertical, representational`
}
export const openShort = (deg: number): string => (Math.round(deg) <= 0 ? 'Closed' : `${Math.round(deg)} deg`)

/** The latch-pad conflict, always as a pair: the derived centres, the printed labels and the gap. Never one set as fact. */
export function latchText(c: CanopyData): { value: string; sub: string } {
  const d = c.latch.derived_centres_fs.map(r2).join(', '), p = c.latch.printed_labels_fs.map(r2).join(', ')
  return { value: `Pad centres FS ${d} (derived)`, sub: `The printed labels read ${p}: ${r2(c.latch.gap_in)} in apart, unresolved` }
}
/** The front cut: representational, its datum is not named in the plans. */
export function frontCutText(c: CanopyData): string {
  return `Front cut about FS ${r2(c.front_cut.fs)}, datum not named (representational)`
}
/** The pad stations, measured forward from the rear cut to each pad's aft edge. */
export function padsText(c: CanopyData): { value: string; sub: string } {
  const l = c.pads.left_aft_edge_fwd_of_cut, r = c.pads.right_aft_edge_fwd_of_cut.map(r2).join(', ')
  return {
    value: `Aft edges forward of FS ${r2(c.rear_cut_fs)}: right ${r}`,
    sub: `Left ${l.map((x, i) => (i === 2 ? `${r2(x)} (safety catch)` : r2(x))).join(', ')}; each pad ${r2(c.pads.length_in)} in long. Hinge pads blue, latch pads green, catch pad red`,
  }
}
/** The A and B checks: heights above the longerons' top (the datum W.L.). */
export function checksText(c: CanopyData): string {
  return `${c.checks.map((k) => `${k.id} ${k.min ? 'at least ' : ''}${r2(k.height_in)} in`).join(', ')}, above WL ${r2(c.checks[0]?.wl0 ?? 0)}`
}

export interface PadRole { label: string; color: number }
/** the three roles of the eight pads (representational colours, told apart; the legend names them) */
export const PAD_ROLES: Record<string, PadRole> = {
  hinge: { label: 'hinge', color: 0x2f6fdc },
  latch: { label: 'latch', color: 0x2fa84f },
  catch: { label: 'safety catch', color: 0xd23b3b },
}

/** the ops with a readout of their own, and what it says (null: none) */
export function canopyKin(opId: string | null, c: CanopyData, openDeg: number): { label: string; value: string; sub: string } | null {
  switch (opId) {
    case CHECK_OP: return { label: 'Canopy height checks', value: checksText(c), sub: 'A is taken 6 in forward of the headrest (the headrest station is fitted); B is taken 15 in forward of the firewall' }
    case CUT_OP: return { label: 'Canopy cuts', value: frontCutText(c), sub: `The rear cut at FS ${r2(c.rear_cut_fs)} is the plans'. The front and rear covers stay on the fuselage` }
    case FRONT_COVER_OP: return { label: 'Front cover', value: frontCutText(c), sub: 'The cover runs from F28 to the front cut' }
    case CARVE_INSIDE_OP: return { label: 'Pads', ...padsText(c) }
    case PADS_OP: return { label: 'Pads', value: 'Hinge (blue, right, 4), latch (green, left, 3), catch (red, left, 1)', sub: '15 BID plies each, wet flox between; the right pads are recessed for the hinges' }
    case HINGE_OP: return { label: 'Canopy opening', value: openText(openDeg, c.hinge), sub: 'Hinged on the right: it swings up and out; the opening arc is representational' }
    case LATCH_OP: { const l = latchText(c); return { label: 'Latch pads', value: l.value, sub: `${l.sub}. Three latches on the left, the handle on the front one` } }
    default: return null
  }
}

/** From the last op of the chapter (the canopy is complete) the readout carries the canopy's CP26 builder weight (N26MS) as a reference row: never in the CG. */
export function canopyRow(ledger: LedgerLite | null, opId: string | null, order: string[]): { value: string; sub: string } | null {
  const r = ledger?.prototype_weights?.rows?.canopy
  if (!r || !opId || !/^f18\./.test(opId) || order.indexOf(opId) < order.indexOf(CANOPY_REF_FROM)) return null
  return { value: `Canopy (CP26 builder weight, N26MS): ${r.weight_lb.toFixed(1)} lb, reference, not in CG`, sub: r.note }
}
