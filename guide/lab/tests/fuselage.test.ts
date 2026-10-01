import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { barOps, type GraphLite, type Op } from '../src/logic/graph'
import {
  fuseBarOps, parseSubject, placement, jigPose, upFace, planHalfWidth, stationLayers, stationSummary, fmtFs, stationAmount,
  STATION_CUT, cgRow, INSTALL, FUSE_CHAPTERS, turnPose, FLIP_SECONDS, hatchSoftness, labelPriority, crossedByStationCut, cutRangeFor, NOSE_COMPONENTS, JIG_ONLY,
  type FusePlyRow, type FusePartRow, type LedgerLite,
} from '../src/logic/fuselage'
import { FUSE_VIEWS, fuseView } from '../src/fuseShots'

const op = (id: string, chapter: number, components: string[] = [], stub = false, variants = ['both']): Op =>
  ({ id, chapter, title: id, summary: '', variants, stub, components })

// a small graph in the real graph's shape: chapter 4's two independent groups, the side ops, the jig ops, and a canard op
const G: GraphLite = {
  ops: [
    op('c03.layup-skills', 3), op('f04.front-seat-bkhd-front', 4, ['fuselage.front_seat_bkhd']), op('f04.panel-f22-f28-aft', 4, ['fuselage.panel', 'fuselage.f22', 'fuselage.f28']),
    op('f04.front-seat-bkhd-back', 4, ['fuselage.front_seat_bkhd']), op('f05.side-blank', 5, ['fuselage.side_left', 'fuselage.side_right']),
    op('f05.stub', 5, [], true), op('f06.trial-fit', 6, ['fuselage.side_left', 'fuselage.front_seat_bkhd', 'fuselage.f22']), op('f06.jig-check', 6, ['fuselage.side_left']), op('f06.bond-front-seat', 6, ['fuselage.front_seat_bkhd']),
    op('f06.bond-panel', 6, ['fuselage.panel']), op('f06.bond-f22', 6, ['fuselage.f22']), op('f06.bottom-foam-fit', 6, ['fuselage.bottom']),
    op('f06.bottom-glass', 6, ['fuselage.bottom']), op('f06.bottom-bond', 6, ['fuselage.bottom']), op('r30.a', 30, [], false, ['roncz']),
  ],
  order: ['c03.layup-skills', 'f04.front-seat-bkhd-front', 'f04.panel-f22-f28-aft', 'f04.front-seat-bkhd-back', 'f05.side-blank', 'f05.stub', 'f06.trial-fit', 'f06.jig-check',
    'f06.bond-front-seat', 'f06.bond-panel', 'f06.bond-f22', 'f06.bottom-foam-fit', 'f06.bottom-glass', 'f06.bottom-bond', 'r30.a'],
}
const ORDER = G.order

test('the fuselage bar is the chapter 4-9, 12 and 13 ops that are not stubs, in graph order, whatever the variant', () => {
  const want = ['f04.front-seat-bkhd-front', 'f04.panel-f22-f28-aft', 'f04.front-seat-bkhd-back', 'f05.side-blank', 'f06.trial-fit', 'f06.jig-check', 'f06.bond-front-seat',
    'f06.bond-panel', 'f06.bond-f22', 'f06.bottom-foam-fit', 'f06.bottom-glass', 'f06.bottom-bond']
  assert.deepEqual(fuseBarOps(G, 'roncz').map((o) => o.id), want)
  assert.deepEqual(fuseBarOps(G, 'gu').map((o) => o.id), want)
  assert.deepEqual([...FUSE_CHAPTERS].sort((a, b) => a - b), [4, 5, 6, 7, 8, 9, 12, 13])
  assert.deepEqual(barOps(G, 'roncz').map((o) => o.id), ['r30.a']) // the canard bar is untouched
})

test('parseSubject keeps the canard as the default', () => {
  assert.equal(parseSubject(null), 'canard')
  assert.equal(parseSubject('nonsense'), 'canard')
  assert.equal(parseSubject('fuselage'), 'fuselage')
})

test('a part goes into the jig at its install op, in the book order, and stays on the table before it', () => {
  const dry = G.ops.find((o) => o.id === 'f06.trial-fit')!.components
  const at = (c: string, o: string | null) => placement(c, o, ORDER, dry)
  assert.equal(at('fuselage.side_left', 'f05.side-blank'), 'table')
  assert.equal(at('fuselage.side_left', 'f06.trial-fit'), 'jig')
  assert.equal(at('fuselage.front_seat_bkhd', 'f06.trial-fit'), 'jig') // dry-fitted with the sides for the trial fit ...
  assert.equal(at('fuselage.front_seat_bkhd', 'f06.jig-check'), 'table') // ... then back out: each is bonded in its own op
  assert.equal(at('fuselage.panel', 'f06.trial-fit'), 'table') // the panel is not in the dry fit
  // after the panel is bonded, the front seat bulkhead and the panel are in, F22 is not
  assert.equal(at('fuselage.front_seat_bkhd', 'f06.bond-panel'), 'jig')
  assert.equal(at('fuselage.panel', 'f06.bond-panel'), 'jig')
  assert.equal(at('fuselage.f22', 'f06.bond-panel'), 'table')
  assert.equal(at('fuselage.f22', 'f06.bond-f22'), 'jig')
  // the bottom sits on the box to be fitted, comes off for its inside glass, and goes back on for the bond
  assert.equal(at('fuselage.bottom', 'f06.bottom-foam-fit'), 'jig')
  assert.equal(at('fuselage.bottom', 'f06.bottom-glass'), 'table')
  assert.equal(at('fuselage.bottom', 'f06.bottom-bond'), 'jig')
  assert.equal(at('fuselage.f22', null), 'jig') // nothing selected: the finished box
})

test('the install table names the book bonding order: front seat, panel, F22, rear seat, firewall, then F28', () => {
  const ch6 = readFileSync(fileURLToPath(new URL('../../graph/ch06.yaml', import.meta.url)), 'utf8')
  const ids = [...ch6.matchAll(/^- id: (\S+)/gm)].map((m) => m[1])
  const bonds = ['fuselage.front_seat_bkhd', 'fuselage.panel', 'fuselage.f22', 'fuselage.rear_seat_bkhd', 'fuselage.firewall', 'fuselage.f28'].map((c) => INSTALL[c])
  for (const b of bonds) assert.ok(ids.includes(b), b)
  const pos = bonds.map((b) => ids.indexOf(b))
  assert.deepEqual([...pos].sort((a, b) => a - b), pos)
})

test('the box is upside down in the jig until the bottom is bonded, then right side up', () => {
  assert.equal(jigPose('f06.trial-fit', ORDER), 'inverted')
  assert.equal(jigPose('f06.bottom-glass', ORDER), 'inverted')
  assert.equal(jigPose('f06.bottom-bond', ORDER), 'upright')
  assert.equal(jigPose(null, ORDER), 'upright')
})

const N: Record<string, FusePlyRow> = {
  'fuselage.front_seat_bkhd.p1': { part: 'front_seat_bkhd', component: 'fuselage.front_seat_bkhd', op: 'f04.front-seat-bkhd-front', op_index: 0, op_order: 1, order: 1, stack: 1, cloth: 'UND', orientation_deg: 45, where: 'x', region: 'face:fwd', fidelity: 'book', lower_bound: true, area_in2: 1, fs_min: 63, fs_max: 82 },
  'fuselage.front_seat_bkhd.p2': { part: 'front_seat_bkhd', component: 'fuselage.front_seat_bkhd', op: 'f04.front-seat-bkhd-front', op_index: 0, op_order: 2, order: 2, stack: 2, cloth: 'UND', orientation_deg: -45, where: 'x', region: 'face:fwd', fidelity: 'book', lower_bound: true, area_in2: 1, fs_min: 62.9, fs_max: 82 },
  'fuselage.front_seat_bkhd.p3': { part: 'front_seat_bkhd', component: 'fuselage.front_seat_bkhd', op: 'f04.front-seat-bkhd-back', op_index: 2, op_order: 1, order: 3, stack: 1, cloth: 'BID', orientation_deg: 45, where: 'y', region: 'face:aft', fidelity: 'book', lower_bound: true, area_in2: 1, fs_min: 63.5, fs_max: 82.5 },
  'fuselage.panel.p1': { part: 'panel', component: 'fuselage.panel', op: 'f04.panel-f22-f28-aft', op_index: 1, op_order: 1, order: 1, stack: 1, cloth: 'BID', orientation_deg: null, where: 'z', region: 'face:aft', fidelity: 'representational', lower_bound: false, area_in2: 1, fs_min: 39.95, fs_max: 39.99 },
}

test('the face that is up on the table is the one being glassed, then the last one glassed', () => {
  assert.equal(upFace('front_seat_bkhd', 'f04.front-seat-bkhd-front', ORDER, N), 'fwd')
  assert.equal(upFace('front_seat_bkhd', 'f04.front-seat-bkhd-back', ORDER, N), 'aft')
  assert.equal(upFace('front_seat_bkhd', 'f05.side-blank', ORDER, N), 'aft')
  assert.equal(upFace('panel', 'f04.panel-f22-f28-aft', ORDER, N), 'aft')
  assert.equal(upFace('f22', 'f04.front-seat-bkhd-front', ORDER, N), 'fwd') // not glassed yet
})

test('planHalfWidth interpolates the plan bend and holds its ends', () => {
  const bend: [number, number][] = [[22, 11.5], [81.75, 11.5], [107, 10.3], [118.5, 9.35]]
  assert.equal(planHalfWidth(bend, 50), 11.5)
  assert.ok(Math.abs(planHalfWidth(bend, (81.75 + 107) / 2) - (11.5 + 10.3) / 2) < 1e-12)
  assert.equal(planHalfWidth(bend, 10), 11.5)
  assert.equal(planHalfWidth(bend, 200), 9.35)
})

test('the station cut: the plane constant is -FS, so the aft side (x >= FS) is kept', () => {
  for (const fs of [22, 63.5, 70, 125.25]) {
    const a = stationAmount(fs)
    const e = STATION_CUT.depth + (STATION_CUT.extent - STATION_CUT.depth) * (1 - a) // CutState.update's formula
    assert.ok(Math.abs(e + fs) < 1e-9, `${fs}: ${e}`)
    assert.ok(a > 0.0005 && a < 1) // caps on, never past the plane's range
  }
  assert.equal(fmtFs(70), 'FS 70')
  assert.equal(fmtFs(63.54), 'FS 63.5')
})

test('stationLayers lists the plies whose extent spans the station, in lay order, and only the live ones', () => {
  assert.deepEqual(stationLayers(N, 70).map((l) => l.node), ['fuselage.front_seat_bkhd.p1', 'fuselage.front_seat_bkhd.p2', 'fuselage.front_seat_bkhd.p3'])
  assert.deepEqual(stationLayers(N, 62.95).map((l) => l.node), ['fuselage.front_seat_bkhd.p2'])
  assert.deepEqual(stationLayers(N, 39.97).map((l) => l.node), ['fuselage.panel.p1'])
  assert.deepEqual(stationLayers(N, 70, new Set(['fuselage.front_seat_bkhd.p1'])).map((l) => l.node), ['fuselage.front_seat_bkhd.p1'])
})

const P: Record<string, FusePartRow> = {
  side_left: { node: 'fuselage.side_left', component: 'fuselage.side_left', fidelity: 'book', label: 'Left side', cite: [], fs_min: 22, fs_max: 125 },
  front_seat_bkhd: { node: 'fuselage.front_seat_bkhd', component: 'fuselage.front_seat_bkhd', fidelity: 'book', label: 'Front seat bulkhead', cite: [], fs_min: 63, fs_max: 82.3 },
  panel: { node: 'fuselage.panel', component: 'fuselage.panel', fidelity: 'representational', label: 'Instrument panel (fitted shape)', cite: [], fs_min: 39.75, fs_max: 39.95 },
}

test('stationSummary names each part cut there with its ply count per cloth, in part order', () => {
  const s = stationSummary(P, ['front_seat_bkhd', 'side_left'], stationLayers(N, 70))
  assert.equal(s, 'Left side · Front seat bulkhead: 2 UND, 1 BID')
  assert.equal(stationSummary(P, [], []), 'Nothing in the jig is cut here')
})

test('the CG row never shows the lower bound as the CG', () => {
  assert.deepEqual(cgRow(null), { value: 'not yet computed', sub: 'no mass ledger in this build' })
  const L: LedgerLite = {
    cg: { weight_lb: 0, arm_in: null, included: [], excluded: { firewall: 'not yet computed: density of birch ply not sourced', f22: 'not yet computed: glass rows not fully placed (1 excluded row(s))' } },
    cg_lower_bound: { weight_lb: 24.46, arm_in: 63.21, included: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'], excluded: {} },
  }
  const r = cgRow(L)
  assert.equal(r.value, 'not yet computed')
  assert.ok(r.sub!.includes('2 of 2 parts') && r.sub!.includes('density of birch ply not sourced'), r.sub!)
  assert.ok(r.sub!.includes('≥ 24.5 lb at FS 63.2, lower bound, 8 parts'), r.sub!)
  const none = cgRow({ ...L, cg_lower_bound: { weight_lb: 0, arm_in: null, included: [], excluded: {} } })
  assert.ok(!none.sub!.includes('lower bound'))
  const done = cgRow({ ...L, cg: { weight_lb: 30, arm_in: 70.04, included: ['x', 'y'], excluded: {} } })
  assert.equal(done.value, '30.0 lb at FS 70.0')
})

test('every chapter 4-9 op in the graph has an authored lab shot, and no shot is stale', () => {
  const ids: string[] = []
  for (const ch of ['ch04', 'ch05', 'ch06', 'ch07', 'ch08', 'ch09']) {
    const y = readFileSync(fileURLToPath(new URL(`../../graph/${ch}.yaml`, import.meta.url)), 'utf8')
    ids.push(...[...y.matchAll(/^- id: (\S+)/gm)].map((m) => m[1]))
  }
  assert.ok(ids.length >= 52)
  assert.deepEqual(Object.keys(FUSE_VIEWS).sort(), [...ids].sort())
  for (const id of ids) {
    const v = fuseView(id)
    // chapters 7-9 look low along the box for the lower corner, the step, the jig blocks and the legs; never from under the floor
    const elMin = /^f0[456]\./.test(id) ? 20 : 5
    assert.ok(v.dist > 20 && v.dist < 200 && v.el >= elMin && v.el <= 75, id)
  }
})

test('the station cut hides the label of a part wholly forward of the plane and keeps one it passes through', async () => {
  const { removedByStationCut } = await import('../src/logic/fuselage')
  const rows: Record<string, { fs_min: number; fs_max: number }> = {
    f22: { fs_min: 22, fs_max: 22.2 }, f28: { fs_min: 27.65, fs_max: 27.85 }, panel: { fs_min: 39.75, fs_max: 39.95 },
    front_seat_bkhd: { fs_min: 63.0151, fs_max: 82.2849 }, side_left: { fs_min: 22, fs_max: 125 }, top_longeron_left: { fs_min: 22, fs_max: 125.5 },
  }
  const hidden = Object.keys(rows).filter((k) => removedByStationCut(rows[k], 72))
  assert.deepEqual(hidden, ['f22', 'f28', 'panel'])
  assert.deepEqual(Object.keys(rows).filter((k) => removedByStationCut(rows[k], 22)), [], 'with the plane at the nose nothing is wholly forward')
})

test('the CG detail names parts by their labels and folds a left and right pair into one reason', () => {
  const L: LedgerLite = {
    cg: {
      weight_lb: 0, arm_in: null, included: [], excluded: {
        top_longeron_left: 'not yet computed: core material of Left top longeron not sourced',
        top_longeron_right: 'not yet computed: core material of Right top longeron not sourced',
        firewall: 'not yet computed: density of birch plywood not sourced',
      },
    },
    cg_lower_bound: { weight_lb: 0, arm_in: null, included: [], excluded: {} },
  }
  const sub = cgRow(L).sub!
  assert.ok(sub.includes('core material of top longeron not sourced (2)'), sub)
  assert.ok(!/_/.test(sub), sub)
})

test('the box turns right side up about its long axis: from inverted to upright, eased, lifted clear of the blocks', () => {
  const half = { h: 11.5, w: 12 }
  assert.ok(FLIP_SECONDS >= 0.8 && FLIP_SECONDS <= 1.3)
  const a = turnPose('inverted', 'upright', 0, half), z = turnPose('inverted', 'upright', 1, half)
  assert.equal(a.angle, Math.PI)
  assert.equal(z.angle, 0)
  assert.equal(a.lift, half.h) // at rest the axis is half the box's height above the block tops
  assert.equal(z.lift, half.h)
  // eased: slow at both ends
  const early = turnPose('inverted', 'upright', 0.1, half).angle
  assert.ok(Math.PI - early < 0.1 * Math.PI, 'eases out of rest')
  // every corner of the section stays above the block tops the whole way round
  for (let k = 0; k <= 1.0001; k += 0.02) {
    const p = turnPose('inverted', 'upright', k, half)
    for (const [y, zz] of [[half.h, half.w], [half.h, -half.w], [-half.h, half.w], [-half.h, -half.w]]) {
      const yy = y * Math.cos(p.angle) - zz * Math.sin(p.angle)
      assert.ok(p.lift + yy >= -1e-9, `corner below the blocks at k=${k}`)
    }
  }
  const mid = turnPose('inverted', 'upright', 0.5, half)
  assert.ok(mid.angle > 0.2 && mid.angle < Math.PI - 0.2 && mid.lift > half.h, 'mid-turn is between the ends and lifted')
  // stepping back turns it the other way, through the same path
  const back = turnPose('upright', 'inverted', 0.5, half)
  assert.ok(Math.abs(back.angle - mid.angle) < 1e-9 && Math.abs(back.lift - mid.lift) < 1e-9)
  assert.equal(turnPose('upright', 'inverted', 1, half).angle, Math.PI)
  // the same k gives the same pose (the film is reproducible)
  assert.deepEqual(turnPose('inverted', 'upright', 0.37, half), turnPose('inverted', 'upright', 0.37, half))
})

test('stripes soften on large faces and stay full on small parts', () => {
  assert.equal(hatchSoftness(20), 0)
  assert.equal(hatchSoftness(92), 0) // F28
  assert.equal(hatchSoftness(300), 0) // the firewall: a bulkhead keeps the full stripes
  assert.ok(hatchSoftness(471) < 0.35) // the panel and F22 barely change
  assert.ok(hatchSoftness(500) > 0 && hatchSoftness(500) < 1)
  assert.equal(hatchSoftness(2300), 1) // the 24 x 96 bottom
  assert.ok(hatchSoftness(800) > hatchSoftness(400))
})

test('label priority: the selected op parts, then the parts the station cut passes through, then fitted shapes', () => {
  const p = (inOp: boolean, cut: boolean, fitted: boolean) => labelPriority({ inOp, cut, fitted })
  assert.ok(p(true, false, false) > p(false, true, true))
  assert.ok(p(false, true, false) > p(false, false, true))
  assert.ok(p(false, false, true) > p(false, false, false))
  assert.equal(crossedByStationCut({ fs_min: 63.0151, fs_max: 82.2849 }, 72), true)
  assert.equal(crossedByStationCut({ fs_min: 22, fs_max: 22.2 }, 72), false)
  assert.equal(crossedByStationCut({ fs_min: 85, fs_max: 118 }, 72), false)
})

// ======================================================================================================================
// Block 2 M2.3 Task 5: chapters 7-9 (the 45 degree rolls, the gear table, the stages, the gear CG rows and the ground note)
// ======================================================================================================================
const ORDER9 = ['f06.bottom-glass', 'f06.bottom-bond', 'f06.bottom-tape', 'f07.carve-corners', 'f07.canard-cutout', 'f07.fuel-gauge-area', 'f07.belt-insert',
  'f07.skin-right', 'f07.skin-left', 'f08.roll-over-foam', 'f08.access-holes', 'f08.step', 'f09.strut-stiffen', 'f09.jig-blocks', 'f09.position-gear',
  'f09.tab-layup', 'f09.axles-brakes', 'f09.brake-lines']

/** Rx(angle) applied to a direction in the lab's box frame (x = FS, y = W.L. up, z = -B.L.): three.js's makeRotationX */
const rotX = (a: number, [x, y, z]: number[]) => [x, y * Math.cos(a) - z * Math.sin(a), y * Math.sin(a) + z * Math.cos(a)]

test('the right skin is glassed with the right side up: its outward normal points up at 45 degrees of left bank (Review Focus 5)', async () => {
  const { poseAngle, BANK_DEG } = await import('../src/logic/fuselage')
  // as core.landing_gear_book.bank_pose's own test: positive is a left bank, the right side (B.L. > 0, the lab's z < 0) goes up
  assert.equal(BANK_DEG['f07.skin-right'], 135)
  assert.equal(BANK_DEG['f07.skin-left'], -135)
  const rightOut = [0, 0, -1], leftOut = [0, 0, 1]
  const atRight = poseAngle(jigPose('f07.skin-right', ORDER9))
  assert.ok(rotX(atRight, rightOut)[1] > 0.7, 'right side faces up at the right skin')
  assert.ok(rotX(atRight, leftOut)[1] < -0.7, 'the left side faces down')
  const atLeft = poseAngle(jigPose('f07.skin-left', ORDER9))
  assert.ok(rotX(atLeft, leftOut)[1] > 0.7, 'left side faces up at the left skin')
  assert.ok(Math.abs(atRight - (3 * Math.PI) / 4) < 1e-12 && Math.abs(atLeft + (3 * Math.PI) / 4) < 1e-12)
  // the exported sign convention drives the same answer (layup.json "bank_deg")
  assert.equal(jigPose('f07.skin-right', ORDER9, { 'f07.skin-right': 135, 'f07.skin-left': -135 }), 'bank-left-45')
})

test('at each skin both faces being glassed (the side and the bottom) face up 45 degrees or more (captain\'s 135 degree reading of p46)', async () => {
  const { poseAngle } = await import('../src/logic/fuselage')
  const down = [0, -1, 0], rightOut = [0, 0, -1], leftOut = [0, 0, 1] // box frame: y up, z = -B.L.
  const atRight = poseAngle(jigPose('f07.skin-right', ORDER9)), atLeft = poseAngle(jigPose('f07.skin-left', ORDER9))
  assert.ok(rotX(atRight, rightOut)[1] >= 0.7, 'right side up at the right skin')
  assert.ok(rotX(atRight, down)[1] >= 0.7, 'bottom up at the right skin')
  assert.ok(rotX(atLeft, leftOut)[1] >= 0.7, 'left side up at the left skin')
  assert.ok(rotX(atLeft, down)[1] >= 0.7, 'bottom up at the left skin')
})

test('the roll from the right skin to the left skin goes the short way, over the top, and clears the support throughout', () => {
  const half = { h: 10.3, w: 12.3 }
  let prev = turnPose('bank-left-45', 'bank-right-45', 0, half).angle
  assert.ok(Math.abs(prev - (3 * Math.PI) / 4) < 1e-12)
  for (let k = 0.02; k <= 1.0001; k += 0.02) {
    const p = turnPose('bank-left-45', 'bank-right-45', k, half)
    if (k < 0.999) assert.ok(p.angle >= prev - 1e-12 && p.angle - prev < 0.2, 'one direction, no jump') // the last frame snaps to -135, the same pose as 225
    prev = p.angle
    for (const [y, z] of [[half.h, half.w], [half.h, -half.w], [-half.h, half.w], [-half.h, -half.w]]) assert.ok(p.lift + y * Math.cos(p.angle) - z * Math.sin(p.angle) >= -1e-9, `k=${k}`)
  }
  assert.ok(Math.abs(prev + (3 * Math.PI) / 4) < 1e-9, 'ends at -135 (equivalently 225)')
  assert.ok(Math.abs(turnPose('bank-left-45', 'bank-right-45', 0.99, half).angle - (5 * Math.PI) / 4) < 0.1, 'it went over the top (through 180), not back through upright')
  // from upright to the right skin and on to the floor of chapter 9 also clears
  for (const [a, b] of [['upright', 'bank-left-45'], ['bank-right-45', 'gear-table'], ['bank-left-45', 'upright']] as const)
    for (let k = 0; k <= 1.0001; k += 0.02) {
      const p = turnPose(a, b, k, half)
      for (const [y, z] of [[half.h, half.w], [half.h, -half.w], [-half.h, half.w], [-half.h, -half.w]]) assert.ok(p.lift + y * Math.cos(p.angle) - z * Math.sin(p.angle) >= -1e-9, `${a}->${b} k=${k}`)
    }
})

test('the chapter 7-9 poses: upright to the right skin, the two rolls in order, upright for chapter 8, inverted from the gear positioning to the end, then on its gear', () => {
  const pose = (id: string | null) => jigPose(id, ORDER9)
  assert.equal(pose('f06.bottom-tape'), 'upright')
  assert.equal(pose('f07.carve-corners'), 'upright')
  assert.equal(pose('f07.belt-insert'), 'upright')
  assert.equal(pose('f07.skin-right'), 'bank-left-45')
  assert.equal(pose('f07.skin-left'), 'bank-right-45')
  assert.ok(ORDER9.indexOf('f07.skin-right') < ORDER9.indexOf('f07.skin-left'))
  assert.equal(pose('f08.roll-over-foam'), 'upright')
  assert.equal(pose('f09.strut-stiffen'), 'upright')
  assert.equal(pose('f09.jig-blocks'), 'upright')
  for (const id of ['f09.position-gear', 'f09.tab-layup', 'f09.axles-brakes', 'f09.brake-lines']) assert.equal(pose(id), 'gear-table', id)
  // after the chapter the book sets it on its own feet: the finished box stands right side up on its gear, on the floor
  assert.equal(pose(null), 'on-gear')
  assert.equal(jigPose('f10.after', [...ORDER9, 'f10.after']), 'on-gear') // anything after the last gear op, too
  // a build with no gear op finishes upright on the jig blocks, as chapter 6 left it
  assert.equal(jigPose(null, ORDER9.slice(0, ORDER9.indexOf('f09.position-gear'))), 'upright')
})

test('the box goes to and from the floor without the turn: it is carried off the bench, not rolled', async () => {
  const { animatedTurn } = await import('../src/logic/fuselage')
  assert.equal(animatedTurn('gear-table', 'on-gear'), false)
  assert.equal(animatedTurn('on-gear', 'upright'), false)
  assert.equal(animatedTurn('inverted', 'upright'), true)
  assert.equal(animatedTurn('upright', 'gear-table'), true)
})

test('the banked poses dim the key and tone the dry cloth; every other pose keeps the canard\'s light and the cloth as it was', async () => {
  const { keyScale, dryTone, KEY_BANK, DRY_TONE_BANK } = await import('../src/logic/fuselage')
  for (const p of ['bank-left-45', 'bank-right-45'] as const) { assert.equal(keyScale(p), KEY_BANK); assert.equal(dryTone(p), DRY_TONE_BANK) }
  for (const p of ['upright', 'inverted', 'gear-table', 'on-gear'] as const) { assert.equal(keyScale(p), 1); assert.equal(dryTone(p), 1) }
  assert.ok(KEY_BANK > 0 && KEY_BANK < 1 && DRY_TONE_BANK > 0.5 && DRY_TONE_BANK < 1)
})

test('the wheels are fitted: their diameter is a named fitted number, the section and rim are the size name\'s 3.40 x 5', async () => {
  const { FITTED_TYRE_OD, TYRE_SECTION, RIM_DIA } = await import('../src/logic/fuselage')
  assert.equal(TYRE_SECTION, 3.4)
  assert.equal(RIM_DIA, 5)
  assert.ok(FITTED_TYRE_OD > RIM_DIA + TYRE_SECTION && FITTED_TYRE_OD < 16)
})

test('the home view labels one part per family: at most ten of the finished box\'s parts, every family still named', async () => {
  const { homeLabel, LABEL_FAMILY } = await import('../src/logic/fuselage')
  // the finished box's parts (layup.json "parts" with no end to their show window) and the drawn wheels
  const parts = ['side_left', 'side_right', 'front_seat_bkhd', 'rear_seat_bkhd', 'top_longeron_left', 'top_longeron_right', 'f22', 'f28', 'panel', 'firewall',
    'bottom', 'carved_corners', 'belt_insert', 'rollover', 'rollover_inserts', 'belt_attach', 'step', 'strut', 'extrusions', 'gear_tubes', 'axles', 'wheels']
  const all = new Set(parts)
  const shown = parts.filter((p) => homeLabel(p, (q) => all.has(q)))
  assert.ok(shown.length <= 10, shown.join())
  assert.deepEqual(shown.filter((p) => ['rollover', 'rollover_inserts'].includes(p)), ['rollover']) // one roll-over label, not its inserts too
  assert.deepEqual(shown.filter((p) => ['strut', 'extrusions', 'gear_tubes', 'axles', 'wheels'].includes(p)), ['wheels']) // one gear label
  // every part's label goes to a part that is shown (a family is never left unnamed)
  for (const p of parts) {
    let q = p
    while (!shown.includes(q)) { q = LABEL_FAMILY[q]; assert.ok(q, p) }
  }
  // with no wheels drawn the strut speaks for the gear; with an op selected the rule is not used (main.ts)
  const noWheels = new Set(parts.filter((p) => p !== 'wheels'))
  assert.ok(homeLabel('strut', (q) => noWheels.has(q)) && !homeLabel('axles', (q) => noWheels.has(q)))
})

test('a roll rests on the lower corner and the gear table pose rests on the longerons above the roll-over', async () => {
  const { poseAngle, poseBase, restLift, GEAR_TABLE_RISE } = await import('../src/logic/fuselage')
  const half = { h: 10.3, w: 12.3 }
  for (const p of ['bank-left-45', 'bank-right-45'] as const) {
    const r = turnPose('upright', p, 1, half)
    // the section's lowest corner sits on the block tops
    const low = Math.min(...[[half.h, half.w], [half.h, -half.w], [-half.h, half.w], [-half.h, -half.w]].map(([y, z]) => y * Math.cos(r.angle) - z * Math.sin(r.angle)))
    assert.ok(Math.abs(r.lift + low) < 1e-9, p)
    assert.equal(r.lift, restLift(poseAngle(p), half))
  }
  const g = turnPose('bank-right-45', 'gear-table', 1, half)
  assert.equal(g.angle, Math.PI)
  assert.equal(g.lift, GEAR_TABLE_RISE + half.h)
  assert.ok(GEAR_TABLE_RISE > 12.6 - 3, 'the roll-over (12.6 in above the longerons) hangs clear of the bench (3 in below the block tops)')
  assert.equal(poseBase('upright'), 0)
  // mid-turn the box clears the lower of its two supports
  for (let k = 0; k <= 1.0001; k += 0.02) {
    const p = turnPose('upright', 'gear-table', k, half)
    for (const [y, zz] of [[half.h, half.w], [half.h, -half.w], [-half.h, half.w], [-half.h, -half.w]]) assert.ok(p.lift + y * Math.cos(p.angle) - zz * Math.sin(p.angle) >= -1e-9, `k=${k}`)
  }
})

test('a part\'s show window and a node\'s stages follow the op', async () => {
  const { shownAt, stageAt } = await import('../src/logic/fuselage')
  assert.equal(shownAt(undefined, 'f07.carve-corners', ORDER9), true)
  const only = { only: 'f07.canard-cutout' }
  assert.equal(shownAt(only, 'f07.canard-cutout', ORDER9), true)
  assert.equal(shownAt(only, 'f07.fuel-gauge-area', ORDER9), false)
  assert.equal(shownAt(only, null, ORDER9), false) // the removed material is not part of the finished box
  const tool = { until: 'f09.tab-layup' }
  assert.equal(shownAt(tool, 'f09.position-gear', ORDER9), true)
  assert.equal(shownAt(tool, 'f09.tab-layup', ORDER9), false)
  assert.equal(shownAt(tool, null, ORDER9), false) // a tool is gone from the finished box
  const from = { from: 'f07.carve-corners' }
  assert.equal(shownAt(from, 'f06.bottom-tape', ORDER9), false)
  assert.equal(shownAt(from, 'f07.carve-corners', ORDER9), true)
  assert.equal(shownAt(from, null, ORDER9), true)
  const st = [{ from: 'f07.carve-corners', node: 'fuselage.side_left~carved' }, { from: 'f07.canard-cutout', node: 'fuselage.side_left~cut' }]
  assert.equal(stageAt(st, 'f06.bottom-tape', ORDER9), null)
  assert.equal(stageAt(st, 'f07.carve-corners', ORDER9), 'fuselage.side_left~carved')
  assert.equal(stageAt(st, 'f08.step', ORDER9), 'fuselage.side_left~cut')
  assert.equal(stageAt(st, null, ORDER9), 'fuselage.side_left~cut')
  assert.equal(stageAt(undefined, 'f08.step', ORDER9), null)
})

const GEAR: LedgerLite['gear'] = {
  rows: [
    { name: 'main_strut', label: 'Main gear strut', weight_lb: 22, arm_in: 110.5, status: 'book', arm_status: 'approximate', cite: ['plans-1980:p50'] },
    { name: 'nose_strut', label: 'Nose gear strut', weight_lb: 2.8, arm_in: 17, status: 'book', arm_status: 'conflict', cite: ['plans-1980:p8'] },
    { name: 'wheels_brakes_tyres_axles', label: 'Wheels and brakes (unsourced)', weight_lb: 20.2, arm_in: 110.5, status: 'unsourced', arm_status: 'unsourced', cite: [] },
  ],
  sourced_lb: 24.8,
  ground_handling: {
    main_axle_fs: 110.5, main_axle_wl: -22, tip_back_line_deg: 12, cite: {},
    tip_back_check: 'not yet computed: no source for the CG height', tip_over_check: 'not yet computed: the track has no source',
  },
}
const LG: LedgerLite = {
  cg: { weight_lb: 0, arm_in: null, included: [], excluded: { firewall: 'not yet computed: density of birch plywood not sourced', wheels_brakes_tyres_axles: 'x' } },
  cg_lower_bound: { weight_lb: 58.03, arm_in: 79.82, included: ['side_left', 'side_right', 'bottom', 'main_strut', 'nose_strut'], excluded: { wheels_brakes_tyres_axles: 'not yet computed: weight and arm of wheels and brakes (unsourced) not sourced' } },
  gear: GEAR,
}

test('the CG row: the lower bound says it carries 24.8 lb of gear (the two struts), and the unsourced wheels row is excluded without its placeholder', () => {
  const r = cgRow(LG)
  assert.equal(r.value, 'not yet computed')
  const segs = r.sub!.split(' · ')
  const last = segs[segs.length - 1]
  assert.ok(last.startsWith('≥ 58.0 lb at FS 79.8, lower bound, 3 parts and 24.8 lb of gear (main and nose struts)'), last)
  assert.ok(!last.includes('not yet computed'))
  assert.ok(segs.includes('Wheels and brakes: excluded, no source'), r.sub!)
  assert.ok(!r.sub!.includes('20.2'), 'the unsourced placeholder weight is never shown')
  assert.ok(!r.sub!.includes('45'), 'the retired lump is never shown')
})

test('the ground note: the book axle station and tip-back line, and both checks "not yet computed" with no number (Review Focus 4)', async () => {
  const { groundRow } = await import('../src/logic/fuselage')
  assert.equal(groundRow(null), null)
  assert.equal(groundRow({ ...LG, gear: { ...GEAR, ground_handling: undefined } }), null)
  const g = groundRow(LG)!
  assert.equal(g.value, 'Main axle F.S. 110.5 (book)')
  assert.ok(g.sub.includes('12° tip-back line from the main tyre contact (p171)'), g.sub)
  const check = (name: string) => g.sub.split(' · ').find((x) => x.startsWith(name))!
  assert.equal(check('tip-back check:'), 'tip-back check: not yet computed (no source for the CG height)')
  assert.equal(check('tip-over check:'), 'tip-over check: not yet computed (the track has no source)')
  for (const c of [check('tip-back check:'), check('tip-over check:')]) assert.ok(!/\d/.test(c), c)
  // a verdict, a number or anything that is not "not yet computed" is never shown until the code that grades it is written on purpose
  for (const bad of ['OK: 14.2 deg', 'not yet computed: CG height 30 in', 'passes', 'fails by 2 deg']) {
    const b = groundRow({ ...LG, gear: { ...GEAR, ground_handling: { ...GEAR!.ground_handling!, tip_back_check: bad, tip_over_check: bad } } })!
    assert.ok(b.sub.includes('tip-back check: not yet computed') && b.sub.includes('tip-over check: not yet computed'), b.sub)
    assert.ok(!/check: [^·]*\d/.test(b.sub), b.sub)
  }
  assert.ok(!/track\D{0,12}\d/i.test(g.sub + g.value), 'no track number')
})

// ---- M2.4 Task 5: chapters 12 and 13 in the fuselage subject, the nose arm and the nose wheel W.L. in the readout ----
test('the fuselage bar takes the chapter 12 and 13 ops, in graph order, after the chapter 9 ones', () => {
  const G2: GraphLite = {
    ops: [...G.ops, op('f09.brake-lines', 9), op('r30.elev-a', 11, [], false, ['roncz']), op('r30.f22-drill-tabs', 12, [], false, ['roncz']), op('f13.nose', 13), op('f13.stub', 13, [], true), op('c12.pins', 12, [], false, ['gu'])],
    order: [...G.order, 'f09.brake-lines', 'r30.elev-a', 'r30.f22-drill-tabs', 'f13.nose', 'f13.stub', 'c12.pins'],
  }
  assert.deepEqual(fuseBarOps(G2, 'roncz').slice(-3).map((o) => o.id), ['f09.brake-lines', 'r30.f22-drill-tabs', 'f13.nose'])
  assert.ok(fuseBarOps(G2, 'gu').some((o) => o.id === 'c12.pins')) // the GU variant's chapter 12 is the fuselage subject's too
  assert.deepEqual(barOps(G2, 'roncz').map((o) => o.id), ['r30.a', 'r30.elev-a']) // the elevators stay on the canard's bar; chapter 12 is off it
})

test('the station cut reaches the nose tip: F.S. -6.8 has a positive amount and the plane constant is -FS, as for the box', () => {
  for (const fs of [-6.8, -3, 0, 10, 22, 70, 125.5]) {
    const a = stationAmount(fs)
    const e = STATION_CUT.depth + (STATION_CUT.extent - STATION_CUT.depth) * (1 - a)
    assert.ok(Math.abs(e + fs) < 1e-9, `${fs}: ${e}`)
    assert.ok(a > 0.0005 && a < 1, `${fs}: ${a}`)
  }
  assert.deepEqual(cutRangeFor(null), { min: 22, max: 125.5 }) // chapters 4-9 keep the box's range
  assert.deepEqual(cutRangeFor(9), { min: 22, max: 125.5 })
  assert.deepEqual(cutRangeFor(12), { min: 22, max: 125.5 })
  assert.deepEqual(cutRangeFor(13), { min: -6.8, max: 125.5 })
})

test('every nose component is installed by the first chapter 13 op that lists it (the real graph)', () => {
  const y = readFileSync(fileURLToPath(new URL('../../graph/ch13.yaml', import.meta.url)), 'utf8')
  const first = new Map<string, string>()
  for (const blk of y.split(/^- id: /m).slice(1)) {
    const id = blk.split('\n')[0].trim()
    const m = /^ {2}components: \[(.*)\]/m.exec(blk)
    for (const c of (m?.[1] ?? '').split(',').map((s) => s.trim()).filter(Boolean)) if (!first.has(c)) first.set(c, id)
  }
  for (const c of NOSE_COMPONENTS) assert.equal(INSTALL[c], first.get(c), c)
  assert.ok(NOSE_COMPONENTS.includes('gear.nose_strut') && NOSE_COMPONENTS.length >= 14)
  for (const c of NOSE_COMPONENTS) assert.ok(JIG_ONLY.has(c), c) // they have no place on the layup table
})

test('the CG row names both nose-wheel arm candidates as a conflict, before the lower bound, and never as one number', () => {
  const L: LedgerLite = { ...LG, gear: { ...GEAR!, nose_arm_candidates: [17, 20], nose_arm_candidates_status: 'conflict' } }
  const r = cgRow(L)
  const segs = r.sub!.split(' · ')
  assert.ok(segs.includes('Nose wheel arm: F.S. 17 (plans) / about 20 (manual): conflict'), r.sub!)
  assert.ok(segs[segs.length - 1].includes('lower bound'), 'the lower bound stays the last segment')
  assert.ok(segs.includes('Wheels and brakes: excluded, no source'))
  assert.ok(!cgRow(LG).sub!.includes('Nose wheel arm')) // no candidates in the ledger: no row (never a guess)
})

test('the ground note adds the nose wheel W.L. (CP25 LPC 24) and no tip-over number', async () => {
  const { groundRow } = await import('../src/logic/fuselage')
  const L: LedgerLite = { ...LG, gear: { ...GEAR!, ground_handling: { ...GEAR!.ground_handling!, nose_wheel_wl: -22 } } }
  const g = groundRow(L)!
  assert.ok(g.sub.includes('nose wheel W.L. -22 (CP25 LPC 24)'), g.sub)
  assert.ok(g.sub.includes('tip-over check: not yet computed (the track has no source)'))
  assert.ok(!/tip-over[^·]*\d/i.test(g.sub), g.sub)
  assert.ok(!groundRow(LG)!.sub.includes('nose wheel')) // without the field: unchanged
})

test('the chapter 12-13 views are authored and keep FUSE_VIEWS the chapter 4-9 set', () => {
  assert.ok(!('f13.nose-door' in FUSE_VIEWS))
  for (const id of ['r30.f22-drill-tabs', 'f13.ng30-plates', 'f13.rig-nose-gear', 'f13.nose-door']) assert.notDeepEqual(fuseView(id), fuseView('f13.unknown'), id)
  assert.deepEqual(fuseView('f13.unknown'), fuseView('f99.unknown'))
})
