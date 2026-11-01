import test from 'node:test'
import assert from 'node:assert/strict'
import { evidenceOf } from '../src/logic/evidence'

test('a sourced flag shows with its evidence: the citation, the derivation note, or the community link', () => {
  assert.deepEqual(evidenceOf('official', 'plans-1980:p34'), { flag: 'official', kind: 'cite', text: 'plans-1980:p34' })
  assert.deepEqual(evidenceOf('derived', '2 plies x 0.6 sq yd per ply, from the p34 sketch'), { flag: 'derived', kind: 'note', text: '2 plies x 0.6 sq yd per ply, from the p34 sketch' })
  assert.deepEqual(evidenceOf('community', 'https://example.org/thread/1'), { flag: 'community', kind: 'link', text: 'https://example.org/thread/1' })
})

test('a flag that claims a source but has no evidence on record shows as an estimate', () => {
  for (const flag of ['official', 'derived', 'community']) {
    for (const source of [undefined, null, '', '   ']) {
      assert.deepEqual(evidenceOf(flag, source), { flag: 'estimate', kind: null, text: null }, `${flag} ${JSON.stringify(source)}`)
    }
  }
  // a community "source" that is not a link is no evidence either
  assert.deepEqual(evidenceOf('community', 'a forum post somewhere'), { flag: 'estimate', kind: null, text: null })
  assert.deepEqual(evidenceOf('community', 'javascript:alert(1)'), { flag: 'estimate', kind: null, text: null })
})

test('estimate and unsourced stay what they are, with no evidence', () => {
  assert.deepEqual(evidenceOf('estimate', null), { flag: 'estimate', kind: null, text: null })
  assert.deepEqual(evidenceOf('estimate', 'stray note'), { flag: 'estimate', kind: null, text: null })
  assert.deepEqual(evidenceOf('unsourced', null), { flag: 'unsourced', kind: null, text: null })
})
