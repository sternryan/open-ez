// The bench panel under the 3D view: what is on the bench for this step (materials, quantities, tools), why a buddy is needed,
// what cure follows, and the step's source detail. The plans chapter appears here, in .source, and nowhere else in the player.
import type { Op, PlanJson } from '../logic/graph'
import type { Actual } from '../logic/actuals'
import { DASH, fmtH } from './navlog'
import { evidenceOf } from '../logic/evidence'
import { PACE_QUALIFIER } from '../logic/pace'

export interface BenchExtra {
  /** graph.json `pages`: scan page -> plans page (empty in a public build) */
  pages?: Record<string, string>
  /** the cure wait after this step in the current environment, and why it is unknown when it is */
  cure?: { hours: number | null; why: string | null }
  /** the one GU note (first canard step only) */
  note?: string | null
  /** the owner's logged hours and receipt for this step, if any. Local only. */
  actual?: Actual | null
  /** multiplier on this step's estimated hours. 1 leaves the logged figure as it is. */
  pace?: number
  /** the next actual for this step, or null to clear it. The estimate on the step is left alone. */
  onActual?: (next: Actual | null) => void
}

const el = <K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text?: string): HTMLElementTagNameMap[K] => {
  const e = document.createElement(tag)
  if (cls) e.className = cls
  if (text !== undefined) e.textContent = text
  return e
}
const qty = (n: number) => (Math.round(n * 100) / 100).toString()

/** One line on a fuel-wetted step whose resin has no published compatibility result. */
function fuelLine(fuel: PlanJson['fuel']): HTMLParagraphElement | null {
  if (!fuel?.wetted || fuel.resin_compat !== 'unknown') return null
  const text = `Fuel-wetted: ${fuel.fuel} compatibility of this resin is unknown (coupon test pending)`
  const p = el('p', 'fuel flag unknown', text)
  p.dataset.flag = 'unknown'
  return p
}

/** " · flag" and, for a sourced value, its evidence: the citation, the derivation note or a link. No evidence: " · estimate". */
function flagged(host: HTMLElement, flag: string, source: string | null | undefined): void {
  const ev = evidenceOf(flag, source)
  const f = el('span', 'flag', ` · ${ev.flag}`)
  f.dataset.flag = ev.flag
  if (ev.flag !== flag) f.title = `flagged ${flag}, but no evidence is on record`
  host.append(f)
  if (!ev.kind || !ev.text) return
  host.append(document.createTextNode(' · '))
  if (ev.kind === 'link') {
    const a = el('a', 'ev', 'source')
    a.href = ev.text
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    host.append(a)
  } else host.append(el(ev.kind === 'cite' ? 'cite' : 'span', `ev ${ev.kind}`, ev.text))
}

/** Where the step's words come from: chapter and plans page per registered source. */
export function sourceText(op: Op, pages: Record<string, string> = {}): string {
  const cites = (op.sources ?? []).map((s) => {
    const page = s.page ?? (s.scan_pp !== null && s.scan_pp !== undefined ? pages[String(s.scan_pp)] : undefined)
    if (page) return `${s.doc} p. ${page}`
    if (s.scan_pp !== null && s.scan_pp !== undefined) return `${s.doc} scan p. ${s.scan_pp}`
    return s.doc
  })
  return [`Chapter ${op.chapter}`, ...[...new Set(cites)]].join(' · ')
}

export function renderBench(root: HTMLElement, op: Op, catalog: Record<string, { label: string; unit: string; flag?: string }>, extra: BenchExtra = {}): void {
  root.replaceChildren()
  const plan = op.plan ?? null
  root.append(el('h3', 'bench-title', op.title))
  const grid = el('dl', 'bench-grid')
  const row = (k: string, label: string, body: HTMLElement | string) => {
    const d = el('div', 'bench-row')
    const v = el('dd')
    v.dataset.k = k
    if (typeof body === 'string') v.textContent = body; else v.append(body)
    d.append(el('dt', 'label', label), v)
    grid.append(d)
  }
  const h = plan?.hours ?? null
  const pace = extra.pace ?? 1
  const scale = pace !== 1 && Number.isFinite(pace) && h?.value != null && Number.isFinite(h.value)
  if (h && h.value !== null) {
    const shown = scale ? h.value * pace : h.value
    const hv = el('span', '', `${fmtH(shown)} h`)
    flagged(hv, h.flag, h.source)
    if (scale && Number.isFinite(shown)) {
      const q = el('span', 'flag', ` · ${PACE_QUALIFIER}`)
      q.dataset.flag = PACE_QUALIFIER
      hv.append(q)
    }
    row('hours', 'Hours', hv)
  } else row('hours', 'Hours', `${DASH} no hours figure yet (planned as 1 h)`)
  const mats = el('ul', 'bench-list')
  for (const m of op.materials ?? []) mats.append(el('li', '', `${m.cloth} × ${m.plies} ${m.plies === 1 ? 'ply' : 'plies'} · ${m.where}`))
  for (const b of plan?.buy ?? []) {
    const c = catalog[b.item]
    const li = el('li', 'buy', `${c?.label ?? b.item}: ${qty(b.qty)} ${c?.unit ?? ''} net`.replace(/ {2,}/g, ' '))
    li.dataset.item = b.item
    flagged(li, b.flag, b.source)
    mats.append(li)
  }
  row('materials', 'On the bench', mats.childElementCount ? mats : 'Nothing listed for this step')
  row('tools', 'Tools', plan?.tools?.length ? plan.tools.join(', ') : 'None listed')
  row('buddy', 'People', plan?.people === 2 ? `Buddy needed: ${plan.people_why ?? DASH}` : 'One person')
  let cure = 'No cure wait'
  if (plan?.cure && plan.cure !== 'none') {
    const scope = plan.cure === 'all' ? 'The whole shop waits for the cure' : 'Nothing more on this part until it sets'
    const c = extra.cure
    const wait = !c ? '' : c.hours !== null ? `: about ${fmtH(c.hours)} h before it can be worked again` : `: wait unknown${c.why ? ` (${c.why})` : ''}`
    cure = scope + wait
  }
  row('cure', 'Cure after', cure)
  root.append(grid)
  const fuelNote = fuelLine(plan?.fuel)
  if (fuelNote) root.append(fuelNote)
  root.append(actualFields(extra))
  if (extra.note) root.append(el('p', 'note gu', extra.note))
  root.append(el('p', 'source', sourceText(op, extra.pages)))
}

const numOrEmpty = (raw: string): number | null | undefined => {
  const t = raw.trim()
  if (t === '') return null
  const n = Number(t)
  if (!Number.isFinite(n) || n < 0) return undefined
  return n
}

/** Logged hours and a receipt for this step. Empty clears that field. Zero is a real value. A negative is rejected. */
function actualFields(extra: BenchExtra): HTMLElement {
  const box = el('div', 'actual')
  const prev = extra.actual ?? {}
  const emit = (patch: { hours?: number | null; spentUsd?: number | null }): void => {
    if (!extra.onActual) return
    const next: Actual = { ...prev }
    if (patch.hours === null) delete next.hours
    else if (typeof patch.hours === 'number') next.hours = patch.hours
    if (patch.spentUsd === null) delete next.spentUsd
    else if (typeof patch.spentUsd === 'number') next.spentUsd = patch.spentUsd
    extra.onActual(next.hours === undefined && next.spentUsd === undefined ? null : next)
  }
  const field = (k: string, label: string, value: number | undefined, aria: string, on: (n: number | null) => void): HTMLLabelElement => {
    const lab = el('label', 'actual-field')
    const input = el('input')
    input.type = 'number'
    input.min = '0'
    input.step = 'any'
    input.inputMode = 'decimal'
    input.dataset.k = k
    input.setAttribute('aria-label', aria)
    if (value !== undefined) input.value = String(value)
    input.addEventListener('change', () => {
      const n = numOrEmpty(input.value)
      if (n === undefined) {
        input.value = value !== undefined ? String(value) : ''
        return
      }
      on(n)
    })
    lab.append(el('span', 'label', label), input)
    return lab
  }
  box.append(field('actual-hours', 'Logged hours', prev.hours, 'Logged hours for this step', (n) => emit({ hours: n })))
  box.append(field('actual-spent', 'Receipt, USD', prev.spentUsd, 'Receipt for this step, dollars', (n) => emit({ spentUsd: n })))
  const clear = el('button', 'btn', 'Clear actual')
  clear.type = 'button'
  clear.dataset.k = 'actual-clear'
  clear.addEventListener('click', () => extra.onActual?.(null))
  box.append(clear)
  return box
}
