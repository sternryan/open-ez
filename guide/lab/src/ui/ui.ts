import type { Op, Variant } from '../logic/graph'
import { fmtBl } from '../logic/section'

type Store = { get(id: string): Set<number>; toggle(id: string, i: number): void }
export interface UIHandlers {
  onVariant(v: Variant): void
  onHome(): void
  onTour(): void
  onSelect(opId: string): void
  onGhost(on: boolean): void
  onScrub(n: number): void
  onPlay(): void
  onSection(on: boolean, bl: number): void
  onLabels(on: boolean): void
  onPaths(on: boolean): void
  onQuality(q: 'high' | 'mid' | 'low' | 'auto'): void
}

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T

/** DOM side of the lab: control card, step card and the bottom op bar. No three.js in here. */
export function initUI(h: UIHandlers, store: Store) {
  const chips = $('chips'), title = $('step-title'), summary = $('step-summary'), list = $('checklist')
  const step = $('step'), head = $('step-head'), variant = $('variant')
  let ops: Op[] = []
  let selected: string | null = null
  const phone = matchMedia('(max-width: 640px)')

  const setOpen = (open: boolean) => { step.dataset.open = String(open); head.setAttribute('aria-expanded', String(open)) }
  // Phones start collapsed to the title line; wide screens always show the body (the toggle is inert there).
  setOpen(!phone.matches)
  phone.addEventListener('change', () => setOpen(!phone.matches))
  head.addEventListener('click', () => { if (phone.matches) setOpen(step.dataset.open !== 'true') })

  // Desktop: when the whole card (summary and checklist) would cover more than ~40% of the canvas height, the checklist folds
  // behind its heading so the card stays a strip and the canard keeps the room. Phones already collapse the whole body.
  const COVER = 0.4
  let listOpen = true
  const fit = () => {
    if (phone.matches) { step.dataset.compact = 'false'; return }
    step.dataset.compact = 'false'
    step.dataset.list = 'open'
    // the card is height-capped, so measure what it wants (heading plus the body's full scroll height), not what it got
    const natural = head.offsetHeight + $('step-body').scrollHeight
    const compact = natural > window.innerHeight * COVER && list.children.length > 0
    step.dataset.compact = String(compact)
    step.dataset.list = compact && !listOpen ? 'closed' : 'open'
    $('checklist-h').setAttribute('aria-expanded', String(!compact || listOpen))
  }
  $('checklist-h').addEventListener('click', () => {
    if (step.dataset.compact !== 'true') return
    listOpen = !listOpen
    fit()
  })
  window.addEventListener('resize', fit)

  variant.addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest('button[data-variant]') as HTMLElement | null
    if (b) h.onVariant(b.dataset.variant as Variant)
  })
  $('home').addEventListener('click', () => h.onHome())
  $('tour').addEventListener('click', () => h.onTour())
  $('bar-home').addEventListener('click', () => h.onHome())
  $('ghost').addEventListener('change', (e) => h.onGhost((e.target as HTMLInputElement).checked))
  $('scrub').addEventListener('input', (e) => h.onScrub(+(e.target as HTMLInputElement).value)) // user input only: setting .value fires no event
  $('play').addEventListener('click', () => h.onPlay())
  const secOn = $('section-on') as HTMLInputElement, secBl = $('section-bl') as HTMLInputElement
  const secChange = () => h.onSection(secOn.checked, +secBl.value)
  secOn.addEventListener('change', secChange)
  secBl.addEventListener('input', secChange)
  $('quality-seg').addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest('button[data-q]') as HTMLElement | null
    if (b) h.onQuality(b.dataset.q as 'high' | 'mid' | 'low' | 'auto')
  })
  $('labels-on').addEventListener('change', (e) => h.onLabels((e.target as HTMLInputElement).checked))
  $('paths-on').addEventListener('change', (e) => h.onPaths((e.target as HTMLInputElement).checked))
  chips.addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest('button[data-op]') as HTMLElement | null
    if (b) h.onSelect(b.dataset.op!)
  })

  const renderCount = (op: Op | null) => {
    const total = op?.completion?.length ?? 0
    const done = op ? [...store.get(op.id)].filter((i) => i < total).length : 0
    $('check-count').textContent = total ? `${done}/${total}` : ''
  }

  const showStep = (op: Op | null) => {
    list.replaceChildren()
    if (!op) {
      title.textContent = ops.length ? 'Pick a step' : 'No steps for this variant'
      summary.textContent = ops.length ? '' : 'The build steps for this canard are not written yet.'
      $('step-count').textContent = ''
      $('checklist-h').hidden = true
      renderCount(null)
      return
    }
    const idx = ops.findIndex((o) => o.id === op.id)
    $('step-count').textContent = `${idx + 1} / ${ops.length}`
    title.textContent = op.title
    summary.textContent = op.summary
    const done = store.get(op.id)
    ;(op.completion ?? []).forEach((text, i) => {
      const li = document.createElement('li')
      const label = document.createElement('label')
      const cb = document.createElement('input')
      cb.type = 'checkbox'
      cb.checked = done.has(i)
      cb.addEventListener('change', () => { store.toggle(op.id, i); renderCount(op) })
      label.append(cb, document.createTextNode(text))
      li.append(label)
      list.append(li)
    })
    $('checklist-h').hidden = list.children.length === 0
    renderCount(op)
    listOpen = false
    fit()
  }

  return {
    setGhost(on: boolean) { ($('ghost') as HTMLInputElement).checked = on },
    /** the scrubber and Play are shown only for an op with plies */
    setBuild(lay: number, count: number) {
      $('scrubwrap').hidden = count === 0
      const s = $('scrub') as HTMLInputElement
      s.max = String(count)
      s.value = String(lay)
      $('scrublabel').textContent = `Ply ${lay} of ${count}`
    },
    /** show the section controls only when the site has a layup; `max` is the layup's semi-span */
    initSection(max: number, bl: number) {
      secBl.max = String(max)
      secBl.value = String(bl)
      $('section').hidden = false
      $('section-station').textContent = fmtBl(bl)
    },
    setSection(on: boolean, bl: number) {
      secOn.checked = on
      secBl.value = String(bl)
      $('section-station').textContent = fmtBl(bl)
    },
    setTouring(on: boolean) {
      $('tour').setAttribute('aria-pressed', String(on))
      $('tour').textContent = on ? 'Stop tour' : 'Tour'
    },
    setPaths(on: boolean) { ($('paths-on') as HTMLInputElement).checked = on },
    setLabels(on: boolean) { ($('labels-on') as HTMLInputElement).checked = on },
    /** the stat tiles: plain text only; `plies` is null when the op has none */
    setReadout(r: { station: string; layers: string; plies: string | null; cloth: string }) {
      $('ro-station').textContent = r.station
      const l = $('ro-layers')
      l.textContent = r.layers
      l.title = r.layers // phone: one ellipsised line, the full text stays in the title
      $('t-plies').hidden = r.plies === null
      $('ro-plies').textContent = r.plies ?? ''
      $('ro-cloth').textContent = r.cloth
    },
    setPlaying(on: boolean) {
      $('play').setAttribute('aria-pressed', String(on))
      $('play').textContent = on ? 'Stop' : 'Play'
    },
    /** the tier in use and whether it is being picked automatically */
    setQuality(tier: 'high' | 'mid' | 'low', auto: boolean) {
      const name = { high: 'High', mid: 'Med', low: 'Low' }[tier]
      $('quality-label').textContent = `Quality: ${name}${auto ? ' (auto)' : ''}`
      for (const b of $('quality-seg').querySelectorAll('button[data-q]')) {
        const q = (b as HTMLElement).dataset.q
        b.setAttribute('aria-pressed', String(q === 'auto' ? auto : !auto && q === tier))
      }
    },
    setVariant(v: Variant) {
      for (const b of variant.querySelectorAll('button[data-variant]')) b.setAttribute('aria-pressed', String((b as HTMLElement).dataset.variant === v))
    },
    setOps(next: Op[]) {
      ops = next
      chips.replaceChildren()
      if (!next.length) {
        const n = document.createElement('span')
        n.className = 'none'
        n.textContent = 'No steps for this variant yet'
        chips.append(n)
        return
      }
      for (const op of next) {
        const b = document.createElement('button')
        b.type = 'button'
        b.dataset.op = op.id
        b.title = op.title
        b.textContent = op.title.length > 34 ? op.title.slice(0, 32).trimEnd() + '…' : op.title
        chips.append(b)
      }
    },
    setSelected(id: string | null) {
      selected = id
      for (const b of chips.querySelectorAll('button[data-op]')) {
        const on = (b as HTMLElement).dataset.op === id
        if (on) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current')
        if (on) (b as HTMLElement).scrollIntoView?.({ block: 'nearest', inline: 'center' })
      }
      showStep(ops.find((o) => o.id === id) ?? null)
    },
    get selected() { return selected },
  }
}
