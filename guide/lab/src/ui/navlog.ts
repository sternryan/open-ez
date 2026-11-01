// The nav log (the session cards of the current build group, with cure and buy markers between them) and the top meter.
// Direct DOM rendering from the planning logic; no three.js. Unknown values render as "—", never as a guessed number.
import type { SeqGroup } from '../logic/sequence'
import { GROUND_GROUP } from '../logic/ground'
import type { Session } from '../logic/sessions'
import type { Kit, Meter } from '../logic/kits'
import { SCRAP } from '../logic/kits'
import { PACE_QUALIFIER } from '../logic/pace'
import { evidenceOf } from '../logic/evidence'

export const DASH = '—'

/** hours to one decimal, without a trailing .0. An unknown is a dash, never NaN. */
export const fmtH = (h: number): string => (Number.isFinite(h) ? (Math.round(h * 10) / 10).toString() : DASH)
export const money = (usd: number): string => (Number.isFinite(usd) ? '$' + Math.round(usd).toLocaleString('en-US') : DASH)
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

const FLAG_ORDER = ['estimate', 'unsourced', 'official', 'derived', 'community']

interface Rollup { bits: string[]; flagCounts: Map<string, number> }

/** Flags and citations from the steps, plus an unpriced count.
 *  A sourced flag with nothing readable on record is an estimate, the same rule the bench uses. */
function collectRollup(g: SeqGroup, kit: Kit | undefined): Rollup {
  const bits: string[] = []
  const flagCounts = new Map<string, number>()
  const say = (flag: string | undefined, source: string | null | undefined): void => {
    if (flag) {
      const shown = evidenceOf(flag, source).flag
      bits.push(shown)
      flagCounts.set(shown, (flagCounts.get(shown) ?? 0) + 1)
    }
    if (source) bits.push(source)
  }
  for (const step of g.steps) {
    const hours = step.plan?.hours
    if (hours?.value === null) bits.push(DASH)
    if (hours) say(hours.flag, hours.source)
    for (const buy of step.plan?.buy ?? []) say(buy.flag, buy.source)
  }
  if (kit && kit.unpriced > 0) bits.push('unpriced')
  return { bits, flagCounts }
}

/** One line for a collapsed group: "3 estimates, 2 unsourced", then each distinct citation, dash or unpriced mark. */
function rollupSummary(roll: Rollup): string {
  const parts: string[] = []
  const seen = new Set<string>()
  for (const flag of [...FLAG_ORDER, ...roll.flagCounts.keys()]) {
    if (seen.has(flag)) continue
    seen.add(flag)
    const n = roll.flagCounts.get(flag)
    if (!n) continue
    parts.push(flag === 'estimate' ? plural(n, 'estimate') : `${n} ${flag}`)
  }
  const extras: string[] = []
  for (const b of roll.bits) {
    if (roll.flagCounts.has(b) || extras.includes(b)) continue
    extras.push(b)
  }
  parts.push(...extras)
  return parts.join(', ')
}

/**
 * Render the nav log into `root`. In group zoom every group shows as a labelled line; the current step's group opens into its
 * session cards. Clicking another group's label goes to its first step.
 * Whole-build zoom starts with one row per group: flag counts and one cure count (buddy and spend markers kept).
 * Clicking a row opens that group — its steps, each cure, and the flag detail — and leaves the others collapsed.
 * Which row is open is kept on the root (`data-build-open`).
 */
export function renderNavlog(root: HTMLElement, seq: SeqGroup[], sessions: Session[], kits: Kit[], currentStep: string,
  onStep: (id: string) => void, zoom: 'group' | 'build', pace = 1, scaled?: ReadonlySet<string> | null): void {
  const paceOn = pace !== 1 && Number.isFinite(pace)
  // A known session is pace-scaled when one of its steps is a scaled estimate. Omit `scaled` to mark every known session.
  const sessionPaced = (s: Session): boolean =>
    paceOn && s.hoursKnown && (scaled == null || s.steps.some((id) => scaled.has(id)))
  const hoursText = (known: boolean, hours: number, paced: boolean): string =>
    known ? `~${fmtH(hours)} h${paced ? ` · ${PACE_QUALIFIER}` : ''}` : `${DASH} h`
  const draw = (): void => {
    root.replaceChildren()
    const order = seq.flatMap((g) => g.steps.map((o) => o.id))
    const curIdx = order.indexOf(currentStep)
    const curSession = sessions.findIndex((s) => s.steps.includes(currentStep))
    const curGroup = seq.find((g) => g.steps.some((o) => o.id === currentStep))?.id ?? seq[0]?.id
    const openId = zoom === 'build' ? (root.dataset.buildOpen ?? '') : (curGroup ?? '')
    for (const g of seq) {
      const mine = sessions.filter((s) => s.group === g.id)
      const open = g.id === openId
      const sec = el('section', 'group' + (g.id === curGroup ? ' current' : '') + (open ? '' : ' collapsed') + (g.id === GROUND_GROUP ? ' pinned' : ''))
      sec.dataset.group = g.id
      const head = el('button', 'group-label')
      head.type = 'button'
      head.append(el('span', 'name', g.label))
      const known = mine.every((s) => s.hoursKnown)
      const hours = mine.reduce((a, s) => a + s.hours, 0)
      const sub = [plural(mine.length, 'session'), hoursText(known, hours, known && mine.some(sessionPaced))]
      if (mine.some((s) => s.buddy)) sub.push('buddy')
      head.append(el('span', 'sub', sub.join(' · ')))
      head.setAttribute('aria-expanded', String(open))
      const first = g.steps[0]?.id
      head.addEventListener('click', () => {
        if (zoom === 'build') {
          // Draw before onStep so a caller that does not re-render still shows the opened group.
          // A caller that re-renders reads data-build-open and draws again with the new step.
          root.dataset.buildOpen = g.id
          draw()
          if (first) onStep(first)
          return
        }
        if (g.id !== curGroup && first) onStep(first)
      })
      sec.append(head)
      const kit = kits.find((k) => k.group === g.id)
      if (open) {
        if (zoom === 'build') {
          const roll = collectRollup(g, kit)
          if (roll.bits.length) sec.append(el('p', 'flags', roll.bits.join(' · ')))
        }
        if (kit && kit.lines.length) sec.append(el('div', 'marker buy', `Buy the ${g.label.toLowerCase()} kit · ${kitText(kit)}`))
        const byId = new Map(g.steps.map((o) => [o.id, o]))
        for (const s of mine) {
          const card = el('div', 'session' + (s.index === curSession ? ' current' : s.index < curSession ? ' done' : ''))
          card.dataset.session = String(s.index)
          const bits = [`Session ${s.index + 1}`, hoursText(s.hoursKnown, s.hours, sessionPaced(s))]
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
      } else if (zoom === 'build') {
        const roll = collectRollup(g, kit)
        const summary = rollupSummary(roll)
        if (summary) sec.append(el('p', 'flags', summary))
        if (kit && kit.lines.length) sec.append(el('div', 'marker buy', `Buy the ${g.label.toLowerCase()} kit · ${kitText(kit)}`))
        let cureCount = 0
        let cureUnknown = false
        for (const s of mine) {
          if (!s.cureAfter) continue
          cureCount += 1
          if (s.cureAfter.hours === null) cureUnknown = true
        }
        if (cureCount) sec.append(el('div', 'marker cure' + (cureUnknown ? ' warn' : ''), plural(cureCount, 'cure wait')))
        if (mine.some((s) => s.buddy) || g.steps.some((o) => o.plan?.people === 2)) sec.append(el('span', 'chip buddy', 'buddy'))
      }
      root.append(sec)
    }
    root.querySelector<HTMLElement>('.step.current')?.scrollIntoView({ block: 'nearest' })
  }
  draw()
}

const SHORT_LABEL: Record<string, string> = { sessions: 'Sessions left' }

/** The top meter. Group zoom is the running plan. Whole-build zoom states cost to date, total remaining and total sessions. */
export function renderMeter(root: HTMLElement, m: Meter, zoom: 'group' | 'build', pace = 1, mark?: boolean): void {
  root.replaceChildren()
  const build = zoom === 'build'
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
  const spentSub = m.spent === null ? 'no kit bought yet' : m.spentUnpriced ? `partial · ${plural(m.spentUnpriced, 'item')} unpriced` : 'estimate'
  const spentQ = m.spent === null ? '' : m.spentUnpriced ? 'partial' : 'estimate'
  tile('spent', build ? 'Cost to date' : 'Spent so far', m.spent === null ? DASH : money(m.spent), spentSub, spentQ)
  if (build) {
    const ru = m.remainingUnpriced
    if (m.remaining === null) tile('next-buy', 'Total remaining', DASH)
    else if (m.remaining === 0 && ru > 0) tile('next-buy', 'Total remaining', DASH, `${plural(ru, 'item')} unpriced`, 'unpriced')
    else tile('next-buy', 'Total remaining', money(m.remaining), ru ? `partial · ${plural(ru, 'item')} unpriced` : 'estimate, incl. scrap', ru ? 'partial' : 'estimate')
  } else {
    const nb = m.nextBuy
    if (!nb) tile('next-buy', 'Next buy', DASH)
    else if (nb.amount === 0 && nb.unpriced > 0) tile('next-buy', 'Next buy', DASH, `${plural(nb.unpriced, 'item')} unpriced`, 'unpriced')
    else tile('next-buy', 'Next buy', money(nb.amount), nb.unpriced ? `partial · ${plural(nb.unpriced, 'item')} unpriced` : 'estimate, incl. scrap', nb.unpriced ? 'partial' : 'estimate')
  }
  const paced = (mark ?? pace !== 1) && pace !== 1 && Number.isFinite(pace) && m.hoursKnown
  const hoursSub = !m.hoursKnown ? 'a step has no hours figure' : paced ? `estimate · ${PACE_QUALIFIER}` : 'estimate'
  const hoursQ = !m.hoursKnown ? '' : paced ? PACE_QUALIFIER : 'est.'
  tile('hours', 'Shop hours', m.hoursKnown ? `${fmtH(m.hoursDone)} / ${fmtH(m.hoursTotal)}` : DASH, hoursSub, hoursQ)
  tile('sessions', build ? 'Total sessions' : 'Sessions left in group', String(build ? m.totalSessions : m.sessionsLeftInGroup))
  tile('calendar', 'Elapsed with cures', m.calendarHours === null ? DASH : `${fmtH(m.calendarHours)} h`, m.calendarHours === null ? 'a cure wait or a step\'s hours is unknown' : 'shop time plus cure waits')
}
