// Hangar index. renderHangarHtml is pure so tests can run it without a DOM.

import { statusLabel, type DecisionRecord, type HangarData, type Spot } from './model'

function esc(s: unknown): string {
  return String(s ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function renderSpot(spot: Spot, records: HangarData['records']): string {
  const kicker = `<p class="kicker">${esc(spot.analogue)}</p>`
  const blurb = `<p class="blurb">${esc(spot.blurb)}</p>`
  const attr = `class="card" data-spot="${esc(spot.id)}" data-state="${esc(spot.state)}"`
  if (spot.state === 'foundation') {
    return `<article ${attr}><a class="cover" href="./">${kicker}<h2>${esc(spot.label)}</h2>${blurb}</a></article>`
  }
  if (spot.state === 'reserved') {
    return `<article ${attr}>${kicker}<h2>${esc(spot.label)}</h2>${blurb}<p class="flag">Reserved</p></article>`
  }
  const items = Object.values(records)
    .filter((r) => r.spot === spot.id)
    .map((r) => renderRecord(r))
    .join('')
  const list = items ? `<ul class="records">${items}</ul>` : ''
  return `<article ${attr}>${kicker}<h2>${esc(spot.label)}</h2>${blurb}${list}</article>`
}

function renderRecord(r: DecisionRecord): string {
  return `<li><a href="briefing.html#${esc(encodeURIComponent(r.id))}">${esc(r.title)}</a><span class="status">${esc(statusLabel(r))}</span></li>`
}

/** Four cards in spot order. The page assigns this string to the root element's innerHTML. */
export function renderHangarHtml(data: HangarData): string {
  return `<div class="spots">${data.spots.map((s) => renderSpot(s, data.records)).join('')}</div>`
}

function hangarUrl(): string {
  const base = document.querySelector('meta[name="data-base"]')?.getAttribute('content') ?? './'
  return new URL('hangar.json', new URL(base, document.baseURI)).href
}

function mount(): void {
  const root = document.getElementById('hangar')
  if (!root) return
  root.textContent = 'Loading the hangar\u2026'
  fetch(hangarUrl())
    .then((res) => {
      if (!res.ok) throw new Error(String(res.status))
      return res.json() as Promise<HangarData>
    })
    .then(async (data) => {
      // With the companion service running, its records are newer than the build-time copy.
      try {
        const live = await fetch(new URL('api/records', hangarUrl()).href)
        if (live.ok) data = { ...data, records: (await live.json()) as HangarData['records'] }
      } catch {
        /* public site: keep the built copy */
      }
      root.innerHTML = renderHangarHtml(data)
    })
    .catch(() => {
      root.textContent = 'The hangar data did not load.'
    })
}

if (typeof document !== 'undefined') mount()
