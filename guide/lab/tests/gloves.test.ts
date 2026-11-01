import test from 'node:test'
import assert from 'node:assert/strict'
import * as THREE from 'three'
import { GLOVE_COLORS, makeGlovePair, poseGlovePair } from '../src/scene/gloves'
import { makeProp } from '../src/scene/props'
import type { PropId } from '../src/logic/actions'

const PROPS: PropId[] = ['squeegee', 'brush', 'scissors', 'hot-wire', 'level', 'sanding-block', 'cup', 'peel-ply', 'string-line', 'stand-in']

const triangles = (o: THREE.Object3D): number => {
  let n = 0
  o.traverse((x) => {
    const m = x as THREE.Mesh
    if (!m.isMesh) return
    const g = m.geometry
    n += (g.index ? g.index.count : g.attributes.position.count) / 3
  })
  return n
}
const colors = (o: THREE.Object3D): Set<number> => {
  const s = new Set<number>()
  o.traverse((x) => {
    const m = x as THREE.Mesh
    if (m.isMesh) s.add((m.material as THREE.MeshStandardMaterial).color.getHex())
  })
  return s
}

test('a glove pair has a left and a right hand, built without WebGL', () => {
  for (const who of ['owner', 'buddy'] as const) {
    const pair = makeGlovePair(who)
    assert.deepEqual(pair.children.map((c) => c.name).sort(), ['left', 'right'])
    let meshes = 0
    pair.traverse((x) => { if ((x as THREE.Mesh).isMesh) meshes++ })
    assert.ok(meshes >= 2, `${who}: ${meshes} meshes`)
    const box = new THREE.Box3().setFromObject(pair)
    assert.ok(!box.isEmpty())
  }
})

test('each pair stays within 4,000 triangles', () => {
  for (const who of ['owner', 'buddy'] as const) {
    const n = triangles(makeGlovePair(who))
    assert.ok(n > 100 && n <= 4000, `${who}: ${n} triangles`)
  }
})

test('the two pairs are in contrasting colours', () => {
  assert.notEqual(GLOVE_COLORS.owner, GLOVE_COLORS.buddy)
  const o = colors(makeGlovePair('owner')), b = colors(makeGlovePair('buddy'))
  assert.ok(o.has(GLOVE_COLORS.owner), [...o].map((c) => c.toString(16)).join())
  assert.ok(b.has(GLOVE_COLORS.buddy), [...b].map((c) => c.toString(16)).join())
  const hue = (c: number) => { const h = { h: 0, s: 0, l: 0 }; new THREE.Color(c).getHSL(h); return h.h }
  const d = Math.abs(hue(GLOVE_COLORS.owner) - hue(GLOVE_COLORS.buddy))
  assert.ok(Math.min(d, 1 - d) > 0.25, `hue gap ${d}`)
})

test('every prop builds headless with geometry and says what it is', () => {
  for (const id of PROPS) {
    const p = makeProp(id)
    assert.equal(p.userData.prop, id)
    const n = triangles(p)
    assert.ok(n > 0 && n <= 1500, `${id}: ${n} triangles`)
    assert.ok(!new THREE.Box3().setFromObject(p).isEmpty(), id)
  }
})

test('the stand-in carries its label', () => {
  assert.equal(makeProp('stand-in', 'gear tube jig').userData.label, 'gear tube jig')
  assert.equal(makeProp('stand-in').userData.label, 'stand-in')
})

test('posing moves the hands and never produces NaN', () => {
  const pair = makeGlovePair('owner')
  const center = new THREE.Vector3(1, 1, 1), size = new THREE.Vector3(0.6, 0.1, 0.4), side = new THREE.Vector3(0, 0, 1)
  const at = (d: string | null, k: number) => {
    poseGlovePair(pair, { do: d, k, t: 0.5, center, size, side })
    pair.updateMatrixWorld(true)
    return pair.getObjectByName('right')!.getWorldPosition(new THREE.Vector3())
  }
  for (const d of [null, 'place', 'wet-out', 'squeegee', 'drape', 'cut', 'flip', 'sand', 'check-level', 'check-string', 'bond', 'wait-cure', 'unknown']) {
    for (const k of [0, 0.5, 1]) {
      const p = at(d, k)
      assert.ok([p.x, p.y, p.z].every(Number.isFinite), `${d} ${k}`)
      assert.ok(p.y > center.y, `${d} ${k}: hands stay above the work (${p.y})`)
    }
  }
  assert.ok(at('squeegee', 0.125).distanceTo(at('squeegee', 0.375)) > 0.05, 'a squeegee stroke moves the hand')
})
