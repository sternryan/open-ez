import * as THREE from 'three'
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'
import { matte, surf } from '../core/materials'
import { roomPlanes, type RoomPlane } from '../logic/roomCull'

/**
 * Our own build shop, procedural and merged to one draw call per material. World units are metres, +Y up.
 * The table is centred on the origin with its long axis along Z; the back wall is at +X, a window wall at -Z.
 * Everything here is static, so the shadow map is rendered once.
 */
export const TABLE_TOP_Y = 0.9
export const ROOM = { x0: -6.6, x1: 2.9, z0: -4.2, z1: 4.2, h: 3.3 }
/** Fixture positions, shared with the environment map so reflections match the room. */
export const FIXTURES: { x: number; z: number }[] = [-2.2, 0, 2.2].flatMap((z) => [-0.5, 1.3].map((x) => ({ x, z })))
export const FIXTURE_Y = ROOM.h - 0.12
export const FIXTURE_LEN = 1.3
export const WINDOW = { z: ROOM.z0, x: 0.4, y: 1.85, w: 2.4, h: 1.4 }

export interface Workshop {
  group: THREE.Group
  jigTopY: number
  /** world centres of the jig blocks along Z (representational, see below) */
  jigZ: number[]
  /** the room's wall planes (inward normals), for the per-frame cull */
  planes: RoomPlane[]
  /** one group per plane key; everything fixed to that plane lives in it, so hiding the group hides the plane's props too */
  planeGroups: Record<string, THREE.Group>
  /** the cull's one switch. Eye inside the room (nothing hidden): the whole room is drawn from one merged mesh per material (the draw count of a room with no groups).
   *  Some plane hidden: the plane groups (each visible unless hidden), the rest of the shop, and the ground apron are drawn instead. */
  setHidden(hidden: ReadonlySet<string>): void
}

export class Batch {
  private m = new Map<string, { key: string; plane: string; mat: THREE.Material; geos: THREE.BufferGeometry[] }>()
  /** plane group that following adds belong to ('' = the shop group itself); merged per (plane, material) */
  plane = ''
  constructor(private mats: Record<string, THREE.Material>) {}
  add(key: string, geo: THREE.BufferGeometry, x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0) {
    geo.applyMatrix4(new THREE.Matrix4().compose(new THREE.Vector3(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(rx, ry, rz)), new THREE.Vector3(1, 1, 1)))
    const g = geo.index ? geo.toNonIndexed() : geo
    for (const n of Object.keys(g.attributes)) if (n !== 'position' && n !== 'normal' && n !== 'uv') g.deleteAttribute(n)
    const id = `${this.plane}|${key}`
    if (!this.m.has(id)) this.m.set(id, { key, plane: this.plane, mat: this.mats[key], geos: [] })
    this.m.get(id)!.geos.push(g)
  }
  box(key: string, w: number, h: number, d: number, x: number, y: number, z: number, ry = 0) { this.add(key, new THREE.BoxGeometry(w, h, d), x, y, z, 0, ry, 0) }
  /** cylinder along an axis: 'x' | 'y' | 'z' */
  cyl(key: string, r: number, len: number, axis: 'x' | 'y' | 'z', x: number, y: number, z: number, seg = 16) {
    this.add(key, new THREE.CylinderGeometry(r, r, len, seg), x, y, z, axis === 'z' ? Math.PI / 2 : 0, 0, axis === 'x' ? Math.PI / 2 : 0)
  }
  /** One merged mesh per material (`shop.<key>`) holding everything, as with no planes at all, and, only for materials that have plane-bound parts,
   *  per-plane meshes in the plane groups plus a `.rest` mesh of the unbound parts. The cull shows either the first or the second set (see Workshop.setHidden). */
  flush(group: THREE.Group, shadow: { cast: Set<string>; receive: Set<string> }, planeGroups: Record<string, THREE.Group> = {}) {
    const mk = (key: string, geos: THREE.BufferGeometry[], name: string) => {
      const mesh = new THREE.Mesh(mergeGeometries(geos, false)!, this.mats[key])
      mesh.name = name
      mesh.castShadow = shadow.cast.has(key)
      mesh.receiveShadow = shadow.receive.has(key)
      return mesh
    }
    const byKey = new Map<string, { plane: string; geos: THREE.BufferGeometry[] }[]>()
    for (const { key, plane, geos } of this.m.values()) byKey.set(key, [...(byKey.get(key) ?? []), { plane, geos }])
    const combined: THREE.Mesh[] = [], split: THREE.Mesh[] = []
    for (const [key, parts] of byKey) {
      const all = mk(key, parts.flatMap((p) => p.geos), `shop.${key}`)
      group.add(all); combined.push(all)
      if (!parts.some((p) => p.plane)) continue
      for (const { plane, geos } of parts) {
        const m = mk(key, geos, plane ? `shop.${key}` : `shop.${key}.rest`)
        ;(plane ? planeGroups[plane] : group).add(m)
        if (!plane) split.push(m)
      }
    }
    return { combined, rest: split }
  }
}

export function pegTexture(): THREE.CanvasTexture {
  const c = document.createElement('canvas')
  c.width = c.height = 64
  const g = c.getContext('2d')!
  g.fillStyle = '#c9b18d'
  g.fillRect(0, 0, 64, 64)
  g.fillStyle = '#2a2018'
  for (const [x, y] of [[16, 16], [48, 16], [16, 48], [48, 48]]) { g.beginPath(); g.arc(x, y, 4.5, 0, 7); g.fill() }
  const t = new THREE.CanvasTexture(c)
  t.wrapS = t.wrapT = THREE.RepeatWrapping
  t.repeat.set(20, 9)
  t.colorSpace = THREE.SRGBColorSpace
  t.anisotropy = 4
  return t
}

export const glow = (hex: number, k: number) => new THREE.MeshBasicMaterial({ color: new THREE.Color(hex).multiplyScalar(k) })

/**
 * @param span   length of the modelled canard along Z, metres
 * @param chord  chord along X, metres
 * Jig blocks are REPRESENTATIONAL: the plans graph names no jig stations for chapter 30, so a few evenly spaced
 * blocks stand in for the jig. They carry userData.representational = true.
 */
export function buildWorkshop(span: number, chord: number): Workshop {
  const group = new THREE.Group()
  group.name = 'workshop'
  const R = ROOM
  const M: Record<string, THREE.Material> = {
    floor: surf({ color: 0x77736c, metalness: 0, roughness: 0.62, detail: 1.3, colorVar: 0.2, roughVar: 0.5, name: 'concrete' }),
    seam: matte(0x35322e, 0.9),
    apron: matte(0x4d4a45, 1), // the ground beyond the slab, for outside shots: close to the concrete, darker, matte
    wall: matte(0xb4b8bd, 0.92, { detail: 0.8, colorVar: 0.07 }),
    wainscot: matte(0x3f5866, 0.7, { detail: 1.5, colorVar: 0.05 }),
    ceiling: matte(0x6a6d72, 0.95),
    beam: matte(0x3a3d42, 0.7),
    wood: surf({ color: 0x5a3f2e, metalness: 0, roughness: 0.55, detail: 5, colorVar: 0.14, roughVar: 0.25, name: 'plywood' }),
    steel: surf({ color: 0x9aa0a6, metalness: 0.9, roughness: 0.32, detail: 3, roughVar: 0.3 }),
    darksteel: surf({ color: 0x2c2f33, metalness: 0.75, roughness: 0.45, detail: 2 }),
    jig: surf({ color: 0xb48a58, metalness: 0, roughness: 0.62, detail: 9, colorVar: 0.16, roughVar: 0.3, name: 'mdf' }), // MDF/plywood cradle blocks
    peg: surf({ color: 0xffffff, metalness: 0, roughness: 0.85, map: pegTexture() }),
    red: matte(0xb3261e, 0.5), orange: matte(0xdb7a1c, 0.5), yellow: matte(0xd8b62a, 0.55), blue: matte(0x2b5e8c, 0.6),
    chest: surf({ color: 0xa3261f, metalness: 0.3, roughness: 0.4, detail: 2 }),
    tyre: matte(0x141414, 0.9),
    cloth: matte(0xd9d2bd, 0.95, { detail: 6, colorVar: 0.08 }),
    carbon: matte(0x26272a, 0.8),
    bin: matte(0x556069, 0.7),
    binb: matte(0x3d6a86, 0.7),
    housing: matte(0x2b2c2f, 0.6),
    tube: glow(0xfff0dc, 5.5),
    win: glow(0xd2e6ff, 3.2),
    frame: matte(0xd8dadc, 0.6),
    led: glow(0x2ee6c8, 3.5),
    lamp: glow(0xffb45a, 4),
  }
  const B = new Batch(M)
  const planes = roomPlanes(R)
  const planeGroups: Record<string, THREE.Group> = {}
  for (const p of planes) { const g = new THREE.Group(); g.name = p.key; planeGroups[p.key] = g; group.add(g) }

  // ---- shell: floor with slab seams, walls, wainscot, ceiling, beams ----
  const W = R.x1 - R.x0, D = R.z1 - R.z0, cx = (R.x0 + R.x1) / 2, cz = (R.z0 + R.z1) / 2
  B.box('floor', W, 0.2, D, cx, -0.1, cz)
  for (let x = R.x0 + 1.25; x < R.x1; x += 2.5) B.box('seam', 0.012, 0.004, D, x, 0.001, cz)
  for (let z = R.z0 + 1.2; z < R.z1; z += 2.4) B.box('seam', W, 0.004, 0.012, cx, 0.001, z)
  // a wall slab plus a darker wainscot on its room side; (nx, nz) points into the room
  const wall = (plane: string, x: number, z: number, w: number, d: number, nx: number, nz: number) => {
    B.plane = plane
    B.box('wall', w, R.h, d, x, R.h / 2, z)
    B.box('wainscot', w + (nx ? 0.03 : 0), 1.05, d + (nz ? 0.03 : 0), x + nx * 0.015, 0.525, z + nz * 0.015)
  }
  wall('room.back', R.x1 + 0.1, cz, 0.2, D, -1, 0) // back wall
  wall('room.window', cx, R.z0 - 0.1, W, 0.2, 0, 1) // window wall
  wall('room.side', cx, R.z1 + 0.1, W, 0.2, 0, -1)
  wall('room.door', R.x0 - 0.1, cz, 0.2, D, 1, 0)
  B.plane = 'room.ceiling'
  B.box('ceiling', W, 0.2, D, cx, R.h + 0.1, cz)
  for (let z = R.z0 + 0.8; z < R.z1; z += 1.6) B.box('beam', W, 0.28, 0.14, cx, R.h - 0.14, z)

  // ---- overhead fluorescent fixtures ----
  for (const f of FIXTURES) {
    B.box('housing', 0.22, 0.07, FIXTURE_LEN + 0.1, f.x, FIXTURE_Y + 0.05, f.z)
    B.box('tube', 0.1, 0.03, FIXTURE_LEN, f.x, FIXTURE_Y, f.z)
  }

  // ---- window on the -Z wall, daylight ----
  B.plane = 'room.window'
  const Wn = WINDOW
  B.box('win', Wn.w, Wn.h, 0.02, Wn.x, Wn.y, Wn.z + 0.01)
  for (const mx of [-Wn.w / 4, Wn.w / 4, 0]) B.box('frame', 0.05, Wn.h + 0.08, 0.05, Wn.x + mx, Wn.y, Wn.z + 0.04)
  for (const my of [-Wn.h / 2, 0, Wn.h / 2]) B.box('frame', Wn.w + 0.1, 0.05, 0.05, Wn.x, Wn.y + my, Wn.z + 0.04)
  B.box('frame', Wn.w + 0.24, 0.06, 0.2, Wn.x, Wn.y - Wn.h / 2 - 0.05, Wn.z + 0.1) // sill

  // ---- back wall: pegboard with tools, steel shelving with cloth rolls, LED accent ----
  B.plane = 'room.back'
  const bx = R.x1 - 0.02
  B.box('peg', 0.03, 1.1, 2.6, bx, 1.8, 0.6)
  B.box('darksteel', 0.05, 0.04, 2.7, bx - 0.02, 2.37, 0.6) // pegboard rail
  const hang = (z: number, y: number, kind: number) => {
    const x = bx - 0.05
    if (kind === 0) { B.box('steel', 0.03, 0.22, 0.05, x, y + 0.1, z); B.box('red', 0.05, 0.16, 0.07, x - 0.01, y - 0.08, z) } // hammer
    else if (kind === 1) { B.box('steel', 0.02, 0.3, 0.035, x, y, z); B.cyl('steel', 0.035, 0.02, 'x', x, y + 0.16, z) } // wrench
    else if (kind === 2) { B.box('orange', 0.04, 0.2, 0.07, x, y, z); B.box('steel', 0.02, 0.1, 0.05, x, y - 0.14, z) } // pliers
    else if (kind === 3) { B.box('yellow', 0.04, 0.3, 0.035, x, y, z) } // tape rule / level edge
    else { B.cyl('darksteel', 0.09, 0.05, 'x', x, y, z, 20); B.cyl('steel', 0.03, 0.06, 'x', x, y, z, 12) } // clamp/spool
  }
  for (let i = 0; i < 12; i++) hang(-0.6 + i * 0.22, 1.95 - (i % 3) * 0.1, i % 5)
  for (let i = 0; i < 8; i++) hang(-0.45 + i * 0.3, 1.5 + (i % 2) * 0.05, (i + 2) % 5)
  // shelving
  const sz = -2.95, sw = 1.7, sd = 0.55, sx = R.x1 - sd / 2 - 0.03
  for (const dz of [-sw / 2, sw / 2]) for (const dx of [-sd / 2, sd / 2]) B.box('darksteel', 0.05, 2.2, 0.05, sx + dx, 1.1, sz + dz)
  const shelfY = [0.35, 0.95, 1.55, 2.15]
  for (const y of shelfY) B.box('darksteel', sd, 0.03, sw, sx, y, sz)
  B.box('led', 0.02, 0.02, sw - 0.1, sx - sd / 2 + 0.01, shelfY[3] - 0.03, sz) // teal accent under the top shelf
  B.box('led', 0.02, 0.02, sw - 0.1, sx - sd / 2 + 0.01, shelfY[2] - 0.03, sz)
  for (let i = 0; i < 3; i++) B.cyl('cloth', 0.09, sd - 0.06, 'x', sx, shelfY[1] + 0.1, sz - 0.55 + i * 0.28, 18) // glass cloth rolls
  for (let i = 0; i < 2; i++) B.cyl('carbon', 0.085, sd - 0.06, 'x', sx, shelfY[2] + 0.1, sz - 0.4 + i * 0.3, 18)
  B.cyl('cloth', 0.09, sd - 0.06, 'x', sx, shelfY[2] + 0.1, sz + 0.35, 18)
  for (let i = 0; i < 3; i++) B.box(i === 1 ? 'binb' : 'bin', 0.4, 0.22, 0.42, sx, shelfY[0] + 0.13, sz - 0.5 + i * 0.5)
  for (let i = 0; i < 4; i++) B.box(i % 2 ? 'binb' : 'bin', 0.4, 0.2, 0.3, sx, shelfY[3] + 0.12, sz - 0.6 + i * 0.4)
  B.box('led', 0.02, 0.025, D - 0.4, R.x1 - 0.02, 1.07, cz) // teal accent along the wainscot cap
  B.box('lamp', 0.04, 0.04, 0.5, R.x1 - 0.05, 2.6, 1.9) // a warm work-light strip over the door side

  // ---- fabric roll rack + rolling tool chest (free-standing: never culled) ----
  B.plane = ''
  const rz = 3.1, rx = R.x1 - 0.35
  for (const dz of [-0.6, 0.6]) B.box('darksteel', 0.05, 1.3, 0.05, rx, 0.65, rz + dz)
  for (const y of [0.4, 0.85, 1.25]) B.box('darksteel', 0.05, 0.04, 1.3, rx, y, rz)
  for (let i = 0; i < 4; i++) B.cyl(i % 2 ? 'cloth' : 'carbon', 0.09, 0.28, 'z', rx, 0.5 + (i % 2) * 0.45, rz - 0.4 + i * 0.27, 16)
  const cx2 = 1.7, cz2 = 1.9
  B.box('chest', 0.62, 0.62, 0.9, cx2, 0.62, cz2)
  for (const dy of [0.42, 0.62, 0.82]) B.box('darksteel', 0.01, 0.03, 0.84, cx2 - 0.315, dy, cz2) // drawer pulls
  B.box('darksteel', 0.66, 0.04, 0.94, cx2, 0.95, cz2)
  for (const [dx, dz] of [[-0.26, -0.4], [0.26, -0.4], [-0.26, 0.4], [0.26, 0.4]]) B.cyl('tyre', 0.06, 0.05, 'z', cx2 + dx, 0.06, cz2 + dz, 14)
  B.box('steel', 0.18, 0.1, 0.22, cx2, 1.02, cz2 + 0.2) // vise on top
  B.box('bin', 0.3, 0.12, 0.28, cx2 - 0.05, 1.03, cz2 - 0.2)

  // ---- the build table: plywood top, steel legs and rails ----
  const TL = Math.max(span + 0.8, 2.4), TD = 0.95
  const tabletop = new THREE.Mesh(new THREE.BoxGeometry(TD, 0.05, TL), M.wood)
  tabletop.position.set(0, TABLE_TOP_Y - 0.025, 0)
  tabletop.name = 'shop.tabletop'
  tabletop.castShadow = true
  tabletop.receiveShadow = true
  group.add(tabletop)
  const lx = TD / 2 - 0.06, lz = TL / 2 - 0.08
  for (const dx of [-lx, lx]) for (const dz of [-lz, lz]) {
    B.box('steel', 0.07, TABLE_TOP_Y - 0.05, 0.07, dx, (TABLE_TOP_Y - 0.05) / 2, dz)
    B.box('darksteel', 0.11, 0.02, 0.11, dx, 0.01, dz) // feet
  }
  for (const dz of [-lz, lz]) B.box('steel', TD - 0.1, 0.07, 0.05, 0, TABLE_TOP_Y - 0.09, dz)
  for (const dx of [-lx, lx]) B.box('steel', 0.05, 0.07, TL - 0.16, dx, TABLE_TOP_Y - 0.09, 0)

  // ---- jig: two strongback rails on the table, blocks with a shallow airfoil-underside notch (representational) ----
  const blockH = 0.14, railH = 0.05, railX = chord * 0.42
  for (const dx of [-railX, railX]) B.box('steel', 0.05, railH, TL - 0.2, dx, TABLE_TOP_Y + railH / 2, 0)
  const jigBase = TABLE_TOP_Y + railH
  const jigTopY = jigBase + blockH
  const bw = chord + 0.1, bd = 0.06
  const shape = new THREE.Shape()
  // top edge: flat lips with a shallow curved notch across the chord, the cradle the canard's surface sits in
  const notch = 0.022
  shape.moveTo(-bw / 2, 0); shape.lineTo(bw / 2, 0); shape.lineTo(bw / 2, blockH); shape.lineTo(chord / 2, blockH)
  for (let i = 1; i < 24; i++) { const u = 1 - (2 * i) / 24; shape.lineTo((chord / 2) * u, blockH - notch * (1 - u * u)) }
  shape.lineTo(-chord / 2, blockH); shape.lineTo(-bw / 2, blockH); shape.closePath()
  const jigZ: number[] = []
  for (let i = 0; i < 5; i++) jigZ.push(-span / 2 + span * (0.07 + 0.215 * i))
  for (const z of jigZ) {
    const g = new THREE.ExtrudeGeometry(shape, { depth: bd, bevelEnabled: false })
    B.add('jig', g, 0, jigBase, z - bd / 2)
  }

  const { combined, rest } = B.flush(group, {
    cast: new Set(['steel', 'darksteel', 'jig', 'chest', 'bin', 'binb', 'cloth', 'carbon']),
    receive: new Set(['floor', 'wall', 'wainscot', 'steel', 'darksteel', 'jig', 'peg', 'chest', 'bin', 'binb']),
  }, planeGroups)
  group.traverse((o) => { if ((o as THREE.Mesh).isMesh && o.name === 'shop.jig') { o.userData.representational = true } })
  group.userData.representational = true // jig stations are illustrative: the graph names none for chapter 30
  // the ground beyond the slab: only drawn while some wall is culled (an outside eye sees ground, not the clear colour)
  const apron = new THREE.Mesh(new THREE.BoxGeometry(400, 0.02, 400), M.apron)
  apron.name = 'shop.apron'
  apron.position.set(cx, -0.21, cz)
  group.add(apron)
  const setHidden = (hidden: ReadonlySet<string>) => {
    const outside = hidden.size > 0
    for (const m of combined) m.visible = !outside
    for (const m of rest) m.visible = outside
    apron.visible = outside
    for (const p of planes) planeGroups[p.key].visible = outside && !hidden.has(p.key)
  }
  setHidden(new Set())
  return { group, jigTopY, jigZ, planes, planeGroups, setHidden }
}
