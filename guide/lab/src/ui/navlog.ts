// The nav log (the session cards of the current build group, with cure and buy markers between them) and the top meter.
// Direct DOM rendering from the planning logic; no three.js. Unknown values render as "—", never as a guessed number.
import type { SeqGroup } from '../logic/sequence'
import type { Session } from '../logic/sessions'
import type { Kit, Meter } from '../logic/kits'
import { SCRAP } from '../logic/kits'

export const DASH = '—'

/** hours to one decimal, without a trailing .0 */
export const fmtH = (h: number): string => (Math.round(h * 10) / 10).toString()
export const money = (usd: number): string => '$' + Math.round(usd).toLocaleString('en-US')
const plural = (n: number, one: string, many = one + 's') => `${n} ${n === 1 ? one : many}`

const el = <K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text?: string): HTMLElementTagNameMap[K] => {
  const e = document.createElement(tag)
  if (cls) e.className = cls
  if (text !== undefined) e.textContent = text
  return e
}

/** A kit's price as it may honestly be said: the whole sum, a partial sum with its unpriced count, or a dash. */
export function kitText(kit: Kit): string {
  const total = kit.subtotal + kit.scrap
  const stale = kit.lines.some((l) => l.stale && l.unitPrice !== null) ? ' · some prices stale' : ''
  if (kit.lines.length && kit.unpriced === kit.lines.length) return `$${DASH} · ${plural(kit.unpriced, 'item')} unpriced`
  const scrap = ` incl. ${Math.round(SCRAP * 100)}% scrap`
  if (kit.unpriced) return `${money(total)} so far${scrap} · ${plural(kit.unpriced, 'item')} unpriced${stale}`
  return `${money(total)}${scrap}${stale}`
}

function cureText(c: NonNullable<Session['cureAfter']>): string {
  const what = c.scope === 'all' ? 'the whole shop waits' : 'nothing more on this part until it sets'
  return `Cure: ${what} · ${c.hours === null ? 'wait unknown' : `about ${fmtH(c.hours)} h`}`
}

/**
 * Render the nav log into `root`. In group zoom every group shows as a labelled line; the current step's group opens into its
 * session cards. Clicking another group's label goes to its first step. `zoom: 'build'` is phase 2 and renders like 'group' now.
 */
export function renderNavlog(root: HTMLElement, seq: SeqGroup[], sessions: Session[], kits: Kit[], currentStep: string,
  onStep: (id: string) => void, zoom: 'group' | 'build'): void {
  void zoom
  root.replaceChildren()
  const order = seq.flatMap((g) => g.steps.map((o) => o.id))
  const curIdx = order.indexOf(currentStep)
  const curSession = sessions.findIndex((s) => s.steps.includes(currentStep))
  const curGroup = seq.find((g) => g.steps.some((o) => o.id === currentStep))?.id ?? seq[0]?.id
  for (const g of seq) {
    const mine = sessions.filter((s) => s.group === g.id)
    const sec = el('section', 'group' + (g.id === curGroup ? ' current' : ' collapsed'))
    sec.dataset.group = g.id
    const head = el('button', 'group-label')
    head.type = 'button'
    head.append(el('span', 'name', g.label))
    const known = mine.every((s) => s.hoursKnown)
    const hours = mine.reduce((a, s) => a + s.hours, 0)
    const sub = [plural(mine.length, 'session'), known ? `~${fmtH(hours)} h` : `${DASH} h`]
    if (mine.some((s) => s.buddy)) sub.push('buddy')
    head.append(el('span', 'sub', sub.join(' · ')))
    head.setAttribute('aria-expanded', String(g.id === curGroup))
    const first = g.steps[0]?.id
    head.addEventListener('click', () => { if (g.id !== curGroup && first) onStep(first) })
    sec.append(head)
    if (g.id === curGroup) {
      const kit = kits.find((k) => k.group === g.id)
      if (kit && kit.lines.length) sec.append(el('div', 'marker buy', `Buy the ${g.label.toLowerCase()} kit · ${kitText(kit)}`))
      const byId = new Map(g.steps.map((o) => [o.id, o]))
      for (const s of mine) {
        const card = el('div', 'session' + (s.index === curSession ? ' current' : s.index < curSession ? ' done' : ''))
        card.dataset.session = String(s.index)
        const bits = [`Session ${s.index + 1}`, s.hoursKnown ? `~${fmtH(s.hours)} h` : `${DASH} h`]
        const sh = el('div', 'session-head', bits.join(' · '))
        if (!s.hoursKnown) sh.title = 'A step in this session has no hours figure (packed as 1 h)'
        if (s.buddy) sh.append(el('span', 'chip buddy', 'buddy'))
        card.append(sh)
        const list = el('ol', 'steps')
        for (const id of s.steps) {
          const op = byId.get(id)
          if (!op) continue
          const i = order.indexOf(id)
          const li = el('li')
          const b = el('button', 'step' + (id === currentStep ? ' current' : i < curIdx ? ' done' : ''))
          b.type = 'button'
          b.dataset.op = id
          b.append(el('span', 'tick', i < curIdx ? '✓' : ''), el('span', 'title', op.title))
          const chips = el('span', 'chips')
          if (op.plan?.people === 2) chips.append(el('span', 'chip buddy', 'buddy'))
          if ((op.plan?.hours?.value ?? null) === null) chips.append(el('span', 'chip unknown', 'no hours'))
          if (chips.childElementCount) b.append(chips)
          if (id === currentStep) b.setAttribute('aria-current', 'step')
          b.addEventListener('click', () => onStep(id))
          li.append(b)
          // (the GU note is the bench's alone: src/ui/bench.ts, one rendered occurrence)
          list.append(li)
        }
        card.append(list)
        sec.append(card)
        if (s.cureAfter) sec.append(el('div', 'marker cure' + (s.cureAfter.hours === null ? ' warn' : ''), cureText(s.cureAfter)))
      }
    }
    root.append(sec)
  }
  root.querySelector<HTMLElement>('.step.current')?.scrollIntoView({ block: 'nearest' })
}

const SHORT_LABEL: Record<string, string> = { sessions: 'Sessions left' }

/** The top meter. `zoom: 'build'` (phase 2) adds the whole-build totals; it renders like 'group' now. */
export function renderMeter(root: HTMLElement, m: Meter, zoom: 'group' | 'build'): void {
  void zoom
  root.replaceChildren()
  // q: the short qualifier the collapsed phone strip keeps beside the number (src/style.css), where the full subtitle has no room
  const tile = (k: string, label: string, value: string, sub = '', q = '') => {
    const t = el('div', 'tile')
    const v = el('b', 'mono', value)
    v.dataset.k = k
    t.dataset.tile = k
    const l = el('span', 'label')
    // the narrow layout's strip has room for a shorter label (src/style.css shows one of the two)
    const short = SHORT_LABEL[k]
    if (short) l.append(el('span', 'l-long', label), el('span', 'l-short', short))
    else l.textContent = label
    t.append(l, v)
    if (q) t.append(el('span', 'q', `· ${q}`))
    if (sub) t.append(el('span', 'sub', sub))
    root.append(t)
  }
  tile('spent', 'Spent so far', m.spent === null ? DASH : money(m.spent), m.spent === null ? 'no kit bought yet' : m.spentUnpriced ? `partial · ${plural(m.spentUnpriced, 'item')} unpriced` : 'estimate', m.spent === null ? '' : m.spentUnpriced ? 'partial' : 'estimate')
  const nb = m.nextBuy
  if (!nb) tile('next-buy', 'Next buy', DASH)
  else if (nb.amount === 0 && nb.unpriced > 0) tile('next-buy', 'Next buy', DASH, `${plural(nb.unpriced, 'item')} unpriced`, 'unpriced')
  else tile('next-buy', 'Next buy', money(nb.amount), nb.unpriced ? `partial · ${plural(nb.unpriced, 'item')} unpriced` : 'estimate, incl. scrap', nb.unpriced ? 'partial' : 'estimate')
  tile('hours', 'Shop hours', m.hoursKnown ? `${fmtH(m.hoursDone)} / ${fmtH(m.hoursTotal)}` : DASH, m.hoursKnown ? 'estimate' : 'a step has no hours figure', m.hoursKnown ? 'est.' : '')
  tile('sessions', 'Sessions left in group', String(m.sessionsLeftInGroup))
  tile('calendar', 'Elapsed with cures', m.calendarHours === null ? DASH : `${fmtH(m.calendarHours)} h`, m.calendarHours === null ? 'a cure wait or a step\'s hours is unknown' : 'shop time plus cure waits')
}
