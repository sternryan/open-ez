// Adapted from AirsupHQ/airsup-lab src/ui/labels.ts (MIT); see NOTICE.
// Changes: label text is set with textContent (no innerHTML); each label may carry a leader-dot colour; a stats() readout for tests;
// an opt-in priority rule (logic/declutter.ts) in place of the vertical nudge, where a label that finds no room collapses to its dot.
import * as THREE from 'three'
import { declutter, type Rect } from '../logic/declutter'

export interface LabelDef {
  id: string
  text: string
  sub?: string | (() => string)
  cls?: string
  /** CSS colour of the leader dot */
  color?: string
  /** world position provider; return null to hide */
  at: () => THREE.Vector3 | null
  /** 0..1 visibility wanted right now */
  vis: () => number
  /** with the priority rule on: higher wins a collision; `tie` breaks equal priority (lower wins) */
  priority?: () => number
  tie?: () => number
}

/** The priority rule: labels collide in priority order and a loser collapses to its dot; `obstacles` are screen rects (the UI cards). */
export interface DeclutterOpts { obstacles: () => Rect[] }

interface Live extends LabelDef {
  el: HTMLDivElement
  subEl: HTMLElement | null
  op: number
  w: number
  x: number
  y: number
  yAdj: number
  on: boolean
  dot: boolean
  /** the priority rule only: the pill's width has been measured on screen (not the 120 px stand-in) */
  sized: boolean
  target: number
}

/**
 * Screen-space pills anchored to points in the scene. Opacity is smoothed with
 * the simulation clock (so recordings are frame exact) and overlapping pills
 * are nudged apart vertically.
 */
export class Labels {
  private items: Live[] = []
  private v = new THREE.Vector3()
  constructor(private root: HTMLElement, private camera: THREE.PerspectiveCamera, private rule: DeclutterOpts | null = null) {}

  add(d: LabelDef) {
    const el = document.createElement('div')
    el.className = 'lbl ' + (d.cls ?? '')
    const dot = document.createElement('i')
    if (d.color) dot.style.background = d.color
    const txt = document.createElement('span')
    txt.textContent = d.text
    el.append(dot, txt)
    let subEl: HTMLElement | null = null
    if (d.sub) {
      subEl = document.createElement('em')
      el.appendChild(subEl)
    }
    this.root.appendChild(el)
    this.items.push({ ...d, el, subEl, op: 0, w: 0, x: 0, y: 0, yAdj: 0, on: false, dot: false, sized: false, target: 0 })
  }

  update(w: number, h: number, dt: number) {
    const cam = this.camera
    const k = 1 - Math.exp(-dt * 9)
    const live: Live[] = []
    for (const it of this.items) {
      const want = it.vis()
      const p = want > 0.01 ? it.at() : null
      let target = 0
      if (p) {
        this.v.copy(p).project(cam)
        const x = (this.v.x * 0.5 + 0.5) * w
        const y = (-this.v.y * 0.5 + 0.5) * h
        const margin = 36
        if (this.v.z < 1 && this.v.z > -1 && x > margin && x < w - margin && y > margin && y < h - margin) {
          target = want
          it.x = x
          it.y = y
        }
      }
      it.target = target
      it.op += (target - it.op) * k
      if (it.op < 0.01 && target === 0) it.op = 0
      if (it.op > 0) {
        if (it.subEl && it.sub) {
          const s = typeof it.sub === 'function' ? it.sub() : it.sub
          if (it.subEl.textContent !== s) { it.subEl.textContent = s; it.w = 0; it.sized = false }
        }
        if (!it.w || (this.rule && !it.sized && it.on)) {
          // measure the full pill (a collapsed one is only its dot); a pill not yet on screen measures 0, so the rule measures again once it is
          if (it.dot) it.el.classList.remove('dot')
          const w = it.el.offsetWidth
          it.w = w || 120
          it.sized = w > 0
          if (it.dot) it.el.classList.add('dot')
        }
        live.push(it)
      }
    }
    for (const it of live) it.yAdj = it.y
    if (this.rule && live.length) {
      // the priority rule: winners keep their place (or take the slot just above or below), losers collapse to their dot
      const placed = declutter(live.map((it) => ({ x: it.x, y: it.y, w: it.w, h: 22, priority: it.target > 0 ? it.priority?.() ?? 0 : -1, tie: it.tie?.() ?? 0 })), this.rule.obstacles())
      live.forEach((it, i) => {
        it.yAdj = it.y + placed[i].dy
        if (placed[i].collapsed !== it.dot) { it.dot = placed[i].collapsed; it.el.classList.toggle('dot', it.dot) }
        if (placed[i].hidden !== it.el.classList.contains('gone')) it.el.classList.toggle('gone', placed[i].hidden)
      })
    }
    // relax overlaps: push pairs apart vertically
    for (let iter = 0; iter < (this.rule ? 0 : 6); iter++) {
      let moved = false
      for (let i = 0; i < live.length; i++)
        for (let j = i + 1; j < live.length; j++) {
          const a = live[i], b = live[j]
          const dx = Math.abs(a.x - b.x), dy = a.yAdj - b.yAdj
          const minX = (a.w + b.w) / 2 + 6, minY = 26
          if (dx < minX && Math.abs(dy) < minY) {
            const push = (minY - Math.abs(dy)) / 2 + 0.5
            const s = dy >= 0 ? 1 : -1
            a.yAdj += s * push
            b.yAdj -= s * push
            moved = true
          }
        }
      if (!moved) break
    }
    for (const it of this.items) {
      const vis = it.op > 0.004
      if (vis !== it.on) { it.el.style.display = vis ? 'flex' : 'none'; it.on = vis }
      if (!vis) continue
      it.el.style.opacity = it.op.toFixed(3)
      it.el.style.transform = `translate(${it.x.toFixed(1)}px, ${it.yAdj.toFixed(1)}px) translate(-50%, -50%)`
    }
  }

  /** What is on screen now, for tests and captures. */
  stats(): { id: string; text: string; opacity: number; x: number; y: number; collapsed?: boolean; hidden?: boolean }[] {
    return this.items.map((i) => (this.rule ? { id: i.id, text: i.text, opacity: i.op, x: i.x, y: i.yAdj, collapsed: i.dot, hidden: i.el.classList.contains('gone') } : { id: i.id, text: i.text, opacity: i.op, x: i.x, y: i.yAdj }))
  }
}
