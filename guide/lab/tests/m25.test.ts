// Chapters 14-17 in the lab: where the spar is (bench or box), the slide-in, the faint box, the cut range, and the ch14-17 tour.
import test from 'node:test'
import assert from 'node:assert/strict'
import { m25Place, slideProgress, slideDuration, SLIDE, boxGhostAt, SPAR_BENCH_LAST, SPAR_FIT_OP, FUSE_PREFIXES, STICK_OP, ELEV_OPS } from '../src/logic/m25'
import { cutRangeFor, FUSE_CHAPTERS, M25_TOUR_CHAPTERS, FUSE_TOUR_CHAPTERS } from '../src/logic/fuselage'
import { KIN_HOLD } from '../src/logic/kin'

const order = ['f06.x', 'f14.jig', 'f14.foam-box', 'f14.nut-access-hole', 'f14.fit-fuselage', 'f14.bond-spar', 'f15.stainless-firewall', 'f16.pitch-pushrod']

test('the spar parts are on the bench through the last bench op and in the box from the fit; everything else is installed', () => {
  for (const c of ['spar.box', 'spar.cap_top', 'spar.lwa', 'spar.jig']) {
    assert.equal(m25Place(c, 'f14.jig', order), 'bench')
    assert.equal(m25Place(c, SPAR_BENCH_LAST, order), 'bench')
    assert.equal(m25Place(c, SPAR_FIT_OP, order), 'installed')
    assert.equal(m25Place(c, 'f16.pitch-pushrod', order), 'installed')
  }
  for (const c of ['spar.em12', 'controls.sticks', 'fuselage.firewall_stainless']) assert.equal(m25Place(c, 'f14.jig', order), 'installed')
})

test('the slide-in waits for the camera, then runs from clear of the box (0) to installed (1), and is monotone', () => {
  assert.equal(slideProgress(0), 0); assert.equal(slideProgress(SLIDE.wait), 0); assert.equal(slideProgress(SLIDE.wait + SLIDE.seconds), 1)
  let last = -1
  for (let t = 0; t < 8; t += 0.1) { const p = slideProgress(t); assert.ok(p >= last && p >= 0 && p <= 1); last = p }
  assert.ok(slideDuration() > SLIDE.wait + SLIDE.seconds)
  assert.equal(KIN_HOLD[SPAR_FIT_OP], slideDuration())
})

test('the box is drawn faint only while the op works on a part buried in it', () => {
  assert.equal(boxGhostAt({ id: 'f14.interior-layups', components: ['spar.box'] }), true)
  assert.equal(boxGhostAt({ id: 'f14.lwa-fabricate', components: ['spar.lwa'] }), true)
  assert.equal(boxGhostAt({ id: 'f14.spruce-layup6', components: ['spar.spruce_blocks', 'spar.lwa', 'spar.box'] }), true)
  assert.equal(boxGhostAt({ id: 'f14.close-box', components: ['spar.box'] }), false)
  assert.equal(boxGhostAt(null), false)
})

test('chapters 14-17 are the fuselage subject, with their own tour and a cut range that reaches the swept aft face', () => {
  for (const ch of [14, 15, 16, 17]) assert.ok(FUSE_CHAPTERS.has(ch))
  assert.deepEqual(M25_TOUR_CHAPTERS, [14, 15, 16, 17])
  assert.ok(!FUSE_TOUR_CHAPTERS.some((c) => c >= 14))
  assert.ok(cutRangeFor(14).max >= 129.9 && cutRangeFor(9).max === 125.5)
  for (const p of ['spar.', 'firewall.', 'controls.', 'trim.']) assert.ok(FUSE_PREFIXES.includes(p), p)
  assert.ok(ELEV_OPS.has(STICK_OP))
})
