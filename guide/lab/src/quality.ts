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
/**
 * Frames after a step or scene change are ignored for this long. Unsourced: a step swap and the shader compile
 * that follows it are a hitch, not the device. One second covers that burst; a device that is still slow once it
 * has passed still steps down.
 */
export const CHANGE_SETTLE_MS = 1000
/** One frame counts for at most this much (a tab coming back from the background reports seconds). */
export const FRAME_CAP_MS = 500
/**
 * A frame at or under this is fast enough to climb a tier. Well under SLOW_MS: a 60 Hz frame (16.7 ms) still counts,
 * and 18–33 ms holds the tier where it is (not slow enough to drop, not fast enough to grow).
 */
export const TIER_FAST_MS = 17
/**
 * Fast frame time before one step up, once a step change has happened since the last tier change. Eight times the
 * 1.5 s drop window, so a short smooth patch cannot flap. A 16x play-through still has about 25 s of fast frames
 * after the long canopy layup, so two of these (low to mid, then mid to high) fit in that tail.
 */
export const TIER_UP_WINDOW_MS = 12_000
/**
 * The same climb when the view never changes step. Longer than the 40 s of 8 ms frames the no-step-up test feeds
 * (those frames do count toward this), so that run stays on the lower tier.
 */
export const TIER_UP_STILL_MS = 48_000

export interface StepState {
  tier: Tier
  frames: number[]
  sum: number
  settle: number
  /** fast frame time (ms) accumulated toward a step up */
  fast: number
  /** a step change has happened since the last tier change, so the shorter up window applies */
  held: boolean
}

/** `settle` is how many ms of frames to ignore first (the page's own start-up compiles). */
export const initialStep = (tier: Tier, settle = 0): StepState => ({ tier, frames: [], sum: 0, settle, fast: 0, held: false })

/** Drop the tier window and ignore the next frames: a step or scene change just happened. Fast-frame credit is kept. */
export function holdTier(state: StepState): StepState {
  return { ...state, frames: [], sum: 0, settle: Math.max(state.settle, CHANGE_SETTLE_MS), held: true }
}

export function median(xs: number[]): number {
  if (!xs.length) return 0
  const s = xs.slice().sort((a, b) => a - b)
  return s[s.length >> 1]
}

/** One tier toward high when the fast credit has covered the up window. Null when it has not, or the tier is already high. */
function stepUp(state: StepState, frames: number[], sum: number, settle: number, fast: number): StepState | null {
  const idx = TIER_ORDER.indexOf(state.tier)
  if (idx <= 0) return null
  const need = state.held ? TIER_UP_WINDOW_MS : TIER_UP_STILL_MS
  if (fast < need) return null
  return { tier: TIER_ORDER[idx - 1], frames: [], sum: 0, settle: SETTLE_MS, fast: 0, held: false }
}

/**
 * Feed one frame time (ms). Returns the next state; when the returned tier differs from the input's, the caller applies it.
 * It drops one tier when the median of the last WINDOW_MS of frames is over SLOW_MS, and never goes below low.
 * It steps back up one tier only after a long run of frames at or under TIER_FAST_MS. A slow frame outside the
 * post-change settle resets that credit. A slow frame inside the settle is the hitch and is ignored both ways;
 * a fast frame there still counts, because a 16x step is shorter than the settle and would otherwise never recover.
 */
export function nextTier(state: StepState, frameMs: number): StepState {
  const ms = Math.min(Math.max(frameMs, 0), FRAME_CAP_MS)
  if (state.settle > 0) {
    const settle = Math.max(0, state.settle - ms)
    const fast = ms <= TIER_FAST_MS ? state.fast + ms : state.fast
    return stepUp(state, state.frames, state.sum, settle, fast) ?? { ...state, settle, fast }
  }
  const frames = state.frames.concat(ms)
  let sum = state.sum + ms
  // keep the newest frames that still cover the window
  while (frames.length > 1 && sum - frames[0] >= WINDOW_MS) sum -= frames.shift()!
  const idx = TIER_ORDER.indexOf(state.tier)
  if (sum >= WINDOW_MS && frames.length >= MIN_FRAMES && median(frames) > SLOW_MS && idx < TIER_ORDER.length - 1) {
    return { tier: TIER_ORDER[idx + 1], frames: [], sum: 0, settle: SETTLE_MS, fast: 0, held: false }
  }
  const fast = ms <= TIER_FAST_MS ? state.fast + ms : 0
  return stepUp(state, frames, sum, 0, fast) ?? { tier: state.tier, frames, sum, settle: 0, fast, held: state.held }
}

// ---- adaptive resolution (the low tier only) ----
// Low is the last tier, so a device that still misses the frame rate there has nothing left to drop but pixels. While on low the
// canvas resolution steps down until most frames land on the display's refresh, and steps back up only after a longer stretch of
// fast frames (hysteresis: a short smooth patch must not flap back up into the next drop). The tier steps back up on its own,
// slower clock (nextTier): a session that only dipped for a heavy layup is not left on the cheap tier for the rest of the build.
/** Shrink while a quarter of the recent frames run over this. A 60 Hz display with a frame to spare reads 16.7 ms. */
export const RES_SLOW_MS = 20
/** Each shrink aims the frame time at this, but never cuts the pixel count by more than half in one step. */
export const RES_AIM_MS = 12
export const RES_WINDOW_MS = 600
export const RES_SETTLE_MS = 800
/**
 * Step up only when p75 stays at or under this for RES_UP_WINDOW_MS. 17 is under the 20 ms down budget, and a 60 Hz frame
 * (16.7 ms) still counts, so a display that is actually keeping up can climb. 18–20 ms holds: not slow enough to drop, not
 * fast enough to grow.
 */
export const RES_FAST_MS = 17
/** Fast time required before a step up. Longer than the 600 ms down window, so the two cannot flap. */
export const RES_UP_WINDOW_MS = 20_000
/** A step up multiplies the pixel count by at most this, and never past 1. */
export const RES_UP_MAX = 2
/**
 * The pixel-count multiplier never goes below this. Unsourced. 0.08 is about 28% on a side (a 1600 px frame becomes
 * ~450 px) and reads as the blocky picture from a long session. 0.2 keeps about 45% on a side, so an edge still reads
 * as an edge, and a slow device can still reach it in the half-steps (1 → 0.5 → 0.25 → 0.2).
 */
export const RES_MIN = 0.2

export interface ResState { scale: number; frames: number[]; sum: number; settle: number; fast: number }
export const initialRes = (settle = 0): ResState => ({ scale: 1, frames: [], sum: 0, settle, fast: 0 })

/**
 * Drop the resolution window and ignore the next frames: a step or scene change just happened.
 * Fast-frame credit is kept. Only this settle window is excluded, so a run of short steps can still recover.
 */
export function holdRes(state: ResState): ResState {
  return { ...state, frames: [], sum: 0, settle: Math.max(state.settle, CHANGE_SETTLE_MS) }
}

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
    return { scale: Math.max(RES_MIN, state.scale * f), frames: [], sum: 0, settle: RES_SETTLE_MS, fast: 0 }
  }
  // not a down step. A window whose p75 is well under the budget adds to the up clock; anything slower resets it.
  const quick = p75 <= RES_FAST_MS
  const fast = quick ? state.fast + sum : 0
  if (quick && fast >= RES_UP_WINDOW_MS && state.scale < 1) {
    const room = RES_SLOW_MS / Math.max(p75, 1)
    const factor = Math.min(RES_UP_MAX, Math.max(1.2, room))
    const scale = Math.min(1, state.scale * factor)
    if (scale > state.scale) return { scale, frames: [], sum: 0, settle: RES_SETTLE_MS, fast: 0 }
  }
  return { ...state, frames: [], sum: 0, fast }
}

// ---- on-screen readout (?hud=1) ----
// The panel is a view of these pure numbers. The page owns the DOM and the clock; tests check the text and the window here.

/** How much recent frame time the readout's median and p75 cover. */
export const HUD_WINDOW_MS = 2000
/** The panel keeps this many tier and resolution transitions, newest last. */
export const HUD_LOG_KEEP = 4

export interface FrameWindow { frames: number[]; sum: number }
export const emptyFrames = (): FrameWindow => ({ frames: [], sum: 0 })

/** Append one frame time and drop the oldest until the window is about `windowMs` long. */
export function pushFrameWindow(w: FrameWindow, frameMs: number, windowMs = HUD_WINDOW_MS): FrameWindow {
  const ms = Math.min(Math.max(frameMs, 0), FRAME_CAP_MS)
  const frames = w.frames.concat(ms)
  let sum = w.sum + ms
  while (frames.length > 1 && sum - frames[0] >= windowMs) sum -= frames.shift()!
  return { frames, sum }
}

export function frameStats(w: FrameWindow): { n: number; medianMs: number; p75Ms: number } {
  return { n: w.frames.length, medianMs: median(w.frames), p75Ms: percentile(w.frames, 0.75) }
}

export interface HudTransition {
  /** ms since the page started feeding frames (wall clock, owned by the page) */
  atMs: number
  kind: 'tier' | 'res'
  from: string
  to: string
  step: string
}

export interface HudSnapshot {
  tier: Tier
  auto: boolean
  resScale: number
  pixelRatio: number
  devicePixelRatio: number
  medianMs: number
  p75Ms: number
  /** how many times the tier has changed since load, and the wall time of the last change */
  tierSteps: number
  resSteps: number
  lastTierAtMs: number | null
  lastResAtMs: number | null
  step: string
  log: HudTransition[]
}

export function noteTransition(log: HudTransition[], next: HudTransition): HudTransition[] {
  const out = log.concat(next)
  return out.length > HUD_LOG_KEEP ? out.slice(out.length - HUD_LOG_KEEP) : out
}

const hudAt = (ms: number | null): string => (ms === null ? '—' : `${(ms / 1000).toFixed(1)}s`)

/** The panel text. One snapshot, so the test hook and the screen cannot disagree. */
export function formatHud(m: HudSnapshot): string {
  const lines = [
    `${TIER_LABEL[m.tier]} · ${m.auto ? 'auto' : 'manual'}`,
    `res ${m.resScale.toFixed(2)} · px ${m.pixelRatio.toFixed(2)} / dpr ${m.devicePixelRatio.toFixed(2)}`,
    `med ${m.medianMs.toFixed(1)} · p75 ${m.p75Ms.toFixed(1)} ms`,
    `tier ×${m.tierSteps} @ ${hudAt(m.lastTierAtMs)} · res ×${m.resSteps} @ ${hudAt(m.lastResAtMs)}`,
    m.step || '—',
    ...m.log.map((t) => `${(t.atMs / 1000).toFixed(1)}s ${t.kind} ${t.from} -> ${t.to} ${t.step || '—'}`),
  ]
  return lines.join('\n')
}
