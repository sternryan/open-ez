import * as THREE from 'three'

/**
 * A warm workshop, baked to a PMREM environment map: a dim wood-and-plaster dome, long overhead
 * fluorescent-style strips, a window-like side panel and a low floor bounce. Only used for image-based light and reflections.
 */
export function workshopEnvironment(renderer: THREE.WebGLRenderer): THREE.Texture {
  const s = new THREE.Scene()

  const grad = document.createElement('canvas')
  grad.width = 4
  grad.height = 256
  const g = grad.getContext('2d')!
  const lg = g.createLinearGradient(0, 0, 0, 256)
  lg.addColorStop(0, '#5a5148') // ceiling
  lg.addColorStop(0.45, '#3b322a') // walls
  lg.addColorStop(0.55, '#2a221b')
  lg.addColorStop(1, '#1a1410') // floor
  g.fillStyle = lg
  g.fillRect(0, 0, 4, 256)
  const gt = new THREE.CanvasTexture(grad)
  gt.colorSpace = THREE.SRGBColorSpace
  s.add(new THREE.Mesh(new THREE.SphereGeometry(30, 32, 16), new THREE.MeshBasicMaterial({ map: gt, side: THREE.BackSide })))

  const sb = document.createElement('canvas')
  sb.width = sb.height = 128
  const c = sb.getContext('2d')!
  const rg = c.createRadialGradient(64, 64, 8, 64, 64, 64)
  rg.addColorStop(0, '#ffffff')
  rg.addColorStop(0.6, '#eeeeee')
  rg.addColorStop(1, '#000000')
  c.fillStyle = rg
  c.fillRect(0, 0, 128, 128)
  const st = new THREE.CanvasTexture(sb)

  const panel = (w: number, h: number, p: [number, number, number], look: [number, number, number], color: number, k: number) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: st, color: new THREE.Color(color).multiplyScalar(k), side: THREE.DoubleSide }))
    m.position.set(...p)
    m.lookAt(...look)
    s.add(m)
  }
  // three long tube fixtures overhead, running along the shop
  for (const z of [-3.2, 0, 3.2]) panel(14, 0.9, [0, 8, z], [0, 0, z], 0xfff0dc, 7.0)
  panel(3, 9, [-10, 3.5, -1], [0, 1.5, 0], 0xffe2bd, 2.6) // warm window light
  panel(16, 1.2, [0, 3.2, 9], [0, 1.0, 0], 0xf2f4ff, 1.6) // long front strip
  panel(12, 1.4, [0, 4.5, -9], [0, 1.2, 0], 0xb9cfff, 1.5) // cool back rim
  panel(12, 12, [0, -3, 0], [0, 1, 0], 0x4a3a2c, 0.8) // floor bounce

  const pm = new THREE.PMREMGenerator(renderer)
  const tex = pm.fromScene(s, 0.02).texture
  pm.dispose()
  return tex
}
