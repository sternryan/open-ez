import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { barOps, type GraphLite, type Op } from '../src/logic/graph'
import {
  fuseBarOps, parseSubject, placement, jigPose, upFace, planHalfWidth, stationLayers, stationSummary, fmtFs, stationAmount,
  STATION_CUT, cgRow, INSTALL, FUSE_CHAPTERS, turnPose, FLIP_SECONDS, hatchSoftness, labelPriority, crossedByStationCut,
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

test('the fuselage bar is the chapter 4-6 ops that are not stubs, in graph order, whatever the variant', () => {
  const want = ['f04.front-seat-bkhd-front', 'f04.panel-f22-f28-aft', 'f04.front-seat-bkhd-back', 'f05.side-blank', 'f06.trial-fit', 'f06.jig-check', 'f06.bond-front-seat',
    'f06.bond-panel', 'f06.bond-f22', 'f06.bottom-foam-fit', 'f06.bottom-glass', 'f06.bottom-bond']
  assert.deepEqual(fuseBarOps(G, 'roncz').map((o) => o.id), want)
  assert.deepEqual(fuseBarOps(G, 'gu').map((o) => o.id), want)
  assert.deepEqual([...FUSE_CHAPTERS].sort(), [4, 5, 6])
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

test('every chapter 4-6 op in the graph has an authored lab shot, and no shot is stale', () => {
  const ids: string[] = []
  for (const ch of ['ch04', 'ch05', 'ch06']) {
    const y = readFileSync(fileURLToPath(new URL(`../../graph/${ch}.yaml`, import.meta.url)), 'utf8')
    ids.push(...[...y.matchAll(/^- id: (\S+)/gm)].map((m) => m[1]))
  }
  assert.ok(ids.length >= 31)
  assert.deepEqual(Object.keys(FUSE_VIEWS).sort(), [...ids].sort())
  for (const id of ids) {
    const v = fuseView(id)
    assert.ok(v.dist > 20 && v.dist < 200 && v.el >= 20 && v.el <= 75, id)
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
