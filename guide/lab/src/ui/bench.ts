// The bench panel under the 3D view: what is on the bench for this step (materials, quantities, tools), why a buddy is needed,
// what cure follows, and the step's source detail. The plans chapter appears here, in .source, and nowhere else in the player.
import type { Op } from '../logic/graph'
import { DASH, fmtH } from './navlog'
import { evidenceOf } from '../logic/evidence'

export interface BenchExtra {
  /** graph.json `pages`: scan page -> plans page (empty in a public build) */
  pages?: Record<string, string>
  /** the cure wait after this step in the current environment, and why it is unknown when it is */
  cure?: { hours: number | null; why: string | null }
  /** the one GU note (first canard step only) */
  note?: string | null
}

const el = <K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text?: string): HTMLElementTagNameMap[K] => {
  const e = document.createElement(tag)
  if (cls) e.className = cls
  if (text !== undefined) e.textContent = text
  return e
}
const qty = (n: number) => (Math.round(n * 100) / 100).toString()

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
  if (h && h.value !== null) {
    const hv = el('span', '', `${fmtH(h.value)} h`)
    flagged(hv, h.flag, h.source)
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
  if (extra.note) root.append(el('p', 'note gu', extra.note))
  root.append(el('p', 'source', sourceText(op, extra.pages)))
}
