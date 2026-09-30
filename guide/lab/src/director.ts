// Adapted from AirsupHQ/airsup-lab src/director.ts (MIT); see NOTICE.
// Changes: kept the sim-time step list and the cursor that really clicks controls (move/click/drag); dropped their tours, brand and end card, took the camera out (shots fly when an op chip is clicked), added named actions, an orbit step, our own title and end cards, a busy flag so the page can tell the cursor's clicks from a person's, and the pure chapterTour builder.
import { tourSteps } from './logic/tour'
import { visibleOps } from './logic/graph'
import { DONE_T, PLAY_ADVANCE_T } from './logic/anim'
import type { GraphLite } from './logic/graph'

export type Step =
  | { t: number; move: string; dur: number; dx?: number; dy?: number }
  | { t: number; click: string }
  | { t: number; drag: string; from: number; to: number; dur: number }
  | { t: number; act: string; arg?: number }
  | { t: number; cursor: 'show' | 'hide' }
  /** turn the camera about the orbit target by `deg` degrees over `dur` seconds */
  | { t: number; orbit: { dur: number; deg: number } }
  /** fade a card in (with text) or out (null) */
  | { t: number; card: { title: string; sub?: string } | null; dur: number }
  /** the tourSteps index that the film is on from here */
  | { t: number; seg: number }

export interface DirectorHooks {
  /** a named action of the page (reset, finish, ...) */
  act(name: string, arg?: number): void
  /** the orbit step, called every frame with progress k in [0, 1]; `first` is true on the frame it starts */
  orbit(k: number, deg: number, first: boolean): void
}

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const sec = (s: Step) => ('dur' in s ? s.dur : 'orbit' in s ? s.orbit.dur : 0)

/** A scripted tour: a visible cursor that really clicks the page's own controls. Advances on sim time only, so a fixed step gives the same frames every run. */
export class Director {
  private steps: Step[] = []
  private idx = 0
  private t0 = 0
  active = false
  /** true only while the director itself is dispatching a click or an input event */
  busy = false
  /** the tourSteps index the film is on */
  seg = -1
  duration = 0
  onEnd: (() => void) | null = null
  readonly cursor: HTMLDivElement
  private cx = -100
  private cy = -100
  private move: { x0: number; y0: number; x1: number; y1: number; t: number; dur: number } | null = null
  private drag: { el: HTMLInputElement; from: number; to: number; t: number; dur: number } | null = null
  private orbit: { t: number; dur: number; deg: number; first: boolean } | null = null
  private cardAnim: { from: number; to: number; t: number; dur: number } | null = null
  private cardOpacity = 0
  private clickT = -10
  private ring: SVGElement
  private ripple: HTMLElement
  private card: HTMLElement

  constructor(private hooks: DirectorHooks) {
    const c = document.createElement('div')
    c.id = 'cursor'
    c.setAttribute('aria-hidden', 'true')
    c.innerHTML = `<svg width="30" height="30" viewBox="0 0 30 30"><circle cx="15" cy="15" r="11" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.9)" stroke-width="1.6"/></svg>
      <svg class="arrow" width="18" height="22" viewBox="0 0 18 22"><path d="M2 1.5v16.2l4.3-4.1 2.9 6.6 2.7-1.2-2.9-6.5h6.1z" fill="#fff" stroke="#0b0f17" stroke-width="1.3" stroke-linejoin="round"/></svg>
      <span class="ripple"></span>`
    document.body.appendChild(c) // above the control cards, which sit over the canvas
    this.cursor = c
    this.ring = c.querySelector('svg') as SVGElement
    this.ripple = c.querySelector('.ripple') as HTMLElement
    const card = document.createElement('div')
    card.id = 'endcard'
    card.setAttribute('aria-hidden', 'true')
    card.innerHTML = '<div class="ec-in"><span class="ec-t"></span><span class="ec-s"></span></div>'
    document.body.appendChild(card)
    this.card = card
  }

  private center(sel: string, dx = 0, dy = 0) {
    const el = document.querySelector<HTMLElement>(sel)
    if (!el) return { x: this.cx, y: this.cy }
    const r = el.getBoundingClientRect()
    return { x: r.left + r.width / 2 + dx, y: r.top + r.height / 2 + dy }
  }

  private thumb(el: HTMLInputElement, v: number) {
    const r = el.getBoundingClientRect()
    const min = Number(el.min), max = Number(el.max)
    const half = 8
    return { x: r.left + half + ((r.width - 2 * half) * (v - min)) / (max - min || 1), y: r.top + r.height / 2 }
  }

  private setCard(o: number) {
    this.cardOpacity = o
    this.card.style.opacity = o.toFixed(3)
    this.card.style.display = o > 0.001 ? 'grid' : 'none'
  }

  load(steps: Step[]) {
    this.steps = steps.slice().sort((a, b) => a.t - b.t) // stable: steps at one time keep their order
    this.duration = Math.max(...this.steps.map((s) => s.t + sec(s))) + 0.6
    this.idx = 0
    this.active = true
    this.seg = 0
    this.move = this.drag = this.orbit = this.cardAnim = null
    this.setCard(0)
    this.cx = window.innerWidth * 0.82
    this.cy = window.innerHeight * 1.05
  }

  start(now: number) {
    this.t0 = now
  }

  stop() {
    this.active = false
    this.busy = false
    this.setCard(0)
    this.cursor.style.opacity = '0'
    this.move = this.drag = this.orbit = this.cardAnim = null
  }

  /** Advance to absolute sim time `now`. Deterministic for a fixed step. */
  update(now: number) {
    if (!this.active) return
    const t = now - this.t0
    this.busy = true
    try {
      while (this.idx < this.steps.length && this.steps[this.idx].t <= t) {
        const s = this.steps[this.idx++]
        if ('move' in s) {
          const p = this.center(s.move, s.dx, s.dy)
          this.move = { x0: this.cx, y0: this.cy, x1: p.x, y1: p.y, t: s.t, dur: s.dur }
        } else if ('click' in s) {
          this.clickT = s.t
          document.querySelector<HTMLElement>(s.click)?.click()
        } else if ('drag' in s) {
          const el = document.querySelector<HTMLInputElement>(s.drag)
          if (el) this.drag = { el, from: s.from, to: s.to, t: s.t, dur: s.dur }
        } else if ('act' in s) this.hooks.act(s.act, s.arg)
        else if ('cursor' in s) this.cursor.style.opacity = s.cursor === 'show' ? '1' : '0'
        else if ('orbit' in s) this.orbit = { t: s.t, dur: s.orbit.dur, deg: s.orbit.deg, first: true }
        else if ('card' in s) {
          if (s.card) {
            this.card.querySelector('.ec-t')!.textContent = s.card.title
            this.card.querySelector('.ec-s')!.textContent = s.card.sub ?? ''
          }
          this.cardAnim = { from: this.cardOpacity, to: s.card ? 1 : 0, t: s.t, dur: s.dur }
        } else if ('seg' in s) this.seg = s.seg
        if (!this.active) return // an action may end the tour
      }
      if (this.move) {
        const k = Math.min(1, (t - this.move.t) / this.move.dur)
        const e = ease(k)
        const m = this.move
        const bow = Math.sin(Math.PI * e) * Math.min(60, Math.hypot(m.x1 - m.x0, m.y1 - m.y0) * 0.12)
        const nx = -(m.y1 - m.y0), ny = m.x1 - m.x0
        const nl = Math.hypot(nx, ny) || 1
        this.cx = m.x0 + (m.x1 - m.x0) * e + (nx / nl) * bow
        this.cy = m.y0 + (m.y1 - m.y0) * e + (ny / nl) * bow
        if (k >= 1) this.move = null
      }
      if (this.drag) {
        const d = this.drag
        const k = Math.min(1, (t - d.t) / d.dur)
        const v = d.from + (d.to - d.from) * ease(k)
        const next = String(Math.round(v))
        if (d.el.value !== next) { // only a changed value is an input event, as with a real thumb
          d.el.value = next
          d.el.dispatchEvent(new Event('input', { bubbles: true }))
        }
        const p = this.thumb(d.el, v)
        this.cx = p.x
        this.cy = p.y
        if (k >= 1) this.drag = null
      }
      if (this.orbit) {
        const o = this.orbit
        const k = Math.min(1, Math.max(0, (t - o.t) / o.dur))
        this.hooks.orbit(k, o.deg, o.first)
        o.first = false
        if (k >= 1) this.orbit = null
      }
    } finally {
      this.busy = false
    }
    if (this.cardAnim) {
      const a = this.cardAnim
      const k = Math.min(1, Math.max(0, (t - a.t) / a.dur))
      this.setCard(a.from + (a.to - a.from) * ease(k))
      if (k >= 1) this.cardAnim = null
    }
    const rk = (t - this.clickT) / 0.55
    if (rk >= 0 && rk <= 1) {
      this.ripple.style.opacity = (0.9 * (1 - rk)).toFixed(3)
      this.ripple.style.transform = `scale(${(0.3 + 1.1 * rk).toFixed(3)})`
    } else this.ripple.style.opacity = '0'
    const pressed = (t - this.clickT >= 0 && t - this.clickT < 0.14) || !!this.drag
    this.ring.style.transform = pressed ? 'scale(0.8)' : 'scale(1)'
    this.cursor.style.transform = `translate(${this.cx.toFixed(1)}px, ${this.cy.toFixed(1)}px)`
    if (t > this.duration) {
      this.stop()
      this.onEnd?.()
    }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// A chapter film. Pure: the same graph and variant give the same steps. The page supplies the actions:
//   reset   home view, nothing selected, section off; part names and load paths forced on for the tour only (a tour-scoped override, never storage)
//   finish  nothing selected (every op built), home view, canard upright
//   closeup fly to the close shot of the cut face
// ---------------------------------------------------------------------------------------------------------------------

/** The build clock runs this much faster than a person would watch it while a tour plays, so the whole film stays near 80 s. */
export const TOUR_BUILD_RATE = 2.5
/** the chapter the recorder's `canard` film shows (the Roncz canard build) */
export const CHAPTER = 30

interface LayupLite { semi_span?: number; nodes?: Record<string, { op: string; bl_max: number | null }> }
export interface TourGraph extends GraphLite {
  plies?: Record<string, { op: string }[]>
  layup?: LayupLite | null
}

/** Seconds the Play button takes to lay `n` plies and cure the op, in film time (the tour runs the build clock at TOUR_BUILD_RATE). */
export const playSeconds = (n: number) => ((n - 1) * PLAY_ADVANCE_T + DONE_T) / TOUR_BUILD_RATE + 0.35

/** The outboard limit of an op's layup: the largest bl_max of its plies (a ply with no limit runs the whole span). */
export function layupSpan(graph: TourGraph, opId: string): number {
  const semi = graph.layup?.semi_span ?? 70
  let hi = 0
  for (const n of Object.values(graph.layup?.nodes ?? {})) if (n.op === opId) hi = Math.max(hi, n.bl_max ?? semi)
  return hi
}

/** Where to cut for an op: 10 in for the shear web, 20 in for caps and skins, always inside the op's own layup. */
export function cutStation(graph: TourGraph, opId: string): number {
  const want = opId.includes('shear-web') ? 10 : 20
  return Math.max(0, Math.min(want, layupSpan(graph, opId)))
}

const SEC_ON = '#section-on', SEC_BL = '#section-bl'
/** where the film ends its cut */
const END_BL = 20

/** The chapter a tour plays, as 2.1 chose it: the selected op's chapter; nothing selected (or an op this variant does not show) tours the variant's
 * first real chapter; a stub-only chapter falls back to that too. Undefined when the variant has nothing to build. */
export function tourChapter(graph: GraphLite, variant: string, selectedId: string | null): number | undefined {
  const vis = visibleOps(graph, variant)
  const cur = vis.find((o) => o.id === selectedId)
  if (cur && tourSteps(graph, variant, cur.chapter).length) return cur.chapter
  return vis.find((o) => !o.stub)?.chapter
}

export function chapterTour(graph: TourGraph, variant: string, chapter: number): Step[] {
  const ops = tourSteps(graph, variant, chapter)
  const nPlies = (id: string) => Object.values(graph.plies ?? {}).flat().filter((r) => r.op === id).length
  const hasCut = !!graph.layup?.nodes
  const semi = graph.layup?.semi_span ?? 70
  let bl = Math.round(semi / 2) // where the slider sits before the first cut (the page's own default)
  const s: Step[] = []
  const name = variant === 'gu' ? 'GU' : 'Roncz'
  s.push({ t: 0, act: 'reset' }, { t: 0, seg: 0 })
  s.push({ t: 0, card: { title: `${name} canard`, sub: `Chapter ${chapter}` }, dur: 0.4 }, { t: 2.3, card: null, dur: 0.6 })
  s.push({ t: 2.6, cursor: 'show' })
  let t = 3.0
  ops.forEach((o, i) => {
    const chip = `#chips button[data-op="${o.op}"]`
    s.push({ t, move: chip, dur: 0.55 }, { t: t + 0.6, click: chip }, { t: t + 0.6, seg: i }) // the click flies to the op's shot (and turns the canard over for the bottom side)
    const n = nPlies(o.op)
    if (!n) { t += 0.6 + 1.7; return } // no plies: a short dwell on its shot
    t += 0.6 + 1.9
    s.push({ t, move: '#play', dur: 0.4 }, { t: t + 0.45, click: '#play' })
    t += 0.5 + playSeconds(n)
    if (hasCut) {
      const to = cutStation(graph, o.op)
      s.push({ t, move: SEC_ON, dur: 0.4 }, { t: t + 0.45, click: SEC_ON })
      s.push({ t: t + 0.6, drag: SEC_BL, from: bl, to, dur: 1.1 })
      bl = to
      s.push({ t: t + 3.0, move: SEC_ON, dur: 0.4 }, { t: t + 3.45, click: SEC_ON }) // hold on the cut face, then close it
      t += 3.9
    }
  })
  // the finished canard: cut open at B.L. 20, a close slow 3/4 turn about the cut face (flows and part names on), then the closing card
  s.push({ t, act: 'finish' })
  if (hasCut) {
    s.push({ t: t + 0.2, move: SEC_ON, dur: 0.4 }, { t: t + 0.7, click: SEC_ON })
    if (bl !== END_BL) s.push({ t: t + 0.9, drag: SEC_BL, from: bl, to: END_BL, dur: 1.0 })
  }
  s.push({ t: t + 1.9, cursor: 'hide' })
  s.push({ t: t + 2.0, act: 'closeup' }) // a 1.8 s flight to the close shot
  s.push({ t: t + 4.0, orbit: { dur: 9, deg: -40 } })
  s.push({ t: t + 13.4, card: { title: `Canard, chapter ${chapter}`, sub: 'Build rehearsal' }, dur: 1.0 })
  s.push({ t: t + 16.2, act: 'noop' })
  return s
}
