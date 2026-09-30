import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { Pipeline } from './render/pipeline'
import { makeNoise3D, NOISE3D } from './core/noise'
import { CutState } from './core/cut'
import { surf } from './core/materials'
import { workshopEnvironment } from './scene/env'
import { buildWorkshop, ROOM, TABLE_TOP_Y } from './scene/workshop'
import { orientation, type Pose } from './logic/pose'
import { labShots, LAB_FOV, type LabShot } from './shots'
import { CameraRig, easeInOut, type Shot } from './camera'
import { barOps, makeStore, type GraphLite, type Variant } from './logic/graph'
import { initUI } from './ui/ui'
import './style.css'

const INCH = 0.0254
const params = new URLSearchParams(location.search)
const TEST = params.get('test') === '1'
const statusEl = document.getElementById('status') as HTMLElement
const setStatus = (msg: string | null, err = false) => {
  statusEl.hidden = msg === null
  statusEl.textContent = msg ?? ''
  statusEl.classList.toggle('err', err)
}

interface Graph extends GraphLite { components: Record<string, unknown>; layup?: { nodes?: Record<string, { cloth?: string }> } | null }
interface Cfg { model: string }
interface CamState { pos: number[]; target: number[]; fov: number }
interface LabHook {
  ready: boolean; meshNames(): string[]; stats(): { calls: number; triangles: number }; advance(seconds: number): void
  selected(): string | null; select(opId: string | null): void; camera(): CamState; shot(name: string): CamState | null; flying(): boolean
  /** the pose the canard is in, or is turning to */
  pose(): Pose; flipping(): boolean; tableTopY(): number
  /** authored lab shots, model inches in the canard's frame (target is the tours.yaml target) */
  labShots(): Record<string, LabShot>
}
declare global { interface Window { __lab?: LabHook } }

const hook: LabHook = {
  ready: false, meshNames: () => [], stats: () => ({ calls: 0, triangles: 0 }), advance: () => {},
  selected: () => null, select: () => {}, camera: () => ({ pos: [0, 0, 0], target: [0, 0, 0], fov: 0 }), shot: () => null, flying: () => false,
  pose: () => 'upright', flipping: () => false, tableTopY: () => TABLE_TOP_Y, labShots: () => ({}),
}
if (TEST) window.__lab = hook

// The export has one mesh per face (~1,800). They are static, so bake each mesh's world transform and merge everything that
// shares a ply node (or, for parts without plies, a component) into one mesh. Same logic as the 2.1 viewer.
function bake(o: THREE.Mesh, flip: boolean): THREE.BufferGeometry {
  const g = o.geometry.clone().applyMatrix4(o.matrixWorld)
  const pos = g.attributes.position, nor = g.attributes.normal
  const out = new THREE.BufferGeometry()
  const P = new Float32Array(pos.count * 3), N = new Float32Array(pos.count * 3)
  for (let i = 0; i < pos.count; i++) {
    P.set([pos.getX(i), pos.getY(i), pos.getZ(i)], i * 3)
    if (nor) N.set([nor.getX(i), nor.getY(i), nor.getZ(i)], i * 3)
  }
  const idx = g.index ? Array.from(g.index.array) : Array.from({ length: pos.count }, (_, i) => i)
  if (flip) for (let i = 0; i < idx.length; i += 3) [idx[i + 1], idx[i + 2]] = [idx[i + 2], idx[i + 1]] // a mirroring transform reverses winding
  out.setAttribute('position', new THREE.BufferAttribute(P, 3))
  out.setIndex(idx)
  if (nor) out.setAttribute('normal', new THREE.BufferAttribute(N, 3)); else out.computeVertexNormals()
  return out
}

interface Merged { cid: string; node: string | null; mesh: THREE.Mesh }

function mergeModel(scene: THREE.Object3D, graph: Graph): { cid: string; node: string | null; geo: THREE.BufferGeometry }[] {
  scene.updateMatrixWorld(true)
  const groups = new Map<string, { cid: string; node: string | null; geos: THREE.BufferGeometry[] }>()
  // GLTFLoader strips dots from node names (canard.core -> canardcore); the original is kept in userData.name.
  const nm = (x: THREE.Object3D): string => (x.userData?.name as string | undefined) ?? x.name
  scene.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    let n: THREE.Object3D = o
    while (n && !graph.components[nm(n)] && n.parent) n = n.parent
    const cid = graph.components[nm(n)] ? nm(n) : nm(o)
    let q: THREE.Object3D = o
    while (q && !/\.p\d+$/.test(nm(q)) && q.parent) q = q.parent
    const node = q && /\.p\d+$/.test(nm(q)) ? nm(q) : null
    const key = `${cid}|${node ?? ''}`
    if (!groups.has(key)) groups.set(key, { cid, node, geos: [] })
    groups.get(key)!.geos.push(bake(mesh, mesh.matrixWorld.determinant() < 0))
  })
  const out = []
  for (const g of groups.values()) {
    const geo = g.geos.length === 1 ? g.geos[0] : mergeGeometries(g.geos)
    if (!geo) throw new Error(`could not merge ${g.node ?? g.cid}`)
    out.push({ cid: g.cid, node: g.node, geo })
  }
  return out
}

/** Distance along `dir` from `target` at which the box spans `fill` of the frame width, as a Shot. */
function fitShot(box: THREE.Box3, target: THREE.Vector3, dir: THREE.Vector3, fovDeg: number, aspect: number, fill: number): Shot {
  const cam = new THREE.PerspectiveCamera(fovDeg, aspect, 0.05, 90)
  const pts: THREE.Vector3[] = []
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) pts.push(new THREE.Vector3(x, y, z))
  const spread = (d: number) => {
    cam.position.copy(target).addScaledVector(dir, d)
    cam.lookAt(target)
    cam.updateMatrixWorld(true)
    cam.updateProjectionMatrix()
    let lo = 1e9, hi = -1e9
    for (const p of pts) { const x = p.clone().project(cam).x; lo = Math.min(lo, x); hi = Math.max(hi, x) }
    return (hi - lo) / 2
  }
  let a = 0.5, b = 12
  for (let i = 0; i < 40; i++) { const m = (a + b) / 2; if (spread(m) > fill) a = m; else b = m }
  const d = (a + b) / 2
  const p = target.clone().addScaledVector(dir, d)
  return { pos: [p.x, p.y, p.z], target: target.toArray() as [number, number, number], fov: fovDeg }
}

async function boot() {
  NOISE3D.value = makeNoise3D(64)
  const canvas = document.getElementById('gl') as HTMLCanvasElement
  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: 'high-performance', stencil: false })
  } catch {
    setStatus('This page needs WebGL 2. Try a recent Chrome, Safari or Firefox.', true)
    return
  }
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.NoToneMapping
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  renderer.shadowMap.autoUpdate = false
  renderer.localClippingEnabled = true
  renderer.info.autoReset = false // count the whole frame (every pipeline pass), not just the last render call

  const coarse = matchMedia('(pointer: coarse)').matches
  const q = params.get('q') || (coarse ? 'mid' : 'high')
  const quality = q === 'low' || q === 'mid' ? q : 'high'

  const scene = new THREE.Scene()
  scene.background = null // a colour background would force-clear on every render() call
  scene.environment = workshopEnvironment(renderer)
  scene.environmentIntensity = 1.5

  // ---- lights: a warm key from the overhead fixtures (one shadowed spot over the table), a cool low fill, the room env for the rest ----
  const key = new THREE.SpotLight(0xffe6c8, 21, 0, 0.5, 1, 2)
  key.position.set(-0.7, ROOM.h - 0.35, 0.5)
  key.castShadow = true
  const sm = quality === 'low' ? 1024 : quality === 'mid' ? 2048 : 4096
  key.shadow.mapSize.set(sm, sm)
  key.shadow.camera.near = 0.5
  key.shadow.camera.far = 6
  key.shadow.bias = -0.0008
  key.shadow.normalBias = 0.03
  key.shadow.radius = 4
  scene.add(key, key.target)
  const fill = new THREE.DirectionalLight(0xb9cfff, 0.9)
  fill.position.set(-3, 1.6, 2.4)
  scene.add(fill)

  // ---- camera ----
  const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.05, 90)
  camera.position.set(-3.4, 1.9, 2.6)
  const controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true
  controls.dampingFactor = 0.075
  controls.minDistance = 0.4
  controls.maxDistance = 7.5
  controls.maxPolarAngle = Math.PI * 0.495 // never orbit under the floor: the target sits at table height, so the eye stays above it
  controls.rotateSpeed = 0.7

  const rig = new CameraRig(camera, controls)

  const pipeline = new Pipeline(renderer, { ao: quality !== 'low', msaa: quality === 'low' ? 0 : 4, aoSamples: 8 })
  pipeline.aoScale = 0.5
  pipeline.params.ao = 0.55
  pipeline.params.dofTaps = 14
  pipeline.params.sharpen = 0.25
  pipeline.params.bloom = 0.12
  const dofOn = quality === 'high'

  const resize = () => {
    const W = window.innerWidth, H = window.innerHeight
    const dpr = Math.min(window.devicePixelRatio || 1, quality === 'low' ? 1 : 1.75)
    renderer.setPixelRatio(dpr)
    renderer.setSize(W, H, false)
    camera.aspect = W / H
    camera.updateProjectionMatrix()
    pipeline.setSize(Math.round(W * dpr), Math.round(H * dpr))
    // Portrait screens see far less width: pull every shot back, as airsup does.
    rig.scale = camera.aspect >= 1 ? Math.max(1, 1.6 / camera.aspect) : Math.min(3.2, (1.6 / camera.aspect) * 0.82)
    if (rig.lastUser < 0 && !rig.flying && currentShot) rig.set(currentShot) // the user has not touched the camera: keep the framing
  }
  let currentShot: string | null = null
  // keep every landing spot inside the room, whatever the portrait pull-back does
  rig.clampPos = (v) => { v.x = THREE.MathUtils.clamp(v.x, ROOM.x0 + 0.4, ROOM.x1 - 0.5); v.z = THREE.MathUtils.clamp(v.z, ROOM.z0 + 0.5, ROOM.z1 - 0.4); v.y = THREE.MathUtils.clamp(v.y, 0.25, ROOM.h - 0.45) }
  window.addEventListener('resize', resize)
  resize()

  // ---- deterministic time ----
  let simT = 0
  let stepPose: (dt: number) => void = () => {}
  const step = (dt: number) => {
    simT += dt
    stepPose(dt)
    rig.update(dt)
    controls.update()
  }
  const render = () => {
    pipeline.params.dofFocus = camera.position.distanceTo(controls.target)
    pipeline.params.dofAperture = dofOn ? 9 : 0
    renderer.info.reset()
    pipeline.render(scene, camera, simT)
  }
  let last = performance.now()
  renderer.setAnimationLoop(() => {
    const t = performance.now(), dt = Math.min((t - last) / 1000, 0.1)
    last = t
    step(dt)
    render()
  })
  hook.advance = (s: number) => { step(s); render() }
  hook.stats = () => ({ calls: renderer.info.render.calls, triangles: renderer.info.render.triangles })

  // ---- data + model ----
  const merged: Merged[] = []
  // canardRoot carries the pose (right side up, or inverted in the jig) and everything that must follow the canard: the meshes,
  // the section cut's owner and, in later tasks, load paths and labels. Its origin is the canard's box centre, in metres.
  const canardRoot = new THREE.Group()
  canardRoot.name = 'canardRoot'
  scene.add(canardRoot)
  const root = new THREE.Group() // the model frame: inches, as exported
  root.scale.setScalar(INCH)
  canardRoot.add(root)
  hook.meshNames = () => merged.map((m) => m.node ?? m.cid)
  try {
    const [graph, cfg] = await Promise.all([
      fetch('../graph.json').then((r) => { if (!r.ok) throw new Error(`graph.json ${r.status}`); return r.json() as Promise<Graph> }),
      fetch('../config.json').then((r) => { if (!r.ok) throw new Error(`config.json ${r.status}`); return r.json() as Promise<Cfg> }),
    ])
    const gltf = await new GLTFLoader().loadAsync('../' + cfg.model)
    const parts = mergeModel(gltf.scene, graph)
    // Placeholder materials by cloth; Task 2 replaces these with real ones.
    const cut = new CutState(root, 80, -80)
    cut.amount = 0
    const cloth = (node: string | null) => (node ? graph.layup?.nodes?.[node]?.cloth : undefined)
    const paint = (node: string | null) => {
      const c = cloth(node)
      if (!node) return { color: 0xe6dfcf, roughness: 0.85 } // foam-ish off-white
      if (c === 'BID') return { color: 0x5f8489, roughness: 0.42 } // teal-grey
      return { color: 0xc99a5b, roughness: 0.42 } // amber-tan
    }
    for (const p of parts) {
      const o = paint(p.node)
      const mesh = new THREE.Mesh(p.geo, surf({ ...o, metalness: 0, detail: 1.2, colorVar: 0.06, roughVar: 0.2, cut, capColor: o.color }))
      mesh.name = p.node ?? p.cid
      mesh.castShadow = true
      mesh.receiveShadow = true
      root.add(mesh)
      merged.push({ cid: p.cid, node: p.node, mesh })
    }
    cut.collect(root)
    cut.update()

    // ---- the shop: sized from the model's own box, the canard laid on its jig blocks ----
    root.updateMatrixWorld(true)
    const box = new THREE.Box3().setFromObject(root)
    const c = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())
    const shop = buildWorkshop(size.z, size.x)
    scene.add(shop.group)
    root.position.copy(c).multiplyScalar(-1) // canardRoot's origin is the box centre
    const restY = shop.jigTopY + size.y / 2 + 0.001
    const halfW = size.x / 2, halfH = size.y / 2

    // ---- pose: upright, or inverted (rotated half a turn about the span axis, Z) with its top surface on the jig blocks ----
    // The box is symmetric about its centre, so both poses rest at the same height. A flip turns about the span axis and lifts
    // just enough that no corner of the box goes through the blocks.
    const FLIP_SECONDS = 1.2
    const angleOf = (p: Pose) => (p === 'inverted' ? Math.PI : 0)
    let pose: Pose = 'upright'
    let flipFrom = 0, flipTo = 0, flipT = 1
    const applyPose = (angle: number, e: number) => {
      const s = Math.abs(Math.sin(angle)), k = Math.abs(Math.cos(angle))
      canardRoot.rotation.set(0, 0, angle)
      canardRoot.position.set(0, restY + (halfW * s + halfH * k - halfH) + 0.03 * Math.sin(Math.PI * e), 0)
      canardRoot.updateMatrixWorld(true)
    }
    applyPose(0, 0)
    stepPose = (dt) => {
      if (flipT >= 1) return
      flipT = Math.min(1, flipT + dt / FLIP_SECONDS)
      const e = easeInOut(flipT)
      applyPose(flipFrom + (flipTo - flipFrom) * e, e)
      pipeline.shadowDirty = true
    }
    const setPose = (p: Pose, animate: boolean) => {
      if (p === pose && flipT >= 1) return
      const cur = flipT >= 1 ? angleOf(pose) : flipFrom + (flipTo - flipFrom) * easeInOut(flipT)
      pose = p
      flipFrom = cur
      flipTo = angleOf(p)
      flipT = animate ? 0 : 1
      applyPose(animate ? flipFrom : flipTo, 0)
      pipeline.shadowDirty = true
    }
    /** model inches -> world metres, with the canard in pose `p` (rest height, no lift) */
    const modelToWorld = (p: Pose): THREE.Matrix4 => {
      const m = new THREE.Matrix4().compose(new THREE.Vector3(0, restY, 0), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), angleOf(p)), new THREE.Vector3(1, 1, 1))
      return m.multiply(new THREE.Matrix4().compose(root.position.clone(), new THREE.Quaternion(), new THREE.Vector3(INCH, INCH, INCH)))
    }
    const cb = new THREE.Box3().setFromObject(root)
    const centre = cb.getCenter(new THREE.Vector3())
    key.target.position.copy(centre)
    key.target.updateMatrixWorld()
    pipeline.shadowDirty = true

    // ---- shots: home is fitted to the canard's box; each op's lab shot is authored in the canard's frame (src/shots.ts) and
    // carried through the pose the canard will be in for that op ----
    const homeTarget = centre.clone().add(new THREE.Vector3(0, -0.06, 0))
    rig.shots.home = fitShot(cb, homeTarget, new THREE.Vector3(-0.66, 0.26, 0.7).normalize(), 30, 1.6, 0.7)
    let lab: Record<string, LabShot> = {}
    const buildShots = (v: Variant) => {
      lab = labShots(graph.tours ?? {}, (id) => orientation(graph, v, id))
      for (const id of Object.keys(rig.shots)) if (id !== 'home') delete rig.shots[id]
      for (const [id, ls] of Object.entries(lab)) {
        const m = modelToWorld(orientation(graph, v, id))
        const tgt = new THREE.Vector3(...ls.target).applyMatrix4(m), pos = new THREE.Vector3(...ls.position).applyMatrix4(m)
        rig.shots[id] = { pos: [pos.x, pos.y, pos.z], target: [tgt.x, tgt.y, tgt.z], fov: LAB_FOV }
      }
    }
    const snap = (name: string): CamState | null => {
      if (!rig.shots[name]) return null
      const l = rig.landing(name)
      return { pos: l.pos.toArray(), target: l.target.toArray(), fov: l.fov }
    }

    // ---- UI ----
    let storage: Storage | null = null
    try { storage = window.localStorage } catch { storage = null } // some browsers throw on access
    const store = makeStore(storage ?? { getItem: () => null, setItem: () => {} })
    let variant: Variant = 'roncz'
    let selected: string | null = null
    const goto = (shot: string, fly: boolean) => {
      currentShot = shot
      if (fly) rig.fly(shot, 1.8, 0.05); else rig.set(shot)
    }
    buildShots(variant)
    const select = (id: string | null, fly = true) => {
      selected = id
      ui.setSelected(id)
      setPose(orientation(graph, variant, id), fly)
      goto(id && rig.shots[id] ? id : 'home', fly)
    }
    const ui = initUI({
      onVariant(v) {
        if (v === variant) return
        variant = v
        buildShots(v)
        ui.setVariant(v)
        const ops = barOps(graph, v)
        ui.setOps(ops)
        select(ops.some((o) => o.id === selected) ? selected : (ops[0]?.id ?? null))
      },
      onHome: () => goto('home', true),
      onSelect: (id) => select(id),
    }, store)
    ui.setVariant(variant)
    const firstOps = barOps(graph, variant)
    ui.setOps(firstOps)
    const want = params.get('op')
    select(firstOps.find((o) => o.id === want)?.id ?? firstOps[0]?.id ?? null, false)

    hook.selected = () => selected
    hook.select = (id) => select(id)
    hook.camera = () => ({ pos: camera.position.toArray(), target: controls.target.toArray(), fov: camera.fov })
    hook.shot = snap
    hook.flying = () => rig.flying
    hook.pose = () => pose
    hook.flipping = () => flipT < 1
    hook.labShots = () => lab
    setStatus(null)
    hook.ready = true
  } catch (e) {
    console.error(e)
    setStatus(`Could not load the canard model (${(e as Error).message}). The rest of the guide still works at the site root.`, true)
  }
}

boot().catch((e) => { console.error(e); setStatus(`The lab failed to start: ${(e as Error).message}`, true) })
