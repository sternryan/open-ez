// Drift guard: each lab test file must be the 2.1 viewer's test file, verbatim, apart from its import lines and blank lines.
// Edit one and this fails until the other matches, so the TypeScript port cannot quietly diverge from the 2.1 behaviour.
// (The three copies are excluded from `tsc` on purpose: they are untyped JavaScript bodies. `tsx` runs them.)
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const here = (p: string) => fileURLToPath(new URL(p, import.meta.url))
const body = (s: string) => s.split('\n').filter((l) => l.trim() !== '' && !/^\s*import\s/.test(l)).join('\n')

for (const n of ['build', 'section', 'tour']) {
  test(`${n}.test.ts is the 2.1 ${n}.test.mjs, verbatim`, () => {
    const old = readFileSync(here(`../../viewer/tests/${n}.test.mjs`), 'utf8')
    const lab = readFileSync(here(`./${n}.test.ts`), 'utf8')
    assert.ok(body(old).length > 200, 'the 2.1 test file read as empty')
    assert.equal(body(lab), body(old))
  })
}
