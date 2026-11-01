import test from 'node:test'
import assert from 'node:assert/strict'
import type { Op } from '../src/logic/graph'
import type { Storage2 } from '../src/logic/graph'
import type { Env } from '../src/logic/cure'
import { applyActuals, type Actual } from '../src/logic/actuals'
import { meterAt } from '../src/logic/kits'
import {
  applyPace,
  DEFAULT_PACE,
  loadPace,
  PACE_KEY,
  PACE_LONG_EZ,
  PACE_QUALIFIER,
  savePace,
  scaledEstimateIds,
  withCustomPace,
  type Pace,
} from '../src/logic/pace'
import type { SeqGroup } from '../src/logic/sequence'
import { packSessions, type PlanStep } from '../src/logic/sessions'
import { renderBench } from '../src/ui/bench'
import { renderMeter, renderNavlog } from '../src/ui/navlog'
import { renderPace } from '../src/ui/environment'

const env: Env = { tempC: 20, humidity: 50, heat: 'none' }
const AS_LOGGED = 'As logged'
const LONG_EZ = "Long-EZ builder pace, x0.653 (derived: ratio of two builders' logs on the sections both recorded)"
const CUSTOM = 'Custom'

const step = (p: Partial<PlanStep> & Pick<PlanStep, 'id'>): PlanStep => ({
  group: 'g',
  hours: 1,
  people: 1,
  cure: 'none',
  resin: null,
  ...p,
})

const mem = (init: Record<string, string> = {}): Storage2 & { data: Record<string, string> } => {
  const data = { ...init }
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = v } }
}
const throwing: Storage2 = {
  getItem: () => { throw new Error('blocked') },
  setItem: () => { throw new Error('blocked') },
}

const close = (got: number | null, want: number): void => {
  assert.equal(got === null, false)
  assert.ok(Math.abs((got as number) - want) < 1e-9, `${got} vs ${want}`)
}

class El {
  tag: string
  className = ''
  id = ''
  _text = ''
  children: El[] = []
  dataset: Record<string, string> = {}
  attrs: Record<string, string> = {}
  type = ''
  title = ''
  value = ''
  selected = false
  hidden = false
  listeners: Record<string, Array<() => void>> = {}
  constructor(tag: string) { this.tag = tag }
  get childElementCount(): number { return this.children.length }
  set textContent(v: string) { this._text = v ?? ''; this.children = [] }
  get textContent(): string {
    // A text node set before append stays, the way the DOM keeps it beside later children.
    const kids = this.children.map((c) => c.textContent).join('')
    return kids ? this._text + kids : this._text
  }
  append(...nodes: El[]): void {
    for (const n of nodes) this.children.push(n)
  }
  replaceChildren(...nodes: El[]): void {
    this.children = []
    this._text = ''
    this.append(...nodes)
  }
  setAttribute(k: string, v: string): void { this.attrs[k] = v }
  addEventListener(type: string, fn: () => void): void { (this.listeners[type] ??= []).push(fn) }
  scrollIntoView(): void {}
  matches(sel: string): boolean {
    const classes = new Set(this.className.split(/\s+/).filter(Boolean))
    let tag: string | null = null
    let rest = sel
    const m = /^([a-z][\w-]*)(.*)$/.exec(sel)
    if (m && !sel.startsWith('.')) { tag = m[1]; rest = m[2] }
    if (tag && this.tag !== tag) return false
    return rest.split('.').filter(Boolean).every((c) => classes.has(c))
  }
  querySelectorAll(sel: string): El[] {
    const out: El[] = []
    const walk = (n: El): void => {
      for (const c of n.children) {
        if (c.matches(sel)) out.push(c)
        walk(c)
      }
    }
    walk(this)
    return out
  }
  querySelector(sel: string): El | null { return this.querySelectorAll(sel)[0] ?? null }
}

const installDom = (): void => {
  const g = globalThis as unknown as { document?: { createElement(tag: string): El } }
  if (g.document?.createElement) return
  g.document = { createElement: (tag: string) => new El(tag) }
}
installDom()

const mount = (): El => document.createElement('div') as unknown as El
const asRoot = (el: El): HTMLElement => el as unknown as HTMLElement
const fire = (el: El, type: string): void => { for (const fn of el.listeners[type] ?? []) fn() }
const findId = (root: El, id: string): El | undefined => {
  const out: El[] = []
  const walk = (n: El): void => {
    for (const c of n.children) {
      if (c.id === id) out.push(c)
      walk(c)
    }
  }
  walk(root)
  return out[0]
}
const byK = (root: El, k: string): El | undefined => {
  const out: El[] = []
  const walk = (n: El): void => {
    for (const c of n.children) {
      if (c.dataset.k === k) out.push(c)
      walk(c)
    }
  }
  walk(root)
  return out[0]
}

const benchOp = (hours: number | null): Op => ({
  id: 'step',
  chapter: 4,
  title: 'A step',
  summary: '',
  variants: ['both'],
  components: [],
  plan: { hours: { value: hours, flag: 'estimate', source: null }, cure: 'none' },
})

test('default is As logged and changes nothing', () => {
  assert.equal(PACE_LONG_EZ, 0.653)
  assert.equal(PACE_QUALIFIER, 'pace-scaled')
  assert.deepEqual(DEFAULT_PACE, { choice: 'logged', m: 1 })
  assert.equal(loadPace(null).choice, 'logged')
  assert.equal(loadPace(null).m, 1)
  const steps = [step({ id: 'a', hours: 3 }), step({ id: 'b', hours: null })]
  const out = applyPace(steps, DEFAULT_PACE.m)
  assert.deepEqual(out.map((s) => s.hours), [3, null])
  assert.equal(steps[0].hours, 3, 'the logged hours on the step are not rewritten')
  const shape = (rows: ReturnType<typeof packSessions>) => rows.map((s) => ({
    steps: s.steps, hours: s.hours, hoursKnown: s.hoursKnown, index: s.index,
  }))
  assert.deepEqual(shape(packSessions(out, {}, env, 4)), shape(packSessions(steps, {}, env, 4)))
  const root = mount()
  renderPace(asRoot(root), DEFAULT_PACE, () => {})
  const sel = findId(root, 'pace-choice')
  assert.ok(sel, 'builder pace sits with the shop controls')
  assert.equal(sel.value, 'logged')
  assert.deepEqual(sel.children.map((o) => o.textContent), [AS_LOGGED, LONG_EZ, CUSTOM])
  const customRow = findId(root, 'pace-custom-row')
  assert.ok(customRow)
  assert.equal(customRow.hidden, true)
})

test('x0.653 scales known hours and repacks sessions', () => {
  const steps = [step({ id: 'a', hours: 3 }), step({ id: 'b', hours: 3 })]
  const paced = applyPace(steps, PACE_LONG_EZ)
  close(paced[0].hours, 3 * 0.653)
  close(paced[1].hours, 3 * 0.653)
  assert.equal(steps[0].hours, 3)
  const atOne = packSessions(steps, {}, env, 4)
  const atPace = packSessions(paced, {}, env, 4)
  assert.deepEqual(atOne.map((s) => s.steps), [['a'], ['b']])
  assert.deepEqual(atPace.map((s) => s.steps), [['a', 'b']])
  close(atPace[0].hours, 6 * 0.653)
  const before = meterAt(atOne, [], 0)
  const after = meterAt(atPace, [], 0)
  assert.equal(before.hoursTotal, 6)
  close(after.hoursTotal, 6 * 0.653)
  assert.equal(before.sessionsLeftInGroup, 2)
  assert.equal(after.sessionsLeftInGroup, 1)
})

test('unknown hours stay unknown and are never multiplied into a number', () => {
  const steps = [step({ id: 'u', hours: null }), step({ id: 'k', hours: 2 }), step({ id: 'bad', hours: Number.NaN })]
  const out = applyPace(steps, PACE_LONG_EZ)
  assert.equal(out[0].hours, null)
  assert.equal(Number.isNaN(out[0].hours), false)
  close(out[1].hours, 2 * 0.653)
  assert.equal(out[2].hours, null, 'a non-finite hour is not multiplied into NaN')
  assert.equal(Number.isNaN(out[2].hours), false)
  const nanM = applyPace([step({ id: 'a', hours: 4 })], Number.NaN)
  assert.equal(nanM[0].hours, 4)
  const sessions = packSessions(out, {}, env, 4)
  assert.equal(sessions.some((s) => s.hoursKnown === false), true)
  assert.ok(sessions.every((s) => Number.isFinite(s.hours) && !Number.isNaN(s.hours)))
  const root = mount()
  renderBench(asRoot(root), benchOp(null), {}, { pace: PACE_LONG_EZ })
  const cell = byK(root, 'hours')
  assert.ok(cell)
  assert.equal(cell.textContent.includes(PACE_QUALIFIER), false)
  assert.equal(cell.textContent.includes('NaN'), false)
  assert.match(cell.textContent, /no hours/)
})

test('an owner actual is not scaled', () => {
  const steps = [step({ id: 'a', hours: 10 }), step({ id: 'b', hours: 2 })]
  const actuals: Record<string, Actual> = { a: { hours: 4 } }
  const ids = scaledEstimateIds(steps, actuals, PACE_LONG_EZ)
  assert.deepEqual([...ids], ['b'])
  assert.equal(scaledEstimateIds(steps, actuals, 1).size, 0)
  const out = applyActuals(applyPace(steps, PACE_LONG_EZ), actuals)
  assert.equal(out[0].hours, 4)
  close(out[1].hours, 2 * 0.653)
  const sessions = packSessions(out, {}, env, 4)
  assert.equal(sessions[0].steps[0], 'a')
  assert.equal(sessions[0].hours, 4)
  const zero = applyActuals(applyPace([step({ id: 'z', hours: null })], PACE_LONG_EZ), { z: { hours: 0 } })
  assert.equal(zero[0].hours, 0)
  const root = mount()
  renderBench(asRoot(root), benchOp(10), {}, { pace: PACE_LONG_EZ, actual: { hours: 4 } })
  const logged = byK(root, 'actual-hours')
  assert.ok(logged)
  assert.equal(logged.value, '4')
  const estimate = byK(root, 'hours')
  assert.ok(estimate)
  assert.match(estimate.textContent, /6\.5 h/)
  assert.match(estimate.textContent, new RegExp(PACE_QUALIFIER))
})

test('custom pace outside 0.25 to 3, NaN, or Infinity is rejected and the previous value kept', () => {
  const prev: Pace = { choice: 'custom', m: 1.5 }
  for (const bad of [0.249, 3.001, 0, -1, 4, Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY, 'nope', null, undefined]) {
    const next = withCustomPace(prev, bad)
    assert.equal(next, prev, `rejected ${String(bad)}`)
  }
  assert.deepEqual(withCustomPace(prev, 0.25), { choice: 'custom', m: 0.25 })
  assert.deepEqual(withCustomPace(prev, 3), { choice: 'custom', m: 3 })
  assert.deepEqual(withCustomPace(prev, '1.25'), { choice: 'custom', m: 1.25 })
  const root = mount()
  const seen: Pace[] = []
  renderPace(asRoot(root), { choice: 'longez', m: PACE_LONG_EZ }, (p) => { seen.push(p) })
  const sel = findId(root, 'pace-choice')
  assert.ok(sel)
  sel.value = 'custom'
  fire(sel, 'change')
  const input = findId(root, 'pace-custom')
  assert.ok(input)
  assert.equal(findId(root, 'pace-custom-row')?.hidden, false)
  const before = seen.length
  input.value = '9'
  fire(input, 'change')
  assert.equal(seen.length, before, 'a rejected custom does not replace the pace')
  assert.equal(input.value, String(PACE_LONG_EZ))
  input.value = 'Infinity'
  fire(input, 'change')
  assert.equal(seen.length, before)
  input.value = '2'
  fire(input, 'change')
  assert.deepEqual(seen.at(-1), { choice: 'custom', m: 2 })
})

test('missing or throwing storage gives As logged, and a saved pace round-trips on its own key', () => {
  assert.equal(PACE_KEY, 'longez.pace')
  const fresh = loadPace(null)
  assert.deepEqual(fresh, DEFAULT_PACE)
  assert.notEqual(fresh, DEFAULT_PACE, 'a copy, so a caller cannot change the default')
  assert.deepEqual(loadPace(throwing), DEFAULT_PACE)
  assert.deepEqual(loadPace(mem()), DEFAULT_PACE)
  savePace(null, { choice: 'longez', m: PACE_LONG_EZ })
  savePace(throwing, { choice: 'longez', m: PACE_LONG_EZ })
  for (const bad of ['{', 'null', '[]', '0.653', '{"choice":"custom","m":9}', '{"choice":"custom","m":null}', '{"choice":"nope","m":1}', '{"m":0.653}']) {
    assert.deepEqual(loadPace(mem({ [PACE_KEY]: bad })), DEFAULT_PACE, bad)
  }
  assert.deepEqual(loadPace(mem({ [PACE_KEY]: '{"choice":"logged","m":2}' })), DEFAULT_PACE)
  assert.deepEqual(loadPace(mem({ [PACE_KEY]: '{"choice":"longez","m":2}' })), { choice: 'longez', m: PACE_LONG_EZ })
  const s = mem()
  savePace(s, { choice: 'custom', m: 1.25 })
  assert.ok(PACE_KEY in s.data)
  assert.deepEqual(loadPace(s), { choice: 'custom', m: 1.25 })
  savePace(s, { choice: 'longez', m: 9 })
  assert.deepEqual(loadPace(s), { choice: 'longez', m: PACE_LONG_EZ })
})

test('the pace-scaled qualifier appears when m is not 1 and not when m is 1', () => {
  const steps = [step({ id: 'a', hours: 3 }), step({ id: 'b', hours: 3 })]
  const plainSessions = packSessions(steps, {}, env, 4)
  const pacedSessions = packSessions(applyPace(steps, PACE_LONG_EZ), {}, env, 4)
  const seq: SeqGroup[] = [{
    id: 'g',
    label: 'Group',
    steps: steps.map((s) => ({
      id: s.id,
      chapter: 4,
      title: s.id,
      summary: '',
      variants: ['roncz'],
      components: [],
      plan: { hours: { value: s.hours, flag: 'estimate', source: null }, cure: 'none' as const },
    })),
  }]
  const plainMeter = mount()
  renderMeter(asRoot(plainMeter), meterAt(plainSessions, [], 0), 'group', 1)
  const plainTile = plainMeter.querySelectorAll('.tile').find((t) => t.dataset.tile === 'hours')
  assert.ok(plainTile)
  assert.equal(plainTile.textContent.includes(PACE_QUALIFIER), false)
  assert.match(plainTile.textContent, /0 \/ 6/)
  const pacedMeter = mount()
  renderMeter(asRoot(pacedMeter), meterAt(pacedSessions, [], 0), 'group', PACE_LONG_EZ)
  const pacedTile = pacedMeter.querySelectorAll('.tile').find((t) => t.dataset.tile === 'hours')
  assert.ok(pacedTile)
  assert.match(pacedTile.textContent, /3\.9/)
  assert.match(pacedTile.textContent, new RegExp(PACE_QUALIFIER))
  const plainNav = mount()
  renderNavlog(asRoot(plainNav), seq, plainSessions, [], 'a', () => {}, 'group', 1)
  assert.equal(plainNav.textContent.includes(PACE_QUALIFIER), false)
  const pacedNav = mount()
  renderNavlog(asRoot(pacedNav), seq, pacedSessions, [], 'a', () => {}, 'group', PACE_LONG_EZ)
  assert.match(pacedNav.textContent, new RegExp(PACE_QUALIFIER))
  assert.match(pacedNav.textContent, /3\.9/)
  const plainBench = mount()
  renderBench(asRoot(plainBench), benchOp(4), {}, { pace: 1 })
  const plainHours = byK(plainBench, 'hours')
  assert.ok(plainHours)
  assert.match(plainHours.textContent, /4 h/)
  assert.equal(plainHours.textContent.includes(PACE_QUALIFIER), false)
  const pacedBench = mount()
  renderBench(asRoot(pacedBench), benchOp(4), {}, { pace: PACE_LONG_EZ })
  const pacedHours = byK(pacedBench, 'hours')
  assert.ok(pacedHours)
  assert.match(pacedHours.textContent, /2\.6 h/)
  assert.match(pacedHours.textContent, new RegExp(PACE_QUALIFIER))
  assert.equal(pacedHours.textContent.includes('4 h'), false)
})
