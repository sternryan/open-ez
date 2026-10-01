// The lab's elevator and nose-gear kinematics against numbers the Python kernels computed (tests/fixtures/kernels.json, regenerated and
// checked by tests/guide/test_lab_kernels_fixture.py). A pass means the TypeScript re-implementation agrees with core/elevators_kin.py and
// core/nose_gear_kin.py / core/landing_gear_book.nose_gear_pose.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  rotateAboutHinge, hangPitchDeg, hangsNoseDown, classifyUpTravel, nosePoints, nosePose, noseAxleAt, retractionThetaDeg, crankTurns,
  travelAngle, travelText, APART_IN, travelDuration, hangState, hangText, crankText, noseArmText, retractProgress, thetaUpForClearanceDeg,
  type NoseGearKin, type ElevatorKin, type Candidate,
} from '../src/logic/kin'

const fx = JSON.parse(readFileSync(fileURLToPath(new URL('./fixtures/kernels.json', import.meta.url)), 'utf8'))
const near = (a: number, b: number, tol = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`)
const ek: ElevatorKin = fx.extras.elevators
const ng: NoseGearKin = fx.extras.nose_gear

test('rotateAboutHinge is core.elevators_kin.rotate_about_hinge', () => {
  const h = fx.elevators.hinge as [number, number]
  near(h[0], ek.hinge_xz[0], 1e-6); near(h[1], ek.hinge_xz[1], 1e-6)
  assert.ok(fx.elevators.rotate.length >= 16)
  for (const r of fx.elevators.rotate) {
    const o = rotateAboutHinge(r.pt, h, r.deg)
    near(o[0], r.out[0], 1e-8, JSON.stringify(r)); near(o[1], r.out[1], 1e-8, JSON.stringify(r))
  }
})

test('the elevator pose matrix of the export is the same rotation (core.elevators_book.elevator_pose)', () => {
  const h = ek.hinge_xz
  for (const p of fx.elevators.poses) {
    // the matrix acts on (x, y, z) with the rotation in x-z; check it on a point against rotateAboutHinge
    const m = p.m as number[][], pt: [number, number] = [4, 0.3]
    const x = m[0][0] * pt[0] + m[0][2] * pt[1] + m[0][3], z = m[2][0] * pt[0] + m[2][2] * pt[1] + m[2][3]
    const o = rotateAboutHinge(pt, h, p.deg)
    near(x, o[0], 1e-5); near(z, o[1], 1e-5) // the exported hinge is rounded to 6 places
  }
})

test('hang pitch, nose-down and the up-travel classes are the kernel', () => {
  for (const r of fx.elevators.hang) {
    near(hangPitchDeg(r.dx, r.dz), r.pitch, 1e-9, JSON.stringify(r))
    assert.equal(hangsNoseDown(r.dx, r.dz), r.nose_down)
  }
  for (const c of fx.elevators.classify) assert.equal(classifyUpTravel(c.deg, ek.travel.up_floor_deg, ek.travel.up_target_deg), c.cls, String(c.deg))
  assert.throws(() => hangPitchDeg(0, 0))
})

test('the travel check reaches 30 down then 15 up and says so in the readout words', () => {
  const k = ek.travel
  let lo = 0, hi = 0
  for (let t = 0; t <= travelDuration() + 1; t += 0.01) { const a = travelAngle(t, k); lo = Math.min(lo, a); hi = Math.max(hi, a) }
  near(hi, 30, 1e-9); near(lo, -15, 1e-9)
  near(travelAngle(0, k), 0); near(travelAngle(travelDuration() + 5, k), -15)
  assert.equal(travelText(-15, k), 'Up 15.0 deg  (target 15, floor 12.5)')
  assert.equal(travelText(30, k), 'Down 30.0 deg  (limit 30)')
  assert.equal(travelText(0, k), 'Neutral')
})

test('the hang settles at the hang pitch, nose down, with the CG under the hinge', () => {
  const p = hangPitchDeg(ek.hang_cg.dx, ek.hang_cg.dz)
  assert.ok(p > 0 && p < 180)
  const end = hangState(60, p)
  near(end.degDown, -p, 1e-6); near(end.slide, APART_IN, 1e-9)
  assert.deepEqual(hangState(0, p), { slide: 0, degDown: 0 })
  const [, z] = rotateAboutHinge([ek.hang_cg.dx, ek.hang_cg.dz], [0, 0], end.degDown)
  assert.ok(z < -1)
  assert.equal(hangText(93.8, true, true), 'Hangs nose down, about 94 deg') // rounded, no decimal; the illustrative-CG note is the sub-line's
  assert.equal(hangText(93.8, true, false), 'Swinging toward nose down, about 94 deg')
  assert.ok(hangText(p, true, true).includes('nose down') && !hangText(p, true, true).includes('illustrative'))
})

test('the nose gear: pivot, angles, pose and axle are the kernel for both candidates', () => {
  assert.equal(ng.status, 'conflict')
  for (const n of fx.nose) {
    const p = nosePoints(ng, n.cand as Candidate)
    near(p.pivot[0], n.pivot[0], 1e-9); near(p.pivot[1], n.pivot[1], 1e-9)
    near(p.axle[0], n.axle[0], 1e-9); near(p.axle[1], n.axle[1], 1e-9)
    near(p.thetaDown, n.theta_down, 1e-9); near(p.thetaUp, n.theta_up, 1e-9)
    for (const r of n.rows) {
      near(retractionThetaDeg(r.t, p.thetaDown, p.thetaUp), r.theta, 1e-9)
      near(crankTurns(r.t, ng.crank_turns), r.crank, 1e-12)
      const m = nosePose(r.t, p)
      m.r.forEach((v, i) => near(v, r.rot[i], 1e-9, `rot ${n.cand} ${r.t}`))
      near(m.tx, r.trans[0], 1e-9); near(m.tz, r.trans[1], 1e-9)
      const a = noseAxleAt(r.t, p)
      near(a[0], r.axle_xz[0], 1e-9); near(a[1], r.axle_xz[1], 1e-9)
    }
  }
  assert.throws(() => retractionThetaDeg(1.1, 10)); assert.throws(() => crankTurns(-0.1))
})

test('retracted: the wheel is forward of the panel, the crank reads 10.8 turns, and the arm is always stated as a conflict', () => {
  for (const c of ['plans', 'manual'] as Candidate[]) {
    const p = nosePoints(ng, c)
    assert.ok(noseAxleAt(1, p)[0] < 39.75, c) // fs_panel (config) is 39.75
  }
  assert.equal(crankText(1, ng.crank_turns), 'Crank 10.8 of 10.8 turns (retracted)')
  assert.equal(crankText(0, ng.crank_turns), 'Crank 0.0 of 10.8 turns (gear down)')
  assert.equal(crankText(0.5, ng.crank_turns), 'Crank 5.4 of 10.8 turns')
  assert.equal(retractProgress(0, 6), 0); assert.equal(retractProgress(100, 6), 1)
  const w = noseArmText([17, 20], 'conflict')!
  assert.equal(w, 'Nose wheel arm: F.S. 17 (plans) / about 20 (manual): conflict')
  assert.equal(noseArmText([17], 'conflict'), null)
  assert.ok(thetaUpForClearanceDeg(2.15, 25.5, 5.4) > 90)
})

test('a film dwells on the ops that move long enough for the motion to play out', async () => {
  const { KIN_HOLD, TRAVEL_OPS, HANG_OP, RIG_OP, RIG_WAIT } = await import('../src/logic/kin')
  for (const o of TRAVEL_OPS) assert.ok(KIN_HOLD[o] > travelDuration(), o)
  assert.ok(KIN_HOLD[HANG_OP] > 7 && KIN_HOLD[RIG_OP] >= RIG_WAIT + 6, 'the crank takes 6 s after the camera comes round')
  assert.equal(RIG_OP, 'f13.rig-nose-gear')
})
