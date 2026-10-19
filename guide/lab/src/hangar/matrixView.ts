// Loading matrix and the unknowns panel. Pure: no DOM, no fetch.

import type { DecisionRecord } from './model'

export type MatrixCell = {
  id: string
  occupancy: string
  occupancy_label: string
  bag: string
  bag_label: string
  fuel: string
  state: string
  fuel_lb: number | null
  gross_lb: number | null
  cg_in: number | null
  fwd_margin_in: number | null
  aft_margin_in: number | null
  gross_margin_lb: number | null
  ok: boolean | null
  flag: string
  loading: string
}

export type MatrixCrossing = {
  fails_above_lb: number | null
  fails_below_lb: number | null
  note: string
}

export type MatrixCrossings = {
  fwd: MatrixCrossing | null
  aft: MatrixCrossing | null
  gross: MatrixCrossing | null
}

export type MatrixDict = {
  engine: string
  cells: MatrixCell[]
  cell_count: number
  unknown_cells: number
  flag: string
  worst: {
    fwd: MatrixCell | null
    aft: MatrixCell | null
    gross: MatrixCell | null
  }
  crossings: MatrixCrossings | null
}

export type MatrixOption = {
  option: string
  label: string
  public: MatrixDict | null
  private: MatrixDict | null
  error?: string
}

export type ResearchProposal = {
  claim: string
  url: string
  title: string
}

export type ResearchSpotcheck = {
  matched: boolean
  detail: string
}

export type ResearchJob = {
  id: string
  state: string
  error: string | null
  proposal: ResearchProposal | null
  spotcheck: ResearchSpotcheck | null
}

export type UnknownState = 'open' | 'researching' | 'sourced' | 'unsourceable'

export type MatrixUnknown = {
  id: string
  text: string
  how: string
  state: UnknownState
  affects: string[]
  source?: string
  job: ResearchJob | null
}

export type MatrixResponse = {
  record_id: string
  options: MatrixOption[]
  unknowns: MatrixUnknown[]
}

const EN_DASH = '\u2013'
const UNKNOWN_STATES: readonly UnknownState[] = ['open', 'researching', 'sourced', 'unsourceable']
const LIMITS = ['fwd', 'aft', 'gross'] as const

function esc(s: unknown): string {
  return String(s ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function isObj(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value)
}

function asStr(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

function asNum(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function asBool(value: unknown): boolean | null {
  return typeof value === 'boolean' ? value : null
}

function asCell(value: unknown): MatrixCell | null {
  if (!isObj(value)) return null
  const id = typeof value.id === 'string' ? value.id : ''
  const loading = typeof value.loading === 'string' ? value.loading : ''
  if (!id && !loading) return null
  return {
    id,
    occupancy: asStr(value.occupancy),
    occupancy_label: asStr(value.occupancy_label),
    bag: asStr(value.bag),
    bag_label: asStr(value.bag_label),
    fuel: asStr(value.fuel),
    state: asStr(value.state),
    fuel_lb: asNum(value.fuel_lb),
    gross_lb: asNum(value.gross_lb),
    cg_in: asNum(value.cg_in),
    fwd_margin_in: asNum(value.fwd_margin_in),
    aft_margin_in: asNum(value.aft_margin_in),
    gross_margin_lb: asNum(value.gross_margin_lb),
    ok: asBool(value.ok),
    flag: asStr(value.flag),
    loading,
  }
}

function asCrossing(value: unknown): MatrixCrossing | null {
  if (!isObj(value)) return null
  return {
    fails_above_lb: asNum(value.fails_above_lb),
    fails_below_lb: asNum(value.fails_below_lb),
    note: asStr(value.note),
  }
}

function asCrossings(value: unknown): MatrixCrossings | null {
  if (value == null) return null
  if (!isObj(value)) return null
  return {
    fwd: asCrossing(value.fwd),
    aft: asCrossing(value.aft),
    gross: asCrossing(value.gross),
  }
}

function asMatrix(value: unknown): MatrixDict | null {
  if (!isObj(value) || !Array.isArray(value.cells)) return null
  const cells = value.cells.map(asCell).filter((cell): cell is MatrixCell => cell !== null)
  const worst = isObj(value.worst) ? value.worst : {}
  return {
    engine: asStr(value.engine),
    cells,
    cell_count: asNum(value.cell_count) ?? cells.length,
    unknown_cells: asNum(value.unknown_cells) ?? 0,
    flag: asStr(value.flag),
    worst: {
      fwd: asCell(worst.fwd),
      aft: asCell(worst.aft),
      gross: asCell(worst.gross),
    },
    crossings: asCrossings(value.crossings),
  }
}

function asOption(value: unknown): MatrixOption | null {
  if (!isObj(value)) return null
  const option = value.option
  if (typeof option !== 'string' || !option.trim() || typeof value.label !== 'string') return null
  let publicMatrix: MatrixDict | null = null
  if (value.public != null) {
    const parsed = asMatrix(value.public)
    if (!parsed) return null
    publicMatrix = parsed
  }
  let privateMatrix: MatrixDict | null = null
  if (value.private != null) {
    const parsed = asMatrix(value.private)
    if (!parsed) return null
    privateMatrix = parsed
  }
  const out: MatrixOption = { option, label: value.label, public: publicMatrix, private: privateMatrix }
  if (typeof value.error === 'string' && value.error.trim()) out.error = value.error
  return out
}

function asProposal(value: unknown): ResearchProposal | null {
  if (!isObj(value)) return null
  const claim = asStr(value.claim)
  const url = asStr(value.url)
  const title = asStr(value.title)
  if (!claim && !url && !title) return null
  return { claim, url, title }
}

function asSpotcheck(value: unknown): ResearchSpotcheck | null {
  if (!isObj(value) || typeof value.matched !== 'boolean') return null
  return { matched: value.matched, detail: asStr(value.detail) }
}

function asJob(value: unknown): ResearchJob | null {
  if (value == null) return null
  if (!isObj(value)) return null
  const id = asStr(value.id)
  const state = asStr(value.state)
  if (!id && !state) return null
  return {
    id,
    state,
    error: typeof value.error === 'string' ? value.error : null,
    proposal: asProposal(value.proposal),
    spotcheck: asSpotcheck(value.spotcheck),
  }
}

function asUnknown(value: unknown): MatrixUnknown | null {
  if (!isObj(value)) return null
  const id = value.id
  const state = value.state
  if (typeof id !== 'string' || !id.trim()) return null
  if (typeof state !== 'string' || !UNKNOWN_STATES.includes(state as UnknownState)) return null
  if ('text' in value && value.text !== undefined && typeof value.text !== 'string') return null
  if ('how' in value && value.how !== undefined && typeof value.how !== 'string') return null
  const affects = Array.isArray(value.affects)
    ? value.affects.filter((item): item is string => typeof item === 'string' && item.length > 0)
    : []
  const out: MatrixUnknown = {
    id,
    text: asStr(value.text),
    how: asStr(value.how),
    state: state as UnknownState,
    affects,
    job: asJob(value.job),
  }
  if (typeof value.source === 'string' && value.source) out.source = value.source
  return out
}

/** `GET api/matrix/<id>`. A non-object body is null. Malformed options, cells, and unknowns are dropped. */
export function asMatrixResponse(body: unknown): MatrixResponse | null {
  try {
    if (!isObj(body)) return null
    const options = Array.isArray(body.options)
      ? body.options.map(asOption).filter((option): option is MatrixOption => option !== null)
      : []
    const unknowns = Array.isArray(body.unknowns)
      ? body.unknowns.map(asUnknown).filter((item): item is MatrixUnknown => item !== null)
      : []
    return { record_id: asStr(body.record_id), options, unknowns }
  } catch {
    return null
  }
}

/** Ids still open or being researched, in response order. */
export function openUnknownIds(data: MatrixResponse | null): string[] {
  if (!data) return []
  return data.unknowns.filter((item) => item.state === 'open' || item.state === 'researching').map((item) => item.id)
}

function formatInches(value: number | null): { text: string; out: boolean } {
  if (typeof value !== 'number' || !Number.isFinite(value)) return { text: EN_DASH, out: false }
  const rounded = Number(value.toFixed(1))
  if (rounded < 0) return { text: `${value.toFixed(1)} in`, out: true }
  if (rounded > 0) return { text: `+${value.toFixed(1)} in`, out: false }
  return { text: '+0.0 in', out: false }
}

function formatLb(value: number | null): { text: string; out: boolean } {
  if (typeof value !== 'number' || !Number.isFinite(value)) return { text: EN_DASH, out: false }
  const rounded = Math.round(value)
  if (rounded < 0) return { text: `${rounded} lb`, out: true }
  return { text: `+${rounded} lb`, out: false }
}

function formatPlain(value: number | null, digits: number): { text: string; out: boolean } {
  if (typeof value !== 'number' || !Number.isFinite(value)) return { text: EN_DASH, out: false }
  const rounded = digits === 0 ? Math.round(value) : Number(value.toFixed(digits))
  const text = digits === 0 ? String(Math.round(value)) : value.toFixed(digits)
  return { text, out: rounded < 0 }
}

function cellTd(text: string, out: boolean): string {
  return out ? `<td class="out">${esc(text)}</td>` : `<td>${esc(text)}</td>`
}

function worstRow(limit: (typeof LIMITS)[number], label: string, cell: MatrixCell | null, kind: 'in' | 'lb'): string {
  const raw = !cell ? null : kind === 'lb' ? cell.gross_margin_lb : limit === 'fwd' ? cell.fwd_margin_in : cell.aft_margin_in
  const shown = kind === 'lb' ? formatLb(raw) : formatInches(raw)
  const cls = shown.out ? ' class="out"' : ''
  const outside = shown.out ? ' outside' : ''
  const loading = cell?.loading ? ` ${esc(cell.loading)}` : ''
  return `<p${cls} data-limit="${limit}"><span class="label">${label}</span> ${esc(shown.text)}${outside}${loading}</p>`
}

function worstRows(matrix: MatrixDict): string {
  return [
    worstRow('fwd', 'Forward limit', matrix.worst.fwd, 'in'),
    worstRow('aft', 'Aft limit', matrix.worst.aft, 'in'),
    worstRow('gross', 'Gross', matrix.worst.gross, 'lb'),
  ].join('')
}

function crossingNotes(crossings: MatrixCrossings | null): string {
  if (!crossings) return ''
  const notes: string[] = []
  for (const limit of LIMITS) {
    const note = crossings[limit]?.note.trim() ?? ''
    if (note) notes.push(`<p class="crossing">${esc(note)}</p>`)
  }
  return notes.join('')
}

function unknownCount(matrix: MatrixDict): string {
  if (typeof matrix.unknown_cells !== 'number' || !(matrix.unknown_cells > 0)) return ''
  return `<p class="unknown">${matrix.unknown_cells} cells unknown</p>`
}

function cellsDetails(matrix: MatrixDict): string {
  const rows = matrix.cells
    .map((cell) => {
      const gross = formatPlain(cell.gross_lb, 0)
      const cg = formatPlain(cell.cg_in, 1)
      const fwd = formatInches(cell.fwd_margin_in)
      const aft = formatInches(cell.aft_margin_in)
      const margin = formatLb(cell.gross_margin_lb)
      return `<tr><td>${esc(cell.loading)}</td>${cellTd(gross.text, gross.out)}${cellTd(cg.text, cg.out)}${cellTd(fwd.text, fwd.out)}${cellTd(aft.text, aft.out)}${cellTd(margin.text, margin.out)}</tr>`
    })
    .join('')
  return `<details><summary>All cells (${matrix.cells.length})</summary><table><thead><tr><th>Loading</th><th>Gross (lb)</th><th>CG (in)</th><th>Fwd margin</th><th>Aft margin</th><th>Gross margin</th></tr></thead><tbody>${rows}</tbody></table></details>`
}

function optionTitle(record: DecisionRecord, opt: MatrixOption): string {
  if (opt.label.trim()) return opt.label
  const found = (record.options ?? []).find((option) => option && option.id === opt.option)
  return found?.label || opt.option
}

function renderOption(record: DecisionRecord, opt: MatrixOption): string {
  const title = `<h4>${esc(optionTitle(record, opt))}</h4>`
  let body = ''
  if (!opt.public) {
    const note = opt.error?.trim() ? opt.error : 'no loading effect'
    body = `<p>${esc(note)}</p>`
  } else {
    body = `${worstRows(opt.public)}${crossingNotes(opt.public.crossings)}${unknownCount(opt.public)}${cellsDetails(opt.public)}`
  }
  if (opt.private) body += `<div class="private"><h4>Your loadings</h4>${worstRows(opt.private)}</div>`
  return `<article data-option="${esc(opt.option)}">${title}${body}</article>`
}

/** Empty when there is no matrix or no options. Text is escaped. Null margins are an en dash. */
export function renderMatrix(record: DecisionRecord, data: MatrixResponse | null): string {
  if (!data || !Array.isArray(data.options) || data.options.length === 0) return ''
  return `<section class="matrix" data-test="matrix"><h3>Loading matrix</h3>${data.options.map((opt) => renderOption(record, opt)).join('')}</section>`
}

function optionLabel(record: DecisionRecord, id: string): string {
  const found = (record.options ?? []).find((option) => option && option.id === id)
  return found?.label || id
}

function affectsText(record: DecisionRecord, ids: string[]): string {
  if (ids.length === 0) return 'Whole record'
  return ids.map((id) => optionLabel(record, id)).join(', ')
}

function researchButton(id: string): string {
  return `<button type="button" data-action="research" data-unknown="${esc(id)}">Research this</button>`
}

function renderProposal(job: ResearchJob, live: boolean): string {
  const parts: string[] = []
  const proposal = job.proposal
  if (proposal?.claim) parts.push(`<p class="claim">${esc(proposal.claim)}</p>`)
  if (proposal?.url) {
    const text = proposal.title.trim() ? proposal.title : proposal.url
    parts.push(`<a href="${esc(proposal.url)}" rel="noopener">${esc(text)}</a>`)
  }
  const matched = job.spotcheck?.matched === true
  const verdict = matched ? 'spot-check: matched' : 'spot-check: not matched'
  const detail = job.spotcheck?.detail.trim() ? ` ${esc(job.spotcheck.detail)}` : ''
  parts.push(`<p>${esc(verdict)}${detail}</p>`)
  if (live) {
    const disabled = matched ? '' : ' disabled'
    const id = esc(job.id)
    parts.push(
      `<button type="button" data-action="resolve" data-outcome="accept" data-job="${id}"${disabled}>Accept</button>`,
      `<button type="button" data-action="resolve" data-outcome="dismiss" data-job="${id}">Dismiss</button>`,
      `<button type="button" data-action="resolve" data-outcome="unsourceable" data-job="${id}">Unsourceable</button>`,
    )
  }
  return parts.join('')
}

function renderOneUnknown(record: DecisionRecord, item: MatrixUnknown, live: boolean): string {
  const parts: string[] = [
    `<p>${esc(item.text)}</p>`,
    `<p>${esc(item.how)}</p>`,
    `<span class="badge" data-state="${esc(item.state)}">${esc(item.state)}</span>`,
    `<p class="affects">${esc(affectsText(record, item.affects))}</p>`,
  ]
  if (item.state === 'sourced' && item.source) parts.push(`<p class="source">${esc(item.source)}</p>`)
  const job = item.job
  if (item.state === 'researching' && job?.state) parts.push(`<p class="job">${esc(job.state)}</p>`)
  if (job?.state === 'proposed') parts.push(renderProposal(job, live))
  if (job?.state === 'failed' && job.error) parts.push(`<p class="error">${esc(job.error)}</p>`)
  if (live && job?.state === 'failed') parts.push(researchButton(item.id))
  else if (live && item.state === 'open') parts.push(researchButton(item.id))
  return `<article>${parts.join('')}</article>`
}

/** Live mode shows the research and resolve buttons. Read-only lists the same gaps with none. */
export function renderUnknowns(record: DecisionRecord, data: MatrixResponse | null, live: boolean): string {
  if (!data || !Array.isArray(data.unknowns) || data.unknowns.length === 0) return ''
  const items = data.unknowns.map((item) => renderOneUnknown(record, item, live)).join('')
  return `<section class="unknowns" data-test="unknowns"><h3>Unknowns</h3>${items}</section>`
}
