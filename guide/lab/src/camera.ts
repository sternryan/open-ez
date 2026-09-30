// Adapted from AirsupHQ/airsup-lab src/camera.ts (MIT); see NOTICE.
// Changes: kept the Shot interface, easeInOut and CameraRig; dropped their SHOTS table and room imports (our shots are built at runtime), resolve() takes a shot or a name from a runtime table, added landing() for tests and an optional clampPos hook that keeps scaled shots inside the room.
import * as THREE from 'three'
import type { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export interface Shot {
  pos: [number, number, number]
  target: [number, number, number]
  fov: number
  /** already framed for the screen: do not pull back further */
  noScale?: boolean
}

export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

/** Camera moves between shots along a gentle arc; the user can take over at any time. */
export class CameraRig {
  private from = { pos: new THREE.Vector3(), target: new THREE.Vector3(), fov: 30 }
  private to = { pos: new THREE.Vector3(), target: new THREE.Vector3(), fov: 30 }
  private lift = 0
  private t = 1
  private dur = 1
  flying = false
  lastUser = -1e9
  /** Distance multiplier for tall screens: a portrait phone sees far less width, so shots pull back. */
  scale = 1
  /** Named shots, filled at runtime once the model is placed. */
  shots: Record<string, Shot> = {}
  /** optional: applied to every scaled landing position */
  clampPos?: (v: THREE.Vector3) => void

  private scaled(s: Shot, out: THREE.Vector3) {
    out.set(...s.pos)
    if (this.scale !== 1 && !s.noScale) {
      const t = new THREE.Vector3(...s.target)
      out.sub(t).multiplyScalar(this.scale).add(t)
    }
    this.clampPos?.(out)
    return out
  }

  constructor(private camera: THREE.PerspectiveCamera, private controls: OrbitControls) {
    controls.addEventListener('start', () => {
      this.flying = false
      this.t = 1
      this.lastUser = performance.now()
    })
  }

  resolve(shot: Shot | string): Shot {
    return typeof shot === 'string' ? this.shots[shot] : shot
  }

  /** where a shot puts the camera once the portrait scale is applied (what the rig converges to) */
  landing(shotIn: Shot | string): { pos: THREE.Vector3; target: THREE.Vector3; fov: number } {
    const s = this.resolve(shotIn)
    return { pos: this.scaled(s, new THREE.Vector3()), target: new THREE.Vector3(...s.target), fov: s.fov }
  }

  set(shotIn: Shot | string) {
    const shot = this.resolve(shotIn)
    this.scaled(shot, this.camera.position)
    this.controls.target.set(...shot.target)
    this.camera.fov = shot.fov
    this.camera.updateProjectionMatrix()
    this.controls.update()
    this.flying = false
    this.t = 1
  }

  fly(shot: Shot | string, dur = 1.8, lift = 0) {
    const s = this.resolve(shot)
    this.from.pos.copy(this.camera.position)
    this.from.target.copy(this.controls.target)
    this.from.fov = this.camera.fov
    this.scaled(s, this.to.pos)
    this.to.target.set(...s.target)
    this.to.fov = s.fov
    this.lift = lift
    this.t = 0
    this.dur = dur
    this.flying = true
  }

  update(dt: number) {
    if (!this.flying) return
    this.t = Math.min(1, this.t + dt / this.dur)
    const e = easeInOut(this.t)
    // the eye leads slightly: the camera looks toward where it is going
    const et = easeInOut(Math.min(1, this.t * 1.3))
    const p = new THREE.Vector3().lerpVectors(this.from.pos, this.to.pos, e)
    p.y += Math.sin(Math.PI * e) * this.lift
    this.camera.position.copy(p)
    this.controls.target.lerpVectors(this.from.target, this.to.target, et)
    this.camera.fov = this.from.fov + (this.to.fov - this.from.fov) * e
    this.camera.updateProjectionMatrix()
    if (this.t >= 1) this.flying = false
  }
}
