import * as THREE from 'three'
import { CutState } from './core/cut'
import { compositeMaterial, partMaterial, plyFrame, setPlyLook, COLORS, HATCH_COLOR } from './core/composite'
import type { MaterialSpec } from './logic/materials'
import { plyPhase, partPhase, type Phase } from './logic/anim'
import type { BuildState, MeshInfo } from './logic/build'
import {
  placement, jigPose, upFace, planHalfWidth, stationAmount, turnPose, hatchSoftness, shownAt, stageAt, poseAngle, poseBase, restLift, animatedTurn, dryTone,
  STATION_CUT, FS_EPS, TRIAL_FIT, FLIP_SECONDS, FLIP_DELAY, JIG_ONLY, GEAR_TABLE_RISE, BANK_DEG, FITTED_TYRE_OD, TYRE_SECTION, RIM_DIA,
  CANARD_INSTALLED_CHAPTERS, NOSE_CHAPTER, NG_BENCH, onBench,
  type FuseLayup, type FusePlyRow, type Placement, type JigPose, type ShowWindow,
} from './logic/fuselage'
import { matte } from './core/materials'
import { buildFuselageStation, STATION, INCH, blockTopY, fsToX } from './scene/fuselageStation'
import { nosePoints, nosePose, noseAxleAt, type Candidate, type NosePoints, type NoseGearKin } from './logic/kin'
import { fuseView, viewOffset } from './fuseShots'
import { M25_CHAPTERS, M25_FIRST_OP, SPAR_BENCH_LAST, ELEV_OPS, STOPS_FROM, SPAR_FIT_OP, SPAR_COMPONENTS, m25Place, boxGhostAt } from './logic/m25'
import { stickAngleDeg, stickDir, type ControlsKin } from './logic/kin'
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
  /** the node's own shape and its later ones (layup.json "stages": the carve, the canard opening, the access holes) */
  base: THREE.BufferGeometry
  stages: { from: string; node: string; geo: THREE.BufferGeometry }[]
  /** the part's own show window (layup.json "show"), and whether it has no place on the layup table */
  show?: ShowWindow
  jigOnly: boolean
  /** the material an opening removes: drawn lifted out of it at its op */
  void: boolean
  /** a chapter 13 nose or nose-gear part (layup.json "extras"): shown only while a chapter 13 op is selected */
  extra: boolean
  /** a chapter 14-17 part (layup.json "extras".m25): the spar (on the bench, then in the box), the firewall face, the controls and the trim; shown on those chapters' ops only */
  m25: boolean
}

// Representational colours (the canard's rule: tell materials apart, not a measured product colour).
const WOOD: Record<string, number> = {
  firewall: 0xc9a06a, top_longeron_left: 0xdcc08e, top_longeron_right: 0xdcc08e,
  belt_insert: 0xc9a06a, rollover_inserts: 0xc9a06a, belt_attach: 0xc9a06a, jig_blocks: 0xb98f5c, datum_board: 0xd2b27c,
}
/** metal and the glass strut (colour, metalness, roughness): aluminium angles and step, steel tubes and axles, S-glass */
const METAL: Record<string, [number, number, number]> = {
  step: [0xc4c8cd, 0.85, 0.35], extrusions: [0xb9bec4, 0.85, 0.4], gear_tubes: [0x8d939a, 0.9, 0.3], axles: [0x8d939a, 0.9, 0.3],
  strut: [0xd8d0b0, 0.05, 0.45],
}
/** the parts the chapter 4-6 poses are measured on (the box itself): the roll-over, gear and tools never move where the box sits */
const BOX = new Set(['side_left', 'side_right', 'front_seat_bkhd', 'rear_seat_bkhd', 'top_longeron_left', 'top_longeron_right', 'f22', 'f28', 'panel', 'firewall', 'bottom'])
/** what a part lies with on the table, if not itself (the longerons and side plies follow their side: see the constructor) */
const CARRIER: Record<string, string> = { rollover_inserts: 'rollover' }
/** fitted parts that are thin bands, not plates: their bounding box says nothing about how large their faces are */
const NARROW = new Set(['carved_corners'])
/** the chapter 14-17 parts' looks (colour, metalness, roughness; 'foam' parts are drawn as foam): REPRESENTATIONAL colours, as the box's */
const M25_LOOK: Record<string, ['wood' | 'metal', number, number, number] | 'foam'> = {
  spar_box: 'foam', spar_bulkheads_end_bulkheads: 'foam', spar_bulkheads_interior_bulkheads: 'foam',
  spar_lwa_lwa1: ['metal', 0xc4c8cd, 0.85, 0.35], spar_lwa_lwa2: ['metal', 0xc4c8cd, 0.85, 0.35], spar_lwa_lwa3: ['metal', 0xc4c8cd, 0.85, 0.35],
  spar_lwa_lwa4: ['metal', 0xc4c8cd, 0.85, 0.35], spar_lwa_lwa5: ['metal', 0xc4c8cd, 0.85, 0.35],
  spar_spruce_blocks: ['wood', 0xdcc08e, 0, 0.6], spar_em12: ['metal', 0x8d939a, 0.9, 0.3], spar_sh1: ['metal', 0xc4c8cd, 0.85, 0.35], spar_jig: ['wood', 0xb98f5c, 0, 0.62],
  fuselage_firewall_stainless: ['metal', 0xd5d8dc, 0.9, 0.3], firewall_belcrank: ['metal', 0x8d939a, 0.9, 0.3], firewall_master_cylinders: ['metal', 0x6d737a, 0.7, 0.4],
  controls_consoles_front_console: 'foam', controls_consoles_rear_console: 'foam', controls_torque_tube: ['metal', 0x8d939a, 0.9, 0.3],
  controls_sticks_front_stick: ['metal', 0x8d939a, 0.9, 0.3], controls_sticks_rear_stick: ['metal', 0x8d939a, 0.9, 0.3], controls_pitch_pushrod: ['metal', 0xc4c8cd, 0.85, 0.35],
  controls_rudder_conduit: ['wood', 0x2e2e30, 0, 0.7], trim_pitch_handle_pth: ['metal', 0xc4c8cd, 0.85, 0.35], trim_pitch_handle_pth_pivot: ['metal', 0x8d939a, 0.9, 0.3],
  trim_pitch_handle_pth_springs: ['metal', 0x9aa0a6, 0.9, 0.35], trim_roll_trim_roll_trim: ['metal', 0xc4c8cd, 0.85, 0.35], trim_roll_trim_roll_trim_springs: ['metal', 0x9aa0a6, 0.9, 0.35],
}
/** the spar's parts that slide into the box as one (the bench's, less the jig) */
const SLIDES = (cid: string) => SPAR_COMPONENTS.has(cid) && cid !== 'spar.jig'
/** the parts bolted on the firewall's aft face: the glass plies lie on that face (the aft ply to F.S. 125.31), where the stainless sheet is exported, so the lab sets them that far aft (display only) */
const FIREWALL_FACE = new Set(['fuselage.firewall_stainless', 'firewall.belcrank', 'firewall.master_cylinders'])
const STICKS = new Set(['controls_sticks_front_stick', 'controls_sticks_rear_stick'])
/** how far the canard opening's removed material is lifted out of the box at its op (inches), so it reads as taken out */
const VOID_LIFT = 5
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
  private jigM = new Map<JigPose, THREE.Matrix4>()
  private bank: Record<string, number>
  /** chapter 9's level gear table, chapter 7's 45 degree cradles, and the axle-station marks (shown by pose and op in paint) */
  readonly gearTable = new THREE.Group()
  readonly cradles: Record<'bank-left-45' | 'bank-right-45', THREE.Group> = { 'bank-left-45': new THREE.Group(), 'bank-right-45': new THREE.Group() }
  readonly marks = new THREE.Group()
  /** the dry cloth's tone on the box in the jig (logic/fuselage.ts dryTone): one uniform shared by every jig ply */
  private dryTone = { value: 1 }
  /** the finished box on its own feet: the main wheels (fitted, in the box's frame) and the stand under the nose (representational furniture) */
  readonly wheels = new THREE.Group()
  readonly noseStand = new THREE.Group()
  /** the box-frame point the wheels' label hangs over: the top of the right (bench-side) wheel */
  private wheelTop: THREE.Vector3 | null = null
  /** the marks' anchors in the box's frame (model inches): the dimension's middle and the axle's end of the station line */
  markAt: { dim: THREE.Vector3; axle: THREE.Vector3 } | null = null
  private marksOn = false
  private firstIdx = new Map<string, number>()
  /** the turn over (logic/fuselage.ts turnPose): from, and progress 0..1 in sim time; 1 = at rest in `pose` */
  private turnFrom: JigPose = 'upright'
  private turnK = 1
  private half = { h: 0, w: 0 }
  private yMid = 0
  /** chapters 12-13: the canard and its elevators installed on the airplane (jig frame, inches), mirrored for the left half */
  readonly installed = new THREE.Group()
  /** the nose gear's other axle candidate, drawn as a ghost wheel and strut beside the one the export draws (the p171 / Owner's Manual conflict) */
  readonly ghost = new THREE.Group()
  private opChapter = new Map<string, number>()
  private opOf = new Map<string, { id: string; components: string[] }>()
  private noseK: NoseGearKin | null = null
  private nosePts: Record<Candidate, NosePoints> | null = null
  private noseT = 0
  private noseShown = false
  private ghostWheel: THREE.Mesh | null = null
  private ghostStrut: THREE.Mesh | null = null
  /** chapters 14-17: the control kinematics' inputs, the spar's slide-in (inches along the span, 0 = installed), the stick's deflection (elevator, up positive) */
  private ctl: ControlsKin | null = null
  private slide = 0
  private deflUp = 0
  /** the pitch stops (fitted, unprinted): two small blocks at the stick's travel limits, shown from STOPS_FROM */
  readonly stops = new THREE.Group()
  private sparBenchM = new Map<string, THREE.Matrix4>()
  private m25Chapter = false
  /** how far aft the firewall face's parts are drawn (inches): the aft glass ply's thickness over the stainless sheet's station, plus a hair */
  private firewallAside = 0

  constructor(parts: { cid: string; node: string | null; geo: THREE.BufferGeometry; name: string }[], readonly data: FuseLayup, graph: GraphLite) {
    this.group.name = 'fuselage'
    this.station = buildFuselageStation()
    this.group.add(this.station, this.jigFrame, this.tableGroup)
    this.jigFrame.name = 'fuselageJig'
    this.jigFrame.matrixAutoUpdate = false
    this.order = graph.order
    for (const o of graph.ops) { this.opChapter.set(o.id, o.chapter); this.opOf.set(o.id, o) }
    this.dry = graph.ops.find((o) => o.id === TRIAL_FIT)?.components ?? []
    const byId = new Map(graph.ops.map((o) => [o.id, o]))
    this.order.forEach((id, i) => { for (const c of byId.get(id)?.components ?? []) if (!this.firstIdx.has(c)) this.firstIdx.set(c, i) })
    this.cut = new CutState(this.jigFrame, STATION_CUT.extent, STATION_CUT.depth, 0, new THREE.Vector3(1, 0, 0))
    this.cut.amount = 0
    this.bank = data.bank_deg ?? BANK_DEG
    const extraParts = new Set(Object.keys(data.extras?.nose_parts ?? {}))
    const m25Parts = new Set(Object.keys(data.extras?.m25?.parts ?? {}))
    this.ctl = data.extras?.m25?.controls ?? null
    const ng = data.extras?.nose_gear
    if (ng) {
      this.noseK = ng as NoseGearKin
      this.nosePts = { plans: nosePoints(this.noseK, 'plans'), manual: nosePoints(this.noseK, 'manual') }
    }
    const partOf = new Map(Object.entries(data.parts).map(([p, r]) => [r.node, p]))
    // a later shape of a node is not a mesh of its own: it replaces the node's geometry from its op on (paint)
    const stageGeo = new Map<string, THREE.BufferGeometry>()
    const stageNodes = new Set(Object.values(data.stages ?? {}).flat().map((s) => s.node))
    for (const p of parts) if (stageNodes.has(p.name)) { p.geo.computeBoundingBox(); stageGeo.set(p.name, p.geo) }
    for (const p of parts) {
      if (stageNodes.has(p.name)) continue
      p.geo.computeBoundingBox()
      const row = p.node ? data.nodes[p.node] ?? null : null
      const part = row ? row.part : partOf.get(p.name)
      if (!part) throw new Error(`fuselage mesh ${p.name} is not in layup.json`)
      const prow = data.parts[part]
      const hatch = prow.fidelity === 'representational'
      // the stripes thin out on a large surface (its two largest extents, in^2); small parts and cut faces keep the full stripes
      const e = p.geo.boundingBox!.getSize(new THREE.Vector3()).toArray().sort((a, b) => b - a)
      // (the carved corners are thin bands whose box spans the whole box: they keep the full stripes)
      const hatchSoft = hatch && !NARROW.has(part) ? hatchSoftness(e[0] * e[1]) : 0
      const carrier = part.startsWith('top_longeron_') ? part.replace('top_longeron_', 'side_') : CARRIER[part] ?? part
      const flat = carrier.startsWith('side_') ? this.flatten(p.geo, isRight(carrier)) : p.geo.clone()
      flat.computeBoundingBox()
      let spec: MaterialSpec, jigMat: THREE.Material, tableMat: THREE.Material
      if (row) {
        const deg = row.orientation_deg ?? 0 // null: the page says the fibre direction is not critical; drawn square
        const cloth = row.cloth === 'UND' ? 'UND' : 'BID'
        spec = { kind: cloth === 'UND' ? 'und' : 'bid', angles: cloth === 'UND' ? [deg] : [deg, deg - 90], ply: { node: p.name, order: row.stack, cloth } }
        const fj = plyFrame(p.geo), ft = plyFrame(flat)
        jigMat = compositeMaterial(spec, this.cut, fj.web, fj.span, { axis: fj.axis, hatch, hatchSoft, dryTone: this.dryTone })
        tableMat = compositeMaterial(spec, null, ft.web, ft.span, { axis: ft.axis, hatch, hatchSoft })
      } else if (M25_LOOK[part] !== undefined && M25_LOOK[part] !== 'foam') {
        const [kind, color, metalness, roughness] = M25_LOOK[part] as ['wood' | 'metal', number, number, number]
        spec = { kind: 'part', angles: [] }
        jigMat = partMaterial(this.cut, { color, metalness, roughness, hatch, hatchSoft, name: part })
        tableMat = partMaterial(null, { color, metalness, roughness, hatch, hatchSoft, name: part })
        void kind
      } else if (WOOD[part] !== undefined) {
        spec = { kind: 'part', angles: [] }
        jigMat = partMaterial(this.cut, { color: WOOD[part], hatch, hatchSoft, name: part })
        tableMat = partMaterial(null, { color: WOOD[part], hatch, hatchSoft, name: part })
      } else if (METAL[part] !== undefined) {
        const [color, metalness, roughness] = METAL[part]
        spec = { kind: 'part', angles: [] }
        jigMat = partMaterial(this.cut, { color, metalness, roughness, hatch, hatchSoft, name: part })
        tableMat = partMaterial(null, { color, metalness, roughness, hatch, hatchSoft, name: part })
      } else {
        spec = { kind: 'foam', angles: [] }
        jigMat = compositeMaterial(spec, this.cut, 0, undefined, { hatch, hatchSoft })
        tableMat = compositeMaterial(spec, null, 0, undefined, { hatch, hatchSoft })
      }
      const jig = new THREE.Mesh(p.geo, jigMat)
      jig.name = p.name
      const table = new THREE.Mesh(flat, tableMat)
      table.name = p.name + ':table'
      table.matrixAutoUpdate = false
      for (const m of [jig, table]) { m.castShadow = true; m.receiveShadow = true; m.visible = false }
      if (part === 'belt_insert') for (const mt of [jigMat, tableMat]) { mt.polygonOffset = true; mt.polygonOffsetFactor = -1; mt.polygonOffsetUnits = -2 } // in the bottom foam's corner: its faces lie on the foam's
      this.jigFrame.add(jig)
      this.tableGroup.add(table)
      const bb = p.geo.boundingBox!
      if (BOX.has(part)) {
        this.yTop = Math.max(this.yTop, bb.max.y)
        this.yBottom = Math.min(this.yBottom, bb.min.y)
        if (!row) this.half.w = Math.max(this.half.w, Math.abs(bb.min.z), Math.abs(bb.max.z))
      }
      const ply = row ? { op: row.op, order: row.op_order } : null
      const stages = (data.stages?.[p.name] ?? []).map((s) => ({ ...s, geo: stageGeo.get(s.node)! })).filter((s) => !!s.geo)
      const cid = row ? row.component : prow.component
      this.meshes.push({
        name: p.name, part, cid, ply, row, fidelity: prow.fidelity, hatch, spec, jig, table, jigMat, tableMat, carrier,
        base: p.geo, stages, show: prow.show, jigOnly: JIG_ONLY.has(cid), void: !!prow.void, extra: extraParts.has(part), m25: m25Parts.has(part),
      })
      this.infos.push({ name: p.name, component: row ? row.component : prow.component, ply })
    }
    this.buildWheels()
    this.cut.collect(this.jigFrame)
    this.cut.update()
    const B = blockTopY(), J = STATION.jig
    this.jigM.set('inverted', new THREE.Matrix4().makeTranslation(J.x, B, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeRotationX(Math.PI)).multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -this.yTop, 0)))
    this.jigM.set('upright', new THREE.Matrix4().makeTranslation(J.x, B, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -this.yBottom, 0)))
    this.half.h = (this.yTop - this.yBottom) / 2
    this.yMid = (this.yTop + this.yBottom) / 2
    for (const p of ['bank-left-45', 'bank-right-45', 'gear-table'] as JigPose[]) {
      const a = poseAngle(p, this.bank)
      this.jigM.set(p, this.poseMatrix(a, poseBase(p) + restLift(a, this.half)))
    }
    // on its own feet: right side up on the shop floor beside the bench, the wheels' lowest point on the floor (y = 0); with no
    // wheels (no axles in this build) the box's own bottom sits on the floor
    const yLow = this.wheelLow ?? this.yBottom
    this.jigM.set('on-gear', new THREE.Matrix4().makeTranslation(J.x, 0, STATION.floor.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -yLow, 0)))
    this.buildFurniture()
    this.buildNoseStand()
    this.buildMarks()
    this.buildGhost()
    this.buildStops()
    {
      const ply = Math.max(...Object.values(data.nodes).filter((n) => n.part === 'firewall').map((n) => n.fs_max), -Infinity)
      const sheet = data.extras?.m25?.parts.fuselage_firewall_stainless?.fs_min
      this.firewallAside = sheet !== undefined && ply > sheet ? ply - sheet + 0.02 : 0
    }
    this.group.add(this.gearTable, this.cradles['bank-left-45'], this.cradles['bank-right-45'], this.noseStand)
    this.jigFrame.add(this.marks, this.installed, this.ghost, this.stops)
    this.installed.name = 'installedCanard'
    this.installed.visible = false
    this.setPose('upright')
    this.pack()
  }

  /** the jig frame's matrix with the box rolled `angle` about its long axis through its middle, that axis `lift` inches above the block tops */
  private poseMatrix(angle: number, lift: number): THREE.Matrix4 {
    const J = STATION.jig
    return new THREE.Matrix4().makeTranslation(J.x, blockTopY() + lift * INCH, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeRotationX(angle)).multiply(new THREE.Matrix4().makeTranslation(-STATION.fsMid, -this.yMid, 0))
  }

  /**
   * The furniture the chapter 7 and 9 poses stand on. REPRESENTATIONAL, as the rest of the station: the book says only "jig the
   * fuselage at 45 degrees" (p46) and "level it on the top longerons" (p50).
   *  - chapter 9: a level table GEAR_TABLE_RISE above the jig blocks on four posts, wide enough for the two datum boards at B.L. 26.75,
   *    with an opening the inverted roll-over hangs through;
   *  - chapter 7: a V cradle under the box's lower side and bottom at two stations, with a post from each board's free end to the bench.
   */
  private buildFurniture() {
    const J = STATION.jig
    const wood = matte(0x9a7650, 0.7, { detail: 5, colorVar: 0.12, name: 'gear-table' })
    const post = matte(0x6b5038, 0.7, { detail: 4, colorVar: 0.1 })
    const add = (g: THREE.Group, m: THREE.Material, sx: number, sy: number, sz: number, x: number, y: number, z: number) => {
      const b = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), m)
      b.position.set(x, y, z); b.castShadow = true; b.receiveShadow = true
      g.add(b)
      return b
    }
    // ---- the gear table: its top at the support height, an opening for the roll-over ----
    const top = blockTopY() + GEAR_TABLE_RISE * INCH, t = 0.75 * INCH, cy = top - t / 2
    const x0 = fsToX(14), x1 = fsToX(134), hw = 31 * INCH
    const ro = this.data.parts.rollover
    const hx0 = fsToX((ro?.fs_min ?? 79) - 1.5), hx1 = fsToX((ro?.fs_max ?? 84) + 1.5), hz = 13 * INCH
    add(this.gearTable, wood, hx0 - x0, t, 2 * hw, (x0 + hx0) / 2, cy, J.z)
    add(this.gearTable, wood, x1 - hx1, t, 2 * hw, (x1 + hx1) / 2, cy, J.z)
    for (const s of [-1, 1]) add(this.gearTable, wood, hx1 - hx0, t, hw - hz, (hx0 + hx1) / 2, cy, J.z + s * (hz + hw) / 2)
    const legH = top - t - J.benchTopY
    for (const fs of [34, 113]) for (const s of [-1, 1]) add(this.gearTable, post, 3.5 * INCH, legH, 3.5 * INCH, fsToX(fs), J.benchTopY + legH / 2, J.z + s * 11 * INCH)
    this.gearTable.name = 'gearTable'
    this.gearTable.visible = false
    this.gearTable.userData.representational = true
    // ---- the 45 degree cradles: boards in the box's frame at rest, posts in the world ----
    const T = 0.75, W = 3.5
    for (const p of ['bank-left-45', 'bank-right-45'] as const) {
      const g = this.cradles[p]
      g.name = `cradle-${p}`
      g.visible = false
      g.userData.representational = true
      const M = this.jigM.get(p)!
      const lowSide = p === 'bank-left-45' ? 1 : -1 // the side that goes down: the left (model z > 0) at a left bank
      const { h, w } = this.half
      // the face that goes down with the low side: the bottom when the roll is under 90 degrees, the top once it is past on its side
      // (the 135 degree roll rests on the top-left corner, the bottom facing up)
      const fy = Math.cos(poseAngle(p, this.bank)) < 0 ? 1 : -1
      for (const fs of [40, 100]) {
        const boards: [THREE.Vector3, THREE.Vector3, THREE.Vector3][] = [ // centre, size (model inches, box frame), free end
          [new THREE.Vector3(fs, this.yMid + fy * (h + T / 2), 0), new THREE.Vector3(W, T, 2 * w + 2 * T), new THREE.Vector3(fs, this.yMid + fy * (h + T / 2), -lowSide * (w + T))],
          [new THREE.Vector3(fs, this.yMid, lowSide * (w + T / 2)), new THREE.Vector3(W, 2 * h + T, T), new THREE.Vector3(fs, this.yMid - fy * h, lowSide * (w + T / 2))],
        ]
        for (const [c, sz, end] of boards) {
          const b = new THREE.Mesh(new THREE.BoxGeometry(sz.x, sz.y, sz.z), post)
          b.matrixAutoUpdate = false
          b.matrix.copy(M).multiply(new THREE.Matrix4().makeTranslation(c.x, c.y, c.z))
          b.castShadow = true; b.receiveShadow = true
          g.add(b)
          const e = end.clone().applyMatrix4(M)
          const ph = e.y - J.benchTopY
          if (ph > 0.02) add(g, post, 1.5 * INCH, ph, 1.5 * INCH, e.x, J.benchTopY + ph / 2, e.z)
        }
      }
    }
  }

  /** the wheels' lowest point in the box's frame (inches), once they are built */
  private wheelLow: number | null = null

  /**
   * The main wheels (logic/fuselage.ts FITTED_TYRE_OD): a tyre and a hub on each axle stub, centred on the stub, the axle along B.L.
   * Fitted: striped and labelled "(fitted shape)" (main.ts). Shown only on the finished box, standing on them.
   */
  private buildWheels() {
    const ax = this.meshes.find((m) => m.part === 'axles')
    if (!ax) return
    const pos = ax.base.attributes.position, v = new THREE.Vector3()
    const half = { [1]: new THREE.Box3(), [-1]: new THREE.Box3() } as Record<number, THREE.Box3>
    for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i); half[v.z >= 0 ? 1 : -1].expandByPoint(v) }
    const R = FITTED_TYRE_OD / 2, tube = TYRE_SECTION / 2
    const tyre = new THREE.TorusGeometry(R - tube, tube, 18, 48) // in the XY plane: its axis is Z, the axle's direction (B.L.)
    const hub = new THREE.CylinderGeometry(RIM_DIA / 2, RIM_DIA / 2, TYRE_SECTION * 0.8, 32).rotateX(Math.PI / 2)
    const rubber = partMaterial(this.cut, { color: 0x2e2e30, roughness: 0.82, hatch: true, name: 'tyre' })
    const metal = partMaterial(this.cut, { color: 0xa9aeb4, metalness: 0.8, roughness: 0.35, hatch: true, name: 'hub' })
    for (const sgn of [1, -1]) {
      const c = half[sgn].getCenter(new THREE.Vector3())
      for (const [g, m] of [[tyre, rubber], [hub, metal]] as const) {
        const w = new THREE.Mesh(g, m)
        w.position.copy(c)
        w.castShadow = true; w.receiveShadow = true
        w.name = 'gear.wheels'
        this.wheels.add(w)
      }
      this.wheelLow = c.y - R
      if (sgn === -1) this.wheelTop = new THREE.Vector3(c.x, c.y + R, c.z) // the right wheel (model z < 0): the bench side, clear of the dock in the home shot
    }
    this.wheels.name = 'gear.wheels'
    this.wheels.visible = false
    this.wheels.userData.representational = true
    this.wheels.userData.hatch = true
    this.jigFrame.add(this.wheels)
  }

  /**
   * The stand under the nose of the finished box. REPRESENTATIONAL furniture, as the cradles: the book has no nose gear until a later
   * chapter, so the box stands on its main wheels with its forward end on a padded stand, the top longerons level as the gear was set.
   */
  private buildNoseStand() {
    const M = this.jigM.get('on-gear')!
    const fs = 34 // a station under the forward bottom
    let yb = Infinity
    for (const m of this.meshes) {
      if (m.ply || !BOX.has(m.part)) continue
      const pos = m.base.attributes.position
      for (let i = 0; i < pos.count; i++) if (Math.abs(pos.getX(i) - fs) < 3) yb = Math.min(yb, pos.getY(i))
    }
    if (!Number.isFinite(yb)) return
    const top = new THREE.Vector3(fs, yb, 0).applyMatrix4(M)
    const wood = matte(0x6b5038, 0.7, { detail: 4, colorVar: 0.1 })
    const pad = matte(0x3a3d42, 0.9)
    const add = (m: THREE.Material, sx: number, sy: number, sz: number, x: number, y: number, z: number) => {
      const b = new THREE.Mesh(new THREE.BoxGeometry(sx * INCH, sy * INCH, sz * INCH), m)
      b.position.set(x, y, z); b.castShadow = true; b.receiveShadow = true
      this.noseStand.add(b)
    }
    const h = top.y / INCH // inches, floor to the box's bottom
    add(pad, 4, 1, 18, top.x, top.y - 0.5 * INCH, top.z) // the padded saddle
    add(wood, 3.5, 1.5, 20, top.x, top.y - 1.75 * INCH, top.z)
    add(wood, 3.5, h - 4, 3.5, top.x, (1.5 + (h - 4) / 2) * INCH, top.z) // the post, foot to beam
    add(wood, 16, 1.5, 16, top.x, 0.75 * INCH, top.z) // the foot
    this.noseStand.name = 'noseStand'
    this.noseStand.visible = false
    this.noseStand.userData.representational = true
  }

  /**
   * The axle-station marks for the gear positioning (plans-1980:p50 figure 1A), in the box's frame so they turn with it: a dimension
   * from the right datum board's forward face (F.S. 125.5) forward to the axle centre line (F.S. 110.5) at the axle's height, its end
   * ticks, and the station line from there out to the axle. Its labels ("15 in", the axle station) are the page's (main.ts). Only the
   * book's numbers are drawn: the board B.L. and the axle height are book; how far out the axle is (the fitted track) is never labelled.
   */
  private buildMarks() {
    const gm = this.data.gear_marks
    const ax = this.meshes.find((m) => m.part === 'axles')
    if (!gm || !ax) return
    const mat = new THREE.MeshBasicMaterial({ color: 0x2fc4ff, toneMapped: false, depthTest: true })
    const y = gm.axle_z, z = -gm.board_bl // the right board (B.L. +26.75): it faces the room once the box is inverted
    const bar = (x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, th = 0.3) => {
      const b = new THREE.Mesh(new THREE.BoxGeometry(Math.max(Math.abs(x1 - x0), th), Math.max(Math.abs(y1 - y0), th), Math.max(Math.abs(z1 - z0), th)), mat)
      b.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
      b.castShadow = false; b.receiveShadow = false
      this.marks.add(b)
    }
    const xa = gm.axle_fs, xb = gm.board_fs
    bar(xa, y, z, xb, y, z) // the 15 in dimension
    for (const x of [xa, xb]) bar(x, y - 2, z, x, y + 2, z) // its end ticks
    const axleEnd = ax.base.boundingBox!.min.z + 5 // the right axle point: its stub runs 5 in outboard from it (FITTED_AXLE_STUB)
    for (let k = 0, zz = z; zz > axleEnd; k++, zz -= 2) bar(xa, y, zz, xa, y, Math.max(axleEnd, zz - 1.2)) // the station line, dashed
    this.markAt = { dim: new THREE.Vector3((xa + xb) / 2, y, z), axle: new THREE.Vector3(xa, y, axleEnd) }
    this.marks.name = 'gearMarks'
    this.marks.visible = false
  }

  /** the chapter 7 and 9 furniture and marks for the pose the box is in (at rest), and whether the marks are shown */
  private furniture() {
    const rest = this.turnK >= 1
    this.gearTable.visible = rest && this.pose === 'gear-table'
    this.cradles['bank-left-45'].visible = rest && this.pose === 'bank-left-45'
    this.cradles['bank-right-45'].visible = rest && this.pose === 'bank-right-45'
    this.marks.visible = rest && this.marksOn
    // the nose stand holds the nose until the nose gear is on the floor, and again once it is up; while the gear is down or swinging it would be in the way
    this.noseStand.visible = rest && this.pose === 'on-gear' && !(this.noseShown && this.noseT < 1)
  }

  /** the axle-station marks are on (the datum boards are out) */
  get marksShown(): boolean { return this.marks.visible }

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

  /** Put the box in pose `p`: at once, or (`animate`) turning over about its long axis from where it is now, in sim time (stepTurn). */
  setPose(p: JigPose, animate = false) {
    this.toneFor(p)
    if (animate && p !== this.pose && animatedTurn(this.pose, p)) {
      if (this.turnK <= 0) { this.pose = p; this.turnK = 1; this.applyMatrix(this.jigM.get(p)!); this.furniture(); return } // asked back before it started: it never left
      // a turn already under way reverses from where it has got to; a fresh one waits for the camera to come round first
      this.turnK = this.turnK < 1 ? 1 - this.turnK : -FLIP_DELAY / FLIP_SECONDS
      this.turnFrom = this.pose
      this.pose = p
      this.applyTurn()
      this.furniture()
      return
    }
    this.pose = p
    this.turnK = 1
    this.applyMatrix(this.jigM.get(p)!)
    this.furniture()
  }

  /** the turn is under way (or about to start) */
  get turning(): boolean { return this.turnK < 1 }

  /** advance the turn by dt seconds of sim time; true when the box moved (the caller redraws the shadow map) */
  stepTurn(dt: number): boolean {
    if (this.turnK >= 1) return false
    this.turnK = Math.min(1, this.turnK + dt / FLIP_SECONDS)
    this.applyTurn()
    this.furniture()
    return true
  }

  /** the jig frame's matrix for pose `p` at rest (world metres from the box's inches) */
  restMatrix(p: JigPose): THREE.Matrix4 { return this.jigM.get(p) ?? this.jigM.get('upright')! }

  /** the pose for an op (layup.json's bank angles) */
  poseFor(opId: string | null): JigPose { return jigPose(opId, this.order, this.bank) }

  private applyTurn() {
    if (this.turnK >= 1) { this.applyMatrix(this.jigM.get(this.pose)!); return }
    const { angle, lift } = turnPose(this.turnFrom, this.pose, Math.max(0, this.turnK), this.half, this.bank)
    this.applyMatrix(this.poseMatrix(angle, lift))
  }

  /** the dry cloth's tone for the pose the box is in or turning to */
  private toneFor(p: JigPose) { this.dryTone.value = dryTone(p) }

  private applyMatrix(m: THREE.Matrix4) {
    this.jigFrame.matrix.copy(m)
    this.jigFrame.matrixWorldNeedsUpdate = true
    this.jigFrame.updateMatrixWorld(true)
    this.cut.update()
  }

  /** the rotation that lays a carrier flat: a side inside face up, a bulkhead with `face` up, the bottom as it is (inside face up) */
  private flatRotation(carrier: string, face: 'fwd' | 'aft'): THREE.Quaternion {
    const up = new THREE.Vector3(0, 1, 0)
    if (carrier.startsWith('side_')) return new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, isRight(carrier) ? 1 : -1), up)
    // the strut lies flat on its bow (its plane of B.L. and W.L. on the table), its span along the table: FS up, B.L. along the table
    // the roll-over box is glassed inside through its open bottom: it lies upside down on the table until it is bonded on
    if (carrier === 'rollover') return new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI)
    if (carrier === 'strut') return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 1), new THREE.Vector3(1, 0, 0)))
    const fwd = this.data.parts[carrier]?.fwd_normal
    if (!fwd) return new THREE.Quaternion()
    const n = toModel(fwd).normalize()
    if (face === 'aft') n.negate()
    return new THREE.Quaternion().setFromUnitVectors(n, up)
  }

  private carrierGeo(carrier: string): THREE.BufferGeometry | null {
    const node = this.data.parts[carrier]?.node ?? `fuselage.${carrier}`
    return this.meshes.find((m) => m.name === node)?.table.geometry ?? null
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
    const u = carrier.startsWith('side_') || carrier === 'bottom' || carrier === 'strut' ? 0 : this.spots.get(carrier) ?? 0
    const v = SIDE_V[carrier] ?? (carrier === 'bottom' || carrier === 'strut' ? 0 : ROW_V)
    const mid = box.getCenter(new THREE.Vector3())
    const m = new THREE.Matrix4().makeTranslation(T.x + u * INCH, T.topY + 0.0015, T.z + v * INCH)
      .multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeTranslation(-mid.x, -box.min.y, -mid.z))
      .multiply(new THREE.Matrix4().makeRotationFromQuaternion(q))
      .multiply(new THREE.Matrix4().makeTranslation(-c.x, -c.y, -c.z))
    this.tableM.set(key, m)
    return m
  }

  private benchM: THREE.Matrix4 | null = null
  /**
   * The nose-gear box on the jig bench (REPRESENTATIONAL: the book says only that it is built before it goes in the airplane). It lies on its
   * side so it fits the bench: the box frame's (F.S., W.L., B.L.) go to the room's (across the bench, along it, up), the assembly's middle over the
   * bench's middle and its lowest face on the bench top. One rigid matrix for the strut group, the plates and NG6, so they keep their places
   * against each other from the op that makes the first of them until the mount; the frame is the part's own base geometry (strut down).
   */
  benchMatrix(): THREE.Matrix4 {
    if (this.benchM) return this.benchM
    const J = STATION.jig
    const R = new THREE.Matrix4().set(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1) // (x, y, z) -> (y, z, x): a proper rotation
    const box = new THREE.Box3()
    for (const m of this.meshes) if (!m.ply && NG_BENCH.includes(m.cid)) box.union(m.base.boundingBox!.clone().applyMatrix4(R))
    const c = box.getCenter(new THREE.Vector3())
    this.benchM = new THREE.Matrix4().makeTranslation(J.x, J.benchTopY + 0.0015, J.z).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeTranslation(-c.x, -box.min.y, -c.z)).multiply(R)
    return this.benchM
  }

  /** the nose-gear box's whole world box on the bench (every part of it, wherever it is built yet), for the bench shots */
  benchAssemblyBox(): THREE.Box3 {
    const M = this.benchMatrix(), bx = new THREE.Box3()
    for (const m of this.meshes) if (!m.ply && NG_BENCH.includes(m.cid)) bx.union(m.base.boundingBox!.clone().applyMatrix4(M))
    return bx
  }

  /** the face a carrier lies on for this op (the bulkheads turn over between their front and back glassing) */
  faceFor(carrier: string, opId: string | null): 'fwd' | 'aft' {
    return this.data.parts[carrier]?.fwd_normal ? upFace(carrier, opId, this.order, this.data.nodes) : 'fwd'
  }

  placeOf(m: FMesh, opId: string | null): Placement {
    if (m.m25) return m25Place(m.cid, opId, this.order) === 'bench' ? 'table' : 'jig'
    return placement(m.cid, opId, this.order, this.dry)
  }

  opCount(opId: string | null): number {
    return opId ? this.meshes.filter((m) => m.ply?.op === opId).length : 0
  }

  /**
   * Show the build: `state` is visibleSet's answer for the selected op (null: the finished box). `backdrop` (with no state): the box
   * as it stands after that op, every part and ply made by then built and nothing later, which is how the canard subject shows its
   * corner of the shop (the chapter 6 box on the jig, as it always has: the finished airplane on the floor would walk into the
   * canard's frames). Returns a signature of what casts shadows, so the caller can redraw the shadow map only when it changed.
   */
  paint(state: Map<string, BuildState> | null, opId: string | null, lay: number, layT: number, ghost: boolean, opIdx: Map<string, number>, backdrop: string | null = null): string {
    const back = !state && backdrop && this.order.includes(backdrop) ? backdrop : null
    const sel = state ? opId : back
    const pose = this.poseFor(sel)
    if (pose !== this.pose) this.setPose(pose)
    const chapter = sel ? this.opChapter.get(sel) ?? -1 : -1
    const noseOn = chapter === NOSE_CHAPTER
    const m25On = M25_CHAPTERS.has(chapter) && !!state
    this.m25Chapter = m25On
    const selOp = sel ? this.opOf.get(sel) ?? null : null
    const boxGhost = m25On && boxGhostAt(selOp)
    // the spar is built on the layup table (chapter 14's bench ops): the box stands on the jig bench between the camera and it, so it is not drawn then
    const benchOps = m25On && !!sel && this.order.indexOf(sel) >= this.order.indexOf(M25_FIRST_OP) && this.order.indexOf(sel) <= this.order.indexOf(SPAR_BENCH_LAST)
    const cur = state && sel ? opIdx.get(sel) : undefined, count = this.opCount(sel)
    const bi = back ? this.order.indexOf(back) : -1
    const madeBy = (m: FMesh) => (m.ply ? this.order.indexOf(m.ply.op) : this.firstIdx.get(m.cid) ?? Infinity) <= bi
    let sig = pose
    let boards = false
    for (const m of this.meshes) {
      const st: BuildState = state ? state.get(m.name) ?? 'hidden' : back ? (madeBy(m) ? 'built' : 'hidden') : 'built'
      const ph = m.ply && cur !== undefined
        ? plyPhase({ meshOpIndex: opIdx.get(m.ply.op), curOpIndex: cur, order: m.ply.order, lay, count, t: layT, ghost })
        : partPhase(st)
      this.phases.set(m.name, ph)
      // the nose-gear box lies on the jig bench until it is mounted on F22 (logic/fuselage.ts onBench): drawn there from its own op on
      const benched = st !== 'ghost' && !m.ply && onBench(m.cid, sel, this.order)
      const where = st === 'ghost' ? 'jig' : benched ? 'table' : this.placeOf(m, sel)
      const shown = st !== 'hidden' && !(m.ply && st === 'current' && ph.unroll <= 0) && (benched || shownAt(m.show, sel, this.order)) && !(m.jigOnly && where === 'table' && !benched) && (!m.extra || noseOn) && (!m.m25 || m25On) && !(benchOps && !m.m25 && where === 'jig')
      // the shape for this op: the node's own, or a later stage (carved, cut, holed)
      const stage = stageAt(m.stages.map((s) => ({ from: s.from, node: s.node })), sel, this.order)
      const geo = stage ? m.stages.find((s) => s.node === stage)!.geo : m.base
      if (m.jig.geometry !== geo) this.swapGeometry(m.jig, geo)
      if (stage) sig += stage
      if (m.void) m.jig.position.y = VOID_LIFT
      m.jig.visible = shown && where === 'jig'
      m.table.visible = shown && where === 'table'
      if (m.part === 'datum_board' && m.jig.visible) boards = true
      if (m.table.visible) {
        const face = this.faceFor(m.carrier, sel)
        m.table.matrix.copy(benched ? this.benchMatrix() : m.m25 ? this.sparBenchMatrix(this.sparStand(sel)) : this.tableMatrix(m.carrier, face))
        m.table.matrixWorldNeedsUpdate = true
        sig += m.carrier + face + (benched ? 'b' : '')
      }
      const cast = st === 'built' || (st === 'current' && ph.unroll >= 1)
      m.jig.castShadow = m.table.castShadow = cast
      const look = { unroll: ph.unroll, front: ph.front, cure: ph.cure, ghost: st === 'ghost' || (boxGhost && m.part === 'spar_box') }
      setPlyLook(m.jigMat, look)
      setPlyLook(m.tableMat, look)
      sig += (m.jig.visible ? 'j' : m.table.visible ? 't' : '-') + (cast ? '1' : '0')
    }
    this.tableGroup.updateMatrixWorld(true)
    // the wheels go on with the finished box, standing on them (the axles are on by then)
    const axles = this.meshes.find((m) => m.part === 'axles')
    this.wheels.visible = this.pose === 'on-gear' && !!axles?.jig.visible
    sig += this.wheels.visible ? 'w' : ''
    this.marksOn = boards
    // chapters 12-13: the canard and the elevators stand installed on the airplane (never on a chapter 4-9 op, nor on the finished ch 4-9 box)
    this.installed.visible = !!state && (CANARD_INSTALLED_CHAPTERS.has(chapter) || (!!sel && ELEV_OPS.has(sel)))
    this.stops.visible = m25On && !!sel && this.order.indexOf(sel) >= this.order.indexOf(STOPS_FROM)
    this.applyM25()
    sig += this.installed.visible ? 'c' : ''
    const strut = this.meshes.find((m) => m.part === 'gear_nose_strut')
    this.noseShown = !!strut?.jig.visible
    this.ghost.visible = this.noseShown
    this.applyNose()
    sig += this.noseShown ? 'n' + this.noseT.toFixed(3) : ''
    this.furniture()
    return sig + (boards ? 'm' : '') + (this.gearTable.visible ? 'g' : '') + (this.cradles['bank-left-45'].visible ? 'l' : '') + (this.cradles['bank-right-45'].visible ? 'r' : '')
  }

  /** put a stage's shape on a jig mesh; while the station cut is open its mesh draws two material groups (core/cut.ts), so the new shape gets them too */
  private swapGeometry(mesh: THREE.Mesh, geo: THREE.BufferGeometry) {
    const old = mesh.geometry
    if (old.groups.length) {
      const count = geo.index ? geo.index.count : geo.attributes.position.count
      geo.clearGroups()
      for (const g of old.groups) geo.addGroup(0, count, g.materialIndex)
    } else geo.clearGroups()
    mesh.geometry = geo
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
    if (!m.ply && onBench(m.cid, opId, this.order)) return m.base.boundingBox!.clone().applyMatrix4(this.benchMatrix())
    const where = this.placeOf(m, opId)
    const mat = where === 'jig'
      ? this.restMatrix(this.poseFor(opId))
      : m.m25 ? this.sparBenchMatrix(this.sparStand(opId)) : this.tableMatrix(m.carrier, this.faceFor(m.carrier, opId))
    const g = where === 'jig' ? m.base : m.table.geometry
    return g.boundingBox!.clone().applyMatrix4(mat)
  }

  /** the lab shot for every fuselage op (world metres), aimed where the op's parts are for that op */
  shots(ops: string[], fov: number): Record<string, Shot> {
    const out: Record<string, Shot> = {}
    for (const id of ops) {
      const v = fuseView(id)
      const target = new THREE.Vector3()
      if (v.focus === 'bench') {
        target.copy(this.benchAssemblyBox().getCenter(new THREE.Vector3()))
      } else if (v.focus === 'marks' && this.markAt) {
        target.copy(this.markAt.dim).lerp(this.markAt.axle, 0.5).applyMatrix4(this.restMatrix(this.poseFor(id))) // both marks' words in frame
      } else if (typeof v.focus === 'object' && 'spar' in v.focus) {
        // the spar at B.L. `bl` (model z = -bl): on the bench, or (ops from the fit on) installed in the box
        const bench = m25Place('spar.box', id, this.order) === 'bench'
        // the span runs the other way on the bench once the box is turned about (sparBenchMatrix): the same B.L. stays at the same end of the spar
        const p = new THREE.Vector3(121.7, 0.35, -v.focus.spar)
        target.copy(p).applyMatrix4(bench ? this.sparBenchMatrix(this.sparStand(id)) : this.restMatrix(this.poseFor(id)))
      } else if (typeof v.focus === 'object' && 'at' in v.focus) {
        target.set(...v.focus.at).applyMatrix4(this.restMatrix(this.poseFor(id)))
      } else if (v.focus === 'box' || v.focus === 'marks') {
        const bx = new THREE.Box3()
        for (const m of this.meshes) if (!m.ply && BOX.has(m.part) && this.placeOf(m, id) === 'jig' && this.isMade(m, id)) bx.union(this.worldBoxAt(m, id))
        if (bx.isEmpty()) target.set(STATION.jig.x, blockTopY() + 0.25, STATION.jig.z); else bx.getCenter(target)
      } else {
        const ms = v.focus.parts.map((p) => this.meshes.find((m) => m.part === p && !m.ply)).filter((m): m is FMesh => !!m)
        if (v.focus.fs !== undefined && ms.length) {
          const m = ms[0], where = this.placeOf(m, id)
          const g = where === 'jig' ? m.base : m.table.geometry
          const c = g.boundingBox!.getCenter(new THREE.Vector3())
          c.x = v.focus.fs
          const mat = where === 'jig' ? this.restMatrix(this.poseFor(id)) : this.tableMatrix(m.carrier, this.faceFor(m.carrier, id))
          target.copy(c.applyMatrix4(mat))
        } else if (v.focus.side && ms.length) { // one half of the part (B.L. > 0 is model z < 0): one axle, one leg
          const right = v.focus.side === 'right'
          const bx = new THREE.Box3(), q = new THREE.Vector3()
          for (const m of ms) {
            const where = this.placeOf(m, id)
            const g = where === 'jig' ? m.base : m.table.geometry
            const mat = where === 'jig' ? this.restMatrix(this.poseFor(id)) : this.tableMatrix(m.carrier, this.faceFor(m.carrier, id))
            const pos = g.attributes.position
            for (let i = 0; i < pos.count; i++) if ((pos.getZ(i) < 0) === right) bx.expandByPoint(q.fromBufferAttribute(pos, i).applyMatrix4(mat))
          }
          bx.getCenter(target)
        } else {
          const bx = new THREE.Box3()
          for (const m of ms) bx.union(this.worldBoxAt(m, id))
          bx.getCenter(target)
        }
      }
      const off = viewOffset(v)
      if (v.pan) {
        // move the aim sideways (along the camera's right) so the subject stands left of the middle, clear of the control card on the right
        const right = new THREE.Vector3(off[0], 0, off[2]).normalize().cross(new THREE.Vector3(0, 1, 0)).negate().multiplyScalar(v.pan * INCH)
        target.add(right)
      }
      if (v.up) target.y -= v.up * INCH
      const pos = target.clone().add(new THREE.Vector3(off[0], off[1], off[2]).multiplyScalar(INCH))
      out[id] = { pos: [pos.x, pos.y, pos.z], target: [target.x, target.y, target.z], fov }
    }
    return out
  }

  /** the close shot of the station cut at `fs`: forward of the plane, a little above, looking aft at the face (world metres; the finished box, right side up) */
  cutShot(fs: number, fov: number, opId: string | null = null, view: { dist?: number; lift?: number } = {}): Shot {
    const bx = new THREE.Box3() // the box as `opId` leaves it (the chapter's last op: on the jig, not the finished airplane on its gear that `null` now means)
    for (const m of this.meshes) if (!m.ply && BOX.has(m.part) && this.placeOf(m, opId) === 'jig' && (opId === null || this.isMade(m, opId))) bx.union(this.worldBoxAt(m, opId))
    const target = bx.isEmpty() ? new THREE.Vector3(STATION.jig.x, blockTopY() + 0.25, STATION.jig.z) : bx.getCenter(new THREE.Vector3())
    target.x = fsToX(fs)
    target.y += view.lift ?? 0
    const off = viewOffset({ focus: 'box', dist: view.dist ?? 58, el: 24, az: 72 })
    const pos = target.clone().add(new THREE.Vector3(off[0], off[1], off[2]).multiplyScalar(INCH))
    return { pos: [pos.x, pos.y, pos.z], target: [target.x, target.y, target.z], fov }
  }

  /** the component's first op is `opId`: it is new on that op */
  isNewOn(cid: string, opId: string | null): boolean {
    return !!opId && this.firstIdx.get(cid) === this.order.indexOf(opId)
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

  /** the finished box on its own feet (world metres): every part of it, the wheels and the nose stand, for its home shot */
  finishedBox(): THREE.Box3 {
    const M = this.restMatrix('on-gear'), bx = new THREE.Box3()
    for (const m of this.meshes) if (!m.ply && !m.m25 && this.placeOf(m, null) === 'jig' && shownAt(m.show, null, this.order)) bx.union(m.base.boundingBox!.clone().applyMatrix4(M))
    for (const w of this.wheels.children) bx.union(((w as THREE.Mesh).geometry.boundingBox ?? ((w as THREE.Mesh).geometry.computeBoundingBox(), (w as THREE.Mesh).geometry.boundingBox!)).clone().translate(w.position).applyMatrix4(M))
    bx.expandByPoint(new THREE.Vector3(bx.min.x, 0, bx.min.z))
    return bx
  }

  /** the jig bench's world box, legs and blocks included (scene/fuselageStation.ts) */
  benchBox(): THREE.Box3 {
    const J = STATION.jig
    return new THREE.Box3(new THREE.Vector3(J.x - J.benchLen / 2, 0, J.z - J.benchDepth / 2), new THREE.Vector3(J.x + J.benchLen / 2, blockTopY(), J.z + J.benchDepth / 2))
  }

  /** where the wheels' label hangs (world metres, as the box is now), or null with no wheels shown */
  wheelAnchor(out: THREE.Vector3): THREE.Vector3 | null {
    if (!this.wheels.visible || !this.wheelTop) return null
    return out.copy(this.wheelTop).applyMatrix4(this.jigFrame.matrixWorld)
  }

  // ---- chapters 14-17: the spar on the bench and sliding in, the stick and the elevators it drives, the pitch stops ----

  /** the spar's parts (the jig too, while it is shown) as a box in the model frame, inches */
  private sparBox(withJig: boolean, withCaps = true): THREE.Box3 {
    const bx = new THREE.Box3()
    for (const m of this.meshes) if (m.m25 && SPAR_COMPONENTS.has(m.cid) && (withJig || m.cid !== 'spar.jig') && (withCaps || !m.cid.startsWith('spar.cap_'))) bx.union(m.base.boundingBox!)
    return bx
  }
  /** the bench stand of the spar for an op: whether its jig is there and whether the caps are laid (the box rests on its bottom cap once that is on) */
  sparStand(opId: string | null): { jig: boolean; caps: boolean } {
    return { jig: shownAt(this.data.parts.spar_jig?.show, opId, this.order), caps: !!opId && this.order.indexOf(opId) >= this.order.indexOf('f14.spar-caps') }
  }

  /**
   * The spar on the layup table (REPRESENTATIONAL: the book builds it in a jig on a bench, and does not say where): its span along the table's
   * length, the aft face (and the jig's upright) toward the wall while it is in its jig, and turned about to face the room (the aft face is
   * where the fittings, the web and the caps go) once the box is lifted out; the lowest thing it stands on (the jig's shelf, or the spar's own bottom
   * once the box is lifted from the jig) on the table top. Rotated a quarter turn about the vertical from the installed frame.
   */
  sparBenchMatrix(stand: { jig: boolean; caps: boolean }): THREE.Matrix4 {
    const key = `${stand.jig}${stand.caps}`
    let M = this.sparBenchM.get(key)
    if (M) return M
    const T = STATION.table, bx = this.sparBox(stand.jig, stand.caps), c = this.sparBox(true, true).getCenter(new THREE.Vector3())
    M = new THREE.Matrix4().makeTranslation(T.x, T.topY + 0.002, T.z + 0.5).multiply(new THREE.Matrix4().makeScale(INCH, INCH, INCH))
      .multiply(new THREE.Matrix4().makeRotationY(stand.jig ? Math.PI / 2 : -Math.PI / 2)).multiply(new THREE.Matrix4().makeTranslation(-c.x, -bx.min.y, -c.z))
    this.sparBenchM.set(key, M)
    return M
  }

  /** the spar as it stands on the bench for `opId`, in the world (metres); null with no spar parts */
  sparBenchWorldBox(stand: { jig: boolean; caps: boolean }): THREE.Box3 {
    return this.sparBox(stand.jig, true).clone().applyMatrix4(this.sparBenchMatrix(stand))
  }

  /** how far (inches along the span) the spar starts from, clear of the box on the room side, for the slide-in */
  slideDistance(): number {
    const bx = this.sparBox(false)
    return (bx.max.z - bx.min.z) / 2 + this.half.w + 6
  }

  /** the slide-in's progress (0 clear of the box, 1 installed) */
  setSparSlide(progress: number) {
    const s = (1 - Math.min(1, Math.max(0, progress))) * this.slideDistance()
    if (s === this.slide) return
    this.slide = s
    this.applyM25()
  }
  get sparSlideInches(): number { return this.slide }

  /** the elevator deflection the stick sits at (up positive, Roncz travel) */
  setStick(deflUp: number) {
    if (deflUp === this.deflUp) return
    this.deflUp = deflUp
    this.applyM25()
  }
  get stickDeflUp(): number { return this.deflUp }

  /** a point in the box frame (python frame: x = F.S., y = B.L., z up) as the model frame */
  private pm(p: [number, number, number]): THREE.Vector3 { return new THREE.Vector3(p[0], p[2], -p[1]) }
  private stickBase(which: 'front' | 'rear'): [number, number, number] {
    const k = this.ctl!
    return [k.pivot_fs[which], k.tube_bl, k.tube_wl - k.wl_zero]
  }

  /** set every chapter 14-17 mesh's own motion: the spar's slide, the sticks' pitch about their pivot, the pushrod with the stick's lever, the elevators */
  private applyM25() {
    const k = this.ctl
    const a0 = k ? stickAngleDeg(0, k) : 0, a = k ? stickAngleDeg(this.deflUp, k) : 0
    const rod = (ang: number, which: 'front' | 'rear') => {
      const d = stickDir(ang, k!.cant_inboard_deg), b = this.stickBase(which)
      return [b[0] + d[0] * k!.lever_in, b[1] + d[1] * k!.lever_in, b[2] + d[2] * k!.lever_in] as [number, number, number]
    }
    for (const m of this.meshes) {
      if (!m.m25) continue
      const mat = new THREE.Matrix4()
      if (FIREWALL_FACE.has(m.cid)) mat.makeTranslation(this.firewallAside, 0, 0)
      else if (SLIDES(m.cid)) mat.makeTranslation(0, 0, this.slide)
      else if (k && STICKS.has(m.part)) {
        const base = this.pm(this.stickBase(m.part === 'controls_sticks_front_stick' ? 'front' : 'rear'))
        mat.makeTranslation(base.x, base.y, base.z).multiply(new THREE.Matrix4().makeRotationZ(((a - a0) * Math.PI) / 180)).multiply(new THREE.Matrix4().makeTranslation(-base.x, -base.y, -base.z))
      } else if (k && m.part === 'controls_pitch_pushrod') {
        const r0 = this.pm(rod(a0, 'front')), r1 = this.pm(rod(a, 'front'))
        mat.makeTranslation(r1.x - r0.x, r1.y - r0.y, r1.z - r0.z)
      }
      m.jig.matrixAutoUpdate = false
      m.jig.matrix.copy(mat)
      m.jig.matrixWorldNeedsUpdate = true
    }
    this.applyElevators()
    this.jigFrame.updateMatrixWorld(true)
  }

  /** the installed elevators turn about their hinge line with the stick (TE down = the stick forward); the hinges stay on the canard */
  private applyElevators() {
    const el = this.data.extras?.elevators
    if (!el) return
    const [hx, hz] = el.hinge_xz
    const degDown = -this.deflUp
    const m = new THREE.Matrix4().makeTranslation(hx, hz, 0).multiply(new THREE.Matrix4().makeRotationZ((-degDown * Math.PI) / 180)).multiply(new THREE.Matrix4().makeTranslation(-hx, -hz, 0))
    for (const mesh of this.installedMeshes()) {
      if (!mesh.name.startsWith('installed:elevator.') || mesh.name.includes('hinges')) continue
      mesh.matrixAutoUpdate = false
      mesh.matrix.copy(m)
      mesh.matrixWorldNeedsUpdate = true
    }
  }

  /** the stick's pitch stops: two small blocks at the front stick's travel limits (fitted, striped; the book prints none) */
  private buildStops() {
    const k = this.ctl
    if (!k) return
    const mat = partMaterial(this.cut, { color: 0xb98f5c, hatch: true, name: 'pitch-stop' })
    const [sx, sy, sz] = k.stop_size_in
    const base = this.stickBase('front')
    for (const defl of [k.up_target_deg, -k.down_deg]) {
      const sgn = defl > 0 ? 1 : -1 // beyond the limit: further aft for the up limit, further forward for the down
      const ang = stickAngleDeg(defl, k) + (defl > 0 ? -1 : 1) * 4
      void sgn
      const d = stickDir(ang, k.cant_inboard_deg)
      const p = this.pm([base[0] + d[0] * k.lever_in, base[1] + d[1] * k.lever_in, base[2] + d[2] * k.lever_in])
      const b = new THREE.Mesh(new THREE.BoxGeometry(sx, sz, sy), mat)
      b.position.copy(p)
      b.castShadow = true; b.receiveShadow = true
      this.stops.add(b)
    }
    this.stops.name = 'controls.pitch_stops'
    this.stops.visible = false
    this.stops.userData.representational = true
    this.stops.userData.hatch = true
  }

  /** the stops' label anchor (world metres), or null while they are not drawn */
  stopsAnchor(out: THREE.Vector3): THREE.Vector3 | null {
    if (!this.stops.visible || !this.stops.children.length) return null
    const c = new THREE.Vector3()
    for (const b of this.stops.children) c.add(b.position)
    c.multiplyScalar(1 / this.stops.children.length).add(new THREE.Vector3(0, 1.4, 0))
    return out.copy(c).applyMatrix4(this.jigFrame.matrixWorld)
  }

  // ---- chapters 12-13: the installed canard, the nose gear's retraction and its other axle candidate ----

  /**
   * Put the canard and elevators on the airplane (shown for chapters 12-13). `items` are meshes the caller built (materials follow this bay's
   * station cut; geometry is the caller's own copy, since a cut rewrites its meshes' groups). The canard's frame (x chord, y up, z = -B.L.)
   * is the box's frame, so the group only translates: its leading edge at F.S. `fs_le` and `z_le` above the wing plane (layup.json
   * "extras".canard_install), at zero incidence to the longerons (book; config canard_incidence is unsourced and is not used).
   * `left` items are the mirror image (z scaled by -1); `both: false` items (the left elevator) are placed as they come.
   */
  attachInstalled(items: { mesh: THREE.Mesh; mirror: boolean }[]) {
    const ci = this.data.extras?.canard_install
    this.installed.position.set(ci?.fs_le ?? 18.7, ci?.z_le ?? 1.5, 0)
    this.installedBaseY = this.installed.position.y
    for (const { mesh, mirror } of items) {
      if (mirror) mesh.scale.z = -1
      mesh.castShadow = true; mesh.receiveShadow = true
      this.installed.add(mesh)
    }
    this.cut.collect(this.jigFrame)
    this.cut.update()
  }

  private installedBaseY = 0
  /** hold the installed canard `inches` above its installed pose (the canard12 film's lowering); 0 is the installed pose exactly */
  setInstalledLift(inches: number) {
    this.installed.position.y = this.installedBaseY + inches
    this.installed.updateMatrixWorld(true)
  }
  /** the installed canard's box in the box (jig) frame, inches, held `lift` inches above its installed pose */
  installedBox(lift = 0): THREE.Box3 {
    const bx = new THREE.Box3()
    for (const m of this.installedMeshes()) {
      m.updateMatrix()
      if (!m.geometry.boundingBox) m.geometry.computeBoundingBox()
      bx.union(m.geometry.boundingBox!.clone().applyMatrix4(m.matrix))
    }
    return bx.translate(new THREE.Vector3(this.installed.position.x, this.installedBaseY + lift, this.installed.position.z))
  }

  /** a part of the installed canard group by mesh name */
  installedMeshes(): THREE.Mesh[] { return this.installed.children.filter((c): c is THREE.Mesh => (c as THREE.Mesh).isMesh) }

  /** the nose gear's retraction progress (0 down, 1 up) is now `t` */
  setNose(t: number) {
    if (t === this.noseT) return
    this.noseT = t
    this.applyNose()
    this.furniture()
  }
  get noseProgress(): number { return this.noseT }
  /** the nose gear's strut is drawn now (a chapter 13 op from the one that makes it) */
  get nosePresent(): boolean { return this.noseShown }

  /** the other axle candidate: a ghost wheel and a ghost strut, striped like every fitted part and drawn faint (it is a possibility, not the model) */
  private buildGhost() {
    const k = this.noseK
    if (!k) return
    const mat = partMaterial(this.cut, { color: 0xc8ccd2, hatch: true, name: 'nose-ghost' })
    setPlyLook(mat, { unroll: 1, front: 1, cure: 1, ghost: true })
    const R = k.tire_od / 2, tube = k.tire_width / 2
    const wheel = new THREE.Mesh(new THREE.TorusGeometry(R - tube, tube, 14, 40), mat)
    const strut = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1.8), mat)
    for (const m of [wheel, strut]) { m.castShadow = false; m.receiveShadow = false; this.ghost.add(m) }
    this.ghostWheel = wheel; this.ghostStrut = strut
    this.ghost.name = 'noseGhost'
    this.ghost.visible = false
    this.ghost.userData.representational = true
    this.ghost.userData.hatch = true
  }

  /** the strut group's matrix about the NG6 pivot at progress `noseT` (jig frame: x = F.S., y up), and the ghost's */
  private applyNose() {
    const pts = this.nosePts
    if (!pts) return
    const t = this.noseT
    const strut = this.meshes.find((m) => m.part === 'gear_nose_strut')
    if (strut) {
      const p = nosePose(t, pts.plans)
      strut.jig.matrixAutoUpdate = false
      strut.jig.matrix.set(p.r[0], p.r[1], 0, p.tx, p.r[2], p.r[3], 0, p.tz, 0, 0, 1, 0, 0, 0, 0, 1)
      strut.jig.matrixWorldNeedsUpdate = true
    }
    if (this.ghostWheel && this.ghostStrut) {
      const g = pts.manual
      const [ax, az] = noseAxleAt(t, g)
      this.ghostWheel.position.set(ax, az, 0)
      const [px, pz] = g.pivot
      const len = Math.hypot(ax - px, az - pz)
      this.ghostStrut.scale.set(1, len, 1.8)
      this.ghostStrut.position.set((ax + px) / 2, (az + pz) / 2, 0)
      this.ghostStrut.rotation.set(0, 0, Math.atan2(az - pz, ax - px) - Math.PI / 2)
    }
    this.jigFrame.updateMatrixWorld(true)
  }

  /** where a candidate's wheel centre is now (the box's frame, inches) */
  noseWheelAt(cand: Candidate): [number, number] | null {
    return this.nosePts ? noseAxleAt(this.noseT, this.nosePts[cand]) : null
  }
  /** a point on a candidate's wheel for its label (world metres), or null with no nose gear shown: above the drawn wheel's top, and below the ghost's bottom,
   * so the two pills (the wheels are only 3 in apart) never share a place and the declutter rule has room for both */
  noseWheelAnchor(cand: Candidate, out: THREE.Vector3): THREE.Vector3 | null {
    const c = this.noseWheelAt(cand)
    if (!c || !this.noseShown || !this.nosePts) return null
    const R = (this.noseK?.tire_od ?? 9) / 2
    return out.set(c[0], cand === 'plans' ? c[1] + R : c[1] - R, cand === 'plans' ? -1 : 1).applyMatrix4(this.jigFrame.matrixWorld)
  }

  labelColor(m: FMesh): string {
    const c = m.hatch ? HATCH_COLOR : WOOD[m.part] ?? METAL[m.part]?.[0] ?? COLORS.foam
    return '#' + c.toString(16).padStart(6, '0')
  }
}
