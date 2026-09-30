import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { Pipeline } from './render/pipeline'
import { makeNoise3D, NOISE3D } from './core/noise'
import { CutState } from './core/cut'
import { surf } from './core/materials'
import { workshopEnvironment } from './scene/env'

const INCH = 0.0254
const params = new URLSearchParams(location.search)
const TEST = params.get('test') === '1'
const statusEl = document.getElementById('status') as HTMLElement
const setStatus = (msg: string | null, err = false) => {
  statusEl.hidden = msg === null
  statusEl.textContent = msg ?? ''
  statusEl.classList.toggle('err', err)
}

interface Graph { components: Record<string, unknown>; layup?: { nodes?: Record<string, { cloth?: string }> } | null }
interface Cfg { model: string }
interface LabHook { ready: boolean; meshNames(): string[]; stats(): { calls: number; triangles: number }; advance(seconds: number): void }
declare global { interface Window { __lab?: LabHook } }

const hook: LabHook = { ready: false, meshNames: () => [], stats: () => ({ calls: 0, triangles: 0 }), advance: () => {} }
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
  renderer.shadowMap.type = THREE.PCFShadowMap
  renderer.shadowMap.autoUpdate = false
  renderer.localClippingEnabled = true

  const coarse = matchMedia('(pointer: coarse)').matches
  const q = params.get('q') || (coarse ? 'mid' : 'high')
  const quality = q === 'low' || q === 'mid' ? q : 'high'

  const scene = new THREE.Scene()
  scene.background = null // a colour background would force-clear on every render() call
  scene.environment = workshopEnvironment(renderer)
  scene.environmentIntensity = 1.0

  // ---- lights ----
  const key = new THREE.DirectionalLight(0xffe9cf, 3.2)
  key.position.set(2.6, 4.4, 2.2)
  key.castShadow = true
  key.shadow.mapSize.set(2048, 2048)
  const sc = key.shadow.camera
  sc.left = -2.4; sc.right = 2.4; sc.top = 2.4; sc.bottom = -2.4; sc.near = 0.5; sc.far = 12
  key.shadow.bias = -0.0004
  key.shadow.normalBias = 0.01
  key.shadow.radius = 4
  scene.add(key, key.target)
  const fill = new THREE.DirectionalLight(0xbcd0ff, 0.6)
  fill.position.set(-3, 2.2, -2.5)
  scene.add(fill)

  // ---- floor and pedestal ----
  const floor = new THREE.Mesh(new THREE.CircleGeometry(40, 96), surf({ color: 0x5c5148, metalness: 0, roughness: 0.66, detail: 1.4, colorVar: 0.18, roughVar: 0.5 }))
  floor.rotation.x = -Math.PI / 2
  floor.receiveShadow = true
  scene.add(floor)
  // A dark warm dome so the floor's edge never meets a black void (the real backdrop is a later task).
  const dc = document.createElement('canvas')
  dc.width = 4; dc.height = 128
  const dg = dc.getContext('2d')!
  const dl = dg.createLinearGradient(0, 0, 0, 128)
  dl.addColorStop(0, '#1b1612'); dl.addColorStop(0.5, '#2a231d'); dl.addColorStop(0.52, '#3a3128'); dl.addColorStop(1, '#3a3128')
  dg.fillStyle = dl; dg.fillRect(0, 0, 4, 128)
  const dt = new THREE.CanvasTexture(dc); dt.colorSpace = THREE.SRGBColorSpace
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.MeshBasicMaterial({ map: dt, side: THREE.BackSide, depthWrite: false })))

  const plinthProfile = [[0, 0], [0.34, 0], [0.34, 0.03], [0.31, 0.05], [0.31, 0.09], [0.2, 0.12], [0.16, 0.16], [0.16, 0.7], [0.19, 0.74], [0.19, 0.78], [0.27, 0.8], [0.27, 0.84], [0, 0.84]]
  const plinth = new THREE.Mesh(new THREE.LatheGeometry(plinthProfile.map(([x, y]) => new THREE.Vector2(x, y)), 64),
    surf({ color: 0x2b2926, metalness: 0.15, roughness: 0.55, detail: 2.0, colorVar: 0.1, roughVar: 0.4 }))
  plinth.castShadow = true
  plinth.receiveShadow = true
  scene.add(plinth)

  // ---- camera ----
  const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.05, 90)
  camera.position.set(3.4, 2.2, 3.0)
  const controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true
  controls.dampingFactor = 0.075
  controls.minDistance = 0.4
  controls.maxDistance = 9
  controls.maxPolarAngle = Math.PI * 0.49
  controls.rotateSpeed = 0.7

  const pipeline = new Pipeline(renderer, { ao: quality !== 'low', msaa: quality === 'low' ? 0 : 4, aoSamples: 8 })
  pipeline.aoScale = 0.4
  pipeline.params.dofTaps = 14
  pipeline.params.sharpen = 0.25
  pipeline.params.bloom = 0.05
  const dofOn = quality === 'high'

  const resize = () => {
    const W = window.innerWidth, H = window.innerHeight
    const dpr = Math.min(window.devicePixelRatio || 1, quality === 'low' ? 1 : 1.75)
    renderer.setPixelRatio(dpr)
    renderer.setSize(W, H, false)
    camera.aspect = W / H
    camera.updateProjectionMatrix()
    pipeline.setSize(Math.round(W * dpr), Math.round(H * dpr))
  }
  window.addEventListener('resize', resize)
  resize()

  // ---- deterministic time ----
  let simT = 0
  const step = (dt: number) => { simT += dt; controls.update() }
  const render = () => {
    pipeline.params.dofFocus = camera.position.distanceTo(controls.target)
    pipeline.params.dofAperture = dofOn ? 9 : 0
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
  const root = new THREE.Group()
  root.scale.setScalar(INCH)
  scene.add(root)
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

    // Sit the canard on the plinth, centred, and frame it large.
    root.updateMatrixWorld(true)
    const box = new THREE.Box3().setFromObject(root)
    const c = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())
    const PLINTH_TOP = 0.84
    root.position.set(-c.x, PLINTH_TOP + 0.02 - box.min.y, -c.z)
    plinth.position.set(0, 0, 0)
    root.updateMatrixWorld(true)
    const b2 = new THREE.Box3().setFromObject(root)
    const centre = b2.getCenter(new THREE.Vector3())
    const aim = centre.clone().add(new THREE.Vector3(0, -0.28, 0)) // aim below the wing so the plinth stays in frame
    controls.target.copy(aim)
    key.target.position.copy(centre)
    const span = Math.max(size.x, size.z)
    const dir = new THREE.Vector3(0.9, 0.3, 0.7).normalize()
    const fov = THREE.MathUtils.degToRad(camera.fov)
    const dist = span / (0.8 * 2 * Math.tan(fov / 2) * Math.min(camera.aspect, 1.9))
    camera.position.copy(aim).addScaledVector(dir, dist)
    controls.update()
    pipeline.shadowDirty = true
    setStatus(null)
    hook.ready = true
  } catch (e) {
    console.error(e)
    setStatus(`Could not load the canard model (${(e as Error).message}). The rest of the guide still works at the site root.`, true)
  }
}

boot().catch((e) => { console.error(e); setStatus(`The lab failed to start: ${(e as Error).message}`, true) })
