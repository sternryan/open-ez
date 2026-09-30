import * as THREE from 'three'
import { CutState } from './core/cut'
import { compositeMaterial, partMaterial, plyFrame, setPlyLook, COLORS, HATCH_COLOR } from './core/composite'
import type { MaterialSpec } from './logic/materials'
import { plyPhase, partPhase, type Phase } from './logic/anim'
import type { BuildState, MeshInfo } from './logic/build'
import {
  placement, jigPose, upFace, planHalfWidth, stationAmount, STATION_CUT, FS_EPS, TRIAL_FIT,
  type FuseLayup, type FusePlyRow, type Placement, type JigPose,
} from './logic/fuselage'
import { buildFuselageStation, STATION, INCH, blockTopY, fsToX } from './scene/fuselageStation'
import { fuseView, viewOffset } from './fuseShots'
import type { GraphLite } from './logic/graph'
import type { Shot } from './camera'

/**
 * The fuselage box in the shop: its meshes, where each one is for an op (layup table or jig), the jig's pose, and its section cut.
 *
 * Each part and ply has two meshes. The JIG mesh sits in `jigFrame`, the assembled box (model inches: x = FS, y = W.L. - 17.4 up,
 * z = -B.L., the glb frame after the Y-up turn); it is the only one the station cut opens. The TABLE mesh lies flat on the layup table
 * with its own matrix; the sides and everything bonded to them are flattened there (the plan bend taken out), since a side is laid up
 * flat before it is bent into the jig. Only one of the two is ever visible.
 */
export interface FMesh {
  /** the mesh name: `fuselage.<part>` or its ply node `fuselage.<part>.p<n>` */
  name: string
  part: string
  cid: string
  ply: { op: string; order: number } | null
  row: FusePlyRow | null
  fidelity: string
  hatch: boolean
  spec: MaterialSpec
  jig: THREE.Mesh
  table: THREE.Mesh
  jigMat: THREE.Material
  tableMat: THREE.Material
  /** the part whose table placement this mesh follows (a longeron and the side plies follow their side) */
  carrier: string
}

// Representational colours (the canard's rule: tell materials apart, not a measured product colour).
const WOOD: Record<string, number> = { firewall: 0xc9a06a, top_longeron_left: 0xdcc08e, top_longeron_right: 0xdcc08e }
/** the bulkheads' row on the table, packed left to right from the nose end, and the two sides' rows (table-local inches) */
const PACK = ['front_seat_bkhd', 'rear_seat_bkhd', 'panel', 'f22', 'f28', 'firewall']
const ROW_V = -22.5
const SIDE_V: Record<string, number> = { side_left: 1, side_right: 23 }
const GAP = 2.4

const toModel = (v: number[]) => new THREE.Vector3(v[0], v[2], -v[1]) // exported (x, y, z) -> the lab's model frame (x, z, -y)
const isRight = (part: string) => part.endsWith('_right')

export class FuselageBay {
  readonly group = new THREE.Group()
  readonly jigFrame = new THREE.Group()
  readonly tableGroup = new THREE.Group()
  readonly station: THREE.Group
  readonly cut: CutState
  readonly meshes: FMesh[] = []
  readonly infos: MeshInfo[] = []
  readonly phases = new Map<string, Phase>()
  pose: JigPose = 'upright'
  private order: string[]
  private dry: string[]
  private yTop = -1e9
  private yBottom = 1e9
  private tableM = new Map<string, THREE.Matrix4>()
  private spots = new Map<string, number>()
  private jigM: Record<JigPose, THREE.Matrix4>
  private firstIdx = new Map<string, number>()

  constructor(parts: { cid: string; node: string | null; geo: THREE.BufferGeometry; name: string }[], readonly data: FuseLayup, graph: GraphLite) {
    this.group.name = 'fuselage'
    this.station = buildFuselageStation()
    this.group.add(this.station, this.jigFrame, this.tableGroup)
    this.jigFrame.name = 'fuselageJig'
    this.jigFrame.matrixAutoUpdate = false
    this.order = graph.order
    this.dry = graph.ops.find((o) => o.id === TRIAL_FIT)?.components ?? []
    const byId = new Map(graph.ops.map((o) => [o.id, o]))
    this.order.forEach((id, i) => { for (const c of byId.get(id)?.components ?? []) if (!this.firstIdx.has(c)) this.firstIdx.set(c, i) })
    this.cut = new CutState(this.jigFrame, STATION_CUT.extent, STATION_CUT.depth, 0, new THREE.Vector3(1, 0, 0))
    this.cut.amount = 0
    const partOf = new Map(Object.entries(data.parts).map(([p, r]) => [r.node, p]))
    for (const p of parts) {
      p.geo.computeBoundingBox()
      const row = p.node ? data.nodes[p.node] ?? null : null
      const part = row ? row.part : partOf.get(p.name)
      if (!part) throw new Error(`fuselage mesh ${p.name} is not in layup.json`)
      const prow = data.parts[part]
      const hatch = prow.fidelity === 'representational'
      const carrier = part.startsWith('top_longeron_') ? part.replace('top_longeron_', 'side_') : part
      const flat = carrier.startsWith('side_') ? this.flatten(p.geo, isRight(carrier)) : p.geo.clone()
      flat.computeBoundingBox()
      let spec: MaterialSpec, jigMat: THREE.Material, tableMat: THREE.Material
      if (row) {
        const deg = row.orientation_deg ?? 0 // null: the page says the fibre direction is not critical; drawn square
        const cloth = row.cloth === 'UND' ? 'UND' : 'BID'
        spec = { kind: cloth === 'UND' ? 'und' : 'bid', angles: cloth === 'UND' ? [deg] : [deg, deg - 90], ply: { node: p.name, order: row.stack, cloth } }
        const fj = plyFrame(p.geo), ft = plyFrame(flat)
        jigMat = compositeMaterial(spec, this.cut, fj.web, fj.span, { axis: fj.axis, hatch })
        tableMat = compositeMaterial(spec, null, ft.web, ft.span, { axis: ft.axis, hatch })
      } else if (WOOD[part] !== undefined) {
        spec = { kind: 'part', angles: [] }
        jigMat = partMaterial(this.cut, { color: WOOD[part], hatch, name: part })
        tableMat = partMaterial(null, { color: WOOD[part], hatch, name: part })
      } else {
        spec = { kind: 'foam', angles: [] }
        jigMat = compositeMaterial(spec, this.cut, 0, undefined, { hatch })
        tableMat = compositeMaterial(spec, null, 0, undefined, { hatch })
      }
      const jig = new THREE.Mesh(p.geo, jigMat)
      jig.name = p.name
      const table = new THREE.Mesh(flat, tableMat)
      table.name = p.name + ':table'
      table.matrixAutoUpdate = false
      for (const m of [jig, table]) { m.castShadow = true; m.receiveShadow = true; m.visible = false }
      this.jigFrame.add(jig)
      this.tableGroup.add(table)
      const bb = p.geo.boundingBox!
      this.yTop = Math.max(this.yTop, bb.max.y)
      this.yBottom = Math.min(this.yBottom, bb.min.y)
      const ply = row ? { op: row.op, order: row.op_order } : null
      this.meshes.push({ name: p.name, part, cid: row ? row.component : prow.component, ply, row, fidelity: prow.fidelity, hatch, spec, jig, table, jigMat, tableMat, carrier })
      this.infos.push({ name: p.name, component: row ? row.component : prow.component, ply })
    }
    this.cut.collect(this.jigFrame)
    this.cut.update()
    const B = blockTopY(), J = STATION.jig
    this.jigM = {
      inverted: new THREE.Matrix4().makeTranslation(J.x, B, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
        .multiply(new THREE.Matrix4().makeRotationX(Math.PI)).multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -this.yTop, 0)),
      upright: new THREE.Matrix4().makeTranslation(J.x, B, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
        .multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -this.yBottom, 0)),
    }
    this.setPose('upright')
    this.pack()
  }

  /** Take the plan bend out: y' = y -+ half_width(x) in the export frame, which is z' = z +- h(x) here (right side at -z). */
  private flatten(geo: THREE.BufferGeometry, right: boolean): THREE.BufferGeometry {
    const g = geo.clone()
    const pos = g.attributes.position
    for (let i = 0; i < pos.count; i++) {
      const h = planHalfWidth(this.data.plan_bend, pos.getX(i))
      pos.setZ(i, pos.getZ(i) + (right ? h : -h))
    }
    pos.needsUpdate = true
    g.computeVertexNormals()
    return g
  }

  setPose(p: JigPose) {
    this.pose = p
    this.jigFrame.matrix.copy(this.jigM[p])
    this.jigFrame.matrixWorldNeedsUpdate = true
    this.jigFrame.updateMatrixWorld(true)
    this.cut.update()
  }

  /** the rotation that lays a carrier flat: a side inside face up, a bulkhead with `face` up, the bottom as it is (inside face up) */
  private flatRotation(carrier: string, face: 'fwd' | 'aft'): THREE.Quaternion {
    const up = new THREE.Vector3(0, 1, 0)
    if (carrier.startsWith('side_')) return new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, isRight(carrier) ? 1 : -1), up)
    const fwd = this.data.parts[carrier]?.fwd_normal
    if (!fwd) return new THREE.Quaternion()
    const n = toModel(fwd).normalize()
    if (face === 'aft') n.negate()
    return new THREE.Quaternion().setFromUnitVectors(n, up)
  }

  private carrierGeo(carrier: string): THREE.BufferGeometry | null {
    return this.meshes.find((m) => m.name === `fuselage.${carrier}`)?.table.geometry ?? null
  }

  /** the carrier's flat box after the rotation, about the flat geometry's own centre (inches) */
  private rotatedBox(carrier: string, q: THREE.Quaternion): { box: THREE.Box3; c: THREE.Vector3 } {
    const g = this.carrierGeo(carrier)!
    g.computeBoundingBox()
    const c = g.boundingBox!.getCenter(new THREE.Vector3())
    const box = new THREE.Box3(), v = new THREE.Vector3(), pos = g.attributes.position
    for (let i = 0; i < pos.count; i++) box.expandByPoint(v.fromBufferAttribute(pos, i).sub(c).applyQuaternion(q))
    return { box, c }
  }

  /** where each bulkhead lies along the table (u, inches from its middle), packed from the nose end */
  private pack() {
    let u = -STATION.table.len / INCH / 2 + 2
    for (const p of PACK) {
      if (!this.carrierGeo(p)) continue
      const { box } = this.rotatedBox(p, this.flatRotation(p, 'fwd'))
      const w = box.max.x - box.min.x
      this.spots.set(p, u + w / 2)
      u += w + GAP
    }
  }

  /** a carrier's matrix on the table, lying with `face` up (world metres from the flat geometry's inches) */
  tableMatrix(carrier: string, face: 'fwd' | 'aft'): THREE.Matrix4 {
    const key = `${carrier}|${face}`
    const hit = this.tableM.get(key)
    if (hit) return hit
    const q = this.flatRotation(carrier, face)
    const { box, c } = this.rotatedBox(carrier, q)
    const T = STATION.table
    const u = carrier.startsWith('side_') || carrier === 'bottom' ? 0 : this.spots.get(carrier) ?? 0
    const v = SIDE_V[carrier] ?? (carrier === 'bottom' ? 0 : ROW_V)
    const mid = box.getCenter(new THREE.Vector3())
    const m = new THREE.Matrix4().makeTranslation(T.x + u * INCH, T.topY + 0.0015, T.z + v * INCH)
      .multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeTranslation(-mid.x, -box.min.y, -mid.z))
      .multiply(new THREE.Matrix4().makeRotationFromQuaternion(q))
      .multiply(new THREE.Matrix4().makeTranslation(-c.x, -c.y, -c.z))
    this.tableM.set(key, m)
    return m
  }

  /** the face a carrier lies on for this op (the bulkheads turn over between their front and back glassing) */
  faceFor(carrier: string, opId: string | null): 'fwd' | 'aft' {
    return this.data.parts[carrier]?.fwd_normal ? upFace(carrier, opId, this.order, this.data.nodes) : 'fwd'
  }

  placeOf(m: FMesh, opId: string | null): Placement {
    return placement(m.cid, opId, this.order, this.dry)
  }

  opCount(opId: string | null): number {
    return opId ? this.meshes.filter((m) => m.ply?.op === opId).length : 0
  }

  /**
   * Show the build: `state` is visibleSet's answer for the selected op (null: the finished box, as the canard subject shows it).
   * Returns a signature of what casts shadows, so the caller can redraw the shadow map only when it changed.
   */
  paint(state: Map<string, BuildState> | null, opId: string | null, lay: number, layT: number, ghost: boolean, opIdx: Map<string, number>): string {
    const sel = state ? opId : null
    const pose = jigPose(sel, this.order)
    if (pose !== this.pose) this.setPose(pose)
    const cur = sel ? opIdx.get(sel) : undefined, count = this.opCount(sel)
    let sig = pose
    for (const m of this.meshes) {
      const st = state ? state.get(m.name) ?? 'hidden' : 'built'
      const ph = m.ply && cur !== undefined
        ? plyPhase({ meshOpIndex: opIdx.get(m.ply.op), curOpIndex: cur, order: m.ply.order, lay, count, t: layT, ghost })
        : partPhase(st)
      this.phases.set(m.name, ph)
      const shown = st !== 'hidden' && !(m.ply && st === 'current' && ph.unroll <= 0)
      const where = st === 'ghost' ? 'jig' : this.placeOf(m, sel)
      m.jig.visible = shown && where === 'jig'
      m.table.visible = shown && where === 'table'
      if (m.table.visible) {
        const face = this.faceFor(m.carrier, sel)
        m.table.matrix.copy(this.tableMatrix(m.carrier, face))
        m.table.matrixWorldNeedsUpdate = true
        sig += m.carrier + face
      }
      const cast = st === 'built' || (st === 'current' && ph.unroll >= 1)
      m.jig.castShadow = m.table.castShadow = cast
      const look = { unroll: ph.unroll, front: ph.front, cure: ph.cure, ghost: st === 'ghost' }
      setPlyLook(m.jigMat, look)
      setPlyLook(m.tableMat, look)
      sig += (m.jig.visible ? 'j' : m.table.visible ? 't' : '-') + (cast ? '1' : '0')
    }
    this.tableGroup.updateMatrixWorld(true)
    return sig
  }

  /** the station cut: open at `fs` (the forward side removed), or closed */
  setStation(on: boolean, fs: number, glow: number) {
    this.cut.amount = on ? stationAmount(fs) : 0
    this.cut.update()
    this.cut.uGlow.value = on ? glow : 0
  }

  /** meshes the station cuts: in the jig, built so far, visible, and spanning fs (model x is FS) */
  capped(fs: number, state: (name: string) => BuildState | undefined): FMesh[] {
    return this.meshes.filter((m) => {
      const st = state(m.name)
      if (!m.jig.visible || (st !== 'built' && st !== 'current')) return false
      const b = m.jig.geometry.boundingBox!
      return b.min.x - FS_EPS <= fs && fs <= b.max.x + FS_EPS
    })
  }

  /** the visible mesh of a part or ply (jig or table), or null */
  shown(name: string): THREE.Mesh | null {
    const m = this.meshes.find((x) => x.name === name)
    if (!m) return null
    return m.jig.visible ? m.jig : m.table.visible ? m.table : null
  }

  /** world box of a mesh where it would be for `opId` (placement and pose for that op) */
  worldBoxAt(m: FMesh, opId: string | null): THREE.Box3 {
    const where = this.placeOf(m, opId)
    const mat = where === 'jig'
      ? this.jigM[jigPose(opId, this.order)]
      : this.tableMatrix(m.carrier, this.faceFor(m.carrier, opId))
    const g = where === 'jig' ? m.jig.geometry : m.table.geometry
    return g.boundingBox!.clone().applyMatrix4(mat)
  }

  /** the lab shot for every fuselage op (world metres), aimed where the op's parts are for that op */
  shots(ops: string[], fov: number): Record<string, Shot> {
    const out: Record<string, Shot> = {}
    for (const id of ops) {
      const v = fuseView(id)
      const target = new THREE.Vector3()
      if (v.focus === 'box') {
        const bx = new THREE.Box3()
        for (const m of this.meshes) if (!m.ply && this.placeOf(m, id) === 'jig' && this.isMade(m, id)) bx.union(this.worldBoxAt(m, id))
        if (bx.isEmpty()) target.set(STATION.jig.x, blockTopY() + 0.25, STATION.jig.z); else bx.getCenter(target)
      } else {
        const ms = v.focus.parts.map((p) => this.meshes.find((m) => m.name === `fuselage.${p}`)).filter((m): m is FMesh => !!m)
        if (v.focus.fs !== undefined && ms.length) {
          const m = ms[0], where = this.placeOf(m, id)
          const g = where === 'jig' ? m.jig.geometry : m.table.geometry
          const c = g.boundingBox!.getCenter(new THREE.Vector3())
          c.x = v.focus.fs
          const mat = where === 'jig' ? this.jigM[jigPose(id, this.order)] : this.tableMatrix(m.carrier, this.faceFor(m.carrier, id))
          target.copy(c.applyMatrix4(mat))
        } else {
          const bx = new THREE.Box3()
          for (const m of ms) bx.union(this.worldBoxAt(m, id))
          bx.getCenter(target)
        }
      }
      const off = viewOffset(v)
      const pos = target.clone().add(new THREE.Vector3(off[0], off[1], off[2]).multiplyScalar(INCH))
      out[id] = { pos: [pos.x, pos.y, pos.z], target: [target.x, target.y, target.z], fov }
    }
    return out
  }

  /** the close shot of the station cut at `fs`: forward of the plane, a little above, looking aft at the face (world metres; the finished box, right side up) */
  cutShot(fs: number, fov: number): Shot {
    const bx = new THREE.Box3()
    for (const m of this.meshes) if (!m.ply && this.placeOf(m, null) === 'jig') bx.union(this.worldBoxAt(m, null))
    const target = bx.isEmpty() ? new THREE.Vector3(STATION.jig.x, blockTopY() + 0.25, STATION.jig.z) : bx.getCenter(new THREE.Vector3())
    target.x = fsToX(fs)
    const off = viewOffset({ focus: 'box', dist: 58, el: 24, az: 72 })
    const pos = target.clone().add(new THREE.Vector3(off[0], off[1], off[2]).multiplyScalar(INCH))
    return { pos: [pos.x, pos.y, pos.z], target: [target.x, target.y, target.z], fov }
  }

  /** a part exists by this op (its component's first op is at or before it) */
  private isMade(m: FMesh, opId: string): boolean {
    const f = this.firstIdx.get(m.cid)
    return f !== undefined && f <= this.order.indexOf(opId)
  }

  /** the station's world box: both tables and the finished box on the jig, for the home shot */
  homeBox(): THREE.Box3 {
    const T = STATION.table, J = STATION.jig
    return new THREE.Box3(new THREE.Vector3(T.x - T.len / 2, J.benchTopY, T.z - T.depth / 2), new THREE.Vector3(T.x + T.len / 2, blockTopY() + 0.6, J.z + J.benchDepth / 2))
  }

  labelColor(m: FMesh): string {
    const c = m.hatch ? HATCH_COLOR : WOOD[m.part] ?? COLORS.foam
    return '#' + c.toString(16).padStart(6, '0')
  }
}
