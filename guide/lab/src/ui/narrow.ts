// The player on a narrow or portrait screen (width <= 820 CSS px, or taller than wide): the 3D view gets the screen. The step list
// and the bench move into the stage, which becomes a bottom sheet (collapsed: the session and step, the caption and one transport
// row); the shop settings and the view card move behind a gear; the meter shows three numbers and opens to all five on a tap.
// One switch (body[data-narrow]) drives the CSS, so the stylesheet and this module never disagree about which layout is on.
// Elements are moved, not copied: their ids, listeners and the code that renders into them stay the same in both layouts.

export const NARROW_QUERY = '(max-width: 820px), (orientation: portrait)'

export interface Narrow {
  /** the narrow layout is on */
  on(): boolean
  /** the bottom sheet is open (always false on the wide layout) */
  open(): boolean
}

const byId = (id: string) => document.getElementById(id) as HTMLElement

/** A node that can sit in one of two places; a comment marks its wide-layout spot so it goes back exactly where it was. */
function mover(node: HTMLElement) {
  const mark = document.createComment(`wide:${node.id || node.className}`)
  return {
    narrow(into: HTMLElement, before: Node | null = null) {
      if (!mark.parentNode) node.replaceWith(mark)
      into.insertBefore(node, before)
    },
    wide() {
      if (mark.parentNode) mark.replaceWith(node)
    },
  }
}

export function setupNarrow(onLayout: () => void): Narrow {
  const mq = window.matchMedia(NARROW_QUERY)
  const body = document.body
  const stage = byId('stage'), handle = byId('sheet-handle'), sheetBody = byId('sheet-body'), bench = byId('bench')
  const meter = byId('meter'), gear = byId('env-toggle'), envsheet = byId('envsheet'), pop = byId('viewpop')
  const shop = byId('envsheet-shop'), view = byId('envsheet-view')
  const sessionRow = byId('session-hours').closest('.env-row') as HTMLElement
  const list = mover(byId('navlog-list'))
  const shopParts = [byId('environment'), sessionRow, byId('env-warn'), byId('env-note')].map(mover)
  const controls = mover(byId('controls'))
  let on = false, inited = false

  const setSheet = (open: boolean) => {
    stage.dataset.open = String(open)
    handle.setAttribute('aria-expanded', String(open))
    if (open) sheetBody.querySelector<HTMLElement>('.step.current')?.scrollIntoView({ block: 'nearest' })
  }
  const setEnv = (open: boolean) => {
    envsheet.hidden = !open
    gear.setAttribute('aria-expanded', String(open))
    if (open) setMeter(false)
  }
  const setMeter = (open: boolean) => {
    meter.dataset.open = String(open)
    if (on) meter.setAttribute('aria-expanded', String(open))
    if (open) setEnv(false)
  }

  const apply = () => {
    const want = mq.matches
    if (inited && want === on) return
    inited = true
    on = want
    setSheet(false); setEnv(false); setMeter(false)
    if (on) {
      body.dataset.narrow = '1'
      list.narrow(sheetBody, bench)
      for (const p of shopParts) p.narrow(shop)
      controls.narrow(view)
      meter.setAttribute('role', 'button')
      meter.tabIndex = 0
      meter.setAttribute('aria-expanded', 'false')
      meter.setAttribute('aria-label', 'Plan so far: tap for the full meter')
    } else {
      delete body.dataset.narrow
      list.wide()
      for (const p of shopParts) p.wide()
      controls.wide()
      for (const a of ['role', 'tabindex', 'aria-expanded']) meter.removeAttribute(a)
      meter.setAttribute('aria-label', 'Plan so far')
    }
    onLayout()
  }

  // the sheet: a tap toggles it; a drag of more than 24 px opens it (up) or closes it (down)
  let y0: number | null = null, dragged = false
  handle.addEventListener('pointerdown', (e) => { y0 = e.clientY; dragged = false; try { handle.setPointerCapture(e.pointerId) } catch { /* a synthetic pointer */ } })
  handle.addEventListener('pointermove', (e) => {
    if (y0 === null || dragged) return
    const dy = e.clientY - y0
    if (Math.abs(dy) > 24) { dragged = true; setSheet(dy < 0) }
  })
  const end = () => { y0 = null }
  handle.addEventListener('pointerup', end)
  handle.addEventListener('pointercancel', end)
  handle.addEventListener('click', () => {
    if (dragged) { dragged = false; return }
    setSheet(stage.dataset.open !== 'true')
  })

  gear.addEventListener('click', () => setEnv(envsheet.hidden))
  document.addEventListener('pointerdown', (e) => {
    const t = e.target as Node
    if (!envsheet.hidden && !envsheet.contains(t) && !gear.contains(t) && !pop.contains(t)) setEnv(false)
  })
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || !on) return
    if (!pop.hidden) return // the display popover closes first (src/ui/ui.ts)
    if (!envsheet.hidden) { setEnv(false); gear.focus() } else if (meter.dataset.open === 'true') setMeter(false)
  })

  const toggleMeter = () => { if (on) setMeter(meter.dataset.open !== 'true') }
  meter.addEventListener('click', toggleMeter)
  meter.addEventListener('keydown', (e) => { if (on && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); toggleMeter() } })

  mq.addEventListener('change', apply)
  window.addEventListener('resize', apply)
  meter.dataset.open = 'false'
  stage.dataset.open = 'false'
  apply()
  return { on: () => on, open: () => on && stage.dataset.open === 'true' }
}
