import type { Op, Variant } from '../logic/graph'
import type { Subject } from '../logic/fuselage'
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
  /** the canard or the fuselage box (optional: a page without the control never calls it) */
  onSubject?(s: Subject): void
}
/** How the section slider reads: the canard's B.L. (the default) or the fuselage's FS. */
export interface SectionScale { min: number; max: number; fmt: (v: number) => string; label: string }

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T

/** DOM side of the lab: control card, step card and the bottom op bar. No three.js in here. */
export function initUI(h: UIHandlers, store: Store) {
  const chips = $('chips'), title = $('step-title'), summary = $('step-summary'), list = $('checklist')
  const step = $('step'), head = $('step-head'), variant = $('variant')
  let ops: Op[] = []
  let selected: string | null = null
  const phone = matchMedia('(max-width: 640px)')
  // up to iPad width the step card starts as its title line (the rest behind the disclosure) so the canard keeps the frame
  const narrow = matchMedia('(max-width: 1180px)')

  let listOpen = false
  const setOpen = (open: boolean) => { step.dataset.open = String(open); head.setAttribute('aria-expanded', String(open)); fit() }
  narrow.addEventListener('change', () => setOpen(!narrow.matches))
  head.addEventListener('click', () => setOpen(step.dataset.open !== 'true'))

  // When the open card would cover too much of the frame the checklist folds behind its heading. The budget is the smaller of 40% of
  // the viewport height and about 8.5% of the viewport area over the dock's width. Phones show the whole body once it is opened.
  const fit = () => {
    step.dataset.compact = 'false'
    step.dataset.list = 'open'
    if (phone.matches || step.dataset.open !== 'true') return
    const dock = $('dock')
    const body = $('step-body')
    // the body is height-capped, so measure what it wants (its full scroll height), not what it got
    const natural = dock.offsetHeight - body.offsetHeight + body.scrollHeight
    const budget = Math.min(window.innerHeight * 0.4, (0.085 * window.innerWidth * window.innerHeight) / Math.max(1, dock.offsetWidth))
    const compact = natural > budget && list.children.length > 0
    step.dataset.compact = String(compact)
    step.dataset.list = compact && !listOpen ? 'closed' : 'open'
    $('checklist-h').setAttribute('aria-expanded', String(!compact || listOpen))
  }
  $('checklist-h').addEventListener('click', () => {
    if (step.dataset.compact !== 'true') return
    listOpen = !listOpen
    fit()
  })

  // the display popover hangs under the control card, right-aligned with it
  const more = $('more'), pop = $('viewpop'), controls = $('controls')
  const placePop = () => {
    const r = controls.getBoundingClientRect()
    pop.style.top = `${Math.round(r.bottom + 8)}px`
    pop.style.right = `${Math.round(window.innerWidth - r.right)}px`
  }
  const setPop = (open: boolean) => {
    pop.hidden = !open
    more.setAttribute('aria-expanded', String(open))
    if (open) placePop()
  }
  more.addEventListener('click', () => setPop(pop.hidden))
  document.addEventListener('pointerdown', (e) => {
    const t = e.target as Node
    if (!pop.hidden && !pop.contains(t) && !more.contains(t)) setPop(false)
  })
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !pop.hidden) { setPop(false); more.focus() } })
  // the card changes height as rows appear (scrubber, section): keep the popover under it
  new ResizeObserver(() => { if (!pop.hidden) placePop() }).observe(controls)
  window.addEventListener('resize', () => { fit(); if (!pop.hidden) placePop() })
  setOpen(!narrow.matches)

  // The fuselage's CG and legend rows fold into one line behind a disclosure (closed by default, so the dock leaves the box clear); the
  // choice is remembered like the other view settings, and a storage that throws only means it is not remembered.
  const DETAILS_KEY = 'longez.fuseDetails'
  const setDetails = (open: boolean, save: boolean) => {
    $('fuse-rows').dataset.open = String(open)
    $('fuse-more').setAttribute('aria-expanded', String(open))
    if (save) try { window.localStorage.setItem(DETAILS_KEY, open ? '1' : '0') } catch { /* per-viewer convenience only */ }
    fit()
  }
  let detailsOpen = false
  try { detailsOpen = window.localStorage.getItem(DETAILS_KEY) === '1' } catch { detailsOpen = false }
  setDetails(detailsOpen, false)
  $('fuse-more').addEventListener('click', () => setDetails($('fuse-rows').dataset.open !== 'true', true))

  $('subject')?.addEventListener('click', (e) => {
    const b = (e.target as HTMLElement).closest('button[data-subject]') as HTMLElement | null
    if (b) h.onSubject?.(b.dataset.subject as Subject)
  })
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
  let secFmt: (v: number) => string = fmtBl
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
      $('section-station').textContent = secFmt(bl)
    },
    /** re-scale the section slider for a subject: the canard's (min 0, B.L.) is what the page starts with */
    scaleSection(sc: SectionScale, on: boolean, v: number) {
      secFmt = sc.fmt
      secBl.min = String(sc.min)
      secBl.max = String(sc.max)
      secBl.setAttribute('aria-label', sc.label)
      secOn.checked = on
      secBl.value = String(v)
      $('section').hidden = false
      $('section-station').textContent = secFmt(v)
    },
    setSection(on: boolean, bl: number) {
      secOn.checked = on
      secBl.value = String(bl)
      $('section-station').textContent = secFmt(bl)
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
    setSubject(s: Subject) {
      for (const b of document.querySelectorAll('#subject button[data-subject]')) b.setAttribute('aria-pressed', String((b as HTMLElement).dataset.subject === s))
      variant.hidden = s !== 'canard' // the variant only changes the canard
      document.body.dataset.subject = s
    },
    /** the fuselage rows of the readout: the CG from the mass ledger (null hides the row) and the stripes legend */
    setCg(cg: { value: string; sub: string | null } | null) {
      $('fuse-rows').hidden = cg === null
      $('t-cg').hidden = cg === null
      $('t-legend').hidden = cg === null
      if (!cg) return
      $('ro-cg').textContent = cg.value
      $('ro-cg-sub').textContent = cg.sub ?? ''
      $('t-cg').title = cg.sub ? `${cg.value}. ${cg.sub}` : cg.value
    },
    /** the motion readout (the elevator's travel and hang, the nose gear's crank): a label, the live value and a note; null hides it */
    setKin(k: { label: string; value: string; sub: string } | null) {
      const t = $('t-kin')
      if (!k) { t.hidden = true; return }
      t.hidden = false
      if ($('ro-kin-label').textContent !== k.label) $('ro-kin-label').textContent = k.label
      if ($('ro-kin').textContent !== k.value) $('ro-kin').textContent = k.value
      if ($('ro-kin-sub').textContent !== k.sub) $('ro-kin-sub').textContent = k.sub
      t.title = `${k.value}. ${k.sub}`
    },
    /** the ground-handling note (book axle station and tip-back line; the checks "not yet computed"); it shows with the CG's detail */
    setGround(g: { value: string; sub: string } | null) {
      $('t-ground').hidden = g === null
      if (!g) return
      $('ro-ground').textContent = g.value
      $('ro-ground-sub').textContent = g.sub
      $('t-ground').title = `${g.value}. ${g.sub}`
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
