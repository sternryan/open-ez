import * as THREE from 'three'
import { FIXTURES, FIXTURE_LEN, FIXTURE_Y, ROOM, WINDOW } from './workshop'

/**
 * The shop, baked to a PMREM environment map for image-based light and reflections. It is the same room the scene draws
 * (same walls, fixture and window positions), seen from table height, so a glossy ply reflects the tubes and the window
 * that are really overhead.
 */
export function workshopEnvironment(renderer: THREE.WebGLRenderer): THREE.Texture {
  const s = new THREE.Scene()
  const Y0 = 1.0 // eye height the map is captured from; the room is shifted down by this
  const R = ROOM
  const mat = (hex: number, k = 1) => new THREE.MeshBasicMaterial({ color: new THREE.Color(hex).multiplyScalar(k), side: THREE.BackSide })
  // room shell: one BackSide box per surface group so floor, walls and ceiling get their own tone
  const wallsMat = [mat(0x6f747b), mat(0x6f747b), mat(0x40454b), mat(0x77736c, 0.85), mat(0x6f747b), mat(0x6f747b)] // +x -x +y(ceiling) -y(floor) +z -z
  const shell = new THREE.Mesh(new THREE.BoxGeometry(R.x1 - R.x0, R.h, R.z1 - R.z0), wallsMat)
  shell.position.set((R.x0 + R.x1) / 2, R.h / 2 - Y0, (R.z0 + R.z1) / 2)
  s.add(shell)
  const glow = (hex: number, k: number) => new THREE.MeshBasicMaterial({ color: new THREE.Color(hex).multiplyScalar(k) })
  for (const f of FIXTURES) {
    const t = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.03, FIXTURE_LEN), glow(0xfff0dc, 9))
    t.position.set(f.x, FIXTURE_Y - Y0, f.z)
    s.add(t)
  }
  const w = new THREE.Mesh(new THREE.BoxGeometry(WINDOW.w, WINDOW.h, 0.05), glow(0xd2e6ff, 4.5))
  w.position.set(WINDOW.x, WINDOW.y - Y0, WINDOW.z + 0.05)
  s.add(w)
  const strip = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, 1.6), glow(0x2ee6c8, 2.5))
  strip.position.set(R.x1 - 0.3, 1.6 - Y0, -2.95)
  s.add(strip)

  const pm = new THREE.PMREMGenerator(renderer)
  const tex = pm.fromScene(s, 0.03).texture
  pm.dispose()
  return tex
}
