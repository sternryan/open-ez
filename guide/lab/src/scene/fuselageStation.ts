import * as THREE from 'three'
import { matte, surf } from '../core/materials'
import { Batch, glow, pegTexture, ROOM, TABLE_TOP_Y } from './workshop'

/**
 * The fuselage station (plans chapters 4-6), in the room corner the canard's shots never look at (-X, -Z), so the canard subject's
 * frames are unchanged. World metres, +Y up. Two pieces of furniture, both running along X:
 *
 *  - the layup table, against the window wall, where the bulkheads are made flat (chapter 4) and the sides lie inside face up
 *    (chapter 5). REPRESENTATIONAL: the plans give no table size; 120 x 68 in is a size that holds both sides and the bulkheads.
 *  - the jig bench nearer the room, 85 in long (plans-1980:p39), with two levelled jig blocks on it (p39: 2-3 ft long, 2-4 in
 *    thick). The block values below are REPRESENTATIONAL picks inside those ranges, and where the blocks stand along the bench is
 *    not printed. The bench height and depth are representational too.
 *
 * Built like the workshop: one merged mesh per material, static. It is its own group so its meshes are culled out of the canard's
 * views (the workshop's merged room meshes are never culled, so nothing is added to them).
 */
export const INCH = 0.0254
export const STATION = {
  table: { x: -3.9, z: -3.06, topY: TABLE_TOP_Y, len: 120 * INCH, depth: 68 * INCH },
  jig: {
    x: -3.9, z: -1.5,
    benchTopY: 0.78, // representational
    benchLen: 85 * INCH, // plans-1980:p39
    benchDepth: 28 * INCH, // representational
    block: { across: 30 * INCH, high: 3 * INCH, along: 3.5 * INCH }, // representational picks within p39's 2-3 ft and 2-4 in
    blockFs: [37, 110], // representational: where the blocks stand is not printed
  },
  /** the fuselage station at the middle of the jig bench (the box's FS extent is 22 to 125.5) */
  fsMid: 73.75,
}
export const blockTopY = () => STATION.jig.benchTopY + STATION.jig.block.high
/** world X of a fuselage station on the jig bench (FS runs toward +X, the nose toward the -X wall) */
export const fsToX = (fs: number) => STATION.jig.x + (fs - STATION.fsMid) * INCH

export function buildFuselageStation(): THREE.Group {
  const group = new THREE.Group()
  group.name = 'fuselageStation'
  const M: Record<string, THREE.Material> = {
    wood: surf({ color: 0x5a3f2e, metalness: 0, roughness: 0.55, detail: 5, colorVar: 0.14, roughVar: 0.25, name: 'plywood' }),
    top: surf({ color: 0x8a6a4c, metalness: 0, roughness: 0.6, detail: 5, colorVar: 0.1, roughVar: 0.25, name: 'mdf-top' }),
    steel: surf({ color: 0x9aa0a6, metalness: 0.9, roughness: 0.32, detail: 3, roughVar: 0.3 }),
    darksteel: surf({ color: 0x2c2f33, metalness: 0.75, roughness: 0.45, detail: 2 }),
    jig: surf({ color: 0xb48a58, metalness: 0, roughness: 0.62, detail: 9, colorVar: 0.16, roughVar: 0.3, name: 'mdf' }),
    peg: surf({ color: 0xffffff, metalness: 0, roughness: 0.85, map: pegTexture() }),
    foam: matte(0xb9c7d6, 0.9, { detail: 3, colorVar: 0.05 }), // spare foam sheets: a blue-grey PVC foam colour, representational
    foam2: matte(0xe0c88c, 0.92, { detail: 3, colorVar: 0.05 }),
    red: matte(0xb3261e, 0.5), yellow: matte(0xd8b62a, 0.55), orange: matte(0xdb7a1c, 0.5),
    housing: matte(0x2b2c2f, 0.6),
    tube: glow(0xfff0dc, 5.5),
    bucket: matte(0xd9d4c8, 0.55),
  }
  const B = new Batch(M)
  const T = STATION.table, J = STATION.jig

  // ---- layup table: MDF top on a steel frame ----
  B.box('top', T.len, 0.04, T.depth, T.x, T.topY - 0.02, T.z)
  const tlx = T.len / 2 - 0.08, tlz = T.depth / 2 - 0.08
  for (const dx of [-tlx, 0, tlx]) for (const dz of [-tlz, tlz]) {
    B.box('steel', 0.06, T.topY - 0.04, 0.06, T.x + dx, (T.topY - 0.04) / 2, T.z + dz)
    B.box('darksteel', 0.1, 0.02, 0.1, T.x + dx, 0.01, T.z + dz)
  }
  for (const dz of [-tlz, tlz]) B.box('steel', T.len - 0.12, 0.06, 0.04, T.x, T.topY - 0.08, T.z + dz)
  B.box('steel', T.len - 0.12, 0.04, 0.04, T.x, 0.22, T.z) // a stretcher low down

  // ---- jig bench, 85 in, and the two jig blocks across it ----
  B.box('wood', J.benchLen, 0.05, J.benchDepth, J.x, J.benchTopY - 0.025, J.z)
  const blx = J.benchLen / 2 - 0.07, blz = J.benchDepth / 2 - 0.06
  for (const dx of [-blx, blx]) for (const dz of [-blz, blz]) {
    B.box('darksteel', 0.07, J.benchTopY - 0.05, 0.07, J.x + dx, (J.benchTopY - 0.05) / 2, J.z + dz)
    B.box('darksteel', 0.1, 0.02, 0.1, J.x + dx, 0.01, J.z + dz)
  }
  for (const dx of [-blx, blx]) B.box('darksteel', 0.05, 0.05, J.benchDepth - 0.1, J.x + dx, 0.3, J.z)
  B.box('darksteel', J.benchLen - 0.14, 0.05, 0.05, J.x, 0.3, J.z)
  for (const fs of J.blockFs) B.box('jig', J.block.along, J.block.high, J.block.across, fsToX(fs), J.benchTopY + J.block.high / 2, J.z)

  // ---- the wall behind: a pegboard with a few tools, spare foam leaning against it, a mixing bucket ----
  const wz = ROOM.z0 + 0.02
  B.box('peg', 2.6, 1.0, 0.03, T.x, 1.75, wz)
  B.box('darksteel', 2.7, 0.04, 0.05, T.x, 2.27, wz + 0.02)
  for (let i = 0; i < 9; i++) {
    const x = T.x - 1.1 + i * 0.27, y = 1.8 - (i % 3) * 0.12, z = wz + 0.05
    if (i % 3 === 0) { B.box('darksteel', 0.05, 0.28, 0.02, x, y, z); B.box('red', 0.07, 0.1, 0.03, x, y - 0.18, z) } // squeegee / saw
    else if (i % 3 === 1) { B.box('yellow', 0.035, 0.34, 0.03, x, y, z) } // straightedge
    else { B.box('orange', 0.07, 0.18, 0.04, x, y, z); B.box('steel', 0.02, 0.12, 0.03, x, y - 0.14, z) } // shears
  }
  for (let i = 0; i < 3; i++) B.box(i % 2 ? 'foam2' : 'foam', 1.2, 0.6, 0.02, ROOM.x0 + 0.9 + i * 0.03, 0.31, wz + 0.25 + i * 0.03) // on edge, against the wall
  B.cyl('bucket', 0.14, 0.3, 'y', T.x + T.len / 2 + 0.35, 0.15, T.z + 0.2, 20)

  // ---- two fluorescent fixtures over the station (the canard's are over its own table) ----
  for (const z of [T.z + 0.3, J.z]) {
    B.box('housing', 2.2, 0.07, 0.22, T.x, ROOM.h - 0.07, z)
    B.box('tube', 2.1, 0.03, 0.1, T.x, ROOM.h - 0.12, z)
  }

  B.flush(group, {
    cast: new Set(['wood', 'top', 'steel', 'darksteel', 'jig', 'foam', 'foam2', 'bucket']),
    receive: new Set(['wood', 'top', 'steel', 'darksteel', 'jig', 'peg', 'foam', 'foam2']),
  })
  group.traverse((o) => { if ((o as THREE.Mesh).isMesh && o.name === 'shop.jig') o.userData.representational = true })
  group.userData.representational = true // table size, bench height and block values are representational (see above)
  return group
}
