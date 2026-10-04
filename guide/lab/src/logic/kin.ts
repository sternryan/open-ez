/**
 * The elevator and nose-gear kinematics for the lab, re-implemented from core/elevators_kin.py and core/nose_gear_kin.py (the Python
 * kernels are the reference: tests/kin.test.ts compares these functions with numbers the kernels computed, tests/fixtures/kernels.json).
 * Pure: no three.js, no DOM. Angles in degrees, lengths in inches.
 *
 * Elevator: a point rotates about the hinge line (axis along the span) by `degDown`, positive = trailing edge down:
 *   x' = hx + dx cos t + dz sin t,  z' = hz - dx sin t + dz cos t   (x chord aft, z up; the canard frame).
 * Nose gear: the strut turns about the NG6 pivot (axis along B.L.); its angle from vertical runs linearly from theta_down to theta_up
 * with the crank, and the crank turns 10.8 for full travel (plans-1980:p73).
 */

import { CUT_OP, HINGE_OP, liftDuration, openDuration } from './canopy'
import { SPAR_FIT_OP, STICK_OP, slideDuration } from './m25'

// ---- elevators (core/elevators_kin.py) ----
export interface ElevatorKin {
  hinge_xz: [number, number]
  travel: { up_target_deg: number; up_floor_deg: number; down_deg: number }
  hang_cg: { dx: number; dz: number; note: string; fitted: boolean }
}

export function rotateAboutHinge(pt: [number, number], hinge: [number, number], degDown: number): [number, number] {
  const [px, pz] = pt, [hx, hz] = hinge
  const dx = px - hx, dz = pz - hz
  const t = (degDown * Math.PI) / 180
  return [hx + dx * Math.cos(t) + dz * Math.sin(t), hz - dx * Math.sin(t) + dz * Math.cos(t)]
}

/** The pitch (degrees, in (-180, 180]) at which an elevator hung on its hinge line settles, for a CG at (cgDx, cgDz) from the hinge. */
export function hangPitchDeg(cgDx: number, cgDz: number): number {
  if (Math.abs(cgDx) < 1e-12 && Math.abs(cgDz) < 1e-12) throw new Error('CG cannot be at the hinge.')
  const phi = (Math.atan2(cgDz, cgDx) * 180) / Math.PI
  let theta = -90 - phi
  while (theta <= -180) theta += 360
  while (theta > 180) theta -= 360
  return theta
}
export const hangsNoseDown = (cgDx: number, cgDz: number): boolean => { const p = hangPitchDeg(cgDx, cgDz); return p > 0 && p < 180 }

export type UpTravel = 'below floor' | 'floor only' | 'target'
export function classifyUpTravel(deg: number, floor = 12.5, target = 15): UpTravel {
  if (deg < floor) return 'below floor'
  if (deg < target) return 'floor only'
  return 'target'
}

/** An elevator pose (TE-down degrees; the hang's pitch is nose down = the leading edge falls = this angle negative) for a moment of the checks. */
const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const clamp01 = (x: number) => Math.min(1, Math.max(0, x))

/** Travel check, in sim seconds since the op was picked: wait for the camera, neutral to the down limit, hold, then to the up target and stay. */
export const TRAVEL = { wait: 1.0, down: 1.4, hold: 0.6, up: 1.8 }
export function travelAngle(t: number, k: { up_target_deg: number; down_deg: number }): number {
  const a = t - TRAVEL.wait
  if (a <= 0) return 0
  if (a < TRAVEL.down) return k.down_deg * ease(a / TRAVEL.down)
  const b = a - TRAVEL.down
  if (b < TRAVEL.hold) return k.down_deg
  const c = clamp01((b - TRAVEL.hold) / TRAVEL.up)
  return k.down_deg + (-k.up_target_deg - k.down_deg) * ease(c)
}
export const travelDuration = (): number => TRAVEL.wait + TRAVEL.down + TRAVEL.hold + TRAVEL.up

/** What the travel readout says for a TE-down angle: "Up 15.0 deg  (target 15, floor 12.5)", "Down 30.0 deg  (limit 30)" or "Neutral". */
export function travelText(degDown: number, k: { up_target_deg: number; up_floor_deg: number; down_deg: number }): string {
  const f = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
  const g = (x: number) => String(Math.round(x * 100) / 100)
  if (Math.abs(degDown) < 0.05) return 'Neutral'
  if (degDown < 0) return `Up ${f(-degDown)} deg  (target ${g(k.up_target_deg)}, floor ${g(k.up_floor_deg)})`
  return `Down ${f(degDown)} deg  (limit ${g(k.down_deg)})`
}

/**
 * Hang test: each elevator comes off the canard (it slides aft by `slide_in`, on its hinge line, to hang clear of it), then swings to the
 * hang pitch like a damped pendulum, in sim seconds. The elevators built apart (cores, skins) are already that far aft.
 */
export const HANG = { wait: 0.8, slide: 1.0, decay: 1.7, period: 1.7 }
/** how far aft of the canard an elevator is held while it is built (chapter 11, before the hinges) and while it hangs, in */
export const APART_IN = 10
export function hangState(t: number, pitchDeg: number): { slide: number; degDown: number } {
  const slide = APART_IN * ease(clamp01((t - HANG.wait) / HANG.slide))
  const s = t - HANG.wait - HANG.slide
  if (s <= 0) return { slide, degDown: 0 }
  // pitch is nose down positive; the TE-down angle is its negative
  const swing = 1 - Math.exp(-HANG.decay * s) * Math.cos((2 * Math.PI * s) / HANG.period)
  return { slide, degDown: -pitchDeg * swing }
}
export const hangDuration = (): number => HANG.wait + HANG.slide + 6
export function hangText(pitchDeg: number, noseDown: boolean, settled: boolean): string {
  // rounded to a whole degree, said as "about": the CG it hangs from is illustrative (its note is the readout's sub-line), so a tenth of a degree claims too much
  return `${settled ? 'Hangs' : 'Swinging toward'} ${noseDown ? 'nose down' : 'nose up'}, about ${Math.round(pitchDeg)} deg`
}

// ---- nose gear (core/nose_gear_kin.py) ----
export interface NoseGearKin {
  strut_length: number; axle_wl: number; pivot_wl: number; clearance_wl: number; wl_zero: number
  crank_turns: number; retract_seconds: number; book_seconds: [number, number]; tire_od: number; tire_width: number
  candidates: Record<'plans' | 'manual', { axle_fs: number; cite: string }>
  status: string
}
export type Candidate = 'plans' | 'manual'

export function thetaDownDeg(pivotWl: number, axleWl: number, strutLen: number): number {
  const dz = pivotWl - axleWl
  if (dz > strutLen) throw new Error('Strut length insufficient for vertical drop.')
  const run = Math.sqrt(strutLen ** 2 - dz ** 2)
  return (Math.atan2(run, dz) * 180) / Math.PI
}
export function ng6PivotForAxle(axleFs: number, axleWl: number, pivotWl: number, strutLen: number): [number, number] {
  const dz = pivotWl - axleWl
  if (dz > strutLen) throw new Error('Strut length insufficient for vertical drop.')
  return [axleFs - Math.sqrt(strutLen ** 2 - dz ** 2), pivotWl]
}
export function retractionThetaDeg(t: number, thetaDown: number, thetaUp = 90): number {
  if (!(t >= 0 && t <= 1)) throw new Error('Retraction parameter t must be in [0, 1].')
  return thetaDown + t * (thetaUp - thetaDown)
}
export function thetaUpForClearanceDeg(pivotWl: number, strutLen: number, clearanceWl: number): number {
  const rise = clearanceWl - pivotWl
  if (Math.abs(rise) > strutLen) throw new Error('Strut too short to reach the clearance height.')
  return 90 + (Math.asin(rise / strutLen) * 180) / Math.PI
}
export function crankTurns(t: number, turns = 10.8): number {
  if (!(t >= 0 && t <= 1)) throw new Error('Retraction parameter t must be in [0, 1].')
  return t * turns
}

export interface NosePoints { pivot: [number, number]; axle: [number, number]; thetaDown: number; thetaUp: number }
/** Pivot and axle (model frame: x = F.S., z = W.L. - wl_zero), and the strut's down and retracted angles, for one axle candidate. */
export function nosePoints(k: NoseGearKin, cand: Candidate): NosePoints {
  const axleFs = k.candidates[cand].axle_fs
  const [pfs] = ng6PivotForAxle(axleFs, k.axle_wl, k.pivot_wl, k.strut_length)
  return {
    pivot: [pfs, k.pivot_wl - k.wl_zero], axle: [axleFs, k.axle_wl - k.wl_zero],
    thetaDown: thetaDownDeg(k.pivot_wl, k.axle_wl, k.strut_length), thetaUp: thetaUpForClearanceDeg(k.pivot_wl, k.strut_length, k.clearance_wl),
  }
}
/** The rotation about the pivot (degrees, in the x-z plane as core.landing_gear_book.nose_gear_pose: R_y(-delta)), delta = theta(t) - theta_down. */
export function noseDelta(t: number, p: NosePoints): number {
  return retractionThetaDeg(t, p.thetaDown, p.thetaUp) - p.thetaDown
}
/** The 2x2 of nose_gear_pose (rotation part, rows x then z) and its translation about the pivot, for progress t. */
export function nosePose(t: number, p: NosePoints): { r: [number, number, number, number]; tx: number; tz: number } {
  const a = (-noseDelta(t, p) * Math.PI) / 180
  const c = Math.cos(a), s = Math.sin(a)
  const [px, pz] = p.pivot
  return { r: [c, s, -s, c], tx: px - (c * px + s * pz), tz: pz - (-s * px + c * pz) }
}
/** A point carried by the gear (the axle): where it is at progress t. */
export function noseAxleAt(t: number, p: NosePoints): [number, number] {
  const m = nosePose(t, p)
  return [m.r[0] * p.axle[0] + m.r[1] * p.axle[1] + m.tx, m.r[2] * p.axle[0] + m.r[3] * p.axle[1] + m.tz]
}

/** Retraction progress in sim seconds since the rig op was picked: the camera comes round first (`wait`), then the crank turns for `seconds`. */
export const RIG_WAIT = 2 // the camera takes about 1.8 s to arrive (measured in freeze mode), then the crank turns
export function retractProgress(t: number, seconds: number): number {
  return clamp01((t - RIG_WAIT) / seconds)
}
export function crankText(t: number, turns = 10.8): string {
  const f = (x: number) => (Math.round(x * 10) / 10).toFixed(1)
  return `Crank ${f(crankTurns(t, turns))} of ${f(turns)} turns${t <= 0 ? ' (gear down)' : t >= 1 ? ' (retracted)' : ''}`
}
/** The nose-wheel arm as the readout states it: always both candidates, always the word conflict. Never one station as fact. */
export function noseArmText(cands: number[] | null | undefined, status: string | null | undefined): string | null {
  if (!cands || cands.length < 2) return null
  const [a, b] = cands
  return `Nose wheel arm: F.S. ${a} (plans) / about ${b} (manual): ${status === 'conflict' || !status ? 'conflict' : status}`
}

// ---- the ops that move, and how long a film dwells on each so the motion plays out (sim seconds) ----
export const TRAVEL_OPS = ['r30.elev-uptravel-test', 'r30.elev-travel-check']
export const HANG_OP = 'r30.elev-balance-check'
export const RIG_OP = 'f13.rig-nose-gear'
export const KIN_HOLD: Record<string, number> = {
  [SPAR_FIT_OP]: slideDuration(), // the spar slides in from the side (chapter 14)
  [CUT_OP]: liftDuration(), // the canopy lifts off and turns over on the bench (chapter 18)
  [HINGE_OP]: openDuration(), // the canopy swings open on its right hinges (chapter 18)
  [STICK_OP]: travelDuration() + 0.8, // the stick sweeps the Roncz travel, the pushrod and elevators with it (chapter 16)
  'r30.elev-uptravel-test': travelDuration() + 0.8,
  'r30.elev-travel-check': travelDuration() + 0.8,
  [HANG_OP]: hangDuration() + 0.8,
  [RIG_OP]: RIG_WAIT + 6 + 1.2, // the crank takes 6 s (layup.json extras nose_gear.retract_seconds)
}

// ---- pitch control (core/controls_kin.py; Roncz travel only: 15 up, 30 down, 12.5 the floor) ----
export interface ControlsKin {
  arm_in: number; lever_in: number; cant_forward_deg: number; cant_inboard_deg: number
  up_target_deg: number; up_floor_deg: number; down_deg: number
  pivot_fs: { front: number; rear: number }; tube_bl: number; tube_wl: number; wl_zero: number
  stop_label: string; stop_size_in: [number, number, number]; note: string
}
/** Elevator deflection clipped to [-down, +up] (up positive, as core.controls_kin). */
export const clampDeflectionDeg = (d: number, k: Pick<ControlsKin, 'up_target_deg' | 'down_deg'>): number => Math.max(-k.down_deg, Math.min(k.up_target_deg, d))
export const pushrodStrokeIn = (deflDeg: number, armIn: number): number => armIn * Math.sin((deflDeg * Math.PI) / 180)
/** Stick angle from vertical (degrees, forward positive) for an elevator deflection (up positive). */
export function stickAngleDeg(deflDeg: number, k: Pick<ControlsKin, 'arm_in' | 'lever_in' | 'cant_forward_deg'>): number {
  const s = Math.sin((k.cant_forward_deg * Math.PI) / 180) - pushrodStrokeIn(deflDeg, k.arm_in) / k.lever_in
  if (Math.abs(s) > 1) throw new Error('Stroke exceeds lever capacity.')
  return (Math.asin(s) * 180) / Math.PI
}
/** The stick's direction in the exported frame (x = F.S., y = B.L., z up) at pitch angle `aDeg` and inboard cant `bDeg`. */
export function stickDir(aDeg: number, bDeg: number): [number, number, number] {
  const a = (aDeg * Math.PI) / 180, b = (bDeg * Math.PI) / 180
  return [-Math.sin(a), -Math.cos(a) * Math.sin(b), Math.cos(a) * Math.cos(b)]
}
/** The elevator deflection (up positive) the control sits at for a TE-down travel angle, and back. */
export const deflUpFromDegDown = (degDown: number): number => -degDown
/** What the stick control's readout says: Roncz numbers only. */
export function stickText(deflUp: number, k: { up_target_deg: number; up_floor_deg: number; down_deg: number }): string {
  return travelText(-deflUp, k)
}
