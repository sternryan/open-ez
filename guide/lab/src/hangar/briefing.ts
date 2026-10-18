// Briefing room. renderBriefingHtml is pure so tests can run it without a DOM.

import {
  skin,
  statusLabel,
  type Axis,
  type DecisionRecord,
  type HangarData,
  type Option,
  type Position,
  type Unknown,
} from './model'
import {
  detectMode,
  reduce,
  type Mode,
  type State,
  type Status,
  type TranscriptLine,
} from './briefingState'

function esc(s: unknown): string {
  return String(s ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function asText(value: unknown): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number') return formatNumber(value)
  if (typeof value === 'boolean') return value ? 'yes' : 'no'
  return ''
}

function formatNumber(n: number): string {
  if (!Number.isFinite(n)) return '—'
  return String(Math.round(n * 1000) / 1000)
}

function formatUnknown(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'number') return formatNumber(value)
  if (typeof value === 'boolean') return value ? 'yes' : 'no'
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value)
  } catch {
    return ''
  }
}

const METRIC_LABELS: Record<string, string> = {
  empty_lb: 'Empty weight (lb)',
  empty_cg: 'Empty CG (in)',
  fuel_needed_lb: 'Fuel needed (lb)',
  takeoff_lb: 'Takeoff weight (lb)',
  takeoff_cg: 'Takeoff CG (in)',
  landing_cg: 'Landing CG (in)',
  range_full_fuel_nm: 'Range, full fuel (nm)',
  block_time_h: 'Block time (h)',
  in_envelope: 'In envelope',
}

function recommendationText(record: DecisionRecord, id: string): string {
  const found = (record.options ?? []).find((o) => o && o.id === id)
  if (found && found.label && found.label !== id) return `${found.label} (${id})`
  return id
}

function renderList(items: string[], empty: string): string {
  if (items.length === 0) return `<p class="muted">${esc(empty)}</p>`
  return `<ul>${items.map((item) => `<li>${esc(item)}</li>`).join('')}</ul>`
}

function renderDecision(record: DecisionRecord): string {
  const decision = record.decision
  if (!decision) return ''
  const picks = decision.picks ?? {}
  const ordered: string[] = []
  const seen = new Set<string>()
  for (const axis of record.axes ?? []) {
    const id = picks[axis.id]
    if (typeof id === 'string' && id) {
      ordered.push(recommendationText(record, id))
      seen.add(axis.id)
    }
  }
  for (const [axis, id] of Object.entries(picks)) {
    if (!seen.has(axis) && id) ordered.push(recommendationText(record, id))
  }
  return `<p class="decision"><span class="label">Decision</span> ${esc(ordered.join(' + '))} — ${esc(decision.reason)}</p>`
}

function renderSkin(record: DecisionRecord, state: State): string {
  const view = skin(record)
  const label = statusLabel({ ...record, status: state.status })
  const lines: string[] = []
  for (const axis of record.axes ?? []) {
    const id = view.recommendations[axis.id]
    if (!id) continue
    lines.push(`<p class="rec"><span class="label">${esc(axis.id)}</span> ${esc(recommendationText(record, id))}</p>`)
  }
  const recBody = lines.length > 0 ? lines.join('') : '<p class="rec">None yet</p>'
  const decision = renderDecision(record)
  return `<section class="panel skin">
    <div data-test="recommendation">
      <p class="kicker">Recommendation</p>
      ${recBody}
    </div>
    <p><span class="label">Why</span> ${esc(view.why ?? '—')}</p>
    <p><span class="label">Confidence</span> ${esc(view.confidence ?? '—')}</p>
    <h3>Disagreements</h3>
    ${renderList(view.disagreements, 'None')}
    <h3>Unknowns</h3>
    ${renderList(view.unknowns, 'None')}
    ${decision}
    <p class="status">${esc(label)}</p>
  </section>`
}

function renderFact(fact: { text?: unknown; cite?: unknown; flag?: unknown }): string {
  const cite = asText(fact.cite)
  const flag = asText(fact.flag)
  const citeHtml = cite ? ` <span class="cite">${esc(cite)}</span>` : ''
  const flagHtml = flag ? ` <span class="flag" data-flag="${esc(flag)}">${esc(flag)}</span>` : ''
  return `<li>${esc(asText(fact.text))}${citeHtml}${flagHtml}</li>`
}

function renderBook(book: Record<string, unknown>): string {
  const text = asText(book.text)
  const cite = asText(book.cite)
  const why = asText(book.why)
  const chunks: string[] = []
  if (text) chunks.push(`<p>${esc(text)}</p>`)
  if (why) chunks.push(`<p>${esc(why)}</p>`)
  if (cite) chunks.push(`<p class="cite">${esc(cite)}</p>`)
  for (const [key, value] of Object.entries(book)) {
    if (key === 'text' || key === 'cite' || key === 'why') continue
    const extra = asText(value)
    if (extra) chunks.push(`<p><span class="label">${esc(key)}</span> ${esc(extra)}</p>`)
  }
  return chunks.join('') || '<p class="muted">No book choice recorded.</p>'
}

function renderImplies(option: Option): string {
  const implies = option.implies
  if (!implies || typeof implies.tank_resin !== 'string' || !implies.tank_resin.trim()) return ''
  const cite = implies.cite ? ` <span class="cite">${esc(implies.cite)}</span>` : ''
  const flag = implies.flag ? ` <span class="flag" data-flag="${esc(implies.flag)}">${esc(implies.flag)}</span>` : ''
  return `<p class="implies">${esc(implies.tank_resin)}${cite}${flag}</p>`
}

function renderOptions(record: DecisionRecord): string {
  const options = record.options ?? []
  if (options.length === 0) return '<p class="muted">No options recorded.</p>'
  return options
    .map((o) => {
      const facts = (o.facts ?? []).map((fact) => renderFact(fact)).join('')
      const why = o.why ? `<p>${esc(o.why)}</p>` : ''
      const list = facts ? `<ul>${facts}</ul>` : ''
      return `<article class="option"><h3>${esc(o.label)} <span class="kind">${esc(o.kind)}</span></h3>${list}${why}${renderImplies(o)}</article>`
    })
    .join('')
}

function renderMetric(key: string, value: unknown): string {
  const label = METRIC_LABELS[key] ?? key
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const row = value as Record<string, unknown>
    if ('v' in row || 'flag' in row) {
      const shown = row.v === null || row.v === undefined || row.v === '' ? '—' : formatUnknown(row.v)
      const flag = asText(row.flag)
      const note = asText(row.note)
      const flagHtml = flag ? ` <span class="flag" data-flag="${esc(flag)}">${esc(flag)}</span>` : ''
      const noteHtml = note ? ` <span class="note">${esc(note)}</span>` : ''
      return `<li><span class="label">${esc(label)}</span> ${esc(shown)}${flagHtml}${noteHtml}</li>`
    }
  }
  return `<li><span class="label">${esc(label)}</span> ${esc(formatUnknown(value))}</li>`
}

function optionLabel(record: DecisionRecord, id: string): string {
  const found = (record.options ?? []).find((o) => o && o.id === id)
  return found?.label || id
}

function renderScore(record: DecisionRecord, id: string, row: unknown): string {
  const title = esc(optionLabel(record, id))
  if (!row || typeof row !== 'object' || Array.isArray(row)) {
    return `<article class="score"><h3>${title}</h3><p>${esc(formatUnknown(row))}</p></article>`
  }
  const obj = row as Record<string, unknown>
  const metrics = Object.entries(obj)
    .filter(([key]) => key !== 'option' && key !== 'assumptions' && key !== 'worst_flag')
    .map(([key, value]) => renderMetric(key, value))
    .join('')
  const worst = asText(obj.worst_flag)
  const worstHtml = worst
    ? `<p><span class="label">Worst flag</span> <span class="flag" data-flag="${esc(worst)}">${esc(worst)}</span></p>`
    : ''
  const assumptions = Array.isArray(obj.assumptions)
    ? `<ul class="assumptions">${obj.assumptions.map((item) => `<li>${esc(asText(item))}</li>`).join('')}</ul>`
    : ''
  const list = metrics ? `<ul class="metrics">${metrics}</ul>` : ''
  return `<article class="score"><h3>${title}</h3>${list}${worstHtml}${assumptions}</article>`
}

/** Recommended engine when the council has one, otherwise the first option on the engine axis. */
function missionEngineId(record: DecisionRecord): string | null {
  const recommended = skin(record).recommendations.engine
  if (typeof recommended === 'string' && recommended) return recommended
  const engine = (record.axes ?? []).find((axis) => axis.id === 'engine')
  const first = engine?.options?.[0]
  return typeof first === 'string' && first ? first : null
}

function renderMission(record: DecisionRecord): string {
  const score = record.mission_score
  if (score === null || score === undefined) return '<p class="muted">No mission scores.</p>'
  if (typeof score !== 'object' || Array.isArray(score)) return `<p>${esc(formatUnknown(score))}</p>`
  const table = score as Record<string, unknown>
  const id = missionEngineId(record)
  if (id) return renderScore(record, id, table[id])
  return Object.entries(table)
    .map(([key, row]) => renderScore(record, key, row))
    .join('')
}

function renderBackbone(record: DecisionRecord): string {
  const book =
    record.book_choice && typeof record.book_choice === 'object' ? record.book_choice : {}
  return `<details class="panel backbone">
    <summary>Backbone</summary>
    <section><h3>Book choice</h3>${renderBook(book)}</section>
    <section><h3>Options</h3>${renderOptions(record)}</section>
    <section><h3>Mission scores</h3>${renderMission(record)}</section>
  </details>`
}

function whoLabel(who: TranscriptLine['who']): string {
  if (who === 'owner') return 'You'
  if (who === 'council') return 'Council'
  return 'Error'
}

function renderChat(state: State): string {
  const lines = state.transcript
    .filter((line) => line.text.trim().length > 0)
    .map(
      (line) =>
        `<li data-who="${esc(line.who)}"><span class="who">${esc(whoLabel(line.who))}</span> ${esc(line.text)}</li>`,
    )
    .join('')
  const list = lines ? `<ol class="transcript">${lines}</ol>` : ''
  const err = state.error ? `<p class="error" role="alert">${esc(state.error)}</p>` : ''
  const busy = state.busy ? ' disabled' : ''
  return `<form data-test="chat">
    <label>Message <textarea name="message" required rows="3"></textarea></label>
    <button type="submit"${busy}>Send</button>
  </form>${list}${err}`
}

function selectableOptions(record: DecisionRecord, axis: Axis): { id: string; label: string }[] {
  const byId = new Map((record.options ?? []).map((o) => [o.id, o]))
  const out: { id: string; label: string }[] = []
  for (const id of axis.options ?? []) {
    const found = byId.get(id)
    if (found && (found.kind === 'dropped' || found.kind === 'unavailable')) continue
    out.push({ id, label: found?.label || id })
  }
  return out
}

function renderDecide(record: DecisionRecord, state: State): string {
  const selects = (record.axes ?? [])
    .map((axis) => {
      const options = ['<option value="">Select\u2026</option>']
        .concat(selectableOptions(record, axis)
        .map((o) => `<option value="${esc(o.id)}">${esc(o.label)}</option>`))
        .join('')
      return `<label>${esc(axis.id)} <select name="pick-${esc(axis.id)}" required>${options}</select></label>`
    })
    .join('')
  const disabled = state.decideEnabled ? '' : ' disabled'
  return `<form data-test="decide">
    <fieldset${disabled}>
      <legend>Decide</legend>
      ${selects}
      <label>Reason <textarea name="reason" required rows="3"></textarea></label>
      <button type="submit">Decide</button>
    </fieldset>
  </form>`
}

/** Reads `pick-<axisId>` fields into the body POST api/decide sends, aside from the record id. */
export function buildDecidePayload(
  data: { get(name: string): unknown },
  axes: readonly { id: string }[],
): { picks: Record<string, string>; reason: string } {
  const picks: Record<string, string> = {}
  for (const axis of axes) {
    const raw = data.get(`pick-${axis.id}`)
    if (typeof raw !== 'string') continue
    const value = raw.trim()
    if (value) picks[axis.id] = value
  }
  const reasonRaw = data.get('reason')
  const reason = typeof reasonRaw === 'string' ? reasonRaw.trim() : ''
  return { picks, reason }
}

function renderReopen(state: State): string {
  const disabled = state.status === 'decided' ? '' : ' disabled'
  return `<form data-test="reopen">
    <fieldset${disabled}>
      <legend>Reopen</legend>
      <label>Reason <textarea name="reason" required rows="2"></textarea></label>
      <button type="submit">Reopen</button>
    </fieldset>
  </form>`
}

function renderLive(record: DecisionRecord, state: State): string {
  return `<section class="panel live"><h3>Council</h3>${renderChat(state)}${renderDecide(record, state)}${renderReopen(state)}</section>`
}

/** Skin, backbone, and (in live mode) the council controls. Record text is escaped. */
export function renderBriefingHtml(record: DecisionRecord, mode: Mode, state: State): string {
  const live = mode === 'live' ? renderLive(record, state) : ''
  return `<article class="record">
    <header class="record-head"><p class="kicker">${esc(record.spot)}</p><h2>${esc(record.title)}</h2><p class="question">${esc(record.question)}</p></header>
    ${renderSkin(record, state)}
    ${renderBackbone(record)}
    ${live}
  </article>`
}

function asStatus(value: string): Status {
  if (value === 'decided' || value === 'reopened') return value
  return 'open'
}

function resourceUrl(path: string): string {
  const base = document.querySelector('meta[name="data-base"]')?.getAttribute('content') ?? './'
  return new URL(path, new URL(base, document.baseURI)).href
}

function recordIdFromLocation(): string {
  const raw = location.hash.startsWith('#') ? location.hash.slice(1) : location.hash
  if (!raw) return ''
  try {
    return decodeURIComponent(raw).trim()
  } catch {
    return raw.trim()
  }
}

function showMessage(text: string): void {
  const root = document.getElementById('briefing')
  if (!root) return
  root.textContent = text
}

async function readBody(res: Response): Promise<unknown> {
  try {
    return await res.json()
  } catch {
    return null
  }
}

function bodyError(body: unknown): string | null {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null
  const err = (body as { error?: unknown }).error
  if (typeof err === 'string' && err.trim()) return err.trim()
  return null
}

function failureMessage(status: number, body: unknown): string {
  return bodyError(body) ?? `The briefing service returned ${status}.`
}

function replyText(body: unknown): string {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return ''
  const text = (body as { reply_text?: unknown }).reply_text
  return typeof text === 'string' ? text : ''
}

function asPicks(value: unknown): Record<string, string> | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null
  const out: Record<string, string> = {}
  for (const [key, pick] of Object.entries(value)) {
    if (typeof pick !== 'string') return null
    const trimmed = pick.trim()
    if (!trimmed) return null
    out[key] = trimmed
  }
  return out
}

function asPositions(value: unknown): Position[] | null {
  if (!Array.isArray(value)) return null
  const out: Position[] = []
  for (const item of value) {
    if (!item || typeof item !== 'object') return null
    const p = item as Record<string, unknown>
    if (typeof p.role !== 'string') return null
    const picks = asPicks(p.picks)
    if (!picks) return null
    const citations = Array.isArray(p.citations) ? p.citations.filter((c): c is string => typeof c === 'string') : []
    out.push({
      role: p.role,
      picks,
      confidence: typeof p.confidence === 'string' ? p.confidence : 'low',
      reasoning: typeof p.reasoning === 'string' ? p.reasoning : '',
      citations,
      judgment: p.judgment === true,
    })
  }
  return out
}

function asUnknowns(value: unknown): Unknown[] | null {
  if (!Array.isArray(value)) return null
  const out: Unknown[] = []
  for (const item of value) {
    if (typeof item === 'string') {
      if (item.trim()) out.push({ text: item })
      continue
    }
    if (!item || typeof item !== 'object') continue
    const u = item as Record<string, unknown>
    out.push({ text: asText(u.text), what: asText(u.what), how: asText(u.how) })
  }
  return out
}

function applyReply(current: DecisionRecord, body: unknown): DecisionRecord {
  if (!body || typeof body !== 'object') return current
  let next = current
  const positions = asPositions((body as { positions?: unknown }).positions)
  if (positions && positions.length > 0) next = { ...next, positions }
  const extra = asUnknowns((body as { unknowns?: unknown }).unknowns)
  if (extra && extra.length > 0) next = { ...next, unknowns: [...(next.unknowns ?? []), ...extra] }
  return next
}

function isRecord(value: unknown): value is DecisionRecord {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  const r = value as Partial<DecisionRecord>
  return typeof r.id === 'string' && typeof r.title === 'string' && typeof r.status === 'string' && typeof r.question === 'string'
}

async function refreshRecord(id: string): Promise<DecisionRecord | null> {
  try {
    const res = await fetch(resourceUrl('api/records'))
    if (!res.ok) return null
    const body: unknown = await res.json()
    if (!body || typeof body !== 'object' || Array.isArray(body)) return null
    const found = (body as Record<string, unknown>)[id]
    return isRecord(found) ? found : null
  } catch {
    return null
  }
}

export function linesFromTurns(body: unknown): TranscriptLine[] {
  if (!Array.isArray(body)) return []
  const lines: TranscriptLine[] = []
  for (const turn of body) {
    if (!turn || typeof turn !== 'object') continue
    const t = turn as Record<string, unknown>
    if (typeof t.message === 'string' && t.reply && typeof t.reply === 'object') {
      // the server's stored shape: {ts, message, reply: {reply_text, positions, unknowns, error}}
      const rep = t.reply as Record<string, unknown>
      if (t.message.trim()) lines.push({ who: 'owner', text: t.message })
      if (typeof rep.reply_text === 'string' && rep.reply_text.trim()) lines.push({ who: 'council', text: rep.reply_text })
      if (typeof rep.error === 'string' && rep.error) lines.push({ who: 'error', text: rep.error })
      continue
    }
    if (typeof t.message === 'string' || typeof t.reply === 'string') {
      if (typeof t.message === 'string' && t.message.trim()) lines.push({ who: 'owner', text: t.message })
      if (typeof t.reply === 'string' && t.reply.trim()) lines.push({ who: 'council', text: t.reply })
      continue
    }
    if ((t.who === 'owner' || t.who === 'council' || t.who === 'error') && typeof t.text === 'string' && t.text.trim()) {
      lines.push({ who: t.who, text: t.text })
    }
  }
  return lines
}

async function loadTranscript(id: string): Promise<TranscriptLine[]> {
  try {
    const res = await fetch(resourceUrl(`api/transcript/${encodeURIComponent(id)}`))
    if (!res.ok) return []
    return linesFromTurns(await res.json())
  } catch {
    return []
  }
}

async function postJson(path: string, payload: unknown): Promise<{ ok: boolean; status: number; body: unknown }> {
  const res = await fetch(resourceUrl(path), {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const body = await readBody(res)
  return { ok: res.ok, status: res.status, body }
}

let record: DecisionRecord | null = null
let state: State | null = null
let mode: Mode = 'read-only'
let generation = 0
let inflight = false
let bound = false

function paint(): void {
  const root = document.getElementById('briefing')
  if (!root || !record || !state) return
  root.innerHTML = renderBriefingHtml(record, mode, state)
}

function initialState(recordId: string, nextMode: Mode, status: Status, transcript: TranscriptLine[]): State {
  const loaded = reduce(
    {
      recordId,
      mode: nextMode,
      status: 'open',
      transcript: [],
      error: null,
      busy: false,
      decideEnabled: true,
    },
    { type: 'loaded', status },
  )
  return { ...loaded, transcript }
}

async function load(): Promise<void> {
  const root = document.getElementById('briefing')
  if (!root) return
  const gen = ++generation
  const id = recordIdFromLocation()
  if (!id) {
    record = null
    state = null
    showMessage('Open a record from the hangar.')
    return
  }
  showMessage('Loading the briefing…')
  try {
    const res = await fetch(resourceUrl('hangar.json'))
    if (!res.ok) throw new Error(String(res.status))
    const data = (await res.json()) as HangarData
    if (gen !== generation) return
    const found = data.records && Object.hasOwn(data.records, id) ? data.records[id] : undefined
    if (!found) {
      record = null
      state = null
      showMessage('That record is not in the hangar.')
      return
    }
    mode = await detectMode(async (url) => fetch(resourceUrl(url)))
    if (gen !== generation) return
    let next = found
    let transcript: TranscriptLine[] = []
    if (mode === 'live') {
      const fresh = await refreshRecord(id)
      if (gen !== generation) return
      if (fresh) next = fresh
      transcript = await loadTranscript(id)
      if (gen !== generation) return
    }
    record = next
    state = initialState(id, mode, asStatus(next.status), transcript)
    document.title = `${next.title} — Briefing`
    paint()
  } catch {
    if (gen !== generation) return
    record = null
    state = null
    showMessage('The briefing did not load.')
  }
}

async function onSubmit(ev: Event): Promise<void> {
  const form = ev.target
  if (!(form instanceof HTMLFormElement)) return
  const kind = form.getAttribute('data-test')
  if (kind !== 'chat' && kind !== 'decide' && kind !== 'reopen') return
  if (!form.reportValidity()) return
  ev.preventDefault()
  if (!record || !state || mode !== 'live' || inflight) return
  const current = record
  const snapshot = state
  const data = new FormData(form)
  const gen = generation
  try {
    if (kind === 'chat') {
      const message = String(data.get('message') ?? '').trim()
      if (!message || snapshot.busy) return
      inflight = true
      state = reduce(snapshot, { type: 'sent', text: message })
      paint()
      const res = await postJson('api/brief', { record_id: current.id, message })
      if (gen !== generation || !state) return
      const err = !res.ok ? failureMessage(res.status, res.body) : bodyError(res.body)
      if (err) {
        state = reduce(state, { type: 'errored', message: err })
      } else {
        state = reduce(state, { type: 'replied', text: replyText(res.body) })
        const fresh = await refreshRecord(current.id)
        if (gen !== generation) return
        record = fresh ?? applyReply(current, res.body)
      }
    } else if (kind === 'decide') {
      const axes = current.axes ?? []
      const built = buildDecidePayload(data, axes)
      const complete = axes.length > 0 && axes.every((axis) => built.picks[axis.id])
      if (!complete || !built.reason || !snapshot.decideEnabled) return
      inflight = true
      const res = await postJson('api/decide', { record_id: current.id, picks: built.picks, reason: built.reason })
      if (gen !== generation || !state) return
      if (!res.ok) {
        state = reduce(state, { type: 'errored', message: failureMessage(res.status, res.body) })
      } else {
        state = reduce(state, { type: 'decided' })
        const fresh = await refreshRecord(current.id)
        if (gen !== generation) return
        record = fresh ?? { ...current, status: 'decided', decision: { picks: built.picks, date: '', reason: built.reason } }
      }
    } else {
      const reason = String(data.get('reason') ?? '').trim()
      if (!reason || snapshot.status !== 'decided') return
      inflight = true
      const res = await postJson('api/reopen', { record_id: current.id, reason })
      if (gen !== generation || !state) return
      if (!res.ok) {
        state = reduce(state, { type: 'errored', message: failureMessage(res.status, res.body) })
      } else {
        state = reduce(state, { type: 'reopened' })
        const fresh = await refreshRecord(current.id)
        if (gen !== generation) return
        record = fresh ?? { ...current, status: 'reopened' }
      }
    }
    if (gen === generation) paint()
  } catch {
    if (gen !== generation || !state) return
    state = reduce(state, { type: 'errored', message: 'The briefing service did not respond.' })
    paint()
  } finally {
    inflight = false
  }
}

function mount(): void {
  const root = document.getElementById('briefing')
  if (!root) return
  if (!bound) {
    bound = true
    root.addEventListener('submit', (ev) => {
      void onSubmit(ev)
    })
    window.addEventListener('hashchange', () => {
      void load()
    })
  }
  void load()
}

if (typeof document !== 'undefined') mount()
