// The tool props the gloves hold (spec section 5): simple procedural shapes, no assets. No WebGL and no DOM here.
// Each prop is built in its grip frame: the hand holds it at the origin, the working end points along -z (toward the work)
// and down (-y), so a glove's pose carries it without per-tool fixups.
import * as THREE from 'three'
import { matte } from '../core/materials'
import type { PropId } from '../logic/actions'

export type { PropId }

const C = {
  handle: 0x8a5a32, // wood
  plastic: 0xd7d2c4,
  yellow: 0xf0c419,
  steel: 0xb8bdc2,
  red: 0xc23b2e,
  dark: 0x3a3632,
  cloth: 0xf1efe8,
  standIn: 0xa7b0b8,
}

/** Props are drawn half again life size, like the gloves' cartoon proportions, so a tool reads in a whole-part shot. */
const PROP_SCALE = 1.5

const mesh = (g: THREE.BufferGeometry, color: number, at: [number, number, number] = [0, 0, 0], name = 'prop-part'): THREE.Mesh => {
  const m = new THREE.Mesh(g, matte(color, 0.6, { name }))
  m.position.set(...at)
  m.castShadow = false
  m.receiveShadow = false
  return m
}
const box = (x: number, y: number, z: number) => new THREE.BoxGeometry(x, y, z)
const cyl = (r: number, h: number, seg = 10, open = false) => new THREE.CylinderGeometry(r, r, h, seg, 1, open)
/** a cylinder lying along z */
const rod = (r: number, len: number, seg = 8) => cyl(r, len, seg).rotateX(Math.PI / 2)

/** A tool prop. `stand-in` is a plain labelled box for steps whose jig or fixture has no geometry (spec section 12). */
export function makeProp(id: PropId, label?: string): THREE.Object3D {
  const g = new THREE.Group()
  g.name = `prop:${id}`
  g.userData.prop = id
  switch (id) {
    case 'squeegee': // a flexible plastic blade, held on edge
      g.add(mesh(box(0.11, 0.06, 0.004), C.yellow, [0, -0.035, -0.02]))
      break
    case 'brush': // a short chip brush
      g.add(mesh(rod(0.007, 0.1), C.handle, [0, 0, 0.02]))
      g.add(mesh(box(0.04, 0.008, 0.035), C.steel, [0, 0, -0.045]))
      g.add(mesh(box(0.038, 0.006, 0.03), C.cloth, [0, -0.002, -0.075]))
      break
    case 'scissors': {
      const a = mesh(box(0.008, 0.003, 0.09), C.steel, [0.004, 0, -0.05]); a.rotation.y = 0.12
      const b = mesh(box(0.008, 0.003, 0.09), C.steel, [-0.004, 0, -0.05]); b.rotation.y = -0.12
      g.add(a, b)
      for (const x of [-0.016, 0.016]) { const r = mesh(new THREE.TorusGeometry(0.012, 0.003, 5, 10), C.red, [x, 0, 0.012]); r.rotation.x = Math.PI / 2; g.add(r) }
      break
    }
    case 'hot-wire': // a bow with a wire across its open end
      g.add(mesh(rod(0.008, 0.12), C.handle, [0, 0.03, 0.02]))
      for (const x of [-0.12, 0.12]) g.add(mesh(cyl(0.005, 0.12, 6), C.steel, [x, -0.03, -0.04]))
      g.add(mesh(cyl(0.005, 0.24, 6).rotateZ(Math.PI / 2), C.steel, [0, 0.03, -0.04]))
      g.add(mesh(cyl(0.0012, 0.24, 4).rotateZ(Math.PI / 2), C.red, [0, -0.09, -0.04]))
      break
    case 'level': // a bar level with its vial
      g.add(mesh(box(0.3, 0.025, 0.02), C.yellow, [0, -0.02, -0.03]))
      g.add(mesh(cyl(0.006, 0.04, 8).rotateZ(Math.PI / 2), 0x6fd06f, [0, -0.004, -0.03]))
      break
    case 'sanding-block':
      g.add(mesh(box(0.1, 0.03, 0.06), C.handle, [0, -0.02, -0.02]))
      g.add(mesh(box(0.1, 0.004, 0.06), C.dark, [0, -0.037, -0.02]))
      break
    case 'cup': // a mixing cup with a stir stick
      g.add(mesh(cyl(0.032, 0.07, 14, true), C.plastic, [0, -0.04, -0.03]))
      g.add(mesh(cyl(0.032, 0.002, 14), C.plastic, [0, -0.075, -0.03]))
      g.add(mesh(box(0.006, 0.12, 0.002), C.handle, [0.01, -0.02, -0.03]))
      break
    case 'peel-ply': // a roll with a sheet coming off it
      g.add(mesh(cyl(0.025, 0.2, 12).rotateZ(Math.PI / 2), C.cloth, [0, -0.02, -0.02]))
      g.add(mesh(box(0.19, 0.001, 0.12), C.cloth, [0, -0.045, -0.09]))
      break
    case 'string-line': // two stakes and a taut line between them
      for (const x of [-0.3, 0.3]) g.add(mesh(cyl(0.006, 0.08, 6), C.handle, [x, -0.04, -0.04]))
      g.add(mesh(cyl(0.001, 0.6, 4).rotateZ(Math.PI / 2), C.red, [0, -0.01, -0.04]))
      break
    case 'stand-in':
      g.add(mesh(box(0.16, 0.08, 0.1), C.standIn, [0, -0.06, -0.06], 'stand-in'))
      g.userData.label = label ?? 'stand-in'
      break
  }
  g.scale.setScalar(PROP_SCALE)
  return g
}
