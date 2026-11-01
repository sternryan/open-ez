// The shop environment (temperature, humidity, heat) and the session length: the two settings that repack the plan.
// Storage helpers are pure (no DOM); renderEnvironment is the only DOM code and runs only in player mode.
import type { Env } from '../logic/cure'
import type { Storage2 } from '../logic/graph'

export const DEFAULT_ENV: Env = { tempC: 20, humidity: 50, heat: 'none' }
export const ENV_KEY = 'longez.env'
export const TEMP_RANGE = { min: 5, max: 30, step: 1 }
export const HUMIDITY_RANGE = { min: 20, max: 90, step: 5 }
const HEATS: Env['heat'][] = ['none', 'space-heater', 'enclosure']

export const DEFAULT_SESSION_HOURS = 4
export const SESSION_KEY = 'longez.sessionHours'
export const SESSION_RANGE = { min: 1, max: 12, step: 0.5 }

const inRange = (v: unknown, r: { min: number; max: number }): v is number => typeof v === 'number' && Number.isFinite(v) && v >= r.min && v <= r.max

/** The stored environment, or the default when storage is missing, blocked or holds anything but a whole valid env. */
export function loadEnv(storage: Storage2 | null): Env {
  try {
    const raw = storage?.getItem(ENV_KEY)
    if (raw) {
      const v = JSON.parse(raw) as Partial<Env> | null
      if (v && typeof v === 'object' && !Array.isArray(v) && inRange(v.tempC, TEMP_RANGE) && inRange(v.humidity, { min: 0, max: 100 }) && HEATS.includes(v.heat as Env['heat'])) {
        return { tempC: v.tempC, humidity: v.humidity, heat: v.heat as Env['heat'] }
      }
    }
  } catch { /* blocked storage or invalid JSON */ }
  return { ...DEFAULT_ENV }
}

export function saveEnv(storage: Storage2 | null, env: Env): void {
  try { storage?.setItem(ENV_KEY, JSON.stringify({ tempC: env.tempC, humidity: env.humidity, heat: env.heat })) } catch { /* per-viewer convenience only */ }
}

export function loadSessionHours(storage: Storage2 | null): number {
  try {
    const raw = storage?.getItem(SESSION_KEY)
    if (raw) {
      const v = Number(raw)
      if (inRange(v, SESSION_RANGE)) return v
    }
  } catch { /* blocked storage */ }
  return DEFAULT_SESSION_HOURS
}

export function saveSessionHours(storage: Storage2 | null, hours: number): void {
  try { storage?.setItem(SESSION_KEY, String(hours)) } catch { /* per-viewer convenience only */ }
}

const HEAT_TEXT: Record<Env['heat'], string> = {
  none: 'No heat',
  'space-heater': 'Space heater (+5 °C, estimate)',
  enclosure: 'Heated enclosure (+15 °C, estimate)',
}

/** The shop controls in #environment: temperature, humidity (recorded only) and heat. Every change goes to onChange. */
export function renderEnvironment(root: HTMLElement, env: Env, onChange: (e: Env) => void): void {
  root.replaceChildren()
  let cur: Env = { ...env }
  const row = (label: string, control: HTMLElement, val?: HTMLElement) => {
    const r = document.createElement('label')
    r.className = 'env-row'
    const l = document.createElement('span')
    l.className = 'label'
    l.textContent = label
    r.append(l, control)
    if (val) r.append(val)
    root.append(r)
  }
  const range = (id: string, r: { min: number; max: number; step: number }, v: number, fmt: (n: number) => string, set: (n: number) => void) => {
    const i = document.createElement('input')
    i.type = 'range'
    i.id = id
    i.min = String(r.min); i.max = String(r.max); i.step = String(r.step); i.value = String(v)
    const out = document.createElement('span')
    out.className = 'val mono'
    out.textContent = fmt(v)
    i.addEventListener('input', () => { out.textContent = fmt(+i.value) })
    i.addEventListener('change', () => { const n = +i.value; if (Number.isFinite(n)) { set(n); onChange({ ...cur }) } })
    return { i, out }
  }
  const t = range('env-temp', TEMP_RANGE, cur.tempC, (n) => `${n} °C`, (n) => { cur = { ...cur, tempC: n } })
  row('Shop temperature', t.i, t.out)
  const h = range('env-humidity', HUMIDITY_RANGE, cur.humidity, (n) => `${n} %`, (n) => { cur = { ...cur, humidity: n } })
  row('Humidity (recorded only)', h.i, h.out)
  const s = document.createElement('select')
  s.id = 'env-heat'
  for (const k of HEATS) {
    const o = document.createElement('option')
    o.value = k
    o.textContent = HEAT_TEXT[k]
    if (k === cur.heat) o.selected = true
    s.append(o)
  }
  s.addEventListener('change', () => { cur = { ...cur, heat: s.value as Env['heat'] }; onChange({ ...cur }) })
  row('Heat', s)
}
