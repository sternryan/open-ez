import test from 'node:test'
import assert from 'node:assert/strict'
import type { Actual } from '../src/logic/actuals'
import type { Op, PlanJson } from '../src/logic/graph'
import { renderBench } from '../src/ui/bench'

// node has no DOM. renderBench only needs the surface it touches.
class El {
  tag: string
  className = ''
  _text = ''
  children: El[] = []
  dataset: Record<string, string> = {}
  attrs: Record<string, string> = {}
  type = ''
  title = ''
  value = ''
  listeners: Record<string, Array<() => void>> = {}
  constructor(tag: string) { this.tag = tag }
  get childElementCount(): number { return this.children.length }
  set textContent(v: string) { this._text = v ?? ''; this.children = [] }
  get textContent(): string {
    return this.children.length ? this.children.map((c) => c.textContent).join('') : this._text
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

const step = (plan: PlanJson): Op => ({
  id: 'step', chapter: 7, title: 'Glass a side', summary: '', variants: ['both'], components: [], plan,
})

const LINE = 'Fuel-wetted: UL94 compatibility of this resin is unknown (coupon test pending)'

test('a fuel-wetted step shows the UL94 unknown line', () => {
  const root = mount()
  renderBench(asRoot(root), step({
    cure: 'part',
    resin: 'mgs-285-287',
    fuel: {
      wetted: true,
      fuel: 'UL94',
      resin_compat: 'unknown',
      why: 'no published UL94 immersion test of this resin; Block 5 coupon test pending',
      source: null,
    },
  }), {})
  const line = root.querySelector('p.fuel')
  assert.ok(line, 'fuel line missing')
  assert.equal(line.textContent, LINE)
  assert.equal(line.className.includes('unknown'), true)
  assert.equal(root.querySelectorAll('p.fuel').length, 1)
})

test('a step without plan.fuel shows no fuel line', () => {
  const root = mount()
  renderBench(asRoot(root), step({ cure: 'part', resin: 'mgs-285-287' }), {})
  assert.equal(root.querySelector('p.fuel'), null)
  assert.equal(root.textContent.includes('Fuel-wetted'), false)
  assert.equal(root.textContent.includes('UL94'), false)
})

const fire = (el: El, type: string): void => { for (const fn of el.listeners[type] ?? []) fn() }
const byK = (root: El, k: string): El | undefined => {
  const walk = (n: El): El | undefined => {
    for (const c of n.children) {
      if (c.dataset.k === k) return c
      const inner = walk(c)
      if (inner) return inner
    }
    return undefined
  }
  return walk(root)
}

test('test_negative_actual_rejected_at_entry', () => {
  const seen: Array<Actual | null> = []
  const root = mount()
  renderBench(asRoot(root), step({ cure: 'none' }), {}, {
    actual: { hours: 2, spentUsd: 10 },
    onActual: (next) => { seen.push(next) },
  })
  const hours = byK(root, 'actual-hours')
  const spent = byK(root, 'actual-spent')
  assert.ok(hours)
  assert.ok(spent)

  hours.value = '-1'
  fire(hours, 'change')
  spent.value = '-99'
  fire(spent, 'change')
  assert.deepEqual(seen, [], 'negative hours and receipts are not logged')
  assert.equal(hours.value, '2', 'a rejected hour leaves the last valid value')
  assert.equal(spent.value, '10', 'a rejected receipt leaves the last valid value')

  hours.value = '0'
  fire(hours, 'change')
  assert.deepEqual(seen.at(-1), { hours: 0, spentUsd: 10 }, 'zero hours is a real value')
  spent.value = '0'
  fire(spent, 'change')
  assert.deepEqual(seen.at(-1), { hours: 2, spentUsd: 0 }, 'zero is a real receipt')

  hours.value = ''
  fire(hours, 'change')
  assert.deepEqual(seen.at(-1), { spentUsd: 10 }, 'an empty hour still clears that field')

  const freshSeen: Array<Actual | null> = []
  const fresh = mount()
  renderBench(asRoot(fresh), step({ cure: 'none' }), {}, { onActual: (next) => { freshSeen.push(next) } })
  const freshHours = byK(fresh, 'actual-hours')
  const freshSpent = byK(fresh, 'actual-spent')
  assert.ok(freshHours)
  assert.ok(freshSpent)
  freshHours.value = '-3'
  fire(freshHours, 'change')
  freshSpent.value = '-4'
  fire(freshSpent, 'change')
  assert.deepEqual(freshSeen, [], 'a negative on an empty actual is not logged')
  assert.equal(freshHours.value, '')
  assert.equal(freshSpent.value, '')
  freshHours.value = '0'
  fire(freshHours, 'change')
  assert.deepEqual(freshSeen.at(-1), { hours: 0 })
  freshSpent.value = '0'
  fire(freshSpent, 'change')
  assert.deepEqual(freshSeen.at(-1), { spentUsd: 0 })
})
