import test from 'node:test'
import assert from 'node:assert/strict'
import { declutter, type DeclutterItem } from '../src/logic/declutter'

const it = (x: number, y: number, priority: number, w = 120, tie = 0): DeclutterItem => ({ x, y, w, h: 22, priority, tie })

test('labels that do not overlap all stay full, where they are', () => {
  const out = declutter([it(100, 100, 0), it(400, 100, 0), it(100, 300, 1)])
  const full = { dy: 0, collapsed: false, hidden: false }
  assert.deepEqual(out, [full, full, full])
})

test('of two overlapping labels the higher priority keeps its place and the lower one is nudged', () => {
  const out = declutter([it(100, 100, 0), it(110, 104, 2)])
  assert.deepEqual(out[1], { dy: 0, collapsed: false, hidden: false })
  assert.equal(out[0].collapsed, false)
  assert.ok(Math.abs(out[0].dy) >= 22, 'moved clear of the other pill')
})

test('a label with no free slot near its anchor collapses to a dot; the winners never do', () => {
  // three winners stacked at the anchor and one slot above and below it: the loser has nowhere to go
  const out = declutter([it(200, 200, 0), it(200, 200, 3), it(200, 176, 3), it(200, 224, 3)])
  assert.deepEqual(out.slice(1).map((o) => o.collapsed), [false, false, false])
  assert.equal(out[0].collapsed, true)
  assert.equal(out[0].hidden, true, 'its dot would sit on a readable pill, so it is hidden')
})

test('a collapsed label keeps its dot where the dot is clear of every readable pill', () => {
  // the loser's anchor is beside the winner, its pill overlaps it in every slot, but the dot itself is clear
  const out = declutter([it(200, 200, 0, 300), it(330, 200, 5, 120), it(330, 176, 5, 120), it(330, 224, 5, 120)])
  assert.deepEqual(out[0], { dy: 0, collapsed: true, hidden: false })
})

test('equal priority: the lower tie value wins, then the earlier item', () => {
  const a = declutter([it(100, 100, 1, 120, 5), it(100, 100, 1, 120, 1), it(100, 100, 1, 120, 1), it(100, 100, 1, 120, 1)])
  assert.equal(a[1].dy, 0)
  assert.equal(a[1].collapsed, false)
  assert.equal(a[0].collapsed, true, 'the highest tie value loses when every slot is taken')
})

test('a label over an obstacle (a card) moves off it or collapses', () => {
  const card = { l: 0, t: 0, r: 300, b: 150 }
  const out = declutter([it(100, 140, 0), it(100, 400, 0)], [card])
  assert.equal(out[0].collapsed, false)
  assert.ok(140 + out[0].dy - 11 >= 150, 'nudged below the card')
  assert.deepEqual(out[1], { dy: 0, collapsed: false, hidden: false })
  const deep = declutter([it(100, 60, 0)], [card])
  assert.equal(deep[0].collapsed, true)
  assert.equal(deep[0].hidden, true, 'a dot under a card is hidden, not left peeking out')
})

test('the answer is a pure function of its input (the recorder needs the same frame every run)', () => {
  const items = [it(10, 10, 1), it(20, 12, 0), it(30, 14, 2), it(25, 30, 0)]
  assert.deepEqual(declutter(items), declutter(items.map((x) => ({ ...x }))))
})
