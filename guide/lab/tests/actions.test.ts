import test from 'node:test'
import assert from 'node:assert/strict'
import { ACTION_SECONDS, CAPTION_ONLY_SECONDS, compileStep, type Action } from '../src/logic/actions'

test('ACTION_SECONDS and the caption-only duration are the contract table', () => {
  assert.deepEqual(ACTION_SECONDS, {
    place: 1.2,
    'wet-out': 1.0,
    squeegee: 1.4,
    drape: 1.6,
    cut: 1.0,
    flip: 2.0,
    sand: 1.2,
    'check-level': 1.0,
    'check-string': 1.0,
    bond: 1.2,
    'wait-cure': 0.8,
  })
  assert.equal(CAPTION_ONLY_SECONDS, 2.5)
})

test('compileStep keeps generated ply count, order, and cloth sequence', () => {
  const materials = [
    { cloth: 'BID', plies: 2 },
    { cloth: 'UND', plies: 1 },
  ]
  const plyTotal = materials.reduce((n, m) => n + m.plies, 0)
  const actions: Action[] = [{ do: 'place', part: 'fuselage.firewall', who: 'owner' }]
  const clothAtPly: string[] = []
  let ply = 1
  for (const material of materials) {
    for (let i = 0; i < material.plies; i++) {
      clothAtPly[ply] = material.cloth
      actions.push({ do: 'wet-out', ply, tool: 'brush', who: 'owner' })
      actions.push({ do: 'squeegee', ply, tool: 'squeegee', who: 'owner' })
      ply += 1
    }
  }
  assert.equal(plyTotal, 3)
  assert.deepEqual(clothAtPly.slice(1), ['BID', 'BID', 'UND'])

  const beats = compileStep(actions, 'Firewall aft face', plyTotal)
  assert.equal(beats.length, actions.length)
  assert.deepEqual(beats.map((b) => b.action?.ply ?? null), [null, 1, 1, 2, 2, 3, 3])
  assert.deepEqual(beats.map((b) => b.caption), [
    'place fuselage.firewall',
    'wet out ply 1 of 3',
    'squeegee ply 1 of 3',
    'wet out ply 2 of 3',
    'squeegee ply 2 of 3',
    'wet out ply 3 of 3',
    'squeegee ply 3 of 3',
  ])
  assert.equal(beats[0].t, 0)
  for (let i = 1; i < beats.length; i++) assert.equal(beats[i].t, beats[i - 1].t + beats[i - 1].dur)
  assert.deepEqual(beats.map((b) => b.dur), actions.map((a) => ACTION_SECONDS[a.do]))
  assert.ok(beats.every((b) => Number.isFinite(b.t) && Number.isFinite(b.dur)))
})

test('captions name the action in our own words', () => {
  const cases: { action: Action; plyTotal: number; caption: string }[] = [
    { action: { do: 'place', part: 'fuselage.firewall', who: 'owner' }, plyTotal: 3, caption: 'place fuselage.firewall' },
    { action: { do: 'cut', part: 'fuselage.firewall', who: 'owner' }, plyTotal: 3, caption: 'cut fuselage.firewall' },
    { action: { do: 'wet-out', ply: 2, tool: 'brush', who: 'owner' }, plyTotal: 3, caption: 'wet out ply 2 of 3' },
    { action: { do: 'squeegee', ply: 2, tool: 'squeegee', who: 'owner' }, plyTotal: 3, caption: 'squeegee ply 2 of 3' },
    { action: { do: 'drape', ply: 2, tool: 'brush', who: 'owner' }, plyTotal: 3, caption: 'drape ply 2 of 3' },
    { action: { do: 'flip', part: 'fuselage.firewall', who: 'owner' }, plyTotal: 3, caption: 'flip fuselage.firewall' },
    { action: { do: 'sand', part: 'fuselage.firewall', who: 'owner' }, plyTotal: 3, caption: 'sand fuselage.firewall' },
    { action: { do: 'check-level', tool: 'level', who: 'owner' }, plyTotal: 3, caption: 'check level' },
    { action: { do: 'check-string', tool: 'string-line', who: 'owner' }, plyTotal: 3, caption: 'check with the string line' },
    { action: { do: 'bond', part: 'fuselage.firewall', who: 'owner' }, plyTotal: 3, caption: 'bond fuselage.firewall' },
    { action: { do: 'wait-cure', who: 'owner' }, plyTotal: 3, caption: 'wait for cure' },
    { action: { do: 'wet-out', ply: 1, who: 'owner' }, plyTotal: 0, caption: 'wet out ply 1' },
    { action: { do: 'squeegee', ply: 1, who: 'owner' }, plyTotal: 0, caption: 'squeegee ply 1' },
    { action: { do: 'drape', ply: 4, who: 'owner' }, plyTotal: 0, caption: 'drape ply 4' },
  ]
  for (const c of cases) {
    const [beat] = compileStep([c.action], 'Step title', c.plyTotal)
    assert.equal(beat.caption, c.caption)
    assert.equal(beat.dur, ACTION_SECONDS[c.action.do])
  }
})

test('why is copied onto the beat and stays off the caption', () => {
  const beats = compileStep([
    { do: 'place', part: 'fuselage.firewall', who: 'owner' },
    { do: 'squeegee', ply: 1, tool: 'squeegee', who: 'owner', why: 'optional, ground school only' },
  ], 'Firewall aft face', 1)
  assert.equal(beats[0].why, undefined)
  assert.equal(beats[1].why, 'optional, ground school only')
  assert.equal(beats[1].caption, 'squeegee ply 1 of 1')
})

test('a step with no script is one finite caption-only beat', () => {
  for (const actions of [undefined, [] as Action[]]) {
    const beats = compileStep(actions, 'Check the jig', 0)
    assert.equal(beats.length, 1)
    assert.equal(beats[0].t, 0)
    assert.equal(beats[0].dur, CAPTION_ONLY_SECONDS)
    assert.equal(beats[0].dur, 2.5)
    assert.ok(Number.isFinite(beats[0].dur))
    assert.equal(beats[0].action, null)
    assert.equal(beats[0].caption, 'Check the jig')
    assert.equal(beats[0].why, undefined)
  }
})
