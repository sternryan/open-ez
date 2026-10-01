import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { Pipeline, LAYER_GLOW } from './render/pipeline'
import { GLOW_TIME, GLOW_VIEW_H, flowRibbon, glowLineMaterial } from './render/flow'
import { makeNoise3D, NOISE3D } from './core/noise'
import { CutState } from './core/cut'
import { CHEAP, setCheapShaders } from './core/materials'
import { compositeMaterial, partMaterial, plyPlane, plySpan, setPlyLook, setWet, COLORS, FOLLOW, HATCH_COLOR } from './core/composite'
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
import { TIER_ORDER, TIERS, tierPixelRatio, parseTier, startTier, nextTier, initialStep, nextRes, initialRes, type ResState, type Tier, type StepState } from './quality'
import { Director, chapterTour, tourChapter, CHAPTER, TOUR_BUILD_RATE } from './director'
import { Labels } from './ui/labels'
import { layersAt, summarize, fmtBl, type LayupNode } from './logic/section'
import { FuselageBay } from './fuselageBay'
import { fuseBarOps, parseSubject, stationLayers, stationSummary, fmtFs, cgRow, groundRow, removedByStationCut, crossedByStationCut, labelPriority, homeLabel, keyScale, FUSE_CHAPTERS, SUBJECT_KEY, type Subject, type FuseLayup, type LedgerLite, type JigPose } from './logic/fuselage'
import { STATION, fsToX } from './scene/fuselageStation'
import { fuselageTour, fuselageTourChapters, FUSE_CUT_FS, FUSE_CUTS, FUSE_CUT_VIEW } from './director'
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
interface Graph extends GraphLite { loadpaths?: LoadPath[]; components: Record<string, { label?: string }>; plies?: Record<string, PlyRef[]>; layup?: { semi_span?: number; nodes?: Record<string, LayupNodeLite & LayupNode>; fuselage?: FuseLayup } | null }
interface LoadPath { id: string; label: string; kind: string; parts: string[]; segments: number[][][] }
interface Cfg { model: string }
interface CamState { pos: number[]; target: number[]; fov: number }
interface LabHook {
  /** quality tier in use; setTier picks one by hand (and turns automatic step-down off); feedFrame injects a frame time (ms) into the step-down rule */
  /** the low tier's adaptive resolution: the multiplier on the pixel count it draws (1 = the tier's full budget) */
  resScale(): number
  /** WebGL context loss (?test=1): whether it is lost now; loseContext/restoreContext drive it through WEBGL_lose_context (false when the browser has no such extension) */
  contextLost(): boolean; loseContext(): boolean; restoreContext(): boolean
  tier(): Tier; setTier(t: Tier): void; auto(): boolean; setAuto(on: boolean): void; feedFrame(ms: number): void
  ready: boolean; meshNames(): string[]; stats(): { calls: number; triangles: number; pixels: number }; advance(seconds: number): void
  /** the tour (the film) is running; the tourSteps index it is on */
  touring(): boolean; tourIndex(): number
  selected(): string | null; select(opId: string | null): void; camera(): CamState; shot(name: string): CamState | null; flying(): boolean
  /** the pose the canard is in, or is turning to */
  pose(): Pose; flipping(): boolean; tableTopY(): number
  /** authored lab shots, model inches in the canard's frame (target is the tours.yaml target) */
  labShots(): Record<string, LabShot>
  /** the composite material a mesh got (by mesh name), or null */
  material(name: string): { kind: string; angles: number[]; wet: number; hatch?: boolean; fidelity?: string } | null
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
  labels(): { id: string; text: string; opacity: number; x: number; y: number; collapsed?: boolean; hidden?: boolean }[]
  /** the load paths: visible = its parts exist in the build; drawn = visible and the toggle is on; worldPoints in metres, every segment's points in order, after the canard's pose; clipped = a point is on the removed side of the section plane */
  paths(): { id: string; kind: string; visible: boolean; drawn: boolean; color: number[]; worldPoints: number[][]; clipped: boolean }[]
  /** world metres -> canvas CSS pixels [x, y] with the camera as it is now */
  project(p: number[]): number[]
  /** what the lab is building: the canard (the default) or the fuselage box and gear (chapters 4-9); setSubject is the control's action */
  subject(): Subject; setSubject(s: Subject): void
  /** the fuselage: where each part is now (on the layup table, in the jig, or not made yet) and which way up the box is */
  placement(): Record<string, 'table' | 'jig' | 'none'>; jigPose(): string
  /** the fuselage ops' lab shots (world metres), and the CG row as the readout shows it */
  fuseShots(): Record<string, CamState>; cg(): { value: string; sub: string | null }
  /** the box's frame (inches: x = FS, y = W.L. - 17.4, z = -B.L.) -> world metres, as the jig holds it now */
  fuseToWorld(p: number[]): number[]
  /** the same with the box at rest in `pose` (no turn under way), and whether the box is turning over now */
  fuseRestToWorld(p: number[], pose: string): number[]; fuseTurning(): boolean
  /** the finished box on its feet: the jig bench's world box and each gear part's (and the wheels') world box as drawn now, metres */
  fuseFloor(): { bench: number[][]; gear: Record<string, number[][]>; noseStand: boolean } | null
  /** the gear positioning's marks (plans-1980:p50): shown, their stations and words, their anchors in the box's frame and the world */
  gearMarks(): { shown: boolean; axleFs: number; boardFs: number; dimText: string; axleText: string; dimModel: number[]; axleModel: number[]; dimWorld: number[]; axleWorld: number[] } | null
  /** the ground-handling note as the readout shows it */
  ground(): { value: string; sub: string } | null
}
interface CutInfo {
  enabled: boolean; bl: number; planeConstant: number | null
  /** fuselage subject: the station (FS) and the plane's constant in the box's frame (-FS); keepsAft/removesForward as the canard's pair */
  fs?: number; keepsAft?: boolean; removesForward?: boolean
  /** true when the plane, in the world as posed now, keeps a point 5 in outboard of the station and removes one 5 in inboard */
  keepsOutboard: boolean; removesInboard: boolean
  cappedNodes: string[]; capsVisible: number; capNodesVisible: string[]; clipped: number
}
declare global { interface Window { __lab?: LabHook } }

const hook: LabHook = {
  ready: false, meshNames: () => [], stats: () => ({ calls: 0, triangles: 0, pixels: 0 }), advance: () => {},
  touring: () => false, tourIndex: () => -1,
  selected: () => null, select: () => {}, camera: () => ({ pos: [0, 0, 0], target: [0, 0, 0], fov: 0 }), shot: () => null, flying: () => false,
  pose: () => 'upright', flipping: () => false, tableTopY: () => TABLE_TOP_Y, labShots: () => ({}),
  material: () => null, setWet: () => {}, meshBox: () => null,
  cut: () => ({ enabled: false, bl: 0, planeConstant: null, keepsOutboard: false, removesInboard: false, cappedNodes: [], capsVisible: 0, capNodesVisible: [], clipped: 0 }),
  plyBox: () => null, setSection: () => {}, labels: () => [], cutGlow: () => 0, toWorld: (p) => p, setCamera: () => {},
  contextLost: () => false, loseContext: () => false, restoreContext: () => false,
  resScale: () => 1, tier: () => 'high', setTier: () => {}, auto: () => false, setAuto: () => {}, feedFrame: () => {},
  paths: () => [], project: () => [0, 0], state: () => ({}), phase: () => null, lay: () => 0, setLay: () => {}, play: () => false, playing: () => false, ghost: () => {}, freeze: () => {},
  subject: () => 'canard', setSubject: () => {}, placement: () => ({}), jigPose: () => 'upright', fuseShots: () => ({}), cg: () => ({ value: 'not yet computed', sub: null }), fuseToWorld: (p) => p,
  fuseRestToWorld: (p) => p, fuseTurning: () => false, fuseFloor: () => null, gearMarks: () => null, ground: () => null,
}
/** the words of the gear positioning's marks: the book's 15 in from the datum board to the axle centre line, and the axle station */
const MARK_TEXT = {
  dim: (inches: number) => `${inches} in`,
  axle: (fs: number) => `Axle C.L. F.S. ${fs} (book)`,
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

function mergeModel(scene: THREE.Object3D, graph: Graph, parts: Set<string> = new Set()): { cid: string; node: string | null; geo: THREE.BufferGeometry }[] {
  scene.updateMatrixWorld(true)
  const groups = new Map<string, { cid: string; node: string | null; geos: THREE.BufferGeometry[] }>()
  // GLTFLoader strips dots from node names (canard.core -> canardcore); the original is kept in userData.name.
  const nm = (x: THREE.Object3D): string => (x.userData?.name as string | undefined) ?? x.name
  scene.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    let n: THREE.Object3D = o
    // a fuselage part node (fuselage.<part>) groups its meshes like a component does; two longerons share one component
    const group = (x: THREE.Object3D) => !!graph.components[nm(x)] || parts.has(nm(x))
    while (n && !group(n) && n.parent) n = n.parent
    const cid = group(n) ? nm(n) : nm(o)
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

/** The finished fuselage's home shot (main: rig.shots.ffinal): eye direction from the target, target offset (metres) and frame fill. */
const FINAL_SHOT = { dir: [0.62, 0.6, 0.5] as [number, number, number], dx: -0.32, dy: -0.12, fill: 0.56 }

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
  renderer.shadowMap.autoUpdate = false
  renderer.localClippingEnabled = true
  renderer.info.autoReset = false // count the whole frame (every pipeline pass), not just the last render call

  const coarse = matchMedia('(pointer: coarse)').matches
  // Quality tier (quality.ts): ?q=high|mid|low forces one and turns automatic step-down off; so do ?freeze=1 and ?rec=1, which must be deterministic.
  const forcedTier = parseTier(params.get('q'))
  // A context loss in this tab's session lowers the start tier for the rest of it (kept across the reload the overlay offers).
  const CAP_KEY = 'lab.tierCap'
  let storedCap: Tier | null = null
  try { storedCap = parseTier(window.sessionStorage.getItem(CAP_KEY)) } catch { /* no storage: no memory */ }
  let tier: Tier = forcedTier ?? (REC ? 'high' : startTier({ coarse, width: window.innerWidth, height: window.innerHeight }))
  if (!forcedTier && !REC && storedCap && TIER_ORDER.indexOf(storedCap) > TIER_ORDER.indexOf(tier)) tier = storedCap
  let res: ResState = initialRes(3000) // adaptive resolution, low tier only (see quality.ts); off for ?freeze=1 and ?rec=1 like the tier step-down
  const resAdapt = !REC && params.get('freeze') !== '1'
  let autoOn = !forcedTier && !REC && params.get('freeze') !== '1'
  CHEAP.on = TIERS[tier].cheapShaders // set before any material exists

  const scene = new THREE.Scene()
  scene.background = null // a colour background would force-clear on every render() call
  let envMap = workshopEnvironment(renderer)
  scene.environment = TIERS[tier].cheapShaders ? null : envMap
  scene.environmentIntensity = 1.5

  // ---- lights: a warm key from the overhead fixtures (one shadowed spot over the table), a cool low fill, the room env for the rest ----
  const key = new THREE.SpotLight(0xffe6c8, 21, 0, 0.5, 1, 2)
  key.position.set(-0.7, ROOM.h - 0.35, 0.5)
  key.castShadow = true
  key.shadow.mapSize.set(Math.max(1, TIERS[tier].shadowMap), Math.max(1, TIERS[tier].shadowMap))
  key.shadow.camera.near = 0.5
  key.shadow.camera.far = 6
  key.shadow.bias = -0.0008
  key.shadow.normalBias = 0.03
  key.shadow.radius = 4
  scene.add(key, key.target)
  const fill = new THREE.DirectionalLight(0xb9cfff, 0.9)
  fill.position.set(-3, 1.6, 2.4)
  scene.add(fill)
  // the low tier lights every surface in its own shader (SURF_CHEAP): no lights, no shadows, no environment
  key.visible = fill.visible = !TIERS[tier].cheapShaders
  renderer.shadowMap.enabled = !TIERS[tier].cheapShaders

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

  const pipeline = new Pipeline(renderer, { ao: TIERS[tier].ao, msaa: TIERS[tier].msaa, aoSamples: REC ? 16 : TIERS[tier].aoSamples })
  pipeline.params.ao = 0.55
  pipeline.params.sharpen = 0.25
  pipeline.params.bloom = 0.12
  // everything a tier changes in the pipeline; the caller resizes afterwards (targets are rebuilt at the new size and pixel ratio)
  const tierPipeline = () => {
    const t = TIERS[tier]
    pipeline.configure({ ao: t.ao, aoSamples: REC ? 16 : t.aoSamples, aoScale: t.aoScale, msaa: t.msaa, bloom: t.bloom })
    pipeline.params.dofTaps = REC ? 40 : t.dofTaps
  }
  tierPipeline()

  const resize = () => {
    const W = window.innerWidth, H = window.innerHeight
    const dpr = Math.max(0.1, tierPixelRatio(TIERS[tier], window.devicePixelRatio, W, H) * Math.sqrt(res.scale))
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
  let glLost = false // the WebGL context is gone (see the contextlost handler below)
  let awaitFrame = false // restored, and the overlay stays until a frame has actually been drawn
  const glLostEl = document.getElementById('gl-lost')
  const render = () => {
    if (glLost) return
    pipeline.params.dofFocus = camera.position.distanceTo(controls.target)
    pipeline.params.dofAperture = TIERS[tier].dof ? 9 : 0
    renderer.info.reset()
    pipeline.render(scene, camera, simT)
    if (awaitFrame && renderer.info.render.calls > 0 && !renderer.getContext().isContextLost()) { awaitFrame = false; if (glLostEl) glLostEl.hidden = true }
  }
  let last = performance.now()
  // ---- quality tier: applying one, and the automatic step-down (driven by real frame times only) ----
  // Nothing here reloads the page or touches the scene state: it rebuilds the pipeline targets, the shadow map and the shader variants.
  // The first seconds are ignored (shader compiles and the model upload make long frames that say nothing about the device).
  let stepState: StepState = initialStep(tier, 3000)
  let onTier: () => void = () => {}
  const applyTier = (t: Tier) => {
    if (t === tier) return
    tier = t
    res = initialRes(1500)
    const spec = TIERS[t]
    tierPipeline()
    key.shadow.mapSize.set(Math.max(1, spec.shadowMap), Math.max(1, spec.shadowMap))
    key.shadow.dispose() // drops the old map; the next frame allocates one at the new size
    pipeline.shadowDirty = true
    // the light set and the shadow filter are compiled into every material: recompile them once for the new tier
    scene.environment = spec.cheapShaders ? null : envMap
    key.visible = fill.visible = !spec.cheapShaders
    renderer.shadowMap.enabled = !spec.cheapShaders
    scene.traverse((o) => { const m = (o as THREE.Mesh).material; if (m) for (const x of Array.isArray(m) ? m : [m]) x.needsUpdate = true })
    setCheapShaders(scene, spec.cheapShaders)
    resize()
    onTier()
  }
  const setAuto = (on: boolean) => { autoOn = on; stepState = initialStep(tier); onTier() }
  const feedRes = (ms: number) => {
    if (tier !== 'low' || !resAdapt) return
    const n = nextRes(res, ms)
    const changed = n.scale !== res.scale
    res = n
    if (changed) resize()
  }
  const feed = (ms: number) => {
    feedRes(ms)
    if (!autoOn) return
    const n = nextTier(stepState, ms)
    const drop = n.tier !== stepState.tier
    stepState = n
    if (drop) applyTier(n.tier)
  }
  // Tests own the clock: their frames are only the ones they inject (feedFrame), unless ?realframes=1 asks for the real path.
  const realFrames = !TEST || params.get('realframes') === '1'
  // ?freeze=1 (or __lab.freeze(true)): the frame loop still draws but no longer advances time, so a test or a capture owns the clock
  let frozen = TEST && params.get('freeze') === '1'
  if (!REC) renderer.setAnimationLoop(() => {
    const t = performance.now(), dt = Math.min((t - last) / 1000, 0.1)
    if (realFrames && hook.ready && !frozen && !glLost) feed(t - last)
    last = t
    if (!frozen) step(dt)
    render()
  })
  // ---- context loss: the iPad can reclaim graphics memory from a tab. Say so, stay usable, and rebuild when the browser gives it back. ----
  // three.js re-creates buffers, textures and programs by itself on restore; what it cannot is content that was drawn into the GPU once:
  // the environment map (a PMREM render target), the shadow map and the pipeline's targets. Those are rebuilt here.
  const reloadBtn = document.getElementById('gl-lost-reload')
  canvas.addEventListener('webglcontextlost', (e) => {
    e.preventDefault() // lets the browser restore the context
    glLost = true
    awaitFrame = false
    stepState = initialStep(tier) // no frame time is fed while it is lost; nothing to step down on
    if (glLostEl) glLostEl.hidden = false
  })
  canvas.addEventListener('webglcontextrestored', () => {
    try {
      if (NOISE3D.value) NOISE3D.value.needsUpdate = true // uploaded again on next use
      envMap.dispose()
      envMap = workshopEnvironment(renderer)
      scene.environment = TIERS[tier].cheapShaders ? null : envMap
      key.shadow.dispose()
      pipeline.shadowDirty = true
      scene.traverse((o) => { const m = (o as THREE.Mesh).material; if (m) for (const x of Array.isArray(m) ? m : [m]) x.needsUpdate = true })
      resize() // the pipeline's targets and shaders, at the current size
      // memory pressure is the likely cause: one tier down, for this session
      const lower = TIER_ORDER[TIER_ORDER.indexOf(tier) + 1]
      if (autoOn && lower) {
        applyTier(lower)
        try { window.sessionStorage.setItem(CAP_KEY, lower) } catch { /* no storage */ }
      }
      stepState = initialStep(tier, 3000)
      last = performance.now()
      glLost = false
      awaitFrame = true // the overlay hides on the first frame that draws
    } catch (err) {
      console.error('context restore failed', err)
    }
  })
  reloadBtn?.addEventListener('click', () => {
    const u = new URL(location.href)
    const op = hook.selected()
    if (op) u.searchParams.set('op', op)
    location.replace(u.toString()) // same page, same step
  })
  const loseExtension = renderer.getContext().getExtension('WEBGL_lose_context') // fetched now: a lost context answers null
  const loseExt = () => loseExtension
  hook.contextLost = () => glLost
  hook.loseContext = () => { const x = loseExt(); if (!x) return false; x.loseContext(); return true }
  hook.restoreContext = () => { const x = loseExt(); if (!x) return false; x.restoreContext(); return true }
  hook.freeze = (on: boolean) => { frozen = on }
  hook.advance = (s: number) => { step(s); render() }
  hook.resScale = () => res.scale
  hook.tier = () => tier
  hook.setTier = (t: Tier) => { autoOn = false; if (t === tier) onTier(); else applyTier(t) }
  hook.auto = () => autoOn
  hook.setAuto = setAuto
  hook.feedFrame = feed
  hook.stats = () => ({ calls: renderer.info.render.calls, triangles: renderer.info.render.triangles, pixels: pipeline.w * pipeline.h })

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
    // The data (graph.json, config.json, models/) sits at the site root: beside this page when the lab is served at /.
    const DATA = document.querySelector<HTMLMetaElement>('meta[name="data-base"]')?.content || './'
    const [graph, cfg] = await Promise.all([
      fetch(DATA + 'graph.json').then((r) => { if (!r.ok) throw new Error(`graph.json ${r.status}`); return r.json() as Promise<Graph> }),
      fetch(DATA + 'config.json').then((r) => { if (!r.ok) throw new Error(`config.json ${r.status}`); return r.json() as Promise<Cfg> }),
    ])
    // the fuselage mass ledger (core.ledger.fuselage_ledger_json) ships beside graph.json; a site without one says so in the CG row
    const ledgerP: Promise<LedgerLite | null> = fetch(DATA + 'ledger.json').then((r) => (r.ok ? (r.json() as Promise<LedgerLite>) : null)).catch(() => null)
    const gltf = await new GLTFLoader().loadAsync(DATA + cfg.model)
    const fuseData = graph.layup?.fuselage ?? null
    // the fuselage's part nodes and their later shapes (stages: the carve, the canard opening, the access holes) group like components
    const fuseNodes = new Set([...Object.values(fuseData?.parts ?? {}).map((r) => r.node), ...Object.values(fuseData?.stages ?? {}).flat().map((st) => st.node)])
    const allParts = mergeModel(gltf.scene, graph, fuseNodes)
    // the canard, the fuselage box and the main gear share the glb; everything below `root` is the canard, exactly as before the fuselage came
    const isFuse = (cid: string) => cid.startsWith('fuselage.') || cid.startsWith('gear.')
    const parts = allParts.filter((p) => !isFuse(p.cid))
    const fuseParts = allParts.filter((p) => isFuse(p.cid)).map((p) => ({ ...p, name: p.node ?? p.cid }))
    const ledger = await ledgerP
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
    // ---- the fuselage station (chapters 4-6): its own corner of the shop, out of every canard shot ----
    const bay = fuseData && fuseParts.length ? new FuselageBay(fuseParts, fuseData, graph) : null
    if (bay) scene.add(bay.group)
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
      if (bay?.stepTurn(dt)) pipeline.shadowDirty = true // the fuselage box turning over (its own clock, sim time)
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
      for (const id of Object.keys(rig.shots)) if (id !== 'home' && id !== 'cutclose' && !fuseShotIds.has(id)) delete rig.shots[id]
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
    // the fuselage's shots: one per chapter 4-6 op, aimed where its parts are for that op (src/fuseShots.ts), and its own home view
    const fuseOpIds = graph.order.filter((id) => FUSE_CHAPTERS.has(graph.ops.find((o) => o.id === id)?.chapter ?? -1))
    const fuseShotIds = new Set<string>(bay ? [...fuseOpIds, 'fhome', 'fcut', 'ffinal', ...Object.values(FUSE_CUTS).map((fs) => `fcut${fs}`)] : [])
    // what the canard subject shows of the fuselage corner: the box as chapter 6 leaves it, on the jig (FuselageBay.paint `backdrop`)
    const canardBackdrop = fuseOpIds.filter((id) => graph.ops.find((o) => o.id === id)?.chapter === 6).at(-1) ?? null
    if (bay) {
      Object.assign(rig.shots, bay.shots(fuseOpIds, LAB_FOV))
      const hb = bay.homeBox()
      // aimed a little toward the nose end: the dock covers the frame's left third
      // each close shot is of the box as its chapter leaves it (that chapter's last op), never the finished airplane on its gear
      const chapterEnd = (ch: number) => fuseOpIds.filter((id) => graph.ops.find((o) => o.id === id)?.chapter === ch).at(-1) ?? null
      rig.shots.fcut = bay.cutShot(FUSE_CUT_FS, LAB_FOV, chapterEnd(6))
      for (const [ch, fs] of Object.entries(FUSE_CUTS)) rig.shots[`fcut${fs}`] = bay.cutShot(fs, LAB_FOV, chapterEnd(Number(ch)), FUSE_CUT_VIEW[fs]) // one close shot per film that ends on a station cut
      rig.shots.fhome = fitShot(hb, hb.getCenter(new THREE.Vector3()).add(new THREE.Vector3(-0.22, -0.05, 0)), new THREE.Vector3(-0.22, 0.6, 0.77).normalize(), 30, 1.6, 0.62)
      // the finished box on its own feet on the floor beside the bench: from the room side and a little aft, the nose kept clear of the dock
      const fb = bay.finishedBox()
      rig.shots.ffinal = fitShot(fb, fb.getCenter(new THREE.Vector3()).add(new THREE.Vector3(FINAL_SHOT.dx, FINAL_SHOT.dy, 0)), new THREE.Vector3(...FINAL_SHOT.dir).normalize(), 30, 1.6, FINAL_SHOT.fill)
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
    // what the lab is building. The canard is the default; the choice is remembered like the other view settings (guarded storage).
    let subject: Subject = 'canard'
    const lastSel: Record<Subject, string | null | undefined> = { canard: undefined, fuselage: undefined }
    let bayStale = true // the canard subject shows the finished box; repaint it only when something it depends on changed
    // ---- build state: recomputed from scratch with visibleSet on every change (op, lay, variant, ghost), never patched ----
    // The look of each mesh (unroll, wet-out front, cure) is plyPhase(op, lay, t), t = seconds since `lay` last changed. All time
    // comes through step(dt), so __lab.advance(s) reproduces any frame.
    const GHOST_KEY = 'longez.ghost'
    let ghost = false
    try { ghost = storage?.getItem(GHOST_KEY) === '1' } catch { ghost = false }
    graph.__ghost = ghost
    const infos: MeshInfo[] = merged.map((m) => ({ name: m.node ?? m.cid, component: m.cid, ply: m.ply }))
    const canardCount = (id: string | null) => (id ? Object.values(graph.plies ?? {}).flat().filter((r) => r.op === id).length : 0)
    // op ids never repeat across subjects, so one count serves both (a canard op has no fuselage plies and back)
    const opCount = (id: string | null) => canardCount(id) + (bay ? bay.opCount(id) : 0)
    let lay = 0, layT = DONE_T, playing = false, tourRate = 1
    let bstate = new Map<string, BuildState>()
    let opIdx = new Map<string, number>()
    const phases = new Map<string, Phase>()
    let shadowSig = ''
    let bayFsig = ''
    // ?hide=<name prefix>[,..] keeps those meshes out of the scene (for close-ups of work hidden inside the core)
    const hide = (params.get('hide') ?? '').split(',').filter(Boolean)
    const recompute = () => {
      opIdx = new Map(visibleOps(graph, variant).map((o, i) => [o.id, i]))
      const mine = subject === 'canard' ? infos : bay?.infos ?? []
      bstate = selected && opIdx.has(selected)
        ? visibleSet(graph, variant, selected, lay, mine)
        : new Map<string, BuildState>(mine.map((i) => [i.name, 'built']))
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
      // the fuselage: its own build state in its subject; the finished box on its jig while the canard is the subject
      if (bay && (subject === 'fuselage' || bayStale)) {
        bayFsig = subject === 'fuselage' ? bay.paint(bstate, selected, lay, layT, ghost, opIdx) : bay.paint(null, null, lay, layT, ghost, opIdx, canardBackdrop)
        bayStale = false
      }
      sig += bayFsig
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
        o.visible = subject === 'canard' && pathVisible(o.p, bstate)
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
      bayStale = true
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
      if (bay && fglow > 0) { fglow *= Math.exp(-dt * 4); if (fglow < 0.01) fglow = 0 }
      if (bay && fsecOn) { bay.setStation(true, fsecFs, fglow); if (dt > 0 && fglow > 0) pipeline.shadowDirty = true }
    }
    // the fuselage's station cut (a constant-FS plane in the box's frame; forward removed, aft kept), with its own glow and state
    const FS_MIN = 22, FS_MAX = 125.5
    let fsecOn = false, fsecFs = 70, fglow = 0
    const setFuseSection = (on: boolean, fs: number) => {
      const was = fsecOn
      fsecOn = on && !!bay
      fsecFs = Math.max(FS_MIN, Math.min(fs, FS_MAX))
      fglow = 1
      bay?.setStation(fsecOn, fsecFs, fglow)
      if (fsecOn !== was) paint()
      pipeline.shadowDirty = true
      ui.setSection(fsecOn, fsecFs)
      updateReadout()
    }
    const setSection = (on: boolean, bl: number) => {
      if (subject === 'fuselage') { setFuseSection(on, bl); return }
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
    const fuseCapped = () => (bay && fsecOn ? bay.capped(fsecFs, (n) => bstate.get(n)) : [])
    const updateFuseReadout = () => {
      if (!bay) return
      const n = opCount(selected)
      const cnt = new Map<string, number>()
      for (const m of bay.meshes) {
        const st = bstate.get(m.name)
        if (!m.row || (st !== 'built' && st !== 'current')) continue
        cnt.set(m.row.cloth, (cnt.get(m.row.cloth) ?? 0) + 1)
      }
      const cloth = [...cnt].sort(([a], [b]) => (CLOTH_ORDER.indexOf(a) + 1 || 99) - (CLOTH_ORDER.indexOf(b) + 1 || 99) || a.localeCompare(b)).map(([k, c]) => `${k} ${c}`).join(' · ')
      let layers = 'Turn on the section to list the layers there'
      if (fsecOn) {
        const cap = fuseCapped()
        const alive = new Set(cap.filter((m) => m.row).map((m) => m.name))
        layers = stationSummary(bay.data.parts, cap.filter((m) => !m.row).map((m) => m.part), stationLayers(bay.data.nodes, fsecFs, alive))
      }
      ui.setReadout({ station: fsecOn ? fmtFs(fsecFs) : 'Section off', layers, plies: n ? `${lay} / ${n}` : null, cloth: cloth || 'none yet' })
      ui.setCg(cgRow(ledger))
      ui.setGround(groundRow(ledger))
    }
    const updateReadout = () => {
      if (subject === 'fuselage') { updateFuseReadout(); return }
      ui.setCg(null)
      ui.setGround(null)
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
          if (subject !== 'canard' || !(tourOv.labels ?? labelsOn) || !a || !mine.some(isBuilt)) return 0
          wp.copy(a.p).applyMatrix4(root.matrixWorld)
          wn.copy(a.n).transformDirection(root.matrixWorld)
          return wn.dot(cp.copy(camera.position).sub(wp)) > 0 ? 1 : 0 // the surface faces away from the camera: hide
        },
      })
    }
    // the fuselage's part labels: every part the selected op works on, and every fitted (representational) part in view, so a fitted
    // shape is never on screen without its "fitted shape" label. The label text comes from the export, which derives it from fidelity.
    // They collide by priority (logic/declutter.ts): the selected op's parts win, then the parts the station cut passes through, then
    // fitted shapes; a label with no room collapses to its dot, and none may sit under a card. The canard's labels keep their nudge.
    // and none may run off the screen's edges (a pill is centred on its anchor, so near an edge it would be cut off)
    const cardRects = () => {
      const W = window.innerWidth, H = window.innerHeight, far = 1e5
      return ['controls', 'dock', 'opbar', 'viewpop'].map((id) => document.getElementById(id)).filter((e): e is HTMLElement => !!e && !e.hidden)
        .map((e) => { const r = e.getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom } }).filter((r) => r.r > r.l && r.b > r.t)
        .concat([{ l: -far, t: -far, r: 0, b: far }, { l: W, t: -far, r: far, b: far }, { l: -far, t: -far, r: far, b: 0 }, { l: -far, t: H, r: far, b: far }])
    }
    const flabels = new Labels(document.getElementById('labels') as HTMLElement, camera, { obstacles: cardRects })
    const fwp = new THREE.Vector3(), fbox = new THREE.Box3()
    if (bay) {
      const byPart = new Map<string, typeof bay.meshes[number]>()
      for (const m of bay.meshes) if (!m.row) byPart.set(m.part, m)
      // a part is there when it is drawn (the wheels are the bay's own meshes, shown on the finished box only)
      const present = (p: string) => (p === 'wheels' ? bay.wheels.visible : !!(byPart.get(p) && bay.shown(byPart.get(p)!.name) && ['built', 'current'].includes(bstate.get(byPart.get(p)!.name) ?? '')))
      // where along the part (0 = its forward end) the label sits: the long parts are spread out so their pills do not stack at mid-box
      const along = (part: string) => (part.startsWith('side_') ? 0.72 : part.startsWith('top_longeron') ? 0.3 : part === 'bottom' ? 0.42 : 0.5)
      for (const [part, m] of byPart) {
        const row = bay.data.parts[part]
        const inJig = () => bay.shown(m.name) === m.jig
        const cutHere = () => fsecOn && inJig() && crossedByStationCut(row, fsecFs)
        const op = () => (selected ? graph.ops.find((o) => o.id === selected) ?? null : null)
        const at = () => {
          const mesh = bay.shown(m.name)
          if (!mesh) return null
          fbox.setFromObject(mesh)
          let x = fbox.min.x + (fbox.max.x - fbox.min.x) * along(part)
          if (fsecOn && inJig()) x = Math.max(x, fsToX(fsecFs) + 0.5 * INCH) // on the kept side of the cut, never over the gap
          return fwp.set(x, fbox.max.y + 0.02, (fbox.min.z + fbox.max.z) / 2)
        }
        flabels.add({
          id: m.name, text: row.label, color: bay.labelColor(m), cls: m.hatch ? 'fitted' : '',
          at,
          vis: () => {
            if (subject !== 'fuselage' || !(tourOv.labels ?? labelsOn)) return 0
            const st = bstate.get(m.name)
            if ((st !== 'built' && st !== 'current') || !bay.shown(m.name)) return 0
            if (fsecOn && inJig() && removedByStationCut(row, fsecFs)) return 0 // the cut took this part away: its label must not hover over the gap
            const o = op()
            // the home view (nothing selected): one label per family of parts (logic/fuselage.ts LABEL_FAMILY); the cut's face keeps its words
            if (!o) return homeLabel(part, present) || cutHere() ? 1 : 0
            return m.hatch || o.components.includes(m.cid) || cutHere() ? 1 : 0
          },
          priority: () => labelPriority({ inOp: !!op()?.components.includes(m.cid), cut: cutHere(), fitted: m.hatch }),
          tie: () => row.fs_max - row.fs_min, // equal priority: the more specific (shorter) part keeps its words
        })
      }
    }
    // the main wheels on the finished box: fitted (logic/fuselage.ts FITTED_TYRE_OD), so labelled as such; at the home view this one
    // label speaks for the whole main gear (the strut, extrusions, tubes and axles are still drawn and striped)
    if (bay) {
      flabels.add({
        id: 'gear.wheels', text: 'Main gear and wheels (fitted shape)', color: '#' + HATCH_COLOR.toString(16).padStart(6, '0'), cls: 'fitted',
        at: () => bay.wheelAnchor(fwp)?.add(new THREE.Vector3(0, 0.02, 0)) ?? null,
        vis: () => (subject === 'fuselage' && (tourOv.labels ?? labelsOn) && bay.wheels.visible ? 1 : 0),
        priority: () => labelPriority({ inOp: false, cut: false, fitted: true }),
        tie: () => 0,
      })
    }
    // the gear positioning's marks (plans-1980:p50 figure 1A): the 15 in from the datum board to the axle line, and the axle station
    if (bay?.markAt && bay.data.gear_marks) {
      const gm = bay.data.gear_marks
      const mk = (id: string, text: string, p: THREE.Vector3) => flabels.add({
        id, text, color: '#2fc4ff', cls: 'mark',
        at: () => fwp.copy(p).applyMatrix4(bay.jigFrame.matrixWorld),
        vis: () => (subject === 'fuselage' && (tourOv.labels ?? labelsOn) && bay.marksShown ? 1 : 0),
        priority: () => 4, // the op's own measurement: never dropped for a part's name
        tie: () => 0,
      })
      mk('mark.dim', MARK_TEXT.dim(gm.axle_fwd_of_board_in), bay.markAt.dim)
      mk('mark.axle', MARK_TEXT.axle(gm.axle_fs), bay.markAt.axle)
    }
    stepLabels = (dt) => { camera.updateMatrixWorld(); labels.update(window.innerWidth, window.innerHeight, dt); flabels.update(window.innerWidth, window.innerHeight, dt) }
    const setLabels = (on: boolean) => {
      labelsOn = on
      try { storage?.setItem(LABELS_KEY, on ? '1' : '0') } catch { /* per-viewer convenience only */ }
      ui.setLabels(on)
    }
    buildShots(variant)
    // the fuselage's home: the finished box on its own feet when nothing is selected, else the station
    const homeShot = () => (subject === 'canard' ? 'home' : selected === null && bay?.pose === 'on-gear' ? 'ffinal' : 'fhome')
    const select = (id: string | null, fly = true) => {
      selected = id
      lastSel[subject] = id
      ui.setSelected(id)
      // the fuselage box turns over (animated, as the canard's turnover) when the step crosses the bottom bond, either way
      if (bay && subject === 'fuselage') { bay.setPose(bay.poseFor(id), fly); aimKey() }
      openOp()
      if (subject === 'canard') setPose(orientation(graph, variant, id), fly)
      goto(id && rig.shots[id] ? id : homeShot(), fly)
    }
    const subjectOps = () => (subject === 'canard' ? barOps(graph, variant) : fuseBarOps(graph, variant))
    // the key light follows the subject: over the canard's table as it always was, or over the fuselage station (a wider cone)
    const KEY_CANARD = { pos: key.position.clone(), target: key.target.position.clone(), angle: key.angle, penumbra: key.penumbra, intensity: key.intensity }
    const aimKey = () => {
      if (subject === 'canard' || !bay) {
        key.position.copy(KEY_CANARD.pos); key.target.position.copy(KEY_CANARD.target); key.angle = KEY_CANARD.angle; key.penumbra = KEY_CANARD.penumbra
        key.intensity = KEY_CANARD.intensity
      } else if (bay.pose === 'on-gear') { // the finished box on the floor beside the bench: the key moves over it
        key.position.set(STATION.jig.x + 0.2, ROOM.h - 0.35, (STATION.jig.z + STATION.floor.z) / 2 + 0.5)
        key.target.position.set(STATION.jig.x, 0.6, (STATION.jig.z + STATION.floor.z) / 2 + 0.35)
        key.angle = 0.92; key.penumbra = 0.75
        key.intensity = KEY_CANARD.intensity * keyScale(bay.pose)
      } else {
        key.position.set(STATION.table.x + 0.2, ROOM.h - 0.35, (STATION.table.z + STATION.jig.z) / 2 + 0.55)
        key.target.position.set(STATION.table.x, 1.0, (STATION.table.z + STATION.jig.z) / 2)
        key.angle = 0.92; key.penumbra = 0.75
        key.intensity = KEY_CANARD.intensity * keyScale(bay.pose)
      }
      key.target.updateMatrixWorld()
      pipeline.shadowDirty = true
    }
    const secScale = () => (subject === 'canard'
      ? { min: 0, max: semi, fmt: fmtBl, label: 'Section station in buttock line inches' }
      : { min: FS_MIN, max: FS_MAX, fmt: fmtFs, label: 'Section station in fuselage station inches' })
    const setSubject = (s: Subject, fly = true, save = true) => {
      if (!bay && s === 'fuselage') return
      if (s === subject) return
      subject = s
      if (save) try { storage?.setItem(SUBJECT_KEY, s) } catch { /* per-viewer convenience only */ }
      canardRoot.visible = s === 'canard'
      ui.setSubject(s)
      if (layupN || bay) ui.scaleSection(secScale(), s === 'canard' ? secOn : fsecOn, s === 'canard' ? secBl : fsecFs)
      aimKey()
      bayStale = true
      const ops = subjectOps()
      ui.setOps(ops)
      const want = lastSel[s]
      select(want !== undefined && (want === null || ops.some((o) => o.id === want)) ? want : ops[0]?.id ?? null, fly)
      syncPaths()
    }
    // ---- the tour: src/director.ts scripts the page's own controls with a cursor. A click the director dispatches is told from a person's by
    // director.busy; anything a person does (op chip, variant, scrubber, Play, the camera, Escape, Tour again) ends the tour where it stands. ----
    let orb: { r: number; y: number; a0: number } | null = null
    const director = new Director({
      act(name, arg, op) {
        if (name === 'reset') { stopPlay(); select(null, !REC); tourOv.labels = true; tourOv.paths = true; syncPaths(); if (subject === 'canard' ? secOn : fsecOn) setSection(false, subject === 'canard' ? secBl : fsecFs) }
        else if (name === 'finish') { stopPlay(); select(op ?? null, true) }
        else if (name === 'cutclose') goto(subject === 'canard' ? 'cutclose' : arg !== undefined && rig.shots[`fcut${arg}`] ? `fcut${arg}` : 'fcut', true)
        else if (name === 'closeup') goto(subject === 'canard' ? 'cutclose' : homeShot(), true)
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
      if (before) { const b = before; before = null; setSection(b.secOn, b.secBl) } // the subject's own section (a tour never changes subject)
      syncPaths()
      ui.setTouring(false)
    }
    const stopTour = () => {
      if (!director.active) return
      director.stop()
      stopPlay() // the film pressed Play for the person: stopping the film leaves the plies where they are, not still laying
      endTour()
    }
    director.onEnd = endTour
    const startTour = (chapter?: number) => {
      if (subject === 'fuselage' && bay) {
        stopPlay()
        before = { secOn: fsecOn, secBl: fsecFs }
        director.load(fuselageTour(graph as never, variant, (id) => bay.opCount(id), chapter ? [chapter] : fuselageTourChapters(graph as never, variant, selected)))
        director.start(simT)
        tourRate = TOUR_BUILD_RATE
        ui.setTouring(true)
        return
      }
      const ch = chapter ?? tourChapter(graph as never, variant, selected)
      if (ch === undefined) return // nothing to build in this variant
      stopPlay()
      before = { secOn, secBl }
      director.load(chapterTour(graph as never, variant, ch))
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
        if (subject !== 'canard') return // the variant only changes the canard; its bar is rebuilt when the canard is chosen again
        const ops = barOps(graph, v)
        ui.setOps(ops)
        select(ops.some((o) => o.id === selected) ? selected : (ops[0]?.id ?? null))
      },
      onSubject(s) { if (s !== subject) { userAct(); setSubject(s) } },
      onHome: () => goto(homeShot(), true),
      onTour: () => (director.active ? stopTour() : startTour()),
      onSelect: (id) => { userAct(); select(id) },
      onGhost: (on) => { userAct(); setGhost(on) },
      onScrub: (n) => { userAct(); setLay(n) },
      onPlay: () => { userAct(); togglePlay() },
      onSection: (on, bl) => { userAct(); setSection(on, bl) },
      onLabels: (on) => { userAct(); setLabels(on) },
      onPaths: (on) => { userAct(); setPaths(on) },
      onQuality: (q) => { if (q === 'auto') setAuto(true); else hook.setTier(q) },
    }, store)
    ui.setGhost(ghost)
    onTier = () => ui.setQuality(tier, autoOn)
    onTier()
    ui.setLabels(labelsOn)
    ui.setPaths(pathsOn)
    if (layupN) ui.initSection(semi, secBl)
    ui.setVariant(variant)
    ui.setSubject('canard')
    const subjEl = document.getElementById('subject')
    if (subjEl) subjEl.hidden = !bay // no fuselage in this build: no choice to offer
    const want = params.get('op')
    let stored: string | null = null
    try { stored = storage?.getItem(SUBJECT_KEY) ?? null } catch { stored = null }
    const wantOp = graph.ops.find((o) => o.id === want)
    const startSubject: Subject = !bay ? 'canard' : wantOp ? (FUSE_CHAPTERS.has(wantOp.chapter) ? 'fuselage' : 'canard') : parseSubject(stored)
    if (startSubject === 'fuselage') {
      lastSel.fuselage = fuseBarOps(graph, variant).find((o) => o.id === want)?.id
      setSubject('fuselage', false, false)
    } else {
      const firstOps = barOps(graph, variant)
      ui.setOps(firstOps)
      select(firstOps.find((o) => o.id === want)?.id ?? firstOps[0]?.id ?? null, false)
    }

    if (bay) hook.meshNames = () => [...merged.map((m) => m.node ?? m.cid), ...bay.meshes.map((m) => m.name)]
    hook.subject = () => subject
    hook.setSubject = (s) => setSubject(s)
    hook.placement = () => {
      const out: Record<string, 'table' | 'jig' | 'none'> = {}
      for (const m of bay?.meshes ?? []) if (!m.row) out[m.part] = m.jig.visible ? 'jig' : m.table.visible ? 'table' : 'none'
      return out
    }
    hook.jigPose = () => bay?.pose ?? 'upright'
    hook.fuseShots = () => Object.fromEntries([...fuseShotIds].map((id) => [id, snap(id)!]))
    hook.cg = () => cgRow(ledger)
    hook.ground = () => groundRow(ledger)
    hook.fuseToWorld = (q) => (bay ? new THREE.Vector3(q[0], q[1], q[2]).applyMatrix4(bay.jigFrame.matrixWorld).toArray() : q)
    hook.fuseRestToWorld = (q, p) => (bay ? new THREE.Vector3(q[0], q[1], q[2]).applyMatrix4(bay.restMatrix(p as JigPose)).toArray() : q)
    hook.gearMarks = () => {
      const gm = bay?.data.gear_marks
      if (!bay || !gm || !bay.markAt) return null
      const w = (v: THREE.Vector3) => v.clone().applyMatrix4(bay.jigFrame.matrixWorld).toArray()
      return { shown: bay.marksShown, axleFs: gm.axle_fs, boardFs: gm.board_fs, dimText: MARK_TEXT.dim(gm.axle_fwd_of_board_in), axleText: MARK_TEXT.axle(gm.axle_fs), dimModel: bay.markAt.dim.toArray(), axleModel: bay.markAt.axle.toArray(), dimWorld: w(bay.markAt.dim), axleWorld: w(bay.markAt.axle) }
    }
    hook.fuseTurning = () => !!bay?.turning
    hook.fuseFloor = () => {
      if (!bay) return null
      bay.group.updateMatrixWorld(true)
      const arr = (b: THREE.Box3) => [b.min.toArray(), b.max.toArray()]
      const gear: Record<string, number[][]> = {}
      for (const m of bay.meshes) if ((m.cid.startsWith('gear.') || m.cid === 'fuselage.gear_extrusions') && !m.ply && m.jig.visible) gear[m.name] = arr(new THREE.Box3().setFromObject(m.jig, true))
      if (bay.wheels.visible) gear['gear.wheels'] = arr(new THREE.Box3().setFromObject(bay.wheels, true))
      return { bench: arr(bay.benchBox()), gear, noseStand: bay.noseStand.visible }
    }
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
      if (name === 'gear.wheels' && bay) { // the bay's own fitted wheels (no glb node): striped like every fitted part
        const ms = bay.wheels.children.map((w) => (w as THREE.Mesh).material as THREE.Material)
        return { kind: 'part', angles: [], wet: 0, hatch: ms.length > 0 && ms.every((x) => !!x.userData.hatch), fidelity: 'representational' }
      }
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      if (!m) {
        const f = bay?.meshes.find((x) => x.name === name)
        if (!f) return null
        const mat = (f.jig.visible || !f.table.visible ? f.jigMat : f.tableMat)
        const fi = mat.userData.comp as { wet: number } | undefined
        return { kind: f.spec.kind, angles: f.spec.angles.slice(), wet: fi?.wet ?? 0, hatch: !!mat.userData.hatch, fidelity: f.fidelity }
      }
      const info = (m.mesh.material as THREE.Material).userData.comp as { wet: number } | undefined
      return { kind: m.spec.kind, angles: m.spec.angles.slice(), wet: info?.wet ?? 0 }
    }
    hook.setWet = (name, w) => {
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      if (m) setWet(m.mesh.material as THREE.Material, w)
      const f = bay?.meshes.find((x) => x.name === name)
      if (f) { setWet(f.jigMat, w); setWet(f.tableMat, w) }
    }
    hook.meshBox = (name) => {
      const m = merged.find((x) => (x.node ?? x.cid) === name)
      const mesh = m ? m.mesh : bay?.shown(name) ?? null
      if (!mesh) return null
      const bx = new THREE.Box3().setFromObject(mesh)
      return [bx.min.toArray(), bx.max.toArray()]
    }
    hook.state = () => Object.fromEntries(bstate)
    hook.phase = (name) => phases.get(name) ?? bay?.phases.get(name) ?? null
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
    hook.labels = () => (subject === 'canard' ? labels.stats() : flabels.stats())
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
      const f = bay?.meshes.find((x) => x.name === name)
      if (!ms.length && f) { const b = f.jig.geometry.boundingBox!; return { min: b.min.toArray(), max: b.max.toArray() } } // the box's frame: x = FS
      if (!ms.length) return null
      const bx = new THREE.Box3()
      for (const m of ms) bx.union(m.mesh.geometry.boundingBox!)
      return { min: bx.min.toArray(), max: bx.max.toArray() }
    }
    hook.cut = () => {
      if (subject === 'fuselage' && bay) {
        const cap = fuseCapped()
        const keptX = (x: number) => bay.cut.world.distanceToPoint(new THREE.Vector3(x, 0, 0).applyMatrix4(bay.jigFrame.matrixWorld)) >= 0
        const capVis = cap.filter((m) => Array.isArray(m.jig.material) && (m.jigMat.userData.back as THREE.Material | undefined)?.userData.u.uGhost.value === 0).map((m) => m.name)
        return {
          enabled: fsecOn, bl: fsecFs, fs: fsecFs, planeConstant: fsecOn ? bay.cut.local.constant : null,
          keepsOutboard: false, removesInboard: false, keepsAft: fsecOn && keptX(fsecFs + 5), removesForward: fsecOn && !keptX(fsecFs - 5),
          cappedNodes: cap.map((m) => m.name), capsVisible: capVis.length, capNodesVisible: capVis,
          clipped: fsecOn ? bay.meshes.filter((m) => m.jig.visible && m.jig.geometry.boundingBox!.min.x < fsecFs).length : 0,
        }
      }
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
        /** begin the film and return its length in seconds; the recorder's `canard` film is the Roncz chapter 30, `fuselage6`, `fuselage8` and `fuselage9` the fuselage's chapters 6, 8 and 9 */
        start(name: string) {
          const fuse = /^fuselage([689])$/.exec(name)
          if (name !== 'canard' && !fuse) throw new Error(`no film called ${name}`)
          if (fuse) { setSubject('fuselage', false, false); startTour(Number(fuse[1])) } // the box's own subject (never saved), its chapter tour
          else startTour(CHAPTER)
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
