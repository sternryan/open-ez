// The rehearsal's transport: which step and beat is playing, on sim time only. No DOM, no three.js, no wall clock.
// main.ts ticks it from step(dt) and owns everything it shows (the camera, the gloves, the nav log).

import { CAPTION_ONLY_SECONDS, type Beat } from './logic/actions'

export type Speed = 1 | 4 | 16

export interface TickResult {
  step: string
  beat: Beat | null
  /** progress through the current beat, 0..1 */
  k: number
  /** true on the tick that entered a new step */
  changed: boolean
}

const EPS = 1e-9

export class Player {
  private idx = 0
  private t = 0
  private _playing = false
  private _speed: Speed = 1
  private beats: Beat[][]

  constructor(beatsByStep: Map<string, Beat[]>, private order: string[]) {
    // a step with no beats plays as one caption-only beat, so play-through never stalls on it
    this.beats = order.map((id) => {
      const b = beatsByStep.get(id)
      return b && b.length ? b : [{ t: 0, dur: CAPTION_ONLY_SECONDS, action: null, caption: id }]
    })
  }

  get playing(): boolean { return this._playing }
  get speed(): number { return this._speed }
  get step(): string { return this.order[this.idx] ?? '' }

  /** At the end of the last step, play starts over from the first. */
  play(): void {
    if (!this.order.length) return
    if (this.atEnd()) { this.idx = 0; this.t = 0 }
    this._playing = true
  }
  pause(): void { this._playing = false }
  next(): void { if (this.idx < this.order.length - 1) { this.idx++; this.t = 0 } }
  prev(): void { if (this.idx > 0) this.idx--; this.t = 0 }
  /** Jump to the start of a step; an unknown id is ignored. The play state is kept. */
  seekStep(id: string): void {
    const i = this.order.indexOf(id)
    if (i < 0) return
    this.idx = i
    this.t = 0
  }
  setSpeed(x: Speed): void { if (x === 1 || x === 4 || x === 16) this._speed = x }

  /**
   * Advance sim time by dt (scaled by speed). A tick enters at most one new step and drops the rest of its time, so every step
   * gets its own camera move and nav update however large dt is.
   */
  tick(dt: number): TickResult {
    if (!this.order.length) return { step: '', beat: null, k: 0, changed: false }
    let changed = false
    if (this._playing) {
      const d = Number.isFinite(dt) && dt > 0 ? dt * this._speed : 0
      this.t += d
      if (this.t >= this.total(this.idx) - EPS) {
        if (this.idx < this.order.length - 1) {
          this.idx++
          this.t = 0
          changed = true
        } else {
          this.t = this.total(this.idx)
          this._playing = false
        }
      }
    }
    const { beat, k } = this.at()
    return { step: this.step, beat, k, changed }
  }

  private total(i: number): number {
    const b = this.beats[i]
    const last = b[b.length - 1]
    return Math.max(EPS, last.t + last.dur)
  }

  private atEnd(): boolean {
    return this.idx === this.order.length - 1 && this.t >= this.total(this.idx) - EPS
  }

  private at(): { beat: Beat; k: number } {
    const b = this.beats[this.idx]
    let beat = b[b.length - 1]
    for (const x of b) if (this.t < x.t + x.dur - EPS) { beat = x; break }
    const k = beat.dur > 0 ? (this.t - beat.t) / beat.dur : 1
    return { beat, k: Math.min(1, Math.max(0, k)) }
  }
}
