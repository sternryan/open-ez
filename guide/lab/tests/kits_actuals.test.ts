import test from 'node:test'
import assert from 'node:assert/strict'
import { loadActuals, saveActuals } from '../src/logic/actuals'
import type { Op, PlanJson, Storage2 } from '../src/logic/graph'
import { SCRAP, meterAt, type Kit } from '../src/logic/kits'
import type { SeqGroup } from '../src/logic/sequence'
import type { Session } from '../src/logic/sessions'
import { renderMeter, renderNavlog } from '../src/ui/navlog'

// node has no DOM. renderNavlog/renderMeter only need the surface they touch.
class El {
  tag: string
  className = ''
  _text = ''
  children: El[] = []
  dataset: Record<string, string> = {}
  attrs: Record<string, string> = {}
  type = ''
  title = ''
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
  click(): void { for (const fn of this.listeners.click ?? []) fn() }
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

const op = (id: string, group: string, plan: PlanJson): Op => ({
  id, chapter: 4, title: id, summary: '', variants: ['roncz'], components: [], group, plan,
})

const session = (p: Partial<Session> & Pick<Session, 'index' | 'group'>): Session => ({
  steps: [p.group], hours: 2, hoursKnown: true, buddy: false, cureAfter: null, ...p,
})

const groupOf = (root: El, id: string): El => {
  const g = root.querySelectorAll('.group').find((e) => e.dataset.group === id)
  assert.ok(g, id)
  return g
}

const bulk = op('bulk.a', 'bulkheads', { people: 1, hours: { value: 2, flag: 'estimate', source: null }, cure: 'none' })
const wing = op('wing.layup', 'wing', {
  people: 2,
  people_why: 'draping the skin',
  hours: { value: 3, flag: 'estimate', source: 'community-log:p4' },
  cure: 'part',
  resin: 'mgs-285-287',
  buy: [{ item: 'bid', qty: 2, flag: 'estimate' }],
})
const nose = op('nose.tip', 'nose', {
  people: 1,
  hours: { value: null, flag: 'unsourced', source: null },
  cure: 'none',
  buy: [{ item: 'peel', qty: 1, flag: 'unsourced' }],
})
const seq: SeqGroup[] = [
  { id: 'bulkheads', label: 'Seat bulkheads and firewall', steps: [bulk] },
  { id: 'wing', label: 'Wing', steps: [wing] },
  { id: 'nose', label: 'Nose', steps: [nose] },
]
const sessions: Session[] = [
  session({ index: 0, group: 'bulkheads', steps: ['bulk.a'], hours: 2 }),
  session({ index: 1, group: 'wing', steps: ['wing.layup'], hours: 3, buddy: true, cureAfter: { hours: null, scope: 'part' } }),
  session({ index: 2, group: 'nose', steps: ['nose.tip'], hours: 1, hoursKnown: false }),
]
const kits: Kit[] = [
  { group: 'bulkheads', lines: [], subtotal: 0, scrap: 0, unpriced: 0 },
  {
    group: 'wing',
    lines: [{ item: 'bid', qty: 2, unitPrice: 10, stale: false, step: 'wing.layup' }],
    subtotal: 20,
    scrap: 5,
    unpriced: 0,
  },
  {
    group: 'nose',
    lines: [{ item: 'peel', qty: 1, unitPrice: null, stale: false, step: 'nose.tip' }],
    subtotal: 0,
    scrap: 0,
    unpriced: 1,
  },
]

test('test_build_zoom_rows_and_markers', () => {
  const root = mount()
  renderNavlog(asRoot(root), seq, sessions, kits, 'bulk.a', () => {}, 'build')
  const meter = mount()
  renderMeter(asRoot(meter), meterAt(sessions, kits, 0), 'build')
  const wingRow = groupOf(root, 'wing')
  const noseRow = groupOf(root, 'nose')
  const problems: string[] = []
  const cards = root.querySelectorAll('.session').length
  if (cards !== 0) problems.push(`build zoom still renders ${cards} session card(s); every group should be one row`)
  if (wingRow.querySelectorAll('.marker.buy').length < 1) problems.push('spend marker missing on the collapsed wing row')
  if (wingRow.querySelectorAll('.marker.cure').length < 1) problems.push('cure marker missing on the collapsed wing row')
  if (wingRow.querySelectorAll('.marker.cure.warn').length < 1) problems.push('an unknown cure must keep the warn marker on the row')
  if (wingRow.querySelectorAll('.chip.buddy').length < 1) problems.push('buddy marker missing on the collapsed wing row')
  if (!wingRow.textContent.includes('estimate')) problems.push('estimate label dropped in the rollup')
  if (!wingRow.textContent.includes('community-log:p4')) problems.push('source label dropped in the rollup')
  if (!noseRow.textContent.includes('—')) problems.push('unknown hours must render as —')
  if (!noseRow.textContent.includes('unsourced')) problems.push('unsourced flag dropped in the rollup')
  if (!noseRow.textContent.includes('unpriced')) problems.push('an unpriced line must stay visible on the row and not be rolled into a total')
  if (root.textContent.includes('NaN') || meter.textContent.includes('NaN')) problems.push('unknown rendered as NaN')
  const mt = meter.textContent
  if (!/cost to date/i.test(mt)) problems.push('build zoom meter should show cost to date')
  if (!/remaining/i.test(mt)) problems.push('build zoom meter should show total remaining')
  if (!/total sessions/i.test(mt)) problems.push('build zoom meter should show total sessions')
  assert.deepEqual(problems, [])
})

test('test_build_zoom_enters_group', () => {
  const root = mount()
  const opened: string[] = []
  renderNavlog(asRoot(root), seq, sessions, kits, 'bulk.a', (id) => { opened.push(id) }, 'build')
  groupOf(root, 'wing').querySelectorAll('.group-label')[0].click()
  const problems: string[] = []
  if (groupOf(root, 'wing').querySelectorAll('.session').length < 1) problems.push('clicking a build-zoom row did not open that group\'s session cards')
  if (groupOf(root, 'bulkheads').querySelectorAll('.session').length !== 0) problems.push('entering a group should leave the other groups collapsed')
  if (groupOf(root, 'nose').querySelectorAll('.session').length !== 0) problems.push('groups that were not clicked should stay one row')
  if (opened[0] !== 'wing.layup') problems.push(`expected the group's first step wing.layup, got ${String(opened[0])}`)
  const steps = groupOf(root, 'wing').querySelectorAll('.step').map((e) => e.dataset.op)
  if (opened[0] === 'wing.layup' && steps.length && !steps.includes('wing.layup')) problems.push('the opened group does not list its step')
  assert.deepEqual(problems, [])
})

test('test_receipt_replaces_only_its_step', () => {
  // Step a is $40 plus one unpriced line. Step b is $8. Scrap is 25% of the estimated subtotal only.
  // A receipt replaces that step's estimate once: it is not added on top, and it does not replace step b.
  const catalogKits: Kit[] = [
    {
      group: 'bulkheads',
      lines: [
        { item: 'bid', qty: 4, unitPrice: 10, stale: false, step: 'a' },
        { item: 'peel', qty: 1, unitPrice: null, stale: false, step: 'a' },
        { item: 'carbon', qty: 2, unitPrice: 4, stale: false, step: 'b' },
      ],
      subtotal: 48,
      scrap: 12,
      unpriced: 1,
    },
    {
      group: 'sides',
      lines: [{ item: 'bid', qty: 1, unitPrice: 10, stale: false, step: 'c' }],
      subtotal: 10,
      scrap: 10 * SCRAP,
      unpriced: 0,
    },
  ]
  const plan = [
    session({ index: 0, group: 'bulkheads', steps: ['a', 'b'] }),
    session({ index: 1, group: 'sides', steps: ['c'] }),
  ]
  const baseline = meterAt(plan, catalogKits, 1)
  assert.equal(baseline.spent, 60)
  assert.equal(baseline.spentUnpriced, 1)
  assert.equal(Number.isNaN(baseline.spent), false)

  const replaced = meterAt(plan, catalogKits, 1, { a: { spentUsd: 30 } })
  const stepB = 8
  assert.equal(
    replaced.spent,
    30 + stepB + stepB * SCRAP,
    `receipt replaces only step a (not the whole kit, and not the estimate plus the receipt); baseline spent was ${baseline.spent}`,
  )
  assert.equal(replaced.spentUnpriced, 0, 'the receipt covers step a, so its unpriced line is no longer an unknown')
  assert.notEqual(replaced.spent, (baseline.spent ?? 0) + 30)
  assert.deepEqual(replaced.nextBuy, baseline.nextBuy, 'a receipt in an earlier group does not change the next kit')
  assert.equal(Number.isNaN(replaced.spent), false)

  const both = meterAt(plan, catalogKits, 1, { a: { spentUsd: 30 }, b: { spentUsd: 5 } })
  assert.equal(both.spent, 35, 'two receipts replace both estimates; scrap is not charged again and the old kit is not added')
  assert.equal(both.spentUnpriced, 0)

  const zero = meterAt(plan, catalogKits, 1, { b: { spentUsd: 0 } })
  assert.equal(zero.spent, 40 + 40 * SCRAP, 'zero is a real receipt for step b; step a and its unpriced line stay')
  assert.equal(zero.spentUnpriced, 1)

  const later = meterAt(plan, catalogKits, 1, { c: { spentUsd: 1 } })
  assert.equal(later.spent, baseline.spent, 'a receipt in the current group does not rewrite earlier spend')
  assert.deepEqual(later.nextBuy, { group: 'sides', amount: 1, unpriced: 0 })

  const hoursOnly = meterAt(plan, catalogKits, 1, { a: { hours: 9 } })
  assert.equal(hoursOnly.spent, baseline.spent, 'an hour with no receipt keeps the estimated spend')
  assert.equal(hoursOnly.spentUnpriced, baseline.spentUnpriced)
})

const memStore = (): Storage2 & { data: Record<string, string> } => {
  const data: Record<string, string> = {}
  return { data, getItem: (k) => (k in data ? data[k] : null), setItem: (k, v) => { data[k] = v } }
}

test('test_empty_buy_receipt_counts_once', () => {
  // f06.trial-fit buys nothing. The bond step in the same group is $40 plus scrap.
  // Trial-fit sits in two sessions, so counting the receipt per session would add it twice.
  const bond = 40
  const bondScrap = bond * SCRAP
  const nose = 8
  const noseScrap = nose * SCRAP
  const estimate = bond + bondScrap
  const boxKits: Kit[] = [
    {
      group: 'fuselage-box',
      lines: [{ item: 'bid', qty: 4, unitPrice: 10, stale: false, step: 'f06.bond-front-seat' }],
      subtotal: bond,
      scrap: bondScrap,
      unpriced: 0,
    },
    {
      group: 'nose',
      lines: [{ item: 'peel', qty: 1, unitPrice: nose, stale: false, step: 'nose.tip' }],
      subtotal: nose,
      scrap: noseScrap,
      unpriced: 0,
    },
  ]
  const plan = [
    session({ index: 0, group: 'fuselage-box', steps: ['f06.trial-fit', 'f06.bond-front-seat'] }),
    session({ index: 1, group: 'fuselage-box', steps: ['f06.trial-fit'] }),
    session({ index: 2, group: 'nose', steps: ['nose.tip'] }),
  ]
  const baseline = meterAt(plan, boxKits, 2)
  assert.equal(baseline.spent, estimate)
  assert.equal(baseline.remaining, nose + noseScrap)

  const receipt = 99
  const once = estimate + receipt
  const open = meterAt(plan, boxKits, 0, { 'f06.trial-fit': { spentUsd: receipt } })
  const logged = meterAt(plan, boxKits, 2, { 'f06.trial-fit': { spentUsd: receipt } })
  const replaced = meterAt(plan, boxKits, 2, { 'f06.bond-front-seat': { spentUsd: 30 } })
  const both = meterAt(plan, boxKits, 2, {
    'f06.trial-fit': { spentUsd: receipt },
    'f06.bond-front-seat': { spentUsd: 30 },
  })
  const cleared = meterAt(plan, boxKits, 2, {})
  const hoursOnly = meterAt(plan, boxKits, 2, { 'f06.trial-fit': { hours: 4 } })
  const store = memStore()
  saveActuals(store, { 'f06.trial-fit': { spentUsd: receipt } })
  const reloaded = meterAt(plan, boxKits, 2, loadActuals(store))
  saveActuals(store, {})
  const clearedStore = meterAt(plan, boxKits, 2, loadActuals(store))

  assert.deepEqual(
    {
      openSpent: open.spent,
      openNext: open.nextBuy?.amount,
      openRemaining: open.remaining,
      spentOnce: logged.spent,
      laterNext: logged.nextBuy,
      replacedOwn: replaced.spent,
      bothOnce: both.spent,
      cleared: cleared.spent,
      hoursOnly: hoursOnly.spent,
      reloaded: reloaded.spent,
      clearedStore: clearedStore.spent,
    },
    {
      openSpent: null,
      openNext: once,
      openRemaining: once + nose + noseScrap,
      spentOnce: once,
      laterNext: baseline.nextBuy,
      replacedOwn: 30,
      bothOnce: receipt + 30,
      cleared: estimate,
      hoursOnly: estimate,
      reloaded: once,
      clearedStore: estimate,
    },
    'a receipt on a step with no buys counts once in that group; a buy-step receipt replaces only its own estimate; clear restores; a reload keeps it',
  )
})

test('a derived value with no evidence rolls up as an estimate', () => {
  // The bench downgrades a sourced flag that has nothing readable on record. The whole-build rollup must do the same.
  const bare = op('cut.foam', 'cloth', {
    people: 1,
    hours: { value: 1.5, flag: 'derived', source: null },
    cure: 'none',
    buy: [{ item: 'foam', qty: 1, flag: 'derived', source: null }],
  })
  const noted = op('ply.note', 'noted', {
    people: 1,
    hours: { value: 2, flag: 'derived', source: '2 plies from the sketch' },
    cure: 'none',
  })
  const seqG: SeqGroup[] = [
    { id: 'cloth', label: 'Cloth', steps: [bare] },
    { id: 'noted', label: 'Noted', steps: [noted] },
  ]
  const sessionsG: Session[] = [
    session({ index: 0, group: 'cloth', steps: ['cut.foam'] }),
    session({ index: 1, group: 'noted', steps: ['ply.note'] }),
  ]
  const root = mount()
  renderNavlog(asRoot(root), seqG, sessionsG, [], 'ply.note', () => {}, 'build')
  const row = groupOf(root, 'cloth')
  assert.equal(row.textContent.includes('derived'), false, `raw derived flag in the rollup: ${row.textContent}`)
  assert.ok(row.textContent.includes('estimate'), `expected an estimate, got: ${row.textContent}`)
  const note = groupOf(root, 'noted')
  assert.ok(note.textContent.includes('derived'), note.textContent)
  assert.ok(note.textContent.includes('2 plies from the sketch'), note.textContent)
})

test('a collapsed build-zoom group summarises flags and cures once', () => {
  const build = (n: number): El => {
    const steps = Array.from({ length: n }, (_, i) => op(`s${i}`, 'bulk', {
      people: 1,
      hours: { value: 1, flag: 'estimate', source: null },
      cure: 'part',
    }))
    const seqG: SeqGroup[] = [{ id: 'bulk', label: 'Bulk', steps }]
    const sessionsG: Session[] = steps.map((s, i) => session({
      index: i,
      group: 'bulk',
      steps: [s.id],
      hours: 1,
      cureAfter: { hours: 8, scope: 'part' },
    }))
    const root = mount()
    renderNavlog(asRoot(root), seqG, sessionsG, [], steps[0].id, () => {}, 'build')
    return root
  }
  const small = build(12)
  const large = build(40)
  const markers = (root: El): El[] => groupOf(root, 'bulk').querySelectorAll('.marker')
  assert.equal(markers(small).length, markers(large).length, 'collapsed marker count must not grow with the step count')
  assert.ok(markers(small).length <= 2, `collapsed row rendered ${markers(small).length} markers`)
  const row = groupOf(small, 'bulk')
  assert.equal(row.querySelectorAll('.marker.cure').length, 1)
  assert.match(row.textContent, /12 estimates/)
  assert.match(row.textContent, /12 cure waits/)
  row.querySelectorAll('.group-label')[0].click()
  const open = groupOf(small, 'bulk')
  assert.equal(open.querySelectorAll('.marker.cure').length, 12, 'entering the group should show each cure')
  assert.match(open.querySelectorAll('.marker.cure')[0].textContent, /Cure:/)
  const detail = open.querySelector('.flags')
  assert.ok(detail, 'opened group should list each flag')
  assert.equal((detail.textContent.match(/estimate/g) ?? []).length, 12)
})
