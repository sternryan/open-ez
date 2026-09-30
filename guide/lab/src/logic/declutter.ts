/**
 * Screen-space label de-cluttering (the fuselage subject's labels). Pure: no DOM, no three.js.
 *
 * Labels are placed in priority order (higher first; equal priority by `tie`, lower first, then input order). Each tries its own
 * anchor, then one slot above and one below it; the first slot that overlaps no label already placed and no obstacle (the UI cards)
 * wins. A label with no free slot collapses to its leader dot; a dot that would sit on a readable label or an obstacle is hidden. A dot is
 * never an obstacle for the labels after it, so a collapsed label never pushes a readable one away.
 */
export interface DeclutterItem {
  /** anchor, CSS pixels (the pill is centred on it) */
  x: number
  y: number
  /** pill size, CSS pixels */
  w: number
  h: number
  priority: number
  tie: number
}
export interface Rect { l: number; t: number; r: number; b: number }
/** collapsed: shown as its dot only; hidden: not even the dot (it would sit on a readable label) */
export interface Placed { dy: number; collapsed: boolean; hidden: boolean }

export const DECLUTTER = { nudge: 24, pad: 3, dot: 13 }

const hit = (a: Rect, b: Rect) => a.l < b.r && b.l < a.r && a.t < b.b && b.t < a.b

export function declutter(items: DeclutterItem[], obstacles: Rect[] = []): Placed[] {
  const order = items.map((_, i) => i).sort((i, j) => items[j].priority - items[i].priority || items[i].tie - items[j].tie || i - j)
  const out: Placed[] = items.map(() => ({ dy: 0, collapsed: true, hidden: false }))
  const taken: Rect[] = []
  const { nudge, pad, dot } = DECLUTTER
  for (const i of order) {
    const it = items[i]
    for (const dy of [0, -nudge, nudge]) {
      const r = { l: it.x - it.w / 2 - pad, r: it.x + it.w / 2 + pad, t: it.y + dy - it.h / 2 - pad, b: it.y + dy + it.h / 2 + pad }
      if (taken.some((q) => hit(q, r)) || obstacles.some((q) => hit(q, r))) continue
      taken.push(r)
      out[i] = { dy, collapsed: false, hidden: false }
      break
    }
  }
  // a dot on top of a readable pill reads as clutter, and one under a card or off the edge peeks out of it: hide it
  items.forEach((it, i) => {
    if (!out[i].collapsed) return
    const d = { l: it.x - dot / 2, r: it.x + dot / 2, t: it.y - dot / 2, b: it.y + dot / 2 }
    out[i].hidden = taken.some((q) => hit(q, d)) || obstacles.some((q) => hit(q, d))
  })
  return out
}
