// Floating cartoon gloves: one pair per person, no bodies, no rigging (spec section 5). Procedural, so no asset ships.
// No WebGL and no DOM in here: the pair is plain three.js geometry and materials, and builds in node for the tests.
import * as THREE from 'three'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { matte } from '../core/materials'

/** The owner's pair is blue; the buddy's, which appears only when two people are needed, is a contrasting orange. */
export const GLOVE_COLORS = { owner: 0x3b6fd8, buddy: 0xe0892f }

/** Overall size of a hand (palm plus fingers is about 15 cm): a little larger than life, so it reads in a whole-part shot. */
const S = 1.0

/**
 * One hand in its own frame: the palm faces -y, the fingers point along -z, the cuff sits at +z. `side` is -1 for the left hand
 * (its thumb is on its +x side) and +1 for the right.
 */
function hand(side: -1 | 1, color: number): THREE.Group {
  const g = new THREE.Group()
  const parts: THREE.BufferGeometry[] = []
  const palm = new THREE.SphereGeometry(1, 12, 8)
  palm.scale(0.042, 0.02, 0.05)
  parts.push(palm)
  // three fingers forward and a thumb out to the side, cartoon style
  const finger = (x: number, len: number, yaw: number, z: number) => {
    const f = new THREE.CapsuleGeometry(0.0125, len, 3, 8)
    f.rotateX(Math.PI / 2) // along z
    f.translate(0, 0, -len / 2)
    f.rotateY(yaw)
    f.translate(x, 0.002, z)
    parts.push(f)
  }
  finger(-0.026, 0.038, 0.05, -0.04)
  finger(0, 0.044, 0, -0.045)
  finger(0.026, 0.038, -0.05, -0.04)
  finger(-side * 0.04, 0.03, -side * 1.0, 0.0) // thumb
  const body = mergeGeometries(parts)!
  const cuff = new THREE.TorusGeometry(0.034, 0.011, 6, 14)
  cuff.scale(1, 0.7, 1)
  cuff.translate(0, 0, 0.055)
  const tint = new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.45).getHex()
  const bodyMesh = new THREE.Mesh(body, matte(color, 0.55, { name: 'glove' }))
  const cuffMesh = new THREE.Mesh(cuff, matte(tint, 0.6, { name: 'glove-cuff' }))
  for (const m of [bodyMesh, cuffMesh]) { m.castShadow = false; m.receiveShadow = false }
  g.add(bodyMesh, cuffMesh)
  g.scale.setScalar(S)
  return g
}

/** A pair of gloves; the children are the hands, named `left` and `right`. */
export function makeGlovePair(who: 'owner' | 'buddy'): THREE.Group {
  const pair = new THREE.Group()
  pair.name = `gloves:${who}`
  const color = GLOVE_COLORS[who]
  const left = hand(-1, color), right = hand(1, color)
  left.name = 'left'
  right.name = 'right'
  pair.add(left, right)
  return pair
}

// ---- grip poses: private animation helpers for main.ts, not a public contract ----

export interface GlovePose {
  /** the action being done (null: caption-only or idle) */
  do: string | null
  /** progress through the beat, 0..1 */
  k: number
  /** sim seconds, for the idle float */
  t: number
  /** world centre and size (metres) of what is being worked on */
  center: THREE.Vector3
  size: THREE.Vector3
  /** horizontal unit vector from the work toward where this person stands */
  side: THREE.Vector3
}

const UP = new THREE.Vector3(0, 1, 0)
const ease = (x: number) => (x < 0.5 ? 2 * x * x : 1 - (-2 * x + 2) ** 2 / 2)
const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : Number.isFinite(x) ? x : 0)

/** Where each hand goes for an action, as offsets in the work's frame: a (across), h (height above the top), r (toward the person). */
function offsets(d: string | null, k: number, t: number, w: number): { l: [number, number, number]; r: [number, number, number]; roll: number } {
  const half = Math.max(0.08, Math.min(w / 2, 0.6))
  const bob = 0.012 * Math.sin(t * 2.4)
  switch (d) {
    case 'place': { const h = 0.12 * (1 - ease(k)) + 0.03; return { l: [-0.14, h, 0.05], r: [0.14, h, 0.05], roll: 0 } }
    case 'drape': { const a = 0.05 + (half - 0.05) * ease(k); const h = 0.16 * (1 - k) + 0.04; return { l: [-a, h, 0.03], r: [a, h, 0.03], roll: 0 } }
    case 'wet-out': { const a = -half * 0.8 + 1.6 * half * k; return { l: [-half * 0.9, 0.04 + bob, 0.18], r: [a, 0.05 + 0.03 * Math.abs(Math.sin(k * Math.PI * 6)), 0.05], roll: 0.3 } }
    case 'squeegee': { const a = half * 0.8 * Math.sin(k * Math.PI * 4); return { l: [-half * 0.9, 0.04 + bob, 0.18], r: [a, 0.035, 0.04], roll: 0.15 } }
    case 'cut': { const a = -half * 0.8 + 1.6 * half * k; return { l: [-half * 0.9, 0.035, 0.12], r: [a, 0.05, 0.0], roll: 0.4 + 0.25 * Math.sin(k * Math.PI * 10) } }
    case 'sand': { const a = 0.06 * Math.sin(k * Math.PI * 16); return { l: [-0.18, 0.04 + bob, 0.15], r: [a, 0.035, 0.03], roll: 0 } }
    case 'flip': { const h = 0.05 + 0.22 * Math.sin(Math.PI * k); return { l: [-half * 0.8, h, 0.0], r: [half * 0.8, h, 0.0], roll: Math.PI * k } }
    case 'check-level': return { l: [-0.12, 0.05 + bob, 0.06], r: [0.04, 0.05, 0.02], roll: 0 }
    case 'check-string': { const a = -half * 0.6 + 1.2 * half * k; return { l: [-half * 0.9, 0.05 + bob, 0.1], r: [a, 0.06, 0.0], roll: 0 } }
    case 'bond': { const h = 0.03 + 0.05 * (1 - ease(Math.min(1, k * 1.6))); return { l: [-0.1, h, 0.04], r: [0.1, h, 0.04], roll: 0 } }
    default: return { l: [-0.16, 0.14 + bob, 0.22], r: [0.16, 0.14 - bob, 0.22], roll: 0 } // idle: waiting, a little above and in front
  }
}

const m4 = new THREE.Matrix4(), across = new THREE.Vector3(), toward = new THREE.Vector3(), base = new THREE.Vector3()

/** Put both hands of a pair where an action has them at progress k. Palms face down, fingers point at the work. */
export function poseGlovePair(pair: THREE.Object3D, p: GlovePose): void {
  const k = clamp01(p.k)
  toward.copy(p.side).setY(0)
  if (toward.lengthSq() < 1e-9) toward.set(0, 0, 1)
  toward.normalize()
  across.crossVectors(UP, toward).normalize() // to the person's right as they face the work; (across, up, toward) is right-handed
  const w = Math.abs(p.size.x * across.x) + Math.abs(p.size.z * across.z)
  const reach = Math.abs(p.size.x * toward.x) + Math.abs(p.size.z * toward.z)
  const o = offsets(p.do, k, Number.isFinite(p.t) ? p.t : 0, w)
  // the hands work over the top of the part, a little in from the person's side of its middle
  base.copy(p.center).addScaledVector(UP, p.size.y / 2).addScaledVector(toward, Math.min(reach / 2, 0.3) * 0.35)
  m4.makeBasis(across, UP, toward) // local x across, y up, z toward the person: fingers (-z) point at the work
  for (const name of ['left', 'right'] as const) {
    const h = pair.getObjectByName(name)
    if (!h) continue
    const [a, up, r] = name === 'left' ? o.l : o.r
    h.position.copy(base).addScaledVector(across, a).addScaledVector(UP, up).addScaledVector(toward, r)
    h.quaternion.setFromRotationMatrix(m4)
    if (o.roll) h.rotateZ(name === 'left' ? -o.roll * 0.3 : o.roll)
  }
  pair.updateMatrixWorld(true)
}
