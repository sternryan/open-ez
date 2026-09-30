import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { Pipeline, LAYER_GLOW } from './render/pipeline'
import { GLOW_TIME, GLOW_VIEW_H, flowRibbon, glowLineMaterial } from './render/flow'
import { makeNoise3D, NOISE3D } from './core/noise'
import { CutState } from './core/cut'
import { compositeMaterial, partMaterial, plyPlane, plySpan, setPlyLook, setWet, COLORS, FOLLOW } from './core/composite'
import { materialFor, type LayupNodeLite, type MaterialSpec } from './logic/materials'
import { workshopEnvironment } from './scene/env'
import { buildWorkshop, ROOM, TABLE_TOP_Y } from './scene/workshop'
import { orientation, type Pose } from './logic/pose'
import { labShots, LAB_FOV, type LabShot } from './shots'
import { CameraRig, easeInOut, type Shot } from './camera'
import { barOps, makeStore, visibleOps, type GraphLite, type Variant } from './logic/graph'
import { visibleSet, pathVisible, type BuildState, type MeshInfo } from './logic/build'
import { plyPhase, partPhase, PLAY_ADVANCE_T, DONE_T, type Phase } from './logic/anim'
import { initUI } from './ui/ui'
import { Director, canardTour, TOUR_BUILD_RATE } from './director'
import { Labels } from './ui/labels'
import { layersAt, summarize, fmtBl, type LayupNode } from './logic/section'
import './style.css'

const INCH = 0.0254
const params = new URLSearchParams(location.search)
const TEST = params.get('test') === '1'
// ?rec=1: the recorder. No frame loop; window.__rec.frame(dt) steps the sim clock and draws, so a film is the same on every run. ?clean=1 hides the controls.
const REC = params.get('rec') === '1'
if (params.get('clean') === '1') document.body.classList.add('clean')
if (REC) document.body.classList.add('rec')
const statusEl = document.getElementById('status') as HTMLElement
const setStatus = (msg: string | null, err = false) => {
  statusEl.hidden = msg === null
  statusEl.textContent = msg ?? ''
  statusEl.classList.toggle('err', err)
}

interface PlyRef { node: string; op: string; order: number }
interface Graph extends GraphLite { loadpaths?: LoadPath[]; components: Record<string, { label?: string }>; plies?: Record<string, PlyRef[]>; layup?: { semi_span?: number; nodes?: Record<string, LayupNodeLite & LayupNode> } | null }
interface LoadPath { id: string; label: string; kind: string; parts: string[]; segments: number[][][] }
interface Cfg { model: string }
interface CamState { pos: number[]; target: number[]; fov: number }
interface LabHook {
  ready: boolean; meshNames(): string[]; stats(): { calls: number; triangles: number }; advance(seconds: number): void
  /** the tour (the film) is running; the tourSteps index it is on */
  touring(): boolean; tourIndex(): number
  selected(): string | null; select(opId: string | null): void; camera(): CamState; shot(name: string): CamState | null; flying(): boolean
  /** the pose the canard is in, or is turning to */
  pose(): Pose; flipping(): boolean; tableTopY(): number
  /** authored lab shots, model inches in the canard's frame (target is the tours.yaml target) */
  labShots(): Record<string, LabShot>
  /** the composite material a mesh got (by mesh name), or null */
  material(name: string): { kind: string; angles: number[]; wet: number } | null
  setWet(name: string, w: number): void
  /** world-space box [min, max] in metres of a mesh, for placing close-up cameras */
  meshBox(name: string): number[][] | null
  /** build state per mesh name (built, current, ghost, hidden), as visibleSet answers it */
  state(): Record<string, BuildState>
  /** the animation phase of a mesh: state, unroll, wet-out front, cure */
  phase(name: string): Phase | null
  lay(): number
  /** lay plies of the selected op (as the scrubber does): resets the animation clock to 0 */
  setLay(n: number): void
  /** the Play button; returns whether it is now playing */
  play(): boolean
  playing(): boolean
  ghost(on: boolean): void
  /** stop the frame loop advancing time; only advance(s) moves the clock */
  freeze(on: boolean): void
  /** the section cut as it is now; planeConstant is the plane's model Z in inches (B.L. b sits at Z = -b, the plane 1e-3 in toward the root; the same number as the 2.1 viewer) */
  cut(): CutInfo
  /** box [min, max] in model inches (the canard's frame, as exported) of a ply node or part */
  plyBox(node: string): { min: number[]; max: number[] } | null
  setSection(on: boolean, bl: number): void
  /** the cut edge's glow, 0..1: kicked when the station moves, decays with sim time */
  cutGlow(): number
  /** model inches -> world metres in the canard's current pose */
  toWorld(p: number[]): number[]
  /** place the camera (world metres); the orbit target is `target` */
  setCamera(pos: number[], target: number[]): void
  /** the part labels: what each shows right now */
  labels(): { id: string; text: string; opacity: number; x: number; y: number }[]
  /** the load paths: visible = its parts exist in the build; drawn = visible and the toggle is on; worldPoints in metres, every segment's points in order, after the canard's pose; clipped = a point is on the removed side of the section plane */
  paths(): { id: string; kind: string; visible: boolean; drawn: boolean; color: number[]; worldPoints: number[][]; clipped: boolean }[]
  /** world metres -> canvas CSS pixels [x, y] with the camera as it is now */
  project(p: number[]): number[]
}
interface CutInfo {
  enabled: boolean; bl: number; planeConstant: number | null
  /** true when the plane, in the world as posed now, keeps a point 5 in outboard of the station and removes one 5 in inboard */
  keepsOutboard: boolean; removesInboard: boolean
  cappedNodes: string[]; capsVisible: number; capNodesVisible: string[]; clipped: number
}
declare global { interface Window { __lab?: LabHook } }

const hook: LabHook = {
  ready: false, meshNames: () => [], stats: () => ({ calls: 0, triangles: 0 }), advance: () => {},
  touring: () => false, tourIndex: () => -1,
  selected: () => null, select: () => {}, camera: () => ({ pos: [0, 0, 0], target: [0, 0, 0], fov: 0 }), shot: () => null, flying: () => false,
  pose: () => 'upright', flipping: () => false, tableTopY: () => TABLE_TOP_Y, labShots: () => ({}),
  material: () => null, setWet: () => {}, meshBox: () => null,
  cut: () => ({ enabled: false, bl: 0, planeConstant: null, keepsOutboard: false, removesInboard: false, cappedNodes: [], capsVisible: 0, capNodesVisible: [], clipped: 0 }),
  plyBox: () => null, setSection: () => {}, labels: () => [], cutGlow: () => 0, toWorld: (p) => p, setCamera: () => {},
  paths: () => [], project: () => [0, 0], state: () => ({}), phase: () => null, lay: () => 0, setLay: () => {}, play: () => false, playing: () => false, ghost: () => {}, freeze: () => {},
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

interface Merged { cid: string; node: string | null; mesh: THREE.Mesh; mat: THREE.Material; spec: MaterialSpec; ply: { op: string; order: number } | null }

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
  const q = params.get('q') || (REC || !coarse ? 'high' : 'mid')
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
  controls.minDistance = 0.15 // close enough to read the weave and the foam cells (12 in = 0.305 m)
  controls.maxDistance = 7.5
  controls.maxPolarAngle = Math.PI * 0.495 // never orbit under the floor: the target sits at table height, so the eye stays above it
  controls.rotateSpeed = 0.7

  const rig = new CameraRig(camera, controls)

  const pipeline = new Pipeline(renderer, { ao: quality !== 'low', msaa: quality === 'low' ? 0 : 4, aoSamples: REC ? 16 : 8 })
  pipeline.aoScale = 0.5
  pipeline.params.ao = 0.55
  pipeline.params.dofTaps = REC ? 40 : 14
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
    GLOW_VIEW_H.value = Math.round(H * dpr)
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
  let stepBuild: (dt: number) => void = () => {}
  let stepCut: (dt: number) => void = () => {}
  let stepLabels: (dt: number) => void = () => {}
  let stepFlows: (dt: number) => void = () => {}
  let stepDirector: (t: number) => void = () => {}
  const step = (dt: number) => {
    simT += dt
    GLOW_TIME.value = simT
    stepDirector(simT)
    stepPose(dt)
    stepBuild(dt)
    stepCut(dt)
    stepFlows(dt)
    rig.update(dt)
    controls.update()
    stepLabels(dt)
  }
  const render = () => {
    pipeline.params.dofFocus = camera.position.distanceTo(controls.target)
    pipeline.params.dofAperture = dofOn ? 9 : 0
    renderer.info.reset()
    pipeline.render(scene, camera, simT)
  }
  let last = performance.now()
  // ?freeze=1 (or __lab.freeze(true)): the frame loop still draws but no longer advances time, so a test or a capture owns the clock
  let frozen = TEST && params.get('freeze') === '1'
  if (!REC) renderer.setAnimationLoop(() => {
    const t = performance.now(), dt = Math.min((t - last) / 1000, 0.1)
    last = t
    if (!frozen) step(dt)
    render()
  })
  hook.freeze = (on: boolean) => { frozen = on }
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
    // One composite material per merged mesh, chosen from the layup cloth/orientation and the component id (logic/materials.ts).
    // The plane lives in the model frame (`root`), so it follows the flip. As in the 2.1 viewer, the kept side of a CutState is local
    // z < e = -b + 1e-3: the inboard side is removed and the cut face looks toward the root, where the op shots are taken from.
    const cut = new CutState(root, 80, -80)
    cut.amount = 0
    const layupNodes = graph.layup?.nodes ?? null
    const plyRefs = new Map<string, PlyRef>()
    for (const list of Object.values(graph.plies ?? {})) for (const r of list) plyRefs.set(r.node, r)
    for (const p of parts) {
      const spec = materialFor(p.node, p.cid, layupNodes)
      const mat = spec.kind === 'part' ? partMaterial(cut) : compositeMaterial(spec, cut, plyPlane(p.geo), plySpan(p.geo))
      const mesh = new THREE.Mesh(p.geo, mat)
      mesh.name = p.node ?? p.cid
      mesh.castShadow = true
      mesh.receiveShadow = true
      root.add(mesh)
      const ref = p.node ? plyRefs.get(p.node) : undefined
      if (p.node && !ref) throw new Error(`ply ${p.node} is not in graph.plies`)
      merged.push({ cid: p.cid, node: p.node, mesh, mat, spec, ply: ref ? { op: ref.op, order: ref.order } : null })
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
      for (const id of Object.keys(rig.shots)) if (id !== 'home' && id !== 'cutclose') delete rig.shots[id]
      for (const [id, ls] of Object.entries(lab)) {
        const m = modelToWorld(orientation(graph, v, id))
        const tgt = new THREE.Vector3(...ls.target).applyMatrix4(m), pos = new THREE.Vector3(...ls.position).applyMatrix4(m)
        rig.shots[id] = { pos: [pos.x, pos.y, pos.z], target: [tgt.x, tgt.y, tgt.z], fov: LAB_FOV }
      }
    }
    // the closing shot: a slow 3/4 turn about the cut face at B.L. 20, from the leading-edge side toward the root (model inches, canard upright)
    const CLOSE = { dist: 47, el: 27, az: -55, target: [4, 0.4, -25] as const }
    {
      const up = modelToWorld('upright')
      const el = (CLOSE.el * Math.PI) / 180, az = (CLOSE.az * Math.PI) / 180
      const t = new THREE.Vector3(...CLOSE.target)
      const p = t.clone().add(new THREE.Vector3(CLOSE.dist * Math.cos(el) * Math.sin(az), CLOSE.dist * Math.sin(el), CLOSE.dist * Math.cos(el) * Math.cos(az)))
      t.applyMatrix4(up); p.applyMatrix4(up)
      rig.shots.cutclose = { pos: p.toArray(), target: t.toArray(), fov: LAB_FOV }
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
    // ---- build state: recomputed from scratch with visibleSet on every change (op, lay, variant, ghost), never patched ----
    // The look of each mesh (unroll, wet-out front, cure) is plyPhase(op, lay, t), t = seconds since `lay` last changed. All time
    // comes through step(dt), so __lab.advance(s) reproduces any frame.
    const GHOST_KEY = 'longez.ghost'
    let ghost = false
    try { ghost = storage?.getItem(GHOST_KEY) === '1' } catch { ghost = false }
    graph.__ghost = ghost
    const infos: MeshInfo[] = merged.map((m) => ({ name: m.node ?? m.cid, component: m.cid, ply: m.ply }))
    const opCount = (id: string | null) => (id ? Object.values(graph.plies ?? {}).flat().filter((r) => r.op === id).length : 0)
    let lay = 0, layT = DONE_T, playing = false, tourRate = 1
    let bstate = new Map<string, BuildState>()
    let opIdx = new Map<string, number>()
    const phases = new Map<string, Phase>()
    let shadowSig = ''
    // ?hide=<name prefix>[,..] keeps those meshes out of the scene (for close-ups of work hidden inside the core)
    const hide = (params.get('hide') ?? '').split(',').filter(Boolean)
    const recompute = () => {
      opIdx = new Map(visibleOps(graph, variant).map((o, i) => [o.id, i]))
      bstate = selected && opIdx.has(selected)
        ? visibleSet(graph, variant, selected, lay, infos)
        : new Map<string, BuildState>(infos.map((i) => [i.name, 'built']))
    }
    const paint = () => {
      const cur = selected ? opIdx.get(selected) : undefined, count = opCount(selected)
      let sig = ''
      for (const m of merged) {
        const name = m.node ?? m.cid, st = bstate.get(name) ?? 'hidden'
        const ph = m.ply && cur !== undefined
          ? plyPhase({ meshOpIndex: opIdx.get(m.ply.op), curOpIndex: cur, order: m.ply.order, lay, count, t: layT, ghost })
          : partPhase(st)
        phases.set(name, ph)
        m.mesh.visible = st !== 'hidden' && !(m.ply && st === 'current' && ph.unroll <= 0) && !hide.some((h) => name.startsWith(h))
        m.mesh.castShadow = st === 'built' || (st === 'current' && ph.unroll >= 1)
        setPlyLook(m.mat, { unroll: ph.unroll, front: ph.front, cure: ph.cure, ghost: st === 'ghost' })
        sig += m.mesh.visible && m.mesh.castShadow ? '1' : '0'
      }
      if (sig !== shadowSig) { shadowSig = sig; pipeline.shadowDirty = true }
    }
    // ---- load paths: airsup's glow-line flows. The points ship in the CadQuery frame (X chord, Y = B.L., Z up), so they hang under a
    // group carrying the glb root's -90 deg X rotation, inside `root`: they follow the scale, the recentring and the flip. Each polyline
    // is a camera-facing ribbon (lines are 1 px in WebGL): a hot core above the bloom threshold, a soft coloured halo, and comet pulses
    // running along its arc length, added as light. While any flow is drawn the laminate dims a little (FOLLOW) so the light reads.
    // Qualitative only: the colours name a kind of load, the brightness carries no magnitude. Direction of travel: lift runs skin -> cap
    // (its points are already in that order), bending and shear run toward the root, so any segment that starts at the root is reversed. ----
    const PATHS_KEY = 'longez.paths'
    // speed: pulses per second past a point; scale: pulse spacing (in). Pulses travel speed * scale inches per second.
    const FLOW: Record<string, { color: number; speed: number; scale: number }> = {
      bending: { color: 0xff6a10, speed: 0.9, scale: 9 }, // amber, along the caps to the root
      shear: { color: 0x2a86ff, speed: 0.9, scale: 8 }, // electric blue, along the web to the root
      lift: { color: 0x10e070, speed: 1.2, scale: 2.5 }, // green, from the skins into the caps
    }
    const FLOW_LOOK = { base: 0.45, pulse: 2.2, core: 1.6, halo: 0.9, hot: 0.08, dim: 0.85, halfWidth: 0.4 * INCH, px: [7, 20] as [number, number] }
    let pathsOn = true
    // a tour may change what is shown while it runs (tourOv), but never the person's own setting (pathsOn, labelsOn) or their storage
    const tourOv: { labels: boolean | null; paths: boolean | null } = { labels: null, paths: null }
    const pathsShown = () => tourOv.paths ?? pathsOn
    try { pathsOn = storage?.getItem(PATHS_KEY) !== '0' } catch { pathsOn = true }
    const pathsGroup = new THREE.Group()
    pathsGroup.name = 'loadPaths'
    pathsGroup.rotation.x = -Math.PI / 2
    root.add(pathsGroup)
    const flowEmph = { value: 1 }
    const flowMats: Record<string, THREE.ShaderMaterial> = {}
    for (const [kind, f] of Object.entries(FLOW)) flowMats[kind] = glowLineMaterial(cut, { ...FLOW_LOOK, color: f.color, emph: flowEmph, speed: f.speed, scale: f.scale })
    interface PathObj { p: LoadPath; group: THREE.Group; visible: boolean }
    const pathObjs: PathObj[] = []
    for (const lp of graph.loadpaths ?? []) {
      const mat = flowMats[lp.kind]
      const group = new THREE.Group()
      group.name = lp.id
      group.visible = false
      for (const seg of mat ? lp.segments : []) {
        let pts = seg.map(([x, y, z]) => new THREE.Vector3(x, y, z))
        if ((lp.kind === 'bending' || lp.kind === 'shear') && pts[0].y < pts[pts.length - 1].y) pts = pts.reverse()
        const tube = new THREE.Mesh(flowRibbon(pts), mat)
        tube.layers.set(LAYER_GLOW)
        tube.renderOrder = 10
        tube.frustumCulled = false
        group.add(tube)
      }
      pathsGroup.add(group)
      pathObjs.push({ p: lp, group, visible: false })
    }
    // recomputed from the build state on every change, never patched; no build state draws nothing
    const syncPaths = () => {
      for (const o of pathObjs) {
        o.visible = pathVisible(o.p, bstate)
        o.group.visible = o.visible && pathsShown()
      }
    }
    // the laminate dims while any flow is drawn, eased in sim time so a recorded frame is reproducible
    stepFlows = (dt) => {
      const want = pathObjs.some((o) => o.group.visible) ? 1 : 0
      FOLLOW.value += (want - FOLLOW.value) * (1 - Math.exp(-dt * 5))
      if (Math.abs(want - FOLLOW.value) < 1e-3) FOLLOW.value = want
    }
    const setPaths = (on: boolean) => {
      pathsOn = on
      try { storage?.setItem(PATHS_KEY, on ? '1' : '0') } catch { /* per-viewer convenience only */ }
      ui.setPaths(on)
      syncPaths()
    }
    const refresh = () => { recompute(); paint(); syncPaths(); ui.setBuild(lay, opCount(selected)); updateReadout() }
    const stopPlay = () => { playing = false; ui.setPlaying(false) }
    const openOp = () => { stopPlay(); lay = opCount(selected); layT = DONE_T; refresh() } // a step opens fully built and cured
    const setLay = (n: number) => { stopPlay(); lay = Math.max(0, Math.min(n, opCount(selected))); layT = 0; refresh() }
    const togglePlay = () => {
      if (playing) { stopPlay(); return }
      if (!opCount(selected)) return
      lay = 1; layT = 0; playing = true
      ui.setPlaying(true)
      refresh()
    }
    const setGhost = (on: boolean) => {
      ghost = on
      graph.__ghost = on
      try { storage?.setItem(GHOST_KEY, on ? '1' : '0') } catch { /* per-viewer convenience only */ }
      ui.setGhost(on)
      refresh()
    }
    stepBuild = (dt) => {
      const count = opCount(selected), before = layT
      let changed = false
      layT += dt * tourRate // a tour runs the build clock faster
      if (playing) {
        while (lay < count && layT >= PLAY_ADVANCE_T) { layT -= PLAY_ADVANCE_T; lay++; changed = true }
        if (lay >= count && layT >= DONE_T) stopPlay() // the cure has run
      }
      layT = Math.min(layT, DONE_T)
      if (changed) refresh()
      else if (layT !== before) paint()
    }
    const goto = (shot: string, fly: boolean) => {
      currentShot = shot
      if (fly) rig.fly(shot, 1.8, 0.05); else rig.set(shot)
    }

    // ---- section cut: airsup's CutState on our meshes. Station b (B.L. inches) is the plane at model Z = -b + EPS, so a ply whose
    // last inch ends exactly at the station still caps. The inboard side is removed (2.1's convention), so the op shots, which
    // look from the root, see the cut face. ----
    const EPS = 1e-3
    const layupN = graph.layup?.nodes ?? null
    const semi = graph.layup?.semi_span ?? 70
    let secOn = false, secBl = Math.round(semi / 2), glow = 0
    for (const m of merged) m.mesh.geometry.computeBoundingBox()
    const nameOf = (m: Merged) => m.node ?? m.cid
    const liveState = (m: Merged) => bstate.get(nameOf(m))
    const isBuilt = (m: Merged) => { const st = liveState(m); return (st === 'built' || st === 'current') && m.mesh.visible }
    // the same inequality as layersAt / guide.layup.counts_at (bl <= bl_max), with the plane's own tolerance at either end
    const crosses = (m: Merged) => { const b = m.mesh.geometry.boundingBox!; return b.min.z - EPS <= -secBl && -secBl <= b.max.z + EPS }
    const isCapped = (m: Merged) => secOn && isBuilt(m) && crosses(m)
    const applyCut = () => {
      // CutState: e = depth + (extent - depth) * (1 - amount) is the plane's model Z; solve for the amount that puts it at -b + EPS
      cut.amount = secOn ? 1 - (-secBl + EPS - cut.depth) / (cut.extent - cut.depth) : 0
      cut.update()
      cut.uGlow.value = secOn ? glow : 0 // the line rides the edge while the station moves, and settles (sim time) when it stops
    }
    stepCut = (dt) => {
      if (glow > 0) { glow *= Math.exp(-dt * 4); if (glow < 0.01) glow = 0 }
      if (secOn) { applyCut(); if (dt > 0 && glow > 0) pipeline.shadowDirty = true }
    }
    const setSection = (on: boolean, bl: number) => {
      const was = secOn
      secOn = on && !!layupN
      secBl = Math.max(0, Math.min(bl, semi))
      glow = 1
      applyCut()
      if (secOn !== was) paint() // the cap pass materials are created when the cut opens: give them the plies' current look
      pipeline.shadowDirty = true
      ui.setSection(secOn, secBl)
      updateReadout()
    }

    // ---- readout: counts and sourced text only ----
    const CLOTH_ORDER = ['UND', 'BID']
    const updateReadout = () => {
      const n = opCount(selected)
      const cnt = new Map<string, number>()
      const lit: Record<string, LayupNode> = {}
      for (const m of merged) {
        if (!m.node || !layupN?.[m.node]) continue
        const st = bstate.get(m.node)
        if (st !== 'built' && st !== 'current') continue
        cnt.set(layupN[m.node].cloth, (cnt.get(layupN[m.node].cloth) ?? 0) + 1)
        lit[m.node] = layupN[m.node]
      }
      const cloth = [...cnt].sort(([a], [b]) => (CLOTH_ORDER.indexOf(a) + 1 || 99) - (CLOTH_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b)).map(([k, c]) => `${k} ${c}`).join(' · ')
      let layers = layupN ? 'Turn on the section to list the layers there' : ''
      if (secOn) {
        const order = Object.keys(graph.components)
        const parts = merged.filter((m) => !m.node && isCapped(m)).sort((a, b) => order.indexOf(a.cid) - order.indexOf(b.cid)).map((m) => graph.components[m.cid]?.label ?? m.cid)
        const here = layersAt(lit, secBl)
        if (here.length || !parts.length) parts.push(summarize(graph, here))
        layers = parts.join(' · ')
      }
      ui.setReadout({ station: secOn ? fmtBl(secBl) : 'Section off', layers, plies: n ? `${lay} / ${n}` : null, cloth: cloth || 'none yet' })
    }

    // ---- part labels: one per part group that has geometry ----
    const LABELS_KEY = 'longez.labels'
    let labelsOn = true
    try { labelsOn = storage?.getItem(LABELS_KEY) !== '0' } catch { labelsOn = true }
    const labels = new Labels(document.getElementById('labels') as HTMLElement, camera)
    const hex = (c: number) => '#' + c.toString(16).padStart(6, '0')
    const ray = new THREE.Raycaster()
    const upright = root.matrixWorld.clone() // the canard is upright here, so world directions are model directions
    /** a point on the part's outer surface at B.L. `bl`, in model inches, with the surface normal; null when nothing is hit there */
    const anchorAt = (cid: string, bl: number): { bl: number; p: THREE.Vector3; n: THREE.Vector3 } | null => {
      const ms = merged.filter((m) => m.cid === cid).map((m) => m.mesh)
      if (!ms.length) return null
      const bx = new THREE.Box3()
      for (const m of ms) bx.union(m.geometry.boundingBox!)
      const dir = cid.includes('bottom') ? new THREE.Vector3(0, 1, 0) : cid.includes('shear_web') ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, -1, 0)
      const c = bx.getCenter(new THREE.Vector3())
      const z = Math.min(Math.max(-bl, bx.min.z + 0.3), bx.max.z - 0.3)
      for (const f of [0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8]) {
        const o = new THREE.Vector3(bx.min.x + (bx.max.x - bx.min.x) * f, c.y, z)
        if (dir.x) o.set(bx.min.x - 4, c.y, z); else if (dir.y < 0) o.y = bx.max.y + 4; else o.y = bx.min.y - 4
        ray.set(o.clone().applyMatrix4(upright), dir)
        const hit = ray.intersectObjects(ms, false)[0]
        if (hit) return { bl: -z, p: hit.point.clone().applyMatrix4(upright.clone().invert()), n: (hit.face?.normal ?? dir.clone().negate()).clone() }
      }
      return null
    }
    const wp = new THREE.Vector3(), wn = new THREE.Vector3(), cp = new THREE.Vector3()
    for (const cid of Object.keys(graph.components)) {
      // candidate anchors along the span: with the section off the label sits near B.L. 25; with it on it rides the nearest one that is on the kept (outboard) side
      // each part has its own preferred station, so the pills spread along the span instead of stacking on one point
      const prefer = cid.includes('skin') ? 40 : cid.includes('shear_web') ? 14 : cid.includes('spar_cap') ? 26 : 32
      const cands = [prefer, 5, 11, 18, 25, 32, 40, 48, 56, 64].map((bl) => anchorAt(cid, bl)).filter((a): a is NonNullable<typeof a> => !!a)
      if (!cands.length) continue // lift tabs and the like have no geometry, so no label
      const mine = merged.filter((m) => m.cid === cid)
      const kind = mine[0].spec.kind
      const color = hex(kind === 'und' ? COLORS.und : kind === 'bid' ? COLORS.bid : kind === 'foam' ? COLORS.foam : 0xe6dfcf)
      const byBl = [...cands].sort((a, b) => a.bl - b.bl)
      const pick = () => (secOn ? byBl.find((a) => a.bl >= secBl + 2) ?? null : cands[0])
      labels.add({
        id: cid, text: graph.components[cid]?.label ?? cid, color,
        at: () => { const a = pick(); return a ? wp.copy(a.p).applyMatrix4(root.matrixWorld) : null },
        vis: () => {
          const a = pick()
          if (!(tourOv.labels ?? labelsOn) || !a || !mine.some(isBuilt)) return 0
          wp.copy(a.p).applyMatrix4(root.matrixWorld)
          wn.copy(a.n).transformDirection(root.matrixWorld)
          return wn.dot(cp.copy(camera.position).sub(wp)) > 0 ? 1 : 0 // the surface faces away from the camera: hide
        },
      })
    }
    stepLabels = (dt) => { camera.updateMatrixWorld(); labels.update(window.innerWidth, window.innerHeight, dt) }
    const setLabels = (on: boolean) => {
      labelsOn = on
      try { storage?.setItem(LABELS_KEY, on ? '1' : '0') } catch { /* per-viewer convenience only */ }
      ui.setLabels(on)
    }
    buildShots(variant)
    const select = (id: string | null, fly = true) => {
      selected = id
      ui.setSelected(id)
      openOp()
      setPose(orientation(graph, variant, id), fly)
      goto(id && rig.shots[id] ? id : 'home', fly)
    }
    // ---- the tour: src/director.ts scripts the page's own controls with a cursor. A click the director dispatches is told from a person's by
    // director.busy; anything a person does (op chip, variant, scrubber, Play, the camera, Escape, Tour again) ends the tour where it stands. ----
    let orb: { r: number; y: number; a0: number } | null = null
    const director = new Director({
      act(name) {
        if (name === 'reset') { stopPlay(); select(null, !REC); tourOv.labels = true; tourOv.paths = true; syncPaths(); if (secOn) setSection(false, secBl) }
        else if (name === 'finish') { stopPlay(); select(null, true) }
        else if (name === 'closeup') goto('cutclose', true)
      },
      orbit(k, deg, first) {
        if (first) {
          const d = camera.position.clone().sub(controls.target)
          orb = { r: Math.hypot(d.x, d.z), y: d.y, a0: Math.atan2(d.x, d.z) }
          rig.flying = false
        }
        if (!orb) return
        const a = orb.a0 - (deg * Math.PI / 180) * k
        camera.position.set(controls.target.x + orb.r * Math.sin(a), controls.target.y + orb.y, controls.target.z + orb.r * Math.cos(a))
        controls.update()
      },
    })
    // whatever ends the tour (its last step, Escape, a person's click), the section cut, paths and labels go back to what the person had
    let before: { secOn: boolean; secBl: number } | null = null
    const endTour = () => {
      tourRate = 1
      tourOv.labels = tourOv.paths = null
      if (before) { const b = before; before = null; setSection(b.secOn, b.secBl) }
      syncPaths()
      ui.setTouring(false)
    }
    const stopTour = () => {
      if (!director.active) return
      director.stop()
      endTour()
    }
    director.onEnd = endTour
    const startTour = () => {
      stopPlay()
      before = { secOn, secBl }
      director.load(canardTour(graph as never, variant))
      director.start(simT)
      tourRate = TOUR_BUILD_RATE
      ui.setTouring(true)
    }
    const userAct = () => { if (director.active && !director.busy) stopTour() }
    stepDirector = (t) => director.update(t)
    controls.addEventListener('start', userAct)
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') stopTour() })

    const ui = initUI({
      onVariant(v) {
        if (v === variant) return
        userAct()
        variant = v
        buildShots(v)
        ui.setVariant(v)
        const ops = barOps(graph, v)
        ui.setOps(ops)
        select(ops.some((o) => o.id === selected) ? selected : (ops[0]?.id ?? null))
      },
      onHome: () => goto('home', true),
      onTour: () => (director.active ? stopTour() : startTour()),
      onSelect: (id) => { userAct(); select(id) },
      onGhost: (on) => { userAct(); setGhost(on) },
      onScrub: (n) => { userAct(); setLay(n) },
      onPlay: () => { userAct(); togglePlay() },
      onSection: (on, bl) => { userAct(); setSection(on, bl) },
      onLabels: (on) => { userAct(); setLabels(on) },
      onPaths: (on) => { userAct(); setPaths(on) },
    }, store)
    ui.setGhost(ghost)
    ui.setLabels(labelsOn)
    ui.setPaths(pathsOn)
    if (layupN) ui.initSection(semi, secBl)
    ui.setVariant(variant)
    const firstOps = barOps(graph, variant)
    ui.setOps(firstOps)
    const want = params.get('op')
    select(firstOps.find((o) => o.id === want)?.id ?? firstOps[0]?.id ?? null, false)

    hook.touring = () => director.active
    hook.tourIndex = () => director.seg
    hook.selected = () => selected
    hook.select = (id) => select(id)
    hook.camera = () => ({ pos: camera.position.toArray(), target: controls.target.toArray(), fov: camera.fov })
    hook.shot = snap
    hook.flying = () => rig.flying
    hook.pose = () => pose
    hook.flipping = () => flipT < 1
    hook.labShots = () => lab
    hook.material = (name) => {
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      if (!m) return null
      const info = (m.mesh.material as THREE.Material).userData.comp as { wet: number } | undefined
      return { kind: m.spec.kind, angles: m.spec.angles.slice(), wet: info?.wet ?? 0 }
    }
    hook.setWet = (name, w) => {
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      if (m) setWet(m.mesh.material as THREE.Material, w)
    }
    hook.meshBox = (name) => {
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      if (!m) return null
      const bx = new THREE.Box3().setFromObject(m.mesh)
      return [bx.min.toArray(), bx.max.toArray()]
    }
    hook.state = () => Object.fromEntries(bstate)
    hook.phase = (name) => phases.get(name) ?? null
    hook.lay = () => lay
    hook.setLay = setLay
    hook.play = () => { togglePlay(); return playing }
    hook.playing = () => playing
    hook.ghost = setGhost
    hook.setSection = setSection
    hook.cutGlow = () => cut.uGlow.value
    hook.toWorld = (p) => new THREE.Vector3(p[0], p[1], p[2]).applyMatrix4(root.matrixWorld).toArray()
    hook.setCamera = (pos, target) => {
      camera.position.set(pos[0], pos[1], pos[2])
      controls.target.set(target[0], target[1], target[2])
      controls.update()
      rig.lastUser = performance.now()
    }
    hook.labels = () => labels.stats()
    hook.paths = () => {
      pathsGroup.updateWorldMatrix(true, true)
      return pathObjs.map((o) => {
        const pts = o.p.segments.flat().map((q) => new THREE.Vector3(q[0], q[1], q[2]).applyMatrix4(pathsGroup.matrixWorld))
        const c = flowMats[o.p.kind]?.uniforms.uColor.value as THREE.Color | undefined
        const rgb = c ? c.getRGB({ r: 0, g: 0, b: 0 }, THREE.SRGBColorSpace) : { r: 0, g: 0, b: 0 }
        return {
          id: o.p.id, kind: o.p.kind, visible: o.visible, drawn: o.visible && pathsShown(), color: [rgb.r, rgb.g, rgb.b],
          worldPoints: pts.map((v) => v.toArray()),
          clipped: secOn && pts.some((v) => cut.world.distanceToPoint(v) < 0),
        }
      })
    }
    hook.project = (p) => {
      camera.updateMatrixWorld()
      const v = new THREE.Vector3(p[0], p[1], p[2]).project(camera)
      const r = canvas.getBoundingClientRect()
      return [(v.x * 0.5 + 0.5) * r.width + r.left, (-v.y * 0.5 + 0.5) * r.height + r.top]
    }
    hook.plyBox = (name) => {
      const ms = merged.filter((m) => nameOf(m) === name || m.cid === name)
      if (!ms.length) return null
      const bx = new THREE.Box3()
      for (const m of ms) bx.union(m.mesh.geometry.boundingBox!)
      return { min: bx.min.toArray(), max: bx.max.toArray() }
    }
    hook.cut = () => {
      const kept = (z: number) => cut.world.distanceToPoint(new THREE.Vector3(0, 0, z).applyMatrix4(root.matrixWorld)) >= 0
      const capNodes = merged.filter((m) => isCapped(m) && Array.isArray(m.mesh.material) && (m.mat.userData.back as THREE.Material | undefined)?.userData.u.uGhost.value === 0).map(nameOf)
      return {
        enabled: secOn, bl: secBl, planeConstant: secOn ? cut.local.constant : null,
        keepsOutboard: secOn && kept(-secBl - 5), removesInboard: secOn && !kept(-secBl + 5),
        cappedNodes: merged.filter(isCapped).map(nameOf), capsVisible: capNodes.length, capNodesVisible: capNodes,
        clipped: secOn ? merged.filter((m) => m.mesh.visible && m.mesh.geometry.boundingBox!.min.z < -secBl + EPS).length : 0,
      }
    }
    // ?wet=<node>[,<node>] floods those plies with resin; ?cam=px,py,pz,tx,ty,tz (world metres) places the camera for close-ups.
    for (const n of (params.get('wet') ?? '').split(',').filter(Boolean)) hook.setWet(n, 1)
    const camp = (params.get('cam') ?? '').split(',').map(Number)
    if (camp.length === 6 && camp.every(Number.isFinite)) {
      camera.position.set(camp[0], camp[1], camp[2])
      controls.target.set(camp[3], camp[4], camp[5])
      controls.update()
      rig.lastUser = performance.now() // treat as the user's camera so a resize keeps it
    }
    setStatus(null)
    hook.ready = true
    if (REC) {
      ;(window as unknown as Record<string, unknown>).__rec = {
        /** begin the film and return its length in seconds; only the canard chapter exists */
        start(name: string) {
          if (name !== 'canard') throw new Error(`no film called ${name}`)
          startTour()
          return director.duration
        },
        /** advance the sim clock by dt seconds; draw=false skips the render (the clock and the DOM still move) */
        frame(dt: number, draw = true) {
          step(dt)
          if (draw) render()
          return { t: simT, active: director.active }
        },
      }
    }
  } catch (e) {
    console.error(e)
    setStatus(`Could not load the canard model (${(e as Error).message}). The rest of the guide still works at the site root.`, true)
  }
}

boot().catch((e) => { console.error(e); setStatus(`The lab failed to start: ${(e as Error).message}`, true) })
