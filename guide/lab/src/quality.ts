// Quality tiers for the lab: one table, plus the pure rules that pick a starting tier and step down when frames run long.
// No three.js and no DOM in here, so node tests can run it.

export type Tier = 'high' | 'mid' | 'low'
export const TIER_ORDER: Tier[] = ['high', 'mid', 'low']

export interface TierSpec {
  /** screen-space ambient occlusion, its sample count and its buffer size as a fraction of the frame */
  ao: boolean
  aoSamples: number
  aoScale: number
  /** depth of field (the lens blur behind the focus) and its tap count */
  dof: boolean
  dofTaps: number
  /** the bloom glow chain */
  bloom: boolean
  /** multisample count for the scene target (0 = none) */
  msaa: number
  /** cap on the device pixel ratio the canvas renders at */
  dprCap: number
  /** ceiling on the pixels drawn per frame; the pixel ratio drops below 1 to stay under it (Infinity = none) */
  maxPixels: number
  /** key light shadow map edge, in texels (0 = no shadows at all) */
  shadowMap: number
  /** SURF_CHEAP: every surface uses the flat lighting (one baked key and a sky/ground gradient: no lights, shadows or image-based light), and
   *  the composite weave and foam cells drop to their albedo-only shader */
  cheapShaders: boolean
}

export const TIERS: Record<Tier, TierSpec> = {
  high: { ao: true, aoSamples: 8, aoScale: 0.5, dof: true, dofTaps: 14, bloom: true, msaa: 4, dprCap: 2, maxPixels: Infinity, shadowMap: 4096, cheapShaders: false },
  mid: { ao: true, aoSamples: 6, aoScale: 0.4, dof: false, dofTaps: 0, bloom: true, msaa: 2, dprCap: 1.5, maxPixels: Infinity, shadowMap: 2048, cheapShaders: false },
  low: { ao: false, aoSamples: 0, aoScale: 0.4, dof: false, dofTaps: 0, bloom: false, msaa: 0, dprCap: 1, maxPixels: 500_000, shadowMap: 0, cheapShaders: true },
}

export const TIER_LABEL: Record<Tier, string> = { high: 'High', mid: 'Med', low: 'Low' }

/** The pixel ratio a tier draws at: the device's, under the tier's cap, and low enough that the frame stays under its pixel ceiling. */
export function tierPixelRatio(spec: TierSpec, deviceRatio: number, cssW: number, cssH: number): number {
  const fit = Math.sqrt(spec.maxPixels / Math.max(1, cssW * cssH))
  return Math.max(0.25, Math.min(deviceRatio || 1, spec.dprCap, fit))
}

/** ?q= value to a tier. 'medium' is accepted as a spelling of 'mid'. Anything else is not a forced tier. */
export function parseTier(q: string | null | undefined): Tier | null {
  const v = (q ?? '').trim().toLowerCase()
  if (v === 'high' || v === 'low') return v
  if (v === 'mid' || v === 'medium') return 'mid'
  return null
}

export interface Device { coarse: boolean; width: number; height: number }

/**
 * Where a session starts. Desktops and iPad-class devices (a coarse pointer with a large viewport) start on high; phones start on
 * medium. "Large" is the shorter side of the viewport being at least 700 CSS px: an iPad is 768 or more in portrait, a phone is under 500.
 */
export function startTier(d: Device): Tier {
  if (!d.coarse) return 'high'
  return Math.min(d.width, d.height) >= 700 ? 'high' : 'mid'
}

// ---- automatic step-down ----
/** A frame slower than this is "long". 34, not 33: a display held at 30 Hz (Low Power Mode) reads 33.3 ms and is not slow. */
export const SLOW_MS = 34
/** The median of the frames in this much recent time has to be slow before a tier drops. */
export const WINDOW_MS = 1500
/** At least this many frames must be in the window (a stalled device may only manage a few per window). */
export const MIN_FRAMES = 3
/** After a drop the next frames are ignored for this long: the new targets and shader variants compile on them. */
export const SETTLE_MS = 1000
/** One frame counts for at most this much (a tab coming back from the background reports seconds). */
export const FRAME_CAP_MS = 500

export interface StepState { tier: Tier; frames: number[]; sum: number; settle: number }

/** `settle` is how many ms of frames to ignore first (the page's own start-up compiles). */
export const initialStep = (tier: Tier, settle = 0): StepState => ({ tier, frames: [], sum: 0, settle })

export function median(xs: number[]): number {
  if (!xs.length) return 0
  const s = xs.slice().sort((a, b) => a - b)
  return s[s.length >> 1]
}

/**
 * Feed one frame time (ms). Returns the next state; when the returned tier differs from the input's, the caller applies it.
 * It drops one tier when the median of the last WINDOW_MS of frames is over SLOW_MS, never goes below low, and never steps up:
 * a session that dropped stays down (the owner can raise it with the control), so it cannot flap between two tiers.
 */
export function nextTier(state: StepState, frameMs: number): StepState {
  const ms = Math.min(Math.max(frameMs, 0), FRAME_CAP_MS)
  if (state.settle > 0) return { ...state, settle: Math.max(0, state.settle - ms) }
  const frames = state.frames.concat(ms)
  let sum = state.sum + ms
  // keep the newest frames that still cover the window
  while (frames.length > 1 && sum - frames[0] >= WINDOW_MS) sum -= frames.shift()!
  const idx = TIER_ORDER.indexOf(state.tier)
  if (sum >= WINDOW_MS && frames.length >= MIN_FRAMES && median(frames) > SLOW_MS && idx < TIER_ORDER.length - 1) {
    return { tier: TIER_ORDER[idx + 1], frames: [], sum: 0, settle: SETTLE_MS }
  }
  return { tier: state.tier, frames, sum, settle: 0 }
}

// ---- adaptive resolution (the low tier only) ----
// Low is the last tier, so a device that still misses the frame rate there has nothing left to drop but pixels. While on low the
// canvas resolution steps down (never back up within a tier: no flapping) until most frames land on the display's refresh.
/** Shrink while a quarter of the recent frames run over this. A 60 Hz display with a frame to spare reads 16.7 ms. */
export const RES_SLOW_MS = 20
/** Each shrink aims the frame time at this, but never cuts the pixel count by more than half in one step. */
export const RES_AIM_MS = 12
export const RES_WINDOW_MS = 600
export const RES_SETTLE_MS = 800
/** The pixel-count multiplier never goes below this. */
export const RES_MIN = 0.08

export interface ResState { scale: number; frames: number[]; sum: number; settle: number }
export const initialRes = (settle = 0): ResState => ({ scale: 1, frames: [], sum: 0, settle })

export function percentile(xs: number[], p: number): number {
  if (!xs.length) return 0
  const s = xs.slice().sort((a, b) => a - b)
  return s[Math.min(s.length - 1, Math.floor(p * s.length))]
}

/** Feed one frame time (ms); returns the next state. `scale` multiplies the pixel count the tier would draw. */
export function nextRes(state: ResState, frameMs: number): ResState {
  const ms = Math.min(Math.max(frameMs, 0), FRAME_CAP_MS)
  if (state.settle > 0) return { ...state, settle: Math.max(0, state.settle - ms) }
  const frames = state.frames.concat(ms)
  const sum = state.sum + ms
  if (sum < RES_WINDOW_MS || frames.length < 3) return { ...state, frames, sum }
  const p75 = percentile(frames, 0.75)
  if (p75 > RES_SLOW_MS && state.scale > RES_MIN) {
    const f = Math.min(0.9, Math.max(0.5, RES_AIM_MS / median(frames)))
    return { scale: Math.max(RES_MIN, state.scale * f), frames: [], sum: 0, settle: RES_SETTLE_MS }
  }
  return { ...state, frames: [], sum: 0 }
}
